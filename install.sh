#!/usr/bin/env bash
# paper-toolkit 수동 설치 (맥·리눅스). 플러그인 설치(/plugin install)를 못 쓸 때만 사용.
# 사용: bash install.sh        # 같은 이름이 있으면 건너뜀
#       bash install.sh -f     # 덮어쓰기
set -euo pipefail
cd "$(dirname "$0")"
FORCE=0; [ "${1:-}" = "-f" ] && FORCE=1
DEST="$HOME/.claude"
mkdir -p "$DEST/skills" "$DEST/agents"

copied=0; skipped=0
for s in skills/*/; do
  n=$(basename "$s")
  if [ -e "$DEST/skills/$n" ] && [ $FORCE -eq 0 ]; then echo "건너뜀  skills/$n (이미 있음, 덮어쓰려면 -f)"; skipped=$((skipped+1)); continue; fi
  rm -rf "$DEST/skills/$n"; cp -R "$s" "$DEST/skills/$n"
  # 플러그인 경로 변수 → 실제 경로
  find "$DEST/skills/$n" -name '*.md' -exec sed -i.bak 's#\${CLAUDE_PLUGIN_ROOT}#'"$DEST"'#g; s#\${CLAUDE_PLUGIN_ROOT:-\$HOME/.claude}#'"$DEST"'#g' {} + -exec rm -f {}.bak \;
  find "$DEST/skills/$n" -name '*.bak' -delete
  echo "설치    skills/$n"; copied=$((copied+1))
done
for a in agents/*.md; do
  n=$(basename "$a")
  if [ -e "$DEST/agents/$n" ] && [ $FORCE -eq 0 ]; then echo "건너뜀  agents/$n"; skipped=$((skipped+1)); continue; fi
  cp "$a" "$DEST/agents/$n"; echo "설치    agents/$n"; copied=$((copied+1))
done

echo
echo "완료: 설치 $copied · 건너뜀 $skipped → $DEST"
echo "Claude Code를 재시작한 뒤 '/paper-writing-order'를 입력해 보세요."
command -v python3 >/dev/null || echo "주의: python3가 없습니다(zotero·kci-journal-finder 스크립트에 필요). 'xcode-select --install' 또는 python.org에서 설치."
