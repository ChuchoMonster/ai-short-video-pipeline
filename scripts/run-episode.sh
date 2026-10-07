#!/usr/bin/env bash
# KWA per-episode runner — Nano Banana 2 (scene-prompt) → Seedance 2 (seedance-prompt) → raw.mp4
# Usage: run-episode.sh <episode-number>   e.g. run-episode.sh 03
#
# Reads:
#   episodes-in-progress/<NN>/prompts/scene-prompt.txt
#   episodes-in-progress/<NN>/prompts/seedance-prompt.txt
# Writes:
#   episodes-in-progress/<NN>/reference/ref.png
#   episodes-in-progress/<NN>/raw/raw.mp4
#   episodes-in-progress/<NN>/run.log
#
# Per the locked production recipe: image is 1:1 (image_size "9:16" silently
# ignored by KIE.AI; Seedance reframes from 1:1). Seedance is 720p 9:16 15s.
# No post-production — raw.mp4 is the deliverable. Promote via finalize.sh.
#
# Cost: ~$2 (image $0.12 + Seedance Standard 720p 15s $1.88).

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <episode-number>  (e.g. $0 03)" >&2
  exit 2
fi

NN="$1"
ROOT="${KWA_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
EP="$ROOT/episodes-in-progress/$NN"
LOG="$EP/run.log"

# shellcheck disable=SC1091
if [[ -f "$ROOT/.env" ]]; then source "$ROOT/.env"; fi
if [[ -z "${KIE_AI_API_KEY:-}" ]]; then
  echo "FAIL: KIE_AI_API_KEY not set (export it or put it in $ROOT/.env)" >&2
  exit 1
fi

mkdir -p "$EP/reference" "$EP/raw"

SCENE_PROMPT="$EP/prompts/scene-prompt.txt"
SEEDANCE_PROMPT="$EP/prompts/seedance-prompt.txt"
[[ -f "$SCENE_PROMPT" ]]    || { echo "FAIL: missing $SCENE_PROMPT" >&2; exit 1; }
[[ -f "$SEEDANCE_PROMPT" ]] || { echo "FAIL: missing $SEEDANCE_PROMPT" >&2; exit 1; }

KIE_BASE="https://api.kie.ai/api/v1/playground"
RESP_TMP="$EP/.poll-resp.json"
log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

# Polling helper: writes response to temp file, parses with python3 (more robust
# than jq for the very large nested-escape payloads Seedance returns — Seedance
# echoes the entire submitted prompt back inside `param` as escaped JSON, which
# can break jq parsing). Caps poll at $1 attempts to prevent infinite-loop hangs.
#   $1 = max polls
#   $2 = sleep seconds between polls
#   $3 = task id
#   $4 = label for log lines (e.g. "img" or "vid")
poll_until_done() {
  local max="$1" interval="$2" task="$3" label="$4"
  for i in $(seq 1 "$max"); do
    curl -sS -m 30 --retry 3 --retry-delay 5 \
      "$KIE_BASE/recordInfo?taskId=$task" \
      -H "Authorization: Bearer $KIE_AI_API_KEY" > "$RESP_TMP" || {
        log "[$label] poll $i/$max: curl failed, retrying"
        sleep "$interval"; continue
      }
    local state
    state=$(python3 -c "import json,sys
try: print(json.load(open(sys.argv[1])).get('data',{}).get('state','unknown'))
except Exception as e: print('parse_error:'+str(e)[:80])" "$RESP_TMP" 2>/dev/null || echo "parse_error")
    log "[$label] state: $state (poll $i/$max)"
    case "$state" in
      success) return 0 ;;
      fail)
        log "[$label] FAIL — task reported failure"
        cat "$RESP_TMP" | tee -a "$LOG"
        return 1 ;;
    esac
    sleep "$interval"
  done
  log "[$label] TIMEOUT after $max polls of ${interval}s"
  return 2
}

# Extract value from the polled response file. python3 instead of jq for same
# payload-size reasons.
#   $1 = python expression returning a string from `data` dict
extract_resp() {
  python3 -c "import json,sys
d = json.load(open(sys.argv[1]))['data']
print($1)" "$RESP_TMP"
}

log "=== Episode $NN ==="
log "Started: $(date)"

##############################################################################
# Step 1 — Nano Banana 2: scene reference image
##############################################################################
log
log "[img] Submitting Nano Banana 2..."
T0=$(date +%s)

SUBMIT=$(jq -n --arg p "$(cat "$SCENE_PROMPT")" '{
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

# Poll up to 200 * 3s = 10 min for image (image gen typically <60s)
poll_until_done 200 3 "$TASK" "img" || exit 1

URL_IMG=$(extract_resp "json.loads(d['resultJson'])['resultUrls'][0]")
log "[img] image URL: $URL_IMG"
curl -sS -o "$EP/reference/ref.png" "$URL_IMG"
T1=$(date +%s)
log "[img] saved: $EP/reference/ref.png"
log "[img] elapsed: $((T1-T0))s"

##############################################################################
# Step 2 — Seedance 2 with reference image (15s 9:16 720p)
##############################################################################
log
log "[vid] Submitting Seedance 2 (15s, 9:16, 720p)..."

SUBMIT=$(jq -n --arg p "$(cat "$SEEDANCE_PROMPT")" --arg url "$URL_IMG" '{
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

# Poll up to 120 * 10s = 20 min for video (Seedance Standard 15s typically 4–8 min)
poll_until_done 120 10 "$TASK" "vid" || exit 1

URL_VID=$(extract_resp "json.loads(d['resultJson'])['resultUrls'][0]")
log "[vid] video URL: $URL_VID"
curl -sS -o "$EP/raw/raw.mp4" "$URL_VID"
T2=$(date +%s)
log "[vid] saved: $EP/raw/raw.mp4"
log "[vid] elapsed: $((T2-T1))s"

log
log "=== Done — Episode $NN ==="
log "Total wall time: $((T2-T0))s"
log "Outputs:"
log "  Reference image: $EP/reference/ref.png"
log "  Raw video:       $EP/raw/raw.mp4"
log
log "Next: review raw.mp4. If it passes recipe-locked criteria, run:"
log "  scripts/finalize.sh $NN"
