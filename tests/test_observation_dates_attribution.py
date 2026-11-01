"""Row-date and commodity attribution regressions; authored offline fixtures."""

from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal
import json
import unittest
from unittest.mock import patch

from investment_research import commodity_data as data, scan_coverage, scan
from investment_research.commodity_report import broad_sections, View, _same_period_groups
from investment_research.orchestrator import replay_ask
from investment_research.orchestrator_report import render_ask_report, observation_audit, _check
from investment_research.source_pipeline import observation_timing, dated_evidence
from investment_research.sources import SourceError
from tests import test_commodity_deep as fixture


class TimingTests(unittest.TestCase):
    def test_calendar_periods_preserve_precision_and_bounds(self):
        expected = {
            '2026-09-22': ('2026-09-22', 'day', '2026-09-22'),
            '2025-07': ('2025-07-31', 'month', '2025-07-01'),
            '2026-06': ('2026-06-30', 'month', '2026-06-01'),
            '2024-02': ('2024-02-29', 'month', '2024-02-01'),
            '2025Q2': ('2025-06-30', 'quarter', '2025-04-01'),
            '2026 2Q': ('2026-06-30', 'quarter', '2026-04-01'),
            '2026H1': ('2026-06-30', 'half_year', '2026-01-01'),
            '2025': ('2025-12-31', 'year', '2025-01-01'),
            'week_ending_2026-10-03': ('2026-10-03', 'week_ending', None),
            '2025-07-01..2026-06-30': ('2026-06-30', 'reporting_interval', '2025-07-01'),
        }
        for period, (end, precision, start) in expected.items():
            with self.subTest(period=period):
                t = observation_timing(period)
                self.assertEqual((t['observed_at'], t['precision'], t['period_start']), (end, precision, start))

    def test_unknown_date_has_no_report_or_capture_fallback(self):
        for period in ('annual_fee', 'prospectus', 'rolling_24h', 'forecast_window', 'daily'):
            self.assertIsNone(observation_timing(period)['observed_at'])

    def test_actual_snapshot_is_separate_from_its_economic_window(self):
        t = observation_timing('exchange_snapshot', '2026-10-06T08:12:03Z')
        self.assertEqual(t['observed_at'], '2026-10-06T08:12:03+00:00')
        self.assertEqual(t['precision'], 'snapshot')
        self.assertIsNone(t['period_end'])

    def test_invalid_calendar_and_disagreeing_explicit_date_are_rejected(self):
        for period, explicit in [
            ('2026-13', None),
            ('2026-02-30', None),
            ('2026-10-02..2026-09-02', None),
            ('2026-09-22', '2026-09-29T00:00:00Z'),
        ]:
            with self.subTest(period=period), self.assertRaises(SourceError):
                observation_timing(period, explicit)


class IntegrityAndAttributionTests(unittest.TestCase):
    # Reuse fixture helpers without inheriting (and rerunning) its 28 tests.
    setUp = fixture.CommodityTests.setUp
    ask = fixture.CommodityTests.ask
    row = fixture.CommodityTests.row
    audit = fixture.CommodityTests.audit
    reb_envelope = fixture.CommodityTests.reb_envelope
    flow_html = fixture.CommodityTests.flow_html
    fetch = fixture.CommodityTests.fetch
    history = fixture.CommodityTests.history

    def test_gas_daily_and_weekly_dates_are_not_latest_series_date(self):
        run = self.ask(fixture.GAS)
        price = {e.period: e for e in run.case.evidence if e.provenance.definition['measure'] == 'EIA_HENRY_HUB_SPOT'}
        self.assertEqual(
            {p: e.observed_at for p, e in price.items()},
            {'2026-09-02': date(2026, 9, 2), '2026-09-09': date(2026, 9, 9)},
        )
        stocks = {
            e.period: e for e in run.case.evidence if e.provenance.definition['measure'] == 'EIA_US_WORKING_GAS_STOCK'
        }
        self.assertEqual(stocks['2026-08-28'].observed_at, date(2026, 8, 28))
        self.assertEqual(stocks['2026-09-04'].observed_at, date(2026, 9, 4))
        self.assertEqual(stocks['2026-08-28'].value, Decimal(1000))

    def test_monthly_production_LNG_and_prior_week_have_their_own_period(self):
        run = self.ask(fixture.GAS)
        for measure in ('EIA_US_DRY_GAS_PRODUCTION', 'EIA_US_LNG_EXPORTS'):
            rows = {e.period: e for e in run.case.evidence if e.provenance.definition['measure'] == measure}
            self.assertEqual(
                {p: e.observed_at for p, e in rows.items()},
                {'2025-07': date(2025, 7, 31), '2026-06': date(2026, 6, 30), '2026-07': date(2026, 7, 31)},
            )
        previous = [
            e for e in run.case.evidence if e.provenance.definition['measure'].startswith('EIA_GAS_ISO_WEEK_REFERENCE_')
        ]
        self.assertEqual({e.observed_at.year for e in previous}, {2021, 2022, 2023, 2024, 2025})
        self.assertTrue(all(e.observed_at == date.fromisoformat(e.period) for e in previous))
        self.assertIn('본문 비교 날짜와 evidence 관측일 대조', render_ask_report(run))

    def test_gold_quarter_and_dollar_history_dates(self):
        run = self.ask(fixture.GOLD)
        q = {
            e.period: e
            for e in run.case.evidence
            if e.provenance.definition['measure'] == 'WGC_CENTRAL_BANK_NET_DEMAND'
        }
        self.assertEqual(
            {p: e.observed_at for p, e in q.items()},
            {'2025Q2': date(2025, 6, 30), '2026Q1': date(2026, 3, 31), '2026Q2': date(2026, 6, 30)},
        )
        usd = {e.period: e for e in run.case.evidence if e.provenance.definition['measure'] == 'FED_BROAD_USD_INDEX'}
        self.assertEqual(usd['2026-09-08'].observed_at, date(2026, 9, 8))
        self.assertEqual(usd['2026-09-09'].observed_at, date(2026, 9, 9))

    def test_scan_crypto_rates_property_oil_dates_and_native_macro(self):
        run = self.ask()
        audit = observation_audit(run)
        self.assertEqual(audit['mismatched_ids'], [])
        measures = {e.provenance.definition['measure'] for e in run.case.evidence if dated_evidence(e)}
        for measure in (
            'COINBASE_BTC_USD_DAILY_CLOSE',
            'COINBASE_ETH_USD_DAILY_CLOSE',
            'EIA_WTI_SPOT',
            'KR_GOVERNMENT_NOMINAL_3Y',
        ):
            self.assertIn(measure, measures)
        self.assertTrue(any(m.startswith('KR_APARTMENT_') for m in measures))
        for e in run.case.evidence:
            if e.provenance.definition['measure'] in ('COINBASE_BTC_USD_DAILY_CLOSE', 'COINBASE_ETH_USD_DAILY_CLOSE'):
                self.assertEqual(e.observed_at, date.fromisoformat(e.period[:10]))
        macro = [e for e in run.case.evidence if e.view == 'macro']
        self.assertTrue(macro)
        self.assertTrue(all(e.observed_at is not None for e in macro))

    def test_unknown_crypto_dates_block_trend_and_previous_scan_points(self):
        run = self.ask()
        crypto = {
            e.id
            for e in run.case.evidence
            if e.provenance.definition['measure'] in ('COINBASE_BTC_USD_DAILY_CLOSE', 'COINBASE_ETH_USD_DAILY_CLOSE')
        }
        case = replace(
            run.case, evidence=tuple(replace(e, observed_at=None) if e.id in crypto else e for e in run.case.evidence)
        )
        calc = scan_coverage.calculations(case, run.cutoff, require_dates=True)
        self.assertFalse(any(m.id in ('SCAN_BTC_WEEK_PRICE_CHANGE', 'SCAN_ETH_WEEK_PRICE_CHANGE') for m in calc))
        self.assertFalse(
            any(m.id == 'SCAN_BTC_PRICE_CHANGE' for m in scan.calculations(case, run.cutoff, require_dates=True))
        )
        points = scan_coverage.observations(replace(run, case=case))
        self.assertFalse(any(p['evidence_id'] in crypto for p in points))

    def test_unknown_gas_dates_block_injection_and_monthly_comparison(self):
        run = self.ask(fixture.GAS)
        ids = {
            e.id
            for e in run.case.evidence
            if e.provenance.definition['measure']
            in ('EIA_US_WORKING_GAS_STOCK', 'EIA_US_DRY_GAS_PRODUCTION', 'EIA_US_LNG_EXPORTS')
        }
        case = replace(
            run.case, evidence=tuple(replace(e, observed_at=None) if e.id in ids else e for e in run.case.evidence)
        )
        calc = data.calculations(case, run.cutoff, require_dates=True)
        self.assertFalse(any(set(m.input_ids) & ids for m in calc))

    def test_manifest_dates_distinguish_observation_release_capture_and_period(self):
        run = self.ask(fixture.GAS)
        audit = json.loads((run.directory / 'observation_integrity.json').read_text())
        row = next(
            r for r in audit['records'] if r['measure'] == 'EIA_US_DRY_GAS_PRODUCTION' and r['period'] == '2025-07'
        )
        self.assertEqual(row['evidence_observed_at'], '2025-07-31')
        self.assertEqual(row['source_series_or_edition_at'], '2026-07-31')
        self.assertEqual(row['precision'], 'month')
        self.assertEqual(row['period_start'], '2025-07-01')
        self.assertNotEqual(row['retrieved_at'][:10], row['evidence_observed_at'])
        self.assertEqual(audit['mismatched_ids'], [])
        manifest = json.loads((run.directory / 'run_manifest.json').read_text())
        self.assertEqual(manifest['observation_integrity']['path'], 'observation_integrity.json')

    def test_report_refuses_silently_replacing_historical_date(self):
        run = self.ask(fixture.GAS)
        e = next(
            e
            for e in run.case.evidence
            if e.provenance.definition['measure'] == 'EIA_HENRY_HUB_SPOT' and e.period == '2026-09-02'
        )
        case = replace(
            run.case,
            evidence=tuple(replace(r, observed_at=date(2026, 9, 9)) if r.id == e.id else r for r in run.case.evidence),
        )
        with self.assertRaises(SourceError):
            _check(replace(run, case=case, result=replace(run.result, case=case)))

    def test_official_sector_YTD_not_MTD_or_12M_columns(self):
        parsed = data._gsci_returns(fixture.DASHBOARD, 'gsci_groups_a')
        self.assertEqual([r['quote'] for r in parsed['records']], ['40.00', '5.00', '-4.00'])
        self.assertEqual(parsed['observed_at'], '2026-09-09')
        self.assertTrue(all('total_return_YTD' in r['definition']['adjustment'] for r in parsed['records']))

    def test_right_hand_strategy_rows_and_spot_return_are_separate(self):
        roll = data._gsci_returns(fixture.DASHBOARD, 'gsci_roll')['records']
        self.assertEqual([r['quote'] for r in roll], ['12.00', '14.00', '8.00'])
        gold = data._gsci_returns(fixture.DASHBOARD, 'gsci_gold')['records']
        self.assertNotEqual(gold[0]['definition']['adjustment'], gold[1]['definition']['adjustment'])
        self.assertEqual(gold[1]['definition']['measure'], 'SP_GSCI_PHYSICAL_GOLD_SPOT_YTD_SPOT_RETURN')

    def test_missing_definition_duplicate_row_or_date_are_rejected(self):
        for bad in (
            fixture.DASHBOARD.replace('YTD', 'FY1'),
            fixture.DASHBOARD.replace('Returns are in USD', 'Returns are in EUR'),
            fixture.DASHBOARD + '\nSeptember 10, 2026',
            fixture.DASHBOARD + '\nEnergy 1% 2% 99% 88%',
        ):
            with self.assertRaises(SourceError):
                data._gsci_returns(bad, 'gsci_groups_a')

    def test_attribution_has_same_window_and_no_fake_contribution_or_roll_calculation(self):
        run = self.ask(fixture.BROAD)
        groups = _same_period_groups(View(run, 'BROAD_COMMODITIES').facts)
        self.assertEqual(len(groups), 5)
        report = render_ask_report(run)
        for text in (
            '2025-12-31 → 2026-09-09',
            '+40.00%',
            '-4.00%',
            '상승의 중심은 에너지',
            'GSG 상승 원인의 정확한 분해는 미확인',
            '근사 기여도도 만들지 않았다',
            '실현 roll return',
            'collateral return',
        ):
            self.assertIn(text, report)
        self.assertFalse(any('attribution' in m.method or 'contribution' in m.method for m in run.result.metrics))
        self.assertTrue(
            any(e.provenance.definition['measure'] == 'SP_GSCI_ENERGY_YTD_TOTAL_RETURN' for e in run.case.evidence)
        )
        self.assertEqual(self.calls.count(data.GSCI_DASHBOARD), 1)

    def test_mismatched_sector_dates_are_never_combined(self):
        run = self.ask(fixture.BROAD)
        changed = replace(
            run,
            case=replace(
                run.case,
                evidence=tuple(
                    (
                        replace(e, observed_at=date(2026, 9, 8))
                        if e.provenance.definition['measure'] == 'SP_GSCI_PRECIOUS_YTD_TOTAL_RETURN'
                        else e
                    )
                    for e in run.case.evidence
                ),
            ),
        )
        text = '\n'.join(broad_sections(View(changed, 'BROAD_COMMODITIES')))
        self.assertNotIn('상승의 중심은 에너지', text)
        self.assertIn('상승 원인의 정확한 분해는 미확인', text)

    def test_missing_sector_source_is_disclosed_not_filled_with_GSG_return(self):
        self.missing.add(data.GSCI_DASHBOARD)
        run = self.ask(fixture.BROAD)
        report = render_ask_report(run)
        self.assertIn('상승 원인의 정확한 분해는 미확인', report)
        self.assertNotIn('상승의 중심은 에너지', report)
        self.assertFalse(any(e.provenance.definition['measure'].startswith('SP_GSCI_') for e in run.case.evidence))

    def test_new_report_and_audit_replay_without_network_or_PDF_decoder(self):
        run = self.ask(fixture.BROAD)
        before = render_ask_report(run)
        with (
            patch('socket.create_connection', side_effect=AssertionError('network forbidden')),
            patch('investment_research.commodity_data.pdf_text', side_effect=AssertionError('decoder forbidden')),
        ):
            replay = replay_ask(run.directory)
        self.assertEqual(render_ask_report(replay), before)
        self.assertEqual(observation_audit(replay), observation_audit(run))

    def test_old_bad_quarter_dates_are_excluded_without_modifying_old_artifacts(self):
        previous = self.ask()
        before = (previous.directory / 'report.md').read_bytes()
        quarter = [
            e for e in previous.case.evidence if e.provenance.definition['measure'] == 'WGC_CENTRAL_BANK_NET_DEMAND'
        ]
        legacy = replace(
            previous,
            input={k: v for k, v in previous.input.items() if k != 'observation_dates_version'},
            case=replace(
                previous.case,
                evidence=tuple(
                    replace(e, observed_at=date(2026, 6, 30)) if e in quarter else e for e in previous.case.evidence
                ),
            ),
        )
        anchor = scan_coverage.capture(legacy, require_dates=True)
        self.assertEqual({p['period'] for p in anchor['excluded_observation_dates']}, {'2025Q2', '2026Q1'})
        self.assertEqual((previous.directory / 'report.md').read_bytes(), before)
        self.now += timedelta(days=1)
        current = self.ask()
        result = scan_coverage.compare(
            scan_coverage.observations(current), anchor, current.cutoff, current.input['synthetic']
        )
        self.assertFalse(
            any(
                r['measure'] == 'WGC_CENTRAL_BANK_NET_DEMAND' and r['status'] == 'regressed_observation'
                for r in result['observations']
            )
        )
        self.assertTrue(any('이전 관측일' in r['reason'] for r in result['newly_observable']))
        self.assertEqual(len(result['excluded_previous_observation_dates']), 2)

    def test_previous_unknown_history_is_not_used_for_a_change(self):
        previous = self.ask()
        anchor = scan_coverage.capture(previous)
        point = next(p for p in anchor['observations'] if p['definition']['measure'] == 'COINBASE_ETH_USD_DAILY_CLOSE')
        rows = tuple(
            (
                replace(
                    e,
                    provenance=replace(
                        e.provenance, definition={**e.provenance.definition, 'period': 'unknown_history'}
                    ),
                )
                if e.id == point['evidence_id']
                else e
            )
            for e in previous.case.evidence
        )
        legacy = replace(
            previous,
            case=replace(previous.case, evidence=rows),
            input={k: v for k, v in previous.input.items() if k != 'observation_dates_version'},
        )
        checked = scan_coverage.capture(legacy, require_dates=True)
        self.assertTrue(
            any(
                p['evidence_id'] == point['evidence_id'] and p['row_calendar_at'] is None
                for p in checked['excluded_observation_dates']
            )
        )
