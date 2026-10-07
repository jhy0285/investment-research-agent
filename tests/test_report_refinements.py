"""Asset-specific explanations and a compact, evidence-bound Scan ending."""
from copy import deepcopy
from dataclasses import asdict,replace
import re
import unittest

from investment_research.orchestrator_report import render_ask_report,_render_legacy_ask_report
from investment_research.report_explanations import explain_terms
from investment_research.sources import SourceError
from tests import test_orchestrator as general
from tests import test_scan as scan_fixture
from tests import test_korean_data as korean_fixture


class ReportRefinementTests(unittest.TestCase):
    def harness(self,klass):
        fixture=klass('runTest');fixture.setUp();self.addCleanup(fixture.doCleanups)
        return fixture

    @staticmethod
    def body(run):return render_ask_report(run).split('<details>',1)[0]

    @staticmethod
    def ending(body):return body.split('## 그래서 지금 시장은 어떤 시장인가\n',1)[1].strip()

    def test_btc_has_its_own_economics_without_corporate_ratios(self):
        fixture=self.harness(general.OrchestratorTests);run=fixture.run_ask('BTC 지금 어때?')
        before=deepcopy((asdict(run.case),asdict(run.result),run.input))
        body=self.body(run)
        for term in ('PER','P/E','EPS','CAPEX','이익수익률','예상 이익과 현재 가격'):
            self.assertNotIn(term,body)
        self.assertIn('실제 자금 유입과 사용 수요',body)
        self.assertIn('레버리지',body)
        self.assertIn('담보가 부족해지면',body)
        self.assertNotIn('하루 기준 배수',body)
        self.assertEqual(before,(asdict(run.case),asdict(run.result),run.input))
        self.assertIn(_render_legacy_ask_report(run).rstrip(),render_ask_report(run))

    def test_exchange_rate_calculation_is_only_in_market_environment(self):
        fixture=self.harness(general.OrchestratorTests);run=fixture.run_ask('BTC 지금 어때?');body=self.body(run)
        asset,environment=body.split('## 시장 환경',1)
        self.assertNotIn('직전 관측치 대비 변화',asset)
        self.assertNotIn('계산한 숫자가 투자 판단',asset)
        self.assertIn('직전 관측치 대비 변화',environment)
        self.assertIn('분석 대상 자체의 가격 수익률은 아니다',environment)
        self.assertIn('2026-09-08 / 2026-09-09',environment)
        self.assertTrue(run.macro.metrics)

    def test_crypto_etf_keeps_crypto_scope(self):
        fixture=self.harness(general.OrchestratorTests);body=self.body(fixture.run_ask('IBIT 지금 어때?'))
        self.assertIn('ETF',body)
        self.assertNotIn('PER',body);self.assertNotIn('P/E',body)
        self.assertNotIn('CAPEX는',body)

    def test_crypto_property_compare_does_not_explain_equity_or_bond_metrics(self):
        fixture=self.harness(general.OrchestratorTests);body=self.body(fixture.run_ask('Bitcoin vs 동탄 아파트'))
        self.assertIn('동탄',body)
        self.assertIn('매도 가능성',body)
        self.assertNotIn('PER',body);self.assertNotIn('P/E',body)
        self.assertNotIn('국채 이자·주식 이익수익률',body)
        self.assertIn('현재 이 조건을 지원할 데이터가 부족하다',body)

    def test_equity_bond_compare_keeps_applicable_earnings_math(self):
        fixture=self.harness(general.OrchestratorTests);run=fixture.run_ask('S&P500이랑 미국 국채 비교해줘')
        body=self.body(run);main=body.split('## 시장 환경',1)[0]
        self.assertIn('합성 F\\_PE: **20.000 배**',main)
        self.assertIn('합성 이익수익률',main)
        self.assertIn('약정 이자를 받는 일',main)
        self.assertIn('차이를 그대로 추가 기대수익으로 해석할 수 없다',main)
        self.assertIn('합성 이익수익률',render_ask_report(run).split('<details>',1)[1])

    def test_first_definition_follows_asset_section_in_mixed_report(self):
        lines=['## Bitcoin','', 'PER로 평가하지 않는다.','',
               '## 미국 주식','', 'Forward P/E를 확인한다.','']
        text='\n'.join(explain_terms(lines,extended=True,korean_suffixes=True,
            families={'crypto','equity'},section_families={'## Bitcoin':{'crypto'},'## 미국 주식':{'equity'}}))
        crypto,equity=text.split('## 미국 주식',1)
        self.assertNotIn('PER은 주가',crypto)
        self.assertIn('Forward P/E는',equity)
        generic='\n'.join(explain_terms(['valuation과 momentum을 본다.',''],families={'commodity'}))
        self.assertNotIn('좋은 회사',generic)
        self.assertNotIn('실적 개선과 함께',generic)
        self.assertIn('보유 비용',generic)

    def test_scan_plus_btc_does_not_leak_other_assets_into_deep_dive(self):
        fixture=self.harness(general.OrchestratorTests);run=fixture.run_ask('전체 시장 보고 BTC는 깊게 봐줘.')
        body=self.body(run);deep=body.split('## Bitcoin — 투자 판단의 핵심',1)[1]
        deep=deep.split('## 그래서 지금 시장은 어떤 시장인가',1)[0]
        for term in ('PER','Forward P/E','예상 이익과 현재 가격','한국 원자료','원화 국고채와 미국 주식'):
            self.assertNotIn(term,deep)
        self.assertNotIn('미국 소비자물가',deep)
        self.assertIn('시장 환경',deep)
        self.assertIsNotNone(run.deep)  # The Scan really has equity facts to omit.

    def test_korean_bond_only_does_not_gain_us_equity_or_fx_paragraph(self):
        fixture=self.harness(korean_fixture.KoreanCoverageTests)
        run=fixture.ask('한국 3년 국채 지금 어때?');body=self.body(run)
        self.assertIn('한국 국고채',body)
        self.assertNotIn('S&P 500',body)
        self.assertNotIn('이익수익률',body)
        self.assertNotIn('달러 자산 자체의 수익',body)
        self.assertNotIn('PER',body)

    def test_scan_non_candidates_are_compact_but_states_and_audit_survive(self):
        fixture=self.harness(scan_fixture.ScanTests);run=fixture.ask();audit=deepcopy(fixture.audit(run))
        report=render_ask_report(run);body=self.body(run)
        non=body.split('## 지금은 덜 매력적인 곳',1)[1].split('\n## ',1)[0]
        self.assertIn('| 영역 | 지금 상태 | 짧게 보는 이유 |',non)
        self.assertNotIn('### ',non)
        self.assertNotIn('다시 볼 조건:',non)
        for row in audit['universe']:
            if row['asset_id'] not in audit['candidates']:
                self.assertIn(row['name'].replace('&','&amp;'),non)
        self.assertIn('데이터 부족',non)
        self.assertIn('현재 긍정 근거가 약함',non)
        self.assertIn('자료가 부족한 자산을 나쁜 투자라고 판정하지 않는다',non)
        self.assertEqual(audit,fixture.audit(run))
        self.assertIn(_render_legacy_ask_report(run).rstrip(),report.split('<details>',1)[1])

    def test_scan_finishes_with_one_to_three_linked_paragraphs(self):
        fixture=self.harness(scan_fixture.ScanTests);run=fixture.ask();body=self.body(run)
        end=self.ending(body);paragraphs=re.split(r'\n\s*\n',end)
        self.assertGreaterEqual(len(paragraphs),1);self.assertLessEqual(len(paragraphs),3)
        self.assertNotIn('\n## ',end)
        self.assertIn('이익이 좋아지는 속도',end)
        self.assertIn('이자를 포기',end)
        self.assertIn('시장 전체에서 가장 좋은 투자라고 말할 수는 없다',end)
        for target in re.findall(r'\]\(#([^)]+)\)',end):self.assertIn('id="'+target+'"',render_ask_report(run))
        self.assertNotIn('매수해야',end);self.assertNotIn('유동성이 늘었다',end)

    def test_no_candidate_scan_does_not_force_a_regime_or_cash_superiority(self):
        fixture=self.harness(scan_fixture.ScanTests)
        def unavailable(url,timeout,max_bytes):raise SourceError('authored unavailable fixture')
        fixture.fetch=unavailable
        run=fixture.ask()
        self.assertFalse(fixture.audit(run)['candidates'])
        end=self.ending(self.body(run))
        self.assertIn('연결할 연구 후보를 고르지 못했다',end)
        self.assertIn('현금이 더 낫다는 결론은 아니다',end)
        self.assertNotIn('지금은 매수',end)
        self.assertNotIn('확실한 상승장',end)
        self.assertLessEqual(len(re.split(r'\n\s*\n',end)),3)

    def test_previous_explanatory_style_keeps_its_original_explanations(self):
        fixture=self.harness(general.OrchestratorTests);run=fixture.run_ask('BTC 지금 어때?')
        previous=replace(run,input={**run.input,'report_style':'ask_report_explanatory_ko_v3'})
        body=self.body(previous)
        self.assertIn('P/E 또는 PER은 주가',body)
        self.assertLess(body.index('직전 관측치 대비 변화'),body.index('## 이 질문에 중요한 시장 환경'))
        self.assertNotIn('P/E 또는 PER은 주가',self.body(run))
        first_guard=replace(run,input={**run.input,'report_style':'ask_report_explanatory_ko_v4'})
        self.assertIn('하루 기준 배수',self.body(first_guard))


if __name__=='__main__':unittest.main()
