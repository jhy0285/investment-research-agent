"""Authored, offline fixtures for minimum Scan coverage and repeated observations."""
from copy import deepcopy
from dataclasses import replace
from datetime import timedelta
from decimal import Decimal
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

from investment_research import scan,scan_coverage as coverage,scan_minimum as minimum
from investment_research.orchestrator import execute_ask,replay_ask
from investment_research.orchestrator_report import render_ask_report
from investment_research.research_catalog import load_catalog
from investment_research.source_pipeline import _digest,_extract
from investment_research.sources import FetchResponse,SourceError
from tests import test_scan as original
from tests.test_discovery import response,flow_html
from tests.test_orchestrator import NOW


def html(text):return FetchResponse(text.encode(),'text/html')


class MinimumScanTests(unittest.TestCase):
    def setUp(self):
        original.ScanTests.setUp(self)
        self.catalog=replace(self.catalog,scan=deepcopy(load_catalog().scan))
        self.catalog.scan['method_version']='evidence_shortlist_v6'
        self.now=NOW;self.crypto_last={'BTC':110,'ETH':220};self.stock_pair=(1000,1100);self.gold_price='2,100.00'

    reb_envelope=original.ScanTests.reb_envelope

    def fetch(self,url,timeout,max_bytes):
        if url in self.missing or urlsplit(url).hostname in self.missing:raise SourceError('authored unavailable')
        if '/candles?' in url:
            product=url.split('/products/')[1].split('/')[0];asset=product.split('-')[0]
            end=self.now.replace(hour=0,minute=0,second=0,microsecond=0)
            first=100 if asset=='BTC' else 200
            return response([[int((end-timedelta(days=8-i)).timestamp()),50,300,100,
                first if i==0 else self.crypto_last[asset] if i==7 else first+i,100+i] for i in range(8)])
        if url.endswith('spdr-gold-shares-gld'):
            return html('<h1>Authored GLD Gold Shares</h1>Fund Net Asset Value as of Sep 09 2026 LBMA Gold Price PM $'+self.gold_price+
                ' Fund Performance Month End as of Aug 31 2026 As Of 1 Month Benchmark LBMA Gold Price PM Aug 31 2026 -2.00%')
        if url=='https://www.federalreserve.gov/releases/h15/':
            return html('Release date: September 10, 2026 Yields in percent per annum <table><tr><th>Instruments</th><th>2026Sep8</th><th>2026Sep9</th></tr>'
                '<tr><td>Inflation indexed 10</td><td></td><td></td></tr><tr><td>10-year</td><td>2.0</td><td>2.1</td></tr></table>')
        if '/hist/rwtcd.htm' in url or '/hist/rngwhhdD.htm' in url:
            oil='/pet/' in url;title='Cushing, OK WTI Spot Price FOB (Dollars per Barrel)' if oil else 'Henry Hub Natural Gas Spot Price (Dollars per Million Btu)'
            return html(title+' <table><tr><th>Week Of</th><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th></tr>'
                '<tr><td>2026 Aug-31 to Sep- 4</td><td>90</td><td>91</td><td>92</td><td>93</td><td>94</td></tr>'
                '<tr><td>2026 Sep- 7 to Sep-11</td><td>95</td><td>96</td><td>97</td><td></td><td></td></tr></table>Release Date: 9/10/2026')
        if url.endswith('/pet_stoc_wstk_dcu_nus_w.htm') or url.endswith('/ng_stor_wkly_s1_w.htm'):
            oil='/pet/' in url;title='Commercial Crude Oil (Excl. Lease Stock)' if oil else 'Total Lower 48 States'
            return html(('Thousand Barrels Product ' if oil else 'Billion Cubic Feet Region ')+
                '07/31/26 08/07/26 08/14/26 08/21/26 08/28/26 09/04/26 View History '+title+
                ' 1,000 1,010 1,020 1,030 '+f'{self.stock_pair[0]:,} {self.stock_pair[1]:,}'+' 1982-2026 Release Date: 9/10/2026')
        if '/StatisticSearch/' in url:
            parts=urlsplit(url).path.split('/');table=parts[9] if len(parts)>9 else ''
            # Schema path positions are read from the reviewed macro registry.
            table=next((t for t in ('817Y002','121Y006') if '/'+t+'/' in url),None)
            item=parts[-1]
            for identifier,fields in minimum.ECOS_CONTEXT.items():
                stat,name,code,label,freq,unit,frequency,age=fields
                if table==stat and item==code:
                    times=['20260908','20260909'] if freq=='D' else ['202607','202608']
                    return response(dict(StatisticSearch=dict(list_total_count=2,row=[dict(STAT_CODE=stat,STAT_NAME=name,ITEM_CODE1=code,
                        ITEM_NAME1=label,ITEM_CODE2=None,ITEM_CODE3=None,ITEM_CODE4=None,UNIT_NAME=unit,TIME=t,DATA_VALUE=str(v))
                        for t,v in zip(times,('3.0','3.1') if freq=='D' else ('4.0','4.1'))])))
        return original.ScanTests.fetch(self,url,timeout,max_bytes)

    def ask(self,question=original.QUESTION,**kw):
        self.count+=1
        return execute_ask(question,self.root/str(self.count),catalog=self.catalog,fetcher=self.fetch,now=self.now,**kw)

    def audit(self,run):return scan.assess(run)
    def row(self,run,asset):return next(r for r in self.audit(run)['universe'] if r['asset_id']==asset)

    def test_minimum_profiles_have_asset_specific_criteria(self):
        run=self.ask();a=self.audit(run)
        self.assertEqual(len(a['universe']),15);self.assertEqual(set(a['coverage_standards']),set(coverage.STANDARDS))
        self.assertNotIn('earnings',dict((s[0],s) for s in coverage.STANDARDS['gas']))
        self.assertEqual(self.row(run,'CASH')['coverage_status'],'sufficient_for_scan')

    def test_coverage_not_attractiveness_or_document_count(self):
        run=self.ask();a=self.audit(run);cash=self.row(run,'CASH');gold=self.row(run,'GOLD')
        self.assertNotIn('CASH',a['candidates']);self.assertNotIn('GOLD',a['candidates'])
        self.assertEqual(gold['coverage_status'],'partial_but_usable')
        self.assertNotEqual(gold['investment_assessment'],'not_assessed_due_to_gap')
        self.assertFalse(any('score' in r for r in a['universe']))

    def test_partial_business_evidence_can_be_conditional_candidate(self):
        r=self.row(self.ask(),'KR_EQUITY')
        self.assertTrue(r['selected']);self.assertEqual(r['coverage_status'],'partial_but_usable')
        self.assertIn('market',r['coverage']['critical_gaps']);self.assertIn('핵심 자료 확인',r['confidence'])

    def test_missing_broad_commodity_data_is_unassessed_not_unattractive(self):
        r=self.row(self.ask(),'BROAD_COMMODITIES')
        self.assertEqual(r['coverage_status'],'insufficient');self.assertEqual(r['investment_assessment'],'not_assessed_due_to_gap')
        self.assertFalse(r['candidate_eligible']);self.assertNotEqual(r['status'],'weak_case')

    def test_crypto_weekly_price_liquidity_without_fabricated_flows(self):
        run=self.ask();a=self.audit(run)
        for asset in ('BTC','ETH'):
            r=self.row(run,asset);self.assertIn(r['coverage_status'],('sufficient_for_scan','partial_but_usable'))
            self.assertEqual(next(m.value for m in run.result.metrics if m.id=='SCAN_'+asset+'_WEEK_PRICE_CHANGE'),Decimal(10))
        self.assertIn('flow',self.row(run,'ETH')['coverage']['missing_categories'])
        self.assertEqual(self.row(run,'ETH')['coverage_status'],'partial_but_usable')
        self.assertNotIn('ETH',a['candidates'])

    def test_incomplete_BTC_flows_are_excluded_from_minimum_slots(self):
        self.documents[self.flow_url]=flow_html(total='10',fbtc='-')
        run=self.ask();r=self.row(run,'BTC')
        self.assertIn('flow',r['coverage']['missing_categories']);self.assertFalse(r['candidate_eligible'])
        self.assertFalse(any(p['definition']['adjustment']=='partial_row_not_final_total' for p in self.audit(run)['observations']))

    def test_positive_complete_flow_can_select_falling_BTC(self):
        self.crypto_last['BTC']=90;self.documents[self.flow_url]=flow_html(total='10')
        r=self.row(self.ask(),'BTC');self.assertTrue(r['candidate_eligible'])
        self.assertEqual(r['decision_rule'],'complete_asset_flow_and_price_not_price_direction')

    def test_GLD_price_is_not_NAV_or_demand(self):
        run=self.ask();r=self.row(run,'GOLD');a=self.audit(run)
        p=next(p for p in a['observations'] if p['definition']['measure']=='LBMA_GOLD_PM_ISSUER_REPORTED')
        self.assertEqual(Decimal(p['value']),Decimal(2100));self.assertEqual(p['definition']['unit'],'USD_per_troy_ounce')
        self.assertIn('demand',r['coverage']['missing_categories']);self.assertNotIn('GOLD',a['candidates'])

    def test_actual_energy_stocks_separate_from_forecasts(self):
        run=self.ask();gas=self.row(run,'NATGAS');oil=self.row(run,'ENERGY')
        self.assertNotIn('physical',gas['coverage']['missing_categories']);self.assertIn('production',gas['coverage']['missing_categories'])
        self.assertEqual(oil['coverage_status'],'sufficient_for_scan');self.assertFalse(oil['selected'])
        self.assertEqual(gas['investment_assessment'],'mixed_signals')

    def test_falling_actual_oil_inventory_can_make_conditional_candidate(self):
        self.stock_pair=(1100,1000);run=self.ask();r=self.row(run,'ENERGY')
        self.assertTrue(r['candidate_eligible']);self.assertIn('실제 원유 재고',r['why_now'])

    def test_regional_rent_and_financing_use_correct_regions_and_definition(self):
        run=self.ask();r=self.row(run,coverage.REGIONAL)
        self.assertEqual(set(r['coverage']['regions']),{'서울','경기','인천'})
        for region,slots in r['coverage']['regions'].items():self.assertTrue(slots['rent'])
        self.assertEqual(r['coverage_status'],'sufficient_for_scan')
        finance=next(s for s in r['coverage']['slots'] if s['category']=='financing')
        self.assertIn('주담대',finance['note']);self.assertIn('아님',finance['note'])

    def test_missing_Seoul_rent_is_not_filled_from_Gyeonggi(self):
        run=self.ask();evidence=tuple(e for e in run.case.evidence if not (e.provenance and e.provenance.definition['measure']=='KR_APARTMENT_SURVEY_JEONSE_INDEX'
            and e.provenance.definition['scope'].startswith('서울 ')))
        altered=replace(run,case=replace(run.case,evidence=evidence));r=self.row(altered,coverage.REGIONAL)
        self.assertIn('rent',r['coverage']['missing_categories']);self.assertFalse(r['coverage']['regions']['서울']['rent'])

    def test_baseline_does_not_claim_increased_community_attention(self):
        a=self.audit(self.ask());h=a['since_previous_scan']
        self.assertEqual(h['status'],'baseline');self.assertEqual(h['community']['status'],'not_comparable')
        self.assertIn('Baseline',(self.root/'1'/'report.md').read_text())

    def test_same_observation_retrieved_later_is_not_market_change(self):
        first=self.ask();self.now=NOW+timedelta(seconds=1);second=self.ask(previous_scan=first.directory)
        h=self.audit(second)['since_previous_scan']
        self.assertEqual(h['status'],'compared');self.assertTrue(h['observations'])
        self.assertTrue(all(c['status']=='same_observation' for c in h['observations']))
        self.assertFalse(h['hypotheses'])

    def test_new_source_coverage_is_not_a_new_market_signal(self):
        first=self.ask();anchor=coverage.capture(first)
        anchor['observations']=[p for p in anchor['observations'] if p['asset_id']!='GOLD']
        anchor['anchor_sha256']=_digest({k:v for k,v in anchor.items() if k!='anchor_sha256'})
        h=coverage.compare(self.audit(first)['observations'],anchor,NOW+timedelta(seconds=1),True)
        self.assertTrue(any(p['asset_id']=='GOLD' for p in h['newly_observable']))
        self.assertFalse(any(p['asset_id']=='GOLD' for p in h['observations']))

    def test_same_date_revised_vintage_is_not_price_momentum(self):
        first=self.ask();anchor=coverage.capture(first);points=deepcopy(self.audit(first)['observations'])
        for p in points:
            if p['definition']['measure']=='LBMA_GOLD_PM_ISSUER_REPORTED':p['value']='2101'
        h=coverage.compare(points,anchor,NOW+timedelta(seconds=1),True)
        item=next(c for c in h['observations'] if c['measure']=='LBMA_GOLD_PM_ISSUER_REPORTED')
        self.assertEqual(item['status'],'revised_vintage');self.assertEqual(Decimal(item['delta']),Decimal(1))
        self.assertFalse(coverage.combinations(h['observations']))

    def test_new_observation_price_change_has_real_trace_and_definition(self):
        first=self.ask();self.now=NOW+timedelta(days=1);self.crypto_last['BTC']=121
        second=self.ask(previous_scan=first.directory);h=self.audit(second)['since_previous_scan']
        item=next(c for c in h['observations'] if c['measure']=='COINBASE_BTC_USD_DAILY_CLOSE' and c['asset_id']=='BTC')
        self.assertEqual(item['status'],'new_observation');self.assertEqual(item['percent_change'],'10.0')
        self.assertTrue(item['previous_ref'].startswith(first.result.run_id+'/'))
        self.assertIn(item['current_evidence_id'],{e.id for e in second.case.evidence})

    def test_different_source_currency_unit_or_basis_cannot_form_series(self):
        first=self.ask();anchor=coverage.capture(first)
        for field,value in [('unit','KRW_per_BTC'),('currency','KRW'),('adjustment','adjusted_close'),('scope','Other venue BTC-USD')]:
            points=deepcopy(self.audit(first)['observations'])
            for p in points:
                if p['definition']['measure']=='COINBASE_BTC_USD_DAILY_CLOSE':
                    p['definition'][field]=value;p['comparison_definition'][field]=value
                    p['series_key']=_digest([p['asset_id'],p['source_identity'],p['comparison_definition']])
            h=coverage.compare(points,anchor,NOW+timedelta(seconds=1),True)
            self.assertFalse(any(c['measure']=='COINBASE_BTC_USD_DAILY_CLOSE' for c in h['observations']))

    def test_FY1_and_rolling_forward_PE_remain_independent(self):
        a=self.audit(self.ask());ps=[p for p in a['observations'] if 'PE' in p['definition']['measure']]
        self.assertTrue(any(p['comparison_definition']['adjustment']=='forward_12m_pe' for p in ps))
        self.assertTrue(any(p['comparison_definition']['adjustment']=='weighted_harmonic_FY1_estimate_not_rolling_12m' for p in ps))
        self.assertEqual(len({p['series_key'] for p in ps}),len({(p['asset_id'],json.dumps(p['comparison_definition'],sort_keys=True),json.dumps(p['source_identity'],sort_keys=True)) for p in ps}))

    def test_snapshot_replay_does_not_need_previous_directory_or_network(self):
        first=self.ask();self.now=NOW+timedelta(seconds=1);second=self.ask(previous_scan=first.directory)
        first.directory.rename(self.root/'archived_prior')
        with patch('investment_research.orchestrator.plan_research',side_effect=AssertionError('no reroute')),patch('investment_research.orchestrator.discover_sources',side_effect=AssertionError('no discovery')):
            replay=replay_ask(second.directory)
        self.assertEqual(render_ask_report(second),render_ask_report(replay));self.assertEqual(self.audit(second),self.audit(replay))

    def test_comparison_artifacts_and_manifest_pin_everything(self):
        run=self.ask();manifest=json.loads((run.directory/'run_manifest.json').read_text())
        for name in ('shortlist.json','scan_observations.json','scan_changes.json'):self.assertIn(name,manifest['artifact_sha256'])
        self.assertEqual(manifest['method_versions']['scan_comparison'],coverage.HISTORY_VERSION)
        self.assertIn('coverage_status',manifest['opportunity_shortlist']['universe'][0])

    def test_invalid_prior_future_or_synthetic_mode_fails_before_acquisition(self):
        first=self.ask()
        with self.assertRaises(SourceError):self.ask(previous_scan=first.directory)
        self.now=NOW+timedelta(seconds=1)
        with self.assertRaises(SourceError):self.ask('BTC 지금 어때?',previous_scan=first.directory)

    def test_conditional_oil_entry_and_exit_explain_actual_new_evidence(self):
        self.stock_pair=(1100,1000);first=self.ask();self.now=NOW+timedelta(seconds=1)
        self.stock_pair=(1000,1100);second=self.ask(previous_scan=first.directory)
        events=self.audit(second)['since_previous_scan']['candidate_changes']
        event=next(e for e in events if e['asset_id']=='ENERGY')
        # Same-date changed official stock is a revision, not market movement.
        self.assertIn(event['change'],('removed','priority_lowered'));self.assertIn('자료',event['reason'])

    def test_original_independent_modes_are_not_forced_through_Scan(self):
        for question in ('BTC 지금 어때?','천연가스 지금 들어갈 만해?','삼성전자랑 SK하이닉스 비교해줘.','내 포트폴리오 괜찮아?'):
            run=self.ask(question);self.assertNotIn('scan',run.input);self.assertFalse((run.directory/'scan_changes.json').exists())

    def test_grouped_decimal_uses_exact_numeric_token_only(self):
        d=dict(measure='X',unit='USD_per_troy_ounce',period='2026-09-09',currency='USD',scope='GLD',adjustment='benchmark')
        self.assertEqual(_extract('2,100.25','grouped_decimal_scalar_v1',d),Decimal('2100.25'))
        self.assertIsNone(_extract('21,00.25','grouped_decimal_scalar_v1',d));self.assertIsNone(_extract('price 2,100.25','grouped_decimal_scalar_v1',d))

    def test_missing_duplicate_gap_or_live_crypto_bars_do_not_pass_contract(self):
        at=NOW.replace(hour=0,minute=0,second=0,microsecond=0)
        rows=[[int((at-timedelta(days=8-i)).timestamp()),50,300,100,100+i,100] for i in range(8)]
        candidate=dict(asset_id='ETH',index_identity_fields={'product':'ETH-USD'},url='https://api.exchange.coinbase.com/products/ETH-USD/candles?granularity=86400',document={'retrieved_at':NOW.isoformat()})
        for bad in (rows[:-1],rows[:-1]+[rows[0]],rows[:-1]+[[int(at.timestamp()),50,300,100,109,100]],rows[:3]+rows[4:]):
            with self.assertRaises(SourceError):minimum.parse_candidate('minimum_crypto_v1',response(bad),candidate)

    def test_inflation_benchmark_and_KRW_cash_are_not_US_yields(self):
        run=self.ask();a=self.audit(run);cash=self.row(run,'CASH');kr=self.row(run,'KR_GOVERNMENT_3Y')
        self.assertTrue(cash['evidence_ids']);self.assertIn('policy',kr['coverage']['missing_categories'])
        for ref in cash['evidence_ids']:
            e=next(e for e in run.case.evidence if e.id==ref);self.assertEqual(e.currency,'KRW');self.assertEqual(e.provenance.definition['measure'],'KR_CD_91D')

    def test_no_rich_data_guaranteed_four_candidate_fill(self):
        self.documents[self.flow_url]=flow_html(total='10',fbtc='-')
        a=self.audit(self.ask());self.assertLess(len(a['candidates']),4)
        self.assertNotIn('KR_GOVERNMENT_3Y',a['candidates']);self.assertIn('KR_GOVERNMENT_3Y',a['comparison_anchors'])

    def test_community_remains_unverified_and_attention_not_inferred(self):
        first=self.ask();self.now=NOW+timedelta(seconds=1);second=self.ask(previous_scan=first.directory)
        h=self.audit(second)['since_previous_scan'];self.assertEqual(h['community']['status'],'not_comparable')
        self.assertNotIn('percent_change',h['community'])

    def test_qualitative_combinations_require_same_windows_and_real_fundamental_input(self):
        base=dict(asset_id='BTC',current_evidence_id='P2',previous_evidence_id='P1',previous_observed_at='2026-09-01',current_observed_at='2026-09-08',
            status='new_observation',series_key='p',measure='COINBASE_BTC_USD_DAILY_CLOSE',direction='down')
        flow={**base,'measure':'US_SPOT_BTC_ETF_DAILY_NET_FLOW','series_key':'f','direction':'up','current_evidence_id':'F2','previous_evidence_id':'F1'}
        hs=coverage.combinations([base,flow]);self.assertEqual(len(hs),1);self.assertFalse(hs[0]['return_guarantee'])
        self.assertIn('반대 의견',hs[0]['text']);self.assertFalse(coverage.combinations([base,{**flow,'current_observed_at':'2026-09-09'}]))

    def test_unavailable_previous_definition_is_not_decline_in_attractiveness(self):
        first=self.ask();anchor=coverage.capture(first);points=[p for p in self.audit(first)['observations'] if p['asset_id']!='GOLD']
        h=coverage.compare(points,anchor,NOW+timedelta(seconds=1),True)
        gaps=[g for g in h['unavailable'] if g['asset_id']=='GOLD'];self.assertTrue(gaps);self.assertIn('아니다',gaps[0]['reason'])

    def test_mismatched_source_is_not_same_price_series(self):
        first=self.ask();anchor=coverage.capture(first);points=deepcopy(self.audit(first)['observations'])
        for p in points:
            if p['definition']['measure']=='COINBASE_BTC_USD_DAILY_CLOSE':
                p['source_identity']['url']='https://different-exchange.example.org/BTC-USD';p['series_key']=_digest([p['asset_id'],p['source_identity'],p['comparison_definition']])
        h=coverage.compare(points,anchor,NOW+timedelta(seconds=1),True)
        self.assertTrue(any(m['measure']=='COINBASE_BTC_USD_DAILY_CLOSE' for m in h['mismatches']))
        self.assertFalse(any(c['measure']=='COINBASE_BTC_USD_DAILY_CLOSE' for c in h['observations']))

    def test_previous_anchor_tampering_rejected(self):
        run=self.ask();anchor=coverage.capture(run);anchor['observations'][0]['value']='999999'
        with self.assertRaises(SourceError):coverage.validate_anchor(anchor,NOW+timedelta(seconds=1),True)

    def test_legitimate_negative_historical_oil_price_does_not_block_current_price(self):
        r=self.fetch('https://www.eia.gov/dnav/pet/hist/rwtcd.htm',15,500000)
        text=r.body.decode().replace('<tr><td>2026 Aug-31', '<tr><td>2020 Apr-20 to Apr-24</td><td>-36.98</td><td>0</td><td>13</td><td>14</td><td>15</td></tr><tr><td>2026 Aug-31')
        c=dict(asset_id='ENERGY',index_identity_fields={'block':'oil_price'},url='https://www.eia.gov/dnav/pet/hist/rwtcd.htm',document={'retrieved_at':NOW.isoformat()})
        parsed=minimum.parse_candidate('minimum_spot_v1',html(text),c)
        self.assertEqual([p['quote'] for p in parsed['records']],['92','97'])

    def test_another_country_company_is_not_the_growth_portfolio_change(self):
        r=self.row(self.ask(),'GROWTH_THEME')
        self.assertIn('change',r['coverage']['missing_categories']);self.assertEqual(r['coverage_status'],'partial_but_usable')

    def test_one_regional_index_point_cannot_supply_price_change(self):
        run=self.ask();seen=set();out=[]
        for e in run.case.evidence:
            if e.provenance and e.provenance.definition['measure']=='KR_APARTMENT_SURVEY_SALE_INDEX':
                if e.provenance.definition['scope'] in seen:continue
                seen.add(e.provenance.definition['scope'])
            out.append(e)
        changed=replace(run,case=replace(run.case,evidence=tuple(out)))
        self.assertIn('market',self.row(changed,coverage.REGIONAL)['coverage']['missing_categories'])

    def test_gold_can_have_conditional_macro_price_hypothesis_without_demand_data(self):
        p=dict(asset_id='GOLD',measure='LBMA_GOLD_PM_ISSUER_REPORTED',direction='flat',status='new_observation',
            current_evidence_id='P2',previous_evidence_id='P1',previous_observed_at='2026-09-01',current_observed_at='2026-09-08',series_key='p')
        rate={**p,'measure':'US_TIPS_10Y_CURRENT','direction':'down','current_evidence_id':'R2','previous_evidence_id':'R1','series_key':'r'}
        h=coverage.combinations([p,rate],enhanced=True);self.assertEqual(len(h),1)
        self.assertIn('직접 수요',h[0]['text']);self.assertFalse(h[0]['return_guarantee'])
        self.assertFalse(coverage.combinations([p,{**rate,'current_observed_at':'2026-09-09'}],enhanced=True))

    def test_flat_fundamentals_not_independent_duplicate_fact_votes(self):
        run=self.ask();a=self.audit(run)
        fact_ids={f['id'] for f in run.deep.facts}
        # Typed facts point back to source evidence; derived fact evidence is
        # not another observation of the same economic input.
        self.assertFalse(any(p['evidence_id'] in fact_ids for p in a['observations']))
        p=dict(asset_id='BTC',measure='COINBASE_BTC_USD_DAILY_CLOSE',direction='up',status='new_observation',
            current_evidence_id='P2',previous_evidence_id='P1',previous_observed_at='2026-09-01',current_observed_at='2026-09-08',series_key='p')
        f={**p,'measure':'US_SPOT_BTC_ETF_DAILY_NET_FLOW','direction':'flat','current_evidence_id':'F2','previous_evidence_id':'F1','series_key':'f'}
        self.assertIn('기대가 먼저',coverage.combinations([p,f],enhanced=True)[0]['text'])

    def test_explicit_combined_scan_and_gas_uses_existing_flows(self):
        run=self.ask('전체 시장 보고 천연가스는 깊게 봐줘.')
        self.assertEqual(set(run.input['plan']['modes']),{'opportunity_scan','asset_deep_dive'})
        self.assertIn('NATGAS',[m['id'] for m in run.input['methods']]);self.assertTrue(run.opportunity)
        self.assertEqual(render_ask_report(run),render_ask_report(replay_ask(run.directory)))

    def test_partial_flow_finalization_is_not_inferred_institutional_growth(self):
        self.documents[self.flow_url]=flow_html(total='10',fbtc='-');first=self.ask()
        self.now=NOW+timedelta(seconds=1);self.documents[self.flow_url]=flow_html(total='(10)',ibit='(12.5)')
        second=self.ask(previous_scan=first.directory);a=self.audit(second);h=a['since_previous_scan']
        n=next(n for n in h['newly_observable'] if n['measure']=='US_SPOT_BTC_ETF_DAILY_NET_FLOW')
        self.assertIn('완료 판본',n['reason']);self.assertFalse(any(c['measure']=='US_SPOT_BTC_ETF_DAILY_NET_FLOW' for c in h['observations']))
        self.assertEqual(self.row(second,'BTC')['investment_assessment'],'mixed_signals')
        self.assertIn('순유출',(second.directory/'report.md').read_text())

    def test_issuer_document_canonical_reason_does_not_claim_source_absent(self):
        run=self.ask();needs=run.discovery['needs']
        for n in needs:
            if n['category'] in ('scan_gold','scan_valuation') and n['status']=='available':
                self.assertIn('발행사 원문',n['canonical_preference']['reason']);self.assertFalse(n['canonical_preference']['primary_available'])

    def test_financial_definition_change_prevents_earnings_series_join(self):
        first=self.ask();anchor=coverage.capture(first);points=deepcopy(self.audit(first)['observations'])
        for p in points:
            if p['definition']['measure']=='F_SP_FORWARD_12M_PE':
                p['comparison_definition']['source_definition']='new basis';p['series_key']=_digest([p['asset_id'],p['source_identity'],p['comparison_definition']])
        h=coverage.compare(points,anchor,NOW+timedelta(seconds=1),True)
        self.assertFalse(any(c['measure']=='F_SP_FORWARD_12M_PE' for c in h['observations']))
        self.assertTrue(any(c['measure']=='F_SP_FORWARD_12M_PE' for c in h['mismatches']))


if __name__=='__main__':unittest.main()
