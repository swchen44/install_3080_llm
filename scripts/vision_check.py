#!/usr/bin/env python3
"""Check whether the local Strata server can read a picture.

Builds a plain red PNG in memory, posts it to /v1/chat/completions and prints the
model's answer.  Read-only: nothing on the server or on disk is changed.

    python3 scripts/vision_check.py                 # localhost:8080
    python3 scripts/vision_check.py --base http://192.168.10.99:8080
"""

from __future__ import annotations

import argparse
import base64
import json
import struct
import sys
import urllib.error
import urllib.request
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY_FILE = ROOT / "local/hermes-private/api-key"


def red_png(size: int = 96) -> bytes:
    """A solid red RGB PNG, written with nothing but the standard library."""
    row = b"\x00" + b"\xff\x00\x00" * size          # filter byte 0, then red pixels
    raw = row * size

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))

    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8080")
    ap.add_argument("--key-file", default=str(KEY_FILE))
    ap.add_argument("--model", default=None, help="default: the first id the server reports")
    ap.add_argument("--prompt", default="圖中有什麼顏色？只回答顏色。")
    a = ap.parse_args()

    key = Path(a.key_file).read_text(encoding="utf-8").strip()

    def get(url: str) -> dict:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))

    try:
        models = get(f"{a.base}/v1/models")
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"FAIL  cannot read {a.base}/v1/models: {exc}", file=sys.stderr)
        return 2

    ids = [m.get("id") for m in models.get("data", [])]
    model = a.model or (ids[0] if ids else None)
    if not model:
        print("FAIL  the server reported no model", file=sys.stderr)
        return 2
    print(f"model      {model}")

    b64 = base64.b64encode(red_png()).decode("ascii")
    body = {
        "model": model,
        "max_tokens": 64,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": a.prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
            ],
        }],
    }
    req = urllib.request.Request(
        f"{a.base}/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            reply = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:600]
        print(f"FAIL  HTTP {exc.code} on /v1/chat/completions: {detail}", file=sys.stderr)
        return 3
    except urllib.error.URLError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 3

    msg = (reply.get("choices") or [{}])[0].get("message", {})
    text = (msg.get("content") or "").strip()
    print(f"answer     {text[:400]}")
    usage = reply.get("usage") or {}
    if usage:
        print(f"usage      prompt {usage.get('prompt_tokens')} / completion {usage.get('completion_tokens')}")
    lowered = text.lower()
    ok = any(w in text for w in ("紅", "红")) or "red" in lowered
    print("RESULT     " + ("VISION_OK  (the picture was read)" if ok
                           else "VISION_UNCLEAR  (answered, but did not say red: check whether the vision section is active)"))
    return 0 if ok else 4


if __name__ == "__main__":
    sys.exit(main())
