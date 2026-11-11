#!/usr/bin/env bash
# ------------------------------------------------------------
# Debug version of the agent sanity‑check suite
# ------------------------------------------------------------

set -uo pipefail          # keep strict handling, but we’ll turn off `-e` locally
SCRIPT_DIR=$(pwd)

# ---------- Helpers ----------
log()   { echo -e "\e[34m==> $*\e[0m"; }   # informational
pass()  { echo -e "\e[32m✔ $*\e[0m"; }
fail()  { echo -e "\e[31m✘ $*\e[0m"; ERR=1; }

# Verify that the OpenCode CLI is available
if ! command -v opencode >/dev/null 2>&1; then
  echo -e "\e[31mERROR: 'opencode' command not found. Install it first:\e[0m"
  echo "    npm i -g @opencode/cli"
  exit 1
fi

# Wrapper that runs a command and never aborts the whole script
run_cmd() {
  local cmd="$1"
  log "Running: $cmd"
  # Use `opencode run` (non‑interactive) and capture both stdout and exit code
  local out
  out=$(opencode run --auto "$cmd" 2>&1)
  local rc=$?
  echo "$out"    # always show the raw output for debugging
  return $rc
}

ERR=0

# ---------- 1️⃣ Designer (design‑review) ----------
out=$(run_cmd "/design-review test design") && rc=$? || rc=$?
if [[ $rc -eq 0 && $out =~ Design[[:space:]]Review ]]; then
  pass "designer → /design-review"
else
  fail "designer → /design-review (no Design Review block; rc=$rc)"
fi

# ---------- 2️⃣ Literature (/lit) ----------
out=$(run_cmd "/lit TP53") && rc=$? || rc=$?
if [[ $rc -eq 0 && $out =~ TP53 && $out =~ PMID ]]; then
  pass "literature → /lit TP53"
else
  fail "literature → /lit TP53 (no evidence table; rc=$rc)"
fi

# ---------- 3️⃣ Auditor ----------
cat > ./tmp_dummy.R <<'EOF'
print("hello")
EOF
out=$(run_cmd "/audit ./tmp_dummy.R") && rc=$? || rc=$?
if [[ $rc -eq 0 && $out =~ Audit ]]; then
  pass "auditor → /audit dummy.R"
else
  fail "auditor → /audit dummy.R (no audit output; rc=$rc)"
fi

# ---------- 4️⃣ Scout ----------
echo "needle_here" > ./scout.txt
out=$(run_cmd "/scout ./scout.txt") && rc=$? || rc=$?
if [[ $rc -eq 0 && $out =~ needle_here ]]; then
  pass "scout → /scout"
else
  fail "scout → /scout (needle not found; rc=$rc)"
fi

# ---------- 5️⃣ Analyst (new‑analysis) ----------
TMPDIR=$(mktemp -d)
out=$(run_cmd "/new-analysis $TMPDIR/demo") && rc=$? || rc=$?
if [[ $rc -eq 0 && $out =~ demo ]]; then
  pass "analyst → /new-analysis"
else
  fail "analyst → /new-analysis (no plan output; rc=$rc)"
fi
rm -rf "$TMPDIR"
# cleanup temporary files created for auditor and scout	rm -f ./tmp_dummy.R ./scout.txt

# ---------- Summary ----------
if [[ $ERR -eq 0 ]]; then
  echo -e "\nAll agent tests passed ✅"
else
  echo -e "\nSome agent tests failed ❌"
fi
exit $ERR
