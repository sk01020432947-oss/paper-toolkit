---
name: zotero
description: 사용자의 로컬 Zotero 라이브러리(~/Zotero)를 직접 조회·진단·내보내기 하는 스킬. 논문 연구 중 "내 조테로에서 찾아줘", "참고문헌 몇 편이야", "서지정보 진단", "BibTeX 뽑아줘", "그 논문 PDF 읽어줘", "중복 정리", "메타데이터 없는 PDF", "인용 가능한지 확인", "참고문헌 목록 만들어줘", "KCI 기준 충족하는지" 같은 요청이 나오거나, 사용자가 자기 서재/라이브러리/조테로/Zotero를 언급하며 문헌을 찾거나 참고문헌 작업을 할 때 발동한다. 논문 집필(paper-writing-order), 논문 학습(paper-study), 논문 심사(paper-critical-review) 스킬과 함께 쓰인다. 읽기 전용이므로 사용자의 Zotero 데이터를 손상시키지 않는다.
---

# Zotero 로컬 라이브러리 연동

사용자의 Zotero 라이브러리를 SQLite에서 직접 읽는다. **Zotero 실행 여부와 무관**하고,
DB를 임시 폴더로 복사해 읽기 전용으로 열기 때문에 **원본을 절대 수정하지 않는다.**

## 실행 방법

```
python3 "${CLAUDE_PLUGIN_ROOT}/skills/zotero/scripts/zotlib.py" <명령>
```

Windows에서 한글 출력이 깨지면 `$env:PYTHONIOENCODING="utf-8"` 를 먼저 설정한다.
파이썬은 맥·리눅스 `python3`, 윈도우 `python`.

## 명령

| 명령 | 용도 |
|---|---|
| `stats` | 라이브러리 개요 — 항목 수, 타입별, 한글/외국어 비율 |
| `collections` | 컬렉션 트리 + 각 컬렉션의 서지 항목 수 |
| `search <검색어> [-c ID] [-n 30]` | 제목·저자·초록·학술지명 검색 |
| `list [-c ID] [-n 50]` | 항목 목록 (연도 역순) |
| `show <itemID\|key>` | 항목 상세 + 첨부 PDF 실제 경로 |
| `diag [-c ID]` | **서지 품질 진단** — 인용 가능 비율, 필드 결손, 중복, 최근5년 비율 |
| `orphans [-n 300]` | 부모 서지항목 없는 PDF (인용 불가 상태) |
| `dups [-c ID]` | 중복 후보 |
| `bib [-c ID] [-o 파일]` | BibTeX 내보내기 |
| `csv [-c ID] [-o 파일]` | 표 내보내기 |
| `pdf <itemID>` | 해당 항목 PDF의 절대 경로 (→ Read 도구로 바로 읽을 수 있음) |
| `pdfs [-c ID]` | PDF 전체 경로 목록 |

모든 명령에 `--json` 을 붙이면 기계 판독용 출력이 된다. 결과를 가공해야 할 때 쓴다.

## 작업 원칙

**논문 본문을 읽어야 할 때**는 `pdf <itemID>` 로 경로를 얻은 뒤 Read 도구로 그 경로를 읽는다.
PDF를 찾겠다고 파일 시스템을 뒤지지 않는다 — storage 폴더는 8자리 키로 되어 있어 사람이 못 찾는다.

**참고문헌 편수를 묻는 질문**에는 `stats`가 아니라 `diag`를 쓴다.
전체 항목 수보다 "인용 가능한 항목 수"(저자·연도·제목이 모두 있는 것)가 실제 답이다.

**BibTeX가 필요할 때**는 Better BibTeX 자동 export 파일이 있으면 그것을 먼저 쓴다
(`~/Documents/research/refs.bib`). 없을 때만 `bib` 명령으로 생성한다.
BBT가 생성한 인용키가 정본이고, 이 스크립트의 키는 대체품이다.

**쓰기 작업은 하지 않는다.** 항목 추가·수정·삭제·병합은 전부 Zotero GUI에서 사용자가 한다.
필요한 변경은 무엇을 어디서 눌러야 하는지 안내하고, 반영된 뒤 다시 조회해 확인한다.

## 메타데이터 복구

서지정보 없는 독립 PDF가 있으면 `zrecover.py`로 후보 메타데이터를 찾는다.

```
python3 "${CLAUDE_PLUGIN_ROOT}/skills/zotero/scripts/zrecover.py" scan       # 대상 목록
python3 "${CLAUDE_PLUGIN_ROOT}/skills/zotero/scripts/zrecover.py" match -n 40
python3 "${CLAUDE_PLUGIN_ROOT}/skills/zotero/scripts/zrecover.py" export -o <폴더>
```

- 조회 순서는 한글 파일명이면 KCI → Crossref → OpenAlex, 그 외는 Crossref → OpenAlex → KCI.
- **KCI 백엔드는 `KCI_API_KEY` 환경변수가 있어야 작동한다.** 없으면 조용히 건너뛴다.
- 실측 적중률: 키 없이 한글 논문 대상 약 12%(8건 중 1건). KCI 키가 있어야 쓸 만해진다.
- 순서상 **Zotero 내장 "PDF 메타데이터 가져오기"를 먼저 돌리게 한 뒤** 남은 것에 쓴다.
  내장 기능은 기존 PDF에 제자리로 메타데이터를 붙이지만, RIS 가져오기는 새 항목을 만든다.

## 현재 라이브러리 (2026-07-29 실측)

- 데이터 폴더 `~/Zotero`, Zotero 8.0.4
- 서지 항목 34건 / 그중 **인용 가능 14건(41%)** / 독립 첨부 **270건**
- 주 연구 컬렉션: `다문화 인권교육 박사학위 논문` (id=4, 서지 22 / 전체 267)
- 기타 컬렉션: `설교준비`(id=1), `글쓰기`(id=2), `AI논문작성 강의`(id=3)

이 수치는 사용자가 정리 작업을 하면 바뀐다. **답변 전 항상 `diag`를 실행해 최신 상태를 확인**하고,
위 숫자를 그대로 인용하지 않는다.

## 참고

설치·설정 절차(Better BibTeX, 자동 export, 로컬 API, KCI 키 발급)는
[references/setup.md](references/setup.md) 참조.
