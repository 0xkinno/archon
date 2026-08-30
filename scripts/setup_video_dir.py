import os
import subprocess
from pathlib import Path

archon_root = Path(__file__).resolve().parent.parent
video_dir = archon_root / "video"
video_dir.mkdir(parents=True, exist_ok=True)

# 1. Create junction for node_modules
target_nm = Path(r"C:\Users\hp\Downloads\remotion-demo\node_modules")
link_nm = video_dir / "node_modules"

if not link_nm.exists() and target_nm.exists():
    cmd = f'cmd /c mklink /J "{link_nm}" "{target_nm}"'
    subprocess.run(cmd, shell=True, check=True)
    print("Created node_modules junction in video/")
else:
    print("node_modules exists in video/")

# 2. Create package.json in video
pkg_json = """{
  "name": "archon-product-film",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "render": "remotion render src/index.tsx ArchonProductFilm out/archon-product-film-4k.mp4 --codec h264",
    "preview": "remotion render src/index.tsx ArchonProductFilm out/preview.mp4 --scale 0.5 --codec h264"
  },
  "dependencies": {
    "@remotion/cli": "4.0.242",
    "@remotion/player": "4.0.242",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "remotion": "4.0.242"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "typescript": "^5.5.0"
  }
}
"""
(video_dir / "package.json").write_text(pkg_json, encoding="utf-8")

# 3. Create tsconfig.json in video
ts_config = """{
  "compilerOptions": {
    "target": "ES2022",
    "module": "CommonJS",
    "jsx": "react-jsx",
    "strict": false,
    "noEmit": true,
    "lib": ["DOM", "DOM.Iterable", "ES2022"],
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true
  },
  "include": ["src/**/*"]
}
"""
(video_dir / "tsconfig.json").write_text(ts_config, encoding="utf-8")

print("Video directory setup complete!")
