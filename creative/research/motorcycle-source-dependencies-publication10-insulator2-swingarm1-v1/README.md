# Recette publique — isolant v2 et corps de bras v1

Audit documentaire en lecture seule des sources existantes. **Aucun maître privé indispensable détecté.** Aucun rendu, modèle, test géométrique, UV ou moteur n’a été relancé ; aucun gel ni README existant modifié. Les empreintes et rôles exacts des dépendances stables sont dans [report.json](report.json). Le `render-report` du bras, encore actif, n’est ni épinglé ni présenté comme une entrée finale de recette.

| Candidat | Entrées réellement lues | Résultat de la lecture |
|---|---|---|
| Isolant v2 — `caa2dcb… /852751f2…`, gel40/revue51 | `build_v2.py` lit paramètres v2, manifeste v1, BLEND v1 `ac925520…`, GLB v1 comme témoin SHA, rapport v1 | Tout est fourni. UV puis deux atlas couleur/rugosité originaux ; aucun maître image privé. Les stries sont du Noise4D W581,404/582,404 mélangé0,7/0,3, bake EMIT2048². Aucun relief normal/bump/displacement appliqué. |
| Bras v1 — `e829f89e… /409a40a9…`, gel26 | Matière depuis G3 `8b16faab… /6ba6cbe3…`, revue grise et métadonnées G3 | Le maître G3 fourni suffit à reprendre la matière avec les JSON publics décrits ci-dessous. Le build intégral utilise les scripts et paramètres publics, sans mesh/photo importé. |

## Reprendre seulement la matière du bras

Dans une **copie isolée**, restaurer les deux binaires de `assets-src/moto-components/swingarm/body/g3-master-v1/` vers les noms actifs du dossier parent, puis restaurer son `source-geometry-check.json` vers le dossier de revue. `material.py` lit aussi `creative/reviews/swingarm-body-v1/gray-review.json` : ce JSON autorise le passage et vérifie les deux empreintes G3. Il est présent, extérieur au gel26 et explicitement prévu dans l’allowlist finale de `record.py`. Le rapport additif en donne le SHA ; aucune modification du gel n’est nécessaire.

Le `geometry-check.json` G3 fourni peut aussi être restauré pour les diagnostics et le protocole de rendu ; il n’est pas lu par `material.py`. Lancer la matière directement sur le candidat PBR actif échouerait volontairement sur l’empreinte G3. La restauration écraserait les chemins actifs : elle n’a pas été exécutée ici.

La matière du bras est générée dans le script : NumPy RNG15009, filtres FFT de travail0,135/1,05mm sur tuile10mm, cartes512², noir linéaire(0,009;0,010;0,012), rugosité0,27–0,33, métal0 et force normale0,25. Ces paramètres sont artistiques estimés, sans maître photo ni mesure de peinture.

## Repartir de la fabrication native

`build.py --stage=full` produit le brut et son rapport à partir des sections, volumes et soudures originaux. `refine_topology.py` consomme ce brut et produit l’étape contractée ; `refine_needles.py` lit cette étape et les rapports générés, en important `authored_normals.py`, puis produit le G3. Le brut et le contracté sont des **intermédiaires régénérables**, pas des maîtres privés à obtenir. Une régénération n’est pas une promesse de `.blend` bit-identique.

Le seul BLEND sous chemin privé, `.../work-in-progress/swingarm/body/needle-refinement-diagnostic.blend`, est **écrit** par la dernière étape et n’est lu par aucune étape suivante. Le dossier de sortie absolu devra exister ou être relocalisé dans une nouvelle recette de travail. Il ne manque pas un maître de géométrie.

## Contexte, diagnostics et environnement

Le bras et son maître G3 n’ont aucune Library externe stockée. L’isolant hérite de la culasse relative : guide de contexte, sans fusion dans son GLB. Le collecteur apparent dans le gel40 sert au contrôle conditionnel d’interface ; `build_v2.py` ne le lit pas pour fabriquer la matière.

Les extractions privées de textures/UV de l’isolant sont des diagnostics produits depuis le GLB par `check_material_export_v2.mjs`, puis lus par le décodeur de pixels. Ce ne sont pas des maîtres de bake. Les photos originales restent des référentiels privés, non lus comme textures par les scripts.

Le CSG du bras invoque le Python hôte via PATH avec manifold3d/numpy ; Blender4.3.2 utilise son numpy embarqué. `requirements.txt` du bras épingle manifold3d et Pillow ; le numpy hôte est épinglé séparément dans `tools/requirements-assets.txt`. Le helper public `tools/blender_component_camera_preflight.py`, importé par le rendu, est hors gel26 et doit accompagner le checkout. Les SHA de ces fichiers figurent dans le JSON.

Aucune revue finale du bras n’est close par cet audit. Aucun clone propre ou déplacé n’a été reconstruit ; les dimensions, l’identité RDC, la matière, la réception artistique et l’iPhone restent hors de cette vérification documentaire.
