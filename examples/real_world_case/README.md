# 실제 공개 자료의 획득·검증 사례

이 사례는 **실제 공개 원문**을 사용해 출처 획득 → 구절 확인 → 주장 연결 → 검증 상태 → 기존 한국어 보고서의 경로를 검증한다. 합성 시장 자료로 실제 자료의 실패를 대신하지 않는다. 고정 기준일은 `2026-10-04`이며, 조사 대상인 FOMC 결정과 커뮤니티 발언은 **2024년의 역사적 사건**이다. 당시 결정에 대한 확인을 현재 금리나 현재 투자 기회로 표현하지 않는다. 획득 timestamp는 UTC를 보존하고 기준일·검토일은 입력에 명시한다.

좁은 질문은 “FOMC가 2024-09-18 발표한 금리 인하 폭은 무엇이며, 그 결정을 이야기하는 실제 커뮤니티 발언은 어디까지 확인할 수 있는가?”다. 여러 자산을 조사할 기반인 공개 출처의 추적과 검증에 집중한다. 이 자료만으로 현금·국채·주식의 순위나 개인 투자비중을 만들지 않는다.

## 실제 출처와 사용하는 범위

| 출처 | 사용하는 원문과 역할 | 시점·보존 한계 |
| --- | --- | --- |
| [Federal Reserve FOMC statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary20240918a.htm) | 실제 발표의 인하 폭·목표 범위, 경제활동과 물가에 관한 구절 | 발표·결정 관측일 `2024-09-18`. 당시 발표된 정책 결정을 확인하며 실제 거래금리·장기채 수익률을 뜻하지 않음 |
| [QuantEcon — Business Cycles](https://intro.quantecon.org/business_cycle.html) | 경기 변동·확장·수축의 정의를 사용하는 교육적 관점 | 페이지의 `Last changed: Jun 27, 2026`은 개정일이며 최초 공개일은 unknown. 현재 확인한 버전을 2024년 당시에 이용 가능했던 자료로 취급하지 않음 |
| [실제 Hacker News 댓글](https://news.ycombinator.com/item?id=41583714) / [공개 API](https://hacker-news.firebaseio.com/v0/item/41583714.json) | `50 bps rather than 25 may be a sign that they should have started doing it last time`라는 원문 구절 | 댓글 생성시각은 공개 JSON의 Unix `time`에서 확인한 `2024-09-18T18:30:23Z`. 한 발언만 관측하며 전체 투자자 의견을 대표하지 않음 |
| [별도 Hacker News 댓글](https://news.ycombinator.com/item?id=41583773) / [공개 API](https://hacker-news.firebaseio.com/v0/item/41583773.json) | 2000년 이후 모든 인하 시작과 침체를 연결하는 실제 역사적 서사 | 전체 인하 주기·침체 정의·관측 자료가 없어 내용은 미확인. 공식 경제 확장 평가와 다른 해석으로 보존하며 binary 반증하지 않음 |

공식 출처의 목표 범위 인하 폭은 `1/2 percentage point`이고 발표된 범위는 `4-3/4 to 5 percent`다. 허용된 결정적 추출 방법으로 단위를 해석하면 인하 폭은 `50 basis_points`다. 이는 **정책 발표의 변화 폭**이며 확정 투자수익이나 장기채 가격 변화가 아니다.

커뮤니티 구절은 확인 가능한 인하 폭과 “더 일찍 했어야 했다는 신호일 수 있다”는 해석을 함께 포함한다. 전자는 공식 발표와 연결해 확인하지만, 후자는 이 자료 묶음이 증명하지 못한다. 발언의 존재, 수치 사실의 확인, 투자·정책 해석의 검토를 분리한다.

Fed의 “경제활동이 견조하게 확장되고 있다”는 설명은 금리 인하에서 즉시 침체·패닉을 단정하는 해석에 다른 관점을 제공한다. 그렇다고 정책당국의 설명만으로 커뮤니티의 걱정이 거짓이거나 미래 침체가 없다고 판정하지 않는다. 물가가 목표를 향해 진전했으나 여전히 높다는 두 구절도 함께 성립할 수 있다.

`50`이라는 수치 확인 주장과 `25`라는 의도적으로 틀린 비교 주장은 좁은 수치 검증의 통과·반박 경로를 보여 준다. 후자는 **검증용 점검 주장**이며 실제 커뮤니티가 발표된 인하 폭을 그렇게 주장했다는 뜻이 아니다.

## 실행과 재현

저장소 루트에서 계획에 지정한 소수 URL만 가져온다. API 키·로그인·LLM 호출은 필요하지 않다.

```bash
python -m investment_research sources acquire examples/real_world_case --store reports/source_snapshots --pins reports/new_source_pins.json
```

새로운 획득은 새 snapshot ID와 새 pins 파일 경로를 사용한다. 기존 획득 기록을 덮어쓰지 않는다. 이 계획은 자동 검색·페이지 순회·전체 시장 수집을 수행하지 않는다. 접근 실패·정책 차단·구절 변경은 실패한 출처의 상태로 남긴다.

고정된 snapshot을 이용하면 인터넷 없이 원문 참조·체크섬·주장 연결을 재검증하고 기존 보고서를 생성한다.

```bash
python -m investment_research sources replay examples/real_world_case --store examples/real_world_case/snapshots --pins examples/real_world_case/pins.json --output reports/replayed_source_brief.md --manifest reports/replayed_source_manifest.json
```

다른 정보 기준일의 최신성 판단은 `--as-of YYYY-MM-DD`로 명시한다. 재생 때 획득 시각을 새로 만들거나 공개일 unknown을 획득일로 채우지 않는다. 같은 계획·snapshot·기준일·방법은 같은 보고서를 만들어야 한다.

현재 보관된 [보고서](research_brief.md)와 [실행 기록](run_manifest.json)은 이 고정 snapshot에서 생성했다. 실제 수집과 기본 테스트를 분리하므로 테스트 실행은 외부 사이트에 요청하지 않는다. 코드를 바꾸면 실행 기록의 코드 해시가 바뀔 수 있으며, 기존 예제 산출물은 다른 내용으로 덮어쓰지 않는다.

## 출처 권리와 검증의 한계

Fed의 [공식 이용 안내](https://www.federalreserve.gov/disclaimer.htm)는 별도 표시가 없는 Board 웹사이트의 정보가 public domain이며 출처를 밝혀 복제·배포할 수 있다고 설명한다. 이 사례는 성명 텍스트를 확인하기 위한 원문을 보존하며, 별도 권리인 로고·공식 인장·제삼자 자료를 가져와 사용하지 않는다.

QuantEcon 원문은 **Creative Commons Attribution-ShareAlike 4.0 International**에 따른다. 예제에서 보존하거나 표시하는 QuantEcon 구절의 출처는 Thomas J. Sargent·John Stachurski, *Business Cycles*, [원문](https://intro.quantecon.org/business_cycle.html), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)이다. 보존한 구절은 변경하지 않으며 이를 재사용하거나 파생한 텍스트에는 같은 라이선스를 적용한다. 이 출처 자료의 라이선스와 애플리케이션 코드는 구분한다.

Hacker News는 [문서화된 공개 API](https://github.com/HackerNews/API)로 필요한 댓글 구절만 획득한다. 공개 API라는 사실이 이용자 게시물 전체의 재배포 허가를 뜻하지 않는다. 짧은 구절·항목 링크·시점·해시를 남기고 사용자 프로필·계정명·전체 토론을 보존하지 않는다.

구절만 보존한 출처의 전체 원문과 정규화 내용은 획득 때 해시를 기록하지만 재생 때 전체 원문을 다시 검증할 수는 없다. 재생은 보존된 구절·메타데이터·snapshot의 동일성을 검증한다. 공식 원문을 완전히 보존한 경우에는 원문 바이트와 정규화 내용을 다시 검증한다.

구절 일치와 제한된 수치 검증은 자동화하지만, 경제적 인과·패닉의 의미·미래 결과·개인 적합성을 자동 판정하지 않는다. `example-curation-review`는 원문과 적용 범위를 대조해 작성한 명시적 사례 검토 기록이며 런타임 LLM의 사실 판정이 아니다. 오래된 공식 자료, 공개일 unknown, 상충하는 해석과 사용자 정보 부족은 결과에서 계속 드러나야 한다.
