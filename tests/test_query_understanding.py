"""Question identity and scope acceptance tests, with authored offline sources."""

from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from investment_research.orchestrator import execute_ask, replay_ask
from investment_research.orchestrator_report import render_ask_report
from investment_research.routing import ResearchMode as Mode, plan_research
from investment_research.sources import FetchResponse
from tests.test_orchestrator import NOW, synthetic_catalog

COMPARE = '한국 3년 국채랑 S&P500 중 지금 신규자금 어디가 더 합리적이야?'
SCAN = '지금 전체 투자판에서 내가 볼 만한 기회 찾아줘.'
PROPERTY = '서울/수도권 아파트 지금 투자 관점에서 어때?'


class QueryUnderstandingTests(unittest.TestCase):
    def test_korean_three_year_new_capital_comparison_preserves_identity(self):
        p = plan_research(COMPARE)
        self.assertEqual(p.modes, (Mode.COMPARE,))
        self.assertFalse(p.clarifications)
        a, b = p.tasks[0].subjects
        self.assertEqual(a.label, '한국 3년 국채')
        self.assertEqual(a.asset_class, 'bond')
        self.assertEqual(a.country, 'KR')
        self.assertEqual(a.maturity.value, '3')
        self.assertEqual(a.maturity.unit, 'years')
        self.assertIsNone(a.duration)
        self.assertEqual(b.label, 'S&P 500')
        self.assertEqual(a.raw_text, '한국 3년 국채')
        self.assertTrue(p.understanding['requested_comparison'])
        self.assertIn('new_capital_allocation', [d['kind'] for d in p.understanding['investment_purpose']])
        self.assertIn('지금', [d['raw_text'] for d in p.understanding['time_context']])

    def test_comparison_survives_words_between_choice_and_question(self):
        for q in (
            '한국 3년 국채랑 S&P500 중 지금 신규자금 어디에 넣을까?',
            '한국3년물 국채와 S&P500 가운데 앞으로 어느 쪽이 나아?',
            '한국 국채(3년)이랑 S&P500 중 신규자금은 어디가 좋아?',
            '삼성전자랑 SK하이닉스 지금 둘 중 뭐가 더 나아?',
        ):
            with self.subTest(q=q):
                self.assertEqual(plan_research(q).modes, (Mode.COMPARE,))

    def test_explicit_numeric_tenors_and_countries_stay_on_their_alternatives(self):
        subjects = plan_research('한국 3년 국채와 미국 10년 국채 비교해줘').tasks[0].subjects
        self.assertEqual([(s.country, s.maturity.value) for s in subjects], [('KR', '3'), ('US', '10')])
        self.assertEqual([s.raw_text for s in subjects], ['한국 3년 국채', '미국 10년 국채'])

    def test_same_country_different_maturities_are_not_deduplicated(self):
        subjects = plan_research('한국 3년 국채 vs 한국 10년 국채').tasks[0].subjects
        self.assertEqual(len(subjects), 2)
        self.assertEqual([s.maturity.value for s in subjects], ['3', '10'])

    def test_month_maturity_is_not_years_or_interest_rate_duration(self):
        s = plan_research('미국 6개월 국채 어때?').tasks[0].subjects[0]
        self.assertEqual(s.country, 'US')
        self.assertEqual(s.maturity.value, '6')
        self.assertEqual(s.maturity.unit, 'months')
        self.assertIsNone(s.duration)

    def test_marketwide_investment_board_question_starts_scan_without_asset_clarification(self):
        p = plan_research(SCAN)
        self.assertEqual(p.modes, (Mode.OPPORTUNITY_SCAN,))
        self.assertEqual(p.understanding['scope'], 'broad_cross_asset')
        self.assertFalse(p.clarifications)
        self.assertEqual(p.tasks[0].subjects, ())

    def test_marketwide_scan_variants_and_negation_do_not_overexpand_specific_questions(self):
        for q in ('전체 투자판에서 투자할 기회 찾아줘', '시장 전반에서 내가 볼 만한 기회 찾아줘'):
            self.assertEqual(plan_research(q).modes, (Mode.OPPORTUNITY_SCAN,))
        for q in ('BTC에 투자기회가 있어?', '전체 투자판을 훑지 말고 BTC 지금 어때?'):
            self.assertEqual(plan_research(q).modes, (Mode.ASSET_DEEP_DIVE,))

    def test_seoul_capital_area_investment_question_preserves_geography(self):
        p = plan_research(PROPERTY)
        self.assertEqual(p.modes, (Mode.ASSET_DEEP_DIVE,))
        self.assertFalse(p.clarifications)
        s = p.tasks[0].subjects[0]
        self.assertEqual(s.asset_class, 'real_estate')
        self.assertEqual(s.regions, ('서울', '수도권'))
        self.assertEqual(s.country, 'KR')
        self.assertEqual(s.label, '서울/수도권 아파트')
        self.assertEqual(s.raw_text, '서울/수도권 아파트')
        self.assertIn('investment_economics', [d['kind'] for d in p.understanding['investment_purpose']])

    def test_region_delimiters_and_two_properties_keep_local_scopes(self):
        for q in ('서울과 수도권 아파트 투자 관점에서 어때?', '서울, 수도권 아파트 어때?'):
            self.assertEqual(plan_research(q).tasks[0].subjects[0].regions, ('서울', '수도권'))
        subjects = plan_research('서울 아파트 vs 부산 아파트').tasks[0].subjects
        self.assertEqual([s.regions for s in subjects], [('서울',), ('부산',)])

    def test_explicit_user_constraints_and_strategy_have_original_text_spans(self):
        q = '배당투자 투자기간 10년, 신규자금 1000만원, 대출 없이 원화 기준으로 지금 어때?'
        p = plan_research(q)
        c = p.understanding['user_constraints']
        self.assertEqual(p.tasks[0].subjects[0].strategies, ('dividend',))
        self.assertEqual(next(x for x in c if x['kind'] == 'holding_period')['value'], '10')
        amount = next(x for x in c if x['kind'] == 'investment_budget')
        self.assertEqual((amount['value'], amount['unit']), ('1000', '만원'))
        self.assertIn('debt_constraint', {x['kind'] for x in c})
        self.assertIn('currency_constraint', {x['kind'] for x in c})
        for d in (*c, *p.understanding['investment_purpose'], *p.understanding['time_context']):
            self.assertEqual(q[d['span'][0] : d['span'][1]], d['raw_text'])

    def test_maturity_duration_and_future_cash_need_are_not_interchanged(self):
        q = '한국 3년 국채랑 S&P500 비교해줘. 2년 뒤 집 살 돈이고 듀레이션 1년을 원해.'
        p = plan_research(q)
        s = p.tasks[0].subjects[0]
        self.assertEqual(s.maturity.value, '3')
        self.assertIsNone(s.duration)
        constraints = {d['kind']: d for d in p.understanding['user_constraints']}
        self.assertEqual(constraints['future_cash_need']['value'], '2')
        self.assertEqual(constraints['interest_rate_duration']['value'], '1')

    def test_holding_period_after_bond_is_not_parsed_as_its_maturity(self):
        p = plan_research('국채 3년 뒤 집 살 돈으로 어때?')
        self.assertIsNone(p.tasks[0].subjects[0].maturity)
        self.assertEqual(p.understanding['user_constraints'][0]['kind'], 'future_cash_need')

    def test_explicit_mode_override_preserves_question_constraints(self):
        p = plan_research(COMPARE, modes=[Mode.ASSET_DEEP_DIVE])
        self.assertEqual(p.modes, (Mode.ASSET_DEEP_DIVE,))
        self.assertTrue(p.understanding['requested_comparison'])
        self.assertEqual(p.tasks[0].subjects[0].country, 'KR')
        self.assertEqual(p.tasks[0].subjects[0].maturity.value, '3')

    def test_six_acceptance_questions_route_independently(self):
        questions = [
            ('BTC 지금 어때?', Mode.ASSET_DEEP_DIVE),
            ('천연가스 지금 들어갈 만해?', Mode.ASSET_DEEP_DIVE),
            ('삼성전자랑 SK하이닉스 지금 둘 중 뭐가 더 나아?', Mode.COMPARE),
            (COMPARE, Mode.COMPARE),
            (SCAN, Mode.OPPORTUNITY_SCAN),
            (PROPERTY, Mode.ASSET_DEEP_DIVE),
        ]
        for q, mode in questions:
            with self.subTest(q=q):
                p = plan_research(q)
                self.assertEqual(p.modes, (mode,))
                self.assertFalse(p.clarifications)


class QueryOrchestrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.catalog, self.documents = synthetic_catalog()
        self.requests = []
        self.sequence = 0
        for target in ('socket.socket.connect', 'socket.getaddrinfo', 'investment_research.sources._fetch_http'):
            blocker = patch(target, side_effect=AssertionError('offline authored fixture only'))
            blocker.start()
            self.addCleanup(blocker.stop)

    def fetch(self, url, timeout, max_bytes):
        self.requests.append(url)
        if url.endswith('/robots.txt'):
            return FetchResponse(b'User-agent: *\nAllow: /\n', 'text/plain')
        return self.documents[url]

    def ask(self, q):
        self.sequence += 1
        return execute_ask(q, self.root / str(self.sequence), catalog=self.catalog, fetcher=self.fetch, now=NOW)

    def test_korean_three_year_comparison_never_executes_generic_us_bond_method(self):
        run = self.ask(COMPARE)
        self.assertEqual(tuple(run.input['plan']['modes']), (Mode.COMPARE,))
        self.assertEqual([m['id'] for m in run.input['methods']], ['US_EQUITY'])
        t = run.input['tasks'][0]
        self.assertEqual(t['subject_method_ids'], [None, 'US_EQUITY'])
        self.assertEqual(t['subjects'][0]['country'], 'KR')
        self.assertEqual(t['subjects'][0]['maturity']['value'], '3')
        self.assertEqual(t['condition_coverage'][0]['status'], 'unavailable')
        self.assertFalse(any('cash_bills' in u for u in self.requests))
        report = render_ask_report(run)
        self.assertIn('한국 3년 국채', report)
        self.assertIn('신규자금', report)
        self.assertIn('현재 이 조건을 지원할 데이터가 부족하다', report)
        self.assertNotIn('발행국이 지정되지 않아', report)
        self.assertNotIn('미국 단기 Treasury', report)

    def test_marketwide_question_invokes_existing_scan_not_an_empty_clarification_report(self):
        run = self.ask(SCAN)
        self.assertIsNotNone(run.opportunity)
        self.assertTrue(self.requests)
        self.assertTrue(run.case.evidence)
        self.assertFalse(run.input['plan']['clarifications'])
        self.assertIn(dict(function='replay_opportunity', purpose='opportunity_scan'), run.invocations)
        self.assertNotIn('Deep Dive 대상', render_ask_report(run))

    def test_seoul_scope_is_preserved_without_nationwide_source_substitution(self):
        run = self.ask(PROPERTY)
        report = render_ask_report(run)
        self.assertEqual(run.input['tasks'][0]['subjects'][0]['regions'], ('서울', '수도권'))
        self.assertEqual(run.input['methods'][0]['label'], '서울/수도권 아파트')
        self.assertEqual(self.requests, [])
        self.assertEqual(run.case.evidence, ())
        self.assertEqual(run.case.alternatives[0].name, '서울/수도권 아파트')
        self.assertIn('현재 이 조건을 지원할 데이터가 부족하다', report)
        self.assertNotIn('동탄', report)
        self.assertNotIn('USD/KRW', report)

    def test_foreign_country_and_numeric_maturity_are_kept_as_unavailable(self):
        for q, country, tenor in [('일본 3년 국채 어때?', 'JP', '3'), ('미국 7년 국채 어때?', 'US', '7')]:
            with self.subTest(q=q):
                run = self.ask(q)
                s = run.input['tasks'][0]['subjects'][0]
                self.assertEqual((s['country'], s['maturity']['value']), (country, tenor))
                self.assertEqual(run.input['methods'], [])
                self.assertEqual(self.requests, [])
                self.assertIn('현재 이 조건을 지원할 데이터가 부족하다', render_ask_report(run))

    def test_foreign_property_is_not_replaced_with_korean_housing(self):
        run = self.ask('일본 도쿄 아파트 지금 어때?')
        s = run.input['tasks'][0]['subjects'][0]
        self.assertEqual(s['country'], 'JP')
        self.assertEqual(s['regions'], ('도쿄',))
        self.assertEqual(run.input['methods'], [])
        self.assertEqual(self.requests, [])

    def test_question_amounts_are_context_not_invented_portfolio_values(self):
        run = self.ask('BTC 투자기간 5년, 신규자금 1000만원, 대출 없이 지금 어때?')
        self.assertIsNone(run.input['portfolio'])
        self.assertEqual(run.portfolio.metrics, ())
        self.assertIn('투자기간 5년', run.case.brief.horizon)
        self.assertNotIn('total_assets', run.case.profile.fields)
        report = render_ask_report(run)
        self.assertIn('신규자금 1000만원', report)
        self.assertIn('대출 없이', report)

    def test_question_constraints_are_in_manifest_and_replay_without_rerouting(self):
        run = self.ask(COMPARE)
        m = json.loads((run.directory / 'run_manifest.json').read_text())
        q = m['query_understanding']
        self.assertEqual(q['original_question'], COMPARE)
        self.assertEqual(q['assets_or_alternatives'][0]['maturity']['value'], '3')
        self.assertEqual(q['assets_or_alternatives'][0]['country'], 'KR')
        with patch('investment_research.orchestrator.plan_research', side_effect=AssertionError('no replay rerouting')):
            replay = replay_ask(run.directory)
        self.assertEqual(replay.digest, run.digest)
        self.assertEqual(render_ask_report(replay), render_ask_report(run))

    def test_dated_question_does_not_replace_requested_date_with_current_data(self):
        run = self.ask('2025-06-30 기준 BTC 지금 어때?')
        q = run.input['plan']['understanding']
        self.assertEqual(q['data_limits'][0]['raw_text'], '2025-06-30 기준')
        self.assertEqual(q['data_limits'][0]['status'], 'unavailable')
        self.assertEqual(self.requests, [])
        self.assertEqual(run.case.evidence, ())
        self.assertIn('현재 자료로 당시 판단을 대체하지 않는다', render_ask_report(run))

    def test_duration_requirement_is_not_approved_from_a_maturity_or_yield(self):
        run = self.ask('미국 국채 듀레이션 3년을 원해')
        q = run.input['plan']['understanding']
        limit = next(d for d in q['data_limits'] if d['kind'] == 'interest_rate_duration')
        self.assertEqual(limit['status'], 'unavailable')
        self.assertIn('채권 만기로 대체하지 않는다', render_ask_report(run))


if __name__ == '__main__':
    unittest.main()
