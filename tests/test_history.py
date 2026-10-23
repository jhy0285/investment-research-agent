"""Authored synthetic provider responses; all real HTTP is forbidden.

Prices and vintages below are invented fixtures, not market data. Expected
values are hand-computed from the fixture definitions.
"""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.parse

from investment_research.backtest import approval, condition_state, run_backtest
from investment_research.decision_data import validate_dataset, validate_plan
from investment_research.history import (
    _derived_features,
    acquire_history,
    build,
    load_catalog,
    parse_alfred,
    replay_history,
    validate_spec,
)
from investment_research.sources import FetchResponse, SourceError, _time

NOW = datetime(2026, 10, 22, 6, 0, tzinfo=timezone.utc)
FIRST_DAY = date(2026, 1, 1)


def synthetic_close(market, day):
    """Authored closes: BTC rises 1,000 KRW a day from 1,000,000; ETH is flat."""
    if market == 'KRW-ETH':
        return Decimal(500000)
    return Decimal(1000000 + 1000 * (day - FIRST_DAY).days)


# Authored real-time database: (observation month, release date, value).
# 2025-01 is first released as 100.0 and revised to 100.5 on 2025-04-20.
CPI_RELEASES = [
    *[(date(2024, m, 1), date(2024, m, 1) + timedelta(days=45), Decimal(95 + m)) for m in range(1, 13)],
    (date(2025, 1, 1), date(2025, 2, 15), Decimal('100.0')),
    (date(2025, 2, 1), date(2025, 3, 15), Decimal('101.0')),
    (date(2025, 3, 1), date(2025, 4, 15), Decimal('102.0')),
    (date(2025, 1, 1), date(2025, 4, 20), Decimal('100.5')),
    (date(2025, 4, 1), date(2025, 5, 15), '.'),  # published as missing
]


def alfred_csv(series, vintage):
    known = {}
    for observed, released, value in CPI_RELEASES:
        if released <= vintage:
            known[observed] = value
    lines = [f'observation_date,{series}_{vintage.strftime("%Y%m%d")}']
    lines += [f'{d.isoformat()},{v}' for d, v in sorted(known.items())]
    return ('\n'.join(lines) + '\n').encode()


def kodex_days():
    """Authored issuer sample: Mondays of 2026 plus a Thursday reference date."""
    days = [date(2026, 1, 5) + timedelta(weeks=i) for i in range(42)]
    return days + [date(2026, 10, 22)]


class FakeInternet:
    def __init__(
        self,
        now=NOW,
        last_day=date(2026, 10, 22),
        leak_future=False,
        store_lag_ms=5,
        distribution='미지급\r\n(재투자)',
        divide_list=(),
        empty_instants=(),
        fund_name='KODEX 200TR',
    ):
        self.now, self.last_day, self.leak_future, self.store_lag_ms = now, last_day, leak_future, store_lag_ms
        self.distribution, self.divide_list, self.empty_instants = distribution, list(divide_list), set(empty_instants)
        self.fund_name = fund_name
        self.urls = []

    def __call__(self, url, timeout, limit):
        self.urls.append(url)
        parts = urllib.parse.urlsplit(url)
        query = dict(urllib.parse.parse_qsl(parts.query))
        if parts.path == '/robots.txt':
            return FetchResponse(b'User-agent: *\nCrawl-delay: 2\nDisallow: /search\n', 'text/plain')
        if parts.hostname == 'www.samsungfund.com' and parts.path == '/api/v1/kodex/product/2ETF92.do':
            product = dict(stkTicker='278530', fNm=self.fund_name, dividRemark=self.distribution)
            body = dict(info=dict(product=product, divideList=self.divide_list))
            return FetchResponse(json.dumps(body, ensure_ascii=False).encode(), 'application/json')
        if parts.hostname == 'www.samsungfund.com' and parts.path == '/api/v1/kodex/product-earning/2ETF92.do':
            assert query == dict(srchTerm='0')
            body = [
                dict(GIJUN_YMD=d.strftime('%Y%m%d'), PRICE=10000 + 100 * i, NAV=10001.5 + 100 * i, JISU=360.25 + i)
                for i, d in enumerate(kodex_days())
            ]
            return FetchResponse(json.dumps(body).encode(), 'application/json')
        if parts.hostname == 'api.upbit.com' and parts.path == '/v1/candles/minutes/30':
            end = datetime.fromisoformat(query['to'].replace('Z', '+00:00'))
            if query['to'] in self.empty_instants:
                return FetchResponse(b'[]', 'application/json')
            body = [
                dict(
                    market=query['market'],
                    unit=30,
                    candle_date_time_utc=(end - timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S'),
                    trade_price=float(synthetic_close(query['market'], end.date())),
                    timestamp=int(end.timestamp() * 1000) + self.store_lag_ms,
                )
            ]
            return FetchResponse(json.dumps(body).encode(), 'application/json')
        if parts.hostname == 'api.upbit.com':
            end = self.last_day
            if 'to' in query:
                end = date.fromisoformat(query['to'][:10]) - timedelta(days=1)
            days = [end - timedelta(days=i) for i in range(int(query['count']))]
            days = [d for d in days if d >= FIRST_DAY]
            body = [
                dict(
                    market=query['market'],
                    candle_date_time_utc=d.isoformat() + 'T00:00:00',
                    trade_price=float(synthetic_close(query['market'], d)),
                    timestamp=int(
                        (datetime.combine(d + timedelta(days=1), datetime.min.time(), timezone.utc).timestamp()) * 1000
                    )
                    + self.store_lag_ms,
                )
                for d in days
            ]
            return FetchResponse(json.dumps(body).encode(), 'application/json;charset=UTF-8')
        if parts.hostname == 'alfred.stlouisfed.org':
            vintage = date.fromisoformat(query['vintage_date'])
            body = alfred_csv(query['id'], vintage)
            if self.leak_future:
                body += f'{(vintage + timedelta(days=40)).isoformat()},999\n'.encode()
            return FetchResponse(body, 'application/csv')
        raise AssertionError('unexpected URL ' + url)


def spec():
    return dict(
        schema_version='investment-history-spec-v1',
        prices=[
            dict(provider='upbit_day_candles', market='KRW-BTC', start='2026-01-01'),
            dict(provider='upbit_day_candles', market='KRW-ETH', start='2026-01-01'),
        ],
        features=[
            dict(
                name='us_cpi',
                provider='alfred_vintage_csv',
                series='CPIAUCSL',
                vintage_start='2025-02-01',
                vintage_step_days=30,
                window_days=500,
            ),
            dict(
                name='btc_return_30d',
                provider='price_derived',
                instrument_id='UPBIT_KRW_BTC',
                kind='trailing_return',
                days=30,
            ),
            dict(
                name='btc_sma_5',
                provider='price_derived',
                instrument_id='UPBIT_KRW_BTC',
                kind='close_to_sma',
                observations=5,
            ),
        ],
    )


def kodex_spec():
    return dict(
        schema_version='investment-history-spec-v1',
        prices=[
            dict(provider='kodex_issuer_weekly', fund='2ETF92'),
            dict(provider='upbit_aligned_candles', market='KRW-BTC', align_to='KODEX_200TR'),
        ],
        features=[
            dict(
                name='btc_sma_5w',
                provider='price_derived',
                instrument_id='UPBIT_KRW_BTC_AT_KODEX_200TR',
                kind='close_to_sma',
                observations=5,
            )
        ],
    )


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        blocked = patch('socket.socket.connect', side_effect=AssertionError('offline history test'))
        blocked.start()
        self.addCleanup(blocked.stop)

    def acquire(self, s=None, fake=None, name='run'):
        self.fake = fake or FakeInternet()
        return acquire_history(
            s or spec(), self.root / name, fetcher=self.fake, clock=lambda: NOW, sleep=lambda _: None
        )

    def test_closed_upbit_candles_become_point_in_time_price_rows(self):
        result = self.acquire()
        btc = result['prices']['UPBIT_KRW_BTC']
        validate_dataset(btc)
        # The 2026-10-22 candle closes at 2026-10-23 00:00 UTC, after retrieval.
        self.assertEqual(btc['rows'][-1]['at'], '2026-10-22T00:00:00+00:00')
        self.assertEqual(btc['rows'][-1]['value'], str(synthetic_close('KRW-BTC', date(2026, 10, 21))))
        self.assertEqual(
            btc['rows'][0],
            dict(at='2026-01-02T00:00:00+00:00', known_at='2026-01-02T00:00:00.005000+00:00', value='1000000'),
        )
        self.assertEqual(len(btc['rows']), (date(2026, 10, 21) - FIRST_DAY).days + 1)
        self.assertEqual((btc['return_kind'], btc['adjustment'], btc['currency']), ('price', 'unadjusted', 'KRW'))
        self.assertGreater(sum('api.upbit.com' in u for u in self.fake.urls), 2)  # paginated
        self.assertEqual(result['failures'], [])

    def test_conflicting_or_misdated_candles_are_rejected(self):
        snapshots = json.loads((self.acquire_and_read('snapshots.json')))
        pages = snapshots['items']['prices:KRW-BTC']['pages']
        duplicate = deepcopy(pages[0])
        duplicate['rows'][3]['close'] = '1'
        broken = deepcopy(snapshots)
        broken['items']['prices:KRW-BTC']['pages'].append(duplicate)
        self.assertIn('conflicting closes', build(spec(), broken)['failures'][0]['reason'])
        broken = deepcopy(snapshots)
        broken['items']['prices:KRW-BTC']['pages'][0]['rows'][3]['last_tick_stored_ms'] += 3600 * 1000
        self.assertIn('outside its daily candle', build(spec(), broken)['failures'][0]['reason'])

    def acquire_and_read(self, name):
        self.acquire()
        return (self.root / 'run' / name).read_text(encoding='utf-8')

    def test_vintage_rows_carry_publication_time_and_revisions_do_not_leak_backwards(self):
        rows = self.acquire()['features']['us_cpi']
        jan = [r for r in rows if r['observed_at'].startswith('2025-01-01')]
        self.assertEqual([r['value'] for r in jan], ['100', '100.5'])
        # Sampled vintages: 2025-03-03 sees the first print, 2025-05-02 the revision.
        self.assertEqual(jan[0]['known_at'], '2025-03-04T06:00:00+00:00')
        self.assertEqual(jan[1]['known_at'], '2025-05-03T06:00:00+00:00')
        for r in rows:
            self.assertLessEqual(_time(r['observed_at']), _time(r['known_at']))
            self.assertLessEqual(_time(r['known_at']), _time(r['retrieved_at']))
        # Missing values are skipped, never zero.
        self.assertFalse(any(r['observed_at'].startswith('2025-04-01') for r in rows))
        rule = [dict(feature='us_cpi', op='>=', value='100.5', max_age_days=366)]
        jan_only = [r for r in rows if r['observed_at'].startswith('2025-01-01')]
        self.assertEqual(condition_state(rule, jan_only, _time('2025-04-30T00:00:00+00:00'))['state'], 'fail')
        self.assertEqual(condition_state(rule, jan_only, _time('2025-05-04T00:00:00+00:00'))['state'], 'pass')

    def test_window_parameter_style_future_rows_are_refused(self):
        result = self.acquire(fake=FakeInternet(leak_future=True))
        self.assertNotIn('us_cpi', result['features'])
        self.assertTrue(any('after its vintage date' in f['reason'] for f in result['failures']))
        with self.assertRaises(SourceError):
            parse_alfred(alfred_csv('CPIAUCSL', date(2025, 3, 3)), 'UNRATE', date(2025, 3, 3), 500)

    def test_same_vintage_year_over_year_uses_exact_base_month(self):
        s = spec()
        s['features'][0].update(transform='yoy_percent')
        rows = self.acquire(s)['features']['us_cpi']
        jan = [r for r in rows if r['observed_at'].startswith('2025-01-01')]
        # 2024-01 level is 96: first print 100/96, revision 100.5/96, same vintage each time.
        self.assertEqual([r['value'] for r in jan], ['4.166667', '4.6875'])
        self.assertEqual(jan[0]['unit'], 'percent')
        s['features'][0]['window_days'] = 200
        with self.assertRaises(SourceError):
            validate_spec(s, load_catalog(), NOW.date())

    def test_derived_features_are_hand_checked_and_use_only_past_rows(self):
        result = self.acquire()
        btc = result['prices']['UPBIT_KRW_BTC']
        ret = {r['observed_at']: r for r in result['features']['btc_return_30d']}
        # Close of 2026-03-01 candle (at 03-02) is 1,059,000; 30 days earlier (at 01-31) is 1,029,000.
        self.assertEqual(
            Decimal(ret['2026-03-02T00:00:00+00:00']['value']),
            (Decimal(1059000) / 1029000 - 1).quantize(Decimal('1e-12')),
        )
        sma = {r['observed_at']: r for r in result['features']['btc_sma_5']}
        # Five consecutive closes 1,055,000..1,059,000 average 1,057,000.
        self.assertEqual(
            Decimal(sma['2026-03-02T00:00:00+00:00']['value']),
            (Decimal(1059000) / 1057000 - 1).quantize(Decimal('1e-12')),
        )
        self.assertNotIn('2026-01-02T00:00:00+00:00', ret)  # no base yet: no value
        cut = dict(btc, rows=[r for r in btc['rows'] if r['at'] <= '2026-03-02T00:00:00+00:00'])
        for item in spec()['features'][1:]:
            full = {r['observed_at']: r for r in _derived_features(item, btc)}
            for r in _derived_features(item, cut):
                self.assertEqual(r['value'], full[r['observed_at']]['value'])
                self.assertEqual(r['known_at'], full[r['observed_at']]['known_at'])

    def test_derived_feature_does_not_bridge_a_gap(self):
        btc = self.acquire()['prices']['UPBIT_KRW_BTC']
        holed = dict(btc, rows=[r for r in btc['rows'] if not '2026-01-20' <= r['at'][:10] <= '2026-02-10'])
        item = dict(name='x', provider='price_derived', instrument_id='UPBIT_KRW_BTC', kind='trailing_return', days=30)
        observed = {r['observed_at'][:10] for r in _derived_features(item, holed)}
        self.assertNotIn('2026-03-01', observed)  # base 2026-01-30 missing and >7 days from neighbours

    def test_unreviewed_inputs_and_unbounded_requests_fail_before_network(self):
        catalog = load_catalog()
        for change in (
            lambda s: s['prices'][0].update(market='KRW-DOGE'),
            lambda s: s['features'][0].update(series='SP500'),
            lambda s: s['features'][0].update(vintage_step_days=1),
            lambda s: s['features'][1].update(instrument_id='UNKNOWN'),
            lambda s: s['prices'][0].update(start='2010-01-01'),
            lambda s: s['features'][0].update(vintage_start='1990-01-01', vintage_step_days=7),
        ):
            s = spec()
            change(s)
            with self.subTest(spec=s), self.assertRaises(SourceError):
                validate_spec(s, catalog, NOW.date())
        with self.assertRaises(SourceError):
            acquire_history(dict(spec(), prices=[]), self.root / 'x', fetcher=None, clock=lambda: NOW)
        self.assertFalse((self.root / 'x').exists())

    def test_transient_failures_are_retried_a_bounded_number_of_times(self):
        class Flaky(FakeInternet):
            def __init__(self, failures, error):
                super().__init__()
                self.failures, self.error = failures, error

            def __call__(self, url, timeout, limit):
                if 'api.upbit.com' in url and self.failures:
                    self.failures -= 1
                    if self.error == 'timeout':
                        raise TimeoutError('read timed out')
                    return FetchResponse(b'busy', 'text/plain', status=503)
                return super().__call__(url, timeout, limit)

        s = dict(spec(), features=[])
        s['prices'] = s['prices'][:1]
        self.assertEqual(self.acquire(s, Flaky(2, 'timeout'), 'retry')['failures'], [])
        failed = self.acquire(s, Flaky(3, 'busy'), 'busy')
        self.assertEqual(failed['prices'], {})
        self.assertIn('HTTP 503', failed['failures'][0]['reason'])

    def test_withdrawn_observation_fails_instead_of_keeping_old_value(self):
        snapshots = json.loads(self.acquire_and_read('snapshots.json'))
        vintages = snapshots['items']['features:us_cpi']['vintages']
        # 2025-02 was first seen in the 2025-04-02 vintage; the 2025-05-02 vintage drops it.
        later = next(v for v in vintages if v['vintage_date'] == '2025-05-02')
        later['rows'] = [r for r in later['rows'] if r[0] != '2025-02-01']
        result = build(spec(), snapshots)
        self.assertNotIn('us_cpi', result['features'])
        self.assertIn('withdrawn', next(f for f in result['failures'] if f['item'] == 'features:us_cpi')['reason'])

    def test_malformed_spec_items_are_input_errors(self):
        catalog = load_catalog()
        for change in (
            lambda s: s['features'][0].pop('vintage_start'),
            lambda s: s['features'][0].update(name=123),
            lambda s: s['prices'][0].pop('start'),
        ):
            s = spec()
            change(s)
            with self.subTest(spec=s), self.assertRaises(SourceError):
                validate_spec(s, catalog, NOW.date())

    def test_crawl_delay_applies_after_robots_check(self):
        sleeps = []
        s = dict(spec(), prices=[], features=spec()['features'][:1])
        acquire_history(s, self.root / 'polite', fetcher=FakeInternet(), clock=lambda: NOW, sleep=sleeps.append)
        self.assertGreater(len(sleeps), 0)
        self.assertGreater(sleeps[0], 1.9)

    def test_sma_refuses_a_window_with_missing_days(self):
        btc = self.acquire()['prices']['UPBIT_KRW_BTC']
        holed = dict(btc, rows=[r for r in btc['rows'] if not '2026-02-20' <= r['at'][:10] <= '2026-02-28'])
        item = dict(
            name='x', provider='price_derived', instrument_id='UPBIT_KRW_BTC', kind='close_to_sma', observations=5
        )
        observed = {r['observed_at'][:10] for r in _derived_features(item, holed)}
        self.assertNotIn('2026-03-02', observed)  # 5 closes would span 2026-02-19..03-02
        self.assertIn('2026-03-06', observed)

    def test_replay_rebuilds_offline_and_detects_tampering(self):
        result = self.acquire()
        self.assertEqual(replay_history(self.root / 'run'), result)
        path = self.root / 'run' / 'history.json'
        path.write_text(path.read_text(encoding='utf-8').replace('1000000', '1000001', 1), encoding='utf-8')
        with self.assertRaises(SourceError):
            replay_history(self.root / 'run')

    def test_history_satisfies_decision_contracts_without_claiming_total_return(self):
        from tests.test_investment_cycle import experiment

        history = self.acquire()
        plan, _ = experiment()
        c = plan['candidates'][0]
        plan['synthetic'] = False
        c.update(
            asset_id='BTC',
            prices=history['prices']['UPBIT_KRW_BTC'],
            benchmark=history['prices']['UPBIT_KRW_ETH'],
            features=history['features']['btc_return_30d'] + history['features']['btc_sma_5'],
        )
        c['benchmark'] = dict(c['benchmark'], asset_id='ETH')
        c['quote'].update(instrument_id='UPBIT_KRW_BTC')
        c['strategy'].update(
            conditions=[dict(feature='btc_return_30d', op='>', value='0', max_age_days=3)],
            price_conditions=[dict(feature='btc_sma_5', op='<', value='0.5', max_age_days=3)],
            invalidations=[dict(feature='btc_return_30d', op='<', value='-0.9', max_age_days=3)],
            splits=dict(
                start='2026-01-01T00:00:00+00:00',
                validation_start='2026-04-01T00:00:00+00:00',
                recent_start='2026-07-01T00:00:00+00:00',
                end='2026-10-22T00:00:00+00:00',
            ),
            locked_at='2026-01-01T00:00:00+00:00',
        )
        validate_plan(plan)
        bt = run_backtest(c, NOW)
        # The coin price is a reviewed lower bound; a price-only benchmark is not.
        self.assertNotIn('배당·분배금을 포함한 실제 상품 수익률이 아니다.', bt['blockers'])
        self.assertIn('비교 시장이 당시 이용 가능했던 총수익 판본이 아니다.', bt['blockers'])
        self.assertEqual(approval(bt, c['strategy'], plan['policy'])[0], 'insufficient')

    def test_kodex_total_return_rests_on_the_issuer_statement(self):
        result = self.acquire(kodex_spec(), name='kodex')
        tr = result['prices']['KODEX_200TR']
        validate_dataset(tr)
        self.assertEqual(
            (tr['return_kind'], tr['adjustment'], tr['return_basis']),
            ('total_return', 'pit_total_return_index', 'non_distributing_fund_price'),
        )
        # 15:30 KST close, published at 18:00 KST; 2026-10-22 was not yet published at retrieval.
        self.assertEqual(
            tr['rows'][0], dict(at='2026-01-05T06:30:00+00:00', known_at='2026-01-05T09:00:00+00:00', value='10000')
        )
        self.assertEqual(tr['rows'][-1]['at'], '2026-10-19T06:30:00+00:00')
        self.assertIn('미지급', tr['return_basis_note'])
        for fake, reason in (
            (FakeInternet(distribution='분기 지급'), 'reinvested'),
            (FakeInternet(divide_list=[dict(date='20260430', amount='100')]), 'reinvested'),
            (FakeInternet(fund_name='KODEX 200'), 'different fund'),
        ):
            with self.subTest(reason=reason):
                failed = self.acquire(
                    kodex_spec(), fake, name='kodex-' + reason.replace(' ', '-') + str(len(fake.divide_list))
                )
                self.assertNotIn('KODEX_200TR', failed['prices'])
                self.assertNotIn('UPBIT_KRW_BTC_AT_KODEX_200TR', failed['prices'])
                self.assertTrue(any(reason in f['reason'] for f in failed['failures']))

    def test_aligned_candles_share_closing_instants_and_skip_empty_windows(self):
        fake = FakeInternet(empty_instants={'2026-03-02T06:30:00Z', '2026-03-09T06:30:00Z'})
        result = self.acquire(kodex_spec(), fake, name='aligned')
        btc = result['prices']['UPBIT_KRW_BTC_AT_KODEX_200TR']
        kodex_at = {r['at'] for r in result['prices']['KODEX_200TR']['rows']}
        self.assertTrue({r['at'] for r in btc['rows']} <= kodex_at)
        self.assertNotIn('2026-03-02T06:30:00+00:00', {r['at'] for r in btc['rows']})
        self.assertEqual(
            btc['provenance']['missing_instants'], ['2026-03-02T06:30:00+00:00', '2026-03-09T06:30:00+00:00']
        )
        first = btc['rows'][0]
        self.assertEqual(first['value'], str(synthetic_close('KRW-BTC', date(2026, 1, 5))))
        self.assertEqual(first['known_at'], '2026-01-05T06:30:00.005000+00:00')
        self.assertEqual((btc['return_kind'], btc['return_basis']), ('price', 'price_lower_bound'))
        # Weekly SMA uses the series' own spacing: 5 weekly closes span 28 days
        # (+7 days tolerance). A two-week hole makes the span 42 days: refused.
        sma = {r['observed_at'][:10] for r in result['features']['btc_sma_5w']}
        self.assertEqual(min(sma), '2026-02-02')
        self.assertNotIn('2026-03-16', sma)
        self.assertIn('2026-04-13', sma)
        self.assertEqual(replay_history(self.root / 'aligned'), result)

    def test_lower_bound_coin_against_kodex_total_return_passes_definition_checks(self):
        from tests.test_investment_cycle import experiment

        history = self.acquire(kodex_spec(), name='pair')
        plan, _ = experiment()
        plan['synthetic'] = False
        c = plan['candidates'][0]
        c.update(
            asset_id='BTC',
            prices=history['prices']['UPBIT_KRW_BTC_AT_KODEX_200TR'],
            benchmark=history['prices']['KODEX_200TR'],
            features=history['features']['btc_sma_5w'],
        )
        c['quote'].update(instrument_id='UPBIT_KRW_BTC_AT_KODEX_200TR')
        rule = [dict(feature='btc_sma_5w', op='>', value='0', max_age_days=8)]
        c['strategy'].update(
            conditions=rule,
            price_conditions=rule,
            invalidations=[dict(feature='btc_sma_5w', op='<', value='-0.5', max_age_days=8)],
            splits=dict(
                start='2026-01-01T00:00:00+00:00',
                validation_start='2026-04-01T00:00:00+00:00',
                recent_start='2026-07-01T00:00:00+00:00',
                end='2026-10-22T00:00:00+00:00',
            ),
            locked_at='2026-01-01T00:00:00+00:00',
        )
        validate_plan(plan)
        bt = run_backtest(c, NOW)
        self.assertEqual(bt['blockers'], [])
        # Same instants on both sides, so paired market returns exist.
        self.assertGreater(bt['periods']['historical']['horizons']['1m']['unconditional']['count'], 0)
        with self.assertRaises(SourceError):
            validate_spec(dict(kodex_spec(), prices=kodex_spec()['prices'][::-1]), load_catalog(), NOW.date())

    def history_plan(self, as_of='2026-10-23T09:00:00+09:00'):
        from tests.test_investment_cycle import experiment

        plan, snapshot = experiment()
        plan['synthetic'] = snapshot['synthetic'] = False
        snapshot['as_of'] = as_of
        snapshot['methods'] = [dict(asset_id='BTC', name='Bitcoin', economics='합성', risk='합성 위험', missing=[])]
        for e in snapshot['evidence']:
            e.update(asset_ids=['BTC'], retrieved_at='2026-10-22T07:00:00+00:00')
        c = plan['candidates'][0]
        for key in ('prices', 'benchmark', 'features', 'quote', 'current_price_evidence_id'):
            c.pop(key)
        rule = [dict(feature='btc_sma_5w', op='>', value='-1', max_age_days=8)]
        c.update(
            asset_id='BTC',
            max_price_age_days=7,
            history=dict(prices='UPBIT_KRW_BTC_AT_KODEX_200TR', benchmark='KODEX_200TR', features=['btc_sma_5w']),
            review=dict(reviewer='synthetic fixture author', at='2026-10-22T08:00:00+00:00', note='합성 검토'),
        )
        c['strategy'].update(
            conditions=rule,
            price_conditions=rule,
            invalidations=[dict(feature='btc_sma_5w', op='<', value='-5', max_age_days=8)],
            locked_at='2026-01-01T00:00:00+00:00',
            splits=dict(
                start='2026-01-01T00:00:00+00:00',
                validation_start='2026-04-01T00:00:00+00:00',
                recent_start='2026-07-01T00:00:00+00:00',
                end='2026-10-23T00:00:00+00:00',
            ),
        )
        return plan, snapshot

    def test_history_run_supplies_linked_current_evidence(self):
        from investment_research.investment_cycle import attach_history, evaluate

        history = self.acquire(kodex_spec(), name='plan')
        plan, snapshot = self.history_plan()
        with self.assertRaises(SourceError):
            validate_plan(plan)  # unexpanded references are not a plan
        expanded, augmented = attach_history(plan, history, 'f' * 64, snapshot)
        validate_plan(expanded)
        c = expanded['candidates'][0]
        self.assertEqual(c['quote']['at'], '2026-10-19T06:30:00+00:00')
        self.assertEqual(c['history']['sha256'], 'f' * 64)
        linked = [r for r in c['features'] if 'evidence_id' in r]
        self.assertEqual([r['observed_at'] for r in linked], ['2026-10-19T06:30:00+00:00'])
        row = evaluate(expanded, augmented)['decisions'][0]
        self.assertFalse(any('검증 원문 연결이 없음' in b for b in row['blockers']), row['blockers'])
        self.assertEqual(row['current_signal']['state'], 'pass')
        self.assertNotIn('비교 시장이 당시 이용 가능했던 총수익 판본이 아니다.', row['backtest']['blockers'])

    def test_history_must_precede_the_judgment_and_exist(self):
        from investment_research.investment_cycle import attach_history

        history = self.acquire(kodex_spec(), name='early')
        plan, snapshot = self.history_plan(as_of='2026-10-22T05:00:00+00:00')
        with self.assertRaises(SourceError):
            attach_history(plan, history, 'f' * 64, snapshot)
        plan, snapshot = self.history_plan()
        plan['candidates'][0]['history']['features'] = ['missing_feature']
        with self.assertRaises(SourceError):
            attach_history(plan, history, 'f' * 64, snapshot)

    def test_history_backed_cycle_replays_without_the_history_directory(self):
        from investment_research.investment_cycle import replay_cycle, run_cycle

        self.acquire(kodex_spec(), name='cycle-history')
        plan, snapshot = self.history_plan()

        class Run:
            pass

        with (
            patch('investment_research.orchestrator.replay_ask', return_value=Run()),
            patch('investment_research.investment_cycle.research_snapshot', return_value=snapshot),
        ):
            result = run_cycle(plan, 'unused', self.root / 'cycle', history=self.root / 'cycle-history')
        self.assertEqual(result['method_version'], 'investment_cycle_v3')
        self.assertEqual(replay_cycle(self.root / 'cycle'), result)

    def test_old_candles_without_storage_time_are_dated_after_the_close(self):
        class NullStamps(FakeInternet):
            def __call__(self, url, timeout, limit):
                response = super().__call__(url, timeout, limit)
                if '/v1/candles/minutes/30' in url:
                    body = json.loads(response.body)
                    for candle in body:
                        candle['timestamp'] = None
                    return FetchResponse(json.dumps(body).encode(), 'application/json')
                return response

        result = self.acquire(kodex_spec(), NullStamps(), name='nulls')
        first = result['prices']['UPBIT_KRW_BTC_AT_KODEX_200TR']['rows'][0]
        self.assertEqual(first['known_at'], '2026-01-05T06:31:00+00:00')

    def test_cli_exit_codes(self):
        from investment_research.__main__ import main

        path = self.root / 'spec.json'
        path.write_text(json.dumps(spec()), encoding='utf-8')
        out, err = StringIO(), StringIO()
        with (
            patch('investment_research.history._fetch_http', FakeInternet()),
            patch('investment_research.history.time.sleep'),
            redirect_stdout(out),
            redirect_stderr(err),
        ):
            self.assertEqual(main(['invest', 'history', 'acquire', str(path), '--output', str(self.root / 'cli')]), 0)
            self.assertEqual(main(['invest', 'history', 'replay', str(self.root / 'cli')]), 0)
            self.assertEqual(main(['invest', 'history', 'acquire', str(path), '--output', str(self.root / 'cli')]), 2)
        self.assertIn('장기 시점 이력 수집 결과', out.getvalue())


if __name__ == '__main__':
    unittest.main()
