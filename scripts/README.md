# Companion scripts

Small, generic helpers for the "Making AI Videos Locally on a Mac" series. They need `ffmpeg`/`ffprobe` (Homebrew), Python 3, and `numpy` for `sync_check.py`. They contain nothing specific to any project.

| Script | What it does |
|---|---|
| `contact_sheet.sh clips_dir out.png` | First/middle/last frame of every clip in one image |
| `last_frame.sh clip.mp4 out.png` | Exact last frame, to seed the next clip |
| `find_pauses.py video.mp4 [--min 0.5]` | Lists silent gaps in the audio |
| `jump_check.py a.mp4 b.mp4 ...` | SSIM between each clip's last frame and the next clip's first frame |
| `sync_check.py clip.mp4 --box X Y W H` | Correlates mouth-region motion with audio loudness (not real lip reading) |
| `loudnorm_two_pass.sh in.wav out.wav [LUFS]` | Linear two-pass loudness normalisation |
| `assemble.py shots.json out.mp4` | Concatenates clips (hard cut or crossfade) and mixes voice + music |

All were smoke-tested on synthetic clips, so check results on your own material.
