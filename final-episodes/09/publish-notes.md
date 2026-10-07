# Episode 09 — publish notes

## Episode summary

- **File**: `final-episodes/09/final.mp4` — 15.07s, 1080×1920, 24fps
- **Animal**: real wild capybara (~1m long, knee-high, Labrador-sized; muted brown-grey-russet damp coat with real river grit; behaves as actual capybaras do — extraordinarily relaxed, jaw moving slowly side-to-side, eyes half-closed, totally unbothered)
- **Setting**: dry-grass back portion of a residential Brazilian backyard in a small interior town, late afternoon, weathered timber fence, papaya tree, whitewashed concrete house corner, dropped soccer ball, scuffed hose. Muted desaturated palette throughout.
- **Cast**: Larissa (~32, on-screen, Brazilian, naturally attractive in a real-person way — explicit anti-AI counter-prompts: real skin texture with mild pores, sun-freckling, slight under-eye, asymmetric features, faded sun-bleached sand-beige long-sleeve linen henley + muted khaki-tan linen pants + brown leather sandals, dark hair in messy bun with flyaways, no makeup) + Mariana (off-camera operator, her ~30 friend, casual Brazilian Portuguese, real-friend chatter)
- **Payoff structure (warm-DEADPAN inverted variant of type #1)**: the animal's complete non-reaction IS the entire joke. Capybara never looks up, never blinks at the kiss, body language identical from second 0 to second 15. Two friends doing something stupid + the chillest mammal alive ignoring it.
- **Generation source**: `episodes-in-progress/09/raw/raw.mp4` (v5 — fifth iteration). v1 archived (dock-water setting, phantom-stranger kissing bug, too-close framing). v2 archived (woman looked fake/AI-rendered, framing too staged). v3 archived (hesitation happened from above the animal which was unrealistic + 4–5 cuts were too many). v4 archived as fallback (clean structure but Larissa landed less natural-looking). v5 = same prompt as v4, re-rolled for a better Larissa render — landed.
- **Cost to produce**: ~$9.92 (one image regen for new dry-grass setting $0.12 + five Seedance attempts $1.88 each, image reused on v3/v4/v5 saved $0.36; plus aborted camel concept ~$2 in `episodes-in-progress/_aborted/09-camel-2026-05-09/`)
- **Production date**: 2026-05-09
- **Format breakthroughs**: many durable rules introduced and validated:
  - **Hook on the animal alone (off-diagonal handheld wide).** First KWA episode where the cold-open is purely on the animal with no human context. Increases scroll-stop probability.
  - **Exactly ONE cut.** New explicit prompt-rule that caps within-clip cuts at exactly 1 (vs the 4–5 Seedance was rendering by default). Single sharp cut between the hook and beat 2; everything after is one continuous handheld shot.
  - **Hesitation from a distance, not above the animal.** Real-person physics: kisser leans torso forward / pulls back from 4–5 ft away, NOT from directly over the animal. Only when they commit do they walk forward and execute fast.
  - **Camera operator naturally backs up to widen frame.** Not a zoom-out — Mariana physically steps backward as Larissa approaches, which widens the framing organically.
  - **Anti-AI face counter-prompts validated.** Explicit "real skin texture, asymmetric features, no AI-perfect symmetry, sun-freckling, mild under-eye, real human imperfection" language got a natural-looking woman render (eventually — required a second roll on v5 to land).
  - **Desaturated color palette as a global rule.** "Slightly desaturated and dusty, no filters" prompt language — fights Seedance's default toward saturated grading.

## Caption text — copy/paste ready

The recommended caption for each platform is the first one. Alternates are safe swaps if the recommended doesn't feel right.

### TikTok (recommended)

```
told my friend to kiss the capybara and the capybara did NOT care

#fyp #weirdanimals #kissingweirdanimals
```

Alternates:
- `the chillest animal on earth is correct #fyp #weirdanimals #kissingweirdanimals`
- `she actually did it and the capybara just kept eating 😭 #fyp #weirdanimals #kissingweirdanimals`
- `me: vai vai vai. capybara: 🌿 #fyp #weirdanimals #capybara`

### Instagram Reels (recommended)

```
my friend kissed a wild capybara and the capybara was unbothered

#weirdanimals #kissingweirdanimals #fyp
```

Alternates:
- `the way it didn't even blink #weirdanimals #kissingweirdanimals`
- `vai Larissa vai 😭 #weirdanimals #kissingweirdanimals`
- `i swear capybaras have figured something out the rest of us haven't #weirdanimals #capybara`

### YouTube Shorts (recommended)

```
woman kisses a wild capybara — capybara does not react #Shorts

#weirdanimals #kissingweirdanimals #capybara
```

Alternates:
- `the world's chillest mammal #Shorts #weirdanimals`
- `wild capybara in a Brazilian backyard #Shorts #kissingweirdanimals`
- `vai vai vai #Shorts #weirdanimals #capybara`

### Facebook Reels (recommended)

Same as Instagram Reels above. If IG↔FB cross-post is connected, FB will pick up automatically. Otherwise paste IG caption into a manual FB Reel upload.

## Platform metadata settings

| Platform | AI-content label | Cover/thumbnail | Other |
|---|---|---|---|
| **TikTok** | **ON** — "AI-generated content" label. The scheduler sends TikTok posts as a Buffer notification by default so the final publish happens in the TikTok app, where this label can be set. | Pick a frame from 0–1s — the lone capybara on the dry grass off-diagonal, no humans. The "what's that in the corner" framing is the stop-scroll image. | Leave auto-captions OFF. |
| **Instagram Reels** | **ON** — apply the AI-generated label ("AI info"). | Same — pre-Larissa lone-capybara hook frame. | Share to Feed: yes. Auto-captions default. |
| **YouTube Shorts** | **YES** — "Altered or synthetic content" in upload details / YouTube Studio. | Auto-thumbnail fine. | Confirm `#Shorts` in description. |
| **Facebook Reels** | **ON** — apply the AI-generated label. | Auto-thumbnail fine. | If connected to IG, auto-cross-posts. |

> **AI disclosure:** this episode is entirely AI-generated (Nano Banana image + Seedance video). Label it as AI-generated on every platform that supports or requires it, and keep the `AI-generated video` line that `schedule_episode.py` appends to every caption by default.

## Posting plan

- **Date**: Sunday 2026-05-10
- **Time**: ~6 PM CT / 7 PM ET
- **Order**: post all four platforms within ~30 minutes of each other
- **First 60 min**: stay on the device; reply to every comment; like every comment

## Pinned comment candidates

The "world's chillest mammal" angle is the strongest pin — viewers will spam "did it die" / "is it sedated" / "is that real" — give them the real biology.

- **`fun fact: capybaras are the world's largest rodents and physiologically the chillest mammal on earth. they cohabit with caimans, monkeys, even crocodiles. nothing has ever bothered them. Larissa was the most excited animal in this video. 🌿`** ← strongest, lean on this
- `the capybara did not consent but the capybara also did not object`
- `the way she had to talk herself into it three times and the capybara was just eating`
- `vai vai vai is the only Portuguese you need to know now`
- `every capybara video makes me question whether i should also just be a capybara`
- `the chillest mammal alive vs the woman who is afraid of her own shadow`

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

(Fill in after posting — anything surprising, things to change for episode 10. Two big format-validation data points to watch: (1) does the new "hook on animal alone" cold-open drive better first-3-second retention than prior episodes that opened on a human? (2) does the inverted-warm "animal completely indifferent" payoff land differently than the active-warm Ep06 quokka nibble?)
