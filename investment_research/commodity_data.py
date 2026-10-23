"""Reviewed commodity documents inside the existing need/acquire/evidence flow.

No routing, crawler, forecast model or investment score. The optional decoder
is restricted to named official commodity PDFs; stored excerpt replay needs
neither a PDF decoder nor a network connection.
"""

from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, localcontext
from functools import lru_cache
import calendar
import csv
import re
from urllib.parse import urlsplit

from .sources import SourceError, _decode, _time, _visible_html
from .discovery_contracts import definition, html_records, json_document
from .scan_minimum import _record, _result
from .models import MetricResult

VERSION = 'commodity_deep_evidence_v1'
NAMES = {'commodity_deep': '질문에 필요한 원자재 실제 수급·계약·상품 자료'}
ASSETS = {'NATGAS', 'GOLD', 'BROAD_COMMODITIES'}
CME = 'https://www.cmegroup.com/daily_bulletin/current/'
GSG_PROSPECTUS = 'https://www.ishares.com/us/literature/prospectus/p-ishares-s-and-p-gsci-commodity-indexed-trust-prospectus-12-31.pdf'
GSCI_DASHBOARD = 'https://www.spglobal.com/spdji/en/documents/performance-reports/dashboard-daily-global-markets.pdf'
WGC_Q2 = 'https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-q2-2026'
WGC_ETF = 'https://www.gold.org/goldhub/data/global-gold-backed-etf-holdings-and-flows'
HISTORY = 'https://www.eia.gov/dnav/ng/hist/nw2_epg0_swo_r48_bcfw.htm'

# Explicit constituent identities; no government collateral masquerades as
# commodity sector weights. All displayed weights become traceable inputs.
GROUPS = {
    'energy': ('LCO', 'CL', 'LGO', 'HO', 'RB', 'NG'),
    'industrial': ('MCU', 'MAL', 'MNI', 'MZN', 'MPB'),
    'precious': ('GC', 'SI'),
    'agriculture': ('C', 'S', 'W', 'KW', 'KC', 'SB', 'CT', 'CC'),
    'livestock': ('LC', 'LH', 'FC'),
}
PDF_PATHS = {
    ('www.cmegroup.com', '/daily_bulletin/current/Section61_Energy_Futures_Products.pdf'),
    ('www.cmegroup.com', '/daily_bulletin/current/Section62_Metals_Futures_Products.pdf'),
    ('www.cmegroup.com', '/daily_bulletin/current/Section03_Agricultural_Futures.pdf'),
    ('www.ishares.com', urlsplit(GSG_PROSPECTUS).path),
    ('www.usda.gov', '/oce/commodity/wasde/wasde0926.pdf'),
    ('www.spglobal.com', urlsplit(GSCI_DASHBOARD).path),
}


def pdf_supported(url):
    p = urlsplit(url)
    return (p.hostname, p.path) in PDF_PATHS and not p.query


@lru_cache(maxsize=12)
def pdf_text(body):
    if len(body) > 2 * 1024 * 1024 or not body.startswith(b'%PDF-'):
        raise SourceError('bounded genuine commodity PDF required')
    from .semiconductor_data import pdf_text as bounded_decoder

    text = bounded_decoder(body)
    if len(text.encode('utf-8')) > 2 * 1024 * 1024:
        raise SourceError('decoded commodity text exceeds limit')
    return text


def text_document(response, url):
    if response.content_type.split(';')[0] == 'application/pdf':
        if not pdf_supported(url):
            raise SourceError('unreviewed commodity PDF identity')
        return pdf_text(response.body)
    return _visible_html(_decode(response.body, response.content_type))


def evidence_needs(methods, tasks, *, scan=False):
    ids = {m['id'] for m in methods} & ASSETS
    if not ids:
        return []
    from .scan_minimum import needs as minimum_needs

    out = (
        []
        if scan
        else minimum_needs([m for m in methods if m['id'] in ids], {'method_version': 'evidence_shortlist_v7'})
    )

    def add(asset, blocks, age):
        for block in blocks:
            out.append(
                dict(
                    id='NEED_DEEP_' + asset + '_' + block.upper(),
                    asset_id=asset,
                    category='commodity_deep',
                    block=block,
                    label=asset + ' ' + block,
                    reason='기초자산 수급과 실제 상품 경제성을 분리할 질문별 원자료',
                    max_age_seconds=age * 86400,
                    max_selected=1,
                )
            )

    if scan:
        if 'NATGAS' in ids:
            add('NATGAS', ['gas_curve_a', 'gas_curve_b'], 5)
        if 'GOLD' in ids:
            add('GOLD', ['gold_etf', 'gold_central'], 100)
        # Three leading constituent weights suffice as a bounded composition
        # clue for Scan. Deep Dive opens all twenty-four from the same document.
        if 'BROAD_COMMODITIES' in ids:
            add('BROAD_COMMODITIES', ['weights_0'], 365)
        return out
    if 'NATGAS' in ids:
        add('NATGAS', ['gas_curve_a', 'gas_curve_b'], 5)
        add('NATGAS', ['gas_history_a', 'gas_history_b', 'gas_prev_reference_a', 'gas_prev_reference_b'], 14)
        add('NATGAS', ['hdd', 'cdd', 'position', 'position_change'], 14)
        add('NATGAS', ['ung_terms', 'ung_fees', 'boil_terms', 'boil_supplement'], 400)
        add('NATGAS', ['ung_holdings'], 135)
    if 'GOLD' in ids:
        add('GOLD', ['gold_etf'], 70)
        add('GOLD', ['gold_central', 'gold_physical'], 130)
        add('GOLD', ['gold_dollar', 'position', 'position_change', 'gold_futures'], 14)
        add('GOLD', ['iau_terms'], 30)
    if 'BROAD_COMMODITIES' in ids:
        add('BROAD_COMMODITIES', ['weights_' + str(i) for i in range(8)], 365)
        add('BROAD_COMMODITIES', ['gsg_terms'], 365)
        add('BROAD_COMMODITIES', ['gsg_fee'], 30)
        add('BROAD_COMMODITIES', ['broad_energy', 'broad_energy_curve', 'broad_metals', 'broad_agri'], 5)
        add('BROAD_COMMODITIES', ['wasde_corn', 'wasde_wheat'], 60)
        add('BROAD_COMMODITIES', ['gsci_groups_a', 'gsci_groups_b', 'gsci_energy', 'gsci_roll', 'gsci_gold'], 14)
        # Reuse exact EIA/gold documents in the same acquisition cache. Scope
        # remains one component market, never the entire commodity basket.
        for block in ('oil_price', 'oil_stock', 'gold', 'real', 'iau', 'gsg'):
            out.append(
                dict(
                    id='NEED_DEEP_BROAD_' + block.upper(),
                    asset_id='BROAD_COMMODITIES',
                    category={
                        'oil_price': 'scan_energy',
                        'oil_stock': 'scan_energy',
                        'gold': 'scan_gold',
                        'real': 'scan_real_rate',
                        'iau': 'scan_gold_demand',
                        'gsg': 'scan_broad',
                    }[block],
                    block=block,
                    label='광범위 원자재의 ' + block + ' 하위시장',
                    reason='개별 하위시장과 전체 바스켓을 구분',
                    max_age_seconds=(14 if block.startswith('oil') else 10) * 86400,
                    max_selected=1,
                )
            )
        add('BROAD_COMMODITIES', ['gold_etf'], 70)
    return out


def policy(base, methods, needs, now, *, scan=False):
    po = deepcopy(base)
    if not scan:
        from .scan_minimum import policy as minimum_policy

        # Same reviewed contracts, without changing Scan or adding a Scan mode.
        po = minimum_policy(po, methods, needs, now, {'method_version': 'evidence_shortlist_v7'})
        # Keep only providers relevant to this independent question.
        ids = {m['id'] for m in methods}
        if 'BROAD_COMMODITIES' in ids:
            for p in po['providers']:
                if p['id'] in ('MIN_EIA', 'MIN_SSGA', 'MIN_REAL_RATE', 'MIN_ISHARES'):
                    p['asset_ids'] = list(dict.fromkeys([*p['asset_ids'], 'BROAD_COMMODITIES']))
                if p['id'] == 'MIN_ISHARES':
                    p['documents']['iau']['contract'] = 'minimum_deep_component_iau_v1'
        po['providers'] = [
            p
            for p in po['providers']
            if set(p['categories']) & {n['category'] for n in needs}
            and (not p.get('asset_ids') or set(p['asset_ids']) & ids)
        ]
    specs = {}

    def doc(block, url, contract='minimum_deep_document_v1'):
        specs[block] = dict(seed_url=url, contract=contract, identity_fields={'block': block})

    for block in ('gas_curve_a', 'gas_curve_b', 'broad_energy', 'broad_energy_curve'):
        doc(block, CME + 'Section61_Energy_Futures_Products.pdf')
    for block in ('gas_history_a', 'gas_history_b', 'gas_prev_reference_a', 'gas_prev_reference_b'):
        doc(block, HISTORY)
    for block in ('hdd', 'cdd'):
        doc(
            block,
            'https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/cdus/degree_days/wsa'
            + ('hddy' if block == 'hdd' else 'cddy')
            + '.txt',
        )
    for block in ('position', 'position_change'):
        doc(block, 'https://www.cftc.gov/dea/newcot/f_disagg.txt')
    for block in ('gold_etf',):
        doc(block, WGC_ETF)
    for block in ('gold_central', 'gold_physical'):
        doc(block, WGC_Q2)
    doc('gold_dollar', 'https://www.federalreserve.gov/releases/h10/current/')
    doc('iau_terms', 'https://www.ishares.com/us/products/239561/ishares-gold-trust-fund')
    for i in range(8):
        doc('weights_' + str(i), GSG_PROSPECTUS)
    doc('gsg_terms', GSG_PROSPECTUS)
    doc('gsg_fee', 'https://www.ishares.com/us/products/239757/ishares-sp-gsci-commodityindexed-trust-fund')
    for block in ('broad_metals', 'gold_futures'):
        doc(block, CME + 'Section62_Metals_Futures_Products.pdf')
    doc('broad_agri', CME + 'Section03_Agricultural_Futures.pdf')
    for block in ('wasde_corn', 'wasde_wheat'):
        doc(block, 'https://www.usda.gov/oce/commodity/wasde/wasde0926.pdf')
    for block in ('gsci_groups_a', 'gsci_groups_b', 'gsci_energy', 'gsci_roll', 'gsci_gold'):
        doc(block, GSCI_DASHBOARD)
    # Attach document blocks to the same bounded provider when possible.
    groups = {}
    for n in needs:
        if n['category'] != 'commodity_deep' or n['block'] not in specs:
            continue
        entry = specs[n['block']]
        host = urlsplit(entry['seed_url']).hostname
        groups.setdefault(host, {})[n['block']] = entry
    existing = {urlsplit(p['seed_url']).hostname: p for p in po['providers'] if p['method'] == 'reviewed_document'}
    names = {
        'www.cmegroup.com': ('CME Group', 'primary'),
        'www.eia.gov': ('U.S. Energy Information Administration', 'primary'),
        'www.cpc.ncep.noaa.gov': ('NOAA Climate Prediction Center', 'primary'),
        'www.cftc.gov': ('CFTC', 'primary'),
        'www.gold.org': ('World Gold Council', 'data_provider'),
        'www.federalreserve.gov': ('Board of Governors of the Federal Reserve System', 'primary'),
        'www.ishares.com': ('BlackRock iShares', 'institution'),
        'www.usda.gov': ('USDA WASDE', 'primary'),
        'www.spglobal.com': ('S&P Dow Jones Indices', 'primary'),
    }
    for host, documents in groups.items():
        chunks = [dict(list(documents.items())[i : i + 8]) for i in range(0, len(documents), 8)]
        for j, chunk in enumerate(chunks):
            p = existing.get(host) if j == 0 else None
            if p and len(p.get('documents', {})) + len(chunk) > 8:
                p = None
            if p:
                if 'documents' not in p:
                    oldblock = p.get('identity_fields', {}).get('block') or next(
                        (n.get('block') for n in needs if n['category'] in p['categories']), None
                    )
                    p['documents'] = {
                        oldblock
                        or 'base_document': dict(
                            seed_url=p['seed_url'], contract=p['contract'], identity_fields=p.get('identity_fields', {})
                        )
                    }
                p['documents'].update(chunk)
                p['categories'] = list(dict.fromkeys([*p['categories'], 'commodity_deep']))
                p['asset_ids'] = list(
                    dict.fromkeys([*p.get('asset_ids', []), *(n['asset_id'] for n in needs if n.get('block') in chunk)])
                )
            else:
                publisher, kind = names[host]
                entry = next(iter(chunk.values()))
                po['providers'].append(
                    dict(
                        id='DEEP_' + host.split('.')[1].upper() + '_' + str(j),
                        publisher=publisher,
                        type=kind,
                        canonical=True,
                        jurisdiction='document_specific',
                        categories=['commodity_deep'],
                        asset_ids=list(ASSETS),
                        method='reviewed_document',
                        **entry,
                        documents=chunk,
                        candidate_hosts=[host],
                        access_method='public_http',
                        policy_url=entry['seed_url'],
                        policy_note='요청별 검토한 공식/원발행 문서의 최대 세 작은 필드·원문 구절·hash를 개인 연구용 귀속 excerpt로 보존. 전체 데이터 재배포/접근 제한 우회/외부 명령 실행 없음.',
                    )
                )
    if not scan:
        for asset, cik, blocks in [
            ('NATGAS', '1376227', ('ung_terms', 'ung_fees', 'ung_holdings')),
            ('NATGAS', '1415311', ('boil_terms', 'boil_supplement')),
        ]:
            if not any(n['asset_id'] == asset and n.get('block') in blocks for n in needs):
                continue
            po['providers'].append(
                dict(
                    id='DEEP_SEC_' + cik,
                    publisher='USCF' if cik == '1376227' else 'ProShares Trust II',
                    type='primary',
                    canonical=True,
                    jurisdiction='US',
                    categories=['commodity_deep'],
                    asset_ids=[asset],
                    blocks=list(blocks),
                    method='publisher_links',
                    seed_url='https://data.sec.gov/submissions/CIK' + cik.zfill(10) + '.json',
                    contract='minimum_deep_sec_v1',
                    identity_fields={'cik': cik},
                    candidate_hosts=['www.sec.gov', 'data.sec.gov'],
                    max_candidates=1,
                    access_method='public_http',
                    policy_url='https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data',
                    policy_note='공식 SEC submissions 등록에서 관련 최신 공시 URL·발표일을 발견하고 실제 본문을 열어 확인. 등록만으로 상품 조건/현재 보유 확인 불가. 2MiB 초과/접근 실패면 gap, 최신 공시를 구판으로 대체하지 않음.',
                )
            )
    po.update(scan_extension='commodity_deep_v1', max_requests=64)
    return po


def filing_candidates(provider, need, response):
    doc = json_document(response)
    cik = provider['identity_fields']['cik']
    if str(int(doc['cik'])) != cik:
        raise SourceError('wrong SEC issuer directory')
    rows = doc['filings']['recent']
    block = need['block']
    form = '10-Q' if block == 'ung_holdings' else '424I' if block == 'boil_supplement' else '424B3'
    indexes = [i for i, f in enumerate(rows['form']) if f == form]
    if not indexes:
        raise SourceError('required primary filing not in current issuer directory')
    latest = max(rows['filingDate'][i] for i in indexes)
    choices = [i for i in indexes if rows['filingDate'][i] == latest]
    # BOIL's short registration supplement is a named fund list, not terms.
    # It is intentionally opened as a separate registration evidence category.
    if block == 'boil_supplement':
        choices = choices[1:2]
    out = []
    for i in choices[:1]:
        url = (
            'https://www.sec.gov/Archives/edgar/data/'
            + cik
            + '/'
            + rows['accessionNumber'][i].replace('-', '')
            + '/'
            + rows['primaryDocument'][i]
        )
        out.append(
            (
                url,
                dict(
                    block=block,
                    cik=cik,
                    form=form,
                    published_at=rows['filingDate'][i],
                    report_date=rows['reportDate'][i],
                ),
            )
        )
    return out


def _numeric(token, measure, unit, period, currency, scope, adjustment, locator):
    return _record(token, measure, unit, period, currency, scope, adjustment, locator, grouped=',' in token)


def _quote(text, measure, period, scope, adjustment, locator):
    q = ' '.join(text.split())
    if not 1 <= len(q) <= 1100:
        raise SourceError('bounded commodity quotation required')
    return dict(
        quote=q,
        locator=locator,
        definition=definition(measure, 'text', period, None, scope, adjustment),
        extraction=None,
        label=measure,
        limitations=[],
    )


def _bulletin(text):
    dates = set(re.findall(r'(?:Mon|Tue|Wed|Thu|Fri), ([A-Z][a-z]{2} \d{2}, \d{4})', text))
    if len(dates) != 1 or 'SETT.' not in text:
        raise SourceError('unique CME bulletin observation and settlement column required')
    day = datetime.strptime(dates.pop(), '%b %d, %Y').date()
    return day, 'preliminary' if 'PRELIMINARY' in text else 'final'


def _future_rows(text, heading):
    match = re.search(r'^' + re.escape(heading) + r'\s*\n(.*?)(?=^TOTAL|^[A-Z0-9]{1,5} FUT|\Z)', text, re.M | re.S)
    if not match:
        raise SourceError('named CME contract table absent')
    rows = {}
    for line in match[1].splitlines():
        m = re.match(r'^([A-Z]{3}\d{2})\s+\S+\s+\S+(?:\s*/\s*\S+)?\s+([\d.]+)\s+([+-]|UNCH)\s*(\d+(?:\.\d+)?)?', line)
        if m:
            month = datetime.strptime(m[1], '%b%y').strftime('%Y-%m')
            if month in rows:
                raise SourceError('duplicate futures delivery month')
            rows[month] = (m[2], m[3], m[4], line)
    if not rows:
        raise SourceError('settlement rows not parsed; no guessed price')
    return rows


def _corn_row(line):
    # Agricultural bulletin columns are open, high, low, settlement. Some
    # layouts put a slash before low; settlement is never a fixed word index.
    match = re.match(r"^([A-Z]{3}\d{2})\s+\S+\s+\S+\s+(?:/\s*)?\S+\s+(\d+'[0246])\s+(?:[+-](?:\s|$)|UNCH\b)", line)
    if not match:
        raise SourceError('corn settlement columns/eighth-cent quote changed')
    return datetime.strptime(match[1], '%b%y').strftime('%Y-%m'), match[2]


def _gsci_returns(raw, block):
    """Named official dashboard rows, one date and USD YTD return definition.

    No chart-label inference, weights-times-returns attribution, or subtraction
    of distinct indices to manufacture roll/collateral returns.
    """
    pages = [p for p in raw.split('\f') if re.search(r'^\s*S&P GSCI Indices\s+', p, re.M)]
    if len(pages) != 1:
        raise SourceError('unique commodity dashboard page required')
    page = pages[0]
    if (
        'INDEX INVESTMENT STRATEGY: Daily Index Dashboard' not in page
        or not re.search(r'INDEX\s+Daily\s+MTD\s+YTD\s+12M', page)
        or 'Index performance based on total return except the S&P Global Carbon Credit' not in page
        or 'Returns are in USD unless otherwise stated.' not in page
    ):
        raise SourceError('official commodity USD total-return table definition missing')
    labels = set(re.findall(r'\b([A-Z][a-z]+ \d{1,2}, \d{4})\b', page))
    if len(labels) != 1:
        raise SourceError('unique commodity dashboard as-of date required')
    day = datetime.strptime(labels.pop(), '%B %d, %Y').date().isoformat()
    blocks = {
        'gsci_groups_a': [('Energy', 'ENERGY'), ('Industrial Metals', 'INDUSTRIAL'), ('Precious Metals', 'PRECIOUS')],
        'gsci_groups_b': [('Agriculture', 'AGRICULTURE'), ('Livestock', 'LIVESTOCK'), ('S&P GSCI', 'BROAD')],
        'gsci_energy': [('Natural Gas', 'NATGAS'), ('WTI Crude', 'WTI'), ('Brent Crude', 'BRENT')],
        'gsci_roll': [('Dynamic Roll', 'DYNAMIC_ROLL'), ('3M Forward', '3M_FORWARD'), ('Light Energy', 'LIGHT_ENERGY')],
        'gsci_gold': [('Gold', 'GOLD'), ('Physical Gold (Spot)', 'PHYSICAL_GOLD_SPOT')],
    }
    records = []
    for label, key in blocks[block]:
        pct = r'(-?\d+(?:\.\d+)?)%'
        matches = list(re.finditer(r'(?:^|\s{2,})' + re.escape(label) + r'\s+' + r'\s*'.join([pct] * 4), page, re.M))
        if len(matches) != 1:
            raise SourceError('unique named GSCI dashboard return row required: ' + label)
        spot = key == 'PHYSICAL_GOLD_SPOT'
        records.append(
            _numeric(
                matches[0][3],
                'SP_GSCI_' + key + '_YTD_' + ('SPOT_RETURN' if spot else 'TOTAL_RETURN'),
                'percent',
                day,
                'USD',
                ('Physical Gold (Spot)' if spot else 'S&P GSCI' if key == 'BROAD' else 'S&P GSCI ' + label),
                'USD_'
                + ('physical_gold_spot_price_return' if spot else 'total_return')
                + '_YTD_prior_calendar_year_end_to_observation_not_contribution',
                'text:Commodity dashboard / ' + label + ' / YTD; Daily, MTD, YTD, 12M verified',
            )
        )
    return _result(
        records,
        day,
        limitations=[
            'S&P 원발행 USD YTD 성과: 전년말부터 명시 관측일. 지수 총수익과 GSG NAV 총수익·현재 구성비·공식 성과 기여는 다르다.',
            'roll 방법/계약월/에너지 비중을 바꾼 지수 차이는 전략 차이이며 실현 roll 수익·담보 이자 분해가 아니다.',
            'Physical Gold (Spot)는 별도 현물 가격 기준이다. 금 선물 total return과의 차이를 roll/collateral로 확정하지 않는다.',
        ],
    )


def parse_candidate(contract, response, candidate):
    block = candidate['index_identity_fields']['block']
    asset = candidate['asset_id']
    url = candidate['url']
    if contract == 'minimum_deep_component_iau_v1':
        if asset != 'BROAD_COMMODITIES' or block != 'iau':
            raise SourceError('reviewed IAU component scope required')
        from .scan_minimum import parse_supplement

        result = parse_supplement('minimum_iau_v2', response, {**candidate, 'asset_id': 'GOLD'})
        result['limitations'].append(
            '광범위 원자재의 금 하위시장 맥락으로 재사용. 한 금 신탁 보유량을 전체 원자재 수요로 확대하지 않는다.'
        )
        return result
    raw = text_document(response, url)
    text = ' '.join(raw.split())
    records = []
    if block.startswith('gsci_'):
        if url != GSCI_DASHBOARD or asset != 'BROAD_COMMODITIES':
            raise SourceError('reviewed primary GSCI dashboard scope required')
        return _gsci_returns(raw, block)
    if block in ('gas_curve_a', 'gas_curve_b', 'broad_energy', 'broad_energy_curve', 'broad_metals', 'gold_futures'):
        day, state = _bulletin(raw)
        heading = (
            'NG FUT               NATURAL GAS HENRY HUB (PHYSICAL)'
            if block.startswith('gas_curve')
            else (
                'CL FUT               NYMEX CRUDE OIL (PHYSICAL)'
                if block.startswith('broad_energy')
                else (
                    'HG FUT               COMEX COPPER FUTURES'
                    if block == 'broad_metals'
                    else 'GC FUT               COMEX GOLD FUTURES'
                )
            )
        )
        rows = _future_rows(raw, heading)
        available = sorted(m for m in rows if m >= day.strftime('%Y-%m'))
        if block.startswith('gas_curve'):
            if len(available) < 6:
                raise SourceError('six consecutive natural gas delivery months required')
            chosen = available[:3] if block == 'gas_curve_a' else available[3:6]
            for m in chosen:
                records.append(
                    _numeric(
                        rows[m][0],
                        'CME_NG_SETTLEMENT',
                        'USD_per_MMBtu',
                        day.isoformat(),
                        'USD',
                        'NYMEX NG Henry Hub physical delivery ' + m,
                        'CME_' + state + '_daily_settlement_not_spot_or_execution',
                        f'text:NG FUT / {m} / SETT. PRICE',
                    )
                )
        elif block == 'broad_energy_curve':
            if len(available) < 3:
                raise SourceError('three WTI delivery months required')
            for m in available[:3]:
                records.append(
                    _numeric(
                        rows[m][0],
                        'CME_CL_SETTLEMENT',
                        'USD_per_barrel',
                        day.isoformat(),
                        'USD',
                        'NYMEX CL WTI physical delivery ' + m,
                        'CME_' + state + '_daily_settlement_not_spot',
                        f'text:NYMEX CL / {m} / SETT. PRICE',
                    )
                )
        else:
            # A liquid December representative, not a stitched front-month
            # time series. Preserve exact contract to prevent roll-date jumps.
            december = day.strftime('%Y') + '-12'
            m = december if december in rows else available[0]
            measure, unit, scope = (
                ('CME_CL_SETTLEMENT', 'USD_per_barrel', 'NYMEX CL WTI physical')
                if block == 'broad_energy'
                else (
                    ('CME_HG_SETTLEMENT', 'USD_per_pound', 'COMEX HG copper')
                    if block == 'broad_metals'
                    else ('CME_GC_SETTLEMENT', 'USD_per_troy_ounce', 'COMEX GC gold')
                )
            )
            records.append(
                _numeric(
                    rows[m][0],
                    measure,
                    unit,
                    day.isoformat(),
                    'USD',
                    scope + ' delivery ' + m,
                    'CME_' + state + '_daily_settlement_not_spot',
                    f'text:{scope} / {m} / SETT. PRICE',
                )
            )
            if rows[m][1] in ('+', '-') and rows[m][2]:
                records.append(
                    dict(
                        quote=rows[m][1] + ' ' + rows[m][2],
                        extraction='spaced_signed_decimal_v1',
                        definition=definition(
                            measure + '_DAY_CHANGE',
                            unit,
                            day.isoformat(),
                            'USD',
                            scope + ' delivery ' + m,
                            'CME_' + state + '_settlement_change_vs_previous_trading_session',
                        ),
                        locator=f'text:{scope} / {m} / PT. CHGE',
                        label=measure + '_DAY_CHANGE',
                        limitations=[],
                    )
                )
        return _result(
            records,
            day.isoformat(),
            limitations=[
                'CME '
                + state
                + ' 日次정산가격. 실시간 체결가/현물가격/ETF 수익 아님. 선물 월별 가격차는 실현 roll 수익률을 보장하지 않는다.'
            ],
        )
    if block.startswith('gas_history') or block.startswith('gas_prev_reference'):
        title = 'Lower 48 States Natural Gas Working Underground Storage (Billion Cubic Feet)'
        if title not in text:
            raise SourceError('working gas scope/unit mismatch')
        tables = [
            t
            for t in html_records(response).tables
            if t and t[0] == ['Year-Month', 'Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5']
        ]
        if len(tables) != 1 or tables[0][1] != ['End Date', 'Value'] * 5:
            raise SourceError('dated storage history columns changed')
        points = {}
        for row in tables[0][2:]:
            if row == ['']:
                continue
            if len(row) != 11:
                raise SourceError('storage history row mismatch')
            year, month = row[0].split('-')
            for ds, v in zip(row[1::2], row[2::2]):
                if not ds and not v:
                    continue
                if v in ('', '-', '--', 'NA', 'W'):
                    continue
                d = datetime.strptime(year + '/' + ds, '%Y/%m/%d').date()
                if d in points or d.strftime('%b') != month or d.weekday() != 4:
                    raise SourceError('ambiguous storage history date')
                points[d] = v
        latest = max(points)
        if block.startswith('gas_history'):
            chosen = sorted(points)[-6:]
            chosen = chosen[:3] if block.endswith('_a') else chosen[3:]
            if any(latest - d > timedelta(days=35) for d in chosen):
                raise SourceError('missing recent consecutive storage weeks')
            for d in chosen:
                records.append(
                    _numeric(
                        points[d],
                        'EIA_US_WORKING_GAS_STOCK',
                        'Bcf',
                        str(d),
                        None,
                        'US Lower 48 working gas underground',
                        'weekly_reported_stock_not_forecast_not_seasonally_adjusted',
                        f'text:working gas / {d}',
                    )
                )
        else:
            week = latest.isocalendar().week
            dates = [
                datetime.fromisocalendar(latest.year - i, week, 5).date() - timedelta(days=7) for i in range(5, 0, -1)
            ]
            if any(d not in points for d in dates):
                raise SourceError('five prior-week seasonal reference observations required')
            chosen = dates[:3] if block.endswith('_a') else dates[3:]
            for d in chosen:
                records.append(
                    _numeric(
                        points[d],
                        'EIA_GAS_PREVIOUS_ISO_WEEK_REFERENCE_' + str(d.year),
                        'Bcf',
                        str(d),
                        None,
                        'US Lower 48 working gas underground',
                        f'reported_historical_stock_reference_for_injection_week_{latest}',
                        f'text:working gas / {d}',
                    )
                )
        release = re.search(r'Release Date: (\d+/\d+/\d+)', text)
        if not release:
            raise SourceError('storage release date missing')
        return _result(
            records,
            str(latest),
            published=datetime.strptime(release[1], '%m/%d/%Y').date().isoformat(),
            limitations=[
                '과거 행은 현재 획득판의 개정 가능 자료. 자체 동일 ISO 주 비교는 EIA 공식 보간 오년 평균/시장 consensus가 아니다.'
            ],
        )
    if block in ('hdd', 'cdd'):
        header = 'HEATING' if block == 'hdd' else 'COOLING'
        if not text.startswith(header + ' DEGREE DAY DATA WEEKLY SUMMARY') or 'POPULATION-WEIGHTED' not in text:
            raise SourceError('CPC degree-day weighting identity missing')
        m = re.search(r'LAST DATE OF DATA COLLECTION PERIOD IS ([A-Z]{3} \d{1,2}, \d{4})', text)
        if not m:
            raise SourceError('degree-day collection week absent')
        day = datetime.strptime(m[1], '%b %d, %Y').date().isoformat()
        region = (
            text.split('GAS HOME HEATING CUSTOMER WEIGHTED REGION', 1)[1].split('OIL HOME HEATING', 1)[0]
            if block == 'hdd'
            else text
        )
        m = re.search(r'UNITED STATES ((?:-?\d+ ){7}-?\d+)\b', region)
        if not m:
            raise SourceError('unique US weekly degree-day row required')
        values = m[1].split()
        scope = 'US natural gas home-heating customer weighted HDD' if block == 'hdd' else 'US population weighted CDD'
        for i, suffix in enumerate(('TOTAL', 'VS_NORMAL', 'VS_LAST_YEAR')):
            if values[i] == '-999':
                raise SourceError('degree-day sentinel not a real observation')
            records.append(
                _numeric(
                    values[i],
                    'NOAA_' + block.upper() + '_' + suffix,
                    'F_degree_days',
                    'week_ending_' + day,
                    None,
                    scope,
                    'reported_weekly_degree_days_legacy_normals_not_Bcf_demand',
                    f'text:{scope} / WEEK {suffix}',
                )
            )
        return _result(
            records,
            day,
            limitations=[
                '실제 관측 주간 누적. 구형 인구·난방고객 가중 및 평년 기준이다. 미래 전망/정확한 천연가스 소비량이 아니다.'
            ],
        )
    if block in ('position', 'position_change'):
        rows = list(csv.reader(_decode(response.body, response.content_type).splitlines()))
        code = '023651' if asset == 'NATGAS' else '088691'
        matched = [r for r in rows if len(r) == 191 and r[3].strip() == code]
        if len(matched) != 1:
            raise SourceError('CFTC exact futures-only market code required')
        r = matched[0]
        day = date.fromisoformat(r[2])
        expected = (
            'NAT GAS NYME - NEW YORK MERCANTILE EXCHANGE' if asset == 'NATGAS' else 'GOLD - COMMODITY EXCHANGE INC.'
        )
        if r[0] != expected or r[1] != day.strftime('%y%m%d'):
            raise SourceError('CFTC market/date mismatch')
        # CFTC disaggregated futures-only file: 13/14 managed-money long/short;
        # 7 OI; 61/62/55 their reported changes. Never label legacy noncommercial
        # columns as managed money or join another Henry Hub contract code.
        indexes = (13, 14, 7) if block == 'position' else (61, 62, 55)
        for idx, suffix in zip(indexes, ('LONG', 'SHORT', 'OPEN_INTEREST')):
            token = r[idx].strip()
            if not re.fullmatch(r'-?\d+', token):
                raise SourceError('CFTC missing/noninteger field')
            if block == 'position' and Decimal(token) < 0:
                raise SourceError('negative position level')
            records.append(
                _numeric(
                    token,
                    'CFTC_' + asset + '_MM_' + suffix + ('_CHANGE' if block == 'position_change' else ''),
                    'contracts',
                    str(day),
                    None,
                    expected + ' code ' + code + ' disaggregated futures only',
                    (
                        'reported_change_vs_previous_week_not_position_level'
                        if block == 'position_change'
                        else 'managed_money_positions_not_all_speculators'
                    ),
                    f'csv:code={code}; date={day}; column={idx}',
                )
            )
        return _result(
            records,
            str(day),
            limitations=[
                '화요일 포지션·후속 공개판, 발표 즉시 거래 시점과 다름. 분류별 long/short 보조자료. 역사적 백분위가 없어 과열 확정/미래 방향 예측 불가.'
            ],
        )
    if block == 'gold_etf':
        pub = re.search(r'Published: (\d{1,2} [A-Z][a-z]+, \d{4})', text)
        month = re.search(r'Gold ETF Flows: ([A-Z][a-z]+ \d{4})', text)
        flows = re.search(r'adding US\$([\d.]+)bn', text)
        held = re.search(r'holdings rose ([\d,.]+)t to (?:a record high of )?([\d,]+)t', text)
        if not all((pub, month, flows, held)):
            raise SourceError('dated WGC ETF net inflow/physical holding change absent')
        at = datetime.strptime(month[1], '%B %Y').date()
        day = at.replace(day=calendar.monthrange(at.year, at.month)[1])
        period = at.strftime('%Y-%m')
        for token, measure, unit, currency in [
            (flows[1], 'WGC_GLOBAL_GOLD_ETF_NET_FLOW', 'USD_billion', 'USD'),
            (held[1], 'WGC_GLOBAL_GOLD_ETF_HOLDINGS_CHANGE', 'tonnes', None),
            (held[2], 'WGC_GLOBAL_GOLD_ETF_HOLDINGS', 'tonnes', None),
        ]:
            records.append(
                _numeric(
                    token,
                    measure,
                    unit,
                    period,
                    currency,
                    'World Gold Council global physically backed gold ETFs',
                    'monthly_provider_reported_not_AUM_price_effect_not_issuer_cross_checked',
                    'text:WGC ETF Highlights / ' + measure,
                )
            )
        return _result(
            records,
            str(day),
            published=datetime.strptime(pub[1], '%d %B, %Y').date().isoformat(),
            limitations=[
                'WGC 전체 실물담보 ETF 월간 집계. 현재 하루/IAU 한 상품 변화와 별개이며 최신 월간치 이후 수요는 미확인.'
            ],
        )
    if block in ('gold_central', 'gold_physical'):
        if (
            'Gold Demand Trends: Q2 2026' not in text
            or 'Quarterly gold supply and demand by sector, tonnes' not in text
        ):
            raise SourceError('WGC quarterly identity/unit required')
        table = html_records(response).tables
        if len(table) != 1 or table[0][0][:6] != ['', "Q2'25", "Q3'25", "Q4'25", "Q1'26", "Q2'26"]:
            raise SourceError('WGC period columns changed')
        choose = (
            [
                ('Central Banks & Other inst.', 'CENTRAL_BANK_NET_DEMAND', col, period)
                for col, period in [(1, '2025Q2'), (4, '2026Q1'), (5, '2026Q2')]
            ]
            if block == 'gold_central'
            else [
                ('Jewellery Consumption', 'JEWELLERY_CONSUMPTION', 5, '2026Q2'),
                ('Total Bar and Coin', 'BAR_COIN_DEMAND', 5, '2026Q2'),
                ('Jewellery Consumption', 'JEWELLERY_CONSUMPTION', 1, '2025Q2'),
            ]
        )
        for label, measure, col, period in choose:
            rows = [r for r in table[0] if r and r[0] == label]
            if len(rows) != 1 or len(rows[0]) != 8:
                raise SourceError('WGC demand row changed')
            records.append(
                _numeric(
                    rows[0][col],
                    'WGC_' + measure,
                    'tonnes',
                    period,
                    None,
                    'global ' + label + ' estimated by World Gold Council',
                    'current_report_edition_including_estimates_and_revisions_not_original_vintage',
                    'table:WGC Q2 2026 / ' + label + ' / ' + period,
                )
            )
        return _result(
            records,
            '2026-06-30',
            published='2026-07-30' if '30 July, 2026' in text else None,
            limitations=[
                '현재 발표판의 분기 수요 추정·개정값. 일부 미보고 매수 포함, IMF/중앙은행 보고만의 확정합계 아님. Q2 수요를 10월 현재 수요로 relabel하지 않는다.'
            ],
        )
    if block == 'gold_dollar':
        if 'Foreign Exchange Rates - H.10' not in text:
            raise SourceError('H10 identity missing')
        table = html_records(response).tables[0]
        r = next((r for r in table if r[:2] == ['1) BROAD', 'JAN06=100']), None)
        pub = re.search(r'Release Date: ([A-Z][a-z]+ \d{1,2}, \d{4})', text)
        if r is None or not pub:
            raise SourceError('dated broad dollar table required')
        published = datetime.strptime(pub[1], '%B %d, %Y').date()
        days = []
        for token in table[0][2:]:
            d = datetime.strptime(token.replace('.', '') + ' ' + str(published.year), '%b %d %Y').date()
            if d > published:
                d = d.replace(year=d.year - 1)
            days.append(d)
        for i in (0, len(days) - 1):
            records.append(
                _numeric(
                    r[i + 2],
                    'FED_BROAD_USD_INDEX',
                    'index_2006_01_100',
                    str(days[i]),
                    None,
                    'Federal Reserve nominal broad trade weighted US dollar index',
                    'nominal_trade_weighted_not_USDKRW',
                    f'table:H10 1) BROAD / {days[i]}',
                )
            )
        return _result(
            records,
            str(days[-1]),
            published=str(published),
            limitations=[
                '명목 교역가중 달러지수. 실질 달러/DXY/원달러 환율과 다른 정의이며 금 가격의 인과나 미래 방향을 확정하지 않는다.'
            ],
        )
    if block in ('iau_terms', 'gsg_fee'):
        iau = block == 'iau_terms'
        if ('iShares Gold Trust' if iau else 'iShares S&P GSCI Commodity-Indexed Trust') not in text:
            raise SourceError('iShares product identity missing')
        fee = re.search(r'Sponsor Fee(?:\s*:\s*Fees as stated in the prospectus)?\s+([\d.]+)%', text)
        if not fee:
            raise SourceError('dated issuer product fee not found')
        at = re.search((r'Tonnes in Trust [\d,.]+' if iau else r'NAV') + r' as of ([A-Z][a-z]{2} \d{2}, \d{4})', text)
        if not at:
            raise SourceError('IAU product date unavailable')
        day = datetime.strptime(at[1], '%b %d, %Y').date().isoformat()
        records = [
            _numeric(
                fee[1],
                'IAU_SPONSOR_FEE' if iau else 'GSG_SPONSOR_FEE',
                'percent',
                'annual_fee',
                None,
                'iShares Gold Trust IAU' if iau else 'iShares GSG commodity futures trust',
                'issuer_disclosed_fee_not_tax_or_spread',
                'text:iShares ' + ('Sponsor Fee' if iau else 'Expense Ratio'),
            )
        ]
        return _result(
            records,
            day,
            limitations=[
                '원발행 상품의 관리보수. 기타 운용비/환율/매매 스프레드/계좌 과세는 별도이며 국내 상품 비용을 대변하지 않는다.'
            ],
        )
    if block.startswith('weights_'):
        m = re.search(r'in each case as of ([A-Z][a-z]+ \d{1,2}, \d{4}), are as follows:', text)
        if not m or 'Dollar Weight' not in text:
            raise SourceError('dated GSCI constituent weights absent')
        at = datetime.strptime(m[1], '%B %d, %Y').date().isoformat()
        start = raw.index('Dollar Weight', raw.index(m[1]))
        section = raw[start : raw.index('The quantity', start)]
        values = []
        for line in section.splitlines():
            match = re.search(
                r'([\d.]+)%\s+(LCO|CL|GC|MCU|LC|LGO|MAL|C|HO|RB|S|LH|FC|NG|W|SI|KC|KW|SB|MNI|MZN|CT|MPB|CC)\s', line
            )
            if match:
                values.append((match[2], match[1]))
        if len(values) != 24 or set(t for t, v in values) != {v for g in GROUPS.values() for v in g}:
            raise SourceError('complete unique 24-constituent GSCI weight table required')
        if abs(sum(Decimal(v) for t, v in values) - 100) > Decimal('0.12'):
            raise SourceError('weights fail published rounded total check')
        index = int(block.split('_')[1])
        chosen = values[index * 3 : (index + 1) * 3]
        if len(chosen) != 3:
            raise SourceError('invalid constituent weight block')
        for ticker, value in chosen:
            records.append(
                _numeric(
                    value,
                    'GSCI_WEIGHT_' + ticker,
                    'percent',
                    at,
                    None,
                    'S&P GSCI constituent ' + ticker,
                    'dated_constituent_dollar_weight_not_Tbill_collateral_not_current_October_weight',
                    'text:GSG prospectus GSCI Dollar Weight / ' + ticker,
                )
            )
        pub = re.search(r'The date of this prospectus is ([A-Z][a-z]+ \d{1,2}, \d{4})\.', text)
        published = datetime.strptime(pub[1], '%B %d, %Y').date().isoformat() if pub else None
        return _result(
            records,
            at,
            published=published,
            limitations=[
                '발행사 prospectus에 인용된 S&P 구성의 명시 기준일. 현재 가중치는 가격/재조정으로 다를 수 있음. 담보 국채 보유 목록과 다름.'
            ],
        )
    if block == 'gsg_terms':
        if 'iShares' not in text or 'S&P GSCI' not in text:
            raise SourceError('GSG prospectus identity missing')
        phrases = [
            re.search(r'[^.]{0,200}fifth[^.]{0,700}ninth[^.]{0,250}\.', text, re.I),
            re.search(r'[^.]{0,160}(?:contango|backwardation)[^.]{0,500}\.', text, re.I),
            re.search(r'with “Collateral Assets” consisting of cash, U\.S\. Treasury securities[^.]{0,600}\.', text),
        ]
        records = [
            _quote(
                m[0],
                'GSG_ROLL_AND_COLLATERAL_TERMS',
                'prospectus',
                'iShares GSG S&P GSCI futures exposure',
                'product_structure_not_realized_roll_yield',
                'text:GSG prospectus roll/curve',
            )
            for m in phrases
            if m
        ]
        if not records:
            raise SourceError('GSG rolling terms absent')
        pub = re.search(r'The date of this prospectus is ([A-Z][a-z]+ \d{1,2}, \d{4})\.', text)
        if not pub:
            raise SourceError('prospectus terms edition date absent')
        day = datetime.strptime(pub[1], '%B %d, %Y').date().isoformat()
        return _result(
            records,
            day,
            published=day,
            limitations=[
                '기초 현물+선물 교체+담보 이자−보수/추적 차이를 구분한다. 실제 실현 roll/현재 섹터 성과 기여는 별도 계산 전 미확인.'
            ],
        )
    if block == 'broad_agri':
        day, state = _bulletin(raw)
        match = re.search(r'^CORN FUT\s*\n(DEC\d{2}[^\n]+)', raw, re.M)
        if not match:
            raise SourceError('CME corn December contract table absent')
        month, token = _corn_row(match[1])
        q = _quote(
            match[1],
            'CME_CORN_QUOTED_SETTLEMENT',
            str(day),
            'CBOT corn delivery ' + month,
            'cents_per_bushel_eighth_cent_quote_' + state,
            'text:CORN FUT / SETT. PRICE',
        )
        return _result(
            [q],
            str(day),
            limitations=[
                '옥수수는 센트/부셸, 끝 숫자는 1/8센트다. deterministic code로 해독하며 달러/톤으로 대체하지 않는다.'
            ],
        )
    if block in ('wasde_corn', 'wasde_wheat'):
        pub = re.search(r'September 11, 2026', text)
        if not pub or 'WASDE-675' not in text:
            raise SourceError('reviewed September 2026 WASDE edition absent')
        if block == 'wasde_corn':
            snippets = [
                re.search(
                    r'Corn production for 2026/27 is forecast at [^.]+?\d+\.\d+ billion bushels, down \d+ million from last month',
                    text,
                ),
                re.search(r'ending stocks are lowered \d+ million bushels to \d+\.\d+ billion\.', text),
            ]
        else:
            snippets = [
                re.search(
                    r'Projected 2026/27 global ending stocks are raised [\d.]+ million tons to [\d.]+ million[^.]*\.',
                    text,
                )
            ]
        for m in snippets:
            if m:
                records.append(
                    _quote(
                        m[0],
                        'USDA_' + block.upper() + '_SUPPLY_DEMAND_FORECAST',
                        '2026/27_marketing_year',
                        'US corn' if block == 'wasde_corn' else 'global wheat',
                        'September_WASDE_projection_not_actual_stock',
                        'text:WASDE-675 prose outlook',
                    )
                )
        if not records:
            raise SourceError('WASDE forecast paragraph changed; no guessed actual inventory')
        return _result(
            records,
            '2026-09-11',
            published='2026-09-11',
            limitations=[
                'USDA 시장연도 전망·전월 전망 수정. 실제 수확/현재 실제 재고와 별개이며 옥수수와 밀의 지역 scope가 다르다.'
            ],
        )
    if block.startswith(('ung_', 'boil_')):
        fields = candidate['index_identity_fields']
        published = fields['published_at']
        if block.startswith('ung_') and 'United States Natural Gas Fund' not in text:
            raise SourceError('UNG filing identity absent')
        if block == 'ung_terms':
            matches = [
                re.search(r'the near month contract to expire, except when[^.]+?next month contract to expire\.', text),
                re.search(
                    r'until the near month contract is within two weeks of expiration, when, over a four-day period[^.]+\.',
                    text,
                ),
            ]
            for m in matches:
                if m:
                    records.append(
                        _quote(
                            m[0],
                            'UNG_BENCHMARK_AND_ROLL',
                            'prospectus',
                            'United States Natural Gas Fund UNG',
                            'near_month_to_next_month_benchmark_not_Henry_Hub_spot_holdings',
                            'text:UNG Benchmark Futures Contract / roll',
                        )
                    )
            if not records:
                raise SourceError('UNG benchmark/roll paragraph unavailable')
        elif block == 'ung_fees':
            fee = re.search(r'Management Fees ([\d.]+)\s*%', text)
            total = re.search(r'Total Annual Fund Operating Expenses ([\d.]+)\s*%', text)
            if not fee or not total:
                raise SourceError('UNG dated fee table absent')
            records = [
                _numeric(
                    fee[1],
                    'UNG_MANAGEMENT_FEE',
                    'percent',
                    'annual_fee',
                    None,
                    'United States Natural Gas Fund UNG',
                    'prospectus_fee_first_1bn_NAV_not_total_cost',
                    'text:UNG Management Fees',
                ),
                _numeric(
                    total[1],
                    'UNG_ANNUAL_OPERATING_EXPENSES',
                    'percent',
                    '2025_reported_expenses',
                    None,
                    'United States Natural Gas Fund UNG',
                    'prior_year_operating_expenses_not_fixed_future_cost',
                    'text:UNG Total Annual Fund Operating Expenses',
                ),
            ]
        elif block == 'ung_holdings':
            match = re.search(
                r'NYMEX Natural Gas Futures NG [A-Z][a-z]+ 2026 contracts, expiring [A-Z][a-z]+ 2026[^#]{0,170}', text
            )
            if not match:
                raise SourceError('dated UNG investment schedule absent')
            records = [
                _quote(
                    match[0],
                    'UNG_REPORTED_FUTURES_HOLDING',
                    fields['report_date'],
                    'United States Natural Gas Fund UNG',
                    'dated_quarter_end_holding_not_current_contract',
                    'text:UNG Schedule of Investments / futures',
                )
            ]
        elif block == 'boil_supplement':
            name = 'ProShares Ultra Bloomberg Natural Gas (BOIL)'
            if name not in text or 'Rule 424(i)' not in text:
                raise SourceError('BOIL named registration supplement unavailable')
            records = [
                _quote(
                    name,
                    'BOIL_SEC_REGISTRATION',
                    '2026-03-31',
                    'ProShares Trust II BOIL',
                    'fund_name_only_not_fee_benchmark_or_current_holding_confirmation',
                    'text:Rule 424(i) fund names',
                )
            ]
        else:
            # Never use an empty, truncated, unrelated or combined filing as
            # proof of a specific fund's current economic terms.
            raise SourceError('BOIL current fund-specific benchmark/fees/holdings contract not verified; preserve gap')
        return _result(
            records,
            fields.get('report_date') or published,
            published=published,
            limitations=[
                'SEC 원공시. 상품 조건·과거 보유·등록 이름을 구분한다. 분기말 계약을 현재 보유로 사용하지 않는다.'
            ],
        )
    raise SourceError('unsupported reviewed commodity document block')


def calculations(case, cutoff, require_dates=False):
    from .scan import eligible
    from .scan_coverage import calculations as minimum_calculations

    es = eligible(case, cutoff)
    out = list(minimum_calculations(case, cutoff, require_dates=require_dates))
    if require_dates:
        from .source_pipeline import dated_evidence

        es = [e for e in es if dated_evidence(e)]

    def select(measure):
        return [e for e in es if e.value is not None and e.provenance.definition['measure'] == measure]

    def metric(identifier, label, value, unit, inputs, assets, method, limits=()):
        out.append(
            MetricResult(
                'CALC_COMMODITY_' + identifier,
                label,
                value,
                unit,
                method,
                tuple(e.id for e in inputs),
                tuple(assets),
                tuple(limits),
            )
        )

    # Deduplicate dependent renderings/different excerpt blocks by observation.
    stocks = {e.period: e for e in select('EIA_US_WORKING_GAS_STOCK')}
    for a, b in zip(sorted(stocks)[:-1], sorted(stocks)[1:]):
        if date.fromisoformat(b) - date.fromisoformat(a) == timedelta(days=7):
            metric(
                'GAS_INJECTION_' + b.replace('-', ''),
                'Lower 48 주간 순주입/인출',
                stocks[b].value - stocks[a].value,
                'Bcf',
                [stocks[a], stocks[b]],
                ['NATGAS'],
                'same_region_weekly_stock_difference_v1',
            )
    previous = {
        e.period[:4]: e
        for e in es
        if e.value is not None and e.provenance.definition['measure'].startswith('EIA_GAS_PREVIOUS_ISO_WEEK_REFERENCE_')
    }
    current = {
        e.period[:4]: e
        for e in es
        if e.value is not None and e.provenance.definition['measure'].startswith('EIA_GAS_ISO_WEEK_REFERENCE_')
    }
    if len(previous) == len(current) == 5 and set(previous) == set(current):
        if all(
            date.fromisoformat(current[y].period) - date.fromisoformat(previous[y].period) == timedelta(days=7)
            for y in current
        ):
            with localcontext() as ctx:
                ctx.prec = 50
                average = sum(current[y].value - previous[y].value for y in current) / 5
            metric(
                'GAS_REFERENCE_INJECTION',
                '과거 오년 같은 ISO 주 순주입 자체 평균',
                average,
                'Bcf',
                [v for y in sorted(current) for v in (previous[y], current[y])],
                ['NATGAS'],
                'same_ISO_week_five_year_actual_stock_differences_v1',
                ['EIA 공식 보간 평균/시장 기대 주입량이 아니다. 현재 획득판의 역사 자료.'],
            )
    curves = select('CME_NG_SETTLEMENT')
    curves = sorted(curves, key=lambda e: e.provenance.definition['scope'].split()[-1])
    if (
        len(curves) == 6
        and all(e.value > 0 for e in curves)
        and len({(e.period, e.provenance.definition['adjustment']) for e in curves}) == 1
    ):
        for a, b in zip(curves, curves[1:]):
            with localcontext() as ctx:
                ctx.prec = 50
                gap = (b.value / a.value - 1) * 100
            label = a.provenance.definition['scope'].split()[-1] + '_TO_' + b.provenance.definition['scope'].split()[-1]
            metric(
                'NG_CURVE_' + label,
                '인접 천연가스 계약 가격차',
                gap,
                'percent',
                [a, b],
                ['NATGAS'],
                'same_instant_futures_contract_price_gap_v1',
                ['실현 roll yield/확정 ETF 손실 아님. 미래 곡선 수렴·보유 계약·담보 이자·비용은 별도.'],
            )
    oil = {e.provenance.definition['scope']: e for e in select('CME_CL_SETTLEMENT')}
    oil = sorted(oil.values(), key=lambda e: e.provenance.definition['scope'])
    if (
        len(oil) == 3
        and all(e.value > 0 for e in oil)
        and len({(e.period, e.provenance.definition['adjustment']) for e in oil}) == 1
    ):
        for a, b in zip(oil, oil[1:]):
            with localcontext() as ctx:
                ctx.prec = 50
                gap = (b.value / a.value - 1) * 100
            suffix = (
                a.provenance.definition['scope'].split()[-1] + '_TO_' + b.provenance.definition['scope'].split()[-1]
            )
            metric(
                'CL_CURVE_' + suffix,
                '인접 WTI 계약 가격차',
                gap,
                'percent',
                [a, b],
                ['BROAD_COMMODITIES'],
                'same_instant_futures_contract_price_gap_v1',
                ['GSG 전체 roll yield/실현 수익 아님. 현재 지정 WTI 계약 가격차.'],
            )
    for asset in ('NATGAS', 'GOLD'):
        long = select('CFTC_' + asset + '_MM_LONG')
        short = select('CFTC_' + asset + '_MM_SHORT')
        dl = select('CFTC_' + asset + '_MM_LONG_CHANGE')
        ds = select('CFTC_' + asset + '_MM_SHORT_CHANGE')
        if len(long) == len(short) == 1 and long[0].period == short[0].period:
            metric(
                asset + '_MM_NET',
                'Managed money 매수−매도 순포지션',
                long[0].value - short[0].value,
                'contracts',
                long + short,
                [asset],
                'same_market_managed_money_long_minus_short_v1',
            )
        if len(dl) == len(ds) == 1 and dl[0].period == ds[0].period:
            metric(
                asset + '_MM_NET_CHANGE',
                'Managed money 전주 대비 순포지션 변화',
                dl[0].value - ds[0].value,
                'contracts',
                dl + ds,
                [asset],
                'same_market_managed_money_long_change_minus_short_change_v1',
            )
    weights = {
        e.provenance.definition['measure'].removeprefix('GSCI_WEIGHT_'): e
        for e in es
        if e.value is not None and e.provenance.definition['measure'].startswith('GSCI_WEIGHT_')
    }
    if len(weights) == 24 and len({e.period for e in weights.values()}) == 1:
        for group, tickers in GROUPS.items():
            if all(t in weights for t in tickers):
                items = [weights[t] for t in tickers]
                metric(
                    'GSCI_' + group.upper() + '_WEIGHT',
                    '기준일 S&P GSCI ' + group + ' 비중 합계',
                    sum(e.value for e in items),
                    'percent',
                    items,
                    ['BROAD_COMMODITIES'],
                    'sum_explicit_dated_constituent_weights_v1',
                    ['현재 10월 비중 아님. 에너지와 금속/농산물은 다른 동인.'],
                )
    for e in es:
        if e.provenance.definition['measure'] == 'CME_CORN_QUOTED_SETTLEMENT':
            month, token = _corn_row(e.text)
            if re.fullmatch(r"\d+'[0246]", token):
                whole, eighth = token.split("'")
                metric(
                    'CORN_SETTLEMENT',
                    'CBOT 옥수수 계약 정산가격',
                    Decimal(whole) + Decimal(eighth) / 8,
                    'cents_per_bushel',
                    [e],
                    ['BROAD_COMMODITIES'],
                    'CBOT_eighth_cent_quote_decode_v1',
                    ['계약/관측일은 원문 definition에 보존. 현물가격/ETF 수익 아님.'],
                )
    for measure, label in [('WGC_CENTRAL_BANK_NET_DEMAND', 'CENTRAL_BANK'), ('WGC_JEWELLERY_CONSUMPTION', 'JEWELLERY')]:
        items = {e.period: e for e in select(measure)}
        for prefix, prior in [('YOY', '2025Q2'), ('QOQ', '2026Q1')]:
            if prior in items and '2026Q2' in items and items[prior].value > 0:
                a, b = items[prior], items['2026Q2']
                with localcontext() as ctx:
                    ctx.prec = 50
                    v = (b.value / a.value - 1) * 100
                metric(
                    'GOLD_' + label + '_' + prefix,
                    'WGC 분기 수요 ' + prefix + ' 변화',
                    v,
                    'percent',
                    [a, b],
                    ['GOLD'],
                    'same_current_edition_quarterly_demand_change_v1',
                    ['현재판 추정/개정값, 당시 발표치/현재 월간 수요 아님.'],
                )
    # Emit one copy of shared calculations in combined questions.
    unique = {m.id: m for m in out}
    return list(unique.values())
