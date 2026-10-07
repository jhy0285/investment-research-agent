"""Evidence-gated shortlist for a broad ask, using the existing opportunity map.

This is a small method registry and draft review, not another acquisition engine.
Different asset economics remain separate. Rules choose research questions, never
expected returns, investment weights or a composite reliability score.
"""
from copy import deepcopy
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
import re
from urllib.parse import urlencode

from .models import MetricResult, InterpretationStatus, VerificationStatus
from .sources import SourceError, _time, _decode, _visible_html
from .source_pipeline import _digest, _decimal
from .research_catalog import METHODS, SCAN_ASSETS, FX, RATES, method
from .routing import Subject
from .korean_data import resolve_korean_subject

VERSION = 'evidence_shortlist_v7'
MINIMUM_VERSIONS = ('evidence_shortlist_v3','evidence_shortlist_v4','evidence_shortlist_v5','evidence_shortlist_v6',VERSION)
REPLAY_VERSIONS = ('evidence_shortlist_v1','evidence_shortlist_v2',*MINIMUM_VERSIONS)
NAMES = {'scan_valuation':'현재 가격과 예상 실적의 관계',
         'scan_momentum':'같은 거래소의 실제 가격 흐름', 'scan_community':'최근 시장 논쟁 원문'}


def validate(config):
    if (config.get('schema_version')!='opportunity-scan-v1' or config.get('method_version') not in REPLAY_VERSIONS
            or type(config.get('max_candidates')) is not int or not 2<=config['max_candidates']<=4
            or config.get('selection_purpose')!='research_priority_not_investment_ranking'
            or config.get('regional_categories')!=(['reb_sale_index','reb_volume','reb_jeonse_index'] if config.get('method_version') in MINIMUM_VERSIONS else ['reb_sale_index','reb_volume'])):
        raise SourceError('unsupported opportunity scan registry')


def universe(korean):
    """Exposure areas, not a stock-pick list. Themes/strategies overlap equities."""
    items=[METHODS[i] for i in SCAN_ASSETS if i!='KR_REALESTATE']
    if korean:
        # Resolve through the existing country/tenor/region contracts.
        from .query_understanding import Term
        items.insert(1,resolve_korean_subject(Subject('한국 3년 국채','bond','bond','KR',maturity=Term('3','years',None,'3년')),True))
        items.append(resolve_korean_subject(Subject('서울/수도권 아파트','real_estate','real_estate','KR',('서울','경기','인천')),True))
    else:
        items.append(method('KR_GOVERNMENT_3Y','한국 국고채 3년','bond',(),(),
            '원화 명목 이자와 금리 변화','중도 매도 가격 손실·물가','원화 금리 대안으로 조사할 이유가 있는가?',
            '기준 수익률과 실제 매수 조건이 다른가?',['한국 공식 금리 미연결'],'미국 국채로 대체하지 않는다.'))
        items.append(replace(METHODS['KR_REALESTATE'],id='KR_APARTMENTS_SEOUL_GYEONGGI_INCHEON',label='서울/경기/인천 아파트',
            source_ids=(),missing=('서울·경기·인천별 실거래·거래량·금융조건 미연결',)))
    items.extend([
        method('GROWTH_THEME','성장주·AI·반도체 테마','equity',('US_SPDR_GROWTH','KR_SAMSUNG_2026Q2_RESULTS',
            'COM_HN_AI_DEMAND_BULL','COM_HN_AI_VALUATION_BEAR','COM_HN_MEMORY_CYCLE_RISK'),(FX,),
            '미래 이익 성장과 그 기대에 지불하는 가격','성장 기대 미달·설비투자 회수 지연·집중',
            '실제 사업 개선이 가격에 반영된 기대를 따라가는가?','공급자 매출을 구매자의 투자수익으로 혼동했는가?',
            ['전체 테마의 이익 전망 수정·현재 주가·고객 투자회수'],'미국/한국 주식과 중복 노출이다. 한 회사의 실적을 테마 전체로 일반화하지 않는다.'),
        method('VALUE_DIVIDEND','가치주·배당 전략','strategy',('US_SPDR_VALUE','US_SPDR_DIVIDEND'),(FX,),
            '실제 이익과 배당 현금흐름·가격 재평가','싼 이유가 구조적 악화일 수 있고 배당도 줄 수 있음',
            '성장 기대를 덜 지불하는 대안이 의미 있는가?','배당 지속성과 구성 종목의 이익을 확인했는가?',
            ['배당 지속성·이익 전망 수정·세후 현금흐름'],'미국 가치/배당 지수의 예시다. 한국 전략·전체 전략의 우위를 대변하지 않는다.'),
        method('BROAD_COMMODITIES','광범위 원자재','commodity',(),(FX,),
            '현물 수급·선물 보유 비용·에너지와 산업금속의 구성','선물 교체 비용·경기둔화·구성 편중',
            '여러 원자재에서 공통된 실제 수급 변화가 있는가?','원유 관측 하나를 전체 원자재로 일반화했는가?',
            ['광범위 지수의 현재 가격·구성·금속 수급·선물곡선'],'원유와 천연가스 자료를 광범위 원자재의 사실로 대체하지 않는다.')])
    return items


def needs(methods, now, config=None):
    selected={m['id'] for m in methods}; out=[]
    for asset,block in [('US_EQUITY','spy'),('GROWTH_THEME','spyg'),('VALUE_DIVIDEND','spyv'),('VALUE_DIVIDEND','spyd')]:
        if config and config['method_version'] in MINIMUM_VERSIONS and block in ('spy','spyd'):continue
        if asset in selected:
            out.append(dict(id='NEED_SCAN_'+block.upper(),asset_id=asset,category='scan_valuation',block=block,
                label=block.upper()+' 현재 가격/실적 자료',reason='서로 같은 정의의 배수와 서로 다른 성장 기대를 구분',
                max_age_seconds=7*86400,max_selected=1))
    if 'BTC' in selected and not (config and config['method_version'] in MINIMUM_VERSIONS):
        out.append(dict(id='NEED_SCAN_BTC_MOMENTUM',asset_id='BTC',category='scan_momentum',
            label='Bitcoin 실제 가격 흐름',reason='가격 상승 자체와 실제 수요 근거를 분리',max_age_seconds=2*86400,max_selected=1))
        out.append(dict(id='NEED_BTC_COMMUNITY',asset_id='BTC',category='community',
            label='Bitcoin 현재 토론',reason='반대 주장과 현재 관심을 표본에서 관찰',max_age_seconds=21*86400,max_selected=1))
    if 'GROWTH_THEME' in selected and not (config and config['method_version'] in MINIMUM_VERSIONS):
        out.append(dict(id='NEED_SCAN_COMMUNITY',asset_id='GROWTH_THEME',category='scan_community',
            label='AI·메모리 현재 논쟁',reason='공급자 실적·고객 투자회수·가격 기대를 구분하는 주장 발견',
            max_age_seconds=21*86400,max_selected=2))
    if config and config['method_version'] in MINIMUM_VERSIONS:
        from .scan_minimum import needs as minimum_needs
        out.extend(minimum_needs(methods,config))
    if config and config['method_version'] in ('evidence_shortlist_v5','evidence_shortlist_v6',VERSION):
        for need in out:need['canonical_context']='official_statistical_or_issuer_document_with_explicit_definition'
    return out


def policy(base, methods, needs, now, config=None):
    """Reuse bounded discovery methods, request cache, robots and source promotion."""
    po=deepcopy(base); categories={n['category'] for n in needs}
    po['providers']=[p for p in po['providers'] if set(p['categories']) & categories]
    for provider in po['providers']:
        if provider['method']=='community_search':provider['max_candidates']=2
    pages={
        'spy':'state-street-spdr-sp-500-etf-trust-spy',
        'spyg':'state-street-spdr-portfolio-sp-500-growth-etf-spyg',
        'spyv':'state-street-spdr-portfolio-sp-500-value-etf-spyv',
        'spyd':'state-street-spdr-portfolio-sp-500-high-dividend-etf-spyd'}
    for block,page in pages.items():
        asset='US_EQUITY' if block=='spy' else 'GROWTH_THEME' if block=='spyg' else 'VALUE_DIVIDEND'
        if not any(n.get('block')==block for n in needs):continue
        url='https://www.ssga.com/us/en/individual/etfs/'+page
        po['providers'].append(dict(id='SCAN_'+block.upper(),publisher='State Street Investment Management',
            type='institution',canonical=True,jurisdiction='US',categories=['scan_valuation'],asset_ids=[asset],blocks=[block],
            method='reviewed_document',seed_url=url,contract='scan_ssga_v1',identity_fields={'symbol':block.upper()},
            candidate_hosts=['www.ssga.com'],access_method='public_http',policy_url=url,
            policy_note='기존 공개 발행사 페이지와 robots 경계를 유지한다. 날짜·구성 정의가 확인된 최대 세 숫자만 개인 연구용 귀속 excerpt/hash로 보존한다. 전체 보유·가격 이력·사이트 복제나 한국 판매 가능성을 추정하지 않는다.'))
    end=now.astimezone(timezone.utc).replace(hour=0,minute=0,second=0,microsecond=0)
    if config and config['method_version'] in MINIMUM_VERSIONS:
        from .scan_minimum import policy as minimum_policy
        return minimum_policy(po,methods,needs,now,config)
    url='https://api.exchange.coinbase.com/products/BTC-USD/candles?'+urlencode(
        dict(granularity=86400,start=(end-timedelta(days=3)).isoformat(),end=end.isoformat()))
    po['providers'].append(dict(id='SCAN_BTC_CLOSES',publisher='Coinbase Exchange',type='primary',canonical=True,
        jurisdiction='US exchange-specific',categories=['scan_momentum'],asset_ids=['BTC'],method='reviewed_document',
        seed_url=url,contract='scan_btc_closes_v1',identity_fields={'product':'BTC-USD'},candidate_hosts=['api.exchange.coinbase.com'],
        access_method='public_api',policy_url='https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-candles',
        policy_note='문서화된 인증 없는 API에서 최근 세 UTC 일봉만 요청한다. 완료된 마지막 두 종가·날짜·원문 hash만 보존한다. 매매체결가·전 시장 추세·장기 총수익률로 취급하지 않는다.'))
    po['providers'].append(dict(id='SCAN_HN',publisher='Hacker News / public HN API',type='community',canonical=True,
        categories=['scan_community'],asset_ids=['GROWTH_THEME'],method='community_search',
        seed_url='https://hn.algolia.com/api/v1/search_by_date?query=AI%20capex&tags=comment&hitsPerPage=30',
        query='AI capex; chronological comments; original item independently opened',
        candidate_template='https://hacker-news.firebaseio.com/v0/item/{identity}.json',candidate_hosts=['hacker-news.firebaseio.com'],
        contract='scan_hn_v1',max_candidates=2,access_method='public_api',policy_url='https://github.com/HackerNews/API',
        policy_note='기존 공개 검색·원 item API 사용. 검색 snippet은 저장·사실 채택하지 않는다. 현재 관련 발언 두 개 이하만 귀속 인용하며 개인정보·좋아요를 수집하지 않는다. 토론 표본은 시장 전체 관심 증가나 사실 검증이 아니다.'))
    if len(po['providers'])>12:raise SourceError('scan exceeds the existing provider budget')
    return po


def parse_candidate(contract,response,candidate):
    from .discovery_contracts import json_document, definition
    if contract=='scan_btc_closes_v1':
        rows=json_document(response); at=_time(candidate['document']['retrieved_at'])
        if not isinstance(rows,list) or not 2<=len(rows)<=5:raise SourceError('bounded daily candles required')
        if candidate.get('index_identity_fields',{}).get('product')!='BTC-USD':raise SourceError('wrong candle product')
        completed=[]
        for i,row in enumerate(rows):
            if not isinstance(row,list) or len(row)!=6 or type(row[0]) is not int or row[0]%86400:
                raise SourceError('invalid UTC daily candle')
            close_at=datetime.fromtimestamp(row[0],timezone.utc)+timedelta(days=1)
            if close_at<=at:
                close=_decimal(str(row[4]),'UTC daily close')
                if not close.is_finite() or close<=0:raise SourceError('invalid daily close')
                completed.append((close_at,i,close))
        completed.sort()
        if len(completed)<2 or len({r[0] for r in completed})!=len(completed):raise SourceError('missing/duplicate completed candles')
        pair=completed[-2:]
        if pair[1][0]-pair[0][0]!=timedelta(days=1):raise SourceError('daily candles are not consecutive')
        records=[dict(quote=str(rows[i][4]),locator=f'json_scalar:/{i}/4',
            definition=definition('COINBASE_BTC_USD_DAILY_CLOSE','USD_per_BTC',t.isoformat(),'USD',
                'Coinbase Exchange BTC-USD UTC daily close','unadjusted_completed_candle'),
            extraction='decimal_scalar_v1',label='Coinbase Bitcoin 완료 일봉 종가',limitations=[])
            for t,i,value in pair]
        return dict(observed_at=pair[-1][0].isoformat(),published_at=None,valid_as_of=pair[-1][0].isoformat(),
            records=records,complete=True,limitations=['한 거래소의 완료 일봉 두 개다. 장기 추세·전 시장 수익률·미래 확률은 아니다.'])
    if contract=='scan_hn_v1':
        doc=json_document(response)
        if doc.get('type')!='comment' or doc.get('dead') or doc.get('deleted') or str(doc.get('id'))!=candidate['identity']:
            raise SourceError('wrong/deleted original discussion')
        text=_visible_html(doc['text'])
        if not 0<len(text)<=1100 or not narrative_relevant(text):raise SourceError('bounded relevant original discussion required')
        at=datetime.fromtimestamp(doc['time'],timezone.utc).isoformat()
        return dict(observed_at=at,published_at=at,valid_as_of=at,complete=True,records=[dict(
            quote=text,locator='json_html:/text',definition=definition('SCAN_AI_COMMUNITY_NARRATIVE','text',at,None,
                'purpose_sampled_Hacker_News_comment','utterance_not_verified_financial_fact'),extraction=None,
            label='관측된 AI·투자회수 논쟁',limitations=['중요한 사실 주장은 검증 전이다.'])],
            limitations=['선택된 공개 발언이며 시장 대표성·관심 증가·주장의 사실성을 증명하지 않는다.'])
    text=_visible_html(_decode(response.body,response.content_type)); fields=candidate['index_identity_fields']
    symbol=fields.get('symbol')
    if symbol not in ('SPY','SPYG','SPYV','SPYD') or symbol not in text:raise SourceError('issuer product identity missing')
    dates=re.findall(r'(?:Index|Fund) Characteristics as of ([A-Z][a-z]{2} \d{2} \d{4})',text)
    if not dates or len(set(dates))!=1:raise SourceError('ambiguous issuer characteristics dates')
    day=datetime.strptime(dates[0],'%b %d %Y').replace(tzinfo=timezone.utc).isoformat()
    # Narrow, explicit prose definitions; numbers cannot be taken from snippets.
    pe=re.search(r'Price/Earnings Ratio FY1 .*?outliers are included in the calculation\. ([\d.]+)',text)
    if not pe:raise SourceError('FY1 harmonic P/E definition/value missing')
    records=[]
    def add(value,measure,unit,locator,adjustment):
        numeric=_decimal(value,'issuer characteristic')
        if numeric<=0:raise SourceError('invalid issuer characteristic')
        records.append(dict(quote=value,locator='text:'+locator,definition=definition(measure,unit,day[:10],'USD',
            symbol+' issuer portfolio characteristics',adjustment),extraction='decimal_scalar_v1',
            label=symbol+' '+measure,limitations=[]))
    add(pe[1],'SSGA_FY1_HARMONIC_PE','ratio','FY1 PE','weighted_harmonic_FY1_estimate_not_rolling_12m')
    # Preserve exact numeric occurrence with unambiguous local context. The
    # source pipeline checks exact value existence; this contract checks identity
    # and the explicit field definition before scalar transcription.
    for record in records:record['locator']='text:FY1 definition ends with '+pe[1]
    growth=re.search(r'mean 3-5 year EPS growth rate estimate\. ([\d.]+)%',text)
    if growth and symbol!='SPYD':add(growth[1],'SSGA_ESTIMATED_EPS_GROWTH','percent','estimated EPS growth','FactSet_mean_3_5_year_estimate_not_actual_growth')
    if symbol in ('SPYD','SPYV'):
        dist=re.search(r'Fund Distribution Yield .*?expressed as a percentage[^.]*\. ([\d.]+)%',text)
        if dist:add(dist[1],'SSGA_TRAILING_DISTRIBUTION_YIELD','percent','distribution yield','past_365_days_distributions_divided_by_NAV_not_guaranteed_future_yield')
    return dict(observed_at=day,published_at=None,valid_as_of=day,records=records,complete=True,
        limitations=['펀드 구성의 예상 이익 배수이며 전체 전략의 매력·미래 실적을 확인한 것은 아니다.',
            'FY1은 다음 회계연도 전망이며 rolling forward 12개월과 섞지 않는다.'])


def narrative_relevant(text):
    return bool(re.search(r'\bAI\b|\bHBM\b|memory|hyperscaler',text,re.I)
                and re.search(r'capex|revenue|profit|bubble|valuat|demand|return|cost|risk|investment',text,re.I))


def eligible(case,cutoff,*,narrative=False):
    sources={s.id:s for s in case.sources};out=[]
    for e in case.evidence:
        p=e.provenance;s=sources[e.source_id];sp=s.provenance
        if (not p or p.match_status!='matched' or p.freshness!='fresh' or not sp or sp.status!='available'
                or _time(sp.retrieved_at)>cutoff or e.interpretation.status==InterpretationStatus.REJECTED):continue
        if any(_time(t)>cutoff for t in (sp.published_at,sp.observed_at,sp.valid_as_of) if t):continue
        if (e.kind=='observed_narrative')!=narrative:continue
        if not narrative and e.verification!=VerificationStatus.SUPPORTED:continue
        out.append(e)
    return out


def calculations(case,cutoff,require_dates=False):
    rows=[e for e in eligible(case,cutoff) if e.value is not None];out=[]
    for e in rows:
        if e.provenance.definition['measure']=='SSGA_FY1_HARMONIC_PE' and e.value>0:
            with localcontext() as ctx:
                ctx.prec=50;ctx.rounding=ROUND_HALF_EVEN;value=Decimal(100)/e.value
            out.append(MetricResult('SCAN_EY_'+e.id,'발행사 FY1 배수의 역수',value,'percent','scan_inverse_fy1_pe_v1',(e.id,),e.asset_ids,
                ('다음 회계연도 예상 이익 기준 배수의 역수다. 실제 배당·기대수익·ERP가 아니다.',)))
    prices=sorted([e for e in rows if e.provenance.definition['measure']=='COINBASE_BTC_USD_DAILY_CLOSE'],key=lambda e:e.period)
    if require_dates:
        from .source_pipeline import dated_evidence
        prices=[e for e in prices if dated_evidence(e)]
    if (len(prices)==2 and _time(prices[1].period)-_time(prices[0].period)==timedelta(days=1)
            and prices[0].currency==prices[1].currency=='USD'
            and prices[0].provenance.definition['scope']==prices[1].provenance.definition['scope']
            and prices[0].provenance.definition['adjustment']==prices[1].provenance.definition['adjustment']=='unadjusted_completed_candle'):
        a,b=prices
        with localcontext() as ctx:
            ctx.prec=50;ctx.rounding=ROUND_HALF_EVEN;value=(b.value/a.value-1)*100
        out.append(MetricResult('SCAN_BTC_PRICE_CHANGE','Bitcoin 완료 일봉 가격 변화',value,'percent','scan_consecutive_utc_close_change_v1',(a.id,b.id),('BTC',),
            ('Coinbase 한 거래소의 연속 완료 일봉 종가 변화다. 한 날의 움직임은 장기 추세·총수익률·투자 매력이 아니다.',)))
    return tuple(out)


def _assess(run):
    """Observable comparisons select conditional questions; no model truth vote."""
    facts=eligible(run.case,run.cutoff); by_id={e.id:e for e in facts}
    legacy=run.input['scan']['method_version']=='evidence_shortlist_v1'
    narratives=eligible(run.case,run.cutoff,narrative=True)
    methods=run.input['methods']; assets={m['id'] for m in methods}
    def observations(asset,measure=None):
        return [e for e in facts if asset in e.asset_ids and (measure is None or e.provenance.definition['measure']==measure)]
    def latest(asset,measure):
        rows=[e for e in observations(asset,measure) if e.value is not None]
        return max(rows,key=lambda e:((e.period or '',e.id) if legacy else
                   (str(e.observed_at or ''),e.period or '',e.id))) if rows else None
    def text_record(asset,needle):
        return next((e for e in observations(asset) if needle in e.text),None)
    def refs(*items):return list(dict.fromkeys(e.id for e in items if e is not None))
    # FactSet's explicitly transcribed facts are already checked by the existing
    # Deep Dive quote engine. Keep their source evidence, date and definition.
    quoted={f['id']:f for f in run.deep.facts if f['status']=='available' and f['source_evidence_id'] in by_id} if run.deep else {}
    def q(identifier):return quoted.get(identifier)
    def qvalue(identifier):return Decimal(q(identifier)['value']) if q(identifier) else None
    rows=[]
    for m in methods:
        current=observations(m['id']); ns=[e for e in narratives if m['id'] in e.asset_ids]
        rows.append(dict(asset_id=m['id'],name=m['label'],family=m['family'],status='insufficient',
            why_now='핵심 가격·실적·수급 중 현재 판단에 필요한 자료가 부족하다.',
            evidence_ids=[],context_ids=[e.id for e in current],narrative_ids=[e.id for e in ns],
            risk=m['downside'],unknowns=list(m['missing']),strengthen=m['bull_question'],invalidate=m['bear_question'],
            confidence='판단 자료 부족',action='데이터 부족으로 판단 보류',
            price_context='현재 가격의 매력을 확정할 비교 자료가 부족하다.',
            momentum='연속 가격 관측 미확보: 상승 추세·과열을 단정하지 않는다.',
            popularity='시장 전체 인지도·보유자 수를 측정하지 않았다.',
            attention=('현재 공개 토론 표본이 있다. 관심 증가율·시장 대표성은 미확인.' if ns else '현재 관련 토론 표본 미확보. 관심이 없다는 뜻은 아니다.'),
            economics=m['economics'],liquidity='상품별 거래비용·매도 가능 조건 확인 필요',
            timing='사용자 자금 사용 시점 미확인',macro_sensitivity='자산 고유 경로만 비교',
            opportunity_cost='원화 현금·국채를 포기할 이유와 해당 자산의 추가 위험을 비교한다.',
            expectation_reality='가격에 반영된 기대와 실제 경제성을 아직 대조하지 못했다.',
            decision_rule='core_evidence_unavailable',interpretation_status='draft',overlap_group=
                'equities' if m['family'] in ('equity','strategy') else m['family']))
    index={r['asset_id']:r for r in rows}
    def setrow(asset,status,why,evidence,rule,**kwargs):
        if asset not in index:return
        r=index[asset];r.update(status=status,why_now=why,evidence_ids=list(dict.fromkeys(evidence)),decision_rule=rule,**kwargs)
        if evidence and 'confidence' not in kwargs:r['confidence']='원문 확인; 투자 해석은 조건부 초안'
    kr=latest('KR_GOVERNMENT_3Y','KR_GOVERNMENT_NOMINAL_3Y')
    us2=latest('SHORT_BOND',RATES[0]);us10=latest('LONG_BOND',RATES[1])
    if kr and kr.value>0:
        setrow('KR_GOVERNMENT_3Y','research_candidate',
            '원화 국채의 실제 금리가 확인됐다. 환율 위험 없이 받을 이자의 기준을 먼저 알면 위험자산에 필요한 추가 보상을 비교하기 쉽다.',
            refs(kr),'positive_current_KRW_starting_yield',action='먼저 다른 후보와 비교',
            price_context='국고채 기준 금리이며 개별 채권의 실제 매수 수익률과 다르다.',
            strengthen='자금 사용 시점과 만기가 맞고, 비용 차감 후 실제 매수 수익률이 확인될 때.',
            invalidate='만기 전 큰 지출이 필요하거나 금리가 더 올라 중도 매도 손실이 커질 때.',
            expectation_reality='금리 하락을 예측할 필요 없이 현재 이자를 대안의 기준으로 삼을 수 있다.',
            macro_sensitivity='물가·한국 금리 상승은 중도 매도 가격에 불리하다.',liquidity='개별 채권/ETF별 호가·매도 조건은 별도 확인')
    for asset,e in [('SHORT_BOND',us2),('LONG_BOND',us10)]:
        if e:
            setrow(asset,'neutral','현재 달러 기준 국채 금리는 비교 가능한 출발점이다. 원화 수익은 환율과 중도 매도 가격에 따라 달라진다.',
                refs(e),'current_USD_yield_alternative',action='한국 국채와 조건을 맞춰 비교',
                price_context=e.provenance.definition['measure']+' 기준 금리; 특정 채권 실현수익 아님',
                strengthen='달러 자금 목적·만기·금리 위험이 맞고 실제 상품 수익률이 확인될 때.',
                invalidate='원화 지출 시점이 가깝거나 달러 약세·금리 상승 손실이 부담될 때.')
    setrow('CASH','normal_alternative','현금은 급한 지출과 판단 유보를 위한 정상적인 대안이다. 다른 자산의 자료 부족이 현금의 우월성을 증명하지는 않는다.',
        [],'cash_preserves_option_not_missing_data_alpha',confidence='역할은 명확; 개인 금리·자금수요 미확인',
        action='비상자금·큰 지출에 필요한 금액부터 확인',price_context='한국 예금/MMF의 실제 세후 금리 미확보; 미국 금리로 대체하지 않는다.',
        risk='물가로 구매력이 줄고, 다른 자산의 상승을 놓칠 수 있다.',strengthen='단기 지출이나 부채 상환 필요가 확인될 때.',
        invalidate='장기 자금인데 유리한 대안과 비교 없이 계속 현금만 보유할 때.')
    pe=qvalue('F_SP_FORWARD_12M_PE');rev=qvalue('F_Q3_EPS_REVISION');avg=qvalue('F_SP_PE_AVG5')
    if pe is not None and rev is not None:
        ids=[q(i)['source_evidence_id'] for i in ('F_SP_FORWARD_12M_PE','F_Q3_EPS_REVISION','F_SP_PE_AVG5') if q(i)]
        improving=rev>0; affordable=avg is not None and pe<avg
        why=('이익 전망이 상향됐고 예상 이익 대비 가격도 같은 정의의 과거 평균보다 낮다. 예상한 이익이 실제로 나올지 확인할 연구 가치가 있다.'
             if improving and affordable else '현재 가격과 이익 전망 수정이 함께 확인됐다. 가격이 요구하는 이익과 실제 실적의 차이를 확인해야 한다.')
        setrow('US_EQUITY','research_candidate' if improving else 'conditional_watch',why,ids,
            'positive_revision_with_comparable_valuation' if improving else 'nonpositive_revision_requires_delivery',
            action='예상 이익의 현실성부터 깊게 조사',
            price_context='FactSet의 향후 열두 달 예상 이익 배수. 발행사 FY1(다음 회계연도) 배수와 정의가 다르다.',
            strengthen='이익 전망 상향이 실제 매출·현금흐름으로 이어지고 소수 회사에만 의존하지 않을 때.',
            invalidate='이익 전망이 내려가거나 이익 증가가 일회성 항목에 치우칠 때.',
            expectation_reality='예상 이익은 개선됐다. 개선 기대가 현재 가격에 이미 반영됐는지와 실적 달성은 별개다.',
            macro_sensitivity='미국 금리·이익 기대·원/달러 환율에 민감',risk='높은 이익 기대 미달·지수 내 대형주 집중·주가 하락·환율')
        index['US_EQUITY']['overheat_check']=dict(
            status='expectation_pressure' if avg is not None and pe>=avg else 'not_established',
            evidence_ids=ids,reason='같은 정의의 과거 평균 이상 배수라면 좋은 실적이 이미 가격에 반영됐을 가능성을 더 엄격히 확인한다. 평균 이하도 저평가의 증명은 아니다.')
    memory=text_record('KR_EQUITY','industry-wide upward trend of prices')
    device=text_record('KR_EQUITY','elevated component cost pressures')
    if memory and device:
        setrow('KR_EQUITY','research_candidate',
            '삼성 공식 자료에서 메모리 가격·AI 수요의 수혜와 기기 부문의 비용 부담이 함께 확인됐다. 같은 산업 호황도 기업별 이익에 다르게 전달된다.',
            refs(memory,device),'observed_business_improvement_and_counterevidence',name='한국 반도체: 실적 개선과 현재 가격의 차이',
            action='기업 실적과 현재 가격을 비교 연구',price_context='사업 개선은 확인됐지만 이 Scan에는 동일 기준 현재 주가·이익 배수 비교가 없다.',
            strengthen='메모리 이익 개선이 현금흐름으로 이어지고 현재 주가가 과도한 성장을 요구하지 않을 때.',
            invalidate='공급 확대로 메모리 가격이 꺾이거나 이익 개선보다 주가 기대가 앞서갈 때.',
            risk='메모리 공급 확대·가격 반전·사업부별 비용 압력·이미 가격에 반영된 호황',
            expectation_reality='AI 공급자 실적 개선이 확인돼도 한국 주식 전체나 모든 AI 고객의 투자회수를 뜻하지 않는다.',
            macro_sensitivity='메모리 가격·설비투자·수출 수요; 미국 자산과 같은 직접 USD/KRW 수익 계산을 적용하지 않음')
    growth=latest('GROWTH_THEME','SSGA_FY1_HARMONIC_PE')
    value=next((e for e in observations('VALUE_DIVIDEND','SSGA_FY1_HARMONIC_PE')
                if e.provenance.definition['scope'].startswith('SPYV ') and e.value is not None),None)
    div=latest('VALUE_DIVIDEND','SSGA_TRAILING_DISTRIBUTION_YIELD')
    if growth:
        setrow('GROWTH_THEME','conditional_watch','성장주가 지불하는 예상 이익 배수를 확인했다. 실제 성장과 설비투자 회수가 기대를 따라가는지 검증해야 한다.',
            refs(growth),'growth_price_requires_business_delivery',action='미국 주식·한국 반도체 연구에 겹치는 노출로 함께 확인',
            price_context='성장주 지수 예시의 FY1 배수; 모든 AI 기업의 배수 아님',
            strengthen='예상 성장과 고객의 실제 투자회수가 함께 확인될 때.',invalidate='고객의 수익 창출보다 투자비와 비용이 계속 앞설 때.')
    if growth and value and growth.period==value.period and value.value<growth.value and div:
        setrow('VALUE_DIVIDEND','research_candidate','같은 날·같은 발행사 정의에서 가치주가 성장주보다 낮은 예상 이익 배수에 거래된다. 배당 현금흐름도 있는 대안이므로, 낮은 가격의 이유와 배당 지속성을 비교할 가치가 있다.',
            refs(value,div),'lower_same_definition_value_PE_with_distribution_context',
            context_ids=list(dict.fromkeys(index['VALUE_DIVIDEND']['context_ids']+[growth.id])),action='성장주와 가격·배당 지속성을 비교',
            strengthen='이익이 구조적으로 감소하지 않고 배당을 현금흐름이 뒷받침할 때.',
            invalidate='낮은 배수의 원인이 장기 이익 감소이거나 배당 삭감·특정 업종 편중일 때.',
            price_context='가치주 배수와 배당 전략의 분배율은 서로 다른 포트폴리오다. 하나의 상품처럼 합치지 않는다.',
            expectation_reality='낮은 기대를 지불하는 대안이지만 낮은 배수가 저평가를 증명하지는 않는다.')
        if run.input['scan']['method_version'] in ('evidence_shortlist_v6',VERSION) and value.source_id==div.source_id:
            index['VALUE_DIVIDEND']['price_context']='SPYV 가치주 예시의 이익 배수와 과거 분배율을 함께 확인했다. SPYG 성장주 예시와 같은 날짜·같은 FY1 정의의 배수를 비교하며, 배당 전문 전략 전체를 대변하지 않는다.'
    elif value or div:
        setrow('VALUE_DIVIDEND','conditional_watch','현재 가격/배당 자료 일부를 확인했다. 같은 정의의 성장주 대안과 배당 지속성을 맞춰봐야 한다.',
            refs(value,div),'partial_style_comparison',action='이익 감소·배당 지속성 확인까지 관찰')
    btc=latest('BTC','COINBASE_BTC_USD_LAST_TRADE')
    flow=latest('BTC','US_SPOT_BTC_ETF_DAILY_NET_FLOW')
    price_change=next((m for m in run.result.metrics if m.id=='SCAN_BTC_PRICE_CHANGE'),None)
    complete=flow is not None and flow.provenance.definition['adjustment']=='complete_row_provider_reported_not_issuer_confirmed'
    if btc:
        status='research_candidate' if complete and flow.value>0 else 'conditional_watch'
        setrow('BTC',status,'거래소 가격과 ETF 수요를 함께 확인한다. 완성된 순유입과 가격 움직임이 같이 이어지는지 검증할 가치가 있다.' if complete else
            '현재 가격은 확인됐다. ETF 흐름이 미완성 또는 미확보이면 강한 수요 유입을 단정하지 않고 확인을 기다린다.',
            refs(btc,*([flow] if complete else [])),'complete_positive_flow_and_market' if complete and flow.value>0 else 'BTC_price_without_complete_positive_flow',
            action='완성된 자금흐름·반대 논리 확인까지 조건부 관찰' if status!='research_candidate' else '수요 지속성과 가격 기대를 깊게 조사',
            strengthen='완성된 순유입이 반복되고 실제 네트워크·유동성 근거와 가격이 함께 개선될 때.',
            invalidate='ETF 수요가 돌아서거나 거래소 신뢰·레버리지 문제가 커질 때.',
            price_context='한 거래소 최근 체결 가격. 이익 배수가 없는 자산이라 가격만으로 싸다고 판단하지 않는다.')
    if price_change:
        index['BTC']['momentum']='완료된 두 UTC 일봉의 실제 가격 변화가 있다. 상승은 관심의 단서이고 기대 과잉의 가능성도 함께 확인한다.' if price_change.value>0 else '완료된 두 UTC 일봉에서 상승하지 않았다. 한 날의 움직임만으로 장기 추세를 정하지 않는다.'
        index['BTC']['momentum_metric_id']=price_change.id
    storage=text_record('NATGAS','5% above the previous five-year average')
    production=text_record('NATGAS','production continues to grow')
    if storage and production:
        setrow('NATGAS','weak_case','공식 전망은 겨울 전 재고가 평년보다 많고 생산도 증가하는 방향이다. 단순한 겨울 수요·재고 부족 주장만으로 먼저 볼 강한 이유는 약하다.',
            refs(storage,production),'forecast_inventory_surplus_and_supply_growth_counter_shortage',action='실제 재고·날씨·만기별 선물 가격이 달라질 때 재검토',
            confidence='공식 전망 확인; 실제 미래 수급·가격 매력은 미확인',
            strengthen='실제 재고가 전망보다 부족하고 그 변화가 투자상품 가격에 덜 반영됐을 때.',
            invalidate='생산 증가와 평년 이상 재고 전망이 실제로 이어질 때.',
            price_context='선물곡선(미래 만기별 가격)·현재 상품 가격이 없어 강한 매수 기회를 확정하지 않는다.',
            expectation_reality='공식 전망은 관측 사실과 다르다. 재고 부족 내러티브와 비교할 반대 근거로만 쓴다.')
    shortage=text_record('ENERGY','production shut-ins averaged')
    recovery=text_record('ENERGY','we forecast oil prices will begin to fall')
    if shortage and recovery:
        setrow('ENERGY','conditional_watch','공급 차질과 향후 공급 회복 전망이 함께 존재한다. 부족의 지속 기간이 중요하므로 가격과 실제 복구 진행을 확인해야 한다.',
            refs(shortage,recovery),'observed_supply_disruption_vs_forecast_recovery',action='공급 복구와 현재 선물 가격 확인까지 관찰',
            strengthen='공급 복구가 지연되고 현재 가격에 그 지연이 충분히 반영되지 않을 때.',
            invalidate='공급 정상화가 현실화되거나 비싼 가격 때문에 수요가 약해질 때.',
            expectation_reality='관측된 생산 차질과 미래 회복 전망을 같은 사실로 취급하지 않는다.')
    for asset in ('ETH','GOLD'):
        if observations(asset):
            setrow(asset,'insufficient','구조·금리 맥락 일부는 확인했지만 현재 가격과 자산 고유 수요를 함께 판단할 핵심 자료가 부족하다.',
                [],'asset_specific_price_demand_gap',action='가격·고유 수요 근거부터 보완')
    region='KR_APARTMENTS_SEOUL_GYEONGGI_INCHEON'
    regionfacts=observations(region) if legacy else [e for e in observations(region) if e.view!='macro']
    if regionfacts:
        available_regions=[]
        if not legacy and run.discovery:
            nmap={n['id']:n for n in run.discovery['needs'] if n['asset_id']==region}
            available_regions=list(dict.fromkeys(nmap[c['need_id']]['region'] for c in run.discovery['candidates']
                if c['need_id'] in nmap and c['status']=='selected' and set(c['evidence_ids']) & {e.id for e in regionfacts}))
        setrow(region,'conditional_watch','서울·경기·인천을 나눈 실제 통계가 있다. 지역별 가격과 거래 회복이 같은 방향인지, 금융비용을 감당하는지 확인해야 한다.',
            [e.id for e in regionfacts],'regional_statistics_not_national_proxy',action='지역·예산·대출·전세 조건을 지정한 뒤 깊게 조사',
            price_context='지역 통계는 특정 아파트의 실제 거래가격·기대 임대수익과 다르다.',
            strengthen='관심 지역 거래가 충분하고 전세·현금흐름·실제 대출비용을 함께 확인할 때.',
            invalidate='거래가 줄거나 대출비용·입주 공급으로 순현금흐름이 악화될 때.',
            risk='지역 차이·낮은 거래 빈도·대출 부담·공급 시차·큰 자금 묶임')
        if not legacy:
            missing_regions=[r for r in ('서울','경기','인천') if r not in available_regions]
            index[region].update(available_regions=available_regions,unavailable_regions=missing_regions,
                why_now='확인된 지역 통계: '+('·'.join(available_regions) or '없음')+'. '+
                    ('미확보 지역: '+'·'.join(missing_regions)+'. ' if missing_regions else '')+
                    '가격과 거래 회복·금융비용을 지역별로 따로 확인해야 한다. 다른 지역으로 대체하지 않는다.')
    # Deterministic question priority, not investment return ranking: first
    # establish a KRW opportunity-cost anchor, then investigate delivery gaps,
    # then test an alternative with different expectations. No total-order
    # claim about expected profits is made.
    order=['KR_GOVERNMENT_3Y','US_EQUITY','KR_EQUITY','VALUE_DIVIDEND','BTC']
    chosen=[index[a] for a in order if a in index and index[a]['status']=='research_candidate']
    limit=run.input['scan']['max_candidates']
    for r in chosen[limit:]:r.update(status='conditional_watch',action='우선 후보 조사 후 추가 검토')
    candidates=chosen[:limit]
    for i,r in enumerate(candidates,1):r['reference_number']=i
    # Check every factual reason against actual promoted evidence, never index
    # IDs. Narrative IDs remain utterances; observations do not certify ROI.
    for r in rows:
        if not set(r['evidence_ids'])<=set(by_id):raise SourceError('scan reason lacks current factual evidence')
    narrative_checks=[]
    for e in narratives:
        related=[f for f in run.findings if f['status']=='available_draft' and set(f['asset_ids']) & set(e.asset_ids)]
        context=list(dict.fromkeys(ref for f in related for ref in f['evidence_ids'] if ref in by_id))
        narrative_checks.append(dict(evidence_id=e.id,text=e.text,verification='unverified',
            context_ids=context,reason='관련 원자료를 연결했지만 발언의 경제적 주장·고객 투자회수·가격 목표를 검증 완료로 승격하지 않는다.'))
    return dict(schema_version='opportunity-shortlist-v1',method_version=run.input['scan']['method_version'],
        purpose='research_priority_not_investment_ranking',as_of=run.cutoff.isoformat(),
        original_question=run.input['question'],universe=rows,candidates=[r['asset_id'] for r in candidates],
        priority_reason='원화 이자 대안을 먼저 정하고 실적과 가격 기대의 차이를 검증한 뒤 다른 전략을 비교하는 조사 순서다. 서로 다른 자산의 미래 수익률 순위가 아니다.',
        momentum_role='상승/하락은 보조 정보이며 단독 선정·배제 조건이 아니다.',
        popularity_role='인지도·거래 접근성은 보조 정보다. 유명하다는 이유만으로 선택·배제하지 않는다.',
        attention_role='토론은 주장 발견용이다. 비교 가능한 이전 표본 없이 관심 증가를 주장하지 않는다.',
        narrative_checks=narrative_checks,personalization='보유자산·부채·투자기간·큰 지출이 미확인이라 비중이나 개인 적절성을 확정하지 않는다.',
        comparison_axes=['수익의 원천','현재 가격/금리와 정의','손실 경로','변화의 계기','자금 사용 시점','사고팔기 쉬움',
            '금리·경기·환율 민감도','핵심 불확실성','근거의 최신성과 범위','대신 포기하는 대안'],
        candidate_cap=limit,selection_status='shortlist' if candidates else 'insufficient_for_shortlist')


def assess(run):
    if run.input['scan']['method_version'] in MINIMUM_VERSIONS:
        from .scan_coverage import assess as assess_coverage
        return assess_coverage(run,_assess(run))
    return _assess(run)


def review(base,assessment):
    """Project the draft into the existing OpportunityReview/ref-status gates."""
    data=deepcopy(base);rows={r['asset_id']:r for r in assessment['universe']}
    def st(text,ids):return dict(text=text,evidence_ids=ids)
    for row in data['rows']:
        r=rows[row['asset_id']];refs=r['evidence_ids']
        row['priority']='candidate' if r['status']=='research_candidate' else 'defer' if r['status']=='weak_case' else 'insufficient' if r['status']=='insufficient' else 'monitor'
        row['priority_reason']=st(r['why_now'],refs);row['negative']=st(r['risk'],[])
        row['recheck']=st(r['invalidate'],[])
        if row['priority']=='candidate':
            row['candidate']=dict(why_now=st(r['why_now'],refs),changed=st(r['expectation_reality'],refs),
                interesting=st('현재 가격을 정당화할 조건을 다음 조사에서 검증한다.',refs),
                counterargument=st(r['risk'],[]),confirm=[r['strengthen']])
    if assessment['candidates']:
        data['next_research']=dict(asset_id=assessment['candidates'][0],title='선정 후보의 대안 비교',question='현재 이자 대안과 추가 위험을 조건에 맞춰 비교한다.')
    return data


REFERENCE_VERSION='saved_shortlist_reference_v1'


def resolve_reference(question,previous):
    """An explicit saved-run reference; do not infer a global 'last' portfolio.

    The existing router receives concrete subjects. Old evidence is not carried
    forward as current; the subsequent independent ask acquires anew.
    """
    if not previous.input.get('scan'):raise SourceError('reference run has no opportunity shortlist')
    a=assess(previous);numbers=[int(n) for n in re.findall(r'(?<!\d)(\d+)\s*(?:위|번(?:\s*후보)?)',question)]
    if not numbers:raise SourceError('saved-run reference requires an explicit candidate number')
    if len(numbers)!=len(set(numbers)) or any(n<1 or n>len(a['candidates']) for n in numbers):
        raise SourceError('requested candidate number does not exist in the saved shortlist')
    labels={'KR_GOVERNMENT_3Y':'한국 3년 국채','US_EQUITY':'S&P500','KR_EQUITY':'한국 반도체',
            'VALUE_DIVIDEND':'가치주와 배당 투자','BTC':'BTC','ETH':'ETH','GOLD':'금','ENERGY':'원유','NATGAS':'천연가스',
            'GROWTH_THEME':'성장주','BROAD_COMMODITIES':'광범위 원자재',
            'KR_APARTMENTS_SEOUL_GYEONGGI_INCHEON':'서울/수도권 아파트','CASH':'현금',
            'SHORT_BOND':'미국 단기 국채','LONG_BOND':'미국 장기 국채'}
    ids=[a['candidates'][n-1] for n in numbers]
    # Expand only the reference. Preserve the user's purpose, time horizon,
    # constraints and requested action for the unchanged query understanding.
    resolved=re.sub(r'(?<!\d)(\d+)\s*(?:위|번(?:\s*후보)?)',
                    lambda match:labels[a['candidates'][int(match[1])-1]],question)
    return dict(method_version=REFERENCE_VERSION,original_question=question,resolved_question=resolved,
        candidate_numbers=numbers,subject_ids=ids,source_run_id=previous.result.run_id,
        shortlist_sha256=_digest(a),source_request_sha256=_digest(previous.input),
        evidence_rule='saved_selection_only; acquire fresh evidence for the independent follow-up')
