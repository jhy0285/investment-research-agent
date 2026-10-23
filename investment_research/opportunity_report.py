"""Reference-bound Korean opportunity map; no financial arithmetic or scoring."""

from __future__ import annotations

from hashlib import sha256
from html import escape
import re
from zoneinfo import ZoneInfo

from .macro_report import _number
from .models import SourceType
from .sources import SourceError, _time

OPPORTUNITY_REPORT_VERSION = "opportunity_report_v1"
_PRIORITY = {"candidate": "후속 조사 후보", "monitor": "관찰", "defer": "우선순위 낮음", "insufficient": "자료 부족"}


def _text(value: object) -> str:
    value = str(value).replace("\n", " / ").replace("\r", " ")
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", value)
    return re.sub(r"([\\`*_{}\[\]#|~])", r"\\\1", escape(value, quote=False))


def _target(identifier: str) -> str:
    return "opportunity-" + sha256(identifier.encode()).hexdigest()


def _anchor(identifier: str) -> str:
    return '<a id="' + _target(identifier) + '"></a>'


def _ref(identifier: str) -> str:
    label = identifier[:16] + "…" if identifier.startswith(("OBS_", "MET_")) else identifier
    return f"[{_text(label)}](#{_target(identifier)})"


def _refs(identifiers) -> str:
    return ", ".join(_ref(identifier) for identifier in identifiers) or "추가 자료 필요"


def _statement(run, statement: dict, narrative: bool | str = False) -> str:
    """A withheld reference never leaves an unsupported current assertion visible."""
    withheld = list(statement.get("_withheld_ids", ()))
    if narrative:
        evidence = {item.id: item for item in run.case.evidence}
        sources = {item.id: item for item in run.case.sources}
        withheld = [
            identifier
            for identifier in withheld
            if not (
                identifier in evidence
                and evidence[identifier].kind == "observed_narrative"
                and evidence[identifier].provenance.freshness == "fresh"
                and evidence[identifier].provenance.match_status == "matched"
                and _time(sources[evidence[identifier].source_id].provenance.retrieved_at) <= run.review.as_of
            )
        ]
    if withheld:
        return "자료·시점 조건을 충족하지 못해 이 문장 채택을 보류함 (" + _refs(withheld) + ")"
    prefix = "[대조 해석 초안] " if narrative == "contrast" else "[관측된 서사 · 내용 미검증] " if narrative else ""
    return prefix + _text(statement["text"]) + " (" + _refs(statement["evidence_ids"]) + ")"


def _check(run) -> None:
    evidence = {item.id: item for item in run.case.evidence}
    for metric in run.result.metrics:
        if not metric.input_ids or any(identifier not in evidence for identifier in metric.input_ids):
            raise SourceError("opportunity report metric has no existing evidence inputs")
    for item in run.case.evidence:
        if item.provenance is None or not item.provenance.snapshot_id or item.provenance.match_status != "matched":
            raise SourceError("opportunity report evidence has no preserved matched provenance")


def render_opportunity_report(run) -> str:
    _check(run)
    data = run.review.data
    cutoff = run.review.as_of
    kst = cutoff.astimezone(ZoneInfo("Asia/Seoul"))
    lines = [
        "# Cross-Asset Opportunity Map",
        "",
        "## 기준 시점",
        "",
        f"- 정보 기준: {kst.isoformat()} (한국시간), {cutoff.isoformat()} (UTC).",
        f"- 질문: {_text(data['question'])}",
        f"- 조사·해석 작성자: {_text(data['author'])}; 상태: **연구 초안**. 사람의 의미 검토 완료·자산 매력 확정이 아니다.",
        "- 원문에서 해당 발표·관측을 확인한 것과 실제 투자 논리가 성립하는 것은 별도다. 후보 선정은 다음 연구 질문의 우선순위다.",
        "- 주식의 성장·가치·배당은 겹치는 특성이고, 이번 펀드 자료는 각 영역의 제한된 표본이다.",
        "",
        "## 한눈에 보기",
        "",
    ]
    lines.extend("- " + _statement(run, item) for item in run.sections["overview"][:5])
    lines.extend(["", "## 현재 시장을 움직이는 핵심 변수", ""])
    lines.extend("- " + _statement(run, item) for item in run.sections["drivers"])
    lines.extend(
        [
            "",
            "### 기존 거시 시계열에서 확인한 값",
            "",
            "서로 다른 관측 기간을 표시한다. 국채 시장금리·과거 물가 상승률·환율을 같은 미래 투자수익률로 순위화하지 않는다.",
            "",
            "| 원관측 | 기준 관측 | 값 | 근거 |",
            "| --- | --- | --- | --- |",
        ]
    )
    for selection in run.macro.snapshot.selections:
        item = selection.latest
        if selection.status == "available" and item is not None and item.value is not None:
            lines.append(
                f"| {_text(selection.definition.name)} | {item.observation_date.isoformat()} | {_number(item.value)} {_text(selection.definition.unit)} | {_ref(item.id)} |"
            )
        else:
            lines.append(
                f"| {_text(selection.definition.name)} | 미확인 | 채택 보류: {_text(selection.status)} | 보존 판본 참조 |"
            )
    for metric in run.result.metrics:
        if metric.method in {"yoy_v1", "yield_spread_v1", "inflation_trend_v1"}:
            lines.append(
                f"- [계산 사실] {_text(metric.label)}: {_number(metric.value)} {_text(metric.unit)} ({_ref(metric.id)})."
            )
    lines.extend(
        [
            "",
            "## Cross-Asset Opportunity Map",
            "",
            "현재 상태·긍정/부정 논리·기회비용은 출처에 연결한 조건부 연구 초안이다. 가격에 반영된 기대와 실행 가능한 보상을 확인하기 전에는 매수 기회로 확정하지 않는다.",
            "",
            "| 영역 | 현재 상태 | 긍정 근거·조사 가설 | 부정 근거·반대 논리 | 중요한 미확인 | 기회비용 | 연구 우선순위 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in run.rows:
        lines.append(
            "| "
            + " | ".join(
                (
                    _text(row["name"]),
                    _statement(run, row["state"]),
                    _statement(run, row["positive"]),
                    _statement(run, row["negative"]),
                    " / ".join(_text(value) for value in row["uncertainty"]),
                    _statement(run, row["opportunity_cost"]),
                    _PRIORITY[row["priority"]] + ": " + _statement(run, row["priority_reason"]),
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## 시장이 지금 믿고 있는 것",
            "",
            "시장 전체의 합의나 대표 sentiment를 추정하지 않았다. 기관 전망·상품 자료와 선택한 공개 발언에서 관측한 기대를 구분한다.",
            "",
        ]
    )
    lines.extend("- " + _statement(run, item) for item in run.sections["market_narratives"])
    lines.extend(["", "## Community에서 발견한 이야기", ""])
    lines.extend("- " + _statement(run, item, narrative=True) for item in run.sections["community"])
    lines.extend(["", "표본과 접근 범위:", ""])
    lines.extend("- " + _text(item) for item in data["sampling_limits"])
    lines.extend(
        [
            "",
            "## Narrative와 Data가 충돌하는 부분",
            "",
            "동일 사실의 모순, 투자 논리 사이의 긴장, 아직 검증하지 못한 주장을 분리한다. 확인 자료 부재를 반증으로 표현하지 않는다.",
            "",
        ]
    )
    lines.extend("- " + _statement(run, item, narrative="contrast") for item in run.sections["gaps"])
    lines.extend(["", "## 지금 더 깊게 볼 가치가 있는 영역", ""])
    candidates = [row for row in run.rows if row["priority"] == "candidate"]
    if not candidates:
        lines.append(
            "현재 근거로 후속 조사 후보를 확정할 수 없다. 후보를 강제로 만들지 않고 부족한 자료를 먼저 확인한다."
        )
    for row in candidates:
        lines.extend([f"### {_text(row['name'])}", ""])
        candidate = row["candidate"]
        for key, label in (
            ("why_now", "왜 지금인가"),
            ("changed", "무엇이 변했는가"),
            ("interesting", "흥미로운 근거"),
            ("counterargument", "가장 큰 반대 논리"),
        ):
            lines.append(f"- {label}: {_statement(run, candidate[key])}")
        lines.extend(
            [
                "- 투자 thesis로 발전시키기 전에 확인할 것: "
                + " / ".join(_text(item) for item in candidate["confirm"]),
                "",
            ]
        )
    lines.extend(["## 현재 우선순위가 낮은 영역", ""])
    for row in run.rows:
        if row["priority"] != "candidate":
            lines.append(
                f"- {_text(row['name'])} · {_PRIORITY[row['priority']]}: {_statement(run, row['priority_reason'])}. 재조사: {_statement(run, row['recheck'])}"
            )
    lines.extend(["", "## 한국 투자자에게 특별히 중요한 부분", ""])
    lines.extend("- " + _statement(run, item) for item in run.sections["korean_context"])
    lines.extend(["", "### 사용자 정보와 개인 판단 제한", "", "| 항목 | 정보 상태 | 입력 |", "| --- | --- | --- |"])
    for name, field in run.case.profile.fields.items():
        lines.append(
            f"| {_text(name)} | {_text(field.status)} | {_text(field.value) if field.value is not None else 'UNKNOWN'} |"
        )
    lines.append("")
    lines.extend("- " + _text(item) for item in run.result.constraints)
    lines.extend(["", "## 아직 모르는 것", ""])
    lines.extend("- " + _text(item) for item in run.sections["unknowns"])
    lines.extend("- " + _text(item) for item in data["comparison_limits"])
    lines.extend(["", "### 접근·자료 지원 한계", ""])
    lines.extend("- " + _text(item) for item in data["access_notes"])
    lines.extend(["", "## 다음 Research", ""])
    followup = data["next_research"]
    selected = next(row for row in run.rows if row["asset_id"] == followup["asset_id"])
    if selected["priority"] == "candidate":
        lines.extend(
            [
                "**" + _text(followup["title"]) + "**",
                "",
                _text(followup["question"]),
                "",
                "이 한 과제는 제안만 하며 이번 실행에서는 수행하지 않았다.",
            ]
        )
    else:
        lines.append("다음 연구 후보의 현재 근거가 부족해 제안을 보류한다. 먼저 차단된 자료를 확인한다.")
    lines.extend(["", "## 초간단 설명", ""])
    lines.extend(_text(item) for item in run.sections["easy"])
    lines.extend(
        [
            "",
            "## 부록 · 원문과 재현",
            "",
            f"- 입력 SHA-256: {run.input_digest}; 연구 초안 SHA-256: {run.review.input_digest}.",
            f"- 방법: {OPPORTUNITY_REPORT_VERSION}; 실행 상태: {_text(run.result.run_status)}; 개인 판단: {_text(run.result.personal_conclusion)}.",
            "- 기관 전망·과거 수치·상품 표본의 정의를 유지한다. 원문 구절의 숫자는 복사된 관측이며 계산 결과는 별도 입력·공식으로 추적한다.",
            "- 아래 인용의 지원 상태는 원문 존재 확인이다. 투자 해석과 연결된 주장은 사람이 검토 완료한 사실로 승격되지 않았다.",
        ]
    )
    for source in run.case.sources:
        provenance = source.provenance
        lines.extend(
            [
                "",
                _anchor(source.id),
                f"### 출처 · {_text(source.id)}",
                "",
                f"- {_text(provenance.publisher)} · {_text(source.name)}; source type: {_text(source.type.value)}.",
                f"- URL: [원문](<{source.location}>)",
                f"- 공개: {_text(provenance.published_at or 'UNKNOWN')}; 관측: {_text(provenance.observed_at or 'UNKNOWN')}; 유효: {_text(provenance.valid_as_of or 'UNKNOWN')}.",
                f"- 획득: {_text(provenance.retrieved_at)}; 상태: {_text(provenance.status)}; 시점 적합성: {_text(provenance.freshness)}.",
                f"- Snapshot: {provenance.snapshot_id}; payload SHA-256: {provenance.payload_sha256}.",
                f"- 보존: {_text(provenance.retention)}; 이용 조건: {_text(provenance.policy_url)} · {_text(provenance.policy_note)}.",
            ]
        )
    for evidence in run.case.evidence:
        lines.extend(
            [
                "",
                _anchor(evidence.id),
                f"### 근거 · {_text(evidence.id)}",
                "",
                f"- 출처: {_ref(evidence.source_id)}; 분류: {_text(evidence.kind)} / {_text(evidence.view)}; 해석 검토: {_text(evidence.interpretation.status.value)}.",
                f"- 원문: {_text(evidence.text)}",
                f"- 위치: {_text(evidence.locator)}; snapshot: {evidence.provenance.snapshot_id}; 구절: {_text(evidence.provenance.excerpt_id)}.",
                f"- 정의: {_text(evidence.provenance.definition)}; 시점 적합성: {_text(evidence.provenance.freshness)}.",
            ]
        )
        lines.extend("- 한계: " + _text(item) for item in evidence.limitations)
    for metric in run.result.metrics:
        original = next(item for item in run.macro.snapshot.metrics if item.id == metric.id)
        lines.extend(
            [
                "",
                _anchor(metric.id),
                f"### 계산 · {_text(metric.id)}",
                "",
                f"- {_text(metric.label)}: {_text(metric.value)} {_text(metric.unit)}; 방법: {_text(metric.method)}.",
                f"- 공식: {_text(original.formula)}; 기간: {_text(original.observation_window)}; 입력: {_refs(metric.input_ids)}.",
            ]
        )
        lines.extend("- 한계: " + _text(item) for item in metric.limitations)
    for claim in run.case.claims:
        if claim.id.startswith("OPPORTUNITY_DRAFT_"):
            continue
        lines.extend(
            [
                "",
                f"### 주장 · {_text(claim.id)}",
                "",
                f"- {_text(claim.text)}; 검증: {_text(claim.verification.value)}; 검토: {_text(claim.interpretation.status.value)}.",
                f"- 지지: {_refs(claim.support_ids)}; 반대: {_refs(claim.counter_ids)}; 맥락: {_refs(claim.context_ids)}.",
            ]
        )
        if claim.narrative_evidence_id:
            lines.append("- 서사 관측: " + _ref(claim.narrative_evidence_id))
        lines.extend("- 한계: " + _text(item) for item in claim.limitations)
    existing = (
        {item.id for item in run.case.sources}
        | {item.id for item in run.case.evidence}
        | {item.id for item in run.result.metrics}
    )
    requested = set()
    for row in run.rows:
        for key in ("state", "positive", "negative", "opportunity_cost", "priority_reason", "recheck"):
            requested.update(row[key]["evidence_ids"])
        if row["candidate"]:
            for key in ("why_now", "changed", "interesting", "counterargument"):
                requested.update(row["candidate"][key]["evidence_ids"])
    for name, items in run.sections.items():
        if name not in {"unknowns", "easy"}:
            requested.update(ref for statement in items for ref in statement["evidence_ids"])
    for identifier in sorted(requested - existing):
        lines.extend(
            [
                "",
                _anchor(identifier),
                f"### 채택 보류 · {_text(identifier)}",
                "",
                "원문 획득·시점·계산 조건이 부족하여 현재 근거로 사용하지 않았다.",
            ]
        )
    lines.extend(["", "### 무결성·검토 진단", ""])
    for row in run.rows:
        for warning in row["_warnings"]:
            lines.append("- " + _text(row["asset_id"] + ": " + warning))
    lines.extend(["", "전체 진단·자료 해시·조건별 제외 기록은 함께 생성한 실행 manifest에 보존한다."])
    return "\n".join(lines) + "\n"
