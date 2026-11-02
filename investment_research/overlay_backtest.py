"""Small, descriptive backtest for always-invested rules (cash exit, fixed mixes, rebalancing).

`pit_overlay_backtest_v1` is deliberately simple. It answers one question the entry-signal backtest cannot: how much
drawdown does a rule remove, and how much return does it give up, compared with holding the asset and with a
constant mix that has the same average exposure. It has no approval gate and no p-value; the output is a table to read.

Definitions (fixed here, not tuned):
- A rule decides at the close of an observation using only rows up to that observation. Trades execute at the NEXT
  observation's price, so the return between the decision and the execution is never earned.
- Cash earns nothing (an explicit, conservative assumption that understates cash; it is reported, not hidden).
- Cost is `cost_bps` of the notional traded at each rebalance, per side. No tax, no slippage beyond that, no leverage,
  no shorting. Prices are the series' own return definition (total return for KODEX, price lower bound for coins).
- Returns are measured between the series' own observations (weekly in the shipped histories); drawdown is the
  worst peak-to-trough over those observations and says nothing about moves inside a week.
"""

from bisect import bisect_right
from datetime import timedelta
from math import sqrt

from .sources import SourceError

VERSION = 'pit_overlay_backtest_v1'
TOLERANCE = 1e-9


class View:
    """What a rule may read at observation `i`: nothing later."""

    def __init__(self, times, prices, i):
        self._times, self._prices, self.i = times, prices, i
        self.time = times[i]

    def close(self, leg, j=None):
        j = self.i if j is None else j
        if j > self.i:
            raise SourceError('a rule cannot read an observation after the decision')
        return self._prices[leg][j]

    def sma(self, leg, observations):
        if self.i + 1 < observations:
            return None
        window = self._prices[leg][self.i + 1 - observations : self.i + 1]
        return sum(window) / observations

    def close_to_sma(self, leg, observations):
        mean = self.sma(leg, observations)
        return None if mean is None else self.close(leg) / mean - 1

    def trailing_return(self, leg, days, max_gap_days=7):
        target = self.time - timedelta(days=days)
        j = bisect_right(self._times, target, 0, self.i + 1) - 1
        if j < 0 or target - self._times[j] > timedelta(days=max_gap_days):
            return None
        return self.close(leg) / self._prices[leg][j] - 1


def _check(times, prices):
    if len(times) < 3 or any(b <= a for a, b in zip(times, times[1:])):
        raise SourceError('overlay backtest needs at least three strictly increasing observations')
    for leg, values in prices.items():
        if len(values) != len(times):
            raise SourceError('every leg must have a price at every common observation: ' + leg)
        if any(v <= 0 for v in values):
            raise SourceError('nonpositive price in ' + leg)


def align(datasets):
    """Common observations of several `investment-prices-v1` datasets. Missing rows are dropped, never filled."""
    from .decision_data import number, timestamp

    maps = {name: {timestamp(r['at']): float(number(r['value'])) for r in d['rows']} for name, d in datasets.items()}
    common = sorted(set.intersection(*[set(m) for m in maps.values()]))
    return (
        common,
        {name: [m[t] for t in common] for name, m in maps.items()},
        {name: len(m) - len(common) for name, m in maps.items()},
    )


def month_end_indices(times):
    return [
        i for i in range(len(times) - 1) if (times[i].year, times[i].month) != (times[i + 1].year, times[i + 1].month)
    ]


def run_overlay(times, prices, rule, *, cost_bps, start=0, decision='month_end'):
    """Run `rule(view) -> {leg: weight}` (weights >= 0, sum <= 1, the rest is cash) from observation `start`."""
    _check(times, prices)
    if decision not in ('month_end', 'every'):
        raise SourceError('decision must be month_end or every')
    cost = float(cost_bps) / 10000
    if not 0 <= cost < 1:
        raise SourceError('invalid cost')
    decide = (
        set(range(start, len(times) - 1))
        if decision == 'every'
        else {i for i in month_end_indices(times) if i >= start}
    )
    # The initial state is all cash at `start`; the first decision at `start` itself executes at start + 1.
    decide.add(start)
    cash, units = 1.0, {leg: 0.0 for leg in prices}
    pending, turnover, paid = None, 0.0, 0.0
    values, exposure, weights_log = [], [], []
    for i in range(start, len(times)):
        worth = {leg: units[leg] * prices[leg][i] for leg in prices}
        total = cash + sum(worth.values())
        if pending is not None:  # execute the previous observation's decision now
            traded = sum(abs(pending.get(leg, 0.0) * total - worth[leg]) for leg in prices)
            fee = cost * traded
            total -= fee
            paid, turnover = paid + fee, turnover + traded
            units = {leg: pending.get(leg, 0.0) * total / prices[leg][i] for leg in prices}
            cash = total - sum(units[leg] * prices[leg][i] for leg in prices)
            worth = {leg: units[leg] * prices[leg][i] for leg in prices}
            pending = None
        values.append(total)
        exposure.append(sum(worth.values()) / total)
        weights_log.append({leg: worth[leg] / total for leg in prices})
        if i in decide:
            target = rule(View(times, prices, i))
            if target is None:
                raise SourceError('a rule must decide at every decision observation')
            if any(w < -TOLERANCE for w in target.values()) or sum(target.values()) > 1 + TOLERANCE:
                raise SourceError('weights must be non-negative and sum to at most 1 (no leverage, no shorting)')
            if set(target) - set(prices):
                raise SourceError('rule named a leg that was not given')
            pending = target
    return _summary(times[start:], values, exposure, turnover, paid, weights_log)


def _summary(times, values, exposure, turnover, paid, weights_log):
    years = (times[-1] - times[0]).days / 365.25
    steps = [b / a - 1 for a, b in zip(values, values[1:])]
    per_year = len(steps) / years
    mean = sum(steps) / len(steps)
    variance = sum((s - mean) ** 2 for s in steps) / (len(steps) - 1)
    peak, worst, trough_at = values[0], 0.0, times[0]
    for t, v in zip(times, values):
        peak = max(peak, v)
        if v / peak - 1 < worst:
            worst, trough_at = v / peak - 1, t
    year_steps = round(per_year)
    rolling = (
        [values[k + year_steps] / values[k] - 1 for k in range(len(values) - year_steps)]
        if len(values) > year_steps
        else []
    )
    return dict(
        method_version=VERSION,
        start=times[0].date().isoformat(),
        end=times[-1].date().isoformat(),
        observations=len(values),
        total_return=values[-1] / values[0] - 1,
        cagr=(values[-1] / values[0]) ** (1 / years) - 1,
        volatility=sqrt(variance) * sqrt(per_year),
        max_drawdown=worst,
        max_drawdown_at=trough_at.date().isoformat(),
        worst_12m=min(rolling) if rolling else None,
        average_exposure=sum(exposure) / len(exposure),
        turnover_per_year=turnover / (sum(values) / len(values)) / years,
        cost_paid=paid,
        final_value=values[-1],
        values=values,
        weights=weights_log,
    )


# --- rules -----------------------------------------------------------------------------------------------------


def buy_and_hold(leg):
    return lambda view: {leg: 1.0}


def trend_cash_exit(leg, observations=43):
    """Hold the leg while its close is above its simple moving average of `observations`, else hold cash."""

    def rule(view):
        gap = view.close_to_sma(leg, observations)
        if gap is None:
            raise SourceError('not enough history for the moving average at the start observation')
        return {leg: 1.0 if gap > 0 else 0.0}

    return rule


def momentum_cash_exit(leg, days=364):
    """Hold the leg while its trailing `days` return is positive, else hold cash."""

    def rule(view):
        value = view.trailing_return(leg, days)
        if value is None:
            raise SourceError('not enough history for the trailing return at the start observation')
        return {leg: 1.0 if value > 0 else 0.0}

    return rule


def constant_mix(weights):
    """Fixed weights, restored at every decision (monthly in the shipped runs)."""
    return lambda view: dict(weights)
