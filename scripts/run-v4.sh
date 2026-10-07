#!/usr/bin/env bash
# Phase B.5.2 — combined Lever 2+3 generation.
# Reads prompts from scripts/smoke-test-out/v4/{scene-prompt,seedance-prompt}.txt,
# submits Nano Banana 2 + Seedance 2.0 via kie.ai, downloads result,
# runs post-ungrade.sh, opens in QuickTime.
#
# Cost: ~$2 (one image + one 15s Seedance Standard 720p).

set -euo pipefail

ROOT="${KWA_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
V4="$ROOT/scripts/smoke-test-out/v4"

# shellcheck disable=SC1091
if [[ -f "$ROOT/.env" ]]; then source "$ROOT/.env"; fi
if [[ -z "${KIE_AI_API_KEY:-}" ]]; then
  echo "FAIL: KIE_AI_API_KEY missing" >&2; exit 1
fi

KIE_BASE="https://api.kie.ai/api/v1/playground"
SCENE_PROMPT="$(cat "$V4/scene-prompt.txt")"
SEEDANCE_PROMPT="$(cat "$V4/seedance-prompt.txt")"

echo "=== Phase B.5.2 v4 — guerrilla iPhone, two girls + axolotl ==="
echo "Started: $(date)"

##############################################################################
# Step 1 — Nano Banana 2: muddy lakebed scene reference
##############################################################################
echo
echo "[1/2] Nano Banana 2 image gen..."
T0=$(date +%s)

IMAGE_SUBMIT=$(jq -n --arg p "$SCENE_PROMPT" '{
  model: "nano-banana-2",
  input: {prompt: $p, output_format: "png", image_size: "1:1"}
}' | curl -sS -X POST "$KIE_BASE/createTask" \
  -H "Authorization: Bearer $KIE_AI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @-)

IMAGE_TASK=$(echo "$IMAGE_SUBMIT" | jq -r '.data.taskId // empty')
if [[ -z "$IMAGE_TASK" ]]; then
  echo "FAIL: image submit"; echo "$IMAGE_SUBMIT"; exit 1
fi
echo "  taskId: $IMAGE_TASK"

while :; do
  IMG=$(curl -sS "$KIE_BASE/recordInfo?taskId=$IMAGE_TASK" \
    -H "Authorization: Bearer $KIE_AI_API_KEY")
  STATE=$(echo "$IMG" | jq -r '.data.state // "unknown"')
  echo "  state: $STATE  ($(date +%H:%M:%S))"
  case "$STATE" in
    success) break ;;
    fail)
      echo "FAIL: image gen"; echo "$IMG" | jq '.data | {state, failCode, failMsg}'
      exit 1 ;;
  esac
  sleep 3
done

IMAGE_URL=$(echo "$IMG" | jq -r '.data.resultJson | fromjson | .resultUrls[0]')
T1=$(date +%s)
echo "  url: $IMAGE_URL"
echo "  time: $((T1-T0))s"
curl -sS -o "$V4/scene.png" "$IMAGE_URL"

##############################################################################
# Step 2 — Seedance 2.0 with reference image, dialogue, anti-cinematic prompt
##############################################################################
echo
echo "[2/2] Seedance 2 video gen (15s, 9:16, 720p)..."
T2=$(date +%s)

VIDEO_SUBMIT=$(jq -n --arg p "$SEEDANCE_PROMPT" --arg url "$IMAGE_URL" '{
  model: "bytedance/seedance-2",
  input: {
    prompt: $p, image_url: $url,
    duration: 15, resolution: "720p", aspect_ratio: "9:16"
  }
}' | curl -sS -X POST "$KIE_BASE/createTask" \
  -H "Authorization: Bearer $KIE_AI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @-)

VIDEO_TASK=$(echo "$VIDEO_SUBMIT" | jq -r '.data.taskId // empty')
if [[ -z "$VIDEO_TASK" ]]; then
  echo "FAIL: video submit"; echo "$VIDEO_SUBMIT"; exit 1
fi
echo "  taskId: $VIDEO_TASK"

while :; do
  VID=$(curl -sS "$KIE_BASE/recordInfo?taskId=$VIDEO_TASK" \
    -H "Authorization: Bearer $KIE_AI_API_KEY")
  STATE=$(echo "$VID" | jq -r '.data.state // "unknown"')
  echo "  state: $STATE  ($(date +%H:%M:%S))"
  case "$STATE" in
    success) break ;;
    fail)
      echo "FAIL: video gen"; echo "$VID" | jq '.data | {state, failCode, failMsg}'
      exit 1 ;;
  esac
  sleep 10
done

VIDEO_URL=$(echo "$VID" | jq -r '.data.resultJson | fromjson | .resultUrls[0]')
T3=$(date +%s)
echo "  url: $VIDEO_URL"
echo "  time: $((T3-T2))s"
curl -sS -o "$V4/raw.mp4" "$VIDEO_URL"

##############################################################################
# Step 3 — Post-ungrade
##############################################################################
echo
echo "[post] Running post-ungrade.sh..."
"$ROOT/scripts/post-ungrade.sh" "$V4/raw.mp4" "$V4/final.mp4"

echo
echo "=== Done ==="
echo "Raw Seedance:  $V4/raw.mp4"
echo "Post-ungrade:  $V4/final.mp4"
echo "Image used:    $V4/scene.png"
