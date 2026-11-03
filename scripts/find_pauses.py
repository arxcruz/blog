#!/usr/bin/env python3
"""Report silent gaps longer than a threshold in a video's audio track.
Usage: find_pauses.py video.mp4 [--min 0.5] [--noise -40]"""
import argparse, re, subprocess

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("--min", type=float, default=0.5, help="min gap in seconds")
ap.add_argument("--noise", type=float, default=-40, help="silence threshold in dB")
a = ap.parse_args()
r = subprocess.run(
    ["ffmpeg", "-i", a.video, "-af", f"silencedetect=n={a.noise}dB:d={a.min}",
     "-f", "null", "-"], capture_output=True, text=True)
starts = re.findall(r"silence_start: ([\d.]+)", r.stderr)
ends = re.findall(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", r.stderr)
if not starts:
    print("no pauses found")
for i, s in enumerate(starts):
    dur = ends[i][1] if i < len(ends) else "?"
    print(f"pause at {float(s):7.2f}s  lasting {dur}s")
