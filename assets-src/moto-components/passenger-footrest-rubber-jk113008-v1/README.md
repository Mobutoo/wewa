# JK113008 passenger step rubber — one bounded exterior exemplar

Unique physical identity **MOTO-PASSENGER-FOOTREST-RUBBER-001**, P16, code JK113008. This is distinct from existing **DF161413 driver** `footrest-rubber-v1`; its geometry was not reused or remade. Root catalogue/parameter scan found no pre-existing JK113008 asset before this model. Manufacturer-family catalogues list two per motorcycle, but this source contains **one exemplar only**, no counterpart or repeated assembly.

Source: `child-candidate.blend`, matching export `child-candidate.glb`. Collection **`WEWA_PASSENGER_FOOTREST_RUBBER_JK113008_V1`** contains one mesh, `JK113008_PASSENGER_RUBBER_VISIBLE_ENVELOPE_ONLY`. Standalone native, identity object matrix/origin0. Local **+X is the longitudinal entry-to-distal axis**, Y lateral and Z review-up; no installed clocking/world position is established. `coord-exemplar.blend` links the source once at identity for the stock coordinator checker; it is an alternative inspection wrapper, not another physical step.

The original authored form follows the Russian Bajajonline and Mundimotos exact seller-code passenger photos: nearly cylindrical body, dense circumferential raised bands, flared terminal rims and short visible near-mouth lip. Near collar is circumferentially complete as observed. Working count14, uncertain13–15; selected length100mm, baseOD30mm, rimOD42mm with explicit broad author ranges in `parameters.json`. **These are uncalibrated estimates, not OEM measurements/tolerances or dimensions inferred from the metal support.** Rubber appearance is a proposed clean black dielectric; chemistry/Shore/friction/grain are undocumented. No private image is copied into geometry textures.

## Deliberately incomplete hidden/ambiguous surfaces

The Mundi longitudinal dark band remains flat-face versus opening versus cutout ambiguous. Consequently **only the lower90° of the middle body, X.010...090m, is omitted as a diagnostic review boundary**. This is **not a physical slot/window or key channel claim**. Both external flared collar rings remain present. The far closure, full inner bore, wall thickness, hidden seat and retention geometry are not invented. This is an open visible-envelope skin, not a manufactured solid/complete sleeve; the inner-looking render surface is the back of the exterior skin, not a modelled bore.

The first, unaccepted working study incorrectly extended the omission through the observed near collar. Its bytes/reports are retained in `creative/reviews/passenger-footrest-rubber-jk113008-v1/initial-open-collar-study/`; current source corrects that defect and its gray/material/native96 sequence was repeated. Only the current source is proposed for integration, same one physical ID.

## Evidence and integration limit

Three corrected gray views read before two corrected material previews; four actual native96 views read including independent neutral lighting and explicit underside uncertainty. FLOAT32 multilayer EXRs accompany all native renders. Gray/candidate GLB attributes and indices are identical; actual native/imported GLB oriented triangles/normals are checked independently. Actual Babylon views read, stock native coordinator exemplar passed. No artistic/G8 reception or package completion is asserted.

`passenger-footpeg-metal-v1`/DP161170 is a documented related catalogue dependency. Both authoring axes are longitudinalX, but axial registration, angular clocking, deformation and retaining interface are unknown. No assembly, guessed fit transform or geometry resizing was created. See `creative/research/passenger-footrest-rubber-jk113008-v1/conditional-metal-interface.json` for actual native reads, dimensional mismatches/unknowns and required next views.

Callable builder/stages: `build.py` (`build`, `stage`), using unchanged versioned `powertrain_completion_common_open_v1.py`. `-- build|gray|material|preview|final` is the Blender CLI. Frozen assets must not be rebuilt in place. Flat P16 fragment and delivery are in the review directory. Git/root metadata and historical sources remain untouched.
