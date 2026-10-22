"""Evidence-gated actions and an explicitly constrained new-cash scenario."""

from copy import deepcopy
from datetime import timedelta
from decimal import Decimal, ROUND_FLOOR
import hashlib
from pathlib import Path

from .backtest import VERSION as BACKTEST_VERSION, approval, condition_state, run_backtest
from .decision_data import VERSION, MARKETS, default_plan, digest, load, number, save, validate_plan, timestamp as _time
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
    return problems


def decide(c, snapshot, policy):
    at = _time(snapshot['as_of'])
    row = dict(
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
    if c['mode'] == 'unvalidated':
        row['blockers'] = c.get('gaps', []) + ['투자 가설·과거/최근 검증·현재 조건이 등록되지 않음']
        if c['held']:
            row['action'] = '보유 유지'
        return row
    s = c['strategy']
    row.update(
        strategy=deepcopy(s),
        thesis=s['hypothesis'],
        holding_horizon=s['holding_horizon'],
        instrument_id=c['prices']['instrument_id'],
        benchmark_instrument_id=c['benchmark']['instrument_id'],
        return_definition={k: c['prices'][k] for k in ('currency', 'return_kind', 'adjustment')},
        invalidation='다음 조건 중 하나가 실제 발생하면 가설을 재검토한다: '
        + '; '.join(r['feature'] + ' ' + r['op'] + ' ' + str(r['value']) for r in s['invalidations']),
    )
    refs = _references(c, snapshot)
    if not snapshot['synthetic']:
        if any(_time(d['retrieved_at']) > at for d in (c['prices'], c['benchmark'])) or any(
            _time(f['retrieved_at']) > at for f in c['features']
        ):
            refs.append('현재 판단 시점 이후에 확보한 자료다. 실제 당시 보유한 자료로만 승인한다.')
    signal = condition_state(s['conditions'], c['features'], at)
    price = condition_state(s['price_conditions'], c['features'], at)
    invalid = [condition_state([r], c['features'], at) for r in s['invalidations']]
    raw_quote = c['quote']
    quote = raw_quote if _time(raw_quote['at']) <= at and _time(raw_quote['known_at']) <= at else None
    # Current conditions need the same scoped numeric source references as the
    # research. Imported histories alone cannot certify today's observations.
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
        e = sources.get(f.get('evidence_id')) if f else None
        if (
            e is None
            or c['asset_id'] not in e['asset_ids']
            or e['value'] is None
            or number(e['value']) != number(check['value'])
            or e['unit'] != f['unit']
            or e['currency'] != f['currency']
            or e['definition']['measure'] != f['measure']
            or e['observed_at'] != _time(f['observed_at']).date().isoformat()
        ):
            reason = check['feature'] + ': 현재 수치의 검증 원문 연결이 없음'
            refs.append(reason)
            if check in invalid_checks:
                invalid_refs.append(reason)
    q = sources.get(c.get('current_price_evidence_id'))
    if quote is not None and (
        q is None
        or c['asset_id'] not in q['asset_ids']
        or q['value'] is None
        or number(q['value']) != number(quote['value'])
        or q['currency'] != quote['currency']
        or q['unit'] != quote['unit']
        or q['definition']['measure'] != quote['measure']
        or q['observed_at'] != _time(quote['at']).date().isoformat()
    ):
        refs.append('현재 투자상품 가격의 검증 원문 연결이 없음')
    row.update(
        current_signal=signal, price_state=price, current_price=quote, invalidation_checks=invalid, blockers=list(refs)
    )
    if quote is None or at - _time(quote['at']) > timedelta(days=c['max_price_age_days']):
        row['blockers'].append('실제 투자상품의 현재 가격이 미확보 또는 오래됨')
    if c['mode'] == 'quantitative':
        bt = run_backtest(c, at)
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
    invalidated = any(i['state'] == 'pass' for i in invalid) and not invalid_refs
    if invalidated:
        row.update(
            grade='F',
            action='매도 검토' if c['held'] else '신규 매수하지 않음',
            rationale='투자 가설을 무효화하는 조건이 실제 발생했다.',
        )
    elif refs or quote is None or at - _time(quote['at']) > timedelta(days=c['max_price_age_days']):
        row.update(
            grade='D',
            action='비중 축소 검토' if c['held'] else '신규 매수하지 않음',
            rationale='현재 판단에 필요한 원자료 또는 실제 상품 가격이 검증되지 않았다.',
        )
    elif status in ('failed', 'degraded'):
        row.update(
            grade='F',
            action='비중 축소 검토' if c['held'] else '신규 매수하지 않음',
            rationale='과거 검증 실패 또는 최근 성과 붕괴로 신규 매수를 중단한다.',
        )
    elif signal['state'] == 'fail' or price['state'] == 'fail':
        row.update(
            grade='F',
            action='보유 유지' if c['held'] else '조건 충족 대기',
            rationale='현재 매수 조건 또는 가격 조건이 충족되지 않았다.',
        )
    elif signal['state'] == 'unknown' or price['state'] == 'unknown':
        row.update(
            grade='D',
            action='보유 유지' if c['held'] else '조건 충족 대기',
            rationale='현재 신호가 확인되지 않아 조건 충족까지 기다린다.',
        )
    elif status == 'insufficient':
        row.update(
            grade='C',
            action='보유 유지' if c['held'] else '신규 매수하지 않음',
            rationale='과거 검증 표본 또는 우위가 충분하지 않아 신규 매수하지 않는다.',
        )
    else:
        grade = {'passed': 'A', 'partial': 'B', 'event_review': 'C'}[status]
        row.update(
            grade=grade,
            action='분할 매수' if grade == 'A' else '소액 매수',
            rationale='투자 논리·현재 조건·가격을 확인했고 '
            + ('과거와 최근 검증을 통과했다.' if grade == 'A' else '근거의 제한에 맞춰 소액만 배분한다.'),
        )
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


def evaluate(plan, snapshot):
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
    rows = [decide(c, snapshot, plan['policy']) for c in plan['candidates']]
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
        method_version=VERSION,
        backtest_version=BACKTEST_VERSION,
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
    result = evaluate(plan, snapshot)
    if run.input.get('previous_investment'):
        result['changes'] = changes(run.input['previous_investment'], result)
    return result


def run_cycle(plan, research_run, directory, *, ledger=None, previous=None):
    from .orchestrator import replay_ask
    from .decision_report import render_decision
    from .decision_journal import record

    validate_plan(plan)
    root = Path(directory)
    if root.exists():
        raise SourceError('use a new investment run directory')
    run = replay_ask(research_run)
    snapshot = research_snapshot(run)
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
    if manifest['method_version'] != VERSION:
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
    result = evaluate(data['plan'], data['research'])
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
