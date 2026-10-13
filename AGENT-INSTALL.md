# 설치 절차서 (Claude Code가 읽고 실행하는 문서)

사용자가 "paper-toolkit 설치해줘"라고 했을 때 Claude Code가 따르는 절차다. 사람이 직접 따라 해도 된다.

## 지킬 것

- 사용자의 기존 스킬·에이전트·설정을 지우거나 덮어쓰지 않는다. 이름이 겹치면 건너뛰고 보고한다.
- 이 절차서에 적힌 것만 설치한다. 프로그램(Zotero, Node.js, Pandoc 등)과 다른 플러그인은 사용자가 고른 것만, 무엇을 설치하는지 말하고 동의를 받은 뒤 설치한다.
- API 키를 대화에 붙여 넣으라고 요청하지 않는다. 발급 주소와 넣을 곳만 알려 준다.
- 명령이 실패하면 오류 문구를 그대로 보여 주고 다음 방법으로 넘어간다. 성공한 척하지 않는다.

## 1단계. 지금 상태 확인

```bash
claude --version
claude plugin list
```

`paper-toolkit`이 이미 목록에 있으면 2단계 대신 **업데이트**를 한다.

```bash
claude plugin marketplace update paper-toolkit
claude plugin update paper-toolkit@paper-toolkit
```

`~/.claude/skills/` 안에 이 묶음과 같은 이름의 폴더(예: `paper-study`, `zotero`, `humanize-korean`)가 이미 있는지도 본다. 있으면 플러그인 것과 이름이 겹쳐 두 개가 보일 수 있다고 사용자에게 알린다. 지우지는 않는다.

## 2단계. 설치 (위에서부터 되는 방법 하나)

### 방법 A. 플러그인으로 설치 (권장)

```bash
claude plugin marketplace add sk01020432947-oss/paper-toolkit
claude plugin install paper-toolkit@paper-toolkit
```

사용자가 ZIP으로 받아 압축을 푼 폴더로 설치할 때는 **방법 B(복사 설치)를 쓴다.** 폴더 경로로 방법 A를 쓰면 플러그인이 복사되지 않고 그 폴더에서 바로 읽히기 때문에, 사용자가 나중에 그 폴더를 옮기거나 지우면 스킬이 모두 사라진다.

`claude plugin` 명령이 없는 옛 버전이면 사용자에게 Claude Code 대화창에 아래 두 줄을 직접 입력해 달라고 한다.

```
/plugin marketplace add sk01020432947-oss/paper-toolkit
/plugin install paper-toolkit@paper-toolkit
```

### 방법 B. 복사 설치 (방법 A가 안 될 때)

저장소를 받는다. ZIP을 이미 풀어 두었으면 이 줄은 건너뛰고, 아래 명령의 `~/paper-toolkit` 자리에 푼 폴더 경로를 쓴다. 푼 폴더는 `skills` 폴더와 `README.md`가 바로 보이는 폴더여야 한다. 한 겹 더 들어가 있으면 안쪽 폴더를 쓴다.

```bash
git clone https://github.com/sk01020432947-oss/paper-toolkit ~/paper-toolkit
```

받은 폴더에서 설치한다. 윈도우에서 `python3`가 없으면 `python`이나 `py -3`을 쓴다.

```bash
python3 ~/paper-toolkit/skills/paper-start/scripts/ptk.py install
```

스킬 21개는 `~/.claude/skills/`에, 에이전트 7개는 `~/.claude/agents/`에 복사된다. 같은 이름이 이미 있으면 건너뛴다. 사용자가 덮어쓰기를 원한다고 분명히 말했을 때만 `--force`를 붙인다. 이때 기존 것은 `~/.claude/backup-paper-toolkit-<시각>/`으로 옮겨진다.

## 3단계. 점검

설치된 `ptk.py`를 찾아 점검을 실행한다.

- 방법 A로 설치했으면 `~/.claude/plugins/` 아래에서 `ptk.py`를 찾는다.
  - 맥·리눅스: `find ~/.claude/plugins -name ptk.py | head -1`
  - 윈도우 PowerShell: `Get-ChildItem "$env:USERPROFILE\.claude\plugins" -Recurse -Filter ptk.py | Select-Object -First 1 -ExpandProperty FullName`
- 방법 B로 설치했으면 `~/.claude/skills/paper-start/scripts/ptk.py`다.

```bash
python3 "<찾은 경로>/ptk.py" doctor
```

결과를 표로 요약한다. ✅는 개수만, ➖는 "선택 사항"으로 항목·쓰는 곳·해결 방법을 보여 준다. ➖는 고장이 아니다. 그 스킬을 쓸 때만 필요하다.

## 4단계. 마무리 안내

사용자에게 다음을 알린다.

1. 설치한 방법(A 또는 B)과 설치된 스킬·에이전트 개수. 방법 A는 `claude plugin details paper-toolkit@paper-toolkit`로, 방법 B는 설치 명령의 출력으로 확인한다. 스킬 21개, 에이전트 7개가 정상이다.
2. 건너뛴 항목이 있으면 그 목록과 이유.
3. **Claude Code를 완전히 종료했다가 다시 시작한 뒤 `/paper-start`를 입력**하면 폴더 설정과 사용 안내가 이어진다는 것. (플러그인으로 설치했으면 `/paper-toolkit:paper-start`로 보일 수 있다.)
4. 사용 설명서는 저장소의 `MANUAL.md`라는 것.

## 함께 쓰면 좋은 것 (사용자가 원할 때만)

| 무엇 | 명령 | 쓰는 곳 |
|---|---|---|
| ARS 플러그인 | `claude plugin marketplace add Imbad0202/academic-research-skills` 다음 `claude plugin install academic-research-skills@academic-research-skills` | 개요, 초안, 인용 검증, 다관점 심사 (`/ars-*`). CC BY-NC 4.0 |
| korean-law MCP | `claude mcp add korean-law -e LAW_OC=<발급키> -- npx -y --ignore-scripts --omit=optional korean-law-mcp@latest` | 법령·판례 인용 검증. 키는 open.law.go.kr에서 무료 발급 |
| kordoc | `npm i -g kordoc` | HWP·HWPX 읽기 |
| lxml | `python3 -m pip install lxml` | HWPX 보고서 생성 |
| RISS API 키 | riss.kr/apicenter에서 발급 후 환경변수 `KSKILL_RISS_API_KEY` | RISS 검색 (대학·비영리 기관에만 발급) |
| 윈도우 프로그램 일괄 설치 | 저장소 폴더에서 `powershell -ExecutionPolicy Bypass -File .\install.ps1 -SkipSkills` | 아래 목록을 한꺼번에 설치한다. 실행 전에 목록을 사용자에게 보여 주고 동의를 받는다 |

`install.ps1`이 설치하는 것은 다음과 같다. 일부만 원하면 `-SkipWinget`, `-SkipPip`, `-SkipMcp`로 단계를 건너뛴다.

- 프로그램(winget) 8종: Zotero, Obsidian, Pandoc, Tesseract-OCR, PDF24 Creator, Python 3.12, Git, Node.js LTS
- Python 패키지(pip) 13종: ocrmypdf, markitdown, pyalex, habanero, arxiv, pymupdf, pypdf, pypdfium2, pandas, scipy, networkx, ruamel.yaml, master-of-hwp
- MCP 서버 3종: kordoc, mohwp, public-data-lens

## 제거

```bash
claude plugin uninstall paper-toolkit@paper-toolkit
claude plugin marketplace remove paper-toolkit
```

복사 설치였다면 `~/.claude/skills/`에서 이 묶음의 폴더 21개와 `~/.claude/agents/`의 에이전트 7개를 사용자에게 확인받고 지운다. 설정 파일은 `~/.config/paper-toolkit/config.json` 하나다. 사용자의 논문 폴더와 위키 폴더는 건드리지 않는다.
