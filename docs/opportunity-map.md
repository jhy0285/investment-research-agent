# 실제 Cross-Asset Opportunity Map

이 경로는 [네 독립 진입점](research-modes.md) 중 Opportunity Scan의 현재 구현 사례다. 다른 Deep Dive·Compare·Portfolio Review의 필수 선행 단계가 아니며, 지도에 없는 자산·전략도 직접 조사할 수 있다.

이 경로는 한국 거주 개인 투자자가 현재 무엇을 더 조사해야 하는지 파악하도록, 저장한 실제 공개 자료와 기존 거시 시계열을 자산 간 조사 지도에 연결한다. 가격·수익률 표를 늘리는 것이 아니라 현금, 채권, 주식, 실물자산, 암호화폐, 한국 주택의 조사 이유·반대 논리·기회비용·미확인 조건을 한 문서에서 보여 준다.

결과는 **연구 초안**이다. 후속 조사 후보는 매수 추천이나 상대 수익률 순위가 아니며, 검토된 자산배분·목표비중·자동매매 결과를 만들지 않는다. 공개 발언과 기관 발표의 존재 확인, 재현 가능한 계산, 경제적 의미에 대한 사람의 검토를 구분한다.

## 이번 실제 조사

정보 기준 시각은 **2026-10-04 13:16:53.131802 한국시간**이며 UTC로는 `2026-10-04T04:16:53.131802+00:00`다. 이 기준은 실제 source 확보를 마친 뒤 정했고, 기존 거시 snapshot은 선택한 pins를 보존해 같은 기준 시각에서 재생했다.

| 고정 입력 | 확인 범위 |
| --- | --- |
| Opportunity source 계획 | 27개 출처: 26개 `available`, Reddit 1개 `policy_blocked`; 실제 연결 source Evidence 64개 |
| 기존 거시 계획 | 4개 출처와 원관측 Evidence 10개 |
| 통합 보고서 | 출처 31개, Evidence 74개, 기존 결정적 Metric 7개; 같은 원자료의 중복을 독립 증거로 세지 않음 |
| 후속 조사 후보 | 미국 주식, 한국 주식, 에너지의 세 영역; 투자 매력과 개인 적절성은 초안·미확인 |

미국 영역은 예상 이익 상향과 선행 배수의 변화에 더해 NVIDIA의 실제 매출 성장 공시를 확인했다. 같은 공시의 고객 결제조건과 매출채권 집중은 현금회수·성장 지속성을 더 검증할 이유다. 공급자의 실현 매출과 AI 구매자의 투자수익, 현재 주가의 적정성을 구분한다. NVIDIA 홈페이지의 자동 접근 제한을 우회하지 않고, 공개 접근을 허용하는 SEC 공시를 별도 원자료로 확보했다.

한국 영역은 반도체 수출·메모리 실적과 소비기기의 비용부담이 다른 방향을 보일 수 있다는 점, 에너지는 원유 공급 차질과 복구 전망을 함께 확인해야 한다는 점을 조사 질문으로 남겼다. 천연가스의 계절성·재고, 금의 직접 수요, BTC/ETH 개별 자금흐름, 한국 부동산의 현재 지역별 가격에 필요한 자료가 부족한 영역은 후보를 강제로 만들지 않았다. 상세 구절·기간·반대 논리는 실제 보고서에서 추적한다.

## 실행과 결과물

Python 3.12 이상과 표준 라이브러리만 필요하다. 저장소 루트에서 아래 명령으로 고정한 자료를 인터넷 없이 재생한다.

```bash
python -m investment_research opportunity replay examples/opportunity_map_case \
  --plan examples/opportunity_map_case \
  --store examples/opportunity_map_case/snapshots \
  --pins examples/opportunity_map_case/pins.json \
  --macro-plan examples/macro_case \
  --macro-store examples/macro_case/snapshots \
  --macro-pins examples/macro_case/pins.json
```

새 파일로 보고서와 실행 기록을 저장하려면 같은 명령에 출력 경로를 지정한다.

```bash
python -m investment_research opportunity replay examples/opportunity_map_case \
  --plan examples/opportunity_map_case \
  --store examples/opportunity_map_case/snapshots \
  --pins examples/opportunity_map_case/pins.json \
  --macro-plan examples/macro_case \
  --macro-store examples/macro_case/snapshots \
  --macro-pins examples/macro_case/pins.json \
  --output reports/opportunity_map.md \
  --manifest reports/opportunity_manifest.json
```

같은 입력·pins·기준 시각·방법·코드에서 같은 문서와 manifest를 만든다. 현재 시각이나 저장 디렉터리의 가장 새 파일을 자동 선택하지 않는다. 다른 내용이 있는 출력 파일은 덮어쓰지 않는다. 자료 부족과 정상적인 판단 유보는 실행 오류가 아니며, 형식·참조·체크섬 오류는 실패로 처리한다.

| 사례 파일 | 책임 |
| --- | --- |
| [사례 안내](../examples/opportunity_map_case/README.md) | 실제 조사 범위·권리·실행 결과 |
| [plan.json](../examples/opportunity_map_case/plan.json) | 명시한 자산 범위, SourceSpec, 구절 정의, 좁은 발표 사실의 확인 범위 |
| [pins.json](../examples/opportunity_map_case/pins.json) | 해당 source 명세와 선택한 immutable snapshot |
| [review.json](../examples/opportunity_map_case/review.json) | 사용자 맥락, 정확한 기준 시각, 자산별 비교와 조건부 해석 초안 |
| [opportunity_map.md](../examples/opportunity_map_case/opportunity_map.md) | 한국어 조사 지도, 후보·보류 이유, 원문·시점·한계 |
| [run_manifest.json](../examples/opportunity_map_case/run_manifest.json) | 코드·방법·입력·출력 해시, 실제 적용 우선순위, 누락·제외 진단과 거시 실행 기록 |

`fragments/`는 이번 조사를 나눠 진행할 때 작성한 자료 검토 메모다. 실행 입력은 plan·review·pins이며 fragment의 자유로운 메모를 자동 사실이나 투자 결론으로 승격하지 않는다.

## 연결 구조

`고정 source plan/pins + 고정 macro plan/pins + review.json → 기존 자료형과 연구 엔진 → 정형 한국어 보고서`로 연결한다. 별도 연구 엔진이나 범용 자율 에이전트 프레임워크를 도입하지 않았다.

| 파일 | 추가한 책임과 경계 |
| --- | --- |
| `investment_research/source_pipeline.py` | 선택적 `asset_ids`로 이번 계획의 대안을 명시한다. 생략한 기존 계획의 기본 범위와 계약은 유지한다. |
| `investment_research/opportunity.py` | 두 기존 replay 결과와 연구 초안을 기존 Source·Evidence·Claim·Alternative·OpportunityCost·Profile·ResearchBrief로 연결한다. 참조·범위·시점을 검사한다. |
| `investment_research/opportunity_report.py` | 연결된 원문·계산·해석 상태로 보고서를 생성한다. 금융 계산이나 자산 점수 산정을 하지 않는다. |
| `investment_research/__main__.py` | 명시적 `opportunity replay`와 출력 보호를 제공한다. 이 명령은 네트워크를 호출하지 않는다. |
| `tests/test_opportunity.py` | 합성 자료로 시점 누수·커뮤니티 채택·범위 유출·누락·재현 경계를 검사한다. 실제 시장 성공을 테스트 fixture로 대신하지 않는다. |

이 replay 명령은 네트워크를 사용하지 않는다. 수집은 기존 `sources acquire`·`macro acquire` 경계에 있으며, 현재 [기본 ask](research-orchestrator.md)는 질문 범위의 계획으로 같은 함수를 재사용한다. 접근·보존 경계는 [공개 출처 안내](source-acquisition.md), 원관측·판본·계산 경계는 [거시 안내](macro-mvrs.md)를 따른다. 고정 기회 지도는 수집기를 재구현하거나 새로운 검색·주문 권한을 추가하지 않는다.

## Broad Scan과 후속 조사

이번 사례는 현금, 단기 국채, 장기 국채, 미국 주식, 한국 주식, 성장주, 가치주, 배당주, 금, 기타 원자재, 에너지, 천연가스, Bitcoin, Ethereum, 한국 주택의 **15개 영역**을 조사 지도에 둔다. 성장·가치·배당은 겹치는 특성이며 서로 독립된 자산군으로 세지 않는다. ETF는 경제적 노출을 얻는 상품이므로 이번 자료에서도 해당 노출의 제한된 표본으로 사용하며 ETF 개수로 분산을 증명하지 않는다. 회사채는 공식 신용여건의 배경으로 조사했지만 독립적인 상품·만기별 비교 행은 만들지 않았다.

각 행은 경제적 노출·수익 정의·유동성을 구분하고 현재 상태, 긍정 단서, 반대 논리, 중요한 미확인, 다른 대안의 기회비용, 재조사 조건을 기록한다. 국채 시장금리·과거 기업실적·상품의 수익률 배수·임대수익률을 같은 미래 투자수익률로 순위화하지 않는다. 미래 기대수익·확률·최적 비중을 입력이 없는 상태에서 만들어 채우지 않는다.

| 조사 우선순위 | 뜻 |
| --- | --- |
| `candidate` | 현재 확인한 비커뮤니티 자료가 더 깊은 연구 질문을 제기한다. 투자 매력 확정이 아니다. |
| `monitor` | 필요한 조건이나 관측 변화를 기다리며 관찰한다. |
| `defer` | 이번 질문과 자료 범위에서 먼저 조사할 이유가 약하다. 자산 전체의 열등함을 뜻하지 않는다. |
| `insufficient` | 중요한 자료·시점·비교 조건이 부족하다. |

초안은 후보마다 왜 지금인지, 무엇이 변했는지, 흥미로운 근거, 가장 큰 반대 논리, 투자 thesis로 발전시키기 전에 확인할 질문을 요구한다. 후보 수에는 상한이 있고, 현재 적격 자료가 없는 후보는 자료 부족으로 낮춘다. 문장에 필요한 근거가 하나라도 채택 조건을 충족하지 못하면 해당 문장을 채택 보류로 표시한다. 후보의 경제적 의미를 자동 심사했다는 뜻은 아니다.

## Evidence와 해석

기관·기업이 전망이나 평가를 발표한 경우 확인 가능한 좁은 사실은 **해당 발표가 있었다**는 것이다. 미래 수요·실적·가격이 실제로 그렇게 변한다는 것은 별도 가설이다. 출처의 높은 위계·구절 일치·계산 재현성이 그 가설의 진실 점수가 되지는 않는다.

`review.json`의 시장 설명·자산별 조건부 해석은 항상 `draft`, 투자 의미 검토는 `pending`으로 보존한다. source plan의 좁은 원문 확인 상태와 합치지 않는다. 해석 문장의 금융 숫자를 직접 입력하는 대신 Evidence 또는 Metric을 참조하게 하고, 보고서는 보존 원문이나 기존 계산 결과를 통해 숫자를 보여 준다. 참조 존재 검사는 문장의 논리와 사실성을 자동 보증하지 않는다.

출처별 원문에는 measure·unit·period·currency·adjustment·scope 정의를 남긴다. 상품의 선행 이익 추정 기반 P/E는 실현 이익 P/E와 다르고, SEC yield·분배수익률·현금상품 계약금리·국채 시장금리도 서로 다르다. 서로 다른 정의를 하나의 현재 수익률 표로 합치지 않는다. 가격 지표를 확인하더라도 기대이익의 분모·추정치 개정·현금흐름·실행 조건을 더 검토해야 한다.

예정 공급은 착공·입주 실적이 아니고, 회사의 지난 분기 설명은 시장 전체의 현재 실적을 대신하지 않는다. 공개·관측·획득 시점과 해당 설명의 범위를 유지한다. 데이터가 상충하는 경우와 투자 논리 사이의 긴장, 확인 자료가 없는 경우를 구분하며, 누락을 반증으로 표현하지 않는다.

## 정확한 기준 시각과 UNKNOWN

기준 시각은 `review.json`의 timezone을 포함한 timestamp다. 한국시간과 UTC를 함께 표시하고, 그 시각 이후에 획득한 source·거시 관측은 현재 근거에서 제외한다. 기존 거시 pins는 별도 입력으로 고정하며 이번에 더 늦은 공개 자료를 조사했다는 이유로 기존 거시 판본을 덮어쓰지 않는다.

공개일이 unknown인 현재 발행사 페이지라도 페이지에서 **관측 기준일**을 확인한 경우에는 해당 판본을 실제 획득한 뒤의 기준 시각에서만 그 명시된 관측을 인용할 수 있다. 이를 최초 공개일이나 당시 투자자가 알 수 있었던 값의 증명으로 사용하지 않는다. 공개·관측일이 모두 없는 페이지는 획득만으로 최신 사실이 되지 않는다. 출처별 freshness 검토창은 자료의 용도별 설정이며 진실성·예측력의 점수가 아니다.

| 상태 | 출력에서 보존하는 의미 |
| --- | --- |
| `MISSING` / 자료 부족 | 필요한 출처·구절·계산 입력을 확보하지 못했거나 현재 파서가 지원하지 않음 |
| `PENDING` / 검토 대기 | 원문을 확보했어도 투자상의 해석을 사람이 검토 완료하지 않음 |
| `UNKNOWN` / 미확인 | 날짜·개정·상품조건·사용자 입력이 알려지지 않음 |
| stale / future / unavailable | 해당 기준 시각의 현재 근거로 채택하지 않음; 원자료와 제외 이유는 보존 |

최신 주간 주택 통계의 공표 사실을 확인해도 첨부 PDF의 전국·수도권·서울 가격·전세 수치를 읽지 못했다면 지역 가격 상태는 부족으로 남긴다. 전국 평균을 개별 주택·동네의 매력으로 복사하지 않는다. 금의 직접 수급과 투자상품 비용, 암호화폐의 최신 자산별 자금흐름 등을 확인하지 못했다면 다른 자산의 지표로 대신 확정하지 않는다.

## Community와 표본 의존

공개 게시물은 사람들이 무엇을 중요하게 생각하는지, 어떤 위험과 서사가 등장하는지 파악하는 단서다. fresh 상태와 구절 일치는 **발언의 존재**에 한정되며 금융 내용의 검증 상태가 아니다. 커뮤니티만으로 후보를 채택하거나 가격 전망·수익률·시장 전체 sentiment를 확정하지 않는다.

각 발언의 주제·시점·게시물 범위·검증할 공식 질문을 기록한다. 낙관과 비관을 함께 살펴보되 선택한 표본이 대표성을 갖는다고 주장하지 않는다. 같은 Hacker News thread의 발언은 공통 논의에 의존하고, 반복된 발언이나 같은 원자료의 미러는 독립 증거가 아니다. 이번 사례의 Fed 시계열 중복, FactSet과 상품자료의 관계, SPDR 상품 표본 및 커뮤니티 공통 thread도 숨기지 않는다.

지원·반대 참조를 유지하고, 중요한 하위 출처 주장은 가능한 공식 자료와 대조한다. 접근이 막힌 community를 몰래 다른 endpoint로 우회하거나 존재하지 않는 발언을 만들지 않는다. 이번 정형 경로는 누락된 반대 자료를 자동으로 검색·발견하지 않으므로 독립적인 후속 확인이 필요하다.

## 한국 투자자와 권리 경계

시장 조사 우선순위와 현재 사용자의 적절성을 구분한다. KRW 생활비·주택 필요자금과 외화 노출의 관계, 주택 매입의 자기자금·상환·유동성, 미국·한국의 같은 산업 위험을 함께 조사할 필요를 설명한다. 보유자산·부채·월 추가 투자액·큰 자금수요·실제 손실 감당 능력이 unknown이면 배분·차입·세후 개인 적합성 결론을 제한한다. 나이와 장기 보유 의향에서 비중이나 레버리지 허용을 자동 도출하지 않는다.

환헤지, 환전 비용, 과세, ISA·연금 등 계좌 조건은 확인된 범위에서만 다룬다. 실제 계좌·상품·매매 시점이 없는데 원화 실현수익이나 세후 순위를 계산하지 않는다. 국채 기준수익률을 예금 보장수익률로 표현하거나 외화 현금을 KRW 의무지출과 동일한 자산으로 취급하지 않는다.

각 SourceSpec에 공개 접근 및 보존 정책 URL·검토 메모를 둔다. 제한된 개인 연구 workspace에서 짧은 원문을 보관할 수 있다는 조건이 보고서 전체의 공개·상업적 재배포 권리를 확정한 것은 아니다. 출처·저작권·비상업 조건 등을 보존하고, 기관 정책이 제한한 자료·이미지·영상·연락처·개인 식별자와 전체 community 원문을 저장하지 않는다. 접근 허용과 저장·재배포 허가는 별개다. 실제 사례의 권리 검토 범위는 사례 안내와 source별 정책 기록에서 확인한다.

## 검증과 다음 연구

Opportunity Map 완료 당시 **159개 테스트가 통과**했다. 기존 134개를 유지하고 합성 오프라인 경계 테스트 25개를 추가했다. 실제 수집 결과는 위 고정 사례의 snapshot에 보존하며, 테스트 fixture에 실제 시장 근거를 대신 넣지 않았다. 현재 전체 검증은 [README](../README.md), Deep Dive의 방법 경계는 [해당 안내](us-equity-deep-dive.md)에 둔다.

```bash
python -m unittest discover -v
```

검증은 기존 경로의 출력·계약을 유지하면서, 정확한 획득 시각 이후 선택, 미래·stale·unknown 자료 보류, current 날짜를 가진 발행사 관측과 publication unknown의 구분, 커뮤니티만으로 후보 생성 금지, 누락 참조·자산 범위 유출, 초안 금융 숫자의 직접 입력, 체크섬·오프라인 재현·출력 보호를 검사한다. 합성 fixture는 실제 시장 근거가 아니며, 라이브 웹사이트 성공과 사람의 경제적 의미 검토를 테스트 통과로 대신하지 않는다.

이 고정 조사 지도에서는 **미국 주식 예상 PER의 분모 검증과 국채 대안 비교**를 한 후속 과제로 제안했다. 이후 [실제 Deep Dive](us-equity-deep-dive.md)로 조사했으며 기존 지도·원자료·판단 시점은 수정하지 않았다. EPS 상향·실적 질·AI 투자와 Treasury의 기회비용을 연결하되 가격·KRW·상품·개인 조건의 미확인 범위는 유보한다. 현재 제안하는 다음 질문은 [로드맵의 단일 Deep Dive](roadmap.md#다음-codex-task-제안)다.

## 자연어 Opportunity Scan의 조건부 후보

[Opportunity Scan 안내](opportunity-scan.md)에 새 넓은 질문의 15영역 최소 조사, 근거 기반 연구 후보, 쉬운 한국어 본문과 상세 부록, 저장된 후보 후속 참조를 설명한다. 기존 고정 map·과거 실행·독립 Deep Dive/Compare/Portfolio Review는 유지한다. 후보는 매수나 미래 수익률 순위가 아니며, 원자료 전사·경제적 해석·개인 적절성의 상태를 구분한다.
