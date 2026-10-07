#!/usr/bin/env bash
# *** DEPRECATED 2026-04-30 ***
#
# This script applied a multi-stage "ungrade" pass (sine-drift motion, split
# luma+chroma noise, color crush, vignette, CRF 32 re-encode, audio highpass+EQ
# +loudnorm) to make AI-clean Seedance output read as phone-shot UGC. The
# approach was validated against raw Seedance output and lost — the raw was
# unanimously the better video. The post-processed version read as
# *processed* (fake grain, dark corners, soft details), which hurt the
# naturalistic look more than the AI cleanness ever did.
#
# Production recipe: ship raw Seedance output. See:
#   scripts/production-recipe.md
#   scripts/aesthetic-spec.md  (Section 6)
#
# This script is kept (not deleted) so the rationale for why we don't post-process
# is recoverable from the file history, and so anyone tempted to "just add a
# little grain" can read this header and reconsider.
#
# If you genuinely need a post pass for a future use case (e.g. burning in
# captions, exporting platform variants), write a NEW script with a NEW name —
# don't repurpose this one.
#
# Original usage: post-ungrade.sh <input.mp4> <output.mp4>

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <input.mp4> <output.mp4>" >&2
  exit 2
fi

IN="$1"
OUT="$2"

if [[ ! -f "$IN" ]]; then
  echo "Input not found: $IN" >&2
  exit 1
fi

# Video filter chain (order matters):
#   1. scale up slightly larger than 1080x1920 -> creates margin for drift
#   2. crop to 1080x1920 with smooth sinusoidal x/y offset per frame ->
#      simulates the off-kilter handheld drift from spec dim 1.
#      Two-sine sum (different frequencies, different phases) so the motion
#      doesn't read as periodic.
#        x in [0, 20] over time, two sines at ~0.35 Hz and ~0.11 Hz
#        y in [0, 36] over time, two sines at ~0.50 Hz and ~0.18 Hz
#   3. eq -> contrast bump, slight desat, slight darken (phones clip differently)
#   4. noise -> phone-sensor grain (split luma/chroma per spec dim 6;
#      smaller per-channel strength than v2's film-style alls=10)
#   5. vignette -> cheap phone lens fall-off
VFILTERS="scale=1100:1956,crop=1080:1920:'10+8*sin(t*2.2)+2*sin(t*0.7+0.5)':'18+12*sin(t*3.14+1.2)+6*sin(t*1.1)',eq=contrast=1.08:saturation=0.92:brightness=-0.02,noise=c0s=8:c1s=5:c2s=5:allf=t+u,vignette=PI/5"

# Audio filter chain:
#   1. highpass at 100 Hz -> kills the boomy low-end John flagged
#   2. equalizer mid-dip at 200 Hz -> further reduces "stereo system" feel
#   3. loudnorm -> -16 LUFS for short-form platforms
AFILTERS="highpass=f=100,equalizer=f=200:t=q:w=1:g=-3,loudnorm=I=-16:LRA=11:TP=-1.5"

ffmpeg -y -hide_banner -loglevel warning \
  -i "$IN" \
  -vf "$VFILTERS" \
  -af "$AFILTERS" \
  -c:v libx264 -crf 32 -preset veryfast -profile:v baseline -level 3.1 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  "$OUT"

echo "Wrote: $OUT"
ffprobe -v error -show_entries format=duration:stream=width,height,codec_name -of default=nw=1 "$OUT"
