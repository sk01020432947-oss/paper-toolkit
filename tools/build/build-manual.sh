#!/usr/bin/env bash
# MANUAL.md → MANUAL.html (파일 하나로 보내기 좋은 판). pandoc 필요.
set -euo pipefail
cd "$(dirname "$0")/../.."
GH="https://github.com/sk01020432947-oss/paper-toolkit/blob/main"
pandoc MANUAL.md -f gfm -t html5 -s --syntax-highlighting=none --toc --toc-depth=3 \
  --metadata title="논문 스킬 매뉴얼집" --metadata lang=ko \
  -H <(printf '<style>\n'; cat tools/build/manual.css; printf '</style>\n') -o MANUAL.html
python3 - "$GH" <<'PY'
import re, sys, pathlib
gh = sys.argv[1]
p = pathlib.Path("MANUAL.html"); t = p.read_text(encoding="utf-8")
t = re.sub(r"<style>\s*html \{.*?</style>", "", t, count=1, flags=re.S)          # pandoc 기본 스타일 제거
t = re.sub(r'<header id="title-block-header">.*?</header>', "", t, count=1, flags=re.S)  # 중복 제목 제거
t = re.sub(r'href="(?!#|https?:)([^"]+)"', lambda m: 'href="%s/%s"' % (gh, m.group(1)), t)  # 상대 링크 → GitHub
p.write_text(t, encoding="utf-8")
PY
echo "MANUAL.html 생성"
