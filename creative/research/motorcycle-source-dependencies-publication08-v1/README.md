# Dépendances avant publication 08 — quatre recettes gelées

Instantané : 2026-10-21T04:06:09.561941+00:00. Vérification statique uniquement : aucun Blender, constructeur, rendu, export ou édition des sources/manifeste/Git. Instruments v4 et soufflets v2 actifs exclus.

| Recette | Fermeture observée | À ajouter au périmètre de dépendances |
|---|---|---|
| Housing v2 depuis gris v5 / core v2 éditable | Fermée par source-freeze 20 + study-freeze 16 | Rien pour cette reprise depuis core éditable |
| Housing : reconstruire le core v2 depuis son origine | Script disponible, chaîne numérique lisible | `build_core_study_v2.py`, `housing-shape-plan-v1.json`, `housing-reliefs-plan-v2.json` |
| Culasse v2 | Les 9 entrées/scripts réellement utilisés sont couverts par préflight 32 / revue 46 | Aucun manque relevé |
| Bouchons de visite v1 | Génération depuis la culasse éditable ; worker CSG transitif oublié | `assets-src/moto-components/front-brake-plate/csg.py` |
| Câbles v2 | Interfaces `.blend` couvertes ; deux lectures JSON oubliées | `creative/workflow/motorcycle-datums-v1.json`, `assets-src/moto-components/ignition-lock/parameters.json` |

Aucun fichier indispensable identifié n’est absent du disque, et tous ceux qui sont déjà cités dans les manifestes examinés concordent à leur SHA. **24 fichiers nécessaires ne sont pas encore indexés Git** à cet instantané ; leurs chemins complets figurent dans `recipe_summaries[].required_files_not_in_git_index` du JSON. Ils existent et plusieurs sont déjà gelés dans un manifeste, ce qui ne les rend pas suivis par Git. Le tableau ci-dessous conserve l’état Git et les SHA exacts des seuls six manques de manifeste.

| Chemin réel | État Git observé | SHA-256 |
|---|---|---|
| `assets-src/moto-components/front-brake-plate/csg.py` | tracked_in_HEAD | `947178b2be8a9a5a0336b619692f62503c9d0921da9cac033e91771343bd707e` |
| `assets-src/moto-components/headlamp/housing/build_core_study_v2.py` | untracked | `aa04bfba4fb104c3ff69cffc3601c1acb64cc6fdc5a1a214a8c2c1c238162609` |
| `assets-src/moto-components/ignition-lock/parameters.json` | tracked_in_HEAD | `69910520fdba65d5e67a28d4e35438bc6dddc47259bf30d887c9305e8b127791` |
| `creative/research/headlamp/housing-reliefs-plan-v2.json` | tracked_in_HEAD | `27c1c4abc5a0860965ac802bd6b6c5e92561537ed694daa9c4aef1e1963b12fe` |
| `creative/research/headlamp/housing-shape-plan-v1.json` | tracked_in_HEAD | `5ffad03b7215e835dc85bed391ed080d4e95a0a1ca44a5b6096bb40bad4d48e8` |
| `creative/workflow/motorcycle-datums-v1.json` | tracked_in_HEAD | `19bf9708f8777b6216ab0c7d487f9ff685e3bedcdd9806f3c9985db78b5e5c9a` |

La chaîne housing complète est : constructeur core v2 + plans forme/reliefs + worker → core éditable/rapport → `add_rear_structures_study_v5.py` + `housing_geometry_v3.py` + plans arrière/contour inférieur + worker → gris v5/rapport/relecture → matière v2. Le gris v5 repart directement de core v2 ; aucune étude grise v1–v4 ou core v1 n’est requise. Le `/tmp/housing-current-debug.blend` est une sortie diagnostique, pas une entrée oubliée.

La culasse remplace la fonction CSG générique par son propre driver/kernel v2. Le worker générique du frein est donc indispensable au bouchon, mais pas à la culasse ni aux câbles. La recette des bouchons prend la culasse gelée comme entrée éditable ; la recette de celle-ci est auditée séparément.

Les JSON `parameters` décrivant une pièce ne remplacent pas une lecture auxiliaire réelle : les câbles vérifient le fichier de datums par SHA puis lisent les paramètres du contact pour le repère de boucle. Ces deux fichiers doivent rester présents même si leurs nombres sont déjà reproduits ailleurs.

Le JSON joint donne les 46 chemins uniques, les neuf manifestes exacts lus, leurs empreintes, les étapes et les vérifications des dépendances déjà couvertes. Aucun pixel de photo privée n’est nécessaire. Les modules externes NumPy/Manifold relèvent de l’environnement `tools/requirements-assets.txt`. Aucune régénération propre ni reproduction binaire n’est déclarée.
