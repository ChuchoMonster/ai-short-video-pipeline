#!/usr/bin/env bash
# Episode 06 v2 — single-shot, sloth in tree fork in jungle.
# Runs Nano Banana 2 (scene-prompt) → Seedance (seedance-prompt) → raw.mp4.
# No stitch.
#
# Cost: ~$2 (one image + one 15s Seedance Standard 720p call).

set -euo pipefail

ROOT="${KWA_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
EP="$ROOT/episodes-in-progress/06"
LOG="$EP/run-06-v2.log"

# shellcheck disable=SC1091
if [[ -f "$ROOT/.env" ]]; then source "$ROOT/.env"; fi
if [[ -z "${KIE_AI_API_KEY:-}" ]]; then
  echo "FAIL: KIE_AI_API_KEY missing" >&2; exit 1
fi

KIE_BASE="https://api.kie.ai/api/v1/playground"

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

log "=== Episode 06 v2 — sloth in tree, single shot ==="
log "Started: $(date)"

##############################################################################
# Step 1 — Nano Banana 2: scene reference (sloth on mossy tree fork, no people)
##############################################################################
log
log "[img] Submitting Nano Banana 2..."
T0=$(date +%s)
PROMPT="$(cat "$EP/prompts/scene-prompt.txt")"

SUBMIT=$(jq -n --arg p "$PROMPT" '{
  model: "nano-banana-2",
  input: {prompt: $p, output_format: "png", image_size: "1:1"}
}' | curl -sS -X POST "$KIE_BASE/createTask" \
  -H "Authorization: Bearer $KIE_AI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @-)

TASK=$(echo "$SUBMIT" | jq -r '.data.taskId // empty')
if [[ -z "$TASK" ]]; then
  log "[img] FAIL: image submit"; echo "$SUBMIT" | tee -a "$LOG"; exit 1
fi
log "[img] taskId: $TASK"

while :; do
  RESP=$(curl -sS "$KIE_BASE/recordInfo?taskId=$TASK" \
    -H "Authorization: Bearer $KIE_AI_API_KEY")
  STATE=$(echo "$RESP" | jq -r '.data.state // "unknown"')
  log "[img] state: $STATE"
  case "$STATE" in
    success) break ;;
    fail)
      log "[img] FAIL: image gen"
      echo "$RESP" | jq '.data | {state, failCode, failMsg}' | tee -a "$LOG"
      exit 1 ;;
  esac
  sleep 3
done

URL_IMG=$(echo "$RESP" | jq -r '.data.resultJson | fromjson | .resultUrls[0]')
log "[img] image URL: $URL_IMG"
curl -sS -o "$EP/reference/ref.png" "$URL_IMG"
T1=$(date +%s)
log "[img] saved: $EP/reference/ref.png"
log "[img] elapsed: $((T1-T0))s"

##############################################################################
# Step 2 — Seedance 2 with reference image
##############################################################################
log
log "[vid] Submitting Seedance 2 (15s, 9:16, 720p)..."
PROMPT_VID="$(cat "$EP/prompts/seedance-prompt.txt")"

SUBMIT=$(jq -n --arg p "$PROMPT_VID" --arg url "$URL_IMG" '{
  model: "bytedance/seedance-2",
  input: {
    prompt: $p, image_url: $url,
    duration: 15, resolution: "720p", aspect_ratio: "9:16"
  }
}' | curl -sS -X POST "$KIE_BASE/createTask" \
  -H "Authorization: Bearer $KIE_AI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @-)

TASK=$(echo "$SUBMIT" | jq -r '.data.taskId // empty')
if [[ -z "$TASK" ]]; then
  log "[vid] FAIL: video submit"; echo "$SUBMIT" | tee -a "$LOG"; exit 1
fi
log "[vid] taskId: $TASK"

while :; do
  RESP=$(curl -sS "$KIE_BASE/recordInfo?taskId=$TASK" \
    -H "Authorization: Bearer $KIE_AI_API_KEY")
  STATE=$(echo "$RESP" | jq -r '.data.state // "unknown"')
  log "[vid] state: $STATE"
  case "$STATE" in
    success) break ;;
    fail)
      log "[vid] FAIL: video gen"
      echo "$RESP" | jq '.data | {state, failCode, failMsg}' | tee -a "$LOG"
      exit 1 ;;
  esac
  sleep 10
done

URL_VID=$(echo "$RESP" | jq -r '.data.resultJson | fromjson | .resultUrls[0]')
log "[vid] video URL: $URL_VID"
curl -sS -o "$EP/raw/raw.mp4" "$URL_VID"
T2=$(date +%s)
log "[vid] saved: $EP/raw/raw.mp4"
log "[vid] elapsed: $((T2-T1))s"

log
log "=== Done ==="
log "Total wall time: $((T2-T0))s"
log "Outputs:"
log "  Reference image: $EP/reference/ref.png"
log "  Raw video:       $EP/raw/raw.mp4"
