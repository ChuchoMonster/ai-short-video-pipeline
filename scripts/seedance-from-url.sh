#!/usr/bin/env bash
# Run Seedance 2 with an existing image URL (e.g. from a prior Nano Banana 2 gen
# that the user has already approved). Avoids re-spending on a regen and
# avoids visual variance from non-deterministic image generation.
#
# Usage: seedance-from-url.sh <prompt_file> <image_url> <output_mp4>
# Cost: ~$1.88 per call (Seedance Standard 720p 15s).

set -euo pipefail

ROOT="${KWA_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

# shellcheck disable=SC1091
if [[ -f "$ROOT/.env" ]]; then source "$ROOT/.env"; fi
if [[ -z "${KIE_AI_API_KEY:-}" ]]; then
  echo "FAIL: KIE_AI_API_KEY missing" >&2; exit 1
fi

KIE_BASE="https://api.kie.ai/api/v1/playground"

PROMPT_FILE="${1:?usage: seedance-from-url.sh <prompt_file> <image_url> <output_mp4>}"
IMAGE_URL="${2:?usage: seedance-from-url.sh <prompt_file> <image_url> <output_mp4>}"
OUT_MP4="${3:?usage: seedance-from-url.sh <prompt_file> <image_url> <output_mp4>}"

if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "FAIL: prompt file not found: $PROMPT_FILE" >&2; exit 1
fi

PROMPT="$(cat "$PROMPT_FILE")"

echo "[$(date +%H:%M:%S)] Submitting Seedance 2 (15s, 9:16, 720p)..."
echo "  prompt: $PROMPT_FILE"
echo "  image:  $IMAGE_URL"
echo "  output: $OUT_MP4"

SUBMIT=$(jq -n --arg p "$PROMPT" --arg url "$IMAGE_URL" '{
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
  echo "FAIL: video submit"; echo "$SUBMIT"; exit 1
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
      echo "FAIL: video gen"
      echo "$RESP" | jq '.data | {state, failCode, failMsg}'
      exit 1 ;;
  esac
  sleep 10
done

URL=$(echo "$RESP" | jq -r '.data.resultJson | fromjson | .resultUrls[0]')
echo "  video URL: $URL"
curl -sS -o "$OUT_MP4" "$URL"
echo "  saved: $OUT_MP4"
