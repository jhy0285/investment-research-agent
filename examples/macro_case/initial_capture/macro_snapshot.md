# Macro Regime Snapshot · 공개 거시자료

## 기준 시점

- 정보 기준 시각: 2026-10-03T17:04:47.018669+00:00 (UTC).
- 한국 시각: 2026-10-04T02:04:47.018669+09:00 (Asia/Seoul). 두 표시는 같은 순간이다.
- 연구 질문: 확인 가능한 미국 물가·국채 금리와 KRW 환율은 각각 어떤 상태이며, 관측·공개·판본의 한계는 무엇인가?.
- 선택한 정의와 저장된 판본 중 이 기준 시각에 이용 가능한 관측만 사용한다. 관측일·발표일·획득일은 다르다.
- '현재'는 이 고정 기준 시각의 이용 가능한 자료를 뜻한다. 실시간 가격·전 시장·개인 투자 결론은 조사 범위에 없다.

## 한눈에 보기

미국 headline CPI의 전년 동월 대비 상승률은 3.397%다 ([계산 f44a6c9d](#macro-record-135c71a790e352208406355e02499f30c78dca15befd5d8253357eac1a49f4bd)).
전월의 전년 대비 상승률과 비교한 방향은 상승이며, 변화는 0.032%p다 ([계산 860c1901](#macro-record-18c0be33598c43cb644eb828f5bee59ba058e6b1369e4eb73e226bf7eb61da97)).
같은 관측일의 미국 10년−2년 명목 국채 수익률 차이는 0.460%p다 ([계산 ee685027](#macro-record-89d85ed99ca36f8a4e4b399a5fae60720bd1161987d00ee77a4ed9ad294499f9)).
USD당 KRW 기준 환율은 직전 관측과 비교해 하락했다 ([계산 642bb49e](#macro-record-b838a4610a8a8b372a7fb0ca1d8187422aab771e6878d4377aed17f85e9bff40)).
고용·정책금리·실질금리·성장·신용·유동성은 이번 자료에 없으므로 전체 경기 상태나 자산 매력을 확정하지 않는다.

## 금리

사용한 금리는 미국 국채의 **명목 시장 수익률**이다. 중앙은행 정책금리·예금 이자·확정 투자수익과 구분한다.

| 자료 | 기준 관측 | 값 | 채택 상태 |
| --- | --- | --- | --- |
| 미국 국채 10년 명목 시장금리 | 2026-10-01 | 5.240 % ([관측 02f3966b](#macro-record-dec681c9d0d53e8079a1cd93ad2a9649a5140e606e75ce89acd701c144c31ed7)) | 사용 가능 |
| 미국 국채 2년 명목 시장금리 | 2026-10-01 | 4.780 % ([관측 a826e005](#macro-record-23dcf82b388a59a78123e8dbcab2fb66a5f90f0ba36b9285f9f3c517fcaa54b7)) | 사용 가능 |

- [계산 결과] 미국 국채 10년 명목 시장금리 · 직전 관측치 대비 변화: -0.050 %p; 두 비교값 사이의 방향: 하락; 비교 관측일: 2026-09-30, 2026-10-01 ([계산 37d30e6a](#macro-record-7d669ad8f2af833c39930ecb0379b2a4436556accc728156be36f8f0378149b0)).
- [계산 결과] 미국 국채 2년 명목 시장금리 · 직전 관측치 대비 변화: -0.100 %p; 두 비교값 사이의 방향: 하락; 비교 관측일: 2026-09-30, 2026-10-01 ([계산 93a6dd37](#macro-record-5c5cbb33b48d2dacdf7cccbcfb060bc567dfdc5f10a72bc87e0dc351ac6d16a0)).
- [계산 결과] 미국 국채 10년 명목 시장금리 / 미국 국채 2년 명목 시장금리 · 10년−2년 국채 수익률 차이: 0.460 %p; 비교 관측일: 2026-10-01 ([계산 ee685027](#macro-record-89d85ed99ca36f8a4e4b399a5fae60720bd1161987d00ee77a4ed9ad294499f9)).

직전 관측 비교는 두 날짜 사이의 변화다. 지속적인 추세나 '역사적으로 높은 금리'를 판정하는 규칙은 구현하지 않았다.

## 물가

미국 도시 소비자 headline CPI의 **계절조정하지 않은 지수**를 사용한다. Core CPI나 계절조정 전월비와 합치지 않는다.

| 자료 | 기준 관측 | 값 | 채택 상태 |
| --- | --- | --- | --- |
| 미국 headline CPI-U 원지수 (NSA) | 2026-08-01 | 334.980 지수 ([관측 94cc77e8](#macro-record-065e317440d9ce1eca7955edb6860e53b4888e1f922d3057b399e810c9c708a9)) | 사용 가능 |

- [계산 결과] 미국 headline CPI-U 원지수 (NSA) · 직전 관측치 대비 변화: 1.062 지수; 두 비교값 사이의 방향: 상승; 비교 관측일: 2026-07-01, 2026-08-01 ([계산 de92c812](#macro-record-d502fede48ad9f5c1825bfe9fce567e9a84835ddf2ecfc53b3be83fd0fe8c8ba)).
- [계산 결과] 미국 headline CPI-U 원지수 (NSA) · 전년 동월 대비 물가 상승률: 3.397 %; 비교 관측일: 2025-08-01, 2026-08-01 ([계산 f44a6c9d](#macro-record-135c71a790e352208406355e02499f30c78dca15befd5d8253357eac1a49f4bd)).
- [계산 결과] 미국 headline CPI-U 원지수 (NSA) · 전월 대비 물가 상승률 변화: 0.032 %p; 두 비교값 사이의 방향: 상승; 비교 관측일: 2025-07-01, 2025-08-01, 2026-07-01, 2026-08-01 ([계산 860c1901](#macro-record-18c0be33598c43cb644eb828f5bee59ba058e6b1369e4eb73e226bf7eb61da97)).

지수의 직전 관측 변화는 물가 수준의 변화이며 물가 상승률의 방향과 다르다. 상승률 방향은 현재 YoY와 정확한 전월 YoY의 차이로만 표시한다.
계절조정하지 않은 지수의 전월 변화에는 계절성이 포함될 수 있다. 상승률 하락은 가격 자체의 하락을 뜻하지 않는다.

## 경기 / 고용

이번 작은 자료 집합에는 고용·실업·생산·성장 지표가 없다. 경기 둔화·침체나 고용 강약을 대신 추론하지 않았다.

## 환율 / 한국 투자자 관점

USD/KRW는 **USD당 KRW**다. 뉴욕 정오 기준 환율 관측을 쓰며 국내 체결 환율·실시간 호가·환전 비용과 구분한다.

| 자료 | 기준 관측 | 값 | 채택 상태 |
| --- | --- | --- | --- |
| 원/달러 뉴욕 정오 기준환율 | 2026-09-25 | 1356.510 원/USD ([관측 891c0cc2](#macro-record-54dfa207ef2d41af4b7b1e6ff59137c447b588ee14b0fc1d32187e3d131b2d70)) | 사용 가능 |

- [계산 결과] 원/달러 뉴욕 정오 기준환율 · 직전 관측치 대비 변화: -12.930 원/USD; 두 비교값 사이의 방향: 하락; 비교 관측일: 2026-09-24, 2026-09-25 ([계산 642bb49e](#macro-record-b838a4610a8a8b372a7fb0ca1d8187422aab771e6878d4377aed17f85e9bff40)).

[정의에 따른 해석] 같은 USD를 원화로 표시할 때 금액이 작아졌다는 뜻이며, 이 관측 사이에서는 원화 강세에 해당한다. ([계산 642bb49e](#macro-record-b838a4610a8a8b372a7fb0ca1d8187422aab771e6878d4377aed17f85e9bff40)).

미국 자산 자체의 USD 시장환경과 한국 투자자의 KRW 평가환경은 별도다. 자산 가격·배당·환헤지·비용·세금 자료 없이 개인의 KRW 수익률을 계산하지 않았다.

## 서로 상충하는 신호

[관측·계산] 전년 대비 물가 상승률의 전월 비교는 상승, 10년 시장금리의 직전 관측 비교는 하락이다 ([계산 860c1901](#macro-record-18c0be33598c43cb644eb828f5bee59ba058e6b1369e4eb73e226bf7eb61da97), [계산 37d30e6a](#macro-record-7d669ad8f2af833c39930ecb0379b2a4436556accc728156be36f8f0378149b0)).
[해석 후보] 방향이 같지 않아 '물가 변화가 금리 변화를 전부 설명한다'는 단순한 설명만으로 읽기 어렵다. 성장 기대·기간 프리미엄 등 다른 설명을 검토해야 하지만 이번 자료는 원인을 확인하지 않는다.
물가 비교는 월별, 금리 비교는 일별이며 서로 다른 관측창이다. 같은 사건에 대한 통계적 모순으로 판정하지 않는다.

## 투자환경에 어떤 의미가 있을 수 있는가

아래는 **조건부 전파 경로·검토 전 해석 후보**다. 위 관측 사실·계산 결과와 구분하며, 경제적 관계의 실증 검증이나 투자 규칙으로 확정하지 않는다.

- **금리 → 채권·기업 가치:** 다른 조건이 같고 현금흐름이 고정되어 있다면 할인율 변화는 현재가치에 영향을 줄 수 있다. 입력 사실: [관측 02f3966b](#macro-record-dec681c9d0d53e8079a1cd93ad2a9649a5140e606e75ce89acd701c144c31ed7), [관측 a826e005](#macro-record-23dcf82b388a59a78123e8dbcab2fb66a5f90f0ba36b9285f9f3c517fcaa54b7). 실제 영향에는 만기·듀레이션·신용·이익 전망이 필요하며 여기서는 계산하지 않았다.
- **물가 → 현금·채권의 구매력:** 명목 이자와 같은 기간의 실제 물가 변화가 필요하다. 입력 사실: [계산 f44a6c9d](#macro-record-135c71a790e352208406355e02499f30c78dca15befd5d8253357eac1a49f4bd). 현재 YoY를 미래 물가나 특정 자산의 실질수익으로 바꾸지 않았다.
- **환율 → 해외자산의 KRW 표시 가치:** 같은 USD 가치와 환노출을 유지한다는 조건에서 환율은 원화 평가에 영향을 줄 수 있다. 입력 사실: [계산 642bb49e](#macro-record-b838a4610a8a8b372a7fb0ca1d8187422aab771e6878d4377aed17f85e9bff40). 실제 상품·환헤지·평가 시점과 사용자 보유 내역은 미확인이다.

현금·국채·주식·배당주·금·원자재·에너지·암호자산·한국 부동산의 향후 연구가 이 근거를 참조할 수 있다. 이번에는 해당 자산의 상대 매력·정해진 대응·매수/매도·배분을 생성하지 않는다.

## 아직 말할 수 없는 것

- 정책금리의 최근 방향, 고용 강약, 경기 침체 여부, 한국 기준금리·한국 물가, 실질금리·신용·유동성의 전체 상태.
- '높다/낮다'의 역사적 기준, 지속적인 추세, 미래 금리·환율·물가, 기대수익·자산 순위·개인 투자비중.
- 공식 개정 이력의 전체 재현: 저장한 판본은 시스템의 획득 판본이며 공식 release/vintage archive와 같지 않다.
- 공개·개정 시각이 unknown인 현재 파일의 값이 과거 투자자에게 같은 형태로 보였는지 여부.
- 관측 주기와 발표 지연 사이의 아직 발표되지 않은 최신 값. 결측·오래된 자료는 이전 값으로 조용히 채우지 않는다.
- 개인 보유자산·현금흐름·부채·필요 자금이 미확인이므로 이 환경이 사용자에게 적절한 배분을 뜻하는지 여부.

## 초간단 설명

이 보고서는 정한 시각까지 알 수 있었던 물가·국채 금리·환율 자료를 살펴본다.
숫자가 언제의 자료이고 언제 알려졌는지 확인하고, 없는 값은 만들어 넣지 않는다.
물가 상승이 느려지는 것과 물건 가격이 내려가는 것은 다르다.
달러 값이 원화로 바뀌는 효과는 미국 자산 자체의 움직임과 따로 봐야 한다.
이 자료만으로 무엇을 사거나 돈을 얼마나 나눌지 정할 수는 없다.

## 부록 · 근거와 재현 기록

- 연구 ID: CURRENT\_OFFICIAL\_MACRO; 입력 SHA-256: e0b85e2202f7e47d135c56531e0409f137c8e6cad4892de12180ea7994e19574.
- 시계열 방법: macro_series_v1; 보고서 방법: macro_report_v1.
- 본문 수치는 소수 셋째 자리까지 표시했다. 아래 계산의 정확한 Decimal 값·원관측·공식·가정은 보존한다.
- release/vintage/revision의 unknown을 관측일이나 획득일로 채우지 않는다. unknown일 때 이용 가능성은 획득 시각부터 보수적으로 인정한다.
- 전체 observation·제외된 판본·결측·진단은 실행 manifest와 저장된 snapshot에 남긴다. 이 부록은 본문·계산이 참조한 근거를 보여 준다.

### 시계열 정의와 선택

#### 원/달러 뉴욕 정오 기준환율

- canonical ID: USD\_KRW\_NOON\_REFERENCE; 정의 SHA-256: 83a506c0a89a9628fa9ce0597ce7e87c4245004734d3a16b63c0c69383c4665a.
- 정의: South Korean won per U.S. dollar; noon New York buying/reference rate. An increase means more KRW per USD, not a domestic executed FX rate or a realized foreign-asset return..
- 단위: KRW\_per\_USD; 빈도: daily; 계절조정: not\_seasonally\_adjusted; 통화: KRW; 변환: raw.
- 발행 주체: Board of Governors of the Federal Reserve System; 관할: US; 출처: [FED\_H10\_KRW](#macro-record-f56e2932df7c7cf95311e4e66639477af2df08d54da6d6f81da7d23af5c880f1).
- 발표 특성: Daily observations normally published in a weekly H.10 release; no invented weekend or not-yet-released daily value.; 개정 특성: Current country CSV can incorporate subsequent corrections; an official August 2026 correction notice exists, but full row revision timestamps/history are unavailable..
- 선택 상태: 사용 가능; 전체 판본 250개, 시점 조건 뒤 선택한 기간 250개, 이후 정보로 제외한 판본 0개.
- 신선도 규칙: 기준 시점의 날짜와 마지막 관측일의 차이가 14일을 초과하면 stale.
- 마지막 선택 관측: 2026-09-25; 공개: unknown · 미확인; 획득: 2026-10-03T17:04:46.206080+00:00; vintage: 2026-10-03T17:04:46.206080+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:04:46.206080+00:00; valid-as-of: unknown · 미확인.
- 마지막 관측의 snapshot: de55ccd831e80f7ded1f2b94a6e6e9c5ec48cee21d8e4c9a42598c3ef749fda6; vintage ID: retrieved\_snapshot:de55ccd831e80f7ded1f2b94a6e6e9c5ec48cee21d8e4c9a42598c3ef749fda6.
- 선택 진단의 요약: OBS\_ad06d0e9d0546c813a2339be4452040f2b401490b83c5f01933790de2a96cf31: 공개 시각 unknown: 획득 시각을 보수적인 이용 가능 시점으로 사용 / OBS\_891c0cc274ded59a917a2734e7aaedadf85b61909f310164019a14803f364323: 공개 시각 unknown: 획득 시각을 보수적인 이용 가능 시점으로 사용.

#### 미국 headline CPI-U 원지수 (NSA)

- canonical ID: US\_CPI\_U\_HEADLINE\_NSA; 정의 SHA-256: 799a3bb2c4ca2bcd89845bf817ae9df864228a7b3e588777b67727ba731e3705.
- 정의: All items CPI-U, U.S. city average, 1982–84=100; not seasonally adjusted. Monthly label is the reference month, not the release date..
- 단위: index; 빈도: monthly; 계절조정: not\_seasonally\_adjusted; 통화: 해당 없음; 변환: raw.
- 발행 주체: U.S. Bureau of Labor Statistics; 관할: US; 출처: [BLS\_CPI\_API](#macro-record-c436613f5d09e28fd85e2bc46b272d6421f81f0e3f63f160bcbb83e83676c4ce).
- 발표 특성: Monthly, typically released in the following month; date varies. Current release is cross-checked against retained official excerpts.; 개정 특성: Full release/revision history absent from v1 API. Current fetched version is not a historical first release; missing October 2025 remains explicit..
- 선택 상태: 사용 가능; 전체 판본 32개, 시점 조건 뒤 선택한 기간 32개, 이후 정보로 제외한 판본 0개.
- 신선도 규칙: 기준 시점의 날짜와 마지막 관측일의 차이가 75일을 초과하면 stale.
- 마지막 선택 관측: 2026-08-01; 공개: 2026-09-11T12:30:00+00:00; 획득: 2026-10-03T17:04:44.497792+00:00; vintage: 2026-10-03T17:04:44.497792+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:04:44.497792+00:00; valid-as-of: unknown · 미확인.
- 마지막 관측의 snapshot: e6b8fb0636747b1f0e563cd3e0d619a404b993c8849bf2465ad720a42bc10807; vintage ID: retrieved\_snapshot:e6b8fb0636747b1f0e563cd3e0d619a404b993c8849bf2465ad720a42bc10807.
- 선택 진단의 요약: OBS\_72142b33b807af3389703165bd2a6e13d71015dfbdb4b4e06c3e6f698f637ac9: 공개 시각 unknown: 획득 시각을 보수적인 이용 가능 시점으로 사용 / OBS\_b2d730c197805a22e7146e775e339fe39d17b858cc873eab50c92a69f09cf734: 공개 시각 unknown: 획득 시각을 보수적인 이용 가능 시점으로 사용.

#### 미국 국채 10년 명목 시장금리

- canonical ID: US\_TREASURY\_NOMINAL\_10Y; 정의 SHA-256: b7a6bce81ddb6d782c1a5e9fead7c0676e396603d4353da3f603992b650eb1c5.
- 정의: 10-year constant-maturity Treasury yield, quoted on investment basis, annual percent; not policy rate, real yield or realized bond return. CSV Currency NA means no currency amount; underlying Treasury exposure is USD..
- 단위: percent; 빈도: daily; 계절조정: not\_seasonally\_adjusted; 통화: USD; 변환: raw.
- 발행 주체: Board of Governors of the Federal Reserve System; 관할: US; 출처: [FED\_H15\_TREASURY](#macro-record-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700).
- 발표 특성: U.S. business-day observation; publication lag and weekends differ from observation date.; 개정 특성: Current H.15 CSV may include corrections; complete first-release/vintage history unavailable..
- 선택 상태: 사용 가능; 전체 판본 262개, 시점 조건 뒤 선택한 기간 262개, 이후 정보로 제외한 판본 0개.
- 신선도 규칙: 기준 시점의 날짜와 마지막 관측일의 차이가 10일을 초과하면 stale.
- 마지막 선택 관측: 2026-10-01; 공개: unknown · 미확인; 획득: 2026-10-03T17:04:45.465763+00:00; vintage: 2026-10-03T17:04:45.465763+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:04:45.465763+00:00; valid-as-of: unknown · 미확인.
- 마지막 관측의 snapshot: 6b7d398baaa1ffd3472b655d3830f04cca228b7aafedc05a904fdcdeb2caab24; vintage ID: retrieved\_snapshot:6b7d398baaa1ffd3472b655d3830f04cca228b7aafedc05a904fdcdeb2caab24.
- 선택 진단의 요약: OBS\_b1687d5d6489c850a4a03e6152964fe70c7957547538e3a05f59b120cadff2be: 공개 시각 unknown: 획득 시각을 보수적인 이용 가능 시점으로 사용 / OBS\_02f3966bf35339cdb6052fce5899738d82afd47163df2c50c46fe8afe1da7190: 공개 시각 unknown: 획득 시각을 보수적인 이용 가능 시점으로 사용.

#### 미국 국채 2년 명목 시장금리

- canonical ID: US\_TREASURY\_NOMINAL\_2Y; 정의 SHA-256: 4702cfbc58c13aa906b2af823595ae9d8e477e414e5fccad50e093887cffe061.
- 정의: 2-year constant-maturity Treasury yield, quoted on investment basis, annual percent; not policy rate, real yield or realized bond return. CSV Currency NA means no currency amount; underlying Treasury exposure is USD..
- 단위: percent; 빈도: daily; 계절조정: not\_seasonally\_adjusted; 통화: USD; 변환: raw.
- 발행 주체: Board of Governors of the Federal Reserve System; 관할: US; 출처: [FED\_H15\_TREASURY](#macro-record-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700).
- 발표 특성: U.S. business-day observation; publication lag and weekends differ from observation date.; 개정 특성: Current H.15 CSV may include corrections; complete first-release/vintage history unavailable..
- 선택 상태: 사용 가능; 전체 판본 262개, 시점 조건 뒤 선택한 기간 262개, 이후 정보로 제외한 판본 0개.
- 신선도 규칙: 기준 시점의 날짜와 마지막 관측일의 차이가 10일을 초과하면 stale.
- 마지막 선택 관측: 2026-10-01; 공개: unknown · 미확인; 획득: 2026-10-03T17:04:45.465763+00:00; vintage: 2026-10-03T17:04:45.465763+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:04:45.465763+00:00; valid-as-of: unknown · 미확인.
- 마지막 관측의 snapshot: 6b7d398baaa1ffd3472b655d3830f04cca228b7aafedc05a904fdcdeb2caab24; vintage ID: retrieved\_snapshot:6b7d398baaa1ffd3472b655d3830f04cca228b7aafedc05a904fdcdeb2caab24.
- 선택 진단의 요약: OBS\_01a92da286879f6d11614f31f55078a52017d948e98eb4ccd032779e0dd5c6cc: 공개 시각 unknown: 획득 시각을 보수적인 이용 가능 시점으로 사용 / OBS\_a826e005dd0e6b111db645c4fe75a4d08f486d223e430db1a349cc36cf983d29: 공개 시각 unknown: 획득 시각을 보수적인 이용 가능 시점으로 사용.

### 고정 출처와 snapshot

<a id="macro-record-7b5bff1cb9bb41923e363e62038c607890f6074f6332453191a0e9cedcdf8927"></a>

- Consumer Price Index — August 2026 release; 출처 ID: BLS\_CPI\_RELEASE; 위치: https://www.bls.gov/news.release/cpi.htm.
- 사용한 고정 snapshot: 71e2da2f67bebfe1ffe6afe7af1dfa2fac529b47cce893a5a5b815ba83f86ea6.
- source-level metadata의 판본: 71e2da2f67bebfe1ffe6afe7af1dfa2fac529b47cce893a5a5b815ba83f86ea6; 획득: 2026-10-03T17:04:38.103680Z; 각 관측의 정확한 판본은 아래 evidence의 snapshot을 따른다.
- 접근: public\_http; 보존: excerpt; 상태: available.
- 정책: https://www.bls.gov/bls/linksite.htm; 검토: Official BLS public-domain release; preserve only three verification excerpts with attribution. Separate API terms apply to API data..
- 원문 SHA-256: f19802d4f56fbe007d78f6aa14a075c7899077705c5d503d61230c498640088c; 정규화 SHA-256: dc72b00e0269c97851e24e9967283ae96994b51a61a71aff7e21394368c72ff0; payload SHA-256: 3f7e347e2146b1e483a63b9df2f50561206b6fa577e23c9d5a534557bf546d50.
- 이 BLS 자료의 실제 획득 시각: 2026-10-03T17:04:38.103680Z.
- BLS 이용 안내 · 획득 이후 분석에 대한 보증 없음: BLS.gov cannot vouch for the data or analyses derived from these data after the data have been retrieved from BLS.gov.

<a id="macro-record-c436613f5d09e28fd85e2bc46b272d6421f81f0e3f63f160bcbb83e83676c4ce"></a>

- BLS CPI-U all items, U.S. city average, not seasonally adjusted; 출처 ID: BLS\_CPI\_API; 위치: https://api.bls.gov/publicAPI/v1/timeseries/data/CUUR0000SA0.
- 사용한 고정 snapshot: e6b8fb0636747b1f0e563cd3e0d619a404b993c8849bf2465ad720a42bc10807.
- source-level metadata의 판본: e6b8fb0636747b1f0e563cd3e0d619a404b993c8849bf2465ad720a42bc10807; 획득: 2026-10-03T17:04:44.497792Z; 각 관측의 정확한 판본은 아래 evidence의 snapshot을 따른다.
- 접근: public\_api; 보존: full; 상태: available.
- 정책: https://www.bls.gov/developers/termsOfService.htm; 검토: Documented unregistered v1 GET API: https://www.bls.gov/developers/api\_signature.htm . Public-domain data: https://www.bls.gov/bls/linksite.htm . Cite access/retrieval date. BLS.gov cannot vouch for the data or analyses derived from these data after the data have been retrieved from BLS.gov..
- 원문 SHA-256: 6087dfe410f56e3147a89732ff0acc03aed6d4e620bf27fc406d239a0394acd1; 정규화 SHA-256: 9ee19857a34b1918577158ad53e33f6f205b8a5c528e058560f6f000be2fc3a0; payload SHA-256: 2938b8e5da8223222982e4c5e4f3c1355438342556360e92162e943acb06902d.
- 이 BLS 자료의 실제 획득 시각: 2026-10-03T17:04:44.497792Z.
- BLS 이용 안내 · 획득 이후 분석에 대한 보증 없음: BLS.gov cannot vouch for the data or analyses derived from these data after the data have been retrieved from BLS.gov.

<a id="macro-record-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700"></a>

- H.15 Treasury constant-maturity nominal yield CSV; 출처 ID: FED\_H15\_TREASURY; 위치: https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&amp;series=bf17364827e38702b42a58cf8eaa3f78&amp;lastobs=&amp;from=&amp;to=&amp;filetype=csv&amp;label=include&amp;layout=seriescolumn&amp;type=package.
- 사용한 고정 snapshot: 6b7d398baaa1ffd3472b655d3830f04cca228b7aafedc05a904fdcdeb2caab24.
- source-level metadata의 판본: 6b7d398baaa1ffd3472b655d3830f04cca228b7aafedc05a904fdcdeb2caab24; 획득: 2026-10-03T17:04:45.465763Z; 각 관측의 정확한 판본은 아래 evidence의 snapshot을 따른다.
- 접근: public\_http; 보존: full; 상태: available.
- 정책: https://www.federalreserve.gov/disclaimer.htm; 검토: The Federal Reserve Board permits reuse of public-domain information with Board attribution; no seals, logos or third-party content are fetched..
- 원문 SHA-256: a72bc770cb6c4f269931eb4014d7dfe4f9624dd948649d765fefdaf4f718fd7c; 정규화 SHA-256: 7fc1b00a97692140da18af34f07c863d5e87102056dd24429397d5902088892b; payload SHA-256: 2816fe45201beabe3da0c4732dc3bad68a1c7b418057264de84e145ffe2935c2.

<a id="macro-record-f56e2932df7c7cf95311e4e66639477af2df08d54da6d6f81da7d23af5c880f1"></a>

- H.10 South Korean won per U.S. dollar daily reference rate CSV; 출처 ID: FED\_H10\_KRW; 위치: https://www.federalreserve.gov/datadownload/Output.aspx?rel=H10&amp;series=60f32914ab61dfab590e0e470153e3ae&amp;lastobs=250&amp;from=&amp;to=&amp;filetype=csv&amp;label=include&amp;layout=seriescolumn&amp;type=package.
- 사용한 고정 snapshot: de55ccd831e80f7ded1f2b94a6e6e9c5ec48cee21d8e4c9a42598c3ef749fda6.
- source-level metadata의 판본: de55ccd831e80f7ded1f2b94a6e6e9c5ec48cee21d8e4c9a42598c3ef749fda6; 획득: 2026-10-03T17:04:46.206080Z; 각 관측의 정확한 판본은 아래 evidence의 snapshot을 따른다.
- 접근: public\_http; 보존: full; 상태: available.
- 정책: https://www.federalreserve.gov/disclaimer.htm; 검토: The Federal Reserve Board permits reuse of public-domain information with Board attribution; no seals, logos or third-party content are fetched. Definition: https://www.federalreserve.gov/releases/h10/about.htm . Noon New York buying rate; daily observations released weekly; current country CSV can include later corrections..
- 원문 SHA-256: d15be650c4a2484ddd9c09dc63f2ff70386b0e57ecde3da70f0106d194007eed; 정규화 SHA-256: a6df24ddc46749152062d97001a2dac7cd897203e57f2fc8ff2f36ad0e256353; payload SHA-256: f30d02b572c8722d2c9e5645130190f2da29bcbdcd83c97897225de4045f0802.

### 본문과 계산이 참조한 원관측 / 기존 EvidenceRecord

<a id="macro-record-1560076feaeffcc88d7784e86393d4997ccfdef35436445a232eaeb30923b1b6"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_01a92da286879f6d11614f31f55078a52017d948e98eb4ccd032779e0dd5c6cc</code>.
- [관측 01a92da2](#macro-record-1560076feaeffcc88d7784e86393d4997ccfdef35436445a232eaeb30923b1b6): US\_TREASURY\_NOMINAL\_2Y; 관측일: 2026-09-30; 원자료 값: 4.88 percent.
- 출처: [FED\_H15\_TREASURY](#macro-record-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700); snapshot: 6b7d398baaa1ffd3472b655d3830f04cca228b7aafedc05a904fdcdeb2caab24; 원문 위치: CSV row 16898, column RIFLGFCY02\_N.B, Time Period=2026-09-30.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:04:45.465763+00:00; vintage: 2026-10-03T17:04:45.465763+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:04:45.465763+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: fresh. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

<a id="macro-record-dec681c9d0d53e8079a1cd93ad2a9649a5140e606e75ce89acd701c144c31ed7"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_02f3966bf35339cdb6052fce5899738d82afd47163df2c50c46fe8afe1da7190</code>.
- [관측 02f3966b](#macro-record-dec681c9d0d53e8079a1cd93ad2a9649a5140e606e75ce89acd701c144c31ed7): US\_TREASURY\_NOMINAL\_10Y; 관측일: 2026-10-01; 원자료 값: 5.24 percent.
- 출처: [FED\_H15\_TREASURY](#macro-record-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700); snapshot: 6b7d398baaa1ffd3472b655d3830f04cca228b7aafedc05a904fdcdeb2caab24; 원문 위치: CSV row 16899, column RIFLGFCY10\_N.B, Time Period=2026-10-01.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:04:45.465763+00:00; vintage: 2026-10-03T17:04:45.465763+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:04:45.465763+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: fresh. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

<a id="macro-record-41b79b9cd60d17966ac516fb10dbfca749cde79768f61069bdc789c0c9b1d7ce"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_238aa5ba8ba0022dab4c858ee6ff53fd61dd05c7f3d64cfefa8064cd2b0eb4c1</code>.
- [관측 238aa5ba](#macro-record-41b79b9cd60d17966ac516fb10dbfca749cde79768f61069bdc789c0c9b1d7ce): US\_CPI\_U\_HEADLINE\_NSA; 관측일: 2025-08-01; 원자료 값: 323.976 index.
- 출처: [BLS\_CPI\_API](#macro-record-c436613f5d09e28fd85e2bc46b272d6421f81f0e3f63f160bcbb83e83676c4ce); snapshot: e6b8fb0636747b1f0e563cd3e0d619a404b993c8849bf2465ad720a42bc10807; 원문 위치: /Results/series/0/data/13/value; year=2025, period=M08.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:04:44.497792+00:00; vintage: 2026-10-03T17:04:44.497792+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:04:44.497792+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: stale. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

<a id="macro-record-ee97e9613c57221cd8935ad3fa7d9637c5507fe89c1ffac16b33fa3ccd446ce4"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_5965910686354208a1e0caf0ca107cd51b8981eb54b7099656005d2506c8e282</code>.
- [관측 59659106](#macro-record-ee97e9613c57221cd8935ad3fa7d9637c5507fe89c1ffac16b33fa3ccd446ce4): US\_CPI\_U\_HEADLINE\_NSA; 관측일: 2025-07-01; 원자료 값: 323.048 index.
- 출처: [BLS\_CPI\_API](#macro-record-c436613f5d09e28fd85e2bc46b272d6421f81f0e3f63f160bcbb83e83676c4ce); snapshot: e6b8fb0636747b1f0e563cd3e0d619a404b993c8849bf2465ad720a42bc10807; 원문 위치: /Results/series/0/data/14/value; year=2025, period=M07.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:04:44.497792+00:00; vintage: 2026-10-03T17:04:44.497792+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:04:44.497792+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: stale. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

<a id="macro-record-54dfa207ef2d41af4b7b1e6ff59137c447b588ee14b0fc1d32187e3d131b2d70"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_891c0cc274ded59a917a2734e7aaedadf85b61909f310164019a14803f364323</code>.
- [관측 891c0cc2](#macro-record-54dfa207ef2d41af4b7b1e6ff59137c447b588ee14b0fc1d32187e3d131b2d70): USD\_KRW\_NOON\_REFERENCE; 관측일: 2026-09-25; 원자료 값: 1356.5100 KRW\_per\_USD.
- 출처: [FED\_H10\_KRW](#macro-record-f56e2932df7c7cf95311e4e66639477af2df08d54da6d6f81da7d23af5c880f1); snapshot: de55ccd831e80f7ded1f2b94a6e6e9c5ec48cee21d8e4c9a42598c3ef749fda6; 원문 위치: CSV row 256, column RXI\_N.B.KO, Time Period=2026-09-25.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:04:46.206080+00:00; vintage: 2026-10-03T17:04:46.206080+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:04:46.206080+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: fresh. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

<a id="macro-record-065e317440d9ce1eca7955edb6860e53b4888e1f922d3057b399e810c9c708a9"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_94cc77e82c1475f818e668ef6b82c714e6e7131193182906421f7df92c4c6750</code>.
- [관측 94cc77e8](#macro-record-065e317440d9ce1eca7955edb6860e53b4888e1f922d3057b399e810c9c708a9): US\_CPI\_U\_HEADLINE\_NSA; 관측일: 2026-08-01; 원자료 값: 334.980 index.
- 출처: [BLS\_CPI\_API](#macro-record-c436613f5d09e28fd85e2bc46b272d6421f81f0e3f63f160bcbb83e83676c4ce); snapshot: e6b8fb0636747b1f0e563cd3e0d619a404b993c8849bf2465ad720a42bc10807; 원문 위치: /Results/series/0/data/0/value; year=2026, period=M08.
- 공개: 2026-09-11T12:30:00+00:00; 획득: 2026-10-03T17:04:44.497792+00:00; vintage: 2026-10-03T17:04:44.497792+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:04:44.497792+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: fresh. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

- 공개 시각의 확인 자료: [BLS\_CPI\_RELEASE](#macro-record-7b5bff1cb9bb41923e363e62038c607890f6074f6332453191a0e9cedcdf8927); snapshot: 71e2da2f67bebfe1ffe6afe7af1dfa2fac529b47cce893a5a5b815ba83f86ea6; 원문 구절 ID: RELEASE\_TIME, CPI\_PERIOD, CPI\_VALUE; 방법: bls\_release\_crosscheck\_v1. 관측 기간·지수·발표 시각의 좁은 대조이며 사후 투자 해석의 보증이 아니다.

<a id="macro-record-23dcf82b388a59a78123e8dbcab2fb66a5f90f0ba36b9285f9f3c517fcaa54b7"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_a826e005dd0e6b111db645c4fe75a4d08f486d223e430db1a349cc36cf983d29</code>.
- [관측 a826e005](#macro-record-23dcf82b388a59a78123e8dbcab2fb66a5f90f0ba36b9285f9f3c517fcaa54b7): US\_TREASURY\_NOMINAL\_2Y; 관측일: 2026-10-01; 원자료 값: 4.78 percent.
- 출처: [FED\_H15\_TREASURY](#macro-record-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700); snapshot: 6b7d398baaa1ffd3472b655d3830f04cca228b7aafedc05a904fdcdeb2caab24; 원문 위치: CSV row 16899, column RIFLGFCY02\_N.B, Time Period=2026-10-01.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:04:45.465763+00:00; vintage: 2026-10-03T17:04:45.465763+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:04:45.465763+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: fresh. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

<a id="macro-record-872dd2891484f02921e8dc54b0100cc65b2cff0a512ecb33b5d75236ef03f9aa"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_ad06d0e9d0546c813a2339be4452040f2b401490b83c5f01933790de2a96cf31</code>.
- [관측 ad06d0e9](#macro-record-872dd2891484f02921e8dc54b0100cc65b2cff0a512ecb33b5d75236ef03f9aa): USD\_KRW\_NOON\_REFERENCE; 관측일: 2026-09-24; 원자료 값: 1369.4400 KRW\_per\_USD.
- 출처: [FED\_H10\_KRW](#macro-record-f56e2932df7c7cf95311e4e66639477af2df08d54da6d6f81da7d23af5c880f1); snapshot: de55ccd831e80f7ded1f2b94a6e6e9c5ec48cee21d8e4c9a42598c3ef749fda6; 원문 위치: CSV row 255, column RXI\_N.B.KO, Time Period=2026-09-24.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:04:46.206080+00:00; vintage: 2026-10-03T17:04:46.206080+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:04:46.206080+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: fresh. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

<a id="macro-record-6586511c485df564f15ba6c4426e8dc522a35e87ca71eeb5e2908b9909e5ce56"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_b1687d5d6489c850a4a03e6152964fe70c7957547538e3a05f59b120cadff2be</code>.
- [관측 b1687d5d](#macro-record-6586511c485df564f15ba6c4426e8dc522a35e87ca71eeb5e2908b9909e5ce56): US\_TREASURY\_NOMINAL\_10Y; 관측일: 2026-09-30; 원자료 값: 5.29 percent.
- 출처: [FED\_H15\_TREASURY](#macro-record-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700); snapshot: 6b7d398baaa1ffd3472b655d3830f04cca228b7aafedc05a904fdcdeb2caab24; 원문 위치: CSV row 16898, column RIFLGFCY10\_N.B, Time Period=2026-09-30.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:04:45.465763+00:00; vintage: 2026-10-03T17:04:45.465763+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:04:45.465763+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: fresh. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

<a id="macro-record-8117233cc5094a3f847def2167a8a467046f26d7cd47d2024f829950272c9b80"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_b2d730c197805a22e7146e775e339fe39d17b858cc873eab50c92a69f09cf734</code>.
- [관측 b2d730c1](#macro-record-8117233cc5094a3f847def2167a8a467046f26d7cd47d2024f829950272c9b80): US\_CPI\_U\_HEADLINE\_NSA; 관측일: 2026-07-01; 원자료 값: 333.918 index.
- 출처: [BLS\_CPI\_API](#macro-record-c436613f5d09e28fd85e2bc46b272d6421f81f0e3f63f160bcbb83e83676c4ce); snapshot: e6b8fb0636747b1f0e563cd3e0d619a404b993c8849bf2465ad720a42bc10807; 원문 위치: /Results/series/0/data/1/value; year=2026, period=M07.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:04:44.497792+00:00; vintage: 2026-10-03T17:04:44.497792+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:04:44.497792+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: stale. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

### 결정적 계산 · 채택 가능한 값만 기존 MetricResult

<a id="macro-record-b838a4610a8a8b372a7fb0ca1d8187422aab771e6878d4377aed17f85e9bff40"></a>

- 계산 ID: <code>MET_642bb49ea0c5dd8ead92c2f622007847b6a26e6805a93c914db190ae30cb19ad</code>.
- [계산 642bb49e](#macro-record-b838a4610a8a8b372a7fb0ca1d8187422aab771e6878d4377aed17f85e9bff40): 직전 관측치 대비 변화; 상태: 사용 가능.
- 출력 series: USD\_KRW\_NOON\_REFERENCE\_\_previous\_change\_v1; 정확한 값: -12.9300 KRW\_per\_USD. stale 값은 과거 계산 기록이며 현재 요약에 채택하지 않는다.
- 방법: previous\_change\_v1; 공식: current\_value - exact\_reference\_value.
- 입력 series: USD\_KRW\_NOON\_REFERENCE; 입력 관측: [관측 ad06d0e9](#macro-record-872dd2891484f02921e8dc54b0100cc65b2cff0a512ecb33b5d75236ef03f9aa), [관측 891c0cc2](#macro-record-54dfa207ef2d41af4b7b1e6ff59137c447b588ee14b0fc1d32187e3d131b2d70).
- 관측창: 2026-09-24, 2026-09-25; 가정: Decimal precision 50; ROUND\_HALF\_EVEN / 결측 보간/forward-fill 없음.

<a id="macro-record-d502fede48ad9f5c1825bfe9fce567e9a84835ddf2ecfc53b3be83fd0fe8c8ba"></a>

- 계산 ID: <code>MET_de92c812251be2b93e249c06d7f0e3314e6e08de5efa61c9d3a2d97de313b793</code>.
- [계산 de92c812](#macro-record-d502fede48ad9f5c1825bfe9fce567e9a84835ddf2ecfc53b3be83fd0fe8c8ba): 직전 관측치 대비 변화; 상태: 사용 가능.
- 출력 series: US\_CPI\_U\_HEADLINE\_NSA\_\_previous\_change\_v1; 정확한 값: 1.062 index. stale 값은 과거 계산 기록이며 현재 요약에 채택하지 않는다.
- 방법: previous\_change\_v1; 공식: current\_value - exact\_reference\_value.
- 입력 series: US\_CPI\_U\_HEADLINE\_NSA; 입력 관측: [관측 b2d730c1](#macro-record-8117233cc5094a3f847def2167a8a467046f26d7cd47d2024f829950272c9b80), [관측 94cc77e8](#macro-record-065e317440d9ce1eca7955edb6860e53b4888e1f922d3057b399e810c9c708a9).
- 관측창: 2026-07-01, 2026-08-01; 가정: Decimal precision 50; ROUND\_HALF\_EVEN / 결측 보간/forward-fill 없음.

<a id="macro-record-7d669ad8f2af833c39930ecb0379b2a4436556accc728156be36f8f0378149b0"></a>

- 계산 ID: <code>MET_37d30e6a93539bf3b74289eda874281bf98c1cd0c4a6b1ea2bc09d892d974f48</code>.
- [계산 37d30e6a](#macro-record-7d669ad8f2af833c39930ecb0379b2a4436556accc728156be36f8f0378149b0): 직전 관측치 대비 변화; 상태: 사용 가능.
- 출력 series: US\_TREASURY\_NOMINAL\_10Y\_\_previous\_change\_v1; 정확한 값: -0.05 percentage\_points. stale 값은 과거 계산 기록이며 현재 요약에 채택하지 않는다.
- 방법: previous\_change\_v1; 공식: current\_value - exact\_reference\_value.
- 입력 series: US\_TREASURY\_NOMINAL\_10Y; 입력 관측: [관측 b1687d5d](#macro-record-6586511c485df564f15ba6c4426e8dc522a35e87ca71eeb5e2908b9909e5ce56), [관측 02f3966b](#macro-record-dec681c9d0d53e8079a1cd93ad2a9649a5140e606e75ce89acd701c144c31ed7).
- 관측창: 2026-09-30, 2026-10-01; 가정: Decimal precision 50; ROUND\_HALF\_EVEN / 결측 보간/forward-fill 없음.

<a id="macro-record-5c5cbb33b48d2dacdf7cccbcfb060bc567dfdc5f10a72bc87e0dc351ac6d16a0"></a>

- 계산 ID: <code>MET_93a6dd37e9846dae5dc933b39ca01954c2503d632fe123ccb281a357797c1fca</code>.
- [계산 93a6dd37](#macro-record-5c5cbb33b48d2dacdf7cccbcfb060bc567dfdc5f10a72bc87e0dc351ac6d16a0): 직전 관측치 대비 변화; 상태: 사용 가능.
- 출력 series: US\_TREASURY\_NOMINAL\_2Y\_\_previous\_change\_v1; 정확한 값: -0.10 percentage\_points. stale 값은 과거 계산 기록이며 현재 요약에 채택하지 않는다.
- 방법: previous\_change\_v1; 공식: current\_value - exact\_reference\_value.
- 입력 series: US\_TREASURY\_NOMINAL\_2Y; 입력 관측: [관측 01a92da2](#macro-record-1560076feaeffcc88d7784e86393d4997ccfdef35436445a232eaeb30923b1b6), [관측 a826e005](#macro-record-23dcf82b388a59a78123e8dbcab2fb66a5f90f0ba36b9285f9f3c517fcaa54b7).
- 관측창: 2026-09-30, 2026-10-01; 가정: Decimal precision 50; ROUND\_HALF\_EVEN / 결측 보간/forward-fill 없음.

<a id="macro-record-135c71a790e352208406355e02499f30c78dca15befd5d8253357eac1a49f4bd"></a>

- 계산 ID: <code>MET_f44a6c9d789de4ba28a43170d3419f85fe9c736766b9dd1bc5e384ab2fb0e8de</code>.
- [계산 f44a6c9d](#macro-record-135c71a790e352208406355e02499f30c78dca15befd5d8253357eac1a49f4bd): 전년 동월 대비 물가 상승률; 상태: 사용 가능.
- 출력 series: US\_CPI\_U\_HEADLINE\_NSA\_\_yoy\_v1; 정확한 값: 3.3965478924364767760574857396844210682272760945300 percent. stale 값은 과거 계산 기록이며 현재 요약에 채택하지 않는다.
- 방법: yoy\_v1; 공식: (index\_t / index\_t\_minus\_12\_months - 1) \* 100.
- 입력 series: US\_CPI\_U\_HEADLINE\_NSA; 입력 관측: [관측 238aa5ba](#macro-record-41b79b9cd60d17966ac516fb10dbfca749cde79768f61069bdc789c0c9b1d7ce), [관측 94cc77e8](#macro-record-065e317440d9ce1eca7955edb6860e53b4888e1f922d3057b399e810c9c708a9).
- 관측창: 2025-08-01, 2026-08-01; 가정: Decimal precision 50; ROUND\_HALF\_EVEN / 결측 보간/forward-fill 없음.
- 계산 진단: 중간 1개월 결측 보존; YoY는 정확한 두 endpoint만 사용.

<a id="macro-record-18c0be33598c43cb644eb828f5bee59ba058e6b1369e4eb73e226bf7eb61da97"></a>

- 계산 ID: <code>MET_860c19014e62d3d53c8ee72e4c5f4cc94a73a2fdfc083101b1de73aad5341ad9</code>.
- [계산 860c1901](#macro-record-18c0be33598c43cb644eb828f5bee59ba058e6b1369e4eb73e226bf7eb61da97): 전월 대비 물가 상승률 변화; 상태: 사용 가능.
- 출력 series: US\_CPI\_U\_HEADLINE\_NSA\_\_inflation\_trend\_v1; 정확한 값: 0.0317228509565728608498385788909786076641399661500 percentage\_points. stale 값은 과거 계산 기록이며 현재 요약에 채택하지 않는다.
- 방법: inflation\_trend\_v1; 공식: YoY\_t - YoY\_t\_minus\_1\_month.
- 입력 series: US\_CPI\_U\_HEADLINE\_NSA; 입력 관측: [관측 59659106](#macro-record-ee97e9613c57221cd8935ad3fa7d9637c5507fe89c1ffac16b33fa3ccd446ce4), [관측 238aa5ba](#macro-record-41b79b9cd60d17966ac516fb10dbfca749cde79768f61069bdc789c0c9b1d7ce), [관측 b2d730c1](#macro-record-8117233cc5094a3f847def2167a8a467046f26d7cd47d2024f829950272c9b80), [관측 94cc77e8](#macro-record-065e317440d9ce1eca7955edb6860e53b4888e1f922d3057b399e810c9c708a9).
- 관측창: 2025-07-01, 2025-08-01, 2026-07-01, 2026-08-01; 가정: Decimal precision 50; ROUND\_HALF\_EVEN / 결측 보간/forward-fill 없음.
- 계산 진단: 중간 1개월 결측 보존; YoY는 정확한 두 endpoint만 사용 / 중간 1개월 결측 보존; YoY는 정확한 두 endpoint만 사용.

<a id="macro-record-89d85ed99ca36f8a4e4b399a5fae60720bd1161987d00ee77a4ed9ad294499f9"></a>

- 계산 ID: <code>MET_ee685027ac36864c28386a350ab5c18c908707a626967e45415e3617830068ee</code>.
- [계산 ee685027](#macro-record-89d85ed99ca36f8a4e4b399a5fae60720bd1161987d00ee77a4ed9ad294499f9): 10년−2년 국채 수익률 차이; 상태: 사용 가능.
- 출력 series: US\_TREASURY\_NOMINAL\_10Y\_\_US\_TREASURY\_NOMINAL\_2Y\_\_yield\_spread\_v1; 정확한 값: 0.46 percentage\_points. stale 값은 과거 계산 기록이며 현재 요약에 채택하지 않는다.
- 방법: yield\_spread\_v1; 공식: yield\_10y\_t - yield\_2y\_t.
- 입력 series: US\_TREASURY\_NOMINAL\_10Y, US\_TREASURY\_NOMINAL\_2Y; 입력 관측: [관측 02f3966b](#macro-record-dec681c9d0d53e8079a1cd93ad2a9649a5140e606e75ce89acd701c144c31ed7), [관측 a826e005](#macro-record-23dcf82b388a59a78123e8dbcab2fb66a5f90f0ba36b9285f9f3c517fcaa54b7).
- 관측창: 2026-10-01; 가정: Decimal precision 50; ROUND\_HALF\_EVEN / 결측 보간/forward-fill 없음.

### 획득·연결 진단

- BLS\_CPI\_RELEASE: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- BLS\_CPI\_RELEASE: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- FED\_H15\_TREASURY: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- FED\_H10\_KRW: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- BLS M13 annual average excluded from monthly observations
- US\_CPI\_U\_HEADLINE\_NSA 2025-10-01: Data unavailable due to the 2025 lapse in appropriations
- BLS M13 annual average excluded from monthly observations
- US\_CPI\_U\_HEADLINE\_NSA: snapshot vintage is retrieval version; complete release/revision history unavailable
- US\_TREASURY\_NOMINAL\_2Y: snapshot vintage is retrieval version; complete release/revision history unavailable
- US\_TREASURY\_NOMINAL\_10Y: snapshot vintage is retrieval version; complete release/revision history unavailable
- USD\_KRW\_NOON\_REFERENCE: snapshot vintage is retrieval version; complete release/revision history unavailable
