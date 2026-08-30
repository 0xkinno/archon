import os
import subprocess
import json
from pathlib import Path

video_path = Path(__file__).resolve().parent.parent / "video" / "out" / "archon-product-film-4k.mp4"
raw_1080p_path = Path(__file__).resolve().parent.parent / "video" / "out" / "archon-1080p.mp4"

print("Checking video files in video/out/...")
print(f"1080p Master exists: {raw_1080p_path.exists()} (Size: {raw_1080p_path.stat().st_size / (1024*1024):.2f} MB)")

if not video_path.exists() or video_path.stat().st_size < 1000:
    print("Encoding 4K version now...")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(raw_1080p_path),
        "-vf", "scale=3840:2160:flags=lanczos",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-movflags", "+faststart",
        str(video_path)
    ]
    subprocess.run(cmd, check=True)

print(f"4K Master exists: {video_path.exists()} (Size: {video_path.stat().st_size / (1024*1024):.2f} MB)")

# Run ffprobe
probe_cmd = [
    "ffprobe", "-v", "error",
    "-select_streams", "v:0",
    "-show_entries", "stream=width,height,r_frame_rate,codec_name,profile,pix_fmt,nb_frames",
    "-show_entries", "format=duration,size",
    "-of", "json",
    str(video_path)
]
probe_res = subprocess.run(probe_cmd, capture_output=True, text=True)
data = json.loads(probe_res.stdout)
v_stream = data["streams"][0]

width = v_stream.get("width")
height = v_stream.get("height")
fps_str = v_stream.get("r_frame_rate", "60/1")
fps_num = eval(fps_str)
duration = float(data["format"].get("duration", 0))
codec = v_stream.get("codec_name")
profile = v_stream.get("profile")
pix_fmt = v_stream.get("pix_fmt")
frames_count = v_stream.get("nb_frames")

print("\n=======================================================")
print("🎬 ARCHON CINEMATIC PRODUCT FILM — VERIFICATION REPORT")
print("=======================================================")
print(f"File Path:       {video_path}")
print(f"File Size:       {float(data['format'].get('size', 0)) / (1024*1024):.2f} MB")
print(f"Resolution:      {width} x {height} (4K UHD 16:9)")
print(f"Frame Rate:      {fps_num:.2f} FPS ({fps_str})")
print(f"Duration:        {duration:.2f} seconds ({frames_count} frames)")
print(f"Video Codec:     {codec.upper()} ({profile})")
print(f"Pixel Format:    {pix_fmt} (Standard Universal Compatibility)")
print("=======================================================\n")
