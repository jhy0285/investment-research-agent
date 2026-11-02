"""Immutable judgments, strategy revisions and matured recommendation outcomes.

Recommendation outcomes are hypothetical next-close trades, not broker fills.
Waiting/missing observations never become zero returns or losses.
"""

from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from .backtest import event_at, lower_confidence_bound, statistics
from .decision_data import (
    HORIZONS,
    comparable_benchmark,
    digest,
    load,
    number,
    require_tradable,
    save,
    target,
    validate_dataset,
    validate_strategy,
    timestamp as _time,
)
from .investment_cycle import BUY_ACTIONS
from .sources import SourceError
from .strategy_registry import read_chain, record_decision, verify_decisions, view

VERSION = 'immutable_decision_journal_v1'


def record(ledger, result, *, validate_only=False, now=None):
    root = Path(ledger)
    if result.get('schema_version') != 'investment-decision-v1':
        raise SourceError('unsupported judgment journal record')
    judged = _time(result['as_of'])
    for row in result['decisions']:
        shadow = row.get('shadow')
        if shadow is not None and (
            result.get('method_version') != 'investment_cycle_v4'
            or number(row['amount_krw']) != 0
            or row['action'] in BUY_ACTIONS
            or (shadow.get('tracked') is True and shadow.get('amount_krw') != '0')
        ):
            raise SourceError('a shadow record has amount zero, is not a buy and belongs to investment_cycle_v4')
        quote = row['current_price']
        if quote is not None and (_time(quote['at']) > judged or _time(quote['known_at']) > judged):
            raise SourceError('journal quote follows the judgment; cannot backdate a recommendation')
        s = row['strategy']
        if s is None:
            continue
        validate_strategy(s)
        version_path = root / 'strategies' / s['id'] / (s['version'] + '.json')
        if version_path.exists() and load(version_path) != s:
            raise SourceError('strategy conditions changed without a new version')
        parent = s.get('parent_sha256')
        existing = [load(p) for p in sorted((root / 'strategies' / s['id']).glob('*.json'))]
        if parent:
            matches = [old for old in existing if digest(old) == parent]
            if not matches or matches[0]['version'] == s['version']:
                raise SourceError('strategy revision parent is missing or version did not change')
            if _time(s['locked_at']) <= _time(matches[0]['locked_at']):
                raise SourceError('revised strategy must freeze after its parent')
        elif existing and not version_path.exists():
            raise SourceError('new strategy version must link its previous immutable definition')
    if validate_only:
        return
    # Conflicts checked for all rows before writing any strategy or judgment.
    for row in result['decisions']:
        if row['strategy']:
            s = row['strategy']
            save(root / 'strategies' / s['id'] / (s['version'] + '.json'), s)
    sha = digest(result)
    save(root / 'decisions' / (sha + '.json'), result)
    if result.get('method_version') == 'investment_cycle_v4':
        record_decision(root, sha, result['as_of'], now=now)


def _diagnostics(outcomes):
    return dict(
        market_structure='가격 표본만으로 구조 변화를 확정할 수 없음',
        rates='금리 환경 원자료의 추가 비교 필요',
        costs='등록한 양방향 거래비용과 실제 체결 비용 대조 필요',
        instrument='현물 수급과 투자상품 구조·환율·분배금 차이 검토',
        entry_delay='현재 평가는 다음 관측 진입이다. 실제 주문·지연은 별도 비교 필요',
        revisions='관측의 known_at·vintage 및 이전 자료 해시 대조',
        overfitting='전략 trial_count와 새 버전의 독립기간 검사',
        sample='성숙 표본 수와 서로 겹치는 추천 제외',
        chance='시장 대비 우위의 신뢰구간과 정책·경쟁 변화 추가 검토',
    )


def review(ledger, datasets, as_of, source=None):
    """Score matured buy recommendations. `source` records where outcome prices came from, when not a file."""
    cutoff = _time(as_of)
    if not isinstance(datasets, list):
        raise SourceError('review datasets must be a list')
    by_id = {}
    for d in datasets:
        validate_dataset(d)
        if d['instrument_id'] in by_id:
            raise SourceError('duplicate outcome instrument')
        if not d['synthetic'] and _time(d['retrieved_at']) > cutoff:
            raise SourceError('actual outcome data were retrieved after this review')
        by_id[d['instrument_id']] = d
    root = Path(ledger)
    outcomes = []
    last_exit = {}
    history = [(p, load(p)) for p in sorted((root / 'decisions').glob('*.json'))]
    history.sort(key=lambda item: (_time(item[1]['as_of']), item[0].name))
    verify_decisions(root, [(p.stem, r) for p, r in history])
    shadow_outcomes = []
    last_shadow_exit = {}

    def score(path, result, judged, r, sink, exits, independence, extra, reason):
        prices = by_id.get(r['instrument_id'])
        if prices is not None:
            require_tradable(prices)  # a benchmark-only series is never the instrument that was bought
        for horizon in HORIZONS:
            out = dict(
                judgment_sha256=path.stem,
                asset_id=r['asset_id'],
                grade=r['grade'],
                strategy_id=r['strategy']['id'],
                strategy_version=r['strategy']['version'],
                horizon=horizon,
                decision_at=result['as_of'],
                state='pending',
                return_=None,
                benchmark_return=None,
                excess_return=None,
                entry_at=None,
                exit_at=None,
                independent=False,
                synthetic=result['synthetic'],
                **extra,
            )
            due = target(judged, horizon)
            if due > cutoff:
                out['reason'] = '아직 평가 시점에 도달하지 않음'
            elif prices is None:
                out.update(state='missing_data', reason='투자상품의 사후 가격 미확보')
            else:
                definition = r.get('return_definition')
                if definition is None:
                    raise SourceError('journal lacks original outcome return definition')
                if (
                    prices['asset_id'] != r['asset_id']
                    or prices['currency'] != definition['currency']
                    or prices['return_kind'] != definition['return_kind']
                    or prices['adjustment'] != definition['adjustment']
                    or prices['synthetic'] != result['synthetic']
                ):
                    raise SourceError('outcome exposure/currency/return definition or synthetic status differs')
                bench = by_id.get(r['benchmark_instrument_id'])
                if bench is None:
                    out.update(state='missing_data', reason='동일 시점 비교 시장 가격 미확보')
                elif not comparable_benchmark(prices, bench):
                    raise SourceError('outcome market benchmark definition differs')
                else:
                    rows = [p for p in prices['rows'] if _time(p['at']) <= cutoff and _time(p['known_at']) <= cutoff]
                    b = [p for p in bench['rows'] if _time(p['at']) <= cutoff and _time(p['known_at']) <= cutoff]
                    # Lock next observation; no favorable later entry selection.
                    idx = next((i for i, p in enumerate(rows) if _time(p['at']) > judged), None)
                    event = (
                        None
                        if idx is None
                        else event_at(
                            rows,
                            idx,
                            horizon,
                            cutoff + timedelta(microseconds=1),
                            r['strategy']['cost_bps_per_side'],
                            b,
                        )
                    )
                    if idx is None or _time(rows[idx]['at']) - judged > timedelta(days=7):
                        out.update(state='missing_data', reason='판단 다음 7일 이내 진입 가격 없음')
                    elif event is None:
                        out.update(
                            state='pending' if target(_time(rows[idx]['at']), horizon) > cutoff else 'missing_data',
                            reason='진입 후 보유기간이 미성숙하거나 정해진 평가일 가격 미확보',
                        )
                    else:
                        key = independence(horizon)
                        independent = key not in exits or _time(event['entry_at']) > exits[key]
                        if independent:
                            exits[key] = _time(event['exit_at'])
                        out.update(
                            state='completed',
                            return_=event['return'],
                            benchmark_return=event['benchmark_return'],
                            excess_return=event['excess_return'],
                            entry_at=event['entry_at'],
                            exit_at=event['exit_at'],
                            drawdown=event['drawdown'],
                            independent=independent,
                            reason=reason,
                        )
            sink.append(out)

    # One report has one horizon for comparisons. All horizons stay in the
    # journal; no pooling a week outcome with a year outcome in grade statistics.
    for path, result in history:
        if path.stem != digest(result):
            raise SourceError('judgment journal checksum mismatch')
        judged = _time(result['as_of'])
        if judged > cutoff:
            continue
        for r in result['decisions']:
            if r['action'] in BUY_ACTIONS and number(r['amount_krw']) > 0:
                score(
                    path,
                    result,
                    judged,
                    r,
                    outcomes,
                    last_exit,
                    lambda horizon, r=r, result=result: (r['asset_id'], horizon, result['synthetic']),
                    {},
                    '다음 관측 진입을 가정한 추천 평가다. 실제 체결 수익은 아니다.',
                )
            elif (r.get('shadow') or {}).get('tracked'):
                # Zero-amount judgment: scored like a buy but kept apart, and independent per strategy
                # (another strategy holding the same asset must not use up this one's sample).
                score(
                    path,
                    result,
                    judged,
                    r,
                    shadow_outcomes,
                    last_shadow_exit,
                    lambda horizon, r=r, result=result: (
                        r['strategy']['id'],
                        r['strategy']['version'],
                        r['asset_id'],
                        horizon,
                        result['synthetic'],
                    ),
                    dict(track=r['shadow']['track'], registration_sha256=r['shadow']['registration_sha256']),
                    '다음 관측 진입을 가정한 섀도 평가다. 금액 0의 기록이며 실제 매수·체결 수익이 아니다.',
                )
    grade_stats = {}
    strategy_stats = {}
    issues = []
    for horizon in HORIZONS:
        mature = [o for o in outcomes if o['horizon'] == horizon and o['state'] == 'completed' and o['independent']]
        grades = {}
        for grade in ('A', 'B', 'C'):
            subset = [o for o in mature if o['grade'] == grade]
            # Separate synthetic from real in the entire ledger.
            grades[grade] = {
                kind: _outcome_stats([o for o in subset if o['synthetic'] == (kind == 'synthetic')])
                for kind in ('real', 'synthetic')
            }
        grade_stats[horizon] = grades
        for kind in ('real', 'synthetic'):
            a, c = grades['A'][kind], grades['C'][kind]
            if a['count'] and c['count'] and number(a['mean']) < number(c['mean']):
                issues.append(horizon + ' ' + kind + ': A등급의 평균 성과가 C등급보다 낮음. 등급 규칙을 재검토한다.')
    for _, result in history:
        if _time(result['as_of']) > cutoff:
            continue
        for r in result['decisions']:
            s = r['strategy']
            if s is None:
                continue
            key = s['id'] + '/' + s['version'] + ('/synthetic' if result['synthetic'] else '/real')
            subset = [
                o
                for o in outcomes
                if o['strategy_id'] == s['id']
                and o['strategy_version'] == s['version']
                and o['horizon'] == s['holding_horizon']
                and o['state'] == 'completed'
                and o['independent']
                and o['synthetic'] == result['synthetic']
            ]
            stats = _outcome_stats(subset)
            minimum = result['policy']['minimum_live']
            recent = subset[-minimum:]
            negative = recent and number(_outcome_stats(recent)['mean_excess']) <= 0
            # A recent failed gate overrides an earlier successful backtest.
            state = '승인' if r.get('verification') in ('passed', 'partial') else '검증중'
            if r.get('verification') in ('failed', 'degraded'):
                state = '경고'
            if stats['count'] >= minimum:
                if negative:
                    state = (
                        '폐기 후보' if stats['count'] >= 2 * minimum and number(stats['mean_excess']) <= 0 else '경고'
                    )
                elif r.get('verification') == 'passed':
                    # Require live market excess lower CI > zero too.
                    from .backtest import _interval

                    interval = _interval([number(o['excess_return']) for o in subset])
                    if interval and number(interval[0]) > 0:
                        state = '강한 승인'
            strategy_stats[key] = dict(
                status=state,
                stats=stats,
                reason='성숙하고 겹치지 않는 동일 버전 신호로 평가한다.',
                diagnostics=_diagnostics(subset) if state in ('경고', '폐기 후보') else None,
            )
    strategy_stats.update(_shadow_strategies(root, history, shadow_outcomes, cutoff))
    return dict(
        schema_version='investment-review-v1',
        method_version=VERSION,
        as_of=cutoff.isoformat(),
        outcomes=outcomes,
        grade_statistics=grade_stats,
        strategies=strategy_stats,
        issues=issues,
        input_sha256=digest(datasets),
        judgment_sha256=[p.stem for p, r in history if _time(r['as_of']) <= cutoff],
        limitation='추천 신호의 가정 평가다. 중복 추천을 독립 성공으로 세지 않고 미성숙 결과를 제외한다.',
        # Present only when the prices came from a verified history run, so file-based reviews are unchanged.
        **({'price_source': source} if source else {}),
        # Present only when zero-amount shadow judgments exist, so journals without them review exactly as before.
        **(
            {
                'shadow_outcomes': shadow_outcomes,
                'shadow_limitation': SHADOW_LIMITATION,
            }
            if shadow_outcomes
            else {}
        ),
    )


SHADOW_LIMITATION = (
    '섀도 판단은 금액 0의 기록이며 실제 매수·체결 결과가 아니다. 위 실제 매수 통계와 섞지 않고 전략별로 따로 센다. '
    '판단을 실행한 시점에 신호가 켜져 있던 경우만 기록되므로, 실행하지 않은 주(週)의 신호는 표본에 없다. '
    '대조군(백테스트에서 승인받지 못한 전략)의 결과는 승인 문턱의 점검용이며 문턱을 바꾸는 근거로 쓰지 않는다.'
)


def promotion_gate(root, events, registration, track, subset):
    """Whether a strategy's first N independent matured shadow outcomes clear its registered gate.

    The gate is read once, at the N-th outcome, and never re-run on later data:
    re-testing every time a new outcome matures would let a lucky streak cross the
    line by chance. The corrected bound divides the tail probability by the number
    of strategies registered by that look (family size K), because the more
    strategies are watched the more of them clear a plain 95% bound by luck.
    """
    rule = registration['promotion_rule']
    look_n, recent_n = rule['minimum_independent'], rule['recent_n']
    gate = dict(
        rule=rule,
        track=track,
        strategy_sha256=registration['strategy_sha256'],
        registration_sha256=registration['registration_sha256'],
        n=len(subset),
        look_n=look_n,
        criteria_met=False,
        eligible=False,
        reasons=[],
    )
    if len(subset) < look_n:
        gate['reasons'].append(f'독립 성숙 섀도 표본 {len(subset)}/{look_n}개')
        return gate
    first = subset[:look_n]
    excess = [number(o['excess_return']) for o in first]
    look = first[-1]['exit_at']
    family = view(root, look, events=events)['family_size']
    quantile = Decimal(rule['one_sided_alpha']) / family
    resamples = max(10000, 800 * family)
    lower = lower_confidence_bound(excess, quantile, resamples)
    mean = sum(excess, Decimal(0)) / look_n
    recent_mean = sum(excess[look_n - recent_n :], Decimal(0)) / recent_n
    gate.update(
        look_exit_at=look,
        family_size=family,
        quantile=str(quantile),
        resamples=resamples,
        mean_excess=str(mean),
        recent_mean_excess=str(recent_mean),
        lower_bound=None if lower is None else str(lower),
    )
    if lower is None:
        gate['reasons'].append('시험한 후보 수에 비해 재추출 횟수가 부족해 보정한 하한을 계산하지 못함')
    elif lower <= 0:
        gate['reasons'].append('시장 대비 평균 초과수익의 보정한 하한이 0 이하')
    if recent_mean <= 0:
        gate['reasons'].append('최근 표본의 시장 대비 평균 초과수익이 0 이하')
    gate['criteria_met'] = lower is not None and lower > 0 and recent_mean > 0
    gate['eligible'] = gate['criteria_met'] and track == 'candidate' and registration['status'] == 'active'
    if gate['criteria_met'] and not gate['eligible']:
        gate['reasons'].append(
            '기준을 충족했지만 승격 대상이 아니다(백테스트에서 승인받지 못한 대조군이거나 폐기한 전략). 문턱을 바꾸는 근거로 쓰지 않는다.'
        )
    return gate


def _shadow_strategies(root, history, shadow_outcomes, cutoff):
    """Per-strategy status of the shadow record, kept under its own `…/shadow_real|shadow_synthetic` key."""
    latest = {}
    for _, result in history:
        if _time(result['as_of']) > cutoff:
            continue
        for r in result['decisions']:
            if (r.get('shadow') or {}).get('tracked'):
                s = r['strategy']
                latest[
                    s['id'] + '/' + s['version'] + ('/shadow_synthetic' if result['synthetic'] else '/shadow_real')
                ] = (
                    result,
                    r,
                )
    if not latest:
        return {}
    events = read_chain(root)
    registered = view(root, cutoff.isoformat(), events=events)['strategies']
    out = {}
    for key, (result, r) in latest.items():
        s = r['strategy']
        subset = [
            o
            for o in shadow_outcomes
            if o['strategy_id'] == s['id']
            and o['strategy_version'] == s['version']
            and o['horizon'] == s['holding_horizon']
            and o['state'] == 'completed'
            and o['independent']
            and o['synthetic'] == result['synthetic']
        ]
        registration = registered.get(s['id'] + '/' + s['version'])
        if registration is None or registration['registration_sha256'] != r['shadow']['registration_sha256']:
            raise SourceError('shadow judgment refers to a registration that is not in the journal chain')
        gate = promotion_gate(root, events, registration, r['shadow']['track'], subset)
        stats = _outcome_stats(subset)
        live = registration['promotion_rule']['recent_n']
        recent = subset[-live:]
        negative = recent and number(_outcome_stats(recent)['mean_excess']) <= 0
        state = '검증중'
        if stats['count'] >= live and negative:
            state = '폐기 후보' if stats['count'] >= 2 * live and number(stats['mean_excess']) <= 0 else '경고'
        elif gate['eligible']:
            state = '승인'
        if gate['eligible'] and state in ('경고', '폐기 후보'):
            # Judgments recorded before the look can mature afterwards. If they turn the record bad, the
            # earlier pass no longer stands.
            gate['eligible'] = False
            gate['reasons'].append(
                '기준을 충족했지만 이후 성숙한 섀도 표본이 나빠져(' + state + ') 승격 자격을 철회한다.'
            )
        out[key] = dict(
            status=state,
            stats=stats,
            source='shadow',
            track=r['shadow']['track'],
            promotion=gate,
            reason='금액 0의 섀도 판단 중 성숙하고 겹치지 않는 동일 버전 신호로 평가한다. 실제 매수 통계와 섞지 않는다.',
            diagnostics=_diagnostics(subset) if state in ('경고', '폐기 후보') else None,
        )
    return out


def _outcome_stats(rows):
    result = statistics([{'return': r['return_'], 'drawdown': r['drawdown']} for r in rows])
    result['mean_excess'] = (
        str(sum((number(r['excess_return']) for r in rows), Decimal(0)) / len(rows)) if rows else None
    )
    return result


def persist_review(ledger, result):
    save(Path(ledger) / 'reviews' / (digest(result) + '.json'), result)


def feedback(ledger, as_of):
    cutoff = _time(as_of)
    reviews = []
    for path in sorted((Path(ledger) / 'reviews').glob('*.json')):
        r = load(path)
        if path.stem != digest(r) or r.get('method_version') != VERSION:
            raise SourceError('strategy feedback review checksum/version mismatch')
        if _time(r['as_of']) <= cutoff:
            reviews.append(r)
    return max(reviews, key=lambda r: _time(r['as_of']))['strategies'] if reviews else {}
