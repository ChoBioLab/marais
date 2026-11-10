#!/usr/bin/env bash
# Links this repo into ~/.config/opencode. Safe to re-run. Never touches secrets/.
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
DST="$HOME/.config/opencode"
mkdir -p "$DST/secrets"
chmod 700 "$DST/secrets"
for f in opencode.json AGENTS.md agents commands skills; do
  if [ -e "$DST/$f" ] && [ ! -L "$DST/$f" ]; then
    mv "$DST/$f" "$DST/$f.bak.$(date +%s)"
  fi
  ln -sfn "$SRC/$f" "$DST/$f"
 done
[ -s "$DST/secrets/minerva-assistant-key" ] || echo "WARN: missing $DST/secrets/minerva-assistant-key"
command -v biomcp >/dev/null || echo "WARN: biomcp not on PATH (uv tool install biomcp-cli)"
echo "Linked. Restart: opencode service restart"
