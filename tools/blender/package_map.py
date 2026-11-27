"""Optimise a completed Blender map and build its offline Quest board page.

Run from the project virtual environment:
  .venv/Scripts/python.exe tools/blender/package_map.py --all
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import random
import re
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
UNIFIED = ROOT / "unified"
MAPS = ROOT / "maps"


def data_uri(path: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def generate_glints(image: Image.Image, seed: int) -> list[list[float]]:
    rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
    red, green, blue = (rgb[:, :, index].astype(np.int16) for index in range(3))
    water = (green > red * 1.4) & (blue > red * 1.5) & (green > 95) & (blue > 95) & (blue > green * 0.88)
    rng = random.Random(seed)
    height, width = water.shape
    glints = []
    for y in range(8, height - 4, 8):
        for x in range(7, width - 6, 11):
            if water[y - 1:y + 2, x - 5:x + 6].all() and rng.random() < 0.18:
                glints.append([x, y, round(rng.uniform(2.0, 5.0), 2), round(rng.random() * 6.28318530718, 3)])
    return glints


def build_standalone(map_dir: Path, metadata: dict, route: dict) -> Path:
    background = map_dir / "output" / "background.webp"
    depth = map_dir / "output" / "depth.png"
    assets = {
        "background": data_uri(background, "image/webp"),
        "depth": data_uri(depth, "image/png"),
        "pawns": [data_uri(UNIFIED / "assets" / f"pawn-{index}.png", "image/png") for index in range(6)],
        "pawnDepth": data_uri(UNIFIED / "assets" / "pawn-depth.png", "image/png"),
    }
    data_script = "window.QUEST_DATA=" + json.dumps(route, separators=(",", ":")) + ";window.QUEST_ASSETS=" + json.dumps(assets, separators=(",", ":")) + ";"
    title = html.escape(f"{metadata['name']} | {metadata['subtitle']}")
    name = html.escape(metadata["name"])
    subtitle = html.escape(metadata["subtitle"])
    page = (UNIFIED / "index.html").read_text(encoding="utf-8")
    page = page.replace("<title>Kingdom Quest | Royal Road</title>", f"<title>{title}</title>")
    page = page.replace('aria-label="Kingdom Quest spectator board"', f'aria-label="{name} spectator board"')
    page = page.replace('alt="The Kingdom Quest miniature island"', f'alt="{name} miniature world"')
    page = page.replace("<span class=\"kicker\">THE ROYAL ROAD</span><h1>Kingdom Quest</h1>", f"<span class=\"kicker\">{subtitle.upper()}</span><h1>{name}</h1>")
    options = "".join(
        f'<option value="{steps + 1}"{" selected" if steps == metadata["defaultMovementSteps"] else ""}>{steps}</option>'
        for steps in metadata["supportedMovementSteps"]
    )
    page, replacements = re.subn(
        r'<label>Stops<select id="stopCount">.*?</select></label>',
        f'<label>Movement steps<select id="stopCount">{options}</select></label>',
        page,
        count=1,
    )
    if replacements != 1:
        raise ValueError("Could not set map-specific movement step choices in the board template")
    page = page.replace('<link rel="stylesheet" href="style.css">', "<style>" + (UNIFIED / "style.css").read_text(encoding="utf-8") + "</style>")
    page = page.replace('<script src="data.js"></script>', "<script>" + data_script + "</script>")
    page = page.replace('<script src="board.js"></script>', "<script>" + (UNIFIED / "board.js").read_text(encoding="utf-8") + "</script>")
    output = UNIFIED / "maps" / f"{metadata['id']}.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")
    return output


def build_gallery(items: list[dict]) -> Path:
    cards = []
    for item in items:
        map_id = html.escape(item["id"])
        name = html.escape(item["name"])
        subtitle = html.escape(item["subtitle"])
        bg = f"../maps/{map_id}/output/background.webp"
        steps = ", ".join(str(value) for value in item["supportedMovementSteps"])
        cards.append(
            f'<a class="card" href="maps/{map_id}.html"><img src="{bg}" alt="{name} environment"><div class="copy"><span>{subtitle}</span><h2>{name}</h2><p>Supported steps: {steps}</p><b>Open board <i>↗</i></b></div></a>'
        )
    document = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Quest | Choose a map</title><style>
*{box-sizing:border-box}body{margin:0;min-height:100vh;color:#f8f2dc;background:radial-gradient(ellipse at 50% 0,#1d4b57,#0b2934 70%);font:16px/1.5 system-ui,sans-serif}.wrap{width:min(1180px,94vw);margin:5vh auto}.eyebrow{color:#eac780;font-size:.75rem;font-weight:800;letter-spacing:.18em;text-transform:uppercase}h1{font:normal clamp(2.4rem,5vw,4.8rem)/1.05 Georgia,serif;margin:.4rem 0}header p{color:#c2d3cd;margin:.5rem 0 2rem}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}.card{overflow:hidden;border:1px solid #d8c59a55;border-radius:14px;background:#102f3be8;color:inherit;text-decoration:none;box-shadow:0 14px 40px #001a2260;transition:transform .18s,border-color .18s}.card:hover,.card:focus-visible{transform:translateY(-3px);border-color:#e8c77d}.card img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover}.copy{padding:16px 19px 18px}.copy>span{color:#e6bf70;font-size:.7rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase}.copy h2{font:normal 1.7rem Georgia,serif;margin:.2rem 0}.copy p{color:#c2d3cd;margin:.2rem 0 .8rem}.copy b{color:#f5ddac;font-size:.85rem}.copy i{font-style:normal;margin-left:.3rem}@media(max-width:720px){.grid{grid-template-columns:1fr}.wrap{margin:28px auto}}
</style></head><body><main class="wrap"><header><span class="eyebrow">GAME NIGHT · QUEST</span><h1>Choose your world</h1><p>Four offline adventure boards. Each keeps the same scoring and spectator controls.</p></header><section class="grid">""" + "".join(cards) + """</section></main></body></html>"""
    path = UNIFIED / "maps.html"
    path.write_text(document, encoding="utf-8")
    return path


def package_one(map_dir: Path) -> dict:
    metadata_path = map_dir / "map.json"
    route_path = map_dir / "output" / "route.json"
    background_path = map_dir / "output" / "background.png"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    route = json.loads(route_path.read_text(encoding="utf-8"))
    image = Image.open(background_path).convert("RGB")
    webp_path = map_dir / "output" / "background.webp"
    image.save(webp_path, "WEBP", quality=91, method=6)
    route["glints"] = generate_glints(image, int(route.get("seed", 0)) or sum(map(ord, metadata["id"])))
    route["name"] = metadata["name"]
    route["subtitle"] = metadata["subtitle"]
    route["defaultMovementSteps"] = metadata["defaultMovementSteps"]
    route["defaultStopCount"] = metadata["defaultStopCount"]
    route["supportedMovementSteps"] = metadata["supportedMovementSteps"]
    route_path.write_text(json.dumps(route, separators=(",", ":")) + "\n", encoding="utf-8")
    metadata["background"] = "output/background.webp"
    metadata["depth"] = "output/depth.png"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    standalone = build_standalone(map_dir, metadata, route)
    metadata["standalone"] = f"unified/maps/{metadata['id']}.html"
    metadata["standaloneBytes"] = standalone.stat().st_size
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    result = {
        "id": metadata["id"],
        "name": metadata["name"],
        "subtitle": metadata["subtitle"],
        "supportedMovementSteps": metadata["supportedMovementSteps"],
        "backgroundBytes": webp_path.stat().st_size,
        "depthBytes": (map_dir / "output" / "depth.png").stat().st_size,
        "standaloneBytes": standalone.stat().st_size,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="package every maps/* folder with map.json")
    parser.add_argument("--map-dir", type=Path, help="package one map directory")
    args = parser.parse_args()
    if args.all:
        map_dirs = sorted(path.parent for path in MAPS.glob("*/map.json"))
    elif args.map_dir:
        map_dirs = [args.map_dir.resolve()]
    else:
        parser.error("Choose --all or --map-dir")
    results = [package_one(path) for path in map_dirs]
    build_gallery(results)
    print(json.dumps({"status": "PASS", "maps": results, "gallery": "unified/maps.html"}, indent=2))


if __name__ == "__main__":
    main()
