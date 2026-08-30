import os
import subprocess
import json
import time
from pathlib import Path

video_dir = Path(__file__).resolve().parent.parent / "video"
out_dir = video_dir / "out"
input_mp4 = out_dir / "archon-1080p.mp4"
output_4k_mp4 = out_dir / "archon-product-film-4k.mp4"

def process_video():
    if not input_mp4.exists():
        print(f"Waiting for {input_mp4} to exist...")
        return False

    print(f"Upscaling/encoding {input_mp4} to 3840x2160 4K UHD 60fps...")
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(input_mp4),
        "-vf", "scale=3840:2160:flags=lanczos",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-movflags", "+faststart",
        str(output_4k_mp4)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FFmpeg error:", res.stderr)
        return False

    print(f"SUCCESS: Created final 4K MP4 at {output_4k_mp4} ({output_4k_mp4.stat().st_size} bytes)")

    # Probe video with ffprobe
    probe_cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(output_4k_mp4)
    ]
    probe_res = subprocess.run(probe_cmd, capture_output=True, text=True)
    probe_data = json.loads(probe_res.stdout)

    v_stream = next(s for s in probe_data["streams"] if s["codec_type"] == "video")
    print("\n=== FINAL VERIFICATION PROOF ===")
    print(f"File Path: {output_4k_mp4}")
    print(f"File Size: {output_4k_mp4.stat().st_size / (1024*1024):.2f} MB")
    print(f"Resolution: {v_stream.get('width')} x {v_stream.get('height')}")
    print(f"Frame Rate: {v_stream.get('r_frame_rate')} ({eval(v_stream.get('r_frame_rate')):.2f} fps)")
    print(f"Duration: {float(probe_data['format'].get('duration', 0)):.2f} seconds")
    print(f"Codec: {v_stream.get('codec_name')} ({v_stream.get('profile')})")
    print("================================")
    return True

if __name__ == "__main__":
    process_video()
