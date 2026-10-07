"""Reader-facing comparison; numbers and every inference retain input refs."""
from decimal import Decimal, localcontext
from .semiconductor_data import COMPANIES, observations, audit
from .macro_report import _number


def sections(run):
    from .orchestrator_report import _refs
    from .sources import _time
    rows=observations(run.case,run.cutoff);review=audit(run)
    metrics={m.id:m for m in run.result.metrics}
    def get(asset,key,period=None):
        items=[e for (k,p),group in rows[asset].items() if k==key and (period is None or p==period) for e in group]
        return items[0] if len(items)==1 else None
    def latest(asset,key):
        ps=[p for k,p in rows[asset] if k==key and len(rows[asset][k,p])==1 and p.endswith(('Q1','Q2','Q3','Q4'))]
        return get(asset,key,max(ps)) if ps else None
    def metric(asset,key):return metrics.get('CALC_SEMI_'+asset+'_'+key)
    def display(item,money=False):
        if item is None or item.value is None:return '확인 불가'
        if money:
            with localcontext() as ctx:
                ctx.prec=50;value=item.value/Decimal(1000000)
            return _number(value)+'조 원 ('+_refs([item.id])+')'
        return _number(item.value)+' ('+_refs([item.id])+')'
    def refs(asset,keys):return _refs([e.id for (k,p),group in rows[asset].items() if k in keys for e in group])
    sam_pe,sk_pe=metric('SAMSUNG','PE'),metric('SK_HYNIX','PE')
    price_dates=[e.period for a in COMPANIES for (k,p),group in rows[a].items() if k=='close' for e in group]
    aligned=len(price_dates)==2 and len(set(price_dates))==1
    lines=['## 한눈에 보기','',
        '**현재 데이터로 우열 판단 어려움.** 사업 실적과 현재 주가를 연결해 볼 자료는 늘었지만, SK하이닉스의 원공시·이익 귀속·영업외 손익 세부를 확인하지 못해 확정적인 상대 risk/reward 판단은 유보한다.',
        '', '삼성전자는 반도체와 스마트폰·가전 등 여러 사업을 함께 보유한다. SK하이닉스는 메모리 사업의 변화가 투자 논리에 더 직접적으로 작용한다. 어느 사업이 빠르게 성장하는지와 어느 주식을 싸게 사는지는 별도 질문이다.',
        '', '아래 투자 논리는 확인한 자료에 연결한 **조건부 해석 초안**이다. 기술 우위·미래 수익·매수 명령을 자동 확정한 결과는 아니다.',
        '', '## 현재 가격과 valuation','',
        'P/E는 주가를 1주당 이익(EPS)으로 나눈 배수다. trailing은 실제로 기록된 과거 이익, forward는 아직 실현되지 않은 예상 이익이다. 이익수익률은 EPS/주가이며 배당이나 확정 투자 수익률이 아니다.',
        '', '| 같은 산술 공식의 입력·결과 | 삼성전자 보통주 | SK하이닉스 보통주 |', '| --- | --- | --- |']
    for title,key in [('표시 장마감 가격 (원/주)','close')]:
        lines.append('| '+title+' | '+display(get('SAMSUNG',key))+' | '+display(get('SK_HYNIX',key))+' |')
    lines.append('| 가격 기준일 | '+(get('SAMSUNG','close').period if get('SAMSUNG','close') else '미확보')+' | '+(get('SK_HYNIX','close').period if get('SK_HYNIX','close') else '미확보')+' |')
    for title,key in [('최근 12개월 EPS (원/주)','TTM_EPS'),('종가/최근 12개월 EPS (배)','PE'),('EPS/종가 (%)','EY')]:
        lines.append('| '+title+' | '+display(metric('SAMSUNG',key))+' | '+display(metric('SK_HYNIX',key))+' |')
    lines.extend(['| 시가총액·일반 P/B | 현재 주식 수·우선주/자본 귀속 미검증으로 보류 | 현재 주식 수·지배주주 자본 귀속 미검증으로 보류 |',
        '| forward P/E·revision | 정의된 최신 consensus 미확보 | 정의된 최신 consensus 미확보 |','',
        '가격은 **한국경제 코리아마켓의 표시 종가**다. KRX 직접 대조는 미완료이며 수정주가 여부도 명시되지 않았다. 보통주 코드 005930·000660을 확인했고 삼성전자 우선주를 섞지 않았다. 관측된 장마감 날짜를 현재 거래일로 바꾸지 않았다.',
        '', '삼성전자는 공식 연결 기본 보통주 EPS를 `전년 연간 + 현재 반기 − 전년 반기`로 합산한다. SK하이닉스는 제공자가 설명한 가중평균 보통주 EPS의 연속 네 분기를 더한다. 분기 하나에 네 배를 곱하지 않는다. 기간별 가중평균 주식 수가 달라 현재 발행 주식 수로 재작성한 EPS와 차이가 있을 수 있다.',
        '', '**같은 공식이 같은 검증 수준을 뜻하지 않는다.** 삼성전자의 기본 보통주 정의는 공식 주석으로 확인한다. SK하이닉스 제공자는 이익/가중평균 보통주 수를 명시하지만 연결 범위·지배주주 귀속·원공시 대조가 미완료여서 그 배수는 잠정이다. ('+refs('SAMSUNG',{'ordinary_eps'})+')',
        '', 'SK하이닉스 제공자의 BVPS는 무형자산을 뺀 장부가치다. 이 값으로 일반 P/B를 만들어 삼성전자와 비교하지 않았다. 순이익/영업이익에 보통주 시가총액을 붙일 때도 우선주·비지배지분·주식 수 기준이 맞아야 하므로 현재 입력으로 억지로 계산하지 않았다. ('+refs('SK_HYNIX',{'tangible_bvps'})+')'])
    if not aligned:lines.extend(['','두 종목의 같은 날짜 가격을 확보하지 못해 현재 시점의 직접 가격 비교가 추가로 제한된다.'])
    if sam_pe and sk_pe:
        lower='SK하이닉스' if sk_pe.value<sam_pe.value else '삼성전자' if sam_pe.value<sk_pe.value else '두 회사'
        lines.extend(['','표시된 입력의 산술 배수는 '+lower+' 쪽이 '+('같다' if sk_pe.value==sam_pe.value else '낮다')+'. 다만 원공시와 반복 가능한 이익의 확인 없이 이를 저평가나 투자 우위로 승격하지 않는다. ('+_refs([sam_pe.id,sk_pe.id])+')'])
    lines.extend(['','## 최근 실적','',
        '| 기업·항목 | 최근 확보 분기 | 전년 같은 분기 | 자료의 성격 |','| --- | --- | --- | --- |'])
    growth=[]
    for asset,(name,_,_) in COMPANIES.items():
        for key,label in [('revenue','매출'),('operating','영업이익'),('net','순이익')]:
            e=latest(asset,key);prior=get(asset,key,str(int(e.period[:4])-1)+e.period[4:]) if e else None
            lines.append('| '+name+' '+label+' | '+(e.period+' · '+display(e,True) if e else '미확보')+' | '+display(prior,True)+' | '+('공식 연결 재무제표; 순이익은 비지배지분 포함' if asset=='SAMSUNG' else 'IR 연결 제공자; 이익 귀속 원공시 미검증')+' |')
        e=latest(asset,'revenue')
        margin=metric(asset,'MARGIN_'+e.period) if e else None
        for m in [margin,metric(asset,'REVENUE_YOY'),metric(asset,'OPERATING_YOY')]:
            if m:growth.append('- '+m.label+': '+_number(m.value)+'% ('+_refs([m.id])+').')
    lines.extend(['',*growth])
    lines.extend(['','### DART 원공시와 제공자 대조',''])
    for asset,(name,_,_) in COMPANIES.items():
        registration=refs(asset,{'filing_registered'})
        lines.append('- '+name+': '+registration+'. 접수목록 확인과 본문 재무 수치 검증은 구분한다. 원문 접근 상태는 아래 발견·검증 기록에 남아 있다.')
    for check in review['cross_checks']:
        if check['status']=='consistent_with_release_rounding':
            lines.append('- 삼성전자 '+check['period']+' '+('매출' if check['field']=='revenue' else '영업이익')+': 공식 상세 재무제표와 기존 공식 발표문의 조 원 단위 반올림 범위 안에서 일치한다. ('+_refs(check['evidence_ids'])+')')
        elif check['status']=='mismatch':
            lines.append('- **삼성전자 수치 불일치**: '+check['field']+'. 같은 분기·단위의 반올림 범위를 넘어 원인 확인이 필요하다. ('+_refs(check['evidence_ids'])+')')
        elif check['status']=='original_filing_unavailable':
            lines.append('- SK하이닉스: 동일 Euroland 페이지의 재추출은 독립적인 검증이 아니다. DART 본문과 값이 일치한다고 주장할 수 없다.')
    lines.extend(['','## 이익의 질','',
        '매출·영업이익 증가 자체는 확인할 수 있지만 가격 상승·물량·제품 구성·비용·일회성 효과의 기여를 분리하려면 회사의 상세 설명이 필요하다. 큰 증가율만으로 기술 경쟁력 개선을 확정하지 않는다.'])
    explanations=[('price_mix','삼성전자는 AI 수요에 맞춘 서버 제품 구성과 업계 가격 상승을 기록적 실적의 요인으로 설명했다. 물량·가격·제품 구성 각각의 정량 기여는 공개된 구절만으로 분해하지 못한다.'),
        ('hbm_statement','삼성전자는 HBM4 판매 확대와 HBM4E 샘플 출하를 설명했다. 이는 회사의 공식 주장이다. 업계 최고 성능이라는 표현이나 고객 인증·양산 물량을 독립적으로 확정하지 않는다.'),
        ('foundry_cost','삼성전자는 파운드리 이익 개선을 인센티브 관련 충당금을 반영하기 전 기준으로 설명했다. 수요 증가와 비용·충당금의 영향을 구분해야 하며 조정 전 개선을 실제 최종 이익과 같게 해석하지 않는다.')]
    for key,text in explanations:
        selected=get('SAMSUNG',key)
        if selected:lines.extend(['',text+' ('+_refs([selected.id])+')'])
    sam_cfo=metric('SAMSUNG','CFO_AFTER_PPE')
    if sam_cfo:
        lines.extend(['','삼성전자는 반기 영업현금흐름과 유형자산 취득 현금지출을 구분해 확인했다. 유형자산 취득을 뺀 영업현금흐름은 '+display(sam_cfo,True)+'다. 무형자산·인수·리스 등을 모두 차감한 전체 free cash flow나 경영진이 발표한 CAPEX와는 다르다.'])
    residual=metric('SK_HYNIX','NONOPERATING_RESIDUAL');share=metric('SK_HYNIX','NONOPERATING_SHARE')
    if residual and share:
        lines.extend(['','SK하이닉스 제공자 표의 최근 분기 세전이익−영업이익은 '+display(residual,True)+', 세전이익의 '+display(share)+'%다. 본업 밖의 손익이 순이익 배수의 분모에 영향을 준다. 세부 주석이 없어서 환율·파생·평가이익·일회성 요인 중 어떤 것인지 확정하지 않는다. 순이익이 큰 것을 HBM의 반복 가능한 현금 이익으로 해석하면 위험하다.'])
    lines.extend(['','SK하이닉스의 투자활동 현금흐름은 CAPEX 자체가 아니다. 표가 단일 분기인지 누적인지도 원공시로 확인하지 못했으므로 삼성전자 반기 현금흐름과 동일 기준으로 비교하지 않았다. ('+refs('SK_HYNIX',{'cfo','investing_cf'})+')',
        '', '삼성전자의 사업부·전망 구절은 실제 보고한 사업부 실적과 경영진 기대를 구분한다. MX/네트워크의 손실이 확인되면 반도체 호황이 전체 사업에 같은 속도로 퍼진다고 볼 수 없다. HBM 세대별 매출·고객 인증·DRAM/NAND 가격과 물량의 기여는 현재 자료로 정밀 검증하지 못했다.',
        '', '## 삼성전자 Bull / Bear','',
        '**가장 강한 Bull 가설:** 공식 자료에서 확인한 반도체 실적과 현금 창출이 이어지고 고부가 메모리 공급 확대가 실제 이익으로 연결된다면, 여러 사업을 가진 회사의 수익 기반이 강화될 수 있다. 필요한 것은 HBM 회복을 믿는 서사가 아니라 실제 매출·이익·현금 회수다. ('+refs('SAMSUNG',{'revenue','operating','cfo','investment_commitments'})+')',
        '', '**가장 강한 Bear 가설:** 최근 높은 메모리 수익성이 업황 고점이라면 이익이 정상화되면서 현재 과거 이익 배수가 올라갈 수 있다. 스마트폰 등 다른 사업의 손실·비용과 설비 투자가 개선분을 줄일 수 있다. 사업 다각화가 자동으로 투자 손실을 줄이는 것은 아니다. ('+refs('SAMSUNG',{'operating','ppe_cash'})+')',
        '', '## SK하이닉스 Bull / Bear','',
        '**가장 강한 Bull 가설:** 고부가 메모리·AI 수요가 지속되고 현재 표시된 영업이익이 반복 가능하다면, 메모리에 집중한 사업이 큰 이익을 유지할 수 있다. 잠정 배수가 낮다면 검증 후 상대 가격 매력을 따져 볼 이유가 있다. HBM 기술 우위와 고객 수요를 현재 재무 숫자만으로 확정하지는 않는다. ('+refs('SK_HYNIX',{'revenue','operating','eps'})+')',
        '', '**가장 강한 Bear 가설:** 순이익에 본업 외 이익이 크게 포함되어 있거나 공급 확대·가격 하락·CAPEX가 수익성을 낮추면, 낮은 과거 이익 배수가 싸 보이는 착시일 수 있다. 원공시 세부 손익과 투자 회수가 확인되지 않은 점이 현재 논리의 약점이다. ('+refs('SK_HYNIX',{'pretax','net','investing_cf'})+')',
        '', '## 시장이 기대하고 있는 것','',
        '**추론:** 현재 가격을 정당화하려면 최근 커진 이익이 유지되거나 추가 사업 성장이 이를 보완해야 한다. 삼성전자 HBM 회복이나 SK하이닉스의 메모리 성장 가능성이 있다는 사실과, 그 기대를 현재 가격이 얼마나 반영했는지는 다르다.',
        '', '현재·과거의 동일 정의 배수 추이와 정의된 forward consensus가 없어 정확한 성장 기대를 가격에서 역산하거나 “이미 다 반영됐다”고 단정하지 않는다. 이 보고서는 실적이 좋은 산업과 투자 가격이 좋은 주식을 구분하는 출발점이다.',
        '', '## Community narrative와 실제 자료',''])
    source_map={s.id:s for s in run.case.sources}
    narratives=[e for e in run.case.evidence if e.kind=='observed_narrative' and e.provenance
                and e.provenance.match_status=='matched' and e.provenance.freshness=='fresh'
                and source_map[e.source_id].provenance.status=='available'
                and _time(source_map[e.source_id].provenance.retrieved_at)<=run.cutoff
                and not any(_time(t)>run.cutoff for t in (source_map[e.source_id].provenance.published_at,
                    source_map[e.source_id].provenance.observed_at,source_map[e.source_id].provenance.valid_as_of) if t)
                and set(e.asset_ids)&set(COMPANIES)]
    if narratives:
        for e in narratives:lines.append('- 실제 발견한 공개 발언: '+e.text+' ('+_refs([e.id])+'). 발언 내용은 미확인이다.')
        checks=run.discovery.get('community_verification',[]) if run.discovery else []
        for check in checks:
            if set(check.get('asset_ids',[]))&set(COMPANIES):
                lines.append('- 원자료 대조: '+check['reason']+' ('+_refs(check['evidence_ids'])+').')
    else:lines.append('이번 실행에서 관련성과 최신성을 함께 충족한 원문 토론을 확보하지 못했다. HBM 기술격차·삼성 회복·메모리 supercycle·중국 경쟁을 실제 관측한 community 주장처럼 기록하지 않았다.')
    lines.extend(['','검색 snippet·일반 뉴스·좋아요·반복을 community 사실 증거로 대체하지 않는다. 접근 제한은 우회하지 않았으며 표본은 시장 전체의 의견을 대표하지 않는다.',
        '', '## 현재 가격에서 더 매력적인 쪽','', review['judgment']+'. '+review['reasoning'],
        '', '잠정 이익배수가 낮은 쪽을 찾는 것과 위험 대비 더 좋은 주식을 찾는 것은 다르다. 특히 순이익의 지속성, 현재 주식 수·자본 귀속, 공시와 제공자 차이를 먼저 해결해야 한다. 가격목표·임의의 점수·배분 비중은 만들지 않았다.',
        '', '## 무엇이 바뀌면 판단이 달라지는가','',
        '- SK하이닉스 원공시에서 연결/지배주주 이익과 영업외 손익의 규모·반복 가능성이 확인되면 잠정 배수의 의미가 달라진다.',
        '- 양사의 HBM·DRAM·NAND 가격/물량/제품 구성, 실제 고객 매출과 마진이 지속되는지 확인한다. 기술 인증에 대한 주장은 공식 확인을 따로 요구한다.',
        '- 같은 기간 CFO·실제 유형자산 CAPEX·재고·투자 약정을 확보하면 회계 이익과 현금 회수의 차이를 평가할 수 있다.',
        '- 두 종목의 같은 날짜 KRX 시세·현재 주식 수·주식 종류와 수정 정책을 확인하고 예상 이익의 정의·revision을 확보한다.',
        '', '## 한국 투자자에게 의미하는 것','',
        '두 종목은 원화 보통주다. 미국 주식의 USD/KRW 환산 노출을 그대로 적용하지 않는다. 회사가 해외 매출·원가·재무에서 받는 환율 영향은 원화로 상장된 주식 자체의 투자 통화와 구분한다.',
        '', '이미 한국 주식·반도체를 많이 보유했는지, 신규자금의 사용 시점·부채·계좌·비용·세금이 어떤지는 미확인이다. 자산 자체의 상대 매력과 내 포트폴리오에 추가할 적절성은 별개다.',
        '', '## 초간단 설명','',
        '회사 실적이 좋아도 주식 가격이 비싸면 좋은 투자가 아닐 수 있다. 삼성전자는 여러 사업을 하고, SK하이닉스는 메모리 변화의 영향을 더 크게 받는다. 우리는 현재 표시된 주가를 실제 과거 이익과 연결해 계산했다. 하지만 SK하이닉스 숫자는 원공시와 충분히 맞춰 보지 못했고, 본업 밖의 이익도 확인해야 한다. 삼성전자의 다른 사업 손실과 큰 설비 투자도 함께 봐야 한다. 그래서 지금은 어느 주식이 확실히 더 낫다고 결정하기 어렵다. 이익이 얼마나 오래 이어지고 실제 현금이 얼마나 남는지 확인하면 판단이 더 선명해진다.',''])
    return lines
