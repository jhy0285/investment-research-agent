# 천연가스·금·광범위 원자재 독립 Deep Dive

지정 자산에서 직접 시작한다. routing과 query understanding은 변경하지 않았다. 기존 `ask → evidence need → discovery → SourcePlan/acquire → provenance/freshness → anomaly validation → claim/계산 → 한국어 보고서/replay`를 사용한다. `commodity_data.py`는 검토된 문서 계약과 필요한 산술, `commodity_report.py`는 근거에 연결한 해석 초안이다. 별도 수집기·추천 점수·거래 엔진은 없다.

```bash
python -m investment_research ask "천연가스 지금 들어갈 만해? UNG랑 BOIL까지 포함해서 딥다이브해."
python -m investment_research ask "금 지금 투자할 만해? 수요와 현재 가격까지 딥다이브해."
python -m investment_research ask "광범위 원자재 지금 투자할 만해? 어떤 원자재가 실제로 끌고 있는지도 딥다이브해."
```

## 천연가스

| 자료 | 공식/원발행 계약 | 구분해야 할 것 |
| --- | --- | --- |
| 가격·선물곡선 | 기존 EIA Henry Hub 현물 + CME Energy Daily Bulletin의 실제 여섯 인도월 정산가격 | 현물/선물, 실시간/정산, 잠정/확정판, 인도월. 현재 가격차는 실현 roll 수익이 아님 |
| 재고·주입 | EIA Lower 48 working storage, 최근 연속 여섯 주 및 과거 같은 ISO 주·직전 주 | 차분은 실제 순주입/인출. 자체 오년 평균은 EIA 공식 보간 평균/시장 예상치가 아님 |
| 생산·LNG | 기존 EIA 미국 전체 월간 실제 dry gas와 LNG 수출 | 일수 보정한 전월/전년 비교. Lower 48 주간 생산·당일 feedgas·시설 가동률은 미확보 |
| 날씨 | 기존 CPC 6–10/8–14일 전망 + 실제 주간 HDD/CDD | 가스 난방고객 가중 HDD와 인구 가중 CDD, 구형 평년 기준을 보존. 이전 forecast 없이 추위 강화 주장 없음 |
| 포지션 | CFTC disaggregated futures-only, NYMEX 계약 코드 `023651` | managed money long/short/net/change. legacy noncommercial과 다른 분류이며 과열 백분위 미계산 |
| UNG·BOIL | SEC submissions에서 최신 관련 원공시 URL 발견 후 본문 확인 | UNG 근월/차월 benchmark·4일 roll·관리보수·과거 연간 운용비·분기말 보유. BOIL 등록명은 비용/레버리지/현재 보유의 증거가 아님 |

월별 계약 gap, 주간 stock 차분, 같은 ISO 주 오년 주입 평균, 월 일수 보정, long−short와 전주 변화는 Decimal로 계산하고 모든 입력 ID를 연결한다. 월간 실적과 미래 날씨, 현재 계약을 동시 관측으로 합치지 않는다. 천연가스 자체·UNG·BOIL의 행동 표현을 별도로 제시한다. 일일 2배의 여러 날 복리는 설명용 수학으로만 설명하며 실제 BOIL 장기 성과를 기초자산의 단순 두 배로 만들지 않는다.

BOIL 발행사 페이지의 robots 정책 확인 실패, 최신 SEC 긴 공시의 2MiB 초과는 자료 공백이다. 접근 제한/상한을 우회하지 않고 다른 레버리지 상품으로 대체하지 않는다.

## 금

기존 GLD 원발행사의 LBMA PM 기준가격/월말 가격 흐름과 IAU 실제 실물량에 WGC 월간 전체 실물담보 ETF 순유입·보유량 변화, 분기 중앙은행 순수요·보석 소비·bar/coin, Fed H.10 명목 교역가중 달러, CFTC 금 코드 `088691`, CME 금 지정 계약, IAU 공식 sponsor fee를 연결한다.

ETF AUM의 가격 효과와 실제 금 보유량/순유입, IAU 한 상품과 전체 집계, 개정/미보고 추정이 포함된 WGC 분기와 국가별 중앙은행 확정 거래를 구분한다. 같은 발표판의 분기 YoY/QoQ는 당시 최초 발표나 현재 매수 속도가 아니다. 최신 WGC 월/분기 이후 수요, 국가별 최신 매수·실제 수입/프리미엄, 같은 정의 기대 인플레이션·국내 상품/계좌 조건은 부족하다. 실질금리와 달러만으로 적정가격·인과·과열을 확정하지 않는다.

## 광범위 원자재

GSG 공식 prospectus의 날짜 있는 24개 GSCI 구성 종목을 다섯 그룹으로 합산한다. 발표일과 구성 기준일은 다르며 최신 전체 가중치가 없을 때 시차를 표시한다. 합산은 같은 기준일의 완전한 목록에서만 수행하고 반올림 오차를 검사한다. 담보 국채는 원자재 노출비중으로 사용하지 않는다.

에너지는 EIA 가격/재고 및 CME WTI 지정 계약·근접 세 계약 곡선, 산업금속은 COMEX 구리, 농산물은 CBOT 옥수수와 USDA September WASDE 시장연도 전망, 귀금속은 기존 금 문서의 같은 원문/정의를 재사용한다. 옥수수는 센트/부셸의 1/8센트 표기를 해독하고 open/high/low를 정산가격으로 읽지 않는다. CME 가격변동의 공백 있는 부호는 별도 좁은 전사 계약으로 읽는다.

대표 계약의 가격과 하루 변화는 같은 인도월·관측일·단위·통화로 연결하고 본문 표에도 인도월을 표시한다. 다른 만기의 가격을 하나의 계약으로 설명하지 않는다. WTI의 교체 조건을 전체 GSG roll yield로 확장하지 않는다. GSG 교체 기간·담보 자산·공식 보수와 현물 가격/선물 교체/담보 이자/운용비를 분리한다. 현재 구성비·같은 YTD 기간의 그룹별 성과/기여도·산업금속 실제 재고/중국 수요/광산 공급·농산물 실제 수확/재고가 부족하다. 높은 GSG 과거 총수익으로 특정 그룹 기여·동반 강세·인플레이션 헤지·향후 분산 효과를 확정하지 않는다.

## 수집·보존 경계

`commodity_deep_v1` marker에만 최대 64 HTTP 요청(robots 포함), 12 providers, source당 1–3 작은 excerpt, 160 evidence를 허용한다. 일반 수집의 기존 상한은 유지한다. 모든 요청은 기존 HTTPS·TLS·robots/public API·10초·2MiB·redirect 금지를 따른다. 한 실행에서 같은 URL 응답은 메모리로 공유하고 기존 acquire의 hash/quote 검사를 다시 통과한다.

선택적 `pdftotext`는 기존 bounded subprocess를 재사용한다. 명시적으로 검토한 CME Energy/Metals/Agriculture, USDA September WASDE, iShares GSG prospectus, S&P 공식 Daily Global Index Dashboard URL만 추가로 허용하며 source 종류와 excerpt-only를 검사한다. 일반 PDF·full retention·외부 JavaScript 실행은 허용하지 않는다. decoder가 없거나 bytes/시간/출력 경계를 넘으면 gap으로 남기고, 저장된 excerpt replay에는 decoder가 필요 없다.

## 관측일 수정과 Broad Commodity 상승 분해 검증

원문 행의 날짜/월/분기에서 값을 연결하며 문서 전체 최신일을 과거 값의 날짜로 복사하지 않는다. 날짜 미확인 과거 입력은 변화 계산에서 제외한다. 천연가스 본문에 Henry Hub·working gas·월간 생산/LNG·과거 같은 ISO 주 재고의 기간과 실제 evidence date를 대조한 표를 넣는다. 월간 합계의 말일 표기는 해당 월 전체 기간이며 당일 flow가 아니다. [공통 날짜 규칙](source-acquisition.md#값별-observation-date-보존)을 다른 자산에도 적용한다.

[S&P 원발행 dashboard](https://www.spglobal.com/spdji/en/documents/performance-reports/dashboard-daily-global-markets.pdf)의 Commodities 페이지에서 실제 관측일, `Daily / MTD / YTD / 12M` 열과 USD total-return 정의를 확인한 후 Energy·Industrial Metals·Precious Metals·Agriculture·Livestock의 같은 YTD 성과를 전사한다. 보조 WTI/Brent/천연가스, 교체 방식 지수, 금 현물/선물은 각각 고유 정의를 유지한다. 숫자만 있는 chart label을 최신 구성비로 추정하지 않는다.

이번 실제 획득에서 최신 확인한 정확한 구성일은 GSG prospectus의 **2026-02-27**, 성과 종료일은 S&P dashboard와 GSG YTD의 **2026-10-02**다. 같은 기간 그룹 성과는 에너지 중심의 강세와 귀금속/축산의 다른 방향을 보여주지만 GSG의 정확한 그룹별 contribution은 미확보다. 중간 시점 비중 × 전체 YTD를 사용한 근사 기여도는 만들지 않는다. 같은 GSCI의 price/spot·excess-return 시계열, 실현 roll·담보 이자도 미확보다. 다른 교체 방식 지수의 성과 차이나 금 현물/선물 지수 차이를 순수 교체 비용으로 계산하지 않는다. **+54.02%만으로 광범위 강세·현재 투자기회를 확정하지 않는다.**

새 보고서·관측일 audit·반복 Scan 입력 제외·보존/replay 결과는 [날짜·원자재 검증 기록](../reports/date_attribution_validation_20261006/validation_report.md)에 둔다.

## 보고서와 반복 Scan

사용자 본문은 현재 결론·왜 지금·가격/실제 수급·Bull/Bear·이미 반영한 기대·상품 차이·지금 행동·판단 변경 조건·한국 투자자 의미·최대 일곱 문장의 쉬운 설명이다. 상세 source·구절·계산·검증·공백은 접힌 부록과 manifest에 둔다. 모든 경제적 해석은 `pending`이며 매매·비중을 확정하지 않는다.

최소 Scan에는 질문에 필요한 곡선·날짜 있는 금 수요·대표 구성 단서만 추가한다. Full Deep Dive를 모든 영역의 Scan 선행 조건으로 만들지 않는다. 이전 accepted Scan과 같은 정의의 변화, 새 연결, 개정, 격리·방법 변경을 구분하고 자료 수를 선정 기준에 넣지 않는다. 실제 세 보고서·마지막 Scan·회귀·replay 결과는 [검증 기록](../reports/commodity_deep_validation_20261006/validation_report.md)에 보존한다.
