# Macro Regime Snapshot · 공개 거시자료

## 기준 시점

- 정보 기준 시각: 2026-10-03T17:13:16.107675+00:00 (UTC).
- 한국 시각: 2026-10-04T02:13:16.107675+09:00 (Asia/Seoul). 두 표시는 같은 순간이다.
- 연구 질문: 확인 가능한 미국 물가·국채 금리와 KRW 환율은 각각 어떤 상태이며, 관측·공개·판본의 한계는 무엇인가?.
- 선택한 정의와 저장된 판본 중 이 기준 시각에 이용 가능한 관측만 사용한다. 관측일·발표일·획득일은 다르다.
- '현재'는 이 고정 기준 시각의 이용 가능한 자료를 뜻한다. 실시간 가격·전 시장·개인 투자 결론은 조사 범위에 없다.

## 한눈에 보기

미국 headline CPI의 전년 동월 대비 상승률은 3.397%다 ([계산 769f31b5](#macro-record-3a5c2c56ebfaf4b67ce343adec0344ec0a76ec9fc39fc92aa008e73356f1280b)).
전월의 전년 대비 상승률과 비교한 방향은 상승이며, 변화는 0.032%p다 ([계산 05aec7e2](#macro-record-51728f0098562db005d1e229401d75058dba5b9353a0dc46c8a89433f7dbfc92)).
같은 관측일의 미국 10년−2년 명목 국채 수익률 차이는 0.460%p다 ([계산 13a9f2e3](#macro-record-0b39aac06c43d9f603bf111f60e852404e416a592300cf80af4554b511459120)).
USD당 KRW 기준 환율은 직전 관측과 비교해 하락했다 ([계산 04040254](#macro-record-e3028ec39ddede367c6e5bff730c77561ac4e54a063f59eb73b23e38bd06d8c9)).
고용·정책금리·실질금리·성장·신용·유동성은 이번 자료에 없으므로 전체 경기 상태나 자산 매력을 확정하지 않는다.

## 금리

사용한 금리는 미국 국채의 **명목 시장 수익률**이다. 중앙은행 정책금리·예금 이자·확정 투자수익과 구분한다.

| 자료 | 기준 관측 | 값 | 채택 상태 |
| --- | --- | --- | --- |
| 미국 국채 10년 명목 시장금리 | 2026-10-01 | 5.240 % ([관측 07818a12](#macro-record-5ea22e484d99243f2bb8980ada756a7d00bce7b1b4889faa97d70aea979fa23f)) | 사용 가능 |
| 미국 국채 2년 명목 시장금리 | 2026-10-01 | 4.780 % ([관측 c91d38cf](#macro-record-c3102ca23240ec811e5b5ff6760356c8ed7b4238555d745fa8db8fec64fc2998)) | 사용 가능 |

- [계산 결과] 미국 국채 10년 명목 시장금리 · 직전 관측치 대비 변화: -0.050 %p; 두 비교값 사이의 방향: 하락; 비교 관측일: 2026-09-30, 2026-10-01 ([계산 768f2bc2](#macro-record-6d01b956d92102ca356b986effa5395dda1693649d738fafc909e11f75341d67)).
- [계산 결과] 미국 국채 2년 명목 시장금리 · 직전 관측치 대비 변화: -0.100 %p; 두 비교값 사이의 방향: 하락; 비교 관측일: 2026-09-30, 2026-10-01 ([계산 6a59bef3](#macro-record-cdce7c6c47f560e7367bbb54adcbd0715d6422a84a2b954ae40e216f385614d5)).
- [계산 결과] 미국 국채 10년 명목 시장금리 / 미국 국채 2년 명목 시장금리 · 10년−2년 국채 수익률 차이: 0.460 %p; 비교 관측일: 2026-10-01 ([계산 13a9f2e3](#macro-record-0b39aac06c43d9f603bf111f60e852404e416a592300cf80af4554b511459120)).

직전 관측 비교는 두 날짜 사이의 변화다. 지속적인 추세나 '역사적으로 높은 금리'를 판정하는 규칙은 구현하지 않았다.

## 물가

미국 도시 소비자 headline CPI의 **계절조정하지 않은 지수**를 사용한다. Core CPI나 계절조정 전월비와 합치지 않는다.

| 자료 | 기준 관측 | 값 | 채택 상태 |
| --- | --- | --- | --- |
| 미국 headline CPI-U 원지수 (NSA) | 2026-08-01 | 334.980 지수 ([관측 01745871](#macro-record-95bedb1a82c5878057b021e4a5c4f230fef156a43501a4a876ebc05790043af8)) | 사용 가능 |

- [계산 결과] 미국 headline CPI-U 원지수 (NSA) · 직전 관측치 대비 변화: 1.062 지수; 두 비교값 사이의 방향: 상승; 비교 관측일: 2026-07-01, 2026-08-01 ([계산 b43d70df](#macro-record-1536f12dcd26180a892498c874de5c8c205a6632e679892209dc825ec0e1d7be)).
- [계산 결과] 미국 headline CPI-U 원지수 (NSA) · 전년 동월 대비 물가 상승률: 3.397 %; 비교 관측일: 2025-08-01, 2026-08-01 ([계산 769f31b5](#macro-record-3a5c2c56ebfaf4b67ce343adec0344ec0a76ec9fc39fc92aa008e73356f1280b)).
- [계산 결과] 미국 headline CPI-U 원지수 (NSA) · 전월 대비 물가 상승률 변화: 0.032 %p; 두 비교값 사이의 방향: 상승; 비교 관측일: 2025-07-01, 2025-08-01, 2026-07-01, 2026-08-01 ([계산 05aec7e2](#macro-record-51728f0098562db005d1e229401d75058dba5b9353a0dc46c8a89433f7dbfc92)).

지수의 직전 관측 변화는 물가 수준의 변화이며 물가 상승률의 방향과 다르다. 상승률 방향은 현재 YoY와 정확한 전월 YoY의 차이로만 표시한다.
계절조정하지 않은 지수의 전월 변화에는 계절성이 포함될 수 있다. 상승률 하락은 가격 자체의 하락을 뜻하지 않는다.

## 경기 / 고용

이번 작은 자료 집합에는 고용·실업·생산·성장 지표가 없다. 경기 둔화·침체나 고용 강약을 대신 추론하지 않았다.

## 환율 / 한국 투자자 관점

USD/KRW는 **USD당 KRW**다. 뉴욕 정오 기준 환율 관측을 쓰며 국내 체결 환율·실시간 호가·환전 비용과 구분한다.

| 자료 | 기준 관측 | 값 | 채택 상태 |
| --- | --- | --- | --- |
| 원/달러 뉴욕 정오 기준환율 | 2026-09-25 | 1356.510 원/USD ([관측 8424e011](#macro-record-e6264ddceb2cd14486287b063dcbdb336ef7605dc926a651e0e5aa56583b899e)) | 사용 가능 |

- [계산 결과] 원/달러 뉴욕 정오 기준환율 · 직전 관측치 대비 변화: -12.930 원/USD; 두 비교값 사이의 방향: 하락; 비교 관측일: 2026-09-24, 2026-09-25 ([계산 04040254](#macro-record-e3028ec39ddede367c6e5bff730c77561ac4e54a063f59eb73b23e38bd06d8c9)).

[정의에 따른 해석] 같은 USD를 원화로 표시할 때 금액이 작아졌다는 뜻이며, 이 관측 사이에서는 원화 강세에 해당한다. ([계산 04040254](#macro-record-e3028ec39ddede367c6e5bff730c77561ac4e54a063f59eb73b23e38bd06d8c9)).

미국 자산 자체의 USD 시장환경과 한국 투자자의 KRW 평가환경은 별도다. 자산 가격·배당·환헤지·비용·세금 자료 없이 개인의 KRW 수익률을 계산하지 않았다.

## 서로 상충하는 신호

[관측·계산] 전년 대비 물가 상승률의 전월 비교는 상승, 10년 시장금리의 직전 관측 비교는 하락이다 ([계산 05aec7e2](#macro-record-51728f0098562db005d1e229401d75058dba5b9353a0dc46c8a89433f7dbfc92), [계산 768f2bc2](#macro-record-6d01b956d92102ca356b986effa5395dda1693649d738fafc909e11f75341d67)).
[해석 후보] 방향이 같지 않아 '물가 변화가 금리 변화를 전부 설명한다'는 단순한 설명만으로 읽기 어렵다. 성장 기대·기간 프리미엄 등 다른 설명을 검토해야 하지만 이번 자료는 원인을 확인하지 않는다.
물가 비교는 월별, 금리 비교는 일별이며 서로 다른 관측창이다. 같은 사건에 대한 통계적 모순으로 판정하지 않는다.

## 투자환경에 어떤 의미가 있을 수 있는가

아래는 **조건부 전파 경로·검토 전 해석 후보**다. 위 관측 사실·계산 결과와 구분하며, 경제적 관계의 실증 검증이나 투자 규칙으로 확정하지 않는다.

- **금리 → 채권·기업 가치:** 다른 조건이 같고 현금흐름이 고정되어 있다면 할인율 변화는 현재가치에 영향을 줄 수 있다. 입력 사실: [관측 07818a12](#macro-record-5ea22e484d99243f2bb8980ada756a7d00bce7b1b4889faa97d70aea979fa23f), [관측 c91d38cf](#macro-record-c3102ca23240ec811e5b5ff6760356c8ed7b4238555d745fa8db8fec64fc2998). 실제 영향에는 만기·듀레이션·신용·이익 전망이 필요하며 여기서는 계산하지 않았다.
- **물가 → 현금·채권의 구매력:** 명목 이자와 같은 기간의 실제 물가 변화가 필요하다. 입력 사실: [계산 769f31b5](#macro-record-3a5c2c56ebfaf4b67ce343adec0344ec0a76ec9fc39fc92aa008e73356f1280b). 현재 YoY를 미래 물가나 특정 자산의 실질수익으로 바꾸지 않았다.
- **환율 → 해외자산의 KRW 표시 가치:** 같은 USD 가치와 환노출을 유지한다는 조건에서 환율은 원화 평가에 영향을 줄 수 있다. 입력 사실: [계산 04040254](#macro-record-e3028ec39ddede367c6e5bff730c77561ac4e54a063f59eb73b23e38bd06d8c9). 실제 상품·환헤지·평가 시점과 사용자 보유 내역은 미확인이다.

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

- 연구 ID: CURRENT\_OFFICIAL\_MACRO; 입력 SHA-256: 4e90c9faedbca21286af05c5257b44c2c3f0ffb6712f2efab0be53ef68f1648b.
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
- 마지막 선택 관측: 2026-09-25; 공개: unknown · 미확인; 획득: 2026-10-03T17:13:16.104545+00:00; vintage: 2026-10-03T17:13:16.104545+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:13:16.104545+00:00; valid-as-of: unknown · 미확인.
- 마지막 관측의 snapshot: e6024ea571d2a6c5b6cd6ed43e1ca06a25673b8ccb4051ed3fdb284d32f9ca0f; vintage ID: retrieved\_snapshot:e6024ea571d2a6c5b6cd6ed43e1ca06a25673b8ccb4051ed3fdb284d32f9ca0f.
- 선택 진단의 요약: OBS\_7fbd2dbc8c42ffd6fd71548a6a0a62d4c0d853b78e49d2512fd3fae3ceda1e18: 공개 시각 unknown: 획득 시각을 보수적인 이용 가능 시점으로 사용 / OBS\_8424e0112254d8ba4e20949656543c4204966432b76a785076aa0670fe697a28: 공개 시각 unknown: 획득 시각을 보수적인 이용 가능 시점으로 사용.

#### 미국 headline CPI-U 원지수 (NSA)

- canonical ID: US\_CPI\_U\_HEADLINE\_NSA; 정의 SHA-256: 799a3bb2c4ca2bcd89845bf817ae9df864228a7b3e588777b67727ba731e3705.
- 정의: All items CPI-U, U.S. city average, 1982–84=100; not seasonally adjusted. Monthly label is the reference month, not the release date..
- 단위: index; 빈도: monthly; 계절조정: not\_seasonally\_adjusted; 통화: 해당 없음; 변환: raw.
- 발행 주체: U.S. Bureau of Labor Statistics; 관할: US; 출처: [BLS\_CPI\_API](#macro-record-c436613f5d09e28fd85e2bc46b272d6421f81f0e3f63f160bcbb83e83676c4ce).
- 발표 특성: Monthly, typically released in the following month; date varies. Current release is cross-checked against retained official excerpts.; 개정 특성: Full release/revision history absent from v1 API. Current fetched version is not a historical first release; missing October 2025 remains explicit..
- 선택 상태: 사용 가능; 전체 판본 32개, 시점 조건 뒤 선택한 기간 32개, 이후 정보로 제외한 판본 0개.
- 신선도 규칙: 기준 시점의 날짜와 마지막 관측일의 차이가 75일을 초과하면 stale.
- 마지막 선택 관측: 2026-08-01; 공개: 2026-09-11T12:30:00+00:00; 획득: 2026-10-03T17:13:14.741705+00:00; vintage: 2026-10-03T17:13:14.741705+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:13:14.741705+00:00; valid-as-of: unknown · 미확인.
- 마지막 관측의 snapshot: 5f659b87469da318e1d476987fb1d686bdf23f34cae1194297a4996299564a05; vintage ID: retrieved\_snapshot:5f659b87469da318e1d476987fb1d686bdf23f34cae1194297a4996299564a05.
- 선택 진단의 요약: OBS\_583ddee47c9a3afc0501623d75490a260638c64ca8cfb9b45f1591c800c4f881: 공개 시각 unknown: 획득 시각을 보수적인 이용 가능 시점으로 사용 / OBS\_747b853a1e65c409c35cdf5a1718c237c2c26eaeb10667e60bd7ebf0058ce20e: 공개 시각 unknown: 획득 시각을 보수적인 이용 가능 시점으로 사용.

#### 미국 국채 10년 명목 시장금리

- canonical ID: US\_TREASURY\_NOMINAL\_10Y; 정의 SHA-256: b7a6bce81ddb6d782c1a5e9fead7c0676e396603d4353da3f603992b650eb1c5.
- 정의: 10-year constant-maturity Treasury yield, quoted on investment basis, annual percent; not policy rate, real yield or realized bond return. CSV Currency NA means no currency amount; underlying Treasury exposure is USD..
- 단위: percent; 빈도: daily; 계절조정: not\_seasonally\_adjusted; 통화: USD; 변환: raw.
- 발행 주체: Board of Governors of the Federal Reserve System; 관할: US; 출처: [FED\_H15\_TREASURY](#macro-record-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700).
- 발표 특성: U.S. business-day observation; publication lag and weekends differ from observation date.; 개정 특성: Current H.15 CSV may include corrections; complete first-release/vintage history unavailable..
- 선택 상태: 사용 가능; 전체 판본 262개, 시점 조건 뒤 선택한 기간 262개, 이후 정보로 제외한 판본 0개.
- 신선도 규칙: 기준 시점의 날짜와 마지막 관측일의 차이가 10일을 초과하면 stale.
- 마지막 선택 관측: 2026-10-01; 공개: unknown · 미확인; 획득: 2026-10-03T17:13:15.483675+00:00; vintage: 2026-10-03T17:13:15.483675+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:13:15.483675+00:00; valid-as-of: unknown · 미확인.
- 마지막 관측의 snapshot: 79a230cc8bff4d412dd2e177ce59c8d2f218131dd37a72bf1cda3324e78f6c9b; vintage ID: retrieved\_snapshot:79a230cc8bff4d412dd2e177ce59c8d2f218131dd37a72bf1cda3324e78f6c9b.
- 선택 진단의 요약: OBS\_d5795e9fafd8d3fe02729bd70c263d8c56c00c609e11bb9748c11b5c7c5a30b2: 공개 시각 unknown: 획득 시각을 보수적인 이용 가능 시점으로 사용 / OBS\_07818a1242169b952349e54e0651560e013d9c511c3728a9955db7bd85184067: 공개 시각 unknown: 획득 시각을 보수적인 이용 가능 시점으로 사용.

#### 미국 국채 2년 명목 시장금리

- canonical ID: US\_TREASURY\_NOMINAL\_2Y; 정의 SHA-256: 4702cfbc58c13aa906b2af823595ae9d8e477e414e5fccad50e093887cffe061.
- 정의: 2-year constant-maturity Treasury yield, quoted on investment basis, annual percent; not policy rate, real yield or realized bond return. CSV Currency NA means no currency amount; underlying Treasury exposure is USD..
- 단위: percent; 빈도: daily; 계절조정: not\_seasonally\_adjusted; 통화: USD; 변환: raw.
- 발행 주체: Board of Governors of the Federal Reserve System; 관할: US; 출처: [FED\_H15\_TREASURY](#macro-record-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700).
- 발표 특성: U.S. business-day observation; publication lag and weekends differ from observation date.; 개정 특성: Current H.15 CSV may include corrections; complete first-release/vintage history unavailable..
- 선택 상태: 사용 가능; 전체 판본 262개, 시점 조건 뒤 선택한 기간 262개, 이후 정보로 제외한 판본 0개.
- 신선도 규칙: 기준 시점의 날짜와 마지막 관측일의 차이가 10일을 초과하면 stale.
- 마지막 선택 관측: 2026-10-01; 공개: unknown · 미확인; 획득: 2026-10-03T17:13:15.483675+00:00; vintage: 2026-10-03T17:13:15.483675+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:13:15.483675+00:00; valid-as-of: unknown · 미확인.
- 마지막 관측의 snapshot: 79a230cc8bff4d412dd2e177ce59c8d2f218131dd37a72bf1cda3324e78f6c9b; vintage ID: retrieved\_snapshot:79a230cc8bff4d412dd2e177ce59c8d2f218131dd37a72bf1cda3324e78f6c9b.
- 선택 진단의 요약: OBS\_4f71fa1977631869c63acd1e8d101a03ef2dfefbeb88d03404e245eceb623042: 공개 시각 unknown: 획득 시각을 보수적인 이용 가능 시점으로 사용 / OBS\_c91d38cfb196adeed9e7d1132bdb9dbd777e11a48a5a0b94764f58fc4c6d6cdb: 공개 시각 unknown: 획득 시각을 보수적인 이용 가능 시점으로 사용.

### 고정 출처와 snapshot

<a id="macro-record-7b5bff1cb9bb41923e363e62038c607890f6074f6332453191a0e9cedcdf8927"></a>

- Consumer Price Index — August 2026 release; 출처 ID: BLS\_CPI\_RELEASE; 위치: https://www.bls.gov/news.release/cpi.htm.
- 사용한 고정 snapshot: 2453dd6520e8899086a09329e0e73b013935feed8091429efd5dec9dbfece26b.
- source-level metadata의 판본: 2453dd6520e8899086a09329e0e73b013935feed8091429efd5dec9dbfece26b; 획득: 2026-10-03T17:13:13.854529Z; 각 관측의 정확한 판본은 아래 evidence의 snapshot을 따른다.
- 접근: public\_http; 보존: excerpt; 상태: available.
- 정책: https://www.bls.gov/bls/linksite.htm; 검토: Official BLS public-domain release; preserve only three verification excerpts with attribution. Separate API terms apply to API data..
- 원문 SHA-256: f19802d4f56fbe007d78f6aa14a075c7899077705c5d503d61230c498640088c; 정규화 SHA-256: dc72b00e0269c97851e24e9967283ae96994b51a61a71aff7e21394368c72ff0; payload SHA-256: 3f7e347e2146b1e483a63b9df2f50561206b6fa577e23c9d5a534557bf546d50.
- 이 BLS 자료의 실제 획득 시각: 2026-10-03T17:13:13.854529Z.
- BLS 이용 안내 · 획득 이후 분석에 대한 보증 없음: BLS.gov cannot vouch for the data or analyses derived from these data after the data have been retrieved from BLS.gov.

<a id="macro-record-c436613f5d09e28fd85e2bc46b272d6421f81f0e3f63f160bcbb83e83676c4ce"></a>

- BLS CPI-U all items, U.S. city average, not seasonally adjusted; 출처 ID: BLS\_CPI\_API; 위치: https://api.bls.gov/publicAPI/v1/timeseries/data/CUUR0000SA0.
- 사용한 고정 snapshot: 5f659b87469da318e1d476987fb1d686bdf23f34cae1194297a4996299564a05.
- source-level metadata의 판본: 5f659b87469da318e1d476987fb1d686bdf23f34cae1194297a4996299564a05; 획득: 2026-10-03T17:13:14.741705Z; 각 관측의 정확한 판본은 아래 evidence의 snapshot을 따른다.
- 접근: public\_api; 보존: full; 상태: available.
- 정책: https://www.bls.gov/developers/termsOfService.htm; 검토: Documented unregistered v1 GET API: https://www.bls.gov/developers/api\_signature.htm . Public-domain data: https://www.bls.gov/bls/linksite.htm . Cite access/retrieval date. BLS.gov cannot vouch for the data or analyses derived from these data after the data have been retrieved from BLS.gov..
- 원문 SHA-256: 30f5c440fc95fbedc214daf7ffde7e6ece451b0f30473a6309e0235938170b03; 정규화 SHA-256: 41ee32f201a98381573ce9c8822d0c90b3003a3e44445d071db08d715587e530; payload SHA-256: 96cb8805cc869a9ca8500a0b01c79b84d21e1b3ecd52b92143c9eae964f89f1c.
- 이 BLS 자료의 실제 획득 시각: 2026-10-03T17:13:14.741705Z.
- BLS 이용 안내 · 획득 이후 분석에 대한 보증 없음: BLS.gov cannot vouch for the data or analyses derived from these data after the data have been retrieved from BLS.gov.

<a id="macro-record-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700"></a>

- H.15 Treasury constant-maturity nominal yield CSV; 출처 ID: FED\_H15\_TREASURY; 위치: https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&amp;series=bf17364827e38702b42a58cf8eaa3f78&amp;lastobs=&amp;from=&amp;to=&amp;filetype=csv&amp;label=include&amp;layout=seriescolumn&amp;type=package.
- 사용한 고정 snapshot: 79a230cc8bff4d412dd2e177ce59c8d2f218131dd37a72bf1cda3324e78f6c9b.
- source-level metadata의 판본: 79a230cc8bff4d412dd2e177ce59c8d2f218131dd37a72bf1cda3324e78f6c9b; 획득: 2026-10-03T17:13:15.483675Z; 각 관측의 정확한 판본은 아래 evidence의 snapshot을 따른다.
- 접근: public\_http; 보존: full; 상태: available.
- 정책: https://www.federalreserve.gov/disclaimer.htm; 검토: The Federal Reserve Board permits reuse of public-domain information with Board attribution; no seals, logos or third-party content are fetched..
- 원문 SHA-256: a72bc770cb6c4f269931eb4014d7dfe4f9624dd948649d765fefdaf4f718fd7c; 정규화 SHA-256: 7fc1b00a97692140da18af34f07c863d5e87102056dd24429397d5902088892b; payload SHA-256: 2816fe45201beabe3da0c4732dc3bad68a1c7b418057264de84e145ffe2935c2.

<a id="macro-record-f56e2932df7c7cf95311e4e66639477af2df08d54da6d6f81da7d23af5c880f1"></a>

- H.10 South Korean won per U.S. dollar daily reference rate CSV; 출처 ID: FED\_H10\_KRW; 위치: https://www.federalreserve.gov/datadownload/Output.aspx?rel=H10&amp;series=60f32914ab61dfab590e0e470153e3ae&amp;lastobs=250&amp;from=&amp;to=&amp;filetype=csv&amp;label=include&amp;layout=seriescolumn&amp;type=package.
- 사용한 고정 snapshot: e6024ea571d2a6c5b6cd6ed43e1ca06a25673b8ccb4051ed3fdb284d32f9ca0f.
- source-level metadata의 판본: e6024ea571d2a6c5b6cd6ed43e1ca06a25673b8ccb4051ed3fdb284d32f9ca0f; 획득: 2026-10-03T17:13:16.104545Z; 각 관측의 정확한 판본은 아래 evidence의 snapshot을 따른다.
- 접근: public\_http; 보존: full; 상태: available.
- 정책: https://www.federalreserve.gov/disclaimer.htm; 검토: The Federal Reserve Board permits reuse of public-domain information with Board attribution; no seals, logos or third-party content are fetched. Definition: https://www.federalreserve.gov/releases/h10/about.htm . Noon New York buying rate; daily observations released weekly; current country CSV can include later corrections..
- 원문 SHA-256: d15be650c4a2484ddd9c09dc63f2ff70386b0e57ecde3da70f0106d194007eed; 정규화 SHA-256: a6df24ddc46749152062d97001a2dac7cd897203e57f2fc8ff2f36ad0e256353; payload SHA-256: f30d02b572c8722d2c9e5645130190f2da29bcbdcd83c97897225de4045f0802.

### 본문과 계산이 참조한 원관측 / 기존 EvidenceRecord

<a id="macro-record-95bedb1a82c5878057b021e4a5c4f230fef156a43501a4a876ebc05790043af8"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_017458714f6243fb8b2424d5e72a290376fdc617f3a1d7b1565c487a6673e884</code>.
- [관측 01745871](#macro-record-95bedb1a82c5878057b021e4a5c4f230fef156a43501a4a876ebc05790043af8): US\_CPI\_U\_HEADLINE\_NSA; 관측일: 2026-08-01; 원자료 값: 334.980 index.
- 출처: [BLS\_CPI\_API](#macro-record-c436613f5d09e28fd85e2bc46b272d6421f81f0e3f63f160bcbb83e83676c4ce); snapshot: 5f659b87469da318e1d476987fb1d686bdf23f34cae1194297a4996299564a05; 원문 위치: /Results/series/0/data/0/value; year=2026, period=M08.
- 공개: 2026-09-11T12:30:00+00:00; 획득: 2026-10-03T17:13:14.741705+00:00; vintage: 2026-10-03T17:13:14.741705+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:13:14.741705+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: fresh. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

- 공개 시각의 확인 자료: [BLS\_CPI\_RELEASE](#macro-record-7b5bff1cb9bb41923e363e62038c607890f6074f6332453191a0e9cedcdf8927); snapshot: 2453dd6520e8899086a09329e0e73b013935feed8091429efd5dec9dbfece26b; 원문 구절 ID: RELEASE\_TIME, CPI\_PERIOD, CPI\_VALUE; 방법: bls\_release\_crosscheck\_v1. 관측 기간·지수·발표 시각의 좁은 대조이며 사후 투자 해석의 보증이 아니다.

<a id="macro-record-5ea22e484d99243f2bb8980ada756a7d00bce7b1b4889faa97d70aea979fa23f"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_07818a1242169b952349e54e0651560e013d9c511c3728a9955db7bd85184067</code>.
- [관측 07818a12](#macro-record-5ea22e484d99243f2bb8980ada756a7d00bce7b1b4889faa97d70aea979fa23f): US\_TREASURY\_NOMINAL\_10Y; 관측일: 2026-10-01; 원자료 값: 5.24 percent.
- 출처: [FED\_H15\_TREASURY](#macro-record-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700); snapshot: 79a230cc8bff4d412dd2e177ce59c8d2f218131dd37a72bf1cda3324e78f6c9b; 원문 위치: CSV row 16899, column RIFLGFCY10\_N.B, Time Period=2026-10-01.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:13:15.483675+00:00; vintage: 2026-10-03T17:13:15.483675+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:13:15.483675+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: fresh. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

<a id="macro-record-72378b2cfe6e2c4037026eae05cebe253852fd77054ab86d9263137b0d9d2b94"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_2306367a60353ffcf26f8e9500b2fb35e06053edca8be83b487a786171ed5e14</code>.
- [관측 2306367a](#macro-record-72378b2cfe6e2c4037026eae05cebe253852fd77054ab86d9263137b0d9d2b94): US\_CPI\_U\_HEADLINE\_NSA; 관측일: 2025-07-01; 원자료 값: 323.048 index.
- 출처: [BLS\_CPI\_API](#macro-record-c436613f5d09e28fd85e2bc46b272d6421f81f0e3f63f160bcbb83e83676c4ce); snapshot: 5f659b87469da318e1d476987fb1d686bdf23f34cae1194297a4996299564a05; 원문 위치: /Results/series/0/data/14/value; year=2025, period=M07.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:13:14.741705+00:00; vintage: 2026-10-03T17:13:14.741705+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:13:14.741705+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: stale. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

<a id="macro-record-5a1bbe31a9d75c92a98131627c8ff42ab446c1975e586ce9f3c3dcde13fae4ee"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_4f71fa1977631869c63acd1e8d101a03ef2dfefbeb88d03404e245eceb623042</code>.
- [관측 4f71fa19](#macro-record-5a1bbe31a9d75c92a98131627c8ff42ab446c1975e586ce9f3c3dcde13fae4ee): US\_TREASURY\_NOMINAL\_2Y; 관측일: 2026-09-30; 원자료 값: 4.88 percent.
- 출처: [FED\_H15\_TREASURY](#macro-record-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700); snapshot: 79a230cc8bff4d412dd2e177ce59c8d2f218131dd37a72bf1cda3324e78f6c9b; 원문 위치: CSV row 16898, column RIFLGFCY02\_N.B, Time Period=2026-09-30.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:13:15.483675+00:00; vintage: 2026-10-03T17:13:15.483675+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:13:15.483675+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: fresh. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

<a id="macro-record-9a80737d20585ec1269bc790495de0fed65545075370ea8c3521ca28c4b278b2"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_747b853a1e65c409c35cdf5a1718c237c2c26eaeb10667e60bd7ebf0058ce20e</code>.
- [관측 747b853a](#macro-record-9a80737d20585ec1269bc790495de0fed65545075370ea8c3521ca28c4b278b2): US\_CPI\_U\_HEADLINE\_NSA; 관측일: 2026-07-01; 원자료 값: 333.918 index.
- 출처: [BLS\_CPI\_API](#macro-record-c436613f5d09e28fd85e2bc46b272d6421f81f0e3f63f160bcbb83e83676c4ce); snapshot: 5f659b87469da318e1d476987fb1d686bdf23f34cae1194297a4996299564a05; 원문 위치: /Results/series/0/data/1/value; year=2026, period=M07.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:13:14.741705+00:00; vintage: 2026-10-03T17:13:14.741705+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:13:14.741705+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: stale. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

<a id="macro-record-d0e7fa100a289ad973f2cb6a8f55eb7f3fe3589b84a75556fe877920dc8cbc59"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_7e4d1757c139da8cbec498d40b56467bb2c1803f22083e004b0df0ce9cd6d490</code>.
- [관측 7e4d1757](#macro-record-d0e7fa100a289ad973f2cb6a8f55eb7f3fe3589b84a75556fe877920dc8cbc59): US\_CPI\_U\_HEADLINE\_NSA; 관측일: 2025-08-01; 원자료 값: 323.976 index.
- 출처: [BLS\_CPI\_API](#macro-record-c436613f5d09e28fd85e2bc46b272d6421f81f0e3f63f160bcbb83e83676c4ce); snapshot: 5f659b87469da318e1d476987fb1d686bdf23f34cae1194297a4996299564a05; 원문 위치: /Results/series/0/data/13/value; year=2025, period=M08.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:13:14.741705+00:00; vintage: 2026-10-03T17:13:14.741705+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:13:14.741705+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: stale. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

<a id="macro-record-040564f07f2b2b9912608053978be8aa818f3a19cf7833eb70b68274559bef9a"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_7fbd2dbc8c42ffd6fd71548a6a0a62d4c0d853b78e49d2512fd3fae3ceda1e18</code>.
- [관측 7fbd2dbc](#macro-record-040564f07f2b2b9912608053978be8aa818f3a19cf7833eb70b68274559bef9a): USD\_KRW\_NOON\_REFERENCE; 관측일: 2026-09-24; 원자료 값: 1369.4400 KRW\_per\_USD.
- 출처: [FED\_H10\_KRW](#macro-record-f56e2932df7c7cf95311e4e66639477af2df08d54da6d6f81da7d23af5c880f1); snapshot: e6024ea571d2a6c5b6cd6ed43e1ca06a25673b8ccb4051ed3fdb284d32f9ca0f; 원문 위치: CSV row 255, column RXI\_N.B.KO, Time Period=2026-09-24.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:13:16.104545+00:00; vintage: 2026-10-03T17:13:16.104545+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:13:16.104545+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: fresh. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

<a id="macro-record-e6264ddceb2cd14486287b063dcbdb336ef7605dc926a651e0e5aa56583b899e"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_8424e0112254d8ba4e20949656543c4204966432b76a785076aa0670fe697a28</code>.
- [관측 8424e011](#macro-record-e6264ddceb2cd14486287b063dcbdb336ef7605dc926a651e0e5aa56583b899e): USD\_KRW\_NOON\_REFERENCE; 관측일: 2026-09-25; 원자료 값: 1356.5100 KRW\_per\_USD.
- 출처: [FED\_H10\_KRW](#macro-record-f56e2932df7c7cf95311e4e66639477af2df08d54da6d6f81da7d23af5c880f1); snapshot: e6024ea571d2a6c5b6cd6ed43e1ca06a25673b8ccb4051ed3fdb284d32f9ca0f; 원문 위치: CSV row 256, column RXI\_N.B.KO, Time Period=2026-09-25.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:13:16.104545+00:00; vintage: 2026-10-03T17:13:16.104545+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:13:16.104545+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: fresh. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

<a id="macro-record-c3102ca23240ec811e5b5ff6760356c8ed7b4238555d745fa8db8fec64fc2998"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_c91d38cfb196adeed9e7d1132bdb9dbd777e11a48a5a0b94764f58fc4c6d6cdb</code>.
- [관측 c91d38cf](#macro-record-c3102ca23240ec811e5b5ff6760356c8ed7b4238555d745fa8db8fec64fc2998): US\_TREASURY\_NOMINAL\_2Y; 관측일: 2026-10-01; 원자료 값: 4.78 percent.
- 출처: [FED\_H15\_TREASURY](#macro-record-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700); snapshot: 79a230cc8bff4d412dd2e177ce59c8d2f218131dd37a72bf1cda3324e78f6c9b; 원문 위치: CSV row 16899, column RIFLGFCY02\_N.B, Time Period=2026-10-01.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:13:15.483675+00:00; vintage: 2026-10-03T17:13:15.483675+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:13:15.483675+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: fresh. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

<a id="macro-record-620a418a6a6a4261843c24ff2333f800efb7980ab22c9104b60985e7cf50d542"></a>

- 기존 EvidenceRecord / 관측 ID: <code>OBS_d5795e9fafd8d3fe02729bd70c263d8c56c00c609e11bb9748c11b5c7c5a30b2</code>.
- [관측 d5795e9f](#macro-record-620a418a6a6a4261843c24ff2333f800efb7980ab22c9104b60985e7cf50d542): US\_TREASURY\_NOMINAL\_10Y; 관측일: 2026-09-30; 원자료 값: 5.29 percent.
- 출처: [FED\_H15\_TREASURY](#macro-record-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700); snapshot: 79a230cc8bff4d412dd2e177ce59c8d2f218131dd37a72bf1cda3324e78f6c9b; 원문 위치: CSV row 16898, column RIFLGFCY10\_N.B, Time Period=2026-09-30.
- 공개: unknown · 미확인; 획득: 2026-10-03T17:13:15.483675+00:00; vintage: 2026-10-03T17:13:15.483675+00:00; revision: unknown · 미확인; known-at: 2026-10-03T17:13:15.483675+00:00; valid-as-of: unknown · 미확인.
- 기존 근거의 확인 범위: supported\_within\_scope; 해석 검토: reviewed; freshness: fresh. 현재 자료 채택 가능성과 과거 구절/관측의 확인은 별도다.

### 결정적 계산 · 채택 가능한 값만 기존 MetricResult

<a id="macro-record-e3028ec39ddede367c6e5bff730c77561ac4e54a063f59eb73b23e38bd06d8c9"></a>

- 계산 ID: <code>MET_04040254d340aa85ae9f6ac0b28a6cce2437c496e0ab15cf4d3538f4679da752</code>.
- [계산 04040254](#macro-record-e3028ec39ddede367c6e5bff730c77561ac4e54a063f59eb73b23e38bd06d8c9): 직전 관측치 대비 변화; 상태: 사용 가능.
- 출력 series: USD\_KRW\_NOON\_REFERENCE\_\_previous\_change\_v1; 정확한 값: -12.9300 KRW\_per\_USD. stale 값은 과거 계산 기록이며 현재 요약에 채택하지 않는다.
- 방법: previous\_change\_v1; 공식: current\_value - exact\_reference\_value.
- 입력 series: USD\_KRW\_NOON\_REFERENCE; 입력 관측: [관측 7fbd2dbc](#macro-record-040564f07f2b2b9912608053978be8aa818f3a19cf7833eb70b68274559bef9a), [관측 8424e011](#macro-record-e6264ddceb2cd14486287b063dcbdb336ef7605dc926a651e0e5aa56583b899e).
- 관측창: 2026-09-24, 2026-09-25; 가정: Decimal precision 50; ROUND\_HALF\_EVEN / 결측 보간/forward-fill 없음.

<a id="macro-record-1536f12dcd26180a892498c874de5c8c205a6632e679892209dc825ec0e1d7be"></a>

- 계산 ID: <code>MET_b43d70df3e98a16f330b0d300b37e6a6d2cc782fd458037cb43892030c9383fa</code>.
- [계산 b43d70df](#macro-record-1536f12dcd26180a892498c874de5c8c205a6632e679892209dc825ec0e1d7be): 직전 관측치 대비 변화; 상태: 사용 가능.
- 출력 series: US\_CPI\_U\_HEADLINE\_NSA\_\_previous\_change\_v1; 정확한 값: 1.062 index. stale 값은 과거 계산 기록이며 현재 요약에 채택하지 않는다.
- 방법: previous\_change\_v1; 공식: current\_value - exact\_reference\_value.
- 입력 series: US\_CPI\_U\_HEADLINE\_NSA; 입력 관측: [관측 747b853a](#macro-record-9a80737d20585ec1269bc790495de0fed65545075370ea8c3521ca28c4b278b2), [관측 01745871](#macro-record-95bedb1a82c5878057b021e4a5c4f230fef156a43501a4a876ebc05790043af8).
- 관측창: 2026-07-01, 2026-08-01; 가정: Decimal precision 50; ROUND\_HALF\_EVEN / 결측 보간/forward-fill 없음.

<a id="macro-record-6d01b956d92102ca356b986effa5395dda1693649d738fafc909e11f75341d67"></a>

- 계산 ID: <code>MET_768f2bc22f4db2cc5399d2808d383afd98b7903863d8ecfdb5b876856b9dd5d8</code>.
- [계산 768f2bc2](#macro-record-6d01b956d92102ca356b986effa5395dda1693649d738fafc909e11f75341d67): 직전 관측치 대비 변화; 상태: 사용 가능.
- 출력 series: US\_TREASURY\_NOMINAL\_10Y\_\_previous\_change\_v1; 정확한 값: -0.05 percentage\_points. stale 값은 과거 계산 기록이며 현재 요약에 채택하지 않는다.
- 방법: previous\_change\_v1; 공식: current\_value - exact\_reference\_value.
- 입력 series: US\_TREASURY\_NOMINAL\_10Y; 입력 관측: [관측 d5795e9f](#macro-record-620a418a6a6a4261843c24ff2333f800efb7980ab22c9104b60985e7cf50d542), [관측 07818a12](#macro-record-5ea22e484d99243f2bb8980ada756a7d00bce7b1b4889faa97d70aea979fa23f).
- 관측창: 2026-09-30, 2026-10-01; 가정: Decimal precision 50; ROUND\_HALF\_EVEN / 결측 보간/forward-fill 없음.

<a id="macro-record-cdce7c6c47f560e7367bbb54adcbd0715d6422a84a2b954ae40e216f385614d5"></a>

- 계산 ID: <code>MET_6a59bef34d7d7bfaf8b189dfb8aa2456ddb431790e1625d07e7ea94d1ae15b83</code>.
- [계산 6a59bef3](#macro-record-cdce7c6c47f560e7367bbb54adcbd0715d6422a84a2b954ae40e216f385614d5): 직전 관측치 대비 변화; 상태: 사용 가능.
- 출력 series: US\_TREASURY\_NOMINAL\_2Y\_\_previous\_change\_v1; 정확한 값: -0.10 percentage\_points. stale 값은 과거 계산 기록이며 현재 요약에 채택하지 않는다.
- 방법: previous\_change\_v1; 공식: current\_value - exact\_reference\_value.
- 입력 series: US\_TREASURY\_NOMINAL\_2Y; 입력 관측: [관측 4f71fa19](#macro-record-5a1bbe31a9d75c92a98131627c8ff42ab446c1975e586ce9f3c3dcde13fae4ee), [관측 c91d38cf](#macro-record-c3102ca23240ec811e5b5ff6760356c8ed7b4238555d745fa8db8fec64fc2998).
- 관측창: 2026-09-30, 2026-10-01; 가정: Decimal precision 50; ROUND\_HALF\_EVEN / 결측 보간/forward-fill 없음.

<a id="macro-record-3a5c2c56ebfaf4b67ce343adec0344ec0a76ec9fc39fc92aa008e73356f1280b"></a>

- 계산 ID: <code>MET_769f31b5a3eb4e6905758128ee2093d72689e91e6860142cda6e8440d3bed7a2</code>.
- [계산 769f31b5](#macro-record-3a5c2c56ebfaf4b67ce343adec0344ec0a76ec9fc39fc92aa008e73356f1280b): 전년 동월 대비 물가 상승률; 상태: 사용 가능.
- 출력 series: US\_CPI\_U\_HEADLINE\_NSA\_\_yoy\_v1; 정확한 값: 3.3965478924364767760574857396844210682272760945300 percent. stale 값은 과거 계산 기록이며 현재 요약에 채택하지 않는다.
- 방법: yoy\_v1; 공식: (index\_t / index\_t\_minus\_12\_months - 1) \* 100.
- 입력 series: US\_CPI\_U\_HEADLINE\_NSA; 입력 관측: [관측 7e4d1757](#macro-record-d0e7fa100a289ad973f2cb6a8f55eb7f3fe3589b84a75556fe877920dc8cbc59), [관측 01745871](#macro-record-95bedb1a82c5878057b021e4a5c4f230fef156a43501a4a876ebc05790043af8).
- 관측창: 2025-08-01, 2026-08-01; 가정: Decimal precision 50; ROUND\_HALF\_EVEN / 결측 보간/forward-fill 없음.
- 계산 진단: 중간 1개월 결측 보존; YoY는 정확한 두 endpoint만 사용.

<a id="macro-record-51728f0098562db005d1e229401d75058dba5b9353a0dc46c8a89433f7dbfc92"></a>

- 계산 ID: <code>MET_05aec7e22db022834322d9a18d5924714c3b32ce8c2981502142729e56d321ae</code>.
- [계산 05aec7e2](#macro-record-51728f0098562db005d1e229401d75058dba5b9353a0dc46c8a89433f7dbfc92): 전월 대비 물가 상승률 변화; 상태: 사용 가능.
- 출력 series: US\_CPI\_U\_HEADLINE\_NSA\_\_inflation\_trend\_v1; 정확한 값: 0.0317228509565728608498385788909786076641399661500 percentage\_points. stale 값은 과거 계산 기록이며 현재 요약에 채택하지 않는다.
- 방법: inflation\_trend\_v1; 공식: YoY\_t - YoY\_t\_minus\_1\_month.
- 입력 series: US\_CPI\_U\_HEADLINE\_NSA; 입력 관측: [관측 2306367a](#macro-record-72378b2cfe6e2c4037026eae05cebe253852fd77054ab86d9263137b0d9d2b94), [관측 7e4d1757](#macro-record-d0e7fa100a289ad973f2cb6a8f55eb7f3fe3589b84a75556fe877920dc8cbc59), [관측 747b853a](#macro-record-9a80737d20585ec1269bc790495de0fed65545075370ea8c3521ca28c4b278b2), [관측 01745871](#macro-record-95bedb1a82c5878057b021e4a5c4f230fef156a43501a4a876ebc05790043af8).
- 관측창: 2025-07-01, 2025-08-01, 2026-07-01, 2026-08-01; 가정: Decimal precision 50; ROUND\_HALF\_EVEN / 결측 보간/forward-fill 없음.
- 계산 진단: 중간 1개월 결측 보존; YoY는 정확한 두 endpoint만 사용 / 중간 1개월 결측 보존; YoY는 정확한 두 endpoint만 사용.

<a id="macro-record-0b39aac06c43d9f603bf111f60e852404e416a592300cf80af4554b511459120"></a>

- 계산 ID: <code>MET_13a9f2e37ac680e73a95c7405923eba74efb7cde3a189a1b3b98a8abf34d23f7</code>.
- [계산 13a9f2e3](#macro-record-0b39aac06c43d9f603bf111f60e852404e416a592300cf80af4554b511459120): 10년−2년 국채 수익률 차이; 상태: 사용 가능.
- 출력 series: US\_TREASURY\_NOMINAL\_10Y\_\_US\_TREASURY\_NOMINAL\_2Y\_\_yield\_spread\_v1; 정확한 값: 0.46 percentage\_points. stale 값은 과거 계산 기록이며 현재 요약에 채택하지 않는다.
- 방법: yield\_spread\_v1; 공식: yield\_10y\_t - yield\_2y\_t.
- 입력 series: US\_TREASURY\_NOMINAL\_10Y, US\_TREASURY\_NOMINAL\_2Y; 입력 관측: [관측 07818a12](#macro-record-5ea22e484d99243f2bb8980ada756a7d00bce7b1b4889faa97d70aea979fa23f), [관측 c91d38cf](#macro-record-c3102ca23240ec811e5b5ff6760356c8ed7b4238555d745fa8db8fec64fc2998).
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
