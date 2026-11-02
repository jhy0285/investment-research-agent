# 사전 등록 전략 라이브러리

[`pre_registered_library.json`](pre_registered_library.json)은 **가설 목록**이다. 시장 근거도, 매수 후보 승인도 아니다. 어떤 항목도 이 시스템의 문턱을 통과하지 않았다. 규칙과 기간은 공개 문헌에서 왔고, 등록 이후의 섀도 기록만 독립 증거가 된다. 전체 설계는 [섀도 추적과 사전 등록](../../docs/shadow-tracking.md), 항목별 조사는 [전략 가설 조사](../../docs/strategy-hypotheses.md)에 있다.

## 시험할 수 있는 후보 4개

| ID | 규칙 | 적용 대상 | 비교 시장 |
| --- | --- | --- | --- |
| `trend_sma43w_btc` / `_eth` | 종가가 43주(약 10개월) 평균보다 높을 때 다음 1개월 보유 | Upbit 원화 BTC / ETH (보유자 수익의 하한) | KODEX 200TR (발행사 확인 원화 총수익) |
| `tsmom_364d_btc` / `_eth` | 지난 364일(약 12개월) 수익률이 0보다 클 때 다음 1개월 보유 | 위와 같음 | 위와 같음 |

- 숫자는 문헌의 10개월·12개월에 맞춘 것이고 이 시스템의 과거 결과를 보고 고르지 않았다(`trial_count` 1). 적용 대상과 비교 시장은 두 자산의 과거를 알고 정했으므로 **완전한 사전 등록이 아니다.** 같은 아이디어의 변형 4개는 서로 상관이 높아 독립 증거 네 개로 세지 않는다.
- 동결 시각은 2026-11-02이고 독립 검증 구간(2027-01-01~)과 최근 구간(2028-07-01~)은 모두 그 뒤다. 과거 구간의 백테스트 결과는 후보를 아는 상태에서 본 값이다.
- 두 규칙의 가격 조건은 신호 조건과 같다(추세 규칙에는 별도의 가격 부담 조건이 없다). 무효화 조건(`< -0.5`)은 보유 재검토 트리거이며 백테스트에 쓰이지 않는다.
- 거래비용 양방향 25bp는 [예시 계획](../investment_cycle/btc_trend_vs_kospi200tr_plan.json)에서 가져온 **자리표시 값**이다. Upbit 수수료표나 호가 차이로 확인하지 않았고 실제 체결 비용을 대신하지 않는다. 세금은 빼지 않았다.

## 시험할 수 없는 후보 15개

이 시스템에 이력 제공자가 없거나, 포트폴리오를 계속 굴리는 규칙을 표현하는 백테스트가 없는 후보다. 이유와 필요한 것을 항목마다 적었다. **시험 불가는 통과가 아니다.** 시험 후보 수 K에도 세지 않는다(시험하지 않았으므로 검정이 없다). 필요한 이력과 엔진은 [포트폴리오 규칙용 백테스트 설계안](../../docs/portfolio-backtest-design.md)에 정리했다.

## 사용

```bash
# 1. 이력 수집과 재현 (인터넷 필요. 실제 자료는 reports/ 같은 미커밋 위치에)
python -m investment_research invest history acquire examples/investment_history/crypto_trend_library_spec.json --output reports/history_crypto_trend
python -m investment_research invest history replay reports/history_crypto_trend

# 2. 사전 등록 (이 컴퓨터의 시계가 등록 시각이 된다. 이 시점부터 전향 기록이 시작된다)
python -m investment_research invest strategy register examples/strategy_library/pre_registered_library.json --journal reports/investment_journal
python -m investment_research invest strategy list --journal reports/investment_journal
```

이후의 점검 절차는 [정기 점검 절차](../../docs/weekly-routine.md)를 따른다. 계획의 `review`는 사람이 직접 쓴다.
