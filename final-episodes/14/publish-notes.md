# Episode 14 — publish notes

## Episode summary

- **File**: `final-episodes/14/final.mp4` — 15.07s, 1080×1920, 24fps, h264 CRF 18 + AAC 96k
- **Animal**: real wild Sonoran-desert horned lizard (Phrynosoma, ~5 inches, palm-sized; mottled muted dusty tan-brown body blending into the dirt, classic CROWN OF SHORT SHARP HORNS around its head, smaller backward-pointing spines along body edges, small alert dark eyes with the characteristic slightly-puffed eye-margins where the blood-squirt defense mechanism lives)
- **Setting**: dusty hard-packed dirt backyard at the edge of a Tucson suburb at late afternoon — Sonoran-desert country, cracked cream-tan stucco wall corner with chipped paint and barred window, sun-bleached prickly-pear cactus, faded weathered plastic patio chair, distant saguaro silhouettes; muted reddish-brown / tan / dusty palette
- **Cast**: Brandon (~25, on-screen, white American Southwest, lean wiry build, weathered tan face + grey-flecked stubble + sun-faded khaki ball cap pulled low + faded heather-grey long-sleeve thermal henley + dark blue jeans + dusty work boots; real human imperfections — beauty mark, visible pores, patchy stubble, chapped lower lip, sunburn line on neck, dark under-eye, asymmetric features) + Casey (off-camera operator, his ~24 girlfriend, casual American Southwest voice, walking handheld)
- **Payoff structure (type #6, kiss-causes-effect)**: silent buildup with Brandon's body-language hesitation 0–10s → physical lip-peck on the lizard's spiny head in wide framing → INSTANT blood-squirt from the lizard's left eye-margin (thin arc of dark red real-animal blood) → BRANDON FREAKS OUT panicking + frantically wiping his cheek with his sleeve while CASEY off-camera DIES LAUGHING with the phone bobbing up-down haphazardly from her body convulsions. Asymmetric reactions: he's panicked + disgusted, she's crying-laughing. First spoken words of the entire video come at second 10 when he yelps "OH —!"
- **Generation source**: `episodes-in-progress/14/raw/raw.mp4` (v5 — fifth iteration). v1 archived (phone-in-hand bug, fake-looking Brandon, delayed reaction). v2 archived (great realism but the kiss got skipped entirely). v3 archived (kiss rendered but too-close-up, weird AI-looking scar on neck). v4 archived (good but Brandon and Casey appeared too co-equal / side-by-side feeling — also still some talking in buildup). v5 = no scars + kiss in wide framing + Casey strictly behind camera + Brandon sole subject in frame + NO TALKING until the kiss + silent body-language hesitation.
- **Cost to produce**: ~$9.52 (one image $0.12 + five Seedance attempts $1.88 each, image reused on v2/v3/v4/v5 saved $0.48; v2 was recovered from an orphan task ID after a DNS-resolution failure mid-poll — no extra spend, just a recovery via direct `recordInfo?taskId=` query)
- **Production date**: 2026-05-12 / 2026-05-13
- **Format breakthroughs**:
  - **NO TALKING UNTIL THE KISS rule.** First KWA episode where the entire buildup (0–10s) is silent except for ambient + soft involuntary off-camera giggles. The first spoken word of the video is Brandon's panic-yelp at second 10 when the blood hits him. Body-language hesitation only during the buildup — Brandon leans forward, pulls back, repeats. Powerful realism multiplier. Worth adding as a permanent option in the playbook for episodes where the payoff is shocking enough that buildup chatter would dilute it.
  - **Operator-behind-subject framing variant.** Previously the [camera-framing memory](feedback_kwa_camera_framing_dual_volume.md) defaulted to "operator-beside-subject + partially-in-frame." This episode validates the alternative: "operator strictly behind camera, subject is sole on-screen human, wide angle, walking handheld." User feedback specifically requested this framing for Ep14 because the side-by-side framing was making Brandon read as co-operator instead of subject. Both framings are valid — operator-beside-subject works well when both characters are chattering/interacting; operator-behind-subject works better for silent-buildup or sole-focus-on-subject episodes.
  - **Kiss-in-wide-framing rule.** Explicit prompt-rule that the kiss MUST be rendered at wide angle, both subject and animal visible in the same frame. Fights Seedance's tendency to zoom in for the kiss action which reads as cinematic instead of phone-bystander.
  - **No-scar exclusion rule for anti-AI counter-prompts.** Discovered that specifying a "faded scar" as an anti-AI imperfection backfires — AI renders scars in an artificial-looking way that reads MORE AI, not less. Better imperfections to use: beauty marks, visible pores, patchy stubble, chapped lips, sunburn lines, dark under-eye, asymmetric features, dirt smudges. Scars are off-limits.
  - **Kiss-must-be-rendered explicit rule.** v2 dropped the kiss entirely because the dense reaction-prompt language crowded it out. v3+ adds explicit top-level rule "THE KISS CANNOT BE SKIPPED" with dedicated 2-second beat. Now the kiss reliably renders.

## Caption text — copy/paste ready

The recommended caption for each platform is the first one. Alternates are safe swaps if the recommended doesn't feel right.

### TikTok (recommended)

```
my boyfriend kissed a lizard and it SHOT BLOOD AT HIS FACE

#fyp #weirdanimals #kissingweirdanimals
```

Alternates:
- `the lizard shot blood out of its EYE 😭 #fyp #weirdanimals #kissingweirdanimals`
- `babe i told you not to 💀 #fyp #weirdanimals #kissingweirdanimals`
- `arizona desert finds are unmatched #fyp #weirdanimals #hornedlizard`

### Instagram Reels (recommended)

```
horned lizards squirt blood from their eyes and my boyfriend just learned that the hard way

#weirdanimals #kissingweirdanimals #fyp
```

Alternates:
- `the way he FREAKED 😭 #weirdanimals #kissingweirdanimals`
- `brandon please leave the wildlife alone #weirdanimals #kissingweirdanimals`
- `wild horned lizard in a tucson backyard #weirdanimals #arizona`

### YouTube Shorts (recommended)

```
guy kisses a horned lizard — lizard SQUIRTS BLOOD at his face 🦎 #Shorts

#weirdanimals #kissingweirdanimals #hornedlizard
```

Alternates:
- `the horned lizard's secret defense move #Shorts #weirdanimals`
- `brandon, your worst decision of the year #Shorts #weirdanimals`
- `wild horned lizard in the Sonoran desert #Shorts #kissingweirdanimals`

### Facebook Reels (recommended)

Same as Instagram Reels above. If IG↔FB cross-post is connected, FB will pick up automatically.

## Platform metadata settings

| Platform | AI-content label | Cover/thumbnail | Other |
|---|---|---|---|
| **TikTok** | **ON** — "AI-generated content" label. The scheduler sends TikTok posts as a Buffer notification by default so the final publish happens in the TikTok app, where this label can be set. | Pick a frame from 0–1s — the lizard alone in the dust with its spiny crown clearly visible. The "what's that spiky thing in the corner" framing is the stop-scroll. | Leave auto-captions OFF. |
| **Instagram Reels** | **ON** — apply the AI-generated label ("AI info"). | Same — pre-kiss lone-lizard frame. | Share to Feed: yes. Auto-captions default. |
| **YouTube Shorts** | **YES** — "Altered or synthetic content" in upload details / YouTube Studio. | Auto-thumbnail fine for Shorts. **NOTE — possible age restriction**: the visible blood-spatter in the payoff may trigger YT's age-restriction filter. If it does, accept it — the educational pin angle makes this clearly biology content, not gore. | Confirm `#Shorts` in description. |
| **Facebook Reels** | **ON** — apply the AI-generated label. | Auto-thumbnail fine. | If connected to IG, auto-cross-posts. |

**⚠ Blood-content moderation note.** This episode has a visible (small, biologically-real) blood spatter on Brandon's cheek. Real horned-lizard biology, but platform AI-moderation may still flag it. Risks:
- **TikTok**: low risk — community guidelines allow real-animal content including defensive behaviors. The dark-red spatter is small and consistent with the educational framing.
- **Instagram**: low-medium risk — Meta's automated review may delay distribution. If the post gets restricted, appeal citing real biology + educational content.
- **YouTube**: medium risk for age restriction. If restricted, leave the restriction in place — age-restricted Shorts still get distributed to logged-in adult viewers.

> **AI disclosure:** this episode is entirely AI-generated (Nano Banana image + Seedance video). Label it as AI-generated on every platform that supports or requires it, and keep the `AI-generated video` line that `schedule_episode.py` appends to every caption by default.

## Posting plan

- **Date**: Friday 2026-05-15
- **Time**: ~6 PM CT / 7 PM ET
- **Order**: post all four platforms within ~30 minutes of each other
- **First 60 min**: stay on the device; reply to every comment; like every comment; check for any moderation flags on the blood content

## Pinned comment candidates

The "horned lizards squirt blood from their eyes" fact is gold — viewers will spam "wait that's REAL?" — give them the biology.

- **`fun fact: horned lizards squirt blood from the corner of their eyes as a defense mechanism — they rupture small blood vessels near their tear ducts and can shoot it up to 3 feet. The blood is foul-tasting to coyotes and dogs. Brandon found out. 🦎`** ← strongest, lean on this
- `horned lizards do this in the wild against canine predators. Brandon was apparently the same threat profile.`
- `the way the lizard waited until AFTER the kiss to fire`
- `babe please go wash your face`
- `casey is no help. casey is part of the problem. casey is dying.`
- `the audible "OH —" is a man whose worldview has shifted in real time`

## Performance to track

| Metric | 1 hr | 24 hr | 7 day | 30 day |
|---|---|---|---|---|
| TikTok views | | | | |
| TikTok completion % | | | | |
| TikTok shares | | | | |
| TikTok comments | | | | |
| TikTok saves | | | | |
| IG Reels views | | | | |
| IG Reels saves | | | | |
| IG Reels shares | | | | |
| YT Shorts views | | | | |
| YT Shorts likes | | | | |
| FB Reels views | | | | |
| New followers (TT/IG/YT/FB) | | | | |

## Notes after posting

(Fill in after posting — anything surprising, things to change for episode 15. Four big format-validation data points: (1) does the silent-buildup-into-shock-payoff structure drive better first-3-second retention than chattier-buildup episodes? (2) does the operator-behind-subject framing read differently than the operator-beside-subject framing of Ep12 marine iguana? (3) does the visible blood get any platform moderation pushback — and if so does it depress reach? (4) does asymmetric payoff (one panics, one laughs) outperform symmetric payoff (both react together)?)
