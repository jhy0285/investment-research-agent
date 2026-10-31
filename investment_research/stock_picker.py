"""Stock picks: acquire -> rank -> backtest -> grade -> size -> report -> journal.

Every run writes a new directory with the raw provider bodies, parsed results,
the journal entries that were visible at the time, and hashes. ``replay_picks``
recomputes from those files without network access and checks the report bytes.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

from . import stock_data as data_mod
from . import stock_model as model
from .sources import SourceError

VERSION = 'stock_picks_run_v1'
MARKETS = ('KR', 'US')
DEFAULT_BUDGET = 10_000_000


def parse_question(question):
    """Markets and example budget from a natural-language stock-pick request."""
    text = question or ''
    kr = bool(re.search(r'한국|국내|코스피|kospi|국장', text, re.I))
    us = bool(re.search(r'미국|해외|나스닥|s&p|미장|\bus\b|뉴욕', text, re.I))
    markets = ('KR',) if kr and not us else ('US',) if us and not kr else MARKETS
    budget = DEFAULT_BUDGET
    match = re.search(r'(\d[\d,]*(?:\.\d+)?)\s*(억|천만|백만|만)\s*원?', text)
    if match:
        unit = {'억': 100_000_000, '천만': 10_000_000, '백만': 1_000_000, '만': 10_000}[match.group(2)]
        budget = int(Decimal(match.group(1).replace(',', '')) * unit)
    return markets, budget


def resolve_watch(universe, items):
    """Map codes or exact universe names to (market, code); unknown items are reported."""
    lookup = {}
    for market, cfg in universe['markets'].items():
        for code, name, _ in cfg['stocks']:
            for key in (code.lower(), name.lower(), code.split('.')[0].lower()):
                lookup.setdefault(key, (market, code))
    found, unknown = [], []
    for item in items:
        key = item.strip().lower()
        if not key:
            continue
        (found.append(lookup[key]) if key in lookup else unknown.append(item.strip()))
    return list(dict.fromkeys(found)), unknown


def watch_from_question(universe, question):
    """Universe names written in the question (e.g. 삼성전자, SK하이닉스, 하이닉스)."""
    text = (question or '').lower().replace(' ', '')
    out = []
    for market, cfg in universe['markets'].items():
        for code, name, _ in cfg['stocks']:
            aliases = {name.lower().replace(' ', '')}
            if name.startswith('SK') and len(name) > 4:
                aliases.add(name[2:].lower())
            if any(len(a) >= 2 and a in text for a in aliases):
                out.append((market, code))
    return out


def is_stock_pick_question(question):
    if re.search(r'비중|배분|포트폴리오|비율|리밸런', question or ''):
        return False
    return bool(re.search(r'(?:종목|주식|개별주)\S{0,4}\s*\S{0,6}\s*(?:추천|골라|뽑아|찍어)|'
                          r'(?:추천|유망|살\s*만한|사\s*볼\s*만한|살만한|매수할\s*만한)\s*(?:종목|주식)|'
                          r'stock\s*picks?|recommend\s+(?:some\s+)?stocks', question or '', re.I))


def _code_digest():
    h = hashlib.sha256()
    root = Path(__file__).parent
    for name in ('stock_data.py', 'stock_model.py', 'stock_picker.py', 'stock_report.py', 'sources.py',
                 'catalog/stock_universe.json'):
        h.update(name.encode() + b'\0' + (root / name).read_bytes() + b'\0')
    return h.hexdigest()


def jsonable(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return value


def _dump(path, value):
    text = json.dumps(jsonable(value), ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    Path(path).write_text(text, encoding='utf-8')
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


# ------------------------------------------------------------------ journal

def load_journal(root):
    folder = Path(root) / 'stock_picks'
    entries = []
    if folder.exists():
        for path in sorted(folder.glob('*/*.json')):
            entry = json.loads(path.read_text(encoding='utf-8'))
            if entry.get('schema_version') == 'stock-pick-journal-v1':
                entries.append(entry)
    return sorted(entries, key=lambda e: (e['market'], e['signal_month'], e['recorded_at']))


def record_journal(root, result):
    """Immutable: one file per (market, signal month, picks, model); never rewritten."""
    written = []
    for market, m in result['markets'].items():
        if m.get('signal_month') is None:
            continue
        key = dict(market=market, signal_month=m['signal_month'], picks=m['picks'], model=model.VERSION)
        digest = hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()[:16]
        path = Path(root) / 'stock_picks' / market / f"{m['signal_month']}_{digest}.json"
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = dict(key, schema_version='stock-pick-journal-v1', recorded_at=result['as_of'],
                     grade=m['grade']['grade'], run_id=result['run_id'],
                     reference_prices={c: m['prices'].get(c) for c in m['picks']})
        path.write_text(json.dumps(jsonable(entry), ensure_ascii=False, indent=2, sort_keys=True) + '\n',
                        encoding='utf-8')
        written.append(str(path))
    return written


# ------------------------------------------------------------------ compute

def compute(universe, markets, budget, as_of, records, bodies, journal_entries, run_id, watch=()):
    parsed = data_mod.parse_all(universe, records, bodies)
    out = dict(schema_version='stock-picks-v1', version=VERSION, model_version=model.VERSION,
               policy_version=model.POLICY_VERSION, run_id=run_id, as_of=as_of.isoformat(),
               watch=[list(w) for w in watch if w[0] in markets],
               budget_krw=budget, params=model.PARAMS, gaps=parsed['gaps'], fx=parsed['fx'],
               data_issues=parsed['data_issues'],
               markets={}, requests=len(records),
               available=sum(1 for r in records if r['id'] in bodies))
    series_by_market, index_by_market, bt_by_market = {}, {}, {}
    for market in markets:
        cfg = universe['markets'][market]
        names = {c: n for c, n, _ in cfg['stocks']}
        sectors = {c: s for c, _, s in cfg['stocks']}
        series = parsed['charts'].get(market, {})
        index = parsed['indices'].get(market)
        last = model.last_complete_month(as_of, cfg['timezone'], cfg['close_time'])
        m = dict(name=cfg['name'], currency=cfg['currency'], benchmark=cfg['benchmark'], cost_bps=cfg['cost_bps_per_side'],
                 cost_note=cfg['cost_note'], last_complete_month=last, names=names, sectors=sectors,
                 universe_size=len(cfg['stocks']), with_history=len(series), signal_month=None, picks=[])
        if index is None or len(series) < model.PARAMS['min_eligible']:
            m.update(grade=dict(grade='D', status='자료 부족', reasons=['지수 또는 종목 가격 이력을 충분히 확보하지 못했다.'], caps=[]))
            out['markets'][market] = m
            continue
        bt = model.backtest(series, index, sectors, last, cfg['cost_bps_per_side'])
        evaluation = model.evaluate(bt)
        series_by_market[market], index_by_market[market], bt_by_market[market] = series, index, bt
        current = bt['signals'].get(last)
        quotes = parsed['quotes'].get(market, {})
        m.update(backtest=evaluation, monthly=bt['months'])
        if current is not None:
            m.update(signal_month=last, picks=current['picks'], ranking=current['rows'], eligible=current['eligible'])
        m['extreme'] = {c: [mo for mo in (model.shift(last, -k) for k in range(12))
                            if mo in series.get(c, {}) and model.shift(mo, -1) in series[c]
                            and abs(series[c][mo][1] / series[c][model.shift(mo, -1)][1] - 1) >= Decimal('0.5')]
                        for c in names}
        prices, valuation = {}, {}
        for code in names:
            q = quotes.get(code) or {}
            price = q.get('price')
            prices[code] = price
            if market == 'KR':
                per = price / q['eps'] if price and q.get('eps') and q['eps'] > 0 else None
                pbr = price / q['bps'] if price and q.get('bps') and q['bps'] > 0 else None
                forward = price / q['consensus_eps'] if price and q.get('consensus_eps') and q['consensus_eps'] > 0 else None
                dividend = q['dividend'] / price * 100 if price and q.get('dividend') is not None else None
                valuation[code] = dict(per=per, pbr=pbr, consensus_multiple=forward, dividend_yield=dividend,
                                       eps_negative=bool(q.get('eps') is not None and q['eps'] <= 0),
                                       high_52w=q.get('high_52w'), observed_at=q.get('observed_at'))
            else:
                valuation[code] = dict(per=q.get('per') if q.get('per') and q['per'] > 0 else None,
                                       per_period=q.get('per_period'), pbr=q.get('pbr'),
                                       dividend_yield=q.get('dividend_yield'), consensus_multiple=None,
                                       eps_negative=bool(q.get('eps') is not None and q['eps'] <= 0),
                                       high_52w=q.get('high_52w'), observed_at=q.get('traded_at'),
                                       industry=q.get('industry'))
        pers = sorted(v['per'] for v in valuation.values() if v['per'] is not None)
        m.update(prices=prices, valuation=valuation,
                 median_per=pers[len(pers) // 2] if pers else None)
        out['markets'][market] = m
    evaluated = model.evaluate_journal(journal_entries, bt_by_market, series_by_market, index_by_market)
    out['journal'] = evaluated
    for market, m in out['markets'].items():
        if 'backtest' not in m:
            continue
        live = model.live_summary(evaluated, market)
        m['live'] = live
        m['grade'] = model.grade(m['backtest'], live)
        earlier = [e for e in journal_entries if e['market'] == market and e['signal_month'] < (m['signal_month'] or '')]
        if earlier:
            last_entry = max(earlier, key=lambda e: (e['signal_month'], e['recorded_at']))
            m['previous'] = dict(signal_month=last_entry['signal_month'], picks=last_entry['picks'],
                                 kept=[c for c in m['picks'] if c in last_entry['picks']],
                                 added=[c for c in m['picks'] if c not in last_entry['picks']],
                                 removed=[c for c in last_entry['picks'] if c not in m['picks']])
    picks = {mk: m['picks'] for mk, m in out['markets'].items()}
    grades = {mk: m['grade'] for mk, m in out['markets'].items()}
    prices = {(mk, c): m.get('prices', {}).get(c) for mk, m in out['markets'].items() for c in m['picks']}
    fx = parsed['fx'][1] if parsed['fx'] else None
    out['allocation'] = model.allocate(picks, grades, prices, budget, fx)
    return out


def _new_run_dir(root):
    if root.exists():
        raise SourceError('run directory already exists; use a new path')
    return root


def run_picks(run_dir, *, markets=MARKETS, budget=DEFAULT_BUDGET, journal=None, question=None,
              watch=(), fetcher=None, now=None, progress=None):
    from .stock_report import render
    if not markets or any(m not in MARKETS for m in markets):
        raise SourceError('markets must be KR and/or US')
    if not isinstance(budget, int) or budget <= 0 or budget > 10**13:
        raise SourceError('budget must be a positive KRW integer')
    universe = data_mod.universe()
    as_of = now or datetime.now(timezone.utc)
    if as_of.tzinfo is None:
        raise SourceError('aware clock required')
    root = _new_run_dir(Path(run_dir))
    requests = data_mod.plan_requests(universe, markets, as_of)
    root.mkdir(parents=True)
    _dump(root / 'started.json', dict(as_of=as_of.isoformat(), markets=list(markets), question=question))
    records, request_count = data_mod.acquire(requests, root, universe['provider_policy'], fetcher=fetcher,
                                              now=now, progress=progress)
    bodies = data_mod.load_bodies(root, records)
    journal_entries = load_journal(journal) if journal else []
    run_id = root.name
    watch = list(dict.fromkeys(tuple(w) for w in watch))
    result = compute(universe, markets, budget, as_of, records, bodies, journal_entries, run_id, watch)
    result['http_requests'] = request_count
    report = render(result)
    files = {}
    files['acquisition.json'] = _dump(root / 'acquisition.json', records)
    files['journal_inputs.json'] = _dump(root / 'journal_inputs.json', journal_entries)
    files['picks.json'] = _dump(root / 'picks.json', {k: v for k, v in result.items() if k != 'markets'} | dict(
        markets={mk: {k: v for k, v in m.items() if k not in ('monthly', 'ranking')} for mk, m in result['markets'].items()}))
    files['backtest.json'] = _dump(root / 'backtest.json', {mk: dict(monthly=m.get('monthly'), ranking=m.get('ranking'))
                                                            for mk, m in result['markets'].items()})
    (root / 'report.md').write_text(report, encoding='utf-8')
    files['report.md'] = hashlib.sha256(report.encode('utf-8')).hexdigest()
    _dump(root / 'picks_manifest.json', dict(
        schema_version='stock-picks-run-v1', version=VERSION, model_version=model.VERSION,
        policy_version=model.POLICY_VERSION, data_version=data_mod.VERSION, as_of=result['as_of'],
        markets=list(markets), budget_krw=budget, question=question, run_id=run_id,
        watch=[list(w) for w in watch],
        http_requests=request_count, code_sha256=_code_digest(), outputs=files))
    if journal:
        result['journal_written'] = record_journal(journal, result)
    return result, report


def replay_picks(run_dir):
    """Offline: verify stored bodies, recompute, compare report bytes."""
    from .stock_report import render
    root = Path(run_dir)
    manifest = json.loads((root / 'picks_manifest.json').read_text(encoding='utf-8'))
    if manifest.get('schema_version') != 'stock-picks-run-v1':
        raise SourceError('not a stock picks run directory')
    records = json.loads((root / 'acquisition.json').read_text(encoding='utf-8'))
    bodies = data_mod.load_bodies(root, records)
    journal_entries = json.loads((root / 'journal_inputs.json').read_text(encoding='utf-8'))
    as_of = datetime.fromisoformat(manifest['as_of'])
    result = compute(data_mod.universe(), tuple(manifest['markets']), manifest['budget_krw'], as_of,
                     records, bodies, journal_entries, manifest['run_id'],
                     [tuple(w) for w in manifest.get('watch', [])])
    result['http_requests'] = manifest['http_requests']
    report = render(result)
    identical = hashlib.sha256(report.encode('utf-8')).hexdigest() == manifest['outputs']['report.md']
    return result, report, identical, manifest['code_sha256'] == _code_digest()
