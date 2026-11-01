"""Synthetic opportunity-map boundaries; no actual market facts or live access.

All values, quotations, source metadata, interpretations and user profiles below
are authored fixtures. They exercise pinned evidence, not investment advice.
"""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from investment_research.macro_pipeline import acquire_macro, load_macro_plan
from investment_research.models import InterpretationStatus, VerificationStatus
from investment_research.opportunity import load_opportunity_review, opportunity_manifest, replay_opportunity
from investment_research.opportunity_report import render_opportunity_report
from investment_research.source_pipeline import _digest, load_source_plan, replay_plan
from investment_research.sources import FetchResponse, SourceError, SourceSpec, acquire
from tests import test_macro_pipeline as macro_fixture

ACQUIRED = macro_fixture.ACQUIRED_AT
CUTOFF = ACQUIRED + timedelta(minutes=30)
ASSETS = (
    "CASH",
    "SHORT_BOND",
    "LONG_BOND",
    "US_EQUITY",
    "KR_EQUITY",
    "GLOBAL_ETF",
    "GROWTH",
    "VALUE",
    "DIVIDEND",
    "CREDIT",
    "GOLD",
    "COMMODITY",
    "ENERGY",
    "CRYPTO",
    "KR_REAL_ESTATE",
)
PRIMARY_QUOTE = "The synthetic Committee decided to lower its target range by 3/4 percentage point."
COMMUNITY_QUOTE = "Synthetic participants say gold is guaranteed to rise after a 75 basis points cut."
DEFINITION = {
    "measure": "policy_rate_cut",
    "unit": "basis_points",
    "period": "policy_decision",
    "currency": "USD",
    "adjustment": "unadjusted",
    "scope": "one synthetic policy decision",
}
NARRATIVE_DEFINITION = {
    "measure": "public_statement",
    "unit": "text",
    "period": "public_discussion",
    "currency": None,
    "adjustment": "not_applicable",
    "scope": "one synthetic public utterance",
}
REVIEWED = {
    "status": "reviewed",
    "reviewer": "synthetic fixture reviewer",
    "reviewed_at": "2026-09-10",
    "rationale": "합성 원문의 좁은 정의를 확인한 테스트 입력이며 실제 투자 검토가 아니다.",
}


def statement(text="합성 원문을 다음 조사 질문의 출발점으로 검토한다.", refs=("E_PRIMARY",), alternatives=None):
    result = {"text": text, "evidence_ids": list(refs)}
    if alternatives is not None:
        result["alternative_ids"] = list(alternatives)
    return result


def synthetic_source_data():
    specifications = []
    items = []
    for identifier, source_type, quote, definition in (
        ("S_PRIMARY", "primary", PRIMARY_QUOTE, DEFINITION),
        ("S_COMMUNITY", "community", COMMUNITY_QUOTE, NARRATIVE_DEFINITION),
    ):
        url = "https://synthetic-opportunity.example.org/" + identifier.lower()
        specifications.append(
            asdict(
                SourceSpec(
                    id=identifier,
                    url=url,
                    canonical_url=url,
                    type=source_type,
                    publisher="Synthetic opportunity fixture publisher",
                    title="Synthetic passage; never actual market evidence",
                    published_at="2026-09-10T11:00:00Z",
                    observed_at="2026-09-10T11:00:00Z",
                    valid_as_of="2026-09-10",
                    jurisdiction="US",
                    topics=("synthetic-opportunity-test",),
                    asset_ids=ASSETS,
                    content_type="text/html",
                    access_method="public_http",
                    policy_url="https://synthetic-opportunity.example.org/terms",
                    policy_note="Authored synthetic test passages; no external content or personal information.",
                    retention="excerpt",
                    max_age_days=5,
                    excerpts=(
                        {
                            "id": "Q_" + identifier,
                            "quote": quote,
                            "locator": "synthetic fixture paragraph",
                            "definition": deepcopy(definition),
                        },
                    ),
                )
            )
        )
        items.append(
            {
                "id": "E_PRIMARY" if source_type == "primary" else "E_COMMUNITY",
                "source_id": identifier,
                "excerpt_id": "Q_" + identifier,
                "view": "macro" if source_type == "primary" else "community",
                "kind": "external_fact" if source_type == "primary" else "observed_narrative",
                "definition": deepcopy(definition),
                "extraction": "fed_rate_cut_v1" if source_type == "primary" else None,
                "interpretation": None,
                "limitations": ["합성 테스트 입력이며 실제 시장에 적용하지 않는다."],
            }
        )
    return {
        "schema_version": "1",
        "id": "PLAN_SYNTHETIC_OPPORTUNITY",
        "question": "합성 원문을 범위가 명시된 조사 질문으로 연결할 수 있는가?",
        "as_of": "2026-09-10",
        "asset_ids": list(ASSETS),
        "sources": specifications,
        "evidence": items,
        "claims": [],
    }


def synthetic_review_data():
    rows = []
    for index, asset in enumerate(ASSETS):
        candidate = None
        if asset in {"CASH", "SHORT_BOND"}:
            candidate = {name: statement() for name in ("why_now", "changed", "interesting", "counterargument")}
            candidate["confirm"] = ["다른 공식 자료와 상품 조건이 같은 설명을 지지하는지 확인한다."]
        rows.append(
            {
                "asset_id": asset,
                "name": "합성 " + asset,
                "exposure": "합성 경제적 노출",
                "return_definition": "미래 수익을 산출하지 않는 조사 범위",
                "liquidity": "실제 상품별 유동성은 미확인",
                "state": statement(),
                "positive": statement(),
                "negative": statement(),
                "uncertainty": ["추가 원자료와 경제적 의미 검토가 필요하다."],
                "opportunity_cost": statement(alternatives=(ASSETS[(index + 1) % len(ASSETS)],)),
                "priority": "candidate" if candidate else "monitor",
                "priority_reason": statement(),
                "recheck": statement(),
                "candidate": candidate,
            }
        )
    sections = {
        name: [statement()]
        for name in (
            "overview",
            "drivers",
            "market_narratives",
            "community",
            "gaps",
            "korean_context",
        )
    }
    sections["community"] = [statement("합성 공개 발언에서 조사 가설만 관측했다.", ("E_COMMUNITY",))]
    sections["unknowns"] = ["보유자산과 부채 및 실제 손실 감당 능력은 미확인이다."]
    sections["easy"] = [
        "이는 실제 시장을 설명하지 않는 합성 조사 지도다.",
        "확인되지 않은 경제적 의미를 투자 매력으로 확정하지 않는다.",
    ]
    return {
        "schema_version": "opportunity-review-v1",
        "id": "SYNTHETIC_OPPORTUNITY_REVIEW",
        "question": "명시된 합성 대안 중 무엇을 더 조사해야 하는가?",
        "as_of": CUTOFF.isoformat(),
        "author": "합성 테스트 작성자",
        "review_status": "draft",
        "horizon": "기간 미확인",
        "profile": {
            "base_currency": {"status": "known", "value": "KRW"},
            "birth_year": {"status": "self_reported", "value": 1998},
            "debt": {"status": "unknown", "value": None},
            "risk_capacity": {"status": "unknown", "value": None},
            "portfolio_allocation": {"status": "unknown", "value": None},
        },
        "comparison_limits": ["금리와 과거 가격 변화를 동일한 미래 수익률로 순위화하지 않는다."],
        "rows": rows,
        "sections": sections,
        "next_research": {
            "asset_id": "CASH",
            "title": "합성 현금 조건 확인",
            "question": "실제 조건을 추가로 확인할 수 있는가?",
        },
        "sampling_limits": ["합성 자료만 사용하며 전체 시장 대표성이 없다."],
        "access_notes": ["외부 사이트 접근 없이 직접 작성한 fixture만 재생한다."],
    }


class OpportunityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.source_store = self.directory / "source_snapshots"
        self.macro_store = self.directory / "macro_snapshots"
        self.source_path = self.directory / "source_plan.json"
        self.macro_path = self.directory / "macro_plan.json"
        self.review_path = self.directory / "review.json"
        self.source_data = synthetic_source_data()
        self.review_data = synthetic_review_data()
        self.macro_data = macro_fixture.synthetic_plan_data()
        self.documents = {
            "https://synthetic-opportunity.example.org/s_primary": FetchResponse(
                ("<p>" + PRIMARY_QUOTE + "</p>").encode(), "text/html"
            ),
            "https://synthetic-opportunity.example.org/s_community": FetchResponse(
                ("<p>" + COMMUNITY_QUOTE + "</p>").encode(), "text/html"
            ),
            self.macro_data["sources"][0]["url"]: FetchResponse(macro_fixture.cpi_document(), "application/json"),
            self.macro_data["sources"][1]["url"]: FetchResponse(
                macro_fixture.fed_csv(
                    (macro_fixture.TWO_FIELD, macro_fixture.TEN_FIELD),
                    (
                        ("2026-09-01", "1.50", "3.00"),
                        ("2026-09-02", "2.00", "3.50"),
                    ),
                ),
                "text/csv",
            ),
            self.macro_data["sources"][2]["url"]: FetchResponse(
                macro_fixture.fed_csv(
                    (macro_fixture.FX_FIELD,),
                    (
                        ("2026-09-01", "1300"),
                        ("2026-09-02", "1310"),
                    ),
                    identifier_prefix="H10/H10/",
                ),
                "text/csv",
            ),
        }
        self.requests = []
        for target in ("socket.socket.connect", "socket.getaddrinfo", "investment_research.sources._fetch_http"):
            blocker = patch(
                target, side_effect=AssertionError("external HTTP/DNS forbidden in synthetic opportunity tests")
            )
            blocker.start()
            self.addCleanup(blocker.stop)
        self.macro_path.write_text(json.dumps(self.macro_data), encoding="utf-8")
        self.macro_plan = load_macro_plan(self.macro_path)
        self.macro_pins = acquire_macro(self.macro_plan, self.macro_store, fetcher=self.fetcher, now=ACQUIRED)
        self.requests.clear()

    def fetcher(self, url, timeout, max_bytes):
        self.requests.append(url)
        if url.endswith("/robots.txt"):
            return FetchResponse(b"User-agent: *\nAllow: /\n", "text/plain", final_url=url)
        response = self.documents[url]
        if isinstance(response, Exception):
            raise response
        return response

    def source_plan(self, data=None):
        self.source_path.write_text(json.dumps(self.source_data if data is None else data), encoding="utf-8")
        return load_source_plan(self.source_path)

    def review(self, data=None):
        self.review_path.write_text(
            json.dumps(self.review_data if data is None else data, ensure_ascii=False), encoding="utf-8"
        )
        return load_opportunity_review(self.review_path)

    def prepare(self, data=None, *, now=ACQUIRED):
        plan = self.source_plan(data)
        pins = {
            "schema_version": "1",
            "plan_id": plan.id,
            "sources_digest": _digest([asdict(spec) for spec in plan.sources]),
            "snapshots": {
                spec.id: acquire(spec, self.source_store, fetcher=self.fetcher, now=now).snapshot_id
                for spec in plan.sources
            },
        }
        self.requests.clear()
        return plan, pins

    def replay(self, source_data=None, review_data=None, *, now=ACQUIRED):
        plan, pins = self.prepare(source_data, now=now)
        return replay_opportunity(
            self.review(review_data), plan, self.source_store, pins, self.macro_plan, self.macro_store, self.macro_pins
        )

    @staticmethod
    def row(run, asset="CASH"):
        return next(row for row in run.rows if row["asset_id"] == asset)

    def test_source_plan_explicit_alternatives_support_fifteen_scopes_without_changing_legacy_default(self):
        self.assertEqual(self.source_plan().asset_ids, ASSETS)
        legacy = deepcopy(self.source_data)
        legacy.pop("asset_ids")
        for spec in legacy["sources"]:
            spec["asset_ids"] = ["CASH", "BOND", "EQUITY"]
        self.assertEqual(self.source_plan(legacy).asset_ids, ("CASH", "BOND", "EQUITY"))
        legacy["sources"][0]["asset_ids"] = ["GOLD"]
        with self.assertRaises(SourceError):
            self.source_plan(legacy)

    def test_custom_scope_rejects_outside_source_and_claim_references(self):
        data = deepcopy(self.source_data)
        data["sources"][0]["asset_ids"] = [*data["sources"][0]["asset_ids"], "UNDECLARED"]
        with self.assertRaises(SourceError):
            self.source_plan(data)
        data = deepcopy(self.source_data)
        data["claims"] = [
            {
                "id": "C_BAD",
                "text": "합성 범위 밖 주장",
                "asset_ids": ["UNDECLARED"],
                "rule": "reviewed_links_v1",
                "support_ids": ["E_PRIMARY"],
                "counter_ids": [],
                "context_ids": [],
                "narrative_evidence_id": None,
                "review": REVIEWED,
                "verification": "supported_within_scope",
            }
        ]
        with self.assertRaises(SourceError):
            self.source_plan(data)

    def test_pending_matched_primary_passage_motivates_draft_question_but_not_verified_attractiveness(self):
        run = self.replay()
        row = self.row(run)
        self.assertEqual(row["priority"], "candidate")
        self.assertEqual(row["_review_status"], "draft")
        self.assertIn("pending", " ".join(row["priority_reason"]["_warnings"]))
        evidence = next(item for item in run.case.evidence if item.id == "E_PRIMARY")
        self.assertEqual(evidence.value, 75)
        self.assertEqual(evidence.interpretation.status, InterpretationStatus.PENDING)
        self.assertEqual(run.result.conclusion, "insufficient_evidence")
        for claim in run.case.claims:
            if claim.id.startswith("OPPORTUNITY_DRAFT_"):
                self.assertEqual(claim.verification, VerificationStatus.UNVERIFIED)
                self.assertEqual(claim.interpretation.status, InterpretationStatus.PENDING)
        self.assertEqual(self.requests, [])

    def test_community_only_candidate_is_downgraded_and_utterance_never_becomes_numeric_fact(self):
        data = deepcopy(self.review_data)
        row = data["rows"][0]
        row["priority_reason"]["evidence_ids"] = ["E_COMMUNITY"]
        run = self.replay(review_data=data)
        self.assertEqual(self.row(run)["priority"], "insufficient")
        self.assertEqual(self.row(run)["_requested_priority"], "candidate")
        self.assertEqual(self.row(run)["priority_reason"]["_available_ids"], [])
        evidence = next(item for item in run.case.evidence if item.id == "E_COMMUNITY")
        self.assertIsNone(evidence.value)
        self.assertIsNone(evidence.unit)

    def test_even_reviewed_narrative_content_cannot_be_promoted_by_source_claim(self):
        data = deepcopy(self.source_data)
        data["evidence"][1]["interpretation"] = REVIEWED
        data["claims"] = [
            {
                "id": "C_NARRATIVE",
                "text": "합성 커뮤니티의 보장 주장을 확인하려는 입력",
                "asset_ids": ["GOLD"],
                "rule": "reviewed_links_v1",
                "support_ids": ["E_COMMUNITY"],
                "counter_ids": [],
                "context_ids": [],
                "narrative_evidence_id": "E_COMMUNITY",
                "review": REVIEWED,
                "verification": "supported_within_scope",
            }
        ]
        run = self.replay(source_data=data)
        claim = next(item for item in run.case.claims if item.id == "C_NARRATIVE")
        self.assertEqual(claim.verification, VerificationStatus.UNVERIFIED)
        self.assertEqual(claim.narrative_evidence_id, "E_COMMUNITY")

    def test_exact_same_day_future_retrieval_withholds_candidate_and_source_fact(self):
        run = self.replay(now=CUTOFF + timedelta(seconds=1))
        row = self.row(run)
        self.assertEqual(row["priority"], "insufficient")
        self.assertEqual(row["state"]["_available_ids"], [])
        evidence = next(item for item in run.case.evidence if item.id == "E_PRIMARY")
        self.assertEqual(evidence.provenance.freshness, "future")

    def test_same_day_future_publication_is_not_current_information_even_if_fetched_early(self):
        data = deepcopy(self.source_data)
        data["sources"][0]["published_at"] = (CUTOFF + timedelta(seconds=1)).isoformat()
        data["sources"][0]["observed_at"] = (CUTOFF + timedelta(seconds=1)).isoformat()
        run = self.replay(source_data=data)
        self.assertEqual(self.row(run)["priority"], "insufficient")
        self.assertEqual(self.row(run)["state"]["_available_ids"], [])

    def test_stale_source_degrades_related_candidate_without_zero_substitution(self):
        data = deepcopy(self.source_data)
        data["sources"][0]["published_at"] = "2026-08-01T11:00:00Z"
        data["sources"][0]["observed_at"] = "2026-08-01T11:00:00Z"
        data["sources"][0]["valid_as_of"] = "2026-08-01"
        run = self.replay(source_data=data)
        self.assertEqual(self.row(run)["priority"], "insufficient")
        evidence = next(item for item in run.case.evidence if item.id == "E_PRIMARY")
        self.assertEqual(evidence.provenance.freshness, "stale")
        self.assertEqual(evidence.value, 75)
        self.assertEqual(self.row(run)["priority_reason"]["_available_ids"], [])

    def test_failed_source_and_unmatched_passage_are_unavailable_not_successful_current_evidence(self):
        for response in (
            FetchResponse(b"synthetic outage", "text/html", status=503),
            FetchResponse(b"<p>Different synthetic passage.</p>", "text/html"),
        ):
            with self.subTest(status=response.status):
                self.documents[self.source_data["sources"][0]["url"]] = response
                run = self.replay()
                self.assertNotIn("E_PRIMARY", {item.id for item in run.case.evidence})
                self.assertEqual(self.row(run)["priority"], "insufficient")
                self.assertEqual(self.row(run)["state"]["_withheld_ids"], ["E_PRIMARY"])

    def test_unknown_personal_debt_and_capacity_survive_self_reported_birth_year(self):
        run = self.replay()
        self.assertEqual(run.case.profile.fields["debt"].status, "unknown")
        self.assertIsNone(run.case.profile.fields["debt"].value)
        self.assertIsNone(run.case.profile.fields["risk_capacity"].value)
        self.assertEqual(run.case.profile.fields["birth_year"].value, 1998)
        self.assertEqual(run.result.personal_conclusion, "insufficient_evidence")
        self.assertTrue(any("무부채" in text for text in run.result.constraints))
        self.assertTrue(any("나이" in text for text in run.result.constraints))
        invalid = deepcopy(self.review_data)
        invalid["profile"]["debt"]["value"] = 0
        with self.assertRaises(SourceError):
            self.review(invalid)

    def test_four_candidate_limit_and_one_followup_reference_are_enforced(self):
        valid = deepcopy(self.review_data)
        for row in valid["rows"][2:4]:
            row["priority"] = "candidate"
            row["candidate"] = deepcopy(valid["rows"][0]["candidate"])
        self.review(valid)
        invalid = deepcopy(valid)
        invalid["rows"][4]["priority"] = "candidate"
        invalid["rows"][4]["candidate"] = deepcopy(invalid["rows"][0]["candidate"])
        with self.assertRaises(SourceError):
            self.review(invalid)
        invalid = deepcopy(valid)
        invalid["next_research"]["asset_id"] = "UNDECLARED"
        with self.assertRaises(SourceError):
            self.review(invalid)

    def test_candidate_requires_counterargument_and_uncertainty_and_confirm_question(self):
        changes = (
            lambda row: row["candidate"].pop("counterargument"),
            lambda row: row.update(uncertainty=[]),
            lambda row: row["candidate"].update(confirm=[]),
        )
        for change in changes:
            with self.subTest(change=change):
                invalid = deepcopy(self.review_data)
                change(invalid["rows"][0])
                with self.assertRaises(SourceError):
                    self.review(invalid)

    def test_costs_reference_other_explicit_alternatives_and_rows_match_source_scope(self):
        for identifier in ("CASH", "UNDECLARED"):
            with self.subTest(identifier=identifier):
                invalid = deepcopy(self.review_data)
                invalid["rows"][0]["opportunity_cost"]["alternative_ids"] = [identifier]
                with self.assertRaises(SourceError):
                    self.review(invalid)
        invalid = deepcopy(self.review_data)
        invalid["rows"] = invalid["rows"][:-1]
        with self.assertRaises(SourceError):
            self.replay(review_data=invalid)

    def test_unknown_and_incompatible_scope_refs_fail_instead_of_being_filled(self):
        invalid = deepcopy(self.review_data)
        invalid["rows"][0]["state"]["evidence_ids"] = ["INVENTED_FACT"]
        with self.assertRaises(SourceError):
            self.replay(review_data=invalid)
        data = deepcopy(self.source_data)
        data["sources"][0]["asset_ids"] = ["CASH"]
        with self.assertRaises(SourceError):
            self.replay(source_data=data)

    def test_raw_financial_numbers_are_rejected_in_draft_instead_of_becoming_facts(self):
        invalid = deepcopy(self.review_data)
        invalid["rows"][0]["state"]["text"] = "현재 현금은 연 9.99% 수익을 보장한다."
        with self.assertRaises(SourceError):
            self.review(invalid)
        invalid = deepcopy(self.review_data)
        invalid["review_status"] = "reviewed"
        with self.assertRaises(SourceError):
            self.review(invalid)

    def test_changed_source_metadata_and_snapshot_pins_cannot_rewrite_pinned_evidence(self):
        plan, pins = self.prepare()
        changed = deepcopy(pins)
        changed["sources_digest"] = "0" * 64
        with self.assertRaises(SourceError):
            replay_opportunity(
                self.review(), plan, self.source_store, changed, self.macro_plan, self.macro_store, self.macro_pins
            )
        changed = deepcopy(pins)
        changed["snapshots"]["S_PRIMARY"] = "0" * 64
        with self.assertRaises(SourceError):
            replay_opportunity(
                self.review(), plan, self.source_store, changed, self.macro_plan, self.macro_store, self.macro_pins
            )

    def test_review_digest_and_pinned_observation_metric_trace_are_preserved(self):
        run = self.replay()
        altered = deepcopy(self.review_data)
        altered["rows"][0]["recheck"]["text"] = "새로운 공식 조건이 나오면 합성 질문을 다시 검토한다."
        repeated = self.replay(review_data=altered)
        self.assertNotEqual(run.review.input_digest, repeated.review.input_digest)
        self.assertNotEqual(run.input_digest, repeated.input_digest)
        evidence = {item.id: item for item in run.case.evidence}
        self.assertTrue(run.result.metrics)
        for metric in run.result.metrics:
            for ref in metric.input_ids:
                self.assertIn(ref, evidence)
                self.assertIsNotNone(evidence[ref].value)
                self.assertIn(evidence[ref].provenance.snapshot_id, run.macro.snapshot_refs[evidence[ref].source_id])
        run_costs = {(item.alternative_id, item.forgone_asset_id) for item in run.case.opportunity_costs}
        self.assertEqual(run_costs, {(asset, ASSETS[(index + 1) % len(ASSETS)]) for index, asset in enumerate(ASSETS)})

    def test_unknown_publication_current_observation_is_opportunity_only_not_rewritten_as_publication(self):
        data = deepcopy(self.source_data)
        data["sources"][0]["published_at"] = None
        plan, pins = self.prepare(data)
        legacy = replay_plan(plan, self.source_store, pins)
        original = next(item for item in legacy.evidence if item.id == "E_PRIMARY")
        self.assertEqual(original.provenance.freshness, "unknown")
        run = replay_opportunity(
            self.review(), plan, self.source_store, pins, self.macro_plan, self.macro_store, self.macro_pins
        )
        source = next(item for item in run.case.sources if item.id == "S_PRIMARY")
        self.assertIsNone(source.published_at)
        self.assertIsNone(source.provenance.published_at)
        self.assertEqual(source.provenance.freshness, "fresh")
        self.assertEqual(self.row(run)["priority"], "candidate")

    def test_current_yoy_accepts_dated_prior_year_baseline_and_preserves_metric_trace(self):
        baseline = self.replay()
        yoy = next(metric for metric in baseline.result.metrics if metric.method == "yoy_v1")
        data = deepcopy(self.review_data)
        for name in ("priority_reason", "positive"):
            data["rows"][0][name]["evidence_ids"] = [yoy.id]
        run = self.replay(review_data=data)
        self.assertEqual(self.row(run)["priority"], "candidate")
        self.assertEqual(self.row(run)["priority_reason"]["_available_ids"], [yoy.id])
        evidence = {item.id: item for item in run.case.evidence}
        self.assertTrue(any(evidence[ref].provenance.freshness == "stale" for ref in yoy.input_ids))
        report = render_opportunity_report(run)
        self.assertIn("5.000 percent", report)  # Authored index endpoints 105 / 100 imply exactly five percent.
        manifest = opportunity_manifest(run, report)
        self.assertEqual(manifest["review_sha256"], run.review.input_digest)
        self.assertEqual(manifest["input_sha256"], run.input_digest)
        self.assertEqual(manifest["report_sha256"], sha256(report.encode()).hexdigest())
        self.assertEqual(manifest["review_status"], "draft")
        self.assertEqual(manifest["macro"]["snapshot_refs"], self.macro_pins["snapshots"])
        available = {item.id for item in run.result.metrics}
        for metric in manifest["macro"]["metrics"]:
            if metric["id"] in available:
                self.assertTrue(set(metric["input_observation_ids"]) <= set(evidence))
        alternative = next(item for item in run.case.alternatives if item.id == "CASH")
        self.assertEqual(set(alternative.support_ids), set(yoy.input_ids))

    def test_mutating_loaded_review_cannot_keep_old_input_hash(self):
        plan, pins = self.prepare()
        review = self.review()
        review.data["rows"][0]["priority_reason"]["text"] = "바뀐 합성 조사 해석"
        with self.assertRaises(SourceError):
            replay_opportunity(
                review, plan, self.source_store, pins, self.macro_plan, self.macro_store, self.macro_pins
            )

    def test_malformed_status_and_priority_types_are_validation_errors(self):
        for field in ("review_status", "priority", "profile_status"):
            with self.subTest(field=field):
                data = deepcopy(self.review_data)
                if field == "priority":
                    data["rows"][0]["priority"] = []
                elif field == "profile_status":
                    data["profile"]["debt"]["status"] = []
                else:
                    data["review_status"] = []
                with self.assertRaises(SourceError):
                    self.review(data)

    def test_report_withholds_future_current_assertion_and_source_claim_but_keeps_fresh_narrative_label(self):
        source_data = deepcopy(self.source_data)
        source_data["evidence"][0]["interpretation"] = REVIEWED
        source_data["claims"] = [
            {
                "id": "C_SYNTHETIC_CURRENT",
                "text": "합성 정책 원문의 좁은 인하 폭을 확인한다.",
                "asset_ids": ["CASH"],
                "rule": "reviewed_links_v1",
                "support_ids": ["E_PRIMARY"],
                "counter_ids": [],
                "context_ids": [],
                "narrative_evidence_id": None,
                "review": REVIEWED,
                "verification": "supported_within_scope",
            }
        ]
        data = deepcopy(self.review_data)
        current_assertion = "합성 현재 금리가 급격하게 하락한 상태라는 주장"
        narrative_observation = "합성 공개 토론에서 보장 수익을 기대하는 발언을 관측했다."
        data["rows"][0]["state"]["text"] = current_assertion
        data["sections"]["community"][0]["text"] = narrative_observation
        run = self.replay(source_data=source_data, review_data=data)
        report = render_opportunity_report(run)
        body = report.split("## 부록 · 원문과 재현", 1)[0]
        self.assertIn(current_assertion, body)
        self.assertIn(narrative_observation, body)
        self.assertIn("관측된 서사 · 내용 미검증", body)
        past = deepcopy(data)
        past["as_of"] = (ACQUIRED - timedelta(seconds=1)).isoformat()
        run = self.replay(source_data=source_data, review_data=past)
        past_body = render_opportunity_report(run).split("## 부록 · 원문과 재현", 1)[0]
        self.assertNotIn(current_assertion, past_body)
        self.assertNotIn(narrative_observation, past_body)
        claim = next(item for item in run.case.claims if item.id == "C_SYNTHETIC_CURRENT")
        self.assertEqual(claim.verification, VerificationStatus.UNVERIFIED)
        self.assertNotIn("합성 현금 조건 확인", past_body)

    def test_stale_and_failed_facts_do_not_leak_into_report_body_and_links_resolve(self):
        assertion = "합성 현재 대안의 현금 조건이 충분하다는 문장"
        data = deepcopy(self.review_data)
        data["rows"][0]["state"]["text"] = assertion
        for stale in (False, True):
            with self.subTest(stale=stale):
                source_data = deepcopy(self.source_data)
                if stale:
                    self.documents[source_data["sources"][0]["url"]] = FetchResponse(
                        ("<p>" + PRIMARY_QUOTE + "</p>").encode(), "text/html"
                    )
                    source_data["sources"][0]["published_at"] = "2026-08-01T11:00:00Z"
                    source_data["sources"][0]["observed_at"] = "2026-08-01T11:00:00Z"
                    source_data["sources"][0]["valid_as_of"] = "2026-08-01"
                else:
                    self.documents[source_data["sources"][0]["url"]] = FetchResponse(
                        b"Unavailable synthetic passage", "text/html", status=503
                    )
                run = self.replay(source_data=source_data, review_data=data)
                report = render_opportunity_report(run)
                body = report.split("## 부록 · 원문과 재현", 1)[0]
                self.assertNotIn(assertion, body)
                self.assertEqual(render_opportunity_report(run), report)
                import re

                targets = set(re.findall(r'\]\(#([^\)]+)\)', report))
                anchors = set(re.findall(r'<a id="([^"]+)"', report))
                self.assertTrue(targets <= anchors)

    def cli_args(self):
        plan, pins = self.prepare()
        self.review()
        source_pins = self.directory / "source_pins.json"
        macro_pins = self.directory / "macro_pins.json"
        source_pins.write_text(json.dumps(pins), encoding="utf-8")
        macro_pins.write_text(json.dumps(self.macro_pins), encoding="utf-8")
        arguments = (
            "opportunity",
            "replay",
            self.review_path,
            "--plan",
            self.source_path,
            "--store",
            self.source_store,
            "--pins",
            source_pins,
            "--macro-plan",
            self.macro_path,
            "--macro-store",
            self.macro_store,
            "--macro-pins",
            macro_pins,
        )
        return arguments, (self.review_path, self.source_path, source_pins, self.macro_path, macro_pins)

    @staticmethod
    def cli_call(*arguments):
        from investment_research.__main__ import main

        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = main(list(map(str, arguments)))
        return status, stdout.getvalue(), stderr.getvalue()

    def test_cli_replay_and_manifest_are_deterministic_offline_and_bad_pins_produce_no_report(self):
        arguments, inputs = self.cli_args()
        with (
            patch(
                "investment_research.source_pipeline.acquire",
                side_effect=AssertionError("opportunity replay must not acquire"),
            ),
            patch(
                "investment_research.macro_pipeline.acquire_macro",
                side_effect=AssertionError("opportunity replay must not acquire macro"),
            ),
        ):
            first = self.cli_call(*arguments)
            second = self.cli_call(*arguments)
            self.assertEqual(first[0], 0, first[2])
            self.assertEqual(first, second)
            self.assertIn("Cross-Asset Opportunity Map", first[1])
            output, manifest = self.directory / "opportunity.md", self.directory / "manifest.json"
            status, stdout, stderr = self.cli_call(*arguments, "--output", output, "--manifest", manifest)
            self.assertEqual(status, 0, stderr)
            self.assertEqual(stdout, "")
            self.assertEqual(output.read_text(encoding="utf-8"), first[1])
            data = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(data["kind"], "cross_asset_opportunity_map")
            self.assertEqual(data["report_sha256"], sha256(output.read_bytes()).hexdigest())
            self.assertEqual(data["review_status"], "draft")
            self.assertEqual(len(data["priorities"]), len(ASSETS))
            self.assertEqual(data["macro"]["snapshot_refs"], self.macro_pins["snapshots"])
            inputs[2].write_text('{"invalid":"pins"}', encoding="utf-8")
            failure_path = self.directory / "must_not_exist.md"
            status, stdout, stderr = self.cli_call(*arguments, "--output", failure_path)
            self.assertEqual(status, 2)
            self.assertEqual(stdout, "")
            self.assertTrue(stderr)
            self.assertFalse(failure_path.exists())
        self.assertEqual(self.requests, [])

    def test_cli_preflights_all_outputs_and_preserves_review_plans_pins_and_user_content(self):
        arguments, inputs = self.cli_args()
        user = self.directory / "user.md"
        user.write_text("사용자가 작성한 투자 연구", encoding="utf-8")
        for protected in (*inputs, user):
            with self.subTest(protected=protected.name):
                original = protected.read_bytes()
                status, stdout, stderr = self.cli_call(*arguments, "--output", protected)
                self.assertEqual(status, 2)
                self.assertEqual(stdout, "")
                self.assertTrue(stderr)
                self.assertEqual(protected.read_bytes(), original)
        fresh = self.directory / "fresh.md"
        status, stdout, stderr = self.cli_call(*arguments, "--output", fresh, "--manifest", user)
        self.assertEqual(status, 2)
        self.assertEqual(stdout, "")
        self.assertTrue(stderr)
        self.assertFalse(fresh.exists())
        self.assertEqual(user.read_text(encoding="utf-8"), "사용자가 작성한 투자 연구")


if __name__ == "__main__":
    unittest.main()
