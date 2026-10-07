# 미국 주식 Deep Dive · 기대이익의 질과 Treasury 기회비용

- 정보 기준: 2026-10-04T09:32:02.671988+00:00 (UTC) / 2026-10-04T18:32:02.671988+09:00 (한국시간).
- 질문: 미국 주식의 forward valuation은 반복 가능한 이익으로 정당화되는가, 그리고 Treasury 기회비용을 감수할 근거가 충분한가?
- 기존 Opportunity Map의 미국 주식 후속 조사 후보에서 출발한다. 이전 연구의 입력·초안 해시와 사용자 맥락을 고정해 연결했다.
- 작성자: Codex · 실제 공개 원자료 조사 및 근거 대조; **근거에 연결한 연구 초안**이다. 원문 수치 전사·계산 확인과 경제적 해석의 검토를 구분한다.
- 매수·매도 명령, 목표가격, 임의 점수, 포트폴리오 비중 및 미래 수익률 추정은 생성하지 않았다.
- 표의 수치는 별도 근거 ID로 추적된다. 계산은 표시상 반올림하며, 정확한 입력·계산 값·원문은 부록과 manifest에 남긴다.

## 핵심 결론

- 전체 판단은 mixed다. 최근 예상 이익이 상향되고 실제 사업 성장도 있어 분모가 모두 허구라는 주장은 지지되지 않는다. 그러나 평균에 가까워진 forward 배수만으로 위험 보상이 충분하다고 확인할 수는 없다. ([60](#opportunity-6b7d1c16c59591fa548f3559dbcf6f1a0e74b7d2752ba1165d7d8b0da7f6cd7a), [58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923), [76](#opportunity-40af50b29fc2a933baae21db3c7f5c042205c7469f5f1bc9eba75813b2d093f6), [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d), [5](#opportunity-9cd65ef6fb7edc8563900ab8602b43cc3031487e3992aad0915a6026f5d0842d))
- 실적의 가장 큰 함정은 EPS 초과분과 반복 가능한 영업 성장을 같은 것으로 보는 것이다. 대형 기업의 평가이익과 세금 효과가 지수 성장에 영향을 주지만, 해당 기업 제외 후에도 다른 기업군의 성장은 남는다. ([50](#opportunity-b8600bd8deef250284422c71d9b794223ab6c97259f188d96a76daef5470da76), [52](#opportunity-508ac2c266322521639c27447547d79009d319c5a0d936e3cf3c9dfcdaffb57f), [36](#opportunity-296b989dfcc7122640fee61bea1996ecc9bb4e0ec975e87578515a1cb48824bf), [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d))
- AI 공급자는 실제 매출과 이익을 기록하고 일부 구매자도 유료 수요를 공개했다. 다만 공급자의 수익과 구매자의 전체 CAPEX 회수는 별개이며, 구매자 현금흐름은 회사와 기간에 따라 상당히 다르다. ([79](#opportunity-57e4dbbc924f0ec234a0e9ffec018db0a3fc8d13b4d1686a9aed0d8fb62a112d), [73](#opportunity-282faaeb22b446a4e13674231f58da7ed73e88f2c558d5c8a33952ca154755f2), [75](#opportunity-aacd0086346ad1a5843f78ef2dd62d70220a9e0c5ffed11f991c8fa305e6f3d9), [4](#opportunity-88fc03b5bc68f014753d8b86df9047b3266294f599424bf045ff05c26682a319), [95](#opportunity-446e2d7f1fb48eacc59df1888c83118dbf60ce7cfa15b41f8db167eed8e0a0a8), [110](#opportunity-d4fc223158d95a3a8034bce468494de0726bf46d26d131a32fa64aa98f5471bf), [113](#opportunity-7794e42e6f3bbdad38a57694f9a354c9af0062ceea5ca16e0f35f3d224ed4141))
- 달러 국채는 실재하는 시작 금리의 대안이다. 현재 주식 이익수익률과 가까운 장기 금리 환경에서는 성장의 반복성과 현금 전환을 검증할 필요가 크지만, 단순 금리 차이는 미래 초과수익이나 적정 배분을 알려주지 않는다. ([6](#opportunity-b58e8146c3c11a468b052598ec28d4d4245f3b8062ded3f8fac26e856cf977ca), [169](#opportunity-68019a948c8c8c365ce41622e139d3f5c886e032164f2180cc56f3d135149b8e), [5](#opportunity-9cd65ef6fb7edc8563900ab8602b43cc3031487e3992aad0915a6026f5d0842d), [82](#opportunity-1019cce484a7a7739959a8e4ba2d4dfdf4abfb0a3ebce5d4dbf29bb7455184bd))
- S&amp;P 지수·Nasdaq 지수·AI 관련 개별 기업은 서로 다른 연구 대상이다. Nasdaq valuation과 개별 기업의 현재 주가 배수는 확보하지 못해 미국 주식 전체나 특정 기업의 가격 매력을 일괄 확정하지 않는다. ([58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923), [64](#opportunity-66774f8cbd44f9662bd86c5f6ac7f2c24026573590ba939cee9eb375ed014ec4), [61](#opportunity-d6f018d7b5412d136438b882d73c1e785547ad6f1ee998b64a05594edd67139c))

## 지금 시장이 기대하는 것

- 동일 제공자의 평균 부근인 forward 배수와 강한 예상 이익 성장의 조합은 분모 실현에 대한 의존을 보여준다. 예상 이익이 낮아지는데 가격이 같으면 배수는 올라간다. 이것이 이번 가설을 시험할 경로이지, 현재 분모가 잘못됐다는 증명은 아니다. ([162](#opportunity-73093f50e5b3d2718365e594b3c901b424a5a91656c007228969c8c7be809404), [152](#opportunity-e7e552d143fe6321c03f0b20ba3fad61adeb0e5445889d4820e904710187dee9), [99](#opportunity-30e83cdba97eb0cbc7bab7414f4f157f9942bbce1210f894deb175a6f9b4c06a))
- 이익 성장이 매출 성장보다 빠를 것이라는 consensus에는 수익성·구성·기저·회계 항목의 기여가 필요하다. 현재 가격이 AI 성장이나 마진 유지 가능성을 이미 어느 정도 반영했다는 해석은 가능하지만, 가격에 포함된 가정을 유일하게 역산할 자료는 없다. ([152](#opportunity-e7e552d143fe6321c03f0b20ba3fad61adeb0e5445889d4820e904710187dee9), [160](#opportunity-6778a553aa00399fafa1be358805067739db73049b4fc5f5a312442b941cddb6), [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d))
- 가설을 반박하는 자료도 있다. 실제 cloud 매출과 영업이익이 증가하고 EPS 예상치가 최근 올라갔으므로, 낮아진 배수가 단순히 근거 없는 먼 미래 약속만으로 만들어졌다고 설명하기 어렵다. ([60](#opportunity-6b7d1c16c59591fa548f3559dbcf6f1a0e74b7d2752ba1165d7d8b0da7f6cd7a), [76](#opportunity-40af50b29fc2a933baae21db3c7f5c042205c7469f5f1bc9eba75813b2d093f6), [39](#opportunity-336adc4556282b6a1e0b10fb829a5ad9dbe3480fb79fa4cc46cee690244bf854), [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d))

## Forward P/E의 분모는 믿을 만한가?

- 현재 자료는 forward 분모가 낙관적일 수 있다는 위험을 일부 뒷받침하지만 과도함을 확정하지 못한다. 추정치 상향과 실매출 성장이라는 반대 증거를 같이 고려한다. 정확한 forward 달러 EPS, 예상 영업마진, 비경상 항목을 조정한 지수 분모는 미확보다. ([60](#opportunity-6b7d1c16c59591fa548f3559dbcf6f1a0e74b7d2752ba1165d7d8b0da7f6cd7a), [58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923), [52](#opportunity-508ac2c266322521639c27447547d79009d319c5a0d936e3cf3c9dfcdaffb57f))
- forward 배수가 낮아진 이유는 가격 변화·예상치 변화·시간이 지나며 바뀐 forward 구간으로 나뉠 수 있다. 현재 보존 자료로 그 기여를 정확히 분해하지 않았고 차기 회계연도 기준과 rolling forward를 혼합하지 않는다. ([162](#opportunity-73093f50e5b3d2718365e594b3c901b424a5a91656c007228969c8c7be809404), [166](#opportunity-863a890922eb503731957e727c17981bd1898d0d0489e7f93d9a5daad63e6ad4), [163](#opportunity-4dbefb1cf006d981bd4fd4206ef0b8a1c5ec7f22d38f072413b56716004514bc), [63](#opportunity-4f0ceaa86703c53a9824524812212fb3d8338d8c7e3f8cfa0ee9ee2afb543122))
- Nasdaq 지수는 금융사를 제외하는 별도 기업군이다. 공식 구성 설명은 확인했지만 최신 valuation·consensus·revision 자료는 미확보여서 S&amp;P나 NVIDIA 실적을 그 지수 전체의 가격 판단으로 대체하지 않는다. ([61](#opportunity-d6f018d7b5412d136438b882d73c1e785547ad6f1ee998b64a05594edd67139c))

### 현재 valuation · 정의와 관측일을 분리한다

| 범위·정의 | 관측일 | P/E | 역수인 이익수익률 | 과거 비교·한계 |
| --- | --- | --- | --- | --- |
| S&amp;P 500 | 2026-09-30 | 19.0 배 ([162](#opportunity-73093f50e5b3d2718365e594b3c901b424a5a91656c007228969c8c7be809404)) | 5.263 % ([6](#opportunity-b58e8146c3c11a468b052598ec28d4d4245f3b8062ded3f8fac26e856cf977ca)) | rolling forward 십이 개월; 같은 제공자의 과거 평균과만 비교 ([58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923)) |
| S&amp;P 500 | 2026-10-01 | 20.43 배 ([163](#opportunity-4dbefb1cf006d981bd4fd4206ef0b8a1c5ec7f22d38f072413b56716004514bc)) | 4.895 % ([8](#opportunity-6392e49e97de10002b6547bb11a22687d01193c152beb50725903e4859f6e1ce)) | FY1 종목별 weighted harmonic; 위 행과 분모가 다름 ([63](#opportunity-4f0ceaa86703c53a9824524812212fb3d8338d8c7e3f8cfa0ee9ee2afb543122)) |
| S&amp;P 500 | 2026-10-01 | 24.62 배 ([167](#opportunity-a95b45c29e1d85ad6b1c1a027d44707f2c232e4955982fdb151d07e2afb26a0a)) | 4.062 % ([9](#opportunity-fe11a56442357956e579d8861fc4b4db6a280cbe3d3089ca595bee693ed2cd01)) | trailing; 과거 회계 이익 ([64](#opportunity-66774f8cbd44f9662bd86c5f6ac7f2c24026573590ba939cee9eb375ed014ec4)) |
| Nasdaq-100 | 자료 미확인 | 미확인 | 미확인 | 현재 동일 정의의 valuation 및 EPS 판본 미확보 |
| 같은 제공자 오 년 평균 | 2026-09-30 | 19.8 배 ([165](#opportunity-c3f1f365bf6c6943467d10b60a833cc77469069bc5e7ce061cfc8a2d5aff4802)) | 해당 없음 | historical mean ([58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923)) |
| 같은 제공자 십 년 평균 | 2026-09-30 | 19.1 배 ([164](#opportunity-26e52141e43b61f663fefa51639a48ea9d23fa1d7cd5912391aeb2656894aac3)) | 해당 없음 | historical mean ([58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923)) |
| 이전 분기말 forward 배수 | 2026-06-30 | 20.4 배 ([166](#opportunity-863a890922eb503731957e727c17981bd1898d0d0489e7f93d9a5daad63e6ad4)) | 미계산 | 당시 가격·추정 분모가 함께 달랐음 ([58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923)) |

- rolling forward 배수는 같은 제공자의 오 년·십 년 평균보다 낮으나 역사적 분위수·최저가·저평가를 의미하지 않는다.
- State Street가 사용하는 기초 데이터의 FactSet 의존도 있어 별개의 독립 검증으로 세지 않는다.
- Nasdaq의 범위 설명은 확보했지만 가격·분모 자료가 없어 다른 지수의 수치를 대입하지 않았다.

## 예상치가 어느 방향으로 바뀌고 있는가?

- 최근 두 분기 EPS 예상치는 분기 중 상향됐고 기업 guidance도 긍정 사례가 우세했다. 이는 최근 기대가 낮아졌다는 가설에 대한 반대 근거다. 기대가 계속 높아지는 동시에 실현해야 할 문턱도 높아질 수 있다. ([149](#opportunity-4735e92aeab47f0c619e0620bb514bf86125b4fee3334249a5a0e04c95cd0550), [153](#opportunity-66b1e8462593efff5028ba8dc5c2a36c5244fa9783cbafad272ede0b6b8c37ad), [59](#opportunity-316f23af85e16b23cf2c3d3571c2761050ce97394468c9a46c388987b30d6e68))
- 연간 성장 예상도 이전 판본보다 높아졌지만, 동일한 기업별 EPS 전망 시계열과 analyst별 변경 분포가 없어 상향의 폭·범위·지속성을 완전히 설명할 수는 없다. guidance 기업 수를 analyst revision 건수로 대체하지 않는다. ([100](#opportunity-2b4a640f819c56f17eeb78cb45c506f1a9def79c966fc8bc7ce40df5b942e610), [99](#opportunity-30e83cdba97eb0cbc7bab7414f4f157f9942bbce1210f894deb175a6f9b4c06a), [59](#opportunity-316f23af85e16b23cf2c3d3571c2761050ce97394468c9a46c388987b30d6e68))

### 예상치 판본과 guidance · analyst 변경 건수와 구분

| 관측 대상 | 이전 판본/음성 | 현재 판본/양성 | 해석 범위 |
| --- | --- | --- | --- |
| 둘째분기 EPS 분기 중 revision | 상향 | 3.4 % ([149](#opportunity-4735e92aeab47f0c619e0620bb514bf86125b4fee3334249a5a0e04c95cd0550)) | 분기 중 per-share consensus 변화; 실제 EPS 증가율 아님 ([57](#opportunity-fea4e3a549d932160d3cbdc73e9d6519da848ff1c0398b5711c6cd23283652a2)) |
| 셋째분기 EPS 분기 중 revision | 상향 | 1.4 % ([153](#opportunity-66b1e8462593efff5028ba8dc5c2a36c5244fa9783cbafad272ede0b6b8c37ad)) | 분기 중 per-share consensus 변화 ([60](#opportunity-6b7d1c16c59591fa548f3559dbcf6f1a0e74b7d2752ba1165d7d8b0da7f6cd7a)) |
| 셋째분기 예상 earnings growth | 26.7 % ([156](#opportunity-c99f385a1413e72205545356a38b500ac01312f15cfb7500f98420a4646fa221)) | 29.5 % ([152](#opportunity-e7e552d143fe6321c03f0b20ba3fad61adeb0e5445889d4820e904710187dee9)) | 전년동기 대비 성장률의 서로 다른 추정 판본 ([59](#opportunity-316f23af85e16b23cf2c3d3571c2761050ce97394468c9a46c388987b30d6e68)) |
| 셋째분기 예상 revenue growth | 10.9 % ([157](#opportunity-31c17d2a4aec9ab493850d9ca2b412fbaff142466c9df2e7b78d5ecea158eaab)) | 12.3 % ([160](#opportunity-6778a553aa00399fafa1be358805067739db73049b4fc5f5a312442b941cddb6)) | 전년동기 대비 매출 성장률의 추정 판본 ([58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923)) |
| 올해 예상 earnings growth | 24.1 % ([100](#opportunity-2b4a640f819c56f17eeb78cb45c506f1a9def79c966fc8bc7ce40df5b942e610)) | 32.4 % ([99](#opportunity-30e83cdba97eb0cbc7bab7414f4f157f9942bbce1210f894deb175a6f9b4c06a)) | 칠월 초와 시월 초 provider 판본; 같은 이유로 바뀌었다는 인과 증명 아님 ([58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923)) |
| 넷째분기 예상 earnings growth | 기대치 | 27.6 % ([161](#opportunity-abf4c6167a636bc85ec5913b587828bf353f515fbe592d7f8bc99517140ac47c)) | 실현값 아님 ([58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923)) |
| 기업 EPS guidance | 44 개 ([155](#opportunity-6d7593215d334eac20aa941badad70051d2afdc8f569acc38233fe05ae66f4c0)) | 72 개 ([158](#opportunity-cf87274a8867005746200c4eb3f37a81277141b9595a5e614d6852d3b9493a1c)) | 음성·양성 guidance 기업 수; analyst 하향·상향 건수 아님 ([59](#opportunity-316f23af85e16b23cf2c3d3571c2761050ce97394468c9a46c388987b30d6e68)) |
| guidance 발표 기업 | 116 개 ([154](#opportunity-53037b12cd639977c63bf48556e737d519f3ea469e3cfc5b20cf9b0092b15fa1)) | 62 % ([159](#opportunity-d2b7630b8092576e7238e834f09facafd5adeaa0f7ae359e0483b6c15485b401)) | 위 기업군의 양성 비율; 지수 전체 기업 비율 아님 ([59](#opportunity-316f23af85e16b23cf2c3d3571c2761050ce97394468c9a46c388987b30d6e68)) |

- 분기 consensus revision과 guidance는 낙관의 현실성을 확인하는 서로 다른 단서다. 상향 자체가 낙관이 옳음을 보장하지는 않는다.
- 연간 달러 EPS 레벨·개별 analyst positive/negative revision 분포·동일 기업의 연속 surprise와 후속 추정치 연결은 미확보다.
- 예상 earnings growth가 revenue growth보다 높아 수익성·구성·기저·비영업 항목의 기여가 필요하지만, 이 두 수치만으로 예상 영업마진을 역산하지 않는다.

## 실제 기업 실적은 기대를 따라가고 있는가?

- 여러 분기에서 consensus 초과와 실제 성장의 단서는 확인된다. 다만 첫째분기의 기업군 실제 성장과 다른 기업군 blended 성장, 둘째분기의 발표 중 blended 값은 모집단과 확정 상태가 달라 하나의 final actual 시계열로 묶을 수 없다. ([51](#opportunity-0bd50cc292ebae23a8190a2ed23e7b7fb81784d8b55ea4eedfd7e5960090c41e), [49](#opportunity-67f88f83d577b04201a022ddd7350653ee9b780e6d9ad0c2f45cb351655c0fee), [55](#opportunity-d37c938f074b4fc26f75020ab141f4fddba305da44efe5573354b648e27db6d3), [52](#opportunity-508ac2c266322521639c27447547d79009d319c5a0d936e3cf3c9dfcdaffb57f))
- Amazon의 GAAP EPS 초과와 후속 지수 추정 상향에는 투자자산 평가이익이 크게 관여했다. Alphabet도 영업 성장보다 훨씬 큰 순이익 증가에 평가이익이 포함됐으며 Meta 이전 분기의 세금 이익은 반복 영업성장과 다르다. ([54](#opportunity-1b207880153d5f87325c148eb3495faec24f75b06b137215ba587f77ecffcba9), [36](#opportunity-296b989dfcc7122640fee61bea1996ecc9bb4e0ec975e87578515a1cb48824bf), [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d), [67](#opportunity-48bf2ab886fc8eed51a714f16d2bd9c345ffe2bcb1247c50ad2fb08fa223b8dd))
- 반대편 근거를 놓치면 안 된다. Microsoft 영업이익, AWS 영업이익, Google Cloud 매출 및 NVIDIA 공급자 실적의 성장 자체는 실제 공시돼 있다. 평가이익이 있다는 사실이 이 사업 성장을 지우지 않는다. ([76](#opportunity-40af50b29fc2a933baae21db3c7f5c042205c7469f5f1bc9eba75813b2d093f6), [39](#opportunity-336adc4556282b6a1e0b10fb829a5ad9dbe3480fb79fa4cc46cee690244bf854), [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d), [79](#opportunity-57e4dbbc924f0ec234a0e9ffec018db0a3fc8d13b4d1686a9aed0d8fb62a112d))
- Meta는 매출 성장에도 최근 영업마진이 전년동기보다 낮아졌다. 공개된 법적 비용도 있으므로 전체 악화를 AI 지출 탓으로 단정하지 않는다. 서로 다른 회사의 좋은 실적을 미국 지수 전체의 미래 수익으로 일반화하지 않는다. ([70](#opportunity-1321b216ca715ccdd1d526a2a0f83c2cf01d02c780146f3bc571920ffacda4e7), [69](#opportunity-f847d37e3d8533aecb2200784f6fcc6b6e9b0b3b009df658340c94674f4e8597))

### 여러 분기의 예상·실적·후속 추정 판본

| 대상 | 비교 기준 | 실제/중간값 | 후속 자료와 한계 |
| --- | --- | --- | --- |
| 첫째분기 지수 EPS surprise | 발표 전 consensus 대비 | 84 % ([144](#opportunity-c617bb8675438c0829a0e3ad516b7a83b1f303efc4e08ab39671cda94e286523)) | positive surprise 비율. 동일 EPS 레벨의 완전한 전후 시계열 아님 ([51](#opportunity-0bd50cc292ebae23a8190a2ed23e7b7fb81784d8b55ea4eedfd7e5960090c41e)) |
| 첫째분기 Mag 기업군 | 실제 earnings growth | 63.2 % ([145](#opportunity-d9bdc8f09d6a500a0ec65beba6d078319a838267cfc7a1285f1b9aaa002a90d9)) | 나머지 기업군은 별도 blended 정의 ([49](#opportunity-67f88f83d577b04201a022ddd7350653ee9b780e6d9ad0c2f45cb351655c0fee)) |
| 첫째분기 기타 기업군 | blended earnings growth | 17.4 % ([146](#opportunity-3403ead72107c2ea6771d22bac4ca24cfa10a800e9544293ea34a71c5a5362b6)) | 전부 final actual이라는 뜻 아님 ([49](#opportunity-67f88f83d577b04201a022ddd7350653ee9b780e6d9ad0c2f45cb351655c0fee)) |
| 둘째분기 시작 예상 | 2026-03-31 | 18.8 % ([151](#opportunity-ff4c27404c7ebb24e7ac148a3ee482924bb4c132beeeefd66524157f020eec28)) | 발표 전 변경을 아래와 구분 ([55](#opportunity-d37c938f074b4fc26f75020ab141f4fddba305da44efe5573354b648e27db6d3)) |
| 둘째분기 발표 직전 예상 | 2026-07-02 | 23.3 % ([148](#opportunity-a78ca6d3932b5b85fe1ea54cdc5b89dc0872f28a4a499d3646e352630dfe8913)) | 발표 직전 상향 ([55](#opportunity-d37c938f074b4fc26f75020ab141f4fddba305da44efe5573354b648e27db6d3)) |
| 둘째분기 발표 중 판본 | 2026-08-03 | 47.4 % ([147](#opportunity-904a07a8fe4e5828efee0b776fd62d91aae63ea96aba9e12d389f7f4a1d3dc4a)) | actual과 미발표 estimates가 섞인 blended ([52](#opportunity-508ac2c266322521639c27447547d79009d319c5a0d936e3cf3c9dfcdaffb57f)) |
| 둘째분기 두 기업 제외 | 2026-08-03 | 28.8 % ([150](#opportunity-4575f64503d310ae597b8fc9489ad4619473a82971018a73f38e259c10b1932a)) | 기업 제외 후에도 성장. 모든 비경상 항목 제거값 아님 ([52](#opportunity-508ac2c266322521639c27447547d79009d319c5a0d936e3cf3c9dfcdaffb57f)) |
| Amazon 둘째분기 GAAP EPS | 1.82 USD/주 ([91](#opportunity-e915fc2397b62a67ce2c969247d103eab8e69ab2482e1fc05be2020ec98fbb9d)) | 5.75 USD/주 ([88](#opportunity-a1804c97e9c94582fab5280da21a248cc375930bd196060127820b8a2116fc51)) | 기대 초과는 확인되나 평가이익 영향을 따로 검토 ([54](#opportunity-1b207880153d5f87325c148eb3495faec24f75b06b137215ba587f77ecffcba9)) |
| 한 주간 이익 순증 기여 | Amazon | 76 % ([98](#opportunity-9a7b059834c435e467a9bdaa05d3b7acc3948ce2286fd3f3e37a5e6ce5c296ed)) | 전체 지수 이익·연간 성장·수익률의 기여 비율로 쓰지 않음 ([54](#opportunity-1b207880153d5f87325c148eb3495faec24f75b06b137215ba587f77ecffcba9)) |

- 여러 분기의 기대 초과와 다음 예상의 상향은 확인되지만, 개별 기업별 당시 consensus·actual·그 직후 revision을 연결한 완전한 패널은 없다.
- 첫째분기 provider 글의 이전 예상치를 설명하는 부분에 다른 분기 레이블이 혼재해 해당 시작 예상 숫자는 사용하지 않았다.
- beat가 다음 revision의 원인이라고 확정하지 않는다. 회계 기저·기업 구성·새 가이던스와 함께 검토해야 한다.

### 공식 최근 실적 · 사업 성장과 회계 EPS를 분리

| 기업·관측항목 | 관측 기간 말 | 관측값 | 비교값/영업 지표 | 회계 요인·해석 |
| --- | --- | --- | --- | --- |
| Microsoft 최근 회계분기 | 2026-06-30 | 90.0 십억 USD ([139](#opportunity-8d0b3366ee2c680cdc42f232731fc05a8665e50e692aed2ca460bd886cb1297d)) | 40.6 십억 USD ([138](#opportunity-4639e68add89ed8038f72d74b728047854207c7666e8817761d59a3b65336b87)) | GAAP와 OpenAI-adjusted EPS 모두 다른 일회 항목을 포함 ([76](#opportunity-40af50b29fc2a933baae21db3c7f5c042205c7469f5f1bc9eba75813b2d093f6)) |
| Microsoft GAAP / adjusted | 2026-06-30 | 4.81 USD/주 ([136](#opportunity-3c09f484c942f3496c07453fc413c6cd8dc6a7c61bdffbd1dcfe646a29103916)) | 4.74 USD/주 ([134](#opportunity-9d77339e64d20ff08bf02db9c3f1822a2f68e52a4dfc7f19cb1b302768e60f5e)) | 3.2 십억 USD ([129](#opportunity-d4a9dde58942bbbeaa03a69b3be646e4df98309f82b80ad49cd628876140ef5d)) |
| Amazon 둘째분기 | 2026-06-30 | 200,606 백만 USD ([94](#opportunity-a09f0c69515564cae44facde399bc2df9f6edf4ad8091e2189e1049cde408c39)) | 27,461 백만 USD ([93](#opportunity-c2c8188a95653b08f775eed887cdffdb94b6eb972545b66d56742dd95ec2c616)) | 50.5 십억 USD ([92](#opportunity-9c8ce6830aa4755cd07334b8388c0d2b2439bfe794023f39277583f37c26f456)) |
| AWS 둘째분기 | 2026-06-30 | 42,232 백만 USD ([90](#opportunity-b6a5495d09248a15d0e1989be582adcbe60c2804f81b3fffc548befcc06f3e73)) | 16,621 백만 USD ([89](#opportunity-b994aeab944cef0b9daf1f3550a2be4713a684fc37789a7e0a5684bff3f9a3eb)) | AI 전용 손익과 고객 ROI 미분리 ([40](#opportunity-b1e3603e6a7013fc14534e3e8ede5925c59341b37516649540d0c9395ff39414)) |
| Google Cloud / Alphabet | 2026-06-30 | 24.8 십억 USD ([101](#opportunity-b900f1535f1e5bb38709eb3cecf043acb5c5c59f594494c67e460699425e917c)) | 34 % ([107](#opportunity-d74255f87d0278fdee5eaef18f94bc23afff1f9ccef6ac314979342b4bb4846c)) | 98.0 십억 USD ([106](#opportunity-38492a72dbaf7f1945299c0ab1ca61e24ded3591daa006f88ac014190a76b00c)) |
| Alphabet 회계 EPS / Cloud 성장 | 2026-06-30 | 9.11 USD/주 ([105](#opportunity-22a67cad831835ab1656dedf5182025de788e020d8bede0cd2e394bacdb11ccf)) | 82 % ([102](#opportunity-85d86b57cbcea4524ae159dda5e9d39bb2fb8488ce840178f32f3e3097de69b6)) | EPS의 급증에는 비영업 평가이익이 크게 작용 ([48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d)) |
| Meta 둘째분기 | 2026-06-30 | 60,801 백만 USD ([127](#opportunity-c4accd3e96ece92e0dadc6f85e044a8622969717a2613b8b496ad33af9f4f191)) | 18,775 백만 USD ([125](#opportunity-e4f9c717ac3738c9f13afcc9a80de4a47634af255ed617f9f0a154d47ee2ae21)) | 2.4 십억 USD ([122](#opportunity-358461e4ff9b1a382923b05fac8c8704684b27bfc5def65e2eb9d91614737a35)) |
| Meta 현재 / 전년동기 margin | 2026-06-30 | 31 % ([123](#opportunity-c0b12216682751663e25aea812e9bf5916421fcc07ab8906401cce1ed6cddfb7)) | 43 % ([126](#opportunity-40ebe93bd8e7138bcf4f730ca13f88d27d26d593da31408a56851f1db80b31b3)) | 비용 상승 전체를 AI에 귀속할 수 없음 ([69](#opportunity-f847d37e3d8533aecb2200784f6fcc6b6e9b0b3b009df658340c94674f4e8597)) |
| Meta 첫째분기 회계 효과 | 2026-03-31 | 8.03 십억 USD ([119](#opportunity-9a010d01af31cff2e946938193c35c9da9511c4c6dbc19433b27fe657db98f80)) | tax benefit | 그 효과를 반복 영업성장으로 보지 않음 ([67](#opportunity-48bf2ab886fc8eed51a714f16d2bd9c345ffe2bcb1247c50ad2fb08fa223b8dd)) |
| NVIDIA 최근 회계분기 | 2026-07-26 | 96,221 백만 USD ([142](#opportunity-10596404e36b7e51a9560e7bc5f22db437f147e73aeaaa783bbe3aa455778c9b)) | 63,734 백만 USD ([141](#opportunity-81adf6140273fcbafbcd61181b5e1efe61eb559111e5ea38f4b80e46b0a43140)) | 구매자의 투자 회수나 현재 주가의 저평가를 증명하지 않음 ([79](#opportunity-57e4dbbc924f0ec234a0e9ffec018db0a3fc8d13b4d1686a9aed0d8fb62a112d)) |
| NVIDIA 매출 성장 / gross margin | 2026-07-26 | 106 % ([143](#opportunity-b1eac2a9c250e22d890d9c3971354f8c7012150465b2fae9d11aed6902541176)) | 75.0 % ([140](#opportunity-91e45f5b51f9f3afad6b434d86938a490060060844cfb61caf30df6a334ad25d)) | 공급자 경제성의 관측 ([79](#opportunity-57e4dbbc924f0ec234a0e9ffec018db0a3fc8d13b4d1686a9aed0d8fb62a112d)) |

- Microsoft 최근 분기는 달력 둘째분기에 끝나는 회계 넷째분기이며 NVIDIA는 여름에 끝나는 회계 둘째분기다. 같은 달력 분기처럼 합산하지 않는다.
- Microsoft의 non-GAAP 조정은 OpenAI 투자 영향 조정으로, Anthropic 평가이익과 다른 일회 항목까지 전부 제거한 수치가 아니다.
- Amazon의 평가 조정액과 Alphabet net gain은 세전/세후·계정 정의가 다르므로 EPS에서 그대로 빼거나 서로 합산하지 않는다.
- 공시된 실제 사업 성장은 존재한다. 이익 초과분의 회계 질 문제를 전체 기업의 무매출·무수익 주장으로 확대하지 않는다.
- 기간 말이 같아도 분기와 최근 일 년은 다르다. 각 행의 기간 설명과 근거의 window를 함께 확인한다.

## AI 투자 사이클

- 투자 사슬은 인프라 공급자와 반도체·GPU·메모리·네트워크, hyperscaler CAPEX, 기업·소비자 도입, 유료 매출, 추가 이익과 현금 회수로 구분한다. 이번 자료는 NVIDIA 공급자와 주요 hyperscaler에서 강하지만 메모리·네트워크 공급자 전체와 최종 고객의 생산성 효과까지 검증한 것은 아니다. ([79](#opportunity-57e4dbbc924f0ec234a0e9ffec018db0a3fc8d13b4d1686a9aed0d8fb62a112d), [75](#opportunity-aacd0086346ad1a5843f78ef2dd62d70220a9e0c5ffed11f991c8fa305e6f3d9), [40](#opportunity-b1e3603e6a7013fc14534e3e8ede5925c59341b37516649540d0c9395ff39414))
- Microsoft의 AI 매출 연환산 규모와 Copilot 유료 좌석 공개는 구매자 측 monetization의 직접 단서다. 그러나 연환산 매출은 완료된 연 매출·순이익·증분 ROIC가 아니며 Azure와 cloud 전체 매출을 AI 전용 매출로 보지 않는다. ([128](#opportunity-4e396e4343ec9dbc5639e6610cb99dce04029096375fe59de7bb83e2fc017890), [75](#opportunity-aacd0086346ad1a5843f78ef2dd62d70220a9e0c5ffed11f991c8fa305e6f3d9))
- Alphabet은 cloud와 영업이익이 늘었지만 최근 분기 FCF가 음수였고 최근 일 년 FCF는 양수였다. Amazon은 AWS 이익이 성장하는 동시에 최근 일 년 net cash PP&amp;E가 OCF를 넘어 FCF가 음수였다. 좋은 영업 성과와 많은 잔여 현금은 같은 사실이 아니다. ([48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d), [110](#opportunity-d4fc223158d95a3a8034bce468494de0726bf46d26d131a32fa64aa98f5471bf), [113](#opportunity-7794e42e6f3bbdad38a57694f9a354c9af0062ceea5ca16e0f35f3d224ed4141), [97](#opportunity-cbf66bd4e581b04e7b55037e42a1fed8d1e155227eb87b8c9a085fc8baaeb37c), [96](#opportunity-d2a2f6d8fdd2ceed329a02a4879f5e4af7de2731bee0efee9ad990313b7a35b0), [95](#opportunity-446e2d7f1fb48eacc59df1888c83118dbf60ce7cfa15b41f8db167eed8e0a0a8), [39](#opportunity-336adc4556282b6a1e0b10fb829a5ad9dbe3480fb79fa4cc46cee690244bf854))
- Microsoft는 현금 PP&amp;E 차감 후에도 현금 잔여가 있지만 이를 리스까지 포함한 총 CAPEX나 AI 전용 투자수익으로 표시하지 않는다. Meta는 두 분기의 CAPEX 증가와 FCF 축소를 공개했으며 연간 지출 guidance의 하단을 높였다. ([4](#opportunity-88fc03b5bc68f014753d8b86df9047b3266294f599424bf045ff05c26682a319), [3](#opportunity-78befe9bced2f80b6e8d6e29a584e9b7e8cf7718a5376fd650eb3414c54ac0f7), [120](#opportunity-a1df977557aab2e6eff61d45ca6c3bfbd3b5b1401ab0b8d105e3bb596ced063d), [117](#opportunity-23406d3f77cb3f3fdefcaada06c4c2526a43b5936706ff7f07ec544f67c3160f), [121](#opportunity-142c3ea2d07a48f1be6e67d7bcaa0575ceaf7f8c7b2607502faa70150faa4c3c), [118](#opportunity-b06059dc19c5bfa984e1c5a11e7dbbb5644af33d35d7bff1ba16320b84cfa893), [69](#opportunity-f847d37e3d8533aecb2200784f6fcc6b6e9b0b3b009df658340c94674f4e8597))
- 설비 지출의 현금 유출이 먼저 나타나고 감가상각은 시간에 걸쳐 손익에 반영될 수 있다. 공개된 감가상각 계정은 모두 같은 범위가 아니므로 회사 간 효율 순위를 만들 수 없다. 향후 활용률·자산 수명·가격·추가 매출과 마진이 관찰 조건이다. ([72](#opportunity-a4ef4d503886c9613a87e27cb4ce4ece799d20d62a6ab9f84e425db74553f9f0), [46](#opportunity-072a77d83aa661d8dc45c55d58f4920c78171325f6bfa81e6bad99ce1475713a), [38](#opportunity-125d2475b86dd881d37f5ce1b1c2648b98cb16f4b87055eb486f9f7a83f5e9fe))
- NVIDIA의 높은 성장과 gross margin은 공급자 경제성의 증거다. 매출채권의 직접 고객 집중과 일부 연장 결제 조건은 현금 전환을 관찰할 이유지만 해당 비율은 매출 비중도 연체율도 아니다. 성장률만으로 현재 주가의 저평가나 고객 ROI를 확인할 수 없다. ([79](#opportunity-57e4dbbc924f0ec234a0e9ffec018db0a3fc8d13b4d1686a9aed0d8fb62a112d), [77](#opportunity-a7351bc446441eca1ad10a93e679bd66981710311f5e4d56ff501bbce4717cd7), [78](#opportunity-494a017b5dc8879f93569451f08c625e064ee6e04dcad1e44aa2a15660e78563))

### AI 구매자 · CAPEX와 남는 현금의 정의가 다르다

| 기업·기간 | 관측 기간 말 | OCF | 설비 지출/다른 기간 | FCF 또는 제한된 잔여 | 정의·해석 |
| --- | --- | --- | --- | --- | --- |
| Microsoft 직전 회계분기 | 2026-03-31 | 46,679 백만 USD ([133](#opportunity-12e23f701fcb503535ad306522457922705dcf6b17596d0c1a02140ae2782f9d)) | -30,876 백만 USD ([132](#opportunity-61bd1a6d733adba9dd6390d1698abc1bd63edac87da8a673186b5372ac760fe5)) | 15803.000 백만 USD ([3](#opportunity-78befe9bced2f80b6e8d6e29a584e9b7e8cf7718a5376fd650eb3414c54ac0f7)) | 현금 PP&amp;E 차감 잔여; 전체 리스 CAPEX 아님 |
| Microsoft 최근 회계분기 | 2026-06-30 | 55,441 백만 USD ([137](#opportunity-71fd39dc85c150853a1e5a60fcb87130b2c0ab60a5ebf921c45895ceb6f5d849)) | -35,802 백만 USD ([135](#opportunity-c1f2a0ed63a34b3fffc1d6a0db03484fc8a8358c9c7012ffd8e8809c530a4aba)) | 19639.000 백만 USD ([4](#opportunity-88fc03b5bc68f014753d8b86df9047b3266294f599424bf045ff05c26682a319)) | 현금 PP&amp;E 차감 잔여; AI 단독 수익성 아님 |
| Alphabet 직전 분기 | 2026-03-31 | 동일 공시 판본 | -35,674 백만 USD ([109](#opportunity-596d06d1667c9bebda7c21459082c4ac93060ff62510faa88581ee7eeb30e0d4)) | 10,116 백만 USD ([108](#opportunity-e5c3ccc2431543e79bd0cc5362ef4a417f2c233d59266251cd939007fd18ac86)) | 분기 기준 FCF ([47](#opportunity-45223e78f81c1f85bea9f34da572b462652182a4214e7f422b0c50ad66e14a60)) |
| Alphabet 최근 분기 | 2026-06-30 | 39,069 백만 USD ([111](#opportunity-39abd35bfec4d58697fde8df5647c83fee3e839f57e2b631741500cf7ec56d4f)) | -44,924 백만 USD ([112](#opportunity-6cd47a78e20b299a53fe58d858430b10e30b88647bc3bca1939fcdf6287785a3)) | -5,855 백만 USD ([110](#opportunity-d4fc223158d95a3a8034bce468494de0726bf46d26d131a32fa64aa98f5471bf)) | 분기 기준 FCF ([47](#opportunity-45223e78f81c1f85bea9f34da572b462652182a4214e7f422b0c50ad66e14a60)) |
| Alphabet 최근 일 년 | 2026-06-30 | TTM | TTM | 53,273 백만 USD ([113](#opportunity-7794e42e6f3bbdad38a57694f9a354c9af0062ceea5ca16e0f35f3d224ed4141)) | 직전 분기 음수와 연간 현금 적자를 구별 ([47](#opportunity-45223e78f81c1f85bea9f34da572b462652182a4214e7f422b0c50ad66e14a60)) |
| Amazon 최근 일 년 | 2026-06-30 | 161,403 백만 USD ([97](#opportunity-cbf66bd4e581b04e7b55037e42a1fed8d1e155227eb87b8c9a085fc8baaeb37c)) | -169,007 백만 USD ([96](#opportunity-d2a2f6d8fdd2ceed329a02a4879f5e4af7de2731bee0efee9ad990313b7a35b0)) | -7,604 백만 USD ([95](#opportunity-446e2d7f1fb48eacc59df1888c83118dbf60ce7cfa15b41f8db167eed8e0a0a8)) | 매각·인센티브 차감한 net cash PP&amp;E; 전체 리스 경제비용 아님 ([35](#opportunity-cbd103faa7480536d1e3615e8a546a5333e8947a770b6b8dfab33bc615da7621)) |
| Amazon 이전 일 년 | 2025-06-30 | TTM | 전년동기 | 18,184 백만 USD ([87](#opportunity-2e5f29377d2a9713fb270e848c311ef250ebbf35a7f5bcbf82a0eed3b18d5e97)) | 위와 동일 reported FCF 정의 ([35](#opportunity-cbd103faa7480536d1e3615e8a546a5333e8947a770b6b8dfab33bc615da7621)) |
| Meta 직전 분기 | 2026-03-31 | 분기 기준 | 19.84 십억 USD ([117](#opportunity-23406d3f77cb3f3fdefcaada06c4c2526a43b5936706ff7f07ec544f67c3160f)) | 12.39 십억 USD ([118](#opportunity-b06059dc19c5bfa984e1c5a11e7dbbb5644af33d35d7bff1ba16320b84cfa893)) | finance-lease 원금 포함 CAPEX ([65](#opportunity-ceb2746fc488290c12cb776edfbfd7301b41e8b3b2588f645715ac5e5e06a629)) |
| Meta 최근 분기 | 2026-06-30 | 31.86 십억 USD ([124](#opportunity-31a3ed49ba4897069dcd2002cc2446dc1f611b3b07c014ee68ff69b7dd3905cb)) | 31.08 십억 USD ([120](#opportunity-a1df977557aab2e6eff61d45ca6c3bfbd3b5b1401ab0b8d105e3bb596ced063d)) | 784 백만 USD ([121](#opportunity-142c3ea2d07a48f1be6e67d7bcaa0575ceaf7f8c7b2607502faa70150faa4c3c)) | 원문의 FCF 사용; 반올림된 십억 단위 두 값을 빼서 재생성하지 않음 ([68](#opportunity-037e439c2fb443f15ca126faaf69866dc85ac6d8ea840154f009267914ce6a5f)) |
| Microsoft AI monetization | 2026-03-31 | &gt;37 십억 USD ([128](#opportunity-4e396e4343ec9dbc5639e6610cb99dce04029096375fe59de7bb83e2fc017890)) | 경영진 annual revenue run rate | AI 순이익·ROIC 미확인 | 분기 매출을 연환산한 규모이며 실현된 일 년 매출과 다름 ([73](#opportunity-282faaeb22b446a4e13674231f58da7ed73e88f2c558d5c8a33952ca154755f2)) |

- 모든 지출이 AI 전용이라는 분해 자료가 없다. 구매자의 전체 현금흐름 압박과 특정 AI 프로젝트의 ROI를 혼동하지 않는다.
- Meta의 연간 CAPEX guidance는 하단이 올라갔지만 상단이 같아 전 구간 대폭 상향으로 표현하지 않는다.
- 공급자 매출은 고객의 지출이다. 고객 매출·추가 이익·자산 수명·재투자·현금 회수가 확인돼야 최종 자본수익을 판단할 수 있다.
- 기간 말이 같아도 분기와 최근 일 년은 다르다. 각 행의 기간 설명과 근거의 window를 함께 확인한다.

### 감가상각 영향 · 회사별 계정 범위가 다르다

| 기업·관측 계정 | 관측 기간 말 | 전년동기 | 보고 분기 | 한계 |
| --- | --- | --- | --- | --- |
| Microsoft depreciation / amortization / other | 2025-03-31 | 7,734 백만 USD ([131](#opportunity-5de1379d83de63b86d11aa4c0aff612d33a3b408adc3d5eb537cc172c95f7511)) | 10,167 백만 USD ([130](#opportunity-0103b3000ae938f2854b6a8fb64870a46cd22bc310af1aecde783a91c5dd0c26)) | 기타 포함; AI 서버만의 감가상각 아님 |
| Alphabet PP&amp;E depreciation | 2025-06-30 | 4,998 백만 USD ([104](#opportunity-45fed6453849ced48ef111336de5aad0421c1adc5c483df03e75e6ae4d1c8c2f)) | 7,104 백만 USD ([103](#opportunity-e2f8ed870f207492f12707ef3929d3a85e6bc3eb11731600f1d8bdc04a6fd171)) | 전체 PP&amp;E 감가상각; AI만의 비용 아님 |
| Amazon depreciation / amortization | 2025-06-30 | 15,227 백만 USD ([86](#opportunity-a90039ce24201556510dda28e1a76f32efd5989ca26f145571a109224c8376c7)) | 19,988 백만 USD ([85](#opportunity-8f6b6f53fb565a1551c187f7a61d7add5cae6f59a5f7c42ffc1cf060ba1d33e0)) | PP&amp;E·콘텐츠·operating lease·기타 포함 |

- 설비 지출은 현금흐름에 먼저 반영되고 감가상각은 사용 기간에 걸쳐 손익에 반영된다. 자산 수명·utilization·매출 회수가 중요하다.
- 관측한 감가상각 증가를 앞으로 동일한 속도로 증가한다고 예측하거나 회사 사이 동일 계정처럼 합산하지 않는다.
- Meta의 동등 범위 최신 감가상각 수치와 각 회사의 AI 전용 ROIC는 이번 보존 자료에서 확보하지 못했다.
- 기간 말이 같아도 분기와 최근 일 년은 다르다. 각 행의 기간 설명과 근거의 window를 함께 확인한다.

### CAPEX guidance · 하단 상향과 상단 유지를 구분

| 기업·범위 | 발표일 | 종전 하단 | 현재 하단 | 유지된 상단 |
| --- | --- | --- | --- | --- |
| Meta · finance lease 원금 포함 | 2026-07-29 | 125 십억 USD ([116](#opportunity-0be512fca65a9b17def1e726f9b5a4d4587010f25442de4c87a6c9e5fa7c2764)) | 130 십억 USD ([115](#opportunity-35fbd2f211104049451fa24e4e7cb1cba180166490a5fbeea78e72832485e47f)) | 145 십억 USD ([114](#opportunity-a8002fcb5a61ba42c9b2bd162669c215f538e585443081cdb9774df4b581c62b)) |

- 예측을 실제 지출로 기록하지 않는다. 전체 범위가 같은 폭으로 올라간 것이 아니라 하단이 올라간 조정이다.
- 다른 hyperscaler의 같은 정의 CAPEX guidance와 전체 변경 이력은 미확보이며, 실제 현금 지출 자료로 대체해 전망치로 표현하지 않는다.

## 지수를 보유할 때의 집중 노출

- 상위 증권 비중과 이익 성장 기여는 서로 다른 방식으로 소수 대형 기업의 노출을 보여준다. Alphabet의 복수 주식 종류는 같은 기업이고 broad index를 샀다고 각 기업 위험이 균등해지지는 않는다. ([62](#opportunity-febef5b3512e3246d505fa88c75746433721577dc6e0c32f756954079be875a5), [49](#opportunity-67f88f83d577b04201a022ddd7350653ee9b780e6d9ad0c2f45cb351655c0fee), [54](#opportunity-1b207880153d5f87325c148eb3495faec24f75b06b137215ba587f77ecffcba9))
- 집중은 수익성 높은 사업이 커진 결과일 수도 있어 자체로 나쁘다고 가정하지 않는다. 다만 AI 수요·CAPEX·감가상각·경쟁이라는 공통 충격이 여러 주요 기업에 함께 전달될 수 있으므로 업종·ticker 개수만으로 독립 분산을 주장하지 않는다. ([62](#opportunity-febef5b3512e3246d505fa88c75746433721577dc6e0c32f756954079be875a5), [75](#opportunity-aacd0086346ad1a5843f78ef2dd62d70220a9e0c5ffed11f991c8fa305e6f3d9), [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d), [79](#opportunity-57e4dbbc924f0ec234a0e9ffec018db0a3fc8d13b4d1686a9aed0d8fb62a112d))

### 지수 내 주요 개별 증권 비중

| 증권 | 지수 시가총액 비중 | 확인한 범위 |
| --- | --- | --- |
| NVDA | 8.46 % ([183](#opportunity-ed12823c22c66323845f8705962084e3ab8fe82d69bf056333c4d298d6de1978)) | 2026-10-01 |
| AAPL | 7.30 % ([174](#opportunity-4c9eadb9660cce133c76aa57ed18e5ef4c0f5ccfd4ba3000104088603cdb51f3)) | 2026-10-01 |
| MSFT | 5.77 % ([181](#opportunity-411b4017c67138af5ce79a12018b88376d82d4142b9174aa77927526c27cf0d1)) | 2026-10-01 |
| AMZN | 3.69 % ([176](#opportunity-6f392751231bf7a7e30f55641953ccb8ec0f88d03bb11973dd770df473968eb6)) | 2026-10-01 |
| GOOGL\_A | 3.01 % ([178](#opportunity-066827a4f3b9aa8f17adfc0c10fd7cd999a26ccb6aff421cc25425cb1dced3df)) | 2026-10-01 |
| AVGO | 2.48 % ([177](#opportunity-928fb03a3376901298565132542011883a47f9268f34318e809b8ccc8cc6da5e)) | 2026-10-01 |
| META | 2.42 % ([180](#opportunity-10ec9264c327abf0a433ec7b472c2b3ca35b7c150f7c197e20a844754be64c34)) | 2026-10-01 |
| GOOGL\_C | 2.41 % ([179](#opportunity-5a9e18f7781c0bffd3dd616ac424f066df84de8eebd0979c9ca8877002b792d2)) | 2026-10-01 |
| MU | 1.88 % ([182](#opportunity-457f917e357e99edd1cfe57da35b1ccbe41a05e614b012a3b09a4fa757e58def)) | 2026-10-01 |
| AMD | 1.52 % ([175](#opportunity-ee056bf87dd1d8c584967e67f8ba95f68d00ce1cb44eecfd917e3e304223be8c)) | 2026-10-01 |

- Alphabet은 서로 다른 주식 종류가 같은 기업의 노출이다. 이를 별개의 사업 분산으로 세지 않는다.
- 지수의 시가총액 비중, 이익 비중, 한 주간 예상 이익 변화 기여, 주가 수익 기여는 서로 다른 분모다.
- equal-weight 대비 cap-weight의 같은 기간 총수익률과 최신 이익 집중 비중은 미확보로, 집중의 수익 효과를 수치로 확정하지 않는다.

## 국채라는 대안

- Treasury의 시작 금리는 현재 확인 가능한 달러 대안이다. 단기는 만기 이후 재투자 위험이 크고 장기는 금리·물가 변화에 따른 가격 변동이 크다. 국가 신용과 약정 이자를 이유로 중도 매도나 KRW 결과까지 안전하다고 표현하지 않는다. ([80](#opportunity-e21239fba7cb4fb001969b6e9782c0f26bcecfc702dd353ed82368fc1b4dc848), [82](#opportunity-1019cce484a7a7739959a8e4ba2d4dfdf4abfb0a3ebce5d4dbf29bb7455184bd))
- 같은 관측일의 비교에서 주식 이익수익률은 장기 국채 금리와 가깝거나 더 낮다. 이는 국채라는 기회비용을 무시하기 어렵다는 단서지만 이익의 성장·재투자와 주식 손실 경로를 반영한 기대 초과수익 계산은 아니다. ([6](#opportunity-b58e8146c3c11a468b052598ec28d4d4245f3b8062ded3f8fac26e856cf977ca), [169](#opportunity-68019a948c8c8c365ce41622e139d3f5c886e032164f2180cc56f3d135149b8e), [5](#opportunity-9cd65ef6fb7edc8563900ab8602b43cc3031487e3992aad0915a6026f5d0842d), [8](#opportunity-6392e49e97de10002b6547bb11a22687d01193c152beb50725903e4859f6e1ce), [168](#opportunity-f00e945ee8a304602c6248939d5468e27794d7fdc1fd0ecb3be3ab52a5b921ef), [7](#opportunity-1e6a870c2879f8b6a479255711ad8cc84c7edb3f5addd9ae3584cae0e1e3f1be))
- 이익수익률과 국채 금리의 차이, 과거 실현 초과수익, 현금흐름 모형으로 역산한 implied ERP는 서로 다른 정의다. 현재 자료로 성장·지급·terminal 가정을 채워 ERP나 가격목표를 계산하지 않는다. ([5](#opportunity-9cd65ef6fb7edc8563900ab8602b43cc3031487e3992aad0915a6026f5d0842d), [7](#opportunity-1e6a870c2879f8b6a479255711ad8cc84c7edb3f5addd9ae3584cae0e1e3f1be))

### Treasury라는 실제 달러 대안 · 최신 확보 관측

| 만기 구분 | 관측일 | 명목 연 금리 | 투자 해석 |
| --- | --- | --- | --- |
| 단기 · 삼 개월 | 2026-10-01 | 4.17 % ([172](#opportunity-2b35a6645cd4a91e26afc7ba06ce297d925abeaec2438d0d4ac83a8d36c9c77a)) | 낮은 duration; 만기 이후 재투자 금리는 미확정 |
| 단기 · 이 년 | 2026-10-01 | 4.78 % ([170](#opportunity-2e4ac33afdb1ab63ba4287711b22dadd7a2b9878facb1fb49ce07a310de3a40b)) | 삼 개월보다 가격 변동과 만기 노출이 큼 |
| 중기 · 오 년 | 2026-10-01 | 5.01 % ([173](#opportunity-c2d59a3c600a2937d3ced074289ab8dc3a946dc2046052b405a081497e2fbfbf)) | 금리 변동에 따른 가격 손익·보유 기간 차이 |
| 중장기 · 십 년 | 2026-10-01 | 5.24 % ([168](#opportunity-f00e945ee8a304602c6248939d5468e27794d7fdc1fd0ecb3be3ab52a5b921ef)) | 이 비교의 기준 만기; 무위험 총수익률 의미 아님 |
| 장기 · 삼십 년 | 2026-10-01 | 5.61 % ([171](#opportunity-ce997e26e3bca55bb05cb209ce8b8e618cbe78e38dcd1a394a1ea4a01cb767ad)) | 높은 duration·물가 위험; 높은 금리가 우월성을 자동 증명하지 않음 |

- Fed 공개일과 관측일을 구분한다. nominal constant-maturity 곡선에서 읽은 investment-basis 연 금리이며 개별 채권 실행 가격의 YTM이나 실현 수익이 아니다.
- 개별 채권의 만기 보유와 계속 만기를 굴리는 Treasury ETF는 다르다. 국채의 신용·달러 약정 성격과 중도 가격·물가·KRW 환율 위험을 구분한다.
- 주식의 영구 보유 노출과 서로 다른 채권 만기를 비교한다. 여기서는 같은 날짜의 시작 조건을 관찰하고, 같은 미래 투자 기간의 수익을 계산하지 않았다.

### 주식 이익수익률과 Treasury · 단순 차이는 ERP가 아니다

| 정의 | 관측일 | 주식 이익수익률 | Treasury 십 년 | 설명용 차이 |
| --- | --- | --- | --- | --- |
| FactSet rolling forward | 2026-09-30 | 5.263 % ([6](#opportunity-b58e8146c3c11a468b052598ec28d4d4245f3b8062ded3f8fac26e856cf977ca)) | 5.29 % ([169](#opportunity-68019a948c8c8c365ce41622e139d3f5c886e032164f2180cc56f3d135149b8e)) | -0.027 %p ([5](#opportunity-9cd65ef6fb7edc8563900ab8602b43cc3031487e3992aad0915a6026f5d0842d)) |
| State Street FY1 harmonic | 2026-10-01 | 4.895 % ([8](#opportunity-6392e49e97de10002b6547bb11a22687d01193c152beb50725903e4859f6e1ce)) | 5.24 % ([168](#opportunity-f00e945ee8a304602c6248939d5468e27794d7fdc1fd0ecb3be3ab52a5b921ef)) | -0.345 %p ([7](#opportunity-1e6a870c2879f8b6a479255711ad8cc84c7edb3f5addd9ae3584cae0e1e3f1be)) |

- 이익수익률은 전액 지급되는 현금 이자가 아니다. 낮거나 음수인 차이만으로 주식이 반드시 불리하다고 결론내리지 않는다.
- historical ERP는 특정 과거 기간의 실현 주식 초과수익, model-implied ERP는 성장·지급·terminal 가정에 맞춰 현재 가격에서 역산한 할인율 차이다. 둘 다 이 표의 단순 역수 차이와 다르다.
- 공식 모형에 필요한 현금 지급·성장·terminal 조건이 없어 model-implied ERP와 미래 가격목표를 만들지 않았다.

## 미국주식에 가장 강한 Bull Case

- 가장 강한 상승 논리는 낮아진 forward 배수에 최근 추정치 상향과 실제 사업 성장이 함께 있다는 것이다. 이익이 대형 평가이익에만 의존하지 않고 다른 기업군에도 성장 단서가 있어, 높은 금리 환경에도 이익이 기대를 충족한다면 가격이 계속 정당화될 수 있다. ([162](#opportunity-73093f50e5b3d2718365e594b3c901b424a5a91656c007228969c8c7be809404), [60](#opportunity-6b7d1c16c59591fa548f3559dbcf6f1a0e74b7d2752ba1165d7d8b0da7f6cd7a), [52](#opportunity-508ac2c266322521639c27447547d79009d319c5a0d936e3cf3c9dfcdaffb57f), [76](#opportunity-40af50b29fc2a933baae21db3c7f5c042205c7469f5f1bc9eba75813b2d093f6), [39](#opportunity-336adc4556282b6a1e0b10fb829a5ad9dbe3480fb79fa4cc46cee690244bf854))
- AI는 공급자 매출만 있는 단계라는 주장보다 현실이 복잡하다. 유료 AI 수요와 cloud 성장의 직접 단서가 있어 CAPEX가 장기간 추가 현금 이익으로 전환될 경우 현재의 현금 부담이 미래 사업 확장의 비용일 수 있다. 이는 조건이며 이미 입증된 전체 투자수익은 아니다. ([128](#opportunity-4e396e4343ec9dbc5639e6610cb99dce04029096375fe59de7bb83e2fc017890), [75](#opportunity-aacd0086346ad1a5843f78ef2dd62d70220a9e0c5ffed11f991c8fa305e6f3d9), [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d), [79](#opportunity-57e4dbbc924f0ec234a0e9ffec018db0a3fc8d13b4d1686a9aed0d8fb62a112d))
- 이 시나리오의 필요 조건은 예상 이익의 반복성, 강한 마진 유지, monetization 개선과 현금 전환이다. Treasury의 고정 현금흐름에는 없는 이익 성장 가능성이 주식 보유의 이유가 될 수 있으나 현재 가격에 성장 기대가 반영된 정도가 관건이다. ([152](#opportunity-e7e552d143fe6321c03f0b20ba3fad61adeb0e5445889d4820e904710187dee9), [160](#opportunity-6778a553aa00399fafa1be358805067739db73049b4fc5f5a312442b941cddb6), [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d), [4](#opportunity-88fc03b5bc68f014753d8b86df9047b3266294f599424bf045ff05c26682a319), [82](#opportunity-1019cce484a7a7739959a8e4ba2d4dfdf4abfb0a3ebce5d4dbf29bb7455184bd))

## Base Case에서 필요한 조건

- 사업 이익은 성장하되 상향된 consensus만큼 빠르지 않고 CAPEX가 현금을 계속 흡수하는 경우를 검토한다. 이는 확률이 가장 높다고 추정한 예측이 아니라 현재 상충 자료를 연결한 조건부 시나리오다. ([60](#opportunity-6b7d1c16c59591fa548f3559dbcf6f1a0e74b7d2752ba1165d7d8b0da7f6cd7a), [152](#opportunity-e7e552d143fe6321c03f0b20ba3fad61adeb0e5445889d4820e904710187dee9), [95](#opportunity-446e2d7f1fb48eacc59df1888c83118dbf60ce7cfa15b41f8db167eed8e0a0a8), [110](#opportunity-d4fc223158d95a3a8034bce468494de0726bf46d26d131a32fa64aa98f5471bf), [4](#opportunity-88fc03b5bc68f014753d8b86df9047b3266294f599424bf045ff05c26682a319))
- 이 경우 좋은 회사의 실적과 주주의 수익은 엇갈릴 수 있다. 예상치가 완만해지거나 배수가 낮아지면 성장의 일부가 가격 상승으로 이어지지 않을 수 있으며, 그동안 받지 못한 Treasury 금리도 기회비용이다. ([162](#opportunity-73093f50e5b3d2718365e594b3c901b424a5a91656c007228969c8c7be809404), [5](#opportunity-9cd65ef6fb7edc8563900ab8602b43cc3031487e3992aad0915a6026f5d0842d), [80](#opportunity-e21239fba7cb4fb001969b6e9782c0f26bcecfc702dd353ed82368fc1b4dc848))

## 미국주식에 가장 강한 Bear Case

- 가장 강한 하락 논리는 낮아 보이는 forward 배수가 높은 성장 기대에 의존하는 동안, 최근 큰 EPS beat의 일부는 반복 현금 이익과 다르다는 점이다. 평가·세금 효과가 사라지고 예상 마진이 유지되지 않으면 분모와 배수가 함께 불리해질 수 있다. ([58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923), [54](#opportunity-1b207880153d5f87325c148eb3495faec24f75b06b137215ba587f77ecffcba9), [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d), [67](#opportunity-48bf2ab886fc8eed51a714f16d2bd9c345ffe2bcb1247c50ad2fb08fa223b8dd), [70](#opportunity-1321b216ca715ccdd1d526a2a0f83c2cf01d02c780146f3bc571920ffacda4e7))
- CAPEX는 유지되는데 유료 수요·가격·utilization이 기대보다 낮으면 감가상각과 재투자 부담이 현금 회수를 압박할 수 있다. 일부 구매자의 음수 FCF와 지수 대형 노출은 이 위험을 조사할 근거지만 현재 모든 기업의 AI ROI가 음수라는 증명은 아니다. ([110](#opportunity-d4fc223158d95a3a8034bce468494de0726bf46d26d131a32fa64aa98f5471bf), [95](#opportunity-446e2d7f1fb48eacc59df1888c83118dbf60ce7cfa15b41f8db167eed8e0a0a8), [62](#opportunity-febef5b3512e3246d505fa88c75746433721577dc6e0c32f756954079be875a5), [72](#opportunity-a4ef4d503886c9613a87e27cb4ce4ece799d20d62a6ab9f84e425db74553f9f0), [46](#opportunity-072a77d83aa661d8dc45c55d58f4920c78171325f6bfa81e6bad99ce1475713a))
- 이 조건에서 충분한 국채 시작 금리가 계속 존재하면 주식의 추가 이익 성장 보상에 더 엄격한 검증이 필요할 수 있다. 반대로 예상 이익과 현금 회수가 실현되면 이 하락 논리는 약해지므로 금리차 하나로 결론내리지 않는다. ([5](#opportunity-9cd65ef6fb7edc8563900ab8602b43cc3031487e3992aad0915a6026f5d0842d), [60](#opportunity-6b7d1c16c59591fa548f3559dbcf6f1a0e74b7d2752ba1165d7d8b0da7f6cd7a), [4](#opportunity-88fc03b5bc68f014753d8b86df9047b3266294f599424bf045ff05c26682a319), [80](#opportunity-e21239fba7cb4fb001969b6e9782c0f26bcecfc702dd353ed82368fc1b4dc848))

## Community에서는 무엇을 믿고 있는가

- [관측된 발언 · 내용 미검증] Google의 cloud 이익과 자체 AI 이익을 구분하면서 Gemini 유료 수요가 부족하고 AI가 적자일 것이라는 발언을 관측했다. ([42](#opportunity-6b6a40179761574ea58c576d9d94acfe4d8b4691566cbfd4050555e2afff7a65))
- [관측된 발언 · 내용 미검증] AI CAPEX를 정당화할 매출이 앞으로도 결코 충분하지 않을 것이라는 강한 비관과 회계 불신을 관측했다. ([41](#opportunity-ba665102c6a778348b729a3ad532ed9cdf61c08cff9813251a52dc780d6d990b))
- [관측된 발언 · 내용 미검증] 과거 인터넷 거품 때와 달리 현재 기업에는 실제 매출·이익·자본이 있다는 반론과 높은 valuation·지출 우려가 동시에 등장했다. ([44](#opportunity-4b96c2e5184c49439ccdb6cc8fa3ed19ba8b3f08af2b2e1cb2a21f51fda4891e))
- [관측된 발언 · 내용 미검증] AI 지출이 경제를 이끌고 주가가 향후 추가 지출과 매출을 반영한다는 주장도 관측했다. ([43](#opportunity-246f6943b38c9aa1d3066432a29662152c1dc26947ce6731c70d947887a8e26e))
- [관측된 발언 · 내용 미검증] 주식과 Treasury가 같은 위험은 아니며 달러 노출과 위기 때의 주식 위험을 우려하는 공개 발언을 관측했다. 국채가 반드시 더 매력적이라는 대표 의견으로 확대하지 않는다. ([45](#opportunity-2d74b8fef1c17f4dae7e0cacb17184aa1fcc887a906f0ed7d98cf806d31caf47))

표본과 접근 한계:

- 실제 공개 Hacker News 발언의 목적 표집이며 영어 기술 참여자와 선택한 논의에 편향된다. 전체 투자자 대표성·시장 consensus·인기 추세를 추정하지 않는다.
- Reddit·X·Bogleheads·Lobsters 접근은 기존 robots 정책 또는 정책 확인 실패로 중단했다. 로그인·접근 제한을 우회하지 않았다.
- Stocktwits 공개 페이지는 접근했지만 검증 가능한 개별 message를 확보하지 못했다. 페이지 도착을 narrative 발견 성공으로 세지 않는다.
- 강한 AI 비관·실제 기업 이익 반론·미래 AI 지출 기대·Treasury와 주식 위험 구별은 관측했다. 금리가 더는 중요하지 않다는 서사는 이 표본에서 확인하지 못했다.
- 선택한 공개 발언은 요약해 비교하며 명예·개인정보 목적의 개인 추적이나 bot 식별·전수 수집은 수행하지 않았다.

## Narrative와 Reality의 차이

- [관측된 발언 · 내용 미검증] AI 기업에 매출·이익이 전혀 없다는 일반화는 공급자의 실제 실적과 Microsoft의 직접 monetization 단서에 맞지 않는다. 그러나 Google Cloud 매출이 있다는 이유로 Gemini 단독 이익과 AI 전체 ROIC가 높다고 확인할 수도 없다. ([42](#opportunity-6b6a40179761574ea58c576d9d94acfe4d8b4691566cbfd4050555e2afff7a65), [79](#opportunity-57e4dbbc924f0ec234a0e9ffec018db0a3fc8d13b4d1686a9aed0d8fb62a112d), [128](#opportunity-4e396e4343ec9dbc5639e6610cb99dce04029096375fe59de7bb83e2fc017890), [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d))
- [관측된 발언 · 내용 미검증] CAPEX 부담이 크다는 우려는 일부 FCF 자료와 일치한다. 앞으로 결코 회수할 수 없거나 회계 사기라는 주장은 현재 자료로 검증할 수 없다. 음수 분기 FCF를 연간 전체 적자로 바꾸는 것도 부정확하다. ([41](#opportunity-ba665102c6a778348b729a3ad532ed9cdf61c08cff9813251a52dc780d6d990b), [110](#opportunity-d4fc223158d95a3a8034bce468494de0726bf46d26d131a32fa64aa98f5471bf), [113](#opportunity-7794e42e6f3bbdad38a57694f9a354c9af0062ceea5ca16e0f35f3d224ed4141), [95](#opportunity-446e2d7f1fb48eacc59df1888c83118dbf60ce7cfa15b41f8db167eed8e0a0a8))
- [관측된 발언 · 내용 미검증] 실제 매출·이익이 있는 기업이라는 반론은 공식 실적과 부합한다. 하지만 좋은 회사가 존재한다는 사실로 현재 가격이 좋다고 결론내릴 수 없다. 모든 대형 기업이 AI에서 높은 ROI를 얻는다는 주장 역시 세부 자료가 없어 확인되지 않는다. ([44](#opportunity-4b96c2e5184c49439ccdb6cc8fa3ed19ba8b3f08af2b2e1cb2a21f51fda4891e), [76](#opportunity-40af50b29fc2a933baae21db3c7f5c042205c7469f5f1bc9eba75813b2d093f6), [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d), [79](#opportunity-57e4dbbc924f0ec234a0e9ffec018db0a3fc8d13b4d1686a9aed0d8fb62a112d))
- [관측된 발언 · 내용 미검증] 주가가 미래를 반영한다는 발언은 관측한 서사다. AI 지출이 경제 성장의 원인이라는 주장과 정확히 얼마의 성장 기대가 가격에 반영됐는지는 공식 macro·가격모형으로 검증되지 않았다. ([43](#opportunity-246f6943b38c9aa1d3066432a29662152c1dc26947ce6731c70d947887a8e26e), [58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923))

## 무엇이 발생하면 판단이 달라지는가

- 같은 정의의 달러 forward EPS 레벨과 analyst revision 분포를 확보하고, 새 실적 발표 뒤 추정치가 넓게 상향되는지 일부 평가이익 기업에만 집중되는지 관찰한다. 전반적 하향으로 돌아서면 낮은 forward 배수의 신뢰도는 약해질 수 있다. ([60](#opportunity-6b7d1c16c59591fa548f3559dbcf6f1a0e74b7d2752ba1165d7d8b0da7f6cd7a), [59](#opportunity-316f23af85e16b23cf2c3d3571c2761050ce97394468c9a46c388987b30d6e68), [54](#opportunity-1b207880153d5f87325c148eb3495faec24f75b06b137215ba587f77ecffcba9))
- AI 유료 매출·추가 영업이익·현금 전환이 CAPEX와 감가상각을 따라가는지 본다. 회사별 같은 기간으로 FCF와 지출을 비교하고, 대형 평가이익을 제외해도 반복 이익이 강하다면 현재 우려가 줄어든다. ([128](#opportunity-4e396e4343ec9dbc5639e6610cb99dce04029096375fe59de7bb83e2fc017890), [4](#opportunity-88fc03b5bc68f014753d8b86df9047b3266294f599424bf045ff05c26682a319), [95](#opportunity-446e2d7f1fb48eacc59df1888c83118dbf60ce7cfa15b41f8db167eed8e0a0a8), [110](#opportunity-d4fc223158d95a3a8034bce468494de0726bf46d26d131a32fa64aa98f5471bf), [46](#opportunity-072a77d83aa661d8dc45c55d58f4920c78171325f6bfa81e6bad99ce1475713a))
- 같은 관측일의 Treasury 금리와 같은 정의의 주식 valuation이 바뀌면 기회비용을 다시 확인한다. 금리 하락이 경기·이익 악화와 동시에 생길 수도 있으므로 국채 금리가 내려갔다는 사실만으로 주식 논리가 강화됐다고 보지 않는다. ([162](#opportunity-73093f50e5b3d2718365e594b3c901b424a5a91656c007228969c8c7be809404), [80](#opportunity-e21239fba7cb4fb001969b6e9782c0f26bcecfc702dd353ed82368fc1b4dc848), [5](#opportunity-9cd65ef6fb7edc8563900ab8602b43cc3031487e3992aad0915a6026f5d0842d))
- 대형 기업 외의 이익 성장과 equal-weight 비교 자료를 확보하면 집중이 사업 우위의 결과인지 취약한 분모의 집중인지 더 구분할 수 있다. 현재 자료는 수익 기여를 확정하기 부족하다. ([62](#opportunity-febef5b3512e3246d505fa88c75746433721577dc6e0c32f756954079be875a5), [49](#opportunity-67f88f83d577b04201a022ddd7350653ee9b780e6d9ad0c2f45cb351655c0fee), [52](#opportunity-508ac2c266322521639c27447547d79009d319c5a0d936e3cf3c9dfcdaffb57f))

## 현재 내릴 수 있는 판단

**mixed** · 경제적 해석 초안

- 가설의 조건부 위험은 확인되지만 미국 주식이 겉으로만 싸 보인다는 전면적 결론은 나오지 않는다. 예상치 상향·실제 영업 성장과 회계 이익의 질·CAPEX 현금 부담이 함께 존재하므로 현재 가장 타당한 표현은 mixed다. ([162](#opportunity-73093f50e5b3d2718365e594b3c901b424a5a91656c007228969c8c7be809404), [60](#opportunity-6b7d1c16c59591fa548f3559dbcf6f1a0e74b7d2752ba1165d7d8b0da7f6cd7a), [52](#opportunity-508ac2c266322521639c27447547d79009d319c5a0d936e3cf3c9dfcdaffb57f), [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d), [36](#opportunity-296b989dfcc7122640fee61bea1996ecc9bb4e0ec975e87578515a1cb48824bf), [4](#opportunity-88fc03b5bc68f014753d8b86df9047b3266294f599424bf045ff05c26682a319), [95](#opportunity-446e2d7f1fb48eacc59df1888c83118dbf60ce7cfa15b41f8db167eed8e0a0a8), [110](#opportunity-d4fc223158d95a3a8034bce468494de0726bf46d26d131a32fa64aa98f5471bf), [5](#opportunity-9cd65ef6fb7edc8563900ab8602b43cc3031487e3992aad0915a6026f5d0842d))
- S&amp;P valuation은 이익 전달에 의존하며 일부 AI 관련 기업의 기대는 높은 사업 성장을 요구한다. Treasury를 포기할 만큼 충분한 추가 보상인지 단정할 자료는 없다. Nasdaq 및 개별 주가 valuation은 자료 부족으로 별도 판단을 유보한다. ([162](#opportunity-73093f50e5b3d2718365e594b3c901b424a5a91656c007228969c8c7be809404), [58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923), [62](#opportunity-febef5b3512e3246d505fa88c75746433721577dc6e0c32f756954079be875a5), [80](#opportunity-e21239fba7cb4fb001969b6e9782c0f26bcecfc702dd353ed82368fc1b4dc848))

## 한국 투자자에게 의미하는 것

- 미국 주식과 Treasury의 위 분석은 달러 원천의 경제성이다. 비헤지 KRW 투자자는 양쪽 모두 USD/KRW 노출이 있고 환율이 주식·채권 자체의 결과를 확대하거나 상쇄할 수 있다. 관측된 환율 수준에서 다음 방향을 확정하지 않는다. ([198](#opportunity-e6264ddceb2cd14486287b063dcbdb336ef7605dc926a651e0e5aa56583b899e), [80](#opportunity-e21239fba7cb4fb001969b6e9782c0f26bcecfc702dd353ed82368fc1b4dc848), [58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923))
- 미국 headline CPI는 기존 macro의 물가 환경 단서다. 과거 물가 상승률을 현재 명목 금리에서 빼 미래 실질 수익률로 만들지 않고, 공개·관측·획득 시점이 다른 자료의 역할을 구분한다. ([184](#opportunity-5618befcb710300272b26f6475dd43e6a660730d6cc8d783954c21e964533f7a), [80](#opportunity-e21239fba7cb4fb001969b6e9782c0f26bcecfc702dd353ed82368fc1b4dc848))
- 사용자가 장기 투자와 안정 소득을 제시했더라도 보유자산·부채·주택 자금·필요 현금이 미확인이다. 현재 연구에서 개인의 적정 비중이나 손실 감당 능력을 자동 도출하지 않는다. ([198](#opportunity-e6264ddceb2cd14486287b063dcbdb336ef7605dc926a651e0e5aa56583b899e), [58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923))
- 실제 적용에는 보유 상품의 환헤지·duration·비용·한국 세법상 계좌·과세 조건이 영향을 줄 수 있다. 이번 자료로 순수익이나 세율을 계산하지 않으며 주택 등 예정 지출 통화와 기간이 확인돼야 개인 적절성을 검토할 수 있다. ([198](#opportunity-e6264ddceb2cd14486287b063dcbdb336ef7605dc926a651e0e5aa56583b899e), [80](#opportunity-e21239fba7cb4fb001969b6e9782c0f26bcecfc702dd353ed82368fc1b4dc848))

### 기존 거시 근거와 사용자 맥락

| 원관측 | 관측일 | 값 | 근거 |
| --- | --- | --- | --- |
| 원/달러 뉴욕 정오 기준환율 | 2026-09-25 | 1356.510 KRW\_per\_USD | [198](#opportunity-e6264ddceb2cd14486287b063dcbdb336ef7605dc926a651e0e5aa56583b899e) |
| 미국 headline CPI-U 원지수 (NSA) | 2026-08-01 | 334.980 index | [191](#opportunity-95bedb1a82c5878057b021e4a5c4f230fef156a43501a4a876ebc05790043af8) |
| 미국 국채 10년 명목 시장금리 | 2026-10-01 | 5.240 percent | [192](#opportunity-5ea22e484d99243f2bb8980ada756a7d00bce7b1b4889faa97d70aea979fa23f) |
| 미국 국채 2년 명목 시장금리 | 2026-10-01 | 4.780 percent | [199](#opportunity-c3102ca23240ec811e5b5ff6760356c8ed7b4238555d745fa8db8fec64fc2998) |

| 사용자 항목 | 정보 상태 | 입력 |
| --- | --- | --- |
| base\_currency | self\_reported | KRW |
| birth\_year | self\_reported | 1998 |
| cash\_balance | unknown | UNKNOWN |
| debt | unknown | UNKNOWN |
| emergency\_fund | unknown | UNKNOWN |
| future\_funding\_needs | unknown | UNKNOWN |
| housing\_funds | unknown | UNKNOWN |
| life\_stage | self\_reported | 자산 축적기 |
| long\_horizon | self\_reported | True |
| monthly\_investment | unknown | UNKNOWN |
| permanent\_loss\_concern | self\_reported | True |
| portfolio\_allocation | unknown | UNKNOWN |
| risk\_capacity | unknown | UNKNOWN |
| risk\_tolerance | self\_reported | 비교적 높은 변동성 감수 의향 |
| stable\_income | self\_reported | True |
| tax\_resident | self\_reported | 대한민국 |
| total\_assets | unknown | UNKNOWN |

## 초간단 설명

주가가 예상 이익에 비해 싸 보이더라도 그 이익이 실제로 남는 돈인지 확인해야 합니다. ([58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923), [52](#opportunity-508ac2c266322521639c27447547d79009d319c5a0d936e3cf3c9dfcdaffb57f))
최근 기업의 예상 이익은 올라갔고 실제 사업도 성장해 기대가 모두 허구라고 말할 수는 없습니다. ([60](#opportunity-6b7d1c16c59591fa548f3559dbcf6f1a0e74b7d2752ba1165d7d8b0da7f6cd7a), [76](#opportunity-40af50b29fc2a933baae21db3c7f5c042205c7469f5f1bc9eba75813b2d093f6))
하지만 일부 큰 이익에는 투자자산 평가이익과 세금 효과가 있고 설비 투자 뒤 남는 현금도 회사마다 다릅니다. ([48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d), [67](#opportunity-48bf2ab886fc8eed51a714f16d2bd9c345ffe2bcb1247c50ad2fb08fa223b8dd), [95](#opportunity-446e2d7f1fb48eacc59df1888c83118dbf60ce7cfa15b41f8db167eed8e0a0a8), [4](#opportunity-88fc03b5bc68f014753d8b86df9047b3266294f599424bf045ff05c26682a319))
AI 장비를 파는 회사가 잘 번다고 그 장비를 산 고객이나 지금 주식을 사는 투자자가 잘 번다는 뜻은 아닙니다. ([79](#opportunity-57e4dbbc924f0ec234a0e9ffec018db0a3fc8d13b4d1686a9aed0d8fb62a112d), [110](#opportunity-d4fc223158d95a3a8034bce468494de0726bf46d26d131a32fa64aa98f5471bf))
국채도 이자를 제공하므로 주식의 추가 위험을 감수할 이유를 성장과 현금 회수에서 확인해야 합니다. ([80](#opportunity-e21239fba7cb4fb001969b6e9782c0f26bcecfc702dd353ed82368fc1b4dc848), [5](#opportunity-9cd65ef6fb7edc8563900ab8602b43cc3031487e3992aad0915a6026f5d0842d))
현재는 긍정 근거와 우려가 함께 있어 강한 저평가 결론보다 이익 실현 여부를 지켜볼 판단이 맞습니다. ([162](#opportunity-73093f50e5b3d2718365e594b3c901b424a5a91656c007228969c8c7be809404), [60](#opportunity-6b7d1c16c59591fa548f3559dbcf6f1a0e74b7d2752ba1165d7d8b0da7f6cd7a), [95](#opportunity-446e2d7f1fb48eacc59df1888c83118dbf60ce7cfa15b41f8db167eed8e0a0a8), [5](#opportunity-9cd65ef6fb7edc8563900ab8602b43cc3031487e3992aad0915a6026f5d0842d))
한국 투자자는 달러 환율과 자신의 필요한 현금까지 별도로 생각해야 합니다. ([198](#opportunity-e6264ddceb2cd14486287b063dcbdb336ef7605dc926a651e0e5aa56583b899e), [80](#opportunity-e21239fba7cb4fb001969b6e9782c0f26bcecfc702dd353ed82368fc1b4dc848))

## 비교 한계와 아직 모르는 것

- 최근 접근 가능한 공식 판본을 확보했지만 Sunday 기준 intraday 최신 가격을 주장하지 않는다. valuation·금리·기업 실적의 관측일은 다르다.
- 분기 예상 이익 증가·전년동기 실제 증가·연환산 매출·blended 성장·회계 평가이익·FCF는 다른 정의다. 분모가 다른 숫자를 같은 추세나 수익률처럼 합치지 않는다.
- FactSet과 State Street 기초 데이터의 의존, Amazon 동일 SEC 문서의 구절 분할, Fed CSV와 HTML 같은 원자료를 독립 확인 횟수로 세지 않는다.
- 상향된 consensus와 좋은 사업은 현재 주가의 저평가를 자동 증명하지 않는다. 가격에 포함된 기대는 유일하게 식별되지 않아 조건부 추론으로 남긴다.
- 고정 quote에서 숫자 토큰·단위·정의를 확인하는 것과 표의 올바른 기업·열·기간 선택은 다른 검토다. 의미 검토를 자동 완성한 것으로 표현하지 않는다.
- Nasdaq의 최신 동일 정의 forward/trailing valuation·EPS consensus·revision, 개별 주가와 밸류에이션, 역사적 valuation 분위수는 미확보.
- 지수의 정확한 forward 달러 EPS·revenue level·margin expectation, analyst별 revision 분포와 기업별 완전한 surprise→revision 패널은 미확보.
- hyperscaler별 AI 전용 매출·증분 이익·전체 lease 포함 투자자본·utilization·ROI·고객 생산성, Meta 동등 계정 depreciation과 모든 최근 guidance 변경 이력은 미확보.
- 지수의 최신 이익 집중 비중·같은 기간 equal-weight 대비 총수익 기여와 AI 공급자 전체 산업의 독립 검증은 미확보.
- 사용자의 자산·부채·주택 자금·예정 지출·실제 상품·계좌·비용·환헤지 조건이 unknown이라 개인 배분 판단을 하지 않는다.

## 다음 Deep Dive 하나

다음 Deep Dive: Microsoft와 Alphabet의 AI monetization은 증가한 투자자본을 회수할 반복 현금흐름으로 연결되는가? 유료 매출·증분 마진·자산 수명·리스 포함 자본을 구분해 구매자 측 회수 조건을 검토한다.

제안만 하며 이번 과제에서 수행하지 않았다.

## 부록 · 출처, 원문, 계산과 재현

- 초안 SHA-256: 702fa90a943e298995f5cda09b2396aa280dde3ca4c125e8ca784232a3964f1b; 통합 입력 SHA-256: 727ad09a68c41157c7cefb115c07de58df0d520e1bf36d37ac5fe7938423ef4a.
- 부모 Opportunity Map: \{'id': 'CURRENT\_KRW\_OPPORTUNITY\_MAP', 'input\_sha256': '00b39cb4bacc43b5aef947a493adc8430ac33728afbb7391f1ad153f9d0adf29', 'review\_sha256': '0769787e52eb65f7ae6c4eac5ab14c75189b3870711ab440779b11c4b3f9d922'\}.
- 출처·구절·숫자 일치는 범위가 제한된 확인이다. 금융 의미·가격 적정성·미래 수익은 자동 검증되지 않았다.
- 사실 전사의 해석 상태는 pending, 경제적 주장 상태는 unverified로 유지한다. 원출처가 같은 자료는 독립 증거로 세지 않는다.

<a id="opportunity-a2363a77d9ca915a89649f2ee2d1555fe4cf90ebc42467eb57532c23492cd23f"></a>
### 출처 · DD\_IDX\_FACTSET\_Q3

- FactSet · FactSet Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30; 유형: data\_provider.
- URL: [원문](<https://insight.factset.com/sp-500-earnings-season-preview-q3-2026>)
- 공개: 2026-10-02; 관측: 2026-10-02; 획득: 2026-10-04T08:47:56.772493Z; 상태: available / fresh.
- Snapshot: 6198b9bf0f8b326c9f7d5b6f189ba66ead923a3c112802dad600c44cdbb6bd09; payload SHA-256: 4e44447e5adf5afb3722140d81d84f47764604c1cc9eefb9f4a0ca532335dcc8.
- 보존: excerpt; 이용 조건: https://www.factset.com/legal · Public FactSet analytical article with copyright and disclaimer; robots allow selected public article. Retain only three short attributed excerpts per article and hashes for personal noncommercial research, no figures or full article, no licence or investment recommendation claimed. FactSet estimate methodology and mixed GAAP/non-GAAP basis are provider statements. Provider articles share underlying estimates and are not independent corroboration. Historical articles are historical earnings-season observations, not current earnings estimates..

<a id="opportunity-b142d987c19eaffec60c583a7c58e0e69322cb50f0a5e2cffd5632238b234b93"></a>
### 출처 · DD\_IDX\_FACTSET\_Q2\_START

- FactSet · FactSet Q2 2026 earnings-season entry vintage 2026-07-02; 유형: data\_provider.
- URL: [원문](<https://insight.factset.com/sp-500-earnings-season-preview-q2-2026>)
- 공개: 2026-07-02; 관측: 2026-07-02; 획득: 2026-10-04T08:47:57.553446Z; 상태: available / fresh.
- Snapshot: 7af8663dd3de1ea741a7d8e9bcb7be9e05fd45256c69d769ee76193c6a072f88; payload SHA-256: cde0871d1e7e3b1657ce2a9f156ea6464b7ebbf6b1c1ee7158ae870812d97807.
- 보존: excerpt; 이용 조건: https://www.factset.com/legal · Public FactSet analytical article with copyright and disclaimer; robots allow selected public article. Retain only three short attributed excerpts per article and hashes for personal noncommercial research, no figures or full article, no licence or investment recommendation claimed. FactSet estimate methodology and mixed GAAP/non-GAAP basis are provider statements. Provider articles share underlying estimates and are not independent corroboration. Historical articles are historical earnings-season observations, not current earnings estimates..

<a id="opportunity-db1be23edf9c5bfa5e78dd0d683ca56aa253b02a438aac1a1a3e9e8abc8e1c25"></a>
### 출처 · DD\_IDX\_FACTSET\_Q2\_QUALITY

- FactSet · FactSet Q2 2026 blended earnings-season intermediate vintage 2026-08-03; 유형: data\_provider.
- URL: [원문](<https://insight.factset.com/amazon-drives-sp-500-earnings-growth-for-q2-above-45-on-valuation-gains>)
- 공개: 2026-08-03; 관측: 2026-08-03; 획득: 2026-10-04T08:47:57.986356Z; 상태: available / fresh.
- Snapshot: e732fddc32803e8a360b43cc8a33febca4117e5ca7a649cb272a6b4dfa3e7f07; payload SHA-256: c65ce7ac03455dd9a0dbc122f4998a9ea5a4da2bb5ec60a373f3429e7d65ef5e.
- 보존: excerpt; 이용 조건: https://www.factset.com/legal · Public FactSet analytical article with copyright and disclaimer; robots allow selected public article. Retain only three short attributed excerpts per article and hashes for personal noncommercial research, no figures or full article, no licence or investment recommendation claimed. FactSet estimate methodology and mixed GAAP/non-GAAP basis are provider statements. Provider articles share underlying estimates and are not independent corroboration. Historical articles are historical earnings-season observations, not current earnings estimates..

<a id="opportunity-f42be2a4b1c038cc57d84221d8156e1e0c66dcb47bc57301f888b544d289f707"></a>
### 출처 · DD\_IDX\_FACTSET\_Q1

- FactSet · FactSet Q1 2026 reported cohort, provider vintage 2026-05-21; 유형: data\_provider.
- URL: [원문](<https://insight.factset.com/mag-7-and-other-493-sp-500-companies-are-reporting-highest-earnings-growth-since-2021>)
- 공개: 2026-05-21; 관측: 2026-05-21; 획득: 2026-10-04T08:48:56.374651Z; 상태: available / fresh.
- Snapshot: 6e3cc957189184012501953c7f25bf447f78ef21e3fd8022cc8beccb47344546; payload SHA-256: ec31c8fd12f2dd39297feecfcb8d8eac455fc939c105431c8628a4bd1f146492.
- 보존: excerpt; 이용 조건: https://www.factset.com/legal · Public FactSet analytical article with copyright and disclaimer; robots allow selected public article. Retain only three short attributed excerpts per article and hashes for personal noncommercial research, no figures or full article, no licence or investment recommendation claimed. FactSet estimate methodology and mixed GAAP/non-GAAP basis are provider statements. Provider articles share underlying estimates and are not independent corroboration. Historical articles are historical earnings-season observations, not current earnings estimates..

<a id="opportunity-b3b2aa1a939b74ccffa5a4e1d71c6658758535f8da8309d73896055f1d36e636"></a>
### 출처 · DD\_IDX\_SPY

- State Street Investment Management · State Street SPY: separately defined index valuation and concentration; 유형: institution.
- URL: [원문](<https://www.ssga.com/us/en/individual/etfs/state-street-spdr-sp-500-etf-trust-spy>)
- 공개: UNKNOWN; 관측: 2026-10-01; 획득: 2026-10-04T08:48:58.325065Z; 상태: available / fresh.
- Snapshot: 5bf56092840023270793395a5349275b3149e80836caa5c8e17e6119c4a50734; payload SHA-256: 4505d4f5ca21dbf226d814a8c27fbe036994be37de426e78d622e56103ecea75.
- 보존: excerpt; 이용 조건: https://www.ssga.com/us/en/individual/etfs/state-street-spdr-sp-500-etf-trust-spy · Public product page with copyright and jurisdiction restrictions; robots allow this page. Only three small attributed analytical excerpts and hashes retained for personal research, not logos, full holdings or PDFs. No Korean product access or redistribution rights inferred. FactSet-based estimates overlap other FactSet evidence..

<a id="opportunity-5d86d847122b5ad98b4fd5ae38197d19da3514d24e01b41fdf41ecdce072b925"></a>
### 출처 · DD\_MSFT\_Q4

- Microsoft · Microsoft actual earnings/cashflow evidence; 유형: primary.
- URL: [원문](<https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q4/press-release-webcast>)
- 공개: 2026-07-29; 관측: 2026-06-30; 획득: 2026-10-04T08:51:23.557574Z; 상태: available / fresh.
- Snapshot: 057377ceb5bd4486b99320eda019008534c5369adc71b9b02ba5b115866cb8d6; payload SHA-256: 6484de7aea0d41052f927a0f583f637ac931b90d65e30185d89b2a0aad744bb9.
- 보존: excerpt; 이용 조건: https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q4/press-release-webcast · Public attributed issuer report; robots and source access enforced by existing acquire. Personal noncommercial research retains at most three short excerpts and hashes; no full document or redistribution licence claimed. Issuer statements, unaudited results and management estimates are distinct from audited investor ROI or price forecasts. SEC regulatory filing on publicly permitted EDGAR path; original issuer copyright is not assumed public domain..

<a id="opportunity-b6d2a18034b99aa4454b4ab7f7e1a0541fad2c654914e71c80c468baea14173e"></a>
### 출처 · DD\_MSFT\_Q3

- Microsoft · Microsoft actual earnings/cashflow evidence; 유형: primary.
- URL: [원문](<https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q3/press-release-webcast>)
- 공개: 2026-04-29; 관측: 2026-03-31; 획득: 2026-10-04T08:51:25.001207Z; 상태: available / fresh.
- Snapshot: ad412080214feceb3e9386aefa1ec0e189ed9d39e8ab1e6ee64fa74c98eda4ce; payload SHA-256: 6b8fb63e243320a3f9c56b95b022fb6266c65e6ceaffe3781fc0d38f0c76515a.
- 보존: excerpt; 이용 조건: https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q3/press-release-webcast · Public attributed issuer report; robots and source access enforced by existing acquire. Personal noncommercial research retains at most three short excerpts and hashes; no full document or redistribution licence claimed. Issuer statements, unaudited results and management estimates are distinct from audited investor ROI or price forecasts. SEC regulatory filing on publicly permitted EDGAR path; original issuer copyright is not assumed public domain..

<a id="opportunity-27acb40a74b281394210518738aeac45a15b737a8b8760ce3748621a468a7f5e"></a>
### 출처 · DD\_AMZN\_Q2

- Amazon · Amazon actual earnings/cashflow evidence; 유형: primary.
- URL: [원문](<https://www.sec.gov/Archives/edgar/data/1018724/000101872426000026/amzn-20260630.htm>)
- 공개: 2026-07-31; 관측: 2026-06-30; 획득: 2026-10-04T08:52:48.350276Z; 상태: available / fresh.
- Snapshot: 7e8c6df634dc0f768926ef987dd17ccf9c8204826e01b38d636915e80e99c758; payload SHA-256: 91a001e12dddc44b33e4c20350b72adbc3000bad87fb2a411a8067a0cad91fa3.
- 보존: excerpt; 이용 조건: https://www.sec.gov/about/privacy-information · Public attributed issuer report; robots and source access enforced by existing acquire. Personal noncommercial research retains at most three short excerpts and hashes; no full document or redistribution licence claimed. Issuer statements, unaudited results and management estimates are distinct from audited investor ROI or price forecasts. SEC regulatory filing on publicly permitted EDGAR path; original issuer copyright is not assumed public domain..

<a id="opportunity-1f6ff239f0d6a378d2b271e4b09a6c3bc936394f73f03739e7e3949aae4e35d4"></a>
### 출처 · DD\_AMZN\_Q2\_OPERATING

- Amazon · Amazon actual earnings/cashflow evidence; 유형: primary.
- URL: [원문](<https://www.sec.gov/Archives/edgar/data/1018724/000101872426000026/amzn-20260630.htm>)
- 공개: 2026-07-31; 관측: 2026-06-30; 획득: 2026-10-04T08:52:49.261937Z; 상태: available / fresh.
- Snapshot: 01758ff10302234cb61120e5e967fbaa451f50f05bae45b4e90f78902efdf974; payload SHA-256: 980a212e56086102b2aecdca3c9ff49c4b01005e997c79db8662d9b414f6fe14.
- 보존: excerpt; 이용 조건: https://www.sec.gov/about/privacy-information · Public attributed issuer report; robots and source access enforced by existing acquire. Personal noncommercial research retains at most three short excerpts and hashes; no full document or redistribution licence claimed. Issuer statements, unaudited results and management estimates are distinct from audited investor ROI or price forecasts. SEC regulatory filing on publicly permitted EDGAR path; original issuer copyright is not assumed public domain..

<a id="opportunity-dec2b5f8753df9ace8da1b71ef2308fd6634581c1ca303d15145f442b920cd73"></a>
### 출처 · DD\_META\_Q2

- Meta Platforms · Meta Platforms actual earnings/cashflow evidence; 유형: primary.
- URL: [원문](<https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Second-Quarter-2026-Results/default.aspx>)
- 공개: 2026-07-29; 관측: 2026-06-30; 획득: 2026-10-04T08:52:51.045768Z; 상태: available / fresh.
- Snapshot: 1794cb1b74b11b8b343855fd0c1e693b335ce60019a3121377b88ee464f4cc4c; payload SHA-256: 0b687662b7646318165dcc175f658e99dd5c1d919561b687995a285f4427e212.
- 보존: excerpt; 이용 조건: https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Second-Quarter-2026-Results/default.aspx · Public attributed issuer report; robots and source access enforced by existing acquire. Personal noncommercial research retains at most three short excerpts and hashes; no full document or redistribution licence claimed. Issuer statements, unaudited results and management estimates are distinct from audited investor ROI or price forecasts. SEC regulatory filing on publicly permitted EDGAR path; original issuer copyright is not assumed public domain..

<a id="opportunity-6f2f4999b142113ec649db6b5c170f96452c4f34f85452796901889c9bfdd419"></a>
### 출처 · DD\_META\_Q1

- Meta Platforms · Meta Platforms actual earnings/cashflow evidence; 유형: primary.
- URL: [원문](<https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-First-Quarter-2026-Results/default.aspx>)
- 공개: 2026-04-29; 관측: 2026-03-31; 획득: 2026-10-04T08:52:51.772821Z; 상태: available / fresh.
- Snapshot: 1e879bc36e21c27f13d72748f5c24edf8f15d47327438d438117fbf4c3815494; payload SHA-256: 64ac9b2e51368fab5cf7c41b25e31d2d0a24e0584a6b9c12a536a073da93efb3.
- 보존: excerpt; 이용 조건: https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-First-Quarter-2026-Results/default.aspx · Public attributed issuer report; robots and source access enforced by existing acquire. Personal noncommercial research retains at most three short excerpts and hashes; no full document or redistribution licence claimed. Issuer statements, unaudited results and management estimates are distinct from audited investor ROI or price forecasts. SEC regulatory filing on publicly permitted EDGAR path; original issuer copyright is not assumed public domain..

<a id="opportunity-b6234296e1544fd47c7e27117adb003ac89d8fa89bcb5ce18e129ed9b0cff996"></a>
### 출처 · DD\_GOOGL\_Q2

- Alphabet · Alphabet actual earnings/cashflow evidence; 유형: primary.
- URL: [원문](<https://www.sec.gov/Archives/edgar/data/1652044/000165204426000066/googexhibit991q22026.htm>)
- 공개: 2026-07-22; 관측: 2026-06-30; 획득: 2026-10-04T08:52:52.222092Z; 상태: available / fresh.
- Snapshot: 28b743b35bda051a490972d025f93c8e3ade50acdd970d81047a3d9ad22457a2; payload SHA-256: 6f1483e3429988858d31664e45f900eb932879a9245e1f944800ce4e4b2d07f9.
- 보존: excerpt; 이용 조건: https://www.sec.gov/about/privacy-information · Public attributed issuer report; robots and source access enforced by existing acquire. Personal noncommercial research retains at most three short excerpts and hashes; no full document or redistribution licence claimed. Issuer statements, unaudited results and management estimates are distinct from audited investor ROI or price forecasts. SEC regulatory filing on publicly permitted EDGAR path; original issuer copyright is not assumed public domain..

<a id="opportunity-b3cd92a892c22fd2f10be7198b002951e7e2c3cab60d1f2b10bcafdf8123a444"></a>
### 출처 · DD\_NVDA\_Q2

- NVIDIA Corporation in SEC EDGAR · NVIDIA regulatory quarterly economics and cash conversion; 유형: primary.
- URL: [원문](<https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm>)
- 공개: 2026-08-26; 관측: 2026-07-26; 획득: 2026-10-04T08:55:31.068548Z; 상태: available / fresh.
- Snapshot: d6e3879ec2d94e115817629de4883a79bd49b185fdf7400218eb99da21b12326; payload SHA-256: d53bab078d8c092333458b39ac80782cb00288b3a63cbe88a30874bc67c86f19.
- 보존: excerpt; 이용 조건: https://www.sec.gov/about/privacy-information · Public attributed issuer report; robots and source access enforced by existing acquire. Personal noncommercial research retains at most three short excerpts and hashes; no full document or redistribution licence claimed. Issuer statements, unaudited results and management estimates are distinct from audited investor ROI or price forecasts. SEC regulatory filing on publicly permitted EDGAR path; original issuer copyright is not assumed public domain..

<a id="opportunity-7fcf16b415162ceb577bbc6a78c56d7f8fd2af2f89d0242f91180e4c489053ab"></a>
### 출처 · DD\_TR\_H15\_CURVE

- Board of Governors of the Federal Reserve System · H15 released 2026-10-02: same-date nominal Treasury constant-maturity curve; 유형: primary.
- URL: [원문](<https://www.federalreserve.gov/releases/h15/>)
- 공개: 2026-10-02; 관측: 2026-10-01; 획득: 2026-10-04T09:05:38.940411Z; 상태: available / fresh.
- Snapshot: e213205d355b63a4d58107a4f8f02c071ec2712c970f56bc15001c4bb3c938f2; payload SHA-256: 79a3bbc80fb199736a6d62309e330abe4382dea0ac2b878c0f396f908a98f70c.
- 보존: excerpt; 이용 조건: https://www.federalreserve.gov/disclaimer.htm · Public-domain Federal Reserve information with attribution. Same underlying Treasury observations as macro FED\_H15\_TREASURY CSV; HTML is a definition/date cross-check, not independent empirical confirmation. Excerpts only; seals, logos and separate third-party content excluded..

<a id="opportunity-a5dfa40b4a59dfc97cf95af9ee3f119d1f7994b3a544822f20d35e7d8c19e668"></a>
### 출처 · DD\_COM\_GOOGLE\_LOSS

- HN public participants · Actual HN narrative: DD\_COM\_GOOGLE\_LOSS; 유형: community.
- URL: [원문](<https://hacker-news.firebaseio.com/v0/item/49931960.json>)
- 공개: 2026-10-02T10:35:05+00:00; 관측: 2026-10-02T10:35:05+00:00; 획득: 2026-10-04T08:54:29.644257Z; 상태: available / fresh.
- Snapshot: 3a267eb7fb8d1df1a6af5040486e209d5e2d5222bced187e6137d1d5e1251ad2; payload SHA-256: ea176d563ed41634293ba4b67a953708d498eef47eff834e355f7f97a9becaf6.
- 보존: excerpt; 이용 조건: https://github.com/HackerNews/API · Official documented unauthenticated HN public item API; bounded single-comment request, no account/profile fields selected, no removed/dead content. Only one short attributed analytic quotation and metadata retained for personal research; no complete thread or content redistribution licence claimed. Purpose-selected from public search, not representative or independent fact corroboration..

<a id="opportunity-40322cf942ac59538d864cbfec67416b9a5a959d510f2fd5031ef5b628a6213e"></a>
### 출처 · DD\_COM\_CAPEX\_NEVER

- HN public participants · Actual HN narrative: DD\_COM\_CAPEX\_NEVER; 유형: community.
- URL: [원문](<https://hacker-news.firebaseio.com/v0/item/49926255.json>)
- 공개: 2026-10-01T19:49:49+00:00; 관측: 2026-10-01T19:49:49+00:00; 획득: 2026-10-04T08:54:29.997493Z; 상태: available / fresh.
- Snapshot: ae7eac737b08b40e76c572af6b465fc8c7e77a8b006b69b0dff1f8cf48448e64; payload SHA-256: e206c30c2082c6bd4372bcb935613ceab5f9df6827b0e4fcc12296ebcda992c3.
- 보존: excerpt; 이용 조건: https://github.com/HackerNews/API · Official documented unauthenticated HN public item API; bounded single-comment request, no account/profile fields selected, no removed/dead content. Only one short attributed analytic quotation and metadata retained for personal research; no complete thread or content redistribution licence claimed. Purpose-selected from public search, not representative or independent fact corroboration..

<a id="opportunity-a5cf44fbd1b23ce53aa32fac27165f1416392d0a723c4e26fdb47bd5276c9cc3"></a>
### 출처 · DD\_COM\_REAL\_PROFITS

- HN public participants · Actual HN narrative: DD\_COM\_REAL\_PROFITS; 유형: community.
- URL: [원문](<https://hacker-news.firebaseio.com/v0/item/49934445.json>)
- 공개: 2026-10-02T15:15:23+00:00; 관측: 2026-10-02T15:15:23+00:00; 획득: 2026-10-04T08:54:30.324803Z; 상태: available / fresh.
- Snapshot: 6e3929ac00883c2f627f6d6473d4b82c3ddffda713357abf64e51e47abbb3245; payload SHA-256: 6800a1ae97dbe3b45a3941d21746264b62e942c5c210de61d7dd981e7d1116f2.
- 보존: excerpt; 이용 조건: https://github.com/HackerNews/API · Official documented unauthenticated HN public item API; bounded single-comment request, no account/profile fields selected, no removed/dead content. Only one short attributed analytic quotation and metadata retained for personal research; no complete thread or content redistribution licence claimed. Purpose-selected from public search, not representative or independent fact corroboration..

<a id="opportunity-19711753c6027dc9a92028cc41b90739805178d5114c27bb95990362a2071294"></a>
### 출처 · DD\_COM\_PRICED\_SPENDING

- HN public participants · Actual HN narrative: DD\_COM\_PRICED\_SPENDING; 유형: community.
- URL: [원문](<https://hacker-news.firebaseio.com/v0/item/49931902.json>)
- 공개: 2026-10-02T10:27:40+00:00; 관측: 2026-10-02T10:27:40+00:00; 획득: 2026-10-04T08:54:30.702617Z; 상태: available / fresh.
- Snapshot: 4c396b72de0180ae2df387536d8e21746c5bb5b5ae451c485c1e64bfd21f67fe; payload SHA-256: 747a6162d22585356496310a29abbe4f748fe48df48c51a77c8b9d104cea08a7.
- 보존: excerpt; 이용 조건: https://github.com/HackerNews/API · Official documented unauthenticated HN public item API; bounded single-comment request, no account/profile fields selected, no removed/dead content. Only one short attributed analytic quotation and metadata retained for personal research; no complete thread or content redistribution licence claimed. Purpose-selected from public search, not representative or independent fact corroboration..

<a id="opportunity-1d972995e49eaaf31eff3ce3b50ce395710a6010685e0fa7fda83d51322ef6a7"></a>
### 출처 · DD\_COM\_TREASURY\_RISK

- HN public participants · Actual HN narrative: DD\_COM\_TREASURY\_RISK; 유형: community.
- URL: [원문](<https://hacker-news.firebaseio.com/v0/item/49757470.json>)
- 공개: 2026-09-18T17:23:53+00:00; 관측: 2026-09-18T17:23:53+00:00; 획득: 2026-10-04T08:54:31.186527Z; 상태: available / fresh.
- Snapshot: 12be92dcd4e90a962a5f6cf6d101d42103f71ca2fbc7dfb66aff4b101ee93691; payload SHA-256: 4897d45695ea00b3ed356512c71261843793ef6f23e19e2b6b228ca1c171156f.
- 보존: excerpt; 이용 조건: https://github.com/HackerNews/API · Official documented unauthenticated HN public item API; bounded single-comment request, no account/profile fields selected, no removed/dead content. Only one short attributed analytic quotation and metadata retained for personal research; no complete thread or content redistribution licence claimed. Purpose-selected from public search, not representative or independent fact corroboration..

<a id="opportunity-9891aca891a61cc960b197758ea96c837aff5a4c91dbc7093e3862dc6b46d136"></a>
### 출처 · DD\_COM\_REDDIT\_ACCESS

- Public discussion access attempt · Actual public access attempt; content not adopted; 유형: community.
- URL: [원문](<https://www.reddit.com/r/investing/search/?q=AI%20capex&restrict_sr=1&sort=new>)
- 공개: UNKNOWN; 관측: UNKNOWN; 획득: 2026-10-04T05:26:53.105733Z; 상태: policy\_blocked / unavailable.
- Snapshot: 37192f06d262efb3e346fa9f98e288db29a5bd4c5d14893e6c4460524a21cf29; payload SHA-256: e4d0899b85ab1417370da2c5de1a0df927d71252a10aa5281b84c87c6db5a534.
- 보존: excerpt; 이용 조건: https://www.redditinc.com/policies/user-agreement · Read-only public access and robots/policy inspection attempt. No login, redirect, cookie, access bypass or whole-discussion storage. Content is not adopted as evidence pending site-specific permitted-use review. Placeholder selector is input configuration and never an observed quotation..

<a id="opportunity-00098d17c3d13362dbe92db9c6c1fe6d512090f022cbb31675bf246a85f1c1db"></a>
### 출처 · DD\_COM\_STOCKTWITS\_ACCESS

- Public discussion access attempt · Actual public access attempt; content not adopted; 유형: community.
- URL: [원문](<https://stocktwits.com/symbol/NVDA>)
- 공개: UNKNOWN; 관측: UNKNOWN; 획득: 2026-10-04T05:26:53.786929Z; 상태: changed / unavailable.
- Snapshot: 24206beeb94a6b59e0b15d44c6143084be5d475a6a57b5dabd797a615a590aa0; payload SHA-256: 8ba7c1703c924ae9490c9504cbe999fdc7dda5e5334dce6d29dcecde5ee27427.
- 보존: excerpt; 이용 조건: https://stocktwits.com/terms · Read-only public access and robots/policy inspection attempt. No login, redirect, cookie, access bypass or whole-discussion storage. Content is not adopted as evidence pending site-specific permitted-use review. Placeholder selector is input configuration and never an observed quotation..

<a id="opportunity-b355c57ce851023582ac64c3f87d67759724ceba98450747521f204dde1fc235"></a>
### 출처 · DD\_COM\_X\_ACCESS

- Public discussion access attempt · Actual public access attempt; content not adopted; 유형: community.
- URL: [원문](<https://x.com/search?q=AI%20capex&src=typed_query&f=live>)
- 공개: UNKNOWN; 관측: UNKNOWN; 획득: 2026-10-04T05:26:54.071370Z; 상태: policy\_blocked / unavailable.
- Snapshot: 05f18cec9d1f707757097891ce884a8679fbb1a71e44886ee55d70bdf337b26a; payload SHA-256: e4d0899b85ab1417370da2c5de1a0df927d71252a10aa5281b84c87c6db5a534.
- 보존: excerpt; 이용 조건: https://x.com/en/tos · Read-only public access and robots/policy inspection attempt. No login, redirect, cookie, access bypass or whole-discussion storage. Content is not adopted as evidence pending site-specific permitted-use review. Placeholder selector is input configuration and never an observed quotation..

<a id="opportunity-16239da4a0455d1ff394e5cb068a12d0424fb8705488095b5869c7caa762b0a1"></a>
### 출처 · DD\_COM\_BOGLEHEADS\_ACCESS

- Public discussion access attempt · Actual public access attempt; content not adopted; 유형: community.
- URL: [원문](<https://www.bogleheads.org/forum/viewforum.php?f=10>)
- 공개: UNKNOWN; 관측: UNKNOWN; 획득: 2026-10-04T05:26:54.906883Z; 상태: policy\_blocked / unavailable.
- Snapshot: 8be33dbdbf7de67719d45642f447758b468fd0c7534905efdadff51cce52e874; payload SHA-256: e4d0899b85ab1417370da2c5de1a0df927d71252a10aa5281b84c87c6db5a534.
- 보존: excerpt; 이용 조건: https://www.bogleheads.org/wiki/Bogleheads:Terms\_of\_use · Read-only public access and robots/policy inspection attempt. No login, redirect, cookie, access bypass or whole-discussion storage. Content is not adopted as evidence pending site-specific permitted-use review. Placeholder selector is input configuration and never an observed quotation..

<a id="opportunity-8d57135889c6b64043031f9a7647e49bbd9e95364e190bf2a1fb4d4c123f2d46"></a>
### 출처 · DD\_COM\_LOBSTERS\_ACCESS

- Public discussion access attempt · Actual public access attempt; content not adopted; 유형: community.
- URL: [원문](<https://lobste.rs/t/ai>)
- 공개: UNKNOWN; 관측: UNKNOWN; 획득: 2026-10-04T05:26:56.402739Z; 상태: policy\_blocked / unavailable.
- Snapshot: 367fd4cd27aecc9d68bd93a718d862fc81436dc173049d56885d1df5089be138; payload SHA-256: e4d0899b85ab1417370da2c5de1a0df927d71252a10aa5281b84c87c6db5a534.
- 보존: excerpt; 이용 조건: https://lobste.rs/about · Read-only public access and robots/policy inspection attempt. No login, redirect, cookie, access bypass or whole-discussion storage. Content is not adopted as evidence pending site-specific permitted-use review. Placeholder selector is input configuration and never an observed quotation..

<a id="opportunity-fd6218f0b6833d3660101c1f8b43091161061237229a4d3c3e2167e0bdf2110d"></a>
### 출처 · DD\_IDX\_NDX\_SCOPE

- Nasdaq Global Indexes · Nasdaq100 scope and accessible-research limits; 유형: institution.
- URL: [원문](<https://indexes.nasdaq.com/Index/Overview/NDX>)
- 공개: UNKNOWN; 관측: UNKNOWN; 획득: 2026-10-04T08:59:03.686331Z; 상태: available / unknown.
- Snapshot: 8acb44251fa8ecdda53f0a0fecff488083a3ded8165f2a878ec8a3d7782e3518; payload SHA-256: fe6ab8027769a09ec5338e31d46d0b25ae7596ba4308ddedc7227f997cb4f00d.
- 보존: excerpt; 이용 조건: https://indexes.nasdaq.com/Index/Overview/NDX · Public official index overview, robots checked. Only one short attributed descriptive scope quotation retained for personal research, no licensed index feed, weighting export or PDF redistribution. Publication/effective date unknown; this is captured provider description, not dated valuation observation or historical membership proof..

<a id="opportunity-7b5bff1cb9bb41923e363e62038c607890f6074f6332453191a0e9cedcdf8927"></a>
### 출처 · BLS\_CPI\_RELEASE

- U.S. Bureau of Labor Statistics · Consumer Price Index — August 2026 release; 유형: primary.
- URL: [원문](<https://www.bls.gov/news.release/cpi.htm>)
- 공개: UNKNOWN; 관측: UNKNOWN; 획득: 2026-10-03T17:13:13.854529Z; 상태: available / per\_observation.
- Snapshot: 2453dd6520e8899086a09329e0e73b013935feed8091429efd5dec9dbfece26b; payload SHA-256: 3f7e347e2146b1e483a63b9df2f50561206b6fa577e23c9d5a534557bf546d50.
- 보존: excerpt; 이용 조건: https://www.bls.gov/bls/linksite.htm · Official BLS public-domain release; preserve only three verification excerpts with attribution. Separate API terms apply to API data..

<a id="opportunity-c436613f5d09e28fd85e2bc46b272d6421f81f0e3f63f160bcbb83e83676c4ce"></a>
### 출처 · BLS\_CPI\_API

- U.S. Bureau of Labor Statistics · BLS CPI-U all items, U.S. city average, not seasonally adjusted; 유형: primary.
- URL: [원문](<https://api.bls.gov/publicAPI/v1/timeseries/data/CUUR0000SA0>)
- 공개: UNKNOWN; 관측: UNKNOWN; 획득: 2026-10-03T17:13:14.741705Z; 상태: available / per\_observation.
- Snapshot: 5f659b87469da318e1d476987fb1d686bdf23f34cae1194297a4996299564a05; payload SHA-256: 96cb8805cc869a9ca8500a0b01c79b84d21e1b3ecd52b92143c9eae964f89f1c.
- 보존: full; 이용 조건: https://www.bls.gov/developers/termsOfService.htm · Documented unregistered v1 GET API: https://www.bls.gov/developers/api\_signature.htm . Public-domain data: https://www.bls.gov/bls/linksite.htm . Cite access/retrieval date. BLS.gov cannot vouch for the data or analyses derived from these data after the data have been retrieved from BLS.gov..

<a id="opportunity-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700"></a>
### 출처 · FED\_H15\_TREASURY

- Board of Governors of the Federal Reserve System · H.15 Treasury constant-maturity nominal yield CSV; 유형: primary.
- URL: [원문](<https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&series=bf17364827e38702b42a58cf8eaa3f78&lastobs=&from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package>)
- 공개: UNKNOWN; 관측: UNKNOWN; 획득: 2026-10-03T17:13:15.483675Z; 상태: available / per\_observation.
- Snapshot: 79a230cc8bff4d412dd2e177ce59c8d2f218131dd37a72bf1cda3324e78f6c9b; payload SHA-256: 2816fe45201beabe3da0c4732dc3bad68a1c7b418057264de84e145ffe2935c2.
- 보존: full; 이용 조건: https://www.federalreserve.gov/disclaimer.htm · The Federal Reserve Board permits reuse of public-domain information with Board attribution; no seals, logos or third-party content are fetched..

<a id="opportunity-f56e2932df7c7cf95311e4e66639477af2df08d54da6d6f81da7d23af5c880f1"></a>
### 출처 · FED\_H10\_KRW

- Board of Governors of the Federal Reserve System · H.10 South Korean won per U.S. dollar daily reference rate CSV; 유형: primary.
- URL: [원문](<https://www.federalreserve.gov/datadownload/Output.aspx?rel=H10&series=60f32914ab61dfab590e0e470153e3ae&lastobs=250&from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package>)
- 공개: UNKNOWN; 관측: UNKNOWN; 획득: 2026-10-03T17:13:16.104545Z; 상태: available / per\_observation.
- Snapshot: e6024ea571d2a6c5b6cd6ed43e1ca06a25673b8ccb4051ed3fdb284d32f9ca0f; payload SHA-256: f30d02b572c8722d2c9e5645130190f2da29bcbdcd83c97897225de4045f0802.
- 보존: full; 이용 조건: https://www.federalreserve.gov/disclaimer.htm · The Federal Reserve Board permits reuse of public-domain information with Board attribution; no seals, logos or third-party content are fetched. Definition: https://www.federalreserve.gov/releases/h10/about.htm . Noon New York buying rate; daily observations released weekly; current country CSV can include later corrections..

<a id="opportunity-6b7d1c16c59591fa548f3559dbcf6f1a0e74b7d2752ba1165d7d8b0da7f6cd7a"></a>
### 근거 · E\_DD\_IDX\_FACTSET\_Q3\_REVISIONS

- 출처: [26](#opportunity-a2363a77d9ca915a89649f2ee2d1555fe4cf90ebc42467eb57532c23492cd23f); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: On a per-share basis, estimated earnings for the third quarter increased by 1.4% from June 30 to September 30. In a typical quarter, analysts usually lower earnings estimates during the quarter. Over the past five years (20 quarters), earnings expectations have fallen by 2.2% on average during the quarter. Over the past ten years, (40 quarters), earnings expectations have fallen by 2.5% on average during the quarter.
- 위치: Analyst estimate revisions paragraph; 구절: REVISIONS; snapshot: 6198b9bf0f8b326c9f7d5b6f189ba66ead923a3c112802dad600c44cdbb6bd09.
- 정의: \{'adjustment': 'Quarter-specific consensus EPS estimate revision; provider averages, not realized EPS growth', 'currency': 'USD', 'measure': 'Quarterly EPS estimate revision', 'period': 'Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30', 'scope': 'S&amp;P 500, provider FactSet; quarterly reporting population and vintage as described, not audited total future index income', 'unit': 'percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-316f23af85e16b23cf2c3d3571c2761050ce97394468c9a46c388987b30d6e68"></a>
### 근거 · E\_DD\_IDX\_FACTSET\_Q3\_GUIDANCE

- 출처: [26](#opportunity-a2363a77d9ca915a89649f2ee2d1555fe4cf90ebc42467eb57532c23492cd23f); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: At this point in time, 116 companies in the index have issued EPS guidance for Q3 2026. Of these companies, 44 have issued negative EPS guidance and 72 have issued positive EPS guidance. The number of companies issuing positive EPS guidance is well above the 5-year average of 42 and well above the 10-year average of 40. The percentage of S&amp;P 500 companies issuing positive EPS guidance for Q3 2026 is 62% (72 out of 116), which is also well above the 5-year average of 40% and well above the 10-year average of 41%. Due to the upward revisions to earnings estimates by analysts and the positive EPS guidance issued by companies, the estimated (year-over-year) earnings growth rate for Q3 2026 is higher today relative to the start of the third quarter. As of today, the S&amp;P 500 is expected to report (year-over-year) earnings growth of 29.5%, compared to the estimated (year-over-year) earnings growth rate of 26.7% on June 30.
- 위치: Positive and negative guidance population paragraph; 구절: GUIDANCE; snapshot: 6198b9bf0f8b326c9f7d5b6f189ba66ead923a3c112802dad600c44cdbb6bd09.
- 정의: \{'adjustment': 'Reported positive/negative guidance count among guiders only, not analyst upgrade/downgrade counts or all index members', 'currency': 'USD', 'measure': 'Company EPS guidance population', 'period': 'Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30', 'scope': 'S&amp;P 500, provider FactSet; quarterly reporting population and vintage as described, not audited total future index income', 'unit': 'counts and percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923"></a>
### 근거 · E\_DD\_IDX\_FACTSET\_Q3\_GROWTH\_PRICE

- 출처: [26](#opportunity-a2363a77d9ca915a89649f2ee2d1555fe4cf90ebc42467eb57532c23492cd23f); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: As of today, the S&amp;P 500 is expected to report (year-over-year) revenue growth of 12.3%, compared to the expectations for revenue growth of 10.9% on June 30. If 12.3% is the actual revenue growth rate for the quarter, it will mark the third consecutive quarter of double-digit revenue growth for the index. All eleven sectors are projected to report year-over-year growth in revenues, led by the Information Technology, Energy, and Communication Services sectors. For Q4 2026, analysts are calling for earnings growth of 27.6%. For CY 2026, analysts are predicting (year-over-year) earnings growth of 32.4%. The forward 12-month P/E ratio is 19.0 (based on Wednesday’s closing price and forward EPS), which is below the 5-year average (19.8) and below the 10-year average (19.1). This P/E ratio is also below the forward P/E ratio of 20.4 recorded at the end of the second quarter (June 30).
- 위치: Expected earnings/revenue and forward valuation paragraphs; 구절: GROWTH\_PRICE; snapshot: 6198b9bf0f8b326c9f7d5b6f189ba66ead923a3c112802dad600c44cdbb6bd09.
- 정의: \{'adjustment': 'Forward earnings are estimates, valuation based on Wednesday 2026-09-30 close, rolling forward 12 months; historical average comparators share stated basis', 'currency': 'USD', 'measure': 'Consensus quarterly earnings/revenue growth and rolling forward P/E', 'period': 'Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30', 'scope': 'S&amp;P 500, provider FactSet; quarterly reporting population and vintage as described, not audited total future index income', 'unit': 'percent and ratio'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-fea4e3a549d932160d3cbdc73e9d6519da848ff1c0398b5711c6cd23283652a2"></a>
### 근거 · E\_DD\_IDX\_FACTSET\_Q2\_START\_REVISION

- 출처: [25](#opportunity-b142d987c19eaffec60c583a7c58e0e69322cb50f0a5e2cffd5632238b234b93); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: On a per-share basis, estimated earnings for the second quarter increased by 3.4% from March 31 to June 30. In a typical quarter, analysts usually lower earnings estimates during the quarter. Over the past five years (20 quarters), earnings expectations have fallen by 2.0% on average during the quarter. Over the past ten years, (40 quarters), earnings expectations have fallen by 2.7% on average during the quarter.
- 위치: Quarterly revision paragraph; 구절: REVISION; snapshot: 7af8663dd3de1ea741a7d8e9bcb7be9e05fd45256c69d769ee76193c6a072f88.
- 정의: \{'adjustment': 'Estimate revision during 2026-03-31 to 2026-06-30; historical observation, not current forward EPS', 'currency': 'USD', 'measure': 'Q2 consensus EPS revision', 'period': 'Q2 2026 earnings-season entry vintage 2026-07-02', 'scope': 'S&amp;P 500, provider FactSet; quarterly reporting population and vintage as described, not audited total future index income', 'unit': 'percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-d37c938f074b4fc26f75020ab141f4fddba305da44efe5573354b648e27db6d3"></a>
### 근거 · E\_DD\_IDX\_FACTSET\_Q2\_START\_EXPECTATION

- 출처: [25](#opportunity-b142d987c19eaffec60c583a7c58e0e69322cb50f0a5e2cffd5632238b234b93); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: As of today, the S&amp;P 500 is expected to report (year-over-year) earnings growth of 23.3%, compared to the estimated (year-over-year) earnings growth rate of 18.8% on March 31. If 23.3% is the actual growth rate for the quarter, it will mark the second consecutive quarter of earnings growth above 20% and the seventh consecutive quarter of double-digit earnings growth for the index. Ten of the eleven sectors are projected to report year-over-year growth, led by the Energy, Information Technology, and Materials sectors. On the other hand, the Health Care sector is the only sector predicted to report a year-over-year decline in earnings.
- 위치: Quarter-start estimate paragraph; 구절: EXPECTATION; snapshot: 7af8663dd3de1ea741a7d8e9bcb7be9e05fd45256c69d769ee76193c6a072f88.
- 정의: \{'adjustment': 'Historical Q2 entry estimate; not final actual and not new Q3 expectation', 'currency': 'USD', 'measure': 'Q2 year-over-year consensus earnings growth', 'period': 'Q2 2026 earnings-season entry vintage 2026-07-02', 'scope': 'S&amp;P 500, provider FactSet; quarterly reporting population and vintage as described, not audited total future index income', 'unit': 'percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-1dd5bf67509f2d871a487d06d46552df17b00f8c45d1b4f58c6201982656a486"></a>
### 근거 · E\_DD\_IDX\_FACTSET\_Q2\_START\_REVENUE

- 출처: [25](#opportunity-b142d987c19eaffec60c583a7c58e0e69322cb50f0a5e2cffd5632238b234b93); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: As of today, the S&amp;P 500 is expected to report (year-over-year) revenue growth of 12.2%, compared to the expectations for revenue growth of 9.5% on March 31. If 12.2% is the actual revenue growth rate for the quarter, it will mark the highest revenue growth rate reported by the index since Q2 2022 (13.9%). It will also mark the second consecutive quarter of double-digit revenue growth for the index. All eleven sectors are projected to report year-over-year growth in revenues, led by the Information Technology, Energy, and Communication Services sectors. For Q3 2026 and Q4 2026, analysts are calling for earnings growth rates of 26.8% and 24.4%. For CY 2026, analysts are predicting (year-over-year) earnings growth of 24.1%.
- 위치: Revenue and valuation paragraphs; 구절: REVENUE; snapshot: 7af8663dd3de1ea741a7d8e9bcb7be9e05fd45256c69d769ee76193c6a072f88.
- 정의: \{'adjustment': 'Historical estimate vintage; no current valuation comparison from this old price', 'currency': 'USD', 'measure': 'Q2 entry revenue expectation and forward P/E context', 'period': 'Q2 2026 earnings-season entry vintage 2026-07-02', 'scope': 'S&amp;P 500, provider FactSet; quarterly reporting population and vintage as described, not audited total future index income', 'unit': 'percent and ratio'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-1b207880153d5f87325c148eb3495faec24f75b06b137215ba587f77ecffcba9"></a>
### 근거 · E\_DD\_IDX\_FACTSET\_Q2\_QUALITY\_SURPRISE

- 출처: [24](#opportunity-db1be23edf9c5bfa5e78dd0d683ca56aa253b02a438aac1a1a3e9e8abc8e1c25); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: At the company level, the positive EPS surprise reported by Amazon.com ($5.75 vs. $1.82) was the largest contributor to the increase in the Q2 earnings growth rate for the S&amp;P 500 during the past week. This company alone accounted for 76% of the net dollar-level increase in earnings for the S&amp;P 500 over this period. However, it should be noted that EPS reported on a GAAP basis by Amazon.com was used for both the earnings surprise and the earnings growth rate calculations, as the majority of analysts contributing EPS estimates to FactSet for Amazon.com are providing EPS estimates on a GAAP basis for this company. Historically, Amazon.com has only reported EPS numbers on a GAAP basis.
- 위치: Amazon surprise and GAAP basis paragraph; 구절: SURPRISE; snapshot: e732fddc32803e8a360b43cc8a33febca4117e5ca7a649cb272a6b4dfa3e7f07.
- 정의: \{'adjustment': 'Actual reported GAAP EPS, consensus majority GAAP; 76% contribution is to ONE WEEK net earnings-estimate change, not total index profit or year return', 'currency': 'USD', 'measure': 'Amazon actual EPS vs provider EPS consensus and weekly contribution', 'period': 'Q2 2026 blended earnings-season intermediate vintage 2026-08-03', 'scope': 'S&amp;P 500, provider FactSet; quarterly reporting population and vintage as described, not audited total future index income', 'unit': 'USD per share and percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-06a6ec05511ee2c1aa3e8c4c9b89b0b2c283dca1d1f81df38eab0c06d3286206"></a>
### 근거 · E\_DD\_IDX\_FACTSET\_Q2\_QUALITY\_QUALITY

- 출처: [24](#opportunity-db1be23edf9c5bfa5e78dd0d683ca56aa253b02a438aac1a1a3e9e8abc8e1c25); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: As a result, Amazon.com is now the second-largest contributor to year-over-year earnings growth for the S&amp;P 500 for Q2 2026, trailing only Alphabet. Last week, Alphabet also reported an unusually large EPS surprise due to (GAAP) EPS that included a net gain of $98.0 billion primarily due to net unrealized gains on equity securities. For more details, please see this article: Alphabet Drives S&amp;P 500 Earnings Growth to Highest Level Since 2021 On Valuation Gains .
- 위치: Nonoperating gains and Alphabet comparison paragraph; 구절: QUALITY; snapshot: e732fddc32803e8a360b43cc8a33febca4117e5ca7a649cb272a6b4dfa3e7f07.
- 정의: \{'adjustment': 'Provider explanation of GAAP valuation gains; not proof all forward EPS includes those gains', 'currency': 'USD', 'measure': 'Investment valuation gains and reported earnings quality', 'period': 'Q2 2026 blended earnings-season intermediate vintage 2026-08-03', 'scope': 'S&amp;P 500, provider FactSet; quarterly reporting population and vintage as described, not audited total future index income', 'unit': 'USD billion and qualitative'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-508ac2c266322521639c27447547d79009d319c5a0d936e3cf3c9dfcdaffb57f"></a>
### 근거 · E\_DD\_IDX\_FACTSET\_Q2\_QUALITY\_EXCLUSIONS

- 출처: [24](#opportunity-db1be23edf9c5bfa5e78dd0d683ca56aa253b02a438aac1a1a3e9e8abc8e1c25); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: If Alphabet and Amazon.com were excluded, the blended earnings growth rate for the S&amp;P 500 for Q2 2026 would fall to 28.8% from 47.4%. Thus, even excluding Alphabet and Amazon.com, the S&amp;P 500 would still be reporting its 2 nd consecutive quarter of year-over-year earnings growth above 20% and 7 th consecutive quarter of double-digit earnings growth.
- 위치: Ex-company growth paragraph; 구절: EXCLUSIONS; snapshot: e732fddc32803e8a360b43cc8a33febca4117e5ca7a649cb272a6b4dfa3e7f07.
- 정의: \{'adjustment': 'Intermediate blended actual/estimated earnings season, exclusion changes population; 28.8 is not a clean operating-earnings estimate for all remaining companies', 'currency': 'USD', 'measure': 'Q2 blended S&amp;P earnings growth with and without two companies', 'period': 'Q2 2026 blended earnings-season intermediate vintage 2026-08-03', 'scope': 'S&amp;P 500, provider FactSet; quarterly reporting population and vintage as described, not audited total future index income', 'unit': 'percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-0bd50cc292ebae23a8190a2ed23e7b7fb81784d8b55ea4eedfd7e5960090c41e"></a>
### 근거 · E\_DD\_IDX\_FACTSET\_Q1\_SURPRISE

- 출처: [23](#opportunity-f42be2a4b1c038cc57d84221d8156e1e0c66dcb47bc57301f888b544d289f707); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Overall, 100% (7 out of 7) of the “Magnificent 7” companies reported a positive EPS surprise, compared to 84% for all S&amp;P 500 companies. In aggregate, earnings reported by the “Magnificent 7” companies exceeded estimates by 32.5%, compared to 16.6% for all S&amp;P 500 companies.
- 위치: Q1 surprise paragraph; 구절: SURPRISE; snapshot: 6e3cc957189184012501953c7f25bf447f78ef21e3fd8022cc8beccb47344546.
- 정의: \{'adjustment': 'Provider mixed company fiscal calendars and GAAP/non-GAAP convention; reporting population as of date; not forward realized total-return evidence', 'currency': 'USD', 'measure': 'Positive EPS surprise frequency and size', 'period': 'Q1 2026 reported cohort, provider vintage 2026-05-21', 'scope': 'S&amp;P 500, provider FactSet; quarterly reporting population and vintage as described, not audited total future index income', 'unit': 'percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-67f88f83d577b04201a022ddd7350653ee9b780e6d9ad0c2f45cb351655c0fee"></a>
### 근거 · E\_DD\_IDX\_FACTSET\_Q1\_ACTUAL

- 출처: [23](#opportunity-f42be2a4b1c038cc57d84221d8156e1e0c66dcb47bc57301f888b544d289f707); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: As a result, the “Magnificent 7” companies reported actual earnings growth of 63.2% for the first quarter, which is the highest earnings growth rate reported by these seven companies since Q2 2021 (89.2%). On the other hand, the blended earnings growth rate for the other 493 S&amp;P 500 companies for Q1 is 17.4%, which is also the highest earnings growth rate reported by this group of companies since Q4 2021 (32.3%). Overall, four of the “Magnificent 7” companies are among the top five contributors to earnings growth for the S&amp;P 500 for the first quarter: NVIDIA, Alphabet, Amazon.com, and Meta Platforms. Micron Technology is the only company outside of the “Magnificent 7” companies that is a top 5 contributor to earnings growth for the S&amp;P 500 for the quarter .
- 위치: Mag7 and other companies growth paragraph; 구절: ACTUAL; snapshot: 6e3cc957189184012501953c7f25bf447f78ef21e3fd8022cc8beccb47344546.
- 정의: \{'adjustment': 'Reported cohort growth; preceding article calls March31 forecast Q4 while main topic is Q1; ambiguous initial-quarter comparison is NOT used as Q1 initial forecast', 'currency': 'USD', 'measure': 'Q1 earnings growth and cohort comparison', 'period': 'Q1 2026 reported cohort, provider vintage 2026-05-21', 'scope': 'S&amp;P 500, provider FactSet; quarterly reporting population and vintage as described, not audited total future index income', 'unit': 'percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-b8600bd8deef250284422c71d9b794223ab6c97259f188d96a76daef5470da76"></a>
### 근거 · E\_DD\_IDX\_FACTSET\_Q1\_BASIS

- 출처: [23](#opportunity-f42be2a4b1c038cc57d84221d8156e1e0c66dcb47bc57301f888b544d289f707); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: It is important to note that EPS reported on a GAAP (generally accepted accounting principles) basis by Alphabet, Amazon.com, and Meta Platforms was used for both the earnings surprise and the earnings growth rate calculations, as the majority of analysts contributing EPS estimates to FactSet for these three companies are providing EPS estimates on a GAAP basis. Alphabet, Amazon.com, and Meta Platforms historically have only reported EPS numbers on a GAAP basis. It is interesting to note that all three companies highlighted items in their Q1 earnings releases that had a positive impact on GAAP earnings for the quarter. The (GAAP) EPS actual for Alphabet for Q1 2026 included a net gain of $37.7 billion primarily due to net unrealized gains on non-marketable equity securities. The (GAAP) EPS actual for Amazon.com for Q1 2026 included pre-tax gains of $16.8 billion included in non-operating income from investments in Anthropic. The (GAAP) EPS actual for Meta Platforms for Q1 2026 included an $8.03 billion income tax benefit. Meta Platforms also stated that EPS excluding the tax benefit for the first quarter would have been $3.13 lower.
- 위치: GAAP/non-GAAP basis explanation; 구절: BASIS; snapshot: 6e3cc957189184012501953c7f25bf447f78ef21e3fd8022cc8beccb47344546.
- 정의: \{'adjustment': 'Provider statements and accounting definitions; retain exactly as published with article label inconsistency disclosed', 'currency': 'USD', 'measure': 'Provider earnings convention and gain impact', 'period': 'Q1 2026 reported cohort, provider vintage 2026-05-21', 'scope': 'S&amp;P 500, provider FactSet; quarterly reporting population and vintage as described, not audited total future index income', 'unit': 'qualitative and percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-66774f8cbd44f9662bd86c5f6ac7f2c24026573590ba939cee9eb375ed014ec4"></a>
### 근거 · E\_DD\_IDX\_SPY\_VALUATION

- 출처: [28](#opportunity-b3b2aa1a939b74ccffa5a4e1d71c6658758535f8da8309d73896055f1d36e636); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Index Characteristics as of Oct 01 2026 Est. 3-5 Year EPS Growth 22.46% Number of Holdings 503 Price/Cash Flow 18.25 Price/Earnings 24.62 Price/Earnings Ratio FY1 20.43
- 위치: Index characteristics row; 구절: VALUATION; snapshot: 5bf56092840023270793395a5349275b3149e80836caa5c8e17e6119c4a50734.
- 정의: \{'adjustment': 'Trailing last12mo PE and FY1 weighted harmonic estimate PE are distinct; NOT FactSet rolling forward12mo PE', 'currency': 'USD', 'measure': 'Index trailing P/E and FY1 harmonic P/E', 'period': '2026-10-01', 'scope': 'S&amp;P 500 characteristics shown by State Street on SPY page', 'unit': 'ratio and percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-febef5b3512e3246d505fa88c75746433721577dc6e0c32f756954079be875a5"></a>
### 근거 · E\_DD\_IDX\_SPY\_HOLDINGS

- 출처: [28](#opportunity-b3b2aa1a939b74ccffa5a4e1d71c6658758535f8da8309d73896055f1d36e636); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Download All Holdings: Daily Index Top Holdings as of Oct 01 2026 Name Weight NVIDIA Corporation 8.46% Apple Inc. 7.30% Microsoft Corporation 5.77% Amazon.com Inc. 3.69% Alphabet Inc. Class A 3.01% Broadcom Inc. 2.48% Meta Platforms Inc Class A 2.42% Alphabet Inc. Class C 2.41% Micron Technology Inc. 1.88% Advanced Micro Devices Inc. 1.52%
- 위치: Index top10 security weights; 구절: HOLDINGS; snapshot: 5bf56092840023270793395a5349275b3149e80836caa5c8e17e6119c4a50734.
- 정의: \{'adjustment': 'Index weights, not SPY fund held weights, earnings weights or contribution to price return', 'currency': 'USD', 'measure': 'Index top-security market-cap weights', 'period': '2026-10-01', 'scope': 'S&amp;P 500 top10 securities; Alphabet dual classes are one issuer', 'unit': 'percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-4f0ceaa86703c53a9824524812212fb3d8338d8c7e3f8cfa0ee9ee2afb543122"></a>
### 근거 · E\_DD\_IDX\_SPY\_PE\_METHOD

- 출처: [28](#opportunity-b3b2aa1a939b74ccffa5a4e1d71c6658758535f8da8309d73896055f1d36e636); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Price/Earnings Ratio FY1 ﻿Price/Earnings Ratio FY1 The weighted harmonic average of current share price divided by the forecasted one year earnings per share for each security in the fund. Negative and positive outliers are included in the calculation. 20.43
- 위치: FY1 PE methodology; 구절: PE\_METHOD; snapshot: 5bf56092840023270793395a5349275b3149e80836caa5c8e17e6119c4a50734.
- 정의: \{'adjustment': 'Forecasted ONE-YEAR earnings per share; negative/positive outliers included; not rolling forward12mo aggregate index calculation', 'currency': 'USD', 'measure': 'FY1 weighted harmonic P/E method', 'period': '2026-10-01', 'scope': 'SPY underlying holdings methodology explained on product page', 'unit': 'ratio definition'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-40af50b29fc2a933baae21db3c7f5c042205c7469f5f1bc9eba75813b2d093f6"></a>
### 근거 · E\_DD\_MSFT\_Q4\_RESULTS

- 출처: [32](#opportunity-5d86d847122b5ad98b4fd5ae38197d19da3514d24e01b41fdf41ecdce072b925); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Revenue was $90.0 billion and increased 18% (up 17% in constant currency) · Operating income was $40.6 billion and increased 18% · Net income was $35.8 billion and increased 31% on a GAAP basis, and was $35.3 billion and increased 22% on a non-GAAP basis · Diluted earnings per share was $4.81 and increased 32% on a GAAP basis, and was $4.74 and increased 23% on a non-GAAP basis · Non-GAAP results exclude the impact from investments in OpenAI, explained in the Non-GAAP Definition section below Several discrete items impacted our financial results in the quarter when compared to our forward-looking guidance provided on April 29, 2026, resulting in a benefit of $0.27 on diluted earnings per share. These include a $3.2 billion gain from our investment in Anthropic and lower-than-expected expenses related to the Voluntary Retirement Program which were partially offset by severance expense and impairment charges in XBOX. When adjusting for these items, we exceeded expectations across revenue, operating income, and diluted earnings per share.
- 위치: Visible reported RESULTS excerpt; 구절: RESULTS; snapshot: 057377ceb5bd4486b99320eda019008534c5369adc71b9b02ba5b115866cb8d6.
- 정의: \{'adjustment': 'GAAP and OpenAI-adjusted non-GAAP distinct; adjustment does NOT remove all other investment gains or restructuring items', 'currency': 'USD', 'measure': 'Quarter revenue, operating income and reported EPS; one-off explanation', 'period': 'Quarter ended 2026-06-30, FY2026 Q4; year-over-year comparisons', 'scope': 'Microsoft consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD billion, USD/share and percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-aacd0086346ad1a5843f78ef2dd62d70220a9e0c5ffed11f991c8fa305e6f3d9"></a>
### 근거 · E\_DD\_MSFT\_Q4\_MONETIZATION

- 출처: [32](#opportunity-5d86d847122b5ad98b4fd5ae38197d19da3514d24e01b41fdf41ecdce072b925); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: This year, Azure revenue surpassed $100 billion for the first time, and Microsoft 365 Copilot reached over 30 million paid seats, reflecting the confidence customers are placing in us to power their AI transformation.” “We delivered a strong quarter to close out the fiscal year, highlighted by Microsoft Cloud revenue of $59.3 billion, up 27% year-over-year,” said Amy Hood, executive vice president and chief financial officer of Microsoft.
- 위치: Visible reported MONETIZATION excerpt; 구절: MONETIZATION; snapshot: 057377ceb5bd4486b99320eda019008534c5369adc71b9b02ba5b115866cb8d6.
- 정의: \{'adjustment': 'Management report; Azure/cloud includes non-AI; paid seats are not disclosed incremental AI profit or capital ROI', 'currency': 'USD', 'measure': 'Azure recognized annual revenue and paid Copilot seats', 'period': 'FY2026 ending2026-06-30; reported2026-07-29', 'scope': 'Microsoft consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD billion annual revenue and paid-seat count'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-3891ddc8357a02d301a5bf0c0a7be57aad8c3f6773a6555f0602e8bac848d2fd"></a>
### 근거 · E\_DD\_MSFT\_Q4\_CASH

- 출처: [32](#opportunity-5d86d847122b5ad98b4fd5ae38197d19da3514d24e01b41fdf41ecdce072b925); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Net cash from operations 55,441 42,647 182,935 136,162 Financing Repayments of debt, maturities of 90 days or less 0 0 0 (5,746) Repayments of debt 0 0 (3,000) (3,216) Common stock issued 520 548 2,009 2,056 Common stock repurchased (4,579) (4,546) (22,271) (18,420) Common stock cash dividends paid (6,758) (6,169) (26,445) (24,082) Other, net (962) (677) (2,839) (2,291) Net cash used in financing (11,779) (10,844) (52,546) (51,699) Investing Additions to property and equipment (35,802) (17,079) (115,948) (64,551)
- 위치: Visible reported CASH excerpt; 구절: CASH; snapshot: 057377ceb5bd4486b99320eda019008534c5369adc71b9b02ba5b115866cb8d6.
- 정의: \{'adjustment': 'Cash additions to PP&amp;E only; finance lease additions excluded; issuer cash-flow table, not total AI CAPEX', 'currency': 'USD', 'measure': 'Operating cash and additions to property and equipment', 'period': 'Three months2026/2025 and twelve months2026/2025 ended2026-06-30, columns in that order', 'scope': 'Microsoft consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD million'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-282faaeb22b446a4e13674231f58da7ed73e88f2c558d5c8a33952ca154755f2"></a>
### 근거 · E\_DD\_MSFT\_Q3\_RESULTS

- 출처: [31](#opportunity-b6d2a18034b99aa4454b4ab7f7e1a0541fad2c654914e71c80c468baea14173e); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Revenue was $82.9 billion and increased 18% (up 15% in constant currency) · Operating income was $38.4 billion and increased 20% (up 16% in constant currency) · Net income was $31.8 billion and increased 23% on a GAAP basis, and increased 20% (up 18% in constant currency) on a non-GAAP basis · Diluted earnings per share was $4.27 and increased 23% on a GAAP basis, and increased 21% (up 18% in constant currency) on a non-GAAP basis · Non-GAAP results exclude the impact from investments in OpenAI, explained in the Non-GAAP Definition section below “We are focused on delivering cloud and AI infrastructure and solutions that empower every business to eval-max their outcomes in the agentic computing era," said Satya Nadella, chairman and chief executive officer of Microsoft. “Our AI business surpassed an annual revenue run rate of $37 billion, up 123% year-over-year.”
- 위치: Visible reported RESULTS excerpt; 구절: RESULTS; snapshot: ad412080214feceb3e9386aefa1ec0e189ed9d39e8ab1e6ee64fa74c98eda4ce.
- 정의: \{'adjustment': 'GAAP reported versus OpenAI-adjusted nonGAAP; AI annual revenue run-rate is extrapolation, not completed annual AI revenue or AI ROI', 'currency': 'USD', 'measure': 'Revenue, operating income and management AI run-rate disclosure', 'period': 'Quarter ended2026-03-31 FY2026 Q3', 'scope': 'Microsoft consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD billion, USD/share and percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-a4ef4d503886c9613a87e27cb4ce4ece799d20d62a6ab9f84e425db74553f9f0"></a>
### 근거 · E\_DD\_MSFT\_Q3\_DEP

- 출처: [31](#opportunity-b6d2a18034b99aa4454b4ab7f7e1a0541fad2c654914e71c80c468baea14173e); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: CASH FLOWS STATEMENTS (In millions) (Unaudited) Three Months Ended March 31, Nine Months Ended March 31, 2026 2025 2026 2025 Operations Net income $31,778 $25,824 $97,983 $74,599 Adjustments to reconcile net income to net cash from operations: Depreciation, amortization, and other 10,167 7,734 27,512 20,116
- 위치: Visible reported DEP excerpt; 구절: DEP; snapshot: ad412080214feceb3e9386aefa1ec0e189ed9d39e8ab1e6ee64fa74c98eda4ce.
- 정의: \{'adjustment': 'Depreciation amortization AND other combined; cannot label pure server depreciation; unaudited', 'currency': 'USD', 'measure': 'Cash-flow depreciation/amortization/other adjustment', 'period': 'Three months2026/2025 and nine months2026/2025 ended2026-03-31, columns in that order', 'scope': 'Microsoft consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD million'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-0df20b81ac7dabce98733f55bf5447774d07c4cc09fe886d0544d958c623770a"></a>
### 근거 · E\_DD\_MSFT\_Q3\_CASH

- 출처: [31](#opportunity-b6d2a18034b99aa4454b4ab7f7e1a0541fad2c654914e71c80c468baea14173e); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Net cash from operations 46,679 37,044 127,494 93,515 Financing Repayments of debt, maturities of 90 days or less 0 0 0 (5,746) Repayments of debt 0 (2,250) (3,000) (3,216) Common stock issued 541 546 1,489 1,508 Common stock repurchased (4,627) (4,781) (17,692) (13,874) Common stock cash dividends paid (6,756) (6,169) (19,687) (17,913) Other, net (509) (382) (1,877) (1,614) Net cash used in financing (11,351) (13,036) (40,767) (40,855) Investing Additions to property and equipment (30,876) (16,745) (80,146) (47,472)
- 위치: Visible reported CASH excerpt; 구절: CASH; snapshot: ad412080214feceb3e9386aefa1ec0e189ed9d39e8ab1e6ee64fa74c98eda4ce.
- 정의: \{'adjustment': 'Cash PP&amp;E additions exclude finance-lease additions; cash free flow residual not audited incremental AI capital return', 'currency': 'USD', 'measure': 'Operating cash and cash PP&amp;E additions', 'period': 'Three months2026/2025 and nine months2026/2025 ended2026-03-31, columns in that order', 'scope': 'Microsoft consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD million'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-b1e3603e6a7013fc14534e3e8ede5925c59341b37516649540d0c9395ff39414"></a>
### 근거 · E\_DD\_AMZN\_Q2\_SALES

- 출처: [10](#opportunity-27acb40a74b281394210518738aeac45a15b737a8b8760ce3748621a468a7f5e); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Net sales information is as follows (in millions): Three Months Ended June 30, Six Months Ended June 30, 2025 2026 2025 2026 Net Sales: North America $ 100,068 $ 116,177 $ 192,955 $ 220,320 International 36,761 42,197 70,274 81,986 AWS 30,873 42,232 60,140 79,819 Consolidated $ 167,702 $ 200,606 $ 323,369 $ 382,125 Year-over-year Percentage Growth: North America 11 % 16 % 9 % 14 % International 16 15 10 17 AWS 17 37 17 33 Consolidated 13 20 11 18
- 위치: Visible reported SALES excerpt; 구절: SALES; snapshot: 7e8c6df634dc0f768926ef987dd17ccf9c8204826e01b38d636915e80e99c758.
- 정의: \{'adjustment': 'Reported sales; AWS includes non-AI cloud revenue; not pureAI revenue', 'currency': 'USD', 'measure': 'Segment and consolidated sales and growth', 'period': 'Three and six months ended2026/2025-06-30; year columns2025,2026 in each pair', 'scope': 'Amazon consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD million and percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-cbd103faa7480536d1e3615e8a546a5333e8947a770b6b8dfab33bc615da7621"></a>
### 근거 · E\_DD\_AMZN\_Q2\_FCF

- 출처: [10](#opportunity-27acb40a74b281394210518738aeac45a15b737a8b8760ce3748621a468a7f5e); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Free cash flow is cash flow from operations reduced by “Purchases of property and equipment, net of proceeds from sales and incentives.” The following is a reconciliation of free cash flow to the most comparable GAAP cash flow measure, “Net cash provided by (used in) operating activities,” for the trailing twelve months ended June 30, 2025 and 2026 (in millions): Twelve Months Ended June 30, 2025 2026 Net cash provided by (used in) operating activities $ 121,137 $ 161,403 Purchases of property and equipment, net of proceeds from sales and incentives (102,953) (169,007) Free cash flow $ 18,184 $ (7,604) Net cash provided by (used in) investing activities $ (123,569) $ (216,775) Net cash provided by (used in) financing activities $ (8,652) $ 75,160
- 위치: Visible reported FCF excerpt; 구절: FCF; snapshot: 7e8c6df634dc0f768926ef987dd17ccf9c8204826e01b38d636915e80e99c758.
- 정의: \{'adjustment': 'Company-defined nonGAAP OCF minus cash purchases net of proceeds/incentives; NOT quarterly FCF or all leasing economic cost', 'currency': 'USD', 'measure': 'Company free cashflow reconciliation', 'period': 'Trailing twelve months ended2025 and2026-06-30, columns in that order', 'scope': 'Amazon consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD million'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-296b989dfcc7122640fee61bea1996ecc9bb4e0ec975e87578515a1cb48824bf"></a>
### 근거 · E\_DD\_AMZN\_Q2\_GAINS

- 출처: [10](#opportunity-27acb40a74b281394210518738aeac45a15b737a8b8760ce3748621a468a7f5e); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: The upward adjustments relating to equity investments in private companies of $ 50.5 billion in Q2 2026 and $ 62.8 billion for the six months ended June 30, 2026 reflect observable changes in prices, primarily from our nonvoting preferred stock in Anthropic.
- 위치: Visible reported GAINS excerpt; 구절: GAINS; snapshot: 7e8c6df634dc0f768926ef987dd17ccf9c8204826e01b38d636915e80e99c758.
- 정의: \{'adjustment': 'Unrealized valuation adjustments to private investments; not operating income or operating cash paid by AI customers', 'currency': 'USD', 'measure': 'Private equity valuation gain explanation', 'period': 'Q2 and firsthalf2026 vs2025 as stated', 'scope': 'Amazon consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD billion'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-336adc4556282b6a1e0b10fb829a5ad9dbe3480fb79fa4cc46cee690244bf854"></a>
### 근거 · E\_DD\_AMZN\_Q2\_OPERATING\_OPERATING

- 출처: [11](#opportunity-1f6ff239f0d6a378d2b271e4b09a6c3bc936394f73f03739e7e3949aae4e35d4); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: AWS Net sales $ 30,873 $ 42,232 $ 60,140 $ 79,819 Operating expenses 20,713 25,611 38,433 49,037 Operating income $ 10,160 $ 16,621 $ 21,707 $ 30,782 Consolidated Net sales $ 167,702 $ 200,606 $ 323,369 $ 382,125 Operating expenses 148,531 173,145 285,793 330,812 Operating income 19,171 27,461 37,576 51,313 Total non-operating income 1,686 53,396 4,960 69,378 Provision for income taxes ( 2,678 ) ( 18,199 ) ( 7,231 ) ( 27,759 ) Equity-method investment activity, net of tax ( 15 ) ( 11 ) ( 14 ) ( 30 ) Net income $ 18,164 $ 62,647 $ 35,291 $ 92,902
- 위치: Visible reported OPERATING excerpt; 구절: OPERATING; snapshot: 01758ff10302234cb61120e5e967fbaa451f50f05bae45b4e90f78902efdf974.
- 정의: \{'adjustment': 'Segment operating income is distinct from GAAP total net income; AWS revenue not pureAI; unaudited', 'currency': 'USD', 'measure': 'AWS and consolidated operating economics', 'period': 'Three and six months ended2025/2026-06-30, columns2025,2026 in each pair', 'scope': 'Amazon consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD million'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-125d2475b86dd881d37f5ce1b1c2648b98cb16f4b87055eb486f9f7a83f5e9fe"></a>
### 근거 · E\_DD\_AMZN\_Q2\_OPERATING\_DEP

- 출처: [11](#opportunity-1f6ff239f0d6a378d2b271e4b09a6c3bc936394f73f03739e7e3949aae4e35d4); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Depreciation and amortization of property and equipment and capitalized content costs, operating lease assets, and other 15,227 19,988 29,489 38,933 58,562 75,200
- 위치: Visible reported DEP excerpt; 구절: DEP; snapshot: 01758ff10302234cb61120e5e967fbaa451f50f05bae45b4e90f78902efdf974.
- 정의: \{'adjustment': 'Includes capitalized content costs, operating lease assets and other; not pureAI server depreciation', 'currency': 'USD', 'measure': 'Broad depreciation and amortization adjustment', 'period': 'Three, six and twelve months ended2025/2026-06-30, six columns2025,2026 per pair', 'scope': 'Amazon consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD million'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-c4b67456569bad12fc3ca8cf5a72a8604a3c9aebdc21836e650926a413f2eab6"></a>
### 근거 · E\_DD\_AMZN\_Q2\_OPERATING\_CASH

- 출처: [11](#opportunity-1f6ff239f0d6a378d2b271e4b09a6c3bc936394f73f03739e7e3949aae4e35d4); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Net cash provided by (used in) operating activities 32,515 45,387 49,530 71,419 121,137 161,403 INVESTING ACTIVITIES: Purchases of property and equipment ( 32,183 ) ( 54,208 ) ( 57,202 ) ( 98,411 ) ( 107,656 ) ( 173,028 ) Proceeds from property and equipment sales and incentives 815 1,132 1,579 2,101 4,703 4,021
- 위치: Visible reported CASH excerpt; 구절: CASH; snapshot: 01758ff10302234cb61120e5e967fbaa451f50f05bae45b4e90f78902efdf974.
- 정의: \{'adjustment': 'Cash PP&amp;E excludes newfinanceleaseassets; gross cash purchase not same as TTM netPP&amp;E nonGAAP reconciliation', 'currency': 'USD', 'measure': 'Operating cash, gross cash PP&amp;E and sale/incentive proceeds', 'period': 'Three, six and twelve months ended2025/2026-06-30, six columns2025,2026 per pair', 'scope': 'Amazon consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD million'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-1321b216ca715ccdd1d526a2a0f83c2cf01d02c780146f3bc571920ffacda4e7"></a>
### 근거 · E\_DD\_META\_Q2\_RESULTS

- 출처: [30](#opportunity-dec2b5f8753df9ace8da1b71ef2308fd6634581c1ca303d15145f442b920cd73); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Second Quarter 2026 Financial Highlights Three Months Ended June 30, % Change In millions, except percentages and per share amounts 2026 2025 Revenue $ 60,801 $ 47,516 28 % Costs and expenses 42,026 27,075 55 % Income from operations $ 18,775 $ 20,441 (8) % Operating margin 31 % 43 % Provision for income taxes $ 2,908 $ 2,197 32 % Effective tax rate 16 % 11 % Net income $ 15,848 $ 18,337 (14) % Diluted earnings per share (EPS) $ 6.18 $ 7.14 (13) %
- 위치: Visible reported RESULTS excerpt; 구절: RESULTS; snapshot: 1794cb1b74b11b8b343855fd0c1e693b335ce60019a3121377b88ee464f4cc4c.
- 정의: \{'adjustment': 'GAAP unaudited; legal/restructuring impact separate from AI spend; past netincome includes tax effects', 'currency': 'USD', 'measure': 'Revenue and operating profitability', 'period': 'Three and six months ended2025/2026-06-30, columns as shown', 'scope': 'Meta Platforms consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD million and percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-037e439c2fb443f15ca126faaf69866dc85ac6d8ea840154f009267914ce6a5f"></a>
### 근거 · E\_DD\_META\_Q2\_CAPEX\_CASH

- 출처: [30](#opportunity-dec2b5f8753df9ace8da1b71ef2308fd6634581c1ca303d15145f442b920cd73); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Capital expenditures – Capital expenditures, including principal payments on finance leases, were $31.08 billion. Capital return program – Dividend and dividend equivalent payments were $1.35 billion. Cash, cash equivalents, and marketable securities – Cash, cash equivalents, and marketable securities were $90.26 billion as of June 30, 2026. Long-term debt – Long-term debt was $83.66 billion as of June 30, 2026. Cash flow – Cash flow from operating activities was $31.86 billion, and free cash flow was $784 million. (1)
- 위치: Visible reported CAPEX\_CASH excerpt; 구절: CAPEX\_CASH; snapshot: 1794cb1b74b11b8b343855fd0c1e693b335ce60019a3121377b88ee464f4cc4c.
- 정의: \{'adjustment': 'CAPEX includes finance-lease principal; company-defined FCF, not same CAPEX basis as Microsoft/Alphabet/Amazon', 'currency': 'USD', 'measure': 'Quarter cash investment, operating cash and free cash flow', 'period': 'Quarter ended2026-06-30', 'scope': 'Meta Platforms consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD billion and USD million'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-f847d37e3d8533aecb2200784f6fcc6b6e9b0b3b009df658340c94674f4e8597"></a>
### 근거 · E\_DD\_META\_Q2\_GUIDANCE

- 출처: [30](#opportunity-dec2b5f8753df9ace8da1b71ef2308fd6634581c1ca303d15145f442b920cd73); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: We expect third quarter 2026 total revenue to be in the range of $61-64 billion. Our guidance assumes foreign currency is an approximately 1% headwind to year-over-year total revenue growth, based on current exchange rates. We are raising the lower-end of our expense outlook to incorporate the $2.4 billion charges related to legal proceedings recognized in the second quarter. We now expect full year 2026 total expenses to be in the range of $165-169 billion. We continue to expect to deliver operating income this year that is above 2025 operating income. We anticipate 2026 capital expenditures, including principal payments on finance leases, to be in the range of $130-145 billion, narrowed from our prior outlook of $125-145 billion.
- 위치: Visible reported GUIDANCE excerpt; 구절: GUIDANCE; snapshot: 1794cb1b74b11b8b343855fd0c1e693b335ce60019a3121377b88ee464f4cc4c.
- 정의: \{'adjustment': 'Management future estimates not actual spending; legal charges noted; full-yearoperatingincomeguidance not proofincrementalAI ROI', 'currency': 'USD', 'measure': 'Expense and CAPEX guidance change', 'period': 'Full-year2026 guidance reported2026-07-29; prior guidance range as disclosed', 'scope': 'Meta Platforms consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD billion ranges and percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-ddb0008650e36126449fe659922968691cf4230a9628bf0fefb8e6ed96d4021a"></a>
### 근거 · E\_DD\_META\_Q1\_RESULTS

- 출처: [29](#opportunity-6f2f4999b142113ec649db6b5c170f96452c4f34f85452796901889c9bfdd419); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: First Quarter 2026 Financial Highlights Three Months Ended March 31, % Change In millions, except percentages and per share amounts 2026 2025 Revenue $ 56,311 $ 42,314 33 % Costs and expenses 33,439 24,759 35 % Income from operations $ 22,872 $ 17,555 30 % Operating margin 41 % 41 % Provision (benefit) for income taxes (1) $ (5,021) $ 1,738 NM Effective tax rate (1) (23) % 9 % Net income $ 26,773 $ 16,644 61 % Diluted earnings per share (EPS) (1) $ 10.44 $ 6.43 62 % \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
- 위치: Visible reported RESULTS excerpt; 구절: RESULTS; snapshot: 1e879bc36e21c27f13d72748f5c24edf8f15d47327438d438117fbf4c3815494.
- 정의: \{'adjustment': 'Reported GAAP includes large income tax benefit; not pure ongoing business earnings', 'currency': 'USD', 'measure': 'Revenue and operating profitability', 'period': 'Quarter ended2026/2025-03-31', 'scope': 'Meta Platforms consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD million and percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-ceb2746fc488290c12cb776edfbfd7301b41e8b3b2588f645715ac5e5e06a629"></a>
### 근거 · E\_DD\_META\_Q1\_CAPEX\_CASH

- 출처: [29](#opportunity-6f2f4999b142113ec649db6b5c170f96452c4f34f85452796901889c9bfdd419); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Capital expenditures – Capital expenditures, including principal payments on finance leases, were $19.84 billion. Capital return program – Dividend and dividend equivalent payments were $1.35 billion. Cash, cash equivalents, and marketable securities – Cash, cash equivalents, and marketable securities were $81.18 billion as of March 31, 2026. Cash flow – Cash flow from operating activities was $32.23 billion, and free cash flow was $12.39 billion. (1)
- 위치: Visible reported CAPEX\_CASH excerpt; 구절: CAPEX\_CASH; snapshot: 1e879bc36e21c27f13d72748f5c24edf8f15d47327438d438117fbf4c3815494.
- 정의: \{'adjustment': 'CAPEX includes finance-leaseprincipal, reportedcompanynonGAAP FCF', 'currency': 'USD', 'measure': 'Quarter cash investment operating cash and FCF', 'period': 'Quarter ended2026-03-31', 'scope': 'Meta Platforms consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD billion'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-48bf2ab886fc8eed51a714f16d2bd9c345ffe2bcb1247c50ad2fb08fa223b8dd"></a>
### 근거 · E\_DD\_META\_Q1\_TAX

- 출처: [29](#opportunity-6f2f4999b142113ec649db6b5c170f96452c4f34f85452796901889c9bfdd419); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Includes an $8.03 billion income tax benefit recognized in the first quarter of 2026, which partially offsets the $15.93 billion non-cash tax charge recorded in the third quarter of 2025 upon enactment of the One Big Beautiful Bill Act. This benefit is the result of U.S. Treasury Notice 2026-7, which addressed the Corporate Alternative Minimum Tax treatment of previously capitalized U.S. research and development costs. Excluding this tax benefit, our effective tax rate would have been 37 percentage points higher and our diluted earnings per share (EPS) would have been $3.13 lower.
- 위치: Visible reported TAX excerpt; 구절: TAX; snapshot: 1e879bc36e21c27f13d72748f5c24edf8f15d47327438d438117fbf4c3815494.
- 정의: \{'adjustment': 'One-off tax benefit not operating cashflow or recurring EPS; source statement only', 'currency': 'USD', 'measure': 'Income tax benefit explanation', 'period': 'Quarter ended2026-03-31', 'scope': 'Meta Platforms consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD billion and USD/share'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d"></a>
### 근거 · E\_DD\_GOOGL\_Q2\_RESULTS

- 출처: [22](#opportunity-b6234296e1544fd47c7e27117adb003ac89d8fa89bcb5ce18e129ed9b0cff996); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Google Cloud saw a meaningful acceleration in growth as revenues increased 82% to $24.8 billion, led by an increase in Google Cloud Platform (GCP) across enterprise AI Solutions and enterprise AI Infrastructure, as well as core GCP services. • Consolidated Alphabet operating income increased 30% and operating margin expanded by 2 percentage points to 34%. • Other income reflected a net gain of $98.0 billion, primarily the result of net unrealized gains on our equity securities. • Net income available to common stockholders increased 298% and EPS increased 294% to $9.11.
- 위치: Visible reported RESULTS excerpt; 구절: RESULTS; snapshot: 28b743b35bda051a490972d025f93c8e3ade50acdd970d81047a3d9ad22457a2.
- 정의: \{'adjustment': 'Cloud revenue includes coreGCP nonAI; GAAP netincome includes unrealizedequitygain; management statements not AI incrementalROI', 'currency': 'USD', 'measure': 'Cloud growth, operating growth and valuation gains', 'period': 'Quarter ended2026-06-30', 'scope': 'Alphabet consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD billion, USD/share and percent'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-45223e78f81c1f85bea9f34da572b462652182a4214e7f422b0c50ad66e14a60"></a>
### 근거 · E\_DD\_GOOGL\_Q2\_FCF

- 출처: [22](#opportunity-b6234296e1544fd47c7e27117adb003ac89d8fa89bcb5ce18e129ed9b0cff996); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Quarter Ended TTM Q3 2025 Q4 2025 Q1 2026 Q2 2026 Q2 2026 Net cash provided by operating activities $ 48,414 $ 52,402 $ 45,790 $ 39,069 $ 185,675 Less: purchases of property and equipment (23,953) (27,851) (35,674) (44,924) (132,402) Free cash flow $ 24,461 $ 24,551 $ 10,116 $ (5,855) $ 53,273 Free cash flow: We define free cash flow as net cash provided by operating activities less capital expenditures. TTM free cash flow: We define trailing twelve months free cash flow as net cash provided by operating activities less capital expenditures for the most recent twelve consecutive months.
- 위치: Visible reported FCF excerpt; 구절: FCF; snapshot: 28b743b35bda051a490972d025f93c8e3ade50acdd970d81047a3d9ad22457a2.
- 정의: \{'adjustment': 'Company definedOCF minuscashCAPEX, quartervsTTM keptseparate; historyasreportedcurrentrelease not firstannouncement vintage', 'currency': 'USD', 'measure': 'Quarter and TTM FCF reconciliation', 'period': 'ColumnsQ3 2025,Q4 2025,Q1 2026,Q2 2026,TTM endedQ2 2026', 'scope': 'Alphabet consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD million'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-072a77d83aa661d8dc45c55d58f4920c78171325f6bfa81e6bad99ce1475713a"></a>
### 근거 · E\_DD\_GOOGL\_Q2\_DEP

- 출처: [22](#opportunity-b6234296e1544fd47c7e27117adb003ac89d8fa89bcb5ce18e129ed9b0cff996); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Operating activities Net income $ 28,196 $ 112,193 $ 62,736 $ 174,771 Adjustments: Depreciation of property and equipment 4,998 7,104 9,485 13,586
- 위치: Visible reported DEP excerpt; 구절: DEP; snapshot: 28b743b35bda051a490972d025f93c8e3ade50acdd970d81047a3d9ad22457a2.
- 정의: \{'adjustment': 'Unauditedcashflows; not only AIservers; company reportedexpenses', 'currency': 'USD', 'measure': 'Depreciation of property and equipment', 'period': 'Three months2025/2026 and six months2025/2026 endedJune30, columns inthatorder', 'scope': 'Alphabet consolidated/identified segment; company only, not index or pure AI cohort', 'unit': 'USD million'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-57e4dbbc924f0ec234a0e9ffec018db0a3fc8d13b4d1686a9aed0d8fb62a112d"></a>
### 근거 · E\_DD\_NVDA\_Q2\_ECONOMICS

- 출처: [33](#opportunity-b3cd92a892c22fd2f10be7198b002951e7e2c3cab60d1f2b10bcafdf8123a444); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Three Months Ended Quarter-over-Quarter Change Year-over-Year Change Jul 26, 2026 Apr 26, 2026 Jul 27, 2025 ($ in millions, except per share data) Revenue $ 96,221 $ 81,615 $ 46,743 18 % 106 % Gross margin 75.0 % 74.9 % 72.4 % 0.1 pts 2.6 pts Operating expenses $ 8,408 $ 7,621 $ 5,413 10 % 55 % Operating income $ 63,734 $ 53,536 $ 28,440 19 % 124 % Net income $ 59,688 $ 58,321 $ 26,422 2 % 126 % Net income per diluted share $ 2.46 $ 2.39 $ 1.08 3 % 128 %
- 위치: Quarter table; 구절: ECONOMICS; snapshot: d6e3879ec2d94e115817629de4883a79bd49b185fdf7400218eb99da21b12326.
- 정의: \{'adjustment': 'Reported GAAP; quarter-over-quarter and year-over-year columns distinct', 'currency': 'USD', 'measure': 'Quarter actual revenue/gross margin/operating income/net income/EPS', 'period': 'FY2027 Q2 Jul26, FY2027 Q1 Apr26, FY2026 Q2 Jul27, columns inthatorder', 'scope': 'NVIDIA consolidated, not the S&amp;P500 or AI customers', 'unit': 'USD million, percent, USD/share'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-a7351bc446441eca1ad10a93e679bd66981710311f5e4d56ff501bbce4717cd7"></a>
### 근거 · E\_DD\_NVDA\_Q2\_CASH

- 출처: [33](#opportunity-b3cd92a892c22fd2f10be7198b002951e7e2c3cab60d1f2b10bcafdf8123a444); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Cash flows from operating activities: Net income $ 118,010 $ 45,197 Adjustments to reconcile net income to net cash provided by operating activities: Stock-based compensation expense 3,954 3,099 Depreciation and amortization 2,124 1,280 Deferred income taxes 982 ( 2,160 ) Gains from equity securities, net ( 23,707 ) ( 2,073 ) Other 222 ( 196 ) Changes in operating assets and liabilities, net of acquisitions: Accounts receivable ( 24,590 ) ( 4,743 ) Inventories ( 10,204 ) ( 4,880 ) Prepaid expenses and other assets ( 6,480 ) 946 Accounts payable 4,125 2,255 Accrued and other current liabilities 8,015 3,075 Other long-term liabilities 1,970 979 Net cash provided by operating activities 74,421 42,779
- 위치: Sixmonth cashflow table; 구절: CASH; snapshot: d6e3879ec2d94e115817629de4883a79bd49b185fdf7400218eb99da21b12326.
- 정의: \{'adjustment': 'OCF includes workingcapital; investmentgains deducted from accountingincome; not quarter FCF or customer ROI', 'currency': 'USD', 'measure': 'Half-year income reconciliation to operating cashflow', 'period': 'Six months ended2026-07-26 vs2025-07-27, columns inthatorder', 'scope': 'NVIDIA consolidated', 'unit': 'USD million'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-494a017b5dc8879f93569451f08c625e064ee6e04dcad1e44aa2a15660e78563"></a>
### 근거 · E\_DD\_NVDA\_Q2\_CREDIT

- 출처: [33](#opportunity-b3cd92a892c22fd2f10be7198b002951e7e2c3cab60d1f2b10bcafdf8123a444); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Five direct customers accounted for 22 %, 14 %, 13 %, 11 %, and 10 % of our accounts receivable balance as of July 26, 2026. Three direct customers accounted for 25 %, 18 %, and 13 % of our accounts receivable balance as of January 25, 2026. Payment from customers is generally due shortly after delivery of our products. In certain cases, for investment-grade customer purchases, we have and may in the future provide longer payment terms ranging from 90 days up to one year to assist customers with large data center builds depending on size.
- 위치: Receivables concentration and paymentterms; 구절: CREDIT; snapshot: d6e3879ec2d94e115817629de4883a79bd49b185fdf7400218eb99da21b12326.
- 정의: \{'adjustment': 'Shares of RECEIVABLES not revenue or default rates; longer terms not proof delinquency', 'currency': 'USD', 'measure': 'Direct customer receivables shares and paymentterms', 'period': 'Balance2026-07-26 vs2026-01-25; terms as reported', 'scope': 'NVIDIA unnamed direct customers; no identities inferred', 'unit': 'percent and days'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-b2402907f0619860113f13a2dab0f7a160a76a75f7d29a101f8933b301181ade"></a>
### 근거 · E\_DD\_TR\_DATES

- 출처: [34](#opportunity-7fcf16b415162ceb577bbc6a78c56d7f8fd2af2f89d0242f91180e4c489053ab); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Release date: October 2, 2026 Selected Interest Rates Yields in percent per annum Instruments 2026 Sep 25 2026 Sep 28 2026 Sep 29 2026 Sep 30 2026 Oct 1
- 위치: H15 DATES visible table/text; 구절: DATES; snapshot: e213205d355b63a4d58107a4f8f02c071ec2712c970f56bc15001c4bb3c938f2.
- 정의: \{'adjustment': 'nominal constant-maturity Treasury yield quoted on investment basis; annual percent; not policy rate, discount-basis bill rate, zero-coupon spot yield, product execution YTM or realized return', 'currency': 'USD', 'measure': 'H15\_date\_column\_order', 'period': '2026-10-01 latest displayed observation, released 2026-10-02; full columns 2026-09-25, 2026-09-28, 2026-09-29, 2026-09-30, 2026-10-01', 'scope': 'H15 current release latest observation identity', 'unit': 'dates'\}; 시점 적합성: fresh.
- 한계: 최종 열은 2026-10-01이며 앞의 네 열과 섞지 않는다. CMT는 시장곡선 보간의 벤치마크다. 개별 채권·ETF의 실행 수익률이나 원화 수익률은 아니다. 같은 원천인 Fed CSV와 독립 증거로 세지 않는다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-e21239fba7cb4fb001969b6e9782c0f26bcecfc702dd353ed82368fc1b4dc848"></a>
### 근거 · E\_DD\_TR\_CURVE

- 출처: [34](#opportunity-7fcf16b415162ceb577bbc6a78c56d7f8fd2af2f89d0242f91180e4c489053ab); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Treasury constant maturities Nominal 9 1-month 4.04 4.04 4.04 4.02 4.06 3-month 4.24 4.28 4.25 4.20 4.17 6-month 4.33 4.41 4.36 4.33 4.27 1-year 4.50 4.59 4.58 4.54 4.44 2-year 4.81 4.92 4.89 4.88 4.78 3-year 4.94 5.01 4.98 5.00 4.91 5-year 4.98 5.06 5.06 5.09 5.01 7-year 5.06 5.15 5.16 5.19 5.12 10-year 5.17 5.24 5.26 5.29 5.24 20-year 5.54 5.60 5.64 5.68 5.64 30-year 5.49 5.56 5.59 5.64 5.61
- 위치: H15 CURVE visible table/text; 구절: CURVE; snapshot: e213205d355b63a4d58107a4f8f02c071ec2712c970f56bc15001c4bb3c938f2.
- 정의: \{'adjustment': 'nominal constant-maturity Treasury yield quoted on investment basis; annual percent; not policy rate, discount-basis bill rate, zero-coupon spot yield, product execution YTM or realized return', 'currency': 'USD', 'measure': 'Treasury\_nominal\_constant\_maturity\_curve', 'period': '2026-10-01 latest displayed observation, released 2026-10-02; full columns 2026-09-25, 2026-09-28, 2026-09-29, 2026-09-30, 2026-10-01', 'scope': 'U.S. Treasury nominal constant-maturity yield curve, every tenor same displayed observation date', 'unit': 'annual\_percent'\}; 시점 적합성: fresh.
- 한계: 최종 열은 2026-10-01이며 앞의 네 열과 섞지 않는다. CMT는 시장곡선 보간의 벤치마크다. 개별 채권·ETF의 실행 수익률이나 원화 수익률은 아니다. 같은 원천인 Fed CSV와 독립 증거로 세지 않는다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-1019cce484a7a7739959a8e4ba2d4dfdf4abfb0a3ebce5d4dbf29bb7455184bd"></a>
### 근거 · E\_DD\_TR\_METHOD

- 출처: [34](#opportunity-7fcf16b415162ceb577bbc6a78c56d7f8fd2af2f89d0242f91180e4c489053ab); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Yields on Treasury nominal securities at “constant maturity” are interpolated by the U.S. Treasury from the daily yield curve for non-inflation-indexed Treasury securities. This curve, which relates the yield on a security to its time to maturity, is based on the closing market bid yields on actively traded Treasury securities in the over-the-counter market. These market yields are calculated from composites of quotations obtained by the Federal Reserve Bank of New York. The constant maturity yield values are read from the yield curve at fixed maturities, currently 1, 3, and 6 months and 1, 2, 3, 5, 7, 10, 20, and 30 years. This method provides a yield for a 10-year maturity, for example, even if no outstanding security has exactly 10 years remaining to maturity.
- 위치: H15 METHOD visible table/text; 구절: METHOD; snapshot: e213205d355b63a4d58107a4f8f02c071ec2712c970f56bc15001c4bb3c938f2.
- 정의: \{'adjustment': 'nominal constant-maturity Treasury yield quoted on investment basis; annual percent; not policy rate, discount-basis bill rate, zero-coupon spot yield, product execution YTM or realized return', 'currency': 'USD', 'measure': 'Treasury\_constant\_maturity\_interpolation', 'period': '2026-10-01 latest displayed observation, released 2026-10-02; full columns 2026-09-25, 2026-09-28, 2026-09-29, 2026-09-30, 2026-10-01', 'scope': 'Interpolation of closing bid yield curve; Treasury nominal securities, not a tradable single-security quote', 'unit': 'source\_method\_definition'\}; 시점 적합성: fresh.
- 한계: 최종 열은 2026-10-01이며 앞의 네 열과 섞지 않는다. CMT는 시장곡선 보간의 벤치마크다. 개별 채권·ETF의 실행 수익률이나 원화 수익률은 아니다. 같은 원천인 Fed CSV와 독립 증거로 세지 않는다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-6b6a40179761574ea58c576d9d94acfe4d8b4691566cbfd4050555e2afff7a65"></a>
### 근거 · E\_DD\_COM\_GOOGLE\_LOSS\_NARRATIVE

- 출처: [14](#opportunity-a5dfa40b4a59dfc97cf95af9ee3f119d1f7994b3a544822f20d35e7d8c19e668); 분류: observed\_narrative; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: &gt; Google makes AI profits, its in their breakdowns. What "AI profits" exactly. Their capex is through the roof. What they're actually earning is in cloud , their own AI is lossy for sure. Who is paying for Gemini? Not many people.
- 위치: /text; 구절: NARRATIVE; snapshot: 3a267eb7fb8d1df1a6af5040486e209d5e2d5222bced187e6137d1d5e1251ad2.
- 정의: \{'adjustment': 'Normalized visible original comment; HTML tags/entities normalized by existing source parser; translation and factual verification separate', 'currency': None, 'measure': 'Observed public comment, content unverified', 'period': '2026-10-02T10:35:05+00:00', 'scope': 'Purpose-selected English HN comment, not market consensus', 'unit': 'text'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-ba665102c6a778348b729a3ad532ed9cdf61c08cff9813251a52dc780d6d990b"></a>
### 근거 · E\_DD\_COM\_CAPEX\_NEVER\_NARRATIVE

- 출처: [13](#opportunity-40322cf942ac59538d864cbfec67416b9a5a959d510f2fd5031ef5b628a6213e); 분류: observed\_narrative; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: You're focusing on the wrong part in the example. Enron's valuation was driven by irrational exuberance and market sentiment. In the case of Enron, the numbers were a fraud. In the case of AI, the numbers show utter carnage but everyone is trading on hope like it's musical chairs. There simply will never be enough revenue to justify to date and forward looking capex. At some point, investors are going to figure out they've been sold a b
- 위치: /text; 구절: NARRATIVE; snapshot: ae7eac737b08b40e76c572af6b465fc8c7e77a8b006b69b0dff1f8cf48448e64.
- 정의: \{'adjustment': 'Normalized visible original comment; HTML tags/entities normalized by existing source parser; translation and factual verification separate', 'currency': None, 'measure': 'Observed public comment, content unverified', 'period': '2026-10-01T19:49:49+00:00', 'scope': 'Purpose-selected English HN comment, not market consensus', 'unit': 'text'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-4b96c2e5184c49439ccdb6cc8fa3ed19ba8b3f08af2b2e1cb2a21f51fda4891e"></a>
### 근거 · E\_DD\_COM\_REAL\_PROFITS\_NARRATIVE

- 출처: [17](#opportunity-a5cf44fbd1b23ce53aa32fac27165f1416392d0a723c4e26fdb47bd5276c9cc3); 분류: observed\_narrative; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: There are signs that we are, and are not, in an AI bubble. Compared to the dotcom boom, firms are well positioned in terms of capital - they have revenue and profits. However, there's still the absurd speculative valuations, risk, and high expenditure (on said data centres). Also, Andrew Bailey from the Bank of England
- 위치: /text; 구절: NARRATIVE; snapshot: 6e3929ac00883c2f627f6d6473d4b82c3ddffda713357abf64e51e47abbb3245.
- 정의: \{'adjustment': 'Normalized visible original comment; HTML tags/entities normalized by existing source parser; translation and factual verification separate', 'currency': None, 'measure': 'Observed public comment, content unverified', 'period': '2026-10-02T15:15:23+00:00', 'scope': 'Purpose-selected English HN comment, not market consensus', 'unit': 'text'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-246f6943b38c9aa1d3066432a29662152c1dc26947ce6731c70d947887a8e26e"></a>
### 근거 · E\_DD\_COM\_PRICED\_SPENDING\_NARRATIVE

- 출처: [16](#opportunity-19711753c6027dc9a92028cc41b90739805178d5114c27bb95990362a2071294); 분류: observed\_narrative; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: because entire economy is booming due to AI spending which priced in for more spending and revenue in the future.
- 위치: /text; 구절: NARRATIVE; snapshot: 4c396b72de0180ae2df387536d8e21746c5bb5b5ae451c485c1e64bfd21f67fe.
- 정의: \{'adjustment': 'Normalized visible original comment; HTML tags/entities normalized by existing source parser; translation and factual verification separate', 'currency': None, 'measure': 'Observed public comment, content unverified', 'period': '2026-10-02T10:27:40+00:00', 'scope': 'Purpose-selected English HN comment, not market consensus', 'unit': 'text'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-2d74b8fef1c17f4dae7e0cacb17184aa1fcc887a906f0ed7d98cf806d31caf47"></a>
### 근거 · E\_DD\_COM\_TREASURY\_RISK\_NARRATIVE

- 출처: [20](#opportunity-1d972995e49eaaf31eff3ce3b50ce395710a6010685e0fa7fda83d51322ef6a7); 분류: observed\_narrative; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: Your point about dollar exposure is true, we just have limited insight into foreign private ownership, as the article points out. If nations are using these vehicles to conceal their dollar exposure (or for some other purpose that results in the same effect), then we will have trouble understanding the functioning of the global economy and the risks present in the system. That seems important. Also, equities and treasuries are not equivalent. If foreign holdings are moving to equities over treasuries, the added risk will be a serious problem in a crisis. It could also be a sign that some nations are being “e
- 위치: /text; 구절: NARRATIVE; snapshot: 12be92dcd4e90a962a5f6cf6d101d42103f71ca2fbc7dfb66aff4b101ee93691.
- 정의: \{'adjustment': 'Normalized visible original comment; HTML tags/entities normalized by existing source parser; translation and factual verification separate', 'currency': None, 'measure': 'Observed public comment, content unverified', 'period': '2026-09-18T17:23:53+00:00', 'scope': 'Purpose-selected English HN comment, not market consensus', 'unit': 'text'\}; 시점 적합성: fresh.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-d6f018d7b5412d136438b882d73c1e785547ad6f1ee998b64a05594edd67139c"></a>
### 근거 · E\_DD\_IDX\_NDX\_SCOPE\_SCOPE

- 출처: [27](#opportunity-fd6218f0b6833d3660101c1f8b43091161061237229a4d3c3e2167e0bdf2110d); 분류: external\_fact; 원문 확인: supported\_within\_scope; 해석 검토: pending.
- 원문: The Nasdaq-100 Index® includes 100 of the largest domestic and international non-financial companies listed on The Nasdaq Stock Market based on market capitalization. The Index reflects companies across major industry groups including computer hardware and software, telecommunications, retail/wholesale trade and biotechnology. It does not contain securities of financial companies including investment companies.
- 위치: Index description; 구절: SCOPE; snapshot: 8acb44251fa8ecdda53f0a0fecff488083a3ded8165f2a878ec8a3d7782e3518.
- 정의: \{'adjustment': 'Provider descriptive scope; membership count/weights/valuation as-of not established', 'currency': 'USD', 'measure': 'Index inclusion and sector scope', 'period': 'Publication and methodology-effective date unknown', 'scope': 'Nasdaq100 includes largest listed nonfinancial companies; not S&amp;P500 or completeUSmarket', 'unit': 'index\_definition'\}; 시점 적합성: unknown.
- 한계: 발표된 구절의 존재 확인이며 경제적 해석·지속성·투자수익의 확인과 다르다. 자료 정의·기간·범위와 source의 정책 및 판본 한계를 따른다.
- 한계: 구절 존재 또는 명시적 원문 수치만 확인한다. 경제적 일반 주장·인과·미래 투자성과를 자동 검증한 것이 아니다.

<a id="opportunity-95bedb1a82c5878057b021e4a5c4f230fef156a43501a4a876ebc05790043af8"></a>
### 근거 · OBS\_017458714f6243fb8b2424d5e72a290376fdc617f3a1d7b1565c487a6673e884

- 출처: [1](#opportunity-c436613f5d09e28fd85e2bc46b272d6421f81f0e3f63f160bcbb83e83676c4ce); 분류: observed\_fact; 원문 확인: supported\_within\_scope; 해석 검토: reviewed.
- 원문: 미국 headline CPI-U 원지수 (NSA); observation=2026-08-01; value=334.980 index
- 위치: /Results/series/0/data/0/value; year=2026, period=M08; 구절: OBS\_017458714f6243fb8b2424d5e72a290376fdc617f3a1d7b1565c487a6673e884; snapshot: 5f659b87469da318e1d476987fb1d686bdf23f34cae1194297a4996299564a05.
- 정의: \{'measure': 'US\_CPI\_U\_HEADLINE\_NSA', 'unit': 'index', 'period': 'monthly', 'currency': None, 'adjustment': 'not\_seasonally\_adjusted', 'scope': 'All items CPI-U, U.S. city average, 1982–84=100; not seasonally adjusted. Monthly label is the reference month, not the release date.'\}; 시점 적합성: fresh.
- 한계: 원관측의 수치 확인이며 수익률·인과·투자 매력의 확인이 아니다.
- 한계: 전체 개정 이력은 미확인이다.

<a id="opportunity-5ea22e484d99243f2bb8980ada756a7d00bce7b1b4889faa97d70aea979fa23f"></a>
### 근거 · OBS\_07818a1242169b952349e54e0651560e013d9c511c3728a9955db7bd85184067

- 출처: [84](#opportunity-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700); 분류: observed\_fact; 원문 확인: supported\_within\_scope; 해석 검토: reviewed.
- 원문: 미국 국채 10년 명목 시장금리; observation=2026-10-01; value=5.24 percent
- 위치: CSV row 16899, column RIFLGFCY10\_N.B, Time Period=2026-10-01; 구절: OBS\_07818a1242169b952349e54e0651560e013d9c511c3728a9955db7bd85184067; snapshot: 79a230cc8bff4d412dd2e177ce59c8d2f218131dd37a72bf1cda3324e78f6c9b.
- 정의: \{'measure': 'US\_TREASURY\_NOMINAL\_10Y', 'unit': 'percent', 'period': 'daily', 'currency': 'USD', 'adjustment': 'not\_seasonally\_adjusted', 'scope': '10-year constant-maturity Treasury yield, quoted on investment basis, annual percent; not policy rate, real yield or realized bond return. CSV Currency NA means no currency amount; underlying Treasury exposure is USD.'\}; 시점 적합성: fresh.
- 한계: 원관측의 수치 확인이며 수익률·인과·투자 매력의 확인이 아니다.
- 한계: 전체 개정 이력은 미확인이다.

<a id="opportunity-72378b2cfe6e2c4037026eae05cebe253852fd77054ab86d9263137b0d9d2b94"></a>
### 근거 · OBS\_2306367a60353ffcf26f8e9500b2fb35e06053edca8be83b487a786171ed5e14

- 출처: [1](#opportunity-c436613f5d09e28fd85e2bc46b272d6421f81f0e3f63f160bcbb83e83676c4ce); 분류: observed\_fact; 원문 확인: supported\_within\_scope; 해석 검토: reviewed.
- 원문: 미국 headline CPI-U 원지수 (NSA); observation=2025-07-01; value=323.048 index
- 위치: /Results/series/0/data/14/value; year=2025, period=M07; 구절: OBS\_2306367a60353ffcf26f8e9500b2fb35e06053edca8be83b487a786171ed5e14; snapshot: 5f659b87469da318e1d476987fb1d686bdf23f34cae1194297a4996299564a05.
- 정의: \{'measure': 'US\_CPI\_U\_HEADLINE\_NSA', 'unit': 'index', 'period': 'monthly', 'currency': None, 'adjustment': 'not\_seasonally\_adjusted', 'scope': 'All items CPI-U, U.S. city average, 1982–84=100; not seasonally adjusted. Monthly label is the reference month, not the release date.'\}; 시점 적합성: stale.
- 한계: 원관측의 수치 확인이며 수익률·인과·투자 매력의 확인이 아니다.
- 한계: 전체 개정 이력은 미확인이다.

<a id="opportunity-5a1bbe31a9d75c92a98131627c8ff42ab446c1975e586ce9f3c3dcde13fae4ee"></a>
### 근거 · OBS\_4f71fa1977631869c63acd1e8d101a03ef2dfefbeb88d03404e245eceb623042

- 출처: [84](#opportunity-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700); 분류: observed\_fact; 원문 확인: supported\_within\_scope; 해석 검토: reviewed.
- 원문: 미국 국채 2년 명목 시장금리; observation=2026-09-30; value=4.88 percent
- 위치: CSV row 16898, column RIFLGFCY02\_N.B, Time Period=2026-09-30; 구절: OBS\_4f71fa1977631869c63acd1e8d101a03ef2dfefbeb88d03404e245eceb623042; snapshot: 79a230cc8bff4d412dd2e177ce59c8d2f218131dd37a72bf1cda3324e78f6c9b.
- 정의: \{'measure': 'US\_TREASURY\_NOMINAL\_2Y', 'unit': 'percent', 'period': 'daily', 'currency': 'USD', 'adjustment': 'not\_seasonally\_adjusted', 'scope': '2-year constant-maturity Treasury yield, quoted on investment basis, annual percent; not policy rate, real yield or realized bond return. CSV Currency NA means no currency amount; underlying Treasury exposure is USD.'\}; 시점 적합성: fresh.
- 한계: 원관측의 수치 확인이며 수익률·인과·투자 매력의 확인이 아니다.
- 한계: 전체 개정 이력은 미확인이다.

<a id="opportunity-9a80737d20585ec1269bc790495de0fed65545075370ea8c3521ca28c4b278b2"></a>
### 근거 · OBS\_747b853a1e65c409c35cdf5a1718c237c2c26eaeb10667e60bd7ebf0058ce20e

- 출처: [1](#opportunity-c436613f5d09e28fd85e2bc46b272d6421f81f0e3f63f160bcbb83e83676c4ce); 분류: observed\_fact; 원문 확인: supported\_within\_scope; 해석 검토: reviewed.
- 원문: 미국 headline CPI-U 원지수 (NSA); observation=2026-07-01; value=333.918 index
- 위치: /Results/series/0/data/1/value; year=2026, period=M07; 구절: OBS\_747b853a1e65c409c35cdf5a1718c237c2c26eaeb10667e60bd7ebf0058ce20e; snapshot: 5f659b87469da318e1d476987fb1d686bdf23f34cae1194297a4996299564a05.
- 정의: \{'measure': 'US\_CPI\_U\_HEADLINE\_NSA', 'unit': 'index', 'period': 'monthly', 'currency': None, 'adjustment': 'not\_seasonally\_adjusted', 'scope': 'All items CPI-U, U.S. city average, 1982–84=100; not seasonally adjusted. Monthly label is the reference month, not the release date.'\}; 시점 적합성: stale.
- 한계: 원관측의 수치 확인이며 수익률·인과·투자 매력의 확인이 아니다.
- 한계: 전체 개정 이력은 미확인이다.

<a id="opportunity-d0e7fa100a289ad973f2cb6a8f55eb7f3fe3589b84a75556fe877920dc8cbc59"></a>
### 근거 · OBS\_7e4d1757c139da8cbec498d40b56467bb2c1803f22083e004b0df0ce9cd6d490

- 출처: [1](#opportunity-c436613f5d09e28fd85e2bc46b272d6421f81f0e3f63f160bcbb83e83676c4ce); 분류: observed\_fact; 원문 확인: supported\_within\_scope; 해석 검토: reviewed.
- 원문: 미국 headline CPI-U 원지수 (NSA); observation=2025-08-01; value=323.976 index
- 위치: /Results/series/0/data/13/value; year=2025, period=M08; 구절: OBS\_7e4d1757c139da8cbec498d40b56467bb2c1803f22083e004b0df0ce9cd6d490; snapshot: 5f659b87469da318e1d476987fb1d686bdf23f34cae1194297a4996299564a05.
- 정의: \{'measure': 'US\_CPI\_U\_HEADLINE\_NSA', 'unit': 'index', 'period': 'monthly', 'currency': None, 'adjustment': 'not\_seasonally\_adjusted', 'scope': 'All items CPI-U, U.S. city average, 1982–84=100; not seasonally adjusted. Monthly label is the reference month, not the release date.'\}; 시점 적합성: stale.
- 한계: 원관측의 수치 확인이며 수익률·인과·투자 매력의 확인이 아니다.
- 한계: 전체 개정 이력은 미확인이다.

<a id="opportunity-040564f07f2b2b9912608053978be8aa818f3a19cf7833eb70b68274559bef9a"></a>
### 근거 · OBS\_7fbd2dbc8c42ffd6fd71548a6a0a62d4c0d853b78e49d2512fd3fae3ceda1e18

- 출처: [83](#opportunity-f56e2932df7c7cf95311e4e66639477af2df08d54da6d6f81da7d23af5c880f1); 분류: observed\_fact; 원문 확인: supported\_within\_scope; 해석 검토: reviewed.
- 원문: 원/달러 뉴욕 정오 기준환율; observation=2026-09-24; value=1369.4400 KRW\_per\_USD
- 위치: CSV row 255, column RXI\_N.B.KO, Time Period=2026-09-24; 구절: OBS\_7fbd2dbc8c42ffd6fd71548a6a0a62d4c0d853b78e49d2512fd3fae3ceda1e18; snapshot: e6024ea571d2a6c5b6cd6ed43e1ca06a25673b8ccb4051ed3fdb284d32f9ca0f.
- 정의: \{'measure': 'USD\_KRW\_NOON\_REFERENCE', 'unit': 'KRW\_per\_USD', 'period': 'daily', 'currency': 'KRW', 'adjustment': 'not\_seasonally\_adjusted', 'scope': 'South Korean won per U.S. dollar; noon New York buying/reference rate. An increase means more KRW per USD, not a domestic executed FX rate or a realized foreign-asset return.'\}; 시점 적합성: fresh.
- 한계: 원관측의 수치 확인이며 수익률·인과·투자 매력의 확인이 아니다.
- 한계: 전체 개정 이력은 미확인이다.

<a id="opportunity-e6264ddceb2cd14486287b063dcbdb336ef7605dc926a651e0e5aa56583b899e"></a>
### 근거 · OBS\_8424e0112254d8ba4e20949656543c4204966432b76a785076aa0670fe697a28

- 출처: [83](#opportunity-f56e2932df7c7cf95311e4e66639477af2df08d54da6d6f81da7d23af5c880f1); 분류: observed\_fact; 원문 확인: supported\_within\_scope; 해석 검토: reviewed.
- 원문: 원/달러 뉴욕 정오 기준환율; observation=2026-09-25; value=1356.5100 KRW\_per\_USD
- 위치: CSV row 256, column RXI\_N.B.KO, Time Period=2026-09-25; 구절: OBS\_8424e0112254d8ba4e20949656543c4204966432b76a785076aa0670fe697a28; snapshot: e6024ea571d2a6c5b6cd6ed43e1ca06a25673b8ccb4051ed3fdb284d32f9ca0f.
- 정의: \{'measure': 'USD\_KRW\_NOON\_REFERENCE', 'unit': 'KRW\_per\_USD', 'period': 'daily', 'currency': 'KRW', 'adjustment': 'not\_seasonally\_adjusted', 'scope': 'South Korean won per U.S. dollar; noon New York buying/reference rate. An increase means more KRW per USD, not a domestic executed FX rate or a realized foreign-asset return.'\}; 시점 적합성: fresh.
- 한계: 원관측의 수치 확인이며 수익률·인과·투자 매력의 확인이 아니다.
- 한계: 전체 개정 이력은 미확인이다.

<a id="opportunity-c3102ca23240ec811e5b5ff6760356c8ed7b4238555d745fa8db8fec64fc2998"></a>
### 근거 · OBS\_c91d38cfb196adeed9e7d1132bdb9dbd777e11a48a5a0b94764f58fc4c6d6cdb

- 출처: [84](#opportunity-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700); 분류: observed\_fact; 원문 확인: supported\_within\_scope; 해석 검토: reviewed.
- 원문: 미국 국채 2년 명목 시장금리; observation=2026-10-01; value=4.78 percent
- 위치: CSV row 16899, column RIFLGFCY02\_N.B, Time Period=2026-10-01; 구절: OBS\_c91d38cfb196adeed9e7d1132bdb9dbd777e11a48a5a0b94764f58fc4c6d6cdb; snapshot: 79a230cc8bff4d412dd2e177ce59c8d2f218131dd37a72bf1cda3324e78f6c9b.
- 정의: \{'measure': 'US\_TREASURY\_NOMINAL\_2Y', 'unit': 'percent', 'period': 'daily', 'currency': 'USD', 'adjustment': 'not\_seasonally\_adjusted', 'scope': '2-year constant-maturity Treasury yield, quoted on investment basis, annual percent; not policy rate, real yield or realized bond return. CSV Currency NA means no currency amount; underlying Treasury exposure is USD.'\}; 시점 적합성: fresh.
- 한계: 원관측의 수치 확인이며 수익률·인과·투자 매력의 확인이 아니다.
- 한계: 전체 개정 이력은 미확인이다.

<a id="opportunity-620a418a6a6a4261843c24ff2333f800efb7980ab22c9104b60985e7cf50d542"></a>
### 근거 · OBS\_d5795e9fafd8d3fe02729bd70c263d8c56c00c609e11bb9748c11b5c7c5a30b2

- 출처: [84](#opportunity-d96ad0a7f2b96bd265d34737b8615c860945599441c2c527ac6ceb02335c3700); 분류: observed\_fact; 원문 확인: supported\_within\_scope; 해석 검토: reviewed.
- 원문: 미국 국채 10년 명목 시장금리; observation=2026-09-30; value=5.29 percent
- 위치: CSV row 16898, column RIFLGFCY10\_N.B, Time Period=2026-09-30; 구절: OBS\_d5795e9fafd8d3fe02729bd70c263d8c56c00c609e11bb9748c11b5c7c5a30b2; snapshot: 79a230cc8bff4d412dd2e177ce59c8d2f218131dd37a72bf1cda3324e78f6c9b.
- 정의: \{'measure': 'US\_TREASURY\_NOMINAL\_10Y', 'unit': 'percent', 'period': 'daily', 'currency': 'USD', 'adjustment': 'not\_seasonally\_adjusted', 'scope': '10-year constant-maturity Treasury yield, quoted on investment basis, annual percent; not policy rate, real yield or realized bond return. CSV Currency NA means no currency amount; underlying Treasury exposure is USD.'\}; 시점 적합성: fresh.
- 한계: 원관측의 수치 확인이며 수익률·인과·투자 매력의 확인이 아니다.
- 한계: 전체 개정 이력은 미확인이다.

<a id="opportunity-73093f50e5b3d2718365e594b3c901b424a5a91656c007228969c8c7be809404"></a>
### 원문 수치 · F\_SP\_FORWARD\_12M\_PE

- S&amp;P 500 rolling forward십이 개월 P/E; 상태: available.
- 관측: 2026-09-30; 범위: SP500; 기간: Rolling next twelve months EPS; price close2026-09-30; 정의: forward\_12m\_pe; 통화: USD.
- 원문과 정의: [58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923); 전사 토큰: 19.0.
- 값: 19.0 ratio; 범위 표현: reported.

<a id="opportunity-c3f1f365bf6c6943467d10b60a833cc77469069bc5e7ce061cfc8a2d5aff4802"></a>
### 원문 수치 · F\_SP\_PE\_AVG5

- 동일 provider forward P/E 오 년 평균; 상태: available.
- 관측: 2026-09-30; 범위: SP500; 기간: Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923); 전사 토큰: 19.8.
- 값: 19.8 ratio; 범위 표현: reported.

<a id="opportunity-26e52141e43b61f663fefa51639a48ea9d23fa1d7cd5912391aeb2656894aac3"></a>
### 원문 수치 · F\_SP\_PE\_AVG10

- 동일 provider forward P/E 십 년 평균; 상태: available.
- 관측: 2026-09-30; 범위: SP500; 기간: Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923); 전사 토큰: 19.1.
- 값: 19.1 ratio; 범위 표현: reported.

<a id="opportunity-863a890922eb503731957e727c17981bd1898d0d0489e7f93d9a5daad63e6ad4"></a>
### 원문 수치 · F\_SP\_PE\_JUN30

- S&amp;P 500 이전 분기말 rolling forward P/E; 상태: available.
- 관측: 2026-06-30; 범위: SP500; 기간: Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923); 전사 토큰: 20.4.
- 값: 20.4 ratio; 범위 표현: reported.

<a id="opportunity-4dbefb1cf006d981bd4fd4206ef0b8a1c5ec7f22d38f072413b56716004514bc"></a>
### 원문 수치 · F\_SP\_FY1\_PE

- State Street S&amp;P 500 FY1 weighted harmonic P/E; 상태: available.
- 관측: 2026-10-01; 범위: SP500; 기간: 2026-10-01; 정의: forward\_fy1\_harmonic\_pe; 통화: USD.
- 원문과 정의: [64](#opportunity-66774f8cbd44f9662bd86c5f6ac7f2c24026573590ba939cee9eb375ed014ec4); 전사 토큰: 20.43.
- 값: 20.43 ratio; 범위 표현: reported.

<a id="opportunity-a95b45c29e1d85ad6b1c1a027d44707f2c232e4955982fdb151d07e2afb26a0a"></a>
### 원문 수치 · F\_SP\_TRAILING\_PE

- State Street S&amp;P 500 trailing P/E; 상태: available.
- 관측: 2026-10-01; 범위: SP500; 기간: 2026-10-01; 정의: trailing\_harmonic\_pe; 통화: USD.
- 원문과 정의: [64](#opportunity-66774f8cbd44f9662bd86c5f6ac7f2c24026573590ba939cee9eb375ed014ec4); 전사 토큰: 24.62.
- 값: 24.62 ratio; 범위 표현: reported.

<a id="opportunity-66b1e8462593efff5028ba8dc5c2a36c5244fa9783cbafad272ede0b6b8c37ad"></a>
### 원문 수치 · F\_Q3\_EPS\_REVISION

- 셋째분기 EPS 예상치 분기 중 상향폭; 상태: available.
- 관측: 2026-09-30; 범위: SP500; 기간: Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [60](#opportunity-6b7d1c16c59591fa548f3559dbcf6f1a0e74b7d2752ba1165d7d8b0da7f6cd7a); 전사 토큰: 1.4.
- 값: 1.4 percent; 범위 표현: reported.

<a id="opportunity-4735e92aeab47f0c619e0620bb514bf86125b4fee3334249a5a0e04c95cd0550"></a>
### 원문 수치 · F\_Q2\_EPS\_REVISION

- 둘째분기 EPS 예상치 분기 중 상향폭; 상태: available.
- 관측: 2026-06-30; 범위: SP500; 기간: Q2 2026 earnings-season entry vintage 2026-07-02; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [57](#opportunity-fea4e3a549d932160d3cbdc73e9d6519da848ff1c0398b5711c6cd23283652a2); 전사 토큰: 3.4.
- 값: 3.4 percent; 범위 표현: reported.

<a id="opportunity-e7e552d143fe6321c03f0b20ba3fad61adeb0e5445889d4820e904710187dee9"></a>
### 원문 수치 · F\_Q3\_EARNINGS\_GROWTH

- 셋째분기 현재 예상 earnings growth; 상태: available.
- 관측: 2026-10-02; 범위: SP500; 기간: Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [59](#opportunity-316f23af85e16b23cf2c3d3571c2761050ce97394468c9a46c388987b30d6e68); 전사 토큰: 29.5.
- 값: 29.5 percent; 범위 표현: reported.

<a id="opportunity-c99f385a1413e72205545356a38b500ac01312f15cfb7500f98420a4646fa221"></a>
### 원문 수치 · F\_Q3\_OLD\_GROWTH

- 셋째분기 시작 당시 예상 earnings growth; 상태: available.
- 관측: 2026-06-30; 범위: SP500; 기간: Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [59](#opportunity-316f23af85e16b23cf2c3d3571c2761050ce97394468c9a46c388987b30d6e68); 전사 토큰: 26.7.
- 값: 26.7 percent; 범위 표현: reported.

<a id="opportunity-6778a553aa00399fafa1be358805067739db73049b4fc5f5a312442b941cddb6"></a>
### 원문 수치 · F\_Q3\_REVENUE\_GROWTH

- 셋째분기 현재 예상 revenue growth; 상태: available.
- 관측: 2026-10-02; 범위: SP500; 기간: Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923); 전사 토큰: 12.3.
- 값: 12.3 percent; 범위 표현: reported.

<a id="opportunity-31c17d2a4aec9ab493850d9ca2b412fbaff142466c9df2e7b78d5ecea158eaab"></a>
### 원문 수치 · F\_Q3\_OLD\_REVENUE

- 셋째분기 시작 당시 예상 revenue growth; 상태: available.
- 관측: 2026-06-30; 범위: SP500; 기간: Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923); 전사 토큰: 10.9.
- 값: 10.9 percent; 범위 표현: reported.

<a id="opportunity-abf4c6167a636bc85ec5913b587828bf353f515fbe592d7f8bc99517140ac47c"></a>
### 원문 수치 · F\_Q4\_EARNINGS\_GROWTH

- 넷째분기 예상 earnings growth; 상태: available.
- 관측: 2026-10-02; 범위: SP500; 기간: Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923); 전사 토큰: 27.6.
- 값: 27.6 percent; 범위 표현: reported.

<a id="opportunity-30e83cdba97eb0cbc7bab7414f4f157f9942bbce1210f894deb175a6f9b4c06a"></a>
### 원문 수치 · F\_CY\_EARNINGS\_GROWTH

- 올해 예상 earnings growth; 상태: available.
- 관측: 2026-10-02; 범위: SP500; 기간: Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [58](#opportunity-966dfca6f5104df1fb3290bc8b86047d7249815a703db0689b0ef3210e633923); 전사 토큰: 32.4.
- 값: 32.4 percent; 범위 표현: reported.

<a id="opportunity-2b4a640f819c56f17eeb78cb45c506f1a9def79c966fc8bc7ce40df5b942e610"></a>
### 원문 수치 · F\_CY\_OLD\_GROWTH

- 칠월 판본의 올해 예상 earnings growth; 상태: available.
- 관측: 2026-07-02; 범위: SP500; 기간: Q2 2026 earnings-season entry vintage 2026-07-02; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [56](#opportunity-1dd5bf67509f2d871a487d06d46552df17b00f8c45d1b4f58c6201982656a486); 전사 토큰: 24.1.
- 값: 24.1 percent; 범위 표현: reported.

<a id="opportunity-53037b12cd639977c63bf48556e737d519f3ea469e3cfc5b20cf9b0092b15fa1"></a>
### 원문 수치 · F\_Q3\_GUIDERS

- EPS guidance를 발표한 기업 수; 상태: available.
- 관측: 2026-10-02; 범위: SP500; 기간: Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [59](#opportunity-316f23af85e16b23cf2c3d3571c2761050ce97394468c9a46c388987b30d6e68); 전사 토큰: 116.
- 값: 116 count; 범위 표현: reported.

<a id="opportunity-cf87274a8867005746200c4eb3f37a81277141b9595a5e614d6852d3b9493a1c"></a>
### 원문 수치 · F\_Q3\_POSITIVE\_GUIDANCE

- positive EPS guidance 기업 수; 상태: available.
- 관측: 2026-10-02; 범위: SP500; 기간: Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [59](#opportunity-316f23af85e16b23cf2c3d3571c2761050ce97394468c9a46c388987b30d6e68); 전사 토큰: 72.
- 값: 72 count; 범위 표현: reported.

<a id="opportunity-6d7593215d334eac20aa941badad70051d2afdc8f569acc38233fe05ae66f4c0"></a>
### 원문 수치 · F\_Q3\_NEGATIVE\_GUIDANCE

- negative EPS guidance 기업 수; 상태: available.
- 관측: 2026-10-02; 범위: SP500; 기간: Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [59](#opportunity-316f23af85e16b23cf2c3d3571c2761050ce97394468c9a46c388987b30d6e68); 전사 토큰: 44.
- 값: 44 count; 범위 표현: reported.

<a id="opportunity-d2b7630b8092576e7238e834f09facafd5adeaa0f7ae359e0483b6c15485b401"></a>
### 원문 수치 · F\_Q3\_POSITIVE\_SHARE

- guidance 기업 중 positive 비율; 상태: available.
- 관측: 2026-10-02; 범위: SP500; 기간: Q3 2026 consensus vintage 2026-10-02; quarter-end revision window 2026-06-30 to 2026-09-30; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [59](#opportunity-316f23af85e16b23cf2c3d3571c2761050ce97394468c9a46c388987b30d6e68); 전사 토큰: 62%.
- 값: 62 percent; 범위 표현: reported.

<a id="opportunity-ff4c27404c7ebb24e7ac148a3ee482924bb4c132beeeefd66524157f020eec28"></a>
### 원문 수치 · F\_Q2\_INITIAL\_GROWTH

- 둘째분기 시작 예상 earnings growth; 상태: available.
- 관측: 2026-03-31; 범위: SP500; 기간: Q2 2026 earnings-season entry vintage 2026-07-02; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [55](#opportunity-d37c938f074b4fc26f75020ab141f4fddba305da44efe5573354b648e27db6d3); 전사 토큰: 18.8.
- 값: 18.8 percent; 범위 표현: reported.

<a id="opportunity-a78ca6d3932b5b85fe1ea54cdc5b89dc0872f28a4a499d3646e352630dfe8913"></a>
### 원문 수치 · F\_Q2\_ENTRY\_GROWTH

- 둘째분기 발표 전 earnings growth 예상; 상태: available.
- 관측: 2026-07-02; 범위: SP500; 기간: Q2 2026 earnings-season entry vintage 2026-07-02; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [55](#opportunity-d37c938f074b4fc26f75020ab141f4fddba305da44efe5573354b648e27db6d3); 전사 토큰: 23.3.
- 값: 23.3 percent; 범위 표현: reported.

<a id="opportunity-904a07a8fe4e5828efee0b776fd62d91aae63ea96aba9e12d389f7f4a1d3dc4a"></a>
### 원문 수치 · F\_Q2\_BLENDED\_GROWTH

- 둘째분기 발표 중 blended earnings growth; 상태: available.
- 관측: 2026-08-03; 범위: SP500; 기간: Q2 2026 blended earnings-season intermediate vintage 2026-08-03; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [52](#opportunity-508ac2c266322521639c27447547d79009d319c5a0d936e3cf3c9dfcdaffb57f); 전사 토큰: 47.4%.
- 값: 47.4 percent; 범위 표현: reported.

<a id="opportunity-4575f64503d310ae597b8fc9489ad4619473a82971018a73f38e259c10b1932a"></a>
### 원문 수치 · F\_Q2\_EX\_TWO

- 둘째분기 Alphabet·Amazon 제외 blended growth; 상태: available.
- 관측: 2026-08-03; 범위: SP500; 기간: Q2 2026 blended earnings-season intermediate vintage 2026-08-03; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [52](#opportunity-508ac2c266322521639c27447547d79009d319c5a0d936e3cf3c9dfcdaffb57f); 전사 토큰: 28.8%.
- 값: 28.8 percent; 범위 표현: reported.

<a id="opportunity-c617bb8675438c0829a0e3ad516b7a83b1f303efc4e08ab39671cda94e286523"></a>
### 원문 수치 · F\_Q1\_BEAT\_RATE

- 첫째분기 S&amp;P EPS positive surprise 비율; 상태: available.
- 관측: 2026-05-21; 범위: SP500; 기간: Q1 2026 reported cohort, provider vintage 2026-05-21; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [51](#opportunity-0bd50cc292ebae23a8190a2ed23e7b7fb81784d8b55ea4eedfd7e5960090c41e); 전사 토큰: 84%.
- 값: 84 percent; 범위 표현: reported.

<a id="opportunity-d9bdc8f09d6a500a0ec65beba6d078319a838267cfc7a1285f1b9aaa002a90d9"></a>
### 원문 수치 · F\_Q1\_MAG\_GROWTH

- 첫째분기 Mag7 실제 earnings growth; 상태: available.
- 관측: 2026-05-21; 범위: SP500; 기간: Q1 2026 reported cohort, provider vintage 2026-05-21; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [49](#opportunity-67f88f83d577b04201a022ddd7350653ee9b780e6d9ad0c2f45cb351655c0fee); 전사 토큰: 63.2%.
- 값: 63.2 percent; 범위 표현: reported.

<a id="opportunity-3403ead72107c2ea6771d22bac4ca24cfa10a800e9544293ea34a71c5a5362b6"></a>
### 원문 수치 · F\_Q1\_REST\_GROWTH

- 첫째분기 기타 기업 blended growth; 상태: available.
- 관측: 2026-05-21; 범위: SP500; 기간: Q1 2026 reported cohort, provider vintage 2026-05-21; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [49](#opportunity-67f88f83d577b04201a022ddd7350653ee9b780e6d9ad0c2f45cb351655c0fee); 전사 토큰: 17.4%.
- 값: 17.4 percent; 범위 표현: reported.

<a id="opportunity-e915fc2397b62a67ce2c969247d103eab8e69ab2482e1fc05be2020ec98fbb9d"></a>
### 원문 수치 · F\_AMZN\_Q2\_CONSENSUS\_EPS

- Amazon 둘째분기 발표 전 consensus GAAP EPS; 상태: available.
- 관측: 2026-08-03; 범위: AMZN; 기간: Q2 2026 blended earnings-season intermediate vintage 2026-08-03; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [54](#opportunity-1b207880153d5f87325c148eb3495faec24f75b06b137215ba587f77ecffcba9); 전사 토큰: $1.82.
- 값: 1.82 USD\_per\_share; 범위 표현: reported.

<a id="opportunity-a1804c97e9c94582fab5280da21a248cc375930bd196060127820b8a2116fc51"></a>
### 원문 수치 · F\_AMZN\_Q2\_ACTUAL\_EPS

- Amazon 둘째분기 actual GAAP EPS; 상태: available.
- 관측: 2026-06-30; 범위: AMZN; 기간: Q2 2026 blended earnings-season intermediate vintage 2026-08-03; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [54](#opportunity-1b207880153d5f87325c148eb3495faec24f75b06b137215ba587f77ecffcba9); 전사 토큰: $5.75.
- 값: 5.75 USD\_per\_share; 범위 표현: reported.

<a id="opportunity-9a7b059834c435e467a9bdaa05d3b7acc3948ce2286fd3f3e37a5e6ce5c296ed"></a>
### 원문 수치 · F\_AMZN\_WEEK\_CONTRIBUTION

- Amazon의 한 주간 지수 예상 달러이익 순증 기여 비율; 상태: available.
- 관측: 2026-08-03; 범위: SP500; 기간: Q2 2026 blended earnings-season intermediate vintage 2026-08-03; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [54](#opportunity-1b207880153d5f87325c148eb3495faec24f75b06b137215ba587f77ecffcba9); 전사 토큰: 76%.
- 값: 76 percent; 범위 표현: reported.

<a id="opportunity-8d0b3366ee2c680cdc42f232731fc05a8665e50e692aed2ca460bd886cb1297d"></a>
### 원문 수치 · F\_MSFT\_Q4\_REVENUE

- Microsoft 최근 회계분기 revenue; 상태: available.
- 관측: 2026-06-30; 범위: MSFT; 기간: Quarter ended 2026-06-30, FY2026 Q4; year-over-year comparisons; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [76](#opportunity-40af50b29fc2a933baae21db3c7f5c042205c7469f5f1bc9eba75813b2d093f6); 전사 토큰: $90.0.
- 값: 90.0 USD\_billion; 범위 표현: reported.

<a id="opportunity-4639e68add89ed8038f72d74b728047854207c7666e8817761d59a3b65336b87"></a>
### 원문 수치 · F\_MSFT\_Q4\_OP

- Microsoft 최근 회계분기 operating income; 상태: available.
- 관측: 2026-06-30; 범위: MSFT; 기간: Quarter ended 2026-06-30, FY2026 Q4; year-over-year comparisons; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [76](#opportunity-40af50b29fc2a933baae21db3c7f5c042205c7469f5f1bc9eba75813b2d093f6); 전사 토큰: $40.6.
- 값: 40.6 USD\_billion; 범위 표현: reported.

<a id="opportunity-4e396e4343ec9dbc5639e6610cb99dce04029096375fe59de7bb83e2fc017890"></a>
### 원문 수치 · F\_MSFT\_AI\_RUN\_RATE

- Microsoft 경영진 AI annual revenue run rate; 상태: available.
- 관측: 2026-03-31; 범위: MSFT; 기간: Quarter ended2026-03-31 FY2026 Q3; 정의: management\_run\_rate; 통화: USD.
- 원문과 정의: [73](#opportunity-282faaeb22b446a4e13674231f58da7ed73e88f2c558d5c8a33952ca154755f2); 전사 토큰: $37.
- 값: 37 USD\_billion; 범위 표현: above.

<a id="opportunity-3c09f484c942f3496c07453fc413c6cd8dc6a7c61bdffbd1dcfe646a29103916"></a>
### 원문 수치 · F\_MSFT\_Q4\_GAAP\_EPS

- Microsoft GAAP diluted EPS; 상태: available.
- 관측: 2026-06-30; 범위: MSFT; 기간: Quarter ended 2026-06-30, FY2026 Q4; year-over-year comparisons; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [76](#opportunity-40af50b29fc2a933baae21db3c7f5c042205c7469f5f1bc9eba75813b2d093f6); 전사 토큰: $4.81.
- 값: 4.81 USD\_per\_share; 범위 표현: reported.

<a id="opportunity-9d77339e64d20ff08bf02db9c3f1822a2f68e52a4dfc7f19cb1b302768e60f5e"></a>
### 원문 수치 · F\_MSFT\_Q4\_ADJ\_EPS

- Microsoft OpenAI-adjusted diluted EPS; 상태: available.
- 관측: 2026-06-30; 범위: MSFT; 기간: Quarter ended 2026-06-30, FY2026 Q4; year-over-year comparisons; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [76](#opportunity-40af50b29fc2a933baae21db3c7f5c042205c7469f5f1bc9eba75813b2d093f6); 전사 토큰: $4.74.
- 값: 4.74 USD\_per\_share; 범위 표현: reported.

<a id="opportunity-d4a9dde58942bbbeaa03a69b3be646e4df98309f82b80ad49cd628876140ef5d"></a>
### 원문 수치 · F\_MSFT\_ANTHROPIC\_GAIN

- Microsoft Anthropic investment gain; 상태: available.
- 관측: 2026-06-30; 범위: MSFT; 기간: Quarter ended 2026-06-30, FY2026 Q4; year-over-year comparisons; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [76](#opportunity-40af50b29fc2a933baae21db3c7f5c042205c7469f5f1bc9eba75813b2d093f6); 전사 토큰: $3.2.
- 값: 3.2 USD\_billion; 범위 표현: reported.

<a id="opportunity-a09f0c69515564cae44facde399bc2df9f6edf4ad8091e2189e1049cde408c39"></a>
### 원문 수치 · F\_AMZN\_Q2\_SALES

- Amazon consolidated revenue; 상태: available.
- 관측: 2026-06-30; 범위: AMZN; 기간: Three months ended2026-06-30 consolidated; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [40](#opportunity-b1e3603e6a7013fc14534e3e8ede5925c59341b37516649540d0c9395ff39414); 전사 토큰: 200,606.
- 값: 200606 USD\_million; 범위 표현: reported.

<a id="opportunity-b6a5495d09248a15d0e1989be582adcbe60c2804f81b3fffc548befcc06f3e73"></a>
### 원문 수치 · F\_AMZN\_Q2\_AWS\_REVENUE

- AWS revenue; 상태: available.
- 관측: 2026-06-30; 범위: AMZN; 기간: Three months ended2026-06-30 AWS; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [40](#opportunity-b1e3603e6a7013fc14534e3e8ede5925c59341b37516649540d0c9395ff39414); 전사 토큰: 42,232.
- 값: 42232 USD\_million; 범위 표현: reported.

<a id="opportunity-b994aeab944cef0b9daf1f3550a2be4713a684fc37789a7e0a5684bff3f9a3eb"></a>
### 원문 수치 · F\_AMZN\_Q2\_AWS\_OP

- AWS operating income; 상태: available.
- 관측: 2026-06-30; 범위: AMZN; 기간: Three months ended2026-06-30 AWS; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [39](#opportunity-336adc4556282b6a1e0b10fb829a5ad9dbe3480fb79fa4cc46cee690244bf854); 전사 토큰: 16,621.
- 값: 16621 USD\_million; 범위 표현: reported.

<a id="opportunity-c2c8188a95653b08f775eed887cdffdb94b6eb972545b66d56742dd95ec2c616"></a>
### 원문 수치 · F\_AMZN\_Q2\_OP

- Amazon consolidated operating income; 상태: available.
- 관측: 2026-06-30; 범위: AMZN; 기간: Three months ended2026-06-30 consolidated; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [39](#opportunity-336adc4556282b6a1e0b10fb829a5ad9dbe3480fb79fa4cc46cee690244bf854); 전사 토큰: 27,461.
- 값: 27461 USD\_million; 범위 표현: reported.

<a id="opportunity-9c8ce6830aa4755cd07334b8388c0d2b2439bfe794023f39277583f37c26f456"></a>
### 원문 수치 · F\_AMZN\_Q2\_GAIN

- Amazon private-equity upward valuation adjustments; 상태: available.
- 관측: 2026-06-30; 범위: AMZN; 기간: Three months ended2026-06-30 valuation upward adjustments; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [36](#opportunity-296b989dfcc7122640fee61bea1996ecc9bb4e0ec975e87578515a1cb48824bf); 전사 토큰: 50.5.
- 값: 50.5 USD\_billion; 범위 표현: reported.

<a id="opportunity-b900f1535f1e5bb38709eb3cecf043acb5c5c59f594494c67e460699425e917c"></a>
### 원문 수치 · F\_GOOGL\_CLOUD

- Google Cloud revenue; 상태: available.
- 관측: 2026-06-30; 범위: GOOGL; 기간: Three months ended2026-06-30 Google Cloud; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d); 전사 토큰: $24.8.
- 값: 24.8 USD\_billion; 범위 표현: reported.

<a id="opportunity-85d86b57cbcea4524ae159dda5e9d39bb2fb8488ce840178f32f3e3097de69b6"></a>
### 원문 수치 · F\_GOOGL\_CLOUD\_GROWTH

- Google Cloud reported revenue growth; 상태: available.
- 관측: 2026-06-30; 범위: GOOGL; 기간: Quarter ended2026-06-30; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d); 전사 토큰: 82%.
- 값: 82 percent; 범위 표현: reported.

<a id="opportunity-d74255f87d0278fdee5eaef18f94bc23afff1f9ccef6ac314979342b4bb4846c"></a>
### 원문 수치 · F\_GOOGL\_MARGIN

- Alphabet consolidated operating margin; 상태: available.
- 관측: 2026-06-30; 범위: GOOGL; 기간: Quarter ended2026-06-30; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d); 전사 토큰: 34%.
- 값: 34 percent; 범위 표현: reported.

<a id="opportunity-38492a72dbaf7f1945299c0ab1ca61e24ded3591daa006f88ac014190a76b00c"></a>
### 원문 수치 · F\_GOOGL\_GAIN

- Alphabet other-income net gain; 상태: available.
- 관측: 2026-06-30; 범위: GOOGL; 기간: Quarter ended2026-06-30; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d); 전사 토큰: $98.0.
- 값: 98.0 USD\_billion; 범위 표현: reported.

<a id="opportunity-22a67cad831835ab1656dedf5182025de788e020d8bede0cd2e394bacdb11ccf"></a>
### 원문 수치 · F\_GOOGL\_EPS

- Alphabet GAAP EPS; 상태: available.
- 관측: 2026-06-30; 범위: GOOGL; 기간: Quarter ended2026-06-30; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [48](#opportunity-91de1b0aee62cb3befa5d291c4751ea8fee3f3ce16a452c71331c7b983f4ff9d); 전사 토큰: $9.11.
- 값: 9.11 USD\_per\_share; 범위 표현: reported.

<a id="opportunity-c4accd3e96ece92e0dadc6f85e044a8622969717a2613b8b496ad33af9f4f191"></a>
### 원문 수치 · F\_META\_Q2\_REVENUE

- Meta revenue; 상태: available.
- 관측: 2026-06-30; 범위: META; 기간: Three and six months ended2025/2026-06-30, columns as shown; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [70](#opportunity-1321b216ca715ccdd1d526a2a0f83c2cf01d02c780146f3bc571920ffacda4e7); 전사 토큰: 60,801.
- 값: 60801 USD\_million; 범위 표현: reported.

<a id="opportunity-e4f9c717ac3738c9f13afcc9a80de4a47634af255ed617f9f0a154d47ee2ae21"></a>
### 원문 수치 · F\_META\_Q2\_OP

- Meta operating income; 상태: available.
- 관측: 2026-06-30; 범위: META; 기간: Three and six months ended2025/2026-06-30, columns as shown; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [70](#opportunity-1321b216ca715ccdd1d526a2a0f83c2cf01d02c780146f3bc571920ffacda4e7); 전사 토큰: 18,775.
- 값: 18775 USD\_million; 범위 표현: reported.

<a id="opportunity-c0b12216682751663e25aea812e9bf5916421fcc07ab8906401cce1ed6cddfb7"></a>
### 원문 수치 · F\_META\_Q2\_MARGIN

- Meta current-quarter operating margin; 상태: available.
- 관측: 2026-06-30; 범위: META; 기간: Three and six months ended2025/2026-06-30, columns as shown; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [70](#opportunity-1321b216ca715ccdd1d526a2a0f83c2cf01d02c780146f3bc571920ffacda4e7); 전사 토큰: 31.
- 값: 31 percent; 범위 표현: reported.

<a id="opportunity-40ebe93bd8e7138bcf4f730ca13f88d27d26d593da31408a56851f1db80b31b3"></a>
### 원문 수치 · F\_META\_Q2\_PRIOR\_MARGIN

- Meta prior-year-quarter operating margin; 상태: available.
- 관측: 2025-06-30; 범위: META; 기간: Prior-year quarter ended2025-06-30; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [70](#opportunity-1321b216ca715ccdd1d526a2a0f83c2cf01d02c780146f3bc571920ffacda4e7); 전사 토큰: 43.
- 값: 43 percent; 범위 표현: reported.

<a id="opportunity-9a010d01af31cff2e946938193c35c9da9511c4c6dbc19433b27fe657db98f80"></a>
### 원문 수치 · F\_META\_Q1\_TAX\_GAIN

- Meta prior-quarter tax benefit; 상태: available.
- 관측: 2026-03-31; 범위: META; 기간: Quarter ended2026-03-31; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [67](#opportunity-48bf2ab886fc8eed51a714f16d2bd9c345ffe2bcb1247c50ad2fb08fa223b8dd); 전사 토큰: $8.03.
- 값: 8.03 USD\_billion; 범위 표현: reported.

<a id="opportunity-358461e4ff9b1a382923b05fac8c8704684b27bfc5def65e2eb9d91614737a35"></a>
### 원문 수치 · F\_META\_Q2\_LEGAL

- Meta legal proceeding charges in second quarter; 상태: available.
- 관측: 2026-06-30; 범위: META; 기간: Full-year2026 guidance reported2026-07-29; prior guidance range as disclosed; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [69](#opportunity-f847d37e3d8533aecb2200784f6fcc6b6e9b0b3b009df658340c94674f4e8597); 전사 토큰: $2.4.
- 값: 2.4 USD\_billion; 범위 표현: reported.

<a id="opportunity-10596404e36b7e51a9560e7bc5f22db437f147e73aeaaa783bbe3aa455778c9b"></a>
### 원문 수치 · F\_NVDA\_Q2\_REVENUE

- NVIDIA latest revenue; 상태: available.
- 관측: 2026-07-26; 범위: NVDA; 기간: FY2027 Q2 ended2026-07-26; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [79](#opportunity-57e4dbbc924f0ec234a0e9ffec018db0a3fc8d13b4d1686a9aed0d8fb62a112d); 전사 토큰: 96,221.
- 값: 96221 USD\_million; 범위 표현: reported.

<a id="opportunity-b1eac2a9c250e22d890d9c3971354f8c7012150465b2fae9d11aed6902541176"></a>
### 원문 수치 · F\_NVDA\_Q2\_REVENUE\_GROWTH

- NVIDIA revenue year-over-year growth; 상태: available.
- 관측: 2026-07-26; 범위: NVDA; 기간: FY2027 Q2 Jul26, FY2027 Q1 Apr26, FY2026 Q2 Jul27, columns inthatorder; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [79](#opportunity-57e4dbbc924f0ec234a0e9ffec018db0a3fc8d13b4d1686a9aed0d8fb62a112d); 전사 토큰: 106.
- 값: 106 percent; 범위 표현: reported.

<a id="opportunity-91e45f5b51f9f3afad6b434d86938a490060060844cfb61caf30df6a334ad25d"></a>
### 원문 수치 · F\_NVDA\_Q2\_MARGIN

- NVIDIA gross margin; 상태: available.
- 관측: 2026-07-26; 범위: NVDA; 기간: FY2027 Q2 Jul26, FY2027 Q1 Apr26, FY2026 Q2 Jul27, columns inthatorder; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [79](#opportunity-57e4dbbc924f0ec234a0e9ffec018db0a3fc8d13b4d1686a9aed0d8fb62a112d); 전사 토큰: 75.0.
- 값: 75.0 percent; 범위 표현: reported.

<a id="opportunity-81adf6140273fcbafbcd61181b5e1efe61eb559111e5ea38f4b80e46b0a43140"></a>
### 원문 수치 · F\_NVDA\_Q2\_OP

- NVIDIA operating income; 상태: available.
- 관측: 2026-07-26; 범위: NVDA; 기간: FY2027 Q2 Jul26, FY2027 Q1 Apr26, FY2026 Q2 Jul27, columns inthatorder; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [79](#opportunity-57e4dbbc924f0ec234a0e9ffec018db0a3fc8d13b4d1686a9aed0d8fb62a112d); 전사 토큰: 63,734.
- 값: 63734 USD\_million; 범위 표현: reported.

<a id="opportunity-71fd39dc85c150853a1e5a60fcb87130b2c0ab60a5ebf921c45895ceb6f5d849"></a>
### 원문 수치 · F\_MSFT\_Q4\_OCF

- Microsoft quarter OCF; 상태: available.
- 관측: 2026-06-30; 범위: MSFT; 기간: Three months ended2026-06-30; 정의: operating\_cash\_flow; 통화: USD.
- 원문과 정의: [74](#opportunity-3891ddc8357a02d301a5bf0c0a7be57aad8c3f6773a6555f0602e8bac848d2fd); 전사 토큰: 55,441.
- 값: 55441 USD\_million; 범위 표현: reported.

<a id="opportunity-c1f2a0ed63a34b3fffc1d6a0db03484fc8a8358c9c7012ffd8e8809c530a4aba"></a>
### 원문 수치 · F\_MSFT\_Q4\_CASH\_PPE

- Microsoft quarter signed cash PP&amp;E; 상태: available.
- 관측: 2026-06-30; 범위: MSFT; 기간: Three months ended2026-06-30; 정의: cash\_ppe\_outflow; 통화: USD.
- 원문과 정의: [74](#opportunity-3891ddc8357a02d301a5bf0c0a7be57aad8c3f6773a6555f0602e8bac848d2fd); 전사 토큰: (35,802).
- 값: -35802 USD\_million; 범위 표현: reported.

<a id="opportunity-12e23f701fcb503535ad306522457922705dcf6b17596d0c1a02140ae2782f9d"></a>
### 원문 수치 · F\_MSFT\_Q3\_OCF

- Microsoft prior-quarter OCF; 상태: available.
- 관측: 2026-03-31; 범위: MSFT; 기간: Three months ended2026-03-31; 정의: operating\_cash\_flow; 통화: USD.
- 원문과 정의: [71](#opportunity-0df20b81ac7dabce98733f55bf5447774d07c4cc09fe886d0544d958c623770a); 전사 토큰: 46,679.
- 값: 46679 USD\_million; 범위 표현: reported.

<a id="opportunity-61bd1a6d733adba9dd6390d1698abc1bd63edac87da8a673186b5372ac760fe5"></a>
### 원문 수치 · F\_MSFT\_Q3\_CASH\_PPE

- Microsoft prior-quarter cash PP&amp;E; 상태: available.
- 관측: 2026-03-31; 범위: MSFT; 기간: Three months ended2026-03-31; 정의: cash\_ppe\_outflow; 통화: USD.
- 원문과 정의: [71](#opportunity-0df20b81ac7dabce98733f55bf5447774d07c4cc09fe886d0544d958c623770a); 전사 토큰: (30,876).
- 값: -30876 USD\_million; 범위 표현: reported.

<a id="opportunity-cbf66bd4e581b04e7b55037e42a1fed8d1e155227eb87b8c9a085fc8baaeb37c"></a>
### 원문 수치 · F\_AMZN\_TTM\_OCF

- Amazon TTM OCF; 상태: available.
- 관측: 2026-06-30; 범위: AMZN; 기간: TTM ended2026-06-30; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [35](#opportunity-cbd103faa7480536d1e3615e8a546a5333e8947a770b6b8dfab33bc615da7621); 전사 토큰: 161,403.
- 값: 161403 USD\_million; 범위 표현: reported.

<a id="opportunity-d2a2f6d8fdd2ceed329a02a4879f5e4af7de2731bee0efee9ad990313b7a35b0"></a>
### 원문 수치 · F\_AMZN\_TTM\_NET\_PPE

- Amazon TTM net cash PP&amp;E signed; 상태: available.
- 관측: 2026-06-30; 범위: AMZN; 기간: TTM ended2026-06-30; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [35](#opportunity-cbd103faa7480536d1e3615e8a546a5333e8947a770b6b8dfab33bc615da7621); 전사 토큰: (169,007).
- 값: -169007 USD\_million; 범위 표현: reported.

<a id="opportunity-446e2d7f1fb48eacc59df1888c83118dbf60ce7cfa15b41f8db167eed8e0a0a8"></a>
### 원문 수치 · F\_AMZN\_TTM\_FCF

- Amazon reported TTM FCF; 상태: available.
- 관측: 2026-06-30; 범위: AMZN; 기간: TTM ended2026-06-30; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [35](#opportunity-cbd103faa7480536d1e3615e8a546a5333e8947a770b6b8dfab33bc615da7621); 전사 토큰: (7,604).
- 값: -7604 USD\_million; 범위 표현: reported.

<a id="opportunity-2e5f29377d2a9713fb270e848c311ef250ebbf35a7f5bcbf82a0eed3b18d5e97"></a>
### 원문 수치 · F\_AMZN\_OLD\_TTM\_FCF

- Amazon prior-year reported TTM FCF; 상태: available.
- 관측: 2025-06-30; 범위: AMZN; 기간: TTM ended2025-06-30; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [35](#opportunity-cbd103faa7480536d1e3615e8a546a5333e8947a770b6b8dfab33bc615da7621); 전사 토큰: 18,184.
- 값: 18184 USD\_million; 범위 표현: reported.

<a id="opportunity-39abd35bfec4d58697fde8df5647c83fee3e839f57e2b631741500cf7ec56d4f"></a>
### 원문 수치 · F\_GOOGL\_Q2\_OCF

- Alphabet quarter OCF; 상태: available.
- 관측: 2026-06-30; 범위: GOOGL; 기간: Three months ended2026-06-30; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [47](#opportunity-45223e78f81c1f85bea9f34da572b462652182a4214e7f422b0c50ad66e14a60); 전사 토큰: 39,069.
- 값: 39069 USD\_million; 범위 표현: reported.

<a id="opportunity-6cd47a78e20b299a53fe58d858430b10e30b88647bc3bca1939fcdf6287785a3"></a>
### 원문 수치 · F\_GOOGL\_Q2\_PPE

- Alphabet quarter cash PP&amp;E signed; 상태: available.
- 관측: 2026-06-30; 범위: GOOGL; 기간: Three months ended2026-06-30; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [47](#opportunity-45223e78f81c1f85bea9f34da572b462652182a4214e7f422b0c50ad66e14a60); 전사 토큰: (44,924).
- 값: -44924 USD\_million; 범위 표현: reported.

<a id="opportunity-d4fc223158d95a3a8034bce468494de0726bf46d26d131a32fa64aa98f5471bf"></a>
### 원문 수치 · F\_GOOGL\_Q2\_FCF

- Alphabet reported quarter FCF; 상태: available.
- 관측: 2026-06-30; 범위: GOOGL; 기간: Three months ended2026-06-30; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [47](#opportunity-45223e78f81c1f85bea9f34da572b462652182a4214e7f422b0c50ad66e14a60); 전사 토큰: (5,855).
- 값: -5855 USD\_million; 범위 표현: reported.

<a id="opportunity-7794e42e6f3bbdad38a57694f9a354c9af0062ceea5ca16e0f35f3d224ed4141"></a>
### 원문 수치 · F\_GOOGL\_TTM\_FCF

- Alphabet reported TTM FCF; 상태: available.
- 관측: 2026-06-30; 범위: GOOGL; 기간: TTM ended2026-06-30; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [47](#opportunity-45223e78f81c1f85bea9f34da572b462652182a4214e7f422b0c50ad66e14a60); 전사 토큰: 53,273.
- 값: 53273 USD\_million; 범위 표현: reported.

<a id="opportunity-596d06d1667c9bebda7c21459082c4ac93060ff62510faa88581ee7eeb30e0d4"></a>
### 원문 수치 · F\_GOOGL\_Q1\_PPE

- Alphabet prior-quarter cash PP&amp;E signed; 상태: available.
- 관측: 2026-03-31; 범위: GOOGL; 기간: Three months ended2026-03-31; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [47](#opportunity-45223e78f81c1f85bea9f34da572b462652182a4214e7f422b0c50ad66e14a60); 전사 토큰: (35,674).
- 값: -35674 USD\_million; 범위 표현: reported.

<a id="opportunity-e5c3ccc2431543e79bd0cc5362ef4a417f2c233d59266251cd939007fd18ac86"></a>
### 원문 수치 · F\_GOOGL\_Q1\_FCF

- Alphabet prior-quarter reported FCF; 상태: available.
- 관측: 2026-03-31; 범위: GOOGL; 기간: Three months ended2026-03-31; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [47](#opportunity-45223e78f81c1f85bea9f34da572b462652182a4214e7f422b0c50ad66e14a60); 전사 토큰: 10,116.
- 값: 10116 USD\_million; 범위 표현: reported.

<a id="opportunity-31a3ed49ba4897069dcd2002cc2446dc1f611b3b07c014ee68ff69b7dd3905cb"></a>
### 원문 수치 · F\_META\_Q2\_OCF

- Meta quarter reported OCF; 상태: available.
- 관측: 2026-06-30; 범위: META; 기간: Three months ended2026-06-30; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [68](#opportunity-037e439c2fb443f15ca126faaf69866dc85ac6d8ea840154f009267914ce6a5f); 전사 토큰: $31.86.
- 값: 31.86 USD\_billion; 범위 표현: reported.

<a id="opportunity-a1df977557aab2e6eff61d45ca6c3bfbd3b5b1401ab0b8d105e3bb596ced063d"></a>
### 원문 수치 · F\_META\_Q2\_CAPEX

- Meta CAPEX including finance-lease principal; 상태: available.
- 관측: 2026-06-30; 범위: META; 기간: Three months ended2026-06-30; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [68](#opportunity-037e439c2fb443f15ca126faaf69866dc85ac6d8ea840154f009267914ce6a5f); 전사 토큰: $31.08.
- 값: 31.08 USD\_billion; 범위 표현: reported.

<a id="opportunity-142c3ea2d07a48f1be6e67d7bcaa0575ceaf7f8c7b2607502faa70150faa4c3c"></a>
### 원문 수치 · F\_META\_Q2\_FCF

- Meta reported FCF exact million value; 상태: available.
- 관측: 2026-06-30; 범위: META; 기간: Three months ended2026-06-30; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [68](#opportunity-037e439c2fb443f15ca126faaf69866dc85ac6d8ea840154f009267914ce6a5f); 전사 토큰: $784.
- 값: 784 USD\_million; 범위 표현: reported.

<a id="opportunity-23406d3f77cb3f3fdefcaada06c4c2526a43b5936706ff7f07ec544f67c3160f"></a>
### 원문 수치 · F\_META\_Q1\_CAPEX

- Meta prior-quarter CAPEX incl lease principal; 상태: available.
- 관측: 2026-03-31; 범위: META; 기간: Three months ended2026-03-31; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [65](#opportunity-ceb2746fc488290c12cb776edfbfd7301b41e8b3b2588f645715ac5e5e06a629); 전사 토큰: $19.84.
- 값: 19.84 USD\_billion; 범위 표현: reported.

<a id="opportunity-b06059dc19c5bfa984e1c5a11e7dbbb5644af33d35d7bff1ba16320b84cfa893"></a>
### 원문 수치 · F\_META\_Q1\_FCF

- Meta prior-quarter reported FCF; 상태: available.
- 관측: 2026-03-31; 범위: META; 기간: Three months ended2026-03-31; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [65](#opportunity-ceb2746fc488290c12cb776edfbfd7301b41e8b3b2588f645715ac5e5e06a629); 전사 토큰: $12.39.
- 값: 12.39 USD\_billion; 범위 표현: reported.

<a id="opportunity-0103b3000ae938f2854b6a8fb64870a46cd22bc310af1aecde783a91c5dd0c26"></a>
### 원문 수치 · F\_MSFT\_DEP\_OTHER

- Microsoft depreciation amortization and other; 상태: available.
- 관측: 2026-03-31; 범위: MSFT; 기간: Three months ended2026-03-31; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [72](#opportunity-a4ef4d503886c9613a87e27cb4ce4ece799d20d62a6ab9f84e425db74553f9f0); 전사 토큰: 10,167.
- 값: 10167 USD\_million; 범위 표현: reported.

<a id="opportunity-5de1379d83de63b86d11aa4c0aff612d33a3b408adc3d5eb537cc172c95f7511"></a>
### 원문 수치 · F\_MSFT\_DEP\_OTHER\_OLD

- Microsoft prior-year depreciation amortization and other; 상태: available.
- 관측: 2025-03-31; 범위: MSFT; 기간: Three months ended2025-03-31; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [72](#opportunity-a4ef4d503886c9613a87e27cb4ce4ece799d20d62a6ab9f84e425db74553f9f0); 전사 토큰: 7,734.
- 값: 7734 USD\_million; 범위 표현: reported.

<a id="opportunity-e2f8ed870f207492f12707ef3929d3a85e6bc3eb11731600f1d8bdc04a6fd171"></a>
### 원문 수치 · F\_GOOGL\_DEP

- Alphabet PP&amp;E depreciation; 상태: available.
- 관측: 2026-06-30; 범위: GOOGL; 기간: Three months ended2026-06-30; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [46](#opportunity-072a77d83aa661d8dc45c55d58f4920c78171325f6bfa81e6bad99ce1475713a); 전사 토큰: 7,104.
- 값: 7104 USD\_million; 범위 표현: reported.

<a id="opportunity-45fed6453849ced48ef111336de5aad0421c1adc5c483df03e75e6ae4d1c8c2f"></a>
### 원문 수치 · F\_GOOGL\_DEP\_OLD

- Alphabet prior-year PP&amp;E depreciation; 상태: available.
- 관측: 2025-06-30; 범위: GOOGL; 기간: Three months ended2025-06-30; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [46](#opportunity-072a77d83aa661d8dc45c55d58f4920c78171325f6bfa81e6bad99ce1475713a); 전사 토큰: 4,998.
- 값: 4998 USD\_million; 범위 표현: reported.

<a id="opportunity-8f6b6f53fb565a1551c187f7a61d7add5cae6f59a5f7c42ffc1cf060ba1d33e0"></a>
### 원문 수치 · F\_AMZN\_DEP

- Amazon broad depreciation amortization expense; 상태: available.
- 관측: 2026-06-30; 범위: AMZN; 기간: Three months ended2026-06-30; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [38](#opportunity-125d2475b86dd881d37f5ce1b1c2648b98cb16f4b87055eb486f9f7a83f5e9fe); 전사 토큰: 19,988.
- 값: 19988 USD\_million; 범위 표현: reported.

<a id="opportunity-a90039ce24201556510dda28e1a76f32efd5989ca26f145571a109224c8376c7"></a>
### 원문 수치 · F\_AMZN\_DEP\_OLD

- Amazon prior-year broad depreciation amortization expense; 상태: available.
- 관측: 2025-06-30; 범위: AMZN; 기간: Three months ended2025-06-30; 정의: reported\_financial; 통화: USD.
- 원문과 정의: [38](#opportunity-125d2475b86dd881d37f5ce1b1c2648b98cb16f4b87055eb486f9f7a83f5e9fe); 전사 토큰: 15,227.
- 값: 15227 USD\_million; 범위 표현: reported.

<a id="opportunity-ed12823c22c66323845f8705962084e3ab8fe82d69bf056333c4d298d6de1978"></a>
### 원문 수치 · F\_WEIGHT\_NVDA

- NVDA index security weight; 상태: available.
- 관측: 2026-10-01; 범위: SP500; 기간: 2026-10-01; 정의: index\_weight; 통화: USD.
- 원문과 정의: [62](#opportunity-febef5b3512e3246d505fa88c75746433721577dc6e0c32f756954079be875a5); 전사 토큰: 8.46%.
- 값: 8.46 percent; 범위 표현: reported.

<a id="opportunity-4c9eadb9660cce133c76aa57ed18e5ef4c0f5ccfd4ba3000104088603cdb51f3"></a>
### 원문 수치 · F\_WEIGHT\_AAPL

- AAPL index security weight; 상태: available.
- 관측: 2026-10-01; 범위: SP500; 기간: 2026-10-01; 정의: index\_weight; 통화: USD.
- 원문과 정의: [62](#opportunity-febef5b3512e3246d505fa88c75746433721577dc6e0c32f756954079be875a5); 전사 토큰: 7.30%.
- 값: 7.30 percent; 범위 표현: reported.

<a id="opportunity-411b4017c67138af5ce79a12018b88376d82d4142b9174aa77927526c27cf0d1"></a>
### 원문 수치 · F\_WEIGHT\_MSFT

- MSFT index security weight; 상태: available.
- 관측: 2026-10-01; 범위: SP500; 기간: 2026-10-01; 정의: index\_weight; 통화: USD.
- 원문과 정의: [62](#opportunity-febef5b3512e3246d505fa88c75746433721577dc6e0c32f756954079be875a5); 전사 토큰: 5.77%.
- 값: 5.77 percent; 범위 표현: reported.

<a id="opportunity-6f392751231bf7a7e30f55641953ccb8ec0f88d03bb11973dd770df473968eb6"></a>
### 원문 수치 · F\_WEIGHT\_AMZN

- AMZN index security weight; 상태: available.
- 관측: 2026-10-01; 범위: SP500; 기간: 2026-10-01; 정의: index\_weight; 통화: USD.
- 원문과 정의: [62](#opportunity-febef5b3512e3246d505fa88c75746433721577dc6e0c32f756954079be875a5); 전사 토큰: 3.69%.
- 값: 3.69 percent; 범위 표현: reported.

<a id="opportunity-066827a4f3b9aa8f17adfc0c10fd7cd999a26ccb6aff421cc25425cb1dced3df"></a>
### 원문 수치 · F\_WEIGHT\_GOOGL\_A

- GOOGL\_A index security weight; 상태: available.
- 관측: 2026-10-01; 범위: SP500; 기간: 2026-10-01; 정의: index\_weight; 통화: USD.
- 원문과 정의: [62](#opportunity-febef5b3512e3246d505fa88c75746433721577dc6e0c32f756954079be875a5); 전사 토큰: 3.01%.
- 값: 3.01 percent; 범위 표현: reported.

<a id="opportunity-5a9e18f7781c0bffd3dd616ac424f066df84de8eebd0979c9ca8877002b792d2"></a>
### 원문 수치 · F\_WEIGHT\_GOOGL\_C

- GOOGL\_C index security weight; 상태: available.
- 관측: 2026-10-01; 범위: SP500; 기간: 2026-10-01; 정의: index\_weight; 통화: USD.
- 원문과 정의: [62](#opportunity-febef5b3512e3246d505fa88c75746433721577dc6e0c32f756954079be875a5); 전사 토큰: 2.41%.
- 값: 2.41 percent; 범위 표현: reported.

<a id="opportunity-2b35a6645cd4a91e26afc7ba06ce297d925abeaec2438d0d4ac83a8d36c9c77a"></a>
### 원문 수치 · F\_TREASURY\_3M

- Treasury 3M nominal CMT yield; 상태: available.
- 관측: 2026-10-01; 범위: UST\_3M; 기간: nominal CMT tenor 3M observed2026-10-01, H15 investment basis; 정의: nominal\_cmt\_investment\_yield; 통화: USD.
- 원문과 정의: [80](#opportunity-e21239fba7cb4fb001969b6e9782c0f26bcecfc702dd353ed82368fc1b4dc848); 전사 토큰: 4.17.
- 값: 4.17 percent; 범위 표현: reported.

<a id="opportunity-2e4ac33afdb1ab63ba4287711b22dadd7a2b9878facb1fb49ce07a310de3a40b"></a>
### 원문 수치 · F\_TREASURY\_2Y

- Treasury 2Y nominal CMT yield; 상태: available.
- 관측: 2026-10-01; 범위: UST\_2Y; 기간: nominal CMT tenor 2Y observed2026-10-01, H15 investment basis; 정의: nominal\_cmt\_investment\_yield; 통화: USD.
- 원문과 정의: [80](#opportunity-e21239fba7cb4fb001969b6e9782c0f26bcecfc702dd353ed82368fc1b4dc848); 전사 토큰: 4.78.
- 값: 4.78 percent; 범위 표현: reported.

<a id="opportunity-c2d59a3c600a2937d3ced074289ab8dc3a946dc2046052b405a081497e2fbfbf"></a>
### 원문 수치 · F\_TREASURY\_5Y

- Treasury 5Y nominal CMT yield; 상태: available.
- 관측: 2026-10-01; 범위: UST\_5Y; 기간: nominal CMT tenor 5Y observed2026-10-01, H15 investment basis; 정의: nominal\_cmt\_investment\_yield; 통화: USD.
- 원문과 정의: [80](#opportunity-e21239fba7cb4fb001969b6e9782c0f26bcecfc702dd353ed82368fc1b4dc848); 전사 토큰: 5.01.
- 값: 5.01 percent; 범위 표현: reported.

<a id="opportunity-f00e945ee8a304602c6248939d5468e27794d7fdc1fd0ecb3be3ab52a5b921ef"></a>
### 원문 수치 · F\_TREASURY\_10Y

- Treasury 10Y nominal CMT yield; 상태: available.
- 관측: 2026-10-01; 범위: UST\_10Y; 기간: nominal CMT tenor 10Y observed2026-10-01, H15 investment basis; 정의: nominal\_cmt\_investment\_yield; 통화: USD.
- 원문과 정의: [80](#opportunity-e21239fba7cb4fb001969b6e9782c0f26bcecfc702dd353ed82368fc1b4dc848); 전사 토큰: 5.24.
- 값: 5.24 percent; 범위 표현: reported.

<a id="opportunity-ce997e26e3bca55bb05cb209ce8b8e618cbe78e38dcd1a394a1ea4a01cb767ad"></a>
### 원문 수치 · F\_TREASURY\_30Y

- Treasury 30Y nominal CMT yield; 상태: available.
- 관측: 2026-10-01; 범위: UST\_30Y; 기간: nominal CMT tenor 30Y observed2026-10-01, H15 investment basis; 정의: nominal\_cmt\_investment\_yield; 통화: USD.
- 원문과 정의: [80](#opportunity-e21239fba7cb4fb001969b6e9782c0f26bcecfc702dd353ed82368fc1b4dc848); 전사 토큰: 5.61.
- 값: 5.61 percent; 범위 표현: reported.

<a id="opportunity-68019a948c8c8c365ce41622e139d3f5c886e032164f2180cc56f3d135149b8e"></a>
### 원문 수치 · F\_TREASURY\_10Y\_SEP30

- Treasury십 년 matching valuation date; 상태: available.
- 관측: 2026-09-30; 범위: UST\_10Y; 기간: nominal CMT tenor10Y observed2026-09-30, fourth date column H15 investment basis; 정의: nominal\_cmt\_investment\_yield; 통화: USD.
- 원문과 정의: [80](#opportunity-e21239fba7cb4fb001969b6e9782c0f26bcecfc702dd353ed82368fc1b4dc848); 전사 토큰: 5.29.
- 값: 5.29 percent; 범위 표현: reported.

<a id="opportunity-35fbd2f211104049451fa24e4e7cb1cba180166490a5fbeea78e72832485e47f"></a>
### 원문 수치 · F\_META\_CAPEX\_CURRENT\_MIN

- Meta current CAPEX guidance lower bound; 상태: available.
- 관측: 2026-07-29; 범위: META; 기간: Full-year2026 CAPEX guidance, not actual, includes finance lease principal; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [69](#opportunity-f847d37e3d8533aecb2200784f6fcc6b6e9b0b3b009df658340c94674f4e8597); 전사 토큰: $130.
- 값: 130 USD\_billion; 범위 표현: reported.

<a id="opportunity-a8002fcb5a61ba42c9b2bd162669c215f538e585443081cdb9774df4b581c62b"></a>
### 원문 수치 · F\_META\_CAPEX\_CURRENT\_MAX

- Meta current CAPEX guidance upper bound; 상태: available.
- 관측: 2026-07-29; 범위: META; 기간: Full-year2026 CAPEX guidance, not actual, includes finance lease principal; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [69](#opportunity-f847d37e3d8533aecb2200784f6fcc6b6e9b0b3b009df658340c94674f4e8597); 전사 토큰: 145.
- 값: 145 USD\_billion; 범위 표현: reported.

<a id="opportunity-0be512fca65a9b17def1e726f9b5a4d4587010f25442de4c87a6c9e5fa7c2764"></a>
### 원문 수치 · F\_META\_CAPEX\_PRIOR\_MIN

- Meta prior guidance lower bound as reported; 상태: available.
- 관측: 2026-07-29; 범위: META; 기간: Prior Full-year2026 CAPEX guidance as restated2026-07-29; 정의: reported\_statistic; 통화: USD.
- 원문과 정의: [69](#opportunity-f847d37e3d8533aecb2200784f6fcc6b6e9b0b3b009df658340c94674f4e8597); 전사 토큰: $125.
- 값: 125 USD\_billion; 범위 표현: reported.

<a id="opportunity-928fb03a3376901298565132542011883a47f9268f34318e809b8ccc8cc6da5e"></a>
### 원문 수치 · F\_WEIGHT\_AVGO

- AVGO index security weight; 상태: available.
- 관측: 2026-10-01; 범위: SP500; 기간: Index top-security market-cap weight2026-10-01; not return or earnings contribution; 정의: index\_weight; 통화: USD.
- 원문과 정의: [62](#opportunity-febef5b3512e3246d505fa88c75746433721577dc6e0c32f756954079be875a5); 전사 토큰: 2.48%.
- 값: 2.48 percent; 범위 표현: reported.

<a id="opportunity-10ec9264c327abf0a433ec7b472c2b3ca35b7c150f7c197e20a844754be64c34"></a>
### 원문 수치 · F\_WEIGHT\_META

- META index security weight; 상태: available.
- 관측: 2026-10-01; 범위: SP500; 기간: Index top-security market-cap weight2026-10-01; not return or earnings contribution; 정의: index\_weight; 통화: USD.
- 원문과 정의: [62](#opportunity-febef5b3512e3246d505fa88c75746433721577dc6e0c32f756954079be875a5); 전사 토큰: 2.42%.
- 값: 2.42 percent; 범위 표현: reported.

<a id="opportunity-457f917e357e99edd1cfe57da35b1ccbe41a05e614b012a3b09a4fa757e58def"></a>
### 원문 수치 · F\_WEIGHT\_MU

- MU index security weight; 상태: available.
- 관측: 2026-10-01; 범위: SP500; 기간: Index top-security market-cap weight2026-10-01; not return or earnings contribution; 정의: index\_weight; 통화: USD.
- 원문과 정의: [62](#opportunity-febef5b3512e3246d505fa88c75746433721577dc6e0c32f756954079be875a5); 전사 토큰: 1.88%.
- 값: 1.88 percent; 범위 표현: reported.

<a id="opportunity-ee056bf87dd1d8c584967e67f8ba95f68d00ce1cb44eecfd917e3e304223be8c"></a>
### 원문 수치 · F\_WEIGHT\_AMD

- AMD index security weight; 상태: available.
- 관측: 2026-10-01; 범위: SP500; 기간: Index top-security market-cap weight2026-10-01; not return or earnings contribution; 정의: index\_weight; 통화: USD.
- 원문과 정의: [62](#opportunity-febef5b3512e3246d505fa88c75746433721577dc6e0c32f756954079be875a5); 전사 토큰: 1.52%.
- 값: 1.52 percent; 범위 표현: reported.

<a id="opportunity-5fd4c37672cd04186b9cd0301e06c206ffe735a01ca6963ffb848ddaa81cb78b"></a>
### 계산 · MET\_8aa97f3984a36ed16dbdbd2471ffc6289f0abec879409d702f2b9efd0b87b894

- 직전 관측치 대비 변화: -12.9300 KRW\_per\_USD; 방법: previous\_change\_v1.
- 입력: [197](#opportunity-040564f07f2b2b9912608053978be8aa818f3a19cf7833eb70b68274559bef9a), [198](#opportunity-e6264ddceb2cd14486287b063dcbdb336ef7605dc926a651e0e5aa56583b899e).
- 공식: current\_value - exact\_reference\_value; 기간: (datetime.date(2026, 9, 24), datetime.date(2026, 9, 25)).
- 한계: Decimal precision 50; ROUND\_HALF\_EVEN
- 한계: 결측 보간/forward-fill 없음

<a id="opportunity-73dec51d03affb30b78ef6af5b9837fb5ccf323b6491c42e3c0ef7ff377093cb"></a>
### 계산 · MET\_7247a104df8d595166151240aa0976741dd6f921fad2875719dd1703a30f63bb

- 직전 관측치 대비 변화: 1.062 index; 방법: previous\_change\_v1.
- 입력: [195](#opportunity-9a80737d20585ec1269bc790495de0fed65545075370ea8c3521ca28c4b278b2), [191](#opportunity-95bedb1a82c5878057b021e4a5c4f230fef156a43501a4a876ebc05790043af8).
- 공식: current\_value - exact\_reference\_value; 기간: (datetime.date(2026, 7, 1), datetime.date(2026, 8, 1)).
- 한계: Decimal precision 50; ROUND\_HALF\_EVEN
- 한계: 결측 보간/forward-fill 없음

<a id="opportunity-b29e24195449b0574b6e5ca012d1403a0452caa1706063ab7346744920e1faf0"></a>
### 계산 · MET\_90a8d4839d48fc7c68c2f87e44b6f72103a5d10788106159258755dd4e4241a6

- 직전 관측치 대비 변화: -0.05 percentage\_points; 방법: previous\_change\_v1.
- 입력: [200](#opportunity-620a418a6a6a4261843c24ff2333f800efb7980ab22c9104b60985e7cf50d542), [192](#opportunity-5ea22e484d99243f2bb8980ada756a7d00bce7b1b4889faa97d70aea979fa23f).
- 공식: current\_value - exact\_reference\_value; 기간: (datetime.date(2026, 9, 30), datetime.date(2026, 10, 1)).
- 한계: Decimal precision 50; ROUND\_HALF\_EVEN
- 한계: 결측 보간/forward-fill 없음

<a id="opportunity-382c29498ffb6f0358d4acfe579aa662e2f259a751f424e51832aae889efc472"></a>
### 계산 · MET\_dd01d9266cf889992b68081227261c67ceb3d8288bf66027e93f1eb92a07e2b1

- 직전 관측치 대비 변화: -0.10 percentage\_points; 방법: previous\_change\_v1.
- 입력: [194](#opportunity-5a1bbe31a9d75c92a98131627c8ff42ab446c1975e586ce9f3c3dcde13fae4ee), [199](#opportunity-c3102ca23240ec811e5b5ff6760356c8ed7b4238555d745fa8db8fec64fc2998).
- 공식: current\_value - exact\_reference\_value; 기간: (datetime.date(2026, 9, 30), datetime.date(2026, 10, 1)).
- 한계: Decimal precision 50; ROUND\_HALF\_EVEN
- 한계: 결측 보간/forward-fill 없음

<a id="opportunity-5618befcb710300272b26f6475dd43e6a660730d6cc8d783954c21e964533f7a"></a>
### 계산 · MET\_1c12f1a36b5cd83d7b0657b2f182ff78a607bc847dfd42e1a730af9228f05696

- 전년 동월 대비 물가 상승률: 3.3965478924364767760574857396844210682272760945300 percent; 방법: yoy\_v1.
- 입력: [196](#opportunity-d0e7fa100a289ad973f2cb6a8f55eb7f3fe3589b84a75556fe877920dc8cbc59), [191](#opportunity-95bedb1a82c5878057b021e4a5c4f230fef156a43501a4a876ebc05790043af8).
- 공식: (index\_t / index\_t\_minus\_12\_months - 1) \* 100; 기간: (datetime.date(2025, 8, 1), datetime.date(2026, 8, 1)).
- 한계: Decimal precision 50; ROUND\_HALF\_EVEN
- 한계: 결측 보간/forward-fill 없음
- 한계: 중간 1개월 결측 보존; YoY는 정확한 두 endpoint만 사용

<a id="opportunity-18aa94b2b2dae271a98b82e3201a7eab89db5e458a82fa7a93a11f02487f19a2"></a>
### 계산 · MET\_bfc3d24a8164e42e009d92cc338ef4bd50c822b5316d1c814e352e6d7cd28ef2

- 전월 대비 물가 상승률 변화: 0.0317228509565728608498385788909786076641399661500 percentage\_points; 방법: inflation\_trend\_v1.
- 입력: [193](#opportunity-72378b2cfe6e2c4037026eae05cebe253852fd77054ab86d9263137b0d9d2b94), [196](#opportunity-d0e7fa100a289ad973f2cb6a8f55eb7f3fe3589b84a75556fe877920dc8cbc59), [195](#opportunity-9a80737d20585ec1269bc790495de0fed65545075370ea8c3521ca28c4b278b2), [191](#opportunity-95bedb1a82c5878057b021e4a5c4f230fef156a43501a4a876ebc05790043af8).
- 공식: YoY\_t - YoY\_t\_minus\_1\_month; 기간: (datetime.date(2025, 7, 1), datetime.date(2025, 8, 1), datetime.date(2026, 7, 1), datetime.date(2026, 8, 1)).
- 한계: Decimal precision 50; ROUND\_HALF\_EVEN
- 한계: 결측 보간/forward-fill 없음
- 한계: 중간 1개월 결측 보존; YoY는 정확한 두 endpoint만 사용
- 한계: 중간 1개월 결측 보존; YoY는 정확한 두 endpoint만 사용

<a id="opportunity-71234770993cb69807fc7e17d8c76582d678a87c1c77d29c8a2a2e923781d35c"></a>
### 계산 · MET\_a749600fc2417f7947dd9707f7f649720288955ab9156a291e6864046262f402

- 10년−2년 국채 수익률 차이: 0.46 percentage\_points; 방법: yield\_spread\_v1.
- 입력: [192](#opportunity-5ea22e484d99243f2bb8980ada756a7d00bce7b1b4889faa97d70aea979fa23f), [199](#opportunity-c3102ca23240ec811e5b5ff6760356c8ed7b4238555d745fa8db8fec64fc2998).
- 공식: yield\_10y\_t - yield\_2y\_t; 기간: (datetime.date(2026, 10, 1),).
- 한계: Decimal precision 50; ROUND\_HALF\_EVEN
- 한계: 결측 보간/forward-fill 없음

<a id="opportunity-b58e8146c3c11a468b052598ec28d4d4245f3b8062ded3f8fac26e856cf977ca"></a>
### 계산 · CALC\_SP\_FORWARD\_EY

- FactSet rolling forward earnings yield: 5.2631578947368421052631578947368421052631578947368 percent; 방법: earnings\_yield\_v1.
- 입력: [162](#opportunity-73093f50e5b3d2718365e594b3c901b424a5a91656c007228969c8c7be809404).
- 공식: 100 / P/E.
- 한계: 추정 이익을 가격으로 나눈 값이며 배당·현금 지급률·실현 투자수익률이 아니다.
- 한계: 미래 이익의 반복성과 추정치의 정확성은 별도 검토다.

<a id="opportunity-6392e49e97de10002b6547bb11a22687d01193c152beb50725903e4859f6e1ce"></a>
### 계산 · CALC\_SP\_FY1\_EY

- State Street FY1 harmonic P/E 역수: 4.8947626040137053352912383749388154674498286833089 percent; 방법: earnings\_yield\_v1.
- 입력: [163](#opportunity-4dbefb1cf006d981bd4fd4206ef0b8a1c5ec7f22d38f072413b56716004514bc).
- 공식: 100 / P/E.
- 한계: 종목별 harmonic P/E의 역수이며 FactSet rolling forward earnings 정의와 동일하지 않다.

<a id="opportunity-fe11a56442357956e579d8861fc4b4db6a280cbe3d3089ca595bee693ed2cd01"></a>
### 계산 · CALC\_SP\_TRAILING\_EY

- State Street trailing P/E 역수: 4.0617384240454914703493095044679122664500406173842 percent; 방법: earnings\_yield\_v1.
- 입력: [167](#opportunity-a95b45c29e1d85ad6b1c1a027d44707f2c232e4955982fdb151d07e2afb26a0a).
- 공식: 100 / P/E.
- 한계: 과거 회계 이익의 가격 대비 값이다. 미래 현금 수익률이나 저평가 판정이 아니다.

<a id="opportunity-88fc03b5bc68f014753d8b86df9047b3266294f599424bf045ff05c26682a319"></a>
### 계산 · CALC\_MSFT\_Q4\_CASH\_RESIDUAL

- Microsoft OCF 차감 현금 PP&amp;E 잔여: 19639 USD\_million; 방법: cash\_residual\_v1.
- 입력: [137](#opportunity-71fd39dc85c150853a1e5a60fcb87130b2c0ab60a5ebf921c45895ceb6f5d849), [135](#opportunity-c1f2a0ed63a34b3fffc1d6a0db03484fc8a8358c9c7012ffd8e8809c530a4aba).
- 공식: 영업현금흐름 + 음수로 기록된 현금 PP&amp;E 지출.
- 한계: 현금 PP&amp;E 기준 잔여다. 리스 포함 총 CAPEX·세부 AI FCF·고객 ROI와 동일하지 않다.

<a id="opportunity-78befe9bced2f80b6e8d6e29a584e9b7e8cf7718a5376fd650eb3414c54ac0f7"></a>
### 계산 · CALC\_MSFT\_Q3\_CASH\_RESIDUAL

- Microsoft 이전 분기 OCF 차감 현금 PP&amp;E 잔여: 15803 USD\_million; 방법: cash\_residual\_v1.
- 입력: [133](#opportunity-12e23f701fcb503535ad306522457922705dcf6b17596d0c1a02140ae2782f9d), [132](#opportunity-61bd1a6d733adba9dd6390d1698abc1bd63edac87da8a673186b5372ac760fe5).
- 공식: 영업현금흐름 + 음수로 기록된 현금 PP&amp;E 지출.
- 한계: 현금 PP&amp;E 기준 잔여이며 완전한 AI 투자 회수 지표가 아니다.

<a id="opportunity-9cd65ef6fb7edc8563900ab8602b43cc3031487e3992aad0915a6026f5d0842d"></a>
### 계산 · CALC\_SP\_FORWARD\_10Y\_GAP

- rolling forward earnings yield 차감 같은 날 십 년 Treasury: -0.0268421052631578947368421052631578947368421052632 percentage\_points; 방법: descriptive\_yield\_gap\_v1.
- 입력: [162](#opportunity-73093f50e5b3d2718365e594b3c901b424a5a91656c007228969c8c7be809404), [169](#opportunity-68019a948c8c8c365ce41622e139d3f5c886e032164f2180cc56f3d135149b8e).
- 공식: 100 / P/E - 같은 관측일 nominal CMT Treasury yield.
- 한계: 단순 정의상 차이이며 Equity Risk Premium·미래 초과수익·배분 기준이 아니다.
- 한계: 이익 성장·유보와 재투자·부채·세금·불확실성·회계 질이 Treasury 약정 현금흐름과 다르다.

<a id="opportunity-1e6a870c2879f8b6a479255711ad8cc84c7edb3f5addd9ae3584cae0e1e3f1be"></a>
### 계산 · CALC\_SP\_FY1\_10Y\_GAP

- FY1 harmonic P/E 역수 차감 같은 날 십 년 Treasury: -0.3452373959862946647087616250611845325501713166911 percentage\_points; 방법: descriptive\_yield\_gap\_v1.
- 입력: [163](#opportunity-4dbefb1cf006d981bd4fd4206ef0b8a1c5ec7f22d38f072413b56716004514bc), [168](#opportunity-f00e945ee8a304602c6248939d5468e27794d7fdc1fd0ecb3be3ab52a5b921ef).
- 공식: 100 / P/E - 같은 관측일 nominal CMT Treasury yield.
- 한계: 동일 날짜에만 비교한 설명용 차이다. 주식 총수익률이나 정의된 model-implied ERP가 아니다.
- 한계: 다른 forward EPS 정의의 차이를 같은 시점의 추세로 해석하지 않는다.

### 무결성·접근 진단

- DD\_IDX\_FACTSET\_Q3: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_IDX\_FACTSET\_Q3: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- DD\_IDX\_FACTSET\_Q3: freshness=fresh; age assessed against source-specific 14-day limit; not a truth score
- DD\_IDX\_FACTSET\_Q2\_START: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_IDX\_FACTSET\_Q2\_START: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- DD\_IDX\_FACTSET\_Q2\_START: freshness=fresh; age assessed against source-specific 180-day limit; not a truth score
- DD\_IDX\_FACTSET\_Q2\_QUALITY: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_IDX\_FACTSET\_Q2\_QUALITY: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- DD\_IDX\_FACTSET\_Q2\_QUALITY: freshness=fresh; age assessed against source-specific 150-day limit; not a truth score
- DD\_IDX\_FACTSET\_Q1: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_IDX\_FACTSET\_Q1: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- DD\_IDX\_FACTSET\_Q1: freshness=fresh; age assessed against source-specific 190-day limit; not a truth score
- DD\_IDX\_SPY: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_IDX\_SPY: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- DD\_IDX\_SPY: freshness=unknown; publication date is unknown; retrieval is not publication; age assessed against source-specific 14-day limit; not a truth score
- DD\_MSFT\_Q4: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_MSFT\_Q4: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- DD\_MSFT\_Q4: freshness=fresh; age assessed against source-specific 120-day limit; not a truth score
- DD\_MSFT\_Q3: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_MSFT\_Q3: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- DD\_MSFT\_Q3: freshness=fresh; age assessed against source-specific 200-day limit; not a truth score
- DD\_AMZN\_Q2: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_AMZN\_Q2: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- DD\_AMZN\_Q2: freshness=fresh; age assessed against source-specific 120-day limit; not a truth score
- DD\_AMZN\_Q2\_OPERATING: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_AMZN\_Q2\_OPERATING: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- DD\_AMZN\_Q2\_OPERATING: freshness=fresh; age assessed against source-specific 120-day limit; not a truth score
- DD\_META\_Q2: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_META\_Q2: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- DD\_META\_Q2: freshness=fresh; age assessed against source-specific 120-day limit; not a truth score
- DD\_META\_Q1: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_META\_Q1: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- DD\_META\_Q1: freshness=fresh; age assessed against source-specific 200-day limit; not a truth score
- DD\_GOOGL\_Q2: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_GOOGL\_Q2: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- DD\_GOOGL\_Q2: freshness=fresh; age assessed against source-specific 120-day limit; not a truth score
- DD\_NVDA\_Q2: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_NVDA\_Q2: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- DD\_NVDA\_Q2: freshness=fresh; age assessed against source-specific 120-day limit; not a truth score
- DD\_TR\_H15\_CURVE: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_TR\_H15\_CURVE: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- DD\_TR\_H15\_CURVE: freshness=fresh; age assessed against source-specific 10-day limit; not a truth score
- DD\_COM\_GOOGLE\_LOSS: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_COM\_GOOGLE\_LOSS: freshness=fresh; age assessed against source-specific 30-day limit; not a truth score
- DD\_COM\_CAPEX\_NEVER: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_COM\_CAPEX\_NEVER: freshness=fresh; age assessed against source-specific 30-day limit; not a truth score
- DD\_COM\_REAL\_PROFITS: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_COM\_REAL\_PROFITS: freshness=fresh; age assessed against source-specific 30-day limit; not a truth score
- DD\_COM\_PRICED\_SPENDING: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_COM\_PRICED\_SPENDING: freshness=fresh; age assessed against source-specific 30-day limit; not a truth score
- DD\_COM\_TREASURY\_RISK: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_COM\_TREASURY\_RISK: freshness=fresh; age assessed against source-specific 30-day limit; not a truth score
- DD\_COM\_REDDIT\_ACCESS: policy: robots policy disallows this source
- DD\_COM\_REDDIT\_ACCESS: freshness=unavailable; publication, observation and valid-as-of dates are unknown; retrieval is not publication
- DD\_COM\_STOCKTWITS\_ACCESS: excerpt: selected excerpts are absent; source changed or selectors are wrong: Q\_ACCESS\_NOT\_OBSERVED
- DD\_COM\_STOCKTWITS\_ACCESS: freshness=unavailable; publication, observation and valid-as-of dates are unknown; retrieval is not publication
- DD\_COM\_X\_ACCESS: policy: robots policy disallows this source
- DD\_COM\_X\_ACCESS: freshness=unavailable; publication, observation and valid-as-of dates are unknown; retrieval is not publication
- DD\_COM\_BOGLEHEADS\_ACCESS: policy: robots policy could not be reliably established
- DD\_COM\_BOGLEHEADS\_ACCESS: freshness=unavailable; publication, observation and valid-as-of dates are unknown; retrieval is not publication
- DD\_COM\_LOBSTERS\_ACCESS: policy: robots policy disallows this source
- DD\_COM\_LOBSTERS\_ACCESS: freshness=unavailable; publication, observation and valid-as-of dates are unknown; retrieval is not publication
- DD\_IDX\_NDX\_SCOPE: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- DD\_IDX\_NDX\_SCOPE: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- DD\_IDX\_NDX\_SCOPE: freshness=unknown; publication date is unknown; retrieval is not publication; publication, observation and valid-as-of dates are unknown; retrieval is not publication
- BLS\_CPI\_RELEASE: Full raw and normalized content were hashed at acquisition but are not retained; replay verifies retained excerpts and metadata, not the discarded full document.
- BLS\_CPI\_RELEASE: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- FED\_H15\_TREASURY: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- FED\_H10\_KRW: Text/HTML selectors match normalized visible document text; descriptive locator labels are supplied review metadata, not automatically verified paragraph identities.
- BLS M13 annual average excluded from monthly observations
- US\_CPI\_U\_HEADLINE\_NSA 2025-10-01: Data unavailable due to the 2025 lapse in appropriations
- BLS M13 annual average excluded from monthly observations
- US\_CPI\_U\_HEADLINE\_NSA: snapshot vintage is retrieval version; complete release/revision history unavailable
- US\_TREASURY\_NOMINAL\_2Y: snapshot vintage is retrieval version; complete release/revision history unavailable
- US\_TREASURY\_NOMINAL\_10Y: snapshot vintage is retrieval version; complete release/revision history unavailable
- USD\_KRW\_NOON\_REFERENCE: snapshot vintage is retrieval version; complete release/revision history unavailable
- DD\_IDX\_SPY: explicitly dated reported observation from the retained page; publication unknown and availability before retrieval unproven
