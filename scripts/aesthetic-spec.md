# KWA Aesthetic Spec

The single source of truth for what a Kissing Weird Animals episode should look, feel, and sound like. Every prompt (image + video) and every post-production step is derived from this spec. If a question comes up during production that isn't answered here, answer it here first, then act.

Reference frames were pulled from a third-party compilation of amateur animal-encounter clips (not included in this repo). That video is a montage; KWA produces single clips. The reference matters for **per-clip aesthetic markers**, not structure.

The smoke test (`smoke-test-out/smoke-video.mp4`) is the negative example — it verified the technical pipeline but failed the aesthetic. Comparing back to it sharpens the spec.

## 1. Camera motion

Three permitted modes. Pick one per episode based on what the action demands.

| Mode | When to use | Reference |
|---|---|---|
| **Locked off** | Animal does the action; operator can put the phone down or hold rock-still | Snake-yawn (frames 1–2): nearly identical 1s apart |
| **Hand-held micro-shake** | Subject is in operator's hand or on a surface; phone in one hand | Tortoise-with-raspberry (frames 3–5): subpixel drift only |
| **Off-kilter drift** | Operator is re-aiming as subject moves; *the default for KWA episodes* | Tortoise-zoo (frames 9–10): clear lateral wander + small tilt corrections |

**Off-kilter drift = the move to nail.** It's slow lateral wander (operator subtly re-aiming), small tilt corrections, organic and a bit imperfect. It is **not** a smooth dolly, **not** a crane, **not** a float, **not** per-frame jitter.

**Anti-patterns (what the smoke video and Lever 1 v2 got wrong):**
- Smooth backward dolly + upward float = cinematic, kills the format.
- Per-frame random crop = high-frequency jitter, reads as broken video, not handheld.

**How it's achieved in post:** sinusoidal x/y crop offsets with frequencies in the 0.3–0.6 Hz range, amplitudes ±4–10 px on a 720-wide source. Phases offset between x and y so the motion isn't perfectly periodic.

## 2. Background — clutter and focus

**Cluttered, not curated.** Real-world objects belong in the background. They were not placed for the shot; they were already there.
- Tortoise+raspberry: parked car, suburban house, fence, grass.
- Python keeper: shelving units, equipment, cabinets, fluorescent fixtures.
- Snake clip: feeding bowl pushed to frame edge, plastic enclosure walls visible.

**Focus rule, derived from the reference frames:**
- **Subject in hand or close** (< 30 cm): background goes soft — mild fall-off, recognizable but not crisp.
- **Subject at body or mid distance** (~1m+): everything in focus.

**Anti-pattern:** the smoke video's mossy forest stream is curated and crisp throughout — wrong on both clutter and focus rules.

**Where this is expressed:** Nano Banana 2 image prompt — describe a real domestic or vocational setting (kitchen counter, pet-store backroom, suburban backyard), name specific clutter items (dish towel, faucet edge, mug, plastic bin, shelving), specify focus fall-off when subject is close.

## 3. Lighting

**Whatever was available.** No editorial grade. Auto white balance.
- Cloudy/overcast soft cool (tortoise+raspberry, starfish-on-hand)
- Mixed indoor: fluorescent overhead + warm secondary (snake)
- Even fluorescent overhead, slight green-cyan cast (python keeper)
- Harsh midday sun, hard shadows (boat starfish)
- Outdoor mid-day filtered through trees, slightly dappled (tortoise zoo)

**Each episode has its own ambient look** — not a unified "channel grade." Variation is itself a UGC tell.

**Anti-pattern: never golden hour.** None of the reference clips use the photogenic late-afternoon warmth the smoke video defaulted to. If a generated frame looks like a wedding photo, it's wrong.

**Where this is expressed:** image prompt — name the lighting condition explicitly ("overhead kitchen LED, slightly cool", "harsh midday sun", "overcast soft daylight"). Avoid: "golden hour", "cinematic lighting", "soft natural light filtering through leaves."

## 4. Lens / focal length

**Wide-angle phone main lens (~26mm equiv) when subject is in hand or close.**
- Mild barrel distortion at frame edges.
- Hand looks slightly oversized in foreground; closer items appear exaggerated.
- Reference: tortoise+raspberry, starfish-on-hand.

**Standard / mild telephoto (~52mm equiv) when subject is at body distance or further.**
- Less distortion, flatter look.
- Reference: python keeper, tortoise zoo.

**Anti-pattern:** the smoke video's grandma-close-up read as a 50mm portrait lens with no distortion — doesn't match a phone-in-hand framing.

**Where this is expressed:** image prompt — "wide-angle phone lens", "slight barrel distortion at edges", "hand looks slightly oversized".

## 5. Composition

**Off-center, asymmetric, sometimes awkward.**
- Tortoise zoo: tortoise dead-left, keeper right-center, tree fills upper third.
- Python keeper: keeper upper-center, snake fills bottom 2/3, edge of co-worker visible at left edge.
- Headroom is uneven — sometimes too tight, sometimes too generous.

**Implied principle:** the operator wasn't worrying about composition. They got the subject in frame; that was enough.

**Anti-pattern:** centered subject, neat headroom, rule-of-thirds — all read as professional.

**Where this is expressed:** image prompt — "subject framed slightly off-center", "uneven headroom", "amateur composition, not rule-of-thirds".

## 6. Texture / grain — DO NOTHING IN POST

**Locked decision (2026-04-30): no synthetic grain, no compression-artifact pass, no color crush, no vignette, no post-production motion drift.** Raw Seedance output is the deliverable.

**Why this changed:** we initially assumed AI video looks too clean and needs grit added in post. That's true for *cinematic* AI output. It's wrong for the kind of output the locked image+video prompt produces — the muddy setting, overcast flat lighting, amateur composition, handheld phone framing, and naturally imperfect lipsync already create the right grit at the content level. Adding fake grain on top reads as *processed*, which is the opposite of *real*. Watching the raw v4 vs the post-ungrade v4 side-by-side, the raw was unanimously the better video.

**What this means in practice:**
- The texture / grit dimension is fully driven by the **image prompt** (lighting language, composition language, "phone snapshot" framing) and the **video prompt** (anti-cinematic camera language, guerrilla-iPhone framing).
- `scripts/post-ungrade.sh` is deprecated — see top of file.
- Phone playback naturally darkens video slightly; trust that and don't pre-darken.
- Audio: don't EQ, don't loudnorm, don't filter. Imperfect Seedance audio reads as authentic.

## Captions and music

- **Captions:** TBD — defined at the end of Phase D when the visual recipe is locked.
- **Music underbed:** **NOT USED.** Per direction 2026-04-30: KWA episodes are silent except for diegetic audio (operator's voice, in-frame reactions, ambient sound from the scene). Guerrilla-iPhone aesthetic; a music bed would break the style.

## Cross-reference to production levers

| Spec dimension | Image prompt (Nano Banana 2) | Video prompt (Seedance 2) | Post (FFmpeg) |
|---|---|---|---|
| 1. Camera motion | — | Heavy (anti-cinematic clauses) | Heavy (sinusoidal drift) |
| 2. Background clutter | Heavy | Reaffirms | — |
| 2. Focus | Heavy (close = soft bg) | Reaffirms | — |
| 3. Lighting | Heavy | Reaffirms | Subtle (vignette + crush) |
| 4. Lens | Heavy | Reaffirms | — |
| 5. Composition | Heavy | Reaffirms | — |
| 6. Grain | — | — | Heavy (noise filter, re-encode) |
