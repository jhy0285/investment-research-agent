"""Reviewed Korean datasets in front of the existing discovery/acquisition engines.

This is a data-coverage registry, not a question parser. Country, tenor and
geography arrive from the existing Subject. Public sample APIs are bounded;
missing fields, truncated samples and mismatched identities fail closed.
"""

from copy import deepcopy
from dataclasses import asdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, localcontext
import calendar
import json
import re
from urllib.parse import parse_qs, urlencode, urlsplit

from .sources import SourceError, SourceSpec, _decode, _parse_json, _visible_html

KOREAN_DATA_VERSION = 'korean_official_coverage_v1'
ECOS_POLICY = 'https://ecos.bok.or.kr/api/'
REB_POLICY = 'https://www.reb.or.kr/r-one/portal/openapi/openApiDevPage.do'
ECOS_ITEMS = {1: '010190000', 3: '010200000', 5: '010200001', 10: '010210000'}
KR_RATES = tuple('KR_GOVERNMENT_NOMINAL_' + str(t) + 'Y' for t in ECOS_ITEMS)
REGIONS = {'서울': '11000000', '경기': '41000000', '인천': '28000000'}
REB_TABLES = {
    'reb_sale_index': ('A_2024_00045', '(월) 매매가격지수_아파트', '지수', 'survey_sale_index'),
    'reb_jeonse_index': ('A_2024_00050', '(월) 전세가격지수_아파트', '지수', 'survey_jeonse_index'),
    'reb_volume': ('A_2024_00554', '(월) 행정구역별 아파트매매거래현황', '동(호)수', 'reported_sale_count'),
    'reb_transaction_index': ('A_2024_00178', '(월) 지역별 매매지수_아파트', '지수', 'transaction_sale_index'),
}
CATEGORY_NAMES = {
    'company_results': '최근 분기 매출·영업이익·순이익',
    'company_prior': '직전 분기 같은 정의의 실적',
    'company_business': '사업부·공식 경영진 설명',
    **{k: v[1] for k, v in REB_TABLES.items()},
}


def regions_for_method(identifier):
    if not identifier.startswith('KR_APARTMENTS_'):
        return ()
    names = identifier.removeprefix('KR_APARTMENTS_').split('_')
    return tuple(r for r in REGIONS if {'서울': 'SEOUL', '경기': 'GYEONGGI', '인천': 'INCHEON'}[r] in names)


def resolve_korean_subject(subject, enabled):
    if not enabled:
        return None
    from .research_catalog import method

    if subject.method_family == 'bond' and subject.country == 'KR' and subject.maturity:
        term = subject.maturity
        if term.unit != 'years' or term.value not in ('1', '3', '5', '10'):
            return None
        return method(
            'KR_GOVERNMENT_' + term.value + 'Y',
            subject.label,
            'bond',
            [],
            KR_RATES,
            '원화 국고채의 계약 현금흐름과 현재 기준 수익률을 구분해 검토한다.',
            '중도 매도 시 금리 상승에 따른 가격 손실·재투자·물가·상품 비용이 중요하다.',
            '원화 자금의 사용 시점과 실제 매수 채권의 만기가 맞는가?',
            '더 긴 기간의 기업 이익 성장과 유동성의 기회비용을 포기할 이유가 충분한가?',
            ['실제 매수 가능한 개별 채권/ETF의 YTM·가격·비용·세금', '신규자금 사용 시점·보유자산·손실 감당 능력'],
            '한국은행 ECOS 시장금리(일별)의 국고채 기준 수익률이다. 미국 Treasury나 확정 실현수익으로 대체하지 않는다.',
        )
    if subject.label in ('삼성전자', 'SK하이닉스') and subject.country in (None, 'KR'):
        identifier = 'SAMSUNG' if subject.label == '삼성전자' else 'SK_HYNIX'
        return method(
            identifier,
            subject.label,
            'equity',
            [],
            [],
            '기업별 분기 매출·영업이익·순이익과 실제 지불 가격을 별도로 검토한다.',
            '메모리 업황·AI 수요·가격 기대·투자 지출·사업 집중·실적 미달의 위험이 있다.',
            '같은 기업의 매출·마진 개선이 지속 가능한 현금흐름으로 이어지는가?',
            '좋은 현재 실적을 가격이 이미 반영했거나 업황 반전이 이익을 줄일 수 있는가?',
            [
                '현재 주가·동일 정의 TTM valuation·현금흐름·consensus/revision',
                *(
                    [
                        '공식 IR 연결 제공자의 재무자료를 DART 원공시와 교차 확인',
                        '접근 가능한 공식 실적 설명·사업부 자료',
                    ]
                    if identifier == 'SK_HYNIX'
                    else ['발표문에 없는 순이익·직전 분기 상세 재무제표']
                ),
            ],
            '명시한 기업의 실적만 사용한다. 분기 EPS를 연간 EPS로 바꾸거나 실적 우위를 주식 매력의 우위로 확정하지 않는다.',
        )
    if subject.method_family == 'real_estate' and subject.country in (None, 'KR') and subject.regions:
        if not set(subject.regions) <= {'서울', '수도권', '경기', '인천'}:
            return None
        selected = tuple(REGIONS) if '수도권' in subject.regions else tuple(r for r in REGIONS if r in subject.regions)
        codes = {'서울': 'SEOUL', '경기': 'GYEONGGI', '인천': 'INCHEON'}
        return method(
            'KR_APARTMENTS_' + '_'.join(codes[r] for r in selected),
            subject.label,
            'real_estate',
            [],
            [],
            '지역별 매매·전세·실거래 지수와 거래량을 구분하고 가격·임대·대출·유동성을 검토한다.',
            '거래 공백·신고 지연·정책·대출·공급·전세금 반환과 매도 유동성이 중요하다.',
            '해당 지역의 실거래·임대 여건이 금융비용과 대체 투자기회를 정당화하는가?',
            '가격 상승이 낮은 거래량·높은 매수 가격·공급·부채 위험을 가리고 있는가?',
            [
                '개별 아파트 실거래 가격·거래 조건·전세가율·임대 현금흐름',
                '지역별 공급/입주·주택담보대출 조건·사용자 부채와 자금수요',
            ],
            ' / '.join(selected)
            + '의 공식 지역 통계만 사용한다. 조사 가격지수·실거래지수·신고 거래량은 개별 매물 가격이나 투자 수익률이 아니다.',
        )
    return None


def supports_discovery(identifier):
    return identifier in ('SAMSUNG', 'SK_HYNIX') or bool(regions_for_method(identifier))


def evidence_needs(methods):
    needs = []
    for method in methods:
        identifier = method['id']
        if identifier in ('SAMSUNG', 'SK_HYNIX'):
            categories = (
                ['company_results', 'company_business']
                if identifier == 'SAMSUNG'
                else ['company_results', 'company_prior']
            )
            for category in categories:
                needs.append(
                    dict(
                        id='NEED_' + identifier + '_' + category.upper(),
                        asset_id=identifier,
                        category=category,
                        label=method['label'] + ' ' + CATEGORY_NAMES[category],
                        reason='기업별 실적과 가격 판단을 분리할 실제 자료',
                        max_age_seconds=135 * 86400,
                        max_selected=1,
                    )
                )
        for region in regions_for_method(identifier):
            for category, (table, title, item, basis) in REB_TABLES.items():
                needs.append(
                    dict(
                        id='NEED_'
                        + identifier
                        + '_'
                        + category.upper()
                        + '_'
                        + {'서울': 'SEOUL', '경기': 'GYEONGGI', '인천': 'INCHEON'}[region],
                        asset_id=identifier,
                        category=category,
                        label=region + ' ' + title,
                        reason='명시한 지역의 가격·전세·유동성 변화',
                        region=region,
                        lawd_code=REGIONS[region],
                        table_id=table,
                        table_title=title,
                        item_name=item,
                        basis=basis,
                        max_age_seconds=100 * 86400,
                        max_selected=1,
                    )
                )
    return needs


def discovery_policy(base, config, needs, now):
    policy = (
        deepcopy(base)
        if base is not None
        else dict(schema_version='discovery-policy-v1', max_requests=32, max_candidates_per_need=8, providers=[])
    )
    providers = []
    for category, (table, title, item, basis) in REB_TABLES.items():
        if not any(n['category'] == category for n in needs):
            continue
        providers.append(
            dict(
                id='REB_' + table,
                publisher='한국부동산원 R-ONE',
                type='primary',
                canonical=True,
                jurisdiction='KR',
                categories=[category],
                method='official_regional_series',
                contract='reb_regional_monthly_v1',
                seed_url='https://www.reb.or.kr/r-one/openapi/SttsApiTbl.do?'
                + urlencode({'STATBL_ID': table, 'Type': 'json'}),
                codes_url='https://www.reb.or.kr/r-one/portal/openapi/selectOpenApiItmCd.do?'
                + urlencode({'statblId': table}),
                candidate_hosts=['www.reb.or.kr'],
                access_method='public_api',
                policy_url=REB_POLICY,
                policy_note='공식 R-ONE API의 인증키 없는 공개 sample 모드(최대 5행). 공식 코드 조회로 표별 지역을 확인하고 최근 4개월·한 지역·한 항목으로 제한한다. 키 제한을 우회하거나 페이지를 반복 수집하지 않는다. 선택한 구절·필드·정의·hash만 귀속 표시하여 개인 연구용으로 보존한다. JSON 본문의 실제 HTTP MIME(text/html)은 그대로 기록한다.',
            )
        )
    for identifier in ('SAMSUNG', 'SK_HYNIX'):
        if not any(n['asset_id'] == identifier for n in needs):
            continue
        p = deepcopy(config['company_providers'][identifier])
        providers.append(p)
    policy['providers'].extend(providers)
    policy['max_requests'] = 32
    policy['as_of_month'] = now.date().strftime('%Y%m')
    return policy


def reb_json(response):
    # The reviewed R-ONE endpoints document Type=json but return text/html.
    if response.content_type.split(';')[0] not in ('application/json', 'text/html'):
        raise SourceError('R-ONE JSON response has an unreviewed MIME')
    return _parse_json(_decode(response.body, response.content_type))


def reb_rows(doc, key):
    parts = doc.get(key)
    if not isinstance(parts, list) or len(parts) != 2:
        raise SourceError('R-ONE table/result missing')
    head = parts[0]['head']
    count = next(h['list_total_count'] for h in head if 'list_total_count' in h)
    result = next(h['RESULT'] for h in head if 'RESULT' in h)
    rows = parts[1]['row']
    if result.get('CODE') != 'INFO-000' or type(count) is not int or count != len(rows):
        raise SourceError('R-ONE unavailable or truncated sample; do not fill from another region')
    return rows


def regional_identity(provider, need, metadata, codes):
    rows = reb_rows(reb_json(metadata), 'SttsApiTbl')
    if len(rows) != 1:
        raise SourceError('unique official table metadata required')
    table = rows[0]
    if (
        table['STATBL_ID'] != need['table_id']
        or table['STATBL_NM'] != need['table_title']
        or table['DTACYCLE_CD'] != 'MM'
        or table['TOP_ORG_NM'] != '한국부동산원'
        or table['OPEN_STATE'] != 'Y'
    ):
        raise SourceError('official regional table identity/frequency changed')
    directory = reb_json(codes)['data']
    region = [
        r
        for r in directory
        if r['statblId'] == need['table_id']
        and r['itmTag'] == '분류'
        and r['itmNm'] == need['region']
        and str(r['lawdCd']) == need['lawd_code']
    ]
    item = [
        r
        for r in directory
        if r['statblId'] == need['table_id'] and r['itmTag'] == '항목' and r['itmNm'] == need['item_name']
    ]
    if len(region) != 1 or len(item) != 1:
        raise SourceError('official table-specific region/item code unavailable')
    base = table.get('RPSTUI_NM')
    if need['basis'] != 'reported_sale_count' and (
        not isinstance(base, str) or not re.fullmatch(r'기준시점\s*:\s*\d{4}\.\d{2}\.=100(?:\.0)?', base)
    ):
        raise SourceError('price-index base definition unavailable')
    return dict(
        table_id=need['table_id'],
        table_title=need['table_title'],
        region=need['region'],
        lawd_code=need['lawd_code'],
        region_code=str(region[0]['itmId']),
        item_code=str(item[0]['itmId']),
        item_name=need['item_name'],
        basis=need['basis'],
        base=base,
    )


def regional_url(identity, month):
    year, mon = int(month[:4]), int(month[4:])
    serial = year * 12 + mon - 1 - 3
    start = f'{serial//12:04d}{serial%12+1:02d}'
    return 'https://www.reb.or.kr/r-one/openapi/SttsApiTblData.do?' + urlencode(
        dict(
            STATBL_ID=identity['table_id'],
            DTACYCLE_CD='MM',
            CLS_ID=identity['region_code'],
            ITM_ID=identity['item_code'],
            START_WRTTIME=start,
            END_WRTTIME=month,
            Type='json',
        )
    )


def euroland_document(body):
    # Read a named JSON array literal, never eval JavaScript or follow its code.
    if not re.search(r"companycode\s*:\s*['\"]kr-000660['\"]", body):
        raise SourceError('financial page company identifier does not match SK hynix')
    matches = list(re.finditer(r'\bLevelZeroItems\s*:\s*', body))
    if len(matches) != 1:
        raise SourceError('unique reviewed financial JSON literal required')
    tail = body[matches[0].end() :]
    decoder = json.JSONDecoder()
    try:
        _, end = decoder.raw_decode(tail)
    except ValueError as exc:
        raise SourceError('invalid embedded financial JSON') from exc
    return {'LevelZeroItems': _parse_json(tail[:end])}


def samsung_document(body):
    visible = _visible_html(body)
    quarter = re.search(
        r'financial results for the (first|second|third|fourth) quarter ended ([A-Za-z]+ \d{1,2}, \d{4})\.', visible
    )
    published = re.search(r'Korea on ([A-Za-z]+ \d{1,2}, \d{4})', visible)
    if not quarter or not published:
        raise SourceError('Samsung quarter/publication identity unavailable')
    period = datetime.strptime(quarter[2], '%B %d, %Y').date()
    publication = datetime.strptime(published[1], '%B %d, %Y').date()
    month = {'first': 3, 'second': 6, 'third': 9, 'fourth': 12}[quarter[1]]
    if period.month != month or period.day != calendar.monthrange(period.year, month)[1] or publication < period:
        raise SourceError('Samsung fiscal quarter/date/publication mismatch')
    metrics = {}
    patterns = {
        'revenue': r'The Company posted KRW ([\d.]+) trillion in consolidated revenue',
        'operating_profit': r'Operating profit also reached another all-time high, increasing to KRW ([\d.]+) trillion',
        'revenue_qoq_percent': r'quarter-on-quarter \(QoQ\) increase of ([\d.]+)%',
    }
    for key, pattern in patterns.items():
        found = list(re.finditer(pattern, visible))
        if len(found) != 1:
            raise SourceError('reviewed Samsung field/context changed: ' + key)
        metrics[key] = found[0][1]
    # Long business excerpts are source text, not claims that guidance occurred.
    texts = {}
    for key, pattern in {
        'ds': r'The DS Division posted .*? for the second quarter\.',
        'mx': r'The MX and Networks Businesses posted .*? for the second quarter\.',
        'guidance': r'In H2 2026, the Memory Business expects .*? agentic AI\.',
    }.items():
        m = re.search(pattern, visible)
        if m:
            texts[key] = m[0]
    return dict(
        metrics=metrics,
        texts=texts,
        period=period.isoformat(),
        published_at=publication.isoformat(),
        quarter=quarter[1],
        visible=visible,
    )


def source_document(url, decoded):
    """Narrow opt-in decoding while retaining the HTTP MIME and original bytes."""
    parsed = urlsplit(url)
    query = parse_qs(parsed.query)
    if (
        parsed.hostname == 'www.reb.or.kr'
        and parsed.path == '/r-one/openapi/SttsApiTblData.do'
        and query.get('Type') == ['json']
    ):
        return _parse_json(decoded)
    if (
        parsed.hostname == 'asia.tools.euroland.com'
        and parsed.path.lower() == '/tools/ia/'
        and query.get('companycode') == ['kr-000660']
    ):
        return euroland_document(decoded)
    if parsed.hostname == 'news.samsung.com' and re.fullmatch(
        r'/global/samsung-electronics-announces-(?:first|second|third|fourth)-quarter-\d{4}-results', parsed.path
    ):
        return samsung_document(decoded)
    return None


def ecos_macro_plan(day, question):
    from .macro import SeriesDefinition

    start = day - timedelta(days=6)
    data = dict(
        schema_version='1',
        id='ASK_KOREAN_MACRO',
        question=question,
        series=[],
        sources=[],
        bindings=[],
        yoy_series_ids=[],
        yield_pair=None,
    )
    for tenor, item in ECOS_ITEMS.items():
        sid = 'BOK_ECOS_GOVERNMENT_' + str(tenor) + 'Y'
        url = f'https://ecos.bok.or.kr/api/StatisticSearch/sample/json/kr/1/10/817Y002/D/{start:%Y%m%d}/{day:%Y%m%d}/{item}'
        definition = SeriesDefinition(
            'KR_GOVERNMENT_NOMINAL_' + str(tenor) + 'Y',
            f'한국 국고채 {tenor}년 시장금리',
            f'ECOS 817Y002 시장금리(일별), {item} 국고채({tenor}년), 단위 연%. 원화 명목 기준 수익률이며 쿠폰·개별채권 실행 YTM·ETF 수익률이 아니다.',
            'percent',
            'daily',
            'not_seasonally_adjusted',
            '한국은행 ECOS',
            sid,
            'KR',
            'KRW',
            release_characteristics='영업일 관측; 개별 최초 공개 시각 미확인. 주말·공휴일 값은 생성하지 않는다.',
            revision_characteristics='획득 판본의 값이다. 최초 발표·전체 개정 이력은 없으며 획득 시각을 known-at 하한으로 사용한다.',
            yield_type='nominal',
            tenor_years=tenor,
            max_age_days=10,
        )
        spec = SourceSpec(
            sid,
            url,
            url,
            'primary',
            '한국은행 ECOS',
            f'ECOS 국고채 {tenor}년 최근 일별 금리',
            None,
            None,
            None,
            'KR',
            ('macro', 'interest_rates'),
            ('BOND',),
            'application/json',
            'public_api',
            ECOS_POLICY,
            '한국은행 공식 공개 sample API: 최대 10행, 최근 7일·한 항목만 요청. 인증키 제한을 우회하지 않는다. 공식 통계의 제한된 응답을 출처 표시한 개인 연구·재현 목적으로 보존한다.',
            'full',
            10,
            excerpts=(
                {
                    'id': 'Q_ECOS_IDENTITY',
                    'quote': f'국고채({tenor}년)',
                    'locator': '/StatisticSearch/row/0/ITEM_NAME1',
                    'definition': dict(
                        measure='ECOS_SERIES_IDENTITY',
                        unit='text',
                        period='metadata',
                        currency='KRW',
                        scope=f'KR government bond {tenor} years',
                        adjustment='official series label',
                    ),
                },
            ),
            full_retention_permission='한국은행 ECOS 공식 통계의 공개 API; 제한된 최근 응답만 귀속 표시하여 개인 통계 연구·재현 용도로 보존. 재배포 데이터베이스를 구축하지 않는다.',
        )
        data['series'].append(asdict(definition))
        data['sources'].append(asdict(spec))
        data['bindings'].append(
            dict(
                series_id=definition.canonical_id,
                source_id=sid,
                adapter='ecos_daily_v1',
                field=item,
                start_date=start.isoformat(),
            )
        )
    return data


def ecos_observations(raw, field, tenor, start):
    from .source_pipeline import _decimal

    doc = _parse_json(raw.decode('utf-8'))
    table = doc.get('StatisticSearch')
    if not isinstance(table, dict):
        raise SourceError('ECOS data unavailable; API error is not a zero yield')
    rows = table['row']
    if type(table['list_total_count']) is not int or table['list_total_count'] != len(rows) or len(rows) > 10:
        raise SourceError('ECOS sample incomplete/truncated')
    out = []
    seen = set()
    for i, r in enumerate(rows):
        if (
            r['STAT_CODE'] != '817Y002'
            or r['STAT_NAME'] != '1.3.2.1. 시장금리(일별)'
            or r['ITEM_CODE1'] != field
            or r['ITEM_NAME1'] != f'국고채({tenor}년)'
            or r['UNIT_NAME'] != '연%'
            or any(r.get('ITEM_CODE' + str(n)) is not None for n in (2, 3, 4))
        ):
            raise SourceError('ECOS country/series/tenor/unit identity mismatch')
        if not re.fullmatch(r'\d{8}', r['TIME']):
            raise SourceError('ECOS daily observation date missing')
        at = datetime.strptime(r['TIME'], '%Y%m%d').date()
        if at in seen or at < start:
            raise SourceError('duplicate/out-of-window ECOS observation')
        seen.add(at)
        value = _decimal(r['DATA_VALUE'], 'ECOS DATA_VALUE')
        if not value.is_finite():
            raise SourceError('ECOS finite yield required')
        out.append((at, value, f'/StatisticSearch/row/{i}/DATA_VALUE; TIME={r["TIME"]}; ITEM_CODE1={field}'))
    return out


def parse_korean_candidate(contract, response, candidate):
    from .discovery_contracts import definition, scalar

    fields = candidate['index_identity_fields']
    if contract == 'reb_regional_monthly_v1':
        doc = reb_json(response)
        rows = reb_rows(doc, 'SttsApiTblData')
        if not rows or len(rows) > 5:
            raise SourceError('regional monthly sample empty/over limit')
        periods = []
        for i, r in enumerate(rows):
            if (
                r['STATBL_ID'] != fields['table_id']
                or r['DTACYCLE_CD'] != 'MM'
                or str(r['CLS_ID']) != fields['region_code']
                or r['CLS_NM'] != fields['region']
                or str(r['ITM_ID']) != fields['item_code']
                or r['ITM_NM'] != fields['item_name']
            ):
                raise SourceError('regional observation table/region/item mismatch; national is not local')
            if not re.fullmatch(r'\d{6}', r['WRTTIME_IDTFR_ID']):
                raise SourceError('monthly period missing')
            period = datetime.strptime(r['WRTTIME_IDTFR_ID'], '%Y%m').date()
            params = parse_qs(urlsplit(candidate['url']).query)
            if not params['START_WRTTIME'][0] <= r['WRTTIME_IDTFR_ID'] <= params['END_WRTTIME'][0]:
                raise SourceError('monthly source ignored requested date window')
            periods.append((period, i))
        if len({p for p, _ in periods}) != len(periods):
            raise SourceError('duplicate monthly observation')
        # Two adjacent observations allow a change calculation. Never search
        # backwards for a complete value if the latest row is missing.
        selected = sorted(periods)[-2:]
        records = []
        for period, i in selected:
            count = fields['basis'] == 'reported_sale_count'
            d = definition(
                'KR_APARTMENT_' + fields['basis'].upper(),
                'count' if count else 'index',
                period.strftime('%Y-%m'),
                None,
                fields['region'] + ' apartments; ' + fields['table_title'],
                fields['basis']
                + ('; ' + fields['base'] if fields['base'] else '; 신고 거래호수; 가격/총거래대금 아님'),
            )
            r = scalar(
                doc,
                f'/SttsApiTblData/1/row/{i}/DTA_VAL',
                fields['region'] + ' ' + fields['table_title'],
                d,
                positive=not count,
            )
            value = Decimal(r['quote'])
            if count and (value < 0 or value != value.to_integral_value()):
                raise SourceError('invalid reported apartment count')
            records.append(r)
        period = selected[-1][0]
        end = date(period.year, period.month, calendar.monthrange(period.year, period.month)[1])
        return dict(
            observed_at=end.isoformat(),
            published_at=None,
            valid_as_of=end.isoformat(),
            records=records,
            complete=True,
            limitations=[
                '한국부동산원 공식 월별 지역 집계이며 개별 아파트의 실거래가격·현재 매수가격·임대수익률이 아니다.',
                '조사 매매/전세지수와 신고 실거래지수는 표본·작성 방법·발표 시차가 다르다. 서로 같은 가격으로 합치지 않는다.',
                '신고 지연·취소·개정 가능성이 있다. 최초 발표 시각과 개정 이력은 미확인이므로 획득 이후만 현재 판본으로 사용한다.',
            ],
        )
    if contract == 'euroland_hynix_quarterly_v1':
        if fields.get('company_code') != 'kr-000660':
            raise SourceError('wrong company financial statement')
        doc = euroland_document(_decode(response.body, response.content_type))
        groups = doc['LevelZeroItems']
        matches = [(i, g) for i, g in enumerate(groups) if g.get('name') == 'Quarterly']
        if len(matches) != 1:
            raise SourceError('quarterly statement required; annual is not quarterly')
        gi, group = matches[0]
        tabs = [(i, t) for i, t in enumerate(group['Data']) if t.get('name') == 'Income Statement']
        if len(tabs) != 1:
            raise SourceError('unique income statement required')
        ti, tab = tabs[0]
        columns = tab['Columns']
        periods = []
        for i, p in enumerate(columns):
            m = re.fullmatch(r'(\d{4}) ([1-4])Q', p)
            if not m:
                raise SourceError('financial reporting period changed')
            periods.append((int(m[1]) * 4 + int(m[2]) - 1, i, p))
        if len(set(columns)) != len(columns) or len(columns) < 2:
            raise SourceError('duplicate/missing quarters')
        ordered = sorted(periods)
        latest = ordered[-1]
        chosen = ordered[-2] if candidate['category'] == 'company_prior' else latest
        if candidate['category'] == 'company_prior' and chosen[0] != latest[0] - 1:
            raise SourceError('adjacent prior quarter unavailable')
        year = int(chosen[2][:4])
        q = int(chosen[2][5])
        month = q * 3
        end = date(year, month, calendar.monthrange(year, month)[1])
        records = []
        for name, key in [
            ('Revenue', 'REVENUE'),
            ('Operating Profit', 'OPERATING_PROFIT'),
            ('Net Profit', 'NET_PROFIT'),
        ]:
            metrics = [
                (i, s) for i, s in enumerate(tab['Series']) if s.get('name') == name and s.get('unit') == 'KRW million'
            ]
            if len(metrics) != 1:
                raise SourceError('financial field/unit missing: ' + name)
            si, series = metrics[0]
            if len(series['Data']) != len(columns):
                raise SourceError('period/value columns misaligned')
            point = series['Data'][chosen[1]]
            # str=null with nr=0 is MISSING, not zero profit. Preserve str
            # instead of rounding the provider's decimal representation.
            if point.get('str') is None:
                raise SourceError('latest financial value is missing: ' + name)
            d = definition(
                'SK_HYNIX_' + key,
                'KRW_million',
                f'{year}Q{q}',
                'KRW',
                'SK hynix; issuer-linked Euroland quarterly statement',
                'provider_reported_quarterly; consolidation/attribution/audit_basis_not_cross_checked_against_filing',
            )
            records.append(
                scalar(
                    doc,
                    f'/LevelZeroItems/{gi}/Data/{ti}/Series/{si}/Data/{chosen[1]}/str',
                    'SK하이닉스 '
                    + f'{year}Q{q} '
                    + {'REVENUE': '매출', 'OPERATING_PROFIT': '영업이익', 'NET_PROFIT': '순이익'}[key],
                    d,
                    positive=key == 'REVENUE',
                )
            )
        latest_year = int(latest[2][:4])
        latest_month = int(latest[2][5]) * 3
        latest_end = date(latest_year, latest_month, calendar.monthrange(latest_year, latest_month)[1])
        return dict(
            observed_at=latest_end.isoformat(),
            published_at=None,
            valid_as_of=latest_end.isoformat(),
            records=records,
            complete=True,
            limitations=[
                'SK하이닉스 공식 IR이 연결한 Euroland 제공자 자료다. DART/공식 원공시의 독립 교차 확인은 완료하지 않았다.',
                '연결·별도, 지배주주 귀속, 회계 조정 정의를 원공시에서 재검증하기 전 다른 기업과 순이익을 직접 순위화하지 않는다.',
                '표시된 소수 자릿수는 제공자 응답이며 그만큼 정확함을 보증하지 않는다. 분기 숫자를 TTM/연간 전망이나 현재 valuation으로 바꾸지 않는다.',
            ],
        )
    if contract == 'samsung_quarterly_release_v1':
        doc = samsung_document(_decode(response.body, response.content_type))
        period = doc['period']
        if not candidate['url'].endswith(
            '/samsung-electronics-announces-' + doc['quarter'] + '-quarter-' + period[:4] + '-results'
        ):
            raise SourceError('Samsung release URL/actual fiscal period mismatch')
        records = []
        if candidate['category'] == 'company_business':
            for key, label in [
                ('ds', 'DS 반도체 사업부'),
                ('mx', 'MX/네트워크 사업부 (영업손실 포함)'),
                ('guidance', '하반기 메모리 수요 경영진 기대'),
            ]:
                if key not in doc['texts']:
                    raise SourceError('Samsung business/guidance field unavailable: ' + key)
                records.append(
                    dict(
                        quote=doc['texts'][key],
                        locator='body:official_business_' + key,
                        definition=definition(
                            'SAMSUNG_' + key.upper(),
                            'text',
                            period,
                            'KRW',
                            'Samsung Electronics official release',
                            (
                                'management_expectation_not_actual'
                                if key == 'guidance'
                                else 'reported_segment_description'
                            ),
                        ),
                        extraction=None,
                        label=label,
                        limitations=['경영진 전망은 실제 미래 실적의 확인이 아니다.'],
                    )
                )
        else:
            for key, label in [
                ('revenue', '연결 매출'),
                ('operating_profit', '영업이익'),
                ('revenue_qoq_percent', '매출 전분기 대비 증가율'),
            ]:
                records.append(
                    dict(
                        quote=doc['metrics'][key],
                        locator='samsung_scalar:' + key,
                        definition=definition(
                            'SAMSUNG_' + key.upper(),
                            'percent' if key.endswith('percent') else 'KRW_trillion',
                            period,
                            'KRW',
                            'Samsung Electronics consolidated quarterly results',
                            'official_release_quarterly_not_TTM',
                        ),
                        extraction='decimal_scalar_v1',
                        label='삼성전자 ' + label,
                        limitations=[],
                    )
                )
        missing = ['순이익'] if candidate['category'] == 'company_results' else []
        return dict(
            observed_at=period,
            published_at=doc['published_at'],
            valid_as_of=period,
            records=records,
            complete=not missing,
            missing_fields=missing,
            limitations=[
                '삼성전자 공식 연결 분기 실적 발표문이다. 순이익·현재 주가·컨센서스는 이 필드에 없다.',
                '공식 전망·AI 수요 기대는 현재 투자 가격의 매력이나 실제 미래 성장의 증명이 아니다.',
            ],
        )
    raise SourceError('unsupported reviewed Korean document contract')


def calculate_korean_observations(case, require_dates=False):
    """Descriptive ratios only, with same-company/region/basis input checks."""
    from .models import MetricResult
    from .source_pipeline import _digest

    sources = {s.id: s for s in case.sources}
    rows = [
        e
        for e in case.evidence
        if e.provenance
        and e.provenance.match_status == 'matched'
        and e.provenance.freshness == 'fresh'
        and e.value is not None
        and e.kind == 'observed_fact'
        and sources[e.source_id].provenance.status == 'available'
    ]
    if require_dates:
        from .source_pipeline import dated_evidence

        rows = [e for e in rows if dated_evidence(e)]
    out = []

    def ratio(label, numerator, denominator, method, subtract=False):
        if denominator.value <= 0:
            return
        with localcontext() as ctx:
            ctx.prec = 50
            value = (numerator.value / denominator.value - (1 if subtract else 0)) * 100
        refs = (numerator.id, denominator.id)
        out.append(
            MetricResult(
                'CALC_KR_' + _digest([method, refs])[:16],
                label,
                value,
                'percent',
                method,
                refs,
                numerator.asset_ids,
                (
                    '관측 자료의 설명용 계산: 같은 정의의 확인한 입력만 계산; 투자 우위·미래 수익·원공시 진실의 증명이 아니다.',
                ),
            )
        )

    for identifier in ('SAMSUNG', 'SK_HYNIX'):
        chosen = [
            e
            for e in rows
            if identifier in e.asset_ids and e.provenance.definition['measure'].startswith(identifier + '_')
        ]
        revenues = [e for e in chosen if e.provenance.definition['measure'] == identifier + '_REVENUE']
        profits = [e for e in chosen if e.provenance.definition['measure'] == identifier + '_OPERATING_PROFIT']
        for revenue in revenues:
            ds = revenue.provenance.definition
            matches = [
                p
                for p in profits
                if all(
                    p.provenance.definition[k] == ds[k] for k in ('unit', 'period', 'currency', 'scope', 'adjustment')
                )
            ]
            if len(matches) == 1:
                ratio(
                    ('삼성전자' if identifier == 'SAMSUNG' else 'SK하이닉스')
                    + ' '
                    + ds['period']
                    + ' 표시 영업이익/매출',
                    matches[0],
                    revenue,
                    'reported_operating_margin_v1',
                )
        for key in ('REVENUE', 'OPERATING_PROFIT', 'NET_PROFIT'):
            series = [e for e in chosen if e.provenance.definition['measure'] == identifier + '_' + key]
            if len(series) != 2:
                continue
            previous, latest = sorted(series, key=lambda e: e.provenance.definition['period'])
            a, b = previous.provenance.definition, latest.provenance.definition
            if not all(a[k] == b[k] for k in ('measure', 'unit', 'currency', 'scope', 'adjustment')):
                continue
            if not re.fullmatch(r'\d{4}Q[1-4]', a['period']) or not re.fullmatch(r'\d{4}Q[1-4]', b['period']):
                continue
            serial = lambda p: int(p[:4]) * 4 + int(p[-1]) - 1
            if serial(b['period']) - serial(a['period']) != 1:
                continue
            ratio(
                'SK하이닉스 '
                + b['period']
                + ' '
                + {'REVENUE': '매출', 'OPERATING_PROFIT': '영업이익', 'NET_PROFIT': '순이익'}[key]
                + ' 전분기 대비',
                latest,
                previous,
                'same_company_quarterly_change_v1',
                True,
            )
    groups = {}
    for e in rows:
        d = e.provenance.definition
        if not d['measure'].startswith('KR_APARTMENT_'):
            continue
        key = tuple(d[k] for k in ('measure', 'unit', 'currency', 'scope', 'adjustment'))
        groups.setdefault(key, []).append(e)
    for series in groups.values():
        if len(series) != 2:
            continue
        previous, latest = sorted(series, key=lambda e: e.provenance.definition['period'])
        a, b = previous.provenance.definition, latest.provenance.definition
        if not re.fullmatch(r'\d{4}-\d{2}', a['period']) or not re.fullmatch(r'\d{4}-\d{2}', b['period']):
            continue
        serial = lambda p: int(p[:4]) * 12 + int(p[-2:]) - 1
        if serial(b['period']) - serial(a['period']) != 1:
            continue
        ratio(b['scope'] + ' ' + b['period'] + ' 전월 대비', latest, previous, 'same_region_monthly_change_v1', True)
    return tuple(out)
