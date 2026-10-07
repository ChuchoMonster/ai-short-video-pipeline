# KWA Production Recipe — locked 2026-04-30

The exact procedure for producing a Kissing Weird Animals episode that matches the v4 raw Seedance output (the validated reference). Follow this, not improvisation, until a future session explicitly relocks.

## The locked decisions (do not litigate these in-session)

1. **Raw Seedance output is the deliverable.** No post-production grain, no compression-artifact pass, no color crush, no vignette, no fake camera motion drift, no audio EQ, no loudness normalization. Seedance's natural output already contains the right amount of imperfection.
2. **No music underbed, ever.** Diegetic audio only — operator's voice, in-frame reactions, ambient outdoor sound from the scene. A music bed would break the handheld-phone-footage style.
3. **Captions are TBD.** Will be added at the very end of production once the visual recipe is fully validated across multiple episodes. Don't bake captions into the Seedance prompt.
4. **Geographic accuracy of animal-to-setting is optional.** Visual incongruity ("wait, an axolotl in a Texas lakebed?") makes the hook stronger. Pick whatever pairing produces the strongest hook.
5. **Two-character framing is allowed** (off-camera operator + in-frame approacher) and may actually be *better* than one-character — it justifies the locked-handheld viewpoint and creates natural off-camera dialogue.
6. **Single 1:1 reference image, animal-only (no people) in the scene.** Seedance generates the human(s) from the video prompt. The reference establishes the setting.

## The pipeline

1. **Pick** animal + creator archetype(s) + setting + payoff type (one of the seven from CLAUDE.md). 5 minutes.
2. **Write the image prompt** to `episodes-in-progress/NN/prompts/scene-prompt.txt` using the template below. Should describe the animal in its setting with no people.
3. **Write the video prompt** to `episodes-in-progress/NN/prompts/seedance-prompt.txt` using the template below. 5 beats, anti-cinematic camera language, full dialogue.
4. **Generate** via `scripts/run-episode.sh NN` — the canonical parameterized runner. Submits Nano Banana 2 → polls → submits Seedance 2 → polls → downloads. Output goes to `episodes-in-progress/NN/raw/raw.mp4`. **Do not run post-ungrade.** (Older per-episode runners like `run-06-v2.sh` and `run-v4.sh` are kept for traceability but should not be reused — adapt `run-episode.sh` instead.)
5. **Review** `episodes-in-progress/NN/raw.mp4` against the recipe-locked criteria below. If it fails on a specific dimension, regenerate with a targeted prompt edit. Don't fix in post.
6. **Upscale to 1080×1920**: run `scripts/finalize.sh NN`. Pure resolution change — lanczos scale, CRF 18 h264, audio bitstream-copied, no filters of any kind. Output goes to `final-episodes/NN/final.mp4`. This is the canonical deliverable.
7. **Write publish notes**: create `final-episodes/NN/publish-notes.md` with caption text per platform (TikTok / IG / YouTube Shorts), hashtags, AI-label setting (always ON), and posting date. Bio + per-platform tone live in CLAUDE.md as defaults — only deviations need to be in publish-notes.

## Image prompt template (Nano Banana 2)

The image is a 1:1 reference for Seedance. Seedance reframes to 9:16 in the video. **Animal alone in the setting — no people in the image.**

```
A phone snapshot of {ANIMAL_DESCRIPTION} in {SETTING_DESCRIPTION_WITH_CLUTTER}.
The {ANIMAL} is positioned slightly off-center toward the {QUADRANT}; the
{OPPOSITE_QUADRANT} shows {BACKGROUND_DETAIL}. Shot with an iPhone wide-angle
main camera held about a foot above the ground at a downward angle, slight
barrel distortion at the edges of the frame. {LIGHTING_DESCRIPTION} — flat,
NOT golden hour, NOT cinematic, NOT studio. Auto white balance. Background is
mildly out of focus, the {ANIMAL} is in focus. The composition is amateur —
slightly tilted, off-center, no rule-of-thirds, framing feels hasty. Mid-tier
phone camera quality, soft details, visible digital noise in the shadowed
areas, hint of compression artifacts on high-contrast edges. No people
visible. No text. No logos. No watermarks.
```

**Slot-filling guidance:**
- `{ANIMAL_DESCRIPTION}` — physical description that anchors the species (color, texture, size, distinguishing feature). Example: *"a real pink axolotl with feathery external gills"*.
- `{SETTING_DESCRIPTION_WITH_CLUTTER}` — the environment + at least 3 named real-world clutter items. Example: *"a shallow puddle of muddy water at the edge of a flat dirty lakebed in rural Arkansas or Oklahoma. The lakebed is cracked and dried in places, with reddish-brown mud, scattered weeds, broken cattails, dried grass, and a piece of driftwood visible at the edges of the frame"*.
- `{LIGHTING_DESCRIPTION}` — name a real ambient condition. Examples: *"overcast cloudy daylight, slightly cool color cast"*, *"harsh midday sun with hard shadows"*, *"overhead kitchen LED, slightly cool"*. **Never** use *"golden hour"*, *"cinematic lighting"*, *"soft natural light"*.

**Validated working example:** `episodes/01/prompts/scene-prompt.txt` (when Phase C lands) or `scripts/smoke-test-out/v4/scene-prompt.txt` (the validated reference).

## Video prompt template (Seedance 2.0 Standard, 720p, 9:16, 15s)

```
Guerrilla-style iPhone footage shot by {OPERATOR_DESCRIPTION}. The camera
does NOT dolly, does NOT crane, does NOT tilt, does NOT track, does NOT zoom,
does NOT float. {CAMERA_BEHAVIOR}. Wide-angle phone main camera, slight
barrel distortion at frame edges. {LIGHTING_DESCRIPTION_MATCHING_IMAGE}.
Composition is amateur, subject slightly off-center.

At 0 to 2 seconds (HOOK): {HOOK_BEAT_DESCRIPTION}. {HOOK_DIALOGUE_IF_ANY}.

At 2 to 6 seconds (SETUP): {SETUP_BEAT_DESCRIPTION}. {SETUP_DIALOGUE_IF_ANY}.

At 6 to 10 seconds (APPROACH/PUCKER): {APPROACH_BEAT_DESCRIPTION}.
{APPROACH_DIALOGUE_LIPSYNCED_FOR_ON_SCREEN_GIRL}.

At 10 to 13 seconds (PAYOFF): {PAYOFF_BEAT_DESCRIPTION}. {PAYOFF_DIALOGUE}.

At 13 to 15 seconds (TAIL): {TAIL_BEAT_DESCRIPTION}. {TAIL_DIALOGUE_IF_ANY}.

Diegetic audio only. No music, no soundtrack. Phone microphone quality —
voices clear, ambient outdoor sounds (light wind, ground textures), no
background music of any kind.
```

**Slot-filling guidance:**
- `{OPERATOR_DESCRIPTION}` — who is holding the phone, in concrete human terms. Example: *"a teenage girl holding the phone in one hand standing about four feet from her friend"*. This single line is what tells Seedance the camera is hand-held and roughly stationary.
- `{CAMERA_BEHAVIOR}` — what the operator does. Example: *"The phone stays pointed at roughly the same spot on the muddy lakebed throughout. Only natural unintentional micro-shake from the operator's hand and a small wobble or two when she reacts."*
- `{LIGHTING_DESCRIPTION_MATCHING_IMAGE}` — must match the image prompt's lighting one-for-one so the video doesn't fight the reference frame.
- `{*_BEAT_DESCRIPTION}` — concrete physical action, no metaphor. Example: *"a teenage girl in a pink hoodie and denim shorts walks into the frame from the right, hesitantly steps toward the axolotl, crouches down a few feet from it, and tilts her head curious and a little grossed out."*
- `{*_DIALOGUE_*}` — write the actual line in quotes. Specify *off-camera* vs *in-frame* (lipsynced). Specify the speaker's vocal tone (urgent / fascinated / laughing / breathy). Use natural teenage speech patterns. Example: *"oh my GOD what IS that?"*, *"AHHH it's slimy oh my god!"*

**Validated working example:** `scripts/smoke-test-out/v4/seedance-prompt.txt`.

## The 5-beat structure (15s, locked)

| Beat | Time | Purpose | Notes |
|---|---|---|---|
| HOOK | 0–2s | Animal alone, "what IS that?" | Tight handheld close-up. Camera nearly static. Off-camera reaction line lands by 1.5s mark. |
| SETUP | 2–6s | The approacher enters frame | They walk in from one side, take their position. Operator may comment off-camera. |
| APPROACH / PUCKER | 6–10s | Tension beat | Approacher reaches out, animal reacts, both girls react. **Critical**: in-frame girl's mouth must be visible and lip-synced for her line. |
| PAYOFF | 10–13s | The kiss / the seven types | Type 1 ("kisses back") was the safe pilot pick. Future episodes vary across the seven types. **Be explicit**: "presses her lips to the top of the head" — the smoke test grandma blew a kiss because the prompt was vague. |
| TAIL | 13–15s | Out-of-frame departure or last animal beat | Ends naturally. Loop is nice-to-have, not required. |

## Recipe-locked criteria (to declare an episode "good")

The episode passes if all five are yes:

1. **Camera reads as guerrilla iPhone**, not cinematic — no smooth dolly, no float, no tilt-up reveal.
2. **Setting reads as real and slightly cluttered**, not designed.
3. **Both characters' dialogue is audible**, in-frame girl is lip-synced, off-camera girl is just a voice.
4. **The kiss makes contact** with the animal's body. No air-kiss.
5. **The video doesn't visibly look "post-processed"** — no fake grain, no fake vignette, no fake jitter.

If any of the five fails, regenerate with a targeted prompt edit. Don't try to fix in post.

## Cost model (validated, per episode)

- Nano Banana 2 image: ~$0.12, ~50 seconds
- Seedance 2.0 Standard 720p 15s with reference image: ~$1.88, ~3.5–6 minutes
- **Total per generation: ~$2, ~5–7 minutes wall time**
- Add 1–2 retries during prompt iteration for early episodes. Steady-state target: $3–5 per episode, 60–90 min wall time including writing prompts.

## What NOT to do

- **Don't run `scripts/post-ungrade.sh`** — it's deprecated. Validated worse than raw Seedance.
- **Don't add music**, even briefly to "see how it feels." It breaks the format.
- **Don't generate the human in the reference image.** Seedance handles humans from the video prompt. Reference image = animal in setting only.
- **Don't use `image_size: "9:16"` for Nano Banana 2.** Verified ignored — kie.ai delivers 1024×1024 regardless. Use `"1:1"` and let Seedance reframe.
- **Don't use 11Labs for voice.** Seedance's native dialogue is good enough and avoids the multi-character voice mixing problem.
- **Don't use HeyGen.** No avatar pipeline needed.
- **Don't write captions into the Seedance prompt** ("the screen says...", "text appears..."). Captions are added in a separate post phase later, against a fully-locked visual track.
- **Don't reference golden hour, cinematic lighting, soft natural light, dramatic shadows, or any photographic vocabulary.** Use plain ambient terms.
- **Don't write smooth camera motion** ("the camera slowly pulls back to reveal..."). Replace with locked + handheld micro-shake language.
- **Don't set the scene in jungles, exotic wilderness, or destinations associated with wildlife/travel content.** Use places real people walk with phones — state park boardwalks, suburban backyards, ornamental ponds, hiking trails, rest stops, public parks. Validated 2026-05-03; the animal can stay incongruous to the setting (incongruity strengthens the hook), but the location must be a credible "I just happened to be there with my phone" spot. See `feedback_kwa_relatable_settings.md`.
- **Don't describe iconic species in stock-photo language.** Red-eyed tree frogs, monarch butterflies, axolotls in clear water, peacocks, etc. default to wildlife-magazine renderings if you describe them in maximum-iconic terms ("bright red eyes," "vivid green skin," "perfect specimen"). Use counter-prompts: muted colors, wet/dirty, off-angle pose, partial obscuring, "NOT wildlife photography." See `feedback_kwa_iconic_species_rendering.md`.
- **Don't open the video on slow curiosity.** First 2 seconds must be a JOLT — animal already mid-action + off-camera scream + adrenaline. Curiosity hooks ("what is that?", camera tilting up to reveal, slow buildup) lose the swipe-up war. See `feedback_kwa_jolt_hook_mechanics.md`.
- **Don't have the animal land on the camera lens.** Have it land on the on-screen character's outstretched hand instead — preserves the at-camera jolt without forcing an awkward lens-stick / phone-flip transition. See `feedback_kwa_jolt_hook_mechanics.md`.
- **Don't have the animal close its eyes / lean into / react sentimentally to the kiss.** Animal stays neutral — eyes open, posture unchanged. The joke is the human's effort vs the animal's non-reaction. See `feedback_kwa_jolt_hook_mechanics.md`.
- **Don't show the operator (camera holder).** They're behind the phone POV. Their body, face, hands, hair — never on screen. See `feedback_kwa_pov_and_framing.md`.
- **Don't keep the on-screen character's full face centered for more than ~0.5s at a time.** Anchor on hand/arm; show face only briefly (chin/mouth leaning in for kiss). Extended face screen-time exposes AI tells. See `feedback_kwa_pov_and_framing.md`.
- **Don't let the phone "flip" or "fly" during a startle.** Phone shakes in place; never leaves the operator's hand. See `feedback_kwa_pov_and_framing.md`.
- **Don't write dialogue without an emotional-delivery cue.** Bald lines like *"Mia: 'okay it's fine.'"* render bland. Add the vocal state inline: *"Mia, voice high and shaky from adrenaline despite her calm words, lipsynced: 'okay it's fine —'"*. Every line needs at least one delivery adjective. See `feedback_kwa_vocal_emotion.md`.
- **Don't leave the on-screen character's bare arms/legs visible during interaction.** AI renders forearms / inside-of-elbow / shins poorly. Default the kisser to long sleeves and long pants; emphasize "sleeves go down to wrists, never ride up" in the prompt. See `feedback_kwa_realism_grounding.md`.
- **Don't trust default animal scaling.** Without explicit scale prompts, AI renders animals at drama-size (mantis as big as a hand, frog palm-sized, etc.). Specify real-world dimensions in BOTH the image prompt and Seedance prompt: *"about 3 inches long, the size of his palm."* See `feedback_kwa_realism_grounding.md`.
- **Don't write "slightly off-center" and expect off-center.** Nano Banana defaults to centered; soft language reads as ignored. Use aggressive quadrant placement: *"FAR UPPER-LEFT QUADRANT, with about 70% of the frame to its right being empty surface."* See `feedback_kwa_realism_grounding.md`.
- **Don't write profanity in dialogue, ever.** Platform algorithms (TikTok, IG, YouTube) downrank cursing. No "fuck," "shit," "damn," etc. Substitute "oh god," "oh my god," "no no no," "dude," "holy crap," or just inarticulate screams/gasps. See `feedback_kwa_no_profanity.md`.
