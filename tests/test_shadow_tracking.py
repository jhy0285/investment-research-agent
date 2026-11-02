"""Shadow tracking (investment_cycle_v4): zero-amount judgments, pre-registration and the one-look promotion gate.

Synthetic fixtures only; every HTTP call is forbidden. Expected numbers are worked out by hand:
with a 10 bp cost per side the net return of buying at 100 and selling at E is E*0.999/(100*1.001) - 1, and the
benchmark stays flat at 100, so the excess return over the benchmark is exactly (E - 100)/100 * 0.999/1.001.
"""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
from io import StringIO
from math import comb
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from investment_research.__main__ import main
from investment_research.backtest import lower_confidence_bound
from investment_research.decision_data import digest, load, save
from investment_research.decision_journal import feedback, persist_review, record, review
from investment_research.decision_report import render_decision, render_review
from investment_research.investment_cycle import evaluate, replay_cycle, run_cycle
from investment_research.sources import SourceError, _time
from investment_research.strategy_registry import discard, read_chain, register, register_many, view
from tests.test_investment_cycle import AT, experiment

APPLICATION = dict(asset_id='US_EQUITY', instrument_id='SYNTHETIC_EQUITY', benchmark_instrument_id='SYNTHETIC_MARKET')
SOURCE = {'class': '자체 가설', 'note': '합성 fixture의 가설이며 시장 근거가 아니다.'}
# Registration policy numbers: look at the first 4 independent outcomes, the last 2 of them must be positive.
GATE = dict(minimum_historical=4, minimum_live=2)
REGISTERED = datetime(2025, 12, 31, tzinfo=timezone.utc)
SCHEDULE = [(2026, 1), (2026, 3), (2026, 5), (2026, 7), (2026, 9), (2026, 11), (2027, 1), (2027, 3)]
WIN, LOSS = 110, 89  # exit value of an entry at 100


def excess_of(end):
    """Excess return over a flat benchmark with 10 bp per side, from the closed form."""
    return (Decimal(end) - 100) / 100 * Decimal('0.999') / Decimal('1.001')


def dated(year, month, day=7, trial_count=3, strategy_id=None):
    """The synthetic experiment judged on a given day, with the current signal on."""
    plan, snapshot = experiment()
    c = plan['candidates'][0]
    c['strategy']['trial_count'] = trial_count
    if strategy_id:
        c['strategy']['id'] = strategy_id
    month_at = f'{year}-{month:02d}-01T00:00:00+00:00'
    at = f'{year}-{month:02d}-{day:02d}T12:00:00+09:00'
    c['review']['at'] = at
    c['quote'].update(at=month_at, known_at=month_at)
    for f in c['features']:
        if f['observed_at'] == month_at and f['name'] == 'demand':
            f['value'] = '1'
    snapshot['as_of'] = at
    for e in snapshot['evidence']:
        e.update(observed_at=month_at[:10], retrieved_at=f'{year}-{month:02d}-{day:02d}T00:00:00+00:00')
    return plan, snapshot


def outcome_prices(plan, ends):
    """Outcome datasets: each (year, month, E) enters at 100 on the 8th and exits at E on the 8th of the next month."""
    data = deepcopy([plan['candidates'][0]['prices'], plan['candidates'][0]['benchmark']])
    for d in data:
        d['retrieved_at'] = '2028-01-01T00:00:00+00:00'
        for year, month, end in ends:
            ny, nm = (year, month + 1) if month < 12 else (year + 1, 1)
            for y, m, value in ((year, month, 100), (ny, nm, end if d['asset_id'] == 'US_EQUITY' else 100)):
                at = f'{y}-{m:02d}-08T00:00:00+00:00'
                d['rows'].append(dict(at=at, known_at=at, value=str(value)))
        d['rows'].sort(key=lambda r: r['at'])
    return data


def register_strategy(ledger, plan, *, now=REGISTERED, policy=GATE, strategy_id=None, application=None):
    strategy = deepcopy(plan['candidates'][0]['strategy'])
    if strategy_id:
        strategy['id'] = strategy_id
    return register(
        ledger,
        dict(kind='testable', strategy=strategy, application=application or APPLICATION, source=SOURCE),
        now=now,
        policy=policy,
    )


def judge(ledger, year, month, *, day=7, trial_count=3, strategy_id=None, mutate=None, persist=True):
    plan, snapshot = dated(year, month, day, trial_count, strategy_id)
    if mutate:
        mutate(plan, snapshot)
    snapshot['strategy_feedback'] = feedback(ledger, snapshot['as_of'])
    snapshot['strategy_registry'] = view(ledger, snapshot['as_of'])
    result = evaluate(plan, snapshot)
    if persist:
        record(ledger, result, now=_time(snapshot['as_of']))
    return result, plan, snapshot


class ShadowCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        p = patch('socket.socket.connect', side_effect=AssertionError('offline shadow experiment'))
        p.start()
        self.addCleanup(p.stop)

    def ledger(self, name='journal', fillers=0, filler_at=REGISTERED, policy=GATE):
        """A journal with the main strategy registered, plus `fillers` other registered strategies."""
        path = self.root / name
        plan, _ = dated(2026, 1)
        register_strategy(path, plan, policy=policy)
        for i in range(fillers):
            register_strategy(path, plan, strategy_id=f'filler_{i}', now=filler_at, policy=policy)
        return path

    def run_schedule(self, ledger, ends, **kw):
        """Judge on the schedule with one shadow judgment per entry; return the matching outcome datasets."""
        entries, plan = [], None
        for (year, month), end in zip(SCHEDULE, ends):
            _, plan, _ = judge(ledger, year, month, **kw)
            entries.append((year, month, end))
        return outcome_prices(plan, entries)

    def gate_of(self, result, strategy='authored_cycle'):
        return result['strategies'][strategy + '/v1/shadow_synthetic']

    def assertClose(self, a, b, tolerance='1e-18'):
        self.assertLess(abs(Decimal(a) - Decimal(b)), Decimal(tolerance), (a, b))


class RegistryTests(ShadowCase):
    def test_registration_is_stamped_by_the_clock_and_a_changed_definition_needs_a_new_version(self):
        plan, _ = dated(2026, 1)
        ledger = self.root / 'journal'
        record_, created = register_strategy(ledger, plan)
        self.assertTrue(created)
        self.assertEqual(record_['registered_at'], REGISTERED.isoformat())
        again, created = register_strategy(ledger, plan, now=datetime(2026, 1, 5, tzinfo=timezone.utc))
        self.assertFalse(created)
        self.assertEqual(again['registered_at'], REGISTERED.isoformat())  # the first stamp stands
        changed = deepcopy(plan)
        changed['candidates'][0]['strategy']['conditions'][0]['value'] = '2'
        with self.assertRaisesRegex(SourceError, 'without a new version'):
            register_strategy(ledger, changed)
        self.assertEqual(len(read_chain(ledger)), 1)

    def test_registration_input_is_validated(self):
        plan, _ = dated(2026, 1)
        ledger = self.root / 'journal'
        with self.assertRaisesRegex(SourceError, 'frozen after'):
            register_strategy(ledger, plan, now=datetime(2012, 1, 1, tzinfo=timezone.utc))  # locked_at is 2013
        with self.assertRaisesRegex(SourceError, 'source class'):
            register(ledger, dict(kind='testable', strategy=plan['candidates'][0]['strategy'], application=APPLICATION))
        with self.assertRaisesRegex(SourceError, 'separate benchmark'):
            register_strategy(ledger, plan, application=dict(APPLICATION, benchmark_instrument_id='SYNTHETIC_EQUITY'))
        with self.assertRaisesRegex(SourceError, 'must link its parent'):
            register_strategy(ledger, plan)
            second = deepcopy(plan)
            second['candidates'][0]['strategy']['version'] = 'v2'
            register_strategy(ledger, second)
        with self.assertRaisesRegex(SourceError, 'minimums'):
            register_strategy(self.root / 'other', plan, policy=dict(minimum_historical=3, minimum_live=5))
        self.assertEqual(len(read_chain(self.root / 'other')), 0)

    def test_chain_breaks_when_an_entry_is_removed_edited_or_reordered(self):
        ledger = self.ledger(fillers=2)
        path = ledger / 'chain.jsonl'
        lines = path.read_text(encoding='utf-8').splitlines()
        self.assertEqual(len(read_chain(ledger)), 3)
        for name, damaged in {
            'removed': [lines[0], lines[2]],
            'edited': [lines[0].replace('"register"', '"discard"'), *lines[1:]],
            'reordered': [lines[1], lines[0], lines[2]],
        }.items():
            with self.subTest(name):
                path.write_text('\n'.join(damaged) + '\n', encoding='utf-8')
                with self.assertRaisesRegex(SourceError, 'chain'):
                    read_chain(ledger)
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        self.assertEqual(len(read_chain(ledger)), 3)

    def test_a_missing_or_altered_registration_file_is_detected(self):
        ledger = self.ledger()
        stored = next((ledger / 'registrations').glob('*.json'))
        text = stored.read_text(encoding='utf-8')
        stored.write_text(text.replace('"자체 가설"', '"학술·공식"'), encoding='utf-8')
        with self.assertRaisesRegex(SourceError, 'does not match'):
            view(ledger, '2026-06-01T00:00:00+00:00')
        stored.unlink()
        with self.assertRaisesRegex(SourceError, 'missing'):
            view(ledger, '2026-06-01T00:00:00+00:00')

    def test_family_size_counts_discarded_strategies_but_not_untestable_ones_and_respects_the_time(self):
        ledger = self.ledger(fillers=2, filler_at=datetime(2026, 3, 1, tzinfo=timezone.utc))
        register(
            ledger,
            dict(
                kind='untestable',
                id='covered_call_income',
                hypothesis='커버드콜 ETF의 분배금을 포함한 총수익이 지수보다 낫다.',
                reason='이 시스템에는 커버드콜 ETF의 가격 이력 제공자가 없다.',
                required=['발행사 분배금 포함 총수익 이력'],
                source=SOURCE,
            ),
            now=datetime(2026, 3, 2, tzinfo=timezone.utc),
        )
        discard(ledger, 'filler_0', 'v1', '합성 시험 후 폐기', now=datetime(2026, 4, 1, tzinfo=timezone.utc))
        early, late = view(ledger, '2026-02-01T00:00:00+00:00'), view(ledger, '2026-06-01T00:00:00+00:00')
        self.assertEqual((early['family_size'], late['family_size']), (1, 3))
        self.assertEqual(late['strategies']['filler_0/v1']['status'], 'discarded')
        self.assertEqual(late['strategies']['untestable/covered_call_income']['status'], 'untestable')
        # The chain head moves with every entry, so a judgment that stores it pins the registry state.
        self.assertNotEqual(early['chain_head_sha256'], late['chain_head_sha256'])
        with self.assertRaisesRegex(SourceError, 'no registered strategy'):
            discard(ledger, 'absent', 'v1', 'x')

    def test_free_text_with_unicode_line_separators_cannot_break_the_chain(self):
        # str.splitlines() would cut a line at these characters and make the whole journal unreadable.
        ledger = self.ledger()
        reason = 'line\u2028separator\u0085and\x1cmore'
        discard(ledger, 'authored_cycle', 'v1', reason, now=datetime(2026, 1, 2, tzinfo=timezone.utc))
        events = read_chain(ledger)
        self.assertEqual([e['kind'] for e in events], ['register', 'discard'])
        self.assertEqual(events[1]['reason'], reason)
        self.assertEqual(view(ledger, '2026-06-01T00:00:00+00:00')['strategies']['authored_cycle/v1']['reason'], reason)

    def test_a_library_is_registered_entirely_or_not_at_all(self):
        plan, _ = dated(2026, 1)
        good = dict(
            kind='testable',
            strategy=deepcopy(plan['candidates'][0]['strategy']),
            application=APPLICATION,
            source=SOURCE,
        )
        bad = deepcopy(good)
        bad['strategy']['id'] = 'second_one'
        bad['application'] = dict(APPLICATION, benchmark_instrument_id=APPLICATION['instrument_id'])
        ledger = self.root / 'journal'
        with self.assertRaisesRegex(SourceError, 'separate benchmark'):
            register_many(ledger, [good, bad], now=REGISTERED)
        self.assertEqual(read_chain(ledger), [])
        self.assertEqual(
            list((ledger / 'registrations').glob('*.json')) if (ledger / 'registrations').exists() else [], []
        )
        self.assertEqual(register_many(ledger, [good], now=REGISTERED), [True])
        self.assertEqual(register_many(ledger, [good], now=REGISTERED), [False])
        self.assertEqual(len(read_chain(ledger)), 1)

    def test_the_multi_trial_blocker_text_that_saved_results_carry_is_pinned(self):
        # Shadow eligibility tells the multi-trial blocker from definition blockers by this exact text, and v1-v3
        # results already saved on disk contain it, so it must not be reworded.
        from investment_research.backtest import TRIAL_BLOCKER

        self.assertEqual(TRIAL_BLOCKER, '여러 조건을 탐색한 전략이다. 새 미래 검증 전에는 강한 승인이 불가하다.')

    def test_the_lower_bound_is_not_reported_when_the_tail_cannot_be_resolved(self):
        one, zero = Decimal(1), Decimal(0)
        # Resample means of [0, 1] are 0 (25%), 0.5 (50%) or 1 (25%).
        self.assertEqual(lower_confidence_bound([zero, one], Decimal('0.1'), 10000), 0)
        self.assertEqual(lower_confidence_bound([zero, one], Decimal('0.5'), 10000), Decimal('0.5'))
        self.assertEqual(lower_confidence_bound([one, one, one], Decimal('0.025'), 1000), 1)
        # 0.0001 of 10,000 resamples is one draw: an unresolved tail would be a made-up number.
        self.assertIsNone(lower_confidence_bound([zero, one], Decimal('0.0001'), 10000))
        self.assertIsNone(lower_confidence_bound([one], Decimal('0.5'), 10000))


class ShadowDecisionTests(ShadowCase):
    def test_a_signal_the_gate_does_not_accept_becomes_a_zero_amount_shadow(self):
        ledger = self.ledger()
        result, _, _ = judge(ledger, 2026, 1)
        row = result['decisions'][0]
        self.assertEqual((row['grade'], row['action'], row['amount_krw']), ('C', '신규 매수하지 않음', '0'))
        self.assertEqual(row['verification'], 'insufficient')
        shadow = row['shadow']
        self.assertEqual((shadow['tracked'], shadow['track'], shadow['amount_krw']), (True, 'candidate', '0'))
        # It never reaches the allocation or the cash.
        self.assertEqual(result['allocation']['investments'], [])
        self.assertEqual(result['allocation']['cash_krw'], '10000000')
        self.assertEqual(result['strategy_registry']['family_size'], 1)
        self.assertEqual(result['strategy_registry']['chain_head_sha256'], read_chain(ledger)[0]['line_sha256'])

    def scenarios(self):
        def uptrend(plan, snapshot):
            for i, r in enumerate(plan['candidates'][0]['prices']['rows']):
                r['value'] = str(Decimal(100) * Decimal('1.01') ** i)

        def held_uptrend(plan, snapshot):
            uptrend(plan, snapshot)
            plan['candidates'][0]['held'] = True

        def thin_history(plan, snapshot):
            for name in ('minimum_historical', 'minimum_validation', 'minimum_recent'):
                plan['policy'][name] = 10000

        def no_signal(plan, snapshot):
            for f in plan['candidates'][0]['features']:
                if f['name'] == 'demand' and f['observed_at'].startswith('2026-01-01'):
                    f['value'] = '0'
            for e in snapshot['evidence']:
                if e['id'] == 'E_DEMAND':
                    e['value'] = '0'

        def broken_thesis(plan, snapshot):
            plan['candidates'][0]['held'] = True
            for f in plan['candidates'][0]['features']:
                if f['name'] == 'broken' and f['observed_at'].startswith('2026-01-01'):
                    f['value'] = '1'
            for e in snapshot['evidence']:
                if e['id'] == 'E_RISK':
                    e['value'] = '1'

        return {
            'approved': (1, None),
            'multi_trial': (3, None),
            'thin_history': (1, thin_history),
            'no_signal': (3, no_signal),
            'failed_backtest': (1, uptrend),
            'failed_backtest_held': (1, held_uptrend),
            'broken_thesis_held': (1, broken_thesis),
        }

    def registered_scenario(self, name, trials, mutate):
        """The plan and snapshot of a scenario, with exactly the strategy being judged registered."""
        path = self.root / name
        plan, snapshot = dated(2026, 1, trial_count=trials)
        if mutate:
            mutate(plan, snapshot)
        register_strategy(path, plan)
        snapshot['strategy_registry'] = view(path, snapshot['as_of'])
        return plan, snapshot

    def test_v4_equals_v3_for_every_case_except_for_the_shadow_mark(self):
        # The rules a saved judgment relied on must not move: only the zero-amount mark is new.
        for name, (trials, mutate) in self.scenarios().items():
            with self.subTest(name):
                plan, snapshot = self.registered_scenario(name, trials, mutate)
                old = evaluate(plan, snapshot, 'investment_cycle_v3')
                new = evaluate(plan, snapshot, 'investment_cycle_v4')
                strip = lambda result: [{k: v for k, v in row.items() if k != 'shadow'} for row in result['decisions']]
                self.assertEqual(strip(new), strip(old))
                self.assertEqual(new['allocation'], old['allocation'])
                self.assertNotIn('strategy_registry', old)

    def test_tracking_covers_exactly_the_signals_the_gate_declined_to_buy(self):
        expected = {
            'approved': None,  # bought, nothing to shadow
            'multi_trial': 'candidate',
            'thin_history': 'candidate',
            'no_signal': None,
            'failed_backtest': 'control',
            'failed_backtest_held': 'control',
            'broken_thesis_held': None,
        }
        for name, (trials, mutate) in self.scenarios().items():
            with self.subTest(name):
                plan, snapshot = self.registered_scenario('c-' + name, trials, mutate)
                row = evaluate(plan, snapshot)['decisions'][0]
                shadow = row.get('shadow')
                self.assertEqual(shadow['track'] if shadow else None, expected[name], row['action'])

    def test_signals_that_are_unverified_stale_or_not_comparable_are_not_shadowed(self):
        def drop_quote(plan, snapshot):
            snapshot['evidence'] = [e for e in snapshot['evidence'] if e['id'] != 'E_QUOTE']

        def stale_quote(plan, snapshot):
            plan['candidates'][0]['max_price_age_days'] = 0
            plan['candidates'][0]['quote'].update(at='2025-12-01T00:00:00+00:00', known_at='2025-12-01T00:00:00+00:00')

        def mismatched_unit(plan, snapshot):
            snapshot['evidence'][0]['unit'] = 'percent'

        def survivors_only(plan, snapshot):
            plan['candidates'][0]['prices']['survivorship'] = 'current_survivors'

        def price_condition_unmet(plan, snapshot):
            plan['candidates'][0]['strategy']['price_conditions'][0]['value'] = '5'  # price_multiple is 10

        ledger = self.ledger()
        for name, mutate in [
            ('quote evidence missing', drop_quote),
            ('quote stale', stale_quote),
            ('current number does not match its source', mismatched_unit),
            ('comparison undefined', survivors_only),
            ('price condition unmet', price_condition_unmet),
        ]:
            with self.subTest(name):
                # The registration must describe the strategy that is judged.
                path = self.root / ('journal-' + name.replace(' ', '-'))
                plan, snapshot = dated(2026, 1)
                mutate(plan, snapshot)
                register_strategy(path, plan)
                snapshot['strategy_registry'] = view(path, snapshot['as_of'])
                row = evaluate(plan, snapshot)['decisions'][0]
                self.assertNotIn('shadow', row, row['blockers'])
        self.assertIn('shadow', judge(ledger, 2026, 1, persist=False)[0]['decisions'][0])  # the control case

    def test_unregistered_changed_discarded_or_misapplied_strategies_are_not_tracked(self):
        def reason_for(setup, edit=None):
            path = self.root / ('j' + str(len(list(self.root.iterdir()))))
            plan, snapshot = dated(2026, 1)
            setup(path, plan)
            if edit:
                edit(plan)
            snapshot['strategy_registry'] = view(path, snapshot['as_of'])
            shadow = evaluate(plan, snapshot)['decisions'][0]['shadow']
            self.assertFalse(shadow['tracked'])
            return shadow['reason']

        self.assertIn('사전 등록(invest strategy register)이 없어', reason_for(lambda path, plan: None))
        self.assertIn(
            '정의가 달라져',
            reason_for(register_strategy, lambda p: p['candidates'][0]['strategy'].update(cost_bps_per_side='11')),
        )
        self.assertIn(
            '적용 대상',
            reason_for(
                lambda path, plan: register_strategy(path, plan, application=dict(APPLICATION, asset_id='OTHER'))
            ),
        )

        def retire(path, plan):
            register_strategy(path, plan)
            discard(path, 'authored_cycle', 'v1', '합성 시험 폐기', now=datetime(2026, 1, 2, tzinfo=timezone.utc))

        self.assertIn('폐기한 전략', reason_for(retire))
        # Without any registry attached (no journal) the signal is also left unrecorded.
        plan, snapshot = dated(2026, 1)
        self.assertIn('등록부가 연결되지 않아', evaluate(plan, snapshot)['decisions'][0]['shadow']['reason'])

    def test_a_registration_made_after_the_judgment_does_not_count_for_it(self):
        plan, _ = dated(2026, 1)
        ledger = self.root / 'journal'
        register_strategy(ledger, plan, now=datetime(2026, 2, 1, tzinfo=timezone.utc))
        january = judge(ledger, 2026, 1, persist=False)[0]['decisions'][0]['shadow']
        march = judge(ledger, 2026, 3, persist=False)[0]['decisions'][0]['shadow']
        self.assertFalse(january['tracked'])
        self.assertTrue(march['tracked'])

    def test_shadow_record_invariants_are_enforced_when_recording(self):
        ledger = self.ledger()
        result, _, _ = judge(ledger, 2026, 1, persist=False)
        at = _time(result['as_of'])

        def variant(edit):
            damaged = deepcopy(result)
            edit(damaged)
            return damaged

        for name, damaged in {
            'amount': variant(lambda d: d['decisions'][0].update(amount_krw='1000')),
            'buy action': variant(lambda d: d['decisions'][0].update(action='소액 매수')),
            'tracked amount': variant(lambda d: d['decisions'][0]['shadow'].update(amount_krw='5')),
            'older version': variant(lambda d: d.update(method_version='investment_cycle_v3')),
        }.items():
            with self.subTest(name), self.assertRaisesRegex(SourceError, 'shadow record'):
                record(ledger, damaged, now=at)
        record(ledger, result, now=at)
        self.assertEqual(len(list((ledger / 'decisions').glob('*.json'))), 1)

    def test_the_report_shows_shadow_records_apart_from_the_allocation(self):
        ledger = self.ledger()
        result, _, _ = judge(ledger, 2026, 1, persist=False)
        text = render_decision(result)
        self.assertIn('## 섀도 기록 (금액 0, 실제 배분에 들어가지 않음)', text)
        self.assertIn('승격 후보', text)
        self.assertIn('사전 등록한 시험 후보는 1개입니다', text)
        section = text.split('## 섀도 기록')[1].split('\n## ')[0]
        self.assertIsNone(re.search(r'\d원', section))  # no money amounts in the shadow section
        self.assertIn('현금 유지: **10,000,000원**', text)
        # A judgment without shadow records reads as before.
        plan, snapshot = dated(2026, 1, trial_count=1)
        plain = render_decision(evaluate(plan, snapshot))
        self.assertNotIn('섀도', plain)


class ShadowReviewTests(ShadowCase):
    def test_shadow_outcomes_are_scored_apart_from_real_buys(self):
        ledger = self.ledger('journal')
        bought, plan_a, _ = judge(ledger, 2026, 1, trial_count=1, strategy_id='bought_cycle')
        self.assertEqual(bought['decisions'][0]['action'], '분할 매수')
        shadow, _, _ = judge(ledger, 2026, 3)
        self.assertEqual(shadow['decisions'][0]['shadow']['track'], 'candidate')
        data = outcome_prices(plan_a, [(2026, 1, WIN), (2026, 3, LOSS)])
        result = review(ledger, data, '2026-05-15T00:00:00+00:00')
        # Real: one buy, scored as before.
        real = [o for o in result['outcomes'] if o['horizon'] == '1m']
        self.assertEqual(len(real), 1)
        self.assertEqual(real[0]['strategy_id'], 'bought_cycle')
        self.assertClose(
            real[0]['return_'], Decimal('110') * Decimal('0.999') / (Decimal('100') * Decimal('1.001')) - 1
        )
        self.assertEqual(result['grade_statistics']['1m']['A']['synthetic']['count'], 1)
        # The shadow's grade is C, but it must not appear in the real grade statistics.
        self.assertEqual(result['grade_statistics']['1m']['C']['synthetic']['count'], 0)
        self.assertEqual({o['strategy_id'] for o in result['shadow_outcomes']}, {'authored_cycle'})
        one_month = next(o for o in result['shadow_outcomes'] if o['horizon'] == '1m')
        self.assertEqual(
            (one_month['state'], one_month['independent'], one_month['track']), ('completed', True, 'candidate')
        )
        self.assertClose(one_month['excess_return'], excess_of(LOSS))
        self.assertIn('금액 0', one_month['reason'])
        shadow_state = self.gate_of(result)
        self.assertEqual(shadow_state['source'], 'shadow')
        self.assertEqual(shadow_state['stats']['count'], 1)
        self.assertEqual(result['strategies']['authored_cycle/v1/synthetic']['stats']['count'], 0)  # never a real buy
        self.assertEqual(result['strategies']['bought_cycle/v1/synthetic']['stats']['count'], 1)
        text = render_review(result)
        self.assertIn('## 섀도 기록 평가', text)
        self.assertIn('실제 매수 통계와 섞지 않고', text)

    def test_a_journal_without_shadow_records_reviews_exactly_as_before(self):
        ledger = self.root / 'journal'
        plan, snapshot = dated(2026, 1, trial_count=1)
        record(ledger, evaluate(plan, snapshot), now=_time(snapshot['as_of']))
        result = review(ledger, outcome_prices(plan, [(2026, 1, WIN)]), '2026-05-15T00:00:00+00:00')
        self.assertNotIn('shadow_outcomes', result)
        self.assertNotIn('shadow_limitation', result)
        self.assertFalse([k for k in result['strategies'] if '/shadow_' in k])
        self.assertNotIn('섀도', render_review(result))

    def test_independence_is_per_strategy_and_overlapping_shadows_are_not_counted(self):
        ledger = self.ledger()
        plan, _ = dated(2026, 1)
        register_strategy(ledger, plan, strategy_id='second_cycle')
        for day, strategy in [(5, None), (5, 'second_cycle'), (6, None)]:
            judge(ledger, 2026, 1, day=day, strategy_id=strategy)
        data = outcome_prices(plan, [(2026, 1, WIN)])
        result = review(ledger, data, '2026-05-15T00:00:00+00:00')
        monthly = [o for o in result['shadow_outcomes'] if o['horizon'] == '1m' and o['state'] == 'completed']
        self.assertEqual(len(monthly), 3)
        self.assertEqual(
            sorted((o['strategy_id'], o['decision_at'][:10], o['independent']) for o in monthly),
            [
                ('authored_cycle', '2026-01-05', True),
                ('authored_cycle', '2026-01-06', False),  # enters while the first is still open
                ('second_cycle', '2026-01-05', True),  # another strategy's open trade does not use up this sample
            ],
        )
        self.assertEqual(self.gate_of(result)['stats']['count'], 1)
        self.assertEqual(self.gate_of(result, 'second_cycle')['stats']['count'], 1)

    def promoted_ledger(self, name='journal', **kw):
        ledger = self.ledger(name, **kw)
        data = self.run_schedule(ledger, [WIN] * 4)
        # The fourth outcome (July) matures on 8 August.
        result = review(ledger, data, '2026-09-15T00:00:00+00:00')
        persist_review(ledger, result)
        return ledger, data, result

    def test_promotion_is_a_single_look_at_the_registered_sample_size(self):
        for count in (3, 4):
            with self.subTest(count):
                ledger = self.ledger(f'n{count}')
                data = self.run_schedule(ledger, [WIN] * count)
                result = review(ledger, data, '2026-09-15T00:00:00+00:00')
                gate = self.gate_of(result)['promotion']
                self.assertEqual((gate['n'], gate['look_n']), (count, 4))
                self.assertEqual(gate['eligible'], count == 4)
                if count == 3:
                    self.assertEqual(self.gate_of(result)['status'], '검증중')
                    self.assertIn('독립 성숙 섀도 표본 3/4개', gate['reasons'])
        ledger, _, result = self.promoted_ledger()
        state = self.gate_of(result)
        gate = state['promotion']
        self.assertEqual((gate['family_size'], gate['quantile'], gate['resamples']), (1, '0.025', 10000))
        self.assertEqual((gate['criteria_met'], gate['eligible'], state['status']), (True, True, '승인'))
        self.assertClose(gate['mean_excess'], excess_of(WIN))
        self.assertClose(gate['lower_bound'], excess_of(WIN))  # four identical outcomes: no spread to widen the bound

    def test_waiting_for_a_lucky_stretch_cannot_pass_the_gate(self):
        # The first four outcomes (one loss, three wins) fail the registered look; seven wins out of eight
        # would clear a plain 95% bound. Re-testing as outcomes arrive would promote by patience alone.
        ledger = self.ledger()
        data = self.run_schedule(ledger, [LOSS] + [WIN] * 7)
        result = review(ledger, data, '2027-05-15T00:00:00+00:00')
        state = self.gate_of(result)
        gate = state['promotion']
        self.assertEqual((gate['n'], gate['look_n']), (8, 4))
        self.assertEqual((gate['criteria_met'], gate['eligible']), (False, False))
        self.assertClose(gate['mean_excess'], (excess_of(LOSS) + 3 * excess_of(WIN)) / 4)  # the first four only
        self.assertLessEqual(Decimal(gate['lower_bound']), 0)
        # ... and the same eight outcomes with the loss second, judged at n=8 by a plain bound, would have passed.
        outcomes = [excess_of(LOSS)] + [excess_of(WIN)] * 7
        self.assertGreater(lower_confidence_bound(outcomes, Decimal('0.025'), 10000), 0)

    def test_a_promoted_strategy_buys_only_a_small_c_grade_amount(self):
        ledger, _, _ = self.promoted_ledger()
        result, _, _ = judge(ledger, 2026, 11)
        row = result['decisions'][0]
        self.assertEqual((row['verification'], row['grade'], row['action']), ('shadow_promoted', 'C', '소액 매수'))
        self.assertNotIn('shadow', row)
        # C cap 5% of 10,000,000 KRW; the reserve and the loss capacity leave room, so the cap is what binds.
        self.assertEqual(row['amount_krw'], '500000')
        self.assertEqual(result['allocation']['cash_krw'], '9500000')
        self.assertTrue(any('사전 고정한 섀도 기록 기준' in b for b in row['blockers']))
        self.assertIn('C등급 소액까지만', row['rationale'])
        # A review that did not exist yet at the judgment cannot promote it.
        late = self.ledger('late')
        data = self.run_schedule(late, [WIN] * 4)
        persist_review(late, review(late, data, '2026-12-01T00:00:00+00:00'))
        november = judge(late, 2026, 11, persist=False)[0]['decisions'][0]
        self.assertEqual((november['action'], november['amount_krw']), ('신규 매수하지 않음', '0'))
        self.assertTrue(november['shadow']['tracked'])

    def test_a_real_warning_outranks_a_promotion(self):
        ledger, _, _ = self.promoted_ledger()
        plan, snapshot = dated(2026, 11)
        snapshot['strategy_registry'] = view(ledger, snapshot['as_of'])
        snapshot['strategy_feedback'] = feedback(ledger, snapshot['as_of'])
        self.assertTrue(snapshot['strategy_feedback']['authored_cycle/v1/shadow_synthetic']['promotion']['eligible'])
        snapshot['strategy_feedback']['authored_cycle/v1/synthetic'] = dict(status='경고')  # losses in real buys
        row = evaluate(plan, snapshot)['decisions'][0]
        self.assertEqual(
            (row['verification'], row['action'], row['amount_krw']), ('degraded', '신규 매수하지 않음', '0')
        )
        self.assertEqual(row['shadow']['track'], 'control')

    def test_a_promotion_that_belongs_to_another_definition_or_registration_is_ignored(self):
        ledger, _, _ = self.promoted_ledger()
        for field in ('strategy_sha256', 'registration_sha256'):
            with self.subTest(field):
                plan, snapshot = dated(2026, 11)
                snapshot['strategy_registry'] = view(ledger, snapshot['as_of'])
                snapshot['strategy_feedback'] = feedback(ledger, snapshot['as_of'])
                snapshot['strategy_feedback']['authored_cycle/v1/shadow_synthetic']['promotion'][field] = 'f' * 64
                row = evaluate(plan, snapshot)['decisions'][0]
                self.assertEqual((row['verification'], row['amount_krw']), ('insufficient', '0'))

    def test_the_corrected_bound_depends_on_how_many_strategies_were_registered(self):
        # Seven wins and one loss (the loss is 10% larger than a win). Exactly: a resample is not positive when it
        # draws the loss four or more times out of eight.
        p = sum(comb(8, k) * Decimal(1) / 8**k * Decimal(7) ** (8 - k) / 8 ** (8 - k) for k in range(4, 9))
        self.assertTrue(Decimal('0.005') < p < Decimal('0.025'), p)  # 1.1%: inside a 2.5% tail but not a 0.5% one
        ends = [WIN, LOSS] + [WIN] * 6
        results = {}
        for fillers in (0, 4):
            ledger = self.ledger(f'k{fillers}', fillers=fillers, policy=dict(minimum_historical=8, minimum_live=2))
            data = self.run_schedule(ledger, ends)
            results[fillers] = self.gate_of(review(ledger, data, '2027-05-15T00:00:00+00:00'))['promotion']
        alone, crowded = results[0], results[4]
        self.assertEqual((alone['family_size'], alone['quantile']), (1, '0.025'))
        self.assertEqual((crowded['family_size'], crowded['quantile']), (5, '0.005'))
        self.assertEqual(alone['mean_excess'], crowded['mean_excess'])  # same outcomes, only K differs
        self.assertGreater(Decimal(alone['lower_bound']), 0)
        self.assertTrue(alone['eligible'])
        self.assertLessEqual(Decimal(crowded['lower_bound']), 0)
        self.assertFalse(crowded['eligible'])
        self.assertIn('보정한 하한이 0 이하', ' '.join(crowded['reasons']))

    def test_strategies_registered_after_the_look_do_not_change_it(self):
        plan, _ = dated(2026, 1)

        def add_fillers(ledger, day):
            for i in range(4):
                register_strategy(ledger, plan, strategy_id=f'late_{i}', now=day)

        # The look is the maturity of the fourth outcome (8 August 2026).
        after = self.ledger('after')
        data = self.run_schedule(after, [WIN] * 4)
        add_fillers(after, datetime(2026, 12, 1, tzinfo=timezone.utc))
        gate = self.gate_of(review(after, data, '2027-01-15T00:00:00+00:00'))['promotion']
        self.assertEqual((gate['family_size'], gate['quantile']), (1, '0.025'))
        before = self.ledger('before')
        for year, month in SCHEDULE[:3]:
            judge(before, year, month)
        add_fillers(before, datetime(2026, 6, 1, tzinfo=timezone.utc))  # between the May and July judgments
        judge(before, *SCHEDULE[3])
        data = outcome_prices(plan, [(y, m, WIN) for y, m in SCHEDULE[:4]])
        gate = self.gate_of(review(before, data, '2027-01-15T00:00:00+00:00'))['promotion']
        self.assertEqual((gate['family_size'], gate['quantile']), (5, '0.005'))

    def test_a_failed_backtest_is_only_a_control_and_never_promoted(self):
        def uptrend(plan, snapshot):
            for i, r in enumerate(plan['candidates'][0]['prices']['rows']):
                r['value'] = str(Decimal(100) * Decimal('1.01') ** i)

        ledger = self.root / 'journal'
        register_strategy(ledger, dated(2026, 1, trial_count=1)[0])
        entries, plan = [], None
        for year, month in SCHEDULE[:4]:
            result, plan, _ = judge(ledger, year, month, trial_count=1, mutate=uptrend)
            row = result['decisions'][0]
            self.assertEqual((row['verification'], row['grade'], row['shadow']['track']), ('failed', 'F', 'control'))
            entries.append((year, month, WIN))
        review_ = review(ledger, outcome_prices(plan, entries), '2026-09-15T00:00:00+00:00')
        state = self.gate_of(review_)
        self.assertEqual(state['track'], 'control')
        self.assertTrue(state['promotion']['criteria_met'])  # four wins would have cleared the look...
        self.assertFalse(state['promotion']['eligible'])  # ...but a control is never promoted
        self.assertNotEqual(state['status'], '승인')
        self.assertIn('대조군', ' '.join(state['promotion']['reasons']))
        persist_review(ledger, review_)
        later = judge(ledger, 2026, 11, trial_count=1, mutate=uptrend, persist=False)[0]['decisions'][0]
        self.assertEqual((later['grade'], later['action'], later['amount_krw']), ('F', '신규 매수하지 않음', '0'))
        self.assertIn('문턱을 바꾸는 근거로 쓰지 않는다', ' '.join(state['promotion']['reasons']))

    def test_judgments_that_mature_late_and_turn_bad_withdraw_a_promotion(self):
        ledger = self.ledger()
        data = self.run_schedule(ledger, [WIN] * 4 + [LOSS] * 2)
        early = self.gate_of(review(ledger, data, '2026-09-15T00:00:00+00:00'))
        self.assertTrue(early['promotion']['eligible'])
        self.assertEqual(early['stats']['count'], 4)
        late = self.gate_of(review(ledger, data, '2027-01-15T00:00:00+00:00'))
        self.assertEqual(late['stats']['count'], 6)
        self.assertEqual(late['status'], '경고')
        self.assertTrue(late['promotion']['criteria_met'])  # the look itself is unchanged
        self.assertFalse(late['promotion']['eligible'])
        self.assertIn('승격 자격을 철회', ' '.join(late['promotion']['reasons']))
        persist_review(ledger, review(ledger, data, '2027-01-15T00:00:00+00:00'))
        row = judge(ledger, 2027, 3, persist=False)[0]['decisions'][0]
        self.assertEqual((row['verification'], row['action']), ('insufficient', '신규 매수하지 않음'))

    def test_gate_numbers_come_from_the_registration_not_the_plan(self):
        ledger = self.ledger()  # registered with a look at 4 outcomes
        data = self.run_schedule(ledger, [WIN] * 3)
        plan, _ = dated(2026, 1)
        self.assertEqual(plan['policy']['minimum_historical'], 2)  # a plan that asks for only 2
        gate = self.gate_of(review(ledger, data, '2026-09-15T00:00:00+00:00'))['promotion']
        self.assertEqual((gate['look_n'], gate['eligible']), (4, False))

    def test_removed_edited_or_unchained_judgments_are_detected(self):
        ledger = self.ledger()
        judge(ledger, 2026, 1)
        judge(ledger, 2026, 3)
        data = outcome_prices(dated(2026, 1)[0], [(2026, 1, WIN), (2026, 3, WIN)])
        self.assertTrue(review(ledger, data, '2026-05-15T00:00:00+00:00')['shadow_outcomes'])
        files = sorted((ledger / 'decisions').glob('*.json'))
        saved = files[0].read_text(encoding='utf-8')
        files[0].unlink()
        with self.assertRaisesRegex(SourceError, 'was removed'):
            review(ledger, data, '2026-05-15T00:00:00+00:00')
        files[0].write_text(saved, encoding='utf-8')
        # A v4 judgment dropped into the folder without going through record() is not accepted.
        forged, _, _ = judge(ledger, 2026, 5, persist=False)
        save(ledger / 'decisions' / (digest(forged) + '.json'), forged)
        with self.assertRaisesRegex(SourceError, 'not in the journal chain'):
            review(ledger, data, '2026-07-15T00:00:00+00:00')


class ReplayAndCliTests(ShadowCase):
    def run_cycle_at(self, plan, snapshot, name, now, version=None, **kw):
        class Run:
            pass

        with (
            patch('investment_research.orchestrator.replay_ask', return_value=Run()),
            patch('investment_research.investment_cycle.research_snapshot', return_value=snapshot),
        ):
            if version is None:
                return run_cycle(plan, 'unused', self.root / name, now=now, **kw)
            with (
                patch('investment_research.investment_cycle.VERSION', version),
                patch('investment_research.investment_cycle.evaluate.__defaults__', (version,)),
            ):
                return run_cycle(plan, 'unused', self.root / name, now=now, **kw)

    def test_a_saved_v3_run_still_replays_with_its_own_rules(self):
        plan, snapshot = experiment()
        saved = self.run_cycle_at(plan, snapshot, 'v3', _time(AT), version='investment_cycle_v3')
        self.assertEqual(saved['method_version'], 'investment_cycle_v3')
        self.assertNotIn('strategy_registry', saved)
        self.assertNotIn('shadow', saved['decisions'][0])
        self.assertEqual(replay_cycle(self.root / 'v3'), saved)

    def test_a_v4_run_stores_the_registry_it_used_and_replays_without_the_journal(self):
        ledger = self.root / 'journal'
        plan, snapshot = experiment()
        plan['candidates'][0]['strategy']['trial_count'] = 3
        register_strategy(ledger, plan, policy=None)
        saved = self.run_cycle_at(plan, snapshot, 'v4', _time(AT), ledger=ledger)
        self.assertEqual(saved['method_version'], 'investment_cycle_v4')
        self.assertTrue(saved['decisions'][0]['shadow']['tracked'])
        stored = load(self.root / 'v4' / 'input.json')['research']['strategy_registry']
        self.assertEqual(stored['family_size'], 1)
        self.assertEqual(saved['strategy_registry']['chain_head_sha256'], stored['chain_head_sha256'])
        self.assertEqual(len(list((ledger / 'decisions').glob('*.json'))), 1)
        self.assertEqual(replay_cycle(self.root / 'v4'), saved)
        text = (self.root / 'v4' / 'report.md').read_text(encoding='utf-8')
        self.assertIn('섀도 기록', text)

    def test_strategy_commands_register_list_and_discard(self):
        plan, _ = dated(2026, 1)
        library = dict(
            schema_version='investment-strategy-library-v1',
            entries=[
                dict(
                    kind='testable', strategy=plan['candidates'][0]['strategy'], application=APPLICATION, source=SOURCE
                ),
                dict(
                    kind='untestable',
                    id='risk_parity_bonds',
                    hypothesis='채권 변동성을 맞춘 배분이 주식 60/40보다 손실이 작다.',
                    reason='채권 ETF 가격 이력 제공자가 없고, 상시 투자 규칙을 표현하는 백테스트 엔진이 없다.',
                    required=['국채 ETF 총수익 이력', '포트폴리오 규칙용 백테스트'],
                    source=SOURCE,
                ),
            ],
        )
        save(self.root / 'library.json', library)
        journal = str(self.root / 'journal')

        def invoke(*argv):
            out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = main(['invest', 'strategy', *argv])
            return code, out.getvalue()

        code, out = invoke('register', str(self.root / 'library.json'), '--journal', journal)
        self.assertEqual(code, 0)
        self.assertIn('새로 등록 2건', out)
        code, out = invoke('register', str(self.root / 'library.json'), '--journal', journal)
        self.assertIn('새로 등록 0건, 이미 같은 정의로 등록됨 2건', out)
        code, out = invoke('list', '--journal', journal)
        self.assertIn('시험 후보 수(K): **1**', out)
        self.assertIn('아직 시험할 수 없는 후보', out)
        self.assertIn('risk_parity_bonds', out)
        code, out = invoke('discard', 'authored_cycle', 'v1', '--reason', '합성 시험 후 폐기', '--journal', journal)
        self.assertEqual(code, 0)
        code, out = invoke('list', '--journal', journal)
        self.assertIn('시험 후보 수(K): **1**', out)  # a discarded strategy still counts
        self.assertIn('discarded', out)
        save(self.root / 'bad.json', {'schema_version': 'other'})
        code, _ = invoke('register', str(self.root / 'bad.json'), '--journal', journal)
        self.assertNotEqual(code, 0)


if __name__ == '__main__':
    unittest.main()
