"""Macro CLI tests use synthetic responses and forbid live HTTP and DNS."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from io import StringIO
import json
from unittest.mock import patch
import unittest

from investment_research.__main__ import main
from investment_research.macro_pipeline import acquire_macro, replay_macro
from investment_research.sources import FetchResponse, load_snapshot
from tests import test_macro_pipeline as fixture


class MacroCLITests(unittest.TestCase):
    setUp = fixture.MacroPipelineTests.setUp
    plan = fixture.MacroPipelineTests.plan
    fetcher = fixture.MacroPipelineTests.fetcher

    def call(self, *arguments):
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = main(list(map(str, arguments)))
        return status, stdout.getvalue(), stderr.getvalue()

    @property
    def pins_path(self):
        return self.directory / "pins.json"

    def acquire_args(self):
        return ("macro", "acquire", self.plan_path, "--store", self.store, "--pins", self.pins_path)

    def replay_args(self):
        return ("macro", "replay", self.plan_path, "--store", self.store, "--pins", self.pins_path)

    def mock_acquisition(self, now=fixture.ACQUIRED_AT):
        return patch(
            "investment_research.macro_pipeline.acquire_macro",
            side_effect=lambda plan, store, previous_pins=None, **kwargs: acquire_macro(
                plan, store, previous_pins=previous_pins, fetcher=self.fetcher, now=now
            ),
        )

    def prepare_replay(self):
        plan = self.plan()
        pins = acquire_macro(plan, self.store, fetcher=self.fetcher, now=fixture.ACQUIRED_AT)
        self.pins_path.write_text(json.dumps(pins, ensure_ascii=False), encoding="utf-8")
        self.requests.clear()
        return plan, pins

    def test_acquire_creates_pins_with_success_status_for_each_source(self):
        self.plan()
        with self.mock_acquisition():
            status, stdout, stderr = self.call(*self.acquire_args())
        self.assertEqual(status, 0, stderr)
        self.assertEqual(stderr, "")
        pins = json.loads(self.pins_path.read_text(encoding="utf-8"))
        self.assertEqual(pins["schema_version"], "macro-pins-v1")
        self.assertEqual(pins["plan_id"], self.data["id"])
        self.assertEqual(len(self.requests), 3)
        for source_id, references in pins["snapshots"].items():
            self.assertEqual(load_snapshot(self.store, source_id, references[0]).status, "available")
            self.assertIn(source_id, stdout)

    def test_acquire_http_failure_keeps_failure_snapshot_and_returns_one(self):
        self.plan()
        self.documents[self.data["sources"][0]["url"]] = FetchResponse(
            b"Synthetic temporary outage", "application/json", status=503
        )
        with self.mock_acquisition():
            status, stdout, stderr = self.call(*self.acquire_args())
        self.assertEqual(status, 1, stderr)
        self.assertIn("unavailable", stdout)
        pins = json.loads(self.pins_path.read_text(encoding="utf-8"))
        self.assertEqual(load_snapshot(self.store, "S_CPI", pins["snapshots"]["S_CPI"][0]).status, "unavailable")

    def test_acquire_preserves_existing_pins_and_refuses_before_any_request(self):
        self.plan()
        existing = b"User-owned acquisition record\n"
        self.pins_path.write_bytes(existing)
        with patch(
            "investment_research.macro_pipeline.acquire_macro", side_effect=AssertionError("GET must not begin")
        ) as acquisition:
            status, stdout, stderr = self.call(*self.acquire_args())
        self.assertEqual(status, 2)
        self.assertEqual(stdout, "")
        self.assertIn("pins", stderr)
        self.assertEqual(self.pins_path.read_bytes(), existing)
        self.assertFalse(self.store.exists())
        acquisition.assert_not_called()

    def test_previous_pins_appends_versions_without_changing_existing_record(self):
        _, old_pins = self.prepare_replay()
        original = self.pins_path.read_bytes()
        new_pins_path = self.directory / "pins_v2.json"
        acquired_at = datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)
        with self.mock_acquisition(now=acquired_at):
            status, _, stderr = self.call(
                "macro",
                "acquire",
                self.plan_path,
                "--store",
                self.store,
                "--pins",
                new_pins_path,
                "--previous-pins",
                self.pins_path,
            )
        self.assertEqual(status, 0, stderr)
        self.assertEqual(self.pins_path.read_bytes(), original)
        new_pins = json.loads(new_pins_path.read_text(encoding="utf-8"))
        for source_id in old_pins["snapshots"]:
            self.assertEqual(new_pins["snapshots"][source_id][0], old_pins["snapshots"][source_id][0])
            self.assertEqual(len(new_pins["snapshots"][source_id]), 2)

    def test_replay_is_deterministic_without_http_dns_or_acquisition(self):
        self.prepare_replay()
        with patch(
            "investment_research.macro_pipeline.acquire_macro", side_effect=AssertionError("replay must not acquire")
        ):
            first = self.call(*self.replay_args())
            second = self.call(*self.replay_args())
        self.assertEqual(first[0], 0, first[2])
        self.assertEqual(first, second)
        self.assertIn("Macro Regime Snapshot", first[1])
        self.assertIn("한국 투자자", first[1])
        self.assertIn("관측", first[1])
        self.assertEqual(self.requests, [])

    def test_manifest_connects_report_metrics_raw_versions_and_existing_evidence(self):
        plan, pins = self.prepare_replay()
        output = self.directory / "snapshot.md"
        manifest_path = self.directory / "run.json"
        status, stdout, stderr = self.call(*self.replay_args(), "--output", output, "--manifest", manifest_path)
        self.assertEqual(status, 0, stderr)
        self.assertEqual(stdout, "")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        report = output.read_text(encoding="utf-8")
        run = replay_macro(plan, self.store, pins)
        self.assertEqual(manifest["kind"], "macro_regime_snapshot")
        self.assertEqual(manifest["snapshot_refs"], pins["snapshots"])
        self.assertEqual(manifest["report_sha256"], sha256(output.read_bytes()).hexdigest())
        self.assertEqual(manifest["input_sha256"], run.input_digest)
        self.assertRegex(manifest["code_sha256"], r"^[0-9a-f]{64}$")
        by_id = {item["id"]: item for item in manifest["observations"]}
        existing_evidence = set(manifest["evidence_ids"])
        for metric in manifest["metrics"]:
            for identifier in metric["input_observation_ids"]:
                observation = by_id[identifier]
                self.assertIn(observation["snapshot_id"], pins["snapshots"][observation["source_id"]])
                self.assertIn(identifier, existing_evidence)
            if metric["status"] == "available":
                self.assertIn(metric["id"], report.replace("\\_", "_"))
        for method in ("macro", "macro_pipeline", "source_acquisition"):
            self.assertTrue(manifest["method_versions"][method])

    def test_invalid_pins_never_produce_success_report(self):
        _, pins = self.prepare_replay()
        encoded = json.dumps(pins)
        inputs = (
            "{invalid JSON",
            encoded.replace(
                '"schema_version": "macro-pins-v1"',
                '"schema_version": "macro-pins-v1", "schema_version": "macro-pins-v1"',
                1,
            ),
            encoded.replace('"schema_version": "macro-pins-v1"', '"schema_version": NaN', 1),
        )
        for text in inputs:
            with self.subTest(text=text[:60]):
                self.pins_path.write_text(text, encoding="utf-8")
                output = self.directory / "snapshot.md"
                status, stdout, stderr = self.call(*self.replay_args(), "--output", output)
                self.assertEqual(status, 2)
                self.assertEqual(stdout, "")
                self.assertTrue(stderr)
                self.assertFalse(output.exists())

    def test_malformed_plan_and_unhashable_pin_entries_are_input_errors_without_traceback(self):
        for field in ("sources", "bindings"):
            with self.subTest(field=field):
                invalid = deepcopy(self.data)
                invalid[field] = [None]
                self.plan_path.write_text(json.dumps(invalid), encoding="utf-8")
                with patch(
                    "investment_research.macro_pipeline.acquire_macro",
                    side_effect=AssertionError("invalid plan must not GET"),
                ) as acquisition:
                    status, stdout, stderr = self.call(*self.acquire_args())
                self.assertEqual(status, 2)
                self.assertEqual(stdout, "")
                self.assertTrue(stderr)
                self.assertFalse(self.pins_path.exists())
                acquisition.assert_not_called()
        _, pins = self.prepare_replay()
        pins["snapshots"]["S_CPI"] = [{}]
        self.pins_path.write_text(json.dumps(pins), encoding="utf-8")
        status, stdout, stderr = self.call(*self.replay_args())
        self.assertEqual(status, 2)
        self.assertEqual(stdout, "")
        self.assertTrue(stderr)

    def test_as_of_requires_strict_date_or_timezone_aware_timestamp(self):
        self.prepare_replay()
        for text in ("20260910", "2026-W37-4", "2026-02-30", "2026-09-10T12:00:00", ""):
            with self.subTest(text=text):
                output = self.directory / "snapshot.md"
                status, stdout, stderr = self.call(*self.replay_args(), "--as-of", text, "--output", output)
                self.assertEqual(status, 2)
                self.assertEqual(stdout, "")
                self.assertTrue(stderr)
                self.assertFalse(output.exists())

    def test_as_of_aware_timestamp_is_one_instant_across_utc_and_korean_time(self):
        self.prepare_replay()
        korean_time = self.call(*self.replay_args(), "--as-of", "2026-09-10T21:00:00+09:00")
        utc_time = self.call(*self.replay_args(), "--as-of", "2026-09-10T12:00:00+00:00")
        self.assertEqual(korean_time[0], 0, korean_time[2])
        self.assertEqual(korean_time, utc_time)
        self.assertIn("2026-09-10T12:00:00+00:00", korean_time[1])
        self.assertIn("2026-09-10T21:00:00+09:00", korean_time[1])

    def test_output_paths_preserve_plan_pins_user_files_and_preflight_all_outputs(self):
        self.prepare_replay()
        user_file = self.directory / "user.md"
        user_file.write_text("사용자가 작성한 거시 연구", encoding="utf-8")
        for output in (self.plan_path, self.pins_path, user_file):
            with self.subTest(output=output.name):
                original = output.read_bytes()
                status, stdout, stderr = self.call(*self.replay_args(), "--output", output)
                self.assertEqual(status, 2)
                self.assertEqual(stdout, "")
                self.assertTrue(stderr)
                self.assertEqual(output.read_bytes(), original)
        fresh = self.directory / "fresh.md"
        status, stdout, stderr = self.call(*self.replay_args(), "--output", fresh, "--manifest", user_file)
        self.assertEqual(status, 2)
        self.assertFalse(fresh.exists())
        self.assertEqual(user_file.read_text(encoding="utf-8"), "사용자가 작성한 거시 연구")


if __name__ == "__main__":
    unittest.main()
