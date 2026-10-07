"""Bounded minimum Scan inputs, using existing discovery and macro collectors.

These are reviewed public document contracts, not a new web research engine.
All financial interpretations live in scan_coverage, separately from extraction.
"""
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import calendar
import re
from urllib.parse import urlencode, urlsplit

from .sources import SourceError, SourceSpec, _decode, _time, _visible_html
from .source_pipeline import _decimal
from .discovery_contracts import definition, html_records, json_document

VERSION = 'minimum_opportunity_evidence_v1'
NAMES = {'scan_crypto': '암호자산 가격 흐름과 거래 유동성',
         'scan_gold': '금 기준가격과 동일 기준 과거 흐름',
         'scan_energy': '공식 현물가격과 실제 재고',
         'scan_real_rate': '현재 실질 국채금리',
         'scan_gas_context': '실제 생산·수출·계절 재고',
         'scan_weather': '공식 기온 전망과 수요의 불확실성',
         'scan_gold_demand': '금 ETF 실제 실물 보유량',
         'scan_eth_flow': 'ETH 고유 ETF 일별 흐름',
         'scan_broad': '광범위 원자재 상품 가격·구성'}


def needs(methods,config=None):
    ids={m['id'] for m in methods};out=[]
    for asset,block,category,age in [
        ('BTC','btc','scan_crypto',2),('ETH','eth','scan_crypto',2),
        ('GOLD','gold','scan_gold',10),('GOLD','real','scan_real_rate',10),
        ('ENERGY','oil_price','scan_energy',14),('ENERGY','oil_stock','scan_energy',14),
        ('NATGAS','gas_price','scan_energy',14),('NATGAS','gas_stock','scan_energy',14)]:
        if asset in ids:out.append(dict(id='NEED_MIN_'+block.upper(),asset_id=asset,block=block,
            category=category,label=asset+' '+NAMES[category],reason='자료의 양과 투자 매력을 분리할 최소 관측',
            max_age_seconds=age*86400,max_selected=1))
    if config and config['method_version']=='evidence_shortlist_v7':
        for asset,block,category,age in [
            ('NATGAS','gas_production','scan_gas_context',100),('NATGAS','gas_lng','scan_gas_context',100),
            ('NATGAS','gas_reference_a','scan_gas_context',14),('NATGAS','gas_reference_b','scan_gas_context',14),
            ('NATGAS','weather_6_10','scan_weather',5),('NATGAS','weather_8_14','scan_weather',5),
            ('GOLD','iau','scan_gold_demand',7),('ETH','eth_flow_recent','scan_eth_flow',7),
            ('ETH','eth_flow_prior','scan_eth_flow',7),('BROAD_COMMODITIES','gsg','scan_broad',7)]:
            if asset in ids:out.append(dict(id='NEED_MIN_'+block.upper(),asset_id=asset,block=block,
                category=category,label=asset+' '+NAMES[category],reason='네 부족 영역의 검토된 최소 원자료; coverage는 매력 점수가 아니다.',
                max_age_seconds=age*86400,max_selected=1))
    return out


def policy(base, methods, all_needs, now,config=None):
    """Share reviewed endpoints; twelve providers, 32 or scoped 48 requests."""
    po=deepcopy(base)
    po['providers']=[p for p in po['providers'] if p['method'] not in ('community_search','access_probe')
        and (p['method']!='market_directory' or any(n['category']=='market_state' for n in all_needs))]
    po['deferred_providers']=[dict(id='LIVE_COMMUNITY',reason='이번 최소 coverage 예산은 가격·수급·지역 원자료에 우선 사용. 현재 고정 발언은 freshness 검사; 비교 가능한 관심 표본 없음.')]
    for p in po['providers']:
        if p['method']=='publisher_links':p['max_candidates']=1
    def provider(identifier,publisher,kind,categories,assets,url,contract,fields=None,documents=None):
        p=dict(id=identifier,publisher=publisher,type=kind,canonical=True,jurisdiction='source_specific',
            categories=categories,asset_ids=assets,method='reviewed_document',seed_url=url,contract=contract,
            identity_fields=fields or {},candidate_hosts=[urlsplit(url).hostname],access_method='public_http',policy_url=url,
            policy_note='검토한 공개 원문에서 날짜·단위·대상을 확인한 최대 세 필드와 hash만 개인 연구용 귀속 excerpt로 보존. 전체 데이터 재배포·접근 제한 우회·외부 지시 실행 없음.')
        if documents:p['documents']=documents
        return p
    end=now.astimezone(timezone.utc).replace(hour=0,minute=0,second=0,microsecond=0)
    documents={}
    for asset,product in [('BTC','BTC-USD'),('ETH','ETH-USD')]:
        url='https://api.exchange.coinbase.com/products/'+product+'/candles?'+urlencode(dict(
            granularity=86400,start=(end-timedelta(days=8)).isoformat(),end=end.isoformat()))
        documents[asset.lower()]=dict(seed_url=url,contract='minimum_crypto_v1',identity_fields={'product':product})
    p=provider('MIN_CRYPTO','Coinbase Exchange','primary',['scan_crypto'],['BTC','ETH'],
        documents['btc']['seed_url'],'minimum_crypto_v1',documents=documents)
    p.update(access_method='public_api',policy_url='https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-candles')
    po['providers'].append(p)
    po['providers'].append(provider('MIN_GOLD','State Street Investment Management','institution',['scan_gold'],['GOLD'],
        'https://www.ssga.com/us/en/individual/etfs/spdr-gold-shares-gld','minimum_gold_v1',{'symbol':'GLD'}))
    po['providers'].append(provider('MIN_REAL_RATE','Board of Governors of the Federal Reserve System','primary',
        ['scan_real_rate'],['GOLD'],'https://www.federalreserve.gov/releases/h15/','minimum_real_rate_v1'))
    docs={block:dict(seed_url=url,contract=contract,identity_fields={'block':block}) for block,url,contract in [
        ('oil_price','https://www.eia.gov/dnav/pet/hist/rwtcd.htm','minimum_spot_v1'),
        ('gas_price','https://www.eia.gov/dnav/ng/hist/rngwhhdD.htm','minimum_spot_v1'),
        ('oil_stock','https://www.eia.gov/dnav/pet/pet_stoc_wstk_dcu_nus_w.htm','minimum_stock_v1'),
        ('gas_stock','https://www.eia.gov/dnav/ng/ng_stor_wkly_s1_w.htm','minimum_stock_v1')]}
    extended=config and config['method_version']=='evidence_shortlist_v7'
    if extended:
        for block,url,contract in [
            ('gas_production','https://www.eia.gov/dnav/ng/hist/n9070us2m.htm','minimum_monthly_gas_v2'),
            ('gas_lng','https://www.eia.gov/dnav/ng/hist/n9133us2m.htm','minimum_monthly_gas_v2'),
            ('gas_reference_a','https://www.eia.gov/dnav/ng/hist/nw2_epg0_swo_r48_bcfw.htm','minimum_gas_reference_v2'),
            ('gas_reference_b','https://www.eia.gov/dnav/ng/hist/nw2_epg0_swo_r48_bcfw.htm','minimum_gas_reference_v2')]:
            docs[block]=dict(seed_url=url,contract=contract,identity_fields={'block':block})
    po['providers'].append(provider('MIN_EIA','U.S. Energy Information Administration','primary',['scan_energy'],['ENERGY','NATGAS'],
        docs['oil_price']['seed_url'],'minimum_spot_v1',documents=docs))
    if extended:
        po['providers'][-1]['categories'].append('scan_gas_context')
        weather='https://www.cpc.ncep.noaa.gov/products/predictions/610day/fxus06.html'
        po['providers'].append(provider('MIN_CPC','NOAA Climate Prediction Center','primary',['scan_weather'],['NATGAS'],
            weather,'minimum_weather_v2',documents={block:dict(seed_url=weather,contract='minimum_weather_v2',identity_fields={'block':block})
                for block in ('weather_6_10','weather_8_14')}))
        iau='https://www.ishares.com/us/products/239561/ishares-gold-trust-fund'
        gsg='https://www.ishares.com/us/products/239757/ishares-sp-gsci-commodityindexed-trust-fund'
        po['providers'].append(provider('MIN_ISHARES','BlackRock iShares','institution',['scan_gold_demand','scan_broad'],['GOLD','BROAD_COMMODITIES'],
            iau,'minimum_iau_v2',documents={block:dict(seed_url=url,contract=contract,identity_fields={'block':block}) for block,url,contract in [
                ('iau',iau,'minimum_iau_v2'),('gsg',gsg,'minimum_gsg_v2')]}))
        # The same publisher directory discovers Ethereum links, not a BTC proxy.
        for p in po['providers']:
            if p['method']=='publisher_links':
                p.update(asset_ids=['BTC','ETH'],categories=['etf_flows','scan_eth_flow'],max_candidates=1)
                p['eth_contract']='minimum_eth_flow_v2'
                p['policy_note']='기존 BTC 최신 행과 별도 ETH 최근 오 보고 거래일만 귀속 excerpt로 보존. 발행자 목록에서 대상 링크를 찾고 원문 날짜·단위·열·합계를 검증한다. 자동 표의 오류 가능성·원발행사 교차 확인 미완료를 명시하며 전체 표 보존/접근 제한 우회 없음.'
        # Reuse the reviewed document map for three pages of one publisher.
        # This leaves the existing twelve-provider boundary intact even when
        # the user explicitly combines the Scan with a Bitcoin Deep Dive.
        same=[p for p in po['providers'] if p['id'] in ('SCAN_SPYG','SCAN_SPYV','MIN_GOLD')]
        ssga_docs={('gold' if p['id']=='MIN_GOLD' else p['id'].removeprefix('SCAN_').lower()):
            dict(seed_url=p['seed_url'],contract='minimum_gold_v1' if p['id']=='MIN_GOLD' else 'minimum_ssga_v2',identity_fields=p['identity_fields']) for p in same}
        po['providers']=[p for p in po['providers'] if p not in same]
        if same:po['providers'].append(provider('MIN_SSGA','State Street Investment Management','institution',['scan_gold','scan_valuation'],
            ['GOLD','GROWTH_THEME','VALUE_DIVIDEND'],same[0]['seed_url'],'minimum_ssga_v2',documents=ssga_docs))
        # Finite ten-need extension, same provider and HTTP access boundaries.
        po.update(max_requests=48,scan_extension='four_asset_minimum_v2')
    if len(po['providers'])>12:raise SourceError('minimum Scan exceeds provider budget')
    return po


def _record(token, measure, unit, period, currency, scope, adjustment, locator, *, grouped=False):
    value=_decimal(token.replace(',','') if grouped else token,'minimum Scan field')
    if unit in ('USD_per_BTC','USD_per_ETH','USD_per_troy_ounce') and value<=0:raise SourceError('positive crypto/gold price required')
    if unit in ('Bcf','thousand_barrels') and (value<0 or value!=value.to_integral_value()):raise SourceError('nonnegative whole inventory required')
    return dict(quote=token,locator=locator,definition=definition(measure,unit,period,currency,scope,adjustment),
        extraction='grouped_decimal_scalar_v1' if grouped and ',' in token else 'decimal_scalar_v1',label=measure,limitations=[])


def _result(records, observed, *, published=None, limitations=()):
    return dict(records=records,observed_at=observed,published_at=published,valid_as_of=observed,complete=True,
        limitations=list(limitations))


def parse_candidate(contract,response,candidate):
    if contract.endswith('_v2'):
        return parse_supplement(contract,response,candidate)
    if contract=='minimum_crypto_v1':
        product=candidate['index_identity_fields']['product'];asset=candidate['asset_id']
        if product not in ('BTC-USD','ETH-USD') or product!=asset+'-USD' or '/products/'+product+'/candles?' not in candidate['url']:
            raise SourceError('crypto venue/product scope mismatch')
        params=candidate['url'].split('?',1)[1]
        if 'granularity=86400' not in params:raise SourceError('UTC daily bars required')
        rows=json_document(response);at=_time(candidate['document']['retrieved_at']);completed=[]
        if not isinstance(rows,list) or not 8<=len(rows)<=10:raise SourceError('bounded eight-day candle window required')
        for i,row in enumerate(rows):
            if not isinstance(row,list) or len(row)!=6 or type(row[0]) is not int or row[0]%86400:
                raise SourceError('invalid UTC daily candle')
            close_at=datetime.fromtimestamp(row[0],timezone.utc)+timedelta(days=1)
            if close_at<=at:
                close=_decimal(str(row[4]),'completed close');volume=_decimal(str(row[5]),'daily volume')
                if close<=0 or volume<0:raise SourceError('invalid candle price or volume')
                completed.append((close_at,i))
        completed.sort()
        if len(completed)<8 or len({r[0] for r in completed})!=len(completed):raise SourceError('missing/duplicate completed bars')
        selected=completed[-8:]
        if any(b[0]-a[0]!=timedelta(days=1) for a,b in zip(selected,selected[1:])):
            raise SourceError('nonconsecutive weekly price endpoints')
        records=[_record(str(rows[i][4]),'COINBASE_'+asset+'_USD_DAILY_CLOSE','USD_per_'+asset,t.isoformat(),'USD',
            'Coinbase Exchange '+product+' UTC daily close','unadjusted_completed_candle',f'json_scalar:/{i}/4')
            for t,i in (selected[0],selected[-1])]
        t,i=selected[-1]
        records.append(_record(str(rows[i][5]),'COINBASE_'+asset+'_DAILY_BASE_VOLUME',asset,t.isoformat(),None,
            'Coinbase Exchange '+product+' UTC daily volume','completed_UTC_day_base_volume',f'json_scalar:/{i}/5'))
        return _result(records,t.isoformat(),limitations=['한 거래소의 일곱 날 가격 흐름·완료 하루 거래량. 총수익률·전 시장 유동성·기관 수요·전체 레버리지가 아니다.'])
    text=_visible_html(_decode(response.body,response.content_type))
    if contract=='minimum_gold_v1':
        if candidate['index_identity_fields'].get('symbol')!='GLD' or not re.search(r'GLD.*?Gold Shares',text):
            raise SourceError('GLD issuer identity missing')
        m=re.search(r'Fund Net Asset Value as of ([A-Z][a-z]{2} \d{2} \d{4}) LBMA Gold Price PM \$([\d,]+\.\d+)',text)
        if not m:raise SourceError('dated LBMA PM benchmark price absent')
        at=datetime.strptime(m[1],'%b %d %Y').replace(tzinfo=timezone.utc).isoformat()
        records=[_record(m[2],'LBMA_GOLD_PM_ISSUER_REPORTED','USD_per_troy_ounce',at[:10],'USD',
            'LBMA Gold Price PM reported by GLD issuer','USD_PM_benchmark_not_GLD_NAV',
            'text:Fund Net Asset Value / dated LBMA Gold Price PM',grouped=True)]
        perf=re.search(r'Fund Performance.*?as of ([A-Z][a-z]{2} \d{2} \d{4}).*?Benchmark LBMA Gold Price PM \1 (-?[\d.]+)%',text)
        if perf:
            day=datetime.strptime(perf[1],'%b %d %Y').date().isoformat()
            records.append(_record(perf[2],'LBMA_GOLD_PM_ISSUER_MONTH_RETURN','percent',day,'USD',
                'LBMA Gold Price PM reported by GLD issuer','issuer_reported_calendar_month_benchmark_return',
                'text:Performance / Month End / Benchmark LBMA Gold Price PM / 1 Month'))
        return _result(records,at,limitations=['GLD 발행사가 보고한 LBMA 오후 기준가격/월말 기준가격 변화다. GLD NAV·ETF 자금흐름·중앙은행 수요·미래 수익은 별개다.'])
    if contract=='minimum_real_rate_v1':
        tabs=html_records(response).tables
        matches=[t for t in tabs if t and t[0][0]=='Instruments' and any(r[0].startswith('Inflation indexed') for r in t)]
        if len(matches)!=1 or 'Yields in percent per annum' not in text:raise SourceError('H.15 real-yield identity/unit changed')
        table=matches[0];days=[datetime.strptime(v,'%Y%b%d').date() for v in table[0][1:]]
        start=next(i for i,r in enumerate(table) if r[0].startswith('Inflation indexed'))
        row=next(r for r in table[start+1:] if r[0]=='10-year')
        if len(row)!=len(days)+1 or days!=sorted(set(days)):raise SourceError('H.15 real dates/columns mismatch')
        records=[]
        for i in range(len(days)-2,len(days)):
            records.append(_record(row[i+1],'US_TIPS_10Y_CURRENT','percent',days[i].isoformat(),'USD',
                'US Treasury TIPS constant maturity 10 years','inflation_indexed_market_yield_not_gold_expected_return',
                f'text:H15 Inflation indexed / 10-year / {days[i]}'))
        pub=re.search(r'Release date: ([A-Z][a-z]+ \d{1,2}, \d{4})',text)
        return _result(records,days[-1].isoformat(),published=datetime.strptime(pub[1],'%B %d, %Y').date().isoformat() if pub else None,
            limitations=['십년 물가연동 국채 실질 시장금리. 금의 기대수익/적정가격을 계산하지 않는다.'])
    if contract=='minimum_spot_v1':
        oil=candidate['index_identity_fields']['block']=='oil_price'
        identity='Cushing, OK WTI Spot Price FOB (Dollars per Barrel)' if oil else 'Henry Hub Natural Gas Spot Price (Dollars per Million Btu)'
        if identity not in text:raise SourceError('EIA spot price identity/unit mismatch')
        tabs=[t for t in html_records(response).tables if t and t[0]==['Week Of','Mon','Tue','Wed','Thu','Fri']]
        if len(tabs)!=1:raise SourceError('one weekday spot price table required')
        points=[]
        for row in tabs[0][1:]:
            if not row or not row[0]:continue
            m=re.fullmatch(r'(\d{4}) ([A-Z][a-z]{2})-\s*(\d{1,2}) to [A-Z][a-z]{2}-\s*\d{1,2}',row[0])
            if not m or len(row)!=6:raise SourceError('EIA weekday/date schema changed')
            start=datetime.strptime(f'{m[1]} {m[2]} {m[3]}','%Y %b %d').date()
            if start.weekday()!=0:raise SourceError('EIA week must start Monday')
            for i,token in enumerate(row[1:]):
                if token in ('','-','--','NA','W'):continue
                _decimal(token,'EIA daily price')  # WTI legitimately went negative in 2020.
                points.append((start+timedelta(days=i),token))
        if len(points)<2 or len({p[0] for p in points})!=len(points):raise SourceError('duplicate/missing spot dates')
        points.sort();latest=points[-1]
        # Approximately one trading week, keeping the exact calendar interval.
        prior=[p for p in points if latest[0]-timedelta(days=10)<=p[0]<=latest[0]-timedelta(days=7)]
        if not prior:raise SourceError('weekly spot comparison endpoint unavailable')
        records=[_record(token,'EIA_WTI_SPOT' if oil else 'EIA_HENRY_HUB_SPOT','USD_per_barrel' if oil else 'USD_per_MMBtu',
            day.isoformat(),'USD',identity,'reported_daily_spot_not_futures_contract',f'text:weekday price / {day}') for day,token in (prior[-1],latest)]
        release=re.search(r'Release Date: (\d{1,2}/\d{1,2}/\d{4})',text)
        return _result(records,latest[0].isoformat(),published=datetime.strptime(release[1],'%m/%d/%Y').date().isoformat() if release else None,
            limitations=['미국 특정 인도지점 현물가격, 정확한 관측 기간의 가격 변화다. 선물곡선·한국 ETF/ETN 실현수익·보관/교체 비용을 대체하지 않는다.'])
    if contract=='minimum_stock_v1':
        oil=candidate['index_identity_fields']['block']=='oil_stock'
        title='Commercial Crude Oil (Excl. Lease Stock)' if oil else 'Total Lower 48 States'
        unit_phrase='Thousand Barrels' if oil else 'Billion Cubic Feet'
        if unit_phrase not in text:raise SourceError('EIA inventory unit missing')
        header=re.search(r'(?:Product|Region)(?:\s+[^\d]{0,40})?\s+((?:\d{2}/\d{2}/\d{2} ){5}\d{2}/\d{2}/\d{2})',text)
        if not header:raise SourceError('six dated weekly inventory columns required')
        days=[datetime.strptime(d,'%m/%d/%y').date() for d in header[1].split()]
        row=re.search(re.escape(title)+r' ((?:[\d,]+ ){5}[\d,]+) \d{4}-\d{4}',text)
        if not row or days!=sorted(set(days)):raise SourceError('inventory row/date alignment missing')
        values=row[1].split()
        if any(b-a!=timedelta(days=7) for a,b in zip(days,days[1:])):raise SourceError('weekly stock dates are not consecutive')
        records=[_record(values[i],'EIA_US_COMMERCIAL_CRUDE_STOCK' if oil else 'EIA_US_WORKING_GAS_STOCK',
            'thousand_barrels' if oil else 'Bcf',days[i].isoformat(),None,
            'US commercial crude excludes lease stock and SPR' if oil else 'US Lower 48 working gas underground',
            'weekly_reported_stock_not_forecast_not_seasonally_adjusted',f'text:{title} / {days[i]}',grouped=True) for i in (4,5)]
        release=re.search(r'Release Date: (\d{1,2}/\d{1,2}/\d{4})',text)
        return _result(records,days[-1].isoformat(),published=datetime.strptime(release[1],'%m/%d/%Y').date().isoformat() if release else None,
            limitations=['공식 주간 추정 실제 재고, 개정 가능. 단순 전주 증가를 계절조정 부족/잉여·가격 매력으로 해석하지 않는다. 평년 대비·날씨·생산·선물 가격은 별도다.'])
    raise SourceError('unsupported minimum evidence document contract')


def parse_supplement(contract,response,candidate):
    """Narrow reviewed tables. Web text is data, never executed instructions."""
    text=_visible_html(_decode(response.body,response.content_type));fields=candidate['index_identity_fields']
    block=fields.get('block');asset=candidate['asset_id']
    if contract=='minimum_ssga_v2':
        from .scan import parse_candidate as parse_scan
        return parse_scan('scan_ssga_v1',response,candidate)
    if contract=='minimum_monthly_gas_v2':
        production=block=='gas_production'
        if asset!='NATGAS' or block not in ('gas_production','gas_lng'):raise SourceError('gas monthly scope mismatch')
        title=('U.S. Dry Natural Gas Production' if production else 'Liquefied U.S. Natural Gas Exports')+' (Million Cubic Feet)'
        path='/dnav/ng/hist/'+('n9070us2m.htm' if production else 'n9133us2m.htm')
        if urlsplit(candidate['url']).path!=path or title not in text:raise SourceError('gas monthly identity/unit mismatch')
        header=['Year',*list(calendar.month_abbr)[1:]]
        tables=[t for t in html_records(response).tables if t and t[0]==header]
        if len(tables)!=1:raise SourceError('one monthly actual gas table required')
        points={}
        for row in tables[0][1:]:
            if row==['']:continue
            if len(row)!=13 or not re.fullmatch(r'\d{4}',row[0]):raise SourceError('monthly gas columns changed')
            for month,token in enumerate(row[1:],1):
                if token in ('','-','--','NA','W'):continue
                day=datetime(int(row[0]),month,calendar.monthrange(int(row[0]),month)[1]).date()
                if day in points:raise SourceError('duplicate gas month')
                value=_decimal(token.replace(',',''),'monthly reported gas')
                if value<0 or value!=value.to_integral_value():raise SourceError('invalid monthly volume')
                points[day]=token
        ordered=sorted(points)
        if not ordered:raise SourceError('actual gas months unavailable')
        latest=ordered[-1];prior=latest.replace(day=1)-timedelta(days=1)
        if prior not in points:raise SourceError('adjacent actual gas month unavailable')
        dates=[prior,latest];year_ago=latest.replace(year=latest.year-1,day=calendar.monthrange(latest.year-1,latest.month)[1])
        if year_ago in points:dates.insert(0,year_ago)
        measure='EIA_US_DRY_GAS_PRODUCTION' if production else 'EIA_US_LNG_EXPORTS'
        records=[_record(points[d],measure,'MMcf',d.strftime('%Y-%m'),None,
            'US nationwide dry gas production' if production else 'US liquefied natural gas exports',
            'reported_monthly_actual_volume_not_forecast_not_daily_feedgas',f'text:{title} / {d:%Y-%m}',grouped=True) for d in dates]
        release=re.search(r'Release Date: (\d{1,2}/\d{1,2}/\d{4})',text)
        if not release:raise SourceError('gas release date missing')
        return _result(records,latest.isoformat(),published=datetime.strptime(release[1],'%m/%d/%Y').date().isoformat(),
            limitations=['미국 전체의 시차 있는 공식 월간 실제 보고량, 개정 가능. Lower 48 주간 현재 생산/당일 LNG feedgas가 아니다. 월 일수가 달라 일평균으로 나누어 비교한다.'])
    if contract=='minimum_gas_reference_v2':
        if asset!='NATGAS' or block not in ('gas_reference_a','gas_reference_b'):
            raise SourceError('gas seasonal reference scope mismatch')
        title='Lower 48 States Natural Gas Working Underground Storage (Billion Cubic Feet)'
        if title not in text:raise SourceError('gas history region/unit mismatch')
        tables=[t for t in html_records(response).tables if t and t[0]==['Year-Month','Week 1','Week 2','Week 3','Week 4','Week 5']]
        if len(tables)!=1 or tables[0][1]!=['End Date','Value']*5:raise SourceError('dated weekly storage history required')
        points={}
        for row in tables[0][2:]:
            if row==['']:continue
            if len(row)!=11 or not re.fullmatch(r'\d{4}-[A-Z][a-z]{2}',row[0]):raise SourceError('gas weekly history columns changed')
            year,month=row[0].split('-')
            for ds,token in zip(row[1::2],row[2::2]):
                if not ds and not token:continue
                day=datetime.strptime(year+'/'+ds,'%Y/%m/%d').date()
                if day.strftime('%b')!=month or day.weekday()!=4 or day in points:raise SourceError('weekly storage dates/duplicates invalid')
                if token in ('','-','--','NA','W'):continue
                points[day]=token
        latest=max(points);week=latest.isocalendar().week;refs=[]
        for year in range(latest.year-5,latest.year):
            day=datetime.fromisocalendar(year,week,5).date()
            if day not in points:raise SourceError('five exact same-ISO-week seasonal endpoints required')
            refs.append(day)
        chosen=refs[:3] if block=='gas_reference_a' else refs[3:]
        records=[_record(points[d],'EIA_GAS_ISO_WEEK_REFERENCE_'+str(d.year),'Bcf',d.isoformat(),None,
            'US Lower 48 working gas underground',f'reported_historical_stock_ISO_week_{week}_reference_for_{latest.isoformat()}',
            f'text:{title} / {d}',grouped=True) for d in chosen]
        release=re.search(r'Release Date: (\d{1,2}/\d{1,2}/\d{4})',text)
        return _result(records,latest.isoformat(),published=datetime.strptime(release[1],'%m/%d/%Y').date().isoformat() if release else None,
            limitations=['현재 판본의 과거 실제 재고. 같은 ISO 주 금요일의 과거 오년 표본으로 자체 비교하며 EIA 공식 보간 오년 평균이 아니다. 최초 발표 vintage/평년 주입 속도는 미확인.'])
    if contract=='minimum_weather_v2':
        if asset!='NATGAS' or block not in ('weather_6_10','weather_8_14'):raise SourceError('weather scope mismatch')
        issue=re.search(r'Issued: ([A-Z][a-z]{2} \d{2}, \d{4})',text)
        label='6-10' if block=='weather_6_10' else '8-14'
        match=re.search(label+r' DAY OUTLOOK TABLE Outlook for ([A-Z][a-z]{2}) (\d{1,2}) - (\d{1,2}) (\d{4}) (.*?)(?=8-14 DAY OUTLOOK TABLE|LEGEND)',text)
        if not issue or not match or 'TEMPS WITH RESPECT TO NORMAL' not in text:raise SourceError('dated CPC table/temperature legend absent')
        issued=datetime.strptime(issue[1],'%b %d, %Y').date();start=datetime.strptime(f'{match[1]} {match[2]} {match[4]}','%b %d %Y').date()
        end=datetime.strptime(f'{match[1]} {match[3]} {match[4]}','%b %d %Y').date()
        if not issued<start<=end or end-start!=timedelta(days=4 if label=='6-10' else 6):raise SourceError('CPC forecast valid window changed')
        records=[]
        for state in ('NEW YORK','OHIO','N TEXAS'):
            values=re.findall(re.escape(state)+r' ([ANB]) ([ANB])\b',match[5])
            if len(values)!=1:raise SourceError('state temperature/precipitation columns ambiguous')
            temp,precip=values[0];quote=state+' '+temp+' '+precip
            records.append(dict(quote=quote,locator=f'text:{label} DAY OUTLOOK TABLE / {start} to {end} / {state} / TEMP then PCPN',
                definition=definition('NOAA_CPC_'+label.replace('-','_')+'_TEMPERATURE_OUTLOOK','text',
                    f'forecast_valid_{start}_to_{end}',None,state+' state average TEMP vs normal','forecast_category_'+temp+'_not_actual_temperature_or_HDD'),
                extraction=None,label=label+'일 '+state+' 기온 전망',limitations=['A=평년보다 높음, N=평년 근처, B=평년보다 낮음. 두번째 열은 강수이며 기온과 혼동하지 않는다.']))
            records[-1]['observed_at']=issued.isoformat()
        return _result(records,issued.isoformat(),published=issued.isoformat(),limitations=[
            '기상 전망을 발표한 사실만 확인. 실제 수요/HDD/CDD 관측·보장된 기온이 아니다. 주 평균은 도시별 차이를 숨길 수 있다.'])
    if contract=='minimum_iau_v2':
        if asset!='GOLD' or '/239561/' not in candidate['url'] or 'iShares Gold Trust' not in text:raise SourceError('IAU identity missing')
        match=re.search(r'Tonnes in Trust ([\d,.]+) as of ([A-Z][a-z]{2} \d{2}, \d{4})',text)
        if not match or 'based on trade date activity' not in text:raise SourceError('dated physical holdings definition absent')
        at=datetime.strptime(match[2],'%b %d, %Y').date().isoformat()
        if _decimal(match[1].replace(',',''),'gold tonnes')<=0:raise SourceError('invalid gold holding')
        return _result([_record(match[1],'IAU_GOLD_PHYSICAL_HELD','tonnes',at,None,'iShares Gold Trust IAU physical gold',
            'issuer_reported_trade_date_holdings_not_AUM_not_net_flow','text:Tonnes in Trust / '+at,grouped=True)],at,
            limitations=['한 금 신탁의 실제 실물 보유량 수준. AUM·전체 ETF 수요·순유입·중앙은행 매수/보유 증가를 증명하지 않는다. 회계 기준 bar list와 거래일 기준은 다를 수 있다.'])
    if contract=='minimum_gsg_v2':
        if asset!='BROAD_COMMODITIES' or '/239757/' not in candidate['url'] or 'GSG Commodity iShares S&P GSCI Commodity-Indexed Trust' not in text:
            raise SourceError('broad commodity GSG identity missing')
        nav=re.search(r'NAV as of ([A-Z][a-z]{2} \d{2}, \d{4}) \$ ([\d,.]+)',text)
        trend=re.search(r'NAV Total Return as of ([A-Z][a-z]{2} \d{2}, \d{4}) YTD: (?:Increase|Decrease) (-?[\d.]+)%',text)
        quote='The fund offers a way to diversify portfolios and express views on energy, metals, agriculture, and livestock markets.'
        if not nav or not trend or quote not in text or 'S&P GSCI(R) Total Return Index' not in text:raise SourceError('broad commodity dates/benchmark/groups absent')
        at=datetime.strptime(nav[1],'%b %d, %Y').date().isoformat();end=datetime.strptime(trend[1],'%b %d, %Y').date().isoformat()
        if end>at:raise SourceError('future GSG performance date')
        records=[_record(nav[2],'ISHARES_GSG_NAV','USD_per_share',at,'USD','iShares GSG S&P GSCI Commodity-Indexed Trust',
            'issuer_reported_fund_NAV_not_spot_index_not_market_price','text:GSG NAV / '+at,grouped=True),
            _record(trend[2],'ISHARES_GSG_YTD_NAV_TOTAL_RETURN','percent',end,'USD','iShares GSG S&P GSCI Commodity-Indexed Trust',
            'issuer_reported_YTD_NAV_total_return_including_fund_costs_calendar_year_'+end[:4],'text:GSG NAV Total Return YTD / '+end),
            dict(quote=quote,locator='text:GSG fund description / sectors',definition=definition('GSG_COMMODITY_GROUPS','text',at,None,
                'energy industrial/precious metals agriculture livestock','product_scope_not_current_group_weights'),
                extraction=None,label='대표 상품 구성 그룹',limitations=['그룹 포함은 확인했으나 현재 에너지/산업금속/귀금속/농산물 비중은 미확인.'])]
        return _result(records,at,limitations=['생산 가중 S&P GSCI 기반 선물 상품의 NAV/총수익, 현물 지수 변화가 아니다. 선물 교체·담보 이자·수수료·추적 차이가 영향을 준다. 전 원자재의 동반 상승 또는 물가 방어를 증명하지 않는다.'])
    if contract=='minimum_eth_flow_v2':
        if asset!='ETH' or block not in ('eth_flow_recent','eth_flow_prior'):raise SourceError('ETH flow scope mismatch')
        if 'Ethereum ETF Flow (US$m)' not in text:raise SourceError('ETH flow title/unit not confirmed')
        tables=[t for t in html_records(response).tables if any('ETHA' in r and 'FETH' in r for r in t)]
        if len(tables)!=1:raise SourceError('one Ethereum ETF table required')
        table=tables[0];header=next(r for r in table if 'ETHA' in r and 'FETH' in r)
        if header[-1:]==[''] and table[0][-1:]==['Total'] and len(table[0])==len(header):header=[*header[:-1],'Total']
        if header[-1:]!=['Total']:raise SourceError('ETH total column missing')
        rows=[]
        for row in table:
            if row and re.fullmatch(r'\d{2} [A-Z][a-z]{2} \d{4}',row[0]):
                if len(row)!=len(header) or any(not re.fullmatch(r'-|\(?[\d,]+(?:\.\d+)?\)?',v) for v in row[1:]):
                    raise SourceError('ETH flow columns/missing values ambiguous')
                rows.append((datetime.strptime(row[0],'%d %b %Y').date(),row))
        if len(rows)<5 or len({d for d,r in rows})!=len(rows):raise SourceError('five unique ETH flow days required')
        rows.sort();recent=rows[-5:];latest=recent[-1][0]
        from .source_pipeline import _extract
        for day,row in recent:
            if '-' not in row[1:]:
                d=definition('US_SPOT_ETH_ETF_DAILY_NET_FLOW','USD_million',day.isoformat(),'USD',
                    'US spot Ethereum ETFs reported by Farside','complete_row_provider_reported_not_issuer_confirmed')
                if _extract(' '.join(row),'eth_dated_table_total_v2',d) is None:raise SourceError('ETH latest-window component/total mismatch')
        selected=recent[-3:] if block=='eth_flow_recent' else recent[:2];records=[];latest_complete='-' not in recent[-1][1][1:]
        for day,row in selected:
            complete='-' not in row[1:]
            records.append(dict(quote=' '.join(row),locator='table:Ethereum ETF Flow (US$m)/'+row[0]+'/Total',
                definition=definition('US_SPOT_ETH_ETF_DAILY_NET_FLOW','USD_million',day.isoformat(),'USD',
                    'US spot Ethereum ETFs reported by Farside',('complete_row_provider_reported_not_issuer_confirmed' if latest_complete else 'historical_reference_not_current_flow_when_latest_partial') if complete else 'partial_row_not_final_total'),
                extraction='eth_dated_table_total_v2',label='미국 ETH ETF 일별 순유입',limitations=['제공자 자동 집계 전사이며 발행사 독립 교차 확인 전이다. 합계 산술 통과가 숫자의 경제적 진실을 증명하지 않는다.']))
        result=_result(records,latest.isoformat(),limitations=['BTC와 별도 ETH 고유 집계. 최신 하루·최근 오 거래일·일곱 날 가격은 서로 다른 기간이다.',
            'Farside는 자동 표의 오류 가능성을 고지한다. 이례적 단일일 집계는 원발행사 확인 전 강한 수요/괴리 판단에 사용하지 않는다.'])
        result.update(complete=latest_complete,missing_columns=[header[i] for i,v in enumerate(recent[-1][1]) if v=='-'])
        return result
    raise SourceError('unsupported four-asset document contract')


ECOS_CONTEXT={
    'KR_CD_91D':('817Y002','1.3.2.1. 시장금리(일별)','010502000','CD(91일)','D','연%','daily',10),
    'KR_HOUSEHOLD_NEW_LOAN_RATE':('121Y006','1.3.3.2.1. 예금은행 대출금리(신규취급액 기준)','BECBLA03','가계대출','M','연리%','monthly',100)}


def macro_context(day,question):
    """Two explicit ECOS benchmark feeds, through the existing macro engine."""
    from .macro import SeriesDefinition
    data=dict(schema_version='1',id='MINIMUM_KR_CONTEXT',question=question,series=[],sources=[],bindings=[],yoy_series_ids=[],yield_pair=None)
    for identifier,(table,title,item,label,freq,unit,frequency,age) in ECOS_CONTEXT.items():
        start=day-timedelta(days=6) if freq=='D' else (day.replace(day=1)-timedelta(days=62)).replace(day=1)
        form='%Y%m%d' if freq=='D' else '%Y%m'
        url='https://ecos.bok.or.kr/api/StatisticSearch/sample/json/kr/1/10/'+table+'/'+freq+'/'+start.strftime(form)+'/'+day.strftime(form)+'/'+item
        sid='BOK_'+identifier
        desc=f'ECOS {table} {title}, {item} {label}, {unit}. '+('원화 CD 91일 시장금리 benchmark; 개인 예금/MMF 계약금리·세후수익 아님.' if freq=='D' else '예금은행 신규취급 가계대출 평균금리; 주담대 전용·지역별·개인 실행금리 아님.')
        d=SeriesDefinition(identifier,label+' 공식 비교 기준',desc,'percent',frequency,'not_seasonally_adjusted','한국은행 ECOS',sid,'KR','KRW',
            max_age_days=age,release_characteristics='최초 공개 시각 미확인; 획득 시각 이후만 현재 판본 사용.',
            revision_characteristics='전체 최초 발표/개정 이력 미확인; 원문 판본 보존.')
        s=SourceSpec(sid,url,url,'primary','한국은행 ECOS',label+' 공식 금리',None,None,None,'KR',('macro','interest_rates'),('CASH','BOND'),'application/json','public_api',
            'https://ecos.bok.or.kr/', '공식 무키 sample 최대10행, 한 항목·짧은 기간. 제한 우회 없음; 귀속 표시한 개인 통계 연구.',
            'full',age,excerpts=({'id':'IDENTITY','quote':label,'locator':'/StatisticSearch/row/0/ITEM_NAME1','definition':{'kind':'reviewed_macro_feed_identity_or_release'}},),
            full_retention_permission='ECOS 공식 공개 통계의 제한된 sample 응답, 개인 연구·재현용 보존 및 출처 표시.')
        data['series'].append(asdict(d));data['sources'].append(asdict(s))
        data['bindings'].append(dict(series_id=identifier,source_id=sid,adapter='ecos_context_v1',field=item,start_date=start.isoformat()))
    return data


def ecos_context_observations(raw,binding,d):
    from .sources import _parse_json
    if d.canonical_id not in ECOS_CONTEXT:raise SourceError('unreviewed ECOS context series')
    table,title,item,label,freq,unit,frequency,age=ECOS_CONTEXT[d.canonical_id]
    if (binding.field!=item or d.source_id!='BOK_'+d.canonical_id or d.unit!='percent' or d.currency!='KRW' or d.frequency!=frequency
            or d.adjustment!='not_seasonally_adjusted' or d.transformation!='raw' or d.jurisdiction!='KR'):
        raise SourceError('ECOS benchmark definition changed')
    doc=_parse_json(raw.decode('utf-8'));data=doc.get('StatisticSearch')
    if not isinstance(data,dict) or type(data.get('list_total_count')) is not int or data['list_total_count']!=len(data['row']) or len(data['row'])>10:
        raise SourceError('ECOS benchmark missing/truncated sample')
    out=[];seen=set()
    for i,r in enumerate(data['row']):
        if (r['STAT_CODE']!=table or r['STAT_NAME']!=title or r['ITEM_CODE1']!=item or r['ITEM_NAME1']!=label or r['UNIT_NAME']!=unit
                or any(r.get('ITEM_CODE'+str(n)) is not None for n in (2,3,4))):raise SourceError('ECOS benchmark field/unit identity changed')
        day=datetime.strptime(r['TIME'],'%Y%m%d' if freq=='D' else '%Y%m').date()
        if day in seen or day<binding.start_date:raise SourceError('duplicate/out-of-window ECOS benchmark')
        seen.add(day);out.append((day,_decimal(r['DATA_VALUE'],'ECOS benchmark'),f'/StatisticSearch/row/{i}/DATA_VALUE; TIME={r["TIME"]}; ITEM_CODE1={item}'))
    return out
