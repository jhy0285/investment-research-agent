"""Samsung/SK hynix data contracts, not routing or a separate research engine.

Original filings, issuer statements and provider fields retain different grades.
All arithmetic consumes matched, dated evidence; a calculated multiple never
certifies the accounting inputs or an investment thesis.
"""
from copy import deepcopy
from datetime import date, datetime, timezone
import calendar
from decimal import Decimal, localcontext
from functools import lru_cache
import re
import resource
import shutil
import subprocess
import tempfile
from urllib.parse import urlsplit

from .sources import SourceError, _decode, _visible_html, _time

VERSION = 'korean_semiconductor_comparison_v1'
COMPANIES = {'SAMSUNG': ('삼성전자', '005930', '00126380'),
             'SK_HYNIX': ('SK하이닉스', '000660', '00164779')}
NAMES = {'semiconductor_registration': 'DART 보고서 등록 확인',
         'semiconductor_filing': 'DART 원공시 본문',
         'semiconductor_accounts': '기간·정의별 재무제표',
         'semiconductor_price': '보통주 장마감 가격',
         'semiconductor_community': '현재 기업·HBM 투자 토론'}
BLOCKS = {
    'SAMSUNG': ('quarter', 'quarter_yoy', 'ytd', 'prior_ytd', 'annual',
                'eps_half', 'eps_annual', 'balance', 'cashflow', 'notes', 'earnings_drivers'),
    'SK_HYNIX': ('quarter_yoy', 'ttm_q3', 'ttm_q4', 'eps_a', 'eps_b',
                 'balance', 'quality', 'cashflow'),
}
SCOPE = 'K-IFRS consolidated Samsung group'
EPS_NOTE = 'EPS : Net income / Weighted average of outstanding common shares (based on audit report)'
BVPS_NOTE = 'BVPS : Total equity less Intangible assets / Total number of shares outstanding'


def evidence_needs(methods):
    needs = []
    for m in methods:
        if m['id'] not in COMPANIES: continue
        asset = m['id']
        for category in ('semiconductor_registration', 'semiconductor_filing', 'semiconductor_price'):
            needs.append(dict(id='NEED_SEMI_'+asset+'_'+category.rsplit('_', 1)[1].upper(),
                asset_id=asset, category=category, label=m['label']+' '+NAMES[category],
                reason='사업의 변화와 현재 지불 가격을 구분하는 비교', max_selected=1,
                max_age_seconds=(7 if category.endswith('price') else 21 if category.endswith('community') else 135)*86400))
        for block in BLOCKS[asset]:
            needs.append(dict(id='NEED_SEMI_'+asset+'_'+block.upper(), asset_id=asset,
                category='semiconductor_accounts', block=block, label=m['label']+' '+block+' 재무 입력',
                reason='같은 기간·주식 종류·회계 정의의 계산 입력', max_selected=1,
                max_age_seconds=(400 if block in ('annual', 'eps_annual') else 135)*86400))
        needs.append(dict(id='NEED_SEMI_'+asset+'_COMMUNITY', asset_id=asset,
            category='semiconductor_community', label=m['label']+' '+NAMES['semiconductor_community'],
            reason='실제로 발견한 투자 가설을 원자료와 대조', max_selected=1, max_age_seconds=21*86400))
    # Core price/statement requests precede optional discussion. Keep the
    # existing request budget rather than let one company's comments starve
    # the other company's financial inputs.
    return sorted(needs, key=lambda n:n['category']=='semiconductor_community')


def policy(base, config, needs):
    out = deepcopy(base)
    assets = {n['asset_id'] for n in needs}
    # Existing BTC/region providers are irrelevant to these needs and consume
    # no requests. Keep providers required by a combined, explicitly scoped ask.
    categories = {n['category'] for n in needs}
    out['providers']=[p for p in out['providers'] if set(p['categories']) & categories
        and (not p.get('asset_ids') or set(p['asset_ids']) & assets)]
    out['providers'].extend(deepcopy(p) for p in config['providers']
        if set(p['asset_ids']) & assets and set(p['categories']) & categories)
    if len(out['providers'])>12:
        ranked=sorted(out['providers'],key=lambda p:(p['method']=='access_probe',p['type']=='community'))
        out['providers']=ranked[:12]
        out['deferred_providers']=[dict(id=p['id'],asset_ids=p.get('asset_ids',[]),categories=p['categories'],
            reason='combined question exceeds existing 12-provider budget; no substitute evidence') for p in ranked[12:]]
    return out


def directory_items(provider, need, response):
    """Extract only first-party links/filing identities; never execute scripts."""
    from .discovery_contracts import html_records
    asset = need['asset_id']; name, code, corp = COMPANIES[asset]
    if provider['method'] == 'semiconductor_dart_directory':
        text = _decode(response.body, response.content_type)
        rows = []
        for row in re.findall(r'<tr\b[^>]*>.*?</tr>', text, re.S | re.I):
            if "openCorpInfoNew('"+corp+"'" not in row: continue
            visible = _visible_html(row)
            match = re.search(r'(반기보고서|분기보고서|사업보고서)\s*\((\d{4})\.(\d{2})\)', visible)
            receipts = list(dict.fromkeys(re.findall(r'/dsaf001/main\.do\?rcpNo=(\d{14})', row)))
            if not match or len(receipts) != 1: continue
            if '기재정정' in visible or '첨부정정' in visible:
                raise SourceError('corrected filing requires edition review; no silent original adoption')
            period = match[2]+'-'+match[3]
            if period != provider['report_period']: continue
            receipt = receipts[0]
            published = date(int(receipt[:4]), int(receipt[4:6]), int(receipt[6:8])).isoformat()
            fields = dict(asset_id=asset, corp_code=corp, stock_code=code, report_period=period,
                report_type=match[1], receipt=receipt, published_at=published, row_quote=visible)
            url = (provider['seed_url'] if need['category']=='semiconductor_registration'
                   else 'https://dart.fss.or.kr/dsaf001/main.do?rcpNo='+receipt)
            rows.append((url, fields))
        if len(rows) != 1: raise SourceError('unique company/period DART registration not found in bounded directory')
        return rows
    if provider['method'] == 'semiconductor_statement_links':
        block = need['block']; annual = block in ('annual', 'eps_annual')
        suffix = 'soi' if block in ('quarter', 'quarter_yoy', 'ytd', 'prior_ytd', 'annual', 'eps_half', 'eps_annual') else {
            'balance':'bs', 'cashflow':'cf', 'notes':'note'}[block]
        from urllib.parse import urljoin
        links = html_records(response).links
        pattern = r'/(\d{4})_con_quarter0([1-4])_'+suffix+r'\.pdf$'
        matches = []
        for href, _ in links:
            url = urljoin(provider['seed_url'], href); parsed = urlsplit(url)
            found = re.search(pattern, parsed.path)
            if not found or parsed.hostname != 'images.samsung.com': continue
            year, quarter = int(found[1]), int(found[2])
            if annual and quarter != 4: continue
            if not annual and quarter == 4: continue
            matches.append((year*4+quarter, url, dict(asset_id=asset, block=block, year=year, quarter=quarter)))
        if not matches: raise SourceError('reviewed consolidated statement link missing')
        latest = max(item[0] for item in matches)
        chosen = {item[1]:item[2] for item in matches if item[0]==latest}
        if len(chosen)!=1: raise SourceError('ambiguous latest statement edition')
        return list(chosen.items())
    raise SourceError('unreviewed semiconductor directory')


def pdf_allowed(url):
    parts = urlsplit(url)
    return parts.hostname=='images.samsung.com' and bool(re.fullmatch(
        r'/is/content/samsung/assets/global/ir/docs/\d{4}_con_quarter0[1-4]_(?:soi|bs|cf|note)\.pdf', parts.path))


@lru_cache(maxsize=8)
def pdf_text(body):
    """Optional local Poppler decoder, bounded bytes/output/time; no shell."""
    if not body.startswith(b'%PDF-') or len(body)>2*1024*1024: raise SourceError('invalid/big reviewed financial PDF')
    binary = shutil.which('pdftotext')
    if binary is None: raise SourceError('optional pdftotext executable unavailable; primary PDF evidence withheld')
    def limits():
        resource.setrlimit(resource.RLIMIT_AS, (512*1024*1024, 512*1024*1024))
        resource.setrlimit(resource.RLIMIT_FSIZE, (4*1024*1024, 4*1024*1024))
        resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    with tempfile.TemporaryFile() as output:
        try:
            result = subprocess.run([binary, '-layout', '-', '-'], input=body, stdout=output,
                stderr=subprocess.DEVNULL, timeout=10, check=False, preexec_fn=limits)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise SourceError('bounded financial PDF decoding failed') from exc
        output.seek(0); decoded = output.read(4*1024*1024+1)
    if result.returncode or len(decoded)>4*1024*1024: raise SourceError('financial PDF decoding failed/output exceeded limit')
    return decoded.decode('utf-8', errors='strict')


def _tokens(text, label, count):
    matches = list(re.finditer(r'^\s*'+re.escape(label)+r'\s+(.+)$', text, re.M))
    if len(matches)!=1: raise SourceError('unique financial row required: '+label)
    # All value columns are separated by layout spacing. Footnote columns
    # precede them; exactly the rightmost count tokens are values.
    tokens = re.findall(r'\(?-?[\d,]+(?:\.\d+)?\)?|(?<!\w)-(?!\w)', matches[0][1])
    if len(tokens)<count: raise SourceError('financial row/column missing: '+label)
    out=[]
    for token in tokens[-count:]:
        if token=='-': out.append(None); continue
        if not re.fullmatch(r'\(?-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\)?',token):
            raise SourceError('invalid financial cell')
        if token.startswith('(') != token.endswith(')'): raise SourceError('malformed signed financial cell')
        value = '-'+token[1:-1] if token.startswith('(') else token
        out.append(value.replace(',', ''))
    return out


def statement_document(body, url):
    if not pdf_allowed(url): raise SourceError('unreviewed PDF destination/statement')
    text = pdf_text(body); parts=urlsplit(url)
    year, quarter, kind = re.search(r'/(\d{4})_con_quarter0([1-4])_(\w+)\.pdf$',parts.path).groups()
    year,quarter=int(year),int(quarter); month=quarter*3
    if 'Samsung Electronics Co., Ltd. and its subsidiaries' not in text or 'CONSOLIDATED' not in text:
        raise SourceError('wrong issuer or separate financial statement')
    if 'In millions of Korean won' not in text: raise SourceError('statement unit missing/changed')
    end = ('December 31' if quarter==4 else {1:'March 31',2:'June 30',3:'September 30'}[quarter])
    if not re.search(re.escape(end)+r'.{0,250}?'+str(year),text,re.S): raise SourceError('statement date differs from filename')
    cells={}; quotes={}
    if kind=='soi':
        text=re.split(r'(?:INTERIM )?CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME',text)[0]
        annual=quarter==4; n=4 if annual else 8
        header='For the years ended December 31' if annual else 'For the three-month periods ended '+end
        if header not in text or not re.search(str(year)+r'\s+'+str(year-1),text):
            raise SourceError('income period/column order missing')
        if not annual and 'For the six-month periods ended June 30' not in text:
            raise SourceError('only reviewed half-year columns supported; new quarter requires review')
        currency_order = r'KRW\s+KRW\s+USD\s+USD' + (r'\s+KRW\s+KRW\s+USD\s+USD' if not annual else '')
        if not re.search(currency_order,text): raise SourceError('KRW/USD statement column order changed')
        for key,label in [('revenue','Revenue'),('operating','Operating profit'),('net','Profit for the year' if annual else 'Profit for the period'),
                          ('owners','Owners of the parent company'),('eps','- Basic')]:
            values=_tokens(text,label,n)
            if any(v is None for v in values): raise SourceError('missing income cell, not zero')
            if annual:
                cells[key]={str(year):values[0],str(year-1):values[1]}
            else:
                cells[key]={f'{year}Q{quarter}':values[0],f'{year-1}Q{quarter}':values[1],
                    f'{year}H1':values[4],f'{year-1}H1':values[5]}
    elif kind=='bs':
        if not re.search(r'KRW\s+KRW\s+USD\s+USD',text):
            raise SourceError('balance-sheet currency column order changed')
        for key,label in [('equity','Total equity'),('nci','Non-controlling interests'),('intangibles','Intangible assets')]:
            values=_tokens(text,label,4);cells[key]={f'{year}Q{quarter}':values[0]}
    elif kind=='cf':
        if 'For the six-month periods ended June 30' not in text or not re.search(r'KRW\s+KRW\s+USD\s+USD',text):
            raise SourceError('cash flow must be reviewed KRW half-year columns')
        for key,label in [('cfo','Net cash from operating activities'),('ppe_cash','Acquisition of property, plant and equipment')]:
            values=_tokens(text,label,4)
            if any(v is None for v in values[:2]): raise SourceError('missing cash flow cell')
            cells[key]={f'{year}H1':values[0],f'{year-1}H1':values[1]}
    else:
        ordinary=re.search(r'\(A\)\s+Ordinary shares.*?(?=\(B\)\s+Preference shares)',text,re.S)
        if not ordinary or 'Basic earnings per share' not in ordinary[0]:
            raise SourceError('ordinary/basic EPS note unavailable')
        quotes['ordinary_eps']=_visible_html(ordinary[0].split('(2)')[0])[:1100]
        paragraphs=[' '.join(p.split()) for p in re.split(r'\n\s*\n',text)]
        for key,pattern in [('investment_commitments',r'contractual commitments for the acquisition'),
                            ('market_risk',r'(?:investment portfolio consists|cyclical|demand.*fluctuat)')]:
            paragraph=next((p for p in paragraphs if re.search(pattern,p) and 30<len(p)<=1100),None)
            if paragraph:quotes[key]=paragraph
    return dict(cells=cells,quotes=quotes,year=year,quarter=quarter,kind=kind)


def market_document(body, url):
    code=urlsplit(url).path.rstrip('/').split('/')[-1]
    asset=next((a for a,(_,c,_) in COMPANIES.items() if c==code),None)
    if asset is None: raise SourceError('not a reviewed ordinary-share market code')
    name=COMPANIES[asset][0]; text=_visible_html(body)
    # Bind the quote to the security header, rather than news/sidebar numbers.
    matched=re.search(re.escape(name)+r'\s+'+code+r'\s+([\d,]+)\s+.*?My Stock.*?(\d{4}\.\d{2}\.\d{2})\s+장마감',text)
    if not matched: raise SourceError('dated closed-market security header unavailable; live quote not substituted')
    at=date.fromisoformat(matched[2].replace('.','-')).isoformat()
    token=matched[1]
    if not re.fullmatch(r'\d{1,3}(?:,\d{3})*',token) or Decimal(token.replace(',',''))<=0:
        raise SourceError('invalid ordinary-share price')
    return dict(asset=asset,code=code,close=token.replace(',',''),date=at,
        header=matched[0],price_type='displayed_market_close',adjustment='spot_quote_adjustment_not_explicitly_stated')


def source_document(body, mime, url):
    parts=urlsplit(url)
    if mime=='application/pdf': return statement_document(body,url)
    if parts.hostname=='markets.hankyung.com' and re.fullmatch(r'/stock/(?:005930|000660)/?',parts.path):
        return market_document(_decode(body,'text/html; charset=utf-8'),url)
    return None


def _definition(asset, key, unit, period, scope, adjustment):
    return dict(measure='SEMI_'+asset+'_'+key.upper(),unit=unit,period=period,
        currency='KRW' if unit!='text' else None,scope=scope,adjustment=adjustment)


def _record(value, locator, definition, label, limitations=()):
    return dict(quote=value,locator=locator,definition=definition,label=label,
        extraction=None if definition['unit']=='text' else 'decimal_scalar_v1',limitations=list(limitations))


def parse_candidate(contract, response, candidate):
    asset=candidate['asset_id']; fields=candidate['index_identity_fields']; category=candidate['category']
    records=[]; published=None; limits=[]; complete=True
    if contract=='semiconductor_dart_v1':
        if category!='semiconductor_registration':
            raise SourceError('DART viewer is not a verified financial table; filing figures remain unavailable')
        visible=_visible_html(_decode(response.body,response.content_type))
        quote=fields['row_quote']
        if quote not in visible: raise SourceError('DART registration row changed')
        at=fields['published_at'];published=at
        records=[_record(quote,'company/corp_code='+fields['corp_code']+'; receipt='+fields['receipt'],
            _definition(asset,'filing_registered','text',fields['report_period'],
                        'DART receipt '+fields['receipt'],'registration_only_not_original_financial_verification'),
            'DART 보고서 등록')]
        limits=['접수목록은 보고서 등록만 확인한다. 원공시 본문의 숫자·주석·최신 정정판 확인을 뜻하지 않는다.']
    elif contract=='semiconductor_market_v1':
        doc=market_document(_decode(response.body,response.content_type),candidate['url'])
        if doc['asset']!=asset: raise SourceError('different company/preferred security quote')
        at=doc['date']
        records=[_record(doc['close'],'json_scalar:/close',_definition(asset,'close','KRW_per_share',doc['date'],
            'KRX '+doc['code']+' ordinary share; domestic provider displayed close',doc['adjustment']), '표시 보통주 종가')]
        limits=['한국경제 코리아마켓 제공 시세; KRX 직접 원장 대조 미완료. 실시간 시세가 아니다.',
                '현재 표시 시세를 사용하며 수정주가 여부는 명시되지 않았다. 과거 수정주가 시계열과 결합하지 않는다.']
    elif contract=='semiconductor_samsung_statement_v1':
        if response.content_type.split(';')[0]!='application/pdf': raise SourceError('issuer statement returned non-PDF')
        doc=statement_document(response.body,candidate['url']);y=doc['year'];q=doc['quarter'];block=fields['block']
        if q!=4 and q!=2: raise SourceError('new interim quarter format requires review')
        at=f'{y}-12-31' if q==4 else f'{y}-06-30'
        periods={'quarter':f'{y}Q{q}','quarter_yoy':f'{y-1}Q{q}','ytd':f'{y}H1',
                 'prior_ytd':f'{y-1}H1','annual':str(y)}
        entries=[]
        if block in periods: entries=[(key,periods[block]) for key in ('revenue','operating','net')]
        elif block=='eps_half': entries=[('eps',f'{y}H1'),('eps',f'{y-1}H1')]
        elif block=='eps_annual': entries=[('eps',str(y))]
        elif block=='balance':entries=[(key,f'{y}Q{q}') for key in ('equity','nci','intangibles')]
        elif block=='cashflow':entries=[('cfo',f'{y}H1'),('ppe_cash',f'{y}H1'),('cfo',f'{y-1}H1')]
        elif block=='notes':
            for key,quote in doc['quotes'].items():
                records.append(_record(quote,'json_text:/quotes/'+key,
                    _definition(asset,key,'text',f'{y}H1',SCOPE,'issuer_financial_statement_note'), key))
            if len(records)<3: complete=False
        for key,period in entries:
            value=doc['cells'][key][period]
            if value is None: raise SourceError('missing primary statement field')
            records.append(_record(value,'json_scalar:/cells/'+key+'/'+period,
                _definition(asset,key,'KRW_per_share' if key=='eps' else 'KRW_million',period,SCOPE,
                    'K_IFRS_basic_common_EPS' if key=='eps' else 'consolidated_total_net_income' if key=='net'
                    else 'cash_PPE_acquisition_outflow' if key=='ppe_cash' else 'K_IFRS_reported'),key))
        limits=['기업 공식 연결 재무제표이며 DART 원문 교차 확인은 별도다. 최초 공개시각/전체 개정 이력은 미확인이다.']
    elif contract=='semiconductor_samsung_drivers_v1':
        from .korean_data import samsung_document
        if asset!='SAMSUNG':raise SourceError('Samsung explanations cannot substitute another company')
        doc=samsung_document(_decode(response.body,response.content_type))
        if not candidate['url'].endswith('/samsung-electronics-announces-'+doc['quarter']+'-quarter-'+doc['period'][:4]+'-results'):
            raise SourceError('issuer explanation URL/period mismatch')
        at=doc['period'];published=doc['published_at']
        patterns={'price_mix':r'The Memory Business achieved another record-breaking quarter .*? contributed to the record earnings\.',
            'hbm_statement':r'Additionally, the Business solidified market competitiveness .*? major customers\.',
            'foundry_cost':r'Earnings for the Foundry Business improved significantly prior to incentive-related provisions,.*? notable example\.'}
        for key,pattern in patterns.items():
            matches=list(re.finditer(pattern,doc['visible']))
            if len(matches)!=1 or len(matches[0][0])>1100:
                complete=False;continue
            records.append(_record(matches[0][0],'body:issuer_earnings_driver_'+key,
                _definition(asset,key,'text',at,'Samsung Electronics official quarterly release',
                    'management_business_explanation_not_independent_technology_validation'),key))
        limits=['기업이 설명한 가격·제품 구성·HBM·비용 맥락이다. 기여도 숫자·기술 순위·고객 인증·미래 수익을 독립적으로 검증한 것은 아니다.']
    elif contract=='semiconductor_hynix_provider_v1':
        from .korean_data import euroland_document
        doc=euroland_document(_decode(response.body,response.content_type));groups=doc['LevelZeroItems']
        quarterly=next(g for g in groups if g['name']=='Quarterly'); block=fields['block']
        table=lambda name:next(t for t in quarterly['Data'] if t['name']==name)
        columns=table('Income Statement')['Columns']
        if len(columns)!=len(set(columns)) or not all(re.fullmatch(r'\d{4} [1-4]Q',c) for c in columns):
            raise SourceError('ambiguous provider quarter columns')
        serial=lambda p:int(p[:4])*4+int(p[-2])-1
        columns=sorted(columns,key=serial);latest=columns[-1];year=int(latest[:4]);quarter=int(latest[-2])
        if any(serial(b)-serial(a)!=1 for a,b in zip(columns[-4:],columns[-3:])):
            raise SourceError('missing TTM provider quarter; no forward fill')
        at=f'{year}-{quarter*3:02d}-'+str(__import__('calendar').monthrange(year,quarter*3)[1])
        targets=[]
        if block in ('quarter_yoy','ttm_q3','ttm_q4'):
            period=f'{year-1} {quarter}Q' if block=='quarter_yoy' else columns[-4] if block=='ttm_q3' else columns[-3]
            targets=[('Income Statement',row,key,period) for row,key in [('Revenue','revenue'),('Operating Profit','operating'),('Net Profit','net')]]
        elif block in ('eps_a','eps_b'):
            t=table('Data Per Share')
            if not any(EPS_NOTE in n for n in t.get('Notes',[])): raise SourceError('provider common/weighted EPS definition missing')
            targets=[('Data Per Share','Earnings Per Share (EPS)','eps',p) for p in (columns[-4:-2] if block=='eps_a' else columns[-2:])]
        elif block=='balance':
            t=table('Data Per Share')
            if not any(BVPS_NOTE in n for n in t.get('Notes',[])): raise SourceError('provider BVPS basis missing')
            targets=[('Financial Position',"Total Shareholders' Equity",'equity',latest),
                     ('Data Per Share','Book-value Per Share (BVPS) ','tangible_bvps',latest)]
        elif block=='quality':targets=[('Income Statement','Profit before Income Tax','pretax',latest)]
        elif block=='cashflow':targets=[('Cash Flows','Cash Flow from Operating Activities','cfo',latest),
                                       ('Cash Flows','Cash Flow from Investing Activities','investing_cf',latest)]
        for table_name,row,key,period in targets:
            t=table(table_name);matching=[s for s in t['Series'] if s['name']==row and s['unit'] in ('KRW million','KRW')]
            if len(matching)!=1 or period not in t['Columns']: raise SourceError('unique provider financial row/period required')
            s=matching[0];idx=t['Columns'].index(period); value=s['Data'][idx]['str']
            if value is None:raise SourceError('provider null is unavailable, never zero')
            gi=groups.index(quarterly);ti=quarterly['Data'].index(t);si=t['Series'].index(s)
            locator=f'json_scalar:/LevelZeroItems/{gi}/Data/{ti}/Series/{si}/Data/{idx}/str'
            basis=('provider_weighted_common_EPS_net_income_attribution_unverified' if key=='eps'
                else 'provider_tangible_equity_per_share_not_standard_PB' if key=='tangible_bvps'
                else 'provider_cashflow_quarter_vs_YTD_unverified' if key in ('cfo','investing_cf')
                else 'provider_reported_quarterly; consolidation/attribution/audit_basis_not_cross_checked_against_filing' if key in ('revenue','operating','net')
                else 'issuer_linked_provider_consolidation_attribution_unverified')
            records.append(_record(value,locator,_definition(asset,key,'KRW_per_share' if s['unit']=='KRW' else 'KRW_million',
                period[:4]+'Q'+period[-2],'SK hynix; issuer-linked Euroland quarterly statement' if key in ('revenue','operating','net','pretax')
                else 'SK hynix issuer-linked Euroland financial table',basis),key))
        limits=['공식 IR 연결 제공자 자료. 연결/별도·이익 귀속·원공시·일회성 손익의 검증은 미완료다.']
    elif contract=='semiconductor_hn_v1':
        from .discovery_contracts import json_document
        doc=json_document(response)
        if doc.get('type')!='comment' or doc.get('dead') or doc.get('deleted') or str(doc.get('id'))!=candidate['identity']:
            raise SourceError('unavailable/wrong original community comment')
        text=_visible_html(doc['text'])
        pattern=r'\bSamsung\b|삼성' if asset=='SAMSUNG' else r'\b(?:SK\s*)?hynix\b|하이닉스'
        if not re.search(pattern,text,re.I) or not re.search(r'HBM|memory|DRAM|NAND|valuat|earnings|capex|메모리',text,re.I):
            raise SourceError('opened comment not about this company/semiconductor investment')
        if len(text)>1100 or re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',text): raise SourceError('community retention/personal-data limit')
        if type(doc['time']) is not int:raise SourceError('community date missing')
        at=datetime.fromtimestamp(doc['time'],timezone.utc).isoformat();published=at
        records=[_record(text,'json_html:/text',_definition(asset,'community','text',at,
            'purpose_sampled_Hacker_News_comment','utterance_not_verified_financial_fact'),'관측된 기업 토론')]
        limits=['실제 발언 존재만 확인한다. 표본 대표성·내용·투자 결론은 미확인이다.']
    else:raise SourceError('unsupported narrow semiconductor contract')
    if not records:raise SourceError('no supported evidence in opened document')
    result=dict(observed_at=at,published_at=published,valid_as_of=at,records=records,
        complete=complete,limitations=limits)
    if not complete:
        expected=('ordinary_eps','investment_commitments','market_risk') if contract=='semiconductor_samsung_statement_v1' else ('price_mix','hbm_statement','foundry_cost')
        found={r['definition']['measure'].removeprefix('SEMI_'+asset+'_').lower() for r in records}
        result['missing_fields']=[key for key in expected if key not in found]
    return result


def community_check(candidate, factual):
    """Only exact company/quarter/unit facts can use the existing claim rule."""
    asset=candidate['asset_id']; r=candidate['verified']['records'][0]
    name='Samsung' if asset=='SAMSUNG' else 'SK hynix'
    check=dict(asset_ids=[asset],narrative_evidence_id=r['evidence_id'],source_id=candidate['source_id'],
        factual_claim=None,verification='unverified',evidence_ids=[],
        reason='발언을 사실로 승격하지 않는다. 같은 기업·기간·정의의 원자료가 있어야 좁은 사실 주장만 검증할 수 있다.')
    match=re.search(re.escape(name)+r' (\d{4}Q[1-4]) revenue was KRW (\d+(?:\.\d+)?) million\.',r['quote'],re.I)
    if not match:
        # Primary explanations provide context for technical narratives, not
        # deterministic proof of technology leadership or a customer's ROI.
        context=[v['evidence_id'] for c,v in factual if c['source_type']=='primary'
            and v['definition']['measure'] in ('SEMI_'+asset+'_HBM_STATEMENT','SEMI_'+asset+'_PRICE_MIX')]
        if context and re.search(r'HBM|memory|메모리',r['quote'],re.I):
            check.update(evidence_ids=context,reason='회사 공식 설명의 가격·제품 구성·HBM 구절을 맥락으로 대조한다. 기술격차·공급 병목·고객 인증은 별도 원자료가 없어 미확인이다.')
        return check
    check['factual_claim']=match[0]
    compatible=[v for c,v in factual if c['source_type']=='primary'
        and v['definition']['measure']=='SEMI_'+asset+'_REVENUE' and v['definition']['period']==match[1]
        and v['definition']['unit']=='KRW_million' and v['definition']['currency']=='KRW'
        and v['definition']['adjustment']=='K_IFRS_reported']
    if len(compatible)==1:
        value=compatible[0]
        check.update(evidence_ids=[value['evidence_id']],rule='numeric_equality_v1',
            assertion={**value['definition'],'evidence_id':value['evidence_id'],'expected_value':match[2]},
            reason='기업·분기·통화·연결 매출의 정의가 같은 공식 재무제표와 이 수치 문장만 대조한다. 발언 전체의 진실·투자 논리는 미확인이다.')
    return check


def _eligible(case, cutoff):
    sources={s.id:s for s in case.sources}; out=[]
    for e in case.evidence:
        p=e.provenance;s=sources[e.source_id]
        if (e.kind=='observed_narrative' or not p or p.match_status!='matched' or p.freshness!='fresh'
                or not s.provenance or s.provenance.status!='available' or _time(s.provenance.retrieved_at)>cutoff):continue
        if any(_time(t)>cutoff for t in (s.provenance.published_at,s.provenance.observed_at,s.provenance.valid_as_of) if t):continue
        out.append(e)
    return out


def observations(case, cutoff):
    """Use separate issuer/provider namespaces; never overwrite contradictions."""
    rows=_eligible(case,cutoff)
    out={a:{} for a in COMPANIES}
    for e in rows:
        d=e.provenance.definition
        for asset in COMPANIES:
            prefix='SEMI_'+asset+'_'
            if asset in e.asset_ids and d['measure'].startswith(prefix):
                key=(d['measure'].removeprefix(prefix).lower(),d['period'])
                out[asset].setdefault(key,[]).append(e)
    # The prior Korean collector already fetched two SK quarters; reuse them
    # under their original evidence IDs rather than duplicating the facts.
    for e in rows:
        d=e.provenance.definition
        prefix='SK_HYNIX_'
        if 'SK_HYNIX' not in e.asset_ids or d['measure'] not in (prefix+'REVENUE',prefix+'OPERATING_PROFIT',prefix+'NET_PROFIT'):continue
        key=({'REVENUE':'revenue','OPERATING_PROFIT':'operating','NET_PROFIT':'net'}[d['measure'].removeprefix(prefix)],d['period'])
        out['SK_HYNIX'].setdefault(key,[]).append(e)
    return out


def calculate(case, cutoff, require_dates=False):
    from .models import MetricResult
    from .source_pipeline import _digest
    rows=observations(case,cutoff);out=[]
    if require_dates:
        from .source_pipeline import dated_evidence
        rows={asset:{key:[e for e in values if dated_evidence(e)] for key,values in series.items()}
            for asset,series in rows.items()}
    def one(asset,key,period):
        found=rows[asset].get((key,period),[])
        return found[0] if len(found)==1 else None
    def metric(asset,key,label,unit,values,operation,limitation):
        if not values or any(e is None or e.value is None for e in values):return
        if any(e.currency!='KRW' for e in values):return
        with localcontext() as ctx:
            ctx.prec=50
            value=operation([e.value for e in values])
        if value is None or not value.is_finite():return
        refs=tuple(e.id for e in values)
        out.append(MetricResult('CALC_SEMI_'+asset+'_'+key,label,value,unit,'semiconductor_'+key.lower()+'_v1',
            refs,(asset,),(limitation,'수치는 원문 전사 또는 명시한 산술이다. 경제적 해석·미래 수익·원공시의 진실을 자동 보증하지 않는다.')))
    for asset,(name,_,_) in COMPANIES.items():
        periods=sorted({p for key,p in rows[asset] if key=='revenue' and re.fullmatch(r'\d{4}Q[1-4]',p)})
        latest=periods[-1] if periods else None
        # No year/month is hardcoded in the arithmetic. All four periods must
        # be consecutive and the last period must agree with current EPS data.
        for p in periods:
            rev,op=one(asset,'revenue',p),one(asset,'operating',p)
            if rev and op and rev.unit==op.unit=='KRW_million' and all(rev.provenance.definition[k]==op.provenance.definition[k] for k in ('scope','adjustment')):
                metric(asset,'MARGIN_'+p,name+' '+p+' 영업이익률','percent',[op,rev],
                    lambda v:v[0]/v[1]*100 if v[1]>0 else None,'해당 기간의 표시 영업이익/매출. 서로 다른 이익 귀속·기업 경쟁력의 증명이 아니다.')
        if latest:
            for field,label in [('revenue','매출'),('operating','영업이익')]:
                current=one(asset,field,latest);previous=one(asset,field,str(int(latest[:4])-1)+latest[4:])
                if current and previous and current.unit==previous.unit=='KRW_million' and all(current.provenance.definition[k]==previous.provenance.definition[k] for k in ('scope','adjustment','currency')):
                    metric(asset,field.upper()+'_YOY',name+' '+latest+' '+label+' 전년동기 대비','percent',[current,previous],
                        lambda v:(v[0]/v[1]-1)*100 if v[1]>0 else None,'같은 기업·연결/제공자 정의·분기를 비교한다. 작은 전년 이익 기저와 업황 효과도 고려한다.')
            y=int(latest[:4]);q=int(latest[-1])
            for field,label in [('revenue','매출'),('operating','영업이익'),('net','순이익')]:
                if asset=='SAMSUNG' and q==2:
                    inputs=[one(asset,field,str(y-1)),one(asset,field,f'{y}H1'),one(asset,field,f'{y-1}H1')]
                    operation=lambda v:v[0]+v[1]-v[2]
                else:
                    serial=y*4+q-1
                    ps=[f'{s//4}Q{s%4+1}' for s in range(serial-3,serial+1)]
                    inputs=[one(asset,field,p) for p in ps];operation=sum
                if any(e is None or e.unit!='KRW_million' for e in inputs):continue
                if len({(e.provenance.definition['scope'],e.provenance.definition['adjustment']) for e in inputs})!=1:continue
                metric(asset,'TTM_'+field.upper(),name+' 최근 12개월 '+label,'KRW_million',inputs,operation,
                    '전년 연간+현재 누적−전년 같은 누적 또는 연속 네 분기를 합산한다. SK하이닉스 제공자의 연결/이익 귀속·원공시 대조는 미완료다.'
                    if asset=='SK_HYNIX' else '공식 연결 재무제표의 전년 연간+현재 반기−전년 반기. 순이익은 비지배지분 포함 전체 연결 이익이다.')
        if asset=='SAMSUNG':
            halves=sorted({p for key,p in rows[asset] if key=='cfo' and re.fullmatch(r'\d{4}H1',p)})
            if halves:
                last=halves[-1];cfo=one(asset,'cfo',last);ppe=one(asset,'ppe_cash',last)
                if cfo and ppe and cfo.unit==ppe.unit=='KRW_million' and ppe.value is not None and ppe.value<=0:
                    metric(asset,'CFO_AFTER_PPE',name+' '+last+' 설비 현금지출을 뺀 영업현금흐름','KRW_million',[cfo,ppe],
                        lambda v:v[0]+v[1],'CFO−유형자산 취득 현금지출. 무형자산·기업 인수·리스 등은 포함하지 않아 회사의 전체 free cash flow나 경영진 CAPEX와 같지 않다.')
        elif latest:
            op=one(asset,'operating',latest);pretax=one(asset,'pretax',latest);net=one(asset,'net',latest)
            if (op and pretax and net and op.unit==pretax.unit==net.unit=='KRW_million'
                    and len({e.provenance.definition['scope'] for e in (op,pretax,net)})==1):
                metric(asset,'NONOPERATING_RESIDUAL',name+' '+latest+' 세전이익−영업이익','KRW_million',[pretax,op],lambda v:v[0]-v[1],
                    '제공자 표의 본업 외 손익 순잔여분이다. 환율·파생·평가·일회성 등 세부 원인은 원공시가 없어서 확정하지 않는다.')
                metric(asset,'NONOPERATING_SHARE',name+' '+latest+' 세전이익 중 영업이익 외 잔여 비중','percent',[pretax,op],
                    lambda v:(v[0]-v[1])/v[0]*100 if v[0]>0 else None,'세전−영업 잔여/세전이익. 이 비중을 영구 이익·현금 회수·기업 경쟁력으로 해석하지 않는다.')
                metric(asset,'IMPLIED_TAX',name+' '+latest+' 세전이익−순이익','KRW_million',[pretax,net],lambda v:v[0]-v[1],
                    '같은 제공자 표의 차액이며 조정 항목/연결/세금 정의를 원공시로 검증하지 못했다.')
        eps=sorted({p for key,p in rows[asset] if key=='eps'})
        eps_inputs=[];formula=None
        halves=[p for p in eps if re.fullmatch(r'\d{4}H1',p)]
        if halves:
            last=max(halves);y=int(last[:4])
            eps_inputs=[one(asset,'eps',str(y-1)),one(asset,'eps',last),one(asset,'eps',f'{y-1}H1')]
            formula=lambda v:v[0]+v[1]-v[2]
            period=f'{y-1}-07-01..{y}-06-30'
        else:
            quarters=[p for p in eps if re.fullmatch(r'\d{4}Q[1-4]',p)]
            if len(quarters)>=4:
                last=quarters[-4:];serial=lambda p:int(p[:4])*4+int(p[-1])-1
                if any(serial(b)-serial(a)!=1 for a,b in zip(last,last[1:])):continue
                if latest and last[-1]!=latest:continue
                eps_inputs=[one(asset,'eps',p) for p in last];formula=sum;period='..'.join((last[0],last[-1]))
        if not formula or any(e is None for e in eps_inputs):continue
        definitions=[e.provenance.definition for e in eps_inputs]
        if any(d['unit']!='KRW_per_share' or d['currency']!='KRW' for d in definitions):continue
        if len({(d['scope'],d['adjustment']) for d in definitions})!=1:continue
        basis=definitions[0]['adjustment']
        if basis not in ('K_IFRS_basic_common_EPS','provider_weighted_common_EPS_net_income_attribution_unverified'):continue
        if asset=='SAMSUNG' and not any(key=='ordinary_eps' for key,p in rows[asset]):continue
        provisional=basis!='K_IFRS_basic_common_EPS'
        limitation=('제공자가 명시한 가중평균 보통주 EPS의 산술값. 연결/이익 귀속과 원공시가 미검증이므로 잠정 배수이며 확정 동일 기준 P/E 비교에 사용하지 않는다.'
            if provisional else '공식 연결 기본 보통주 EPS: 전년 연간+현재 반기−전년 반기. 기간별 가중평균 주식 수의 차이가 있어 현재 주식 수로 재작성한 EPS와 다를 수 있다.')
        metric(asset,'TTM_EPS',name+' '+period+' 최근 12개월 EPS'+(' (제공자 기준)' if provisional else ''),
            'KRW_per_share',eps_inputs,formula,limitation)
        prices=[e for (key,p),items in rows[asset].items() if key=='close' for e in items]
        if len(prices)!=1 or prices[0].unit!='KRW_per_share':continue
        inputs=[prices[0],*eps_inputs]
        metric(asset,'PE',name+' 표시 종가/최근 12개월 EPS'+(' (잠정)' if provisional else ''),'ratio',inputs,
            lambda v:v[0]/formula(v[1:]) if formula(v[1:])>0 and v[0]>0 else None,limitation+' 가격은 국내 제공자 표시 종가; KRX 직접 대조·수정 여부 미확인.')
        metric(asset,'EY',name+' 최근 12개월 EPS/표시 종가','percent',inputs,
            lambda v:formula(v[1:])/v[0]*100 if formula(v[1:])>0 and v[0]>0 else None,
            limitation+' 이익수익률은 배당·확정 투자 수익률이 아니다.')
    return tuple(out)


def audit(run):
    """Reviewable inputs/gaps/cross-checks and judgment, with no invented score."""
    rows=observations(run.case,run.cutoff);sources={s.id:s for s in run.case.sources}
    data=dict(method_version=VERSION,judgment='현재 데이터로 우열 판단 어려움',
        comparison_eligible=False,companies={},cross_checks=[],
        reasoning='같은 산술 공식이어도 원공시·연결 범위·이익 귀속·현재 가격·이익 지속성을 모두 검증한 것은 아니다. 배수 하나만으로 미래 위험 대비 수익의 우위를 결정하지 않는다.')
    for asset,(name,code,corp) in COMPANIES.items():
        if asset not in {m['id'] for m in run.input['methods']}:continue
        metrics=[m for m in run.result.metrics if m.id.startswith('CALC_SEMI_'+asset+'_')]
        data['companies'][asset]=dict(name=name,ordinary_code=code,dart_corp_code=corp,
            numeric_evidence_ids=[e.id for group in rows[asset].values() for e in group if e.value is not None],
            calculation_ids=[m.id for m in metrics],
            gaps=['현재 상장/유통 주식 수와 우선주/지배주주 자본 귀속을 맞춘 시가총액·일반 P/B',
                  'DART 원공시 본문·정정판 교차 검증','정의된 forward consensus·forecast date·revision'],
            price_evidence_ids=[e.id for (key,p),items in rows[asset].items() if key=='close' for e in items],
            price_type='provider_displayed_market_close',adjusted_price_status='not_explicitly_stated',
            filing_registration_ids=[e.id for (key,p),items in rows[asset].items() if key=='filing_registered' for e in items])
        if asset=='SK_HYNIX':
            data['companies'][asset]['gaps'].extend(['연결/별도·순이익의 지배주주 귀속·영업외 손익 세부',
                'CFO의 단일 분기/누적 기간과 유형자산 CAPEX','현재 HBM 실적·경영진 guidance의 접근 가능한 공식 원문'])
        # Cross-check primary Samsung quarterly amounts with the old release.
        if asset=='SAMSUNG':
            for key,old in [('revenue','SAMSUNG_REVENUE'),('operating','SAMSUNG_OPERATING_PROFIT')]:
                primary=[e for (k,p),group in rows[asset].items() if k==key and re.fullmatch(r'\d{4}Q[1-4]',p)
                         for e in group if sources[e.source_id].type.value=='primary']
                if not primary:continue
                latest=max(primary,key=lambda e:e.period)
                other=[e for e in _eligible(run.case,run.cutoff) if e.provenance.definition['measure']==old
                       and e.provenance.definition['period']==f'{latest.period[:4]}-{int(latest.period[-1])*3:02d}-'+str(calendar.monthrange(int(latest.period[:4]),int(latest.period[-1])*3)[1])
                       and e.unit=='KRW_trillion' and e.currency=='KRW'
                       and sources[e.source_id].type.value=='primary']
                if len(other)!=1 or latest.value is None or other[0].value is None:continue
                with localcontext() as ctx:
                    ctx.prec=50;diff=latest.value-other[0].value*1000000
                data['cross_checks'].append(dict(company=asset,field=key,period=latest.period,
                    evidence_ids=[latest.id,other[0].id],difference_KRW_million=str(diff),
                    status='consistent_with_release_rounding' if abs(diff)<=Decimal('50000') else 'mismatch',
                    reason='발표문의 소수점 한 자리 조 원 반올림 허용범위로 대조했다. 차이가 이 범위를 넘으면 일치로 처리하지 않는다.'))
    if 'SK_HYNIX' in data['companies']:
        data['cross_checks'].append(dict(company='SK_HYNIX',status='original_filing_unavailable',evidence_ids=[],
            reason='동일 Euroland 응답의 재추출은 독립적 교차 확인이 아니다. DART 원공시 대조는 미완료다.'))
    return data
