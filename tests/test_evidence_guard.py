"""Hand-authored values: quarantine is a review boundary, never a truth score."""

from dataclasses import replace
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
import unittest

from investment_research.evidence_guard import guard_records, guard_case, validate_config, VERSION
from investment_research.models import (
    EvidenceRecord,
    EvidenceProvenance,
    SourceRecord,
    SourceProvenance,
    SourceType,
    Review,
    InterpretationStatus,
    VerificationStatus,
    ResearchClaim,
)
from investment_research.sources import SourceError
from investment_research.validation import load_case

NOW = datetime(2026, 10, 6, tzinfo=timezone.utc)
PENDING = Review(InterpretationStatus.PENDING, None, None, 'Authored synthetic fixture.')


def source(identifier='S_A', publisher='Authored provider A', kind=SourceType.DATA_PROVIDER, origin=None):
    p = SourceProvenance(
        '0' * 64,
        publisher,
        'Authored synthetic evidence',
        '2026-10-05T12:00:00Z',
        'US',
        ('test',),
        'text/plain',
        'public_http',
        'https://fixture.example.org/policy',
        'Authored fixture',
        'excerpt',
        '1' * 64,
        '2' * 64,
        '3' * 64,
        'available',
        None,
        '2026-10-05',
        '2026-10-05',
        'fresh',
    )
    return SourceRecord(
        identifier,
        kind,
        publisher,
        'https://fixture.example.org/' + identifier,
        None,
        None,
        date(2026, 10, 5),
        origin,
        ('Synthetic only.',),
        p,
    )


def evidence(identifier='E_1', value='100', day='2026-10-01', sid='S_A', **changes):
    definition = dict(
        measure='US_SPOT_ETH_ETF_DAILY_NET_FLOW',
        unit='USD_million',
        period=day,
        currency='USD',
        scope='US spot Ethereum ETFs reported by Farside',
        adjustment='complete_row_provider_reported_not_issuer_confirmed',
    )
    definition.update(changes)
    return EvidenceRecord(
        identifier,
        sid,
        value or 'null',
        'Authored fixture token',
        date(2026, 10, 5),
        date(2026, 10, 6),
        ('ETH',),
        'quantitative',
        'external_fact',
        VerificationStatus.SUPPORTED,
        PENDING,
        ('Synthetic fixture.',),
        Decimal(value) if value is not None else None,
        definition['unit'],
        definition['period'],
        definition['currency'],
        EvidenceProvenance('0' * 64, 'Q_1', 'matched', 'fresh', definition),
    )


class GuardTests(unittest.TestCase):
    def guard(self, es, ss=None, **kw):
        adjusted, audit = guard_records(es, ss or [source()], NOW, **kw)
        return {e.id: e for e in adjusted}, {r['evidence_id']: r for r in audit['records']}, audit

    def extreme(self):
        return [
            evidence('E_' + str(i), v, '2026-10-0' + str(i)) for i, v in enumerate(['10', '-12', '11', '-25000'], 1)
        ]

    def test_same_provider_endpoint_conflict_quarantines_both(self):
        a = evidence()
        b = evidence('E_2', '200', sid='S_B')
        es, rows, audit = self.guard([a, b], [source(), source('S_B')])
        self.assertEqual(audit['quarantined_ids'], ['E_1', 'E_2'])
        self.assertEqual({r['status'] for r in rows.values()}, {'conflicting'})
        self.assertTrue(all(e.value is None for e in es.values()))
        self.assertEqual(a.value, Decimal(100))  # Immutable input/quote preserved.

    def test_dated_period_not_source_latest_date_identifies_observation(self):
        a = evidence()
        b = replace(evidence('E_2', '200', sid='S_B'), observed_at=date(2026, 10, 4))
        _, rows, _ = self.guard([a, b], [source(), source('S_B')])
        self.assertEqual(rows['E_1']['status'], 'conflicting')

    def test_same_rendering_duplicate_cannot_be_independent_cross_check(self):
        es = self.extreme()
        es.append(evidence('E_COPY', '-25000', '2026-10-04', 'S_B'))
        _, rows, _ = self.guard(es, [source(), source('S_B')])
        self.assertEqual(rows['E_4']['status'], 'anomalous')

    def test_extreme_value_needs_review_not_error_verdict(self):
        es, rows, audit = self.guard(self.extreme())
        self.assertEqual(audit['quarantined_ids'], ['E_4'])
        self.assertEqual(rows['E_4']['raw_value'], '-25000')
        self.assertEqual(rows['E_4']['raw_text'], '-25000')
        self.assertIsNone(es['E_4'].value)
        self.assertIn('오류로 확정하지 않는다', rows['E_4']['reasons'][0])

    def test_three_distinct_neighbours_required_not_duplicate_count(self):
        es = [
            evidence('E_1', '10'),
            evidence('E_2', '10'),
            evidence('E_3', '10'),
            evidence('E_4', '10000', '2026-10-02'),
        ]
        _, _, audit = self.guard(es)
        self.assertEqual(audit['quarantined_ids'], [])

    def test_real_zero_and_small_negative_flow_remain_numbers(self):
        es, _, audit = self.guard([evidence('ZERO', '0'), evidence('NEG', '-12', '2026-10-02')])
        self.assertEqual(es['ZERO'].value, Decimal(0))
        self.assertEqual(es['NEG'].value, Decimal(-12))
        self.assertEqual(audit['quarantined_ids'], [])

    def test_missing_and_partial_subtotal_not_final_zero(self):
        missing = evidence('MISSING', None)
        partial = evidence('PARTIAL', '2.5', adjustment='partial_row_not_final_total')
        es, rows, audit = self.guard([missing, partial], numeric_ids=['MISSING', 'PARTIAL'])
        self.assertIsNone(es['MISSING'].value)
        self.assertEqual(es['PARTIAL'].value, Decimal('2.5'))  # Explicit raw subtotal.
        self.assertEqual(es['PARTIAL'].verification, VerificationStatus.UNVERIFIED)
        self.assertEqual({r['status'] for r in rows.values()}, {'incomplete'})
        self.assertEqual(len(audit['quarantined_ids']), 2)

    def test_usd_and_usd_million_not_automatically_converted(self):
        es, rows, _ = self.guard([evidence(unit='USD')])
        self.assertEqual(rows['E_1']['status'], 'unit_mismatch')
        self.assertIsNone(es['E_1'].value)

    def test_percent_vs_decimal_and_tonnes_vs_ounces(self):
        for measure, unit, currency in [
            ('US_TIPS_10Y_CURRENT', 'fraction', 'USD'),
            ('IAU_GOLD_PHYSICAL_HELD', 'ounces', None),
        ]:
            with self.subTest(measure=measure):
                _, rows, _ = self.guard([evidence(measure=measure, unit=unit, currency=currency)])
                self.assertEqual(rows['E_1']['status'], 'unit_mismatch')

    def test_bcf_mmcf_and_monthly_daily_not_substituted(self):
        for unit, period in [('Bcf', '2026-07'), ('MMcf', '2026-07-31')]:
            with self.subTest(unit=unit, period=period):
                _, rows, _ = self.guard(
                    [
                        evidence(
                            measure='EIA_US_DRY_GAS_PRODUCTION',
                            unit=unit,
                            period=period,
                            currency=None,
                            adjustment='reported_monthly_actual_volume_not_forecast_not_daily_feedgas',
                        )
                    ]
                )
                self.assertEqual(rows['E_1']['status'], 'unit_mismatch')

    def test_total_per_share_price_nav_and_holdings_aum(self):
        for measure, unit, currency, adjustment in [
            ('ISHARES_GSG_NAV', 'USD', 'USD', 'issuer_reported_fund_NAV_not_spot_index_not_market_price'),
            ('ISHARES_GSG_NAV', 'USD_per_share', 'USD', 'market_price'),
            ('IAU_GOLD_PHYSICAL_HELD', 'tonnes', None, 'AUM'),
        ]:
            with self.subTest(measure=measure, unit=unit, adjustment=adjustment):
                _, rows, _ = self.guard(
                    [evidence(measure=measure, unit=unit, currency=currency, adjustment=adjustment)]
                )
                self.assertEqual(rows['E_1']['status'], 'unit_mismatch')

    def test_same_provider_different_units_quarantine_without_conversion(self):
        a = evidence(measure='Authored measure', unit='USD')
        b = evidence('E_2', '0.0001', sid='S_B', measure='Authored measure', unit='USD_million')
        _, rows, _ = self.guard([a, b], [source(), source('S_B')])
        self.assertEqual({r['status'] for r in rows.values()}, {'unit_mismatch'})

    def test_transcription_definition_unit_mismatch_quarantines(self):
        e = replace(evidence(), unit='USD')
        _, rows, _ = self.guard([e])
        self.assertEqual(rows['E_1']['status'], 'unit_mismatch')

    def test_nonfinite_number_and_unmatched_primary_check_are_blocked(self):
        _, rows, _ = self.guard([evidence(value='Infinity')])
        self.assertEqual(rows['E_1']['status'], 'anomalous')
        es = self.extreme()
        check = evidence('CHECK', '-25000', '2026-10-04', 'S_P')
        es.append(replace(check, provenance=replace(check.provenance, match_status='changed')))
        _, rows, _ = self.guard(es, [source(), source('S_P', 'Authored primary', SourceType.PRIMARY)])
        self.assertEqual(rows['E_4']['status'], 'anomalous')

    def test_different_scope_and_definition_not_conflicts(self):
        a = evidence()
        b = evidence('E_2', '200', scope='Other ETF universe')
        _, _, audit = self.guard([a, b])
        self.assertEqual(audit['quarantined_ids'], [])

    def test_independent_primary_same_definition_releases_suspicion(self):
        es = self.extreme()
        es.append(evidence('CHECK', '-25000', '2026-10-04', 'S_P'))
        adjusted, rows, _ = self.guard(es, [source(), source('S_P', 'Authored primary', SourceType.PRIMARY)])
        self.assertEqual(rows['E_4']['status'], 'cross_checked')
        self.assertEqual(rows['E_4']['cross_check_ids'], ['CHECK'])
        self.assertEqual(adjusted['E_4'].value, Decimal(-25000))

    def test_republished_origin_cannot_release_or_wrong_scope(self):
        for inherited, scope in [(True, None), (False, 'Other country')]:
            with self.subTest(inherited=inherited):
                es = self.extreme()
                check = evidence('CHECK', '-25000', '2026-10-04', 'S_P')
                if scope:
                    check = replace(
                        check,
                        provenance=replace(
                            check.provenance, definition={**check.provenance.definition, 'scope': scope}
                        ),
                    )
                es.append(check)
                _, rows, _ = self.guard(
                    es, [source(), source('S_P', 'Authored primary', SourceType.PRIMARY, 'S_A' if inherited else None)]
                )
                self.assertEqual(rows['E_4']['status'], 'anomalous')

    def test_future_or_stale_check_cannot_release(self):
        for stale in (True, False):
            with self.subTest(stale=stale):
                es = self.extreme()
                check = evidence('CHECK', '-25000', '2026-10-04', 'S_P')
                primary = source('S_P', 'Authored primary', SourceType.PRIMARY)
                if stale:
                    check = replace(check, provenance=replace(check.provenance, freshness='stale'))
                else:
                    primary = replace(
                        primary, provenance=replace(primary.provenance, retrieved_at='2026-10-07T00:00:00Z')
                    )
                es.append(check)
                _, rows, _ = self.guard(es, [source(), primary])
                self.assertEqual(rows['E_4']['status'], 'anomalous')

    def test_community_number_cannot_release_and_narrative_is_not_numeric_truth(self):
        es = self.extreme()
        es.append(evidence('CHECK', '-25000', '2026-10-04', 'S_P'))
        _, rows, _ = self.guard(es, [source(), source('S_P', 'Community', SourceType.COMMUNITY)])
        self.assertEqual(rows['E_4']['status'], 'anomalous')
        narrative = replace(evidence('STORY', '10000000'), kind='observed_narrative')
        _, rows, _ = self.guard([narrative])
        self.assertEqual(rows, {})

    def test_claim_using_quarantined_counter_evidence_is_withheld(self):
        case = load_case(Path(__file__).resolve().parents[1] / 'examples/cross_asset_case')
        claim = ResearchClaim(
            'C_TEST',
            'Authored claim',
            ('ETH',),
            VerificationStatus.SUPPORTED,
            PENDING,
            (),
            ('E_4',),
            None,
            (),
            'Authored recheck',
        )
        case = replace(case, evidence=tuple(self.extreme()), sources=(source(),), claims=(claim,))
        result, _ = guard_case(case, NOW)
        self.assertEqual(result.claims[0].verification, VerificationStatus.UNVERIFIED)
        self.assertEqual(result.claims[0].interpretation.status, InterpretationStatus.PENDING)

    def test_config_requires_version_and_unique_numeric_ids(self):
        self.assertEqual(validate_config(dict(method_version=VERSION, numeric_ids=['E_1']))['method_version'], VERSION)
        for change in [
            dict(method_version='unknown', numeric_ids=[]),
            dict(method_version=VERSION, numeric_ids=['E_1', 'E_1']),
        ]:
            with self.assertRaises(SourceError):
                validate_config(change)


if __name__ == '__main__':
    unittest.main()
