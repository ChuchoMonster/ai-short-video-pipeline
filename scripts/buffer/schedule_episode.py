#!/usr/bin/env python3
"""Schedule a KWA episode to TikTok, Instagram Reels, and YouTube Shorts via
Buffer. Uses GitHub Releases as the public CDN that Buffer fetches the video
and cover image from.

Usage:
  schedule_episode.py <NN> <iso_datetime> [--live] [--tiktok-direct] [--no-ai-caption-label]

Examples:
  schedule_episode.py 03 2026-05-04T23:00:00Z          # draft mode (default)
  schedule_episode.py 03 2026-05-04T23:00:00Z --live   # actually schedule

Requires:
  - final-episodes/<NN>/final.mp4
  - final-episodes/<NN>/publish-notes.md
  - scripts/buffer/channels.json (run discover_channels.py once;
    see channels.example.json for the shape)
  - BUFFER_API_KEY in the environment or in the project .env
  - KWA_MEDIA_REPO=<owner>/<repo>: a public GitHub repo used to host the
    video + cover as release assets (gh CLI must be authenticated to it)

AI-content labeling (ON by default):
  These videos are AI-generated. When this was built, Buffer's API did not
  expose the platforms' native AI-content toggles, so the script does two
  things by default:
    1. Appends a visible disclosure line (AI_DISCLOSURE_TEXT, default
       "AI-generated video.") to every caption. Opt out with
       --no-ai-caption-label only if you label by another means.
    2. Sends the TikTok post in Buffer "notification" mode, so the final
       publish happens in the TikTok app, where the "AI-generated content"
       label can be switched on. --tiktok-direct publishes automatically
       instead (then the native TikTok label cannot be set).
  Still set the native label on YouTube ("Altered or synthetic content")
  and Instagram ("AI info") if the platform has not applied it.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

PROJECT_ROOT = Path(os.environ.get("KWA_ROOT") or Path(__file__).resolve().parents[2])
ENV_PATH = PROJECT_ROOT / ".env"
CHANNELS_PATH = Path(os.environ.get("BUFFER_CHANNELS_FILE")
                     or PROJECT_ROOT / "scripts" / "buffer" / "channels.json")
BUFFER_API = "https://api.buffer.com"
# Public GitHub repo whose Releases host the media Buffer fetches, e.g.
# "your-user/your-media-repo". Read lazily in main() so --help works without it.
GH_REPO = os.environ.get("KWA_MEDIA_REPO", "")
AI_DISCLOSURE_TEXT = os.environ.get("AI_DISCLOSURE_TEXT", "AI-generated video.")

YT_CATEGORY_ID_PETS_ANIMALS = "15"  # YouTube category: Pets & Animals

UA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Accept": "application/json",
}


# ---------------------------------------------------------------------------
# Env + config loading
# ---------------------------------------------------------------------------

def load_env():
    """Read KEY=VALUE pairs from the project .env (if present), then let real
    environment variables override them."""
    env = {}
    lines = ENV_PATH.read_text().splitlines() if ENV_PATH.exists() else []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    env.update(os.environ)
    return env


def load_channels():
    return json.loads(CHANNELS_PATH.read_text())


# ---------------------------------------------------------------------------
# publish-notes.md parser
# ---------------------------------------------------------------------------

def parse_publish_notes(path: Path) -> dict:
    """Pull recommended captions, pinned comment, and YT title out of the
    publish-notes markdown structure. Returns dict with keys:
      tiktok_text, instagram_text, youtube_text, youtube_title,
      instagram_first_comment.
    """
    text = path.read_text()
    out = {}

    # Recommended caption blocks live under "### <Platform> (recommended)"
    # then a fenced ``` block. Use a reusable extractor.
    def extract_recommended(platform_label: str) -> str:
        pat = re.compile(
            rf"###\s+{re.escape(platform_label)}\s*\(recommended\)\s*\n+```\s*\n(.*?)\n```",
            re.DOTALL,
        )
        m = pat.search(text)
        if not m:
            sys.exit(f"FAIL: could not find '### {platform_label} (recommended)' block in {path}")
        return m.group(1).strip()

    out["tiktok_text"] = extract_recommended("TikTok")
    out["instagram_text"] = extract_recommended("Instagram Reels")
    out["youtube_text"] = extract_recommended("YouTube Shorts")

    # YouTube title: first non-empty line of the YT recommended caption,
    # stripped of #Shorts (which YouTube wants in description, not title).
    yt_first_line = out["youtube_text"].split("\n", 1)[0]
    yt_title = re.sub(r"\s*#Shorts\s*", " ", yt_first_line).strip()
    if len(yt_title) > 100:
        yt_title = yt_title[:97] + "..."
    out["youtube_title"] = yt_title

    # First (= strongest) pinned comment candidate. Convention in
    # publish-notes.md: the strongest pin is bolded with **`backticks`**.
    pin_pat = re.compile(
        r"##\s+Pinned comment candidates.*?\n.*?\*\*`(.+?)`\*\*",
        re.DOTALL,
    )
    m = pin_pat.search(text)
    out["instagram_first_comment"] = m.group(1).strip() if m else ""

    return out


# ---------------------------------------------------------------------------
# Cover frame extraction
# ---------------------------------------------------------------------------

def extract_cover_frame(video: Path, out_png: Path, timestamp: float = 1.0):
    """Extract a frame at `timestamp` seconds from `video` to `out_png`."""
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", str(timestamp), "-i", str(video),
        "-frames:v", "1", "-q:v", "2",
        str(out_png),
    ]
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------------------
# GitHub Releases upload
# ---------------------------------------------------------------------------

def gh_release_upload(nn: str, video: Path, cover: Path) -> dict:
    """Create (or replace) a GitHub release for episode <nn>, upload final.mp4
    and cover.png as assets, return a dict with the public asset URLs.
    """
    tag = f"ep{nn}"

    # Delete any existing release with this tag (clean re-runs)
    subprocess.run(
        ["gh", "release", "delete", tag, "--repo", GH_REPO,
         "--yes", "--cleanup-tag"],
        capture_output=True,  # ignore failure (release may not exist)
    )

    # Create the release with both assets attached in one call
    subprocess.run(
        ["gh", "release", "create", tag,
         str(video), str(cover),
         "--repo", GH_REPO,
         "--title", f"Episode {nn}",
         "--notes", f"KWA episode {nn} — public hosting for Buffer API. Will be deleted after the post fires."],
        check=True,
    )

    # Get the public download URLs for both assets
    out = subprocess.run(
        ["gh", "release", "view", tag, "--repo", GH_REPO, "--json", "assets"],
        check=True, capture_output=True, text=True,
    )
    data = json.loads(out.stdout)
    urls = {}
    for asset in data["assets"]:
        if asset["name"].endswith(".mp4"):
            urls["video_url"] = asset["url"]
        elif asset["name"].endswith(".png"):
            urls["cover_url"] = asset["url"]
    if "video_url" not in urls or "cover_url" not in urls:
        sys.exit(f"FAIL: missing asset URLs in release {tag}: {data}")

    # GitHub release URLs are 302-redirects to Azure Blob Storage signed URLs.
    # Both the GitHub redirect AND the Azure blob need to propagate before the
    # URL is fully fetchable. Buffer's platform validation (TikTok especially)
    # 404s if it hits during this window. Verify by doing a GET that follows
    # the redirect chain all the way to Azure. urllib does this automatically.
    for label, url in [("video", urls["video_url"]), ("cover", urls["cover_url"])]:
        for attempt in range(60):  # up to ~3 min
            try:
                req = urllib.request.Request(url, method="GET",
                                             headers={"User-Agent": "Mozilla/5.0",
                                                      "Range": "bytes=0-0"})
                with urllib.request.urlopen(req, timeout=15) as r:
                    if r.status in (200, 206):  # 206 Partial Content from Range
                        break
            except urllib.error.HTTPError:
                pass
            except Exception:
                pass
            time.sleep(3)
        else:
            sys.exit(f"FAIL: {label} URL never became accessible after ~3 min: {url}")

    # Buffer fetches each URL independently per platform call — and Azure
    # signed URLs can return 404 again briefly during validation if there's a
    # cache layer between Azure regions. Add a small buffer so all 3 platforms
    # see consistent state.
    time.sleep(5)
    return urls


# ---------------------------------------------------------------------------
# Buffer GraphQL
# ---------------------------------------------------------------------------

def buffer_mutation(token: str, query: str, variables: dict) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        **UA_HEADERS,
    }
    req = urllib.request.Request(BUFFER_API, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"errors": [{"message": f"HTTP {e.code}: {e.read().decode('utf-8')}"}]}


CREATE_POST_MUTATION = """
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    __typename
    ... on PostActionSuccess { post { id } }
    ... on NotFoundError { message }
    ... on UnauthorizedError { message }
    ... on UnexpectedError { message }
    ... on RestProxyError { message link code }
    ... on LimitReachedError { message }
    ... on InvalidInputError { message }
  }
}
"""

DELETE_POST_MUTATION = """
mutation DeletePost($id: ID!) {
  deletePost(input: { id: $id }) {
    __typename
    ... on DeletePostSuccess { id }
    ... on VoidMutationError { message }
  }
}
"""

LIST_DRAFTS_QUERY = """
query ListDrafts($orgId: OrganizationId!) {
  posts(input: { organizationId: $orgId, filter: { status: [draft] } }, first: 100) {
    edges { node { id dueAt channel { id service } } }
  }
}
"""


def delete_existing_drafts_for(token, org_id, channel_ids, due_at):
    """Find any existing drafts that target the same (channel, dueAt) tuple
    we're about to create and delete them. Prevents duplicate drafts when
    the script is re-run for the same episode + time."""
    resp = buffer_mutation(token, LIST_DRAFTS_QUERY, {"orgId": org_id})
    if "errors" in resp:
        print(f"  WARN: could not list drafts to dedup: {resp['errors']}", file=sys.stderr)
        return 0
    edges = resp["data"]["posts"]["edges"]
    deleted = 0
    for edge in edges:
        n = edge["node"]
        if n["channel"]["id"] in channel_ids and n["dueAt"] == due_at:
            r = buffer_mutation(token, DELETE_POST_MUTATION, {"id": n["id"]})
            if "data" in r and r["data"]["deletePost"]["__typename"] == "DeletePostSuccess":
                deleted += 1
                print(f"  Dedup: deleted existing draft id={n['id']} ({n['channel']['service']})")
    return deleted


def with_ai_disclosure(text: str, enabled: bool) -> str:
    """Append the AI-generated disclosure line to a caption (default ON)."""
    if not enabled or AI_DISCLOSURE_TEXT.lower() in text.lower():
        return text
    return f"{text}\n\n{AI_DISCLOSURE_TEXT}"


def schedule_post(token, channel_id, service, text, video_url, cover_url,
                  due_at, save_to_draft, metadata=None,
                  scheduling_type="automatic"):
    """Submit one createPost mutation. Returns post id (or raises).
    `metadata` should already be the per-service nested dict, e.g.
    {"instagram": {...}} or {"youtube": {...}}.
    """
    input_obj = {
        "channelId": channel_id,
        "schedulingType": scheduling_type,  # enum: 'automatic' or 'notification'
        "mode": "customScheduled",
        "dueAt": due_at,
        "text": text,
        # Buffer API shape migrated 2026-05-12: `assets` is now an ordered array
        # where each item wraps a single typed asset (image | video | ...).
        # Old shape: { videos: [{ url, thumbnailUrl }] }. Old shape still
        # accepted until 2026-05-25; new shape required after that.
        "assets": [
            {
                "video": {
                    "url": video_url,
                    "thumbnailUrl": cover_url,
                }
            }
        ],
        "saveToDraft": save_to_draft,
    }
    if metadata:
        input_obj["metadata"] = metadata

    resp = buffer_mutation(token, CREATE_POST_MUTATION, {"input": input_obj})
    if "errors" in resp:
        print(f"  [{service}] FAIL: {resp['errors']}", file=sys.stderr)
        return None
    result = resp["data"]["createPost"]
    typename = result.get("__typename", "")
    if typename == "PostActionSuccess":
        return result["post"]["id"]
    # All other union members are error types with a `message` field
    msg = result.get("message", "(no message)")
    print(f"  [{service}] FAIL ({typename}): {msg}", file=sys.stderr)
    return None


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser()
    p.add_argument("nn", help="Episode number, e.g. 03")
    p.add_argument("due_at", help="ISO 8601 UTC datetime, e.g. 2026-05-04T23:00:00Z")
    p.add_argument("--live", action="store_true", help="Schedule live (default: save to draft)")
    p.add_argument("--cover-ts", type=float, default=1.0, help="Seconds into the video for cover frame (default 1.0)")
    p.add_argument("--no-ai-caption-label", action="store_true",
                   help="Do NOT append the AI-generated disclosure line to captions (default: append it)")
    p.add_argument("--tiktok-direct", action="store_true",
                   help="Publish TikTok automatically instead of via the TikTok app "
                        "(default: notification mode, so the native AI-generated label can be set)")
    args = p.parse_args()
    ai_caption_label = not args.no_ai_caption_label
    tiktok_scheduling = "automatic" if args.tiktok_direct else "notification"

    global GH_REPO
    GH_REPO = GH_REPO or os.environ.get("KWA_MEDIA_REPO", "")
    if not GH_REPO:
        sys.exit("FAIL: set KWA_MEDIA_REPO=<owner>/<repo> (public repo used to host release assets)")

    nn = args.nn.zfill(2)
    save_to_draft = not args.live

    env = load_env()
    token = env.get("BUFFER_API_KEY") or env.get("Buffer_API_KEY")
    if not token:
        sys.exit("FAIL: BUFFER_API_KEY not set (environment or .env)")

    channels = load_channels()
    for needed in ("tiktok", "instagram", "youtube"):
        if needed not in channels:
            sys.exit(f"FAIL: channel '{needed}' missing from {CHANNELS_PATH}")

    ep_dir = PROJECT_ROOT / "final-episodes" / nn
    video = ep_dir / "final.mp4"
    notes = ep_dir / "publish-notes.md"
    if not video.exists():
        sys.exit(f"FAIL: {video} not found")
    if not notes.exists():
        sys.exit(f"FAIL: {notes} not found")

    print(f"=== Scheduling Episode {nn} ===")
    print(f"Mode: {'LIVE SCHEDULE' if args.live else 'DRAFT (review in Buffer UI)'}")
    print(f"Due at: {args.due_at}")
    print()

    print(f"[1/4] Parsing {notes.name}...")
    parsed = parse_publish_notes(notes)
    for key in ("tiktok_text", "instagram_text", "youtube_text"):
        parsed[key] = with_ai_disclosure(parsed[key], ai_caption_label)
    print(f"  AI caption label  : {'ON' if ai_caption_label else 'OFF (--no-ai-caption-label)'}")
    print(f"  TikTok publishing : {tiktok_scheduling}")
    print(f"  TikTok caption    : {parsed['tiktok_text'][:60]}...")
    print(f"  Instagram caption : {parsed['instagram_text'][:60]}...")
    print(f"  YouTube title     : {parsed['youtube_title']}")
    print(f"  IG first comment  : {parsed['instagram_first_comment'][:60]}...")
    print()

    print(f"[2/4] Extracting cover frame at t={args.cover_ts}s...")
    cover = Path(f"/tmp/kwa-ep{nn}-cover.png")
    extract_cover_frame(video, cover, args.cover_ts)
    print(f"  Wrote {cover}")
    print()

    print(f"[3/4] Uploading to GitHub release ep{nn}...")
    urls = gh_release_upload(nn, video, cover)
    print(f"  Video URL: {urls['video_url']}")
    print(f"  Cover URL: {urls['cover_url']}")
    print()

    # Dedup: delete any existing drafts for the same (channel, dueAt) — protects
    # against duplicates if the script is re-run for the same episode + time.
    # Normalize the dueAt to Buffer's canonical format (with .000Z) so the
    # comparison matches what Buffer stores.
    due_at_normalized = args.due_at if "." in args.due_at else args.due_at.replace("Z", ".000Z")
    channel_id_set = {channels[s]["id"] for s in ("tiktok", "instagram", "youtube")}
    org_id = channels["tiktok"]["organizationId"]
    deleted = delete_existing_drafts_for(token, org_id, channel_id_set, due_at_normalized)
    if deleted:
        print(f"  Removed {deleted} pre-existing draft(s) at this time slot.")
    print()

    print(f"[4/4] Submitting Buffer createPost x3...")
    results = {}

    # TikTok — no metadata needed for video posts (TikTokPostMetadataInput.title is for photo posts only)
    results["tiktok"] = schedule_post(
        token, channels["tiktok"]["id"], "tiktok",
        parsed["tiktok_text"], urls["video_url"], urls["cover_url"],
        args.due_at, save_to_draft, scheduling_type=tiktok_scheduling,
    )
    print(f"  [tiktok] {'OK' if results['tiktok'] else 'FAILED'} — id={results['tiktok']}")

    # Instagram Reels — metadata nested under "instagram"
    # NOTE: firstComment requires a paid Buffer plan. Skipped on free tier.
    # The pinned-comment text stays in publish-notes.md for manual posting
    # during the first-hour engagement window.
    ig_inner = {"type": "reel", "shouldShareToFeed": True}
    results["instagram"] = schedule_post(
        token, channels["instagram"]["id"], "instagram",
        parsed["instagram_text"], urls["video_url"], urls["cover_url"],
        args.due_at, save_to_draft, metadata={"instagram": ig_inner},
    )
    print(f"  [instagram] {'OK' if results['instagram'] else 'FAILED'} — id={results['instagram']}")

    # YouTube Shorts — metadata nested under "youtube"
    yt_inner = {
        "title": parsed["youtube_title"],
        "categoryId": YT_CATEGORY_ID_PETS_ANIMALS,
        "privacy": "public",
        "madeForKids": False,
        "notifySubscribers": True,
        "embeddable": True,
    }
    results["youtube"] = schedule_post(
        token, channels["youtube"]["id"], "youtube",
        parsed["youtube_text"], urls["video_url"], urls["cover_url"],
        args.due_at, save_to_draft, metadata={"youtube": yt_inner},
    )
    print(f"  [youtube] {'OK' if results['youtube'] else 'FAILED'} — id={results['youtube']}")

    print()
    print("=== Done ===")
    if save_to_draft:
        print("Posts are in DRAFT. Review in Buffer's UI:")
        print("  https://publish.buffer.com/drafts")
    else:
        print("Posts SCHEDULED for", args.due_at)
        print("  https://publish.buffer.com/queue")
    print("AI labeling checklist (these videos are AI-generated):")
    if tiktok_scheduling == "notification":
        print("  - TikTok: finish the post from the Buffer notification in the TikTok app")
        print("    and switch ON 'AI-generated content' before publishing.")
    else:
        print("  - TikTok: published directly; the native AI label could not be set.")
    print("  - YouTube: confirm 'Altered or synthetic content' = Yes in YouTube Studio.")
    print("  - Instagram: confirm the AI label is applied (Edit -> AI info) if Meta did not add it.")

    if any(v is None for v in results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
