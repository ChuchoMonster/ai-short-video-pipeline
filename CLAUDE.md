# Project briefing for Claude Code

This repo produces 15-second vertical AI videos ("Kissing Weird Animals") and schedules them via Buffer. See `README.md` for the pipeline, setup and env vars.

## Non-negotiables

- **Every video is AI-generated and must be labeled as such** on every platform that supports or requires it. Never remove the caption disclosure or switch TikTok to `--tiktok-direct` unless the user explicitly asks and labels another way.
- Before producing an episode, read `scripts/production-recipe.md` and `scripts/aesthetic-spec.md`. They are the source of truth for prompt wording.
- Never print or commit API keys. Keys come from the environment or a git-ignored `.env`.

## Working rules (locked)

1. Raw Seedance output is the deliverable. The only post step is `scripts/finalize.sh NN` (1080×1920 lanczos, CRF 18, AAC 96k for the Instagram 128 kbps audio cap). Do not use `post-ungrade.sh`.
2. No music bed. Use only sound that would exist in the scene.
3. The reference image is 1:1, animal in its setting, with no people. Seedance generates the people from the video prompt.
4. Five beats in 15 s: hook (0–2 s), setup (2–6 s), approach (6–10 s), payoff (10–13 s), tail (13–15 s).
5. If a render fails review, edit the prompt and re-roll. Don't fix it in post. Move the rejected version to `episodes-in-progress/NN/archive/<version>-<what-went-wrong>/`.
6. Use `scripts/regen-ref.sh` or `scripts/seedance-from-url.sh` to re-roll a single stage and save credits.

## Layout

- `episodes-in-progress/NN/prompts/` holds `scene-prompt.txt` and `seedance-prompt.txt`.
- `final-episodes/NN/` holds `final.mp4` (git-ignored except for samples) and `publish-notes.md`. The scheduler parses the `### <Platform> (recommended)` caption blocks in that file.
- `scripts/buffer/` holds the scheduler and the channel-discovery helper. `channels.json` is git-ignored.

## Scheduling

```
python3 scripts/buffer/schedule_episode.py <NN> <iso_utc> [--live]
```

The default is drafts. Re-runs are idempotent for the same time slot. For Buffer schema quirks, see the "Buffer API notes" section in `README.md`. Don't re-derive them.
