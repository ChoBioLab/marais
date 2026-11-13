#!/usr/bin/env bash
# ------------------------------------------------------------
#  Copy repository OpenCode configuration into ~/.config/opencode
#  (no symlinks – pure copy). Safe to re-run.
#  Compatible with bash 3.2 (macOS default) through 5.x.
# ------------------------------------------------------------

set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
DST="${HOME}/.config/opencode"
STAMP="$(date +%s).$$"

# Move an existing entry (file or dir) aside; drop stale symlinks so cp
# can't write *through* them.
backup_if_exists() {
  local target="${DST}/$1"
  if [ -L "${target}" ]; then
    rm -f "${target}"
  elif [ -e "${target}" ]; then
    mv "${target}" "${target}.bak.${STAMP}"
  fi
}

# copy_entry <dest-name> <path-relative-to-repo>
copy_entry() {
  local dst_name="$1" src_path="${SRC}/$2"

  if [ ! -e "${src_path}" ]; then
    echo "WARN: source '${src_path}' not found – skipping."
    return 0
  fi

  backup_if_exists "${dst_name}"
  cp -a "${src_path}" "${DST}/${dst_name}"
  echo " → Copied '${dst_name}'"
}

mkdir -p "${DST}/secrets"
chmod 700 "${DST}/secrets"

# Ensure uv is installed
if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found – installing via official script..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Verify installation
  if ! command -v uv >/dev/null 2>&1; then
    echo "ERROR: uv installation failed. Exiting."
    exit 1
  fi
fi

# Install biomcp-cli using uv (if not already available)
if ! command -v biomcp >/dev/null 2>&1; then
  echo "Installing biomcp-cli via uv..."
  uv tool install biomcp-cli || echo "WARN: Failed to install biomcp-cli"
fi

copy_entry "opencode.json" ".opencode/opencode.json"
copy_entry "AGENTS.md" ".opencode/AGENTS.md"
copy_entry "@agents" "@agents"
copy_entry "@commands" "@commands"
copy_entry "@skills" "@skills"

# Backward-compatibility: expose skills under the historic "skills/" path
if [ -d "${DST}/@skills" ]; then
  backup_if_exists "skills"
  cp -a "${DST}/@skills" "${DST}/skills"
  echo " → Copied '@skills' to legacy 'skills' location"
fi

# Post-copy sanity checks
if [ ! -s "${DST}/secrets/minerva-assistant-key" ]; then
  echo "WARN: missing ${DST}/secrets/minerva-assistant-key"
fi

if ! command -v biomcp >/dev/null 2>&1; then
  echo "WARN: biomcp not on PATH (install with: uv tool install biomcp-cli)"
fi

# Prompt for Minerva assistant API key
read -p "Enter your Minerva assistant API key (or press ENTER to skip): " MINERVA_KEY
if [ -n "$MINERVA_KEY" ]; then
  echo "$MINERVA_KEY" > "${DST}/secrets/minerva-assistant-key"
  chmod 600 "${DST}/secrets/minerva-assistant-key"
  echo " → Saved Minerva API key"
fi

echo "Copied. Restart: opencode service restart"
