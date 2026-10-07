# 투자 질문에 대한 조사 결과

**질문:** 내 포트폴리오 괜찮아?

정보 기준: 2026-09-10T12:00:00+00:00 / 2026-09-10T21:00:00+09:00 (한국시간).

## 결론

**합성 검증 자료가 포함된 예제다. 실제 투자 판단에 사용하지 않는다.**

제공된 보유표로 계산 가능한 구성은 확인했다. 이 계산이 적정 배분이나 전체 포트폴리오의 안전성을 증명하지는 않는다. ([판단 근거](#opportunity-0ba4e6fd875567bb9a01ce7919798f7e936e8402342a11a2e150730c3498b641))
확보한 자료와 남은 공백을 함께 보면, 현재 가격에서 투자 매력이 충분하다고 확정할 근거는 부족하다. 조사 가능한 부분의 결과를 아래에 정리했다.

매수·매도 명령·미래 수익률·투자 순위·최적 비중은 생성하지 않았다. 결론 유보만으로 현금이 우월하다고 판단하지 않는다.

## 원문에서 확인한 가격·이익·금리 자료

P/E는 주가가 이익의 몇 배인지 나타낸다. forward는 앞으로 예상되는 이익, trailing은 이미 기록된 이익이다. FY1은 다음 회계연도라 앞으로의 일정 기간과 정의가 다를 수 있다.

| 항목 | 값 | 관측일 | 근거 |
| --- | --- | --- | --- |
| 합성 F\_PE | 20.000 배 | 2026-09-10 | [자료 확인](#opportunity-85e43e67b246f03b58db36af129f999ae4788915be45426a96e9d8f5031725e3) |
| 합성 F\_TREASURY | 3.000 % | 2026-09-10 | [자료 확인](#opportunity-7224142aa5ac7ebc71edee0b417c6b93f9d5c040bcb259ea461d8eb384a269ad) |

관측일·분모·기간이 다른 값은 같은 배수·수익률로 합치지 않는다. 이익 전망·실제 이익·현재 금리는 서로 다른 종류의 자료다.

## 확인한 계산과 현재 비교 수치

| 항목 | 값 | 의미와 한계 |
| --- | --- | --- |
| 직전 관측치 대비 변화 | 10.000 원/달러 ([계산 확인](#opportunity-8ae8002f47aece4696a0adab214599f88d41133b47afe4a6c598e86311c4dbc7)) | 결측 보간/forward-fill 없음 |
| 직전 관측치 대비 변화 | 0.500 %p ([계산 확인](#opportunity-c3b7a8c8ec30dcdbe248e6be24ee57881686ab162e2ff49a7814b790cd631dff)) | 결측 보간/forward-fill 없음 |
| 직전 관측치 대비 변화 | 0.500 %p ([계산 확인](#opportunity-82518adebd0ff216c1637a7022c8c246d6c2ef2ab91d93b99a63b85048f1e269)) | 결측 보간/forward-fill 없음 |
| 10년−2년 국채 수익률 차이 | 1.500 %p ([계산 확인](#opportunity-1087f2d54ea5ddbd8a6349ceef65162a17cc0229f5db0cc5c2416893351f2dfd)) | 결측 보간/forward-fill 없음 |
| 합성 이익수익률 | 5.000 % ([계산 확인](#opportunity-08032a3743508f2b94e3345f8a120de9a96b9325bb9fa2a0ba2a615e07bd20ca)) | 합성 입력, 미래 수익 아님 |
| 합성 이익수익률과 국채의 차이 | 2.000 %p ([계산 확인](#opportunity-2b72b220b401c0be5c64719de5ad955969b73a9997a9566b5d6754d201af7b0b)) | 합성 입력, ERP 아님 |
| 제공된 전체 보유 평가액과 현금 합계 | 10000000.000 원 ([계산 확인](#opportunity-46cc475a6a6edd04fc003d4ead1e8f790b535689158dc51cd4a370a15f799f20)) | 제공된 KRW 평가액의 합계다. 외부 가격·전체 계좌의 정확성을 검증한 값은 아니다. |
| STOCK의 제공된 평가액 비중 | 60.000 % ([계산 확인](#opportunity-a42c19a7d5f42f743b194260da72765cb22ed379bdc828b9c978c0d3dfe5ddf6)) | 분모는 제공된 보유액과 현금 합계다. 권고·적정 비중이 아니다. |
| COIN의 제공된 평가액 비중 | 20.000 % ([계산 확인](#opportunity-96d987ae988493e24712db6aee7a696f6548db32ccf335b56ce2268c12201713)) | 분모는 제공된 보유액과 현금 합계다. 권고·적정 비중이 아니다. |
| CASH의 제공된 평가액 비중 | 20.000 % ([계산 확인](#opportunity-f65460cf139235dc1b9a424b31a41d52da7046b6937da04803ae516bc6838b8a)) | 분모는 제공된 보유액과 현금 합계다. 권고·적정 비중이 아니다. |
| 제공된 총자산에서 부채를 뺀 금액 | 9000000.000 원 ([계산 확인](#opportunity-415f2558f60de91cb5f2d586c35d75010609aad686772537dfe9504a8965b263)) | 부채 상환 일정·금리·담보·소득 충격을 평가하지 않는다. |
| 사용자가 나열한 향후 자금수요 합계 | 3000000.000 원 ([계산 확인](#opportunity-966d7d6c694cc0831cf5772b1a7cd44d12f119cd0ae8b2d2c1198e4cd67950fa)) | 여러 필요 시점의 명목 합계다. 시점별 지급 가능성·수익·할인을 추정하지 않는다. |

## 질문에 관련된 시장 환경

| 관측 | 관측일 | 값 | 근거 |
| --- | --- | --- | --- |
| 합성 달러당 원화 | 2026-09-09 | 1310.000 원/달러 | [자료 확인](#opportunity-59f08f6de13bd52c1768dc44fd865f10bb941759896764ff46ed83b425be37cc) |
| 합성 미국 국채 10년 | 2026-09-09 | 3.500 % | [자료 확인](#opportunity-3690d902090f22f9cf25ca20dbd4c4514452163c536b207188adbf0fbbd64655) |
| 합성 미국 국채 2년 | 2026-09-09 | 2.000 % | [자료 확인](#opportunity-5a699101a3aa29da90189a09e68e6fffb2de10038cffdf5afe5a8a7bd66391eb) |

## 내 보유에 적용할 수 있는 범위

보유 입력의 기준일: 2026-09-10; 전체성: complete. 숫자는 사용자의 자기보고 평가액이다.

제공된 평가액 중 가장 큰 항목: 미국 주식. 이것만으로 과도한 집중이나 적정 비중을 확정하지 않는다.

자산 자체의 매력과 이미 보유한 노출, 추가 자본이 전체 구성에 미치는 영향은 각각 확인해야 한다. ETF 구성·산업·통화·직업/주택 노출의 겹침을 아직 완전히 계산하지 않았다.

## 공개 토론과 실제 근거의 차이

- 관측된 공개 발언이며 내용은 미확인: Authored synthetic participants question durable demand. ([자료 확인](#opportunity-bf415ef1b49892b0b976d55ae96233f4b50137568dd88641e2be1742b48b6d9e))
- 관측된 공개 발언이며 내용은 미확인: Authored synthetic participants question durable demand. ([자료 확인](#opportunity-131d52604f16eb2c47dcc2aa5cdf50d18d8d35afc22d63276d1fd998f676bda5))

목적 표집한 소수 발언이다. 반복·인기는 사실이나 시장 전체의 생각을 증명하지 않는다. 연결된 주장의 검증 기록과 공식 자료를 함께 확인해야 한다.

## 한국 투자자에게 의미하는 것

달러 자산의 사업·계약 경제성과 원화로 평가한 환율 노출을 구분한다. 현재 USD/KRW(달러당 원화) 관측만으로 미래 환율을 예측하지 않는다.

실제 상품·환헤지·계좌·비용·과세 요건이 미확인이면 세후 순위와 개인 추가 투자 비중을 확정하지 않는다.

## 무엇을 더 확인하면 판단이 달라지나

- S&amp;P 500 / 미국 주식: 전체 consensus→actual→후속 revision의 같은 정의 패널
- S&amp;P 500 / 미국 주식: 회사별 현금흐름과 전체 지수 기대의 연결
- Bitcoin: BTC 단독 ETF 일별 순유입과 실제 보유량
- Bitcoin: 가격·거래량·선물 funding/미결제약정·청산·network의 최신 자료
- Bitcoin: 가격의 매력을 판단할 검증된 가치 대용 지표

## 근거와 판단을 직접 확인하기

원문 일치는 발언·공시 구절의 존재를 확인한다. 경제적 해석의 진실·투자 매력은 자동 검증되지 않았으며 검토 전 초안으로 유지한다. 오래되거나 시점이 맞지 않는 자료는 현재 판단에 채택하지 않는다.

<a id="opportunity-93f16cd346fa597765cd93599d76c162381198d7f1b93f581160e718af40ad97"></a>
### 판단의 연결 · INSIGHT\_US\_EQUITY

확보한 valuation·이익 근거는 S&amp;P 500 중심이다. Nasdaq이나 미국 개별주 전체로 일반화하지 않는다. 현재 가격의 매력·미래 수익은 이 자료만으로 확정하지 않는다.

관련 근거: [자료 확인 1](#opportunity-e180108a82a1d68e145b44e788124eef89aa6b4fad284c78ac33cebdacd8663c), [자료 확인 2](#opportunity-4345e4f2e91b0eb6ff1acc53b92b8c735273d1e78179f9db1eebb8dad69dd798), [자료 확인 3](#opportunity-d1c3f021b9bab4393653e7cc32ab9e663140432c1878014c70560460a5874cd1), [자료 확인 4](#opportunity-85e43e67b246f03b58db36af129f999ae4788915be45426a96e9d8f5031725e3), [자료 확인 5](#opportunity-7224142aa5ac7ebc71edee0b417c6b93f9d5c040bcb259ea461d8eb384a269ad); 계산: 현재 확인 가능한 직접 근거 부족

반대 질문: 높은 이익 기대와 금리 대안이 현재 가격의 추가 보상을 줄이는가?

재검토 조건: 예상 이익 상향이 실제 매출·마진·현금흐름으로 이어지는가?

<a id="opportunity-d9c39de1384daba0391ceadb14687ed9a280acbe15511ac33855659c04185b9f"></a>
### 판단의 연결 · INSIGHT\_BTC

IBIT 상품과 제공자의 디지털자산 전체 flow를 구분한다. aggregate flow는 BTC 단독 flow가 아니다. 현재 가격의 매력·미래 수익은 이 자료만으로 확정하지 않는다.

관련 근거: [자료 확인 1](#opportunity-3d8e3c091666185a64ee5e865c96608ed37ad2da4e4f3b645aa1e4979dc3ac8d), [자료 확인 2](#opportunity-632dc13821bcc979a05a50a937334d36598a9829999ade5124fe13d8846dc3bf); 계산: 현재 확인 가능한 직접 근거 부족

반대 질문: 유입 둔화·보관 위험이 강세 논리를 약화시키는가?

재검토 조건: 투자상품의 자금 유입이 Bitcoin 고유 수요의 지속으로 이어지는가?

<a id="opportunity-0ba4e6fd875567bb9a01ce7919798f7e936e8402342a11a2e150730c3498b641"></a>
### 판단의 연결 · INSIGHT\_PORTFOLIO

제공된 보유 구성의 계산과 자산의 시장 매력, 추가 보유의 적절성은 별도 판단이다.

관련 근거: [자료 확인 1](#opportunity-534fa82dfbb8330d7b0f6ebebb41680873886d69f9ecf046c40cc0e9bfd5a12e), [자료 확인 2](#opportunity-0348a87db81067ed99ee339e19734b728989337d4d5d91f6bb5416e27ee64935), [자료 확인 3](#opportunity-d45c5bf0d4e9a7a1da091cf5eda79567cbe41c7d86db0ced4758b6e191e01407), [자료 확인 4](#opportunity-bef2d55b54cb132092e3fe3947db40dae0da80a9ea1c5ba2d45da03f0a55753e), [자료 확인 5](#opportunity-25df8d1f013924c70c94d9587de1b33b5a0ce7aecc8d908598ae1bc71954d360), [자료 확인 6](#opportunity-1005588d847509fd392cb61788cf09c43b4e5e2dfff78af50841017a35f52a1a); 계산: [계산 확인 1](#opportunity-46cc475a6a6edd04fc003d4ead1e8f790b535689158dc51cd4a370a15f799f20), [계산 확인 2](#opportunity-a42c19a7d5f42f743b194260da72765cb22ed379bdc828b9c978c0d3dfe5ddf6), [계산 확인 3](#opportunity-96d987ae988493e24712db6aee7a696f6548db32ccf335b56ce2268c12201713), [계산 확인 4](#opportunity-f65460cf139235dc1b9a424b31a41d52da7046b6937da04803ae516bc6838b8a), [계산 확인 5](#opportunity-415f2558f60de91cb5f2d586c35d75010609aad686772537dfe9504a8965b263), [계산 확인 6](#opportunity-966d7d6c694cc0831cf5772b1a7cd44d12f119cd0ae8b2d2c1198e4cd67950fa)

반대 질문: 좋은 자산도 기존 노출·자금수요·부채에 따라 추가 보유가 적절하지 않을 수 있다.

재검토 조건: 전체 보유와 평가 기준일·현금·부채·향후 자금수요·손실 감당 능력을 확인한다.

<a id="opportunity-bf415ef1b49892b0b976d55ae96233f4b50137568dd88641e2be1742b48b6d9e"></a>
### 근거 · E\_COM\_HN\_BTC\_BEAR\_PERFORMANCE

Authored synthetic participants question durable demand.

출처: [자료 확인](#opportunity-6a7a734c4208d3288e84af5190e15784845c2178549d7d8a3d3018a6f056d79b); 원문 위치: synthetic paragraph.
정의: \{'adjustment': 'authored fixture', 'currency': None, 'measure': 'authored synthetic passage', 'period': 'synthetic snapshot', 'scope': 'synthetic fixture', 'unit': 'text'\}
시점 상태: 최신성 조건 충족; snapshot: fab5887f225a7917ae14641ff2eac4b39cc7295b95c99a3d44853defd4f436ef; 구절: Q\_SYNTHETIC.

<a id="opportunity-131d52604f16eb2c47dcc2aa5cdf50d18d8d35afc22d63276d1fd998f676bda5"></a>
### 근거 · E\_COM\_HN\_BTC\_CUSTODY\_RISK

Authored synthetic participants question durable demand.

출처: [자료 확인](#opportunity-a324428ccba34fb377c7d1cca41ba633ca4582a93a1557f5fab296f5c04775f3); 원문 위치: synthetic paragraph.
정의: \{'adjustment': 'authored fixture', 'currency': None, 'measure': 'authored synthetic passage', 'period': 'synthetic snapshot', 'scope': 'synthetic fixture', 'unit': 'text'\}
시점 상태: 최신성 조건 충족; snapshot: 0b22d7a316667b18fc4936f6c93a5cd55a3d03f9632f14046d3cff3b920273e2; 구절: Q\_SYNTHETIC.

<a id="opportunity-3d8e3c091666185a64ee5e865c96608ed37ad2da4e4f3b645aa1e4979dc3ac8d"></a>
### 근거 · E\_CR\_IBIT\_ISSUER

Authored synthetic issuer describes its economics and risks.

출처: [자료 확인](#opportunity-77fbfa7085e637daa7af246c487943d12eddd8b7a2b09f445d681d041d90683b); 원문 위치: synthetic paragraph.
정의: \{'adjustment': 'authored fixture', 'currency': None, 'measure': 'authored synthetic passage', 'period': 'synthetic snapshot', 'scope': 'synthetic fixture', 'unit': 'text'\}
시점 상태: 최신성 조건 충족; snapshot: 8ac154063ee1dc89ca4f0e9eb094ec0c119c659c0b4ade3c2734e5b5495b698d; 구절: Q\_SYNTHETIC.

<a id="opportunity-632dc13821bcc979a05a50a937334d36598a9829999ade5124fe13d8846dc3bf"></a>
### 근거 · E\_CR\_COINSHARES\_CURRENT\_FLOWS

Authored synthetic issuer describes its economics and risks.

출처: [자료 확인](#opportunity-d1c7daac5621457249d3b9b4356f1e03d35e67211602d65bd04d9e0b42426184); 원문 위치: synthetic paragraph.
정의: \{'adjustment': 'authored fixture', 'currency': None, 'measure': 'authored synthetic passage', 'period': 'synthetic snapshot', 'scope': 'synthetic fixture', 'unit': 'text'\}
시점 상태: 최신성 조건 충족; snapshot: 6706f5790f517c0dba4332cdddc76f026133fd54889e7bd9aa78a67dd81a7342; 구절: Q\_SYNTHETIC.

<a id="opportunity-e180108a82a1d68e145b44e788124eef89aa6b4fad284c78ac33cebdacd8663c"></a>
### 근거 · E\_DD\_IDX\_FACTSET\_Q3

Synthetic fixture only. Forward P/E 20.0; Treasury 3.0 percent.

출처: [자료 확인](#opportunity-a2363a77d9ca915a89649f2ee2d1555fe4cf90ebc42467eb57532c23492cd23f); 원문 위치: synthetic paragraph.
정의: \{'adjustment': 'authored fixture', 'currency': 'USD', 'measure': 'authored synthetic valuation and yield', 'period': 'synthetic snapshot', 'scope': 'synthetic index and Treasury', 'unit': 'ratio and percent'\}
시점 상태: 최신성 조건 충족; snapshot: 70e68011228b27ae252bed8c34e371369ea29ed5243d296cadd4e97cd77c0d07; 구절: Q\_SYNTHETIC.

<a id="opportunity-4345e4f2e91b0eb6ff1acc53b92b8c735273d1e78179f9db1eebb8dad69dd798"></a>
### 근거 · E\_DD\_IDX\_SPY

Authored synthetic issuer describes its economics and risks.

출처: [자료 확인](#opportunity-b3b2aa1a939b74ccffa5a4e1d71c6658758535f8da8309d73896055f1d36e636); 원문 위치: synthetic paragraph.
정의: \{'adjustment': 'authored fixture', 'currency': None, 'measure': 'authored synthetic passage', 'period': 'synthetic snapshot', 'scope': 'synthetic fixture', 'unit': 'text'\}
시점 상태: 최신성 조건 충족; snapshot: 679de074e8a72c79fa12cdf57d37181f76b7c1ab645cfe0894d036a20fc0e4a1; 구절: Q\_SYNTHETIC.

<a id="opportunity-d1c3f021b9bab4393653e7cc32ab9e663140432c1878014c70560460a5874cd1"></a>
### 근거 · E\_DD\_TR\_H15\_CURVE

Synthetic fixture only. Forward P/E 20.0; Treasury 3.0 percent.

출처: [자료 확인](#opportunity-7fcf16b415162ceb577bbc6a78c56d7f8fd2af2f89d0242f91180e4c489053ab); 원문 위치: synthetic paragraph.
정의: \{'adjustment': 'authored fixture', 'currency': 'USD', 'measure': 'authored synthetic valuation and yield', 'period': 'synthetic snapshot', 'scope': 'synthetic index and Treasury', 'unit': 'ratio and percent'\}
시점 상태: 최신성 조건 충족; snapshot: 4ce401f045c4ace518537b9bdb740eb672d7f712419de29d25804bf0891f0104; 구절: Q\_SYNTHETIC.

<a id="opportunity-d967b8173e3c831002cb61514b8cbe895db37d84b5b559b41eef7ae01e69f0d1"></a>
### 근거 · OBS\_37ca53e054042d4dc0645afce032b17472f680936ce1b02916b3d8cf7754f66a

합성 미국 국채 2년; observation=2026-09-08; value=1.50 percent

출처: [자료 확인](#opportunity-e787ac88b25c40e76d527a3dea432be2960264b79f61926f1d2b1cc88dda7b91); 원문 위치: CSV row 7, column RIFLGFCY02\_N.B, Time Period=2026-09-08.
값: 1.50 percent; 기간: daily; 통화: USD.
정의: \{'measure': 'US\_TREASURY\_NOMINAL\_2Y', 'unit': 'percent', 'period': 'daily', 'currency': 'USD', 'adjustment': 'not\_seasonally\_adjusted', 'scope': 'Nominal 2-year Treasury constant maturity yield, synthetic values'\}
시점 상태: 최신성 조건 충족; snapshot: 928e1e09c1082f4f967708ff0a2a879fee492efa1bbf690be313bcf678fa8c60; 구절: OBS\_37ca53e054042d4dc0645afce032b17472f680936ce1b02916b3d8cf7754f66a.

<a id="opportunity-11c7fca77628d6869f95475120baa788a46c8741121ac0d658d48088eeb4f75b"></a>
### 근거 · OBS\_4a7ebb688605194c2b9bca295327a036e69af95851474805ad9846839705f428

합성 미국 국채 10년; observation=2026-09-08; value=3.00 percent

출처: [자료 확인](#opportunity-e787ac88b25c40e76d527a3dea432be2960264b79f61926f1d2b1cc88dda7b91); 원문 위치: CSV row 7, column RIFLGFCY10\_N.B, Time Period=2026-09-08.
값: 3.00 percent; 기간: daily; 통화: USD.
정의: \{'measure': 'US\_TREASURY\_NOMINAL\_10Y', 'unit': 'percent', 'period': 'daily', 'currency': 'USD', 'adjustment': 'not\_seasonally\_adjusted', 'scope': 'Nominal 10-year Treasury constant maturity yield, synthetic values'\}
시점 상태: 최신성 조건 충족; snapshot: 928e1e09c1082f4f967708ff0a2a879fee492efa1bbf690be313bcf678fa8c60; 구절: OBS\_4a7ebb688605194c2b9bca295327a036e69af95851474805ad9846839705f428.

<a id="opportunity-3690d902090f22f9cf25ca20dbd4c4514452163c536b207188adbf0fbbd64655"></a>
### 근거 · OBS\_6333f059b7c0f680dc1be5c70e8133446f7c65ca90c30753c6f0825a95adf3a8

합성 미국 국채 10년; observation=2026-09-09; value=3.50 percent

출처: [자료 확인](#opportunity-e787ac88b25c40e76d527a3dea432be2960264b79f61926f1d2b1cc88dda7b91); 원문 위치: CSV row 8, column RIFLGFCY10\_N.B, Time Period=2026-09-09.
값: 3.50 percent; 기간: daily; 통화: USD.
정의: \{'measure': 'US\_TREASURY\_NOMINAL\_10Y', 'unit': 'percent', 'period': 'daily', 'currency': 'USD', 'adjustment': 'not\_seasonally\_adjusted', 'scope': 'Nominal 10-year Treasury constant maturity yield, synthetic values'\}
시점 상태: 최신성 조건 충족; snapshot: 928e1e09c1082f4f967708ff0a2a879fee492efa1bbf690be313bcf678fa8c60; 구절: OBS\_6333f059b7c0f680dc1be5c70e8133446f7c65ca90c30753c6f0825a95adf3a8.

<a id="opportunity-59f08f6de13bd52c1768dc44fd865f10bb941759896764ff46ed83b425be37cc"></a>
### 근거 · OBS\_772b7be89563c67aa881f888b2f99cbe2ce812a59e4a2f825f36d2defb015976

합성 달러당 원화; observation=2026-09-09; value=1310 KRW\_per\_USD

출처: [자료 확인](#opportunity-bf41cd7205fbc3d1a780eb2b31b7ea60671426e0d55947b4f2fb39abd870dd59); 원문 위치: CSV row 8, column RXI\_N.B.KO, Time Period=2026-09-09.
값: 1310 KRW\_per\_USD; 기간: daily; 통화: KRW.
정의: \{'measure': 'USD\_KRW\_NOON\_REFERENCE', 'unit': 'KRW\_per\_USD', 'period': 'daily', 'currency': 'KRW', 'adjustment': 'not\_seasonally\_adjusted', 'scope': 'KRW per one USD, synthetic values'\}
시점 상태: 최신성 조건 충족; snapshot: a044b226681a6387af1672ff3dd41bc5dc09b704c2dccae3ccabf49d7947f2ee; 구절: OBS\_772b7be89563c67aa881f888b2f99cbe2ce812a59e4a2f825f36d2defb015976.

<a id="opportunity-5a699101a3aa29da90189a09e68e6fffb2de10038cffdf5afe5a8a7bd66391eb"></a>
### 근거 · OBS\_7d4a276ab88b493bf9842e73f10ce791c961b71887342389239c15a10b6132b9

합성 미국 국채 2년; observation=2026-09-09; value=2.00 percent

출처: [자료 확인](#opportunity-e787ac88b25c40e76d527a3dea432be2960264b79f61926f1d2b1cc88dda7b91); 원문 위치: CSV row 8, column RIFLGFCY02\_N.B, Time Period=2026-09-09.
값: 2.00 percent; 기간: daily; 통화: USD.
정의: \{'measure': 'US\_TREASURY\_NOMINAL\_2Y', 'unit': 'percent', 'period': 'daily', 'currency': 'USD', 'adjustment': 'not\_seasonally\_adjusted', 'scope': 'Nominal 2-year Treasury constant maturity yield, synthetic values'\}
시점 상태: 최신성 조건 충족; snapshot: 928e1e09c1082f4f967708ff0a2a879fee492efa1bbf690be313bcf678fa8c60; 구절: OBS\_7d4a276ab88b493bf9842e73f10ce791c961b71887342389239c15a10b6132b9.

<a id="opportunity-32bff80d42a5d2c3236108871df19bc10df973f9e64198f3f40cd9e15373ade1"></a>
### 근거 · OBS\_baa1c8a7706744a4ec4b2376c237147a4975fce54e4c18ad9ed25904aced71d0

합성 달러당 원화; observation=2026-09-08; value=1300 KRW\_per\_USD

출처: [자료 확인](#opportunity-bf41cd7205fbc3d1a780eb2b31b7ea60671426e0d55947b4f2fb39abd870dd59); 원문 위치: CSV row 7, column RXI\_N.B.KO, Time Period=2026-09-08.
값: 1300 KRW\_per\_USD; 기간: daily; 통화: KRW.
정의: \{'measure': 'USD\_KRW\_NOON\_REFERENCE', 'unit': 'KRW\_per\_USD', 'period': 'daily', 'currency': 'KRW', 'adjustment': 'not\_seasonally\_adjusted', 'scope': 'KRW per one USD, synthetic values'\}
시점 상태: 최신성 조건 충족; snapshot: a044b226681a6387af1672ff3dd41bc5dc09b704c2dccae3ccabf49d7947f2ee; 구절: OBS\_baa1c8a7706744a4ec4b2376c237147a4975fce54e4c18ad9ed25904aced71d0.

<a id="opportunity-85e43e67b246f03b58db36af129f999ae4788915be45426a96e9d8f5031725e3"></a>
### 근거 · F\_PE

Forward P/E 20.0

출처: [자료 확인](#opportunity-a2363a77d9ca915a89649f2ee2d1555fe4cf90ebc42467eb57532c23492cd23f); 원문 위치: synthetic paragraph.
값: 20.0 ratio; 기간: synthetic snapshot; 통화: USD.
정의: \{'adjustment': 'authored fixture', 'currency': 'USD', 'measure': '합성 F\_PE', 'period': 'synthetic snapshot', 'scope': 'SYNTHETIC', 'unit': 'ratio'\}
시점 상태: 최신성 조건 충족; snapshot: 70e68011228b27ae252bed8c34e371369ea29ed5243d296cadd4e97cd77c0d07; 구절: Q\_SYNTHETIC.

<a id="opportunity-7224142aa5ac7ebc71edee0b417c6b93f9d5c040bcb259ea461d8eb384a269ad"></a>
### 근거 · F\_TREASURY

Treasury 3.0 percent

출처: [자료 확인](#opportunity-7fcf16b415162ceb577bbc6a78c56d7f8fd2af2f89d0242f91180e4c489053ab); 원문 위치: synthetic paragraph.
값: 3.0 percent; 기간: synthetic snapshot; 통화: USD.
정의: \{'adjustment': 'authored fixture', 'currency': 'USD', 'measure': '합성 F\_TREASURY', 'period': 'synthetic snapshot', 'scope': 'SYNTHETIC', 'unit': 'percent'\}
시점 상태: 최신성 조건 충족; snapshot: 4ce401f045c4ace518537b9bdb740eb672d7f712419de29d25804bf0891f0104; 구절: Q\_SYNTHETIC.

<a id="opportunity-534fa82dfbb8330d7b0f6ebebb41680873886d69f9ecf046c40cc0e9bfd5a12e"></a>
### 근거 · PORT\_VALUE\_STOCK

미국 주식 · 사용자 제공 값

출처: [자료 확인](#opportunity-efbc442da75fd5b9759de9ef647724dcf38c2b90040f31fe45292307811bc1f4); 원문 위치: PORT\_VALUE\_STOCK.
값: 6000000 KRW; 기간: self\_reported\_snapshot; 통화: KRW.
사용자가 제공한 값이며 실제 계좌 잔액의 외부 확인이 아니다.

<a id="opportunity-0348a87db81067ed99ee339e19734b728989337d4d5d91f6bb5416e27ee64935"></a>
### 근거 · PORT\_VALUE\_COIN

Bitcoin · 사용자 제공 값

출처: [자료 확인](#opportunity-efbc442da75fd5b9759de9ef647724dcf38c2b90040f31fe45292307811bc1f4); 원문 위치: PORT\_VALUE\_COIN.
값: 2000000 KRW; 기간: self\_reported\_snapshot; 통화: KRW.
사용자가 제공한 값이며 실제 계좌 잔액의 외부 확인이 아니다.

<a id="opportunity-d45c5bf0d4e9a7a1da091cf5eda79567cbe41c7d86db0ced4758b6e191e01407"></a>
### 근거 · PORT\_CASH

cash\_krw · 사용자 제공 값

출처: [자료 확인](#opportunity-efbc442da75fd5b9759de9ef647724dcf38c2b90040f31fe45292307811bc1f4); 원문 위치: PORT\_CASH.
값: 2000000 KRW; 기간: self\_reported\_snapshot; 통화: KRW.
사용자가 제공한 값이며 실제 계좌 잔액의 외부 확인이 아니다.

<a id="opportunity-bef2d55b54cb132092e3fe3947db40dae0da80a9ea1c5ba2d45da03f0a55753e"></a>
### 근거 · PORT\_DEBT

debt\_krw · 사용자 제공 값

출처: [자료 확인](#opportunity-efbc442da75fd5b9759de9ef647724dcf38c2b90040f31fe45292307811bc1f4); 원문 위치: PORT\_DEBT.
값: 1000000 KRW; 기간: self\_reported\_snapshot; 통화: KRW.
사용자가 제공한 값이며 실제 계좌 잔액의 외부 확인이 아니다.

<a id="opportunity-25df8d1f013924c70c94d9587de1b33b5a0ce7aecc8d908598ae1bc71954d360"></a>
### 근거 · PORT\_MONTHLY

monthly\_investable\_krw · 사용자 제공 값

출처: [자료 확인](#opportunity-efbc442da75fd5b9759de9ef647724dcf38c2b90040f31fe45292307811bc1f4); 원문 위치: PORT\_MONTHLY.
값: 500000 KRW; 기간: self\_reported\_snapshot; 통화: KRW.
사용자가 제공한 값이며 실제 계좌 잔액의 외부 확인이 아니다.

<a id="opportunity-1005588d847509fd392cb61788cf09c43b4e5e2dfff78af50841017a35f52a1a"></a>
### 근거 · PORT\_NEED\_0

합성 이사 비용 · 사용자 제공 값

출처: [자료 확인](#opportunity-efbc442da75fd5b9759de9ef647724dcf38c2b90040f31fe45292307811bc1f4); 원문 위치: PORT\_NEED\_0.
값: 3000000 KRW; 기간: self\_reported\_snapshot; 통화: KRW.
사용자가 제공한 값이며 실제 계좌 잔액의 외부 확인이 아니다.

<a id="opportunity-8ae8002f47aece4696a0adab214599f88d41133b47afe4a6c598e86311c4dbc7"></a>
### 계산 · MET\_fb38e689bdce9ccffc95bc569bd02d5e1ad3c01db2084cc3d9eb31c2014b1485

10 KRW\_per\_USD; 방법: previous\_change\_v1.

입력: [자료 확인 1](#opportunity-32bff80d42a5d2c3236108871df19bc10df973f9e64198f3f40cd9e15373ade1), [자료 확인 2](#opportunity-59f08f6de13bd52c1768dc44fd865f10bb941759896764ff46ed83b425be37cc)

<a id="opportunity-c3b7a8c8ec30dcdbe248e6be24ee57881686ab162e2ff49a7814b790cd631dff"></a>
### 계산 · MET\_79cbbcaf624b436e994db6310b1fc4c195cd94dfbe999dab03bff2bd6ef525a1

0.50 percentage\_points; 방법: previous\_change\_v1.

입력: [자료 확인 1](#opportunity-11c7fca77628d6869f95475120baa788a46c8741121ac0d658d48088eeb4f75b), [자료 확인 2](#opportunity-3690d902090f22f9cf25ca20dbd4c4514452163c536b207188adbf0fbbd64655)

<a id="opportunity-82518adebd0ff216c1637a7022c8c246d6c2ef2ab91d93b99a63b85048f1e269"></a>
### 계산 · MET\_a62cf22b20a7883ce4ac04181e039220df715a8a086711de475f6e72a3efd230

0.50 percentage\_points; 방법: previous\_change\_v1.

입력: [자료 확인 1](#opportunity-d967b8173e3c831002cb61514b8cbe895db37d84b5b559b41eef7ae01e69f0d1), [자료 확인 2](#opportunity-5a699101a3aa29da90189a09e68e6fffb2de10038cffdf5afe5a8a7bd66391eb)

<a id="opportunity-1087f2d54ea5ddbd8a6349ceef65162a17cc0229f5db0cc5c2416893351f2dfd"></a>
### 계산 · MET\_586fd48cc159c2051aa0140188a349034634d1a85d22ebdc708eddfe8f183046

1.50 percentage\_points; 방법: yield\_spread\_v1.

입력: [자료 확인 1](#opportunity-3690d902090f22f9cf25ca20dbd4c4514452163c536b207188adbf0fbbd64655), [자료 확인 2](#opportunity-5a699101a3aa29da90189a09e68e6fffb2de10038cffdf5afe5a8a7bd66391eb)

<a id="opportunity-08032a3743508f2b94e3345f8a120de9a96b9325bb9fa2a0ba2a615e07bd20ca"></a>
### 계산 · CALC\_EY

5 percent; 방법: earnings\_yield\_v1.

입력: [자료 확인](#opportunity-85e43e67b246f03b58db36af129f999ae4788915be45426a96e9d8f5031725e3)

<a id="opportunity-2b72b220b401c0be5c64719de5ad955969b73a9997a9566b5d6754d201af7b0b"></a>
### 계산 · CALC\_GAP

2.0 percentage\_points; 방법: descriptive\_yield\_gap\_v1.

입력: [자료 확인 1](#opportunity-85e43e67b246f03b58db36af129f999ae4788915be45426a96e9d8f5031725e3), [자료 확인 2](#opportunity-7224142aa5ac7ebc71edee0b417c6b93f9d5c040bcb259ea461d8eb384a269ad)

<a id="opportunity-46cc475a6a6edd04fc003d4ead1e8f790b535689158dc51cd4a370a15f799f20"></a>
### 계산 · PORT\_TOTAL

10000000 KRW; 방법: portfolio\_total\_v1.

입력: [자료 확인 1](#opportunity-534fa82dfbb8330d7b0f6ebebb41680873886d69f9ecf046c40cc0e9bfd5a12e), [자료 확인 2](#opportunity-0348a87db81067ed99ee339e19734b728989337d4d5d91f6bb5416e27ee64935), [자료 확인 3](#opportunity-d45c5bf0d4e9a7a1da091cf5eda79567cbe41c7d86db0ced4758b6e191e01407)

<a id="opportunity-a42c19a7d5f42f743b194260da72765cb22ed379bdc828b9c978c0d3dfe5ddf6"></a>
### 계산 · PORT\_WEIGHT\_STOCK

60.0 percent; 방법: portfolio\_weight\_v1.

입력: [자료 확인 1](#opportunity-534fa82dfbb8330d7b0f6ebebb41680873886d69f9ecf046c40cc0e9bfd5a12e), [자료 확인 2](#opportunity-0348a87db81067ed99ee339e19734b728989337d4d5d91f6bb5416e27ee64935), [자료 확인 3](#opportunity-d45c5bf0d4e9a7a1da091cf5eda79567cbe41c7d86db0ced4758b6e191e01407)

<a id="opportunity-96d987ae988493e24712db6aee7a696f6548db32ccf335b56ce2268c12201713"></a>
### 계산 · PORT\_WEIGHT\_COIN

20.0 percent; 방법: portfolio\_weight\_v1.

입력: [자료 확인 1](#opportunity-534fa82dfbb8330d7b0f6ebebb41680873886d69f9ecf046c40cc0e9bfd5a12e), [자료 확인 2](#opportunity-0348a87db81067ed99ee339e19734b728989337d4d5d91f6bb5416e27ee64935), [자료 확인 3](#opportunity-d45c5bf0d4e9a7a1da091cf5eda79567cbe41c7d86db0ced4758b6e191e01407)

<a id="opportunity-f65460cf139235dc1b9a424b31a41d52da7046b6937da04803ae516bc6838b8a"></a>
### 계산 · PORT\_WEIGHT\_CASH

20.0 percent; 방법: portfolio\_weight\_v1.

입력: [자료 확인 1](#opportunity-534fa82dfbb8330d7b0f6ebebb41680873886d69f9ecf046c40cc0e9bfd5a12e), [자료 확인 2](#opportunity-0348a87db81067ed99ee339e19734b728989337d4d5d91f6bb5416e27ee64935), [자료 확인 3](#opportunity-d45c5bf0d4e9a7a1da091cf5eda79567cbe41c7d86db0ced4758b6e191e01407)

<a id="opportunity-415f2558f60de91cb5f2d586c35d75010609aad686772537dfe9504a8965b263"></a>
### 계산 · PORT\_NET\_ASSETS

9000000 KRW; 방법: portfolio\_net\_assets\_v1.

입력: [자료 확인 1](#opportunity-534fa82dfbb8330d7b0f6ebebb41680873886d69f9ecf046c40cc0e9bfd5a12e), [자료 확인 2](#opportunity-0348a87db81067ed99ee339e19734b728989337d4d5d91f6bb5416e27ee64935), [자료 확인 3](#opportunity-d45c5bf0d4e9a7a1da091cf5eda79567cbe41c7d86db0ced4758b6e191e01407), [자료 확인 4](#opportunity-bef2d55b54cb132092e3fe3947db40dae0da80a9ea1c5ba2d45da03f0a55753e)

<a id="opportunity-966d7d6c694cc0831cf5772b1a7cd44d12f119cd0ae8b2d2c1198e4cd67950fa"></a>
### 계산 · PORT\_CASH\_NEEDS

3000000 KRW; 방법: portfolio\_cash\_needs\_v1.

입력: [자료 확인](#opportunity-1005588d847509fd392cb61788cf09c43b4e5e2dfff78af50841017a35f52a1a)

<a id="opportunity-6a7a734c4208d3288e84af5190e15784845c2178549d7d8a3d3018a6f056d79b"></a>
### 출처 · Synthetic fixture, never live evidence

[원문](<https://synthetic-ask.example.org/com_hn_btc_bear_performance>)
출처 상태: 확보; 시점: 최신성 조건 충족.
관측: 2026-09-10T11:00:00Z; 공개: 2026-09-10T11:00:00Z; 획득: 2026-09-10T12:00:00Z.
보존 조건: Authored synthetic fixture retained only for offline tests.; 정책: [확인](<https://synthetic-ask.example.org/terms>)
snapshot: fab5887f225a7917ae14641ff2eac4b39cc7295b95c99a3d44853defd4f436ef; 보존 payload SHA-256: 223b448672def8b2cb98e96772600e165d8077a2c6bbd84dd9b8ef880ea4232b.

<a id="opportunity-a324428ccba34fb377c7d1cca41ba633ca4582a93a1557f5fab296f5c04775f3"></a>
### 출처 · Synthetic fixture, never live evidence

[원문](<https://synthetic-ask.example.org/com_hn_btc_custody_risk>)
출처 상태: 확보; 시점: 최신성 조건 충족.
관측: 2026-09-10T11:00:00Z; 공개: 2026-09-10T11:00:00Z; 획득: 2026-09-10T12:00:00Z.
보존 조건: Authored synthetic fixture retained only for offline tests.; 정책: [확인](<https://synthetic-ask.example.org/terms>)
snapshot: 0b22d7a316667b18fc4936f6c93a5cd55a3d03f9632f14046d3cff3b920273e2; 보존 payload SHA-256: 223b448672def8b2cb98e96772600e165d8077a2c6bbd84dd9b8ef880ea4232b.

<a id="opportunity-d1c7daac5621457249d3b9b4356f1e03d35e67211602d65bd04d9e0b42426184"></a>
### 출처 · Synthetic fixture, never live evidence

[원문](<https://synthetic-ask.example.org/cr_coinshares_current_flows>)
출처 상태: 확보; 시점: 최신성 조건 충족.
관측: 2026-09-10T11:00:00Z; 공개: 2026-09-10T11:00:00Z; 획득: 2026-09-10T12:00:00Z.
보존 조건: Authored synthetic fixture retained only for offline tests.; 정책: [확인](<https://synthetic-ask.example.org/terms>)
snapshot: 6706f5790f517c0dba4332cdddc76f026133fd54889e7bd9aa78a67dd81a7342; 보존 payload SHA-256: 31248bb7f6e02c56e98965ef2acd044b6a31d3f0c1021002dbb6982f928fcc8a.

<a id="opportunity-77fbfa7085e637daa7af246c487943d12eddd8b7a2b09f445d681d041d90683b"></a>
### 출처 · Synthetic fixture, never live evidence

[원문](<https://synthetic-ask.example.org/cr_ibit_issuer>)
출처 상태: 확보; 시점: 최신성 조건 충족.
관측: 2026-09-10T11:00:00Z; 공개: 2026-09-10T11:00:00Z; 획득: 2026-09-10T12:00:00Z.
보존 조건: Authored synthetic fixture retained only for offline tests.; 정책: [확인](<https://synthetic-ask.example.org/terms>)
snapshot: 8ac154063ee1dc89ca4f0e9eb094ec0c119c659c0b4ade3c2734e5b5495b698d; 보존 payload SHA-256: 31248bb7f6e02c56e98965ef2acd044b6a31d3f0c1021002dbb6982f928fcc8a.

<a id="opportunity-a2363a77d9ca915a89649f2ee2d1555fe4cf90ebc42467eb57532c23492cd23f"></a>
### 출처 · Synthetic fixture, never live evidence

[원문](<https://synthetic-ask.example.org/dd_idx_factset_q3>)
출처 상태: 확보; 시점: 최신성 조건 충족.
관측: 2026-09-10T11:00:00Z; 공개: 2026-09-10T11:00:00Z; 획득: 2026-09-10T12:00:00Z.
보존 조건: Authored synthetic fixture retained only for offline tests.; 정책: [확인](<https://synthetic-ask.example.org/terms>)
snapshot: 70e68011228b27ae252bed8c34e371369ea29ed5243d296cadd4e97cd77c0d07; 보존 payload SHA-256: c508b1ba656d1c88673b3e1d615187f08e7034124b2627173a8333bf6f687a94.

<a id="opportunity-b3b2aa1a939b74ccffa5a4e1d71c6658758535f8da8309d73896055f1d36e636"></a>
### 출처 · Synthetic fixture, never live evidence

[원문](<https://synthetic-ask.example.org/dd_idx_spy>)
출처 상태: 확보; 시점: 최신성 조건 충족.
관측: 2026-09-10T11:00:00Z; 공개: 2026-09-10T11:00:00Z; 획득: 2026-09-10T12:00:00Z.
보존 조건: Authored synthetic fixture retained only for offline tests.; 정책: [확인](<https://synthetic-ask.example.org/terms>)
snapshot: 679de074e8a72c79fa12cdf57d37181f76b7c1ab645cfe0894d036a20fc0e4a1; 보존 payload SHA-256: 31248bb7f6e02c56e98965ef2acd044b6a31d3f0c1021002dbb6982f928fcc8a.

<a id="opportunity-7fcf16b415162ceb577bbc6a78c56d7f8fd2af2f89d0242f91180e4c489053ab"></a>
### 출처 · Synthetic fixture, never live evidence

[원문](<https://synthetic-ask.example.org/dd_tr_h15_curve>)
출처 상태: 확보; 시점: 최신성 조건 충족.
관측: 2026-09-10T11:00:00Z; 공개: 2026-09-10T11:00:00Z; 획득: 2026-09-10T12:00:00Z.
보존 조건: Authored synthetic fixture retained only for offline tests.; 정책: [확인](<https://synthetic-ask.example.org/terms>)
snapshot: 4ce401f045c4ace518537b9bdb740eb672d7f712419de29d25804bf0891f0104; 보존 payload SHA-256: c508b1ba656d1c88673b3e1d615187f08e7034124b2627173a8333bf6f687a94.

<a id="opportunity-e787ac88b25c40e76d527a3dea432be2960264b79f61926f1d2b1cc88dda7b91"></a>
### 출처 · Synthetic fixture, never actual market evidence

[원문](<https://synthetic-macro.example.org/s_yields>)
출처 상태: 확보; 시점: per\_observation.
관측: UNKNOWN; 공개: UNKNOWN; 획득: 2026-09-10T12:00:00Z.
보존 조건: Synthetic HTTP fixture retained for offline tests only.; 정책: [확인](<https://synthetic-macro.example.org/terms>)
snapshot: 928e1e09c1082f4f967708ff0a2a879fee492efa1bbf690be313bcf678fa8c60; 보존 payload SHA-256: d61f4a454435db628e318c6a56870cab5222fa8a6fb7585228b022ad5f88397f.

<a id="opportunity-bf41cd7205fbc3d1a780eb2b31b7ea60671426e0d55947b4f2fb39abd870dd59"></a>
### 출처 · Synthetic fixture, never actual market evidence

[원문](<https://synthetic-macro.example.org/s_fx>)
출처 상태: 확보; 시점: per\_observation.
관측: UNKNOWN; 공개: UNKNOWN; 획득: 2026-09-10T12:00:00Z.
보존 조건: Synthetic HTTP fixture retained for offline tests only.; 정책: [확인](<https://synthetic-macro.example.org/terms>)
snapshot: a044b226681a6387af1672ff3dd41bc5dc09b704c2dccae3ccabf49d7947f2ee; 보존 payload SHA-256: c028fdf2b7734ba921e11fe54278c1e74b3b52fbc0ff61403d3fe6d25d6259bb.

<a id="opportunity-efbc442da75fd5b9759de9ef647724dcf38c2b90040f31fe45292307811bc1f4"></a>
### 출처 · 사용자가 제공한 KRW 보유 입력

사용자의 로컬 입력을 추적한다. 자기보고이며 공개 금융 데이터의 출처와 구분한다.

