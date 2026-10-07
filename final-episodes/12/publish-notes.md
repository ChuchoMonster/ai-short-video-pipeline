# Episode 12 — publish notes

## Episode summary

- **File**: `final-episodes/12/final.mp4` — 15.07s, 1080×1920, 24fps
- **Animal**: real wild marine iguana (Amblyrhynchus cristatus, ~3 ft long, the size of a small dog stretched out flat; mottled muted dark-grey-brown coat, low spiny dorsal crest, flat boxy head with rounded snout, half-closed lazy basking eyes, **dried white salt-crusts visible around its nostrils** — key biological detail for the payoff)
- **Setting**: dry dirt-and-concrete back-courtyard at a small Ecuadorian coastal-town home, mid-morning, palm tree + chipped pale-yellow concrete house + plastic chair + garden hose; muted dirt-tan/concrete palette, NO boats anywhere
- **Cast**: Don José (~50, on-screen, Ecuadorian coastal-town man, weathered tan face + salt-and-pepper hair + grey stubble + faded cream long-sleeve work shirt + brown cotton pants + casual leather shoes) + Valentina (off-camera operator, his ~17-year-old daughter, walking BESIDE him with the phone, Ecuadorian Spanish)
- **Payoff structure (type #6, kiss-causes-effect)**: open MID-SNEEZE with iguana already spraying salt-mist while both characters laugh at it from across the courtyard → back-and-forth chatter at distance with intermittent iguana sneezes (sneezes #1 and #2 at 0–1s and 4–5s) → ONE CUT to Don José closer + hesitation → physical lip-peck on iguana's flat head → IMMEDIATE pull-back-and-tilt-away → iguana SNEEZES one more time (#3, the payoff), partial salt-mist hits his chin + Valentina jolts back hard so the phone wobbles → BOTH burst into BIG real-startle yelps + loud surprised laughter
- **Generation source**: `episodes-in-progress/12/raw/raw.mp4` (v4 — fourth iteration, image regenerated on v2 to remove boats). v1 archived (boats-biased: Seedance rendered Don José rowing in a boat). v2 archived (too close, no laughter buildup). v3 archived (static camera, stiff arms, soft reaction). v4 = walking camera + operator-beside-subject framing + natural body language + dual-volume rule + partial-spray-dodge mechanic.
- **Cost to produce**: ~$7.76 (one image $0.12 + four Seedance attempts $1.88 each — v3 and v4 each had one orphan task recovered after network resets)
- **Production date**: 2026-05-11
- **Format breakthroughs**:
  - **Operator-beside-subject framing.** First episode where the off-camera operator and on-screen subject stand TOGETHER at distance from the animal, with the subject partially-in-frame from the edge. Reads as authentic UGC ("two people standing together filming an animal in their yard") vs the more-staged "operator far behind animal" framing of earlier episodes.
  - **Walking camera.** Camera operator physically walks during the wide phase — phone bobs with her gait, footfalls audible as soft scuffing on dirt. Not setup-on-a-tripod.
  - **Dual-volume rule (validated).** Quiet private murmured buildup → BIG real-startle reactions at payoff. Resolves the apparent conflict with the Acting Realism rule by phase-gating: low-private during buildup, big-real during reactive payoff. Both are realistic — real people DO get loud when an animal sprays them by surprise.
  - **Natural body language rule.** Explicit prompt block forbidding the on-screen subject from standing stiffly with arms at sides. Subject must gesture, shift weight, point, fidget with constant micro-movement.
  - **Partial-spray-and-dodge mechanic.** Subject commits the kiss, then immediately starts pulling back AND tilting away in anticipation. Animal's spray happens during the pull-back, MOSTLY dodged but clips chin/side of face. More realistic than either "subject takes the full hit" or "subject perfectly dodges."
  - All five rules captured durably in `feedback_kwa_camera_framing_dual_volume.md`.

## Caption text — copy/paste ready

The recommended caption for each platform is the first one. Alternates are safe swaps if the recommended doesn't feel right.

### TikTok (recommended)

```
my dad kissed an iguana and it SNEEZED on him 😭

#fyp #weirdanimals #kissingweirdanimals
```

Alternates:
- `the iguana fired its salt cannon at exactly the wrong moment 🤧 #fyp #weirdanimals #kissingweirdanimals`
- `papi me dio toda la sal 😭 #fyp #weirdanimals #ecuador`
- `ecuadorian dads will do anything on a dare #fyp #weirdanimals`

### Instagram Reels (recommended)

```
my dad got salt-sneezed in the face by an iguana

#weirdanimals #kissingweirdanimals #fyp
```

Alternates:
- `the iguana waited UNTIL the kiss was done to fire 😭 #weirdanimals #kissingweirdanimals`
- `papi 😭 papi 😭 #weirdanimals #kissingweirdanimals #ecuador`
- `marine iguanas: do NOT play with them #weirdanimals #kissingweirdanimals`

### YouTube Shorts (recommended)

```
man kisses a marine iguana — iguana sneezes salt at him 🦎 #Shorts

#weirdanimals #kissingweirdanimals #ecuador
```

Alternates:
- `marine iguana salt-sneeze for $0 #Shorts #weirdanimals`
- `wild marine iguana in an ecuadorian backyard #Shorts #kissingweirdanimals`
- `papi got the salt #Shorts #weirdanimals`

### Facebook Reels (recommended)

Same as Instagram Reels above.

## Platform metadata settings

| Platform | AI-content label | Cover/thumbnail | Other |
|---|---|---|---|
| **TikTok** | **ON** — "AI-generated content" label. The scheduler sends TikTok posts as a Buffer notification by default so the final publish happens in the TikTok app, where this label can be set. | Pick a frame from 0–1s — iguana mid-sneeze with the salt mist puffing up. The visible salt-spray is the stop-scroll. | Leave auto-captions OFF. |
| **Instagram Reels** | **ON** — apply the AI-generated label ("AI info"). | Same — pre-kiss mid-sneeze frame. | Share to Feed: yes. Auto-captions default. |
| **YouTube Shorts** | **YES** — "Altered or synthetic content" in upload details / YouTube Studio. | Auto-thumbnail fine. | Confirm `#Shorts` in description. |
| **Facebook Reels** | **ON** — apply the AI-generated label. | Auto-thumbnail fine. | If connected to IG, auto-cross-posts. |

> **AI disclosure:** this episode is entirely AI-generated (Nano Banana image + Seedance video). Label it as AI-generated on every platform that supports or requires it, and keep the `AI-generated video` line that `schedule_episode.py` appends to every caption by default.

## Posting plan

- **Date**: Wednesday 2026-05-13
- **Time**: ~6 PM CT / 7 PM ET
- **Order**: post all four platforms within ~30 minutes of each other
- **First 60 min**: stay on the device; reply to every comment; like every comment

## Pinned comment candidates

The "marine iguanas sneeze salt" fact is gold — viewers will spam "wait that's real" — give them the biology.

- **`fun fact: marine iguanas drink seawater while diving for algae and have to sneeze the excess salt out their nostrils — that's why they have white crusts around their nose. They sneeze constantly. Papi just got hit with a fresh batch. 🦎`** ← strongest, lean on this
- `marine iguanas are the only seagoing lizard on Earth. they live on the Galápagos and parts of coastal Ecuador. and yes they sneeze salt at you.`
- `the way the iguana waited until AFTER the kiss to fire its cannon`
- `Don José is a hero. Valentina is a snitch with a phone.`
- `papi me dio toda la sal — quote of the year`
- `Charles Darwin described marine iguanas as "hideous-looking" and "disgusting" in 1835. they sneezed at him too probably.`

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

(Fill in after posting — anything surprising, things to change for episode 13. Three format-validation points: (1) does the operator-beside-subject framing read more authentic to viewers than the operator-far-behind framing of prior episodes? (2) does the dual-volume rule (quiet buildup → BIG real-startle payoff) drive higher save/share rates than the deadpan-throughout register of Ep08/Ep09? (3) does the kiss-causes-effect payoff type perform differently than the warm / dodge / anatomy-reveal payoff types we've already shipped?)
