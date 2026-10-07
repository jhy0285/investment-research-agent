"""Small immutable contracts. Verification records are supplied reviews, not truth scores."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum


class SourceType(StrEnum):
    PRIMARY = "primary"
    INSTITUTION = "institution"
    DATA_PROVIDER = "data_provider"
    RESEARCH = "research"
    NEWS = "news"
    EXPERT = "expert"
    COMMUNITY = "community"


SOURCE_HIERARCHY = {
    SourceType.PRIMARY: 1,
    SourceType.INSTITUTION: 2,
    SourceType.DATA_PROVIDER: 3,
    SourceType.RESEARCH: 4,
    SourceType.NEWS: 4,
    SourceType.EXPERT: 5,
    SourceType.COMMUNITY: 6,
}


class VerificationStatus(StrEnum):
    SUPPORTED = "supported_within_scope"
    PARTIAL = "partially_supported"
    CONTRADICTED = "contradicted_within_scope"
    DISPUTED = "disputed"
    UNVERIFIED = "unverified"
    NOT_VERIFIABLE = "not_verifiable"


class InterpretationStatus(StrEnum):
    REVIEWED = "reviewed"
    PENDING = "pending"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Review:
    status: InterpretationStatus
    reviewer: str | None
    reviewed_at: date | None
    rationale: str


@dataclass(frozen=True)
class SourceProvenance:
    snapshot_id: str
    publisher: str
    title: str
    retrieved_at: str
    jurisdiction: str
    topics: tuple[str, ...]
    content_type: str
    access_method: str
    policy_url: str
    policy_note: str
    retention: str
    raw_sha256: str | None
    normalized_sha256: str | None
    payload_sha256: str
    status: str
    published_at: str | None
    observed_at: str | None
    valid_as_of: str | None
    freshness: str


@dataclass(frozen=True)
class EvidenceProvenance:
    snapshot_id: str
    excerpt_id: str
    match_status: str
    freshness: str
    definition: dict[str, str | None]


@dataclass(frozen=True)
class SourceRecord:
    id: str
    type: SourceType
    name: str
    location: str
    published_at: date | None
    available_at: date | None
    retrieved_at: date
    origin_source_id: str | None
    limitations: tuple[str, ...]
    provenance: SourceProvenance | None = None


@dataclass(frozen=True)
class EvidenceRecord:
    id: str
    source_id: str
    text: str
    locator: str
    observed_at: date | None
    analyzed_at: date
    asset_ids: tuple[str, ...]
    view: str
    kind: str
    verification: VerificationStatus
    interpretation: Review
    limitations: tuple[str, ...]
    value: Decimal | None
    unit: str | None
    period: str | None
    currency: str | None
    provenance: EvidenceProvenance | None = None


@dataclass(frozen=True)
class ResearchClaim:
    id: str
    text: str
    asset_ids: tuple[str, ...]
    verification: VerificationStatus
    interpretation: Review
    support_ids: tuple[str, ...]
    counter_ids: tuple[str, ...]
    narrative_evidence_id: str | None
    limitations: tuple[str, ...]
    recheck: str
    context_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReviewedText:
    text: str
    evidence_ids: tuple[str, ...]
    interpretation: Review


@dataclass(frozen=True)
class OpportunityCost:
    alternative_id: str
    forgone_asset_id: str
    explanation: ReviewedText


@dataclass(frozen=True)
class Alternative:
    id: str
    name: str
    exposure: str
    return_definition: str
    liquidity: str
    support_ids: tuple[str, ...]
    counter_ids: tuple[str, ...]
    unknowns: tuple[str, ...]
    recheck: tuple[ReviewedText, ...]


@dataclass(frozen=True)
class ProfileField:
    status: str
    value: str | int | bool | None


@dataclass(frozen=True)
class ProfileSnapshot:
    id: str
    as_of: date
    fields: dict[str, ProfileField]


@dataclass(frozen=True)
class ResearchBrief:
    id: str
    question: str
    as_of: date
    base_currency: str
    horizon: str
    market_context_ids: tuple[str, ...]
    excluded: tuple[str, ...]
    comparison_limits: tuple[str, ...]


@dataclass(frozen=True)
class CalculationSpec:
    id: str
    label: str
    method: str
    input_ids: tuple[str, ...]
    asset_ids: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class MetricResult:
    id: str
    label: str
    value: Decimal
    unit: str
    method: str
    input_ids: tuple[str, ...]
    asset_ids: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ResearchCase:
    schema_version: str
    synthetic: bool
    brief: ResearchBrief
    profile: ProfileSnapshot
    sources: tuple[SourceRecord, ...]
    evidence: tuple[EvidenceRecord, ...]
    claims: tuple[ResearchClaim, ...]
    alternatives: tuple[Alternative, ...]
    calculations: tuple[CalculationSpec, ...]
    opportunity_costs: tuple[OpportunityCost, ...]
    input_digest: str
    source_verification: bool = False
    diagnostics: tuple[str, ...] = ()


@dataclass(frozen=True)
class AlternativeAssessment:
    asset_id: str
    strength: str
    support_ids: tuple[str, ...]
    counter_ids: tuple[str, ...]
    withheld_ids: tuple[str, ...]
    duplicate_origin_ids: tuple[str, ...]


@dataclass(frozen=True)
class ResearchResult:
    case: ResearchCase
    metrics: tuple[MetricResult, ...]
    assessments: tuple[AlternativeAssessment, ...]
    run_status: str
    conclusion: str
    personal_conclusion: str
    constraints: tuple[str, ...]
    run_id: str
