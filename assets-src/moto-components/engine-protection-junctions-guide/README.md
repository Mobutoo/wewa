# Engine-guard junction context — working assembly v1

Context scene only. It copies four already fabricated candidate meshes (tube, centre plate, independently made terminalA and terminalB), applies explicit estimated poses and adds no new physical component. No weld, hook, spacer, fastening, actual installation or strength is received.

`build_guide.py` reads the four source paths and records their SHA256 before/after; local mesh positions remain unchanged. All actual datablocks are local. Blender's append weak Library metadata is removed only after an actual `bpy.data.user_map()` check establishes there are no linked datablocks. Eight original author PNGs are packed and have byte-exact relative companions; no private photograph pixels.

The tab contact witness samples192 nominal tube-end annulus locations against actual transformed plate triangles per end. It is a sampled working-pose witness, not a full contact/intersection/strength certificate or a recovered OEM interface. A and B use opposite estimated poses; their meshes were never mirrored. The B lower hole and backside remain unknown. The centre-plate return placement is a separate estimated hypothesis.

References and pose choices: `creative/research/engine-protection-junctions-15-v1/`. [Related PF231201 photographs](https://www.croslandrepuestos.pe/protector-de-piernas-pf231201/p) are comparison inputs, not a calibrated installation or current RDC certification.

Rebuild in Blender4.3.2 with bundled numpy, one thread, `--python-exit-code 1 --python build_guide.py`. The three gray12 pictures are RAM-only material overrides; the saved source keeps the original candidate PBR materials. Original component sources are never saved. No GLB or new component ID is produced.
