---
name: ref-toolkit
description: 박사논문 레퍼런스 수집 도구 안내·라우팅 스킬. 사용자가 "레퍼런스 수집", "문헌 검색 도구", "Consensus/Elicit/SciSpace 뭐 쓸까", "논문 자료 조사 도구", "레퍼런스 대시보드", "/ref-toolkit"을 요청하면 발동. 상황(질문형 탐색/체계적 고찰/국내 문헌/원문 확보/서지 정리)에 맞는 도구를 추천하고, 레퍼런스 커맨드 센터 대시보드를 안내·갱신한다.
---

# ref-toolkit — 레퍼런스 수집 도구 라우터

## 정본 대시보드 (URL 재사용 필수)

- 아티팩트: `artifact-url.txt`의 URL을 **반드시 재사용**해 갱신한다 (신규 발행 금지).
- 로컬 정본이 필요하면 대시보드 HTML을 Documents에 저장 후 안내.

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

## 대시보드 갱신 절차

1. 가격·기능 변동을 WebSearch로 확인 (가격은 "YYYY-MM 기준" 명기).
2. 대시보드 HTML 수정 (도구 카드는 `data-cat`/`data-kw` 속성 유지 — 필터·검색이 이에 의존).
3. `artifact-url.txt`의 URL로 재발행 (favicon 📚 유지).

## 연계 자산

- 사용자의 Zotero×Obsidian×Pandoc 파이프라인 구축 완료 (research-pkm-pipeline 메모리 참조).
- OpenAlex 자동 수집은 AI×복지 위클리 뉴스레터에서 검증된 패턴.
