"""Short Korean scan body; detailed, pinned evidence stays in the appendix."""
from decimal import Decimal
from zoneinfo import ZoneInfo
from .scan import assess, eligible
from .research_catalog import RATES


def sections(run):
    from .orchestrator_report import _text, _refs, _number, _unit
    legacy=run.input['scan']['method_version']=='evidence_shortlist_v1'
    a=assess(run);rows={r['asset_id']:r for r in a['universe']}
    minimum=a.get('minimum_evidence_version') is not None
    enhanced=run.input['scan']['method_version'] in ('evidence_shortlist_v4','evidence_shortlist_v5','evidence_shortlist_v6','evidence_shortlist_v7')
    facts=eligible(run.case,run.cutoff);metrics={m.id:m for m in run.result.metrics}
    quoted={f['id']:f for f in run.deep.facts if f['status']=='available'} if run.deep else {}
    def observation(asset,measure):
        es=[e for e in facts if asset in e.asset_ids and e.provenance.definition['measure']==measure and e.value is not None]
        return max(es,key=lambda e:(e.period or '') if legacy else (str(e.observed_at or ''),e.period or '',e.id)) if es else None
    def show(e):
        if not e:return '현재 값 미확보'
        period=e.period if legacy else str(e.observed_at or e.period)
        return _number(e.value)+' '+_text(e.unit if legacy else _unit(e.unit))+' ('+_text(period)+') '+_refs([e.id])
    def source_refs(ids):return _refs(ids if legacy else ids[:3]) if ids else '핵심 자료 미확보'
    lines=['# 지금 전체 투자판에서 더 볼 만한 곳','', '**질문:** '+_text(run.input['question']),
        '', '정보 확인: '+run.cutoff.astimezone(ZoneInfo('Asia/Seoul')).isoformat()+' (한국시간).','']
    if run.input['synthetic']:lines.extend(['**합성 검증 자료다. 실제 투자 판단에 사용하지 않는다.**',''])
    lines.extend(['## 오늘의 결론',''])
    if a['candidates']:
        names=' · '.join(rows[i]['name'] for i in a['candidates'])
        lines.append('- 먼저 더 조사할 후보: **'+_text(names)+'**. 아래 번호는 조사 순서이며 투자 수익률 순위가 아니다.')
    else:lines.append('- 현재 확보된 근거에서는 우선 후보를 억지로 고르기 어렵다. 아래에 실제 확인한 부분과 부족한 부분을 나눴다.')
    lines.extend([
        '- 국채 이자는 위험자산 대신 얻을 수 있는 실제 대안이다. 주식의 예상 이익·배당률과 같은 수익으로 놓고 비교하면 안 된다.',
        '- 사업이 좋아지는 것과 현재 가격이 싼 것은 다르다. 실적 개선이 이미 가격에 반영됐는지 다음 조사에서 검증한다.',
        '- 가격 상승과 공개 토론은 참고 신호다. 이전 표본이 없으면 관심이 늘었다고 말하지 않고, 자료 부족을 투자 매력 부족으로 바꾸지 않는다.',
        '- '+a['personalization'],'','## 지금 볼 만한 후보',''])
    for asset in a['candidates']:
        r=rows[asset];lines.extend(['### '+str(r['reference_number'])+'. '+_text(r['name']),'',
            '**왜 지금:** '+_text(r['why_now']), '', '**핵심 근거:** '+source_refs(r['evidence_ids'])])
        if asset=='KR_GOVERNMENT_3Y':
            lines.append('한국 국고채 3년: '+show(observation(asset,'KR_GOVERNMENT_NOMINAL_3Y'))+
                '. 실제 채권을 만기까지 보유할 때의 수익은 매수가·이자·비용에 달려 있고, 중도 매도하면 손실이 날 수 있다.')
        elif asset=='US_EQUITY':
            f=quoted.get('F_SP_FORWARD_12M_PE');rev=quoted.get('F_Q3_EPS_REVISION');avg=quoted.get('F_SP_PE_AVG5')
            if f and rev:
                window=rev['window']
                if not legacy:
                    import re
                    dates=re.findall(r'\d{4}-\d{2}-\d{2}',window)
                    window=(' ~ '.join(dates[-2:])) if dates else '해당 분기의 전망 수정'
                lines.append('향후 열두 달 예상 이익 기준 주가 배수: '+_number(Decimal(f['value']))+'배 ('+f['observed_at']+
                    '); 분기 이익 전망 수정: '+_number(Decimal(rev['value']))+'% ('+window+').'+
                    (' 같은 정의의 오년 평균은 '+_number(Decimal(avg['value']))+'배다.' if avg else '')+
                    ' 예상 이익이 실현돼야 이 가격 비교가 의미 있다.')
        elif asset=='VALUE_DIVIDEND':
            for e in facts:
                if asset in e.asset_ids and e.id in r['evidence_ids']:
                    label=e.provenance.definition['scope'] if legacy else ('미국 가치주 예시의 예상 이익 배수' if e.provenance.definition['measure']=='SSGA_FY1_HARMONIC_PE' else '미국 배당 전략 예시의 과거 분배율')
                    lines.append(_text(label)+': '+show(e))
            if not legacy:
                e=observation('GROWTH_THEME','SSGA_FY1_HARMONIC_PE')
                if e:lines.append('같은 정의의 미국 성장주 예시 배수: '+show(e)+'. 낮은 배수만으로 투자 우위를 확정하지 않는다.')
            lines.append('분배율은 과거 지급액 기준이다. 국채처럼 미래 지급이나 원금을 보장하지 않는다.')
        elif asset=='BTC':lines.append('Bitcoin 가격: '+show(observation(asset,'COINBASE_BTC_USD_DAILY_CLOSE' if minimum else 'COINBASE_BTC_USD_LAST_TRADE')))
        if minimum:
            lines.extend(['', '**자료 충족:** '+r['coverage']['label']+'. 투자 매력 점수가 아니다.'])
            if r['coverage']['critical_gaps']:lines.append('**조건부 후보 — 핵심 자료 확인 필요.** 현재 가격에서 투자 우위는 판단하지 않는다.')
        lines.extend(['', '**가격·추세·관심:** '+_text(r['price_context'])+' '+_text(r['momentum'])+' '+_text(r['attention']),
            '', '**가장 큰 위험:** '+_text(r['risk']),
            '', '**핵심 미확인:** '+_text(' / '.join(r['unknowns'])),
            '', '**가설이 강해지는 조건:** '+_text(r['strengthen']),
            '', '**판단을 바꿀 조건:** '+_text(r['invalidate']),
            '', '**다음 행동:** '+_text(r['action'])+'. '+_text(r['confidence'])+'.',
            '', '**깊게 볼 가치:** '+_text(r['expectation_reality']),''])
        if not legacy and r['narrative_ids']:
            lines.extend(['관련 공개 토론: '+source_refs(r['narrative_ids'])+'. 발언의 존재만 확인했으며 같은 주장 반복을 독립 증거로 세지 않는다.',''])
    if len(a['candidates'])<2:lines.extend(['현재 근거로 두 개 이상 후보를 만들지 못했다. 후보 수를 채우려고 선정 기준을 낮추지 않았다.',''])
    lines.extend(['## 지금은 굳이 안 볼 영역','',
        '아래는 우선 조사에서 뒤로 둔 이유다. 자료가 없는 자산을 나쁜 투자라고 판정하지 않는다.',''])
    for r in a['universe']:
        if r['asset_id'] in a['candidates']:continue
        state={'weak_case':'현재 긍정 논거 약함','insufficient':'판단 자료 부족','conditional_watch':'조건부 관찰',
               'normal_alternative':'정상적인 대기 대안','neutral':'비교 기준'}[r['status']]
        lines.append('- **'+_text(r['name'])+' — '+state+':** '+_text(r['why_now'])+' '+source_refs(r['evidence_ids']))
    if minimum:
        lines.extend(['','## 각 영역을 얼마나 검토할 수 있었나','',
            '아래 상태는 자료 충족 여부다. 충분하다고 투자 매력이 높아지는 것은 아니며, 부족하다고 나쁜 투자라는 뜻도 아니다.','',
            '| 조사 영역 | 최소 자료 상태 | 남은 핵심/보조 자료 |','| --- | --- | --- |'])
        for r in a['universe']:
            missing=[s['label'] for s in r['coverage']['slots'] if s['status']=='missing']
            lines.append('| '+_text(r['name'])+' | '+r['coverage']['label']+' | '+_text(' · '.join(missing) or 'Scan 기준 충족; 실제 상품·개인 조건은 별도')+' |')
        if enhanced:lines.extend(minimum_observations(a))
        if run.input['scan']['method_version']=='evidence_shortlist_v7':lines.extend(four_asset_observations(run,a))
        lines.extend(['','## 지난 Scan 이후 달라진 점',''])
        h=a['since_previous_scan']
        if h['status']=='baseline':lines.append('- **Baseline:** 비교할 이전 Scan을 지정하지 않았다. 이번 관측을 기준으로 남기며 시장/관심이 좋아졌다고 주장하지 않는다.')
        else:
            lines.append('- 비교 기준: '+h['previous_as_of']+'의 보존된 Scan. 현재 원문은 새로 확인했다.')
            changed=[c for c in h['observations'] if c['status']=='new_observation' and c['direction']!='flat']
            if not changed:lines.append('- **새롭게 좋아진/나빠진 신호:** 비교 가능한 현재 시장 관측에서 새 방향 변화를 확인하지 못했다. 같은 관측 재확인과 새 데이터 연결을 시장 변화로 표현하지 않는다.')
            for c in changed[:6]:
                lines.append('- '+_text(rows[c['asset_id']]['name'])+' / '+_text(c['measure'])+': '+c['previous_value']+' → '+c['current_value']+' '+_text(c['unit'])+
                    ' ('+c['previous_observed_at'][:10]+' → '+c['current_observed_at'][:10]+'). 상승/하락 자체가 투자 매력의 개선/악화는 아니다. '+_refs([c['current_evidence_id']]))
            for kind,label in [('added','새 후보'),('removed','빠진 후보'),('priority_raised','조사 우선순위 상승'),('priority_lowered','조사 우선순위 하락')]:
                events=[e for e in h['candidate_changes'] if e['change']==kind]
                lines.append('- **'+label+':** '+('없음.' if not events else ' / '.join(_text(rows[e['asset_id']]['name'])+' — '+_text(e['reason']) for e in events)))
            same=[rows[e['asset_id']]['name'] for e in h['candidate_changes'] if e['change']=='unchanged_candidate' or enhanced and e['change'] in ('priority_raised','priority_lowered') and not e['new_evidence_ids']]
            lines.append('- **판단이 그대로인 후보:** '+_text(' · '.join(same) or '없음')+'.')
            if h.get('excluded_previous_observation_dates'):
                lines.append('- **과거 관측일 오류:** 이전 값의 날짜가 원문 기간과 맞지 않거나 확인되지 않은 항목은 변화 계산에서 제외했다. 날짜 처리 수정이 시장 악화·자료 후퇴를 의미하지 않는다. 과거 보고서는 그대로 보존했다.')
            if h['newly_observable']:lines.append('- 새로 확인 가능한 가격·거래·전세·금리 자료는 coverage 개선이다. 과거 같은 자료가 없던 자산의 시장 매력이 좋아졌다는 증거로 쓰지 않았다.')
            if run.input['scan']['method_version'] in ('evidence_shortlist_v5','evidence_shortlist_v6','evidence_shortlist_v7'):
                for n in h['newly_observable']:
                    if '완료 판본' in n['reason']:lines.append('- **판본 확정:** '+_text(n['reason'])+' '+_refs([n['current_evidence_id']]))
            if any(c['status']=='revised_vintage' for c in h['observations']):lines.append('- 같은 관측일 값의 개정이 있다. 이전 Scan 이후 시장 상승/하락과 구분하며 상세 변경 기록에 남겼다.')
            if h['mismatches']:lines.append('- 정의/출처가 달라 시계열 연결을 보류한 항목은 상세 변경 기록에 남겼다.')
        lines.extend(['- **Community:** '+_text(h['community']['reason'])+' 절대 표본 수를 관심 증가율로 바꾸지 않았다.',
            '- 현재 값·과거 값·계산식·원문 hash·후보 변경 이유는 [관측 기록](scan_observations.json)과 [변경 기록](scan_changes.json)에 연결된다.',''])
    lines.extend(['','## 시장 전체에서 중요한 변화',''])
    for asset,measure,label in [('KR_GOVERNMENT_3Y','KR_GOVERNMENT_NOMINAL_3Y','원화 이자 대안'),
                                 ('SHORT_BOND',RATES[0],'미국 국채 이년'),('LONG_BOND',RATES[1],'미국 국채 십년')]:
        e=observation(asset,measure)
        if e:lines.append('- '+label+': '+show(e)+'. 금리가 올라가면 새로 살 때 이자는 좋아지지만 이미 가진 채권 가격은 떨어질 수 있다.')
    if run.macro:
        for m in run.macro.metrics:
            if 'yoy' in m.method and m.id in metrics:
                lines.append('- 미국 소비자물가의 전년 대비 변화: '+_number(m.value)+' '+_text(m.unit)+' '+_refs([m.id])+'. 생활비와 금리 부담을 판단하는 맥락이며 한국 물가로 대신 쓰지 않는다.')
    if 'NATGAS' in rows and rows['NATGAS']['status']=='weak_case':
        lines.append('- 천연가스: 공식 재고·생산 전망은 단순 부족 주장에 반대 근거를 준다. 전망이 실제 재고로 이어지는지 확인한다. '+source_refs(rows['NATGAS']['evidence_ids']))
    if 'ENERGY' in rows and rows['ENERGY']['status']=='conditional_watch':
        lines.append('- 원유: 공급 차질은 관측됐지만 향후 회복은 전망이다. 복구가 늦어지는지 실제 자료로 볼 필요가 있다. '+source_refs(rows['ENERGY']['evidence_ids']))
    if 'BTC' in rows:
        r=rows['BTC'];lines.append('- Bitcoin: '+_text(r['why_now'])+' '+source_refs(r['evidence_ids']))
        if 'momentum_metric_id' in r:
            m=metrics[r['momentum_metric_id']]
            lines.append('  같은 거래소의 완료 일봉 종가 변화: '+_number(m.value)+'% '+_refs([m.id])+'. 한 날 상승/하락은 장기 추세나 투자 매력을 증명하지 않는다.')
    lines.extend(['- 성장·물가·정책·전체 유동성 중 미확보한 항목은 추정하지 않았다. 테마·가치/배당 전략은 주식과 겹치는 노출이다.','',
        '## 다음에 물어볼 만한 것',''])
    followups={'KR_GOVERNMENT_3Y':'한국 3년 국채랑 S&P500 중 신규자금 어디가 더 합리적이야?',
               'US_EQUITY':'S&P500 예상 이익이 실제로 나올 수 있는지 자세히 봐.',
               'KR_EQUITY':'삼성전자랑 SK하이닉스 현재 가격 기준으로 비교해줘.',
               'VALUE_DIVIDEND':'성장주랑 가치주·배당투자 비교해줘.', 'BTC':'BTC 자세히 봐.'}
    for asset in a['candidates']:lines.append('- “'+followups.get(asset,rows[asset]['name']+' 자세히 봐.')+'”')
    lines.extend(['- “천연가스 더 파봐.” 또는 “서울 아파트 자세히 봐.”처럼 특정 대상을 바로 물어도 된다.',
        '', '후보 선정 이유·전체 조사 범위·미확인 조건은 [shortlist.json](shortlist.json), 원문과 계산은 아래 상세 근거에서 확인할 수 있다.',''])
    if not legacy:lines.extend(['“1위랑 2위 비교해줘.”처럼 번호로 묻는 CLI 실행에는 `--context-run`으로 이 보고서의 실행 디렉터리를 지정한다. 저장된 후보만 참조하고 자료는 새로 확인한다.',''])
    return lines


def minimum_observations(assessment):
    """Latest inputs and meaningful intervals, without imposing equal metrics."""
    from .orchestrator_report import _number,_refs,_text
    points=assessment['observations'];changes=assessment['within_scan_changes']
    def point(asset,measure):
        ps=[p for p in points if p['asset_id']==asset and p['definition']['measure']==measure]
        from .sources import _time
        return max(ps,key=lambda p:_time(p['observed_at'])) if ps else None
    def value(p,unit):
        return _number(Decimal(p['value']))+' '+unit+' ('+p['observed_at'][:10]+') '+_refs([p['evidence_id']]) if p else '미확보'
    def movement(asset,measure,scope=None):
        c=next((c for c in changes if c['asset_id']==asset and c['measure']==measure and (scope is None or c['scope'].startswith(scope+' apartments;'))),None)
        if c is None:return '비교 가능한 기간 변화 미확보'
        return c['previous_observed_at'][:10]+' → '+c['current_observed_at'][:10]+': '+_number(Decimal(c['percent_change']))+'%' if c['percent_change'] is not None else '기준값이 양수가 아니어서 변화율 계산 보류'
    out=['','### 새로 확인한 최소 관측','']
    cash=point('CASH','KR_CD_91D')
    if cash:out.append('- **원화 현금 금리 기준:** '+value(cash,'%')+'. CD 91일 시장금리이며 개인 예금/MMF 계약금리·세후 수익·보호를 보장하지 않는다.')
    for asset,label in [('BTC','Bitcoin'),('ETH','Ethereum')]:
        p=point(asset,'COINBASE_'+asset+'_USD_DAILY_CLOSE')
        if p:out.append('- **'+label+':** '+value(p,'달러/'+asset)+'. 일곱 날 완료 종가 변화 '+movement(asset,'COINBASE_'+asset+'_USD_DAILY_CLOSE')+'. 한 거래소 가격·하루 거래량이며 확정 기관 흐름·전 시장 레버리지는 제한된다.')
        if assessment['method_version'] in ('evidence_shortlist_v5','evidence_shortlist_v6','evidence_shortlist_v7'):
            f=point(asset,'US_SPOT_'+asset+'_ETF_DAILY_NET_FLOW')
            if f:out.append('  최신 완료 미국 현물 ETF 하루 순유입: '+value(f,'백만 달러')+'. 제공자 집계이며 원발행사 독립 대조는 미완료다. 일곱 날 가격과 다른 기간이므로 동시 변화나 전체 기관 수요의 추세로 일반화하지 않는다.')
            else:out.append('  해당 자산의 최신 완료 ETF 흐름은 미확보다. 미완성 합계·다른 crypto 흐름·영으로 채우지 않는다.')
    gold=point('GOLD','LBMA_GOLD_PM_ISSUER_REPORTED');ret=point('GOLD','LBMA_GOLD_PM_ISSUER_MONTH_RETURN');real=point('GOLD','US_TIPS_10Y_CURRENT')
    if gold:out.append('- **금:** '+value(gold,'달러/트로이온스(금 무게 기준)')+'. 월말 기준가격 변화 '+value(ret,'%')+'; 십년 실질 국채금리 '+value(real,'%')+'. '+
        ('직접 수요 수준은 아래 실물 보유량에서 별도로 확인하고 서로 다른 기간을 동시 변화로 묶지 않는다.' if assessment['method_version']=='evidence_shortlist_v7' else '서로 다른 기간을 하나의 동시 변화로 묶지 않고 직접 수요는 미확보로 남긴다.'))
    for asset,label,price_measure,stock_measure,price_unit,stock_unit in [
        ('ENERGY','원유','EIA_WTI_SPOT','EIA_US_COMMERCIAL_CRUDE_STOCK','달러/배럴','천 배럴'),
        ('NATGAS','천연가스','EIA_HENRY_HUB_SPOT','EIA_US_WORKING_GAS_STOCK','달러/MMBtu(열량 단위)','Bcf(십억 입방피트)')]:
        p=point(asset,price_measure);s=point(asset,stock_measure)
        if p or s:out.append('- **'+label+':** '+value(p,price_unit)+'; 실제 미국 재고 '+value(s,stock_unit)+'. 현물가격 흐름 '+movement(asset,price_measure)+'. 재고 증가를 계절성 없는 잉여로, 현물 변화를 선물 ETF/ETN 수익으로 바꾸지 않는다.')
    out.extend(['','서울·경기·인천 월별 관측은 각 지역의 같은 정의·같은 기간으로 비교했다. 조사 가격지수는 개별 아파트 거래가격이 아니다.','',
        '| 지역 | 매매지수 변화 | 거래호수 변화 | 전세지수 변화 |','| --- | --- | --- | --- |'])
    for region in ('서울','경기','인천'):
        out.append('| '+region+' | '+movement('KR_APARTMENTS_SEOUL_GYEONGGI_INCHEON','KR_APARTMENT_SURVEY_SALE_INDEX',region)+
            ' | '+movement('KR_APARTMENTS_SEOUL_GYEONGGI_INCHEON','KR_APARTMENT_REPORTED_SALE_COUNT',region)+
            ' | '+movement('KR_APARTMENTS_SEOUL_GYEONGGI_INCHEON','KR_APARTMENT_SURVEY_JEONSE_INDEX',region)+' |')
    p=point('KR_APARTMENTS_SEOUL_GYEONGGI_INCHEON','KR_HOUSEHOLD_NEW_LOAN_RATE')
    if p:out.append('\n국내 신규 가계대출 평균금리: '+value(p,'%')+'. 관측일은 해당 월의 표기 기준이다. 지역별·개인 주담대 실행금리와 한도는 별도 확인한다.')
    out.append('')
    return out


def four_asset_observations(run,assessment):
    """Current verified fields, calculations and meaningful missing conditions."""
    from .orchestrator_report import _number,_refs,_text
    from .sources import _time
    facts=eligible(run.case,run.cutoff);metrics={m.id:m for m in run.result.metrics}
    def field(measure):
        rows=[p for p in assessment['observations'] if p['definition']['measure']==measure]
        if not rows:return '미확보'
        p=max(rows,key=lambda p:_time(p['observed_at']))
        return _number(Decimal(p['value']))+' '+_text(p['definition']['unit'])+' ('+p['definition']['period']+') '+_refs([p['evidence_id']])
    def metric(identifier):
        m=metrics.get(identifier)
        return _number(m.value)+' '+_text(m.unit)+' '+_refs([m.id]) if m else '같은 정의 비교 미확보'
    out=['','### 네 영역의 실제 근거와 판단 제한','', '**천연가스 — 현물·수급·투자상품을 나누어 본다.**','']
    for measure,label in [('EIA_US_DRY_GAS_PRODUCTION','미국 전체 실제 월간 dry gas 생산'),('EIA_US_LNG_EXPORTS','미국 실제 월간 LNG 수출')]:
        out.append('- '+label+': '+field(measure)+'. 일평균 비교는 아래에서 월 일수로 나누며 현재 주간 생산/당일 feedgas가 아니다.')
    for prefix,label in [('PRODUCTION','생산'),('LNG_EXPORTS','LNG 수출')]:
        out.append('- 일수 보정한 '+label+' 일평균 전월 대비: '+metric('SCAN_GAS_'+prefix+'_DAILY_MOM')+
            '; 전년 같은 월 대비: '+metric('SCAN_GAS_'+prefix+'_DAILY_YOY')+'. 달 길이 차이를 성장으로 세지 않았다.')
    out.append('- 자체 계절 기준: '+metric('SCAN_GAS_SEASONAL_5Y_REFERENCE')+'; 현재 재고의 기준 대비 차이 '+metric('SCAN_GAS_STOCK_VS_SEASONAL_REFERENCE')+
        '. 같은 ISO 주 금요일의 과거 오년 실제 재고 평균이며 **EIA 공식 보간 평균이 아니다**. 전년 기준 값은 원문 참조에 남겼고 평년 주입 속도는 미확보다.')
    names={'NEW YORK':'뉴욕','OHIO':'오하이오','N TEXAS':'텍사스 북부'};temps={'A':'평년보다 높음','N':'평년 근처','B':'평년보다 낮음'}
    for measure,label in [('NOAA_CPC_6_10_TEMPERATURE_OUTLOOK','6~10일'),('NOAA_CPC_8_14_TEMPERATURE_OUTLOOK','8~14일')]:
        es=[e for e in facts if e.provenance.definition['measure']==measure]
        if es:
            descriptions=[names[e.provenance.definition['scope'].split(' state')[0]]+' '+temps[e.provenance.definition['adjustment'].split('_')[2]] for e in es]
            period=es[0].provenance.definition['period'].replace('forecast_valid_','').replace('_to_',' ~ ')
            out.append('- NOAA '+label+' 기온 전망 ('+period+'; 발행 '+str(es[0].observed_at)+'): '+', '.join(descriptions)+'. '+_refs([e.id for e in es]))
        else:out.append('- NOAA '+label+' 최신 전망 미확보.')
    out.extend(['- 기온 전망은 실제 수요가 아니다. HDD/CDD는 난방/냉방이 필요한 기온 차이를 쌓은 수요 지표이며 이번 자료에는 없다. 따뜻한 날씨는 난방을 줄이고 냉방을 늘릴 수 있어 총수요는 별도로 확인한다.',
        '- 가격 상승·재고의 계절 기준·일수 보정 생산/수출·기온 전망을 함께 본다. 기간이 다르고 선물곡선이 없어 겨울이라는 이유로 후보를 올리지 않았다.',
        '- 여러 만기 선물가격·UNG/BOIL 원상품 구조·CFTC 포지션의 현재 검증된 입력은 미확보다. 먼 계약이 더 비싸면 갈아탈 때 비용이 생길 수 있고, 가까운 계약이 더 비싸면 현재 공급 긴장일 수 있다. 현재 contango/backwardation을 추정하지 않는다. 레버리지 상품의 일별 재설정과 선물 교체 때문에 현물 상승률을 상품 수익률로 바꾸지 않는다.',
        '', '**금 — 가격과 직접 수요 수준을 구분한다.**','',
        '- IAU 실물 금 보유량: '+field('IAU_GOLD_PHYSICAL_HELD')+'. 가격에 따라 달라지는 AUM이 아니다. 한 상품의 수준만 확인했으므로 보유량 증가/ETF 순유입/중앙은행 매수라고 표현하지 않는다.',
        '- 월말 금 가격 흐름·실질금리와 관측 기간이 다르다. 달러 환경·중앙은행/실물 수요의 같은 기간 변화가 없으면 강한 수요 확인은 보류한다.',
        '', '**Ethereum — BTC와 분리한 기관 집계다.**','',
        '- 최신 미국 현물 ETH ETF 하루 제공자 보고값: '+field('US_SPOT_ETH_ETF_DAILY_NET_FLOW')+'. 최근 오 보고 거래일 합계: '+metric('SCAN_ETH_FIVE_REPORTED_DAYS_NET_FLOW')+'. 기간과 각 일별 원문은 계산 참조에서 확인한다.',
        '- 이는 **Farside 자동 집계 전사**다. 표는 오류 가능성을 고지하며 최신 하루 값의 크기와 정확성을 발행사 원자료로 독립 확인하지 못했다. 산술 일치만으로 실제 기관 수요의 강도를 확정하지 않는다. 일곱 날 ETH 가격과 조사 기간이 달라 동시 괴리나 장기 수요 추세로 묶지 않는다.',
        '- 한 거래소 거래량은 유지했다. 네트워크 사용·수수료·staking·issuance/burn·전체 레버리지는 미확보이며 기관 집계로 대신하지 않는다.',
        '', '**광범위 원자재 — 원유만으로 전체를 설명하지 않는다.**','',
        '- 대표 상품 GSG NAV: '+field('ISHARES_GSG_NAV')+'; 별도 기준일 연초 이후 NAV 총수익: '+field('ISHARES_GSG_YTD_NAV_TOTAL_RETURN')+'. 펀드 NAV와 비용을 반영한 총수익이며 현물 지수 level/가격 변화와 구분한다.',
        '- 발행사는 S&P GSCI 기반 에너지·금속·농산물·축산 노출을 설명한다. 현재 에너지/산업금속/귀금속/농산물 비중은 미확보라 어떤 그룹이 상품 변화를 주도했는지 결론내리지 않는다.',
        '- 에너지: 미국 원유 실제 재고 '+field('EIA_US_COMMERCIAL_CRUDE_STOCK')+'. 귀금속: 위 IAU 실물 보유량의 수요 수준. 산업금속/농산물: 현재 수급 미확보. 원유와 금의 별도 기간 자료를 전체 원자재 동반 강세나 물가 방어의 증거로 합치지 않는다.',
        '- 선물 기반 상품에는 계약 교체 비용/이익, 담보 이자, 수수료, 추적 차이가 있다. 다른 자산과 분산될 가능성과 실제 위기 시 분산 효과·미래 수익은 별도로 확인해야 한다.',
        '', '이번 연결로 평가할 자료는 늘었지만 투자 매력이 자동으로 높아진 것은 아니다. 새 자료는 이전 시장 변화와 구분해 기록했다.',''])
    if run.input.get('commodity_coverage'):
        curve=[e for e in facts if e.provenance.definition['measure']=='CME_NG_SETTLEMENT']
        if curve:
            curve.sort(key=lambda e:e.provenance.definition['scope'])
            out=[line for line in out if not line.startswith(('- 가격 상승·재고의 계절 기준','- 여러 만기 선물가격'))]
            out.insert(out.index('**금 — 가격과 직접 수요 수준을 구분한다.**'),
                '- 천연가스 실제 만기별 선물 ('+curve[0].period+'): '+', '.join(e.provenance.definition['scope'].split()[-1]+' '+str(e.value)+' USD/MMBtu' for e in curve)+
                '. 잠정 정산 여부는 원문 정의에 보존했다. 월별 가격차는 실현 교체 손익이 아니며 겨울만으로 후보를 올리지 않는다. '+_refs([e.id for e in curve]))
            out.insert(out.index('**금 — 가격과 직접 수요 수준을 구분한다.**'),
                '- UNG/BOIL 실제 상품 조건·HDD/CDD·CFTC 포지션은 이 최소 Scan에서 모두 조사하지 않았다. 독립 Deep Dive 결과와 Scan의 조사 범위를 구분한다.')
        wgc=[e for e in facts if e.provenance.definition['measure']=='WGC_GLOBAL_GOLD_ETF_NET_FLOW']
        if wgc:
            at=wgc[-1].period
            out.insert(out.index('**Ethereum — BTC와 분리한 기관 집계다.**'),
                '- 전체 실물담보 금 ETF '+at+' 순유입 '+field('WGC_GLOBAL_GOLD_ETF_NET_FLOW')+'; 실물량 변화 '+field('WGC_GLOBAL_GOLD_ETF_HOLDINGS_CHANGE')+
                '. 한 IAU의 보유 증가나 10월 현재 유입과 다르다. Q2 중앙은행 추정도 같은 시점의 확정 매수로 사용하지 않는다.')
        leading=[e for e in facts if e.provenance.definition['measure'].startswith('GSCI_WEIGHT_')]
        if leading:
            out.append('- 추가 구성 단서 ('+leading[0].period+'): '+', '.join(e.provenance.definition['scope'].split()[-1]+' '+str(e.value)+'%' for e in leading)+
                '. 현재 전체 구성비·올해 기여도는 아니다. 완전한 구성 합계는 독립 원자재 Deep Dive의 같은 날짜 문서에서 확인한다. '+_refs([e.id for e in leading]))
    return out
