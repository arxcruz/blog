#!/usr/bin/env python3
"""Join clips with hard cuts or short fades, and mix a voice track and music.
Usage: assemble.py shots.json out.mp4
shots.json:
{
  "clips": [{"file": "a.mp4", "fade": 0.0}, {"file": "b.mp4", "fade": 0.4}],
  "voice": "voice.wav",        (optional)
  "music": "music.wav",        (optional)
  "music_volume": 0.15
}
"fade" is the crossfade (seconds) INTO that clip; 0 means a hard cut."""
import json, subprocess, sys

def dur(p):
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", p]))

cfg = json.load(open(sys.argv[1])); out = sys.argv[2]
clips = cfg["clips"]
args = ["ffmpeg", "-v", "error", "-y"]
for c in clips:
    args += ["-i", c["file"]]
vf, af = [], []
v, acc = "[0:v]", dur(clips[0]["file"])
a_ = "[0:a]"
for i in range(1, len(clips)):
    f = float(clips[i].get("fade", 0))
    if f > 0:
        vf.append(f"{v}[{i}:v]xfade=transition=fade:duration={f}:offset={acc-f:.3f}[v{i}]")
        af.append(f"{a_}[{i}:a]acrossfade=d={f}[a{i}]")
        acc += dur(clips[i]["file"]) - f
    else:
        vf.append(f"{v}[{i}:v]concat=n=2:v=1:a=0[v{i}]")
        af.append(f"{a_}[{i}:a]concat=n=2:v=0:a=1[a{i}]")
        acc += dur(clips[i]["file"])
    v, a_ = f"[v{i}]", f"[a{i}]"
n = len(clips)
extra = []
if cfg.get("voice"):
    args += ["-i", cfg["voice"]]; extra.append((n, 1.0)); n += 1
if cfg.get("music"):
    args += ["-i", cfg["music"]]; extra.append((n, cfg.get("music_volume", 0.15))); n += 1
if extra:
    parts = "".join(f"[{i}:a]volume={vol}[x{i}];" for i, vol in extra)
    mix = a_ + "".join(f"[x{i}]" for i, _ in extra)
    af.append(parts + f"{mix}amix=inputs={1+len(extra)}:duration=first:normalize=0[aout]")
    a_ = "[aout]"
fc = ";".join(vf + af) if len(clips) > 1 or extra else ""
cmd = args + (["-filter_complex", fc, "-map", v, "-map", a_] if fc else [])
cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", out]
subprocess.run(cmd, check=True); print("wrote", out)
