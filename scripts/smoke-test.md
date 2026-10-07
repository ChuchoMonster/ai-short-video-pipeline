# Phase B Smoke Test — Result

Run at: Wed Apr 29 17:18:02 CDT 2026

## What was tested

A single end-to-end pass through kie.ai:

1. **Nano Banana 2** — generate a vertical 9:16 reference image of an axolotl in a forest stream.
2. **Seedance 2.0 Standard** — generate a 15s 9:16 720p video using that image as the reference, with a Korean grandma character speaking a line of dialogue ("oh my, hello little one"). This single call exercises four briefing assumptions at once: 15s duration, 9:16 aspect, image-to-video reference, and native audio with dialogue/lipsync.

## Results

### Nano Banana 2

- Submit: HTTP 200, taskId `7c9269fe2d7391f7f091aeaabff0da4d`
- Generation time: 50s
- Delivered dimensions (px): `1024x1024`
- Saved to: `scripts/smoke-test-out/smoke-image.png`
- URL (temporary): https://tempfile.aiquickdraw.com/images/1777500723083-gqltlm424t.png

### Seedance 2.0 Standard

- Submit: HTTP 200, taskId `20be77b6c5fc713fd78555abafd8a75a`
- Generation time: 354s
- Delivered dimensions (px): `720x1280`
- Delivered duration (s): `15.069002`
- Audio codec: `aac`
- Audio stream duration (s): `15.069002`
- Saved to: `scripts/smoke-test-out/smoke-video.mp4`
- URL (temporary): https://tempfile.aiquickdraw.com/seedance/1777501069916-zn7fqmofx09.mp4

## Manual checks the script can't do

Open the saved video and confirm:

- [ ] **Native dialogue audible.** Did the grandma actually say "oh my, hello little one" (or some recognizable speech)?
- [ ] **Lipsync.** Does her mouth move with the words, or is it generic mouth motion?
- [ ] **Visual quality.** Does this look like phone-shot UGC, or like polished AI?
- [ ] **Loop quality.** Does the last frame cut cleanly to the first?

## Decisions this informs

- If `Audio codec` is empty / `NONE` → briefing audio plan is wrong; switch to silent Seedance + 11Labs voiceover composited in FFmpeg.
- If `Delivered duration` < 15 → 15s is not supported for Seedance 2.0 Standard with reference image; format spec drops to whatever max worked (likely 10s).
- If `Delivered dimensions` width > height → 9:16 was ignored; need to investigate whether to crop in post or change call shape.
- If lipsync is bad even though audio is present → might still need to layer 11Labs on top for production polish.

