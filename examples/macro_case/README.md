# 실제 거시 자료의 현재 상태 예제

이 사례는 합성 자료가 아니다. BLS와 Federal Reserve Board의 실제 공개 자료 4개를 명시적으로 확보하고, 4개 원시계열로 한국어 [Macro Regime Snapshot](macro_snapshot.md)을 만든다. 정보 기준 시각은 **2026-10-04 02:13:16.107675 KST**이며 고정 [pins](pins.json)에 UTC 시각을 기록했다. 장중 실시간 화면이나 이후 발표를 반영한 보고서가 아니다.

## 선택한 최소 시계열

| 시계열 | 원자료 정의 | 이 사례에서 확인할 질문 |
| --- | --- | --- |
| `US_CPI_U_HEADLINE_NSA` | 미국 CPI-U 전체 품목, 도시 평균, 1982–84=100, 월별 비계절조정 원지수 | 정확히 12개월 전과 비교한 물가 상승률과 직전 월 대비 상승률 변화 |
| `US_TREASURY_NOMINAL_2Y` | 2년 constant-maturity 명목 시장금리, 연율 % | 단기 국채 시장금리의 수준과 직전 관측 변화 |
| `US_TREASURY_NOMINAL_10Y` | 10년 constant-maturity 명목 시장금리, 연율 % | 장기 시장금리와 같은 날의 10년−2년 금리 차이 |
| `USD_KRW_NOON_REFERENCE` | 뉴욕 정오 기준 매입환율, USD 1당 KRW | 한국 투자자의 원화 환산 환경을 미국 자산 자체 환경과 구분 |

물가·서로 다른 만기의 국채·KRW 환율이면 정의·주기·공개 지연·결측·변환·통화 방향을 작은 경로에서 검증할 수 있다. 정책금리·고용·성장·한국 CPI·한국 기준금리는 이번 집합에 포함하지 않았고 관련 판단은 보류한다. 미국 국채 시장금리는 정책금리·실질금리·실현 채권수익률이 아니다. 환율은 국내 체결환율이나 개인 해외자산 수익률이 아니다.

정의·출처·단위·빈도·계절조정·발행 주체·관할·변환·공개/개정 특성·신선도 한도는 [plan.json](plan.json)에 있다. Fed 금리 CSV의 `Currency: NA`는 백분율이 통화 금액이 아니라는 의미이며 USD 국채 노출 정의와 구분해서 검증한다. FX의 단위는 역수인 USD/KRW 금액과 혼합하지 않는다.

## 자료와 시점

공식 CPI API와 CPI 발표문, Fed H.15 국채 CSV와 H.10 원화 CSV를 사용한다. [snapshots](snapshots)는 덮어쓰지 않는 해시 판본이며 full 원자료 또는 허용한 짧은 구절, 획득 완료 시각과 권리·접근 기록을 보존한다. [run_manifest.json](run_manifest.json)은 코드·방법·자료·보고서 해시, 정의·입력·관측·변환·제외 판본과 발표문 교차 확인을 담는다. API 키는 필요 없다.

관측일·발표일·획득일·vintage·개정일·valid-as-of·known-at는 다른 필드다. CPI 월별 관측일의 1일은 월을 식별하는 표지이며 발표일이 아니다. 최신 2026년 8월 원지수는 공식 발표문의 2026-09-11 08:30 ET(12:30 UTC), 관측 월과 동일 지수 값을 교차 확인했다. 발표문 확인에는 별도 snapshot과 세 구절의 provenance가 연결된다. 나머지 행의 최초 발표·개정 시각은 unknown이며 임의로 역산하지 않는다.

이번 API·CSV는 조회 당시의 판본이다. 원래 발표판이나 완전한 과거 vintage라고 주장하지 않는다. vintage는 획득 판본을 뜻하며, 전체 개정 이력이 없는 값은 해당 판본을 확보한 시각보다 앞선 조회에서 채택하지 않는다. 이후 판본은 `--previous-pins`로 추가하고 같은 기준 시점에서 이용 가능한 판본만 고른다. 미래에 수집한 발표 확인 자료를 과거 조회에 연결하지 않는다.

2025년 10월 CPI는 공식 응답의 결측 상태를 그대로 보존한다. 최신 값이 결측이면 과거 숫자로 현재를 채우지 않고, YoY는 정확히 12개월 떨어진 두 endpoint가 있을 때만 계산한다. 중간 월 결측은 공개하되 두 endpoint가 확인되는 YoY를 보간할 필요는 없다. 신선도 한도는 계획의 명시적 설정이며 공식 발표 달력 전체의 검증이 아니다.

## 이 판본에서 확인한 상태

| 항목 | 관측 기준 | 확인 값 |
| --- | --- | --- |
| CPI-U 원지수 / 계산된 YoY | 2026년 8월 | 334.980 / 약 3.397% |
| 2년 / 10년 국채 시장금리 | 2026-10-01 | 4.780% / 5.240% |
| 계산된 10년−2년 금리 차이 | 같은 날·같은 정의 | 0.460%p |
| USD 1당 KRW 기준환율 | 2026-09-25 | 1,356.510 KRW |

숫자의 정확한 Decimal 결과·계산식·입력 관측 ID·기간과 직전 변화는 보고서 부록에 있다. 물가의 월별 변화, 금리의 직전 영업일 변화, 환율의 직전 공개 관측 변화는 같은 기간의 신호가 아니다. 단일 경제 국면·경기 예측·자산 순위·배분을 생성하지 않는다.

## 인터넷 없는 replay와 과거 조회

저장소 루트에서 실행한다.

```bash
python -m investment_research macro replay examples/macro_case --store examples/macro_case/snapshots --pins examples/macro_case/pins.json
python -m investment_research macro replay examples/macro_case --store examples/macro_case/snapshots --pins examples/macro_case/pins.json --as-of 2025-06-30T23:59:59+09:00
```

두 번째 실행은 필요한 당시 판본이 없으므로 현재 자료를 과거에 넣지 않고 모두 차단된 정상 결과를 출력한다. 시간대가 있는 시각 또는 `YYYY-MM-DD`(그 날짜 UTC 끝)를 받는다. 한국 날짜 끝이 목적이면 예시처럼 `+09:00`을 지정한다. 기본 replay는 현재 벽시계 대신 pins의 기준 시각을 사용한다.

새 실제 획득은 명시적 명령으로만 한다. 기존 저장소의 판본도 계속 참조하려면 같은 store와 plan을 사용한다. 기존 결과를 덮어쓰지 않도록 새 pins·출력 경로를 지정한다.

```bash
python -m investment_research macro acquire examples/macro_case --store examples/macro_case/snapshots --previous-pins examples/macro_case/pins.json --pins reports/macro_new_pins.json
python -m investment_research macro replay examples/macro_case --store examples/macro_case/snapshots --pins reports/macro_new_pins.json --output reports/macro_new_snapshot.md --manifest reports/macro_new_manifest.json
```

출처 실패·정의 변경·단위/빈도 불일치·오래된 값은 해당 결과를 제한하고 진단을 남긴다. `acquire`의 일부 실패는 종료 코드 1이며 실패 snapshot도 보존한다. `replay`의 데이터 부족은 정상적인 결론 유보로 완료할 수 있다. 입력·출력 보호 오류는 2다. 자세한 계약과 테스트는 [거시 MVP 안내](../../docs/macro-mvrs.md)에 있다.

## 권리와 보존 한계

BLS와 Federal Reserve Board의 공공 자료를 출처와 획득 시점, 기록된 이용 조건과 함께 보존했다. BLS API의 공개 이용 안내를 적용했고 API와 일반 웹 크롤링을 구분했다. 일반 HTTP는 기존 robots·허용 URL·timeout·크기 한도·보존 정책을 따른다. 로고·공식 인장·별도 권리의 이미지는 수집하지 않았다. BLS API를 사용한 보고서에는 다음 원문을 포함한다.

> BLS.gov cannot vouch for the data or analyses derived from these data after the data have been retrieved from BLS.gov.

[initial_capture](initial_capture/README.md)는 수정 전의 첫 획득·보고서·실행 기록을 보존한 작업 기록이다. 그 판본은 획득 시각을 요청 시작 시각으로 기록했으므로 엄밀한 과거 가용성 증명에 사용하지 않는다. 상위 pins는 HTTP 응답과 파싱 완료 후 시각을 기록한 재획득 판본만 고정한다.
