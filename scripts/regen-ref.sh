#!/usr/bin/env bash
# Regenerate a Nano Banana 2 reference image from a prompt file.
# Useful for iterating on the scene prompt without re-spending Seedance credits.
#
# Usage: regen-ref.sh <prompt_file> <output_png>
# Cost: ~$0.12 per call.

set -euo pipefail

ROOT="${KWA_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

# shellcheck disable=SC1091
if [[ -f "$ROOT/.env" ]]; then source "$ROOT/.env"; fi
if [[ -z "${KIE_AI_API_KEY:-}" ]]; then
  echo "FAIL: KIE_AI_API_KEY missing" >&2; exit 1
fi

KIE_BASE="https://api.kie.ai/api/v1/playground"

PROMPT_FILE="${1:?usage: regen-ref.sh <prompt_file> <output_png>}"
OUT_PNG="${2:?usage: regen-ref.sh <prompt_file> <output_png>}"

if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "FAIL: prompt file not found: $PROMPT_FILE" >&2; exit 1
fi

PROMPT="$(cat "$PROMPT_FILE")"

echo "[$(date +%H:%M:%S)] Submitting Nano Banana 2..."
echo "  prompt: $PROMPT_FILE"
echo "  output: $OUT_PNG"

SUBMIT=$(jq -n --arg p "$PROMPT" '{
  model: "nano-banana-2",
  input: {prompt: $p, output_format: "png", image_size: "1:1"}
}' | curl -sS -X POST "$KIE_BASE/createTask" \
  -H "Authorization: Bearer $KIE_AI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @-)

TASK=$(echo "$SUBMIT" | jq -r '.data.taskId // empty')
if [[ -z "$TASK" ]]; then
  echo "FAIL: image submit"; echo "$SUBMIT"; exit 1
fi
echo "  taskId: $TASK"

while :; do
  RESP=$(curl -sS "$KIE_BASE/recordInfo?taskId=$TASK" \
    -H "Authorization: Bearer $KIE_AI_API_KEY")
  STATE=$(echo "$RESP" | jq -r '.data.state // "unknown"')
  echo "  [$(date +%H:%M:%S)] state: $STATE"
  case "$STATE" in
    success) break ;;
    fail)
      echo "FAIL: image gen"
      echo "$RESP" | jq '.data | {state, failCode, failMsg}'
      exit 1 ;;
  esac
  sleep 3
done

URL=$(echo "$RESP" | jq -r '.data.resultJson | fromjson | .resultUrls[0]')
echo "  URL: $URL"
curl -sS -o "$OUT_PNG" "$URL"
echo "  saved: $OUT_PNG"
