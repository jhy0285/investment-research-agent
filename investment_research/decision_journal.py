"""Immutable judgments, strategy revisions and matured recommendation outcomes.

Recommendation outcomes are hypothetical next-close trades, not broker fills.
Waiting/missing observations never become zero returns or losses.
"""

from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from .backtest import event_at, statistics
from .decision_data import (
    HORIZONS,
    digest,
    load,
    number,
    save,
    target,
    validate_dataset,
    validate_strategy,
    timestamp as _time,
)
from .investment_cycle import BUY_ACTIONS
from .sources import SourceError

VERSION = 'immutable_decision_journal_v1'


def record(ledger, result, *, validate_only=False):
    root = Path(ledger)
    if result.get('schema_version') != 'investment-decision-v1':
        raise SourceError('unsupported judgment journal record')
    judged = _time(result['as_of'])
    for row in result['decisions']:
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
    save(root / 'decisions' / (digest(result) + '.json'), result)


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


def review(ledger, datasets, as_of):
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
    # One report has one horizon for comparisons. All horizons stay in the
    # journal; no pooling a week outcome with a year outcome in grade statistics.
    for path, result in history:
        if path.stem != digest(result):
            raise SourceError('judgment journal checksum mismatch')
        judged = _time(result['as_of'])
        if judged > cutoff:
            continue
        for r in result['decisions']:
            if r['action'] not in BUY_ACTIONS or number(r['amount_krw']) <= 0:
                continue
            prices = by_id.get(r['instrument_id'])
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
                    elif any(bench[k] != prices[k] for k in ('currency', 'return_kind', 'adjustment', 'synthetic')):
                        raise SourceError('outcome market benchmark definition differs')
                    else:
                        rows = [
                            p for p in prices['rows'] if _time(p['at']) <= cutoff and _time(p['known_at']) <= cutoff
                        ]
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
                            key = (r['asset_id'], horizon, result['synthetic'])
                            independent = key not in last_exit or _time(event['entry_at']) > last_exit[key]
                            if independent:
                                last_exit[key] = _time(event['exit_at'])
                            out.update(
                                state='completed',
                                return_=event['return'],
                                benchmark_return=event['benchmark_return'],
                                excess_return=event['excess_return'],
                                entry_at=event['entry_at'],
                                exit_at=event['exit_at'],
                                drawdown=event['drawdown'],
                                independent=independent,
                                reason='다음 관측 진입을 가정한 추천 평가다. 실제 체결 수익은 아니다.',
                            )
                outcomes.append(out)
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
    )


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
