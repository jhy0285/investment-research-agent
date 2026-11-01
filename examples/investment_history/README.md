# 장기 시점 이력 수집 예제

[btc_macro_spec.json](btc_macro_spec.json)은 Upbit 원화 BTC·ETH 일별 종가(2017-10 이후), 미국 CPI 전년 대비(같은 판본 계산)와 10년 국채 수익률의 ALFRED 판본, BTC 90일 수익률·200일 평균 괴리를 함께 모으는 명세다.

```bash
python -m investment_research invest history acquire examples/investment_history/btc_macro_spec.json --output reports/history_btc_macro
python -m investment_research invest history replay reports/history_btc_macro
```

ALFRED는 robots.txt의 Crawl-delay 2초를 지키므로 판본 약 190개를 받는 데 몇 분 걸린다. 실제 응답은 이 저장소에 넣지 않는다. 결과의 의미와 한계는 [시점 보장 장기 이력 수집](../../docs/long-history.md)을 읽는다.
