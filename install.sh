#!/usr/bin/env bash
# paper-toolkit 복사 설치 (맥·리눅스). 플러그인 설치(claude plugin install)를 못 쓸 때만 사용.
#   bash install.sh           같은 이름이 이미 있으면 건너뜀
#   bash install.sh --force   기존 것을 ~/.claude/backup-paper-toolkit-<시각>/ 으로 옮기고 덮어씀
set -euo pipefail
command -v python3 >/dev/null || { echo "python3가 필요합니다. 맥: xcode-select --install"; exit 1; }
[ "${1:-}" = "-f" ] && set -- --force
exec python3 "$(dirname "$0")/skills/paper-start/scripts/ptk.py" install "$@"
