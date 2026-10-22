"""Natural-language research using the existing acquisition and replay engines.

Live asks acquire only reviewed, scoped sources. Replay is immutable and offline.
Economic conclusions remain limited draft interpretations, never trading orders.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import json
from pathlib import Path

from .deep_dive import DEEP_DIVE_VERSION, SECTIONS, load_deep_dive_review, replay_deep_dive
from .discovery import (
    DISCOVERY_VERSION,
    attach_discovery,
    discover_sources,
    evidence_needs,
    replay_discovery,
    scoped_catalog_sources,
    validate_policy,
)
from .discovery_contracts import CONTRACT_VERSION
from .engine import ENGINE_VERSION, run_research
from .macro import MACRO_VERSION
from .macro_pipeline import MACRO_PIPELINE_VERSION, acquire_macro, load_macro_plan, replay_macro
from .models import (
    Alternative,
    InterpretationStatus,
    ResearchBrief,
    ResearchCase,
    ResearchClaim,
    Review,
    VerificationStatus,
)
from .opportunity import OPPORTUNITY_VERSION, OpportunityReview, replay_opportunity
from .portfolio import PORTFOLIO_VERSION, review_portfolio, validate_portfolio
from .research_catalog import (
    CATALOG_VERSION,
    CPI,
    METHODS,
    SCAN_ASSETS,
    load_catalog,
    project_macro,
    project_sources,
    resolve_subject,
)
from .routing import ROUTING_VERSION, ResearchMode, _subjects, plan_research
from .source_pipeline import PIPELINE_VERSION, _digest, acquire_plan, load_pins, load_source_plan, replay_plan
from .sources import SOURCE_VERSION, SourceError, _time, freshness, load_snapshot, _parse_json
from .korean_data import (
    KOREAN_DATA_VERSION,
    KR_RATES,
    discovery_policy as korean_discovery_policy,
    evidence_needs as korean_evidence_needs,
    ecos_macro_plan,
    resolve_korean_subject,
    supports_discovery,
    calculate_korean_observations,
)
from .semiconductor_data import (
    VERSION as SEMICONDUCTOR_VERSION,
    evidence_needs as semiconductor_needs,
    policy as semiconductor_policy,
    calculate as calculate_semiconductor,
    audit as semiconductor_audit,
)
from . import scan

ORCHESTRATOR_VERSION = 'research_orchestrator_v1'
METHOD_VERSIONS = dict(
    orchestrator=ORCHESTRATOR_VERSION,
    routing=ROUTING_VERSION,
    catalog=CATALOG_VERSION,
    portfolio=PORTFOLIO_VERSION,
    engine=ENGINE_VERSION,
    acquisition=SOURCE_VERSION,
    source_verification=PIPELINE_VERSION,
    macro=MACRO_VERSION,
    macro_pipeline=MACRO_PIPELINE_VERSION,
    opportunity=OPPORTUNITY_VERSION,
    deep_dive=DEEP_DIVE_VERSION,
    findings='bounded_findings_v1',
)


def _save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n'
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        handle.write(text)


def _scope(plan, portfolio, *, korean=False, scan_config=None, commodity=False):
    methods = {}
    tasks = []
    unresolved = list(plan.clarifications)
    date_limits = [d for d in plan.understanding['data_limits'] if d['kind'] == 'dated_reference']
    unresolved.extend(d['raw_text'] + ': ' + d['reason'] for d in plan.understanding['data_limits'])
    for task in plan.tasks:
        target_methods = []
        unsupported = []
        subject_methods = []
        coverage = []
        if task.mode == ResearchMode.OPPORTUNITY_SCAN:
            target_methods = (
                scan.universe(korean) if scan_config else [METHODS[identifier] for identifier in SCAN_ASSETS]
            )
        elif task.mode == ResearchMode.PORTFOLIO_REVIEW:
            for holding in (portfolio or {}).get('holdings', []):
                subjects = _subjects(holding.get('asset', holding['name']))
                found = (
                    (resolve_korean_subject(subjects[0], korean) or resolve_subject(subjects[0]))
                    if len(subjects) == 1
                    else None
                )
                if found is not None:
                    target_methods.append(found)
                else:
                    unsupported.append(holding['name'])
                    unresolved.append(
                        holding['name'] + ': 평가액 구성은 계산할 수 있지만 이 보유의 시장 근거 연결은 미지원이다.'
                    )
        elif task.scope != 'scan_candidates_only_if_supported':
            for subject in task.subjects:
                found = resolve_korean_subject(subject, korean) or resolve_subject(subject)
                if found is None:
                    unsupported.append(subject.label)
                    unresolved.append(
                        subject.label
                        + ': 명시한 조건을 지원할 출처·고유 방법 연결이 없다. 현재 이 조건을 지원할 데이터가 부족하다.'
                    )
                else:
                    if date_limits:
                        found = replace(
                            found,
                            source_ids=(),
                            macro_ids=(),
                            missing=(*found.missing, *(d['raw_text'] + ': ' + d['reason'] for d in date_limits)),
                        )
                    target_methods.append(found)
                    if (
                        not found.source_ids
                        and not found.macro_ids
                        and not (korean and supports_discovery(found.id) and not date_limits)
                        and not (commodity and found.id in ('NATGAS', 'GOLD', 'BROAD_COMMODITIES') and not date_limits)
                    ):
                        unsupported.append(subject.label)
                        unresolved.extend(found.missing)
                subject_methods.append(found.id if found else None)
                unavailable = (
                    found is None
                    or not found.source_ids
                    and not found.macro_ids
                    and not (korean and supports_discovery(found.id) and not date_limits)
                    and not (commodity and found.id in ('NATGAS', 'GOLD', 'BROAD_COMMODITIES') and not date_limits)
                )
                coverage.append(
                    dict(
                        subject=asdict(subject),
                        method_id=found.id if found else None,
                        status='unavailable' if unavailable else 'partial',
                        reason=(
                            '명시된 조건의 데이터 연결이 부족하다. 조건을 버리거나 다른 국가·만기·지역 자료로 대체하지 않는다.'
                            if unavailable
                            else '해당 대상의 기존 자료 범위만 조사한다.'
                        ),
                    )
                )
        if date_limits and task.mode in (ResearchMode.OPPORTUNITY_SCAN, ResearchMode.PORTFOLIO_REVIEW):
            target_methods = [
                replace(
                    m,
                    source_ids=(),
                    macro_ids=(),
                    missing=(*m.missing, *(d['raw_text'] + ': ' + d['reason'] for d in date_limits)),
                )
                for m in target_methods
            ]
        tasks.append(
            dict(
                id=task.id,
                mode=task.mode.value,
                subjects=[asdict(s) for s in task.subjects],
                method_ids=list(dict.fromkeys(item.id for item in target_methods)),
                unsupported=unsupported,
                subject_method_ids=subject_methods,
                candidate_dependent=task.scope == 'scan_candidates_only_if_supported',
                condition_coverage=coverage,
            )
        )
        for item in target_methods:
            methods[item.id] = asdict(item)
    return list(methods.values()), tasks, unresolved


def _findings(input_data, case):
    """Retain bounded draft reasoning only for its exact current factual inputs.

    A changed quote/definition never inherits an old interpretation. A matched
    occurrence remains a source statement, not an automatically true thesis.
    """
    evidence = {e.id: e for e in case.evidence}
    selected = {m['id'] for m in input_data['methods']}
    results = []
    for original in input_data['findings']:
        assets = [identifier for identifier in original['asset_ids'] if identifier in selected]
        if not assets:
            continue
        reasons = []
        for identifier in original['evidence_ids']:
            item = evidence.get(identifier)
            if item is None or item.provenance is None:
                reasons.append(identifier + ': 원문 미확보')
            elif (
                item.kind == 'observed_narrative'
                or item.provenance.freshness != 'fresh'
                or item.verification != VerificationStatus.SUPPORTED
            ):
                reasons.append(identifier + ': 현재 사실 참조로 채택하지 않음')
            elif not set(assets) <= set(item.asset_ids):
                reasons.append(identifier + ': 자산 범위 불일치')
            elif (
                _digest({'text': item.text, 'definition': item.provenance.definition})
                != original['fingerprints'][identifier]
            ):
                reasons.append(identifier + ': 검토한 원문·정의가 변경됨')
        results.append(
            {
                **deepcopy(original),
                'asset_ids': assets,
                'status': 'withheld' if reasons else 'available_draft',
                'withheld_reasons': reasons,
            }
        )
    return tuple(results)


def _review(methods, source_plan, cutoff, profile, identifier='ASK_EVIDENCE_REVIEW', *, discovery=False):
    def statement(text, refs=()):
        return dict(text=text, evidence_ids=list(refs))

    rows = []
    for item in methods:
        source_ids = {s['id'] for s in source_plan['sources'] if item['id'] in s['asset_ids']}
        refs = [
            e['id']
            for e in source_plan['evidence']
            if e['source_id'] in source_ids and e['kind'] != 'observed_narrative'
        ]
        positive_refs = [ref for ref in refs if not ref.startswith('E_DISC_')] if discovery else refs
        rows.append(
            dict(
                asset_id=item['id'],
                name=item['label'].replace('S&P 500', '미국 주가지수'),
                exposure=item['economics'],
                return_definition='수익의 원천과 정의를 구분하며 미래 수익을 추정하지 않는다.',
                liquidity='실제 상품·개인 조건은 확인한 범위만 사용한다.',
                state=statement('선택한 원자료의 구절·시점과 조사 범위를 확인한다.', refs),
                positive=statement(
                    '가설을 지지하는지 확인할 배경 자료다. 원문 존재가 가설의 증명은 아니다.', positive_refs
                ),
                negative=statement('반대 논리와 같은 정의의 반증 자료를 추가로 검토해야 한다.'),
                uncertainty=item['missing'],
                opportunity_cost={
                    **statement('다른 수익의 정의·기간·통화·손실 경로를 맞춰 비교해야 한다.'),
                    'alternative_ids': [m['id'] for m in methods if m['id'] != item['id']],
                },
                priority='monitor',
                priority_reason=statement('현재 가격의 매력이나 우월성을 자동 확정하지 않고 검토를 이어간다.', refs),
                recheck=statement('새 원자료·반대 근거·사용자 제약이 판단을 바꾸는지 확인한다.'),
                candidate=None,
            )
        )
    return dict(
        schema_version='opportunity-review-v1',
        id=identifier,
        question='질문에 필요한 근거와 비교 조건을 확인한다.',
        as_of=cutoff.isoformat(),
        author='검토한 규칙 기반 연구 작성기',
        review_status='draft',
        profile=profile,
        horizon='사용자 투자기간은 확인한 입력 범위에서만 사용한다.',
        comparison_limits=['수익률 정의가 다른 수치를 순위나 미래 수익으로 합치지 않는다.'],
        rows=rows,
        sections={
            key: []
            for key in (
                'overview',
                'drivers',
                'market_narratives',
                'community',
                'gaps',
                'korean_context',
                'unknowns',
                'easy',
            )
        },
        next_research={
            'asset_id': methods[0]['id'],
            'title': '필요한 원자료 검토',
            'question': '부족한 현재 원자료와 반대 근거를 보완한다.',
        },
        sampling_limits=['검토한 공개 URL의 제한된 표본이다. 전체 시장이나 커뮤니티를 대표하지 않는다.'],
        access_notes=[],
    )


def _deep_review(input_data, source_plan, cutoff, profile):
    known = {e['id'] for e in source_plan['evidence']}
    facts = [f for f in input_data['quoted_facts']['facts'] if f['source_evidence_id'] in known]
    fact_ids = {f['id'] for f in facts}
    calculations = [c for c in input_data['quoted_facts']['calculations'] if set(c['input_ids']) <= fact_ids]
    refs = [
        f['id']
        for f in facts
        if f['basis'] in ('forward_12m_pe', 'forward_fy1_harmonic_pe', 'trailing_pe', 'nominal_cmt_investment_yield')
    ]
    statement = dict(
        text='확보한 수치의 정의·기간·시점을 확인하며 기대 이익과 국채 대안을 구분한다.',
        evidence_ids=refs,
        role='interpretation',
    )
    sections = {name: [] for name in SECTIONS}
    sections['conclusions'] = [deepcopy(statement) for _ in range(3)]
    sections['denominator'] = [deepcopy(statement)]
    sections['treasury'] = [deepcopy(statement)]
    return dict(
        schema_version='deep-dive-review-v1',
        id='ASK_US_EARNINGS_TREASURY',
        question='미국 주식의 이익 기대와 국채 기회비용을 구분한다.',
        as_of=cutoff.isoformat(),
        author='검토한 원문 수치의 명시적 전사',
        review_status='draft',
        parent=None,
        profile=profile,
        horizon='미확인 투자기간에서 개인 판단을 확정하지 않는다.',
        facts=facts,
        calculations=calculations,
        tables=[],
        sections=sections,
        judgment='insufficient evidence',
        comparison_limits=['이익수익률과 국채 금리의 차이는 확정 기대수익이나 ERP가 아니다.'],
        sampling_limits=['선택한 지수 원자료의 검토 범위이며 전체 기업의 미래 이익을 검증한 것은 아니다.'],
        unknowns=['새로운 가격 매력 판단에는 실제 실적·수정·반대 근거의 의미 검토가 필요하다.'],
        next_research='현재 질문에 필요한 누락 원자료를 보완한다.',
    )


def _align(case, store, cutoff):
    """Apply the same exact-cutoff/unknown-publication rules as opportunity replay."""
    sources = []
    for source in case.sources:
        p = source.provenance
        shot = load_snapshot(store, source.id, p.snapshot_id)
        age = freshness(shot, cutoff)['status'] if shot.status == 'available' else 'unavailable'
        if _time(p.retrieved_at) > cutoff:
            age = 'future'
        elif age not in ('future', 'unavailable') and p.published_at is None and p.observed_at is None:
            age = 'unknown'
        sources.append(replace(source, provenance=replace(p, freshness=age)))
    ages = {s.id: s.provenance.freshness for s in sources}
    evidence = tuple(replace(e, provenance=replace(e.provenance, freshness=ages[e.source_id])) for e in case.evidence)
    return replace(case, sources=tuple(sources), evidence=evidence)


@dataclass(frozen=True)
class AskRun:
    directory: Path
    input: dict
    cutoff: datetime
    case: object
    result: object
    portfolio: object
    macro: object
    opportunity: object
    deep: object
    invocations: tuple[dict, ...]
    findings: tuple[dict, ...]
    digest: str
    discovery: dict | None = None
    evidence_validation: dict | None = None
    investment: dict | None = None


def _execute(root, input_data):
    cutoff = _time(input_data['as_of'])
    calls = []
    macro = None
    opportunity = None
    deep = None
    portfolio = review_portfolio(input_data['portfolio'], cutoff.date())
    profile = {name: asdict(value) for name, value in portfolio.profile.fields.items()}
    plan = load_source_plan(root / 'source_plan.json') if input_data['has_sources'] else None
    macro_plan = load_macro_plan(root / 'macro_plan.json') if input_data['has_macro'] else None
    source_pins = load_pins(root / 'source_pins.json') if plan else None
    macro_pins = load_pins(root / 'macro_pins.json') if macro_plan else None
    if plan and macro_plan and 'US_EQUITY' in plan.asset_ids:
        deep = replay_deep_dive(
            load_deep_dive_review(root / 'deep_review.json'),
            plan,
            root / 'source_snapshots',
            source_pins,
            macro_plan,
            root / 'macro_snapshots',
            macro_pins,
        )
        case = deep.case
        metrics = list(deep.metrics)
        macro = deep.integration.macro
        calls.append(dict(function='replay_deep_dive', purpose='quoted_financials_and_source_macro_validation'))
    elif plan and macro_plan:
        data = load_pins(root / 'evidence_review.json')
        integration = replay_opportunity(
            OpportunityReview(data, _digest(data)),
            plan,
            root / 'source_snapshots',
            source_pins,
            macro_plan,
            root / 'macro_snapshots',
            macro_pins,
        )
        case = integration.case
        metrics = list(integration.result.metrics)
        macro = integration.macro
        calls.append(dict(function='replay_opportunity', purpose='scoped_source_macro_validation'))
    elif plan:
        case = _align(
            replay_plan(plan, root / 'source_snapshots', source_pins, as_of=cutoff.date()),
            root / 'source_snapshots',
            cutoff,
        )
        metrics = []
        calls.append(dict(function='replay_plan', purpose='source_and_claim_validation'))
    else:
        case = ResearchCase(
            '1',
            input_data['synthetic'],
            ResearchBrief(
                'ASK_EMPTY', input_data['question'], cutoff.date(), 'KRW', '필요한 입력을 확인한다.', (), (), ()
            ),
            portfolio.profile,
            (),
            (),
            (),
            (),
            (),
            (),
            _digest(None),
        )
        metrics = []
        if macro_plan:
            macro = replay_macro(macro_plan, root / 'macro_snapshots', macro_pins, as_of=cutoff)
            case = macro.case
            metrics = list(macro.metrics)
            calls.append(dict(function='replay_macro', purpose='relevant_macro'))
    if ResearchMode.OPPORTUNITY_SCAN.value in input_data['plan']['modes'] and plan and macro_plan:
        data = load_pins(root / 'opportunity_review.json')
        opportunity = replay_opportunity(
            OpportunityReview(data, _digest(data)),
            plan,
            root / 'source_snapshots',
            source_pins,
            macro_plan,
            root / 'macro_snapshots',
            macro_pins,
        )
        calls.append(dict(function='replay_opportunity', purpose='opportunity_scan'))
    discovery = None
    if input_data.get('has_discovery'):
        if deep:
            old_ids = {c.id for c in case.claims}
            case = replace(
                case,
                claims=(
                    *case.claims,
                    *(
                        c
                        for c in deep.integration.case.claims
                        if c.id.startswith('DISC_COMMUNITY_CLAIM_') and c.id not in old_ids
                    ),
                ),
            )
        if plan is None:
            case = replace(
                case,
                alternatives=tuple(
                    Alternative(
                        m['id'],
                        m['label'],
                        m['economics'],
                        '미래 수익은 추정하지 않는다.',
                        '실제 상품·유동성 미확인',
                        (),
                        (),
                        tuple(m['missing']),
                        (),
                    )
                    for m in input_data['methods']
                ),
            )
        record = load_pins(root / 'discovery.json')
        if _digest(record) != input_data['discovery_sha256']:
            raise SourceError('discovery record checksum mismatch')
        discovery = replay_discovery(record, case, cutoff)
        # The source-level legacy day limit is intentionally coarser than the
        # discovery need's hour limit. Apply the stricter selection window to
        # actual evidence too, so a late tick cannot enter a current conclusion.
        ages = {c['source_id']: c['freshness']['status'] for c in discovery['candidates'] if c['status'] == 'selected'}
        from .discovery import candidate_freshness

        for need in discovery['needs']:
            for c in discovery['candidates']:
                if c['need_id'] == need['id'] and c['status'] == 'selected':
                    ages[c['source_id']] = candidate_freshness(c, need, cutoff)['status']
        for s in case.sources:
            if s.id in ages and s.provenance.status != 'available':
                ages[s.id] = 'unavailable'
        case = replace(
            case,
            sources=tuple(
                replace(s, provenance=replace(s.provenance, freshness=ages[s.id])) if s.id in ages else s
                for s in case.sources
            ),
            evidence=tuple(
                replace(e, provenance=replace(e.provenance, freshness=ages[e.source_id])) if e.source_id in ages else e
                for e in case.evidence
            ),
        )
        calls.append(dict(function='replay_discovery', purpose='source_selection_freshness_and_promotion_audit'))
    validation = None
    if input_data.get('evidence_validation'):
        if input_data.get('scan', {}).get('method_version') in scan.MINIMUM_VERSIONS:
            from .scan_coverage import macro_evidence

            case = replace(case, evidence=(*case.evidence, *macro_evidence(macro, case, cutoff)))
        from .source_pipeline import validate_evidence

        case, validation = validate_evidence(case, cutoff, input_data['evidence_validation'])
        blocked = set(validation['quarantined_ids'])
        metrics = [m for m in metrics if not set(m.input_ids) & blocked]
        if discovery:
            for need in discovery['needs']:
                rejected = sorted(set(need['evidence_ids']) & blocked)
                if rejected:
                    need['evidence_ids'] = [i for i in need['evidence_ids'] if i not in blocked]
                    # A source can be partially available while its current
                    # financial value is quarantined. Preserve that distinction.
                    need['status'] = 'partial'
                    need['gaps'].append(
                        '이상/충돌/미완성 행 자료 격리: ' + ', '.join(rejected) + '; 독립 원자료 교차 확인 필요.'
                    )
        calls.append(
            dict(
                function='validate_evidence',
                purpose='quarantine_anomalies_conflicts_units_missing_before_financial_use',
            )
        )
    findings = _findings(input_data, case)
    if input_data.get('korean_coverage') and plan is None and input_data['methods']:
        scope = tuple(m['id'] for m in input_data['methods'])
        case = replace(
            case,
            alternatives=tuple(
                Alternative(
                    m['id'],
                    m['label'],
                    m['economics'],
                    '미래 수익은 추정하지 않는다.',
                    '실제 상품·유동성 미확인',
                    (),
                    (),
                    tuple(m['missing']),
                    (),
                )
                for m in input_data['methods']
            ),
            evidence=tuple(replace(e, asset_ids=scope) for e in case.evidence),
            claims=tuple(replace(c, asset_ids=scope) for c in case.claims),
        )
    known = {e.id for e in case.evidence}
    pending = Review(
        InterpretationStatus.PENDING,
        None,
        None,
        '원문·정의가 일치한 좁은 해석 초안이다. 투자 가설의 의미 검토 완료가 아니다.',
    )
    claims = list(case.claims)
    for finding in findings:
        claims.append(
            ResearchClaim(
                'ASK_FINDING_' + finding['id'],
                finding['text'],
                tuple(finding['asset_ids']),
                VerificationStatus.UNVERIFIED,
                pending,
                (),
                (),
                None,
                tuple(finding['withheld_reasons']) + ('원문 존재와 경제적 해석의 사실 검증은 구분한다.',),
                finding['reassessment'],
                tuple(ref for ref in finding['evidence_ids'] if ref in known),
            )
        )
    sources = list(case.sources)
    evidence = list(case.evidence)
    if portfolio.source:
        sources.append(portfolio.source)
        evidence.extend(portfolio.evidence)
        metrics.extend(portfolio.metrics)
        calls.append(dict(function='review_portfolio', purpose='self_reported_composition'))
    digest = _digest(
        {
            'input': input_data,
            'source_pins': source_pins,
            'macro_pins': macro_pins,
            'validated_case': case.input_digest,
            'portfolio': portfolio.input_digest,
            'methods': input_data['method_versions'],
        }
    )
    horizon = (
        str(input_data['portfolio']['horizon_months']) + '개월 · 사용자 제공 기간'
        if input_data['portfolio'] and input_data['portfolio']['horizon_months'] is not None
        else 'UNKNOWN · 실제 투자기간은 확인되지 않았다.'
    )
    if input_data['plan'].get('understanding'):
        explicit = [
            c['raw_text']
            for c in input_data['plan']['understanding']['user_constraints']
            if c['kind'] == 'holding_period'
        ]
        if explicit and not input_data['portfolio']:
            horizon = ' / '.join(explicit) + ' · 질문에서 명시한 기간; 전체 재무 조건은 미확인'
        if not case.alternatives and input_data['methods']:
            case = replace(
                case,
                alternatives=tuple(
                    Alternative(
                        m['id'],
                        m['label'],
                        m['economics'],
                        '미래 수익은 추정하지 않는다.',
                        '실제 자료·유동성 미확인',
                        (),
                        (),
                        tuple(m['missing']),
                        (),
                    )
                    for m in input_data['methods']
                ),
            )
    brief = replace(
        case.brief,
        id='ASK_RESEARCH',
        question=input_data['question'],
        as_of=cutoff.date(),
        horizon=horizon,
        excluded=tuple(
            label + '의 고유 방법·자료 연결 미지원' for task in input_data['tasks'] for label in task['unsupported']
        ),
    )
    case = replace(
        case,
        synthetic=input_data['synthetic'],
        brief=brief,
        profile=portfolio.profile,
        sources=tuple(sources),
        evidence=tuple(evidence),
        claims=tuple(claims),
        input_digest=digest,
    )
    if input_data.get('korean_coverage'):
        metrics.extend(
            calculate_korean_observations(case, require_dates=bool(input_data.get('observation_dates_version')))
        )
        calls.append(
            dict(
                function='calculate_korean_observations', purpose='same_definition_company_region_ratios_not_forecasts'
            )
        )
    if input_data.get('semiconductor_coverage'):
        metrics.extend(
            calculate_semiconductor(case, cutoff, require_dates=bool(input_data.get('observation_dates_version')))
        )
        calls.append(
            dict(
                function='calculate_semiconductor',
                purpose='reported_TTM_EPS_price_multiples_and_earnings_quality_with_basis_gates',
            )
        )
    if input_data.get('scan'):
        if input_data['scan']['method_version'] in scan.MINIMUM_VERSIONS:
            from .scan_coverage import macro_evidence, calculations as minimum_calculations

            extra = () if validation is not None else macro_evidence(macro, case, cutoff)
            case = replace(case, evidence=(*case.evidence, *extra))
            metrics.extend(
                minimum_calculations(case, cutoff, require_dates=bool(input_data.get('observation_dates_version')))
            )
            calls.append(
                dict(
                    function='scan_coverage',
                    purpose='minimum_coverage_same_definition_observations_not_attractiveness_scores',
                )
            )
        metrics.extend(scan.calculations(case, cutoff, require_dates=bool(input_data.get('observation_dates_version'))))
        calls.append(
            dict(
                function='scan.calculations', purpose='same_definition_price_and_valuation_context_not_expected_return'
            )
        )
    if input_data.get('commodity_coverage'):
        from .commodity_data import calculations as commodity_calculations

        extra = commodity_calculations(case, cutoff, require_dates=bool(input_data.get('observation_dates_version')))
        existing = {m.id for m in metrics}
        metrics.extend(m for m in extra if m.id not in existing)
        calls.append(
            dict(
                function='commodity_data.calculations',
                purpose='typed_futures_storage_position_constituent_arithmetic_not_forecasts',
            )
        )
    result = replace(run_research(case), metrics=tuple(metrics))
    calls.append(dict(function='run_research', purpose='evidence_quality_and_conclusion_limits'))
    run = AskRun(
        root,
        input_data,
        cutoff,
        case,
        result,
        portfolio,
        macro,
        opportunity,
        deep,
        tuple(calls),
        findings,
        digest,
        discovery,
        validation,
    )
    if input_data.get('scan') and opportunity:
        assessment = scan.assess(run)
        reviewed = scan.review(load_pins(root / 'opportunity_review.json'), assessment)
        selected = replay_opportunity(
            OpportunityReview(reviewed, _digest(reviewed)),
            plan,
            root / 'source_snapshots',
            source_pins,
            macro_plan,
            root / 'macro_snapshots',
            macro_pins,
        )
        calls.append(dict(function='replay_opportunity', purpose='evidence_gated_scan_shortlist'))
        run = replace(run, opportunity=selected, invocations=tuple(calls))
    if input_data.get('investment_cycle_version'):
        from .investment_cycle import attach_to_ask

        run = replace(run, investment=attach_to_ask(run))
    return run


def execute_ask(
    question,
    directory,
    *,
    modes=None,
    portfolio=None,
    catalog=None,
    now=None,
    fetcher=None,
    progress=None,
    context_run=None,
    previous_scan=None,
    decision_plan=None,
    decision_journal=None,
):
    catalog = catalog or load_catalog()
    start = now or datetime.now(timezone.utc)
    if start.tzinfo is None:
        raise SourceError('aware acquisition clock required')
    reference = scan.resolve_reference(question, replay_ask(context_run)) if context_run is not None else None
    plan = plan_research(reference['resolved_question'] if reference else question, modes=modes)
    if decision_plan is not None:
        from .decision_data import validate_plan

        validate_plan(decision_plan)
    if portfolio is not None:
        validate_portfolio(portfolio)
    review_portfolio(portfolio, start.date())
    scan_config = catalog.scan if ResearchMode.OPPORTUNITY_SCAN in plan.modes else None
    if scan_config:
        scan.validate(scan_config)
    anchor = None
    previous_investment = None
    if previous_scan is not None:
        if not scan_config or scan_config['method_version'] not in scan.MINIMUM_VERSIONS:
            raise SourceError('previous-scan is available only for a current Opportunity Scan')
        from .scan_coverage import capture, validate_anchor

        previous_run = replay_ask(previous_scan)
        anchor = capture(previous_run, require_dates=True)
        previous_investment = previous_run.investment
        validate_anchor(anchor, start, catalog.synthetic or bool((portfolio or {}).get('synthetic')))
    methods, tasks, unresolved = _scope(
        plan,
        portfolio,
        korean=catalog.korean is not None,
        scan_config=scan_config,
        commodity=catalog.commodity is not None,
    )
    dated = any(d['kind'] == 'dated_reference' for d in plan.understanding['data_limits'])
    needs = evidence_needs(question, methods, tasks) if catalog.discovery is not None and not dated else []
    if scan_config and scan_config['method_version'] in scan.MINIMUM_VERSIONS:
        # Pure Scan uses completed-price/volume inputs. Explicit combined BTC
        # Deep Dive retains its requested richer acquisition needs.
        pure = all(t['mode'] == 'opportunity_scan' for t in tasks if 'BTC' in t['method_ids'])
        if pure:
            needs = [n for n in needs if n['category'] not in ('market_state', 'community')]
    korean_needs = korean_evidence_needs(methods) if catalog.korean is not None and not dated else []
    if scan_config:
        # A scan checks regional price/volume first. Jeonse, individual property
        # cashflows and financing belong to a subsequent scoped deep dive.
        korean_needs = [
            n
            for n in korean_needs
            if not n['category'].startswith('reb_') or n['category'] in scan_config['regional_categories']
        ]
    semi_needs = (
        semiconductor_needs(methods)
        if catalog.semiconductor is not None and catalog.korean is not None and not dated
        else []
    )
    uses_korean = bool(korean_needs or any(set(m['macro_ids']) & set(KR_RATES) for m in methods))
    if uses_korean and (
        catalog.korean.get('schema_version') != 'korean-coverage-v1'
        or catalog.korean.get('method_version') != KOREAN_DATA_VERSION
    ):
        raise SourceError('unsupported Korean coverage registry')
    needs.extend(korean_needs)
    policy = (
        korean_discovery_policy(catalog.discovery, catalog.korean, korean_needs, start)
        if korean_needs
        else catalog.discovery
    )
    if scan_config and not dated and catalog.discovery is not None:
        needs.extend(scan.needs(methods, start, scan_config))
        policy = scan.policy(policy, methods, needs, start, scan_config)
    commodity_needs = []
    if catalog.commodity is not None and catalog.discovery is not None and not dated:
        from . import commodity_data

        if (
            catalog.commodity.get('method_version') != commodity_data.VERSION
            or catalog.commodity.get('schema_version') != 'commodity-coverage-v1'
        ):
            raise SourceError('unsupported commodity coverage registry')
        relevant = {
            i for t in tasks if t['mode'] in ('asset_deep_dive', 'compare', 'opportunity_scan') for i in t['method_ids']
        } & commodity_data.ASSETS
        selected = [m for m in methods if m['id'] in relevant]
        commodity_needs = commodity_data.evidence_needs(selected, tasks, scan=bool(scan_config))
        if commodity_needs:
            needs.extend(commodity_needs)
            policy = commodity_data.policy(policy, methods, needs, start, scan=bool(scan_config))
            for m in selected:
                m['missing'] = [
                    '최신 원자료의 실제 확보 여부는 실행 결과에서 확인한다. 미래 수익·개인 계좌/보유 조건은 미확인이다.'
                ]
                m['scope_note'] = (
                    '해당 원자재의 실제 수급·정의별 선물과 상품을 직접 조사한다. 다른 시장 자료로 결측을 대신하지 않는다.'
                )
    if semi_needs:
        if (
            catalog.semiconductor.get('schema_version') != 'semiconductor-coverage-v1'
            or catalog.semiconductor.get('method_version') != SEMICONDUCTOR_VERSION
        ):
            raise SourceError('unsupported semiconductor coverage registry')
        needs.extend(semi_needs)
        policy = semiconductor_policy(policy, catalog.semiconductor, needs)
        for method in methods:
            if method['id'] not in ('SAMSUNG', 'SK_HYNIX'):
                continue
            method['missing'] = [
                'DART 원공시 본문·정정판·이익 귀속의 교차 확인',
                '현재 주식 수·우선주/지배주주 자본 귀속을 맞춘 시가총액·P/B',
                '정의·기간·발표일이 확인된 forward consensus와 revision',
            ]
            method['scope_note'] = (
                '보통주 표시 종가와 기간별 실제 EPS를 연결한다. 공식 재무제표·DART 등록·제공자 재무 입력을 구분하며 잠정 배수를 투자 우위로 확정하지 않는다.'
            )
    if needs:
        validate_policy(policy)
        for method in methods:
            if method['id'] == 'BTC':
                method['missing'] = [
                    '검증된 가치 대용 지표와 가격 매력·반대 논리의 의미 검토',
                    '거래소·계약·토론 표본의 대표성과 원자료의 독립 교차 확인',
                ]
                method['scope_note'] = (
                    '질문에 선택한 Bitcoin 근거만 새 출처에서 확인한다. 거래소·ETF·내러티브의 정의와 확인 범위를 구분한다.'
                )
    for item in methods:
        unresolved.extend(item['label'] + ': ' + note for note in item['missing'])
    data = dict(
        schema_version='ask-input-v1',
        question=question,
        plan=plan.to_dict(),
        methods=methods,
        tasks=tasks,
        unresolved=list(dict.fromkeys(unresolved)),
        portfolio=portfolio,
        synthetic=catalog.synthetic or bool((portfolio or {}).get('synthetic')),
        catalog_sha256=catalog.digest,
        method_versions=METHOD_VERSIONS,
        as_of=None,
        has_sources=False,
        has_macro=False,
        quoted_facts=catalog.quoted_facts,
        findings=list(catalog.findings),
    )
    from .orchestrator_report import EXPLANATORY_REPORT_VERSION

    data['report_style'] = EXPLANATORY_REPORT_VERSION
    from .source_pipeline import OBSERVATION_DATES_VERSION

    data['observation_dates_version'] = OBSERVATION_DATES_VERSION
    data['method_versions'] = {**data['method_versions'], 'observation_dates': OBSERVATION_DATES_VERSION}
    if catalog.discovery is not None:
        from .evidence_guard import VERSION as GUARD_VERSION

        data['evidence_validation'] = {'method_version': GUARD_VERSION, 'numeric_ids': []}
        data['method_versions'] = {**data['method_versions'], 'evidence_validation': GUARD_VERSION}
    if commodity_needs:
        data['commodity_coverage'] = deepcopy(catalog.commodity)
        data['method_versions'] = {**data['method_versions'], 'commodity': commodity_data.VERSION}
    data['plan']['execution_status'] = 'dispatched'
    if reference:
        data['reference_resolution'] = reference
        data['method_versions'] = {**data['method_versions'], 'follow_up': scan.REFERENCE_VERSION}
    if scan_config:
        data['scan'] = deepcopy(scan_config)
        data['method_versions'] = {**data['method_versions'], 'scan': scan_config['method_version']}
        if scan_config['method_version'] in scan.MINIMUM_VERSIONS:
            from .scan_coverage import VERSION as MINIMUM_VERSION, HISTORY_VERSION

            data['method_versions'] = {
                **data['method_versions'],
                'minimum_evidence': MINIMUM_VERSION,
                'scan_comparison': HISTORY_VERSION,
            }
            if scan_config['method_version'] == 'evidence_shortlist_v7':
                from .scan_coverage import FOUR_ASSET_VERSION

                data['method_versions']['scan_four_assets'] = FOUR_ASSET_VERSION
            if anchor:
                data['previous_scan'] = anchor
    if scan_config or decision_plan is not None:
        from .decision_data import VERSION as INVESTMENT_VERSION, digest as decision_digest

        data['investment_cycle_version'] = INVESTMENT_VERSION
        data['method_versions'] = {**data['method_versions'], 'investment_cycle': INVESTMENT_VERSION}
        if decision_plan is not None:
            data['investment_plan_sha256'] = decision_digest(decision_plan)
        if previous_investment is not None:
            data['previous_investment'] = previous_investment
    if uses_korean:
        data['korean_coverage'] = deepcopy(catalog.korean)
        data['method_versions'] = {**data['method_versions'], 'korean_data': KOREAN_DATA_VERSION}
    if semi_needs:
        data['semiconductor_coverage'] = deepcopy(catalog.semiconductor)
        data['method_versions'] = {**data['method_versions'], 'semiconductor': SEMICONDUCTOR_VERSION}
    source_data = project_sources(catalog, methods, question, start.date()) if methods else None
    source_data = scoped_catalog_sources(source_data, needs)
    selected_evidence = {e['id'] for e in source_data['evidence']} if source_data else set()
    selected_facts = [f for f in catalog.quoted_facts['facts'] if f['source_evidence_id'] in selected_evidence]
    selected_fact_ids = {f['id'] for f in selected_facts}
    data['quoted_facts'] = {
        'facts': selected_facts,
        'calculations': [c for c in catalog.quoted_facts['calculations'] if set(c['input_ids']) <= selected_fact_ids],
    }
    selected_assets = {m['id'] for m in methods}
    data['findings'] = [f for f in catalog.findings if set(f['asset_ids']) & selected_assets]
    macro_ids = {identifier for item in methods for identifier in item['macro_ids']}
    if commodity_needs and any(m['id'] in ('GOLD', 'BROAD_COMMODITIES') for m in methods):
        macro_ids.update((CPI, 'US_TREASURY_NOMINAL_10Y'))
    if ResearchMode.OPPORTUNITY_SCAN in plan.modes and not dated:
        macro_ids.add(CPI)
    macro_data = project_macro(catalog, macro_ids - set(KR_RATES))
    if set(macro_ids) & set(KR_RATES):
        kr_macro = ecos_macro_plan(start.date(), question)
        if macro_data:
            for key in ('series', 'sources', 'bindings'):
                macro_data[key].extend(kr_macro[key])
        else:
            macro_data = kr_macro
    if scan_config and scan_config['method_version'] in scan.MINIMUM_VERSIONS and not dated:
        from .scan_minimum import macro_context

        context = macro_context(start.date(), question)
        if macro_data:
            for key in ('series', 'sources', 'bindings'):
                macro_data[key].extend(context[key])
        else:
            macro_data = context
    root = Path(directory)
    if root.exists():
        raise SourceError('run directory already exists; use a new directory or --replay')
    root.mkdir(parents=True, exist_ok=False)
    _save(root / 'started.json', {'question': question, 'started_at': start.isoformat(), 'state': 'acquiring'})
    try:
        acquisition_fetcher = fetcher
        if needs:
            record, acquisition_fetcher = discover_sources(needs, policy, fetcher=fetcher, now=now, progress=progress)
            _save(root / 'discovery.json', record)
            data.update(
                has_discovery=True,
                discovery_sha256=_digest(record),
                evidence_needs=needs,
                method_versions={
                    **data['method_versions'],
                    'discovery': DISCOVERY_VERSION,
                    'discovery_contracts': CONTRACT_VERSION,
                },
            )
            source_data = attach_discovery(
                source_data, record, question, _time(record['selection_as_of']).date(), [m['id'] for m in methods]
            )
            if source_data and commodity_needs:
                source_data['scan_extension'] = 'commodity_deep_v1'
            if (
                source_data
                and scan_config
                and scan_config['method_version'] == 'evidence_shortlist_v7'
                and not commodity_needs
            ):
                source_data['scan_extension'] = 'four_asset_minimum_v2'
            selected_evidence = {e['id'] for e in source_data['evidence']} if source_data else set()
            data['findings'] = [f for f in data['findings'] if set(f['evidence_ids']) <= selected_evidence]
            if source_data and korean_needs:
                for method in methods:
                    if not supports_discovery(method['id']):
                        continue
                    refs = [
                        e['id']
                        for e in source_data['evidence']
                        if method['id']
                        in next(s['asset_ids'] for s in source_data['sources'] if s['id'] == e['source_id'])
                    ]
                    source_data['claims'] = [
                        c for c in source_data['claims'] if c['id'] != 'ASK_THESIS_' + method['id']
                    ]
                    source_data['claims'].append(
                        dict(
                            id='ASK_THESIS_' + method['id'],
                            text=method['bull_question'],
                            asset_ids=[method['id']],
                            rule='reviewed_links_v1',
                            support_ids=[],
                            counter_ids=[],
                            context_ids=refs,
                            narrative_evidence_id=None,
                            verification='unverified',
                            review=None,
                            limitations=['원문·수치 확인을 투자 가격 매력·개인 적절성의 증명으로 승격하지 않는다.'],
                            recheck=method['bear_question'],
                        )
                    )
            if (
                source_data
                and 'BTC' in selected_assets
                and not any(c['id'] == 'ASK_THESIS_BTC' for c in source_data['claims'])
            ):
                source_data['claims'].append(
                    dict(
                        id='ASK_THESIS_BTC',
                        text='현재 확인한 수요·비용·가격 근거가 Bitcoin의 보유 경제성을 충분히 설명하는가?',
                        asset_ids=['BTC'],
                        rule='reviewed_links_v1',
                        support_ids=[],
                        counter_ids=[],
                        context_ids=[
                            e['id']
                            for e in source_data['evidence']
                            if e['kind'] != 'observed_narrative'
                            and 'BTC'
                            in next(s['asset_ids'] for s in source_data['sources'] if s['id'] == e['source_id'])
                        ],
                        narrative_evidence_id=None,
                        verification='unverified',
                        review=None,
                        limitations=['새 관측값을 확보해도 가격 매력·미래 수익은 자동 확정하지 않는다.'],
                        recheck='근거의 대표성·반대 논리·적정 가치 방법을 검토한다.',
                    )
                )
        if source_data:
            source_data['observation_dates_version'] = OBSERVATION_DATES_VERSION
            acquisition_path = root / ('acquisition_plan.json' if needs else 'source_plan.json')
            _save(acquisition_path, source_data)
            source_plan = load_source_plan(acquisition_path)
            pins = acquire_plan(
                source_plan, root / 'source_snapshots', fetcher=acquisition_fetcher, now=now, progress=progress
            )
            _save(root / 'source_pins.json', pins)
            data['has_sources'] = True
        if macro_data:
            _save(root / 'macro_plan.json', macro_data)
            macro_plan = load_macro_plan(root / 'macro_plan.json')
            if progress:
                progress('질문에 필요한 거시 자료 확인')
            pins = acquire_macro(macro_plan, root / 'macro_snapshots', fetcher=acquisition_fetcher, now=now)
            _save(root / 'macro_pins.json', pins)
            data['has_macro'] = True
        cutoff = now or datetime.now(timezone.utc)
        data['as_of'] = cutoff.isoformat()
        if source_data and needs:
            # Quote verification finishes after discovery. An ask crossing UTC
            # midnight must not claim its verification predates the snapshot.
            # Keep the acquisition input immutable and save a separate final
            # plan; pins bind unchanged SourceSpecs, not review-date prose.
            for item in source_data['evidence']:
                review = item.get('interpretation')
                if item['source_id'].startswith('DISC_') and review and review['status'] == 'reviewed':
                    review['reviewed_at'] = cutoff.date().isoformat()
            for item in source_data['claims']:
                if (
                    item['id'].startswith('DISC_COMMUNITY_CLAIM_')
                    and item.get('review', {}).get('status') == 'reviewed'
                ):
                    item['review']['reviewed_at'] = cutoff.date().isoformat()
            _save(root / 'source_plan.json', source_data)
        profile = {
            name: asdict(value) for name, value in review_portfolio(portfolio, cutoff.date()).profile.fields.items()
        }
        if source_data and macro_data:
            review = _review(methods, source_data, cutoff, profile, discovery=bool(needs))
            _save(root / 'evidence_review.json', review)
            if ResearchMode.OPPORTUNITY_SCAN in plan.modes:
                _save(root / 'opportunity_review.json', review)
            if 'US_EQUITY' in source_data['asset_ids']:
                _save(root / 'deep_review.json', _deep_review(data, source_data, cutoff, profile))
        if data.get('evidence_validation') and source_data:
            data['evidence_validation']['numeric_ids'] = [
                e['id'] for e in source_data['evidence'] if e['extraction'] is not None
            ]
        if data.get('investment_cycle_version'):
            if decision_plan is not None:
                _save(root / 'investment_plan.json', decision_plan)
            if decision_journal is not None:
                from .decision_journal import feedback

                data['strategy_feedback'] = feedback(decision_journal, data['as_of'])
        _save(root / 'input.json', data)
        run = _execute(root, data)
        if run.investment:
            from .decision_journal import record

            _save(root / 'investment_decision.json', run.investment)
            record(root / 'investment_journal', run.investment)
            if decision_journal is not None:
                record(decision_journal, run.investment)
        if data.get('observation_dates_version'):
            from .orchestrator_report import observation_audit

            _save(root / 'observation_integrity.json', observation_audit(run))
        if run.evidence_validation:
            _save(root / 'evidence_validation.json', run.evidence_validation)
        if commodity_needs:
            from .commodity_report import assessment

            _save(root / 'commodity_research.json', assessment(run))
        if semi_needs:
            _save(root / 'company_comparison.json', semiconductor_audit(run))
        if scan_config:
            assessment = scan.assess(run)
            _save(root / 'shortlist.json', assessment)
            if scan_config['method_version'] in scan.MINIMUM_VERSIONS:
                _save(
                    root / 'scan_observations.json',
                    {
                        'method_version': 'minimum_opportunity_evidence_v1',
                        'as_of': data['as_of'],
                        'observations': assessment['observations'],
                    },
                )
                _save(root / 'scan_changes.json', assessment['since_previous_scan'])
            if run.opportunity:
                _save(root / 'shortlist_review.json', run.opportunity.review.data)
        from .orchestrator_report import build_manifest, render_ask_report

        report = render_ask_report(run)
        with (root / 'report.md').open('x', encoding='utf-8', newline='\n') as handle:
            handle.write(report)
        _save(root / 'run_manifest.json', build_manifest(run, report))
        return run
    except Exception as exc:
        if not (root / 'failed.json').exists():
            _save(
                root / 'failed.json', {'state': 'failed', 'error_type': type(exc).__name__, 'message': str(exc)[:1000]}
            )
        raise


def replay_ask(directory, *, question=None):
    root = Path(directory)
    data = load_pins(root / 'input.json')
    # Manifests contain bounded output evidence, not acquisition instructions.
    # Keep the shared 1MiB pins/input limit; allow up to 2MiB only for this
    # already-created output, including the first coverage probe's rich audit.
    manifest_path = root / 'run_manifest.json'
    if manifest_path.stat().st_size > 2 * 1024 * 1024:
        raise SourceError('ask manifest exceeds output size limit')
    saved = _parse_json(manifest_path.read_text(encoding='utf-8'))
    # Stored scopes are replayed, never routed again. Preserve older routing
    # inputs and reports while new questions use the refined BTC ETF grammar.
    routing = data.get('method_versions', {}).get('routing')
    if routing not in ('research_routing_v2', 'research_routing_v3', 'research_routing_v4', ROUTING_VERSION):
        raise SourceError('unsupported ask routing version')
    expected = {
        **METHOD_VERSIONS,
        'routing': routing,
        **({'korean_data': KOREAN_DATA_VERSION} if data.get('korean_coverage') else {}),
        **({'semiconductor': SEMICONDUCTOR_VERSION} if data.get('semiconductor_coverage') else {}),
        **({'scan': data['scan']['method_version']} if data.get('scan') else {}),
        **(
            {
                'minimum_evidence': 'minimum_opportunity_evidence_v1',
                'scan_comparison': 'same_definition_scan_comparison_v1',
            }
            if data.get('scan', {}).get('method_version') in scan.MINIMUM_VERSIONS
            else {}
        ),
        **({'follow_up': scan.REFERENCE_VERSION} if data.get('reference_resolution') else {}),
        **(
            {'scan_four_assets': 'four_asset_minimum_v2'}
            if data.get('scan', {}).get('method_version') == 'evidence_shortlist_v7'
            else {}
        ),
        **(
            {'discovery': DISCOVERY_VERSION, 'discovery_contracts': CONTRACT_VERSION}
            if data.get('has_discovery')
            else {}
        ),
    }
    if data.get('evidence_validation'):
        from .evidence_guard import VERSION as GUARD_VERSION

        expected['evidence_validation'] = GUARD_VERSION
    if data.get('observation_dates_version'):
        from .source_pipeline import OBSERVATION_DATES_VERSION

        if data['observation_dates_version'] != OBSERVATION_DATES_VERSION:
            raise SourceError('unsupported observation date method')
        expected['observation_dates'] = OBSERVATION_DATES_VERSION
    if data.get('commodity_coverage'):
        from .commodity_data import VERSION as COMMODITY_VERSION

        expected['commodity'] = COMMODITY_VERSION
    if data.get('investment_cycle_version'):
        from .decision_data import VERSION as INVESTMENT_VERSION

        if data['investment_cycle_version'] != INVESTMENT_VERSION:
            raise SourceError('unsupported investment cycle version')
        expected['investment_cycle'] = INVESTMENT_VERSION
    if data.get('schema_version') != 'ask-input-v1' or data.get('method_versions') != expected:
        raise SourceError('unsupported ask replay or changed method versions')
    if question is not None and question.strip() != data['question'].strip():
        raise SourceError('replay preserves the original question; run a new ask for a changed question')
    if _digest(data) != saved['request_sha256']:
        raise SourceError('ask input checksum mismatch')
    for relative, digest in saved['artifact_sha256'].items():
        path = Path(relative)
        if path.is_absolute() or '..' in path.parts:
            raise SourceError('unsafe replay artifact path')
        import hashlib

        if not (root / path).is_file() or hashlib.sha256((root / path).read_bytes()).hexdigest() != digest:
            raise SourceError('ask replay artifact checksum mismatch: ' + relative)
    run = _execute(root, data)
    if run.investment:
        from .decision_data import load as load_decision

        if load_decision(root / 'investment_decision.json') != run.investment:
            raise SourceError('investment decision replay differs')
    if data.get('evidence_validation') and load_pins(root / 'evidence_validation.json') != run.evidence_validation:
        raise SourceError('evidence quarantine validation replay differs')
    if data.get('commodity_coverage'):
        from .commodity_report import assessment

        if load_pins(root / 'commodity_research.json') != assessment(run):
            raise SourceError('commodity research audit replay differs')
    if data.get('semiconductor_coverage') and load_pins(root / 'company_comparison.json') != semiconductor_audit(run):
        raise SourceError('semiconductor comparison audit replay differs')
    if data.get('scan'):
        scan.validate(data['scan'])
        if load_pins(root / 'shortlist.json') != scan.assess(run):
            raise SourceError('opportunity shortlist replay differs')
        if run.opportunity and load_pins(root / 'shortlist_review.json') != run.opportunity.review.data:
            raise SourceError('opportunity shortlist review replay differs')
        if data['scan']['method_version'] in scan.MINIMUM_VERSIONS:
            a = scan.assess(run)
            if load_pins(root / 'scan_changes.json') != a['since_previous_scan'] or load_pins(
                root / 'scan_observations.json'
            ) != {
                'method_version': 'minimum_opportunity_evidence_v1',
                'as_of': data['as_of'],
                'observations': a['observations'],
            }:
                raise SourceError('Scan comparison observations replay differs')
    from .orchestrator_report import report_version, render_ask_report

    if data.get('observation_dates_version'):
        from .orchestrator_report import observation_audit

        if load_pins(root / 'observation_integrity.json') != observation_audit(run):
            raise SourceError('observation date audit replay differs')
    if saved.get('method_versions') != {**expected, 'report': report_version(run)}:
        raise SourceError('unsupported ask report method versions')
    report = render_ask_report(run)
    if report.encode() != (root / 'report.md').read_bytes() or run.digest != saved['input_sha256']:
        raise SourceError('ask replay differs; preserve the original and inspect changed methods')
    # The saved manifest carries its creation code hash; replay validates method
    # and input/results instead of pretending code upgrades were the old code.
    return run
