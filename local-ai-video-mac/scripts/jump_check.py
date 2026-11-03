#!/usr/bin/env python3
"""Compare the last frame of each clip with the first frame of the next one
(SSIM, 1.0 = identical). Low scores flag jumps in a chained sequence.
Usage: jump_check.py clip1.mp4 clip2.mp4 clip3.mp4 ... [--warn 0.6]"""
import argparse, re, subprocess, tempfile, os

def frame(path, out, last):
    cmd = ["ffmpeg", "-v", "error", "-y"]
    cmd += ["-sseof", "-0.5"] if last else []
    cmd += ["-i", path, "-update", "1", "-frames:v", "1", out] if last else \
           ["-i", path, "-frames:v", "1", out]
    subprocess.run(cmd, check=True)

ap = argparse.ArgumentParser()
ap.add_argument("clips", nargs="+")
ap.add_argument("--warn", type=float, default=0.6)
a = ap.parse_args()
with tempfile.TemporaryDirectory() as t:
    for i in range(len(a.clips) - 1):
        x, y = os.path.join(t, "a.png"), os.path.join(t, "b.png")
        frame(a.clips[i], x, True); frame(a.clips[i + 1], y, False)
        r = subprocess.run(["ffmpeg", "-i", x, "-i", y, "-lavfi", "ssim",
                            "-f", "null", "-"], capture_output=True, text=True)
        m = re.search(r"All:([\d.]+)", r.stderr)
        s = float(m.group(1)) if m else float("nan")
        flag = "  <-- jump" if s < a.warn else ""
        print(f"{os.path.basename(a.clips[i])} -> {os.path.basename(a.clips[i+1])}: {s:.3f}{flag}")
