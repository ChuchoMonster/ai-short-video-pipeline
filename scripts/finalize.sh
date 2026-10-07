#!/usr/bin/env bash
# KWA finalize — promotes a reviewed raw Seedance output to a 1080x1920
# publish-ready file in final-episodes/NN/. Lanczos upscale, CRF 18 h264
# (visually lossless), audio re-encoded to AAC 96k to stay under Buffer's
# Instagram 128kbps cap (Seedance's native audio runs 128-130kbps and gets
# rejected). Per the locked production recipe (no post-production beyond
# resolution + audio-cap compliance).
#
# Usage: finalize.sh <episode-number>
#   e.g. finalize.sh 01
#
# Reads:  episodes-in-progress/<NN>/raw.mp4
# Writes: final-episodes/<NN>/final.mp4
#
# If the source raw is not at episodes-in-progress/<NN>/raw.mp4, set
# KWA_RAW_PATH env var to override.

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <episode-number>  (e.g. $0 01)" >&2
  exit 2
fi

NN="$1"
ROOT="${KWA_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
RAW="${KWA_RAW_PATH:-$ROOT/episodes-in-progress/$NN/raw/raw.mp4}"
OUT_DIR="$ROOT/final-episodes/$NN"
OUT="$OUT_DIR/final.mp4"

if [[ ! -f "$RAW" ]]; then
  echo "Source not found: $RAW" >&2
  echo "Override with KWA_RAW_PATH=/path/to/raw.mp4 $0 $NN" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

echo "Source: $RAW"
echo "Target: $OUT"

ffmpeg -y -hide_banner -loglevel warning \
  -i "$RAW" \
  -vf "scale=1080:1920:flags=lanczos" \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p \
  -c:a aac -b:a 96k \
  -movflags +faststart \
  "$OUT"

echo
echo "=== Finalized episode $NN ==="
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,bit_rate \
  -show_entries format=duration \
  -of default=nw=1 "$OUT"
echo
echo "Open: open '$OUT'"
echo "Next: write $OUT_DIR/publish-notes.md before posting."
