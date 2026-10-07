"""Short Korean commodity deep dives with separately traceable draft reasoning."""
from decimal import Decimal
from zoneinfo import ZoneInfo

from .commodity_data import VERSION, ASSETS
from .scan import eligible

GSCI_SECTORS=(('ENERGY','에너지'),('INDUSTRIAL','산업금속'),('PRECIOUS','귀금속'),
    ('AGRICULTURE','농산물'),('LIVESTOCK','축산'))


def _same_period_groups(facts):
    rows=[]
    for key,_ in GSCI_SECTORS:
        matches=[e for e in facts if e.value is not None and e.provenance.definition['measure']=='SP_GSCI_'+key+'_YTD_TOTAL_RETURN']
        if len(matches)!=1:return []
        rows+=matches
    identity=lambda e:tuple(e.provenance.definition[k] for k in ('period','unit','currency','adjustment'))
    if (len({identity(e) for e in rows})!=1 or rows[0].unit!='percent' or rows[0].currency!='USD'
            or any(e.observed_at is None or e.period!=e.observed_at.isoformat() for e in rows)):
        return []
    return rows


def assessment(run):
    facts=eligible(run.case,run.cutoff);metrics=list(run.result.metrics);assets={}
    def has(measure):return any(e.provenance.definition['measure']==measure and e.value is not None for e in facts)
    for asset in sorted({m['id'] for m in run.input['methods']}&ASSETS):
        ids=[e.id for e in facts if asset in e.asset_ids]
        calc=[m.id for m in metrics if asset in m.asset_ids]
        needs=[n for n in (run.discovery or {}).get('needs',[]) if n['asset_id']==asset]
        gaps=[n['label']+': '+g for n in needs for g in n['gaps']]
        if asset=='NATGAS':
            meaningful=has('EIA_HENRY_HUB_SPOT') and has('EIA_US_WORKING_GAS_STOCK')
            action='관찰' if meaningful else '데이터 부족'
            reason='가격·재고·생산·LNG·날씨와 실제 계약 비용을 함께 확인한다. 한쪽 신호만으로 강한 진입 논리를 확정하지 않는다.'
            gaps.extend(['현재 주간 Lower 48 실제 생산·당일 LNG feedgas/시설 가동률',
                'EIA 공식 보간 오년 평균·시장 기대 주입량·비교 가능한 이전 기상 forecast',
                'UNG/BOIL 현재 일별 보유계약·실제 roll 체결; BOIL 최신 비용/지수 규칙 본문',
                'CFTC 같은 정의 장기 표본의 포지션 백분위; 개인 보유기간·손실 한도'])
        elif asset=='GOLD':
            meaningful=has('LBMA_GOLD_PM_ISSUER_REPORTED') and has('US_TIPS_10Y_CURRENT')
            action='관찰' if meaningful else '데이터 부족'
            reason='ETF·중앙은행 수요와 실물 소비의 차이를 구분한다. 수요 자료의 시차와 이자/달러 대안 때문에 현재 가격 진입 판단은 조건부다.'
            gaps.extend(['최신 9월/10월 전체 금 ETF flow·같은 IAU의 이전 보유 관측',
                '최신 월간 중앙은행 국가별 확정 매수·중국/인도 실제 수입/프리미엄',
                '같은 관측일·정의의 기대 인플레이션과 금 가격의 충분한 기간 비교',
                '국내 KRX 금·한국 금 ETF의 현재 비용/계좌 과세·개인 포트폴리오 역할'])
        else:
            meaningful=has('ISHARES_GSG_NAV')
            action='확인 후 진입 검토' if meaningful and has('GSCI_WEIGHT_LCO') else '데이터 부족'
            reason='가격과 구성의 실제 관측은 늘었지만 구성 기준일·하위시장 수급·연초 이후 성과 기여가 다르다. 광범위 동반 강세나 인플레이션 방어를 확정하지 않는다.'
            groups=_same_period_groups(facts) if run.input.get('observation_dates_version') else []
            gaps.extend([('현재 S&P GSCI/GSG 전체 구성비·정확한 공식 YTD 성과 기여도' if groups else '현재 S&P GSCI/GSG 전체 구성비·동일 YTD 기간 하위 지수 성과/기여도'),
                '산업금속 실제 재고·중국 수요·광산 공급; 농산물 실제 재고/수확·작황',
                '모든 하위 계약 곡선·실현 roll yield·담보 이자와 총비용의 성과 분해',
                '다른 자산과 같은 기간의 correlation·개인 보유 목적/계좌 조건'])
        assets[asset]=dict(action=action,judgment='mixed' if meaningful else 'insufficient evidence',
            reasoning=reason,evidence_ids=ids,metric_ids=calc,gaps=list(dict.fromkeys(gaps)),
            interpretation_status='pending',source_count_is_not_attractiveness=True,
            counterargument='강한 수요가 실제로 지속되고 불리한 공급·보유 비용을 넘어설 수 있다. 반대로 이미 가격에 반영되었거나 수요가 약화될 수 있다.',
            reassessment='현재 가격·독립 수급·같은 정의 변화와 실제 보유 상품 조건을 다시 확인한다.')
        if asset=='BROAD_COMMODITIES' and run.input.get('observation_dates_version'):
            assets[asset]['attribution']={'same_period_sector_returns':bool(groups),
                'period_end':groups[0].period if groups else None,'evidence_ids':[e.id for e in groups],
                'exact_GSG_contribution':'unavailable','weight_times_return_estimate':'not_computed_dated_midyear_weights_are_not_starting_weights',
                'roll_and_collateral_decomposition':'unavailable'}
    return dict(method_version=VERSION,question=run.input['question'],as_of=run.cutoff.isoformat(),
        economic_interpretation='draft_not_verified_trade_or_allocation',assets=assets)


class View:
    def __init__(self,run,asset):
        self.run=run;self.asset=asset
        self.facts=[e for e in eligible(run.case,run.cutoff) if asset in e.asset_ids]
        self.metrics=list(run.result.metrics)

    def select(self,measure):
        return sorted([e for e in self.facts if e.provenance.definition['measure']==measure],key=lambda e:e.provenance.definition['period'])

    def fact(self,measure,last=True):
        values=self.select(measure)
        return values[-1 if last else 0] if values else None

    def metric(self,identifier):return next((m for m in self.metrics if m.id==identifier),None)

    @staticmethod
    def value(item,digits=2):
        if item is None or item.value is None:return '미확보'
        v=item.value.quantize(Decimal(1).scaleb(-digits))
        return format(v,',f')

    @staticmethod
    def refs(items):
        from .orchestrator_report import _refs
        return _refs([i.id for i in items if i is not None])

    def row(self,label,measure,unit,note=''):
        e=self.fact(measure)
        if e is None:return '| '+label+' | 미확보 | 관련 판단 보류 |'
        return '| '+label+' | '+self.value(e)+' '+unit+' | '+e.provenance.definition['period']+' · '+note+' '+self.refs([e])+' |'

    def contract_row(self,label,measure,change_measure,unit,digits=2):
        prices=self.select(measure);change=self.fact(change_measure)
        if not prices:return '| '+label+' | 미확보 | 관련 판단 보류 |'
        # A later expiry is a different instrument, even on the same bulletin
        # date. Match the separately reported daily change to its own contract.
        def identity(e):
            d=e.provenance.definition
            return tuple(d[k] for k in ('scope','period','unit','currency'))
        matches=[e for e in prices if change is not None and identity(e)==identity(change)]
        e=matches[0] if matches and len({e.value for e in matches})==1 else sorted(prices,key=lambda e:e.provenance.definition['scope'].split()[-1])[0]
        d=e.provenance.definition
        note=d['scope'].split()[-1]+' 인도 계약 · '+('잠정 정산' if 'preliminary' in d['adjustment'] else '정산')
        return '| '+label+' | '+self.value(e,digits)+' '+unit+' | '+d['period']+' · '+note+' '+self.refs([e])+' |'


def sections(run):
    audits=assessment(run)['assets'];lines=[]
    if run.input['synthetic']:lines+=['**합성 fixture 검증이다. 실제 투자 판단에 사용하지 않는다.**','']
    for asset,audit in audits.items():
        v=View(run,asset)
        if len(audits)>1:lines+=['# '+{'NATGAS':'천연가스','GOLD':'금','BROAD_COMMODITIES':'광범위 원자재'}[asset],'']
        lines+=['## 현재 결론','', '**'+audit['action']+' · '+audit['judgment']+'**. '+audit['reasoning'],
            '', '아래 판단은 근거에 연결한 해석 초안이다. 실제 매매 명령·개인 비중은 사용자의 보유기간·자금수요·손실 감당 조건 없이는 정하지 않는다.','']
        if asset=='NATGAS':lines+=gas_sections(v)
        elif asset=='GOLD':lines+=gold_sections(v)
        else:lines+=broad_sections(v)
        if run.input.get('observation_dates_version'):
            lines+=['**관측일 확인:** 본문 비교 기간과 각 값의 날짜를 대조했다. 자료 전체 최신일·공개일·획득일을 과거 값의 날짜로 사용하지 않았다. 월·분기 자료의 날짜는 보고기간 말일 표기다. [값별 날짜 확인](observation_integrity.json).','']
        lines+=['## 지금 행동','']
        if asset=='NATGAS':
            ung_known=bool(v.select('UNG_BENCHMARK_AND_ROLL') and v.fact('UNG_MANAGEMENT_FEE'))
            lines+=['- **천연가스 자체: '+audit['action']+'.** LNG 수요와 겨울 수요 가설을 현재 재고·생산·기온과 함께 확인한다. 계절성만으로 진입을 정당화하기 어렵다.',
                '- **UNG: '+('확인 후 진입 검토' if ung_known else '데이터 부족')+'.** 현물 방향 외에 실제 보유계약·교체 비용·보수·보유기간을 먼저 확인한다.',
                '- **BOIL: 데이터 부족.** 최신 본문의 지수·계약·비용 확인이 제한되어 상품 진입 판단은 보류한다. 방향이 맞아도 일별 레버리지 경로가 성과를 바꿀 수 있다.','']
        elif asset=='GOLD':
            lines+=['- **더 연구할 가치:** ETF·중앙은행 수요가 실질금리의 부담을 얼마나 상쇄하는지 확인할 가치가 있다.',
                '- **현재 진입 검토:** 과거 월·분기 수요의 개선만으로 현재 가격 진입을 확정하지 않는다. 개인 포트폴리오의 목적과 상품 비용을 확인해야 한다.',
                '- **기다릴 조건:** 더 최신 ETF flow와 같은 상품 보유량 변화, 금리·달러·현재 가격의 반응을 같이 확인한다.','']
        else:lines+=['**'+audit['action']+'**. 구성비의 시차와 각 하위시장 방향을 확인해야 한다. 최근 구성과 같은 기간 성과 기여가 확인되기 전 전체 원자재가 유리하다고 판단하지 않는다.','']
        lines+=['## 판단을 바꿀 조건','']
        if asset=='NATGAS':
            lines+=['- 강세 강화: 비교 가능한 forecast가 더 추워지고 실제 주입이 평년보다 둔화하거나 인출이 늘며, 생산 둔화·LNG 가동 증가가 함께 확인될 때.',
                '- 무효화/약화: 재고가 계속 쌓이고 생산 증가가 수요를 넘거나 LNG 시설 정지·따뜻한 전망이 이어질 때. 상품 roll 비용까지 악화되면 기초자산과 상품 결론은 달라진다.']
        elif asset=='GOLD':
            lines+=['- 강세 강화: 더 최신 전체 ETF 실물량·유입이 증가하고 중앙은행 매수가 지속되며 금리/달러 부담 속에서도 가격이 수요와 함께 지지될 때.',
                '- thesis 약화: ETF 유출·중앙은행 매수 둔화가 겹치고 높은 실질금리/달러가 계속 부담을 주며 가격만 수요와 분리되어 앞설 때.']
        else:lines+=['- 강세 강화: 최신 비중과 같은 기간 성과에서 여러 그룹의 독립 수급 개선이 확인되고 실제 roll/담보/비용까지 보유 논리를 지지할 때.',
            '- thesis 약화: 상승이 한 에너지 충격에 편중되고 다른 그룹 재고/수요가 악화되거나 높은 교체 비용이 총수익을 깎을 때.']
        lines+=['','## 한국 투자자에게 의미하는 것','',
            '기초자산의 달러 가격과 KRW 평가액의 환율 효과를 구분한다. USD/KRW 한 관측으로 미래 환율을 예측하지 않는다. 실제 상품의 환헤지·수수료·과세·계좌·보유기간이 확인되어야 개인에게 적절한지 평가할 수 있다.','',
            '## 초간단 설명','']
        if asset=='NATGAS':lines+=['가스 가격은 날씨와 공급, 재고, 수출에 함께 영향을 받습니다. 겨울이 온다고 무조건 오르는 것은 아닙니다. 지금 겨울 계약이 더 비싸다면 시장이 겨울 수요를 이미 기대하고 있을 수 있습니다. UNG는 가스 자체 대신 선물을 갈아타기 때문에 결과가 달라집니다. BOIL 같은 일별 레버리지 상품은 오래 보유한 수익이 단순 두 배가 아닐 수 있습니다. 현재 상품 조건까지 확인한 뒤 판단하는 편이 합리적입니다.']
        elif asset=='GOLD':lines+=['금은 이자를 주지 않지만 보유하려는 사람들의 수요가 가격을 지지할 수 있습니다. 최근 공개 자료에서는 ETF와 중앙은행, 보석 소비가 서로 다르게 움직였습니다. ETF의 돈이 늘어도 금값만 올라 그런 것인지 실제 금이 더 들어온 것인지 구분해야 합니다. 높은 실질금리는 금을 보유할 때 포기하는 이자 대안입니다. 오래된 수요 자료가 오늘도 이어진다고 단정할 수 없습니다. 현재 가격과 더 최신 수요를 함께 확인해야 합니다.']
        else:lines+=['원자재 상품에는 석유부터 구리와 곡물까지 서로 다른 시장이 섞여 있습니다. 어떤 구성은 에너지 비중이 크므로 석유 뉴스의 영향이 클 수 있습니다. 한 원자재의 상승이 전체 원자재의 강세를 뜻하지 않습니다. 선물 교체 비용과 담보 이자도 상품 수익에 영향을 줍니다. 오래된 구성비로 올해 수익을 누가 만들었는지 확정할 수 없습니다. 현재 구성과 같은 기간 자료를 확인한 뒤 진입을 검토해야 합니다.']
        lines+=['']
    return lines


def gas_sections(v):
    spot=v.select('EIA_HENRY_HUB_SPOT');stock=v.select('EIA_US_WORKING_GAS_STOCK');curve=v.select('CME_NG_SETTLEMENT')
    prod=v.metric('SCAN_GAS_PRODUCTION_DAILY_YOY');lng=v.metric('SCAN_GAS_LNG_EXPORTS_DAILY_YOY');season=v.metric('SCAN_GAS_STOCK_VS_SEASONAL_REFERENCE')
    lines=['## 왜 지금?','']
    if len(spot)>=2:lines+=['- Henry Hub 현물은 '+spot[0].period+'의 '+v.value(spot[0])+'에서 '+spot[-1].period+'의 '+v.value(spot[-1])+' 달러/MMBtu로 변했다. 최신 실제 발표와 현재 선물가격의 시점은 다르다. '+v.refs(spot)]
    if season:lines+=['- 현재 재고는 자체 같은 ISO 주 오년 기준 대비 '+v.value(season)+'% 차이다. 공식 오년 평균과 다르며 재고 부족을 계절성만으로 주장하지 않는다. '+v.refs([season])]
    if prod and lng:lines+=['- 월간 실제 일평균의 전년 대비 변화는 생산 '+v.value(prod)+'%, LNG 수출 '+v.value(lng)+'%다. 둘 다 시차 있는 월간 실제량이며 당일 생산/수출시설 feedgas가 아니다. '+v.refs([prod,lng])]
    lines+=['- 기온 전망·실제 냉난방 수요와 계약 교체 비용은 반대 방향으로 작용할 수 있다. 단일 신호만으로 결론내리지 않는다.','',
        '## 가격과 실제 수급','', '| 항목 | 값 | 기준·의미 |','| --- | --- | --- |',
        v.row('현재 working gas','EIA_US_WORKING_GAS_STOCK','Bcf','미국 Lower 48'),
        v.row('월간 실제 dry gas 생산','EIA_US_DRY_GAS_PRODUCTION','MMcf','미국 전체·월간'),
        v.row('월간 실제 LNG 수출','EIA_US_LNG_EXPORTS','MMcf','당일 feedgas 아님')]
    injections=sorted([m for m in v.metrics if m.id.startswith('CALC_COMMODITY_GAS_INJECTION_')],key=lambda m:m.id)
    if injections:
        lines+=['','최근 주입/인출(Bcf; 양수=주입): '+', '.join(m.id[-8:]+': '+v.value(m) for m in injections)+'. '+v.refs(injections)]
    reference=v.metric('CALC_COMMODITY_GAS_REFERENCE_INJECTION')
    if reference:lines+=['과거 같은 ISO 주 자체 오년 순주입 평균은 '+v.value(reference)+' Bcf다. 시장 예상치가 없으므로 “예상보다” 빠르다는 판단은 보류한다. '+v.refs([reference])]
    prior=[e for e in v.facts if e.provenance.definition['measure'].startswith('EIA_GAS_ISO_WEEK_REFERENCE_')]
    if prior:
        e=max(prior,key=lambda e:e.period);lines+=['전년 같은 ISO 주 재고 '+v.value(e)+' Bcf ('+e.period+'). 같은 달력 날짜/공식 보간 평균과 구분한다. '+v.refs([e])]
    if v.run.input.get('observation_dates_version'):
        lines+=gas_date_table(v)
    lines+=['','**날씨:** HDD(난방도일)는 얼마나 추워 난방이 필요했는지, CDD(냉방도일)는 얼마나 더워 냉방이 필요했는지 누적한 값이다. 기온 범주나 Bcf 수요와 같지 않다.']
    for measure,label in [('NOAA_HDD_TOTAL','가스 난방 고객 가중 미국 HDD'),('NOAA_HDD_VS_NORMAL','HDD 평년 대비'),('NOAA_CDD_TOTAL','인구 가중 미국 CDD'),('NOAA_CDD_VS_NORMAL','CDD 평년 대비')]:
        e=v.fact(measure)
        if e:lines+=['- '+label+': '+v.value(e)+' 도일, '+e.provenance.definition['period']+'. '+v.refs([e])]
    forecasts=[e for e in v.facts if e.provenance.definition['measure'].startswith('NOAA_CPC_')]
    if forecasts:
        by_window={}
        for e in forecasts:
            parts=e.text.split();temp=parts[-2]
            place=' '.join(parts[:-2]);label={'NEW YORK':'뉴욕','OHIO':'오하이오','N TEXAS':'북텍사스'}.get(place,place)
            by_window.setdefault(e.provenance.definition['period'],[]).append(label+' '+{'A':'평년보다 따뜻함','N':'평년 근처','B':'추움'}.get(temp,'범주 미확인'))
        for period,regions in by_window.items():
            window=period.removeprefix('forecast_valid_').replace('_to_','~')
            refs=[e for e in forecasts if e.provenance.definition['period']==period]
            lines+=['- CPC '+window+' 전망: '+', '.join(regions)+'. 이전 동일 표본이 없어 전망이 더 추워졌다고 말하지 않는다. '+v.refs(refs[:1])]
    net=v.metric('CALC_COMMODITY_NATGAS_MM_NET');change=v.metric('CALC_COMMODITY_NATGAS_MM_NET_CHANGE')
    if net:lines+=['','**포지셔닝:** managed money 순포지션 '+v.value(net,0)+' 계약'+(' / 전주 변화 '+v.value(change,0)+' 계약' if change else '')+'. 역사적 분포가 없어 과도한 long/short를 확정하지 않는다. '+v.refs([net,change])]
    lines+=['','### 선물곡선과 보유 비용','', '| 인도 월 | 가격 (달러/MMBtu) | 기준 |','| --- | --- | --- |']
    for e in sorted(curve,key=lambda e:e.provenance.definition['scope']):lines+=['| '+e.provenance.definition['scope'].split()[-1]+' | '+v.value(e,3)+' | '+e.period+' · '+('잠정' if 'preliminary' in e.provenance.definition['adjustment'] else '확정판')+' 정산 '+v.refs([e])+' |']
    if len(curve)==6:
        ordered=sorted(curve,key=lambda e:e.provenance.definition['scope']);diff=[b.value-a.value for a,b in zip(ordered,ordered[1:])]
        shape='혼합 구조' if any(d>0 for d in diff) and any(d<0 for d in diff) else 'contango' if all(d>=0 for d in diff) else 'backwardation' if all(d<=0 for d in diff) else '판단 보류'
        lines+=['','**'+shape+'**. 뒤 계약이 더 비싼 구간(contango)은 같은 노출을 이어갈 때 불리한 교체 조건이 될 수 있고, 더 싼 구간(backwardation)은 반대다. 현재 가격차가 미래 실현 손실·수익률과 같지는 않다. 겨울 구간의 높은 가격은 겨울 수요가 이미 일부 기대되고 있다는 단서다. '+v.refs(ordered)]
    else:lines+=['','계약별 곡선을 충분히 확보하지 못해 roll 조건 판단을 보류한다.']
    lines+=['','## Bull Case','', 'LNG 수출의 실제 확대에 겨울 추위가 더해지고 생산 증가가 둔화되면 재고가 줄어들 수 있다. 포지션이 매도 쪽이어도 수요 개선이 확인되면 되돌림의 촉매가 될 수 있다. 다만 현재 시차 있는 수출 증가만으로 이 조합이 이미 성립했다고 보지 않는다.',
        '', '## Bear Case','', '생산 증가·충분한 재고·따뜻한 전망이 수요의 강세 논리를 상쇄할 수 있다. 겨울 프리미엄을 이미 지불하고도 실수요가 부족하면 계약가격 하락과 교체 비용을 함께 겪을 수 있다.',
        '', '## 시장이 이미 반영한 기대','', '관측한 겨울/봄 계약의 차이는 계절 수급 기대를 보여 준다. 정확한 기대 확률이나 목표가격은 역산하지 않는다. 현재 feedgas·시설 정비·가동률이 미확인이라 LNG 월간 실적을 오늘의 가동 상황으로 바꾸지 않는다.',
        '', '## 투자상품 차이','',
        '| 대상 | 실제로 얻는 노출 | 진입 판단에서 추가 확인할 것 |','| --- | --- | --- |',
        '| 천연가스 자체 | Henry Hub 현물·지역 실물 수급 | 가격, 재고, 생산, 수요의 같은 시점 연결 |',
        '| UNG | '+('SEC 원문에서 확인한 근월/차월 선물 benchmark' if v.select('UNG_BENCHMARK_AND_ROLL') else '최신 benchmark 원문 미확인')+' | 현재 보유월·roll 체결·담보 이자·운용 비용 |',
        '| BOIL | 등록 이름은 확인. 최신 상품 본문 확인은 제한 | 일일 레버리지 목표·지수 계약·보수·현재 보유를 원문으로 확인 |','']
    for measure in ('UNG_BENCHMARK_AND_ROLL','UNG_REPORTED_FUTURES_HOLDING'):
        items=v.select(measure)
        if items:lines+=['- '+('UNG: 근월물이 만기에 가까워지면 4일에 걸쳐 다음 계약으로 benchmark를 옮기는 규칙을 확인했다.' if measure=='UNG_BENCHMARK_AND_ROLL' else 'UNG 분기말 선물 보유는 '+items[-1].provenance.definition['period']+' 자료다. 당시 계약은 현재 보유 증거로 사용하지 않는다.')+' '+v.refs(items)]
    fee=v.fact('UNG_MANAGEMENT_FEE');total=v.fact('UNG_ANNUAL_OPERATING_EXPENSES')
    if fee:lines+=['- UNG 관리보수 '+v.value(fee)+'% (첫 NAV 구간)'+(' / 2025 보고 연간 운용비 '+v.value(total)+'%' if total else '')+'. 향후 고정 총비용·세후 비용으로 확정하지 않는다. '+v.refs([fee,total])]
    lines+=['- **일일 2배 상품의 일반적 구조:** 비용·추적 차이를 제외한 설명용 식은 `각 일별 (1 + 2×수익률)의 곱 − 1`이다. 기초자산의 장기 수익률에 단순히 2를 곱한 값과 다르다. 매일의 움직임·변동성·보유기간·roll·비용이 결과에 영향을 준다. 일방향 추세에서 복리 이득이 날 수도 있어 항상 일정한 “decay”를 가정하지 않는다.',
        '- BOIL 최신 긴 공시는 기존 2MiB 수집 한도 등으로 확인이 제한될 수 있다. 아래 자료 공백을 확인하며 최신 지수/계약/보수는 등록 이름이나 다른 레버리지 상품으로 대체하지 않는다.','']
    return lines


def gas_date_table(v):
    measures={'EIA_HENRY_HUB_SPOT':'Henry Hub', 'EIA_US_WORKING_GAS_STOCK':'working gas',
        'EIA_US_DRY_GAS_PRODUCTION':'dry gas 월간 합계', 'EIA_US_LNG_EXPORTS':'LNG 수출 월간 합계'}
    rows=[e for e in v.facts if e.provenance.definition['measure'] in measures
        or e.provenance.definition['measure'].startswith('EIA_GAS_ISO_WEEK_REFERENCE_')]
    rows=sorted({(e.provenance.definition['measure'],e.period):e for e in rows}.values(),
        key=lambda e:(e.provenance.definition['measure'],e.period))
    lines=['','### 본문 비교 날짜와 evidence 관측일 대조','',
        '아래 날짜는 원문 행의 기간에서 확인했다. 월간 합계는 월 전체 값이며 관측일 필드의 말일은 기간 표기다. 공개일·획득일·자료 전체 최신일은 별도 부록에 남겼다.','',
        '| 자료 | 값 | 본문·원문 기간 | evidence 관측일 | 결과 |','| --- | --- | --- | --- | --- |']
    from .source_pipeline import observation_timing, _timestamp_day
    for e in rows:
        expected=_timestamp_day(observation_timing(e.period)['observed_at'])
        label=measures.get(e.provenance.definition['measure'],'과거 같은 ISO 주 재고')
        lines+=['| '+label+' | '+v.value(e)+' '+e.unit+' | '+e.period+' | '+str(e.observed_at or '미확인')+' | '+
            ('일치' if expected is not None and expected==e.observed_at else '미확인·변화 계산 제외')+' '+v.refs([e])+' |']
    lines+=['']
    return lines


def gold_sections(v):
    price=v.fact('LBMA_GOLD_PM_ISSUER_REPORTED');flow=v.fact('WGC_GLOBAL_GOLD_ETF_NET_FLOW');held=v.fact('WGC_GLOBAL_GOLD_ETF_HOLDINGS');delta=v.fact('WGC_GLOBAL_GOLD_ETF_HOLDINGS_CHANGE')
    bank=v.fact('WGC_CENTRAL_BANK_NET_DEMAND');real=v.fact('US_TIPS_10Y_CURRENT');jew=v.metric('CALC_COMMODITY_GOLD_JEWELLERY_YOY')
    lines=['## 왜 지금?','']
    if flow and held and delta:lines+=['- '+flow.period+' 전체 실물담보 금 ETF 순유입 '+v.value(flow)+'십억 달러, 실물량 변화 '+v.value(delta)+'톤, 월말 '+v.value(held)+'톤이다. AUM의 가격 효과와 구분되는 수요 단서다. '+v.refs([flow,delta,held])]
    if bank:lines+=['- 최근 공개된 '+bank.period+' 중앙은행·기타기관 순수요 추정은 '+v.value(bank)+'톤이다. 과거 분기 개정값과 미보고 활동 추정이 포함되어 현재 확정 매수/국가별 최신 거래로 보지 않는다. '+v.refs([bank])]
    by=v.metric('CALC_COMMODITY_GOLD_CENTRAL_BANK_YOY');bq=v.metric('CALC_COMMODITY_GOLD_CENTRAL_BANK_QOQ')
    if by and bq:lines+=['- 같은 발표판에서 중앙은행 순수요의 전년 같은 분기 대비 변화는 '+v.value(by)+'%, 전분기 대비 '+v.value(bq)+'%다. 낮은 전분기 기준과 개정/추정의 영향을 포함하므로 지금 매수 속도나 당시 발표 surprise로 해석하지 않는다. '+v.refs([by,bq])]
    if jew:lines+=['- 보석 소비량은 전년 같은 분기 대비 '+v.value(jew)+'%로 투자 수요와 다르게 움직였다. 금 가격과 지출액 증가가 실물 소비량 증가를 뜻하지 않는다. '+v.refs([jew])]
    if real:lines+=['- 십년 TIPS 실질금리 '+v.value(real)+'%는 이자를 주지 않는 금의 기회비용이다. 이 값 하나로 금 적정가격을 계산하지 않는다. '+v.refs([real])]
    lines+=['','## 가격과 실제 수급','', '| 항목 | 값 | 기준·의미 |','| --- | --- | --- |',
        v.row('LBMA 금 PM 기준가격','LBMA_GOLD_PM_ISSUER_REPORTED','달러/트로이온스','발행사 보고 기준가격'),
        v.row('최근 월말 금 기준가격 수익','LBMA_GOLD_PM_ISSUER_MONTH_RETURN','%','지정 월말·ETF 수익 아님'),
        v.row('IAU 현재 실물 보유','IAU_GOLD_PHYSICAL_HELD','톤','한 신탁 수준·증가/유입 아님'),
        v.row('전체 금 ETF 월간 순유입','WGC_GLOBAL_GOLD_ETF_NET_FLOW','십억 달러','원발행사 전체 독립 확인 전 제공자 집계'),
        v.row('중앙은행 순수요 추정','WGC_CENTRAL_BANK_NET_DEMAND','톤','분기·개정/미보고 추정 포함'),
        v.row('보석 소비','WGC_JEWELLERY_CONSUMPTION','톤','실물량·전세계'),
        v.row('바/코인 수요','WGC_BAR_COIN_DEMAND','톤','해당 분기 실물량'),
        v.row('실질 10년 금리','US_TIPS_10Y_CURRENT','%','TIPS 시장금리')]
    usd=v.select('FED_BROAD_USD_INDEX')
    if len(usd)==2:lines+=['','교역가중 명목 달러지수는 '+usd[0].period+' '+v.value(usd[0])+' → '+usd[-1].period+' '+v.value(usd[-1])+'. USD/KRW나 DXY와 다르다. 달러/금리 부담을 수요가 상쇄할 가능성은 있지만 서로 다른 월·주·일의 관측으로 인과를 확정하지 않는다. '+v.refs(usd)]
    net=v.metric('CALC_COMMODITY_GOLD_MM_NET');change=v.metric('CALC_COMMODITY_GOLD_MM_NET_CHANGE')
    if net:lines+=['CFTC managed money 순포지션 '+v.value(net,0)+' 계약'+(' / 전주 변화 '+v.value(change,0) if change else '')+'. 매수 우세 여부의 보조자료이며 장기 백분위가 없으므로 과열 확정은 유보한다. '+v.refs([net,change])]
    lines+=['','**수요 변화의 한계:** 위 월간 ETF와 분기 중앙은행/보석 자료는 오늘의 수요가 아니다. IAU 이전 같은 정의 보유량이 없어 한 시점 '+('보유량에서' if not v.fact('IAU_GOLD_PHYSICAL_HELD') else v.value(v.fact('IAU_GOLD_PHYSICAL_HELD'))+'톤에서')+' IAU 수요 증가를 주장하지 않는다. 주간 WGC 자료의 차트/다운로드가 열려도 원문 숫자가 확인되지 않으면 현재 유입으로 채우지 않는다.',
        '', '## Bull Case','', '투자자의 실물담보 ETF 매수와 중앙은행의 준비자산 수요가 지속되면 금리의 기회비용을 상쇄할 수 있다. 현금흐름이 없는 자산이므로 주식의 이익 성장이나 채권의 이자와 다른 보유 동기를 조사할 가치가 있다.',
        '', '## Bear Case','', '높은 실질금리·달러 부담, 보석 소비량 감소와 투자 수요의 반전이 겹칠 수 있다. 과거 높은 수요가 이미 가격에 반영되어 있다면 좋은 수요 소식만으로 좋은 진입가격을 뜻하지 않는다.',
        '', '## 시장이 이미 반영한 기대','', '투자 수요·준비자산 분산·불확실성에 대한 기대가 가격을 지지할 수 있다. 지정학 사건이 금 상승을 자동 보장하지는 않는다. 현재 자료로 어떤 기대가 얼마만큼 반영됐는지 또는 과열 확률을 역산하지 않는다.',
        '', '## 투자상품 차이','',
        '| 노출 | 수익의 차이 | 확인 상태 |','| --- | --- | --- |',
        '| IAU 등 실물담보 미국 금 신탁 | 실물 금 가치에서 보수/추적 차이·거래 비용, KRW 환율 영향 | '+('IAU 공식 보수 확인' if v.fact('IAU_SPONSOR_FEE') else 'IAU 공식 보수 미확인')+' |',
        '| 금 선물 상품 | 계약 가격·교체 비용·담보 이자·상품 비용, 환헤지별 차이 | '+('CME 지정 계약 확인' if v.fact('CME_GC_SETTLEMENT') else 'CME 지정 계약 미확인')+'; ETF 실제 보유/실현 roll 미확인 |',
        '| 국내 KRX 금/국내 ETF | 원화 거래가격·현물/선물 추종·비용·계좌 조건 | 현재 공식 상품/세금 원문 연결 부족; 미국 상품과 동일 취급하지 않음 |','']
    fee=v.fact('IAU_SPONSOR_FEE')
    if fee:lines+=['IAU 공식 sponsor fee '+v.value(fee)+'%/년. 매매 스프레드와 개인 계좌 세금은 별도다. '+v.refs([fee]),'']
    return lines


def broad_sections(v):
    nav=v.fact('ISHARES_GSG_NAV');ret=v.fact('ISHARES_GSG_YTD_NAV_TOTAL_RETURN')
    weights=[v.metric('CALC_COMMODITY_GSCI_'+g+'_WEIGHT') for g in ('ENERGY','INDUSTRIAL','PRECIOUS','AGRICULTURE','LIVESTOCK')]
    lines=['## 왜 지금?','']
    if nav and ret:lines+=['- GSG NAV '+v.value(nav)+'달러/주 ('+nav.period+'), YTD NAV 총수익 '+v.value(ret)+'% ('+ret.period+')이다. 현물 원자재 전체 수익률이나 동일 기간 섹터 기여와 다르다. '+v.refs([nav,ret])]
    if all(weights):lines+=['- 확인한 dated GSCI 구성에서는 에너지 비중 '+v.value(weights[0])+'%다. 다른 그룹도 있으므로 동질적인 단일 자산으로 설명하지 않는다. '+v.refs(weights)]
    lines+=['- 같은 관측일의 원유·구리·금·옥수수 계약은 방향과 수급 원인이 다를 수 있다. 한 날의 방향으로 올해 상승을 누가 만들었는지 확정하지 않는다.',
        '- 선물 교체와 담보 이자·운용비가 실제 상품 수익을 바꾼다. 현물 상승과 상품 총수익은 별개의 질문이다.','',
        '## 가격과 실제 수급','', '### 구성: 현재 확인한 가장 최근 명시 기준일','',
        '| 그룹 | 합산 비중 | 주의점 |','| --- | --- | --- |']
    for label,m in zip(('에너지','산업금속','귀금속','농산물','축산'),weights):
        lines+=['| '+label+' | '+v.value(m)+'% | '+('같은 기준일 24개 구성 종목의 합계 '+v.refs([m]) if m else '전체 구성 합계 계산 미확보')+' |']
    rawweights=[e for e in v.facts if e.provenance.definition['measure'].startswith('GSCI_WEIGHT_')]
    if rawweights:lines+=['','기준일 **'+rawweights[0].period+'**. 현재 비중이 아니다. 가격 변화/재조정으로 달라질 수 있고 반올림으로 합계가 정확히 100%가 아닐 수 있다. 담보 국채 목록은 원자재 노출비중으로 쓰지 않았다. '+v.refs(rawweights[:1])]
    if v.run.input.get('observation_dates_version'):
        lines+=broad_attribution_sections(v)
    lines+=['','### 서로 다른 대표 시장','', '| 하위시장 | 확인한 계약 가격 | 관측·범위 |','| --- | --- | --- |',
        v.contract_row('에너지: WTI','CME_CL_SETTLEMENT','CME_CL_SETTLEMENT_DAY_CHANGE','달러/배럴'),
        v.contract_row('산업금속: 구리','CME_HG_SETTLEMENT','CME_HG_SETTLEMENT_DAY_CHANGE','달러/파운드',4)]
    corn=v.metric('CALC_COMMODITY_CORN_SETTLEMENT')
    corn_quote=v.fact('CME_CORN_QUOTED_SETTLEMENT')
    corn_note=(corn_quote.provenance.definition['period']+' · '+corn_quote.provenance.definition['scope'].split()[-1]+' 인도 계약 · ' if corn_quote else '')
    lines+=['| 농산물: 옥수수 | '+v.value(corn)+'센트/부셸 | '+corn_note+'CBOT 단위 변환 확인 '+v.refs([corn])+' |',
        v.row('귀금속: LBMA 금','LBMA_GOLD_PM_ISSUER_REPORTED','달러/트로이온스','현물 PM 기준·선물과 다른 시점')]
    for measure,label in [('CME_CL_SETTLEMENT_DAY_CHANGE','WTI'),('CME_HG_SETTLEMENT_DAY_CHANGE','구리')]:
        e=v.fact(measure)
        if e:lines+=['','- '+label+' '+e.provenance.definition['scope'].split()[-1]+' 인도 계약의 전 거래일 가격차 '+v.value(e,4)+' '+e.unit+' ('+e.period+'). 단일일 변화는 같은 YTD 성과 기여나 동반 강세의 증거가 아니다. '+v.refs([e])]
    energy=v.fact('EIA_US_COMMERCIAL_CRUDE_STOCK')
    if energy:lines+=['','**에너지 수급:** 미국 상업 원유 재고 '+v.value(energy,0)+'천 배럴 ('+energy.period+'). SPR·lease stock 제외, 세계 원유 전체 수급과 구분한다. '+v.refs([energy])]
    crops=[e for e in v.facts if e.provenance.definition['measure'].startswith('USDA_WASDE_')]
    if crops:
        corn=[e for e in crops if 'CORN' in e.provenance.definition['measure']]
        wheat=[e for e in crops if 'WHEAT' in e.provenance.definition['measure']]
        descriptions=(['미국 옥수수 생산/기말 재고 전망 감소'] if corn else [])+(['세계 밀 기말 재고 전망 증가'] if wheat else [])
        lines+=['**농산물:** USDA 시장연도 자료에서 '+', '.join(descriptions)+'를 확인했다. 원문 숫자·시장연도·지역은 부록에 보존했으며 전망을 실제 재고로 사용하지 않는다. '+v.refs(crops)]
    else:lines+=['**농산물:** 실제 수급/공식 전망 연결이 부족하다. 가격만으로 부족을 확정하지 않는다.']
    lines+=['**산업금속:** 구리 계약가격은 확인했지만 실제 LME/COMEX 재고·중국 소비·광산 공급의 같은 정의 최신 관측은 부족하다. 가격 증가만으로 수요가 강하다고 결론내리지 않는다.',
        '**귀금속:** 금 ETF의 월간 수요와 실질금리 자료는 다른 금속/농산물의 근거로 확대하지 않는다. 같은 원문이 이미 열렸다면 응답을 재사용한다.','',
        '## Bull Case','', '여러 하위 시장에서 독립적인 공급 부족/수요 회복이 확인되고 유리한 선물 구조와 담보 이자가 동반된다면 기업 이익·명목 채권과 다른 수익 동인을 제공할 수 있다. 개별 시장의 강한 논리를 바스켓 전체의 상승으로 확장하려면 구성과 기간을 맞춰야 한다.',
        '', '## Bear Case','', '경기 둔화·공급 복구·작황 개선은 각각 산업금속·에너지·농산물 가격을 누를 수 있다. 오래된 구성에서 에너지가 크게 포함된 바스켓은 특정 충격에 편중될 수 있다. 현물이 올라도 불리한 교체 비용과 상품 비용 때문에 투자 수익은 약할 수 있다.',
        '', '## 시장이 이미 반영한 기대','',
        ('같은 기간 그룹 수익에서 에너지와 다른 그룹의 방향을 구분할 수 있지만, GSG의 높은 YTD 총수익은 이미 실현된 과거 상품 성과다. 현재 진입 가격의 매력·모든 그룹의 강세·향후 인플레이션 방어를 증명하지 않는다. 최신 전체 비중과 공식 기여 자료가 없어 GSG의 정확한 기여도는 계산하지 않는다.'
         if v.run.input.get('observation_dates_version') and _same_period_groups(v.facts) else
         'GSG의 높은 YTD 총수익은 실현된 과거 상품 성과다. 현재 자료로 이를 에너지의 기여, 현재 전 그룹의 강세 또는 향후 인플레이션 방어로 확정할 수 없다. 같은 기간 섹터별 total return과 최신 가중치가 없어 정확한 기여도는 계산하지 않는다.'),
        '', '## 투자상품 차이','',
        'GSG는 생산 가중 GSCI 선물 노출을 제공한다. 현물 수급/계약가격에 선물 교체(roll)·담보 이자·운용비/추적 차이가 더해져 총수익이 결정된다. 실제 위험 노출은 광범위라는 이름보다 구성비와 계약을 확인해야 한다.','']
    terms=v.select('GSG_ROLL_AND_COLLATERAL_TERMS')
    if terms:lines+=['- 공식 prospectus의 월별 교체 기간과 contango/backwardation 위험 문구를 확인했다. 실제 계약들의 현재 실현 roll yield·담보 수익을 역산하지 않았다. '+v.refs(terms)]
    oil={e.provenance.definition['scope']:e for e in v.select('CME_CL_SETTLEMENT')}
    oil=sorted(oil.values(),key=lambda e:e.provenance.definition['scope'])
    if len(oil)==3:
        diff=[b.value-a.value for a,b in zip(oil,oil[1:])]
        shape='backwardation(뒤 계약이 더 쌈)' if all(d<0 for d in diff) else 'contango(뒤 계약이 더 비쌈)' if all(d>0 for d in diff) else '혼합/평탄 구조'
        lines+=['- WTI 곡선 ('+oil[0].period+'): '+', '.join(e.provenance.definition['scope'].split()[-1]+' '+v.value(e)+'달러/배럴' for e in oil)+'. **'+shape+'**. 월별 교체 조건의 단서이며 GSG 전체의 실현 roll yield로 환산하지 않는다. '+v.refs(oil)]
    fee=v.fact('GSG_SPONSOR_FEE')
    if fee:lines+=['- GSG 공식 sponsor fee '+v.value(fee)+'%/년. 담보 이자·기타 비용·세금·추적 차이는 별도다. '+v.refs([fee])]
    lines+=['- 각 계약의 선물 구조는 서로 다르다. 모든 하위 계약의 곡선이 같다고 가정하지 않는다.',
        '- **물가 방어 검증:** CPI와 원자재 상품의 관측을 같이 보되, 서로 다른 기간·공급 충격·실질금리 조건에서는 동반 상승을 보장하지 않는다. 비교 가능한 같은 기간 시계열·비용이 없으므로 현재 hedge 효과나 상관을 계산하지 않는다.','']
    return lines


def broad_attribution_sections(v):
    groups=_same_period_groups(v.facts)
    lines=['','### 같은 기간 YTD: 실제로 어떤 그룹이 강했나?','']
    if not groups:
        return lines+['같은 정의·기간의 다섯 그룹 성과를 모두 확인하지 못했다. 서로 다른 기간 자료를 합치지 않으며 **상승 원인의 정확한 분해는 미확인**이다. GSG 총수익만으로 광범위 강세나 투자 매력을 판단하지 않는다.','']
    end=groups[0].period;year=int(end[:4])
    lines+=['기간: **'+str(year-1)+'-12-31 → '+end+'**, USD, S&P GSCI 하위 지수 **total return(선물 교체와 담보 이자를 포함하는 지수 총수익)**. 각 숫자는 공식 표의 YTD 열이며 비중이나 기여율이 아니다.','',
        '| 그룹 | 대표 지수 | 같은 기간 총수익 | 근거 |','| --- | --- | --- | --- |']
    for (key,label),e in zip(GSCI_SECTORS,groups):
        lines+=['| '+label+' | '+e.provenance.definition['scope']+' | '+('+' if e.value>0 else '')+v.value(e)+'% | '+v.refs([e])+' |']
    def aligned(measure):
        e=v.fact(measure)
        if e and e.period==end and e.observed_at and e.observed_at.isoformat()==end and e.unit=='percent' and e.currency=='USD':return e
    broad=aligned('SP_GSCI_BROAD_YTD_TOTAL_RETURN');gsg=aligned('ISHARES_GSG_YTD_NAV_TOTAL_RETURN')
    if broad:lines+=['','동일 종료일 S&P GSCI 총수익 **'+v.value(broad)+'%**'+('와 GSG NAV 총수익 **'+v.value(gsg)+'%**' if gsg else '')+'를 구분한다. 운용비·담보 운용·노출/추적 차이가 있어 둘을 같은 성과로 사용하지 않는다. '+v.refs([broad,gsg])]
    energy=groups[0]
    if energy.value>0 and all(energy.value>e.value for e in groups[1:]):
        lines+=['','**상승의 중심은 에너지였다는 해석을 지지한다.** 에너지 그룹의 상승이 다른 그룹보다 훨씬 컸고, 위의 명확한 구성일 자료에서 GSCI는 에너지 비중이 큰 바스켓이었다. 귀금속·축산까지 동반 강세였다는 설명은 실제 표와 맞지 않는다. 이는 그룹 성과와 dated 구성으로 확인하는 방향 판단이며 GSG의 정확한 기여율 계산은 아니다. '+v.refs(groups)]
    detail=[aligned('SP_GSCI_'+key+'_YTD_TOTAL_RETURN') for key in ('WTI','BRENT','NATGAS')]
    if all(detail):
        lines+=['에너지 안에서도 WTI '+v.value(detail[0])+'%, Brent '+v.value(detail[1])+'%, 천연가스 '+v.value(detail[2])+'%로 달랐다. 에너지 지수 상승을 천연가스 강세로 대체하지 않는다. 모두 같은 기간 선물 지수 총수익이며 EIA 현물 변동과 다르다. '+v.refs(detail)]
    lines+=['','**GSG 상승 원인의 정확한 분해는 미확인.** 현재/연초 비중·일별 재조정·공식 그룹별 contribution(전체 성과에 더해진 실제 기여)이 없다. 중간 시점의 과거 구성비에 전체 YTD 수익을 곱하면 기간이 맞지 않으므로 근사 기여도도 만들지 않았다. 높은 과거 총수익만으로 현재 좋은 기회라고 결론내리지 않는다.','',
        '### 현물·선물 교체·담보 이자·총수익의 구분','',
        '- **spot/price return:** 가격 수준의 변화이며 지수별 기초 가격 정의를 확인해야 한다. 선물 지수의 “spot” 명칭을 실물 현물 바스켓 수익과 동일시하지 않는다. **excess return:** 선물 노출과 교체 효과를 담은 수익. **total return:** 선물 수익에 담보 이자 효과를 포함하는 지수 총수익. GSG NAV 총수익에는 상품 운용·비용·추적 차이가 추가된다.',
        '- 공식 표에서 전체·그룹별 total return은 확인했지만, 같은 GSCI의 spot/price return·excess return 전체 시계열은 미확보다. **실현 roll return(선물 교체 효과)과 collateral return(담보 이자)은 정량 분해하지 못했다.**']
    gold=aligned('SP_GSCI_GOLD_YTD_TOTAL_RETURN');spot=aligned('SP_GSCI_PHYSICAL_GOLD_SPOT_YTD_SPOT_RETURN')
    if gold and spot:
        lines+=['- 같은 종료일의 금 현물 기준 '+v.value(spot)+'%와 GSCI 금 선물 총수익 '+v.value(gold)+'%는 서로 다르다. 별도 지수·가격 결정 방식의 차이까지 포함하므로 두 값을 빼서 순수 roll 비용이나 담보 이자로 해석하지 않는다. '+v.refs([spot,gold])]
    dynamic=aligned('SP_GSCI_DYNAMIC_ROLL_YTD_TOTAL_RETURN');forward=aligned('SP_GSCI_3M_FORWARD_YTD_TOTAL_RETURN');light=aligned('SP_GSCI_LIGHT_ENERGY_YTD_TOTAL_RETURN')
    if dynamic and forward:
        lines+=['- 같은 기간의 GSCI Dynamic Roll '+v.value(dynamic)+'%, 3M Forward '+v.value(forward)+'%는 계약 선택/교체 방식이 투자 결과에 의미 있는 차이를 만들 수 있음을 보여준다. 바스켓·계약월·규칙이 달라 기본 GSCI와의 성과 차이를 실현 roll 수익으로 확정하지 않는다. '+v.refs([dynamic,forward])]
    if light:
        lines+=['- 같은 기간 Light Energy 총수익 '+v.value(light)+'%는 에너지 비중을 낮춘 구성의 결과가 다르다는 보조 비교다. GSG의 정확한 에너지 기여도나 앞으로의 성과 예측은 아니다. '+v.refs([light])]
    lines+=['- 현재 WTI 곡선과 실제 교체 규칙은 아래에서 별도로 확인한다. 현재 backwardation/contango를 YTD 내내 지속된 구조나 확정 수익으로 추정하지 않는다.','']
    return lines
