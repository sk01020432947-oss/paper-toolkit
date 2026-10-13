# paper-toolkit install.ps1 — 논문 도구 일괄 설치 (Windows PowerShell 5.1 / pwsh 7 공용)
# 사용: powershell -ExecutionPolicy Bypass -File .\install.ps1
# 옵션: -SkipSkills(플러그인으로 스킬 설치한 경우) -SkipWinget -SkipPip -SkipMcp -Force(기존 스킬 덮어쓰기) -WithDissertationSimulator(git clone 포함)
param(
    [switch]$SkipSkills,   # 플러그인(/plugin install paper-toolkit@paper-toolkit)으로 스킬을 깔았다면 켜기 — 1·2단계 생략
    [switch]$SkipWinget,
    [switch]$SkipPip,
    [switch]$SkipMcp,
    [switch]$Force,
    [switch]$WithDissertationSimulator
)
$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$root   = $PSScriptRoot
$claude = Join-Path $env:USERPROFILE '.claude'
$docs   = [Environment]::GetFolderPath('MyDocuments')
$dest   = Join-Path $docs 'paper-toolkit'
$backup = Join-Path $claude ('backup-paper-toolkit-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
$done = @(); $skipped = @(); $failed = @()
function Step($m){ Write-Host "`n== $m" -ForegroundColor Cyan }
function Ok($m){ Write-Host "   [OK] $m" -ForegroundColor Green;  $script:done += $m }
function Skip($m){ Write-Host "   [--] $m" -ForegroundColor DarkGray; $script:skipped += $m }
function Fail($m){ Write-Host "   [!!] $m" -ForegroundColor Red;    $script:failed += $m }

# ---------- 1. 스킬 ----------
Step '1/6 Claude Code 스킬 복사 → ~\.claude\skills'
if ($SkipSkills) { Skip '플러그인으로 설치됨(-SkipSkills) — 스킬·에이전트 복사 생략' } else {
$skillDst = Join-Path $claude 'skills'
New-Item -ItemType Directory -Force -Path $skillDst | Out-Null
Get-ChildItem (Join-Path $root 'skills') -Directory | ForEach-Object {
    $to = Join-Path $skillDst $_.Name
    if ((Test-Path $to) -and -not $Force) { Skip "스킬 $($_.Name) — 이미 있음(-Force로 덮어쓰기)"; return }
    if (Test-Path $to) { New-Item -ItemType Directory -Force -Path (Join-Path $backup 'skills') | Out-Null; Move-Item $to (Join-Path $backup "skills\$($_.Name)") -Force }  # 덮어쓰기 전 백업
    Copy-Item $_.FullName $to -Recurse -Force
    Ok "스킬 $($_.Name)"
}

# ---------- 2. 에이전트 ----------
Step '2/6 humanize 에이전트 복사 → ~\.claude\agents'
$agDst = Join-Path $claude 'agents'
New-Item -ItemType Directory -Force -Path $agDst | Out-Null
Get-ChildItem (Join-Path $root 'agents') -Filter *.md | ForEach-Object {
    $to = Join-Path $agDst $_.Name
    if ((Test-Path $to) -and -not $Force) { Skip "에이전트 $($_.Name) — 이미 있음"; return }
    Copy-Item $_.FullName $to -Force; Ok "에이전트 $($_.Name)"
}

}
# ---------- 3. 도구·설정 파일 ----------
Step "3/6 분석기·Pandoc 설정·목록 → $dest"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
if ($root -ieq $dest) { Skip '이미 대상 폴더에서 실행 중 — 복사 생략' }
else {
    foreach ($d in 'tools','pandoc') {
        Copy-Item (Join-Path $root $d) (Join-Path $dest $d) -Recurse -Force; Ok "$d\ 복사"
    }
    foreach ($f in 'README.md','MANUAL.md','MANUAL.html') { Copy-Item (Join-Path $root $f) $dest -Force }
    Ok 'MANUAL.html (사용 설명서)'
}

# ---------- 4. winget ----------
Step '4/6 데스크톱 프로그램 (winget)'
if ($SkipWinget) { Skip 'winget 단계 건너뜀' }
elseif (-not (Get-Command winget -ErrorAction SilentlyContinue)) { Fail 'winget 없음 — Microsoft Store에서 "앱 설치 관리자" 설치 후 재실행' }
else {
    $pkgs = @(
        @{id='DigitalScholar.Zotero';           name='Zotero'},
        @{id='Obsidian.Obsidian';               name='Obsidian'},
        @{id='JohnMacFarlane.Pandoc';           name='Pandoc'},
        @{id='UB-Mannheim.TesseractOCR';        name='Tesseract-OCR'},
        @{id='geeksoftwareGmbH.PDF24Creator';   name='PDF24 Creator'},
        @{id='Python.Python.3.12';              name='Python 3.12'},
        @{id='Git.Git';                         name='Git'},
        @{id='OpenJS.NodeJS.LTS';               name='Node.js LTS (npx MCP용)'}
    )
    foreach ($p in $pkgs) {
        $have = winget list --id $p.id -e 2>$null | Select-String -SimpleMatch $p.id
        if ($have) { Skip "$($p.name) — 설치됨"; continue }
        winget install --id $p.id -e --silent --accept-source-agreements --accept-package-agreements | Out-Null
        if ($LASTEXITCODE -eq 0) { Ok $p.name } else { Fail "$($p.name) (winget 종료코드 $LASTEXITCODE)" }
    }
}

# ---------- 5. pip ----------
Step '5/6 Python 패키지 (pip)'
if ($SkipPip) { Skip 'pip 단계 건너뜀' }
else {
    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) { Fail 'python 없음 — 새 터미널에서 다시 실행(방금 설치했다면 PATH 반영 필요)' }
    else {
        $mods = 'ocrmypdf','markitdown','pyalex','habanero','arxiv','pymupdf','pypdf','pypdfium2','pandas','scipy','networkx','ruamel.yaml','master-of-hwp'
        python -m pip install --user --upgrade @mods
        if ($LASTEXITCODE -eq 0) { Ok "pip $($mods.Count)종" } else { Fail 'pip 설치 일부 실패 — 위 출력 확인' }
    }
}

# ---------- 6. MCP ----------
Step '6/6 MCP 서버 등록 (claude mcp add)'
if ($SkipMcp) { Skip 'MCP 단계 건너뜀' }
elseif (-not (Get-Command claude -ErrorAction SilentlyContinue)) { Fail 'claude CLI 없음 — Claude Code 설치 후 아래 명령을 직접 실행' }
else {
    $mcps = @(
        @('kordoc',           '--', 'cmd', '/c', 'npx', '-y', 'kordoc', 'mcp'),
        @('mohwp',            '--', 'mohwp', 'mcp-serve'),
        @('public-data-lens', '--transport', 'http', 'https://service.datahub.kr/projects/public-data-lens/mcp')
    )
    foreach ($m in $mcps) {
        if ($m[1] -eq '--transport') { claude mcp add --transport $m[2] $m[0] $m[3] 2>&1 | Out-Null }
        else { claude mcp add $m[0] $m[1..($m.Count-1)] 2>&1 | Out-Null }
        if ($LASTEXITCODE -eq 0) { Ok "MCP $($m[0])" } else { Skip "MCP $($m[0]) — 이미 등록됐거나 실패(claude mcp list로 확인)" }
    }
}

# ---------- 선택: Dissertation Simulator ----------
if ($WithDissertationSimulator) {
    Step '선택: Dissertation Simulator git clone'
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $ds = Join-Path $dest 'Dissertation-Simulator-AgenticWorkflow'
        if (Test-Path $ds) { Skip 'Dissertation Simulator — 이미 있음' }
        else { git clone https://github.com/cysinsight/Dissertation-Simulator-AgenticWorkflow.git $ds; if ($LASTEXITCODE -eq 0) { Ok "Dissertation Simulator → $ds (그 폴더에서 claude → /start)" } else { Fail 'git clone 실패' } }
    } else { Fail 'git 없음' }
}

# ---------- 요약 ----------
Write-Host "`n========== 결과 ==========" -ForegroundColor Cyan
Write-Host " 완료 $($done.Count) / 건너뜀 $($skipped.Count) / 실패 $($failed.Count)"
if ($failed) { $failed | ForEach-Object { Write-Host "   실패: $_" -ForegroundColor Red } }

Write-Host @"

========== 남은 수동 작업 ==========
[Claude Code 안에서 실행]  (PowerShell에서는 안 됨)
  /plugin marketplace add sk01020432947-oss/paper-toolkit        ← 이 묶음의 스킬 21종+에이전트 (ZIP 복사 대신 써도 됨)
  /plugin install paper-toolkit@paper-toolkit
  /plugin marketplace add Imbad0202/academic-research-skills
  /plugin install academic-research-skills@academic-research-skills
  (그 뒤 Claude Code 재시작 → /paper-start 로 점검·설정)

[직접 설치]
  - Ghostscript 10.x (OCRmyPDF 의존): https://github.com/ArtifexSoftware/ghostpdl-downloads/releases
  - Umi-OCR Paddle 포터블: https://github.com/hiroi-sora/Umi-OCR/releases
  - Zotero 확장 xpi: Better BibTeX https://github.com/retorquere/zotero-better-bibtex/releases
                    Zotmoov       https://github.com/wileyyugeta/zotmoov/releases
  - Obsidian 커뮤니티 플러그인: Zotero Integration · Templater · Pandoc Reference List · Copy Block Link
    → 문헌노트 템플릿: $dest\pandoc\Template_literature-note-Zotero.md, CSS 스니펫 zotero-highlights.css
  - Pandoc 변환: Zotero에서 My Library → Export → Better CSL YAML(Keep updated) → $dest\pandoc\My Library.yaml
    사용: pwsh -File "$dest\pandoc\convert.ps1" 원고.md
  - 한컴오피스(상용) — HWP 최종 조판 시

[API 키]  (선택) LAW_OC — 국가법령 MCP. open.law.go.kr 에서 발급한 뒤:
            claude mcp add korean-law -e LAW_OC=<키> -- cmd /c npx -y --ignore-scripts --omit=optional korean-law-mcp@latest
          (선택) KSKILL_RISS_API_KEY — RISS 검색 · KCI_API_KEY — zotero 메타데이터 복구
[설정]    Claude Code에서 /paper-start 를 입력하면 논문 폴더·위키 폴더·Zotero 폴더를 한 번에 설정합니다.
[분석기]  $dest\tools\KBG-PAPER-A.html 을 브라우저로 열면 PLS-SEM 분석기 (매뉴얼 동봉)
[설명서]  $dest\MANUAL.html
"@
