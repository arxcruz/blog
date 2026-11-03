#!/usr/bin/env bash
# Extract the exact last frame of a clip, to use as the first frame of the next one.
# Usage: last_frame.sh clip.mp4 out.png
set -euo pipefail
ffmpeg -v error -y -sseof -0.5 -i "${1:?clip}" -update 1 -q:v 1 "${2:?out png}"
echo "wrote $2"
