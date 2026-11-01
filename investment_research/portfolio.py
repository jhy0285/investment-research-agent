"""Self-reported holdings and deterministic composition, never optimal weights."""

from dataclasses import dataclass
from datetime import date
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from pathlib import Path

from .models import (
    EvidenceRecord,
    InterpretationStatus,
    MetricResult,
    ProfileField,
    ProfileSnapshot,
    Review,
    SourceRecord,
    SourceType,
    VerificationStatus,
)
from .source_pipeline import _day, _decimal, _digest, _id, _list, _object, _text, load_pins
from .sources import SourceError

PORTFOLIO_VERSION = "portfolio_composition_v1"
CONTEXT = Context(prec=50, rounding=ROUND_HALF_EVEN)


def _amount(value, name):
    if value is None:
        return None
    number = _decimal(value, name)
    if number < 0:
        raise SourceError(name + ': nonnegative self-reported amount required')
    return number


def validate_portfolio(data):
    _object(
        data,
        {
            'schema_version',
            'as_of',
            'base_currency',
            'coverage',
            'holdings',
            'cash_krw',
            'debt_krw',
            'monthly_investable_krw',
            'future_cash_needs',
            'horizon_months',
        },
        {'synthetic'},
        'portfolio',
    )
    if data['schema_version'] != 'portfolio-v1' or data['base_currency'] != 'KRW':
        raise SourceError(
            'portfolio-v1 requires explicit KRW-valued inputs; foreign amounts need a verified conversion first'
        )
    _day(data['as_of'], 'portfolio.as_of')
    if data['coverage'] not in ('complete', 'partial', 'unknown'):
        raise SourceError('portfolio.coverage must disclose complete/partial/unknown holdings')
    if type(data.get('synthetic', False)) is not bool:
        raise SourceError('portfolio.synthetic must be boolean')
    ids = []
    for holding in _list(data['holdings'], 'holdings'):
        _object(holding, {'id', 'name', 'value_krw'}, {'asset'}, 'holding')
        ids.append(_id(holding['id'], 'holding.id'))
        _text(holding['name'], 'holding.name')
        if len(holding['id']) > 64 or len(holding['name']) > 300:
            raise SourceError('bounded holding identifiers and labels required')
        if 'asset' in holding:
            _text(holding['asset'], 'holding.asset')
        _amount(holding['value_krw'], 'holding.value_krw')
    if len(ids) != len(set(ids)) or 'CASH' in ids:
        raise SourceError('unique holding IDs required; CASH is reserved')
    for name in ('cash_krw', 'debt_krw', 'monthly_investable_krw'):
        _amount(data[name], name)
    needs = data['future_cash_needs']
    if needs is not None:
        for need in _list(needs, 'future_cash_needs'):
            _object(need, {'name', 'amount_krw', 'needed_at'}, set(), 'cash need')
            _text(need['name'], 'need.name')
            _amount(need['amount_krw'], 'need.amount_krw')
            _day(need['needed_at'], 'need.needed_at')
    horizon = data['horizon_months']
    if horizon is not None and (type(horizon) is not int or not 1 <= horizon <= 1200):
        raise SourceError('horizon_months must be a positive bounded integer or null')
    return data


def load_portfolio(path):
    return validate_portfolio(load_pins(path))


@dataclass(frozen=True)
class PortfolioReview:
    status: str
    missing: tuple[str, ...]
    source: SourceRecord | None
    evidence: tuple[EvidenceRecord, ...]
    metrics: tuple[MetricResult, ...]
    profile: ProfileSnapshot
    largest_ids: tuple[str, ...]
    input_digest: str


def review_portfolio(data, cutoff: date) -> PortfolioReview:
    unknown_profile = ProfileSnapshot('ASK_PROFILE', cutoff, {'base_currency': ProfileField('known', 'KRW')})
    if data is None:
        return PortfolioReview(
            'needs_input',
            (
                '실제 보유내역·금액/구성·누락 범위',
                '현금',
                '부채',
                '월 추가 투자 가능액',
                '향후 큰 자금수요',
                '투자기간',
            ),
            None,
            (),
            (),
            unknown_profile,
            (),
            _digest(None),
        )
    validate_portfolio(data)
    observed = _day(data['as_of'], 'portfolio.as_of')
    if observed > cutoff:
        raise SourceError('portfolio information is after the research cutoff')
    missing = []
    if data['coverage'] != 'complete':
        missing.append('전체 보유 범위 확인')
    if not data['holdings'] and data['coverage'] != 'complete':
        missing.append('보유 내역 확인; 불완전한 빈 목록이 무자산을 뜻하지 않는다')
    for field, label in [
        ('cash_krw', '현금'),
        ('debt_krw', '부채'),
        ('monthly_investable_krw', '월 추가 투자 가능액'),
        ('future_cash_needs', '향후 큰 자금수요'),
        ('horizon_months', '투자기간'),
    ]:
        if data[field] is None:
            missing.append(label)
    if any(holding['value_krw'] is None for holding in data['holdings']):
        missing.append('누락된 보유 평가금액')
    if data['future_cash_needs'] is not None and any(need['amount_krw'] is None for need in data['future_cash_needs']):
        missing.append('미확인 자금수요 금액')
    source = SourceRecord(
        'ASK_PORTFOLIO_INPUT',
        SourceType.PRIMARY,
        '사용자가 제공한 KRW 보유 입력',
        'local:input.json#/portfolio',
        observed,
        observed,
        cutoff,
        None,
        (
            '자기보고 금액이며 계좌 잔액·시장가격의 외부 검증이 아니다.',
            'KRW로 입력한 평가액만 사용하고 환율을 추정하지 않는다.',
        ),
    )
    pending = Review(
        InterpretationStatus.PENDING, None, None, '사용자의 자기보고 입력이다. 계산 가능성과 투자 적절성은 다르다.'
    )
    evidence = []

    def record(identifier, label, value, unit='KRW'):
        if value is None:
            return
        evidence.append(
            EvidenceRecord(
                identifier,
                source.id,
                label + ' · 사용자 제공 값',
                identifier,
                observed,
                cutoff,
                (),
                'quantitative',
                'observed_fact',
                VerificationStatus.SUPPORTED,
                pending,
                ('검증 범위는 제공된 입력의 형식·계산이다. 실제 잔액 검증이 아니다.',),
                value,
                unit,
                'self_reported_snapshot',
                'KRW' if unit == 'KRW' else None,
            )
        )

    for holding in data['holdings']:
        record('PORT_VALUE_' + holding['id'], holding['name'], _amount(holding['value_krw'], 'holding value'))
    for field, identifier in [
        ('cash_krw', 'PORT_CASH'),
        ('debt_krw', 'PORT_DEBT'),
        ('monthly_investable_krw', 'PORT_MONTHLY'),
    ]:
        record(identifier, field, _amount(data[field], field))
    for index, need in enumerate(data['future_cash_needs'] or []):
        record('PORT_NEED_' + str(index), need['name'], _amount(need['amount_krw'], 'need amount'))
    metrics = []
    largest = ()
    complete = (
        data['coverage'] == 'complete'
        and data['cash_krw'] is not None
        and all(holding['value_krw'] is not None for holding in data['holdings'])
    )
    with localcontext(CONTEXT):
        if complete:
            amounts = [(holding['id'], Decimal(holding['value_krw'])) for holding in data['holdings']] + [
                ('CASH', Decimal(data['cash_krw']))
            ]
            inputs = tuple(
                'PORT_CASH' if identifier == 'CASH' else 'PORT_VALUE_' + identifier for identifier, _ in amounts
            )
            total = sum((value for _, value in amounts), Decimal(0))
            metrics.append(
                MetricResult(
                    'PORT_TOTAL',
                    '제공된 전체 보유 평가액과 현금 합계',
                    total,
                    'KRW',
                    'portfolio_total_v1',
                    inputs,
                    (),
                    ('제공된 KRW 평가액의 합계다. 외부 가격·전체 계좌의 정확성을 검증한 값은 아니다.',),
                )
            )
            if total > 0:
                for identifier, value in amounts:
                    metrics.append(
                        MetricResult(
                            'PORT_WEIGHT_' + identifier,
                            identifier + '의 제공된 평가액 비중',
                            value / total * 100,
                            'percent',
                            'portfolio_weight_v1',
                            inputs,
                            (identifier,),
                            ('분모는 제공된 보유액과 현금 합계다. 권고·적정 비중이 아니다.',),
                        )
                    )
                maximum = max(value for _, value in amounts)
                largest = tuple(identifier for identifier, value in amounts if value == maximum)
            else:
                missing.append('양의 전체 평가액; 비중 계산은 보류한다')
            if data['debt_krw'] is not None:
                metrics.append(
                    MetricResult(
                        'PORT_NET_ASSETS',
                        '제공된 총자산에서 부채를 뺀 금액',
                        total - Decimal(data['debt_krw']),
                        'KRW',
                        'portfolio_net_assets_v1',
                        (*inputs, 'PORT_DEBT'),
                        (),
                        ('부채 상환 일정·금리·담보·소득 충격을 평가하지 않는다.',),
                    )
                )
        needs = data['future_cash_needs']
        if needs is not None and needs and all(need['amount_krw'] is not None for need in needs):
            metrics.append(
                MetricResult(
                    'PORT_CASH_NEEDS',
                    '사용자가 나열한 향후 자금수요 합계',
                    sum((Decimal(need['amount_krw']) for need in needs), Decimal(0)),
                    'KRW',
                    'portfolio_cash_needs_v1',
                    tuple('PORT_NEED_' + str(index) for index in range(len(needs))),
                    (),
                    ('여러 필요 시점의 명목 합계다. 시점별 지급 가능성·수익·할인을 추정하지 않는다.',),
                )
            )
    fields = {
        'base_currency': ProfileField('self_reported', 'KRW'),
        'holdings': ProfileField(
            'self_reported' if data['coverage'] == 'complete' else 'unknown',
            data['coverage'] if data['coverage'] == 'complete' else None,
        ),
    }
    for key, original in [
        ('cash', 'cash_krw'),
        ('debt', 'debt_krw'),
        ('monthly_investable', 'monthly_investable_krw'),
        ('horizon', 'horizon_months'),
    ]:
        fields[key] = ProfileField('unknown' if data[original] is None else 'self_reported', data[original])
    # The existing engine consumes these canonical context names. Preserve its
    # unknown guards without falsely asking again for supplied composition and
    # monthly amounts. Cash is not automatically an emergency fund, and a long
    # horizon is not proof of risk capacity.
    fields['monthly_investment'] = fields['monthly_investable']
    fields['total_assets'] = ProfileField('self_reported', str(total)) if complete else ProfileField('unknown', None)
    fields['portfolio_allocation'] = (
        ProfileField('self_reported', '사용자가 전체라고 명시한 KRW 평가액 구성; PORT_WEIGHT 계산을 참조한다.')
        if complete and total > 0
        else ProfileField('unknown', None)
    )
    return PortfolioReview(
        'partial' if missing else 'completed_composition',
        tuple(missing),
        source,
        tuple(evidence),
        tuple(metrics),
        ProfileSnapshot('ASK_PROFILE', observed, fields),
        largest,
        _digest(data),
    )
