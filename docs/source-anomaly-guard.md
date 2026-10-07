# Source Anomaly Guard

`source_pipeline.validate_evidence`는 기존 획득·원문 대조·freshness 적용 뒤, 현재 계산·claim·coverage 앞에서 실행한다. 새 `ask`는 `source_anomaly_guard_v1`을 입력과 manifest에 고정한다. 기존 snapshot과 과거 실행은 수정하지 않는다. marker가 없는 과거 replay는 당시 방법과 보고서를 그대로 재현한다.

## 무엇을 격리하는가

| 검사 | 기준 | 처리 |
| --- | --- | --- |
| 동일 제공자 충돌 | 같은 측정·관측기간·scope·adjustment에서 endpoint/표/rendering의 값 또는 단위가 다름 | `conflicting` 또는 `unit_mismatch` |
| 극단적인 값 | 동일 제공자·정의의 서로 다른 인접 날짜가 최소 세 개 있고, 주변 절대값 중앙값의 20배 이상 | `anomalous`: 추가 검증 요청이며 오류 판정이 아님 |
| 단위·경제적 의미 | 등록 측정의 단위/통화/주기 및 확인된 adjustment 계약, 전사 값의 metadata 일치 | USD/million, percent/fraction, tonnes/ounces, Bcf/MMcf, 월간/일간, 총액/주당, AUM/flow, 시장가격/NAV를 자동 변환하지 않음 |
| 결측·미완성 | 숫자 selector가 실패하거나 최신 행이 미완성 | `incomplete`; null, 빈칸, `-`, 미보고, 실제 zero를 대체하지 않음 |

날짜가 이미 정의에 있는 관측은 source의 최신 발표일로 덮어쓰지 않는다. `daily` 같은 빈도만 있는 기존 거시 정의에는 각 관측일도 비교 키에 포함한다. 다른 만기·선물 인도월·지역·분기·FY1/forward/trailing·재고/수출 정의는 서로 충돌이나 동일 시계열로 취급하지 않는다. 인접 표본이 없으면 통계적 격리 검사를 할 수 없다. 등록되지 않은 경제적 의미를 자동 추론하지도 않는다.

## 계산·claim·coverage에서의 차단

격리 근거는 검증 상태를 `unverified`, 해석을 `pending`으로 둔다. 이상치·충돌 수치는 현재 사용 값에서 제거하지만 원문 인용·raw value·definition·snapshot은 보존한다. 미완성 행에 실제 표시된 subtotal은 원문 전사로 남기되 확정 flow로 사용하지 않는다. 일반 계산과 보고서의 현재 수치 삽입, 기존 findings와 주장 support/counter/context, 최소 coverage는 이 검증 상태를 검사한다. 이미 만들어진 설명용 계산도 격리 입력에 의존하면 제거하며 report 검증기가 다시 차단한다.

선택한 ETF 관측창의 한 행이라도 격리되면 그 창을 현재 flow 시계열과 coverage slot에 사용하지 않는다. 오래된 정상 행으로 최신 값을 대신하거나 네 날짜로 오 거래일 합계를 만들지 않는다. 가격·거래량 등 독립적으로 확인된 슬롯은 그대로 평가하며 자료 부족과 매력 부족을 구분한다.

## 언제 해제할 수 있는가

독립 발행의 primary source에서 같은 날짜·단위·통화·scope·adjustment 값을 확인한 경우에만 `cross_checked`를 기록한다. 같은 제공자의 다른 rendering, 원출처를 공유하는 재게시, 커뮤니티, 오래되거나 미래인 자료, unmatched 구절은 해제 근거가 아니다. 단위 불일치와 결측을 자동 환산/보간하여 해제하지 않는다. 이 확인도 자산 매력이나 경제적 가설 전체의 검증을 뜻하지 않는다.

## 기록과 재현

`evidence_validation.json`은 규칙·정의·원문·raw value·격리 이유·독립 확인 ID를 보존한다. report/manifest는 판단 제한과 해당 근거를 연결한다. replay는 저장한 입력·source pins·quote를 사용해 격리 결과까지 다시 계산하고 기록과 비교한다. 네트워크나 PDF decoder가 필요 없다.

직전 accepted Scan의 ETH 이상치 재검사는 [역사 자료 재판정](../reports/commodity_deep_validation_20261006/historical_eth_revalidation.json)에 별도로 남긴다. 이는 당시 시장이 악화된 관측이 아니라 자료 검증 방법을 강화한 결과다. 전체 실제 결과와 보존 검증은 [acceptance 기록](../reports/commodity_deep_validation_20261006/validation_report.md)을 따른다.
