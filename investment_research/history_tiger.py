"""TIGER overseas-index ETF NAV series with distributions reinvested (KRW, pre-tax).

TIGER US equity ETFs pay cash distributions, so their market price is a price
return. The issuer's public chart endpoint also returns a cumulative NAV
series; this module labels it total return only after proving, on every
acquisition and from a second issuer table, that it keeps the distributions:

    market price / NAV drifts down each calendar year by the annual
    distribution rate the issuer publishes in its separate table.

Observed on the live data (2022-2025) the two agreed within 0.1 pp a year for
both reviewed products, while a NAV that did not reinvest would differ by the
full rate (0.37-1.44 pp). The series is a NAV, not an executable price, so
plans may use it only as a market benchmark.
"""

import html
import re
from datetime import date, timedelta
from decimal import Decimal
from statistics import mean

from .decision_data import number, validate_dataset, timestamp as _time
from .history import VERSION, _json, _kodex_instants, _text_number
from .sources import SourceError, _sha

_YMD = re.compile(r'\d{8}')
_YEAR = re.compile(r'<th[^>]*colspan="2"[^>]*>\s*(\d{4})년\s*</th>')
_CODE = re.compile(r'<p class="code">\((\d{6})\)</p>')
_CELL = re.compile(r'<td>\s*<span>([^<]*)</span>\s*</td>')
_AMOUNT = re.compile(r'\d{1,3}(?:,\d{3})*|\d+')
_RATE = re.compile(r'(\d+(?:\.\d+)?)%')
PROVIDER = 'tiger_nav_reinvested'


def estimate_span(item, catalog, today):
    """(trading-day rows, ISO weeks) the endpoint will return, before any request is made."""
    provider = catalog['providers'][PROVIDER]
    listed = date.fromisoformat(provider['products'][item['fund']]['listed'])
    days = min((today - listed).days, provider['history_years_limit'] * 366)
    return days * 5 // 7 + 1, days // 7 + 2


def parse_profit(body, ksd, contract):
    """Cumulative percent rows; a missing value stays missing and is listed."""
    data = _json(body, 'TIGER profit chart')
    rows = data.get('rtnData') if isinstance(data, dict) else None
    if not isinstance(rows, list) or not rows:
        raise SourceError('TIGER profit chart has no rows')
    out, missing, prior = [], [], None
    for r in rows:
        if (
            not isinstance(r, dict)
            or r.get('ksdFund') != ksd
            or html.unescape(str(r.get('jongName', ''))) != contract['name']
        ):
            raise SourceError('TIGER chart row names a different fund')
        stamp = str(r.get('wkdate', ''))
        if not _YMD.fullmatch(stamp):
            raise SourceError('TIGER chart row lacks a YYYYMMDD date')
        day = date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:]))
        if prior is not None and day <= prior:
            raise SourceError('TIGER chart rows must be sorted and unique')
        prior = day
        nav, prc = r.get('nav'), r.get('prc')
        if nav is None or prc is None:
            missing.append(day.isoformat())
            continue
        for value in (nav, prc):
            if isinstance(value, bool) or not isinstance(value, (int, Decimal)) or number(value) <= -100:
                raise SourceError('TIGER cumulative percent is malformed or at/below -100')
        out.append([day.isoformat(), _text_number(prc), _text_number(nav)])
    if not out:
        raise SourceError('TIGER chart has no complete row')
    return dict(rows=out, missing=missing)


def parse_distribution(page_body, row_body, contract):
    """Annual distribution (KRW, %) by year, with column years read from the header."""
    try:
        page, row = page_body.decode('utf-8'), row_body.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise SourceError('TIGER distribution table is not UTF-8') from exc
    years = [int(y) for y in _YEAR.findall(page)]
    if len(years) < 2 or years != sorted(set(years), reverse=True):
        raise SourceError('TIGER distribution table header years are missing or unordered')
    code = _CODE.search(row)
    if code is None or code.group(1) != contract['ticker']:
        raise SourceError('TIGER distribution row names a different fund')
    cells = [c.strip() for c in _CELL.findall(row)]
    if len(cells) != 2 * len(years):
        raise SourceError('TIGER distribution row does not match the header years')
    by_year = {}
    for i, year in enumerate(years):
        amount, rate = cells[2 * i], cells[2 * i + 1]
        if (amount, rate) == ('-', '-'):
            continue  # No figure for that year; the year is not compared.
        a, r = _AMOUNT.fullmatch(amount), _RATE.fullmatch(rate)
        if not a or not r:
            raise SourceError('TIGER distribution cell is malformed')
        by_year[str(year)] = dict(amount_krw=amount.replace(',', ''), rate_pct=r.group(1))
    return dict(years=years, by_year=by_year)


def verify_reinvestment(rows, distribution, provider):
    """Refuse the total-return label unless NAV keeps what the price loses."""
    window = provider['verification_window_rows']
    tolerance, minimum_rate = number(provider['tolerance_pp']), number(provider['min_rate_pct'])
    ratios = {}
    for day, prc, nav in rows:
        ratios.setdefault(int(day[:4]), []).append((1 + number(prc) / 100) / (1 + number(nav) / 100))

    def year_end(year):
        values = ratios.get(year, [])
        return mean(values[-window:]) if len(values) >= window else None

    last_year, checks = int(rows[-1][0][:4]), []
    for text, figure in sorted(distribution['by_year'].items()):
        year, rate = int(text), number(figure['rate_pct'])
        if year >= last_year:
            continue  # A partial year has no year-end to compare.
        now, before = year_end(year), year_end(year - 1)
        if now is None or before is None:
            continue
        observed = (now / before - 1) * 100
        difference = observed + rate
        checks.append(
            dict(
                year=year,
                observed_pp=_text_number(observed.quantize(Decimal('0.01'))),
                issuer_rate_pct=figure['rate_pct'],
                difference_pp=_text_number(difference.quantize(Decimal('0.01'))),
                discriminating=rate >= minimum_rate,
            )
        )
        if abs(difference) > tolerance:
            raise SourceError(
                f'NAV does not track the issuer distribution rate in {year}: price/NAV moved {observed:.2f} pp, '
                f'issuer table says {rate} %; distributions may not be reinvested'
            )
    if sum(1 for c in checks if c['discriminating']) < provider['min_comparable_years']:
        raise SourceError('too few comparable years to verify that distributions are reinvested')
    return checks


def collect(session, item, catalog, today):
    provider = catalog['providers'][PROVIDER]
    contract = provider['products'][item['fund']]
    start = max(date.fromisoformat(contract['listed']), today - timedelta(days=provider['history_years_limit'] * 366))
    out = dict(
        contract=contract,
        provider={
            k: provider[k]
            for k in (
                'close_time_kst',
                'known_at_kst',
                'boundary',
                'nav_note',
                'revision_note',
                'tax_note',
                'verification_window_rows',
                'tolerance_pp',
                'min_rate_pct',
                'min_comparable_years',
            )
        },
    )
    url = provider['history_endpoint'].format(
        ksd=item['fund'], start=start.strftime('%Y%m%d'), end=today.strftime('%Y%m%d')
    )
    response, retrieved_at = session.get(PROVIDER, url)
    out['history'] = dict(
        request_start=start.isoformat(),
        url=url,
        retrieved_at=retrieved_at,
        raw_sha256=_sha(response.body),
        raw_bytes=len(response.body),
        data=parse_profit(response.body, item['fund'], contract),
    )
    page, page_at = session.get(PROVIDER, provider['distribution_page'], cache=True)
    row_url = provider['distribution_endpoint'].format(ticker=contract['ticker'])
    row, row_at = session.get(PROVIDER, row_url)
    out['distribution'] = dict(
        urls=[provider['distribution_page'], row_url],
        retrieved_at=max(page_at, row_at),
        raw_sha256=[_sha(page.body), _sha(row.body)],
        parsed=parse_distribution(page.body, row.body, contract),
    )
    return out


def dataset(item, retained):
    contract, provider = retained['contract'], retained['provider']
    history, distribution = retained['history'], retained['distribution']
    retrieved = _time(history['retrieved_at'])
    published, rows = [], []
    for day, price, nav in history['data']['rows']:
        at, known_at = _kodex_instants(day, provider)
        if known_at <= retrieved:  # a row not yet published at retrieval is neither verified nor emitted
            published.append([day, price, nav])
            rows.append(
                dict(at=at.isoformat(), known_at=known_at.isoformat(), value=_text_number(1 + number(nav) / 100))
            )
    if not rows:
        raise SourceError('no published TIGER NAV in the history')
    checks = verify_reinvestment(published, distribution['parsed'], provider)
    summary = '; '.join(
        f'{c["year"]}: 가격/NAV 비율 {c["observed_pp"]}%p, 발행사 분배율 {c["issuer_rate_pct"]}%' for c in checks
    )
    result = dict(
        schema_version='investment-prices-v1',
        synthetic=False,
        instrument_id=contract['instrument_id'],
        asset_id=item.get('asset_id', contract['asset_id']),
        name=contract['name'] + ' (발행사 NAV, 분배금 재투자)',
        currency='KRW',
        unit='index (1 + cumulative NAV return from the request start date)',
        measure='tiger_issuer_nav_distributions_reinvested_index',
        source='미래에셋자산운용 TIGER ETF 공개 차트(누적 NAV 수익률)와 연간 분배율 표 ' + contract['ticker'],
        calendar=provider['boundary'] + ' ' + provider['nav_note'] + ' ' + provider['revision_note'],
        survivorship='single_instrument',
        return_kind='total_return',
        adjustment='pit_total_return_index',
        return_basis='issuer_nav_reinvested',
        return_basis_note=(
            f'{contract["index"]}를 추종하는 상품명에 (H)가 없는 비헤지 상품이라 원화 가격에 달러/원 변동이 포함된다. '
            f'NAV 계열이 분배금을 재투자한 값임을 발행사의 별도 분배율 표와 대조해 확인했다({summary}). '
            + provider['tax_note']
        ),
        retrieved_at=max(retrieved, _time(distribution['retrieved_at'])).isoformat(),
        rows=rows,
        provenance=dict(
            method_version=VERSION,
            provider=PROVIDER,
            fund=item['fund'],
            raw_sha256=[history['raw_sha256'], *distribution['raw_sha256']],
            verification=checks,
            request_start=history['request_start'],
            first_returned=history['data']['rows'][0][0],
            missing_dates=history['data']['missing'],
        ),
    )
    validate_dataset(result)
    return result
