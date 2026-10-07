# Episode 10 — publish notes

## Episode summary

- **File**: `final-episodes/10/final.mp4` — 15.07s, 1080×1920, 24fps
- **Animal**: real wild walking-leaf insect (Phyllium philippinicum, ~10cm, palm-sized; muted natural leaf-green with embossed leaf-vein patterns and brownish "fake bite marks" on the body edges to mimic a chewed banana leaf)
- **Setting**: rural Filipino backyard banana grove in the Visayas, mid-morning, soft tropical haze, woven palm-bamboo fence, concrete house corner, hanging laundry, muted natural-green palette
- **Cast**: Jasmine (~17, on-screen, Filipino teen, faded dusty-blue long-sleeve cotton tee + cream-tan cotton pants + flip-flops, natural Filipino skin tone, no makeup, real teen skin texture with mild teen-acne marks and asymmetric features) + Bryan (off-camera operator, her ~12-year-old younger brother, slightly less steady kid grip, pure Tagalog)
- **Payoff structure (type #5, transform/disguise reveal)**: HOOK is a bug LEAP from leaf A to leaf B in 0–2s (camera jerkily follows) → settles to perfect leaf-camouflage → Jasmine commits and makes physical lip-contact with the bug (thinking it's a leaf) → the moment her lips break contact the bug LEAPS AGAIN right at her face → BOTH siblings scream-startle in real shock, camera jerks hard with Bryan's body
- **Generation source**: `episodes-in-progress/10/raw/raw.mp4` (v2 Take B — second iteration, the better of two parallel rolls of the same v2 prompt). v1 archived (air-kiss instead of physical contact, Jasmine looked fake/AI, English words snuck into Tagalog dialogue). v2 Take A still available at `v2-takes/take-a.mp4` as a slightly-bigger-bug alternate.
- **Cost to produce**: ~$3.88 (one image $0.12 + two Seedance attempts $1.88 each — both rolls recovered from orphaned task IDs after network resets, then the better roll picked as final)
- **Production date**: 2026-05-10
- **Format breakthroughs**:
  - **Bug-leap hook.** First action-based animal hook (vs static-reveal hooks in earlier episodes). Camera jerkily handheld-follows the leap. Stops scrolls because something is *moving*.
  - **Pure non-English dialogue.** First episode in 100% Tagalog with NO Taglish/English-word mixing. Explicit "LANGUAGE RULE" prompt-block forbids mixed languages. Validated.
  - **Physical lip-to-animal contact (not air-kiss).** Explicit "KISS RULE — PHYSICAL CONTACT REQUIRED" prompt language fights Seedance's tendency to render kisses as floating-near-target. Lips visibly press against the bug's body.
  - **Reactive both-character startle payoff.** First payoff where BOTH on-screen and off-camera characters scream-startle in real shock. Reactive register works for the "scary surprise" payoff family (vs the deadpan register that works for "warm" / "indifferent" payoffs).
  - **Two-roll recovery from orphan task IDs.** Network resets killed both polling loops but the kie.ai tasks completed server-side. Recovered both via direct `recordInfo?taskId=` polling, saved as parallel takes — gave us A/B comparison for free.

## Caption text — copy/paste ready

The recommended caption for each platform is the first one. Alternates are safe swaps if the recommended doesn't feel right.

### TikTok (recommended)

```
told my sister to kiss this "leaf" 🍃 turns out it had LEGS

#fyp #weirdanimals #kissingweirdanimals
```

Alternates:
- `she did NOT know it was alive 😭 #fyp #weirdanimals #kissingweirdanimals`
- `the leaf just JUMPED at her face #fyp #weirdanimals #kissingweirdanimals`
- `kahit kelan hindi siya magtitiwala sa akin ulit #fyp #weirdanimals #philippines`

### Instagram Reels (recommended)

```
my sister kissed a leaf and the leaf had LEGS

#weirdanimals #kissingweirdanimals #fyp
```

Alternates:
- `ate hindi siya dahon — ate it's not a leaf 😭 #weirdanimals #kissingweirdanimals`
- `the way it just LAUNCHED at her face 🍃 #weirdanimals #kissingweirdanimals`
- `walking leaf insects exist and they will ruin your day #weirdanimals #philippines`

### YouTube Shorts (recommended)

```
girl kisses a leaf — leaf turns out to be an insect 🍃 #Shorts

#weirdanimals #kissingweirdanimals #philippines
```

Alternates:
- `walking-leaf insect in the Philippines #Shorts #weirdanimals`
- `the leaf was alive #Shorts #kissingweirdanimals`
- `pranked my sister with a real bug #Shorts #weirdanimals`

### Facebook Reels (recommended)

Same as Instagram Reels above. If IG↔FB cross-post is connected, FB will pick up automatically. Otherwise paste IG caption into a manual FB Reel upload.

## Platform metadata settings

| Platform | AI-content label | Cover/thumbnail | Other |
|---|---|---|---|
| **TikTok** | **ON** — "AI-generated content" label. The scheduler sends TikTok posts as a Buffer notification by default so the final publish happens in the TikTok app, where this label can be set. | Pick a frame from 0–1s — the bug mid-leap or the leaves before/after the first leap. The leap motion is the stop-scroll moment. | Leave auto-captions OFF. |
| **Instagram Reels** | **ON** — apply the AI-generated label ("AI info"). | Same — pre-jolt foliage frame. | Share to Feed: yes. Auto-captions default. |
| **YouTube Shorts** | **YES** — "Altered or synthetic content" in upload details / YouTube Studio. | Auto-thumbnail fine. | Confirm `#Shorts` in description. |
| **Facebook Reels** | **ON** — apply the AI-generated label. | Auto-thumbnail fine. | If connected to IG, auto-cross-posts. |

> **AI disclosure:** this episode is entirely AI-generated (Nano Banana image + Seedance video). Label it as AI-generated on every platform that supports or requires it, and keep the `AI-generated video` line that `schedule_episode.py` appends to every caption by default.

## Posting plan

- **Date**: Monday 2026-05-11
- **Time**: ~6 PM CT / 7 PM ET
- **Order**: post all four platforms within ~30 minutes of each other
- **First 60 min**: stay on the device; reply to every comment; like every comment

## Pinned comment candidates

The "fake bite marks built into its exoskeleton" fact is the strongest pin — viewers will spam "wait is that even real" — give them the real biology.

- **`fun fact: the walking-leaf insect (Phyllium philippinicum) is endemic to the Philippines. Its body has fake bite-marks and leaf-vein patterns built into its exoskeleton — it mimics a chewed-up leaf so well that OTHER INSECTS try to eat it by mistake. Ate just kissed it. 🍃`** ← strongest, lean on this
- `walking-leaf insects can be male or female and the females are flightless. they live their whole lives pretending to be foliage. and they're winning.`
- `ate hindi yan dahon — ATE`
- `the way it LAUNCHED at her face is exactly what i would have done as a leaf`
- `Bryan's scream is the same pitch as my soul leaving my body`
- `this is the most Filipino-rural-backyard energy ever`

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

(Fill in after posting — anything surprising, things to change for episode 11. Big format-validation data points: (1) does the action-leap hook drive better first-3-second retention than static cold-opens? (2) does the reactive-scared-both-characters payoff over-perform or under-perform vs the deadpan-non-reaction Ep09 capybara? (3) does the non-English dialogue help or hurt with the predominantly-US TT/IG audience — does the Tagalog feel exotic-interesting or alienating?)
