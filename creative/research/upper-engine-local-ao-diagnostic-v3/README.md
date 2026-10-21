# AO local V3 — barrières après libération, non exécutée

V1 et V2 restent intactes et leurs deux échecs sont conservés. Root a exécuté V2 une fois : le dernier jalon est `UV.select_meshes.before`, séquence 1142, puis SIGSEGV 139. Les douze témoins initiaux et après localisation ont terminé ; les UV ont été créés, mais aucun `prepared` blend ni bake n’existe.

Le code **installé** `bpy/ops.py` permet une conclusion limitée mais précise : `bpy.ops.object.select_all()` passe par `_view_layer_update()` **avant** `_op_call()`. La pile montre `view_layer.update()` à cet endroit. Le corps de l’opérateur de sélection n’était donc pas encore exécuté. Remplacer seulement cet opérateur contournerait ce premier point de mise à jour sans expliquer l’état du graphe, susceptible d’être réévalué à l’entrée en mode édition.

La nouvelle variante [prepare_upper_engine_local_ao_v3.py](../../../tools/prepare_upper_engine_local_ao_v3.py) garde faulthandler, les jalons et tous les contrôles exacts. Elle ajoute deux barrières explicites :

1. Immédiatement après chaque `to_mesh_clear()`, supprimer les références Python temporaires `em`/`evaluated`, puis appeler et tracer `bpy.context.view_layer.update()`. Seuls les tableaux copiés et empreintes du témoin restent conservés ; aucune donnée temporaire n’est réutilisée après libération.
2. À l’entrée de `unwrap_pack`, faire une autre mise à jour tracée **avant** de créer ou modifier les UV. `select_all`, sa mise à jour implicite et le passage en mode édition restent inchangés en aval.

L’hypothèse est une invalidation/évaluation paresseuse après les lectures `to_mesh`/normales/tangentes, mise en évidence lors de la première évaluation suivant les UV. **La cause mémoire n’est pas démontrée.** Les API officielles 4.3 et le code RNA v4.3.2 précisent que `to_mesh()` produit une donnée temporaire appartenant à l’objet, qu’elle doit être libérée par `to_mesh_clear()` et que la conservation de toutes les couches requiert un graphe évalué. `ViewLayer.update()` actualise les données marquées. Ces faits justifient une expérience de synchronisation, pas une certitude sur le SIGSEGV.

| Dernier passage observé lors du futur essai | Interprétation limitée |
|---|---|
| Crash à `evaluated.post_release.view_layer_update.before` | La mise à jour échoue avant toute mutation UV à ce stade ; conserver l’objet/lot de témoin, ne pas incriminer le packing. |
| Barrières après libération passées, crash avant retour de `UV.pre_mutation.view_layer_update` | Le graphe reste en échec avant les UV ; aucune sélection de remplacement ne serait un correctif démontré. |
| Toutes les barrières pré-UV passent, puis même crash après les couches UV | L’ajout/mutation des UV ou ses invalidations demeure suspect ; cette synchronisation n’a pas résolu le défaut. |
| Préparation et contrôles terminent | L’expérience a évité cet échec dans ce processus, sans établir seule une cause native ni autoriser un bake ou une réception. |

Les fonctions de conservation/export, leurs clés float32 exactes, le clipping d’intersections et la phase bake sont identiques à V2 par comparaison AST. Aucun seuil de changement ajouté, aucune correction de maillage, aucun abandon de normales/tangentes, aucun patch d’installation Blender. Les paramètres AO et UV restent ceux des deux témoins. Aucune donnée de pièce ou pose n’est reconstruite.

Après revue, root pourra décider d’un seul essai neuf :

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python tools/prepare_upper_engine_local_ao_v3.py -- --phase prepare --spec creative/research/upper-engine-local-ao-diagnostic-v3/spec.json > /tmp/wewa-upper-engine-local-ao-prepare-003.log 2>&1
```

Le spec vise la racine privée neuve `…/upper-engine-local-ao-diagnostic-v1/run-003`. Aucune invocation Blender ou création de cette racine n’a été faite ici. Aucun essai automatique, aucun bake, aucune image. Un SIGSEGV peut empêcher `FAILED.json` ; le code de sortie, le dernier jalon et le crash natif restent la preuve de l’échec.

Le superviseur de `run-002` a seulement reçu un **supplément daté de vérification après échec** des dix entrées : source de revue, GLB, HDR et sept bibliothèques, toutes conformes aux SHA de la spec exécutée. Le JSON précédent est conservé byte pour byte dans `supervisor-before-input-verification-supplement.json`. Script, spec exécutée, journal et crash archivés sont inchangés ; `run-001` n’a pas été modifié. Ce supplément ne prétend pas qu’un contrôle final Python a réussi avant le signal.

Références relues : `bpy/ops.py` installé ; [Object API 4.3](https://docs.blender.org/api/4.3/bpy.types.Object.html#bpy.types.Object.to_mesh), [ViewLayer.update 4.3](https://docs.blender.org/api/4.3/bpy.types.ViewLayer.html#bpy.types.ViewLayer.update), [RNA objet v4.3.2](https://raw.githubusercontent.com/blender/blender/v4.3.2/source/blender/makesrna/intern/rna_object_api.cc). Originaux et SHA des documents sont privés et référencés dans `spec.json`. Syntaxe/JSON et comparaison AST vérifiés uniquement ; aucun `main` V3 exécuté.
