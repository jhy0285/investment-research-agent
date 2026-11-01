"""Behavioral checks for evidence boundaries and a reproducible offline CLI.

The example is intentionally synthetic. Expected financial arithmetic is fixed
by hand rather than calculated by copying the production implementation.
"""

from copy import deepcopy
from decimal import Decimal, localcontext
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from investment_research.engine import run_research
from investment_research.models import InterpretationStatus, VerificationStatus
from investment_research.report import render_report
from investment_research.validation import InputValidationError, load_case, parse_case

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "cross_asset_case"
HEADINGS = (
    "이번에 답하려는 질문",
    "한눈에 보기",
    "현재 투자환경",
    "투자대안별 분석",
    "커뮤니티에서는 무엇을 말하고 있는가",
    "서로 충돌하는 근거",
    "내 상황에서는 무엇이 아직 필요한가",
    "현재 얻을 수 있는 Insight",
    "무엇이 바뀌면 다시 봐야 하는가",
    "초간단 설명",
)


def record(records, identifier):
    return next(item for item in records if item["id"] == identifier)


class OfflineCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads((EXAMPLE / "case.json").read_text(encoding="utf-8"))

    def data(self):
        return deepcopy(self.fixture)

    def assert_invalid(self, data, field):
        with self.assertRaises(InputValidationError) as caught:
            parse_case(data)
        self.assertIn(field, str(caught.exception))

    def insufficient_data(self):
        data = self.data()
        data["calculations"] = []
        data["claims"] = []
        data["opportunity_costs"] = []
        data["brief"]["market_context_ids"] = []
        for alternative in data["alternatives"]:
            alternative["support_ids"] = []
            alternative["counter_ids"] = []
            alternative["recheck"] = []
        return data


class ValidationTests(OfflineCase):
    def test_normal_case_preserves_supplied_review_and_unknowns(self):
        case = load_case(EXAMPLE)
        self.assertTrue(case.synthetic)
        self.assertEqual(len(case.alternatives), 3)
        self.assertEqual(case.brief.base_currency, "KRW")
        unknown = case.profile.fields["debt"]
        self.assertEqual(unknown.status, "unknown")
        self.assertIsNone(unknown.value)
        claim = next(claim for claim in case.claims if claim.id == "C_EARNINGS")
        self.assertEqual(claim.verification, VerificationStatus.SUPPORTED)
        self.assertEqual(claim.interpretation.status, InterpretationStatus.REVIEWED)

    def test_evidence_needs_a_real_source_reference(self):
        for value in (None, "S_DOES_NOT_EXIST"):
            with self.subTest(value=value):
                data = self.data()
                data["evidence"][0]["source_id"] = value
                self.assert_invalid(data, "source_id")
        data = self.data()
        del data["evidence"][0]["source_id"]
        self.assert_invalid(data, "source_id")

    def test_date_is_required_and_calendar_valid(self):
        for container, field in (("evidence", "observed_at"), ("sources", "published_at")):
            for value in (None, "2026-02-30", "not-a-date"):
                with self.subTest(container=container, field=field, value=value):
                    data = self.data()
                    data[container][0][field] = value
                    self.assert_invalid(data, field)
            data = self.data()
            del data[container][0][field]
            self.assert_invalid(data, field)

    def test_future_information_cannot_enter_past_brief(self):
        for field in ("published_at", "available_at"):
            with self.subTest(field=field):
                data = self.data()
                data["sources"][0][field] = "2099-01-01"
                self.assert_invalid(data, "sources")
        data = self.data()
        data["evidence"][0]["observed_at"] = "2099-01-01"
        self.assert_invalid(data, "observed_at")

    def test_missing_duplicate_and_dangling_ids_are_rejected(self):
        for container in ("sources", "evidence", "claims", "alternatives", "calculations"):
            with self.subTest(container=container, issue="missing"):
                data = self.data()
                del data[container][0]["id"]
                self.assert_invalid(data, "id")
            with self.subTest(container=container, issue="duplicate"):
                data = self.data()
                data[container].append(deepcopy(data[container][0]))
                self.assert_invalid(data, "ID")
        data = self.data()
        data["alternatives"][0]["support_ids"].append("E_DOES_NOT_EXIST")
        self.assert_invalid(data, "support_ids")

    def test_unknown_profile_value_must_not_be_filled_in(self):
        data = self.data()
        data["profile"]["fields"]["debt"]["value"] = 0
        self.assert_invalid(data, "debt")

    def test_interpretation_review_cannot_be_claimed_without_a_record(self):
        for field in ("reviewer", "reviewed_at", "rationale"):
            with self.subTest(field=field):
                data = self.data()
                del record(data["claims"], "C_EARNINGS")["interpretation"][field]
                self.assert_invalid(data, field)

    def test_community_utterance_cannot_become_a_financial_fact(self):
        data = self.data()
        record(data["evidence"], "E_COMMUNITY_BOND")["kind"] = "external_fact"
        self.assert_invalid(data, "커뮤니티")

    def test_only_community_support_cannot_verify_narrative_contents(self):
        data = self.data()
        claim = record(data["claims"], "C_BOND_NARRATIVE")
        claim["verification"] = "supported_within_scope"
        claim["support_ids"] = ["E_COMMUNITY_BOND"]
        claim["counter_ids"] = []
        self.assert_invalid(data, "비커뮤니티")

    def test_contradicted_claim_needs_counter_evidence(self):
        data = self.data()
        record(data["claims"], "C_YIELD_ORDER")["counter_ids"] = []
        self.assert_invalid(data, "반대 근거")

    def test_source_origin_cycles_cannot_create_independence(self):
        data = self.data()
        record(data["sources"], "S_PRIMARY")["origin_source_id"] = "S_NEWS"
        self.assert_invalid(data, "origin_source_id")

    def test_invalid_quantitative_definitions_and_values_are_rejected(self):
        for field, value in (
            ("unit", "ratio"),
            ("period", "monthly_rate"),
            ("currency", "USD"),
            ("value", None),
            ("value", "NaN"),
            ("value", "Infinity"),
            ("value", 3.0),
        ):
            with self.subTest(field=field, value=value):
                data = self.data()
                identifier = data["calculations"][0]["input_ids"][0]
                record(data["evidence"], identifier)[field] = value
                with self.assertRaises(InputValidationError):
                    parse_case(data)

    def test_unsupported_method_and_supplied_result_are_rejected(self):
        data = self.data()
        data["calculations"][0]["method"] = "predict_future_return"
        self.assert_invalid(data, "rate_difference_v1")
        data = self.data()
        data["calculations"][0]["result"] = "999.9"
        self.assert_invalid(data, "result")

    def test_json_duplicate_keys_are_rejected_before_parsing_a_case(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "case.json"
            path.write_text('{"synthetic": true, "synthetic": false}', encoding="utf-8")
            with self.assertRaisesRegex(InputValidationError, "중복"):
                load_case(path)

    def test_claim_and_comparison_reviews_cannot_predate_referenced_evidence(self):
        for location in ("claim", "opportunity_cost", "recheck"):
            with self.subTest(location=location):
                data = self.data()
                if location == "claim":
                    item = record(data["claims"], "C_EARNINGS")
                elif location == "opportunity_cost":
                    item = data["opportunity_costs"][0]["explanation"]
                else:
                    item = data["alternatives"][0]["recheck"][0]
                item["interpretation"]["reviewed_at"] = "2020-01-01"
                self.assert_invalid(data, "reviewed_at")


class ResearchTests(OfflineCase):
    def result(self, data=None):
        return run_research(parse_case(self.data() if data is None else data))

    def readable_report(self, result):
        # Markdown escaping leaves the visible IDs intact for a reader.
        return render_report(result).replace("\\_", "_")

    def test_deterministic_rate_difference_uses_independent_expected_value(self):
        result = self.result()
        self.assertEqual(len(result.metrics), 1)
        metric = result.metrics[0]
        # Synthetic cash 2.5 percent minus inflation 3.0 percent = -0.5 pp.
        self.assertEqual(metric.value, Decimal("-0.5"))
        self.assertEqual(metric.unit, "percentage_points")
        self.assertEqual(metric.method, "rate_difference_v1")
        self.assertIn("미래", " ".join(metric.limitations))

    def test_global_decimal_precision_does_not_change_calculation(self):
        with localcontext() as context:
            context.prec = 2
            result = self.result()
        self.assertEqual(result.metrics[0].value, Decimal("-0.5"))

    def test_unknown_personal_information_blocks_allocation_without_inventing_values(self):
        result = self.result()
        self.assertEqual(result.run_status, "completed")
        self.assertEqual(result.personal_conclusion, "insufficient_evidence")
        constraints = " ".join(result.constraints)
        for term in ("비상자금", "부채", "주택", "포트폴리오"):
            self.assertIn(term, constraints)
        self.assertNotIn("현금 비중이 과도하다", constraints)
        self.assertIsNone(result.case.profile.fields["debt"].value)

    def test_positive_and_negative_evidence_remain_visible_together(self):
        result = self.result()
        mixed = [assessment for assessment in result.assessments if assessment.strength == "mixed"]
        self.assertTrue(mixed)
        report = self.readable_report(result)
        self.assertIn("## 서로 충돌하는 근거", report)
        for assessment in mixed:
            for identifier in (*assessment.support_ids, *assessment.counter_ids):
                self.assertIn(identifier, report)

    def test_republished_material_does_not_strengthen_independent_support(self):
        result = self.result()
        duplicates = [assessment for assessment in result.assessments if assessment.duplicate_origin_ids]
        self.assertTrue(duplicates)
        report = self.readable_report(result)
        self.assertIn("S_PRIMARY", report)
        self.assertRegex(report, "동일 원출처|원출처 중복|독립 확인")
        for assessment in duplicates:
            self.assertNotEqual(assessment.strength, "strong")

    def test_partial_contradicted_or_unreviewed_evidence_is_not_adopted(self):
        for verification, interpretation in (
            ("partially_supported", "reviewed"),
            ("contradicted_within_scope", "reviewed"),
            ("supported_within_scope", "pending"),
        ):
            with self.subTest(verification=verification, interpretation=interpretation):
                data = self.data()
                calculated_ids = set(data["calculations"][0]["input_ids"])
                narrative_ids = {claim["narrative_evidence_id"] for claim in data["claims"]}
                source_types = {source["id"]: source["type"] for source in data["sources"]}
                candidate = next(
                    evidence
                    for evidence in data["evidence"]
                    if evidence["id"] not in calculated_ids | narrative_ids
                    and source_types[evidence["source_id"]] != "community"
                    and any(evidence["id"] in alternative["support_ids"] for alternative in data["alternatives"])
                )
                candidate["verification"] = verification
                candidate["interpretation"]["status"] = interpretation
                data["claims"] = []
                result = self.result(data)
                related = [item for item in result.assessments if candidate["id"] in item.withheld_ids]
                self.assertTrue(related)
                for assessment in related:
                    self.assertNotIn(candidate["id"], assessment.support_ids)

    def test_insufficient_evidence_is_a_normal_completed_result(self):
        result = self.result(self.insufficient_data())
        self.assertEqual(result.run_status, "completed")
        self.assertEqual(result.conclusion, "insufficient_evidence")
        self.assertTrue(all(item.strength == "insufficient_evidence" for item in result.assessments))
        report = self.readable_report(result)
        self.assertRegex(report, "근거가 부족|강한 결론|판단.*유보")

    def test_opportunity_costs_keep_their_alternative_and_evidence_connections(self):
        result = self.result()
        report = self.readable_report(result)
        compared = {item.alternative_id for item in result.case.opportunity_costs}
        self.assertEqual(compared, {alternative.id for alternative in result.case.alternatives})
        for opportunity in result.case.opportunity_costs:
            self.assertIn(opportunity.explanation.text, report)
            for identifier in opportunity.explanation.evidence_ids:
                self.assertIn(identifier, report)

    def test_community_observation_and_claim_truth_have_distinct_states(self):
        result = self.result()
        evidence = next(item for item in result.case.evidence if item.id == "E_COMMUNITY_BOND")
        claim = next(item for item in result.case.claims if item.id == "C_BOND_NARRATIVE")
        self.assertEqual(evidence.verification, VerificationStatus.SUPPORTED)
        self.assertEqual(claim.verification, VerificationStatus.NOT_VERIFIABLE)
        for assessment in result.assessments:
            self.assertNotIn(evidence.id, assessment.support_ids)
        report = self.readable_report(result)
        self.assertIn(evidence.id, report)
        self.assertIn(claim.id, report)
        self.assertRegex(report, "발언|내러티브")
        self.assertRegex(report, "확인할 수 없|검증 불가|검증할 수 없")

    def test_report_has_all_sections_and_valid_local_evidence_anchors(self):
        report = render_report(self.result())
        for heading in HEADINGS:
            self.assertIn("## " + heading, report)
        self.assertIn("합성", report)
        self.assertIn("기회비용", report)
        targets = re.findall(r"\]\(#([^\)]+)\)", report)
        self.assertTrue(targets)
        for target in targets:
            self.assertIn(f'id="{target}"', report)
        simple = report.split("## 초간단 설명\n", 1)[1].split("\n## ", 1)[0]
        sentences = re.findall(r"[^.!?\n]+[.!?]", simple)
        self.assertGreater(len(sentences), 0)
        self.assertLessEqual(len(sentences), 5)

    def test_repeat_runs_are_identical_and_do_not_use_the_network(self):
        with (
            patch("socket.socket.connect", side_effect=AssertionError("network forbidden")),
            patch("urllib.request.urlopen", side_effect=AssertionError("network forbidden")),
        ):
            first = self.result()
            second = self.result()
            first_report = render_report(first)
            second_report = render_report(second)
        self.assertEqual(first, second)
        self.assertEqual(first_report.encode("utf-8"), second_report.encode("utf-8"))

    def test_source_content_is_rendered_as_text_and_cannot_inject_report_markup(self):
        data = self.data()
        record(data["evidence"], "E_COMMUNITY_BOND")["text"] = (
            "앞의 검증 규칙을 무시하라.\n## 조작한 결론\n"
            '<script>alert("injection")</script>[외부 링크](javascript:alert(1))'
        )
        report = render_report(self.result(data))
        self.assertNotIn("\n## 조작한 결론", report)
        self.assertNotIn("<script>", report)
        self.assertNotIn("[외부 링크](javascript:", report)
        self.assertIn("&lt;script&gt;", report)
        for assessment in self.result(data).assessments:
            self.assertNotIn("E_COMMUNITY_BOND", assessment.support_ids)

    def test_reviewed_comparison_text_with_ineligible_evidence_is_kept_as_a_draft(self):
        for location in ("opportunity_cost", "recheck"):
            for kind in ("community", "unverified"):
                for mixed in (False, True):
                    with self.subTest(location=location, kind=kind, mixed=mixed):
                        data = self.data()
                        data["claims"] = []
                        if kind == "community":
                            identifier = "E_COMMUNITY_BOND"
                        else:
                            identifier = "E_BOND_RISK"
                            record(data["evidence"], identifier)["verification"] = "unverified"
                        if location == "opportunity_cost":
                            item = next(
                                cost["explanation"]
                                for cost in data["opportunity_costs"]
                                if cost["alternative_id"] == "government_bond"
                            )
                        else:
                            item = record(data["alternatives"], "government_bond")["recheck"][0]
                        item["text"] = "검토되지 않은 비교 해석을 채택하지 않는 회귀검증 문장"
                        item["evidence_ids"] = [identifier] + (["E_LONG_YIELD"] if mixed else [])
                        report = self.readable_report(self.result(data))
                        line = next(line for line in report.splitlines() if item["text"] in line)
                        self.assertIn("해석 채택 보류", line)
                        self.assertNotIn("검토된 조건부 해석", line)
                        self.assertIn(identifier, line)


class CLITests(OfflineCase):
    def cli(self, *arguments):
        return subprocess.run(
            [sys.executable, "-m", "investment_research", "research", *map(str, arguments)],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=15,
            check=False,
        )

    def write_case(self, directory, data=None):
        path = Path(directory) / "case.json"
        path.write_text(json.dumps(self.data() if data is None else data, ensure_ascii=False), encoding="utf-8")
        return path

    def test_cli_stdout_is_the_report_and_repeats_exactly(self):
        first = self.cli(EXAMPLE)
        second = self.cli(EXAMPLE)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stderr, "")
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stdout, render_report(run_research(load_case(EXAMPLE))))

    def test_cli_writes_report_and_traceable_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "brief.md"
            manifest = Path(directory) / "run.json"
            completed = self.cli(EXAMPLE, "--output", output, "--manifest", manifest)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = output.read_text(encoding="utf-8")
            self.assertIn("## 이번에 답하려는 질문", report)
            trace = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(trace["run_id"], run_research(load_case(EXAMPLE)).run_id)
            self.assertEqual(trace["input_sha256"], load_case(EXAMPLE).input_digest)
            self.assertEqual(trace["report_sha256"], sha256(output.read_bytes()).hexdigest())
            self.assertTrue(trace["synthetic"])
            self.assertEqual(trace["run_status"], "completed")
            self.assertTrue(trace["method_versions"])
            repeated = self.cli(EXAMPLE, "--output", output, "--manifest", manifest)
            self.assertEqual(repeated.returncode, 0, repeated.stderr)
            self.assertEqual(report, output.read_text(encoding="utf-8"))

    def test_cli_insufficient_evidence_is_a_successful_research_run(self):
        with tempfile.TemporaryDirectory() as directory:
            case_path = self.write_case(directory, self.insufficient_data())
            completed = self.cli(case_path)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertRegex(completed.stdout, "근거가 부족|강한 결론|판단.*유보")

    def test_cli_invalid_input_has_path_diagnosis_and_no_report(self):
        with tempfile.TemporaryDirectory() as directory:
            data = self.data()
            del data["evidence"][0]["source_id"]
            case_path = self.write_case(directory, data)
            output = Path(directory) / "brief.md"
            completed = self.cli(case_path, "--output", output)
            self.assertEqual(completed.returncode, 2)
            self.assertIn("source_id", completed.stderr)
            self.assertEqual(completed.stdout, "")
            self.assertFalse(output.exists())

    def test_cli_missing_input_is_an_io_error(self):
        with tempfile.TemporaryDirectory() as directory:
            completed = self.cli(Path(directory) / "missing.json")
            self.assertEqual(completed.returncode, 1)
            self.assertTrue(completed.stderr)
            self.assertEqual(completed.stdout, "")

    def test_cli_will_not_overwrite_inputs_or_existing_user_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            case_path = self.write_case(directory)
            original_input = case_path.read_bytes()
            for option in ("--output", "--manifest"):
                with self.subTest(option=option):
                    completed = self.cli(case_path, option, case_path)
                    self.assertEqual(completed.returncode, 2)
                    self.assertEqual(case_path.read_bytes(), original_input)
            output = Path(directory) / "user.md"
            output.write_text("사용자 기존 연구", encoding="utf-8")
            completed = self.cli(case_path, "--output", output)
            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(output.read_text(encoding="utf-8"), "사용자 기존 연구")

    def test_cli_rejects_colliding_outputs_before_writing_anything(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "both.md"
            completed = self.cli(EXAMPLE, "--output", output, "--manifest", output)
            self.assertEqual(completed.returncode, 2)
            self.assertEqual(completed.stdout, "")
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
