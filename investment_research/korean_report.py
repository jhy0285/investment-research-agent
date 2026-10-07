"""Decision-relevant reading of the connected Korean evidence, without ranking."""
from decimal import Decimal

from .korean_data import KR_RATES, REGIONS, regions_for_method
from .macro_report import _number


def korean_report(run):
    if not run.input.get('korean_coverage'): return []
    from .orchestrator_report import _current, _refs, _unit
    evidence=[e for e in run.case.evidence if e.provenance and _current(run,e)]
    metrics=[m for m in run.result.metrics if m.id.startswith('CALC_KR_')]
    methods={m['id']:m for m in run.input['methods']}
    lines=['## 한국 원자료가 이번 판단에 주는 의미','']
    if any(identifier.startswith('KR_GOVERNMENT_') for identifier in methods):
        lines.extend(['### 원화 국고채와 미국 주식의 기회비용','',
            '| 한국 국고채 만기 | 마지막 확보 수익률 (연율) | 관측일 | 근거 |', '| --- | --- | --- | --- |'])
        current=[]
        for s in run.macro.snapshot.selections if run.macro else ():
            if s.definition.canonical_id not in KR_RATES: continue
            if s.status=='available' and s.latest is not None and s.latest.value is not None:
                current.append(s)
                lines.append('| '+str(s.definition.tenor_years)+'년 | '+_number(s.latest.value)+'% | '+s.latest.observation_date.isoformat()+' | '+_refs([s.latest.id])+' |')
            else: lines.append('| '+str(s.definition.tenor_years)+'년 | 미확보 | 확인 불가 | 현재 수익률로 사용하지 않음 |')
        lines.extend(['','이는 한국은행의 **원화 국고채 시장 기준금리**다. 개별 채권의 쿠폰이나 지금 매수 가능한 채권의 만기수익률(YTM), 국채 ETF의 확정 수익률과는 다르다.'])
        if current:
            requested=[m for m in methods.values() if m['id'].startswith('KR_GOVERNMENT_')]
            for m in requested:
                tenor=int(m['id'].rsplit('_',1)[1][:-1]);selected=next((s for s in current if s.definition.tenor_years==tenor),None)
                if selected:
                    lines.append('질문에 명시한 '+m['label']+'의 기준 수익률 '+_number(selected.latest.value)+'%를 이제 실제 대안의 출발점으로 확인할 수 있다. ('+_refs([selected.latest.id])+')')
        lines.extend(['',
            '원화 지출에 사용할 신규자금이라면 원화 이자와 만기의 예측 가능성이 중요한 비교 조건이다. S&P 500은 기업 이익 성장에 참여하지만 가격 하락과 USD/KRW 변동을 함께 감수한다. 장기 이익 성장이 실현되면 주식의 경제성이 더 좋아질 수 있다.',
            '국고채 금리와 미국 주식의 이익수익률은 통화·현금 지급 방식·시점·위험이 다르므로 빼서 투자 우열이나 확정 주식 위험보상을 만들지 않았다. 투자기간·자금 사용일·실제 상품과 비용·현재 보유가 미확인이어서 어느 쪽에 신규자금을 넣을지 확정하지 않는다.',
            '판단을 바꿀 자료: 실제 매수 채권의 가격/만기수익률과 자금 사용일, 미국 기업의 예상 이익 실현·valuation, 환헤지 여부와 비용.',''])
    if set(methods)&{'SAMSUNG','SK_HYNIX'} and not run.input.get('semiconductor_coverage'):
        lines.extend(['### 실적이 좋은 기업과 매수 가격이 좋은 주식은 별개다','',
            '| 기업·항목 | 확보한 값 | 보고기간 | 자료 성격 | 근거 |','| --- | --- | --- | --- | --- |'])
        for e in evidence:
            d=e.provenance.definition;measure=d['measure']
            for identifier,name in [('SAMSUNG','삼성전자'),('SK_HYNIX','SK하이닉스')]:
                if identifier not in methods or measure not in (identifier+'_REVENUE',identifier+'_OPERATING_PROFIT',identifier+'_NET_PROFIT'):continue
                if e.value is None: continue
                item={'REVENUE':'매출','OPERATING_PROFIT':'영업이익','NET_PROFIT':'순이익'}[measure.removeprefix(identifier+'_')]
                basis='공식 연결 분기 발표문' if identifier=='SAMSUNG' else '공식 IR 연결 제공자; 원공시 교차 확인 미완료'
                lines.append('| '+name+' '+item+' | '+_number(e.value)+' '+_unit(e.unit)+' | '+d['period']+' | '+basis+' | '+_refs([e.id])+' |')
        lines.extend(['','같은 기업·기간·단위·자료 정의 안에서 계산한 결과:',''])
        company_metrics=[m for m in metrics if m.method in ('reported_operating_margin_v1','same_company_quarterly_change_v1')]
        if company_metrics:
            for m in company_metrics: lines.append('- '+m.label+': '+_number(m.value)+'%. ('+_refs([m.id])+')')
        else: lines.append('- 같은 정의의 입력이 부족하여 계산을 보류했다.')
        sam=[e for e in evidence if e.provenance.definition['measure']=='SAMSUNG_GUIDANCE']
        mx=[e for e in evidence if e.provenance.definition['measure']=='SAMSUNG_MX']
        if sam:
            lines.append('- 삼성전자는 AI 인프라 투자와 서버 수요에 대한 하반기 기대를 설명한다. 이는 경영진 전망이며 실제 미래 매출의 확인은 아니다. ('+_refs([e.id for e in sam])+')')
        if mx:
            lines.append('- 삼성전자 발표문은 MX/네트워크의 영업손실도 명시한다. 반도체 호황을 전체 사업부의 동일한 수익성으로 일반화할 수 없다. ('+_refs([e.id for e in mx])+')')
        hynix=[e for e in evidence if e.provenance.definition['measure']=='SK_HYNIX_NET_PROFIT']
        for net in hynix:
            profits=[e for e in evidence if e.provenance.definition['measure']=='SK_HYNIX_OPERATING_PROFIT'
                and e.provenance.definition['period']==net.provenance.definition['period']]
            if profits and net.value is not None and net.value>profits[0].value:
                lines.append('- SK하이닉스 제공자 표에서는 '+net.provenance.definition['period']+' 순이익이 영업이익보다 크다. 영업외 손익·세금·회계 정의의 원공시 확인 없이 이를 본업 경쟁력이나 반복 가능한 이익의 우위로 해석하지 않는다. ('+_refs([net.id,profits[0].id])+')')
        lines.extend(['',
            '확보한 분기 실적은 사업 변화의 근거가 되지만 **현재 주가와 같은 정의의 연간/TTM 이익이 없어 어느 주식의 가격이 더 합리적인지는 판단할 수 없다**. 분기 EPS를 네 배로 곱해 PER을 만들거나 제공자 자료의 순이익을 원공시 값으로 확정하지 않았다.',
            '강세 논리: 메모리·AI 수요가 실제 매출과 이익으로 이어지는지 조사할 자료가 생겼다. 반대 논리: 업황과 큰 이익 기대가 가격에 이미 반영되었거나, 가격·수요 정상화 및 투자 지출이 미래 이익을 낮출 수 있다.',
            '판단을 바꿀 자료: 양 기업의 동일 기준 공시·현금흐름, 현재 주가/주식 수, 같은 기간 EPS와 valuation, SK하이닉스 공식 경영진 설명과 이익 조정 항목. 컨센서스와 earnings revision은 이번 연결 자료에 없다.',''])
    regional=[m for m in methods if regions_for_method(m)]
    if regional:
        names=tuple(dict.fromkeys(r for m in regional for r in regions_for_method(m)))
        lines.extend(['### 지역 가격 변화와 실제 투자 경제성을 구분한다','',
            '조사 지역: '+' / '.join(names)+'. 전국 집계는 이 지역의 숫자로 사용하지 않았다. 수도권은 서울·경기·인천을 각각 보여준다.',
            '', '| 지역·항목 | 마지막 확보월 | 전월 대비 변화 | 근거 |','| --- | --- | --- | --- |'])
        for m in metrics:
            if m.method=='same_region_monthly_change_v1':
                row=next(e for e in evidence if e.id==m.input_ids[0]);d=row.provenance.definition
                lines.append('| '+d['scope']+' | '+d['period']+' | '+_number(m.value)+'% | '+_refs([m.id])+' |')
        if not any(m.method=='same_region_monthly_change_v1' for m in metrics):
            lines.append('| 해당 지역 | 미확인 | 동일 정의의 연속 월 자료 부족 | 변화 계산 보류 |')
        lines.extend(['',
            '매매·전세 조사 지수는 각 지역의 가격 변화 방향을, 실거래지수는 신고 거래 기반의 변화를, 거래호수는 거래 활동을 보여준다. **지수 수준은 아파트 가격(원)이 아니며 서로 다른 지역의 지수 수준으로 비싼 지역을 순위화할 수 없다.** 지수의 기준시점도 함께 보존했다.',
            '네 통계의 마지막 확보월은 다를 수 있다. 실거래 신고 지연·취소·개정과 조사 표본의 차이 때문에 같은 달·같은 시장가격으로 합치지 않는다. 최근 월이 빠졌다면 현재 월로 보간하지 않았다.',
            '전월 대비 상승은 투자할 가격이 싸다는 증명이 아니다. 전세지수 상승도 해당 매물의 전세금·전세가율·임대수익률을 알려주지는 않는다. 거래량 감소가 있더라도 그것만으로 가격 하락을 확정할 수 없다.',
            '지금 확인할 수 있는 것은 지역별 가격·임대·거래 활동의 동반 변화다. 개별 실거래 가격, 공급/입주, 대출금리·조건과 금융비용, 전세금 반환 및 실제 매물의 현금흐름이 없어서 아파트 투자의 상대 매력은 유보한다.',
            '판단을 바꿀 자료: 지역/단지/면적별 실제 가격과 거래량, 전세 계약·가격, 공급 일정과 대출 견적, 필요한 자기자금·보유기간 및 대체 투자의 수익/손실 경로.',''])
    return lines
