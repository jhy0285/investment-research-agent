# 거시 시계열 MVP와 Macro Regime Snapshot

후속 [한국 원자료 coverage](korean-official-coverage.md)는 기존 macro acquisition/replay에 ECOS `817Y002` 국고채 1·3·5·10년 adapter를 추가했다. 국가·통화·만기·연%와 일별 관측을 확인하고 최초 발표/개정 시각 unknown에는 기존 획득 시각 하한 규칙을 사용한다. 이 문서의 미국 중심 원래 고정 예제는 수정하지 않았다.

Macro는 [독립 연구 모드](research-modes.md)의 공통 선택 도구다. 모든 Deep Dive·Compare·Portfolio Review가 전체 Macro Snapshot이나 Opportunity Scan을 먼저 실행할 필요는 없다. 현재 예제의 네 series는 고정 사례의 범위이며 실제 질문에 영향을 주는 factor만 사용한다.

실제 공개 거시 자료를 확보하고, 숫자의 정의·관측 기간·공개 시점·획득 판본을 구분한 뒤 한국어로 현재 확인 가능한 상태를 설명한다. 가격 예측, 자산 순위, 매수·매도, 개인 투자비중은 만들지 않는다. 거시 상태와 사용자의 투자 적합성은 별도 판단이다.

Python 3.12 이상과 표준 라이브러리로 실행한다. 기존 [합성 오프라인 연구](offline-mvrs.md)와 [공개 source 검증](source-acquisition.md)을 유지하고 같은 snapshot·provenance·EvidenceRecord·MetricResult에 연결한다.

## 1. 최소 자료 집합과 선택 이유

| 원자료 | 공식 식별자와 정의 | 단위·빈도 | 답하는 질문과 한계 |
| --- | --- | --- | --- |
| 미국 headline CPI-U 지수 | BLS `CUUR0000SA0`, 미국 도시 평균의 모든 품목, 계절조정하지 않은 CPI-U, 1982–84=100 | `index`, 월별 | 정확한 전년 동월 지수와 비교해 물가 상승률을 계산. Core CPI·계절조정 전월비와 구분 |
| 미국 2년 Treasury 수익률 | Fed H.15 `RIFLGFCY02_N.B`, 명목 constant maturity, investment basis | `percent`, 일별 | 단기 시장금리의 관측·변화. 정책 목표금리·실효 연방기금금리가 아님 |
| 미국 10년 Treasury 수익률 | Fed H.15 `RIFLGFCY10_N.B`, 명목 constant maturity, investment basis | `percent`, 일별 | 장기 시장금리와 동일 날짜의 10년−2년 차이. 실제 채권의 확정 수익률이 아님 |
| USD/KRW 기준환율 | Fed H.10 `RXI_N.B.KO`, 뉴욕 정오 buying rate, USD당 KRW | `KRW_per_USD`, 일별 관측·주간 발표 | 한국 투자자의 통화 평가 환경. 국내 체결 환율·실시간 호가·환전 비용이 아님 |

네 series는 물가·금리곡선·한국 투자자의 환율 환경을 작은 범위에서 연결한다. 고용·성장·정책금리·한국 CPI·한국 기준금리는 이번 집합에 없다. 빈 항목을 대체 지표로 채우거나 침체 여부를 추정하지 않는다.

Treasury CSV의 원문 단위는 `Percent:_Per_Year`, `Multiplier: 1`, `Currency: NA`다. 수익률 자체는 화폐 금액이 아닌 비율이다. 정규화된 정의의 `currency: USD`는 기초인 미국 국채의 통화 맥락과 비교 조건을 뜻하며, 원문 `NA`를 USD 금액으로 바꾸었다는 뜻이 아니다. FX 원문은 `Unit: Currency`, `Currency: KRW`, `Multiplier: 1`이고 방향을 별도로 검증한다.

## 2. 실제 source와 획득 경로

계획의 명시적인 **4개 URL**을 기존 source collector로 읽는다. 세 원자료 dataset에 CPI 공식 release를 교차 확인용으로 추가한다.

| source | 역할·보존 |
| --- | --- |
| [BLS 공개 v1 API](https://api.bls.gov/publicAPI/v1/timeseries/data/CUUR0000SA0) | 무등록 GET의 최근 3년 CPI 원관측 JSON. 허용된 전체 원문 보존 |
| [Fed H.15 Treasury CSV](https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&series=bf17364827e38702b42a58cf8eaa3f78&lastobs=&from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package) | 공식 Treasury package에서 2년·10년 열을 선택. 전체 파일이 2MiB 수집 한도 안에 있는지 확인하며 분석 기간은 binding으로 제한 |
| [Fed H.10 일별 환율 CSV](https://www.federalreserve.gov/datadownload/Output.aspx?rel=H10&series=60f32914ab61dfab590e0e470153e3ae&lastobs=250&from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package) | 최근 250행의 공개 환율 package에서 KRW 열을 선택. 전체 원문 보존 |
| [BLS CPI 공식 release](https://www.bls.gov/news.release/cpi.htm) | 발표 시각·관측월·CPI-U 원지수의 세 구절만 보존하고 원자료와 교차 확인. 해당 관측의 공개 시점만 확인하며 과거 전체 release calendar는 생성하지 않음 |

API는 [BLS의 명시적인 v1 GET 문서](https://www.bls.gov/developers/api_signature.htm)와 [이용 조건](https://www.bls.gov/developers/termsOfService.htm)에 따라 호출한다. robots로 막힌 API 호스트를 일반 웹 scraping 대상으로 바꾸거나 인증·제한을 우회하지 않는다. Fed와 BLS release의 공개 웹 경로는 기존 robots·HTTPS·redirect·용량·timeout 검사를 따른다. 자동 검색·페이지 순회는 수행하지 않는다.

권리는 [BLS public domain 안내](https://www.bls.gov/bls/linksite.htm)와 [Fed disclaimer](https://www.federalreserve.gov/disclaimer.htm)를 따른다. 자료의 출처와 실제 획득 시점을 표시한다. 로고·공식 인장·별도 권리의 이미지·제삼자 자료는 수집·재사용 대상으로 삼지 않는다. BLS API 자료를 사용한 결과에는 다음 문장을 그대로 표시한다.

> BLS.gov cannot vouch for the data or analyses derived from these data after the data have been retrieved from BLS.gov.

## 3. 정의와 원관측의 계약

`SeriesDefinition`은 canonical ID, 이름·정의, 단위·빈도·계절조정, publisher·source·관할, raw/transformation, 발표·개정 특성, 통화 맥락, 필요하면 명목/실질·만기, 신선도 한도를 담는다. 같은 canonical ID에 다른 정의를 조용히 끼워 넣지 않는다.

`MacroObservation`은 값 또는 명시적 결측, 관측일, 공개·획득·vintage·revision·known-at·valid-as-of, source와 snapshot ID, 원문 위치, 단위·빈도·조정·통화를 담는다. observation ID는 이 기록에서 결정적으로 생성한다. 모르는 날짜는 `None`으로 보존한다.

- 월별 CPI의 관측일 `YYYY-MM-01`은 **해당 월의 기간 라벨**이다. 월 첫날에 지수를 발표했다는 뜻이 아니다.
- CPI는 expected series ID와 응답 성공 상태를 확인한다. `M01`–`M12`를 월별로 읽고 `M13` annual average는 제외한다.
- 실제 API의 **2025년 10월**은 값 `-`와 “Data unavailable due to the 2025 lapse in appropriations”라는 footnote를 가진다. 결측과 원문 진단을 유지하며 보간·0 대체를 하지 않는다.
- Fed CSV는 설명·Unit·Multiplier·Currency·Unique Identifier·Time Period의 메타데이터와 정확한 열 ID를 확인한다. `ND`·빈칸은 결측이다. 양쪽 yield와 FX의 다른 의미를 이름만 보고 합치지 않는다.
- 수치 형식 오류, 단위·열·빈도·통화·명목/실질·만기의 변화는 파싱 또는 비교 전제를 실패시킨다. 같은 기간·판본에 다른 값이 있으면 상충으로 진단한다.

## 4. 시점·vintage와 역사적 질의

관측이 발생한 기간과 그 특정 값의 판본을 알 수 있던 순간은 다르다. 선택은 기준 시점 이전의 관측 중 공개·vintage·revision·known-at 조건을 충족한 판본만 사용한다. 같은 관측일의 여러 판본은 보존하고, 조건을 통과한 마지막 판본을 선택한다.

이번 실제 어댑터는 현재 원자료의 **획득 시각을 `vintage_at`과 `known_at`의 보수적인 하한**으로 둔다. `vintage_id`의 `retrieved_snapshot:<hash>`는 시스템이 확보한 판본 ID다. 공식 ALFRED vintage나 최초 발표 판본의 증명과 같지 않다. API·현재 CSV의 오래된 row를 가져왔다고 당시 투자자가 같은 값을 알고 있었다고 인정하지 않는다.

실제 `retrieved_at`은 HTTP 응답 획득과 파싱을 완료한 뒤 기록한다. 요청을 시작한 순간에는 아직 받은 값을 알 수 없으므로, 시작 시각을 이용 가능 시각으로 사용하지 않는다. 기존 요청 시작 시각을 기록했던 초기 17:04 UTC 사례는 `examples/macro_case/initial_capture/`에 따로 보존하며 엄밀한 과거 가용성 증명에 사용하지 않는다. 현재 main pins는 수정된 방식으로 4개 source를 다시 확보한 판본이다.

이번 CPI 교차 확인은 2026년 8월 CPI-U의 지수와 공식 release의 **2026-09-11 08:30 ET**를 대조한다. 관측월·원지수 일치가 확인되면 해당 관측에 `released_at`을 연결한다. 그래도 현재 API와 release를 확보한 시점보다 `known_at`을 앞당기지 않는다. 나머지 월의 공개·개정 날짜는 unknown이다. release가 실패하거나 변경되었으면 그 한계를 진단하며 현재 API를 과거 발표본으로 승격하지 않는다.

교차 확인용 release도 질의의 cutoff 이전에 획득된 판본만 사용한다. 나중에 확보한 release를 과거 질의에 붙여 당시 관측의 공개 시각·내용을 바꾸지 않는다. 같은 과거 cutoff의 pins에 이후 판본을 추가해도 그 시점의 채택 관측·계산은 변하지 않아야 한다. 기록에 추가 판본과 진단이 늘어난다는 사실과 과거에 알 수 있던 결과의 변화는 구분한다.

CPI-U NSA는 정기적인 계절조정 재추정과 구분하지만 오류 정정이 전혀 없었다는 증거는 아니다. Fed H.10은 후속 정정을 현재 country data에 반영할 수 있다. 이번 공식 공지는 2026-08-03 자료의 8월 12일 정정을 알리지만 모든 과거 값의 수정 이력을 제공하지 않는다. CSV HTTP `Last-Modified`는 동적으로 파일을 생성한 시각일 수 있어 release date나 경제자료 revision date로 대체하지 않는다.

따라서 현재 확보한 실제 파일만으로 `2025-06-30`의 당시 값은 재현하지 못한다. 그 cutoff에서는 이후 판본을 제외하고 차단·자료 부족을 보고한다. 명시적인 여러 판본을 가진 테스트로 수정 전후 선택을 검증할 수 있다는 사실과 실제 전 기간의 공식 vintage를 확보했다는 주장은 구분한다.

## 5. 원자료와 결정적 변환

계산은 `macro.py`의 고정 Decimal 문맥에서 수행한다. 보고서는 숫자를 계산하거나 LLM 판단으로 방향을 만들지 않는다. 각 `MacroMetric`은 출력 series ID, 공식·방법 버전, 입력 series와 observation ID, 정확한 관측창, 단위·가정·상태·진단을 담는다.

| 변환 | 공식·조건 | 해석의 경계 |
| --- | --- | --- |
| CPI YoY | `(index_t / index_t_minus_12_months - 1) * 100`; 같은 raw 월별 양수 index의 정확한 두 endpoint | 출력은 percent. 중간 월 결측은 공개하되 두 endpoint가 있으면 계산 가능; endpoint 결측이면 차단 |
| 10년−2년 spread | `yield_10y_t - yield_2y_t`; 동일 관측일·기준 시점·단위·통화 맥락·명목/실질·조정 | 출력은 percentage points. 과거 마지막 공통 날짜로 조용히 후퇴하지 않음 |
| 원관측 변화 | `current_value - exact_reference_value` | 지정한 비교창의 차이이며 지속 추세나 원인의 증명이 아님 |
| YoY 상승률 변화 | 현재 YoY와 정확한 전월 YoY의 차이 | 지수 수준의 상승·하락과 물가 상승률의 방향을 구분 |

방향은 지원되는 계산 결과의 부호를 `up/down/unchanged`로 표시한다. 일별 series의 직전 선택 관측은 날짜를 함께 보여 준다. 월별·개월 비교는 정확한 필요한 기간을 요구하며 빈 기간을 가까운 값으로 채우지 않는다. “장기금리가 높다/낮다”의 역사적 등급이나 침체 확률은 이 규칙으로 생성하지 않는다.

## 6. 기존 evidence와 보고서 연결

선택된 원관측과 계산 입력을 기존 `EvidenceRecord`로 연결한다. source와 observation의 snapshot ID·원문 위치·정의·시점·freshness를 유지한다. 채택 가능한 계산은 같은 ID·값·단위·방법·입력 observation ID를 가진 기존 `MetricResult`로 연결한다. 해당 정의 안의 계산 사실은 주장으로 추적할 수 있지만, 자동 확인 범위는 계산과 원관측의 구조적 일치다.

보고서가 사용하는 값에 맞는 EvidenceRecord 또는 MetricResult가 없거나 참조가 다른 값·단위·원문 판본을 가리키면 보고를 거부한다. 숫자 표시의 반올림과 원래 Decimal 값은 구분한다. 실행 manifest에는 모든 관측·판본·선택/제외·결측·계산·진단과 고정 source 참조를 남긴다.

CPI의 확인된 발표 시각은 `release_provenance`에 observation ID부터 공식 release source·snapshot·세 구절 ID까지 연결한다. API의 원지수 위치와 release의 시각·기간·지수 위치를 각각 추적하며, 같은 source ID가 있다는 사실만으로 발표 시각을 인정하지 않는다.

한국어 보고서는 기준 시점, 핵심 변화, 금리, 물가, 경기/고용의 미구현 범위, 환율·한국 투자자 관점, 상충해 보이는 신호, 가능한 전파 경로, 아직 말할 수 없는 것, 최대 5문장의 쉬운 설명, 근거 부록으로 구성한다. 서로 다른 월별·일별 관측창의 방향 차이를 같은 사건의 통계적 모순이나 인과로 표현하지 않는다.

금리→할인율, 물가→구매력, 환율→KRW 표시 가치의 설명은 조건과 필요한 추가 자료를 가진 **검토 전 해석 후보**다. 채권 계약·기업 이익·환헤지·비용·세금·개인 원장 없이 자산별 성과나 개인 적합성을 확정하지 않는다. 개인 입력은 KRW 외 unknown이며 자산 추천·비중을 출력하지 않는다.

## 7. 실행과 재현

저장소 루트에서 검토한 계획의 source만 새로 확보한다. 기존 pins는 덮어쓰지 않고 새 파일을 지정한다.

```bash
python -m investment_research macro acquire examples/macro_case --store examples/macro_case/snapshots --pins reports/macro_pins_new.json
```

동일한 계획의 이전 snapshot을 보존하면서 새 판본을 추가하려면:

```bash
python -m investment_research macro acquire examples/macro_case --store examples/macro_case/snapshots --previous-pins examples/macro_case/pins.json --pins reports/macro_pins_next.json
```

고정 예제를 네트워크 없이 재생한다. `--as-of`를 생략하면 pins에 저장된 정확한 기준 시각을 사용한다.

```bash
python -m investment_research macro replay examples/macro_case --store examples/macro_case/snapshots --pins examples/macro_case/pins.json --output reports/macro_snapshot.md --manifest reports/macro_manifest.json
```

정확한 과거 순간의 질의에는 timezone을 포함한 ISO timestamp를 쓴다. 날짜만 지정하면 **그 날짜의 UTC 일말**로 해석한다. `2025-06-30`과 한국 시각의 `2025-06-30T23:59:59+09:00`은 같은 cutoff가 아니다. 보고서의 사용자용 기준 시각은 Asia/Seoul을 함께 표시하고, 저장된 timestamp·판본은 UTC 의미를 보존한다.

```bash
python -m investment_research macro replay examples/macro_case --store examples/macro_case/snapshots --pins examples/macro_case/pins.json --as-of 2025-06-30T23:59:59+09:00
```

이 명령군에서는 `macro acquire`만 네트워크를 호출한다. 기본 `ask`도 관련 series만 투영해 동일한 `acquire_macro`를 재사용한다. replay는 고정 snapshot에서 보존한 내용의 원문·정규화·payload·메타데이터 해시와 계획·pins의 연결을 검사한다. CPI release 전체 원문은 획득 때 해시를 기록하고 폐기하므로, replay는 남은 구절과 메타데이터만 재검증하며 폐기한 전체 페이지의 일치를 보증하지 않는다. 같은 계획·pins·cutoff·코드·방법에서는 같은 구조화 결과와 보고서를 재현한다. 이전 판본에서 이후 판본이 달라져도 원자료를 덮어쓰지 않는다.

## 8. 실패·결측·신선도

획득 실패, timeout, 접근/robots 정책 차단, 원문 변경·selector 부재, 파싱·정의 오류는 source와 연결 진단으로 남긴다. 실패한 source를 성공한 evidence처럼 취급하지 않는다. 독립적으로 유효한 자료가 있으면 지원되는 부분만 설명하고 빠진 범위를 공개한다. pins·체크섬·계약 자체가 잘못되면 정상 보고서를 만들지 않고 입력 오류로 종료한다.

선택 상태는 `available/stale/missing/blocked`를 구분한다. 최신 관측이 결측이면 이전 수치를 현재 값으로 대체하지 않는다. 신선도 규칙은 기준 시점의 날짜와 마지막 관측일 차이에 대한 계획의 명시적인 `max_age_days`다. stale 값은 과거 기록으로 보존하지만 현재 핵심 요약에 채택하지 않는다.

CPI의 월별 발표 지연, H.10의 주간 업데이트, 휴일을 고려해 각 series에 별도 허용 한도를 둔다. 월 첫날은 CPI의 기간 라벨이며 현재 날짜의 관측값이 매일 발표되는 것처럼 다루지 않는다. 이번 신선도 기준은 완전한 공식 release calendar나 자동 지연 탐지 기능이 아니다. 아직 발표되지 않은 값과 실제 결측을 구분할 추가 자료가 없으면 이를 한계로 표시한다.

기존 파일에 다른 내용이 있으면 덮어쓰지 않는다. 획득은 모든 source가 available이면 종료 코드 0, 일부 획득 실패면 기록을 남기고 1이다. 계약·입력·출력 경로 오류는 2, 파일·실행 오류는 1이다. 유효한 replay에서 근거 부족·과거 cutoff 차단을 정직하게 설명하는 보고서는 정상 결과이며 투자 지시로 바꾸지 않는다.

## 9. 구현 파일과 검증

| 파일 | 책임 |
| --- | --- |
| `investment_research/macro.py` | 정의·원관측·판본 선택·freshness·변환과 방향 규칙 |
| `investment_research/macro_pipeline.py` | 계획·pins·공식 JSON/CSV 어댑터·CPI release 교차 확인·기존 evidence/metric 연결·manifest |
| `investment_research/macro_report.py` | 수치·참조 검사와 정형 한국어 설명; 계산·네트워크 없음 |
| `investment_research/__main__.py` | `macro acquire/replay`, 명시적 cutoff와 출력 보존 |
| `examples/macro_case/` | 실제 계획·고정 원문 snapshot·pins·생성 보고서·실행 기록 |
| `tests/test_macro*.py` | 수정 전후 선택·시점·결측·단위·변환·live 주입/replay·보고서·CLI 검증 |

일반 테스트는 인터넷을 호출하지 않는다. 실제 source를 확보한 사례와 합성 revision·오류 fixture를 구분한다. 합성 판본으로 수정 이력을 검증했다는 사실을 실제 공식 빈티지 확보로 표현하지 않는다.

```bash
python -m unittest discover -v
```

기존 오프라인/source 테스트와 함께 공개 시점·vintage·수정·동일 순간 판본 충돌·과거 cutoff, 결측·stale·단위·빈도 변화, 독립 기대값의 YoY·yield spread, 동일 결과 재생, 보고서의 모든 주요 수치·입력 ID·원문 참조를 검증한다. 코드가 통과해도 자료의 경제적 의미·미래 적용 가능성이 자동 보증되지는 않는다.

거시 MVP 완료 당시 검증은 **134개 테스트 통과**다. 기존 82개, 거시 core 23개, 거시 pipeline 18개, 거시 CLI 11개를 포함한다. 응답 완료 전 자료 채택과 이후 release 판본에 의한 과거 결과 변경을 검출하는 회귀 검증도 포함한다. 실제 획득에서는 4개 source가 available이며 고정 [계획](../examples/macro_case/plan.json)·[pins](../examples/macro_case/pins.json)·[실행 기록](../examples/macro_case/run_manifest.json)과 [한국어 보고서](../examples/macro_case/macro_snapshot.md)를 보존했다. 이후 Opportunity Map을 포함한 전체 검증은 [현재 안내](opportunity-map.md)에 둔다.

보고서의 정보 기준 시각은 **2026-10-04 02:13 KST**이며, pins의 정확한 timestamp는 `2026-10-03T17:13:16.107675+00:00`이다. 이 고정 사례에서 확인한 내용은 다음과 같다. 새 실행의 최신 값으로 혼동하지 않는다.

| 원관측·계산 | 관측 기간 | 고정 사례의 결과 |
| --- | --- | --- |
| CPI-U NSA raw index | 2026년 8월 / 2025년 8월 | 334.980 / 323.976 |
| CPI YoY | 위 두 endpoint | 3.397%; 전월 YoY와 비교한 변화는 +0.032%p. 표시만 반올림하고 정확한 계산 값은 manifest에 보존 |
| 미국 2년 / 10년 명목 Treasury yield | 2026-10-01 | 4.780% / 5.240%; 10년−2년 spread 0.460%p |
| USD당 KRW 기준환율 | 2026-09-25 / 2026-09-24 | 1356.510 / 1369.440; 직전 관측 대비 −12.930 KRW/USD |

## 10. 현재 한계와 다음 과제

현재 선택한 시계열의 상태만 설명하며 정책금리·고용·성장·한국 물가·유동성·신용 전체를 평가하지 않는다. 정기적인 자동 갱신, 공식 vintage archive 전체 수집, 최초 공개와 모든 revision의 입증, 미래 예측, 자산 가치평가·순위·배분은 구현하지 않았다. release selector나 source 정의가 바뀌면 계획과 검토를 갱신해야 한다.

이후 [실제 Opportunity Map](opportunity-map.md)이 이 고정 거시 snapshot을 자산별 원문·반대 논리·기회비용·사용자 UNKNOWN과 연결했다. 15영역과 후속 후보 3개를 기록했고 [첫 미국 주식 Deep Dive](us-equity-deep-dive.md)가 EPS·AI 투자와 현재 단기/중기/장기 Treasury 기회비용을 조사했다. 같은 Fed HTML과 CSV는 독립 확인으로 세지 않는다. 다음 단일 과제는 [로드맵](roadmap.md#다음-codex-task-제안)에 두며 아직 수행하지 않았다.
