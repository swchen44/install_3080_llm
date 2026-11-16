#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 INPUT_12_25S.mp4 OUTPUT_12S.mp4" >&2
  exit 2
fi
INPUT="$1"
OUTPUT="$2"
[[ -f "$INPUT" ]] || { echo "Input not found: $INPUT" >&2; exit 2; }
[[ ! -e "$OUTPUT" ]] || { echo "Refusing to overwrite: $OUTPUT" >&2; exit 2; }

ffmpeg -hide_banner -y -i "$INPUT" \
  -map 0:v:0 -map 0:a:0 \
  -vf 'trim=end_frame=288,setpts=PTS-STARTPTS' \
  -af 'atrim=end=12,asetpts=PTS-STARTPTS' \
  -frames:v 288 -t 12 -r 24 \
  -c:v libx264 -preset slow -crf 12 -pix_fmt yuv420p \
  -c:a aac -b:a 192k "$OUTPUT"

ffprobe -v error -show_entries format=duration -show_entries stream=codec_type,width,height,avg_frame_rate,nb_frames \
  -of json "$OUTPUT" | tee "${OUTPUT%.mp4}.ffprobe.json"
python3 "$(dirname "$0")/verify_12s_video.py" "$OUTPUT"
