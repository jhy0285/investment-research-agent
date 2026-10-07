# Cross-Asset Research Brief

**합성 데이터 · 개발 검증용 보고서입니다. 실제 현재 시장이나 사용자에게 적용할 투자 판단이 아닙니다.**

## 이번에 답하려는 질문

현재 한국의 자산축적기 투자자가 추가 투자자금을 배분한다고 할 때, 현금성 자산, 국채, 주식 노출 중 어떤 선택지를 더 깊게 검토할 가치가 있는가? 이번 답변은 합성 자료로 연구 흐름을 검증한다.

- 정보 기준 시점: 2025-01-31; 기간: 사용자 자기보고상 장기 투자 가능. 추가 자금의 실제 사용 시점은 미확인이다.; 기준 통화: KRW.
- 사용자 정보: PROFILE\_SYNTHETIC\_ACCUMULATION\_V1 / 2025-01-31; 브리프: BRIEF\_SYNTHETIC\_CROSS\_ASSET\_V1.
- 실행 상태: completed; 시장 결론 상태: conditional; 개인 적용 상태: insufficient\_evidence.
- 실행 완료는 투자 결론의 확정을 뜻하지 않으며 결론 유보도 정상 결과다.

## 한눈에 보기

아래 결과는 합성 자료에서 연구 경로를 확인한 결과이며 실제 시장 인사이트가 아니다.

- 현금성 자산 · 합성 KRW 노출: 지지와 반대 근거가 함께 있어 판단 유보 (mixed).
- 국채 · 합성 장기 KRW 노출: 지지와 반대 근거가 함께 있어 판단 유보 (mixed).
- 주식 · 합성 기업군 노출: 지지와 반대 근거가 함께 있어 판단 유보 (mixed).
- 수익 정의와 손실 경로가 다른 대안을 단일 점수·수익률 순위로 합치지 않는다.
- 사용자 미확인 정보에 의존하는 배분 판단을 제한하며, 판단 유보가 현금의 우월성을 입증하지는 않는다.

## 현재 투자환경

- 근거 [E\_POLICY\_RATE](#record-2d5ce882fe0a5ce455a06483e6f4f0b940ddd3743f2d3bef9e2ecb871f7ae186) / 출처 [S\_PRIMARY](#record-af72ce688d370947bb342a086cd221a49008bf9c34e70c1a0856419760b91feb) / 거시환경: 원문·관측 기록: “합성 공식 금리 원자료에 기준 시점의 정책금리가 기록되어 있다.”; 관측 수치: 3.5 %; 기간 정의: annual\_rate; 통화: KRW. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.
- 근거 [E\_LONG\_YIELD](#record-2c6c6df3c0efa5bbc2b390e25c538afcf234109a6dbc96358836bdb14224f4ed) / 출처 [S\_DATA\_PROVIDER](#record-1db310d72eadd453df445bdad57c71c88b22ed530e99f1683423070c6029c075) / 정량: 원문·관측 기록: “합성 관측표에 지정한 장기 국채 노출의 만기수익률이 기록되어 있다.”; 관측 수치: 4.5 %; 기간 정의: annual\_rate; 통화: KRW. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.
- 근거 [E\_INFLATION](#record-0985fac19dc62891dc6b381df424d0c777857b63c0add26f1b76bc933ef1a0f0) / 출처 [S\_PRIMARY](#record-af72ce688d370947bb342a086cd221a49008bf9c34e70c1a0856419760b91feb) / 거시환경: 원문·관측 기록: “합성 공식 물가 원자료에 후행 연간 소비자물가 상승률이 기록되어 있다.”; 관측 수치: 3.0 %; 기간 정의: annual\_rate; 통화: KRW. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.
- 근거 [E\_MARKET\_EXPECTATION](#record-29827c8ee47ede094c9b27b0c8df797f0b20b867a41b668c8fda412c23e8356e) / 출처 [S\_DATA\_PROVIDER](#record-1db310d72eadd453df445bdad57c71c88b22ed530e99f1683423070c6029c075) / 거시환경: 원문·관측 기록: “합성 시장 기대 요약에는 향후 통화정책 완화를 예상하는 가격 해석이 포함되어 있다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.
- 근거 [E\_LIQUIDITY](#record-84da45149546fb5e59c2e7cb8a7d958cc35ed3f1d5fa32d82fd5a12786eed904) / 출처 [S\_RESEARCH](#record-cb4f90a401d7adea71295abb157fc1dcc837114861cd1810a44074067d909831) / 거시환경: 원문·관측 기록: “합성 연구 메모는 지정한 관측 기간의 자금 조달 조건이 이전 비교기간보다 완화된 것으로 요약한다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.

### 검증된 입력으로 계산한 값

- [계산 M\_CASH\_RATE\_GAP] 합성 명목 현금 이자율과 후행 물가상승률의 단순 차이: -0.5 %p (퍼센트포인트).
  방법: rate\_difference\_v1; 입력: [E\_CASH\_RATE](#record-781048addafe3da8e5fdb6886088902e6f492935b262e90f8dcc012c63c39631), [E\_INFLATION](#record-0985fac19dc62891dc6b381df424d0c777857b63c0add26f1b76bc933ef1a0f0); 정의: 첫 입력의 연율 percent 값에서 두 번째 값을 뺀 단순 격차.
  한계: 명목 연 이자율에서 후행 연간 물가상승률을 뺀 기술적 차이이며 단위는 퍼센트포인트다. / 미래 실질수익·사용자 실제 구매력 변화·동일기간 실현 수익이 아니다. / 정확한 복리 실질수익 공식이나 미래 물가 추정을 사용하지 않는다. / 비용·세금은 미확인으로 남기며 계산에 포함하지 않는다. / 이 차이만으로 현금·국채·주식을 순위화하지 않는다. / 두 연율 관측값의 단순 격차다. 관측 물가를 대입해도 미래 실질수익, 확정 투자성과 또는 자산 간 우위를 뜻하지 않는다. 비용·세금·가격변화는 계산하지 않았다.

비교 범위와 제한:

- 기간: 장기 자기보고와 실제 추가 자금의 사용 시점은 구분하며, 동일 보유기간의 미래 성과는 계산하지 않는다.
- 통화: 합성 관측은 KRW 범위로 한정한다. 실제 해외 노출의 원화 환산 자료는 없다.
- 수익 정의: 현금의 명목 연 이자율·국채 만기수익률·주식 이익 증가 구절은 다른 개념이다. 같은 미래 수익률로 순위화하지 않는다.
- 비용: 거래·운용·환전 비용은 미확인이다. 비용을 영으로 채우거나 비용후 결과로 표현하지 않는다.
- 세금: 대한민국 거주자라는 가상 자기보고만 있고 규칙·계좌·개인 과세 자료가 없다. 실제 세금은 계산하지 않는다.
- 환헤지: 실제 외화 노출·헤지 방식·헤지 비용은 미확인이다. 환헤지 성과를 생성하지 않는다.
- 유동성: 합성 현금 인출 조건과 국채·주식 매도 가능성은 구분한다. 매도 가능하다는 사실이 원하는 가격의 회수를 보장하지 않는다.
- 불확실성: 합성 시나리오의 지지·반대 논리를 보여 줄 뿐 미래 수익·상승 확률·최적 투자비중·전체 시장 최선을 판단하지 않는다.

보류·제외한 연구 범위:

- 한국 부동산: 주택 구입 필요자금·지역·주거 목적이 미확인이고 지역별 거래·임대·대출 자료가 없어 보류한다.
- 회사채: 신용·스프레드·발행기관 자료가 없어 보류한다.
- 금·천연가스 등 원자재와 에너지: 수급·선물 구조 자료가 없어 보류한다.
- 암호자산: 네트워크·보관·유동성 근거가 없어 보류한다.
- 개별 미국·한국 종목과 글로벌 ETF 상품: 이번 범위는 합성 경제적 노출 비교이며 상품·계좌 선택은 보류한다.

## 투자대안별 분석

<a id="record-ab0fcec08e18a7bccda1e81df4974e3434fcd36000518f7e776fb85495b5a494"></a>

### 현금성 자산 · 합성 KRW 노출

- 대안 ID: cash; 경제적 노출: cash.
- 수익 정의: 합성 조건표의 세전·비용전 명목 연 이자율. 미래 갱신금리·실현 성과·실질수익률은 계산하지 않는다..
- 유동성·보유 제약: 합성 조건표상 수시 인출 가능. 실제 상품 접근·기관 위험·인출 예외는 미확인이다..
- 결론 강도: 지지와 반대 근거가 함께 있어 판단 유보.

**지지 근거**

- 근거 [E\_CASH\_RATE](#record-781048addafe3da8e5fdb6886088902e6f492935b262e90f8dcc012c63c39631) / 출처 [S\_CASH\_INSTITUTION](#record-78f486e914cbeff24f201dfa85e54dcb4081aebffbd2dee1e7ee2d51cd1c5a84) / 정량: 원문·관측 기록: “합성 현금성 노출 조건표에 명목 연 이자율이 기록되어 있다.”; 관측 수치: 2.5 %; 기간 정의: annual\_rate; 통화: KRW. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.
- 근거 [E\_CASH\_LIQUIDITY](#record-19fad00c610860d07367140fd0f77d2477e1907255efe14aef9248e1734d8244) / 출처 [S\_CASH\_INSTITUTION](#record-78f486e914cbeff24f201dfa85e54dcb4081aebffbd2dee1e7ee2d51cd1c5a84) / 사업·기초가치: 원문·관측 기록: “합성 현금성 노출 조건표는 원화 수시 인출이 가능한 조건을 명시한다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.

**반대 근거**

- 근거 [E\_INFLATION](#record-0985fac19dc62891dc6b381df424d0c777857b63c0add26f1b76bc933ef1a0f0) / 출처 [S\_PRIMARY](#record-af72ce688d370947bb342a086cd221a49008bf9c34e70c1a0856419760b91feb) / 거시환경: 원문·관측 기록: “합성 공식 물가 원자료에 후행 연간 소비자물가 상승률이 기록되어 있다.”; 관측 수치: 3.0 %; 기간 정의: annual\_rate; 통화: KRW. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.
- 근거 [E\_NEWS\_INFLATION](#record-8cfe5eafe56cb2f3f54c08372a8e45691f6127171694038f6986d64665abd301) / 출처 [S\_NEWS](#record-24d3c9a8e7c3bf789ad24de06ac9c6915e3eec4bafbf9524f2567f870167fd4b) / 거시환경: 원문·관측 기록: “합성 경제 기사는 합성 공식 원자료의 후행 물가 관측을 재인용한다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.

**기회비용 · 다른 대안을 선택하지 않을 때 포기할 가능성**

- 비교 대안: 주식 · 합성 기업군 노출. 검토된 조건부 해석: “합성 현금을 유지하면 인출 선택권을 두는 대신 주식의 이익 성장에 참여할 가능성을 포기한다. 그러나 주식의 가격 부담과 참여 범위 약화 위험도 피할 수 있어 실제 미래 차이는 확정할 수 없다.” [근거: [E\_CASH\_LIQUIDITY](#record-19fad00c610860d07367140fd0f77d2477e1907255efe14aef9248e1734d8244), [E\_EARNINGS](#record-044a29f16d42b7f88daddf9dd3238acfdf6e2aa684435f27d77803b7ec528aa5), [E\_VALUATION](#record-94cd9f091e0cf4fe709bd172692a1f2b61d26f138b0b956554f181aad864d7e1), [E\_BREADTH](#record-a700daf2ec08c07d54a71a154fb5522c0c9d7f27a2abd36456c4f9f482c0689b)]. 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 유동성·성장 근거와 주식 반대 자료를 함께 연결한 조건부 기회비용이다. 미래 수익이나 현금 우위를 판단하지 않는다.
- 비교 대안: 국채 · 합성 장기 KRW 노출. 검토된 조건부 해석: “합성 현금을 유지하면 장기 국채 수익률과 정책 완화 기대를 더 조사할 선택을 미루지만, 장기금리 상승에 따른 만기 전 가격 손실을 감수하지 않을 수 있다. 이자율과 만기수익률의 차이를 확정 수익 차이로 바꾸지 않는다.” [근거: [E\_CASH\_RATE](#record-781048addafe3da8e5fdb6886088902e6f492935b262e90f8dcc012c63c39631), [E\_LONG\_YIELD](#record-2c6c6df3c0efa5bbc2b390e25c538afcf234109a6dbc96358836bdb14224f4ed), [E\_MARKET\_EXPECTATION](#record-29827c8ee47ede094c9b27b0c8df797f0b20b867a41b668c8fda412c23e8356e), [E\_BOND\_RISK](#record-9f09c4dbe2b1eb8c64cafd27f753c49cca13059ebaa7fad072342115c6cce057)]. 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 서로 다른 금리 정의와 채권 손실 경로를 공개한 합성 비교다. 실제 동일기간 수익 차이는 계산하지 않는다.

**미확인 사항과 채택을 보류한 자료**

- 비상자금·가까운 자금수요·주택 구입 자금이 미확인이다.
- 실제 현금 상품·비용·세금·기관 위험·향후 이자 조건이 미확인이다.
- 현재 현금 비중을 모르므로 현금이 과도한지 판단할 수 없다.

동일 원출처 중복: [S\_CASH\_INSTITUTION](#record-78f486e914cbeff24f201dfa85e54dcb4081aebffbd2dee1e7ee2d51cd1c5a84), [S\_PRIMARY](#record-af72ce688d370947bb342a086cd221a49008bf9c34e70c1a0856419760b91feb). 해당 재인용·관측은 별도의 독립 근거로 세지 않는다.

관련 계산 ID: [M\_CASH\_RATE\_GAP](#record-b2f1753c14311bc33e661827a5e4a926b0ec47f2427af80e05642dac4093d8de). 계산은 별도 결과이며 지지·반대 근거의 독립 확인으로 중복 계산하지 않는다.

<a id="record-e9c778e2cbb7e6f9dbdbebc6c463428f28fe252ffeaf65c422ce019c104b31a7"></a>

### 국채 · 합성 장기 KRW 노출

- 대안 ID: government\_bond; 경제적 노출: government\_bond.
- 수익 정의: 합성 장기 국채 만기수익률 관측. 계약 현금흐름·재투자·만기 전 매도가격이 없어 보유기간 총수익과 구분한다..
- 유동성·보유 제약: 합성 시장에서 매도할 수 있는 노출로 가정하지만 현금으로 쓸 때 원하는 가격이 보장되지는 않는다. 실제 거래 유동성은 미확인이다..
- 결론 강도: 지지와 반대 근거가 함께 있어 판단 유보.

**지지 근거**

- 근거 [E\_LONG\_YIELD](#record-2c6c6df3c0efa5bbc2b390e25c538afcf234109a6dbc96358836bdb14224f4ed) / 출처 [S\_DATA\_PROVIDER](#record-1db310d72eadd453df445bdad57c71c88b22ed530e99f1683423070c6029c075) / 정량: 원문·관측 기록: “합성 관측표에 지정한 장기 국채 노출의 만기수익률이 기록되어 있다.”; 관측 수치: 4.5 %; 기간 정의: annual\_rate; 통화: KRW. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.
- 근거 [E\_MARKET\_EXPECTATION](#record-29827c8ee47ede094c9b27b0c8df797f0b20b867a41b668c8fda412c23e8356e) / 출처 [S\_DATA\_PROVIDER](#record-1db310d72eadd453df445bdad57c71c88b22ed530e99f1683423070c6029c075) / 거시환경: 원문·관측 기록: “합성 시장 기대 요약에는 향후 통화정책 완화를 예상하는 가격 해석이 포함되어 있다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.

**반대 근거**

- 근거 [E\_INFLATION](#record-0985fac19dc62891dc6b381df424d0c777857b63c0add26f1b76bc933ef1a0f0) / 출처 [S\_PRIMARY](#record-af72ce688d370947bb342a086cd221a49008bf9c34e70c1a0856419760b91feb) / 거시환경: 원문·관측 기록: “합성 공식 물가 원자료에 후행 연간 소비자물가 상승률이 기록되어 있다.”; 관측 수치: 3.0 %; 기간 정의: annual\_rate; 통화: KRW. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.
- 근거 [E\_BOND\_RISK](#record-9f09c4dbe2b1eb8c64cafd27f753c49cca13059ebaa7fad072342115c6cce057) / 출처 [S\_EXPERT](#record-e28de2e21c1c21c146824c886a13ce8503e9ea4375264972536d7f3369bc506b) / 거시환경: 원문·관측 기록: “합성 전문가의 반대 검토는 물가 압력이 이어지거나 장기금리가 상승하면 만기 전 장기채 가격이 하락할 수 있다고 경고한다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.

**기회비용 · 다른 대안을 선택하지 않을 때 포기할 가능성**

- 비교 대안: 현금성 자산 · 합성 KRW 노출. 검토된 조건부 해석: “합성 장기 국채를 선택하면 현금의 수시 인출 조건을 포기할 수 있고 자금 필요 시 시장가격으로 매도해야 할 수 있다. 출발 수익률은 조사 이유지만 물가·금리 변화가 가격 회수에 영향을 줄 수 있다.” [근거: [E\_CASH\_LIQUIDITY](#record-19fad00c610860d07367140fd0f77d2477e1907255efe14aef9248e1734d8244), [E\_LONG\_YIELD](#record-2c6c6df3c0efa5bbc2b390e25c538afcf234109a6dbc96358836bdb14224f4ed), [E\_INFLATION](#record-0985fac19dc62891dc6b381df424d0c777857b63c0add26f1b76bc933ef1a0f0), [E\_BOND\_RISK](#record-9f09c4dbe2b1eb8c64cafd27f753c49cca13059ebaa7fad072342115c6cce057)]. 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 국채 관측과 현금 인출 조건을 자금수요 관점으로 연결했다. 실제 상품 잠금이나 무위험 회수를 가정하지 않는다.
- 비교 대안: 주식 · 합성 기업군 노출. 검토된 조건부 해석: “합성 국채에 자금을 쓰면 같은 자금으로 주식 이익 성장에 참여할 선택을 포기한다. 그러나 주식 가격 부담과 국채 금리 위험이 각각 있어 두 노출의 미래 우열은 이 입력으로 정할 수 없다.” [근거: [E\_LONG\_YIELD](#record-2c6c6df3c0efa5bbc2b390e25c538afcf234109a6dbc96358836bdb14224f4ed), [E\_BOND\_RISK](#record-9f09c4dbe2b1eb8c64cafd27f753c49cca13059ebaa7fad072342115c6cce057), [E\_EARNINGS](#record-044a29f16d42b7f88daddf9dd3238acfdf6e2aa684435f27d77803b7ec528aa5), [E\_VALUATION](#record-94cd9f091e0cf4fe709bd172692a1f2b61d26f138b0b956554f181aad864d7e1)]. 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 국채 만기수익률과 주식 이익 증가를 같은 미래 수익 숫자로 다루지 않는 합성 조건부 비교다.

**미확인 사항과 채택을 보류한 자료**

- 실제 채권·만기·듀레이션·현금흐름·재투자 조건이 미확인이다.
- 주택 구입 등 자금 필요 시점·손실 감당 능력이 미확인이다.
- 큰 금리 인하의 시점·정도·실현 여부와 비용·세금이 미확인이다.

동일 원출처 중복: [S\_DATA\_PROVIDER](#record-1db310d72eadd453df445bdad57c71c88b22ed530e99f1683423070c6029c075). 해당 재인용·관측은 별도의 독립 근거로 세지 않는다.

<a id="record-30703a5c0fcb28e886e06f6769f4cdf59c4e2e7cbe8d944b8e38ff4d11fb2887"></a>

### 주식 · 합성 기업군 노출

- 대안 ID: equity; 경제적 노출: equity.
- 수익 정의: 합성 이익·유동성·가격 부담·참여 범위의 정성 근거. 가격·배당 총수익과 미래 기대수익률은 제공하지 않는다..
- 유동성·보유 제약: 합성 상장 노출을 가정한다. 매도 가능성과 자금 필요 시 손실 없이 회수할 가능성은 다르며 실제 거래 조건은 미확인이다..
- 결론 강도: 지지와 반대 근거가 함께 있어 판단 유보.

**지지 근거**

- 근거 [E\_EARNINGS](#record-044a29f16d42b7f88daddf9dd3238acfdf6e2aa684435f27d77803b7ec528aa5) / 출처 [S\_COMPANY\_INSTITUTION](#record-a3ad5ff870f66fa7345d2f44b08f856ee3370a0107ddf9b9c43eab60305a47c9) / 사업·기초가치: 원문·관측 기록: “합성 기업군의 확정 실적 자료에는 비교 가능한 이전 보고기간보다 이익이 증가한 것으로 기록되어 있다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.
- 근거 [E\_LIQUIDITY](#record-84da45149546fb5e59c2e7cb8a7d958cc35ed3f1d5fa32d82fd5a12786eed904) / 출처 [S\_RESEARCH](#record-cb4f90a401d7adea71295abb157fc1dcc837114861cd1810a44074067d909831) / 거시환경: 원문·관측 기록: “합성 연구 메모는 지정한 관측 기간의 자금 조달 조건이 이전 비교기간보다 완화된 것으로 요약한다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.

**반대 근거**

- 근거 [E\_VALUATION](#record-94cd9f091e0cf4fe709bd172692a1f2b61d26f138b0b956554f181aad864d7e1) / 출처 [S\_RESEARCH](#record-cb4f90a401d7adea71295abb157fc1dcc837114861cd1810a44074067d909831) / 사업·기초가치: 원문·관측 기록: “합성 연구 메모는 주식 가격이 내부의 명시된 비교틀에서 부담스러운 영역에 있다고 해석한다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.
- 근거 [E\_BREADTH](#record-a700daf2ec08c07d54a71a154fb5522c0c9d7f27a2abd36456c4f9f482c0689b) / 출처 [S\_DATA\_PROVIDER](#record-1db310d72eadd453df445bdad57c71c88b22ed530e99f1683423070c6029c075) / 정량: 원문·관측 기록: “합성 관측표는 상승 참여가 일부 구성에 집중되며 비교기간보다 참여 범위가 약화된 것으로 기록한다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.

**기회비용 · 다른 대안을 선택하지 않을 때 포기할 가능성**

- 비교 대안: 현금성 자산 · 합성 KRW 노출. 검토된 조건부 해석: “합성 주식 노출을 선택하면 현금의 명시된 이자·인출 선택권을 포기한다. 이익 성장의 가능성은 조사할 수 있지만 가격 부담과 참여 범위 약화가 있어 필요 자금을 주식에 둘 적절성은 별도로 확인해야 한다.” [근거: [E\_CASH\_RATE](#record-781048addafe3da8e5fdb6886088902e6f492935b262e90f8dcc012c63c39631), [E\_CASH\_LIQUIDITY](#record-19fad00c610860d07367140fd0f77d2477e1907255efe14aef9248e1734d8244), [E\_EARNINGS](#record-044a29f16d42b7f88daddf9dd3238acfdf6e2aa684435f27d77803b7ec528aa5), [E\_VALUATION](#record-94cd9f091e0cf4fe709bd172692a1f2b61d26f138b0b956554f181aad864d7e1), [E\_BREADTH](#record-a700daf2ec08c07d54a71a154fb5522c0c9d7f27a2abd36456c4f9f482c0689b)]. 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 성장 근거와 가격·참여 위험, 현금 조건을 함께 검토했다. 미확인 개인 자금수요를 채우거나 배분 비중을 제시하지 않는다.
- 비교 대안: 국채 · 합성 장기 KRW 노출. 검토된 조건부 해석: “합성 주식 노출을 선택하면 국채의 관측된 출발 수익률과 현금흐름 조건을 더 검토할 선택을 포기한다. 주식에는 성장과 가격 부담이, 국채에는 금리 손실 경로가 있어 동일기간 대안 성과는 아직 비교할 수 없다.” [근거: [E\_EARNINGS](#record-044a29f16d42b7f88daddf9dd3238acfdf6e2aa684435f27d77803b7ec528aa5), [E\_VALUATION](#record-94cd9f091e0cf4fe709bd172692a1f2b61d26f138b0b956554f181aad864d7e1), [E\_LONG\_YIELD](#record-2c6c6df3c0efa5bbc2b390e25c538afcf234109a6dbc96358836bdb14224f4ed), [E\_BOND\_RISK](#record-9f09c4dbe2b1eb8c64cafd27f753c49cca13059ebaa7fad072342115c6cce057)]. 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 주식과 국채의 다른 수익 원천·손실 경로를 연결한 합성 비교이며 실제 채권 계약 현금흐름은 미확인임을 유지한다.

**미확인 사항과 채택을 보류한 자료**

- 실제 기업·국가·산업·통화·상품 범위가 미확인이다.
- 현재 보유 노출·집중위험·부채·손실 감당 능력이 미확인이다.
- 미래 이익·가격 반영 기대·비용·세금·실제 환노출은 미확인이다.

동일 원출처 중복: [S\_RESEARCH](#record-cb4f90a401d7adea71295abb157fc1dcc837114861cd1810a44074067d909831). 해당 재인용·관측은 별도의 독립 근거로 세지 않는다.

## 커뮤니티에서는 무엇을 말하고 있는가

### 관측한 발언 · E\_COMMUNITY\_BOND

발언 자료 원문: “합성 공개 토론 구절에는 “금리가 곧 크게 떨어질 것이므로 장기채는 지금 거의 확실한 기회다”라는 발언이 있다.” [출처: S\_COMMUNITY; 위치: 합성 문서 v1의 E\_COMMUNITY\_BOND 구절; 관측일: 2025-01-24].

발언 기록의 확인 상태: 한정된 범위에서 확인; 해석 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 원문 구절과 fixture의 대상·시점을 대조한 검토 기록이다. 이 기록은 실제 시장 확인이나 미래 결과의 검증이 아니다..

발언의 존재와 발언 내용의 진실성은 다르다. 이 자료는 투자 사실 근거로 채택하지 않으며, 반복·인기도는 독립 확인이나 미래 수익 확률이 아니다.

**내용 검증 대상 · 주장 C\_BOND\_NARRATIVE**

입력된 주장 원문: “금리가 곧 크게 떨어질 것이므로 장기채는 지금 거의 확실한 기회다.”.

내용의 검증 상태: 현재 자료로 확인할 수 없음 (not\_verifiable); 해석: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: E\_COMMUNITY\_BOND에서 발언의 존재는 확인했다. E\_POLICY\_RATE·E\_LONG\_YIELD·E\_INFLATION·E\_MARKET\_EXPECTATION·E\_BOND\_RISK와 비교했지만 미래 큰 인하와 거의 확실한 투자성과를 기준 시점에서 확인할 수 없다. 미확인 상태를 검토한 기록이며 투자 주장 채택이 아니다..

지지 자료와 각 자료의 채택 상태:

- 근거 [E\_POLICY\_RATE](#record-2d5ce882fe0a5ce455a06483e6f4f0b940ddd3743f2d3bef9e2ecb871f7ae186) / 출처 [S\_PRIMARY](#record-af72ce688d370947bb342a086cd221a49008bf9c34e70c1a0856419760b91feb) / 거시환경: 원문·관측 기록: “합성 공식 금리 원자료에 기준 시점의 정책금리가 기록되어 있다.”; 관측 수치: 3.5 %; 기간 정의: annual\_rate; 통화: KRW. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.
- 근거 [E\_LONG\_YIELD](#record-2c6c6df3c0efa5bbc2b390e25c538afcf234109a6dbc96358836bdb14224f4ed) / 출처 [S\_DATA\_PROVIDER](#record-1db310d72eadd453df445bdad57c71c88b22ed530e99f1683423070c6029c075) / 정량: 원문·관측 기록: “합성 관측표에 지정한 장기 국채 노출의 만기수익률이 기록되어 있다.”; 관측 수치: 4.5 %; 기간 정의: annual\_rate; 통화: KRW. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.
- 근거 [E\_MARKET\_EXPECTATION](#record-29827c8ee47ede094c9b27b0c8df797f0b20b867a41b668c8fda412c23e8356e) / 출처 [S\_DATA\_PROVIDER](#record-1db310d72eadd453df445bdad57c71c88b22ed530e99f1683423070c6029c075) / 거시환경: 원문·관측 기록: “합성 시장 기대 요약에는 향후 통화정책 완화를 예상하는 가격 해석이 포함되어 있다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.

반대 자료와 각 자료의 채택 상태:

- 근거 [E\_INFLATION](#record-0985fac19dc62891dc6b381df424d0c777857b63c0add26f1b76bc933ef1a0f0) / 출처 [S\_PRIMARY](#record-af72ce688d370947bb342a086cd221a49008bf9c34e70c1a0856419760b91feb) / 거시환경: 원문·관측 기록: “합성 공식 물가 원자료에 후행 연간 소비자물가 상승률이 기록되어 있다.”; 관측 수치: 3.0 %; 기간 정의: annual\_rate; 통화: KRW. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.
- 근거 [E\_BOND\_RISK](#record-9f09c4dbe2b1eb8c64cafd27f753c49cca13059ebaa7fad072342115c6cce057) / 출처 [S\_EXPERT](#record-e28de2e21c1c21c146824c886a13ce8503e9ea4375264972536d7f3369bc506b) / 거시환경: 원문·관측 기록: “합성 전문가의 반대 검토는 물가 압력이 이어지거나 장기금리가 상승하면 만기 전 장기채 가격이 하락할 수 있다고 경고한다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거.

확인하지 못한 범위·한계: 합성 발언의 존재와 내용의 진실성은 별개다. / 현재 금리와 기대는 향후 인하·가격 상승·기회 확실성을 증명하지 않는다. / 확인 불가를 반증이나 현금 우위로 바꾸지 않는다..

재검토 질문(주장 검토 기록): 새 공식 정책·물가 자료와 장기금리 변화, 실제 상품의 만기·현금흐름·가격 민감도를 확인한 뒤 조건부 논리를 다시 조사한다..

## 서로 충돌하는 근거

투자 논리의 긴장은 긍정·부정 요인이 공존한다는 뜻이다. 동일한 사실의 모순을 자동 판정한 것이 아니며, 내용 검증 기록의 반박·상충 상태와 구분한다.

- 투자 논리의 긴장: 현금성 자산 · 합성 KRW 노출의 지지 [[E\_CASH\_RATE](#record-781048addafe3da8e5fdb6886088902e6f492935b262e90f8dcc012c63c39631), [E\_CASH\_LIQUIDITY](#record-19fad00c610860d07367140fd0f77d2477e1907255efe14aef9248e1734d8244)]와 반대 [[E\_INFLATION](#record-0985fac19dc62891dc6b381df424d0c777857b63c0add26f1b76bc933ef1a0f0), [E\_NEWS\_INFLATION](#record-8cfe5eafe56cb2f3f54c08372a8e45691f6127171694038f6986d64665abd301)]가 함께 남는다.
- 투자 논리의 긴장: 국채 · 합성 장기 KRW 노출의 지지 [[E\_LONG\_YIELD](#record-2c6c6df3c0efa5bbc2b390e25c538afcf234109a6dbc96358836bdb14224f4ed), [E\_MARKET\_EXPECTATION](#record-29827c8ee47ede094c9b27b0c8df797f0b20b867a41b668c8fda412c23e8356e)]와 반대 [[E\_INFLATION](#record-0985fac19dc62891dc6b381df424d0c777857b63c0add26f1b76bc933ef1a0f0), [E\_BOND\_RISK](#record-9f09c4dbe2b1eb8c64cafd27f753c49cca13059ebaa7fad072342115c6cce057)]가 함께 남는다.
- 투자 논리의 긴장: 주식 · 합성 기업군 노출의 지지 [[E\_EARNINGS](#record-044a29f16d42b7f88daddf9dd3238acfdf6e2aa684435f27d77803b7ec528aa5), [E\_LIQUIDITY](#record-84da45149546fb5e59c2e7cb8a7d958cc35ed3f1d5fa32d82fd5a12786eed904)]와 반대 [[E\_VALUATION](#record-94cd9f091e0cf4fe709bd172692a1f2b61d26f138b0b956554f181aad864d7e1), [E\_BREADTH](#record-a700daf2ec08c07d54a71a154fb5522c0c9d7f27a2abd36456c4f9f482c0689b)]가 함께 남는다.
- 내용 검증 기록의 충돌: 주장 C\_YIELD\_ORDER는 동일한 범위에서 반박됨 (contradicted\_within\_scope). 입력 원문: “합성 기준 시점의 장기 국채 만기수익률은 합성 정책금리보다 낮다.”; 지지 [없음]; 반대 [[E\_LONG\_YIELD](#record-2c6c6df3c0efa5bbc2b390e25c538afcf234109a6dbc96358836bdb14224f4ed), [E\_POLICY\_RATE](#record-2d5ce882fe0a5ce455a06483e6f4f0b940ddd3743f2d3bef9e2ecb871f7ae186)]; 검토 이유: 같은 합성 기준 시점의 E\_LONG\_YIELD와 E\_POLICY\_RATE 값이 이 부등관계와 모순된다. 잘못된 비교를 반박된 주장으로 보존하는 검증 사례다.. 동일 범위의 사실 반박 상태와 투자 전망의 불확실성을 구분해서 읽어야 한다.
- 내용 검증 기록의 충돌: 주장 C\_EQUITY\_BALANCE는 자료가 상충함 (disputed). 입력 원문: “합성 주식 자료의 이익·유동성 개선은 추가 조사 이유를 주지만 가격 부담·참여 범위 약화와 충돌해 상대 우위를 확정하기 어렵다.”; 지지 [[E\_EARNINGS](#record-044a29f16d42b7f88daddf9dd3238acfdf6e2aa684435f27d77803b7ec528aa5), [E\_LIQUIDITY](#record-84da45149546fb5e59c2e7cb8a7d958cc35ed3f1d5fa32d82fd5a12786eed904)]; 반대 [[E\_VALUATION](#record-94cd9f091e0cf4fe709bd172692a1f2b61d26f138b0b956554f181aad864d7e1), [E\_BREADTH](#record-a700daf2ec08c07d54a71a154fb5522c0c9d7f27a2abd36456c4f9f482c0689b)]; 검토 이유: E\_EARNINGS·E\_LIQUIDITY의 지지 논리와 E\_VALUATION·E\_BREADTH의 반대 논리를 함께 검토했다. 이 입력은 주식의 확정 매력·순위·투자비중을 제공하지 않는다.. 동일 범위의 사실 반박 상태와 투자 전망의 불확실성을 구분해서 읽어야 한다.

## 내 상황에서는 무엇이 아직 필요한가

- 기준 통화: KRW; 정보 상태: known.
- 출생연도: 1998; 정보 상태: known.
- 부채: UNKNOWN · 미확인; 정보 상태: unknown.
- 비상자금: UNKNOWN · 미확인; 정보 상태: unknown.
- 근로소득: 안정적인 근로소득이라는 가상 자기보고; 정보 상태: known.
- 투자 기간: 장기 투자 가능이라는 가상 자기보고; 정보 상태: known.
- 주택 구입 필요자금·시점: UNKNOWN · 미확인; 정보 상태: unknown.
- 월 추가 투자 가능액: UNKNOWN · 미확인; 정보 상태: unknown.
- 현재 포트폴리오 배분·보유범위: UNKNOWN · 미확인; 정보 상태: unknown.
- 위험 감당 능력: UNKNOWN · 미확인; 정보 상태: unknown.
- 자산 축적 단계: 자산 축적기; 정보 상태: known.
- 세법상 거주자 상태: 대한민국 세법상 거주자라는 가상 자기보고; 정보 상태: known.
- 현재 총자산: UNKNOWN · 미확인; 정보 상태: unknown.

미확인 정보가 제한하는 판단:

- 총자산이 미확인이라 실제 손실 감당 규모와 전체 자산 대비 투자금의 크기를 판단할 수 없다.
- 비상자금이 미확인이라 현금 비중이 과도하거나 추가 투자에 충분하다고 판단할 수 없다.
- 부채가 미확인이라 무부채로 가정하거나 부채 상환과 투자 사이의 개인 기회비용을 판단할 수 없다.
- 주택 구입 필요자금과 시점이 미확인이라 장기간 자금이 묶이는 선택의 적절성을 판단할 수 없다.
- 현재 포트폴리오 배분과 보유범위가 미확인이라 전체 집중위험이나 분산·안전성을 판단할 수 없다.
- 월 추가 투자 가능액이 미확인이라 안정적인 근로소득에서 투자 가능 금액을 추정할 수 없다.
- 위험 감당 능력이 미확인이라 나이·소득·위험 감수 의향에서 손실 한도·투자 비중·레버리지 허용을 도출할 수 없다.

위험 감수 의향은 심리적 의향이고 위험 감당 능력은 생활과 의무지출을 유지할 재무 능력이다. 나이·안정적 소득·장기 투자 가능성은 자산의 미래 기대수익을 증명하지 않는다.

## 현재 얻을 수 있는 Insight

- 현금성 자산 · 합성 KRW 노출: 지지와 반대의 전달 경로를 함께 재검토할 이유가 있으며, 현재 근거로 다른 대안보다 우월하다고 확정할 수 없다. 지지 [[E\_CASH\_RATE](#record-781048addafe3da8e5fdb6886088902e6f492935b262e90f8dcc012c63c39631), [E\_CASH\_LIQUIDITY](#record-19fad00c610860d07367140fd0f77d2477e1907255efe14aef9248e1734d8244)]; 반대 [[E\_INFLATION](#record-0985fac19dc62891dc6b381df424d0c777857b63c0add26f1b76bc933ef1a0f0), [E\_NEWS\_INFLATION](#record-8cfe5eafe56cb2f3f54c08372a8e45691f6127171694038f6986d64665abd301)]; 보류 [없음].
- 국채 · 합성 장기 KRW 노출: 지지와 반대의 전달 경로를 함께 재검토할 이유가 있으며, 현재 근거로 다른 대안보다 우월하다고 확정할 수 없다. 지지 [[E\_LONG\_YIELD](#record-2c6c6df3c0efa5bbc2b390e25c538afcf234109a6dbc96358836bdb14224f4ed), [E\_MARKET\_EXPECTATION](#record-29827c8ee47ede094c9b27b0c8df797f0b20b867a41b668c8fda412c23e8356e)]; 반대 [[E\_INFLATION](#record-0985fac19dc62891dc6b381df424d0c777857b63c0add26f1b76bc933ef1a0f0), [E\_BOND\_RISK](#record-9f09c4dbe2b1eb8c64cafd27f753c49cca13059ebaa7fad072342115c6cce057)]; 보류 [없음].
- 주식 · 합성 기업군 노출: 지지와 반대의 전달 경로를 함께 재검토할 이유가 있으며, 현재 근거로 다른 대안보다 우월하다고 확정할 수 없다. 지지 [[E\_EARNINGS](#record-044a29f16d42b7f88daddf9dd3238acfdf6e2aa684435f27d77803b7ec528aa5), [E\_LIQUIDITY](#record-84da45149546fb5e59c2e7cb8a7d958cc35ed3f1d5fa32d82fd5a12786eed904)]; 반대 [[E\_VALUATION](#record-94cd9f091e0cf4fe709bd172692a1f2b61d26f138b0b956554f181aad864d7e1), [E\_BREADTH](#record-a700daf2ec08c07d54a71a154fb5522c0c9d7f27a2abd36456c4f9f482c0689b)]; 보류 [없음].
- 이 결론 강도는 채택 가능한 지지·반대 근거의 존재에 따른 정성 상태다. 근거 개수·출처 등급으로 신뢰도 점수나 자산 순위를 만들지 않는다.
- 개인 적용: 미확인 정보 또는 지지 근거 부족으로 개인 자산배분의 적절성은 판단 유보한다.
- 결론 유보는 현금의 우위를 뜻하지 않는다. 자료가 다른 대안의 수익·위험·유동성 차이를 충분히 설명하는지 확인해야 한다.

## 무엇이 바뀌면 다시 봐야 하는가

- 현금성 자산 · 합성 KRW 노출: 검토된 조건부 해석: “현금 이자 조건이나 새 물가 관측이 바뀌면 단순 금리 차이와 인출 조건을 다시 확인한다.” [근거: [E\_CASH\_RATE](#record-781048addafe3da8e5fdb6886088902e6f492935b262e90f8dcc012c63c39631), [E\_INFLATION](#record-0985fac19dc62891dc6b381df424d0c777857b63c0add26f1b76bc933ef1a0f0), [E\_CASH\_LIQUIDITY](#record-19fad00c610860d07367140fd0f77d2477e1907255efe14aef9248e1734d8244)]. 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 현금 조건·후행 물가·유동성 구절의 적용 범위에서만 재조사 항목을 도출했다.
- 국채 · 합성 장기 KRW 노출: 검토된 조건부 해석: “물가·정책 경로·장기금리·시장 기대가 바뀌거나 실제 채권 현금흐름과 가격 민감도를 확보하면 양쪽 논리를 다시 조사한다.” [근거: [E\_INFLATION](#record-0985fac19dc62891dc6b381df424d0c777857b63c0add26f1b76bc933ef1a0f0), [E\_POLICY\_RATE](#record-2d5ce882fe0a5ce455a06483e6f4f0b940ddd3743f2d3bef9e2ecb871f7ae186), [E\_LONG\_YIELD](#record-2c6c6df3c0efa5bbc2b390e25c538afcf234109a6dbc96358836bdb14224f4ed), [E\_MARKET\_EXPECTATION](#record-29827c8ee47ede094c9b27b0c8df797f0b20b867a41b668c8fda412c23e8356e), [E\_BOND\_RISK](#record-9f09c4dbe2b1eb8c64cafd27f753c49cca13059ebaa7fad072342115c6cce057)]. 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 금리 관측과 기대·위험 구절을 조건부 재검토 항목으로 연결했으며 금리 방향을 예측하지 않는다.
- 주식 · 합성 기업군 노출: 검토된 조건부 해석: “새 실적과 가격 부담·자금 조달 조건·시장 참여 범위가 바뀌면 성장 지지와 반대 논리를 함께 다시 검토한다.” [근거: [E\_EARNINGS](#record-044a29f16d42b7f88daddf9dd3238acfdf6e2aa684435f27d77803b7ec528aa5), [E\_LIQUIDITY](#record-84da45149546fb5e59c2e7cb8a7d958cc35ed3f1d5fa32d82fd5a12786eed904), [E\_VALUATION](#record-94cd9f091e0cf4fe709bd172692a1f2b61d26f138b0b956554f181aad864d7e1), [E\_BREADTH](#record-a700daf2ec08c07d54a71a154fb5522c0c9d7f27a2abd36456c4f9f482c0689b)]. 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 주식의 지지·반대 범위에 필요한 관찰 항목을 연결했으며 매매 조건·미래 수익으로 확정하지 않는다.
- 주장 C\_EARNINGS / 검토 기록의 재검토 조건: 같은 기업군·회계 정의의 새 실적이나 정정이 있으면 이익 증가 구절을 다시 대조한다.. 검토: 검토됨.
- 주장 C\_YIELD\_ORDER / 검토 기록의 재검토 조건: 두 관측의 날짜·금리 정의·단위가 바뀌면 같은 범위의 부등관계를 다시 확인한다.. 검토: 검토됨.
- 주장 C\_MARKET\_EASING / 검토 기록의 재검토 조건: 새 물가 관측·정책 발표·시장 기대 변화가 생기면 기대와 실제 결정의 차이를 다시 조사한다.. 검토: 검토됨.
- 주장 C\_EQUITY\_BALANCE / 검토 기록의 재검토 조건: 이익 정정·가격 부담 변화·유동성 역전·참여 범위 회복 또는 추가 약화가 나타나면 양쪽 논리를 다시 비교한다.. 검토: 검토됨.
- 주장 C\_BOND\_NARRATIVE / 검토 기록의 재검토 조건: 새 공식 정책·물가 자료와 장기금리 변화, 실제 상품의 만기·현금흐름·가격 민감도를 확인한 뒤 조건부 논리를 다시 조사한다.. 검토: 검토됨.
- 주장 C\_LIQUIDITY\_CAUSALITY / 채택 보류한 주장 초안의 재검토 질문: 필요한 가격·사업·금리·기대 자료와 경쟁하는 설명을 확보하고 별도 의미 검토를 완료해야 한다.. 검토: 검토 대기.
- 사용자 미확인 정보가 확인되거나 자료·검증 상태가 달라지면 새 입력 버전으로 연구를 다시 실행한다.

## 초간단 설명

이 보고서는 합성 자료로 현금성 자산·국채·주식을 비교하는 연구 과정을 시험한 결과다.
좋은 점과 나쁜 점을 함께 보고, 정보가 부족하면 결론을 기다린다.
인터넷에서 누가 한 말과 그 말이 사실이라는 것은 다르다.
내가 가진 돈·부채·앞으로 쓸 돈을 모르면 나에게 맞는 비중을 정할 수 없다.
지금 결론을 기다려도 현금의 우위가 증명된 것은 아니다.

## 부록 · 근거와 재현 기록

- 실행 ID: 076004880871c82c5299d1a4a2ee1f566645e59249f2592d02c66aba82380b31; 입력 SHA-256: ec2b7687943ef2e96be97b10d1de8cdc8e0b6dce43da675efc7991e02e2ace6a.
- 스키마: 1; 코드 버전: 0.1.0; 근거 규칙: evidence_rules_v1; 보고서: korean_brief_v1.
- 구조·참조·시점 검증과 결정적 계산은 내용·해석의 의미, 미래 성과 또는 사용자 적합성을 자동 보증하지 않는다.
- 숫자는 등록된 관측 또는 계산에서 삽입했다. 인용문·조건부 해석은 입력된 검토 기록의 범위에서 표시했다.

### 출처 목록

<a id="record-af72ce688d370947bb342a086cd221a49008bf9c34e70c1a0856419760b91feb"></a>

- 출처 S\_PRIMARY: 합성 공식 금리·물가 원자료 묶음; 유형: primary; 확인 우선순위: 1 (신뢰도 점수가 아님).
  위치: synthetic://cross-asset-case/s\_primary/v1; 공개일: 2025-01-27; 이용 가능일: 2025-01-28; 획득일: 2025-01-30.
  직접 원출처: 재인용 관계 없음; 추적한 원출처 ID: S\_PRIMARY; 한계: 개발 검증용 합성 출처이며 실제 기관·문서·시장 자료가 아니다. / 정책금리와 후행 물가 관측만 담으며 미래 정책 경로나 물가를 전망하지 않는다..
<a id="record-78f486e914cbeff24f201dfa85e54dcb4081aebffbd2dee1e7ee2d51cd1c5a84"></a>

- 출처 S\_CASH\_INSTITUTION: 합성 기관의 현금성 노출 조건표; 유형: institution; 확인 우선순위: 2 (신뢰도 점수가 아님).
  위치: synthetic://cross-asset-case/s\_cash\_institution/v1; 공개일: 2025-01-27; 이용 가능일: 2025-01-28; 획득일: 2025-01-30.
  직접 원출처: 재인용 관계 없음; 추적한 원출처 ID: S\_CASH\_INSTITUTION; 한계: 개발 검증용 합성 출처이며 실제 기관·문서·시장 자료가 아니다. / 가상 이자·인출 조건이며 모든 실제 현금 상품의 안전성이나 조건을 대표하지 않는다..
<a id="record-a3ad5ff870f66fa7345d2f44b08f856ee3370a0107ddf9b9c43eab60305a47c9"></a>

- 출처 S\_COMPANY\_INSTITUTION: 합성 기업군의 사업 실적 자료; 유형: institution; 확인 우선순위: 2 (신뢰도 점수가 아님).
  위치: synthetic://cross-asset-case/s\_company\_institution/v1; 공개일: 2025-01-27; 이용 가능일: 2025-01-28; 획득일: 2025-01-30.
  직접 원출처: 재인용 관계 없음; 추적한 원출처 ID: S\_COMPANY\_INSTITUTION; 한계: 개발 검증용 합성 출처이며 실제 기관·문서·시장 자료가 아니다. / 정해진 가상 기업군의 보고기간 실적이며 전체 시장이나 미래 이익을 대표하지 않는다..
<a id="record-1db310d72eadd453df445bdad57c71c88b22ed530e99f1683423070c6029c075"></a>

- 출처 S\_DATA\_PROVIDER: 합성 금융 관측표 제공자; 유형: data\_provider; 확인 우선순위: 3 (신뢰도 점수가 아님).
  위치: synthetic://cross-asset-case/s\_data\_provider/v1; 공개일: 2025-01-27; 이용 가능일: 2025-01-28; 획득일: 2025-01-30.
  직접 원출처: 재인용 관계 없음; 추적한 원출처 ID: S\_DATA\_PROVIDER; 한계: 개발 검증용 합성 출처이며 실제 기관·문서·시장 자료가 아니다. / 만기수익률·시장 기대 요약·참여 범위의 가상 관측이다. 완전한 가격 경로나 실제 투자성과는 없다..
<a id="record-cb4f90a401d7adea71295abb157fc1dcc837114861cd1810a44074067d909831"></a>

- 출처 S\_RESEARCH: 합성 전문 연구 메모; 유형: research; 확인 우선순위: 4 (신뢰도 점수가 아님).
  위치: synthetic://cross-asset-case/s\_research/v1; 공개일: 2025-01-27; 이용 가능일: 2025-01-28; 획득일: 2025-01-30.
  직접 원출처: 재인용 관계 없음; 추적한 원출처 ID: S\_RESEARCH; 한계: 개발 검증용 합성 출처이며 실제 기관·문서·시장 자료가 아니다. / 명시한 가상 비교틀의 유동성·가격 부담 해석이며 추정이나 논리의 타당성을 자동 보증하지 않는다..
<a id="record-24d3c9a8e7c3bf789ad24de06ac9c6915e3eec4bafbf9524f2567f870167fd4b"></a>

- 출처 S\_NEWS: 합성 경제 기사; 유형: news; 확인 우선순위: 4 (신뢰도 점수가 아님).
  위치: synthetic://cross-asset-case/s\_news/v1; 공개일: 2025-01-27; 이용 가능일: 2025-01-28; 획득일: 2025-01-30.
  직접 원출처: S\_PRIMARY; 추적한 원출처 ID: S\_PRIMARY; 한계: 개발 검증용 합성 출처이며 실제 기관·문서·시장 자료가 아니다. / 합성 공식 원자료의 물가 구절을 재인용한다. 독립적인 물가 확인으로 세지 않는다..
<a id="record-e28de2e21c1c21c146824c886a13ce8503e9ea4375264972536d7f3369bc506b"></a>

- 출처 S\_EXPERT: 합성 채권 전문가의 반대 검토 메모; 유형: expert; 확인 우선순위: 5 (신뢰도 점수가 아님).
  위치: synthetic://cross-asset-case/s\_expert/v1; 공개일: 2025-01-27; 이용 가능일: 2025-01-28; 획득일: 2025-01-30.
  직접 원출처: 재인용 관계 없음; 추적한 원출처 ID: S\_EXPERT; 한계: 개발 검증용 합성 출처이며 실제 기관·문서·시장 자료가 아니다. / 가상 전문가의 금리 위험 설명이며 실제 전망이나 결과 확인이 아니다. 이해관계는 실제로 조사하지 않았다..
<a id="record-52dfadc283137bc0ae2df13aeccaa38439d5c5c48d3af6384a60084715d2f8fe"></a>

- 출처 S\_COMMUNITY: 합성 공개 토론 표본; 유형: community; 확인 우선순위: 6 (신뢰도 점수가 아님).
  위치: synthetic://cross-asset-case/s\_community/v1; 공개일: 2025-01-27; 이용 가능일: 2025-01-28; 획득일: 2025-01-30.
  직접 원출처: 재인용 관계 없음; 추적한 원출처 ID: S\_COMMUNITY; 한계: 개발 검증용 합성 출처이며 실제 기관·문서·시장 자료가 아니다. / 가상의 공개 토론 구절만 보존한다. 실제 이용자·플랫폼·개인 식별자는 없다. / 선택한 구절은 전체 투자자를 대표하지 않는다. 반복·좋아요·조회수로 신뢰도나 확률을 만들지 않는다..

### 근거 목록

<a id="record-781048addafe3da8e5fdb6886088902e6f492935b262e90f8dcc012c63c39631"></a>

- 근거 [E\_CASH\_RATE](#record-781048addafe3da8e5fdb6886088902e6f492935b262e90f8dcc012c63c39631) / 출처 [S\_CASH\_INSTITUTION](#record-78f486e914cbeff24f201dfa85e54dcb4081aebffbd2dee1e7ee2d51cd1c5a84) / 정량: 원문·관측 기록: “합성 현금성 노출 조건표에 명목 연 이자율이 기록되어 있다.”; 관측 수치: 2.5 %; 기간 정의: annual\_rate; 통화: KRW. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거. 한계: 개발 검증용 합성 근거이며 실제 현재 시장에 적용할 수 없다. / 가상 계약의 세전·비용전 명목 이자율이다. 실제 수령액·미래 갱신금리·실질수익률이 아니다.
  유형: external\_fact; 위치: 합성 문서 v1의 E\_CASH\_RATE 구절; 관측일: 2025-01-24; 분석일: 2025-01-31; 자산 범위: [cash](#record-ab0fcec08e18a7bccda1e81df4974e3434fcd36000518f7e776fb85495b5a494).
  해석 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 원문 구절과 fixture의 대상·시점을 대조한 검토 기록이다. 이 기록은 실제 시장 확인이나 미래 결과의 검증이 아니다..
<a id="record-19fad00c610860d07367140fd0f77d2477e1907255efe14aef9248e1734d8244"></a>

- 근거 [E\_CASH\_LIQUIDITY](#record-19fad00c610860d07367140fd0f77d2477e1907255efe14aef9248e1734d8244) / 출처 [S\_CASH\_INSTITUTION](#record-78f486e914cbeff24f201dfa85e54dcb4081aebffbd2dee1e7ee2d51cd1c5a84) / 사업·기초가치: 원문·관측 기록: “합성 현금성 노출 조건표는 원화 수시 인출이 가능한 조건을 명시한다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거. 한계: 개발 검증용 합성 근거이며 실제 현재 시장에 적용할 수 없다. / 해당 가상 조건에 한정하며 모든 현금성 자산의 원금 보장·무위험을 주장하지 않는다.
  유형: external\_fact; 위치: 합성 문서 v1의 E\_CASH\_LIQUIDITY 구절; 관측일: 2025-01-24; 분석일: 2025-01-31; 자산 범위: [cash](#record-ab0fcec08e18a7bccda1e81df4974e3434fcd36000518f7e776fb85495b5a494).
  해석 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 원문 구절과 fixture의 대상·시점을 대조한 검토 기록이다. 이 기록은 실제 시장 확인이나 미래 결과의 검증이 아니다..
<a id="record-0985fac19dc62891dc6b381df424d0c777857b63c0add26f1b76bc933ef1a0f0"></a>

- 근거 [E\_INFLATION](#record-0985fac19dc62891dc6b381df424d0c777857b63c0add26f1b76bc933ef1a0f0) / 출처 [S\_PRIMARY](#record-af72ce688d370947bb342a086cd221a49008bf9c34e70c1a0856419760b91feb) / 거시환경: 원문·관측 기록: “합성 공식 물가 원자료에 후행 연간 소비자물가 상승률이 기록되어 있다.”; 관측 수치: 3.0 %; 기간 정의: annual\_rate; 통화: KRW. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거. 한계: 개발 검증용 합성 근거이며 실제 현재 시장에 적용할 수 없다. / 원화 생활비 맥락의 후행 물가 관측이다. 미래 물가율이나 사용자별 생활비 상승률이 아니다.
  유형: observed\_fact; 위치: 합성 문서 v1의 E\_INFLATION 구절; 관측일: 2025-01-24; 분석일: 2025-01-31; 자산 범위: [cash](#record-ab0fcec08e18a7bccda1e81df4974e3434fcd36000518f7e776fb85495b5a494), [government\_bond](#record-e9c778e2cbb7e6f9dbdbebc6c463428f28fe252ffeaf65c422ce019c104b31a7), [equity](#record-30703a5c0fcb28e886e06f6769f4cdf59c4e2e7cbe8d944b8e38ff4d11fb2887).
  해석 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 원문 구절과 fixture의 대상·시점을 대조한 검토 기록이다. 이 기록은 실제 시장 확인이나 미래 결과의 검증이 아니다..
<a id="record-2d5ce882fe0a5ce455a06483e6f4f0b940ddd3743f2d3bef9e2ecb871f7ae186"></a>

- 근거 [E\_POLICY\_RATE](#record-2d5ce882fe0a5ce455a06483e6f4f0b940ddd3743f2d3bef9e2ecb871f7ae186) / 출처 [S\_PRIMARY](#record-af72ce688d370947bb342a086cd221a49008bf9c34e70c1a0856419760b91feb) / 거시환경: 원문·관측 기록: “합성 공식 금리 원자료에 기준 시점의 정책금리가 기록되어 있다.”; 관측 수치: 3.5 %; 기간 정의: annual\_rate; 통화: KRW. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거. 한계: 개발 검증용 합성 근거이며 실제 현재 시장에 적용할 수 없다. / 정책금리는 현금 상품 금리·주식 수익률과 같지 않다. 향후 인하 시점은 이 관측으로 확인할 수 없다.
  유형: observed\_fact; 위치: 합성 문서 v1의 E\_POLICY\_RATE 구절; 관측일: 2025-01-24; 분석일: 2025-01-31; 자산 범위: [cash](#record-ab0fcec08e18a7bccda1e81df4974e3434fcd36000518f7e776fb85495b5a494), [government\_bond](#record-e9c778e2cbb7e6f9dbdbebc6c463428f28fe252ffeaf65c422ce019c104b31a7), [equity](#record-30703a5c0fcb28e886e06f6769f4cdf59c4e2e7cbe8d944b8e38ff4d11fb2887).
  해석 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 원문 구절과 fixture의 대상·시점을 대조한 검토 기록이다. 이 기록은 실제 시장 확인이나 미래 결과의 검증이 아니다..
<a id="record-2c6c6df3c0efa5bbc2b390e25c538afcf234109a6dbc96358836bdb14224f4ed"></a>

- 근거 [E\_LONG\_YIELD](#record-2c6c6df3c0efa5bbc2b390e25c538afcf234109a6dbc96358836bdb14224f4ed) / 출처 [S\_DATA\_PROVIDER](#record-1db310d72eadd453df445bdad57c71c88b22ed530e99f1683423070c6029c075) / 정량: 원문·관측 기록: “합성 관측표에 지정한 장기 국채 노출의 만기수익률이 기록되어 있다.”; 관측 수치: 4.5 %; 기간 정의: annual\_rate; 통화: KRW. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거. 한계: 개발 검증용 합성 근거이며 실제 현재 시장에 적용할 수 없다. / 가상 만기수익률은 보유기간의 확정 총수익이 아니다. 듀레이션·현금흐름·재투자·매도가격 자료가 없다.
  유형: observed\_fact; 위치: 합성 문서 v1의 E\_LONG\_YIELD 구절; 관측일: 2025-01-24; 분석일: 2025-01-31; 자산 범위: [government\_bond](#record-e9c778e2cbb7e6f9dbdbebc6c463428f28fe252ffeaf65c422ce019c104b31a7).
  해석 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 원문 구절과 fixture의 대상·시점을 대조한 검토 기록이다. 이 기록은 실제 시장 확인이나 미래 결과의 검증이 아니다..
<a id="record-29827c8ee47ede094c9b27b0c8df797f0b20b867a41b668c8fda412c23e8356e"></a>

- 근거 [E\_MARKET\_EXPECTATION](#record-29827c8ee47ede094c9b27b0c8df797f0b20b867a41b668c8fda412c23e8356e) / 출처 [S\_DATA\_PROVIDER](#record-1db310d72eadd453df445bdad57c71c88b22ed530e99f1683423070c6029c075) / 거시환경: 원문·관측 기록: “합성 시장 기대 요약에는 향후 통화정책 완화를 예상하는 가격 해석이 포함되어 있다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거. 한계: 개발 검증용 합성 근거이며 실제 현재 시장에 적용할 수 없다. / 가격에서 읽은 기대의 합성 요약이다. 실제 정책 경로·큰 인하·채권의 확정 수익을 관측한 것이 아니다.
  유형: external\_fact; 위치: 합성 문서 v1의 E\_MARKET\_EXPECTATION 구절; 관측일: 2025-01-24; 분석일: 2025-01-31; 자산 범위: [government\_bond](#record-e9c778e2cbb7e6f9dbdbebc6c463428f28fe252ffeaf65c422ce019c104b31a7), [equity](#record-30703a5c0fcb28e886e06f6769f4cdf59c4e2e7cbe8d944b8e38ff4d11fb2887).
  해석 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 원문 구절과 fixture의 대상·시점을 대조한 검토 기록이다. 이 기록은 실제 시장 확인이나 미래 결과의 검증이 아니다..
<a id="record-9f09c4dbe2b1eb8c64cafd27f753c49cca13059ebaa7fad072342115c6cce057"></a>

- 근거 [E\_BOND\_RISK](#record-9f09c4dbe2b1eb8c64cafd27f753c49cca13059ebaa7fad072342115c6cce057) / 출처 [S\_EXPERT](#record-e28de2e21c1c21c146824c886a13ce8503e9ea4375264972536d7f3369bc506b) / 거시환경: 원문·관측 기록: “합성 전문가의 반대 검토는 물가 압력이 이어지거나 장기금리가 상승하면 만기 전 장기채 가격이 하락할 수 있다고 경고한다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거. 한계: 개발 검증용 합성 근거이며 실제 현재 시장에 적용할 수 없다. / 검토 의견의 존재와 조건부 손실 경로를 기록한다. 실제 금리 상승의 확률이나 손실 크기는 계산하지 않는다.
  유형: external\_fact; 위치: 합성 문서 v1의 E\_BOND\_RISK 구절; 관측일: 2025-01-24; 분석일: 2025-01-31; 자산 범위: [government\_bond](#record-e9c778e2cbb7e6f9dbdbebc6c463428f28fe252ffeaf65c422ce019c104b31a7).
  해석 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 원문 구절과 fixture의 대상·시점을 대조한 검토 기록이다. 이 기록은 실제 시장 확인이나 미래 결과의 검증이 아니다..
<a id="record-044a29f16d42b7f88daddf9dd3238acfdf6e2aa684435f27d77803b7ec528aa5"></a>

- 근거 [E\_EARNINGS](#record-044a29f16d42b7f88daddf9dd3238acfdf6e2aa684435f27d77803b7ec528aa5) / 출처 [S\_COMPANY\_INSTITUTION](#record-a3ad5ff870f66fa7345d2f44b08f856ee3370a0107ddf9b9c43eab60305a47c9) / 사업·기초가치: 원문·관측 기록: “합성 기업군의 확정 실적 자료에는 비교 가능한 이전 보고기간보다 이익이 증가한 것으로 기록되어 있다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거. 한계: 개발 검증용 합성 근거이며 실제 현재 시장에 적용할 수 없다. / 지정한 가상 기업군의 보고된 이익에만 한정한다. 미래 성장이나 전체 주식시장 성과를 증명하지 않는다.
  유형: external\_fact; 위치: 합성 문서 v1의 E\_EARNINGS 구절; 관측일: 2025-01-24; 분석일: 2025-01-31; 자산 범위: [equity](#record-30703a5c0fcb28e886e06f6769f4cdf59c4e2e7cbe8d944b8e38ff4d11fb2887).
  해석 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 원문 구절과 fixture의 대상·시점을 대조한 검토 기록이다. 이 기록은 실제 시장 확인이나 미래 결과의 검증이 아니다..
<a id="record-84da45149546fb5e59c2e7cb8a7d958cc35ed3f1d5fa32d82fd5a12786eed904"></a>

- 근거 [E\_LIQUIDITY](#record-84da45149546fb5e59c2e7cb8a7d958cc35ed3f1d5fa32d82fd5a12786eed904) / 출처 [S\_RESEARCH](#record-cb4f90a401d7adea71295abb157fc1dcc837114861cd1810a44074067d909831) / 거시환경: 원문·관측 기록: “합성 연구 메모는 지정한 관측 기간의 자금 조달 조건이 이전 비교기간보다 완화된 것으로 요약한다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거. 한계: 개발 검증용 합성 근거이며 실제 현재 시장에 적용할 수 없다. / 합성 연구의 정의와 비교 범위에 한정한다. 주식 가격 상승의 원인이나 지속성을 입증하지 않는다.
  유형: external\_fact; 위치: 합성 문서 v1의 E\_LIQUIDITY 구절; 관측일: 2025-01-24; 분석일: 2025-01-31; 자산 범위: [equity](#record-30703a5c0fcb28e886e06f6769f4cdf59c4e2e7cbe8d944b8e38ff4d11fb2887).
  해석 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 원문 구절과 fixture의 대상·시점을 대조한 검토 기록이다. 이 기록은 실제 시장 확인이나 미래 결과의 검증이 아니다..
<a id="record-94cd9f091e0cf4fe709bd172692a1f2b61d26f138b0b956554f181aad864d7e1"></a>

- 근거 [E\_VALUATION](#record-94cd9f091e0cf4fe709bd172692a1f2b61d26f138b0b956554f181aad864d7e1) / 출처 [S\_RESEARCH](#record-cb4f90a401d7adea71295abb157fc1dcc837114861cd1810a44074067d909831) / 사업·기초가치: 원문·관측 기록: “합성 연구 메모는 주식 가격이 내부의 명시된 비교틀에서 부담스러운 영역에 있다고 해석한다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거. 한계: 개발 검증용 합성 근거이며 실제 현재 시장에 적용할 수 없다. / 가격 부담은 합성 비교틀의 해석이다. 내재가치 확정·가격 하락 예측·저평가 순위를 뜻하지 않는다.
  유형: external\_fact; 위치: 합성 문서 v1의 E\_VALUATION 구절; 관측일: 2025-01-24; 분석일: 2025-01-31; 자산 범위: [equity](#record-30703a5c0fcb28e886e06f6769f4cdf59c4e2e7cbe8d944b8e38ff4d11fb2887).
  해석 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 원문 구절과 fixture의 대상·시점을 대조한 검토 기록이다. 이 기록은 실제 시장 확인이나 미래 결과의 검증이 아니다..
<a id="record-a700daf2ec08c07d54a71a154fb5522c0c9d7f27a2abd36456c4f9f482c0689b"></a>

- 근거 [E\_BREADTH](#record-a700daf2ec08c07d54a71a154fb5522c0c9d7f27a2abd36456c4f9f482c0689b) / 출처 [S\_DATA\_PROVIDER](#record-1db310d72eadd453df445bdad57c71c88b22ed530e99f1683423070c6029c075) / 정량: 원문·관측 기록: “합성 관측표는 상승 참여가 일부 구성에 집중되며 비교기간보다 참여 범위가 약화된 것으로 기록한다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거. 한계: 개발 검증용 합성 근거이며 실제 현재 시장에 적용할 수 없다. / 지정한 가상 구성과 기간의 비수치 요약이다. 전체 시장 폭이나 미래 하락 확률로 확대하지 않는다.
  유형: observed\_fact; 위치: 합성 문서 v1의 E\_BREADTH 구절; 관측일: 2025-01-24; 분석일: 2025-01-31; 자산 범위: [equity](#record-30703a5c0fcb28e886e06f6769f4cdf59c4e2e7cbe8d944b8e38ff4d11fb2887).
  해석 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 원문 구절과 fixture의 대상·시점을 대조한 검토 기록이다. 이 기록은 실제 시장 확인이나 미래 결과의 검증이 아니다..
<a id="record-8cfe5eafe56cb2f3f54c08372a8e45691f6127171694038f6986d64665abd301"></a>

- 근거 [E\_NEWS\_INFLATION](#record-8cfe5eafe56cb2f3f54c08372a8e45691f6127171694038f6986d64665abd301) / 출처 [S\_NEWS](#record-24d3c9a8e7c3bf789ad24de06ac9c6915e3eec4bafbf9524f2567f870167fd4b) / 거시환경: 원문·관측 기록: “합성 경제 기사는 합성 공식 원자료의 후행 물가 관측을 재인용한다.”. 내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 검토 범위에서 채택 가능한 근거. 한계: 개발 검증용 합성 근거이며 실제 현재 시장에 적용할 수 없다. / E\_INFLATION과 같은 S\_PRIMARY 원출처에 의존하므로 별개의 독립 확인으로 세지 않는다.
  유형: external\_fact; 위치: 합성 문서 v1의 E\_NEWS\_INFLATION 구절; 관측일: 2025-01-24; 분석일: 2025-01-31; 자산 범위: [cash](#record-ab0fcec08e18a7bccda1e81df4974e3434fcd36000518f7e776fb85495b5a494), [government\_bond](#record-e9c778e2cbb7e6f9dbdbebc6c463428f28fe252ffeaf65c422ce019c104b31a7), [equity](#record-30703a5c0fcb28e886e06f6769f4cdf59c4e2e7cbe8d944b8e38ff4d11fb2887).
  해석 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 원문 구절과 fixture의 대상·시점을 대조한 검토 기록이다. 이 기록은 실제 시장 확인이나 미래 결과의 검증이 아니다..
<a id="record-e7d1c00ca32c94b045d5c11a8c30dedee03093901d153fe61a621e0c1ea44b6b"></a>

- 근거 [E\_COMMUNITY\_BOND](#record-e7d1c00ca32c94b045d5c11a8c30dedee03093901d153fe61a621e0c1ea44b6b) / 출처 [S\_COMMUNITY](#record-52dfadc283137bc0ae2df13aeccaa38439d5c5c48d3af6384a60084715d2f8fe) / 커뮤니티·내러티브: 원문·관측 기록: “합성 공개 토론 구절에는 “금리가 곧 크게 떨어질 것이므로 장기채는 지금 거의 확실한 기회다”라는 발언이 있다.”. 발언 관측 확인(내용의 진실성 검증 아님): 한정된 범위에서 확인 (supported\_within\_scope); 해석: 검토됨; 확정근거 채택 보류: 발언·내러티브 관측이며 내용의 사실 근거로 채택하지 않음. 한계: 개발 검증용 합성 근거이며 실제 현재 시장에 적용할 수 없다. / 확인한 것은 가상 구절에 이런 발언이 있다는 사실이다. 발언 내용의 사실성은 C\_BOND\_NARRATIVE에서 별도로 다룬다. / 반복·좋아요·조회수·전체 시장의 대표성은 입력하거나 추정하지 않았다.
  유형: observed\_narrative; 위치: 합성 문서 v1의 E\_COMMUNITY\_BOND 구절; 관측일: 2025-01-24; 분석일: 2025-01-31; 자산 범위: [government\_bond](#record-e9c778e2cbb7e6f9dbdbebc6c463428f28fe252ffeaf65c422ce019c104b31a7).
  해석 검토 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 합성 원문 구절과 fixture의 대상·시점을 대조한 검토 기록이다. 이 기록은 실제 시장 확인이나 미래 결과의 검증이 아니다..

### 주장 목록 · 사실 검증과 해석 검토는 별도

<a id="record-54ed47e5e6e848ff38f8898e76374600e2937c2ad2fadf0892ca25818bb6f751"></a>

- 주장 C\_EARNINGS / 입력 원문: “합성 기업군의 보고된 이익 증가라는 좁은 사실은 해당 합성 실적 구절에서 확인된다.”; 자산 범위: [equity](#record-30703a5c0fcb28e886e06f6769f4cdf59c4e2e7cbe8d944b8e38ff4d11fb2887).
  내용 검증: 한정된 범위에서 확인 (supported\_within\_scope); 해석 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: E\_EARNINGS의 합성 확정 실적 구절에만 한정해 확인한다. 이익 증가를 주식의 미래 수익이나 투자 우위로 확대하지 않는다..
  지지: [E\_EARNINGS](#record-044a29f16d42b7f88daddf9dd3238acfdf6e2aa684435f27d77803b7ec528aa5); 반대: 없음; 발언 관측: 없음.
  한계: 실제 기업·시장에 대한 확인이 아니다. / 다른 이익 정의·수정·미확인 기업군은 검토하지 않았다.; 재검토 질문: 같은 기업군·회계 정의의 새 실적이나 정정이 있으면 이익 증가 구절을 다시 대조한다..
<a id="record-d1b0be03aa8075f2eecaea64d2c14f7436f0bff00dd0db0e83b06101c342b902"></a>

- 주장 C\_YIELD\_ORDER / 입력 원문: “합성 기준 시점의 장기 국채 만기수익률은 합성 정책금리보다 낮다.”; 자산 범위: [government\_bond](#record-e9c778e2cbb7e6f9dbdbebc6c463428f28fe252ffeaf65c422ce019c104b31a7).
  내용 검증: 동일한 범위에서 반박됨 (contradicted\_within\_scope); 해석 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: 같은 합성 기준 시점의 E\_LONG\_YIELD와 E\_POLICY\_RATE 값이 이 부등관계와 모순된다. 잘못된 비교를 반박된 주장으로 보존하는 검증 사례다..
  지지: 없음; 반대: [E\_LONG\_YIELD](#record-2c6c6df3c0efa5bbc2b390e25c538afcf234109a6dbc96358836bdb14224f4ed), [E\_POLICY\_RATE](#record-2d5ce882fe0a5ce455a06483e6f4f0b940ddd3743f2d3bef9e2ecb871f7ae186); 발언 관측: 없음.
  한계: 의도적으로 틀리게 넣은 합성 주장이다. 확인된 사실로 게시하면 안 된다. / 두 금리를 비교해도 채권 보유기간 수익이나 상대 투자 매력은 증명되지 않는다.; 재검토 질문: 두 관측의 날짜·금리 정의·단위가 바뀌면 같은 범위의 부등관계를 다시 확인한다..
<a id="record-07ae5403e47ecb4555ae01ff98c9a31b2d722623ac405459f8bd01ef6a72e777"></a>

- 주장 C\_MARKET\_EASING / 입력 원문: “합성 시장 기대 자료에는 정책 완화의 단서가 있지만 큰 인하의 시점과 실제 실현까지 확인된 것은 아니다.”; 자산 범위: [government\_bond](#record-e9c778e2cbb7e6f9dbdbebc6c463428f28fe252ffeaf65c422ce019c104b31a7).
  내용 검증: 일부 확인 (partially\_supported); 해석 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: E\_MARKET\_EXPECTATION은 완화 기대 해석의 존재만 지지한다. E\_INFLATION과 E\_BOND\_RISK를 반대 검토로 연결하며 미래 정책의 실현은 미확인으로 남긴다..
  지지: [E\_MARKET\_EXPECTATION](#record-29827c8ee47ede094c9b27b0c8df797f0b20b867a41b668c8fda412c23e8356e); 반대: [E\_INFLATION](#record-0985fac19dc62891dc6b381df424d0c777857b63c0add26f1b76bc933ef1a0f0), [E\_BOND\_RISK](#record-9f09c4dbe2b1eb8c64cafd27f753c49cca13059ebaa7fad072342115c6cce057); 발언 관측: 없음.
  한계: 정책 완화 기대와 실제 정책 결정은 다른 대상이다. / 미래 인하 폭·시점·발생 확률을 계산하지 않는다.; 재검토 질문: 새 물가 관측·정책 발표·시장 기대 변화가 생기면 기대와 실제 결정의 차이를 다시 조사한다..
<a id="record-6fcde66ae675fcbeabd0b394994230c57aff3608de7880ce5c4ba8030a81bf12"></a>

- 주장 C\_EQUITY\_BALANCE / 입력 원문: “합성 주식 자료의 이익·유동성 개선은 추가 조사 이유를 주지만 가격 부담·참여 범위 약화와 충돌해 상대 우위를 확정하기 어렵다.”; 자산 범위: [equity](#record-30703a5c0fcb28e886e06f6769f4cdf59c4e2e7cbe8d944b8e38ff4d11fb2887).
  내용 검증: 자료가 상충함 (disputed); 해석 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: E\_EARNINGS·E\_LIQUIDITY의 지지 논리와 E\_VALUATION·E\_BREADTH의 반대 논리를 함께 검토했다. 이 입력은 주식의 확정 매력·순위·투자비중을 제공하지 않는다..
  지지: [E\_EARNINGS](#record-044a29f16d42b7f88daddf9dd3238acfdf6e2aa684435f27d77803b7ec528aa5), [E\_LIQUIDITY](#record-84da45149546fb5e59c2e7cb8a7d958cc35ed3f1d5fa32d82fd5a12786eed904); 반대: [E\_VALUATION](#record-94cd9f091e0cf4fe709bd172692a1f2b61d26f138b0b956554f181aad864d7e1), [E\_BREADTH](#record-a700daf2ec08c07d54a71a154fb5522c0c9d7f27a2abd36456c4f9f482c0689b); 발언 관측: 없음.
  한계: 서로 다른 질문의 관측을 단일 점수로 더하지 않는다. / 가격에 반영된 기대와 실제 미래 성장 사이의 차이는 미확인이다.; 재검토 질문: 이익 정정·가격 부담 변화·유동성 역전·참여 범위 회복 또는 추가 약화가 나타나면 양쪽 논리를 다시 비교한다..
<a id="record-00571c8ecb2f937d6639011a06513992d2e18ff71134725b3138dbf1646acec3"></a>

- 주장 C\_BOND\_NARRATIVE / 입력 원문: “금리가 곧 크게 떨어질 것이므로 장기채는 지금 거의 확실한 기회다.”; 자산 범위: [government\_bond](#record-e9c778e2cbb7e6f9dbdbebc6c463428f28fe252ffeaf65c422ce019c104b31a7).
  내용 검증: 현재 자료로 확인할 수 없음 (not\_verifiable); 해석 기록: 검토됨 (reviewed); 검토자: synthetic-fixture-review; 검토일: 2025-01-31; 이유: E\_COMMUNITY\_BOND에서 발언의 존재는 확인했다. E\_POLICY\_RATE·E\_LONG\_YIELD·E\_INFLATION·E\_MARKET\_EXPECTATION·E\_BOND\_RISK와 비교했지만 미래 큰 인하와 거의 확실한 투자성과를 기준 시점에서 확인할 수 없다. 미확인 상태를 검토한 기록이며 투자 주장 채택이 아니다..
  지지: [E\_POLICY\_RATE](#record-2d5ce882fe0a5ce455a06483e6f4f0b940ddd3743f2d3bef9e2ecb871f7ae186), [E\_LONG\_YIELD](#record-2c6c6df3c0efa5bbc2b390e25c538afcf234109a6dbc96358836bdb14224f4ed), [E\_MARKET\_EXPECTATION](#record-29827c8ee47ede094c9b27b0c8df797f0b20b867a41b668c8fda412c23e8356e); 반대: [E\_INFLATION](#record-0985fac19dc62891dc6b381df424d0c777857b63c0add26f1b76bc933ef1a0f0), [E\_BOND\_RISK](#record-9f09c4dbe2b1eb8c64cafd27f753c49cca13059ebaa7fad072342115c6cce057); 발언 관측: E\_COMMUNITY\_BOND.
  한계: 합성 발언의 존재와 내용의 진실성은 별개다. / 현재 금리와 기대는 향후 인하·가격 상승·기회 확실성을 증명하지 않는다. / 확인 불가를 반증이나 현금 우위로 바꾸지 않는다.; 재검토 질문: 새 공식 정책·물가 자료와 장기금리 변화, 실제 상품의 만기·현금흐름·가격 민감도를 확인한 뒤 조건부 논리를 다시 조사한다..
<a id="record-6f838cc76ac92c5710eb8e5c4ba207731e274c94b2faf95c1745544e96713e99"></a>

- 주장 C\_LIQUIDITY\_CAUSALITY / 입력 원문: “합성 유동성 조건의 개선이 주식 가격 상승의 원인이다.”; 자산 범위: [equity](#record-30703a5c0fcb28e886e06f6769f4cdf59c4e2e7cbe8d944b8e38ff4d11fb2887).
  내용 검증: 아직 확인되지 않음 (unverified); 해석 기록: 검토 대기 (pending); 검토자: 미기록; 검토일: 미기록; 이유: 합성 유동성 구절만 있으며 가격 경로·인과 식별·다른 설명을 대조한 검토가 없다. 검토 전 가설로 남기고 확정 인사이트로 사용하지 않는다..
  지지: [E\_LIQUIDITY](#record-84da45149546fb5e59c2e7cb8a7d958cc35ed3f1d5fa32d82fd5a12786eed904); 반대: 없음; 발언 관측: 없음.
  한계: 동행과 인과를 구분하기 위한 미검토 합성 주장이다. / 출처와 근거 ID의 존재만으로 인과성이 검증되지 않는다.; 재검토 질문: 필요한 가격·사업·금리·기대 자료와 경쟁하는 설명을 확보하고 별도 의미 검토를 완료해야 한다..

### 계산 목록

<a id="record-b2f1753c14311bc33e661827a5e4a926b0ec47f2427af80e05642dac4093d8de"></a>

- 계산 M\_CASH\_RATE\_GAP: 합성 명목 현금 이자율과 후행 물가상승률의 단순 차이 = -0.5 %p (퍼센트포인트); 방법: rate\_difference\_v1.
  입력: [E\_CASH\_RATE](#record-781048addafe3da8e5fdb6886088902e6f492935b262e90f8dcc012c63c39631), [E\_INFLATION](#record-0985fac19dc62891dc6b381df424d0c777857b63c0add26f1b76bc933ef1a0f0); 자산 범위: [cash](#record-ab0fcec08e18a7bccda1e81df4974e3434fcd36000518f7e776fb85495b5a494); 단위 코드: percentage\_points; 한계: 명목 연 이자율에서 후행 연간 물가상승률을 뺀 기술적 차이이며 단위는 퍼센트포인트다. / 미래 실질수익·사용자 실제 구매력 변화·동일기간 실현 수익이 아니다. / 정확한 복리 실질수익 공식이나 미래 물가 추정을 사용하지 않는다. / 비용·세금은 미확인으로 남기며 계산에 포함하지 않는다. / 이 차이만으로 현금·국채·주식을 순위화하지 않는다. / 두 연율 관측값의 단순 격차다. 관측 물가를 대입해도 미래 실질수익, 확정 투자성과 또는 자산 간 우위를 뜻하지 않는다. 비용·세금·가격변화는 계산하지 않았다..
