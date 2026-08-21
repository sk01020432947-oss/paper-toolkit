# Zotero 연구 환경 설정 절차

작성 2026-07-29 · 대상 PC: Windows 11 / Zotero 8.0.4 / 데이터 폴더 `%USERPROFILE%\Zotero`

스크립트 연동(`zotlib.py`)은 **추가 설정 없이 이미 작동한다.** 아래는 그 위에 얹는 것들이다.

---

## 1. Better BibTeX 설치 — 자동 .bib 유지

Zotero 8에는 네이티브 인용키 필드가 생겨 BBT와의 관계가 한 번 정리됐다.
**BBT 8.0.x 계열이 Zotero 8 대응 버전**이므로 7.x 대 파일을 받지 않도록 주의한다.

1. https://retorque.re/zotero-better-bibtex/installation/ 에서 최신 `.xpi` 다운로드
   - 브라우저가 xpi를 열어버리면 링크 우클릭 → "다른 이름으로 저장"
2. Zotero → 도구(Tools) → 플러그인(Plugins)
3. 우측 상단 톱니 → **Install Plugin From File…** → 받은 `.xpi` 선택
4. Zotero 재시작
5. 최초 실행 시 전체 라이브러리 인용키 생성이 돌아간다 (수 분 소요)

설치 확인: 편집 → 설정(Settings)에 **Better BibTeX** 탭이 생기면 성공.

### 인용키 규칙 (설치 직후 반드시 설정)

Better BibTeX 탭 → Citation keys → Citation key formula:

```
auth.lower + year + shorttitle(1,1).lower
```

한글 저자는 로마자 변환 없이 그대로 들어가 LaTeX에서 문제가 될 수 있다.
한글 문헌이 많으므로 아래를 권장한다:

```
auth.transliterate.lower + year
```

`transliterate`가 한글을 라틴 문자로 바꿔 키가 깨지지 않는다.

---

## 2. 자동 내보내기 설정 — refs.bib

1. 좌측 컬렉션 목록에서 **다문화 인권교육 박사학위 논문** 우클릭
2. **Export Collection…**
3. Format: **Better BibLaTeX**
4. **Keep updated 체크** ← 이게 핵심. 빠뜨리면 1회성 내보내기가 된다
5. 저장 위치: `%USERPROFILE%\Documents\research\refs.bib`

이후 Zotero에 문헌을 추가·수정할 때마다 이 파일이 자동 갱신된다.
대화 중 "참고문헌 상태 봐줘" 하면 이 파일을 직접 읽어 진단할 수 있다.

컬렉션이 여러 개면 각각 별도 `.bib`로 내보낸다 (`refs-설교.bib` 등).

---

## 3. 로컬 HTTP API 활성화 (선택)

Zotero가 실행 중일 때 실시간 조회를 열어두는 설정. `zotlib.py`는 이것 없이도 동작하므로
필수는 아니고, 다른 도구(pyzotero 등)를 붙일 때 필요하다.

1. Zotero → 편집 → 설정 → **고급(Advanced)**
2. **"이 컴퓨터의 다른 프로그램이 Zotero와 통신하도록 허용"** 체크
3. 확인:

```bash
curl "http://127.0.0.1:23119/api/users/0/items?limit=1"
```

`403 Forbidden`이 나오면 위 체크박스가 꺼져 있는 것이다.
Zotero가 종료돼 있으면 연결 자체가 실패한다.

---

## 4. KCI Open API 키 발급

한글 논문 메타데이터 복구의 적중률을 좌우한다. **키 없이는 12% 수준.**

### 경로 A — 공공데이터포털 (권장, 자동승인)

1. https://www.data.go.kr 회원가입
2. "한국연구재단 KCI" 검색 → **KCI 논문정보서비스** / **KCI 학술지정보서비스** 활용신청
3. 개발계정은 **자동승인**이라 즉시 발급 (운영계정 전환은 심의 필요)
4. 마이페이지 → 개발계정 → **일반 인증키(Decoding)** 복사

### 경로 B — KCI 포털 직접 (제목 검색 API, 공문 필요)

`apiCode=articleSearch` 로 제목·저자·학술지 검색이 되는 건 이쪽이다.
다만 발급 절차가 무겁다: 회원가입 → 인증키 신청서 작성 → **공문과 신청서를
kciadmin@nrf.re.kr 로 발송** → 승인 후 발급.
연구 목적이면 대개 승인되지만 며칠 걸린다.

### 키 등록

발급받은 키를 환경변수로 넣는다. **PowerShell 7 기준:**

```powershell
[Environment]::SetEnvironmentVariable("KCI_API_KEY", "<발급받은키>", "User")
```

새 터미널부터 적용된다. 확인:

```powershell
$env:KCI_API_KEY
```

> 키를 스크립트나 대화창에 직접 붙여넣지 말 것. 환경변수로만 다룬다.

---

## 5. Zotero Connector (브라우저)

문헌을 브라우저에서 곧바로 담는 확장. 없으면 수집 속도가 크게 떨어진다.

- https://www.zotero.org/download/connectors 에서 Chrome/Edge용 설치
- RISS·KCI·DBpia는 번역기가 어느 정도 동작하나 **저자명·학회지명이 깨지는 경우**가 있다.
  저장 직후 항목을 열어 저자/연도/학회지를 눈으로 확인하는 습관을 들일 것.
- 번역기가 안 먹으면 사이트의 **내보내기 → RIS/EndNote** 버튼으로 받아 Zotero에 끌어다 놓는다.

---

## 6. Unpaywall 확장

유료 논문 페이지에서 합법 무료본을 자동 탐색한다.
https://unpaywall.org/products/extension — 기관 구독이 없을 때 체감 효과가 크다.

---

## 점검 순서

설정을 마쳤으면 아래를 돌려 상태를 확인한다.

```powershell
$env:PYTHONIOENCODING="utf-8"
& "C:\Python314\python.exe" "${CLAUDE_PLUGIN_ROOT}\skills\zotero\scripts\zotlib.py" diag
```

`인용 가능` 비율이 목표치다. KCI 등재지 투고를 전제로 하면
**인용 가능 항목 45건 이상, 그중 한글 문헌 15건 이상, 최근 5년 30% 이상**이 기준선이다.
