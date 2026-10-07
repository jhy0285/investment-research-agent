# 공개 출처 획득·검증 MVP

이 기능은 소수의 명시한 실제 공개 URL에서 확보한 자료를 기존 `SourceRecord → EvidenceRecord → ResearchClaim → run_research → render_report`로 연결한다. 기존 합성 `research` 입력 계약과 결과를 유지한다. 현재 기능은 출처·구절·좁은 수치·검토 기록의 추적이며, 현재 시장의 투자 매력이나 개인 자산배분을 판단하지 않는다.

현재 [ask orchestration](research-orchestrator.md)은 이 경계를 재사용해 질문 범위의 source/macro 계획을 만들고 실제 수집·검증·한국어 보고서를 연결한다. 획득 정책과 원문·정의·시점 검증을 우회하지 않는다. `acquire_plan`의 선택적 fetcher/clock은 합성 오프라인 검증에, progress callback은 CLI 진행 표시에 사용한다. 원출처 관계가 있는 자료는 해당 원출처도 같은 scope의 계획에 포함하고 독립 확인으로 중복 계산하지 않는다.

## 실행

Python 3.12 이상과 표준 라이브러리만 필요하다. 저장소 루트에서 고정된 실제 자료를 재생한다. 아래 명령과 기본 테스트는 네트워크 요청을 하지 않는다.

```bash
python -m investment_research sources replay examples/real_world_case --store examples/real_world_case/snapshots --pins examples/real_world_case/pins.json
python -m investment_research sources replay examples/real_world_case --store examples/real_world_case/snapshots --pins examples/real_world_case/pins.json --output reports/source_brief.md --manifest reports/source_manifest.json
python -m unittest discover -v
```

네트워크를 사용하는 동작은 명시적인 `acquire`다. 현재 검토한 계획의 URL만 GET하고 검색·페이지 순회·자동 투자 판단을 수행하지 않는다. 새 획득에는 새 pins 경로를 지정한다.

```bash
python -m investment_research sources acquire examples/real_world_case --store reports/source_snapshots --pins reports/new_source_pins.json
```

새 pins를 replay할 때는 같은 계획과 `--store reports/source_snapshots --pins reports/new_source_pins.json`을 사용한다. 실패한 획득도 snapshot과 pins를 남긴다. `acquire` 종료 코드 0은 모든 출처 확보, 1은 일부 획득 또는 파일 실행 실패, 2는 입력·출력 경로 검증 차단이다. `replay`의 정상 미확인·결론 유보는 0이며 형식·참조·체크섬 오류는 2다. 보고서·manifest 출력 파일은 다른 내용으로 덮어쓰지 않는다.

## 파일과 책임

| 파일 | 현재 책임 |
| --- | --- |
| `investment_research/sources.py` | 공개 접근의 경계, bounded GET, HTML/JSON 정규화, 구절 대조, 불변 snapshot, hash·freshness 검증 |
| `investment_research/source_pipeline.py` | 엄격한 SourcePlan/pins 입력, 실제 source를 기존 자료형으로 변환, 좁은 수치 비교와 명시된 검토 기록 연결 |
| `investment_research/models.py` | 기존 Source/Evidence의 선택적 provenance, Claim의 `context_ids`, 실제 source 사례의 diagnostics |
| `investment_research/engine.py` | community·미검토·stale/unknown/future 근거의 현재 판단 채택 보류 |
| `investment_research/report.py` | 출처·시점·정의·구절·support/counter/context·검토 범위와 실패를 한국어 보고서로 표시 |
| `investment_research/__main__.py` | `sources acquire/replay`, 기존 `research`, 출력 보호와 추적 manifest |
| `examples/real_world_case/` | 검토 계획, 실제 획득 pins·snapshot, 생성된 보고서·manifest, 출처 권리와 사례 설명 |
| `tests/test_sources.py`, `tests/test_source_pipeline.py`, `tests/test_source_cli.py` | 외부 서비스 없이 수집·실패·연결·CLI·replay 검증 |

모듈과 입력 경로를 나눈 이유는 명시적인 네트워크 획득과 고정된 자료의 재현을 구별하기 위해서다. 별도의 연구 엔진을 만들지 않고 같은 근거·주장·보고서 모델을 사용한다. 출처 계획과 기존 합성 case는 각각 버전 `1`의 다른 입력 계약이며 서로 대체하지 않는다.

## 획득과 보존

흐름은 `검토한 plan.json → 공개 GET → 정규화·구절 대조 → snapshot → pins → offline replay → 기존 근거 모델 → 보고서·manifest`다. 외부 글을 코드나 시스템 지시로 실행하지 않는다. 현재 런타임에는 LLM이 없다.

`sources acquire` 자체는 계속 명시적인 계획만 읽는다. 이후 추가한 [ask Source Discovery](source-discovery.md)는 **그 앞단**에서 need·검토된 공개 목록/발행자/검색 정책으로 최종 URL·관측·구절을 발견하고 SourcePlan을 만든다. 실제 source를 열어 본 response를 같은 acquire에 전달해 원문 hash·quote·정의를 확인한다. 새 JSON scalar selector는 비커뮤니티의 명시적 `json_scalar:` 위치만, HTML community 필드는 `json_html:`의 원문 text 위치만 사용한다. community 숫자는 계속 null이고 full retention을 허용하지 않는다. 검색 결과/index는 source evidence가 아니며 날짜/판본/미완성/누락은 discovery 선택 기록에 별도로 보존한다. 위 소수 명시 URL 사례와 과거 보고서는 변경하지 않는다.

HTTPS 공개 호스트만 허용하고 인증 URL·IP 주소·사설 목적지·리다이렉트·쿠키 인증을 사용하지 않는다. 요청별 timeout은 10초, 응답은 최대 2MiB, robots 응답은 최대 128KiB다. 무한 재시도나 제한 우회는 없다. `public_http`는 robots를 확인하고, 404는 robots 부재로 기록한다. robots를 읽을 수 없거나 요청이 금지되면 차단한다. `public_api`는 문서화된 공개 API라는 사전 검토와 정책 URL·메모를 요구한다. robots 부재나 API 공개가 저작권 허가를 뜻하지 않는다.

접근·라이선스 정책은 계획을 작성할 때 확인해 `policy_url`, `policy_note`, 필요하면 `full_retention_permission`으로 기록한다. 코드가 정책 문장의 법적 의미를 자동 판정하거나 정책 페이지 전체를 자동 수집하지 않는다. 획득 기록에는 robots 상태·시각·해시와 최종 URL·HTTP 상태·실제 content type·ETag/Last-Modified 중 존재한 값을 남긴다.

snapshot은 `store/<source_id>/<snapshot_id>.json`에 배타적으로 생성하고 덮어쓰지 않는다. 새 획득 시각·내용·메타데이터는 새 snapshot ID를 만든다. pins는 계획의 source 명세 해시와 선택한 snapshot ID를 고정한다. 디렉터리에서 임의로 가장 최신 파일을 고르지 않는다.

| 보존·검증 항목 | 의미 |
| --- | --- |
| `raw_sha256` | 확보한 원문 바이트의 SHA-256 |
| `normalized_sha256` | 정규화한 HTML visible text 또는 JSON 등의 SHA-256 |
| `payload_sha256` | 실제 보관한 구절·원문 등 payload의 SHA-256 |
| `snapshot_id` | 시점·명세·HTTP·정책·해시·payload를 포함한 snapshot 내용의 SHA-256 |
| `retention=full` | 명시적 보존 허가가 있는 경우 원문 base64·정규화 텍스트·구절을 함께 저장하고 replay에서 재검증 |
| `retention=excerpt` | 필요한 구절·메타데이터·해시만 저장; 버린 전체 원문을 replay에서 재검증할 수 없음 |

출처당 1~3개, 구절당 정규화 문자 1,200개 이하로 제한한다. 커뮤니티는 전체 원문 보관을 허용하지 않고 계정명·프로필 필드를 구절로 선택할 수 없으며 삭제·dead·removed 항목을 성공 자료로 만들지 않는다. 선택한 구절 자체에 개인 정보가 있는지는 별도 검토가 필요하다. 해시는 보관 자료의 동일성·변조를 검사하며 발행자의 전자서명이나 진실성 증명이 아니다.

## Provenance와 시점

SourceSpec은 ID, 요청 URL·canonical URL, 유형, 발행 주체·제목, 지역·topic·자산 범위, content type·접근 방식·정책·보존 범위, 원출처 의존 관계와 아래 시점을 기록한다. 실제 확보가 성공한 Evidence에는 snapshot·excerpt ID, locator, 일치 상태와 정의를 연결한다. 원출처 순환·없는 참조·자산 범위 유출은 차단한다.

| 시점 | 의미와 현재 경계 |
| --- | --- |
| `published_at` | 공개 시점. 모르면 null로 유지하며 획득 시각으로 채우지 않음 |
| `observed_at` | 내용이 다루는 사건·관측 시점. 발행일과 같다고 자동 가정하지 않음 |
| `retrieved_at` | 이번 HTTP 확보 시각. timezone을 가진 UTC timestamp를 자동 기록하고 replay에서 고정 |
| `valid_as_of` | 유효 기준·판본 시점. 사례의 페이지 개정일은 최초 공개일이나 과거 이용 가능 시점을 증명하지 않음 |
| `available_at` | 기존 모델의 당시 이용 가능 시점. 실제 사례에서는 입증하지 못했으므로 미확인 |

발행·관측·판본 시점은 검토한 SourcePlan의 메타데이터다. 일반 페이지의 날짜를 자동 발견하거나 진위를 자동 확인하지 않는다. 숫자만 있는 날짜를 입력할 수 있고 timestamp는 timezone을 요구한다. 최신성 기준일 `as_of`는 `YYYY-MM-DD`이며 현재 구현은 그 날 UTC 종료 시점으로 비교한다. 사용자 예제의 기준일은 `2026-10-04`이고 실제 획득 timestamp의 UTC 날짜와 구분한다.

알려진 시점 중 기준일 이후가 있으면 `future`다. 나머지는 `valid_as_of → observed_at → published_at`의 첫 알려진 시점과 출처별 `max_age_days`로 나이를 판단한다. 연구 연결 경로는 공개일 미확인을 `unknown`으로 보수적으로 표시하고 실패한 출처는 `unavailable`로 취급한다. 획득일은 최신성의 대체 기준이 아니다. stale·unknown·future를 현재 투자 판단의 확정 근거로 채택하지 않는다. 과거 사건의 좁은 사실 확인 상태는 이 적용 제한과 구분한다. freshness 임계값은 계획의 조사 목적별 설정이며 진실 점수가 아니다.

`--as-of`는 자료 나이를 다시 평가하는 옵션이다. 이번에 확보한 개정판·검토 기록이 과거에도 이용 가능했다는 증명이 아니므로 당시 정보만 사용한 백테스트나 역사적 투자 시뮬레이션으로 표현하지 않는다. 검토 기록은 참조한 자료의 획득·관측·분석·검토일보다 앞서면 차단한다.

## 구절·정의·주장 검증

계획은 자료에서 대조할 구절과 위치를 명시한다. JSON pointer는 `/text` 등 실제 string 필드를 확인한다. HTML/plain text는 공백·태그를 정규화한 텍스트에 구절이 존재하는지 확인한다. HTML의 paragraph·section locator는 검토자가 붙인 설명이며 자동으로 해당 DOM 문단 번호를 확인한 것은 아니다. 최초 공개 출처 MVP에는 PDF·표·숫자 관측 배열의 parser가 없었다. 이후 discovery/거시에 검토된 데이터 계약을 추가했고 [반도체 비교](korean-semiconductor-comparison.md)에는 작은 삼성 공식 PDF의 기업·기간·통화 열과 명시 scalar/text 전사를 추가했다. 선택적 bounded `pdftotext`와 원문 field locator를 사용하며 일반 PDF·모든 금융 표·음성 timestamp를 이해하는 parser로 확대하지 않는다.

각 Evidence 정의는 `measure`, `unit`, `period`, `currency` 또는 null, `adjustment`, `scope`를 모두 요구하며 source excerpt 정의와 일치해야 한다. headline/core CPI, nominal/real yield, 조정 여부처럼 다른 정의를 같은 수치로 합치지 않는다. 지원하는 추출은 `fed_rate_cut_v1`과 `basis_points_statement_v1`의 좁은 bp 문자열이다. 지원하지 않는 수치가 없으면 값을 만들지 않는다.

Claim은 `support_ids`, `counter_ids`, `context_ids`와 별도의 `narrative_evidence_id`를 가진다. 문맥은 지지·반박 수나 확신 점수에 넣지 않는다. 출처 위계는 추가 확인의 우선순위다. 구절 확인으로 성립하는 것은 “해당 출처에 이 발언이 있다”라는 제한된 관측이며, 일반적 경제·투자 주장 전체의 진실성은 아니다.

| 검증 경로 | 자동 검사와 의미의 경계 |
| --- | --- |
| `numeric_equality_v1` | 검토된 비커뮤니티 구절에서 좁은 수치를 추출하고 같은 measure/unit/period/currency/scope/adjustment의 기대값과 비교. 일치하면 supported, 불일치하면 contradicted, 부족하면 unverified |
| `reviewed_links_v1` | 입력의 검토자·날짜·이유와 지지/반대 참조 조건을 확인해 명시된 상태를 보존. 문장 의미를 자동 판정하지 않음 |

숫자 assertion의 `adjustment`를 생략하면 해당 관측의 정의를 따른다. 실제 예제는 이를 명시한다. 같은 원문 참조를 지지와 반대에 동시에 넣을 수 없다. 확보하지 못한 필수 참조·검토 누락·커뮤니티만 있는 지지로는 확인 상태로 승격하지 않는다. 한 출처로 확인 가능한 좁은 발표 사실과 복수 자료가 필요한 일반 주장·인과·미래 결과를 구별한다. API는 모델이 검증 상태를 정하는 권한을 제공하지 않는다.

커뮤니티 근거는 항상 `observed_narrative`이며 숫자 투자 근거로 쓰지 않는다. 발언 존재를 확인한 뒤 발언 내용을 공식 자료와 연결한다. `example-curation-review`는 이 사례의 원문·범위를 대조해 작성한 명시적 검토 기록이며 사람의 실제 서명이나 런타임 LLM의 사실 판정을 뜻하지 않는다. 독립적인 의미 검토의 필요성은 남는다.

상충은 support/counter/context와 각자의 정의·시점·한계로 보존한다. 공식 “당시 경제 확장”과 커뮤니티 “인하 이후 침체 우려”는 범위가 달라 모두 가능하다. 배경 자료를 자동 반증으로 바꾸거나 댓글 하나로 시장 전체 sentiment를 판정하지 않는다. 일반 모순 탐지·여론 대표성·커뮤니티 자동 탐색은 구현하지 않았다.

## 실제 사례와 실패

[실제 사례 설명](../examples/real_world_case/README.md), [계획](../examples/real_world_case/plan.json), [보고서](../examples/real_world_case/research_brief.md), [manifest](../examples/real_world_case/run_manifest.json)에 4개의 실제 확보 source·6개 Evidence·4개 Claim을 보관한다. Fed 공식 발표, QuantEcon 연구·교육 자료와 실제 Hacker News 댓글 두 개를 사용했다. QuantEcon과 댓글은 좁은 구절만 저장하고, Fed 성명은 확인한 public-domain 안내에 따라 원문을 저장했다. 권리·저자 표시는 사례 README와 source 정책 기록에 있다.

| 주장 | 결과와 범위 |
| --- | --- |
| 2024-09-18 FOMC 인하 폭은 50bp | 공식 구절의 `1/2 percentage point`와 같은 정의의 기대값을 비교해 `supported_within_scope` |
| 같은 결정이 25bp인가 | 의도적으로 틀린 **점검 입력**은 `contradicted_within_scope`; 실제 커뮤니티 주장으로 가장하지 않음 |
| 댓글의 50bp 사실과 정책 대응이 늦었다는 해석 | 사실 부분을 공식 자료와 연결하고 타이밍 해석은 확인하지 않아 명시적 검토 기록의 `partially_supported` |
| 2000년 이후 모든 인하 시작은 침체 직전인가 | 댓글의 존재만 확인. 전체 역사 자료·정의가 없어 `unverified`; 당시 확장 설명으로 임의 반증하지 않음 |

고정 기준일에 Fed·댓글은 stale이고 QuantEcon 최초 공개일은 unknown이다. 이는 현재 기회 분석이 아니라 과거 공개 자료의 사후 검증이다. KRW 외 사용자 정보는 확인하지 않아 실제 자산·소득·부채·주택 계획을 추정하거나 개인 적합성을 확정하지 않는다.

획득 status는 `available`, `unavailable`, `timeout`, `policy_blocked`, `parse_error`, `changed`다. HTTP 404·접근 실패·timeout·robots 차단·MIME/디코딩/JSON 오류·없는/변경된 구절을 각각 기록한다. `changed`가 뜻하는 것은 검토한 구절이 현재 응답에서 일치하지 않는다는 것이며, 작성자의 정정이나 주장의 거짓을 증명하지 않는다. 실패 source에서는 성공 Evidence를 만들지 않고 영향받은 Claim을 미확인으로 남긴다. 필수 source가 실패해도 합성 source로 대체하지 않는다.

## 값별 observation date 보존

새 `ask`와 해당 source plan에는 `observation_dates_version: per_record_observation_dates_v1`을 기록한다. 전사한 **각 행의** `definition.period` 또는 검토된 API의 행별 명시 timestamp에서 `EvidenceRecord.observed_at`을 만든다. 문서/시리즈 전체의 최신 `SourceProvenance.observed_at`, 공개일, 획득일을 과거 값에 복사하지 않는다. source의 전체 판본 기준일은 그대로 별도 metadata다.

월·분기·반기·연간 합계는 기간 전체 관측이다. 기존 date-only 필드는 기간 말일 표기로 사용하고 `observation_integrity.json`에 원기간, 시작/종료, precision, 날짜 의미를 함께 남긴다. 예를 들어 `2025-07` 월간 LNG 합계는 `2025-07-31`이라는 기간 말일 표기이며 그날 하루 수출이 아니다. 실제 API timestamp는 audit에 시간을 포함해 보존한다. publication/release, retrieval, source validity도 별도 필드다.

날짜를 확인할 수 없는 `annual_fee`, `rolling_24h` 등은 과거 관측일을 추정하지 않는다. 이전/현재 변화·trend·TTM/성장 비교·반복 Scan의 dated point 입력에서는 날짜 미확인 값과 기간/날짜 불일치를 제외한다. 현재 수준의 자료 자체와 상품 조건은 별도로 설명할 수 있다. 날씨의 미래 유효기간은 forecast의 대상이며 실제 관측일로 쓰지 않는다.

과거 source plan/ask의 고정 방법은 원래 바이트로 replay하며 과거 보고서·provenance를 덮어쓰지 않는다. 새로운 실행에 날짜 검증 artifact와 방법을 남긴다. 이전 Scan anchor의 날짜가 원문 행 기간과 불일치하거나 미확인이면 **새 anchor에서 그 비교 입력을 제외하고 이유·원래 날짜를 기록**한다. 이를 시장 악화·자료 후퇴로 계산하지 않는다. 원래 실행 파일은 수정하지 않는다. 실제 수정 전후 검증은 [날짜·원자재 검증 기록](../reports/date_attribution_validation_20261006/validation_report.md)에 남긴다.

## 검증과 현재 한계

기본 자동 테스트 **82개**가 인터넷 없이 통과했다. 기존 합성 테스트 35개를 변경하지 않고 유지했으며 source 20개·pipeline 19개·CLI 8개를 추가했다. provenance·hash 변조·시점·구절·숫자 정의·지지/반박/배경·커뮤니티·stale·unknown/future·실패·pins 일치·오프라인 replay·기존 출력 보호를 확인한다. 실제 네트워크 획득은 별도 CLI 실행으로 4개 source 모두 `available`을 확인했다. 라이브 사이트의 성공 여부를 기본 테스트 조건으로 넣지 않는다.

같은 계획·pins·기준일·방법·코드에서는 동일한 보고서·manifest를 만든다. manifest는 입력·보고서·코드 해시, 기존 engine/report 방법과 `source_snapshot_v1`, `source_verification_v1`, snapshot 상태·ID·보관 payload 해시·claim 연결을 기록한다. 전체 원문을 보관하지 않은 출처는 보관한 구절·metadata의 재현만 증명한다. 과거 합성 예제의 manifest는 생성 당시 코드 해시를 보존하며 이후 코드 변경의 해시와 같을 필요는 없다.

새로운 경제지표나 자산별 방법·세금·KRW 수익률·현재 전체 시장·개인 적절성·투자 결론은 이번 구현의 결과가 아니다. source plan 날짜와 검토 의미는 독립 확인이 필요한 명시적 입력이다. 정책 검토·HTML 위치·excerpt-only 원문 검증의 한계는 위에서 공개한다. 출력 경로는 사전 검사하지만 여러 파일 쓰기 중 파일 시스템이 실패하면 전체 rollback을 보장하지 않는다.

이후 구현한 [실제 거시 경로](macro-mvrs.md)는 원관측·판본·결정적 변환과 현재 상태 설명을 추가한다. [Opportunity Map](opportunity-map.md)은 같은 획득·보존 경로로 15영역과 실제 community 서사를 연결했고 [첫 미국 주식 Deep Dive](us-equity-deep-dive.md)는 이 원문 숫자·분모·AI 현금 회수·Treasury 비교를 조사했다. source acquisition은 [네 독립 모드](research-modes.md)가 필요한 범위에서 공유하는 도구이며 Scan의 후속 전용 경로가 아니다. 위 82개는 공개 출처 MVP 당시 검증이며 현재 전체 테스트는 [README](../README.md), 전사 방법의 한계는 Deep Dive 안내에 둔다. 다음 단일 연구는 [로드맵](roadmap.md#다음-codex-task-제안)에 두며 아직 수행하지 않았다.
