# Moto extérieure v5

[Images, inventaire et état réel](../../../creative/reviews/motorcycle-exterior-v5/README.md).

`motorcycle-exterior-v5.blend` relie les sources originales de 177 groupes. Le [manifeste portable](../../../creative/research/motorcycle-exterior-v5/portable-files.json) énumère les dépendances avec leurs octets et SHA256 ; les chemins restent relatifs au dépôt. Le [glTF détaillé](../motorcycle-exterior-v5.gltf) lit les buffers d’origine sans les recopier. `lod/motorcycle-lod.glb` est une dérivation autonome pour la revue.

La [préparation](../../../tools/prepare_motorcycle_exterior_v5.py), la [liaison native](../../../tools/build_motorcycle_exterior_v5.py), le [compositeur glTF conservé](../../../tools/compose_motorcycle_gltf_v1.mjs) et le [générateur LOD v2](../../../tools/build_motorcycle_lod_v2.mjs) décrivent la reconstruction. L’assemblage reste statique et comporte des poses estimées et interfaces ouvertes ; il ne remplace pas le modèle du jeu.
