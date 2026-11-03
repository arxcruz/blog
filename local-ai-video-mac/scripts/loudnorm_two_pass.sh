#!/usr/bin/env bash
# Two-pass (linear) loudness normalisation, default -14 LUFS for social video.
# Usage: loudnorm_two_pass.sh in.wav out.wav [LUFS]
set -euo pipefail
in="${1:?input}"; out="${2:?output}"; I="${3:--14}"
j=$(ffmpeg -hide_banner -i "$in" -af "loudnorm=I=$I:TP=-1.5:LRA=11:print_format=json" \
    -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$j" | python3 -c "import sys,json;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -i "$in" -af "loudnorm=I=$I:TP=-1.5:LRA=11:\
measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):\
measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true" "$out"
echo "wrote $out"
