"""Broad scan acceptance fixtures: authored data, no external HTTP or DNS."""

from copy import deepcopy
from dataclasses import replace, asdict
from datetime import timedelta
from decimal import Decimal
from datetime import date
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

from investment_research import scan
from investment_research.orchestrator import execute_ask, replay_ask
from investment_research.orchestrator_report import render_ask_report
from investment_research.models import InterpretationStatus, Review
from investment_research.research_catalog import load_catalog
from investment_research.source_pipeline import _digest
from investment_research.sources import FetchResponse, SourceError
from tests.test_orchestrator import NOW, FINANCIAL
from tests.test_discovery import discovery_fixture, response
from tests import test_korean_data as korean_fixture

QUESTION = '지금 전체 투자판에서 내가 볼 만한 기회 찾아줘.'


def issuer_html(symbol, pe, day='Sep 09 2026', growth='10.0', distribution='4.0'):
    return FetchResponse(
        (
            '<h1>Authored synthetic '
            + symbol
            + '</h1><p>Fund Characteristics as of '
            + day
            + ' Price/Earnings Ratio FY1 The weighted harmonic average of current share price divided by the forecasted one year earnings per share for each security in the fund. '
            'Negative and positive outliers are included in the calculation. '
            + pe
            + ' Est. 3-5 Year EPS Growth Estimates are used to calculate a mean 3-5 year EPS growth rate estimate. '
            + growth
            + '% '
            + 'Fund Distribution Yield The sum of the distributions within the past 365 days divided by Net Asset Value per share, expressed as a percentage. '
            + distribution
            + '%</p>'
        ).encode(),
        'text/html',
    )


def fixture():
    catalog, documents, providers, flow_url = discovery_fixture()
    catalog = replace(catalog, korean=deepcopy(load_catalog().korean), scan=deepcopy(load_catalog().scan))
    # Keep the complete original v2 regression suite; v3 has independent
    # fixtures for its minimum inputs and repeated observation semantics.
    catalog.scan.update(method_version='evidence_shortlist_v2', regional_categories=['reb_sale_index', 'reb_volume'])
    sources = deepcopy(catalog.sources)
    for s in sources['sources']:
        if s['id'] == 'DD_IDX_FACTSET_Q3':
            quote = 'Forward P/E 20.0; revisions 2.0; 5Y average 21.0'
        elif s['id'] == 'KR_SAMSUNG_2026Q2_RESULTS':
            quote = 'The industry-wide upward trend of prices contributed to memory results; device earnings declined due to elevated component cost pressures.'
        elif s['id'] == 'RA_EIA_STEO_GAS':
            quote = 'Forecast 5% above the previous five-year average; production continues to grow.'
        else:
            continue
        s['excerpts'][0]['quote'] = quote
        documents[s['url']] = FetchResponse(('<p>' + quote + '</p>').encode(), 'text/html')
    for identifier in (
        'US_SPDR_GROWTH',
        'US_SPDR_VALUE',
        'US_SPDR_DIVIDEND',
        'COM_HN_AI_DEMAND_BULL',
        'COM_HN_AI_VALUATION_BEAR',
    ):
        if any(s['id'] == identifier for s in sources['sources']):
            continue
        s = deepcopy(sources['sources'][0])
        s['id'] = identifier
        s['url'] = 'https://synthetic-ask.example.org/' + identifier
        s['canonical_url'] = s['url']
        sources['sources'].append(s)
        e = deepcopy(sources['evidence'][0])
        e['id'] = 'E_' + identifier
        e['source_id'] = identifier
        sources['evidence'].append(e)
        documents[s['url']] = FetchResponse(('<p>' + s['excerpts'][0]['quote'] + '</p>').encode(), 'text/html')
    facts = deepcopy(catalog.quoted_facts)
    for identifier, value, basis, unit, context in [
        ('F_SP_FORWARD_12M_PE', '20.0', 'forward_12m_pe', 'ratio', 'Forward P/E 20.0'),
        ('F_Q3_EPS_REVISION', '2.0', 'reported_statistic', 'percent', 'revisions 2.0'),
        ('F_SP_PE_AVG5', '21.0', 'reported_statistic', 'ratio', '5Y average 21.0'),
    ]:
        facts['facts'].append(
            dict(
                id=identifier,
                label='합성 ' + identifier,
                source_evidence_id='E_DD_IDX_FACTSET_Q3',
                quote_context=context,
                quote_token=value,
                value=value,
                unit=unit,
                basis=basis,
                currency='USD',
                entity='SYNTHETIC',
                window='synthetic current quarter',
                observed_at='2026-09-09',
                source_definition=FINANCIAL,
            )
        )
    # The original fixture's old PE quote has changed. Do not inherit its value.
    facts['facts'] = [f for f in facts['facts'] if f['id'] != 'F_PE']
    facts['calculations'] = []
    return replace(catalog, sources=sources, quoted_facts=facts), documents, flow_url


class ScanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.catalog, self.documents, self.flow_url = fixture()
        self.requests = []
        self.mutations = {}
        self.count = 0
        self.current_samsung = korean_fixture.samsung_html()
        self.current_financials = korean_fixture.financial_html()
        self.styles = {'SPY': '20', 'SPYG': '25', 'SPYV': '15', 'SPYD': '12'}
        self.issuer_date = 'Sep 09 2026'
        self.price_pair = (100, 110)
        self.missing = set()
        self.community_preview = 'AI capex is unsustainable and revenue is zero.'
        self.community_original = 'AI capex is high but supplier profit does not establish customer return.'
        for name in (
            'socket.socket.connect',
            'socket.getaddrinfo',
            'investment_research.sources._fetch_http',
            'investment_research.discovery._fetch_http',
        ):
            p = patch(name, side_effect=AssertionError('fixture HTTP/DNS only'))
            p.start()
            self.addCleanup(p.stop)

    reb_envelope = korean_fixture.KoreanCoverageTests.reb_envelope

    def fetch(self, url, timeout, max_bytes):
        if url in self.missing or urlsplit(url).hostname in self.missing:
            raise SourceError('authored synthetic unavailable')
        if url.endswith('/directory/REDDIT_PUBLIC_ACCESS'):
            return FetchResponse(b'authored blocked access', 'text/plain', 403)
        if urlsplit(url).hostname == 'www.ssga.com' and not url.endswith('/robots.txt'):
            self.requests.append(url)
            symbol = url.rsplit('-', 1)[-1].upper()
            return issuer_html(symbol, self.styles[symbol], self.issuer_date)
        if '/products/BTC-USD/candles?' in url:
            self.requests.append(url)
            end = NOW.replace(hour=0, minute=0, second=0, microsecond=0)
            return response(
                [
                    [int((end - timedelta(days=2 - i)).timestamp()), 90, 120, 100, price, 10]
                    for i, price in enumerate(self.price_pair)
                ]
            )
        if 'hn.algolia.com' in url:
            self.requests.append(url)
            return response(
                dict(
                    hits=[
                        dict(
                            objectID='12345',
                            created_at=(NOW - timedelta(days=1)).isoformat(),
                            comment_text=self.community_preview,
                            points=999999,
                        )
                    ]
                )
            )
        if 'hacker-news.firebaseio.com/v0/item/12345.json' in url:
            self.requests.append(url)
            return response(
                dict(
                    id=12345,
                    type='comment',
                    time=int((NOW - timedelta(days=1)).timestamp()),
                    text=self.community_original,
                    score=999999,
                )
            )
        return korean_fixture.KoreanCoverageTests.fetch(self, url, timeout, max_bytes)

    def ask(self, question=QUESTION, **kw):
        self.count += 1
        return execute_ask(
            question, self.root / str(self.count), catalog=self.catalog, fetcher=self.fetch, now=NOW, **kw
        )

    def audit(self, run):
        return scan.assess(run)

    def row(self, run, asset):
        return next(r for r in self.audit(run)['universe'] if r['asset_id'] == asset)

    def test_exact_broad_question_executes_without_clarification(self):
        run = self.ask()
        self.assertEqual(run.input['plan']['modes'], ('opportunity_scan',))
        self.assertFalse(run.input['plan']['clarifications'])
        self.assertTrue((run.directory / 'shortlist.json').exists())
        self.assertIn('scan', run.input['method_versions'])

    def test_multi_asset_universe_includes_KR_bonds_regions_and_strategies(self):
        run = self.ask()
        ids = {m['id'] for m in run.input['methods']}
        self.assertEqual(len(ids), 15)
        self.assertTrue({'KR_GOVERNMENT_3Y', 'VALUE_DIVIDEND', 'GROWTH_THEME', 'BROAD_COMMODITIES', 'ETH'} <= ids)
        self.assertIn('KR_APARTMENTS_SEOUL_GYEONGGI_INCHEON', ids)
        self.assertNotIn('SAMSUNG', ids)

    def test_candidates_have_evidence_counterargument_and_recheck(self):
        run = self.ask()
        a = self.audit(run)
        self.assertGreaterEqual(len(a['candidates']), 2)
        self.assertLessEqual(len(a['candidates']), 4)
        for r in a['universe']:
            if r['asset_id'] in a['candidates']:
                self.assertTrue(r['evidence_ids'])
                self.assertTrue(r['risk'])
                self.assertTrue(r['strengthen'])
                self.assertTrue(r['invalidate'])
                self.assertIn('초안', r['confidence'])

    def test_priorities_are_research_not_return_scores(self):
        a = self.audit(self.ask())
        self.assertEqual(a['candidates'][0], 'KR_GOVERNMENT_3Y')
        self.assertEqual(a['purpose'], 'research_priority_not_investment_ranking')
        self.assertFalse(any('score' in r for r in a['universe']))

    def test_scan_reuses_actual_opportunity_map_and_validation(self):
        run = self.ask()
        self.assertIsNotNone(run.opportunity)
        self.assertIn(dict(function='replay_opportunity', purpose='evidence_gated_scan_shortlist'), run.invocations)
        self.assertEqual(
            {r['asset_id'] for r in run.opportunity.rows if r['priority'] == 'candidate'},
            set(self.audit(run)['candidates']),
        )

    def test_momentum_calculation_is_actual_same_venue_change(self):
        run = self.ask()
        m = next(m for m in run.result.metrics if m.id == 'SCAN_BTC_PRICE_CHANGE')
        self.assertEqual(m.value, Decimal(10))
        self.assertEqual(len(m.input_ids), 2)
        self.assertIn('보조', self.audit(run)['momentum_role'])

    def test_rising_price_alone_does_not_select_and_falling_price_does_not_exclude(self):
        from tests.test_discovery import flow_html

        self.documents[self.flow_url] = flow_html(total='10', fbtc='-')
        rise = self.ask()
        self.assertNotIn('BTC', self.audit(rise)['candidates'])
        self.price_pair = (100, 90)
        fall = self.ask()
        self.assertEqual(self.row(rise, 'BTC')['status'], self.row(fall, 'BTC')['status'])

    def test_popularity_and_large_like_count_do_not_change_priority(self):
        run = self.ask()
        a = self.audit(run)
        self.assertIn('인지도', a['popularity_role'])
        self.assertNotIn('999999', json.dumps(a))
        self.assertIn('관심 증가율', self.row(run, 'GROWTH_THEME')['attention'])

    def test_community_snippet_is_not_evidence(self):
        run = self.ask()
        a = self.audit(run)
        self.assertTrue(any(self.community_original == n['text'] for n in a['narrative_checks']))
        self.assertFalse(any(self.community_preview == e.text for e in run.case.evidence))

    def test_community_factual_claim_is_unverified_not_ROI_proof(self):
        self.community_original = 'AI capex exploded, all AI companies have zero revenue and infinite losses.'
        run = self.ask()
        ns = [n for n in self.audit(run)['narrative_checks'] if n['text'] == self.community_original]
        self.assertTrue(ns)
        self.assertEqual(ns[0]['verification'], 'unverified')
        self.assertTrue(all(n['evidence_id'] not in r['evidence_ids'] for n in ns for r in self.audit(run)['universe']))

    def test_future_or_stale_issuer_data_is_not_current(self):
        self.issuer_date = 'Jan 01 2026'
        run = self.ask()
        self.assertNotIn('VALUE_DIVIDEND', self.audit(run)['candidates'])
        self.issuer_date = 'Dec 01 2026'
        future = self.ask()
        self.assertNotIn('VALUE_DIVIDEND', self.audit(future)['candidates'])

    def test_newer_characteristics_replace_old_catalog(self):
        run = self.ask()
        records = [e for e in run.case.evidence if e.provenance.definition['measure'] == 'SSGA_FY1_HARMONIC_PE']
        self.assertEqual({e.value for e in records}, {Decimal('20'), Decimal('25'), Decimal('15'), Decimal('12')})
        self.assertEqual(
            next(
                m
                for m in run.result.metrics
                if m.id == 'SCAN_EY_' + next(e.id for e in records if e.value == Decimal('25'))
            ).value,
            Decimal(4),
        )

    def test_different_dates_do_not_support_style_comparison(self):
        run = self.ask()
        evidence = tuple(
            (
                replace(
                    e,
                    period='2026-09-08',
                    provenance=replace(e.provenance, definition={**e.provenance.definition, 'period': '2026-09-08'}),
                )
                if e.provenance.definition['scope'].startswith('SPYV ')
                else e
            )
            for e in run.case.evidence
        )
        altered = replace(run, case=replace(run.case, evidence=evidence))
        self.assertNotIn('VALUE_DIVIDEND', self.audit(altered)['candidates'])

    def test_negative_earnings_revision_changes_priority(self):
        catalog = deepcopy(self.catalog)
        # Change both the quote and transcribed inputs, never just a conclusion.
        src = catalog.sources
        s = next(s for s in src['sources'] if s['id'] == 'DD_IDX_FACTSET_Q3')
        s['excerpts'][0]['quote'] = s['excerpts'][0]['quote'].replace('revisions 2.0', 'revisions -2.0')
        self.documents[s['url']] = FetchResponse(('<p>' + s['excerpts'][0]['quote'] + '</p>').encode(), 'text/html')
        f = next(f for f in catalog.quoted_facts['facts'] if f['id'] == 'F_Q3_EPS_REVISION')
        f.update(value='-2.0', quote_token='-2.0', quote_context='revisions -2.0')
        self.catalog = catalog
        run = self.ask()
        self.assertNotIn('US_EQUITY', self.audit(run)['candidates'])

    def test_business_improvement_does_not_claim_cheap_price(self):
        r = self.row(self.ask(), 'KR_EQUITY')
        self.assertEqual(r['status'], 'research_candidate')
        self.assertIn('현재 주가', r['price_context'])
        self.assertIn('없다', r['price_context'])
        self.assertIn('이미 가격', r['risk'])

    def test_gas_inventory_forecast_counterargument_and_curve_gap(self):
        r = self.row(self.ask(), 'NATGAS')
        self.assertEqual(r['status'], 'weak_case')
        self.assertIn('선물곡선', r['price_context'])
        self.assertIn('공식 전망', r['confidence'])
        self.assertNotEqual(r['confidence'], '매수 확신 높음')

    def test_cash_is_normal_alternative_without_fabricated_KRW_rate(self):
        r = self.row(self.ask(), 'CASH')
        self.assertEqual(r['status'], 'normal_alternative')
        self.assertIn('미확보', r['price_context'])
        self.assertIn('우월성', r['why_now'])
        self.assertNotIn('CASH', self.audit(self.ask())['candidates'])

    def test_unavailable_evidence_not_unattractive(self):
        r = self.row(self.ask(), 'BROAD_COMMODITIES')
        self.assertEqual(r['status'], 'insufficient')
        self.assertEqual(r['evidence_ids'], [])
        self.assertNotEqual(r['status'], 'weak_case')

    def test_regional_scope_and_shallow_depth_preserved(self):
        run = self.ask()
        needs = [n for n in run.input['evidence_needs'] if n['category'].startswith('reb_')]
        self.assertEqual({n['region'] for n in needs}, {'서울', '경기', '인천'})
        self.assertEqual({n['category'] for n in needs}, {'reb_sale_index', 'reb_volume'})
        self.assertNotIn('semiconductor_coverage', run.input)

    def test_scoped_momentum_candles_reject_duplicate_gaps_and_live_bar(self):
        now = NOW.replace(hour=0, minute=0, second=0, microsecond=0)
        t = int((now - timedelta(days=1)).timestamp())
        candidate = dict(document=dict(retrieved_at=NOW.isoformat()), index_identity_fields={'product': 'BTC-USD'})
        for stamps in [(t, t), (t - 3 * 86400, t), (t, t + 86400)]:
            with self.subTest(stamps=stamps), self.assertRaises(SourceError):
                scan.parse_candidate('scan_btc_closes_v1', response([[s, 1, 2, 1, 2, 3] for s in stamps]), candidate)
        with self.assertRaises(SourceError):
            scan.parse_candidate(
                'scan_btc_closes_v1', response([[t - 86400, 1, 2, 1, 'not a price', 3], [t, 1, 2, 1, 2, 3]]), candidate
            )

    def test_missing_prices_never_invent_a_momentum(self):
        self.missing = {'api.exchange.coinbase.com'}
        run = self.ask()
        self.assertFalse(any(m.id == 'SCAN_BTC_PRICE_CHANGE' for m in run.result.metrics))
        self.assertIn('미확보', self.row(run, 'BTC')['momentum'])

    def test_evidence_traceability_and_manifest_selection(self):
        run = self.ask()
        m = json.loads((run.directory / 'run_manifest.json').read_text())
        known = {e.id for e in run.case.evidence}
        for r in m['opportunity_shortlist']['universe']:
            self.assertTrue(set(r['evidence_ids']) <= known)
        for c in m['calculations']:
            self.assertTrue(set(c['input_ids']) <= known)
        self.assertIn('shortlist.json', m['artifact_sha256'])
        self.assertIn('shortlist_review.json', m['artifact_sha256'])

    def test_replay_does_not_discover_route_or_access_network(self):
        run = self.ask()
        before = (run.directory / 'report.md').read_bytes()
        with (
            patch(
                'investment_research.orchestrator.discover_sources', side_effect=AssertionError('discovery in replay')
            ),
            patch('investment_research.orchestrator.plan_research', side_effect=AssertionError('routing in replay')),
        ):
            replay = replay_ask(run.directory)
        self.assertEqual(before, render_ask_report(replay).encode())
        self.assertEqual(self.audit(run), self.audit(replay))

    def test_same_input_clock_and_fixtures_repeat_identically(self):
        a = self.ask()
        b = self.ask()
        self.assertEqual(a.digest, b.digest)
        self.assertEqual(render_ask_report(a), render_ask_report(b))

    def test_final_report_explanatory_main_and_detailed_appendix(self):
        run = self.ask()
        report = render_ask_report(run)
        body = report.split('<details>')[0]
        for heading in (
            '오늘 시장을 이해하는 핵심',
            '지금 가장 볼 만한 곳',
            '지금은 덜 매력적인 곳',
            '시장 전체 그림',
            '다음에 깊게 볼 것',
        ):
            self.assertIn('## ' + heading, body)
        self.assertIn('합성 검증 자료', body)
        self.assertNotIn('SHA-256', body)
        self.assertIn('snapshot:', report)

    def test_independent_direct_questions_do_not_enter_scan(self):
        questions = [
            'BTC 지금 어때?',
            '천연가스 지금 들어갈 만해?',
            '삼성전자랑 SK하이닉스 비교해줘.',
            '서울 아파트 지금 어때?',
            'S&P500이랑 미국 국채 비교해줘.',
        ]
        for question in questions:
            with self.subTest(question=question):
                run = self.ask(question)
                self.assertNotIn('opportunity_scan', run.input['plan']['modes'])
                self.assertNotIn('scan', run.input)
                self.assertFalse((run.directory / 'shortlist.json').exists())

    def test_current_source_modified_or_rejected_cannot_select(self):
        run = self.ask()
        case = replace(
            run.case,
            evidence=tuple(
                replace(e, interpretation=Review(InterpretationStatus.REJECTED, None, None, 'synthetic rejected'))
                for e in run.case.evidence
            ),
        )
        altered = replace(run, case=case)
        self.assertEqual(self.audit(altered)['candidates'], [])

    def test_interpretation_cannot_promote_narrative_to_financial_support(self):
        run = self.ask()
        a = self.audit(run)
        ns = {n['evidence_id'] for n in a['narrative_checks']}
        self.assertTrue(ns)
        self.assertFalse(any(set(r['evidence_ids']) & ns for r in a['universe']))

    def test_scan_does_not_include_full_deep_dive_supplier_universe(self):
        run = self.ask()
        self.assertFalse(any(m['id'].startswith('COMPANY_') or m['id'] == 'SAMSUNG' for m in run.input['methods']))
        self.assertLessEqual(len({i['provider_id'] for i in run.discovery['indexes']}), 12)

    def test_saved_candidate_comparison_is_independent_and_preserves_original_question(self):
        previous = self.ask()
        run = self.ask('1위랑 2위 비교해줘.', context_run=previous.directory)
        self.assertEqual(run.input['question'], '1위랑 2위 비교해줘.')
        self.assertEqual(run.input['plan']['modes'], ('compare',))
        self.assertNotIn('scan', run.input)
        self.assertEqual([m['id'] for m in run.input['methods']], ['KR_GOVERNMENT_3Y', 'US_EQUITY'])
        self.assertEqual(render_ask_report(run), render_ask_report(replay_ask(run.directory)))
        reference = scan.resolve_reference('1위랑 2위 세후로 비교해줘. 2년 뒤 주택 구입할 돈이야.', previous)
        self.assertIn('세후로 비교해줘. 2년 뒤 주택 구입할 돈이야.', reference['resolved_question'])
        self.assertIn('한국 3년 국채', reference['resolved_question'])
        self.assertIn('S&P500', reference['resolved_question'])

    def test_candidate_reference_cannot_invent_a_missing_rank(self):
        previous = self.ask()
        with self.assertRaises(SourceError):
            self.ask('9위 후보 자세히 봐.', context_run=previous.directory)
        self.assertFalse((self.root / str(self.count)).exists())

    def test_high_multiple_is_two_sided_expectation_risk_not_automatic_rejection(self):
        catalog = deepcopy(self.catalog)
        s = next(s for s in catalog.sources['sources'] if s['id'] == 'DD_IDX_FACTSET_Q3')
        s['excerpts'][0]['quote'] = s['excerpts'][0]['quote'].replace('P/E 20.0', 'P/E 30.0')
        self.documents[s['url']] = FetchResponse(('<p>' + s['excerpts'][0]['quote'] + '</p>').encode(), 'text/html')
        f = next(f for f in catalog.quoted_facts['facts'] if f['id'] == 'F_SP_FORWARD_12M_PE')
        f.update(value='30.0', quote_token='30.0', quote_context='Forward P/E 30.0')
        self.catalog = catalog
        a = self.audit(self.ask())
        row = next(r for r in a['universe'] if r['asset_id'] == 'US_EQUITY')
        self.assertEqual(row['overheat_check']['status'], 'expectation_pressure')
        self.assertEqual(row['status'], 'research_candidate')

    def test_latest_macro_value_uses_observation_date_not_hash_or_daily_label(self):
        run = self.ask()
        e = next(e for e in run.case.evidence if e.provenance.definition['measure'] == 'KR_GOVERNMENT_NOMINAL_3Y')
        old = replace(e, id='ZZ_OLD_OBSERVATION', value=Decimal('2'), observed_at=date(2026, 9, 8), period='daily')
        new = replace(e, id='AA_NEW_OBSERVATION', value=Decimal('4'), observed_at=date(2026, 9, 9), period='daily')
        rest = tuple(x for x in run.case.evidence if x.provenance.definition['measure'] != 'KR_GOVERNMENT_NOMINAL_3Y')
        r = self.row(replace(run, case=replace(run.case, evidence=(*rest, old, new))), 'KR_GOVERNMENT_3Y')
        self.assertEqual(r['evidence_ids'], [new.id])

    def test_other_regional_or_macro_data_cannot_fill_missing_Seoul(self):
        self.missing = {'www.reb.or.kr'}
        run = self.ask()
        r = self.row(run, 'KR_APARTMENTS_SEOUL_GYEONGGI_INCHEON')
        self.assertEqual(r['status'], 'insufficient')
        self.assertEqual(r['evidence_ids'], [])
        self.assertTrue(self.row(run, 'KR_GOVERNMENT_3Y')['evidence_ids'])

    def test_unknown_portfolio_limits_personalization_without_blocking_market_scan(self):
        run = self.ask()
        self.assertIsNone(run.input['portfolio'])
        self.assertTrue(self.audit(run)['candidates'])
        self.assertIn('미확인', self.audit(run)['personalization'])
        self.assertNotIn('최적 비중', render_ask_report(run).split('<details>')[0])

    def test_combined_scan_keeps_explicit_deep_dive_and_does_not_autodive_shortlist(self):
        run = self.ask('전체 시장 보고 천연가스는 깊게 봐줘.')
        self.assertEqual(set(run.input['plan']['modes']), {'opportunity_scan', 'asset_deep_dive'})
        deep = [t for t in run.input['tasks'] if t['mode'] == 'asset_deep_dive']
        self.assertEqual(deep[0]['method_ids'], ['NATGAS'])
        self.assertEqual(len(deep), 1)

    def test_one_candle_currency_or_definition_mismatch_blocks_calculation(self):
        run = self.ask()
        price_ids = {i for m in run.result.metrics if m.id == 'SCAN_BTC_PRICE_CHANGE' for i in m.input_ids}
        target = next(iter(price_ids))
        bad = tuple(replace(e, currency='KRW') if e.id == target else e for e in run.case.evidence)
        self.assertFalse(
            any(m.id == 'SCAN_BTC_PRICE_CHANGE' for m in scan.calculations(replace(run.case, evidence=bad), run.cutoff))
        )


if __name__ == '__main__':
    unittest.main()
