#!/usr/bin/env bash
# Episode 06 — RESUME from Part B onward.
# Use after a kie.ai top-up. Skips:
#   - Nano Banana 2 Part A (ref-a.png already on disk)
#   - Seedance Part A (raw-a.mp4 already on disk)
#   - Nano Banana 2 Part B (ref-b.png already on disk)
# Re-uploads ref-b.png to kie.ai? No — kie.ai's earlier output URL has expired
# by now (tempfile.aiquickdraw.com URLs are short-lived). Solution: re-submit
# the Part B Nano Banana 2 call to get a fresh hosted URL, then run Seedance B.
# This costs ~$0.12 extra but is the simplest reliable path.
#
# Cost: ~$2.00 (one fresh Part B image + one Seedance Part B).

set -euo pipefail

ROOT="${KWA_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
EP="$ROOT/episodes-in-progress/06"
LOG="$EP/resume-06.log"

# shellcheck disable=SC1091
if [[ -f "$ROOT/.env" ]]; then source "$ROOT/.env"; fi
if [[ -z "${KIE_AI_API_KEY:-}" ]]; then
  echo "FAIL: KIE_AI_API_KEY missing" >&2; exit 1
fi

KIE_BASE="https://api.kie.ai/api/v1/playground"

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

log "=== Episode 06 RESUME — Part B + stitch ==="
log "Started: $(date)"

# Re-submit Part B Nano Banana 2 to get a fresh URL hosted on kie.ai.
log "[B.img] Re-submitting Nano Banana 2 to get a fresh URL..."
PROMPT_B="$(cat "$EP/prompts/scene-prompt-b.txt")"

SUBMIT=$(jq -n --arg p "$PROMPT_B" '{
  model: "nano-banana-2",
  input: {prompt: $p, output_format: "png", image_size: "1:1"}
}' | curl -sS -X POST "$KIE_BASE/createTask" \
  -H "Authorization: Bearer $KIE_AI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @-)

TASK=$(echo "$SUBMIT" | jq -r '.data.taskId // empty')
if [[ -z "$TASK" ]]; then
  log "[B.img] FAIL: image submit"; echo "$SUBMIT" | tee -a "$LOG"; exit 1
fi
log "[B.img] taskId: $TASK"

while :; do
  RESP=$(curl -sS "$KIE_BASE/recordInfo?taskId=$TASK" \
    -H "Authorization: Bearer $KIE_AI_API_KEY")
  STATE=$(echo "$RESP" | jq -r '.data.state // "unknown"')
  log "[B.img] state: $STATE"
  case "$STATE" in
    success) break ;;
    fail)
      log "[B.img] FAIL: image gen"
      echo "$RESP" | jq '.data | {state, failCode, failMsg}' | tee -a "$LOG"
      exit 1 ;;
  esac
  sleep 3
done

URL_B=$(echo "$RESP" | jq -r '.data.resultJson | fromjson | .resultUrls[0]')
log "[B.img] image URL: $URL_B"
# Overwrite ref-b.png with the fresh image so the on-disk copy matches the URL.
curl -sS -o "$EP/reference/ref-b.png" "$URL_B"
log "[B.img] saved: $EP/reference/ref-b.png"

# Now Seedance Part B.
log "[B.vid] Submitting Seedance 2 (15s, 9:16, 720p)..."
PROMPT_VID_B="$(cat "$EP/prompts/seedance-prompt-b.txt")"

SUBMIT=$(jq -n --arg p "$PROMPT_VID_B" --arg url "$URL_B" '{
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
  log "[B.vid] FAIL: video submit"; echo "$SUBMIT" | tee -a "$LOG"; exit 1
fi
log "[B.vid] taskId: $TASK"

while :; do
  RESP=$(curl -sS "$KIE_BASE/recordInfo?taskId=$TASK" \
    -H "Authorization: Bearer $KIE_AI_API_KEY")
  STATE=$(echo "$RESP" | jq -r '.data.state // "unknown"')
  log "[B.vid] state: $STATE"
  case "$STATE" in
    success) break ;;
    fail)
      log "[B.vid] FAIL: video gen"
      echo "$RESP" | jq '.data | {state, failCode, failMsg}' | tee -a "$LOG"
      exit 1 ;;
  esac
  sleep 10
done

URL_VID_B=$(echo "$RESP" | jq -r '.data.resultJson | fromjson | .resultUrls[0]')
log "[B.vid] video URL: $URL_VID_B"
curl -sS -o "$EP/raw/raw-b.mp4" "$URL_VID_B"
log "[B.vid] saved: $EP/raw/raw-b.mp4"

# Extract Part A's last frame for documentation / future literal-stitch retry.
log "--- Extracting Part A last frame for reference ---"
ffmpeg -y -sseof -0.05 -i "$EP/raw/raw-a.mp4" -vframes 1 -q:v 2 \
  "$EP/reference/frame-a-last.png" 2>>"$LOG"
log "saved: $EP/reference/frame-a-last.png"

# Stitch.
log "--- Stitching A + B ---"
ffmpeg -y -i "$EP/raw/raw-a.mp4" -i "$EP/raw/raw-b.mp4" \
  -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -crf 18 -c:a aac -b:a 192k \
  "$EP/raw/raw-stitched.mp4" 2>>"$LOG"
log "saved: $EP/raw/raw-stitched.mp4"

log
log "=== Done ==="
log "Outputs:"
log "  Part A raw:    $EP/raw/raw-a.mp4"
log "  Part B raw:    $EP/raw/raw-b.mp4"
log "  Stitched:      $EP/raw/raw-stitched.mp4"
log "  Last-A frame:  $EP/reference/frame-a-last.png"
log "  Refs:          $EP/reference/ref-a.png, $EP/reference/ref-b.png"
