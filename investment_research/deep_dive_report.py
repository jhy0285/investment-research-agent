"""Korean Deep Dive, rendered only from pinned evidence and explicit metrics."""

from __future__ import annotations

from decimal import Decimal
from zoneinfo import ZoneInfo

from .macro_report import _number
from .opportunity_report import _anchor, _target, _text
from .sources import SourceError, _time

DEEP_DIVE_REPORT_VERSION = 'deep_dive_report_v1'
HEADINGS = (
    ('conclusions', '핵심 결론'),
    ('priced_expectations', '지금 시장이 기대하는 것'),
    ('denominator', 'Forward P/E의 분모는 믿을 만한가?'),
    ('revisions', '예상치가 어느 방향으로 바뀌고 있는가?'),
    ('actual_results', '실제 기업 실적은 기대를 따라가고 있는가?'),
    ('ai_chain', 'AI 투자 사이클'),
    ('concentration', '지수를 보유할 때의 집중 노출'),
    ('treasury', '국채라는 대안'),
    ('bull_case', '미국주식에 가장 강한 Bull Case'),
    ('base_case', 'Base Case에서 필요한 조건'),
    ('bear_case', '미국주식에 가장 강한 Bear Case'),
    ('community', 'Community에서는 무엇을 믿고 있는가'),
    ('narrative_gaps', 'Narrative와 Reality의 차이'),
    ('reassessment', '무엇이 발생하면 판단이 달라지는가'),
    ('current_judgment', '현재 내릴 수 있는 판단'),
    ('korean_context', '한국 투자자에게 의미하는 것'),
    ('easy', '초간단 설명'),
)
TABLE_SECTIONS = {
    'VALUATION': 'denominator',
    'REVISIONS': 'revisions',
    'QUARTERS': 'actual_results',
    'ACTUALS': 'actual_results',
    'CASH': 'ai_chain',
    'DEPRECIATION': 'ai_chain',
    'CAPEX_GUIDANCE': 'ai_chain',
    'CONCENTRATION': 'concentration',
    'TREASURY': 'treasury',
    'YIELD_GAPS': 'treasury',
}
UNITS = {
    'ratio': '배',
    'percent': '%',
    'percentage_points': '%p',
    'USD_million': '백만 USD',
    'USD_billion': '십억 USD',
    'USD_per_share': 'USD/주',
    'count': '개',
}
FORMULAS = {
    'earnings_yield_v1': '100 / P/E',
    'descriptive_yield_gap_v1': '100 / P/E - 같은 관측일 nominal CMT Treasury yield',
    'cash_residual_v1': '영업현금흐름 + 음수로 기록된 현금 PP&E 지출',
}


class _Citations:
    def __init__(self, run):
        ids = (
            {s.id for s in run.case.sources}
            | {e.id for e in run.case.evidence}
            | {f['id'] for f in run.facts}
            | {m.id for m in run.metrics}
        )
        ids.update(c['id'] for c in run.review.data['calculations'])
        ids.update(f['source_evidence_id'] for f in run.facts)
        ids.update(ref for items in run.sections.values() for item in items for ref in item['evidence_ids'])
        ids.update(ref for t in run.review.data['tables'] for row in t['rows'] for cell in row for ref in cell['refs'])
        self.numbers = {identifier: index + 1 for index, identifier in enumerate(sorted(ids))}

    def ref(self, identifier):
        return '[' + str(self.numbers[identifier]) + '](#' + _target(identifier) + ')'

    def refs(self, identifiers):
        return ', '.join(self.ref(i) for i in identifiers) or '추가 자료 필요'


def _check(run):
    evidence = {e.id: e for e in run.case.evidence}
    metrics = {m.id: m for m in run.result.metrics}
    if run.result.case != run.case:
        raise SourceError('Deep Dive result/case mismatch')
    for fact in run.facts:
        item = evidence.get(fact['id'])
        if fact['status'] == 'available' and (
            item is None
            or item.value != Decimal(fact['value'])
            or item.unit != fact['unit']
            or item.currency != fact['currency']
            or item.period != fact['window']
            or item.text != fact['quote_context']
        ):
            raise SourceError('Deep Dive quoted scalar/result mismatch')
        if fact['status'] == 'withheld' and item is not None:
            raise SourceError('withheld scalar must not remain usable evidence')
    for metric in run.metrics:
        if (
            metrics.get(metric.id) != metric
            or not metric.input_ids
            or any(ref not in evidence for ref in metric.input_ids)
        ):
            raise SourceError('Deep Dive metric/result/input mismatch')
    for item in run.case.evidence:
        if item.provenance is None or not item.provenance.snapshot_id or item.provenance.match_status != 'matched':
            raise SourceError('Deep Dive evidence must retain matched snapshot provenance')


def _statement(item, links):
    if item['status'] == 'withheld':
        return '자료·시점 조건이 부족해 이 문장 채택을 보류함 (' + links.refs(item['withheld_ids']) + ')'
    prefix = '[관측된 발언 · 내용 미검증] ' if item['role'] == 'narrative' else ''
    return prefix + _text(item['text']) + ' (' + links.refs(item['evidence_ids']) + ')'


def _cell(run, cell, links):
    refs = cell['refs']
    if not cell['text']:
        if len(refs) != 1:
            raise SourceError('numeric cell requires one quoted scalar or computed metric')
        identifier = refs[0]
        facts = {f['id']: f for f in run.facts}
        metrics = {m.id: m for m in run.metrics}
        if identifier in facts:
            f = facts[identifier]
            prefixes = {'reported': '', 'above': '&gt;', 'below': '&lt;', 'approximate': '약 '}
            value = prefixes[f.get('qualifier', 'reported')] + format(Decimal(f['value']), ',f')
            unit = UNITS[f['unit']]
            if f['status'] != 'available':
                return '채택 보류 (' + links.ref(identifier) + ')'
        elif identifier in metrics:
            m = metrics[identifier]
            value = _number(m.value)
            unit = UNITS.get(m.unit, _text(m.unit))
        elif identifier in {c['id'] for c in run.review.data['calculations']}:
            return '계산 보류 (' + links.ref(identifier) + ')'
        else:
            raise SourceError('financial table must reference a typed scalar/metric, not a raw passage')
        return value + ' ' + unit + ' (' + links.ref(identifier) + ')'
    evidence = {e.id: e for e in run.case.evidence}
    sources = {s.id: s for s in run.case.sources}
    available = {m.id for m in run.metrics}
    for identifier in refs:
        if identifier in available:
            continue
        e = evidence.get(identifier)
        if (
            e is None
            or e.provenance.freshness != 'fresh'
            or _time(sources[e.source_id].provenance.retrieved_at) > run.review.as_of
        ):
            return '자료·시점 조건 부족 (' + links.refs(refs) + ')'
    return _text(cell['text']) + (' (' + links.refs(refs) + ')' if refs else '')


def _table(run, table, links):
    lines = [
        '',
        '### ' + _text(table['title']),
        '',
        '| ' + ' | '.join(_text(c) for c in table['columns']) + ' |',
        '| ' + ' | '.join('---' for _ in table['columns']) + ' |',
    ]
    lines.extend('| ' + ' | '.join(_cell(run, cell, links) for cell in row) + ' |' for row in table['rows'])
    lines.append('')
    lines.extend('- ' + _text(note) for note in table['notes'])
    return lines


def render_deep_dive_report(run):
    _check(run)
    data = run.review.data
    cutoff = run.review.as_of
    links = _Citations(run)
    if run.parent is None:
        entry = '- 지정한 미국 주식 질문에서 직접 시작한 Deep Dive다. Opportunity Scan이나 후보 선정을 선행 조건으로 요구하지 않는다.'
    elif any(row['asset_id'] == 'US_EQUITY' and row['priority'] == 'candidate' for row in run.parent.rows):
        entry = '- 기존 Opportunity Map의 미국 주식 후속 조사 후보에서 출발한다. 이전 연구의 입력·초안 해시와 사용자 맥락을 고정해 연결했다.'
    else:
        entry = '- 기존 Opportunity Map을 선택적 맥락으로 연결했다. 후보 선정 여부는 Deep Dive의 실행 조건이 아니다.'
    if 'profile' in data and run.parent is not None:
        entry = '- 기존 Opportunity Map을 선택적 맥락으로 연결하고 이 연구에 명시한 사용자 맥락을 사용한다. 후보 선정 여부는 실행 조건이 아니다.'
    lines = [
        '# 미국 주식 Deep Dive · 기대이익의 질과 Treasury 기회비용',
        '',
        '- 정보 기준: '
        + cutoff.isoformat()
        + ' (UTC) / '
        + cutoff.astimezone(ZoneInfo('Asia/Seoul')).isoformat()
        + ' (한국시간).',
        '- 질문: ' + _text(data['question']),
        entry,
        '- 작성자: '
        + _text(data['author'])
        + '; **근거에 연결한 연구 초안**이다. 원문 수치 전사·계산 확인과 경제적 해석의 검토를 구분한다.',
        '- 매수·매도 명령, 목표가격, 임의 점수, 포트폴리오 비중 및 미래 수익률 추정은 생성하지 않았다.',
        '- 표의 수치는 별도 근거 ID로 추적된다. 계산은 표시상 반올림하며, 정확한 입력·계산 값·원문은 부록과 manifest에 남긴다.',
        '',
    ]
    for key, title in HEADINGS:
        lines.extend(['## ' + title, ''])
        if key == 'current_judgment':
            lines.extend(['**' + _text(run.effective_judgment) + '** · 경제적 해석 초안', ''])
        lines.extend(('- ' if key != 'easy' else '') + _statement(item, links) for item in run.sections[key])
        for table in data['tables']:
            if TABLE_SECTIONS.get(table['id']) == key:
                lines.extend(_table(run, table, links))
        if key == 'community':
            lines.extend(['', '표본과 접근 한계:', ''])
            lines.extend('- ' + _text(n) for n in data['sampling_limits'])
        if key == 'korean_context':
            lines.extend(
                [
                    '',
                    '### 기존 거시 근거와 사용자 맥락',
                    '',
                    '| 원관측 | 관측일 | 값 | 근거 |',
                    '| --- | --- | --- | --- |',
                ]
            )
            for selection in run.integration.macro.snapshot.selections:
                item = selection.latest
                if selection.status == 'available' and item is not None:
                    lines.append(
                        '| '
                        + _text(selection.definition.name)
                        + ' | '
                        + item.observation_date.isoformat()
                        + ' | '
                        + _number(item.value)
                        + ' '
                        + _text(selection.definition.unit)
                        + ' | '
                        + links.ref(item.id)
                        + ' |'
                    )
                else:
                    lines.append('| ' + _text(selection.definition.name) + ' | 미확인 | 채택 보류 | 고정 거시 판본 |')
            lines.extend(['', '| 사용자 항목 | 정보 상태 | 입력 |', '| --- | --- | --- |'])
            for name, field in run.case.profile.fields.items():
                lines.append(
                    '| '
                    + _text(name)
                    + ' | '
                    + _text(field.status)
                    + ' | '
                    + _text(field.value if field.value is not None else 'UNKNOWN')
                    + ' |'
                )
        lines.append('')
    lines.extend(['## 비교 한계와 아직 모르는 것', ''])
    lines.extend('- ' + _text(n) for n in (*data['comparison_limits'], *data['unknowns']))
    lines.extend(
        [
            '',
            '## 다음 Deep Dive 하나',
            '',
            _text(data['next_research']),
            '',
            '제안만 하며 이번 과제에서 수행하지 않았다.',
            '',
            '## 부록 · 출처, 원문, 계산과 재현',
            '',
            '- 초안 SHA-256: ' + run.review.input_digest + '; 통합 입력 SHA-256: ' + run.input_digest + '.',
            '- 부모 Opportunity Map: ' + _text(str(data.get('parent'))) + '.',
            '- 출처·구절·숫자 일치는 범위가 제한된 확인이다. 금융 의미·가격 적정성·미래 수익은 자동 검증되지 않았다.',
            '- 사실 전사의 해석 상태는 pending, 경제적 주장 상태는 unverified로 유지한다. 원출처가 같은 자료는 독립 증거로 세지 않는다.',
        ]
    )
    for source in run.case.sources:
        p = source.provenance
        lines.extend(
            [
                '',
                _anchor(source.id),
                '### 출처 · ' + _text(source.id),
                '',
                '- ' + _text(p.publisher) + ' · ' + _text(source.name) + '; 유형: ' + _text(source.type.value) + '.',
                '- URL: [원문](<' + source.location + '>)',
                '- 공개: '
                + _text(p.published_at or 'UNKNOWN')
                + '; 관측: '
                + _text(p.observed_at or 'UNKNOWN')
                + '; 획득: '
                + _text(p.retrieved_at)
                + '; 상태: '
                + _text(p.status)
                + ' / '
                + _text(p.freshness)
                + '.',
                '- Snapshot: ' + _text(p.snapshot_id) + '; payload SHA-256: ' + _text(p.payload_sha256) + '.',
                '- 보존: '
                + _text(p.retention)
                + '; 이용 조건: '
                + _text(p.policy_url)
                + ' · '
                + _text(p.policy_note)
                + '.',
            ]
        )
    scalar_ids = {f['id'] for f in run.facts}
    for e in run.case.evidence:
        if e.id in scalar_ids:
            continue
        p = e.provenance
        lines.extend(
            [
                '',
                _anchor(e.id),
                '### 근거 · ' + _text(e.id),
                '',
                '- 출처: '
                + links.ref(e.source_id)
                + '; 분류: '
                + _text(e.kind)
                + '; 원문 확인: '
                + _text(e.verification.value)
                + '; 해석 검토: '
                + _text(e.interpretation.status.value)
                + '.',
                '- 원문: ' + _text(e.text),
                '- 위치: '
                + _text(e.locator)
                + '; 구절: '
                + _text(p.excerpt_id)
                + '; snapshot: '
                + _text(p.snapshot_id)
                + '.',
                '- 정의: ' + _text(str(p.definition)) + '; 시점 적합성: ' + _text(p.freshness) + '.',
            ]
        )
        lines.extend('- 한계: ' + _text(n) for n in e.limitations)
    for f in run.facts:
        lines.extend(
            [
                '',
                _anchor(f['id']),
                '### 원문 수치 · ' + _text(f['id']),
                '',
                '- ' + _text(f['label']) + '; 상태: ' + _text(f['status']) + '.',
                '- 관측: '
                + f['observed_at']
                + '; 범위: '
                + _text(f['entity'])
                + '; 기간: '
                + _text(f['window'])
                + '; 정의: '
                + _text(f['basis'])
                + '; 통화: '
                + _text(f['currency'])
                + '.',
                '- 원문과 정의: '
                + links.ref(f['source_evidence_id'])
                + '; 전사 토큰: '
                + _text(f['quote_token'])
                + '.',
            ]
        )
        if f['status'] == 'available':
            lines.append(
                '- 값: '
                + _text(f['value'])
                + ' '
                + _text(f['unit'])
                + '; 범위 표현: '
                + _text(f.get('qualifier', 'reported'))
                + '.'
            )
        else:
            lines.append('- 채택 보류: ' + _text(f['reason']) + '.')
    for m in run.metrics:
        lines.extend(
            [
                '',
                _anchor(m.id),
                '### 계산 · ' + _text(m.id),
                '',
                '- '
                + _text(m.label)
                + ': '
                + _text(m.value)
                + ' '
                + _text(m.unit)
                + '; 방법: '
                + _text(m.method)
                + '.',
                '- 입력: ' + links.refs(m.input_ids) + '.',
            ]
        )
        if m.method in FORMULAS:
            lines.append('- 공식: ' + _text(FORMULAS[m.method]) + '.')
        else:
            original = next(x for x in run.integration.macro.snapshot.metrics if x.id == m.id)
            lines.append('- 공식: ' + _text(original.formula) + '; 기간: ' + _text(original.observation_window) + '.')
        lines.extend('- 한계: ' + _text(n) for n in m.limitations)
    existing = (
        {s.id for s in run.case.sources} | {e.id for e in run.case.evidence} | scalar_ids | {m.id for m in run.metrics}
    )
    requested = {ref for items in run.sections.values() for item in items for ref in item['evidence_ids']}
    requested.update(ref for t in data['tables'] for row in t['rows'] for cell in row for ref in cell['refs'])
    requested.update(f['source_evidence_id'] for f in run.facts)
    requested.update(c['id'] for c in data['calculations'])
    for identifier in sorted(requested - existing):
        lines.extend(
            [
                '',
                _anchor(identifier),
                '### 채택 보류 · ' + _text(identifier),
                '',
                '원문 획득·시점·계산 조건이 부족하다. 수치와 관련 현재 주장을 채택하지 않았다.',
            ]
        )
    lines.extend(['', '### 무결성·접근 진단', ''])
    lines.extend('- ' + _text(n) for n in run.diagnostics)
    return '\n'.join(lines) + '\n'
