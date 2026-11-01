"""Deterministic evidence processing, without ranking or invented market conclusions."""

from decimal import Context, Decimal, localcontext
from hashlib import sha256

from . import __version__
from .models import (
    AlternativeAssessment,
    EvidenceRecord,
    InterpretationStatus,
    MetricResult,
    ResearchCase,
    ResearchResult,
    SourceRecord,
    SourceType,
    VerificationStatus,
)

ENGINE_VERSION = "evidence_rules_v1"
REPORT_VERSION = "korean_brief_v1"
RATE_DIFFERENCE_LIMIT = (
    "두 연율 관측값의 단순 격차다. 관측 물가를 대입해도 미래 실질수익, "
    "확정 투자성과 또는 자산 간 우위를 뜻하지 않는다. 비용·세금·가격변화는 계산하지 않았다."
)

PROFILE_CONSTRAINTS = (
    ("total_assets", "총자산이 미확인이라 실제 손실 감당 규모와 전체 자산 대비 투자금의 크기를 판단할 수 없다."),
    ("emergency_fund", "비상자금이 미확인이라 현금 비중이 과도하거나 추가 투자에 충분하다고 판단할 수 없다."),
    ("debt", "부채가 미확인이라 무부채로 가정하거나 부채 상환과 투자 사이의 개인 기회비용을 판단할 수 없다."),
    ("housing_funds", "주택 구입 필요자금과 시점이 미확인이라 장기간 자금이 묶이는 선택의 적절성을 판단할 수 없다."),
    (
        "portfolio_allocation",
        "현재 포트폴리오 배분과 보유범위가 미확인이라 전체 집중위험이나 분산·안전성을 판단할 수 없다.",
    ),
    ("monthly_investment", "월 추가 투자 가능액이 미확인이라 안정적인 근로소득에서 투자 가능 금액을 추정할 수 없다."),
    (
        "risk_capacity",
        "위험 감당 능력이 미확인이라 나이·소득·위험 감수 의향에서 손실 한도·투자 비중·레버리지 허용을 도출할 수 없다.",
    ),
)


def withheld_reason(evidence: EvidenceRecord, source: SourceRecord) -> str | None:
    """An observed utterance is never evidence that its financial content is true."""
    reasons = []
    if evidence.kind == "observed_narrative" or source.type == SourceType.COMMUNITY:
        reasons.append("발언·내러티브 관측이며 내용의 사실 근거로 채택하지 않음")
    if evidence.verification != VerificationStatus.SUPPORTED:
        reasons.append(f"내용 검증 상태가 {evidence.verification.value}임")
    if evidence.interpretation.status != InterpretationStatus.REVIEWED:
        reasons.append(f"해석 검토 상태가 {evidence.interpretation.status.value}임")
    if evidence.provenance is not None:
        if evidence.provenance.match_status != "matched":
            reasons.append(f"보존 자료와 구절의 일치 상태가 {evidence.provenance.match_status}임")
        if evidence.provenance.freshness != "fresh":
            reasons.append(
                f"자료의 시점 적합성이 {evidence.provenance.freshness}임; 과거 사실 확인과 현재 적용은 별도임"
            )
    return "; ".join(reasons) if reasons else None


def evidence_usable(evidence: EvidenceRecord, source: SourceRecord) -> bool:
    return withheld_reason(evidence, source) is None


def origin_id(source: SourceRecord, sources: dict[str, SourceRecord]) -> str:
    """Resolve an origin chain; the loader rejects missing origins and cycles."""
    seen = set()
    while source.origin_source_id is not None:
        if source.id in seen:
            raise ValueError("원출처 관계에 순환이 있습니다.")
        seen.add(source.id)
        source = sources[source.origin_source_id]
    return source.id


def _metrics(
    case: ResearchCase,
    evidence_by_id: dict[str, EvidenceRecord],
    sources: dict[str, SourceRecord],
) -> tuple[MetricResult, ...]:
    metrics = []
    for spec in case.calculations:
        if spec.method != "rate_difference_v1" or len(spec.input_ids) != 2:
            raise ValueError("지원 계산은 두 입력을 받는 rate_difference_v1뿐입니다.")
        inputs = [evidence_by_id[identifier] for identifier in spec.input_ids]
        for evidence in inputs:
            if (
                not evidence_usable(evidence, sources[evidence.source_id])
                or evidence.value is None
                or not isinstance(evidence.value, Decimal)
                or not evidence.value.is_finite()
                or evidence.unit != "percent"
                or evidence.period != "annual_rate"
            ):
                raise ValueError("금리 격차 입력은 검토된 유한 연율 percent 관측값이어야 합니다.")
        if inputs[0].currency != inputs[1].currency:
            raise ValueError("금리 격차 입력의 통화가 서로 다릅니다.")
        # A fresh Context avoids ambient precision, rounding, or trap changes.
        # The loader bounds numeric input size; ample precision keeps subtraction exact.
        precision = max(
            34,
            sum(len(e.value.as_tuple().digits) + abs(e.value.as_tuple().exponent) for e in inputs) + 4,
        )
        with localcontext(Context(prec=precision)):
            value = inputs[0].value - inputs[1].value
        metrics.append(
            MetricResult(
                id=spec.id,
                label=spec.label,
                value=value,
                unit="percentage_points",
                method=spec.method,
                input_ids=spec.input_ids,
                asset_ids=spec.asset_ids,
                limitations=(*spec.limitations, RATE_DIFFERENCE_LIMIT),
            )
        )
    return tuple(metrics)


def run_research(case: ResearchCase) -> ResearchResult:
    """Process a validated case; inconclusive research is a completed run."""
    sources = {source.id: source for source in case.sources}
    evidence_by_id = {evidence.id: evidence for evidence in case.evidence}
    metrics = _metrics(case, evidence_by_id, sources)
    assessments = []
    for alternative in case.alternatives:
        support = []
        counter = []
        withheld = []
        origins = []
        duplicate_origins = []
        for identifiers, accepted in (
            (alternative.support_ids, support),
            (alternative.counter_ids, counter),
        ):
            for identifier in identifiers:
                evidence = evidence_by_id[identifier]
                source = sources[evidence.source_id]
                if not evidence_usable(evidence, source):
                    if identifier not in withheld:
                        withheld.append(identifier)
                    continue
                accepted.append(identifier)
                origin = origin_id(source, sources)
                if origin in origins and origin not in duplicate_origins:
                    duplicate_origins.append(origin)
                origins.append(origin)
        strength = "mixed" if support and counter else "limited_support" if support else "insufficient_evidence"
        assessments.append(
            AlternativeAssessment(
                asset_id=alternative.id,
                strength=strength,
                support_ids=tuple(support),
                counter_ids=tuple(counter),
                withheld_ids=tuple(withheld),
                duplicate_origin_ids=tuple(duplicate_origins),
            )
        )
    constraints = tuple(
        explanation
        for name, explanation in PROFILE_CONSTRAINTS
        if name not in case.profile.fields
        or case.profile.fields[name].status == "unknown"
        or case.profile.fields[name].value is None
    )
    has_support = any(assessment.support_ids for assessment in assessments)
    manifest = "|".join((case.input_digest, __version__, ENGINE_VERSION, REPORT_VERSION))
    return ResearchResult(
        case=case,
        metrics=metrics,
        assessments=tuple(assessments),
        run_status="completed",
        conclusion="conditional" if has_support else "insufficient_evidence",
        personal_conclusion="insufficient_evidence" if constraints or not has_support else "conditional",
        constraints=constraints,
        run_id=sha256(manifest.encode("utf-8")).hexdigest(),
    )
