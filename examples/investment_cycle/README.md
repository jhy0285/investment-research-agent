# 투자 판단과 일지 예제

실제 시장 데이터를 만들어 채우지 않는다. 다음 두 실행은 목적이 다르다.

`no_validated_strategy.json`은 실제 완료 연구에 아직 승인 전략이 없을 때 쓰는 기본 계획이다. 원래 조사 시점의 자료를 읽고 신규 매수를 차단한다. 실시간 새 조사는 `ask`로 실행한다.

```bash
python -m investment_research invest run examples/investment_cycle/no_validated_strategy.json --research-run reports/opportunity_coverage_validation_20261006T130156KST/final_repeat_scan --run-dir reports/example_current_decision --journal reports/investment_journal
python -m investment_research invest replay reports/example_current_decision
```

아래 생성기는 테스트와 공유하는 **합성** 가격 경로·당시 판본·원문 참조로 승인을 검증한다. 금융 숫자는 작성된 fixture이며 실제 시장·미래 성과가 아니다. 생성된 계획에서 현재 상품 종가와 배당 포함 총수익 지수가 별도 필드임을 확인할 수 있다. 과거/독립/최근 1개월 우위가 있으면 A 분할 매수와 400만원 배정, 600만원 현금 유지가 나온다. 합성 사후 가격에서는 추천 손실을 계산한다.

```bash
python -m examples.investment_cycle.demo --output reports/example_synthetic_cycle
python -m investment_research invest review --journal reports/example_synthetic_cycle/journal --prices reports/example_synthetic_cycle/outcome_prices.json --as-of '2026-12-10T09:00:00+09:00' --run-dir reports/example_synthetic_review
```

생성기에서는 표본 최소 개수를 2로 낮춰 테스트한다. 실제 기본 정책은 20/10/10이다. 새 독립 전략 승인에 테스트용 정책을 그대로 적용하지 않는다. 전체 계약과 제한은 [운영 안내](../../docs/investment-cycle.md)에 있다.
