import os
import glob
import re
from pathlib import Path

video_dir = Path(__file__).resolve().parent.parent / "video"
public_dir = video_dir / "public"
public_files = set(os.listdir(public_dir))
print("Available in video/public:", public_files)

all_ok = True
for f in (video_dir / "src").glob("**/*.tsx"):
    text = f.read_text(encoding="utf-8")
    for match in re.findall(r'staticFile\([\'"]([^\'"]+)[\'"]\)', text):
        if match not in public_files:
            print(f"MISSING in {f.name}: {match}")
            all_ok = False
        else:
            print(f"FOUND in {f.name}: {match}")

if all_ok:
    print("ALL STATIC ASSETS ARE PRESENT IN video/public/!")
