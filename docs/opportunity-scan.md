# 전체 투자판 조사와 반복 관측

`ask '지금 전체 투자판에서 내가 볼 만한 기회 찾아줘.'`는 기존 질문 해석으로 Opportunity Scan을 선택한다. 기존 discovery → source/macro acquisition → provenance/freshness/claim 검증 → 설명용 계산 → Opportunity Map → 한국어 shortlist를 재사용한다. Deep Dive·Compare·Portfolio Review는 독립 진입점이며 좁은 질문에 Scan을 추가하지 않는다.

## 최소 자료와 투자 매력의 분리

15개 조사 영역은 현금, 한국 국고채, 미국 단기/장기 국채, 미국/한국 주식, 성장·AI·반도체, 가치·배당, BTC, ETH, 금, 광범위 원자재, 원유, 천연가스, 서울·경기·인천 아파트다. 테마와 전략은 주식과 겹치는 노출이며 독립 분산으로 세지 않는다.

[scan_coverage.py](../investment_research/scan_coverage.py)의 `STANDARDS`는 Scan 참여에 필요한 최소 의사결정 입력을 정의한다. 완전한 Deep Dive 요건이나 투자 매력 점수가 아니다. 같은 관측을 여러 범주에 설명할 수 있어도 독립 증거 여러 개로 세지 않는다.

| 자산군 | 최소 evidence | 핵심 누락의 영향 |
| --- | --- | --- |
| 주식·지수·주식 전략 | 현재 가격/대표 valuation, 실제 이익 변화/명확한 전망, 같은 정의의 가격·배수·전망 변화, 촉매와 반대 논리 | 가격이나 이익이 없으면 현재 가격의 투자 우위 유보. 독립적인 사업 개선·반대 근거가 있으면 조건부 연구 후보 가능 |
| 국채 | 국가·통화·만기가 명확한 현재 yield, 같은 만기의 최근 변화, 해당 국가 물가/정책 | 다른 국가/만기로 대체하지 않음. 시작 금리는 비교 기준이며 단독 기회 선정 조건 아님 |
| BTC·ETH | 거래소·통화가 명확한 가격, 의미 있는 기간의 동일 시장 흐름, 자산별 기관/ETF 흐름, 유동성 또는 레버리지 관측, 보유 논리와 downside | 기관 흐름 누락을 다른 crypto/미완성 행/영으로 채우지 않음. 한 거래소 거래량은 전 시장 레버리지 아님 |
| 금 | 금 기준가격, 동일 기준 기간 변화, 실질금리, ETF 보유/중앙은행/실물 수요 중 하나 | GLD NAV를 금 가격으로, AUM을 순유입/수요 증가로 대체하지 않음. 수요 미확보는 결론 제한 |
| 원유 | 현재 가격, 실제 재고/생산/수요, 선물구조 또는 실제 실물 수급 변화 | 실제 주간 재고 변화는 최소 수급 신호로 가능. 선물 투자상품의 기대수익·계절성 없는 잉여까지 확정하지 않음 |
| 천연가스 | 현재 가격, 실제 재고, 실제 생산, 날씨/수요, 명시한 계절 기준, 실제 LNG 수출 | 월간/주간/전망을 보존. 자체 계절 기준은 EIA 공식 보간 평균과 구분. 곡선·평년 주입 속도·상품 비용은 추가 gap |
| 광범위 원자재 | 대표 상품 가격, 하위 그룹 구성/비중, 정의가 명확한 흐름, 복수 하위 그룹의 수급 단서 | 원유만으로 전체를 대표하지 않음. 비중이나 산업금속/농산물 수급이 없으면 영향 범위를 제한 |
| 지역 부동산 | 서울·경기·인천 각각의 가격 변화, 거래량, 전세/임대 변화, 국내 금융비용 | 다른 지역·조사/실거래지수를 섞지 않음. 대출 평균금리는 개별 주담대 조건 아님 |
| 현금 | 접근 가능한 KRW 단기 수익률 또는 정의가 명확한 benchmark | 개인 예금/MMF 세후금리·보호·출금 조건을 benchmark에서 추정하지 않음 |

각 슬롯에는 `available/missing`, 관련 evidence ID, 핵심 여부, 누락이 제한하는 판단을 남긴다.

- `sufficient_for_scan`: 해당 최소 슬롯을 확인했다. 투자할 만하다는 뜻은 아니다.
- `partial_but_usable`: 관련 있는 복수 입력과 핵심 관측 또는 명시적 사업 가설이 있어 제한적으로 검토 가능하다. 중요한 누락과 조건을 공개한다.
- `insufficient`: 최소 경제적 질문 자체를 평가할 핵심 자료가 부족하다. `not_assessed_due_to_gap`으로 남기며 매력 부족으로 판정하지 않는다.

`coverage_status`, `investment_assessment`, `candidate_eligible`, `selected`는 별도 필드다. source 수·숫자 수·coverage 충족 개수를 우선순위로 더하지 않는다. 실제 경제적 조사 질문이 있어야 후보가 된다. 후보는 최대 네 개이고 빈자리를 채우지 않는다. 자료가 충분한 원유나 부동산도 서로 엇갈린 신호 때문에 관찰 상태로 남을 수 있다.

## 작은 원자료 연결

[scan_minimum.py](../investment_research/scan_minimum.py)는 기존 discovery의 검토된 문서/표 계약을 사용한다. 새로운 수집 엔진·범용 crawler·LLM truth 판정은 없다.

| source | 제한된 입력과 정의 |
| --- | --- |
| Coinbase Exchange | BTC-USD·ETH-USD 최근 여덟 UTC 일봉 요청. 완료된 연속 여덟 봉을 검사하고 일곱 날 전/최신 종가와 최신 하루 base 거래량만 보존 |
| State Street | SPYG·SPYV 같은 날 FY1 가중 조화평균 P/E. SPYV의 과거 분배율을 해당 포트폴리오에 연결. GLD 페이지의 **LBMA PM 기준가격**과 월말 benchmark 변화 |
| Fed H.15 | 현재 십년 TIPS 실질금리의 두 관측. 금 가격 월간 변화와 일간 금리 변화를 동시 변화처럼 묶지 않음 |
| EIA | WTI·Henry Hub 현물가격 두 endpoint와 실제 미국 원유/Lower 48 가스 주간 재고. 원유는 lease stock/SPR 제외 상업 재고, 가스는 working gas |
| 한국은행 ECOS | 기존 국고채 1·3·5·10년과 추가 CD 91일 시장금리, 신규취급 **가계대출** 평균금리. 인증 없는 sample의 열/행 제한과 정확한 표·항목·단위 유지 |
| 한국부동산원 R-ONE | 서울·경기·인천 각각의 월별 조사 매매/전세지수와 신고 거래호수, 같은 표·지역·월 정의로 비교 |
| 기존 FactSet·기업·Farside | 유효한 현재 인용·정의에 한해 이익 기대/수정·공식 사업 설명·최신 완료 BTC ETF 하루 집계 재사용 |

EIA의 과거 음수 현물가격은 허용한다. 양수 기준값이 없으면 상대 변화율을 만들지 않는다. 원유/가스 현물 흐름은 선물 ETF/ETN 수익이 아니다. 금 가격·순자산·보유량·순유입은 다른 지표다. 이익 성장과 고객 투자회수도 다른 주장이다.

검토한 provider 최대 12개·discovery 요청 최대 32개와 기존 HTTPS·robots·byte/보존 경계를 유지한다. provider의 작은 문서 목록은 같은 정책·호스트의 검토된 endpoint만 묶는다. 슬롯이 추가됐다는 이유로 매번 기업 공시 전체나 모든 시장을 깊게 수집하지 않는다. 지역 통계에 전세와 국내 금융비용 benchmark를 더했지만 특정 단지 실거래·개인 대출·공급량은 Scan에서 완성하지 않았다.

현재 최소 Scan은 요청 예산을 가격·실제 수급·지역 자료에 우선 사용해 신규 community 검색을 보류하고 그 이유를 기록한다. 기존 실제 발언은 freshness를 확인한 범위의 주장 탐색용이다. 목적 표본·고정 개수 인용·좋아요를 관심량으로 해석하지 않는다. 비교 가능한 과거 표본이 없어 관심 증가율은 미확인이다. 독립 BTC Deep Dive의 기존 검색 경로는 유지한다.

## 반복 관측과 시점

`--previous-scan`은 완료된 이전 Scan을 먼저 offline replay로 검증하고 비교 anchor를 새 `input.json`에 보존한다. 이전 run ID·cutoff·입력/shortlist hash·관측·후보를 기록한다. 이후 새 실행의 replay는 이전 폴더나 인터넷 없이 가능하다. 과거 금융 자료를 현재 evidence로 가져오지 않는다. 미래 cutoff, 합성/실제 혼합, 정의 fingerprint 훼손은 새 HTTP 요청 전에 거절한다.

`scan_observations.json`은 source identity·definition·unit·currency·scope·adjustment·forecast window·관측/획득 시각·원문 hash·locator·evidence ID를 기록한다. 요청 창만 달라지는 검토된 API URL은 창 부분만 정규화하고 거래소·상품·주기·지역·통계 항목은 유지한다. FY1과 rolling forward 12-month, 다른 거래소, 다른 부동산 지수는 하나의 시계열로 연결하지 않는다. 원문 금융 정의도 fingerprint에 포함한다. 같은 사실의 typed fact와 파생 evidence 표현을 중복 집계하지 않는다.

`scan_changes.json`은 다음 상태를 구분한다.

- `new_observation`: 같은 정의의 더 늦은 관측. 실제 두 값·날짜·delta·참조를 보존한다.
- `same_observation`: 나중에 다시 받았지만 관측일과 값은 동일하다. 시장 변화가 아니다.
- `revised_vintage`: 같은 관측일 값의 개정. 새 시장 움직임이 아니다.
- 미완성 ETF 행의 확정: 이전 완료값이 없으면 flow 증가/감소를 계산하지 않는다.
- `newly_observable`: 새로 연결된 자료. 과거 시장 개선의 증거가 아니다.
- `mismatches/unavailable/regressed_observation`: 정의 차이·현재 미확보·더 오래된 관측으로 후퇴. 조용히 연결하거나 영으로 채우지 않는다.

Decimal precision 50·ROUND_HALF_EVEN으로 같은 정의의 차이와 양수 기준값의 변화율만 계산한다. 금리는 퍼센트포인트 차이를 구분한다. 비교 가능한 **동일 시작/종료 관측기간**의 가격·이익 기대·flow·실질금리 조합만 가설로 설명한다. 가격 상승+이익 하향은 기대 괴리 위험, 가격 정체/하락+실적 개선은 반영 여부를 재검토할 단서다. 기간이 다르면 나란히 보여 주되 결합 신호는 만들지 않는다. 모든 조합은 연구 가설이며 미래 수익 보장이 아니다.

후보의 신규/제외·조사 순서 상승/하락·판단 유지는 실제 새 evidence와 선정 규칙으로 설명한다. 선정 방법 변경과 순서 재배치는 시장 악화로 표현하지 않는다. 동일 근거 후보는 이전 상대 순서를 유지하고, 새 경제적 질문이 있는 후보를 먼저 조사한다. coverage나 source 개수를 tie-break 점수로 쓰지 않는다.

## 실행과 결과 확인

```bash
# 첫 관측: 명시한 이전 실행이 없으므로 baseline
python -m investment_research ask '지금 전체 투자판에서 내가 볼 만한 기회 찾아줘.' --run-dir reports/scan_20261007
# 후속 관측: 새 폴더에 새 원문을 획득하고 전 실행과 비교
python -m investment_research ask '지금 전체 투자판에서 내가 볼 만한 기회 찾아줘.' --run-dir reports/scan_20261008 --previous-scan reports/scan_20261007
# 원자료와 당시 보고서의 오프라인 재현; 시장 업데이트가 아님
python -m investment_research ask --replay reports/scan_20261008
# 후보 번호를 구체적인 독립 조사 질문으로 연결
python -m investment_research ask '1위랑 2위 비교해줘.' --context-run reports/scan_20261008
```

`--previous-scan`은 시간 비교이고 `--context-run`은 후보 번호 해석이다. 전역의 마지막 대화·사용자 포트폴리오를 추정하지 않는다. 이전 Scan 없이 실행하면 **baseline**을 명시한다. `## 지난 Scan 이후 달라진 점`에는 방향 변화, 새/빠진 후보, 순서 변화, 유지된 판단과 자료 연결/개정의 차이를 짧게 넣는다. 자세한 정의·원문·계산·검증은 JSON과 접힌 상세 영역에 둔다.

새 실행은 `evidence_shortlist_v7`, 기본 minimum 기준은 `minimum_opportunity_evidence_v1`, 네 영역 추가 기준은 `four_asset_minimum_v2`, 비교 방법은 `same_definition_scan_comparison_v1`이다. 기존 v1~v6는 보존한 방법으로 replay한다. 기존 입력·보고서를 소급 수정하지 않는다. manifest는 관측/변경 JSON의 경로와 hash를 연결하고 replay는 모든 artifact와 다시 계산한 결과를 검증한다.

## 네 부족 영역의 실제 최소 연결

[scan_minimum.py](../investment_research/scan_minimum.py)의 소수 문서 계약과 기존 discovery/source pipeline을 재사용한다. 새 routing·범용 search·자동 Deep Dive·투자 점수는 추가하지 않았다. v7에서만 다음 need를 추가하며 다른 모드의 독립 질문에는 추가하지 않는다.

| 영역 | 실제 입력 | 의미/제한 |
| --- | --- | --- |
| 천연가스 | 기존 현물·working gas + EIA US dry gas 월간 실제 생산, 월간 LNG 실제 수출, 과거 같은 ISO 주 금요일 재고, NOAA/CPC 6~10·8~14일 지역 기온 전망 | `MMcf / 1000 / calendar_days`로 Bcf/day와 MoM/YoY 계산. 월간 US와 주간 Lower 48 범위를 구분. 수출은 당일 feedgas가 아님. 자체 오년 평균은 EIA 공식 보간 평균/평년 주입 속도가 아님. 기상 전망은 실제 기온/HDD/CDD·수요 관측이 아님 |
| 금 | 기존 LBMA 가격·월말 흐름·실질금리 + iShares IAU 거래일 기준 실물 금 tonnes | 한 신탁의 보유 수준. AUM·전체 ETF 수요·순유입·보유 증가·중앙은행 매수와 구분 |
| ETH | 기존 Coinbase 종가·일곱 날 흐름·거래량 + 발행자 링크에서 발견한 Farside Ethereum 최근 오 보고일 | BTC와 별도. 날짜/단위/열/음수/누락/반올림 범위 내 합계를 검사하고 `eth_dated_table_total_v2`로 전사. 최신 행 미완성/합계 오류면 과거 완료 행을 현재 flow로 쓰지 않음. 누락 영업일이면 누적 계산 보류. 산술 확인은 원발행사 정확성 확인이 아님 |
| 광범위 원자재 | iShares GSG NAV, 기준일이 명확한 YTD NAV 총수익, 에너지·금속·농산물·축산 포함, 별도 원유 재고/금 신탁 보유 단서 | NAV와 현물 지수/시장 체결가를 구분. YTD의 달력 연도도 fingerprint에 보존. 그룹 비중/산업금속·농산물 수급 미확인은 partial로 유지. 두 단서는 전체 원자재 동반 강세의 증거가 아님 |

최대 열 추가 need, 동일 URL 응답 공유, 소수 숫자/구절만 보존한다. 한 발행자의 주식 스타일/금 페이지는 기존 reviewed document map을 공유해 최대 12 providers를 유지한다. 네 영역 v7에만 `scan_extension=four_asset_minimum_v2`로 HTTP 예산을 48(robots 포함), source plan evidence 상한을 160으로 제한한다. 일반 discovery 상한 32, 일반 evidence 상한 100, GET 10초/2MiB·TLS·robots·redirect 금지·source당 최대 세 구절·excerpt 보존은 유지한다. 예산이나 자료 개수는 후보 순위에 사용하지 않는다.

최소 자료 충족은 평가 가능한 입력이 있다는 뜻이다. 선물 상품 경제성, 금 수요 증가, ETH network/원발행사 확인, 모든 원자재 하위 그룹 수급을 완성했다는 뜻은 아니다. 새 source 연결은 `newly_observable`이며 동일 관측 재확인·새 관측·개정·방법 변경과 분리한다. [실제 네 영역 검증과 보고서](../reports/four_asset_minimum_validation_20261006/validation_report.md)를 확인한다.

권장 사용은 시장 자료가 갱신되는 영업일에 한 번, 지역 부동산은 월별 새 통계가 나왔을 때 확인하는 것이다. 같은 관측이 반복되면 판단을 억지로 바꾸지 않는다. 날짜만 바꾸거나 replay를 최신 연구로 사용하지 않는다. [이번 실제 coverage·반복 검증](../reports/opportunity_coverage_validation_20261006T130156KST/validation_report.md)과 [이전 acceptance](../reports/opportunity_discovery_validation_20261006T103434KST/validation_report.md)에 결과를 보존한다.

## 기본 보고서의 설명 난이도

새 `ask`는 [설명형 보고서 기준](reporting.md)을 따른다. 실제 shortlist와 판단 강도는 그대로 두고 각 후보의 변화·숫자 의미·반대 근거·이미 반영된 기대·재검토 조건을 충분한 쉬운 한국어로 설명한다. 자료 부족과 투자 매력 부족을 구분하고, 용어는 첫 등장 때 뜻과 투자 의미를 붙인다. 전체 원자료·관측·계산·검증·hash는 상세 근거에 유지하며 기본 본문에 길게 노출하지 않는다. 과거 형식과 후보 선정 방법은 소급 변경하지 않는다.
