"""Tests for scripts/buffer/discover_channels.py with Buffer's API mocked."""
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from _support import load_script

dc = load_script("discover_channels", "buffer/discover_channels.py")

ACCOUNT = {"data": {"account": {"email": "someone@example.test",
                                "organizations": [{"id": "org-1", "name": "Org One"},
                                                  {"id": "org-2", "name": "Org Two"}]}}}


def channels_for(org_id, *services):
    return {"data": {"channels": [
        {"id": f"{org_id}-{s}", "service": s, "type": "profile", "name": f"{s} handle", "organizationId": org_id}
        for s in services]}}


class DiscoverChannelsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / "channels.json"

    def run_main(self, responses, env={"BUFFER_API_KEY": "fake"}):
        queries = []

        def fake_query(token, query):
            queries.append(query)
            return responses.pop(0)

        with mock.patch.object(dc, "OUT_PATH", self.out), \
             mock.patch.object(dc, "load_env", return_value=env), \
             mock.patch.object(dc, "buffer_query", side_effect=fake_query), \
             redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            dc.main()
        return queries

    def test_writes_one_entry_per_service_across_organisations(self):
        queries = self.run_main([ACCOUNT, channels_for("org-1", "tiktok", "instagram"),
                                 channels_for("org-2", "youtube")])
        written = json.loads(self.out.read_text())
        self.assertEqual(set(written), {"tiktok", "instagram", "youtube"})
        self.assertEqual(written["youtube"], {"id": "org-2-youtube", "name": "youtube handle",
                                              "type": "profile", "organizationId": "org-2"})
        # Each organisation id is interpolated into its own channels query.
        self.assertIn('"org-1"', queries[1])
        self.assertIn('"org-2"', queries[2])

    def test_failed_org_query_is_skipped_not_fatal(self):
        self.run_main([ACCOUNT, {"errors": ["nope"]}, channels_for("org-2", "tiktok")])
        self.assertEqual(list(json.loads(self.out.read_text())), ["tiktok"])

    def test_missing_token_exits_without_querying(self):
        with self.assertRaises(SystemExit):
            self.run_main([], env={})
        self.assertFalse(self.out.exists())


if __name__ == "__main__":
    unittest.main()
