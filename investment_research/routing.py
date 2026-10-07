"""Bounded intent routing, without acquisition, financial judgments or execution.

These rules cover common Korean/English requests. Unresolved intent or asset
methods produce clarification requirements, never a default full-market Scan.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
import re

from .sources import SourceError
from .query_understanding import (COUNTRY_PATTERN, REGION_PATTERN, Term, bond_label, subject_details,
                                  understand_question)

ROUTING_VERSION = "research_routing_v5"


class ResearchMode(StrEnum):
    OPPORTUNITY_SCAN = "opportunity_scan"
    ASSET_DEEP_DIVE = "asset_deep_dive"
    COMPARE = "compare"
    PORTFOLIO_REVIEW = "portfolio_review"


# Labels identify research subjects, not preferred instruments or sources.
SUBJECT_PATTERNS = (
    (r'(?:(?:한국|대한민국|원화|미국|일본|독일|영국|중국|프랑스)(?:의)?\s*)?(?:(?:단기|중기|장기)\s*)?(?:\d+(?:\.\d+)?\s*(?:년|개월)(?:물|\s*만기)?\s*)?국채(?:\s*\(\s*\d+(?:\.\d+)?\s*(?:년|개월)(?:물)?\s*\)|\s*만기\s*\d+(?:\.\d+)?\s*(?:년|개월)|\s*\d+(?:\.\d+)?\s*(?:년|개월)물)?',None,'bond'),
    (r'(?:(?:'+COUNTRY_PATTERN+r')(?:의)?\s*)?(?:'+REGION_PATTERN+r')(?:\s*(?:[/·,]|과|와|및)\s*(?:'+REGION_PATTERN+r'))*\s*(?:의\s*)?(?:아파트|집|주택|부동산)',None,'real_estate'),
    (r'(?:'+COUNTRY_PATTERN+r')(?:의)?\s*(?:아파트|집|주택|부동산)',None,'real_estate'),
    (r"삼성전자|Samsung Electronics|\bSSNLF\b", "삼성전자", "equity"),
    (r"SK\s*하이닉스|SK Hynix", "SK하이닉스", "equity"),
    (r"Microsoft|마이크로소프트|\bMSFT\b", "Microsoft", "equity"),
    (r"Alphabet|알파벳|\bGOOGL?\b", "Alphabet", "equity"),
    (r"Amazon|아마존|\bAMZN\b", "Amazon", "equity"),
    (r"\bMeta\b|메타", "Meta", "equity"),
    (r"NVIDIA|엔비디아|\bNVDA\b", "NVIDIA", "equity"),
    (r"Apple|애플|\bAAPL\b", "Apple", "equity"),
    (r"S\s*&\s*P\s*500|S&P500", "S&P 500", "equity_index"),
    (r"Nasdaq[- ]?100|나스닥\s*100", "Nasdaq-100", "equity_index"),
    (r"Nasdaq|나스닥", "Nasdaq", "equity_index"),
    (r"미국\s*주식|US equities|US stocks", "미국 주식", "equity_index"),
    (r"한국\s*주식|Korean stocks", "한국 주식", "equity_index"),
    (r"한국\s*반도체|Korean semiconductors", "한국 반도체", "equity_sector"),
    (r"반도체|semiconductor(?:s)?", "반도체", "equity_sector"),
    (r"한국\s*배당주|Korean dividend stocks", "한국 배당주", "equity_strategy"),
    (r"배당\s*투자|dividend invest(?:ing|ment)", "배당 투자", "equity_strategy"),
    (r"성장주|growth stocks", "성장주", "equity_strategy"),
    (r"가치주|value stocks", "가치주", "equity_strategy"),
    (r"\bSCHD\b|\bVOO\b|\bSPY\b|\bQQQ\b|\bIBIT\b|\bETHA\b|\bETF\b", None, "etf"),
    (r"Bitcoin|비트코인|\bBTC\b", "Bitcoin", "crypto"),
    (r"Ethereum|이더리움|\bETH\b", "Ethereum", "crypto"),
    (r"Solana|솔라나|\bSOL\b", "Solana", "crypto"),
    (r"천연\s*가스|natural gas", "천연가스", "natural_gas"),
    (r"원유|crude oil", "원유", "commodity"),
    (r"원자재|commodit(?:y|ies)", "원자재", "commodity"),
    (r"(?<![가-힣])금(?![가-힣])|\bgold\b", "금", "commodity"),
    (r"미국\s*단기\s*국채|US\s+short[- ](?:duration|term)\s+Treasur(?:y|ies)(?: bonds)?", "단기 국채", "bond"),
    (r"미국\s*중기\s*국채|US\s+intermediate(?:[- ]duration)?\s+Treasur(?:y|ies)(?: bonds)?", "중기 국채", "bond"),
    (r"미국\s*장기\s*국채|US\s+long[- ](?:duration|term)\s+Treasur(?:y|ies)(?: bonds)?", "장기 국채", "bond"),
    (r"단기\s*국채|short[- ](?:duration|term)\s+Treasur(?:y|ies)(?: bonds)?", "단기 국채", "bond"),
    (r"중기\s*국채|intermediate(?:[- ]duration)?\s+Treasur(?:y|ies)(?: bonds)?", "중기 국채", "bond"),
    (r"장기\s*국채|long[- ](?:duration|term)\s+Treasur(?:y|ies)(?: bonds)?", "장기 국채", "bond"),
    (r"미국\s*국채|US\s+Treasur(?:y|ies)(?: bonds)?", "미국 국채", "bond"),
    (r"(?:한국|대한민국|원화)(?:의)?\s*(?:(?:단기|중기|장기)\s*)?국채|Korean\s+government bonds", "한국 국채", "bond"),
    (r"국채|Treasur(?:y|ies)(?: bonds)?|government bonds", "국채", "bond"),
    (r"회사채|corporate bonds", "회사채", "bond"),
    (r"동탄\s*(?:아파트|집|주택|부동산)|Dongtan(?: apartments| housing| property)?", "동탄 주거 부동산", "real_estate"),
    (r"한국\s*부동산|Korean real estate|아파트|부동산|real estate|\bproperty\b", None, "real_estate"),
    (r"현금성?\s*자산|현금|\bcash\b", "현금", "cash"),
)

METHOD_INPUTS = {
    "equity": ("사업·실적·현금흐름·재무와 가격 기대", "동일 정의 valuation·예상치 수정·반대 논리"),
    "equity_index": ("지수 정의·구성·집중 노출", "동일 정의 valuation·이익 전망과 수정·실제 실적"),
    "equity_sector": ("산업 구조·경쟁·수급과 기업별 실적", "산업 내 차이·valuation·catalyst·반대 논리"),
    "equity_strategy": ("전략의 목적·노출·실행 수단", "배당/성장/가치의 지속성·총수익 정의·비용·관련 과세"),
    "etf": ("기초 노출·보유 구성·중복", "복제·보수·환헤지·분배·상품 구조와 관련 기초자산 근거"),
    "crypto": ("프로토콜·사용·발행·공급·유동성", "보관·거래 상대방·규제·downside·검증할 narrative"),
    "natural_gas": ("지역·허브·재고·생산·소비·계절·기상", "현물/선물 곡선·roll·실제 투자상품"),
    "commodity": ("해당 원자재의 수급·재고·지역·단위", "현물/선물·보유 비용·관련 macro 전달 경로"),
    "bond": ("종류·만기·계약 현금흐름·현재 yield 정의", "duration·신용·재투자·유동성·보유 기간"),
    "real_estate": ("지역·물건·실거래·거래량·전세·공급", "금융비용·대출·정책·유동성·실거주 편익"),
    "cash": ("통화·금융기관·이자·접근 조건", "유동성·물가·신용과 대기하는 기회비용"),
}
COMPARE_CRITERIA = (
    "수익의 경제적 원천과 가정", "downside와 손실 경로", "기회비용",
    "해당되는 valuation 정의", "유동성·투자기간", "관련 세금·계좌·환율 제약",
    "확인된 사용자 상황에서의 적절성; 비교 불가능한 축은 표시",
)
PORTFOLIO_INPUTS = (
    "기준일과 실제 보유자산·수량/가치·통화·상품·중복 노출",
    "현금·부채·소득/지출·추가 투자 가능액", "비상자금·큰 자금수요·주택 계획·투자기간",
    "위험 감당 능력과 감수 의향·관련 세법/계좌 제약",
)


@dataclass(frozen=True)
class Subject:
    label: str
    method_family: str
    asset_class: str | None = None
    country: str | None = None
    regions: tuple[str, ...] = ()
    maturity: Term | None = None
    duration: Term | None = None
    strategies: tuple[str, ...] = ()
    raw_text: str | None = None


@dataclass(frozen=True)
class ResearchTask:
    id: str
    mode: ResearchMode
    subjects: tuple[Subject, ...]
    scope: str
    depends_on: tuple[str, ...]
    required_inputs: tuple[str, ...]
    questions: tuple[str, ...]


@dataclass(frozen=True)
class ResearchPlan:
    question: str
    selection_source: str
    modes: tuple[ResearchMode, ...]
    tasks: tuple[ResearchTask, ...]
    clarifications: tuple[str, ...]
    understanding: dict

    def to_dict(self) -> dict:
        return {
            "schema_version": "research-plan-v1", "method_version": ROUTING_VERSION,
            "status": "needs_clarification" if self.clarifications else "planned",
            "execution_status": "not_started", **asdict(self),
            "limits": [
                "선택한 모드의 조사 계획이며 금융 분석 결과·수치·추천이 아니다.",
                "규칙 기반 질문 해석의 범위를 넘으면 확인하며 전체 Scan으로 대체하지 않는다.",
                "관련 macro·대안만 조사한다. 미조사 자산의 열등함을 뜻하지 않는다.",
                "필수 근거·보유 정보가 unknown이면 영향을 받는 결론을 보류한다.",
            ],
        }


def _subjects(text: str) -> tuple[Subject, ...]:
    # Korean particles attached to tickers are not part of the symbol.
    original=text;characters=[];positions=[]
    for index,char in enumerate(original):
        if index and re.fullmatch(r'[A-Za-z0-9][가-힣]|[가-힣][A-Za-z0-9]',original[index-1:index+1]):
            characters.append(' ');positions.append(index)
        characters.append(char);positions.append(index)
    text=''.join(characters)
    # In a Bitcoin ETF-flow question, ETF is the evidence/product category;
    # it is not an additional unspecified alternative requiring another dive.
    text = re.sub(r'(Bitcoin|비트코인|\bBTC\b)\s+(?:spot\s+|현물\s+)?ETF\b',
                  lambda m:m[1]+' '*(len(m[0])-len(m[1])),text,flags=re.I)
    matches = []
    for pattern, label, family in SUBJECT_PATTERNS:
        for match in re.finditer(pattern, text, re.I):
            raw_start=positions[match.start()]
            prefix_start=max(0,raw_start-20)
            country=re.search(r'(?:'+COUNTRY_PATTERN+r')(?:의)?\s*$',original[prefix_start:raw_start])
            if country:raw_start=prefix_start+country.start()
            raw=original[raw_start:positions[match.end()-1]+1].strip()
            details=subject_details(label,family,raw)
            name=label or (bond_label(raw,details) if family=='bond' else raw)
            if family=='real_estate' and details['regions']==('동탄',):name='동탄 주거 부동산'
            matches.append((match.start(), match.end(), Subject(name,family,**details)))
    selected = []
    for start, end, subject in sorted(matches, key=lambda m: (m[0], -(m[1] - m[0]))):
        if any(start < old_end and end > old_start for old_start, old_end, _ in selected):
            continue
        key=lambda s:(s.label,s.method_family,s.country,s.regions,s.maturity,s.duration,s.strategies)
        if key(subject) not in [key(item[2]) for item in selected]:
            selected.append((start, end, subject))
    result = tuple(item[2] for item in selected)
    generic_labels = {"ETF", "아파트", "부동산", "real estate", "property"}
    return tuple(subject for subject in result if subject.label not in generic_labels
                 or not any(other.method_family == subject.method_family and other.label not in generic_labels for other in result))


def _modes(values) -> tuple[ResearchMode, ...]:
    if isinstance(values, (str, bytes)):
        raise SourceError("modes: a nonempty sequence of explicit modes is required")
    try:
        result = tuple(ResearchMode(value) for value in values)
    except (TypeError, ValueError):
        raise SourceError("unsupported research mode") from None
    if not result or len(result) != len(set(result)):
        raise SourceError("explicit modes must be nonempty and unique")
    return result


def plan_research(question: str, *, modes=None) -> ResearchPlan:
    """Choose only requested work; never acquire data or dispatch a research run."""
    if not isinstance(question, str) or not question.strip() or len(question) > 4000:
        raise SourceError("question: nonempty text of at most 4000 characters required")
    text = question.strip()
    prefix = re.match(r"^(Opportunity Scan|Asset Deep Dive|Compare|Portfolio Review)"
                      r"((?:\s*\+\s*(?:Opportunity Scan|Asset Deep Dive|Compare|Portfolio Review))*)\s*[:：]", text, re.I)
    source = "explicit" if modes is not None or prefix else "inferred_rules"
    if modes is not None:
        chosen = _modes(modes)
    elif prefix:
        chosen = _modes(part.strip().lower().replace(" ", "_") for part in prefix.group(0).rstrip(":：").split("+"))
    else:
        chosen = ()
    if prefix:
        text = text[prefix.end():].strip()
    # A negated request to Scan does not turn a specific question into a Scan.
    text = re.sub(r"(?:시장\s*전체|전체\s*시장|전체\s*투자판|기회\s*탐색|Opportunity Scan).{0,20}?(?:하지\s*말고|훑지\s*말고|빼고|제외하고)", "", text, flags=re.I)
    text = re.sub(r"(?:do not|don't)\s+(?:run\s+)?(?:an?\s+)?(?:opportunity scan|scan (?:the )?(?:whole )?market)", "", text, flags=re.I)
    subjects = _subjects(text)
    # Preserve explicitly named alternatives even when their method is unknown.
    alternatives = re.split(r"\s+(?:vs\.?|versus)\s+", text, flags=re.I)
    if len(alternatives) >= 2:
        subjects = tuple(subject for part in alternatives for subject in
                         (_subjects(part) or (Subject(part.strip(" ?.!"), "unresolved"),)))
    portfolio = bool(re.search(r"내\s*(?:포트폴리오|보유|자산|계좌)|현재\s*보유|my\s+(?:portfolio|holdings|allocation)|자산\s*배분|asset allocation|portfolio (?:review|risk)|리밸런|rebalanc|집중\s*위험|concentration risk|현금\s*(?:비중|수준)|cash level", text, re.I))
    compare = bool(re.search(r"\bvs\.?\b|\bversus\b|비교|\bcompare\b|between\b",text,re.I)
                   or len(subjects)>=2 and re.search(r"(?:중|가운데).{0,60}?(?:뭐|어느|어디|더\s*(?:나|좋|합리))",text,re.I))
    depth = bool(re.search(r"깊게|심층|deep dives?|in.depth", text, re.I))
    broad = bool(re.search(r"(?:시장\s*전체|전체\s*시장|여러\s*시장)(?:를|을)?\s*(?:한번\s*)?(?:훑|살펴|조사|분석|보고)|(?:시장\s*전체|전체\s*시장).{0,15}(?:변했|변한|변화)|market scan|(?:changed|opportunities).*across markets", text, re.I))
    broad = broad or bool(re.search(r'(?:전체\s*투자판|시장\s*전반).{0,60}?(?:기회|훑|탐색)',text))
    opportunity = bool(re.search(r"투자\s*기회|투자할\s*(?:만한\s*)?곳|(?:전체\s*투자판|시장\s*전반|여러\s*자산).{0,60}?(?:기회|투자할)|자산군.*(?:기회|매력|조사)|where.*(?:opportunit|invest|risk.?reward)|what.*changed.*markets|(?:what|which).*asset classes.*(?:worth|research|interesting)", text, re.I))
    opportunity = opportunity or bool(re.search(r'(?:어디에|어디가|어느\s*(?:곳|자산)).{0,45}?(?:투자|합리적)|신규\s*자금.{0,50}?어디',text))
    if (opportunity and subjects and all(s.method_family=='cash' for s in subjects) and
            re.search(r'(?:신규\s*(?:자금|현금)|투자\s*가능한\s*(?:돈|현금)|현금.{0,20}있다면)',text)):
        subjects=()
    scan = broad or (opportunity and not subjects and not portfolio and not compare)
    if source == "inferred_rules":
        selected = []
        if scan:
            selected.append(ResearchMode.OPPORTUNITY_SCAN)
        if portfolio:
            selected.append(ResearchMode.PORTFOLIO_REVIEW)
        if compare:
            selected.append(ResearchMode.COMPARE)
        if depth or (subjects and not scan and not compare and not portfolio):
            selected.append(ResearchMode.ASSET_DEEP_DIVE)
        chosen = tuple(selected)

    clarifications = []
    if not chosen:
        # An unrecognised name is not a reason to investigate every asset.
        chosen = (ResearchMode.ASSET_DEEP_DIVE,)
        clarifications.append("조사할 자산·기업·전략과 실제 질문의 범위를 확인해야 한다.")
    if ResearchMode.COMPARE in chosen and len(subjects) < 2:
        clarifications.append("비교할 두 개 이상의 대안과 관련 비교 조건을 확인해야 한다.")
    if any(subject.method_family == "unresolved" for subject in subjects):
        clarifications.append("명시한 대상의 자산/상품 유형과 고유 분석 방법을 확인해야 한다.")
    candidate_selection = scan and depth and not subjects
    if ResearchMode.ASSET_DEEP_DIVE in chosen and not subjects and not candidate_selection:
        clarifications.append("Deep Dive 대상과 자산/전략에 맞는 분석 방법을 확인해야 한다.")
    tasks = []
    for mode in chosen:
        if mode == ResearchMode.OPPORTUNITY_SCAN:
            tasks.append(ResearchTask("scan", mode, (), "question_relevant_asset_classes", (),
                ("질문에 관련된 여러 자산군의 현재 근거·변화·반대 논리",),
                ("더 조사할 이유와 보류 이유; 약한 근거로 순위·추천·후보 수를 강제하지 않는다.",)))
        elif mode == ResearchMode.COMPARE:
            personal_context = ("동일 요청의 실제 포트폴리오·재무 제약을 개인 비교에 연결; unknown이면 개인 적절성 유보",) if ResearchMode.PORTFOLIO_REVIEW in chosen else ()
            tasks.append(ResearchTask("compare", mode, subjects, "provided_alternatives", (),
                ("각 대안에 고유한 자료·정의·손실 경로", "관련 기간·통화·사용자 제약") + personal_context, COMPARE_CRITERIA))
        elif mode == ResearchMode.PORTFOLIO_REVIEW:
            tasks.append(ResearchTask("portfolio", mode, subjects, "actual_portfolio_and_constraints", (),
                PORTFOLIO_INPUTS, ("자산 자체의 매력", "기존 중복·과도한 노출", "추가 자본이 전체 포트폴리오에 미치는 변화; 누락 정보로 안전·적절성을 확정하지 않는다.")))
        elif candidate_selection:
            tasks.append(ResearchTask("deep_candidates", mode, (), "scan_candidates_only_if_supported", ("scan",),
                ("사용자가 요청한 수·범위 안에서 근거가 있는 후보; 부족하면 선택 유보",),
                ("후보별 고유 방법으로 기대·실제 근거·반대 논리·재검토 조건을 검증한다.",)))
        else:
            for index, subject in enumerate(subjects or (Subject(text, "unresolved"),)):
                tasks.append(ResearchTask("deep_" + str(index + 1), mode, (subject,), "specified_subject", (),
                    METHOD_INPUTS.get(subject.method_family, ("대상과 고유 분석 방법 확인",)),
                    ("기대와 실제 근거·가장 강한 반대 논리", "관련된 대안·macro만 필요한 범위에서 검토")))
    understanding=understand_question(question.strip(),subjects,[mode.value for mode in chosen],compare)
    return ResearchPlan(question.strip(), source, chosen, tuple(tasks), tuple(dict.fromkeys(clarifications)),understanding)
