# Dépendances publiques — admission, isolant et collecteur v1

Audit documentaire de la recette, sans fabrication, rendu, modification de gel ou clôture de revue. Les chemins, SHA-256, couvertures exactes de manifestes et état Git local sont dans [report.json](report.json).

**Aucun maître privé de fabrication indispensable détecté.** Les trois photos privées restent des référentiels documentaires : ni `build.py`, ni le bake, ni les vues finales ne lisent leurs pixels. Aucun original à promouvoir pour ces deux recettes.

| Candidat gelé | Chaîne réelle | Entrées de fabrication et guides |
|---|---|---|
| Isolant v1 — source `ac925520`, GLB `14d3eea5`, préflight32 | `build.py`, sections puis CSG et nettoyage | Paramètres publics, helpers `control_geometry`, `topology_cleanup_v2`, `csg.py`; culasse v3 pour datum/interface. Matière constante, sans carte ni maître gris privé. |
| Collecteur v1 — source `428eecbc`, GLB `78fce609`, préflight56 | `recipe.py` → `build.py` → `topology_stage.py` → `material.py` | Paramètres et sections publics; étapes géométrie et topologie fournies avec rapports; isolant v1 et culasse v3 pour datum/interfaces. Deux cartes originales fournies et empaquetées. |

Le grain du collecteur vient d’un Noise4D Blender, W52,18, échelle de travail0,22mm, relief de travail12µm et rugosité0,42–0,56. Ce sont des estimations artistiques, pas des mesures de la fonte. Bake CPU16,2048², NORMAL tangent OpenGL et EMIT, marge12px. Les deux PNG sources sont présents dans `textures/`, liés relativement et empaquetés ; aucun bake depuis une photographie ou un maître externe. `build_v2.py` de l’isolant prépare une autre révision et n’appartient pas à cette recette v1.

Les bibliothèques servent aux datums et contrôles, sans être fusionnées à la pièce exportée. L’isolant montre la culasse dans sa seule vue `conditional-head-context` ; ses quatre autres vues et les quatre vues du collecteur sont isolées. Les13 chemins Library stockés sur11 BLEND de la fermeture conservatrice existent et sont relatifs. Cette lecture statique n’affirme pas que tous les IDs hérités sont chargés : les contrôles existants de résolution courante ne listent que les guides effectivement chargés. Aucun clone déplacé n’a été ouvert.

Quelques limites concrètes restent à conserver :

- `recipe.py` du collecteur utilise le chemin local absolu du binaire Blender4.3.2. Sa provenance et son archive officielle sont documentées ; ce n’est pas un asset privé. Le CSG lance le Python trouvé dans PATH, qui doit avoir les dépendances système du fichier public `tools/requirements-assets.txt`.
- Les tests de pixels lisent des extractions privées sous `work-in-progress/.../exported-v1-textures`. Elles sont produites depuis le GLB public par `check_material_export.mjs`, puis lues par `check_exported_map_pixels.py` : diagnostics régénérables, pas maîtres de matière. Ces chemins absolus limitent leur portabilité. Pillow est importé par ce diagnostic mais n’est pas épinglé dans `requirements-assets.txt` ; le bake lui-même ne le requiert pas.
- `working-packaging-check.json` de l’isolant concerne une ancienne paire `64907498/63acffb7`, pas la paire gelée actuelle. Le script de resauvegarde et l’archive «unrelocated» sont hors recette courante ; ne pas présenter ce diagnostic historique comme correction du gel actuel.
- Les recettes protégées ne se relancent pas sur leur préflight fermé. Une éventuelle reconstruction doit utiliser une nouvelle copie de travail et préserver les gels.

Les SHA des dépendances choisies ont été calculés, mais aucun rendu, fabrication complète, checker de géométrie/UV/Babylon ni qualification iPhone n’a été rejoué. La reproductibilité binaire et la fidélité OEM/RDC ne sont pas reçues. Les manifestes de vues finales restent la responsabilité de leur fabricant ; leur état instantané est relevé dans le JSON, sans clôture implicite.
