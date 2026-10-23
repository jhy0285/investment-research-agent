"""Small, reviewed document contracts used after a source has been opened.

Discovery can find new URLs, editions and values. It cannot invent their meaning:
each supported format supplies explicit identity, units, dates and limitations.
These are transcription checks, not economic judgments or a truth score.
"""

from datetime import datetime, timezone
from html.parser import HTMLParser
import re

from .source_pipeline import _decimal
from .sources import SourceError, _decode, _parse_json, _time, _visible_html

CONTRACT_VERSION = 'discovery_document_contracts_v1'


class HTMLRecords(HTMLParser):
    """Read anchors/canonical metadata and table cells; never script contents."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.canonical = None
        self.tables = []
        self._link = None
        self._table = None
        self._row = None
        self._cell = None
        self._hidden = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script', 'style', 'template', 'noscript'):
            self._hidden += 1
        if self._hidden:
            return
        if tag == 'link' and 'canonical' in a.get('rel', '').split():
            self.canonical = a.get('href')
        if tag == 'a' and a.get('href'):
            self._link = [a['href'], []]
        if tag == 'table':
            self._table = []
        if tag == 'tr' and self._table is not None:
            self._row = []
        if tag in ('td', 'th') and self._row is not None:
            self._cell = []

    def handle_data(self, data):
        if self._hidden:
            return
        if self._link is not None:
            self._link[1].append(data)
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'template', 'noscript') and self._hidden:
            self._hidden -= 1
        if self._hidden:
            return
        if tag == 'a' and self._link is not None:
            self.links.append((self._link[0], ' '.join(''.join(self._link[1]).split())))
            self._link = None
        if tag in ('td', 'th') and self._cell is not None:
            self._row.append(' '.join(''.join(self._cell).split()))
            self._cell = None
        if tag == 'tr' and self._row is not None:
            self._table.append(self._row)
            self._row = None
        if tag == 'table' and self._table is not None:
            self.tables.append(self._table)
            self._table = None


def html_records(response):
    if response.content_type.split(';')[0].strip() not in ('text/html', 'application/xhtml+xml'):
        raise SourceError('publisher index/candidate must be HTML')
    parser = HTMLRecords()
    parser.feed(_decode(response.body, response.content_type))
    parser.close()
    return parser


def json_document(response):
    if response.content_type.split(';')[0].strip() != 'application/json':
        raise SourceError('documented API returned a different format')
    return _parse_json(_decode(response.body, response.content_type))


def definition(measure, unit, period, currency, scope, adjustment):
    return dict(measure=measure, unit=unit, period=period, currency=currency, scope=scope, adjustment=adjustment)


def scalar(document, pointer, label, d, *, positive=False):
    current = document
    for key in pointer.split('/')[1:]:
        current = current[int(key)] if isinstance(current, list) else current[key]
    value = _decimal(str(current), 'discovered observation')
    if isinstance(current, bool) or (positive and value <= 0):
        raise SourceError('invalid financial field in opened source')
    return dict(
        quote=str(current),
        locator='json_scalar:' + pointer,
        definition=d,
        extraction='decimal_scalar_v1',
        label=label,
        limitations=[],
    )


def _date(value):
    if not isinstance(value, str) or _time(value) is None:
        raise SourceError('source observation date is required')
    return _time(value).isoformat()


def parse_candidate(contract, response, candidate):
    """No snippets, model calls, DOM instructions, or guessed dates/definitions."""
    if contract.startswith('minimum_deep_'):
        from .commodity_data import parse_candidate as parse_commodity

        return parse_commodity(contract, response, candidate)
    if contract.startswith('minimum_'):
        from .scan_minimum import parse_candidate as parse_minimum

        return parse_minimum(contract, response, candidate)
    if contract.startswith('scan_'):
        from .scan import parse_candidate as parse_scan_candidate

        return parse_scan_candidate(contract, response, candidate)
    if contract.startswith('semiconductor_'):
        from .semiconductor_data import parse_candidate as parse_semiconductor_candidate

        return parse_semiconductor_candidate(contract, response, candidate)
    if contract in ('reb_regional_monthly_v1', 'euroland_hynix_quarterly_v1', 'samsung_quarterly_release_v1'):
        from .korean_data import parse_korean_candidate

        return parse_korean_candidate(contract, response, candidate)
    if contract == 'coinbase_ticker_v1':
        doc = json_document(response)
        at = _date(doc['time'])
        # Identity came from the official directory, not an unrelated price.
        if candidate['identity'] != 'BTC-USD':
            raise SourceError('unexpected market identity')
        records = [
            scalar(
                doc,
                '/price',
                'Coinbase BTC/USD 최근 체결 가격',
                definition(
                    'COINBASE_BTC_USD_LAST_TRADE',
                    'USD_per_BTC',
                    'last_trade',
                    'USD',
                    'Coinbase Exchange BTC-USD',
                    'unadjusted_exchange_trade',
                ),
                positive=True,
            ),
            scalar(
                doc,
                '/volume',
                'Coinbase BTC/USD 24시간 거래량',
                definition(
                    'COINBASE_BTC_USD_24H_BASE_VOLUME',
                    'BTC',
                    'rolling_24h',
                    None,
                    'Coinbase Exchange BTC-USD',
                    'exchange_reported_base_volume',
                ),
            ),
        ]
        records[1]['limitations'] = ['가격 시각과 거래량의 24시간 종료 시각이 정확히 같다는 보장은 없다.']
        if _decimal(records[1]['quote'], 'volume') < 0:
            raise SourceError('negative exchange volume')
        records[0]['observed_at'] = at
        return dict(
            observed_at=at,
            published_at=None,
            valid_as_of=at,
            records=records,
            complete=True,
            limitations=['한 거래소의 최근 체결·거래량이며 전 시장 대표 가격·총거래량이 아니다.'],
        )
    if contract == 'deribit_ticker_v1':
        envelope = json_document(response)
        doc = envelope['result']
        if (
            envelope.get('testnet') is not False
            or doc['instrument_name'] != candidate['identity']
            or doc['state'] != 'open'
        ):
            raise SourceError('wrong instrument, testnet or closed derivatives market')
        timestamp = doc['timestamp']
        if isinstance(timestamp, bool) or not isinstance(timestamp, int):
            raise SourceError('invalid exchange timestamp')
        at = datetime.fromtimestamp(timestamp / 1000, timezone.utc).isoformat()
        scope = 'Deribit BTC-PERPETUAL inverse USD contract settled in BTC'
        records = [
            scalar(
                doc,
                '/funding_8h',
                'Deribit 무기한 선물 8시간 funding 비율',
                definition(
                    'DERIBIT_BTC_PERPETUAL_FUNDING_8H',
                    'fraction',
                    'reported_8h',
                    None,
                    scope,
                    'exchange_reported_not_annualized',
                ),
            ),
            scalar(
                doc,
                '/open_interest',
                'Deribit 무기한 선물 미결제약정',
                definition(
                    'DERIBIT_BTC_PERPETUAL_OPEN_INTEREST',
                    'USD',
                    'exchange_snapshot',
                    'USD',
                    scope,
                    'inverse_contract_USD_notional',
                ),
            ),
            scalar(
                doc,
                '/mark_price',
                'Deribit 무기한 선물 평가 가격',
                definition(
                    'DERIBIT_BTC_PERPETUAL_MARK_PRICE',
                    'USD_per_BTC',
                    'exchange_snapshot',
                    'USD',
                    scope,
                    'mark_price_not_spot_or_execution_price',
                ),
                positive=True,
            ),
        ]
        for record in records:
            record['locator'] = record['locator'].replace('json_scalar:/', 'json_scalar:/result/', 1)
        if _decimal(records[1]['quote'], 'open interest') < 0:
            raise SourceError('negative open interest')
        for record in records:
            record['observed_at'] = at
        return dict(
            observed_at=at,
            published_at=None,
            valid_as_of=at,
            records=records,
            complete=True,
            limitations=[
                '한 거래소·한 계약의 관측이다. 전체 레버리지·청산 규모나 포지션 방향을 증명하지 않는다.',
                'funding은 매수·매도 보유자가 주고받는 비용 비율이며 연율·미래 수익률이 아니다.',
            ],
        )
    if contract == 'farside_daily_table_v1':
        html = html_records(response)
        visible = _visible_html(_decode(response.body, response.content_type))
        if 'Bitcoin ETF Flow (US$m)' not in visible:
            raise SourceError('BTC flow table title/unit not confirmed')
        tables = [t for t in html.tables if any('IBIT' in r and 'FBTC' in r for r in t)]
        if len(tables) != 1:
            raise SourceError('unambiguous Bitcoin ETF table required')
        table = tables[0]
        header = next(r for r in table if 'IBIT' in r and 'FBTC' in r)
        # Farside uses a Total cell spanning the logo/ticker/fee header rows.
        if 'Total' not in header and table[0][-1:] == ['Total'] and len(table[0]) == len(header) + 1:
            header = [*header, 'Total']
        elif header[-1:] == [''] and table[0][-1:] == ['Total'] and len(table[0]) == len(header):
            header = [*header[:-1], 'Total']
        if header[-1:] != ['Total'] or header.count('Total') != 1:
            raise SourceError('total column not confirmed')
        rows = []
        for row in table:
            if row and re.fullmatch(r'\d{2} [A-Z][a-z]{2} \d{4}', row[0]):
                if len(row) != len(header):
                    raise SourceError('ETF row/header columns disagree')
                at = datetime.strptime(row[0], '%d %b %Y').replace(tzinfo=timezone.utc)
                if any(not re.fullmatch(r'-|\(?[\d,]+(?:\.\d+)?\)?', x) for x in row[1:]):
                    raise SourceError('unrecognized ETF cell; do not guess missing values')
                rows.append((at, row))
        if not rows or len({at for at, _ in rows}) != len(rows):
            raise SourceError('missing or duplicate flow observation dates')
        # A newer partial row replaces an older complete row for current research.
        # We never quietly relabel the older complete total as today's value.
        at, row = max(rows)
        complete = '-' not in row[1:]
        d = definition(
            'US_SPOT_BTC_ETF_DAILY_NET_FLOW',
            'USD_million',
            at.date().isoformat(),
            'USD',
            'US spot Bitcoin ETFs reported by Farside',
            'complete_row_provider_reported_not_issuer_confirmed' if complete else 'partial_row_not_final_total',
        )
        record = dict(
            quote=' '.join(row),
            locator='table:Bitcoin ETF Flow (US$m)/' + row[0] + '/Total',
            definition=d,
            extraction='dated_table_total_v1',
            label='미국 현물 BTC ETF 일별 순유입' if complete else '미국 현물 BTC ETF 잠정 합계 (미완성 행)',
            limitations=['발행사별 원자료의 독립 교차 확인을 완료하지 않은 데이터 제공자 집계다.'],
        )
        missing = [header[i] for i, cell in enumerate(row) if cell == '-']
        return dict(
            observed_at=at.isoformat(),
            published_at=None,
            valid_as_of=at.isoformat(),
            records=[record],
            complete=complete,
            missing_columns=missing,
            table_columns=header,
            canonical=html.canonical,
            limitations=[
                '순유입은 현금 유입·유출 집계이며 가격 상승·적정 가치의 증명이 아니다.',
                *(
                    ['누락 ETF: ' + ', '.join(missing) + '; 잠정 합계를 전체 확정 순유입으로 사용하지 않는다.']
                    if missing
                    else []
                ),
            ],
        )
    if contract == 'hn_comment_v1':
        doc = json_document(response)
        if (
            doc.get('type') != 'comment'
            or doc.get('dead')
            or doc.get('deleted')
            or str(doc.get('id')) != candidate['identity']
        ):
            raise SourceError('missing, deleted, dead or wrong community item')
        paragraphs = [_visible_html(p) for p in re.split(r'<p(?:\s[^>]*)?>', doc['text'], flags=re.I)]
        relevant = [
            p
            for p in paragraphs
            if re.search(r'\bbitcoin\b|\bBTC\b', p, re.I)
            and re.search(
                r'\b(?:price|ETF|inflow|outflow|risk|value|supply|scarcity|inflation|ponzi|invest|bull|bear|demand)\w*\b',
                p,
                re.I,
            )
        ]
        text = next((p for p in relevant if 0 < len(p) <= 1100), '')
        if not text:
            raise SourceError('opened comment is not relevant investment discussion')
        if len(text) > 1100 or re.search(
            r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|\bbc1[a-z0-9]{20,}|\brésumé\b|\bremote:\s*yes\b', text, re.I
        ):
            raise SourceError('community excerpt is too long or contains unnecessary personal/contact data')
        timestamp = doc['time']
        if isinstance(timestamp, bool) or not isinstance(timestamp, int):
            raise SourceError('invalid community publication time')
        at = datetime.fromtimestamp(timestamp, timezone.utc).isoformat()
        d = definition(
            'OBSERVED_BTC_COMMUNITY_NARRATIVE',
            'text',
            'publication_at_' + at,
            None,
            'purpose_sampled_Hacker_News_comment',
            'utterance_not_verified_financial_fact',
        )
        return dict(
            observed_at=at,
            published_at=at,
            valid_as_of=at,
            records=[
                dict(
                    quote=text,
                    locator='json_html:/text',
                    definition=d,
                    extraction=None,
                    label='관측된 Bitcoin 투자 토론',
                    limitations=['발언 존재만 확인한다. 내용·대표성은 확인되지 않았다.'],
                )
            ],
            complete=True,
            limitations=['목적 표집한 공개 토론이다. 검색 순위·좋아요·반복은 독립적인 사실 근거가 아니다.'],
        )
    raise SourceError('no reviewed document contract for this evidence category')
