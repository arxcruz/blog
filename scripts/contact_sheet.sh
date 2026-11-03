#!/usr/bin/env bash
# Build a contact sheet (first / middle / last frame of every clip) so you can
# review a whole batch at a glance.
# Usage: contact_sheet.sh clips_dir out.png
set -euo pipefail
dir="${1:?clips dir}"; out="${2:?output png}"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
n=0
for f in "$dir"/*.mp4; do
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  for t in 0 "$(echo "$d/2" | bc -l)" "$(echo "$d-0.05" | bc -l)"; do
    ffmpeg -v error -y -ss "$t" -i "$f" -frames:v 1 -vf scale=240:-2 \
      "$tmp/$(printf %04d $n).png"; n=$((n+1))
  done
done
ffmpeg -v error -y -framerate 1 -i "$tmp/%04d.png" \
  -vf "tile=3x$(( n/3 ))" -frames:v 1 "$out"
echo "wrote $out ($((n/3)) clips)"
