"""Deterministic Korean macro explanation; numbers come from linked results.

This layer formats observations and calculations. It does not calculate financial
metrics, infer an investment regime, or turn transmission hypotheses into facts.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from hashlib import sha256
from html import escape
import re
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from .macro import MACRO_VERSION, MacroError, MacroMetric, SeriesSelection

if TYPE_CHECKING:
    from .macro_pipeline import MacroRun


MACRO_REPORT_VERSION = "macro_report_v1"
_STATUS = {
    "available": "사용 가능",
    "stale": "오래된 자료 · 현재 설명에 채택 보류",
    "missing": "요청한 최신 관측 없음/결측",
    "blocked": "시점 또는 계산 전제 부족 · 차단",
}
_UNIT = {"percent": "%", "percentage_points": "%p", "index": "지수", "KRW_per_USD": "원/USD"}
_DIRECTION = {"up": "상승", "down": "하락", "unchanged": "변화 없음"}


def _text(value: object) -> str:
    text = str(value).replace("\r\n", "\n").replace("\r", "\n").replace("\n", " / ")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text)
    return re.sub(r"([\\`*_{}\[\]#|~])", r"\\\1", escape(text, quote=False))


def _target(identifier: str) -> str:
    return "macro-record-" + sha256(identifier.encode("utf-8")).hexdigest()


def _anchor(identifier: str) -> str:
    return f'<a id="{_target(identifier)}"></a>'


def _ref(identifier: str) -> str:
    label = (
        "관측 " + identifier[4:12]
        if identifier.startswith("OBS_")
        else "계산 " + identifier[4:12] if identifier.startswith("MET_") else identifier
    )
    return f"[{_text(label)}](#{_target(identifier)})"


def _refs(identifiers: tuple[str, ...]) -> str:
    return ", ".join(_ref(identifier) for identifier in identifiers) or "없음"


def _number(value: Decimal) -> str:
    # Display rounding only. The exact value and formula remain in the appendix.
    with localcontext() as context:
        context.rounding = ROUND_HALF_EVEN
        return format(value, ".3f")


def _instant(value: object) -> str:
    return _text(value.isoformat()) if value is not None else "unknown · 미확인"


def _code(value: object) -> str:
    return "<code>" + escape(str(value), quote=False) + "</code>"


def _status(status: str) -> str:
    return _STATUS.get(status, _text(status))


def _metric_text(metric: MacroMetric) -> str:
    if metric.status != "available" or metric.value is None:
        return f"{_text(metric.name)}: {_status(metric.status)} ({_ref(metric.id)})"
    direction = f"; 두 비교값 사이의 방향: {_DIRECTION[metric.direction]}" if metric.direction else ""
    dates = ", ".join(item.isoformat() for item in metric.observation_window) or "미확인"
    return (
        f"{_text(metric.name)}: {_number(metric.value)} {_text(_UNIT.get(metric.unit, metric.unit))}"
        f"{direction}; 비교 관측일: {dates} ({_ref(metric.id)})"
    )


def _series_table(selections: tuple[SeriesSelection, ...]) -> list[str]:
    lines = ["| 자료 | 기준 관측 | 값 | 채택 상태 |", "| --- | --- | --- | --- |"]
    for selection in selections:
        observation = selection.latest
        date_text = observation.observation_date.isoformat() if observation else "미확인"
        value = (
            f"{_number(observation.value)} {_text(_UNIT.get(selection.definition.unit, selection.definition.unit))} "
            f"({_ref(observation.id)})"
            if selection.status == "available" and observation and observation.value is not None
            else "현재 값으로 채택하지 않음"
        )
        lines.append(f"| {_text(selection.definition.name)} | {date_text} | {value} | {_status(selection.status)} |")
    return lines


def _check_links(run: MacroRun) -> None:
    evidence = {item.id: item for item in run.case.evidence}
    results = {item.id: item for item in run.metrics}
    observations = {item.id: item for selection in run.snapshot.selections for item in selection.all_observations}
    for selection in run.snapshot.selections:
        if selection.status != "available" or selection.latest is None or selection.latest.value is None:
            continue
        item = evidence.get(selection.latest.id)
        if (
            item is None
            or item.value != selection.latest.value
            or item.source_id != selection.latest.source_id
            or item.unit != selection.definition.unit
        ):
            raise MacroError("macro report: latest observation has no matching EvidenceRecord")
    for metric in run.snapshot.metrics:
        if metric.status != "available" or metric.value is None:
            continue
        result = results.get(metric.id)
        if (
            result is None
            or result.value != metric.value
            or result.unit != metric.unit
            or result.input_ids != metric.input_observation_ids
            or result.method != metric.transformation
        ):
            raise MacroError("macro report: calculation has no matching MetricResult")
        if any(identifier not in evidence for identifier in metric.input_observation_ids):
            raise MacroError("macro report: calculation input has no EvidenceRecord")
    for item in run.case.evidence:
        observation = observations.get(item.id)
        if (
            observation is None
            or item.value != observation.value
            or item.source_id != observation.source_id
            or item.locator != observation.locator
            or item.provenance is None
            or item.provenance.snapshot_id != observation.snapshot_id
            or item.provenance.match_status != "matched"
        ):
            raise MacroError("macro report: evidence disagrees with preserved observation")


def render_macro_report(run: MacroRun) -> str:
    """Render a fixed-cutoff snapshot without networking or financial arithmetic."""
    _check_links(run)
    snapshot = run.snapshot
    rates = tuple(
        item
        for item in snapshot.selections
        if item.definition.yield_type == "nominal" and item.definition.tenor_years in (2, 10)
    )
    inflation = tuple(
        item
        for item in snapshot.selections
        if item.definition.unit == "index" and item.definition.frequency == "monthly"
    )
    fx = tuple(item for item in snapshot.selections if item.definition.unit == "KRW_per_USD")
    metrics = snapshot.metrics

    def selected_metrics(selections: tuple[SeriesSelection, ...]) -> tuple[MacroMetric, ...]:
        ids = {item.definition.canonical_id for item in selections}
        return tuple(metric for metric in metrics if set(metric.input_series_ids) <= ids)

    def metric_of(kind: str, selections: tuple[SeriesSelection, ...]) -> MacroMetric | None:
        return next((metric for metric in selected_metrics(selections) if metric.transformation == kind), None)

    def metric_lines(selections: tuple[SeriesSelection, ...]) -> list[str]:
        names = {item.definition.canonical_id: item.definition.name for item in selections}
        return [
            f"- [계산 결과] {_text(' / '.join(names[identifier] for identifier in metric.input_series_ids))} · "
            f"{_metric_text(metric)}."
            for metric in selected_metrics(selections)
        ]

    def usable(metric: MacroMetric | None) -> bool:
        return metric is not None and metric.status == "available" and metric.value is not None

    yoy_metric = metric_of("yoy_v1", inflation)
    inflation_direction = metric_of("inflation_trend_v1", inflation)
    spread = metric_of("yield_spread_v1", rates)
    fx_direction = metric_of("previous_change_v1", fx)
    ten_year = tuple(item for item in rates if item.definition.tenor_years == 10)
    ten_direction = metric_of("previous_change_v1", ten_year)
    cutoff_kst = snapshot.as_of.astimezone(ZoneInfo("Asia/Seoul"))
    lines = [
        "# Macro Regime Snapshot · 공개 거시자료",
        "",
        "## 기준 시점",
        "",
        f"- 정보 기준 시각: {_instant(snapshot.as_of)} (UTC).",
        f"- 한국 시각: {_instant(cutoff_kst)} (Asia/Seoul). 두 표시는 같은 순간이다.",
        f"- 연구 질문: {_text(run.plan.question)}.",
        "- 선택한 정의와 저장된 판본 중 이 기준 시각에 이용 가능한 관측만 사용한다. 관측일·발표일·획득일은 다르다.",
        "- '현재'는 이 고정 기준 시각의 이용 가능한 자료를 뜻한다. 실시간 가격·전 시장·개인 투자 결론은 조사 범위에 없다.",
        "",
        "## 한눈에 보기",
        "",
    ]
    summary: list[str] = []
    if any(
        source.provenance is not None and source.provenance.status != "available" for source in run.case.sources
    ) or any("parsing blocked" in item for item in run.diagnostics):
        summary.append(
            "일부 출처의 최신 획득 또는 파싱이 실패했으므로, 각 자료의 관측일·고정 판본·채택 상태와 실패 진단을 함께 확인해야 한다."
        )
    if usable(yoy_metric):
        summary.append(
            f"미국 headline CPI의 전년 동월 대비 상승률은 {_number(yoy_metric.value)}%다 ({_ref(yoy_metric.id)})."
        )
    else:
        summary.append("물가 상승률의 현재 수치는 결측·시점·신선도 조건을 충족한 계산이 없어 채택하지 않았다.")
    if usable(inflation_direction):
        summary.append(
            f"전월의 전년 대비 상승률과 비교한 방향은 {_DIRECTION[inflation_direction.direction]}이며, "
            f"변화는 {_number(inflation_direction.value)}%p다 ({_ref(inflation_direction.id)})."
        )
    if usable(spread):
        summary.append(
            f"같은 관측일의 미국 10년−2년 명목 국채 수익률 차이는 {_number(spread.value)}%p다 ({_ref(spread.id)})."
        )
    else:
        summary.append("장단기 수익률 차이는 같은 날짜의 검증된 두 관측이 없어 현재 상태를 설명하지 않았다.")
    if usable(fx_direction):
        phrase = {"up": "상승했다", "down": "하락했다", "unchanged": "변화가 없다"}[fx_direction.direction]
        summary.append(f"USD당 KRW 기준 환율은 직전 관측과 비교해 {phrase} ({_ref(fx_direction.id)}).")
    else:
        summary.append("환율의 최신 변화는 이용 가능한 계산으로 확인하지 못했다.")
    summary.append(
        "고용·정책금리·실질금리·성장·신용·유동성은 이번 자료에 없으므로 전체 경기 상태나 자산 매력을 확정하지 않는다."
    )
    lines.extend(summary[:5])
    lines.extend(
        [
            "",
            "## 금리",
            "",
            "사용한 금리는 미국 국채의 **명목 시장 수익률**이다. 중앙은행 정책금리·예금 이자·확정 투자수익과 구분한다.",
            "",
        ]
    )
    lines.extend(_series_table(rates) if rates else ["이 정의의 시장금리 자료가 없다."])
    lines.append("")
    lines.extend(metric_lines(rates))
    lines.extend(
        [
            "",
            "직전 관측 비교는 두 날짜 사이의 변화다. 지속적인 추세나 '역사적으로 높은 금리'를 판정하는 규칙은 구현하지 않았다.",
            "",
            "## 물가",
            "",
            "미국 도시 소비자 headline CPI의 **계절조정하지 않은 지수**를 사용한다. Core CPI나 계절조정 전월비와 합치지 않는다.",
            "",
        ]
    )
    lines.extend(_series_table(inflation) if inflation else ["이 정의의 물가지수 자료가 없다."])
    lines.append("")
    lines.extend(metric_lines(inflation))
    lines.extend(
        [
            "",
            "지수의 직전 관측 변화는 물가 수준의 변화이며 물가 상승률의 방향과 다르다. 상승률 방향은 현재 YoY와 정확한 전월 YoY의 차이로만 표시한다.",
            "계절조정하지 않은 지수의 전월 변화에는 계절성이 포함될 수 있다. 상승률 하락은 가격 자체의 하락을 뜻하지 않는다.",
            "",
            "## 경기 / 고용",
            "",
            "이번 작은 자료 집합에는 고용·실업·생산·성장 지표가 없다. 경기 둔화·침체나 고용 강약을 대신 추론하지 않았다.",
            "",
            "## 환율 / 한국 투자자 관점",
            "",
            "USD/KRW는 **USD당 KRW**다. 뉴욕 정오 기준 환율 관측을 쓰며 국내 체결 환율·실시간 호가·환전 비용과 구분한다.",
            "",
        ]
    )
    lines.extend(_series_table(fx) if fx else ["이 정의의 KRW 환율 자료가 없다."])
    lines.append("")
    lines.extend(metric_lines(fx))
    if usable(fx_direction):
        direction_note = {
            "up": "같은 USD를 원화로 표시할 때 금액이 커졌다는 뜻이며, 이 관측 사이에서는 원화 약세에 해당한다.",
            "down": "같은 USD를 원화로 표시할 때 금액이 작아졌다는 뜻이며, 이 관측 사이에서는 원화 강세에 해당한다.",
            "unchanged": "두 관측의 USD당 원화 금액이 같다는 뜻이며, 다른 날짜까지 안정적이었다는 뜻은 아니다.",
        }
        lines.extend(["", f"[정의에 따른 해석] {direction_note[fx_direction.direction]} ({_ref(fx_direction.id)})."])
    lines.extend(
        [
            "",
            "미국 자산 자체의 USD 시장환경과 한국 투자자의 KRW 평가환경은 별도다. 자산 가격·배당·환헤지·비용·세금 자료 없이 개인의 KRW 수익률을 계산하지 않았다.",
            "",
            "## 서로 상충하는 신호",
            "",
        ]
    )
    if usable(inflation_direction) and usable(ten_direction):
        lines.append(
            f"[관측·계산] 전년 대비 물가 상승률의 전월 비교는 {_DIRECTION[inflation_direction.direction]}, "
            f"10년 시장금리의 직전 관측 비교는 {_DIRECTION[ten_direction.direction]}이다 "
            f"({_ref(inflation_direction.id)}, {_ref(ten_direction.id)})."
        )
        if inflation_direction.direction != ten_direction.direction:
            lines.append(
                "[해석 후보] 방향이 같지 않아 '물가 변화가 금리 변화를 전부 설명한다'는 단순한 설명만으로 읽기 어렵다. "
                "성장 기대·기간 프리미엄 등 다른 설명을 검토해야 하지만 이번 자료는 원인을 확인하지 않는다."
            )
        else:
            lines.append("[해석의 한계] 두 변화의 방향이 같아도 같은 원인이나 인과관계를 입증하지 않는다.")
        lines.append(
            "물가 비교는 월별, 금리 비교는 일별이며 서로 다른 관측창이다. 같은 사건에 대한 통계적 모순으로 판정하지 않는다."
        )
    else:
        lines.append("채택 가능한 물가 상승률 변화와 장기금리 변화가 함께 없어 두 신호의 현재 방향을 비교하지 않았다.")
    lines.extend(
        [
            "",
            "## 투자환경에 어떤 의미가 있을 수 있는가",
            "",
            "아래는 **조건부 전파 경로·검토 전 해석 후보**다. 위 관측 사실·계산 결과와 구분하며, 경제적 관계의 실증 검증이나 투자 규칙으로 확정하지 않는다.",
            "",
        ]
    )
    if any(item.status == "available" for item in rates):
        ids = tuple(item.latest.id for item in rates if item.status == "available" and item.latest is not None)
        lines.append(
            f"- **금리 → 채권·기업 가치:** 다른 조건이 같고 현금흐름이 고정되어 있다면 할인율 변화는 현재가치에 영향을 줄 수 있다. "
            f"입력 사실: {_refs(ids)}. 실제 영향에는 만기·듀레이션·신용·이익 전망이 필요하며 여기서는 계산하지 않았다."
        )
    if usable(yoy_metric):
        lines.append(
            f"- **물가 → 현금·채권의 구매력:** 명목 이자와 같은 기간의 실제 물가 변화가 필요하다. "
            f"입력 사실: {_ref(yoy_metric.id)}. 현재 YoY를 미래 물가나 특정 자산의 실질수익으로 바꾸지 않았다."
        )
    if usable(fx_direction):
        lines.append(
            f"- **환율 → 해외자산의 KRW 표시 가치:** 같은 USD 가치와 환노출을 유지한다는 조건에서 환율은 원화 평가에 영향을 줄 수 있다. "
            f"입력 사실: {_ref(fx_direction.id)}. 실제 상품·환헤지·평가 시점과 사용자 보유 내역은 미확인이다."
        )
    if not any(item.status == "available" for item in snapshot.selections):
        lines.append("- 현재 설명에 채택 가능한 관측이 없어 개별 투자환경 해석의 입력으로 사용하지 않았다.")
    lines.extend(
        [
            "",
            "현금·국채·주식·배당주·금·원자재·에너지·암호자산·한국 부동산의 향후 연구가 이 근거를 참조할 수 있다. "
            "이번에는 해당 자산의 상대 매력·정해진 대응·매수/매도·배분을 생성하지 않는다.",
            "",
            "## 아직 말할 수 없는 것",
            "",
            "- 정책금리의 최근 방향, 고용 강약, 경기 침체 여부, 한국 기준금리·한국 물가, 실질금리·신용·유동성의 전체 상태.",
            "- '높다/낮다'의 역사적 기준, 지속적인 추세, 미래 금리·환율·물가, 기대수익·자산 순위·개인 투자비중.",
            "- 공식 개정 이력의 전체 재현: 저장한 판본은 시스템의 획득 판본이며 공식 release/vintage archive와 같지 않다.",
            "- 공개·개정 시각이 unknown인 현재 파일의 값이 과거 투자자에게 같은 형태로 보였는지 여부.",
            "- 관측 주기와 발표 지연 사이의 아직 발표되지 않은 최신 값. 결측·오래된 자료는 이전 값으로 조용히 채우지 않는다.",
            "- 개인 보유자산·현금흐름·부채·필요 자금이 미확인이므로 이 환경이 사용자에게 적절한 배분을 뜻하는지 여부.",
            "",
            "## 초간단 설명",
            "",
            "이 보고서는 정한 시각까지 알 수 있었던 물가·국채 금리·환율 자료를 살펴본다.",
            "숫자가 언제의 자료이고 언제 알려졌는지 확인하고, 없는 값은 만들어 넣지 않는다.",
            "물가 상승이 느려지는 것과 물건 가격이 내려가는 것은 다르다.",
            "달러 값이 원화로 바뀌는 효과는 미국 자산 자체의 움직임과 따로 봐야 한다.",
            "이 자료만으로 무엇을 사거나 돈을 얼마나 나눌지 정할 수는 없다.",
            "",
            "## 부록 · 근거와 재현 기록",
            "",
            f"- 연구 ID: {_text(run.plan.id)}; 입력 SHA-256: {_text(run.input_digest)}.",
            f"- 시계열 방법: {MACRO_VERSION}; 보고서 방법: {MACRO_REPORT_VERSION}.",
            "- 본문 수치는 소수 셋째 자리까지 표시했다. 아래 계산의 정확한 Decimal 값·원관측·공식·가정은 보존한다.",
            "- release/vintage/revision의 unknown을 관측일이나 획득일로 채우지 않는다. unknown일 때 이용 가능성은 획득 시각부터 보수적으로 인정한다.",
            "- 전체 observation·제외된 판본·결측·진단은 실행 manifest와 저장된 snapshot에 남긴다. 이 부록은 본문·계산이 참조한 근거를 보여 준다.",
            "",
            "### 시계열 정의와 선택",
            "",
        ]
    )
    for selection in snapshot.selections:
        definition, latest = selection.definition, selection.latest
        lines.extend(
            [
                f"#### {_text(definition.name)}",
                "",
                f"- canonical ID: {_text(definition.canonical_id)}; 정의 SHA-256: {definition.digest}.",
                f"- 정의: {_text(definition.definition)}.",
                f"- 단위: {_text(definition.unit)}; 빈도: {_text(definition.frequency)}; 계절조정: {_text(definition.adjustment)}; "
                f"통화: {_text(definition.currency) if definition.currency else '해당 없음'}; 변환: {_text(definition.transformation)}.",
                f"- 발행 주체: {_text(definition.publisher)}; 관할: {_text(definition.jurisdiction)}; 출처: {_ref(definition.source_id)}.",
                f"- 발표 특성: {_text(definition.release_characteristics)}; 개정 특성: {_text(definition.revision_characteristics)}.",
                f"- 선택 상태: {_status(selection.status)}; 전체 판본 {len(selection.all_observations)}개, "
                f"시점 조건 뒤 선택한 기간 {len(selection.observations)}개, 이후 정보로 제외한 판본 {len(selection.excluded)}개.",
                f"- 신선도 규칙: 기준 시점의 날짜와 마지막 관측일의 차이가 {definition.max_age_days}일을 초과하면 stale.",
            ]
        )
        if latest is not None:
            lines.extend(
                [
                    f"- 마지막 선택 관측: {_text(latest.observation_date.isoformat())}; "
                    f"공개: {_instant(latest.released_at)}; 획득: {_instant(latest.retrieved_at)}; "
                    f"vintage: {_instant(latest.vintage_at)}; revision: {_instant(latest.revised_at)}; "
                    f"known-at: {_instant(latest.known_at)}; valid-as-of: {_instant(latest.valid_as_of)}.",
                    f"- 마지막 관측의 snapshot: {_text(latest.snapshot_id)}; vintage ID: "
                    f"{_text(latest.vintage_id) if latest.vintage_id else 'unknown · 미확인'}.",
                ]
            )
        else:
            lines.append("- 해당 기준 시점의 마지막 이용 가능 관측을 선택하지 못했다.")
        if selection.diagnostics:
            lines.append("- 선택 진단의 요약: " + " / ".join(_text(item) for item in selection.diagnostics[-2:]) + ".")
        lines.append("")
    lines.extend(["### 고정 출처와 snapshot", ""])
    for source in run.case.sources:
        lines.extend(
            [
                _anchor(source.id),
                "",
                f"- {_text(source.name)}; 출처 ID: {_text(source.id)}; 위치: {_text(source.location)}.",
                f"- 사용한 고정 snapshot: {_text(', '.join(run.snapshot_refs.get(source.id, [])) or '없음')}.",
            ]
        )
        provenance = source.provenance
        if provenance is not None:
            lines.extend(
                [
                    f"- source-level metadata의 판본: {_text(provenance.snapshot_id)}; 획득: {_text(provenance.retrieved_at)}; "
                    "각 관측의 정확한 판본은 아래 evidence의 snapshot을 따른다.",
                    f"- 접근: {_text(provenance.access_method)}; 보존: {_text(provenance.retention)}; 상태: {_text(provenance.status)}.",
                    f"- 정책: {_text(provenance.policy_url)}; 검토: {_text(provenance.policy_note)}.",
                    f"- 원문 SHA-256: {_text(provenance.raw_sha256 or '미보존')}; 정규화 SHA-256: "
                    f"{_text(provenance.normalized_sha256 or '미보존')}; payload SHA-256: {_text(provenance.payload_sha256)}.",
                ]
            )
            if source.location.startswith(
                ("https://api.bls.gov/", "https://www.bls.gov/", "https://download.bls.gov/")
            ):
                lines.extend(
                    [
                        f"- 이 BLS 자료의 실제 획득 시각: {_text(provenance.retrieved_at)}.",
                        "- BLS 이용 안내 · 획득 이후 분석에 대한 보증 없음: "
                        "BLS.gov cannot vouch for the data or analyses derived from these data after the data have been retrieved from BLS.gov.",
                    ]
                )
        lines.append("")
    observations = {item.id: item for selection in snapshot.selections for item in selection.all_observations}
    definitions = {item.definition.canonical_id: item.definition for item in snapshot.selections}
    lines.extend(["### 본문과 계산이 참조한 원관측 / 기존 EvidenceRecord", ""])
    for evidence in run.case.evidence:
        observation = observations[evidence.id]
        definition = definitions[observation.series_id]
        lines.extend(
            [
                _anchor(evidence.id),
                "",
                f"- 기존 EvidenceRecord / 관측 ID: {_code(evidence.id)}.",
                f"- {_ref(evidence.id)}: {_text(definition.canonical_id)}; 관측일: {observation.observation_date.isoformat()}; "
                f"원자료 값: {_text(format(observation.value, 'f')) if observation.value is not None else 'missing · 결측'} "
                f"{_text(definition.unit)}.",
                f"- 출처: {_ref(evidence.source_id)}; snapshot: {_text(observation.snapshot_id)}; 원문 위치: {_text(observation.locator)}.",
                f"- 공개: {_instant(observation.released_at)}; 획득: {_instant(observation.retrieved_at)}; "
                f"vintage: {_instant(observation.vintage_at)}; revision: {_instant(observation.revised_at)}; "
                f"known-at: {_instant(observation.known_at)}; valid-as-of: {_instant(observation.valid_as_of)}.",
                f"- 기존 근거의 확인 범위: {_text(evidence.verification.value)}; 해석 검토: {_text(evidence.interpretation.status.value)}; "
                f"freshness: {_text(evidence.provenance.freshness) if evidence.provenance else '미기록'}. "
                "현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.",
                "",
            ]
        )
        release = run.release_provenance.get(evidence.id)
        if release is not None:
            lines.extend(
                [
                    f"- 공개 시각의 확인 자료: {_ref(release['source_id'])}; "
                    f"snapshot: {_text(release['snapshot_id'])}; 원문 구절 ID: {_text(', '.join(release['excerpt_ids']))}; "
                    f"방법: {_text(release['method'])}. 관측 기간·지수·발표 시각의 좁은 대조이며 사후 투자 해석의 보증이 아니다.",
                    "",
                ]
            )
    lines.extend(["### 결정적 계산 · 채택 가능한 값만 기존 MetricResult", ""])
    evidence_ids = {item.id for item in run.case.evidence}
    for metric in metrics:
        input_refs = (
            ", ".join(
                (
                    _ref(identifier)
                    if identifier in evidence_ids
                    else _text(identifier) + " (근거 미연결 · 계산 채택하지 않음)"
                )
                for identifier in metric.input_observation_ids
            )
            or "없음"
        )
        lines.extend(
            [
                _anchor(metric.id),
                "",
                f"- 계산 ID: {_code(metric.id)}.",
                f"- {_ref(metric.id)}: {_text(metric.name)}; 상태: {_status(metric.status)}.",
                f"- 출력 series: {_text(metric.output_series_id)}; 정확한 값: "
                f"{_text(format(metric.value, 'f')) if metric.value is not None else '계산하지 않음'} {_text(metric.unit)}. "
                "stale 값은 과거 계산 기록이며 현재 요약에 채택하지 않는다.",
                f"- 방법: {_text(metric.transformation)}; 공식: {_text(metric.formula)}.",
                f"- 입력 series: {_text(', '.join(metric.input_series_ids))}; 입력 관측: {input_refs}.",
                f"- 관측창: {_text(', '.join(item.isoformat() for item in metric.observation_window) or '없음')}; "
                f"가정: {_text(' / '.join(metric.assumptions))}.",
            ]
        )
        if metric.diagnostics:
            lines.append(f"- 계산 진단: {_text(' / '.join(metric.diagnostics))}.")
        lines.append("")
    lines.extend(["### 획득·연결 진단", ""])
    if run.diagnostics:
        lines.extend(f"- {_text(item)}" for item in run.diagnostics)
    else:
        lines.append("- 별도 획득·연결 실패가 기록되지 않았다. 전체 자료의 정확성이나 의미 검증을 보증하지 않는다.")
    return "\n".join(lines).rstrip() + "\n"
