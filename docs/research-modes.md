# 독립 연구 진입점과 최소 조사 범위

시스템은 사용자의 투자 질문에 답한다. 사용자가 내부 workflow나 모드 이름을 배울 필요는 없다. **Opportunity Scan, Asset Deep Dive, Compare, Portfolio Review는 독립 진입점**이다. Scan의 실행·완료·후보 선정은 다른 모드의 선행 조건이 아니다. 사용자가 모드를 명시하면 이를 우선하며, 명시하지 않으면 질문의 대상과 판단 목적에서 해석한다.

## 모드별 계약

| 모드 | 사용할 질문 | 시작 입력과 방법 | 결과와 제한 |
| --- | --- | --- | --- |
| Opportunity Scan | 현재 투자기회, 조사할 자산군, 여러 시장의 변화·위험/보상 | 질문에 관련된 여러 자산군의 근거·변화·접근 조건을 가볍게 검토 | 더 조사할 영역·이유·반대 논리·보류 조건; 근거가 약하면 순위·추천·정해진 수의 후보를 만들지 않음 |
| Asset Deep Dive | 특정 자산·기업·ETF·sector·industry·crypto·원자재·채권·부동산 시장/물건·투자 전략 | 지정 대상과 실제 질문에 직접 진입하고 대상 고유의 방법 선택 | 기대와 실제 근거, 가격/경제성, downside, 반대 논리·재검토 조건; 질문에 실질적으로 필요한 macro·대안만 추가 |
| Compare | 두 개 이상의 명시한 대안 사이의 선택 | 지정 대안과 비교할 판단·기간·통화·유동성 제약 | 경제적 수익 원천·downside·기회비용·해당되는 valuation·세금/계좌·사용자 적절성을 축별 비교; 다른 자산에 같은 지표를 강제하지 않음 |
| Portfolio Review | 실제 보유·배분·집중위험·현금 수준·재조정·신규 자본 배분 | 기준일의 실제 포트폴리오와 재무 제약부터 확인 | 자산 자체의 매력, 기존 과다 노출, 추가 보유의 전체 포트폴리오 효과를 구분; 중요한 정보가 없으면 안전·적절성·재조정 결론 제한 |

Compare는 전체 Deep Dive 여러 편을 먼저 완성해야 하는 관문이 아니다. 비교 질문에 필요한 각 대안의 근거만 조사할 수 있다. Deep Dive에서 Treasury 기회비용을 살피는 것도 전체 Scan을 수행하거나 별도 Compare 모드를 반드시 추가한다는 뜻이 아니다. 모드는 답의 목적이며 macro·fundamental·quantitative·community는 목적에 맞춰 선택하는 근거와 방법이다.

Portfolio Review에서는 보유자산의 종류·수량/가치·통화·상품·기준일·누락 범위를 확인하고, 관련 현금·부채·소득/지출·추가 투자액·비상자금·큰 자금수요·주택 계획·기간·capacity/tolerance를 연결한다. 총액이 없으면 금액 기준 집중도를, 다른 자산이 빠지면 전체 분산을 확정하지 않는다. 보유 정보가 없으면 필요한 입력과 가능한 제한된 시장 해석까지만 제공한다. 좋은 자산이어도 이미 과다 보유했다면 추가 보유의 적절성이 다를 수 있다.

## 자연어 질문의 해석 예시

| 사용자 질문 | 필요한 모드·범위 |
| --- | --- |
| 오늘 투자기회 찾아줘. | Opportunity Scan |
| 지금 전체 투자판에서 내가 볼 만한 기회 찾아줘. | Opportunity Scan; 특정 자산을 되묻지 않고 broad cross-asset 조사 |
| BTC 지금 어때? / Bitcoin 지금 어때? | Crypto Deep Dive |
| 천연가스 투자 괜찮아? | Energy / Natural Gas Deep Dive |
| 동탄 아파트 지금 사도 될까? | Korean Real Estate Deep Dive; 지역/물건·실거주·대출에 필요한 맥락 확인 |
| 배당투자 지금 할 만해? / 지금 배당투자를 늘리는 게 맞아? | Dividend Strategy Deep Dive; 개인 증액 판단에는 현재 노출·자금 제약 필요 |
| 삼성전자랑 SK하이닉스 비교해줘. | Compare |
| 한국 3년 국채랑 S&P500 중 지금 신규자금 어디가 더 합리적이야? | Compare; 한국·3년·신규자금 목적 보존, 해당 국채 자료 부족을 명시 |
| 서울/수도권 아파트 지금 투자 관점에서 어때? | Real Estate Deep Dive; 서울·수도권·투자 관점 보존, 전국 자료로 대체하지 않음 |
| S&P 500 vs Treasury bonds / SCHD vs Korean dividend stocks | Compare |
| Bitcoin vs Ethereum / Korean real estate vs US equities | Compare |
| 내 포트폴리오 괜찮아? | Portfolio Review |
| 동탄 집이랑 S&P500 중 뭐가 나아? | Compare; 실거주 편익·금융비용과 금융자산의 경제성을 다른 축으로 비교 |
| 시장 전체를 훑고 천연가스와 한국 반도체는 깊게 분석해줘. | Opportunity Scan + 지정한 두 Deep Dive |
| 내 포트폴리오를 보고 국채와 S&P 500 중 어디에 신규 자금을 넣을지 비교해줘. | Portfolio Review + Compare |
| 요즘 투자할 곳 찾아보고 가장 유망한 두 개를 깊게 분석해줘. | Opportunity Scan + 근거가 충분한 후보의 Deep Dive; 후보가 부족하면 선정 유보 |

지정한 대상의 Deep Dive는 함께 요청된 Scan과도 독립적으로 시작할 수 있다. 마지막 예시는 사용자가 Scan 결과로 조사 대상을 정해 달라고 했으므로 그 **개별 작업만** 후보 선택에 의존한다. 이 조건부 의존을 모든 Deep Dive의 전역 순서로 확대하지 않는다. Portfolio Review + Compare는 실제 보유 제약을 비교 판단에 전달하며, 자료가 부족해도 가능한 대안 자체의 비교와 개인화 결론을 구분한다.

## 범위와 해석 규칙

1. 명시한 모드·대상·제외 범위가 자동 해석보다 우선한다. 필요한 입력이 모자라면 질문하거나 영향을 받는 판단을 유보한다. 사용자의 모드를 조용히 다른 모드로 바꾸지 않는다.
2. 질문·자산/상품·전략·의사결정·근거·관련 사용자 상황으로 **잘 답할 수 있는 가장 작은 범위**를 정한다. 익숙한 지표가 있다는 이유로 대상을 바꾸거나 전 시장을 조사하지 않는다.
3. 여러 모드가 실제로 필요한 경우만 조합한다. 대상이 분명하면 Scan 후보 목록에 없거나 이전 연구가 없어도 직접 시작한다.
4. macro·사업·정량·community의 채택은 질문에 대한 전달 경로로 설명한다. 공급자 매출, 고객 ROI, valuation, 사용자 적절성은 별도 주장이다.
5. 자산의 방법이 미지원이면 필요한 고유 입력·방법과 가능한 조사 범위를 공개한다. 주식의 P/E나 Treasury 비교를 crypto·부동산·모든 전략에 강제하지 않는다.
6. 모드 선택은 사실 검증이나 경제적 결론의 승인이 아니다. 모든 실행에서 기존 [research integrity](research-integrity.md), source hierarchy·시점·원문·계산·반대 근거·UNKNOWN 규칙을 유지한다.

## 현재 구현과 실행 경계

[routing.py](../investment_research/routing.py)의 작은 규칙 기반 `plan_research`가 네 모드·명시적 override·필요한 조합·대상별 자료 요구를 정리한다. 흔한 한국어/영어 표현과 대상 별칭을 지원한다. 모든 자연어·임의의 자산 이름을 완전히 이해하는 일반 언어 모델은 아니다. 불명확한 대상·비교 조건·방법은 `needs_clarification`으로 남기고 전체 Scan으로 대체하지 않는다. `ask --plan-only`는 `research-plan-v1`, `execution_status: not_started` 계획만 출력한다. 기본 `ask`는 [Research Orchestrator](research-orchestrator.md)로 검토된 자료의 실제 수집·기존 검증·계산·한국어 보고서까지 실행한다. 완료된 실행과 강한 연구 결론은 구분한다.

```bash
python -m investment_research ask 'BTC 지금 어때?'
python -m investment_research ask '동탄 집이랑 S&P500 중 뭐가 나아?'
python -m investment_research ask '내 포트폴리오 괜찮아?' --portfolio my_portfolio.json
python -m investment_research ask 'BTC 지금 어때?' --plan-only --output reports/btc_plan.json
python -m investment_research ask --replay reports/btc_run
python -m investment_research ask 'BTC vs ETH' --mode compare
python -m investment_research ask '내 포트폴리오에서 BTC vs ETH' --mode portfolio_review --mode compare
```

모드는 선택적으로 `Asset Deep Dive: BTC 지금 어때?` 또는 `Portfolio Review + Compare: …` 접두부로도 명시할 수 있다. 일반 사용자는 접두부·옵션을 쓸 필요가 없다. 실행은 대상·모드별 작업, 필요한 입력, 실제 의존, 미확인 질문과 한계를 보존한다. [질문 조건 보존](query-understanding.md)의 routing v4는 국가·지역·만기·전략·판단 목적·시점·사용자 제약을 구조화하고 미지원 조건을 명시한다. 수치는 기존 파싱·quote/metric·자기보고 값에서만 나오고 임의 수익률·점수·추천·source URL·LLM 판단은 생성하지 않는다. `ask --replay`는 원래 입력·기준 시점·자료·보고서를 인터넷 없이 재현한다.

**금융 분석 실행**은 기존 source/macro와 근거 모델을 사용한다. 현재 Opportunity Map은 Scan의 실제 고정 사례이고, `deep-dive replay`는 미국 주식의 기대이익·AI 경제성·Treasury 대안이라는 **특정 분석 방법**이다. 부모 Opportunity Map과 후보 검사는 필수가 아니며, 직접 입력한 `profile`·`horizon`으로 독립 replay가 가능하다. 기존 부모 연결 사례는 그대로 재현한다. 입력 계약은 [미국 주식 Deep Dive 안내](us-equity-deep-dive.md)에 있다.

Compare MVP는 지정한 대안의 고유 자료와 공통 의사결정 축을 연결한다. Portfolio Review MVP는 명시적 KRW 보유 금액·전체성·현금으로 계산 가능한 구성만 검토한다. Combined Mode는 출처를 한 번 수집해 지정한 작업을 조합한다. [Source Discovery](source-discovery.md)는 질문에서 필요한 BTC 범주만 선택해 새 source/관측/판본을 발견하는 제한된 앞단이다. 모드를 추가하거나 Scan을 강제하지 않는다. [넓은 Scan](opportunity-scan.md)은 근거 조건을 충족한 조사 후보만 선정한다. 미래 수익 순위·전체 자산의 완전한 방법·look-through·개인 최적 배분·arbitrary web search는 미지원이다. 상세 입력·artifact·실제 예제와 제한은 [orchestration 안내](research-orchestrator.md)를 따른다.

## 이번 변경의 이유

이전 아키텍처의 `사용자 맥락 → 전반적 후보 조사 → Deep Dive` 흐름과 코드의 필수 부모·후보 검사는 직접 자산 질문을 가로막았다. 이를 독립 모드 선택과 필요한 자료 검증으로 바꿨다. 부모의 hash·시점 검증은 **연결한 경우의 provenance 검사**로 유지하고, 부모를 생략했다고 원문·정의·시점 검증을 완화하지 않는다. 기존 고정 보고서·snapshot·manifest는 역사적 실행으로 보존한다. 개발 단계의 순서는 사용자의 연구 순서가 아니다.

## 검증 기록

독립 진입 계약 완료 당시 205개, 이번 실제 orchestration 연결 후 전체 **236개 테스트가 통과**했다. 기존 모드·부모 없는 replay 검증을 유지하고 31개 실행·artifact·보유·근거 추적·미지원·동일 재현 검증을 추가했다. 계획 CLI 검증은 `--plan-only`로 명시했다. 실제 시장 숫자를 새 unit test 근거로 쓰지 않았다.

HTTP/DNS를 차단하고 기존 합성·source·macro·Opportunity Map·미국 주식 Deep Dive 다섯 보고서와 입력 해시가 동일함을 확인했다. 기존 예제 파일 251개를 보존했고 로컬 문서 링크도 확인했다. 새 실행의 code hash는 코드 변경을 반영하며 과거 manifest를 덮어쓰지 않는다. 이는 질문 해석·재현·자료 경계의 검증이며 경제적 결론의 진실이나 미구현 금융 분석기의 완성을 뜻하지 않는다.

이후 discovery 37개와 query understanding 23개를 추가해 현재 전체 **296개**가 통과한다. 세 정확한 실패 문장과 BTC·천연가스·한국 반도체 비교의 실제 회귀 결과는 [별도 기록](../reports/query_understanding_regression_20261005T080806Z/regression_report.md)에 보존한다. 이전 v2/v3 실행은 재해석하지 않고 그대로 replay한다.
