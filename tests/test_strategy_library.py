"""The shipped pre-registration library stays valid, honest about what it cannot test, and consistent with its history spec."""

from datetime import date, datetime, timezone
from pathlib import Path
import tempfile
import unittest

from investment_research.decision_data import load
from investment_research.history import load_catalog, validate_spec
from investment_research.strategy_registry import SOURCE_CLASSES, register, view

ROOT = Path(__file__).resolve().parent.parent
LIBRARY = load(ROOT / 'examples' / 'strategy_library' / 'pre_registered_library.json')
SPEC = load(ROOT / 'examples' / 'investment_history' / 'crypto_trend_library_spec.json')


class StrategyLibraryTests(unittest.TestCase):
    def test_every_entry_registers_and_untestable_ones_do_not_count_toward_the_family(self):
        with tempfile.TemporaryDirectory() as tmp:
            for entry in LIBRARY['entries']:
                register(tmp, entry, now=datetime(2026, 11, 3, tzinfo=timezone.utc))
            registry = view(tmp, '2026-12-01T00:00:00+00:00')
        testable = [e for e in LIBRARY['entries'] if e['kind'] == 'testable']
        untestable = [e for e in LIBRARY['entries'] if e['kind'] == 'untestable']
        self.assertEqual(registry['family_size'], len(testable))
        self.assertEqual(sum(v['status'] == 'untestable' for v in registry['strategies'].values()), len(untestable))
        # A cannot-test idea names what is missing; none is dressed up as a candidate.
        for entry in untestable:
            self.assertTrue(entry['required'] and entry['reason'], entry['id'])
        self.assertEqual({e['source']['class'] for e in LIBRARY['entries']} - set(SOURCE_CLASSES), set())

    def test_the_testable_strategies_are_frozen_before_their_validation_periods(self):
        for entry in LIBRARY['entries']:
            if entry['kind'] != 'testable':
                continue
            s = entry['strategy']
            self.assertEqual(s['trial_count'], 1)  # rules and periods come from the literature, not from tuning
            self.assertIsNone(s['parent_sha256'])
            # No part of the validation or recent window can lie before the freeze: those periods are forward only.
            self.assertGreaterEqual(s['splits']['validation_start'], s['locked_at'])
            self.assertGreater(s['splits']['recent_start'], s['splits']['validation_start'])
            self.assertIn('완전한 사전 등록이 아니다', s['revision_reason'])

    def test_the_history_spec_is_valid_and_produces_every_feature_the_strategies_read(self):
        validate_spec(SPEC, load_catalog(), date(2026, 11, 2))
        produced = {f['name'] for f in SPEC['features']}
        for entry in LIBRARY['entries']:
            if entry['kind'] != 'testable':
                continue
            s = entry['strategy']
            used = {c['feature'] for key in ('conditions', 'price_conditions', 'invalidations') for c in s[key]}
            self.assertLessEqual(used, produced, s['id'])
            self.assertIn(entry['application']['asset_id'], ('BTC', 'ETH'))
            self.assertTrue(entry['application']['instrument_id'].endswith('_AT_KODEX_200TR'))
            self.assertEqual(entry['application']['benchmark_instrument_id'], 'KODEX_200TR')


if __name__ == '__main__':
    unittest.main()
