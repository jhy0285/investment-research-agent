"""Overlay backtest on hand-worked paths. Synthetic numbers only; they say nothing about any market."""

from datetime import datetime, timedelta, timezone
import unittest

from investment_research.overlay_backtest import (
    align,
    buy_and_hold,
    constant_mix,
    month_end_indices,
    momentum_cash_exit,
    run_overlay,
    trend_cash_exit,
)
from investment_research.sources import SourceError

START = datetime(2026, 1, 5, tzinfo=timezone.utc)


def weekly(n):
    return [START + timedelta(days=7 * i) for i in range(n)]


class OverlayBacktestTests(unittest.TestCase):
    def test_a_trade_decided_at_an_observation_executes_at_the_next_one(self):
        # Decide at obs0, buy at obs1 (price 100); the move 100 -> 100 is not earned, then +10%, +10%, flat.
        r = run_overlay(weekly(5), {'A': [100, 100, 110, 121, 121]}, buy_and_hold('A'), cost_bps=0, decision='every')
        self.assertEqual([round(v, 10) for v in r['values']], [1, 1, 1.1, 1.21, 1.21])
        self.assertAlmostEqual(r['total_return'], 0.21)
        self.assertAlmostEqual(r['average_exposure'], 0.8)  # in cash at obs0 only

    def test_costs_are_charged_on_the_traded_notional_once(self):
        r = run_overlay(weekly(5), {'A': [100, 100, 110, 121, 121]}, buy_and_hold('A'), cost_bps=10, decision='every')
        self.assertAlmostEqual(r['final_value'], 0.999 * 1.21)  # buy 1.0 of notional at 10 bp; holding trades nothing
        self.assertAlmostEqual(r['cost_paid'], 0.001)
        self.assertAlmostEqual(
            r['turnover_per_year'] * ((weekly(5)[-1] - weekly(5)[0]).days / 365.25) * (sum(r['values']) / 5), 1.0
        )

    def test_an_exit_signal_seen_at_a_crash_cannot_avoid_it(self):
        # Hold while the close rose versus the previous close. The drop to 60 is seen at obs3 and sold at obs4 (66).
        def rose(view):
            return {'A': 1.0} if view.i and view.close('A') > view.close('A', view.i - 1) else {}

        prices = {'A': [100, 110, 121, 60, 66, 72.6]}
        r = run_overlay(weekly(6), prices, rose, cost_bps=0, decision='every')
        # Bought at obs2 (121), marked at 60 and 66, then in cash; the obs4 buy executes at obs5 (72.6) at no gain.
        self.assertEqual(
            [round(v, 6) for v in r['values']], [1, 1, 1, round(60 / 121, 6), round(66 / 121, 6), round(66 / 121, 6)]
        )
        self.assertAlmostEqual(r['max_drawdown'], 60 / 121 - 1)
        self.assertEqual(r['max_drawdown_at'], weekly(6)[3].date().isoformat())

    def test_rebalancing_restores_weights_and_charges_for_the_trades(self):
        prices = {'A': [100, 100, 200, 200], 'B': [100, 100, 100, 100]}
        free = run_overlay(weekly(4), prices, constant_mix({'A': 0.5, 'B': 0.5}), cost_bps=0, decision='every')
        self.assertEqual([round(v, 10) for v in free['values']], [1, 1, 1.5, 1.5])
        # After A doubles the mix is 2/3 and 1/3; restoring 50/50 trades 0.25 + 0.25 of a 1.5 portfolio.
        self.assertAlmostEqual(free['weights'][2]['A'], 0.5)  # logged after the trade; just before it A was 2/3
        self.assertAlmostEqual(free['weights'][3]['A'], 0.5)
        paid = run_overlay(weekly(4), prices, constant_mix({'A': 0.5, 'B': 0.5}), cost_bps=10, decision='every')
        # obs1: buy 1.0 -> 0.999. obs2: value 1.4985, restore 0.4995 of notional -> fee 0.0004995.
        self.assertAlmostEqual(paid['values'][2], 1.4985 - 0.0004995)

    def test_a_rule_cannot_read_after_the_decision_or_exceed_full_investment(self):
        prices = {'A': [100, 101, 102, 103, 104]}
        with self.assertRaisesRegex(SourceError, 'after the decision'):
            run_overlay(weekly(5), prices, lambda v: {'A': 1.0 if v.close('A', v.i + 1) > 0 else 0.0}, cost_bps=0)
        for bad in ({'A': 1.1}, {'A': -0.1}, {'A': 0.6, 'B': 0.6}, {'C': 0.5}):
            with self.subTest(bad), self.assertRaises(SourceError):
                run_overlay(weekly(5), {'A': prices['A'], 'B': prices['A']}, lambda v, b=bad: b, cost_bps=0)

    def test_moving_average_and_momentum_rules_use_only_past_rows(self):
        times = weekly(8)
        rising = {'A': [100, 101, 102, 103, 104, 105, 106, 107]}
        # SMA of the last 3 closes at obs2 is 101: close 102 is above it -> invested from the next observation.
        r = run_overlay(times, rising, trend_cash_exit('A', 3), cost_bps=0, start=2, decision='every')
        self.assertAlmostEqual(r['total_return'], 107 / 103 - 1)  # bought at obs3 (103)
        # A start before the average exists is refused, not padded.
        with self.assertRaisesRegex(SourceError, 'not enough history'):
            run_overlay(times, rising, trend_cash_exit('A', 3), cost_bps=0, start=1, decision='every')
        # 14-day trailing return at obs2 is 102/100 - 1 > 0.
        r2 = run_overlay(times, rising, momentum_cash_exit('A', 14), cost_bps=0, start=2, decision='every')
        self.assertAlmostEqual(r2['total_return'], 107 / 103 - 1)
        falling = {'A': [100, 99, 98, 97, 96, 95, 94, 93]}
        r3 = run_overlay(times, falling, momentum_cash_exit('A', 14), cost_bps=0, start=2, decision='every')
        self.assertEqual(r3['total_return'], 0)  # never invested: cash earns nothing by assumption

    def test_series_are_aligned_without_filling_gaps(self):
        t = weekly(4)

        def data(skip):
            return {'rows': [dict(at=x.isoformat(), value=str(100 + i)) for i, x in enumerate(t) if i != skip]}

        times, prices, dropped = align({'A': data(None), 'B': data(2)})
        self.assertEqual(len(times), 3)
        self.assertEqual(dropped, {'A': 1, 'B': 0})
        self.assertEqual(prices['A'], [100.0, 101.0, 103.0])  # the common dates only; nothing interpolated

    def test_month_end_decisions_use_the_last_observation_of_each_month(self):
        times = (
            [datetime(2026, 1, d, tzinfo=timezone.utc) for d in (5, 12, 19, 26)]
            + [datetime(2026, 2, d, tzinfo=timezone.utc) for d in (2, 9, 16, 23)]
            + [datetime(2026, 3, 2, tzinfo=timezone.utc)]
        )
        self.assertEqual(month_end_indices(times), [3, 7])

    def test_bad_inputs_are_refused(self):
        with self.assertRaises(SourceError):
            run_overlay(weekly(2), {'A': [1, 2]}, buy_and_hold('A'), cost_bps=0)
        with self.assertRaises(SourceError):
            run_overlay(weekly(4), {'A': [1, 2, 3]}, buy_and_hold('A'), cost_bps=0)
        with self.assertRaises(SourceError):
            run_overlay(weekly(4), {'A': [1, 2, 0, 3]}, buy_and_hold('A'), cost_bps=0)


if __name__ == '__main__':
    unittest.main()
