# Commodo gauche — candidat corrigé v1

Pièce apparentéeJB401400, catalogueD04UG5gear ; référence exacte125HD RDC non certifiée. Une photo frontale nette et trois petites vues de pièce liée guident ce candidat, sans dimensions physiques relevées.

Source originale éditable : `switchgear-left-v1.blend`, collection `WEWA_SWITCHGEAR_LEFT`. Export réel `switchgear-left-inspection.glb`, 15710triangles. +Xgauche physique, +Ypilote, Zhaut ; mètres. Les cotes et courses sont estimées dans `parameters.json`, les commandes exportées sont dans `controls.json`.

Deux coques creuses indépendantes, joint .3mm, passage de tube ouvert, bossages percés, vis séparées, rocker à deux pentes, sélecteur avec capot/col étroit et poche rectangulaire, langue de klaxon enU. Les surfaces sont des sections originales et des volumes Blender calculés par Manifold ; aucun mesh ou pixel photographique importé. Les lettres et symboles originaux sont projetés sommet par sommet sur la peau. La fente20mm correspond à une proportion photo d'environ40–45% de coque, contre73% dans la version refusée. Les marquages sont au-dessus de la couture.

Polymère sombre : teinte linéaire(.004,.005,.006), rugosité originale à variations déterministes, normal map dérivée d'un champ de hauteur original RMS4µm par tuile10mm. Cette échelle de grain est une hypothèse artistique déclarée, pas un relevé. Les deux textures sont réellement incorporées au GLB et leurs octets vérifiés.

Les booléens/bevels sont nettoyés à2µm ; un essai10µm non fermé a été rejeté. Les corps finaux restent connectés, fermés, à volumes positifs. Le bevel global aprèsCSG est retiré ; les petits rayons sont placés sur les cutters avant découpe. Les angles francs sont marqués avant WeightedNormal. La triangulation évaluée conserve les normales. L'exportBlender laisse 4tangentes nulles sur des triangles non nuls très fins : `finalize_export.mjs` calcule leurs dérivées positions/UV, les projette sur la normale et fixe le signe ; aucune base arbitraire n'est acceptée. Le rapport prouve positions/normales/UV/indices et états matières/images identiques. Cela ne prouve pas une équivalence visuelle exacte avec MikkTSpace.

Reconstruction depuis la racine du dépôt :

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/switchgear-left/build.py
node assets-src/moto-components/switchgear-left/check_export.mjs
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/switchgear-left/check_motion.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/switchgear-left/check_clutch_interface.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/switchgear-left/render.py
```

Blender4.3.2 officiel, Manifold3D3.3.2, NodeIO. Chaque reconstruction change l'empreinte source et invalide les anciennes preuves. Les rendus vérifient les empreintes avant usage et ne sauvent pas la scène modifiée. Cycles96/OIDNCPU ; passes activées mais EXRbrut non archivé.

SourceSHA256 `1d3daa6c33c688e4900ed6870b403e72c6e124b511c9d1184540bcf981e48664` ; GLBSHA256 `0a52d32bb408594b055df9aaf381dfca994d5b28a71a41440c459478a28c66ae`.

[Preuves et limites](../../../creative/reviews/switchgear-left-v1/README.md) ; [recherche](../../../creative/research/switchgear-left/README.md). Aucune réception artistique, qualification physiqueiPhone ou fonction électrique acquise.
