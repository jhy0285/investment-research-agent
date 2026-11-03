"""Pre-registration of strategies and a tamper-evident chain over the decision journal.

A forward (shadow) record is worth something only if the rule was fixed before its
outcomes existed and nobody can quietly drop the unfavourable ones. So:

* every strategy is registered, with the rule that will promote it, before any
  shadow judgment can count for it (`registrations/<sha256>.json`);
* the registrations, discards and recorded judgments are linked in an append-only
  hash chain (`chain.jsonl`), so a deleted or edited entry breaks the chain;
* the number of registered strategies (the family size K) is read from that chain,
  never typed in, because K sets how much evidence a promotion needs.

Registration time is the machine clock at registration. It cannot be set by the
caller on the command line. The chain is tamper-evident, not tamper-proof: someone
who can rewrite the whole directory can rewrite the chain, so the head hash that
each judgment stores is the thing to keep somewhere else if that matters.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from .decision_data import (
    SHADOW_VERSIONS,
    contract,
    default_plan,
    digest,
    load,
    save,
    timestamp as _time,
    validate_strategy,
)
from .sources import SourceError, _parse_json

VERSION = 'strategy_registry_v1'
RULE_METHOD = 'forward_first_n_bootstrap_bonferroni_v1'
ZERO_HASH = '0' * 64
# Where a hypothesis came from, ordered by how much weight it deserves. Claims are
# hypotheses at every level; the class only records provenance.
SOURCE_CLASSES = ('학술·공식', '실무자 공개 자료', '커뮤니티·SNS 가설', '자체 가설')
MAX_FAMILY = 250  # beyond this the bootstrap cannot resolve the corrected tail


def _line_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _chain_path(ledger):
    return Path(ledger) / 'chain.jsonl'


def read_chain(ledger):
    """Every chain event in order, after checking sequence, links and time order."""
    path = _chain_path(ledger)
    if not path.exists():
        return []
    events, previous, last = [], ZERO_HASH, None
    # Not str.splitlines(): it also splits on U+2028, U+0085 and similar characters that free text (a discard
    # reason) may legitimately contain, which would cut one chain entry in two and make the journal unreadable.
    lines = path.read_text(encoding='utf-8').split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    for position, raw in enumerate(lines, 1):
        try:
            event = _parse_json(raw)
            at = _time(event['at'])
        except (SourceError, KeyError, TypeError, ValueError) as exc:
            raise SourceError('journal chain line is unreadable') from exc
        if event.get('seq') != position or event.get('prev') != previous:
            raise SourceError('journal chain is broken: an entry was removed, edited or reordered')
        if last is not None and at < last:
            raise SourceError('journal chain time runs backwards')
        previous, last = _line_hash(raw), at
        events.append(dict(event, line_sha256=previous))
    return events


def _append(ledger, kind, payload, now):
    root = Path(ledger)
    events = read_chain(root)
    at = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if events and at < _time(events[-1]['at']):
        raise SourceError('journal chain entries cannot be dated before the previous entry')
    event = dict(seq=len(events) + 1, prev=events[-1]['line_sha256'] if events else ZERO_HASH, at=at.isoformat())
    event.update(kind=kind, **payload)
    line = json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
    root.mkdir(parents=True, exist_ok=True)
    with _chain_path(root).open('a', encoding='utf-8', newline='\n') as handle:
        handle.write(line + '\n')
    return dict(event, line_sha256=_line_hash(line))


def _key(strategy):
    return strategy['id'] + '/' + strategy['version']


def promotion_rule(policy=None):
    """The gate a strategy must clear, fixed at registration from the plan policy numbers.

    The rule is stored with the registration, so later edits to a plan's policy
    cannot lower the bar for a strategy that was already registered.
    """
    policy = policy or default_plan()['policy']
    rule = dict(
        method=RULE_METHOD,
        minimum_independent=policy['minimum_historical'],
        recent_n=policy['minimum_live'],
        one_sided_alpha='0.025',
    )
    if not (
        type(rule['minimum_independent']) is int
        and type(rule['recent_n']) is int
        and 2 <= rule['recent_n'] <= rule['minimum_independent']
    ):
        raise SourceError('promotion rule needs integer minimums with 2 <= recent <= independent')
    return rule


@contract
def _validated(entry, registered, policy):
    if not isinstance(entry, dict) or entry.get('kind') not in ('testable', 'untestable'):
        raise SourceError('registration must declare kind testable or untestable')
    source = entry.get('source')
    if (
        not isinstance(source, dict)
        or source.get('class') not in SOURCE_CLASSES
        or not isinstance(source.get('note'), str)
        or not source['note'].strip()
    ):
        raise SourceError('registration needs a source class and note: ' + ', '.join(SOURCE_CLASSES))
    if entry['kind'] == 'untestable':
        for field in ('id', 'hypothesis', 'reason'):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                raise SourceError('untestable registration needs ' + field)
        required = entry.get('required')
        if not isinstance(required, list) or not required or not all(isinstance(r, str) and r for r in required):
            raise SourceError('untestable registration must list the data or engine it lacks')
        return dict(
            schema_version='investment-strategy-registration-v1',
            kind='untestable',
            registered_at=registered.isoformat(),
            id=entry['id'],
            hypothesis=entry['hypothesis'],
            reason=entry['reason'],
            required=required,
            source=source,
        )
    strategy = entry['strategy']
    validate_strategy(strategy)
    if _time(strategy['locked_at']) > registered:
        raise SourceError('a strategy cannot be frozen after the moment it is registered')
    application = entry.get('application')
    if (
        not isinstance(application, dict)
        or set(application) != {'asset_id', 'instrument_id', 'benchmark_instrument_id'}
        or not all(isinstance(v, str) and v for v in application.values())
        or application['instrument_id'] == application['benchmark_instrument_id']
    ):
        raise SourceError('registration must name the asset, the traded instrument and a separate benchmark instrument')
    return dict(
        schema_version='investment-strategy-registration-v1',
        kind='testable',
        registered_at=registered.isoformat(),
        strategy=strategy,
        application=application,
        source=source,
        promotion_rule=promotion_rule(policy),
    )


def load_registrations(ledger, events):
    """(event, record) for each registration event, with the stored file checked against the chain."""
    found = []
    for event in events:
        if event['kind'] != 'register':
            continue
        path = Path(ledger) / 'registrations' / (event['record_sha256'] + '.json')
        if not path.exists():
            raise SourceError('registration listed in the journal chain is missing')
        record = load(path)
        if digest(record) != event['record_sha256']:
            raise SourceError('registration content does not match the journal chain')
        found.append((event, record))
    return found


def register(ledger, entry, *, now=None, policy=None):
    """Register a strategy (or record that a candidate cannot be tested yet).

    Returns (registration, created). Registering identical content again is a no-op.
    """
    when = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    record = _validated(entry, when, policy)
    root = Path(ledger)
    events = read_chain(root)
    existing = load_registrations(root, events)
    if record['kind'] == 'untestable':
        same = [r for _, r in existing if r['kind'] == 'untestable' and r['id'] == record['id']]
        if same:
            if {k: v for k, v in same[0].items() if k != 'registered_at'} != {
                k: v for k, v in record.items() if k != 'registered_at'
            }:
                raise SourceError('an untestable registration changed; give the changed idea a new id')
            return same[0], False
    else:
        s = record['strategy']
        olds = [r for _, r in existing if r['kind'] == 'testable' and r['strategy']['id'] == s['id']]
        same = [r for r in olds if r['strategy']['version'] == s['version']]
        if same:
            if {k: v for k, v in same[0].items() if k != 'registered_at'} != {
                k: v for k, v in record.items() if k != 'registered_at'
            }:
                raise SourceError('a registered strategy changed without a new version')
            return same[0], False
        parent = s.get('parent_sha256')
        if parent:
            if parent not in {digest(r['strategy']) for r in olds}:
                raise SourceError('strategy revision parent is not registered')
        elif olds:
            raise SourceError('a new version of a registered strategy must link its parent')
        if len([1 for r in existing if r[1]['kind'] == 'testable']) >= MAX_FAMILY:
            raise SourceError('too many registered strategies for the corrected bound to be resolved')
    sha = digest(record)
    save(root / 'registrations' / (sha + '.json'), record)
    _append(root, 'register', dict(record_sha256=sha, registration_kind=record['kind']), when)
    return record, True


def register_many(ledger, entries, *, now=None, policy=None):
    """Register a whole library or none of it: an invalid entry must not leave a half-registered journal.

    The entries are first registered in a scratch copy of the journal, so the duplicate, version and parent
    checks run exactly as they will for real.
    """
    when = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    with tempfile.TemporaryDirectory() as scratch:
        trial = Path(scratch) / 'journal'
        if Path(ledger).exists():
            shutil.copytree(ledger, trial)
        for entry in entries:
            register(trial, entry, now=when, policy=policy)
    return [register(ledger, entry, now=when, policy=policy)[1] for entry in entries]


def discard(ledger, strategy_id, version, reason, *, now=None):
    """Retire a registered strategy. It keeps counting in the family size and keeps its record."""
    if not isinstance(reason, str) or not reason.strip():
        raise SourceError('discarding a strategy needs a reason')
    root = Path(ledger)
    key = strategy_id + '/' + version
    if key not in view(root, '9999-12-31T00:00:00+00:00')['strategies']:
        raise SourceError('no registered strategy ' + key)
    return _append(root, 'discard', dict(strategy=key, reason=reason), now)


def view(ledger, as_of, *, events=None, registrations=None):
    """What was registered, and the chain head, as of a time.

    `events` and `registrations` (from read_chain and load_registrations) let a caller that asks many
    times read the journal once.
    """
    cutoff = _time(as_of)
    root = Path(ledger)
    chain = [e for e in (events if events is not None else read_chain(root)) if _time(e['at']) <= cutoff]
    strategies, family = {}, 0
    source = registrations if registrations is not None else load_registrations(root, chain)
    for event, record in [(e, r) for e, r in source if _time(e['at']) <= cutoff]:
        if record['kind'] == 'untestable':
            strategies['untestable/' + record['id']] = dict(
                registration_sha256=event['record_sha256'],
                registered_at=record['registered_at'],
                testability='untestable',
                status='untestable',
                reason=record['reason'],
                required=record['required'],
            )
            continue
        family += 1
        s = record['strategy']
        strategies[_key(s)] = dict(
            registration_sha256=event['record_sha256'],
            strategy_sha256=digest(s),
            registered_at=record['registered_at'],
            testability='testable',
            status='active',
            application=record['application'],
            promotion_rule=record['promotion_rule'],
            source=record['source'],
        )
    for event in chain:
        if event['kind'] == 'discard' and event['strategy'] in strategies:
            strategies[event['strategy']].update(status='discarded', discarded_at=event['at'], reason=event['reason'])
    return dict(
        version=VERSION,
        chain_head_sha256=chain[-1]['line_sha256'] if chain else None,
        family_size=family,
        strategies=strategies,
    )


def record_decision(ledger, decision_sha256, decided_at, *, now=None):
    """Link a saved judgment into the chain (once)."""
    root = Path(ledger)
    if any(e['kind'] == 'decision' and e['decision_sha256'] == decision_sha256 for e in read_chain(root)):
        return
    _append(root, 'decision', dict(decision_sha256=decision_sha256, decided_at=decided_at), now)


def verify_decisions(ledger, decisions):
    """Chained judgments must all exist, and every investment_cycle_v4 judgment must be chained.

    `decisions` is a list of (sha256, judgment) read from the journal. Older
    judgments (v1-v3) predate the chain and are not required to appear in it.
    """
    chained = {e['decision_sha256'] for e in read_chain(ledger) if e['kind'] == 'decision'}
    present = {sha for sha, _ in decisions}
    if chained - present:
        raise SourceError('a judgment listed in the journal chain was removed')
    for sha, judgment in decisions:
        if judgment.get('method_version') in SHADOW_VERSIONS and sha not in chained:
            raise SourceError('an investment_cycle_v4 judgment is not in the journal chain')


def render_registry(registry):
    """Plain Korean list of what is registered, what cannot be tested yet, and the family size K."""
    testable = {k: v for k, v in registry['strategies'].items() if v['testability'] == 'testable'}
    untestable = {k: v for k, v in registry['strategies'].items() if v['testability'] == 'untestable'}
    lines = [
        '# 사전 등록한 전략',
        '',
        f"시험 후보 수(K): **{registry['family_size']}**. 폐기한 전략도 센다. 시험 후보가 많을수록 승격 문턱이 엄격해진다.",
        '',
    ]
    if testable:
        lines.extend(['| 전략 | 상태 | 등록 시각(UTC) | 출처 구분 | 적용 대상 |', '|---|---|---|---|---|'])
        for key, v in testable.items():
            app = v['application']
            lines.append(
                f"| {key} | {v['status']} | {v['registered_at']} | {v['source']['class']} | "
                f"{app['asset_id']} · {app['instrument_id']} vs {app['benchmark_instrument_id']} |"
            )
        lines.append('')
    if untestable:
        lines.extend(
            [
                '## 아직 시험할 수 없는 후보 (통과로 세지 않음)',
                '',
                '| 후보 | 시험할 수 없는 이유 | 필요한 것 |',
                '|---|---|---|',
            ]
        )
        for key, v in untestable.items():
            lines.append(f"| {key.split('/', 1)[1]} | {v['reason']} | {'; '.join(v['required'])} |")
        lines.append('')
    if not testable and not untestable:
        lines.append('등록된 전략이 없습니다.')
    return '\n'.join(lines) + '\n'
