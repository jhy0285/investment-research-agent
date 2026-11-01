"""Korean templates with explicit review states and complete provenance."""

from decimal import Decimal
from datetime import date
from hashlib import sha256
from html import escape
import re

from . import __version__
from .engine import ENGINE_VERSION, REPORT_VERSION, origin_id, withheld_reason
from .models import (
    EvidenceRecord,
    InterpretationStatus,
    ResearchResult,
    Review,
    ReviewedText,
    SOURCE_HIERARCHY,
    SourceRecord,
    SourceType,
    VerificationStatus,
)

VERIFICATION_LABELS = {
    VerificationStatus.SUPPORTED: "한정된 범위에서 확인",
    VerificationStatus.PARTIAL: "일부 확인",
    VerificationStatus.CONTRADICTED: "동일한 범위에서 반박됨",
    VerificationStatus.DISPUTED: "자료가 상충함",
    VerificationStatus.UNVERIFIED: "아직 확인되지 않음",
    VerificationStatus.NOT_VERIFIABLE: "현재 자료로 확인할 수 없음",
}
REVIEW_LABELS = {
    InterpretationStatus.REVIEWED: "검토됨",
    InterpretationStatus.PENDING: "검토 대기",
    InterpretationStatus.REJECTED: "해석 채택 거부",
}
VIEW_LABELS = {
    "macro": "거시환경",
    "fundamental": "사업·기초가치",
    "quantitative": "정량",
    "community": "커뮤니티·내러티브",
}
STRENGTH_LABELS = {
    "mixed": "지지와 반대 근거가 함께 있어 판단 유보",
    "limited_support": "검토 범위의 제한적 지지 · 높은 확신을 뜻하지 않음",
    "insufficient_evidence": "현재는 강한 결론을 내릴 근거가 부족하다",
}
PROFILE_LABELS = {
    "tax_residency": "세법상 거주자 상태",
    "birth_year": "출생연도",
    "base_currency": "기준 통화",
    "life_stage": "자산 축적 단계",
    "stage": "자산 축적 단계",
    "employment_income": "근로소득",
    "employment": "근로소득",
    "investment_horizon": "투자 기간",
    "horizon": "투자 기간",
    "risk_tolerance": "위험 감수 의향",
    "total_assets": "현재 총자산",
    "emergency_fund": "비상자금",
    "debt": "부채",
    "housing_funds": "주택 구입 필요자금·시점",
    "portfolio_allocation": "현재 포트폴리오 배분·보유범위",
    "monthly_investment": "월 추가 투자 가능액",
    "risk_capacity": "위험 감당 능력",
}
UNIT_LABELS = {"percent": "%", "percentage_points": "%p (퍼센트포인트)", "basis_points": "bp (기준점)"}


def _text(value: object) -> str:
    """Render input as text, never as Markdown headings, links, HTML, or commands."""
    text = str(value).replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\n", " / ")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text)
    text = escape(text, quote=False)
    return re.sub(r"([\\`*_{}\[\]#|~])", r"\\\1", text)


def _ids(identifiers: tuple[str, ...]) -> str:
    return ", ".join(_reference(identifier) for identifier in identifiers) or "없음"


def _target(identifier: str) -> str:
    # Input IDs cannot insert HTML attributes or a Markdown link destination.
    return "record-" + sha256(identifier.encode("utf-8")).hexdigest()


def _reference(identifier: str) -> str:
    return f"[{_text(identifier)}](#{_target(identifier)})"


def _anchor(identifier: str) -> str:
    return f'<a id="{_target(identifier)}"></a>'


def _number(value: Decimal) -> str:
    return format(value, "f")


def _review(review: Review) -> str:
    return (
        f"{REVIEW_LABELS[review.status]} ({_text(review.status.value)}); "
        f"검토자: {_text(review.reviewer) if review.reviewer else '미기록'}; "
        f"검토일: {review.reviewed_at.isoformat() if review.reviewed_at else '미기록'}; "
        f"이유: {_text(review.rationale)}"
    )


def _limits(limitations: tuple[str, ...]) -> str:
    return " / ".join(_text(limit) for limit in limitations) or "입력에 별도 한계가 기록되지 않음"


def _date(value: date | None, unknown: str) -> str:
    return value.isoformat() if value is not None else f"UNKNOWN ({unknown})"


def _moment(value: str | None, unknown: str) -> str:
    return _text(value) if value else f"UNKNOWN ({unknown})"


def _source_provenance(source: SourceRecord) -> list[str]:
    provenance = source.provenance
    if provenance is None:
        return []
    return [
        f"  스냅샷: {_text(provenance.snapshot_id)}; 확보 상태: {_text(provenance.status)}; 자료 시점 적합성: {_text(provenance.freshness)}.",
        f"  발행 주체: {_text(provenance.publisher)}; 제목: {_text(provenance.title)}; 관할: {_text(provenance.jurisdiction)}; 주제: {_text(', '.join(provenance.topics))}.",
        f"  발행 시각: {_moment(provenance.published_at, '발행일 미확인')}; 관측 대상 시점: {_moment(provenance.observed_at, '관측 시점 미확인')}; 자료 적용 기준일: {_moment(provenance.valid_as_of, '적용 기준일 미확인')}.",
        f"  획득 시각: {_text(provenance.retrieved_at)}. 획득 시각은 발행일이나 당시 이용 가능 시점을 대신하지 않는다.",
        f"  접근 방법: {_text(provenance.access_method)}; 자료 형식: {_text(provenance.content_type)}; 보존 범위: {_text(provenance.retention)}.",
        f"  이용·보존 조건 출처: {_text(provenance.policy_url)}; 확인 기록: {_text(provenance.policy_note)}.",
        f"  획득 원문 SHA-256: {_text(provenance.raw_sha256) if provenance.raw_sha256 else 'UNKNOWN (원문 전체 해시 없음)'}; 정규화 자료 SHA-256: {_text(provenance.normalized_sha256) if provenance.normalized_sha256 else 'UNKNOWN (정규화 원문 해시 없음)'}.",
        f"  보존 payload SHA-256: {_text(provenance.payload_sha256)}. 원문 전체·정규화 원문·보존 구절 payload의 해시는 대상이 다르며 구절 보존을 원문 전체 보존으로 표현하지 않는다.",
    ]


def _evidence_provenance(evidence: EvidenceRecord) -> list[str]:
    provenance = evidence.provenance
    if provenance is None:
        return []
    definition = (
        "; ".join(f"{_text(key)}={_text(value)}" for key, value in sorted(provenance.definition.items()))
        or "UNKNOWN (자료 정의 미확인)"
    )
    return [
        f"  스냅샷: {_text(provenance.snapshot_id)}; 구절: {_text(provenance.excerpt_id)}; 보존 자료와의 일치 상태: {_text(provenance.match_status)}; 시점 적합성: {_text(provenance.freshness)}.",
        f"  자료 정의: {definition}.",
        "  구절 일치·시점 검사는 사실 내용·투자 해석의 의미 검토와 별도다. 과거 범위의 사실 확인 상태를 현재 투자 근거로 자동 승격하지 않는다.",
    ]


def _evidence_line(evidence: EvidenceRecord, source: SourceRecord, *, details: bool = False) -> str:
    reason = withheld_reason(evidence, source)
    designation = f"확정근거 채택 보류: {_text(reason)}" if reason else "검토 범위에서 채택 가능한 근거"
    numeric = ""
    if evidence.value is not None:
        numeric = (
            f"; 관측 수치: {_number(evidence.value)} {_text(UNIT_LABELS.get(evidence.unit, evidence.unit))}"
            f"; 기간 정의: {_text(evidence.period)}; 통화: {_text(evidence.currency or '해당 없음')}"
        )
    verification_label = (
        "발언 관측 확인(내용의 진실성 검증 아님)"
        if evidence.kind == "observed_narrative" or source.type == SourceType.COMMUNITY
        else "내용 검증"
    )
    limitation = f" 한계: {_limits(evidence.limitations)}" if details else ""
    return (
        f"- 근거 {_reference(evidence.id)} / 출처 {_reference(source.id)} / "
        f"{_text(VIEW_LABELS.get(evidence.view, evidence.view))}: "
        f"원문·관측 기록: “{_text(evidence.text)}”{numeric}. "
        f"{verification_label}: {VERIFICATION_LABELS[evidence.verification]} "
        f"({_text(evidence.verification.value)}); 해석: {REVIEW_LABELS[evidence.interpretation.status]}; "
        f"{designation}.{limitation}"
    )


def _evidence_list(
    identifiers: tuple[str, ...],
    evidence_by_id: dict[str, EvidenceRecord],
    sources: dict[str, SourceRecord],
) -> list[str]:
    if not identifiers:
        return ["- 검토한 범위에서 채택 가능한 자료 없음."]
    return [
        _evidence_line(evidence_by_id[identifier], sources[evidence_by_id[identifier].source_id])
        for identifier in identifiers
    ]


def _reviewed_text(
    record: ReviewedText,
    evidence_by_id: dict[str, EvidenceRecord],
    sources: dict[str, SourceRecord],
) -> str:
    reasons = []
    if record.interpretation.status != InterpretationStatus.REVIEWED:
        reasons.append(f"해석 검토 상태가 {record.interpretation.status.value}임")
    if not record.evidence_ids:
        reasons.append("해석을 뒷받침하는 근거 참조가 없음")
    for identifier in record.evidence_ids:
        evidence = evidence_by_id.get(identifier)
        source = sources.get(evidence.source_id) if evidence else None
        reason = withheld_reason(evidence, source) if evidence and source else "근거 또는 출처 참조가 없음"
        if reason:
            reasons.append(f"{identifier}: {reason}")
    if not reasons:
        prefix = "검토된 조건부 해석"
    else:
        prefix = "해석 채택 보류 · 입력 초안(확정 결론 아님)"
    withheld = f" 채택 보류 이유: {_text('; '.join(reasons))}." if reasons else ""
    return (
        f"{prefix}: “{_text(record.text)}” [근거: {_ids(record.evidence_ids)}]. "
        f"검토 기록: {_review(record.interpretation)}{withheld}"
    )


def render_report(result: ResearchResult) -> str:
    """Render only supplied observations, calculations, reviews, and fixed rules."""
    case = result.case
    sources = {source.id: source for source in case.sources}
    evidence_by_id = {evidence.id: evidence for evidence in case.evidence}
    alternatives = {alternative.id: alternative for alternative in case.alternatives}
    assessments = {assessment.asset_id: assessment for assessment in result.assessments}
    lines = ["# 실제 공개자료 출처 검증 브리프" if case.source_verification else "# Cross-Asset Research Brief", ""]
    if case.synthetic:
        lines.extend(
            [
                "**합성 데이터 · 개발 검증용 보고서입니다. 실제 현재 시장이나 사용자에게 적용할 투자 판단이 아닙니다.**",
                "",
            ]
        )
    elif case.source_verification:
        lines.extend(
            [
                "**실제 공개자료의 출처·보존 구절을 확인하는 사후 검토 보고서입니다. 과거 자료를 사용하며 실제 현재 시장의 투자 기회나 개인 자산배분에 대한 답이 아닙니다.**",
                "",
            ]
        )
    else:
        lines.extend(["**오프라인 입력 자료 보고서 · 기준 시점과 입력 검토 범위 안에서만 읽어야 합니다.**", ""])
    lines.extend(
        [
            "## 이번에 답하려는 질문",
            "",
            _text(case.brief.question),
            "",
            f"- 정보 기준 시점: {case.brief.as_of.isoformat()}; 기간: {_text(case.brief.horizon)}; 기준 통화: {_text(case.brief.base_currency)}.",
            f"- 사용자 정보: {_text(case.profile.id)} / {case.profile.as_of.isoformat()}; 브리프: {_text(case.brief.id)}.",
            (
                f"- 실행 상태: {_text(result.run_status)}; 투자 매력·개인 배분 판단: 미실시."
                if case.source_verification
                else f"- 실행 상태: {_text(result.run_status)}; 시장 결론 상태: {_text(result.conclusion)}; 개인 적용 상태: {_text(result.personal_conclusion)}."
            ),
            "- 실행 완료는 투자 결론의 확정을 뜻하지 않으며 결론 유보도 정상 결과다.",
            "",
            "## 한눈에 보기",
            "",
        ]
    )
    if case.synthetic:
        lines.extend(["아래 결과는 합성 자료에서 연구 경로를 확인한 결과이며 실제 시장 인사이트가 아니다.", ""])
    elif case.source_verification:
        lines.extend(
            [
                "획득 여부·구절 일치·자료 시점·정의와 주장 내용의 확인 범위를 분리해 기록한다. 자료를 확보했거나 출처 위계가 높다는 이유만으로 내용이 사실이라고 확정하지 않는다.",
                "",
            ]
        )
        if case.diagnostics:
            lines.extend(["확보·검증에서 남은 제한:", ""])
            lines.extend(f"- {_text(diagnostic)}" for diagnostic in case.diagnostics)
            lines.append("")
        if case.claims:
            lines.extend(
                [
                    "주장별 확인 범위:",
                    "",
                    "| 주장 | 내용 확인 상태 | 지지 | 반대 | 배경 |",
                    "| --- | --- | --- | --- | --- |",
                ]
            )
            for claim in case.claims:
                lines.append(
                    f"| {_text(claim.text)} | {VERIFICATION_LABELS[claim.verification]} | "
                    f"{_ids(claim.support_ids)} | {_ids(claim.counter_ids)} | {_ids(claim.context_ids)} |"
                )
            lines.append("")
    for alternative in case.alternatives:
        assessment = assessments[alternative.id]
        lines.append(
            f"- {_text(alternative.name)}: 자료 검토 범위만 연결하며 투자 매력·추천·비중 판단은 미실시."
            if case.source_verification
            else f"- {_text(alternative.name)}: {STRENGTH_LABELS[assessment.strength]} ({_text(assessment.strength)})."
        )
    lines.extend(
        [
            "- 수익 정의와 손실 경로가 다른 대안을 단일 점수·수익률 순위로 합치지 않는다.",
            "- 사용자 미확인 정보에 의존하는 배분 판단을 제한하며, 판단 유보가 현금의 우월성을 입증하지는 않는다.",
            "",
            "## 자료의 시점과 검증 범위" if case.source_verification else "## 현재 투자환경",
            "",
        ]
    )
    lines.extend(_evidence_list(case.brief.market_context_ids, evidence_by_id, sources))
    if result.metrics:
        lines.extend(["", "### 검증된 입력으로 계산한 값", ""])
        for metric in result.metrics:
            lines.extend(
                [
                    f"- [계산 {_text(metric.id)}] {_text(metric.label)}: {_number(metric.value)} {_text(UNIT_LABELS[metric.unit])}.",
                    f"  방법: {_text(metric.method)}; 입력: {_ids(metric.input_ids)}; 정의: 첫 입력의 연율 percent 값에서 두 번째 값을 뺀 단순 격차.",
                    f"  한계: {_limits(metric.limitations)}",
                ]
            )
    else:
        lines.extend(["", "정량 계산은 이번 입력에 없으며 숫자를 대신 생성하지 않았다."])
    lines.extend(["", "비교 범위와 제한:", ""])
    lines.extend(f"- {_text(limit)}" for limit in case.brief.comparison_limits)
    if not case.brief.comparison_limits:
        lines.append("- 입력에 별도 비교 제한이 기록되지 않았으며 비교 우위를 자동 확정하지 않는다.")
    lines.extend(["", "보류·제외한 연구 범위:", ""])
    lines.extend(f"- {_text(excluded)}" for excluded in case.brief.excluded)
    if not case.brief.excluded:
        lines.append("- 별도 제외 이유가 입력되지 않았다. 이 자료 묶음은 전체 투자시장을 조사한 결과가 아니다.")
    lines.extend(["", "## 투자대안별 분석", ""])
    for alternative in case.alternatives:
        assessment = assessments[alternative.id]
        lines.extend(
            [
                _anchor(alternative.id),
                "",
                f"### {_text(alternative.name)}",
                "",
                f"- 대안 ID: {_text(alternative.id)}; 경제적 노출: {_text(alternative.exposure)}.",
                f"- 수익 정의: {_text(alternative.return_definition)}.",
                f"- 유동성·보유 제약: {_text(alternative.liquidity)}.",
                (
                    "- 투자 매력·결론 강도 판단: 미실시."
                    if case.source_verification
                    else f"- 결론 강도: {STRENGTH_LABELS[assessment.strength]}."
                ),
                "",
                "**지지 근거**",
                "",
            ]
        )
        lines.extend(_evidence_list(assessment.support_ids, evidence_by_id, sources))
        lines.extend(["", "**반대 근거**", ""])
        lines.extend(_evidence_list(assessment.counter_ids, evidence_by_id, sources))
        lines.extend(["", "**기회비용 · 다른 대안을 선택하지 않을 때 포기할 가능성**", ""])
        costs = [cost for cost in case.opportunity_costs if cost.alternative_id == alternative.id]
        for cost in costs:
            lines.append(
                f"- 비교 대안: {_text(alternatives[cost.forgone_asset_id].name)}. {_reviewed_text(cost.explanation, evidence_by_id, sources)}"
            )
        if not costs:
            lines.append("- 근거와 검토 기록이 있는 설명이 입력되지 않아 개인 기회비용을 추정하지 않았다.")
        lines.extend(["", "**미확인 사항과 채택을 보류한 자료**", ""])
        lines.extend(f"- {_text(unknown)}" for unknown in alternative.unknowns)
        if assessment.withheld_ids:
            lines.extend(_evidence_list(assessment.withheld_ids, evidence_by_id, sources))
        if not alternative.unknowns and not assessment.withheld_ids:
            lines.append("- 입력에 별도 미확인 항목이 기록되지 않았으며 모든 위험이 조사되었다는 뜻은 아니다.")
        if assessment.duplicate_origin_ids:
            lines.extend(
                [
                    "",
                    f"동일 원출처 중복: {_ids(assessment.duplicate_origin_ids)}. 해당 재인용·관측은 별도의 독립 근거로 세지 않는다.",
                ]
            )
        metrics = [metric for metric in result.metrics if alternative.id in metric.asset_ids]
        if metrics:
            lines.extend(
                [
                    "",
                    f"관련 계산 ID: {_ids(tuple(metric.id for metric in metrics))}. 계산은 별도 결과이며 지지·반대 근거의 독립 확인으로 중복 계산하지 않는다.",
                ]
            )
        lines.append("")
    lines.extend(["## 커뮤니티에서는 무엇을 말하고 있는가", ""])
    narratives = [
        evidence
        for evidence in case.evidence
        if evidence.kind == "observed_narrative" or sources[evidence.source_id].type == SourceType.COMMUNITY
    ]
    if not narratives:
        lines.extend(["관측한 커뮤니티 자료가 없으며 시장 참여자의 의견을 대신 만들지 않았다.", ""])
    for narrative in narratives:
        source = sources[narrative.source_id]
        lines.extend(
            [
                f"### 관측한 발언 · {_text(narrative.id)}",
                "",
                f"발언 자료 원문: “{_text(narrative.text)}” [출처: {_text(source.id)}; 위치: {_text(narrative.locator)}; 관측일: {_date(narrative.observed_at, '관측일 미확인')}].",
                "",
                f"발언 기록의 확인 상태: {VERIFICATION_LABELS[narrative.verification]}; 해석 기록: {_review(narrative.interpretation)}.",
                "",
                "발언의 존재와 발언 내용의 진실성은 다르다. 이 자료는 투자 사실 근거로 채택하지 않으며, 반복·인기도는 독립 확인이나 미래 수익 확률이 아니다.",
                "",
            ]
        )
        linked = [claim for claim in case.claims if claim.narrative_evidence_id == narrative.id]
        for claim in linked:
            lines.extend(
                [
                    f"**내용 검증 대상 · 주장 {_text(claim.id)}**",
                    "",
                    f"입력된 주장 원문: “{_text(claim.text)}”.",
                    "",
                    f"내용의 검증 상태: {VERIFICATION_LABELS[claim.verification]} ({_text(claim.verification.value)}); 해석: {_review(claim.interpretation)}.",
                    "",
                    "지지 자료와 각 자료의 채택 상태:",
                    "",
                ]
            )
            lines.extend(_evidence_list(claim.support_ids, evidence_by_id, sources))
            lines.extend(["", "반대 자료와 각 자료의 채택 상태:", ""])
            lines.extend(_evidence_list(claim.counter_ids, evidence_by_id, sources))
            if claim.context_ids:
                lines.extend(["", "배경 자료 · 내용의 지지·반대 근거와 별도:", ""])
                lines.extend(_evidence_list(claim.context_ids, evidence_by_id, sources))
            lines.extend(
                [
                    "",
                    f"확인하지 못한 범위·한계: {_limits(claim.limitations)}.",
                    "",
                    f"재검토 질문(주장 검토 기록): {_text(claim.recheck)}.",
                    "",
                ]
            )
        if not linked:
            lines.extend(["내용 검증의 별도 Claim 기록이 없어 내용은 미확인 상태로 남긴다.", ""])
    lines.extend(
        [
            "## 서로 충돌하는 근거",
            "",
            "투자 논리의 긴장은 긍정·부정 요인이 공존한다는 뜻이다. 동일한 사실의 모순을 자동 판정한 것이 아니며, 내용 검증 기록의 반박·상충 상태와 구분한다.",
            "",
        ]
    )
    tension = False
    for alternative in case.alternatives:
        assessment = assessments[alternative.id]
        if case.source_verification:
            continue
        if assessment.support_ids and assessment.counter_ids:
            tension = True
            lines.append(
                f"- 투자 논리의 긴장: {_text(alternative.name)}의 지지 [{_ids(assessment.support_ids)}]와 "
                f"반대 [{_ids(assessment.counter_ids)}]가 함께 남는다."
            )
    for claim in case.claims:
        if claim.verification in (VerificationStatus.CONTRADICTED, VerificationStatus.DISPUTED):
            tension = True
            lines.append(
                f"- 내용 검증 기록의 충돌: 주장 {_text(claim.id)}는 {VERIFICATION_LABELS[claim.verification]} "
                f"({_text(claim.verification.value)}). 입력 원문: “{_text(claim.text)}”; "
                f"지지 [{_ids(claim.support_ids)}]; 반대 [{_ids(claim.counter_ids)}]; "
                f"검토 이유: {_text(claim.interpretation.rationale)}. "
                "동일 범위의 사실 반박 상태와 투자 전망의 불확실성을 구분해서 읽어야 한다."
            )
        elif case.source_verification and claim.context_ids and claim.narrative_evidence_id:
            tension = True
            lines.append(
                f"- 원문과 해석의 비교(자동 반증 아님): 주장 {_text(claim.id)}는 "
                f"{VERIFICATION_LABELS[claim.verification]}. 관측된 발언 {_reference(claim.narrative_evidence_id)}; "
                f"지지 [{_ids(claim.support_ids)}]; 반대 [{_ids(claim.counter_ids)}]; "
                f"배경 [{_ids(claim.context_ids)}]. 검토 범위: {_limits(claim.limitations)}. "
                "배경 자료와 서사의 대상·정의 차이를 보존하며 서로 다른 범위를 같은 사실의 모순으로 판정하지 않는다."
            )
    if not tension:
        lines.append(
            "- 입력된 채택 근거·검토 기록에서는 충돌이 표시되지 않았다. 반대 자료가 존재하지 않거나 모든 충돌이 해소되었다는 뜻은 아니다."
        )
    lines.extend(["", "## 내 상황에서는 무엇이 아직 필요한가", ""])
    for name in sorted(case.profile.fields):
        field = case.profile.fields[name]
        value = "UNKNOWN · 미확인" if field.status == "unknown" or field.value is None else _text(field.value)
        lines.append(f"- {_text(PROFILE_LABELS.get(name, name))}: {value}; 정보 상태: {_text(field.status)}.")
    lines.extend(["", "미확인 정보가 제한하는 판단:", ""])
    lines.extend(f"- {_text(constraint)}" for constraint in result.constraints)
    if not result.constraints:
        lines.append(
            "- 주요 개인 입력에 unknown은 없지만 자기보고의 정확성·보유범위와 실제 적용 조건은 별도로 검토해야 한다."
        )
    lines.extend(
        [
            "",
            "위험 감수 의향은 심리적 의향이고 위험 감당 능력은 생활과 의무지출을 유지할 재무 능력이다. 나이·안정적 소득·장기 투자 가능성은 자산의 미래 기대수익을 증명하지 않는다.",
            "",
            "## 현재 얻을 수 있는 Insight",
            "",
        ]
    )
    for alternative in case.alternatives:
        assessment = assessments[alternative.id]
        if case.source_verification:
            lines.append(
                f"- {_text(alternative.name)}: 출처 자료의 구절·시점·정의를 확인하는 범위이며 투자 기회나 다른 대안 대비 우위는 판단하지 않았다."
            )
            continue
        if assessment.strength == "mixed":
            insight = "지지와 반대의 전달 경로를 함께 재검토할 이유가 있으며, 현재 근거로 다른 대안보다 우월하다고 확정할 수 없다"
        elif assessment.strength == "limited_support":
            insight = "검토한 범위에 지지 근거가 있어 후속 조사 대상으로 남길 수 있지만, 반대 자료의 부재가 높은 확신이나 투자 우위를 뜻하지는 않는다"
        else:
            insight = "현재는 강한 결론을 내릴 근거가 부족하며, 필요한 출처·내용 검증·해석 검토를 먼저 확인해야 한다"
        lines.append(
            f"- {_text(alternative.name)}: {insight}. 지지 [{_ids(assessment.support_ids)}]; 반대 [{_ids(assessment.counter_ids)}]; 보류 [{_ids(assessment.withheld_ids)}]."
        )
    lines.extend(
        [
            (
                "- 출처 확보·구절 일치·시점 적합성은 별도 검사 결과다. 주장 내용은 명시한 좁은 확인 범위와 입력 검토 기록에서만 읽으며 의미 전체가 자동 검증되었다고 주장하지 않는다."
                if case.source_verification
                else "- 이 결론 강도는 채택 가능한 지지·반대 근거의 존재에 따른 정성 상태다. 근거 개수·출처 등급으로 신뢰도 점수나 자산 순위를 만들지 않는다."
            ),
            "- 개인 적용: "
            + (
                "이번 실행은 개인 자산배분의 적절성을 판단하지 않는다."
                if case.source_verification
                else (
                    "미확인 정보 또는 지지 근거 부족으로 개인 자산배분의 적절성은 판단 유보한다."
                    if result.personal_conclusion == "insufficient_evidence"
                    else "입력된 개인 조건의 범위에서 추가 검토할 수 있지만 자산 비중·매수·매도를 자동 결정하지 않는다."
                )
            ),
            "- 결론 유보는 현금의 우위를 뜻하지 않는다. 자료가 다른 대안의 수익·위험·유동성 차이를 충분히 설명하는지 확인해야 한다.",
            "",
            "## 무엇이 바뀌면 다시 봐야 하는가",
            "",
        ]
    )
    rechecks = False
    for alternative in case.alternatives:
        for record in alternative.recheck:
            rechecks = True
            lines.append(f"- {_text(alternative.name)}: {_reviewed_text(record, evidence_by_id, sources)}")
    for claim in case.claims:
        rechecks = True
        label = (
            "검토 기록의 재검토 조건"
            if claim.interpretation.status == InterpretationStatus.REVIEWED
            else "채택 보류한 주장 초안의 재검토 질문"
        )
        lines.append(
            f"- 주장 {_text(claim.id)} / {label}: {_text(claim.recheck)}. 검토: {REVIEW_LABELS[claim.interpretation.status]}."
        )
    if not rechecks:
        lines.append("- 근거를 연결한 재검토 조건이 입력되지 않아 임의의 촉매·가격 목표를 만들지 않았다.")
    lines.extend(
        [
            "- 사용자 미확인 정보가 확인되거나 자료·검증 상태가 달라지면 새 입력 버전으로 연구를 다시 실행한다.",
            "",
            "## 초간단 설명",
            "",
            (
                "이 보고서는 합성 자료로 현금성 자산·국채·주식을 비교하는 연구 과정을 시험한 결과다."
                if case.synthetic
                else (
                    "이 보고서는 과거 공개자료의 출처와 구절을 확인하는 사후 검토다."
                    if case.source_verification
                    else "이 보고서는 입력 자료가 허용하는 범위에서 투자대안의 근거를 비교한 결과다."
                )
            ),
            (
                "글을 확보하고 구절을 대조했다는 사실만으로 내용 전체가 참이라고 확정할 수 없다."
                if case.source_verification
                else "좋은 점과 나쁜 점을 함께 보고, 정보가 부족하면 결론을 기다린다."
            ),
            "인터넷에서 누가 한 말과 그 말이 사실이라는 것은 다르다.",
            (
                "옛 자료가 맞았다고 해서 현재 투자 기회가 확인된 것은 아니다."
                if case.source_verification
                else "내가 가진 돈·부채·앞으로 쓸 돈을 모르면 나에게 맞는 비중을 정할 수 없다."
            ),
            (
                "자료의 시점과 정의를 다시 확인해야 현재 질문에 쓸 수 있다."
                if case.source_verification
                else "지금 결론을 기다려도 현금의 우위가 증명된 것은 아니다."
            ),
            "",
            "## 부록 · 근거와 재현 기록",
            "",
            f"- 실행 ID: {_text(result.run_id)}; 입력 SHA-256: {_text(case.input_digest)}.",
            f"- 스키마: {_text(case.schema_version)}; 코드 버전: {__version__}; 근거 규칙: {ENGINE_VERSION}; 보고서: {REPORT_VERSION}.",
            "- 구조·참조·시점 검증과 결정적 계산은 내용·해석의 의미, 미래 성과 또는 사용자 적합성을 자동 보증하지 않는다.",
            "- 숫자는 등록된 관측 또는 계산에서 삽입했다. 인용문·조건부 해석은 입력된 검토 기록의 범위에서 표시했다.",
            "",
            "### 출처 목록",
            "",
        ]
    )
    for source in case.sources:
        lines.extend(
            [
                _anchor(source.id),
                "",
                f"- 출처 {_text(source.id)}: {_text(source.name)}; 유형: {_text(source.type.value)}; 확인 우선순위: {SOURCE_HIERARCHY[source.type]} (신뢰도 점수가 아님).",
                f"  위치: {_text(source.location)}; 공개일: {_date(source.published_at, '발행일 미확인')}; 이용 가능일: {_date(source.available_at, '당시 이용 가능 시점 미확인')}; 획득일: {source.retrieved_at.isoformat()}.",
                f"  직접 원출처: {_text(source.origin_source_id) if source.origin_source_id else '재인용 관계 없음'}; 추적한 원출처 ID: {_text(origin_id(source, sources))}; 한계: {_limits(source.limitations)}.",
            ]
        )
        lines.extend(_source_provenance(source))
    lines.extend(["", "### 근거 목록", ""])
    for evidence in case.evidence:
        source = sources[evidence.source_id]
        lines.extend(
            [
                _anchor(evidence.id),
                "",
                _evidence_line(evidence, source, details=True),
                f"  유형: {_text(evidence.kind)}; 위치: {_text(evidence.locator)}; 관측일: {_date(evidence.observed_at, '관측일 미확인')}; 분석일: {evidence.analyzed_at.isoformat()}; 자산 범위: {_ids(evidence.asset_ids)}.",
                f"  해석 검토 기록: {_review(evidence.interpretation)}.",
            ]
        )
        lines.extend(_evidence_provenance(evidence))
    lines.extend(["", "### 주장 목록 · 사실 검증과 해석 검토는 별도", ""])
    if not case.claims:
        lines.append("- 입력된 주장 없음.")
    for claim in case.claims:
        lines.extend(
            [
                _anchor(claim.id),
                "",
                f"- 주장 {_text(claim.id)} / 입력 원문: “{_text(claim.text)}”; 자산 범위: {_ids(claim.asset_ids)}.",
                f"  내용 검증: {VERIFICATION_LABELS[claim.verification]} ({_text(claim.verification.value)}); 해석 기록: {_review(claim.interpretation)}.",
                f"  지지: {_ids(claim.support_ids)}; 반대: {_ids(claim.counter_ids)}; 발언 관측: {_text(claim.narrative_evidence_id) if claim.narrative_evidence_id else '없음'}.",
                f"  한계: {_limits(claim.limitations)}; 재검토 질문: {_text(claim.recheck)}.",
            ]
        )
        if claim.context_ids:
            lines.append(f"  배경 자료(지지·반대 근거와 별도): {_ids(claim.context_ids)}.")
    lines.extend(["", "### 계산 목록", ""])
    if not result.metrics:
        lines.append("- 입력된 계산 없음.")
    for metric in result.metrics:
        lines.extend(
            [
                _anchor(metric.id),
                "",
                f"- 계산 {_text(metric.id)}: {_text(metric.label)} = {_number(metric.value)} {_text(UNIT_LABELS[metric.unit])}; 방법: {_text(metric.method)}.",
                f"  입력: {_ids(metric.input_ids)}; 자산 범위: {_ids(metric.asset_ids)}; 단위 코드: {_text(metric.unit)}; 한계: {_limits(metric.limitations)}.",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
