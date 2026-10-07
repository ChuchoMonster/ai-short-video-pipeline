# Episode 06 v2 — Edit Plan

## Structure
**Single 15s shot, no stitch.** Replaces v1 two-shot bridge scene (archived in `archive/v1-bridge/`).

## Scene
- **Setting:** Costa Rican cloud forest, off-trail, in front of a thick mossy tree. No bridge.
- **Animal:** Three-toed sloth wedged in a low V-fork at chest height, camouflaged into mossy bark.
- **Cast:** Jack (Australian, off-camera operator), Camila (Brazilian, voice-only at start, walks into frame at 7s).
- **Mechanism:** Camila's deliberate decision against Jack's protests.
- **Payoff:** Type 4 deadpan / human-comedy hybrid. Sloth doesn't react — the joke is Camila's casualness + Jack's disbelief.

## Beat structure (15s)
- 0–2s HOOK — Jack hand-tilts phone up the tree trunk, "babe... babe babe — hey babe — look. look. look."
- 2–5s SHE STILL CAN'T SEE IT — sloth is camouflaged. Camila: "what?... what?" / Jack: "look, look — right there —" / "the FORK. the fork."
- 5–7s SHE FINALLY SEES IT — Camila: "ohhh — oh my god." / both whisper-giggle.
- 7–9s HE BACKS UP, SHE STEPS IN — Camila enters frame from right with backpack on, walks toward tree. Jack: "wait — wait — what are you — babe —"
- 9–12s BACKPACK OFF, KISS — Camila slowly slips backpack off both shoulders, lowers it to ground. Jack: "what are you DOING. what are you DOING." She leans in, presses lips to top of sloth's head. Jack: "no — no no no — babe no — BABE —" Sloth does NOT react.
- 12–14s GETAWAY — Camila giggles, grabs backpack by one strap, scuttles past camera off frame right.
- 14–15s JACK ALONE — camera holds on sloth, Jack laughs once in disbelief, "she just — she just —"

## Production
- 1× Nano Banana 2 image (scene-prompt.txt, 1:1, animal + setting only, no people)
- 1× Seedance Standard 720p 15s (seedance-prompt.txt, image-to-video, 9:16)
- No FFmpeg stitch needed.
- Output: `raw/raw.mp4` directly.

## Cost estimate
- Nano Banana 2: ~$0.12, ~50s
- Seedance Standard 720p 15s: ~$1.88, ~3.5–6 min
- **Total: ~$2.00, ~5–7 min wall time.**

## Recipe-locked checks (review after raw lands)
1. Camera reads as guerrilla iPhone — only the deliberate hand-tilt-up at 0–2s and natural micro-shake elsewhere. No dolly, no float, no smooth motion.
2. Setting reads as real cluttered jungle, not designed.
3. Both characters' dialogue is audible. Camila is lipsynced when in frame (9s onward). Jack is voice-only.
4. The kiss makes contact with the top of the sloth's head — clear lip-on-fur contact.
5. The video doesn't visibly look "post-processed."
6. **NEW v2 check:** the sloth doesn't react. No kissing back, no head turn, no blink during the kiss.

If any check fails, regenerate with a targeted prompt edit. Don't try to fix in post.
