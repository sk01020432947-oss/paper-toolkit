---
name: korean-law-search
description: 한국 법령·조문·판례·해석례·자치법규(조례)·행정규칙 조회와 AI 글의 법 인용 검증에 korean-law MCP(v4.15, 도구 10개)를 쓴다. "OO법 제N조", "판례 찾아줘", "인용 맞는지 검증", "조례 상위법 개정 반영됐나", "과거 시점 법", "종교인소득·기부금·개인정보·통합돌봄 근거 조문" 요청 시 발동. MCP가 막히면 법망(api.beopmang.org)으로 폴백.
license: MIT
metadata:
  category: legal
  locale: ko-KR
  phase: v2
  updated: 2026-10-04
---

# Korean Law Search

`korean-law` MCP를 먼저 등록한다: `claude mcp add korean-law -e LAW_OC=<발급키> -- npx -y --ignore-scripts --omit=optional korean-law-mcp@latest` (키 발급: https://open.law.go.kr). 도구는 `mcp__korean-law__*`로 보인다. 지연 로딩이면 ToolSearch로 먼저 불러온다.


## 도구 선택 (v4.4 이후 구조)

| 필요 | 도구 |
|---|---|
| 법령·조례·고시 이름 → lawId/MST | `search_law` (약칭 자동 변환, 0건이면 자치법규·행정규칙 폴백) |
| 조문 본문 | `get_law_text(mst, jo="제21조")`, 과거 시점은 `efYd` |
| 별표·서식(과태료표·신청서) | `get_annexes(lawName, query/annexNo, date)` |
| 판례·헌재·해석례·행심·조세심판·국세청·공정위·노동위·개인정보위 | `search_decisions(domain=...)` → `get_decision_text` |
| 복합 질문 | `legal_research(task=full_research/law_system/action_basis/dispute_prep/amendment_track/ordinance_compare/procedure_detail/document_review)` |
| 인용 검증 / 판례 생사 / 행위시법 / 영향 그래프 | `legal_analysis(mode=verify_citations/cite_check/applicable_law/impact_map)` |
| 조례 상위법 개정 추적 | `ordinance_radar(ordinSeq=...)` |
| 그 밖의 전문 도구(용어, 신구대조, `search_law_bulk` 등) | `discover_tools` → `execute_tool` |

옛 이름(`search_precedents`, `search_interpretations`, `search_ordinance`, `search_all`, `chain_*`)은 `execute_tool` 경유로 하위호환만 된다. 새로 쓰지 않는다.

## 규칙

- 한국 법 관련 사실은 학습 지식으로 답하지 않고 먼저 조회한다. 최근 개정(예: 돌봄통합지원법 2026-09-10 시행)은 학습 자료에 없다.
- AI가 쓴 글(보고서·설교·칼럼·논문)에 조문·판례 인용이 있으면 내보내기 전에 `verify_citations`를 돌린다. `[HALLUCINATION_DETECTED]`가 나오면 "검증 완료"라고 말하지 말고 오류 인용을 명시한다.
- `verify_citations`는 법령은 항 단위까지만 본다. 호·목은 `get_law_text`로 원문 확인.
- `ordinance_radar`는 조례 이름으로 넣으면 첫 검색 결과를 잡아 엉뚱한 조례를 판정할 수 있다. `search_law`로 일련번호를 얻어 `ordinSeq`로 넘긴다. `[NO_PARENT]`면 조례 본문을 열어 근거법을 확인한다. "정비 검토 대상"은 신호일 뿐 정비 필요 판정이 아니다.
- `document_review`는 키워드 규칙 기반이다. 일방 해지·무과실 배상 같은 불공정 조항을 놓치고 법령을 잘못 짚을 수 있다(2026-10-04 실측). 계약서는 Claude가 조항별로 먼저 분석하고, 그 분석의 법 인용을 `verify_citations`로 검증한다.
- `[NOT_FOUND]`면 추측하지 말고 못 찾았다고 보고하고 다른 검색어·도메인을 시도한다.
- 결과에는 법령명·조문·시행일(또는 사건번호·선고일)을 붙인다. 법률 자문처럼 단정하지 않는다.

## 자주 쓰는 질문 (예시)

- 목회·교회행정: 종교인소득(소득세법 제21조 제1항 제26호, 제4항) + `search_decisions(domain="nts", query="종교인소득")`, 기부금영수증, 교인 개인정보(`domain="pipc"`), 종교시설 용도변경(`procedure_detail`).
- 사회복지·통합돌봄: 「의료ㆍ요양 등 지역 돌봄의 통합지원에 관한 법률」(MST 286733) 체계는 `law_system`, 전국 조례 비교는 `ordinance_compare`, 시설 처분기준은 `action_basis` + `get_annexes`.
- 지방행정·의회: 조례안 상위법 적합성은 `ordinance_compare(scenario=compliance)`, 회의록·예산은 `local-government` MCP와 함께, 정책 브리프는 `policy-brief` 스킬.

## 연결 정보

- 로컬 MCP 인자: `["-y","--ignore-scripts","--omit=optional","korean-law-mcp@latest"]`
- 원격(claude.ai·ChatGPT 커넥터): `https://mcp.gomdori.app/law?oc=<LAW_OC>` (옛 `korean-law-mcp.fly.dev`는 하위호환만)
- CLI: `npm i -g --ignore-scripts --omit=optional korean-law-mcp`, `export LAW_OC=...`, `korean-law "민법 제1조"`, `korean-law list`
- 키 발급: https://open.law.go.kr/LSO/openApi/guideList.do
- 폴백(법제처 경로 장애 시만): 법망 MCP `https://api.beopmang.org/mcp`, REST `https://api.beopmang.org/api/v4/law?action=search&q=관세법`

## Notes

- upstream: https://github.com/chrisryugj/korean-law-mcp
