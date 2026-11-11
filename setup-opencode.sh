#!/usr/bin/env bash
# ------------------------------------------------------------
#  Copy repository OpenCode configuration into ~/.config/opencode
#  (no symlinks – pure copy). Safe to re-run.
# ------------------------------------------------------------

set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
DST="${HOME}/.config/opencode"

# -----------------------------------------------------------------
# Helper to backup an existing entry (file or directory)
# -----------------------------------------------------------------
backup_if_exists() {
  local target="$1"
  if [ -e "${DST}/${target}" ] && [ ! -L "${DST}/${target}" ]; then
    mv "${DST}/${target}" "${DST}/${target}.bak.$(date +%s)"
  fi
}

# -----------------------------------------------------------------
# Create target root (and the secrets sub‑dir) if missing
# -----------------------------------------------------------------
mkdir -p "${DST}/secrets"
chmod 700 "${DST}/secrets"

# -----------------------------------------------------------------
# Mapping of *what we want in the destination* → *where it lives in the repo*
# -----------------------------------------------------------------
declare -A MAP=(
  [opencode.json]=".opencode/opencode.json"
  [AGENTS.md]=".opencode/AGENTS.md"
  [@agents]="@agents"
  [@commands]="@commands"
  [@skills]="@skills"
  # optional – copy any extra hidden config (rules, custom scripts, etc.)
  [.opencode]=".opencode"
)

# -----------------------------------------------------------------
# Copy each entry, backing up any previous version
# -----------------------------------------------------------------
for dst_name in "${!MAP[@]}"; do
  src_path="${SRC}/${MAP[$dst_name]}"

  if [ ! -e "${src_path}" ]; then
    echo "WARN: source '${src_path}' not found – skipping."
    continue
  fi

  # backup existing destination entry (file **or** directory)
  backup_if_exists "${dst_name}"

  # Use -a to preserve permissions / timestamps; -r works for dirs too
  cp -a "${src_path}" "${DST}/${dst_name}"
  echo " → Copied '${dst_name}'"
done

# -----------------------------------------------------------------
# Backward‑compatibility: expose skills under the historic "skills/" path
# -----------------------------------------------------------------
if [ -d "${DST}/@skills" ]; then
  # backup any existing plain skills directory
  backup_if_exists "skills"
  cp -a "${DST}/@skills" "${DST}/skills"
  echo " → Copied '@skills' to legacy 'skills' location"
fi

# -----------------------------------------------------------------
# Post‑copy sanity checks / user hints
# -----------------------------------------------------------------
if [ ! -s "${DST}/secrets/minerva-assistant-key" ]; then
  echo "WARN: missing ${DST}/secrets/minerva-assistant-key"
fi

if ! command -v biomcp >/dev/null 2>&1; then
  echo "WARN: biomcp not on PATH (install with: uv pip install biomcp-cli)"
fi

echo "Copied. Restart: opencode service restart"
