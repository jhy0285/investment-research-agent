"""Validate the offline packet without fetching sources or deciding whether prose is true."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .models import (
    Alternative,
    CalculationSpec,
    EvidenceRecord,
    InterpretationStatus,
    OpportunityCost,
    ProfileField,
    ProfileSnapshot,
    ResearchBrief,
    ResearchCase,
    ResearchClaim,
    Review,
    ReviewedText,
    SourceRecord,
    SourceType,
    VerificationStatus,
)


class InputValidationError(ValueError):
    """The packet is blocked; it must not produce a successful research report."""


def _fail(path: str, reason: str) -> None:
    raise InputValidationError(f"{path}: {reason}")


def _object(value: Any, path: str, fields: str) -> dict:
    if not isinstance(value, dict):
        _fail(path, "객체가 필요합니다")
    expected = set(fields.split())
    missing = sorted(expected - value.keys())
    extra = sorted(value.keys() - expected)
    if missing:
        _fail(path, "필수 필드 누락: " + ", ".join(missing))
    if extra:
        _fail(path, "지원하지 않는 필드: " + ", ".join(extra))
    return value


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(path, "비어 있지 않은 문자열이 필요합니다")
    return value


def _id(value: Any, path: str) -> str:
    value = _text(value, path)
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", value):
        _fail(path, "ID는 영문자로 시작하고 영문·숫자·밑줄·하이픈만 사용합니다")
    return value


def _date(value: Any, path: str) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        _fail(path, "날짜는 YYYY-MM-DD 형식이어야 합니다")
    try:
        return date.fromisoformat(value)
    except ValueError:
        _fail(path, "유효하지 않은 날짜입니다")


def _list(value: Any, path: str) -> list:
    if not isinstance(value, list):
        _fail(path, "배열이 필요합니다")
    return value


def _strings(value: Any, path: str, *, ids: bool = False) -> tuple[str, ...]:
    convert = _id if ids else _text
    result = tuple(convert(v, f"{path}[{i}]") for i, v in enumerate(_list(value, path)))
    if len(set(result)) != len(result):
        _fail(path, "중복 항목은 허용하지 않습니다")
    return result


def _enum(enum: type, value: Any, path: str):
    _text(value, path)
    try:
        return enum(value)
    except ValueError:
        _fail(path, "지원하지 않는 상태 또는 유형입니다")


def _review(value: Any, path: str) -> Review:
    d = _object(value, path, "status reviewer reviewed_at rationale")
    status = _enum(InterpretationStatus, d["status"], path + ".status")
    reviewer = None if d["reviewer"] is None else _text(d["reviewer"], path + ".reviewer")
    reviewed = None if d["reviewed_at"] is None else _date(d["reviewed_at"], path + ".reviewed_at")
    rationale = _text(d["rationale"], path + ".rationale")
    if status != InterpretationStatus.PENDING and (reviewer is None or reviewed is None):
        _fail(path, "검토 완료/거부 상태에는 검토자와 날짜가 필요합니다")
    return Review(status, reviewer, reviewed, rationale)


def _reviewed_text(value: Any, path: str) -> ReviewedText:
    d = _object(value, path, "text evidence_ids interpretation")
    return ReviewedText(
        _text(d["text"], path + ".text"),
        _strings(d["evidence_ids"], path + ".evidence_ids", ids=True),
        _review(d["interpretation"], path + ".interpretation"),
    )


def _source(value: Any, path: str) -> SourceRecord:
    d = _object(
        value, path, "id type name location published_at available_at retrieved_at origin_source_id limitations"
    )
    return SourceRecord(
        _id(d["id"], path + ".id"),
        _enum(SourceType, d["type"], path + ".type"),
        _text(d["name"], path + ".name"),
        _text(d["location"], path + ".location"),
        _date(d["published_at"], path + ".published_at"),
        _date(d["available_at"], path + ".available_at"),
        _date(d["retrieved_at"], path + ".retrieved_at"),
        None if d["origin_source_id"] is None else _id(d["origin_source_id"], path + ".origin_source_id"),
        _strings(d["limitations"], path + ".limitations"),
    )


def _evidence(value: Any, path: str) -> EvidenceRecord:
    d = _object(
        value,
        path,
        "id source_id text locator observed_at analyzed_at asset_ids view kind verification interpretation limitations value unit period currency",
    )
    quantity = None
    if d["value"] is not None:
        number = _text(d["value"], path + ".value")
        if len(number) > 64:
            _fail(path + ".value", "수치 표현이 너무 깁니다")
        try:
            quantity = Decimal(number)
        except InvalidOperation:
            _fail(path + ".value", "수치는 유효한 십진 문자열이어야 합니다")
        if not quantity.is_finite() or abs(quantity.adjusted()) > 256:
            _fail(path + ".value", "유한하고 지원 가능한 범위의 십진수가 필요합니다")
    units = {}
    for field in ("unit", "period", "currency"):
        units[field] = None if d[field] is None else _text(d[field], path + "." + field)
    if quantity is not None and any(v is None for v in units.values()):
        _fail(path, "수치에는 단위·기간 정의·통화 기준이 모두 필요합니다")
    if quantity is None and any(v is not None for v in units.values()):
        _fail(path, "수치 없이 단위·기간·통화만 입력하지 않습니다")
    return EvidenceRecord(
        _id(d["id"], path + ".id"),
        _id(d["source_id"], path + ".source_id"),
        _text(d["text"], path + ".text"),
        _text(d["locator"], path + ".locator"),
        _date(d["observed_at"], path + ".observed_at"),
        _date(d["analyzed_at"], path + ".analyzed_at"),
        _strings(d["asset_ids"], path + ".asset_ids", ids=True),
        _text(d["view"], path + ".view"),
        _text(d["kind"], path + ".kind"),
        _enum(VerificationStatus, d["verification"], path + ".verification"),
        _review(d["interpretation"], path + ".interpretation"),
        _strings(d["limitations"], path + ".limitations"),
        quantity,
        units["unit"],
        units["period"],
        units["currency"],
    )


def _claim(value: Any, path: str) -> ResearchClaim:
    d = _object(
        value,
        path,
        "id text asset_ids verification interpretation support_ids counter_ids narrative_evidence_id limitations recheck",
    )
    return ResearchClaim(
        _id(d["id"], path + ".id"),
        _text(d["text"], path + ".text"),
        _strings(d["asset_ids"], path + ".asset_ids", ids=True),
        _enum(VerificationStatus, d["verification"], path + ".verification"),
        _review(d["interpretation"], path + ".interpretation"),
        _strings(d["support_ids"], path + ".support_ids", ids=True),
        _strings(d["counter_ids"], path + ".counter_ids", ids=True),
        (
            None
            if d["narrative_evidence_id"] is None
            else _id(d["narrative_evidence_id"], path + ".narrative_evidence_id")
        ),
        _strings(d["limitations"], path + ".limitations"),
        _text(d["recheck"], path + ".recheck"),
    )


def _alternative(value: Any, path: str) -> Alternative:
    d = _object(value, path, "id name exposure return_definition liquidity support_ids counter_ids unknowns recheck")
    return Alternative(
        _id(d["id"], path + ".id"),
        _text(d["name"], path + ".name"),
        _text(d["exposure"], path + ".exposure"),
        _text(d["return_definition"], path + ".return_definition"),
        _text(d["liquidity"], path + ".liquidity"),
        _strings(d["support_ids"], path + ".support_ids", ids=True),
        _strings(d["counter_ids"], path + ".counter_ids", ids=True),
        _strings(d["unknowns"], path + ".unknowns"),
        tuple(_reviewed_text(v, f"{path}.recheck[{i}]") for i, v in enumerate(_list(d["recheck"], path + ".recheck"))),
    )


def _calculation(value: Any, path: str) -> CalculationSpec:
    d = _object(value, path, "id label method input_ids asset_ids limitations")
    return CalculationSpec(
        _id(d["id"], path + ".id"),
        _text(d["label"], path + ".label"),
        _text(d["method"], path + ".method"),
        _strings(d["input_ids"], path + ".input_ids", ids=True),
        _strings(d["asset_ids"], path + ".asset_ids", ids=True),
        _strings(d["limitations"], path + ".limitations"),
    )


def parse_case(data: dict) -> ResearchCase:
    """Parse one versioned synthetic packet. No normalization creates missing facts."""
    d = _object(
        data,
        "case",
        "schema_version synthetic brief profile sources evidence claims alternatives calculations opportunity_costs",
    )
    if d["schema_version"] != "1":
        _fail("case.schema_version", "지원 버전은 문자열 1입니다")
    if d["synthetic"] is not True:
        _fail("case.synthetic", "이 MVP는 합성 자료만 지원합니다")
    b = _object(
        d["brief"], "brief", "id question as_of base_currency horizon market_context_ids excluded comparison_limits"
    )
    brief = ResearchBrief(
        _id(b["id"], "brief.id"),
        _text(b["question"], "brief.question"),
        _date(b["as_of"], "brief.as_of"),
        _text(b["base_currency"], "brief.base_currency"),
        _text(b["horizon"], "brief.horizon"),
        _strings(b["market_context_ids"], "brief.market_context_ids", ids=True),
        _strings(b["excluded"], "brief.excluded"),
        _strings(b["comparison_limits"], "brief.comparison_limits"),
    )
    p = _object(d["profile"], "profile", "id as_of fields")
    if not isinstance(p["fields"], dict):
        _fail("profile.fields", "객체가 필요합니다")
    profile_fields = {}
    for key, value in p["fields"].items():
        _id(key, "profile.fields key")
        item = _object(value, "profile.fields." + key, "status value")
        if item["status"] not in ("known", "unknown"):
            _fail("profile.fields." + key, "상태는 known 또는 unknown입니다")
        if item["status"] == "unknown" and item["value"] is not None:
            _fail("profile.fields." + key, "unknown 값은 null이어야 합니다")
        if item["status"] == "known" and (
            item["value"] is None
            or type(item["value"]) not in (str, int, bool)
            or isinstance(item["value"], str)
            and not item["value"].strip()
        ):
            _fail("profile.fields." + key, "known에는 문자열·정수·불리언 값이 필요합니다")
        profile_fields[key] = ProfileField(item["status"], item["value"])
    profile = ProfileSnapshot(_id(p["id"], "profile.id"), _date(p["as_of"], "profile.as_of"), profile_fields)
    collections = {}
    for key, parser in (
        ("sources", _source),
        ("evidence", _evidence),
        ("claims", _claim),
        ("alternatives", _alternative),
        ("calculations", _calculation),
    ):
        collections[key] = tuple(parser(v, f"{key}[{i}]") for i, v in enumerate(_list(d[key], key)))
    costs = []
    for i, value in enumerate(_list(d["opportunity_costs"], "opportunity_costs")):
        path = f"opportunity_costs[{i}]"
        c = _object(value, path, "alternative_id forgone_asset_id explanation")
        costs.append(
            OpportunityCost(
                _id(c["alternative_id"], path + ".alternative_id"),
                _id(c["forgone_asset_id"], path + ".forgone_asset_id"),
                _reviewed_text(c["explanation"], path + ".explanation"),
            )
        )
    try:
        canonical = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
            "utf-8"
        )
    except (TypeError, ValueError):
        _fail("case", "지원하지 않는 JSON 값입니다")
    case = ResearchCase(
        d["schema_version"],
        True,
        brief,
        profile,
        collections["sources"],
        collections["evidence"],
        collections["claims"],
        collections["alternatives"],
        collections["calculations"],
        tuple(costs),
        hashlib.sha256(canonical).hexdigest(),
    )
    _validate_links(case)
    return case


def _validate_links(case: ResearchCase) -> None:
    all_ids = [case.brief.id, case.profile.id]
    for items in (case.sources, case.evidence, case.claims, case.alternatives, case.calculations):
        all_ids.extend(item.id for item in items)
    if len(all_ids) != len(set(all_ids)):
        _fail("case", "중복 ID가 있습니다")
    assets = {a.id: a for a in case.alternatives}
    sources = {s.id: s for s in case.sources}
    evidence = {e.id: e for e in case.evidence}
    if {a.exposure for a in case.alternatives} != {"cash", "government_bond", "equity"}:
        _fail("alternatives", "이 MVP는 현금성·국채·주식 노출을 모두 비교합니다")
    if len(case.alternatives) != 3:
        _fail("alternatives", "이번 버전은 세 노출의 단일 사례를 지원합니다")
    if case.brief.base_currency != "KRW":
        _fail("brief.base_currency", "이 MVP의 기준 통화는 KRW입니다")
    base = case.profile.fields.get("base_currency")
    if base is not None and base.status == "known" and base.value != case.brief.base_currency:
        _fail("profile.fields.base_currency", "연구 기준 통화와 일치해야 합니다")
    if case.profile.as_of > case.brief.as_of:
        _fail("profile.as_of", "연구 기준 시점 이후 사용자 정보입니다")

    def references(ids: tuple[str, ...], path: str, scope: tuple[str, ...] = ()):
        for eid in ids:
            if eid not in evidence:
                _fail(path, "존재하지 않는 evidence ID: " + eid)
            if scope and not set(scope).issubset(evidence[eid].asset_ids):
                _fail(path, "근거의 자산 범위를 벗어난 참조: " + eid)

    def asset_scope(ids: tuple[str, ...], path: str):
        if not ids or not set(ids).issubset(assets):
            _fail(path, "하나 이상의 지원 자산 ID가 필요합니다")

    def usable(eid: str) -> bool:
        e = evidence[eid]
        return (
            e.kind != "observed_narrative"
            and sources[e.source_id].type != SourceType.COMMUNITY
            and e.verification == VerificationStatus.SUPPORTED
            and e.interpretation.status == InterpretationStatus.REVIEWED
        )

    def review_references(review: Review, ids: tuple[str, ...], path: str) -> None:
        if review.reviewed_at is None:
            return
        for eid in ids:
            item = evidence[eid]
            ready_at = max(item.analyzed_at, item.interpretation.reviewed_at or item.analyzed_at)
            if review.reviewed_at < ready_at:
                _fail(path + ".interpretation.reviewed_at", "참조 근거의 분석·검토 이전 날짜입니다: " + eid)

    for s in case.sources:
        if not s.location.startswith("synthetic://") or not s.location.removeprefix("synthetic://").strip():
            _fail(f"sources.{s.id}.location", "합성 출처 식별자는 synthetic://로 시작합니다")
        if not s.published_at <= s.available_at <= s.retrieved_at:
            _fail(f"sources.{s.id}", "발행·이용 가능·획득 날짜 순서가 잘못되었습니다")
        if s.available_at > case.brief.as_of:
            _fail(f"sources.{s.id}.available_at", "연구 기준 시점 이후에 이용 가능한 출처입니다")
        seen = {s.id}
        parent = s.origin_source_id
        while parent is not None:
            if parent not in sources:
                _fail(f"sources.{s.id}.origin_source_id", "원출처 ID가 없습니다")
            if parent in seen:
                _fail(f"sources.{s.id}.origin_source_id", "원출처 관계가 순환합니다")
            seen.add(parent)
            parent = sources[parent].origin_source_id
    for e in case.evidence:
        path = "evidence." + e.id
        if e.source_id not in sources:
            _fail(path + ".source_id", "출처 ID가 없습니다")
        asset_scope(e.asset_ids, path + ".asset_ids")
        if e.view not in ("macro", "fundamental", "quantitative", "community"):
            _fail(path + ".view", "지원하지 않는 연구 관점입니다")
        if e.kind not in ("observed_fact", "external_fact", "observed_narrative"):
            _fail(path + ".kind", "지원하지 않는 근거 유형입니다")
        source = sources[e.source_id]
        if e.observed_at > case.brief.as_of:
            _fail(path + ".observed_at", "연구 기준 시점 이후 관측입니다")
        if e.analyzed_at < max(e.observed_at, source.retrieved_at):
            _fail(path + ".analyzed_at", "관측·획득 이전에 분석할 수 없습니다")
        if e.interpretation.reviewed_at is not None and e.interpretation.reviewed_at < e.analyzed_at:
            _fail(path + ".interpretation.reviewed_at", "분석 이전의 검토 날짜입니다")
        if source.type == SourceType.COMMUNITY and (e.kind != "observed_narrative" or e.view != "community"):
            _fail(path, "커뮤니티는 발언 관측으로 기록하며 내용을 사실로 승격하지 않습니다")
        if e.kind == "observed_narrative" and e.value is not None:
            _fail(path, "서사에 수치 관측을 붙여 신뢰도나 확률로 사용하지 않습니다")
    references(case.brief.market_context_ids, "brief.market_context_ids")
    for a in case.alternatives:
        references(a.support_ids, f"alternatives.{a.id}.support_ids", (a.id,))
        references(a.counter_ids, f"alternatives.{a.id}.counter_ids", (a.id,))
        if set(a.support_ids) & set(a.counter_ids):
            _fail(f"alternatives.{a.id}", "같은 근거를 지지와 반대로 중복 배치하지 않습니다")
        for i, note in enumerate(a.recheck):
            references(note.evidence_ids, f"alternatives.{a.id}.recheck[{i}]", (a.id,))
            review_references(note.interpretation, note.evidence_ids, f"alternatives.{a.id}.recheck[{i}]")
            if note.interpretation.status == InterpretationStatus.REVIEWED and not note.evidence_ids:
                _fail(f"alternatives.{a.id}.recheck[{i}]", "검토된 설명에는 근거 참조가 필요합니다")
    for c in case.claims:
        path = "claims." + c.id
        asset_scope(c.asset_ids, path + ".asset_ids")
        references(c.support_ids, path + ".support_ids", c.asset_ids)
        references(c.counter_ids, path + ".counter_ids", c.asset_ids)
        if set(c.support_ids) & set(c.counter_ids):
            _fail(path, "같은 근거를 지지와 반대로 중복 배치하지 않습니다")
        if c.narrative_evidence_id is not None:
            references((c.narrative_evidence_id,), path + ".narrative_evidence_id", c.asset_ids)
            if evidence[c.narrative_evidence_id].kind != "observed_narrative":
                _fail(path, "발언 관측 근거만 내러티브에 연결합니다")
        review_ids = c.support_ids + c.counter_ids
        if c.narrative_evidence_id is not None:
            review_ids += (c.narrative_evidence_id,)
        review_references(c.interpretation, review_ids, path)
        if c.verification in (VerificationStatus.SUPPORTED, VerificationStatus.PARTIAL, VerificationStatus.DISPUTED):
            if c.interpretation.status != InterpretationStatus.REVIEWED or not any(usable(e) for e in c.support_ids):
                _fail(path, "확인·일부 확인·상충 상태에는 검토 기록과 확인된 비커뮤니티 지지 근거가 필요합니다")
        if c.verification in (VerificationStatus.CONTRADICTED, VerificationStatus.DISPUTED):
            if c.interpretation.status != InterpretationStatus.REVIEWED or not any(usable(e) for e in c.counter_ids):
                _fail(path, "반박·상충 상태에는 검토 기록과 확인된 반대 근거가 필요합니다")
    for c in case.calculations:
        path = "calculations." + c.id
        asset_scope(c.asset_ids, path + ".asset_ids")
        references(c.input_ids, path + ".input_ids", c.asset_ids)
        if c.method != "rate_difference_v1" or len(c.input_ids) != 2:
            _fail(path, "지원 방법은 두 입력의 rate_difference_v1입니다")
        inputs = [evidence[eid] for eid in c.input_ids]
        if any(not usable(e.id) or e.value is None for e in inputs):
            _fail(path, "계산 입력은 확인·검토된 비커뮤니티 수치여야 합니다")
        if any(e.unit != "percent" or e.period != "annual_rate" for e in inputs):
            _fail(path, "계산 입력은 percent 단위의 annual_rate 정의여야 합니다")
        if len({e.currency for e in inputs}) != 1:
            _fail(path, "계산 입력의 통화 기준이 다릅니다")
        if not c.limitations:
            _fail(path, "기간·수익 정의와 미래 적용 한계를 명시해야 합니다")
    for i, cost in enumerate(case.opportunity_costs):
        path = f"opportunity_costs[{i}]"
        if (
            cost.alternative_id not in assets
            or cost.forgone_asset_id not in assets
            or cost.alternative_id == cost.forgone_asset_id
        ):
            _fail(path, "서로 다른 지원 대안 사이의 기회비용이어야 합니다")
        references(cost.explanation.evidence_ids, path + ".explanation.evidence_ids")
        review_references(cost.explanation.interpretation, cost.explanation.evidence_ids, path + ".explanation")
        if (
            cost.explanation.interpretation.status == InterpretationStatus.REVIEWED
            and not cost.explanation.evidence_ids
        ):
            _fail(path, "검토된 기회비용 설명에는 근거가 필요합니다")


def case_file(path: str | Path) -> Path:
    path = Path(path)
    return path / "case.json" if path.is_dir() else path


def load_case(path: str | Path) -> ResearchCase:
    """Read local JSON only; directory inputs resolve to case.json."""

    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                _fail("JSON", "중복 필드: " + key)
            result[key] = value
        return result

    def reject_constant(value):
        _fail("JSON", "NaN 또는 Infinity는 허용하지 않습니다")

    try:
        raw = case_file(path).read_text(encoding="utf-8")
        data = json.loads(raw, object_pairs_hook=unique_keys, parse_constant=reject_constant)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise InputValidationError("JSON: UTF-8 형식의 유효한 JSON이 필요합니다") from exc
    return parse_case(data)
