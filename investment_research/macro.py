"""Small, offline macro-series core with explicit point-in-time availability.

Dates describe observations; they never establish when a particular version was
known. Unknown release/version history uses retrieval as a conservative floor.
Calculations use fixed Decimal rules and preserve their exact input references.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timezone
from decimal import Context, Decimal, DecimalException, ROUND_HALF_EVEN, localcontext
import hashlib
import json
from types import MappingProxyType
from typing import Iterable, Mapping

from .sources import SourceError


MACRO_VERSION = "macro_series_v1"
_UTC = timezone.utc
_ARITHMETIC = Context(prec=50, rounding=ROUND_HALF_EVEN)
_FREQUENCIES = {"daily", "weekly", "monthly", "quarterly", "annual"}


class MacroError(SourceError):
    """Invalid definitions, observations, or incompatible transformation inputs."""


def _text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise MacroError(f"{name}: nonempty text required")


def _date(value: object, name: str) -> date:
    if type(value) is not date:
        raise MacroError(f"{name}: date required")
    return value


def _instant(value: object, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise MacroError(f"{name}: timezone-aware datetime required")
    return value.astimezone(_UTC)


def _cutoff(value: date | datetime) -> datetime:
    if isinstance(value, datetime):
        return _instant(value, "as_of")
    return datetime.combine(_date(value, "as_of"), time.max, _UTC)


def _digest(value: object) -> str:
    def encode(item: object) -> str:
        if isinstance(item, (date, datetime)):
            return item.isoformat()
        if isinstance(item, Decimal):
            return str(item)
        raise TypeError(type(item).__name__)
    payload = json.dumps(value, default=encode, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SeriesDefinition:
    canonical_id: str
    name: str
    definition: str
    unit: str
    frequency: str
    adjustment: str
    publisher: str
    source_id: str
    jurisdiction: str
    currency: str | None = None
    transformation: str = "raw"
    release_characteristics: str = "unknown"
    revision_characteristics: str = "unknown"
    yield_type: str | None = None
    tenor_years: int | None = None
    max_age_days: int = 45

    def __post_init__(self) -> None:
        for name in ("canonical_id", "name", "definition", "unit", "adjustment", "publisher",
                     "source_id", "jurisdiction", "transformation", "release_characteristics",
                     "revision_characteristics"):
            _text(getattr(self, name), name)
        if not isinstance(self.frequency, str) or self.frequency not in _FREQUENCIES:
            raise MacroError("frequency: unsupported observation frequency")
        for name in ("currency", "yield_type"):
            if getattr(self, name) is not None:
                _text(getattr(self, name), name)
        if self.tenor_years is not None and (type(self.tenor_years) is not int or self.tenor_years <= 0):
            raise MacroError("tenor_years: positive integer required")
        if type(self.max_age_days) is not int or self.max_age_days < 0:
            raise MacroError("max_age_days: nonnegative integer required")

    @property
    def digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True)
class MacroObservation:
    series_id: str
    observation_date: date
    value: Decimal | None
    retrieved_at: datetime
    source_id: str
    snapshot_id: str
    locator: str
    released_at: datetime | None = None
    vintage_at: datetime | None = None
    revised_at: datetime | None = None
    known_at: datetime | None = None
    valid_as_of: date | None = None
    vintage_id: str | None = None
    unit: str | None = None
    frequency: str | None = None
    adjustment: str | None = None
    currency: str | None = None

    def __post_init__(self) -> None:
        for name in ("series_id", "source_id", "snapshot_id", "locator"):
            _text(getattr(self, name), name)
        _date(self.observation_date, "observation_date")
        if self.valid_as_of is not None:
            _date(self.valid_as_of, "valid_as_of")
        if self.value is not None and (not isinstance(self.value, Decimal) or not self.value.is_finite()):
            raise MacroError("value: finite Decimal or explicit None required")
        for name in ("retrieved_at", "released_at", "vintage_at", "revised_at", "known_at"):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, _instant(value, name))
        if self.retrieved_at is None:
            raise MacroError("retrieved_at: required")
        for name in ("vintage_id", "unit", "frequency", "adjustment", "currency"):
            if getattr(self, name) is not None:
                _text(getattr(self, name), name)

    @property
    def id(self) -> str:
        return "OBS_" + _digest(asdict(self))


@dataclass(frozen=True)
class SeriesSelection:
    definition: SeriesDefinition
    as_of: datetime
    observations: tuple[MacroObservation, ...]
    all_observations: tuple[MacroObservation, ...]
    excluded: tuple[MacroObservation, ...]
    latest: MacroObservation | None
    status: str
    diagnostics: tuple[str, ...] = ()


@dataclass(frozen=True)
class MacroMetric:
    id: str
    name: str
    output_series_id: str
    value: Decimal | None
    unit: str
    status: str
    transformation: str
    formula: str
    input_series_ids: tuple[str, ...]
    input_observation_ids: tuple[str, ...]
    observation_window: tuple[date, ...]
    assumptions: tuple[str, ...]
    direction: str | None = None
    diagnostics: tuple[str, ...] = ()


@dataclass(frozen=True)
class MacroSnapshot:
    as_of: datetime
    selections: tuple[SeriesSelection, ...]
    metrics: tuple[MacroMetric, ...]
    diagnostics: tuple[str, ...] = ()


def make_registry(definitions: Iterable[SeriesDefinition]) -> Mapping[str, SeriesDefinition]:
    registry: dict[str, SeriesDefinition] = {}
    for definition in definitions:
        if not isinstance(definition, SeriesDefinition):
            raise MacroError("registry: SeriesDefinition required")
        old = registry.get(definition.canonical_id)
        if old is not None and old != definition:
            raise MacroError(f"{definition.canonical_id}: canonical definition changed")
        registry[definition.canonical_id] = definition
    return MappingProxyType(dict(sorted(registry.items())))


def _availability(observation: MacroObservation, definition: SeriesDefinition) -> tuple[datetime, str | None]:
    dates = [value for value in (observation.released_at, observation.vintage_at,
                                 observation.revised_at, observation.known_at) if value is not None]
    reason = None
    if observation.released_at is None:
        dates.append(observation.retrieved_at)
        reason = "공개 시각 unknown: 획득 시각을 보수적인 이용 가능 시점으로 사용"
    elif (observation.vintage_at is None and observation.revised_at is None
          and observation.known_at is None and definition.revision_characteristics != "not_revised"):
        dates.append(observation.retrieved_at)
        reason = "개정 판본의 이용 가능 시각 unknown: 획득 이전의 당시 값을 확인할 수 없음"
    return max(dates), reason


def _validate_observation(definition: SeriesDefinition, observation: MacroObservation) -> None:
    if observation.series_id != definition.canonical_id:
        raise MacroError(f"{observation.series_id}: wrong canonical series")
    if observation.source_id != definition.source_id:
        raise MacroError(f"{observation.series_id}: source changed")
    for name in ("unit", "frequency", "adjustment", "currency"):
        recorded = getattr(observation, name)
        if recorded is not None and recorded != getattr(definition, name):
            raise MacroError(f"{observation.series_id}: {name} changed")
    if definition.frequency == "monthly" and observation.observation_date.day != 1:
        raise MacroError("monthly observation_date: use the first day of the reference month")


def select_series(definition: SeriesDefinition, observations: Iterable[MacroObservation],
                  as_of: date | datetime, expected_period: date | None = None) -> SeriesSelection:
    if not isinstance(definition, SeriesDefinition):
        raise MacroError("selection: SeriesDefinition required")
    cutoff = _cutoff(as_of)
    if expected_period is not None:
        _date(expected_period, "expected_period")
        if definition.frequency == "monthly" and expected_period.day != 1:
            raise MacroError("monthly expected_period: first day required")
    items = tuple(observations)
    if any(not isinstance(item, MacroObservation) for item in items):
        raise MacroError("observations: MacroObservation required")
    relevant = tuple(sorted((item for item in items if item.series_id == definition.canonical_id),
                            key=lambda item: (item.observation_date, item.id)))
    candidates: dict[date, list[tuple[datetime, datetime, MacroObservation]]] = {}
    excluded: list[MacroObservation] = []
    diagnostics: list[str] = []
    for observation in relevant:
        _validate_observation(definition, observation)
        available, caveat = _availability(observation, definition)
        if caveat:
            diagnostics.append(f"{observation.id}: {caveat}")
        if (available > cutoff or observation.observation_date > cutoff.date()
                or (observation.valid_as_of is not None and observation.valid_as_of > cutoff.date())):
            excluded.append(observation)
            diagnostics.append(f"{observation.id}: 기준 시점 이후 공개/판본/관측일로 당시 사용 차단")
            continue
        version_dates = [value for value in (observation.released_at, observation.vintage_at,
                                             observation.revised_at, observation.known_at)
                         if value is not None]
        version = max(version_dates) if version_dates else observation.retrieved_at
        candidates.setdefault(observation.observation_date, []).append((available, version, observation))
    chosen: list[MacroObservation] = []
    for period, versions in sorted(candidates.items()):
        rank = max((item[0], item[1]) for item in versions)
        tied = [item[2] for item in versions if (item[0], item[1]) == rank]
        if any(item.value != tied[0].value for item in tied[1:]):
            raise MacroError(f"{definition.canonical_id} {period}: conflicting values for the same available vintage")
        chosen.append(min(tied, key=lambda item: item.id))
        if len(versions) > 1:
            diagnostics.append(f"{definition.canonical_id} {period}: {len(versions)}개 판본 보존; 당시 마지막 판본 선택")
    latest = (next((item for item in chosen if item.observation_date == expected_period), None)
              if expected_period is not None else (chosen[-1] if chosen else None))
    if latest is None or latest.value is None:
        status = "blocked" if not chosen and excluded else "missing"
        diagnostics.append("요청한 관측치 없음/결측: 이전 값을 현재 값으로 대체하지 않음")
    elif (cutoff.date() - latest.observation_date).days > definition.max_age_days:
        status = "stale"
        diagnostics.append(f"{definition.canonical_id}: 마지막 관측치가 {definition.max_age_days}일 신선도 한도 초과")
    else:
        status = "available"
    return SeriesSelection(definition, cutoff, tuple(chosen), relevant, tuple(excluded),
                           latest, status, tuple(diagnostics))


def _month_shift(period: date, months: int) -> date | None:
    year, month = divmod(period.year * 12 + period.month - 1 + months, 12)
    try:
        return date(year, month + 1, period.day)
    except ValueError:
        return None


def _period(selection: SeriesSelection, period: date | None) -> date | None:
    if period is not None:
        _date(period, "period")
        return period
    return selection.latest.observation_date if selection.latest is not None else None


def _at(selection: SeriesSelection, period: date | None) -> MacroObservation | None:
    return next((item for item in selection.observations if item.observation_date == period), None)


def _metric(name: str, transformation: str, formula: str, selections: tuple[SeriesSelection, ...],
            observations: tuple[MacroObservation, ...], window: tuple[date, ...],
            value: Decimal | None, unit: str, diagnostics: tuple[str, ...] = (),
            *, directional: bool = False, output_suffix: str = "") -> MacroMetric:
    ids = tuple(item.definition.canonical_id for item in selections)
    output = "__".join(ids) + "__" + transformation + output_suffix
    reference = window[-1] if window else None
    status = "blocked" if value is None else ("stale" if any(
        reference is not None and (item.as_of.date() - reference).days > item.definition.max_age_days
        for item in selections) else "available")
    direction = ("up" if value > 0 else "down" if value < 0 else "unchanged") if directional and value is not None else None
    assumptions = ("Decimal precision 50; ROUND_HALF_EVEN", "결측 보간/forward-fill 없음")
    key = {"version": MACRO_VERSION, "output": output, "as_of": selections[0].as_of,
           "inputs": tuple(item.id for item in observations), "window": window}
    return MacroMetric("MET_" + _digest(key), name, output, value, unit, status, transformation,
                       formula, ids, tuple(item.id for item in observations), window,
                       assumptions, direction, diagnostics)


def _calculate(operation) -> Decimal:
    try:
        with localcontext(_ARITHMETIC):
            value = operation()
        if not value.is_finite():
            raise MacroError("transformation: nonfinite result")
        return value
    except DecimalException as error:
        raise MacroError("transformation: Decimal arithmetic failed") from error


def _monthly_index(selection: SeriesSelection) -> None:
    definition = selection.definition
    if definition.frequency != "monthly" or definition.unit != "index" or definition.transformation != "raw":
        raise MacroError("YoY: monthly raw index series required")


def yoy(selection: SeriesSelection, period: date | None = None) -> MacroMetric:
    _monthly_index(selection)
    current_period = _period(selection, period)
    prior_period = _month_shift(current_period, -12) if current_period is not None else None
    current, prior = _at(selection, current_period), _at(selection, prior_period)
    inputs = tuple(item for item in (prior, current) if item is not None)
    window = tuple(item for item in (prior_period, current_period) if item is not None)
    value, diagnostics = None, []
    if current is None or prior is None or current.value is None or prior.value is None:
        diagnostics.append("YoY: 정확한 현재/12개월 전 관측치가 없거나 결측")
    elif prior.value <= 0 or current.value <= 0:
        diagnostics.append("YoY: 양수 index endpoint 필요")
    else:
        value = _calculate(lambda: (current.value / prior.value - Decimal(1)) * Decimal(100))
        gaps = [shift for shift in range(-11, 0) if (item := _at(selection, _month_shift(current_period, shift))) is None
                or item.value is None]
        if gaps:
            diagnostics.append(f"중간 {len(gaps)}개월 결측 보존; YoY는 정확한 두 endpoint만 사용")
    return _metric("전년 동월 대비 물가 상승률", "yoy_v1", "(index_t / index_t_minus_12_months - 1) * 100",
                   (selection,), inputs, window, value, "percent", tuple(diagnostics))


def yield_spread(ten_year: SeriesSelection, two_year: SeriesSelection,
                 period: date | None = None) -> MacroMetric:
    ten, two = ten_year.definition, two_year.definition
    if ten_year.as_of != two_year.as_of:
        raise MacroError("yield spread: different as-of cutoffs")
    if (ten.unit != "percent" or two.unit != "percent" or ten.frequency != "daily"
            or two.frequency != "daily" or ten.adjustment != two.adjustment
            or ten.currency != two.currency or ten.currency is None
            or ten.yield_type != two.yield_type or ten.yield_type is None
            or ten.tenor_years != 10 or two.tenor_years != 2
            or ten.transformation != "raw" or two.transformation != "raw"):
        raise MacroError("yield spread: compatible daily percent/yield-type/currency/adjustment and 10Y/2Y required")
    current_period = _period(ten_year, period)
    a, b = _at(ten_year, current_period), _at(two_year, current_period)
    mismatch = period is None and _period(two_year, None) != current_period
    inputs = tuple(item for item in (a, b) if item is not None)
    value = None if mismatch or a is None or b is None or a.value is None or b.value is None else _calculate(lambda: a.value - b.value)
    diagnostics = ("10년/2년 동일 관측일의 두 값 필요; 마지막 공통 날짜로 대체하지 않음",) if value is None else ()
    return _metric("10년−2년 국채 수익률 차이", "yield_spread_v1", "yield_10y_t - yield_2y_t",
                   (ten_year, two_year), inputs, (current_period,) if current_period is not None else (),
                   value, "percentage_points", diagnostics)


def _difference(selection: SeriesSelection, current_period: date | None, prior_period: date | None,
                transformation: str, name: str, suffix: str = "") -> MacroMetric:
    current, prior = _at(selection, current_period), _at(selection, prior_period)
    inputs = tuple(item for item in (prior, current) if item is not None)
    window = tuple(item for item in (prior_period, current_period) if item is not None)
    value = None if current is None or prior is None or current.value is None or prior.value is None else _calculate(lambda: current.value - prior.value)
    unit = "percentage_points" if selection.definition.unit == "percent" else selection.definition.unit
    return _metric(name, transformation, "current_value - exact_reference_value", (selection,),
                   inputs, window, value, unit,
                   ("정확한 비교 관측치 없음/결측",) if value is None else (),
                   directional=True, output_suffix=suffix)


def trend_change(selection: SeriesSelection, months_back: int = 1,
                 period: date | None = None) -> MacroMetric:
    if type(months_back) is not int or months_back not in {1, 3, 6, 12}:
        raise MacroError("trend: predefined 1/3/6/12-month window required")
    current = _period(selection, period)
    prior = _month_shift(current, -months_back) if current is not None else None
    return _difference(selection, current, prior, "trend_change_v1", f"정확한 {months_back}개월 전 대비 변화",
                       f"_{months_back}m")


def previous_change(selection: SeriesSelection, period: date | None = None) -> MacroMetric:
    current = _period(selection, period)
    if selection.definition.frequency == "monthly":
        prior = _month_shift(current, -1) if current is not None else None
    else:
        earlier = [item.observation_date for item in selection.observations
                   if current is not None and item.observation_date < current]
        prior = max(earlier) if earlier else None
    return _difference(selection, current, prior, "previous_change_v1", "직전 관측치 대비 변화")


def inflation_trend(selection: SeriesSelection, period: date | None = None) -> MacroMetric:
    _monthly_index(selection)
    current = _period(selection, period)
    prior = _month_shift(current, -1) if current is not None else None
    now_metric, prior_metric = yoy(selection, current), yoy(selection, prior) if prior is not None else None
    value = None if prior_metric is None or now_metric.value is None or prior_metric.value is None else _calculate(lambda: now_metric.value - prior_metric.value)
    ids = set(now_metric.input_observation_ids)
    if prior_metric is not None:
        ids.update(prior_metric.input_observation_ids)
    inputs = tuple(item for item in selection.observations if item.id in ids)
    window = tuple(sorted({item.observation_date for item in inputs}))
    diagnostics = now_metric.diagnostics + (prior_metric.diagnostics if prior_metric is not None else ())
    if value is None:
        diagnostics += ("물가 상승률 방향: 현재/정확한 전월 YoY 각각의 endpoint 필요",)
    return _metric("전월 대비 물가 상승률 변화", "inflation_trend_v1", "YoY_t - YoY_t_minus_1_month",
                   (selection,), inputs, window, value, "percentage_points", diagnostics, directional=True)


def build_macro_snapshot(definitions: Iterable[SeriesDefinition], observations: Iterable[MacroObservation],
                         as_of: date | datetime, yoy_series_ids: tuple[str, ...] = (),
                         yield_pair: tuple[str, str] | None = None) -> MacroSnapshot:
    registry = make_registry(definitions)
    items = tuple(observations)
    if any(not isinstance(item, MacroObservation) for item in items):
        raise MacroError("observations: MacroObservation required")
    unknown = {item.series_id for item in items} - registry.keys()
    if unknown:
        raise MacroError(f"observations: unknown canonical IDs {sorted(unknown)}")
    selections = tuple(select_series(definition, items, as_of) for definition in registry.values())
    by_id = {item.definition.canonical_id: item for item in selections}
    metrics: list[MacroMetric] = [previous_change(item) for item in selections]
    for series_id in yoy_series_ids:
        if series_id not in by_id:
            raise MacroError(f"YoY: unknown canonical ID {series_id}")
        metrics.extend((yoy(by_id[series_id]), inflation_trend(by_id[series_id])))
    if yield_pair is not None:
        if len(yield_pair) != 2 or any(series_id not in by_id for series_id in yield_pair):
            raise MacroError("yield_pair: existing 10Y/2Y IDs required")
        metrics.append(yield_spread(by_id[yield_pair[0]], by_id[yield_pair[1]]))
    return MacroSnapshot(_cutoff(as_of), selections, tuple(metrics),
                         tuple(message for item in selections for message in item.diagnostics))
