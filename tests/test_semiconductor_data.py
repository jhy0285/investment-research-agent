"""Authored synthetic company data, never real prices/filings or live HTTP.

Arithmetic expectations below are manually checkable. The PDF layout fixtures
exercise accounting column selection independently of the optional decoder.
"""
from copy import deepcopy
from dataclasses import replace
from datetime import timedelta
from decimal import Decimal
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from investment_research import semiconductor_data as semi
from investment_research.discovery import candidate_freshness
from investment_research.models import SourceType
from investment_research.orchestrator import execute_ask, replay_ask
from investment_research.orchestrator_report import render_ask_report
from investment_research.research_catalog import load_catalog
from investment_research.sources import FetchResponse, SourceError, SourceSpec, _validate
from tests.test_korean_data import samsung_html
from tests.test_orchestrator import NOW, synthetic_catalog

QUESTION='삼성전자랑 SK하이닉스 지금 둘 중 뭐가 더 나아?'
PDF_BASE='https://images.samsung.com/is/content/samsung/assets/global/ir/docs/'


def income_text(annual=False):
    if annual:
        header=('For the years ended December 31 2025 2024\nKRW KRW USD USD\n')
        rows=[('Revenue',[2500000,2000000,900,800]),('Operating profit',[200000,150000,90,80]),
              ('Profit for the year',[160000,120000,70,60]),('Owners of the parent company',[150000,110000,60,50]),
              ('- Basic',[200,160,1,1])]
    else:
        header=('For the three-month periods ended June 30 2026 2025\n'
                'For the six-month periods ended June 30 2026 2025\nKRW KRW USD USD KRW KRW USD USD\n')
        rows=[('Revenue',[1000000,600000,900,800,1800000,1100000,700,600]),
              ('Operating profit',[200000,60000,90,80,340000,100000,70,60]),
              ('Profit for the period',[150000,45000,70,60,250000,80000,50,40]),
              ('Owners of the parent company',[140000,40000,60,50,240000,70000,40,30]),
              ('- Basic',[100,20,1,1,180,60,1,1])]
    return ('Authored synthetic fixture only\nSamsung Electronics Co., Ltd. and its subsidiaries\n'
        'CONSOLIDATED STATEMENTS OF INCOME\nIn millions of Korean won\n'+header+
        '\n'.join(name+'    99    '+'    '.join(f'{v:,}' for v in values) for name,values in rows))


def statement_text(kind,annual=False):
    if kind=='soi':return income_text(annual)
    header=('Authored synthetic fixture only\nSamsung Electronics Co., Ltd. and its subsidiaries\n'
            'INTERIM CONSOLIDATED STATEMENTS\nIn millions of Korean won\nJune 30 2026\nKRW KRW USD USD\n')
    if kind=='bs':return header+('Total equity    5,000,000    4,000,000    500    400\n'
        'Non-controlling interests    100,000    90,000    10    9\nIntangible assets    200,000    180,000    20    18\n')
    if kind=='cf':return header+('For the six-month periods ended June 30 2026 2025\n'
        'Net cash from operating activities    300,000    90,000    300    90\n'
        'Acquisition of property, plant and equipment    (100,000)    (80,000)    (100)    (80)\n')
    return header+('(A) Ordinary shares\nBasic earnings per share are calculated on weighted average ordinary shares.\n'
        '(B) Preference shares\n\nThe Group has contractual commitments for the acquisition of equipment.\n\n'
        'The investment portfolio consists of listed equity instruments subject to fair-value risk.\n')


def provider_html():
    columns=['2025 2Q','2025 3Q','2025 4Q','2026 1Q','2026 2Q']
    def table(name,items,notes=()):
        return dict(name=name,Columns=columns,Notes=list(notes),Series=[dict(name=n,unit=u,
            Data=[dict(nr=float(v),str=str(v)) for v in values]) for n,u,values in items])
    groups=[dict(name='Quarterly',Data=[
        table('Income Statement',[
            ('Revenue','KRW million',[800,900,1000,1100,1200]),
            ('Operating Profit','KRW million',[80,90,100,110,120]),
            ('Net Profit','KRW million',[50,60,70,80,200]),
            ('Profit before Income Tax','KRW million',[70,80,90,100,300])]),
        table('Data Per Share',[
            ('Earnings Per Share (EPS)','KRW',[10,15,20,25,40]),
            ('Book-value Per Share (BVPS) ','KRW',[100,110,120,130,140])],[semi.EPS_NOTE,semi.BVPS_NOTE]),
        table('Financial Position',[("Total Shareholders' Equity",'KRW million',[800,900,1000,1100,1200])]),
        table('Cash Flows',[
            ('Cash Flow from Operating Activities','KRW million',[80,90,100,110,120]),
            ('Cash Flow from Investing Activities','KRW million',[-20,-25,-30,-35,-40])])])]
    return '<script>var data={companycode: "kr-000660", LevelZeroItems : '+json.dumps(groups)+'};</script>'


def dart_row(asset):
    name,code,corp=semi.COMPANIES[asset]
    receipt='20260814000001' if asset=='SAMSUNG' else '20260814000002'
    return ('<table><tr><td><a onclick="openCorpInfoNew(\''+corp+'\', \'win\')">'+name+'</a></td>'
        '<td><a href="/dsaf001/main.do?rcpNo='+receipt+'">반기보고서 (2026.06)</a></td></tr></table>')


class SemiconductorTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        catalog,self.documents=synthetic_catalog();live=load_catalog()
        self.catalog=replace(catalog,korean=deepcopy(live.korean),semiconductor=deepcopy(live.semiconductor))
        self.requests=[];self.sequence=0;self.price_date='2026.09.09';self.prices={'SAMSUNG':'6,400','SK_HYNIX':'1,000'}
        self.financial=provider_html();self.samsung=samsung_html()+(
            '<p>The Memory Business achieved another record-breaking quarter by focusing on server products. '
            'The continued industry-wide upward trend of prices also contributed to the record earnings.</p>'
            '<p>Additionally, the Business solidified market competitiveness via HBM. The Business scaled up HBM4 '
            'sales and shipped HBM4E samples to major customers.</p>'
            '<p>Earnings for the Foundry Business improved significantly prior to incentive-related provisions, '
            'driven by HBM base-die demand. 2nm HPC engagements were a notable example.</p>')
        self.pdfs={}
        for filename,kind,annual in [('2026_con_quarter02_soi.pdf','soi',False),('2025_con_quarter04_soi.pdf','soi',True),
            ('2026_con_quarter02_bs.pdf','bs',False),('2026_con_quarter02_cf.pdf','cf',False),('2026_con_quarter02_note.pdf','note',False)]:
            body=b'%PDF-1.4 AUTHORED SYNTHETIC '+filename.encode()
            self.documents[PDF_BASE+filename]=FetchResponse(body,'application/pdf');self.pdfs[body]=statement_text(kind,annual)
        decoder=patch('investment_research.semiconductor_data.pdf_text',side_effect=lambda b:self.pdfs[b]);decoder.start();self.addCleanup(decoder.stop)
        for name in ('socket.socket.connect','socket.getaddrinfo','investment_research.sources._fetch_http','investment_research.discovery._fetch_http'):
            guard=patch(name,side_effect=AssertionError('live HTTP/DNS forbidden in authored fixtures'));guard.start();self.addCleanup(guard.stop)

    def fetch(self,url,timeout,max_bytes):
        self.requests.append(url);parts=urlsplit(url)
        if parts.path=='/robots.txt':
            rule=b'User-agent: *\nDisallow: /dsaf001/\n' if parts.hostname=='dart.fss.or.kr' else b'User-agent: *\nAllow: /\n'
            if parts.hostname=='www.reddit.com':rule=b'User-agent: *\nDisallow: /\n'
            return FetchResponse(rule,'text/plain')
        if url in self.documents:return self.documents[url]
        if parts.hostname=='dart.fss.or.kr':
            asset='SAMSUNG' if parse_qs(parts.query).get('currentPage')==['5'] else 'SK_HYNIX'
            return FetchResponse(dart_row(asset).encode(),'text/html')
        if parts.hostname=='markets.hankyung.com':
            asset='SAMSUNG' if parts.path.endswith('005930') else 'SK_HYNIX';name,code,_=semi.COMPANIES[asset]
            return FetchResponse(('<p>'+name+' '+code+' '+self.prices[asset]+' KRW My Stock '+self.price_date+' 장마감</p>').encode(),'text/html')
        if parts.hostname=='news.samsung.com':return FetchResponse(self.samsung.encode(),'text/html')
        if parts.hostname=='www.samsung.com':
            return FetchResponse(''.join('<a href="'+url+'">Authored synthetic statement</a>' for url in self.documents if url.startswith(PDF_BASE)).encode(),'text/html')
        if parts.hostname=='www.skhynix.com':
            text='<script src="/_nuxt/123abcd.js"></script>' if parts.path=='/ir/UI-FR-IR07/' else (
                'UI-FR-IR07; titleEnglish:"SK hynix IAT";urlBase:"//asia.tools.euroland.com/tools/ia/?companycode=kr-000660&v=redesign"')
            return FetchResponse(text.encode(),'text/html' if parts.path.startswith('/ir/') else 'application/javascript')
        if parts.hostname=='asia.tools.euroland.com':return FetchResponse(self.financial.encode(),'text/html')
        if parts.hostname=='hn.algolia.com':
            samsung='Samsung' in parse_qs(parts.query)['query'][0];identity='101' if samsung else '102'
            text='Samsung HBM: Samsung 2026Q2 revenue was KRW 1000000 million.' if samsung else 'SK hynix memory earnings may not persist. Authored synthetic comment.'
            return FetchResponse(json.dumps(dict(hits=[dict(objectID=identity,comment_text=text,created_at=NOW.isoformat())])).encode(),'application/json')
        if parts.hostname=='hacker-news.firebaseio.com':
            sam=parts.path.endswith('/101.json');text='Samsung HBM: Samsung 2026Q2 revenue was KRW 1000000 million.' if sam else 'SK hynix memory earnings may not persist. Authored synthetic comment.'
            return FetchResponse(json.dumps(dict(id=101 if sam else 102,type='comment',text=text,time=int((NOW-timedelta(hours=1)).timestamp()))).encode(),'application/json')
        raise AssertionError('unplanned authored fixture request '+url)

    def ask(self,question=QUESTION):
        self.sequence+=1
        return execute_ask(question,self.root/str(self.sequence),catalog=self.catalog,now=NOW,fetcher=self.fetch)

    def metrics(self,run,case=None):return {m.id:m for m in semi.calculate(case or run.case,run.cutoff)}

    def altered(self,run,measure,period=None,**changes):
        rows=[]
        for e in run.case.evidence:
            if e.provenance and e.provenance.definition['measure']==measure and (period is None or e.period==period):
                definition=deepcopy(e.provenance.definition);definition.update(changes.pop('definition',{}))
                e=replace(e,provenance=replace(e.provenance,definition=definition),**changes)
            rows.append(e)
        return replace(run.case,evidence=tuple(rows))

    def test_exact_question_same_manual_ttm_formula_and_traceable_inputs(self):
        run=self.ask();m=self.metrics(run)
        self.assertEqual(tuple(run.input['plan']['modes']),('compare',))
        self.assertEqual([x['id'] for x in run.input['methods']],['SAMSUNG','SK_HYNIX'])
        self.assertEqual(m['CALC_SEMI_SAMSUNG_TTM_EPS'].value,Decimal('320')) # 200+180-60
        self.assertEqual(m['CALC_SEMI_SK_HYNIX_TTM_EPS'].value,Decimal('100')) # 15+20+25+40
        self.assertEqual(m['CALC_SEMI_SAMSUNG_PE'].value,Decimal('20'))
        self.assertEqual(m['CALC_SEMI_SK_HYNIX_PE'].value,Decimal('10'))
        self.assertEqual(m['CALC_SEMI_SAMSUNG_EY'].value,Decimal('5'))
        self.assertEqual(m['CALC_SEMI_SK_HYNIX_EY'].value,Decimal('10'))
        self.assertEqual(m['CALC_SEMI_SAMSUNG_TTM_REVENUE'].value,Decimal('3200000'))
        self.assertEqual(m['CALC_SEMI_SAMSUNG_TTM_OPERATING'].value,Decimal('440000'))
        self.assertEqual(m['CALC_SEMI_SK_HYNIX_TTM_REVENUE'].value,Decimal('4200'))
        self.assertEqual(m['CALC_SEMI_SK_HYNIX_TTM_NET'].value,Decimal('410'))
        self.assertEqual(m['CALC_SEMI_SK_HYNIX_REVENUE_YOY'].value,Decimal('50'))
        self.assertEqual(m['CALC_SEMI_SK_HYNIX_MARGIN_2026Q2'].value,Decimal('10'))
        self.assertEqual(len(m['CALC_SEMI_SK_HYNIX_PE'].input_ids),5)
        facts={e.id:e for e in run.case.evidence}
        for result in m.values():
            self.assertTrue(set(result.input_ids)<=set(facts))
            self.assertTrue(all(facts[i].provenance.match_status=='matched' for i in result.input_ids))
        self.assertFalse(semi.audit(run)['comparison_eligible'])
        self.assertTrue(any('잠정' in x.label for x in m.values()))

    def test_cash_quality_is_independent_of_quote_and_not_full_fcf(self):
        run=self.ask();case=replace(run.case,evidence=tuple(e for e in run.case.evidence if not e.provenance.definition['measure'].endswith('_CLOSE')))
        m=self.metrics(run,case)
        self.assertEqual(m['CALC_SEMI_SAMSUNG_CFO_AFTER_PPE'].value,Decimal('200000'))
        self.assertEqual(m['CALC_SEMI_SK_HYNIX_NONOPERATING_RESIDUAL'].value,Decimal('180'))
        self.assertEqual(m['CALC_SEMI_SK_HYNIX_NONOPERATING_SHARE'].value,Decimal('60'))
        self.assertNotIn('CALC_SEMI_SAMSUNG_PE',m)
        self.assertFalse(any(key.endswith(('_FCF','_PB','_MARKET_CAP','_FORWARD_PE')) for key in m))

    def test_missing_ttm_quarter_does_not_annualize_or_fill(self):
        run=self.ask();case=replace(run.case,evidence=tuple(e for e in run.case.evidence if not
            (e.provenance.definition['measure']=='SEMI_SK_HYNIX_EPS' and e.period=='2025Q4')))
        self.assertNotIn('CALC_SEMI_SK_HYNIX_PE',self.metrics(run,case))
        self.assertNotIn('CALC_SEMI_SK_HYNIX_TTM_EPS',self.metrics(run,case))

    def test_mixed_eps_definitions_and_negative_earnings_withhold_multiple(self):
        run=self.ask()
        for case in (self.altered(run,'SEMI_SK_HYNIX_EPS','2025Q4',definition={'scope':'separate accounts'}),
                     self.altered(run,'SEMI_SK_HYNIX_EPS',value=Decimal('-50'))):
            self.assertNotIn('CALC_SEMI_SK_HYNIX_PE',self.metrics(run,case))

    def test_ordinary_basis_note_required_not_preferred_eps(self):
        run=self.ask();case=replace(run.case,evidence=tuple(e for e in run.case.evidence if e.provenance.definition['measure']!='SEMI_SAMSUNG_ORDINARY_EPS'))
        self.assertNotIn('CALC_SEMI_SAMSUNG_PE',self.metrics(run,case))

    def test_conflicting_input_is_not_silently_overwritten(self):
        run=self.ask();old=next(e for e in run.case.evidence if e.provenance.definition['measure']=='SEMI_SAMSUNG_EPS')
        case=replace(run.case,evidence=(*run.case.evidence,replace(old,id='SYNTHETIC_CONFLICT',value=old.value+1)))
        self.assertNotIn('CALC_SEMI_SAMSUNG_PE',self.metrics(run,case))

    def test_scope_and_currency_mismatch_blocks_financial_ratio(self):
        run=self.ask()
        for case in (self.altered(run,'SEMI_SAMSUNG_OPERATING','2026Q2',definition={'scope':'separate'}),
                     self.altered(run,'SEMI_SAMSUNG_OPERATING','2026Q2',currency='USD')):
            self.assertNotIn('CALC_SEMI_SAMSUNG_MARGIN_2026Q2',self.metrics(run,case))

    def test_stale_and_future_close_never_promoted_to_current_price(self):
        for date_text in ('2026.08.01','2026.09.11'):
            self.price_date=date_text;run=self.ask()
            self.assertNotIn('CALC_SEMI_SAMSUNG_PE',self.metrics(run))
            statuses=[c['freshness']['status'] for c in run.discovery['candidates'] if c.get('category')=='semiconductor_price']
            self.assertTrue(all(s in ('stale','future') for s in statuses))

    def test_source_retrieval_after_cutoff_blocks_arithmetic(self):
        run=self.ask();close=next(e for e in run.case.evidence if e.provenance.definition['measure']=='SEMI_SAMSUNG_CLOSE')
        case=replace(run.case,sources=tuple(replace(s,provenance=replace(s.provenance,retrieved_at=(NOW+timedelta(days=1)).isoformat())) if s.id==close.source_id else s for s in run.case.sources))
        self.assertNotIn('CALC_SEMI_SAMSUNG_PE',self.metrics(run,case))

    def test_dart_registration_is_not_original_financial_validation(self):
        run=self.ask();audit=semi.audit(run)
        for company in audit['companies'].values():self.assertTrue(company['filing_registration_ids'])
        blocked=[c for c in run.discovery['candidates'] if c.get('category')=='semiconductor_filing']
        self.assertEqual(len(blocked),2);self.assertTrue(all(c['status']=='rejected' for c in blocked))
        self.assertFalse(any('/dsaf001/' in u for u in self.requests))
        self.assertIn('original_filing_unavailable',{x['status'] for x in audit['cross_checks']})

    def test_company_and_correction_identity_fail_closed(self):
        provider=next(p for p in self.catalog.semiconductor['providers'] if p['id']=='SEMI_DART_SAMSUNG')
        need={'asset_id':'SAMSUNG','category':'semiconductor_registration'}
        for body in (dart_row('SK_HYNIX'),dart_row('SAMSUNG').replace('반기보고서','[기재정정] 반기보고서')):
            with self.assertRaises(SourceError):semi.directory_items(provider,need,FetchResponse(body.encode(),'text/html'))

    def test_latest_issuer_edition_is_not_silently_replaced_with_old_format(self):
        provider=next(p for p in self.catalog.semiconductor['providers'] if p['contract']=='semiconductor_samsung_statement_v1')
        old=PDF_BASE+'2025_con_quarter02_soi.pdf';new=PDF_BASE+'2026_con_quarter03_soi.pdf'
        result=semi.directory_items(provider,{'asset_id':'SAMSUNG','block':'quarter'},FetchResponse(
            ('<a href="'+old+'">old</a><a href="'+new+'">new</a>').encode(),'text/html'))
        self.assertEqual(result[0][0],new)
        self.assertEqual(result[0][1]['quarter'],3) # Later unsupported format is a gap, not a stale fallback.

    def test_release_rounding_crosscheck_and_material_mismatch_are_distinct(self):
        run=self.ask();checks=[x for x in semi.audit(run)['cross_checks'] if x['company']=='SAMSUNG']
        self.assertEqual(len(checks),2);self.assertTrue(all(x['status']=='consistent_with_release_rounding' for x in checks))
        bad=self.altered(run,'SEMI_SAMSUNG_REVENUE','2026Q2',value=Decimal('2000000'))
        checks=semi.audit(replace(run,case=bad))['cross_checks']
        self.assertIn('mismatch',{x['status'] for x in checks})

    def test_provider_tangible_bvps_and_ambiguous_cashflow_do_not_make_pb_or_capex(self):
        run=self.ask();rows=semi.observations(run.case,run.cutoff)
        book=rows['SK_HYNIX']['tangible_bvps','2026Q2'][0]
        self.assertEqual(book.provenance.definition['adjustment'],'provider_tangible_equity_per_share_not_standard_PB')
        cf=rows['SK_HYNIX']['investing_cf','2026Q2'][0]
        self.assertIn('quarter_vs_YTD_unverified',cf.provenance.definition['adjustment'])
        self.assertFalse(any('PB' in m.id or 'SK_HYNIX_CFO_AFTER_PPE' in m.id for m in run.result.metrics))

    def test_community_narrative_actual_source_and_narrow_primary_fact_check(self):
        run=self.ask();report=render_ask_report(run)
        self.assertIn('실제 발견한 공개 발언',report)
        checks=run.discovery['community_verification'];check=next(c for c in checks if c.get('asset_ids')==['SAMSUNG'])
        self.assertEqual(check['rule'],'numeric_equality_v1');self.assertEqual(check['verification'],'supported_within_scope')
        other=next(c for c in checks if c.get('asset_ids')==['SK_HYNIX'])
        self.assertEqual(other['verification'],'unverified')
        claims=[c for c in run.case.claims if c.narrative_evidence_id]
        self.assertTrue(all('BTC' not in c.asset_ids for c in claims))
        self.assertTrue(all('hacker-news.firebaseio.com' in c['url'] for c in run.discovery['candidates'] if c.get('category')=='semiconductor_community'))

    def test_technical_narrative_not_verified_by_company_promotion(self):
        r=dict(quote='Samsung HBM is superior to all peers.',evidence_id='N')
        candidate=dict(asset_id='SAMSUNG',source_id='S',verified=dict(records=[r]))
        primary=dict(evidence_id='P',definition=dict(measure='SEMI_SAMSUNG_HBM_STATEMENT'))
        check=semi.community_check(candidate,[(dict(source_type='primary'),primary)])
        self.assertEqual(check['verification'],'unverified');self.assertNotIn('rule',check)
        self.assertEqual(check['evidence_ids'],['P'])

    def test_snapshot_selection_and_report_replay_are_offline_byte_identical(self):
        run=self.ask();before=(run.directory/'report.md').read_bytes()
        with (patch('investment_research.orchestrator.plan_research',side_effect=AssertionError('no re-routing')),
             patch('investment_research.orchestrator.discover_sources',side_effect=AssertionError('no new discovery')),
             patch('investment_research.semiconductor_data.pdf_text',side_effect=AssertionError('replay consumes pinned excerpts'))):
            again=replay_ask(run.directory)
        self.assertEqual(render_ask_report(again).encode(),before)
        self.assertEqual(again.digest,run.digest)
        self.assertEqual(json.loads((run.directory/'company_comparison.json').read_text()),semi.audit(again))
        self.assertEqual(len(run.discovery['requests']),len(set(run.discovery['requests'])))
        self.assertLessEqual(len(run.discovery['requests']),32)

    def test_report_sections_and_explanation_show_input_limits(self):
        from investment_research.orchestrator import acquire_plan
        with patch('investment_research.orchestrator.acquire_plan',wraps=acquire_plan) as acquisition:
            run=self.ask()
        self.assertEqual(acquisition.call_count,1)
        report=render_ask_report(run)
        for heading in ('한눈에 보기','현재 가격과 valuation','최근 실적','이익의 질','삼성전자 Bull / Bear',
            'SK하이닉스 Bull / Bear','시장이 기대하고 있는 것','Community narrative와 실제 자료',
            '현재 가격에서 더 매력적인 쪽','무엇이 바뀌면 판단이 달라지는가','한국 투자자에게 의미하는 것','초간단 설명'):
            self.assertIn('## '+heading,report)
        self.assertIn('무형자산을 뺀',report);self.assertIn('인센티브 관련 충당금',report)
        self.assertIn('수정주가 여부도 명시되지',report)
        easy=report.split('## 초간단 설명\n\n')[1].split('<details>')[0].strip()
        self.assertLessEqual(len([x for x in easy.split('.') if x.strip()]),7)
        functions={x['function'] for x in run.invocations}
        self.assertTrue({'replay_plan','replay_discovery','calculate_semiconductor'}<=functions)

    def test_single_company_does_not_acquire_other_company_or_scan(self):
        run=self.ask('삼성전자 지금 어때?')
        self.assertEqual([m['id'] for m in run.input['methods']],['SAMSUNG'])
        self.assertFalse(any('000660' in u or 'hynix' in u.lower() for u in self.requests))
        self.assertNotIn('opportunity_scan',run.input['plan']['modes'])

    def test_historical_question_does_not_use_current_financial_editions(self):
        run=self.ask('2024-10-01 기준 삼성전자랑 SK하이닉스 비교해줘')
        self.assertNotIn('semiconductor_coverage',run.input)
        self.assertFalse(any('markets.hankyung' in u or 'dart.fss' in u for u in self.requests))

    def test_pdf_columns_distinguish_krw_usd_quarter_ytd_and_parent_total(self):
        doc=semi.statement_document(next(b for b in self.pdfs if b.endswith(b'2026_con_quarter02_soi.pdf')),PDF_BASE+'2026_con_quarter02_soi.pdf')
        self.assertEqual(doc['cells']['revenue']['2026Q2'],'1000000')
        self.assertEqual(doc['cells']['revenue']['2026H1'],'1800000')
        self.assertEqual(doc['cells']['owners']['2026Q2'],'140000')
        self.assertEqual(doc['cells']['net']['2026Q2'],'150000')
        self.assertEqual(doc['cells']['eps']['2025H1'],'60')

    def test_pdf_wrong_units_columns_dates_and_missing_cells_fail_closed(self):
        url=PDF_BASE+'2026_con_quarter02_soi.pdf';body=self.documents[url].body;original=self.pdfs[body]
        variants=[original.replace('KRW KRW USD USD','USD USD KRW KRW'),original.replace('In millions of Korean won','In millions of dollars'),
            original.replace('2026','2027'),original.replace('CONSOLIDATED','SEPARATE'),original.replace('1,000,000','-')]
        for text in variants:
            self.pdfs[body]=text
            with self.assertRaises(SourceError):semi.statement_document(body,url)
        self.pdfs[body]=original

    def test_comprehensive_income_duplicate_rows_not_mistaken_for_profit(self):
        url=PDF_BASE+'2026_con_quarter02_soi.pdf';body=self.documents[url].body
        self.pdfs[body]+='\nINTERIM CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME\nProfit for the period 999 999 999 999 999 999 999 999\n'
        doc=semi.statement_document(body,url);self.assertEqual(doc['cells']['net']['2026Q2'],'150000')

    def test_provider_missing_eps_definition_and_null_do_not_create_multiple(self):
        original=self.financial
        for text in (original.replace(semi.EPS_NOTE,'Undefined EPS'),original.replace('"str": "40"','"str": null')):
            self.financial=text;run=self.ask();self.assertNotIn('CALC_SEMI_SK_HYNIX_PE',self.metrics(run))

    def test_ordinary_code_date_and_closed_quote_required(self):
        for url,body in [('https://markets.hankyung.com/stock/005935','삼성전자 005935 6400 KRW My Stock 2026.09.09 장마감'),
            ('https://markets.hankyung.com/stock/005930','SK하이닉스 000660 1000 KRW My Stock 2026.09.09 장마감'),
            ('https://markets.hankyung.com/stock/005930','삼성전자 005930 6,400 KRW My Stock 실시간')]:
            with self.assertRaises(SourceError):semi.market_document(body,url)


    def test_financial_history_and_current_price_keep_separate_dates(self):
        from datetime import date
        run=self.ask()
        rows={(e.provenance.definition['measure'],e.period):e for e in run.case.evidence}
        self.assertEqual(rows[('SEMI_SAMSUNG_REVENUE','2025Q2')].observed_at,date(2025,6,30))
        self.assertEqual(rows[('SEMI_SAMSUNG_REVENUE','2026Q2')].observed_at,date(2026,6,30))
        self.assertEqual(rows[('SEMI_SAMSUNG_REVENUE','2025')].observed_at,date(2025,12,31))
        self.assertEqual(rows[('SEMI_SAMSUNG_REVENUE','2026H1')].observed_at,date(2026,6,30))
        self.assertEqual(rows[('SEMI_SAMSUNG_CLOSE','2026-09-09')].observed_at,date(2026,9,9))

    def test_undated_earnings_history_cannot_support_growth_or_TTM_valuation(self):
        run=self.ask()
        case=self.altered(run,'SEMI_SAMSUNG_REVENUE','2025Q2',observed_at=None)
        ms={m.id:m for m in semi.calculate(case,run.cutoff,require_dates=True)}
        self.assertNotIn('CALC_SEMI_SAMSUNG_REVENUE_YOY',ms)
        case=self.altered(run,'SEMI_SAMSUNG_EPS','2025',observed_at=None)
        ms={m.id:m for m in semi.calculate(case,run.cutoff,require_dates=True)}
        self.assertNotIn('CALC_SEMI_SAMSUNG_TTM_EPS',ms)
        self.assertNotIn('CALC_SEMI_SAMSUNG_PE',ms)


class DecoderBoundaryTests(unittest.TestCase):
    def test_decoder_is_optional_and_invalid_or_oversized_bytes_are_rejected(self):
        semi.pdf_text.cache_clear()
        with patch('investment_research.semiconductor_data.shutil.which',return_value=None):
            with self.assertRaisesRegex(SourceError,'unavailable'):semi.pdf_text(b'%PDF-1.4 authored optional-boundary test')
        for body in (b'not a PDF',b'%PDF-'+b'x'*(2*1024*1024)):
            with self.assertRaises(SourceError):semi.pdf_text(body)

    def test_pdf_allowlist_does_not_expand_generic_retention_or_downloads(self):
        data=dict(id='PDF_TEST',url=PDF_BASE+'2026_con_quarter02_soi.pdf',canonical_url=PDF_BASE+'2026_con_quarter02_soi.pdf',
            type='primary',publisher='Authored fixture',title='Authored fixture',content_type='application/pdf',
            policy_url=PDF_BASE,policy_note='Authored fixture excerpt policy',
            excerpts=({'id':'Q','quote':'Authored synthetic financial text','locator':'body', 'definition':'Authored synthetic note'},))
        _validate(SourceSpec(**data))
        for changed in (dict(type='community'),dict(url='https://unreviewed.example.org/report.pdf'),dict(retention='full')):
            with self.assertRaises(SourceError):_validate(SourceSpec(**{**data,**changed}))
