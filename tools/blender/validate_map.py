"""Validate exported map images/routes and create route review overlays.

Run with the project virtual environment:
  .venv/Scripts/python.exe tools/blender/validate_map.py --map-dir maps/kingdom-quest
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import LineString


DEPTH_SCALE = 32.0


def interpolate_route(records, distance):
    lo, hi = 0, len(records) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if records[mid][0] < distance:
            lo = mid + 1
        else:
            hi = mid
    b = records[lo]
    a = records[max(0, lo - 1)]
    span = b[0] - a[0]
    t = 0.0 if span <= 1e-9 else (distance - a[0]) / span
    return [a[i] + (b[i] - a[i]) * t for i in range(len(a))]


def min_pair_spacing(stops):
    return min(
        math.hypot(a[4] - b[4], a[5] - b[5])
        for index, a in enumerate(stops)
        for b in stops[index + 1:]
    ) if len(stops) > 1 else 0.0


def depth_samples(records, depth_rgb, flipped=False):
    height, width, _ = depth_rgb.shape
    errors, actual_depths, missing, samples = [], [], 0, []
    stride = max(1, len(records) // 240)
    for index in range(0, len(records), stride):
        row = records[index]
        x = min(width - 1, max(0, int(round(row[4]))))
        y = min(height - 1, max(0, int(round(row[5]))))
        if flipped:
            y = height - 1 - y
        code = int(depth_rgb[y, x, 0]) * 256 + int(depth_rgb[y, x, 1])
        if code == 0:
            missing += 1
            continue
        actual = (code - 1) / DEPTH_SCALE - 128.0
        actual_depths.append(actual)
        error = abs(actual - row[6])
        errors.append(error)
        samples.append({"routeIndex": index, "screen": [x, y], "world": [row[1], row[2], row[3]], "expected": row[6], "actual": actual, "absoluteError": error})
    if not errors:
        return {"sampleCount": 0, "missingSamples": missing, "medianAbsoluteError": None, "p95AbsoluteError": None, "maxAbsoluteError": None}
    return {
        "sampleCount": len(errors),
        "missingSamples": missing,
        "medianAbsoluteError": float(np.median(errors)),
        "p95AbsoluteError": float(np.percentile(errors, 95)),
        "maxAbsoluteError": float(np.max(errors)),
        "medianRuntimeDepth": float(np.median(actual_depths)),
        "worstSamples": sorted(samples, key=lambda item: item["absoluteError"], reverse=True)[:10],
    }


def write_route_overlay(background_path, route, output_dir):
    width, height = route["width"], route["height"]
    records = route["route"]
    total = records[-1][0]
    steps = int(route["defaultMovementSteps"])
    stops = [interpolate_route(records, total * index / steps) for index in range(steps + 1)]

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    path = [(row[4], row[5]) for row in records]
    draw.line(path, fill=(8, 18, 27, 230), width=10, joint="curve")
    draw.line(path, fill=(40, 232, 215, 255), width=5, joint="curve")
    for index, stop in enumerate(stops):
        x, y = stop[4], stop[5]
        radius = 5 if index not in (0, steps) else 8
        color = (92, 245, 141, 255) if index == 0 else (255, 202, 84, 255) if index == steps else (245, 251, 255, 255)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color, outline=(10, 20, 28, 255), width=2)

    overlay_path = output_dir / "route-overlay.png"
    overlay.save(overlay_path, optimize=True)
    base = Image.open(background_path).convert("RGBA")
    composite = Image.alpha_composite(base, overlay)
    composite.save(output_dir / "route-overlay-review.png", optimize=True)
    return overlay_path, output_dir / "route-overlay-review.png", stops


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map-dir", type=Path, required=True)
    args = parser.parse_args()
    map_dir = args.map_dir.resolve()
    config = json.loads((map_dir / "scene-config.json").read_text(encoding="utf-8"))
    route_path = map_dir / "output/route.json"
    background_path = map_dir / "output/background.png"
    depth_path = map_dir / "output/depth.png"
    route = json.loads(route_path.read_text(encoding="utf-8"))
    records = route["route"]

    background = Image.open(background_path)
    depth_image = Image.open(depth_path).convert("RGB")
    depth_rgb = np.asarray(depth_image, dtype=np.uint8)
    dimensions_match = background.size == (route["width"], route["height"]) == depth_image.size

    normal = depth_samples(records, depth_rgb, False)
    flipped = depth_samples(records, depth_rgb, True)
    orientation = "top-down" if normal["medianAbsoluteError"] is not None and normal["medianAbsoluteError"] <= flipped["medianAbsoluteError"] else "vertically-flipped"
    depth_alignment = normal if orientation == "top-down" else flipped

    route_line = LineString([(row[4], row[5]) for row in records])
    out_of_frame = sum(not (0 <= row[4] < route["width"] and 0 <= row[5] < route["height"]) for row in records)
    final_scale = config["render"]["finalResolution"][0] / route["width"]
    spacing = {}
    for movement_steps in (30, 40, 50, 60):
        stops = [interpolate_route(records, records[-1][0] * index / movement_steps) for index in range(movement_steps + 1)]
        spacing[str(movement_steps)] = {
            "stopCount": len(stops),
            "minimumPairSpacingFinalPx": round(min_pair_spacing(stops) * final_scale, 2),
        }

    overlay_path, review_path, default_stops = write_route_overlay(background_path, route, map_dir / "output")
    issues = []
    if not dimensions_match:
        issues.append("Background, depth and route dimensions do not match")
    if not route_line.is_simple:
        issues.append("Projected route is not simple in screen space")
    if out_of_frame:
        issues.append(f"{out_of_frame} route samples fall outside the image")
    if depth_alignment["missingSamples"]:
        issues.append("Some projected road samples contain the depth background sentinel")
    if depth_alignment["p95AbsoluteError"] is None or depth_alignment["p95AbsoluteError"] > 0.25:
        issues.append("Depth samples do not align with the projected road")
    if route["defaultStopCount"] != route["defaultMovementSteps"] + 1 or len(default_stops) != route["defaultStopCount"]:
        issues.append("Default stop count must equal movement steps plus one")

    report = {
        "status": "PASS" if not issues else "REVIEW_REQUIRED",
        "map": route["map"],
        "dimensionsMatch": dimensions_match,
        "projectedRouteIsSimple": route_line.is_simple,
        "routeSamplesOutsideFrame": out_of_frame,
        "routeLength": route["length"],
        "movementStopSpacing": spacing,
        "defaultMovementSteps": route["defaultMovementSteps"],
        "defaultStopCount": len(default_stops),
        "depthOrientation": orientation,
        "depthRoadAlignment": depth_alignment,
        "depthFlipComparison": {"topDownMedianError": normal["medianAbsoluteError"], "flippedMedianError": flipped["medianAbsoluteError"]},
        "routeOverlay": str(overlay_path.relative_to(map_dir)).replace("\\", "/"),
        "routeOverlayReview": str(review_path.relative_to(map_dir)).replace("\\", "/"),
        "issues": issues,
    }
    report_path = map_dir / "reports/map-validation.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
