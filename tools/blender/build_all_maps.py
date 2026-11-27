"""Render and validate the configured map set with the shared Blender toolchain."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAP_ROOT = ROOT / "maps"


def blender_path(value: str | None) -> Path:
    if value:
        path = Path(value)
    elif os.environ.get("BLENDER"):
        path = Path(os.environ["BLENDER"])
    elif sys.platform == "win32":
        candidates = sorted(Path(r"C:\Program Files\Blender Foundation").glob("Blender*/blender.exe"))
        if not candidates:
            raise FileNotFoundError("Set BLENDER to blender.exe; no Blender install was found under Program Files.")
        path = candidates[-1]
    else:
        found = shutil.which("blender")
        if not found:
            raise FileNotFoundError("Set BLENDER or put blender on PATH.")
        path = Path(found)
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quality", choices=("draft", "review", "final"), default="final")
    parser.add_argument("--map-id", action="append", help="build one map; may be supplied more than once")
    parser.add_argument("--blender", help="Blender executable; defaults to BLENDER or an installed executable")
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--no-package", action="store_true", help="skip WebP and standalone HTML packaging")
    args = parser.parse_args()
    executable = blender_path(args.blender)
    configs = sorted(MAP_ROOT.glob("*/scene-config.json"))
    if args.map_id:
        requested = set(args.map_id)
        configs = [path for path in configs if path.parent.name in requested]
        missing = requested - {path.parent.name for path in configs}
        if missing:
            parser.error("Unknown map id(s): " + ", ".join(sorted(missing)))
    if not configs:
        parser.error("No map scene-config.json files found")

    for config in configs:
        print(f"Rendering {config.parent.name} ({args.quality})", flush=True)
        subprocess.run([
            str(executable), "--background", "-t", str(args.threads),
            "--python", str(ROOT / "tools" / "blender" / "assemble_map.py"), "--",
            "--config", str(config), "--quality", args.quality,
        ], cwd=ROOT, check=True)
        subprocess.run([
            sys.executable, str(ROOT / "tools" / "blender" / "validate_map.py"),
            "--map-dir", str(config.parent),
        ], cwd=ROOT, check=True)

    if args.quality == "final" and not args.no_package:
        subprocess.run([sys.executable, str(ROOT / "tools" / "blender" / "package_map.py"), "--all"], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
