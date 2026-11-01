"""Reviewed source plans connect explicit acquisition to offline research replay.

Matched passages establish source-statement occurrence. Only the small numeric
rule below compares an extracted statement; general financial meaning remains
a supplied, disclosed review, never a model-generated truth judgement.
"""

from __future__ import annotations

from dataclasses import MISSING, asdict, dataclass, fields
from datetime import date, datetime, time, timezone
from decimal import Context, Decimal, InvalidOperation, localcontext
import calendar
import hashlib
import json
from pathlib import Path
import re

from .models import (
    Alternative,
    EvidenceProvenance,
    EvidenceRecord,
    InterpretationStatus,
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
from .sources import SourceError, SourceSpec, acquire, freshness, load_snapshot, _parse_json, _validate
from .validation import InputValidationError, _review

PIPELINE_VERSION = "source_verification_v1"
OBSERVATION_DATES_VERSION = 'per_record_observation_dates_v1'
ASSET_IDS = ("CASH", "BOND", "EQUITY")
DEFINITION_FIELDS = {"measure", "unit", "period", "currency", "adjustment", "scope"}
EXTRACTIONS = {
    None,
    "fed_rate_cut_v1",
    "basis_points_statement_v1",
    "decimal_scalar_v1",
    "dated_table_total_v1",
    "grouped_decimal_scalar_v1",
    "eth_dated_table_total_v2",
    "spaced_signed_decimal_v1",
}


@dataclass(frozen=True)
class SourcePlan:
    id: str
    question: str
    as_of: date
    sources: tuple[SourceSpec, ...]
    evidence: tuple[dict, ...]
    claims: tuple[dict, ...]
    input_digest: str
    asset_ids: tuple[str, ...] = ASSET_IDS
    observation_dates_version: str | None = None


def observation_timing(period, explicit=None):
    try:
        return _observation_timing(period, explicit)
    except (ValueError, TypeError, OverflowError) as exc:
        raise SourceError('invalid row observation calendar label') from exc


def _observation_timing(period, explicit=None):
    """Resolve only a row's explicit calendar label, never its series date.

    Monthly/quarterly data describe a period. The existing date-only evidence
    field uses that period's end; the period and precision remain in the audit.
    A reviewed API may additionally supply its own actual snapshot timestamp.
    """
    start = end = None
    precision = 'unknown'
    instant = None
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:T.+)?', period):
        from .sources import _time

        parsed = _time(period)
        start = end = parsed.date()
        precision = 'instant' if 'T' in period else 'day'
        instant = parsed if precision == 'instant' else None
    elif re.fullmatch(r'\d{4}-\d{2}', period):
        y, m = map(int, period.split('-'))
        start = date(y, m, 1)
        end = date(y, m, calendar.monthrange(y, m)[1])
        precision = 'month'
    elif re.fullmatch(r'\d{4}(?:Q[1-4]| [1-4]Q|H[12])', period):
        y = int(period[:4])
        if 'H' in period:
            m = 1 + (int(period[-1]) - 1) * 6
            length = 6
            precision = 'half_year'
        else:
            q = int(period[5])
            m = 1 + (q - 1) * 3
            length = 3
            precision = 'quarter'
        start = date(y, m, 1)
        last = m + length - 1
        end = date(y, last, calendar.monthrange(y, last)[1])
    elif re.fullmatch(r'\d{4}', period):
        y = int(period)
        start = date(y, 1, 1)
        end = date(y, 12, 31)
        precision = 'year'
    elif re.fullmatch(r'week_ending_\d{4}-\d{2}-\d{2}', period):
        end = date.fromisoformat(period.removeprefix('week_ending_'))
        precision = 'week_ending'
    elif re.fullmatch(r'\d{4}-\d{2}-\d{2}\.\.\d{4}-\d{2}-\d{2}', period):
        a, b = period.split('..')
        start, end = date.fromisoformat(a), date.fromisoformat(b)
        if start > end:
            raise SourceError('observation period is reversed')
        precision = 'reporting_interval'
    if explicit is not None:
        from .sources import _time

        actual = _time(explicit)
        if actual is None:
            raise SourceError('explicit row observation timestamp is missing')
        if end is not None and actual.date() != end:
            raise SourceError('explicit row observation disagrees with its calendar period')
        instant = actual
        if precision == 'unknown':
            precision = 'snapshot'
    at = instant.isoformat() if instant is not None else end.isoformat() if end is not None else None
    return dict(
        observed_at=at,
        precision=precision,
        period=period,
        period_start=start.isoformat() if start else None,
        period_end=end.isoformat() if end else None,
        date_meaning=(
            'period_end_label_not_daily_measurement'
            if precision in ('month', 'quarter', 'half_year', 'year', 'reporting_interval')
            else 'row_timestamp_or_calendar_label' if at else 'unconfirmed_no_source_date_fallback'
        ),
    )


def dated_evidence(e):
    """Whether a row has a confirmed time label for a change calculation."""
    if e.observed_at is None or e.provenance is None:
        return False
    if e.view == 'macro':
        return True  # The macro parser already binds each row.
    timing = observation_timing(e.provenance.definition['period'])
    return timing['observed_at'] is not None and _timestamp_day(timing['observed_at']) == e.observed_at


def _digest(value: object) -> str:
    try:
        data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError, RecursionError) as exc:
        raise SourceError("plan must contain finite JSON-compatible values") from exc
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _object(value, required: set[str], optional: set[str], path: str) -> dict:
    if not isinstance(value, dict) or not required <= value.keys() or value.keys() - required - optional:
        raise SourceError(f"{path}: missing or unsupported fields")
    return value


def _text(value, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SourceError(f"{path}: nonempty text is required")
    return value


def _id(value, path: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,99}", value):
        raise SourceError(f"{path}: invalid identifier")
    return value


def _list(value, path: str, limit=100) -> list:
    if not isinstance(value, list) or len(value) > limit:
        raise SourceError(f"{path}: a bounded JSON array is required")
    return value


def _strings(value, path: str, identifiers: bool = False) -> tuple[str, ...]:
    result = tuple((_id if identifiers else _text)(item, path) for item in _list(value, path))
    if len(set(result)) != len(result):
        raise SourceError(f"{path}: duplicate entries")
    return result


def _day(value, path: str) -> date:
    try:
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError()
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SourceError(f"{path}: expected a valid YYYY-MM-DD date") from exc


def _timestamp_day(value: str | None) -> date | None:
    if value is None:
        return None
    if len(value) == 10:
        return date.fromisoformat(value)
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).date()


def _review_record(value, path: str) -> Review:
    if value is None:
        return Review(InterpretationStatus.PENDING, None, None, "원문 의미의 해석 검토는 아직 수행하지 않았다.")
    try:
        return _review(value, path)
    except InputValidationError as exc:
        raise SourceError(str(exc)) from exc


def _review_not_before(review: Review, earliest: date, path: str) -> None:
    # A supplied date on a pending review is still a chronological assertion.
    if review.reviewed_at is not None and review.reviewed_at < earliest:
        raise SourceError(f"{path}: review date precedes referenced acquisition, observation or review")


def _definition(value, path: str) -> dict:
    data = _object(value, DEFINITION_FIELDS, set(), path)
    for key, item in data.items():
        if key != "currency" or item is not None:
            _text(item, f"{path}.{key}")
    return data


def _decimal(value, path: str) -> Decimal:
    try:
        if not isinstance(value, str) or len(value) > 64:
            raise ValueError()
        result = Decimal(value)
        if not result.is_finite() or abs(result.as_tuple().exponent) > 100:
            raise ValueError()
        return result
    except (ValueError, InvalidOperation) as exc:
        raise SourceError(f"{path}: a bounded finite decimal string is required") from exc


def load_source_plan(path: str | Path) -> SourcePlan:
    """Read a strict local plan; this operation never performs a request."""
    path = Path(path)
    path = path / "plan.json" if path.is_dir() else path

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise SourceError("plan JSON has duplicate keys")
            result[key] = value
        return result

    try:
        if path.stat().st_size > 1024 * 1024:
            raise SourceError("source plan exceeds its size limit")
        data = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=unique,
            parse_constant=lambda _: (_ for _ in ()).throw(SourceError("nonfinite JSON value")),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise SourceError("source plan is unavailable or invalid UTF-8 JSON") from exc
    d = _object(
        data,
        {"schema_version", "id", "question", "as_of", "sources", "evidence", "claims"},
        {"asset_ids", "scan_extension", "observation_dates_version"},
        "plan",
    )
    date_version = d.get('observation_dates_version')
    if date_version not in (None, OBSERVATION_DATES_VERSION):
        raise SourceError('unsupported observation dates method')
    extension = d.get('scan_extension')
    if extension not in (None, 'four_asset_minimum_v2', 'commodity_deep_v1'):
        raise SourceError('unreviewed source plan extension')
    if d["schema_version"] != "1":
        raise SourceError("unsupported source plan schema")
    identifier, question, cutoff = (
        _id(d["id"], "plan.id"),
        _text(d["question"], "plan.question"),
        _day(d["as_of"], "plan.as_of"),
    )
    asset_ids = _strings(d.get("asset_ids", list(ASSET_IDS)), "plan.asset_ids", True)
    if not asset_ids:
        raise SourceError("plan.asset_ids: at least one asset ID is required")
    specifications = []
    source_fields = {f.name for f in fields(SourceSpec)}
    required = {f.name for f in fields(SourceSpec) if f.default is MISSING and f.default_factory is MISSING}
    for index, item in enumerate(_list(d["sources"], "sources")):
        item = dict(_object(item, required, source_fields - required, f"sources[{index}]"))
        for key in ("topics", "asset_ids"):
            item[key] = _strings(item.get(key, []), f"sources[{index}].{key}", key == "asset_ids")
        item["excerpts"] = tuple(_list(item.get("excerpts", []), f"sources[{index}].excerpts"))
        try:
            spec = SourceSpec(**item)
            _validate(spec)
        except (TypeError, AttributeError) as exc:
            raise SourceError(f"sources[{index}]: invalid source metadata") from exc
        if not set(spec.asset_ids) <= set(asset_ids):
            raise SourceError("source asset IDs must belong to the explicit plan asset scope")
        specifications.append(spec)
    if not specifications:
        raise SourceError("at least one explicit source is required")
    sources = {s.id: s for s in specifications}
    if len(sources) != len(specifications):
        raise SourceError("duplicate source IDs")
    for spec in specifications:
        seen, parent = {spec.id}, spec.origin_source_id
        while parent is not None:
            if parent not in sources or parent in seen:
                raise SourceError("source origin references are missing or cyclic")
            seen.add(parent)
            parent = sources[parent].origin_source_id
    evidence = []
    for index, item in enumerate(_list(d["evidence"], "evidence", 160 if extension else 100)):
        p = f"evidence[{index}]"
        _object(
            item,
            {"id", "source_id", "excerpt_id", "view", "kind", "definition", "extraction", "limitations"},
            {"interpretation", "observed_at"},
            p,
        )
        for key in ("id", "source_id", "excerpt_id"):
            _id(item[key], p + "." + key)
        if item["source_id"] not in sources:
            raise SourceError(p + ": missing source reference")
        spec = sources[item["source_id"]]
        excerpt = next((e for e in spec.excerpts if e["id"] == item["excerpt_id"]), None)
        if excerpt is None or _definition(item["definition"], p + ".definition") != excerpt["definition"]:
            raise SourceError(p + ": excerpt reference or definition mismatch")
        if 'observed_at' in item:
            if date_version is None:
                raise SourceError('row dates require an explicit method version')
            observation_timing(item['definition']['period'], item['observed_at'])
        if _text(item["view"], p + ".view") not in {"macro", "fundamental", "quantitative", "community"} or _text(
            item["kind"], p + ".kind"
        ) not in {"observed_fact", "external_fact", "observed_narrative"}:
            raise SourceError(p + ": unsupported research view or evidence kind")
        if spec.type == "community" and (item["view"] != "community" or item["kind"] != "observed_narrative"):
            raise SourceError(p + ": community text must remain observed narrative")
        if (
            not (item["extraction"] is None or isinstance(item["extraction"], str))
            or item["extraction"] not in EXTRACTIONS
        ):
            raise SourceError(p + ": unsupported numeric extraction")
        _review_record(item.get("interpretation"), p + ".interpretation")
        _strings(item["limitations"], p + ".limitations")
        evidence.append(item)
    by_id = {item["id"]: item for item in evidence}

    def check_reference(ref, scope: tuple[str, ...], path: str) -> None:
        _id(ref, path)
        if ref not in by_id or not set(scope) <= set(sources[by_id[ref]["source_id"]].asset_ids or asset_ids):
            raise SourceError(path + ": evidence reference or asset scope mismatch")

    claims = []
    for index, item in enumerate(_list(d["claims"], "claims")):
        p = f"claims[{index}]"
        _object(
            item,
            {
                "id",
                "text",
                "asset_ids",
                "rule",
                "support_ids",
                "counter_ids",
                "context_ids",
                "narrative_evidence_id",
                "review",
            },
            {"assertion", "verification", "limitations", "recheck"},
            p,
        )
        _id(item["id"], p + ".id")
        _text(item["text"], p + ".text")
        scope = _strings(item["asset_ids"], p + ".asset_ids", True)
        if not scope or not set(scope) <= set(asset_ids):
            raise SourceError(p + ": unsupported claim asset scope")
        for key in ("support_ids", "counter_ids", "context_ids"):
            for ref in _strings(item[key], p + "." + key, True):
                check_reference(ref, scope, p + "." + key)
        if set(item["support_ids"]) & set(item["counter_ids"]):
            raise SourceError(p + ": the same passage cannot support and contradict a claim")
        narrative = item["narrative_evidence_id"]
        if narrative is not None:
            check_reference(narrative, scope, p + ".narrative_evidence_id")
            if by_id[narrative]["kind"] != "observed_narrative":
                raise SourceError(p + ": invalid narrative reference")
        _review_record(item["review"], p + ".review")
        if item["rule"] == "numeric_equality_v1":
            assertion = _object(
                item.get("assertion"),
                {"evidence_id", "expected_value", "unit", "period", "currency", "measure", "scope"},
                {"adjustment"},
                p + ".assertion",
            )
            check_reference(assertion["evidence_id"], scope, p + ".assertion.evidence_id")
            _decimal(assertion["expected_value"], p + ".assertion.expected_value")
            for key in ("unit", "period", "currency", "measure", "scope"):
                if key != "currency" or assertion[key] is not None:
                    _text(assertion[key], p + ".assertion." + key)
            if "adjustment" in assertion:
                _text(assertion["adjustment"], p + ".assertion.adjustment")
        elif item["rule"] == "reviewed_links_v1":
            try:
                VerificationStatus(item.get("verification"))
            except (ValueError, TypeError) as exc:
                raise SourceError(p + ": reviewed links require a supported verification status") from exc
        else:
            raise SourceError(p + ": unsupported verification rule")
        _strings(item.get("limitations", []), p + ".limitations")
        if "recheck" in item:
            _text(item["recheck"], p + ".recheck")
        claims.append(item)
    ids = [identifier, *sources, *by_id, *(c["id"] for c in claims)]
    if len(evidence) != len(by_id) or len(ids) != len(set(ids)) or set(ids) & set(asset_ids):
        raise SourceError("plan has duplicate or reserved IDs")
    return SourcePlan(
        identifier,
        question,
        cutoff,
        tuple(specifications),
        tuple(evidence),
        tuple(claims),
        _digest(data),
        asset_ids,
        date_version,
    )


def acquire_plan(plan: SourcePlan, store: str | Path, *, fetcher=None, now=None, progress=None) -> dict:
    """The sole network boundary: acquire exactly the reviewed plan sources."""
    snapshots = {}
    options = {}
    if fetcher is not None:
        options['fetcher'] = fetcher
    if now is not None:
        options['now'] = now
    for spec in plan.sources:
        shot = acquire(spec, store, **options)
        snapshots[spec.id] = shot.snapshot_id
        if progress is not None:
            progress(spec.id + ': ' + shot.status)
    return {
        "schema_version": "1",
        "plan_id": plan.id,
        "sources_digest": _digest([asdict(s) for s in plan.sources]),
        "snapshots": snapshots,
    }


def load_pins(path: str | Path) -> dict:
    """Read bounded local replay pins without requests or permissive JSON parsing."""
    path = Path(path)
    try:
        if path.stat().st_size > 1024 * 1024:
            raise SourceError("replay pins exceed their size limit")
        pins = _parse_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        raise SourceError("replay pins are unavailable or invalid UTF-8 JSON") from exc
    if not isinstance(pins, dict):
        raise SourceError("replay pins must be a JSON object")
    _digest(pins)  # Reject exponent overflow/nonfinite floats as well as NaN tokens.
    return pins


def validate_evidence(case, cutoff, config):
    """Optional, versioned validation before downstream financial use.

    Quote transcription and source freshness precede this gate. This gate never
    edits snapshots or quietly reinterprets an old pinned research run.
    """
    from .evidence_guard import guard_case, validate_config

    validate_config(config)
    return guard_case(case, cutoff, numeric_ids=config['numeric_ids'])


def _extract(quote: str, method: str | None, definition: dict) -> Decimal | None:
    if method is None:
        return None
    if method == 'spaced_signed_decimal_v1':
        if (
            not definition['measure'].startswith('CME_')
            or not definition['measure'].endswith('_DAY_CHANGE')
            or 'settlement_change_vs_previous_trading_session' not in definition['adjustment']
            or definition['currency'] != 'USD'
            or not re.fullmatch(r'[+-] \d+(?:\.\d+)?', quote)
        ):
            return None
        return _decimal(quote.replace(' ', ''), 'explicitly signed CME daily price change')
    if method == 'grouped_decimal_scalar_v1':
        if definition['unit'] == 'text' or not re.fullmatch(r'[+-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?', quote):
            return None
        return _decimal(quote.replace(',', ''), 'grouped source scalar')
    if method == "decimal_scalar_v1":
        # The discovery contract supplies a checked JSON field and six-part
        # definition. This rule only transcribes its entire decimal token.
        if definition["unit"] == "text" or not re.fullmatch(r"[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", quote):
            return None
        return _decimal(quote, "source scalar")
    if method == "dated_table_total_v1":
        if (
            definition["measure"] != "US_SPOT_BTC_ETF_DAILY_NET_FLOW"
            or definition["unit"] != "USD_million"
            or definition["currency"] != "USD"
            or definition["scope"] != "US spot Bitcoin ETFs reported by Farside"
            or not re.fullmatch(r"\d{2} [A-Z][a-z]{2} \d{4}(?: (?:-|\(?[\d,]+(?:\.\d+)?\)?))+", quote)
        ):
            return None
        try:
            quoted_day = datetime.strptime(' '.join(quote.split()[:3]), '%d %b %Y').date().isoformat()
        except ValueError:
            return None
        if definition['period'] != quoted_day or definition['adjustment'] not in {
            'complete_row_provider_reported_not_issuer_confirmed',
            'partial_row_not_final_total',
        }:
            return None
        token = quote.split()[-1]
        if token == "-":
            return None
        token = '-' + token[1:-1] if token.startswith('(') and token.endswith(')') else token
        return _decimal(token.replace(',', ''), "dated table total")
    if method == 'eth_dated_table_total_v2':
        if (
            definition['measure'] != 'US_SPOT_ETH_ETF_DAILY_NET_FLOW'
            or definition['scope'] != 'US spot Ethereum ETFs reported by Farside'
            or definition['adjustment'] != 'complete_row_provider_reported_not_issuer_confirmed'
        ):
            return None
        # Reuse the existing dated-token check; stored definition remains ETH.
        btc = {
            **definition,
            'measure': 'US_SPOT_BTC_ETF_DAILY_NET_FLOW',
            'scope': 'US spot Bitcoin ETFs reported by Farside',
        }
        total = _extract(quote, 'dated_table_total_v1', btc)
        cells = quote.split()[3:]
        if total is None or len(cells) < 3 or '-' in cells:
            return None

        def cell(token):
            negative = token.startswith('(') and token.endswith(')')
            value = _decimal(token.strip('()').replace(',', ''), 'ETH flow component')
            return -value if negative else value

        with localcontext() as ctx:
            ctx.prec = 50
            values = [cell(v) for v in cells]
            # Each published rounded cell contributes at most half its last
            # decimal place. This is transcription tolerance, not a trust score.
            rounding = sum(Decimal(1).scaleb(v.as_tuple().exponent) / 2 for v in values)
            if abs(sum(values[:-1]) - values[-1]) > rounding:
                return None
        return total
    if (
        definition["unit"] != "basis_points"
        or definition["period"] != "policy_decision"
        or definition["currency"] != "USD"
    ):
        return None
    if method == "fed_rate_cut_v1":
        match = re.search(r"decided to lower\b[^.;]{0,240}?\bby\s+(\d+)/(\d+)\s+percentage point\b", quote, re.I)
        if match and int(match[2]) != 0:
            with localcontext(Context(prec=34)):
                return Decimal(match[1]) / Decimal(match[2]) * 100
    if method == "basis_points_statement_v1":
        match = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:bps|basis points)\b", quote, re.I)
        if match:
            return Decimal(match[1])
    return None


def replay_plan(plan: SourcePlan, store: str | Path, pins: dict, as_of: date | None = None) -> ResearchCase:
    """Validate pinned local snapshots and adapt them to the existing models."""
    _object(pins, {"schema_version", "plan_id", "sources_digest", "snapshots"}, set(), "pins")
    if (
        pins["schema_version"] != "1"
        or pins["plan_id"] != plan.id
        or pins["sources_digest"] != _digest([asdict(s) for s in plan.sources])
    ):
        raise SourceError("pins do not match the reviewed source plan")
    if not isinstance(pins["snapshots"], dict) or set(pins["snapshots"]) != {s.id for s in plan.sources}:
        raise SourceError("pins must reference exactly the reviewed sources")
    cutoff = as_of if as_of is not None else plan.as_of
    if type(cutoff) is not date:
        raise SourceError("replay as_of must be a date")
    snapshots, source_records, diagnostics, ages = {}, [], [], {}
    for spec in plan.sources:
        shot = load_snapshot(store, spec.id, pins["snapshots"][spec.id])
        if _digest(shot.source) != _digest(asdict(spec)):
            raise SourceError("snapshot source metadata differs from the reviewed plan")
        snapshots[spec.id] = shot
        age = freshness(shot, datetime.combine(cutoff, time.max, timezone.utc))
        status = (
            "unavailable"
            if shot.status != "available"
            else "future" if age["status"] == "future" else "unknown" if spec.published_at is None else age["status"]
        )
        ages[spec.id] = status
        diagnostics.extend(f"{spec.id}: {item}" for item in shot.diagnostics)
        age_reason = (
            "publication date is unknown; retrieval is not publication; " + age["reason"]
            if status == "unknown" and spec.published_at is None
            else age["reason"]
        )
        diagnostics.append(f"{spec.id}: freshness={status}; {age_reason}")
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
            status,
        )
        source_records.append(
            SourceRecord(
                spec.id,
                SourceType(spec.type),
                spec.title,
                spec.canonical_url,
                _timestamp_day(spec.published_at),
                None,
                _timestamp_day(shot.retrieved_at),
                spec.origin_source_id,
                tuple(shot.diagnostics),
                provenance,
            )
        )
    source_lookup = {s.id: s for s in source_records}
    evidence = []
    for item in plan.evidence:
        shot = snapshots[item["source_id"]]
        excerpt = next((e for e in shot.payload.get("excerpts", []) if e["id"] == item["excerpt_id"]), None)
        if shot.status != "available" or excerpt is None or excerpt.get("match_status") != "matched":
            diagnostics.append(f"{item['id']}: failed source or missing passage; no successful evidence was produced")
            continue
        review = _review_record(item.get("interpretation"), "evidence.interpretation")
        timing = (
            observation_timing(item['definition']['period'], item.get('observed_at'))
            if plan.observation_dates_version
            else None
        )
        observed = _timestamp_day(timing['observed_at']) if timing else _timestamp_day(shot.source.get("observed_at"))
        earliest = max(_timestamp_day(shot.retrieved_at), observed or date.min)
        _review_not_before(review, earliest, f"evidence.{item['id']}.interpretation")
        numeric = _extract(excerpt["quote"], item["extraction"], item["definition"])
        if item["kind"] == "observed_narrative":
            numeric = None
        definition = item["definition"]
        limitations = tuple(item["limitations"]) + (
            "구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.",
        )
        if timing and timing['observed_at'] is None:
            limitations += (
                "해당 행의 실제 관측일이 미확인이다. 자료 전체 최신일·공개일·획득일로 채우거나 변화 계산에 사용하지 않는다.",
            )
        elif timing and timing['date_meaning'] == 'period_end_label_not_daily_measurement':
            limitations += ("observed_at은 명시된 보고기간의 말일 표기이며 그 하루의 측정값을 뜻하지 않는다.",)
        if item["extraction"] is not None and numeric is None and item["kind"] != "observed_narrative":
            limitations += ("지원하는 수치·정의로 추출할 수 없어 수치 주장을 확인하지 않았다.",)
        analyzed = max(earliest, review.reviewed_at or date.min)
        evidence.append(
            EvidenceRecord(
                item["id"],
                item["source_id"],
                excerpt["quote"],
                excerpt["locator"],
                observed,
                analyzed,
                tuple(shot.source["asset_ids"]) or plan.asset_ids,
                item["view"],
                item["kind"],
                VerificationStatus.SUPPORTED,
                review,
                limitations,
                numeric,
                definition["unit"] if numeric is not None else None,
                definition["period"] if numeric is not None else None,
                definition["currency"] if numeric is not None else None,
                EvidenceProvenance(
                    shot.snapshot_id, item["excerpt_id"], "matched", ages[item["source_id"]], definition
                ),
            )
        )
    by_id = {e.id: e for e in evidence}

    def factual(ref: str) -> bool:
        e = by_id.get(ref)
        return bool(
            e
            and e.kind != "observed_narrative"
            and source_lookup[e.source_id].type != SourceType.COMMUNITY
            and e.interpretation.status == InterpretationStatus.REVIEWED
            and e.provenance.freshness != "future"
        )

    claims = []
    for item in plan.claims:
        support, counter, context = (
            [ref for ref in item[key] if ref in by_id] for key in ("support_ids", "counter_ids", "context_ids")
        )
        narrative = item["narrative_evidence_id"] if item["narrative_evidence_id"] in by_id else None
        refs = (
            item["support_ids"]
            + item["counter_ids"]
            + item["context_ids"]
            + ([item["narrative_evidence_id"]] if item["narrative_evidence_id"] else [])
        )
        if item["rule"] == "numeric_equality_v1":
            refs += [item["assertion"]["evidence_id"]]
        missing = [ref for ref in refs if ref not in by_id]
        review = _review_record(item["review"], "claim.review")
        for ref in set(refs):
            record = by_id.get(ref)
            if record is not None:
                earliest = max(record.analyzed_at, record.interpretation.reviewed_at or date.min)
                _review_not_before(review, earliest, f"claims.{item['id']}.review")
        limitations = list(item.get("limitations", []))
        state = VerificationStatus.UNVERIFIED
        if missing:
            limitations.append("확보하지 못한 원문 근거: " + ", ".join(missing))
        elif review.status != InterpretationStatus.REVIEWED:
            limitations.append("주장 의미에 대한 명시적 검토가 없어 확인 상태로 승격하지 않았다.")
        elif item["rule"] == "numeric_equality_v1":
            assertion = item["assertion"]
            ref, expected = assertion["evidence_id"], _decimal(assertion["expected_value"], "assertion.expected_value")
            e = by_id.get(ref)
            compatible = (
                e is not None
                and all(
                    e.provenance.definition[key] == assertion[key]
                    for key in ("unit", "period", "currency", "measure", "scope")
                )
                and e.provenance.definition["adjustment"]
                == assertion.get("adjustment", e.provenance.definition["adjustment"])
            )
            if not factual(ref) or e.value is None or not compatible:
                limitations.append("비커뮤니티 검토 근거·지원 수치 추출·동일 정의가 부족하여 수치 주장은 미확인이다.")
            else:
                support, counter = [r for r in support if r != ref], [r for r in counter if r != ref]
                state = VerificationStatus.SUPPORTED if e.value == expected else VerificationStatus.CONTRADICTED
                (support if state == VerificationStatus.SUPPORTED else counter).append(ref)
                limitations.append("numeric_equality_v1: 보존된 좁은 원문 수치와 명시한 기대값의 일치만 비교했다.")
        else:
            desired = VerificationStatus(item["verification"])
            supports, opposes = any(factual(ref) for ref in support), any(factual(ref) for ref in counter)
            if (
                desired not in (VerificationStatus.SUPPORTED, VerificationStatus.PARTIAL, VerificationStatus.DISPUTED)
                or supports
            ) and (desired not in (VerificationStatus.CONTRADICTED, VerificationStatus.DISPUTED) or opposes):
                state = desired
            else:
                limitations.append("커뮤니티 내용·누락·미검토 근거만으로 주장을 확인하지 않았다.")
            limitations.append(
                "reviewed_links_v1: 내용의 의미 판정은 명시한 사례 검토 기록이며 자동 사실 판정이 아니다."
            )
        claims.append(
            ResearchClaim(
                item["id"],
                item["text"],
                tuple(item["asset_ids"]),
                state,
                review,
                tuple(support),
                tuple(counter),
                narrative,
                tuple(limitations),
                item.get("recheck", "구절·정의·시점과 반대 근거를 추가로 검토한다."),
                tuple(context),
            )
        )
    brief = ResearchBrief(
        plan.id,
        plan.question,
        cutoff,
        "KRW",
        "실제 과거 공개 자료의 출처·주장 검증; 현재 투자 판단은 하지 않는다.",
        tuple(e.id for e in evidence if e.kind != "observed_narrative"),
        ("전체 시장 조사·개인 자산배분·매매 판단은 이번 범위에서 제외한다.",),
        (
            "자료의 과거 사실 확인과 현재 투자환경 적용은 다르다.",
            "자료 정의가 다른 수치를 수익률·매력 순위로 합치지 않는다.",
        ),
    )
    profile = ProfileSnapshot(plan.id + "_PROFILE", cutoff, {"base_currency": ProfileField("known", "KRW")})
    labels = dict(zip(ASSET_IDS, zip(("현금성 노출", "국채 노출", "주식 노출"), ("cash", "government_bond", "equity"))))
    alternatives = tuple(
        Alternative(
            identifier,
            *labels.get(identifier, (identifier, identifier.lower())),
            "투자수익을 계산하지 않는다",
            "실제 상품·유동성은 미확인이다",
            (),
            (),
            ("출처 검증만 수행하여 자산의 매력·개인 적절성은 미확인이다.",),
            (),
        )
        for identifier in plan.asset_ids
    )
    return ResearchCase(
        "1",
        False,
        brief,
        profile,
        tuple(source_records),
        tuple(evidence),
        tuple(claims),
        alternatives,
        (),
        (),
        _digest({"plan": plan.input_digest, "pins": pins, "as_of": cutoff.isoformat(), "method": PIPELINE_VERSION}),
        True,
        tuple(diagnostics),
    )
