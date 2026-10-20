# Commodo gauche — révision v2, marquages documentaires

Cette révision remplace les pictogrammes génériques de la v1 par des courbes originales suivant la photo documentaire liée JB401400. Les deux phares ont cinq rayons et un contour en D ; le klaxon a un pavillon allongé et une boucle ovale ajourée. La variante exacte du commodo RDC actuel reste inconnue. La v1 et sa documentation restent historiques.

Source : `switchgear-left-v2.blend`, SHA256 `657ecbdb13f48f9eb59a354ed7ebfba2ab05a7ac7d6b6e7c7ced8cb33b610ea4`. Export : `switchgear-left-v2-inspection.glb`, SHA256 `145a1464a83b0454eb2116e0c8b18cd51c972a9c5b74d5e5ca08624b2bd8f1d3`. Collection : `WEWA_SWITCHGEAR_LEFT`. Contrat des commandes : `controls-v2.json`. Provenance propre : `provenance-v2.json`.

Les dix anciens objets de pictogrammes sont remplacés par trois maillages d’encre, dérivés de contours Bézier éditables dans la collection masquée `LH editable photo-traced symbol curves v2`. Aucun pixel photographique ni numéro de fabricant n’est utilisé comme texture. Les dimensions et le placement des marquages restent estimés, sans calibrage photographique.

La preuve `creative/reviews/switchgear-left-v2/annotation-only-change-check.json` compare les buffers réels : les sept corps rigides, TURN et les deux flèches ont des positions, normales, UV, tangentes utiles, indices, matières, images et transformations identiques à la v1. Les commandes restent identiques. La source est aussi comparée avant/après. Les preuves de corps et d’interfaces v1 restent applicables à ces corps inchangés ; cela ne vaut pas réception artistique.

Le contrôle `glyph-structure-check.json` teste les maillages réels par rayons : cinq traits par phare, quatre espaces entre eux, intérieur des D et boucle du klaxon vides. L’encre n’est pas qualifiée comme un solide mécanique. Les tangentes inutilisées des matières sans normalmap sont absentes de l’export. Le validateur glTF ne trouve ni erreur ni avertissement (16 414 triangles).

Les vues ciblées réelles se trouvent dans `creative/reviews/switchgear-left-v2/`, avec leurs réglages et leur présence effective dans `render-report.json` : Cycles 96 échantillons, OpenImageDenoise CPU, 1100×1000. Les anciennes vues de corps restent dans leur dossier v1. Les captures moteur relèvent de la revue commune. Pas de réception de fidélité artistique, électrique ou sur iPhone physique acquise.

Reproduction depuis la racine du dépôt :

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/switchgear-left/build_markings_v2.py
node assets-src/moto-components/switchgear-left/check_export_v2.mjs
node assets-src/moto-components/switchgear-left/check_annotation_diff_v2.mjs
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/switchgear-left/check_glyphs_v2.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/switchgear-left/render_markings_v2.py
```

Le script de traçage `trace_markings_v2.py` demande la photo originale privée pour régénérer les seuls vecteurs documentaires. Le build exploite le registre vectoriel déjà présent et n’exige pas cette photo privée.
