"""Convert Blender's multilayer OpenEXR depth output to Quest's RGB depth PNG."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import OpenEXR
from PIL import Image


DEPTH_OFFSET = 128.0
DEPTH_SCALE = 32.0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    args = parser.parse_args()

    exr = OpenEXR.File(str(args.input))
    channels = exr.channels()
    depth_key = next((name for name in channels if name.rsplit(".", 1)[-1] in {"V", "R", "Y"}), None)
    if depth_key is None:
        raise RuntimeError(f"No scalar depth channel found in {args.input}; channels: {list(channels)}")

    depth = np.asarray(channels[depth_key].pixels, dtype=np.float32)
    if depth.shape != (args.height, args.width):
        raise RuntimeError(f"Depth dimensions {depth.shape[::-1]} do not match render {(args.width, args.height)}")

    valid = np.isfinite(depth) & (depth > 0.0) & (depth <= 100000.0)
    runtime_depth = DEPTH_OFFSET - depth
    codes = np.zeros(depth.shape, dtype=np.uint16)
    encoded = np.rint((runtime_depth[valid] + DEPTH_OFFSET) * DEPTH_SCALE).astype(np.int64) + 1
    codes[valid] = np.clip(encoded, 1, 65535).astype(np.uint16)

    rgb = np.zeros((args.height, args.width, 3), dtype=np.uint8)
    rgb[..., 0] = (codes >> 8).astype(np.uint8)
    rgb[..., 1] = (codes & 255).astype(np.uint8)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgb, mode="RGB").save(args.output, optimize=True)

    valid_depth = runtime_depth[valid]
    report = {
        "validPixels": int(valid.sum()),
        "backgroundPixels": int(valid.size - valid.sum()),
        "minRuntimeDepth": float(np.min(valid_depth)) if valid.any() else None,
        "maxRuntimeDepth": float(np.max(valid_depth)) if valid.any() else None,
        "sourceChannel": depth_key,
        "sourceDepthConvention": "Blender camera-space positive distance",
        "encoding": "RGB; code=R*256+G; depth=(code-1)/32-128; code 0 means background; greater is nearer.",
    }
    print(json.dumps(report))


if __name__ == "__main__":
    main()
