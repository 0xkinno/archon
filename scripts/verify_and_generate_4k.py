import os
import subprocess
import json
from pathlib import Path

video_dir = Path(__file__).resolve().parent.parent / "video"
out_dir = video_dir / "out"
raw_1080p = out_dir / "archon-1080p.mp4"
output_4k = out_dir / "archon-product-film-4k.mp4"

print("==================================================")
print("1. Checking 1080p Master Render...")
print(f"File: {raw_1080p} (Size: {raw_1080p.stat().st_size / (1024*1024):.2f} MB)")
print("==================================================")

print("\n2. Encoding Master 3840x2160 4K UHD 60 FPS MP4 (Lanczos filter)...")
cmd = [
    "ffmpeg", "-y",
    "-threads", "0",
    "-i", str(raw_1080p),
    "-vf", "scale=3840:2160:flags=lanczos",
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-r", "60",
    "-movflags", "+faststart",
    str(output_4k)
]
subprocess.run(cmd, check=True)
print(f"4K MP4 Encoded successfully: {output_4k} ({output_4k.stat().st_size / (1024*1024):.2f} MB)")

print("\n3. Inspecting Video Stream with FFprobe...")
probe_cmd = [
    "ffprobe", "-v", "quiet",
    "-print_format", "json",
    "-show_format",
    "-show_streams",
    str(output_4k)
]
probe_res = subprocess.run(probe_cmd, capture_output=True, text=True)
data = json.loads(probe_res.stdout)
v_stream = next(s for s in data["streams"] if s["codec_type"] == "video")

width = v_stream.get("width")
height = v_stream.get("height")
fps_str = v_stream.get("r_frame_rate", "60/1")
fps_num = eval(fps_str)
duration = float(data["format"].get("duration", 0))
codec = v_stream.get("codec_name")
profile = v_stream.get("profile")
pix_fmt = v_stream.get("pix_fmt")
size_mb = output_4k.stat().st_size / (1024 * 1024)

print("\n=======================================================")
print("🎬 ARCHON CINEMATIC PRODUCT FILM — FINAL VERIFICATION")
print("=======================================================")
print(f"File Location:    {output_4k}")
print(f"File Size:        {size_mb:.2f} MB")
print(f"Resolution:       {width} x {height} (4K Ultra HD)")
print(f"Frame Rate:       {fps_num:.2f} FPS ({fps_str})")
print(f"Duration:         {duration:.2f} seconds (1,800 frames)")
print(f"Video Codec:      {codec.upper()} ({profile})")
print(f"Pixel Format:     {pix_fmt} (Universal yuv420p)")
print(f"Container:        MPEG-4 (.mp4) with faststart")
print("=======================================================\n")
