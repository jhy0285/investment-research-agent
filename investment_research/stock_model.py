"""Locked cross-sectional stock ranking, PIT backtest, grade and new-cash sizing.

Model ``stock_picker_momentum_lowvol_v1`` was fixed before looking at results
and is not tuned on this data (trial_count = 1). Its ingredients are standard
public-literature factors, which is prior knowledge and is disclosed as such.

Timing contract (no look-ahead):
  * signal month t uses only *complete* monthly closes t-12..t;
  * trades execute at the first open of month t+1 and are held until the first
    open of month t+2 (next observation, never the signal close);
  * a missing bar is never filled; affected months are excluded and counted.
"""
from __future__ import annotations

import calendar
from datetime import date, timedelta
from decimal import Decimal, ROUND_FLOOR
from random import Random
from zoneinfo import ZoneInfo

VERSION = 'stock_picker_momentum_lowvol_v1'
POLICY_VERSION = 'stock_pick_grade_v1'
ZERO, ONE = Decimal(0), Decimal(1)
PARAMS = dict(top_n=5, lookback=12, skip=1, sma=10, weight_momentum=Decimal(2) / 3,
              weight_low_vol=Decimal(1) / 3, sector_cap=2, min_eligible=10,
              validation_start='2019-01', recent_start='2023-01', bootstrap=2000, seed=0,
              trial_count=1)
GRADE_CAP = {'B': Decimal('0.20'), 'C': Decimal('0.05')}
MIN_MONTHS = dict(historical=24, validation=24, recent=12)


def shift(month, k):
    n = int(month[:4]) * 12 + int(month[5:]) - 1 + k
    return f'{n // 12:04d}-{n % 12 + 1:02d}'


def last_complete_month(as_of, timezone_name, close_time):
    """A month is complete one hour after the close of its last weekday."""
    local = as_of.astimezone(ZoneInfo(timezone_name))
    current = f'{local.year:04d}-{local.month:02d}'
    last = date(local.year, local.month, calendar.monthrange(local.year, local.month)[1])
    while last.weekday() >= 5:
        last -= timedelta(days=1)
    hour, minute = (int(x) for x in close_time.split(':'))
    if local.date() > last or (local.date() == last and (local.hour, local.minute) >= (hour + 1, minute)):
        return current
    return shift(current, -1)


def _stdev(values):
    mean = sum(values, ZERO) / len(values)
    return (sum(((v - mean) ** 2 for v in values), ZERO) / (len(values) - 1)).sqrt()


def factor_row(bars, t, p=PARAMS):
    """Factors from complete closes t-12..t only; None if any month is missing."""
    months = [shift(t, -k) for k in range(p['lookback'], -1, -1)]
    if any(m not in bars for m in months):
        return None
    closes = [bars[m][1] for m in months]
    returns = [closes[i] / closes[i - 1] - 1 for i in range(1, len(closes))]
    sma = sum(closes[-p['sma']:], ZERO) / p['sma']
    peak, worst = closes[0], ZERO
    for c in closes:
        peak = max(peak, c)
        worst = min(worst, c / peak - 1)
    return dict(close=closes[-1], momentum=closes[-1 - p['skip']] / closes[0] - 1,
                volatility=_stdev(returns), sma=sma, trend_gap=closes[-1] / sma - 1,
                trend=closes[-1] > sma, return_1m=returns[-1], drawdown_12m=worst)


def pct_ranks(values):
    """0 = worst, 1 = best; ties share the average rank."""
    items = sorted(values.items(), key=lambda kv: (kv[1], kv[0]))
    n, out, i = len(items), {}, 0
    while i < n:
        j = i
        while j + 1 < n and items[j + 1][1] == items[i][1]:
            j += 1
        for k in range(i, j + 1):
            out[items[k][0]] = Decimal(i + j) / 2 / (n - 1) if n > 1 else ONE
        i = j + 1
    return out


def rank_month(series, sectors, t, p=PARAMS):
    rows = {}
    for code, bars in series.items():
        row = factor_row(bars, t, p)
        if row is not None:
            rows[code] = dict(row, code=code, sector=sectors[code])
    if len(rows) < p['min_eligible']:
        return None
    momentum = pct_ranks({c: r['momentum'] for c, r in rows.items()})
    low_vol = pct_ranks({c: -r['volatility'] for c, r in rows.items()})
    for c, r in rows.items():
        r.update(momentum_pct=momentum[c], low_vol_pct=low_vol[c],
                 score=p['weight_momentum'] * momentum[c] + p['weight_low_vol'] * low_vol[c])
    order = sorted(rows.values(), key=lambda r: (-r['score'], r['code']))
    picks, per_sector = [], {}
    for i, r in enumerate(order, 1):
        r['rank'] = i
        if len(picks) >= p['top_n']:
            r['status'] = 'below_cutoff'
        elif not r['trend']:
            r['status'] = 'excluded_trend'
        elif per_sector.get(r['sector'], 0) >= p['sector_cap']:
            r['status'] = 'excluded_sector_cap'
        else:
            per_sector[r['sector']] = per_sector.get(r['sector'], 0) + 1
            r['status'] = 'selected'
            picks.append(r['code'])
    return dict(month=t, eligible=len(rows), rows=order, picks=picks)


def _open(bars, month):
    """Execution price of a month, or None when the bar or its open is unusable."""
    bar = bars.get(month)
    return bar[0] if bar is not None else None


def _period(entry, p):
    return ('historical' if entry < p['validation_start'] else
            'validation' if entry < p['recent_start'] else 'recent')


def backtest(series, index_bars, sectors, last_complete, cost_bps, p=PARAMS):
    """Monthly rebalanced equal-slot portfolio; unfilled slots stay in cash at 0%."""
    months = sorted({m for bars in series.values() for m in bars if m <= last_complete})
    if not months:
        return dict(months=[], signals={})
    cost = Decimal(cost_bps) / 10000
    rows, signals, previous = [], {}, None
    t = shift(months[0], p['lookback'])
    while t <= last_complete:
        ranked = rank_month(series, sectors, t, p)
        entry, exit_ = shift(t, 1), shift(t, 2)
        if ranked is None:
            previous = None
            t = shift(t, 1)
            continue
        signals[t] = ranked
        weight = ONE / p['top_n']
        record = dict(signal=t, entry=entry, exit=exit_, picks=list(ranked['picks']),
                      eligible=ranked['eligible'], cash=ONE - weight * len(ranked['picks']),
                      period=_period(entry, p))
        if entry not in index_bars or exit_ not in index_bars:
            record['status'] = 'pending'
            rows.append(record)
            previous = None
            t = shift(t, 1)
            continue
        missing = [c for c in ranked['picks'] if _open(series[c], entry) is None or _open(series[c], exit_) is None]
        if _open(index_bars, entry) is None or _open(index_bars, exit_) is None:
            missing.append('index')
        if missing:
            record.update(status='incomplete', missing=missing)
            rows.append(record)
            previous = None
            t = shift(t, 1)
            continue
        returns = {c: series[c][exit_][0] / series[c][entry][0] - 1 for c in ranked['picks']}
        gross = sum((weight * r for r in returns.values()), ZERO)
        target = {c: weight for c in ranked['picks']}
        if previous is None:
            turnover = sum(target.values(), ZERO)
        else:
            drift = {c: w * (1 + previous['returns'][c]) / (1 + previous['gross'])
                     for c, w in previous['weights'].items()}
            turnover = sum((abs(target.get(c, ZERO) - drift.get(c, ZERO)) for c in set(target) | set(drift)), ZERO)
        universe = [_open(series[c], exit_) / _open(series[c], entry) - 1 for c in (r['code'] for r in ranked['rows'])
                    if _open(series[c], entry) is not None and _open(series[c], exit_) is not None]
        record.update(status='realized', returns=returns, gross=gross, turnover=turnover,
                      net=gross - cost * turnover, net_double_cost=gross - 2 * cost * turnover,
                      equal_weight=sum(universe, ZERO) / len(universe),
                      index=index_bars[exit_][0] / index_bars[entry][0] - 1)
        rows.append(record)
        previous = dict(weights=target, returns=returns, gross=gross)
        t = shift(t, 1)
    return dict(months=rows, signals=signals)


def bootstrap_interval(values, p=PARAMS):
    if len(values) < 2:
        return None
    rng, n = Random(p['seed']), len(values)
    means = sorted(sum((values[rng.randrange(n)] for _ in range(n)), ZERO) / n for _ in range(p['bootstrap']))
    lo, hi = int(p['bootstrap'] * 0.025), int(p['bootstrap'] * 0.975) - 1
    return [means[lo], means[hi]]


def _path(returns):
    level, peak, worst = ONE, ONE, ZERO
    for r in returns:
        level *= 1 + r
        peak = max(peak, level)
        worst = min(worst, level / peak - 1)
    return level - 1, worst


def summarize(rows, key='net', p=PARAMS):
    rows = [r for r in rows if r['status'] == 'realized']
    if not rows:
        return dict(months=0)
    net = [r[key] for r in rows]
    ex_ew = [r[key] - r['equal_weight'] for r in rows]
    ex_index = [r[key] - r['index'] for r in rows]
    n = Decimal(len(rows))
    cumulative, mdd = _path(net)
    cum_index, _ = _path([r['index'] for r in rows])
    cum_ew, _ = _path([r['equal_weight'] for r in rows])
    annual = (1 + cumulative) ** (Decimal(12) / n) - 1 if cumulative > -1 else Decimal(-1)
    return dict(months=len(rows), start=rows[0]['entry'], end=rows[-1]['exit'],
                mean=sum(net, ZERO) / n, cumulative=cumulative, annualized=annual,
                annual_volatility=_stdev(net) * Decimal(12).sqrt() if len(net) > 1 else None,
                max_drawdown=mdd, cumulative_index=cum_index, cumulative_equal_weight=cum_ew,
                mean_excess_equal_weight=sum(ex_ew, ZERO) / n, mean_excess_index=sum(ex_index, ZERO) / n,
                hit_rate_equal_weight=Decimal(sum(1 for x in ex_ew if x > 0)) / n,
                hit_rate_index=Decimal(sum(1 for x in ex_index if x > 0)) / n,
                interval_excess_equal_weight=bootstrap_interval(ex_ew, p),
                interval_excess_index=bootstrap_interval(ex_index, p),
                average_turnover=sum((r['turnover'] for r in rows), ZERO) / n,
                average_cash=sum((r['cash'] for r in rows), ZERO) / n)


def evaluate(bt, p=PARAMS):
    rows = bt['months']
    periods = {name: summarize([r for r in rows if r['period'] == name], p=p)
               for name in ('historical', 'validation', 'recent')}
    pooled = [r for r in rows if r['period'] != 'recent']
    return dict(periods=periods, all=summarize(rows, p=p), pooled=summarize(pooled, p=p),
                pooled_double_cost=summarize(pooled, 'net_double_cost', p),
                recent_double_cost=summarize([r for r in rows if r['period'] == 'recent'], 'net_double_cost', p),
                excluded=dict(incomplete=sum(r['status'] == 'incomplete' for r in rows),
                              pending=sum(r['status'] == 'pending' for r in rows)))


def grade(evaluation, live=None):
    """Deterministic policy. A is unavailable: the universe is not point-in-time."""
    periods, reasons = evaluation['periods'], []
    short = [name for name, need in MIN_MONTHS.items() if periods[name].get('months', 0) < need]
    if short:
        return dict(grade='D', status='검증 표본 부족', reasons=['검증 표본 부족: ' + ', '.join(short)],
                    caps=['A 불가: 과거 시점별 종목 구성이 아닌 현재 작성 후보군'])
    positive = {name: periods[name]['mean_excess_equal_weight'] > 0 for name in periods}
    pooled = evaluation['pooled']
    interval = pooled['interval_excess_equal_weight']
    if all(positive.values()) and interval and interval[0] > 0:
        g = 'B'
        reasons.append('과거·독립검증·최근 세 구간 모두 같은 후보군 동일가중보다 월평균 수익이 높고, 과거+검증 구간 95% 재추출 구간 하단이 0보다 크다.')
    elif pooled['mean_excess_equal_weight'] > 0 and positive['recent']:
        g = 'C'
        reasons.append('과거+검증 평균과 최근 구간은 동일가중보다 좋지만 일부 구간이 음수이거나 95% 구간이 0을 포함한다.')
    else:
        g = 'D'
        reasons.append('최근 또는 전체 검증에서 같은 후보군 동일가중보다 낫다는 근거가 없다.')
    if g in ('B', 'C') and evaluation['pooled_double_cost']['mean_excess_equal_weight'] <= 0:
        g = 'C' if g == 'B' else 'D'
        reasons.append('거래비용을 두 배로 가정하면 초과수익이 사라져 한 단계 낮춘다.')
    status = {'B': '검증 통과', 'C': '조건부(소액)', 'D': '추천 중단'}[g]
    if live and live.get('months', 0) >= 6 and live['mean_excess_equal_weight'] < 0 and g != 'D':
        g = 'C' if g == 'B' else 'D'
        status = '경고: 실전 추천 성과 악화'
        reasons.append('일지에 기록된 실제 추천 6개월 이상이 동일가중보다 나빠 한 단계 낮춘다.')
    return dict(grade=g, status=status, reasons=reasons,
                caps=['A 불가: 2026년에 작성한 후보군이라 과거에 사라진 종목이 빠져 있다(생존 편향).',
                      '배당을 뺀 가격 수익률 기준이며 세금·환전 비용은 반영하지 않았다.'])


def allocate(picks, grades, prices, budget, fx, top_n=PARAMS['top_n']):
    """Equal slots per market sleeve, capped by grade; whole shares only."""
    markets = list(picks)
    sleeve = (Decimal(budget) / len(markets)).quantize(ONE, rounding=ROUND_FLOOR) if markets else ZERO
    lines, spent = [], ZERO
    for market in markets:
        g = grades[market]['grade']
        if g not in GRADE_CAP:
            continue
        slot = min(sleeve / top_n, GRADE_CAP[g] * Decimal(budget))
        for code in picks[market]:
            price = prices.get((market, code))
            if price is None:
                lines.append(dict(market=market, code=code, shares=0, amount_krw=ZERO, note='현재 가격 미확보'))
                continue
            rate = ONE if market == 'KR' else fx
            if rate is None:
                lines.append(dict(market=market, code=code, shares=0, amount_krw=ZERO, note='원/달러 환율 미확보'))
                continue
            unit = price * rate
            shares = int((slot / unit).to_integral_value(rounding=ROUND_FLOOR))
            amount = (unit * shares).quantize(ONE, rounding=ROUND_FLOOR)
            spent += amount
            lines.append(dict(market=market, code=code, shares=shares, amount_krw=amount, slot_krw=slot.quantize(ONE, rounding=ROUND_FLOOR),
                              unit_price_krw=unit, note=None if shares else '1주 가격이 배정액보다 큼'))
    return dict(budget_krw=Decimal(budget), sleeve_krw=sleeve, lines=lines, invested_krw=spent,
                cash_krw=Decimal(budget) - spent)


def evaluate_journal(entries, bt_by_market, series_by_market, index_by_market, p=PARAMS):
    """Score past *recorded* picks once their full holding window exists."""
    out = []
    for e in entries:
        market, signal = e['market'], e['signal_month']
        series, index = series_by_market.get(market, {}), index_by_market.get(market, {})
        entry, exit_ = shift(signal, 1), shift(signal, 2)
        row = dict(market=market, signal_month=signal, picks=e['picks'], entry=entry, exit=exit_)
        if entry not in index or exit_ not in index:
            out.append(dict(row, status='미성숙'))
            continue
        if (_open(index, entry) is None or _open(index, exit_) is None or
                any(_open(series.get(c, {}), entry) is None or _open(series.get(c, {}), exit_) is None for c in e['picks'])):
            out.append(dict(row, status='자료 부족'))
            continue
        weight = ONE / p['top_n']
        returns = {c: series[c][exit_][0] / series[c][entry][0] - 1 for c in e['picks']}
        gross = sum((weight * r for r in returns.values()), ZERO)
        bt = next((r for r in bt_by_market.get(market, {}).get('months', []) if r['signal'] == signal
                   and r['status'] == 'realized'), None)
        out.append(dict(row, status='성숙', returns=returns, gross=gross,
                        index=index[exit_][0] / index[entry][0] - 1,
                        equal_weight=bt['equal_weight'] if bt else None))
    return out


def live_summary(evaluated, market):
    rows = [r for r in evaluated if r['market'] == market and r['status'] == '성숙' and r['equal_weight'] is not None]
    seen, unique = set(), []
    for r in sorted(rows, key=lambda r: r['signal_month']):
        if r['signal_month'] not in seen:
            seen.add(r['signal_month'])
            unique.append(r)
    if not unique:
        return dict(months=0)
    n = Decimal(len(unique))
    return dict(months=len(unique), mean=sum((r['gross'] for r in unique), ZERO) / n,
                mean_excess_equal_weight=sum((r['gross'] - r['equal_weight'] for r in unique), ZERO) / n,
                mean_excess_index=sum((r['gross'] - r['index'] for r in unique), ZERO) / n)
