"""Authored fixtures: four minimum-coverage areas, no HTTP/DNS dependency."""
from copy import deepcopy
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal
import calendar
import json
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

from investment_research import scan, scan_coverage as coverage, scan_minimum as minimum
from investment_research.discovery import validate_policy
from investment_research.orchestrator import replay_ask
from investment_research.orchestrator_report import render_ask_report
from investment_research.sources import SourceError
from tests import test_scan_coverage as previous
from tests.test_scan_coverage import html
from tests.test_scan import QUESTION


class FourAssetTests(unittest.TestCase):
    def setUp(self):
        previous.MinimumScanTests.setUp(self)
        self.catalog.scan['method_version']='evidence_shortlist_v7'
        self.flow_cells=['100','200','-50','10','-20']
        self.gas_values=('31000','30000','31000')

    ask=previous.MinimumScanTests.ask
    row=previous.MinimumScanTests.row
    audit=previous.MinimumScanTests.audit
    reb_envelope=previous.MinimumScanTests.reb_envelope

    def flow_html(self):
        days=['03 Sep 2026','04 Sep 2026','07 Sep 2026','08 Sep 2026','09 Sep 2026']
        rows=[]
        for day,v in zip(days,self.flow_cells):
            value='('+v[1:]+')' if v.startswith('-') and v!='-' else v
            rows.append('<tr><td>'+day+'</td><td>'+value+'</td><td>0.0</td><td>'+value+'</td></tr>')
        return '<h1>Ethereum ETF Flow (US$m)</h1><table><tr><th>Date</th><th>ETHA</th><th>FETH</th><th>Total</th></tr>'+''.join(rows)+'</table>'

    def fetch(self,url,timeout,max_bytes):
        if url in self.missing or urlsplit(url).hostname in self.missing:raise SourceError('authored unavailable')
        if url.endswith('/hist/n9070us2m.htm') or url.endswith('/hist/n9133us2m.htm'):
            prod='n9070' in url;title='U.S. Dry Natural Gas Production' if prod else 'Liquefied U.S. Natural Gas Exports'
            header='<tr>'+''.join('<th>'+v+'</th>' for v in ['Year',*calendar.month_abbr[1:]])+'</tr>'
            old,prior,current=self.gas_values if prod else ('15500','15000','15500')
            def row(year,values):return '<tr>'+''.join('<td>'+v+'</td>' for v in [str(year),*values])+'</tr>'
            return html(title+' (Million Cubic Feet)<table>'+header+row(2025,['']*6+[old]+['']*5)+
                row(2026,['']*5+[prior,current]+['']*5)+'</table>Release Date: 9/9/2026')
        if url.endswith('/hist/nw2_epg0_swo_r48_bcfw.htm'):
            cells='<tr><th>Year-Month</th>'+''.join('<th>Week '+str(i)+'</th>' for i in range(1,6))+'</tr><tr>'+('<th>End Date</th><th>Value</th>'*5)+'</tr>'
            for i,year in enumerate(range(2021,2027)):
                day=date.fromisocalendar(year,36,5);v=900+i*100 if year<2026 else 1100
                cells+='<tr><td>'+day.strftime('%Y-%b')+'</td><td>'+day.strftime('%m/%d')+'</td><td>'+str(v)+'</td>'+('<td></td>'*8)+'</tr>'
            return html('Lower 48 States Natural Gas Working Underground Storage (Billion Cubic Feet)<table>'+cells+'</table>Release Date: 9/9/2026')
        if url.endswith('/610day/fxus06.html'):
            return html('Issued: Sep 09, 2026 6-10 DAY OUTLOOK TABLE Outlook for Sep 15 - 19 2026 STATE TEMP PCPN '+
                'NEW YORK B A OHIO B N N TEXAS A B 8-14 DAY OUTLOOK TABLE Outlook for Sep 17 - 23 2026 STATE TEMP PCPN '+
                'NEW YORK N A OHIO A N N TEXAS B A LEGEND TEMPS WITH RESPECT TO NORMAL A - ABOVE N - NEAR B - BELOW')
        if '/239561/' in url:
            return html('IAU iShares Gold Trust Tonnes in Trust 123.45 as of Sep 09, 2026 based on trade date activity Net Assets 9999999')
        if '/239757/' in url:
            return html('GSG Commodity iShares S&P GSCI Commodity-Indexed Trust NAV as of Sep 09, 2026 $ 29.00 '+
                'NAV Total Return as of Sep 09, 2026 YTD: Increase 10.00% S&P GSCI(R) Total Return Index '+
                'The fund offers a way to diversify portfolios and express views on energy, metals, agriculture, and livestock markets.')
        if url.endswith('/directory/FARSIDE_PUBLISHER'):
            r=previous.MinimumScanTests.fetch(self,url,timeout,max_bytes)
            return html(r.body.decode()+'<a href="https://discovery-fixture.example.org/new-eth-table/">Ethereum ETF Flow</a>')
        if url=='https://discovery-fixture.example.org/new-eth-table/':return html(self.flow_html())
        return previous.MinimumScanTests.fetch(self,url,timeout,max_bytes)

    def parser(self,contract,body,asset='NATGAS',block='gas_production',url='https://www.eia.gov/dnav/ng/hist/n9070us2m.htm'):
        return minimum.parse_candidate(contract,html(body),dict(url=url,asset_id=asset,index_identity_fields={'block':block}))

    def test_four_minimum_inputs_use_existing_pipeline(self):
        run=self.ask();rows={r['asset_id']:r for r in self.audit(run)['universe']}
        for asset in ('NATGAS','GOLD','ETH'):self.assertEqual(rows[asset]['coverage_status'],'sufficient_for_scan',asset)
        self.assertEqual(rows['BROAD_COMMODITIES']['coverage_status'],'partial_but_usable')
        self.assertIn('composition',rows['BROAD_COMMODITIES']['coverage']['missing_categories'])
        self.assertTrue(any(i['function']=='scan_coverage' for i in run.invocations))
        self.assertEqual(run.input['method_versions']['scan_four_assets'],coverage.FOUR_ASSET_VERSION)
        self.assertLessEqual(len(run.discovery['requests']),48)

    def test_added_coverage_does_not_force_candidates(self):
        run=self.ask();a=self.audit(run)
        self.assertFalse(set(a['candidates'])&{'NATGAS','GOLD','ETH','BROAD_COMMODITIES'})
        self.assertFalse(any('score' in r for r in a['universe']))
        self.assertEqual(self.row(run,'GOLD')['investment_assessment'],'mixed_signals')

    def test_daily_rate_corrects_different_month_lengths(self):
        ms={m.id:m for m in self.ask().result.metrics}
        self.assertEqual(ms['SCAN_GAS_PRODUCTION_DAILY_202607'].value,Decimal(1))
        self.assertEqual(ms['SCAN_GAS_PRODUCTION_DAILY_MOM'].value,Decimal(0))
        self.assertEqual(ms['SCAN_GAS_PRODUCTION_DAILY_YOY'].value,Decimal(0))
        self.assertEqual(ms['SCAN_GAS_LNG_EXPORTS_DAILY_MOM'].value,Decimal(0))

    def test_gas_production_scope_not_lower48_or_forecast(self):
        run=self.ask();es=[e for e in run.case.evidence if e.provenance and e.provenance.definition['measure']=='EIA_US_DRY_GAS_PRODUCTION']
        self.assertEqual({e.unit for e in es},{'MMcf'})
        self.assertTrue(all(e.provenance.definition['scope']=='US nationwide dry gas production' for e in es))
        self.assertTrue(all('not_forecast' in e.provenance.definition['adjustment'] for e in es))

    def test_monthly_missing_adjacent_month_not_replaced_by_forecast(self):
        raw=self.fetch('https://www.eia.gov/dnav/ng/hist/n9070us2m.htm',10,100000).body.decode().replace('<td>30000</td>','<td></td>')
        with self.assertRaises(SourceError):self.parser('minimum_monthly_gas_v2',raw)

    def test_monthly_unit_or_country_change_is_rejected(self):
        raw=self.fetch('https://www.eia.gov/dnav/ng/hist/n9070us2m.htm',10,100000).body.decode()
        for wrong in (raw.replace('Million Cubic Feet','Billion Cubic Feet'),raw.replace('U.S. Dry','Canada Dry')):
            with self.assertRaises(SourceError):self.parser('minimum_monthly_gas_v2',wrong)

    def test_leap_month_matches_prior_nonleap_month_end(self):
        header='<tr>'+''.join('<th>'+v+'</th>' for v in ['Year',*calendar.month_abbr[1:]])+'</tr>'
        def row(year,jan,feb):return '<tr>'+''.join('<td>'+v+'</td>' for v in [str(year),jan,feb]+['']*10)+'</tr>'
        raw='U.S. Dry Natural Gas Production (Million Cubic Feet)<table>'+header+row(2023,'31000','28000')+row(2024,'31000','29000')+'</table>Release Date: 3/1/2024'
        p=self.parser('minimum_monthly_gas_v2',raw)
        self.assertEqual(p['observed_at'],'2024-02-29')
        self.assertEqual([r['definition']['period'] for r in p['records']],['2023-02','2024-01','2024-02'])

    def test_empty_official_table_is_unavailable_not_crash(self):
        raw='U.S. Dry Natural Gas Production (Million Cubic Feet)<table><tr>'+''.join('<th>'+v+'</th>' for v in ['Year',*calendar.month_abbr[1:]])+'</tr></table>Release Date: 9/9/2026'
        with self.assertRaisesRegex(SourceError,'unavailable'):self.parser('minimum_monthly_gas_v2',raw)

    def test_five_year_reference_has_known_manual_mean(self):
        ms={m.id:m for m in self.ask().result.metrics}
        m=ms['SCAN_GAS_SEASONAL_5Y_REFERENCE'];self.assertEqual(m.value,Decimal(1100));self.assertEqual(len(m.input_ids),5)
        self.assertEqual(ms['SCAN_GAS_STOCK_VS_SEASONAL_REFERENCE'].value,Decimal(0))
        self.assertIn('EIA 공식 보간 평균',m.limitations[0])

    def test_missing_reference_year_blocks_seasonal_mean(self):
        self.missing.add('https://www.eia.gov/dnav/ng/hist/nw2_epg0_swo_r48_bcfw.htm')
        run=self.ask();self.assertNotIn('SCAN_GAS_SEASONAL_5Y_REFERENCE',{m.id for m in run.result.metrics})
        self.assertIn('seasonal',self.row(run,'NATGAS')['coverage']['missing_categories'])

    def test_weather_forecast_is_not_numeric_observation_or_hdd(self):
        run=self.ask();es=[e for e in run.case.evidence if e.provenance and e.provenance.definition['measure'].startswith('NOAA_CPC_')]
        self.assertEqual(len(es),6);self.assertTrue(all(e.value is None for e in es))
        self.assertTrue(all(e.provenance.definition['period'].startswith('forecast_valid_') for e in es))
        self.assertFalse(any(p['definition']['measure'].startswith('NOAA_CPC') for p in self.audit(run)['observations']))
        report=render_ask_report(run);self.assertIn('뉴욕 평년보다 낮음',report);self.assertIn('HDD/CDD',report)

    def test_stale_weather_does_not_fill_demand(self):
        old=self.fetch
        def fetch(url,t,b):
            r=old(url,t,b)
            return html(r.body.decode().replace('Issued: Sep 09, 2026','Issued: Aug 09, 2026')) if '/610day/' in url else r
        with patch.object(self,'fetch',side_effect=fetch):run=self.ask()
        self.assertIn('demand',self.row(run,'NATGAS')['coverage']['missing_categories'])

    def test_gold_physical_tonnes_is_not_aum_or_flow(self):
        run=self.ask();ps=[p for p in self.audit(run)['observations'] if p['definition']['measure']=='IAU_GOLD_PHYSICAL_HELD']
        self.assertEqual(ps[0]['value'],'123.45');self.assertEqual(ps[0]['definition']['unit'],'tonnes')
        self.assertIn('not_AUM_not_net_flow',ps[0]['definition']['adjustment'])
        self.assertNotIn('GOLD',self.audit(run)['candidates'])

    def test_gold_aum_alone_does_not_supply_demand(self):
        old=self.fetch
        def fetch(url,t,b):return html('IAU iShares Gold Trust Net Assets 9999999 as of Sep 09, 2026') if '/239561/' in url else old(url,t,b)
        with patch.object(self,'fetch',side_effect=fetch):run=self.ask()
        self.assertIn('demand',self.row(run,'GOLD')['coverage']['missing_categories'])

    def test_eth_flow_has_separate_identity_and_five_reported_days(self):
        run=self.ask();ms={m.id:m for m in run.result.metrics};m=ms['SCAN_ETH_FIVE_REPORTED_DAYS_NET_FLOW']
        self.assertEqual(m.value,Decimal(240));self.assertEqual(len(m.input_ids),5)
        ps=[p for p in self.audit(run)['observations'] if p['definition']['measure']=='US_SPOT_ETH_ETF_DAILY_NET_FLOW']
        self.assertEqual(len(ps),5);self.assertTrue(all(p['asset_id']=='ETH' for p in ps))
        self.assertTrue(any(c['index_locator'].startswith('anchor') for c in run.discovery['candidates'] if c.get('asset_id')=='ETH' and c['category']=='scan_eth_flow'))

    def test_missing_latest_eth_row_never_falls_back_to_older_complete_flow(self):
        self.flow_cells[-1]='-';run=self.ask()
        self.assertIn('flow',self.row(run,'ETH')['coverage']['missing_categories'])
        self.assertNotIn('SCAN_ETH_FIVE_REPORTED_DAYS_NET_FLOW',{m.id for m in run.result.metrics})
        self.assertFalse(self.row(run,'ETH')['candidate_eligible'])

    def test_btc_table_cannot_be_used_for_eth(self):
        with self.assertRaises(SourceError):self.parser('minimum_eth_flow_v2',self.flow_html().replace('Ethereum','Bitcoin'),'ETH','eth_flow_recent','https://discovery-fixture.example.org/new-eth-table/')

    def test_unbalanced_flow_total_is_not_promoted(self):
        old=self.flow_html
        with patch.object(self,'flow_html',side_effect=lambda:old().replace('<td>(20)</td></tr>','<td>999</td></tr>')):
            run=self.ask()
        self.assertIn('flow',self.row(run,'ETH')['coverage']['missing_categories'])

    def test_broad_price_is_nav_not_crude_or_index_level(self):
        run=self.ask();p=next(p for p in self.audit(run)['observations'] if p['definition']['measure']=='ISHARES_GSG_NAV')
        self.assertEqual(p['value'],'29.00');self.assertIn('not_spot_index_not_market_price',p['definition']['adjustment'])
        self.assertIn('calendar_year_2026',next(p for p in self.audit(run)['observations'] if p['definition']['measure']=='ISHARES_GSG_YTD_NAV_TOTAL_RETURN')['definition']['adjustment'])

    def test_broad_supply_requires_distinct_subgroups_not_oil_alone(self):
        self.missing.add('https://www.ishares.com/us/products/239561/ishares-gold-trust-fund');run=self.ask()
        self.assertIn('physical',self.row(run,'BROAD_COMMODITIES')['coverage']['missing_categories'])
        self.assertFalse(self.row(run,'BROAD_COMMODITIES')['candidate_eligible'])

    def test_new_connections_are_not_market_change_against_v6(self):
        self.catalog.scan['method_version']='evidence_shortlist_v6';old=self.ask();self.now+=timedelta(seconds=1)
        self.catalog.scan['method_version']='evidence_shortlist_v7';new=self.ask(previous_scan=old.directory)
        h=self.audit(new)['since_previous_scan']
        self.assertTrue(h['newly_observable']);self.assertFalse(any(c['status']=='new_observation' for c in h['observations']))
        self.assertEqual(self.audit(old)['candidates'],self.audit(new)['candidates'])

    def test_narrow_modes_do_not_add_scan_extension(self):
        run=self.ask('BTC 지금 어때?')
        self.assertNotIn('scan',run.input)
        self.assertFalse(any(n['category'] in ('scan_gas_context','scan_weather','scan_gold_demand','scan_eth_flow','scan_broad') for n in run.input['evidence_needs']))

    def test_other_asset_coverage_is_preserved(self):
        self.catalog.scan['method_version']='evidence_shortlist_v6';old=self.ask()
        self.catalog.scan['method_version']='evidence_shortlist_v7';new=self.ask()
        for r in self.audit(old)['universe']:
            if r['asset_id'] not in ('NATGAS','GOLD','ETH','BROAD_COMMODITIES'):
                self.assertEqual(r['coverage_status'],self.row(new,r['asset_id'])['coverage_status'],r['asset_id'])

    def test_explicit_scan_and_btc_dive_fit_existing_provider_bound(self):
        run=self.ask('전체 시장 보고 BTC도 깊게 봐줘')
        self.assertEqual([t['mode'] for t in run.input['tasks']],['opportunity_scan','asset_deep_dive'])
        self.assertLessEqual(len({i['provider_id'] for i in run.discovery['indexes']}),12)
        self.assertNotIn('GOLD',{m for t in run.input['tasks'] if t['mode']=='asset_deep_dive' for m in t['method_ids']})

    def test_bounded_budget_does_not_expand_generic_discovery(self):
        po=deepcopy(self.catalog.discovery);po['max_requests']=33
        with self.assertRaises(SourceError):validate_policy(po)
        po.update(scan_extension='four_asset_minimum_v2',max_requests=48);validate_policy(po)
        po['max_requests']=49
        with self.assertRaises(SourceError):validate_policy(po)

    def test_replay_traceability_and_source_dependency(self):
        run=self.ask();before=render_ask_report(run)
        with patch('socket.getaddrinfo',side_effect=AssertionError('offline replay')),patch('investment_research.orchestrator.discover_sources',side_effect=AssertionError('no rediscovery')):
            replay=replay_ask(run.directory)
        self.assertEqual(before,render_ask_report(replay))
        self.assertIn('네 영역의 실제 근거와 판단 제한',before)
        by_id={e.id:e for e in run.case.evidence}
        for m in run.result.metrics:
            if m.id.startswith('SCAN_GAS_') or m.id.startswith('SCAN_ETH_FIVE'):
                self.assertTrue(set(m.input_ids)<=set(by_id))
        eth_sources=[s for s in run.discovery['sources'] if s['url']=='https://discovery-fixture.example.org/new-eth-table/']
        self.assertEqual(len(eth_sources),2);self.assertEqual(eth_sources[1]['origin_source_id'],eth_sources[0]['id'])
        self.assertNotIn('score',self.audit(run))

    def test_missing_core_data_is_explicit_not_fake_support(self):
        self.missing.update({'www.eia.gov','www.cpc.ncep.noaa.gov','www.ishares.com','farside.co.uk','https://discovery-fixture.example.org/new-eth-table/'})
        run=self.ask();self.assertEqual(self.row(run,'NATGAS')['coverage_status'],'insufficient')
        self.assertEqual(self.row(run,'BROAD_COMMODITIES')['coverage_status'],'insufficient')
        self.assertIn('flow',self.row(run,'ETH')['coverage']['missing_categories'])
        self.assertNotIn('ETH',self.audit(run)['candidates'])
