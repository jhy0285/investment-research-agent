"""Authored synthetic responses only: real orchestration without live HTTP/DNS."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext
from io import StringIO
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from investment_research.__main__ import main
from investment_research.models import InterpretationStatus, VerificationStatus
from investment_research.orchestrator import execute_ask, replay_ask
from investment_research.orchestrator_report import render_ask_report, research_status
from investment_research.portfolio import review_portfolio, validate_portfolio
from investment_research.research_catalog import CPI, FX, RATES, METHODS, ResearchCatalog, load_catalog
from investment_research.routing import ResearchMode as Mode
from investment_research.sources import FetchResponse, SourceError, SourceSpec
from investment_research.source_pipeline import _digest
from tests import test_macro_pipeline as macro_fixture

NOW = macro_fixture.ACQUIRED_AT
DEFINITION = dict(
    measure="authored synthetic passage",
    unit="text",
    period="synthetic snapshot",
    currency=None,
    scope="synthetic fixture",
    adjustment="authored fixture",
)
FINANCIAL = dict(
    measure="authored synthetic valuation and yield",
    unit="ratio and percent",
    period="synthetic snapshot",
    currency="USD",
    scope="synthetic index and Treasury",
    adjustment="authored fixture",
)


def synthetic_catalog():
    # Use catalog IDs to exercise method projection. All publications, bodies,
    # observations, numbers and conclusions are freshly authored test fixtures.
    originals = load_catalog()
    sources = []
    evidence = []
    documents = {}
    for old in originals.sources["sources"]:
        identifier = old["id"]
        community = old["type"] == "community"
        definition = FINANCIAL if identifier in {"DD_IDX_FACTSET_Q3", "DD_TR_H15_CURVE"} else DEFINITION
        quote = (
            "Synthetic fixture only. Forward P/E 20.0; Treasury 3.0 percent."
            if definition == FINANCIAL
            else (
                "Authored synthetic participants question durable demand."
                if community
                else "Authored synthetic issuer describes its economics and risks."
            )
        )
        url = "https://synthetic-ask.example.org/" + identifier.lower()
        spec = SourceSpec(
            id=identifier,
            url=url,
            canonical_url=url,
            type="community" if community else "primary",
            publisher="Authored synthetic test publisher",
            title="Synthetic fixture, never live evidence",
            jurisdiction="US",
            topics=("synthetic-test",),
            asset_ids=("BTC",),
            content_type="text/html",
            access_method="public_http",
            policy_url="https://synthetic-ask.example.org/terms",
            policy_note="Authored synthetic fixture retained only for offline tests.",
            retention="excerpt",
            max_age_days=5,
            observed_at="2026-09-10T11:00:00Z",
            published_at="2026-09-10T11:00:00Z",
            valid_as_of="2026-09-10",
            excerpts=(
                {"id": "Q_SYNTHETIC", "quote": quote, "locator": "synthetic paragraph", "definition": definition},
            ),
        )
        sources.append(asdict(spec))
        evidence.append(
            dict(
                id="E_" + identifier,
                source_id=identifier,
                excerpt_id="Q_SYNTHETIC",
                view="community" if community else "fundamental",
                kind="observed_narrative" if community else "external_fact",
                definition=deepcopy(definition),
                extraction=None,
                interpretation=None,
                limitations=["Authored synthetic fixture; not actual market evidence."],
            )
        )
        documents[url] = FetchResponse(("<p>" + quote + "</p>").encode(), "text/html")
    macro = macro_fixture.synthetic_plan_data()
    ids = {
        macro_fixture.CPI_ID: CPI,
        macro_fixture.TWO_ID: RATES[0],
        macro_fixture.TEN_ID: RATES[1],
        macro_fixture.FX_ID: FX,
    }
    for item in macro["series"]:
        item["canonical_id"] = ids[item["canonical_id"]]
    for item in macro["bindings"]:
        item["series_id"] = ids[item["series_id"]]
    macro["yoy_series_ids"] = [CPI]
    macro["yield_pair"] = [RATES[1], RATES[0]]
    documents[macro["sources"][0]["url"]] = FetchResponse(macro_fixture.cpi_document(), "application/json")
    documents[macro["sources"][1]["url"]] = FetchResponse(
        macro_fixture.fed_csv(
            (macro_fixture.TWO_FIELD, macro_fixture.TEN_FIELD),
            (("2026-09-08", "1.50", "3.00"), ("2026-09-09", "2.00", "3.50")),
        ),
        "text/csv",
    )
    documents[macro["sources"][2]["url"]] = FetchResponse(
        macro_fixture.fed_csv(
            (macro_fixture.FX_FIELD,), (("2026-09-08", "1300"), ("2026-09-09", "1310")), identifier_prefix="H10/H10/"
        ),
        "text/csv",
    )
    facts = []
    for identifier, source, value, unit, basis, context in (
        ("F_PE", "DD_IDX_FACTSET_Q3", "20.0", "ratio", "forward_12m_pe", "Forward P/E 20.0"),
        ("F_TREASURY", "DD_TR_H15_CURVE", "3.0", "percent", "nominal_cmt_investment_yield", "Treasury 3.0 percent"),
    ):
        facts.append(
            dict(
                id=identifier,
                label="합성 " + identifier,
                source_evidence_id="E_" + source,
                quote_context=context,
                quote_token=value,
                value=value,
                unit=unit,
                basis=basis,
                currency="USD",
                entity="SYNTHETIC",
                window="synthetic snapshot",
                observed_at="2026-09-10",
                source_definition=FINANCIAL,
            )
        )
    calculations = [
        dict(
            id="CALC_EY",
            label="합성 이익수익률",
            method="earnings_yield_v1",
            input_ids=["F_PE"],
            limitations=["합성 입력, 미래 수익 아님"],
        ),
        dict(
            id="CALC_GAP",
            label="합성 이익수익률과 국채의 차이",
            method="descriptive_yield_gap_v1",
            input_ids=["F_PE", "F_TREASURY"],
            limitations=["합성 입력, ERP 아님"],
        ),
    ]
    return (
        ResearchCatalog(
            dict(sources=sources, evidence=evidence, claims=[]),
            macro,
            dict(facts=facts, calculations=calculations),
            synthetic=True,
        ),
        documents,
    )


def portfolio_data(**changes):
    data = dict(
        schema_version="portfolio-v1",
        as_of="2026-09-10",
        base_currency="KRW",
        coverage="complete",
        holdings=[
            dict(id="STOCK", name="미국 주식", asset="S&P500", value_krw="6000000"),
            dict(id="COIN", name="Bitcoin", asset="BTC", value_krw="2000000"),
        ],
        cash_krw="2000000",
        debt_krw="1000000",
        monthly_investable_krw="500000",
        future_cash_needs=[dict(name="합성 이사 비용", amount_krw="3000000", needed_at="2027-09-10")],
        horizon_months=60,
        synthetic=True,
    )
    data.update(changes)
    return data


class OrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.catalog, self.documents = synthetic_catalog()
        self.requests = []
        self.sequence = 0
        for target in ("socket.socket.connect", "socket.getaddrinfo", "investment_research.sources._fetch_http"):
            blocker = patch(target, side_effect=AssertionError("unit tests must not use HTTP/DNS"))
            blocker.start()
            self.addCleanup(blocker.stop)

    def fetcher(self, url, timeout, max_bytes):
        if url.endswith('/robots.txt'):
            return FetchResponse(b'User-agent: *\nAllow: /\n', 'text/plain')
        self.requests.append(url)
        response = self.documents[url]
        if isinstance(response, Exception):
            raise response
        return response

    def run_ask(self, question, **kwargs):
        self.sequence += 1
        return execute_ask(
            question, self.directory / str(self.sequence), catalog=self.catalog, fetcher=self.fetcher, now=NOW, **kwargs
        )

    def manifest(self, run):
        return json.loads((run.directory / "run_manifest.json").read_text())

    def test_scan_executes_opportunity_map_and_generates_report_without_forced_ranking(self):
        run = self.run_ask("오늘 투자할 만한 곳 찾아줘.")
        self.assertEqual(list(run.input["plan"]["modes"]), [Mode.OPPORTUNITY_SCAN])
        self.assertEqual({m["id"] for m in run.input["methods"]}, set(METHODS))
        self.assertIsNotNone(run.opportunity)
        self.assertIn(dict(function="replay_opportunity", purpose="opportunity_scan"), run.invocations)
        self.assertIn("투자 대상을 억지로 선정하지 않았다", render_ask_report(run))
        self.assertTrue((run.directory / "report.md").is_file())

    def test_btc_direct_execution_uses_only_crypto_and_fx_sources(self):
        run = self.run_ask("BTC 지금 어때?")
        self.assertEqual(list(run.input["plan"]["modes"]), [Mode.ASSET_DEEP_DIVE])
        self.assertEqual([m["id"] for m in run.input["methods"]], ["BTC"])
        self.assertEqual({s.id for s in run.case.sources}, set(METHODS["BTC"].source_ids) | {"S_FX"})
        self.assertIsNone(run.opportunity)
        self.assertIsNone(run.deep)
        self.assertNotIn("천연가스", render_ask_report(run))
        self.assertEqual(len(self.requests), len(set(self.requests)))
        self.assertTrue(
            all(
                c.interpretation.status == InterpretationStatus.PENDING
                for c in run.case.claims
                if not c.id.startswith('CLAIM_MET_')
            )
        )

    def test_natural_gas_uses_its_own_method_and_never_equity_pe(self):
        run = self.run_ask("천연가스 지금 들어갈 만해?")
        self.assertEqual([m["id"] for m in run.input["methods"]], ["NATGAS"])
        self.assertEqual({s.id for s in run.case.sources}, set(METHODS["NATGAS"].source_ids) | {"S_FX"})
        self.assertFalse(any(m.method == "earnings_yield_v1" for m in run.result.metrics))

    def test_compare_runs_independent_us_earnings_and_treasury_calculations(self):
        run = self.run_ask("S&P500이랑 미국 국채 비교해줘")
        self.assertEqual(list(run.input["plan"]["modes"]), [Mode.COMPARE])
        self.assertIsNone(run.opportunity)
        self.assertIsNotNone(run.deep)
        values = {m.id: m.value for m in run.result.metrics}
        self.assertEqual(values["CALC_EY"], Decimal("5"))
        self.assertEqual(values["CALC_GAP"], Decimal("2"))
        report = render_ask_report(run)
        self.assertIn("대안을 비교하면", report)
        self.assertIn("동일한 미래 수익률이 아니다", report)

    def test_incompatible_assets_keep_common_decision_criteria_and_local_property_gap(self):
        run = self.run_ask("Bitcoin vs 동탄 아파트")
        self.assertEqual(list(run.input["plan"]["modes"]), [Mode.COMPARE])
        self.assertEqual({m["family"] for m in run.input["methods"]}, {"crypto", "real_estate"})
        self.assertFalse(any("earnings_yield" in m.method for m in run.result.metrics))
        self.assertIn("개별 아파트", render_ask_report(run))
        self.assertEqual(research_status(run), "partial")

    def test_portfolio_without_actual_information_creates_input_gap_report_and_no_http(self):
        run = self.run_ask("내 포트폴리오 괜찮아?")
        self.assertEqual(list(run.input["plan"]["modes"]), [Mode.PORTFOLIO_REVIEW])
        self.assertEqual(research_status(run), "needs_input")
        self.assertEqual(self.requests, [])
        self.assertEqual(run.result.metrics, ())
        self.assertIn("실제 보유 내역과 재무 제약이 없어", render_ask_report(run))
        self.assertEqual(research_status(replay_ask(run.directory)), "needs_input")

    def test_portfolio_known_composition_is_calculated_but_not_optimal_allocation(self):
        run = self.run_ask("내 포트폴리오 괜찮아?", portfolio=portfolio_data())
        values = {m.id: m.value for m in run.portfolio.metrics}
        self.assertEqual(values["PORT_TOTAL"], Decimal("10000000"))
        self.assertEqual(values["PORT_WEIGHT_STOCK"], Decimal("60"))
        self.assertEqual(values["PORT_WEIGHT_COIN"], Decimal("20"))
        self.assertEqual(values["PORT_WEIGHT_CASH"], Decimal("20"))
        self.assertEqual(values["PORT_NET_ASSETS"], Decimal("9000000"))
        self.assertEqual(values["PORT_CASH_NEEDS"], Decimal("3000000"))
        self.assertEqual(run.portfolio.largest_ids, ("STOCK",))
        self.assertEqual(run.case.profile.fields['monthly_investment'].value, '500000')
        self.assertEqual(run.case.profile.fields['total_assets'].value, '10000000')
        self.assertEqual(run.case.profile.fields['portfolio_allocation'].status, 'self_reported')
        self.assertFalse(
            any(
                note.startswith(
                    ('총자산이 미확인', '현재 포트폴리오 배분과 보유범위가 미확인', '월 추가 투자 가능액이 미확인')
                )
                for note in run.result.constraints
            )
        )
        self.assertTrue(any('위험 감당 능력이 미확인' in note for note in run.result.constraints))
        self.assertIn("전체 포트폴리오의 안전성을 증명하지는", render_ask_report(run))
        self.assertEqual({m["id"] for m in run.input["methods"]}, {"US_EQUITY", "BTC"})

    def test_unknown_portfolio_values_are_not_replaced_with_zero(self):
        data = portfolio_data(
            cash_krw=None, debt_krw=None, monthly_investable_krw=None, future_cash_needs=None, horizon_months=None
        )
        run = self.run_ask("내 포트폴리오 괜찮아?", portfolio=data)
        self.assertEqual(run.portfolio.metrics, ())
        self.assertIsNone(run.case.profile.fields["debt"].value)
        self.assertIn("부채", run.portfolio.missing)
        self.assertIn("비중 계산을 보류", render_ask_report(run))
        self.assertNotIn("PORT_DEBT", {e.id for e in run.portfolio.evidence})

    def test_partial_holdings_or_zero_denominator_withhold_portfolio_weights(self):
        partial = review_portfolio(portfolio_data(coverage="partial"), NOW.date())
        self.assertFalse(any(m.method == "portfolio_weight_v1" for m in partial.metrics))
        data = portfolio_data(cash_krw="0")
        for holding in data["holdings"]:
            holding["value_krw"] = "0"
        zero = review_portfolio(data, NOW.date())
        self.assertFalse(any(m.method == "portfolio_weight_v1" for m in zero.metrics))
        self.assertTrue(zero.missing)

    def test_explicit_complete_cash_only_portfolio_is_not_treated_as_unknown_holdings(self):
        portfolio = review_portfolio(portfolio_data(holdings=[], cash_krw='10000000'), NOW.date())
        values = {m.id: m.value for m in portfolio.metrics}
        self.assertEqual(values['PORT_TOTAL'], Decimal('10000000'))
        self.assertEqual(values['PORT_WEIGHT_CASH'], Decimal('100'))
        self.assertEqual(portfolio.status, 'completed_composition')

    def test_future_portfolio_is_blocked_before_acquisition(self):
        with self.assertRaisesRegex(SourceError, 'after the research cutoff'):
            self.run_ask('내 포트폴리오 괜찮아?', portfolio=portfolio_data(as_of='2026-09-11'))
        self.assertEqual(self.requests, [])

    def test_unregistered_holding_keeps_composition_but_discloses_market_research_gap(self):
        data = portfolio_data(holdings=[dict(id='UNKNOWN', name='SK하이닉스', value_krw='8000000')])
        run = self.run_ask('내 포트폴리오 괜찮아?', portfolio=data)
        self.assertTrue(run.portfolio.metrics)
        self.assertEqual(run.input['methods'], [])
        self.assertEqual(self.requests, [])
        self.assertIn('SK하이닉스', run.input['tasks'][0]['unsupported'])
        self.assertIn('완전히 계산하지 않았다', render_ask_report(run))

    def test_combined_scan_and_direct_deep_dives_share_sources(self):
        run = self.run_ask("전체 시장 보고 천연가스랑 한국 반도체는 깊게 봐줘.")
        self.assertEqual(list(run.input["plan"]["modes"]), [Mode.OPPORTUNITY_SCAN, Mode.ASSET_DEEP_DIVE])
        tasks = [t for t in run.input["tasks"] if t["mode"] == Mode.ASSET_DEEP_DIVE]
        self.assertEqual([t["method_ids"] for t in tasks], [["NATGAS"], ["KR_EQUITY"]])
        self.assertEqual(len(self.requests), len(set(self.requests)))
        report = render_ask_report(run)
        self.assertIn("천연가스를 어떻게", report)
        self.assertIn("한국 주식 / 반도체를 어떻게", report)

    def test_combined_portfolio_compare_does_not_add_a_scan_or_unrequested_deep_dive(self):
        run = self.run_ask(
            "내 포트폴리오 보고 신규자금은 국채랑 S&P500 중 어디가 나은지 봐줘.", portfolio=portfolio_data()
        )
        self.assertEqual(list(run.input["plan"]["modes"]), [Mode.PORTFOLIO_REVIEW, Mode.COMPARE])
        self.assertIsNone(run.opportunity)
        self.assertIn("대안을 비교하면", render_ask_report(run))
        self.assertIn("내 보유에 적용할", render_ask_report(run))

    def test_conditional_candidate_deep_dive_is_not_fabricated(self):
        run = self.run_ask("요즘 투자할 곳 찾아보고 가장 유망한 두 개를 깊게 분석해줘.")
        self.assertTrue(run.input["tasks"][-1]["candidate_dependent"])
        self.assertIn("자동 후속 조사는 수행하지 않았다", render_ask_report(run))

    def test_unsupported_solana_or_korean_treasury_never_substitutes_bitcoin_or_us_treasury(self):
        for question in (
            "Solana 지금 어때?",
            "한국 국채 지금 어때?",
            "한국 단기 국채 지금 어때?",
            "한국의 장기 국채 지금 어때?",
        ):
            with self.subTest(question=question):
                run = self.run_ask(question)
                self.assertEqual(run.input["methods"], [])
                self.assertEqual(research_status(run), "unsupported")
                self.assertEqual(self.requests, [])
                self.assertIn("연결이 없다", render_ask_report(run))

    def test_company_compare_does_not_replace_missing_hynix_with_samsung_data(self):
        run = self.run_ask("삼성전자랑 SK하이닉스 비교해줘.")
        self.assertEqual([m["id"] for m in run.input["methods"]], ["SAMSUNG"])
        self.assertEqual(run.input["tasks"][0]["unsupported"], ["SK하이닉스"])
        self.assertEqual({s.id for s in run.case.sources}, {"KR_SAMSUNG_2026Q2_RESULTS"})

    def test_existing_acquisition_and_verification_functions_are_actually_called(self):
        from investment_research import orchestrator

        with (
            patch.object(orchestrator, "acquire_plan", wraps=orchestrator.acquire_plan) as sources,
            patch.object(orchestrator, "acquire_macro", wraps=orchestrator.acquire_macro) as macro,
            patch.object(orchestrator, "replay_opportunity", wraps=orchestrator.replay_opportunity) as verification,
            patch.object(orchestrator, "run_research", wraps=orchestrator.run_research) as engine,
        ):
            self.run_ask("BTC 지금 어때?")
        sources.assert_called_once()
        macro.assert_called_once()
        verification.assert_called_once()
        engine.assert_called_once()

    def test_scoped_source_projection_preserves_origin_chain_and_deduplicates_shared_sources(self):
        child = next(s for s in self.catalog.sources['sources'] if s['id'] == 'CR_COINSHARES_CURRENT_FLOWS')
        child['origin_source_id'] = 'CR_IBIT_ISSUER'
        run = self.run_ask('Bitcoin vs Ethereum')
        sources = {s.id: s for s in run.case.sources}
        self.assertEqual(sources['CR_COINSHARES_CURRENT_FLOWS'].origin_source_id, 'CR_IBIT_ISSUER')
        self.assertEqual(len(self.requests), len(set(self.requests)))
        self.assertEqual(
            set(
                next(
                    s
                    for s in json.loads((run.directory / 'source_plan.json').read_text())['sources']
                    if s['id'] == 'CR_IBIT_ISSUER'
                )['asset_ids']
            ),
            {'BTC', 'ETH'},
        )

    def test_evidence_claim_calculation_and_reasoning_traceability_and_report_links(self):
        run = self.run_ask("S&P500 vs 미국 국채")
        data = self.manifest(run)
        report = render_ask_report(run)
        evidence = {e["id"]: e for e in data["evidence_used"]}
        sources = {s["id"]: s for s in data["sources_accessed"]}
        self.assertTrue(data["claims_evaluated"])
        self.assertTrue(data["reasoning"])
        for item in evidence.values():
            self.assertIn(item["source_id"], sources)
            if item["provenance"]:
                self.assertEqual(item["provenance"]["match_status"], "matched")
                self.assertTrue(item["provenance"]["snapshot_id"])
        for calculation in data["calculations"]:
            self.assertTrue(set(calculation["input_ids"]) <= evidence.keys())
        for claim in data["claims_evaluated"]:
            self.assertTrue(set(claim["support_ids"] + claim["counter_ids"] + claim["context_ids"]) <= evidence.keys())
            if not claim['id'].startswith('CLAIM_MET_'):
                self.assertEqual(claim["interpretation"]["status"], "pending")
        anchors = set(re.findall(r'<a id="([^"]+)"', report))
        self.assertTrue(set(re.findall(r'\]\(#([^)]+)\)', report)) <= anchors)

    def test_bounded_findings_are_evidence_linked_drafts_and_include_macro_view_text_in_appendix(self):
        data = deepcopy(self.catalog.sources)
        entry = next(e for e in data['evidence'] if e['source_id'] == 'CR_IBIT_ISSUER')
        entry['view'] = 'macro'  # A qualitative macro-view excerpt, not a time series.
        source = next(s for s in data['sources'] if s['id'] == entry['source_id'])
        fingerprint = _digest({'text': source['excerpts'][0]['quote'], 'definition': entry['definition']})
        finding = dict(
            id='SYNTHETIC_FINDING',
            asset_ids=['BTC'],
            evidence_ids=[entry['id']],
            fingerprints={entry['id']: fingerprint},
            text='합성 발행사의 설명은 가격 매력의 증거가 아니다.',
            counterargument='합성 반대 질문이다.',
            reassessment='합성 후속 조건이다.',
            role='interpretation_draft',
        )
        self.catalog = replace(self.catalog, sources=data, findings=(finding,))
        run = self.run_ask('BTC 지금 어때?')
        report = render_ask_report(run)
        self.assertEqual(run.findings[0]['status'], 'available_draft')
        self.assertIn(finding['text'], report)
        claim = next(c for c in run.case.claims if c.id == 'ASK_FINDING_SYNTHETIC_FINDING')
        self.assertEqual(claim.verification, VerificationStatus.UNVERIFIED)
        self.assertEqual(claim.interpretation.status, InterpretationStatus.PENDING)
        used = {e['id'] for e in self.manifest(run)['evidence_used']}
        self.assertIn(entry['id'], used)
        anchors = set(re.findall(r'<a id="([^"]+)"', report))
        self.assertTrue(set(re.findall(r'\]\(#([^)]+)\)', report)) <= anchors)
        self.assertEqual(render_ask_report(replay_ask(run.directory)), report)

        # Even a newly matched source cannot inherit the interpretation attached
        # to a different excerpt: exact semantic input fingerprints must agree.
        source['excerpts'][0]['quote'] = 'Changed synthetic issuer wording.'
        self.documents[source['url']] = FetchResponse(b'<p>Changed synthetic issuer wording.</p>', 'text/html')
        changed = self.run_ask('BTC 지금 어때?')
        self.assertEqual(changed.findings[0]['status'], 'withheld')
        self.assertNotIn(finding['text'], render_ask_report(changed))

    def test_community_occurrence_cannot_activate_a_factual_finding(self):
        entry = next(
            e
            for e in self.catalog.sources['evidence']
            if e['kind'] == 'observed_narrative' and e['source_id'] in METHODS['BTC'].source_ids
        )
        source = next(s for s in self.catalog.sources['sources'] if s['id'] == entry['source_id'])
        finding = dict(
            id='NARRATIVE_TRUTH',
            asset_ids=['BTC'],
            evidence_ids=[entry['id']],
            fingerprints={
                entry['id']: _digest({'text': source['excerpts'][0]['quote'], 'definition': entry['definition']})
            },
            text='채택해서는 안 되는 합성 사실 주장.',
            counterargument='내용은 미확인이다.',
            reassessment='원자료 필요.',
            role='interpretation_draft',
        )
        self.catalog = replace(self.catalog, findings=(finding,))
        run = self.run_ask('BTC 지금 어때?')
        self.assertEqual(run.findings[0]['status'], 'withheld')
        self.assertNotIn(finding['text'], render_ask_report(run))

    def test_replay_is_byte_identical_offline_and_independent_of_decimal_context(self):
        run = self.run_ask("S&P500 vs 미국 국채")
        before = {str(p.relative_to(run.directory)): p.read_bytes() for p in run.directory.rglob("*") if p.is_file()}
        self.requests.clear()
        with (
            patch("investment_research.orchestrator.acquire_plan", side_effect=AssertionError("no replay acquisition")),
            patch("investment_research.orchestrator.acquire_macro", side_effect=AssertionError("no replay macro")),
            localcontext() as context,
        ):
            context.prec = 3
            replayed = replay_ask(run.directory)
        self.assertEqual(run.digest, replayed.digest)
        self.assertEqual(render_ask_report(run), render_ask_report(replayed))
        self.assertEqual(
            before, {str(p.relative_to(run.directory)): p.read_bytes() for p in run.directory.rglob("*") if p.is_file()}
        )
        self.assertEqual(self.requests, [])

    def test_replay_rejects_changed_inputs_artifacts_question_or_method_versions(self):
        run = self.run_ask("BTC 지금 어때?")
        with self.assertRaisesRegex(SourceError, "original question"):
            replay_ask(run.directory, question="ETH 지금 어때?")
        path = run.directory / "report.md"
        original = path.read_bytes()
        path.write_text("changed")
        with self.assertRaisesRegex(SourceError, "checksum"):
            replay_ask(run.directory)
        path.write_bytes(original)
        path = run.directory / "input.json"
        original = path.read_bytes()
        data = json.loads(original)
        data["method_versions"]["orchestrator"] = "unknown"
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(SourceError, "method versions"):
            replay_ask(run.directory)
        path.write_bytes(original)

    def test_source_failure_is_partial_research_with_recorded_status_not_faked_evidence(self):
        url = next(s["url"] for s in self.catalog.sources["sources"] if s["id"] == "CR_IBIT_ISSUER")
        self.documents[url] = TimeoutError("authored fixture timeout")
        run = self.run_ask("BTC 지금 어때?")
        source = next(s for s in run.case.sources if s.id == "CR_IBIT_ISSUER")
        self.assertEqual(source.provenance.status, "timeout")
        self.assertFalse(any(e.source_id == source.id for e in run.case.evidence))
        self.assertIn("시간 초과", render_ask_report(run))
        self.assertEqual(self.manifest(run)["execution_status"], "completed")
        self.assertEqual(research_status(run), "partial")

    def test_stale_or_future_numeric_sources_do_not_produce_current_financial_metrics(self):
        for timestamp in ("2026-08-01T11:00:00Z", "2026-09-11T11:00:00Z"):
            with self.subTest(timestamp=timestamp):
                catalog = deepcopy(self.catalog)
                for source in catalog.sources["sources"]:
                    source["observed_at"] = timestamp
                    source["published_at"] = timestamp
                    source["valid_as_of"] = timestamp[:10]
                self.sequence += 1
                run = execute_ask(
                    "S&P500 지금 어때?",
                    self.directory / str(self.sequence),
                    catalog=catalog,
                    now=NOW,
                    fetcher=self.fetcher,
                )
                self.assertFalse(any(m.id in {"CALC_EY", "CALC_GAP"} for m in run.result.metrics))
                self.assertNotIn("Forward P/E 20.0", render_ask_report(run).split("## 근거와 판단을 직접 확인하기")[0])

    def test_cli_default_executes_and_prints_report_path_and_replay_works_offline(self):
        root = self.directory / "cli"
        stdout = StringIO()
        stderr = StringIO()

        def execute(question, directory, **kwargs):
            return execute_ask(question, directory, catalog=self.catalog, fetcher=self.fetcher, now=NOW, **kwargs)

        with (
            patch("investment_research.orchestrator.execute_ask", side_effect=execute),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            self.assertEqual(main(["ask", "BTC 지금 어때?", "--run-dir", str(root)]), 0)
        self.assertTrue(stdout.getvalue().startswith("# 투자 질문"))
        self.assertIn(str(root / "report.md"), stderr.getvalue())
        stdout = StringIO()
        with redirect_stdout(stdout), redirect_stderr(StringIO()):
            self.assertEqual(main(["ask", "--replay", str(root)]), 0)
        self.assertEqual(stdout.getvalue(), (root / "report.md").read_text())

    def test_cli_preflight_and_plan_only_never_acquire_or_overwrite_inputs(self):
        output = self.directory / "protected.md"
        output.write_text("user content")
        with (
            redirect_stdout(StringIO()),
            redirect_stderr(StringIO()),
            patch("investment_research.orchestrator.execute_ask", side_effect=AssertionError("no acquisition")),
        ):
            self.assertEqual(main(["ask", "BTC 지금 어때?", "--output", str(output)]), 2)
            self.assertEqual(main(["ask", "BTC 지금 어때?", "--plan-only"]), 0)
            self.assertEqual(main(["ask", "BTC 지금 어때?", "--plan-only", "--portfolio", str(output)]), 2)
        self.assertEqual(output.read_text(), "user content")

    def test_existing_run_directory_is_immutable_and_not_reused_for_new_acquisition(self):
        run = self.run_ask("BTC 지금 어때?")
        self.requests.clear()
        with self.assertRaisesRegex(SourceError, "already exists"):
            execute_ask("BTC 지금 어때?", run.directory, catalog=self.catalog, fetcher=self.fetcher, now=NOW)
        self.assertEqual(self.requests, [])

    def test_invalid_unknown_or_foreign_portfolio_inputs_and_future_date_are_rejected(self):
        cases = [
            portfolio_data(base_currency="USD"),
            portfolio_data(cash_krw="-1"),
            portfolio_data(cash_krw="NaN"),
            portfolio_data(horizon_months=True),
            portfolio_data(coverage="guessed"),
        ]
        for data in cases:
            with self.subTest(data=data), self.assertRaises(SourceError):
                validate_portfolio(data)
        with self.assertRaisesRegex(SourceError, "after the research cutoff"):
            review_portfolio(portfolio_data(as_of="2026-09-11"), NOW.date())

    def test_unresolved_intent_does_not_launch_broad_market_research(self):
        run = self.run_ask("어떻게 생각해?")
        self.assertEqual(self.requests, [])
        self.assertEqual(research_status(run), "needs_clarification")
        self.assertIn("먼저 확인할 질문", render_ask_report(run))
