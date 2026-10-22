# JZ561415 exterior review context v1

This is one reusable local context parent, **zero new physical IDs**, not a new selector geometry or qualified mounted assembly. Five existing native parents are linked through collection instances, one occurrence each; seven source mesh objects and their original materials remain external, unchanged. Link collection `GEAR_SELECTOR_EXTERIOR_CONTEXT_V1` for integration, excluding review lights/camera. Move `GEAR_SELECTOR_EXTERIOR_CONTEXT_ROOT` as a whole. No world-motorcycle mounting transform is supplied.

Native: `gear-selector-exterior-context-v1.blend`. Review export: `gear-selector-exterior-context-v1-inspection.glb`. Existing parent directories must remain alongside this directory for native relative library resolution. Native axes: X toe negative / heel positive, Y projected up, Z toward rubber side. GLB conversion is X,Y,Z -> X,Z,-Y.

The arm remains in its native frame. Collar and visible ears/head share exactly the same rigid transform. Their bridge is near the rear arm face with a nominal 2mm review gap; no root union or shaft is created. The toe sleeve is near the documented arm endpoint with a nominal 2mm gap, with no hidden peg or retention. The broad heel pad remains visibly separated near the heel terminal, its underside/seat uncertain. All transforms and uncertainty allowances are in `creative/research/gear-selector-exterior-context-v1/plan.json` and `native-links-and-transforms.json`. Those allowances are review estimates, not OEM tolerances.

Two opposite marked-kit photographs constrain the side relationship: hub opposite the rubbers. Position and clocking remain estimates. Marked JZ561415 related-family kit identity does **not** certify RDC125 applicability. Existing source simplifications (including arm terminal and heel tread/underside) remain unchanged. No hidden spline, shank, nut, root or supporting bracket is invented.

Gray is a render-only view-layer override; it is not saved in the native source. Three gray views were read before two original-material previews, then three actual 96-sample native renders including neutral, each with FLOAT32 multilayer EXR. Babylon imports seven meshes; software Chromium evidence is not hardware/artistic/physical-fit acceptance. No G8.

Review delivery: `creative/reviews/gear-selector-exterior-context-v1/delivery-frozen.json`. This context is for integration review; do not count its five parents again in physical coverage.
