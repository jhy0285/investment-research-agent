"""Authored commodity fixtures, including PDFs: no live HTTP, DNS or decoder."""

from copy import deepcopy
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal
import csv
from io import StringIO
import json
import re
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

from investment_research import commodity_data as data, scan, scan_coverage
from investment_research.commodity_report import assessment, broad_sections, View
from investment_research.discovery import validate_policy
from investment_research.models import VerificationStatus
from investment_research.orchestrator import replay_ask
from investment_research.orchestrator_report import render_ask_report, _check
from investment_research.research_catalog import load_catalog
from investment_research.source_pipeline import _extract
from investment_research.sources import FetchResponse, SourceError, SourceSpec, _validate
from tests.test_scan_coverage import html
from tests import test_scan_four_assets as four

GAS = '천연가스 지금 들어갈 만해? UNG랑 BOIL까지 포함해서 딥다이브해.'
GOLD = '금 지금 투자할 만해? 수요와 현재 가격까지 딥다이브해.'
BROAD = '광범위 원자재 지금 투자할 만해? 어떤 원자재가 실제로 끌고 있는지도 딥다이브해.'
HEADER = 'PRELIMINARY Wed, Sep 09, 2026 SETT. PRICE PT. CHGE\n'

# Authored values, deliberately different from live data. Right-hand strategy
# rows and non-YTD columns detect both two-column and return-column mistakes.
DASHBOARD = '''INDEX INVESTMENT STRATEGY: Daily Index Dashboard
September 9, 2026
COMMODITIES
INDEX                 Daily       MTD       YTD       12M
S&P GSCI Indices
S&P GSCI              1.00%       2.00%     18.00%    80.00%
Energy                1.10%       2.10%     40.00%    81.00%
Industrial Metals     1.20%       2.20%      5.00%    82.00%
Precious Metals       1.30%       2.30%     -4.00%    83.00%
Agriculture           1.40%       2.40%      3.00%    84.00%    Dynamic Roll    9.00%    8.00%    12.00%    90.00%
Livestock             1.50%       2.50%     -2.00%    85.00%    3M Forward      7.00%    6.00%    14.00%    91.00%
Natural Gas           1.60%       2.60%     -5.00%    86.00%    Light Energy    5.00%    4.00%     8.00%    92.00%
WTI Crude             1.70%       2.70%     25.00%    87.00%
Brent Crude           1.80%       2.80%     30.00%    88.00%
Gold                  1.90%       2.90%     -2.00%    89.00%
Physical Gold (Spot)   2.00%       3.00%     -1.00%    90.00%
Source: S&P Dow Jones Indices LLC and/or its affiliates. Index performance based on total return except the S&P Global Carbon Credit, which is based on excess return. Returns are in USD unless otherwise stated.
'''


def bulletin():
    # Authored high/low/open differ from settlement to detect column mistakes.
    gas = 'NG FUT               NATURAL GAS HENRY HUB (PHYSICAL)\n'
    for month, price in [
        ('OCT26', '3.000'),
        ('NOV26', '3.300'),
        ('DEC26', '3.600'),
        ('JAN27', '3.900'),
        ('FEB27', '3.400'),
        ('MAR27', '3.100'),
    ]:
        gas += month + ' 8.0 9.0 / 7.0 ' + price + ' + 0.100 1 2 3\n'
    oil = 'CL FUT               NYMEX CRUDE OIL (PHYSICAL)\n'
    for month, price in [('OCT26', '60.00'), ('NOV26', '61.00'), ('DEC26', '62.00')]:
        oil += month + ' 80.0 90.0 / 70.0 ' + price + ' - 1.00 1 2 3\n'
    metals = 'GC FUT               COMEX GOLD FUTURES\nDEC26 8000 9000 / 7000 2000.00 - 10.00 1 2 3\nTOTAL GC FUT\n'
    metals += 'HG FUT               COMEX COPPER FUTURES\nDEC26 8.0 9.0 / 7.0 4.0000 + 0.1000 1 2 3\nTOTAL HG FUT\n'
    return HEADER + gas + 'TOTAL NG FUT\n' + oil + 'TOTAL CL FUT\n' + metals


def weights():
    values = {
        'energy': [10, 10, 5, 5, 5, 5],
        'industrial': [4] * 5,
        'precious': [5] * 2,
        'agriculture': [2.5] * 8,
        'livestock': [4, 3, 3],
    }
    text = 'iShares S&P GSCI. The date of this prospectus is May 22, 2026.\n'
    text += 'The components, in each case as of February 27, 2026, are as follows:\nDollar Weight\n'
    for group, tickers in data.GROUPS.items():
        for ticker, value in zip(tickers, values[group]):
            text += 'Authored commodity ' + str(value) + '% ' + ticker + ' name\n'
    return (
        text
        + 'The quantity is a dated constituent quantity. Contracts roll from the fifth to the ninth business day. Contango may reduce return.\n'
    )


def cot():
    out = StringIO()
    writer = csv.writer(out)
    for asset, code, name in [
        ('NATGAS', '023651', 'NAT GAS NYME - NEW YORK MERCANTILE EXCHANGE'),
        ('GOLD', '088691', 'GOLD - COMMODITY EXCHANGE INC.'),
    ]:
        r = ['0'] * 191
        r[0] = name
        r[1] = '260908'
        r[2] = '2026-09-08'
        r[3] = code
        for i, v in [(7, '1000'), (13, '120'), (14, '200'), (55, '0'), (61, '20'), (62, '10')]:
            r[i] = v
        writer.writerow(r)
    return out.getvalue()


class CommodityTests(unittest.TestCase):
    ask = four.FourAssetTests.ask
    row = four.FourAssetTests.row
    audit = four.FourAssetTests.audit
    reb_envelope = four.FourAssetTests.reb_envelope
    flow_html = four.FourAssetTests.flow_html

    def setUp(self):
        four.FourAssetTests.setUp(self)
        self.now += timedelta(days=2)
        self.catalog = replace(self.catalog, commodity=deepcopy(load_catalog().commodity))
        self.pdfs = {
            b'%PDF-energy': bulletin(),
            b'%PDF-metals': bulletin(),
            b'%PDF-agri': HEADER + "CORN FUT\nDEC26 400'0 405'0 / 399'0 402'2 + 1'0 1 2\nTOTAL CORN FUT\n",
            b'%PDF-weights': weights(),
            b'%PDF-wasde': 'WASDE-675 September 11, 2026. '
            + 'Corn production for 2026/27 is forecast at 15.8 billion bushels, down 213 million from last month. '
            + 'Corn ending stocks are lowered 86 million bushels to 1.6 billion. '
            + 'Projected 2026/27 global ending stocks are raised 3.0 million tons to 276.3 million.',
        }
        self.calls = []
        self.pdfs[b'%PDF-dashboard'] = DASHBOARD
        decoder = patch('investment_research.commodity_data.pdf_text', side_effect=lambda b: self.pdfs[b])
        decoder.start()
        self.addCleanup(decoder.stop)

    def history(self):
        rows = []
        points = {
            date(2026, 7, 31) + timedelta(days=7 * i): str(v) for i, v in enumerate([800, 850, 900, 950, 1000, 1100])
        }
        for i, year in enumerate(range(2021, 2026)):
            d = date.fromisocalendar(year, 36, 5)
            points[d] = str(900 + i * 100)
            points[d - timedelta(days=7)] = str(820 + i * 100)
        for d, v in sorted(points.items()):
            rows.append(
                '<tr><td>'
                + d.strftime('%Y-%b')
                + '</td><td>'
                + d.strftime('%m/%d')
                + '</td><td>'
                + v
                + '</td>'
                + ('<td></td>' * 8)
                + '</tr>'
            )
        header = (
            '<tr><th>Year-Month</th>'
            + ''.join('<th>Week ' + str(i) + '</th>' for i in range(1, 6))
            + '</tr><tr>'
            + ('<th>End Date</th><th>Value</th>' * 5)
            + '</tr>'
        )
        return (
            'Lower 48 States Natural Gas Working Underground Storage (Billion Cubic Feet)<table>'
            + header
            + ''.join(rows)
            + '</table>Release Date: 9/9/2026'
        )

    def fetch(self, url, timeout, max_bytes):
        self.calls.append(url)
        if url in self.missing or urlsplit(url).hostname in self.missing:
            raise SourceError('authored unavailable')
        if url.endswith('/robots.txt'):
            return FetchResponse(b'User-agent: *\nAllow: /\n', 'text/plain')
        if 'Section61_' in url:
            return FetchResponse(b'%PDF-energy', 'application/pdf')
        if 'Section62_' in url:
            return FetchResponse(b'%PDF-metals', 'application/pdf')
        if 'Section03_' in url:
            return FetchResponse(b'%PDF-agri', 'application/pdf')
        if url == data.GSG_PROSPECTUS:
            return FetchResponse(b'%PDF-weights', 'application/pdf')
        if url == data.GSCI_DASHBOARD:
            return FetchResponse(b'%PDF-dashboard', 'application/pdf')
        if url.endswith('/wasde0926.pdf'):
            return FetchResponse(b'%PDF-wasde', 'application/pdf')
        if url == data.HISTORY:
            return html(self.history())
        if 'wsahddy.txt' in url:
            return FetchResponse(
                (
                    'HEATING DEGREE DAY DATA WEEKLY SUMMARY POPULATION-WEIGHTED '
                    + 'LAST DATE OF DATA COLLECTION PERIOD IS SEP 5, 2026 GAS HOME HEATING CUSTOMER WEIGHTED REGION '
                    + 'UNITED STATES 10 -2 3 0 0 0 0 0 OIL HOME HEATING'
                ).encode(),
                'text/plain',
            )
        if 'wsacddy.txt' in url:
            return FetchResponse(
                (
                    'COOLING DEGREE DAY DATA WEEKLY SUMMARY POPULATION-WEIGHTED '
                    + 'LAST DATE OF DATA COLLECTION PERIOD IS SEP 5, 2026 UNITED STATES 12 2 -1 0 0 0 0 0'
                ).encode(),
                'text/plain',
            )
        if 'f_disagg.txt' in url:
            return FetchResponse(cot().encode(), 'text/plain')
        if url == data.WGC_ETF:
            return html(
                'Gold ETF Flows: August 2026 Published: 9 September, 2026 '
                + 'adding US$2bn; holdings rose 5t to 100t. AUM rose 1000 percent, never a flow.'
            )
        if url == data.WGC_Q2:
            rows = [
                ['', "Q2'25", "Q3'25", "Q4'25", "Q1'26", "Q2'26", 'yoy', 'qoq'],
                ['Central Banks & Other inst.', '100', '100', '100', '80', '120', '20', '50'],
                ['Jewellery Consumption', '300', '290', '280', '275', '270', '-10', '-2'],
                ['Total Bar and Coin', '90', '90', '90', '90', '100', '11', '11'],
            ]
            return html(
                'Gold Demand Trends: Q2 2026 Quarterly gold supply and demand by sector, tonnes <table>'
                + ''.join('<tr>' + ''.join('<td>' + v + '</td>' for v in r) + '</tr>' for r in rows)
                + '</table>'
            )
        if url == 'https://www.federalreserve.gov/releases/h10/current/':
            return html(
                'Foreign Exchange Rates - H.10 Release Date: September 10, 2026 <table>'
                + '<tr><th>Currency</th><th>Units</th><th>Sep. 8</th><th>Sep. 9</th></tr>'
                + '<tr><td>1) BROAD</td><td>JAN06=100</td><td>100.0</td><td>101.0</td></tr></table>'
            )
        if 'data.sec.gov/submissions/' in url:
            cik = '1376227' if '1376227' in url else '1415311'
            forms = ['424B3', '10-Q'] if cik == '1376227' else ['424B3', '424I', '424I']
            rows = dict(
                form=forms,
                filingDate=(
                    ['2026-04-24', '2026-08-07'] if cik == '1376227' else ['2026-03-26', '2026-03-31', '2026-03-31']
                ),
                reportDate=['', '2026-06-30'] if cik == '1376227' else ['', '', ''],
                accessionNumber=['0000000000-26-00000' + str(i) for i in range(len(forms))],
                primaryDocument=(
                    ['ung-prospectus.htm', 'ung-quarter.htm']
                    if cik == '1376227'
                    else ['boil-prospectus.htm', 'other.htm', 'boil-registration.htm']
                ),
            )
            return FetchResponse(json.dumps(dict(cik=int(cik), filings=dict(recent=rows))).encode(), 'application/json')
        if 'ung-prospectus.htm' in url:
            return html(
                'United States Natural Gas Fund. '
                + 'the near month contract to expire, except when it is near expiration, then next month contract to expire. '
                + 'until the near month contract is within two weeks of expiration, when, over a four-day period the benchmark moves. '
                + 'Management Fees 0.60 % Total Annual Fund Operating Expenses 1.17 %.'
            )
        if 'ung-quarter.htm' in url:
            return html(
                'United States Natural Gas Fund. NYMEX Natural Gas Futures NG August 2026 contracts, expiring July 2026 100'
            )
        if 'boil-prospectus.htm' in url:
            raise SourceError('authored combined filing exceeds reviewed limit')
        if 'boil-registration.htm' in url:
            return html('Rule 424(i) ProShares Ultra Bloomberg Natural Gas (BOIL)')
        r = four.FourAssetTests.fetch(self, url, timeout, max_bytes)
        if '/239561/' in url or '/239757/' in url:
            return html(
                r.body.decode()
                + ' Sponsor Fee: Fees as stated in the prospectus '
                + ('0.25' if '/239561/' in url else '0.75')
                + '%'
            )
        return r

    def parse(self, block, body=None, asset='NATGAS', fields=None):
        if block in (
            'gas_curve_a',
            'gas_curve_b',
            'broad_energy',
            'broad_energy_curve',
            'broad_metals',
            'gold_futures',
            'broad_agri',
            'gsg_terms',
        ) or block.startswith('weights_'):
            self.pdfs[b'%PDF-parser'] = body or bulletin()
            body = b'%PDF-parser'
        response = FetchResponse(
            body if isinstance(body, bytes) else (body or bulletin()).encode(),
            'application/pdf' if isinstance(body, bytes) else 'text/html',
        )
        url = (
            data.CME + 'Section61_Energy_Futures_Products.pdf'
            if isinstance(body, bytes)
            else 'https://fixture.example.org/document'
        )
        return data.parse_candidate(
            'minimum_deep_document_v1',
            response,
            dict(url=url, asset_id=asset, index_identity_fields={'block': block, **(fields or {})}),
        )

    def test_three_questions_start_directly_and_reuse_existing_pipeline(self):
        for question, asset in [(GAS, 'NATGAS'), (GOLD, 'GOLD'), (BROAD, 'BROAD_COMMODITIES')]:
            with self.subTest(asset=asset):
                run = self.ask(question)
                self.assertEqual(list(run.input['plan']['modes']), ['asset_deep_dive'])
                self.assertEqual({m['id'] for m in run.input['methods']}, {asset})
                self.assertNotIn('scan', run.input)
                self.assertIsNone(run.opportunity)
                self.assertFalse(any(i['purpose'] == 'opportunity_scan' for i in run.invocations))
                self.assertTrue(any(i['function'] == 'validate_evidence' for i in run.invocations))
                self.assertTrue(any(i['function'] == 'commodity_data.calculations' for i in run.invocations))
                self.assertTrue((run.directory / 'report.md').exists())
                self.assertLessEqual(len(run.discovery['requests']), 64)

    def test_six_contracts_use_settlement_not_open_high_or_low(self):
        records = self.parse('gas_curve_a')['records'] + self.parse('gas_curve_b')['records']
        self.assertEqual([r['quote'] for r in records], ['3.000', '3.300', '3.600', '3.900', '3.400', '3.100'])
        self.assertEqual(len({r['definition']['scope'] for r in records}), 6)
        self.assertEqual({r['definition']['period'] for r in records}, {'2026-09-09'})
        self.assertTrue(all('preliminary' in r['definition']['adjustment'] for r in records))

    def test_curve_unknown_date_or_duplicate_delivery_month_is_rejected(self):
        for raw in [bulletin().replace('Sep 09, 2026', 'not a date'), bulletin().replace('MAR27', 'JAN27')]:
            with self.assertRaises(SourceError):
                self.parse('gas_curve_a', raw)

    def test_signed_daily_change_is_not_rejected_as_negative_price(self):
        r = self.parse('gold_futures', asset='GOLD')['records']
        self.assertEqual(r[0]['quote'], '2000.00')
        self.assertEqual(_extract(r[1]['quote'], r[1]['extraction'], r[1]['definition']), Decimal(-10))
        self.assertIsNone(
            _extract('- 10.0', 'spaced_signed_decimal_v1', {**r[1]['definition'], 'measure': 'unreviewed value'})
        )

    def test_five_week_injections_and_same_iso_reference_hand_checked(self):
        run = self.ask(GAS)
        ms = {m.id: m for m in run.result.metrics}
        injections = [m.value for k, m in sorted(ms.items()) if k.startswith('CALC_COMMODITY_GAS_INJECTION_')]
        self.assertEqual(injections, [Decimal(50)] * 4 + [Decimal(100)])
        self.assertEqual(ms['CALC_COMMODITY_GAS_REFERENCE_INJECTION'].value, Decimal(80))
        self.assertEqual(ms['CALC_COMMODITY_NG_CURVE_2026-10_TO_2026-11'].value, Decimal(10))
        self.assertIn('실현 roll', ms['CALC_COMMODITY_NG_CURVE_2026-10_TO_2026-11'].limitations[0])

    def test_missing_reference_week_does_not_fabricate_mean(self):
        old = self.history
        with patch.object(self, 'history', side_effect=lambda: old().replace('<td>820</td>', '<td></td>')):
            run = self.ask(GAS)
        self.assertNotIn('CALC_COMMODITY_GAS_REFERENCE_INJECTION', {m.id for m in run.result.metrics})

    def test_actual_monthly_production_not_current_feedgas(self):
        run = self.ask(GAS)
        report = render_ask_report(run)
        self.assertIn('당일 feedgas 아님', report)
        es = [
            e
            for e in run.case.evidence
            if e.provenance and e.provenance.definition['measure'] == 'EIA_US_DRY_GAS_PRODUCTION'
        ]
        self.assertEqual({e.period for e in es}, {'2025-07', '2026-06', '2026-07'})
        self.assertTrue(all(e.unit == 'MMcf' for e in es))

    def test_hdd_weighted_heating_not_population_and_sentinel_not_zero(self):
        r = self.fetch(
            'https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/cdus/degree_days/wsahddy.txt', 10, 100000
        )
        parsed = self.parse('hdd', r.body.decode())
        self.assertEqual(parsed['records'][0]['quote'], '10')
        self.assertIn('gas home-heating customer', parsed['records'][0]['definition']['scope'])
        with self.assertRaises(SourceError):
            self.parse('hdd', r.body.decode().replace('UNITED STATES 10', 'UNITED STATES -999'))

    def test_cftc_exact_managed_money_code_and_net_change(self):
        run = self.ask(GAS)
        ms = {m.id: m for m in run.result.metrics}
        self.assertEqual(ms['CALC_COMMODITY_NATGAS_MM_NET'].value, Decimal(-80))
        self.assertEqual(ms['CALC_COMMODITY_NATGAS_MM_NET_CHANGE'].value, Decimal(10))
        with self.assertRaises(SourceError):
            self.parse('position', cot().replace('023651', '023652'))

    def test_ung_dated_holdings_not_current_and_boil_registration_not_terms(self):
        run = self.ask(GAS)
        report = render_ask_report(run)
        self.assertIn('2026-06-30 자료', report)
        self.assertIn('현재 보유 증거로 사용하지 않는다', report)
        self.assertIn('BOIL: 데이터 부족', report)
        self.assertNotIn(
            'BOIL_MANAGEMENT_FEE', {e.provenance.definition['measure'] for e in run.case.evidence if e.provenance}
        )
        self.assertIn('일일 2배 상품의 일반적 구조', report)

    def test_etf_flow_and_physical_change_not_aum(self):
        run = self.ask(GOLD)
        es = {e.provenance.definition['measure']: e for e in run.case.evidence if e.provenance}
        self.assertEqual(es['WGC_GLOBAL_GOLD_ETF_NET_FLOW'].value, Decimal(2))
        self.assertEqual(es['WGC_GLOBAL_GOLD_ETF_HOLDINGS_CHANGE'].value, Decimal(5))
        self.assertEqual(es['WGC_GLOBAL_GOLD_ETF_HOLDINGS'].value, Decimal(100))
        self.assertEqual(es['WGC_GLOBAL_GOLD_ETF_NET_FLOW'].period, '2026-08')
        raw = self.fetch(data.WGC_ETF, 10, 100000).body.decode().replace('holdings rose 5t to 100t.', '')
        with self.assertRaises(SourceError):
            self.parse('gold_etf', raw, 'GOLD')

    def test_quarter_demand_current_edition_yoy_not_current_october(self):
        run = self.ask(GOLD)
        ms = {m.id: m for m in run.result.metrics}
        self.assertEqual(ms['CALC_COMMODITY_GOLD_CENTRAL_BANK_YOY'].value, Decimal(20))
        self.assertEqual(ms['CALC_COMMODITY_GOLD_CENTRAL_BANK_QOQ'].value, Decimal(50))
        self.assertEqual(ms['CALC_COMMODITY_GOLD_JEWELLERY_YOY'].value, Decimal(-10))
        self.assertIn('당시 발표치', ms['CALC_COMMODITY_GOLD_CENTRAL_BANK_YOY'].limitations[0])

    def test_iau_single_level_does_not_imply_demand_change(self):
        report = render_ask_report(self.ask(GOLD))
        self.assertIn('IAU 수요 증가를 주장하지 않는다', report)
        self.assertIn('IAU 공식 sponsor fee 0.25%', report)

    def test_twenty_four_weights_sector_sums_hand_checked_and_lagged(self):
        run = self.ask(BROAD)
        ms = {m.id: m for m in run.result.metrics}
        for group, value in [
            ('ENERGY', 40),
            ('INDUSTRIAL', 20),
            ('PRECIOUS', 10),
            ('AGRICULTURE', 20),
            ('LIVESTOCK', 10),
        ]:
            self.assertEqual(ms['CALC_COMMODITY_GSCI_' + group + '_WEIGHT'].value, Decimal(value))
        es = [
            e
            for e in run.case.evidence
            if e.provenance and e.provenance.definition['measure'].startswith('GSCI_WEIGHT_')
        ]
        self.assertEqual(len(es), 24)
        self.assertEqual({e.period for e in es}, {'2026-02-27'})
        self.assertIn('현재 비중이 아니다', render_ask_report(run))
        self.assertIn('정확한 기여도는 계산하지 않는다', render_ask_report(run))

    def test_missing_duplicate_and_non_unit_total_weights_rejected(self):
        for raw in [
            weights().replace('10% LCO name', ''),
            weights().replace('10% LCO', '10% CL'),
            weights().replace('10% LCO', '80% LCO'),
        ]:
            with self.assertRaises(SourceError):
                self.parse('weights_0', raw, 'BROAD_COMMODITIES')

    def test_corn_eighth_cent_not_whole_cent_and_broad_roll_fee(self):
        run = self.ask(BROAD)
        ms = {m.id: m for m in run.result.metrics}
        self.assertEqual(ms['CALC_COMMODITY_CORN_SETTLEMENT'].value, Decimal('402.25'))
        report = render_ask_report(run)
        self.assertIn('contango(뒤 계약이 더 비쌈)', report)
        self.assertIn('GSG 공식 sponsor fee 0.75%', report)
        self.assertIn('현재 hedge 효과나 상관을 계산하지 않는다', report)

    def test_broad_uses_gold_component_not_entire_basket_demand(self):
        run = self.ask(BROAD)
        e = next(
            e
            for e in run.case.evidence
            if e.provenance and e.provenance.definition['measure'] == 'IAU_GOLD_PHYSICAL_HELD'
        )
        self.assertEqual(e.asset_ids, ('BROAD_COMMODITIES',))
        self.assertIn('IAU physical gold', e.provenance.definition['scope'])
        self.assertTrue(any('전체 원자재 수요로 확대하지 않는다' in s for s in e.limitations))

    def test_no_new_sources_automatically_become_bullish_or_recommended(self):
        for question, asset in [(GAS, 'NATGAS'), (GOLD, 'GOLD'), (BROAD, 'BROAD_COMMODITIES')]:
            review = assessment(self.ask(question))['assets'][asset]
            self.assertEqual(review['interpretation_status'], 'pending')
            self.assertNotIn('score', review)
            self.assertEqual(review['judgment'], 'mixed')

    def test_blocked_source_yields_data_gap_not_substitute(self):
        self.missing.add('www.cmegroup.com')
        run = self.ask(GAS)
        self.assertFalse(any(m.id.startswith('CALC_COMMODITY_NG_CURVE_') for m in run.result.metrics))
        self.assertIn('roll 조건 판단을 보류', render_ask_report(run))

    def test_anomalous_eth_flow_excluded_from_current_slot_and_sum(self):
        self.flow_cells[-1] = '-25000'
        run = self.ask()
        audit = scan.assess(run)
        eth = next(r for r in audit['universe'] if r['asset_id'] == 'ETH')
        self.assertEqual(eth['coverage_status'], 'partial_but_usable')
        self.assertIn('flow', eth['coverage']['missing_categories'])
        self.assertNotIn('SCAN_ETH_FIVE_REPORTED_DAYS_NET_FLOW', {m.id for m in run.result.metrics})
        self.assertFalse(
            any(
                p['asset_id'] == 'ETH' and p['definition']['measure'] == 'US_SPOT_ETH_ETF_DAILY_NET_FLOW'
                for p in audit['observations']
            )
        )
        self.assertTrue(run.evidence_validation['quarantined_ids'])
        self.assertIn('격리한 자료', render_ask_report(run))

    def test_current_quarantine_is_not_market_deterioration_against_previous_scan(self):
        old = self.ask()
        before = (old.directory / 'report.md').read_bytes()
        self.now += timedelta(seconds=1)
        self.flow_cells[-1] = '-25000'
        new = self.ask(previous_scan=old.directory)
        changes = scan.assess(new)['since_previous_scan']
        missing = [p for p in changes['unavailable'] if p['asset_id'] == 'ETH' and 'ETF' in p['measure']]
        self.assertTrue(missing)
        self.assertIn('하락했다는 뜻이 아니다', missing[0]['reason'])
        self.assertEqual((old.directory / 'report.md').read_bytes(), before)

    def test_provenance_and_every_numeric_input_are_traceable(self):
        run = self.ask(BROAD)
        manifest = json.loads((run.directory / 'run_manifest.json').read_text())
        ids = {e.id for e in run.case.evidence}
        self.assertTrue(all(set(m.input_ids) <= ids for m in run.result.metrics))
        self.assertTrue(all(e.provenance.snapshot_id for e in run.case.evidence if e.provenance))
        self.assertIn('evidence_validation', manifest)
        self.assertIn('commodity_research', manifest)
        self.assertTrue((run.directory / 'commodity_research.json').exists())

    def test_representative_futures_price_and_daily_change_use_same_expiry(self):
        run = self.ask(BROAD)
        december = next(
            e
            for e in run.case.evidence
            if e.provenance
            and e.provenance.definition['measure'] == 'CME_CL_SETTLEMENT'
            and e.provenance.definition['scope'].endswith('2026-12')
        )
        # Authored extra January contract has a different price. Adding it
        # must not pair January's level with December's reported daily change.
        january = replace(
            december,
            id='E_AUTHORED_JANUARY_PRICE',
            value=Decimal(74),
            text='Authored synthetic January settlement 74.00',
            provenance=replace(
                december.provenance,
                definition={
                    **december.provenance.definition,
                    'scope': december.provenance.definition['scope'].replace('2026-12', '2027-01'),
                },
            ),
        )
        run = replace(run, case=replace(run.case, evidence=(*run.case.evidence, january)))
        report = '\n'.join(broad_sections(View(run, 'BROAD_COMMODITIES')))
        row = next(line for line in report.splitlines() if line.startswith('| 에너지: WTI'))
        self.assertIn('62.00 달러/배럴', row)
        self.assertIn('2026-12 인도 계약', row)
        self.assertNotIn('74.00', row)
        self.assertIn('WTI 2026-12 인도 계약의 전 거래일 가격차 -1.0000', report)
        self.assertIn('2026-09-09 · 2026-12 인도 계약 · CBOT', report)

    def test_replay_all_three_reports_and_validation_without_network_or_decoder(self):
        for question in (GAS, GOLD, BROAD):
            with self.subTest(question=question):
                run = self.ask(question)
                before = (run.directory / 'report.md').read_bytes()
                with patch(
                    'investment_research.commodity_data.pdf_text',
                    side_effect=AssertionError('replay must not decode PDFs'),
                ):
                    replayed = replay_ask(run.directory)
                self.assertEqual(render_ask_report(replayed).encode(), before)
                self.assertEqual(run.evidence_validation, replayed.evidence_validation)

    def test_guarded_report_refuses_metric_with_quarantined_input(self):
        self.flow_cells[-1] = '-25000'
        run = self.ask()
        blocked = run.evidence_validation['quarantined_ids'][0]
        metric = replace(run.result.metrics[0], input_ids=(blocked,))
        changed = replace(run, result=replace(run.result, metrics=(metric,)))
        with self.assertRaisesRegex(SourceError, 'quarantined'):
            _check(changed)

    def test_scan_reports_new_curve_and_dated_demand_without_promoting_source_count(self):
        run = self.ask()
        report = render_ask_report(run)
        self.assertIn('천연가스 실제 만기별 선물', report)
        self.assertIn('전체 실물담보 금 ETF 2026-08 순유입', report)
        self.assertNotIn('기간이 다르고 선물곡선이 없어', report)
        self.assertFalse(set(scan.assess(run)['candidates']) & {'NATGAS', 'GOLD', 'BROAD_COMMODITIES'})

    def test_pdf_whitelist_excludes_arbitrary_pdf_or_full_retention(self):
        quote = dict(id='Q_TEST', quote='Authored', locator='page 1', definition='Authored synthetic')
        spec = SourceSpec(
            'TEST',
            data.CME + 'Section61_Energy_Futures_Products.pdf',
            data.CME + 'Section61_Energy_Futures_Products.pdf',
            'primary',
            'CME Group',
            'Authored fixture',
            content_type='application/pdf',
            policy_url='https://www.cmegroup.com/policy',
            policy_note='Authored small excerpt only',
            excerpts=(quote,),
        )
        _validate(spec)
        for change in [
            dict(url='https://fixture.example.org/arbitrary.pdf'),
            dict(type='community'),
            dict(retention='full', full_retention_permission='Authored permission'),
        ]:
            with self.assertRaises(SourceError):
                _validate(replace(spec, **change))

    def test_all_three_policy_bounds_preserved(self):
        for question in (GAS, GOLD, BROAD):
            run = self.ask(question)
            policy = json.loads((run.directory / 'input.json').read_text())
            self.assertTrue(run.discovery)
            self.assertLessEqual(len(run.discovery['requests']), 64)
            self.assertEqual(policy['commodity_coverage']['method_version'], data.VERSION)


if __name__ == '__main__':
    unittest.main()
