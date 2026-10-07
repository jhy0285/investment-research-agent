"""Authored synthetic Deep Dive fixtures; no live financial evidence or HTTP."""
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import asdict, replace
from datetime import timedelta
from decimal import Decimal
from io import StringIO
import json
import re
import unittest
from unittest.mock import patch

from investment_research.deep_dive import SECTIONS, deep_dive_manifest, load_deep_dive_review, replay_deep_dive
from investment_research.deep_dive_report import render_deep_dive_report
from investment_research.models import InterpretationStatus, VerificationStatus
from investment_research.opportunity_report import _target
from investment_research.source_pipeline import _digest, load_source_plan
from investment_research.sources import FetchResponse, SourceError, acquire
from tests import test_opportunity as opportunity_fixture

ACQUIRED=opportunity_fixture.ACQUIRED
CUTOFF=opportunity_fixture.CUTOFF

QUOTE = ('Synthetic fixture only. Forward P/E 20.0; alternative P/E 20.5. Treasury 3.0 percent. '
         'Operating cash flow 120 USD million; cash PP&E (35) USD million.')
DEFINITION = dict(measure='synthetic financial passage',unit='ratio and percent and USD million',
                  period='synthetic quarter',currency='USD',scope='synthetic issuer and index',adjustment='authored fixture')
DEFAULT_PARENT = object()


class DeepDiveTests(unittest.TestCase):
    def setUp(self):
        # Reuse only the existing synthetic acquisition fixture, not its tests.
        self.fixture=opportunity_fixture.OpportunityTests('runTest');self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        fixture=self.fixture
        rows=fixture.review_data['rows']
        template=next(r for r in rows if r['asset_id']=='CASH')
        us=next(r for r in rows if r['asset_id']=='US_EQUITY')
        us['priority']='candidate';us['candidate']=deepcopy(template['candidate'])
        self.parent=fixture.replay()
        self.path=fixture.directory/'deep_review.json';self.plan_path=fixture.directory/'deep_plan.json'
        self.store=fixture.directory/'deep_snapshots'
        source=deepcopy(fixture.source_data['sources'][0])
        source.update(id='S_FIN',url='https://synthetic-opportunity.example.org/s_fin',
                      canonical_url='https://synthetic-opportunity.example.org/s_fin',title='Authored synthetic financial fixture',
                      asset_ids=['US_EQUITY','SHORT_BOND','LONG_BOND'])
        source['excerpts']=[dict(id='Q_FIN',quote=QUOTE,locator='synthetic fixture paragraph',definition=DEFINITION)]
        community=deepcopy(source);community.update(id='S_FIN_COM',type='community',
            url='https://synthetic-opportunity.example.org/s_fin_com',canonical_url='https://synthetic-opportunity.example.org/s_fin_com')
        self.plan_data=dict(schema_version='1',id='SYNTHETIC_DEEP_PLAN',question='합성 원문을 비교할 수 있는가?',
            as_of='2026-09-10',asset_ids=['US_EQUITY','SHORT_BOND','LONG_BOND'],sources=[source,community],claims=[],
            evidence=[dict(id=eid,source_id=sid,excerpt_id='Q_FIN',view=view,kind=kind,definition=DEFINITION,
                           extraction=None,interpretation=None,limitations=['합성 테스트 입력이다.'])
                      for eid,sid,view,kind in [('E_FIN','S_FIN','fundamental','external_fact'),
                                             ('E_FIN_COM','S_FIN_COM','community','observed_narrative')]])
        fixture.documents[source['url']]=FetchResponse(('<p>'+QUOTE+'</p>').encode(),'text/html')
        fixture.documents[community['url']]=FetchResponse(('<p>'+QUOTE+'</p>').encode(),'text/html')
        facts=[]
        for name,token,context,unit,basis in [
            ('PE','20.0','Forward P/E 20.0','ratio','forward_12m_pe'),
            ('TREASURY','3.0','Treasury 3.0 percent','percent','nominal_cmt_investment_yield'),
            ('OCF','120','Operating cash flow 120 USD million','USD_million','operating_cash_flow'),
            ('PPE','(35)','cash PP&E (35) USD million','USD_million','cash_ppe_outflow')]:
            value='-35' if token=='(35)' else token
            facts.append(dict(id='F_'+name,label='합성 '+name,source_evidence_id='E_FIN',quote_context=context,
                quote_token=token,value=value,unit=unit,basis=basis,currency='USD',entity='SYNTHETIC',
                window='synthetic quarter',observed_at='2026-09-10',source_definition=DEFINITION))
        statement=dict(text='합성 비교 조건을 검토하며 실제 시장 판단으로 사용하지 않는다.',
                       evidence_ids=['F_PE','CALC_GAP'],role='interpretation')
        sections={name:[deepcopy(statement)] for name in SECTIONS}
        sections['conclusions']=[deepcopy(statement) for _ in range(3)]
        sections['community']=[dict(text='합성 발언을 관측했으며 내용을 사실로 확인하지 않았다.',
                                    evidence_ids=['E_FIN_COM'],role='narrative')]
        self.data=dict(schema_version='deep-dive-review-v1',id='SYNTHETIC_DEEP_REVIEW',
            question='합성 입력의 원문과 대안 정의를 보존하는가?',as_of=CUTOFF.isoformat(),author='합성 테스트 작성자',
            review_status='draft',parent=dict(id=self.parent.review.id,review_sha256=self.parent.review.input_digest,
                                             input_sha256=self.parent.input_digest),facts=facts,
            calculations=[dict(id=name,label='합성 '+name,method=method,input_ids=refs,limitations=['합성 값이며 투자 수익 예측이 아니다.'])
                for name,method,refs in [('CALC_EY','earnings_yield_v1',['F_PE']),
                                        ('CALC_GAP','descriptive_yield_gap_v1',['F_PE','F_TREASURY']),
                                        ('CALC_CASH','cash_residual_v1',['F_OCF','F_PPE'])]],
            tables=[dict(id='VALUATION',title='합성 값',columns=['항목','값'],notes=['합성 fixture다.'],
                         rows=[[dict(text='합성 이익수익률',refs=[]),dict(text='',refs=['CALC_EY'])]])],
            sections=sections,judgment='mixed',comparison_limits=['미래 수익은 계산하지 않는다.'],
            sampling_limits=['합성 발언이며 대표성이 없다.'],unknowns=['실제 사용자 금융정보는 미확인이다.'],
            next_research='다음 합성 질문의 필요 자료를 검토한다.')
        self.prepare()

    def prepare(self,*,now=ACQUIRED):
        self.plan_path.write_text(json.dumps(self.plan_data),encoding='utf-8')
        self.plan=load_source_plan(self.plan_path)
        self.pins=dict(schema_version='1',plan_id=self.plan.id,sources_digest=_digest([asdict(s) for s in self.plan.sources]),
                       snapshots={s.id:acquire(s,self.store,fetcher=self.fixture.fetcher,now=now).snapshot_id for s in self.plan.sources})
        self.fixture.requests.clear()

    def review(self):
        self.path.write_text(json.dumps(self.data,ensure_ascii=False),encoding='utf-8')
        return load_deep_dive_review(self.path)

    def replay(self,review=None,parent=DEFAULT_PARENT):
        f=self.fixture
        return replay_deep_dive(review or self.review(),self.plan,self.store,self.pins,
                               f.macro_plan,f.macro_store,f.macro_pins,self.parent if parent is DEFAULT_PARENT else parent)

    def standalone(self):
        self.data['parent']=None
        self.data['profile']={'base_currency':{'status':'self_reported','value':'KRW'},
                              'debt':{'status':'unknown','value':None},
                              'holdings':{'status':'unknown','value':None}}
        self.data['horizon']='UNKNOWN · 사용자 기간은 미확인이다.'

    def test_independent_arithmetic_and_pending_economic_interpretation(self):
        run=self.replay();values={m.id:m.value for m in run.metrics}
        self.assertEqual(values['CALC_EY'],Decimal('5'))
        self.assertEqual(values['CALC_GAP'],Decimal('2'))
        self.assertEqual(values['CALC_CASH'],Decimal('85'))
        self.assertTrue(all(c.verification==VerificationStatus.UNVERIFIED for c in run.case.claims))
        self.assertTrue(all(c.interpretation.status==InterpretationStatus.PENDING for c in run.case.claims))
        fact=next(e for e in run.case.evidence if e.id=='F_PE')
        self.assertEqual(fact.verification,VerificationStatus.SUPPORTED)
        self.assertEqual(fact.interpretation.status,InterpretationStatus.PENDING)
        self.assertIsNone(run.case.profile.fields['debt'].value)
        self.assertEqual(self.fixture.requests,[])
        for basis in ('forward_fy1_harmonic_pe','trailing_pe'):
            self.data['facts'][0]['basis']=basis
            self.assertEqual(next(m.value for m in self.replay().metrics if m.id=='CALC_EY'),Decimal('5'))

    def test_wrong_numeric_token_substring_and_missing_context_rejected(self):
        original=deepcopy(self.data)
        for changes in [dict(value='19.0'),dict(quote_token='20',value='20'),dict(quote_context='imagined EPS 20.0')]:
            with self.subTest(changes=changes):
                self.data=deepcopy(original);self.data['facts'][0].update(changes)
                with self.assertRaises(SourceError):self.replay()

    def test_ambiguous_repeated_token_requires_narrow_context(self):
        quote=QUOTE+' Again P/E 20.0.'
        for source in self.plan_data['sources']:source['excerpts'][0]['quote']=quote
        for url in [s['url'] for s in self.plan_data['sources']]:
            self.fixture.documents[url]=FetchResponse(('<p>'+quote+'</p>').encode(),'text/html')
        self.prepare();self.data['facts'][0]['quote_context']=quote
        with self.assertRaisesRegex(SourceError,'ambiguous'):self.replay()

    def test_parenthesized_pe_reference_is_not_negative_accounting_cash(self):
        quote=QUOTE.replace('Forward P/E 20.0','Forward P/E (20.0)')
        self.plan_data['sources'][0]['excerpts'][0]['quote']=quote
        self.fixture.documents[self.plan_data['sources'][0]['url']]=FetchResponse(('<p>'+quote+'</p>').encode(),'text/html')
        self.data['facts'][0]['quote_context']='Forward P/E (20.0)'
        self.prepare()
        self.assertEqual(next(m.value for m in self.replay().metrics if m.id=='CALC_EY'),Decimal('5'))

    def test_currency_source_definition_and_silent_unit_scaling_rejected(self):
        original=deepcopy(self.data)
        for index,changes in [(0,dict(currency=None)),(0,dict(source_definition={**DEFINITION,'adjustment':'invented'})),
                              (2,dict(unit='USD_billion'))]:
            with self.subTest(changes=changes):
                self.data=deepcopy(original);self.data['facts'][index].update(changes)
                with self.assertRaises(SourceError):self.replay()

    def test_yield_gap_requires_same_date_usd_and_nominal_investment_definition(self):
        original=deepcopy(self.data)
        for changes in [dict(observed_at='2026-09-09'),dict(basis='reported_statistic')]:
            with self.subTest(changes=changes):
                self.data=deepcopy(original);self.data['facts'][1].update(changes)
                with self.assertRaisesRegex(SourceError,'same-date'):self.replay()
        self.data=deepcopy(original)
        for f in self.data['facts']:f['currency']=None;f['source_definition']={**DEFINITION,'currency':None}
        for s in self.plan_data['sources']:s['excerpts'][0]['definition']={**DEFINITION,'currency':None}
        for e in self.plan_data['evidence']:e['definition']={**DEFINITION,'currency':None}
        self.prepare()
        with self.assertRaisesRegex(SourceError,'same-date'):self.replay()

    def test_zero_pe_invalid_even_if_source_contains_zero(self):
        quote=QUOTE.replace('Forward P/E 20.0','Forward P/E 0.0')
        self.plan_data['sources'][0]['excerpts'][0]['quote']=quote
        self.fixture.documents[self.plan_data['sources'][0]['url']]=FetchResponse(('<p>'+quote+'</p>').encode(),'text/html')
        self.data['facts'][0].update(value='0.0',quote_token='0.0',quote_context='Forward P/E 0.0')
        self.prepare()
        with self.assertRaisesRegex(SourceError,'positive'):self.replay()

    def test_cash_residual_rejects_other_company_period_and_positive_outflow(self):
        original=deepcopy(self.data)
        for changes in [dict(entity='OTHER'),dict(window='other period')]:
            with self.subTest(changes=changes):
                self.data=deepcopy(original);self.data['facts'][3].update(changes)
                with self.assertRaisesRegex(SourceError,'cash residual'):self.replay()
        self.data=deepcopy(original);self.data['facts'][3].update(quote_token='35',value='35')
        with self.assertRaisesRegex(SourceError,'negative sign'):self.replay()
        self.data=deepcopy(original)
        quote=QUOTE.replace('(35) USD million','35 USD million')
        self.plan_data['sources'][0]['excerpts'][0]['quote']=quote
        self.fixture.documents[self.plan_data['sources'][0]['url']]=FetchResponse(('<p>'+quote+'</p>').encode(),'text/html')
        self.data['facts'][3].update(quote_token='35',value='35',quote_context='cash PP&E 35 USD million')
        self.prepare()
        with self.assertRaisesRegex(SourceError,'cash residual'):self.replay()

    def test_community_cannot_supply_financial_scalars(self):
        self.data['facts'][0]['source_evidence_id']='E_FIN_COM'
        with self.assertRaisesRegex(SourceError,'community numbers'):self.replay()

    def test_community_observation_never_upgrades_economic_truth(self):
        self.data['sections']['bull_case'][0]['evidence_ids']=['E_FIN_COM']
        run=self.replay()
        self.assertEqual(run.sections['bull_case'][0]['status'],'withheld')
        self.assertEqual(run.sections['community'][0]['status'],'draft')
        # The reused pipeline confirms utterance existence, not its contents.
        self.assertEqual(next(e for e in run.case.evidence if e.id=='E_FIN_COM').interpretation.status,InterpretationStatus.PENDING)
        self.assertTrue(all(c.verification==VerificationStatus.UNVERIFIED for c in run.case.claims))

    def test_future_retrieval_suppresses_numbers_claims_and_judgment(self):
        self.prepare(now=CUTOFF+timedelta(seconds=1))
        run=self.replay();body=render_deep_dive_report(run).split('## 부록')[0]
        self.assertEqual(run.effective_judgment,'insufficient evidence')
        self.assertNotIn('CALC_EY',{m.id for m in run.metrics})
        self.assertTrue(all(f['status']=='withheld' for f in run.facts))
        self.assertNotIn('합성 비교 조건을 검토하며',body)
        self.assertNotIn('5 %',body)
        self.assertNotIn('**mixed**',body)
        self.assertEqual(deep_dive_manifest(run,render_deep_dive_report(run))['judgment']['effective'],'insufficient evidence')

    def test_stale_source_and_future_scalar_observation_withheld(self):
        self.data['as_of']=(CUTOFF+timedelta(days=10)).isoformat()
        run=self.replay()
        self.assertEqual(run.effective_judgment,'insufficient evidence')
        self.assertTrue(all(f['status']=='withheld' for f in run.facts))
        self.data['as_of']=CUTOFF.isoformat();self.data['facts'][0]['observed_at']='2026-09-11'
        run=self.replay()
        self.assertEqual(run.effective_judgment,'insufficient evidence')
        self.assertNotIn('CALC_EY',{m.id for m in run.metrics})

    def test_failed_acquisition_retains_withholding_not_fabricated_facts(self):
        self.fixture.documents[self.plan_data['sources'][0]['url']]=FetchResponse(b'denied','text/html',status=503)
        self.prepare();run=self.replay();report=render_deep_dive_report(run)
        self.assertTrue(all(f['status']=='withheld' for f in run.facts))
        self.assertEqual(run.effective_judgment,'insufficient evidence')
        self.assertNotIn('F_PE',{e.id for e in run.case.evidence})
        self.assertIn(_target('E_FIN'),report)

    def test_missing_refs_direct_prose_figures_and_numeric_table_text_rejected(self):
        original=deepcopy(self.data)
        for target,value in [('ref','IMAGINED'),('prose','합성 EPS 99.0이 좋다.'),('cell','99.0')]:
            with self.subTest(target=target):
                self.data=deepcopy(original)
                if target=='ref':self.data['sections']['bull_case'][0]['evidence_ids']=[value]
                elif target=='prose':self.data['sections']['bull_case'][0]['text']=value
                else:self.data['tables'][0]['rows'][0][1]['text']=value
                with self.assertRaises(SourceError):self.replay()
        self.data=deepcopy(original)
        self.data['sections']['bull_case'][0]['text']='합성 FY1에서는 회계 정의를 구분한다.'
        self.assertEqual(self.replay().sections['bull_case'][0]['status'],'draft')

    def test_parent_hashes_and_review_mutation_rejected(self):
        self.data['parent']['input_sha256']='0'*64
        with self.assertRaisesRegex(SourceError,'parent'):self.replay()
        self.data['parent']['input_sha256']=self.parent.input_digest
        review=self.review();review.data['judgment']='valuation looks compelling'
        with self.assertRaisesRegex(SourceError,'mutated'):self.replay(review)

    def test_linked_context_need_not_nominate_a_deep_dive_candidate(self):
        us=next(r for r in self.fixture.review_data['rows'] if r['asset_id']=='US_EQUITY')
        us.update(priority='monitor',candidate=None)
        parent=self.fixture.replay()
        self.data['parent']=dict(id=parent.review.id,review_sha256=parent.review.input_digest,
                                 input_sha256=parent.input_digest)
        run=self.replay(parent=parent)
        self.assertEqual(run.effective_judgment,'mixed')
        self.assertIn('선택적 맥락',render_deep_dive_report(run))

    def test_standalone_run_uses_own_unknown_profile_and_no_prior_map(self):
        self.standalone()
        # Patching the parent entry point does not disable the internal shared
        # source/macro adapter, whose inputs contain no Scan candidates.
        with patch('investment_research.opportunity.replay_opportunity',side_effect=AssertionError('no parent Scan')):
            run=self.replay(parent=None)
        self.assertIsNone(run.parent)
        self.assertEqual(run.case.profile.fields['holdings'].status,'unknown')
        self.assertIsNone(run.case.profile.fields['holdings'].value)
        self.assertEqual(next(m.value for m in run.metrics if m.id=='CALC_GAP'),Decimal('2'))
        report=render_deep_dive_report(run)
        self.assertIn('직접 시작한 Deep Dive',report)
        self.assertNotIn('후속 조사 후보에서 출발',report)
        manifest=deep_dive_manifest(run,report)
        self.assertIsNone(manifest['parent'])
        self.assertEqual(manifest['profile'],self.data['profile'])
        self.assertEqual(self.fixture.requests,[])

    def test_standalone_context_missing_or_invalid_is_not_inferred(self):
        self.standalone();original=deepcopy(self.data)
        for change in ('profile','horizon'):
            self.data=deepcopy(original);del self.data[change]
            with self.assertRaisesRegex(SourceError,'profile and horizon'):self.review()
        self.data=deepcopy(original);self.data['profile']['debt']['value']=0
        with self.assertRaisesRegex(SourceError,'unknown'):self.review()

    def test_omitted_parent_field_is_valid_for_explicit_standalone_context(self):
        self.standalone();del self.data['parent']
        self.assertIsNone(self.replay(parent=None).parent)

    def test_optional_context_does_not_silently_attach_or_drop_provenance(self):
        with self.assertRaisesRegex(SourceError,'parent'):self.replay(parent=None)
        self.standalone()
        with self.assertRaisesRegex(SourceError,'unexpected parent'):self.replay()

    def test_mutated_linked_context_cannot_supply_a_different_user_profile(self):
        self.parent.review.data['profile']['debt']={'status':'known','value':0}
        with self.assertRaisesRegex(SourceError,'parent review mutated'):self.replay()

    def test_explicit_current_context_overrides_legacy_parent_profile(self):
        self.data['profile']={'base_currency':{'status':'known','value':'KRW'},
                              'income':{'status':'unknown','value':None}}
        self.data['horizon']='새 질문의 기간은 미확인이다.'
        run=self.replay()
        self.assertEqual(set(run.case.profile.fields),{'base_currency','income'})
        self.assertEqual(deep_dive_manifest(run,render_deep_dive_report(run))['profile'],self.data['profile'])

    def test_bounds_not_treated_as_exact_calculation_inputs(self):
        self.data['facts'][0]['qualifier']='above'
        with self.assertRaisesRegex(SourceError,'bounds'):self.replay()

    def test_judgment_requires_financial_valuation_and_treasury_context(self):
        self.data['sections']['current_judgment'][0]['evidence_ids']=['E_FIN']
        self.assertEqual(self.replay().effective_judgment,'insufficient evidence')
        self.data['sections']['current_judgment'][0]['evidence_ids']=['F_PE','CALC_GAP']
        self.data['sections']['current_judgment'][0]['role']='definition'
        self.assertEqual(self.replay().effective_judgment,'insufficient evidence')

    def test_invalid_nonfinite_values_and_nonstring_enums(self):
        original=deepcopy(self.data)
        for name,value in [('value','NaN'),('value',20.0),('unit',[]),('basis',{})]:
            with self.subTest(name=name,value=value):
                self.data=deepcopy(original);self.data['facts'][0][name]=value
                with self.assertRaises(SourceError):self.review()
        self.data=deepcopy(original);self.data['calculations'][0]['method']=[]
        with self.assertRaises(SourceError):self.review()
        self.data=deepcopy(original);self.data['sections']['easy'][0]['role']=[]
        with self.assertRaises(SourceError):self.review()

    def test_report_escape_references_determinism_and_tamper_detection(self):
        self.data['sections']['conclusions'][0]['text']='합성 <script>alert(위조)</script> [가짜](#조작) | 보고다.'
        run=self.replay();report=render_deep_dive_report(run)
        self.assertNotIn('<script>',report)
        refs=set(re.findall(r'\]\(#([^)]*)\)',report));anchors=re.findall(r'<a id="([^"]+)">',report)
        self.assertTrue(refs<=set(anchors));self.assertEqual(len(anchors),len(set(anchors)))
        again=self.replay();self.assertEqual(report,render_deep_dive_report(again))
        self.assertEqual(deep_dive_manifest(run,report),deep_dive_manifest(again,report))
        modified=tuple(replace(m,value=Decimal('999')) if m.id=='CALC_EY' else m for m in run.result.metrics)
        with self.assertRaisesRegex(SourceError,'mismatch'):
            render_deep_dive_report(replace(run,result=replace(run.result,metrics=modified)))

    def test_cli_replays_and_protects_both_studies_and_snapshots(self):
        from investment_research.__main__ import main
        argv=self.cli_args()
        f=self.fixture
        deep_pins=f.directory/'deep_pins.json';parent_pins=f.directory/'parent_pins.json'
        macro_pins=f.directory/'macro_pins.json'
        output=f.directory/'report.md';manifest=f.directory/'manifest.json'
        with redirect_stdout(StringIO()),redirect_stderr(StringIO()):
            self.assertEqual(main(argv+['--output',str(output),'--manifest',str(manifest)]),0)
            original=output.read_bytes()
            self.assertEqual(main(argv+['--output',str(output),'--manifest',str(manifest)]),0)
            for protected in (self.path,self.plan_path,deep_pins,f.review_path,f.source_path,parent_pins,
                              f.macro_path,macro_pins,self.store/'bad-output.md'):
                before=protected.read_bytes() if protected.is_file() else None
                self.assertEqual(main(argv+['--output',str(protected)]),2)
                self.assertEqual(protected.read_bytes() if protected.is_file() else None,before)
        self.assertEqual(output.read_bytes(),original)
        self.assertEqual(self.fixture.requests,[])

    def cli_args(self,*,standalone=False):
        f=self.fixture;self.review()
        deep_pins=f.directory/'deep_pins.json';deep_pins.write_text(json.dumps(self.pins))
        parent_pins=f.directory/'parent_pins.json'
        parent_plan=load_source_plan(f.source_path)
        parent_pins.write_text(json.dumps(dict(schema_version='1',plan_id=parent_plan.id,
            sources_digest=_digest([asdict(s) for s in parent_plan.sources]),
            snapshots={s.id:s.provenance.snapshot_id for s in self.parent.case.sources if s.id in {'S_PRIMARY','S_COMMUNITY'}})))
        macro_pins=f.directory/'macro_pins.json';macro_pins.write_text(json.dumps(f.macro_pins))
        argv=['deep-dive','replay',str(self.path)]
        flags=[('plan',self.plan_path),('store',self.store),('pins',deep_pins),
               ('macro-plan',f.macro_path),('macro-store',f.macro_store),('macro-pins',macro_pins)]
        if not standalone:
            flags.extend([('parent-review',f.review_path),('parent-plan',f.source_path),('parent-store',f.source_store),
                          ('parent-pins',parent_pins),('parent-macro-plan',f.macro_path),
                          ('parent-macro-store',f.macro_store),('parent-macro-pins',macro_pins)])
        for flag,path in flags:argv.extend(['--'+flag,str(path)])
        return argv

    def test_cli_standalone_does_not_require_or_load_parent_files(self):
        from investment_research.__main__ import main
        self.standalone();argv=self.cli_args(standalone=True)
        output=self.fixture.directory/'standalone.md'
        with redirect_stdout(StringIO()),redirect_stderr(StringIO()), \
             patch('investment_research.opportunity.load_opportunity_review',side_effect=AssertionError('no prior review')):
            self.assertEqual(main(argv+['--output',str(output)]),0)
            self.assertEqual(main(argv+['--output',str(self.path)]),2)
        self.assertIn('직접 시작한 Deep Dive',output.read_text())

    def test_cli_partial_parent_options_are_blocked_before_replay(self):
        from investment_research.__main__ import main
        self.standalone();argv=self.cli_args(standalone=True)
        with redirect_stdout(StringIO()),redirect_stderr(StringIO()):
            self.assertEqual(main(argv+['--parent-review',str(self.fixture.directory/'absent.json')]),2)
        self.assertEqual(self.fixture.requests,[])
