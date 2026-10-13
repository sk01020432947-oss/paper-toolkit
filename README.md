# paper-toolkit — 논문 연구·집필 도구 묶음 (Claude Code 플러그인)

논문의 기획 → 문헌 검색 → 학습 → 서지 관리 → 집필 → 퇴고 → 심사 대비 → 투고처 선택 → HWPX 제출까지를 돕는 Claude Code 스킬 21종과 에이전트 7종입니다. 맥과 윈도우에서 함께 씁니다.

## 설치 — 아래 글을 Claude Code에 붙여 넣기

상자 안의 글을 통째로 복사해서 Claude Code 대화창에 붙여 넣고 Enter를 누르세요. Claude가 설치하고 점검 결과까지 보여 줍니다.

```text
논문 도구 묶음 paper-toolkit을 내 Claude Code에 설치해 줘.

저장소: https://github.com/sk01020432947-oss/paper-toolkit

1. 터미널에서 아래 두 명령을 차례로 실행해.
   claude plugin marketplace add sk01020432947-oss/paper-toolkit
   claude plugin install paper-toolkit@paper-toolkit
   이미 설치돼 있다고 나오면 대신 이 두 명령으로 최신판으로 올려 줘.
   claude plugin marketplace update paper-toolkit
   claude plugin update paper-toolkit@paper-toolkit
2. 1번이 실패하면 저장소를 내 홈 폴더의 paper-toolkit 폴더로 git clone 한 다음,
   그 폴더에서 python3 skills/paper-start/scripts/ptk.py install 을 실행해.
   (윈도우에서 python3가 없으면 python)
3. 설치가 끝나면 설치된 폴더에서 ptk.py 파일을 찾아
   python3 <경로>/ptk.py doctor 를 실행하고 결과를 표로 정리해 줘.
4. 내 기존 스킬과 설정은 지우거나 덮어쓰지 마.
   프로그램 설치나 API 키가 필요한 항목은 설치하지 말고 목록만 알려 줘.
5. 마지막에 무엇이 설치됐는지 요약하고,
   "Claude Code를 다시 시작한 뒤 /paper-start 를 입력하세요"라고 안내해 줘.
```

설치가 끝나면 **Claude Code를 다시 시작하고 `/paper-start`를 입력**합니다. 논문 폴더와 위키 폴더를 한 번 정하면, 지금 상황에 맞는 스킬을 알려 줍니다.

- ZIP 파일로 받았거나 직접 입력해서 설치하려면: [INSTALL-PROMPT.md](INSTALL-PROMPT.md)
- Claude가 따르는 설치 절차 전문: [AGENT-INSTALL.md](AGENT-INSTALL.md)

## 사용 설명서

**[MANUAL.md](MANUAL.md)** 한 권에 다 있습니다. 설치, 상황별 시나리오 10개, 스킬 21종 사전, 자주 묻는 질문 순서입니다. GitHub 화면에서 바로 읽힙니다.

## 들어 있는 것 (v1.3)

| 단계 | 스킬 | 하는 일 |
|---|---|---|
| 출발 | `paper-start` | 환경 점검, 폴더 설정, 지금 상황에 맞는 스킬 안내 |
| 기획 | `paper-writing-order` | 논문이 안 써질 때. 넓은 주제 → 발췌독 → 인용문 3분류 → 뼈대 → 서론·결론 쌍 |
| 검색 | `ref-toolkit` | 레퍼런스 수집 도구 20여 종(Consensus, Elicit, Scite, RISS, KCI 등)을 상황별로 안내 |
| 검색 | `keris-academic-search` | RISS에서 국내 학위논문·학술지·연구보고서 검색 |
| 학습 | `paper-study` | 논문 PDF를 능동 회상과 파인만 재설명으로 공부하고 위키에 쌓기 |
| 기억 | `wiki-recall` | 쓰기 전에 내 위키·메모 폴더에서 쌓아 둔 노트 먼저 꺼내기 |
| 기억 | `weekly-review` | 파일 기록에 근거한 주간 연구 회고 |
| 서지 | `zotero` | 내 Zotero 서재를 읽기 전용으로 조회·진단·BibTeX 내보내기 |
| 자료 | `korean-law-search` | 법령·판례·조례 조회와 원고의 법 인용 검증 |
| 자료 | `notebooklm` | Google NotebookLM 연동 |
| 퇴고 | `humanize` · `humanize-korean` · `humanize-redo` | AI가 쓴 한글의 "AI 티" 40여 패턴 탐지·윤문 (에이전트 7종 동반) |
| 퇴고 | `toego-korean` | 사람이 쓴 한국어 글을 구조 → 문단 → 문장 순으로 퇴고 |
| 교정 | `korean-spell-check` · `korean-character-count` | 맞춤법·띄어쓰기 / 초록·양식 글자수 |
| 점검 | `reporting-guideline-router` | 연구 설계에 맞는 보고 지침(CONSORT, STROBE, PRISMA, SRQR, COREQ, TRIPOD+AI 등) 판정 |
| 심사 | `paper-critical-review` | Reviewer 2 관점의 모의 심사, 구조 감사, 주장 도전 원장 |
| 투고 | `kci-journal-finder` | KCI 등재지 2,888종에서 투고처 고르기. 게재료·심사료·마감·대학원생 감면 |
| 제출 | `read-hwp` · `hwpx-mouseco` | HWP·HWPX 읽기·변환 / 공공문서 HWPX 보고서 생성 |

함께 든 것은 다음과 같습니다.

| 폴더·파일 | 내용 |
|---|---|
| `agents/` | humanize용 에이전트 7종 |
| `tools/KBG-PAPER-A.html` | PLS-SEM 분석기(HTML 파일 하나, 데이터는 내 컴퓨터에서만 처리)와 매뉴얼 |
| `pandoc/` | 옵시디언 md → Word 변환 때 Zotero 인용 살리기 |
| `install.sh` · `install.ps1` | 복사 설치(맥·리눅스) / 윈도우용 프로그램·pip·MCP 일괄 설치 |
| `MANUAL.html` | 사용 설명서의 HTML판. 파일 하나라 메신저로 보내기 좋습니다 |

## 함께 쓰면 좋은 것 (선택)

| 무엇 | 설치 | 쓰는 곳 |
|---|---|---|
| ARS 플러그인 | `claude plugin marketplace add Imbad0202/academic-research-skills` 다음 `claude plugin install academic-research-skills@academic-research-skills` | 개요, 초안, 인용 검증, 다관점 심사, 심사평 대응 (`/ars-*` 16개). CC BY-NC 4.0 |
| korean-law MCP | `claude mcp add korean-law -e LAW_OC=<발급키> -- npx -y --ignore-scripts --omit=optional korean-law-mcp@latest` | `korean-law-search`. 키는 open.law.go.kr에서 무료 발급 |
| RISS API 키 | riss.kr/apicenter (대학·비영리 기관에 발급) | `keris-academic-search` |
| Zotero, kordoc, Pandoc, lxml | `/paper-start`의 점검표가 필요한 것과 설치 방법을 알려 줍니다 | 서지, HWP, Word 변환 |

## 이 저장소에 넣지 않은 것

| 스킬 | 이유 / 출처 |
|---|---|
| `hwpxskill` | 라이선스 미표기. https://github.com/jkf87/hwpx-skill |
| `kosis-stats` · `public-data-finder` · `national-assembly-tracker` · `deep-research-pro` | 원 출처 표기 문서 누락. 원 제작자에게 직접 받으세요 |
| `deep-interview` | 출처 불명 |
| `anthropic-skills` (baksapaper, phd-dissertation) | Claude 앱 쪽 클라우드 플러그인. 각자 계정에서 켭니다 |
| KCI 학술지 데이터 | 논문완주연구소(nonwan-kci.netlify.app) 자료. 배포본에 넣지 않고 첫 실행 때 내려받습니다 |

## 라이선스와 출처

- 다른 분이 만든 스킬은 원 라이선스(MIT)와 출처를 따릅니다. 목록은 [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)에 있습니다.
- 나머지(`paper-start`, `paper-writing-order`, `paper-study`, `paper-critical-review`, `zotero`, `ref-toolkit`, `reporting-guideline-router`, `kci-journal-finder`, `wiki-recall`, `weekly-review`, `toego-korean`)는 따로 라이선스를 걸지 않은 개인 제작물입니다. 비상업적 연구·교육 목적으로 자유롭게 쓰고 고치세요.
- 모든 스킬에 공통된 원칙: 인용, 통계 수치, 법 조문은 원문을 직접 확인합니다.

## 변경 이력

- **v1.3.0 (2026-10-14)**: 붙여넣기 설치문과 설치 절차서(`INSTALL-PROMPT.md`, `AGENT-INSTALL.md`) · `paper-start` 추가(점검·설정·길 안내, 공용 도우미 `ptk.py`) · `wiki-recall`과 `weekly-review`를 개인 볼트 전제 없이 누구나 쓰게 다시 씀 · 공용 설정 파일(`~/.config/paper-toolkit/config.json`) · 스크립트 경로를 `${CLAUDE_SKILL_DIR}`로 통일 · 스킬 본문의 개인 경로·개인 서재 정보 제거 · `install.ps1`이 본문의 `~` 기호를 바꿔 버리던 버그 수정 · 복사 설치 때 기존 스킬 백업 · v1.1 HTML 안내서 4종은 내용이 낡아 뺌(사용 설명은 `MANUAL.md`·`MANUAL.html`로 통합)
- v1.2.0 (2026-10-05): `kci-journal-finder` 추가 · `paper-critical-review` 강화 · `korean-law-search` v2 · 맥 지원 · 매뉴얼집 `MANUAL.md`
- v1.1.0 (2026-09-03): 스킬 4종 추가, 박사과정생용 HTML 안내서
- v1.0.0: 최초 공개
