# 미국 주식 Deep Dive · 기대이익과 국채 기회비용

첫 실제 Deep Dive는 기존 Opportunity Map에서 선정한 미국 주식 질문을 조사한다. [한국어 보고서](../examples/us_equity_deep_dive/us_equity_deep_dive.md), [사례와 실행 안내](../examples/us_equity_deep_dive/README.md), [고정 초안](../examples/us_equity_deep_dive/review.json), [실행 기록](../examples/us_equity_deep_dive/run_manifest.json)에 자료와 판단 한계를 보존한다. 좋은 기업·좋은 실적·좋은 투자 가격을 구분하며 BUY/SELL·가격목표·투자 비중은 생성하지 않는다.

## 실제 조사와 확인할 수 없는 범위

S&P 500은 FactSet의 분기 예상치·revision·surprise·blended growth와 State Street의 index valuation·비중을 사용한다. Nasdaq-100의 공식 구성 설명은 확인했지만 최신 동일 정의 P/E·EPS·revision은 미확보라 판단을 유보한다. Microsoft·Alphabet·Amazon·Meta·NVIDIA의 공식 실적과 SEC 자료를 확인하고, 일부 다른 상위 증권은 지수 비중만 확인했다. 이를 해당 기업 전체의 fundamental 조사로 표현하지 않는다.

rolling forward 12개월 P/E, 차기 회계연도 FY1 weighted harmonic P/E, trailing P/E는 구분한다. historical mean과 percentile, 분기 중 EPS revision과 실제 EPS 성장, guidance 기업 수와 analyst revision 건수, 실제·blended·예상 성장도 합치지 않는다. 여러 분기의 공개 판본은 확보했으나 기업별 전체 consensus→actual→직후 revision 패널은 없다. GAAP/non-GAAP·세전/세후·비경상 이익을 확인하고 자료 없이 “clean index EPS”를 만들지 않는다.

AI 공급자의 매출·마진은 구매자 ROIC나 현재 주가의 매력을 증명하지 않는다. 구매자 자료에서도 cloud 전체와 AI 전용 매출, run rate와 실현 연 매출, 현금 PP&E와 finance-lease 원금 포함 CAPEX, 분기와 TTM FCF, 전체 depreciation과 AI 전용 비용을 구별한다. 같은 정의의 hyperscaler별 incremental AI profit·utilization·전체 투자자본은 부족하다.

Fed H.15의 nominal CMT investment-basis yield를 단기·중기·장기 대안으로 살핀다. 개별 채권 실행 YTM, 할인식 bill rate, 정책금리, ETF distribution/SEC yield로 대체하지 않는다. EY와 Treasury의 차이는 같은 관측일·USD에서만 계산하며 ERP·예상 총수익률·권고 비중으로 쓰지 않는다. KRW 환율·실제 상품·보유 기간·재투자·duration·세금은 별도 조건이다.

실제로 채택한 community는 Hacker News 공개 발언이다. Reddit·X·Bogleheads·Lobsters는 접근 정책/정책 확인 실패로 중단했고 Stocktwits는 검증 가능한 message를 확보하지 못했다. 실패도 source plan·pins·snapshot에 남긴다. 목적 표집은 시장 consensus·인기·미래 확률을 대표하지 않으며, 극단적 주장의 확인 불가와 반증을 구분한다.

## 기존 시스템과 연결

`deep-dive replay`는 새로운 네트워크 수집기가 아니다. 기존 `sources acquire`로 확보한 SourceSpec/Snapshot/pins와 `replay_opportunity`의 정확한 cutoff·source/macro 검증을 사용한다. 같은 ResearchCase·EvidenceRecord·MetricResult·ResearchClaim 모델에 연결한다. 내부의 작은 OpportunityReview adapter는 source/macro 통합을 재사용하기 위한 것으로 별도의 추천 지도나 자동 후보 선정을 만들지 않는다.

**부모 Opportunity Map과 후보 선정은 필수가 아니다.** 독립 연구는 `review.json`에 자체 `profile`·`horizon`을 넣고 `parent`를 생략하거나 `null`로 둔다. profile은 `{항목: {status: known/self_reported/unknown, value: 값/null}}`이며 UNKNOWN은 null을 유지한다. horizon도 미확인이면 이를 명시한다. 소득·나이·투자의향에서 손실 감당 능력이나 비중을 추정하지 않는다.

이전 맥락을 연결한 경우만 부모의 review ID·review SHA-256·통합 입력 SHA-256과 cutoff를 검사한다. 후보 선정 여부와 무관하게 직접 조사할 수 있다. 부모를 연결하려면 CLI의 `--parent-*` 일곱 옵션을 모두 지정하고, review의 parent hash를 맞춘다. 일부 옵션만 지정하거나 고정 링크를 조용히 버리는 것은 차단한다. 기존 review-v1 사례는 부모의 자기보고·UNKNOWN·horizon을 상속한다. 현재 review에 자체 profile/horizon을 명시하면 그것이 우선한다. 연결된 맥락의 이후 cutoff만 허용하며 새 연구가 과거 공개 시점을 소급 입증한다고 주장하지 않는다.

예를 들어 완전한 미국 주식 review에 아래 맥락을 추가하면 부모 없이 replay할 수 있다. 나머지 fact·section·source/macro 계약은 그대로 필요하다.

```json
{
  "parent": null,
  "profile": {
    "base_currency": {"status": "self_reported", "value": "KRW"},
    "holdings": {"status": "unknown", "value": null},
    "debt": {"status": "unknown", "value": null}
  },
  "horizon": "UNKNOWN · 투자기간은 미확인이다."
}
```

```bash
python -m investment_research deep-dive replay reports/my_us_equity_review.json --plan examples/us_equity_deep_dive --store examples/us_equity_deep_dive/snapshots --pins examples/us_equity_deep_dive/pins.json --macro-plan examples/macro_case --macro-store examples/macro_case/snapshots --macro-pins examples/macro_case/pins.json --output reports/my_us_equity_report.md
```

이 예시는 입력을 준비한 경우의 고정 replay이며 신규 시장조사를 자동 수행하지 않는다. 미국 주식 scope·P/E·Treasury·source/macro 입력은 **이 특정 분석 방법**의 조건이다. crypto·부동산·배당 전략 등의 Deep Dive에 이 방법을 강제하지 않는다. 네 독립 진입점과 현재 계획/실행 차이는 [연구 모드](research-modes.md)에 정리했다.

## 원문 숫자 계약

각 fact는 원문 Evidence ID, 실제 보존한 contiguous quote context, 유일한 숫자 token, Decimal 문자열, 원문의 6필드 definition, 더 좁은 단위·통화·entity·window·관측일·basis를 기록한다. 원문 definition/currency 불일치, 단위의 묵시적 million→billion 변환, 없는/중복 token, 비유한 값, ID 충돌과 미등록 참조를 거부한다. 금융 표의 숫자는 이 fact나 계산 ID에서만 삽입한다. 일반 prose에 금융 숫자를 직접 입력하는 것도 거부한다. 지수명·공시명·FY1은 숫자 값이 아닌 제한된 명칭이다.

괄호로 표현한 현금 지출은 음수를 보존한다. 참고 평균을 괄호에 적은 P/E까지 음수 회계 금액으로 해석하지 않는다. `above`·`below`·`approximate` qualifier는 점추정으로 바꾸지 않으며 정확한 계산 입력으로 사용할 수 없다. Microsoft run rate의 “surpassed”는 해당 숫자를 초과한다는 발표로 보존한다.

이 검사는 **원문 전사와 구조**를 확인한다. 선택한 표의 열·기간·기업·의미가 맞는지는 명시한 작성·대조 기록이며 자동 검증되지 않는다. 원문 locator도 DOM/표 위치의 자동 증명은 아니다. 이를 감추기 위해 fact를 경제적 진실로 승격하지 않는다. 숫자 전사는 `supported_within_scope`이지만 해석은 `pending`, 경제적 주장과 scenario는 `unverified`/draft로 유지한다. 커뮤니티 숫자는 금융 fact가 될 수 없다. community evidence의 지원 상태도 발언 존재에만 한정된다.

## 이번 질문에 필요한 결정적 계산

| 방법 | 공식 | 필수 조건과 한계 |
| --- | --- | --- |
| `earnings_yield_v1` | `100 / P/E` | 양수 P/E·명시한 forward/trailing basis; 지급 현금·미래 수익률 아님 |
| `descriptive_yield_gap_v1` | `100 / P/E − Treasury yield` | 같은 관측일·USD·nominal CMT investment basis; 출력 `%p`; ERP 아님 |
| `cash_residual_v1` | `OCF + 음수 현금 PP&E` | 같은 기업·기간·관측일·단위·통화, PP&E 양수 금지; 전체 리스 CAPEX·AI ROI 아님 |

고정 Decimal precision 50·ROUND_HALF_EVEN을 사용하며 표시는 반올림한다. 원문 수치의 정밀도나 미래 경제적 확실성이 높아졌다는 뜻은 아니다. Meta의 반올림된 OCF/CAPEX로 FCF를 재생성하지 않고 공시된 million 단위 FCF를 사용한다. 회계 평가이익을 세후 EPS에서 단순 차감하거나 정의가 다른 회사의 FCF를 합산하는 계산은 구현하지 않았다.

## 시점·실패와 판단 유보

matched·fresh·비커뮤니티 source와 cutoff 이전 실제 retrieval이 필요하다. publication unknown·observation known의 발행사 페이지는 획득 후 현재 판본으로만 쓴다. 둘 다 unknown인 Nasdaq 구성 설명은 definition 맥락으로만 쓰며 현재 금융 값이 될 수 없다. 미래 관측, stale·실패·미래 retrieval이면 fact·파생 값과 관련 현재 prose를 보류한다.

질적 판단 heading도 핵심 근거와 함께 보류한다. 현재 판단의 참조에 이용 가능한 P/E와 Treasury 숫자/계산 맥락이 없거나 해석 role이 아니면 effective judgment는 `insufficient evidence`다. `mixed`는 이 연구에서 작성한 경제적 해석 초안이다. 기존 engine의 `conclusion`과 `personal_conclusion`은 검토 완료 근거가 부족한 `insufficient_evidence`로 유지한다. 두 필드는 자동 승인과 연구 초안을 구분한다.

보고서는 snapshot/구절/definition, fact와 입력 공식, 부모 및 통합 input hash, source failures와 경제 해석 상태를 연결한다. 본문의 짧은 번호 링크는 부록의 원문·숫자·계산으로 이동한다. 고정 replay는 새로운 시장 조사나 자동 판단 갱신이 아니다. 기존 입력·pins·snapshot·다른 내용의 출력은 덮어쓰지 않는다.

## 검증과 현재 한계

첫 Deep Dive 완료 당시 Python 3.12.14에서 전체 **179개 테스트가 통과**했다. 기존 159개를 유지하고 합성 오프라인 Deep Dive 경계 20개를 추가했다. 독립적으로 검산 가능한 EY/차이/현금 잔여, 단위·통화·날짜·괄호·bound, community 숫자 승격 금지, 미래/stale/실패 차단, 부모 hash와 프로필 UNKNOWN, 변조·출력 보호·인용 링크를 확인했다. 이후 독립 진입점 변경에서 부모 후보 관문을 제거하고 독립/선택적 맥락 replay 검증을 추가했다. 현재 전체 검증은 [README](../README.md)에 둔다. 실제 시장 숫자는 테스트 fixture로 쓰지 않는다.

실제 고정 보고서·manifest를 HTTP·DNS 차단 상태에서 두 번 재생해 동일성을 확인했다. 기존 합성·출처·거시·Opportunity Map 네 보고서는 바이트가 같고 기존 사례의 입력·원자료·보고서·manifest도 보존했다. 코드 추가에 따라 새 실행의 code hash가 기존 manifest와 다른 것은 정상이다. 이러한 검증은 경제적 추론의 진실이나 미래 투자 성과를 자동 입증하지 않는다.

정형 표 전체의 의미 자동 검증, 유료 consensus/vintage 자료, 회사별 AI ROI·lease 포함 자본 비교, 최신 Nasdaq valuation과 equal-weight 기여, 실제 포트폴리오·상품·계좌 조건은 부족하다. 새로운 범용 수집·대규모 agent·점수 엔진을 선행 구현하지 않는다. [로드맵](roadmap.md#다음-codex-task-제안)의 다음 Deep Dive 하나만 제안하며 수행하지 않았다.
