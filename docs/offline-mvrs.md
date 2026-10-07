# 오프라인 Cross-Asset Research Brief MVP

이 문서는 기존 합성 `research` 경로의 계약을 설명한다. 현재 추가된 실제 자료의 획득·snapshot·주장 연결은 [공개 출처 안내](source-acquisition.md)에 둔다. 합성 parser의 필수 날짜·세 대안·합성 식별자 규칙은 유지하며 실제 자료는 명시적 source plan을 거쳐 같은 연구 모델로 연결한다.

세 대안과 비교 중심 템플릿은 이 합성 fixture의 계약이다. 다른 모드에 적용하는 의무 workflow가 아니다. [네 독립 진입점](research-modes.md)은 실제 질문에 따라 Scan 없이도 Deep Dive·Compare·Portfolio Review를 시작한다. 현재 [ask orchestration](research-orchestrator.md)은 별도 진입 계약으로 기존 source/macro·연구 모델을 재사용하며 이 합성 parser를 변경하지 않는다.

## 실행과 결과

저장소 루트에서 Python 3.12 이상으로 실행한다. 외부 패키지·인터넷·API 키는 필요 없다. Python 3.12.14에서 실행과 테스트를 확인했다.

```bash
python -m investment_research research examples/cross_asset_case
python -m investment_research research examples/cross_asset_case --output reports/brief.md --manifest reports/run.json
python -m unittest discover -v
```

디렉터리 입력은 `case.json`을 읽는다. JSON 파일 경로도 가능하다. `--output`을 생략하면 Markdown을 표준 출력으로 보낸다. `--manifest`는 선택적인 JSON 실행 기록이다. 입력 파일과 출력 파일 충돌, 보고서와 실행 기록의 경로 충돌, 내용이 다른 기존 출력은 거부한다. 같은 내용의 기존 출력은 그대로 두므로 같은 명령을 다시 실행할 수 있다. 운영체제 오류가 쓰기 도중 발생했을 때 여러 출력 파일을 원자적으로 되돌리는 기능은 없다.

| 결과 | 종료 코드 | 보고서 |
| --- | --- | --- |
| 정상 완료·상충·근거 부족·개인 판단 유보 | 0 | 생성 |
| 입력 계약·참조·날짜·계산 전제·출력 경로 검증 위반 (`blocked`) | 2 | 생성하지 않음 |
| 파일 접근·쓰기·실행 오류 (`failed`) | 1 | 정상 보고서로 대체하지 않음 |

[예제 입력](../examples/cross_asset_case/case.json), [생성 보고서](../examples/cross_asset_case/research_brief.md), [실행 기록](../examples/cross_asset_case/run_manifest.json)은 모두 합성 사례다. 기준 시점은 2025-01-31이며 실제 당시 또는 현재 시장을 나타내지 않는다.

## 전체 흐름

`case.json → load_case/parse_case → run_research → render_report → Markdown + 선택적 실행 기록`

1. 질문·기준 시점·사용자 맥락·세 노출과 비교 한계를 읽는다.
2. 엄격한 필드·ID·참조·자산 범위·날짜·원출처 관계·검토 기록·수치 정의를 검사한다.
3. 지지/반대 근거 중 사실 확인과 해석 검토가 모두 완료된 비커뮤니티 근거만 채택한다. 나머지는 이유를 남기고 보류한다.
4. 승인된 계산 방법만 Decimal로 실행한다. 대안의 상충·중복·정보 부족과 사용자 unknown을 별도로 기록한다.
5. 연결된 조건부 기회비용과 재검토 설명을 검사하고 10개 한국어 본문 섹션·근거 부록으로 렌더링한다. 외부 문자열은 Markdown/HTML을 이스케이프하며 실행하지 않는다.

## 자료형과 파일

| 파일 | 역할 |
| --- | --- |
| `investment_research/models.py` | dataclass·상태·출처 유형 |
| `investment_research/validation.py` | 로컬 JSON 파싱과 구조·전제 검사 |
| `investment_research/engine.py` | 적격 근거 선별·원출처 중복·계산·결론 상태·개인 제약 |
| `investment_research/report.py` | 정형 한국어 Markdown·내부 근거 링크 |
| `investment_research/__main__.py` | CLI·파일 보존·실행 기록 |
| `examples/cross_asset_case/` | 합성 입력·설명·생성 보고서·실행 기록 |
| `tests/test_research.py` | 오프라인 연구·입력 오류·CLI 회귀 검증 |
| `README.md`, `AGENTS.md`, `docs/*.md` | 현재 실행과 설계 전체의 범위를 구분한 안내 |

`ResearchCase`가 한 자료 묶음을 담는다. 모든 필드는 명시하며 nullable 필드도 생략하지 않는다. 미지원 필드, 중복 JSON 키와 ID, NaN/Infinity, 실제 자료 표시는 거부한다. 현재 정확히 현금성·국채·주식 노출 하나씩과 KRW 기준 질문만 지원한다.

| 자료형 | 보존하는 내용 |
| --- | --- |
| `ResearchBrief` | 질문·기준 시점·기간·통화·시장 근거 ID·제외 범위·비교 한계 |
| `ProfileSnapshot` / `ProfileField` | 사용자 정보 기준 시점·known/unknown·명시 값 |
| `SourceRecord` | 출처 ID·유형·이름·합성 위치·공개/이용 가능/획득 날짜·원출처·한계 |
| `EvidenceRecord` | 근거 ID·원문 위치·문장·관측/분석 날짜·자산 범위·연구 관점·사실/해석 상태·한계·선택적 수치 정의 |
| `ResearchClaim` / `Review` | 주장·지지/반대 근거·연결된 서사·검증 상태·검토자/날짜/이유·확인 한계·추가 질문 |
| `Alternative` / `OpportunityCost` | 노출·수익 정의·유동성·지지/반대·미확인·재검토 조건·포기하는 대안과 검토된 설명 |
| `CalculationSpec` / `MetricResult` | 방법·입력 ID·값·단위·자산 범위·계산 한계 |

이 합성 경로에서 전체 설계의 `MarketContext`, `ResearchPlan`, `ComparisonFrame`은 위 질문과 대안 필드로 작게 표현한다. 별도의 `ask`는 이후 추가한 규칙 기반 질문 해석과 검토된 자료의 실제 orchestration 경로다. `--plan-only`는 기존 계획만 출력한다. 전체 자산 전략·상품 선택·데이터베이스는 도입하지 않았다. 정량 계산은 출처 유형으로 위장하지 않고 입력 근거와 방법을 가진 별도 결과다.

## 주장과 근거를 채택하는 경계

사실 상태는 `supported_within_scope`, `partially_supported`, `contradicted_within_scope`, `disputed`, `unverified`, `not_verifiable`이다. 해석은 `reviewed`, `pending`, `rejected`와 검토 기록으로 따로 관리한다. 출처 위계는 상위 원자료를 확인할 우선순위이며 점수가 아니다.

확인·일부 확인 주장에는 적격 지지 근거, 반박 주장에는 적격 반대 근거, 상충 주장에는 양쪽이 필요하다. 이 상태를 확정한 주장에는 검토 기록이 필요하다. 검토 날짜는 참조한 근거의 분석·검토 날짜보다 앞설 수 없다. 공개·이용 가능·관측 날짜는 연구 기준 시점 이후일 수 없다. 이후의 획득·분석·검토는 공개된 자료를 사후 검토하는 경우에 허용하되 정보 기준 시점과 구분한다.

투자상의 지지/반대는 `supported_within_scope + reviewed + 비커뮤니티 사실`에 한해 채택한다. 확인된 사실의 해석이 대기 중인 경우도 허용하지만 채택을 보류한다. 일부 확인·반박·상충·미확인 근거는 원문을 보존해 검토 대상으로 표시한다. 기회비용·재검토 설명은 검토 완료, 참조 존재, 모든 참조 적격이라는 조건을 만족해야 채택한다. 한 참조라도 부적격이면 초안·이유·검토 기록을 보존한다.

**이 검사는 자동 사실 확인이 아니다.** fixture 작성자의 검토 상태와 논리가 사실에 맞는지, 연결된 구절이 실제로 존재하는지 코드는 증명하지 않는다. 임의의 prose를 금융적으로 이해하고 숫자를 검산하는 기능도 없다. 수치 필드와 정형 계산은 추적 가능하게 출력하며 원문·조건부 해석 문장은 입력 검토 기록으로 표시한다.

## 커뮤니티와 상충 근거

커뮤니티는 `observed_narrative`로만 기록한다. “그 발언을 관측했다”의 상태와 “발언 내용이 맞다”라는 연결된 주장의 상태는 다르다. 좋아요·반복 횟수·출처 등급을 신뢰도나 미래 확률로 바꾸지 않는다.

예제는 “금리가 곧 크게 떨어져 장기채는 거의 확실한 기회”라는 서사를 합성 정책금리·장기금리·물가·시장 기대·위험 의견과 대조한 검토 기록을 포함한다. 미래의 확실한 수익 부분은 `not_verifiable`로 남긴다. 출처·지지·반대·확인 불가 부분을 함께 출력한다.

주식의 이익·유동성 개선과 밸류에이션·시장 참여 폭 약화는 함께 성립할 수 있는 투자 논리의 긴장으로 표시한다. “장기금리가 정책금리보다 낮다”라는 별도 합성 주장은 수치와 모순되는 `contradicted_within_scope` 사례다. 상반된 투자 요인과 동일 사실의 모순을 구별한다. 같은 원출처를 재인용한 뉴스는 중복을 표시하며 결론을 강화하는 표로 세지 않는다.

## 계산·기회비용·결론 강도

방법 `rate_difference_v1`은 같은 통화 기준, `percent`, `annual_rate`인 두 확인·검토된 수치의 차이를 구한다. 예제의 합성 현금 명목 연율 2.5와 물가 연율 3.0으로 **2.5 − 3.0 = −0.5 %p**를 얻는다. 서로 다른 관측 기간의 단순 격차이므로 미래 실질수익·개인 실현 수익·정확한 Fisher 실질수익 계산이 아니다. 세금·비용·환율을 계산하지 않는다. 주변 Decimal 설정을 바꾸어도 같은 결과를 내도록 연산 문맥을 고정한다.

각 대안에서 나머지 두 대안을 포기하는 기회비용을 연결한다. 입력 작성자가 검토한 가능한 이익·위험 차이를 근거 ID와 함께 설명하며 확정 수익이나 최적 선택으로 바꾸지 않는다.

| 대안의 상태 | 규칙과 의미 |
| --- | --- |
| `mixed` | 적격 지지와 반대가 함께 있음; 강한 결론 유보 |
| `limited_support` | 적격 지지만 있음; 반대 자료·미조사 범위 확인 필요 |
| `insufficient_evidence` | 적격 지지가 없음; 확인된 반대 자료는 보존 |

숫자 점수·순위·승자는 없다. 연구 전체는 적격 지지가 있으면 `conditional`, 없으면 `insufficient_evidence`이며 둘 다 정상 완료다. 이는 논리적 진실성·원출처 독립성·미래 예측력의 등급이 아니다.

## 사용자 미확인과 재현성

예제의 알려진 맥락은 한국 세법상 거주자·1998년생·KRW·자산축적기·안정적인 근로소득·장기 기간이다. 모두 테스트용 합성 자기보고다. 총자산·비상자금·부채·주택 필요자금·보유 배분·월 투자액·위험 감당 능력 7개는 명시적으로 unknown이다. 필드가 없는 경우도 unknown으로 처리한다.

unknown을 0·무부채·충분한 현금으로 바꾸지 않는다. 각 항목이 제한하는 판단을 표시하고 시장 근거와 개인 배분 결론을 분리한다. 필요한 조건이 알려져도 현재 코드에 적합성 평가·투자 비중 결정 방법은 없으므로 확정 배분을 생성하지 않는다.

입력은 키 순서를 정규화한 JSON의 SHA-256으로 식별한다. `run_id`는 입력 해시와 고정 프로그램·방법 버전에서 나온다. 실행 기록에는 실제 패키지 Python 파일 해시와 보고서 해시, 계산·주장 상태도 담는다. 런타임 날짜·난수·로컬 절대 경로를 결과에 넣지 않는다. 코드가 바뀌었는지는 실행 기록의 코드 해시로 확인하며 방법 변경 시 버전도 갱신한다.

## 검증 범위와 현재 한계

합성 경로의 기존 **35개 테스트를 변경하지 않고 모두 통과**했다. Python 3.12.14에서 `python -m unittest discover -v`로 검증하며, 추가 출처 47개와 거시 검증을 포함한 현재 전체 결과는 [공개 출처 안내](source-acquisition.md)와 [거시 안내](macro-mvrs.md)에 둔다. 합성 테스트는 정상 사례, 출처/날짜 누락, 미래 정보, 검토 날짜 역전, 주장 확인/반박, 원출처 순환/중복, 커뮤니티 승격 차단, 상충 표시, unknown, 정상 근거 부족, 단위/통화 위반, 계산 검산, 재현성, 보고서 구조/근거 링크, 외부 텍스트 이스케이프, 네트워크 미호출, CLI 오류·출력 보존·체크섬을 검증한다.

별도의 [공개 출처 MVP](source-acquisition.md)는 실제 URL 획득·구절 대조·snapshot replay를 추가했고 [거시 MVP](macro-mvrs.md)는 실제 자료의 현재 상태를 설명한다. 이후 [Opportunity Map](opportunity-map.md)은 15영역과 후속 후보를, [첫 미국 주식 Deep Dive](us-equity-deep-dive.md)는 예상 이익·실적 질·AI 현금 회수·Treasury 비교를 같은 모델에 연결했다. 일반 의미의 자동 검증·소스 대표성 평가·자동 후보 선정·전체 자산 가치평가·실제 포트폴리오 집중위험·세금·LLM·추천은 구현하지 않았다. 자료에 누락된 반대 근거도 자동으로 찾지 못한다. 다음 단일 연구는 [로드맵](roadmap.md#다음-codex-task-제안)에 두며 아직 수행하지 않았다.
