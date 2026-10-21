# AO local V2 — localisation du crash, non exécutée

V1 reste intacte : outil SHA `8286b3ed4b2ffc5ec77447c3b5ab18d95ae56f3380a868d0af4f7e768e28119e`. Root a exécuté son `prepare` dans `run-001` et constaté un **SIGSEGV 139**, sans bake. Le journal contient « Read blend » puis l’écriture du crash ; la pile Python du fichier Blender est vide. Cela ne démontre pas encore que l’ouverture a retourné avant le signal. Les traces historiques sont conservées par root, pas réécrites par V2.

Cette variante **séparée** [prepare_upper_engine_local_ao_v2.py](../../../tools/prepare_upper_engine_local_ao_v2.py) installe `faulthandler` sur stderr avant l’ouverture de la source et écrit chaque jalon en JSON avec `flush=True`. Les marqueurs suivent l’ouverture avant/après, la collection et ses douze maillages, chaque lot de témoins, chaque accès brut `foreach_get` avec propriété/type/taille, le graphe évalué, `to_mesh(preserve_all_data_layers=True)`, ses normales, ses tangentes et son nettoyage. La copie locale des données et matériaux, les signatures, l’édition des UV, Smart Project, Pack Islands, le contrôle UV et la sauvegarde ont aussi leurs marqueurs. Les identifiants d’objet et de lot permettent de distinguer témoins initiaux, après copie et après UV. Les boucles par coin ne produisent pas un message par UV.

**Aucun correctif supposé n’est ajouté.** L’ordre des appels de conservation demeure le même ; aucun `view_layer.update()` supplémentaire à l’ouverture, aucune substitution de `to_mesh`, aucun cache de graphe ajouté, aucun abandon des normales ou tangentes. Les fonctions de comparaison exacte, audit d’export, clipping UV et bake sont identiques à V1 par comparaison AST. Les paramètres AO et les contrôles sont inchangés. Aucun seuil n’a été élargi.

Hypothèses à départager, sans cause annoncée :

- Si `prepare.open_source.after` manque, la lecture/liason/évaluation native de la scène peut être en cause ; une ouverture seule dans un processus distinct pourra être décidée par root avant toute copie.
- Si l’ouverture et la collecte passent, la lecture paresseuse de normales ou un `foreach_get` sur les données liées peut être le premier appel fautif. Le dernier jalon nommera la propriété et l’objet ; les vieux audits n’utilisent pas tous ce même accès.
- Un crash dans l’évaluation, `to_mesh` avec toutes les couches, les tangentes ou `to_mesh_clear` est une autre possibilité. `engine-head/check_caps_v3.py` fait une mise à jour explicite du graphe puis `to_mesh()` simple ; le contrôle de raccord du réservoir lit surtout vertices/polygones. Ces différences de contexte ne sont pas une preuve ni un correctif. V2 les conserve comme questions.

Une tentative de résolution des adresses natives sans informations de ligne n’a pas identifié de fonction fiable ; elle ne fonde aucune de ces hypothèses. La trace faulthandler peut aider mais un SIGSEGV peut empêcher l’écriture de `FAILED.json` : **absence de rapport n’est jamais succès**. Les derniers marqueurs flushés et le code de sortie restent nécessaires. Pas de récupération ni de relance automatique.

Après revue du code, root prévoit **une seule invocation** neuve `run-002`, avec stdout et stderr réunis :

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python tools/prepare_upper_engine_local_ao_v2.py -- --phase prepare --spec creative/research/upper-engine-local-ao-diagnostic-v2/spec.json > /tmp/wewa-upper-engine-local-ao-prepare-002.log 2>&1
```

Le spec pointe vers `/workspace/wewa-assets/work-in-progress/upper-engine-local-ao-diagnostic-v1/run-002`. Aucun dossier de dérivé n’est créé par cette livraison. Le script refuse un chemin déjà utilisé. Une éventuelle phase bake reste une décision ultérieure distincte après lecture du résultat de préparation ; cette note ne la lance pas.

Contrôles effectués ici : syntaxe Python, JSON et comparaison AST des fonctions de conservation/export/bake. **Aucun Blender, `main`, bake ou rendu exécuté**. Les API et SHA de sources restent les mêmes que V1. Aucun original, V1, catalogue ou registre modifié.
