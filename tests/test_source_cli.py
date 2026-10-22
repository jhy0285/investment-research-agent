"""Public-source CLI behavior with synthetic HTTP and pinned local snapshots.

The fixture describes the source pipeline, not an actual market observation.
Live requests are forbidden throughout this suite, including replay commands.
"""

from contextlib import redirect_stderr, redirect_stdout
from dataclasses import asdict
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from investment_research.__main__ import main
from investment_research.source_pipeline import acquire_plan, load_source_plan, replay_plan
from investment_research.sources import FetchResponse, acquire, load_snapshot
from tests.test_source_pipeline import ACQUIRED_AT, CUT_QUOTE, RATE_DEFINITION, claim, evidence, make_spec


class SourceCLITests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.store = self.directory / "snapshots"
        self.pins_path = self.directory / "pins.json"
        self.plan_path = self.directory / "plan.json"
        source = make_spec("S_POLICY", "primary", CUT_QUOTE, RATE_DEFINITION)
        self.data = {
            "schema_version": "1",
            "id": "PLAN_SYNTHETIC_SOURCE_CLI",
            "question": "합성 source CLI의 원문·주장 연결을 재현할 수 있는가?",
            "as_of": "2026-10-03",
            "sources": [asdict(source)],
            "evidence": [evidence("E_CUT", source.id, RATE_DEFINITION, extraction="fed_rate_cut_v1")],
            "claims": [claim()],
        }
        self.plan_path.write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")
        self.document = FetchResponse(f"<p>{CUT_QUOTE}</p>".encode(), "text/html; charset=utf-8")
        self.requests = []
        for target in ("socket.socket.connect", "investment_research.sources._fetch_http"):
            blocker = patch(target, side_effect=AssertionError("external network forbidden in CLI tests"))
            blocker.start()
            self.addCleanup(blocker.stop)

    def fetcher(self, url, timeout, max_bytes):
        self.requests.append(url)
        if url.endswith("/robots.txt"):
            return FetchResponse(b"User-agent: *\nAllow: /\n", "text/plain")
        self.assertEqual(url, self.data["sources"][0]["url"])
        return self.document

    def mock_acquisition(self):
        return patch(
            "investment_research.source_pipeline.acquire",
            side_effect=lambda source, store: acquire(source, store, fetcher=self.fetcher, now=ACQUIRED_AT),
        )

    def call(self, *arguments):
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(map(str, arguments)))
        return code, stdout.getvalue(), stderr.getvalue()

    def acquire_arguments(self):
        return ("sources", "acquire", self.plan_path, "--store", self.store, "--pins", self.pins_path)

    def prepare_replay(self):
        with self.mock_acquisition():
            pins = acquire_plan(load_source_plan(self.plan_path), self.store)
        self.pins_path.write_text(json.dumps(pins, ensure_ascii=False), encoding="utf-8")
        self.requests.clear()
        return pins

    def replay_arguments(self):
        return ("sources", "replay", self.plan_path, "--store", self.store, "--pins", self.pins_path)

    def test_acquire_available_sources_writes_pins_and_reports_successful_status(self):
        with self.mock_acquisition():
            code, stdout, stderr = self.call(*self.acquire_arguments())
        self.assertEqual(code, 0, stderr)
        self.assertEqual(stderr, "")
        self.assertIn("S_POLICY: available", stdout)
        pins = json.loads(self.pins_path.read_text(encoding="utf-8"))
        self.assertEqual(pins["plan_id"], self.data["id"])
        snapshot = load_snapshot(self.store, "S_POLICY", pins["snapshots"]["S_POLICY"])
        self.assertEqual(snapshot.status, "available")
        self.assertEqual(snapshot.payload["excerpts"][0]["quote"], CUT_QUOTE)
        self.assertEqual(len(self.requests), 2)

    def test_acquire_failed_source_writes_diagnostic_pins_and_exits_one(self):
        self.document = FetchResponse(b"Synthetic temporary unavailable", "text/html", status=503)
        with self.mock_acquisition():
            code, stdout, _ = self.call(*self.acquire_arguments())
        self.assertEqual(code, 1)
        self.assertIn("S_POLICY: unavailable", stdout)
        self.assertNotIn("S_POLICY: available", stdout)
        pins = json.loads(self.pins_path.read_text(encoding="utf-8"))
        snapshot = load_snapshot(self.store, "S_POLICY", pins["snapshots"]["S_POLICY"])
        self.assertEqual(snapshot.status, "unavailable")
        self.assertEqual(snapshot.payload["excerpts"], [])

    def test_acquire_preserves_existing_pins_before_any_get(self):
        existing = b"User-owned acquisition record\n"
        self.pins_path.write_bytes(existing)
        with patch(
            "investment_research.source_pipeline.acquire_plan", side_effect=AssertionError("must refuse before GET")
        ) as fetch:
            code, stdout, stderr = self.call(*self.acquire_arguments())
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("pins", stderr)
        self.assertEqual(self.pins_path.read_bytes(), existing)
        fetch.assert_not_called()
        self.assertFalse(self.store.exists())

    def test_replay_repeats_without_network_and_writes_traceable_manifest(self):
        pins = self.prepare_replay()
        with patch(
            "investment_research.source_pipeline.acquire_plan", side_effect=AssertionError("replay must not acquire")
        ):
            first = self.call(*self.replay_arguments())
            second = self.call(*self.replay_arguments())
        self.assertEqual(first[0], 0, first[2])
        self.assertEqual(first, second)
        self.assertIn("출처 검증 브리프", first[1])
        self.assertIn("투자 매력·개인 배분 판단: 미실시", first[1])
        self.assertEqual(self.requests, [])
        output = self.directory / "brief.md"
        manifest_path = self.directory / "run.json"
        code, stdout, stderr = self.call(*self.replay_arguments(), "--output", output, "--manifest", manifest_path)
        self.assertEqual(code, 0, stderr)
        self.assertEqual(stdout, "")
        self.assertEqual(output.read_text(encoding="utf-8"), first[1])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        case = replay_plan(load_source_plan(self.plan_path), self.store, pins)
        self.assertFalse(manifest["synthetic"])
        self.assertEqual(manifest["input_sha256"], case.input_digest)
        self.assertEqual(manifest["report_sha256"], sha256(output.read_bytes()).hexdigest())
        self.assertRegex(manifest["code_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(manifest["source_snapshots"]["S_POLICY"]["snapshot_id"], pins["snapshots"]["S_POLICY"])
        self.assertEqual(manifest["source_snapshots"]["S_POLICY"]["status"], "available")
        for method in ("source_acquisition", "source_pipeline"):
            self.assertTrue(manifest["method_versions"][method])

    def test_invalid_pins_json_is_blocked_and_never_produces_a_report(self):
        pins = self.prepare_replay()
        serialized = json.dumps(pins)
        inputs = (
            b"{not valid JSON",
            serialized.replace('"schema_version": "1"', '"schema_version": "1", "schema_version": "1"', 1).encode(),
            serialized.replace('"schema_version": "1"', '"schema_version": NaN', 1).encode(),
            b"\xff",
        )
        for raw in inputs:
            with self.subTest(raw=raw[:60]):
                self.pins_path.write_bytes(raw)
                output = self.directory / "brief.md"
                code, stdout, stderr = self.call(*self.replay_arguments(), "--output", output)
                self.assertEqual(code, 2)
                self.assertEqual(stdout, "")
                self.assertTrue(stderr)
                self.assertFalse(output.exists())

    def test_as_of_uses_strict_calendar_iso_dates_before_writing(self):
        self.prepare_replay()
        for value in ("20261003", "2026-W40-6", "2026-02-30", ""):
            with self.subTest(value=value):
                output = self.directory / "brief.md"
                code, stdout, stderr = self.call(*self.replay_arguments(), "--as-of", value, "--output", output)
                self.assertEqual(code, 2)
                self.assertEqual(stdout, "")
                self.assertIn("as_of", stderr)
                self.assertFalse(output.exists())

    def test_replay_preserves_plan_pins_and_user_output_files(self):
        self.prepare_replay()
        user_output = self.directory / "user.md"
        user_output.write_text("사용자 기존 연구", encoding="utf-8")
        for output in (self.plan_path, self.pins_path, user_output):
            with self.subTest(output=output.name):
                original = output.read_bytes()
                code, stdout, stderr = self.call(*self.replay_arguments(), "--output", output)
                self.assertEqual(code, 2)
                self.assertEqual(stdout, "")
                self.assertTrue(stderr)
                self.assertEqual(output.read_bytes(), original)

    def test_corrupted_pinned_source_is_an_input_error_without_success_report(self):
        pins = self.prepare_replay()
        snapshot_path = self.store / "S_POLICY" / (pins["snapshots"]["S_POLICY"] + ".json")
        data = json.loads(snapshot_path.read_text(encoding="utf-8"))
        data["payload"]["excerpts"][0]["quote"] = "tampered synthetic passage"
        snapshot_path.write_text(json.dumps(data), encoding="utf-8")
        output = self.directory / "brief.md"
        code, stdout, stderr = self.call(*self.replay_arguments(), "--output", output)
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("checksum", stderr)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
