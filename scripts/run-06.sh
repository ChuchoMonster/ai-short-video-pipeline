#!/usr/bin/env bash
# Episode 06 — sloth on Costa Rica jungle bridge, two-shot.
# Runs:
#   Part A: Nano Banana 2 (scene-prompt-a) → Seedance (seedance-prompt-a) → raw-a.mp4
#   Part B: Nano Banana 2 (scene-prompt-b) → Seedance (seedance-prompt-b) → raw-b.mp4
#   Stitch: ffmpeg concat → raw-stitched.mp4
#
# Cost: ~$4 (two images + two 15s Seedance Standard 720p calls).

set -euo pipefail

ROOT="${KWA_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
EP="$ROOT/episodes-in-progress/06"
LOG="$EP/run-06.log"

# shellcheck disable=SC1091
if [[ -f "$ROOT/.env" ]]; then source "$ROOT/.env"; fi
if [[ -z "${KIE_AI_API_KEY:-}" ]]; then
  echo "FAIL: KIE_AI_API_KEY missing" >&2; exit 1
fi

KIE_BASE="https://api.kie.ai/api/v1/playground"

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

log "=== Episode 06 — sloth, Costa Rica jungle bridge, two-shot ==="
log "Started: $(date)"

submit_image() {
  local prompt_file="$1"
  local out_png="$2"
  local label="$3"

  local prompt
  prompt="$(cat "$prompt_file")"

  log "[$label] Submitting Nano Banana 2..."
  local submit
  submit=$(jq -n --arg p "$prompt" '{
    model: "nano-banana-2",
    input: {prompt: $p, output_format: "png", image_size: "1:1"}
  }' | curl -sS -X POST "$KIE_BASE/createTask" \
    -H "Authorization: Bearer $KIE_AI_API_KEY" \
    -H "Content-Type: application/json" \
    --data-binary @-)

  local task
  task=$(echo "$submit" | jq -r '.data.taskId // empty')
  if [[ -z "$task" ]]; then
    log "[$label] FAIL: image submit"; echo "$submit" | tee -a "$LOG"; exit 1
  fi
  log "[$label] taskId: $task"

  while :; do
    local resp state
    resp=$(curl -sS "$KIE_BASE/recordInfo?taskId=$task" \
      -H "Authorization: Bearer $KIE_AI_API_KEY")
    state=$(echo "$resp" | jq -r '.data.state // "unknown"')
    log "[$label] state: $state"
    case "$state" in
      success) break ;;
      fail)
        log "[$label] FAIL: image gen"
        echo "$resp" | jq '.data | {state, failCode, failMsg}' | tee -a "$LOG"
        exit 1 ;;
    esac
    sleep 3
  done

  local url
  url=$(echo "$resp" | jq -r '.data.resultJson | fromjson | .resultUrls[0]')
  log "[$label] image URL: $url"
  curl -sS -o "$out_png" "$url"
  log "[$label] saved: $out_png"

  echo "$url"
}

submit_video() {
  local prompt_file="$1"
  local image_url="$2"
  local out_mp4="$3"
  local label="$4"

  local prompt
  prompt="$(cat "$prompt_file")"

  log "[$label] Submitting Seedance 2 (15s, 9:16, 720p)..."
  local submit
  submit=$(jq -n --arg p "$prompt" --arg url "$image_url" '{
    model: "bytedance/seedance-2",
    input: {
      prompt: $p, image_url: $url,
      duration: 15, resolution: "720p", aspect_ratio: "9:16"
    }
  }' | curl -sS -X POST "$KIE_BASE/createTask" \
    -H "Authorization: Bearer $KIE_AI_API_KEY" \
    -H "Content-Type: application/json" \
    --data-binary @-)

  local task
  task=$(echo "$submit" | jq -r '.data.taskId // empty')
  if [[ -z "$task" ]]; then
    log "[$label] FAIL: video submit"; echo "$submit" | tee -a "$LOG"; exit 1
  fi
  log "[$label] taskId: $task"

  while :; do
    local resp state
    resp=$(curl -sS "$KIE_BASE/recordInfo?taskId=$task" \
      -H "Authorization: Bearer $KIE_AI_API_KEY")
    state=$(echo "$resp" | jq -r '.data.state // "unknown"')
    log "[$label] state: $state"
    case "$state" in
      success) break ;;
      fail)
        log "[$label] FAIL: video gen"
        echo "$resp" | jq '.data | {state, failCode, failMsg}' | tee -a "$LOG"
        exit 1 ;;
    esac
    sleep 10
  done

  local url
  url=$(echo "$resp" | jq -r '.data.resultJson | fromjson | .resultUrls[0]')
  log "[$label] video URL: $url"
  curl -sS -o "$out_mp4" "$url"
  log "[$label] saved: $out_mp4"
}

##############################################################################
# Part A
##############################################################################
log
log "--- Part A ---"
T0=$(date +%s)
URL_A=$(submit_image "$EP/prompts/scene-prompt-a.txt" "$EP/reference/ref-a.png" "A.img")
T1=$(date +%s)
log "[A.img] elapsed: $((T1-T0))s"

submit_video "$EP/prompts/seedance-prompt-a.txt" "$URL_A" "$EP/raw/raw-a.mp4" "A.vid"
T2=$(date +%s)
log "[A.vid] elapsed: $((T2-T1))s"

##############################################################################
# Part B
##############################################################################
log
log "--- Part B ---"
URL_B=$(submit_image "$EP/prompts/scene-prompt-b.txt" "$EP/reference/ref-b.png" "B.img")
T3=$(date +%s)
log "[B.img] elapsed: $((T3-T2))s"

submit_video "$EP/prompts/seedance-prompt-b.txt" "$URL_B" "$EP/raw/raw-b.mp4" "B.vid"
T4=$(date +%s)
log "[B.vid] elapsed: $((T4-T3))s"

##############################################################################
# Extract Part A's last frame (for documentation / future literal-stitch retry)
##############################################################################
log
log "--- Extracting Part A last frame for reference ---"
ffmpeg -y -sseof -0.05 -i "$EP/raw/raw-a.mp4" -vframes 1 -q:v 2 \
  "$EP/reference/frame-a-last.png" 2>>"$LOG"
log "saved: $EP/reference/frame-a-last.png"

##############################################################################
# Stitch with FFmpeg concat (hard cut, no cutaway)
##############################################################################
log
log "--- Stitching A + B ---"
ffmpeg -y -i "$EP/raw/raw-a.mp4" -i "$EP/raw/raw-b.mp4" \
  -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -crf 18 -c:a aac -b:a 192k \
  "$EP/raw/raw-stitched.mp4" 2>>"$LOG"
log "saved: $EP/raw/raw-stitched.mp4"

T5=$(date +%s)
log
log "=== Done ==="
log "Total wall time: $((T5-T0))s"
log "Outputs:"
log "  Part A raw:    $EP/raw/raw-a.mp4"
log "  Part B raw:    $EP/raw/raw-b.mp4"
log "  Stitched:      $EP/raw/raw-stitched.mp4"
log "  Last-A frame:  $EP/reference/frame-a-last.png"
log "  Refs:          $EP/reference/ref-a.png, $EP/reference/ref-b.png"
