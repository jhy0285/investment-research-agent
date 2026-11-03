"""investment_cycle_v5: a person-written review is needed to BUY, not to record a zero-amount shadow."""

from copy import deepcopy
import unittest

from investment_research.decision_data import validate_plan
from investment_research.decision_journal import persist_review, record, review
from investment_research.decision_report import render_decision
from investment_research.investment_cycle import evaluate
from investment_research.sources import SourceError, _time
from investment_research.strategy_registry import view
from tests.test_shadow_tracking import GATE, SCHEDULE, WIN, ShadowCase, dated, judge, outcome_prices, register_strategy


def strip_review(plan, snapshot):
    c = plan['candidates'][0]
    for key in ('review', 'evidence_ids', 'counter_evidence_ids'):
        c.pop(key, None)


class UnreviewedShadowTests(ShadowCase):
    def registered(self, name, trials, mutate=strip_review):
        ledger = self.root / name
        plan, snapshot = dated(2026, 1, trial_count=trials)
        if mutate:
            mutate(plan, snapshot)
        register_strategy(ledger, plan)
        snapshot['strategy_registry'] = view(ledger, snapshot['as_of'])
        return ledger, plan, snapshot

    def test_v4_still_demands_the_review_and_v5_does_not(self):
        _, plan, snapshot = self.registered('a', 3)
        with self.assertRaisesRegex(SourceError, 'explicit scoped review'):
            evaluate(plan, snapshot, 'investment_cycle_v4')
        with self.assertRaisesRegex(SourceError, 'explicit scoped review'):
            validate_plan(plan, 'investment_cycle_v3')
        row = evaluate(plan, snapshot)['decisions'][0]
        self.assertEqual(row['reviewed'], False)
        self.assertEqual((row['action'], row['amount_krw']), ('신규 매수하지 않음', '0'))
        self.assertEqual((row['shadow']['tracked'], row['shadow']['track']), (True, 'candidate'))

    def test_a_buy_needs_the_review_even_when_every_other_condition_is_met(self):
        _, plan, snapshot = self.registered('b', 1)  # single-trial strategy that passes its backtest
        result = evaluate(plan, snapshot)
        row = result['decisions'][0]
        self.assertEqual(
            (row['verification'], row['grade'], row['action'], row['amount_krw']),
            ('passed', 'D', '신규 매수하지 않음', '0'),
        )
        self.assertTrue(any('사람이 쓴 경제적 검토' in b for b in row['blockers']))
        self.assertEqual(result['allocation']['investments'], [])
        self.assertEqual(result['allocation']['cash_krw'], '10000000')
        self.assertEqual(row['shadow']['track'], 'candidate')  # still a forward observation
        text = render_decision(result)
        self.assertIn('계획에 review를 쓰면 실제 매수 판단이 된다', text)
        # The same plan with a review is the v4 judgment: a real buy.
        reviewed_plan, reviewed_snapshot = dated(2026, 1, trial_count=1)
        bought = evaluate(reviewed_plan, reviewed_snapshot)['decisions'][0]
        self.assertEqual(
            (bought['reviewed'], bought['grade'], bought['action'], bought['amount_krw']),
            (True, 'A', '분할 매수', '4000000'),
        )

    def test_a_malformed_review_or_an_event_candidate_without_one_is_still_refused(self):
        _, plan, snapshot = self.registered('c', 3, mutate=None)
        broken = deepcopy(plan)
        broken['candidates'][0]['review'] = dict(reviewer='someone', at=broken['candidates'][0]['review']['at'])
        with self.assertRaisesRegex(SourceError, 'explicit scoped review'):
            validate_plan(broken)
        event = deepcopy(plan)
        event['candidates'][0]['mode'] = 'event'
        event['candidates'][0].pop('review')
        with self.assertRaisesRegex(SourceError, 'explicit scoped review'):
            validate_plan(event)

    def test_v5_matches_v4_whenever_the_review_is_present(self):
        def uptrend(plan, snapshot):
            for i, r in enumerate(plan['candidates'][0]['prices']['rows']):
                r['value'] = str(100 * 1.01**i)

        for name, trials, mutate in [('approved', 1, None), ('multi', 3, None), ('failed', 1, uptrend)]:
            with self.subTest(name):
                ledger = self.root / ('eq-' + name)
                plan, snapshot = dated(2026, 1, trial_count=trials)
                if mutate:
                    mutate(plan, snapshot)
                register_strategy(ledger, plan)
                snapshot['strategy_registry'] = view(ledger, snapshot['as_of'])
                old, new = evaluate(plan, snapshot, 'investment_cycle_v4'), evaluate(
                    plan, snapshot, 'investment_cycle_v5'
                )
                strip = lambda r: [{k: v for k, v in row.items() if k != 'reviewed'} for row in r['decisions']]
                self.assertEqual(strip(new), strip(old))
                self.assertEqual(new['allocation'], old['allocation'])

    def test_a_promoted_strategy_waits_for_a_review_before_it_buys(self):
        ledger = self.ledger()
        data = self.run_schedule(ledger, [WIN] * 4, mutate=strip_review)  # four unreviewed shadow judgments
        result = review(ledger, data, '2026-09-15T00:00:00+00:00')
        persist_review(ledger, result)
        gate = result['strategies']['authored_cycle/v1/shadow_synthetic']['promotion']
        self.assertTrue(gate['eligible'])
        waiting = judge(ledger, 2026, 11, mutate=strip_review, persist=False)[0]['decisions'][0]
        self.assertEqual(
            (waiting['verification'], waiting['action'], waiting['amount_krw']),
            ('shadow_promoted', '신규 매수하지 않음', '0'),
        )
        self.assertTrue(
            waiting['shadow']['tracked']
        )  # the record keeps growing, so a bad stretch can still withdraw it
        bought = judge(ledger, 2026, 11, persist=False)[0]['decisions'][0]
        self.assertEqual((bought['reviewed'], bought['action'], bought['amount_krw']), (True, '소액 매수', '500000'))

    def test_recording_refuses_a_buy_that_claims_no_review_and_accepts_unreviewed_shadows(self):
        ledger = self.ledger()
        shadow, _, _ = judge(ledger, 2026, 1, mutate=strip_review)  # recorded without complaint
        self.assertEqual(shadow['decisions'][0]['reviewed'], False)
        plan, snapshot = dated(2026, 3, trial_count=1, strategy_id='bought_cycle')  # another strategy: no redefinition
        bought = evaluate(plan, snapshot)
        self.assertEqual(bought['decisions'][0]['action'], '분할 매수')
        forged = deepcopy(bought)
        forged['decisions'][0]['reviewed'] = False
        with self.assertRaisesRegex(SourceError, 'person-written review'):
            record(ledger, forged, now=_time(snapshot['as_of']))
        missing = deepcopy(bought)
        del missing['decisions'][0]['reviewed']
        with self.assertRaisesRegex(SourceError, 'person-written review'):
            record(ledger, missing, now=_time(snapshot['as_of']))
        record(ledger, bought, now=_time(snapshot['as_of']))
        scored = review(ledger, outcome_prices(plan, [(2026, 1, WIN), (2026, 3, WIN)]), '2026-05-15T00:00:00+00:00')
        self.assertTrue(scored['shadow_outcomes'])  # unreviewed shadow rows are scored like any other


if __name__ == '__main__':
    unittest.main()
