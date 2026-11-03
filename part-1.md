---
layout: default
title: "Making AI Videos Locally on a Mac, Part 1: The Stack and Your First Clip"
---

# Making AI Videos Locally on a Mac, Part 1: The Stack and Your First Clip

*Part 1 of 3. Each part stands on its own. Part 2 covers characters, voices and lip-sync; Part 3 covers assembly, quality control and the mistakes that cost me the most time.*

I spent several weeks building a small studio that produces vertical YouTube Shorts (about one minute each) on a MacBook with Apple Silicon. A cartoon girl and her robot friend teach the alphabet, one letter per episode: each episode has a script, consistent characters, voices, music, and subtitles in three languages.

Almost everything runs on my own machine. This series is what I wish I had read on day one. It is practical, and it includes the failures.

## Why run video generation locally?

Three reasons kept me going:

- **Cost.** Video models bill per second of output. A one-minute short is dozens of generations once you count retries, and retries are the normal case. Locally, a retry costs electricity and patience.
- **Control.** You can pin seeds, swap models, script the whole pipeline, and nothing changes under you when a vendor updates an endpoint.
- **Privacy.** Reference images and scripts never leave your disk.

The honest cost is **time and memory**. A local clip takes minutes, not seconds, and the big models want a lot of RAM. If you have an M-series Mac with 32 GB or more of unified memory you can follow along; I use 64 GB, and one of my rules is *never run two generations at once* (a single LTX run peaks around 40 GB).

## The one idea that makes everything work: image first, then video

My most important rule, learned the hard way:

> **Never generate video from text alone when a character has to look the same twice. Always go image → video.**

Text-to-video drifts. The girl's hair changes, the robot loses an antenna. Instead, the pipeline is:

1. Generate or pick a **keyframe image** for each shot (this is where you control the look).
2. Feed that image to an **image-to-video** model with a short motion prompt.
3. Cut the clips together.

Think of the keyframe as the casting and the set design, and the video model as the camera operator who only has to make it move.

## The stack

| Job | Tool | Where it runs |
|---|---|---|
| Image → video (talking shots) | LTX-2.5 via an MLX port (`ltx-2-mlx`, 8-bit weights) | Mac, Apple Silicon |
| Image → video (action, transitions) | Wan 2.2 (MLX port) | Mac (slow) or a GPU box |
| Keyframe images | Qwen-Image locally, or a hosted image API | Mac / GPU box / API |
| Voices | ElevenLabs (optional) or local TTS | API / Mac |
| Assembly, audio, subtitles | `ffmpeg`, Python, a subtitle renderer | Mac |
| Upscaling | Real-ESRGAN | Mac |

I will be upfront: **it is not 100% local.** My keyframe images sometimes come from a hosted image API, and my voices come from ElevenLabs, because for me they were noticeably better than the local options I tested. Everything that moves pixels, the video generation itself, runs on the Mac. I'll point out where each part can be swapped for a fully local alternative.

## Setup

You need a recent Python, Homebrew, and `ffmpeg`.

```bash
brew install ffmpeg python@3.11 git
python3.11 -m venv .venv
source .venv/bin/activate
```

Always work inside the virtual environment. My project's first rule is literally "activate the venv before running any script", because the MLX tooling is picky about versions.

Next, install the video model runner. I use an MLX port of LTX that downloads quantized weights (8-bit keeps memory sane) from Hugging Face on first run. Follow the install instructions in that project's README rather than copying commands from a blog post; these ports move fast.

Two practical notes from my own setup:

- **Weights are large** (tens of GB across models). Check free disk space first, and keep models outside any folder that syncs to the cloud.
- **Do one smoke test before building anything.** Generate a single 4-second clip from a single image and watch it. If that works, your install is good.

## Your first clip

Pick a clean, well-lit image at the aspect ratio you want. For Shorts that is 9:16. I generate at a small size and upscale later:

- **Generation:** 576 × 1024
- **Final:** 1080 × 1920 (via upscaling, in Part 3)
- **Frame rate:** 24 fps

Generating small is a big win: it is much faster and uses less memory, and a good upscaler recovers a lot of the detail.

Write the motion prompt in English, short and concrete:

```
The girl smiles and waves at the camera. Her curls bounce softly.
Static camera. The robot beside her tilts its head.
```

Principles that improved my results:

- **Describe motion, not appearance.** The image already carries the look. Repeating it in the prompt invites the model to redraw things.
- **Say what the camera does.** "Static camera" prevents surprise zooms.
- **Say where the feet go.** For small characters I add things like "feet return to the ground", or the model happily lets them float.
- **Keep clips short.** About 4 seconds per shot is the sweet spot for stability. Longer clips drift.

Run it, and open the result. Then run it again with a **different seed**. Seeds matter more than prompt tweaks: in my episodes, the second seed fixed most failed shots. I allow myself at most two retries per shot, and then I change the image or the idea instead of burning more compute.

## What "good enough" looks like

Before you move on to Part 2, check every clip for the same short list:

1. Does the first frame match your image? (If not, something is wrong with how the image was passed in.)
2. Are hands and fingers sane? (Count them. Seriously.)
3. Is the face stable, or does it melt in the last second?
4. Does the background behave?

A tiny script that grabs the first, middle and last frame of each clip as PNGs and puts them in a contact sheet saves hours. Looking at three frames is faster than rewatching a video, and you will catch most problems. I put a generic version in the companion scripts (`contact_sheet.sh`, in the [companion scripts]({{ site.github.repository_url }}/tree/main/scripts)).

## Run long jobs in the background

Local generation is slow, so treat it like a batch job: launch it in the background with a log file, and check progress with a small status script instead of staring at the terminal.

```bash
mkdir -p logs
nohup python scripts/gen_clip.py shot01 > logs/shot01.log 2>&1 &
tail -f logs/shot01.log
```

(Replace `gen_clip.py` with whatever wrapper you write around your video model. The point is the log file.)

## Companion scripts

All scripts: [{{ site.github.repository_url }}/tree/main/scripts]({{ site.github.repository_url }}/tree/main/scripts).

The small helper scripts from this series are generic, tested on synthetic clips, and collected in a `scripts/` folder with their own README. For this part: `contact_sheet.sh` and `last_frame.sh`.

## Next

Part 2 is about the hard part nobody warns you about: making *the same characters* look and sound identical across dozens of shots, and checking whether the mouths actually match the voices.

---

*Series: [Part 1](part-1) · [Part 2](part-2) · [Part 3](part-3)*
