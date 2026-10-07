# 질문의 의도와 명시 조건 보존

이 문서의 실패/수정 표와 296개 검증은 query-understanding 변경 당시의 기록이다. 이후 [한국 원자료 coverage](korean-official-coverage.md)가 **동일한 질문 해석 코드** 아래 ECOS 국채·기업 실적·서울/경기/인천 아파트 자료를 연결했다. 현재 live catalog의 지원 범위는 해당 문서를 따른다. 자료 연결 없는 fixture는 당시 미지원 조건을 계속 검증하며, 이전 보고서는 수정하지 않았다.

`ask`의 `research_routing_v4`는 모드 이름뿐 아니라 **사용자가 지정한 대상·국가·지역·만기·판단 목적**을 실행과 보고서까지 보존한다. 자료가 없는 조건을 더 넓은 조건이나 다른 국가의 자산으로 바꾸지 않는다. 금융 데이터 연결을 늘리기 전에 실전 acceptance test에서 발견한 세 해석 오류를 수정한 변경이다.

## 실패와 수정

| 질문 | 이전 실행의 문제 | 수정된 실행 |
| --- | --- | --- |
| 한국 3년 국채랑 S&P500 중 지금 신규자금 어디가 더 합리적이야? | 두 Deep Dive로 분리하고 한국·3년을 잃어 미국 단기 국채에 연결 | Compare. 한국 3년 국채와 S&P 500, 신규자금 목적을 보존. 한국 3년 자료는 미지원으로 표시하고 미국 단기 국채를 수집하지 않음 |
| 지금 전체 투자판에서 내가 볼 만한 기회 찾아줘. | 대상 없는 Deep Dive로 분류해 특정 자산 확인 요구 | Opportunity Scan. 대상 확인 없이 기존 11영역의 cross-asset pipeline 실행 |
| 서울/수도권 아파트 지금 투자 관점에서 어때? | 지역을 버리고 전국 부동산 게시물과 무관한 동탄 설명 사용 | Real Estate Deep Dive. 서울·수도권, 투자 관점을 보존. 지역 데이터 부족을 명시하며 전국 게시물을 지역 근거로 대체하지 않음 |

자료 부족은 질문을 이해하지 못했다는 뜻이 아니다. 한국 3년 국채의 수익률 연결이 없더라도 비교 의도는 Compare로 유지한다. S&P 500의 미국 금리는 주식의 배경 자료일 수 있지만 **한국 3년 국채 수익률의 대체값은 아니다**. 지역 부동산 방법은 분석해야 할 항목을 보여 줄 수 있지만, 원자료 없이 해당 지역의 현재 경제성을 검증했다고 주장하지 않는다.

## 구조화하는 내용

[query_understanding.py](../investment_research/query_understanding.py)는 외부 호출 없이 명시 구절을 추출한다. [routing.py](../investment_research/routing.py)는 기존 네 독립 모드와 작업을 선택한다.

| 필드 | 의미 |
| --- | --- |
| `original_question`, `intent`, `requested_comparison` | 원래 질문, 선택 모드들, 비교 요청 여부 |
| `scope`, `assets_or_alternatives` | 전체 시장 또는 지정 대상, 원래 순서의 자산/대안 |
| 대상의 `label`, `method_family`, `asset_class`, `raw_text` | 보존한 대상 이름·연구 방법·자산군·원래 구절 |
| 대상의 `country`, `regions` | 대상에 붙은 국가와 지역. 투자자의 거주 국가를 추정하는 필드가 아님 |
| 대상의 `maturity`, `duration` | 만기 값·단위와 단기/중기/장기 표현. 두 의미를 합치지 않음 |
| 대상의 `strategies`, 질문의 `strategies` | 명시한 배당·성장·가치 등 전략 |
| `investment_purpose` | 신규자금, 투자 경제성, 실거주, 주택 구입, 은퇴, 비상자금 등 명시 목적 |
| `time_context` | 지금·최근·달력 표현·지정 날짜 |
| `user_constraints` | 보유기간·미래 자금수요·예산·부채·위험·환율·계좌·수치 duration·세법상 거주 등 명시 구절 |
| `data_limits` | 해석했지만 현재 실행에서 지원할 수 없는 지정 날짜·수치 duration 조건 |
| `schema_version`, `method_version` | `query-understanding-v1`, `explicit_query_constraints_v1` |

목적·시점·사용자 제약·질문 전략의 각 항목은 `raw_text`와 원래 질문의 `span: [start, end]`를 가진다. 대상도 원래 구절을 보존한다. 만기·보유기간·미래 자금수요의 숫자는 문자열 값과 years/months 단위로 기록한다. 예산은 사용자가 적은 값과 단위를 남기며 질문의 금액으로 전체 포트폴리오나 투자 비중을 만들어내지 않는다.

예를 들어 첫 질문의 국채는 다음 의미로 저장된다. 전체 출력은 `ask --plan-only`로 확인할 수 있다.

```json
{
  "label": "한국 3년 국채",
  "method_family": "bond",
  "asset_class": "bond",
  "country": "KR",
  "regions": [],
  "maturity": {"value": "3", "unit": "years", "descriptor": null, "raw_text": "3년"},
  "duration": null,
  "raw_text": "한국 3년 국채"
}
```

`한국 3년 국채, 2년 뒤 집 살 돈, 듀레이션 1년`의 세 숫자는 각각 채권 만기, 예정 자금수요, 금리 민감도다. 같은 숫자 형식이라는 이유로 서로 바꾸지 않는다. 단기/장기는 기간 특성 표현이며 특정 계약의 수치 duration을 증명하지 않는다.

## 실행에서 조건을 지키는 경계

1. `중 … 어디/뭐/어느/더 합리적` 같은 선택 표현과 복수 대안을 비교로 해석한다. `전체 투자판 … 기회`는 broad Scan으로 해석한다. 명시 모드 override와 기존 Scan 부정·최소 범위 규칙은 유지한다.
2. 국가·만기·지역이 다른 대상은 별도 대안으로 유지한다. 한 비교의 한국 조건을 다른 미국 대안에 복사하지 않는다.
3. [research_catalog.py](../investment_research/research_catalog.py)의 방법 선택에서 명시한 한국 국채, 정확한 숫자 만기, 미지원 중기 채권 등을 미국 단기/장기 방법으로 연결하지 않는다. 외국 지역 부동산을 한국 부동산으로 연결하지 않는다.
4. 지역 부동산은 지역 이름을 보존한다. 연결이 없는 지역/단지는 방법 설명과 공백만 표시하며 전국 자료와 무관한 환율 series를 수집하지 않는다. 현재 설정된 서울·경기·인천의 공식 통계도 개별 단지의 가격으로 일반화하지 않는다.
5. 각 작업의 `condition_coverage`에 대상·방법·`partial/unavailable`·이유를 기록한다. 보고서에는 **“현재 이 조건을 지원할 데이터가 부족하다”**를 표시하고 비교 우열·신규자금 배분을 유보한다.
6. 사용자의 명시 보유기간은 알려진 질문 맥락으로 유지한다. 보유액·현금·부채·전체성의 계산은 계속 별도 자기보고 portfolio 입력만 사용한다.

질문 해석 변경 자체는 금융 data connector를 추가하지 않았다. 후속 한국 자료 연결도 기존 수집·원자료·claim·계산·counterargument infrastructure를 사용하며 추천·portfolio optimization을 추가하지 않았다.

## 시점과 재현

“지금/오늘”은 현재 자료를 사용하는 요청이다. 명시한 절대 날짜는 보존하되, 현재 ask에는 임의 날짜의 당시 이용 가능 판본을 자동 선택하는 기능이 없다. 이 경우 현재 자료 획득과 BTC discovery를 실행하지 않고 조건 부족을 보고한다. 과거 질문을 현재 가격으로 대체하지 않는다. 연도·상대적 달력 표현은 맥락으로 남기며 정확한 과거 cutoff로 변환하지 않는다.

`input.json`의 `plan.understanding`, `run_manifest.json`의 `query_understanding`과 `resolved_intent`, 작업의 `condition_coverage`로 질문→지원 범위→원자료→보고서를 추적한다. 방법 버전은 routing v4로 고정한다. routing v2/v3의 이전 실행은 질문을 다시 해석하지 않고 저장한 범위·구판 보고서 그대로 재현한다. 이전 오류가 있던 기록도 역사적 실행으로 남기고 수정 결과는 새 디렉터리에 보존한다.

## 검증

기존 273개와 [신규 23개 테스트](../tests/test_query_understanding.py), 전체 **296개가 인터넷 없이 통과**했다. 세 정확한 실패 문장, 여섯 질문의 모드, 비교 표현 변형, 국가/만기별 대안, 지역 구분, 보유기간·자금수요·duration의 분리, 원문 위치, 미지원 조건, 최소 수집, portfolio 입력 추정 금지, 원래 질문과 보고서 재현을 확인한다.

```bash
python -m unittest discover -v
python -m investment_research ask '한국 3년 국채랑 S&P500 중 지금 신규자금 어디가 더 합리적이야?'
python -m investment_research ask '지금 전체 투자판에서 내가 볼 만한 기회 찾아줘.'
python -m investment_research ask '서울/수도권 아파트 지금 투자 관점에서 어때?'
```

BTC·천연가스·삼성전자 vs SK하이닉스를 포함한 여섯 질문은 모드 옵션과 portfolio 주입 없이 실제로 다시 실행했다. [전후 회귀 검증 기록](../reports/query_understanding_regression_20261005T080806Z/regression_report.md)에 질문별 결과와 데이터 한계, 보고서·manifest·offline replay를 정리한다. 해석·조건 보존 통과와 시장 판단의 충분성은 별개다.

## 현재 한계

규칙 기반 parser이며 임의의 국가·지역·상품 이름과 모든 복합문장을 완전히 해석하지 않는다. 지원 국가명·지역 패턴·자산 별칭과 표현의 범위가 정해져 있다. 새 표현은 원래 질문과 구조화 결과를 비교하는 acceptance fixture로 확장한다. 명시한 제약을 보존하는 일이 세금·대출·duration·자금수요의 실제 적절성을 계산했다는 뜻은 아니다. 한국 3년 국채·지역 부동산·SK하이닉스 원자료 부족은 이번 변경 후에도 남아 있다.
