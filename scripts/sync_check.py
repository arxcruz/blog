#!/usr/bin/env python3
"""Rough lip-sync check: correlate mouth-region motion with audio loudness.
There is no real lip reading here; this only tells you whether the mouth moves
when the audio is loud and stays still when it is quiet.

Usage: sync_check.py clip.mp4 --box X Y W H     (box = mouth region, in pixels)
Roughly: > 0.6 looks fine, < 0.3 is suspect (off-beat mouth, tiny face, or an
object near the mouth). Needs numpy and ffmpeg."""
import argparse, subprocess
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("clip")
ap.add_argument("--box", nargs=4, type=int, required=True, metavar=("X", "Y", "W", "H"))
ap.add_argument("--fps", type=int, default=24)
a = ap.parse_args()
x, y, w, h = a.box

raw = subprocess.run(
    ["ffmpeg", "-v", "error", "-i", a.clip, "-vf",
     f"fps={a.fps},crop={w}:{h}:{x}:{y},format=gray", "-f", "rawvideo", "-"],
    capture_output=True, check=True).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
motion = np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2))

sr = 16000
pcm = subprocess.run(
    ["ffmpeg", "-v", "error", "-i", a.clip, "-ac", "1", "-ar", str(sr),
     "-f", "s16le", "-"], capture_output=True, check=True).stdout
audio = np.frombuffer(pcm, np.int16).astype(np.float32)
step = sr // a.fps
env = np.array([np.sqrt((audio[i*step:(i+1)*step] ** 2).mean() + 1e-9)
                for i in range(len(motion) + 1)])[1:len(motion) + 1]
n = min(len(motion), len(env))
c = np.corrcoef(motion[:n], env[:n])[0, 1]
print(f"correlation: {c:.3f}  ({n} frames)")
