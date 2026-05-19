"""Fetch the 8 already-generated images from the previous run by task ID."""
import json
import os

import requests

ENV_PATH = "/Users/macbook/Documents/new workflows/.env"
OUT_DIR = "/Users/macbook/Documents/new workflows/APsystems/clients/CherryJane-Okeke/images/services"

TASKS = {
    "iul": "bd0ac5edee4a3d1654cec1e1b86c85fb",
    "term-life": "bc4cd7f5844a84efbc8877b7178d9ca0",
    "rop-term": "1c5f856e6f8605e148a3bcd299c0c94a",
    "whole-life": "9724ba2a3636f0e8a301982576f2d02f",
    "annuity": "fa70c3e3a24704362a2a734c4296e1a0",
    "final-expense": "1743f735bd5820692418f15bef89b868",
    "rollover": "8fba0efef0ee7cbdaec04128fa65bc6c",
    "gul": "c3cffc21cf5f056bf47d783b82e85163",
}


def load_key():
    with open(ENV_PATH) as f:
        for line in f:
            if line.startswith("KIE_AI_API_KEY="):
                return line.strip().split("=", 1)[1].strip("'\"")


def main():
    key = load_key()
    os.makedirs(OUT_DIR, exist_ok=True)
    for slug, task_id in TASKS.items():
        r = requests.get(
            "https://api.kie.ai/api/v1/jobs/recordInfo",
            headers={"Authorization": f"Bearer {key}"},
            params={"taskId": task_id},
            timeout=30,
        ).json()
        data = r.get("data") or {}
        state = data.get("state")
        if state not in ("success", "completed"):
            print(f"[{slug}] state={state} — skipping")
            continue
        urls = json.loads(data.get("resultJson", "{}")).get("resultUrls", [])
        if not urls:
            print(f"[{slug}] no result url")
            continue
        out = os.path.join(OUT_DIR, f"{slug}.jpg")
        resp = requests.get(urls[0], headers={"User-Agent": "Mozilla/5.0"}, timeout=60, stream=True)
        resp.raise_for_status()
        with open(out, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        size = os.path.getsize(out)
        print(f"[{slug}] saved {size//1024} KB -> {out}")


if __name__ == "__main__":
    main()
