"""Deterministic quarantine of suspect evidence, not a statistical truth engine.

Raw quotes and immutable snapshots are retained. Quarantined numbers lose
permission to drive calculations, claims, coverage or current conclusions.
Old runs without the explicit method marker retain their original replay.
"""

from collections import defaultdict
from dataclasses import replace
from decimal import Decimal, localcontext
from statistics import median
import re

from .models import InterpretationStatus, Review, SourceType, VerificationStatus
from .sources import SourceError, _time

VERSION = 'source_anomaly_guard_v1'
# Unit/meaning contracts are explicit identities, never conversion guesses.
CONTRACTS = {
    'US_SPOT_BTC_ETF_DAILY_NET_FLOW': ('USD_million', 'USD'),
    'US_SPOT_ETH_ETF_DAILY_NET_FLOW': ('USD_million', 'USD'),
    'IAU_GOLD_PHYSICAL_HELD': ('tonnes', None),
    'EIA_US_WORKING_GAS_STOCK': ('Bcf', None),
    'EIA_US_DRY_GAS_PRODUCTION': ('MMcf', None),
    'EIA_US_LNG_EXPORTS': ('MMcf', None),
    'ISHARES_GSG_NAV': ('USD_per_share', 'USD'),
    'US_TIPS_10Y_CURRENT': ('percent', 'USD'),
    'DERIBIT_BTC_PERPETUAL_FUNDING_8H': ('fraction', None),
    'WGC_GLOBAL_GOLD_ETF_NET_FLOW': ('USD_billion', 'USD'),
    'WGC_GLOBAL_GOLD_ETF_HOLDINGS_CHANGE': ('tonnes', None),
    'WGC_GLOBAL_GOLD_ETF_HOLDINGS': ('tonnes', None),
    'WGC_CENTRAL_BANK_NET_DEMAND': ('tonnes', None),
    'WGC_JEWELLERY_CONSUMPTION': ('tonnes', None),
    'WGC_BAR_COIN_DEMAND': ('tonnes', None),
    'EIA_HENRY_HUB_SPOT': ('USD_per_MMBtu', 'USD'),
    'EIA_WTI_SPOT': ('USD_per_barrel', 'USD'),
    'LBMA_GOLD_PM_ISSUER_REPORTED': ('USD_per_troy_ounce', 'USD'),
}
PERIOD_PATTERNS = {
    'US_SPOT_BTC_ETF_DAILY_NET_FLOW': r'\d{4}-\d{2}-\d{2}',
    'US_SPOT_ETH_ETF_DAILY_NET_FLOW': r'\d{4}-\d{2}-\d{2}',
    'EIA_US_DRY_GAS_PRODUCTION': r'\d{4}-\d{2}',
    'EIA_US_LNG_EXPORTS': r'\d{4}-\d{2}',
    'WGC_GLOBAL_GOLD_ETF_NET_FLOW': r'\d{4}-\d{2}',
    'WGC_GLOBAL_GOLD_ETF_HOLDINGS_CHANGE': r'\d{4}-\d{2}',
    'ISHARES_GSG_NAV': r'\d{4}-\d{2}-\d{2}',
}
ADJUSTMENTS = {
    'ISHARES_GSG_NAV': {'issuer_reported_fund_NAV_not_spot_index_not_market_price'},
    'IAU_GOLD_PHYSICAL_HELD': {'issuer_reported_trade_date_holdings_not_AUM_not_net_flow'},
    'EIA_US_DRY_GAS_PRODUCTION': {'reported_monthly_actual_volume_not_forecast_not_daily_feedgas'},
    'EIA_US_LNG_EXPORTS': {'reported_monthly_actual_volume_not_forecast_not_daily_feedgas'},
    'WGC_GLOBAL_GOLD_ETF_NET_FLOW': {'monthly_provider_reported_not_AUM_price_effect_not_issuer_cross_checked'},
    'WGC_GLOBAL_GOLD_ETF_HOLDINGS_CHANGE': {'monthly_provider_reported_not_AUM_price_effect_not_issuer_cross_checked'},
}


def validate_config(config):
    if (
        not isinstance(config, dict)
        or set(config) != {'method_version', 'numeric_ids'}
        or config['method_version'] != VERSION
        or not isinstance(config['numeric_ids'], list)
        or len(config['numeric_ids']) > 160
        or any(not isinstance(i, str) for i in config['numeric_ids'])
        or len(set(config['numeric_ids'])) != len(config['numeric_ids'])
    ):
        raise SourceError('invalid source anomaly validation contract')
    return config


def guard_records(evidence, sources, cutoff=None, *, numeric_ids=()):
    """Same-provider conflicts and >=20x neighbour magnitude require a check.

    Twenty is a disclosed conservative *review trigger*, not an error threshold or
    investment score. At least three distinct same-definition adjacent observations
    are required; provider duplicates are not independent observations. A move can
    be real. Only independently published, same-definition primary evidence can
    release a suspicion; repeated renderings from one provider cannot do so.
    """
    lookup = {s.id: s for s in sources}
    by_id = {e.id: e for e in evidence}
    rows = {}
    for e in evidence:
        if e.kind == 'observed_narrative' or not e.provenance:
            continue
        rows[e.id] = dict(
            evidence_id=e.id,
            source_id=e.source_id,
            snapshot_id=e.provenance.snapshot_id,
            definition=e.provenance.definition,
            raw_value=str(e.value) if e.value is not None else None,
            raw_text=e.text,
            status='accepted',
            reasons=[],
            cross_check_ids=[],
        )

    def flag(e, status, reason):
        row = rows[e.id]
        row['status'] = status
        if reason not in row['reasons']:
            row['reasons'].append(reason)

    def provider(e):
        s = lookup[e.source_id]
        return s.provenance.publisher if s.provenance else s.name

    def available(e):
        s = lookup[e.source_id]
        p = e.provenance
        sp = s.provenance
        return (
            e.verification == VerificationStatus.SUPPORTED
            and p.match_status == 'matched'
            and (e.value is None or e.value.is_finite())
            and p.freshness in ('fresh', 'per_observation')
            and sp
            and sp.status == 'available'
            and (
                cutoff is None
                or (
                    _time(sp.retrieved_at) <= cutoff
                    and (e.observed_at is None or e.observed_at <= cutoff.date())
                    and (sp.published_at is None or _time(sp.published_at) <= cutoff)
                )
            )
        )

    def key(e, period=True, unit=True):
        d = e.provenance.definition
        return tuple(
            d[k]
            for k in (
                'measure',
                'scope',
                'adjustment',
                *(('period',) if period else ()),
                *(('unit', 'currency') if unit else ()),
            )
        ) + ((str(e.observed_at),) if period and d['period'] in ('daily', 'weekly', 'monthly', 'annual') else ())

    def root(e):
        s = lookup[e.source_id]
        seen = set()
        while s.origin_source_id in lookup and s.id not in seen:
            seen.add(s.id)
            s = lookup[s.origin_source_id]
        return s.id

    for e in evidence:
        if e.id not in rows:
            continue
        d = e.provenance.definition
        expected = CONTRACTS.get(d['measure'])
        if e.value is not None and not e.value.is_finite():
            flag(e, 'anomalous', '유한하지 않은 수치는 계산·현재 판단에 사용하지 않는다.')
        if expected and (d['unit'], d['currency']) != expected:
            flag(e, 'unit_mismatch', '검토된 measure의 단위/통화와 다름. 단위를 임의 변환하지 않고 격리한다.')
        if d['measure'] in PERIOD_PATTERNS and not re.fullmatch(PERIOD_PATTERNS[d['measure']], d['period']):
            flag(e, 'unit_mismatch', '검토된 측정의 관측 주기와 기간이 다르다. daily/monthly를 대체하지 않는다.')
        if d['measure'] in ADJUSTMENTS and d['adjustment'] not in ADJUSTMENTS[d['measure']]:
            flag(
                e,
                'unit_mismatch',
                '등록 측정의 경제적 정의와 다르다. flow/AUM, price/NAV, 실제/전망을 대체하지 않는다.',
            )
        if e.value is not None and (e.unit, e.period, e.currency) != (d['unit'], d['period'], d['currency']):
            flag(e, 'unit_mismatch', '전사 숫자와 provenance의 단위/기간/통화가 충돌한다.')
        if e.id in numeric_ids and e.value is None:
            flag(e, 'incomplete', 'null/blank/-/미보고/미완성 또는 추출 실패. zero로 대체하지 않는다.')
        if d['adjustment'] in (
            'partial_row_not_final_total',
            'historical_reference_not_current_flow_when_latest_partial',
        ):
            flag(e, 'incomplete', '최신 ETF 행이 미완성. 과거 완료 행이나 잠정 합계로 현재 flow를 채우지 않는다.')

    groups = defaultdict(list)
    for e in evidence:
        if e.id in rows and e.value is not None and available(e):
            groups[(provider(e), key(e, unit=False))].append(e)
    for members in groups.values():
        if len({(e.unit, e.currency) for e in members}) > 1:
            for e in members:
                flag(
                    e, 'unit_mismatch', '같은 제공자·측정·기간·scope의 단위가 충돌한다. USD/million 등 자동 환산 없음.'
                )
        elif len({e.value for e in members}) > 1:
            for e in members:
                flag(e, 'conflicting', '같은 제공자의 동일 정의 관측이 endpoint/rendering/table 사이에서 충돌한다.')

    series = defaultdict(list)
    for e in evidence:
        if e.id in rows and e.value is not None and available(e) and rows[e.id]['status'] == 'accepted':
            series[(provider(e), key(e, period=False))].append(e)
    for members in series.values():
        points = defaultdict(list)
        for e in members:
            # Only dated observations, not FY1/TTM/month-vs-day mixtures.
            try:
                day = _time(e.period)
            except SourceError:
                continue
            if day is not None:
                points[day].append(e)
        dates = sorted(points)
        for at in dates:
            neighbours = sorted((d for d in dates if d != at), key=lambda d: abs((d - at).total_seconds()))[:4]
            if len(neighbours) < 3:
                continue
            # Conflicting duplicates must never become a "normal range".
            values = [abs(points[d][0].value) for d in neighbours if len({e.value for e in points[d]}) == 1]
            if len(values) < 3:
                continue
            typical = median(values)
            with localcontext() as ctx:
                ctx.prec = 50
                for e in points[at]:
                    if typical > 0 and abs(e.value) >= typical * 20:
                        flag(
                            e,
                            'anomalous',
                            '인접 동일 정의 관측 절대값 중앙값 대비 20배 이상: 단위/데이터 오류 가능성 추가 검증 필요. 오류로 확정하지 않는다.',
                        )

    for e in evidence:
        row = rows.get(e.id)
        if not row or row['status'] not in ('anomalous', 'conflicting'):
            continue
        matches = [
            other
            for other in evidence
            if other.id != e.id
            and other.value == e.value
            and other.id in rows
            and rows[other.id]['status'] == 'accepted'
            and available(other)
            and lookup[other.source_id].type == SourceType.PRIMARY
            and provider(other) != provider(e)
            and root(other) != root(e)
            and key(other) == key(e)
        ]
        if matches:
            row.update(status='cross_checked', cross_check_ids=sorted(o.id for o in matches))
            row['reasons'].append(
                '독립 원자료의 같은 날짜·단위·scope 값과 일치. 범위 밖 경제적 진실/투자 매력은 확인하지 않는다.'
            )

    blocked = {i for i, r in rows.items() if r['status'] not in ('accepted', 'cross_checked')}
    adjusted = []
    for e in evidence:
        if e.id in blocked:
            # A reported subtotal of an incomplete row remains a raw
            # transcription. Its verification blocks every financial consumer;
            # it is never relabelled as the final flow or filled with zero.
            raw_partial = e.value if rows[e.id]['status'] == 'incomplete' else None
            adjusted.append(
                replace(
                    e,
                    value=raw_partial,
                    verification=VerificationStatus.UNVERIFIED,
                    interpretation=Review(
                        InterpretationStatus.PENDING,
                        None,
                        None,
                        '이상/충돌/미완성 자료는 추가 원자료 검증 전 격리한다.',
                    ),
                    limitations=(
                        *e.limitations,
                        'source_anomaly_guard_v1: quarantined; ' + ' / '.join(rows[e.id]['reasons']),
                    ),
                )
            )
        else:
            adjusted.append(e)
    audit = dict(
        method_version=VERSION,
        rule='quarantine_not_truth_or_attractiveness_score',
        threshold='at least 3 distinct same-definition neighbouring dates; magnitude >= 20 * median absolute neighbour value',
        records=list(rows.values()),
        quarantined_ids=sorted(blocked),
    )
    return tuple(adjusted), audit


def guard_case(case, cutoff, *, numeric_ids=()):
    evidence, audit = guard_records(case.evidence, case.sources, cutoff, numeric_ids=numeric_ids)
    blocked = set(audit['quarantined_ids'])
    claims = []
    for c in case.claims:
        refs = set((*c.support_ids, *c.counter_ids, *c.context_ids)) & blocked
        claims.append(
            replace(
                c,
                verification=VerificationStatus.UNVERIFIED,
                interpretation=Review(InterpretationStatus.PENDING, None, None, '격리 근거에 의존하는 주장 확인 보류.'),
                limitations=(*c.limitations, '격리 근거: ' + ', '.join(sorted(refs))),
            )
            if refs
            else c
        )
    return replace(case, evidence=evidence, claims=tuple(claims)), audit
