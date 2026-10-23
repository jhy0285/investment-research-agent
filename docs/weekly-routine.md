# 정기 점검 절차 (사람이 하는 주간 루틴)

이 시스템은 예약 실행을 포함하지 않는다. 이력 수집과 조사는 자동으로 돌릴 수 있지만, **투자 판단은 자동으로 낼 수 없다.** 계획의 경제적 검토(`review`)는 사람이 쓰는 것이 규칙이고, 코드나 LLM이 대신 쓴 검토로 매수 판단을 만들지 않는다. 그래서 절차를 "자동 수집 → 사람이 읽고 검토 → 판단"으로 나눈다.

## 한 번의 점검

날짜는 예시다. 새 디렉터리를 쓴다(기존 실행은 덮어쓰지 않는다).

```bash
# 1. 이력 갱신 (인터넷 필요. 몇 분 걸린다)
python -m investment_research invest history acquire my_history_spec.json --output reports/history_2026-11-06
python -m investment_research invest history replay reports/history_2026-11-06     # 해시·재현 확인

# 2. 조사 (인터넷 필요)
python -m investment_research ask '현재 신규 자금을 투자한다면 어디에 투자하는 것이 가장 합리적인가?' \
  --previous-scan reports/asks/<지난 조사 실행> --run-dir reports/asks/2026-11-06

# 3. 보고서를 읽고 계획의 review를 직접 쓴다 (사람)
#    - evidence_ids / counter_evidence_ids: 이번 조사 실행의 근거 ID
#    - review.reviewer / at / note: 검토자, 근거 확보 이후·판단 이전 시각, 범위와 한계

# 4. 판단 (인터넷 불필요)
python -m investment_research invest run my_plan.json --research-run reports/asks/2026-11-06 \
  --history reports/history_2026-11-06 --run-dir reports/decisions/2026-11-06 --journal reports/investment_journal
python -m investment_research invest replay reports/decisions/2026-11-06

# 5. 지난 판단의 사후 평가 (성숙한 결과가 생긴 뒤. outcome_prices.json은 새 history.json의 prices 값
#    중 투자상품과 비교 시장의 데이터셋을 JSON 배열로 모은 파일이다)
python -m investment_research invest review --journal reports/investment_journal --prices outcome_prices.json \
  --as-of '2026-11-06T18:00:00+09:00' --run-dir reports/reviews/2026-11-06
```

## 순서가 중요한 이유

- **이력 → 조사 → 판단**이다. 판단은 판단 시각보다 늦게 받은 이력을 거부한다. 이력 수집이 판단 전이기만 하면 조사 전·후 어느 쪽이든 괜찮다.
- 조사가 판단 시각에 7일보다 오래됐으면 판단을 보류한다. 격주로 돌린다면 조사도 같이 갱신한다.
- 같은 날짜의 자료는 `known_at`으로 구분된다. 한국 장이 끝나기 전에 돌리면 그날 종가는 아직 없고, 직전 거래일 값이 현재 근거가 된다.

## 자동화해도 되는 것과 안 되는 것

| 단계 | 자동화 | 이유 |
| --- | --- | --- |
| 이력 수집·재현 | 가능 | 결정적이고 실패하면 값을 만들지 않는다 |
| `ask` 조사 | 가능 | 새 실행 디렉터리만 만든다 |
| `review` 작성 | **불가** | 경제적 의미의 검토는 사람이 한다 |
| `invest run` | 검토가 있을 때만 | 검토자·시각·메모가 없는 계획은 계획 검증에서 거부된다 |
| 주문 | 해당 없음 | 이 프로그램은 주문을 보내지 않는다 |

예약 작업(주기 실행)은 이 저장소가 만들지 않는다. 클라우드나 로컬 스케줄러에서 1~2단계만 정기 실행하도록 설정하는 것은 사용자 환경의 결정이다. 이때 이력 수집은 요청 수와 Crawl-delay 때문에 몇 분에서 수십 분이 걸리고, 제공자의 요청 제한을 지켜야 한다. 이력 수집이 일부 실패해도(종료 코드 1) 성공한 항목은 `history.json`에 그대로 있다. 실패한 항목은 `history.md`의 "수집·검증 실패"에서 이유를 확인한다.

## 점검 목록

- 이력 보고서의 "수집·검증 실패"가 비어 있는가, 아니면 이유가 합당한가.
- 총수익 표시가 필요한 비교 시장(KODEX TR, TIGER 미국 NAV)이 검증을 통과했는가. 통과하지 못하면 승인 검증이 막히는 것이 정상이다.
- 판단 보고서의 "판단을 제한하는 근거"와 "시장 조사 범위와 남은 공백"을 읽었는가.
- 지난 판단의 전략 상태가 `경고` 또는 `폐기 후보`이면 같은 버전은 신규 매수가 막힌다. 조건을 바꾸려면 새 버전으로 만든다([투자 판단과 사후검증](investment-cycle.md)).
