"""Concrete Korean stock-pick report. Numbers come only from the computed result."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from . import stock_model as model

PERIOD_NAMES = dict(historical='과거', validation='독립 검증', recent='최근')


def _q(x, digits):
    return Decimal(x).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)


def pct(x, digits=1, sign=True):
    if x is None:
        return '확인 불가'
    v = _q(Decimal(x) * 100, digits)
    return (f'{v:+,.{digits}f}%' if sign else f'{v:,.{digits}f}%')


def pp(x, digits=2):
    return '확인 불가' if x is None else f'{_q(Decimal(x) * 100, digits):+,.{digits}f}%p'


def mult(x, digits=1):
    return '-' if x is None else f'{_q(x, digits):,.{digits}f}배'


def plain_pct(x, digits=1):
    return '-' if x is None else f'{_q(x, digits):,.{digits}f}%'


def krw(x):
    return f'{int(_q(x, 0)):,}원'


def price(x, currency):
    if x is None:
        return '확인 불가'
    return f'{int(_q(x, 0)):,}원' if currency == 'KRW' else f'${_q(x, 2):,.2f}'


def _local(iso):
    dt = datetime.fromisoformat(iso)
    from zoneinfo import ZoneInfo
    return dt.astimezone(ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d %H:%M')


def _ym(month):
    return f'{month[:4]}년 {int(month[5:])}월'


def _row_by_code(m):
    return {r['code']: r for r in m.get('ranking', [])}


def _alloc(result):
    return {(l['market'], l['code']): l for l in result['allocation']['lines']}


def _headline(result):
    lines = ['## 한 줄 결론', '']
    alloc = _alloc(result)
    for mk, m in result['markets'].items():
        g = m['grade']
        names = ', '.join(m['names'][c] for c in m['picks']) or '없음'
        invested = sum((alloc[(mk, c)]['amount_krw'] for c in m['picks'] if (mk, c) in alloc), Decimal(0))
        if g['grade'] == 'D':
            lines.append(f'- **{m["name"]}: 등급 {g["grade"]} · {g["status"]}** → 이 규칙으로는 이번 달 신규 매수 0원. '
                         f'규칙 상위 종목(매수 보류, 관심 목록): {names}.')
        else:
            lines.append(f'- **{m["name"]}: 등급 {g["grade"]} · {g["status"]}** → {len(m["picks"])}종목 매수 예시 {krw(invested)}. 추천: {names}.')
    a = result['allocation']
    lines += ['', f'예산 {krw(a["budget_krw"])} 중 **{krw(a["invested_krw"])} 매수 예시, {krw(a["cash_krw"])} 현금**. '
              '등급은 아래 과거·독립·최근 검증으로 정했고 종목은 매달 같은 규칙으로 바뀐다.', '']
    failed = [m for m in result['markets'].values() if m['grade']['grade'] == 'D' and 'backtest' in m]
    if failed:
        lines += ['**등급 D가 뜻하는 것:** 이 규칙으로 고른 5종목이 같은 후보 대형주를 골고루 산 것보다 낫다는 근거가 과거·검증·최근 기록에서 나오지 않았다. '
                  '종목을 골라 사는 이유가 검증되지 않았다는 뜻이며, 아래 종목이 나쁘다는 판정은 아니다. 이럴 때의 기본값은 개별 종목 대신 '
                  '시장 전체에 나눠 담는 것(예: 지수 ETF)이고, 아래 목록은 관심 종목으로만 보고 개별 분석(`ask "종목명 지금 어때?"`)으로 확인한다.', '']
    return lines


def _pick_table(result):
    alloc = _alloc(result)
    lines = ['## 이번 달 규칙 상위 종목', '',
             '| 시장 | 순위 | 종목 | 섹터 | 기준가 | 최근 1년 수익률 (직전 1개월 제외) | 연 변동성 | 10개월 평균선 대비 | PER | PBR | 배당수익률 | 예시 수량 | 예시 금액 |',
             '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for mk, m in result['markets'].items():
        rows = _row_by_code(m)
        for i, c in enumerate(m['picks'], 1):
            r, v, a = rows[c], m['valuation'].get(c, {}), alloc.get((mk, c))
            qty = f'{a["shares"]}주' if a and a['shares'] else ('0주' if a else '-')
            amount = krw(a['amount_krw']) if a and a['shares'] else (a['note'] if a and a.get('note') else '-')
            lines.append(f'| {m["name"]} | {i} | **{m["names"][c]}** ({c}) | {m["sectors"][c]} | '
                         f'{price(m["prices"].get(c), m["currency"])} | {pct(r["momentum"])} | '
                         f'{pct(r["volatility"] * Decimal(12).sqrt(), sign=False)} | {pct(r["trend_gap"])} | '
                         f'{mult(v.get("per"))} | {mult(v.get("pbr"), 2)} | {plain_pct(v.get("dividend_yield"), 2)} | {qty} | {amount} |')
    if not any(m['picks'] for m in result['markets'].values()):
        lines.append('| - | - | 이번 달 조건을 통과한 종목 없음 | | | | | | | | | | |')
    lines += ['', '기준가는 제공자 표시 최근 종가다. 실제 체결은 다음 거래일 시가라 수량·금액이 달라질 수 있다. '
              'PER·PBR·배당은 현재 제공자 값으로 **선정에는 쓰지 않았고** 가격 부담을 읽는 참고값이다.', '']
    return lines


def _explain(result):
    lines = ['## 종목별 설명', '']
    for mk, m in result['markets'].items():
        if not m['picks']:
            continue
        rows, n = _row_by_code(m), m.get('eligible')
        next_month = model.shift(m['signal_month'], 1)
        for i, c in enumerate(m['picks'], 1):
            r, v = rows[c], m['valuation'].get(c, {})
            lines.append(f'### {m["name"]} {i}. {m["names"][c]} ({c} · {m["sectors"][c]})')
            lines.append('')
            lines.append(f'- **왜 골랐나:** 직전 1개월을 뺀 최근 12개월 동안 {pct(r["momentum"])} 움직였다. '
                         f'후보 {n}개 중 상승 강도는 상위 {pct(1 - r["momentum_pct"], 0, False)}, '
                         f'가격 흔들림이 작은 정도는 상위 {pct(1 - r["low_vol_pct"], 0, False)}이다. '
                         f'종합점수 {_q(r["score"], 3)}로 전체 {r["rank"]}위.')
            lines.append(f'- **지금 추세:** 10개월 평균 가격보다 {pct(r["trend_gap"])} 위에 있고, 지난달 한 달 수익률은 {pct(r["return_1m"])}다.')
            per = v.get('per')
            note = ''
            if v.get('eps_negative'):
                note = ' 제공자 EPS가 0 이하라 이익 기준 가격 판단이 어렵다.'
            elif per is not None and m.get('median_per') and per > 2 * m['median_per']:
                note = f' 후보군 PER 중앙값({mult(m["median_per"])})의 두 배를 넘어 **이익 대비 가격 부담이 크다.**'
            elif per is not None and m.get('median_per') and per < m['median_per']:
                note = f' 후보군 PER 중앙값({mult(m["median_per"])})보다 낮다. 다만 낮은 배수는 이익이 정점일 때도 나타난다.'
            consensus = (f' · 컨센서스 EPS 기준 {mult(v["consensus_multiple"])}(제공자 값, 작성일·기간 미공개)'
                         if v.get('consensus_multiple') else '')
            lines.append(f'- **가격 부담:** PER {mult(per)} · PBR {mult(v.get("pbr"), 2)} · 배당 {plain_pct(v.get("dividend_yield"), 2)}{consensus}.{note}')
            high = v.get('high_52w')
            cur = m['prices'].get(c)
            from_high = f', 52주 고점 대비 {pct(cur / high - 1)}' if high and cur else ''
            lines.append(f'- **위험:** 연 변동성 {pct(r["volatility"] * Decimal(12).sqrt(), sign=False)}, '
                         f'최근 12개월 월말 기준 고점 대비 최대 하락 {pct(r["drawdown_12m"])}{from_high}. '
                         f'변동성이 크면 한 달에 그만큼 크게 빠질 수 있다.')
            extreme = m.get('extreme', {}).get(c)
            if extreme:
                lines.append(f'- **자료 확인 필요:** {", ".join(sorted(extreme))}에 한 달 ±50% 이상 움직였다. 실제 급등락인지 액면분할·병합이 '
                             '가격에 덜 반영된 것인지 원자료로 확인 전까지 이 종목의 점수를 그대로 믿지 않는다.')
            lines.append(f'- **언제 팔까:** {_ym(next_month)} 말 종가로 다시 계산해 상위 {model.PARAMS["top_n"]}위 안에 없거나 '
                         f'10개월 평균선 아래로 내려가면 그다음 첫 거래일에 팔고 새 1~5위로 교체한다. 손절선은 검증하지 않아 넣지 않았다.')
            lines.append('')
    return lines


def _validation(result):
    lines = ['## 이 규칙은 과거에 실제로 통했나', '',
             '매달 말 위 규칙으로 5종목을 고르고 **다음 달 첫 거래일 시가에 사서 그다음 달 첫 거래일 시가에 판다**고 가정했다. '
             '신호를 만든 종가로 산 것처럼 계산하지 않는다. 편도 거래비용을 차감했고, 10개월 평균선 아래라 빈 자리는 현금(이자 0%)으로 둔다. '
             '비교 대상은 같은 후보군을 매달 똑같이 나눠 산 **동일가중**과 시장 **지수**다. 같은 후보군 동일가중 대비 성과가 이 규칙의 실제 실력에 더 가깝다.', '']
    for mk, m in result['markets'].items():
        if 'backtest' not in m:
            lines += [f'### {m["name"]}', '', '- 가격 이력이 부족해 검증하지 못했다.', '']
            continue
        b, g = m['backtest'], m['grade']
        lines += [f'### {m["name"]} · 비교 지수: {m["benchmark"]["name"]} · 비용 편도 {Decimal(m["cost_bps"]) / 100}%', '',
                  '| 구간 | 보유 기간 | 개월 | 연환산 | 누적 | 최대 낙폭 | 동일가중 누적 | 지수 누적 | 동일가중 대비 월평균 초과 (95% 구간) | 지수 대비 월평균 초과 | 동일가중보다 좋았던 달 |',
                  '|---|---|---|---|---|---|---|---|---|---|---|']
        for key in ('historical', 'validation', 'recent', 'all'):
            s = b['periods'][key] if key != 'all' else b['all']
            if not s.get('months'):
                lines.append(f'| {PERIOD_NAMES.get(key, "전체")} | - | 0 | | | | | | | | |')
                continue
            ci = s['interval_excess_equal_weight']
            ci_text = f' ({pp(ci[0])} ~ {pp(ci[1])})' if ci else ''
            lines.append(f'| {PERIOD_NAMES.get(key, "전체")} | {s["start"]} ~ {s["end"]} | {s["months"]} | {pct(s["annualized"])} | '
                         f'{pct(s["cumulative"], 0)} | {pct(s["max_drawdown"])} | {pct(s["cumulative_equal_weight"], 0)} | {pct(s["cumulative_index"], 0)} | '
                         f'{pp(s["mean_excess_equal_weight"])}{ci_text} | {pp(s["mean_excess_index"])} | {pct(s["hit_rate_equal_weight"], 0, False)} |')
        d = b['pooled_double_cost']
        lines += ['', f'- 비용을 두 배(편도 {Decimal(m["cost_bps"]) * 2 / 100}%)로 잡아도 과거+독립 검증 동일가중 대비 월평균 초과는 {pp(d.get("mean_excess_equal_weight"))}, '
                  f'최근은 {pp(b["recent_double_cost"].get("mean_excess_equal_weight"))}다.',
                  f'- 평균 월 교체 비중 {pct(b["all"].get("average_turnover"), 0, False)}, 평균 현금 비중 {pct(b["all"].get("average_cash"), 0, False)}. '
                  f'자료 공백으로 제외한 달 {b["excluded"]["incomplete"]}개, 아직 결과가 나오지 않은 달 {b["excluded"]["pending"]}개.',
                  f'- **등급 {g["grade"]} ({g["status"]})**: ' + ' '.join(g['reasons']), '']
    lines += ['월평균 초과수익의 95% 구간은 달별 결과를 2,000번 다시 뽑아 계산한 범위다. 0보다 크면 운이 아니라 규칙의 효과일 가능성이 상대적으로 높다는 뜻이고, '
              '과거 승률이 미래 확률은 아니다.', '']
    return lines


def _sizing(result):
    a = result['allocation']
    fx = result.get('fx')
    lines = ['## 금액을 이렇게 나눴다', '',
             f'- 예산 {krw(a["budget_krw"])}을 요청한 시장 수로 똑같이 나눴다(시장당 {krw(a["sleeve_krw"])}). 시장 안에서는 5칸으로 균등하게 나눈다.',
             f'- 한 종목 최대 금액은 등급 B면 예산의 20%, C면 5%, D면 0원이다. 1주 단위로 계산하고 남는 돈은 현금으로 둔다.']
    if fx:
        lines.append(f'- 미국 주식은 원/달러 {fx[1]}원({fx[0]}, 제공자 표시 매매기준율) 기준으로 환산했다. 실제 환전 스프레드·수수료와 환율 변동은 별도다.')
    lines += ['- 이 예시는 입력한 예산이 **1년 이상 써도 되지 않는 여유자금**이라는 가정이다. 비상금·대출·곧 쓸 돈·기존 보유 종목(예: 이미 반도체가 많은지)은 반영하지 않았다.', '']
    return lines


def _history(result):
    lines = ['## 지난 추천과 비교', '']
    any_line = False
    for mk, m in result['markets'].items():
        prev = m.get('previous')
        if prev:
            any_line = True
            name = lambda codes: ', '.join(m['names'].get(c, c) for c in codes) or '없음'
            lines.append(f'- {m["name"]} ({_ym(prev["signal_month"])} 추천 대비): 유지 {name(prev["kept"])} · 신규 {name(prev["added"])} · 제외 {name(prev["removed"])}')
    matured = [e for e in result.get('journal', []) if e['status'] == '성숙']
    for e in matured:
        any_line = True
        m = result['markets'].get(e['market'], {})
        ew = pp(e['gross'] - e['equal_weight']) if e.get('equal_weight') is not None else '확인 불가'
        lines.append(f'- {m.get("name", e["market"])} {_ym(e["signal_month"])} 추천: {e["entry"]}~{e["exit"]} 수익 {pct(e["gross"])}, '
                     f'지수 {pct(e["index"])}, 동일가중 대비 {ew}')
    pending = [e for e in result.get('journal', []) if e['status'] != '성숙']
    if pending:
        any_line = True
        lines.append(f'- 아직 결과가 나오지 않은 기록 {len(pending)}건(미성숙·자료 부족). 0%로 채우지 않는다.')
    for mk, m in result['markets'].items():
        live = m.get('live') or {}
        if live.get('months'):
            lines.append(f'- {m["name"]} 실전 기록 {live["months"]}개월: 월평균 {pct(live["mean"])}, 동일가중 대비 {pp(live["mean_excess_equal_weight"])}')
    if not any_line:
        lines.append('- 이전 추천 기록이 없다. `--journal`로 일지를 지정하면 이번 추천을 저장하고 다음 실행부터 실제 결과를 채점한다.')
    lines.append('')
    return lines


def _near_misses(result):
    lines = ['## 점수는 높았지만 빠진 종목', '']
    reason = dict(excluded_trend='10개월 평균선 아래', excluded_sector_cap='같은 섹터 2종목 한도')
    for mk, m in result['markets'].items():
        ranking = m.get('ranking', [])
        worst = max((r['rank'] for r in ranking if r['status'] == 'selected'), default=0)
        misses = [r for r in ranking if r['rank'] < worst and r['status'] in reason]
        if misses:
            lines.append(f'- {m["name"]}: ' + '; '.join(f'{m["names"][r["code"]]}({r["rank"]}위, {reason[r["status"]]})' for r in misses))
    if len(lines) == 2:
        lines.append('- 없음')
    lines.append('')
    return lines


def _watch(result):
    if not result.get('watch'):
        return []
    lines = ['## 보유·관심 종목 점검', '',
             '| 종목 | 이번 달 순위 | 종합점수 | 최근 1년 수익률 (직전 1개월 제외) | 연 변동성 | 10개월 평균선 대비 | PER | 이 규칙에서의 상태 |',
             '|---|---|---|---|---|---|---|---|']
    status = dict(selected='선정', excluded_trend='제외: 10개월 평균선 아래', excluded_sector_cap='제외: 섹터 2종목 한도',
                  below_cutoff='5위 안에 들지 못함')
    for market, code in result['watch']:
        m = result['markets'].get(market)
        if m is None:
            continue
        r = _row_by_code(m).get(code)
        name = f'{m["names"][code]} ({code})'
        if r is None:
            lines.append(f'| {name} | 계산 불가 | | | | | | 최근 13개월 연속 가격 이력이 없음 |')
            continue
        state = status[r['status']]
        if r['status'] == 'below_cutoff' and not r['trend']:
            state += ' · 10개월 평균선 아래'
        lines.append(f'| {name} | {r["rank"]}/{m["eligible"]} | {_q(r["score"], 3)} | {pct(r["momentum"])} | '
                     f'{pct(r["volatility"] * Decimal(12).sqrt(), sign=False)} | {pct(r["trend_gap"])} | '
                     f'{mult(m["valuation"].get(code, {}).get("per"))} | {state} |')
    lines += ['', '10개월 평균선 아래는 이 규칙의 매도·제외 조건이다. 기업 실적이 좋아도 가격 추세가 꺾이면 규칙상 사지 않는다. '
              '보유 중인 종목을 팔지는 세금·보유 목적·다른 자산을 함께 보고 따로 판단한다.', '']
    return lines


def _limits(result):
    gaps = result['gaps']
    missing = sorted({g['code'] for g in gaps if g['role'] == 'chart'})
    lines = ['## 자료와 한계', '',
             f'- 자료: 네이버 증권 공개 월봉·시세 JSON {result["available"]}/{result["requests"]}건 확보(HTTP 요청 {result["http_requests"]}회, robots.txt 확인). 제공자 표시값이며 거래소 원장 대조는 하지 않았다.']
    if missing:
        lines.append(f'- 가격 이력을 받지 못한 종목: {", ".join(missing)}. 상장폐지·비상장 전환이면 과거 손실이 검증에서 빠진다.')
    issues = result.get('data_issues', [])
    if issues:
        names = {}
        for i in issues:
            m = result['markets'].get(i['market'])
            label = (m['names'].get(i['code'], i['code']) if m else i['code'])
            names.setdefault(label, []).append(i['issue'].split(':')[0])
        lines.append(f'- 월봉 품질 격리 {len(issues)}건: ' + '; '.join(f'{k} {", ".join(v)}' for k, v in sorted(names.items()))
                     + '. 시가 0·같은 달 서로 다른 월봉은 그 달만 제외하고 0이나 이웃 값으로 채우지 않았다.')
    other = [g for g in gaps if g['role'] != 'chart']
    if other:
        lines.append(f'- 보조 자료 공백 {len(other)}건(시세·밸류에이션·환율). 해당 값은 "확인 불가"로 두고 다른 값으로 채우지 않았다.')
    for mk, m in result['markets'].items():
        lines.append(f'- {m["name"]}: 후보 {m["universe_size"]}개 중 이력 확보 {m["with_history"]}개, 신호월 {m["last_complete_month"]}. {m["cost_note"]}')
    lines += ['- **생존 편향:** 후보군을 2026년에 정했다. 그동안 크게 망해 사라진 종목은 빠져 있어 과거 수익이 실제보다 좋게 보일 수 있다. 그래서 같은 후보군 동일가중과 비교하고, 최고 등급(A)은 주지 않는다.',
              '- **가격 수익률:** 분할만 조정한 가격이며 배당은 빠져 있다(배당이 큰 종목에 불리). 세금(배당소득세·해외주식 양도세)과 환전 비용은 반영하지 않았다.',
              '- **모델 선택:** 모멘텀·저변동성은 공개된 연구에서 알려진 요인이다. 이 데이터에서 여러 조합을 시험해 고른 것은 아니지만, 알려진 요인을 고른 것 자체가 사전 지식이다.',
              '- 이 보고서는 규칙 기반 계산 결과이며 주문을 내지 않는다. 개인 재무 상황은 반영하지 않았다.', '']
    return lines


def render(result):
    signal = ', '.join(f'{m["name"]} {m["last_complete_month"]} 월말 종가' for m in result['markets'].values())
    lines = ['# 종목 추천 리포트', '',
             f'기준 시각: {_local(result["as_of"])} (한국시간) · 신호: {signal} · 예시 예산: {krw(Decimal(result["budget_krw"]))}', '',
             f'규칙: **최근 1년 상승 강도(직전 1개월 제외) 2/3 + 가격 흔들림이 작은 정도 1/3**로 점수를 매기고, 10개월 평균선 위에 있는 종목만, '
             f'섹터당 최대 2개로 시장별 상위 5종목을 고른다. 규칙은 `{model.VERSION}`로 고정돼 있고 과거 성과에 맞춰 바꾸지 않았다.', '']
    lines += _headline(result)
    lines += _pick_table(result)
    lines += _explain(result)
    lines += _validation(result)
    lines += _sizing(result)
    lines += _history(result)
    lines += _watch(result)
    lines += _near_misses(result)
    lines += _limits(result)
    lines += ['## 다시 보기', '', '- 인터넷 없이 같은 결과 재현: `python -m investment_research picks replay <이 실행 디렉터리>`',
              '- 다음 달 말 이후 새로 실행하면 이번 추천의 실제 성과를 채점하고 종목을 교체한다: `python -m investment_research picks run --journal reports/investment_journal`', '']
    return '\n'.join(lines)
