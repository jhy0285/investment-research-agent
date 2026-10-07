"""Synthetic macro observations; no values here describe actual markets.

Small, hand-checkable series exercise version availability and financial
definitions independently of a data provider or the current system clock.
"""

from dataclasses import asdict, replace
from datetime import date, datetime, timezone
from decimal import Decimal, localcontext
import json
import unittest
from unittest.mock import patch

from investment_research.macro import (
    MacroError,
    MacroObservation,
    SeriesDefinition,
    build_macro_snapshot,
    inflation_trend,
    make_registry,
    previous_change,
    select_series,
    trend_change,
    yield_spread,
    yoy,
)


AS_OF = date(2026, 10, 3)


def instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def definition(identifier="SYN_CPI", **changes):
    record = SeriesDefinition(
        canonical_id=identifier,
        name="Synthetic test CPI index, never market evidence",
        definition="Synthetic monthly price index for independent arithmetic checks",
        unit="index",
        frequency="monthly",
        adjustment="not_seasonally_adjusted",
        publisher="Synthetic test publisher",
        source_id="S_SYNTHETIC",
        jurisdiction="synthetic",
        release_characteristics="synthetic recorded release times",
        revision_characteristics="synthetic recorded vintages",
        max_age_days=90,
    )
    return replace(record, **changes)


def observation(series, period, value, **changes):
    period = date.fromisoformat(period)
    release = datetime(period.year, period.month, period.day, 18, tzinfo=timezone.utc)
    record = MacroObservation(
        series_id=series.canonical_id,
        observation_date=period,
        value=Decimal(value) if value is not None else None,
        retrieved_at=release,
        released_at=release,
        vintage_at=release,
        source_id=series.source_id,
        snapshot_id="ab" * 32,
        locator="synthetic observation " + period.isoformat(),
        unit=series.unit,
        frequency=series.frequency,
        adjustment=series.adjustment,
        currency=series.currency,
    )
    return replace(record, **changes)


def yield_definition(tenor, **changes):
    return definition(
        "SYN_YIELD_" + str(tenor),
        name="Synthetic nominal government yield",
        definition="Synthetic market yield quoted in percent, not a policy rate",
        unit="percent",
        frequency="daily",
        adjustment="unadjusted",
        currency="USD",
        yield_type="nominal_treasury",
        tenor_years=tenor,
        **changes,
    )


def snapshot_bytes(snapshot):
    def encode(value):
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        if isinstance(value, Decimal):
            return str(value)
        raise TypeError(type(value).__name__)

    return json.dumps(asdict(snapshot), default=encode, sort_keys=True,
                      ensure_ascii=False, separators=(",", ":")).encode("utf-8")


class MacroTests(unittest.TestCase):
    def setUp(self):
        for target in ("socket.create_connection", "urllib.request.urlopen"):
            blocker = patch(target, side_effect=AssertionError("Macro unit tests must stay offline"))
            blocker.start()
            self.addCleanup(blocker.stop)

    def test_historical_selection_uses_first_release_and_preserves_later_revision(self):
        series = definition()
        initial = observation(
            series, "2026-08-01", "100",
            released_at=instant("2026-09-10T14:00:00Z"),
            vintage_at=instant("2026-09-10T14:00:00Z"),
            retrieved_at=instant("2026-09-10T15:00:00Z"),
            vintage_id="synthetic-first-release",
        )
        revision = replace(
            initial, value=Decimal("101"),
            vintage_at=instant("2026-10-02T14:00:00Z"),
            revised_at=instant("2026-10-02T14:00:00Z"),
            retrieved_at=instant("2026-10-03T04:00:00Z"),
            vintage_id="synthetic-revision",
            snapshot_id="cd" * 32,
        )
        before = select_series(series, [initial, revision], date(2026, 9, 9))
        historical = select_series(series, [revision, initial], date(2026, 9, 30))
        current = select_series(series, [initial, revision], AS_OF)
        self.assertEqual(before.status, "blocked")
        self.assertIsNone(before.latest)
        self.assertEqual(historical.latest, initial)
        self.assertIn(revision, historical.excluded)
        self.assertEqual(current.latest, revision)
        self.assertEqual(set(current.all_observations), {initial, revision})
        self.assertEqual(initial.value, Decimal("100"))
        self.assertNotEqual(initial.id, revision.id)

    def test_each_future_availability_field_prevents_historical_use(self):
        series = definition()
        original = observation(series, "2026-08-01", "100")
        future = instant("2026-10-02T12:00:00Z")
        for field in ("released_at", "vintage_at", "revised_at", "known_at",
                      "valid_as_of", "observation_date"):
            with self.subTest(field=field):
                value = date(2026, 10, 1) if field in {"valid_as_of", "observation_date"} else future
                changed = replace(original, **{field: value})
                selected = select_series(series, [changed], date(2026, 9, 30))
                self.assertEqual(selected.status, "blocked")
                self.assertIsNone(selected.latest)
                self.assertEqual(selected.excluded, (changed,))

    def test_date_cutoff_means_end_of_day_but_datetime_is_exact(self):
        series = definition()
        released = observation(
            series, "2026-10-01", "100",
            released_at=instant("2026-10-03T21:00:00Z"),
            vintage_at=instant("2026-10-03T21:00:00Z"),
        )
        self.assertEqual(select_series(series, [released], instant("2026-10-03T20:59:59Z")).status, "blocked")
        self.assertEqual(select_series(series, [released], instant("2026-10-03T21:00:00Z")).latest, released)
        self.assertEqual(select_series(series, [released], AS_OF).latest, released)
        self.assertEqual(select_series(series, [released], instant("2026-10-04T06:00:00+09:00")).latest, released)
        with self.assertRaises(MacroError):
            select_series(series, [released], datetime(2026, 10, 3))

    def test_unknown_release_or_version_history_uses_retrieval_without_inventing_release(self):
        series = definition()
        base = observation(series, "2026-08-01", "100",
                           retrieved_at=instant("2026-10-03T04:00:00Z"), vintage_at=None)
        for release in (None, instant("2026-09-10T14:00:00Z")):
            with self.subTest(release=release):
                item = replace(base, released_at=release)
                past = select_series(series, [item], date(2026, 9, 30))
                now = select_series(series, [item], AS_OF)
                self.assertEqual(past.status, "blocked")
                self.assertEqual(now.latest, item)
                self.assertEqual(now.latest.released_at, release)
                self.assertIn("unknown", " ".join(now.diagnostics))

    def test_same_vintage_conflicts_are_errors_and_identical_duplicates_are_not_added(self):
        series = definition()
        original = observation(series, "2026-08-01", "100")
        with self.assertRaises(MacroError):
            select_series(series, [original, replace(original, value=Decimal("101"))], AS_OF)
        duplicate = replace(original, snapshot_id="cd" * 32)
        a = select_series(series, [original, duplicate, original], AS_OF)
        b = select_series(series, [duplicate, original], AS_OF)
        self.assertEqual(a.observations, b.observations)
        self.assertEqual(len(a.observations), 1)
        self.assertEqual(a.latest.value, Decimal("100"))

    def test_canonical_registry_keeps_distinct_definitions_and_is_immutable(self):
        raw = definition()
        transformed = replace(raw, canonical_id="SYN_CPI_YOY", unit="percent", transformation="yoy_v1")
        registry = make_registry([raw, raw, transformed])
        self.assertEqual(len(registry), 2)
        self.assertEqual(registry[raw.canonical_id], raw)
        with self.assertRaises(TypeError):
            registry[raw.canonical_id] = transformed
        for changes in ({"unit": "percent"}, {"adjustment": "seasonally_adjusted"},
                        {"transformation": "yoy_v1"}, {"definition": "Synthetic core CPI, different measure"}):
            with self.subTest(changes=changes), self.assertRaises(MacroError):
                make_registry([raw, replace(raw, **changes)])

    def test_observation_definition_changes_are_rejected_instead_of_silently_combined(self):
        series = definition(currency="USD")
        item = observation(series, "2026-08-01", "100")
        for changes in ({"unit": "percent"}, {"frequency": "daily"},
                        {"adjustment": "seasonally_adjusted"}, {"currency": "KRW"},
                        {"source_id": "S_OTHER_SYNTHETIC"}, {"observation_date": date(2026, 8, 15)}):
            with self.subTest(changes=changes), self.assertRaises(MacroError):
                select_series(series, [replace(item, **changes)], AS_OF)

    def test_observations_require_finite_decimal_and_timezone_aware_metadata(self):
        item = observation(definition(), "2026-08-01", "100")
        for value in (Decimal("NaN"), Decimal("Infinity"), 100.0):
            with self.subTest(value=value), self.assertRaises(MacroError):
                replace(item, value=value)
        for field in ("retrieved_at", "released_at", "vintage_at", "revised_at", "known_at"):
            with self.subTest(field=field), self.assertRaises(MacroError):
                replace(item, **{field: datetime(2026, 8, 2)})

    def test_latest_missing_and_delayed_publication_do_not_fall_back_to_older_value(self):
        series = definition()
        july = observation(series, "2026-07-01", "100")
        august = observation(series, "2026-08-01", None)
        latest_missing = select_series(series, [july, august], date(2026, 8, 31))
        absent = select_series(series, [july], date(2026, 8, 31), expected_period=date(2026, 8, 1))
        delayed = replace(august, value=Decimal("101"),
                          released_at=instant("2026-09-10T14:00:00Z"),
                          vintage_at=instant("2026-09-10T14:00:00Z"))
        not_released = select_series(series, [july, delayed], date(2026, 8, 31),
                                     expected_period=date(2026, 8, 1))
        self.assertEqual(latest_missing.status, "missing")
        self.assertIsNone(latest_missing.latest.value)
        self.assertEqual(absent.status, "missing")
        self.assertIsNone(absent.latest)
        self.assertEqual(not_released.status, "missing")
        self.assertIsNone(not_released.latest)
        self.assertIn(delayed, not_released.excluded)
        self.assertEqual(select_series(series, [], AS_OF).status, "missing")

    def test_stale_series_and_derived_value_remain_explicitly_stale(self):
        series = definition(max_age_days=30)
        old = observation(series, "2025-08-01", "100")
        current = observation(series, "2026-08-01", "110")
        selected = select_series(series, [old, current], AS_OF)
        metric = yoy(selected)
        self.assertEqual(selected.status, "stale")
        self.assertEqual(metric.status, "stale")
        self.assertEqual(metric.value, Decimal("10"))
        self.assertEqual(selected.latest.observation_date, date(2026, 8, 1))

    def test_yoy_uses_exact_endpoints_and_preserves_raw_value_and_provenance(self):
        series = definition()
        old = observation(series, "2025-08-01", "100")
        current = observation(series, "2026-08-01", "110")
        metric = yoy(select_series(series, [current, old], AS_OF))
        self.assertEqual(metric.value, Decimal("10"))  # Hand checked: 100 -> 110 is +10%.
        self.assertEqual(metric.unit, "percent")
        self.assertEqual(metric.status, "available")
        self.assertEqual(metric.input_series_ids, (series.canonical_id,))
        self.assertEqual(metric.input_observation_ids, (old.id, current.id))
        self.assertEqual(metric.observation_window, (date(2025, 8, 1), date(2026, 8, 1)))
        self.assertTrue(metric.formula)
        self.assertTrue(metric.assumptions)
        self.assertNotEqual(metric.output_series_id, series.canonical_id)
        self.assertEqual(current.value, Decimal("110"))
        self.assertIn("결측", " ".join(metric.diagnostics))

    def test_intermediate_missing_month_does_not_block_endpoint_yoy(self):
        series = definition()
        observations = [
            observation(series, "2025-08-01", "100"),
            observation(series, "2025-10-01", None),
            observation(series, "2026-07-01", "108"),
            observation(series, "2026-08-01", "110"),
        ]
        metric = yoy(select_series(series, observations, AS_OF))
        self.assertEqual(metric.value, Decimal("10"))
        self.assertEqual(metric.status, "available")
        self.assertEqual(len(metric.input_observation_ids), 2)
        self.assertIn("결측", " ".join(metric.diagnostics))

    def test_missing_invalid_or_wrong_month_endpoint_blocks_yoy_without_imputation(self):
        series = definition()
        current = observation(series, "2026-08-01", "110")
        for prior in (None, observation(series, "2025-07-01", "100"),
                      observation(series, "2025-08-01", None),
                      observation(series, "2025-08-01", "0"),
                      observation(series, "2025-08-01", "-100")):
            with self.subTest(prior=prior):
                items = [current] if prior is None else [current, prior]
                metric = yoy(select_series(series, items, AS_OF))
                self.assertEqual(metric.status, "blocked")
                self.assertIsNone(metric.value)
        old = observation(series, "2025-08-01", "100")
        for value in (None, Decimal("0")):
            with self.subTest(current=value):
                metric = yoy(select_series(series, [old, replace(current, value=value)], AS_OF))
                self.assertEqual(metric.status, "blocked")
                self.assertIsNone(metric.value)

    def test_yoy_rejects_percent_nonmonthly_or_already_transformed_series(self):
        for changes in ({"unit": "percent"}, {"frequency": "annual"}, {"transformation": "yoy_v1"}):
            with self.subTest(changes=changes):
                series = definition(**changes)
                selected = select_series(series, [observation(series, "2026-08-01", "10")], AS_OF)
                with self.assertRaises(MacroError):
                    yoy(selected)

    def test_inflation_can_slow_while_its_raw_price_index_rises(self):
        series = definition()
        items = [observation(series, period, value) for period, value in (
            ("2025-07-01", "100"), ("2025-08-01", "110"),
            ("2026-07-01", "110"), ("2026-08-01", "115.5"),
        )]
        selected = select_series(series, items, AS_OF)
        raw_change = previous_change(selected)
        inflation = inflation_trend(selected)
        self.assertEqual(raw_change.value, Decimal("5.5"))
        self.assertEqual(raw_change.direction, "up")
        self.assertEqual(yoy(selected).value, Decimal("5"))
        self.assertEqual(inflation.value, Decimal("-5"))  # Prior inflation 10%, now 5%.
        self.assertEqual(inflation.direction, "down")
        self.assertEqual(inflation.unit, "percentage_points")
        self.assertEqual(set(inflation.input_observation_ids), {item.id for item in items})

    def test_inflation_trend_requires_each_exact_endpoint_for_both_months(self):
        series = definition()
        items = [observation(series, period, value) for period, value in (
            ("2025-07-01", "100"), ("2025-08-01", "100"),
            ("2026-07-01", "108"), ("2026-08-01", "110"),
        )]
        for removed in items:
            with self.subTest(missing=removed.observation_date):
                remaining = [item for item in items if item != removed]
                metric = inflation_trend(select_series(series, remaining, AS_OF), period=date(2026, 8, 1))
                self.assertEqual(metric.status, "blocked")
                self.assertIsNone(metric.value)
                self.assertIsNone(metric.direction)

    def test_trend_direction_is_arithmetic_and_monthly_gaps_are_not_skipped(self):
        series = definition(unit="percent")
        prior = observation(series, "2026-07-01", "4")
        for value, expected, direction in (("4.5", ".5", "up"), ("3.5", "-.5", "down"), ("4", "0", "unchanged")):
            with self.subTest(value=value):
                current = observation(series, "2026-08-01", value)
                metric = trend_change(select_series(series, [prior, current], AS_OF))
                self.assertEqual(metric.value, Decimal(expected))
                self.assertEqual(metric.direction, direction)
                self.assertEqual(metric.unit, "percentage_points")
                self.assertEqual(metric.input_observation_ids, (prior.id, current.id))
        june = observation(series, "2026-06-01", "4")
        august = observation(series, "2026-08-01", "4.5")
        selected = select_series(series, [june, august], AS_OF)
        for metric in (trend_change(selected), previous_change(selected)):
            self.assertEqual(metric.status, "blocked")
            self.assertIsNone(metric.value)
            self.assertIsNone(metric.direction)

    def test_daily_previous_observation_handles_market_calendar_gap_explicitly(self):
        series = yield_definition(10)
        friday = observation(series, "2026-09-25", "4")
        tuesday = observation(series, "2026-09-29", "3.75")
        selected = select_series(series, [friday, tuesday], AS_OF)
        metric = previous_change(selected)
        self.assertEqual(metric.value, Decimal("-.25"))
        self.assertEqual(metric.direction, "down")
        self.assertEqual(metric.observation_window, (date(2026, 9, 25), date(2026, 9, 29)))
        self.assertEqual(trend_change(selected).status, "blocked")

    def test_yield_spread_has_hand_checked_units_including_negative_nominal_yields(self):
        ten, two = yield_definition(10), yield_definition(2)
        for long, short, expected in (("4.5", "4", ".5"), ("-.25", "-.75", ".5"), ("3", "4", "-1")):
            with self.subTest(long=long, short=short):
                a = observation(ten, "2026-09-29", long)
                b = observation(two, "2026-09-29", short)
                metric = yield_spread(select_series(ten, [a], AS_OF), select_series(two, [b], AS_OF))
                self.assertEqual(metric.value, Decimal(expected))
                self.assertEqual(metric.unit, "percentage_points")
                self.assertEqual(metric.status, "available")
                self.assertEqual(metric.input_observation_ids, (a.id, b.id))
                self.assertEqual(metric.observation_window, (date(2026, 9, 29),))

    def test_yield_spread_rejects_different_financial_definitions(self):
        ten, two = yield_definition(10), yield_definition(2)
        a = select_series(ten, [observation(ten, "2026-09-29", "4.5")], AS_OF)
        for changes in ({"unit": "basis_points"}, {"frequency": "monthly"},
                        {"currency": "KRW"}, {"currency": None},
                        {"yield_type": "real_treasury"}, {"yield_type": "target_policy_rate"},
                        {"adjustment": "adjusted"}, {"tenor_years": 3},
                        {"transformation": "previous_change_v1"}):
            with self.subTest(changes=changes):
                changed = replace(two, **changes)
                period = "2026-09-01" if changed.frequency == "monthly" else "2026-09-29"
                b = select_series(changed, [observation(changed, period, "4")], AS_OF)
                with self.assertRaises(MacroError):
                    yield_spread(a, b)
        with self.assertRaises(MacroError):
            yield_spread(a, select_series(two, [observation(two, "2026-09-29", "4")], date(2026, 10, 2)))

    def test_yield_spread_does_not_silently_choose_older_common_date(self):
        ten, two = yield_definition(10), yield_definition(2)
        long = [observation(ten, "2026-09-25", "4.5"), observation(ten, "2026-09-29", "4.75")]
        short = [observation(two, "2026-09-25", "4"), observation(two, "2026-09-28", "4.1")]
        a, b = select_series(ten, long, AS_OF), select_series(two, short, AS_OF)
        self.assertEqual(yield_spread(a, b).status, "blocked")
        self.assertIsNone(yield_spread(a, b).value)
        explicit = yield_spread(a, b, period=date(2026, 9, 25))
        self.assertEqual(explicit.value, Decimal(".5"))
        self.assertEqual(explicit.observation_window, (date(2026, 9, 25),))
        missing = select_series(two, [observation(two, "2026-09-29", None)], AS_OF)
        self.assertEqual(yield_spread(a, missing).status, "blocked")

    def test_snapshot_and_calculations_are_deterministic_without_network_or_decimal_context(self):
        cpi, ten, two = definition(), yield_definition(10), yield_definition(2)
        definitions = [cpi, ten, two]
        items = [
            observation(cpi, "2025-07-01", "100"), observation(cpi, "2025-08-01", "100"),
            observation(cpi, "2026-07-01", "105"), observation(cpi, "2026-08-01", "110"),
            observation(ten, "2026-09-25", "4"), observation(ten, "2026-09-29", "4.12345"),
            observation(two, "2026-09-25", "3.9"), observation(two, "2026-09-29", "3.98765"),
        ]
        pair = (ten.canonical_id, two.canonical_id)
        with localcontext() as context:
            context.prec = 3
            first = build_macro_snapshot(definitions, items, AS_OF, (cpi.canonical_id,), pair)
        with localcontext() as context:
            context.prec = 28
            repeated = build_macro_snapshot(list(reversed(definitions)), list(reversed(items)),
                                            AS_OF, (cpi.canonical_id,), pair)
        self.assertEqual(snapshot_bytes(first), snapshot_bytes(repeated))
        spread = next(metric for metric in first.metrics if metric.transformation == "yield_spread_v1")
        self.assertEqual(spread.value, Decimal(".13580"))
        self.assertEqual(next(metric for metric in first.metrics if metric.transformation == "yoy_v1").value,
                         Decimal("10"))
        self.assertEqual(next(metric for metric in first.metrics if metric.transformation == "inflation_trend_v1").value,
                         Decimal("5"))

    def test_snapshot_rejects_unknown_series_instead_of_dropping_data(self):
        cpi = definition()
        unrelated = definition("SYN_OTHER")
        with self.assertRaises(MacroError):
            build_macro_snapshot([cpi], [observation(unrelated, "2026-08-01", "100")], AS_OF)


if __name__ == "__main__":
    unittest.main()
