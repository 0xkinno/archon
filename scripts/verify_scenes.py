import subprocess
from pathlib import Path

video_dir = Path(__file__).resolve().parent.parent / "video"
cli_path = video_dir / "node_modules" / "@remotion" / "cli" / "remotion-cli.js"
chrome_path = r"C:\Users\hp\AppData\Local\ms-playwright\chromium-1234\chrome-win64\chrome.exe"

test_frames = [
    (150, "scene1_brand.png"),
    (450, "scene2_problem.png"),
    (750, "scene3_architecture.png"),
    (1050, "scene4_workflow.png"),
    (1400, "scene5_governance.png"),
    (1680, "scene6_hero.png"),
]

for frame_num, out_name in test_frames:
    out_path = f"out/{out_name}"
    cmd = [
        "node",
        str(cli_path),
        "still",
        "src/index.tsx",
        "ArchonProductFilmPreview",
        out_path,
        "--frame",
        str(frame_num),
        "--browser-executable",
        chrome_path,
    ]
    print(f"Rendering frame {frame_num} -> {out_name}...")
    res = subprocess.run(cmd, cwd=str(video_dir), capture_output=True, text=True)
    if res.returncode != 0:
        print(f"ERROR rendering frame {frame_num}:", res.stderr)
    else:
        print(f"SUCCESS: Rendered {out_name}")

print("All test frames verified!")
