# Pneu avant — revue de la première pièce

Date : 20 octobre 2026. Direction choisie : [réalisme cinématographique](../../GRAPHIC_STYLE.md). Source : [Blender et paramètres](../../../assets-src/moto-components/front-tyre/README.md). Statut : candidat à reprendre, pas de réception artistique utilisateur.

## Ce qui existe

Une pièce isolée avec section creuse, épaules/flancs/talons, rainures géométriques, UV, caoutchouc procédural et guides d’axes. Un export d’inspection distinct permet le contrôle dans Babylon.js. Aucun conducteur, aucune nouvelle moto globale assemblée et aucun remplacement du modèle public.

Les images `neutral-quarter.png`, `neutral-side.png`, `tread-close.png` et `cinematic-quarter.png` sont des rendus **réels Blender** de cette géométrie. Elles ne proviennent pas du générateur d’images. La [moto seule en style2](../../direction/motorcycle-style-02-generated-reference.png) est, elle, une référence artistique générée ; elle ne démontre pas qu’une moto3D complète existe.

## Comparaison et défauts

| Contrôle | Résultat actuel | Décision |
|---|---|---|
| Construction | Section creuse et rainures intégrées ; source détaillée conservée | Moyen de fabrication disponible, pas une preuve de fidélité à lui seul |
| Normales | Orientation initiale incorrecte détectée et corrigée | Refaire les rendus et contrôler le volume exporté |
| Lumière | Première exposition trop forte détectée ; puissances réduites et rendus neutres/chauds repris | Réponse sombre mieux conservée ; réception visuelle toujours ouverte |
| Sculpture | Crans du premier maillage détectés ; rails du maillage réorientés sur les rainures et ajoutés à leurs bords ; nouveau gros plan examiné, bords continus | Motif et pas OEM restent non confirmés ; pas de réception complète |
| Flanc | Pas de marquages fabricant ni de détail de moule confirmé | À compléter avec une source de pneu identifiée |
| Cotes gonflées | Rayon extérieur et largeur explicitement estimés | Conserver plages ; ne pas annoncer un relevé millimétrique |
| Caméras photo | Quatre arcs relevés, intrinsics et poses non résolus | Calibration multivue encore ouverte |
| Export matière | Rugosité procédurale non reconnue initialement ; approximation explicite à0,60 ajoutée ; micrograin non cuit | Ne pas recevoir le passage matière moteur |

Les comparaisons aux sources sont limitées par les masques de détourage, l’occlusion et la résolution des vues du [manifeste constructeur](../../library/motorcycle-reference-views.json). Le rayon d’un cercle ajusté à un arc n’est pas automatiquement le rayon physique du pneu. Les observations chiffrées sont dans `assets-src/moto-components/front-tyre/reference-observations.json`.

## Suite

Recevoir la direction de rendu de la pièce, résoudre ou borner les inconnues visibles, puis reprendre le calage et la sculpture avant la jante et le moyeu. La moto entière et son conducteur ne sont pas déclarés fabriqués par cette livraison intermédiaire.
