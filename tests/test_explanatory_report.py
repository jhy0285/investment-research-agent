"""Presentation acceptance: unchanged research, understandable default prose."""
from copy import deepcopy
from dataclasses import asdict, replace
import hashlib
import json
import re
import unittest
from unittest.mock import patch

from investment_research.orchestrator import replay_ask, _execute
from investment_research.orchestrator_report import (
    EXPLANATORY_REPORT_VERSION, REPORT_VERSION, render_ask_report,
    _render_legacy_ask_report, build_manifest,
)
from investment_research.report_explanations import explain_terms
from investment_research.sources import SourceError
from investment_research.models import VerificationStatus
from tests import test_orchestrator as general
from tests import test_scan as scan_fixture
from tests import test_discovery as discovery_fixture
from tests import test_commodity_deep as commodity_fixture
from tests import test_semiconductor_data as semi_fixture


class ExplanationTermsTests(unittest.TestCase):
    def test_first_use_explains_meaning_and_investment_effect_once(self):
        original=['## 기업의 투자','', 'CAPEX와 capacity를 본다.','', 'CAPEX를 다시 본다.','']
        text='\n'.join(explain_terms(original))
        self.assertIn('CAPEX는 공장·설비·데이터센터',text)
        self.assertIn('투자비 회수가 늦어지고',text)
        self.assertLess(text.index('CAPEX는'),text.index('CAPEX와 capacity'))
        self.assertEqual(text.count('CAPEX는 공장'),1)
        self.assertIn('공급과잉 위험',text)
        self.assertEqual(original[2],'CAPEX와 capacity를 본다.')

    def test_table_stays_contiguous_and_number_is_never_rewritten(self):
        rows=['| 항목 | 값 |','| --- | --- |','| Forward P/E | 19.00 |','| TTM EPS | 4.50 |']
        text='\n'.join(explain_terms(['## 가격','',*rows,'']))
        self.assertIn('\n'.join(rows),text)
        self.assertLess(text.index('Forward P/E는'),text.index(rows[0]))
        self.assertIn('예상 이익이 실제로 나오지 않으면',text)
        self.assertIn('TTM은 최근 열두 달',text)
        self.assertNotIn('Trailing P/E는',text)

    def test_futures_terms_keep_cost_conditions_not_return_promises(self):
        text='\n'.join(explain_terms(['contango / backwardation / roll / collateral','']))
        self.assertIn('뒤에 만기가 오는 선물이 더 비싼',text)
        self.assertIn('미래 수익을 보장하지는 않는다',text)
        self.assertIn('실제 기여는 별도 자료',text)

    def test_extended_funding_explanation_does_not_annualize_a_small_ratio(self):
        text='\n'.join(explain_terms(['funding 0.000125 fraction',''],extended=True))
        self.assertIn('해당 시간 구간의 비율이지 연간 금리가 아니다',text)
        self.assertIn('0.000125 fraction',text)

    def test_korean_particles_do_not_hide_first_acronym_use(self):
        text='\n'.join(explain_terms(['EPS를 확인하고 PER로 비교한다.',''],korean_suffixes=True))
        self.assertIn('EPS는 회사 이익',text)
        self.assertIn('P/E 또는 PER은 주가',text)
        self.assertLess(text.index('EPS는'),text.index('EPS를 확인'))
        unrelated='\n'.join(explain_terms(['proper reporting',''],korean_suffixes=True))
        self.assertNotIn('PER은 주가',unrelated)


class ExplanatoryReportTests(unittest.TestCase):
    def harness(self,klass):
        fixture=klass('runTest');fixture.setUp();self.addCleanup(fixture.doCleanups)
        return fixture

    @staticmethod
    def body(run):return render_ask_report(run).split('<details>',1)[0]

    def test_new_ask_pins_presentation_version_and_replays_without_acquisition(self):
        fixture=self.harness(general.OrchestratorTests);run=fixture.run_ask('BTC 지금 어때?')
        manifest=fixture.manifest(run)
        self.assertEqual(run.input['report_style'],EXPLANATORY_REPORT_VERSION)
        self.assertEqual(manifest['method_versions']['report'],EXPLANATORY_REPORT_VERSION)
        with patch('investment_research.orchestrator.acquire_plan',side_effect=AssertionError('no acquisition')):
            self.assertEqual(render_ask_report(replay_ask(run.directory)),render_ask_report(run))

    def test_style_rendering_does_not_change_evidence_claims_or_calculations(self):
        fixture=self.harness(general.OrchestratorTests);run=fixture.run_ask('S&P500이랑 미국 국채 비교해줘')
        before=deepcopy((asdict(run.case),asdict(run.result),run.input,run.invocations))
        legacy=_render_legacy_ask_report(run);new=render_ask_report(run)
        self.assertEqual(before,(asdict(run.case),asdict(run.result),run.input,run.invocations))
        self.assertIn(legacy.rstrip(),new)
        body=self.body(run)
        self.assertIn('그 돈이 전부 배당으로 지급되는 것은 아니',body)
        self.assertIn('차이를 그대로 추가 기대수익으로 해석할 수 없다',new)
        self.assertIn('약정 이자를 받는 일',body)

    def test_explicit_btc_scope_does_not_gain_unrelated_assets(self):
        fixture=self.harness(general.OrchestratorTests);run=fixture.run_ask('BTC 지금 어때?')
        body=self.body(run)
        self.assertNotIn('서울',body);self.assertNotIn('천연가스',body)
        self.assertIn('가격이 오른다는 것은',body)
        self.assertIn('걱정할 점',body);self.assertIn('이미 기대하고 있는 것',body)
        self.assertIn('무엇이 바뀌면 판단이 달라지는가',body)

    def test_discovered_numbers_have_time_and_economic_meaning(self):
        fixture=self.harness(discovery_fixture.DiscoveryTests);run=fixture.ask()
        body=self.body(run)
        self.assertIn('순유입은 들어온 돈에서 빠져나간 돈',body)
        self.assertIn('장기 수요나 다음 가격을 확정할 수 없다',body)
        self.assertIn('관측 ',body)
        self.assertIn('검증에서 확인한 범위',body)
        self.assertIn('발언이 있었다는 사실과 내용이 맞다는 것은 다르다',body)

    def test_unavailable_flows_are_explicit_in_default_body(self):
        fixture=self.harness(discovery_fixture.DiscoveryTests)
        provider=fixture.providers['FARSIDE_PUBLISHER']
        fixture.documents[provider['seed_url']]=TimeoutError()
        body=self.body(fixture.ask())
        self.assertIn('이번 판단을 제한하는 자료 공백',body)
        self.assertIn('BTC 현물 ETF 자금흐름: 미확보',body)
        self.assertIn('현재 가격·수요·위험에 대한 판단을 제한',body)

    def test_quarantined_forward_fact_is_not_current_financial_value(self):
        fixture=self.harness(general.OrchestratorTests);run=fixture.run_ask('S&P500 지금 어때?')
        case=replace(run.case,evidence=tuple(replace(e,verification=VerificationStatus.UNVERIFIED)
            if e.id=='F_PE' else e for e in run.case.evidence))
        metrics=tuple(m for m in run.result.metrics if 'F_PE' not in m.input_ids)
        changed=replace(run,input={**run.input,'evidence_validation':{'numeric_ids':['F_PE']}},case=case,
            result=replace(run.result,case=case,metrics=metrics),
            evidence_validation={'quarantined_ids':['F_PE'],'records':[]})
        body=self.body(changed)
        self.assertNotIn('합성 F_PE: **20',body)
        self.assertIn('추가 검증을 위해 격리한 자료',body)
        # The original matched passage remains available as raw source detail.
        self.assertIn('Forward P/E 20.0',render_ask_report(changed).split('<details>',1)[1])

    def test_source_hash_and_ids_are_hidden_but_body_links_resolve(self):
        fixture=self.harness(discovery_fixture.DiscoveryTests);run=fixture.ask()
        report=render_ask_report(run);body=self.body(run)
        for jargon in ('SHA-256','snapshot:','INSIGHT_','E_DISC_','CALC_'):
            self.assertNotIn(jargon,body)
        self.assertIn('SHA-256',report)
        for target in re.findall(r'\]\(#([^\)]+)\)',body):self.assertIn('id="'+target+'"',report)

    def test_small_verified_fraction_keeps_precision_and_korean_unit(self):
        fixture=self.harness(discovery_fixture.DiscoveryTests);run=fixture.ask();body=self.body(run)
        self.assertIn('0.000125 비율 (8시간 기준, 연간 금리 아님)',body)
        self.assertNotIn('0.000 fraction',body)
        self.assertIn('달러/BTC',body);self.assertNotIn('USD\\_per\\_BTC',body)
        old=replace(run,input={**run.input,'report_style':'ask_report_explanatory_ko_v1'})
        self.assertIn('0.000 fraction',self.body(old))
        self.assertEqual(run.result.metrics,old.result.metrics)

    def test_english_community_original_is_available_in_details(self):
        fixture=self.harness(discovery_fixture.DiscoveryTests);run=fixture.ask();report=render_ask_report(run)
        narrative=next(e for e in run.case.evidence if e.kind=='observed_narrative')
        self.assertNotIn(narrative.text,self.body(run))
        self.assertIn(narrative.text,report.split('<details>',1)[1])
        self.assertIn('의미는 아직 검증하지 못했다',self.body(run))

    def test_portfolio_missing_inputs_do_not_become_zero_or_safe_allocation(self):
        fixture=self.harness(general.OrchestratorTests)
        data=general.portfolio_data(cash_krw=None,debt_krw=None,future_cash_needs=None,horizon_months=None)
        run=fixture.run_ask('내 포트폴리오 괜찮아?',portfolio=data);body=self.body(run)
        self.assertFalse(run.portfolio.metrics)
        self.assertIn('미확인 금액을 영으로 채워',body)
        self.assertIn('부채',body);self.assertIn('보유표 기준일',body)
        self.assertIn('추가 보유의 적절성',body)

    def test_portfolio_weights_are_composition_not_risk_contributions(self):
        fixture=self.harness(general.OrchestratorTests)
        run=fixture.run_ask('내 포트폴리오 괜찮아?',portfolio=general.portfolio_data());body=self.body(run)
        self.assertIn('이 항목이 차지하는 비중',body)
        self.assertIn('위험 기여도와는 달라',body)
        self.assertIn('이미 같은 산업이나 자산',body)

    def test_unsupported_conditions_and_geography_remain_in_default_body(self):
        fixture=self.harness(general.OrchestratorTests)
        run=fixture.run_ask('서울/수도권 아파트 지금 투자 관점에서 어때?');body=self.body(run)
        self.assertIn('서울',body);self.assertIn('수도권',body)
        self.assertIn('현재 이 조건을 지원할 데이터가 부족하다',body)
        self.assertIn('지역 지수가 올랐다는 이유만으로',body)

    def test_scan_keeps_exact_shortlist_and_detailed_candidate_logic(self):
        fixture=self.harness(scan_fixture.ScanTests);run=fixture.ask();audit=fixture.audit(run)
        report=render_ask_report(run);body=self.body(run)
        legacy=_render_legacy_ask_report(run)
        self.assertEqual(audit,fixture.audit(run));self.assertIn(legacy.rstrip(),report)
        for identifier in audit['candidates']:
            row=next(r for r in audit['universe'] if r['asset_id']==identifier)
            candidate=body.split('### '+str(row['reference_number'])+'. ',1)[1].split('\n### ',1)[0]
            for heading in ('왜 지금 보는가','쉽게 말하면','좋은 점','걱정할 점','시장이 이미 기대하고 있는 것','무엇을 확인하면 더 강한 기회가 되는가','지금 판단'):
                self.assertIn('#### '+heading,candidate)
            self.assertIn(row['invalidate'],candidate)
            self.assertIn(row['strengthen'],candidate)

    def test_scan_distinguishes_missing_data_from_weak_economics(self):
        fixture=self.harness(scan_fixture.ScanTests);run=fixture.ask();body=self.body(run)
        self.assertIn('자료가 부족한 자산을 나쁜 투자라고 판정하지 않는다',body)
        self.assertIn('현재 긍정 근거가 약함',body)
        self.assertIn('데이터 부족',body)
        self.assertIn('이는 투자 매력 점수가 아니다',body)
        self.assertNotIn('최적 비중',body)

    def test_combined_scan_shows_requested_deep_dive_only(self):
        fixture=self.harness(scan_fixture.ScanTests)
        run=fixture.ask('전체 시장 보고 천연가스는 깊게 봐줘.');body=self.body(run)
        self.assertIn('천연가스 — 투자 판단의 핵심',body)
        tasks=[t for t in run.input['tasks'] if t['mode']=='asset_deep_dive']
        self.assertEqual([t['method_ids'] for t in tasks],[['NATGAS']])

    def test_gas_definitions_and_examples_do_not_change_real_calculations(self):
        fixture=self.harness(commodity_fixture.CommodityTests);run=fixture.ask(commodity_fixture.GAS)
        metrics=deepcopy(asdict(run.result));body=self.body(run)
        self.assertIn('원문 행의 기간',body)
        self.assertNotIn('evidence 관측일',body)
        self.assertIn('가스가 내는 열량의 단위',body)
        self.assertIn('다음은 현재 계약가격이 아닌 설명용 예시',body)
        self.assertIn('최신 약관이나 실제 성과를',body)
        self.assertIn('월간 생산·수출 합계도 현재 하루',body)
        self.assertEqual(metrics,asdict(run.result))

    def test_broad_commodity_explanation_keeps_attribution_limits(self):
        fixture=self.harness(commodity_fixture.CommodityTests);run=fixture.ask(commodity_fixture.BROAD);body=self.body(run)
        self.assertIn('현재 비중이 아니다',body)
        self.assertIn('정확한 기여도는 계산하지 않는다',body)
        self.assertIn('상품 전체가 올라도 일부 원자재만',body)
        self.assertIn('담보 이자는',body)

    def test_semiconductor_business_price_and_cash_remain_separate(self):
        fixture=self.harness(semi_fixture.SemiconductorTests);run=fixture.ask();body=self.body(run)
        self.assertIn('CAPEX는 공장',body)
        self.assertIn('영업이익률은 매출',body)
        self.assertIn('실제 과거 이익을 같은 산술 방식',body)
        self.assertIn('미래에도 이어질 수 있는 이익인지',body)
        self.assertIn('원공시',body)
        self.assertIn('현재 데이터로 우열 판단 어려움',body)

    def test_unknown_style_is_rejected_instead_of_silent_fallback(self):
        fixture=self.harness(general.OrchestratorTests);run=fixture.run_ask('BTC 지금 어때?')
        unknown=replace(run,input={**run.input,'report_style':'unknown'})
        with self.assertRaisesRegex(SourceError,'unsupported ask report style'):render_ask_report(unknown)

    def test_markerless_saved_report_stays_byte_identical_on_replay(self):
        fixture=self.harness(general.OrchestratorTests);run=fixture.run_ask('BTC 지금 어때?')
        data=deepcopy(run.input);del data['report_style']
        path=run.directory/'input.json';path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
        legacy_run=_execute(run.directory,data);legacy=render_ask_report(legacy_run)
        self.assertEqual(legacy,_render_legacy_ask_report(legacy_run))
        report_path=run.directory/'report.md';report_path.write_text(legacy)
        manifest=build_manifest(legacy_run,legacy)
        (run.directory/'run_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        before=hashlib.sha256(report_path.read_bytes()).hexdigest()
        replayed=replay_ask(run.directory)
        self.assertEqual(manifest['method_versions']['report'],REPORT_VERSION)
        self.assertEqual(render_ask_report(replayed),legacy)
        self.assertEqual(before,hashlib.sha256(report_path.read_bytes()).hexdigest())


if __name__=='__main__':unittest.main()
