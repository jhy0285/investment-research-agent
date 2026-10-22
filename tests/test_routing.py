"""Intent and scope contracts: no market acquisition or fabricated analysis."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from investment_research.__main__ import main
from investment_research.routing import ResearchMode as Mode, plan_research
from investment_research.sources import SourceError


class RoutingTests(unittest.TestCase):
    def test_natural_single_entry_examples(self):
        cases = {
            "오늘 투자기회 찾아줘.": Mode.OPPORTUNITY_SCAN,
            "현재 신규 자금을 투자한다면 어디에 투자하는 것이 가장 합리적인가?": Mode.OPPORTUNITY_SCAN,
            "오늘 투자 가능한 현금 1,000만원이 있다면 어디에 투자할까?": Mode.OPPORTUNITY_SCAN,
            "어떤 자산군을 지금 조사할까?": Mode.OPPORTUNITY_SCAN,
            "What asset classes are worth researching now?": Mode.OPPORTUNITY_SCAN,
            "What has changed across markets?": Mode.OPPORTUNITY_SCAN,
            "Where does risk/reward appear interesting?": Mode.OPPORTUNITY_SCAN,
            "BTC 지금 어때?": Mode.ASSET_DEEP_DIVE,
            "천연가스 투자 괜찮아?": Mode.ASSET_DEEP_DIVE,
            "동탄 아파트 지금 사도 될까?": Mode.ASSET_DEEP_DIVE,
            "배당투자 지금 할 만해?": Mode.ASSET_DEEP_DIVE,
            "지금 배당투자를 늘리는 게 맞아?": Mode.ASSET_DEEP_DIVE,
            "S&P500 현재 valuation을 깊게 검토해줘.": Mode.ASSET_DEEP_DIVE,
            "내 포트폴리오 괜찮아?": Mode.PORTFOLIO_REVIEW,
            "Should I rebalance?": Mode.PORTFOLIO_REVIEW,
            "현금 비중 괜찮아?": Mode.PORTFOLIO_REVIEW,
            "삼성전자랑 SK하이닉스 비교해줘.": Mode.COMPARE,
            "동탄 집이랑 S&P500 중 뭐가 나아?": Mode.COMPARE,
            "SCHD vs Korean dividend stocks": Mode.COMPARE,
            "Bitcoin vs Ethereum": Mode.COMPARE,
            "Samsung Electronics vs SK Hynix": Mode.COMPARE,
            "S&P 500 vs Treasury bonds": Mode.COMPARE,
            "Korean real estate vs US equities": Mode.COMPARE,
        }
        for question, expected in cases.items():
            with self.subTest(question=question):
                plan = plan_research(question)
                self.assertEqual(plan.modes, (expected,))
                self.assertFalse(plan.clarifications)
                self.assertTrue(all(not t.depends_on for t in plan.tasks))

    def test_asset_methods_are_distinct_and_do_not_require_scan(self):
        for question, family in [
            ("BTC 지금 어때?", "crypto"),
            ("천연가스 분석해줘", "natural_gas"),
            ("동탄 집을 조사해줘", "real_estate"),
            ("배당투자 어때?", "equity_strategy"),
        ]:
            with self.subTest(question=question):
                task = plan_research(question).tasks[0]
                self.assertEqual(task.subjects[0].method_family, family)
                self.assertEqual(task.scope, "specified_subject")
                self.assertNotIn("P/E", " ".join(task.required_inputs))

    def test_scoped_opportunity_question_remains_deep_dive(self):
        self.assertEqual(plan_research("BTC에 투자기회가 있어?").modes, (Mode.ASSET_DEEP_DIVE,))

    def test_compare_keeps_asset_specific_economics_and_named_alternatives(self):
        task = plan_research("동탄 집이랑 S&P500 중 뭐가 나아?").tasks[0]
        self.assertEqual({s.method_family for s in task.subjects}, {"real_estate", "equity_index"})
        self.assertTrue(any("비교 불가능" in q for q in task.questions))
        self.assertTrue(any("세금" in q for q in task.questions))
        plan = plan_research("HYG vs LQD")
        self.assertEqual(plan.modes, (Mode.COMPARE,))
        self.assertEqual([s.label for s in plan.tasks[0].subjects], ["HYG", "LQD"])
        self.assertTrue(plan.clarifications)

    def test_duration_alternatives_are_not_collapsed(self):
        task = plan_research("단기 국채와 장기 국채 비교해줘").tasks[0]
        self.assertEqual([s.label for s in task.subjects], ["단기 국채", "장기 국채"])

    def test_type_labels_do_not_add_an_extra_deep_dive_and_index_scope_is_preserved(self):
        plan = plan_research("SPY ETF를 분석해줘")
        self.assertEqual(len(plan.tasks), 1)
        self.assertEqual(plan.tasks[0].subjects[0].label, "SPY")
        task = plan_research("Nasdaq vs Nasdaq-100").tasks[0]
        self.assertEqual([s.label for s in task.subjects], ["Nasdaq", "Nasdaq-100"])

    def test_relevant_market_context_does_not_trigger_a_full_scan(self):
        plan = plan_research("BTC를 전체 시장 맥락에서 분석해줘")
        self.assertEqual(plan.modes, (Mode.ASSET_DEEP_DIVE,))
        self.assertEqual(len(plan.tasks), 1)

    def test_portfolio_begins_with_holdings_and_distinguishes_marginal_effect(self):
        task = plan_research("내 포트폴리오 괜찮아?").tasks[0]
        self.assertEqual(task.scope, "actual_portfolio_and_constraints")
        self.assertTrue(any("실제 보유" in item for item in task.required_inputs))
        self.assertTrue(any("부채" in item for item in task.required_inputs))
        self.assertEqual(len(task.questions), 3)
        self.assertTrue(any("안전·적절성을 확정하지" in item for item in task.questions))

    def test_combined_scan_and_two_direct_deep_dives_have_no_scan_gate(self):
        plan = plan_research("시장 전체를 훑고 천연가스와 한국 반도체는 깊게 분석해줘.")
        self.assertEqual(plan.modes, (Mode.OPPORTUNITY_SCAN, Mode.ASSET_DEEP_DIVE))
        deep = [task for task in plan.tasks if task.mode == Mode.ASSET_DEEP_DIVE]
        self.assertEqual(len(deep), 2)
        self.assertTrue(all(not task.depends_on for task in deep))

    def test_combined_portfolio_and_compare_adds_no_scan_or_extra_deep_dive(self):
        plan = plan_research("내 포트폴리오를 보고 국채와 S&P 500 중 어디에 신규 자금을 넣을지 비교해줘.")
        self.assertEqual(plan.modes, (Mode.PORTFOLIO_REVIEW, Mode.COMPARE))
        self.assertEqual(len(plan.tasks), 2)
        self.assertTrue(any("실제 포트폴리오" in item for item in plan.tasks[1].required_inputs))

    def test_user_requested_scan_candidates_are_conditional_dependency(self):
        plan = plan_research("요즘 투자할 곳 찾아보고 가장 유망한 두 개를 깊게 분석해줘.")
        self.assertEqual(plan.modes, (Mode.OPPORTUNITY_SCAN, Mode.ASSET_DEEP_DIVE))
        task = plan.tasks[-1]
        self.assertEqual(task.depends_on, ("scan",))
        self.assertEqual(task.scope, "scan_candidates_only_if_supported")
        self.assertTrue(any("선택 유보" in item for item in task.required_inputs))

    def test_explicit_modes_override_inference_without_adding_modes(self):
        plan = plan_research("오늘 투자기회 찾아줘", modes=[Mode.ASSET_DEEP_DIVE])
        self.assertEqual(plan.selection_source, "explicit")
        self.assertEqual(plan.modes, (Mode.ASSET_DEEP_DIVE,))
        self.assertTrue(plan.clarifications)
        plan = plan_research("Asset Deep Dive: BTC 지금 어때?")
        self.assertEqual(plan.modes, (Mode.ASSET_DEEP_DIVE,))
        plan = plan_research("Portfolio Review + Compare: 내 포트폴리오에서 BTC vs ETH")
        self.assertEqual(plan.modes, (Mode.PORTFOLIO_REVIEW, Mode.COMPARE))

    def test_negated_scan_does_not_expand_scope(self):
        for question in ("시장 전체를 훑지 말고 BTC만 깊게 분석해줘.", "Don't run an Opportunity Scan; BTC 지금 어때?"):
            self.assertEqual(plan_research(question).modes, (Mode.ASSET_DEEP_DIVE,))

    def test_unresolved_questions_require_clarification_not_full_scan(self):
        for question in ("괜찮아?", "Acme strategy 지금 어때?", "비교해줘"):
            plan = plan_research(question)
            self.assertTrue(plan.clarifications)
            self.assertNotIn(Mode.OPPORTUNITY_SCAN, plan.modes)
            self.assertEqual(plan.to_dict()["execution_status"], "not_started")

    def test_invalid_explicit_modes_and_questions_are_rejected(self):
        for modes in ([], ["other"], ["compare", "compare"], "compare"):
            with self.subTest(modes=modes), self.assertRaises(SourceError):
                plan_research("BTC vs ETH", modes=modes)
        for question in (None, " ", "a" * 4001):
            with self.assertRaises(SourceError):
                plan_research(question)

    def test_cli_planning_is_offline_deterministic_and_preserves_files(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            patch("socket.create_connection", side_effect=AssertionError("no network")),
        ):
            path = Path(directory) / "plan.json"
            args = ["ask", "BTC 지금 어때?", "--plan-only", "--output", str(path)]
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                self.assertEqual(main(args), 0)
                first = path.read_bytes()
                self.assertEqual(main(args), 0)
                self.assertEqual(path.read_bytes(), first)
                self.assertEqual(main(["ask", "천연가스 투자 어때?", "--plan-only", "--output", str(path)]), 2)
                self.assertEqual(path.read_bytes(), first)
            data = json.loads(first)
            self.assertEqual(data["modes"], ["asset_deep_dive"])
            self.assertEqual(data["execution_status"], "not_started")
            self.assertNotIn("judgment", data)

    def test_cli_explicit_mode_wins(self):
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["ask", "BTC vs ETH", "--mode", "asset_deep_dive", "--plan-only"]), 0)
        self.assertEqual(json.loads(output.getvalue())["modes"], ["asset_deep_dive"])
