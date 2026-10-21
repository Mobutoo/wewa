# Admission13 — complément axe de pivot et réservoir WEWA

Ce complément laisse inchangée l’[admission13 initiale](../motorcycle-source-dependencies-publication13-v1/README.md). Le [rapport](report.json) vérifie152 entrées SHA de8 manifestes, sans écart. Aucun générateur, rendu, export ou stager n’est exécuté ; aucune fiche, source, recette gelée, table globale ou entrée d’index n’est modifiée. Les finales96 encore actives restent exclues.

L’[axe apparentéJA121003](../../../assets-src/moto-components/swingarm/pivot-shaft/README.md) dispose du source28 et du vrai maître G3. La recette native lit ses paramètres numériques ; la matière produit deux cartes originales normale/ORM par FFT avec graine15180. Sa reprise exige la restauration des deux binaires G3 et de leur contrôle source vers les chemins actifs d’une copie isolée. Le garde `gray-review.json` correspond exactement aux SHA du maître livré. Ce garde, les contrôles courants source/GLB/interface et la lecture de matière courte sont cinq petites entrées stables hors28 à joindre à la fermeture finale. Les images qui y sont citées ne sont pas des textures requises.

Le [réservoir WEWA](../../../assets-src/moto-components/fuel-tank-shell/README.md) repart du vrai maître gris6, de son rapport, de sa lecture bornée, du PNG original et de sa provenance. Cette route PBR n’ouvre aucun maître1–5, aucune photo ni police système. Le SHA du PNG et le SHA des pixels RGB décodés sont vérifiés contre la provenance. La composition WEWA blanche/or est générée depuis la police DejaVu attribuée et des tracés originaux ; aucun graphisme constructeur n’est incorporé.

La publication du source30 **inchangé** impose cependant ses références de gel6 puis4/5 puis3/2/1. La [liste exacte de fermeture](tank-original-freezes-required-closure-v1.json) contient124 fichiers,7 manifestes et154271541octets. Les anciens modèles1–5 représentent104833524octets qui ne servent pas au simple redémarrage depuis6. Root a choisi de fournir cette liste fermée exacte : aucun dossier d’essais n’est aspiré. Les états anciens/refusés gardent cette qualification, sans revendication de reconstruction depuis un clone propre.

Cette fermeture ne sélectionne que trois rasters : l’atlas WEWA, la carte d’exposition diffuse18% et le rendu de contrôle sous ciel neutre. Les deux derniers sont nos images Blender gelées ; leurs empreintes concordent avec les preuves. Les photos et anciennes images privées citées dans les JSON restent des métadonnées historiques, sans copie de pixels. Le HDR neutre est déjà suivi ; aucun fichier `app/` n’est changé.

La [police publique ajoutée séparément](../../../assets-src/fonts/dejavu/README.md) est le TTF exact `ba8db8a1…`,614068octets, avec notice `63d3ba75…` lue et vérifiée. Le TTF public est identique au fichier système et à l’empreinte de la provenance de l’atlas. Sa licence autorise sa redistribution avec les notices et conditions indiquées ; aucun fichier de police n’est modifié. Pour régénérer l’atlas avec le générateur inchangé, fournir TTF et notice aux deux emplacements système qu’il attend, comme l’explique cette notice publique. L’ancienne provenance « binaire non redistribué » reste un état historique et n’est pas réécrite.

## Reprise des finales : seul checkpoint numérique

`render_final_candidate_v1.py` attend un checkpoint des aperçus12 à un chemin privé fixe. Sa [copie publique numérique](replay-inputs/tank-preview-checkpoints-v1.json),19065octets, SHA`c17d77f4ceffb5a484a3090c5e184b04c2923f25647dfbb20b70323e4cf11406`, est **byte-identique** à l’entrée lue. Dans un environnement isolé, depuis la racine du checkout, restaurer uniquement ce JSON avant de relancer la recette gelée :

```sh
mkdir -p /workspace/wewa-assets/work-in-progress/fuel-tank-shell-v1/previews
cp creative/research/motorcycle-source-dependencies-publication13-axis-tank-addendum-v1/replay-inputs/tank-preview-checkpoints-v1.json /workspace/wewa-assets/work-in-progress/fuel-tank-shell-v1/previews/render-checkpoints.json
sha256sum /workspace/wewa-assets/work-in-progress/fuel-tank-shell-v1/previews/render-checkpoints.json
```

Le renderer vérifie les caméras/configurations numériques appariées ; il n’ouvre pas les PNG/EXR privés cités dans ce JSON. Aucun de ces pixels n’est copié. Les chemins, la version Blender, les sources exactes et les dépendances du rendu restent à fournir dans l’environnement de reprise. Cette restauration documentaire ne prouve pas qu’un rendu a été rejoué ni qu’un résultat artistique est reçu.

Les futures fiches et modèles de carter de chaîne, de selle ou autres ne sont pas des dépendances de ce complément et ne bloquent pas son admission statique. Aucun catalogue ou registre global n’est épinglé ici.
