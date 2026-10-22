"""Synthetic HTTP responses exercise the real-source path without external access.

The policy sentence resembles a public announcement solely to exercise the
bounded parser. Every publisher, snapshot and review here is a test fixture;
these tests do not acquire or verify actual market facts.
"""

from copy import deepcopy
from dataclasses import asdict, replace
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from investment_research.engine import run_research
from investment_research.models import InterpretationStatus, VerificationStatus
from investment_research.report import render_report
from investment_research.source_pipeline import acquire_plan, load_source_plan, replay_plan
from investment_research.sources import FetchResponse, SourceError, SourceSpec, acquire

ACQUIRED_AT = datetime(2026, 10, 3, 4, 30, 1, tzinfo=timezone.utc)
CUT_QUOTE = (
    "The Committee decided to lower the target range for the federal funds "
    "rate by 1/2 percentage point to 4-3/4 to 5 percent."
)
NARRATIVE_QUOTE = "The cut was 50 basis points, so long bonds are now a guaranteed opportunity."
RATE_DEFINITION = {
    "measure": "policy_rate_cut",
    "unit": "basis_points",
    "period": "policy_decision",
    "currency": "USD",
    "adjustment": "unadjusted",
    "scope": "US synthetic policy decision on 2024-09-18",
}
NARRATIVE_DEFINITION = {
    "measure": "community_utterance",
    "unit": "text",
    "period": "public_discussion",
    "currency": None,
    "adjustment": "not_applicable",
    "scope": "one synthetic public discussion passage",
}
REVIEW = {
    "status": "reviewed",
    "reviewer": "synthetic-test-reviewer",
    "reviewed_at": "2026-10-03",
    "rationale": "합성 테스트의 좁은 정의와 원문 참조를 확인한 입력 기록이며 실제 사람의 시장 검토가 아니다.",
}


def make_spec(identifier, source_type, quote, definition):
    return SourceSpec(
        id=identifier,
        url=f"https://synthetic-pipeline.example.org/{identifier.lower()}",
        canonical_url=f"https://synthetic-pipeline.example.org/{identifier.lower()}",
        type=source_type,
        publisher="Synthetic pipeline test publisher",
        title="Synthetic test passage, never actual market evidence",
        published_at="2024-09-18",
        observed_at="2024-09-18",
        valid_as_of="2024-09-18",
        jurisdiction="US",
        topics=("synthetic-source-verification",),
        asset_ids=("CASH", "BOND", "EQUITY"),
        content_type="text/html",
        policy_url="https://synthetic-pipeline.example.org/terms",
        policy_note="Synthetic mock fixture: retain only its selected short passage.",
        retention="excerpt",
        max_age_days=10000,
        excerpts=(
            {
                "id": "Q_" + identifier,
                "quote": quote,
                "locator": "synthetic paragraph",
                "definition": deepcopy(definition),
            },
        ),
    )


def evidence(identifier, source, definition, *, kind="external_fact", extraction=None, view="macro"):
    return {
        "id": identifier,
        "source_id": source,
        "excerpt_id": "Q_" + source,
        "view": view,
        "kind": kind,
        "definition": deepcopy(definition),
        "extraction": extraction,
        "interpretation": deepcopy(REVIEW),
        "limitations": ["합성 HTTP 응답과 합성 검토 기록이며 실제 시장에 적용하지 않는다."],
    }


def claim(identifier="C_RATE", expected="50"):
    return {
        "id": identifier,
        "text": "합성 정책 결정 기록의 인하 폭이 명시한 값과 일치하는지 확인한다.",
        "asset_ids": ["CASH", "BOND", "EQUITY"],
        "rule": "numeric_equality_v1",
        "support_ids": ["E_CUT"],
        "counter_ids": [],
        "context_ids": [],
        "narrative_evidence_id": None,
        "review": deepcopy(REVIEW),
        "assertion": {
            "evidence_id": "E_CUT",
            "expected_value": expected,
            "unit": "basis_points",
            "period": "policy_decision",
            "currency": "USD",
            "measure": "policy_rate_cut",
            "scope": RATE_DEFINITION["scope"],
        },
        "limitations": ["합성 원문의 좁은 수치 일치 확인이며 투자 기회를 검증하지 않는다."],
        "recheck": "원문 또는 정책 결정의 정의가 달라지면 다시 대조한다.",
    }


class SourcePipelineTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.store = self.directory / "snapshots"
        primary = make_spec("S_POLICY", "primary", CUT_QUOTE, RATE_DEFINITION)
        community = make_spec("S_COMMUNITY", "community", NARRATIVE_QUOTE, NARRATIVE_DEFINITION)
        self.documents = {
            primary.url: (f"<html><body><p>{CUT_QUOTE}</p></body></html>".encode(), 200),
            community.url: (f"<html><body><p>{NARRATIVE_QUOTE}</p></body></html>".encode(), 200),
        }
        self.data = {
            "schema_version": "1",
            "id": "PLAN_SYNTHETIC_PUBLIC_SOURCE_PATH",
            "question": "합성 공개자료 응답의 인하 수치와 커뮤니티 발언을 좁은 범위에서 확인할 수 있는가?",
            "as_of": "2026-10-03",
            "sources": [asdict(primary), asdict(community)],
            "evidence": [
                evidence("E_CUT", "S_POLICY", RATE_DEFINITION, extraction="fed_rate_cut_v1"),
                evidence(
                    "E_COMMUNITY",
                    "S_COMMUNITY",
                    NARRATIVE_DEFINITION,
                    kind="observed_narrative",
                    view="community",
                    extraction="basis_points_statement_v1",
                ),
            ],
            "claims": [claim()],
        }

    def plan(self, data=None):
        path = self.directory / "plan.json"
        path.write_text(json.dumps(self.data if data is None else data, ensure_ascii=False), encoding="utf-8")
        return load_source_plan(path)

    def fetcher(self, url, timeout, max_bytes):
        if url.endswith("/robots.txt"):
            return FetchResponse(b"User-agent: *\nAllow: /\n", "text/plain", final_url=url)
        body, status = self.documents[url]
        return FetchResponse(body, "text/html; charset=utf-8", status=status, final_url=url)

    def acquire_and_replay(self, data=None):
        plan = self.plan(data)
        with patch(
            "investment_research.source_pipeline.acquire",
            side_effect=lambda spec, store: acquire(spec, store, fetcher=self.fetcher, now=ACQUIRED_AT),
        ):
            pins = acquire_plan(plan, self.store)
        return plan, pins, replay_plan(plan, self.store, pins)

    def test_narrow_policy_cut_uses_hand_checked_basis_point_conversion(self):
        _, _, case = self.acquire_and_replay()
        observed = next(e for e in case.evidence if e.id == "E_CUT")
        self.assertEqual(observed.value, Decimal("50"))  # 1/2 percentage point = 50 bp.
        self.assertEqual(observed.unit, "basis_points")
        self.assertEqual(observed.period, "policy_decision")
        self.assertEqual(case.claims[0].verification, VerificationStatus.SUPPORTED)
        self.assertFalse(case.synthetic)
        self.assertTrue(case.source_verification)

    def test_numeric_mismatch_is_counter_evidence_without_rewriting_observation(self):
        data = deepcopy(self.data)
        data["claims"] = [claim("C_MATCH", "50"), claim("C_MISMATCH", "25")]
        _, _, case = self.acquire_and_replay(data)
        by_id = {c.id: c for c in case.claims}
        self.assertEqual(by_id["C_MATCH"].verification, VerificationStatus.SUPPORTED)
        self.assertEqual(by_id["C_MISMATCH"].verification, VerificationStatus.CONTRADICTED)
        self.assertIn("E_CUT", by_id["C_MISMATCH"].counter_ids)
        self.assertEqual(next(e for e in case.evidence if e.id == "E_CUT").value, Decimal("50"))

    def test_occurrence_and_numeric_extraction_do_not_supply_interpretation_review(self):
        data = deepcopy(self.data)
        del data["evidence"][0]["interpretation"]
        _, _, case = self.acquire_and_replay(data)
        observed = next(e for e in case.evidence if e.id == "E_CUT")
        self.assertEqual(observed.verification, VerificationStatus.SUPPORTED)
        self.assertEqual(observed.interpretation.status, InterpretationStatus.PENDING)
        self.assertEqual(case.claims[0].verification, VerificationStatus.UNVERIFIED)

    def test_community_compound_claim_preserves_partial_review_and_separate_context(self):
        data = deepcopy(self.data)
        data["claims"] = [
            {
                **claim("C_NARRATIVE"),
                "text": "인하 수치는 확인되지만 장기채 기회가 확실하다는 합성 발언까지 확인되지는 않는다.",
                "rule": "reviewed_links_v1",
                "verification": "partially_supported",
                "support_ids": ["E_CUT"],
                "context_ids": ["E_CUT"],
                "narrative_evidence_id": "E_COMMUNITY",
            }
        ]
        del data["claims"][0]["assertion"]
        _, _, case = self.acquire_and_replay(data)
        narrative = next(e for e in case.evidence if e.id == "E_COMMUNITY")
        self.assertEqual(narrative.verification, VerificationStatus.SUPPORTED)
        self.assertIsNone(narrative.value)
        self.assertEqual(case.claims[0].verification, VerificationStatus.PARTIAL)
        self.assertEqual(case.claims[0].context_ids, ("E_CUT",))
        report = render_report(run_research(case)).replace("\\_", "_")
        self.assertIn("배경 자료", report)
        self.assertIn("발언의 존재와 발언 내용의 진실성은 다르다", report)
        self.assertIn("일부 확인", report)

    def test_community_only_cannot_verify_its_financial_content(self):
        data = deepcopy(self.data)
        data["claims"] = [
            {
                **claim("C_ONLY_COMMUNITY"),
                "rule": "reviewed_links_v1",
                "verification": "supported_within_scope",
                "support_ids": ["E_COMMUNITY"],
                "narrative_evidence_id": "E_COMMUNITY",
            }
        ]
        del data["claims"][0]["assertion"]
        _, _, case = self.acquire_and_replay(data)
        self.assertEqual(case.claims[0].verification, VerificationStatus.UNVERIFIED)
        self.assertEqual(
            next(e for e in case.evidence if e.id == "E_COMMUNITY").verification, VerificationStatus.SUPPORTED
        )
        self.assertTrue(all("E_COMMUNITY" not in a.support_ids for a in run_research(case).assessments))

    def test_stale_historical_fact_remains_confirmed_but_current_adoption_is_withheld(self):
        data = deepcopy(self.data)
        data["sources"][0]["max_age_days"] = 30
        _, _, case = self.acquire_and_replay(data)
        observed = next(e for e in case.evidence if e.id == "E_CUT")
        self.assertEqual(observed.provenance.freshness, "stale")
        self.assertEqual(case.claims[0].verification, VerificationStatus.SUPPORTED)
        report = render_report(run_research(case))
        self.assertIn("stale", report)
        self.assertIn("과거 사실 확인과 현재 적용은 별도", report)
        self.assertIn("투자 매력·개인 배분 판단: 미실시", report)

    def test_unknown_dates_are_not_replaced_with_retrieval_and_do_not_confirm_freshness(self):
        data = deepcopy(self.data)
        for field in ("published_at", "observed_at", "valid_as_of"):
            data["sources"][0][field] = None
        _, _, case = self.acquire_and_replay(data)
        observed = next(e for e in case.evidence if e.id == "E_CUT")
        self.assertEqual(observed.provenance.freshness, "unknown")
        self.assertEqual(case.claims[0].verification, VerificationStatus.SUPPORTED)
        report = render_report(run_research(case))
        self.assertIn("UNKNOWN (발행일 미확인)", report)
        self.assertIn("2026-10-03T04:30:01Z", report)
        self.assertIn("획득 시각은 발행일", report)

    def test_future_source_does_not_become_a_known_fact_at_earlier_cutoff(self):
        data = deepcopy(self.data)
        data["sources"][0]["published_at"] = "2026-10-04"
        _, _, case = self.acquire_and_replay(data)
        observed = next(e for e in case.evidence if e.id == "E_CUT")
        self.assertEqual(observed.provenance.freshness, "future")
        self.assertEqual(case.claims[0].verification, VerificationStatus.UNVERIFIED)
        self.assertIn("future", render_report(run_research(case)))

    def test_evidence_review_dates_cannot_predate_acquisition_or_observation(self):
        for status in ("reviewed", "pending"):
            for prerequisite in ("acquisition", "observation"):
                with self.subTest(status=status, prerequisite=prerequisite):
                    data = deepcopy(self.data)
                    review = data["evidence"][0]["interpretation"]
                    review["status"] = status
                    if prerequisite == "acquisition":
                        review["reviewed_at"] = "2026-10-02"
                    else:
                        data["sources"][0]["observed_at"] = "2026-10-04"
                    with self.assertRaisesRegex(SourceError, "review date"):
                        self.acquire_and_replay(data)

    def test_claim_review_date_covers_context_narrative_and_assertion_references(self):
        for reference in ("context", "narrative", "assertion"):
            with self.subTest(reference=reference):
                data = deepcopy(self.data)
                item = data["claims"][0]
                item["review"]["reviewed_at"] = "2026-10-02"
                item["support_ids"] = []
                item["counter_ids"] = []
                if reference in ("context", "narrative"):
                    item["rule"] = "reviewed_links_v1"
                    item["verification"] = "unverified"
                    del item["assertion"]
                    if reference == "context":
                        item["context_ids"] = ["E_CUT"]
                    else:
                        item["narrative_evidence_id"] = "E_COMMUNITY"
                with self.assertRaisesRegex(SourceError, "review date"):
                    self.acquire_and_replay(data)

    def test_unknown_publication_does_not_hide_future_valid_as_of(self):
        data = deepcopy(self.data)
        data["sources"][0]["published_at"] = None
        data["sources"][0]["valid_as_of"] = "2026-10-04"
        _, _, case = self.acquire_and_replay(data)
        primary = next(source for source in case.sources if source.id == "S_POLICY")
        observed = next(item for item in case.evidence if item.id == "E_CUT")
        self.assertIsNone(primary.published_at)
        self.assertEqual(primary.provenance.freshness, "future")
        self.assertEqual(observed.provenance.freshness, "future")
        self.assertEqual(case.claims[0].verification, VerificationStatus.UNVERIFIED)

    def test_adjustment_mismatch_leaves_claim_unverified_without_rewriting_value(self):
        data = deepcopy(self.data)
        data["claims"][0]["assertion"]["adjustment"] = "seasonally_adjusted"
        _, _, case = self.acquire_and_replay(data)
        observed = next(item for item in case.evidence if item.id == "E_CUT")
        self.assertEqual(observed.value, Decimal("50"))
        self.assertEqual(observed.provenance.definition["adjustment"], "unadjusted")
        self.assertEqual(case.claims[0].verification, VerificationStatus.UNVERIFIED)
        self.assertEqual(case.claims[0].counter_ids, ())

    def test_scalar_assertion_and_narrative_references_cannot_escape_asset_scope(self):
        for reference in ("assertion", "narrative"):
            with self.subTest(reference=reference):
                data = deepcopy(self.data)
                if reference == "assertion":
                    data["sources"][0]["asset_ids"] = ["CASH"]
                    data["claims"][0]["support_ids"] = []
                else:
                    data["sources"][1]["asset_ids"] = ["CASH"]
                    data["claims"][0]["narrative_evidence_id"] = "E_COMMUNITY"
                with self.assertRaisesRegex(SourceError, "asset scope"):
                    self.plan(data)

    def test_unavailable_or_changed_source_does_not_create_fact_evidence(self):
        primary_url = self.data["sources"][0]["url"]
        for body, status in ((b"temporary unavailable", 503), (b"<p>Changed synthetic document.</p>", 200)):
            with self.subTest(http_status=status):
                self.documents[primary_url] = (body, status)
                _, _, case = self.acquire_and_replay()
                self.assertNotIn("E_CUT", {e.id for e in case.evidence})
                self.assertEqual(case.claims[0].verification, VerificationStatus.UNVERIFIED)
                self.assertTrue(case.diagnostics)
                report = render_report(run_research(case))
                self.assertRegex(report, "unavailable|changed|변경|확보")

    def test_incompatible_definition_does_not_turn_mismatch_into_false_claim(self):
        for field, value in (("unit", "percent"), ("period", "monthly_average"), ("scope", "another policy decision")):
            with self.subTest(field=field):
                data = deepcopy(self.data)
                data["claims"][0]["assertion"][field] = value
                _, _, case = self.acquire_and_replay(data)
                self.assertEqual(case.claims[0].verification, VerificationStatus.UNVERIFIED)
                self.assertTrue(case.claims[0].limitations)

    def test_strict_plan_contract_rejects_unknown_fields_and_missing_definitions(self):
        malformed = []
        data = deepcopy(self.data)
        data["unexpected"] = "ignored configuration would be unsafe"
        malformed.append(data)
        data = deepcopy(self.data)
        del data["evidence"][0]["definition"]["scope"]
        malformed.append(data)
        data = deepcopy(self.data)
        data["claims"][0]["assertion"]["expected_value"] = 50.0
        malformed.append(data)
        for data in malformed:
            with self.subTest(data=data):
                with self.assertRaises(SourceError):
                    self.plan(data)

    def test_evidence_definition_cannot_override_snapshot_definition(self):
        data = deepcopy(self.data)
        data["evidence"][0]["definition"]["scope"] = "a different synthetic decision"
        with self.assertRaises(SourceError):
            self.plan(data)

    def test_pins_reject_plan_or_source_metadata_changes(self):
        plan, pins, _ = self.acquire_and_replay()
        bad_plan = replace(plan, id="ANOTHER_PLAN")
        bad_spec = replace(plan.sources[0], title="Different synthetic source metadata")
        modified_sources = replace(plan, sources=(bad_spec, *plan.sources[1:]))
        for changed in (bad_plan, modified_sources):
            with self.subTest(plan=changed.id):
                with self.assertRaises(SourceError):
                    replay_plan(changed, self.store, pins)
        corrupted = deepcopy(pins)
        corrupted["sources_digest"] = "0" * 64
        with self.assertRaises(SourceError):
            replay_plan(plan, self.store, corrupted)

    def test_local_replay_is_identical_without_fetching_and_report_anchors_resolve(self):
        plan, pins, first = self.acquire_and_replay()
        with (
            patch(
                "investment_research.source_pipeline.acquire",
                side_effect=AssertionError("replay attempted acquisition"),
            ),
            patch("investment_research.sources._fetch_http", side_effect=AssertionError("replay attempted HTTP")),
            patch("socket.socket.connect", side_effect=AssertionError("replay attempted socket")),
        ):
            second = replay_plan(plan, self.store, pins)
        self.assertEqual(first, second)
        left = render_report(run_research(first))
        right = render_report(run_research(second))
        self.assertEqual(left.encode(), right.encode())
        targets = re.findall(r"\]\(#([^\)]+)\)", left)
        self.assertTrue(targets)
        for target in targets:
            self.assertIn(f'id="{target}"', left)
        self.assertIn("과거 자료", left)
        self.assertNotIn("(mixed)", left)


if __name__ == "__main__":
    unittest.main()
