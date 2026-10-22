# Existing RH side cover: standalone coordinate-conversion derivative

Both original RH meshes are preserved as the same physical objects, with the authorized improper convention conversion **A(x,y,z)=(-z,x,y)** baked into vertex positions. This is neither a copied LH cover nor a new physical part. Source objects and historical freezes remain unchanged. Origin0 and identity positive-scale object matrices are retained. The new collection `WEWA_RIGHT_SIDE_COVER_WORLD_FRAME_V1` contains **both** skin and visible lower head.

`child-candidate.blend` is standalone: no linked libraries; original material graphs and packed analytic image retained. `child-candidate.glb` is the corresponding normalized, unplaced export. Axes now match the motorcycle: +X pilot LEFT, +Y rear, +Z up. RH crown is toward −X. Integrate at identity rotation/unit scale; no negative scale or further convention rotation required.

The source det−1 conversion is **not a pure rigid rotation**. Winding is reversed once, with original vertex/triangle connectivity preserved. Source corner normals are transformed by A; UV values stay associated with the same polygon/vertex corners. The UV skin tangent follows A and its bitangent sign reverses relative to the historical native. The head had no UV/tangents and receives none. Official Blender4.3.2 exports the native bitangent sign unchanged while mapping V->1−V; actual native/GLB parity checks that behavior. No normal-map textures exist on the inherited materials.

Actual reopened-native/GLB proof covers 42,768 oriented triangles, attributes and actual source/export matrices. Original embedded PNG bytes and PBR factors are identical to the historical GLB. Three gray override views were read before two original-material previews, followed by three actual native96 views including independent neutral lighting and FLOAT32 raw EXRs. Gray is render-only; the material source is not replaced or retouched. Prior G4/G8 state is unchanged.

`build.py` exposes callable `build`, `normalize_object`, `export`, `render`. `exemplar.py` is the CLI wrapper: Blender `--python exemplar.py -- build|gray|preview|final`. Final uses the documented neutral-light wrapper in the research directory. Rebuilding a frozen deliverable is not an instruction to overwrite it; use a new revision for later changes.

## Estimated context, separately available

`estimated-context.blend` links this derivative collection once under `COVERAGE_PARENT [right-side-cover-coordinate-conversion-v1]`. `estimated-context.glb` wraps the normalized export once. Context **T=[−.135,.535,−.41]m, R0, scale[1,1,1]** passes the existing native coordination checker and native/GLB bounds checks.

World bounds: X −.158484..−.129m, Y .346449...720313m, Z −.522254..−.308385m. This is a coarse exterior context only. Relative to the source photo's nominal axle projection, T shifts the cover **65.0mm rearward and3.26mm upward** (−26.66px,−1.34px). The photograph and wholebike skeleton are uncalibrated; that shift is explicitly **not** qualified photo registration or physical fitting. Tank/seat/frame contacts and hidden mounts remain unresolved. No arbitrary spacers or hidden geometry are added.

Delivery: `creative/reviews/right-side-cover-coordinate-conversion-v1/delivery.json`. Flat fragment and exemplar wrapper are in that same review directory. Do not count the old RH source and this replacement derivative as separate physical parts.
