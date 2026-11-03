---
layout: default
title: "Making AI Videos Locally on a Mac, Part 3: Assembly, Quality Control and Hard-Won Lessons"
---

# Making AI Videos Locally on a Mac, Part 3: Assembly, Quality Control and Hard-Won Lessons

*Part 3 of 3, and self-contained. Setup is in Part 1, characters and voices in Part 2. Here I assume you already have a folder of short clips and audio lines.*

Generation is maybe half the work. The other half is turning 15–18 clips into something that feels like one video, and making sure you don't ship the flaws.

## 1. Preview first, final later

The most valuable habit: **never render the expensive final until a cheap preview is approved.**

- Preview: 720p, no upscaling, fast to render.
- Final: 1080 × 1920 upscaled with Real-ESRGAN, which is slow.

Name previews with versions (`preview_v1_720p.mp4`, `preview_v2_720p.mp4`) and make it impossible for the preview script to overwrite the final file. I lost an approved version once because a preview script reused a filename. Never again.

## 2. Assembling with ffmpeg

The core is just ffmpeg and a Python script that reads a JSON list of shots. The decisions are what matter:

- **Cut vs dissolve vs generated bridge.** A hard cut is best between shots in the same sequence. A short fade (about 0.4 s) works for scene changes. For a "magic" transformation between places, I generate a short bridge clip from one image to the next with the video model.
- **Trim dead air.** Generated clips often start slow and end with a pause. I trim clips and bridges so there are no silent gaps, and I run a check that flags pauses longer than a threshold (`find_pauses.py`).
- **Normalize audio properly.** Mix voice, music and sound effects separately, then apply loudness normalization once at the end. I used the *linear* mode of ffmpeg's `loudnorm`; the dynamic mode made my audio go silent in some cases.

`loudnorm_two_pass.sh` in the companion scripts does the measure-then-apply two-pass version. A minimal single-pass example:

```bash
ffmpeg -i mix.wav -af loudnorm=I=-14:TP=-1.5:LRA=11 out.wav
```

(Measure first with `print_format=json` and feed the numbers back for true linear normalization.)

## 3. Music that doesn't fight the voice

For a kids' channel I wanted soft background music. What worked: generate several instrumental candidates, listen, and choose the quietest, simplest one. Loud or dense tracks compete with speech and make the voice sound worse. Duck the music under dialogue, and keep it low.

## 4. Subtitles

I render burned-in subtitles with an HTML-based renderer, with the option to ship both a subtitled and a clean version. Some practical points:

- Align timings to the *final* audio using a local speech-to-text model, not to the script.
- Leave extra space at the bottom: platform interfaces cover the bottom of vertical video. I raised mine by about 100 px.
- Whatever your subtitle step does to audio, check it. One of mine raised the volume by about 3 dB; I replaced its audio with the original.

## 5. Dubbing into other languages

Because the pipeline treats voice as a separate layer, dubbing is cheap: translate lines, regenerate voices, reuse the same video clips, remix, re-render. The constraint is timing: each translated line must fit its shot (speech + ~0.4 s). Translate with that in mind, and sometimes rewrite shorter instead of speeding up the audio.

## 6. QA: look at the frames, not the video

The quality-control step that paid off most was brutally manual:

- Extract frames from every clip, including the **first and last frame of every bridge**, and look at them at full size.
- Compare each frame against the reference images, and against the neighboring shots.
- Count fingers.
- Check anatomy while in motion: for a flying character I noticed legs "walking" in the air only on the playback of a full second. If a flaw appears late in a clip, keep the stable early part rather than accepting the whole clip.

I also built a script that compares the end of one shot to the start of the next (an image similarity score) to flag jumps in a chained sequence before I watch anything.

## Companion scripts

All scripts: [{{ site.github.repository_url }}/tree/main/local-ai-video-mac/scripts]({{ site.github.repository_url }}/tree/main/local-ai-video-mac/scripts).

Everything below is in the `scripts/` folder: `assemble.py` (hard cuts and crossfades from a JSON list, plus voice and music mix), `contact_sheet.sh`, `find_pauses.py`, `jump_check.py`, `loudnorm_two_pass.sh`, `sync_check.py`, `last_frame.sh`. They are small starting points, not a framework; adapt them to your own folder layout.

## 7. The mistakes list

These are the lessons, roughly in the order they cost me time:

1. **Small faces in wide shots get distorted.** Use close-ups, shots from behind, or just boots.
2. **Bridges that climb a character's body hallucinate.** A camera moving from boots up to a face made the model invent a different outfit. Use a dissolve instead, and always inspect bridges where the character faces the camera.
3. **Prompts like "thrusters on the back" produce flames at hip level.** Say exactly where: "jet flames from the soles of the boots".
4. **Video models open mouths even on "silent" shots.** Look closely at faces in non-dialogue shots too.
5. **"Slightly blurry" is a defect.** I let a few through; the viewer noticed. Don't.
6. **Reference sheets leak.** If a character sheet is the only reference, parts of the sheet itself may appear in the image. Use an approved shot as the reference instead.
7. **Name your reference files uniquely.** Two files with the same name from different folders collided in one of my batch scripts.
8. **One generation at a time.** Memory pressure causes crashes and corrupted outputs.
9. **Spend deliberately.** Hosted image generation adds up per image; I approve each paid image one at a time. Free local generation can run in batches.
10. **Detached background processes can't notify you.** Use whatever your tooling offers for background jobs, or check logs yourself.

## 8. What it costs, honestly

In my setup, on a 64 GB MacBook: local image generation took about 3.5 minutes per image (peaking around 35 GB of memory), a Wan 2.2 bridge about 5.5 minutes and an action shot about 9 minutes, roughly five times slower than a desktop GPU. LTX talking shots were the practical sweet spot on the Mac. An episode of about a minute is an overnight job, not a coffee break. If you have a second machine with a good GPU, use it for images and action shots, and keep the Mac for the rest; if you don't, the Mac-only path works, slowly.

## 9. Where I'd start if I did it again

- Write the **data model first** (characters, series, shots), because everything else reads from it.
- Build the **preview loop** before the beautiful final render.
- Automate the **checks** (sync score, pronunciation, pause detector, jump detector) early; they replace dozens of manual re-watches.
- Treat every model as replaceable. In this project, the video, image and voice models changed several times, and only the pipeline stayed.

If you build your own version, I'd love to hear what you learned that I missed.

---

*Series: [Part 1](part-1) · [Part 2](part-2) · [Part 3](part-3)*
