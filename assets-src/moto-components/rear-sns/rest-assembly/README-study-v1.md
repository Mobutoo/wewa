# SNS exact-source rest review — preparation

This is a composition study, not a thirteenth physical part. `resolve_inputs_v1.py` requires all twelve component final freezes to exist and verifies every listed file. `build_rest_v1.py` directly links the exact component collections with relative Blender library paths. Component mesh, material, node, and shared unplaced transforms remain unchanged; own studio/camera are review-only. No installed vehicle transform or suspension motion is added.

`merge_exact_glbs_v1.mjs` independently combines original GLB documents. Only buffers/scenes are collected; attributes and indices are checked byte-for-byte, with material semantics and local/world matrices, after reload. No deduplication, topology optimization or quantization. This transport check does not establish Blender/Babylon optical parity.

The first images are TWO whole gray views and ONE interface macro. A scene material override leaves the linked source materials untouched. Read the actual images against the PF native before any long final/PBR series. Observed missing external plates/supports become future fabrication, distinct from hidden hydraulic unknowns. Candidate radial/axial gaps are not seated contacts or functional load paths. Camera roll is a presentation choice only. Actual back/depth/scale/circumference estimates in the twelve components remain estimates.

Generation order from repository root: `python assets-src/moto-components/rear-sns/rest-assembly/resolve_inputs_v1.py`, Blender `build_rest_v1.py`, Node `merge_exact_glbs_v1.mjs`, then Blender `render_gray_v1.py`, all single CPU. No image is claimed saved/read by this preparation document. No reception or physical-device performance claim.
