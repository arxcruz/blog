---
layout: default
title: "Making AI Videos Locally on a Mac, Part 2: Consistent Characters, Voices and Lip-Sync"
---

# Making AI Videos Locally on a Mac, Part 2: Consistent Characters, Voices and Lip-Sync

*Part 2 of 3. You can read this without Part 1: all you need to know is that I make 9:16 shorts by turning still images into short video clips with models running on an Apple Silicon Mac.*

A single good clip is easy. A minute of video with the same character in 15 shots is where projects die. This part covers how I kept characters consistent, how I produce voices, and what "lip-sync" really means with today's open models.

## Characters are files, not prompts

My biggest structural decision: **a character is a folder with a data file and reference images**, not a paragraph I paste into prompts.

```
characters/hero/
  character.json     # visual description, language, voice, movement style
  refs/              # approved reference images (face, hair, full body)
```

The JSON holds things like the visual description, the language the character speaks, the voice ID, whether lip-sync is on, and how the character moves ("calm, speaks to camera, moderate gestures"). Every script that builds a prompt reads from this one source of truth. When I fix the hair description once, it is fixed in every future episode.

I also separated **series** (rules, default language, target length, regular cast) from **characters**. Any character can appear in any episode; the episode's series decides language and rules. This sounds like over-engineering until you want a crossover.

## Consistency checklist for keyframes

Most "AI video problems" are actually keyframe problems. These are the checks that caught the most issues:

1. **Fixed set.** Keep a reference image of the location (and a short text "set bible" describing it). Attach it to every keyframe that happens there.
2. **Scale between characters.** If two characters are children, they must be the same height in every frame. Say it explicitly.
3. **Hair and costume.** Describe them identically every time. For tricky hair I keep a close-up reference and attach it.
4. **A tight portrait for whoever speaks.** The video model animates *any visible face*. If a wide shot shows three small faces, all three will wiggle, and small faces distort. Rule: a shot with dialogue is a close-up of the speaker only.
5. **No readable text, logos or numbers** in images. They come out garbled and look cheap.
6. **Approve before you spend.** I generate a "folder" of anchor images (the set, plus two or three shots) first, approve those, and only then generate the rest.

When an image is wrong, resist the urge to patch it with an edit prompt. Editing works for small details (a pose, a glove). For composition or scale, **generate a new image without the rejected one as a reference**, or the mistake gets inherited.

## Long scenes: chain keyframes instead of stretching clips

If a scene happens in one place for 12–15 seconds, don't ask for one long clip. Split it into several ~4 s shots in the same sequence:

- Each shot has its own image, generated using the *previous* image as a reference.
- The clip for shot N goes from image N to image N+1 (the next image is used as an "end anchor").
- Cutting between them is a plain hard cut.

I tried generating each image independently, sharing only the set. It was clearly worse than chaining. I also chain at the clip level: grab the **actual last frame** of the generated clip and use it as the first frame of the next one, which keeps continuity much tighter than reusing the planned keyframe.

## Voices

Text-to-speech is a quality cliff. I tested three engines on the same lines in English, German and Portuguese:

- A commercial cloud TTS (ElevenLabs): best by a clear margin in all three languages.
- A local open model (Qwen3-TTS): good in English, usable elsewhere.
- Another local model (Chatterbox): fine in English, bad in German.

So my pipeline lets each character specify its engine, defaulting to a local one and optionally using the cloud service for the final take. If you want a fully local pipeline, a local model is workable; just budget more time for retakes.

Lessons that only hurt once:

- **Never let the pitch go up.** A single isolated word or letter makes TTS raise its pitch. Put it inside a short sentence ("the letter A", not "A").
- **Don't post-process pitch to fake a character.** I tried pitch-shifting a voice to sound like a helium-filled character. It sounded robotic and was rejected. A natural take with a different seed beat any effect.
- **Pick the calm profile for kids' content.** Higher stability and low "style" settings in the TTS give a steadier delivery. I generate several takes and pick by listening, and sometimes by measuring pitch variation.
- **Check pronunciation automatically.** Run the generated audio through a local speech-to-text model and compare against the script. It catches things like a planet name pronounced as a different word. Words that open a sentence confuse recognition, so test them in context.
- **Measure each line.** A line must fit inside its shot: duration of speech plus ~0.4 s of breathing room. If it doesn't, rewrite the line, not the clip.

## About lip-sync

Here is the part many tutorials gloss over: **there is no real lip-reading in this pipeline.** The approach is:

1. Generate the voice first.
2. Feed the audio to the video model together with the image (audio-conditioned image-to-video), so the model moves the mouth in time with sound.
3. **Verify numerically.** Compare the mouth's motion over time to the audio energy. My check (a generic version is in the companion scripts as `sync_check.py`) outputs a correlation score; values around 0.6–0.9 looked good, while very low values meant the mouth was moving off-beat or the face was too small.

If it fails twice, I fall back to **narration mode**: mouth closed, voice laid over in assembly. That is better than a bad lip-sync.

Things that break the score: an object near the mouth, a face that is too small in frame, and clips that end in an aggressive macro zoom on the face (trim them).

Also: even a good model's mouth lags the voice slightly. I measured about 170 ms of delay in one setup and compensate by shifting the audio when assembling. Dubbing into another language reuses the same video clips, so the mouth movements follow the original language; for cartoon characters with a stylized mouth that was acceptable, but it's worth knowing.

## Companion scripts

All scripts: [{{ site.github.repository_url }}/tree/main/local-ai-video-mac/scripts]({{ site.github.repository_url }}/tree/main/local-ai-video-mac/scripts).

For this part: `sync_check.py` (mouth motion vs. audio loudness) and `last_frame.sh` (grab the real last frame for chaining). Note that `sync_check.py` needs you to give it the mouth region as a pixel box.

## What to take away

- Characters as data files; one source of truth.
- Keyframe discipline beats prompt cleverness.
- Close-ups for speakers.
- Chain frames for long scenes.
- Measure sync and pronunciation instead of trusting your ears at 2 a.m.

In Part 3 we put everything together: transitions, upscaling, music, subtitles, quality control, and a list of mistakes I made so you don't have to.

---

*Series: [Part 1](part-1) · [Part 2](part-2) · [Part 3](part-3)*
