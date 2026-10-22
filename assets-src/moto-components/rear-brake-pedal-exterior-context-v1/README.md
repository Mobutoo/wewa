# Rear brake pedal: four-parent local exterior review context

**Four existing parents, one occurrence each, zero new physical IDs.** No arm/mesh/material reconstruction, hidden pivot shaft, root union, weld, fixing or fitted foot-plane is manufactured. Rod/clevis are excluded: the source relationship to the pedal is unproven, and 6mm clevis versus9mm lug bores do not establish a mating pair. Related PF161002 product identity is not certified current-RDC125 fit.

## Native for main integration review

Use **`integration-wrapper.blend`**, collection **`REAR_BRAKE_PEDAL_EXTERIOR_INTEGRATION_V1`**, root **`REAR_BRAKE_PEDAL_EXTERIOR_CONTEXT_ROOT`**. It contains four local mesh-object wrappers referencing the **exact linked historical mesh datablocks and materials**, at the same four rigid poses as the review. All historical source files must remain at their canonical relative sibling paths. Stock coordinator checker actually passed its single linked `coord-exemplar.blend`, identity root and four visible source meshes.

`rear-brake-pedal-exterior-context-v1.blend` is the render-author source: four exact linked collection instances, identical data/poses/materials. `rear-brake-pedal-exterior-context-v1-inspection.glb` preserves source accessors/material factors and uses the same rigid matrices converted by C(X,Y,Z)=(X,Z,−Y). Actual GLB reimport confirms 111,534 oriented triangles and zero vertex distance from the native instances; import/custom-normal differences are recorded separately, not claimed bit-identical. The direct-object wrapper is structurally easier for the main checker; use **one** representation, not both together.

## Frame, parked pieces and world hint

Arm source frame: **+X projected front, +Y projected up, +Z estimated outward**. Root0 is the authored photo bend pixel178,159, **not a certified pivot centre**. Sleeve axis and lug-hole axes are transverse localZ. Their translations follow bounded product-photo guides; their axial/root relations remain separate and unqualified. The sleeve is partly occluded behind the arm in profile, visible in oblique/reverse views.

The pad at `[.20916,−.20475,.050]m` is **parked separately**, retaining its original source face-study orientation. It is **not** an installed foot-up surface. Do not turn it into a fitted pad by snapping to the arm endpoint `[.19278,−.17577,.028]`. That endpoint is not the pad centre; pad underside/angle/root remain unresolved.

Coordinator Q EulerXYZ **[90°,0°,−90°]**, determinant+1, maps local X→world−Y front, Y→world+Z up, Z→world−X right. The numeric convention is correct, but applying Q does **not** validate the product camera or installed kit. In particular the parked pad normal+Z would map to world−X rather than foot-up, so it must remain an explicitly separated review part or be excluded from mounted-context selection.

The coordinator illustrative endpoint target Y=.136,Z=−.777 implies **arm-origin** world Y=.32878,Z=−.60123; those are not proven pivot coordinates. With this review sleeve guide, its axis would instead have Y=.33508,Z=−.59493. Transverse worldX is unknown and is not assigned. No mounted transform or physical travel is supplied.

## Evidence

Three gray views actually read -> two original-material previews actually read -> three actual native96 views actually read, including independent neutral environment/FLOAT32 raw. Actual Babylon quarter/reverse views read. Source hashes/rigid matrices and wrapper equivalence are frozen in the research namespace; no private photo pixels redistributed. Existing source shape/paint/G4/G8 limitations remain. This is not a received functioning pedal assembly.

Flat fragment, exemplar contract and immutable delivery: `creative/reviews/rear-brake-pedal-exterior-context-v1/`.
