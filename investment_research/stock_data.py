"""Bounded acquisition and strict parsing of public stock price/quote JSON.

Only the reviewed hosts in ``catalog/stock_universe.json`` are requested. Each
request goes through ``sources.read_public`` (HTTPS, public address, robots.txt,
no redirects, 2 MiB cap). Raw bodies are kept byte-for-byte in the run
directory so the same picks can be replayed offline. Provider numbers are
parsed into Decimal; missing or malformed values stay ``None`` and are never
replaced by zero or by another provider's value.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import threading

from .sources import SourceError, _fetch_http, read_public

VERSION = 'stock_public_json_v1'
CHART = 'https://api.stock.naver.com/chart/{kind}/{group}/{code}/month?startDateTime=200001010000&endDateTime={end}2359'
KR_QUOTES = 'https://polling.finance.naver.com/api/realtime?query=SERVICE_ITEM:{codes}'
US_BASIC = 'https://api.stock.naver.com/stock/{code}/basic'
FX = 'https://api.stock.naver.com/marketindex/exchange/FX_USDKRW/prices?page=1&pageSize=10'
MAX_REQUESTS = 300
KR_BATCH = 25


def universe():
    data = json.loads((Path(__file__).parent / 'catalog' / 'stock_universe.json').read_text(encoding='utf-8'))
    if data.get('schema_version') != 'stock-universe-v1':
        raise SourceError('stock universe: unsupported schema')
    seen = set()
    for market, cfg in data['markets'].items():
        for code, name, sector in cfg['stocks']:
            if (market, code) in seen or not re.fullmatch(r'[0-9A-Za-z.]{1,12}', code):
                raise SourceError('stock universe: duplicate or invalid code ' + code)
            seen.add((market, code))
    return data


def plan_requests(data, markets, as_of):
    """Deterministic request list; nothing is fetched here."""
    end = as_of.astimezone(timezone.utc).strftime('%Y%m%d')
    out = []
    for market in markets:
        cfg = data['markets'][market]
        kind = cfg['chart_kind']
        bench = cfg['benchmark']['code']
        out.append(dict(id=f'index_{market}', role='index', market=market, code=bench,
                        url=CHART.format(kind=kind, group='index', code=bench, end=end)))
        for code, _, _ in cfg['stocks']:
            out.append(dict(id=f'chart_{market}_{_safe(code)}', role='chart', market=market, code=code,
                            url=CHART.format(kind=kind, group='item', code=code, end=end)))
        if market == 'KR':
            codes = [c for c, _, _ in cfg['stocks']]
            for i in range(0, len(codes), KR_BATCH):
                batch = codes[i:i + KR_BATCH]
                out.append(dict(id=f'quote_KR_{i // KR_BATCH + 1}', role='kr_quotes', market=market,
                                code=','.join(batch), url=KR_QUOTES.format(codes=','.join(batch))))
        else:
            for code, _, _ in cfg['stocks']:
                out.append(dict(id=f'basic_{market}_{_safe(code)}', role='us_basic', market=market, code=code,
                                url=US_BASIC.format(code=code)))
    if 'US' in markets:
        out.append(dict(id='fx_USDKRW', role='fx', market='US', code='FX_USDKRW', url=FX))
    if len(out) > MAX_REQUESTS:
        raise SourceError('stock picks: planned requests exceed the bounded limit')
    return out


def _safe(code):
    return code.replace('.', '_')


class _RobotsCache:
    """Reuse one robots.txt answer per host within a run (fewer requests)."""

    def __init__(self, base):
        self.base, self.cache, self.lock, self.requests = base, {}, threading.Lock(), 0

    def __call__(self, url, timeout, limit):
        robots = url.endswith('/robots.txt')
        if robots:
            with self.lock:
                if url in self.cache:
                    return self.cache[url]
        result = self.base(url, timeout, limit)
        with self.lock:
            self.requests += 1
            if robots:
                self.cache[url] = result
        return result


def acquire(requests, run_dir, policy, *, fetcher=None, now=None, workers=6, progress=None):
    """Fetch each planned URL once; failures are recorded, never filled."""
    raw = Path(run_dir) / 'raw'
    raw.mkdir(parents=True, exist_ok=False)
    perform = _RobotsCache(fetcher or _fetch_http)

    def one(spec):
        doc = read_public(spec['url'], access_method='public_http', policy_url=policy['policy_url'],
                          policy_note=policy['policy_note'], fetcher=perform, now=now)
        record = dict(spec, status=doc.status, retrieved_at=doc.retrieved_at,
                      robots=doc.policy.get('robots'), diagnostics=list(doc.diagnostics),
                      http_status=None, content_type=None, sha256=None, bytes=None)
        if doc.response is not None:
            record.update(http_status=doc.response.status, content_type=doc.response.content_type)
            if doc.status == 'available':
                body = doc.response.body
                (raw / (spec['id'] + '.body')).write_bytes(body)
                record.update(sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))
        return record

    # Warm the robots cache host by host so parallel workers do not race it.
    hosts, ordered = set(), []
    for spec in requests:
        host = spec['url'].split('/')[2]
        (ordered.insert(0, spec) if host not in hosts else ordered.append(spec))
        hosts.add(host)
    first = [s for s in ordered[:len(hosts)]]
    records = [one(s) for s in first]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        records += list(pool.map(one, ordered[len(hosts):]))
    if progress:
        progress(f'{sum(r["status"] == "available" for r in records)}/{len(records)}개 자료 확보')
    by_id = {r['id']: r for r in records}
    return [by_id[s['id']] for s in requests], perform.requests


def load_bodies(run_dir, records):
    """Verify every stored body against its recorded hash before reuse."""
    bodies = {}
    for r in records:
        if r.get('sha256') is None:
            continue
        body = (Path(run_dir) / 'raw' / (r['id'] + '.body')).read_bytes()
        if hashlib.sha256(body).hexdigest() != r['sha256']:
            raise SourceError('stored stock response hash mismatch: ' + r['id'])
        bodies[r['id']] = body
    return bodies


# ---------------------------------------------------------------- parsing

def _json(body, encoding='utf-8'):
    try:
        return json.loads(body.decode(encoding), parse_float=Decimal, parse_int=Decimal)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SourceError('provider response is not valid JSON') from exc


def _positive(value):
    if isinstance(value, Decimal) and value.is_finite() and value > 0:
        return value
    return None


def parse_chart(body, issues=None):
    """Monthly bars: month -> (first open or None, last close).

    Bad observations are quarantined individually (Source Anomaly Guard
    style) instead of discarding a 25-year series: a non-positive close drops
    that month, a non-positive open keeps the close for signals but blocks the
    month as an entry/exit price, and two different bars for one month drop
    that month. Nothing is filled with zero or a neighbouring value.
    """
    issues = [] if issues is None else issues
    rows = _json(body)
    if not isinstance(rows, list):
        raise SourceError('chart: list of monthly bars required')
    bars, conflicts = {}, set()
    for row in rows:
        if not isinstance(row, dict) or not re.fullmatch(r'\d{8}', str(row.get('localDate', ''))):
            raise SourceError('chart: each bar needs an 8-digit localDate')
        month = row['localDate'][:4] + '-' + row['localDate'][4:6]
        open_, close = _positive(row.get('openPrice')), _positive(row.get('closePrice'))
        if close is None:
            issues.append(month + ': 종가가 없거나 0 이하라 이 달을 격리')
            continue
        if open_ is None:
            issues.append(month + ': 시가가 없거나 0 이하라 이 달 매수·매도 계산에서 제외')
        if month in bars:
            if bars[month] != (open_, close):
                conflicts.add(month)
            continue
        bars[month] = (open_, close)
    for month in sorted(conflicts):
        del bars[month]
        issues.append(month + ': 같은 달에 서로 다른 월봉 두 개(조정/미조정 혼재 가능)라 이 달을 격리')
    return dict(sorted(bars.items()))


def _number(text):
    if isinstance(text, Decimal):
        return text if text.is_finite() else None
    if not isinstance(text, str):
        return None
    cleaned = re.sub(r'[,\s]|배|%|USD|원', '', text)
    if not re.fullmatch(r'-?\d+(?:\.\d+)?', cleaned):
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _poll_time(stamp):
    """Provider sends either KST 'YYYYMMDDHHMMSS' or epoch milliseconds."""
    text = str(stamp)
    if re.fullmatch(r'\d{14}', text):
        return datetime.strptime(text, '%Y%m%d%H%M%S').isoformat() + '+09:00'
    if re.fullmatch(r'\d{13}', text):
        return datetime.fromtimestamp(int(text) / 1000, timezone.utc).isoformat()
    raise SourceError('kr quotes: unknown observation time format')


def parse_kr_quotes(body):
    """Domestic quote fields; EPS definitions are provider-labelled, not audited."""
    data = _json(body, 'cp949')
    try:
        rows = data['result']['areas'][0]['datas']
        stamp = data['result']['time']
    except (KeyError, IndexError, TypeError) as exc:
        raise SourceError('kr quotes: unexpected structure') from exc
    observed = _poll_time(stamp)
    out = {}
    for row in rows:
        code = str(row.get('cd', ''))
        if not re.fullmatch(r'\d{6}', code):
            raise SourceError('kr quotes: invalid code')
        out[code] = dict(price=_positive(row.get('nv')), eps=_number(row.get('eps')),
                         bps=_number(row.get('bps')), consensus_eps=_number(row.get('cnsEps')),
                         dividend=_number(row.get('dv')), shares=_positive(row.get('countOfListedStock')),
                         high_52w=_positive(row.get('highPriceOf52Weeks')),
                         low_52w=_positive(row.get('lowPriceOf52Weeks')),
                         observed_at=observed, currency='KRW')
    return out


def parse_us_basic(body):
    data = _json(body)
    if not isinstance(data, dict):
        raise SourceError('us basic: object required')
    infos = {}
    for item in data.get('stockItemTotalInfos') or []:
        if isinstance(item, dict) and isinstance(item.get('code'), str):
            infos[item['code']] = (_number(item.get('value')), item.get('keyDesc'))
    industry = (data.get('industryCodeType') or {}).get('industryGroupKor')
    def info(key):
        return infos.get(key, (None, None))
    return dict(price=_positive(_number(data.get('closePriceRaw'))), traded_at=data.get('localTradedAt'),
                per=info('per')[0], per_period=info('per')[1], eps=info('eps')[0],
                pbr=info('pbr')[0], dividend_yield=info('dividendYieldRatio')[0],
                high_52w=_positive(info('highPriceOf52Weeks')[0]), low_52w=_positive(info('lowPriceOf52Weeks')[0]),
                market_cap_krw=_positive(_number(data.get('marketValueKrwRaw'))),
                industry=industry if isinstance(industry, str) else None, currency='USD')


def parse_fx(body):
    rows = _json(body)
    if not isinstance(rows, list) or not rows:
        raise SourceError('fx: list required')
    dated = []
    for row in rows:
        day, value = row.get('localTradedAt'), _positive(_number(row.get('closePrice')))
        if isinstance(day, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', day) and value is not None:
            dated.append((day, value))
    if not dated:
        raise SourceError('fx: no dated positive close')
    return max(dated)


def parse_all(data, records, bodies):
    """Parse every available body; a parse failure becomes a recorded gap."""
    charts, indices, quotes, gaps, fx, issues = {}, {}, {}, [], None, []
    for r in records:
        if r['id'] not in bodies:
            gaps.append(dict(id=r['id'], market=r['market'], code=r['code'], role=r['role'],
                             reason=(r['diagnostics'] or [r['status']])[0]))
            continue
        try:
            body = bodies[r['id']]
            if r['role'] in ('chart', 'index'):
                found = []
                bars = parse_chart(body, found)
                issues += [dict(market=r['market'], code=r['code'], issue=i) for i in found]
                if not bars:
                    raise SourceError('provider returned no monthly bars (상장폐지·비상장 전환 가능)')
                (indices if r['role'] == 'index' else charts.setdefault(r['market'], {}))[
                    r['market'] if r['role'] == 'index' else r['code']] = bars
            elif r['role'] == 'kr_quotes':
                quotes.setdefault('KR', {}).update(parse_kr_quotes(body))
            elif r['role'] == 'us_basic':
                quotes.setdefault('US', {})[r['code']] = parse_us_basic(body)
            elif r['role'] == 'fx':
                fx = parse_fx(body)
        except SourceError as exc:
            gaps.append(dict(id=r['id'], market=r['market'], code=r['code'], role=r['role'], reason=str(exc)))
    return dict(charts=charts, indices=indices, quotes=quotes, fx=fx, gaps=gaps, data_issues=issues)
