# 변경 이력

저장소의 첫 커밋(`6fc6a92`)에 그 이전의 작업이 한 번에 들어 있어 Git 이력만으로는 기능별 변경 시점을 알 수 없다. 이 파일은 그 이후의 변경을 기록하고, 첫 커밋의 내용은 문서에 적힌 날짜 기준으로만 요약한다.

## 2026-10-22

### 고침
- **보유 자산의 판단 보류** (`investment_cycle_v2`). 이전 규칙은 현재 원자료나 상품 가격이 확인되지 않은 보유 자산에 `비중 축소 검토`를 냈다. 자료 부족을 반대 근거로 취급한 것이어서, 이제는 `보유 유지`(판단 보류)로 두고 신규 매수만 막는다. 이미 측정된 검증 실패·최근 붕괴·실전 경고는 자료 공백이 있어도 축소 검토로 남는다. 다만 판단 시점 이후에 확보한 이력(look-ahead)으로 계산한 실패는 행동 근거로 쓰지 않는다. `investment_cycle_v1`로 저장한 실행은 v1 규칙 그대로 재현한다. [판단 표](docs/investment-cycle.md#계산과-승인)
- `decide()`를 현재 상태 확인·검증·행동 규칙 단계로 나눠 규칙 버전을 표로 관리한다.

### 추가
- **시점 보장 장기 이력 수집** `invest history acquire/replay`. Upbit 원화 BTC·ETH 일 캔들, 미국 정부 거시 계열(CPI·실업률·연방기금금리·10년 국채·원/달러)의 ALFRED 판본, 같은 판본 안의 전년 대비 변화, 가격 파생 특징값(N일 수익률·이동평균 괴리)을 `investment-prices-v1`·특징값 계약으로 만든다. 보존 행으로 오프라인 재현한다. [안내](docs/long-history.md)
- ALFRED에 관측창 인자(`cosd`)를 붙이면 판본이 아닌 값이 섞여 돌아오는 것을 확인하고, 판본일보다 늦은 관측이 든 응답을 거부하는 검사를 넣었다.
- 일시적인 시간 초과·429/5xx는 1초부터 늘린 간격으로 최대 두 번 다시 요청한다. 실패한 항목은 값을 만들지 않고 실패로 기록한다. 이후 판본에서 관측이 철회되면 옛 값을 남기지 않고 그 특징값을 실패로 둔다.

### 정리
- `black`(줄 길이 120, 따옴표 유지)으로 Python 서식을 정리했다. 동작은 바뀌지 않았다. 문서 문자열 하나의 들여쓰기를 빼면 모든 파일의 구문 트리가 같다.
- README에 기능 상태 표를 추가했다.

## 첫 커밋 `6fc6a92`에 포함된 작업 (문서에 적힌 날짜 기준)

- 합성 오프라인 Cross-Asset Research Brief, 공개 출처 획득·검증·replay, Macro Regime Snapshot. [오프라인 안내](docs/offline-mvrs.md), [공개 출처](docs/source-acquisition.md), [거시](docs/macro-mvrs.md)
- 2026-10-04: 실제 15영역 Opportunity Map과 첫 미국 주식 Deep Dive 고정 연구. [Opportunity Map](docs/opportunity-map.md), [Deep Dive](docs/us-equity-deep-dive.md)
- 자연어 `ask` Research Orchestrator, Source Discovery, 한국 원자료, 삼성전자·SK하이닉스 비교, 원자재 Deep Dive, Source Anomaly Guard.
- 2026-10-07: 투자 가설·과거/최근 검증·행동·1,000만원 예시 배분·불변 일지·사후 평가. [투자 판단과 사후검증](docs/investment-cycle.md)
