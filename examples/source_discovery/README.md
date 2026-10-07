# 실제 BTC source discovery 전후 검증

동일한 자연어 질문 **`BTC 지금 어때?`**를 개선 전 코드와 개선 후 코드로 각각 실제 실행했다. 둘 다 Bitcoin 직접 조사이며 Opportunity Scan·다른 자산 조사·매매·개인 비중 계산을 추가하지 않았다. 합성 시장 데이터가 아니다.

| 실행 | 실제 수집 기준 시각 | 보고서·기록 |
| --- | --- | --- |
| 개선 전 | 2026-10-04 15:24:37 UTC / 2026-10-05 00:24:37 한국시간 | [한국어 보고서](btc_before/report.md) · [manifest](btc_before/run_manifest.json) |
| 개선 후 | 2026-10-04 16:50:22 UTC / 2026-10-05 01:50:22 한국시간 | [한국어 보고서](btc_after/report.md) · [manifest](btc_after/run_manifest.json) · [출처 선택 기록](btc_after/discovery.json) |

개선 전 실행은 변경을 시작하기 전에 확보했고 파일을 그대로 보존했다. 각 manifest의 `code_sha256`·method version·cutoff·report/artifact hash가 실제 생성 버전을 기록한다. 두 시점의 비교는 **근거 범위·최신성·추적 가능성의 개선**이며 가격 수익률이나 투자 성과 검증이 아니다. 요약 수치와 새 URL의 catalog 미등록 여부는 [comparison.json](comparison.json)에서 추적한다.

## 질문에 필요한 근거가 어떻게 달라졌나

| 범위 | 개선 전 | 개선 후 |
| --- | --- | --- |
| 가격·거래 상태 | 현재 BTC 숫자 없음 | Coinbase BTC/USD 실제 최근 체결·24시간 BTC 수량 기준 거래량 |
| BTC 현물 ETF 흐름 | 전체 digital-asset 흐름은 BTC 일별 순유입의 대체 자료가 아님 | Farside의 최신 10월 2일 행 발견. IBIT 누락으로 **잠정 합계만 확인**, 전체 확정 순유입 미확보 |
| 파생 | 직접 자료 없음 | Deribit의 활성 BTC 무기한 계약 funding_8h·USD 미결제약정·평가 가격 |
| 공개 토론 | 미리 적은 두 구절 | 검색에서 후보를 찾고 original API로 실제 item·구절·게시 시점 확인. 선택한 두 발언의 사실 함의는 미확인 |
| 추적 기록 | 사용한 source·quote·claim·계산 | 기존 기록에 need·후보·선택/제외·발견 목록 hash·판본·freshness·gap 추가 |
| 사용 근거 | 9개 | 13개 |

SourceSpec은 5개에서 7개로 늘었고 claim은 12개에서 11개로 바뀌었다. 이것을 독립 출처·강한 결론 증가로 해석하지 않는다. 불필요한 전체 crypto 흐름과 고정 community 구절을 BTC 현재 조사에서 제외했고, 숫자 전사를 투자 가설의 지지 근거로 자동 연결하지 않았다. 두 실행 모두 현재 가격의 매력을 확정하기에는 근거가 부족한 `partial` 연구 결과다.

## 미리 최종 URL을 등록하지 않고 실제 발견한 자료

1. [Coinbase BTC/USD ticker](https://api.exchange.coinbase.com/products/BTC-USD/ticker): 공식 products 목록에서 활성 BTC/USD identity를 확인한 뒤 연결했다. 실제 관측 가격은 **85,409.98 USD/BTC**, 거래 시각은 2026-10-04 16:50:09.911158 UTC다. 한 거래소 관측이며 전 시장 대표 가격이 아니다.
2. [Deribit BTC-PERPETUAL ticker](https://www.deribit.com/api/v2/public/ticker?instrument_name=BTC-PERPETUAL): 공식 instrument 목록에서 활성 mainnet inverse USD/BTC-settled 계약을 확인했다. 시각은 16:50:15.970 UTC, funding_8h는 **0.00000382 비율**, 미결제약정은 **796,721,140 USD**다. 연율·미래 수익률·전체 시장 레버리지로 해석하지 않는다.
3. [Farside Bitcoin ETF 표](https://farside.co.uk/btc/): 미리 지정한 최종 표 URL 대신 발행자 홈페이지의 링크에서 찾았다. 2026-10-02 최신 행의 **31.7백만 달러는 IBIT 값이 없는 잠정 합계**다. 과거 완성 행으로 대신하거나 0을 채우지 않았다. 발행사별 원자료 교차 확인은 미완료다.
4. [HN 공개 발언 49851823](https://news.ycombinator.com/item?id=49851823): public 검색에서 새 ID를 찾고 [original item API](https://hacker-news.firebaseio.com/v0/item/49851823.json)를 열었다. 9월 26일의 토지 투자와 Bitcoin 희소성 비교 문단이다. 검색 snippet을 원문 구절로 사용하지 않았다.

위 네 최종 요청 URL은 기존 source catalog에 없었다. 두 번째 community item [49785002](https://news.ycombinator.com/item?id=49785002)는 9월 21일의 MtGox 보관/인출 위험 비유이며 기존 catalog에도 있었다. 이번에는 검색에서 다시 발견했으므로 모든 선택 URL이 새 URL이라고 주장하지 않는다. 이 목적 표집은 21일 관련성 창의 소수 발언이지 오늘의 BTC 강세/약세 비율이나 시장 전체 sentiment가 아니다. Reddit은 robots 제한을 확인한 뒤 content 요청을 중단했다.

발견 단계에서 18개 HTTP 요청(robots 포함)으로 12개 후보를 확인하고 5개 발견 source를 선택했다. 기존 IBIT 상품 설명·관련 환율 자료의 수집은 이 발견 요청 수에 포함되지 않으며, 모두 기존 evidence pipeline으로 이어졌다. 선택 source는 모두 `available`이었지만 **자료의 접근 성공과 ETF 행 완성·가격 매력 검증은 다른 상태**다. 완성된 ETF 수치와 같은 날짜/정의의 community 숫자 주장만 자동 비교할 수 있으며 실제 두 발언은 그러한 문장이 없어 `unverified`로 남았다.

## 인터넷 없이 재현

```bash
python -m investment_research ask --replay examples/source_discovery/btc_before
python -m investment_research ask --replay examples/source_discovery/btc_after
```

원래 cutoff·scope·source 판본으로 replay한다. 날짜를 현재로 바꾸거나 새 시장 판단으로 게시하지 않는다. 원자료 전체는 보관하지 않고 필요한 구절·필드·정의·hash만 보존하므로 버린 원문 전체를 재구성할 수는 없다.

HTTP/DNS와 live discovery를 차단한 상태에서 전후 두 실행 및 기존 다섯 ask 예제의 보고서·digest·artifact가 동일하게 재현됐다. 기존 예제 파일 **341개가 모두 변경 없이 보존**됐다. 기존 236개와 신규 37개, 전체 **273개 offline 테스트**가 통과한다.

## 현재 한계

발견 정책·공개 목록·검토된 문서/필드 계약 안에서 새 URL·값·판본을 찾는다. 임의 사이트의 의미를 자동 이해하거나 BTC 적정 가치·전 시장 leverage·network·liquidity를 검증하는 시스템은 아니다. 현재 가격 관측이 추가되어도 좋은 투자 가격이라는 결론을 자동 만들지 않는다. 전체 실행 경계는 [설계 안내](../../docs/source-discovery.md), 다음 단일 제안은 [로드맵](../../docs/roadmap.md#다음-codex-task-제안)을 따른다.
