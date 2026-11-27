"""Assemble and bake a declarative Quest map in Blender.

Example:
  blender --background --python tools/blender/assemble_map.py -- \
    --config maps/kingdom-quest/scene-config.json --quality draft

The script links KayKit collections from the shared library, builds only the
terrain, water and traversable road surfaces that are specific to this map,
then saves an editable .blend, background render, lossless runtime depth map,
route data and camera/landmark metadata.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import random
import subprocess
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils.bvhtree import BVHTree
from mathutils import Vector


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
LIBRARY_PATH = PROJECT_ROOT / "assets/kaykit-medieval/library/kaykit-medieval.blend"
MANIFEST_PATH = PROJECT_ROOT / "assets/kaykit-medieval/asset-manifest.json"
DEPTH_OFFSET = 128.0
ASSET_INFO = {
    item["source"]: item
    for item in json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["assets"]
} if MANIFEST_PATH.exists() else {}
PROP_ASSETS = {
    "decoration/props/barrel.gltf",
    "decoration/props/crate_A_big.gltf",
    "decoration/props/resource_lumber.gltf",
    "decoration/props/resource_stone.gltf",
    "decoration/props/sack.gltf",
}


def parse_args():
    script_args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=pathlib.Path, default=PROJECT_ROOT / "maps/kingdom-quest/scene-config.json")
    parser.add_argument("--quality", choices=("draft", "review", "final"), default="draft")
    parser.add_argument("--output-blend", type=pathlib.Path)
    parser.add_argument("--output-dir", type=pathlib.Path)
    return parser.parse_args(script_args)


def slug(source):
    return pathlib.PurePosixPath(source).with_suffix("").as_posix().replace("/", "__")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def assets_needed(config):
    required = {bridge["asset"] for bridge in bridge_specs(config)}
    required.update({config["castle"]["asset"], "buildings/neutral/building_grain.gltf"})
    required.update(item["asset"] for item in config.get("shoreStructures", []))
    required.update(item["asset"] for item in config["buildings"])
    required.update(PROP_ASSETS)
    required.update(source for group in config["forestGroups"] for source in group["variants"])
    required.update(source for group in config["rockGroups"] for source in group["variants"])
    return sorted(required)


def bridge_specs(config):
    """Normalize the legacy single bridge and the multi-bridge map format."""
    river = config["river"]
    bridges = river.get("bridges")
    if bridges:
        output = []
        for index, item in enumerate(bridges, start=1):
            output.append({
                "name": item.get("name", f"River Crossing {index}"),
                "center": item["center"],
                "asset": item.get("asset", river.get("bridgeAsset", "buildings/neutral/building_bridge_A.gltf")),
                "scale": item.get("scale", river.get("bridgeScale", 1.8)),
                "deckOffset": item.get("deckOffset", river.get("bridgeDeckOffset", 0.3)),
                "deckLocalZ": item.get("deckLocalZ", river.get("bridgeDeckLocalZ", 0.2)),
                "approachRadius": item.get("approachRadius", config["road"].get("bridgeApproachRadius", 3.5)),
            })
        return output
    return [{
        "name": "Whispering Ford",
        "center": river["bridgeCenter"],
        "asset": river["bridgeAsset"],
        "scale": river.get("bridgeScale", 1.8),
        "deckOffset": river["bridgeDeckOffset"],
        "deckLocalZ": river["bridgeDeckLocalZ"],
        "approachRadius": config["road"]["bridgeApproachRadius"],
    }]


def link_asset_collections(sources):
    if not LIBRARY_PATH.exists():
        raise FileNotFoundError(f"KayKit Blender library not found: {LIBRARY_PATH}")
    names = [slug(source) for source in sources]
    with bpy.data.libraries.load(str(LIBRARY_PATH), link=True) as (source_data, target_data):
        available = set(source_data.collections)
        missing = [name for name in names if name not in available]
        if missing:
            raise RuntimeError("Missing collections in KayKit library: " + ", ".join(missing))
        target_data.collections = names
    linked = {collection.name: collection for collection in target_data.collections if collection}
    return {source: linked[slug(source)] for source in sources}


def new_collection(scene, name):
    collection = bpy.data.collections.new(name)
    scene.collection.children.link(collection)
    return collection


def material(name, color, roughness=0.82, metallic=0.0, transmission=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    if not mat.use_nodes:
        mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    if shader:
        shader.inputs["Base Color"].default_value = (*color, 1.0)
        shader.inputs["Roughness"].default_value = roughness
        shader.inputs["Metallic"].default_value = metallic
        if "Transmission Weight" in shader.inputs:
            shader.inputs["Transmission Weight"].default_value = transmission
        elif "Transmission" in shader.inputs:
            shader.inputs["Transmission"].default_value = transmission
        if "Coat Weight" in shader.inputs:
            shader.inputs["Coat Weight"].default_value = 0.18 if transmission else 0.0
    return mat


def make_materials():
    return {
        "grass": material("Terrain | Meadow grass", (0.20, 0.39, 0.13)),
        "meadow": material("Terrain | Sunlit meadow", (0.34, 0.53, 0.19)),
        "forest": material("Terrain | Woodland floor", (0.12, 0.28, 0.10)),
        "shore": material("Terrain | River gravel and sand", (0.60, 0.41, 0.22)),
        "rock": material("Terrain | Exposed mountain stone", (0.25, 0.29, 0.30)),
        "cliff_a": material("Island cut | Slate", (0.19, 0.25, 0.28)),
        "cliff_b": material("Island cut | Warm strata", (0.28, 0.30, 0.28)),
        "cliff_c": material("Island cut | Basalt", (0.12, 0.18, 0.21)),
        "mountain_shadow": material("Crown Ridge | Blue slate shadow", (0.105, 0.15, 0.20)),
        "mountain_rock": material("Crown Ridge | Weathered slate", (0.20, 0.26, 0.30)),
        "mountain_warm": material("Crown Ridge | Warm exposed face", (0.30, 0.26, 0.22)),
        "mountain_light": material("Crown Ridge | Lit stone facet", (0.36, 0.40, 0.41)),
        "sea": material("Sea | Deep blue", (0.018, 0.09, 0.15), roughness=0.24, metallic=0.1),
        "river": material("River | Deep teal", (0.025, 0.24, 0.34), roughness=0.2, metallic=0.12, transmission=0.04),
        "river_edge": material("River | Shallow turquoise", (0.07, 0.42, 0.48), roughness=0.18, metallic=0.08, transmission=0.03),
        "road_edge": material("Road | Dark earth edge", (0.18, 0.12, 0.065)),
        "road": material("Road | Packed ochre earth", (0.52, 0.34, 0.18)),
        "lane": material("Settlement | Worn stone lane", (0.38, 0.34, 0.26)),
        "court": material("Settlement | Sunlit gate court", (0.60, 0.52, 0.37)),
        "field_soil": material("Fields | Dark furrow soil", (0.22, 0.15, 0.065)),
        "crop_a": material("Fields | Wheat gold", (0.67, 0.43, 0.10)),
        "crop_b": material("Fields | Wheat light", (0.82, 0.59, 0.16)),
    }


def catmull_rom(points, steps_per_segment=12):
    source = [Vector((float(point[0]), float(point[1]))) for point in points]
    if len(source) < 2:
        raise ValueError("A path needs at least two control points")
    output = []
    for index in range(len(source) - 1):
        p0 = source[max(0, index - 1)]
        p1 = source[index]
        p2 = source[index + 1]
        p3 = source[min(len(source) - 1, index + 2)]
        for step in range(steps_per_segment):
            t = step / steps_per_segment
            t2, t3 = t * t, t * t * t
            point = 0.5 * (
                2 * p1
                + (-p0 + p2) * t
                + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                + (-p0 + 3 * p1 - 3 * p2 + p3) * t3
            )
            output.append(point)
    output.append(source[-1])
    return output


def nearest_path(point, path):
    point = Vector((float(point[0]), float(point[1])))
    best_dist2 = float("inf")
    best_point = None
    best_tangent = Vector((1.0, 0.0))
    best_index = 0
    for index, (a, b) in enumerate(zip(path, path[1:])):
        ab = b - a
        denom = ab.length_squared
        t = 0.0 if denom <= 1e-12 else max(0.0, min(1.0, (point - a).dot(ab) / denom))
        closest = a + t * ab
        dist2 = (point - closest).length_squared
        if dist2 < best_dist2:
            best_dist2 = dist2
            best_point = closest
            best_tangent = ab.normalized() if ab.length > 1e-8 else best_tangent
            best_index = index
    return math.sqrt(best_dist2), best_point, best_tangent, best_index


def gaussian(x, y, center, height, radius):
    dx = (x - center[0]) / max(radius[0], 0.001)
    dy = (y - center[1]) / max(radius[1], 0.001)
    return height * math.exp(-0.5 * (dx * dx + dy * dy))


class MapSurface:
    def __init__(self, config, river_path):
        self.config = config
        self.terrain = config["terrain"]
        self.river = config["river"]
        self.river_path = river_path
        self.terrain_bvh = None

    def bind_terrain_mesh(self, mesh):
        vertices = [vertex.co.copy() for vertex in mesh.vertices]
        polygons = [tuple(poly.vertices) for poly in mesh.polygons]
        self.terrain_bvh = BVHTree.FromPolygons(vertices, polygons, all_triangles=True, epsilon=0.0)

    def base_height(self, x, y):
        cfg = self.terrain
        value = cfg["baseElevation"]
        value += 0.08 * math.sin(0.32 * x + 0.4) * math.cos(0.28 * y - 0.5)
        for hill in cfg["hills"]:
            value += gaussian(x, y, hill["center"], hill["height"], hill["radius"])
        peaks = [gaussian(x, y, peak["center"], peak["height"], peak["radius"]) for peak in cfg["mountainPeaks"]]
        if peaks:
            value += max(peaks)
        return value

    def river_distance(self, x, y):
        return nearest_path((x, y), self.river_path)[0]

    def height(self, x, y):
        if self.terrain_bvh is not None:
            hit = self.terrain_bvh.ray_cast(Vector((x, y, 100.0)), Vector((0.0, 0.0, -1.0)), 200.0)
            if hit[0] is not None:
                return hit[0].z
        dist = self.river_distance(x, y)
        sigma = self.terrain["riverValleySigma"]
        valley = self.terrain["riverValleyDepth"] * math.exp(-0.5 * (dist / sigma) ** 2)
        return self.base_height(x, y) - valley

    def river_z(self, x, y, along=0.0):
        dist = self.river_distance(x, y)
        sigma = self.terrain["riverValleySigma"]
        floor = self.terrain["riverValleyDepth"] * math.exp(-0.5 * (dist / sigma) ** 2)
        return self.base_height(x, y) - floor + self.river["waterOffsetFromValleyFloor"] + 0.025 * math.sin(along * 0.55)

    def road_z(self, x, y):
        road = self.config["road"]
        base = self.height(x, y) + road["surfaceOffset"]
        best_blend, bridge_z = 0.0, base
        for bridge in bridge_specs(self.config):
            bx, by = bridge["center"]
            dist = math.hypot(x - bx, y - by)
            dims = ASSET_INFO.get(bridge["asset"], {}).get("dimensions", [1.33, 1.92, 1.25])
            deck_half_span = dims[1] * bridge["scale"] * 0.5
            deck_top = self.river_z(bx, by) + bridge["deckOffset"] + 0.05 * bridge["scale"]
            if dist <= deck_half_span + 0.04:
                return deck_top - 0.055
            u = max(0.0, min(1.0, 1.0 - dist / bridge["approachRadius"]))
            blend = u * u * (3.0 - 2.0 * u)
            if blend > best_blend:
                best_blend = blend
                bridge_z = deck_top - 0.055
        return base * (1.0 - best_blend) + bridge_z * best_blend


def terrain_material_index(surface, materials, x, y, z):
    cfg = surface.terrain
    radius = math.sqrt((x / cfg["radiusX"]) ** 2 + (y / cfg["radiusY"]) ** 2)
    if z > 2.5:
        return materials["rock"]
    if radius > 0.925 or surface.river_distance(x, y) < surface.river["width"] * 0.5 + surface.river["shorelineWidth"]:
        return materials["shore"]
    for group in surface.config["forestGroups"]:
        dx = (x - group["center"][0]) / group["radius"][0]
        dy = (y - group["center"][1]) / group["radius"][1]
        if dx * dx + dy * dy < 1.0:
            return materials["forest"]
    if z > 0.7:
        return materials["meadow"]
    return materials["grass"]


def mesh_object(collection, name, vertices, faces, materials=(), indices=None, smooth=False):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(vertices, [], faces)
    for mat in materials:
        mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if indices:
        for polygon, index in zip(mesh.polygons, indices):
            polygon.material_index = int(index)
    if smooth:
        for polygon in mesh.polygons:
            polygon.use_smooth = True
    return obj


def build_island(surface, collection, materials):
    cfg = surface.terrain
    rings, segments = int(cfg["rings"]), int(cfg["segments"])
    vertices = [(0.0, 0.0, surface.height(0.0, 0.0))]
    boundary_points = []
    for ring in range(1, rings + 1):
        radius = ring / rings
        for step in range(segments):
            angle = 2.0 * math.pi * step / segments
            wave = 0.58 * math.sin(3.0 * angle + 0.2) + 0.27 * math.sin(5.0 * angle - 0.9) + 0.15 * math.cos(8.0 * angle + 0.8)
            radial_scale = 1.0 + cfg["boundaryVariation"] * (radius ** 3) * wave
            for inlet in cfg.get("inlets", []):
                center = math.radians(inlet["angleDegrees"])
                angular_delta = math.atan2(math.sin(angle - center), math.cos(angle - center))
                width = math.radians(max(0.1, inlet["widthDegrees"]))
                notch = inlet["depth"] * math.exp(-0.5 * (angular_delta / width) ** 2) * radius ** 2.2
                radial_scale -= notch
            x = cfg["radiusX"] * radius * radial_scale * math.cos(angle)
            y = cfg["radiusY"] * radius * radial_scale * math.sin(angle)
            z = surface.height(x, y)
            vertices.append((x, y, z))
            if ring == rings:
                boundary_points.append((x, y, z))

    faces = []
    material_indices = []
    top_materials = [materials[key] for key in ("grass", "meadow", "forest", "shore", "rock")]
    top_material_index = {mat: index for index, mat in enumerate(top_materials)}
    first = 1
    for i in range(segments):
        j = (i + 1) % segments
        face = (0, first + i, first + j)
        faces.append(face)
        x = sum(vertices[k][0] for k in face) / 3.0
        y = sum(vertices[k][1] for k in face) / 3.0
        z = sum(vertices[k][2] for k in face) / 3.0
        material_indices.append(top_material_index[terrain_material_index(surface, materials, x, y, z)])
    for ring in range(rings - 1):
        inner = 1 + ring * segments
        outer = inner + segments
        for i in range(segments):
            j = (i + 1) % segments
            for face in ((inner + i, outer + i, outer + j), (inner + i, outer + j, inner + j)):
                faces.append(face)
                x = sum(vertices[k][0] for k in face) / 3.0
                y = sum(vertices[k][1] for k in face) / 3.0
                z = sum(vertices[k][2] for k in face) / 3.0
                selected = terrain_material_index(surface, materials, x, y, z)
                material_indices.append(top_material_index[selected])

    top = mesh_object(collection, "Terrain | Crownfall Island", vertices, faces, top_materials, material_indices)
    surface.bind_terrain_mesh(top.data)

    levels = cfg["slabLevels"]
    side_vertices = list(boundary_points)
    side_rings = [list(range(segments))]
    for level_index, level in enumerate(levels):
        scale = (1.012, 1.025, 0.99)[level_index]
        ring_ids = []
        for x, y, _ in boundary_points:
            ring_ids.append(len(side_vertices))
            side_vertices.append((x * scale, y * scale, level))
        side_rings.append(ring_ids)
    side_faces, side_mats = [], []
    band_materials = [materials["cliff_a"], materials["cliff_b"], materials["cliff_c"]]
    for band in range(len(side_rings) - 1):
        upper, lower = side_rings[band], side_rings[band + 1]
        for i in range(segments):
            j = (i + 1) % segments
            side_faces.append((upper[i], lower[i], lower[j], upper[j]))
            side_mats.append(band)
    bottom_center = len(side_vertices)
    side_vertices.append((0.0, 0.0, levels[-1]))
    bottom_ring = side_rings[-1]
    side_faces.append(tuple([bottom_center] + list(reversed(bottom_ring))))
    side_mats.append(2)
    mesh_object(collection, "Terrain | Strata and cliff edge", side_vertices, side_faces, band_materials, side_mats)
    return top


def build_mountain_ridge(config, surface, collection, materials):
    """Build connected faceted ridges; KayKit mountain props stay as flank detail."""
    configs = config.get("mountainRidges")
    if configs is None:
        configs = [config.get("mountainRidge")]
    output = []
    lateral_steps = [-1.0, -0.76, -0.50, -0.24, 0.0, 0.22, 0.48, 0.75, 1.0]
    profile = [0.02, 0.20, 0.43, 0.74, 1.0, 0.81, 0.49, 0.22, 0.02]
    rock_materials = [materials["mountain_shadow"], materials["mountain_rock"], materials["mountain_warm"], materials["mountain_light"]]
    for ridge_index, cfg in enumerate(item for item in configs if item):
        spine = catmull_rom(cfg["spineControlPoints"], int(cfg.get("segmentsPerSpan", 8)))
        rng = random.Random(config["seed"] + 621 + ridge_index * 97)
        vertices = []
        for index, point in enumerate(spine):
            before, after = spine[max(0, index - 1)], spine[min(len(spine) - 1, index + 1)]
            tangent = (after - before).normalized()
            normal = Vector((-tangent.y, tangent.x))
            t = index / max(1, len(spine) - 1)
            peak_profile = max(
                peak["amplitude"] * math.exp(-0.5 * ((t - peak["position"]) / peak["spread"]) ** 2)
                for peak in cfg["peaks"]
            )
            peak_profile = 0.26 + 0.74 * peak_profile
            end_taper = max(0.0, float(cfg.get("endTaper", 0.0)))
            if end_taper:
                fade = min(1.0, t / end_taper, (1.0 - t) / end_taper)
                fade = fade * fade * (3.0 - 2.0 * fade)
            else:
                fade = 1.0
            for row, lateral in enumerate(lateral_steps):
                jitter = 0.0 if row in (0, len(lateral_steps) - 1) else rng.uniform(-0.18, 0.18)
                along_jitter = 0.0 if row in (0, len(lateral_steps) - 1, 4) else rng.uniform(-0.12, 0.12)
                offset = lateral * cfg["width"] * 0.5 + jitter
                x = point.x + normal.x * offset + tangent.x * along_jitter
                y = point.y + normal.y * offset + tangent.y * along_jitter
                footing = surface.height(x, y)
                height_fraction = profile[row]
                roughness = rng.uniform(-0.12, 0.12) * height_fraction
                z = footing + (cfg["height"] * peak_profile * height_fraction + roughness) * fade
                vertices.append((x, y, z))

        faces, indices = [], []
        for station in range(len(spine) - 1):
            for row in range(len(lateral_steps) - 1):
                a = station * len(lateral_steps) + row
                b = (station + 1) * len(lateral_steps) + row
                cells = ((a, b, b + 1), (a, b + 1, a + 1)) if (station + row) % 2 == 0 else ((a, b, a + 1), (b, b + 1, a + 1))
                for face in cells:
                    faces.append(face)
                    outer_face = row in (0, 1, 6, 7)
                    if outer_face:
                        indices.append(0 if (station + row) % 3 else 1)
                    elif row in (2, 5):
                        indices.append(1 if (station + row) % 2 else 2)
                    else:
                        indices.append(2 if (station + row) % 3 else 3)
        ridge_name = cfg.get("name", f"Crown Ridge {ridge_index + 1}")
        ridge = mesh_object(collection, f"Mountain | {ridge_name} | Connected faceted massif", vertices, faces, rock_materials, indices)
        ridge["construction"] = "Connected irregular spine mesh with exposed low-poly rock faces and terrain-matched foothills."
        ridge["reusable_component"] = "crown-ridge-v1"
        output.append(ridge)
    return output


def build_sea(collection, sea_material, z):
    vertices = [(-100.0, -100.0, z), (100.0, -100.0, z), (100.0, 100.0, z), (-100.0, 100.0, z)]
    mesh_object(collection, "Sea | Surrounding water", vertices, [(0, 1, 2, 3)], [sea_material])


def build_river(surface, collection, river_material, edge_material):
    points = surface.river_path
    cross_steps = 6
    width = surface.river["width"]
    vertices = []
    for index, point in enumerate(points):
        before = points[max(0, index - 1)]
        after = points[min(len(points) - 1, index + 1)]
        tangent = (after - before).normalized()
        normal = Vector((-tangent.y, tangent.x))
        along = index / max(1, len(points) - 1) * 24.0
        for cross_index in range(cross_steps):
            fraction = cross_index / (cross_steps - 1) - 0.5
            offset = fraction * width
            x = point.x + normal.x * offset
            y = point.y + normal.y * offset
            z = surface.river_z(x, y, along) + 0.035 * math.sin(along + cross_index * 0.9)
            vertices.append((x, y, z))
    faces, indices = [], []
    for i in range(len(points) - 1):
        for j in range(cross_steps - 1):
            a = i * cross_steps + j
            b = (i + 1) * cross_steps + j
            faces.append((a, b, b + 1, a + 1))
            indices.append(1 if j in (0, cross_steps - 2) else 0)
    return mesh_object(collection, "RIVER_MAIN | Meandering water", vertices, faces, [river_material, edge_material], indices, smooth=True)


def ribbon_mesh(collection, name, samples, width, surface, mat, offset=0.0):
    vertices = []
    for index, point in enumerate(samples):
        before = samples[max(0, index - 1)]
        after = samples[min(len(samples) - 1, index + 1)]
        tangent = (after - before).normalized()
        normal = Vector((-tangent.y, tangent.x))
        for side in (-0.5, 0.5):
            x = point.x + normal.x * width * side
            y = point.y + normal.y * width * side
            vertices.append((x, y, surface.road_z(x, y) + offset))
    faces = []
    for i in range(len(samples) - 1):
        a = 2 * i
        b = 2 * (i + 1)
        faces.append((a, b, b + 1, a + 1))
    return mesh_object(collection, name, vertices, faces, [mat])


def bridge_route_gaps(config, route_samples):
    """Return route-distance intervals occupied by bridge decks."""
    cumulative = [0.0]
    for a, b in zip(route_samples, route_samples[1:]):
        cumulative.append(cumulative[-1] + (b - a).length)
    gaps = []
    for bridge in bridge_specs(config):
        _, closest, _, index = nearest_path(bridge["center"], route_samples)
        a, b = route_samples[index], route_samples[index + 1]
        span = b - a
        fraction = 0.0 if span.length_squared < 1e-9 else max(0.0, min(1.0, (closest - a).dot(span) / span.length_squared))
        center_distance = cumulative[index] + span.length * fraction
        asset_dims = ASSET_INFO.get(bridge["asset"], {}).get("dimensions", [1.33, 1.92, 1.25])
        deck_length = asset_dims[1] * bridge["scale"]
        # Let the packed road run a short way onto each abutment so the deck
        # reads as a continuous crossing even where the curved route approaches.
        radius = max(0.0, deck_length * 0.5 - 0.34)
        gaps.append((max(0.0, center_distance - radius), min(cumulative[-1], center_distance + radius)))
    return gaps


def ribbon_mesh_with_gaps(collection, name, samples, width, surface, mat, gaps, offset=0.0):
    """Draw road ribbons in continuous runs, leaving the KayKit bridge decks visible."""
    cumulative = [0.0]
    for a, b in zip(samples, samples[1:]):
        cumulative.append(cumulative[-1] + (b - a).length)
    runs, run = [], []
    for point, distance in zip(samples, cumulative):
        inside_gap = any(start <= distance <= end for start, end in gaps)
        if inside_gap:
            if len(run) > 1:
                runs.append(run)
            run = []
        else:
            run.append(point)
    if len(run) > 1:
        runs.append(run)
    return [ribbon_mesh(collection, f"{name} | segment {i + 1:02d}", run, width, surface, mat, offset)
            for i, run in enumerate(runs)]


def make_route_curve(collection, samples, surface):
    curve = bpy.data.curves.new("ROUTE_MAIN", type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 1
    spline = curve.splines.new("POLY")
    spline.points.add(len(samples) - 1)
    for sample, point in zip(spline.points, samples):
        sample.co = (point.x, point.y, surface.road_z(point.x, point.y) + 0.07, 1.0)
    obj = bpy.data.objects.new("ROUTE_MAIN", curve)
    collection.objects.link(obj)
    obj.hide_render = True
    obj.display_type = "WIRE"
    obj["authority"] = "Primary traversable route; sampled to route.json."
    return obj


def inside_field(x, y, field, margin=0.0):
    dx, dy = x - field["center"][0], y - field["center"][1]
    angle = math.radians(field["angleDegrees"])
    lx = dx * math.cos(angle) + dy * math.sin(angle)
    ly = -dx * math.sin(angle) + dy * math.cos(angle)
    return abs(lx) <= field["size"][0] * 0.5 + margin and abs(ly) <= field["size"][1] * 0.5 + margin


def transformed_xy(cx, cy, x, y, angle):
    co, si = math.cos(angle), math.sin(angle)
    return (cx + x * co - y * si, cy + x * si + y * co)


def build_field(field, index, surface, collection, materials, assets):
    cx, cy = field["center"]
    width, depth = field["size"]
    angle = math.radians(field["angleDegrees"])
    local = [(-width / 2, -depth / 2), (width / 2, -depth / 2), (width / 2, depth / 2), (-width / 2, depth / 2)]
    vertices = []
    for x, y in local:
        wx, wy = transformed_xy(cx, cy, x, y, angle)
        vertices.append((wx, wy, surface.height(wx, wy) + 0.035))
    mesh_object(collection, f"Field {index:02d} | Cultivated earth", vertices, [(0, 1, 2, 3)], [materials["field_soil"]])

    row_count = max(8, int(width / 0.21))
    strip_width = width - 0.28
    for row in range(row_count):
        ly = -depth * 0.42 + row * (depth * 0.84 / max(1, row_count - 1))
        points = []
        for lx in (-strip_width / 2, strip_width / 2):
            wx, wy = transformed_xy(cx, cy, lx, ly, angle)
            points.append((wx, wy, surface.height(wx, wy) + 0.075))
        dx, dy = points[1][0] - points[0][0], points[1][1] - points[0][1]
        length = math.hypot(dx, dy)
        nx, ny = -dy / length * 0.035, dx / length * 0.035
        row_vertices = [
            (points[0][0] - nx, points[0][1] - ny, points[0][2]),
            (points[1][0] - nx, points[1][1] - ny, points[1][2]),
            (points[1][0] + nx, points[1][1] + ny, points[1][2]),
            (points[0][0] + nx, points[0][1] + ny, points[0][2]),
        ]
        crop_mat = materials["crop_a"] if row % 3 else materials["crop_b"]
        mesh_object(collection, f"Field {index:02d} | Wheat row {row + 1:02d}", row_vertices, [(0, 1, 2, 3)], [crop_mat])

    grain_source = "buildings/neutral/building_grain.gltf"
    for j, offset in enumerate(((-width * 0.35, -depth * 0.34), (width * 0.34, depth * 0.30), (0.1, depth * 0.37))):
        gx, gy = transformed_xy(cx, cy, offset[0], offset[1], angle)
        place_instance(collection, assets[grain_source], f"Grain {index:02d}-{j + 1}", gx, gy, surface.height(gx, gy) + 0.05, 0.42, random.uniform(-0.25, 0.25))


def build_courtyard(item, surface, collection, mat):
    cx, cy = item["center"]
    width, depth = item["size"]
    angle = math.radians(item.get("angleDegrees", 0.0))
    corners = [(-0.42, -0.5), (0.42, -0.5), (0.5, -0.28), (0.5, 0.28), (0.42, 0.5), (-0.42, 0.5), (-0.5, 0.28), (-0.5, -0.28)]
    vertices = [(cx, cy, surface.height(cx, cy) + 0.10)]
    for u, v in corners:
        x, y = transformed_xy(cx, cy, u * width, v * depth, angle)
        vertices.append((x, y, surface.height(x, y) + 0.10))
    faces = [(0, i + 1, ((i + 1) % len(corners)) + 1) for i in range(len(corners))]
    mesh_object(collection, f"Forecourt | {item['name']}", vertices, faces, [mat])


def place_instance(collection, asset_collection, name, x, y, z, scale=1.0, rotation=0.0):
    instance = bpy.data.objects.new(name, None)
    instance.instance_type = "COLLECTION"
    instance.instance_collection = asset_collection
    instance.empty_display_type = "PLAIN_AXES"
    instance.location = (float(x), float(y), float(z))
    instance.rotation_euler = (0.0, 0.0, float(rotation))
    instance.scale = (float(scale), float(scale), float(scale))
    collection.objects.link(instance)
    return instance


def point_near_building(x, y, buildings, clearance=1.15):
    return any(math.hypot(x - bx, y - by) < clearance for bx, by in buildings)


def place_buildings(config, assets, surface, collection):
    footprints = []
    for index, building in enumerate(config["buildings"], start=1):
        x, y = building["position"]
        z = surface.height(x, y) + 0.015
        place_instance(collection, assets[building["asset"]], f"{building['district']} | {slug(building['asset'])} {index:02d}", x, y, z, building.get("scale", 1.0), math.radians(building.get("rotationDegrees", 0.0)))
        footprints.append((x, y))
    castle = config["castle"]
    x, y = castle["position"]
    place_instance(collection, assets[castle["asset"]], "Crownfall Castle | Keep", x, y, surface.height(x, y) + 0.02, castle["scale"], math.radians(castle["rotationDegrees"]))
    footprints.append((x, y))
    return footprints


def building_footprint_checks(config, surface, route_samples):
    checks = []
    for building in config["buildings"]:
        asset = ASSET_INFO.get(building["asset"], {})
        dimensions = asset.get("dimensions", [1.0, 1.0, 1.0])
        scale = float(building.get("scale", 1.0))
        angle = math.radians(building.get("rotationDegrees", 0.0))
        cx, cy = building["position"]
        min_water, min_route = float("inf"), float("inf")
        # Sample the actual rotated asset footprint rather than only its origin.
        for ix in range(7):
            for iy in range(7):
                lx = ((ix / 6.0) - 0.5) * dimensions[0] * scale
                ly = ((iy / 6.0) - 0.5) * dimensions[1] * scale
                x, y = transformed_xy(cx, cy, lx, ly, angle)
                min_water = min(min_water, surface.river_distance(x, y) - surface.river["width"] * 0.5)
                min_route = min(min_route, nearest_path((x, y), route_samples)[0] - config["road"]["width"] * 0.5)
        checks.append({
            "asset": pathlib.PurePosixPath(building["asset"]).name,
            "district": building["district"],
            "position": building["position"],
            "minimumWaterClearance": round(min_water, 3),
            "minimumRouteClearance": round(min_route, 3),
            "dryFootprint": min_water >= 0.15,
            "clearOfRoute": min_route >= 0.15,
        })
    return checks


def place_district_props(config, assets, surface, route_samples, collection):
    """Add small KayKit trade and craft props to settlement edges and yards."""
    placed = []
    buildings = config["buildings"]
    all_centers = [item["position"] for item in buildings] + [config["castle"]["position"]]
    for index, building in enumerate(buildings):
        source = building["asset"]
        if not any(word in source for word in ("market", "tavern", "blacksmith", "mill", "windmill")):
            continue
        props = ["decoration/props/crate_A_big.gltf", "decoration/props/barrel.gltf"]
        if "mill" in source or "blacksmith" in source:
            props[0] = "decoration/props/resource_lumber.gltf" if "mill" in source else "decoration/props/resource_stone.gltf"
        cx, cy = building["position"]
        for prop_index, prop in enumerate(props):
            best = None
            seed_angle = (index * 2.399963 + prop_index * 1.5708) % math.tau
            for radius in (0.85, 1.05, 1.25, 1.45):
                for turn in range(16):
                    angle = seed_angle + turn * math.tau / 16.0
                    x, y = cx + math.cos(angle) * radius, cy + math.sin(angle) * radius
                    if surface.river_distance(x, y) < surface.river["width"] * 0.5 + 0.2:
                        continue
                    if nearest_path((x, y), route_samples)[0] < config["road"]["width"] * 0.5 + 0.28:
                        continue
                    if point_near_building(x, y, all_centers, 0.9):
                        continue
                    best = (x, y, angle)
                    break
                if best:
                    break
            if not best:
                continue
            x, y, angle = best
            scale = 2.25 if prop.endswith("barrel.gltf") else 1.9
            place_instance(collection, assets[prop], f"{building['district']} | Trade detail {index + 1:02d}-{prop_index + 1}", x, y, surface.height(x, y) + 0.015, scale, angle)
            placed.append((x, y))
    return placed


def place_forest_groups(config, assets, surface, route_samples, fields, collection):
    rng = random.Random(config["seed"])
    placed, requested, warnings = [], 0, []
    buildings = [item["position"] for item in config["buildings"]] + [config["castle"]["position"]]
    for group in config["forestGroups"]:
        requested += group["count"]
        cx, cy = group["center"]
        rx, ry = group["radius"]
        count, attempts = 0, 0
        while count < group["count"] and attempts < group["count"] * 80:
            attempts += 1
            angle = rng.random() * math.tau
            radius = math.sqrt(rng.random())
            x, y = cx + math.cos(angle) * rx * radius, cy + math.sin(angle) * ry * radius
            if math.sqrt((x / surface.terrain["radiusX"]) ** 2 + (y / surface.terrain["radiusY"]) ** 2) > 0.95:
                continue
            if nearest_path((x, y), route_samples)[0] < group["routeClearance"]:
                continue
            if surface.river_distance(x, y) < surface.river["width"] * 0.5 + group["riverClearance"]:
                continue
            if surface.height(x, y) > 2.7 or point_near_building(x, y, buildings, 1.5):
                continue
            if point_near_building(x, y, placed, group.get("assetSpacing", 1.15)):
                continue
            if any(inside_field(x, y, field, 0.4) for field in fields):
                continue
            source = rng.choice(group["variants"])
            scale = rng.uniform(*group["scale"])
            rotation = rng.random() * math.tau
            place_instance(collection, assets[source], f"{group['name']} | Tree {count + 1:02d}", x, y, surface.height(x, y) + 0.015, scale, rotation)
            placed.append((x, y))
            count += 1
        if count != group["count"]:
            warnings.append(f"{group['name']}: placed {count}/{group['count']} trees after clearance checks")
    return placed, requested, warnings


def place_rock_groups(config, assets, surface, route_samples, collection):
    rng = random.Random(config["seed"] + 891)
    placed, requested, warnings = [], 0, []
    for group in config["rockGroups"]:
        requested += group["count"]
        cx, cy = group["center"]
        rx, ry = group["radius"]
        count, attempts = 0, 0
        while count < group["count"] and attempts < group["count"] * 100:
            attempts += 1
            angle = rng.random() * math.tau
            radius = math.sqrt(rng.random())
            x, y = cx + math.cos(angle) * rx * radius, cy + math.sin(angle) * ry * radius
            if nearest_path((x, y), route_samples)[0] < group["routeClearance"]:
                continue
            if surface.height(x, y) < 1.5 or point_near_building(x, y, placed, group.get("assetSpacing", 1.8)):
                continue
            source = rng.choice(group["variants"])
            scale = rng.uniform(*group["scale"])
            rotation = rng.random() * math.tau
            place_instance(collection, assets[source], f"{group['name']} | Crag {count + 1:02d}", x, y, surface.height(x, y) - 0.04, scale, rotation)
            placed.append((x, y))
            count += 1
        if count != group["count"]:
            warnings.append(f"{group['name']}: placed {count}/{group['count']} crags after clearance checks")
    return placed, requested, warnings


def make_bridge(config, assets, surface, collection, route_samples):
    reports = []
    objects = []
    for bridge in bridge_specs(config):
        x, y = bridge["center"]
        distance, _, river_tangent, _ = nearest_path((x, y), surface.river_path)
        _, _, road_tangent, _ = nearest_path((x, y), route_samples)
        # The bridge asset's long local Y axis spans the river. Set it to the
        # route tangent so the deck, road approaches and player path agree.
        road_angle = math.atan2(road_tangent.y, road_tangent.x)
        rotation = road_angle - math.pi / 2.0
        water_z = surface.river_z(x, y)
        deck_z = water_z + bridge["deckOffset"]
        origin_z = deck_z - bridge["deckLocalZ"] * bridge["scale"]
        obj = place_instance(
            collection,
            assets[bridge["asset"]],
            f"{bridge['name']} | KayKit stone bridge",
            x, y, origin_z, bridge["scale"], rotation,
        )
        objects.append(obj)
        river_angle = math.atan2(river_tangent.y, river_tangent.x)
        cross_angle = math.atan2(math.sin(road_angle - (river_angle + math.pi / 2)), math.cos(road_angle - (river_angle + math.pi / 2)))
        cross_error = abs(math.degrees(cross_angle))
        cross_error = min(cross_error, abs(180.0 - cross_error))
        deck_axis_error = abs(math.degrees(math.atan2(math.sin((rotation + math.pi / 2.0) - road_angle), math.cos((rotation + math.pi / 2.0) - road_angle))))
        dims = ASSET_INFO.get(bridge["asset"], {}).get("dimensions", [1.33, 1.92, 1.25])
        deck_length, deck_width = dims[1] * bridge["scale"], dims[0] * bridge["scale"]
        reports.append({
            "name": bridge["name"],
            "center": [x, y, deck_z],
            "waterSurfaceZ": water_z,
            "deckZ": deck_z,
            "riverCenterlineError": distance,
            "roadRiverCrossingAngleErrorDegrees": cross_error,
            "deckRoadAlignmentErrorDegrees": deck_axis_error,
            "deckLength": round(deck_length, 3),
            "deckWidth": round(deck_width, 3),
            "roadGapLength": round(max(0.0, deck_length - 0.16), 3),
            "rotationDegrees": math.degrees(rotation),
        })
    first = reports[0]
    report = dict(first)
    report["bridges"] = reports
    report["riverCenterlineError"] = max(item["riverCenterlineError"] for item in reports)
    report["roadRiverCrossingAngleErrorDegrees"] = max(item["roadRiverCrossingAngleErrorDegrees"] for item in reports)
    return objects, report


def place_shore_structures(config, assets, surface, collection):
    placed = []
    for item in config.get("shoreStructures", []):
        x, y = item["position"]
        scale = item.get("scale", 1.8)
        # Start the landing at the dry bank's height so its deck joins land
        # instead of floating below the foreshore.
        deck_z = max(surface.height(x, y), surface.terrain["seaLevel"]) + item.get("deckOffset", 0.32)
        local_z = item.get("deckLocalZ", 0.20)
        origin_z = deck_z - local_z * scale
        obj = place_instance(
            collection,
            assets[item["asset"]],
            f"{item.get('name', 'Shore Landing')} | KayKit timber landing",
            x, y, origin_z, scale, math.radians(item.get("rotationDegrees", 0.0)),
        )
        placed.append(obj)
    return placed


def look_at(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()


def configure_camera_and_lights(scene, config, collection, width, height):
    camera_cfg = config["camera"]
    camera_data = bpy.data.cameras.new("Board Camera | Orthographic")
    camera = bpy.data.objects.new("Board Camera | Orthographic", camera_data)
    collection.objects.link(camera)
    camera.location = camera_cfg["location"]
    look_at(camera, camera_cfg["target"])
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = camera_cfg["orthographicScale"]
    camera_data.clip_start = camera_cfg["clipStart"]
    camera_data.clip_end = camera_cfg["clipEnd"]
    scene.camera = camera
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.view_transform = "AgX"
    look_items = {item.identifier for item in scene.view_settings.bl_rna.properties["look"].enum_items}
    if "AgX - Medium High Contrast" in look_items:
        scene.view_settings.look = "AgX - Medium High Contrast"
    else:
        scene.view_settings.look = "Medium High Contrast" if "Medium High Contrast" in look_items else scene.view_settings.look
    scene.view_settings.exposure = 0.32

    world = bpy.data.worlds.new("Crownfall | Cloudlit sky")
    world.use_nodes = True
    world.node_tree.nodes.get("Background").inputs["Color"].default_value = (*config["lighting"]["worldColor"], 1.0)
    world.node_tree.nodes.get("Background").inputs["Strength"].default_value = config["lighting"]["worldStrength"]
    scene.world = world

    def add_area(key, title):
        light_cfg = config["lighting"][key]
        data = bpy.data.lights.new(f"{title} | Area", type="AREA")
        data.energy = light_cfg["energy"]
        data.shape = "DISK"
        data.size = light_cfg["size"]
        data.color = light_cfg["color"]
        if hasattr(data, "use_shadow"):
            data.use_shadow = True
        if hasattr(data, "use_contact_shadow"):
            data.use_contact_shadow = True
        obj = bpy.data.objects.new(f"{title} | Area", data)
        collection.objects.link(obj)
        obj.location = light_cfg["location"]
        look_at(obj, (0.0, 0.0, 0.0))

    add_area("key", "Key | Late afternoon")
    add_area("fill", "Fill | Cool sky")
    add_area("rim", "Rim | Warm horizon")
    return camera


def convert_depth_exr(exr_path, depth_path, width, height):
    venv_python = PROJECT_ROOT / (".venv/Scripts/python.exe" if sys.platform == "win32" else ".venv/bin/python")
    if not venv_python.exists():
        raise FileNotFoundError(f"Project virtual environment not found: {venv_python}")
    converter = PROJECT_ROOT / "tools/blender/depth_from_exr.py"
    result = subprocess.run(
        [str(venv_python), str(converter), "--input", str(exr_path), "--output", str(depth_path),
         "--width", str(width), "--height", str(height)],
        capture_output=True, text=True,
    )
    if result.returncode:
        raise RuntimeError("Depth conversion failed:\n" + result.stdout + result.stderr)
    return json.loads(result.stdout)


def make_route_records(samples, surface, scene, camera, width, height):
    bpy.context.view_layer.update()
    inverse = camera.matrix_world.inverted()
    records = []
    cumulative = 0.0
    previous = None
    for point in samples:
        z = surface.road_z(point.x, point.y) + 0.07
        world = Vector((point.x, point.y, z))
        if previous is not None:
            cumulative += (world - previous).length
        coord = world_to_camera_view(scene, camera, world)
        screen_x = coord.x * width
        screen_y = (1.0 - coord.y) * height
        camera_local = inverse @ world
        runtime_depth = DEPTH_OFFSET + camera_local.z
        records.append([cumulative, world.x, world.z, world.y, screen_x, screen_y, runtime_depth])
        previous = world
    return records


def route_at(records, distance):
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
    return [a[i] + (b[i] - a[i]) * t for i in range(1, len(a))]


def minimum_stop_gap(records, movement_steps):
    length = records[-1][0]
    stops = [route_at(records, length * i / movement_steps) for i in range(movement_steps + 1)]
    gaps = [math.hypot(a[3] - b[3], a[4] - b[4]) for i, a in enumerate(stops) for b in stops[i + 1:]]
    return min(gaps) if gaps else 0.0


def segments_intersect(a, b, c, d):
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
    return o1 * o2 < -1e-8 and o3 * o4 < -1e-8


def route_self_intersections(samples):
    segments = [(tuple(a), tuple(b)) for a, b in zip(samples, samples[1:])]
    intersections = []
    for i, (a, b) in enumerate(segments):
        for j in range(i + 3, len(segments)):
            c, d = segments[j]
            if segments_intersect(a, b, c, d):
                intersections.append([i, j])
    return intersections


def configure_depth_compositor(scene, output_dir):
    scene.view_layers[0].use_pass_z = True
    if hasattr(scene, "compositing_node_group"):
        # Blender 5.0+ stores the compositor in a reusable node-group datablock.
        tree = bpy.data.node_groups.new("Quest | Render and depth export", "CompositorNodeTree")
        scene.compositing_node_group = tree
        scene.render.use_compositing = True
    else:
        scene.use_nodes = True
        tree = scene.node_tree
    tree.nodes.clear()
    render_node = tree.nodes.new("CompositorNodeRLayers")
    if hasattr(render_node, "scene"):
        render_node.scene = scene
        render_node.layer = scene.view_layers[0].name
        render_node.update()
    render_node.location = (0, 80)
    depth_output = tree.nodes.new("CompositorNodeOutputFile")
    depth_output.name = "Quest Depth Export | Temporary OpenEXR"
    depth_output.location = (300, -80)
    if hasattr(depth_output, "file_output_items"):
        depth_output.file_output_items.new("FLOAT", "Depth")
        depth_output.directory = str((output_dir / "depth-pass").resolve())
        depth_output.file_name = "quest-depth-"
    else:
        depth_output.base_path = str((output_dir / "depth-pass").resolve())
        depth_output.file_slots[0].path = "quest-depth-"
    depth_output.format.file_format = "OPEN_EXR_MULTILAYER" if hasattr(depth_output, "file_output_items") else "OPEN_EXR"
    depth_output.format.color_mode = "RGB" if hasattr(depth_output, "file_output_items") else "BW"
    depth_output.format.color_depth = "32"
    depth_output.format.exr_codec = "ZIP"
    z_socket = render_node.outputs.get("Depth") or render_node.outputs.get("Z")
    if z_socket is None:
        raise RuntimeError("Blender render layer does not expose its Z pass")
    depth_input = depth_output.inputs.get("Depth") or depth_output.inputs[0]
    tree.links.new(z_socket, depth_input)
    if hasattr(tree, "interface"):
        output = tree.nodes.new("NodeGroupOutput")
        tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        tree.links.new(output.inputs["Image"], render_node.outputs["Image"])
    else:
        composite = tree.nodes.new("CompositorNodeComposite")
        composite.location = (300, 160)
        tree.links.new(render_node.outputs["Image"], composite.inputs["Image"])
    return depth_output


def render_outputs(scene, camera, output_dir, width, height, samples):
    output_dir.mkdir(parents=True, exist_ok=True)
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.filepath = str((output_dir / "background.png").resolve())
    scene.camera = camera
    scene.render.use_file_extension = True
    configure_depth_compositor(scene, output_dir)
    if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = samples
    bpy.ops.render.render(write_still=True)
    background_path = output_dir / "background.png"
    if not background_path.exists():
        candidate = output_dir / "background.png0001.png"
        if candidate.exists():
            candidate.rename(background_path)
    depth_folder = output_dir / "depth-pass"
    exr_files = sorted(depth_folder.glob("*.exr")) if depth_folder.exists() else []
    if not exr_files:
        raise RuntimeError(f"Blender did not write an EXR depth pass under {depth_folder}")
    depth_path = output_dir / "depth.png"
    depth_report = convert_depth_exr(exr_files[-1], depth_path, width, height)
    for exr_path in exr_files:
        exr_path.unlink()
    depth_folder.rmdir()
    return background_path, depth_path, depth_report


def field_checks(config, surface, route_samples):
    checks = []
    for field in config["fields"]:
        river_min = float("inf")
        route_min = float("inf")
        for ix in range(13):
            for iy in range(9):
                lx = (ix / 12 - 0.5) * field["size"][0]
                ly = (iy / 8 - 0.5) * field["size"][1]
                x, y = transformed_xy(field["center"][0], field["center"][1], lx, ly, math.radians(field["angleDegrees"]))
                river_min = min(river_min, surface.river_distance(x, y))
                route_min = min(route_min, nearest_path((x, y), route_samples)[0])
        water_clearance = river_min - surface.river["width"] * 0.5
        road_clearance = route_min - config["road"]["width"] * 0.5
        checks.append({
            "name": field["name"],
            "minimumWaterClearance": water_clearance,
            "minimumRoadClearance": road_clearance,
            "clearOfRiver": water_clearance > 0.2,
            "clearOfRoad": road_clearance > 0.2,
        })
    return checks


def camera_frame_report(scene, camera, width, height):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    bounds = []
    for evaluated in depsgraph.object_instances:
        obj = evaluated.instance_object if evaluated.is_instance else evaluated.object
        if obj is None or obj.type not in {"MESH", "CURVE"} or obj.name.startswith("Sea | Surrounding water"):
            continue
        matrix = evaluated.matrix_world
        if obj.type == "MESH":
            points = (matrix @ vertex.co for vertex in obj.data.vertices)
        else:
            points = (matrix @ Vector(point.co[:3]) for spline in obj.data.splines for point in spline.points)
        for world in points:
            coord = world_to_camera_view(scene, camera, world)
            bounds.append((coord.x * width, (1.0 - coord.y) * height, obj.name))
    if not bounds:
        return {"geometryObjectsMeasured": 0, "allVisibleWithinFrame": False, "minimumMarginPx": None, "edgeObjects": []}
    min_x, max_x = min(item[0] for item in bounds), max(item[0] for item in bounds)
    min_y, max_y = min(item[1] for item in bounds), max(item[1] for item in bounds)
    margin = min(min_x, min_y, width - max_x, height - max_y)
    edge_objects = sorted({name for x, y, name in bounds if x < 12 or y < 12 or x > width - 12 or y > height - 12})
    return {
        "geometryObjectsMeasured": len(set(item[2] for item in bounds)),
        "pixelBounds": [round(min_x, 2), round(min_y, 2), round(max_x, 2), round(max_y, 2)],
        "minimumMarginPx": round(margin, 2),
        "allVisibleWithinFrame": margin >= 0.0,
        "edgeObjects": edge_objects,
    }


def build_report(config, route_samples, route_records, bridge_report, field_report, building_report, frame_report, forest_count, rock_count, placement_warnings, width, height):
    length = route_records[-1][0]
    final_pixel_scale = config["render"]["finalResolution"][0] / width
    stops = {str(movement): minimum_stop_gap(route_records, movement) * final_pixel_scale for movement in (30, 40, 50, 60)}
    self_crossings = route_self_intersections(route_samples)
    in_frame = all(0 <= record[4] <= width and 0 <= record[5] <= height for record in route_records)
    in_frame = in_frame and frame_report["allVisibleWithinFrame"]
    river_crossing_ok = bridge_report["riverCenterlineError"] < 0.25 and bridge_report["roadRiverCrossingAngleErrorDegrees"] < 28 and all(item["deckRoadAlignmentErrorDegrees"] < 8 for item in bridge_report["bridges"])
    field_clear = all(item["clearOfRiver"] and item["clearOfRoad"] for item in field_report)
    buildings_clear = all(item["dryFootprint"] and item["clearOfRoute"] for item in building_report)
    route_cells = len(config["road"]["controlPoints"])
    route_steps = config["capacity"]["supportedMovementSteps"]
    candidate_steps = []
    for movement in config["capacity"].get("candidateMovementSteps", []):
        if stops[str(movement)] >= 26.0:
            candidate_steps.append(movement)
    supported_gaps = {str(n): stops[str(n)] for n in route_steps}
    supported_clear = all(gap >= 26.0 for gap in supported_gaps.values())
    grade_max = 0.0
    for a, b in zip(route_records, route_records[1:]):
        horiz = math.hypot(b[1] - a[1], b[3] - a[3])
        grade_max = max(grade_max, abs(b[2] - a[2]) / max(0.001, horiz))
    issues = []
    if self_crossings:
        issues.append(f"Road has {len(self_crossings)} self-intersection(s)")
    if not river_crossing_ok:
        issues.append("Bridge centerline/alignment needs review")
    if not field_clear:
        issues.append("One or more fields overlap the road or river")
    if not buildings_clear:
        issues.append("One or more building footprints overlap the road or river")
    if not in_frame:
        issues.append("Map geometry or route samples fall outside the camera frame")
    if not supported_clear:
        issues.append("One or more configured stop capacities have under 26 px pairwise spacing")
    return {
        "status": "PASS" if not issues else "REVIEW_REQUIRED",
        "map": config["id"],
        "name": config["name"],
        "qualityResolution": [width, height],
        "roadRouteLength": round(length, 3),
        "routeSampleCount": len(route_records),
        "routeSelfIntersections": self_crossings,
        "routeWithinFrame": in_frame,
        "cameraFrame": frame_report,
        "stopSpacingReferenceResolution": config["render"]["finalResolution"],
        "maxSampledGrade": round(grade_max, 4),
        "bridge": bridge_report,
        "fields": field_report,
        "buildings": building_report,
        "buildingFootprintsClear": buildings_clear,
        "forestsPlaced": forest_count,
        "rockGroupsPlaced": rock_count,
        "minimumAllPairStopSpacingPx": {key: round(value, 2) for key, value in stops.items()},
        "supportedMovementSteps": sorted(set(route_steps).union(candidate_steps)) if supported_clear else [],
        "candidateMovementStepsPromoted": candidate_steps,
        "placementWarnings": placement_warnings,
        "issues": issues,
    }


def main():
    args = parse_args()
    config_path = args.config.resolve()
    config = read_json(config_path)
    map_root = config_path.parent
    output_dir = (args.output_dir or map_root / "output").resolve()
    report_dir = (map_root / "reports").resolve()
    blend_path = (args.output_blend or map_root / "source" / f"{config['id']}.blend").resolve()
    blend_path.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    resolutions = {
        "draft": config["render"]["draftResolution"],
        "review": config["render"]["reviewResolution"],
        "final": config["render"]["finalResolution"],
    }
    width, height = resolutions[args.quality]
    sources = assets_needed(config)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = f"{config['name']} | {config['subtitle']}"
    engine_ids = {item.identifier for item in scene.render.bl_rna.properties["engine"].enum_items}
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engine_ids else "BLENDER_EEVEE"

    collections = {
        "terrain": new_collection(scene, "01 | Terrain and coast"),
        "river": new_collection(scene, "02 | River and bridge"),
        "roads": new_collection(scene, "03 | ROUTE_MAIN and roads"),
        "architecture": new_collection(scene, "04 | Settlements and landmarks"),
        "vegetation": new_collection(scene, "05 | Forest and mountain assets"),
        "fields": new_collection(scene, "06 | Agriculture"),
        "camera": new_collection(scene, "07 | Camera and lighting"),
        "guides": new_collection(scene, "08 | Authoring guides"),
    }
    materials = make_materials()
    river_path = catmull_rom(config["river"]["controlPoints"], 12)
    route_samples = catmull_rom(config["road"]["controlPoints"], 24)
    surface = MapSurface(config, river_path)
    assets = link_asset_collections(sources)

    build_sea(collections["terrain"], materials["sea"], config["terrain"]["seaLevel"])
    build_island(surface, collections["terrain"], materials)
    ridges = build_mountain_ridge(config, surface, collections["terrain"], materials)
    build_river(surface, collections["river"], materials["river"], materials["river_edge"])
    road_gaps = bridge_route_gaps(config, route_samples)
    ribbon_mesh_with_gaps(collections["roads"], "Road edge | Packed-earth shoulder", route_samples, config["road"]["edgeWidth"], surface, materials["road_edge"], road_gaps, 0.015)
    ribbon_mesh_with_gaps(collections["roads"], "ROAD_MAIN | Meandering road and exposed bridges", route_samples, config["road"]["width"], surface, materials["road"], road_gaps, 0.055)
    for lane in config.get("districtLanes", []):
        lane_samples = catmull_rom(lane["controlPoints"], 16)
        ribbon_mesh(collections["roads"], f"Lane shoulder | {lane['name']}", lane_samples, lane.get("width", 0.62) + 0.22, surface, materials["road_edge"], 0.035)
        ribbon_mesh(collections["roads"], f"Lane | {lane['name']}", lane_samples, lane.get("width", 0.62), surface, materials["lane"], 0.075)
    make_route_curve(collections["guides"], route_samples, surface)

    for courtyard in config.get("courtyards", []):
        build_courtyard(courtyard, surface, collections["architecture"], materials["court"])

    for index, field in enumerate(config["fields"], start=1):
        build_field(field, index, surface, collections["fields"], materials, assets)

    bridge_objects, bridge_report = make_bridge(config, assets, surface, collections["river"], route_samples)
    shore_objects = place_shore_structures(config, assets, surface, collections["river"])
    building_positions = place_buildings(config, assets, surface, collections["architecture"])
    forest_positions, forest_requested, forest_warnings = place_forest_groups(config, assets, surface, route_samples, config["fields"], collections["vegetation"])
    rock_positions, rock_requested, rock_warnings = place_rock_groups(config, assets, surface, route_samples, collections["vegetation"])
    district_prop_positions = place_district_props(config, assets, surface, route_samples, collections["architecture"])

    camera = configure_camera_and_lights(scene, config, collections["camera"], width, height)
    bpy.context.view_layer.update()
    background_path, depth_path, depth_report = render_outputs(scene, camera, output_dir, width, height, config["render"]["samples"])

    route_records = make_route_records(route_samples, surface, scene, camera, width, height)
    field_report = field_checks(config, surface, route_samples)
    frame_report = camera_frame_report(scene, camera, width, height)
    building_report = building_footprint_checks(config, surface, route_samples)
    placement_warnings = forest_warnings + rock_warnings
    report = build_report(config, route_samples, route_records, bridge_report, field_report, building_report, frame_report, len(forest_positions), len(rock_positions), placement_warnings, width, height)
    report["depth"] = depth_report
    report["shoreStructuresPlaced"] = len(shore_objects)
    report["districtPropsPlaced"] = len(district_prop_positions)
    report["assetSourceCount"] = len(sources)
    formations = [{
        "name": ridge.name,
        "connectedMesh": True,
        "vertices": len(ridge.data.vertices),
        "faces": len(ridge.data.polygons),
    } for ridge in ridges]
    report["mountainFormation"] = {
        "name": formations[0]["name"] if formations else None,
        "connectedMesh": bool(formations),
        "vertices": sum(item["vertices"] for item in formations),
        "faces": sum(item["faces"] for item in formations),
        "formations": formations,
    }

    # Route and camera metadata use the existing Quest runtime order:
    # [distance, worldX, worldElevation, worldY, pixelX, pixelY, cameraDepth].
    camera_direction = (Vector(config["camera"]["target"]) - Vector(config["camera"]["location"])).normalized()
    elevation = math.asin(max(-1.0, min(1.0, camera_direction.z)))
    projection = {
        "sin": math.sin(elevation),
        "cos": math.cos(elevation),
        "offset": 0,
        "cameraElevationDegrees": math.degrees(elevation),
        "pixelsPerWorldUnit": width / config["camera"]["orthographicScale"],
        "verticalScreenPixelsPerWorldUnit": width / config["camera"]["orthographicScale"] * math.cos(elevation),
        "verticalDepthPerWorldUnit": math.sin(elevation),
    }
    landmark_data = []
    for landmark in config["landmarks"]:
        x, y = landmark["position"]
        z = surface.height(x, y) + 0.08
        world = Vector((x, y, z))
        coord = world_to_camera_view(scene, camera, world)
        nearest = min(route_records, key=lambda row: (row[1] - x) ** 2 + (row[3] - y) ** 2)
        landmark_data.append({
            "name": landmark["name"], "kind": landmark["kind"],
            "world": [x, z, y],
            "screen": [coord.x * width, (1.0 - coord.y) * height],
            "routeDistance": nearest[0],
        })

    route_data = {
        "map": config["id"],
        "name": config["name"],
        "subtitle": config["subtitle"],
        "startLandmark": config.get("routeLabels", {}).get("start", config["landmarks"][0]["name"]),
        "finishLandmark": config.get("routeLabels", {}).get("finish", config["landmarks"][-1]["name"]),
        "width": width,
        "height": height,
        "projection": projection,
        "route": [[round(value, 5) for value in row] for row in route_records],
        "length": route_records[-1][0],
        "regions": {item["name"]: next((row[0] for row in route_records if math.hypot(row[1] - item["position"][0], row[3] - item["position"][1]) < 1.0), min(route_records, key=lambda row: math.hypot(row[1] - item["position"][0], row[3] - item["position"][1]))[0]) for item in config["landmarks"]},
        "glints": [],
        "tiles": 0,
        "routeCells": len(config["road"]["controlPoints"]),
        "unmatched": [],
        "bridge": {"x": bridge_report["center"][0], "y": bridge_report["center"][1], "deckZ": bridge_report["deckZ"]},
        "bridges": [
            {"name": item["name"], "x": item["center"][0], "y": item["center"][1], "deckZ": item["deckZ"]}
            for item in bridge_report["bridges"]
        ],
        "gate": {"x": config["castle"]["gate"][0], "y": surface.height(*config["castle"]["gate"]), "z": config["castle"]["gate"][1]},
        "defaultMovementSteps": config["capacity"]["defaultMovementSteps"],
        "defaultStopCount": config["capacity"]["defaultStopCount"],
        "supportedMovementSteps": report["supportedMovementSteps"],
        "candidateMovementStepsPromoted": report["candidateMovementStepsPromoted"],
        "minimumStopSpacingPx": report["minimumAllPairStopSpacingPx"],
    }
    camera_data = {
        "type": "ORTHOGRAPHIC",
        "resolution": [width, height],
        "cameraLocation": list(camera.location),
        "target": config["camera"]["target"],
        "orthographicScale": config["camera"]["orthographicScale"],
        "cameraWorldMatrix": [[round(float(camera.matrix_world[r][c]), 8) for c in range(4)] for r in range(4)],
        "depthConvention": depth_report["encoding"],
        "runtimeDepthFromBlenderZ": "128 - camera_distance; larger values are nearer",
        "runtimeWorldAxisOrder": ["x", "elevation_z", "y"],
        "projection": projection,
    }

    write_json(output_dir / "route.json", route_data)
    write_json(output_dir / "camera.json", camera_data)
    write_json(output_dir / "landmarks.json", {"map": config["id"], "landmarks": landmark_data})
    write_json(report_dir / "scene-validation.json", report)
    write_json(map_root / "map.json", {
        "id": config["id"], "name": config["name"], "subtitle": config["subtitle"], "defaultMovementSteps": config["capacity"]["defaultMovementSteps"],
        "defaultStopCount": config["capacity"]["defaultStopCount"], "supportedMovementSteps": route_data["supportedMovementSteps"],
        "candidateMovementStepsPromoted": route_data["candidateMovementStepsPromoted"], "background": "output/background.png",
        "depth": "output/depth.png", "route": "output/route.json", "camera": "output/camera.json", "landmarks": "output/landmarks.json",
        "assetLibrary": "../../assets/kaykit-medieval/library/kaykit-medieval.blend",
    })

    scene["map_id"] = config["id"]
    scene["scene_config"] = str(config_path)
    scene["route_object"] = "ROUTE_MAIN"
    scene["depth_encoding"] = depth_report["encoding"]
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    print(json.dumps({
        "status": report["status"], "blend": str(blend_path), "background": str(background_path), "depth": str(depth_path),
        "route": str(output_dir / "route.json"), "validation": str(report_dir / "scene-validation.json"),
        "routeLength": round(route_records[-1][0], 3), "routeSamples": len(route_records),
        "forestCount": len(forest_positions), "rockGroupCount": len(rock_positions), "assetSources": len(sources),
        "stopSpacing": report["minimumAllPairStopSpacingPx"], "issues": report["issues"], "placementWarnings": placement_warnings,
    }, indent=2))


if __name__ == "__main__":
    main()
