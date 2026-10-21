# Source09 — reprise bougie v2 et protection des trois pièces

**Aucune omission concrète d’entrée trouvée** pour la reprise ou son vérificateur d’invariants dans le préflight30. Ses 30 fichiers correspondent aux SHA ; la source est `35648efb…`, le GLB `db4382d7…`, avec 90 696 triangles déclarés par les vrais accesseurs d’indices.

La recette lit huit fichiers : `build_v2.py`, `parameters-v2.json`, `body_geometry_v2.py`, le helper partagé `control_geometry.py`, les BLEND fixes bougie v1 **a797**, capuchon v1 **69dc**, culasse3 **fbbec8**, et **le build-report du capuchon** pour ses noms de maillages. Tous sont couverts. Le garde de bougie v1 du capuchon reste historique ; aucune substitution par la v2.

La reprise conserve le contour de l’hexagone original et ne remplace que le maillage métallique. Le garde source compare les signatures des trois autres volumes, leurs attributs/UV/flags de normales, matériaux simples, parent et matrices ; le datum et la pose du corps sont également vérifiés. Le helper analytique n’ouvre aucun autre fichier et aucun CSG n’est appelé.

## Vérificateur déjà suffisant dans son périmètre

`check_invariants_v2.mjs` et `protected-export-invariants.json` ont été lus. Leurs deux vrais GLB correspondent aux SHA du rapport. Pour rondelle, céramique et borne, le vérificateur compare les indices et **tous les attributs présents** avec type/taille/normalisation/empreinte des octets, puis matériaux simples, matrices locales/monde et parent. Il compare aussi tous les matériaux et le datum.

Une petite lecture indépendante du JSON des deux GLB confirme quatre noms de maillage uniques et **aucune texture, image ou extension de matériau** : aucun état matériel actuel ne tombe hors du périmètre simple de ce garde. Les calculs complets d’accesseurs n’ont donc pas été rejoués. Le rapport distingue cette revue statique des calculs de l’auteur et ne prétend pas avoir exécuté à nouveau son checker.

Le GLB historique v1 est une vraie entrée du vérificateur et figure déjà parmi les30. Aucun brut privé manquant. Pour régénérer v1 elle-même, les quatre entrées d’origine restent couvertes par son préflight25 imbriqué ; cela ne transforme pas cette passe en reconstruction propre exécutée.

Aucun pixel photographique, nouvelle carte matérielle ou générateur extérieur à publier. Aucun catalogue global, ancien audit, gel, mesh ou record modifié.

Les trois finales96 étaient annoncées en file ; le parent a réellement ouvert les macros24 PBR/reflets, pas cet audit. La clôture visuelle des finales reste distincte et non vérifiée ici. Aucune réception artistique, parité visuelle complète du corps modifié ou conformité de montage OEM n’est déduite.

`report.json` conserve les chemins réels, les SHA, l’état Git, les gardes et leurs limites. Audit statique seulement, sans Blender, export, rendu ni nouvelle exécution du checker.
