"""Authored synthetic experiments; all HTTP calls are forbidden.

Analytic price paths and hand-calculated expectations test financial behavior,
not a duplicate implementation of the backtest.
"""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from investment_research.backtest import approval, condition_state, drawdown, event_at, net_return, run_backtest
from investment_research.decision_data import (
    default_plan,
    digest,
    encode,
    load,
    save,
    target,
    validate_dataset,
    validate_plan,
    validate_strategy,
)
from investment_research.decision_journal import feedback, persist_review, record, review
from investment_research.decision_report import render_decision, render_review
from investment_research.investment_cycle import evaluate, replay_cycle, run_cycle
from investment_research.sources import SourceError, _time

AT = '2026-10-07T12:00:00+09:00'


def experiment():
    """Repeated authored four-month cycle: one +8% period and three -1%.

    Signal is published before the entry period. Benchmark is flat. Signal
    months vary through the calendar so matched-season comparison has controls.
    """
    rows = []
    features = []
    value = Decimal(100)
    for i in range(327):
        year, month = divmod(2000 * 12 + i, 12)
        at = f'{year:04d}-{month+1:02d}-01T00:00:00+00:00'
        # A positive signal at i-2 precedes next observation's entry (i-1).
        if i:
            value *= Decimal('1.08') if (i - 2) % 5 == 0 else Decimal('0.99')
        rows.append(dict(at=at, known_at=at, value=str(value)))
        for name, v in [('demand', '1' if i % 5 == 0 else '0'), ('price_multiple', '10'), ('broken', '0')]:
            features.append(
                dict(
                    name=name,
                    value=v,
                    observed_at=at,
                    known_at=at,
                    measure=name,
                    unit='ratio',
                    currency='not_applicable',
                    retrieved_at='2027-04-01T00:00:00+00:00',
                    source='authored synthetic fixture',
                    vintage=at,
                    evidence_id={'demand': 'E_DEMAND', 'price_multiple': 'E_PRICE', 'broken': 'E_RISK'}[name],
                )
            )
    # Current signal is explicitly authored; it is not a historical result.
    latest = [f for f in features if f['observed_at'].startswith('2026-10-01')]
    for f in latest:
        if f['name'] == 'demand':
            f['value'] = '1'
    metadata = dict(
        schema_version='investment-prices-v1',
        synthetic=True,
        asset_id='US_EQUITY',
        currency='KRW',
        source='authored monthly instrument returns; not market data',
        measure='synthetic_total_return_index',
        unit='KRW per synthetic unit',
        calendar='authored monthly fixture',
        survivorship='single_instrument',
        return_kind='total_return',
        adjustment='pit_total_return_index',
        retrieved_at='2027-04-01T00:00:00+00:00',
    )
    prices = dict(metadata, instrument_id='SYNTHETIC_EQUITY', rows=rows)
    benchmark = dict(
        metadata, instrument_id='SYNTHETIC_MARKET', asset_id='MARKET', rows=[dict(r, value='100') for r in rows]
    )

    def r(name, op, v):
        return dict(feature=name, op=op, value=v, max_age_days=40)

    strategy = dict(
        id='authored_cycle',
        version='v1',
        hypothesis='수요가 개선되고 가격이 정해진 범위일 때 다음 한 달 상품 수익이 대안보다 좋을 것이다.',
        locked_at='2013-01-01T00:00:00+00:00',
        trial_count=1,
        holding_horizon='1m',
        revision_reason='합성 계산 검증용 최초 정의',
        parent_sha256=None,
        cost_bps_per_side='10',
        conditions=[r('demand', '>=', '1')],
        price_conditions=[r('price_multiple', '<=', '15')],
        invalidations=[r('broken', '>=', '1')],
        splits=dict(
            start='2000-01-01T00:00:00+00:00',
            validation_start='2014-01-01T00:00:00+00:00',
            recent_start='2020-01-01T00:00:00+00:00',
            end='2027-04-01T00:00:00+00:00',
        ),
    )
    current = next(r for r in rows if r['at'].startswith('2026-10-01'))
    quote = dict(
        at=current['at'],
        known_at=current['known_at'],
        value='10000',
        currency='KRW',
        unit='KRW per share',
        measure='synthetic_executable_quote',
        instrument_id='SYNTHETIC_EQUITY',
    )
    candidate = dict(
        asset_id='US_EQUITY',
        name='합성 주식',
        group='equity',
        held=False,
        mode='quantitative',
        quote=quote,
        reasons_up=['검산용 수요 개선 조건'],
        reasons_down=['조건이 사라질 위험'],
        evidence_ids=['E_DEMAND'],
        counter_evidence_ids=['E_RISK'],
        current_price_evidence_id='E_QUOTE',
        review=dict(reviewer='synthetic fixture author', at=AT, note='경제적 검토도 합성 fixture다.'),
        strategy=strategy,
        prices=prices,
        benchmark=benchmark,
        features=features,
        max_price_age_days=31,
    )
    plan = default_plan()
    plan.update(
        synthetic=True,
        candidates=[candidate],
        profile=dict(
            reserve_krw='1000000', loss_capacity_krw='5000000', loss_tolerance_fraction='0.5', horizon_months=12
        ),
    )
    plan['policy'].update(minimum_historical=2, minimum_validation=2, minimum_recent=2, minimum_live=2)
    snapshot = dict(
        as_of=AT,
        synthetic=True,
        research_sha256='a' * 64,
        scan=None,
        methods=[dict(asset_id='US_EQUITY', name='합성 주식', economics='합성', risk='합성 위험', missing=[])],
        evidence=[
            dict(
                id=i,
                asset_ids=['US_EQUITY'],
                text='authored synthetic evidence',
                source_id=i,
                retrieved_at='2026-10-07T00:00:00+00:00',
                value=v,
                observed_at='2026-10-01',
                definition={
                    'measure': {
                        'E_DEMAND': 'demand',
                        'E_PRICE': 'price_multiple',
                        'E_RISK': 'broken',
                        'E_QUOTE': 'synthetic_executable_quote',
                    }[i]
                },
                unit='KRW per share' if i == 'E_QUOTE' else 'ratio',
                currency='KRW' if i == 'E_QUOTE' else 'not_applicable',
            )
            for i, v in [('E_DEMAND', '1'), ('E_PRICE', '10'), ('E_RISK', '0'), ('E_QUOTE', '10000')]
        ],
    )
    return plan, snapshot


def outcome_prices(candidate):
    data = deepcopy([candidate['prices'], candidate['benchmark']])
    for d in data:
        original = next(r for r in d['rows'] if r['at'].startswith('2026-10-01'))
        for day in ('2026-10-08', '2026-10-09', '2026-11-08', '2026-11-09'):
            at = day + 'T00:00:00+00:00'
            value = Decimal(original['value'])
            if day.startswith('2026-11') and d['asset_id'] == 'US_EQUITY':
                value *= Decimal('.9')
            d['rows'].append(dict(at=at, known_at=at, value=str(value)))
        d['rows'].sort(key=lambda r: r['at'])
    return data


def dated_experiment(month):
    plan, snapshot = experiment()
    month_at = f'2026-{month:02d}-01T00:00:00+00:00'
    at = f'2026-{month:02d}-07T12:00:00+09:00'
    candidate = plan['candidates'][0]
    candidate['review']['at'] = at
    candidate['quote'].update(at=month_at, known_at=month_at)
    for f in candidate['features']:
        if f['observed_at'] == month_at and f['name'] == 'demand':
            f['value'] = '1'
    snapshot['as_of'] = at
    for e in snapshot['evidence']:
        e.update(observed_at=month_at[:10], retrieved_at=f'2026-{month:02d}-07T00:00:00+00:00')
    return plan, snapshot


class InvestmentCycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.plan, self.snapshot = experiment()
        self.c = self.plan['candidates'][0]
        p = patch('socket.socket.connect', side_effect=AssertionError('offline investment experiment'))
        p.start()
        self.addCleanup(p.stop)

    def test_transaction_costs_use_buy_and_sell_cash_flows(self):
        self.assertEqual(net_return('100', '110', '100'), Decimal('108.9') / Decimal('101') - 1)
        self.assertLess(net_return('100', '100', '100'), 0)

    def test_drawdown_is_peak_to_trough_and_includes_intermediate_path(self):
        self.assertEqual(drawdown(list(map(Decimal, ['100', '110', '88', '120']))), Decimal('-.2'))

    def test_calendar_horizons_handle_month_end_and_leap_year(self):
        self.assertEqual(target(_time('2024-01-31T00:00:00+00:00'), '1m').day, 29)
        self.assertEqual(target(_time('2024-02-29T00:00:00+00:00'), '1y').day, 28)

    def test_future_revision_does_not_rewrite_old_signal(self):
        f = deepcopy(self.c['features'][:1])
        f[0]['value'] = '0'
        changed = {**f[0], 'value': '1', 'known_at': '2000-02-01T00:00:00+00:00', 'vintage': 'revision'}
        at = _time('2000-01-15T00:00:00+00:00')
        self.assertEqual(condition_state(self.c['strategy']['conditions'], f + [changed], at)['state'], 'fail')

    def test_future_released_observation_is_not_usable(self):
        f = deepcopy(self.c['features'][:1])
        f[0]['known_at'] = '2001-01-01T00:00:00+00:00'
        self.assertEqual(
            condition_state(self.c['strategy']['conditions'], f, _time('2000-02-01T00:00:00+00:00'))['state'], 'unknown'
        )

    def test_stale_observation_does_not_qualify_as_current_signal(self):
        self.assertEqual(
            condition_state(self.c['strategy']['conditions'], self.c['features'][:1], _time(AT))['state'], 'unknown'
        )

    def test_price_rows_require_order_unique_positive_finite_values(self):
        for mutation in ('duplicate', 'negative', 'nan', 'unsorted'):
            d = deepcopy(self.c['prices'])
            if mutation == 'duplicate':
                d['rows'].insert(0, d['rows'][0])
            elif mutation == 'negative':
                d['rows'][0]['value'] = '-1'
            elif mutation == 'nan':
                d['rows'][0]['value'] = 'NaN'
            else:
                d['rows'][0], d['rows'][1] = d['rows'][1], d['rows'][0]
            with self.subTest(mutation=mutation), self.assertRaises(SourceError):
                validate_dataset(d)

    def test_latest_adjusted_and_current_survivors_cannot_approve_buys(self):
        for key, value in [('adjustment', 'latest_adjusted'), ('survivorship', 'current_survivors')]:
            c = deepcopy(self.c)
            c['prices'][key] = value
            bt = run_backtest(c, _time(AT))
            self.assertEqual(approval(bt, c['strategy'], self.plan['policy'])[0], 'insufficient')

    def test_reversed_currency_or_price_only_cannot_pass_allocation_definition(self):
        self.c['benchmark']['currency'] = 'USD'
        with self.assertRaises(SourceError):
            validate_plan(self.plan)
        self.c['benchmark']['currency'] = 'KRW'
        self.c['prices'].update(return_kind='price', adjustment='unadjusted')
        self.c['benchmark'].update(return_kind='price', adjustment='unadjusted')
        self.assertEqual(evaluate(self.plan, self.snapshot)['decisions'][0]['action'], '신규 매수하지 않음')

    def test_strategy_freeze_precedes_independent_validation(self):
        self.c['strategy']['locked_at'] = '2015-01-01T00:00:00+00:00'
        with self.assertRaises(SourceError):
            validate_strategy(self.c['strategy'])

    def test_signal_enters_next_observation_and_never_crosses_partition(self):
        bt = run_backtest(self.c, _time(AT))
        h = bt['periods']['historical']['horizons']['1m']
        self.assertEqual(h['episodes'][0]['entry_at'], '2000-02-01T00:00:00+00:00')
        self.assertEqual(Decimal(h['episodes'][0]['return']), Decimal('1.08') * Decimal('.999') / Decimal('1.001') - 1)
        for part in bt['periods'].values():
            for study in part['horizons'].values():
                self.assertTrue(all(_time(e['exit_at']) < _time(part['end']) for e in study['episodes']))
                for left, right in zip(study['episodes'], study['episodes'][1:]):
                    self.assertLess(_time(left['exit_at']), _time(right['entry_at']))

    def test_all_horizons_and_unconditional_season_market_buyhold_baselines_exist(self):
        bt = run_backtest(self.c, _time(AT))
        self.assertEqual(set(bt['periods']['recent']['horizons']), {'1m', '3m', '6m', '1y'})
        h = bt['periods']['recent']['horizons']['1m']
        self.assertGreater(h['signal']['count'], 2)
        self.assertGreater(Decimal(h['signal']['mean']), Decimal(h['unconditional']['mean']))
        self.assertGreater(Decimal(h['signal']['mean']), Decimal(h['same_season']['mean']))
        self.assertIsNotNone(bt['periods']['recent']['buy_and_hold'])

    def test_validated_strategy_produces_A_grade_buy_and_conserves_cash(self):
        r = evaluate(self.plan, self.snapshot)
        row = r['decisions'][0]
        self.assertEqual((row['grade'], row['action']), ('A', '분할 매수'))
        self.assertEqual(row['amount_krw'], '4000000')
        self.assertEqual(r['allocation']['cash_krw'], '6000000')
        self.assertEqual(
            sum(Decimal(row['entry_plan'][k]) for k in ('today_krw', 'next_review_krw', 'following_review_krw')),
            Decimal('4000000'),
        )

    def test_unknown_financial_constraints_waits_with_all_cash(self):
        self.plan['profile'] = None
        r = evaluate(self.plan, self.snapshot)
        self.assertEqual(r['decisions'][0]['action'], '조건 충족 대기')
        self.assertEqual(r['allocation']['cash_krw'], '10000000')

    def test_missing_source_or_current_numeric_mismatch_blocks_buy(self):
        for change in ('missing', 'mismatch'):
            snap = deepcopy(self.snapshot)
            if change == 'missing':
                snap['evidence'] = []
            else:
                snap['evidence'][0]['value'] = '0'
            with self.subTest(change=change):
                self.assertEqual(evaluate(self.plan, snap)['decisions'][0]['grade'], 'D')

    def test_no_current_signal_waits_and_invalidated_held_thesis_reviews_sale(self):
        for f in self.c['features']:
            if f['name'] == 'demand' and f['observed_at'].startswith('2026-10-01'):
                f['value'] = '0'
        self.snapshot['evidence'][0]['value'] = '0'
        self.assertEqual(evaluate(self.plan, self.snapshot)['decisions'][0]['action'], '조건 충족 대기')
        self.c['held'] = True
        for f in self.c['features']:
            if f['name'] == 'broken' and f['observed_at'].startswith('2026-10-01'):
                f['value'] = '1'
        self.snapshot['evidence'][2]['value'] = '1'
        self.assertEqual(evaluate(self.plan, self.snapshot)['decisions'][0]['action'], '매도 검토')

    def test_recent_collapse_blocks_buy_even_with_good_old_history(self):
        for r in self.c['prices']['rows']:
            if r['at'] >= '2020':
                r['value'] = '1'
        self.assertEqual(evaluate(self.plan, self.snapshot)['decisions'][0]['verification'], 'degraded')

    def test_tiny_samples_and_multiple_search_trials_cannot_produce_strong_buy(self):
        for name in ('minimum_historical', 'minimum_validation', 'minimum_recent'):
            self.plan['policy'][name] = 10000
        self.assertEqual(evaluate(self.plan, self.snapshot)['decisions'][0]['action'], '신규 매수하지 않음')
        self.c['strategy']['trial_count'] = 10
        self.assertEqual(evaluate(self.plan, self.snapshot)['decisions'][0]['grade'], 'C')

    def test_uniform_uptrend_does_not_prove_signal_beats_unconditional_buy(self):
        for i, r in enumerate(self.c['prices']['rows']):
            r['value'] = str(Decimal(100) * Decimal('1.01') ** i)
        bt = run_backtest(self.c, _time(AT))
        # All one-month holding returns are the same. No timing superiority.
        self.assertEqual(approval(bt, self.c['strategy'], self.plan['policy'])[0], 'failed')

    def test_event_review_is_capped_at_C_without_fake_backtest(self):
        self.c.update(mode='event', analog_evidence_ids=['E_DEMAND'])
        r = evaluate(self.plan, self.snapshot)['decisions'][0]
        self.assertEqual((r['grade'], r['action'], r['amount_krw']), ('C', '소액 매수', '500000'))
        self.assertIsNone(r['backtest'])

    def test_maturity_missing_prices_and_next_observation_are_not_zero_returns(self):
        r = evaluate(self.plan, self.snapshot)
        record(self.root, r)
        data = outcome_prices(self.c)
        pending = review(self.root, data, AT)
        self.assertTrue(all(o['state'] == 'pending' for o in pending['outcomes']))
        later = review(self.root, data, '2026-12-10T00:00:00+00:00')
        monthly = next(o for o in later['outcomes'] if o['horizon'] == '1m')
        self.assertEqual(monthly['entry_at'], '2026-10-08T00:00:00+00:00')
        self.assertEqual(monthly['state'], 'completed')
        missing = review(self.root, [], '2027-12-10T00:00:00+00:00')
        self.assertTrue(all(o['state'] == 'missing_data' and o['return_'] is None for o in missing['outcomes']))

    def test_duplicate_run_record_is_idempotent_and_judgment_tampering_rejected(self):
        result = evaluate(self.plan, self.snapshot)
        record(self.root, result)
        record(self.root, result)
        self.assertEqual(len(list((self.root / 'decisions').glob('*.json'))), 1)
        p = next((self.root / 'decisions').glob('*.json'))
        bad = load(p)
        bad['as_of'] = '2020-01-01T00:00:00+00:00'
        p.write_text(encode(bad))
        with self.assertRaises(SourceError):
            review(self.root, [], AT)

    def test_strategy_change_requires_new_version_parent_reason_and_future_validation(self):
        result = evaluate(self.plan, self.snapshot)
        record(self.root, result)
        changed = deepcopy(result)
        s = changed['decisions'][0]['strategy']
        s['conditions'][0]['value'] = '2'
        with self.assertRaises(SourceError):
            record(self.root, changed)
        s.update(
            version='v2',
            parent_sha256=digest(result['decisions'][0]['strategy']),
            locked_at='2026-10-08T00:00:00+00:00',
            revision_reason='수요의 정의 변경으로 미래 검증을 새로 한다.',
        )
        with self.assertRaises(SourceError):
            record(self.root, changed)
        s['splits'].update(validation_start='2026-11-01T00:00:00+00:00', recent_start='2027-01-01T00:00:00+00:00')
        record(self.root, changed)
        self.assertEqual(len(list((self.root / 'strategies' / 'authored_cycle').glob('*.json'))), 2)

    def test_feedback_warning_blocks_next_cycle_and_cannot_use_future_review(self):
        r = dict(
            schema_version='investment-review-v1',
            method_version='immutable_decision_journal_v1',
            as_of=AT,
            strategies={'authored_cycle/v1/synthetic': dict(status='경고')},
        )
        persist_review(self.root, r)
        self.assertEqual(feedback(self.root, '2025-01-01T00:00:00+00:00'), {})
        self.snapshot['strategy_feedback'] = feedback(self.root, AT)
        self.assertEqual(evaluate(self.plan, self.snapshot)['decisions'][0]['action'], '신규 매수하지 않음')

    def test_actual_matured_losses_downgrade_strategy_and_feed_next_judgment(self):
        for month in (7, 9):
            plan, snapshot = dated_experiment(month)
            result = evaluate(plan, snapshot)
            self.assertEqual(result['decisions'][0]['grade'], 'A')
            record(self.root, result)
        data = deepcopy([self.c['prices'], self.c['benchmark']])
        for d in data:
            for month in (7, 9):
                for m, value in ((month, '100'), (month + 1, '90' if d['asset_id'] == 'US_EQUITY' else '100')):
                    at = f'2026-{m:02d}-08T00:00:00+00:00'
                    d['rows'].append(dict(at=at, known_at=at, value=value))
            d['rows'].sort(key=lambda r: r['at'])
        r = review(self.root, data, '2026-11-30T00:00:00+00:00')
        state = r['strategies']['authored_cycle/v1/synthetic']
        self.assertEqual(state['stats']['count'], 2)
        self.assertEqual(state['status'], '경고')
        self.assertIsNotNone(state['diagnostics'])
        persist_review(self.root, r)
        plan, snapshot = dated_experiment(12)
        snapshot['strategy_feedback'] = feedback(self.root, snapshot['as_of'])
        self.assertEqual(evaluate(plan, snapshot)['decisions'][0]['verification'], 'degraded')

    def test_current_definition_and_date_mismatches_are_not_approved(self):
        for key, value in [('unit', 'percent'), ('currency', 'USD'), ('observed_at', '2025-10-01')]:
            snapshot = deepcopy(self.snapshot)
            snapshot['evidence'][0][key] = value
            with self.subTest(key=key):
                self.assertEqual(evaluate(self.plan, snapshot)['decisions'][0]['grade'], 'D')

    def test_date_only_timestamp_and_malformed_policy_are_input_errors(self):
        self.c['features'][0]['known_at'] = '2000-01-01'
        with self.assertRaises(SourceError):
            validate_plan(self.plan)
        bad = default_plan()
        bad['policy'] = None
        with self.assertRaises(SourceError):
            validate_plan(bad)

    def test_total_return_index_is_not_the_current_share_quote(self):
        result = evaluate(self.plan, self.snapshot)
        r = result['decisions'][0]
        self.assertEqual(r['current_price']['value'], '10000')
        self.assertNotEqual(r['current_price']['value'], self.c['prices']['rows'][-1]['value'])

    def test_overlapping_recommendations_and_horizons_are_not_pooled(self):
        result = evaluate(self.plan, self.snapshot)
        record(self.root, result)
        second = deepcopy(result)
        second['as_of'] = '2026-10-08T12:00:00+09:00'
        record(self.root, second)
        report = review(self.root, outcome_prices(self.c), '2026-12-10T00:00:00+00:00')
        self.assertEqual(report['grade_statistics']['1m']['A']['synthetic']['count'], 1)
        self.assertEqual(report['grade_statistics']['1y']['A']['synthetic']['count'], 0)
        self.assertEqual(report['grade_statistics']['1m']['A']['real']['count'], 0)

    def test_report_leads_with_action_allocation_and_never_invents_future_outcomes(self):
        result = evaluate(self.plan, self.snapshot)
        text = render_decision(result)
        self.assertTrue(text.startswith('# 오늘의 투자 결론'))
        self.assertIn('분할 매수', text)
        self.assertIn('4,000,000원', text)
        self.assertIn('현재 시장 추천이 아닙니다', text)
        record(self.root, result)
        r = review(self.root, [], AT)
        self.assertIn('미성숙 결과는 성공으로 세지 않습니다', render_review(r))

    def test_offline_cycle_run_replay_detects_changed_files(self):
        class Run:
            pass

        fake = Run()
        with (
            patch('investment_research.orchestrator.replay_ask', return_value=fake),
            patch('investment_research.investment_cycle.research_snapshot', return_value=self.snapshot),
        ):
            r = run_cycle(self.plan, 'unused', self.root / 'run', ledger=self.root / 'journal')
        self.assertEqual(r, replay_cycle(self.root / 'run'))
        (self.root / 'run' / 'report.md').write_text('changed')
        with self.assertRaises(SourceError):
            replay_cycle(self.root / 'run')

    def test_unverified_current_data_withholds_judgment_on_holding(self):
        # Missing data is not negative evidence: the held position is kept and
        # only new buying stops. v1 asked for a reduction and must still replay.
        self.c['held'] = True
        self.snapshot['evidence'] = [e for e in self.snapshot['evidence'] if e['id'] != 'E_QUOTE']
        row = evaluate(self.plan, self.snapshot)['decisions'][0]
        self.assertEqual((row['grade'], row['action']), ('D', '보유 유지'))
        self.assertIn('현재 투자상품 가격의 검증 원문 연결이 없음', row['blockers'])
        old = evaluate(self.plan, self.snapshot, 'investment_cycle_v1')
        self.assertEqual(old['method_version'], 'investment_cycle_v1')
        self.assertEqual((old['decisions'][0]['grade'], old['decisions'][0]['action']), ('D', '비중 축소 검토'))
        self.c['held'] = False
        self.assertEqual(evaluate(self.plan, self.snapshot)['decisions'][0]['action'], '신규 매수하지 않음')

    def test_observed_failure_still_reduces_holding_despite_data_gap(self):
        self.c['held'] = True
        for r in self.c['prices']['rows']:
            if r['at'] >= '2020':
                r['value'] = '1'
        self.snapshot['evidence'] = [e for e in self.snapshot['evidence'] if e['id'] != 'E_QUOTE']
        row = evaluate(self.plan, self.snapshot)['decisions'][0]
        self.assertEqual((row['verification'], row['grade'], row['action']), ('degraded', 'F', '비중 축소 검토'))

    def test_lookahead_history_cannot_drive_reduction(self):
        # A failure measured on data retrieved after the judgment is look-ahead.
        plan, snapshot = deepcopy(self.plan), deepcopy(self.snapshot)
        plan['synthetic'] = snapshot['synthetic'] = False
        c = plan['candidates'][0]
        c['held'] = True
        for d in (c['prices'], c['benchmark']):
            d['synthetic'] = False
        for r in c['prices']['rows']:
            if r['at'] >= '2020':
                r['value'] = '1'
        row = evaluate(plan, snapshot)['decisions'][0]
        self.assertIn('현재 판단 시점 이후에 확보한 자료다. 실제 당시 보유한 자료로만 승인한다.', row['blockers'])
        self.assertEqual((row['grade'], row['action']), ('D', '보유 유지'))

    def test_saved_v1_cycle_replays_with_its_own_rule(self):
        class Run:
            pass

        self.c['held'] = True
        self.snapshot['evidence'] = [e for e in self.snapshot['evidence'] if e['id'] != 'E_QUOTE']
        with (
            patch('investment_research.orchestrator.replay_ask', return_value=Run()),
            patch('investment_research.investment_cycle.research_snapshot', return_value=self.snapshot),
            patch('investment_research.investment_cycle.VERSION', 'investment_cycle_v1'),
            patch('investment_research.investment_cycle.evaluate.__defaults__', ('investment_cycle_v1',)),
        ):
            saved = run_cycle(self.plan, 'unused', self.root / 'v1')
        self.assertEqual(saved['decisions'][0]['action'], '비중 축소 검토')
        self.assertEqual(replay_cycle(self.root / 'v1'), saved)
        with self.assertRaises(SourceError):
            evaluate(self.plan, self.snapshot, 'investment_cycle_v0')

    def test_reviewed_price_lower_bound_can_face_total_return_benchmark(self):
        # A non-distributing asset's price understates holder return when
        # non-cash distributions are omitted; against a PIT total-return
        # benchmark that can only make approval harder.
        self.c['prices'].update(
            return_kind='price',
            adjustment='unadjusted',
            return_basis='price_lower_bound',
            return_basis_note='authored fixture: no cash distributions',
        )
        validate_plan(self.plan)
        bt = run_backtest(self.c, _time(AT))
        self.assertEqual(bt['blockers'], [])
        self.assertTrue(any('보수적' in x for x in bt['limitations']))
        self.assertEqual(evaluate(self.plan, self.snapshot)['decisions'][0]['grade'], 'A')
        old = run_backtest(self.c, _time(AT), 'pit_event_backtest_v1')
        self.assertIn('배당·분배금을 포함한 실제 상품 수익률이 아니다.', old['blockers'])
        saved = evaluate(self.plan, self.snapshot, 'investment_cycle_v2')
        self.assertEqual(saved['backtest_version'], 'pit_event_backtest_v1')
        self.assertEqual(saved['decisions'][0]['grade'], 'C')

    def test_lower_bound_needs_total_return_benchmark_and_consistent_basis(self):
        self.c['prices'].update(
            return_kind='price', adjustment='unadjusted', return_basis='price_lower_bound', return_basis_note='x'
        )
        self.c['benchmark'].update(return_kind='price', adjustment='unadjusted')
        bt = run_backtest(self.c, _time(AT))
        self.assertIn('비교 시장이 당시 이용 가능했던 총수익 판본이 아니다.', bt['blockers'])
        for basis, kind, adjustment, note in (
            ('price_lower_bound', 'total_return', 'pit_total_return_index', 'x'),
            ('non_distributing_fund_price', 'price', 'unadjusted', 'x'),
            ('price_lower_bound', 'price', 'unadjusted', ''),
            ('guess', 'price', 'unadjusted', 'x'),
        ):
            d = dict(
                self.c['prices'], return_kind=kind, adjustment=adjustment, return_basis=basis, return_basis_note=note
            )
            with self.subTest(basis=basis, kind=kind), self.assertRaises(SourceError):
                validate_dataset(d)
        tr = dict(self.c['benchmark'], return_kind='total_return', adjustment='pit_total_return_index')
        self.c['prices'].update(return_kind='total_return', adjustment='pit_total_return_index')
        self.c['prices'].pop('return_basis')
        self.c['benchmark'] = dict(tr, return_kind='price', adjustment='unadjusted')
        with self.assertRaises(SourceError):
            validate_plan(self.plan)  # total return vs price stays a definition mismatch

    def test_review_cli_and_invalid_plan_exit_codes(self):
        from investment_research.__main__ import main

        save(self.root / 'prices.json', [self.c['prices'], self.c['benchmark']])
        record(self.root / 'ledger', evaluate(self.plan, self.snapshot))
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            code = main(
                [
                    'invest',
                    'review',
                    '--journal',
                    str(self.root / 'ledger'),
                    '--prices',
                    str(self.root / 'prices.json'),
                    '--as-of',
                    AT,
                    '--run-dir',
                    str(self.root / 'review'),
                ]
            )
        self.assertEqual(code, 0)
        self.assertTrue((self.root / 'review' / 'report.md').exists())
        save(self.root / 'bad.json', {})
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            code = main(
                [
                    'invest',
                    'run',
                    str(self.root / 'bad.json'),
                    '--research-run',
                    'absent',
                    '--run-dir',
                    str(self.root / 'bad-run'),
                ]
            )
        self.assertEqual(code, 2)
        self.assertFalse((self.root / 'bad-run').exists())

    def test_ask_pins_decision_plan_and_replays_without_network(self):
        from tests.test_orchestrator import OrchestratorTests
        from investment_research.orchestrator import replay_ask
        from investment_research.orchestrator_report import render_ask_report

        fixture = OrchestratorTests('runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        run = fixture.run_ask('S&P500 지금 어때?', decision_plan=self.plan)
        self.assertTrue((run.directory / 'investment_plan.json').exists())
        self.assertTrue((run.directory / 'investment_decision.json').exists())
        # This fixture's September source IDs do not certify October conditions.
        self.assertEqual(run.investment['decisions'][0]['action'], '신규 매수하지 않음')
        self.assertEqual(render_ask_report(run), render_ask_report(replay_ask(run.directory)))

    def test_invalid_ask_plan_is_rejected_before_source_acquisition(self):
        from investment_research.orchestrator import execute_ask

        with patch(
            'investment_research.orchestrator.acquire_plan', side_effect=AssertionError('no HTTP for invalid plan')
        ):
            with self.assertRaises(SourceError):
                execute_ask('S&P500 지금 어때?', self.root / 'invalid-ask', decision_plan={})
        self.assertFalse((self.root / 'invalid-ask').exists())
