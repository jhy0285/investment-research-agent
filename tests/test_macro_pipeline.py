"""Synthetic public macro responses; no live market facts or network access.

The values and publisher labels here are invented, explicitly for testing. The
CSV layout mirrors the documented adapters so parsing, version retention, and
raw-to-evidence linkage can be checked without depending on an external site.
"""

from copy import deepcopy
from dataclasses import asdict
from datetime import date, datetime, timezone
from decimal import Decimal
import csv
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from investment_research.macro import MacroError, SeriesDefinition
from investment_research.sources import FetchResponse, SourceSpec, load_snapshot

ACQUIRED_AT = datetime(2026, 9, 10, 12, 0, 0, tzinfo=timezone.utc)
CPI_ID = "US_CPI_ALL_NSA"
TWO_ID = "US_TREASURY_2Y"
TEN_ID = "US_TREASURY_10Y"
FX_ID = "USD_KRW"
TWO_FIELD = "RIFLGFCY02_N.B"
TEN_FIELD = "RIFLGFCY10_N.B"
FX_FIELD = "RXI_N.B.KO"


def synthetic_source(identifier, mime, quote, locator):
    url = f"https://synthetic-macro.example.org/{identifier.lower()}"
    return SourceSpec(
        id=identifier,
        url=url,
        canonical_url=url,
        type="primary",
        publisher="Synthetic macro test publisher",
        title="Synthetic fixture, never actual market evidence",
        jurisdiction="US",
        topics=("synthetic-macro-test",),
        asset_ids=("CASH", "BOND", "EQUITY"),
        content_type=mime,
        access_method="public_api",
        policy_url="https://synthetic-macro.example.org/terms",
        policy_note="Synthetic HTTP fixture retained for offline tests only.",
        retention="full",
        full_retention_permission="The synthetic test data are authored for these tests.",
        max_age_days=90,
        excerpts=(
            {
                "id": "SELECTOR_" + identifier,
                "quote": quote,
                "locator": locator,
                "definition": "Synthetic provider identity marker, not a market claim.",
            },
        ),
    )


def cpi_document(values=None):
    values = values or (("2025", "M08", "100"), ("2026", "M07", "104"), ("2026", "M08", "105"))
    return json.dumps(
        {
            "status": "REQUEST_SUCCEEDED",
            "responseTime": 0,
            "message": [],
            "Results": {
                "series": [
                    {
                        "seriesID": "CUUR0000SA0",
                        "data": [
                            {
                                "year": year,
                                "period": period,
                                "periodName": "Synthetic reference period",
                                "value": value,
                                "footnotes": [{}],
                            }
                            for year, period, value in values
                        ],
                    }
                ]
            },
        }
    ).encode()


def fed_csv(fields, rows, *, currency=None, unit=None, identifier_prefix="H15/H15/"):
    buffer = StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "Series Description",
            *[
                (
                    "South Korean Won"
                    if field == FX_FIELD
                    else f"Market yield on U.S. Treasury securities at {2 if field == TWO_FIELD else 10}-year  constant maturity, quoted on investment basis"
                )
                for field in fields
            ],
        ]
    )
    writer.writerow(
        ["Unit:", *[(unit or ("Currency" if field == FX_FIELD else "Percent:_Per_Year")) for field in fields]]
    )
    writer.writerow(["Multiplier:", *["1" for _ in fields]])
    writer.writerow(["Currency:", *[(currency or ("KRW" if field == FX_FIELD else "NA")) for field in fields]])
    writer.writerow(["Unique Identifier: ", *[identifier_prefix + field for field in fields]])
    writer.writerow(["Time Period", *fields])
    writer.writerows(rows)
    return buffer.getvalue().encode()


def synthetic_plan_data():
    sources = (
        synthetic_source("S_CPI", "application/json", "CUUR0000SA0", "/Results/series/0/seriesID"),
        synthetic_source("S_YIELDS", "text/csv", "Time Period", "CSV header identity"),
        synthetic_source("S_FX", "text/csv", "Time Period", "CSV header identity"),
    )
    common = dict(
        adjustment="not_seasonally_adjusted",
        publisher="Synthetic macro test publisher",
        jurisdiction="US",
        revision_characteristics="unknown",
        release_characteristics="Unknown individual publication times; actual fetch time retained.",
    )
    definitions = (
        SeriesDefinition(
            CPI_ID,
            "합성 미국 CPI",
            "US all-items CPI index, NSA, synthetic values",
            "index",
            "monthly",
            source_id="S_CPI",
            max_age_days=90,
            **common,
        ),
        SeriesDefinition(
            TWO_ID,
            "합성 미국 국채 2년",
            "Nominal 2-year Treasury constant maturity yield, synthetic values",
            "percent",
            "daily",
            source_id="S_YIELDS",
            currency="USD",
            yield_type="nominal",
            tenor_years=2,
            max_age_days=20,
            **common,
        ),
        SeriesDefinition(
            TEN_ID,
            "합성 미국 국채 10년",
            "Nominal 10-year Treasury constant maturity yield, synthetic values",
            "percent",
            "daily",
            source_id="S_YIELDS",
            currency="USD",
            yield_type="nominal",
            tenor_years=10,
            max_age_days=20,
            **common,
        ),
        SeriesDefinition(
            FX_ID,
            "합성 달러당 원화",
            "KRW per one USD, synthetic values",
            "KRW_per_USD",
            "daily",
            source_id="S_FX",
            currency="KRW",
            max_age_days=20,
            **common,
        ),
    )
    return {
        "schema_version": "1",
        "id": "PLAN_SYNTHETIC_MACRO",
        "question": "합성 macro fixture의 정의와 당시 판본을 재현할 수 있는가?",
        "series": [asdict(item) for item in definitions],
        "sources": [asdict(item) for item in sources],
        "bindings": [
            {
                "series_id": CPI_ID,
                "source_id": "S_CPI",
                "adapter": "bls_cpi_v1",
                "field": "CUUR0000SA0",
                "start_date": "2025-01-01",
            },
            {
                "series_id": TWO_ID,
                "source_id": "S_YIELDS",
                "adapter": "fed_csv_v1",
                "field": TWO_FIELD,
                "start_date": "2025-01-01",
            },
            {
                "series_id": TEN_ID,
                "source_id": "S_YIELDS",
                "adapter": "fed_csv_v1",
                "field": TEN_FIELD,
                "start_date": "2025-01-01",
            },
            {
                "series_id": FX_ID,
                "source_id": "S_FX",
                "adapter": "fed_csv_v1",
                "field": FX_FIELD,
                "start_date": "2025-01-01",
            },
        ],
        "yoy_series_ids": [CPI_ID],
        "yield_pair": [TEN_ID, TWO_ID],
    }


class MacroPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.store = self.directory / "snapshots"
        self.plan_path = self.directory / "plan.json"
        self.data = synthetic_plan_data()
        self.requests = []
        self.documents = {
            self.data["sources"][0]["url"]: FetchResponse(cpi_document(), "application/json"),
            self.data["sources"][1]["url"]: FetchResponse(
                fed_csv(
                    (TWO_FIELD, TEN_FIELD),
                    (
                        ("2026-09-01", "1.50", "3.00"),
                        ("2026-09-02", "2.00", "3.50"),
                    ),
                ),
                "text/csv",
            ),
            self.data["sources"][2]["url"]: FetchResponse(
                fed_csv(
                    (FX_FIELD,),
                    (
                        ("2026-09-01", "1300"),
                        ("2026-09-02", "1310"),
                    ),
                    identifier_prefix="H10/H10/",
                ),
                "text/csv",
            ),
        }
        for target in ("socket.socket.connect", "socket.getaddrinfo", "investment_research.sources._fetch_http"):
            blocker = patch(target, side_effect=AssertionError("external HTTP/DNS forbidden in synthetic macro tests"))
            blocker.start()
            self.addCleanup(blocker.stop)

    def plan(self, data=None):
        from investment_research.macro_pipeline import load_macro_plan

        self.plan_path.write_text(json.dumps(self.data if data is None else data, ensure_ascii=False), encoding="utf-8")
        return load_macro_plan(self.plan_path)

    def fetcher(self, url, timeout, max_bytes):
        self.requests.append(url)
        response = self.documents[url]
        if isinstance(response, Exception):
            raise response
        return response

    def acquire_and_replay(self, data=None, *, now=ACQUIRED_AT):
        from investment_research.macro_pipeline import acquire_macro, replay_macro

        plan = self.plan(data)
        pins = acquire_macro(plan, self.store, fetcher=self.fetcher, now=now)
        return plan, pins, replay_macro(plan, self.store, pins)

    @staticmethod
    def selection(run, series_id):
        return next(item for item in run.snapshot.selections if item.definition.canonical_id == series_id)

    def test_live_mock_response_becomes_pinned_offline_observations(self):
        from investment_research.macro_pipeline import replay_macro

        plan, pins, run = self.acquire_and_replay()
        self.assertEqual(pins["schema_version"], "macro-pins-v1")
        self.assertEqual(pins["plan_id"], plan.id)
        self.assertEqual(len(self.requests), 3)
        self.assertEqual(set(pins["snapshots"]), {"S_CPI", "S_YIELDS", "S_FX"})
        for source_id, references in pins["snapshots"].items():
            self.assertEqual(len(references), 1)
            shot = load_snapshot(self.store, source_id, references[0])
            self.assertEqual(shot.status, "available")
            self.assertEqual(shot.source["retention"], "full")
        self.requests.clear()
        repeated = replay_macro(plan, self.store, pins)
        self.assertEqual(run, repeated)
        self.assertEqual(self.requests, [])
        cpi = self.selection(run, CPI_ID).latest
        self.assertEqual(cpi.observation_date, date(2026, 8, 1))
        self.assertEqual(cpi.value, Decimal("105"))
        self.assertIsNone(cpi.released_at)
        self.assertEqual(cpi.retrieved_at, ACQUIRED_AT)
        self.assertEqual(cpi.vintage_at, ACQUIRED_AT)
        self.assertEqual(cpi.snapshot_id, pins["snapshots"]["S_CPI"][0])
        self.assertIn("Results", cpi.locator)

    def test_live_retrieval_is_recorded_after_response_completion_and_cannot_leak_mid_request(self):
        from investment_research.macro_pipeline import acquire_macro, replay_macro

        before = datetime(2026, 9, 10, 12, 0, 0, tzinfo=timezone.utc)
        after = datetime(2026, 9, 10, 12, 0, 10, tzinfo=timezone.utc)
        midpoint = datetime(2026, 9, 10, 12, 0, 5, tzinfo=timezone.utc)
        completed = [False]

        class CollectionClock(datetime):
            @classmethod
            def now(cls, tz=None):
                value = after if completed[0] else before
                return cls.fromisoformat(value.isoformat()).astimezone(tz or timezone.utc)

        def finishing_fetcher(url, timeout, max_bytes):
            response = self.fetcher(url, timeout, max_bytes)
            # Advance the clock only once the synthetic response is available.
            completed[0] = True
            return response

        plan = self.plan()
        with (
            patch("investment_research.sources.datetime", CollectionClock),
            patch("investment_research.macro_pipeline.datetime", CollectionClock),
        ):
            pins = acquire_macro(plan, self.store, fetcher=finishing_fetcher)
        first = load_snapshot(self.store, "S_CPI", pins["snapshots"]["S_CPI"][0])
        self.assertEqual(datetime.fromisoformat(first.retrieved_at.replace("Z", "+00:00")), after)
        during_request = replay_macro(plan, self.store, pins, as_of=midpoint)
        self.assertTrue(all(item.status == "blocked" for item in during_request.snapshot.selections))
        self.assertTrue(all(item.latest is None for item in during_request.snapshot.selections))
        self.assertFalse(during_request.case.evidence)
        self.assertFalse(during_request.metrics)
        after_request = replay_macro(plan, self.store, pins, as_of=after)
        self.assertEqual(self.selection(after_request, CPI_ID).latest.value, Decimal("105"))
        self.assertEqual(self.selection(after_request, CPI_ID).latest.retrieved_at, after)
        self.assertEqual(self.selection(after_request, CPI_ID).latest.known_at, after)

    def test_transforms_have_independent_hand_checked_values_and_input_references(self):
        _, _, run = self.acquire_and_replay()
        cpi_metrics = [
            item
            for item in run.snapshot.metrics
            if item.input_series_ids == (CPI_ID,) and item.transformation == "yoy_v1"
        ]
        self.assertEqual(len(cpi_metrics), 1)
        self.assertEqual(cpi_metrics[0].value, Decimal("5"))  # 105 / 100 - 1 = 5%.
        self.assertEqual(set(cpi_metrics[0].observation_window), {date(2025, 8, 1), date(2026, 8, 1)})
        spread = next(item for item in run.snapshot.metrics if item.transformation == "yield_spread_v1")
        self.assertEqual(spread.value, Decimal("1.50"))  # 3.50% - 2.00% = 1.50 percentage points.
        self.assertEqual(spread.unit, "percentage_points")
        self.assertEqual(set(spread.input_series_ids), {TEN_ID, TWO_ID})
        raw_ids = {item.id for selected in run.snapshot.selections for item in selected.observations}
        for metric in (cpi_metrics[0], spread):
            self.assertTrue(metric.input_observation_ids)
            self.assertLessEqual(set(metric.input_observation_ids), raw_ids)
            self.assertTrue(metric.formula)
            self.assertTrue(metric.assumptions)
        bridge = next(item for item in run.metrics if item.id == spread.id)
        self.assertEqual(bridge.value, Decimal("1.50"))
        self.assertTrue(bridge.input_ids)
        self.assertLessEqual(set(bridge.input_ids), {item.id for item in run.case.evidence})

    def test_unknown_release_and_vintage_do_not_leak_into_historical_query(self):
        from investment_research.macro_pipeline import replay_macro

        plan, pins, _ = self.acquire_and_replay()
        run = replay_macro(plan, self.store, pins, as_of=date(2026, 9, 9))
        self.assertTrue(all(item.latest is None for item in run.snapshot.selections))
        self.assertTrue(all(item.status == "blocked" for item in run.snapshot.selections))
        self.assertFalse(any(item.value is not None for item in run.snapshot.metrics))
        self.assertTrue(
            any(
                "판본" in message or "공개" in message
                for item in run.snapshot.selections
                for message in item.diagnostics
            )
        )

    def test_bls_annual_average_is_not_a_month_and_missing_latest_is_not_forward_filled(self):
        self.documents[self.data["sources"][0]["url"]] = FetchResponse(
            cpi_document(
                (
                    ("2025", "M08", "100"),
                    ("2026", "M07", "104"),
                    ("2026", "M08", "-"),
                    ("2026", "M13", "777"),
                )
            ),
            "application/json",
        )
        _, _, run = self.acquire_and_replay()
        selected = self.selection(run, CPI_ID)
        self.assertEqual(len(selected.observations), 3)
        self.assertEqual(selected.latest.observation_date, date(2026, 8, 1))
        self.assertIsNone(selected.latest.value)
        self.assertEqual(selected.status, "missing")
        self.assertNotIn(Decimal("777"), [item.value for item in selected.observations])
        self.assertFalse(
            any(item.value is not None for item in run.snapshot.metrics if item.input_series_ids == (CPI_ID,))
        )

    def test_csv_nd_latest_is_preserved_as_missing_not_replaced_by_prior_quote(self):
        self.documents[self.data["sources"][2]["url"]] = FetchResponse(
            fed_csv(
                (FX_FIELD,),
                (
                    ("2026-09-01", "1300"),
                    ("2026-09-02", "1310"),
                    ("2026-09-03", "ND"),
                ),
                identifier_prefix="H10/H10/",
            ),
            "text/csv",
        )
        _, _, run = self.acquire_and_replay()
        selected = self.selection(run, FX_ID)
        self.assertEqual(selected.latest.observation_date, date(2026, 9, 3))
        self.assertIsNone(selected.latest.value)
        self.assertEqual(selected.status, "missing")
        self.assertTrue(any(item.value == Decimal("1310") for item in selected.observations))

    def test_late_cutoff_marks_stale_series_without_renaming_old_dates_as_current(self):
        from investment_research.macro_pipeline import replay_macro

        plan, pins, _ = self.acquire_and_replay()
        run = replay_macro(plan, self.store, pins, as_of=date(2027, 1, 1))
        self.assertTrue(all(item.status == "stale" for item in run.snapshot.selections))
        self.assertEqual(self.selection(run, CPI_ID).latest.observation_date, date(2026, 8, 1))
        self.assertEqual(self.selection(run, FX_ID).latest.observation_date, date(2026, 9, 2))

    def test_failed_http_source_yields_diagnostics_not_successful_evidence(self):
        self.documents[self.data["sources"][0]["url"]] = FetchResponse(
            b"Synthetic service down", "application/json", status=503
        )
        _, pins, run = self.acquire_and_replay()
        shot = load_snapshot(self.store, "S_CPI", pins["snapshots"]["S_CPI"][0])
        self.assertEqual(shot.status, "unavailable")
        self.assertIsNone(self.selection(run, CPI_ID).latest)
        self.assertFalse(any(item.source_id == "S_CPI" for item in run.case.evidence))
        self.assertTrue(run.diagnostics)
        self.assertEqual(self.selection(run, TEN_ID).status, "available")

    def test_provider_unit_currency_and_column_identity_changes_block_affected_series(self):
        original = self.documents[self.data["sources"][1]["url"]]
        malformed = (
            fed_csv((TWO_FIELD, TEN_FIELD), (("2026-09-02", "2", "3.5"),), unit="Basis_Points"),
            fed_csv((TWO_FIELD, TEN_FIELD), (("2026-09-02", "2", "3.5"),), currency="EUR"),
            fed_csv((TWO_FIELD, TEN_FIELD), (("2026-09-02", "2", "3.5"),), identifier_prefix="H10/H10/"),
            original.body.replace(TWO_FIELD.encode(), b"RIFLGFCY03_N.B"),
        )
        for document in malformed:
            with self.subTest(document=document[:80]):
                self.documents[self.data["sources"][1]["url"]] = FetchResponse(document, "text/csv")
                _, _, run = self.acquire_and_replay()
                self.assertIsNone(self.selection(run, TWO_ID).latest)
                self.assertFalse(
                    any(item.value is not None for item in run.snapshot.metrics if TWO_ID in item.input_series_ids)
                )
                self.assertTrue(run.diagnostics)

    def test_append_acquisition_preserves_old_values_and_uses_only_available_versions(self):
        from investment_research.macro_pipeline import acquire_macro, replay_macro

        plan, old_pins, old_run = self.acquire_and_replay()
        old_id = old_pins["snapshots"]["S_CPI"][0]
        old_bytes = (self.store / "S_CPI" / (old_id + ".json")).read_bytes()
        self.documents[self.data["sources"][0]["url"]] = FetchResponse(
            cpi_document(
                (
                    ("2025", "M08", "100"),
                    ("2026", "M07", "104"),
                    ("2026", "M08", "106"),
                )
            ),
            "application/json",
        )
        updated_at = datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)
        pins = acquire_macro(plan, self.store, previous_pins=old_pins, fetcher=self.fetcher, now=updated_at)
        self.assertEqual((self.store / "S_CPI" / (old_id + ".json")).read_bytes(), old_bytes)
        self.assertEqual(old_pins["snapshots"]["S_CPI"], [old_id])
        self.assertEqual(pins["snapshots"]["S_CPI"][0], old_id)
        self.assertEqual(len(pins["snapshots"]["S_CPI"]), 2)
        before_revision = replay_macro(plan, self.store, pins, as_of=ACQUIRED_AT)
        self.assertEqual(self.selection(before_revision, CPI_ID).latest.value, Decimal("105"))
        self.assertEqual(self.selection(old_run, CPI_ID).latest.value, Decimal("105"))
        after_revision = replay_macro(plan, self.store, pins)
        self.assertEqual(self.selection(after_revision, CPI_ID).latest.value, Decimal("106"))
        self.assertIsNone(self.selection(after_revision, CPI_ID).latest.revised_at)
        self.assertEqual(self.selection(after_revision, CPI_ID).latest.vintage_at, updated_at)
        self.assertEqual(
            len(
                [
                    item
                    for item in self.selection(after_revision, CPI_ID).all_observations
                    if item.observation_date == date(2026, 8, 1)
                ]
            ),
            2,
        )

    def test_tampered_snapshot_and_pins_are_rejected_before_analysis(self):
        from investment_research.macro_pipeline import replay_macro

        plan, pins, _ = self.acquire_and_replay()
        wrong_pins = deepcopy(pins)
        wrong_pins["plan_sha256"] = "0" * 64
        with self.assertRaises(MacroError):
            replay_macro(plan, self.store, wrong_pins)
        path = self.store / "S_CPI" / (pins["snapshots"]["S_CPI"][0] + ".json")
        data = json.loads(path.read_text(encoding="utf-8"))
        data["payload"]["raw_base64"] = "dGFtcGVyZWQ="
        path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises((MacroError, ValueError)):
            replay_macro(plan, self.store, pins)

    def add_release_fixture(self, value="105"):
        source = asdict(synthetic_source("S_RELEASE", "text/html", "Synthetic release", "Synthetic release passage"))
        source["retention"] = "excerpt"
        source["published_at"] = "2026-09-09T12:30:00+00:00"
        source["excerpts"] = [
            {
                "id": "RELEASE_TIME",
                "quote": "8:30 a.m. (ET) September 9, 2026",
                "locator": "Synthetic release header",
                "definition": "Synthetic exact release time",
            },
            {
                "id": "CPI_PERIOD",
                "quote": "CONSUMER PRICE INDEX - AUGUST 2026",
                "locator": "Synthetic title",
                "definition": "Synthetic reference month",
            },
            {
                "id": "CPI_VALUE",
                "quote": f"index level of {value} (1982-84=100)",
                "locator": "Synthetic index sentence",
                "definition": "Synthetic NSA all-items index cross-check",
            },
        ]
        self.data["sources"].append(source)
        self.data["bindings"][0]["release_source_id"] = source["id"]
        self.documents[source["url"]] = FetchResponse(
            (
                "<html><body>"
                + "".join("<p>" + item["quote"] + "</p>" for item in source["excerpts"])
                + "</body></html>"
            ).encode(),
            "text/html",
        )

    def acquire_with_delayed_release(self, plan, api_at, release_at, previous_pins=None):
        from investment_research.macro_pipeline import acquire_macro
        from investment_research.sources import acquire

        def separately_timed_source(spec, store, fetcher=None, now=None):
            instant = release_at if spec.id == "S_RELEASE" else api_at
            return acquire(spec, store, fetcher=fetcher, now=instant)

        with patch("investment_research.macro_pipeline.acquire", side_effect=separately_timed_source):
            return acquire_macro(plan, self.store, previous_pins=previous_pins, fetcher=self.fetcher, now=release_at)

    def test_future_appended_release_does_not_change_past_observation_ids_or_metrics(self):
        from investment_research.macro_pipeline import replay_macro

        self.add_release_fixture()
        plan = self.plan()
        api_at = datetime(2026, 9, 10, 12, 0, 0, tzinfo=timezone.utc)
        release_at = datetime(2026, 9, 10, 12, 0, 5, tzinfo=timezone.utc)
        cutoff = datetime(2026, 9, 10, 12, 0, 10, tzinfo=timezone.utc)
        first_pins = self.acquire_with_delayed_release(plan, api_at, release_at)
        first = replay_macro(plan, self.store, first_pins, as_of=cutoff)
        original = self.selection(first, CPI_ID).latest
        self.assertEqual(original.value, Decimal("105"))
        self.assertEqual(original.known_at, release_at)
        yoy = next(item for item in first.snapshot.metrics if item.transformation == "yoy_v1")
        self.assertEqual(yoy.value, Decimal("5"))

        # New retrieval versions may have unchanged values. Their later helper
        # metadata must still leave an earlier research query unchanged.
        next_api_at = datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc)
        next_release_at = datetime(2026, 9, 11, 12, 0, 5, tzinfo=timezone.utc)
        updated_pins = self.acquire_with_delayed_release(plan, next_api_at, next_release_at, first_pins)
        self.assertEqual(len(updated_pins["snapshots"]["S_CPI"]), 2)
        self.assertEqual(len(updated_pins["snapshots"]["S_RELEASE"]), 2)
        replayed = replay_macro(plan, self.store, updated_pins, as_of=cutoff)
        self.assertEqual(self.selection(replayed, CPI_ID).latest.value, Decimal("105"))
        self.assertEqual(self.selection(replayed, CPI_ID).latest.id, original.id)
        for series_id in (CPI_ID, TWO_ID, TEN_ID, FX_ID):
            before = self.selection(first, series_id).observations
            after = self.selection(replayed, series_id).observations
            self.assertEqual(tuple(item.id for item in after), tuple(item.id for item in before))
            self.assertEqual(tuple(item.value for item in after), tuple(item.value for item in before))
        self.assertEqual(replayed.snapshot.metrics, first.snapshot.metrics)
        self.assertEqual(replayed.metrics, first.metrics)
        self.assertEqual(replayed.release_provenance[original.id], first.release_provenance[original.id])

    def test_future_release_helper_does_not_block_already_retrieved_api_value(self):
        from investment_research.macro_pipeline import replay_macro

        self.add_release_fixture()
        plan = self.plan()
        api_at = datetime(2026, 9, 10, 12, 0, 0, tzinfo=timezone.utc)
        release_at = datetime(2026, 9, 10, 12, 0, 5, tzinfo=timezone.utc)
        cutoff = datetime(2026, 9, 10, 12, 0, 3, tzinfo=timezone.utc)
        pins = self.acquire_with_delayed_release(plan, api_at, release_at)
        run = replay_macro(plan, self.store, pins, as_of=cutoff)
        selected = self.selection(run, CPI_ID)
        self.assertEqual(selected.status, "available")
        self.assertEqual(selected.latest.value, Decimal("105"))
        self.assertEqual(selected.latest.observation_date, date(2026, 8, 1))
        self.assertEqual(selected.latest.known_at, api_at)
        self.assertIsNone(selected.latest.released_at)
        self.assertNotIn(selected.latest.id, run.release_provenance)
        self.assertTrue(all(item.released_at is None for item in selected.observations))
        yoy = next(item for item in run.snapshot.metrics if item.transformation == "yoy_v1")
        self.assertEqual(yoy.value, Decimal("5"))
        self.assertEqual(yoy.status, "available")

    def test_official_release_crosscheck_keeps_release_distinct_from_retrieval_and_vintage(self):
        from investment_research.macro_pipeline import replay_macro

        self.add_release_fixture()
        plan, pins, run = self.acquire_and_replay()
        latest = self.selection(run, CPI_ID).latest
        self.assertEqual(latest.released_at, datetime(2026, 9, 9, 12, 30, tzinfo=timezone.utc))
        self.assertEqual(latest.retrieved_at, ACQUIRED_AT)
        self.assertEqual(latest.vintage_at, ACQUIRED_AT)
        historical = replay_macro(plan, self.store, pins, as_of=date(2026, 9, 9))
        self.assertEqual(self.selection(historical, CPI_ID).status, "blocked")
        self.assertIsNone(self.selection(historical, CPI_ID).latest)
        self.assertIsNone(
            next(
                item for item in self.selection(run, CPI_ID).observations if item.observation_date == date(2025, 8, 1)
            ).released_at
        )

    def test_conflicting_release_index_and_api_value_are_not_silently_merged(self):
        self.add_release_fixture(value="106")
        _, _, run = self.acquire_and_replay()
        self.assertIsNone(self.selection(run, CPI_ID).latest)
        self.assertFalse(any(item.source_id == "S_CPI" for item in run.case.evidence))
        self.assertTrue(any("differs" in message and "revision" in message for message in run.diagnostics))
        self.assertEqual(self.selection(run, FX_ID).status, "available")

    def test_release_time_origin_links_observation_to_its_exact_pinned_release(self):
        from investment_research.macro_pipeline import macro_manifest
        from investment_research.macro_report import render_macro_report

        self.add_release_fixture()
        _, pins, run = self.acquire_and_replay()
        latest = self.selection(run, CPI_ID).latest
        provenance = run.release_provenance[latest.id]
        self.assertEqual(provenance["source_id"], "S_RELEASE")
        self.assertEqual(provenance["snapshot_id"], pins["snapshots"]["S_RELEASE"][0])
        self.assertEqual(set(provenance["excerpt_ids"]), {"RELEASE_TIME", "CPI_PERIOD", "CPI_VALUE"})
        self.assertTrue(provenance["method"])
        report = render_macro_report(run)
        manifest = macro_manifest(run, report)
        self.assertEqual(manifest["release_provenance"][latest.id], provenance)
        binding = next(item for item in manifest["bindings"] if item["series_id"] == CPI_ID)
        self.assertEqual(binding["release_source_id"], "S_RELEASE")
        self.assertIn(provenance["snapshot_id"], report)
        self.assertIn("RELEASE_TIME", report.replace("\\_", "_"))
        self.assertIn(latest.id, report.replace("\\_", "_"))

    def test_bls_frequency_change_blocks_source_without_converting_period(self):
        self.documents[self.data["sources"][0]["url"]] = FetchResponse(
            cpi_document(
                (
                    ("2025", "M08", "100"),
                    ("2026", "Q03", "105"),
                )
            ),
            "application/json",
        )
        _, _, run = self.acquire_and_replay()
        self.assertIsNone(self.selection(run, CPI_ID).latest)
        self.assertFalse(any(item.source_id == "S_CPI" for item in run.case.evidence))
        self.assertTrue(any("frequency/period" in message for message in run.diagnostics))

    def test_timeout_records_failure_without_generating_observations(self):
        self.documents[self.data["sources"][0]["url"]] = TimeoutError("Synthetic timeout")
        _, pins, run = self.acquire_and_replay()
        self.assertEqual(load_snapshot(self.store, "S_CPI", pins["snapshots"]["S_CPI"][0]).status, "timeout")
        self.assertIsNone(self.selection(run, CPI_ID).latest)
        self.assertFalse(any(item.source_id == "S_CPI" for item in run.case.evidence))


if __name__ == "__main__":
    unittest.main()
