"""Shared helpers for the test suite: import the scripts by path and build
fictional fixtures. Nothing here touches the network or real credentials."""
import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"


def load_script(name: str, rel_path: str):
    """Import a script file as a module without executing its main()."""
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / rel_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# A fictional publish-notes.md in the same shape the scheduler expects.
PUBLISH_NOTES = """# Episode 99 — publish notes

## Caption text — copy/paste ready

### TikTok (recommended)

```
my cousin kissed a fictional newt 😭

#fyp #testanimals
```

Alternates:
- `not this one`

### Instagram Reels (recommended)

```
the newt did not consent

#testanimals
```

### YouTube Shorts (recommended)

```
cousin kisses a pretend newt #Shorts

#testanimals
```

## Pinned comment candidates

- `a plain candidate that is not bold`
- **`newts are made up for this test file`** ← strongest
- **`second bold one should be ignored`**
"""

CHANNELS = {
    "tiktok": {"id": "ch-tt", "name": "fake-tt", "type": "profile", "organizationId": "org-1"},
    "instagram": {"id": "ch-ig", "name": "fake-ig", "type": "business", "organizationId": "org-1"},
    "youtube": {"id": "ch-yt", "name": "Fake YT", "type": "channel", "organizationId": "org-1"},
}


def write_channels(path: Path):
    path.write_text(json.dumps(CHANNELS))
