# paper-toolkit — 논문 연구·집필 도구 묶음 (Claude Code 플러그인)

논문의 기획 → 문헌 검색 → 학습 → 서지 관리 → 집필 → 퇴고 → 심사 대비 → HWPX 제출까지를 돕는 Claude Code 스킬 20종과 에이전트 7종, 데스크톱 프로그램 일괄 설치 스크립트, 그리고 박사과정생용 안내 문서를 한 저장소에 모았습니다.

> **📘 매뉴얼집: [MANUAL.md](MANUAL.md)** — 설치, 상황별 시나리오 10개, 스킬 20종 사전, FAQ를 GitHub 화면에서 바로 읽을 수 있습니다.
>
> v1.1 HTML 안내서(윈도우판): [phd-toolkit-guide.html](phd-toolkit-guide.html) (도구 총람 — 무엇이 있고 왜 쓰는가) → [INSTALL-GUIDE.html](INSTALL-GUIDE.html) (설치) → [phd-toolkit-manual.html](phd-toolkit-manual.html) (사용 매뉴얼 — 시나리오 9개 따라하기). GitHub 화면에서는 파일을 Raw로 저장한 뒤 브라우저로 여세요. 기술 명세는 [paper-toolkit-inventory.html](paper-toolkit-inventory.html).

## 설치 — Claude Code 안에서 2줄

```
/plugin marketplace add sk01020432947-oss/paper-toolkit
/plugin install paper-toolkit@paper-toolkit
```

Claude Code를 재시작하면 `/paper-writing-order`, `/humanize`, `/zotero` 등이 바로 뜹니다.
Claude Code에게 그냥 **"sk01020432947-oss/paper-toolkit 마켓플레이스 추가하고 paper-toolkit 플러그인 설치해줘"** 라고 말해도 됩니다.

### 함께 깔면 좋은 플러그인 (같은 방식, 선택)

```
/plugin marketplace add Imbad0202/academic-research-skills   → /plugin install academic-research-skills   # ARS: /ars-plan·/ars-lit-review·/ars-citation-check·/ars-reviewer 등 16 명령
/plugin marketplace add fivetaku/gptaku_plugins              → /plugin install deep-research               # 멀티에이전트 딥리서치
```

### 플러그인 없이 복사 설치 (맥·리눅스)

```bash
git clone https://github.com/sk01020432947-oss/paper-toolkit
bash paper-toolkit/install.sh        # 이미 있는 스킬은 건너뜀, 덮어쓰려면 -f
```

### 데스크톱 프로그램·MCP까지 (선택, 윈도우 PowerShell)

Zotero·Obsidian·Pandoc·OCR·Python 패키지·HWP MCP(kordoc/mohwp)·법령 MCP를 한 번에 깔려면:

```powershell
git clone https://github.com/sk01020432947-oss/paper-toolkit
cd paper-toolkit
powershell -ExecutionPolicy Bypass -File .\install.ps1 -SkipSkills
```

(`-SkipSkills`: 스킬은 이미 플러그인으로 들어왔으니 프로그램·pip·MCP·분석기 복사만 수행.) Claude Code에게 "이 저장소 clone해서 install.ps1 -SkipSkills 실행해줘"라고 시켜도 됩니다. 끝나면 화면에 남은 수동 작업(Ghostscript, Zotero 확장, API 키 등)이 출력됩니다 — 자세한 건 INSTALL-GUIDE.html 5~6절.

## 들어 있는 것 (v1.2)

| 구분 | 이름 | 역할 |
|---|---|---|
| 기획 | `paper-writing-order` | 논문이 안 써질 때 — 넓은 주제→발췌독→인용문 3분류→뼈대→서론·결론 쌍 5단계 코칭 |
| 검색 | `keris-academic-search` | RISS에서 국내 학위논문·학술지·연구보고서 검색 (MIT, NomaDamas/k-skill) |
| 투고 | `kci-journal-finder` | KCI 등재지 2,888종에서 투고처 고르기 — 게재료·심사료·마감·대학원생 감면(215종) (v1.2 신규, 자료: 논문완주연구소) |
| 검색 | `ref-toolkit` | 레퍼런스 수집 도구 26종(Consensus·Elicit·Scite·RISS·KCI…) 상황별 라우팅 |
| 학습 | `paper-study` | 남의 논문 PDF를 능동 회상·파인만 재설명으로 학습, 마크다운 위키에 축적 |
| 서지 | `zotero` | 로컬 Zotero 라이브러리를 SQLite로 직접 조회·진단·BibTeX 내보내기 (읽기 전용, MCP 불필요) |
| 심사 | `paper-critical-review` | Reviewer 2 관점의 적대적 심사·투고 전 약점 진단 |
| 점검 | `reporting-guideline-router` | 연구 설계에 맞는 보고 가이드라인(CONSORT·STROBE·PRISMA·SRQR·COREQ·TRIPOD+AI…) 판정·체크 |
| 퇴고 | `humanize-korean` · `humanize` · `humanize-redo` | AI가 쓴 한글의 "AI 티" 40+ 패턴 탐지·윤문 (에이전트 7종 동반) |
| 퇴고 | `toego-korean` | 사람이 쓴 한국어 글을 구조→문단→문장 순으로 고치는 퇴고 |
| 교정 | `korean-spell-check` · `korean-character-count` | 맞춤법·띄어쓰기 보수 교정 / 초록·양식 글자수 정밀 계산 (MIT) |
| 기억 | `wiki-recall` · `weekly-review` | 내 위키·옵시디언 볼트에서 선행 지식 회수, 주간 연구 회고 (볼트 경로 본인 것으로 수정 필요) |
| 자료 | `korean-law-search` | 국가법령 검색 (korean-law MCP 우선, 법망 폴백) — MIT |
| 자료 | `notebooklm` | Google NotebookLM 비공식 CLI 연동 (notebooklm-py, MIT) |
| HWP | `hwpx-mouseco` · `read-hwp` | 공공문서 HWPX 보고서 양식 생성 / kordoc으로 HWP·HWPX 읽기·변환 — MIT |
| 에이전트 | `agents/` 7종 | ai-tell-detector · korean-style-rewriter · content-fidelity-auditor · naturalness-reviewer · korean-ai-tell-taxonomist · taxonomy-gap-analyzer · humanize-monolith |
| 도구 | `tools/KBG-PAPER-A.html` | PLS-SEM 원클릭 분석기(단일 HTML, 데이터 로컬 처리) + 매뉴얼 |
| 설정 | `pandoc/` | 옵시디언 md → Word(docx) 변환 시 Zotero 인용 살리기 (`convert.ps1`, `zotero.lua`, 문헌노트 템플릿, 하이라이트 CSS) |
| 문서 | `phd-toolkit-guide.html` 외 | 도구 총람 · 사용 매뉴얼 · 설치 안내서 · 기술 명세 (HTML 4종) |
| 스크립트 | `install.ps1` · `install.sh` | 윈도우: 프로그램(winget)·pip·MCP 일괄 설치 / 맥·리눅스: 스킬·에이전트 복사 |

## 이 저장소에 넣지 않은 것 (라이선스 미확인 → 원 출처에서 설치)

| 스킬 | 이유 / 출처 |
|---|---|
| `hwpxskill` | 라이선스 미표기 — https://github.com/jkf87/hwpx-skill |
| `kosis-stats` · `public-data-finder` · `national-assembly-tracker` · `deep-research-pro` | 원 attribution 문서 누락(ClawHub 계열 적응본) — 필요 시 원 제작자에게 직접 받거나 ZIP 배포본 사용 |
| `deep-interview` | 출처 불명 |
| `anthropic-skills` (baksapaper·phd-dissertation) | Claude 앱 쪽 클라우드 플러그인 — 각자 계정에서 활성화 |

## 주의

- `zotero` 스킬은 Zotero 데이터 폴더를 `~/Zotero`(윈도우 `%USERPROFILE%\Zotero`, 기본값)로 가정합니다. 다를 때는 `--data-dir` 지정.
- `wiki-recall`·`weekly-review`는 원 제작자 볼트 구조 기준 — SKILL.md의 경로를 본인 볼트로 바꾸세요.
- `pandoc/My Library.yaml`(개인 서지)은 포함하지 않았습니다. Zotero → Export → Better CSL YAML(Keep updated)로 직접 생성.
- MIT 표기된 제3자 스킬(keris-academic-search·korean-spell-check·korean-character-count·korean-law-search·hwpx-mouseco·read-hwp·notebooklm 연동 대상)은 원 라이선스와 출처(NomaDamas/k-skill 등)를 따릅니다. 나머지는 별도 라이선스를 걸지 않은 개인 제작물 — 비상업적 연구·교육 목적으로 자유롭게 쓰세요. ARS 플러그인은 CC BY-NC 4.0.

## 변경 이력

- **v1.2.0 (2026-10-05)** — `kci-journal-finder` 추가 · `paper-critical-review`에 구조 감사 6항목·주장 도전 원장·FACT/SYNTHESIS 구분 · `korean-law-search` v2(MCP 도구 10종, 인용 검증) · `humanize-korean` 병렬 검증을 서브에이전트 방식으로 · 맥 지원(`install.sh`, 경로 정리, zotero 기본 폴더 버그 수정) · 매뉴얼집 `MANUAL.md`
- v1.1.0 (2026-09-03) — 스킬 4종 추가 + 박사과정생용 HTML 안내서
- v1.0.0 — 최초 공개

## 업데이트

```
/plugin marketplace update paper-toolkit
/plugin update paper-toolkit@paper-toolkit
```
