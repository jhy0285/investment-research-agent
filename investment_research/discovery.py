"""Bounded, need-first source discovery in front of the existing source pipeline.

Publisher directories and public searches return candidates, never evidence.
Only an opened document satisfying a reviewed contract can become a SourceSpec.
No crawler, model truth authority, shell instructions, or composite trust score.
"""

from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
import re
from urllib.parse import quote, urljoin

from .discovery_contracts import CONTRACT_VERSION, html_records, json_document, parse_candidate
from .models import SOURCE_HIERARCHY, SourceType
from .source_pipeline import _digest
from .sources import (
    SourceError,
    SourceSpec,
    _decode,
    _fetch_http,
    _sha,
    _time,
    _url,
    _validate,
    _visible_html,
    read_public,
)

DISCOVERY_VERSION = 'need_first_source_discovery_v1'
NEED_NAMES = {
    'market_state': '현재 가격·거래 상태',
    'etf_flows': 'BTC 현물 ETF 자금흐름',
    'derivatives': '파생 계약의 비용·미결제약정',
    'community': '최근 투자 내러티브',
    'network': '네트워크 활동',
    'liquidity': '시장 유동성',
    'regulation': '규제 변화',
    'stablecoins': 'stablecoin 환경',
}
AGE_SECONDS = {
    'market_state': 3600,
    'etf_flows': 4 * 86400,
    'derivatives': 3600,
    'community': 21 * 86400,
    'network': 86400,
    'liquidity': 86400,
    'regulation': 30 * 86400,
    'stablecoins': 86400,
}
from .korean_data import CATEGORY_NAMES

NEED_NAMES.update(CATEGORY_NAMES)
from .semiconductor_data import NAMES as SEMICONDUCTOR_NAMES

NEED_NAMES.update(SEMICONDUCTOR_NAMES)
from .scan import NAMES as SCAN_NAMES
from .scan_minimum import NAMES as MINIMUM_NAMES
from .commodity_data import NAMES as COMMODITY_NAMES

NEED_NAMES.update(SCAN_NAMES)
NEED_NAMES.update(MINIMUM_NAMES)
NEED_NAMES.update(COMMODITY_NAMES)


def evidence_needs(question, methods, tasks):
    """Select relevant categories, not every possible crypto checklist item."""
    if 'BTC' not in {m['id'] for m in methods}:
        return []
    patterns = {
        'market_state': r'가격|시세|price|거래량',
        'etf_flows': r'ETF|자금.?흐름|순유입|순유출|flow|기관',
        'derivatives': r'선물|파생|funding|미결제|레버리지|청산',
        'community': r'커뮤니티|내러티브|narrative|sentiment|여론|토론',
        'network': r'네트워크|온체인|on.chain',
        'liquidity': r'유동성|liquidity',
        'regulation': r'규제|regulation',
        'stablecoins': r'stablecoin|스테이블',
    }
    selected = [name for name, pattern in patterns.items() if re.search(pattern, question, re.I)]
    if not selected:
        scan_only = all(t['mode'] == 'opportunity_scan' for t in tasks if 'BTC' in t['method_ids'])
        selected = (
            ['market_state', 'etf_flows'] if scan_only else ['market_state', 'etf_flows', 'derivatives', 'community']
        )
    return [
        dict(
            id='NEED_BTC_' + name.upper(),
            asset_id='BTC',
            category=name,
            label=NEED_NAMES[name],
            reason='사용자 질문의 Bitcoin 판단에 필요한 ' + NEED_NAMES[name],
            max_age_seconds=AGE_SECONDS[name],
            max_selected=2 if name == 'community' else 1,
        )
        for name in selected
    ]


def validate_policy(policy):
    if not isinstance(policy, dict) or policy.get('schema_version') != 'discovery-policy-v1':
        raise SourceError('unsupported discovery policy')
    extension = policy.get('scan_extension')
    if extension not in (None, 'four_asset_minimum_v2', 'commodity_deep_v1'):
        raise SourceError('unreviewed discovery extension')
    for key, low, high in (
        ('max_requests', 1, 64 if extension == 'commodity_deep_v1' else 48 if extension else 32),
        ('max_candidates_per_need', 1, 12),
    ):
        if type(policy.get(key)) is not int or not low <= policy[key] <= high:
            raise SourceError('invalid discovery request/candidate budget')
    providers = policy.get('providers')
    if not isinstance(providers, list) or len(providers) > 12:
        raise SourceError('bounded discovery providers required')
    seen = set()
    for p in providers:
        if (
            not isinstance(p, dict)
            or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]{0,49}', p.get('id', ''))
            or p['id'] in seen
        ):
            raise SourceError('invalid or duplicate discovery provider')
        seen.add(p['id'])
        if p.get('type') not in {x.value for x in SourceType} or type(p.get('canonical')) is not bool:
            raise SourceError('explicit source hierarchy and canonical-owner status required')
        if p.get('method') not in (
            'market_directory',
            'instrument_directory',
            'publisher_links',
            'community_search',
            'access_probe',
            'official_regional_series',
            'reviewed_document',
            'issuer_financial_link',
            'semiconductor_dart_directory',
            'semiconductor_statement_links',
        ):
            raise SourceError('unsupported discovery method')
        if not isinstance(p.get('categories'), list) or not set(p['categories']) <= set(NEED_NAMES):
            raise SourceError('invalid evidence categories')
        if 'max_candidates' in p and (type(p['max_candidates']) is not int or not 1 <= p['max_candidates'] <= 12):
            raise SourceError('invalid provider candidate budget')
        if 'blocks' in p and (
            not isinstance(p['blocks'], list)
            or not p['blocks']
            or any(not isinstance(b, str) or not re.fullmatch(r'[a-z][a-z0-9_]{0,39}', b) for b in p['blocks'])
        ):
            raise SourceError('invalid reviewed provider financial blocks')
        if not isinstance(p.get('publisher'), str) or not p['publisher'].strip() or not p.get('policy_note'):
            raise SourceError('reviewed publisher/access metadata required')
        _url(p['seed_url'])
        _url(p['policy_url'])
        if p.get('access_method') not in ('public_api', 'public_http'):
            raise SourceError('invalid discovery access method')
        if not isinstance(p.get('candidate_hosts'), list) or not p['candidate_hosts']:
            raise SourceError('explicit candidate destination policy required')
        for host in p['candidate_hosts']:
            _url('https://' + host + '/')
        if p.get('candidate_template'):
            _url(p['candidate_template'].replace('{identity}', 'BTC-USD'))
        if 'documents' in p:
            if (
                p['method'] != 'reviewed_document'
                or not isinstance(p['documents'], dict)
                or not 1 <= len(p['documents']) <= 8
            ):
                raise SourceError('bounded reviewed document map required')
            for block, entry in p['documents'].items():
                if not re.fullmatch(r'[a-z][a-z0-9_]{0,39}', block) or set(entry) != {
                    'seed_url',
                    'contract',
                    'identity_fields',
                }:
                    raise SourceError('invalid reviewed document mapping')
                if _url(entry['seed_url']).hostname not in p['candidate_hosts'] or not entry['contract'].startswith(
                    'minimum_'
                ):
                    raise SourceError('reviewed document outside permitted contract/host')
    return policy


class DiscoverySession:
    """Keep opened bytes in memory until acquire verifies their exact passages.

    The shared collector still checks policy, HTTPS, redirects and byte limits.
    Reusing the same response prevents selection and acquisition seeing different
    market ticks. Full bodies are not written to discovery artifacts.
    """

    def __init__(self, fetcher, budget):
        self.transport = fetcher or _fetch_http
        self.budget = budget
        self.cache = {}
        self.requests = []

    def fetch(self, url, timeout, max_bytes):
        if url not in self.cache:
            if len(self.requests) >= self.budget:
                raise SourceError('discovery request budget exhausted')
            self.requests.append(url)
            response = self.transport(url, timeout, max_bytes)
            self.cache[url] = response
        return self.cache[url]

    def acquisition_fetcher(self, url, timeout, max_bytes):
        # After discovery, ordinary curated sources retain their existing
        # acquisition boundary. Discovery responses are reused, not re-fetched.
        return self.cache[url] if url in self.cache else self.transport(url, timeout, max_bytes)


def _opened(url, provider, session, now):
    document = read_public(
        url,
        access_method=provider['access_method'],
        policy_url=provider['policy_url'],
        policy_note=provider['policy_note'],
        fetcher=session.fetch,
        now=now,
    )
    response = document.response
    record = dict(
        url=url,
        status=document.status,
        retrieved_at=document.retrieved_at,
        policy=document.policy,
        diagnostics=list(document.diagnostics),
        raw_sha256=_sha(response.body) if response else None,
        http_status=response.status if response else None,
        content_type=response.content_type if response else None,
    )
    return document, record


def _candidate(url, identity, provider, need, index, rank, advertised_at=None, locator=None, identity_fields=None):
    if len(url) > 4096:
        raise SourceError('discovered URL exceeds the bounded metadata limit')
    parts = _url(url)
    if parts.hostname not in provider['candidate_hosts']:
        raise SourceError('discovered destination is outside reviewed publisher policy')
    advertised_status = 'unknown' if advertised_at is None else 'known'
    if advertised_at is not None:
        try:
            _time(advertised_at)
        except SourceError:
            advertised_at = None
            advertised_status = 'invalid'
    return dict(
        id='CAND_' + _digest([need['id'], provider['id'], url])[:16],
        need_id=need['id'],
        url=url,
        canonical_url=url,
        identity=identity,
        provider_id=provider['id'],
        source_type=provider['type'],
        canonical_owner=provider['canonical'],
        method=provider['method'],
        discovered_via=index['url'],
        discovery_sha256=index['raw_sha256'],
        search_rank=rank,
        advertised_at=advertised_at,
        advertised_date_status=advertised_status,
        index_locator=locator,
        index_identity_fields=identity_fields,
        edition_key=provider['id']
        + ':'
        + need['asset_id']
        + ':'
        + need['category']
        + (':item:' + identity if provider['method'] == 'community_search' else ''),
        status='candidate',
        selection_reason=None,
        freshness=None,
    )


def _index_candidates(provider, need, document, index, *, auxiliary=None, month=None):
    method = provider['method']
    items = []
    if method == 'market_directory':
        directory = json_document(document.response)
        if not isinstance(directory, list):
            raise SourceError('exchange product directory must be an array')
        for i, p in enumerate(directory):
            if (
                isinstance(p, dict)
                and p.get('base_currency') == 'BTC'
                and p.get('quote_currency') == 'USD'
                and p.get('status') == 'online'
                and p.get('trading_disabled') is False
            ):
                items.append(
                    (
                        p['id'],
                        None,
                        i,
                        '/' + str(i),
                        {k: p[k] for k in ('id', 'base_currency', 'quote_currency', 'status', 'trading_disabled')},
                    )
                )
    elif method == 'instrument_directory':
        directory = json_document(document.response)['result']
        for i, p in enumerate(directory):
            if (
                p.get('base_currency') == 'BTC'
                and p.get('quote_currency') == 'USD'
                and p.get('settlement_currency') == 'BTC'
                and p.get('instrument_type') == 'reversed'
                and p.get('is_active') is True
                and p.get('kind') == 'future'
                and p.get('instrument_name') == 'BTC-PERPETUAL'
            ):
                keys = (
                    'instrument_name',
                    'base_currency',
                    'quote_currency',
                    'settlement_currency',
                    'instrument_type',
                    'is_active',
                    'kind',
                )
                items.append((p['instrument_name'], None, i, '/result/' + str(i), {k: p[k] for k in keys}))
    elif method == 'publisher_links':
        if provider.get('contract') == 'minimum_deep_sec_v1':
            from .commodity_data import filing_candidates

            out = []
            for i, (url, fields) in enumerate(filing_candidates(provider, need, document.response)):
                c = _candidate(
                    url, url, provider, need, index, i, fields['published_at'], 'SEC submissions recent filing', fields
                )
                c.update(asset_id=need['asset_id'], category=need['category'])
                out.append(c)
            return out
        for i, (href, title) in enumerate(html_records(document.response).links):
            pattern = r'ethereum|\bETH\b' if provider.get('contract') == 'minimum_eth_flow_v2' else r'bitcoin|\bBTC\b'
            if re.search(pattern, title, re.I):
                items.append(
                    (
                        urljoin(provider['seed_url'], href),
                        None,
                        i,
                        'anchor[' + str(i) + ']/href',
                        {'href': href, 'label': title[:200]},
                    )
                )
    elif method == 'community_search':
        hits = json_document(document.response)['hits']
        # Search text is deliberately neither retained nor used as evidence.
        for i, h in enumerate(hits):
            if not isinstance(h, dict) or not isinstance(h.get('objectID'), str):
                continue
            # Screening a hit for relevance is allowed; its text never becomes
            # a quote/fact. The original item is independently opened below.
            preview = _visible_html(h.get('comment_text') or '')
            if provider.get('contract') == 'scan_hn_v1':
                from .scan import narrative_relevant

                relevant = narrative_relevant(preview)
            elif provider.get('contract') == 'semiconductor_hn_v1':
                company = r'\bSamsung\b|삼성' if need['asset_id'] == 'SAMSUNG' else r'\b(?:SK\s*)?hynix\b|하이닉스'
                relevant = bool(
                    re.search(company, preview, re.I)
                    and re.search(r'HBM|memory|DRAM|NAND|valuat|earnings|capex', preview, re.I)
                )
            else:
                relevant = bool(
                    re.search(r'\bbitcoin\b|\bBTC\b', preview, re.I)
                    and re.search(
                        r'\b(?:price|ETF|inflow|outflow|risk|value|supply|scarcity|inflation|ponzi|invest|bull|bear|demand)\w*\b',
                        preview,
                        re.I,
                    )
                )
            if relevant:
                items.append(
                    (
                        h['objectID'],
                        h.get('created_at'),
                        i,
                        '/hits/' + str(i) + '/objectID',
                        {'objectID': h['objectID'], 'created_at': h.get('created_at')},
                    )
                )
    elif method == 'official_regional_series':
        from .korean_data import regional_identity, regional_url

        identity = regional_identity(provider, need, document.response, auxiliary.response)
        url = regional_url(identity, month)
        items.append((url, None, 0, 'official table metadata + table-specific region/item directory', identity))
    elif method == 'reviewed_document':
        items.append(
            (
                provider['seed_url'],
                None,
                0,
                'reviewed document URL',
                provider.get('identity_fields', {'company': 'SAMSUNG'}),
            )
        )
    elif method in ('semiconductor_dart_directory', 'semiconductor_statement_links'):
        from .semiconductor_data import directory_items

        for i, (url, fields) in enumerate(directory_items(provider, need, document.response)):
            items.append((url, fields.get('published_at'), i, 'reviewed issuer link or company-bound DART row', fields))
    elif method == 'issuer_financial_link':
        # Auxiliary is a first-party route bundle LINKED by the IR page. Read
        # only the explicit provider URL literal; never run downloaded scripts.
        body = _decode(auxiliary.response.body, auxiliary.response.content_type)
        if 'UI-FR-IR07' not in body or 'SK hynix IAT' not in body:
            raise SourceError('issuer financial-statements route identity missing')
        links = re.findall(
            r'urlBase:"(//asia\.tools\.euroland\.com/tools/ia/\?companycode=kr-000660&v=redesign)"', body
        )
        if len(links) != 1:
            raise SourceError('issuer-linked financial provider URL not unambiguous')
        url = 'https:' + links[0] + '&lang=en-gb'
        items.append(
            (url, None, 0, 'official IR-linked route urlBase; no JavaScript execution', {'company_code': 'kr-000660'})
        )
    seen = set()
    candidates = []
    for identity, advertised_at, rank, locator, identity_fields in items:
        if method in ('market_directory', 'instrument_directory') and not re.fullmatch(r'[A-Z0-9_-]{1,40}', identity):
            continue
        if method == 'community_search' and not re.fullmatch(r'\d{1,15}', identity):
            continue
        url = (
            identity
            if method
            in (
                'publisher_links',
                'official_regional_series',
                'reviewed_document',
                'issuer_financial_link',
                'semiconductor_dart_directory',
                'semiconductor_statement_links',
            )
            else provider['candidate_template'].replace('{identity}', quote(identity, safe=''))
        )
        if url in seen:
            continue
        seen.add(url)
        try:
            c = _candidate(url, identity, provider, need, index, rank, advertised_at, locator, identity_fields)
            if method in (
                'official_regional_series',
                'reviewed_document',
                'issuer_financial_link',
                'semiconductor_dart_directory',
                'semiconductor_statement_links',
            ) or provider.get('contract', '').startswith('semiconductor_'):
                c['category'] = need['category']
            if provider.get('contract', '').startswith('semiconductor_'):
                c['asset_id'] = need['asset_id']
                c['index_identity_fields'] = {
                    **(c['index_identity_fields'] or {}),
                    **({'block': need['block']} if 'block' in need else {}),
                }
            if provider.get('contract', '').startswith(('scan_', 'minimum_')):
                c['asset_id'] = need['asset_id']
                if provider.get('contract') == 'minimum_eth_flow_v2':
                    c['category'] = need['category']
                    c['index_identity_fields']['block'] = need['block']
            candidates.append(c)
        except SourceError:
            continue
    return candidates


def candidate_freshness(candidate, need, as_of, research_kind='current'):
    verified = candidate.get('verified')
    if not verified:
        return dict(status='unavailable', reason='actual source not successfully opened and parsed')
    dates = [_time(verified.get(k)) for k in ('published_at', 'observed_at', 'valid_as_of')]
    retrieved = _time(candidate['document']['retrieved_at'])
    if retrieved > as_of or any(d and d > as_of for d in dates):
        return dict(status='future', reason='observation/publication/availability is after cutoff')
    if research_kind == 'historical':
        # Conservative known-at: a newly retrieved edition is not proof that
        # its original historical values were publicly available at that time.
        return dict(status='historical', reason='pinned edition was retrieved by historical cutoff')
    at = next((d for d in reversed(dates) if d), None)
    if at is None:
        return dict(status='unknown', reason='retrieval/search date does not establish observation freshness')
    age = (as_of - at).total_seconds()
    return dict(
        status='stale' if age > need['max_age_seconds'] else 'fresh',
        age_seconds=age,
        basis='valid_as_of/observed_at/published_at',
        max_age_seconds=need['max_age_seconds'],
        reason='category-specific relevance window; not a reliability score',
    )


def select_candidates(candidates, need, as_of, research_kind='current'):
    """Newest same-source edition first; hierarchy/canonical preference second."""
    if research_kind not in ('current', 'historical'):
        raise SourceError('unsupported research time mode')
    items = deepcopy(candidates)
    latest = {}
    for c in items:
        c['freshness'] = candidate_freshness(c, need, as_of, research_kind)
        verified = c.get('verified', {})
        at = (
            verified.get('valid_as_of')
            or verified.get('observed_at')
            or verified.get('published_at')
            or c.get('advertised_at')
        )
        if at and _time(at) <= as_of and (research_kind != 'historical' or c['freshness']['status'] == 'historical'):
            old = latest.get(c['edition_key'])
            if old is None or _time(at) > _time(old):
                latest[c['edition_key']] = at
        c['version_at'] = at
    eligible = []
    for c in items:
        newer = latest.get(c['edition_key'])
        if c['version_at'] and newer and _time(c['version_at']) < _time(newer):
            c.update(status='rejected', selection_reason='superseded by newer same-source edition ' + newer)
            c['superseded_by'] = [
                other['id']
                for other in items
                if other['edition_key'] == c['edition_key'] and other['version_at'] == newer
            ]
        elif c['freshness']['status'] not in ('fresh', 'historical'):
            c.update(status='rejected', selection_reason=c.get('error') or c['freshness']['reason'])
        else:
            eligible.append(c)
    eligible.sort(
        key=lambda c: (
            SOURCE_HIERARCHY[SourceType(c['source_type'])],
            not c['canonical_owner'],
            -_time(c['version_at']).timestamp(),
            c['url'],
        )
    )
    texts = set()
    selected = 0
    for c in eligible:
        key = _digest([r['quote'] for r in c['verified']['records']])
        if key in texts:
            c.update(status='rejected', selection_reason='duplicate underlying passage; not independent evidence')
        elif selected >= need['max_selected']:
            c.update(
                status='rejected',
                selection_reason='sufficient scoped evidence selected; hierarchy/canonical preference, not search rank',
            )
        else:
            texts.add(key)
            selected += 1
            c.update(
                status='selected',
                selection_reason='opened source, relevant contract, current edition; prefer primary/canonical source when compatible',
            )
    return items


def _source_entries(candidate, provider, need):
    v = candidate['verified']
    identifier = 'DISC_' + _digest([need['id'], candidate['url']])[:16]
    candidate['source_id'] = identifier
    candidate['evidence_ids'] = []
    excerpts = []
    evidence = []
    for i, record in enumerate(v['records']):
        qid = 'Q_' + str(i + 1)
        eid = 'E_' + identifier + '_' + str(i + 1)
        excerpts.append(dict(id=qid, quote=record['quote'], locator=record['locator'], definition=record['definition']))
        candidate['evidence_ids'].append(eid)
        record['evidence_id'] = eid
        community = provider['type'] == 'community'
        evidence.append(
            dict(
                id=eid,
                source_id=identifier,
                excerpt_id=qid,
                view='community' if community else 'quantitative',
                kind='observed_narrative' if community else 'observed_fact',
                definition=record['definition'],
                extraction=record['extraction'],
                interpretation=(
                    None
                    if community
                    else dict(
                        status='reviewed',
                        reviewer='deterministic discovery document contract',
                        reviewed_at=_time(candidate['document']['retrieved_at']).date().isoformat(),
                        rationale='원문 필드·대상·시각·단위 전사만 확인했다. 경제적 해석·투자 매력의 의미 검토가 아니다.',
                    )
                ),
                limitations=[*v['limitations'], *record['limitations']],
            )
        )
        if record.get('observed_at') is not None:
            evidence[-1]['observed_at'] = record['observed_at']
    canonical = candidate['url']
    if provider['contract'] in ('hn_comment_v1', 'semiconductor_hn_v1', 'scan_hn_v1'):
        canonical = 'https://news.ycombinator.com/item?id=' + candidate['identity']
    elif v.get('canonical'):
        target = urljoin(candidate['url'], v['canonical'])
        parts = _url(target)
        if parts.hostname not in provider['candidate_hosts']:
            raise SourceError('unapproved canonical destination')
        canonical = target
    candidate['canonical_url'] = canonical
    spec = SourceSpec(
        id=identifier,
        url=candidate['url'],
        canonical_url=canonical,
        type=provider['type'],
        publisher=provider['publisher'],
        title=need['label'] + ' · ' + provider['publisher'],
        published_at=v['published_at'],
        observed_at=v['observed_at'],
        valid_as_of=v['valid_as_of'],
        jurisdiction=provider.get('jurisdiction', 'unknown'),
        topics=(need['category'],),
        asset_ids=(need['asset_id'],),
        content_type=candidate['document']['content_type'].split(';')[0].strip(),
        access_method=provider['access_method'],
        policy_url=provider['policy_url'],
        policy_note=provider['policy_note'],
        retention='excerpt',
        max_age_days=max(1, (need['max_age_seconds'] + 86399) // 86400),
        excerpts=tuple(excerpts),
    )
    _validate(spec)
    candidate['source_version'] = v['valid_as_of'] + '#' + candidate['document']['raw_sha256']
    return asdict(spec), evidence


def discover_sources(needs, policy, *, fetcher=None, now=None, progress=None):
    policy = validate_policy(policy)
    session = DiscoverySession(fetcher, policy['max_requests'])
    record = dict(
        schema_version='source-discovery-v1',
        method_version=DISCOVERY_VERSION,
        contract_version=CONTRACT_VERSION,
        research_kind='current',
        needs=deepcopy(needs),
        indexes=[],
        candidates=[],
        selection_as_of=None,
        requests=[],
        sources=[],
        evidence=[],
        index_retention='selected candidate identities/links, policy and hashes only; full search/index bodies not retained',
    )
    providers = {p['id']: p for p in policy['providers']}
    if policy.get('deferred_providers'):
        record['deferred_providers'] = deepcopy(policy['deferred_providers'])
    for need in needs:
        candidates = []
        remaining = policy['max_candidates_per_need']
        for provider in policy['providers']:
            if need['category'] == 'scan_eth_flow' and provider.get('eth_contract') == 'minimum_eth_flow_v2':
                provider = {
                    **provider,
                    'contract': provider['eth_contract'],
                    'identity_fields': {'block': need['block']},
                }
            if need['category'] not in provider['categories']:
                continue
            if provider.get('asset_ids') and need['asset_id'] not in provider['asset_ids']:
                continue
            if provider.get('blocks') and need.get('block') not in provider['blocks']:
                continue
            if provider.get('documents'):
                document = provider['documents'].get(need.get('block'))
                if document is None:
                    continue
                provider = {**provider, **document}
            if progress:
                progress(need['label'] + ' 출처 발견: ' + provider['publisher'])
            opened, index = _opened(provider['seed_url'], provider, session, now)
            index.update(
                need_id=need['id'],
                provider_id=provider['id'],
                method=provider['method'],
                query=provider.get('query'),
                role='discovery_candidates_only_not_evidence',
            )
            record['indexes'].append(index)
            if opened.status != 'available':
                continue
            try:
                auxiliary = None
                dependency = None
                if provider['method'] == 'official_regional_series':
                    auxiliary, meta = _opened(provider['codes_url'], provider, session, now)
                    meta.update(
                        need_id=need['id'],
                        provider_id=provider['id'],
                        method=provider['method'],
                        role='official_table_specific_codes_not_evidence',
                    )
                    record['indexes'].append(meta)
                    if auxiliary.status != 'available':
                        raise SourceError('official region/item codes unavailable')
                    dependency = dict(url=meta['url'], raw_sha256=meta['raw_sha256'], role=meta['role'])
                elif provider['method'] == 'issuer_financial_link':
                    body = _decode(opened.response.body, opened.response.content_type)
                    paths = list(dict.fromkeys(re.findall(r'<script[^>]*src="(/_nuxt/[a-f0-9]{7}\.js)"', body)))
                    for path in paths[:6]:
                        url = urljoin(provider['seed_url'], path)
                        script, meta = _opened(url, provider, session, now)
                        meta.update(
                            need_id=need['id'],
                            provider_id=provider['id'],
                            method=provider['method'],
                            role='issuer_linked_route_metadata_only_never_executed',
                        )
                        record['indexes'].append(meta)
                        if script.status == 'available' and 'SK hynix IAT' in _decode(
                            script.response.body, script.response.content_type
                        ):
                            auxiliary = script
                            dependency = dict(url=meta['url'], raw_sha256=meta['raw_sha256'], role=meta['role'])
                            break
                    if auxiliary is None:
                        raise SourceError('official IR financial provider link unavailable')
                found = _index_candidates(
                    provider, need, opened, index, auxiliary=auxiliary, month=policy.get('as_of_month')
                )
                if dependency:
                    for c in found:
                        c['discovery_dependency'] = dependency
            except (SourceError, KeyError, TypeError, ValueError, OverflowError) as exc:
                index.update(status='parse_error', diagnostics=[str(exc)])
                continue
            limit = min(remaining, provider.get('max_candidates', remaining))
            for candidate in found[:limit]:
                doc, metadata = _opened(candidate['url'], provider, session, now)
                candidate['document'] = metadata
                try:
                    if doc.status != 'available':
                        raise SourceError('; '.join(doc.diagnostics) or doc.status)
                    candidate['verified'] = parse_candidate(provider['contract'], doc.response, candidate)
                except (SourceError, KeyError, TypeError, ValueError, OverflowError) as exc:
                    candidate['error'] = str(exc)
                    candidate['status'] = 'rejected'
                candidates.append(candidate)
                if progress:
                    progress(
                        need['label']
                        + ' 원문 확인: '
                        + (
                            'contract_matched'
                            if 'verified' in candidate
                            else candidate['document']['status'] if doc.status != 'available' else 'parse_error'
                        )
                    )
            remaining -= min(limit, len(found))
            if remaining <= 0:
                break
        record['candidates'].extend(candidates)
    cutoff = now or datetime.now(timezone.utc)
    record['selection_as_of'] = cutoff.isoformat()
    chosen = []
    for need in record['needs']:
        choices = select_candidates([c for c in record['candidates'] if c['need_id'] == need['id']], need, cutoff)
        for candidate in choices:
            if candidate['status'] == 'selected':
                spec, evidence = _source_entries(candidate, providers[candidate['provider_id']], need)
                record['sources'].append(spec)
                record['evidence'].extend(evidence)
        chosen.extend(choices)
    record['candidates'] = chosen
    record['requests'] = session.requests
    # Several fields/quarters from the same document are dependent, even when
    # excerpt limits require separate SourceSpecs.
    if any(
        n['category'] in {*CATEGORY_NAMES, *SEMICONDUCTOR_NAMES, 'scan_gas_context', 'scan_eth_flow', 'commodity_deep'}
        for n in needs
    ):
        origins = {}
        for spec in record['sources']:
            key = spec['url']
            if key in origins:
                spec['origin_source_id'] = origins[key]
            else:
                origins[key] = spec['id']
    record['community_verification'] = community_verifications(record)
    return record, session.acquisition_fetcher


def community_verifications(record):
    """Verify only an explicit, dated, same-definition factual subclaim.

    Everything outside this narrow grammar remains unverified. Broad causal
    claims, different dates, incomplete flow totals and general sentiment cannot
    be proved/contradicted by a convenient nearby number.
    """
    selected = [c for c in record['candidates'] if c['status'] == 'selected']
    factual = [(c, r) for c in selected if c['source_type'] != 'community' for r in c['verified']['records']]
    checks = []
    grammar = r'On (\d{4}-\d{2}-\d{2}),? US spot Bitcoin ETFs had net (inflows|outflows) of \$(\d+(?:\.\d+)?) million\.'
    for c in selected:
        if c['source_type'] != 'community':
            continue
        if c.get('asset_id') in ('SAMSUNG', 'SK_HYNIX'):
            from .semiconductor_data import community_check

            checks.append(community_check(c, factual))
            continue
        if c.get('asset_id') == 'GROWTH_THEME':
            checks.append(
                dict(
                    asset_ids=['GROWTH_THEME'],
                    narrative_evidence_id=c['evidence_ids'][0],
                    source_id=c['source_id'],
                    factual_claim=None,
                    verification='unverified',
                    evidence_ids=[r['evidence_id'] for f, r in factual if f.get('asset_id') == 'GROWTH_THEME'],
                    reason='현재 발행사 자료를 맥락으로 연결한다. 공급자 매출·고객 투자회수·가격 기대 주장은 같은 정의의 사실 검증 전이다.',
                )
            )
            continue
        r = c['verified']['records'][0]
        text = r['quote']
        linked = [
            v['evidence_id']
            for _, v in factual
            if 'ETF' in text and v['definition']['measure'] == 'US_SPOT_BTC_ETF_DAILY_NET_FLOW'
        ]
        check = dict(
            narrative_evidence_id=r['evidence_id'],
            source_id=c['source_id'],
            factual_claim=None,
            verification='unverified',
            evidence_ids=linked,
            reason='공식/제공자 자료를 대조하되 같은 기간·정의의 검증 가능한 사실 문장이 부족하다. 발언 전체는 미확인이다.',
        )
        match = re.search(grammar, text)
        if match:
            expected = ('-' if match[2] == 'outflows' else '') + match[3]
            compatible = [
                v
                for _, v in factual
                if v['definition']['measure'] == 'US_SPOT_BTC_ETF_DAILY_NET_FLOW'
                and v['definition']['period'] == match[1]
                and v['definition']['adjustment'] == 'complete_row_provider_reported_not_issuer_confirmed'
            ]
            check['factual_claim'] = match[0]
            if compatible:
                v = compatible[0]
                check.update(
                    evidence_ids=[v['evidence_id']],
                    rule='numeric_equality_v1',
                    assertion={**v['definition'], 'evidence_id': v['evidence_id'], 'expected_value': expected},
                    reason='날짜·통화·범위가 일치한 완성 행의 제공자 수치와 좁은 사실 문장만 비교한다. narrative 전체·투자 해석은 미확인이다.',
                )
            else:
                check['reason'] = (
                    '동일 날짜·정의의 완성 ETF 행이 없어 사실 문장 확인을 보류했다. 오래된/잠정 합계로 대체하지 않는다.'
                )
        checks.append(check)
    return checks


def scoped_catalog_sources(source_data, needs):
    """Old registered prose cannot stand in for a discovered BTC observation."""
    if not source_data or not any(n['asset_id'] == 'BTC' for n in needs):
        return source_data
    data = deepcopy(source_data)
    categories = {n['category'] for n in needs}
    keep_product = bool(categories & {'etf_flows', 'community'})
    sources = []
    for s in data['sources']:
        if 'BTC' in s['asset_ids'] and not (keep_product and s['id'] == 'CR_IBIT_ISSUER'):
            s['asset_ids'] = [a for a in s['asset_ids'] if a != 'BTC']
        if s['asset_ids']:
            sources.append(s)
    data['sources'] = sources
    scope = {s['id']: set(s['asset_ids']) for s in sources}
    data['evidence'] = [e for e in data['evidence'] if e['source_id'] in scope]
    available = {e['id']: scope[e['source_id']] for e in data['evidence']}
    claims = []
    for c in data['claims']:
        refs = (
            c['support_ids']
            + c['counter_ids']
            + c['context_ids']
            + ([c['narrative_evidence_id']] if c['narrative_evidence_id'] else [])
        )
        if all(r in available and set(c['asset_ids']) <= available[r] for r in refs):
            claims.append(c)
    data['claims'] = claims
    return data


def attach_discovery(source_data, record, question, day, asset_ids):
    data = (
        deepcopy(source_data)
        if source_data
        else dict(
            schema_version='1',
            id='ASK_SELECTED_SOURCES',
            question=question,
            as_of=day.isoformat(),
            asset_ids=asset_ids,
            sources=[],
            evidence=[],
            claims=[],
        )
    )
    data['sources'].extend(record['sources'])
    data['evidence'].extend(record['evidence'])
    if any('observed_at' in e for e in record['evidence']):
        from .source_pipeline import OBSERVATION_DATES_VERSION

        data['observation_dates_version'] = OBSERVATION_DATES_VERSION
    for i, check in enumerate(record['community_verification']):
        narrative = check['narrative_evidence_id']
        is_numeric = check.get('rule') == 'numeric_equality_v1'
        data['claims'].append(
            dict(
                id='DISC_COMMUNITY_CLAIM_' + str(i + 1),
                text=check['factual_claim'] or '발견된 공개 발언의 내용은 같은 정의의 원자료로 추가 확인해야 한다.',
                asset_ids=check.get('asset_ids', ['BTC']),
                rule='numeric_equality_v1' if is_numeric else 'reviewed_links_v1',
                support_ids=[],
                counter_ids=[],
                context_ids=check['evidence_ids'],
                narrative_evidence_id=narrative,
                review=dict(
                    status='reviewed' if is_numeric else 'pending',
                    reviewer='deterministic dated flow assertion parser' if is_numeric else None,
                    reviewed_at=day.isoformat() if is_numeric else None,
                    rationale=check['reason'],
                ),
                verification='unverified',
                limitations=['커뮤니티 발언은 numeric evidence가 아니며 발언 전체의 진실·대표성은 검증하지 않는다.'],
                recheck='동일 날짜·정의의 발행사 원자료·정정·반대 자료를 확인한다.',
                **({'assertion': check['assertion']} if is_numeric else {}),
            )
        )
    return data if data['sources'] else None


def replay_discovery(record, case, cutoff):
    """Offline promotion audit against actual evidence, pins and fine freshness."""
    if (
        record.get('schema_version') != 'source-discovery-v1'
        or record.get('method_version') != DISCOVERY_VERSION
        or record.get('contract_version') != CONTRACT_VERSION
    ):
        raise SourceError('unsupported discovery replay')
    out = deepcopy(record)
    sources = {s.id: s for s in case.sources}
    evidence = {e.id: e for e in case.evidence}
    for need in record['needs']:
        stored = [c for c in record['candidates'] if c['need_id'] == need['id']]
        calculated = select_candidates(stored, need, _time(record['selection_as_of']), record['research_kind'])
        keys = ('id', 'status', 'selection_reason', 'freshness', 'version_at')
        if [{k: c[k] for k in keys} for c in stored] != [{k: c[k] for k in keys} for c in calculated]:
            raise SourceError('discovery selection does not replay under its pinned time/rules')
    claims = {c.id: c for c in case.claims}
    for i, check in enumerate(out['community_verification']):
        claim = claims.get('DISC_COMMUNITY_CLAIM_' + str(i + 1))
        if claim:
            check.update(
                claim_id=claim.id,
                verification=claim.verification.value,
                support_ids=list(claim.support_ids),
                counter_ids=list(claim.counter_ids),
            )
    for need in out['needs']:
        selected = [c for c in out['candidates'] if c['need_id'] == need['id'] and c['status'] == 'selected']
        accepted = []
        reasons = []
        for candidate in selected:
            source = sources.get(candidate['source_id'])
            age = candidate_freshness(candidate, need, cutoff)
            refs = candidate['evidence_ids']
            if (
                source is None
                or source.provenance.status != 'available'
                or age['status'] != 'fresh'
                or any(r not in evidence for r in refs)
            ):
                reasons.append('최신 원문·동일 snapshot 근거를 확보하지 못함: ' + candidate['url'])
                continue
            if source.provenance.raw_sha256 != candidate['document']['raw_sha256']:
                raise SourceError('discovered source changed between opening and acquisition')
            for ref, r in zip(refs, candidate['verified']['records']):
                e = evidence[ref]
                if e.text != r['quote'] or e.provenance.definition != r['definition'] or e.source_id != source.id:
                    raise SourceError('discovery promotion disagrees with verified source evidence')
            accepted.extend(refs)
            if not candidate['verified']['complete']:
                reasons.append(
                    '원문에서 확인하지 못한 필드: '
                    + ', '.join(candidate['verified'].get('missing_fields', []))
                    + '. 다른 자료·추정값으로 채우지 않는다.'
                    if need['category'] in CATEGORY_NAMES
                    else '최신 ETF 행에 누락 값이 있어 전체 확정 순유입은 unavailable; 잠정 합계만 확인했다.'
                )
        need['canonical_preference'] = dict(
            selected_types=list(dict.fromkeys(c['source_type'] for c in selected)),
            primary_available=any(c['source_type'] == 'primary' for c in selected),
            reason=(
                '공식 거래소 원문을 사용했다.'
                if any(c['source_type'] == 'primary' for c in selected)
                else (
                    '같은 정의의 공식 일별 전체 집계 연결은 없다. 상품 설명·AUM은 순유입과 달라 대체하지 않았고 확인한 제공자 행만 사용한다.'
                    if need['category'] == 'etf_flows'
                    else (
                        '공개 발언의 원문을 확인한다. 금융 사실의 원출처 지위로 올리지 않는다.'
                        if need['category'] == 'community'
                        else '적격 원출처를 확보하지 못했다.'
                    )
                )
            ),
        )
        if need['category'] in CATEGORY_NAMES:
            need['canonical_preference'] = dict(
                selected_types=list(dict.fromkeys(c['source_type'] for c in selected)),
                primary_available=any(c['source_type'] == 'primary' for c in selected),
                reason=(
                    '공식 원문·표 정의·기업/지역 식별자를 확인했다.'
                    if any(c['source_type'] == 'primary' for c in selected)
                    else (
                        '공식 IR 연결 제공자 자료만 확보했다. 원공시 확인이 미완료이며 primary로 승격하지 않는다.'
                        if selected
                        else '조건에 맞는 원문을 확보하지 못했으며 다른 국가·기업·지역으로 대체하지 않는다.'
                    )
                ),
            )
        if need.get('canonical_context') == 'official_statistical_or_issuer_document_with_explicit_definition':
            need['canonical_preference'] = dict(
                selected_types=list(dict.fromkeys(c['source_type'] for c in selected)),
                primary_available=any(c['source_type'] == 'primary' for c in selected),
                reason=(
                    '공식 통계/거래소 원문에서 대상·날짜·단위를 확인했다. 수치 전사는 투자 해석의 검증과 별개다.'
                    if any(c['source_type'] == 'primary' for c in selected)
                    else (
                        '발행사 원문의 명시적 정의를 확인했다. 외부 benchmark/전망 원제공자의 독립 대조와 투자 해석은 별도다.'
                        if selected
                        else '조건에 맞는 현재 원문을 확보하지 못했다. 다른 자산이나 정의로 대신하지 않는다.'
                    )
                ),
            )
        need.update(
            evidence_ids=accepted,
            status='partial' if accepted and reasons else 'available' if accepted else 'unavailable',
            gaps=(
                reasons
                if reasons
                else (
                    []
                    if accepted
                    else ['필요한 최신 원문·정의의 evidence를 찾지 못했다. 비슷한 자료로 대체하지 않는다.']
                )
            ),
        )
    return out
