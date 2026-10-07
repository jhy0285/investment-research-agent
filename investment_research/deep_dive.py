"""Offline, source-linked financial transcription and descriptive Deep Dive.

The existing opportunity replay supplies source/macro time checks and core models.
This module adds bounded quoted scalars and three explicit calculations. It never
infers economic truth, returns, fair value, allocation, or community consensus.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from datetime import date, datetime
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from pathlib import Path
import re

from .engine import run_research
from .models import EvidenceRecord, InterpretationStatus, MetricResult, ResearchClaim, Review, VerificationStatus
from .opportunity import OpportunityReview, OpportunityRun, replay_opportunity, validate_profile
from .source_pipeline import SourcePlan, _decimal, _digest, _id, _list, _object, _strings, _text, load_pins
from .sources import SourceError, _time

DEEP_DIVE_VERSION = 'deep_dive_v1'
SECTIONS = ('conclusions','priced_expectations','denominator','revisions','actual_results','ai_chain',
            'concentration','treasury','bull_case','base_case','bear_case','community','narrative_gaps',
            'reassessment','current_judgment','korean_context','easy')
JUDGMENTS = {'valuation looks compelling','reasonable but dependent on earnings delivery','mixed',
             'expectations appear demanding','insufficient evidence'}
PE_BASES = {'forward_12m_pe','forward_fy1_harmonic_pe','trailing_pe'}
BASES = PE_BASES | {'nominal_cmt_investment_yield','reported_financial','reported_statistic',
                   'operating_cash_flow','cash_ppe_outflow','management_run_rate','index_weight'}
UNITS = {'ratio','percent','percentage_points','USD_million','USD_billion','USD_per_share','count'}
TABLE_IDS = {'VALUATION','REVISIONS','QUARTERS','ACTUALS','CASH','DEPRECIATION','CAPEX_GUIDANCE',
             'CONCENTRATION','TREASURY','YIELD_GAPS'}
CONTEXT = Context(prec=50, rounding=ROUND_HALF_EVEN)


def _financial_numerals(text):
    # Named indices, accounting forms and a provider's FY1 method are labels,
    # not permission to type a valuation or monetary amount into prose.
    labels=r'(?<![A-Za-z0-9_])(?:S&P 500|Nasdaq-100|FY1|Mag7|Magnificent 7|10-Q|10-K|8-K)(?![A-Za-z0-9_])'
    return re.search(r'[0-9]',re.sub(labels,'',text)) is not None


def _prose(value, path):
    text = _text(value,path)
    if len(text)>3000 or _financial_numerals(text):
        raise SourceError(path+': financial numerals belong in source-linked facts, not authored prose')
    return text


def _statement(item,path):
    _object(item,{'text','evidence_ids','role'},set(),path)
    _prose(item['text'],path+'.text')
    _strings(item['evidence_ids'],path+'.evidence_ids',True)
    if not isinstance(item['role'],str) or item['role'] not in {'interpretation','narrative','definition'}:
        raise SourceError(path+': unsupported statement role')


@dataclass(frozen=True)
class DeepDiveReview:
    data: dict
    input_digest: str

    @property
    def as_of(self): return _time(self.data['as_of'])


def load_deep_dive_review(path: str|Path) -> DeepDiveReview:
    path=Path(path);path=path/'review.json' if path.is_dir() else path
    data=load_pins(path)
    _object(data,{'schema_version','id','question','as_of','author','review_status',
                 'facts','calculations','tables','sections','judgment','comparison_limits',
                 'sampling_limits','unknowns','next_research'},{'parent','profile','horizon'},'deep dive review')
    if data['schema_version']!='deep-dive-review-v1' or data['review_status']!='draft':
        raise SourceError('Deep Dive requires explicit draft schema')
    _id(data['id'],'id')
    for name in ('question','author','next_research'): _prose(data[name],name)
    cutoff=_time(data['as_of'])
    if cutoff is None or len(data['as_of'])==10: raise SourceError('exact aware cutoff required')
    parent=data.get('parent')
    if parent is not None:
        _object(parent,{'id','review_sha256','input_sha256'},set(),'parent')
        _id(parent['id'],'parent.id')
        for name in ('review_sha256','input_sha256'):
            if not isinstance(parent[name],str) or not re.fullmatch(r'[a-f0-9]{64}',parent[name]):
                raise SourceError('parent: explicit hashes required')
    if ('profile' in data)!=('horizon' in data) or (parent is None and 'profile' not in data):
        raise SourceError('standalone Deep Dive requires its own profile and horizon; unknowns may be explicit')
    if 'profile' in data:
        validate_profile(data['profile'])
        _prose(data['horizon'],'horizon')
    ids=[data['id']]
    for index,fact in enumerate(_list(data['facts'],'facts')):
        p=f'facts[{index}]'
        _object(fact,{'id','label','source_evidence_id','quote_context','quote_token','value',
                      'unit','currency','observed_at','entity','window','basis','source_definition'},{'qualifier'},p)
        ids.append(_id(fact['id'],p+'.id'));_id(fact['source_evidence_id'],p+'.source_evidence_id')
        for name in ('label','quote_context','quote_token','entity','window'): _text(fact[name],p+'.'+name)
        _decimal(fact['value'],p+'.value')
        if not isinstance(fact.get('qualifier','reported'),str) or fact.get('qualifier','reported') not in {'reported','above','below','approximate'}:
            raise SourceError(p+': unsupported scalar qualifier')
        if (not isinstance(fact['unit'],str) or fact['unit'] not in UNITS
                or not isinstance(fact['basis'],str) or fact['basis'] not in BASES
                or not (fact['currency'] is None or fact['currency']=='USD')):
            raise SourceError(p+': unsupported scalar definition')
        try: date.fromisoformat(fact['observed_at'])
        except (TypeError,ValueError): raise SourceError(p+': observed_at requires YYYY-MM-DD')
        _object(fact['source_definition'],{'measure','unit','period','currency','scope','adjustment'},set(),p+'.source_definition')
    for index,calc in enumerate(_list(data['calculations'],'calculations')):
        p=f'calculations[{index}]'
        _object(calc,{'id','label','method','input_ids','limitations'},set(),p)
        ids.append(_id(calc['id'],p+'.id'));_text(calc['label'],p+'.label')
        _strings(calc['input_ids'],p+'.input_ids',True)
        if not isinstance(calc['method'],str) or calc['method'] not in {'earnings_yield_v1','descriptive_yield_gap_v1','cash_residual_v1'}:
            raise SourceError(p+': unsupported calculation')
        for note in _strings(calc['limitations'],p+'.limitations'): _prose(note,p+'.limitations')
    if len(ids)!=len(set(ids)): raise SourceError('duplicate Deep Dive IDs')
    _object(data['sections'],set(SECTIONS),set(),'sections')
    for key,items in data['sections'].items():
        for index,item in enumerate(_list(items,'sections.'+key)): _statement(item,f'sections.{key}.{index}')
    if not 3<=len(data['sections']['conclusions'])<=5 or len(data['sections']['easy'])>7:
        raise SourceError('Deep Dive needs three to five conclusions and at most seven easy sentences')
    if not isinstance(data['judgment'],str) or data['judgment'] not in JUDGMENTS:
        raise SourceError('unsupported qualitative judgment')
    for name in ('comparison_limits','sampling_limits','unknowns'):
        for note in _strings(data[name],name): _prose(note,name)
    table_ids=set()
    for table in _list(data['tables'],'tables'):
        _object(table,{'id','title','columns','rows','notes'},set(),'table')
        _id(table['id'],'table.id');_text(table['title'],'table.title')
        if table['id'] not in TABLE_IDS or table['id'] in table_ids:
            raise SourceError('unknown or duplicate rendered table ID')
        table_ids.add(table['id'])
        columns=_strings(table['columns'],'table.columns')
        if not 2<=len(columns)<=8: raise SourceError('bounded table columns required')
        for row in _list(table['rows'],'table.rows'):
            if not isinstance(row,list) or len(row)!=len(columns): raise SourceError('table row width mismatch')
            for cell in row:
                _object(cell,{'text','refs'},set(),'table cell')
                if not isinstance(cell['text'],str) or len(cell['text'])>3000:
                    raise SourceError('table cell.text: bounded text required')
                _strings(cell['refs'],'table cell.refs',True)
                if _financial_numerals(cell['text']) and cell['refs']:
                    raise SourceError('table financial values must use referenced scalar insertion')
                if _financial_numerals(cell['text']) and not re.fullmatch(r'\d{4}-\d{2}-\d{2}',cell['text']):
                    raise SourceError('table numerals must be a quoted scalar or explicit date/index label')
        for note in _strings(table['notes'],'table.notes'): _prose(note,'table.notes')
    return DeepDiveReview(data,_digest(data))


def _adapter(review,plan,profile,horizon):
    """Reuse the existing time-aware source/macro integration, not another engine."""
    statement={'text':'후속 연구의 원문과 비교 조건을 보존한다.','evidence_ids':[]}
    rows=[]
    names={'US_EQUITY':'미국 주식','SHORT_BOND':'단기 국채','INTERMEDIATE_BOND':'중기 국채',
           'LONG_BOND':'장기 국채','GROWTH':'성장 특성'}
    for asset in plan.asset_ids:
        rows.append(dict(asset_id=asset,name=names.get(asset,asset),exposure='명시한 노출의 조사 범위',
            return_definition='달러 원천의 회계 이익·현금흐름·수익률 정의를 구분한다.',liquidity='상품·개인 조건 미확인',
            state=deepcopy(statement),positive=deepcopy(statement),negative=deepcopy(statement),
            uncertainty=['개인 실행 조건과 미래 보상 미확인'],
            opportunity_cost={**deepcopy(statement),'alternative_ids':[a for a in plan.asset_ids if a!=asset]},
            priority='monitor',priority_reason=deepcopy(statement),recheck=deepcopy(statement),candidate=None))
    data=dict(schema_version='opportunity-review-v1',id=review.data['id']+'_INTEGRATION',
        question=review.data['question'],as_of=review.data['as_of'],author=review.data['author'],review_status='draft',
        profile=deepcopy(profile),horizon=horizon,
        comparison_limits=review.data['comparison_limits'],rows=rows,
        sections={key:[] for key in ('overview','drivers','market_narratives','community','gaps','korean_context','unknowns','easy')},
        next_research={'asset_id':'US_EQUITY','title':'후속 질문','question':'새 자료로 이익의 반복성과 가격 조건을 확인한다.'},
        sampling_limits=review.data['sampling_limits'],access_notes=[])
    return OpportunityReview(data,_digest(data))


def _quoted_decimal(token):
    # Preserve parentheses as negative cash flow; no inferred unit scaling.
    text=token.replace(',','').replace('$','').replace('%','').strip()
    if text.startswith('(') and text.endswith(')'): text='-'+text[1:-1].strip()
    return _decimal(text,'quote token')


@dataclass(frozen=True)
class DeepDiveRun:
    review: DeepDiveReview
    integration: OpportunityRun
    parent: OpportunityRun | None
    case: object
    result: object
    facts: tuple[dict,...]
    metrics: tuple[MetricResult,...]
    sections: dict
    diagnostics: tuple[str,...]
    input_digest: str

    @property
    def effective_judgment(self):
        # A heading must not leak a conclusion whose decisive references failed.
        items=self.sections['current_judgment']
        if not items or any(item['status']=='withheld' or item['role']!='interpretation' for item in items):
            return 'insufficient evidence'
        references={ref for item in items for ref in item['evidence_ids']}
        inputs={ref for metric in self.metrics if metric.id in references for ref in metric.input_ids}
        usable=[f for f in self.facts if f['status']=='available' and f['id'] in references|inputs]
        if not any(f['basis'] in PE_BASES for f in usable) or not any(f['basis']=='nominal_cmt_investment_yield' for f in usable):
            return 'insufficient evidence'
        return self.review.data['judgment']


def replay_deep_dive(review,plan,store,pins,macro_plan,macro_store,macro_pins,parent=None):
    if _digest(review.data)!=review.input_digest: raise SourceError('review mutated; reload explicit input')
    if review.data.get('parent') is not None:
        if parent is None: raise SourceError('linked parent Opportunity Map must be supplied for provenance')
        if _digest(parent.review.data)!=parent.review.input_digest:
            raise SourceError('parent review mutated; replay explicit linked context')
        expected={'id':parent.review.id,'review_sha256':parent.review.input_digest,'input_sha256':parent.input_digest}
        if review.data['parent']!=expected: raise SourceError('parent Opportunity Map hashes do not match')
        if review.as_of<parent.review.as_of: raise SourceError('Deep Dive cannot precede linked context')
    elif parent is not None:
        raise SourceError('unexpected parent: standalone review must not silently inherit Scan context')
    profile=review.data.get('profile',parent.review.data['profile'] if parent else None)
    horizon=review.data.get('horizon',parent.review.data['horizon'] if parent else None)
    if profile is None or horizon is None: raise SourceError('explicit profile and horizon required')
    if 'US_EQUITY' not in plan.asset_ids: raise SourceError('US equity scope required')
    integrated=replay_opportunity(_adapter(review,plan,profile,horizon),plan,store,pins,macro_plan,macro_store,macro_pins)
    base={item.id:item for item in integrated.case.evidence};sources={s.id:s for s in integrated.case.sources}
    evidence=list(integrated.case.evidence);facts=[];pending=Review(InterpretationStatus.PENDING,None,None,'원문 숫자의 전사 확인은 경제적 의미·투자 판단의 확인과 다르다.')
    occupied={s.id for s in integrated.case.sources}|set(base)|{m.id for m in integrated.result.metrics}|set(plan.asset_ids)
    def source_ok(item,role='interpretation'):
        if item is None or item.provenance is None:return False
        source=sources[item.source_id]
        if item.provenance.match_status!='matched' or _time(source.provenance.retrieved_at)>review.as_of:return False
        if item.provenance.freshness=='fresh':return role=='narrative' or item.kind!='observed_narrative'
        return role=='definition' and item.provenance.freshness=='unknown' and item.kind!='observed_narrative'
    for spec in review.data['facts']:
        if spec['id'] in occupied: raise SourceError('fact ID collides with existing research records')
        occupied.add(spec['id']);item=base.get(spec['source_evidence_id'])
        if item is None:
            if spec['source_evidence_id'] not in {e['id'] for e in plan.evidence}:raise SourceError('unknown scalar evidence reference')
            facts.append({**spec,'status':'withheld','reason':'source unavailable'});continue
        if item.kind=='observed_narrative':raise SourceError('community numbers cannot become financial scalars')
        if spec['source_definition']!=item.provenance.definition or spec['currency']!=item.provenance.definition['currency']:
            raise SourceError('scalar source definition/currency mismatch')
        declared_unit=spec['source_definition']['unit'].lower()
        aliases={'ratio':('ratio',),'percent':('percent',),'percentage_points':('percentage_points','percentage points'),
                 'USD_million':('million',),'USD_billion':('billion',),
                 'USD_per_share':('usd/share','per share'),'count':('count',)}
        if not any(alias in declared_unit for alias in aliases[spec['unit']]):
            raise SourceError('scalar unit cannot silently scale the source amount')
        context=spec['quote_context'];token=spec['quote_token']
        if context not in item.text or token not in context or len(context)>1200:
            raise SourceError(spec['id']+': scalar quote context/token not present in retained evidence')
        # Exact bounded token prevents 19 matching 19.8, and money words are not parsed.
        pattern=r'(?<![\w.])'+re.escape(token)+r'(?!\w|\.\d)'
        if len(re.findall(pattern,context))!=1 or _quoted_decimal(token)!=_decimal(spec['value'],'value'):
            raise SourceError(spec['id']+': scalar token is ambiguous or differs from supplied value')
        match=re.search(pattern,context)
        if (spec['unit'] in {'USD_million','USD_billion','USD_per_share'}
                and not token.strip().startswith('(')
                and re.search(r'\(\s*\$?\s*$',context[:match.start()])
                and re.match(r'\s*\)',context[match.end():])):
            raise SourceError(spec['id']+': retain the accounting parentheses and negative sign')
        available=source_ok(item) and date.fromisoformat(spec['observed_at'])<=review.as_of.date()
        fact={**spec,'status':'available' if available else 'withheld','reason':'' if available else 'source freshness or exact cutoff'}
        facts.append(fact)
        if available:
            narrow={**item.provenance.definition,'measure':spec['label'],'unit':spec['unit'],
                    'period':spec['window'],'scope':spec['entity']}
            evidence.append(replace(item,id=spec['id'],text=context,observed_at=date.fromisoformat(spec['observed_at']),
                value=_decimal(spec['value'],'value'),unit=spec['unit'],period=spec['window'],currency=spec['currency'],
                verification=VerificationStatus.SUPPORTED,interpretation=pending,
                provenance=replace(item.provenance,definition=narrow),
                limitations=(*item.limitations,'quoted_scalar_v1: exact token and declared context/definition checked; semantic field mapping is authored review, not automatic source audit')))
    by_fact={f['id']:f for f in facts};new_metrics=[]
    for calc in review.data['calculations']:
        if calc['id'] in occupied:raise SourceError('calculation ID collision')
        occupied.add(calc['id']);refs=calc['input_ids'];arity=1 if calc['method']=='earnings_yield_v1' else 2
        if len(refs)!=arity or any(ref not in by_fact for ref in refs):raise SourceError('calculation needs explicit quoted-scalar inputs')
        fs=[by_fact[ref] for ref in refs]
        if any(f['status']!='available' for f in fs):continue
        if any(f.get('qualifier','reported')!='reported' for f in fs):
            raise SourceError('calculation requires reported values, not bounds or approximations')
        values=[_decimal(f['value'],'value') for f in fs]
        with localcontext(CONTEXT):
            if calc['method'] in {'earnings_yield_v1','descriptive_yield_gap_v1'}:
                if fs[0]['basis'] not in PE_BASES or fs[0]['unit']!='ratio' or values[0]<=0:
                    raise SourceError('earnings yield requires a positive explicitly defined P/E')
                value=Decimal(100)/values[0];unit='percent'
                if calc['method']=='descriptive_yield_gap_v1':
                    if fs[1]['basis']!='nominal_cmt_investment_yield' or fs[1]['unit']!='percent' or fs[1]['currency']!='USD' or fs[0]['currency']!='USD' or fs[0]['observed_at']!=fs[1]['observed_at']:
                        raise SourceError('ratio gap needs same-date USD nominal investment-basis Treasury yield')
                    value-=values[1];unit='percentage_points'
            else:
                if fs[0]['basis']!='operating_cash_flow' or fs[1]['basis']!='cash_ppe_outflow' or values[1]>0 or any(fs[0][key]!=fs[1][key] for key in ('unit','currency','window','entity','observed_at')) or fs[0]['unit'] not in {'USD_million','USD_billion'}:
                    raise SourceError('cash residual needs same-company/window/unit OCF and signed cash PP&E outflow')
                value=values[0]+values[1];unit=fs[0]['unit']
        new_metrics.append(MetricResult(calc['id'],calc['label'],value,unit,calc['method'],tuple(refs),
            tuple(sorted({a for f in fs for a in base[f['source_evidence_id']].asset_ids})),tuple(calc['limitations'])))
    known=set(base)|{e['id'] for e in plan.evidence}|set(by_fact)|{c['id'] for c in review.data['calculations']}|{m.id for m in integrated.result.metrics}
    metric_ids={m.id for m in new_metrics}|{m.id for m in integrated.result.metrics};sections={};claims=[]
    ev={e.id:e for e in evidence}
    for name,items in review.data['sections'].items():
        sections[name]=[]
        for index,item in enumerate(items):
            unknown=set(item['evidence_ids'])-known
            if unknown:raise SourceError('unknown Deep Dive statement reference: '+','.join(sorted(unknown)))
            withheld=[ref for ref in item['evidence_ids'] if ref not in metric_ids and not source_ok(ev.get(ref),item['role'])]
            if item['role']=='interpretation' and not item['evidence_ids']:
                raise SourceError('economic interpretation requires explicit supporting context')
            sections[name].append({**item,'withheld_ids':withheld,'status':'withheld' if withheld else 'draft'})
            claims.append(ResearchClaim('DEEP_DRAFT_'+name+'_'+str(index),item['text'],('US_EQUITY',),
                VerificationStatus.UNVERIFIED,pending,(),(),None,
                ('경제적 해석은 명시한 근거에 연결한 연구 초안이다. 자료 대조와 자동 진실 판정은 다르다.',),
                '새 원자료·반대 근거·가격 조건을 확인하면 재검토한다.',
                tuple(ref for ref in item['evidence_ids'] if ref in ev)))
    for table in review.data['tables']:
        for row in table['rows']:
            for cell in row:
                if set(cell['refs'])-known:raise SourceError('unknown Deep Dive table reference')
                if len(cell['refs'])>1 and cell['text']=='':raise SourceError('numeric table cell needs a single value reference')
    digest=_digest({'review':review.input_digest,'integrated':integrated.input_digest,'parent':parent.input_digest if parent else None,'method':DEEP_DIVE_VERSION})
    metrics=(*integrated.result.metrics,*new_metrics)
    case=replace(integrated.case,brief=replace(integrated.case.brief,id=review.data['id']),evidence=tuple(evidence),
                 claims=tuple(claims),input_digest=digest)
    result=replace(run_research(case),metrics=metrics)
    diagnostics=(*integrated.diagnostics,*(f['id']+': '+f['reason'] for f in facts if f['status']=='withheld'))
    return DeepDiveRun(review,integrated,parent,case,result,tuple(facts),tuple(metrics),sections,tuple(diagnostics),digest)


def deep_dive_manifest(run,report):
    from .__main__ import manifest_for
    from .macro_pipeline import macro_manifest
    from .macro_report import render_macro_report
    manifest=manifest_for(run.result,report)
    manifest.update(kind='us_equity_deep_dive',review_sha256=run.review.input_digest,review_status='draft',
        author=run.review.data['author'],parent=run.review.data.get('parent'),as_of=run.review.data['as_of'],
        judgment={'requested':run.review.data['judgment'],'effective':run.effective_judgment,
                  'status':'draft','economic_truth_automatically_verified':False},
        facts=list(run.facts),sections=run.sections,profile=run.integration.review.data['profile'],
        calculations=run.review.data['calculations'],diagnostics=list(run.diagnostics),
        macro=macro_manifest(run.integration.macro,render_macro_report(run.integration.macro)))
    from .deep_dive_report import DEEP_DIVE_REPORT_VERSION
    manifest['method_versions'].update(deep_dive=DEEP_DIVE_VERSION,quoted_scalar='quoted_scalar_v1',
                                      deep_dive_report=DEEP_DIVE_REPORT_VERSION)
    return manifest
