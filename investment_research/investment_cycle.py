"""Evidence-gated actions and an explicitly constrained new-cash scenario."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_FLOOR
import hashlib
from pathlib import Path

from .backtest import approval, condition_state, run_backtest
from .decision_data import (
    SUPPORTED_VERSIONS,
    VERSION,
    MARKETS,
    default_plan,
    digest,
    load,
    number,
    save,
    validate_plan,
    timestamp as _time,
)
from .sources import SourceError

BUY_ACTIONS = ('적극 매수', '분할 매수', '소액 매수')
ACTIONS = (*BUY_ACTIONS, '조건 충족 대기', '보유 유지', '신규 매수하지 않음', '비중 축소 검토', '매도 검토')


def research_snapshot(run):
    from .scan import assess, eligible

    evidence = eligible(run.case, run.cutoff)
    sources = {s.id: s for s in run.case.sources}
    return dict(
        as_of=run.cutoff.isoformat(),
        synthetic=run.input['synthetic'],
        research_sha256=run.digest,
        methods=[
            dict(
                asset_id=m['id'],
                name=m['label'],
                economics=m['economics'],
                risk=m['downside'],
                missing=list(m['missing']),
            )
            for m in run.input['methods']
        ],
        evidence=[
            dict(
                id=e.id,
                asset_ids=list(e.asset_ids),
                text=e.text,
                value=str(e.value) if e.value is not None else None,
                source_id=e.source_id,
                definition=e.provenance.definition,
                observed_at=e.observed_at.isoformat() if e.observed_at else None,
                unit=e.unit,
                currency=e.currency,
                retrieved_at=sources[e.source_id].provenance.retrieved_at,
            )
            for e in evidence
        ],
        scan=assess(run) if run.input.get('scan') else None,
    )


def fallback_candidates(snapshot):
    scan = snapshot.get('scan')
    rows = {r['asset_id']: r for r in scan['universe']} if scan else {}
    ids = scan['candidates'][:5] if scan else [m['asset_id'] for m in snapshot['methods']][:5]
    methods = {m['asset_id']: m for m in snapshot['methods']}
    return [
        dict(
            asset_id=i,
            name=methods[i]['name'],
            group=i,
            mode='unvalidated',
            held=False,
            reasons_up=[rows[i]['why_now'] if i in rows else methods[i]['economics']],
            reasons_down=[rows[i]['risk'] if i in rows else methods[i]['risk']],
            gaps=methods[i]['missing'] + ['재현 가능한 투자 전략 미등록'],
        )
        for i in ids
    ]


def _references(c, snapshot):
    records = {e['id']: e for e in snapshot['evidence']}
    ids = c.get('evidence_ids', []) + c.get('counter_evidence_ids', []) + c.get('analog_evidence_ids', [])
    problems = []
    for i in ids:
        e = records.get(i)
        if e is None or c['asset_id'] not in e['asset_ids']:
            problems.append(i + ': 최신·검증·해당 자산 원자료가 미확보 또는 격리됨')
        elif _time(e['retrieved_at']) > _time(c['review']['at']):
            problems.append(i + ': 의미 검토가 원자료 확보보다 이르다')
    if _time(c['review']['at']) > _time(snapshot['as_of']):
        problems.append('투자 논리 검토 시점이 판단보다 늦음')
    research = snapshot.get('research_as_of')
    if research is not None and _time(snapshot['as_of']) - _time(research) > STALE_RESEARCH:
        problems.append('조사 실행이 판단 시점보다 7일 넘게 오래됐다. 새 조사로 다시 판단한다.')
    return problems


# investment_cycle_v3 judges when the judgment is made. For `invest run` that
# is when the command executes, after a human could read the research and
# write the review; the result then carries research_as_of. The ask path
# judges at the end of its own research run (no research_as_of), so a plan
# review written before that run cannot cite evidence it fetches. Older
# versions judged `invest run` at the research cutoff, which left only the
# seconds between evidence retrieval and cutoff for a dated review.
DECIDED_AT_VERSIONS = ('investment_cycle_v3',)
STALE_RESEARCH = timedelta(days=7)


def _base_row(c, snapshot):
    return dict(
        asset_id=c['asset_id'],
        name=c['name'],
        group=c['group'],
        held=c['held'],
        mode=c['mode'],
        grade='D',
        action='신규 매수하지 않음',
        amount_krw='0',
        reasons_up=c['reasons_up'],
        reasons_down=c['reasons_down'],
        rationale='재현 가능한 전략 검증이 없어 신규 매수하지 않는다.',
        blockers=[],
        thesis='미등록',
        backtest=None,
        current_signal=dict(state='unknown', checks=[]),
        price_state=dict(state='unknown', checks=[]),
        current_price=None,
        instrument_id=None,
        invalidation='투자 이유의 원자료가 반박되면 다시 판단한다.',
        holding_horizon=None,
        strategy=None,
        research_sha256=snapshot['research_sha256'],
    )


def _strategy_fields(c, s):
    return dict(
        strategy=deepcopy(s),
        thesis=s['hypothesis'],
        holding_horizon=s['holding_horizon'],
        instrument_id=c['prices']['instrument_id'],
        benchmark_instrument_id=c['benchmark']['instrument_id'],
        return_definition={k: c['prices'][k] for k in ('currency', 'return_kind', 'adjustment')},
        invalidation='다음 조건 중 하나가 실제 발생하면 가설을 재검토한다: '
        + '; '.join(r['feature'] + ' ' + r['op'] + ' ' + str(r['value']) for r in s['invalidations']),
    )


def _links(evidence, asset_id, value, unit, currency, measure, observed_at):
    """A current number counts only when the verified passage states the same observation."""
    return (
        evidence is not None
        and asset_id in evidence['asset_ids']
        and evidence['value'] is not None
        and number(evidence['value']) == number(value)
        and evidence['unit'] == unit
        and evidence['currency'] == currency
        and evidence['definition']['measure'] == measure
        and evidence['observed_at'] == _time(observed_at).date().isoformat()
    )


def _current_state(c, snapshot, s, at):
    """Today's conditions, quote and the reasons they cannot be certified."""
    refs = _references(c, snapshot)
    lookahead = not snapshot['synthetic'] and (
        any(_time(d['retrieved_at']) > at for d in (c['prices'], c['benchmark']))
        or any(_time(f['retrieved_at']) > at for f in c['features'])
    )
    if lookahead:
        refs.append('현재 판단 시점 이후에 확보한 자료다. 실제 당시 보유한 자료로만 승인한다.')
    signal = condition_state(s['conditions'], c['features'], at)
    price = condition_state(s['price_conditions'], c['features'], at)
    invalid = [condition_state([r], c['features'], at) for r in s['invalidations']]
    raw_quote = c['quote']
    quote = raw_quote if _time(raw_quote['at']) <= at and _time(raw_quote['known_at']) <= at else None
    # Current conditions need the same scoped numeric source references as the
    # research. Numbers typed into a plan cannot certify today's observations;
    # only research passages or rows from a replay-verified history run
    # (attach_history) become evidence.
    sources = {e['id']: e for e in snapshot['evidence']}
    invalid_refs = []
    invalid_checks = [check for state in invalid for check in state['checks']]
    for check in signal['checks'] + price['checks'] + invalid_checks:
        f = next(
            (
                f
                for f in c['features']
                if f['name'] == check['feature']
                and f['known_at'] == check['known_at']
                and f['observed_at'] == check['observed_at']
                and f['vintage'] == check['vintage']
            ),
            None,
        )
        if f is None or not _links(
            sources.get(f.get('evidence_id')),
            c['asset_id'],
            check['value'],
            f['unit'],
            f['currency'],
            f['measure'],
            f['observed_at'],
        ):
            reason = check['feature'] + ': 현재 수치의 검증 원문 연결이 없음'
            refs.append(reason)
            if check in invalid_checks:
                invalid_refs.append(reason)
    if quote is not None and not _links(
        sources.get(c.get('current_price_evidence_id')),
        c['asset_id'],
        quote['value'],
        quote['unit'],
        quote['currency'],
        quote['measure'],
        quote['at'],
    ):
        refs.append('현재 투자상품 가격의 검증 원문 연결이 없음')
    stale = quote is None or at - _time(quote['at']) > timedelta(days=c['max_price_age_days'])
    return dict(
        signal=signal,
        price=price,
        invalid=invalid,
        quote=quote,
        refs=refs,
        invalid_refs=invalid_refs,
        lookahead=lookahead,
        stale=stale,
    )


def _verification(c, snapshot, s, at, policy, row, version):
    if c['mode'] == 'quantitative':
        bt = run_backtest(c, at, BACKTESTS[version])
        status, why = approval(bt, s, policy)
        row.update(backtest=bt, verification=status)
        row['blockers'].extend(why)
    else:
        status = 'event_review'
        row.update(verification=status)
        row['blockers'].append('반복 표본이 없는 사건 투자다. 검토된 유사 사례만 사용하며 C등급까지만 허용한다.')
    feedback = snapshot.get('strategy_feedback', {}).get(
        s['id'] + '/' + s['version'] + ('/synthetic' if snapshot['synthetic'] else '/real')
    )
    if feedback and feedback['status'] in ('경고', '폐기 후보'):
        status = 'degraded'
        row['verification'] = 'degraded'
        row['blockers'].append('실제 추천 결과에서 전략 ' + feedback['status'] + ' 상태다. 신규 매수를 중단한다.')
    return status


def _invalidated(c):
    return dict(
        grade='F',
        action='매도 검토' if c['held'] else '신규 매수하지 않음',
        rationale='투자 가설을 무효화하는 조건이 실제 발생했다.',
    )


def _failed(c):
    return dict(
        grade='F',
        action='비중 축소 검토' if c['held'] else '신규 매수하지 않음',
        rationale='과거 검증 실패 또는 최근 성과 붕괴로 신규 매수를 중단한다.',
    )


def _outcome_v1(c, current, status):
    """Original rule, kept so investment_cycle_v1 runs replay unchanged.

    It answered unverified current data on a held position with a weight
    reduction review, which treats missing data as negative evidence.
    """
    if current['invalidated']:
        return _invalidated(c)
    if current['refs'] or current['stale']:
        return dict(
            grade='D',
            action='비중 축소 검토' if c['held'] else '신규 매수하지 않음',
            rationale='현재 판단에 필요한 원자료 또는 실제 상품 가격이 검증되지 않았다.',
        )
    if status in ('failed', 'degraded'):
        return _failed(c)
    return _signal_outcome(c, current, status)


def _outcome_v2(c, current, status):
    """Missing data withholds judgment; only observed failure reduces a holding.

    A failed or degraded verification is acted on before data gaps unless the
    history itself was retrieved after the judgment time (look-ahead).
    """
    if current['invalidated']:
        return _invalidated(c)
    if status in ('failed', 'degraded') and not current['lookahead']:
        return _failed(c)
    if current['refs'] or current['stale']:
        return dict(
            grade='D',
            action='보유 유지' if c['held'] else '신규 매수하지 않음',
            rationale='현재 판단에 필요한 원자료 또는 실제 상품 가격이 검증되지 않아 판단을 보류한다. '
            '자료 부족은 매도·축소의 근거가 아니다.',
        )
    return _signal_outcome(c, current, status)


def _signal_outcome(c, current, status):
    if current['signal']['state'] == 'fail' or current['price']['state'] == 'fail':
        return dict(
            grade='F',
            action='보유 유지' if c['held'] else '조건 충족 대기',
            rationale='현재 매수 조건 또는 가격 조건이 충족되지 않았다.',
        )
    if current['signal']['state'] == 'unknown' or current['price']['state'] == 'unknown':
        return dict(
            grade='D',
            action='보유 유지' if c['held'] else '조건 충족 대기',
            rationale='현재 신호가 확인되지 않아 조건 충족까지 기다린다.',
        )
    if status == 'insufficient':
        return dict(
            grade='C',
            action='보유 유지' if c['held'] else '신규 매수하지 않음',
            rationale='과거 검증 표본 또는 우위가 충분하지 않아 신규 매수하지 않는다.',
        )
    grade = {'passed': 'A', 'partial': 'B', 'event_review': 'C'}[status]
    return dict(
        grade=grade,
        action='분할 매수' if grade == 'A' else '소액 매수',
        rationale='투자 논리·현재 조건·가격을 확인했고 '
        + ('과거와 최근 검증을 통과했다.' if grade == 'A' else '근거의 제한에 맞춰 소액만 배분한다.'),
    )


OUTCOMES = {'investment_cycle_v1': _outcome_v1, 'investment_cycle_v2': _outcome_v2, 'investment_cycle_v3': _outcome_v2}
BACKTESTS = {
    'investment_cycle_v1': 'pit_event_backtest_v1',
    'investment_cycle_v2': 'pit_event_backtest_v1',
    'investment_cycle_v3': 'pit_event_backtest_v2',
}
assert set(OUTCOMES) == set(BACKTESTS) == set(SUPPORTED_VERSIONS)


def decide(c, snapshot, policy, version=VERSION):
    """Grade and action for one candidate under the given decision method version."""
    if version not in OUTCOMES:
        raise SourceError('unsupported investment decision version')
    at = _time(snapshot['as_of'])
    row = _base_row(c, snapshot)
    if c['mode'] == 'unvalidated':
        row['blockers'] = c.get('gaps', []) + ['투자 가설·과거/최근 검증·현재 조건이 등록되지 않음']
        if c['held']:
            row['action'] = '보유 유지'
        return row
    s = c['strategy']
    row.update(_strategy_fields(c, s))
    current = _current_state(c, snapshot, s, at)
    row.update(
        current_signal=current['signal'],
        price_state=current['price'],
        current_price=current['quote'],
        invalidation_checks=current['invalid'],
        blockers=list(current['refs']),
    )
    if current['stale']:
        row['blockers'].append('실제 투자상품의 현재 가격이 미확보 또는 오래됨')
    status = _verification(c, snapshot, s, at, policy, row, version)
    current['invalidated'] = any(i['state'] == 'pass' for i in current['invalid']) and not current['invalid_refs']
    row.update(OUTCOMES[version](c, current, status))
    return row


def allocate(rows, plan):
    cash = number(plan['new_cash_krw'])
    profile = plan['profile']
    remaining = max(Decimal(0), cash - number(profile['reserve_krw'])) if profile else Decimal(0)
    loss_budget = (
        min(number(profile['loss_capacity_krw']), cash * number(profile['loss_tolerance_fraction']))
        if profile
        else Decimal(0)
    )
    # Historical drawdown is a loss scenario, never a worst-case guarantee.
    # Reserve full principal against capacity as losses may exceed the backtest.
    remaining = min(remaining, loss_budget)
    groups = {}
    for row in rows:
        if row['action'] not in BUY_ACTIONS:
            continue
        if profile is None or profile['horizon_months'] < {'1m': 1, '3m': 3, '6m': 6, '1y': 12}[row['holding_horizon']]:
            row.update(
                action='조건 충족 대기', rationale='재무 제약과 투자기간이 확인되거나 충족될 때까지 집행을 기다린다.'
            )
            row['blockers'].append('필요 자금·감당 가능한 손실·손실 감수 의향·투자기간 미확인 또는 불충족')
            continue
        cap = cash * number(plan['policy']['caps'][row['grade']])
        group_left = max(
            Decimal(0), cash * number(plan['policy']['caps']['group_cap']) - groups.get(row['group'], Decimal(0))
        )
        amount = min(cap, group_left, remaining).to_integral_value(rounding=ROUND_FLOOR)
        remaining -= amount
        groups[row['group']] = groups.get(row['group'], Decimal(0)) + amount
        row['amount_krw'] = str(amount)
        if amount == 0:
            row.update(
                action='조건 충족 대기',
                rationale='신규 자금의 손실 한도·예비자금·같은 노출 상한 때문에 추가 집행을 기다린다.',
            )
        else:
            # Calendar splitting is an execution convention, not a claimed edge.
            first = int(amount) // 3 if row['action'] == '분할 매수' else int(amount)
            second = (int(amount) - first) // 2 if row['action'] == '분할 매수' else 0
            row['entry_plan'] = dict(
                today_krw=str(first),
                next_review_krw=str(second),
                following_review_krw=str(int(amount) - first - second),
                rule=(
                    '다음 월간 점검마다 현재 조건·원자료·자금 제약을 다시 확인한 뒤 집행한다. 달력 분할의 성과 우위는 검증하지 않았다.'
                    if row['action'] == '분할 매수'
                    else '현재 검증 가격을 기준으로 소액을 배정한다. 주문·체결은 별도 기록한다.'
                ),
            )
    return dict(
        new_cash_krw=str(cash),
        investments=[
            dict(asset_id=r['asset_id'], name=r['name'], amount_krw=r['amount_krw'], reason=r['rationale'])
            for r in rows
            if number(r['amount_krw']) > 0
        ],
        cash_krw=str(cash - sum((number(r['amount_krw']) for r in rows), Decimal(0))),
        scenario_note=plan['scenario_note'],
        limitation='정책 상한에 따른 예시 배분이다. 미래 기대수익의 최적화나 개인 전체 포트폴리오의 적정 비중이 아니다.',
    )


def evaluate(plan, snapshot, version=VERSION):
    plan = deepcopy(validate_plan(plan))
    if plan['synthetic'] != snapshot['synthetic']:
        raise SourceError('research and decision plan synthetic status differ')
    if not plan['candidates']:
        plan['candidates'] = fallback_candidates(snapshot)
    available = {m['asset_id'] for m in snapshot['methods']}
    if any(c['asset_id'] not in available for c in plan['candidates']):
        raise SourceError('decision candidate was not researched in this run')
    # Ranking requires a common investment horizon and definition. A high raw
    # return on a differently timed or USD-only study cannot take first place.
    quantitative = [c for c in plan['candidates'] if c['mode'] == 'quantitative']
    if (
        len(
            {
                (
                    c['strategy']['holding_horizon'],
                    c['strategy']['splits']['validation_start'],
                    c['strategy']['splits']['recent_start'],
                    c['strategy']['splits']['end'],
                )
                for c in quantitative
            }
        )
        > 1
    ):
        raise SourceError('ranked candidates must use the same holding horizon and independent periods')
    rows = [decide(c, snapshot, plan['policy'], version) for c in plan['candidates']]
    original_order = {c['asset_id']: i for i, c in enumerate(plan['candidates'])}

    def order(r):
        bt = r['backtest']
        excess = (
            number(bt['periods']['recent']['horizons'][r['holding_horizon']]['mean_excess'] or '0')
            if bt
            else Decimal(0)
        )
        return ('ABCDF'.index(r['grade']), -excess, original_order[r['asset_id']])

    rows.sort(key=order)
    allocation = allocate(rows, plan)
    for i, r in enumerate(rows, 1):
        r['rank'] = i
    scan = snapshot.get('scan')
    coverage = [
        dict(name=m['name'], asset_id=m['asset_id'], status='조사됨 · 검증된 자료 범위만', missing=m['missing'])
        for m in snapshot['methods']
    ]
    return dict(
        schema_version='investment-decision-v1',
        method_version=version,
        backtest_version=BACKTESTS[version],
        as_of=snapshot['as_of'],
        synthetic=plan['synthetic'],
        research_sha256=snapshot['research_sha256'],
        plan_sha256=digest(plan),
        policy=plan['policy'],
        decisions=rows,
        allocation=allocation,
        coverage=coverage,
        market_checklist=list(MARKETS),
        scan_candidate_ids=scan['candidates'] if scan else [],
        **({'research_as_of': snapshot['research_as_of']} if snapshot.get('research_as_of') else {}),
        ranking_basis='검증 등급과 동일 기간의 최근 시장 대비 성과로 정렬한다. 검증 부족 후보의 번호는 조사 순서이며 상대 수익 우위가 아니다.',
        limitations=[
            '자료가 없는 시장의 매력은 평가하지 않았다.',
            '신규 자금의 판단과 실제 보유의 매도 판단은 구분한다.',
            '현금 유지는 검증 부재 또는 자금 제약의 결과일 수 있으며 현금의 수익 우위를 증명하지 않는다.',
        ],
    )


def attach_to_ask(run):
    plan = (
        load(run.directory / 'investment_plan.json')
        if run.input.get('investment_plan_sha256')
        else {**default_plan(), 'synthetic': run.input['synthetic']}
    )
    if run.input.get('investment_plan_sha256') and digest(plan) != run.input['investment_plan_sha256']:
        raise SourceError('investment plan checksum mismatch')
    snapshot = research_snapshot(run)
    snapshot['strategy_feedback'] = run.input.get('strategy_feedback', {})
    result = evaluate(plan, snapshot, run.input['investment_cycle_version'])
    if run.input.get('previous_investment'):
        result['changes'] = changes(run.input['previous_investment'], result)
    return result


def _current_row(rows, at):
    """The row condition_state would read at `at`: latest observation, then latest revision."""
    visible = [r for r in rows if _time(r['known_at']) <= at and _time(r.get('observed_at', r.get('at'))) <= at]
    return max(visible, key=lambda r: (_time(r.get('observed_at', r.get('at'))), _time(r['known_at'])), default=None)


def attach_history(plan, history, history_sha256, snapshot):
    """Expand `history` references from a replay-verified history run.

    The values come from this system's own reviewed collectors (retained rows
    and hashes), not from numbers typed into a plan. Only the row each current
    check will read becomes evidence, and only if it was retrieved before the
    judgment time.
    """
    plan = deepcopy(plan)
    at = _time(snapshot['as_of'])
    evidence = []
    source_id = 'history:' + history_sha256[:16]
    for c in plan['candidates']:
        ref = c.get('history')
        if ref is None:
            continue
        if not isinstance(ref, dict) or not isinstance(ref.get('features'), list):
            raise SourceError('history reference needs prices, benchmark and a feature list')
        try:
            prices, benchmark = history['prices'][ref['prices']], history['prices'][ref['benchmark']]
            features = [history['features'][name] for name in ref['features']]
        except (KeyError, TypeError) as exc:
            raise SourceError('history run lacks a referenced dataset or feature') from exc
        datasets = [prices, benchmark] + [row for rows in features for row in rows]
        if any(_time(d['retrieved_at']) > at for d in datasets):
            raise SourceError('history was retrieved after the judgment time (look-ahead)')
        rows = []
        for name, series in zip(ref['features'], features):
            current = _current_row(series, at)
            for row in series:
                row = dict(row)
                if row == current:
                    row['evidence_id'] = f'H:{c["asset_id"]}:{name}:{row["observed_at"]}'
                    evidence.append(
                        dict(
                            id=row['evidence_id'],
                            asset_ids=[c['asset_id']],
                            text=f'{row["source"]} {name} = {row["value"]} {row["unit"]} (관측 {row["observed_at"]})',
                            value=row['value'],
                            source_id=source_id,
                            definition=dict(measure=row['measure']),
                            observed_at=_time(row['observed_at']).date().isoformat(),
                            unit=row['unit'],
                            currency=row['currency'],
                            retrieved_at=row['retrieved_at'],
                        )
                    )
                rows.append(row)
        quote_row = _current_row(prices['rows'], at)
        if quote_row is None:
            raise SourceError('history has no price known at the judgment time')
        quote = dict(
            at=quote_row['at'],
            known_at=quote_row['known_at'],
            value=quote_row['value'],
            currency=prices['currency'],
            unit=prices['unit'],
            measure=prices['measure'],
            instrument_id=prices['instrument_id'],
        )
        quote_id = f'H:{c["asset_id"]}:price:{prices["instrument_id"]}:{quote_row["at"]}'
        evidence.append(
            dict(
                id=quote_id,
                asset_ids=[c['asset_id']],
                text=f'{prices["source"]} {prices["name"]} 종가 {quote_row["value"]} {prices["unit"]} ({quote_row["at"]})',
                value=quote_row['value'],
                source_id=source_id,
                definition=dict(measure=prices['measure']),
                observed_at=_time(quote_row['at']).date().isoformat(),
                unit=prices['unit'],
                currency=prices['currency'],
                retrieved_at=prices['retrieved_at'],
            )
        )
        c.update(
            prices=prices,
            benchmark=benchmark,
            features=rows,
            quote=quote,
            current_price_evidence_id=quote_id,
            history=dict(ref, sha256=history_sha256),
        )
    existing, added = {e['id'] for e in snapshot['evidence']}, []
    for e in evidence:
        if e['id'] not in existing:
            existing.add(e['id'])
            added.append(e)
    return plan, dict(snapshot, evidence=snapshot['evidence'] + added)


def run_cycle(plan, research_run, directory, *, ledger=None, previous=None, history=None, now=None):
    from .orchestrator import replay_ask
    from .decision_report import render_decision
    from .decision_journal import record

    if history is None:
        validate_plan(plan)
    root = Path(directory)
    if root.exists():
        raise SourceError('use a new investment run directory')
    run = replay_ask(research_run)
    snapshot = research_snapshot(run)
    if VERSION in DECIDED_AT_VERSIONS:
        decided = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        if decided < _time(snapshot['as_of']):
            raise SourceError('judgment time precedes the research cutoff')
        snapshot = dict(snapshot, research_as_of=snapshot['as_of'], as_of=decided.isoformat())
    if history is not None:
        from .history import replay_history

        verified = replay_history(history)
        sha = hashlib.sha256((Path(history) / 'history.json').read_bytes()).hexdigest()
        plan, snapshot = attach_history(plan, verified, sha, snapshot)
        validate_plan(plan)
    if ledger:
        from .decision_journal import feedback

        snapshot['strategy_feedback'] = feedback(ledger, snapshot['as_of'])
    result = evaluate(plan, snapshot)
    if previous:
        old = replay_cycle(previous)
        result['changes'] = changes(old, result)
    # Ledger conflicts are checked before creating the run output.
    if ledger:
        record(ledger, result, validate_only=True)
    root.mkdir(parents=True)
    save(root / 'input.json', dict(plan=plan, research=snapshot, previous=old if previous else None))
    save(root / 'decision.json', result)
    report = render_decision(result)
    (root / 'report.md').write_text(report, encoding='utf-8')
    save(
        root / 'run_manifest.json',
        dict(
            method_version=VERSION,
            artifacts={
                p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.iterdir()) if p.is_file()
            },
        ),
    )
    if ledger:
        record(ledger, result)
    return result


def replay_cycle(directory):
    from .decision_report import render_decision

    root = Path(directory)
    manifest = load(root / 'run_manifest.json')
    if manifest['method_version'] not in SUPPORTED_VERSIONS:
        raise SourceError('unsupported decision replay version')
    for name, h in manifest['artifacts'].items():
        if (
            name not in ('input.json', 'decision.json', 'report.md')
            or hashlib.sha256((root / name).read_bytes()).hexdigest() != h
        ):
            raise SourceError('decision artifact checksum mismatch')
    if set(manifest['artifacts']) != {'input.json', 'decision.json', 'report.md'}:
        raise SourceError('missing decision replay artifact')
    data = load(root / 'input.json')
    result = evaluate(data['plan'], data['research'], manifest['method_version'])
    if data['previous']:
        result['changes'] = changes(data['previous'], result)
    if result != load(root / 'decision.json') or render_decision(result) != (root / 'report.md').read_text(
        encoding='utf-8'
    ):
        raise SourceError('decision replay differs')
    return result


def changes(previous, current):
    if _time(previous['as_of']) >= _time(current['as_of']):
        raise SourceError('previous judgment must precede this judgment')
    if previous['synthetic'] != current['synthetic']:
        raise SourceError('previous judgment synthetic status differs')
    old = {r['asset_id']: r for r in previous['decisions']}
    return [
        dict(
            asset_id=r['asset_id'],
            previous=old[r['asset_id']]['action'],
            current=r['action'],
            reason=r['rationale'],
            signal_changed=old[r['asset_id']]['current_signal'] != r['current_signal'],
            strategy_changed=old[r['asset_id']]['strategy'] != r['strategy'],
        )
        for r in current['decisions']
        if r['asset_id'] in old and old[r['asset_id']]['action'] != r['action']
    ]
