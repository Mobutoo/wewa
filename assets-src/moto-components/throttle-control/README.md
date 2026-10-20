# Manchon et came d’accélérateur — candidat v1

La photo voisine DU191003 montre un manchon clair distinct du caoutchouc. La forme cachée de la roue, sa gorge, son siège de câble et le guide ne sont pas lisibles : ils sont construits comme hypothèses estimées, non comme une reproduction constructeur démontrée. La coque externe RH est fabriquée séparément par le lot commodos.

Collection `WEWA_THROTTLE_CONTROL` : datum vide, manchon/roue mobile et guide creux fixe. Repère physique droit −X. Ouverture 0–50° appliquée sur axe local −X (rotation locale X 0→−50°), avec preuve sur un sommet réel se déplaçant vers le pilote +Y, pour inspection, sans course de câble certifiée. Six poses contrôlées sans croisement de surfaces avec tube, poignée v2 et guide. Les jeux radiaux de 0,15 / 0,20 / 0,50 mm sont des paramètres de travail.

Source : [throttle-control-v1.blend](throttle-control-v1.blend), export évalué [throttle-control-inspection.glb](throttle-control-inspection.glb), [paramètres](parameters.json), [provenance](provenance.json), [recherche](../../../creative/research/throttle-control/reference-observations.json). Les collections de guides sont liées en lecture seule et masquées par leur collection locale persistante, hors export et hors rendu isolé.

Chaque volume source est fermé, connexe et positif ; le GLB est contrôlé à partir de ses buffers et possède une animation de rotation. Ces preuves concernent l’intégrité technique. Les matières PBR sont originales et estimées ; pas de photo utilisée comme texture. Aucune réception artistique ou vérification physique iPhone, aucun LOD mobile qualifié.

Construction : Blender officiel 4.3.2 `--background --threads 1 --python-exit-code 1 --python assets-src/moto-components/throttle-control/build.py`. Contrôle : `node assets-src/moto-components/throttle-control/check_export.mjs throttle-control`. Le générateur partagé `throttle-control/control_geometry.py` et le CSG existant `front-brake-plate/csg.py` sont des dépendances ; les deux leviers partagent aussi `clutch-control/lever_builder.py`. Les empreintes du manifeste doivent être relues avant reconstruction.

Les vues finales sont maintenant reprises par checkpoint indépendant : source et configuration effective, PNG et EXR linéaire hachés après chaque vue. Une reprise conserve uniquement les vues vérifiées. Clôture des preuves après inspection :

```sh
python assets-src/moto-components/throttle-control/record_checkpoint_review.py throttle-control
```
