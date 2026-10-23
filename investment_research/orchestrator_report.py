"""Korean question-first reports and a navigable evidence/reasoning record."""

from dataclasses import asdict
from decimal import Decimal
import hashlib
from pathlib import Path
from zoneinfo import ZoneInfo

from .macro_report import _number
from .opportunity_report import _anchor, _target, _text
from .routing import ResearchMode
from .sources import SourceError, _time
from .query_understanding import constraint_labels

REPORT_VERSION = 'ask_report_v1'
EXPLANATORY_REPORT_VERSION = 'ask_report_explanatory_ko_v5'
EXPLANATORY_REPORT_VERSIONS = (
    'ask_report_explanatory_ko_v1',
    'ask_report_explanatory_ko_v2',
    'ask_report_explanatory_ko_v3',
    'ask_report_explanatory_ko_v4',
    EXPLANATORY_REPORT_VERSION,
)
STATUS_NAMES = {
    'available': '확보',
    'unavailable': '미확보',
    'policy_blocked': '접근·정책 제한',
    'changed': '검토한 구절이 현재 응답과 다름',
    'parse_error': '해석 실패',
    'timeout': '시간 초과',
    'fresh': '최신성 조건 충족',
    'stale': '오래된 자료',
    'future': '기준 시점 이후',
    'unknown': '시점 미확인',
}


def _current(run, evidence):
    if evidence.provenance is None or evidence.kind == 'observed_narrative':
        return False
    source = next(s for s in run.case.sources if s.id == evidence.source_id)
    return (
        evidence.provenance.freshness == 'fresh'
        and (not run.input.get('evidence_validation') or evidence.verification.value == 'supported_within_scope')
        and _time(source.provenance.retrieved_at) <= run.cutoff
        and (evidence.observed_at is None or evidence.observed_at <= run.cutoff.date())
    )


def _asset_evidence(run, identifier):
    series = {s.definition.canonical_id for s in run.macro.snapshot.selections} if run.macro else set()
    return tuple(
        e
        for e in run.case.evidence
        if identifier in e.asset_ids
        and e.provenance is not None
        and _current(run, e)
        and e.provenance.definition['measure'] not in series
    )


def _refs(ids):
    ids = tuple(ids)

    def label(identifier, index):
        if identifier.startswith('INSIGHT_'):
            name = '판단 근거'
        elif identifier.startswith(('MET_', 'CALC_', 'PORT_WEIGHT_', 'PORT_TOTAL', 'PORT_NET', 'PORT_CASH_NEEDS')):
            name = '계산 확인'
        else:
            name = '자료 확인'
        return name + ' ' + str(index + 1) if len(ids) > 1 else name

    return (
        ', '.join(
            '[' + label(identifier, index) + '](#' + _target(identifier) + ')' for index, identifier in enumerate(ids)
        )
        or '현재 확인 가능한 직접 근거 부족'
    )


def _insights(run):
    items = []
    for finding in run.findings:
        if finding['status'] == 'available_draft':
            items.append(
                dict(
                    id='INSIGHT_FINDING_' + finding['id'],
                    text=finding['text'],
                    evidence_ids=finding['evidence_ids'],
                    metric_ids=[],
                    role='interpretation_draft',
                    limitations=['검토 전 해석이며 원문의 경제적 의미를 자동 검증하지 않는다.'],
                    counterargument=finding['counterargument'],
                    reassessment=finding['reassessment'],
                )
            )
    for method in run.input['methods']:
        records = _asset_evidence(run, method['id'])
        refs = tuple(e.id for e in records)
        items.append(
            dict(
                id='INSIGHT_' + method['id'],
                text=method['scope_note'] + ' 현재 가격의 매력·미래 수익은 이 자료만으로 확정하지 않는다.',
                evidence_ids=list(refs),
                metric_ids=[],
                role='interpretation_draft',
                limitations=list(method['missing']),
                counterargument=method['bear_question'],
                reassessment=method['bull_question'],
            )
        )
    for task in run.input['tasks']:
        if task['mode'] == ResearchMode.COMPARE:
            refs = [
                e.id
                for e in run.case.evidence
                if any(identifier in e.asset_ids for identifier in task['method_ids']) and _current(run, e)
            ]
            items.append(
                dict(
                    id='INSIGHT_COMPARE_' + task['id'],
                    text='확보한 대안의 수익 원천·손실 경로·기간·통화는 다르다. 전체 우열과 개인 적절성은 확인한 범위 밖에서 유보한다.',
                    evidence_ids=refs,
                    metric_ids=[m.id for m in run.result.metrics if not m.id.startswith('PORT_')],
                    role='interpretation_draft',
                    limitations=task['unsupported'],
                    counterargument='금리 대안·성장 미달·유동성·실거주와 자금수요 조건이 비교를 바꿀 수 있다.',
                    reassessment='같은 기준의 현재 가격/현금흐름·투자기간·사용자 자금 제약을 확인한다.',
                )
            )
    if ResearchMode.PORTFOLIO_REVIEW in run.input['plan']['modes']:
        items.append(
            dict(
                id='INSIGHT_PORTFOLIO',
                text='제공된 보유 구성의 계산과 자산의 시장 매력, 추가 보유의 적절성은 별도 판단이다.',
                evidence_ids=[e.id for e in run.portfolio.evidence],
                metric_ids=[m.id for m in run.portfolio.metrics],
                role='self_reported_composition',
                limitations=list(run.portfolio.missing),
                counterargument='좋은 자산도 기존 노출·자금수요·부채에 따라 추가 보유가 적절하지 않을 수 있다.',
                reassessment='전체 보유와 평가 기준일·현금·부채·향후 자금수요·손실 감당 능력을 확인한다.',
            )
        )
    if run.input.get('semiconductor_coverage'):
        from .semiconductor_data import audit

        review = audit(run)
        items.append(
            dict(
                id='INSIGHT_SEMICONDUCTORS',
                text=review['reasoning'],
                evidence_ids=[
                    e.id
                    for e in run.case.evidence
                    if e.provenance and _current(run, e) and set(e.asset_ids) & {'SAMSUNG', 'SK_HYNIX'}
                ],
                metric_ids=[m.id for m in run.result.metrics if m.id.startswith('CALC_SEMI_')],
                role='conditional_comparison_draft',
                limitations=['원공시·회계 귀속·현재 주식 수·이익 지속성의 미검증'],
                counterargument='잠정 배수가 낮고 영업이익이 실제로 지속되면 상대 가격 매력이 성립할 수 있다.',
                reassessment='동일 기준 공시와 이익의 반복 가능성·현금 회수를 확인한다.',
            )
        )
    if run.input.get('scan'):
        from .scan import assess

        for row in assess(run)['universe']:
            items.append(
                dict(
                    id='INSIGHT_SCAN_' + row['asset_id'],
                    text=row['why_now'],
                    evidence_ids=row['evidence_ids'],
                    metric_ids=([row['momentum_metric_id']] if 'momentum_metric_id' in row else []),
                    role='conditional_research_priority_draft',
                    limitations=row['unknowns'],
                    counterargument=row['risk'],
                    reassessment=row['invalidate'],
                )
            )
    if run.input.get('commodity_coverage'):
        from .commodity_report import assessment

        for asset, review in assessment(run)['assets'].items():
            items.append(
                dict(
                    id='INSIGHT_COMMODITY_' + asset,
                    text=review['reasoning'],
                    evidence_ids=review['evidence_ids'],
                    metric_ids=review['metric_ids'],
                    role='interpretation_draft',
                    limitations=review['gaps'],
                    counterargument=review['counterargument'],
                    reassessment=review['reassessment'],
                )
            )
    return items


def _used_evidence(run):
    used = {e.id for e in run.case.evidence if e.provenance is not None and e.view != 'macro'}
    used.update(e.id for e in run.portfolio.evidence)
    used.update(identifier for metric in run.result.metrics for identifier in metric.input_ids)
    if run.input.get('scan', {}).get('method_version') in (
        'evidence_shortlist_v4',
        'evidence_shortlist_v5',
        'evidence_shortlist_v6',
        'evidence_shortlist_v7',
    ):
        from .scan import assess

        used.update(p['evidence_id'] for p in assess(run)['observations'])
    for finding in run.findings:
        used.update(finding['evidence_ids'])
    for claim in (*run.case.claims, *(run.deep.integration.case.claims if run.deep else ())):
        used.update((*claim.support_ids, *claim.counter_ids, *claim.context_ids))
    if run.macro:
        used.update(
            selection.latest.id
            for selection in run.macro.snapshot.selections
            if selection.status == 'available' and selection.latest is not None
        )
    return tuple(e for e in run.case.evidence if e.id in used)


def _unit(value):
    return {
        'KRW': '원',
        'KRW_per_USD': '원/달러',
        'percent': '%',
        'percentage_points': '%p',
        'ratio': '배',
        'count': '개',
        'USD_million': '백만 달러',
        'USD_billion': '십억 달러',
        'KRW_million': '백만 원',
        'KRW_trillion': '조 원',
        'KRW_per_share': '원/주',
    }.get(value, value)


def _limits(items):
    # Calculation configuration remains in the appendix/manifest. It is not
    # useful in the reader's investment decision table.
    return ' / '.join(item for item in items if not item.startswith('Decimal precision'))


def _guard_report(run):
    if not run.evidence_validation or not run.evidence_validation['quarantined_ids']:
        return []
    lines = [
        '## 추가 검증을 위해 격리한 자료',
        '',
        '원문을 보존하되 이상치·충돌·미완성 행은 계산·현재 판단·최소 자료 충족에서 제외했다. 같은 제공자의 반복 게시만으로 격리를 해제하지 않는다.',
        '',
    ]
    for r in run.evidence_validation['records']:
        if r['evidence_id'] in run.evidence_validation['quarantined_ids']:
            lines.append(
                '- '
                + _text(r['definition']['measure'])
                + ' '
                + _text(r['definition']['period'])
                + ': '
                + _text(r['status'])
                + ' · '
                + _text(' / '.join(r['reasons']))
                + ' ('
                + _refs([r['evidence_id']])
                + ')'
            )
    lines.append('')
    return lines


def observation_audit(run):
    """Show row date, release, capture and period as different assertions."""
    from .source_pipeline import observation_timing, load_pins, OBSERVATION_DATES_VERSION, _timestamp_day

    path = run.directory / 'source_plan.json'
    declared = {e['id']: e.get('observed_at') for e in load_pins(path)['evidence']} if path.exists() else {}
    financial = {f['id']: f for f in run.deep.facts if f['status'] == 'available'} if run.deep else {}
    sources = {s.id: s for s in run.case.sources}
    records = []
    for e in run.case.evidence:
        if e.provenance is None:
            continue
        p = sources[e.source_id].provenance
        d = e.provenance.definition
        if e.id in financial:
            t = dict(
                observed_at=financial[e.id]['observed_at'],
                precision='typed_financial_observation',
                period=d['period'],
                period_start=None,
                period_end=None,
                date_meaning='existing_quote_verified_financial_fact_date',
            )
        elif e.view == 'macro':
            t = dict(
                observed_at=e.observed_at.isoformat() if e.observed_at else None,
                precision='macro_' + d['period'],
                period=d['period'],
                period_start=None,
                period_end=None,
                date_meaning='native_macro_per_observation',
            )
        else:
            t = observation_timing(d['period'], declared.get(e.id))
        expected = _timestamp_day(t['observed_at'])
        status = (
            'matched'
            if expected is not None and e.observed_at == expected
            else 'unknown' if expected is None and e.observed_at is None else 'mismatch'
        )
        records.append(
            dict(
                evidence_id=e.id,
                measure=d['measure'],
                value=str(e.value) if e.value is not None else None,
                **t,
                evidence_observed_at=e.observed_at.isoformat() if e.observed_at else None,
                source_series_or_edition_at=p.observed_at,
                published_at=p.published_at,
                retrieved_at=p.retrieved_at,
                source_valid_as_of=p.valid_as_of,
                snapshot_id=e.provenance.snapshot_id,
                status=status,
                can_use_for_historical_change=expected is not None
                and status == 'matched'
                and t['precision'] != 'snapshot',
            )
        )
    return dict(
        method_version=OBSERVATION_DATES_VERSION,
        records=records,
        mismatched_ids=[r['evidence_id'] for r in records if r['status'] == 'mismatch'],
        unknown_ids=[r['evidence_id'] for r in records if r['status'] == 'unknown'],
        meaning='Rows use their own verified calendar label; source edition, release, retrieval and validity are not substitutes.',
    )


def _check(run):
    if run.case != run.result.case:
        raise SourceError('ask result/case mismatch')
    evidence = {e.id: e for e in run.case.evidence}
    if run.input.get('observation_dates_version') and observation_audit(run)['mismatched_ids']:
        raise SourceError('row observation date disagrees with its verified period')
    ids = [s.id for s in run.case.sources] + list(evidence) + [m.id for m in run.result.metrics]
    if len(ids) != len(set(ids)):
        raise SourceError('ambiguous ask report identifiers')
    for metric in run.result.metrics:
        if not metric.input_ids or any(identifier not in evidence for identifier in metric.input_ids):
            raise SourceError('ask metric inputs are not traceable')
        if run.evidence_validation and set(metric.input_ids) & set(run.evidence_validation['quarantined_ids']):
            raise SourceError('quarantined evidence cannot drive an ask calculation')
    for e in run.case.evidence:
        if e.provenance is not None and e.provenance.match_status != 'matched':
            raise SourceError('ask evidence must retain a matched snapshot')


def research_status(run):
    if run.input['plan']['clarifications']:
        return 'needs_clarification'
    if tuple(run.input['plan']['modes']) == (ResearchMode.PORTFOLIO_REVIEW,) and run.portfolio.status == 'needs_input':
        return 'needs_input'
    if not run.input['methods'] and ResearchMode.PORTFOLIO_REVIEW not in run.input['plan']['modes']:
        return 'unsupported'
    if any(task['unsupported'] or task['candidate_dependent'] for task in run.input['tasks']):
        return 'partial'
    if (
        any(method['missing'] for method in run.input['methods'])
        or run.portfolio.missing
        and ResearchMode.PORTFOLIO_REVIEW in run.input['plan']['modes']
    ):
        return 'partial'
    return 'completed'


def _unresolved(run):
    notes = list(run.input['unresolved'])
    if run.discovery:
        notes.extend(need['label'] + ': ' + gap for need in run.discovery['needs'] for gap in need['gaps'])
    for source in run.case.sources:
        p = source.provenance
        if p and (p.status != 'available' or p.freshness not in ('fresh', 'per_observation')):
            notes.append(
                source.name
                + ': '
                + STATUS_NAMES.get(p.status, p.status)
                + ' / '
                + STATUS_NAMES.get(p.freshness, p.freshness)
                + '; 영향을 받는 현재 주장·계산을 제한한다.'
            )
    if run.macro:
        for selection in run.macro.snapshot.selections:
            if selection.status != 'available':
                notes.append(selection.definition.name + ': 현재 관측 채택 보류 (' + selection.status + ')')
    if ResearchMode.PORTFOLIO_REVIEW in run.input['plan']['modes']:
        notes.extend('사용자 입력: ' + item for item in run.portfolio.missing)
    return list(dict.fromkeys(notes))


def _task_results(run):
    records = []
    for task in run.input['tasks']:
        if task['candidate_dependent']:
            status = 'awaiting_supported_candidate'
        elif task['mode'] == ResearchMode.PORTFOLIO_REVIEW:
            status = run.portfolio.status
        elif task['unsupported']:
            status = 'partial' if task['method_ids'] else 'unsupported'
        elif not task['method_ids']:
            status = 'needs_clarification'
        else:
            status = (
                'partial'
                if any(m['missing'] for m in run.input['methods'] if m['id'] in task['method_ids'])
                else 'completed'
            )
        records.append(dict(task_id=task['id'], mode=task['mode'], status=status, method_ids=task['method_ids']))
    return records


def _query_report(run):
    query = run.input['plan'].get('understanding')
    if not query:
        return []  # Historical v2/v3 reports keep their original bytes.
    names = {
        'opportunity_scan': '여러 자산군의 기회 탐색',
        'asset_deep_dive': '지정 대상 심층 조사',
        'compare': '명시한 대안 비교',
        'portfolio_review': '실제 보유 검토',
    }
    lines = ['## 질문의 목적과 조사 범위', '', '조사 목적: ' + ' + '.join(names[m] for m in query['intent']) + '.', '']
    if query['scope'] == 'broad_cross_asset':
        lines.extend(['특정 자산을 먼저 지정할 필요 없이 여러 관련 자산군에서 더 조사할 영역을 찾는다.', ''])
    for subject in query['assets_or_alternatives']:
        details = constraint_labels(subject)
        lines.append('- ' + _text(subject['label']) + (' — ' + _text('; '.join(details)) if details else ''))
    for field, label in (
        ('investment_purpose', '자금 목적'),
        ('time_context', '시점'),
        ('user_constraints', '명시한 조건'),
        ('strategies', '전략'),
    ):
        if query[field]:
            lines.append('- ' + label + ': ' + _text(' / '.join(dict.fromkeys(d['raw_text'] for d in query[field]))))
    lines.append('')
    gaps = [
        c for task in run.input['tasks'] for c in task.get('condition_coverage', []) if c['status'] == 'unavailable'
    ]
    if gaps or query['data_limits']:
        lines.append(
            '현재 다음 조건을 지원할 데이터가 부족하다. 질문의 조건은 유지하며 다른 국가·만기·지역 자료로 대신하지 않는다.'
        )
        lines.append('')
        for gap in gaps:
            lines.append('- ' + _text(gap['subject']['label']) + ': 현재 이 조건을 지원할 데이터가 부족하다.')
        for limit in query['data_limits']:
            lines.append('- ' + _text(limit['raw_text']) + ': ' + _text(limit['reason']))
        lines.append('')
    if any(p['kind'] == 'new_capital_allocation' for p in query['investment_purpose']):
        lines.extend(
            [
                '신규자금의 대안을 비교한다. 투자기간·필요 자금·기존 보유가 확인되지 않으면 개인에게 적절한 배분은 유보한다.',
                '',
            ]
        )
    return lines


def report_version(run):
    style = run.input.get('report_style')
    if style is None:
        return REPORT_VERSION
    if style not in EXPLANATORY_REPORT_VERSIONS:
        raise SourceError('unsupported ask report style')
    return style


def render_ask_report(run):
    """New questions get explanatory prose; pinned reports keep their style."""
    if report_version(run) == REPORT_VERSION:
        return _render_legacy_ask_report(run)
    from .report_explanations import render_explanatory_report

    report = render_explanatory_report(run, _render_legacy_ask_report(run))
    if run.investment and report_version(run) == EXPLANATORY_REPORT_VERSION:
        from .decision_report import render_decision

        report = render_decision(run.investment) + '\n' + report
    return report


def _render_legacy_ask_report(run):
    _check(run)
    modes = run.input['plan']['modes']
    insights = _insights(run)
    lines = [
        '# 투자 질문에 대한 조사 결과',
        '',
        '**질문:** ' + _text(run.input['question']),
        '',
        '정보 기준: '
        + run.cutoff.isoformat()
        + ' / '
        + run.cutoff.astimezone(ZoneInfo('Asia/Seoul')).isoformat()
        + ' (한국시간).',
        '',
        '## 결론',
        '',
    ]
    if run.input['synthetic']:
        lines.extend(['**합성 검증 자료가 포함된 예제다. 실제 투자 판단에 사용하지 않는다.**', ''])
    if ResearchMode.PORTFOLIO_REVIEW in modes:
        if run.portfolio.status == 'needs_input':
            lines.append('실제 보유 내역과 재무 제약이 없어 포트폴리오의 구성·안전성·적절성을 판단할 수 없다.')
        elif run.portfolio.metrics:
            lines.append(
                '제공된 보유표로 계산 가능한 구성은 확인했다. 이 계산이 적정 배분이나 전체 포트폴리오의 안전성을 증명하지는 않는다. ('
                + _refs(['INSIGHT_PORTFOLIO'])
                + ')'
            )
        else:
            lines.append('확인되지 않은 보유 범위·현금·평가액 때문에 전체 비중 계산을 보류했다.')
    if run.input['methods']:
        lines.append(
            '확보한 자료와 남은 공백을 함께 보면, 현재 가격에서 투자 매력이 충분하다고 확정할 근거는 부족하다. 조사 가능한 부분의 결과를 아래에 정리했다.'
        )
    elif ResearchMode.PORTFOLIO_REVIEW not in modes:
        lines.append(
            '질문의 대상 또는 필요한 자료 연결을 확인하지 못해 투자 판단을 유보한다. 지원하지 않는 분석을 다른 자산의 자료로 대신하지 않았다.'
        )
    lines.extend(
        [
            '',
            (
                '이 부분은 자료 조사 단계다. 최종 행동·등급·신규 자금 배분은 보고서 첫 화면의 투자 결론을 따른다.'
                if run.investment
                else '매수·매도 명령·미래 수익률·투자 순위·최적 비중은 생성하지 않았다. 결론 유보만으로 현금이 우월하다고 판단하지 않는다.'
            ),
            '',
        ]
    )
    lines.extend(_query_report(run))
    if run.input.get('korean_coverage'):
        from .korean_report import korean_report

        lines.extend(korean_report(run))
    findings = [f for f in run.findings if f['status'] == 'available_draft']
    if findings:
        lines.extend(['## 원자료에서 확인한 핵심 단서', ''])
        for finding in findings[:5]:
            lines.append('- ' + _text(finding['text']) + ' (' + _refs(['INSIGHT_FINDING_' + finding['id']]) + ')')
        lines.extend(
            [
                '',
                '위 설명은 확인한 원문에 연결된 해석 초안이다. 미래 수익·가격 매력이나 가설 전체의 진실을 확정한 결과는 아니다.',
                '',
            ]
        )
    if run.discovery:
        lines.extend(_discovery_report(run))
    lines.extend(_guard_report(run))
    unavailable = [s for s in run.case.sources if s.provenance and s.provenance.status != 'available']
    if unavailable:
        lines.extend(['## 확보하지 못한 중요한 자료', ''])
        for source in unavailable:
            lines.append(
                '- '
                + _text(source.name)
                + ': '
                + _text(STATUS_NAMES.get(source.provenance.status, source.provenance.status))
                + ' ('
                + _refs([source.id])
                + '). 관련 판단을 제한한다.'
            )
        lines.append('')
    if run.input['plan']['clarifications']:
        lines.extend(['## 먼저 확인할 질문', ''])
        lines.extend('- ' + _text(note) for note in run.input['plan']['clarifications'])
        lines.append('')
    if ResearchMode.OPPORTUNITY_SCAN in modes:
        lines.extend(
            [
                '## 어떤 영역을 더 조사할 이유가 있나',
                '',
                '| 영역 | 현재 확보한 직접 근거 | 다음 검증 질문 |',
                '| --- | --- | --- |',
            ]
        )
        for method in run.input['methods']:
            refs = [e.id for e in _asset_evidence(run, method['id'])]
            lines.append(
                '| ' + _text(method['label']) + ' | ' + _refs(refs) + ' | ' + _text(method['bull_question']) + ' |'
            )
        lines.extend(
            [
                '',
                '현재 확보 범위에서 투자 대상을 억지로 선정하지 않았다. 관망하며 확인할 조건을 남긴다. 현금의 계약금리·구매력·기회비용도 따로 확인해야 한다.',
                '',
            ]
        )
    methods = {item['id']: item for item in run.input['methods']}
    for task in run.input['tasks']:
        if task['mode'] == ResearchMode.ASSET_DEEP_DIVE:
            if task['candidate_dependent']:
                lines.extend(
                    [
                        '## 후속 심층 조사 대상',
                        '',
                        '근거가 충분한 투자 후보를 강제로 만들지 않았다. 현재 자료로 후보 선정이 유보되어 자동 후속 조사는 수행하지 않았다.',
                        '',
                    ]
                )
            for identifier in task['method_ids']:
                item = methods[identifier]
                records = _asset_evidence(run, identifier)
                lines.extend(
                    [
                        '## ' + _text(item['label']) + '를 어떻게 봐야 하나',
                        '',
                        _text(item['economics']),
                        '',
                        _text(item['scope_note']) + ' (' + _refs(['INSIGHT_' + identifier]) + ')',
                        '',
                        '왜 중요한가: ' + _text(item['downside']),
                        '',
                        '**상승 논리를 검증할 질문:** ' + _text(item['bull_question']),
                        '',
                        '**가장 강한 반대 질문:** ' + _text(item['bear_question']),
                        '',
                        '현재 확보한 직접 근거: ' + _refs([e.id for e in records]),
                        '',
                    ]
                )
                for finding in findings:
                    if identifier in finding['asset_ids']:
                        lines.extend(
                            [
                                _text(finding['text']) + ' (' + _refs(['INSIGHT_FINDING_' + finding['id']]) + ')',
                                '',
                                '반대 근거·대안 설명: ' + _text(finding['counterargument']),
                                '',
                                '더 확인할 조건: ' + _text(finding['reassessment']),
                                '',
                            ]
                        )
                lines.extend(
                    [
                        '',
                        '판단이 달라질 조건: 아래 누락 원자료를 확보하고 지지·반대 논리의 의미를 함께 검토해야 한다.',
                        '',
                    ]
                )
                lines.extend('- ' + _text(note) for note in item['missing'])
                lines.append('')
        if task['mode'] == ResearchMode.COMPARE:
            lines.extend(
                [
                    '## 대안을 비교하면 무엇이 다른가',
                    '',
                    '| 대안 | 수익의 경제적 원천 | 주요 손실 경로 | 고유하게 더 확인할 자료 |',
                    '| --- | --- | --- | --- |',
                ]
            )
            for index, subject in enumerate(task['subjects']):
                label = subject['label']
                matching = methods.get(task['subject_method_ids'][index])
                if matching:
                    lines.append(
                        '| '
                        + _text(label)
                        + ' | '
                        + _text(matching['economics'])
                        + ' | '
                        + _text(matching['downside'])
                        + ' | '
                        + _text(' / '.join(matching['missing']))
                        + ' |'
                    )
                else:
                    lines.append(
                        '| '
                        + _text(label)
                        + ' | 고유 자료 미확보 | 비교할 손실 경로의 원자료 필요 | 다른 대안 자료로 대체하지 않음 |'
                    )
            lines.extend(
                [
                    '',
                    '공통 판단 기준은 같은 자금의 사용 시점·통화·유동성·손실 경로·기회비용이다. valuation(가격 대비 경제적 가치)은 해당 자산에 맞는 정의로만 사용한다.',
                    '',
                    '국채 이자·주식 이익수익률·부동산 임대수익·crypto의 수요 가설은 동일한 미래 수익률이 아니다. 가격·기간·세금·계좌와 사용자 조건이 부족하면 전체 우열을 유보한다. ('
                    + _refs(['INSIGHT_COMPARE_' + task['id']])
                    + ')',
                    '',
                ]
            )
        if task['unsupported']:
            lines.extend(['## 이번에 조사하지 못한 부분', ''])
            if run.input['plan'].get('understanding'):
                lines.extend(
                    '- '
                    + _text(label)
                    + ': 명시한 조건을 지원할 자료 연결이 없다. 현재 이 조건을 지원할 데이터가 부족하다.'
                    for label in task['unsupported']
                )
            else:
                lines.extend(
                    '- '
                    + _text(label)
                    + ': 검토한 고유 출처·방법 연결이 없다. 현재 가격/실적·기간·상품 정의와 공식 자료 연결을 추가해야 한다.'
                    for label in task['unsupported']
                )
            lines.append('')
    if run.deep:
        available = [f for f in run.deep.facts if f['status'] == 'available']
        if available:
            lines.extend(
                [
                    '## 원문에서 확인한 가격·이익·금리 자료',
                    '',
                    'P/E는 주가가 이익의 몇 배인지 나타낸다. forward는 앞으로 예상되는 이익, trailing은 이미 기록된 이익이다. FY1은 다음 회계연도라 앞으로의 일정 기간과 정의가 다를 수 있다.',
                    '',
                    '| 항목 | 값 | 관측일 | 근거 |',
                    '| --- | --- | --- | --- |',
                ]
            )
            for fact in available:
                lines.append(
                    '| '
                    + _text(fact['label'])
                    + ' | '
                    + _number(Decimal(fact['value']))
                    + ' '
                    + _text(_unit(fact['unit']))
                    + ' | '
                    + fact['observed_at']
                    + ' | '
                    + _refs([fact['id']])
                    + ' |'
                )
            lines.extend(
                [
                    '',
                    '관측일·분모·기간이 다른 값은 같은 배수·수익률로 합치지 않는다. 이익 전망·실제 이익·현재 금리는 서로 다른 종류의 자료다.',
                    '',
                ]
            )
    if run.result.metrics:
        lines.extend(['## 확인한 계산과 현재 비교 수치', '', '| 항목 | 값 | 의미와 한계 |', '| --- | --- | --- |'])
        for metric in run.result.metrics:
            lines.append(
                '| '
                + _text(metric.label)
                + ' | '
                + _number(metric.value)
                + ' '
                + _text(_unit(metric.unit))
                + ' ('
                + _refs([metric.id])
                + ') | '
                + _text(_limits(metric.limitations))
                + ' |'
            )
        lines.append('')
    if run.macro:
        lines.extend(['## 질문에 관련된 시장 환경', '', '| 관측 | 관측일 | 값 | 근거 |', '| --- | --- | --- | --- |'])
        for selection in run.macro.snapshot.selections:
            if selection.status == 'available' and selection.latest is not None:
                obs = selection.latest
                lines.append(
                    '| '
                    + _text(selection.definition.name)
                    + ' | '
                    + obs.observation_date.isoformat()
                    + ' | '
                    + _number(obs.value)
                    + ' '
                    + _text(_unit(selection.definition.unit))
                    + ' | '
                    + _refs([obs.id])
                    + ' |'
                )
            else:
                lines.append(
                    '| '
                    + _text(selection.definition.name)
                    + ' | 미확인 | 현재 값 채택 보류 | '
                    + _text(selection.status)
                    + ' |'
                )
        lines.append('')
    if ResearchMode.PORTFOLIO_REVIEW in modes:
        lines.extend(['## 내 보유에 적용할 수 있는 범위', ''])
        if run.input['portfolio']:
            lines.append(
                '보유 입력의 기준일: '
                + run.input['portfolio']['as_of']
                + '; 전체성: '
                + _text(run.input['portfolio']['coverage'])
                + '. 숫자는 사용자의 자기보고 평가액이다.'
            )
        if run.portfolio.largest_ids:
            names = {h['id']: h['name'] for h in run.input['portfolio']['holdings']}
            names['CASH'] = '현금'
            lines.extend(
                [
                    '',
                    '제공된 평가액 중 가장 큰 항목: '
                    + ', '.join(_text(names[i]) for i in run.portfolio.largest_ids)
                    + '. 이것만으로 과도한 집중이나 적정 비중을 확정하지 않는다.',
                ]
            )
        lines.extend(
            [
                '',
                '자산 자체의 매력과 이미 보유한 노출, 추가 자본이 전체 구성에 미치는 영향은 각각 확인해야 한다. ETF 구성·산업·통화·직업/주택 노출의 겹침을 아직 완전히 계산하지 않았다.',
            ]
        )
        if run.portfolio.missing:
            lines.extend(['', '누락되어 제한되는 판단:', ''])
            lines.extend(
                '- ' + _text(note) + ' — 전체 구성·자금 지급 가능성·개인 적절성에 관련된 판단을 제한한다.'
                for note in run.portfolio.missing
            )
        lines.append('')
    narratives = [e for e in _used_evidence(run) if e.kind == 'observed_narrative']
    if narratives:
        lines.extend(['## 공개 토론과 실제 근거의 차이', ''])
        for e in narratives:
            lines.append('- 관측된 공개 발언이며 내용은 미확인: ' + _text(e.text) + ' (' + _refs([e.id]) + ')')
        lines.extend(
            [
                '',
                '목적 표집한 소수 발언이다. 반복·인기는 사실이나 시장 전체의 생각을 증명하지 않는다. 연결된 주장의 검증 기록과 공식 자료를 함께 확인해야 한다.',
                '',
            ]
        )
        if run.discovery and run.discovery['community_verification']:
            lines.extend(['### 공개 발언의 사실 확인', ''])
            for check in run.discovery['community_verification']:
                names = {
                    'unverified': '미확인',
                    'supported_within_scope': '좁은 수치 범위에서 일치',
                    'contradicted_within_scope': '좁은 수치 범위에서 불일치',
                }
                lines.append(
                    '- '
                    + names.get(check['verification'], check['verification'])
                    + ': '
                    + _text(check['reason'])
                    + ' ('
                    + _refs([check['narrative_evidence_id'], *check['evidence_ids']])
                    + ')'
                )
            lines.append('')
    lines.extend(['## 한국 투자자에게 의미하는 것', ''])
    if not run.input['plan'].get('understanding') or any(method['macro_ids'] for method in run.input['methods']):
        lines.extend(
            [
                '달러 자산의 사업·계약 경제성과 원화로 평가한 환율 노출을 구분한다. 현재 USD/KRW(달러당 원화) 관측만으로 미래 환율을 예측하지 않는다.',
                '',
            ]
        )
    if run.input['plan'].get('understanding'):
        lines.extend(
            ['실제 상품·계좌·비용·과세·자금수요가 미확인이면 세후 우열과 개인 추가 투자 비중을 확정하지 않는다.', '']
        )
    else:
        lines.extend(
            ['실제 상품·환헤지·계좌·비용·과세 요건이 미확인이면 세후 순위와 개인 추가 투자 비중을 확정하지 않는다.', '']
        )
    lines.extend(['## 무엇을 더 확인하면 판단이 달라지나', ''])
    lines.extend('- ' + _text(note) for note in _unresolved(run))
    lines.extend(
        [
            '',
            '## 근거와 판단을 직접 확인하기',
            '',
            '원문 일치는 발언·공시 구절의 존재를 확인한다. 경제적 해석의 진실·투자 매력은 자동 검증되지 않았으며 검토 전 초안으로 유지한다. 오래되거나 시점이 맞지 않는 자료는 현재 판단에 채택하지 않는다.',
            '',
        ]
    )
    for item in insights:
        lines.extend(
            [
                _anchor(item['id']),
                '### 판단의 연결 · ' + _text(item['id']),
                '',
                _text(item['text']),
                '',
                '관련 근거: ' + _refs(item['evidence_ids']) + '; 계산: ' + _refs(item['metric_ids']),
                '',
                '반대 질문: ' + _text(item['counterargument']),
                '',
                '재검토 조건: ' + _text(item['reassessment']),
                '',
            ]
        )
    evidence = _used_evidence(run)
    for e in evidence:
        lines.extend(
            [
                _anchor(e.id),
                '### 근거 · ' + _text(e.id),
                '',
                _text(e.text),
                '',
                '출처: ' + _refs([e.source_id]) + '; 원문 위치: ' + _text(e.locator) + '.',
            ]
        )
        if e.value is not None:
            lines.append(
                '값: '
                + str(e.value)
                + ' '
                + _text(e.unit)
                + '; 기간: '
                + _text(e.period)
                + '; 통화: '
                + _text(e.currency)
                + '.'
            )
        if e.provenance:
            if run.input.get('observation_dates_version'):
                lines.append(
                    '해당 값의 관측일: '
                    + _text(str(e.observed_at) if e.observed_at else 'UNKNOWN')
                    + '; 원문 기간: '
                    + _text(e.provenance.definition['period'])
                    + '. 월·분기 자료의 날짜는 기간 말일 표기다.'
                )
            lines.extend(
                [
                    '정의: ' + _text(str(e.provenance.definition)),
                    '시점 상태: '
                    + _text(STATUS_NAMES.get(e.provenance.freshness, e.provenance.freshness))
                    + '; snapshot: '
                    + _text(e.provenance.snapshot_id)
                    + '; 구절: '
                    + _text(e.provenance.excerpt_id)
                    + '.',
                ]
            )
        else:
            lines.append('사용자가 제공한 값이며 실제 계좌 잔액의 외부 확인이 아니다.')
        lines.append('')
    for m in run.result.metrics:
        lines.extend(
            [
                _anchor(m.id),
                '### 계산 · ' + _text(m.id),
                '',
                str(m.value) + ' ' + _text(m.unit) + '; 방법: ' + _text(m.method) + '.',
                '',
                '입력: ' + _refs(m.input_ids),
                '',
            ]
        )
    for s in run.case.sources:
        lines.extend([_anchor(s.id), '### 출처 · ' + _text(s.name), ''])
        if s.provenance:
            p = s.provenance
            lines.extend(
                [
                    '[원문](<' + s.location + '>)',
                    '출처 상태: '
                    + _text(STATUS_NAMES.get(p.status, p.status))
                    + '; 시점: '
                    + _text(STATUS_NAMES.get(p.freshness, p.freshness))
                    + '.',
                    ('자료 전체/판본 기준: ' if run.input.get('observation_dates_version') else '관측: ')
                    + _text(p.observed_at or 'UNKNOWN')
                    + '; 공개: '
                    + _text(p.published_at or 'UNKNOWN')
                    + '; 획득: '
                    + p.retrieved_at
                    + '.',
                    '보존 조건: ' + _text(p.policy_note) + '; 정책: [확인](<' + p.policy_url + '>)',
                    'snapshot: ' + p.snapshot_id + '; 보존 payload SHA-256: ' + p.payload_sha256 + '.',
                ]
            )
        else:
            lines.append('사용자의 로컬 입력을 추적한다. 자기보고이며 공개 금융 데이터의 출처와 구분한다.')
        lines.append('')
    if (
        run.input.get('semiconductor_coverage')
        and {m['id'] for m in run.input['methods']} == {'SAMSUNG', 'SK_HYNIX'}
        and tuple(run.input['plan']['modes']) == (ResearchMode.COMPARE,)
    ):
        from .semiconductor_report import sections

        appendix = lines[lines.index('## 근거와 판단을 직접 확인하기') :]
        lines = [
            '# 삼성전자와 SK하이닉스 비교',
            '',
            '**질문:** ' + _text(run.input['question']),
            '',
            '정보 기준: '
            + run.cutoff.isoformat()
            + ' / '
            + run.cutoff.astimezone(ZoneInfo('Asia/Seoul')).isoformat()
            + ' (한국시간).',
            '',
        ]
        if run.input['synthetic']:
            lines.extend(['**합성 검증 자료다. 실제 투자 판단에 사용하지 않는다.**', ''])
        lines.extend(sections(run))
        lines.extend(['<details>', '<summary>출처 선택·미확보 자료·계산 근거를 확인하기</summary>', ''])
        lines.extend(_guard_report(run))
        if run.discovery:
            lines.extend(_discovery_report(run))
        lines.extend(['## 남은 자료 공백', ''])
        lines.extend('- ' + _text(n) for n in _unresolved(run))
        lines.append('')
        lines.extend(appendix)
        lines.extend(['', '</details>', ''])
    if run.input.get('scan'):
        from .scan_report import sections

        appendix = lines[lines.index('## 근거와 판단을 직접 확인하기') :]
        combined = (
            lines[lines.index('## 개별 대상을 깊게 조사하면') : lines.index('## 근거와 판단을 직접 확인하기')]
            if '## 개별 대상을 깊게 조사하면' in lines
            else []
        )
        lines = sections(run)
        lines.extend(combined)
        lines.extend(_guard_report(run))
        lines.extend(['<details>', '<summary>전체 조사 범위·출처·계산·검증 기록</summary>', ''])
        from .scan import assess

        review = assess(run)
        lines.extend(
            [
                '## 조사 범위와 비교 기준',
                '',
                '공통 기준: ' + ' · '.join(review['comparison_axes']) + '.',
                '',
                '| 영역 | 조사 결과 | 고유 수익 원천 |',
                '| --- | --- | --- |',
            ]
        )
        for r in review['universe']:
            lines.append('| ' + _text(r['name']) + ' | ' + _text(r['status']) + ' | ' + _text(r['economics']) + ' |')
        lines.extend(['', '인지도: ' + review['popularity_role'], '', '커뮤니티: ' + review['attention_role'], ''])
        for n in review['narrative_checks']:
            lines.extend(
                [
                    '- 관측 발언: '
                    + _refs([n['evidence_id']])
                    + '. 사실 검증: 미검증. 관련 원자료: '
                    + _refs(n['context_ids'])
                    + '. '
                    + n['reason']
                ]
            )
        if run.discovery:
            lines.extend(_discovery_report(run))
        lines.extend(['## 남은 핵심 자료', ''])
        lines.extend('- ' + _text(n) for n in _unresolved(run))
        lines.append('')
        lines.extend(appendix)
        lines.extend(['', '</details>', ''])
    if (
        run.input.get('commodity_coverage')
        and tuple(run.input['plan']['modes']) == (ResearchMode.ASSET_DEEP_DIVE,)
        and {m['id'] for m in run.input['methods']} <= {'NATGAS', 'GOLD', 'BROAD_COMMODITIES'}
    ):
        from .commodity_report import sections, assessment

        appendix = lines[lines.index('## 근거와 판단을 직접 확인하기') :]
        lines = [
            '# 원자재 심층 조사',
            '',
            '**질문:** ' + _text(run.input['question']),
            '',
            '정보 기준: ' + run.cutoff.astimezone(ZoneInfo('Asia/Seoul')).isoformat() + ' (한국시간).',
            '',
        ]
        lines.extend(sections(run))
        lines.extend(['<details>', '<summary>원자료·누락·판단 연결·계산 상세</summary>', ''])
        lines.extend(_guard_report(run))
        for asset, a in assessment(run)['assets'].items():
            lines.extend(['### ' + asset + ' 핵심 자료 공백', '', *('- ' + _text(g) for g in a['gaps']), ''])
        if run.discovery:
            lines.extend(_discovery_report(run))
        lines.extend(appendix)
        lines.extend(['', '</details>', ''])
    return '\n'.join(lines) + '\n'


def _discovery_report(run):
    """Numbers come only from actually promoted evidence, not search previews."""
    lines = [
        '## 새 원자료로 확인한 현재 상태',
        '',
        '| 항목 | 확인한 값 | 자료 시각·범위 | 근거 |',
        '| --- | --- | --- | --- |',
    ]
    evidence = {e.id: e for e in run.case.evidence}
    accepted = {ref for need in run.discovery['needs'] for ref in need['evidence_ids']}
    limits = []
    for candidate in run.discovery['candidates']:
        if candidate['status'] != 'selected' or candidate['source_type'] == 'community':
            continue
        for r in candidate['verified']['records']:
            e = evidence.get(r['evidence_id'])
            if e is None or e.id not in accepted or not _current(run, e):
                continue
            unit = {'USD_per_BTC': '달러/BTC', 'USD': '달러', 'fraction': '비율 (8시간, 연율 아님)'}.get(
                e.unit, _unit(e.unit)
            )
            is_text = e.unit == 'text' or bool(
                run.input.get('semiconductor_coverage') and e.provenance.definition['unit'] == 'text'
            )
            value = (
                format(e.value, 'f') + ' ' + unit
                if e.value is not None
                else (
                    '원문 구절 확인 (하단 근거 참조)'
                    if run.input.get('korean_coverage') and is_text
                    else '수치 채택 보류'
                )
            )
            row_date = (
                (str(e.observed_at) if e.observed_at else 'UNKNOWN')
                if run.input.get('observation_dates_version')
                else candidate['verified']['observed_at']
            )
            lines.append(
                '| '
                + _text(r['label'])
                + ' | '
                + _text(value)
                + ' | '
                + _text(row_date)
                + ' · '
                + (_text(e.provenance.definition['period']) + ' · ' if run.input.get('korean_coverage') else '')
                + _text(e.provenance.definition['scope'])
                + ' | '
                + _refs([e.id])
                + ' |'
            )
        limits.extend(candidate['verified']['limitations'])
    lines.extend(
        [
            '',
            *('- ' + _text(x) for x in dict.fromkeys(limits)),
            '',
            (
                '관측 사실·제공자 집계·경영진 전망의 범위와 정의를 구분한다. 수치 확인은 저평가·미래 상승의 증명이 아니다.'
                if run.input.get('korean_coverage')
                else '가격은 거래소의 체결 가격, 선물 평가 가격은 계약 평가용 값이다. 서로 같은 현물 가격으로 섞지 않는다. 수치 확인은 저평가·미래 상승의 증명이 아니다.'
            ),
            '',
            '### 확인하지 못한 근거도 결과다',
            '',
        ]
    )
    for need in run.discovery['needs']:
        if need['status'] == 'available':
            lines.append(
                '- '
                + _text(need['label'])
                + ': 선택한 범위의 원문·시점·정의 확인. ('
                + _refs(need['evidence_ids'])
                + ')'
            )
        else:
            lines.append(
                '- '
                + _text(need['label'])
                + ': '
                + ('일부 확인' if need['status'] == 'partial' else '자료 미확보 (unavailable)')
                + '. '
                + _text(' / '.join(need['gaps']))
            )
    blocked = [i for i in run.discovery['indexes'] if i['status'] != 'available']
    for index in blocked:
        lines.append(
            '- 접근하지 못한 공개 경로: '
            + _text(index['url'])
            + ' · '
            + _text(STATUS_NAMES.get(index['status'], index['status']))
            + '. 제한을 우회하지 않았다.'
        )
    lines.extend(
        [
            '',
            '선택 이유·검토한 후보·제외 이유·최신성·판본은 함께 보존한 출처 선택 기록에서 확인할 수 있다. 검색 결과와 요약은 금융 근거로 사용하지 않았다.',
            '',
        ]
    )
    return lines


def build_manifest(run, report):
    _check(run)
    evidence = _used_evidence(run)
    claims = {claim.id: claim for claim in run.case.claims}
    if run.deep:
        if run.evidence_validation:
            from .evidence_guard import guard_case

            guarded, _ = guard_case(
                run.deep.integration.case, run.cutoff, numeric_ids=run.input['evidence_validation']['numeric_ids']
            )
            claims.update({c.id: c for c in guarded.claims if c.id not in claims})
        else:
            claims.update({claim.id: claim for claim in run.deep.integration.case.claims})
    code = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob('*.py')):
        code.update(path.name.encode() + b'\0' + path.read_bytes() + b'\0')
    artifacts = {
        str(path.relative_to(run.directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(run.directory.rglob('*'))
        if path.is_file() and path.name != 'run_manifest.json'
    }

    def serial(value):
        if isinstance(value, Decimal):
            return str(value)
        if hasattr(value, 'isoformat'):
            return value.isoformat()
        raise TypeError(type(value).__name__)

    import json

    data = dict(
        schema_version='ask-run-v1',
        execution_status='completed',
        research_status=research_status(run),
        question=run.input['question'],
        resolved_intent=run.input['plan'],
        selected_modes=run.input['plan']['modes'],
        scope=run.input['tasks'],
        task_results=_task_results(run),
        methods=run.input['methods'],
        as_of=run.cutoff.isoformat(),
        synthetic=run.input['synthetic'],
        request_sha256=_digest_input(run.input),
        input_sha256=run.digest,
        run_id=run.result.run_id,
        code_sha256=code.hexdigest(),
        method_versions={**run.input['method_versions'], 'report': report_version(run)},
        pipeline_invocations=list(run.invocations),
        sources_accessed=[asdict(s) for s in run.case.sources],
        evidence_used=[asdict(e) for e in evidence],
        claims_evaluated=[asdict(c) for c in claims.values()],
        calculations=[asdict(m) for m in run.result.metrics],
        reasoning=_insights(run),
        finding_checks=list(run.findings),
        unresolved_questions=_unresolved(run),
        portfolio_missing=list(run.portfolio.missing),
        conclusion=run.result.conclusion,
        personal_conclusion=run.result.personal_conclusion,
        personal_constraints=list(run.result.constraints),
        report={'path': 'report.md', 'sha256': hashlib.sha256(report.encode()).hexdigest()},
        artifact_sha256=artifacts,
        follow_up_reference={'run_id': run.result.run_id, 'subject_ids': [m['id'] for m in run.input['methods']]},
    )
    if run.input.get('observation_dates_version'):
        dates = observation_audit(run)
        data['observation_integrity'] = {
            'path': 'observation_integrity.json',
            'method_version': dates['method_version'],
            'mismatched_ids': dates['mismatched_ids'],
            'unknown_ids': dates['unknown_ids'],
        }
    if run.discovery:
        data['source_discovery'] = run.discovery
    if run.evidence_validation:
        data['evidence_validation'] = {
            'path': 'evidence_validation.json',
            'quarantined_ids': run.evidence_validation['quarantined_ids'],
            'method_version': run.evidence_validation['method_version'],
        }
    if run.input.get('commodity_coverage'):
        from .commodity_report import assessment

        data['commodity_research'] = assessment(run)
    if run.input.get('semiconductor_coverage'):
        from .semiconductor_data import audit

        data['company_comparison'] = audit(run)
    if run.input.get('scan'):
        from .scan import assess

        a = assess(run)
        if run.input['scan']['method_version'] in (
            'evidence_shortlist_v4',
            'evidence_shortlist_v5',
            'evidence_shortlist_v6',
            'evidence_shortlist_v7',
        ):
            # Full numeric ledgers are pinned once in their own artifacts,
            # instead of duplicating them in an increasingly large manifest.
            data['opportunity_shortlist'] = {
                k: v for k, v in a.items() if k not in ('observations', 'within_scan_changes', 'since_previous_scan')
            }
            data['scan_artifacts'] = {
                'observations': 'scan_observations.json',
                'changes': 'scan_changes.json',
                'full_shortlist': 'shortlist.json',
                'comparison_input': 'input.json:previous_scan',
                'method': 'same_definition_scan_comparison_v1',
            }
        else:
            data['opportunity_shortlist'] = a
        data['follow_up_reference']['candidate_subject_ids'] = data['opportunity_shortlist']['candidates']
    if run.input['plan'].get('understanding'):
        data['query_understanding'] = run.input['plan']['understanding']
    return json.loads(json.dumps(data, default=serial, ensure_ascii=False, allow_nan=False))


def _digest_input(value):
    from .source_pipeline import _digest

    return _digest(value)
