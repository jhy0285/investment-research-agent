# 자연어 ask의 실제 실행과 오프라인 재현 예제

사용자가 모드를 지정하지 않고 질문하면 필요한 범위를 선택해 실제 acquisition·evidence/claim 검증·가능한 계산·한국어 보고서까지 연결한다. 아래 live 세 사례는 2026-10-04 실제 공개 URL에서 확보한 판본이다. 보유 구성 예제는 별도의 합성 fixture이며 사용자의 실제 자산으로 해석하지 않는다.

| 질문/입력 | 보고서 | 선택한 범위·결과 |
| --- | --- | --- |
| BTC 지금 어때? | [BTC 실제 보고서](btc_live/report.md) | Bitcoin 직접 조사, FX만 관련 macro. 5 SourceSpec·9 사용 근거·12 주장·1 환율 계산. 상품 구조·디지털자산 전체 flow와 BTC 고유 수요를 구분하고 현재 가격 매력은 자료 부족으로 유보 |
| 오늘 투자할 만한 곳 찾아줘 | [실제 기회 탐색](scan_live/report.md) | 11영역 Opportunity Scan, 24 SourceSpec·92 사용 근거·106 주장·12 계산. 약한 자료로 매력 순위나 후보를 강제하지 않음 |
| S&P500이랑 미국 국채 비교해줘 | [실제 비교](compare_live/report.md) | Compare, S&P 500·Treasury와 관련 금리/FX. 7 SourceSpec·54 근거·28 주장·9 계산. 이익 전망 수정·P/E 정의·이익수익률과 같은 날 국채 차이를 구분하고 미래 수익 우열 유보 |
| 내 포트폴리오 괜찮아? / 입력 없음 | [보유 정보 부족](portfolio_unknown/report.md) | 실제 보유가 없으므로 수집·비중 추정 없이 누락 정보와 제한 보고. `needs_input` |
| 내 포트폴리오 괜찮아? / 합성 자기보고 금액 | [합성 보유 구성](portfolio_synthetic/report.md) | 600만·200만·현금 200만원으로 60%·20%·20%를 검산. 제공 자산−부채·필요 자금 합계도 계산. 적정 비중·안전성·개인 추가 투자 추천 아님 |

SourceSpec 개수는 독립 출처 개수가 아니다. 같은 Fed 자료의 다른 열·구절·HTML/CSV를 독립 확인으로 세지 않는다. 원문·정의·시점의 확인과 투자상의 경제적 의미는 구분하고 해석 초안은 pending으로 유지한다.

Live 정보 기준은 BTC와 Compare가 2026-10-04 14:14:50 UTC, Scan이 14:15:07 UTC다. 한국시간으로 각각 23:14:50, 23:15:07이다. 획득 날짜와 원 관측 날짜가 다른 자료는 관측일을 그대로 표시한다. 모든 live 사례의 연구 상태는 필요한 가격/실적/상품/사용자 자료가 남아 `partial`이다. Scan의 한국부동산원 통계 페이지는 `policy_blocked`로 기록했고 접근 제한을 우회하지 않았다. 다른 23 SourceSpec은 이 실행에서 `available`이었다. 실행이 완료되었다고 투자 기회가 검증 완료되었다는 뜻은 아니다.

합성 보유 예제의 숫자·기관·공시·macro·profile·획득 응답은 테스트용으로 작성되었다. 기준 시각 2026-09-10은 고정 fixture clock이며 실제 live 투자 근거로 사용하지 않는다. 실제 보유를 추정하거나 개인 계좌를 조회하지 않았다. 현재 보유정보 부족 예제는 기준 시각이 실제 실행 시각이지만 시장자료 수집은 하지 않는다.

## replay

아래 명령은 인터넷·API 키·LLM·test 모듈 없이 저장된 입력과 snapshot을 검증하고 원래 보고서를 출력한다.

```bash
python -m investment_research ask --replay examples/ask_orchestrator/btc_live
python -m investment_research ask --replay examples/ask_orchestrator/scan_live
python -m investment_research ask --replay examples/ask_orchestrator/compare_live
python -m investment_research ask --replay examples/ask_orchestrator/portfolio_unknown
python -m investment_research ask --replay examples/ask_orchestrator/portfolio_synthetic
```

동일 질문을 새로 live 조사하려면 새 run directory로 일반 `ask`를 실행한다. 기존 예제의 날짜나 pins를 바꾸어 현재 분석으로 게시하지 않는다. 새로운 보고서 사본이 필요하면 replay에 실행 디렉터리 밖의 `--output`을 지정한다.

각 폴더의 `input.json`, source/macro 계획·pins·snapshot, 해당하는 review, `run_manifest.json`이 질문·실제 scope·접근 출처·사용 근거·평가 주장·계산 입력·reasoning·counterargument·누락 질문·artifact/report 해시를 추적한다. `follow_up_reference`에 run/subject ID를 남기지만 완전한 대화 기억은 구현하지 않았다. 미지원 지역 실거래나 등록되지 않은 기업을 다른 자산의 자료로 대체하지 않는다.

## 검증

Python 3.12.14에서 기존 205개 + 새 31개, 전체 **236개 테스트**가 통과한다. HTTP/DNS를 차단해 위 다섯 사례의 API·CLI replay가 보고서와 모든 artifact를 같은 바이트로 유지함을 확인했다. 모든 본문 참조가 근거 부록 anchor에 연결되고 계산·claim·reasoning의 사용 근거도 manifest에서 확인했다. 기존 다섯 보고서와 기존 예제 파일 251개는 그대로 보존했다.

현재 가장 큰 한계는 검토된 정확한 구절·판본에 의존하고 새로운 데이터 판본을 자율 조사하지 않는 점이다. BTC 가격·BTC별 flow·파생/network와 특정 지역 실거래·일반 consensus 패널은 공백이다. 현재 지원·입력 계약은 [orchestrator 안내](../../docs/research-orchestrator.md)를 따른다.
