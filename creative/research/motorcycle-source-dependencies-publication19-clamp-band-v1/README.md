# Source19 — recette clamp-band

Base métadonnées43 `a2aa4bc04d5c6fff242de160d806cd4fdc91313b`. Aucun cutoff ou curateurSource19 fixé. [Rapport](report.json), [fermeture](source-closure-v1.json) et [entrées stables](stable-recipe-inputs-v1.json) : **79paires SHA/octets** vérifiées et **41entrées** nommées. Source `3fc41201dc15a252d00f661b9b6abc5083c12bf73ac6926b69ff7b08930e036e` / GLB `43f8260565e55972a8e200124d586c0aac0207b5135774fba3c2d712cd81da6d`.

Band final96 closed/byteverified without openingpixels; no artisticreceipt inferred.

## Construction, matériau et reprise

**geometry** — build.py reads own parameters and shared control_geometry; true csg() calls hostPython front-brake-plate/csg.py using Manifold3D over original temporary operands. Shared modules already source79. Native Blender creates continuous strip/rounded section/formed ears and cuts finite bores. TempCSG JSONs are generated inside TemporaryDirectory, not initial dependencies. Supplied G3 geometryBLEND/GLB/report are actual material-stage masters.

**atlas** — material_atlas.py verifies supplied G3/readiness, creates smart_project UV atlas with explicit nonzero UVguard, protects source positions/polygons/corner normals/matrices, emits uniform witness BLEND/GLB, uniformreport and material-atlas-input.npz. All in79. Exporter may reindex after changed UV; expanded trianglecorner geometry protected.

**color** — generate_original_color.py consumes NPZ+uniformreport+materialparams, uses deterministic NumPy field in authored3D (12 sinusoidal waves/3–9mm estimates), rasterizes in atlas, linearRGB→sRGB8 and SciPy nearestvalid padding. Original1024² PNG+generationJSON provided. No photograph, font, grain, normalmap or angular iridescence input. Microtriangles without texelcentres documented, not collapsedUV.

**material** — material.py opens exact uniform witness, verifies readiness/generation/imageSHA, packs originalcolor sRGB at //relativepath, preserves source snapshot includingUV and writes candidate. Roughness/metallic constant. Current export compared bitexact P/N/UV/index/matrices to uniform witness; this audit reads existing checks, does not recompute.

**uniform_test** — render_uniform_control.py reads uniform-gold-report + uniform-export-check and uses same view/camera/light protocol as render.py, including rakingcontrol. Uniform and mapped24 comparisons are existing author evidence; private previews are optional outputs, not prerequisites. The older diagnostics/uniform-gold-plan-only branch outside79 is not a current witness or required input.

**scratch** — check_protected_export.mjs reads uniform/currentGLB, writes protected-export-invariants.json AND actual-embedded-basecolor.png in private WIP. check_exported_color_pixels.py then reads those generated outputs and publicoriginalPNG. Scratch is an output of the preceding checker; no copy/pinning of private scratch required.

**render** — Current renderer requires currentsource/buildreport/exportcheck/localcamerahelper/checkpointhelper. Final checkpoints optionally resume; absence produces new PNG+halfEXR via helper. No preview checkpoint, HDR or18percentcard required upfront.

**restart_guards** — recipe.py/build.py/material_atlas.py/generate_original_color.py/material.py all refuse an existing preflight-manifest. Preserve original79 unchanged; restart only in a separate unfrozen working copy with its own outputs and reviewed geometrygate. The supplied master/witness/NPZ allow bounded laterstage restart, but guards are not bypassed by this audit. recipe.py also names absolute Blender4.3.2 binary path requiring matching external environment. No clean-clone rerun claimed.

**history** — Frozen79 includes named original lug-overlap diagnostic BLEND/GLB/scripts as required authorhistory; this exact79 closure is distinguished from current recipe use. No additional diagnostic-folder sweep, scratch, old uniformplan-only model or privatePNG copied.

**scope** — BAND and formed ears only. Tangential screw/hardware, inner bridge and installedfit remain separate; ID45/W10 commercialworking values and contrary39 remain unresolved.

Versions hôtes simplement observées : numpy2.3.5, scipy1.17.0, Pillow12.3.0, manifold3d3.3.2. Le lockfileNode existant reste la base. Ces versions ne constituent ni un nouveau verrou d’environnement ni une preuve de réinstallation. Ne supprimer/renommer aucun gel original : les gardes de recette s’appliquent à une copie de travail isolée non figée. Aucune copie de scratch ni checkpoint facultatif admise.

Aucun constructeur, checker, rendu, export ou ouvertureBlender exécuté ici. Les18fichiers des trois auditsSource19 précédents restent byte-identiques ; aucune source/anciengel/globale/Git modifiée. Aucun pixel photographique ou ancien master privé ajouté, aucune nouvelle mesure ou réception artistique/physique revendiquée. Les tables historiques des rapports ne deviennent pas des manifestes vivants.
