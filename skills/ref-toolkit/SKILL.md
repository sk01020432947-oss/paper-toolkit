---
name: ref-toolkit
description: 박사논문 레퍼런스 수집 도구 안내·라우팅 스킬. 사용자가 "레퍼런스 수집", "문헌 검색 도구", "Consensus/Elicit/SciSpace 뭐 쓸까", "논문 자료 조사 도구", "/ref-toolkit"을 요청하면 발동. 상황(질문형 탐색/체계적 고찰/국내 문헌/원문 확보/서지 정리)에 맞는 도구와 순서를 추천한다.
---

# ref-toolkit — 레퍼런스 수집 도구 라우터

## 상황별 라우팅

| 사용자 상황 | 1순위 | 보조 |
|---|---|---|
| "~가 효과 있나?" 질문형 탐색 | Consensus (무료) | Perplexity 학술 모드 |
| 체계적 문헌고찰·PRISMA | Scopus/WoS (기관, 검색식 기록) | RISS 병행 |
| 문헌 스노우볼링·지형 파악 | Research Rabbit (무료, Zotero 동기화) | Connected Papers |
| 논문 표 추출·비교 매트릭스 | Elicit (무료~Plus $12) | SciSpace |
| 난해한 PDF 독해 | SciSpace Copilot | — |
| 핵심 인용 반박 여부 검증 | Scite ($20/월) | — |
| 국내 학위논문 | RISS → 국회도서관 | — |
| 국내 학술지 원문 | DBpia (기관) | KISS, KCI |
| 등재지·피인용 확인 | KCI | WoS(SSCI) |
| 원문 확보 실패 시 | 도서관 프록시 → Unpaywall → RISS 원문복사(ILL) | EndNote Click |
| 서지 정리·인용 | Zotero (단일 허브 원칙) | Better BibTeX → Obsidian |
| 자동 수집·모니터링 | OpenAlex API, Scholar 알림 | Semantic Scholar API |

## 운영 원칙 (답변 시 항상 반영)

1. **유료 결제는 마지막** — 기관 구독 + 무료 도구로 90% 해결. 유료 우선순위: Elicit Plus > SciSpace 연간 > Scite.
2. **Zotero 단일 허브** — 어떤 도구든 서지는 Zotero 한 곳으로. RIS 발견 즉시 반입.
3. **AI 추출값은 원문 대조** — 숫자·효과크기·표본 수는 인용 전 반드시 확인.
4. **체계적 고찰은 AI 검색 불가** — 재현성 때문에 본 검색은 Scopus/WoS/RISS, AI는 보조.
5. **국내·해외 이중 트랙** — 검색어를 따로 설계 (번역어 여러 벌).

## 가격·기능 확인

위 표의 가격과 무료 범위는 2026-08 기준이다. 결제를 권하기 전에 WebSearch로 지금 가격을 확인하고 "YYYY-MM 기준"이라고 밝힌다.

## 이어지는 스킬

- 서지를 Zotero에 담은 뒤의 조회·진단은 `zotero` 스킬.
- 국내 학위논문·학술지 검색 실행은 `keris-academic-search` 스킬.
- 투고할 학술지 고르기는 `kci-journal-finder` 스킬.
