#!/usr/bin/env python3
"""Verify a finalized lcz.me 3045 submission clip against its video specs."""
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("Usage: verify_12s_video.py FILE.mp4")
path = Path(sys.argv[1])
probe = subprocess.run(
    [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,width,height,avg_frame_rate,nb_frames",
        "-of", "json", str(path),
    ],
    check=True,
    capture_output=True,
    text=True,
)
data = json.loads(probe.stdout)
video = next((stream for stream in data.get("streams", []) if stream.get("codec_type") == "video"), None)
if video is None:
    raise SystemExit("FAIL: no video stream")
checks = {
    "width": (video.get("width"), 1344),
    "height": (video.get("height"), 768),
    "frames": (int(video["nb_frames"]) if str(video.get("nb_frames", "")).isdigit() else None, 288),
    "fps": (float(Fraction(video["avg_frame_rate"])), 24.0),
    "duration": (float(data["format"]["duration"]), 12.0),
}
failures = []
for name, (actual, expected) in checks.items():
    if name == "duration":
        passed = actual is not None and abs(actual - expected) <= 0.001
    elif name == "fps":
        passed = actual is not None and abs(actual - expected) <= 0.001
    else:
        passed = actual == expected
    print(f"{'PASS' if passed else 'FAIL'} {name}: {actual} (expected {expected})")
    if not passed:
        failures.append(name)
if failures:
    raise SystemExit("Video does not meet the 1344x768 / 12.00s / 24fps / 288-frame target")
