"""Build a reusable Blender Asset Browser library from the official KayKit pack.

Run with Blender's bundled Python, not the project's virtual environment:

  blender --background --python tools/blender/build_asset_library.py -- \
    --zip assets/kaykit-medieval/originals/KayKit_Medieval_Hexagon_Pack_1.0_FREE.zip \
    --output assets/kaykit-medieval/library/kaykit-medieval.blend

Only glTF sources are imported. The complete original archive stays intact as
the source of record; temporary extracted files are removed after packing the
imported textures into the Blender file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import sys
import tempfile
import uuid
import zipfile

import bpy
from mathutils import Vector


CATALOG_NAMESPACE = uuid.UUID("83f6e11a-51cc-4dd0-99d4-70dd516ab4d2")
PACK_PREFIX = "KayKit_Medieval_Hexagon_Pack_1.0_FREE/"


def parse_args():
    script_args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--manifest", type=pathlib.Path)
    parser.add_argument("--preview", type=pathlib.Path)
    return parser.parse_args(script_args)


def stable_id(category):
    return str(uuid.uuid5(CATALOG_NAMESPACE, category))


def category_for(relative):
    parts = [part.lower() for part in pathlib.PurePosixPath(relative).parts]
    name = pathlib.PurePosixPath(relative).stem.lower()
    if parts[0] == "tiles":
        if "roads" in parts or "road" in name:
            return "Roads"
        if "rivers" in parts:
            return "Bridges" if "crossing" in name else "Rivers and water"
        if "coast" in parts:
            return "Coasts"
        return "Terrain"
    if parts[0] == "decoration" and len(parts) > 1 and parts[1] == "nature":
        if any(word in name for word in ("mountain", "hill", "rock")):
            return "Rocks and mountains"
        return "Trees and vegetation"
    if parts[0] == "decoration" and len(parts) > 1 and parts[1] == "props":
        return "Environmental props"
    if parts[0] == "buildings":
        if "bridge" in name or "crossing" in name:
            return "Bridges"
        if any(word in name for word in ("castle", "tower", "wall_")):
            return "Castles and fortifications"
        if any(word in name for word in ("grain", "windmill", "farm", "crop")):
            return "Farms"
        if any(word in name for word in ("fence", "gate", "stage", "scaffolding")):
            return "Infrastructure"
        return "Architecture"
    return "Environmental props"


def extract_gltf_sources(archive, temp_dir):
    prefix = PACK_PREFIX + "Assets/gltf/"
    members = []
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            name = info.filename
            if info.is_dir() or not name.startswith(prefix):
                continue
            if pathlib.PurePosixPath(name).suffix.lower() not in {".gltf", ".bin", ".png"}:
                continue
            zf.extract(info, temp_dir)
            if name.lower().endswith(".gltf"):
                relative = name[len(prefix):]
                members.append((relative, pathlib.Path(temp_dir, *pathlib.PurePosixPath(name).parts)))
    members.sort(key=lambda item: item[0].lower())
    if not members:
        raise RuntimeError(f"No glTF files found under {prefix} in {archive}")
    return members


def object_bounds(objects):
    points = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not points:
        return None
    minimum = Vector(tuple(min(point[i] for point in points) for i in range(3)))
    maximum = Vector(tuple(max(point[i] for point in points) for i in range(3)))
    dimensions = maximum - minimum
    return {
        "minimum": list(minimum),
        "maximum": list(maximum),
        "dimensions": list(dimensions),
    }


def collection_for(root, category_collections, asset_slug, category):
    if category not in category_collections:
        category_collection = bpy.data.collections.new(category)
        root.children.link(category_collection)
        category_collections[category] = category_collection
    collection = bpy.data.collections.new(asset_slug)
    category_collections[category].children.link(collection)
    return collection


def mark_collection_asset(collection, category, source_relative):
    try:
        with bpy.context.temp_override(selected_ids=[collection]):
            bpy.ops.asset.mark()
        metadata = collection.asset_data
        metadata.catalog_id = stable_id(category)
        for key, value in (("author", "Kay Lousberg"), ("description", f"KayKit Medieval Hexagon asset from {source_relative}. Original proportions and hierarchy retained; source pack is CC0."), ("license", "CC0 1.0")):
            if hasattr(metadata, key):
                setattr(metadata, key, value)
        for tag in ("KayKit", category, "CC0"):
            try:
                metadata.tags.new(tag)
            except (AttributeError, RuntimeError, TypeError):
                pass
        return True, None
    except Exception as exc:  # Keep the reusable collection if an API version changes.
        return False, str(exc)


def make_material(name, color, roughness=0.8):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    if shader:
        shader.inputs["Base Color"].default_value = (*color, 1.0)
        shader.inputs["Roughness"].default_value = roughness
    return material


def look_at(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()


def add_mesh_object(collection, name, vertices, faces, material):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def make_box(collection, name, center, size, material):
    cx, cy, cz = center
    sx, sy, sz = (value / 2 for value in size)
    vertices = [
        (cx - sx, cy - sy, cz - sz), (cx + sx, cy - sy, cz - sz),
        (cx + sx, cy + sy, cz - sz), (cx - sx, cy + sy, cz - sz),
        (cx - sx, cy - sy, cz + sz), (cx + sx, cy - sy, cz + sz),
        (cx + sx, cy + sy, cz + sz), (cx - sx, cy + sy, cz + sz),
    ]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return add_mesh_object(collection, name, vertices, faces, material)


def create_showcase(source_collections, bounds_by_source, output_path, preview_path):
    scene = bpy.data.scenes.new("KayKit Asset Showcase")
    engine_ids = {item.identifier for item in scene.render.bl_rna.properties["engine"].enum_items}
    eevee_id = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engine_ids else "BLENDER_EEVEE"
    scene.render.engine = eevee_id
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = 64
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("Showcase World")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.11, 0.17, 0.20, 1)
    scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.8
    scene.view_settings.exposure = 0.35

    display = bpy.data.collections.new("SHOWCASE DISPLAY")
    scene.collection.children.link(display)
    ground_material = make_material("Showcase | Slate", (0.15, 0.23, 0.24))
    base_material = make_material("Showcase | Plinth", (0.34, 0.43, 0.40))
    text_material = make_material("Showcase | Label", (0.94, 0.87, 0.68))
    add_mesh_object(display, "Showcase Ground", [(-60, -60, -0.20), (60, -60, -0.20), (60, 60, -0.20), (-60, 60, -0.20)], [(0, 1, 2, 3)], ground_material)

    picks = [
        ("tiles/base/hex_grass.gltf", "Grass tile"),
        ("tiles/roads/hex_road_A.gltf", "Road tile"),
        ("tiles/rivers/hex_river_A.gltf", "River tile"),
        ("tiles/rivers/hex_river_crossing_A.gltf", "River crossing"),
        ("tiles/coast/hex_coast_A.gltf", "Coast tile"),
        ("decoration/nature/mountain_C.gltf", "Mountain"),
        ("decoration/nature/hill_single_A.gltf", "Hill"),
        ("decoration/nature/rock_single_C.gltf", "Rock"),
        ("decoration/nature/tree_single_A.gltf", "Tree A"),
        ("decoration/nature/tree_single_B.gltf", "Tree B"),
        ("buildings/red/building_home_A_red.gltf", "House"),
        ("buildings/red/building_market_red.gltf", "Market"),
        ("buildings/red/building_windmill_red.gltf", "Windmill"),
        ("buildings/neutral/building_bridge_A.gltf", "Bridge"),
        ("buildings/red/building_castle_red.gltf", "Castle"),
        ("decoration/props/resource_lumber.gltf", "Lumber prop"),
    ]
    missing = [path for path, _ in picks if path not in source_collections]
    if missing:
        raise RuntimeError("Showcase source missing: " + ", ".join(missing))

    columns = 4
    spacing_x, spacing_y = 6.1, 5.9
    start_x, start_y = -((columns - 1) * spacing_x) / 2, 8.8
    for index, (source, label) in enumerate(picks):
        column, row = index % columns, index // columns
        x = start_x + column * spacing_x
        y = start_y - row * spacing_y
        bounds = bounds_by_source[source]
        minimum, maximum = Vector(bounds["minimum"]), Vector(bounds["maximum"])
        dimensions = maximum - minimum
        extent = max(dimensions)
        scale = 2.65 / max(extent, 0.001)
        floor_z = 0.18

        make_box(display, f"Plinth {index + 1:02d}", (x, y, 0.015), (5.45, 5.00, 0.30), base_material)
        instance = bpy.data.objects.new(f"Preview {label}", None)
        instance.instance_type = "COLLECTION"
        instance.instance_collection = source_collections[source]
        instance.empty_display_type = "PLAIN_AXES"
        instance.scale = (scale, scale, scale)
        center = (minimum + maximum) / 2
        instance.location = (x - scale * center.x, y - scale * center.y, floor_z - scale * minimum.z)
        display.objects.link(instance)

        curve = bpy.data.curves.new(f"Label {label}", type="FONT")
        curve.body = label
        curve.size = 0.28
        curve.extrude = 0.001
        curve.materials.append(text_material)
        text = bpy.data.objects.new(f"Label {label}", curve)
        text.location = (x - 2.35, y - 2.25, 0.172)
        display.objects.link(text)

    camera_data = bpy.data.cameras.new("Showcase Camera")
    camera = bpy.data.objects.new("Showcase Camera", camera_data)
    display.objects.link(camera)
    camera.location = (0, -38, 58)
    look_at(camera, (0, -0.2, 0))
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 36.0
    scene.camera = camera

    def area_light(name, location, power, size, color):
        data = bpy.data.lights.new(name, type="AREA")
        data.energy = power
        data.shape = "DISK"
        data.size = size
        data.color = color
        light = bpy.data.objects.new(name, data)
        display.objects.link(light)
        light.location = location
        look_at(light, (0, 0, 0))
        return light

    area_light("Key | Warm Softbox", (-12, -16, 34), 7000, 18, (1.0, 0.84, 0.66))
    area_light("Fill | Cool Sky", (14, 3, 30), 4600, 22, (0.63, 0.79, 1.0))
    area_light("Rim | Warm Horizon", (0, 18, 24), 3000, 14, (1.0, 0.68, 0.42))

    scene.render.filepath = str(preview_path.resolve())
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True, scene=scene.name)
    return scene


def write_catalog_file(output_path, categories):
    catalog_path = output_path.parent / "blender_assets.cats.txt"
    lines = [
        "# Asset Catalog Definition File",
        "# Generated by tools/blender/build_asset_library.py",
        "VERSION 1",
    ]
    for category in sorted(categories):
        lines.append(f"{stable_id(category)}:KayKit/{category}:{category}")
    catalog_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    args = parse_args()
    archive = args.zip.resolve()
    output = args.output.resolve()
    manifest = (args.manifest or output.parent.parent / "asset-manifest.json").resolve()
    preview = (args.preview or output.parent.parent / "previews" / "asset-showcase.png").resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not hasattr(bpy.ops.import_scene, "gltf"):
        raise RuntimeError("Blender's glTF 2.0 importer is not available")

    library_scene = bpy.context.scene
    library_scene.name = "KayKit Asset Library"
    library_root = bpy.data.collections.new("KAYKIT MEDIEVAL HEXAGON")
    library_scene.collection.children.link(library_root)
    category_collections = {}
    source_collections = {}
    entries = []
    warnings = []

    with tempfile.TemporaryDirectory(prefix="kaykit-gltf-") as temp_dir:
        sources = extract_gltf_sources(archive, temp_dir)
        for index, (relative, gltf_path) in enumerate(sources, start=1):
            source_slug = pathlib.PurePosixPath(relative).with_suffix("").as_posix().replace("/", "__")
            category = category_for(relative)
            asset_collection = collection_for(library_root, category_collections, source_slug, category)
            before = set(bpy.data.objects)
            bpy.ops.import_scene.gltf(filepath=str(gltf_path), import_pack_images=False)
            new_objects = [obj for obj in bpy.data.objects if obj not in before]
            if not new_objects:
                raise RuntimeError(f"Importer produced no objects for {relative}")
            for object_index, obj in enumerate(new_objects, start=1):
                for old_collection in list(obj.users_collection):
                    old_collection.objects.unlink(obj)
                suffix = "" if len(new_objects) == 1 else f"__part_{object_index:02d}"
                obj.name = source_slug + suffix
                if obj.data:
                    obj.data.name = source_slug + suffix + "_data"
                asset_collection.objects.link(obj)
            bpy.context.view_layer.update()
            bounds = object_bounds(new_objects)
            if bounds is None or any(value <= 0 for value in bounds["dimensions"]):
                warnings.append(f"No non-zero mesh dimensions for {relative}")
            asset_collection["source_asset"] = relative
            asset_collection["asset_category"] = category
            marked, mark_error = mark_collection_asset(asset_collection, category, relative)
            if not marked:
                warnings.append(f"Asset Browser mark failed for {relative}: {mark_error}")
            source_collections[relative] = asset_collection
            entries.append({
                "id": source_slug,
                "source": relative,
                "category": category,
                "objectCount": len(new_objects),
                "meshObjectCount": sum(obj.type == "MESH" for obj in new_objects),
                "vertexCount": sum(len(obj.data.vertices) for obj in new_objects if obj.type == "MESH"),
                "dimensions": bounds["dimensions"] if bounds else None,
                "bounds": bounds,
                "assetBrowserMarked": marked,
            })
            if index % 25 == 0 or index == len(sources):
                print(f"Imported {index}/{len(sources)} KayKit models")

        # Pack atlases before the temporary extraction tree is cleaned up.
        bpy.ops.file.pack_all()

    bpy.context.view_layer.update()
    bounds_by_source = {entry["source"]: entry["bounds"] for entry in entries if entry["bounds"]}
    showcase_scene = create_showcase(source_collections, bounds_by_source, output, preview)

    # The image data was packed while source paths were still available, so the
    # library remains portable after the temporary directory has been removed.
    packed_images = sum(bool(getattr(image, "packed_file", None)) for image in bpy.data.images)
    for scene in bpy.data.scenes:
        scene.render.resolution_percentage = 100
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    write_catalog_file(output, category_collections)

    manifest_data = {
        "schemaVersion": 1,
        "name": "KayKit Medieval Hexagon Pack",
        "author": "Kay Lousberg",
        "version": "1.0 FREE",
        "license": "CC0 1.0 Universal",
        "licenseSource": "KayKit_Medieval_Hexagon_Pack_1.0_FREE/License.txt",
        "sourceArchive": archive.name,
        "sourceArchiveBytes": archive.stat().st_size,
        "sourceArchiveSha256": sha256(archive),
        "blenderVersion": bpy.app.version_string,
        "assetLibrary": os.path.relpath(output, manifest.parent),
        "assetCatalogs": os.path.relpath(output.parent / "blender_assets.cats.txt", manifest.parent),
        "showcase": os.path.relpath(preview, manifest.parent),
        "modelCount": len(entries),
        "assetBrowserMarkedCount": sum(entry["assetBrowserMarked"] for entry in entries),
        "packedImageCount": packed_images,
        "categories": sorted(category_collections),
        "assets": entries,
        "warnings": warnings,
    }
    manifest.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "assetLibrary": str(output),
        "showcase": str(preview),
        "manifest": str(manifest),
        "importedModels": len(entries),
        "assetBrowserMarked": manifest_data["assetBrowserMarkedCount"],
        "packedImages": packed_images,
        "warnings": len(warnings),
        "showcaseScene": showcase_scene.name,
    }, indent=2))


if __name__ == "__main__":
    main()
