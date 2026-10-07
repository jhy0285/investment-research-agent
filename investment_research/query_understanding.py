"""Explicit question details, without financial data or inferred user finances.

Every extracted detail retains its text and position in the user's question.
Bond maturity, interest-rate duration and the user's holding period are distinct.
This bounded parser does not turn a phrase into portfolio input or a data source.
"""
from dataclasses import asdict, dataclass
import re

UNDERSTANDING_VERSION = 'explicit_query_constraints_v1'
COUNTRIES = {'한국':'KR','대한민국':'KR','원화':'KR','미국':'US','일본':'JP',
             '독일':'DE','영국':'GB','중국':'CN','프랑스':'FR'}
COUNTRY_PATTERN = '|'.join(COUNTRIES)
REGION_PATTERN = r'서울(?:시)?|수도권|경기(?:도)?|인천(?:시)?|동탄|부산(?:시)?|대구(?:시)?|대전(?:시)?|광주(?:시)?|울산(?:시)?|세종(?:시)?|제주(?:도)?|분당|판교|강남|뉴욕|런던|도쿄|[가-힣]{2,12}(?:구|동|읍|면)'
ASSET_CLASSES = {'equity':'equity','equity_index':'equity','equity_sector':'equity',
                 'equity_strategy':'equity','etf':'etf','crypto':'crypto',
                 'natural_gas':'commodity','commodity':'commodity','bond':'bond',
                 'real_estate':'real_estate','cash':'cash','unresolved':'unknown'}


@dataclass(frozen=True)
class Term:
    value: str | None
    unit: str | None
    descriptor: str | None
    raw_text: str


def subject_details(label, family, raw):
    """Extract only details attached to this subject, not a different alternative."""
    country=next((code for name,code in COUNTRIES.items() if name in raw),None)
    if country is None:
        if re.search(r'\b(?:US|U\.S\.)\b|American',raw,re.I):country='US'
        elif re.search(r'\bKorean\b',raw,re.I):country='KR'
    regions=tuple(dict.fromkeys(m.group() for m in re.finditer(REGION_PATTERN,raw))) if family=='real_estate' else ()
    if regions and country is None:
        countries={ {'뉴욕':'US','런던':'GB','도쿄':'JP'}.get(r,'KR') for r in regions }
        if len(countries)==1:country=countries.pop()  # Place identity, not user residence.
    maturity=None;duration=None
    if family=='bond':
        match=re.search(r'(\d+(?:\.\d+)?)\s*(년|개월)(?:물|\s*만기)?',raw)
        if match:maturity=Term(match[1],'years' if match[2]=='년' else 'months',None,match.group())
        descriptor=next((name for name in ('단기','중기','장기') if name in raw),None)
        if descriptor:duration=Term(None,None,{'단기':'short','중기':'intermediate','장기':'long'}[descriptor],descriptor)
    strategies=tuple(name for pattern,name in ((r'배당|dividend','dividend'),(r'성장|growth','growth'),
                       (r'가치|value','value'),(r'레버리지|leveraged','leverage'),(r'환헤지|hedged','currency_hedged'))
                     if re.search(pattern,raw,re.I))
    return dict(asset_class=ASSET_CLASSES.get(family,'unknown'),country=country,regions=regions,
                maturity=maturity,duration=duration,strategies=strategies,raw_text=raw)


def bond_label(raw, details):
    country=next((name for name in COUNTRIES if name in raw),None)
    term=details['maturity'];duration=details['duration']
    descriptor={'short':'단기','intermediate':'중기','long':'장기'}.get(duration.descriptor) if duration else None
    tenor=term.value+('년' if term.unit=='years' else '개월') if term else None
    return ' '.join(x for x in (country,descriptor,tenor,'국채') if x)


def _details(question, rules):
    details=[]
    for kind,pattern in rules:
        for match in re.finditer(pattern,question,re.I):
            details.append(dict(kind=kind,raw_text=match.group(),span=[match.start(),match.end()]))
    return sorted(details,key=lambda d:(d['span'][0],d['kind']))


def understand_question(question, subjects, modes, compare_requested):
    purposes=_details(question,(
        ('new_capital_allocation',r'신규\s*자금|새\s*자금|new\s+capital'),
        ('investment_economics',r'투자\s*관점|investment perspective'),
        ('residential_use',r'실거주|거주\s*목적'),
        ('home_purchase',r'주택\s*(?:구입|매수)|집\s*(?:구입|매수|살)'),
        ('retirement',r'노후|은퇴|retirement'),('emergency_reserve',r'비상\s*자금'),
    ))
    time_context=_details(question,(
        ('current',r'지금|현재|오늘|요즘|\bnow\b|\bcurrent(?:ly)?\b|\btoday\b'),
        ('recent',r'최근|recent(?:ly)?'),
        ('calendar_reference',r'올해|내년|작년|지난해'),
        ('dated_reference',r'\d{4}[-./]\d{1,2}[-./]\d{1,2}(?:\s*(?:기준|당시))?|\d{4}년\s*\d{1,2}월\s*\d{1,2}일(?:\s*(?:기준|당시))?'),
    ))
    constraints=_details(question,(
        ('holding_period',r'(?:투자\s*기간|보유\s*기간)\s*(?:은|는|:|약)?\s*\d+(?:\.\d+)?\s*(?:년|개월)|\d+(?:\.\d+)?\s*(?:년|개월)(?:간|\s*동안)\s*(?:투자|보유)'),
        ('future_cash_need',r'\d+(?:\.\d+)?\s*(?:년|개월)\s*(?:뒤|후).{0,35}?(?:주택\s*구입|집\s*살|자금\s*필요|써야|사용해야|학자금)'),
        ('investment_budget',r'(?:신규\s*자금|투자\s*금액|예산)\s*(?:은|는|:|약)?\s*[\d,]+(?:\.\d+)?\s*(?:억\s*원|만\s*원|원|달러)'),
        ('debt_constraint',r'(?:대출|부채)(?:은|는|이|가)?\s*(?:없(?:다|어|음|이)?|없이)|(?:대출|부채)\s*[\d,]+\s*(?:억\s*원|만\s*원|원)'),
        ('risk_constraint',r'원금\s*보전|원금\s*손실.{0,12}?(?:싫|안|불가)|레버리지\s*없이'),
        ('currency_constraint',r'원화\s*기준|KRW\s*(?:base|기준)|환헤지\s*(?:없이|해서|필요|원해)?'),
        ('account_constraint',r'\bISA\b|\bIRP\b|연금저축|일반\s*계좌'),
        ('interest_rate_duration',r'(?:듀레이션|duration)\s*(?:은|는|:|약)?\s*\d+(?:\.\d+)?\s*(?:년|years?)'),
        ('tax_residence',r'(?:한국|대한민국)\s*(?:세법상\s*)?거주자'),
    ))
    for constraint in constraints:
        if constraint['kind'] in ('holding_period','future_cash_need','interest_rate_duration'):
            term=re.search(r'(\d+(?:\.\d+)?)\s*(년|개월|years?)',constraint['raw_text'])
            if term:constraint.update(value=term[1],unit='months' if term[2]=='개월' else 'years')
        elif constraint['kind']=='investment_budget':
            amount=re.search(r'([\d,]+(?:\.\d+)?)\s*(억\s*원|만\s*원|원|달러)',constraint['raw_text'])
            if amount:constraint.update(value=amount[1],unit=re.sub(r'\s','',amount[2]))
    data_limits=[dict(kind=c['kind'],raw_text=c['raw_text'],status='unavailable',
                     reason='해당 수치의 실제 계약 duration 자료가 없다. 채권 만기로 대체하지 않는다.')
                 for c in constraints if c['kind']=='interest_rate_duration']
    data_limits.extend(dict(kind=c['kind'],raw_text=c['raw_text'],status='unavailable',
                            reason='지정한 날짜의 당시 이용 가능 판본을 자동 선택하는 ask 실행은 미지원이다. 현재 자료로 당시 판단을 대체하지 않는다.')
                       for c in time_context if c['kind']=='dated_reference')
    return dict(schema_version='query-understanding-v1',method_version=UNDERSTANDING_VERSION,
                original_question=question,intent=list(modes),
                scope='broad_cross_asset' if 'opportunity_scan' in modes else 'specified_subjects',
                assets_or_alternatives=[asdict(s) for s in subjects],requested_comparison=compare_requested,
                investment_purpose=purposes,time_context=time_context,user_constraints=constraints,data_limits=data_limits,
                strategies=_details(question,(('dividend',r'배당\s*투자|dividend invest(?:ing|ment)'),
                                              ('growth',r'성장주|growth stocks'),('value',r'가치주|value stocks'))),
                interpretation_limits=['명시 구절만 구조화한다. 금액·투자기간을 portfolio 입력으로 추정하지 않는다.',
                                       '채권 만기·금리 민감도·사용자 보유 기간을 서로 대체하지 않는다.',
                                       '지원되지 않는 조건은 보존하고 근거 부족을 표시한다.'])


def constraint_labels(subject):
    """Human-readable scope without internal research architecture vocabulary."""
    details=[]
    if subject.get('country'):
        country={'KR':'한국','US':'미국','JP':'일본','DE':'독일','GB':'영국','CN':'중국','FR':'프랑스'}.get(subject['country'],subject['country'])
        details.append('국가: '+country)
    if subject.get('regions'):details.append('지역: '+' / '.join(subject['regions']))
    if subject.get('maturity'):details.append('만기: '+subject['maturity']['raw_text'])
    if subject.get('duration'):details.append('기간 특성: '+subject['duration']['raw_text'])
    if subject.get('strategies'):details.append('전략: '+' / '.join(subject['strategies']))
    return details
