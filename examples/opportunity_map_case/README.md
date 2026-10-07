# 실제 현재 시장의 Cross-Asset Opportunity Map

[한국어 보고서](opportunity_map.md)는 **2026-10-04 13:16:53.131802 한국시간**(`2026-10-04T04:16:53.131802+00:00`)의 고정 연구다. 신규 자금을 가진 한국 거주 자산축적기 투자자가 무엇을 더 깊게 조사할지 질문한다. 매수·매도·투자비중이나 미래 수익을 확정하지 않는다.

## 실제 조사 범위와 결과

현금성 자산, 단기·장기 국채, 미국·한국 주식, 성장·가치·배당, 금, 광범위 원자재, 에너지, 천연가스, BTC, ETH, 한국 주거 부동산의 **15개 행**을 작성했다. 성장·가치·배당은 겹치는 주식 특성이며 모든 행을 독립적인 분산 자산군으로 세지 않는다. 기관·상품·기업 표본의 깊이도 같지 않다.

후속 조사 후보는 **미국 주식, 한국 주식, 에너지**다. 후보 선정은 현재 근거로 검증할 질문이 구체적이라는 연구 초안이며 투자 매력·즉시 매수를 뜻하지 않는다. 금·광범위 원자재·천연가스·BTC·ETH·지역 부동산의 현재 상대 매력은 부족한 자료를 공개하고 유보했다. 배당은 개인 현금 분배 필요·계좌 조건을 모르는 상태에서 독립 Deep Dive 우선순위를 낮췄다.

가장 의미 있는 긴장은 미국 대형 지수의 낮아진 예상 PER과 높은 이익성장 전망, NVIDIA 실제 매출·영업현금흐름 증가와 고객 결제·매출채권 조건이다. 공급자 매출 증가와 구매자 투자 회수는 별도이며 현재 적정가격은 아직 확인하지 않았다. 다음 한 과제는 **미국 주식 예상 PER의 분모 검증과 국채 대안 비교**다. 이번에는 제안만 한다.

## 자료·기존 시스템 연결

이 사례의 새 자료는 **27개 source**(26개 available, Reddit 1개 policy_blocked)와 **64개 source Evidence**다. 기존 거시 snapshot의 4개 source·10개 Evidence·7개 Metric을 합쳐 **31개 source·74개 Evidence·7개 Metric**을 기존 ResearchCase에 연결한다. 원자료가 다른 source ID로 반복돼도 독립 확인 횟수로 세지 않는다.

| 파일 | 역할 |
| --- | --- |
| [plan.json](plan.json) | 공식·공급자·community URL, 정의·시점·정책·원문 구절·주장과 명시적 자산 범위 |
| [pins.json](pins.json) | 실제 source 획득의 고정 snapshot ID·계획 연결 |
| [review.json](review.json) | 질문·자기보고/UNKNOWN·15개 비교 행·조건부 해석·후속 후보의 검토 전 초안 |
| [snapshots](snapshots) | 기존 SourceSpec/acquire로 확보한 불변 원문 구절·해시·획득 완료 시각 |
| [fragments](fragments) | 자산별 출처 조사 기록·검증 질문·접근 실패와 원출처 의존 |
| [run_manifest.json](run_manifest.json) | 코드·방법·자료·보고서 해시, 출처·근거·주장·계산·효과적 우선순위와 전체 거시 판본 기록 |
| [기존 macro pins](../macro_case/pins.json) | CPI·미국 국채·KRW 환율의 고정 판본 |

정성 prose에는 금융 숫자를 직접 적지 않고 Evidence·Metric ID로 연결한다. 보고서의 주요 수치는 보존 원문 또는 기존 deterministic macro 계산에서 나온다. 구절 일치 확인은 공급자가 해당 내용을 발표했다는 좁은 확인이며 경제적 의미·미래 적용 가능성·투자 매력의 자동 검증이 아니다. 종합 해석과 source 서사 주장은 pending으로 보존한다.

## 현재 정보와 관측 기간

- FactSet 10/2 예상 이익 자료와 SPDR 10/1 표본: 예상·과거 분배·보유 비중의 서로 다른 정의를 유지한다. 추정치의 원출처는 공유될 수 있다.
- NVIDIA 8/26 SEC 공시의 7/26 종료 분기와 삼성 7/30 발표의 6/30 종료 분기는 당시 사업 실적이다. 이를 10월 실시간 사업 상태나 고객 미래 수요로 바꾸지 않는다.
- 산업부 10/1의 9월 수출, FSC의 9/30 시장금리와 비용 맥락은 한국 경제의 별도 근거다. 한국 국채금리를 예금·정책금리로 부르지 않는다.
- EIA의 9/25 주간 재고와 9월판 수급 추정·조건부 전망을 분리한다. 8월 평균가격을 오늘의 실행가격으로 쓰지 않는다. 미래 연도의 LNG·생산·재고 전망을 현재 실측으로 표시하지 않는다.
- HN의 9월·10월 실제 댓글 5개는 한 영어 채널의 목적 검색 표본이다. 확산·대표성·합의·인기 점수·독립 사실을 추정하지 않는다.
- iShares 10/2 상품 관측과 CoinShares 10/2 보고를 활용했지만 전체 디지털자산 유입을 BTC·ETH별 흐름으로 바꾸거나 주중/전체 주를 같은 기간으로 계산하지 않는다.

발행일 미확인인 상품 페이지는 명시한 관측일과 실제 획득 완료 시각을 별도로 보존한다. 관측 기간이 최신이라는 조건과 획득 이후라는 조건을 만족할 때만 현재 확보판의 구절로 사용하며, 당시 최초 공개판·retrieval 이전 이용 가능성을 증명하지 않는다. 실패·stale·미래 참조를 가진 현재 문장은 채택 보류로 렌더링한다. 현재 YoY의 과거 기준 관측은 계산 입력으로만 사용하며 현재 물가처럼 표시하지 않는다.

## 오프라인 실행

저장소 루트에서 아래 명령을 실행한다. 인터넷·API 키·LLM을 호출하지 않는다.

```bash
python -m investment_research opportunity replay examples/opportunity_map_case --plan examples/opportunity_map_case --store examples/opportunity_map_case/snapshots --pins examples/opportunity_map_case/pins.json --macro-plan examples/macro_case --macro-store examples/macro_case/snapshots --macro-pins examples/macro_case/pins.json
```

`--output reports/opportunity_map.md --manifest reports/opportunity_manifest.json`을 붙여 새 파일을 생성할 수 있다. 이미 다른 내용이 있는 결과나 입력 계획·pins·review는 덮어쓰지 않는다. 새 자료 획득은 기존 `sources acquire`와 `macro acquire`에만 있으며, 새 pins·연구 초안을 검토해야 새 현재 연구가 된다. 고정 입력의 replay 날짜만 바꾸어 최신 연구로 게시하지 않는다.

## 사용자·권리·자료 한계

대한민국 세법상 거주자·1998년생·KRW·자산축적기·안정적인 근로소득·장기 투자 의향·변동성 감수 의향은 사용자 자기보고다. 총자산·현금·비상자금·부채·보유범위·월 투자액·큰 자금수요·주택 필요자금·위험 감당 능력은 UNKNOWN이며 0·무부채·높은 허용위험으로 대체하지 않는다. 세금·계좌별 순수익·개인 비중을 계산하지 않았다.

각 출처의 정책·robots·권리·보존 조건을 snapshot에 기록했다. 전체 공개자료·웹페이지의 재배포 권리를 확보했다고 주장하지 않는다. 삼성·발행사 등의 짧은 구절은 출처 표시를 한 개인·비상업적 workspace 연구 범위이며 상업 서비스·전체 자료 재배포 허가는 아니다. 제한된 원문이 있다면 해당 범위·정책을 다시 확인해야 한다. 이 task에서는 외부로 게시하거나 메시지를 보내지 않았다.

Reddit robots, WGC 자동 수집 제한, BOK robots 응답 형식, 일부 API/페이지 크기·리다이렉트 제한을 우회하지 않았다. NVIDIA 사이트의 자동 접근 제한을 확인한 뒤 독립적인 공개 SEC 공시를 확보했다. 부동산 최신 지역 가격·전세·거래량의 공식 PDF는 현재 parser로 처리하지 못해 수치를 대체하지 않았다. 이 실패·미확인과 Gold 수요·Crypto 세부 흐름 부족은 조사 결과의 일부다.

[첫 연구 초안](draft_capture/README.md), [비교 참조 보완 전 판본](draft_capture/comparison_review/README.md), [현금 표현 검토 전 판본](draft_capture/wording_review/README.md)은 문장 검토 과정의 보존 기록이다. 최종 해석은 상위 report와 review를 따른다. 원자료·계산·정보 기준 시각을 유지하면서 지원되지 않는 재고 감소 표현과 모호한 기간·비교 참조·상품 이자 표현을 수정했다.

기존 134개를 유지한 **159개 테스트**와 인터넷 차단 replay·근거 참조를 검증했다. 구현 계약과 경제적 의미 검토의 한계는 [Opportunity Map 안내](../../docs/opportunity-map.md)에 정리했다.
