"""Generate 8 photorealistic happy family images for the Achievers Wealth Academy services page.

Submits all 8 tasks to KIE.ai concurrently, polls each until complete, and downloads
the results to images/services/.
"""
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

ENV_PATH = "/Users/macbook/Documents/new workflows/.env"
OUT_DIR = "/Users/macbook/Documents/new workflows/APsystems/clients/CherryJane-Okeke/images/services"
MODEL = "nano-banana-pro"
ASPECT = "4:3"

PROMPTS = {
    "term-life": (
        "Photorealistic candid lifestyle photograph of a young Black father and his Latina wife in their early thirties "
        "playing with their two small children, a toddler boy and a baby girl, in a sunlit backyard at golden hour. "
        "Genuine laughter, natural skin tones, soft warm cinematic light, shallow depth of field, 4:3, magazine quality. "
        "No text, no logos."
    ),
    "rop-term": (
        "Photorealistic candid photograph of a happy Asian American couple in their mid thirties sitting together on a "
        "cream colored couch in a warm modern living room, sharing a quiet celebratory moment with a coffee mug in hand, "
        "looking at each other with genuine joy, sunlight streaming through tall windows. Natural skin tones, soft warm "
        "cinematic light, shallow depth of field, 4:3, magazine quality. No text, no logos."
    ),
    "whole-life": (
        "Photorealistic candid multi generation family portrait of grandparents, parents, and two grandchildren of mixed "
        "African American and Caribbean heritage, three generations together laughing on a wide cream colored sectional "
        "sofa in a warm elegant living room. Genuine joy, natural skin tones, soft warm cinematic light, shallow depth "
        "of field, 4:3, magazine quality. No text, no logos."
    ),
    "iul": (
        "Photorealistic candid lifestyle photograph of a Hispanic father and African American mother in their forties "
        "at a sunlit kitchen island with their teenage son and daughter, all looking at a tablet together, warm modern "
        "kitchen with marble counters and natural wood, hopeful confident expressions. Natural skin tones, soft warm "
        "cinematic light, shallow depth of field, 4:3, magazine quality. No text, no logos."
    ),
    "gul": (
        "Photorealistic candid lifestyle photograph of a Black couple in their early sixties sitting close together on "
        "the porch swing of a beautiful warm wooden front porch at golden hour, content and relaxed, holding hands, "
        "soft genuine smiles. Natural skin tones, soft warm cinematic light, shallow depth of field, 4:3, magazine "
        "quality. No text, no logos."
    ),
    "final-expense": (
        "Photorealistic candid intimate photograph of an adult Black woman in her forties tenderly holding the hand of "
        "her elderly mother who is seated in a sunlit warm living room. Both smiling softly, eyes meeting, a peaceful "
        "tender moment of love. Natural skin tones, soft warm cinematic light, shallow depth of field, 4:3, magazine "
        "quality. No text, no logos."
    ),
    "rollover": (
        "Photorealistic candid lifestyle photograph of a multiracial couple in their mid fifties seated at a sunlit "
        "kitchen table reviewing retirement documents together on a laptop, relieved and confident expressions, two "
        "coffee mugs nearby, warm modern home, natural wood and cream tones. Natural skin tones, soft warm cinematic "
        "light, shallow depth of field, 4:3, magazine quality. No text, no logos."
    ),
    "annuity": (
        "Photorealistic candid lifestyle photograph of a retired African American couple in their late sixties walking "
        "together hand in hand along a quiet sandy beach at golden hour, dressed in casual elegant cream and linen, "
        "genuine warm smiles, gentle waves behind them. Natural skin tones, soft warm cinematic light, shallow depth "
        "of field, 4:3, magazine quality. No text, no logos."
    ),
}


def load_api_key():
    with open(ENV_PATH) as f:
        for line in f:
            if line.startswith("KIE_AI_API_KEY="):
                return line.strip().split("=", 1)[1].strip("'\"")
    raise RuntimeError("KIE_AI_API_KEY not found in .env")


def submit_task(api_key, prompt):
    r = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": MODEL,
            "input": {
                "prompt": prompt,
                "aspect_ratio": ASPECT,
                "resolution": "1K",
                "output_format": "jpg",
            },
        },
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 200:
        raise RuntimeError(f"Submit failed: {data}")
    return data["data"]["taskId"]


def poll_task(api_key, task_id, max_attempts=90, interval=5):
    for attempt in range(max_attempts):
        time.sleep(interval)
        r = requests.get(
            "https://api.kie.ai/api/v1/jobs/recordInfo",
            headers={"Authorization": f"Bearer {api_key}"},
            params={"taskId": task_id},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json().get("data") or {}
        state = data.get("state", "")
        if state in ("success", "completed"):
            urls = json.loads(data.get("resultJson", "{}")).get("resultUrls", [])
            if not urls:
                raise RuntimeError(f"No result URLs for task {task_id}")
            return urls[0]
        if state in ("failed", "error"):
            raise RuntimeError(f"Task {task_id} failed: {data}")
    raise TimeoutError(f"Task {task_id} timed out after {max_attempts * interval}s")


def download(url, out_path):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60, stream=True)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)


def generate_one(api_key, slug, prompt):
    print(f"[{slug}] submitting", flush=True)
    task_id = submit_task(api_key, prompt)
    print(f"[{slug}] task_id={task_id}", flush=True)
    url = poll_task(api_key, task_id)
    out = os.path.join(OUT_DIR, f"{slug}.jpg")
    download(url, out)
    print(f"[{slug}] saved -> {out}", flush=True)
    return slug, out


def main():
    api_key = load_api_key()
    os.makedirs(OUT_DIR, exist_ok=True)

    results = {}
    failed = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(generate_one, api_key, slug, prompt): slug for slug, prompt in PROMPTS.items()}
        for fut in as_completed(futures):
            slug = futures[fut]
            try:
                slug_out, path = fut.result()
                results[slug_out] = path
            except Exception as exc:
                print(f"[{slug}] ERROR: {exc}", flush=True)
                failed.append((slug, str(exc)))

    print("\n=== SUMMARY ===")
    for slug, path in results.items():
        print(f"OK  {slug} -> {path}")
    for slug, err in failed:
        print(f"ERR {slug}: {err}")
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
