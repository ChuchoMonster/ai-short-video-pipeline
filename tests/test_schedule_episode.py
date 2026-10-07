"""Unit and orchestration tests for scripts/buffer/schedule_episode.py.

Every external effect is mocked: Buffer's GraphQL endpoint, the `gh` CLI,
ffmpeg, and the URL readiness probe. No network, no credentials."""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from _support import CHANNELS, PUBLISH_NOTES, REPO_ROOT, load_script, write_channels

se = load_script("schedule_episode", "buffer/schedule_episode.py")


class ParsePublishNotesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.notes = Path(self.tmp.name) / "publish-notes.md"

    def parse(self, text):
        self.notes.write_text(text)
        return se.parse_publish_notes(self.notes)

    def test_extracts_each_recommended_caption_block(self):
        out = self.parse(PUBLISH_NOTES)
        self.assertEqual(out["tiktok_text"], "my cousin kissed a fictional newt 😭\n\n#fyp #testanimals")
        self.assertEqual(out["instagram_text"], "the newt did not consent\n\n#testanimals")
        self.assertTrue(out["youtube_text"].startswith("cousin kisses a pretend newt #Shorts"))

    def test_youtube_title_is_first_line_without_shorts_tag(self):
        self.assertEqual(self.parse(PUBLISH_NOTES)["youtube_title"], "cousin kisses a pretend newt")

    def test_youtube_title_is_truncated_to_100_chars(self):
        long_line = "word " * 40  # 200 chars
        text = PUBLISH_NOTES.replace("cousin kisses a pretend newt #Shorts", long_line + "#Shorts")
        title = self.parse(text)["youtube_title"]
        self.assertEqual(len(title), 100)
        self.assertTrue(title.endswith("..."))

    def test_first_comment_is_the_first_bold_candidate(self):
        self.assertEqual(self.parse(PUBLISH_NOTES)["instagram_first_comment"],
                         "newts are made up for this test file")

    def test_first_comment_is_empty_when_section_missing(self):
        text = PUBLISH_NOTES.split("## Pinned comment candidates")[0]
        self.assertEqual(self.parse(text)["instagram_first_comment"], "")

    def test_missing_platform_block_exits_with_clear_message(self):
        text = PUBLISH_NOTES.replace("### Instagram Reels (recommended)", "### Instagram Reels")
        with self.assertRaises(SystemExit) as ctx:
            self.parse(text)
        self.assertIn("Instagram Reels (recommended)", str(ctx.exception))

    def test_every_tracked_publish_notes_file_parses(self):
        # Contract test: the scheduler must be able to read every episode
        # committed to the repo, so a formatting slip is caught before posting.
        files = sorted((REPO_ROOT / "final-episodes").glob("*/publish-notes.md"))
        self.assertGreater(len(files), 0)
        for path in files:
            with self.subTest(episode=path.parent.name):
                out = se.parse_publish_notes(path)
                for key in ("tiktok_text", "instagram_text", "youtube_text", "youtube_title"):
                    self.assertTrue(out[key], f"{key} empty")
                self.assertNotIn("#Shorts", out["youtube_title"])
                self.assertLessEqual(len(out["youtube_title"]), 100)


class AiDisclosureTests(unittest.TestCase):
    def test_appends_disclosure_on_its_own_paragraph(self):
        self.assertEqual(se.with_ai_disclosure("hello", True), f"hello\n\n{se.AI_DISCLOSURE_TEXT}")

    def test_does_not_duplicate_existing_disclosure_case_insensitively(self):
        text = "hello\n\n" + se.AI_DISCLOSURE_TEXT.upper()
        self.assertEqual(se.with_ai_disclosure(text, True), text)

    def test_disabled_leaves_caption_untouched(self):
        self.assertEqual(se.with_ai_disclosure("hello", False), "hello")


class LoadEnvTests(unittest.TestCase):
    def test_reads_dotenv_and_real_environment_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_file = Path(tmp) / ".env"
            env_file.write_text("# comment\n\nBUFFER_API_KEY=from-file\nOTHER = spaced=value\nnot a pair\n")
            with mock.patch.object(se, "ENV_PATH", env_file), \
                 mock.patch.dict(os.environ, {"BUFFER_API_KEY": "from-env"}, clear=True):
                env = se.load_env()
        self.assertEqual(env["BUFFER_API_KEY"], "from-env")
        self.assertEqual(env["OTHER"], "spaced=value")
        self.assertNotIn("not a pair", env)


class SchedulePostTests(unittest.TestCase):
    def call(self, response, **kwargs):
        with mock.patch.object(se, "buffer_mutation", return_value=response) as m, \
             redirect_stderr(io.StringIO()) as err:
            post_id = se.schedule_post("tok", "ch-1", "youtube", "caption",
                                       "https://v.example/v.mp4", "https://v.example/c.png",
                                       "2030-01-01T00:00:00Z", True, **kwargs)
        return post_id, m, err.getvalue()

    def test_builds_new_assets_array_shape(self):
        post_id, m, _ = self.call({"data": {"createPost": {"__typename": "PostActionSuccess", "post": {"id": "p1"}}}},
                                  metadata={"youtube": {"title": "t"}})
        self.assertEqual(post_id, "p1")
        token, query, variables = m.call_args.args
        inp = variables["input"]
        self.assertEqual(token, "tok")
        self.assertIn("createPost", query)
        self.assertEqual(inp["assets"], [{"video": {"url": "https://v.example/v.mp4",
                                                    "thumbnailUrl": "https://v.example/c.png"}}])
        self.assertEqual(inp["schedulingType"], "automatic")
        self.assertEqual(inp["mode"], "customScheduled")
        self.assertTrue(inp["saveToDraft"])
        self.assertEqual(inp["metadata"], {"youtube": {"title": "t"}})

    def test_union_error_type_returns_none_and_reports_typename(self):
        post_id, _, err = self.call({"data": {"createPost": {"__typename": "InvalidInputError",
                                                             "message": "bad thumbnail"}}})
        self.assertIsNone(post_id)
        self.assertIn("InvalidInputError", err)
        self.assertIn("bad thumbnail", err)

    def test_top_level_graphql_errors_return_none(self):
        post_id, _, err = self.call({"errors": [{"message": "HTTP 401"}]})
        self.assertIsNone(post_id)
        self.assertIn("HTTP 401", err)


class DedupDraftsTests(unittest.TestCase):
    def test_deletes_only_drafts_matching_channel_and_time(self):
        drafts = {"data": {"posts": {"edges": [
            {"node": {"id": "d1", "dueAt": "2030-01-01T00:00:00.000Z", "channel": {"id": "ch-tt", "service": "tiktok"}}},
            {"node": {"id": "d2", "dueAt": "2030-01-02T00:00:00.000Z", "channel": {"id": "ch-tt", "service": "tiktok"}}},
            {"node": {"id": "d3", "dueAt": "2030-01-01T00:00:00.000Z", "channel": {"id": "other", "service": "facebook"}}},
            {"node": {"id": "d4", "dueAt": "2030-01-01T00:00:00.000Z", "channel": {"id": "ch-yt", "service": "youtube"}}},
        ]}}}
        deleted_ids = []

        def fake(token, query, variables):
            if "ListDrafts" in query:
                return drafts
            deleted_ids.append(variables["id"])
            return {"data": {"deletePost": {"__typename": "DeletePostSuccess", "id": variables["id"]}}}

        with mock.patch.object(se, "buffer_mutation", side_effect=fake), redirect_stdout(io.StringIO()):
            n = se.delete_existing_drafts_for("tok", "org-1", {"ch-tt", "ch-yt"}, "2030-01-01T00:00:00.000Z")
        self.assertEqual(deleted_ids, ["d1", "d4"])
        self.assertEqual(n, 2)

    def test_list_failure_is_a_warning_not_a_crash(self):
        with mock.patch.object(se, "buffer_mutation", return_value={"errors": ["boom"]}), \
             redirect_stderr(io.StringIO()) as err:
            self.assertEqual(se.delete_existing_drafts_for("tok", "org", {"x"}, "t"), 0)
        self.assertIn("WARN", err.getvalue())


class BufferMutationTests(unittest.TestCase):
    def test_http_error_is_returned_as_graphql_style_error(self):
        http_err = urllib.error.HTTPError("https://api.buffer.com", 403, "Forbidden", {}, io.BytesIO(b"cloudflare says no"))
        self.addCleanup(http_err.close)
        with mock.patch.object(se.urllib.request, "urlopen", side_effect=http_err):
            resp = se.buffer_mutation("tok", "query{}", {})
        self.assertEqual(resp, {"errors": [{"message": "HTTP 403: cloudflare says no"}]})

    def test_sends_bearer_token_and_browser_user_agent(self):
        fake_resp = mock.MagicMock()
        fake_resp.__enter__.return_value.read.return_value = b'{"data": {}}'
        with mock.patch.object(se.urllib.request, "urlopen", return_value=fake_resp) as uo:
            self.assertEqual(se.buffer_mutation("tok", "q", {"a": 1}), {"data": {}})
        req = uo.call_args.args[0]
        self.assertEqual(req.get_header("Authorization"), "Bearer tok")
        self.assertIn("Mozilla", req.get_header("User-agent"))
        self.assertEqual(json.loads(req.data), {"query": "q", "variables": {"a": 1}})


class GhReleaseUploadTests(unittest.TestCase):
    ASSETS = {"assets": [{"name": "final.mp4", "url": "https://gh.example/final.mp4"},
                         {"name": "cover.png", "url": "https://gh.example/cover.png"}]}

    def run_upload(self, assets, urlopen_side_effect):
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            stdout = json.dumps(assets) if cmd[:3] == ["gh", "release", "view"] else ""
            return subprocess.CompletedProcess(cmd, 0, stdout=stdout)

        with mock.patch.object(se, "GH_REPO", "someone/media"), \
             mock.patch.object(se.subprocess, "run", side_effect=fake_run), \
             mock.patch.object(se.urllib.request, "urlopen", side_effect=urlopen_side_effect) as uo, \
             mock.patch.object(se.time, "sleep"):
            result = se.gh_release_upload("07", Path("v.mp4"), Path("c.png"))
        return result, calls, uo

    def not_found(self):
        err = urllib.error.HTTPError("u", 404, "nf", {}, io.BytesIO(b""))
        self.addCleanup(err.close)
        return err

    @staticmethod
    def ok(status):
        resp = mock.MagicMock()
        resp.__enter__.return_value.status = status
        return resp

    def test_recreates_release_and_returns_asset_urls(self):
        result, calls, _ = self.run_upload(self.ASSETS, lambda *a, **k: self.ok(206))
        self.assertEqual(result, {"video_url": "https://gh.example/final.mp4",
                                  "cover_url": "https://gh.example/cover.png"})
        self.assertEqual([c[:3] for c in calls], [["gh", "release", "delete"],
                                                  ["gh", "release", "create"],
                                                  ["gh", "release", "view"]])
        self.assertIn("ep07", calls[1])
        self.assertIn("someone/media", calls[1])

    def test_waits_until_urls_resolve(self):
        attempts = [self.not_found(), Exception("dns"), self.ok(200), self.ok(200)]
        _, _, uo = self.run_upload(self.ASSETS, attempts)
        self.assertEqual(uo.call_count, 4)
        self.assertEqual(uo.call_args_list[0].args[0].get_header("Range"), "bytes=0-0")

    def test_exits_when_an_asset_url_is_missing(self):
        with self.assertRaises(SystemExit):
            self.run_upload({"assets": [{"name": "final.mp4", "url": "u"}]}, lambda *a, **k: self.ok(200))

    def test_exits_when_url_never_resolves(self):
        with self.assertRaises(SystemExit) as ctx:
            self.run_upload(self.ASSETS, self.not_found())
        self.assertIn("never became accessible", str(ctx.exception))


class MainOrchestrationTests(unittest.TestCase):
    """Runs main() end to end against a fictional episode with every external
    effect replaced, and checks the three createPost payloads."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        ep = root / "final-episodes" / "07"
        ep.mkdir(parents=True)
        (ep / "final.mp4").write_bytes(b"not really a video")
        (ep / "publish-notes.md").write_text(PUBLISH_NOTES)
        self.channels = root / "channels.json"
        write_channels(self.channels)
        self.root = root

    def run_main(self, *extra):
        posts, lists, self.deleted = [], [], []
        stale = {"node": {"id": "old-draft", "dueAt": "2030-01-01T23:00:00.000Z",
                          "channel": {"id": "ch-tt", "service": "tiktok"}}}

        def fake_buffer(token, query, variables):
            if "ListDrafts" in query:
                lists.append(variables)
                return {"data": {"posts": {"edges": [stale]}}}
            if "DeletePost" in query:
                self.deleted.append(variables["id"])
                return {"data": {"deletePost": {"__typename": "DeletePostSuccess", "id": variables["id"]}}}
            posts.append(variables["input"])
            return {"data": {"createPost": {"__typename": "PostActionSuccess",
                                            "post": {"id": f"post-{len(posts)}"}}}}

        argv = ["schedule_episode.py", "7", "2030-01-01T23:00:00Z", *extra]
        with mock.patch.object(sys, "argv", argv), \
             mock.patch.object(se, "PROJECT_ROOT", self.root), \
             mock.patch.object(se, "CHANNELS_PATH", self.channels), \
             mock.patch.object(se, "GH_REPO", "someone/media"), \
             mock.patch.object(se, "load_env", return_value={"BUFFER_API_KEY": "fake-token"}), \
             mock.patch.object(se, "extract_cover_frame") as cover, \
             mock.patch.object(se, "gh_release_upload",
                               return_value={"video_url": "https://v/v.mp4", "cover_url": "https://v/c.png"}) as up, \
             mock.patch.object(se, "buffer_mutation", side_effect=fake_buffer), \
             redirect_stdout(io.StringIO()) as out:
            se.main()
        return posts, lists, cover, up, out.getvalue()

    def test_default_run_saves_three_labelled_drafts(self):
        posts, lists, cover, up, _ = self.run_main()
        by_channel = {p["channelId"]: p for p in posts}
        self.assertEqual(set(by_channel), {"ch-tt", "ch-ig", "ch-yt"})
        for p in posts:
            self.assertTrue(p["saveToDraft"])
            self.assertTrue(p["text"].endswith(se.AI_DISCLOSURE_TEXT))
            self.assertEqual(p["dueAt"], "2030-01-01T23:00:00Z")
        self.assertEqual(by_channel["ch-tt"]["schedulingType"], "notification")
        self.assertEqual(by_channel["ch-ig"]["metadata"], {"instagram": {"type": "reel", "shouldShareToFeed": True}})
        yt = by_channel["ch-yt"]["metadata"]["youtube"]
        self.assertEqual(yt["title"], "cousin kisses a pretend newt")
        self.assertEqual(yt["categoryId"], "15")
        self.assertFalse(yt["madeForKids"])
        # Episode number is zero-padded everywhere downstream.
        self.assertEqual(up.call_args.args[0], "07")
        self.assertEqual(cover.call_args.args[2], 1.0)
        # Dedup normalises "...Z" to Buffer's stored "....000Z" before matching,
        # so a re-run removes the earlier draft for the same slot.
        self.assertEqual(lists, [{"orgId": "org-1"}])
        self.assertEqual(self.deleted, ["old-draft"])

    def test_flags_switch_live_direct_and_unlabelled(self):
        posts, _, _, _, _ = self.run_main("--live", "--tiktok-direct", "--no-ai-caption-label", "--cover-ts", "2.5")
        by_channel = {p["channelId"]: p for p in posts}
        self.assertEqual(by_channel["ch-tt"]["schedulingType"], "automatic")
        for p in posts:
            self.assertFalse(p["saveToDraft"])
            self.assertNotIn(se.AI_DISCLOSURE_TEXT, p["text"])

    def test_missing_token_exits_before_any_upload(self):
        with mock.patch.object(sys, "argv", ["x", "07", "2030-01-01T23:00:00Z"]), \
             mock.patch.object(se, "GH_REPO", "someone/media"), \
             mock.patch.object(se, "load_env", return_value={}), \
             mock.patch.object(se, "gh_release_upload") as up:
            with self.assertRaises(SystemExit) as ctx:
                se.main()
        self.assertIn("BUFFER_API_KEY", str(ctx.exception))
        up.assert_not_called()

    def test_missing_channel_exits(self):
        partial = dict(CHANNELS)
        del partial["youtube"]
        self.channels.write_text(json.dumps(partial))
        with self.assertRaises(SystemExit) as ctx:
            self.run_main()
        self.assertIn("youtube", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
