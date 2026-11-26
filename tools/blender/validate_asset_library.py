"""Validate the generated KayKit Blender library and write a JSON report.

  blender --background --python tools/blender/validate_asset_library.py -- \
    --blend assets/kaykit-medieval/library/kaykit-medieval.blend \
    --manifest assets/kaykit-medieval/asset-manifest.json
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys

import bpy


def parse_args():
    script_args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blend", required=True, type=pathlib.Path)
    parser.add_argument("--manifest", required=True, type=pathlib.Path)
    parser.add_argument("--report", type=pathlib.Path)
    return parser.parse_args(script_args)


def main():
    args = parse_args()
    blend_path = args.blend.resolve()
    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))

    model_collections = [
        collection for collection in bpy.data.collections
        if collection.get("source_asset")
    ]
    failures = []
    warnings = []
    source_ids = set()
    mesh_count = 0
    vertex_count = 0
    parented_object_count = 0
    for collection in model_collections:
        source = collection["source_asset"]
        if source in source_ids:
            failures.append(f"Duplicate source mapping: {source}")
        source_ids.add(source)
        meshes = [obj for obj in collection.all_objects if obj.type == "MESH"]
        mesh_count += len(meshes)
        vertex_count += sum(len(obj.data.vertices) for obj in meshes)
        if not meshes:
            failures.append(f"No mesh geometry in {source}")
        for obj in collection.all_objects:
            if obj.parent:
                parented_object_count += 1
                if obj.parent.name not in bpy.data.objects:
                    failures.append(f"Missing parent for {source}: {obj.name}")
            for value in (*obj.location, *obj.rotation_euler, *obj.scale):
                if not math.isfinite(value):
                    failures.append(f"Non-finite transform in {source}: {obj.name}")

    marked = [
        collection for collection in model_collections
        if getattr(collection, "asset_data", None) is not None
    ]
    unmarked = [collection.name for collection in model_collections if collection not in marked]
    if unmarked:
        failures.append(f"{len(unmarked)} model collections are not Asset Browser assets")

    # Ignore Blender's non-persistent Render Result / Viewer buffer.
    images = [image for image in bpy.data.images if image.source != "VIEWER"]
    unpacked = [image.name for image in images if not getattr(image, "packed_file", None)]
    if unpacked:
        failures.append(f"{len(unpacked)} images are not packed: {', '.join(unpacked[:8])}")
    # A library reopened from a script can leave image pixels lazily decoded;
    # packed bytes and positive dimensions are the portable integrity checks.
    empty_images = [
        image.name for image in images
        if min(image.size) <= 0 or not image.packed_file or image.packed_file.size <= 0
    ]
    if empty_images:
        failures.append(f"{len(empty_images)} images have no decoded pixels: {', '.join(empty_images[:8])}")

    catalog_file = blend_path.parent / "blender_assets.cats.txt"
    catalog_rows = []
    if not catalog_file.exists():
        failures.append("Missing blender_assets.cats.txt beside the library")
    else:
        for line in catalog_file.read_text(encoding="utf-8").splitlines():
            if line and not line.startswith("#") and not line.startswith("VERSION"):
                catalog_rows.append(line)

    expected_models = int(manifest.get("modelCount", -1))
    if len(model_collections) != expected_models:
        failures.append(f"Manifest says {expected_models} models; library has {len(model_collections)}")
    if len(marked) != int(manifest.get("assetBrowserMarkedCount", -1)):
        failures.append("Asset Browser count differs from the import manifest")
    if len(images) != int(manifest.get("packedImageCount", -1)):
        failures.append("Packed image count differs from the import manifest")
    if len(catalog_rows) != len({collection.asset_data.catalog_id for collection in marked}):
        warnings.append("Catalog count does not exactly match marked collection catalog IDs")

    report = {
        "status": "PASS" if not failures else "FAIL",
        "blendFile": str(blend_path),
        "blenderVersion": bpy.app.version_string,
        "modelCount": len(model_collections),
        "assetBrowserMarkedCount": len(marked),
        "meshObjectCount": mesh_count,
        "vertexCount": vertex_count,
        "parentedObjectCount": parented_object_count,
        "packedImageCount": len(images) - len(unpacked),
        "catalogCount": len(catalog_rows),
        "failures": failures,
        "warnings": warnings,
    }
    report_path = (args.report or blend_path.parent.parent / "library-validation.json").resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
