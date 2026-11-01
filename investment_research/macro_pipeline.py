"""Explicit macro acquisition, pinned replay, and existing research evidence links."""

from __future__ import annotations

import base64
import csv
from dataclasses import MISSING, asdict, dataclass, field, fields
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import io
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from .macro import (
    MACRO_VERSION,
    MacroError,
    MacroObservation,
    MacroSnapshot,
    SeriesDefinition,
    build_macro_snapshot,
    make_registry,
    _cutoff,
)
from .models import (
    EvidenceProvenance,
    EvidenceRecord,
    InterpretationStatus,
    MetricResult,
    ProfileField,
    ProfileSnapshot,
    ResearchBrief,
    ResearchCase,
    ResearchClaim,
    Review,
    SourceProvenance,
    SourceRecord,
    SourceType,
    VerificationStatus,
)
from .source_pipeline import _digest, _id, _object, _strings, load_pins
from .sources import SOURCE_VERSION, SourceSpec, Snapshot, _parse_json, _time, _validate, acquire, load_snapshot

MACRO_PIPELINE_VERSION = "macro_pipeline_v1"
ASSETS = ("CASH", "BOND", "EQUITY")


@dataclass(frozen=True)
class MacroBinding:
    series_id: str
    source_id: str
    adapter: str
    field: str
    start_date: date
    release_source_id: str | None = None


@dataclass(frozen=True)
class MacroPlan:
    id: str
    question: str
    series: tuple[SeriesDefinition, ...]
    sources: tuple[SourceSpec, ...]
    bindings: tuple[MacroBinding, ...]
    yoy_series_ids: tuple[str, ...]
    yield_pair: tuple[str, str] | None
    input_digest: str


@dataclass(frozen=True)
class MacroRun:
    plan: MacroPlan
    snapshot: MacroSnapshot
    case: ResearchCase
    metrics: tuple[MetricResult, ...]
    snapshot_refs: dict[str, list[str]]
    input_digest: str
    diagnostics: tuple[str, ...]
    release_provenance: dict[str, dict] = field(default_factory=dict)

    @property
    def as_of(self) -> datetime:
        return self.snapshot.as_of


def _construct(cls, data: dict, where: str):
    spec = {item.name: item for item in fields(cls)}
    required = {name for name, item in spec.items() if item.default is MISSING and item.default_factory is MISSING}
    _object(data, required, set(spec) - required, where)
    try:
        return cls(**data)
    except (TypeError, AttributeError) as exc:
        raise MacroError(f"{where}: invalid contract") from exc


def _day(value: str) -> date:
    try:
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError()
        return date.fromisoformat(value)
    except ValueError as exc:
        raise MacroError("expected ISO observation date") from exc


def load_macro_plan(path: str | Path) -> MacroPlan:
    path = Path(path)
    path = path / "plan.json" if path.is_dir() else path
    data = load_pins(path)  # Shared bounded, strict JSON reader; no network.
    _object(
        data,
        {"schema_version", "id", "question", "series", "sources", "bindings", "yoy_series_ids", "yield_pair"},
        set(),
        "macro plan",
    )
    if data["schema_version"] != "1":
        raise MacroError("unsupported macro plan schema")
    _id(data["id"], "macro plan.id")
    if not isinstance(data["question"], str) or not data["question"].strip():
        raise MacroError("macro question required")
    for key in ("series", "sources", "bindings", "yoy_series_ids"):
        if not isinstance(data[key], list) or len(data[key]) > 20:
            raise MacroError(f"{key}: bounded array required")
    definitions = tuple(_construct(SeriesDefinition, item, "series") for item in data["series"])
    registry = make_registry(definitions)
    if not registry or len(registry) != len(definitions):
        raise MacroError("unique, nonempty series registry required")
    specifications = []
    for item in data["sources"]:
        if not isinstance(item, dict):
            raise MacroError("sources: object required")
        item = dict(item)
        for key in ("topics", "asset_ids", "excerpts"):
            if key in item:
                item[key] = tuple(item[key])
        source = _construct(SourceSpec, item, "sources")
        _validate(source)
        specifications.append(source)
    sources = {item.id: item for item in specifications}
    if not sources or len(sources) != len(specifications):
        raise MacroError("unique, nonempty sources required")
    bindings = []
    for raw in data["bindings"]:
        if not isinstance(raw, dict):
            raise MacroError("bindings: object required")
        item = dict(raw)
        item["start_date"] = _day(item.get("start_date"))
        binding = _construct(MacroBinding, item, "bindings")
        if binding.series_id not in registry or binding.source_id not in sources:
            raise MacroError("binding references an unknown series or source")
        definition = registry[binding.series_id]
        if definition.source_id != binding.source_id or definition.publisher != sources[binding.source_id].publisher:
            raise MacroError("definition and source identity differ")
        if (
            binding.adapter not in {"bls_cpi_v1", "fed_csv_v1", "ecos_daily_v1", "ecos_context_v1"}
            or not isinstance(binding.field, str)
            or not binding.field
        ):
            raise MacroError("unsupported reviewed macro adapter")
        if sources[binding.source_id].retention != "full":
            raise MacroError("macro observations require permitted full raw retention")
        if binding.release_source_id is not None and binding.release_source_id not in sources:
            raise MacroError("unknown release source")
        bindings.append(binding)
    if {item.series_id for item in bindings} != set(registry) or len(bindings) != len(registry):
        raise MacroError("exactly one binding per canonical series required")
    yoy_ids = _strings(data["yoy_series_ids"], "yoy series", True)
    pair = data["yield_pair"]
    if pair is not None:
        pair = _strings(pair, "yield pair", True)
        if len(pair) != 2:
            raise MacroError("yield pair requires 10Y and 2Y")
    if not set(yoy_ids).union(pair or ()) <= set(registry):
        raise MacroError("transformation references unknown series")
    ids = [data["id"], *registry, *sources]
    if len(ids) != len(set(ids)):
        raise MacroError("plan, source and canonical series IDs must differ")
    return MacroPlan(
        data["id"], data["question"], definitions, tuple(specifications), tuple(bindings), yoy_ids, pair, _digest(data)
    )


def _validate_pins(plan: MacroPlan, pins: dict) -> None:
    _object(pins, {"schema_version", "plan_id", "plan_sha256", "as_of", "snapshots"}, set(), "macro pins")
    if (
        pins["schema_version"] != "macro-pins-v1"
        or pins["plan_id"] != plan.id
        or pins["plan_sha256"] != plan.input_digest
    ):
        raise MacroError("macro pins do not match the reviewed plan")
    if not isinstance(pins["snapshots"], dict) or set(pins["snapshots"]) != {s.id for s in plan.sources}:
        raise MacroError("pins must reference exactly the reviewed sources")
    if _time(pins["as_of"]) is None:
        raise MacroError("pins require a fixed as_of timestamp")
    for values in pins["snapshots"].values():
        if (
            not isinstance(values, list)
            or not values
            or len(values) > 100
            or any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value) for value in values)
            or len(set(values)) != len(values)
        ):
            raise MacroError("pins require unique bounded snapshot IDs")


def acquire_macro(
    plan: MacroPlan, store: str | Path, previous_pins: dict | None = None, fetcher=None, now: datetime | None = None
) -> dict:
    """The only macro network boundary. Keep earlier observed versions explicitly."""
    if previous_pins is not None:
        _validate_pins(plan, previous_pins)
        specs = {spec.id: spec for spec in plan.sources}
        for key, refs in previous_pins["snapshots"].items():
            if len(refs) >= 100:
                raise MacroError("pinned history limit reached; no acquisition was performed")
            for ref in refs:
                prior = load_snapshot(store, key, ref)
                if _digest(prior.source) != _digest(asdict(specs[key])):
                    raise MacroError("previous snapshot metadata differs from the reviewed plan")
    snapshots = {spec.id: list(previous_pins["snapshots"][spec.id]) if previous_pins else [] for spec in plan.sources}
    for spec in plan.sources:
        shot = acquire(spec, store, fetcher=fetcher, now=now)
        if shot.snapshot_id not in snapshots[spec.id]:
            snapshots[spec.id].append(shot.snapshot_id)
    at = now if now is not None else datetime.now(timezone.utc)
    return {
        "schema_version": "macro-pins-v1",
        "plan_id": plan.id,
        "plan_sha256": plan.input_digest,
        "as_of": _cutoff(at).isoformat(),
        "snapshots": snapshots,
    }


def _decimal(value: object) -> Decimal | None:
    if value in ("", "ND", "-", None):
        return None
    try:
        if not isinstance(value, str) or len(value) > 64:
            raise InvalidOperation()
        number = Decimal(value)
        if not number.is_finite() or abs(number.as_tuple().exponent) > 100:
            raise InvalidOperation()
        return number
    except InvalidOperation as exc:
        raise MacroError("macro source contains an invalid finite decimal") from exc


def _raw(shot: Snapshot) -> bytes:
    try:
        return base64.b64decode(shot.payload["raw_base64"], validate=True)
    except (KeyError, ValueError) as exc:
        raise MacroError("macro source requires verified retained raw bytes") from exc


def _observation(
    definition: SeriesDefinition,
    shot: Snapshot,
    period: date,
    value: Decimal | None,
    locator: str,
    released_at: datetime | None = None,
) -> MacroObservation:
    at = _time(shot.retrieved_at)
    return MacroObservation(
        definition.canonical_id,
        period,
        value,
        at,
        definition.source_id,
        shot.snapshot_id,
        locator,
        released_at=released_at,
        vintage_at=at,
        known_at=at,
        vintage_id="retrieved_snapshot:" + shot.snapshot_id,
        unit=definition.unit,
        frequency=definition.frequency,
        adjustment=definition.adjustment,
        currency=definition.currency,
    )


def _bls_release(shot: Snapshot) -> tuple[date, datetime, Decimal] | None:
    """A narrow, retained official CPI release cross-check; not a release calendar."""
    if shot.status != "available":
        return None
    excerpts = {item["id"]: item["quote"] for item in shot.payload["excerpts"]}
    if not {"RELEASE_TIME", "CPI_PERIOD", "CPI_VALUE"} <= excerpts.keys():
        return None
    months = {
        name.upper(): index
        for index, name in enumerate(
            (
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ),
            1,
        )
    }
    period = re.search(r"CONSUMER PRICE INDEX - ([A-Z]+) (\d{4})", excerpts["CPI_PERIOD"])
    instant = re.search(r"(\d{1,2}):(\d{2}) a\.m\. \(ET\).*?([A-Za-z]+) (\d{1,2}), (\d{4})", excerpts["RELEASE_TIME"])
    value = re.search(r"index level of (\d+(?:\.\d+)?) \(1982-84=100\)", excerpts["CPI_VALUE"])
    if not period or not instant or not value:
        raise MacroError("official CPI release metadata changed")
    try:
        reference = date(int(period[2]), months[period[1]], 1)
        released = datetime(
            int(instant[5]),
            months[instant[3].upper()],
            int(instant[4]),
            int(instant[1]),
            int(instant[2]),
            tzinfo=ZoneInfo("America/New_York"),
        )
    except (ValueError, KeyError) as exc:
        raise MacroError("official CPI release date invalid") from exc
    return reference, released.astimezone(timezone.utc), _decimal(value[1])


def _parse_binding(
    binding: MacroBinding, definition: SeriesDefinition, shot: Snapshot, release: Snapshot | None
) -> tuple[list[MacroObservation], list[str]]:
    diagnostics = []
    raw = _raw(shot)
    records = []
    if binding.adapter == "bls_cpi_v1":
        if (
            binding.field != "CUUR0000SA0"
            or definition.unit != "index"
            or definition.frequency != "monthly"
            or definition.adjustment != "not_seasonally_adjusted"
            or definition.transformation != "raw"
        ):
            raise MacroError("BLS adapter requires CPI-U all-items NSA monthly index definition")
        body = _parse_json(raw.decode("utf-8"))
        series = body.get("Results", {}).get("series", [])
        if body.get("status") != "REQUEST_SUCCEEDED" or len(series) != 1 or series[0].get("seriesID") != binding.field:
            raise MacroError("BLS API status or series identity changed")
        release_record = _bls_release(release) if release is not None else None
        for index, row in enumerate(series[0].get("data", [])):
            month = row.get("period")
            if month == "M13":
                diagnostics.append("BLS M13 annual average excluded from monthly observations")
                continue
            if not isinstance(month, str) or not re.fullmatch(r"M(?:0[1-9]|1[0-2])", month):
                raise MacroError("BLS observation frequency/period changed")
            period = date(int(row["year"]), int(month[1:]), 1)
            if period < binding.start_date:
                continue
            value = _decimal(row.get("value"))
            if value is not None and value <= 0:
                raise MacroError("CPI index must be positive or explicitly missing")
            released_at = None
            if release_record is not None and period == release_record[0]:
                if value != release_record[2]:
                    raise MacroError(
                        "current API index differs from the pinned official release; revision or conflicting source"
                    )
                released_at = release_record[1]
            for note in row.get("footnotes", []):
                if note.get("text"):
                    diagnostics.append(f"{definition.canonical_id} {period}: {note['text']}")
            records.append(
                _observation(
                    definition,
                    shot,
                    period,
                    value,
                    f"/Results/series/0/data/{index}/value; year={row['year']}, period={month}",
                    released_at,
                )
            )
    elif binding.adapter == 'ecos_context_v1':
        from .scan_minimum import ecos_context_observations

        for period, value, locator in ecos_context_observations(raw, binding, definition):
            records.append(_observation(definition, shot, period, value, locator, None))
    elif binding.adapter == 'ecos_daily_v1':
        from .korean_data import ECOS_ITEMS, ecos_observations

        if (
            definition.tenor_years not in ECOS_ITEMS
            or binding.field != ECOS_ITEMS[definition.tenor_years]
            or definition.canonical_id != 'KR_GOVERNMENT_NOMINAL_' + str(definition.tenor_years) + 'Y'
            or definition.unit != 'percent'
            or definition.frequency != 'daily'
            or definition.currency != 'KRW'
            or definition.jurisdiction != 'KR'
            or definition.yield_type != 'nominal'
            or definition.adjustment != 'not_seasonally_adjusted'
            or definition.transformation != 'raw'
        ):
            raise MacroError('ECOS government yield country/tenor/currency/definition mismatch')
        for period, value, locator in ecos_observations(raw, binding.field, definition.tenor_years, binding.start_date):
            records.append(_observation(definition, shot, period, value, locator, None))
    else:
        rows = list(csv.reader(io.StringIO(raw.decode("utf-8-sig"))))
        if len(rows) < 6 or [row[0].strip() for row in rows[:6]] != [
            "Series Description",
            "Unit:",
            "Multiplier:",
            "Currency:",
            "Unique Identifier:",
            "Time Period",
        ]:
            raise MacroError("Fed CSV header/schema changed")
        header = rows[5]
        if len(header) != len(set(header)) or binding.field not in header:
            raise MacroError("Fed CSV series column identity changed")
        column = header.index(binding.field)
        if any(len(row) != len(header) for row in rows[:6]):
            raise MacroError("Fed CSV metadata columns changed")
        unit, multiplier, currency, identifier = (rows[i][column].strip() for i in range(1, 5))
        description = " ".join(rows[0][column].split())
        if (
            definition.frequency != "daily"
            or definition.adjustment != "not_seasonally_adjusted"
            or definition.transformation != "raw"
            or multiplier != "1"
        ):
            raise MacroError("Fed frequency/adjustment/transformation/multiplier mismatch")
        if definition.unit == "percent":
            tenor = definition.tenor_years
            if (
                tenor not in (2, 10)
                or definition.yield_type != "nominal"
                or definition.currency != "USD"
                or binding.field != f"RIFLGFCY{tenor:02d}_N.B"
                or unit != "Percent:_Per_Year"
                or currency != "NA"
                or identifier != "H15/H15/" + binding.field
                or f"{tenor}-year constant maturity" not in description
            ):
                raise MacroError("Treasury yield definition/unit/currency/tenor mismatch")
        elif definition.unit == "KRW_per_USD":
            if (
                binding.field != "RXI_N.B.KO"
                or unit != "Currency"
                or currency != "KRW"
                or identifier != "H10/H10/RXI_N.B.KO"
                or description != "South Korean Won"
            ):
                raise MacroError("Fed USD/KRW definition/unit/currency mismatch")
        else:
            raise MacroError("unsupported Fed series unit")
        for line, row in enumerate(rows[6:], 7):
            if not row:
                continue
            if len(row) != len(header):
                raise MacroError("Fed CSV observation columns changed")
            period = _day(row[0])
            if period < binding.start_date:
                continue
            value = _decimal(row[column])
            if definition.unit == "KRW_per_USD" and value is not None and value <= 0:
                raise MacroError("USD/KRW rate must be positive or explicitly missing")
            records.append(
                _observation(
                    definition, shot, period, value, f"CSV row {line}, column {binding.field}, Time Period={row[0]}"
                )
            )
    if len({item.observation_date for item in records}) != len(records):
        raise MacroError("duplicate periods in one macro source vintage")
    if not records:
        raise MacroError("source has no observations in the declared window")
    diagnostics.append(
        f"{definition.canonical_id}: snapshot vintage is retrieval version; complete release/revision history unavailable"
    )
    return records, diagnostics


def replay_macro(plan: MacroPlan, store: str | Path, pins: dict, as_of: date | datetime | None = None) -> MacroRun:
    _validate_pins(plan, pins)
    cutoff = _cutoff(as_of) if as_of is not None else _time(pins["as_of"])
    registry = make_registry(plan.series)
    shots, observations, diagnostics, release_provenance = {}, [], [], {}
    for spec in plan.sources:
        versions = []
        for reference in pins["snapshots"][spec.id]:
            shot = load_snapshot(store, spec.id, reference)
            if _digest(shot.source) != _digest(asdict(spec)):
                raise MacroError("macro snapshot metadata differs from the reviewed plan")
            versions.append(shot)
            diagnostics.extend(f"{spec.id}: {message}" for message in shot.diagnostics)
            if shot.status != "available":
                diagnostics.append(f"{spec.id}: {shot.status}; no successful observations from this snapshot")
        shots[spec.id] = sorted(versions, key=lambda item: (_time(item.retrieved_at), item.snapshot_id))
    for binding in plan.bindings:
        for shot in shots[binding.source_id]:
            if shot.status != "available":
                continue
            # A later helper must not rewrite what an earlier query could know.
            # Prefer the last helper already captured with this API vintage;
            # otherwise use its first subsequent cross-check known at cutoff.
            helpers = [
                item
                for item in shots.get(binding.release_source_id, ())
                if item.status == "available" and _time(item.retrieved_at) <= cutoff
            ]
            releases = [item for item in helpers if _time(item.retrieved_at) <= _time(shot.retrieved_at)]
            release = releases[-1] if releases else (helpers[0] if helpers else None)
            try:
                values, messages = _parse_binding(binding, registry[binding.series_id], shot, release)
                if release is not None:
                    values = [
                        item if item.released_at is None else _with_release_known_floor(item, release)
                        for item in values
                    ]
                    for item in values:
                        if item.released_at is not None:
                            release_provenance[item.id] = {
                                "source_id": release.source_id,
                                "snapshot_id": release.snapshot_id,
                                "excerpt_ids": ["RELEASE_TIME", "CPI_PERIOD", "CPI_VALUE"],
                                "method": "bls_release_crosscheck_v1",
                            }
                observations.extend(values)
                diagnostics.extend(messages)
            except (MacroError, ValueError, KeyError, TypeError, UnicodeDecodeError, IndexError) as exc:
                diagnostics.append(
                    f"{binding.series_id}/{shot.snapshot_id}: parsing blocked: {exc}; no successful observations"
                )
    snapshot = build_macro_snapshot(plan.series, observations, cutoff, plan.yoy_series_ids, plan.yield_pair)
    by_obs = {item.id: item for item in observations}
    needed = {ref for metric in snapshot.metrics for ref in metric.input_observation_ids}
    needed.update(item.latest.id for item in snapshot.selections if item.latest is not None)
    sources = []
    for spec in plan.sources:
        shot = shots[spec.id][-1]
        provenance = SourceProvenance(
            shot.snapshot_id,
            spec.publisher,
            spec.title,
            shot.retrieved_at,
            spec.jurisdiction,
            spec.topics,
            spec.content_type,
            spec.access_method,
            spec.policy_url,
            spec.policy_note,
            spec.retention,
            shot.raw_sha256,
            shot.normalized_sha256,
            shot.payload_sha256,
            shot.status,
            spec.published_at,
            spec.observed_at,
            spec.valid_as_of,
            "per_observation",
        )
        sources.append(
            SourceRecord(
                spec.id,
                SourceType(spec.type),
                spec.title,
                spec.canonical_url,
                _time(spec.published_at).date() if spec.published_at else None,
                None,
                _time(shot.retrieved_at).date(),
                spec.origin_source_id,
                tuple(shot.diagnostics),
                provenance,
            )
        )
    evidence = []
    for ref in sorted(needed):
        item = by_obs[ref]
        definition = registry[item.series_id]
        age = "stale" if (cutoff.date() - item.observation_date).days > definition.max_age_days else "fresh"
        review = Review(
            InterpretationStatus.REVIEWED,
            "deterministic_macro_parser_v1",
            item.retrieved_at.date(),
            "공식 필드·정의·수치의 결정적 파싱 기록. 사람의 투자 해석 검토나 의미 전체의 자동 검증이 아니다.",
        )
        evidence.append(
            EvidenceRecord(
                item.id,
                item.source_id,
                f"{definition.name}; observation={item.observation_date}; value={item.value if item.value is not None else 'MISSING'} {definition.unit}",
                item.locator,
                item.observation_date,
                item.retrieved_at.date(),
                ASSETS,
                "macro",
                "observed_fact",
                VerificationStatus.SUPPORTED if item.value is not None else VerificationStatus.UNVERIFIED,
                review,
                ("원관측의 수치 확인이며 수익률·인과·투자 매력의 확인이 아니다.", "전체 개정 이력은 미확인이다."),
                item.value,
                definition.unit if item.value is not None else None,
                definition.frequency if item.value is not None else None,
                definition.currency if item.value is not None else None,
                EvidenceProvenance(
                    item.snapshot_id,
                    item.id,
                    "matched",
                    age,
                    {
                        "measure": item.series_id,
                        "unit": definition.unit,
                        "period": definition.frequency,
                        "currency": definition.currency,
                        "adjustment": definition.adjustment,
                        "scope": definition.definition,
                    },
                ),
            )
        )
    metrics = tuple(
        MetricResult(
            metric.id,
            metric.name,
            metric.value,
            metric.unit,
            metric.transformation,
            metric.input_observation_ids,
            ASSETS,
            (*metric.assumptions, *metric.diagnostics),
        )
        for metric in snapshot.metrics
        if metric.status == "available" and metric.value is not None
    )
    claims = tuple(
        ResearchClaim(
            "CLAIM_" + metric.id,
            metric.label + ": " + str(metric.value) + " " + metric.unit,
            ASSETS,
            VerificationStatus.SUPPORTED,
            Review(
                InterpretationStatus.REVIEWED,
                "deterministic_macro_transform_v1",
                cutoff.date(),
                metric.method + "; 좁은 계산 사실만 확인",
            ),
            metric.input_ids,
            (),
            None,
            metric.limitations,
            "원자료·정의·공개·판본이 달라지면 같은 규칙으로 다시 계산한다.",
        )
        for metric in metrics
    )
    digest = _digest(
        {
            "plan": plan.input_digest,
            "pins": pins,
            "as_of": cutoff.isoformat(),
            "macro": MACRO_VERSION,
            "pipeline": MACRO_PIPELINE_VERSION,
        }
    )
    brief = ResearchBrief(
        plan.id,
        plan.question,
        cutoff.date(),
        "KRW",
        "확인 가능한 현재 거시 상태; 투자 매력·배분 판단 미실시",
        tuple(item.latest.id for item in snapshot.selections if item.status == "available" and item.latest is not None),
        ("정책금리·고용·성장·전체 자산의 상대 매력은 이번 범위에서 평가하지 않는다.",),
        ("미국 물가·금리와 한국 투자자의 환율 노출을 분리한다.",),
    )
    case = ResearchCase(
        "1",
        False,
        brief,
        ProfileSnapshot(plan.id + "_PROFILE", cutoff.date(), {"base_currency": ProfileField("known", "KRW")}),
        tuple(sources),
        tuple(evidence),
        claims,
        (),
        (),
        (),
        digest,
        True,
        tuple(diagnostics),
    )
    return MacroRun(
        plan,
        snapshot,
        case,
        metrics,
        {key: list(value) for key, value in pins["snapshots"].items()},
        digest,
        tuple(diagnostics),
        release_provenance,
    )


def _with_release_known_floor(observation: MacroObservation, release: Snapshot) -> MacroObservation:
    from dataclasses import replace

    return replace(observation, known_at=max(observation.known_at, _time(release.retrieved_at)))


def macro_manifest(run: MacroRun, report: str) -> dict:
    from .__main__ import manifest_for
    from .engine import run_research
    from .macro_report import MACRO_REPORT_VERSION

    manifest = manifest_for(run_research(run.case), report)
    manifest["kind"] = "macro_regime_snapshot"
    manifest["as_of"] = run.as_of.isoformat()
    manifest["method_versions"].update(
        {
            "macro": MACRO_VERSION,
            "macro_pipeline": MACRO_PIPELINE_VERSION,
            "macro_report": MACRO_REPORT_VERSION,
            "source_acquisition": SOURCE_VERSION,
        }
    )
    manifest["snapshot_refs"] = run.snapshot_refs
    manifest["series_definitions"] = [asdict(item) for item in run.plan.series]
    manifest["bindings"] = [asdict(item) for item in run.plan.bindings]
    manifest["release_provenance"] = run.release_provenance
    manifest["metrics"] = [asdict(item) for item in run.snapshot.metrics]
    manifest["evidence_ids"] = [item.id for item in run.case.evidence]
    manifest["selections"] = [
        {
            "series_id": item.definition.canonical_id,
            "status": item.status,
            "latest_id": item.latest.id if item.latest else None,
            "selected_ids": [obs.id for obs in item.observations],
            "excluded_ids": [obs.id for obs in item.excluded],
            "diagnostics": list(item.diagnostics),
        }
        for item in run.snapshot.selections
    ]
    manifest["observations"] = [
        dict(id=obs.id, **asdict(obs)) for selection in run.snapshot.selections for obs in selection.all_observations
    ]
    return json.loads(
        json.dumps(
            manifest,
            default=lambda value: str(value) if isinstance(value, Decimal) else value.isoformat(),
            ensure_ascii=False,
            allow_nan=False,
        )
    )
