"""Pinned, offline opportunity-map synthesis with disclosed draft interpretation.

Source-statement occurrence can motivate a research question. It does not
verify an investment thesis, establish attractiveness, or authorize allocation.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
import re

from .engine import run_research
from .macro_pipeline import MacroPlan, MacroRun, macro_manifest, replay_macro
from .models import (
    Alternative,
    InterpretationStatus,
    OpportunityCost,
    ProfileField,
    ProfileSnapshot,
    ResearchBrief,
    ResearchCase,
    ResearchClaim,
    ResearchResult,
    Review,
    ReviewedText,
    SourceType,
    VerificationStatus,
)
from .source_pipeline import (
    SourcePlan,
    _digest,
    _id,
    _list,
    _object,
    _strings,
    _text,
    load_pins,
    replay_plan,
)
from .sources import SourceError, _time, freshness, load_snapshot

OPPORTUNITY_VERSION = "opportunity_map_v1"
PRIORITIES = {"candidate", "monitor", "defer", "insufficient"}
ROW_FIELDS = {
    "asset_id",
    "name",
    "exposure",
    "return_definition",
    "liquidity",
    "state",
    "positive",
    "negative",
    "uncertainty",
    "opportunity_cost",
    "priority",
    "priority_reason",
    "recheck",
    "candidate",
}
SECTION_FIELDS = {
    "overview",
    "drivers",
    "market_narratives",
    "community",
    "gaps",
    "korean_context",
    "unknowns",
    "easy",
}
QUOTE_SOURCES = {
    SourceType.PRIMARY,
    SourceType.INSTITUTION,
    SourceType.DATA_PROVIDER,
    SourceType.RESEARCH,
    SourceType.NEWS,
}


@dataclass(frozen=True)
class OpportunityReview:
    data: dict
    input_digest: str

    @property
    def id(self) -> str:
        return self.data["id"]

    @property
    def as_of(self) -> datetime:
        return _time(self.data["as_of"])


@dataclass(frozen=True)
class OpportunityRun:
    review: OpportunityReview
    case: ResearchCase
    result: ResearchResult
    macro: MacroRun
    rows: tuple[dict, ...]
    diagnostics: tuple[str, ...]
    input_digest: str
    sections: dict


def _prose(value, path: str) -> str:
    value = _text(value, path)
    if re.search(r"\d", value):
        raise SourceError(f"{path}: draft prose must reference financial numbers instead of typing them")
    return value


def _prose_list(value, path: str) -> tuple[str, ...]:
    result = tuple(_prose(item, path) for item in _list(value, path))
    if len(result) != len(set(result)):
        raise SourceError(f"{path}: duplicate entries")
    return result


def _statement(value, path: str, cost: bool = False) -> dict:
    _object(value, {"text", "evidence_ids"} | ({"alternative_ids"} if cost else set()), set(), path)
    _prose(value["text"], path + ".text")
    _strings(value["evidence_ids"], path + ".evidence_ids", True)
    if cost:
        _strings(value["alternative_ids"], path + ".alternative_ids", True)
    return value


def validate_profile(profile: dict) -> None:
    """Shared information-state contract; unknown personal inputs stay null."""
    if not isinstance(profile, dict) or len(profile) > 100:
        raise SourceError("review.profile: bounded object required")
    for name, field in profile.items():
        _id(name, "profile field")
        _object(field, {"status", "value"}, set(), "profile." + name)
        if not isinstance(field["status"], str) or field["status"] not in {"known", "self_reported", "unknown"}:
            raise SourceError("profile: unsupported information status")
        value = field["value"]
        if field["status"] == "unknown":
            if value is not None:
                raise SourceError("unknown profile fields must have null values")
        elif type(value) not in {str, int, bool} or (isinstance(value, str) and not value.strip()):
            raise SourceError("known or self-reported profile fields require a scalar value")
        if name == "base_currency" and value not in {None, "KRW"}:
            raise SourceError("this research path uses KRW as its base currency")


def load_opportunity_review(path: str | Path) -> OpportunityReview:
    """Load a bounded, strict draft; read-only, with no implicit discovery."""
    path = Path(path)
    path = path / "review.json" if path.is_dir() else path
    data = load_pins(path)
    required = {
        "schema_version",
        "id",
        "question",
        "as_of",
        "author",
        "review_status",
        "profile",
        "horizon",
        "comparison_limits",
        "rows",
        "sections",
        "next_research",
        "sampling_limits",
        "access_notes",
    }
    _object(data, required, set(), "opportunity review")
    if data["schema_version"] != "opportunity-review-v1" or data["review_status"] != "draft":
        raise SourceError("opportunity review must use the supported draft schema")
    _id(data["id"], "review.id")
    for name in ("question", "author", "horizon"):
        _prose(data[name], "review." + name)
    cutoff = _time(data["as_of"])
    if cutoff is None or len(data["as_of"]) == 10:
        raise SourceError("review.as_of requires an aware ISO timestamp")
    for name in ("comparison_limits", "sampling_limits", "access_notes"):
        _prose_list(data[name], "review." + name)
    validate_profile(data["profile"])
    rows = _list(data["rows"], "rows")
    if not rows or len(rows) > 25:
        raise SourceError("opportunity map requires one to twenty-five explicit rows")
    asset_ids = []
    candidates = 0
    for index, row in enumerate(rows):
        path = f"rows[{index}]"
        _object(row, ROW_FIELDS, set(), path)
        asset_ids.append(_id(row["asset_id"], path + ".asset_id"))
        for name in ("name", "exposure", "return_definition", "liquidity"):
            _prose(row[name], path + "." + name)
        for name in ("state", "positive", "negative", "priority_reason", "recheck"):
            _statement(row[name], path + "." + name)
        _statement(row["opportunity_cost"], path + ".opportunity_cost", True)
        _prose_list(row["uncertainty"], path + ".uncertainty")
        if not isinstance(row["priority"], str) or row["priority"] not in PRIORITIES:
            raise SourceError(path + ": unsupported research priority")
        candidate = row["candidate"]
        if candidate is not None:
            candidates += 1
            if row["priority"] != "candidate":
                raise SourceError(path + ": candidate detail requires candidate research priority")
            _object(
                candidate,
                {"why_now", "changed", "interesting", "counterargument", "confirm"},
                set(),
                path + ".candidate",
            )
            for name in ("why_now", "changed", "interesting", "counterargument"):
                _statement(candidate[name], path + ".candidate." + name)
            if not _prose_list(candidate["confirm"], path + ".candidate.confirm"):
                raise SourceError(path + ": candidate requires a confirmation question")
        if row["priority"] == "candidate" and (candidate is None or not row["uncertainty"]):
            raise SourceError(path + ": candidate requires counterargument and uncertainty detail")
    if len(asset_ids) != len(set(asset_ids)) or data["id"] in asset_ids:
        raise SourceError("opportunity rows must use unique, unreserved asset IDs")
    if candidates > 4:
        raise SourceError("at most four candidates can receive deeper discussion")
    for row in rows:
        alternatives = row["opportunity_cost"]["alternative_ids"]
        if not set(alternatives) <= set(asset_ids) or row["asset_id"] in alternatives:
            raise SourceError("opportunity-cost comparisons must reference other explicit alternatives")
    _object(data["sections"], SECTION_FIELDS, set(), "sections")
    for name, content in data["sections"].items():
        if name in {"unknowns", "easy"}:
            _prose_list(content, "sections." + name)
        else:
            for statement in _list(content, "sections." + name):
                _statement(statement, "sections." + name)
    if len(data["sections"]["easy"]) > 5:
        raise SourceError("easy explanation must contain at most five sentences")
    followup = _object(data["next_research"], {"asset_id", "title", "question"}, set(), "next_research")
    if followup["asset_id"] not in asset_ids:
        raise SourceError("next research must reference an explicit alternative")
    for name in ("title", "question"):
        _prose(followup[name], "next_research." + name)
    return OpportunityReview(data, _digest(data))


def _all_statements(data: dict):
    for row in data["rows"]:
        for name in ("state", "positive", "negative", "opportunity_cost", "priority_reason", "recheck"):
            yield row["asset_id"], name, row[name]
        if row["candidate"]:
            for name in ("why_now", "changed", "interesting", "counterargument"):
                yield row["asset_id"], "candidate." + name, row["candidate"][name]
    for name, content in data["sections"].items():
        if name not in {"unknowns", "easy"}:
            for index, statement in enumerate(content):
                yield None, f"sections.{name}.{index}", statement


def replay_opportunity(
    review: OpportunityReview,
    source_plan: SourcePlan,
    store: str | Path,
    pins: dict,
    macro_plan: MacroPlan,
    macro_store: str | Path,
    macro_pins: dict,
) -> OpportunityRun:
    """Combine existing replay contracts without acquiring or scoring assets."""
    if _digest(review.data) != review.input_digest:
        raise SourceError("opportunity review changed after loading; reload the explicit input")
    cutoff = review.as_of
    asset_ids = tuple(row["asset_id"] for row in review.data["rows"])
    if set(source_plan.asset_ids) != set(asset_ids):
        raise SourceError("source plan and opportunity review must declare the same alternatives")
    source_case = replay_plan(source_plan, store, pins, as_of=cutoff.date())
    macro = replay_macro(macro_plan, macro_store, macro_pins, as_of=cutoff)
    diagnostics = [*source_case.diagnostics, *macro.diagnostics]
    sources = []
    evidence = []
    for source in source_case.sources:
        provenance = source.provenance
        if provenance is not None:
            shot = load_snapshot(store, source.id, provenance.snapshot_id)
            age = freshness(shot, cutoff)["status"]
            age = "unavailable" if shot.status != "available" else age
            if _time(provenance.retrieved_at) > cutoff:
                age = "future"
            elif age != "future" and provenance.published_at is None:
                if provenance.observed_at is None:
                    age = "unknown" if age != "unavailable" else age
                elif age == "fresh":
                    diagnostics.append(
                        source.id
                        + ": explicitly dated reported observation from the retained page; publication unknown and availability before retrieval unproven"
                    )
            provenance = replace(provenance, freshness=age)
            if age == "future":
                diagnostics.append(
                    source.id + ": source timing is after the exact opportunity cutoff; current facts withheld"
                )
        sources.append(replace(source, provenance=provenance))
    source_by_id = {source.id: source for source in sources}
    for item in source_case.evidence:
        source = source_by_id[item.source_id]
        provenance = item.provenance
        if source.provenance is not None:
            provenance = replace(provenance, freshness=source.provenance.freshness)
        evidence.append(replace(item, provenance=provenance))
    macro_scope = tuple(
        identifier for identifier in ("SHORT_BOND", "LONG_BOND", "CASH", "US_EQUITY") if identifier in asset_ids
    )
    for item in macro.case.evidence:
        definition_id = item.provenance.definition["measure"]
        scope = macro_scope if definition_id.startswith("US_TREASURY_") else asset_ids
        evidence.append(replace(item, asset_ids=scope or asset_ids))
    sources.extend(macro.case.sources)
    source_by_id = {source.id: source for source in sources}
    evidence_by_id = {item.id: item for item in evidence}
    metrics = tuple(
        (
            replace(metric, asset_ids=macro_scope or asset_ids)
            if all(
                evidence_by_id[ref].provenance.definition["measure"].startswith("US_TREASURY_")
                for ref in metric.input_ids
            )
            else replace(metric, asset_ids=asset_ids)
        )
        for metric in macro.metrics
    )
    metric_by_id = {metric.id: metric for metric in metrics}
    merged_ids = [review.id, *asset_ids, *source_by_id, *evidence_by_id, *metric_by_id]
    if (
        len(source_by_id) != len(sources)
        or len(evidence_by_id) != len(evidence)
        or len(merged_ids) != len(set(merged_ids))
    ):
        raise SourceError("source, observation and metric IDs must remain unambiguous")
    known_refs = {item["id"] for item in source_plan.evidence}
    planned_scopes = {
        item["id"]: next(
            source.asset_ids or source_plan.asset_ids
            for source in source_plan.sources
            if source.id == item["source_id"]
        )
        for item in source_plan.evidence
    }
    known_refs.update(evidence_by_id)
    known_refs.update(metric.id for metric in macro.snapshot.metrics)
    metric_states = {metric.id: metric.status for metric in macro.snapshot.metrics}

    def ref_status(identifier: str, scope: str | None = None) -> tuple[bool, str]:
        if identifier not in known_refs:
            raise SourceError("unknown opportunity evidence or metric reference: " + identifier)
        if identifier in metric_by_id:
            metric = metric_by_id[identifier]
            if scope is not None and scope not in metric.asset_ids:
                raise SourceError("opportunity metric reference has incompatible asset scope: " + identifier)
            # A current YoY or change intentionally uses an older baseline.
            # Its own macro status validates the current endpoint and method;
            # applying standalone observation freshness to every input would
            # incorrectly reject a valid exact twelve-month comparison.
            inputs = [evidence_by_id.get(ref) for ref in metric.input_ids]
            usable = bool(inputs) and all(
                item is not None
                and item.value is not None
                and item.provenance is not None
                and item.provenance.match_status == "matched"
                and item.provenance.freshness != "future"
                and item.verification == VerificationStatus.SUPPORTED
                for item in inputs
            )
            return usable, (
                "current computed fact with explicitly dated inputs" if usable else "metric input unavailable"
            )
        item = evidence_by_id.get(identifier)
        if item is None:
            if scope is not None and identifier in planned_scopes and scope not in planned_scopes[identifier]:
                raise SourceError("opportunity missing-source reference has incompatible asset scope: " + identifier)
            return False, "missing or " + metric_states.get(identifier, "failed source")
        if scope is not None and scope not in item.asset_ids:
            raise SourceError("opportunity evidence reference has incompatible asset scope: " + identifier)
        source = source_by_id[item.source_id]
        if item.provenance is None or item.provenance.match_status != "matched":
            return False, "passage not matched"
        if item.provenance.freshness != "fresh":
            return False, item.provenance.freshness
        if item.kind == "observed_narrative" or source.type == SourceType.COMMUNITY:
            return False, "observed narrative; financial content unverified"
        if (
            item.verification != VerificationStatus.SUPPORTED
            or item.interpretation.status == InterpretationStatus.REJECTED
        ):
            return False, "unverified or rejected"
        if source.type not in QUOTE_SOURCES:
            return False, "opinion source requires corroboration"
        if item.interpretation.status == InterpretationStatus.PENDING:
            return True, "matched source-statement occurrence; economic meaning review pending"
        return True, "narrow source or calculation fact; investment interpretation remains draft"

    def effective(statement: dict, scope: str | None = None) -> dict:
        available, withheld, warnings = [], [], []
        for identifier in statement["evidence_ids"]:
            usable, reason = ref_status(identifier, scope)
            (available if usable else withheld).append(identifier)
            if not usable or "pending" in reason:
                warnings.append(identifier + ": " + reason)
        return {
            **statement,
            "_available_ids": available,
            "_withheld_ids": withheld,
            "_warnings": warnings,
            "_status": "partial" if available and withheld else "unavailable" if withheld else "draft",
        }

    rows = []
    for original in review.data["rows"]:
        row = dict(original)
        scope = row["asset_id"]
        for name in ("state", "positive", "negative", "opportunity_cost", "priority_reason", "recheck"):
            # Opportunity cost intentionally discusses the referenced other alternatives.
            row[name] = effective(row[name], None if name == "opportunity_cost" else scope)
        if row["candidate"]:
            row["candidate"] = {
                name: effective(statement, scope) if name != "confirm" else list(statement)
                for name, statement in row["candidate"].items()
            }
        row["_requested_priority"] = row["priority"]
        row["_warnings"] = []
        priority_refs = row["priority_reason"]["_available_ids"]
        if row["priority"] == "candidate" and not priority_refs:
            row["priority"] = "insufficient"
            row["_warnings"].append(
                "candidate priority withheld: no current noncommunity factual occurrence supports this research question"
            )
        if row["state"]["_withheld_ids"]:
            row["_warnings"].append(
                "current-state draft contains unavailable references; affected text is not a verified current fact"
            )
        row["_review_status"] = "draft"
        diagnostics.extend(scope + ": " + warning for warning in row["_warnings"])
        rows.append(row)
    sections = {
        name: list(content) if name in {"unknowns", "easy"} else [effective(statement) for statement in content]
        for name, content in review.data["sections"].items()
    }
    pending = Review(
        InterpretationStatus.PENDING,
        None,
        None,
        "Codex의 허용된 연구 초안. 인용 존재와 계산 사실은 경제적 의미·투자 매력·사람의 검토 완료를 뜻하지 않는다.",
    )

    def evidence_refs(identifiers):
        # Existing ResearchCase references point to evidence, not calculations.
        # Keep metric references in the map; expand their inputs in this adapter.
        refs = []
        for identifier in identifiers:
            candidates = metric_by_id[identifier].input_ids if identifier in metric_by_id else (identifier,)
            refs.extend(ref for ref in candidates if ref in evidence_by_id and ref not in refs)
        return tuple(refs)

    alternatives = tuple(
        Alternative(
            row["asset_id"],
            row["name"],
            row["exposure"],
            row["return_definition"],
            row["liquidity"],
            evidence_refs(row["positive"]["evidence_ids"]),
            evidence_refs(row["negative"]["evidence_ids"]),
            tuple(row["uncertainty"]),
            (ReviewedText(row["recheck"]["text"], evidence_refs(row["recheck"]["evidence_ids"]), pending),),
        )
        for row in rows
    )
    costs = tuple(
        OpportunityCost(
            row["asset_id"],
            other,
            ReviewedText(
                row["opportunity_cost"]["text"], evidence_refs(row["opportunity_cost"]["evidence_ids"]), pending
            ),
        )
        for row in rows
        for other in row["opportunity_cost"]["alternative_ids"]
    )
    claims = []
    for claim in (*source_case.claims, *macro.case.claims):
        claim_refs = (
            *claim.support_ids,
            *claim.counter_ids,
            *claim.context_ids,
            *((claim.narrative_evidence_id,) if claim.narrative_evidence_id else ()),
        )
        unavailable = any(
            ref in evidence_by_id and evidence_by_id[ref].provenance.freshness == "future" for ref in claim_refs
        )
        claims.append(
            replace(
                claim,
                asset_ids=tuple(identifier for identifier in claim.asset_ids if identifier in asset_ids) or asset_ids,
                verification=VerificationStatus.UNVERIFIED if unavailable else claim.verification,
                limitations=(
                    (*claim.limitations, "exact opportunity cutoff excludes a referenced later retrieval")
                    if unavailable
                    else claim.limitations
                ),
            )
        )
    for index, (scope, name, statement) in enumerate(_all_statements(review.data)):
        claims.append(
            ResearchClaim(
                "OPPORTUNITY_DRAFT_" + str(index),
                statement["text"],
                (scope,) if scope else asset_ids,
                VerificationStatus.UNVERIFIED,
                pending,
                (),
                (),
                None,
                ("연구 우선순위와 조건부 해석의 초안이며 사실 확인·상대 매력 확정이 아니다.",),
                "새 원자료·반대 근거·사용자 제약이 확인되면 다시 검토한다.",
                evidence_refs(statement["evidence_ids"]),
            )
        )
    digest = _digest(
        {
            "review": review.input_digest,
            "source_case": source_case.input_digest,
            "macro": macro.input_digest,
            "method": OPPORTUNITY_VERSION,
            "as_of": cutoff.isoformat(),
        }
    )
    brief = ResearchBrief(
        review.id,
        review.data["question"],
        cutoff.date(),
        "KRW",
        review.data["horizon"],
        evidence_refs(ref for statement in sections["drivers"] for ref in statement["evidence_ids"]),
        tuple(review.data["sampling_limits"]),
        tuple(review.data["comparison_limits"]),
    )
    profile = ProfileSnapshot(
        review.id + "_PROFILE",
        cutoff.date(),
        {name: ProfileField(field["status"], field["value"]) for name, field in review.data["profile"].items()},
    )
    case = ResearchCase(
        "1",
        False,
        brief,
        profile,
        tuple(sources),
        tuple(evidence),
        tuple(claims),
        alternatives,
        (),
        costs,
        digest,
        True,
        tuple(diagnostics),
    )
    result = replace(run_research(case), metrics=metrics)
    return OpportunityRun(review, case, result, macro, tuple(rows), tuple(diagnostics), digest, sections)


def opportunity_manifest(run: OpportunityRun, report: str) -> dict:
    from .__main__ import manifest_for
    from .macro_report import render_macro_report
    from .opportunity_report import OPPORTUNITY_REPORT_VERSION

    manifest = manifest_for(run.result, report)
    manifest.update(
        {
            "kind": "cross_asset_opportunity_map",
            "as_of": run.review.as_of.isoformat(),
            "review_sha256": run.review.input_digest,
            "review_status": "draft",
            "author": run.review.data["author"],
            "profile": run.review.data["profile"],
            "source_statement_scope": "matched occurrence; investment meaning not automatically verified",
            "priorities": [
                {
                    "asset_id": row["asset_id"],
                    "requested": row["_requested_priority"],
                    "effective": row["priority"],
                    "review_status": "draft",
                    "warnings": row["_warnings"],
                }
                for row in run.rows
            ],
            "references": [
                {"asset_id": scope, "location": name, "evidence_ids": statement["evidence_ids"]}
                for scope, name, statement in _all_statements(run.review.data)
            ],
            "effective_rows": list(run.rows),
            "effective_sections": run.sections,
            "macro": macro_manifest(run.macro, render_macro_report(run.macro)),
        }
    )
    manifest["method_versions"].update(
        {"opportunity": OPPORTUNITY_VERSION, "opportunity_report": OPPORTUNITY_REPORT_VERSION}
    )
    return manifest
