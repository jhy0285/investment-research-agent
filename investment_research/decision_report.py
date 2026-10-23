"""Plain Korean, conclusion-first reports with reproducible calculation details."""

from decimal import Decimal
from zoneinfo import ZoneInfo

from .backtest import BASE_LIMITATIONS
from .decision_data import number
from .sources import _time


def _text(value):
    return str(value).replace('|', '\\|').replace('\n', ' ').replace('<', '&lt;').replace('>', '&gt;')


def _money(value):
    return f'{number(value):,.0f}원'


def _pct(value):
    return '미계산' if value is None else f'{number(value)*100:+.2f}%'


def _state(value):
    return {
        'passed': '통과',
        'partial': '부분 통과',
        'failed': '실패',
        'degraded': '최근 악화',
        'insufficient': '검증 부족',
        'event_review': '사례 검토',
        'pass': '충족',
        'fail': '미충족',
        'unknown': '미확인',
    }.get(value, value)


def render_decision(result):
    rows = result['decisions']
    allocation = result['allocation']
    lines = [
        '# 오늘의 투자 결론',
        '',
        '판단 기준: ' + _time(result['as_of']).astimezone(ZoneInfo('Asia/Seoul')).isoformat() + ' (한국시간).',
        '',
    ]
    if result.get('research_as_of'):
        lines[-1:-1] = [
            '조사 기준: '
            + _time(result['research_as_of']).astimezone(ZoneInfo('Asia/Seoul')).isoformat()
            + ' (한국시간). 판단은 조사를 읽고 검토한 뒤의 시각에 내렸고, 그 시각까지 알려진 자료만 썼습니다.',
        ]
    if result['synthetic']:
        lines.extend(['**합성 데이터로 시스템 동작을 검증한 예제입니다. 현재 시장 추천이 아닙니다.**', ''])
    for r in rows[:3]:
        lines.append(f"**{r['rank']}위: {_text(r['name'])} — {r['action']} ({r['grade']}등급)**  ")
        lines.extend([_text(r['rationale']), ''])
    if not rows:
        lines.extend(['검증된 매수 후보가 없어 신규 매수하지 않습니다.', ''])
    lines.extend(
        ['## 신규 현금 ' + _money(allocation['new_cash_krw']) + '이 있다면', '', _text(allocation['scenario_note']), '']
    )
    for a in allocation['investments']:
        lines.append('- ' + _text(a['name']) + ': **' + _money(a['amount_krw']) + '** — ' + _text(a['reason']))
    lines.extend(
        [
            '- 현금 유지: **' + _money(allocation['cash_krw']) + '**',
            '',
            allocation['limitation'],
            '',
            '## 최종 투자 순위',
            '',
            result['ranking_basis'],
            '',
            '| 순위 | 자산 | 투자논리 | 과거검증 | 최근검증 | 현재신호 | 가격부담 | 최종판단 |',
            '|---|---|---|---|---|---|---|---|',
        ]
    )
    for r in rows:
        verification = _state(r.get('verification', 'insufficient'))
        historical = recent = verification
        if r['backtest']:

            def status(part):
                h = r['backtest']['periods'][part]['horizons'][r['holding_horizon']]
                if h['signal']['count'] < result['policy']['minimum_' + part]:
                    return '표본 부족'
                if (
                    number(h['signal']['mean']) <= 0
                    or number(h['mean_excess']) <= 0
                    or number(h['signal']['mean']) <= number(h['unconditional']['mean'])
                ):
                    return '우위 없음'
                return '평균 우위 확인'

            historical, recent = status('historical'), status('recent')
        lines.append(
            '| '
            + ' | '.join(
                map(
                    _text,
                    [
                        r['rank'],
                        r['name'],
                        '검토됨' if r['strategy'] else '미검증',
                        historical,
                        recent,
                        _state(r['current_signal']['state']),
                        _state(r['price_state']['state']),
                        r['action'],
                    ],
                )
            )
            + ' |'
        )
    for r in rows:
        lines.extend(
            [
                '',
                '## ' + _text(r['name']),
                '',
                '**한 줄 결론:** ' + _text(r['rationale']),
                '',
                '**왜 오를 수 있는가**',
                '',
            ]
        )
        lines.extend('- ' + _text(t) for t in r['reasons_up'])
        lines.extend(['', '**왜 떨어질 수 있는가**', ''])
        lines.extend('- ' + _text(t) for t in r['reasons_down'])
        lines.extend(
            [
                '',
                '**이미 가격에 반영됐는가:** 현재 가격 조건은 '
                + _state(r['price_state']['state'])
                + '입니다. 좋은 사업과 좋은 매수 가격을 구분합니다.',
                '',
                '**검증할 투자 가설:** ' + _text(r['thesis']),
            ]
        )
        if r['current_price']:
            lines.extend(
                [
                    '',
                    '당시 투자상품 기준가격: '
                    + _money(r['current_price']['value'])
                    + ' ('
                    + r['current_price']['at']
                    + '). 주문 체결가격은 별도입니다.',
                ]
            )
        if r['backtest']:
            bt = r['backtest']
            lines.extend(
                [
                    '',
                    '과거 가격 이력: '
                    + str(round(number(bt['history_years']), 1))
                    + '년. 거래비용을 차감하고 배당·원화 환산 정의를 확인합니다.',
                    '승률은 과거 표본에서 이익이 난 비율이며 미래의 성공 확률이 아닙니다.',
                ]
                + [x for x in bt['limitations'] if x not in BASE_LIMITATIONS]
                + [
                    '',
                    '| 구간 | 기간 | 성숙 신호 | 신호 평균 | 중앙값 | 승률 | 아무 날 평균 | 같은 계절 평균 | 같은 시점 시장 | 최대 중간 하락 |',
                    '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|',
                ]
            )
            for part in ('historical', 'validation', 'recent'):
                for horizon, study in bt['periods'][part]['horizons'].items():
                    stats = study['signal']
                    win = '미계산' if stats['win_rate'] is None else f"{number(stats['win_rate'])*100:.1f}%"
                    lines.append(
                        '| '
                        + ' | '.join(
                            [
                                (
                                    '과거 분석'
                                    if part == 'historical'
                                    else '독립 검증' if part == 'validation' else '최근 독립 검증'
                                ),
                                horizon,
                                str(stats['count']),
                                _pct(stats['mean']),
                                _pct(stats['median']),
                                win,
                                _pct(study['unconditional']['mean']),
                                _pct(study['same_season']['mean']),
                                _pct(study['paired_market']['mean']),
                                _pct(stats['worst_interim_drawdown']),
                            ]
                        )
                        + ' |'
                    )
            lines.extend(['', '<details><summary>평균 이익·손실, 최대 결과와 계산 근거</summary>', ''])
            for part in ('historical', 'validation', 'recent'):
                h = bt['periods'][part]['horizons'][r['holding_horizon']]
                s = h['signal']
                lines.append(
                    '- '
                    + part
                    + ': 평균 이익 '
                    + _pct(s['average_gain'])
                    + ', 평균 손실 '
                    + _pct(s['average_loss'])
                    + ', 최대 이익 '
                    + _pct(s['maximum_gain'])
                    + ', 가장 낮은 결과 '
                    + _pct(s['maximum_loss'])
                    + ', 시장 대비 평균 '
                    + _pct(h['mean_excess'])
                    + ', 단순 보유 '
                    + _pct(bt['periods'][part]['buy_and_hold'])
                    + '.'
                )
            lines.extend(
                [
                    '',
                    '조건 없는 비교 표본은 보유기간이 겹치는 설명용 통계입니다. 승인 표본은 겹침을 제외합니다.',
                    '',
                    '</details>',
                ]
            )
        else:
            lines.extend(
                [
                    '',
                    '과거 수익률은 계산하지 않았습니다. '
                    + (
                        '반복 표본이 없는 사건이므로 검토된 유사 사례와 실제 사업 근거로 C등급까지 평가했습니다.'
                        if r['mode'] == 'event'
                        else '검증되지 않은 이야기를 백테스트 성공으로 표시하지 않습니다.'
                    ),
                ]
            )
        if r.get('entry_plan'):
            p = r['entry_plan']
            lines.extend(
                [
                    '',
                    '**진입 방법:** 오늘 '
                    + _money(p['today_krw'])
                    + ', 다음 점검 '
                    + _money(p['next_review_krw'])
                    + ', 그다음 점검 '
                    + _money(p['following_review_krw'])
                    + '. '
                    + p['rule'],
                ]
            )
        lines.extend(
            [
                '',
                '**무엇이 발생하면 틀렸다고 인정하는가:** ' + _text(r['invalidation']),
                '',
                '**예상 보유기간:** ' + str(r['holding_horizon'] or '미등록'),
                '',
                '**판단을 제한하는 근거:**',
                '',
            ]
        )
        lines.extend('- ' + _text(t) for t in r['blockers'])
    lines.extend(['', '## 이전 판단과 비교', ''])
    if result.get('changes'):
        lines.extend(
            '- ' + _text(c['asset_id']) + ': ' + c['previous'] + ' → ' + c['current'] + '. ' + _text(c['reason'])
            for c in result['changes']
        )
    else:
        lines.append('연결된 이전 판단이 없거나 행동 판단에 변화가 없습니다.')
    lines.extend(
        [
            '',
            '## 시장 조사 범위와 남은 공백',
            '',
            '시장 전체를 고려하되 실제 자료와 방법이 연결된 범위만 평가했습니다. 원자료 수가 많다는 이유로 순위를 높이지 않았습니다.',
            '',
            '| 조사 대상 | 현재 범위 | 핵심 누락 |',
            '|---|---|---|',
        ]
    )
    for c in result['coverage']:
        lines.append('| ' + _text(c['name']) + ' | ' + c['status'] + ' | ' + _text('; '.join(c['missing'])) + ' |')
    lines.extend(
        [
            '',
            '전체 점검 목록: ' + ', '.join(result['market_checklist']) + '.',
            '은·산업금속·주요 기타 암호화폐·글로벌 부동산의 별도 현재 검증은 아직 연결되지 않았습니다.',
            '',
            '## 투자 일지와 다음 점검',
            '',
            '판단일·당시 가격·행동·등급·금액·근거·과거 검증·현재 신호·보유기간·무효화 조건을 decision.json에 보존합니다. '
            '1주·1개월·3개월·6개월·1년 결과는 해당 시점이 지난 뒤 실제 자료로 채웁니다. '
            '추천 평가와 실제 주문 체결 성과는 구분합니다. 전략 수정은 이전 기록을 고치지 않고 새 버전으로 검증합니다.',
            '',
        ]
    )
    return '\n'.join(lines)


def render_review(result):
    lines = [
        '# 투자 판단 사후검증',
        '',
        '평가 기준: ' + _time(result['as_of']).astimezone(ZoneInfo('Asia/Seoul')).isoformat() + ' (한국시간).',
        '',
        result['limitation'],
        '',
        '| 전략 버전 | 상태 | 성숙 표본 | 평균 수익 | 시장 대비 |',
        '|---|---|---:|---:|---:|',
    ]
    for key, s in result['strategies'].items():
        lines.append(
            '| '
            + ' | '.join(
                [
                    _text(key),
                    s['status'],
                    str(s['stats']['count']),
                    _pct(s['stats']['mean']),
                    _pct(s['stats']['mean_excess']),
                ]
            )
            + ' |'
        )
    lines.extend(
        [
            '',
            '## 등급별 실제 신호 결과',
            '',
            '| 기간 | 자료 | 등급 | 성숙 표본 | 평균 수익 | 승률 | 평균 손실 | 시장 대비 |',
            '|---|---|---|---:|---:|---:|---:|---:|',
        ]
    )
    for horizon, grades in result['grade_statistics'].items():
        for grade, kinds in grades.items():
            for kind, s in kinds.items():
                if not s['count']:
                    continue
                lines.append(
                    '| '
                    + ' | '.join(
                        [
                            horizon,
                            '합성 검증' if kind == 'synthetic' else '실제 자료',
                            grade,
                            str(s['count']),
                            _pct(s['mean']),
                            _pct(s['win_rate']),
                            _pct(s['average_loss']),
                            _pct(s['mean_excess']),
                        ]
                    )
                    + ' |'
                )
    lines.extend(['', '## 발견한 문제', ''])
    lines.extend('- ' + _text(t) for t in result['issues'])
    if not result['issues']:
        lines.append('등급 간 비교에 필요한 성숙 결과가 없거나 확인된 역전이 없습니다.')
    lines.extend(['', '## 이전 판단이 틀린 사례', ''])
    losers = [o for o in result['outcomes'] if o['state'] == 'completed' and number(o['return_']) < 0]
    for o in losers:
        lines.append(
            '- '
            + _text(o['asset_id'])
            + ' '
            + o['decision_at']
            + ' '
            + o['horizon']
            + ': '
            + _pct(o['return_'])
            + '. 당시 추천은 이 기간에 손실을 냈습니다. 전략 원자료·환경·비용을 점검합니다.'
        )
    if not losers:
        lines.append('현재 평가 가능한 기간에서 기록된 손실 사례가 없습니다. 미성숙 결과는 성공으로 세지 않습니다.')
    for key, s in result['strategies'].items():
        if s['diagnostics']:
            lines.extend(['', '### ' + _text(key) + ' 성과 차이 원인 점검', ''])
            lines.extend('- ' + _text(v) for v in s['diagnostics'].values())
    pending = sum(o['state'] == 'pending' for o in result['outcomes'])
    missing = sum(o['state'] == 'missing_data' for o in result['outcomes'])
    lines.extend(
        ['', f'평가시점 미도달: {pending}건. 자료 미확보: {missing}건. 해당 결과를 0% 또는 실패로 채우지 않습니다.', '']
    )
    return '\n'.join(lines)
