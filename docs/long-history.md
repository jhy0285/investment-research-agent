# 시점 보장 장기 이력 수집

2026-10-22 추가하고 2026-10-23 확장했다(`pit_history_v2`). [투자 판단과 사후검증](investment-cycle.md)은 과거·독립·최근 검증에 **당시 알 수 있었던 값**을 요구하지만, 그동안 실제 장기 이력을 가져오는 어댑터가 없어 사용자가 직접 계약 형식으로 입력해야 했다. `invest history`는 검토된 공개 제공자에서 이 입력을 자동으로 만든다.

이 기능은 **자료를 모으는 단계**다. 투자 등급·순위·매수 승인을 만들지 않는다. 수익의 의미(총수익인지, 보유자 수익의 하한인지)는 검토된 계약대로만 표시한다.

## 실행

```bash
python -m investment_research invest history acquire examples/investment_history/btc_vs_kospi200tr_spec.json --output reports/history_btc_kospi
python -m investment_research invest history replay reports/history_btc_kospi
```

`acquire`는 인터넷에서 받아 새 디렉터리에 저장한다. `replay`는 보존한 행만으로 결과를 다시 만들고 모든 파일의 해시와 내용을 대조한다. 인터넷을 쓰지 않는다. 실패한 항목이 있으면 종료 코드 1, 명세·경로 오류는 2, 정상 완료는 0이다. `pit_history_v1`로 저장한 실행은 v1 규칙 그대로 재현한다.

| 파일 | 내용 |
| --- | --- |
| `spec.json` | 실행한 수집 명세 |
| `snapshots.json` | 요청 URL·획득 시각·원문 SHA-256·바이트 수와 판단에 쓰는 행·발췌, 접근 정책 확인 기록 |
| `history.json` | `investment-prices-v1` 가격 데이터셋과 특징값 행, 요약, 실패, 한계 |
| `history.md` | 쉬운 한국어 요약 |
| `history_manifest.json` | 위 네 파일의 해시 |

실제 자료는 `reports/`처럼 저장소에 커밋하지 않는 위치에 둔다. 개인 연구 재현용이며 재배포하지 않는다.

## 검토된 제공자

목록에 없는 제공자·시장·펀드·계열은 네트워크 요청 전에 거부한다. 계약은 [catalog/history.json](../investment_research/catalog/history.json)에 있다.

| 제공자 | 대상 | 시점 규칙 | 수익의 의미 |
| --- | --- | --- | --- |
| Upbit 일 캔들 | `KRW-BTC`, `KRW-ETH` (2017-09-25 이후) | 캔들 종료(00:00 UTC = 09:00 KST). `known_at`은 종료 시각과 마지막 틱 저장 시각 중 늦은 쪽 | 보유자 수익의 **하한**(`price_lower_bound`) |
| Upbit 30분 캔들(정렬) | 다른 가격 계열의 종가 시각마다 그 시각에 끝나는 캔들 하나 | 정렬 대상과 같은 `at`. 그 30분에 체결이 없으면 값을 만들지 않는다 | 하한(`price_lower_bound`) |
| 삼성자산운용 KODEX 발행사 JSON | `KODEX 200TR`, `KODEX MSCI KOREA TR`, `KODEX 코스피TR` (상장 이후 주별 표본) | KRX 종가 15:30 KST, 공표는 보수적으로 18:00 KST | **원화 세전 총수익**(`non_distributing_fund_price`) |
| St. Louis Fed ALFRED 판본 CSV | `CPIAUCSL`, `UNRATE`, `FEDFUNDS`, `DGS10`, `DEXKOUS` | 판본일 당일 미국 중부시각 자정(다음 날 06:00 UTC) 이후, 단 실제 획득보다 늦지 않게 | 거시 특징값 |
| FactSet Earnings Insight PDF | S&P 500 forward 12개월 P/E (2017-01 이후 주간 판) | 발행일 미국 동부시각 자정(다음 날 05:00 UTC) 이후 | 이익 전망 기반 밸류에이션 특징값 |

### 수익의 의미를 정하는 방법

- **KODEX TR ETF.** 발행사 상품 정보의 분배 정책이 "미지급(재투자)"이고 분배 내역이 비어 있을 때만 총수익으로 표시한다. 이 진술은 수집할 때마다 다시 확인하며, 바뀌면 그 상품은 실패로 남기고 총수익으로 표시하지 않는다. 오늘의 정책 문구는 과거를 증명하지 못하므로 **이력 자체도 대조한다.** 분배금을 지급하면 NAV가 추종하는 총수익 지수보다 그만큼 떨어진다. 실제 2017~2026 KODEX 200TR 주간 표본에서 NAV/지수의 최악 주간 차이는 -0.62%, 평균은 +0.0004%였다. 한 주라도 -1% 이하이거나 누적 차이가 보수(연 0.5% 상한)+1%보다 나쁘면 분배 가능성으로 보고 총수익 표시를 거부한다. 1%보다 작은 분배는 이 검사로 놓칠 수 있다. 국내 TR ETF 매매차익은 보유기간 과세 대상이며 이 수익에서 세금을 빼지 않았다.
- **코인 현물.** 하한 표시는 검토된 Upbit 수집기가 만든 데이터셋에만 인정한다(`provenance.provider`). 계획에 직접 적은 하한 표시는 배당주처럼 정기 분배가 있는 자산을 잘못 표시해 같은 상품 안의 시점 비교를 치우치게 할 수 있어 받지 않는다. 현금 분배가 없다. Upbit가 과거 포크·에어드롭(예: ETHW)을 실제로 지급했는지는 공지로 확인하지 못했다(2026-10 조사). 그래서 총수익이라고 하지 않고, 빠진 비현금 분배는 보유자 수익을 낮게 잡는 쪽이므로 측정 수익을 **하한**으로 표시한다. 같은 상품 안의 시점 비교는 빠진 분배의 시점에 따라 어느 쪽으로든 조금 치우칠 수 있다.

### 제공자별 확인 사항

- Upbit의 `timestamp`는 체결 시각이 아니라 마지막 틱이 **저장된** 시각이다. 종료 후 60초까지만 허용한다. 2018년 등 오래된 캔들은 `timestamp`가 비어 있어, 종료 60초 뒤에 알려진 것으로 보수적으로 둔다.
- KODEX 발행사 응답은 상장 이후를 주별 첫 거래일 표본으로 준다. 2017~2026 표본의 비월요일 날짜를 수능일과 대조해 15:30 종가 규칙에 예외가 없음을 확인했다. 발행사 사이트에는 별도 이용약관 페이지가 없었고 robots.txt는 전체 허용이다.
- FactSet은 금요일 판을 먼저, 휴일 주에는 목요일 판을 찾는다. 둘 다 없으면 그 주는 비워 두고 이전 값을 끌어오지 않는다. 1쪽 머리글의 발행일이 요청한 판과 같아야 하고, "The forward 12-month P/E ratio for the S&P 500 is X." 문장이 하나의 값만 말해야 한다. 오래된 판은 약 5MB라 이 제공자만 8MB까지 받는다. 1쪽만 해독하며 선택적 `pdftotext`·`pdfinfo`가 없으면 그 판은 실패로 남긴다. 한 판을 읽지 못해도 그 판만 `invalid`로 기록하고 나머지 판은 유지한다. 같은 URL의 파일이 나중에 교체됐을 수 있으므로 PDF 작성·수정일이 발행일보다 3일 넘게 늦거나 없으면 그 판은 발행일이 아니라 획득 시각부터 알려진 것으로 둔다(`known_at_basis`). 관측일은 발행일 2일 전(그 주 수요일 종가)으로 둬 신선도 검사가 실제보다 새로워 보이지 않게 한다.

## 시점 누수를 막는 방법

- **판본 표본.** ALFRED에서 `vintage_start`부터 `vintage_step_days` 간격(7~92일)과 오늘의 판본을 받는다. 각 판본에서 새 관측이나 **고쳐진 값만** 새 행으로 남긴다. 그래서 같은 관측의 처음 발표값과 개정값이 서로 다른 `known_at`으로 함께 보존되고, 과거 시점의 조건 판단은 그때 보였던 값만 쓴다. 표본 사이에 나온 발표는 다음 표본일에 보인 것으로 기록되므로 실제보다 늦을 수는 있어도 이르지 않다.
- **관측창 인자 금지.** ALFRED에 `cosd`/`coed`(관측 시작·끝) 인자를 붙이면 판본이 아닌 값이 섞여 돌아오는 것을 실제 응답으로 확인했다. 예를 들어 2020-03-02 판본에 아직 발표되지 않은 2020년 3월 CPI가 들어 있었다. 그래서 항상 전체 판본을 받아 로컬에서 `window_days`만큼만 보존한다. 판본일보다 늦은 관측이 하나라도 있으면 그 응답 전체를 거부한다.
- **관측창 밖 개정.** 각 판본에서 `window_days` 안의 관측만 보존하므로, 관측창을 벗어난 오래된 관측의 개정(예: 매년 2월 CPI 계절조정 개정)은 기록하지 않는다. 조건 판단은 그 시점에 보인 **가장 최근 관측**만 쓰므로 판단에는 영향이 없지만, 오래된 관측의 값 자체를 분석할 용도로 쓰면 안 된다.
- **철회 감지.** 이전 판본에 있던 관측이 같은 관측창 안에서 이후 판본에서 사라지거나 결측으로 바뀌면 그 특징값 전체를 실패로 남긴다. 특징값 행은 "더 이상 없음"을 표현할 수 없고, 옛 값을 그대로 두면 철회된 숫자를 보여 주게 되기 때문이다.
- **헤더 확인.** ALFRED CSV 첫 줄과 FactSet 1쪽 발행일이 요청한 판과 다르면 거부한다.
- **결측은 결측.** `.`·빈 값·체결 없는 캔들은 0이나 이전 값으로 바꾸지 않고 건너뛴다.
- **같은 판본 안의 전년 대비.** `transform: "yoy_percent"`는 월별 계열에서만 허용한다. 각 판본 안에서 정확히 12개월 전 같은 달의 값으로 계산한다. 기준월이 없으면 값을 만들지 않는다.
- **파생 가격 특징값.** `trailing_return`(N일 전 종가 대비 수익률)과 `close_to_sma`(최근 N개 종가 평균 대비 괴리)는 그 시점까지 알려진 행만 쓰고 `known_at`은 사용한 행 중 가장 늦은 시각이다. 기준 관측이 7일보다 멀거나, N개 종가가 그 계열의 평소 간격 기준 (N−1)간격+7일보다 넓게 흩어져 있으면 값을 만들지 않는다. 빠진 표본 요약도 그 계열의 평소 간격(일·주)으로 센다.

## 수집 명세

```json
{
  "schema_version": "investment-history-spec-v1",
  "prices": [
    {"provider": "kodex_issuer_weekly", "fund": "2ETF92"},
    {"provider": "upbit_aligned_candles", "market": "KRW-BTC", "align_to": "KODEX_200TR"},
    {"provider": "upbit_day_candles", "market": "KRW-ETH", "start": "2017-10-01"}
  ],
  "features": [
    {"name": "btc_close_to_sma43w", "provider": "price_derived", "instrument_id": "UPBIT_KRW_BTC_AT_KODEX_200TR",
     "kind": "close_to_sma", "observations": 43},
    {"name": "us_cpi_yoy", "provider": "alfred_vintage_csv", "series": "CPIAUCSL", "transform": "yoy_percent",
     "vintage_start": "2019-01-01", "vintage_step_days": 30, "window_days": 500},
    {"name": "sp500_forward_pe", "provider": "factset_earnings_insight", "series": "sp500_forward_pe",
     "start": "2025-01-03", "step_weeks": 4}
  ]
}
```

정렬 계열(`upbit_aligned_candles`)은 명세에서 정렬 대상보다 뒤에 둔다. 가격은 최대 다섯, 특징값은 최대 스무 개다. 예상 요청 수가 1,200을 넘으면 실행 전에 거부한다. 일시적인 시간 초과·연결 끊김·429/5xx 응답은 1초부터 두 배씩 늘린 간격으로 최대 두 번 다시 요청하며(robots.txt 확인도 요청 수와 Crawl-delay에 포함), 그래도 실패하면 그 항목만 실패로 기록하고 값을 만들지 않는다.

## 투자 계획에 연결하기

후보에 데이터를 붙여 넣지 않고 이력의 ID를 적는다. [예시 계획](../examples/investment_cycle/btc_trend_vs_kospi200tr_plan.json)을 참고한다.

```json
"history": {"prices": "UPBIT_KRW_BTC_AT_KODEX_200TR", "benchmark": "KODEX_200TR", "features": ["btc_close_to_sma43w"]}
```

```bash
python -m investment_research invest run my_plan.json --research-run reports/asks/<조사 실행> --history reports/history_btc_kospi --run-dir reports/my_decision
```

- 이력 실행을 먼저 오프라인 재현해 검증하고, 판단 시각보다 늦게 받은 이력이면 거부한다(look-ahead 방지). 보통 **이력 수집 → 조사(`ask`) → `invest run`** 순서로 실행하며, 판단 전이라면 조사 뒤에 받은 이력도 쓸 수 있다. 이력의 근거는 조사 실행 해시가 아니라 이력 실행의 `history.json` 해시로 판단 기록에 남는다.
- 현재 조건 판단이 읽는 행(각 특징값의 그 시각 최신 행)과 최신 가격 행만 현재 근거로 연결한다. 이 숫자는 사용자가 계획에 적은 값이 아니라 이 시스템의 검토된 수집기가 보존한 행과 해시에서 나온다. 펼친 계획과 근거는 실행 기록에 저장되므로 이후 `invest replay`에는 이력 디렉터리가 필요 없다.
- **비교 시장**은 같은 통화의 별도 상품이다. 코인 하한은 시점 보장 총수익 비교 시장(예: KODEX 200TR)과만 승인 검증에 쓸 수 있다. 어떤 상품이 그 전략의 시장 대안인지는 사용자가 검토해 정한다.
- 사후 평가(`invest review --prices`)에 판단 이후의 실제 가격 이력으로 쓸 수 있다.

## 지원하지 않는 것

미국 주식·ETF의 원화 총수익(KODEX 발행사 목록 검색에서 해외지수 TR ETF를 찾지 못했다), KODEX 외 국내 종목·ETF 가격(KRX 정보데이터시스템은 로그인 필요, Naver·Yahoo·Nasdaq API는 robots.txt가 전체 차단), FactSet 외 개별 기업 이익 전망 판본, 자동 예약 갱신은 없다. FRED의 최신 CSV는 개정 이력이 없으므로 과거 판단용 이력으로 쓰지 않는다. 이 기능으로 받은 자료를 전체 시장의 완전한 이력이라고 표현하지 않는다.
