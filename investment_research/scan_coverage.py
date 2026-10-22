"""Minimum coverage and point-in-time Scan comparisons; no investment score.

Past observations are a pinned comparison input, never current evidence. A new
source connection, a revised vintage and a market observation are distinct events.
"""

from collections import defaultdict
from copy import deepcopy
from dataclasses import replace
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
import calendar
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .sources import SourceError, _time
from .source_pipeline import _digest
from .models import MetricResult

VERSION = 'minimum_opportunity_evidence_v1'
HISTORY_VERSION = 'same_definition_scan_comparison_v1'
REGIONAL = 'KR_APARTMENTS_SEOUL_GYEONGGI_INCHEON'

# A slot describes a decision input, not another independent vote. The same
# observation may explain more than one slot without earning extra priority.
STANDARDS = {
    'equity': [
        ('market', '현재 가격 또는 대표 valuation', True),
        ('earnings', '실제 이익 변화 또는 명확한 이익 전망', True),
        ('change', '가격/배수/이익 전망의 동일 정의 변화', False),
        ('catalyst', '실제 촉매와 중요한 반대 논리', False),
    ],
    'bond': [
        ('yield', '현재 수익률과 명확한 만기·통화', True),
        ('change', '같은 만기의 최근 금리 변화', False),
        ('policy', '해당 국가 물가 또는 정책 맥락', False),
    ],
    'crypto': [
        ('market', '현재 거래소 가격', True),
        ('change', '의미 있는 기간의 같은 거래소 가격 흐름', True),
        ('flow', '해당 자산 ETF/기관 흐름(존재 시)', False),
        ('liquidity', '유동성 또는 레버리지 관측', False),
        ('catalyst', '주요 보유 논리와 downside', False),
    ],
    'gold': [
        ('market', '현재 금 기준가격', True),
        ('change', '같은 기준가격의 기간 변화', False),
        ('real_rate', '실질금리 맥락', False),
        ('demand', 'ETF 보유/중앙은행/실물 수요 중 하나', False),
    ],
    'oil': [
        ('market', '현재 원유 가격', True),
        ('physical', '재고/생산/수요의 실제 관측', True),
        ('structure', '선물곡선 또는 현재 실물 수급 변화', False),
    ],
    'gas': [
        ('market', '현재 천연가스 가격', True),
        ('physical', '실제 재고', True),
        ('production', '생산 관측', False),
        ('demand', '날씨/수요 맥락', False),
    ],
    'broad_commodity': [
        ('market', '광범위 지수/상품의 가격·구성', True),
        ('change', '대표 가격 흐름', False),
        ('physical', '복수 원자재의 수급 맥락', True),
    ],
    'real_estate': [
        ('market', '서울·경기·인천별 지역 가격 변화', True),
        ('volume', '각 지역 거래량', True),
        ('rent', '각 지역 전세/임대 변화', False),
        ('financing', '국내 금융비용 환경', False),
    ],
    'cash': [('yield', '접근 가능한 KRW 단기 금리 또는 명확한 benchmark', True)],
}

FOUR_ASSET_VERSION = 'four_asset_minimum_v2'
FOUR_STANDARDS = {
    **STANDARDS,
    'gas': [*STANDARDS['gas'], ('seasonal', '같은 계절 과거 재고 비교', False), ('lng', '실제 LNG 수출/수요', False)],
    'broad_commodity': [
        ('market', '대표 광범위 상품 가격', True),
        ('composition', '하위 그룹 구성과 비중', False),
        ('change', '대표 상품의 정의가 명확한 흐름', False),
        ('physical', '복수 하위 그룹의 실제 수급 단서', True),
    ],
}

LABELS = {
    'sufficient_for_scan': 'Scan 최소 자료 충족',
    'partial_but_usable': '일부 자료로 검토 가능',
    'insufficient': 'Scan 핵심 자료 부족',
}


def profile(asset):
    if asset in ('BTC', 'ETH'):
        return 'crypto'
    if asset == 'GOLD':
        return 'gold'
    if asset == 'ENERGY':
        return 'oil'
    if asset == 'NATGAS':
        return 'gas'
    if asset == 'BROAD_COMMODITIES':
        return 'broad_commodity'
    if asset == REGIONAL:
        return 'real_estate'
    if asset == 'CASH':
        return 'cash'
    if asset in ('KR_GOVERNMENT_3Y', 'SHORT_BOND', 'LONG_BOND'):
        return 'bond'
    return 'equity'


def macro_evidence(macro, case, cutoff):
    """Expose two already validated macro points for descriptive Scan changes."""
    if macro is None:
        return ()
    templates = {e.provenance.definition['measure']: e for e in case.evidence if e.view == 'macro' and e.provenance}
    known = {e.id for e in case.evidence}
    out = []
    for selection in macro.snapshot.selections:
        sid = selection.definition.canonical_id
        t = templates.get(sid)
        if t is None:
            continue
        eligible = [
            o
            for o in selection.observations
            if o.value is not None
            and o.retrieved_at <= cutoff
            and o.observation_date <= cutoff.date()
            and (cutoff.date() - o.observation_date).days <= selection.definition.max_age_days
        ]
        # The macro selector already enforces known-at/revision/release rules.
        for o in sorted(eligible, key=lambda o: o.observation_date)[-2:]:
            if o.id not in known:
                out.append(
                    replace(
                        t,
                        id=o.id,
                        text=f'{selection.definition.name}; observation={o.observation_date}; value={o.value} {selection.definition.unit}',
                        locator=o.locator,
                        observed_at=o.observation_date,
                        analyzed_at=o.retrieved_at.date(),
                        value=o.value,
                        provenance=replace(t.provenance, snapshot_id=o.snapshot_id, excerpt_id=o.id),
                    )
                )
                known.add(o.id)
    return tuple(out)


def source_identity(source, measure):
    parts = urlsplit(source.location)
    path = parts.path
    query = parse_qsl(parts.query, keep_blank_values=True)
    if parts.hostname == 'api.exchange.coinbase.com' and path.endswith('/candles'):
        query = [(k, v) for k, v in query if k not in ('start', 'end')]
    elif parts.hostname == 'www.reb.or.kr' and path.endswith('/SttsApiTblData.do'):
        query = [(k, v) for k, v in query if k not in ('START_WRTTIME', 'END_WRTTIME')]
    elif parts.hostname == 'ecos.bok.or.kr' and '/StatisticSearch/' in path:
        # Only the requested window changes; table, language, frequency, field
        # and official definition remain part of the identity.
        path = re.sub(r'/(D|M)/\d{6,8}/\d{6,8}/', r'/\1/{window}/', path)
    return dict(
        publisher=source.provenance.publisher if source.provenance else source.name,
        source_type=source.type.value,
        url=urlunsplit((parts.scheme, parts.netloc, path, urlencode(sorted(query)), '')),
    )


def _point_date(e, strict=False):
    p = e.provenance.definition['period']
    if strict:
        from .source_pipeline import dated_evidence

        if not dated_evidence(e):
            return None
    if re.fullmatch(r'\d{4}-\d{2}', p):
        y, m = map(int, p.split('-'))
        return date(y, m, calendar.monthrange(y, m)[1]).isoformat()
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:T.*)?', p):
        return _time(p).isoformat()
    return str(e.observed_at) if e.observed_at else None


def _basis_period(period, measure):
    if re.fullmatch(r'\d{4}-\d{2}', period):
        return 'calendar_month'
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', period):
        return 'dated_observation'
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}T.*', period):
        return 'UTC_daily_close' if 'DAILY_' in measure else 'dated_instant'
    # Forecast target, FY/TTM windows and revision windows are NOT stripped.
    return period


def observations(run):
    from .scan import eligible

    sources = {s.id: s for s in run.case.sources}
    out = []
    fact_ids = {f['id'] for f in run.deep.facts} if run.deep else set()
    for e in eligible(run.case, run.cutoff):
        if e.value is None:
            continue
        if run.evidence_validation and 'ETF_DAILY_NET_FLOW' in e.provenance.definition['measure']:
            same = [
                x
                for x in run.case.evidence
                if x.provenance and x.provenance.definition['measure'] == e.provenance.definition['measure']
            ]
            if any(x.verification.value != 'supported_within_scope' for x in same):
                continue  # A corrupt row in the selected window requires independent validation.
        if run.input['scan']['method_version'] != 'evidence_shortlist_v3' and e.id in fact_ids:
            continue  # One typed financial fact, not two representations/votes.
        d = deepcopy(e.provenance.definition)
        s = sources[e.source_id]
        point = _point_date(e, bool(run.input.get('observation_dates_version')))
        if point is None or _time(point) > run.cutoff:
            continue
        # Never promote the provider's unfinished aggregate as a complete flow.
        if d['adjustment'] == 'partial_row_not_final_total':
            continue
        if d['adjustment'] == 'historical_reference_not_current_flow_when_latest_partial':
            continue
        for asset in e.asset_ids:
            if asset not in {m['id'] for m in run.input['methods']}:
                continue
            if e.view == 'macro':
                permitted = {
                    'CASH': {'KR_CD_91D'},
                    'KR_GOVERNMENT_3Y': {'KR_GOVERNMENT_NOMINAL_3Y'},
                    'SHORT_BOND': {'US_TREASURY_NOMINAL_2Y', 'US_CPI_U_HEADLINE_NSA'},
                    'LONG_BOND': {'US_TREASURY_NOMINAL_10Y', 'US_CPI_U_HEADLINE_NSA'},
                    REGIONAL: {'KR_HOUSEHOLD_NEW_LOAN_RATE'},
                }
                if d['measure'] not in permitted.get(asset, set()):
                    continue
            identity = source_identity(s, d['measure'])
            basis = {**d, 'period': _basis_period(d['period'], d['measure'])}
            out.append(
                dict(
                    asset_id=asset,
                    evidence_id=e.id,
                    source_id=e.source_id,
                    source_identity=identity,
                    definition=d,
                    comparison_definition=basis,
                    series_key=_digest([asset, identity, basis]),
                    observed_at=point,
                    value=str(e.value),
                    retrieved_at=s.provenance.retrieved_at,
                    snapshot_id=e.provenance.snapshot_id,
                    raw_sha256=s.provenance.raw_sha256,
                    payload_sha256=s.provenance.payload_sha256,
                    locator=e.locator,
                    verification='supported_within_scope',
                    interpretation='transcription_not_investment_judgment',
                )
            )
    # Facts are explicitly verified by the existing Deep Dive quote engine.
    if run.deep:
        current = {e.id for e in eligible(run.case, run.cutoff)}
        for f in run.deep.facts:
            if f['status'] != 'available' or f['source_evidence_id'] not in current:
                continue
            s = sources[next(e.source_id for e in run.case.evidence if e.id == f['source_evidence_id'])]
            d = dict(
                measure=f['id'],
                unit=f['unit'],
                period=f['window'],
                currency=f['currency'],
                scope=f['entity'],
                adjustment=f['basis'],
            )
            identity = source_identity(s, f['id'])
            basis = deepcopy(d)
            if run.input['scan']['method_version'] != 'evidence_shortlist_v3':
                basis['source_definition'] = f['source_definition']
            # This is the explicit rolling forward definition, not any FY1 PE.
            if f['basis'] == 'forward_12m_pe':
                basis['period'] = 'rolling_forward_12_months'
            out.append(
                dict(
                    asset_id='US_EQUITY',
                    evidence_id=f['source_evidence_id'],
                    fact_id=f['id'],
                    source_id=s.id,
                    source_identity=identity,
                    definition=d,
                    comparison_definition=basis,
                    series_key=_digest(['US_EQUITY', identity, basis]),
                    observed_at=f['observed_at'],
                    value=f['value'],
                    retrieved_at=s.provenance.retrieved_at,
                    snapshot_id=s.provenance.snapshot_id,
                    raw_sha256=s.provenance.raw_sha256,
                    payload_sha256=s.provenance.payload_sha256,
                    locator=f['quote_context'],
                    verification='supported_within_scope',
                    interpretation='transcription_not_investment_judgment',
                )
            )
    return sorted(out, key=lambda o: (o['asset_id'], o['series_key'], o['observed_at'], o['evidence_id']))


def _latest(points):
    return max(points, key=lambda p: (_time(p['observed_at']), p['evidence_id'])) if points else None


def _delta(a, b):
    av, bv = Decimal(a['value']), Decimal(b['value'])
    with localcontext() as ctx:
        ctx.prec = 50
        ctx.rounding = ROUND_HALF_EVEN
        delta = bv - av
        pct = (bv / av - 1) * 100 if av > 0 else None
    unit = b['definition']['unit']
    return dict(
        previous_value=str(av),
        current_value=str(bv),
        delta=str(delta),
        unit=unit,
        delta_unit='percentage_points' if unit in ('percent', 'percent_per_annum') else unit,
        percent_change=str(pct) if pct is not None else None,
        direction='up' if delta > 0 else 'down' if delta < 0 else 'flat',
        formula='current - previous; (current / previous - 1) * 100 only if previous > 0',
        method='decimal_same_definition_change_v1',
        previous_observed_at=a['observed_at'],
        current_observed_at=b['observed_at'],
        current_evidence_id=b['evidence_id'],
        previous_evidence_id=a['evidence_id'],
        series_key=b['series_key'],
        definition=b['comparison_definition'],
        source_identity=b['source_identity'],
    )


def within_changes(points):
    groups = defaultdict(list)
    for p in points:
        groups[p['series_key']].append(p)
    out = []
    for values in groups.values():
        ordered = sorted(values, key=lambda o: _time(o['observed_at']))
        if len(ordered) >= 2 and _time(ordered[0]['observed_at']) < _time(ordered[-1]['observed_at']):
            out.append(
                dict(
                    asset_id=ordered[-1]['asset_id'],
                    measure=ordered[-1]['definition']['measure'],
                    scope=ordered[-1]['definition']['scope'],
                    **_delta(ordered[0], ordered[-1]),
                )
            )
    return sorted(out, key=lambda p: (p['asset_id'], p['measure'], p['scope']))


def calculations(case, cutoff, require_dates=False):
    """Weekly exchange price change. Two actual endpoints, no invented bars."""
    from .scan import eligible

    out = []
    facts = eligible(case, cutoff)
    if require_dates:
        from .source_pipeline import dated_evidence

        facts = [e for e in facts if dated_evidence(e)]
    for asset in ('BTC', 'ETH'):
        es = [
            e
            for e in facts
            if e.provenance.definition['measure'] == 'COINBASE_' + asset + '_USD_DAILY_CLOSE' and e.value is not None
        ]
        es = sorted(es, key=lambda e: e.period)
        if len(es) != 2:
            continue
        a, b = es
        da, db = a.provenance.definition, b.provenance.definition
        if (
            all(da[k] == db[k] for k in ('measure', 'unit', 'currency', 'scope', 'adjustment'))
            and b.currency == 'USD'
            and db['adjustment'] == 'unadjusted_completed_candle'
            and _time(b.period) - _time(a.period) == timedelta(days=7)
            and a.value > 0
        ):
            with localcontext() as ctx:
                ctx.prec = 50
                ctx.rounding = ROUND_HALF_EVEN
                v = (b.value / a.value - 1) * 100
            out.append(
                MetricResult(
                    'SCAN_' + asset + '_WEEK_PRICE_CHANGE',
                    asset + ' 완료 일봉 일곱 날 가격 변화',
                    v,
                    'percent',
                    'same_venue_seven_calendar_day_close_change_v1',
                    (a.id, b.id),
                    (asset,),
                    ('한 거래소·동일 USD 시장·완료 일봉. 배당/비용/환율을 포함한 총수익률이나 미래수익은 아니다.',),
                )
            )
    # Actual monthly volume -> daily rate. Different month lengths must not
    # masquerade as growth in production or exports. No forecast substitution.
    for measure, label in [('EIA_US_DRY_GAS_PRODUCTION', 'PRODUCTION'), ('EIA_US_LNG_EXPORTS', 'LNG_EXPORTS')]:
        es = sorted(
            [e for e in facts if e.value is not None and e.provenance.definition['measure'] == measure],
            key=lambda e: e.period,
        )
        if not es:
            continue
        rates = {}
        for e in es:
            if (
                e.unit != 'MMcf'
                or e.value < 0
                or not re.fullmatch(r'\d{4}-\d{2}', e.period)
                or e.provenance.definition['adjustment']
                != 'reported_monthly_actual_volume_not_forecast_not_daily_feedgas'
            ):
                raise SourceError('monthly actual gas calculation definition mismatch')
            y, m = map(int, e.period.split('-'))
            days = calendar.monthrange(y, m)[1]
            with localcontext() as ctx:
                ctx.prec = 50
                ctx.rounding = ROUND_HALF_EVEN
                rates[e.period] = e.value / Decimal(1000 * days)
            out.append(
                MetricResult(
                    'SCAN_GAS_' + label + '_DAILY_' + e.period.replace('-', ''),
                    e.period + ' 실제 보고 월간량의 일평균',
                    rates[e.period],
                    'Bcf_per_day',
                    'actual_monthly_MMcf_divide_1000_calendar_days_v1',
                    (e.id,),
                    ('NATGAS',),
                    ('미국 전체의 시차 있는 월간 실제 보고량. 현재 주간 Lower 48 생산 또는 LNG feedgas가 아니다.',),
                )
            )
        b = es[-1]
        y, m = map(int, b.period.split('-'))
        previous = (date(y, m, 1) - timedelta(days=1)).strftime('%Y-%m')
        for suffix, period in [('MOM', previous), ('YOY', f'{y-1:04d}-{m:02d}')]:
            a = next((e for e in es if e.period == period), None)
            if a and rates[a.period] > 0:
                with localcontext() as ctx:
                    ctx.prec = 50
                    ctx.rounding = ROUND_HALF_EVEN
                    value = (rates[b.period] / rates[a.period] - 1) * 100
                out.append(
                    MetricResult(
                        'SCAN_GAS_' + label + '_DAILY_' + suffix,
                        '실제 월간 일평균의 ' + suffix + ' 변화',
                        value,
                        'percent',
                        'same_actual_monthly_daily_rate_change_v1',
                        (a.id, b.id),
                        ('NATGAS',),
                        (a.period + ' → ' + b.period + '; 정확한 월과 달력 일수를 맞춘 비교. 현시점 예측 아님.',),
                    )
                )
    refs = [
        e
        for e in facts
        if e.value is not None and e.provenance.definition['measure'].startswith('EIA_GAS_ISO_WEEK_REFERENCE_')
    ]
    stocks = sorted(
        [e for e in facts if e.value is not None and e.provenance.definition['measure'] == 'EIA_US_WORKING_GAS_STOCK'],
        key=lambda e: e.period,
    )
    if refs and stocks:
        current = stocks[-1]
        day = date.fromisoformat(current.period)
        week = day.isocalendar().week
        required = {day.year - i for i in range(1, 6)}
        if (
            len(refs) == 5
            and {date.fromisoformat(e.period).year for e in refs} == required
            and all(
                e.unit == 'Bcf'
                and date.fromisoformat(e.period).isocalendar().week == week
                and e.provenance.definition['adjustment']
                == f'reported_historical_stock_ISO_week_{week}_reference_for_{day}'
                for e in refs
            )
        ):
            with localcontext() as ctx:
                ctx.prec = 50
                ctx.rounding = ROUND_HALF_EVEN
                avg = sum(e.value for e in refs) / 5
                premium = (current.value / avg - 1) * 100 if avg > 0 else None
            ids = tuple(e.id for e in refs)
            limits = (
                '자체 동일 ISO 주 금요일 오년 평균; EIA 공식 보간 평균/당시 vintage가 아니다. 평년 주입 속도는 별도.',
            )
            out.append(
                MetricResult(
                    'SCAN_GAS_SEASONAL_5Y_REFERENCE',
                    '동일 ISO 주 과거 오년 재고 평균',
                    avg,
                    'Bcf',
                    'five_same_ISO_week_friday_stock_mean_v1',
                    ids,
                    ('NATGAS',),
                    limits,
                )
            )
            if premium is not None:
                out.append(
                    MetricResult(
                        'SCAN_GAS_STOCK_VS_SEASONAL_REFERENCE',
                        '현재 재고의 자체 계절 기준 대비 차이',
                        premium,
                        'percent',
                        'actual_stock_vs_same_ISO_week_reference_v1',
                        (*ids, current.id),
                        ('NATGAS',),
                        limits,
                    )
                )
    flows = sorted(
        [
            e
            for e in facts
            if e.value is not None
            and e.provenance.definition['measure'] == 'US_SPOT_ETH_ETF_DAILY_NET_FLOW'
            and e.provenance.definition['adjustment'] == 'complete_row_provider_reported_not_issuer_confirmed'
        ],
        key=lambda e: e.period,
    )
    if len(flows) == 5 and len({e.period for e in flows}) == 5:
        start, end = date.fromisoformat(flows[0].period), date.fromisoformat(flows[-1].period)
        business_dates = [
            start + timedelta(days=i)
            for i in range((end - start).days + 1)
            if (start + timedelta(days=i)).weekday() < 5
        ]
        if (
            [date.fromisoformat(e.period) for e in flows] == business_dates
            and len(business_dates) == 5
            and all(e.unit == 'USD_million' for e in flows)
        ):
            with localcontext() as ctx:
                ctx.prec = 50
                ctx.rounding = ROUND_HALF_EVEN
                total = sum(e.value for e in flows)
            out.append(
                MetricResult(
                    'SCAN_ETH_FIVE_REPORTED_DAYS_NET_FLOW',
                    '최근 오 보고 거래일 ETH ETF 순유입 합계',
                    total,
                    'USD_million',
                    'five_complete_same_provider_ETH_flow_rows_sum_v1',
                    tuple(e.id for e in flows),
                    ('ETH',),
                    (
                        str(start)
                        + ' → '
                        + str(end)
                        + '; 누락 영업일/미완성 행이면 계산 보류. 제공자 전사이며 원발행사 확인 전이다.',
                        '일곱 날 거래소 가격과 다른 기간. 동시 수요 확인·지속적 기관 수요를 증명하지 않는다.',
                    ),
                )
            )
    return tuple(out)


def capture(previous, require_dates=False):
    from .scan import assess

    if not previous.input.get('scan'):
        raise SourceError('previous-scan must be a completed Opportunity Scan')
    a = assess(previous)
    data = dict(
        schema_version='scan-comparison-anchor-v1',
        method_version=HISTORY_VERSION,
        as_of=previous.cutoff.isoformat(),
        synthetic=previous.input['synthetic'],
        run_id=previous.result.run_id,
        request_sha256=_digest(previous.input),
        shortlist_sha256=_digest(a),
        scan_method=previous.input['scan']['method_version'],
        observations=observations(previous),
        rows=[{k: r[k] for k in ('asset_id', 'status', 'why_now', 'decision_rule')} for r in a['universe']],
        candidates=a['candidates'],
        community=dict(
            status='not_comparable', reason='목적 표본·고정 개수 발언은 관심 모집단의 언급량/증가율이 아니다.'
        ),
    )
    if require_dates:
        from .source_pipeline import observation_timing, OBSERVATION_DATES_VERSION

        evidence = {e.id: e for e in previous.case.evidence}
        kept = []
        excluded = []
        for point in data['observations']:
            timing = observation_timing(point['definition']['period'])
            e = evidence.get(point['evidence_id'])
            expected = timing['observed_at']
            if point.get('fact_id') and previous.deep:
                f = next(
                    (f for f in previous.deep.facts if f['id'] == point['fact_id'] and f['status'] == 'available'), None
                )
                expected = f['observed_at'] if f else None
            elif e is not None and e.view == 'macro':
                expected = str(e.observed_at) if e.observed_at else None
            matches = expected is not None and (
                _time(expected) == _time(point['observed_at'])
                if timing['precision'] == 'instant'
                else _time(expected).date() == _time(point['observed_at']).date()
            )
            if matches:
                kept.append(point)
            else:
                excluded.append(
                    dict(
                        series_key=point['series_key'],
                        asset_id=point['asset_id'],
                        evidence_id=point['evidence_id'],
                        measure=point['definition']['measure'],
                        period=point['definition']['period'],
                        recorded_observed_at=point['observed_at'],
                        row_calendar_at=expected,
                        reason='이전 날짜가 원문 행 기간과 불일치하거나 미확인: 과거 artifact를 보존하고 변화 계산에서 제외.',
                    )
                )
        data['observations'] = kept
        data['observation_dates_version'] = OBSERVATION_DATES_VERSION
        data['excluded_observation_dates'] = excluded
    data['incomplete_observations'] = []
    if previous.discovery:
        for c in previous.discovery['candidates']:
            if c['status'] != 'selected' or c.get('verified', {}).get('complete') is not False:
                continue
            for r in c['verified']['records']:
                data['incomplete_observations'].append(
                    dict(
                        definition=r['definition'],
                        source_id=c['source_id'],
                        raw_sha256=c['document']['raw_sha256'],
                        reason='해당 이전 판본은 미완성 합계; 완성된 과거 수치로 사용 불가',
                    )
                )
    data['anchor_sha256'] = _digest(data)
    return data


def validate_anchor(anchor, cutoff, synthetic):
    if (
        not isinstance(anchor, dict)
        or anchor.get('schema_version') != 'scan-comparison-anchor-v1'
        or anchor.get('method_version') != HISTORY_VERSION
    ):
        raise SourceError('unsupported previous Scan anchor')
    content = {k: v for k, v in anchor.items() if k != 'anchor_sha256'}
    if _digest(content) != anchor.get('anchor_sha256'):
        raise SourceError('previous Scan anchor checksum differs')
    if _time(anchor['as_of']) >= cutoff:
        raise SourceError('previous Scan must precede current research cutoff')
    if anchor['synthetic'] != synthetic:
        raise SourceError('synthetic/live Scans cannot be compared as actual market observations')
    for p in anchor['observations']:
        if _time(p['observed_at']) > _time(anchor['as_of']) or _time(p['retrieved_at']) > _time(anchor['as_of']):
            raise SourceError('future point in previous Scan anchor')
        if p['series_key'] != _digest([p['asset_id'], p['source_identity'], p['comparison_definition']]):
            raise SourceError('previous observation definition fingerprint differs')
        if not Decimal(p['value']).is_finite():
            raise SourceError('invalid previous Scan numeric observation')


def compare(points, anchor, cutoff, synthetic):
    if anchor is None:
        return dict(
            status='baseline',
            observations=[],
            newly_observable=[p['series_key'] for p in points],
            unavailable=[],
            mismatches=[],
            community=dict(
                status='not_comparable', reason='비교 가능한 이전 관심 표본 없음. 관심 증가를 주장하지 않는다.'
            ),
        )
    validate_anchor(anchor, cutoff, synthetic)
    past = defaultdict(list)
    current = defaultdict(list)
    for p in anchor['observations']:
        past[p['series_key']].append(p)
    for p in points:
        current[p['series_key']].append(p)
    result = []
    mismatches = []
    new = []
    for key, values in sorted(current.items()):
        b = _latest(values)
        if key not in past:
            finalized = any(
                p['definition']['measure'] == b['definition']['measure']
                and p['definition']['period'] == b['definition']['period']
                and p['definition']['scope'] == b['definition']['scope']
                for p in anchor.get('incomplete_observations', [])
            )
            invalid_past = any(p['series_key'] == key for p in anchor.get('excluded_observation_dates', []))
            new.append(
                dict(
                    asset_id=b['asset_id'],
                    measure=b['definition']['measure'],
                    scope=b['definition']['scope'],
                    current_evidence_id=b['evidence_id'],
                    reason=(
                        '같은 최신 행이 미완성에서 완료 판본으로 확정됨. 이전 완료값이 없어 순유입 증가/감소 비교는 보류.'
                        if finalized
                        else (
                            '이전 관측일이 원문 기간과 맞지 않아 변화 계산에서 제외했다. 이번 날짜 확인은 시장 개선·후퇴가 아니다.'
                            if invalid_past
                            else '새로 관측 가능해진 자료; 이전 시장 개선의 증거가 아니다.'
                        )
                    ),
                )
            )
            related = [
                p
                for p in anchor['observations']
                if p['asset_id'] == b['asset_id']
                and p['definition']['measure'] == b['definition']['measure']
                and p['definition']['scope'] == b['definition']['scope']
            ]
            if related:
                mismatches.append(
                    dict(
                        asset_id=b['asset_id'],
                        measure=b['definition']['measure'],
                        current_evidence_id=b['evidence_id'],
                        reason='source/definition/unit/currency/basis가 달라 시계열 연결 보류',
                        previous_keys=sorted({p['series_key'] for p in related}),
                    )
                )
            continue
        a = _latest(past[key])
        delta = _delta(a, b)
        at, bt = _time(a['observed_at']), _time(b['observed_at'])
        status = (
            'new_observation'
            if bt > at
            else (
                'same_observation'
                if bt == at and Decimal(a['value']) == Decimal(b['value'])
                else 'revised_vintage' if bt == at else 'regressed_observation'
            )
        )
        # Same-date revision is data revision, not intervening market movement.
        result.append(
            dict(
                asset_id=b['asset_id'],
                measure=b['definition']['measure'],
                scope=b['definition']['scope'],
                status=status,
                previous_run_id=anchor['run_id'],
                previous_ref=anchor['run_id'] + '/' + a['evidence_id'],
                **delta,
            )
        )
    unavailable = [
        dict(
            asset_id=_latest(past[k])['asset_id'],
            measure=_latest(past[k])['definition']['measure'],
            reason='이전 정의의 현재 관측 미확보; 투자 매력이 하락했다는 뜻이 아니다.',
        )
        for k in sorted(past.keys() - current.keys())
    ]
    return dict(
        status='compared',
        previous_run_id=anchor['run_id'],
        previous_as_of=anchor['as_of'],
        observations=result,
        newly_observable=new,
        unavailable=unavailable,
        mismatches=mismatches,
        community=deepcopy(anchor['community']),
        **(
            {'excluded_previous_observation_dates': deepcopy(anchor['excluded_observation_dates'])}
            if 'excluded_observation_dates' in anchor
            else {}
        ),
    )


def combinations(changes, *, enhanced=False):
    """Only comparable overlapping periods; directions are hypotheses, not alpha."""
    out = []
    for asset in sorted({c['asset_id'] for c in changes}):
        cs = [c for c in changes if c['asset_id'] == asset and c.get('status', 'new_observation') == 'new_observation']
        price = [
            c
            for c in cs
            if c['measure'].endswith('DAILY_CLOSE')
            or c['measure'] in ('EIA_WTI_SPOT', 'EIA_HENRY_HUB_SPOT', 'LBMA_GOLD_PM_ISSUER_REPORTED')
        ]
        fundamentals = [
            c
            for c in cs
            if 'EPS' in c['measure']
            or c['measure'].endswith('OPERATING_PROFIT')
            or 'NET_FLOW' in c['measure']
            or enhanced
            and c['measure'] == 'US_TIPS_10Y_CURRENT'
        ]
        for p in price:
            for f in fundamentals:
                # Different lag/windows cannot establish that one led the other.
                if (p['previous_observed_at'][:10], p['current_observed_at'][:10]) != (
                    f['previous_observed_at'][:10],
                    f['current_observed_at'][:10],
                ):
                    continue
                if enhanced and f['measure'] == 'US_TIPS_10Y_CURRENT':
                    if f['direction'] != 'down':
                        continue
                    text = '금 가격과 함께 비교한 실질금리가 하락했다. 이자 없는 금의 기회비용이 줄어드는 조건부 가설; 직접 수요·이미 반영된 가격 확인 필요.'
                elif p['direction'] == 'up' and f['direction'] == 'up':
                    text = '가격 상승과 경제 신호 개선이 함께 관측됐다. 실제 재평가인지 이미 반영됐는지 확인할 조건부 가설.'
                elif p['direction'] == 'flat' and f['direction'] == 'up':
                    text = '가격이 그대로인데 경제 신호는 개선됐다. 아직 덜 반영됐을 가능성을 조사하되 저평가로 확정하지 않는다.'
                elif p['direction'] == 'down' and f['direction'] == 'up':
                    text = '가격 하락과 경제 신호 개선이 공존한다. 반대 의견을 검토하는 조건부 연구 후보이며 미래 수익 보장이 아니다.'
                elif p['direction'] == 'up' and f['direction'] == 'down':
                    text = '가격 상승과 경제 신호 악화가 공존한다. 기대와 실제 자료의 괴리 위험을 점검한다.'
                elif p['direction'] == 'up' and f['direction'] == 'flat':
                    text = '가격 상승을 경제 신호 개선으로 설명하지 못했다. 기대가 먼저 움직였을 가능성; 과열 확정은 아니다.'
                else:
                    continue
                out.append(
                    dict(
                        asset_id=asset,
                        text=text,
                        role='conditional_hypothesis',
                        evidence_ids=[p['current_evidence_id'], f['current_evidence_id']],
                        previous_refs=[
                            p.get('previous_ref', p['previous_evidence_id']),
                            f.get('previous_ref', f['previous_evidence_id']),
                        ],
                        source_changes=[p['series_key'], f['series_key']],
                        return_guarantee=False,
                    )
                )
    return out


def coverage(run, row, points, changes, *, enhanced=False):
    from .scan import eligible

    asset = row['asset_id']
    kind = profile(asset)
    ps = [p for p in points if p['asset_id'] == asset]
    four = run.input['scan']['method_version'] == 'evidence_shortlist_v7'
    facts = [e for e in eligible(run.case, run.cutoff) if asset in e.asset_ids]
    slots = defaultdict(list)
    notes = {}

    def add(slot, items):
        slots[slot].extend(p['evidence_id'] for p in items)

    def measure(pattern):
        return [p for p in ps if re.search(pattern, p['definition']['measure'])]

    cs = [c for c in changes if c['asset_id'] == asset]
    if kind == 'equity':
        add('market', measure(r'PE$|_PE$|PRICE'))
        add('earnings', measure(r'EPS|EARNINGS|GROWTH'))
        add('change', measure(r'REVISION'))
        if kind and any('PE' in c['measure'] for c in cs):
            add('change', [p for p in ps if 'PE' in p['definition']['measure']])
        # Business evidence is scoped to this company/sector; no index proxy.
        business = [
            e.id
            for e in facts
            if (not enhanced or asset == 'KR_EQUITY')
            and ('industry-wide upward trend of prices' in e.text or 'elevated component cost pressures' in e.text)
        ]
        slots['earnings'].extend(business)
        slots['catalyst'].extend(row['evidence_ids'])
        if business:
            slots['change'].extend(business)
            notes['change'] = '회사 설명의 실적 변화. 같은 기준 가격 변화는 미확보.'
        if not slots['catalyst'] and slots['earnings']:
            slots['catalyst'].extend(slots['earnings'])
            notes['catalyst'] = '실적/전망의 조사 계기와 방법에 명시된 downside. 반대 가설의 독립 실증은 별도 확인.'
    elif kind == 'bond':
        add(
            'yield',
            measure(
                'KR_GOVERNMENT_NOMINAL_3Y'
                if asset == 'KR_GOVERNMENT_3Y'
                else 'US_TREASURY_NOMINAL_2Y' if asset == 'SHORT_BOND' else 'US_TREASURY_NOMINAL_10Y'
            ),
        )
        slots['change'].extend(
            c['current_evidence_id']
            for c in cs
            if c['measure'].endswith('3Y' if asset == 'KR_GOVERNMENT_3Y' else '2Y' if asset == 'SHORT_BOND' else '10Y')
        )
        if asset != 'KR_GOVERNMENT_3Y':
            add('policy', measure(r'US_CPI'))
        else:
            notes['policy'] = '미국 CPI로 한국 물가/통화정책을 대체하지 않는다.'
    elif kind == 'crypto':
        add('market', measure('COINBASE_' + asset + '_USD_(DAILY_CLOSE|LAST_TRADE)'))
        slots['change'].extend(
            c['current_evidence_id']
            for c in cs
            if c['measure'] == 'COINBASE_' + asset + '_USD_DAILY_CLOSE'
            and _time(c['current_observed_at']) - _time(c['previous_observed_at']) >= timedelta(days=7)
        )
        add('flow', measure('US_SPOT_' + asset + '_ETF_DAILY_NET_FLOW'))
        add('liquidity', measure(r'DAILY_BASE_VOLUME|24H_BASE_VOLUME|DERIBIT_.*OPEN_INTEREST|FUNDING'))
        slots['catalyst'].extend(e.id for e in facts if e.value is None and e.view != 'macro')
        notes['liquidity'] = '한 거래소 하루 거래량은 전체 시장 유동성/레버리지와 다르다.'
        notes['flow'] = '미완성 ETF 합계·전체 crypto flow·AUM으로 해당 자산 확정 순유입을 채우지 않는다.'
        if run.evidence_validation and any(
            r['definition']['measure'] == 'US_SPOT_' + asset + '_ETF_DAILY_NET_FLOW'
            and r['status'] not in ('accepted', 'cross_checked')
            for r in run.evidence_validation['records']
        ):
            slots['flow'] = []
            notes['flow'] += ' 이상/충돌 자료 격리로 현재 flow slot은 미충족; 독립 원자료 확인 전 해제하지 않는다.'
    elif kind == 'gold':
        add('market', measure('LBMA_GOLD_PM_ISSUER_REPORTED'))
        add('change', measure('LBMA_GOLD_PM_ISSUER_MONTH_RETURN'))
        add('real_rate', measure('US_TIPS_10Y_CURRENT'))
        add('demand', measure(r'GOLD.*(HELD|DEMAND|FLOW)'))
        notes['demand'] = 'AUM 증가/가격 상승을 실물 수요나 순유입으로 바꾸지 않는다.'
    elif kind in ('oil', 'gas'):
        add('market', measure('EIA_WTI_SPOT' if kind == 'oil' else 'EIA_HENRY_HUB_SPOT'))
        add('physical', measure('EIA_US_COMMERCIAL_CRUDE_STOCK' if kind == 'oil' else 'EIA_US_WORKING_GAS_STOCK'))
        if kind == 'oil':
            slots['structure'].extend(
                c['current_evidence_id'] for c in cs if c['measure'] == 'EIA_US_COMMERCIAL_CRUDE_STOCK'
            )
        else:
            prod = [
                e.id
                for e in facts
                if 'production continues to grow' in e.text
                or e.provenance.definition['measure']
                == 'EIA_US_natural_gas_production_consumption_LNG_exports_forecast'
            ]
            notes['production'] = (
                '공식 생산 전망은 있다. 실제 최신 생산 관측을 대체하지 않는다.'
                if prod
                else '실제 생산 및 전망 연결 미확보.'
            )
            notes['demand'] = '날씨·현재 수요와 계절별 재고 비교 미확보. 선물곡선은 추가 확인 항목.'
            if four:
                add('production', measure('EIA_US_DRY_GAS_PRODUCTION'))
                slots['demand'].extend(
                    e.id for e in facts if e.provenance.definition['measure'].startswith('NOAA_CPC_')
                )
                metrics = {m.id: m for m in run.result.metrics}
                if 'SCAN_GAS_SEASONAL_5Y_REFERENCE' in metrics:
                    slots['seasonal'].extend(metrics['SCAN_GAS_SEASONAL_5Y_REFERENCE'].input_ids)
                add('lng', measure('EIA_US_LNG_EXPORTS'))
                notes.update(
                    production='공식 월간 실제량, 일수 보정 비교. 현재 주간 생산은 아니다.',
                    demand='6~10/8~14일 기온 전망. 실제 기온·HDD/CDD와 총 수요는 미확보.',
                    seasonal='자체 동일 ISO 주 오년 비교; EIA 공식 보간 평균·평년 주입 속도 아님.',
                    lng='월간 실제 수출. 현재 일별 LNG feedgas로 대체하지 않는다.',
                )
    elif kind == 'broad_commodity' and four:
        add('market', measure('ISHARES_GSG_NAV'))
        add('change', measure('ISHARES_GSG_YTD_NAV_TOTAL_RETURN'))
        # Independent subgroup clues, retaining their own scope. Crude alone
        # cannot stand in for a broad commodity basket.
        energy = [
            p
            for p in points
            if p['asset_id'] == 'ENERGY' and p['definition']['measure'] == 'EIA_US_COMMERCIAL_CRUDE_STOCK'
        ]
        gold = [p for p in points if p['asset_id'] == 'GOLD' and p['definition']['measure'] == 'IAU_GOLD_PHYSICAL_HELD']
        if energy and gold:
            add('physical', energy + gold)
        notes.update(
            composition='에너지·금속·농산물·축산 포함은 발행사 확인. 현재 네 그룹 비중은 미확인.',
            physical='미국 원유 재고와 한 금 신탁 실물 보유량의 두 단서. 산업금속/농산물 수급·전체 원자재 동반 강세는 미확인.',
            change='현재 NAV와 별도 기준일 YTD NAV 총수익. 현물가격 수익/지수 level과 구분한다.',
        )
    elif kind == 'real_estate':
        regions = {r: {'market': [], 'volume': [], 'rent': []} for r in ('서울', '경기', '인천')}
        for region in regions:
            scoped = [p for p in ps if p['definition']['scope'].startswith(region + ' apartments;')]
            for slot, measure_id in [
                ('market', 'KR_APARTMENT_SURVEY_SALE_INDEX'),
                ('volume', 'KR_APARTMENT_REPORTED_SALE_COUNT'),
                ('rent', 'KR_APARTMENT_SURVEY_JEONSE_INDEX'),
            ]:
                refs = [p['evidence_id'] for p in scoped if p['definition']['measure'] == measure_id]
                if enhanced and slot in ('market', 'rent'):
                    changing = any(
                        c['asset_id'] == asset
                        and c['measure'] == measure_id
                        and c['scope'].startswith(region + ' apartments;')
                        for c in changes
                    )
                    if not changing:
                        refs = []
                regions[region][slot] = list(dict.fromkeys(refs))
        for slot in ('market', 'volume', 'rent'):
            if all(regions[r][slot] for r in regions):
                slots[slot].extend(ref for r in regions for ref in regions[r][slot])
            else:
                notes[slot] = (
                    '미확보 지역: '
                    + ', '.join(r for r in regions if not regions[r][slot])
                    + '. 다른 지역으로 대체하지 않는다.'
                )
        add('financing', measure('KR_HOUSEHOLD_NEW_LOAN_RATE'))
        notes['financing'] = '한국 전체 신규 가계대출 평균, 개인 주담대/지역 실행금리 아님.'
    elif kind == 'cash':
        add('yield', measure('KR_CD_91D'))
        notes['yield'] = 'CD 91일 benchmark, 개인 예금 계약금리·보장·세후 수익 아님.'
    rows = []
    for slot, label, critical in (FOUR_STANDARDS if four else STANDARDS)[kind]:
        ids = list(dict.fromkeys(slots[slot]))
        rows.append(
            dict(
                category=slot,
                label=label,
                critical=critical,
                status='available' if ids else 'missing',
                evidence_ids=ids,
                impact=(
                    '현재 가격의 투자 우위는 판단 유보'
                    if critical and not ids
                    else '반대 가설·지속성 확인 제한' if not ids else '한정된 정의에서 비교 가능'
                ),
                note=notes.get(slot, ''),
            )
        )
    available = {s['category'] for s in rows if s['evidence_ids']}
    core = {s['category'] for s in rows if s['critical']}
    sufficient = all(s['evidence_ids'] for s in rows)
    usable = bool(available & core) and len(available) >= 2
    # Price is not a prerequisite for an explicitly conditional business
    # question, but no price attractiveness judgment may follow.
    if kind == 'equity' and 'earnings' in available and 'change' in available:
        usable = True
    status = 'sufficient_for_scan' if sufficient else 'partial_but_usable' if usable else 'insufficient'
    result = dict(
        method_version=FOUR_ASSET_VERSION if four else VERSION,
        status=status,
        label=LABELS[status],
        purpose='scan_evaluability_not_investment_attractiveness',
        standard=kind,
        slots=rows,
        missing_categories=[s['category'] for s in rows if not s['evidence_ids']],
        critical_gaps=[s['category'] for s in rows if s['critical'] and not s['evidence_ids']],
        supplementary_gaps=['실제 투자상품 비용·사용자 자금 제약·반대 가설 검증은 Scan 완료와 별개다.'],
    )
    if kind == 'real_estate':
        result['regions'] = regions
    return result


def assess(run, base):
    """Choose meaningful economic questions; neither document counts nor coverage rank."""
    from .scan import eligible

    points = observations(run)
    changes = within_changes(points)
    enhanced = run.input['scan']['method_version'] in (
        'evidence_shortlist_v4',
        'evidence_shortlist_v5',
        'evidence_shortlist_v6',
        'evidence_shortlist_v7',
    )
    current_version = run.input['scan']['method_version'] in (
        'evidence_shortlist_v5',
        'evidence_shortlist_v6',
        'evidence_shortlist_v7',
    )
    four = run.input['scan']['method_version'] == 'evidence_shortlist_v7'
    past = run.input.get('previous_scan')
    history = compare(points, past, run.cutoff, run.input['synthetic'])
    factual = {e.id: e for e in eligible(run.case, run.cutoff)}
    index = {r['asset_id']: r for r in base['universe']}

    def latest(asset, measure):
        return _latest([p for p in points if p['asset_id'] == asset and p['definition']['measure'] == measure])

    def selected_refs(asset):
        return list(dict.fromkeys(p['evidence_id'] for p in points if p['asset_id'] == asset))

    def change(asset, measure):
        return next((c for c in changes if c['asset_id'] == asset and c['measure'] == measure), None)

    for r in base['universe']:
        r.pop('reference_number', None)
        r['selected'] = False
        r['candidate_eligible'] = False
        r['coverage'] = coverage(run, r, points, changes, enhanced=enhanced)
        r['coverage_status'] = r['coverage']['status']
        resolved_limits = {
            'GOLD': ['직접 금 수요·보유 상품 비용·환율과 현재 가격의 연결'],
            'ENERGY': ['선물 만기별 가격·실제 상품 구조·실제 수요의 추가 관측'],
            'NATGAS': ['실제 생산·날씨·평년 대비 재고·선물곡선·실제 상품 비용'],
            'ETH': ['ETH 고유 기관 흐름·네트워크 수요·가치 대용 지표·프로토콜 위험'],
            'BTC': ['확정 기관 흐름·전 시장 레버리지·독립 수요·가치 대용 지표'],
            'CASH': ['개인 원화 상품의 실제 계약금리·세후수익·보호·자금 접근 조건'],
            REGIONAL: ['지역/단지/면적별 실제 매수가·공급·실제 주담대·사용자 자금 제약'],
        }
        if r['asset_id'] in resolved_limits:
            r['unknowns'] = resolved_limits[r['asset_id']]
        if current_version and r['asset_id'] == 'BTC':
            r['unknowns'] = ['기관 수요의 지속성·원발행사 교차 확인·전 시장 레버리지·독립 수요·가치 대용 지표']
        r['investment_assessment'] = (
            'not_assessed_due_to_gap' if r['coverage_status'] == 'insufficient' else 'no_distinct_opportunity_signal'
        )
        # Existing cases require independent economic inputs, not more quotes.
        if r['decision_rule'] in (
            'positive_revision_with_comparable_valuation',
            'observed_business_improvement_and_counterevidence',
            'lower_same_definition_value_PE_with_distribution_context',
        ):
            r['candidate_eligible'] = True
            r['investment_assessment'] = 'conditional_research_case'
        if r['asset_id'] in ('KR_GOVERNMENT_3Y', 'SHORT_BOND', 'LONG_BOND'):
            r.update(
                status='neutral',
                investment_assessment='comparison_anchor',
                candidate_eligible=False,
                why_now='현재 시작 금리와 만기는 다른 투자에서 포기할 이자의 비교 기준이다. 양의 금리나 자료의 양만으로 기회 후보를 만들지 않는다.',
                decision_rule='starting_yield_anchor_not_automatic_opportunity',
            )
        if r['asset_id'] == 'CASH':
            p = latest('CASH', 'KR_CD_91D')
            if p:
                r.update(
                    evidence_ids=[p['evidence_id']],
                    price_context='한국은행 CD 91일 시장금리 benchmark를 확인했다. 개인 예금/MMF 실제 계약·세금·보호는 별도다.',
                )
            r['investment_assessment'] = 'liquidity_alternative'
        if r['asset_id'] in ('BTC', 'ETH'):
            asset = r['asset_id']
            price = latest(asset, 'COINBASE_' + asset + '_USD_DAILY_CLOSE')
            flow = latest(asset, 'US_SPOT_' + asset + '_ETF_DAILY_NET_FLOW')
            if price:
                r.update(
                    status='conditional_watch',
                    evidence_ids=selected_refs(asset),
                    decision_rule='price_trend_liquidity_with_explicit_flow_gap',
                    why_now='같은 거래소 가격 흐름과 실제 하루 거래량을 확인했다. 현재 가격만으로 저평가를 판단할 수 없고 확정 기관 수요/레버리지 근거가 제한된다.',
                    price_context='Coinbase USD 시장 완료 일봉 종가; 실시간 가격·전 시장 대표 가격 아님.',
                    momentum='일곱 날의 완료 일봉 가격 변화. 상승/하락 자체를 선정 조건으로 사용하지 않는다.',
                    confidence='한정된 가격/유동성 확인; 경제적 투자 해석은 조건부 초안',
                )
                if flow and Decimal(flow['value']) > 0:
                    r.update(
                        candidate_eligible=True,
                        investment_assessment='conditional_research_case',
                        why_now='같은 자산의 확정 ETF 순유입과 가격 흐름이 함께 확인됐다. 자금 유입이 지속되고 현재 가격에 덜 반영됐는지 조사할 조건부 후보.',
                        decision_rule='complete_asset_flow_and_price_not_price_direction',
                    )
                elif current_version and flow:
                    r.update(
                        investment_assessment='mixed_signals',
                        why_now=(
                            '최신 완료 ETF 하루 집계는 순유출이다. 일곱 날 가격 흐름과 조사 기간이 달라 장기 수요 약화로 일반화하지 않고 수요 지속성을 관찰한다.'
                            if Decimal(flow['value']) < 0
                            else '최신 완료 ETF 하루 집계는 순유입이 없다. 가격 흐름 자체로 기관 수요나 투자 우위를 확정하지 않는다.'
                        ),
                        decision_rule='complete_nonpositive_daily_flow_not_missing_data_not_long_term_verdict',
                    )
            else:
                r['candidate_eligible'] = False
        if r['asset_id'] == 'GOLD' and latest('GOLD', 'LBMA_GOLD_PM_ISSUER_REPORTED'):
            r.update(
                status='conditional_watch',
                evidence_ids=selected_refs('GOLD'),
                investment_assessment='mixed_signals',
                why_now='현재 금 기준가격·월말 가격 흐름·실질금리를 확인했다. 직접 수요 변화와 현재 가격의 투자 우위를 확정할 자료는 부족하다.',
                decision_rule='gold_price_real_rate_context_without_demand_confirmation',
                confidence='원문 전사 확인; 수요 및 투자 해석은 조건부 초안',
            )
        if r['asset_id'] in ('ENERGY', 'NATGAS'):
            asset = r['asset_id']
            measure = 'EIA_US_COMMERCIAL_CRUDE_STOCK' if asset == 'ENERGY' else 'EIA_US_WORKING_GAS_STOCK'
            price = latest(asset, 'EIA_WTI_SPOT' if asset == 'ENERGY' else 'EIA_HENRY_HUB_SPOT')
            stock = change(asset, measure)
            if price and stock:
                r.update(
                    evidence_ids=list(dict.fromkeys(r['evidence_ids'] + selected_refs(asset))),
                    status='conditional_watch',
                    investment_assessment='mixed_signals',
                    why_now='실제 미국 현물가격과 주간 재고를 확인했다. 재고 변화의 계절성·생산/수요·선물 만기별 가격을 확인해야 현재 상품의 투자 매력을 판단할 수 있다.',
                    decision_rule='actual_spot_and_stock_separate_from_supply_forecast',
                    confidence='실제 가격·재고 확인; 해석은 조건부 초안',
                )
                if asset == 'ENERGY' and stock['direction'] == 'down':
                    r.update(
                        candidate_eligible=True,
                        investment_assessment='conditional_research_case',
                        why_now='실제 원유 재고가 감소했다. 공급 차질과 실제 가격을 함께 조사할 조건부 후보이며 계절성·수요·이미 반영된 가격을 재검증한다.',
                        decision_rule='physical_stock_tightening_with_observed_price',
                    )
                if asset == 'NATGAS':
                    r['unknowns'] = list(
                        dict.fromkeys(
                            r['unknowns'] + ['계절별 평년 재고·실제 생산·날씨·선물곡선; 전망은 실제 미래 관측이 아님']
                        )
                    )
        if r['asset_id'] == REGIONAL:
            region_cases = []
            for region in ('서울', '경기', '인천'):
                cs = [
                    c for c in changes if c['asset_id'] == REGIONAL and c['scope'].startswith(region + ' apartments;')
                ]
                sale = next((c for c in cs if c['measure'] == 'KR_APARTMENT_SURVEY_SALE_INDEX'), None)
                volume = next((c for c in cs if c['measure'] == 'KR_APARTMENT_REPORTED_SALE_COUNT'), None)
                rent = next((c for c in cs if c['measure'] == 'KR_APARTMENT_SURVEY_JEONSE_INDEX'), None)
                if (
                    sale
                    and volume
                    and rent
                    and volume['direction'] == 'up'
                    and rent['direction'] != 'down'
                    and sale['direction'] != 'down'
                    and len({(c['previous_observed_at'], c['current_observed_at']) for c in (sale, volume, rent)}) == 1
                ):
                    region_cases.append(region)
            if region_cases:
                r.update(
                    candidate_eligible=True,
                    investment_assessment='conditional_research_case',
                    why_now='가격·거래량·전세의 같은 월 변화가 함께 확인된 지역: '
                    + ', '.join(region_cases)
                    + '. 금융비용·물건별 현금흐름·가격 반영을 확인할 조건부 연구 후보.',
                    decision_rule='same_region_month_sale_volume_rent_confirmation',
                    evidence_ids=selected_refs(REGIONAL),
                )
            r['candidate_regions'] = region_cases
        if four:
            asset = r['asset_id']
            if asset == 'GOLD' and latest(asset, 'IAU_GOLD_PHYSICAL_HELD'):
                r.update(
                    why_now='금 가격·흐름·실질금리와 IAU 실물 보유량 수준을 확인했다. 보유량 증가/순유입이 확인된 것은 아니며 가격만으로 투자 우위를 결론내리지 않는다.',
                    decision_rule='gold_direct_holding_level_not_automatic_flow_or_opportunity',
                    unknowns=['같은 금 신탁의 보유량 변화·ETF 순유입·중앙은행/실물 수요·달러 환경·상품 비용'],
                )
            if asset == 'NATGAS' and latest(asset, 'EIA_US_DRY_GAS_PRODUCTION'):
                r.update(
                    why_now='실제 월간 생산·LNG 수출, 계절별 재고 기준과 기온 전망을 함께 비교할 수 있다. 기간이 다른 자료이며 겨울·가격 상승만으로 공급 부족이나 좋은 선물 투자로 결론내리지 않는다.',
                    decision_rule='actual_gas_supply_seasonal_storage_forecast_weather_separate_periods',
                    unknowns=[
                        '현재 주간 실제 생산·당일 LNG feedgas·공식 보간 오년 평균/주입 속도·HDD/CDD·선물곡선·UNG/BOIL 상품 구조·투기 포지션'
                    ],
                )
            if asset == 'ETH' and latest(asset, 'US_SPOT_ETH_ETF_DAILY_NET_FLOW'):
                r['unknowns'] = [
                    'ETH ETF 집계의 원발행사 확인·이례적 하루 값의 정확성·동일 기간 가격/흐름·네트워크 사용/수수료·staking·레버리지'
                ]
                r[
                    'why_now'
                ] += ' ETH 기관 집계를 BTC와 분리해 확보했다. 제공자 자동 집계의 산술 확인은 원자료 정확성 확인과 다르며 네트워크/경제 가치로 일반화하지 않는다.'
            if asset == 'BROAD_COMMODITIES' and latest(asset, 'ISHARES_GSG_NAV'):
                r.update(
                    status='conditional_watch',
                    evidence_ids=selected_refs(asset),
                    context_ids=list(dict.fromkeys(r['context_ids'] + r['coverage']['slots'][-1]['evidence_ids'])),
                    why_now='광범위 원자재 선물 상품 GSG의 NAV/정의가 명확한 흐름과 복수 하위 그룹 단서를 확인했다. 전체 구성 비중·산업금속/농산물 수급이 부족해 원유만으로 동반 강세를 확정하지 않는다.',
                    investment_assessment='mixed_signals',
                    decision_rule='broad_product_and_distinct_subgroup_clues_not_crude_proxy',
                    unknowns=[
                        '현재 하위 그룹 비중·산업금속/농산물 수급·서로 같은 기간 가격·선물 교체 비용·물가 방어의 실증'
                    ],
                )
        if run.input.get('commodity_coverage'):
            new_facts = [e for e in factual.values() if r['asset_id'] in e.asset_ids]
            if r['asset_id'] == 'NATGAS' and any(
                e.provenance.definition['measure'] == 'CME_NG_SETTLEMENT' for e in new_facts
            ):
                r[
                    'why_now'
                ] += ' 동일 관측일의 만기별 실제 선물곡선도 확인했다. 가격차를 실현 roll 수익으로 바꾸거나 새 자료 수로 후보를 올리지 않는다.'
                r['unknowns'] = [
                    '현재 주간 실제 생산·당일 LNG feedgas·공식 보간 평균/시장 기대 주입량·HDD/CDD',
                    'UNG/BOIL 현재 상품 구조·실현 roll·CFTC 포지션; Scan에서는 모두 깊게 조사하지 않음',
                ]
            if r['asset_id'] == 'GOLD' and any(
                e.provenance.definition['measure'] == 'WGC_GLOBAL_GOLD_ETF_NET_FLOW' for e in new_facts
            ):
                r['why_now'] = (
                    '한 신탁 보유 수준과 전체 금 ETF의 최근 공개 월 순유입/실물량 변화를 구분해 확인했다. 월·분기 수요는 현재 일별 가격과 시차가 있어 현재 진입 우위를 확정하지 않는다.'
                )
                r['unknowns'] = [
                    '더 최신 전체 금 ETF flow·IAU 보유량 변화·국가별 확정 중앙은행 매수·실물 소비·달러 환경·상품 비용'
                ]
                r['evidence_ids'] = list(
                    dict.fromkeys(
                        r['evidence_ids']
                        + [e.id for e in new_facts if e.provenance.definition['measure'].startswith('WGC_')]
                    )
                )
        if r['coverage_status'] == 'insufficient':
            r['candidate_eligible'] = False
            if r['investment_assessment'] not in ('comparison_anchor', 'liquidity_alternative'):
                r['investment_assessment'] = 'not_assessed_due_to_gap'
        if r['coverage']['critical_gaps'] and r['candidate_eligible']:
            r['confidence'] = '조건부 연구 후보 — 핵심 자료 확인 필요; 투자 가격의 우위 판단 유보'
        r['unknowns'] = list(
            dict.fromkeys(
                r['unknowns']
                + [s['label'] + ': ' + s['impact'] for s in r['coverage']['slots'] if s['status'] == 'missing']
            )
        )
    economic_changes = [
        c for c in history['observations'] if c['status'] == 'new_observation' and c['direction'] != 'flat'
    ]
    # Flat fundamentals are part of a price-versus-reality comparison, too.
    hypotheses = combinations(history['observations'] if enhanced else economic_changes, enhanced=enhanced)
    # A supported new divergence may make any eligible asset worth researching.
    for h in hypotheses:
        r = index[h['asset_id']]
        if enhanced and '괴리 위험' in h['text']:
            r.update(
                candidate_eligible=False,
                investment_assessment='mixed_signals',
                status='conditional_watch',
                why_now=h['text'],
                evidence_ids=list(dict.fromkeys(r['evidence_ids'] + h['evidence_ids'])),
                decision_rule='price_up_economic_signal_down_counterevidence',
            )
            continue
        if r['coverage_status'] != 'insufficient' and not ('괴리 위험' in h['text']):
            r.update(
                candidate_eligible=True,
                investment_assessment='conditional_research_case',
                why_now=h['text'],
                evidence_ids=list(dict.fromkeys(r['evidence_ids'] + h['evidence_ids'])),
                decision_rule='same_definition_economic_change_hypothesis',
            )
    if enhanced:
        # A new, higher starting yield plus a worsening equity earnings
        # outlook can make the income alternative worth comparison. No yield
        # threshold, guaranteed return or rate/earnings period equivalence.
        revs = [
            c
            for c in economic_changes
            if c['asset_id'] == 'US_EQUITY' and c['measure'] == 'F_Q3_EPS_REVISION' and c['direction'] == 'down'
        ]
        for asset, measure in [
            ('KR_GOVERNMENT_3Y', 'KR_GOVERNMENT_NOMINAL_3Y'),
            ('SHORT_BOND', 'US_TREASURY_NOMINAL_2Y'),
            ('LONG_BOND', 'US_TREASURY_NOMINAL_10Y'),
        ]:
            ys = [
                c
                for c in economic_changes
                if c['asset_id'] == asset and c['measure'] == measure and c['direction'] == 'up'
            ]
            if revs and ys and index[asset]['coverage_status'] != 'insufficient':
                r = index[asset]
                r.update(
                    candidate_eligible=True,
                    investment_assessment='conditional_research_case',
                    why_now='새로 확인한 시작 금리가 높아졌고 미국 주식의 같은 분기 이익 전망 수정은 악화됐다. 이자 대안의 기회비용을 비교할 조건부 연구 질문. 관측 주기 차이와 한국/미국 통화·만기는 별도 확인.',
                    evidence_ids=list(dict.fromkeys(r['evidence_ids'] + [c['current_evidence_id'] for c in ys])),
                    context_ids=list(dict.fromkeys(r['context_ids'] + [c['current_evidence_id'] for c in revs])),
                    decision_rule='new_starting_yield_vs_worsening_equity_expectation',
                )
        # A current source regressing behind the saved observation cannot
        # masquerade as new/current price information.
        for c in history['observations']:
            if c['status'] == 'regressed_observation':
                r = index[c['asset_id']]
                r['candidate_eligible'] = False
                r['unknowns'].append(
                    '동일 출처의 현재 관측이 이전 Scan보다 오래됨: ' + c['measure'] + '; 현재 변화 판단 보류'
                )
    for r in base['universe']:
        if r['candidate_eligible']:
            r['research_priority'] = (
                'changed_economic_question'
                if any(h['asset_id'] == r['asset_id'] for h in hypotheses)
                or enhanced
                and r['decision_rule'] == 'new_starting_yield_vs_worsening_equity_expectation'
                else 'conditional_economic_question'
            )
        else:
            r['research_priority'] = 'context_or_watch'
    # Coverage status, source count, popularity and the number of observations
    # are absent from this order. A changed economic question goes first;
    # unchanged questions retain their relative order. Ties use universe order.
    universe_order = {r['asset_id']: i for i, r in enumerate(base['universe'])}
    prior_order = {a: i for i, a in enumerate(past['candidates'])} if past else {}
    chosen = sorted(
        [r for r in base['universe'] if r['candidate_eligible']],
        key=lambda r: (
            0 if r['research_priority'] == 'changed_economic_question' else 1,
            prior_order.get(r['asset_id'], len(prior_order) + universe_order[r['asset_id']]),
        ),
    )[: base['candidate_cap']]
    for r in base['universe']:
        if r['candidate_eligible']:
            r.update(
                status='conditional_watch',
                action='조건부 경제 가설이 있으나 이번 짧은 목록 밖; 자료 양이나 매력 부족으로 탈락한 것 아님',
            )
    for i, r in enumerate(chosen, 1):
        r.update(
            status='research_candidate',
            selected=True,
            reference_number=i,
            action='현재 가격이 실제 개선을 얼마나 반영했는지와 핵심 반대 근거를 깊게 검증',
        )
    candidates = [r['asset_id'] for r in chosen]
    candidate_changes = []
    if past:
        previous = {r['asset_id']: r for r in past['rows']}
        for r in base['universe']:
            asset = r['asset_id']
            before = asset in past['candidates']
            after = asset in candidates
            old = previous.get(asset)
            changed = [c for c in economic_changes if c['asset_id'] == asset]
            method_changed = past['scan_method'] != run.input['scan']['method_version']
            kind = (
                'added'
                if after and not before
                else (
                    'removed'
                    if before and not after
                    else 'unchanged_candidate' if before and after else 'unchanged_watch'
                )
            )
            if kind == 'unchanged_candidate' and r['research_priority'] == 'changed_economic_question':
                kind = 'priority_raised'
            if old and old['status'] == 'research_candidate' and r['candidate_eligible'] and not after:
                kind = 'priority_lowered'
            if enhanced:
                if before and not after:
                    kind = 'removed'
                elif before and after:
                    old_position = past['candidates'].index(asset)
                    new_position = candidates.index(asset)
                    kind = (
                        'priority_raised'
                        if new_position < old_position
                        else 'priority_lowered' if new_position > old_position else 'unchanged_candidate'
                    )
            reason = (
                '같은 정의의 새 시장 관측으로 연구 질문을 재검토.'
                if changed
                else '현재 확인한 같은 관측에서 판단 유지.'
            )
            if method_changed and kind in ('removed', 'added', 'priority_lowered', 'priority_raised'):
                reason = '최소 coverage/후보 선정 방법 변경. 시장 가격·실적이 변했다는 뜻이 아니다. ' + r['why_now']
            elif enhanced and kind in ('priority_lowered', 'priority_raised') and not changed:
                reason = '다른 경제 가설의 조사 순서 변경으로 목록 내 위치 이동. 이 자산 자체의 매력/자료 충족 변화로 단정하지 않는다.'
            elif not changed and kind in ('added', 'removed', 'priority_lowered'):
                reason = (
                    '자료 연결/현재 검증 상태 또는 짧은 목록의 범위 변경. 시장 개선·악화로 단정하지 않는다. '
                    + r['why_now']
                )
            candidate_changes.append(
                dict(
                    asset_id=asset,
                    change=kind,
                    reason=reason,
                    new_evidence_ids=[c['current_evidence_id'] for c in changed],
                    before_status=old['status'] if old else None,
                    current_status=r['status'],
                )
            )
    history.update(
        candidate_changes=candidate_changes,
        hypotheses=hypotheses,
        meaning='시장 변화 / 같은 관측 재확인 / 동일 관측 개정 / 새 자료 연결 / 방법 변경을 구분한다.',
    )
    for r in base['universe']:
        if not set(r['evidence_ids']) <= set(factual):
            raise SourceError('minimum Scan reason lacks current evidence')
    return {
        **base,
        'universe': base['universe'],
        'candidates': candidates,
        'minimum_evidence_version': VERSION,
        'coverage_standards': {k: [list(s) for s in v] for k, v in (FOUR_STANDARDS if four else STANDARDS).items()},
        'observations': points,
        'within_scan_changes': changes,
        'since_previous_scan': history,
        'comparison_anchors': [
            r['asset_id']
            for r in base['universe']
            if r['investment_assessment'] in ('comparison_anchor', 'liquidity_alternative')
        ],
        'priority_reason': '동일 정의의 의미 있는 경제 신호 변화가 있는 연구 질문을 먼저 본다. 나머지는 기존 질문 순서, 첫 실행 동률은 조사 영역 순서다. 자료 수·coverage 상태는 순위 입력이 아니다.',
        'selection_status': 'shortlist' if candidates else 'insufficient_for_shortlist',
    }
