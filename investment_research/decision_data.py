"""Strict, offline contracts for predeclared investment experiments.

Inputs are reviewed data, not forecasts inferred by a language model. A latest
revised historical series cannot masquerade as a point-in-time series.
"""

from calendar import monthrange
from datetime import timedelta
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
from functools import wraps

from .sources import SourceError, _parse_json, _time as _parse_time

VERSION = 'investment_cycle_v3'
# v1 reduced a held position when current data were unverified. v3 keeps the
# v2 action rules and uses backtest v2 (reviewed price lower bounds). Older
# versions stay replayable so saved judgments are reproduced, never rewritten.
SUPPORTED_VERSIONS = ('investment_cycle_v1', 'investment_cycle_v2', 'investment_cycle_v3')
# Only reviewed collectors for assets without cash distributions may label a
# price series a lower bound; a typed label on, say, a dividend stock would
# bias the same-series timing baselines that approval still compares.
LOWER_BOUND_PROVIDERS = ('upbit_day_candles', 'upbit_aligned_candles')
# return_basis -> (return_kind, adjustment) it must declare.
RETURN_BASES = {
    'price_lower_bound': ('price', 'unadjusted'),
    'non_distributing_fund_price': ('total_return', 'pit_total_return_index'),
    # Issuer NAV (not an executable price) verified to keep reinvested distributions.
    'issuer_nav_reinvested': ('total_return', 'pit_total_return_index'),
}
# These bases describe a market measure, not something a plan can buy at that value.
BENCHMARK_ONLY_BASES = ('issuer_nav_reinvested',)
HORIZONS = {'1w': 0, '1m': 1, '3m': 3, '6m': 6, '1y': 12}
MARKETS = (
    '미국 주식',
    '한국 주식',
    '성장주',
    'AI',
    '반도체',
    '가치주',
    '배당주',
    '미국 국채',
    '한국 국채',
    '금',
    '은',
    '원유',
    '천연가스',
    '산업금속',
    '기타 원자재',
    'Bitcoin',
    'Ethereum',
    '주요 암호화폐',
    '서울/수도권 부동산',
    '글로벌 부동산',
    '새로운 투자 기회',
)


def lower_bound(dataset):
    provenance = dataset.get('provenance')
    return (
        dataset.get('return_basis') == 'price_lower_bound'
        and dataset['return_kind'] == 'price'
        and dataset['adjustment'] == 'unadjusted'
        and isinstance(provenance, dict)
        and provenance.get('provider') in LOWER_BOUND_PROVIDERS
    )


def timestamp(value):
    if not isinstance(value, str) or len(value) < 19:
        raise SourceError('investment timestamps require explicit time and timezone')
    result = _parse_time(value)
    if result is None:
        raise SourceError('investment timestamp cannot be unknown')
    return result


_time = timestamp


def contract(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except SourceError:
            raise
        except (KeyError, TypeError, AttributeError, ValueError, OverflowError) as exc:
            raise SourceError(function.__name__ + ': malformed or missing required field') from exc

    return wrapped


def number(value, name='number'):
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise SourceError(name + ': use a finite decimal string or integer')
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise SourceError(name + ': invalid decimal') from exc
    if not result.is_finite():
        raise SourceError(name + ': nonfinite value')
    return result


def digest(data):
    return hashlib.sha256(encode(data).encode()).hexdigest()


def encode(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n'


def load(path):
    path = Path(path)
    if path.stat().st_size > 32 * 1024 * 1024:
        raise SourceError('decision input exceeds 32 MiB')
    return _parse_json(path.read_text(encoding='utf-8'))


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = encode(data)
    if path.exists():
        if path.read_text(encoding='utf-8') != text:
            raise SourceError('immutable record differs: ' + str(path))
        return
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        handle.write(text)


def target(at, horizon):
    if horizon not in HORIZONS:
        raise SourceError('unsupported holding horizon')
    if horizon == '1w':
        return at + timedelta(days=7)
    months = at.year * 12 + at.month - 1 + HORIZONS[horizon]
    year, month = divmod(months, 12)
    return at.replace(year=year, month=month + 1, day=min(at.day, monthrange(year, month + 1)[1]))


@contract
def rule(rule):
    if (
        not isinstance(rule, dict)
        or not rule.get('feature')
        or rule.get('op') not in ('>', '>=', '<', '<=', '==')
        or type(rule.get('max_age_days')) is not int
        or not 0 <= rule['max_age_days'] <= 366
    ):
        raise SourceError('invalid feature condition or freshness limit')
    number(rule.get('value'), 'condition value')


@contract
def validate_dataset(data):
    if not isinstance(data, dict) or data.get('schema_version') != 'investment-prices-v1':
        raise SourceError('unsupported investment price dataset')
    if type(data.get('synthetic')) is not bool:
        raise SourceError('dataset must explicitly declare synthetic status')
    if data.get('return_kind') not in ('price', 'total_return'):
        raise SourceError('declare price or total_return; do not double count dividends')
    if data.get('adjustment') not in ('unadjusted', 'pit_total_return_index', 'latest_adjusted'):
        raise SourceError('unknown price adjustment meaning')
    if data['return_kind'] == 'total_return' and data['adjustment'] == 'unadjusted':
        raise SourceError('unadjusted price is not a total-return series')
    basis = data.get('return_basis')
    if basis is not None and (
        basis not in RETURN_BASES
        or RETURN_BASES[basis] != (data['return_kind'], data['adjustment'])
        or not isinstance(data.get('return_basis_note'), str)
        or not data['return_basis_note'].strip()
    ):
        raise SourceError('return basis must match its reviewed return definition and carry a review note')
    for field in ('instrument_id', 'asset_id', 'currency', 'source', 'calendar', 'survivorship', 'unit', 'measure'):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise SourceError('dataset missing ' + field)
    if data['survivorship'] not in ('single_instrument', 'point_in_time_universe', 'current_survivors'):
        raise SourceError('unknown survivorship policy')
    _time(data['retrieved_at'])
    rows = data.get('rows')
    if not isinstance(rows, list) or not rows:
        raise SourceError('price rows required')
    prior = None
    for row in rows:
        at = _time(row['at'])
        known = _time(row['known_at'])
        if known < at or known > _time(data['retrieved_at']):
            raise SourceError('price availability precedes observation or follows retrieval')
        if prior is not None and at <= prior:
            raise SourceError('price rows must be sorted and unique')
        prior = at
        if number(row['value'], 'price') <= 0:
            raise SourceError('nonpositive price')


@contract
def validate_strategy(s):
    if not isinstance(s, dict):
        raise SourceError('strategy object required')
    for field in ('id', 'version'):
        if not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}', s.get(field, '')):
            raise SourceError('invalid strategy identity')
    for field in ('hypothesis', 'revision_reason'):
        if not isinstance(s.get(field), str) or not s[field].strip():
            raise SourceError('strategy missing ' + field)
    _time(s['locked_at'])
    if type(s.get('trial_count')) is not int or s['trial_count'] < 1:
        raise SourceError('declare all attempted strategy variants')
    if s.get('holding_horizon') not in ('1m', '3m', '6m', '1y'):
        raise SourceError('declare decision holding horizon')
    for key in ('conditions', 'price_conditions', 'invalidations'):
        if not isinstance(s.get(key), list) or not s[key]:
            raise SourceError('strategy must define ' + key)
        for item in s[key]:
            rule(item)
    split = s['splits']
    times = [_time(split[k]) for k in ('start', 'validation_start', 'recent_start', 'end')]
    if times != sorted(set(times)):
        raise SourceError('experiment partitions must be ordered and distinct')
    if _time(s['locked_at']) > times[1]:
        raise SourceError('independent validation starts before strategy was frozen')
    if number(s['cost_bps_per_side'], 'transaction cost') < 0 or number(s['cost_bps_per_side']) >= 10000:
        raise SourceError('invalid round-trip cost per side')
    if s.get('parent_sha256') is not None and not re.fullmatch('[0-9a-f]{64}', s['parent_sha256']):
        raise SourceError('invalid parent strategy hash')


@contract
def validate_plan(data):
    if not isinstance(data, dict) or data.get('schema_version') != 'investment-plan-v1':
        raise SourceError('unsupported investment decision plan')
    if type(data.get('synthetic')) is not bool:
        raise SourceError('plan must explicitly declare synthetic status')
    if number(data.get('new_cash_krw')) <= 0 or number(data['new_cash_krw']) % 1:
        raise SourceError('new cash must be positive integer KRW')
    if not isinstance(data.get('scenario_note'), str) or not data['scenario_note']:
        raise SourceError('declare allocation scenario assumptions')
    policy = data['policy']
    for name in ('minimum_historical', 'minimum_validation', 'minimum_recent', 'minimum_live'):
        if type(policy.get(name)) is not int or policy[name] < 2:
            raise SourceError('minimum samples must be declared and at least two')
    for name in ('A', 'B', 'C', 'group_cap'):
        value = number(policy['caps'][name])
        if not 0 <= value <= 1:
            raise SourceError('allocation cap outside [0, 1]')
    if not number(policy['caps']['A']) >= number(policy['caps']['B']) >= number(policy['caps']['C']):
        raise SourceError('grade caps must be ordered')
    profile = data.get('profile')
    if profile is not None:
        for key in ('reserve_krw', 'loss_capacity_krw'):
            if number(profile[key]) < 0:
                raise SourceError('negative scenario constraint')
        if not 0 <= number(profile['loss_tolerance_fraction']) <= 1:
            raise SourceError('invalid loss tolerance')
        if type(profile['horizon_months']) is not int or profile['horizon_months'] < 1:
            raise SourceError('invalid investment horizon')
    candidates = data.get('candidates')
    if not isinstance(candidates, list) or len(candidates) > 5:
        raise SourceError('at most five investment candidates')
    identifiers = set()
    for c in candidates:
        if not c.get('asset_id') or c['asset_id'] in identifiers:
            raise SourceError('duplicate or empty asset identity')
        identifiers.add(c['asset_id'])
        if c.get('mode') not in ('quantitative', 'event', 'unvalidated'):
            raise SourceError('declare candidate verification method')
        if not c.get('name') or not c.get('group') or type(c.get('held')) is not bool:
            raise SourceError('declare candidate name, overlapping exposure group and held status')
        for name in ('reasons_up', 'reasons_down'):
            if not isinstance(c.get(name), list) or not 1 <= len(c[name]) <= 5:
                raise SourceError('declare one to five supporting and opposing reasons')
        if c['mode'] == 'unvalidated':
            continue
        if 'history' in c and 'prices' not in c:
            raise SourceError('candidate refers to a history run; expand it with invest run --history')
        if not isinstance(c.get('current_price_evidence_id'), str) or not c['current_price_evidence_id']:
            raise SourceError('current price source reference required')
        if not isinstance(c.get('review'), dict) or not c['review'].get('reviewer') or not c['review'].get('note'):
            raise SourceError('economic thesis needs an explicit scoped review')
        _time(c['review']['at'])
        if not c.get('evidence_ids') or not c.get('counter_evidence_ids'):
            raise SourceError('supporting and opposing source references required')
        validate_strategy(c['strategy'])
        for dataset in ('prices', 'benchmark'):
            validate_dataset(c[dataset])
            if c[dataset]['synthetic'] != data['synthetic']:
                raise SourceError('synthetic and real data cannot be mixed')
        quote = c['quote']
        if (
            quote['instrument_id'] != c['prices']['instrument_id']
            or quote['currency'] != 'KRW'
            or not quote['unit']
            or not quote['measure']
            or number(quote['value']) <= 0
        ):
            raise SourceError('declare actual KRW instrument quote, separate from total-return index')
        if _time(quote['at']) > _time(quote['known_at']):
            raise SourceError('quote known before its observation')
        if c['prices']['asset_id'] != c['asset_id']:
            raise SourceError('investment exposure and traded price instrument differ')
        if c['prices'].get('return_basis') in BENCHMARK_ONLY_BASES:
            raise SourceError('an issuer NAV series is a market benchmark, not a price the plan can trade at')
        # A reviewed price lower bound may face a total-return benchmark: the
        # omission can only understate the candidate, never flatter it.
        bounded = lower_bound(c['prices']) and c['benchmark']['return_kind'] == 'total_return'
        if c['prices']['currency'] != c['benchmark']['currency'] or (
            c['prices']['return_kind'] != c['benchmark']['return_kind'] and not bounded
        ):
            raise SourceError('benchmark currency or return definition differs')
        if c['prices']['instrument_id'] == c['benchmark']['instrument_id']:
            raise SourceError('market benchmark must be a separate declared instrument')
        if c['prices']['currency'] != 'KRW':
            raise SourceError('allocation comparison needs explicit KRW returns including currency exposure')
        if type(c.get('max_price_age_days')) is not int or not 0 <= c['max_price_age_days'] <= 31:
            raise SourceError('declare executable price freshness limit')
        features = c.get('features')
        if not isinstance(features, list):
            raise SourceError('point-in-time feature observations required')
        seen = set()
        for f in features:
            observed, known = _time(f['observed_at']), _time(f['known_at'])
            if observed > known or known > _time(f['retrieved_at']):
                raise SourceError('feature publication/revision availability is inconsistent')
            number(f['value'])
            for key in ('unit', 'currency', 'measure'):
                if not isinstance(f.get(key), str) or not f[key]:
                    raise SourceError('feature definition missing ' + key)
            key = (f['name'], f['observed_at'], f['known_at'])
            if key in seen or not f.get('source') or not f.get('vintage'):
                raise SourceError('duplicate feature vintage or missing source')
            seen.add(key)
        definitions = {}
        for f in features:
            d = tuple(f[k] for k in ('unit', 'currency', 'measure', 'source'))
            if f['name'] in definitions and definitions[f['name']] != d:
                raise SourceError('feature definition changed within one history')
            definitions[f['name']] = d
        if c['mode'] == 'event' and not c.get('analog_evidence_ids'):
            raise SourceError('nonrepeatable event requires reviewed comparable cases')
    return data


def default_plan():
    return dict(
        schema_version='investment-plan-v1',
        synthetic=False,
        new_cash_krw='10000000',
        scenario_note='신규 현금 1,000만원의 예시다. 개인 재무 조건이 미확인인 자금은 집행하지 않는다.',
        profile=None,
        candidates=[],
        policy=dict(
            minimum_historical=20,
            minimum_validation=10,
            minimum_recent=10,
            minimum_live=10,
            caps=dict(A='0.4', B='0.2', C='0.05', group_cap='0.5'),
        ),
    )
