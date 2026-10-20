VIVA WEWA — EDITABLE ARCHITECTURE AND STREET KIT

Production files
- viva-wewa-street-kit.blend: named collections containing editable individual construction parts.
- generate_street_kit.py: original offline Blender generator; no external Python dependencies.
- exports/: 12 architectural bays and 20 street props exported at their placement origin.
- manifest.json: bounds, dimensions, front vector, triangle budget, materials, provenance, SHA256.
- validation.json: actual Khronos glTF Validator results, all exported files.
- facades-preview.png / props-preview.png: actual offline Blender renders, not game captures.

Rebuild
blender -b -t 4 --python generate_street_kit.py

The generator resolves its directory automatically. Keep textures/ beside the script. Concrete maps
are also packed into the .blend and embedded in the GLBs. No paid asset or external model is needed.

Placement contract
GLB metres; +Y up, +Z points toward street, +X right. Asset origin is ground/storey base centre.
All architectural bays are exactly 3.4 m wide by 3.0 m high with <=0.65 m total depth.
They are open assemblies: no full rectangular wall backing is exported. Source building geometry
provides the rear wall. Place and cull on source building edges; never enlarge source footprints.
Perforated compound panels genuinely have holes; shutters, fins and railings are geometry.

Editing
Each source asset has an EDITABLE_ROOT empty. Its offset is only for the library contact sheet.
Move that root to origin before a manual export, preserving the original parts' local positions.
The generator exports copies fused by shared material while retaining the individual source parts.
The library shares five material names. Runtime code can reuse/deduplicate these materials and
geometry for thin instances. Glass is solid dark PBR, not a transparent interior rendering feature.

Rights and limits
Geometry is original procedural work authored for the user's Viva Wewa project.
Only concrete_wall_003 diffuse/OpenGL-normal maps are from Poly Haven, CC0-1.0:
https://polyhaven.com/a/concrete_wall_003
https://polyhaven.com/license
The maps depict a concrete surface, not photographed building windows or a facade billboard.
Nothing here is a surveyed reconstruction of Gombe. No geographic coordinates or source footprints
were edited. Architectural plausibility, local placement and photographic acceptance remain to review.
