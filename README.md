# 개인 투자 리서치 시스템

현재 시점에 한국 거주 개인 투자자에게 어떤 투자 기회가 합리적인지 조사하고, **시장 스캔 → 투자 가설 → 과거/최근 검증 → 현재 신호 → 행동·신규 자금 배분 → 사후 성과 → 전략 수정**을 반복하는 개인 투자 리서치 시스템이다. 충분한 검증이 있으면 매수 판단을 내리고, 검증 실패·현재 신호 부재·자금 제약은 행동에 반영한다. 숫자와 수익률을 만들어 강한 결론을 내리지 않는다.

핵심 질문은 다음과 같다.

> 현재 신규 자금을 투자한다면 어디에 투자하는 것이 가장 합리적인가? 이전 판단은 실제로 맞았으며, 틀린 결과를 다음 판단에 어떻게 반영할 것인가?

미국·한국 주식, 글로벌 ETF, 성장·가치·배당 특성, 국채·회사채, 현금성 자산, 금·원자재·천연가스, BTC·ETH, 한국 부동산 등을 잠재 선택지로 다룬다. 모든 자산을 매번 조사하지 않는다. 시장 맥락과 사용자 상황에 따라 조사 우선순위를 정하고 제외 이유를 남긴다. 가격 분석과 백테스트는 특정 질문에 답하는 도구다.

## 사용자의 질문에서 시작하는 네 모드

새 Broad Scan에는 [투자 판단과 사후검증](docs/investment-cycle.md)을 기본 연결한다. 첫 화면에 최종 행동·최대 다섯 후보·신규 1,000만원 예시 배분을 보여 주고 불변 일지를 남긴다. 등록 검증 자료가 없으면 신규 매수하지 않고 예시 현금을 유지한다. 실제 10년 가격/이익 전망 판본 자동 수집은 아직 연결하지 않았으며, 검토된 계약 입력을 받아 과거·최근 검증을 수행한다.

```bash
python -m investment_research ask '현재 신규 자금을 투자한다면 어디에 투자하는 것이 가장 합리적인가?' --journal reports/investment_journal
python -m investment_research ask '전체 투자판에서 기회 찾아줘' --decision-plan my_investment_plan.json --journal reports/investment_journal
python -m examples.investment_cycle.demo --output reports/example_synthetic_cycle
```

`invest run/replay/record/review`로 완료 연구의 투자 결론 재현, 기존 판단 기록, 성숙 결과와 등급·전략 평가를 실행한다. 경고 상태는 다음 신규 매수를 차단하고, 조건 수정은 이전 정의를 보존한 새 버전으로 검증한다. [실행·데이터 계약과 현재 제한](docs/investment-cycle.md), [합성 예제](examples/investment_cycle/README.md)를 참고한다.

| 질문의 목적 | 독립 진입점 |
| --- | --- |
| 오늘 투자기회·여러 시장의 변화 | Opportunity Scan |
| BTC·천연가스·특정 기업·동탄 집·배당 전략 | Asset Deep Dive |
| 삼성전자 vs SK하이닉스·S&P 500 vs 국채·집 vs 주식 | Compare |
| 내 보유·배분·집중·현금·재조정 | Portfolio Review |

명시한 모드가 우선이며 그 외에는 질문으로 해석한다. **Scan은 다른 모드의 선행 조건이 아니다.** 필요한 경우만 모드를 조합하고 답에 충분한 최소 범위·대상별 방법을 사용한다. Portfolio Review는 실제 보유와 재무 제약부터 확인한다. 자세한 계약과 자연어 예시는 [연구 진입점](docs/research-modes.md)에 있다.

```bash
python -m investment_research ask 'BTC 지금 어때?'
python -m investment_research ask '오늘 투자할 만한 곳 찾아줘'
python -m investment_research ask 'S&P500이랑 미국 국채 비교해줘'
python -m investment_research ask '삼성전자랑 SK하이닉스 비교해줘.'
python -m investment_research ask '내 포트폴리오 괜찮아?'
```

현재 `ask`는 **질문 해석 → 최소 범위 → 기존 source/macro 수집·검증 → 가능한 계산·반대 논리·사용자 제약 → 한국어 보고서**를 실행한다. 기본 보고서·근거·실행 기록은 새 `reports/asks/` 디렉터리에 보존하고 생성 경로를 출력한다. `--plan-only`는 수집 없는 계획 JSON, `--replay <실행 디렉터리>`는 인터넷 없는 재현이다. Portfolio Review에는 선택적 `--portfolio my_portfolio.json`으로 자기보고 입력을 연결한다. 없거나 불완전하면 추정하지 않고 제한을 보고한다.

새 질문의 기본 본문은 **쉽지만 충분히 자세한 설명형 보고서**다. 전문용어를 처음 쓸 때 뜻과 투자 의미를 설명하고, 숫자를 실제 변화·반대 근거·가격에 반영된 기대·판단을 바꿀 조건으로 연결한다. Scan은 실제 선정된 후보를 자세히 설명하고 자료 부족과 투자 매력 부족을 구분한다. Deep Dive·비교·보유 검토도 같은 난이도로 읽을 수 있다. 원자료·계산식·검증·해시·replay는 펼쳐 볼 수 있는 상세 근거에 유지한다. 과거 보고서는 원래 형식으로 재현한다. [보고서 설명 기준](docs/reporting.md)을 따른다.

자산 본문에는 해당 수익 구조에 맞는 용어·계산만 설명하고, 금리·환율의 관측과 변화 계산은 **시장 환경**으로 구분한다. BTC에 PER 풀이를 붙이지 않는다. Scan의 비후보는 짧은 표로 압축하고, 마지막 **그래서 지금 시장은 어떤 시장인가**에서 실제 후보와 이자 대안·가격 기대·불확실성을 1~3문단으로 연결한다. [동일 자료의 전후 검증과 예시](reports/explanation_guard_validation_20261007/validation_report.md)를 확인할 수 있다.

[질문 조건 보존](docs/query-understanding.md)은 국가·지역·만기·전략·목적·시점·명시 제약을 구조화해 실행과 보고서에 연결한다. “한국 3년 국채”를 미국 단기 국채로, “서울/수도권 아파트”를 전국 자료로 바꾸지 않는다. 미지원 조건은 데이터 부족으로 표시한다. “전체 투자판에서 기회”는 자산을 되묻지 않고 Scan을 실행한다. [여섯 실제 질문의 전후 회귀 기록](reports/query_understanding_regression_20261005T080806Z/regression_report.md)에 결과와 남은 자료 공백을 보존했다.

BTC에는 [Source Discovery & Freshness MVP](docs/source-discovery.md)를 연결했다. 질문에 필요한 범주를 먼저 고르고, 검토한 공개 목록·발행자 링크·community 검색에서 **미등록 최종 URL·현재 관측값·새 판본**을 찾아 기존 snapshot·근거·claim pipeline으로 검증한다. 가격만 물으면 가격만, ETF 순유입을 물으면 해당 흐름만 발견한다. 검색 snippet은 evidence가 아니며 source의 실제 관측일·단위·원문을 확인한다. 최신 ETF 행이 미완성이면 잠정 합계와 확정 흐름 미확보를 함께 표시한다.

넓은 기회 질문에는 [조건부 Opportunity Scan](docs/opportunity-scan.md)을 실행한다. 15영역의 최소 evidence 충족 여부와 투자 매력을 따로 기록하고 실제 조사 질문이 있는 후보만 최대 네 개 선택한다. BTC·ETH 가격 흐름, 금 기준가격·실질금리, 원유·가스 실제 재고, 지역 전세·국내 금리 benchmark를 기존 pipeline에 연결했다. `--previous-scan`은 이전 완료 실행과 같은 정의의 관측을 비교하고 새 연결·개정·시장 변화·후보 변경 이유를 구분한다. 가격 상승·인기도·자료 수는 투자 순위가 아니다. 후보 번호 후속 질문은 `--context-run`으로 이전 실행을 지정한다. arbitrary web search·전체 자산 parser·BTC network/전체 derivatives/적정 가치·특정 아파트 실거래·자동 배분은 미지원이다. [이번 실제 검증](reports/opportunity_coverage_validation_20261006T130156KST/validation_report.md), [실행 계약](docs/research-orchestrator.md), [기존 질문별 예제](examples/ask_orchestrator/README.md)를 확인할 수 있다.

천연가스 실제 월간 생산·LNG 수출·계절 재고·기온 전망, 금 IAU 실물 보유량, ETH 고유 ETF 집계, GSG 광범위 원자재 NAV/구성도 Scan v7의 최소 입력으로 연결했다. 자료 충족과 투자 매력은 별개이며 ETH 원발행사 확인·원자재 비중/일부 수급은 여전히 부족하다. [네 영역 실제 검증](reports/four_asset_minimum_validation_20261006/validation_report.md)을 확인할 수 있다.

[Source Anomaly Guard](docs/source-anomaly-guard.md)는 원문에 있는 숫자도 동일 제공자 충돌·극단적 관측·단위/주기/경제적 정의·미완성 여부를 검사해 계산과 coverage에서 격리한다. 과거 artifact는 유지하고 새 실행에 재판정 이유를 남긴다. [세 원자재 독립 Deep Dive](docs/commodity-deep-dive.md)는 실제 만기별 선물·주입 속도·난방도일·CFTC·UNG 공시, 금 ETF/중앙은행/실물 수요, 날짜 있는 GSCI 구성과 하위시장/상품 비용을 기존 pipeline으로 조사한다. BOIL 최신 조건·현재 전체 구성/성과 기여 등 남은 공백은 그대로 공개한다. [실제 보고서와 회귀 검증](reports/commodity_deep_validation_20261006/validation_report.md)을 확인할 수 있다.

[삼성전자·SK하이닉스 비교](docs/korean-semiconductor-comparison.md)는 공식 삼성전자 연결 제표, SK하이닉스 IR 연결 제공자, 국내 표시 종가를 기존 근거 pipeline으로 검증해 TTM EPS·잠정 이익배수·이익의 질을 연결한다. DART는 접수등록만 확인했고 본문 검증과 KRX 직접 대조는 미완료다. 제공자의 장부가치·현금흐름 정의 차이를 공개하며 낮은 배수를 투자 우위로 자동 확정하지 않는다. [실제 재실행](reports/semiconductor_comparison_validation_20261005T121543Z/live_comparison/report.md)에 판단 근거와 남은 공백을 보존했다.

## 현재 상태와 이번 작업의 범위

**오프라인 Cross-Asset Research Brief, 공개 출처 획득·검증, Macro Regime Snapshot, 실제 Opportunity Map과 첫 미국 주식 Deep Dive가 있다.** 합성 비교와 과거 FOMC 검증을 유지하고 15개 투자 영역을 조사한 뒤 미국 주식의 예상 이익·실적 질·AI 투자·Treasury 기회비용을 실제 자료로 검토했다. 우선순위와 경제적 판단은 근거에 연결한 검토 전 해석이며 자산 매력·개인 배분·예측을 확정하지 않는다. 수치·구절 확인과 경제적 의미의 검토를 구분한다.

Python 3.12 이상과 표준 라이브러리만 사용한다. Python 3.12.14에서 실행과 테스트를 확인했다. 합성 연구·저장 자료 replay·기본 테스트는 인터넷·API 키·패키지 설치 없이 저장소 루트에서 실행한다.

삼성전자 공식 PDF와 [검토된 CME·USDA·GSG 문서](docs/commodity-deep-dive.md)의 live 획득에는 선택적 로컬 `pdftotext`가 필요하다. 이 클라우드에는 이미 설치되어 있다. 없으면 해당 원문은 미확보로 남기며 저장된 replay와 offline 테스트에는 필요하지 않다. Python 패키지는 추가하지 않았다.

```bash
python -m investment_research research examples/cross_asset_case
```

보고서와 실행 기록을 파일로 남기려면:

```bash
python -m investment_research research examples/cross_asset_case --output reports/cross_asset_brief.md --manifest reports/cross_asset_manifest.json
python -m unittest discover -v
```

[생성된 예제 보고서](examples/cross_asset_case/research_brief.md), [실행 기록](examples/cross_asset_case/run_manifest.json), [입력 사례 설명](examples/cross_asset_case/README.md)을 검토할 수 있다. 같은 입력·방법·코드에서는 동일한 결과가 나온다. 기존 파일에 다른 내용이 있으면 덮어쓰지 않는다. 입력·출력 경로 검증 오류는 종료 코드 2, 실행·파일 접근/쓰기 오류는 1, 정상적인 결론 유보를 포함한 완료는 0이다.

현재 구현과 설계 전체의 차이, 합성 경로의 입력 계약은 [오프라인 MVP 안내](docs/offline-mvrs.md)에 정리했다. 가격 엔진·세금·추천·자동매매·LLM은 이후 기능 범위다.

## 실제 공개 자료와 replay

Fed 발표문·QuantEcon 연구 자료·Hacker News 댓글을 확보한 [실제 사례](examples/real_world_case/README.md)와 [출처 검증 보고서](examples/real_world_case/research_brief.md)를 보관한다. 고정 snapshot을 사용하는 다음 명령은 인터넷을 호출하지 않는다.

```bash
python -m investment_research sources replay examples/real_world_case --store examples/real_world_case/snapshots --pins examples/real_world_case/pins.json
```

명시적으로 새 자료를 가져오려면 새 pins 경로를 지정한다. 접근 정책·robots·timeout·보존 범위를 확인하고 실패 상태를 남긴다.

```bash
python -m investment_research sources acquire examples/real_world_case --store reports/source_snapshots --pins reports/new_source_pins.json
```

[공개 출처 안내](docs/source-acquisition.md)에 입력 계약·권리·구절 검증·최신성·실패·재현성의 경계를 설명한다. 합성 `research`와 모든 replay는 네트워크 없이 동작한다. 기본 `ask`도 기존 acquire 함수로 질문에 선택한 URL만 요청한다.

## 실제 거시 상태와 과거 시점 조회

[거시 예제 보고서](examples/macro_case/macro_snapshot.md)는 CPI 원지수의 YoY·상승률 변화, 같은 날의 10년−2년 국채 금리 차이, USD당 KRW 기준환율의 직전 관측 변화를 설명한다. [계획·자료 설명](examples/macro_case/README.md)과 [거시 MVP 안내](docs/macro-mvrs.md)에 정의·판본·공개 시점·결측과 한계를 정리했다. 아래 replay는 인터넷을 사용하지 않는다.

```bash
python -m investment_research macro replay examples/macro_case --store examples/macro_case/snapshots --pins examples/macro_case/pins.json
python -m investment_research macro replay examples/macro_case --store examples/macro_case/snapshots --pins examples/macro_case/pins.json --as-of 2025-06-30T23:59:59+09:00
```

두 번째 명령은 현재 확보판만으로 당시 이용 가능성을 증명할 수 없어 숫자 채택을 차단한 보고서를 만든다. 관측일이 과거라는 이유로 현재 개정값을 과거에 넣지 않는다. 새 실제 획득은 다음처럼 명시하고, 기존 판본을 함께 보존하려면 같은 계획의 `--previous-pins`를 지정한다.

```bash
python -m investment_research macro acquire examples/macro_case --store reports/macro_snapshots --pins reports/new_macro_pins.json
```

현재 전체 **569개 테스트가 인터넷 없이 통과**한다. 검증 명령은 `python -m unittest discover -v`다. 기존 557개를 유지하고 자산별 용어·계산 범위, 시장 환경 분리, 비후보 압축, 마지막 종합 문단과 구형 보고서 보존 검증 12개를 추가했다. 실제 라이브 획득과 기본 테스트는 분리한다. [자산별 설명과 종합 문단 검증](reports/explanation_guard_validation_20261007/validation_report.md), [기존 설명형 보고서](reports/explanatory_report_validation_20261006/validation_report.md), [관측일·원자재 검증](reports/date_attribution_validation_20261006/validation_report.md)을 보존한다.

## 한국 시장 원자료

기존 질문 해석을 유지하며 한국은행 ECOS 국고채 1·3·5·10년 금리, 삼성전자 공식 분기 실적, SK하이닉스 공식 IR 연결 제공자의 두 분기 재무자료, 한국부동산원 서울·경기·인천 아파트 매매/전세지수·거래량·실거래지수를 기존 pipeline에 연결했다. 제공자 숫자와 원공시, 기준금리와 실행 YTM, 지역 지수와 개별 거래 가격을 구분한다. 현재 주가/같은 정의 valuation·원공시 교차 확인·개별 실거래·공급/대출은 여전히 제한된다.

[연결·정의·권한·시점 안내](docs/korean-official-coverage.md), [세 실제 질문의 전후 검증](reports/korean_coverage_validation_20261005T092721Z/coverage_validation.md)에서 자료 수가 아닌 판단 가능한 범위의 변화를 설명한다. 세 질문은 한국 국채/다른 기업/전국 자료로 대체하지 않고 실제로 실행했다.

## 실제 현재 시장의 Opportunity Map

[한국어 Opportunity Map](examples/opportunity_map_case/opportunity_map.md)은 2026-10-04 13:16 한국시간의 고정 연구다. 현금·단기/장기 국채·미국/한국 주식·성장/가치/배당·금·원자재·에너지·천연가스·BTC·ETH·한국 주거 부동산을 살폈다. 3개 후속 조사 후보와 보류 이유, 반대 논리·기회비용·커뮤니티 서사와 데이터의 차이를 공개한다. 실제 자료 부족과 사용자 UNKNOWN이 제한하는 판단도 포함한다.

```bash
python -m investment_research opportunity replay examples/opportunity_map_case --plan examples/opportunity_map_case --store examples/opportunity_map_case/snapshots --pins examples/opportunity_map_case/pins.json --macro-plan examples/macro_case --macro-store examples/macro_case/snapshots --macro-pins examples/macro_case/pins.json
```

이 명령은 기존 source·macro replay와 연구 모델을 사용하며 인터넷·LLM 없이 고정된 자료와 해석 초안을 재생한다. 새 자료는 기존 `sources acquire`·`macro acquire`로 명시적으로 확보하고 별도 연구 입력을 검토한다. 새 실행에서 판단을 자동 생성하거나 날짜만 바꾸어 최신 연구처럼 게시하지 않는다. [실제 사례 설명](examples/opportunity_map_case/README.md)과 [입력·검증 안내](docs/opportunity-map.md)에 실행과 현재 한계를 정리했다.

## 첫 실제 미국 주식 Deep Dive

[한국어 보고서](examples/us_equity_deep_dive/us_equity_deep_dive.md)는 2026-10-04 18:32 한국시간의 고정 연구다. S&P 500의 forward 분모·revision·실적의 질, Microsoft·Alphabet·Amazon·Meta·NVIDIA의 사업·CAPEX·현금흐름, 단기·중기·장기 Treasury와 실제 community 서사를 비교했다. Nasdaq의 최신 valuation·전체 consensus 패널과 AI 전용 ROI는 자료 부족으로 명시한다. 판단은 **mixed**라는 경제적 해석 초안이며 BUY/SELL·가격목표·allocation을 하지 않는다.

[실제 사례와 replay 명령](examples/us_equity_deep_dive/README.md), [방법과 독립 실행 입력](docs/us-equity-deep-dive.md)에 실행·자료·현재 기능 부족을 정리했다. `deep-dive replay`는 기존 source/macro pipeline을 사용하며 자체 profile/horizon으로 부모 없이 시작할 수 있다. Opportunity Map은 선택적 맥락이고 후보 선정은 실행 조건이 아니다. 기존 부모 연결 사례도 인터넷·LLM 없이 고정 숫자·계산·초안을 재생한다. 원문 token 확인과 투자 해석을 구분하고 EY−Treasury yield를 확정 ERP로 사용하지 않는다. 기존 고정 보고서는 같은 바이트로 재현된다.

## 문서 읽기 순서

| 문서 | 다루는 내용 |
| --- | --- |
| [문제 정의와 투자 원칙](docs/product.md) | 자본배분 질문, 조사 범위, 설계 검토와 변경 이유 |
| [네 독립 연구 진입점](docs/research-modes.md) | 질문 해석·명시적 모드·최소 범위·필요한 조합·계획과 실행의 차이 |
| [질문 조건 보존](docs/query-understanding.md) | 국가·지역·만기·목적·시점·사용자 제약, 미지원 조건 보호와 실제 회귀 검증 |
| [Research Orchestrator](docs/research-orchestrator.md) | 자연어 ask의 실제 실행·지원 범위·Compare/Portfolio MVP·자료와 실행 기록·오프라인 replay |
| [Source Discovery & Freshness](docs/source-discovery.md) | need 기반 새 source 발견·원문 확인·canonical·최신 판본·누락·BTC 전후 검증 |
| [한국 시장 원자료](docs/korean-official-coverage.md) | ECOS 국채·기업 실적·서울/경기/인천 아파트, 공식/제공자 위계·결측·시점·전후 검증 |
| [삼성전자·SK하이닉스 비교](docs/korean-semiconductor-comparison.md) | 공식 제표·국내 가격·TTM 배수·이익의 질, 원공시 제한·정의 불일치·재현 |
| [아키텍처](docs/architecture.md) | 사용자·시장 맥락, cross-asset 비교, 근거와 실행 계약 |
| [리서치 신뢰성](docs/research-integrity.md) | 출처 위계, 정성·커뮤니티 검증, 수치·백테스트 원칙 |
| [한국 투자자 맥락](docs/korean-investor-context.md) | 개인화·집중위험, 한국 부동산, KRW·비용·세금 |
| [보고서와 설명](docs/reporting.md) | 시장 핵심, 대안·기회비용, 사용자 관련성과 이해 가능한 설명 |
| [구현 로드맵](docs/roadmap.md) | 조사 중심 최소 시스템, 단계별 완료 기준과 다음 과제 |
| [오프라인 MVP 안내](docs/offline-mvrs.md) | 실행, 실제 파일·자료형, 검증 규칙, 재현성과 현재 한계 |
| [공개 출처 안내](docs/source-acquisition.md) | 실제 획득·snapshot·구절·주장 연결, 권리·시점·실패·replay |
| [거시 시계열 안내](docs/macro-mvrs.md) | 현재 거시 상태, 공개·획득 판본·개정·과거 시점 선택, 결정적 변환 |
| [실제 Opportunity Map](docs/opportunity-map.md) | 15개 영역의 Broad Scan, 원문·서사 대조, 연구 초안·우선순위·기회비용·재현 |
| [미국 주식 Deep Dive](docs/us-equity-deep-dive.md) | 예상 이익·AI 현금 회수·Treasury 비교, 원문 숫자·scope·판단 유보·선택적 이전 맥락 |
| [Source Anomaly Guard](docs/source-anomaly-guard.md) | 제공자 충돌·이상치·단위·결측 격리와 claim/계산/coverage·이전 판본 보존 |
| [원자재 Deep Dive](docs/commodity-deep-dive.md) | 독립 가스/금/바스켓 조사, 실제 선물·수요·상품 차이와 시차/공백 |
| [개발 지침](AGENTS.md) | 향후 작업에서 유지할 원칙과 검증 기준 |

## 우선 지킬 경계

- 수치와 수익률은 출처가 있는 데이터 또는 재현 가능한 계산에서만 나온다.
- 사실, 계산, 해석, 가정, 추측을 구분한다. 과거 성과를 미래 확률로 바꾸어 말하지 않는다.
- 투자 아이디어의 지지 근거와 반대 근거, 무효화 조건을 함께 제시한다.
- 위험을 견딜 의향과 실제로 감당할 능력을 분리한다. 나이와 소득은 자산의 기대수익을 증명하지 않는다.
- 기초자산의 논리, 상품 구조, 계좌 조건, 레버리지 위험은 각각 평가한다.
- 출처·시점·단위가 불명확하거나 계산 전제가 충족되지 않으면 해당 결과를 만들지 않는다.
- 거시·사업·정량·시장 내러티브를 구별한다. 커뮤니티의 반복된 주장은 검증할 질문이며 그 자체로 사실이 아니다.
- 시장 매력과 사용자 적절성을 구분해 함께 검토한다. 비교 조건이 다르면 단일 점수·순위·투자비중을 만들지 않는다.

## 반복 사용

시장 자료가 갱신되는 영업일에 Scan을 실행하고 지난 완료 실행을 명시한다. 지역 부동산은 월별 통계가 갱신됐을 때 다시 확인한다. 보고서의 자료 누락과 변경 이유부터 읽고 같은 관측을 새 시장 신호로 해석하지 않는다.

```bash
python -m investment_research ask '지금 전체 투자판에서 내가 볼 만한 기회 찾아줘.' --previous-scan reports/opportunity_coverage_validation_20261006T130156KST/final_repeat_scan
python -m investment_research ask --replay reports/opportunity_coverage_validation_20261006T130156KST/final_repeat_scan
```

첫 명령은 새 연구와 보고서를 만들고 두 번째는 저장된 당시 연구만 인터넷 없이 재현한다. 매번 새 실행 디렉터리를 사용하며 이전 판본은 보존한다.
