"""Presentation only: explain existing, checked research without new decisions.

No acquisition, financial calculation, claim promotion or candidate selection
lives here. Historical report bytes are rendered by the legacy report method.
"""
from dataclasses import replace
from decimal import Decimal
import re
from zoneinfo import ZoneInfo

from .routing import ResearchMode


# These are educational explanations, not claims about today's market.
# Longest aliases win (forward P/E must not be explained as trailing P/E).
TERMS = (
    (r'forward\s*P/E|forward\s*PER|Forward P/E', 'Forward P/E는 앞으로 벌 것으로 예상하는 이익에 비해 현재 주가가 몇 배인지 보는 값이다. 낮아 보여도 예상 이익이 실제로 나오지 않으면 싸다는 판단이 틀릴 수 있다.'),
    (r'trailing\s*P/E|trailing\s*PER', 'Trailing P/E는 이미 기록된 과거 이익에 비해 현재 주가가 몇 배인지 보는 값이다. 과거 이익이 일회성이거나 업황의 정점에서 나온 것이라면 낮은 배수가 지속적인 저평가를 뜻하지 않는다.'),
    (r'(?<![\w/])P/E(?!\w)|(?<!\w)PER(?!\w)|이익배수', 'P/E 또는 PER은 주가를 한 주당 이익으로 나눈 값이다. 같은 이익을 더 싸게 사는지 볼 수 있지만, 어떤 기간의 이익인지와 그 이익이 계속 나올지가 더 중요하다.'),
    (r'valuation|밸류에이션', 'Valuation은 현재 가격이 회사가 버는 돈이나 자산가치에 비해 비싼지 싼지를 살펴보는 것이다. 좋은 회사라도 좋은 미래를 이미 비싸게 지불하면 투자 수익은 기대보다 낮을 수 있다.'),
    (r'CAPEX', 'CAPEX는 공장·설비·데이터센터처럼 미래 생산능력을 늘리기 위해 쓰는 큰 투자비용이다. 수요가 강하면 매출 기회를 늘리지만, 수요가 예상보다 약하면 투자비 회수가 늦어지고 회사에 남는 현금이 줄 수 있다.'),
    (r'capacity|캐파', 'Capacity, 즉 캐파는 공장이 얼마나 많이 생산할 수 있는지 나타내는 생산능력이다. 증설은 수요가 강할 때 매출을 늘릴 기회지만 업황이 꺾이면 공급과잉 위험을 키울 수 있다.'),
    (r'operating margin|영업이익률|마진', '영업이익률은 매출 중 본업의 비용을 내고 얼마나 남겼는지를 보여준다. 매출이 늘어도 이 비율이 떨어진다면 비용 부담이나 가격 경쟁 때문에 이익이 기대만큼 늘지 않을 수 있다.'),
    (r'free cash flow|잉여현금흐름|(?<!\w)FCF(?!\w)', 'Free Cash Flow, 즉 잉여현금흐름은 사업에 필요한 투자비용을 쓰고도 실제로 남는 현금이다. 회계상 이익이 좋아도 현금이 남지 않으면 주주에게 돌아갈 돈은 제한될 수 있다. 실제 계산에서 어떤 투자 지출을 뺐는지는 따로 확인해야 한다.'),
    (r'(?<!\w)EPS(?!\w)', 'EPS는 회사 이익을 주식 한 주 기준으로 나눈 값이다. 주가와 같은 단위로 이익을 비교할 수 있지만 보통주 귀속·주식 수·실적 기간이 다르면 서로 다른 EPS를 그대로 비교할 수 없다.'),
    (r'(?<!\w)TTM(?!\w)', 'TTM은 최근 열두 달을 뜻한다. 한 분기가 유난히 좋았다고 그 이익을 일 년 내내 반복한다고 가정하지 않고 실제 여러 분기를 합쳐 보는 기준이다.'),
    (r'(?<!\w)FY1(?!\w)', 'FY1은 예상하는 다음 회계연도다. 오늘부터 열두 달의 예상 이익과 기간이 다를 수 있어 두 배수를 같은 가치평가 기준으로 합치면 안 된다.'),
    (r'컨센서스|consensus', '컨센서스는 여러 분석가의 예상치를 모은 것이다. 회사가 약속한 이익이나 확정 실적이 아니므로 이후 예상치 수정과 실제 실적을 함께 확인해야 한다.'),
    (r'earnings revision|revision|리비전', 'Earnings revision은 앞으로의 이익 예상치를 올리거나 내리는 수정이다. 상향은 기대 개선의 단서지만 이미 주가가 더 빠르게 올랐다면 투자 가격의 매력은 별도로 봐야 한다.'),
    (r'momentum|모멘텀', 'Momentum, 즉 모멘텀은 최근 가격이 어느 방향으로 움직이고 있는지 보는 것이다. 실적 개선과 함께 나타나면 재평가의 단서가 될 수 있지만 가격만 급등하면 기대가 먼저 앞서갔을 수 있다.'),
    (r'contango|콘탱고', 'Contango는 뒤에 만기가 오는 선물이 더 비싼 구조다. 선물을 계속 갈아타는 상품은 더 비싼 다음 계약으로 옮기면서 보유에 불리한 조건을 겪을 수 있다. 지금 계약 간 가격차가 앞으로의 실제 손실과 같다는 뜻은 아니다.'),
    (r'backwardation|백워데이션', 'Backwardation은 가까운 선물이 먼 선물보다 비싼 구조다. 당장 필요한 물건의 수요·공급이 빡빡하다는 단서일 수 있고 선물 교체 조건이 유리할 수도 있다. 미래 수익을 보장하지는 않는다.'),
    (r'(?<!\w)roll(?!\w)|롤 비용|선물 교체', 'Roll, 즉 선물 교체는 만기가 가까워진 계약을 팔고 다음 계약으로 갈아타는 것이다. 다음 계약의 가격과 상품 비용 때문에 원자재 가격의 방향이 맞아도 투자상품의 수익은 달라질 수 있다.'),
    (r'레버리지|leverage', '레버리지는 빌린 돈이나 파생계약으로 가격 움직임의 영향을 키우는 구조다. 이익과 손실이 모두 커질 수 있으며 하루 기준 배수를 맞추는 상품의 장기 수익은 단순한 배수가 아니다.'),
    (r'이익수익률|earnings yield', '이익수익률은 현재 주가에 비해 회사가 벌었거나 벌 것으로 예상하는 이익의 비율이다. 그 돈이 전부 배당으로 지급되는 것은 아니므로 채권 이자나 확정 투자수익률과 같게 보면 안 된다.'),
    (r'duration|듀레이션', '듀레이션은 금리 변화에 채권 가격이 얼마나 민감한지 보는 기준이다. 보통 이 기준이 큰 채권은 금리가 오를 때 가격 손실도 커질 수 있어, 높은 이자와 중도 매도 위험을 함께 봐야 한다.'),
    (r'(?<!\w)YTM(?!\w)|만기수익률', 'YTM, 즉 만기수익률은 매수가격과 계약상 이자·원금으로 계산한 채권의 수익률이다. 만기 전 매도 가격, 재투자, 비용·세금에 따라 투자자가 실제 얻는 수익은 달라질 수 있다.'),
    (r'실질금리|real.rate|(?<!\w)TIPS(?!\w)', '실질금리는 물가의 영향을 구분해 보는 이자 기준이다. TIPS는 물가에 따라 원금이 조정되는 미국 국채다. 이런 이자 대안이 높으면 이자를 주지 않는 금을 보유하기 위해 포기하는 수익도 커질 수 있다.'),
    (r'(?<!\w)NAV(?!\w)', 'NAV는 펀드가 가진 자산에서 비용·부채를 반영한 순자산을 한 주 기준으로 나눈 값이다. 거래소의 매매가격과 다를 수 있고, NAV 수익률이 기초자산의 현물 가격 변화와 같지는 않다.'),
    (r'total return|총수익', 'Total Return, 즉 총수익은 가격 변화 외에 해당 자료가 정한 배당·이자·담보 수익 등을 포함한 성과다. 무엇을 재투자하고 어떤 비용을 반영했는지 확인해야 실제 상품과 비교할 수 있다.'),
    (r'excess return', 'Excess Return은 선물 지수에서는 일반적으로 선물 가격 변화와 계약 교체 효과를 포함하고 담보 이자는 제외한 성과다. 주식에서 말하는 초과수익과 같은 뜻으로 쓰지 않는다.'),
    (r'spot return', 'Spot Return은 이 보고서에서 사용하는 지수의 가격 변화 부분이다. 선물 가격 기반 spot 지수와 실물 현물 가격은 다를 수 있으므로 이름만 보고 같은 수익으로 합치지 않는다.'),
    (r'collateral|담보 이자', '담보 이자는 선물 투자에 함께 보유하는 현금·단기채 등 담보 자산에서 얻는 이자다. 선물 가격이 그대로여도 상품 총수익에 영향을 줄 수 있지만 실제 기여는 별도 자료가 있어야 분리할 수 있다.'),
    (r'(?<!\w)ETF(?!\w)', 'ETF는 거래소에서 주식처럼 사고파는 펀드다. 이름이 같은 자산을 가리켜도 실제 보유자산·선물·환헤지·비용에 따라 결과가 달라지므로 상품 구조를 확인해야 한다.'),
    (r'(?<!\w)HBM\d*[A-Z]?(?!\w)', 'HBM은 여러 메모리 칩을 쌓아 데이터를 빠르게 주고받도록 만든 고대역폭 메모리다. AI 서버 수요가 매출 기회가 될 수 있지만 기술 설명과 실제 고객 판매·이익을 구분해야 한다.'),
    (r'(?<!\w)LNG(?!\w)', 'LNG는 배로 운반하기 위해 액화한 천연가스다. 수출이 늘면 미국 내 가스 수요를 늘릴 수 있지만 생산 증가와 시설 가동·재고도 함께 확인해야 한다.'),
    (r'working gas|dry gas|feedgas', 'Working gas는 사용할 수 있는 저장 가스이고, dry gas는 불순물 등을 제거한 판매 가능한 생산 가스다. Feedgas는 액화시설로 들어가는 원료 가스다. 재고·생산·수출은 서로 다른 자료라 한 숫자로 전체 수급을 대신할 수 없다.'),
    (r'(?<!\w)MMBtu(?!\w)|(?<!\w)Bcf(?!\w)|(?<!\w)MMcf(?!\w)', 'MMBtu는 가스가 내는 열량의 단위이고, Bcf와 MMcf는 각각 십억·백만 입방피트라는 부피 단위다. 가격은 열량당 얼마인지, 생산·수출·재고는 부피가 얼마인지 보므로 단위를 섞어 직접 비교하지 않는다.'),
    (r'narrative|내러티브', 'Narrative, 즉 내러티브는 사람들이 시장을 설명하며 믿는 이야기다. 새로운 투자 가설을 찾는 단서는 되지만 널리 퍼졌다는 사실이 내용의 정확성을 증명하지는 않는다.'),
    (r'기회비용|opportunity cost', '기회비용은 한 자산을 선택하면서 포기하는 다른 대안의 이익과 선택권이다. 주식의 성장 가능성을 볼 때도 채권 이자나 당장 쓸 수 있는 현금의 가치를 함께 봐야 한다.'),
)


ADDITIONAL_TERMS = (
    (r'funding|펀딩', 'Funding, 즉 펀딩비는 무기한 선물에서 매수·매도 쪽이 노출을 유지하며 주고받는 비용이다. 해당 시간 구간의 비율이지 연간 금리가 아니다. 한 거래소의 낮은 비용만으로 시장 전체의 빚을 낸 거래가 안전하다고 판단할 수 없다.'),
    (r'미결제약정|open interest', '미결제약정은 아직 종료되지 않은 파생계약의 규모다. 새로 들어온 투자금이나 순매수액과 다르고, 계약마다 매수자와 매도자가 함께 있으므로 규모만으로 가격 방향을 알 수 없다.'),
    (r'CFTC|managed money', 'CFTC는 미국 상품선물거래위원회이며, managed money는 선물 통계에서 펀드 등 운용자금으로 분류한 집단이다. 이들의 포지션은 일부 참여자의 노출이며 전체 수요나 앞으로의 가격을 확정하는 자료가 아니다.'),
    (r'(?<!\w)AUM(?!\w)', 'AUM은 펀드가 운용하는 자산의 총가치다. 가격이 올라서 늘 수도 있어 AUM 증가가 새 자금의 유입이나 금 보유량의 증가를 뜻하지는 않는다.'),
    (r'(?<!\w)P/B(?!\w)|(?<!\w)BVPS(?!\w)', 'P/B는 주가를 한 주당 장부가치(BVPS)로 나눈 값이다. 회사 장부에 기록된 자산·부채를 보는 기준으로, 무형자산을 뺀 값과 일반 장부가치를 섞으면 두 기업의 가격 비교가 잘못될 수 있다.'),
    (r'(?<!\w)CFO(?!\w)|(?<!\w)PP&E(?!\w)|(?<!\w)PPE(?!\w)', 'CFO는 본업에서 들어오고 나간 영업현금흐름이며, PP&E는 공장·설비 등 유형자산이다. 유형자산 취득 지출을 뺀 잔여 현금과 모든 투자 지출을 뺀 잉여현금흐름은 다를 수 있다.'),
    (r'risk/reward', 'Risk/reward는 감수하는 손실 위험에 비해 기대할 수 있는 보상이 충분한지 묻는 것이다. 성장 속도나 낮은 배수 하나로 정할 수 없고 나쁜 경우의 손실과 다른 투자 대안을 함께 봐야 한다.'),
)


def _family(method):
    """Display scope follows the existing method, including an ETF's exposure."""
    family=method['family'];identifier=method.get('id',method.get('asset_id'))
    if family.startswith('equity') or family=='strategy' or identifier=='ETF_SPY':return 'equity'
    if identifier in ('ETF_IBIT','ETF_ETHA'):return 'crypto'
    if family=='natural_gas':return 'commodity'
    return family


def _term_definition(index,definition,families,contract_leverage=False):
    if families is None:return definition  # Pinned v1-v3 keep their prose.
    corporate={0,1,2,4,5,6,7,8,9,10,11,12,18,28,38,39}
    if index in corporate and 'equity' not in families:return None
    if index in {24,25,26,29,30,31} and 'commodity' not in families:return None
    if index in {19,20} and 'bond' not in families:return None
    if index==3 and 'equity' not in families:
        return 'Valuation은 지금 지불하는 가격이 해당 자산의 수익 원천과 위험에 비해 합리적인지 살펴보는 것이다. 이 자산에서 실제로 확인할 수 있는 수요·현금흐름·보유 비용을 사용해야 하며 가격 상승만으로 싸거나 비싸다고 정할 수 없다.'
    if index==13 and 'equity' not in families:
        return 'Momentum, 즉 모멘텀은 최근 가격이 어느 방향으로 움직이는지 보는 것이다. 실제 수요 변화가 함께 확인되는지 봐야 하며 가격만 빠르게 오른다면 기대나 빚을 낸 거래가 앞서갔을 수 있다.'
    if index==17 and contract_leverage and 'crypto' in families:
        return '레버리지는 빌린 돈이나 파생계약으로 가격 움직임의 영향을 키우는 구조다. 이익과 손실이 모두 커지고, 가격이 불리하게 움직여 담보가 부족해지면 원치 않는 시점에 포지션이 강제로 정리될 수 있다. 계약 규모와 담보·청산 조건을 함께 봐야 한다.'
    if index==21:
        return '실질금리는 물가의 영향을 구분해 보는 이자 기준이다. TIPS는 물가에 따라 원금이 조정되는 미국 국채다. 자금 조달과 이자 대안을 이해하는 시장 환경이며 이 값 하나로 분석 대상의 가격 방향을 정할 수 없다.'
    if index==33:
        return '기회비용은 한 자산을 선택하면서 포기하는 다른 대안의 이익과 선택권이다. 불확실한 가격 상승을 기다리는 동안 받을 수 있는 이자와 필요할 때 바로 쓸 수 있는 현금의 가치도 함께 봐야 한다.'
    if index==37:
        return 'AUM은 펀드가 운용하는 자산의 총가치다. 보유자산 가격이 올라서 늘 수도 있어 AUM 증가와 새 투자금 유입은 구분해야 한다.'
    if index==40 and 'equity' not in families:
        return 'Risk/reward는 감수하는 손실 위험에 비해 기대할 수 있는 보상이 충분한지 묻는 것이다. 가격 상승 하나로 정할 수 없고 수익의 원천·나쁜 경우의 손실·다른 투자 대안을 함께 봐야 한다.'
    return definition


def explain_terms(lines,*,extended=False,korean_suffixes=False,families=None,section_families=None,contract_leverage=False):
    """Explain first use before a paragraph/table, never rewrite source quotes.

    Process complete Markdown blocks so explanatory prose cannot split a table.
    The detailed source appendix is intentionally excluded from this function.
    """
    seen=set();out=[];block=[];scope=families;scope_level=0
    def emit():
        nonlocal scope,scope_level
        if not block:return
        if families is not None and block[0].startswith('#'):
            heading=block[0];level=len(heading)-len(heading.lstrip('#'))
            if heading in (section_families or {}):scope=section_families[heading];scope_level=level
            elif level<=scope_level or level<=2:scope=families;scope_level=0
        text='\n'.join(block);definitions=[]
        for index,(pattern,definition) in enumerate(TERMS+(ADDITIONAL_TERMS if extended else ())):
            if korean_suffixes:
                # Korean particles (EPS를, PER로) are not part of the acronym.
                # Keep Latin/identifier boundaries so words like "proper"
                # cannot accidentally trigger the PER explanation.
                pattern=pattern.replace(r'(?<!\w)',r'(?<![A-Za-z0-9_])').replace(r'(?!\w)',r'(?![A-Za-z0-9_])')
            definition=_term_definition(index,definition,scope,contract_leverage)
            if definition and index not in seen and re.search(pattern,text,re.IGNORECASE):
                definitions.extend([definition,'']);seen.add(index)
                # A specific forward/trailing definition also explains P/E.
                if index in (0,1):seen.add(2)
        if block[0].startswith('#'):
            out.extend(block);out.append('');out.extend(definitions)
        else:out.extend(definitions);out.extend(block);out.append('')
        block.clear()
    for line in lines:
        if not line:emit()
        else:block.append(line)
    emit();return out


def _reader_format(run,lines):
    """v2 display corrections; v1 stays reproducible without rewriting it."""
    from .orchestrator_report import _current,_number,_text,_unit,_refs
    from .opportunity_report import _target
    evidence={_target(e.id):e for e in run.case.evidence if e.provenance and _current(run,e)}
    units={'USD_per_BTC':'달러/BTC', 'USD_per_ETH':'달러/ETH', 'USD':'달러',
           'fraction':'비율 (8시간 기준, 연간 금리 아님)', 'USD_million':'백만 달러'}
    periods={'last_trade':'최근 체결', 'rolling_24h':'제공자 표시 직전 24시간',
             'reported_8h':'보고된 8시간 구간', 'exchange_snapshot':'해당 거래소의 관측 시점'}
    narratives={e.text:e.id for e in run.case.evidence if e.kind=='observed_narrative'}
    out=[];date_table=False
    for line in lines:
        if line=='### 본문 비교 날짜와 evidence 관측일 대조':
            date_table=True
            out.extend(['비교 날짜는 원문 행의 기간을 확인했다. 월간 합계는 월 전체 값이며 자세한 날짜 대조표는 아래 상세 근거에 보존했다.',''])
            continue
        if date_table:
            if line.startswith('**날씨:**'):date_table=False
            else:continue
        if line.startswith('**'):
            target=next((t for t in re.findall(r'\]\(#([^\)]+)\)',line) if t in evidence),None)
            e=evidence.get(target)
            if e and e.value is not None:
                # Decimal formatting only, not a newly computed financial value.
                # Particularly important for small funding fractions: rounding
                # to three decimals can incorrectly make them appear zero.
                number=format(e.value,',f')
                if '.' in number:number=number.rstrip('0').rstrip('.')
                line=line.replace(_number(e.value)+' '+_text(_unit(e.unit)),number+' '+_text(units.get(e.unit,_unit(e.unit))))
                for original,label in periods.items():line=line.replace(_text(original),label)
                line=line.replace('관측 관측일 미확인','관측 시각 미확인')
        if line.startswith('확인한 발언: '):
            for text,identifier in narratives.items():
                if _text(text) in line and not re.search('[가-힣]',text):
                    line='영어로 작성된 공개 발언의 원문을 확보했다. 원문은 아래 상세 근거에서 확인할 수 있다. 내용의 진실과 현재 투자 논리에 주는 의미는 아직 검증하지 못했다. '+_refs([identifier])
                    break
        line=line.replace('NATGAS boil\\_terms','BOIL 최신 상품 조건').replace('NATGAS boil_terms','BOIL 최신 상품 조건')
        line=line.replace('정의의 evidence','정의의 근거').replace('unavailable','미확보')
        line=line.replace('현재 값·과거 값·계산식·원문 hash·후보 변경 이유는','비교한 값·관측 기간·후보 변경 이유는')
        line=line.replace('현재 가격 또는 대표 valuation가 없어','현재 가격이나 같은 기준의 가치평가 자료가 없어')
        line=line.replace('결측 보간/forward-fill 없음','없는 날짜의 값을 보간하거나 직전 값으로 채우지 않았다.')
        out.append(line)
    return out


ECONOMICS = {
    'equity': '회사 매출이 늘고 본업에서 남기는 돈도 늘면 주주에게 돌아갈 이익의 기반이 좋아질 수 있다. 하지만 시장이 그 성장을 예상해 주가를 먼저 올려 놓았다면 좋은 실적이 나와도 추가 상승 여력은 작을 수 있다. 사업 개선과 현재 가격의 매력을 따로 확인해야 한다.',
    'bond': '채권을 사는 것은 정해진 이자와 만기 상환을 받을 권리를 사는 일이다. 지금 금리는 위험자산 대신 얻을 수 있는 이자의 출발점이지만 실제 상품의 매수가격과 비용은 다를 수 있다. 금리가 오르면 이미 가진 채권의 가격은 내려갈 수 있어 자금 사용 시점과 만기를 맞춰 봐야 한다.',
    'crypto': '가격이 오른다는 것은 더 높은 가격을 받아들이는 거래가 있었다는 뜻이다. 주식의 회사 이익이나 채권의 약정 이자처럼 가치를 받쳐 주는 현금흐름과는 다르다. 실제 자금 유입과 사용 수요가 이어지는지, 빚을 낸 거래가 가격을 밀어 올린 것은 아닌지 확인해야 한다.',
    'gold': '금은 보유만으로 이자를 주지 않는다. 금을 원하는 투자자·중앙은행·실물 소비자의 수요가 중요하지만, 이자를 주는 채권을 포기하고 금을 살 만큼 가격과 위험이 합리적인지도 따로 봐야 한다. 과거 수요 개선이 지금도 이어진다고 가정해서는 안 된다.',
    'energy': '원자재 가격은 당장 필요한 양과 공급 가능한 양의 차이에 영향을 받는다. 부족해 보이는 이야기가 있어도 실제 재고가 쌓이거나 공급이 회복되면 가격이 약해질 수 있다. 선물 상품을 살 때는 원자재 방향과 계약 교체·상품 비용을 나누어 봐야 한다.',
    'real_estate': '집값 변화는 시작점이다. 실제 매매가격과 임대 조건, 대출 이자, 매도하는 데 걸리는 시간까지 알아야 투자로 남는 돈을 판단할 수 있다. 지역 지수가 올랐다는 이유만으로 특정 아파트가 싸거나 개인의 주택 구입이 적절하다고 결론 내릴 수 없다.',
    'cash': '현금은 필요할 때 바로 쓸 수 있고 다음 기회를 기다릴 선택권을 준다. 대신 물가가 오르면 같은 돈으로 살 수 있는 양이 줄 수 있다. 실제 받을 수 있는 원화 이자와 가까운 자금수요를 확인해야 현금을 유지할 이유를 판단할 수 있다.',
    'broad': '광범위 원자재 상품에는 석유·금속·곡물 등 서로 다른 시장이 들어 있다. 상품 전체가 올라도 일부 원자재만 상승을 이끌었을 수 있다. 현재 구성비와 같은 기간 성과를 함께 봐야 어떤 위험과 기대를 실제로 사는지 알 수 있다.',
}


def _economics(method):
    identifier=method.get('asset_id',method.get('id'));family=method['family']
    if identifier=='KR_EQUITY':return '메모리 가격이 오르면 같은 물량을 팔아도 회사가 남기는 이익이 늘 수 있다. 다만 휴대폰·가전 같은 다른 사업의 비용은 별도로 작용한다. 반도체 호황이 모든 회사·사업의 개선을 뜻하지 않고, 주가가 호황을 먼저 반영했다면 좋은 실적과 좋은 투자 가격도 다를 수 있다.'
    if identifier=='VALUE_DIVIDEND':return '낮은 가격에 회사 이익과 배당 현금흐름을 사는 대안이다. 성장 기대가 낮아 가격이 싸 보일 수 있지만, 실제 사업이 약하거나 배당을 줄일 위험 때문에 싼 것일 수도 있다. 낮은 가격의 이유와 앞으로 지급할 여력을 함께 봐야 한다.'
    if identifier=='GOLD':key='gold'
    elif identifier=='BROAD_COMMODITIES':key='broad'
    elif family.startswith('equity') or family=='strategy':key='equity'
    elif family=='commodity':key='energy'
    else:key=family
    return ECONOMICS.get(key,'해당 자산의 수익이 어디서 생기고 어떤 조건에서 손실이 나는지 먼저 확인해야 한다. 지금 확보한 범위 밖의 미래 수익과 개인 적절성은 유보한다.')


def _metric_meaning(metric):
    method=metric.method.lower();identifier=metric.id.upper()
    if 'yield_gap' in method:return '주식의 이익 비율과 채권 이자 사이의 설명용 차이다. 주식 이익은 약정 지급이 아니어서 이 차이를 그대로 추가 기대수익으로 해석할 수 없다.'
    if 'earnings_yield' in method or identifier.endswith('_EY'):return '가격 대비 이익을 보는 기준이다. 배당으로 받을 돈이나 앞으로 확정적으로 얻을 수익률은 아니므로 이익 지속성과 가격 하락 위험을 따로 확인해야 한다.'
    if identifier.endswith('_PE'):return '같은 이익을 살 때 지불하는 가격의 배수다. 낮아도 일회성 이익이나 업황의 정점 때문에 낮은 것이라면 좋은 가격이라고 확정할 수 없다.'
    if 'yoy' in method and ('cpi' in method or 'CPI' in identifier or '물가' in metric.label):return '물가가 전년 같은 기간보다 얼마나 변했는지다. 물가 부담은 금리 정책과 가계 구매력에 연결되지만 한 번의 관측만으로 앞으로의 정책이나 자산 수익을 확정할 수 없다.'
    if 'portfolio_weight' in method:return '제공한 전체 평가액 중 이 항목이 차지하는 비중이다. 위험 기여도와는 달라 산업·통화·직업 노출의 겹침도 확인해야 한다.'
    if 'margin' in method:return '매출에서 본업 비용을 내고 남긴 비율이다. 매출 증가가 실제 수익성 개선으로 이어지는지 보는 기준이다.'
    if 'flow' in method or 'FLOW' in identifier:return '해당 기간의 들어온 돈에서 빠져나간 돈을 뺀 값이다. 한 번의 유입이 장기 수요를 보장하지 않고 원발행사 확인 여부에 따라 해석 강도도 달라진다.'
    if 'gas' in identifier.lower() and ('PRODUCTION' in identifier or 'LNG_EXPORTS' in identifier):return '월 길이 차이를 보정한 실제 생산·수출 변화다. 공급이 늘었는지 수요가 늘었는지의 단서지만 시차가 있는 월간 값으로 당일 수급을 대신할 수 없다.'
    if 'change' in method or 'return' in method or 'growth' in method:return '표시한 기간·정의 안에서 실제로 확인한 변화다. 상승 자체가 저평가나 다음 기간 상승을 뜻하지 않아 실적·수요·비용의 반대 근거와 함께 봐야 한다.'
    return '표시한 입력과 정의로 계산한 결과다. 투자로 남는 돈이나 미래 수익을 바로 뜻하지 않으며 계산의 기간·전제·한계를 함께 봐야 한다.'


def _environment_metrics(run,series=None):
    macro_ids={m.id for m in run.macro.metrics} if run.macro else set()
    evidence={e.id:e for e in run.case.evidence}
    metrics=[m for m in run.result.metrics if m.id in macro_ids or m.input_ids and
             all(i in evidence and evidence[i].view=='macro' for i in m.input_ids)]
    if series is not None:
        metrics=[m for m in metrics if all(evidence[i].provenance and
                 evidence[i].provenance.definition['measure'] in series for i in m.input_ids)]
    return metrics


def _market_context(run,*,broad=False,scoped=False,identifiers=()):
    from .orchestrator_report import _number,_text,_refs,_unit
    lines=['## 시장 전체 그림' if broad else '## 시장 환경' if scoped else '## 이 질문에 중요한 시장 환경','']
    families={_family(m) for m in run.input['methods'] if broad or m['id'] in identifiers}
    series=None
    if scoped and not broad:
        series={i for m in run.input['methods'] if m['id'] in identifiers for i in m['macro_ids']}
        if 'US_EQUITY' in identifiers:
            from .research_catalog import CPI
            series.add(CPI)
    present=False;explained=set();blocked=set((run.evidence_validation or {}).get('quarantined_ids',[]))
    if run.macro:
        for selection in run.macro.snapshot.selections:
            if selection.status!='available' or selection.latest is None:continue
            obs=selection.latest;definition=selection.definition
            if obs.id in blocked:continue
            if series is not None and definition.canonical_id not in series:continue
            identifier=definition.canonical_id.upper()
            if 'CPI' in identifier:continue  # The index level alone is not inflation.
            present=True
            if 'KRW' in identifier or 'FX' in identifier or definition.unit=='KRW_per_USD':
                meaning='달러 자산을 원화로 평가할 때 적용되는 환율 맥락이다. 달러로 수익이 나도 원화가 강해지면 원화 수익은 줄 수 있고 반대도 가능하다. 지금 환율 한 값으로 다음 방향을 정할 수 없다.'
            elif 'TIPS' in identifier or 'REAL' in identifier:
                meaning='물가에 연동되는 미국 국채의 이자 대안이다. 이자가 없는 금에는 보유 기회비용이지만, 이 값 하나로 금 가격이 반드시 떨어진다고 판단하지 않는다.'
                if scoped and not broad and 'GOLD' not in identifiers:meaning='물가에 연동되는 미국 국채의 이자 대안이다. 자금을 빌리는 비용과 위험을 감수하면서 포기하는 이자를 판단하는 맥락이며, 이 값 하나로 분석 대상의 가격 방향을 정하지 않는다.'
            else:
                meaning='이 금리는 주식·원자재의 위험을 감수하는 대신 얻을 수 있는 이자 대안의 기준이다. 위험자산에는 그 이자를 포기할 이유가 필요하다. 다만 시장 기준금리와 실제 매수 채권·예금의 수익은 다르고, 채권도 중도 매도하면 가격 손실이 날 수 있다.'
                if scoped and not broad:meaning='이 금리는 분석 대상의 가격 위험을 감수하는 대신 받을 이자 대안의 기준이다. 다만 시장 기준금리와 실제 매수 채권·예금의 수익은 다르고 채권도 중도 매도하면 가격 손실이 날 수 있다.'
            lines.extend(['**'+_text(definition.name)+': '+_number(obs.value)+' '+_text(_unit(definition.unit))+' ('+obs.observation_date.isoformat()+').** '+_refs([obs.id]),''])
            if meaning not in explained:lines.extend([meaning,'']);explained.add(meaning)
        for m in run.macro.metrics if not scoped or broad else ():
            if 'yoy' in m.method and m.id in {x.id for x in run.result.metrics}:
                present=True
                lines.extend([_text(m.label)+': '+_number(m.value)+' '+_text(_unit(m.unit))+'. '+_refs([m.id]),'',_metric_meaning(m),''])
    if scoped and not broad:
        evidence={e.id:e for e in run.case.evidence}
        for m in _environment_metrics(run,series):
            present=True;inputs=[evidence[i] for i in m.input_ids]
            if any(e.unit=='KRW_per_USD' for e in inputs):meaning='같은 기준의 이전 환율과 비교한 변화다. 달러로 얻은 손익을 원화로 바꿀 때 결과가 달라질 수 있다는 뜻이며 분석 대상 자체의 가격 수익률은 아니다.'
            elif 'yoy' in m.method:meaning=_metric_meaning(m)
            else:meaning='같은 정의로 확인한 시장 환경의 변화다. 이자 대안과 자금 조달 조건을 이해하는 자료이며 분석 대상의 기대수익이나 투자 매력을 직접 계산한 값은 아니다.'
            dates=' / '.join(dict.fromkeys(str(e.observed_at or '관측일 미확인') for e in inputs))
            lines.extend([_text(m.label)+': **'+_number(m.value)+' '+_text(_unit(m.unit))+'** (관측 '+dates+'). '+_refs([m.id]),'',meaning,''])
    if not present:lines.extend(['질문에 관련된 최신 금리·물가·환율의 충분한 관측을 확보하지 못했다. 시장 환경을 유리하다고 가정해 결론을 보강하지 않았다.',''])
    connection='금리는 이자 대안과 자금 조달 비용으로, 물가·경기는 가계 구매력과 기업 매출·원자재 수요로 연결된다. 유동성은 사고팔 수 있는 자금의 여유다. 자금이 풀리면 위험자산 수요를 도울 수 있지만 실제로 확인하지 못한 유동성 개선을 사실로 쓰지 않는다.'
    if scoped and not broad:connection='금리와 자금 조달 조건은 이 자산을 보유하며 포기하는 이자와 빚을 내 유지하는 부담에 영향을 준다. 유동성은 사고팔 수 있는 자금의 여유다. 이런 환경의 영향과 자산 자체의 수요·수익 구조는 구분하고, 확인하지 못한 환경 개선으로 투자 논리를 보강하지 않는다.'
    lines.extend([connection,'',
                  '각 자료의 관측 기간이 다르면 함께 움직였다고 단정할 수 없다. 확인된 환경은 투자 논리의 조건이며 미래 가격을 결정하는 공식이 아니다.',''])
    return lines


def _section(lines,title):
    start=next((i for i,x in enumerate(lines) if x=='## '+title),None)
    if start is None:return []
    end=next((i for i in range(start+1,len(lines)) if lines[i].startswith('## ')),len(lines))
    return lines[start:end]


def _deepen_explanations(lines,asset):
    """Explain the meaning of existing detailed sections, without new facts."""
    contexts={
        '## 왜 지금?': {'NATGAS': '가스 가격·재고·생산·수출은 서로 다른 조각이다. 생산이 늘면 공급 부담이 되고 LNG 수출이 늘면 미국 안의 가스를 더 소비하는 효과가 있다. 서로 반대 힘이 작용할 수 있으므로 한 성장률만으로 부족이나 과잉을 결정하지 않는다.',
            'GOLD': '금 수요의 주체가 서로 다르게 움직일 수 있다. 투자용 금이 늘어도 보석 소비가 줄면 전체 실물 수요가 함께 강해졌다고 말하기 어렵다. 수요가 발표된 기간과 지금 매수할 가격의 시차도 중요하다.',
            'BROAD_COMMODITIES': '상품 전체 수익은 여러 하위시장의 결과를 묶은 것이다. 전체 성과가 커도 일부 시장만 좋아졌을 수 있어, 무엇이 성과를 이끌었고 그 기대가 이미 가격에 반영됐는지 구분해야 한다.'},
        '## 가격과 실제 수급': {'NATGAS': '재고 수준은 당장 쓸 수 있는 공급의 여유를, 주입·인출은 그 여유가 늘거나 줄었는지를 보여준다. 저장이 계절적으로 늘어나는 시기라면 단순 증가가 과잉을 뜻하지 않아 같은 계절 기준과 비교해야 한다. 아래 월간 생산·수출 합계도 현재 하루의 상황으로 바꾸어 읽으면 안 된다.'},
        '### 선물곡선과 보유 비용': {'NATGAS': '서로 다른 인도 월의 가격은 그때 가스를 받을 권리의 가격이다. 겨울 계약이 봄보다 비싸면 겨울 수요 기대를 이미 지불하고 있을 수 있다. 따라서 겨울이 온다는 사실만으로 지금의 계약이 싸다고 판단할 수 없다.'},
        '## 현재 가격과 valuation': {'SEMICONDUCTORS': '두 회사가 돈을 잘 버는지와 그 이익을 주가에서 얼마나 비싸게 사는지는 다른 질문이다. 아래 배수는 표시 종가와 실제 과거 이익을 같은 산술 방식으로 연결한 값이다. 이익의 회계 귀속과 반복 가능성이 확인되지 않은 기업은 계산이 가능해도 투자 우위를 확정할 수 없다.'},
        '## 최근 실적': {'SEMICONDUCTORS': '매출 증가는 회사가 판매한 규모의 변화이고 영업이익은 본업 비용을 내고 남긴 돈이다. 매출보다 영업이익이 빨리 늘면 가격·제품 구성·비용 조건이 좋아졌을 수 있다. 다만 기준 분기가 나빴거나 일회성 항목이 있으면 증가율만 크게 보일 수 있어 아래 이익의 질을 함께 읽어야 한다.'},
        '## 이익의 질': {'SEMICONDUCTORS': '같은 이익 증가라도 더 비싼 제품을 팔아 반복적으로 돈을 번 경우와 본업 밖에서 한 번 이익이 난 경우는 다르다. 미래에도 이어질 수 있는 이익인지 확인해야 현재 낮아 보이는 주가 배수가 의미가 있다. 공장에 돈을 다시 써야 한다면 회계상 이익만큼 현금이 남지 않을 수도 있다.'},
    }
    out=[]
    for line in lines:
        out.append(line)
        explanation=contexts.get(line,{}).get(asset)
        if explanation:out.extend(['',explanation,''])
    return out


def _candidate_observations(run,row):
    """Reuse the checked legacy candidate's numbers, dates and definitions."""
    from .scan_report import sections
    from .orchestrator_report import _current
    if row['asset_id']=='US_EQUITY' and run.deep:
        evidence={e.id:e for e in run.case.evidence}
        if any(i not in evidence or not _current(run,evidence[i]) for i in ('F_SP_FORWARD_12M_PE','F_Q3_EPS_REVISION')):return []
    old=sections(run);prefix='### '+str(row['reference_number'])+'. '
    start=next((i for i,x in enumerate(old) if x.startswith(prefix)),None)
    if start is None:return []
    end=next((i for i in range(start+1,len(old)) if old[i].startswith(('### ','## '))),len(old))
    out=[x for x in old[start+1:end] if x.startswith(('한국 국고채 3년:', '향후 열두 달', '미국 가치주', '미국 배당', '같은 정의의 미국 성장주', 'Bitcoin 가격:'))]
    if row['asset_id']=='US_EQUITY' and out:
        out.extend(['','예상 이익 배수가 낮다는 것은 예상 이익 한 단위를 사는 가격이 비교 기준보다 낮다는 뜻이다. 이익 전망의 상향은 긍정적인 변화지만 그 예상이 실현되지 않으면 분모가 줄어 지금 가격이 다시 비싸 보일 수 있다. 다음 조사에서는 전망 수정의 이유와 실제 매출·이익·현금이 따라오는지를 확인해야 한다.'])
    if row['asset_id']=='VALUE_DIVIDEND' and out:
        out.extend(['','배수가 낮으면 같은 예상 이익을 더 적은 가격으로 사는 셈이지만 성장의 약함이 이유일 수 있다. 과거 분배율은 이미 지급한 금액을 보는 값으로, 앞으로 같은 배당을 받을 약속이나 국채 이자와는 다르다.'])
    return out


def _scan_body(run,*,scoped=False):
    from .scan import assess
    from .scan_report import sections
    from .orchestrator_report import _text,_refs
    a=assess(run);rows={r['asset_id']:r for r in a['universe']};old=sections(run)
    lines=['## 오늘 시장을 이해하는 핵심','']
    if a['candidates']:
        lines.extend(['현재 먼저 더 살펴볼 곳은 **'+_text(' · '.join(rows[i]['name'] for i in a['candidates']))+'**이다. 이 순서는 더 검증할 연구 질문의 순서다. 높은 수익이 보장되거나 지금 사야 한다는 뜻은 아니다.',''])
    else:lines.extend(['지금 확인한 근거에서는 투자 대상을 억지로 선정하지 않았다. 실제 변화와 남은 공백을 함께 보며 기다릴 조건을 정리한다.',''])
    # Use only actual selected research signals; no quota of market changes.
    for identifier in a['candidates']:
        r=rows[identifier]
        lines.extend(['**'+_text(r['name'])+'에서 확인할 변화:** '+_text(r['why_now'])+' '+_refs(r['evidence_ids'][:3]),''])
    lines.extend(['새 자료 연결과 시장 변화는 다르다. 비교 가능한 이전 관측이 없으면 시장이나 관심이 좋아졌다고 말하지 않는다. 아래의 강세·약세 논리는 확인한 근거에 연결된 조건부 해석이다.',
                  '', '자료 충족 여부는 얼마나 평가할 수 있는지를 뜻한다. 이는 투자 매력 점수가 아니다. 자료가 많다는 이유로 후보가 되거나 부족하다는 이유로 나쁜 투자가 되지는 않는다.','',
                  '## 지금 가장 볼 만한 곳',''])
    for identifier in a['candidates']:
        r=rows[identifier];gap=r.get('coverage',{}).get('critical_gaps',[])
        judgment='조건부 관찰' if gap or r['status']=='conditional_watch' else '더 깊게 볼 가치 높음'
        lines.extend(['### '+str(r['reference_number'])+'. '+_text(r['name']),'','#### 왜 지금 보는가','',_text(r['why_now'])+' '+_refs(r['evidence_ids'][:3]),''])
        lines.extend(_candidate_observations(run,r));lines.append('')
        lines.extend(['#### 쉽게 말하면','',_economics(r),'','#### 좋은 점','',
            _text(r['economics'])+' '+_text(r['expectation_reality']),
            '', '#### 걱정할 점','', '주요 위험: '+_text(r['risk']).rstrip('.')+'. 투자 이유가 약해지는 조건은 '+_text(r['invalidate']),
            '', '#### 시장이 이미 기대하고 있는 것','',_text(r['price_context'])+' '+_text(r['momentum']),
            '', '좋은 뉴스가 알려져 있고 가격이 먼저 움직였다면 실제 사업이 개선돼도 추가 수익은 작을 수 있다. 현재 자료만으로 기대가 가격에 정확히 얼마나 반영됐는지는 확정하지 않는다.',
            '', '#### 무엇을 확인하면 더 강한 기회가 되는가','',_text(r['strengthen']),
            '', '남은 확인 항목: '+_text(' / '.join(r['unknowns'])),
            '', '#### 지금 판단','', '**'+judgment+'**. '+_text(r['action'])+'. '+_text(r['confidence'])+'.',''])
        if r.get('coverage'):
            missing=[s['label'] for s in r['coverage']['slots'] if s['status']=='missing']
            lines.extend(['검토 가능한 자료: '+_text(r['coverage']['label'])+'. 이는 투자 매력 점수가 아니다.'+(' '+_text(' · '.join(missing))+'가 없어 해당 판단은 제한된다.' if missing else ' 최소 조사 자료가 있어도 개인 투자 적절성을 보장하지 않는다.'),''])
        if r.get('narrative_ids'):
            lines.extend(['공개 토론은 어떤 기대를 검증할지 찾는 보조 자료다. '+_text(r['attention'])+' 반복·인기를 독립적인 사실 증거로 세지 않는다. '+_refs(r['narrative_ids'][:2]),''])
    if len(a['candidates'])<2:lines.extend(['근거가 부족하면 후보 수를 채우지 않는다. 강한 결론을 만들 자료가 부족하다는 결과도 정상적인 연구 결과다.',''])
    lines.extend(['## 지금은 덜 매력적인 곳','',
                  '여기는 투자 매력이 낮은 경우와 평가 자료가 부족한 경우를 구분한다. 자료가 부족한 자산을 나쁜 투자라고 판정하지 않는다. 국채·현금처럼 비교 기준이나 대기 대안인 영역도 별도로 읽어야 한다.',''])
    labels={'weak_case':'현재 긍정 근거가 약함','insufficient':'데이터 부족', 'conditional_watch':'조건부 관찰',
            'normal_alternative':'자금 대기·이자 대안','neutral':'다른 자산의 비교 기준'}
    if scoped:
        lines.extend(['| 영역 | 지금 상태 | 짧게 보는 이유 |','| --- | --- | --- |'])
    for r in a['universe']:
        if r['asset_id'] in a['candidates']:continue
        if scoped:
            reason=re.split(r'(?<=[.!?])\s+',r['why_now'])[0]
            if r['status']=='insufficient':
                missing=[s['label'] for s in r.get('coverage',{}).get('slots',[]) if s['status']=='missing' and s['critical']]
                if missing:reason='핵심 자료 미확인: '+' · '.join(missing)
            elif r['status'] in ('conditional_watch','weak_case'):
                reason+=' 확인할 위험: '+re.split(r'(?<=[.!?])\s+',r['risk'])[0]
            lines.append('| '+_text(r['name'])+' | '+labels.get(r['status'],'현재 연구 후보에서 보류')+' | '+_text(reason)+' '+_refs(['INSIGHT_SCAN_'+r['asset_id']])+' |')
        else:
            lines.extend(['### '+_text(r['name'])+' — '+labels.get(r['status'],'현재 연구 후보에서 보류'),'',
                _text(r['why_now'])+' '+_refs(r['evidence_ids'][:2]),'',
                '판단을 제한하거나 약화시키는 부분: '+_text(r['risk'])+' '+_text(' / '.join(r['unknowns'])),
                '', '다시 볼 조건: '+_text(r['strengthen']),''])
    if scoped:lines.extend(['','각 영역의 남은 자료·반대 근거·다시 볼 조건은 상세 근거에 남겼다. 지금 우선 후보가 아니라는 이유만으로 손실이 예상되거나 투자 가치가 없다는 뜻은 아니다.',''])
    history=_section(old,'지난 Scan 이후 달라진 점')
    if history:
        # Opaque machine measure keys belong in the audit, not reader prose.
        names={p['definition']['measure']:p['definition']['scope'] for p in a.get('observations',[])}
        for line in history:
            for measure,scope in names.items():line=line.replace(measure,scope)
            line=line.replace('**Baseline:**','**첫 비교 기준(Baseline):**').replace('**Community:**','**공개 토론:**')
            lines.append(line)
    lines.extend(_market_context(run,broad=True,scoped=scoped))
    lines.extend(['## 다음에 깊게 볼 것',''])
    questions={'US_EQUITY':'S&P500 예상 이익이 실제로 나올지, 국채 이자 대안까지 비교해서 깊게 봐줘.',
        'KR_EQUITY':'삼성전자랑 SK하이닉스의 사업 변화와 지금 주가를 연결해서 비교해줘.',
        'VALUE_DIVIDEND':'가치주·배당투자의 낮은 가격이 기회인지, 성장이 약한 이유가 있는지 봐줘.',
        'KR_GOVERNMENT_3Y':'한국 3년 국채랑 S&P500 중 신규자금 어디가 더 합리적이야?'}
    for identifier in a['candidates']:
        lines.extend(['- “'+questions.get(identifier,rows[identifier]['name']+'를 현재 가격과 반대 근거까지 깊게 봐줘.')+'”'])
    if not a['candidates']:lines.extend(['현재 확보하지 못한 핵심 자료가 확인되면 같은 질문을 다시 조사할 수 있다. 특정 자산을 바로 물어도 된다.'])
    lines.extend(['','## 한국 투자자에게 의미하는 것','',_text(a['personalization']),
        '', '원화로 쓸 돈의 사용 시점과 이미 보유한 자산이 판단을 바꾼다. 관심 후보의 사업·가격 매력과 내 포트폴리오에 더 보유할 적절성은 별도로 확인해야 한다.',''])
    return lines


def _scan_synthesis(run):
    """Connect the existing shortlist and known alternatives, not a new regime."""
    from .scan import assess
    from .orchestrator_report import _text,_refs
    a=assess(run);rows={r['asset_id']:r for r in a['universe']};chosen=[rows[i] for i in a['candidates']]
    lines=['## 그래서 지금 시장은 어떤 시장인가','']
    if not chosen:
        lines.extend(['이번 자료에서는 강한 투자 논리로 연결할 연구 후보를 고르지 못했다. 지금은 확인한 가격 움직임과 실제 수익의 기반을 연결할 자료를 더 확인해야 하는 상태다. 이는 시장에 기회가 없다는 판정이나 현금이 더 낫다는 결론은 아니다.',''])
    else:
        families={_family(r) for r in chosen}
        links=_refs(['INSIGHT_SCAN_'+r['asset_id'] for r in chosen])
        if 'equity' in families:
            focus='핵심은 이익이 좋아지는 속도와 그 이익을 사는 가격의 차이다. 기업이 더 잘 벌어도 시장이 그 좋은 미래를 먼저 비싸게 지불했다면 추가 보상은 작을 수 있다. 따라서 지금은 좋은 실적 소식에서 멈추지 않고, 실제 이익·현금이 기대를 따라오는지와 현재 가격을 연결해 선별해서 읽을 시장이다.'
        elif 'commodity' in families:
            focus='핵심은 실물 수급 변화가 현재 가격과 실제 투자상품의 수익으로 이어지는지다. 부족 기대가 먼저 가격에 반영됐거나 선물 교체 비용이 크면 방향을 맞혀도 투자 결과는 약할 수 있다. 지금은 재고·수요의 개선과 이미 지불하는 기대를 함께 가려볼 시장이다.'
        elif 'crypto' in families:
            focus='핵심은 가격을 밀어 올리는 수요가 얼마나 지속 가능한지다. 실제 자금 유입과 사용 수요를 빚을 낸 계약의 확대와 구분해야 한다. 지금은 가격 상승을 그대로 강한 보유 이유로 읽기보다 수요의 지속성과 가격에 들어간 기대를 함께 확인할 시장이다.'
        else:
            focus='핵심은 자금을 묶는 동안 받을 이자와 감수할 가격·유동성 위험의 관계다. 현재 이자가 확인돼도 자금 사용일보다 긴 만기를 사거나 환율을 감수하면 실제 결과는 달라진다. 지금은 수익의 출발점과 자금이 필요한 조건을 연결해 볼 시장이다.'
        lines.extend(['앞서 확인한 '+_text(' · '.join(r['name'] for r in chosen))+'의 연구 질문을 연결하면 '+focus+' '+links,''])
    from .orchestrator_report import _current
    rate_refs=[s.latest.id for s in run.macro.snapshot.selections if s.status=='available' and s.latest is not None and
               s.definition.unit=='percent' and 'CPI' not in s.definition.canonical_id and
               any(token in s.definition.canonical_id for token in ('TREASURY','GOVERNMENT','RATE','YIELD')) and
               any(e.id==s.latest.id and _current(run,e) for e in run.case.evidence)] if run.macro else []
    if rate_refs:lines.extend(['동시에 확인한 국채 금리는 투자하지 않고 받는 이자의 비교 기준을 준다. 위험자산의 좋은 이야기에는 이자를 포기하고 가격 하락을 감수할 이유가 더 필요하다는 뜻이다. 이익이나 수요가 좋아지는 것, 이미 가격에 반영된 기대, 이자 대안을 함께 놓아야 지금 더 조사할 가치와 실제 매수할 이유를 구분할 수 있다. '+_refs(rate_refs[:3]),''])
    if any(r['status'] in ('insufficient','conditional_watch') for r in a['universe']):
        lines.extend(['아직 다른 영역의 핵심 자료나 지속성 확인이 부족하므로 이 후보들이 시장 전체에서 가장 좋은 투자라고 말할 수는 없다. 다음 판단의 갈림길은 개선 신호가 같은 기준의 후속 관측에서도 이어지는지, 그동안 가격이 기대를 얼마나 더 반영하는지다. 자료 공백을 채우거나 반대 근거가 나타나면 현재의 조사 우선순위도 바뀔 수 있다.',''])
    return lines


def _numeric_reading(run,asset):
    from .orchestrator_report import _asset_evidence,_number,_refs,_text,_unit
    records=_asset_evidence(run,asset);labels={}
    for c in (run.discovery or {}).get('candidates',[]):
        if c.get('status')!='selected':continue
        for r in c.get('verified',{}).get('records',[]):
            if r.get('evidence_id'):labels[r['evidence_id']]=r['label']
    latest={}
    for e in records:
        if e.value is None:continue
        d=e.provenance.definition;key=tuple(d[k] for k in ('measure','scope','unit','currency','adjustment'))
        if key not in latest or str(e.observed_at or '')>str(latest[key].observed_at or ''):latest[key]=e
    lines=[]
    for e in latest.values():
        d=e.provenance.definition;measure=d['measure'].upper();label=labels.get(e.id)
        if not label:continue  # Raw passages remain in the evidence appendix.
        if 'FLOW' in measure:meaning='순유입은 들어온 돈에서 빠져나간 돈을 뺀 것이다. 실제 매수 수요의 단서지만 이 집계의 범위와 원발행사 대조 여부를 봐야 한다. 한 거래일로 장기 수요나 다음 가격을 확정할 수 없다.'
        elif 'FUNDING' in measure:meaning='선물 매수·매도 쪽이 노출을 유지하며 주고받는 자금 비용이다. 한 거래소·한 계약의 값이므로 시장 전체가 과열됐다고 단정할 수 없다.'
        elif 'OPEN_INTEREST' in measure:meaning='아직 정리되지 않은 파생계약 규모다. 거래량이나 새로 유입된 현금과 같지 않으며 규모만으로 상승·하락 방향을 알 수 없다.'
        elif 'PRICE' in measure or 'TRADE' in measure or 'CLOSE' in measure or 'MARK' in measure:meaning='실제로 확인한 가격의 출발점이다. 최근 움직임을 비교할 수 있어도 가격 한 값으로 싸거나 비싸다고 판단할 수 없다. 현물 체결가와 파생계약 평가가격도 서로 다르다.'
        elif 'VOLUME' in measure:meaning='해당 제공자에서 관측한 거래 활동의 규모다. 시장 전체의 수요나 기관 매수액과 같지 않고 독립적인 매수 근거를 대신할 수 없다.'
        else:meaning='이 자료는 표시한 기간과 범위에서 확인한 관측이다. 현재 가격의 매력으로 이어지려면 자산의 수익 원천과 반대 근거를 함께 검토해야 한다.'
        period=_text(e.period or '기간 미확인');date=str(e.observed_at or '관측일 미확인')
        lines.extend(['**'+_text(label)+': '+_number(e.value)+' '+_text(_unit(e.unit))+'** ('+period+'; 관측 '+date+'). '+_refs([e.id]),'',meaning,''])
    return lines


def _evidence_limits(run,identifiers):
    from .orchestrator_report import _text
    needs=[n for n in (run.discovery or {}).get('needs',[]) if n['asset_id'] in identifiers and n['status']!='available']
    if not needs:return []
    lines=['## 이번 판단을 제한하는 자료 공백','',
        '과거에 확인한 값이나 일부 집계가 있어도 지금 필요한 전체 자료가 확보됐다는 뜻은 아니다. 아래 공백은 현재 가격·수요·위험에 대한 판단을 제한한다.','']
    for n in needs:
        gaps=[]
        for gap in n['gaps']:
            if gap.startswith('이상/충돌/미완성 행 자료 격리:'):
                gap='서로 충돌하거나 이상·미완성 상태인 관측을 제외했다. 독립 원자료 대조가 필요하다.'
            gaps.append(_text(gap))
        lines.extend(['- '+_text(n['label'])+': '+('일부 확인' if n['status']=='partial' else '미확보')+'. '+' / '.join(gaps)])
    lines.append('');return lines


def _asset_body(run,method,*,scoped=False):
    from .orchestrator_report import _text,_refs,_asset_evidence
    identifier=method['id'];records=_asset_evidence(run,identifier)
    lines=['## '+_text(method['label'])+' — 투자 판단의 핵심','',_economics(method),'',
           '### 왜 지금 보는가','']
    findings=[f for f in run.findings if f['status']=='available_draft' and identifier in f['asset_ids']]
    for f in findings:
        lines.extend([_text(f['text'])+' '+_refs(['INSIGHT_FINDING_'+f['id']]),'',
                      '이 해석의 반대 근거: '+_text(f['counterargument']),''])
    if not findings:lines.extend(['현재 확인한 자료는 아래 범위다. 지금이 특별히 유리한 진입 시점이라는 결론은 아직 입증하지 못했다.',''])
    lines.extend(_numeric_reading(run,identifier))
    lines.extend(['### 좋은 점을 검증할 질문','',_text(method['bull_question']),
        '', '이 질문이 실제 데이터에서 확인되면 수익의 기반이 강해질 수 있다. 지금 확인되지 않은 조건을 이미 이뤄진 사실로 보지 않는다.',
        '', '### 걱정할 점','',_text(method['downside']), '',_text(method['bear_question']),
        '', '### 시장이 이미 기대하고 있는 것','',
        '좋은 이야기가 알려져 있어도 현재 가격이 그 기대를 얼마나 지불하고 있는지는 별도 문제다. '+_text(method['scope_note'])+
        ' 같은 기준의 가격·사업·수요 변화가 부족하면 기대가 싸게 반영됐다고 결론 내릴 수 없다.',
        '', '### 무엇이 바뀌면 판단이 달라지는가',''])
    for f in findings:lines.extend([_text(f['reassessment']),''])
    for gap in method['missing']:lines.extend(['- '+_text(gap)])
    economics=method['economics']
    if scoped and _family(method)=='crypto':economics=economics.replace('기업 이익이나 PER로 평가하지 않는다.','').strip()
    lines.extend(['','현재 판단: **'+('조건부 관찰' if records else '데이터 부족')+'**. '+_text(economics)+
        ' 확인한 관측과 투자 해석을 구분하며 현재 가격의 매력·미래 수익을 확정하지 않는다. '+_refs(['INSIGHT_'+identifier]),''])
    return lines


def _korean_reading(run,identifiers):
    from .korean_report import korean_report
    view=replace(run,input={**run.input,'methods':[m for m in run.input['methods'] if m['id'] in identifiers]},
        result=replace(run.result,metrics=tuple(m for m in run.result.metrics if set(m.asset_ids)&set(identifiers))))
    lines=korean_report(view)
    if len(lines)<=2:return []
    if 'US_EQUITY' not in identifiers:
        lines=[line.replace('### 원화 국고채와 미국 주식의 기회비용','### 질문에 명시한 원화 국고채의 기준 수익률') for line in lines]
        lines=[line for line in lines if not any(s in line for s in ('S&P 500','국고채 금리와 미국 주식의 이익수익률','판단을 바꿀 자료: 실제 매수 채권'))]
        if any(m['id'].startswith('KR_GOVERNMENT_') for m in view.input['methods']):
            lines.extend(['원화로 쓸 돈의 사용일과 채권 만기를 함께 확인한다. 기준금리를 확인했어도 실제 매수가격·만기수익률·중도 매도 위험을 알아야 보유할 이유를 판단할 수 있다.',''])
    return lines


def _focused_body(run,*,combined=False,scoped=False):
    from .orchestrator_report import _query_report,_text,_refs,_number,_unit
    modes=run.input['plan']['modes'];methods={m['id']:m for m in run.input['methods']}
    lines=[]
    if not combined:lines.extend(_query_report(run))
    for task in run.input['tasks']:
        if task['mode']==ResearchMode.PORTFOLIO_REVIEW:
            lines.extend(['## 내 보유에 적용할 수 있는 범위',''])
            if run.input['portfolio']:lines.extend(['보유표 기준일: '+run.input['portfolio']['as_of']+'. 아래 금액은 사용자의 자기보고 평가액이다. 실제 보유 전체가 포함됐는지도 함께 확인한다.',''])
            if run.portfolio.status=='needs_input':lines.extend(['실제 보유 내역과 재무 제약이 없어 포트폴리오의 구성·안전성·적절성을 판단할 수 없다. 좋은 자산을 찾는 것과 이미 가진 자산을 더 사도 되는지는 다른 질문이다.',''])
            elif not run.portfolio.metrics:lines.extend(['보유 범위·현금·평가액이 충분히 확인되지 않아 전체 비중 계산을 보류했다. 미확인 금액을 영으로 채워 안전한 것처럼 설명하지 않는다.',''])
            else:
                lines.extend(['제공한 평가액으로 구성은 계산했다. 이 계산이 전체 포트폴리오의 안전성을 증명하지는 않는다. 이미 같은 산업이나 자산을 많이 가진 경우에는 좋은 자산을 더 사도 전체 위험이 커질 수 있다.',''])
                for m in run.portfolio.metrics:
                    lines.extend([_text(m.label)+': **'+_number(m.value)+' '+_unit(m.unit)+'**. '+_refs([m.id]),'',_metric_meaning(m),''])
            lines.extend(['부채 상환과 향후 큰 지출은 투자자금이 실제로 얼마나 오래 남아 있을지 결정한다. 자산의 시장 매력과 추가 보유의 적절성을 따로 봐야 한다.',''])
            if run.portfolio.missing:
                lines.extend(['확인하지 못해 판단이 제한되는 정보:','',*('- '+_text(g)+' — 자금 지급 가능성과 개인 적절성의 판단을 제한한다.' for g in run.portfolio.missing),''])
        if task['mode']==ResearchMode.COMPARE:
            comparison='국채 이자·주식 이익수익률·부동산 임대수익·crypto 수요는 동일한 미래 수익률이 아니다. 약정 이자를 받는 일과 불확실한 성장에 참여하는 일의 차이를 함께 읽어야 한다.'
            if scoped:
                families={_family(methods[i]) for i in task['method_ids']}
                comparison=('국채 이자와 주식 이익수익률은 동일한 미래 수익률이 아니다. 약정 이자를 받는 일과 불확실한 성장에 참여하는 일의 차이를 함께 읽어야 한다.'
                    if {'equity','bond'}<=families else '각 대안의 수익 원천과 손실 경로를 따로 확인한다. 성격이 다른 지표는 동일한 미래 수익률이 아니므로 숫자 하나로 우열을 정하지 않는다.')
            lines.extend(['## 대안을 비교하면 무엇이 다른가','',
                '같은 자금의 사용 시점·통화·매도 가능성·손실 경로·기회비용부터 비교한다. 자산마다 돈을 버는 방식이 달라 한 지표로 우열을 정할 수 없다.',
                '', comparison,''])
        if task['candidate_dependent']:
            lines.extend(['## 후속 심층 조사 대상','', '현재 자료로 후보 선정이 유보되어 자동 후속 조사는 수행하지 않았다. 선정되지 않은 자산을 임의로 골라 분석한 것처럼 보여 주지 않는다.',''])
        if task['unsupported']:
            lines.extend(['## 이번에 조사하지 못한 부분','',*('- '+_text(s)+': 현재 이 조건을 지원할 데이터가 부족하다. 명시한 조건을 다른 국가·지역·만기로 바꾸지 않는다.' for s in task['unsupported']),''])
    identifiers=list(dict.fromkeys(i for task in run.input['tasks'] if task['mode']!=ResearchMode.OPPORTUNITY_SCAN for i in task['method_ids']))
    if not combined and not identifiers:identifiers=list(methods)
    lines.extend(_evidence_limits(run,identifiers))
    semi=bool(run.input.get('semiconductor_coverage') and set(identifiers)=={'SAMSUNG','SK_HYNIX'} and ResearchMode.COMPARE in modes)
    if semi:
        from .semiconductor_report import sections
        lines.extend(_deepen_explanations(sections(run),'SEMICONDUCTORS'))
    else:
        if not identifiers and (scoped or run.input.get('report_style')=='ask_report_explanatory_ko_v3'):return lines
        for identifier in identifiers:
            if run.input.get('commodity_coverage') and identifier in {'NATGAS','GOLD','BROAD_COMMODITIES'}:
                from .commodity_report import View,assessment,gas_sections,gold_sections,broad_sections
                review=assessment(run)['assets'][identifier];v=View(run,identifier)
                lines.extend(['## '+_text(methods[identifier]['label'])+' — 현재 판단','',_text(review['action'])+' · '+_text(review['reasoning']),
                    '',_economics(methods[identifier]),''])
                detail={'NATGAS':gas_sections,'GOLD':gold_sections,'BROAD_COMMODITIES':broad_sections}[identifier](v)
                lines.extend(_deepen_explanations(detail,identifier))
                if identifier=='NATGAS':
                    lines.extend(['### 선물 교체를 쉽게 이해하는 예','',
                        '다음은 현재 계약가격이 아닌 설명용 예시다. 이번 계약을 3달러에 보유하다 다음 계약이 3.5달러라면, 같은 금액으로 더 비싼 계약을 사면서 유지할 수 있는 노출이 줄 수 있다. 실제 비용은 교체 시점·계약가격·상품 규칙에 따라 달라진다.',
                        '', '### 하루 배수 상품을 쉽게 이해하는 예','',
                        '다음 역시 설명용 예시다. 기초자산이 첫날 +10%, 다음 날 -10% 움직이면 하루 2배 상품은 +20% 뒤 -20%를 겪는다. 둘째 날 손익은 첫날 바뀐 잔액에서 계산되므로 장기 결과는 기초자산의 단순 두 배가 아니다. 이 예시는 BOIL의 최신 약관이나 실제 성과를 확인했다는 뜻이 아니다.',''])
                lines.extend(['## 무엇이 바뀌면 판단이 달라지는가','',_text(review['reassessment']),
                    '', '반대 가능성: '+_text(review['counterargument']),
                    '', '여전히 확인할 항목:','',*('- '+_text(g) for g in review['gaps']),''])
            else:lines.extend(_asset_body(run,methods[identifier],scoped=scoped))
        if run.input.get('korean_coverage'):
            from .korean_report import korean_report
            lines.extend(_korean_reading(run,identifiers) if scoped else korean_report(run))
        if run.deep:
            from .orchestrator_report import _current
            evidence={e.id:e for e in run.case.evidence}
            facts=[f for f in run.deep.facts if f['status']=='available' and f['id'] in evidence and _current(run,evidence[f['id']])]
            if scoped:facts=[f for f in facts if set(evidence[f['id']].asset_ids)&set(identifiers)]
            if facts or not scoped:lines.extend(['## 예상 이익과 현재 가격을 연결해서 읽기',''])
            for f in facts:
                meaning=('시장이 앞으로의 이익을 이 정도 가격에 사고 있다는 단서다. 예상 이익이 미달하면 같은 주가도 더 비싼 가격이 되므로 예상치 수정과 실제 실적을 함께 봐야 한다.'
                    if f['basis'].startswith('forward') else '이미 기록된 이익·시장 기대·금리 중 표시한 정의의 관측이다. 서로 다른 기간의 자료를 한 시점의 확정 수익으로 비교하지 않는다.')
                qualifier={'reported':'','above':'&gt;','below':'&lt;','approximate':'약 '}.get(f.get('qualifier','reported'),'')
                lines.extend([_text(f['label'])+': **'+qualifier+_number(Decimal(f['value']))+' '+_text(_unit(f['unit']))+'** ('+f['observed_at']+'; '+_text(f['window'])+'). '+_refs([f['id']]),'',meaning,''])
        other=[m for m in run.result.metrics if not m.id.startswith(('PORT_','CALC_COMMODITY_','SCAN_GAS_')) and (not combined or set(m.asset_ids)&set(identifiers))]
        if scoped:
            environment_ids={m.id for m in _environment_metrics(run)}
            other=[m for m in other if m.id not in environment_ids and set(m.asset_ids)&set(identifiers)]
            if not any(_family(methods[i])=='equity' for i in identifiers):
                other=[m for m in other if m.method not in ('earnings_yield_v1','descriptive_yield_gap_v1')]
        if other:
            lines.extend(['## 계산한 숫자가 투자 판단에서 뜻하는 것',''])
            from .orchestrator_report import _limits
            for m in other:
                lines.extend(['**'+_text(m.label)+': '+_number(m.value)+' '+_text(_unit(m.unit))+'**. '+_refs([m.id]),'',
                    _metric_meaning(m)+' '+_text(_limits(m.limitations)),''])
        lines.extend(_market_context(run,scoped=scoped,identifiers=identifiers))
        lines.extend(['## 한국 투자자에게 의미하는 것',''])
        from .research_catalog import FX
        if any(FX in methods[i]['macro_ids'] if scoped else methods[i]['macro_ids'] for i in identifiers):lines.extend(['달러 자산 자체의 수익과 원화로 환산한 결과는 다를 수 있다. 원화가 강해지면 달러 수익이 원화에서는 줄어들 수 있고 반대도 가능하다. 현재 환율 한 값으로 미래 방향을 확정하지 않는다.',''])
        lines.extend(['실제 상품·계좌·비용·세금·보유기간과 큰 자금수요를 확인해야 개인에게 적절한지 판단할 수 있다. 지금의 자산 분석을 그대로 투자비중이나 매매 명령으로 바꾸지 않는다.',''])
    return lines


def render_explanatory_report(run,legacy):
    from .orchestrator_report import _text,_guard_report
    scan=bool(run.input.get('scan'));style=run.input.get('report_style')
    scoped=style in ('ask_report_explanatory_ko_v4','ask_report_explanatory_ko_v5')
    lines=['# '+('지금 전체 투자판에서 더 볼 만한 곳' if scan else '투자 질문을 이해하기 위한 조사 보고서'),'',
        '**질문:** '+_text(run.input['question']),'',
        '정보 기준: '+run.cutoff.astimezone(ZoneInfo('Asia/Seoul')).isoformat()+' (한국시간). 각 숫자의 관측 기간은 본문과 원자료에서 따로 확인한다.','']
    if run.input['synthetic']:lines.extend(['**합성 검증 자료가 포함된 예제다. 실제 투자 판단에 사용하지 않는다.**',''])
    lines.extend(['확인한 사실과 계산, 근거를 해석한 조건부 논리를 구분한다. 쉬운 설명이 근거의 강도나 현재 판단을 바꾸지는 않는다.',''])
    if scan:
        lines.extend(_scan_body(run,scoped=scoped))
        if any(t['mode']!=ResearchMode.OPPORTUNITY_SCAN for t in run.input['tasks']):lines.extend(_focused_body(run,combined=True,scoped=scoped))
    else:
        lines.extend(['## 핵심 판단',''])
        if run.input.get('semiconductor_coverage') and {m['id'] for m in run.input['methods']}=={'SAMSUNG','SK_HYNIX'}:
            from .semiconductor_data import audit
            review=audit(run);lines.extend([_text(review['judgment'])+'. '+_text(review['reasoning']),''])
        elif run.input.get('commodity_coverage'):
            from .commodity_report import assessment
            for asset,review in assessment(run)['assets'].items():
                label=next(m['label'] for m in run.input['methods'] if m['id']==asset)
                lines.extend([_text(label)+': **'+_text(review['action'])+'**. '+_text(review['reasoning']),''])
        elif ResearchMode.PORTFOLIO_REVIEW in run.input['plan']['modes']:
            lines.extend(['보유정보에서 확인할 수 있는 구성과 아직 판단할 수 없는 안전성·적절성을 나누어 본다. 전체 보유와 재무 제약이 불완전하면 추가 투자나 적정 비중을 정하지 않는다.',''])
        else:lines.extend(['확인한 근거만으로 현재 가격의 투자 매력과 전체 우열을 확정하기는 어렵다. 아래에는 실제로 확인한 변화, 그 의미와 가장 강한 반대 질문을 함께 설명한다.',''])
        lines.extend(_focused_body(run,scoped=scoped))
    # Generic reports retain actual community observations, never synthesize a
    # popular thesis. Dedicated reports already carry their own narrative view.
    if (not scan and not run.input.get('semiconductor_coverage')
            and (run.input['methods'] or style not in ('ask_report_explanatory_ko_v3','ask_report_explanatory_ko_v4','ask_report_explanatory_ko_v5'))):
        from .orchestrator_report import _used_evidence,_refs
        narratives=[e for e in _used_evidence(run) if e.kind=='observed_narrative']
        lines.extend(['## 공개 토론과 실제 근거의 차이',''])
        if not narratives:lines.extend(['관련성과 최신성을 충족하는 공개 토론을 확인하지 못했다. 사람들이 낙관적이거나 비관적이라고 추정하지 않는다.',''])
        for e in narratives:lines.extend(['확인한 발언: '+_text(e.text)+' '+_refs([e.id]),'',
            '발언이 있었다는 사실과 내용이 맞다는 것은 다르다. 사실 주장에는 공식 자료의 대조가 필요하고 소수 표본·반복·좋아요로 시장 전체의 생각을 단정할 수 없다.',''])
        for check in (run.discovery or {}).get('community_verification',[]):
            lines.extend(['검증에서 확인한 범위: '+_text(check['reason'])+' '+_refs([check['narrative_evidence_id'],*check['evidence_ids']]),''])
    if run.input['plan']['clarifications']:lines.extend(['## 먼저 확인할 질문','',*('- '+_text(q) for q in run.input['plan']['clarifications']),''])
    if run.evidence_validation and run.evidence_validation['quarantined_ids']:
        lines.extend(['## 추가 검증을 위해 격리한 자료','',
            '원문 숫자 사이의 충돌·이상치·미완성 자료는 계산과 현재 판단에서 제외했다. 원문을 발견했다는 이유만으로 믿을 수 있는 수치가 되지는 않는다. 어떤 자료를 제외했고 왜 제외했는지는 아래 상세 근거에 보존했다.',''])
    if not scan and '## 초간단 설명' not in lines:
        lines.extend(['## 초간단 설명','',
            '지금 무엇이 좋아지는지와 지금 가격이 싼지는 다른 질문입니다. 확인한 숫자는 관측한 기간과 범위 안에서만 읽어야 합니다. 좋은 기대가 가격에 먼저 반영됐거나 반대 조건이 생기면 손실이 날 수 있습니다. 더 확인할 핵심 자료가 빠져 있다면 강한 결론을 기다리는 것이 정상입니다. 실제 상품과 내 자금 사용 시점까지 알아야 개인 투자 판단으로 연결할 수 있습니다.',''])
    if scan and scoped:lines.extend(_scan_synthesis(run))
    lines=[line.replace('## Bull Case','## 좋아질 수 있는 가장 강한 논리 (Bull Case)')
        .replace('## Bear Case','## 나빠질 수 있는 가장 강한 논리 (Bear Case)') for line in lines]
    polished=style in ('ask_report_explanatory_ko_v2','ask_report_explanatory_ko_v3','ask_report_explanatory_ko_v4','ask_report_explanatory_ko_v5')
    if polished:lines=_reader_format(run,lines)
    families={_family(m) for m in run.input['methods']} if scoped else None
    headings={}
    if scoped:
        for m in run.input['methods']:
            for suffix in (' — 투자 판단의 핵심',' — 현재 판단'):headings['## '+_text(m['label'])+suffix]={_family(m)}
        if scan:
            from .scan import assess
            assessment=assess(run)
            for r in assessment['universe']:
                if r['asset_id'] in assessment['candidates']:headings['### '+str(r['reference_number'])+'. '+_text(r['name'])]={_family(r)}
    lines=explain_terms(lines,extended=polished,korean_suffixes=style in ('ask_report_explanatory_ko_v3','ask_report_explanatory_ko_v4','ask_report_explanatory_ko_v5'),families=families,section_families=headings,contract_leverage=style=='ask_report_explanatory_ko_v5')
    # Keep every legacy source, calculation, claim link, hash and guard record.
    # Reusing this validated rendering also preserves all anchor targets.
    lines.extend(['<details>','<summary>근거 자세히 보기 · 계산 방법 · 원자료 · 검증 및 재현 기록</summary>','',
        '여기에는 동일한 분석의 상세 조사 내용과 원자료·계산·판단 연결을 보존한다. 본문에 붙은 “자료 확인”·“계산 확인” 링크가 해당 근거로 이어진다.','',
        legacy.rstrip(),'','</details>',''])
    return '\n'.join(lines)+'\n'
