"""Question-scoped, reviewed acquisition templates; no model-generated URLs.

Templates retain their original observation dates and exact excerpts. They are
not a live discovery service: changed passages or stale editions are withheld.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass, replace
from pathlib import Path

from .routing import Subject
from .source_pipeline import _digest, load_pins
from .sources import SourceError

CATALOG_VERSION = "curated_research_catalog_v1"
FX = "USD_KRW_NOON_REFERENCE"
RATES = ("US_TREASURY_NOMINAL_2Y", "US_TREASURY_NOMINAL_10Y")
CPI = "US_CPI_U_HEADLINE_NSA"


@dataclass(frozen=True)
class AssetMethod:
    id: str
    label: str
    family: str
    source_ids: tuple[str, ...]
    macro_ids: tuple[str, ...]
    economics: str
    downside: str
    bull_question: str
    bear_question: str
    missing: tuple[str, ...]
    scope_note: str = "검토한 공개 자료의 제한된 조사 범위"


def method(identifier, label, family, sources, macro, economics, downside, bull, bear, missing, scope):
    return AssetMethod(
        identifier, label, family, tuple(sources), tuple(macro), economics, downside, bull, bear, tuple(missing), scope
    )


METHODS = {
    "BTC": method(
        "BTC",
        "Bitcoin",
        "crypto",
        ["CR_IBIT_ISSUER", "CR_COINSHARES_CURRENT_FLOWS", "COM_HN_BTC_CUSTODY_RISK", "COM_HN_BTC_BEAR_PERFORMANCE"],
        [FX],
        "사용·보유 수요와 희소성 가설을 검증한다. 기업 이익이나 PER로 평가하지 않는다.",
        "수요 감소·레버리지 청산·규제·거래소/보관 위험; ETF와 현물 보관은 다르다.",
        "투자상품의 자금 유입이 Bitcoin 고유 수요의 지속으로 이어지는가?",
        "유입 둔화·보관 위험이 강세 논리를 약화시키는가?",
        [
            "BTC 단독 ETF 일별 순유입과 실제 보유량",
            "가격·거래량·선물 funding/미결제약정·청산·network의 최신 자료",
            "가격의 매력을 판단할 검증된 가치 대용 지표",
        ],
        "IBIT 상품과 제공자의 디지털자산 전체 flow를 구분한다. aggregate flow는 BTC 단독 flow가 아니다.",
    ),
    "ETH": method(
        "ETH",
        "Ethereum",
        "crypto",
        ["CR_ETHA_ISSUER", "CR_ETH_ISSUANCE_MECHANISM", "CR_COINSHARES_CURRENT_FLOWS", "COM_HN_BTC_CUSTODY_RISK"],
        [FX],
        "네트워크 사용·수수료·발행/소각·수요의 연결을 검증한다.",
        "프로토콜·경쟁·보관·규제·유동성 위험을 검토한다.",
        "네트워크 사용과 투자 수요가 실제 수수료·보유 경제성으로 이어지는가?",
        "사용 증가가 토큰 보유자의 경제적 가치 증가와 분리될 수 있는가?",
        ["ETH 고유 최신 flow·사용·수수료·발행량", "가격·레버리지·프로토콜 위험의 현재 자료"],
        "발행 메커니즘 설명은 현재 network 활동이나 미래 수익을 입증하지 않는다.",
    ),
    "NATGAS": method(
        "NATGAS",
        "천연가스",
        "natural_gas",
        ["RA_EIA_GAS_WEEKLY", "RA_EIA_STEO_GAS"],
        [FX],
        "지역별 공급·소비·재고·LNG 수요와 선물곡선을 함께 검토한다.",
        "날씨·공급 증가·재고·선물 교체 비용·지역 가격 차이가 중요하다.",
        "LNG 수요와 겨울 소비가 공급 증가를 넘어 재고를 줄이는가?",
        "생산 증가와 예상 재고가 부족 서사를 약화시키는가?",
        ["Henry Hub 선물곡선·계약별 가격·roll 비용", "날씨·같은 주의 계절/장기 재고 비교·실제 투자상품"],
        "미국 Lower 48 재고와 EIA 전망의 범위다. 전망 재고는 실제 관측 재고가 아니다.",
    ),
    "US_EQUITY": method(
        "US_EQUITY",
        "S&P 500 / 미국 주식",
        "equity_index",
        ["DD_IDX_FACTSET_Q3", "DD_IDX_SPY", "DD_TR_H15_CURVE"],
        [*RATES, FX],
        "기업의 미래 이익·현금흐름과 지불한 가격을 구분하고 국채 대안과 비교한다.",
        "예상 이익 미달·배수 하락·집중·drawdown(큰 평가손실)·환율 위험이 있다.",
        "예상 이익 상향이 실제 매출·마진·현금흐름으로 이어지는가?",
        "높은 이익 기대와 금리 대안이 현재 가격의 추가 보상을 줄이는가?",
        ["전체 consensus→actual→후속 revision의 같은 정의 패널", "회사별 현금흐름과 전체 지수 기대의 연결"],
        "확보한 valuation·이익 근거는 S&P 500 중심이다. Nasdaq이나 미국 개별주 전체로 일반화하지 않는다.",
    ),
    "SHORT_BOND": method(
        "SHORT_BOND",
        "미국 단기 Treasury",
        "bond",
        ["MAC_H15_CASH_BILLS"],
        [*RATES, FX],
        "계약 이자와 원금·현재 시작 수익률·재투자를 검토한다.",
        "재투자·매도 가격·환율 위험이 있다. 달러 국채와 원화 생활비는 다르다.",
        "확인한 yield와 자금 사용 시점이 투자 목적에 맞는가?",
        "만기와 자금 필요 시점·환율 노출이 맞지 않는가?",
        ["실제 채권/ETF·만기·거래 YTM·비용·세금"],
        "H.15 기준금리는 실행 YTM이나 확정 기간수익이 아니다.",
    ),
    "LONG_BOND": method(
        "LONG_BOND",
        "미국 장기 Treasury",
        "bond",
        ["DD_TR_H15_CURVE"],
        [*RATES, FX],
        "장기 계약 현금흐름과 현재 yield를 검토한다.",
        "duration(금리 변화에 따른 가격 민감도)·물가·환율·중도 매도 위험이 중요하다.",
        "장기 이자와 기간이 자금 목적을 충족하는가?",
        "금리 상승 또는 조기 자금수요가 가격 손실을 키우는가?",
        ["실제 상품·계약 현금흐름·보유 기간·비용·세금"],
        "장기 국채의 낮은 신용 위험은 낮은 가격 위험을 뜻하지 않는다.",
    ),
    "CASH": method(
        "CASH",
        "현금과 현금성 자산",
        "cash",
        ["MAC_H15_CASH_BILLS"],
        [*RATES, FX],
        "현재 이자와 자금 접근성·대기의 선택 가치를 검토한다.",
        "물가·통화·발행기관·재투자와 포기한 투자기회를 확인한다.",
        "유동성과 이자가 필요 자금을 보존하는가?",
        "기회비용과 구매력 감소가 현금 유지의 장점을 넘는가?",
        ["사용자의 원화 예금/현금상품 계약금리·보호 범위"],
        "USD Treasury 금리를 한국 예금 금리로 대체하지 않는다.",
    ),
    "KR_EQUITY": method(
        "KR_EQUITY",
        "한국 주식 / 반도체",
        "equity_sector",
        ["KR_EXPORT_SEP2026_BRIEFING", "KR_SAMSUNG_2026Q2_RESULTS", "COM_HN_MEMORY_CYCLE_RISK"],
        [],
        "수출·산업 수급·기업 실적과 현재 가격 기대의 연결을 검토한다.",
        "메모리 사이클·수요·고객 비용 부담·집중 위험이 있다.",
        "산업 수요가 실제 기업의 이익·현금 회수로 이어지는가?",
        "공급과 사이클 변동이 성장 기대를 약화시키는가?",
        ["동일 시점 한국 지수 valuation·이익 전망 수정", "기업별 가격·현금흐름·SK하이닉스 공식 실적"],
        "한국 수출과 삼성전자 사례의 범위다. 특정 기업의 실적을 지수나 다른 기업에 복제하지 않는다.",
    ),
    "GOLD": method(
        "GOLD",
        "금",
        "commodity",
        ["RA_FED_REAL_YIELD"],
        [FX],
        "수요·통화/실질금리와 보유 비용을 검토한다. 계약 이자를 제공하지 않는다.",
        "가격·실질금리·환율·보유 상품 비용이 중요하다.",
        "직접 수요와 통화 환경이 금 보유 이유를 강화하는가?",
        "금리 대안과 현재 가격이 보유 이유를 약화시키는가?",
        ["현재 금 가격·직접 수요/수급·상품 비용"],
        "실질금리 자료만으로 금의 매력을 확정하지 않는다.",
    ),
    "ENERGY": method(
        "ENERGY",
        "에너지 / 원유",
        "commodity",
        ["RA_EIA_OIL_WEEKLY", "RA_EIA_STEO_OIL"],
        [FX],
        "실물 수급·재고·공급 차질과 복구를 검토한다.",
        "경기 수요·정책·지정학·선물 교체와 지역 가격 위험이 있다.",
        "공급 차질이 실제 재고와 가격 조건을 바꾸는가?",
        "공급 복구 또는 수요 약화가 부족 서사를 약화시키는가?",
        ["계약별 선물 가격·현재 상품 구조·수요의 추가 관측"],
        "원유 전망을 천연가스 수급 모형으로 대체하지 않는다.",
    ),
    "KR_REALESTATE": method(
        "KR_REALESTATE",
        "한국 주거 부동산",
        "real_estate",
        ["KR_HOUSING_SUPPLY_20260813", "KR_REB_WEEK_20260928_METADATA"],
        [],
        "실거주 편익·임대 현금흐름·금융비용·매매 가격을 분리한다.",
        "대출·거래 유동성·전세보증금·공급·정책·큰 단일 노출을 검토한다.",
        "실거래·전세·공급·금융비용이 실제 물건의 경제성을 지지하는가?",
        "금융비용·매도 지연·지역 공급이 주거/투자 목적을 약화시키는가?",
        ["지역/단지/면적별 최신 실거래·거래량·전세·공급 연결", "물건 가격·대출·실거주 기간·사용자 자금 제약"],
        "국가 공급정책과 통계 게시물 범위만 지원한다. 동탄 개별 아파트의 가격·가치 분석은 미지원이다.",
    ),
}
SCAN_ASSETS = (
    'CASH',
    'SHORT_BOND',
    'LONG_BOND',
    'US_EQUITY',
    'KR_EQUITY',
    'GOLD',
    'ENERGY',
    'NATGAS',
    'BTC',
    'ETH',
    'KR_REALESTATE',
)


def resolve_subject(subject: Subject) -> AssetMethod | None:
    # A named country or numeric tenor is not a synonym for the generic
    # Treasury method. No connector for those conditions is added here.
    if subject.method_family == 'bond':
        if subject.country not in (None, 'US') or subject.maturity is not None:
            return None
        if subject.duration:
            if subject.duration.descriptor == 'intermediate':
                return None
            identifier = {'short': 'SHORT_BOND', 'long': 'LONG_BOND'}.get(subject.duration.descriptor)
            if identifier:
                return METHODS[identifier]
    if subject.method_family == 'real_estate' and subject.country not in (None, 'KR'):
        return None
    if subject.method_family == 'real_estate' and subject.regions:
        # Preserve the local question and its economics while withholding
        # nationwide catalog sources that cannot establish this local market.
        region = ' / '.join(subject.regions)
        return replace(
            METHODS['KR_REALESTATE'],
            id='SCOPED_REALESTATE_'
            + _digest({'country': subject.country, 'regions': subject.regions, 'subject': subject.label})[:12],
            label=subject.label,
            source_ids=(),
            macro_ids=(),
            missing=(
                region
                + ' 조건을 지원할 최신 실거래·거래량·전세·공급 자료 연결이 없다. 현재 이 조건을 지원할 데이터가 부족하다.',
                '개별 아파트의 가격·대출·임대 현금흐름·사용자 자금 제약',
            ),
            scope_note=region
            + '의 투자 관점을 유지한다. 전국 정책·통계 게시물은 해당 지역의 투자 경제성 자료로 대체하지 않는다.',
        )
    if subject.country == 'KR' and subject.method_family not in ('bond', 'real_estate'):
        if subject.label not in ('한국 주식', '한국 반도체', '반도체', '삼성전자', '한국 배당주'):
            return None
    elif subject.country not in (None, 'US', 'KR'):
        return None
    if subject.label == '국채':
        return replace(
            METHODS['SHORT_BOND'],
            missing=(*METHODS['SHORT_BOND'].missing, '질문에서 생략된 발행국·통화·원하는 만기를 확인해야 한다.'),
            scope_note='이번에 확보한 자료는 미국 Treasury다. 발행국이 지정되지 않아 한국 국채·원화 수익률의 분석으로 해석할 수 없다.',
        )
    mapping = {
        "Bitcoin": "BTC",
        "Ethereum": "ETH",
        "천연가스": "NATGAS",
        "S&P 500": "US_EQUITY",
        "미국 주식": "US_EQUITY",
        "국채": "SHORT_BOND",
        "미국 국채": "SHORT_BOND",
        "단기 국채": "SHORT_BOND",
        "장기 국채": "LONG_BOND",
        "한국 주식": "KR_EQUITY",
        "한국 반도체": "KR_EQUITY",
        "반도체": "KR_EQUITY",
        "현금": "CASH",
        "금": "GOLD",
        "원유": "ENERGY",
        "동탄 주거 부동산": "KR_REALESTATE",
    }
    identifier = mapping.get(subject.label)
    if identifier:
        return METHODS[identifier]
    if subject.method_family == "real_estate":
        return METHODS["KR_REALESTATE"]
    if subject.label == "삼성전자":
        return method(
            "SAMSUNG",
            "삼성전자",
            "equity",
            ["KR_SAMSUNG_2026Q2_RESULTS"],
            [],
            METHODS['KR_EQUITY'].economics,
            METHODS['KR_EQUITY'].downside,
            METHODS['KR_EQUITY'].bull_question,
            METHODS['KR_EQUITY'].bear_question,
            ["현재 주가·동일 정의 valuation·consensus/revision·현금흐름"],
            "삼성전자 공식 실적만 조사한다. 다른 기업에 일반화하지 않는다.",
        )
    if subject.label in {"Microsoft", "Alphabet", "Amazon", "Meta", "NVIDIA"}:
        sources = {
            "Microsoft": ["DD_MSFT_Q4", "DD_MSFT_Q3"],
            "Alphabet": ["DD_GOOGL_Q2"],
            "Amazon": ["DD_AMZN_Q2", "DD_AMZN_Q2_OPERATING"],
            "Meta": ["DD_META_Q2", "DD_META_Q1"],
            "NVIDIA": ["DD_NVDA_Q2"],
        }
        return method(
            "COMPANY_" + subject.label.upper(),
            subject.label,
            "equity",
            sources[subject.label],
            [FX],
            "실제 사업·이익·현금흐름과 지불한 가격을 구분한다.",
            "실적 미달·투자 회수·경쟁·가격 기대의 위험이 있다.",
            "성장이 반복 가능한 이익·현금으로 이어지는가?",
            "높은 가격 기대나 투자 지출이 좋은 사업의 투자 보상을 낮추는가?",
            ["현재 주가·valuation·기업별 consensus/revision·투자 회수 자료"],
            "명시한 기업의 검토한 공시 판본만 사용한다.",
        )
    if subject.label in {"배당 투자", "한국 배당주", "성장주", "가치주"}:
        source = {
            "배당 투자": "US_SPDR_DIVIDEND",
            "한국 배당주": None,
            "성장주": "US_SPDR_GROWTH",
            "가치주": "US_SPDR_VALUE",
        }[subject.label]
        if source is None:
            return None
        return method(
            "STRATEGY_" + source.rsplit('_', 1)[1],
            subject.label,
            "equity_strategy",
            [source],
            [FX],
            "전략의 총수익·기업의 지속성과 실행 상품을 구분한다.",
            "배당 감소·스타일 집중·비용·세금 위험이 있다.",
            "지속 가능한 현금 창출력과 실행 조건이 전략 목적에 맞는가?",
            "높은 분배율이나 스타일 명칭이 약한 총수익·집중을 가리는가?",
            ["전략별 기업의 지속성·동일 기간 총수익·상품/계좌 비용"],
            "미국 발행사 상품은 전략의 제한된 사례이며 한국 전략의 대체 자료가 아니다.",
        )
    if subject.label in {"SPY", "IBIT", "ETHA"}:
        underlying = METHODS[{"SPY": "US_EQUITY", "IBIT": "BTC", "ETHA": "ETH"}[subject.label]]
        source = {"SPY": "DD_IDX_SPY", "IBIT": "CR_IBIT_ISSUER", "ETHA": "CR_ETHA_ISSUER"}[subject.label]
        return method(
            "ETF_" + subject.label,
            subject.label,
            "etf",
            [source],
            [FX],
            underlying.economics,
            underlying.downside,
            underlying.bull_question,
            underlying.bear_question,
            ["보수·추적 차이·과세·실제 거래 조건"],
            "기초 노출과 해당 ETF의 실현 성과·계좌 제약을 구분한다.",
        )
    if subject.label == '원자재':
        from .scan import universe

        return next(m for m in universe(False) if m.id == 'BROAD_COMMODITIES')
    return None


@dataclass(frozen=True)
class ResearchCatalog:
    sources: dict
    macro: dict
    quoted_facts: dict
    synthetic: bool = False
    findings: tuple[dict, ...] = ()
    discovery: dict | None = None
    korean: dict | None = None
    semiconductor: dict | None = None
    scan: dict | None = None
    commodity: dict | None = None

    @property
    def digest(self):
        return _digest(
            {
                "sources": self.sources,
                "macro": self.macro,
                "facts": self.quoted_facts,
                "methods": [asdict(value) for value in METHODS.values()],
                "version": CATALOG_VERSION,
                "synthetic": self.synthetic,
                "findings": self.findings,
                **({"discovery": self.discovery} if self.discovery is not None else {}),
                **({"korean": self.korean} if self.korean is not None else {}),
                **({"semiconductor": self.semiconductor} if self.semiconductor is not None else {}),
                **({"scan": self.scan} if self.scan is not None else {}),
                **({"commodity": self.commodity} if self.commodity is not None else {}),
            }
        )


def load_catalog() -> ResearchCatalog:
    root = Path(__file__).parent / "catalog"
    return ResearchCatalog(
        *(load_pins(root / name) for name in ("sources.json", "macro.json", "quoted_facts.json")),
        findings=tuple(load_pins(root / 'findings.json')['findings']),
        discovery=load_pins(root / 'discovery.json'),
        korean=load_pins(root / 'korean.json'),
        semiconductor=load_pins(root / 'semiconductor.json'),
        scan=load_pins(root / 'scan.json'),
        commodity=load_pins(root / 'commodity.json'),
    )


def project_sources(catalog, methods, question, day):
    """Project source scope, but keep original dates, quotes and definitions."""
    originals = {source['id']: source for source in catalog.sources['sources']}
    assignments = {}
    for item in methods:
        for identifier in item['source_ids']:
            assignments.setdefault(identifier, set()).add(item['id'])
    # Referenced originals are part of this scoped question, not another mode.
    # Preserve attribution and independent-origin counting when a commentary
    # cites an official source already used elsewhere in the same ask.
    pending = list(assignments)
    while pending:
        identifier = pending.pop()
        original = originals.get(identifier)
        if original and original.get('origin_source_id'):
            parent = original['origin_source_id']
            if parent not in originals:
                raise ValueError('catalog source origin is missing')
            before = set(assignments.get(parent, ()))
            assignments.setdefault(parent, set()).update(assignments[identifier])
            if assignments[parent] != before:
                pending.append(parent)
    data = dict(
        schema_version='1',
        id='ASK_SELECTED_SOURCES',
        question=question,
        as_of=day.isoformat(),
        asset_ids=[item['id'] for item in methods],
        sources=[],
        evidence=[],
        claims=[],
    )
    for identifier in sorted(assignments):
        if identifier not in originals:
            raise SourceError('selected catalog source is missing: ' + identifier)
        spec = deepcopy(originals[identifier])
        spec['asset_ids'] = [item['id'] for item in methods if item['id'] in assignments[identifier]]
        data['sources'].append(spec)
    scope = {item['id']: item['asset_ids'] for item in data['sources']}
    for original in catalog.sources['evidence']:
        if original['source_id'] in scope:
            item = deepcopy(original)
            item['interpretation'] = None
            data['evidence'].append(item)
    available = {item['id'] for item in data['evidence']}
    for original in catalog.sources['claims']:
        refs = {*original['support_ids'], *original['counter_ids'], *original['context_ids']}
        if original.get('narrative_evidence_id'):
            refs.add(original['narrative_evidence_id'])
        if refs and refs <= available:
            item = deepcopy(original)
            compatible = set(data['asset_ids'])
            for ref in refs:
                eid = next(e for e in data['evidence'] if e['id'] == ref)
                compatible &= set(scope[eid['source_id']])
            if compatible:
                item['asset_ids'] = sorted(compatible)
                item['review'] = {
                    'status': 'pending',
                    'reviewer': None,
                    'reviewed_at': None,
                    'rationale': '경제적 의미 검토 전 주장이다. 원문과 반대 근거를 대조한다.',
                }
                item['verification'] = 'unverified'
                data['claims'].append(item)
    # Every selected asset gets a traceable thesis check, never an automatic verdict.
    for item in methods:
        refs = [e['id'] for e in data['evidence'] if item['id'] in scope[e['source_id']]]
        data['claims'].append(
            dict(
                id='ASK_THESIS_' + item['id'],
                text=item['bull_question'],
                asset_ids=[item['id']],
                rule='reviewed_links_v1',
                support_ids=[],
                counter_ids=[],
                context_ids=refs,
                narrative_evidence_id=None,
                verification='unverified',
                review={
                    'status': 'pending',
                    'reviewer': None,
                    'reviewed_at': None,
                    'rationale': '가설의 사실 확인과 가격 매력 판단은 아직 완료되지 않았다.',
                },
                limitations=['배경 원문을 가설의 증명으로 승격하지 않는다.'],
                recheck=item['bear_question'],
            )
        )
    return data if data['sources'] else None


def project_macro(catalog, ids):
    if not ids:
        return None
    data = deepcopy(catalog.macro)
    data['id'] = 'ASK_SELECTED_MACRO'
    data['series'] = [item for item in data['series'] if item['canonical_id'] in ids]
    data['bindings'] = [item for item in data['bindings'] if item['series_id'] in ids]
    sources = {item['source_id'] for item in data['bindings']} | {
        item.get('release_source_id') for item in data['bindings']
    }
    data['sources'] = [item for item in data['sources'] if item['id'] in sources]
    data['yoy_series_ids'] = [identifier for identifier in data['yoy_series_ids'] if identifier in ids]
    if data['yield_pair'] is not None and not set(data['yield_pair']) <= set(ids):
        data['yield_pair'] = None
    return data
