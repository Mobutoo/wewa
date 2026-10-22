# Engine exterior completion v3 — upper/rear cast envelope

Concrete bounded exterior candidate for main integration; no artistic acceptance or exact OEM fit claimed. Main owns Git and whole assembly. All historical files untouched.

Use `main-integration-fragment.json`: **add exactly one parent**, collection `WEWA_ENGINE_UPPER_REAR_CAST_SHELL_V3`, from `upper-rear-cast-shell-v3.blend`, translation/rotation zero, scale one. GLB: `upper-rear-cast-shell-v3.glb`. Do not add `diagnostic-linked-v3.blend` to the whole assembly: it includes the eight existing engine parents for comparison. Preserve all original161 parents; resulting162 before main's other additions.

## Root cause and observations

v2 corrected a lower LH apron, not the installed upper/rear cast enclosure. Existing bounds overlap, but actual evaluated surface rays show the upper/rear casing recessed20–42mm beneath the candidate shoulder at five stations (`actual-before-after-surface-rays.json`). This is an incomplete exterior envelope and donor/cover boundary mismatch, **not proof that the entire crankcase core is absent**. A blanket rigid displacement would disturb the cover axes and cylinder foot and is not justified.

Actually opened physical documentary images: official RDC `RDC-bike.webp`, RDC opposed04/00, and related BM150 JE541038 donor65222. SHA, private path, observations, identity distinction, and URLs are in `G0-G2-observations-and-bounds.json`. RDC photographs support compact contiguous casing directly under the inclined cylinder and real open frame triangles above/behind. The related disassembled donor constrains cast depth/shoulder, not exact RDC dimensions. No generated image is used as documentary evidence; documentary pixels are not redistributed.

## Shape and bounds

A compact hollow cast shell closes the upper/rear envelope. Thirteen longitudinal stations are recorded explicitly in the G0–G2 plan. Metres, inherited world datum; identity parent. Width constrained to102mm each side, cylinder foot constrained by the actual native flange atY.07076–.09745 andZ−.55873..−.55003; rear termination atY.367 remains before the existing output cover'sY.37603. Rounded transverse sections and tapered end terminations avoid the earlier exposed flat slab. Roof and thickness are estimated: roof±12mm, width±8mm, longitudinal stations±10mm, nominal wall6mm with4–10mm estimate range; thin tips use min(6mm,0.3×height,0.3×halfwidth), down to2.7mm offset at the9mm tip. This terminal construction thickness is not measured. Inner positive dimensions, monotoneY and vertex containment inside every interpolated outer section are asserted (`inner-shell-containment.json`). These are review bounds, not physical measurement precision. No internals, bearings, galleries, serials, hidden mechanisms or invented hardware.

The wide left flare trial was removed: finalX is±.102, not+.128. The remaining narrow donor/output-cover boundary seam is visible in `left-rear-after.png`. Exact donor pairing/cover boundary fit remains unknown; this candidate does not certify a welded/continuous OEM topology across independent parents. It improves the missing envelope without masking that boundary with a shelf. Review that seam in main's whole gray context before artistic acceptance.

## Proof

- `geometry-check.json`:832vertices,1656triangles, no boundary/nonmanifold edges. Outer0.007522110m³ minus cavity0.006503563m³ =0.001018547m³ material, below0.012980522m³ bounding box. Inner winding explicitly reversed after separate-component normal orientation.
- `export-parity-and-occupancy.json`: GLB reimport positions, triangle coordinate multiset, maximum vertex error; deck/rear occupancy and empty frame-space probes.
- `cylinder-foot-contact.json`: four actual flange rays,4.7–6.3mm source intersection, not a bore-interior probe. Small overlap provides a continuous visible exterior without pretending an OEM mating measurement.
- `historical-inputs-unchanged.json`: all eight original engine inputs retain their recorded SHA.
- `right-quarter-before.png` / `right-quarter-after.png` and `left-rear-before.png` / `left-rear-after.png`: actual native Cycles20sample CPU,640×540, same cameras/lights. `render-report.json` records parameters. No denoiser supported on this Blender build; previews are deliberately modest and show sampling grain. No whole-bike render or runtime G6 qualification is claimed by this local handoff.

No old assets, assembly/catalogue, workflow register, Git index, commit or remote changed by this owner. Source and GLB are compact; no blend1 or whole-source copies. `frozen-outputs.json` pins this handoff. Future modifications require a new version after main freezes it.
