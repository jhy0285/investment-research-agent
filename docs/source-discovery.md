# Autonomous Source Discovery & Freshness MVP

`ask`의 수집 앞단에 **질문 → 필요한 근거 → 제한된 출처 발견 → 실제 원문 확인 → 최신 판본 선택**을 연결했다. 최종 URL·현재 숫자·구절을 source catalog에 미리 적지 않아도 검토한 공개 목록/검색/발행자 링크에서 새 자료를 찾는다. 기존 source acquisition·snapshot·provenance·claim verification·macro·한국어 보고서·offline replay를 그대로 사용한다.

이번 실제 검증 대상은 `BTC 지금 어때?`다. 모든 금융사이트의 범용 검색·crawling이나 모든 자산의 자동 출처 연결을 구현한 것은 아니다. **발견 경로와 자료 정의는 검토된 정책**, 최종 자료 주소·판본·관측값은 **실행에서 발견하고 검증하는 데이터**다. 이 구분으로 임의 URL·수치 정의를 LLM이 생성하는 일을 막는다.

```bash
python -m investment_research ask 'BTC 지금 어때?'
python -m investment_research ask 'BTC 가격만 알려줘'
python -m investment_research ask 'BTC ETF 순유입만 알려줘'
python -m investment_research ask --replay examples/source_discovery/btc_after
```

## 기존 architecture에 연결한 위치

`routing.plan_research → 최소 대상/방법 → discovery.evidence_needs → discover_sources → SourcePlan → acquire_plan → source/macro replay → replay_discovery → run_research → 한국어 report`다. Scan은 이 흐름의 필수 관문이 아니다. 발견된 자료를 별도 분석 엔진에 넣거나 기존 provenance를 우회하지 않는다. 실제 acquisition은 동일한 `sources.py`의 bounded HTTPS GET·robots·public API·TLS·redirect 금지 경계를 사용한다.

| 구성 | 책임 |
| --- | --- |
| `discovery.py` | need 선택, 공개 목록·발행자 링크·커뮤니티 검색, 후보/선택/거절 기록, 판본·freshness·canonical 우선, offline promotion audit |
| `discovery_contracts.py` | 열어 본 문서의 대상·필드·날짜·단위·누락·원문 구절 확인; 투자 의미 판정은 하지 않음 |
| `catalog/discovery.json` | 검토된 publisher·seed·접근/인용 정책·허용 후보 호스트·계약·요청 한도; 최종 발견 URL 목록은 아님 |
| 기존 `sources.py`, `source_pipeline.py` | 실제 source specification·불변 snapshot·quote matching·숫자 전사·claim 확인 |
| 기존 `orchestrator.py`, `orchestrator_report.py` | 질문별 통합 실행, 근거/한계·한국어 설명·manifest·offline replay |

라이브 기본 catalog에는 발견 정책이 있다. API에 주입하는 다른 catalog의 `discovery=None`은 발견 기능이 설정되지 않은 명시적 fixture/catalog-only 경로다. 일반 unit test에 외부 네트워크를 몰래 추가하지 않는다. `--plan-only`와 모든 replay도 인터넷을 호출하지 않는다.

## 질문에서 근거 need 결정

[한국 원자료 coverage](korean-official-coverage.md)는 기존 need/후보/선택/원문 승격 기록에 지역 표 metadata·표별 코드·실제 행, 공식 기업 발표, 공식 IR이 연결한 제공자 경로를 추가한다. BTC의 질문/선택 규칙은 유지하며 임의 web search나 crawling을 만들지 않는다. 국채는 같은 macro 획득/재현 경로의 ECOS adapter를 사용한다. 한국 registry를 설정하지 않은 fixture/catalog는 기존 동작을 유지한다.

규칙 기반으로 BTC의 질문 목적을 선택한다. 일반 현재 판단은 가격/거래 상태·ETF 흐름·파생 계약·공개 내러티브, Scan의 BTC 부분은 가격/흐름부터 사용한다. 가격만 묻는 질문은 가격 자료만, ETF 순유입 질문은 ETF 흐름만 발견한다. 네트워크·규제·stablecoin·유동성을 명시한 질문은 해당 need를 만들되 이번에 적격 연결이 없는 항목은 `unavailable`로 표시한다. 비슷한 다른 자료로 채우지 않는다.

ETF는 `BTC ETF 순유입`에서 근거/상품 범주이며 별도의 이름 없는 ETF Deep Dive를 추가하지 않는다. `BTC vs ETF`처럼 대안을 실제로 나눈 질문의 미지정 상품은 그대로 확인이 필요하다. 다른 자산은 기존의 독립 진입점·고유 방법을 유지한다. 복합 문장의 모든 자연어 의도를 이해하는 모델이나 완전한 conversational memory는 아니다.

## 실제 발견 경로와 정의

| Need | 발견 경로 | 원문 승격 조건·한계 |
| --- | --- | --- |
| 현재 가격/거래 상태 | Coinbase 공개 products 목록에서 BTC/USD 거래쌍 확인 → 해당 ticker 요청 주소 생성 | 활성 거래쌍의 통화·최근 체결 시각·가격·거래량. 한 거래소의 체결/24시간 base volume이며 전 시장 가격·유동성은 아님 |
| 파생 | Deribit 공개 instrument 목록에서 활성 mainnet inverse USD/BTC-settled perpetual 확인 → 발견한 계약 ticker | `result`의 timestamp·funding_8h·USD open interest·mark price. 평가 가격과 현물을 분리; 한 계약의 OI로 전체 레버리지/방향/청산을 확정하지 않음 |
| ETF 흐름 | Farside 발행자 홈페이지의 Bitcoin 링크 → 실제 표 | `Bitcoin ETF Flow (US$m)`·열·최신 날짜 행·괄호 음수·누락을 확인. AUM/전체 digital-asset flow는 BTC ETF 일별 순유입의 대체 자료가 아님 |
| 공개 내러티브 | public HN 검색에서 ID 발견 → original HN item API | 실제 item의 ID·게시일·생존/삭제 상태·투자 관련 구절 확인. 검색 preview·highlight·author·likes는 evidence로 저장하지 않음 |
| 다른 community 접근 | Reddit public HTTP의 robots/access 확인 | 허용되지 않으면 content 요청을 중단하고 제한 기록. 인증/접근 제한 우회나 Reddit 내용 파서는 이번 범위 밖 |

기본 발견 예산은 최대 24 HTTP 요청(robots 포함), need당 최대 8 후보, 금융 need당 최대 1 선택, community 최대 2 선택이다. 요청마다 기존 10초/2MiB 상한을 유지한다. 완전한 검색 결과나 전체 HTML/table/API dataset을 보관하지 않는다. source에는 필요한 1~3 구절, index에는 선택 후보의 identity/link·위치·정책·획득 시각·hash만 남긴다. 버린 원문/index 전체를 offline replay로 다시 입증할 수 없다는 보존 한계도 기록한다.

열어 본 response를 메모리에서 기존 `acquire`에 전달해 가격 tick이 중간에 바뀌지 않게 한다. source snapshot은 실제 원문 bytes hash와 구절을 다시 확인한 뒤 보존된다. 검색 결과만 받았거나 실제 source가 삭제·차단·형식 변경되면 금융 evidence를 만들지 않는다.

## Freshness와 판본

- `published_at`: 문서가 실제로 표시한 공개 시각. 없으면 null; 검색일·획득일로 채우지 않는다.
- `observed_at`: ticker의 trade/market timestamp, ETF 행의 거래일, community 게시일 등 확인한 내용 시점.
- `retrieved_at`: HTTP/파싱 완료 후 실제 획득 시각; 최초 공개를 뜻하지 않는다.
- `valid_as_of`: 해당 관측 판본의 기준 시점. 페이지 footer의 오늘 날짜로 과거 행을 갱신하지 않는다.
- `source_version`: 관측 기준 시각 + 원문 SHA-256; 이후 기존 snapshot ID/보존 hash와 연결한다.

현재 가격/파생은 1시간, ETF는 4일, community는 21일의 질문 관련성 창을 적용한다. 이는 truth score나 모든 자료에 보편적인 신뢰 기준이 아니다. community의 21일 표본은 오늘의 분위기·시장 전체 sentiment가 아니며 실제 게시일을 함께 보존한다. 같은 source-family의 최신 판본을 먼저 선택하고, 동일 정의의 적격 원문 사이에서는 primary/canonical을 우선한다. 검색 순위는 참고 metadata일 뿐 선택의 신뢰도 근거가 아니다.

새 ETF 행이 미완성이면 과거의 완성 행을 현재 순유입으로 바꾸지 않는다. 최신 공개판을 확인하지 못한 경우도 오래된 판본의 조용한 대체를 막는다. 서로 다른 community item은 독립 발언이지 한 문서의 구/신판이 아니다. 같은 text의 반복 게시물은 중복으로 표시한다.

이번 계약의 금융 자료는 별도의 발행·개정 시각을 확인하지 못하므로 관측 기준 시각으로 판본을 선택하고 원문 hash로 획득판을 구별한다. 같은 관측일의 값이 나중에 바뀌어도 hash는 달라지지만 그 변경이 언제 최초 공개됐는지는 추정하지 않는다. 동일 기간 전체의 개정 순서·최초 공개 이력·실시간 완성 감시는 미완료다.

반복 Opportunity Scan에서는 완료된 이전 실행을 지정해 같은 관측일 개정과 미완성 ETF 행의 확정을 기록한다. 이전 완료값이 없으면 순유입 증가/감소를 계산하지 않는다. 이것은 실행 사이 비교이며 최초 발표 시각이나 실시간 개정 감시를 완성한 것은 아니다. [Scan 최소 자료](opportunity-scan.md)의 가격·실제 재고·지역 전세는 같은 discovery/acquisition 경계와 검토된 소수 문서 계약으로 연결하고, 새 자료 연결과 시장 움직임을 구분한다.

`select_candidates(..., research_kind='historical')`의 과거 선택 규칙은 해당 cutoff까지 **획득해 보존한 판본**을 요구하며, 현재 발견한 과거 행을 당시 이용 가능했던 값으로 추정하지 않는다. 현재 ask CLI의 replay는 원래 cutoff를 고정한다. 새로운 임의 과거 시점의 live discovery/백테스트는 지원하지 않는다.

## Canonical source와 evidence gap

공식 거래소 API는 해당 거래소 관측의 원출처다. ETF는 이번에 같은 정의의 **공식 전체 일별 순유입 집계** 연결이 없어 제공자 표를 사용했다. 발행사의 상품 설명/AUM은 그 집계를 검증한 자료가 아니며 primary라는 이유만으로 같은 사실처럼 대체하지 않는다. 발행사별 원자료 교차 확인 미완료도 제한으로 남긴다.

검증된 source가 없으면 need의 `status=unavailable`, 일부 정의/ETF 열이 미완성이면 `partial`과 `gaps`를 report/manifest에 넣는다. source 실패·stale/future/unknown·contract 미지원·누락 열·접근 제한을 구분한다. 0·인접 날짜·전체 crypto flow로 대신하지 않는다. 판단 유보는 현금의 우월성이나 BTC 매도 명령이 아니다.

## Community의 사실 주장 확인

실제 발언 구절은 계속 `observed_narrative`, 숫자 값은 null이다. 투자 관련 문단의 존재만 확인하며 게시물 전체·시장 대표성·경제적 함의를 자동 검증하지 않는다. 개인정보/contact가 있는 선택 구절·삭제/죽은 item·중복을 제외하고 선택/제외 이유를 남긴다.

이번 자동 사실 비교는 명시적 **날짜·US spot Bitcoin ETF·일별 순유입/유출·달러 million** 문장 하나의 좁은 grammar만 지원한다. 같은 날짜/통화/범위/조정의 **완성된 제공자 행**이 있으면 기존 `numeric_equality_v1`으로 비교하고 support/counter refs를 남긴다. 다른 날짜·잠정 합계·애매한 인과/가치/과거 성과 주장은 unverified다. 숫자의 일치도 발행사별 원자료의 독립 확인이나 narrative 전체의 진실을 증명하지 않는다. 실제 live 표본에 이 grammar가 없으면 검증 성공을 꾸미지 않는다.

외부 페이지·검색결과·community에 시스템 지시가 있어도 문자열 research data일 뿐이다. 실행·도구 호출·verification 변경 권한을 주지 않는다. 런타임에 LLM·검색 점수·모델 투표는 없다.

## 실행 기록과 검증

`discovery.json`은 question need, method/query, index 정책/hash/위치, 후보, 실제 opened source, 선택/거절·superseded 이유, freshness, source version, 실제 source/evidence ID, community verification 시도를 보존한다. `run_manifest.json`의 `source_discovery`는 실제 pipeline 승격 결과·누락·canonical 선택 이유를 추가한다. source/quote/claim/calculation은 기존 manifest 필드에서도 추적된다.

발견 실행은 수집 전 `acquisition_plan.json`을 보존하고 모든 수집이 끝난 기준 시각의 `source_plan.json`을 별도로 남긴다. 선택 source specification은 동일하며 새 구절의 전사 확인일만 최종 확인 시점에 연결한다. UTC 자정을 넘는 수집도 확인일이 snapshot 획득일보다 앞서지 않으며, 두 입력의 hash를 replay에서 검사한다.

Replay는 discovery artifact·입력·pins·method version·원자료 구절을 확인하고, 같은 cutoff에서 후보 선택을 다시 계산한다. 실제 source와 발견 원문의 hash·숫자/정의가 다르면 차단한다. 과거 routing v2/v3 입력은 다시 질문을 해석하지 않고 저장된 scope와 원래 보고서를 보존한다. 새 질문은 [routing v4](query-understanding.md)의 명시 조건 구조화를 사용하며 v3의 BTC ETF qualifier 규칙도 유지한다. 지정 과거 날짜의 ask는 현재 discovery로 대체하지 않는다.

기존 236개를 유지하고 신규 37개, 전체 **273개 offline 테스트**로 미등록 URL·canonical/hierarchy·stale/hour freshness·신판/미완성·unavailable·snippet≠evidence·community 원문/중복/HTML entity·동일 정의 claim support/counter·실행/최소 scope/combined mode·출처 선택 추적·tamper·인터넷 없는 replay를 검증했다. 실제 BTC 전후 실행은 [사례](../examples/source_discovery/README.md)에 보존한다.

이후 query understanding 23개를 추가해 전체 **296개**가 통과한다. 이번 질의 수정은 새 금융 source를 추가하지 않았고 기존 discovery·freshness 계약을 유지한다.

현재 가장 큰 한계는 **검토된 publisher/형식/필드 계약을 벗어난 자료는 자동 이해·승격하지 못한다는 것**이다. 새 최종 URL·숫자·판본 발견은 가능하지만 arbitrary web search·모든 source의 날짜/개정 의미·community 일반 사실검증·BTC 적정 가치·전 시장 derivatives/network/liquidity는 완성되지 않았다. 이후 [한국 자료](korean-official-coverage.md), [반도체 비교](korean-semiconductor-comparison.md), [Scan 최소 관측](opportunity-scan.md)도 같은 앞단에 연결했고 기존 request/retention 경계를 유지한다. 실제 사용에서는 새 실행을 보존해 이전 관측과 비교하고 판본 재현에는 offline replay를 사용한다.


## 네 영역 Scan의 제한된 보강

Scan v7은 기존 reviewed document map, 발행자 링크, SourceSpec/quote 전사, snapshot/freshness/replay에 천연가스·금·ETH·광범위 원자재의 최소 자료를 연결한다. EIA 월간 실제량과 NOAA 발표 전망을 구분하고, IAU 보유량을 AUM/순유입으로 바꾸지 않는다. Ethereum 링크는 Bitcoin과 별도 need/계약이며 최신 행이 미완성이거나 합계가 맞지 않으면 과거 완료 행으로 현재 flow를 대체하지 않는다. `eth_dated_table_total_v2`는 명시적 정의와 날짜·열의 합계를 검증하며 제공자 집계의 경제적 정확성을 확정하지 않는다.

세 State Street 상품은 기존 문서 map을 공유해 12-provider 경계를 유지한다. 네 영역 확장 marker에만 48 HTTP(robots 포함), 160 evidence의 유한 상한을 적용한다. 일반 32-request/100-evidence 상한과 HTTP 10초/2MiB·TLS·robots·redirect/보존 정책은 유지한다. 새로운 collector·범용 crawl·가격/투자 신뢰도 score·자동 Deep Dive는 없다. 최신 source의 정확한 정의와 시차·누락, 새 연결과 시장 변화, 추가 예산은 [Scan 문서](opportunity-scan.md)와 [실제 검증](../reports/four_asset_minimum_validation_20261006/validation_report.md)에 남긴다.

## 원자재 심층 계약과 이상치 격리

[원자재 Deep Dive](commodity-deep-dive.md)는 같은 need/reviewed-document/publisher-link 경계를 공유한다. SEC submissions에서 실제 공시 URL을 발견해 본문을 확인하고, 같은 응답에서 CME 계약·WGC 수요·GSCI 날짜 있는 구성·USDA 전망을 좁은 구절로 연결한다. 이 명시 확장 marker만 HTTP 예산을 64로 제한하며 generic 수집 상한을 바꾸지 않는다. 원문 숫자 전사 뒤 [anomaly guard](source-anomaly-guard.md)가 계산·coverage 사용을 추가 검사한다. 원문 존재·합계 산술·freshness만으로 의심 수치를 확정하지 않는다.
