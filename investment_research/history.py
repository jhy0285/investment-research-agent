"""Point-in-time long histories from reviewed public providers.

This connects real data to the decision contracts in ``decision_data``:
exchange trade records and an ETF issuer's own price history become
``investment-prices-v1`` datasets, and ALFRED vintages become feature rows
whose ``known_at`` is the vintage, never the latest revision. Derived price
features use only rows known at their time.

Nothing here grades, ranks or approves an investment. A coin price is labelled
a lower bound of holder return, not total return; only a fund the issuer
states reinvests every distribution is labelled total return, and that
statement is re-checked on every acquisition.
"""

from bisect import bisect_right
from datetime import date, datetime, timedelta, timezone
from statistics import median
from decimal import Decimal, InvalidOperation
import json
import math
from pathlib import Path
import re
import time
import urllib.parse

from .decision_data import contract, digest, encode, load, number, save, validate_dataset, timestamp as _time
from .sources import MAX_BYTES, SourceError, _access_policy, _fetch_http, _reject_duplicate_keys, _response, _sha, _url

VERSION = 'pit_history_v2'
# v1 collected Upbit days and ALFRED vintages without a return basis. v2 adds
# KRX-close datasets and labels returns; v1 runs still replay as v1.
VERSIONS = ('pit_history_v1', 'pit_history_v2')
KST = timezone(timedelta(hours=9))
CATALOG = Path(__file__).with_name('catalog') / 'history.json'
ARTIFACTS = ('spec.json', 'snapshots.json', 'history.json', 'history.md')
_NAME = re.compile(r'[A-Za-z0-9_.-]{1,64}\Z')
_UPBIT_CANDLE = re.compile(r'\d{4}-\d{2}-\d{2}T00:00:00')
_UPBIT_MINUTE = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:00')
_YMD = re.compile(r'\d{8}')
MAX_PRICE_PAGES = 60
DERIVED_GAP_DAYS = 7
# Upbit `timestamp` is when the candle's last tick was stored; observed lag
# after the boundary is milliseconds. Larger lags are treated as data errors.
UPBIT_STORE_LAG = timedelta(seconds=60)
RETRIES = 2
TRANSIENT = (429, 500, 502, 503, 504)


def load_catalog(path=CATALOG):
    data = load(path)
    if data.get('schema_version') != 'history-catalog-v1' or data.get('method_version') != VERSION:
        raise SourceError('unsupported history catalog')
    return data


def _day(value, name):
    if not isinstance(value, str) or len(value) != 10:
        raise SourceError(name + ': use YYYY-MM-DD')
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SourceError(name + ': invalid date') from exc


def _integer(item, key, low, high):
    value = item.get(key)
    if type(value) is not int or not low <= value <= high:
        raise SourceError(f'{key}: integer between {low} and {high} required')
    return value


def _vintage_dates(item, today):
    start = _day(item.get('vintage_start'), 'vintage_start')
    end = min(_day(item['vintage_end'], 'vintage_end') if item.get('vintage_end') else today, today)
    if start > end:
        raise SourceError('vintage_start follows vintage_end or today')
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += timedelta(days=item['vintage_step_days'])
    if dates[-1] != end:
        dates.append(end)
    return dates


PRICE_PROVIDERS = ('upbit_day_candles', 'kodex_issuer_weekly', 'upbit_aligned_candles')


def instrument_id(item, catalog):
    providers = catalog['providers']
    if item['provider'] == 'kodex_issuer_weekly':
        product = providers['kodex_issuer_weekly']['products'].get(item.get('fund'))
        if product is None:
            raise SourceError('fund has no reviewed issuer contract')
        return product['instrument_id']
    market = providers['upbit_day_candles']['markets'].get(item.get('market'))
    if market is None:
        raise SourceError('market has no reviewed history contract')
    if item['provider'] == 'upbit_aligned_candles':
        return market['instrument_id'] + '_AT_' + str(item.get('align_to'))
    return market['instrument_id']


def _price_key(item):
    if item['provider'] == 'kodex_issuer_weekly':
        return 'prices:kodex:' + item['fund']
    if item['provider'] == 'upbit_aligned_candles':
        return 'prices:aligned:' + item['market'] + '@' + item['align_to']
    return 'prices:' + item['market']


@contract
def validate_spec(spec, catalog, today=None):
    """Reject unreviewed providers, series and unbounded requests before any network use."""
    today = today or datetime.now(timezone.utc).date()
    if not isinstance(spec, dict) or spec.get('schema_version') != 'investment-history-spec-v1':
        raise SourceError('unsupported investment history spec')
    prices, features = spec.get('prices', []), spec.get('features', [])
    if not isinstance(prices, list) or not isinstance(features, list) or not prices + features:
        raise SourceError('declare prices and/or features to collect')
    if len(prices) > 5 or len(features) > 20:
        raise SourceError('at most five price series and twenty features')
    providers = catalog['providers']
    instruments, requests = set(), 0
    weekly = {}
    for item in prices:
        if not isinstance(item, dict) or item.get('provider') not in PRICE_PROVIDERS:
            raise SourceError('price provider must be a reviewed provider contract')
        if 'asset_id' in item and (not isinstance(item['asset_id'], str) or not _NAME.fullmatch(item['asset_id'])):
            raise SourceError('invalid asset_id override')
        instrument = instrument_id(item, catalog)
        if instrument in instruments:
            raise SourceError('duplicate price instrument')
        if item['provider'] == 'upbit_day_candles':
            provider = providers['upbit_day_candles']
            start = _day(item.get('start'), 'start')
            if start < _day(provider['earliest'], 'earliest') or start > today:
                raise SourceError('start precedes the provider history or follows today')
            requests += math.ceil(((today - start).days + 1) / provider['page_size'])
        elif item['provider'] == 'kodex_issuer_weekly':
            listed = _day(providers['kodex_issuer_weekly']['products'][item['fund']]['listed'], 'listed')
            weekly[instrument] = (today - listed).days // 7 + 2
            requests += 2
        else:
            # Alignment needs the other series' closing instants, collected first.
            if item.get('align_to') not in weekly:
                raise SourceError('aligned candles need a KRX-close series listed earlier in this spec')
            requests += weekly[item['align_to']]
        instruments.add(instrument)
    names, hosts = set(), set()
    for item in features:
        name = item.get('name') if isinstance(item, dict) else None
        if not isinstance(name, str) or not _NAME.fullmatch(name) or name in names:
            raise SourceError('feature names must be unique safe identifiers')
        names.add(item['name'])
        if item.get('provider') == 'alfred_vintage_csv':
            if item.get('series') not in providers['alfred_vintage_csv']['series']:
                raise SourceError('series has no reviewed vintage contract')
            _integer(item, 'vintage_step_days', 7, 92)
            _integer(item, 'window_days', 30, 800)
            if item.get('transform', 'level') not in ('level', 'yoy_percent'):
                raise SourceError('unsupported vintage transform')
            if item.get('transform') == 'yoy_percent':
                contract = providers['alfred_vintage_csv']['series'][item['series']]
                if contract['frequency'] != 'monthly' or item['window_days'] < 400:
                    raise SourceError('year-over-year needs a monthly series and a window of at least 400 days')
            requests += len(_vintage_dates(item, today))
        elif item.get('provider') == 'factset_earnings_insight':
            provider = providers['factset_earnings_insight']
            if item.get('series') not in provider['series']:
                raise SourceError('series has no reviewed FactSet contract')
            if _day(item.get('start'), 'start') < _day(provider['earliest'], 'earliest'):
                raise SourceError('start precedes the reviewed FactSet archive')
            _integer(item, 'step_weeks', 1, 13)
            requests += 2 * len(_issue_dates(item, today))  # Friday, then Thursday in holiday weeks
            hosts.add('factset')
        elif item.get('provider') == 'price_derived':
            if item.get('instrument_id') not in instruments:
                raise SourceError('derived feature must use a price series collected in this spec')
            if item.get('kind') == 'trailing_return':
                _integer(item, 'days', 5, 400)
            elif item.get('kind') == 'close_to_sma':
                _integer(item, 'observations', 5, 400)
            else:
                raise SourceError('unsupported derived feature kind')
        else:
            raise SourceError('feature provider must be a reviewed provider contract')
    if any(f['provider'] == 'alfred_vintage_csv' for f in features):
        requests += 1  # robots.txt, checked once per host
    if weekly:
        requests += 1
    requests += len(hosts)
    if requests > catalog['max_requests']:
        raise SourceError(f'spec needs about {requests} requests; reviewed limit is {catalog["max_requests"]}')
    return spec


class _Session:
    """One bounded acquisition: robots once per host, provider pacing, no redirects."""

    def __init__(self, catalog, fetcher, clock, sleep, progress):
        self.catalog, self.perform = catalog, fetcher or _fetch_http
        self.clock, self.sleep, self.progress = clock, sleep, progress
        self.policies, self.last, self.requests = {}, {}, 0

    def get(self, provider_name, url, missing_ok=False):
        provider = self.catalog['providers'][provider_name]
        host = _url(url).hostname
        if host not in self.policies:
            policy = dict(
                url=provider['policy_url'],
                review_note=provider['policy_note'],
                access_method=provider['access_method'],
                robots='not_checked',
            )
            if provider['access_method'] == 'public_http':
                self._count()  # robots.txt is a request to the same host
            _access_policy(url, provider['access_method'], self.perform, self.clock().isoformat(), policy)
            if provider['access_method'] == 'public_http':
                self.last[provider_name] = time.monotonic()  # crawl delay applies after robots.txt too
            self.policies[host] = policy
        for attempt in range(1, RETRIES + 2):
            waited = time.monotonic() - self.last.get(provider_name, -math.inf)
            # Retries back off from at least one second, past per-second rate limits.
            pause = (
                provider['min_interval_seconds']
                if attempt == 1
                else max(1, provider['min_interval_seconds']) * 2 ** (attempt - 2)
            )
            if waited < pause:
                self.sleep(pause - waited)
            self._count()
            try:
                response = _response(self.perform, url, provider.get('max_bytes', MAX_BYTES))
            except OSError:
                # Timeouts and dropped connections are retried a bounded number
                # of times; the retry never changes what a success records.
                if attempt > RETRIES:
                    raise
                continue
            finally:
                self.last[provider_name] = time.monotonic()
            if response.status in TRANSIENT and attempt <= RETRIES:
                continue
            break
        # Retrieval time is recorded after the body has been read.
        retrieved_at = self.clock().astimezone(timezone.utc).isoformat()
        if missing_ok and response.status == 404:
            return None, retrieved_at
        if response.status != 200:
            raise SourceError(f'{provider_name}: HTTP {response.status}')
        if self.progress:
            self.progress(f'{provider_name}: {self.requests}번째 요청 완료')
        return response, retrieved_at

    def _count(self):
        if self.requests >= self.catalog['max_requests']:
            raise SourceError('reviewed request limit reached')
        self.requests += 1


def _text_number(value):
    """Exact decimal text; never scientific notation, never float rounding."""
    result = format(number(value).normalize(), 'f')
    return '0' if result in ('-0', '') else result


def parse_upbit(body, market):
    try:
        data = json.loads(
            body.decode('utf-8'),
            parse_float=Decimal,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=lambda _: (_ for _ in ()).throw(SourceError('nonfinite JSON number')),
        )
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise SourceError('Upbit candles are not valid JSON') from exc
    if not isinstance(data, list):
        raise SourceError('Upbit candles must be a JSON array')
    rows = []
    for c in data:
        if not isinstance(c, dict) or c.get('market') != market:
            raise SourceError('Upbit candle market differs from the request')
        candle = c.get('candle_date_time_utc')
        if not isinstance(candle, str) or not _UPBIT_CANDLE.fullmatch(candle):
            raise SourceError('Upbit daily candle must start at 00:00 UTC')
        price, last = c.get('trade_price'), c.get('timestamp')
        if (
            isinstance(price, bool)
            or not isinstance(price, (int, Decimal))
            or (last is not None and type(last) is not int)
        ):
            raise SourceError('Upbit candle close or last-tick storage time is missing')
        if number(price) <= 0:
            raise SourceError('nonpositive Upbit close')
        rows.append(dict(candle=candle[:10], close=_text_number(price), last_tick_stored_ms=last))
    return rows


def parse_alfred(body, series, vintage, window_days):
    try:
        lines = body.decode('utf-8-sig').splitlines()
    except UnicodeDecodeError as exc:
        raise SourceError('ALFRED CSV is not UTF-8') from exc
    header = f'observation_date,{series}_{vintage.strftime("%Y%m%d")}'
    if not lines or lines[0].strip() != header:
        raise SourceError('ALFRED header does not name the requested series vintage')
    first = vintage - timedelta(days=window_days)
    rows, prior = [], None
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.strip().split(',')
        if len(parts) != 2:
            raise SourceError('ALFRED CSV row is not a date/value pair')
        observed = _day(parts[0], 'observation_date')
        if prior is not None and observed <= prior:
            raise SourceError('ALFRED observations must be sorted and unique')
        prior = observed
        # A vintage cannot contain a later period. Seeing one means the
        # response is not a point-in-time snapshot (e.g. a window parameter).
        if observed > vintage:
            raise SourceError('vintage contains observations after its vintage date')
        if observed < first or parts[1] in ('', '.'):
            continue  # Missing values stay missing; they are never zero.
        try:
            value = Decimal(parts[1])
        except InvalidOperation as exc:
            raise SourceError('ALFRED value is not a decimal') from exc
        rows.append([observed.isoformat(), _text_number(value)])
    return rows


def _json(body, name):
    try:
        return json.loads(
            body.decode('utf-8'),
            parse_float=Decimal,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=lambda _: (_ for _ in ()).throw(SourceError('nonfinite JSON number')),
        )
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise SourceError(name + ' is not valid JSON') from exc


def parse_kodex_detail(body, contract):
    """Keep only the issuer statements the total-return label depends on."""
    data = _json(body, 'KODEX product detail')
    try:
        product, divide = data['info']['product'], data['info']['divideList']
    except (KeyError, TypeError) as exc:
        raise SourceError('KODEX product detail lacks product or distribution fields') from exc
    if product.get('stkTicker') != contract['ticker'] or product.get('fNm') != contract['name']:
        raise SourceError('KODEX product detail names a different fund')
    remark = product.get('dividRemark')
    if not isinstance(remark, str) or not isinstance(divide, list):
        raise SourceError('KODEX distribution policy is missing')
    return dict(ticker=product['stkTicker'], name=product['fNm'], divid_remark=remark, divide_list=divide)


def parse_kodex_history(body, contract):
    data = _json(body, 'KODEX price history')
    if not isinstance(data, list) or not data:
        raise SourceError('KODEX price history must be a non-empty JSON array')
    rows, prior = [], None
    for r in data:
        if not isinstance(r, dict) or not _YMD.fullmatch(str(r.get('GIJUN_YMD', ''))):
            raise SourceError('KODEX row lacks a YYYYMMDD reference date')
        day = date(int(r['GIJUN_YMD'][:4]), int(r['GIJUN_YMD'][4:6]), int(r['GIJUN_YMD'][6:]))
        if prior is not None and day <= prior:
            raise SourceError('KODEX rows must be sorted and unique')
        prior = day
        values = [r.get(k) for k in ('PRICE', 'NAV', 'JISU')]
        if any(isinstance(v, bool) or not isinstance(v, (int, Decimal)) or number(v) <= 0 for v in values):
            raise SourceError('KODEX close, NAV and index must be positive numbers')
        rows.append([day.isoformat(), *(_text_number(v) for v in values)])
    if rows[0][0] < contract['listed']:
        raise SourceError('KODEX history starts before the fund was listed')
    return rows


def parse_upbit_minute(body, market, unit):
    data = _json(body, 'Upbit minute candles')
    if not isinstance(data, list) or len(data) > 1:
        raise SourceError('aligned request must return at most one candle')
    if not data:
        return None
    c = data[0]
    if not isinstance(c, dict) or c.get('market') != market or c.get('unit') != unit:
        raise SourceError('Upbit minute candle differs from the request')
    candle, price, last = c.get('candle_date_time_utc'), c.get('trade_price'), c.get('timestamp')
    if not isinstance(candle, str) or not _UPBIT_MINUTE.fullmatch(candle):
        raise SourceError('Upbit minute candle time is malformed')
    # Older candles carry timestamp=null; the close is then dated
    # conservatively after the candle end instead of being rejected.
    if isinstance(price, bool) or not isinstance(price, (int, Decimal)) or number(price) <= 0:
        raise SourceError('Upbit candle close is missing')
    if last is not None and type(last) is not int:
        raise SourceError('Upbit last-tick storage time is malformed')
    return dict(candle=candle, close=_text_number(price), last_tick_stored_ms=last)


def _kodex_instants(day, provider):
    hours, minutes = map(int, provider['close_time_kst'].split(':'))
    known_h, known_m = map(int, provider['known_at_kst'].split(':'))
    base = datetime.combine(date.fromisoformat(day), datetime.min.time(), KST)
    at = base + timedelta(hours=hours, minutes=minutes)
    return at.astimezone(timezone.utc), (base + timedelta(hours=known_h, minutes=known_m)).astimezone(timezone.utc)


def _collect_kodex(session, item, catalog):
    provider = catalog['providers']['kodex_issuer_weekly']
    contract = provider['products'][item['fund']]
    out = {}
    for part, key, parse in (
        ('detail', 'detail_endpoint', parse_kodex_detail),
        ('history', 'history_endpoint', parse_kodex_history),
    ):
        url = provider[key].format(fid=item['fund'])
        response, retrieved_at = session.get('kodex_issuer_weekly', url)
        out[part] = dict(
            url=url,
            retrieved_at=retrieved_at,
            raw_sha256=_sha(response.body),
            raw_bytes=len(response.body),
            data=parse(response.body, contract),
        )
    return out


def _collect_aligned(session, item, catalog, target):
    provider = catalog['providers']['upbit_aligned_candles']
    candles = []
    for row in target['rows']:
        at = _time(row['at'])
        if at.minute % provider['unit_minutes'] or at.second or at.microsecond:
            raise SourceError('alignment instant is not on a candle boundary')
        query = dict(market=item['market'], count=1, to=at.strftime('%Y-%m-%dT%H:%M:%SZ'))
        url = provider['endpoint'] + '?' + urllib.parse.urlencode(query)
        response, retrieved_at = session.get('upbit_aligned_candles', url)
        candles.append(
            dict(
                at=row['at'],
                url=url,
                retrieved_at=retrieved_at,
                raw_sha256=_sha(response.body),
                candle=parse_upbit_minute(response.body, item['market'], provider['unit_minutes']),
            )
        )
    return candles


KODEX_WEEKLY_GAP = Decimal('-0.01')
KODEX_CUMULATIVE_SLACK = Decimal('0.01')
KODEX_MAX_FEE = Decimal('0.005')  # per year, far above the reviewed funds' total fees


def _check_no_paid_distribution(rows):
    """Today's policy text cannot prove the past; the history must agree too.

    A paid distribution lowers NAV against the total-return index it tracks.
    Over the live 2017-2026 KODEX 200TR sample the worst week was -0.62% and
    the mean +0.0004%, so a 1% weekly drop or a cumulative shortfall beyond
    fees plus 1% is treated as a possible distribution and the label refused.
    """
    for (day0, _p0, nav0, idx0), (day1, _p1, nav1, idx1) in zip(rows, rows[1:]):
        if number(nav1) / number(nav0) / (number(idx1) / number(idx0)) - 1 <= KODEX_WEEKLY_GAP:
            raise SourceError(f'NAV fell against its total-return index in the week to {day1}; possible distribution')
    years = Decimal((date.fromisoformat(rows[-1][0]) - date.fromisoformat(rows[0][0])).days) / Decimal('365.25')
    drift = number(rows[-1][2]) / number(rows[0][2]) / (number(rows[-1][3]) / number(rows[0][3])) - 1
    if drift < -(KODEX_MAX_FEE * years + KODEX_CUMULATIVE_SLACK):
        raise SourceError(
            'cumulative NAV shortfall against the total-return index exceeds fees; possible distributions'
        )


def _kodex_dataset(item, retained):
    contract, provider = retained['contract'], retained['provider']
    detail = retained['detail']['data']
    # The total-return label rests on the issuer's own statement, checked on
    # every acquisition: reinvested, never paid, and no distribution listed.
    if '미지급' not in detail['divid_remark'] or '재투자' not in detail['divid_remark'] or detail['divide_list']:
        raise SourceError('issuer no longer states that every distribution is reinvested; total return unverified')
    _check_no_paid_distribution(retained['history']['data'])
    retrieved = _time(retained['history']['retrieved_at'])
    rows = []
    for day, close, _nav, _index in retained['history']['data']:
        at, known_at = _kodex_instants(day, provider)
        if known_at <= retrieved:
            rows.append(dict(at=at.isoformat(), known_at=known_at.isoformat(), value=close))
    if not rows:
        raise SourceError('no published KODEX close in the history')
    dataset = dict(
        schema_version='investment-prices-v1',
        synthetic=False,
        instrument_id=contract['instrument_id'],
        asset_id=item.get('asset_id', contract['asset_id']),
        name=contract['name'],
        currency='KRW',
        unit='KRW per share',
        measure='krx_close_price_non_distributing_etf',
        source='삼성자산운용 KODEX product-earning (since inception) ' + contract['ticker'],
        calendar=provider['boundary'],
        survivorship='single_instrument',
        return_kind='total_return',
        adjustment='pit_total_return_index',
        return_basis='non_distributing_fund_price',
        return_basis_note=(
            f'발행사 상품 정보의 분배 정책 "{detail["divid_remark"].strip()}"이고 분배 내역이 비어 있다'
            f'(획득 {retained["detail"]["retrieved_at"]}). 기초지수 {contract["index"]}. {provider["tax_note"]}'
        ),
        retrieved_at=max(retrieved, _time(retained['detail']['retrieved_at'])).isoformat(),
        rows=rows,
        provenance=dict(
            method_version=VERSION,
            provider='kodex_issuer_weekly',
            fund=item['fund'],
            raw_sha256=[retained['detail']['raw_sha256'], retained['history']['raw_sha256']],
        ),
    )
    validate_dataset(dataset)
    return dataset


def _aligned_dataset(item, retained, target):
    contract, provider = retained['contract'], retained['provider']
    rows, missing = [], []
    for c in retained['candles']:
        at = _time(c['at'])
        if c['candle'] is None or _time(c['candle']['candle'] + '+00:00') != at - timedelta(
            minutes=provider['unit_minutes']
        ):
            missing.append(c['at'])  # No trade in that window; the close is not invented.
            continue
        stored_ms = c['candle']['last_tick_stored_ms']
        if stored_ms is None:
            known_at = at + UPBIT_STORE_LAG
        else:
            stored = datetime.fromtimestamp(stored_ms / 1000, timezone.utc)
            if not at - timedelta(minutes=provider['unit_minutes']) <= stored <= at + UPBIT_STORE_LAG:
                raise SourceError('Upbit last tick storage time lies outside its candle')
            known_at = max(at, stored)
        if known_at <= _time(c['retrieved_at']):
            rows.append(dict(at=c['at'], known_at=known_at.isoformat(), value=c['candle']['close']))
    if not rows:
        raise SourceError('no Upbit close at the aligned instants')
    dataset = dict(
        schema_version='investment-prices-v1',
        synthetic=False,
        instrument_id=contract['instrument_id'] + '_AT_' + item['align_to'],
        asset_id=item.get('asset_id', contract['asset_id']),
        name=contract['name'] + ' (' + target['name'] + ' 종가 시각)',
        currency='KRW',
        unit=contract['unit'],
        measure='upbit_krw_spot_close_at_aligned_instant',
        source='Upbit Open API GET /v1/candles/minutes/30 market=' + item['market'],
        calendar=provider['boundary'] + ' 시각은 ' + target['instrument_id'] + '의 종가 시각과 같다.',
        survivorship='single_instrument',
        return_kind='price',
        adjustment='unadjusted',
        return_basis='price_lower_bound',
        return_basis_note=contract['distribution_note'],
        retrieved_at=max(_time(c['retrieved_at']) for c in retained['candles']).isoformat(),
        rows=rows,
        provenance=dict(
            method_version=VERSION,
            provider='upbit_aligned_candles',
            market=item['market'],
            aligned_to=item['align_to'],
            missing_instants=missing,
        ),
    )
    validate_dataset(dataset)
    return dataset


FACTSET_MODIFIED_SLACK_DAYS = 3
_MONTHS = ('January February March April May June July August September October November December').split()


def _issue_dates(item, today):
    start = _day(item['start'], 'start')
    friday = start + timedelta(days=(4 - start.weekday()) % 7)
    dates = []
    while friday <= today:
        dates.append(friday)
        friday += timedelta(weeks=item['step_weeks'])
    return dates


def _pdf_page_one(body, max_bytes):
    from .semiconductor_data import bounded_pdf_text

    return bounded_pdf_text(body, max_bytes=max_bytes, first_page=1, last_page=1)


def _pdf_modified(body, max_bytes):
    """Latest of the PDF's creation/modification dates, or None when absent."""
    from .semiconductor_data import bounded_pdf_info

    dates = []
    for line in bounded_pdf_info(body, max_bytes=max_bytes).splitlines():
        m = re.fullmatch(r'(?:CreationDate|ModDate):\s+(\d{4}-\d{2}-\d{2})T\S*', line.strip())
        if m:
            dates.append(m.group(1))
    return max(dates) if dates else None


def parse_factset_page(text, issue, pattern):
    """Publication date and the one reviewed sentence; anything else is refused."""
    dated = None
    for line in text.splitlines():
        m = re.fullmatch(r'\s*(' + '|'.join(_MONTHS) + r') (\d{1,2}), (\d{4})\s*', line)
        if m:
            dated = date(int(m.group(3)), _MONTHS.index(m.group(1)) + 1, int(m.group(2)))
            break
    if dated != issue:
        raise SourceError('FactSet issue date differs from the requested edition')
    lines = [line for line in text.splitlines() if re.search(pattern, line)]
    values = {re.search(pattern, line).group(1) for line in lines}
    if len(values) != 1:
        raise SourceError('FactSet forward P/E sentence missing or ambiguous on page 1')
    return dict(excerpt=' '.join(lines[0].split()), value=values.pop())


def _collect_factset(session, item, catalog, today):
    provider = catalog['providers']['factset_earnings_insight']
    pattern = provider['series'][item['series']]['pattern']
    issues = []
    for friday in _issue_dates(item, today):
        record = dict(week_of=friday.isoformat(), status='absent')
        for issue in (friday, friday - timedelta(days=1)):
            url = provider['endpoint'].format(mmddyy=issue.strftime('%m%d%y'))
            response, retrieved_at = session.get('factset_earnings_insight', url, missing_ok=True)
            if response is None:
                continue
            record = dict(
                week_of=friday.isoformat(),
                issue=issue.isoformat(),
                url=url,
                retrieved_at=retrieved_at,
                raw_sha256=_sha(response.body),
                raw_bytes=len(response.body),
            )
            try:
                found = parse_factset_page(_pdf_page_one(response.body, provider['max_bytes']), issue, pattern)
                record.update(status='found', pdf_modified=_pdf_modified(response.body, provider['max_bytes']), **found)
            except SourceError as exc:
                # One unreadable edition is recorded and skipped; the rest stand.
                record.update(status='invalid', reason=str(exc))
            break
        issues.append(record)
    return issues


def _factset_features(item, retained):
    contract = retained['contract']
    rows = []
    for issue in retained['issues']:
        if issue['status'] != 'found':
            continue  # A week without a published edition is missing, never carried forward.
        day = date.fromisoformat(issue['issue'])
        retrieved = _time(issue['retrieved_at'])
        # End of the publication day in US Eastern time is at most 05:00 UTC next day.
        published = datetime.combine(day + timedelta(days=1), datetime.min.time(), timezone.utc) + timedelta(hours=5)
        modified = issue['pdf_modified']
        # A file changed well after its issue date may have been replaced at the
        # same URL; with no revision history it counts only from retrieval.
        if modified is None or date.fromisoformat(modified) > day + timedelta(days=FACTSET_MODIFIED_SLACK_DAYS):
            known_at, basis = retrieved, 'retrieval'
        else:
            known_at, basis = min(published, retrieved), 'publication'
        rows.append(
            dict(
                name=item['name'],
                value=issue['value'],
                unit=contract['unit'],
                currency='not_applicable',
                measure=contract['measure'],
                source=contract['publisher'],
                # The P/E uses that week's Wednesday close; two days before the
                # issue keeps freshness checks from looking newer than the data.
                observed_at=(day - timedelta(days=2)).isoformat() + 'T00:00:00+00:00',
                known_at=known_at.isoformat(),
                known_at_basis=basis,
                retrieved_at=issue['retrieved_at'],
                vintage=f'FactSet Earnings Insight {issue["issue"]}',
                excerpt=issue['excerpt'],
            )
        )
    if not rows:
        raise SourceError('no FactSet edition found in the requested weeks')
    return rows


def _collect_prices(session, item, catalog):
    provider = catalog['providers']['upbit_day_candles']
    start, pages, to = _day(item['start'], 'start'), [], None
    while True:
        query = dict(market=item['market'], count=provider['page_size'])
        if to:
            query['to'] = to
        url = provider['endpoint'] + '?' + urllib.parse.urlencode(query)
        response, retrieved_at = session.get('upbit_day_candles', url)
        rows = parse_upbit(response.body, item['market'])
        pages.append(
            dict(
                url=url,
                retrieved_at=retrieved_at,
                raw_sha256=_sha(response.body),
                raw_bytes=len(response.body),
                rows=rows,
            )
        )
        if len(rows) < provider['page_size'] or min(r['candle'] for r in rows) <= start.isoformat():
            return pages
        if len(pages) >= MAX_PRICE_PAGES:
            raise SourceError('Upbit pagination exceeded the reviewed page limit')
        to = min(r['candle'] for r in rows) + 'T00:00:00Z'


def _collect_vintages(session, item, catalog, today):
    provider = catalog['providers']['alfred_vintage_csv']
    vintages = []
    for vintage in _vintage_dates(item, today):
        # Never pass cosd/coed: ALFRED then mixes non-vintage values.
        url = provider['endpoint'] + '?' + urllib.parse.urlencode(dict(id=item['series'], vintage_date=vintage))
        response, retrieved_at = session.get('alfred_vintage_csv', url)
        vintages.append(
            dict(
                vintage_date=vintage.isoformat(),
                url=url,
                retrieved_at=retrieved_at,
                raw_sha256=_sha(response.body),
                raw_bytes=len(response.body),
                rows=parse_alfred(response.body, item['series'], vintage, item['window_days']),
            )
        )
    return vintages


def _price_dataset(item, retained, version=VERSION):
    contract = retained['contract']
    by_day = {}
    for page in retained['pages']:
        retrieved = _time(page['retrieved_at'])
        for r in page['rows']:
            start = _time(r['candle'] + 'T00:00:00+00:00')
            end = start + timedelta(days=1)
            if end > retrieved:
                continue  # The current candle is not closed yet.
            if r['last_tick_stored_ms'] is None:
                stored = end + UPBIT_STORE_LAG  # no storage time: dated conservatively after the close
            else:
                stored = datetime.fromtimestamp(r['last_tick_stored_ms'] / 1000, timezone.utc)
            if not start <= stored <= end + UPBIT_STORE_LAG:
                raise SourceError('Upbit last tick storage time lies outside its daily candle')
            if r['candle'] in by_day and by_day[r['candle']]['value'] != r['close']:
                raise SourceError('conflicting closes for one Upbit candle; keep both raw pages for review')
            # The close is known once the candle ends and its last tick is stored.
            known_at = max(end, stored)
            if known_at > retrieved:
                continue
            by_day[r['candle']] = dict(at=end.isoformat(), known_at=known_at.isoformat(), value=r['close'])
    rows = [by_day[d] for d in sorted(by_day) if d >= item['start']]
    if not rows:
        raise SourceError('no closed Upbit candle in the requested range')
    retrieved_at = max(_time(p['retrieved_at']) for p in retained['pages']).isoformat()
    dataset = dict(
        schema_version='investment-prices-v1',
        synthetic=False,
        instrument_id=contract['instrument_id'],
        asset_id=item.get('asset_id', contract['asset_id']),
        name=contract['name'],
        currency='KRW',
        unit=contract['unit'],
        measure=contract['measure'],
        source='Upbit Open API GET /v1/candles/days market=' + item['market'],
        calendar='24시간 거래; ' + contract['boundary'],
        survivorship='single_instrument',
        return_kind='price',
        adjustment='unadjusted',
        **(
            dict(return_basis='price_lower_bound', return_basis_note=contract['distribution_note'])
            if version != 'pit_history_v1'
            else {}
        ),
        retrieved_at=retrieved_at,
        rows=rows,
        provenance=dict(
            method_version=version,
            provider='upbit_day_candles',
            market=item['market'],
            raw_sha256=[p['raw_sha256'] for p in retained['pages']],
            revision_note=contract['revision_note'],
            distribution_note=contract['distribution_note'],
        ),
    )
    validate_dataset(dataset)
    return dataset


def _known_at_vintage(vintage, retrieved_at):
    # End of the vintage day in US Central time is at most 06:00 UTC next day.
    conservative = datetime.combine(date.fromisoformat(vintage) + timedelta(days=1), datetime.min.time(), timezone.utc)
    return min(conservative + timedelta(hours=6), _time(retrieved_at))


def _same_vintage_yoy(rows):
    """Percent change against the exact month a year earlier in the same vintage.

    Mixing a revised level with another vintage's base would invent a number
    nobody could see; a missing base month gives no value.
    """
    levels = dict(rows)
    out = []
    for observed, value in rows:
        day = date.fromisoformat(observed)
        if day.month == 2 and day.day == 29:
            continue  # No exact base date exists a year earlier.
        base = levels.get(day.replace(year=day.year - 1).isoformat())
        if base is None or number(base) == 0:
            continue
        change = (number(value) / number(base) - 1) * 100
        out.append([observed, _text_number(change.quantize(Decimal('1e-6')))])
    return out


def _vintage_features(item, retained):
    contract = retained['contract']
    yoy = item.get('transform') == 'yoy_percent'
    unit, measure = (
        ('percent', contract['measure'] + '_yoy_percent_same_vintage')
        if yoy
        else (contract['unit'], contract['measure'])
    )
    emitted, rows, seen = {}, [], set()
    for v in sorted(retained['vintages'], key=lambda v: v['vintage_date']):
        known_at = _known_at_vintage(v['vintage_date'], v['retrieved_at']).isoformat()
        present = {observed for observed, _ in v['rows']}
        start = (date.fromisoformat(v['vintage_date']) - timedelta(days=item['window_days'])).isoformat()
        withdrawn = sorted(d for d in seen if d >= start and d not in present)
        if withdrawn:
            # A feature row cannot say "no longer available"; keeping the old
            # value would show a number the later vintage withdrew.
            raise SourceError(
                f'{item["series"]} {withdrawn[0]} was withdrawn in vintage {v["vintage_date"]}; review before use'
            )
        seen |= present
        for observed, value in _same_vintage_yoy(v['rows']) if yoy else v['rows']:
            # Only new observations or revisions are new knowledge. Repeating
            # an unchanged value under a later known_at would add nothing.
            if emitted.get(observed) == value:
                continue
            emitted[observed] = value
            rows.append(
                dict(
                    name=item['name'],
                    value=value,
                    unit=unit,
                    currency=contract.get('currency', 'not_applicable'),
                    measure=measure,
                    source=f'ALFRED {item["series"]} ({contract["publisher"]})',
                    observed_at=observed + 'T00:00:00+00:00',
                    known_at=known_at,
                    retrieved_at=v['retrieved_at'],
                    vintage=f'ALFRED:{item["series"]}:{v["vintage_date"]}',
                )
            )
    return rows


def _derived_features(item, dataset):
    rows = dataset['rows']
    times = [_time(r['at']) for r in rows]
    instrument = dataset['instrument_id']
    if item['kind'] == 'trailing_return':
        measure = f'trailing_{item["days"]}d_price_return:{instrument}'
    else:
        measure = f'close_to_sma_{item["observations"]}obs:{instrument}'
    if dataset['provenance']['method_version'] == 'pit_history_v1' or len(times) < 2:
        step = timedelta(days=1)  # v1 rule: daily 24-hour series
    else:
        step = median(b - a for a, b in zip(times, times[1:]))
    out = []
    for i, r in enumerate(rows):
        if item['kind'] == 'trailing_return':
            target = times[i] - timedelta(days=item['days'])
            j = bisect_right(times, target) - 1
            if j < 0 or target - times[j] > timedelta(days=DERIVED_GAP_DAYS):
                continue  # No base observation close enough; never fill a gap.
            used = [rows[j], r]
            value = number(r['value']) / number(rows[j]['value']) - 1
        else:
            n = item['observations']
            # n observations at the series' usual spacing span (n-1) steps; a
            # longer span means missing rows inside the average, refused.
            if i + 1 < n or times[i] - times[i + 1 - n] > (n - 1) * step + timedelta(days=DERIVED_GAP_DAYS):
                continue
            used = rows[i + 1 - n : i + 1]
            value = number(r['value']) / (sum((number(x['value']) for x in used), Decimal(0)) / n) - 1
        out.append(
            dict(
                name=item['name'],
                value=_text_number(value.quantize(Decimal('1e-12'))),
                unit='ratio',
                currency='not_applicable',
                measure=measure,
                source=f'derived {dataset["provenance"]["method_version"]} from {dataset["source"]}',
                observed_at=r['at'],
                known_at=max(_time(x['known_at']) for x in used).isoformat(),
                retrieved_at=dataset['retrieved_at'],
                vintage=f'derived:{instrument}:{r["at"]}',
            )
        )
    return out


def _gaps(rows, version):
    days = [_time(r['at']).date() for r in rows]
    if version == 'pit_history_v1':
        return [
            dict(after=a.isoformat(), before=b.isoformat(), missing_days=(b - a).days - 1)
            for a, b in zip(days, days[1:])
            if (b - a).days > 1
        ]
    # Gaps are counted in the series' own steps (days or weeks), not days.
    step = median((b - a).days for a, b in zip(days, days[1:])) if len(days) > 1 else 1
    gaps = []
    for a, b in zip(days, days[1:]):
        missing = round((b - a).days / step) - 1
        if missing > 0:
            gaps.append(dict(after=a.isoformat(), before=b.isoformat(), missing_rows=missing))
    return gaps


def _build_price(item, retained, prices, version):
    if item['provider'] == 'upbit_day_candles':
        return _price_dataset(item, retained, version)
    if item['provider'] == 'kodex_issuer_weekly':
        return _kodex_dataset(item, retained)
    if item['align_to'] not in prices:
        raise SourceError('aligned series unavailable: ' + item['align_to'])
    return _aligned_dataset(item, retained, prices[item['align_to']])


def build(spec, snapshots):
    """Offline and deterministic: the same retained snapshots give the same history."""
    version = snapshots['method_version']
    retained = snapshots['items']
    prices, features, failures = {}, {}, list(snapshots['failures'])
    for item in spec.get('prices', []):
        key = _price_key(item)
        if key not in retained:
            continue
        try:
            dataset = _build_price(item, retained[key], prices, version)
        except (SourceError, KeyError, TypeError, ValueError, InvalidOperation) as exc:
            failures.append(dict(item=key, stage='build', reason=str(exc)))
            continue
        prices[dataset['instrument_id']] = dataset
    for item in spec.get('features', []):
        key = 'features:' + item['name']
        try:
            if item['provider'] == 'price_derived':
                if item['instrument_id'] not in prices:
                    failures.append(dict(item=key, stage='build', reason='source price series unavailable'))
                    continue
                features[item['name']] = _derived_features(item, prices[item['instrument_id']])
            elif key in retained and item['provider'] == 'factset_earnings_insight':
                features[item['name']] = _factset_features(item, retained[key])
            elif key in retained:
                features[item['name']] = _vintage_features(item, retained[key])
        except (SourceError, KeyError, TypeError, ValueError, InvalidOperation) as exc:
            failures.append(dict(item=key, stage='build', reason=str(exc)))
    summary = dict(
        prices=[
            dict(
                instrument_id=d['instrument_id'],
                name=d['name'],
                rows=len(d['rows']),
                first=d['rows'][0]['at'],
                last=d['rows'][-1]['at'],
                last_value=d['rows'][-1]['value'],
                unit=d['unit'],
                gaps=_gaps(d['rows'], version),
            )
            for d in prices.values()
        ],
        features=[
            dict(
                name=name,
                rows=len(rows),
                revisions=len(rows) - len({r['observed_at'] for r in rows}),
                latest=max(rows, key=lambda r: (r['observed_at'], r['known_at'])) if rows else None,
            )
            for name, rows in features.items()
        ],
    )
    return dict(
        schema_version='investment-history-v1',
        method_version=version,
        synthetic=False,
        spec_sha256=digest(spec),
        prices=prices,
        features=features,
        summary=summary,
        failures=failures,
        limitations=LIMITATIONS[version]
        + [
            'ALFRED 관측값의 known_at은 표본으로 고른 판본일 기준이다. 실제 공표보다 늦을 수는 있어도 이르지 않다.',
            CURRENT_EVIDENCE[version],
            '빈 날짜와 결측값은 채우지 않았다. 지표 계산에 필요한 관측이 없으면 그 시점의 값을 만들지 않았다.',
        ],
    )


LIMITATIONS = {
    'pit_history_v1': [
        '거래소 가격은 가격 수익이며 하드포크·에어드롭·스테이킹을 포함한 총수익이 아니다. 매수 승인 검증에는 그대로 쓸 수 없다.'
    ],
    'pit_history_v2': [
        '코인 가격은 현금 분배가 없는 자산의 가격 수익이다. 확인하지 못한 포크·에어드롭과 스테이킹은 빠졌으므로 보유자 수익의 '
        '하한(price_lower_bound)으로 표시한다.',
        'KODEX TR ETF 종가는 발행사가 분배금을 지급하지 않고 재투자한다고 밝힌 상품의 세전 총수익이다. 이 진술은 수집할 때마다 '
        '다시 확인하며, 바뀌면 총수익으로 표시하지 않는다.',
    ],
}
CURRENT_EVIDENCE = {
    'pit_history_v1': '이력 자료는 현재 판단의 검증 원문을 대신하지 않는다. 오늘의 숫자는 조사 실행의 검증 근거와 연결해야 한다.',
    'pit_history_v2': '이 이력은 invest run --history로 오프라인 재현 검증을 거친 뒤, 판단 시각 이전에 받은 최신 행만 현재 근거가 된다. '
    '계획에 직접 적은 숫자는 현재 근거가 아니다.',
}
DATE_NOTES = {
    'pit_history_v1': '날짜는 종가 시각(UTC 00:00 = 한국시간 09:00)이다. 예를 들어 10월 21일 캔들의 종가는 10월 22일 00:00 UTC 값이다.',
    'pit_history_v2': '날짜는 종가 시각(UTC)이다. Upbit 일 캔들은 UTC 00:00(한국시간 09:00), KRX 종가와 그 시각에 맞춘 Upbit 값은 '
    'UTC 06:30(한국시간 15:30)이다.',
}


def render_history(result):
    lines = ['# 장기 시점 이력 수집 결과', '']
    lines.append(
        '투자 판단이 아니라 검증에 쓸 원자료 묶음이다. 각 값은 당시 알 수 있었던 시각(known_at)과 함께 저장했다.'
    )
    lines += ['', '## 가격 이력', '']
    lines.append(DATE_NOTES[result['method_version']])
    lines.append('')
    if not result['summary']['prices']:
        lines.append('- 수집한 가격 이력이 없다.')
    v1 = result['method_version'] == 'pit_history_v1'
    for p in result['summary']['prices']:
        gaps = sum(g['missing_days' if v1 else 'missing_rows'] for g in p['gaps'])
        lines.append(
            f'- **{p["name"]}** (`{p["instrument_id"]}`): {p["rows"]}개 {"일별 " if result["method_version"] == "pit_history_v1" else ""}종가, '
            f'{p["first"][:10]} ~ {p["last"][:10]}, 마지막 값 {p["last_value"]} {p["unit"]}. '
            + (
                (f'빠진 날 {gaps}일은 채우지 않았다.' if gaps else '빠진 날 없음.')
                if v1
                else (f'평소 간격 기준으로 빠진 표본 {gaps}개는 채우지 않았다.' if gaps else '빠진 표본 없음.')
            )
        )
    lines += ['', '## 특징값 이력', '']
    if not result['summary']['features']:
        lines.append('- 수집한 특징값이 없다.')
    for f in result['summary']['features']:
        latest = f['latest']
        tail = (
            f'최신 관측 {latest["observed_at"][:10]} = {latest["value"]} {latest["unit"]} (알 수 있었던 시각 {latest["known_at"]})'
            if latest
            else '값 없음'
        )
        lines.append(f'- **{f["name"]}**: {f["rows"]}행, 이후 판본에서 고쳐진 값 {f["revisions"]}건. {tail}.')
    if result['failures']:
        lines += ['', '## 수집·검증 실패', '']
        lines += [f'- `{x["item"]}` ({x["stage"]}): {x["reason"]}' for x in result['failures']]
    lines += ['', '## 한계', '']
    lines += ['- ' + x for x in result['limitations']]
    lines += [
        '',
        '## 사용 방법',
        '',
        '`history.json`의 `prices`와 `features`를 투자 계획 후보의 `prices`/`benchmark`/`features`에 넣는다. '
        '비교 시장(benchmark)은 같은 통화·수익 정의의 별도 상품이어야 한다.',
        '',
    ]
    return '\n'.join(lines)


def _acquire_price(session, item, catalog, built):
    providers = catalog['providers']
    if item['provider'] == 'upbit_day_candles':
        market = providers['upbit_day_candles']['markets'][item['market']]
        contract = dict(
            market,
            boundary=providers['upbit_day_candles']['boundary'],
            revision_note=providers['upbit_day_candles']['revision_note'],
        )
        return dict(contract=contract, pages=_collect_prices(session, item, catalog))
    if item['provider'] == 'kodex_issuer_weekly':
        provider = providers['kodex_issuer_weekly']
        retained = dict(
            contract=provider['products'][item['fund']],
            provider={k: provider[k] for k in ('close_time_kst', 'known_at_kst', 'boundary', 'tax_note')},
        )
        return dict(retained, **_collect_kodex(session, item, catalog))
    if item['align_to'] not in built:
        raise SourceError('aligned series unavailable: ' + item['align_to'])
    provider = providers['upbit_aligned_candles']
    return dict(
        contract=providers['upbit_day_candles']['markets'][item['market']],
        provider={k: provider[k] for k in ('unit_minutes', 'boundary')},
        candles=_collect_aligned(session, item, catalog, built[item['align_to']]),
    )


def acquire_history(spec, directory, *, fetcher=None, clock=None, sleep=None, progress=None, catalog=None):
    catalog = catalog or load_catalog()
    clock = clock or (lambda: datetime.now(timezone.utc))
    today = clock().astimezone(timezone.utc).date()
    validate_spec(spec, catalog, today)
    root = Path(directory)
    if root.exists():
        raise SourceError('use a new history output directory')
    session = _Session(catalog, fetcher, clock, sleep or time.sleep, progress)
    items, failures = {}, []
    errors = (SourceError, OSError, TimeoutError, ValueError)
    built = {}
    for item in spec.get('prices', []):
        key = _price_key(item)
        try:
            items[key] = _acquire_price(session, item, catalog, built)
        except errors as exc:
            failures.append(dict(item=key, stage='acquire', reason=str(exc) or type(exc).__name__))
            continue
        try:
            built[instrument_id(item, catalog)] = _build_price(item, items[key], built, VERSION)
        except errors:
            pass  # build() below records the same failure deterministically
    for item in spec.get('features', []):
        if item['provider'] not in ('alfred_vintage_csv', 'factset_earnings_insight'):
            continue
        key = 'features:' + item['name']
        contract = catalog['providers'][item['provider']]['series'][item['series']]
        try:
            if item['provider'] == 'alfred_vintage_csv':
                items[key] = dict(contract=contract, vintages=_collect_vintages(session, item, catalog, today))
            else:
                items[key] = dict(contract=contract, issues=_collect_factset(session, item, catalog, today))
        except errors as exc:
            failures.append(dict(item=key, stage='acquire', reason=str(exc) or type(exc).__name__))
    snapshots = dict(
        schema_version='history-snapshots-v1',
        method_version=VERSION,
        retention='관측창 행과 원문 SHA-256만 보존한다. 개인 연구 재현용이며 재배포하지 않는다.',
        policies=session.policies,
        items=items,
        failures=failures,
    )
    result = build(spec, snapshots)
    root.mkdir(parents=True)
    save(root / 'spec.json', spec)
    save(root / 'snapshots.json', snapshots)
    save(root / 'history.json', result)
    (root / 'history.md').write_text(render_history(result), encoding='utf-8')
    save(root / 'history_manifest.json', dict(method_version=VERSION, artifacts=_hashes(root)))
    return result


def _hashes(root):
    return {name: _sha((root / name).read_bytes()) for name in ARTIFACTS}


def replay_history(directory):
    """Rebuild the history from retained rows without network and compare every artifact."""
    root = Path(directory)
    manifest = load(root / 'history_manifest.json')
    if manifest.get('method_version') not in VERSIONS:
        raise SourceError('unsupported history replay version')
    if set(manifest['artifacts']) != set(ARTIFACTS) or manifest['artifacts'] != _hashes(root):
        raise SourceError('history artifact checksum mismatch')
    spec, snapshots = load(root / 'spec.json'), load(root / 'snapshots.json')
    if snapshots.get('method_version') != manifest['method_version']:
        raise SourceError('history snapshot and manifest versions differ')
    result = build(spec, snapshots)
    if encode(result) != encode(load(root / 'history.json')) or render_history(result) != (
        root / 'history.md'
    ).read_text(encoding='utf-8'):
        raise SourceError('history replay differs')
    return result
