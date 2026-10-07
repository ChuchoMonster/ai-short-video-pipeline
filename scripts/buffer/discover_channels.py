#!/usr/bin/env python3
"""One-time helper: query Buffer's GraphQL API to discover the connected
channel IDs (TikTok, Instagram, YouTube, Facebook) and save them to a config
file the rest of the integration scripts will read.

Usage: python3 scripts/buffer/discover_channels.py

Reads the Buffer token from $BUFFER_API_KEY (environment or project .env).
Writes scripts/buffer/channels.json with the resolved IDs (git-ignored; see
channels.example.json for the shape).
"""
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


PROJECT_ROOT = Path(os.environ.get("KWA_ROOT") or Path(__file__).resolve().parents[2])
ENV_PATH = PROJECT_ROOT / ".env"
OUT_PATH = Path(os.environ.get("BUFFER_CHANNELS_FILE")
                or PROJECT_ROOT / "scripts" / "buffer" / "channels.json")
BUFFER_API = "https://api.buffer.com"


def load_env():
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


def buffer_query(token, query):
    body = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request(
        BUFFER_API,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            # Cloudflare blocks Python's default UA — pretend to be a browser
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8')}", file=sys.stderr)
        sys.exit(1)


def main():
    env = load_env()
    token = env.get("BUFFER_API_KEY") or env.get("Buffer_API_KEY")
    if not token:
        print("FAIL: BUFFER_API_KEY not set (environment or .env)", file=sys.stderr)
        sys.exit(1)

    # Step 1: get account + organizations
    account_q = """
    query {
      account {
        email
        organizations { id name }
      }
    }
    """
    resp = buffer_query(token, account_q)
    if "errors" in resp:
        print(f"FAIL: account query: {resp['errors']}", file=sys.stderr)
        sys.exit(1)
    orgs = resp["data"]["account"]["organizations"]
    print(f"Account: {resp['data']['account']['email']}")
    print(f"Organizations: {[(o['id'], o['name']) for o in orgs]}")

    if not orgs:
        print("FAIL: no organizations on this account", file=sys.stderr)
        sys.exit(1)

    # Step 2: query channels per organization
    all_channels = []
    for org in orgs:
        ch_q = f"""
        query {{
          channels(input: {{ organizationId: "{org['id']}" }}) {{
            id
            service
            type
            name
            organizationId
          }}
        }}
        """
        resp = buffer_query(token, ch_q)
        if "errors" in resp:
            print(f"FAIL: channels query for org {org['id']}: {resp['errors']}", file=sys.stderr)
            continue
        channels = resp["data"]["channels"]
        all_channels.extend(channels)
        print(f"\nOrg '{org['name']}' ({org['id']}): {len(channels)} channels")
        for ch in channels:
            print(f"  - {ch['service']:<12} {ch['type']:<10} '{ch['name']}'  id={ch['id']}")

    # Step 3: write a clean JSON config
    by_service = {}
    for ch in all_channels:
        # Buffer's service names: "tiktok", "instagram", "youtube", "facebook"
        by_service[ch["service"]] = {
            "id": ch["id"],
            "name": ch["name"],
            "type": ch["type"],
            "organizationId": ch["organizationId"],
        }

    OUT_PATH.write_text(json.dumps(by_service, indent=2))
    print(f"\nWrote: {OUT_PATH}")
    print(f"Resolved channels: {list(by_service.keys())}")


if __name__ == "__main__":
    main()
