# Admission statique Source14 — recettes des quatre candidats

Base de travail : `620167fd4b7f5fff65e35f0a9d40b82c7c484498`. Lecture des recettes et empreintes, aucun rendu, export ou régénération. Les rendus actifs ne sont pas gelés par cet audit. Les [entrées par phase](stable-recipe-inputs-v1.json), la [fermeture des gels sources](source-closure-v1.json) et le [rapport](report.json) portent des chemins et SHA exacts ; leurs tables sont un relevé historique, pas des manifestes vivants du catalogue.

| Candidat | Gel source | Fermeture imposée | Reprise utile |
|---|---|---|---|
| Pare-chaleur1 | 66 entrées | 66 fichiers, aucun écart | Maître géométrique avec atlas + geometry-report + paramètres → material.py. Silencieux lié et modules fournis. |
| Fixation1 | 71 entrées | 71 fichiers, aucun écart | build.py + fastener_geometry + paramètres ; shader constant. Deux instances d’un type, aucun atlas. |
| Carter supérieur1 | 34 entrées | 34 fichiers, aucun écart | Restaurer les deux binaires gris et le contrôle de source du g3-master-v1 avant material.py. Conserver gray-review.json hors gel34, puis les contrôles actuels pour rendre le PBR. |
| Enveloppe selle1 | 33 entrées | 91 fichiers / 5 manifestes / 92 paires SHA, aucun écart | study4.blend + rapports de source/lecture + trois PNG originaux → build_candidate ; transport des tangentes puis contrôles. |

La fermeture des quatre gels représente 263 paires SHA vérifiées. Elle ne vaut ni réception de forme ni montage ou essai iPhone.

## Entrées à admettre explicitement

Le renderer final de selle lit un checkpoint numérique hors dépôt. La [copie publique](replay-inputs/seat-preview-checkpoints-v1.json) est **byte-identique**, 18981 octets, SHA `e7a54eae959ca3dae0fafef32b32e41edb5e402c1aaa2dd0bee0409359c673b3`. Seul ce JSON a été copié ; aucun PNG/EXR WIP. Dans une copie de travail, restaurer avant rendu :

```sh
mkdir -p /workspace/wewa-assets/work-in-progress/seat-envelope-v1/previews
cp creative/research/motorcycle-source-dependencies-publication14-v1/replay-inputs/seat-preview-checkpoints-v1.json /workspace/wewa-assets/work-in-progress/seat-envelope-v1/previews/render-checkpoints.json
```

Le TTF système exigé est exactement le compagnon public13 `assets-src/fonts/dejavu/DejaVuSansCondensed-BoldOblique.ttf` : SHA `ba8db8a1aba41e53aa1401c1a7fe75d66bb027bf6cd66ecaf8d16af70f590358`, 614 068 octets. La notice système, la notice selle et COPYRIGHT.txt public sont égales. Réutiliser cette police et cette licence aux deux chemins système attendus par le générateur ; aucune nouvelle police à publier. Les PNG déjà livrés sont les maîtres de pixels pour une reprise PBR, sans relancer le lettrage.

Pour le carter, trois petits JSON existants lus réellement doivent accompagner les recettes : `creative/reviews/chaincase-upper-v1/gray-review.json`, `geometry-check.json`, `source-geometry-check.json`. Le premier autorise la matière sur le gris ; les deux suivants servent au renderer courant. Ils sont hors du gel source34. Leurs citations d’images grises restent historiques ; le pipeline ne lit pas ces PNG comme textures. Les outils caméra communs, HDR déjà suivi et compagnon de police sont listés comme dépendances existantes, sans ajouter un catalogue global au gel.

## Maîtres et limites de reprise

La matière de carter écrase les chemins actifs : restaurer `g3-master-v1/chaincase-upper-v1.blend`, son GLB et `source-geometry-check.json` vers les chemins actifs correspondants dans une copie isolée, puis appliquer la matière. Elle n’est pas idempotente sur le PBR actuel. Le pare-chaleur exige également une nouvelle copie sans son garde préflight pour reconstruire ; ses états pré-atlas restent des preuves historiques.

Le gel33 de selle inclut study4, qui inclut les manifestes2/3, lesquels ferment l’étude1. La liste exacte contient **91 chemins et 67 273 281 octets**. Les anciens états1–3 comptent 26,737,338 octets binaires ; ils ne sont pas tous nécessaires pour appliquer la matière au maître4. Ils deviennent néanmoins des dépendances de publication si ces gels inchangés sont admis. Aucun balayage du dossier ni reprise complète de toute origine n’est revendiqué. Les seuls pixels de cette fermeture sont nos trois atlas/cartes originales et nos deux PNG d’éclairage neutre ; aucun pixel documentaire privé.

Le transport selle se rejoue dans l’ordre : build_candidate produit le GLB non projeté, check_candidate écrit son contrôle préalable (puis peut signaler l’orthogonalité), orthogonalize_export_tangents lit ce contrôle et projette Txyz, puis check_candidate et comparaison avec gris4 sont relancés. Le raw GLB WIP et les extractions UV/PNG du pare-chaleur sont **des sorties régénérées**, pas des maîtres privés oubliés. Les EXR restent des sorties/cache.

Aucune CSG n’est invoquée par les deux builders d’échappement malgré une fonction CSG inutilisée dans leur helper partagé. Les bibliothèques réellement liées pare-chaleur/silencieux et tous les modules appelés sont nommés. Chemins absolus des outils et scratchs, versions Blender/NumPy/Pillow/SciPy/Node, garde des gels et arrondis d’export limitent toute promesse de replay : aucun clone propre n’a été exécuté ici.

## Hors coupe

JE591002 n’a pas encore de gel préflight à la lecture de cet audit ; il reste hors de cette admission. Carter inférieur, embase de selle et unités suivantes ne sont pas aspirés. Les sources et les anciens gels restent inchangés, comme l’index et les registres. Seules les sources stables des quatre candidats et la copie numérique autorisée sont pointées ; les finales actives seront admises séparément après clôture réelle.
