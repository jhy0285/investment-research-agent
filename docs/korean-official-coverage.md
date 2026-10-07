# 한국 시장 원자료 coverage

자연어 질문 해석은 기존 routing v4와 query-understanding v1을 그대로 사용한다. 이번 변경은 **이미 해석한 국가·만기·기업·지역에 맞는 실제 자료**를 연결한다. `routing.py`, `query_understanding.py`는 변경하지 않았다. 최초 세 질문의 전후 차이는 [실전 검증 기록](../reports/korean_coverage_validation_20261005T092721Z/coverage_validation.md), 이후 기업의 가격·EPS·이익의 질 보완은 [반도체 비교](korean-semiconductor-comparison.md)에 정리했다.

## 연결한 자료와 지원 범위

| 영역 | 원자료와 경로 | 확보하는 내용 | 여전히 제한되는 판단 |
| --- | --- | --- | --- |
| 한국 국채 | 한국은행 ECOS `StatisticSearch`, 통계 `817Y002` 시장금리(일별) | 국고채 1·3·5·10년, 연%, 관측일, KRW, 공식 항목 코드와 자료 정의 | 개별 매수 채권/ETF의 가격·실행 YTM·비용·세금, 사용자에게 적절한 배분 |
| 삼성전자 | 공식 발표문·연결 제표 PDF, DART 접수목록, 국내 시세 제공자 | 분기/반기/연간 손익·기본 보통주 EPS·현금흐름·가격·TTM 배수, DS/MX·이익 증가 설명, 발표문 반올림 대조 | DART 본문·정정판, 현재 주식 수/일반 P/B·시가총액, consensus/revision |
| SK하이닉스 | 공식 IR 연결 Euroland, DART 접수목록, 국내 시세 제공자 | 연속 분기 손익·EPS·세전이익·현금흐름 필드, 표시 종가와 잠정 TTM 배수, 이익의 질 단서 | **제공자 자료**다. 원공시의 연결/귀속·영업외 손익·CF 기간, 공식 guidance/사업부·유형자산 CAPEX·일반 P/B·시가총액 |
| 서울·경기·인천 아파트 | 한국부동산원 R-ONE 공식 표 metadata + 지역/항목 코드 + 월별 데이터 API | 각 지역의 조사 매매지수·전세지수·신고 거래호수·실거래 매매지수 | 개별 거래 가격, 단지/면적별 시세, 전세가율·임대수익률, 공급/입주, 대출 조건과 투자 가격의 매력 |

SK하이닉스 공식 IR 연결이라는 사실이 Euroland의 숫자를 regulatory filing으로 바꾸지는 않는다. source type은 `data_provider`, canonical owner는 false로 보존한다. 공식 newsroom은 이번 환경에서 robots 허용을 신뢰성 있게 확인할 수 없었다. 원공시 교차 확인은 미완료다. 이후 삼성전자에는 검토된 작은 개별 PDF 계약을 추가했지만 일반 금융 PDF 수집으로 확대하지 않았다. 접근 제한·파일 제한을 우회하지 않았다.

KRX 직접 대조와 DART 본문 API 권한 연결은 미완료다. 이후 비교에서는 한국경제 코리아마켓의 보통주 표시 종가·실제 날짜를 사용하되 수정 정책 unknown을 공개한다. Samsung IR의 시세 제공자 경로는 robots 제한을 확인했다. 과거 분기 말 주가나 제공자 표의 PSR/PER을 현재 가격/valuation으로 사용하지 않는다. 국토부 개별 실거래 API의 서비스키 연결과 지역별 공급·대출 자료도 미완료다. 미확보 경로와 대체 후보는 `catalog/korean.json` 및 실행의 `input.json`에 남긴다. 비밀 값은 저장하지 않는다.

## 기존 architecture에 연결하는 방식

`ResearchCatalog.korean`은 선택적인 자료 registry다. 기본 live catalog는 이를 로드하고, 별도 fixture/catalog가 `korean=None`이면 기존 coverage만 실행한다. 지원되지 않는 만기·지역/단지는 기존 미지원 결과를 유지한다. 국채 만기는 현재 1·3·5·10년만 연결한다. 아파트 지역은 서울·경기·인천이며, 수도권 질문은 세 지역을 각각 조사한다. 동탄 개별 물건을 경기 전체 통계로 대체하지 않는다.

1. 기존 `Subject`를 `resolve_korean_subject`의 자료 coverage와 대조한다. 질문 해석이나 모드를 새로 만들지 않는다.
2. 한국 국채는 최근 일별 URL과 series definition을 생성해 기존 `load_macro_plan → acquire_macro → replay_macro`를 사용한다. 새 `ecos_daily_v1`은 공식 통계/항목·국가·만기·단위·빈도를 확인한다.
3. 지역 통계와 기업 실적은 기존 `discover_sources`의 need·index·후보·선택·freshness 기록을 사용한다. 지역 표 metadata와 코드 directory, 공식 IR이 연결한 route bundle의 URL literal은 발견 metadata일 뿐 금융 evidence가 아니다.
4. 실제 문서의 검토된 필드 계약을 확인한 뒤 기존 SourceSpec와 `decimal_scalar_v1`에 연결한다. 기존 `acquire_plan → replay_plan`, raw hash·snapshot·exact excerpt·definition 검증을 통과해야 evidence가 된다.
5. `calculate_korean_observations`는 같은 기업/지역·단위·통화·회계/지수 정의·인접 기간의 입력으로만 설명용 계산을 한다. 한국어 보고서에서 근거와 계산 링크, 반대 논리, 미확보 자료를 함께 보여 준다.

별도 수집기·분석 시스템·LLM 판단기·금융사이트 crawler를 만들지 않았다. 일반 요청의 HTTPS·robots·10초 timeout·2 MiB 응답 제한을 유지한다. 새 publisher들을 필요한 질문에만 추가하고 discovery 요청은 최대 32회다. 동일 응답은 discovery부터 acquisition까지 같은 bytes로 재사용한다. 같은 문서에서 나눈 필드/분기는 `origin_source_id`로 연결해 독립 증거로 세지 않는다.

## API와 financial definition의 경계

ECOS의 인증키 없는 공식 `sample` API는 요청당 최대 10행이다. 최근 7일·한 만기만 요청한다. sample이라는 이름은 테스트용 가짜 값이라는 의미가 아니다. 합성 fixture와 실제 공식 응답은 별도로 표시한다. 전체 행수/응답 행수·중복 날짜·항목 코드·이름·연%를 확인하며, 주말 값·누락 값을 생성하지 않는다. 이 수익률은 원화 국고채 **시장 기준금리**이고 쿠폰이나 특정 상품의 실행 YTM이 아니다. 3년 만기가 해당 채권의 수치 duration을 알려주지는 않는다.

R-ONE 공식 API 문서는 KEY를 생략한 sample mode의 최대 5행과 START/END 기간·CLS/ITM 필터를 허용한다. 최근 4개월·한 지역·한 항목으로 제한하고 pagination을 사용하지 않는다. 응답의 전체 행수가 보존한 행수보다 많으면 표본이 잘린 것으로 보고 차단한다. 각 표의 실제 code directory에서 지역명·행정코드와 항목을 찾고, 데이터 응답의 지역명·표 ID·분류 코드·항목·월을 다시 확인한다. **표마다 같은 지역의 코드가 다르다.** 전국 row는 거절한다.

R-ONE은 JSON 요청에도 HTTP `text/html`을 반환한다. 이 실제 header를 보존하며, 검토한 `SttsApiTblData.do?…Type=json`만 strict JSON으로 읽는다. 일반 HTML 응답을 JSON으로 추정하지 않는다. metadata의 `DATA_END_YY`는 일부 표에서 실제 관측보다 오래된 연도로 표시되어 최신성 판단에 사용하지 않는다. 실제 응답의 `WRTTIME_IDTFR_ID`, index 기준시점, 요청한 기간을 확인한다.

Euroland 문서는 표시된 회사 코드와 `LevelZeroItems`라는 JSON literal만 decoding한다. JavaScript를 실행하지 않는다. `str=null, nr=0`은 결측이므로 이익 0으로 바꾸지 않는다. 실제 분기 column과 매출/영업이익/순이익 행의 단위·정렬을 확인한다. 최신 분기의 결측을 전분기의 완성 값으로 채우지 않는다. 제공자의 소수 자릿수는 정확성 보증이 아니다.

삼성전자 분기 발표문은 URL·분기 종료일·공개일과 숫자의 문맥을 함께 확인한다. 본업의 영업이익과 순이익, 매출과 손실, 경영진 기대와 실제 실적을 구분한다. 현재는 검토한 Q2 2026 발표 URL이며 향후 새로운 분기 URL의 자동 발견은 미구현이다. 문구 변경·stale은 gap으로 처리한다.

## Freshness·point-in-time·계산

국채 관측은 기존 macro의 10일 최신성 창을, 지역 월별 자료는 100일, 분기 기업 자료는 135일 창을 쓴다. 이는 질문 관련성의 보수적 범위이며 최신 판본이 없다는 증명이나 신뢰도 점수가 아니다. 마지막 확보월/분기·획득 시각·원문 hash를 함께 공개한다. 월말 날짜는 월의 관측기간 종료일이며 발표일을 뜻하지 않는다.

기업 제공자 문서의 `observed_at/valid_as_of`는 문서에 있는 최종 보고분기 종료일이다. 직전 분기 숫자는 별도의 definition.period를 보존하며 최근 실적처럼 바꾸지 않는다. SK하이닉스 제공자와 지역 통계의 최초 공개/개정 시각은 unknown이다. ECOS도 최초 발표·전체 vintage 이력이 없으므로 기존 macro의 **획득 시각을 known-at 하한으로 쓰는 규칙**을 따른다. 새로운 과거 기준 ask는 기존 지정 날짜 제한을 유지하며 현재 자료로 당시 판단을 만들지 않는다. 저장된 replay만 원래 cutoff를 재현한다.

영업이익/매출과 전분기 변화, 지역별 전월 비율 변화는 Decimal precision 50으로 계산하고 정확한 input ID를 남긴다. 음의 이익은 허용하지만 전분기 기준값이 0/음수면 일반 성장률을 보류한다. 지수의 변화는 `(새 지수/이전 지수−1)×100`이며 지수 차이나 %p로 표현하지 않는다. 서로 다른 지역·기준시점·빈도·중간 월이 빠진 값은 계산하지 않는다. 실거래지수 한 달만 있으면 변화 계산도 없다.

이 계산은 미래 수익·ERP·자산 순위가 아니다. 원화 국고채 금리와 미국 주식의 이익수익률은 통화와 지급 방식이 달라 차감해 우열을 만들지 않는다. 한 분기 EPS를 네 배로 곱해 PER을 만들지 않는다. 월간 거래량 감소는 계절성·신고 시차도 고려해야 하며 가격 하락이나 수요 붕괴의 증명이 아니다.

## 실행과 검증

```bash
python -m investment_research ask '한국 3년 국채랑 S&P500 중 지금 신규자금 어디가 더 합리적이야?'
python -m investment_research ask '삼성전자랑 SK하이닉스 지금 둘 중 뭐가 더 나아?'
python -m investment_research ask '서울/수도권 아파트 지금 투자 관점에서 어때?'
python -m unittest discover -v
```

기존 296개와 새 [29개 합성 fixture 테스트](../tests/test_korean_data.py), 전체 325개가 인터넷 없이 통과했다. 잘못된 만기/단위·결측/잘린 표본·전국/타 지역 대체·index 기준 불명·회사/분기 식별·음의 손익 구절·제공자 위계·외부 지시문·최소 범위·의존 출처·계산의 독립 기대값·traceability·세 질문의 byte-identical replay를 검증한다. 기존 19개 ask replay와 578개 기존 예제/보고서·자연어 파서 파일 hash도 유지했다. 실제 획득 결과와 fixture 검증을 섞지 않는다.

## 다음 기능 하나

**권한 있는 DART 원공시로 SK하이닉스 지배주주 TTM EPS·영업외 손익을 대조**한다. [이후 비교](korean-semiconductor-comparison.md)에서 표시 종가와 잠정 배수까지 연결했지만 분모의 반복 가능성과 제공자 정의의 원공시 확인이 남았다. 이 한 기능은 제안만 하며 후속 구현을 시작하지 않는다.
