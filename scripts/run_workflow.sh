#!/usr/bin/env bash
# Wrapper to run OpenCode guide workflows with parameter substitution
# Usage:
#   scripts/run_workflow.sh <workflow> [--variant <variant>] [--gene <gene>] [--disease <disease>]
# Example:
#   scripts/run_workflow.sh variant-pathogenicity-workflow --variant "BRAF V600E"
#   scripts/run_workflow.sh broad-gene-disease-workflow --gene EGFR --disease "non-small cell lung cancer"

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <workflow> [--variant <variant>] [--gene <gene>] [--disease <disease>]"
  exit 1
fi

WORKFLOW="$1"
shift

# Parse optional arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --variant)
      VARIANT="$2"; shift 2;;
    --gene)
      GENE="$2"; shift 2;;
    --disease)
      DISEASE="$2"; shift 2;;
    *)
      echo "Unknown argument: $1"; exit 1;;
  esac
done

SRC_WORKFLOW="@workflows/${WORKFLOW}.yaml"
if [[ ! -f "$SRC_WORKFLOW" ]]; then
  echo "Workflow file $SRC_WORKFLOW not found"
  exit 1
fi

# Create a temporary workflow with placeholders replaced
TMP_WORKFLOW=$(mktemp "${WORKFLOW}_XXXX.yaml")
cp "$SRC_WORKFLOW" "$TMP_WORKFLOW"

# Replace placeholders if values are set
if [[ -n "${VARIANT:-}" ]]; then
  sed -i "s/{{variant}}/${VARIANT//\//\\\/}/g" "$TMP_WORKFLOW"
fi
if [[ -n "${GENE:-}" ]]; then
  sed -i "s/{{gene}}/${GENE//\//\\\/}/g" "$TMP_WORKFLOW"
fi
if [[ -n "${DISEASE:-}" ]]; then
  sed -i "s/{{disease}}/${DISEASE//\//\\\/}/g" "$TMP_WORKFLOW"
fi

# If testing, just show the rendered workflow; otherwise run via OpenCode subagent
if [[ "${RUN_TEST:-}" == "1" ]]; then
  echo "--- Rendered workflow: $TMP_WORKFLOW ---"
  cat "$TMP_WORKFLOW"
  rm -f "$TMP_WORKFLOW"
  exit 0
fi
opencode subagent general "run-workflow $TMP_WORKFLOW"

# Clean up
rm -f "$TMP_WORKFLOW"
