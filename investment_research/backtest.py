"""Calendar-horizon event studies with next-observation execution and PIT inputs.

Nonoverlapping episodes are used for approval. Unconditional/seasonal baselines
are descriptive overlapping observations, explicitly not independent trials.
"""

from bisect import bisect_left
from datetime import timedelta
from decimal import Decimal
from random import Random
from statistics import median

from .decision_data import HORIZONS, digest, number, target, validate_dataset, validate_strategy, timestamp as _time
from .sources import SourceError

VERSION = 'pit_event_backtest_v2'
# v1 required total return on both sides. v2 also accepts a candidate price
# series reviewed as a lower bound of the holder's return (no cash
# distributions; omitted non-cash distributions can only add value) when the
# benchmark is a point-in-time total return. Saved v1 results replay as v1.
VERSIONS = ('pit_event_backtest_v1', 'pit_event_backtest_v2')
LOWER_BOUND = 'price_lower_bound'
BASE_LIMITATIONS = (
    '수익은 거래비용 차감 후이며 세금·미체결은 별도다.',
    '서로 겹치지 않는 신호로 평가한다. 표본 빈도는 미래 확률이 아니다.',
    '비교 구간 안에서 보유기간이 끝난 표본만 사용한다. 미성숙 신호는 성과에 넣지 않는다.',
    '신뢰구간은 독립에 가까운 표본 재추출이며 시장 구조 변화와 모든 의존성을 보증하지 않는다.',
)
ZERO = Decimal(0)
OPS = {
    '>': lambda a, b: a > b,
    '>=': lambda a, b: a >= b,
    '<': lambda a, b: a < b,
    '<=': lambda a, b: a <= b,
    '==': lambda a, b: a == b,
}


def condition_state(conditions, features, at):
    checks = []
    for r in conditions:
        eligible = [
            f
            for f in features
            if f['name'] == r['feature'] and _time(f['known_at']) <= at and _time(f['observed_at']) <= at
        ]
        # Choose latest observation, then latest revision available at that time.
        f = max(eligible, key=lambda f: (_time(f['observed_at']), _time(f['known_at']))) if eligible else None
        status = 'unknown'
        if f is not None and at - _time(f['observed_at']) <= timedelta(days=r['max_age_days']):
            status = 'pass' if OPS[r['op']](number(f['value']), number(r['value'])) else 'fail'
        checks.append(
            dict(
                feature=r['feature'],
                state=status,
                value=f['value'] if f else None,
                observed_at=f['observed_at'] if f else None,
                known_at=f['known_at'] if f else None,
                vintage=f['vintage'] if f else None,
            )
        )
    state = (
        'fail'
        if any(c['state'] == 'fail' for c in checks)
        else 'unknown' if any(c['state'] == 'unknown' for c in checks) else 'pass'
    )
    return dict(state=state, checks=checks)


def _prices(dataset, cutoff):
    return [r for r in dataset['rows'] if _time(r['at']) <= cutoff and _time(r['known_at']) <= cutoff]


def net_return(entry, exit, cost_bps):
    cost = number(cost_bps) / 10000
    return number(exit) * (1 - cost) / (number(entry) * (1 + cost)) - 1


def drawdown(values):
    peak, worst = values[0], ZERO
    for value in values:
        peak = max(peak, value)
        worst = min(worst, value / peak - 1)
    return worst


def statistics(episodes):
    values = [number(e['return']) for e in episodes]
    gains, losses = [v for v in values if v > 0], [v for v in values if v < 0]

    def avg(xs):
        return str(sum(xs, ZERO) / len(xs)) if xs else None

    return dict(
        count=len(values),
        mean=avg(values),
        median=str(median(values)) if values else None,
        win_rate=str(Decimal(len(gains)) / len(values)) if values else None,
        average_gain=avg(gains),
        average_loss=avg(losses),
        maximum_gain=str(max(values)) if values else None,
        maximum_loss=str(min(values)) if values else None,
        worst_interim_drawdown=str(min(number(e['drawdown']) for e in episodes)) if values else None,
    )


def _interval(values):
    if len(values) < 2:
        return None
    rng = Random(0)
    means = sorted(sum((rng.choice(values) for _ in values), ZERO) / len(values) for _ in range(1000))
    return [str(means[24]), str(means[974])]


def event_at(rows, i, horizon, end, cost, benchmark, *, times=None, benchmark_map=None):
    at = _time(rows[i]['at'])
    due = target(at, horizon)
    times = times if times is not None else [_time(r['at']) for r in rows]
    j = bisect_left(times, due, lo=i + 1)
    if j >= len(rows) or times[j] >= end or times[j] - due > timedelta(days=7):
        return None
    b = benchmark_map if benchmark_map is not None else {_time(r['at']): r for r in benchmark}
    if at not in b or times[j] not in b:
        return None
    cost = number(cost) / 10000
    path = [Decimal(1)] + [number(r['value']) / (number(rows[i]['value']) * (1 + cost)) for r in rows[i : j + 1]]
    path[-1] *= 1 - cost
    result = net_return(rows[i]['value'], rows[j]['value'], cost * 10000)
    baseline = net_return(b[at]['value'], b[times[j]]['value'], cost * 10000)
    return dict(
        entry_at=rows[i]['at'],
        exit_at=rows[j]['at'],
        entry_value=rows[i]['value'],
        exit_value=rows[j]['value'],
        **{
            'return': str(result),
            'benchmark_return': str(baseline),
            'excess_return': str(result - baseline),
            'drawdown': str(drawdown(path)),
        },
    )


def run_backtest(candidate, cutoff, version=VERSION):
    if version not in VERSIONS:
        raise SourceError('unsupported backtest version')
    s = candidate['strategy']
    validate_strategy(s)
    validate_dataset(candidate['prices'])
    validate_dataset(candidate['benchmark'])
    end = min(_time(s['splits']['end']), cutoff + timedelta(microseconds=1))
    rows, bench = _prices(candidate['prices'], cutoff), _prices(candidate['benchmark'], cutoff)
    row_times = [_time(r['at']) for r in rows]
    benchmark_map = {_time(r['at']): r for r in bench}
    features = candidate['features']
    # No same-close execution: the signal must have been available at the previous
    # close, and that close itself must have been known before the next entry.
    signals = []
    visible = {}
    cursor = 0
    releases = sorted(features, key=lambda f: _time(f['known_at']))
    for i in range(1, len(rows)):
        signal_at = _time(rows[i - 1]['at'])
        while cursor < len(releases) and _time(releases[cursor]['known_at']) <= signal_at:
            f = releases[cursor]
            old = visible.get(f['name'])
            if old is None or (_time(f['observed_at']), _time(f['known_at'])) > (
                _time(old['observed_at']),
                _time(old['known_at']),
            ):
                visible[f['name']] = f
            cursor += 1
        if (
            _time(rows[i - 1]['known_at']) < row_times[i]
            and condition_state(s['conditions'] + s['price_conditions'], list(visible.values()), signal_at)['state']
            == 'pass'
        ):
            signals.append(i)
    signal_set = set(signals)
    edges = [_time(s['splits'][k]) for k in ('start', 'validation_start', 'recent_start')] + [end]
    periods = {}
    for partition, start, stop in zip(('historical', 'validation', 'recent'), edges, edges[1:]):
        horizons = {}
        for horizon in ('1m', '3m', '6m', '1y'):
            selected, unconditional, seasonal = [], [], []
            last_exit = None
            months = {_time(rows[i]['at']).month for i in signals if start <= _time(rows[i]['at']) < stop}
            for i, r in enumerate(rows):
                at = _time(r['at'])
                if not start <= at < stop:
                    continue
                event = event_at(
                    rows, i, horizon, stop, s['cost_bps_per_side'], bench, times=row_times, benchmark_map=benchmark_map
                )
                if event is None:
                    continue
                unconditional.append(event)
                if at.month in months:
                    seasonal.append(event)
                if i in signal_set and (last_exit is None or at > last_exit):
                    selected.append(event)
                    last_exit = _time(event['exit_at'])
            excess = [number(e['excess_return']) for e in selected]
            horizons[horizon] = dict(
                signal=statistics(selected),
                unconditional=statistics(unconditional),
                same_season=statistics(seasonal),
                paired_market=statistics([{**e, 'return': e['benchmark_return']} for e in selected]),
                mean_excess=str(sum(excess, ZERO) / len(excess)) if excess else None,
                excess_interval_95=_interval(excess),
                episodes=selected,
                baseline_dependence='unconditional and same-season starts overlap; descriptive only',
            )
        selected_rows = [r for r in rows if start <= _time(r['at']) < stop]
        bh = (
            str(net_return(selected_rows[0]['value'], selected_rows[-1]['value'], s['cost_bps_per_side']))
            if len(selected_rows) > 1
            else None
        )
        periods[partition] = dict(start=start.isoformat(), end=stop.isoformat(), horizons=horizons, buy_and_hold=bh)
    history_years = (
        max((_time(r['at']) for r in rows), default=cutoff) - min((_time(r['at']) for r in rows), default=cutoff)
    ).days / 365.25
    blockers, limitations = _definition_blockers(candidate, version)
    if candidate['prices']['survivorship'] == 'current_survivors':
        blockers.append('현재 생존 종목만 사용했다.')
    if s['trial_count'] > 1:
        blockers.append('여러 조건을 탐색한 전략이다. 새 미래 검증 전에는 강한 승인이 불가하다.')
    return dict(
        method_version=version,
        strategy_sha256=digest(s),
        history_years=str(history_years),
        signal_occurrences=len(signals),
        periods=periods,
        blockers=blockers,
        limitations=list(BASE_LIMITATIONS) + limitations,
    )


def lower_bound(dataset):
    return (
        dataset.get('return_basis') == LOWER_BOUND
        and dataset['return_kind'] == 'price'
        and dataset['adjustment'] == 'unadjusted'
    )


def _definition_blockers(candidate, version):
    prices, bench = candidate['prices'], candidate['benchmark']
    blockers = []
    if version == 'pit_event_backtest_v1':
        if prices['return_kind'] != 'total_return':
            blockers.append('배당·분배금을 포함한 실제 상품 수익률이 아니다.')
        if any(d['adjustment'] != 'pit_total_return_index' for d in (prices, bench)):
            blockers.append('당시 이용 가능했던 총수익 판본이 아니다.')
        return blockers, []
    bounded = lower_bound(prices)
    if prices['return_kind'] != 'total_return' and not bounded:
        blockers.append('배당·분배금을 포함한 실제 상품 수익률이 아니다.')
    if not bounded and prices['adjustment'] != 'pit_total_return_index':
        blockers.append('당시 이용 가능했던 총수익 판본이 아니다.')
    if bench['return_kind'] != 'total_return' or bench['adjustment'] != 'pit_total_return_index':
        blockers.append('비교 시장이 당시 이용 가능했던 총수익 판본이 아니다.')
    limitations = []
    if bounded:
        limitations.append(
            '상품 수익은 현금 분배가 없는 자산의 가격 수익이다. 제외한 포크·에어드롭 같은 비현금 분배는 보유자 수익을 '
            '낮게 잡는 쪽이므로 절대 수익과 시장 대비 비교는 보수적이다. 같은 상품 안의 시점 비교(조건 없는 매수·같은 '
            '계절)는 제외한 분배의 시점에 따라 어느 쪽으로든 조금 치우칠 수 있다.'
        )
    return blockers, limitations


def approval(backtest, strategy, policy):
    if backtest['blockers']:
        return 'insufficient', backtest['blockers']
    results, reasons = {}, []
    for partition in ('historical', 'validation', 'recent'):
        r = backtest['periods'][partition]['horizons'][strategy['holding_horizon']]
        if r['signal']['count'] < policy['minimum_' + partition]:
            results[partition] = 'insufficient'
            reasons.append(partition + ': 서로 겹치지 않는 성숙 표본 부족')
        elif (
            number(r['signal']['mean']) <= 0
            or number(r['mean_excess']) <= 0
            or number(r['signal']['mean']) <= number(r['unconditional']['mean'])
            or r['same_season']['mean'] is not None
            and number(r['signal']['mean']) <= number(r['same_season']['mean'])
        ):
            results[partition] = 'failed'
            reasons.append(partition + ': 비용 차감 후 수익·조건 없는 매수·같은 계절·같은 시점 시장 대비 우위가 없음')
        elif r['excess_interval_95'] and number(r['excess_interval_95'][0]) > 0:
            results[partition] = 'passed'
        else:
            results[partition] = 'partial'
            reasons.append(partition + ': 평균 우위는 있지만 우연의 영향을 배제하기 어려움')
    if results['historical'] == 'failed' or results['validation'] == 'failed':
        return 'failed', reasons
    if results['recent'] == 'failed':
        return 'degraded', reasons
    if 'insufficient' in results.values():
        return 'insufficient', reasons
    if results['historical'] != 'passed' or results['validation'] != 'passed':
        return 'insufficient', reasons
    if results['recent'] == 'partial':
        return 'partial', reasons
    if number(backtest['history_years']) < 10:
        return 'partial', reasons + ['과거 가격 이력이 10년보다 짧음']
    return 'passed', reasons
