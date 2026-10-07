#!/usr/bin/env bash
# Phase B smoke test — verifies kie.ai endpoint behavior end-to-end before
# committing to the production pipeline shape. Writes a result file at
# scripts/smoke-test.md
#
# Costs: ~$0.12 (Nano Banana 2 image) + ~$1.88 (Seedance 2.0 Standard 15s) ≈ $2.

set -euo pipefail

ROOT="${KWA_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
OUT="$ROOT/scripts/smoke-test-out"
RESULT="$ROOT/scripts/smoke-test.md"
mkdir -p "$OUT"

# shellcheck disable=SC1091
if [[ -f "$ROOT/.env" ]]; then source "$ROOT/.env"; fi

if [[ -z "${KIE_AI_API_KEY:-}" ]]; then
  echo "FAIL: KIE_AI_API_KEY not set after sourcing .env" >&2
  exit 1
fi

KIE_BASE="https://api.kie.ai/api/v1/playground"

echo "=== KWA smoke test ==="
echo "Started: $(date)"
echo

##############################################################################
# Step 1 — Nano Banana 2 image generation (vertical reference)
##############################################################################
echo "[1/2] Submitting Nano Banana 2 image gen..."
T0=$(date +%s)

IMAGE_SUBMIT=$(curl -sS -X POST "$KIE_BASE/createTask" \
  -H "Authorization: Bearer $KIE_AI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @- <<'JSON'
{
  "model": "nano-banana-2",
  "input": {
    "prompt": "A real pink axolotl with feathery external gills resting in shallow water at the edge of a mossy forest stream. Hyperreal close-up, golden afternoon light filtering through leaves, slight handheld phone aesthetic, vertical 9:16 composition, sharp focus on the axolotl, soft natural background. No text, no logos.",
    "output_format": "png",
    "image_size": "9:16"
  }
}
JSON
)
echo "  submit response: $IMAGE_SUBMIT"
IMAGE_TASK=$(echo "$IMAGE_SUBMIT" | jq -r '.data.taskId // empty')
if [[ -z "$IMAGE_TASK" ]]; then
  echo "FAIL: no taskId in image submit response" >&2
  exit 1
fi
echo "  taskId: $IMAGE_TASK"

while :; do
  IMG_INFO=$(curl -sS "$KIE_BASE/recordInfo?taskId=$IMAGE_TASK" \
    -H "Authorization: Bearer $KIE_AI_API_KEY")
  STATE=$(echo "$IMG_INFO" | jq -r '.data.state // "unknown"')
  echo "  state: $STATE  ($(date +%H:%M:%S))"
  case "$STATE" in
    success) break ;;
    fail)
      echo "FAIL: image gen failed" >&2
      echo "$IMG_INFO" | jq '.data | {state, failCode, failMsg}' >&2
      exit 1
      ;;
  esac
  sleep 3
done

IMAGE_URL=$(echo "$IMG_INFO" | jq -r '.data.resultJson | fromjson | .resultUrls[0]')
T1=$(date +%s)
IMAGE_DUR=$((T1 - T0))
echo "  image URL: $IMAGE_URL"
echo "  gen time: ${IMAGE_DUR}s"

curl -sS -o "$OUT/smoke-image.png" "$IMAGE_URL"
IMAGE_DIMS=$(ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height -of csv=p=0:s=x "$OUT/smoke-image.png")
echo "  image dimensions: $IMAGE_DIMS"
echo

##############################################################################
# Step 2 — Seedance 2.0 with reference image, 9:16, 15s, native dialogue
##############################################################################
echo "[2/2] Submitting Seedance 2 video gen (15s, 9:16, 720p, dialogue prompt)..."
T2=$(date +%s)

VIDEO_PROMPT=$(cat <<EOF
Hyperreal handheld phone-shot UGC aesthetic, slight natural jitter, golden afternoon forest light. At 0 to 1.5 seconds, tight handheld close-up of a real pink axolotl resting at the edge of a mossy forest stream, its feathery external gills waving gently. At 1.5 to 5 seconds, the camera pulls back to reveal a friendly Korean grandmother in a colorful traditional cardigan kneeling on the bank beside the stream, smiling warmly at the axolotl. At 5 to 8 seconds, she leans down toward the axolotl and gently puckers her lips. She says warmly: "oh my, hello little one." At 8 to 13 seconds, the axolotl playfully boops its nose against her lips and she laughs softly. At 13 to 15 seconds, she beams at the camera and looks back at the axolotl. Vertical 9:16. No text on screen, no logos.
EOF
)

VIDEO_SUBMIT=$(jq -n --arg p "$VIDEO_PROMPT" --arg url "$IMAGE_URL" '{
  model: "bytedance/seedance-2",
  input: {
    prompt: $p,
    image_url: $url,
    duration: 15,
    resolution: "720p",
    aspect_ratio: "9:16"
  }
}' | curl -sS -X POST "$KIE_BASE/createTask" \
  -H "Authorization: Bearer $KIE_AI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @-)

echo "  submit response: $VIDEO_SUBMIT"
VIDEO_TASK=$(echo "$VIDEO_SUBMIT" | jq -r '.data.taskId // empty')
if [[ -z "$VIDEO_TASK" ]]; then
  echo "FAIL: no taskId in video submit response" >&2
  exit 1
fi
echo "  taskId: $VIDEO_TASK"

while :; do
  VID_INFO=$(curl -sS "$KIE_BASE/recordInfo?taskId=$VIDEO_TASK" \
    -H "Authorization: Bearer $KIE_AI_API_KEY")
  STATE=$(echo "$VID_INFO" | jq -r '.data.state // "unknown"')
  echo "  state: $STATE  ($(date +%H:%M:%S))"
  case "$STATE" in
    success) break ;;
    fail)
      echo "FAIL: video gen failed" >&2
      echo "$VID_INFO" | jq '.data | {state, failCode, failMsg}' >&2
      exit 1
      ;;
  esac
  sleep 10
done

VIDEO_URL=$(echo "$VID_INFO" | jq -r '.data.resultJson | fromjson | .resultUrls[0]')
T3=$(date +%s)
VIDEO_GEN_DUR=$((T3 - T2))
echo "  video URL: $VIDEO_URL"
echo "  gen time: ${VIDEO_GEN_DUR}s"

curl -sS -o "$OUT/smoke-video.mp4" "$VIDEO_URL"

V_DIMS=$(ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height -of csv=p=0:s=x "$OUT/smoke-video.mp4")
V_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/smoke-video.mp4")
A_CODEC=$(ffprobe -v error -select_streams a:0 \
  -show_entries stream=codec_name -of csv=p=0 "$OUT/smoke-video.mp4" 2>/dev/null || echo "")
A_DUR=$(ffprobe -v error -select_streams a:0 \
  -show_entries stream=duration -of csv=p=0 "$OUT/smoke-video.mp4" 2>/dev/null || echo "")

##############################################################################
# Result file
##############################################################################
cat > "$RESULT" <<EOF
# Phase B Smoke Test — Result

Run at: $(date)

## What was tested

A single end-to-end pass through kie.ai:

1. **Nano Banana 2** — generate a vertical 9:16 reference image of an axolotl in a forest stream.
2. **Seedance 2.0 Standard** — generate a 15s 9:16 720p video using that image as the reference, with a Korean grandma character speaking a line of dialogue ("oh my, hello little one"). This single call exercises four briefing assumptions at once: 15s duration, 9:16 aspect, image-to-video reference, and native audio with dialogue/lipsync.

## Results

### Nano Banana 2

- Submit: HTTP 200, taskId \`$IMAGE_TASK\`
- Generation time: ${IMAGE_DUR}s
- Delivered dimensions (px): \`$IMAGE_DIMS\`
- Saved to: \`scripts/smoke-test-out/smoke-image.png\`
- URL (temporary): $IMAGE_URL

### Seedance 2.0 Standard

- Submit: HTTP 200, taskId \`$VIDEO_TASK\`
- Generation time: ${VIDEO_GEN_DUR}s
- Delivered dimensions (px): \`$V_DIMS\`
- Delivered duration (s): \`$V_DUR\`
- Audio codec: \`${A_CODEC:-NONE}\`
- Audio stream duration (s): \`${A_DUR:-n/a}\`
- Saved to: \`scripts/smoke-test-out/smoke-video.mp4\`
- URL (temporary): $VIDEO_URL

## Manual checks the script can't do

Open the saved video and confirm:

- [ ] **Native dialogue audible.** Did the grandma actually say "oh my, hello little one" (or some recognizable speech)?
- [ ] **Lipsync.** Does her mouth move with the words, or is it generic mouth motion?
- [ ] **Visual quality.** Does this look like phone-shot UGC, or like polished AI?
- [ ] **Loop quality.** Does the last frame cut cleanly to the first?

## Decisions this informs

- If \`Audio codec\` is empty / \`NONE\` → briefing audio plan is wrong; switch to silent Seedance + 11Labs voiceover composited in FFmpeg.
- If \`Delivered duration\` < 15 → 15s is not supported for Seedance 2.0 Standard with reference image; format spec drops to whatever max worked (likely 10s).
- If \`Delivered dimensions\` width > height → 9:16 was ignored; need to investigate whether to crop in post or change call shape.
- If lipsync is bad even though audio is present → might still need to layer 11Labs on top for production polish.

EOF

echo
echo "=== Done ==="
echo "Result file: $RESULT"
echo "Open video:  open $OUT/smoke-video.mp4"
echo "Open image:  open $OUT/smoke-image.png"
