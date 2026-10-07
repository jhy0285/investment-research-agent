# 실제 미국 주식 Deep Dive

[한국어 보고서](us_equity_deep_dive.md)는 **2026-10-04 18:32:02 한국시간**의 고정 연구 초안이다. [부모 Opportunity Map](../opportunity_map_case/opportunity_map.md)의 미국 주식 후보에서 출발해 forward EPS·실적 질·AI 투자·Treasury 기회비용을 검토했다. BUY/SELL·가격목표·portfolio allocation은 하지 않았다. 가장 중요한 결론은 실제 성장·추정치 상향과 비경상 이익·현금 부담을 함께 본 `mixed`다.

| 파일 | 역할 |
| --- | --- |
| `plan.json` | 기존 SourcePlan, 검토한 25개 source와 48개 구절 Evidence 연결 |
| `pins.json` | 정확한 source spec digest와 선택한 immutable snapshot ID |
| `review.json` | 부모 hash·cutoff·원문 숫자 99개·계산 요청·해석 초안·scope/unknown/다음 질문 |
| `snapshots/` | 최종 채택 및 탐색·실패 판본; 덮어쓰지 않음 |
| `fragments/` | 실제 획득의 분야별 authoring 기록·접근 실패·자료 한계; 자동 연구 결과 아님 |
| `us_equity_deep_dive.md` | 한국어 본문·비교표·bull/base/bear·서사 검증·원문/계산 부록 |
| `run_manifest.json` | 구조화 결과·source/macro/부모 provenance·숫자/계산·진단·해시 |

## 조사 범위와 공식 자료

- S&P 500: FactSet의 10월 초 분기 earnings preview, 7월 예상과 8월 blended surprise, 첫째분기 기업군 실적. State Street/SPY index characteristics·상위 증권 비중·FY1 정의를 별도로 확인했다. Nasdaq-100은 공식 구성 설명만 현재 확인됐으며 valuation·EPS 자료는 부족하다.
- Microsoft: FY2026 Q4·Q3 공식 IR 결과와 cash flow. annual run rate·Copilot 유료 수요와 현금 PP&E를 조사했다.
- Alphabet: SEC에 제출된 8-K의 furnished earnings exhibit. 큰 10-Q는 기존 2MiB 한도를 넘어 사용하지 않았고 별개의 공개 exhibit를 확인했다. Cloud 성장·영업마진·평가이익·분기와 TTM FCF·depreciation을 구분했다.
- Amazon: 최근 10-Q의 revenue·AWS operating income·TTM FCF·평가 조정·depreciation. 같은 공시에서 두 source ID로 짧은 다른 구절을 선택했으며 독립 확인으로 세지 않는다.
- Meta: 최근 두 분기 IR 자료, lease 원금 포함 CAPEX·FCF·세금 효과·영업마진·legal charge와 연간 guidance 범위.
- NVIDIA: 공개 SEC 10-Q의 공급자 매출·margin·첫 반기 현금흐름·매출채권 집중·일부 결제 조건. 발행사 페이지의 자동 접근 제한은 우회하지 않았다.
- Treasury: Fed H.15 2026-10-02 release의 2026-10-01 만기별 nominal CMT investment-basis 금리와 같은 valuation 날짜인 2026-09-30 열을 확인했다. 기존 Macro Snapshot의 CPI·국채·USD/KRW도 같은 pipeline으로 사용했다.

99개 숫자는 원문 token을 그대로 옮긴 범위 내 기록이다. 새 Deep Dive 계산 7개는 EY 3개·같은 날짜의 설명용 yield gap 2개·Microsoft cash residual 2개다. 기존 macro 계산 7개를 함께 포함해 manifest에는 14개 MetricResult가 있다. 과거/현재/예상 기간, company vs index, GAAP vs adjusted, 분기 vs TTM·run rate를 구분한다. 현재 price·forward EPS 달러값·예상 margin·전체 revision 패널·pure-AI ROI가 없는 곳은 채우지 않았다.

## 실제 획득과 권리 범위

선택 source 중 **20개 available, 4개 policy_blocked, 1개 changed**다. available 구절 중 경제적 의미가 자동 검토 완료된 것은 없다. 구성 설명의 날짜는 unknown이며 정의 맥락으로만 사용한다. `changed`는 이번 검증 가능한 message selector를 찾지 못한 상태로 Stocktwits가 내용을 수정했다는 증명이 아니다.

Community는 실제 Hacker News API의 공개 발언 5개다. Reddit·X·Bogleheads·Lobsters에는 실제 접근/정책 확인을 시도하고 허용되지 않은 요청은 중단했다. Stocktwits HTML에는 접근했으나 기존 parser로 검증할 individual message를 확보하지 못했다. robots·인증·접근 제한을 우회하지 않았다. 관측된 AI 적자/거품·CAPEX 회수 불가 주장·실제 기업 이익 반론·가격에 반영된 지출 기대를 primary company data와 비교했다. 표본은 전체 투자자의 sentiment가 아니다.

기업·공급자 문서는 SourceSpec별 최대 세 구절, 구절당 정규화 텍스트 최대 1,200자로 제한했다. full issuer 문서·차트·이미지는 이 사례에 보존하지 않았다. 기관별 정책 URL·짧은 attribution·한계를 남겼으며 접근 성공을 공개·상업적 재배포 권한으로 추정하지 않는다. community 개인 원문 전체나 추가 개인 식별자를 수집하지 않는다. 공식 정부 데이터도 정의·판본·최초 공개 한계를 유지한다.

탐색 중 남은 `changed`/접근 실패 snapshot과 `*_partial.json` fragment는 당시 실패/중간 기록이다. 최종 plan과 pins의 선택 목록만 연구 입력이며, 탐색 결과를 모두 성공 Evidence로 세지 않는다. 잘린/없는 필드, PDF 미지원·redirect·size 한도·정책 차단을 숨기지 않는다. Q1 provider 글의 시작 예상 분기 레이블 혼재도 기록해 해당 비교 숫자를 사용하지 않았다.

`draft_capture/trailing_method_review/`에는 최종 정의 대조 전 보고서·review·manifest를 보존했다. 보존 구절에서 harmonic 방법 설명이 FY1에만 명시돼 trailing의 동일 aggregate 방식을 확정하지 않는 것으로 좁혔다. 숫자와 핵심 판단은 같으며 현재 root의 보고서가 채택본이다.

`draft_capture/forward_window_review/`는 분기·연간 성장률과 rolling forward EPS의 기간 차이 설명을 보완하기 전 초안이다. 현재 본문은 과거의 평가이익이 미래 consensus에도 포함됐다고 단정할 수 없다는 한계를 명시한다. 원문·숫자·판단은 같으며 설명의 추론 범위만 더 명확히 했다.

## 인터넷 없이 재현

저장소 루트에서 다음을 실행한다. Python 3.12 이상, 외부 패키지·API 키·LLM은 필요 없다.

```bash
python -m investment_research deep-dive replay examples/us_equity_deep_dive \
  --plan examples/us_equity_deep_dive \
  --store examples/us_equity_deep_dive/snapshots \
  --pins examples/us_equity_deep_dive/pins.json \
  --macro-plan examples/macro_case \
  --macro-store examples/macro_case/snapshots \
  --macro-pins examples/macro_case/pins.json \
  --parent-review examples/opportunity_map_case \
  --parent-plan examples/opportunity_map_case \
  --parent-store examples/opportunity_map_case/snapshots \
  --parent-pins examples/opportunity_map_case/pins.json \
  --parent-macro-plan examples/macro_case \
  --parent-macro-store examples/macro_case/snapshots \
  --parent-macro-pins examples/macro_case/pins.json \
  --output reports/us_equity_deep_dive.md \
  --manifest reports/us_equity_deep_dive_manifest.json
python -m unittest discover -v
```

보고서/manifest 경로를 생략하면 표준 출력만 사용한다. 다른 내용의 기존 파일·원문 snapshot·부모/현재 계획·pins·review는 덮어쓰지 않는다. 입력 보호·hash·정의 오류는 종료 코드 2, 파일 실행 실패는 1, 정상적인 판단 유보는 0이다. 이 replay는 고정된 연구의 재현이며 새로운 market update가 아니다.

새 획득이 필요하면 기존 `sources acquire`에 검토한 계획과 **새** pins 경로를 지정한다. source definitions·새 판본·cutoff·부모 hashes와 거시 metric ID까지 새 review에서 검토해야 한다. 날짜만 바꾸거나 source pins만 바꾸어 기존 초안을 최신 연구로 게시하지 않는다.

## 검증과 다음 질문

전체 **179개 테스트** 통과. Deep Dive의 합성 경계 20개를 추가했고 실제 HTTP·DNS 차단 replay 두 번에서 report·manifest가 동일했다. 모든 본문 참조는 고유 부록 anchor로 이동한다. 기존 네 보고서는 바이트가 같고 이전 사례 입력·pins·snapshot·manifest를 보존했다.

`mixed`는 작성된 draft 판단이고 engine의 시장/개인 확정 결론은 `insufficient_evidence`다. 자동 의미 검토·개인 적정 배분을 완료했다는 뜻이 아니다. quote 전사·계산·시점 검증과 경제적 설명의 의미 검토는 다르다. [방법과 현재 기능 부족](../../docs/us-equity-deep-dive.md)을 함께 읽는다.

다음 Deep Dive 하나는 **Microsoft와 Alphabet의 AI monetization이 투자자본을 회수할 반복 현금흐름으로 연결되는가**다. 유료 매출·증분 마진·자산 수명·리스 포함 투자자본의 조건을 검토한다. 제안만 했으며 이번 연구에서는 수행하지 않았다.
