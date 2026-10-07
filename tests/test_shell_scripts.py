"""Black-box tests for the shell runners.

Each test builds a throwaway project root and puts fake `curl`, `ffmpeg`,
`ffprobe` and `sleep` executables first on PATH. The fakes record their
arguments and answer like the kie.ai API would, so the real scripts run end
to end with no network, no credits spent and no video rendered. `jq` and
`python3` are the real ones (both are listed as requirements)."""
import json
import os
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

from _support import SCRIPTS

FAKE_CURL = r'''#!/usr/bin/env python3
"""Fake curl for the tests. Behaviour is driven by files in $FAKE_DIR."""
import json, os, sys
fake = os.environ["FAKE_DIR"]
args = sys.argv[1:]
with open(os.path.join(fake, "curl.log"), "a") as f:
    f.write(json.dumps(args) + "\n")
if "-o" in args:                       # download of a result URL
    out = args[args.index("-o") + 1]
    url = args[-1]
    open(out, "w").write("downloaded:" + url)
    sys.exit(0)
url = next(a for a in args if a.startswith("http"))
if url.endswith("/createTask"):
    body = json.loads(sys.stdin.read())
    with open(os.path.join(fake, "submits.jsonl"), "a") as f:
        f.write(json.dumps(body) + "\n")
    kind = "img" if body["model"] == "nano-banana-2" else "vid"
    print(json.dumps({"code": 200, "data": {"taskId": "task-" + kind}}))
    sys.exit(0)
if "/recordInfo?taskId=" in url:
    task = url.split("taskId=")[1]
    states_file = os.path.join(fake, "states-" + task)
    states = open(states_file).read().split() if os.path.exists(states_file) else ["success"]
    state = states.pop(0) if len(states) > 1 else states[0]
    open(states_file, "w").write(" ".join(states))
    ext = "png" if task == "task-img" else "mp4"
    result = json.dumps({"resultUrls": ["https://files.example/" + task + "." + ext]})
    print(json.dumps({"data": {"state": state, "resultJson": result, "param": "{\"echo\":\"\\\"big\\\"\"}"}}))
    sys.exit(0)
sys.exit("unexpected curl call: %r" % args)
'''

FAKE_RECORDER = '''#!/usr/bin/env bash
echo "$(basename "$0") $*" >> "$FAKE_DIR/tools.log"
if [[ "$(basename "$0")" == ffmpeg ]]; then
  # last argument is the output file
  for last; do :; done
  echo "fake-encoded" > "$last"
fi
'''


def make_exec(path: Path, body: str):
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


class ShellScriptTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.root = base / "project"
        self.fake = base / "fake"
        bin_dir = base / "bin"
        for d in (self.root, self.fake, bin_dir):
            d.mkdir()
        make_exec(bin_dir / "curl", FAKE_CURL)
        for tool in ("ffmpeg", "ffprobe", "sleep"):
            make_exec(bin_dir / tool, FAKE_RECORDER)
        self.env = {
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "HOME": str(base),
            "FAKE_DIR": str(self.fake),
            "KWA_ROOT": str(self.root),
            "KIE_AI_API_KEY": "fake-key-for-tests",
        }

    def run_script(self, name, *args, env_overrides=None):
        env = dict(self.env, **(env_overrides or {}))
        env = {k: v for k, v in env.items() if v is not None}
        return subprocess.run(["bash", str(SCRIPTS / name), *args], env=env,
                              capture_output=True, text=True, timeout=60)

    def submits(self):
        path = self.fake / "submits.jsonl"
        return [json.loads(l) for l in path.read_text().splitlines()] if path.exists() else []

    def tool_log(self):
        path = self.fake / "tools.log"
        return path.read_text() if path.exists() else ""


class RunEpisodeTests(ShellScriptTestCase):
    def setUp(self):
        super().setUp()
        self.ep = self.root / "episodes-in-progress" / "42"
        (self.ep / "prompts").mkdir(parents=True)
        (self.ep / "prompts" / "scene-prompt.txt").write_text('A fictional newt on a "wet" log.\nNo people.')
        (self.ep / "prompts" / "seedance-prompt.txt").write_text("Fictional character says: \"hi newt\".")

    def test_rejects_wrong_argument_count(self):
        r = self.run_script("run-episode.sh")
        self.assertEqual(r.returncode, 2)
        self.assertIn("Usage", r.stderr)

    def test_requires_api_key(self):
        r = self.run_script("run-episode.sh", "42", env_overrides={"KIE_AI_API_KEY": None})
        self.assertEqual(r.returncode, 1)
        self.assertIn("KIE_AI_API_KEY not set", r.stderr)
        self.assertFalse((self.fake / "curl.log").exists())

    def test_reads_api_key_from_project_dotenv(self):
        (self.root / ".env").write_text("KIE_AI_API_KEY=from-dotenv\n")
        r = self.run_script("run-episode.sh", "42", env_overrides={"KIE_AI_API_KEY": None})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Bearer from-dotenv", (self.fake / "curl.log").read_text())

    def test_missing_prompt_file_fails_before_calling_api(self):
        (self.ep / "prompts" / "seedance-prompt.txt").unlink()
        r = self.run_script("run-episode.sh", "42")
        self.assertEqual(r.returncode, 1)
        self.assertIn("seedance-prompt.txt", r.stderr)
        self.assertEqual(self.submits(), [])

    def test_full_run_submits_image_then_video_from_image_url(self):
        r = self.run_script("run-episode.sh", "42")
        self.assertEqual(r.returncode, 0, r.stderr)
        img, vid = self.submits()
        self.assertEqual(img["model"], "nano-banana-2")
        self.assertEqual(img["input"]["image_size"], "1:1")
        self.assertEqual(img["input"]["prompt"], 'A fictional newt on a "wet" log.\nNo people.')
        self.assertEqual(vid["model"], "bytedance/seedance-2")
        self.assertEqual(vid["input"]["image_url"], "https://files.example/task-img.png")
        self.assertEqual((vid["input"]["duration"], vid["input"]["resolution"], vid["input"]["aspect_ratio"]),
                         (15, "720p", "9:16"))
        self.assertEqual((self.ep / "reference" / "ref.png").read_text(),
                         "downloaded:https://files.example/task-img.png")
        self.assertEqual((self.ep / "raw" / "raw.mp4").read_text(),
                         "downloaded:https://files.example/task-vid.mp4")
        self.assertIn("=== Done — Episode 42 ===", (self.ep / "run.log").read_text())

    def test_polls_until_success(self):
        (self.fake / "states-task-vid").write_text("waiting generating success")
        r = self.run_script("run-episode.sh", "42")
        self.assertEqual(r.returncode, 0, r.stderr)
        log = (self.ep / "run.log").read_text()
        self.assertIn("[vid] state: generating (poll 2/120)", log)
        self.assertIn("[vid] state: success (poll 3/120)", log)
        self.assertEqual(self.tool_log().count("sleep 10"), 2)

    def test_failed_image_task_stops_before_video(self):
        (self.fake / "states-task-img").write_text("fail")
        r = self.run_script("run-episode.sh", "42")
        self.assertEqual(r.returncode, 1)
        self.assertEqual([s["model"] for s in self.submits()], ["nano-banana-2"])
        self.assertFalse((self.ep / "raw" / "raw.mp4").exists())


class FinalizeTests(ShellScriptTestCase):
    def test_upscales_and_caps_audio_bitrate(self):
        raw = self.root / "episodes-in-progress" / "42" / "raw" / "raw.mp4"
        raw.parent.mkdir(parents=True)
        raw.write_text("raw")
        r = self.run_script("finalize.sh", "42")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = self.root / "final-episodes" / "42" / "final.mp4"
        self.assertTrue(out.exists())
        ffmpeg = next(l for l in self.tool_log().splitlines() if l.startswith("ffmpeg "))
        self.assertIn(f"-i {raw}", ffmpeg)
        self.assertIn("scale=1080:1920:flags=lanczos", ffmpeg)
        self.assertIn("-b:a 96k", ffmpeg)
        self.assertIn("-crf 18", ffmpeg)
        self.assertTrue(ffmpeg.endswith(str(out)))

    def test_raw_path_override(self):
        custom = Path(self.tmp.name) / "elsewhere.mp4"
        custom.write_text("raw")
        r = self.run_script("finalize.sh", "42", env_overrides={"KWA_RAW_PATH": str(custom)})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"-i {custom}", self.tool_log())

    def test_missing_source_explains_override(self):
        r = self.run_script("finalize.sh", "42")
        self.assertEqual(r.returncode, 1)
        self.assertIn("KWA_RAW_PATH", r.stderr)
        self.assertEqual(self.tool_log(), "")


class SyntaxTests(unittest.TestCase):
    def test_every_shell_script_parses(self):
        scripts = sorted(SCRIPTS.glob("*.sh"))
        self.assertGreater(len(scripts), 0)
        for script in scripts:
            with self.subTest(script=script.name):
                r = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
