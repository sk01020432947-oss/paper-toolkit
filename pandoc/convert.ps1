# 옵시디언 원고(md) → Zotero 실시간 인용이 살아있는 Word(docx) 변환
# 사용법:  pwsh -File convert.ps1 "볼트\원고.md"            → Downloads\원고.docx
#          pwsh -File convert.ps1 "원고.md" "출력.docx"
param(
    [Parameter(Mandatory)][string]$InputFile,
    [string]$OutputFile
)

$here = $PSScriptRoot
$lua  = Join-Path $here "zotero.lua"
$bib  = Join-Path $here "My Library.yaml"

if (-not (Test-Path $InputFile)) { Write-Error "입력 파일 없음: $InputFile"; exit 1 }
if (-not (Test-Path $bib)) {
    Write-Error "서지 파일 없음: $bib`nZotero에서 My Library 우클릭 → Export Library → Better CSL YAML (Keep updated 체크) → 이 폴더에 'My Library.yaml'로 저장하세요."
    exit 1
}
if (-not $OutputFile) {
    $OutputFile = Join-Path "$env:USERPROFILE\Downloads" ([IO.Path]::GetFileNameWithoutExtension($InputFile) + ".docx")
}

pandoc $InputFile --lua-filter=$lua --bibliography=$bib -o $OutputFile
if ($LASTEXITCODE -eq 0) {
    Write-Host "완료: $OutputFile  (Word에서 Zotero 탭 → Refresh → 스타일 지정)"
} else {
    Write-Error "pandoc 변환 실패 (exit $LASTEXITCODE)"
}
