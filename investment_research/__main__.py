"""Explicit acquisition and offline research; never silently overwrite user files."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from . import __version__
from .engine import ENGINE_VERSION, REPORT_VERSION, run_research
from .models import ResearchResult
from .report import render_report
from .sources import SourceError
from .validation import InputValidationError, _date, case_file, load_case


def manifest_for(result: ResearchResult, report: str) -> dict:
    code = hashlib.sha256()
    for file in sorted(Path(__file__).parent.glob("*.py")):
        code.update(file.name.encode("utf-8"))
        code.update(b"\0")
        code.update(file.read_bytes())
        code.update(b"\0")
    manifest = {
        "schema_version": result.case.schema_version,
        "synthetic": result.case.synthetic,
        "input_sha256": result.case.input_digest,
        "run_id": result.run_id,
        "version": __version__,
        "method_versions": {
            "engine": ENGINE_VERSION,
            "report": REPORT_VERSION,
            "calculation": "rate_difference_v1",
        },
        "code_sha256": code.hexdigest(),
        "report_sha256": hashlib.sha256(report.encode("utf-8")).hexdigest(),
        "run_status": result.run_status,
        "conclusion": result.conclusion,
        "personal_conclusion": result.personal_conclusion,
        "metrics": [
            {
                "id": m.id,
                "label": m.label,
                "value": str(m.value),
                "unit": m.unit,
                "method": m.method,
                "input_ids": list(m.input_ids),
                "asset_ids": list(m.asset_ids),
                "limitations": list(m.limitations),
            }
            for m in result.metrics
        ],
        "claims": [
            {
                "id": c.id,
                "verification": c.verification.value,
                "interpretation_status": c.interpretation.status.value,
                "support_ids": list(c.support_ids),
                "counter_ids": list(c.counter_ids),
                "narrative_evidence_id": c.narrative_evidence_id,
            }
            for c in result.case.claims
        ],
    }
    if result.case.source_verification:
        from .source_pipeline import PIPELINE_VERSION
        from .sources import SOURCE_VERSION

        manifest["method_versions"].update({"source_acquisition": SOURCE_VERSION, "source_pipeline": PIPELINE_VERSION})
        manifest["source_snapshots"] = {
            source.id: {
                "snapshot_id": source.provenance.snapshot_id,
                "status": source.provenance.status,
                "freshness": source.provenance.freshness,
                "payload_sha256": source.provenance.payload_sha256,
            }
            for source in result.case.sources
            if source.provenance is not None
        }
        manifest["diagnostics"] = list(result.case.diagnostics)
        for item, claim in zip(manifest["claims"], result.case.claims, strict=True):
            item["context_ids"] = list(claim.context_ids)
    return manifest


def _check_destinations(input_file: Path, writes: list[tuple[Path, str]]) -> None:
    """Preflight every output before creating any of them."""
    resolved = []
    for path, text in writes:
        target = path.resolve()
        if target == input_file.resolve():
            raise InputValidationError("output: 입력 case.json을 덮어쓸 수 없습니다")
        if target in resolved:
            raise InputValidationError("output: 보고서와 실행 기록의 출력 경로가 같습니다")
        resolved.append(target)
        if path.exists():
            if not path.is_file() or path.read_bytes() != text.encode("utf-8"):
                raise InputValidationError("output: 기존 파일이 있습니다. 다른 출력 경로를 사용하세요")


def _write(path: Path, text: str) -> None:
    if path.exists():
        # Preflight checked identical content; check again rather than overwriting.
        if path.is_file() and path.read_bytes() == text.encode("utf-8"):
            return
        raise InputValidationError("output: 기존 파일이 변경되어 쓰기를 중단했습니다")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cross-Asset Research Brief와 공개 출처 검증")
    parser.add_argument("--version", action="version", version=__version__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    ask = subcommands.add_parser("ask", help="자연어 투자 질문을 조사하고 근거가 연결된 한국어 보고서 생성")
    ask.add_argument("question", nargs="?", help="사용자의 자연어 투자 질문; replay는 원래 질문 사용")
    ask.add_argument(
        "--mode",
        action="append",
        choices=["opportunity_scan", "asset_deep_dive", "compare", "portfolio_review"],
        help="명시적 모드가 자동 해석보다 우선; 필요한 조합은 반복 지정",
    )
    ask.add_argument("--plan-only", action="store_true", help="수집 없이 조사 계획 JSON만 확인")
    ask.add_argument("--run-dir", type=Path, help="새 실행 디렉터리; 기본 reports/asks 아래 자동 생성")
    ask.add_argument("--replay", type=Path, help="보존된 ask 실행을 인터넷 없이 검증·재현")
    ask.add_argument("--portfolio", type=Path, help="portfolio-v1 JSON 자기보고 보유·재무 입력")
    ask.add_argument(
        "--context-run", type=Path, help="후보 번호를 참조할 이전 Scan 실행; 후속 조사는 새 자료로 독립 실행"
    )
    ask.add_argument("--previous-scan", type=Path, help="이전 완료 Scan과 같은 정의의 관측 비교; 현재 자료는 새로 획득")
    ask.add_argument("--decision-plan", type=Path, help="등록 가설·시점 보장 이력·자금 제약으로 투자 판단 연결")
    ask.add_argument("--journal", type=Path, help="불변 판단·전략 일지; 이전 사후검증을 현재 판단에 반영")
    ask.add_argument("--output", type=Path, help="Markdown 보고서 사본; plan-only는 계획 JSON")
    invest = subcommands.add_parser("invest", help="투자 판단·과거 검증·일지·사후 성과의 반복 실행")
    invest_commands = invest.add_subparsers(dest="investment_action", required=True)
    invest_run = invest_commands.add_parser("run", help="완료 연구와 등록 전략으로 투자 결론·배분 생성")
    invest_run.add_argument("plan", type=Path)
    invest_run.add_argument("--research-run", type=Path, required=True)
    invest_run.add_argument("--run-dir", type=Path, required=True)
    invest_run.add_argument("--journal", type=Path)
    invest_run.add_argument("--previous-run", type=Path)
    invest_replay = invest_commands.add_parser("replay", help="저장된 투자 판단을 인터넷 없이 검증·재현")
    invest_replay.add_argument("run", type=Path)
    invest_record = invest_commands.add_parser("record", help="검증된 기존 투자 판단을 공용 일지에 보존")
    invest_record.add_argument("--run", type=Path, required=True)
    invest_record.add_argument("--journal", type=Path, required=True)
    invest_review = invest_commands.add_parser("review", help="성숙한 추천의 1주~1년 결과와 전략 상태 평가")
    invest_review.add_argument("--journal", type=Path, required=True)
    invest_review.add_argument("--prices", type=Path, required=True, help="investment-prices-v1 데이터셋의 JSON 배열")
    invest_review.add_argument("--as-of", required=True, help="timezone을 포함한 평가 시각")
    invest_review.add_argument("--run-dir", type=Path, required=True)
    research = subcommands.add_parser("research", help="로컬 합성 JSON 자료로 한국어 보고서 생성")
    research.add_argument("case", type=Path, help="case.json 또는 그 파일을 포함한 디렉터리")
    research.add_argument("--output", type=Path, help="Markdown 파일 경로; 생략하면 표준 출력")
    research.add_argument("--manifest", type=Path, help="재현 정보 JSON 파일 경로")
    sources = subcommands.add_parser("sources", help="명시적인 공개 자료 획득 또는 로컬 snapshot 검증")
    source_commands = sources.add_subparsers(dest="source_command", required=True)
    acquire = source_commands.add_parser("acquire", help="계획에 지정한 소수 URL을 획득하고 snapshot을 보존")
    acquire.add_argument("plan", type=Path, help="plan.json 또는 그 파일을 포함한 디렉터리")
    acquire.add_argument("--store", type=Path, required=True, help="불변 snapshot 저장 디렉터리")
    acquire.add_argument("--pins", type=Path, required=True, help="이번 획득의 snapshot ID 기록; 새 경로 필요")
    replay = source_commands.add_parser("replay", help="고정 snapshot을 검증하고 기존 근거 모델로 보고서 생성")
    replay.add_argument("plan", type=Path, help="plan.json 또는 그 파일을 포함한 디렉터리")
    replay.add_argument("--store", type=Path, required=True)
    replay.add_argument("--pins", type=Path, required=True)
    replay.add_argument("--as-of", help="최신성 판단 기준 YYYY-MM-DD; 생략하면 계획의 기준일")
    replay.add_argument("--output", type=Path, help="Markdown 파일; 생략하면 표준 출력")
    replay.add_argument("--manifest", type=Path, help="재현 정보 JSON 파일")
    macro = subcommands.add_parser("macro", help="실제 거시 시계열과 한국어 Macro Regime Snapshot")
    macro_commands = macro.add_subparsers(dest="macro_command", required=True)
    macro_acquire = macro_commands.add_parser("acquire", help="검토한 공식 거시 자료를 확보하고 판본을 보존")
    macro_acquire.add_argument("plan", type=Path)
    macro_acquire.add_argument("--store", type=Path, required=True)
    macro_acquire.add_argument("--pins", type=Path, required=True)
    macro_acquire.add_argument("--previous-pins", type=Path, help="같은 계획의 기존 판본을 새 pins에 함께 보존")
    macro_replay = macro_commands.add_parser("replay", help="네트워크 없이 거시 상태와 근거를 재현")
    macro_replay.add_argument("plan", type=Path)
    macro_replay.add_argument("--store", type=Path, required=True)
    macro_replay.add_argument("--pins", type=Path, required=True)
    macro_replay.add_argument("--as-of", help="YYYY-MM-DD(UTC 일말) 또는 timezone을 포함한 ISO timestamp")
    macro_replay.add_argument("--output", type=Path)
    macro_replay.add_argument("--manifest", type=Path)
    opportunity = subcommands.add_parser("opportunity", help="고정 실제 자료로 자산 간 조사 우선순위 지도 재생")
    opportunity_commands = opportunity.add_subparsers(dest="opportunity_command", required=True)
    opportunity_replay = opportunity_commands.add_parser(
        "replay", help="출처·거시·연구 초안을 기존 모델로 연결; 네트워크 없음"
    )
    opportunity_replay.add_argument("review", type=Path, help="review.json 또는 그 디렉터리")
    opportunity_replay.add_argument("--plan", type=Path, required=True, help="검토한 source plan")
    opportunity_replay.add_argument("--store", type=Path, required=True)
    opportunity_replay.add_argument("--pins", type=Path, required=True)
    opportunity_replay.add_argument("--macro-plan", type=Path, required=True)
    opportunity_replay.add_argument("--macro-store", type=Path, required=True)
    opportunity_replay.add_argument("--macro-pins", type=Path, required=True)
    opportunity_replay.add_argument("--output", type=Path)
    opportunity_replay.add_argument("--manifest", type=Path)
    deep = subcommands.add_parser("deep-dive", help="미국 주식 Deep Dive 재생; Opportunity Map은 선택적 맥락")
    deep_commands = deep.add_subparsers(dest="deep_command", required=True)
    deep_replay = deep_commands.add_parser("replay", help="원문 숫자·명시적 계산·해석 초안 연결; 네트워크 없음")
    deep_replay.add_argument("review", type=Path)
    for flag in ("plan", "store", "pins", "macro-plan", "macro-store", "macro-pins"):
        deep_replay.add_argument("--" + flag, type=Path, required=True)
    parent_flags = (
        "parent-review",
        "parent-plan",
        "parent-store",
        "parent-pins",
        "parent-macro-plan",
        "parent-macro-store",
        "parent-macro-pins",
    )
    for flag in parent_flags:
        deep_replay.add_argument("--" + flag, type=Path, help="선택적 이전 맥락; 연결하려면 부모 관련 옵션 모두 지정")
    deep_replay.add_argument("--output", type=Path)
    deep_replay.add_argument("--manifest", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "invest":
            from .decision_data import load, save
            from .decision_report import render_decision, render_review
            from .investment_cycle import run_cycle, replay_cycle
            from .decision_journal import record, review, persist_review

            if args.investment_action == "run":
                result = run_cycle(
                    load(args.plan), args.research_run, args.run_dir, ledger=args.journal, previous=args.previous_run
                )
                sys.stdout.write(render_decision(result))
            elif args.investment_action == "replay":
                sys.stdout.write(render_decision(replay_cycle(args.run)))
            elif args.investment_action == "record":
                if (args.run / 'investment_decision.json').exists():
                    from .orchestrator import replay_ask

                    result = replay_ask(args.run).investment
                else:
                    result = replay_cycle(args.run)
                if result is None:
                    raise SourceError('run has no investment judgment')
                record(args.journal, result)
                print('투자 판단을 불변 일지에 보존했습니다.')
            else:
                if args.run_dir.exists():
                    raise SourceError('use a new review run directory')
                result = review(args.journal, load(args.prices), args.as_of)
                report = render_review(result)
                save(args.run_dir / 'review.json', result)
                (args.run_dir / 'report.md').write_text(report, encoding='utf-8')
                persist_review(args.journal, result)
                sys.stdout.write(report)
            return 0
        if args.command == "ask":
            from .routing import plan_research

            if args.plan_only:
                if (
                    args.replay
                    or args.run_dir
                    or args.portfolio
                    or args.context_run
                    or args.previous_scan
                    or args.decision_plan
                    or args.journal
                ):
                    raise InputValidationError("plan-only: 실행·replay·보유 입력 옵션을 함께 사용할 수 없습니다")
                text = (
                    json.dumps(plan_research(args.question, modes=args.mode).to_dict(), ensure_ascii=False, indent=2)
                    + "\n"
                )
                if args.output is None:
                    sys.stdout.write(text)
                else:
                    if args.output.exists() and (
                        not args.output.is_file() or args.output.read_bytes() != text.encode("utf-8")
                    ):
                        raise InputValidationError("output: 기존 파일이 있습니다. 다른 출력 경로를 사용하세요")
                    _write(args.output, text)
                return 0

            from .orchestrator import execute_ask, replay_ask
            from .orchestrator_report import render_ask_report
            from .portfolio import load_portfolio

            if args.replay:
                if (
                    args.mode
                    or args.run_dir
                    or args.portfolio
                    or args.context_run
                    or args.previous_scan
                    or args.decision_plan
                    or args.journal
                ):
                    raise InputValidationError(
                        "replay: 원래 모드·보유·실행 입력을 보존합니다. 변경은 새 ask로 실행하세요"
                    )
                run = replay_ask(args.replay, question=args.question)
                if (
                    args.output
                    and args.output.resolve().is_relative_to(args.replay.resolve())
                    and args.output.resolve() != (args.replay / "report.md").resolve()
                ):
                    raise InputValidationError("output: replay 입력과 실행 기록 안에 새 출력 파일을 넣을 수 없습니다")
            else:
                # Resolve/validate inputs and destinations before any HTTP request.
                plan_research(args.question, modes=args.mode)
                portfolio = load_portfolio(args.portfolio) if args.portfolio else None
                from .decision_data import load as load_decision, validate_plan

                decision_plan = validate_plan(load_decision(args.decision_plan)) if args.decision_plan else None
                root = args.run_dir or Path("reports/asks") / (
                    datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
                    + "_"
                    + hashlib.sha256(args.question.encode()).hexdigest()[:10]
                )
                if args.output and (args.output.exists() or args.output.resolve().is_relative_to(root.resolve())):
                    raise InputValidationError(
                        "output: 새 실행 밖의 새 보고서 사본 경로를 사용하세요; 기본 보고서는 run-dir/report.md입니다"
                    )
                if args.portfolio and (
                    args.portfolio.resolve().is_relative_to(root.resolve())
                    or args.output
                    and args.output.resolve() == args.portfolio.resolve()
                ):
                    raise InputValidationError("output: 보유 입력을 실행 출력으로 덮어쓸 수 없습니다")
                if args.decision_plan and (
                    args.decision_plan.resolve().is_relative_to(root.resolve())
                    or args.output
                    and args.output.resolve() == args.decision_plan.resolve()
                ):
                    raise InputValidationError('output: 투자 전략 입력을 출력으로 덮어쓸 수 없습니다')
                run = execute_ask(
                    args.question,
                    root,
                    modes=args.mode,
                    portfolio=portfolio,
                    context_run=args.context_run,
                    previous_scan=args.previous_scan,
                    decision_plan=decision_plan,
                    decision_journal=args.journal,
                    progress=lambda message: print("자료 확인: " + message, file=sys.stderr, flush=True),
                )
            text = render_ask_report(run)
            if args.output is None:
                sys.stdout.write(text)
            else:
                _write(args.output, text)
            print(f"보고서: {run.directory / 'report.md'}", file=sys.stderr)
            print(f"실행 기록: {run.directory / 'run_manifest.json'}", file=sys.stderr)
            return 0
        if args.command == "deep-dive":
            from .deep_dive import deep_dive_manifest, load_deep_dive_review, replay_deep_dive
            from .deep_dive_report import render_deep_dive_report
            from .macro_pipeline import load_macro_plan
            from .opportunity import load_opportunity_review, replay_opportunity
            from .source_pipeline import load_pins, load_source_plan

            parent_paths = [getattr(args, flag.replace("-", "_")) for flag in parent_flags]
            if any(path is not None for path in parent_paths) and not all(path is not None for path in parent_paths):
                raise InputValidationError("parent: 이전 맥락을 연결하려면 모든 부모 옵션을 지정해야 합니다")
            parent = None
            if args.parent_review is not None:
                parent = replay_opportunity(
                    load_opportunity_review(args.parent_review),
                    load_source_plan(args.parent_plan),
                    args.parent_store,
                    load_pins(args.parent_pins),
                    load_macro_plan(args.parent_macro_plan),
                    args.parent_macro_store,
                    load_pins(args.parent_macro_pins),
                )
            review = load_deep_dive_review(args.review)
            run = replay_deep_dive(
                review,
                load_source_plan(args.plan),
                args.store,
                load_pins(args.pins),
                load_macro_plan(args.macro_plan),
                args.macro_store,
                load_pins(args.macro_pins),
                parent,
            )
            report = render_deep_dive_report(run)
            writes = []
            if args.output is not None:
                writes.append((args.output, report))
            if args.manifest is not None:
                writes.append(
                    (
                        args.manifest,
                        json.dumps(deep_dive_manifest(run, report), ensure_ascii=False, sort_keys=True, indent=2)
                        + "\n",
                    )
                )
            input_file = args.review / "review.json" if args.review.is_dir() else args.review
            protected = [input_file, args.pins, args.macro_pins]
            if parent is not None:
                protected.extend(
                    [
                        args.parent_pins,
                        args.parent_macro_pins,
                        args.parent_review / "review.json" if args.parent_review.is_dir() else args.parent_review,
                    ]
                )
            protected.extend(
                path / "plan.json" if path.is_dir() else path
                for path in (args.plan, args.macro_plan, args.parent_plan, args.parent_macro_plan)
                if path is not None
            )
            stores = tuple(
                path
                for path in (args.store, args.macro_store, args.parent_store, args.parent_macro_store)
                if path is not None
            )
            if any(
                path.resolve() in {p.resolve() for p in protected}
                or any(path.resolve().is_relative_to(store.resolve()) for store in stores)
                for path, _ in writes
            ):
                raise InputValidationError("output: 초안·계획·pins·snapshot 입력을 덮어쓸 수 없습니다")
            _check_destinations(input_file, writes)
            for path, value in writes:
                _write(path, value)
            if args.output is None:
                sys.stdout.write(report)
            return 0
        if args.command == "opportunity":
            from .macro_pipeline import load_macro_plan
            from .opportunity import load_opportunity_review, opportunity_manifest, replay_opportunity
            from .opportunity_report import render_opportunity_report
            from .source_pipeline import load_pins, load_source_plan

            review = load_opportunity_review(args.review)
            run = replay_opportunity(
                review,
                load_source_plan(args.plan),
                args.store,
                load_pins(args.pins),
                load_macro_plan(args.macro_plan),
                args.macro_store,
                load_pins(args.macro_pins),
            )
            report = render_opportunity_report(run)
            input_file = args.review / "review.json" if args.review.is_dir() else args.review
            writes = []
            if args.output is not None:
                writes.append((args.output, report))
            if args.manifest is not None:
                writes.append(
                    (
                        args.manifest,
                        json.dumps(opportunity_manifest(run, report), ensure_ascii=False, sort_keys=True, indent=2)
                        + "\n",
                    )
                )
            protected = [
                input_file,
                args.plan / "plan.json" if args.plan.is_dir() else args.plan,
                args.pins,
                args.macro_plan / "plan.json" if args.macro_plan.is_dir() else args.macro_plan,
                args.macro_pins,
            ]
            if any(path.resolve() in {item.resolve() for item in protected} for path, _ in writes):
                raise InputValidationError("output: 연구 초안·계획·pins 입력 파일을 덮어쓸 수 없습니다")
            _check_destinations(input_file, writes)
            for path, value in writes:
                _write(path, value)
            if args.output is None:
                sys.stdout.write(report)
            return 0
        if args.command == "macro":
            from .macro_pipeline import acquire_macro, load_macro_plan, macro_manifest, replay_macro
            from .macro_report import render_macro_report
            from .source_pipeline import load_pins
            from .sources import _time, load_snapshot

            plan = load_macro_plan(args.plan)
            input_file = args.plan / "plan.json" if args.plan.is_dir() else args.plan
            if args.macro_command == "acquire":
                if args.pins.exists() or args.pins.resolve() == input_file.resolve():
                    raise InputValidationError("pins: 새 경로를 사용해야 기존 자료를 보존합니다")
                previous = load_pins(args.previous_pins) if args.previous_pins else None
                pins = acquire_macro(plan, args.store, previous_pins=previous)
                text = json.dumps(pins, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
                _check_destinations(input_file, [(args.pins, text)])
                _write(args.pins, text)
                statuses = {
                    key: load_snapshot(args.store, key, values[-1]).status for key, values in pins["snapshots"].items()
                }
                print(f"거시 획득 기록: {args.pins}")
                for source_id, status in statuses.items():
                    print(f"{source_id}: {status}")
                return 0 if statuses and all(value == "available" for value in statuses.values()) else 1
            as_of = (
                None
                if args.as_of is None
                else (_date(args.as_of, "as_of") if len(args.as_of) == 10 else _time(args.as_of))
            )
            run = replay_macro(plan, args.store, load_pins(args.pins), as_of=as_of)
            report = render_macro_report(run)
            writes = []
            if args.output is not None:
                writes.append((args.output, report))
            if args.manifest is not None:
                writes.append(
                    (
                        args.manifest,
                        json.dumps(macro_manifest(run, report), ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                    )
                )
            _check_destinations(input_file, writes)
            for path, text in writes:
                _write(path, text)
            if args.output is None:
                sys.stdout.write(report)
            return 0
        if args.command == "sources":
            from .source_pipeline import acquire_plan, load_pins, load_source_plan, replay_plan

            plan = load_source_plan(args.plan)
            input_file = args.plan / "plan.json" if args.plan.is_dir() else args.plan
            if args.source_command == "acquire":
                if args.pins.exists() or args.pins.resolve() == input_file.resolve():
                    raise InputValidationError("pins: 원본과 기존 획득 기록을 보존하려면 새 경로를 사용하세요")
                pins = acquire_plan(plan, args.store)
                text = json.dumps(pins, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
                _check_destinations(input_file, [(args.pins, text)])
                _write(args.pins, text)
                print(f"획득 기록: {args.pins}")
                from .sources import load_snapshot

                statuses = {
                    key: load_snapshot(args.store, key, value).status for key, value in pins["snapshots"].items()
                }
                for source_id, status in statuses.items():
                    print(f"{source_id}: {status}")
                return 0 if statuses and all(item == "available" for item in statuses.values()) else 1
            as_of = None if args.as_of is None else _date(args.as_of, "as_of")
            pins = load_pins(args.pins)
            case = replay_plan(plan, args.store, pins, as_of=as_of)
        else:
            case = load_case(args.case)
            input_file = case_file(args.case)
        result = run_research(case)
        report = render_report(result)
        writes = []
        if args.output is not None:
            writes.append((args.output, report))
        if args.manifest is not None:
            manifest = json.dumps(manifest_for(result, report), ensure_ascii=False, sort_keys=True, indent=2) + "\n"
            writes.append((args.manifest, manifest))
        _check_destinations(input_file, writes)
        for path, text in writes:
            _write(path, text)
        if args.output is None:
            sys.stdout.write(report)
        return 0
    except (InputValidationError, SourceError) as exc:
        print(f"입력 또는 출력 경로 검증 실패 (blocked): {exc}", file=sys.stderr)
        return 2
    except (OSError, ValueError, ArithmeticError) as exc:
        print(f"연구 실행 실패 (failed): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
