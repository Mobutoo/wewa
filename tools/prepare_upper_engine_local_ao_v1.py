"""QA derivative only. Run inside Blender 4.3.2; NEVER run automatically.

Two separate invocations: --phase prepare, then --phase bake. Each reserves a
new output subdirectory. A failed directory is evidence and is never reused.
No library, source review, material catalogue or game file is saved.
The committed tool is unexecuted; its existence is not a successful bake.
"""
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import traceback

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
UV_AO = "UV_AO"


class ConservationError(AssertionError):
    def __init__(self, message, diagnostic):
        super().__init__(message)
        self.diagnostic = diagnostic


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def array_digest(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def write_json(path, value):
    assert not path.exists(), f"Refusing overwrite: {path}"
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def repo_path(value):
    path = Path(value)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def read_array(collection, prop, width, dtype=np.float32):
    out = np.empty(len(collection) * width, dtype=dtype)
    collection.foreach_get(prop, out)
    return out.reshape((-1, width))


def material_signature(material):
    """Fingerprint original node settings/links, excluding editor selection."""
    def value(v):
        if isinstance(v, (str, int, float, bool)) or v is None:
            return v
        if hasattr(v, "name_full"):
            return [v.bl_rna.identifier, v.name_full]
        try:
            return list(v)
        except TypeError:
            return str(v)
    rows = []
    for node in material.node_tree.nodes:
        props = {}
        for prop in node.bl_rna.properties:
            key = prop.identifier
            if prop.is_readonly or key in {"rna_type", "select", "location", "dimensions"}:
                continue
            if prop.type in {"BOOLEAN", "INT", "FLOAT", "STRING", "ENUM", "POINTER"}:
                props[key] = value(getattr(node, key))
        rows.append({"type": node.bl_idname, "name": node.name, "props": props,
                     "inputs": [(s.identifier, value(getattr(s, "default_value", None)))
                                for s in node.inputs]})
    links = sorted((l.from_node.name, l.from_socket.identifier,
                    l.to_node.name, l.to_socket.identifier) for l in material.node_tree.links)
    return hashlib.sha256(json.dumps([rows, links], sort_keys=True).encode()).hexdigest()


def mesh_witness(obj, uv_names):
    """Raw topology and evaluated normals; UV/tangents remain corner data."""
    import bpy
    mesh = obj.data
    mesh.calc_loop_triangles()
    result = {"world": [list(r) for r in obj.matrix_world],
              "basis": [list(r) for r in obj.matrix_basis],
              "parent": obj.parent.name if obj.parent else None,
              "position": array_digest(read_array(mesh.vertices, "co", 3)),
              "loop_vertices": array_digest(read_array(mesh.loops, "vertex_index", 1, np.int32)),
              "triangles": array_digest(read_array(mesh.loop_triangles, "loops", 3, np.int32)),
              "corner_normals": array_digest(read_array(mesh.corner_normals, "vector", 3)),
              "uv": {name: array_digest(read_array(mesh.uv_layers[name].data, "uv", 2))
                     for name in uv_names}}
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    em = evaluated.to_mesh(preserve_all_data_layers=True,
                           depsgraph=bpy.context.evaluated_depsgraph_get())
    try:
        em.calc_loop_triangles()
        result["evaluated_position"] = array_digest(read_array(em.vertices, "co", 3))
        result["evaluated_triangles"] = array_digest(read_array(em.loop_triangles, "loops", 3, np.int32))
        result["evaluated_normals"] = array_digest(read_array(em.corner_normals, "vector", 3))
        if uv_names:
            # Match the pre-existing active render UV explicitly, never UV_AO.
            render_uv = next((u.name for u in mesh.uv_layers if u.active_render), uv_names[0])
            assert render_uv in uv_names, "AO UV unexpectedly active for normal tangents"
            em.calc_tangents(uvmap=render_uv)
            result["existing_tangent_UV"] = render_uv
            result["evaluated_tangent"] = array_digest(read_array(em.loops, "tangent", 3))
            result["evaluated_bitangent_sign"] = array_digest(read_array(em.loops, "bitangent_sign", 1))
    finally:
        evaluated.to_mesh_clear()
    return result


def witnesses(objects, uv_names):
    return {o.name: mesh_witness(o, uv_names[o.name]) for o in objects}


def demand_same(before, after, label):
    assert before == after, f"Conservation failed ({label}); stop, do not relax tolerances"


def select_meshes(objects):
    import bpy
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]


def uv_overlap_audit(objects, epsilon):
    """Exact convex clipping after a 128² broadphase, not a pixel occupancy test.

    Zero-area edge contacts are legal. A positive intersection area above the
    explicit numerical epsilon fails. This does not prove mip gutter quality.
    """
    def cross(a, b):
        return float(a[0] * b[1] - a[1] * b[0])
    def intersection_area(a, b):
        polygon = list(a)
        if cross(b[1] - b[0], b[2] - b[0]) < 0:
            b = b[::-1]
        for start, end in zip(b, np.roll(b, -1, axis=0)):
            if not polygon:
                return 0.0
            output = []
            previous = polygon[-1]
            pd = cross(end - start, previous - start)
            for current in polygon:
                cd = cross(end - start, current - start)
                if (cd >= 0) != (pd >= 0):
                    output.append(previous + (current - previous) * (pd / (pd - cd)))
                if cd >= 0:
                    output.append(current)
                previous, pd = current, cd
            polygon = output
        return abs(sum(cross(a, b) for a, b in zip(polygon, polygon[1:] + polygon[:1]))) * .5
    triangles, owners = [], []
    for obj in objects:
        mesh = obj.data
        mesh.calc_loop_triangles()
        uv = read_array(mesh.uv_layers[UV_AO].data, "uv", 2).astype(np.float64)
        for tri in mesh.loop_triangles:
            points = uv[list(tri.loops)]
            assert np.isfinite(points).all() and (points >= 0).all() and (points <= 1).all()
            assert abs(cross(points[1] - points[0], points[2] - points[0])) > epsilon
            triangles.append(points)
            owners.append([obj.name, tri.index])
    grid, tests = collections.defaultdict(list), 0
    for i, tri in enumerate(triangles):
        lo = np.minimum(127, np.floor(tri.min(axis=0) * 128).astype(int))
        hi = np.minimum(127, np.floor(tri.max(axis=0) * 128).astype(int))
        cells = [(x, y) for x in range(lo[0], hi[0] + 1) for y in range(lo[1], hi[1] + 1)]
        candidates = {j for cell in cells for j in grid[cell]}
        for j in candidates:
            other = triangles[j]
            if np.any(tri.max(0) <= other.min(0)) or np.any(other.max(0) <= tri.min(0)):
                continue
            tests += 1
            area = intersection_area(tri, other)
            assert area <= epsilon, f"AO UV overlap: {owners[i]} / {owners[j]}, area={area}"
        for cell in cells:
            grid[cell].append(i)
    return {"triangles": len(triangles), "exact_pair_tests": tests,
            "overlap_area_epsilon_UV2": epsilon, "positive_overlap_found": False,
            "mip_margin_or_texel_density_qualified": False}


def unwrap_pack(objects, settings):
    import bpy
    for obj in objects:
        mesh = obj.data
        assert UV_AO not in mesh.uv_layers, "Reserved UV name already used"
        if not mesh.uv_layers:
            mesh.uv_layers.new(name="UV0_placeholder", do_init=False)
        assert len(mesh.uv_layers) == 1, "Expected zero/one existing UV; do not reorder hidden UVs"
        mesh.uv_layers.new(name=UV_AO, do_init=False)
        mesh.uv_layers.active_index = 1
        for loop in mesh.uv_layers[UV_AO].data:
            loop.select = True
    select_meshes(objects)
    bpy.context.scene.tool_settings.use_uv_select_sync = False
    bpy.ops.object.mode_set(mode="EDIT")
    try:
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(settings["unwrap_angle_deg"]),
                                island_margin=0, area_weight=0, correct_aspect=True,
                                scale_to_bounds=False)
        bpy.ops.uv.select_all(action="SELECT")
        # Two bake margins between islands; border reserved separately below.
        border = settings["margin_px"] / settings["resolution"]
        bpy.ops.uv.pack_islands(udim_source="CLOSEST_UDIM", rotate=True,
                               rotate_method="ANY", scale=True, merge_overlap=False,
                               margin_method="FRACTION", margin=2 * border,
                               pin=False, shape_method="CONCAVE")
    finally:
        bpy.ops.object.mode_set(mode="OBJECT")
    border = settings["margin_px"] / settings["resolution"]
    for obj in objects:
        mesh = obj.data
        values = read_array(mesh.uv_layers[UV_AO].data, "uv", 2)
        values = values * (1 - 2 * border) + border
        mesh.uv_layers[UV_AO].data.foreach_set("uv", values.ravel())
        if mesh.uv_layers[0].name == "UV0_placeholder":
            # Existing UV0 is never written. This placeholder has no source map.
            mesh.uv_layers[0].data.foreach_set("uv", values.ravel())
        mesh.uv_layers.active_index = 0
        mesh.uv_layers[0].active_render = True


def load_glb(path):
    data = Path(path).read_bytes()
    magic, version, length = struct.unpack_from("<III", data)
    assert magic == 0x46546C67 and version == 2 and length == len(data)
    size, kind = struct.unpack_from("<II", data, 12)
    assert kind == 0x4E4F534A
    document = json.loads(data[20:20 + size])
    start = 20 + size
    size, kind = struct.unpack_from("<II", data, start)
    assert kind == 0x004E4942
    binary = data[start + 8:start + 8 + size]
    def accessor(index):
        a = document["accessors"][index]
        assert "sparse" not in a and not a.get("normalized", False)
        view = document["bufferViews"][a["bufferView"]]
        dtype = {5126: "<f4", 5125: "<u4", 5123: "<u2", 5121: "u1"}[a["componentType"]]
        width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[a["type"]]
        return np.ndarray((a["count"], width), dtype=dtype, buffer=binary,
                          offset=view.get("byteOffset", 0) + a.get("byteOffset", 0),
                          strides=(view.get("byteStride", width * np.dtype(dtype).itemsize),
                                   np.dtype(dtype).itemsize)).copy()
    return document, binary, accessor


def material_export_signatures(document, binary):
    """Compare original material payloads; permit only the AO addition."""
    def texture_signature(index):
        texture = document["textures"][index]
        image = document["images"][texture["source"]]
        view = document["bufferViews"][image["bufferView"]]
        start = view.get("byteOffset", 0)
        payload = binary[start:start + view["byteLength"]]
        return {"image_sha256": hashlib.sha256(payload).hexdigest(),
                "sampler": document.get("samplers", [])[texture["sampler"]]
                if "sampler" in texture else None}
    def visit(value):
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                if key.endswith("Texture") and isinstance(item, dict) and "index" in item:
                    result[key] = {**{k: visit(v) for k, v in item.items() if k != "index"},
                                   "resolved_texture": texture_signature(item["index"])}
                else:
                    result[key] = visit(item)
            return result
        if isinstance(value, list):
            return [visit(v) for v in value]
        return value
    signatures = []
    for material in document["materials"]:
        original = {k: v for k, v in material.items()
                    if k not in {"name", "occlusionTexture", "extras"}}
        signatures.append(hashlib.sha256(json.dumps(visit(original), sort_keys=True).encode()).hexdigest())
    return signatures


def corner_table(document, accessor, node, attributes, material_signatures):
    """Exact float32 corner multiset, preserving cyclic orientation.

    No spatial quantization or proximity matching. Material and protected
    corner bits break ties for coincident triangles, so a harmless reorder is
    allowed only if the complete oriented records remain identical.
    """
    values, materials = [], []
    for primitive in document["meshes"][node["mesh"]]["primitives"]:
        assert primitive.get("mode", 4) == 4
        ids = accessor(primitive["indices"]).ravel().astype(np.int64)
        assert len(ids) % 3 == 0
        arrays = [accessor(primitive["attributes"][key])[ids].reshape((-1, 3, width))
                  for key, width in attributes]
        assert all(a.dtype.kind == "f" and a.dtype.itemsize == 4 for a in arrays)
        joined = np.concatenate(arrays, axis=2)
        assert np.isfinite(joined).all(), "Nonfinite protected float32 attributes"
        positions = np.ascontiguousarray(joined[:, :, :3]).view(np.uint32)
        # Canonical cyclic order only. Reversing triangle orientation is illegal.
        for i in range(len(joined)):
            rotation = min(range(3), key=lambda k: tuple(np.roll(positions[i], -k, axis=0).ravel()))
            joined[i] = np.roll(joined[i], -rotation, axis=0)
            positions[i] = np.roll(positions[i], -rotation, axis=0)
        values.append((positions.reshape((-1, 9)), joined))
        materials.extend([material_signatures[primitive["material"]]] * len(joined))
    keys = np.concatenate([k for k, v in values])
    table = np.concatenate([v for k, v in values])
    materials = np.asarray(materials)
    corner_bits = np.ascontiguousarray(table).view(np.uint32).reshape((len(table), -1))
    sort_columns = ([keys[:, i] for i in range(9)] + [materials]
                    + [corner_bits[:, i] for i in range(corner_bits.shape[1])])
    order = np.lexsort(tuple(reversed(sort_columns)))
    return keys[order], table[order], materials[order]


def audit_export(reference, candidate, tolerances):
    """Compare per physical node, permitting only exporter UV vertex splits."""
    base, bb, ba = load_glb(reference)
    test, tb, ta = load_glb(candidate)
    bm = material_export_signatures(base, bb)
    tm = material_export_signatures(test, tb)
    bn = {n["name"]: n for n in base["nodes"] if "mesh" in n}
    tn = {n["name"]: n for n in test["nodes"] if "mesh" in n}
    assert bn.keys() == tn.keys(), "Physical mesh node set changed"
    result = []
    for name, node in bn.items():
        p = base["meshes"][node["mesh"]]["primitives"]
        attributes = [("POSITION", 3), ("NORMAL", 3)]
        if any("normalTexture" in base["materials"][x["material"]] for x in p):
            assert all("TEXCOORD_0" in x["attributes"] and "TANGENT" in x["attributes"] for x in p)
            attributes += [("TEXCOORD_0", 2), ("TANGENT", 4)]
        # Direct node TRS/matrix proof in addition to source hierarchy fingerprints.
        for prop in ("matrix", "translation", "rotation", "scale"):
            demand_same(node.get(prop), tn[name].get(prop), f"export node {name}/{prop}")
        bk, bv, bmat = corner_table(base, ba, node, attributes, bm)
        tk, tv, tmat = corner_table(test, ta, tn[name], attributes, tm)
        if not np.array_equal(bk, tk):
            # Unmatched exact records are evidence; no nearest-position match.
            source_keys = collections.Counter(row.tobytes() for row in bk)
            derived_keys = collections.Counter(row.tobytes() for row in tk)
            missing, added = source_keys - derived_keys, derived_keys - source_keys
            raise ConservationError(f"Exact oriented position records changed: {name}", {
                "node": name, "kind": "POSITION_float32_exact_mismatch",
                "source_triangles": len(bk), "derived_triangles": len(tk),
                "missing_exact_triangles": sum(missing.values()),
                "added_exact_triangles": sum(added.values()),
                "missing_examples_uint32": [np.frombuffer(k, dtype=np.uint32).tolist()
                                            for k in list(missing)[:3]],
                "added_examples_uint32": [np.frombuffer(k, dtype=np.uint32).tolist()
                                          for k in list(added)[:3]],
                "spatial_grouping_or_nearest_matching_used": False})
        if not np.array_equal(bmat, tmat):
            raise ConservationError(f"Original material/map assignment changed: {name}", {
                "node": name, "kind": "material_or_original_image_mismatch",
                "mismatched_oriented_records": int(np.count_nonzero(bmat != tmat))})
        assert bv.shape == tv.shape
        errors, offset = {}, 0
        for key, width in attributes:
            source_values = np.ascontiguousarray(bv[:, :, offset:offset + width])
            derived_values = np.ascontiguousarray(tv[:, :, offset:offset + width])
            changed = source_values.view(np.uint32) != derived_values.view(np.uint32)
            delta = np.abs(source_values.astype(np.float64) - derived_values.astype(np.float64))
            error = float(delta.max(initial=0))  # Diagnostic only, never acceptance.
            if np.any(changed):
                first = tuple(np.argwhere(changed)[0])
                raise ConservationError(f"Protected {key} float32 bits changed: {name}", {
                    "node": name, "kind": key + "_float32_exact_mismatch",
                    "changed_scalar_count": int(np.count_nonzero(changed)),
                    "max_abs_difference_diagnostic_only": error,
                    "first_changed_triangle_corner_component": list(map(int, first)),
                    "source_float32": float(source_values[first]),
                    "derived_float32": float(derived_values[first]),
                    "source_uint32": int(source_values.view(np.uint32)[first]),
                    "derived_uint32": int(derived_values.view(np.uint32)[first]),
                    "change_tolerance": "none; fail before investigating cause"})
            errors[key] = error
            offset += width
        # Report real unit-length quantification; reject beyond explicit bound.
        base_normal_error = float(np.abs(np.linalg.norm(bv[:, :, 3:6], axis=2) - 1).max(initial=0))
        normal_error = float(np.abs(np.linalg.norm(tv[:, :, 3:6], axis=2) - 1).max(initial=0))
        assert normal_error <= tolerances["normal_unit_error"]
        result.append({"node": name, "triangles": len(tv), "max_abs_errors": errors,
                       "max_normal_unit_error": normal_error,
                       "source_max_normal_unit_error": base_normal_error,
                       "original_materials_and_images_unchanged": True,
                       "source_normal_float32_sha": array_digest(bv[:, :, 3:6]),
                       "derived_normal_float32_sha": array_digest(tv[:, :, 3:6])})
    return {"physical_nodes": result, "vertex_array_memcmp_claimed": False,
            "method": "Per-node exact float32 oriented/cyclic position/corner records; no spatial grouping. Coincident records are sorted using material and protected corner bits. No protected attribute change is accepted.",
            "separate_technical_limits": {"normal_unit_error": tolerances["normal_unit_error"]},
            "external_gltf_validator_run": False}


def verify_occlusion(glb, image, stage, expected_receivers):
    import bpy
    document, binary, accessor = load_glb(glb)
    expected = np.array(image.pixels[:], dtype=np.float32).reshape((-1, 4))[:, 0]
    image_checks, primitive_count = {}, 0
    for node in document["nodes"]:
        if "mesh" not in node:
            continue
        assert node["name"] in expected_receivers
        for primitive in document["meshes"][node["mesh"]]["primitives"]:
            primitive_count += 1
            material = document["materials"][primitive["material"]]
            occlusion = material.get("occlusionTexture")
            assert occlusion and occlusion.get("texCoord", 0) == 1
            assert occlusion.get("strength", 1) == 1
            assert "TEXCOORD_1" in primitive["attributes"]
            uv = accessor(primitive["attributes"]["TEXCOORD_1"])
            assert np.isfinite(uv).all() and (uv >= 0).all() and (uv <= 1).all()
            texture = document["textures"][occlusion["index"]]
            idx = texture["source"]
            if idx in image_checks:
                continue
            entry = document["images"][idx]
            assert entry.get("mimeType") == "image/png" and "bufferView" in entry
            view = document["bufferViews"][entry["bufferView"]]
            payload = binary[view.get("byteOffset", 0):view.get("byteOffset", 0) + view["byteLength"]]
            file = stage / f"exported-occlusion-{idx}.png"
            assert not file.exists()
            file.write_bytes(payload)
            loaded = bpy.data.images.load(str(file), check_existing=False)
            try:
                loaded.colorspace_settings.name = "Non-Color"
                assert list(loaded.size) == list(image.size)
                red = np.array(loaded.pixels[:], dtype=np.float32).reshape((-1, 4))[:, 0]
                error = float(np.abs(red - expected).max(initial=0))
                assert error <= 1 / 255 + 1e-6, "Exported R does not preserve baked scalar"
                image_checks[idx] = {"sha256": digest(file), "red_error_abs": error,
                                     "png_quantization_tolerance": 1 / 255 + 1e-6}
            finally:
                bpy.data.images.remove(loaded)
    return {"primitives_with_AO": primitive_count, "images": image_checks,
            "runtime_shader_was_verified": False,
            "next_gate": "Babylon coordinatesIndex1/gammaSpacefalse/strength0-1 and analytical impact0 must be checked by a separate real GPU capture."}


def prepare(spec, stage, protocol):
    import bpy
    bpy.ops.wm.open_mainfile(filepath=str(repo_path(spec["material_spec_data"]["source"])))
    collection = bpy.data.collections[spec["collection"]]
    objects = sorted((o for o in collection.all_objects if o.type == "MESH" and not o.hide_render), key=lambda o: o.name)
    assert len(objects) == spec["physical_mesh_copies"]
    assert all(o.library is None for o in objects), "Unexpected linked Object IDs: stop before localisation"
    assert all(not o.modifiers and not o.data.shape_keys for o in objects), "Modifier/morph bake not covered"
    assert all(slot.link == "DATA" for o in objects for slot in o.material_slots), "Object material overrides require explicit handling"
    names = {o.name: [u.name for u in o.data.uv_layers] for o in objects}
    before = witnesses(objects, names)
    original_active = {o.name: o.data.uv_layers.active_index for o in objects}
    material_proof = {}
    for obj in objects:
        obj.data = obj.data.copy()  # Each tappet occurrence gets independent UVs.
        assert obj.data.library is None
        for i, material in enumerate(list(obj.data.materials)):
            assert material and material.use_nodes
            local = material.copy()
            assert local.library is None
            obj.data.materials[i] = local
            material_proof[local.name] = material_signature(local)
    bpy.context.view_layer.update()
    demand_same(before, witnesses(objects, names), "localised mesh/data/material copies")
    unwrap_pack(objects, spec["AO"])
    bpy.context.view_layer.update()
    demand_same(before, witnesses(objects, names), "unwrap/pack left original geometry/normals/UV/T/poses intact")
    uv_proof = uv_overlap_audit(objects, spec["tolerances"]["uv_area_epsilon"])
    for obj in objects:
        obj["qa_ao_original_uv_names"] = json.dumps(names[obj.name])
        obj["qa_ao_source_object"] = obj.name
    bpy.context.scene["qa_ao_protocol_sha256"] = protocol["spec_sha256"]
    scene = bpy.context.scene
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 1
    target = stage / "prepared-local-uv.blend"
    assert not target.exists()
    bpy.ops.wm.save_as_mainfile(filepath=str(target), check_existing=False)
    report = {**protocol, "phase": "prepare", "source_copy_created": True,
              "bake_executed": False, "prepared_blend": str(target), "prepared_blend_sha256": digest(target),
              "original_witnesses": before, "original_uv_names": names,
              "original_active_uv_indices": original_active, "material_signatures": material_proof,
              "uv_audit": uv_proof, "art_accepted": False, "runtime_checked": False}
    write_json(stage / "prepare-report.json", report)


def bake(spec, stage, protocol, prepare_stage):
    import bpy
    report_path = prepare_stage / "prepare-report.json"
    prior = json.loads(report_path.read_text())
    assert not (prepare_stage / "FAILED.json").exists(), "Rejected preparation cannot be baked"
    assert prior["spec_sha256"] == protocol["spec_sha256"]
    assert prior["tool_sha256"] == protocol["tool_sha256"], "Tool changed after prepare; new run required"
    prepared = Path(prior["prepared_blend"])
    assert prepared.resolve().is_relative_to(prepare_stage.resolve())
    assert digest(prepared) == prior["prepared_blend_sha256"]
    bpy.ops.wm.open_mainfile(filepath=str(prepared))
    assert bpy.context.scene["qa_ao_protocol_sha256"] == protocol["spec_sha256"]
    objects = sorted((o for o in bpy.data.collections[spec["collection"]].all_objects
                      if o.type == "MESH" and not o.hide_render), key=lambda o: o.name)
    demand_same(prior["original_witnesses"], witnesses(objects, prior["original_uv_names"]), "prepared file reload")
    uv_proof = uv_overlap_audit(objects, spec["tolerances"]["uv_area_epsilon"])
    materials = {m.name: m for o in objects for m in o.data.materials}
    demand_same(prior["material_signatures"], {n: material_signature(m) for n, m in materials.items()}, "prepared material reload")
    scene, settings = bpy.context.scene, spec["AO"]
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = settings["cycles_samples"]
    scene.cycles.seed = settings["seed"]
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.use_denoising = False
    scene.render.threads_mode, scene.render.threads = "FIXED", 1
    scene.render.use_compositing = False
    scene.render.bake.use_selected_to_active = False
    scene.render.bake.use_clear = False
    scene.render.bake.margin = settings["margin_px"]
    scene.render.bake.margin_type = "EXTEND"
    scene.render.bake.target = "IMAGE_TEXTURES"
    image = bpy.data.images.new("QA original local AO - not qualified", width=settings["resolution"],
                                height=settings["resolution"], alpha=False, float_buffer=False)
    image.colorspace_settings.name = "Non-Color"
    image.generated_color = (1, 1, 1, 1)
    image.pixels.foreach_set(np.ones(settings["resolution"] ** 2 * 4, dtype=np.float32))
    image.update()
    restores = []
    try:
        for material in materials.values():
            tree = material.node_tree
            old_active = tree.nodes.active
            old_selection = {n: n.select for n in tree.nodes}
            outputs = [n for n in tree.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output]
            assert len(outputs) == 1
            output = outputs[0]
            assert not output.inputs["Volume"].is_linked and not output.inputs["Displacement"].is_linked
            old_links = [(l.from_socket, l.to_socket) for l in output.inputs["Surface"].links]
            assert len(old_links) == 1
            temporary = []
            restores.append((material, old_active, old_selection, old_links, temporary))
            ao = tree.nodes.new("ShaderNodeAmbientOcclusion"); temporary.append(ao)
            ao.inputs["Distance"].default_value = settings["distance_m"]
            ao.inside = False
            ao.only_local = True
            ao.samples = settings["node_samples"]
            emission = tree.nodes.new("ShaderNodeEmission"); temporary.append(emission)
            emission.inputs["Strength"].default_value = 1
            tree.links.new(ao.outputs["AO"], emission.inputs["Color"])
            tree.links.new(emission.outputs[0], output.inputs["Surface"])
            target = tree.nodes.new("ShaderNodeTexImage"); temporary.append(target)
            target.image = image
            for node in tree.nodes:
                node.select = False
            target.select = True
            tree.nodes.active = target
        for obj in objects:
            obj.data.uv_layers.active_index = 1
        select_meshes(objects)
        result = bpy.ops.object.bake(type="EMIT", uv_layer=UV_AO,
                                     use_clear=False, use_selected_to_active=False,
                                     margin=settings["margin_px"])
        assert result == {"FINISHED"}
    finally:
        for material, active, selection, links, temporary in reversed(restores):
            tree = material.node_tree
            for node in reversed(temporary):
                tree.nodes.remove(node)
            for origin, destination in links:
                tree.links.new(origin, destination)
            tree.nodes.active = active
            for node, selected in selection.items():
                node.select = selected
        for obj in objects:
            obj.data.uv_layers.active_index = 0
            obj.data.uv_layers[0].active_render = True
    demand_same(prior["material_signatures"], {n: material_signature(m) for n, m in materials.items()}, "exact shader restore after EMIT bake")
    bpy.context.view_layer.update()
    demand_same(prior["original_witnesses"], witnesses(objects, prior["original_uv_names"]), "after AO bake")
    pixels = np.array(image.pixels[:], dtype=np.float32).reshape((-1, 4))
    assert np.isfinite(pixels).all() and (pixels[:, :3] >= 0).all() and (pixels[:, :3] <= 1).all()
    assert np.max(np.abs(pixels[:, 0] - pixels[:, 1])) < 1e-5
    assert np.max(np.abs(pixels[:, 0] - pixels[:, 2])) < 1e-5
    assert pixels[:, 0].min() < .99, "AO all white: do not claim bake applied"
    texture_dir = stage / "textures"; texture_dir.mkdir()
    png = texture_dir / "original-local-ao.png"
    image.filepath_raw, image.file_format = str(png), "PNG"
    image.save()  # Data image, NOT save_render / AgX.
    image.pack()
    image.filepath_raw = "//textures/original-local-ao.png"
    # Exact recognised exporter hook. Source shader nodes remain intact.
    group = bpy.data.node_groups.new("glTF Material Output", "ShaderNodeTree")
    assert group.name == "glTF Material Output", "Existing hook requires explicit review"
    group.interface.new_socket(name="Occlusion", in_out="INPUT", socket_type="NodeSocketFloat")
    group.nodes.new("NodeGroupInput")
    for material in materials.values():
        tree = material.node_tree
        uv = tree.nodes.new("ShaderNodeUVMap"); uv.uv_map = UV_AO
        tex = tree.nodes.new("ShaderNodeTexImage"); tex.image = image
        separate = tree.nodes.new("ShaderNodeSeparateColor"); separate.mode = "RGB"
        hook = tree.nodes.new("ShaderNodeGroup"); hook.node_tree = group
        tree.links.new(uv.outputs["UV"], tex.inputs["Vector"])
        tree.links.new(tex.outputs["Color"], separate.inputs["Color"])
        tree.links.new(separate.outputs["Red"], hook.inputs["Occlusion"])
    # Persist a distinct derived scene; never save the prepared or source file.
    derived = stage / "upper-engine-local-ao-diagnostic.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(derived), check_existing=False)
    selected = list(bpy.data.collections[spec["collection"]].all_objects)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in selected:
        obj.hide_set(False); obj.select_set(True)
    glb = stage / "upper-engine-local-ao-diagnostic.glb"
    # No shared exporter patch, no post-export buffer repair or tangent pruning.
    import addon_utils
    addon_utils.enable("io_scene_gltf2", default_set=False, persistent=False)
    result = bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB",
                                      use_selection=True, export_yup=True,
                                      export_texcoords=True, export_normals=True,
                                      export_tangents=True, export_apply=False,
                                      export_materials="EXPORT", export_image_format="PNG",
                                      export_keep_originals=False, export_animations=False,
                                      export_cameras=False, export_lights=False)
    assert result == {"FINISHED"}
    geo_check = audit_export(repo_path(spec["material_spec_data"]["export"]), glb, spec["tolerances"])
    ao_check = verify_occlusion(glb, image, stage, {o.name for o in objects})
    report = {**protocol, "phase": "bake", "bake_executed": True,
              "prepare_report_sha256": digest(report_path), "AO": settings,
              "restored_original_material_signatures": prior["material_signatures"],
              "UV_overlap_check": uv_proof, "export_geometry_check": geo_check,
              "occlusion_export_check": ao_check,
              "outputs": {str(p): digest(p) for p in (derived, glb, png)},
              "art_accepted": False, "runtime_checked": False,
              "mobile_qualified": False, "photometric_parity": False}
    write_json(stage / "bake-report.json", report)


def main():
    import bpy
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("prepare", "bake"), required=True)
    parser.add_argument("--spec", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    spec_path = args.spec.resolve()
    spec = json.loads(spec_path.read_text())
    assert tuple(bpy.app.version) == (4, 3, 2), "Pinned Blender4.3.2 required"
    material_spec = repo_path(spec["material_spec"])
    assert digest(material_spec) == spec["material_spec_sha256"]
    material_data = json.loads(material_spec.read_text())
    for key in ("source", "export", "HDR"):
        assert digest(repo_path(material_data[key])) == material_data[key + "_sha256"]
    linked = repo_path(material_data["linked_source_check"])
    assert digest(linked) == material_data["linked_source_check_sha256"]
    libraries = json.loads(linked.read_text())["linked_sources"]
    assert len(libraries) == 7
    demand_same(spec["linked_libraries_expected"], libraries, "seven pinned library identities")
    for row in libraries:
        assert digest(repo_path(row["source"])) == row["sha256"]
    for row in spec["API_references"]:
        assert digest(repo_path(row["path"])) == row["sha256"], "Inspected API/reference changed"
    assert spec["AO"] == {"resolution": 1024, "margin_px": 8, "distance_m": .015,
                           "only_local": True, "inside": False, "cycles_samples": 16,
                           "node_samples": 16, "seed": 331601, "threads": 1,
                           "device": "CPU", "unwrap_angle_deg": 66}
    spec["material_spec_data"] = material_data
    base = repo_path(spec["output_root"])
    assert base.is_relative_to(Path("/workspace/wewa-assets/work-in-progress")), "Private derivative destination required"
    if args.phase == "prepare":
        base.mkdir(parents=True, exist_ok=False)
    else:
        assert (base / "prepare" / "prepare-report.json").is_file()
    stage = base / args.phase
    stage.mkdir(exist_ok=False)
    inputs = {str(repo_path(material_data[key])): material_data[key + "_sha256"] for key in ("source", "export", "HDR")}
    inputs.update({str(repo_path(row["source"])): row["sha256"] for row in libraries})
    inputs[str(material_spec)] = spec["material_spec_sha256"]
    inputs[str(linked)] = material_data["linked_source_check_sha256"]
    protocol = {"schema": "wewa.local-ao-QA.v1", "spec_sha256": digest(spec_path),
                "tool_sha256": digest(__file__), "blender_version": bpy.app.version_string,
                "immutable_inputs": inputs, "phase_output": str(stage),
                "unexecuted_tool_is_not_proof": True}
    try:
        if args.phase == "prepare":
            prepare(spec, stage, protocol)
        else:
            bake(spec, stage, protocol, base / "prepare")
        for path, expected in inputs.items():
            assert digest(path) == expected, f"Immutable input changed: {path}"
    except BaseException as error:
        failure = {**protocol, "failed": True, "traceback": traceback.format_exc(),
                   "conservation_diagnostic": getattr(error, "diagnostic", None),
                   "immutable_inputs_after": {p: digest(p) for p in inputs},
                   "outputs_not_accepted": True, "retry_requires_new_output_root": True}
        write_json(stage / "FAILED.json", failure)
        raise


if __name__ == "__main__":
    main()
