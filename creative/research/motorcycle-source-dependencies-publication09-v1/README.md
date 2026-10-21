# Dépendances source09 — culasse 3, raccord OHC et compteurs 5

Instantané : 2026-10-21T04:45:19.706402+00:00. Audit statique uniquement, aucune régénération, exécution Blender, image96 ouverte, édition des gels/records/catalogue ni indexation Git.

| Périmètre | Résultat |
|---|---|
| Culasse v3 | 12 entrées/scripts/helpers/guides réellement utilisés, présents et couverts aux bons SHA par préflight39/revue53 |
| Raccord OHC v1 | 5 entrées actuelles couvertes par préflight24 ; source285eca8f gelée |
| Compteurs C3→C4→C5 | C4 est une vraie dépendance intermédiaire, même hors catalogue. C3.blend et son rapport sont requis par C4 et couverts par le gel C3 séparé ; ils ne sont pas hashés dans les tableaux `files` C5+C4 |
| Cockpit v3 | Builder2, catalogue courant, fichier de liaisons, HDR CC0,14sources éditables et outil de retrait de tangentes inutilisées ; brut et livraison vérifiés. Manifeste global root encore en construction |

## Chaînes à publier selon la frontière choisie

`C3 éditable + rapport → build_v4 + finalize_export_v4 → C4 éditable + rapport/relecture → build_v5 + finalize_export_v5 → C5` est la chaîne exacte des révisions actuelles. Les chemins et SHA sont dans `required_stages` et `construction_input_chain_path_fields_sha_supplement` du JSON. Le champ `construction_input_chain` du gel C5 contient trois chemins sans leurs SHA : ce complément les fournit, sans modifier le gel.

Pour **refabriquer C3**, il faut aussi C2.blend/rapport et la relecture de diagnostic optique. Pour **refabriquer C2**, il faut C1.blend, le USB matériel r2 et sa relecture, le plan de cadran, `v2_artwork_helpers.py` et le finaliseur. La recette USB matériau requiert son gris r2, les plans et les trois PNG originaux ; le générateur de cartes lit deux PNG originaux de miroir. Toutes ces entrées intermédiaires sont classées avec SHA. Les anciennes études USB rejetées ne sont pas requises.

**Limite publique précise :** le constructeur USB gris r2 lit une photo privée uniquement pour en vérifier le SHA. Les pixels ne créent ni maillage ni texture, mais le fichier reste nécessaire pour exécuter ce script inchangé. Ne pas publier cette photo. La reprise depuis un USB/C3 éditable publié reste possible ; prétendre à une recette complète depuis zéro demanderait une révision portable séparée de ce garde documentaire. Aucune modification de ce type n’a été faite.

Chaque constructeur de compteurs produit son GLB brut, puis son finaliseur relit/écrase le même chemin. Aucun brut privé préexistant n’est à publier pour cette opération. En revanche, les vérificateurs comparatifs C3/C4/C5 lisent vraiment les anciens GLB finaux C2/C3/C4 : ils sont listés séparément comme dépendances de vérification. Le cockpit a deux vrais fichiers distincts, `inspection.glb` brut puis `delivery.glb` consommant le brut via `tools/remove_unused_review_tangents.mjs`.

Les ancêtres capuchons/OHC de la culasse3 reprennent la culasse2 éditable et le worker CSG partagé ; cette frontière ancienne est conservée explicitement. Il n’y a pas de boucle de génération culasse3↔raccord : le raccord consomme la culasse3, qui consomme le corps de cache OHC antérieur, pas le raccord.

## État de publication

Le JSON fournit pour chaque chemin son SHA réel, sa présence et son état `tracked_in_HEAD` / `added_to_index` / `untracked` à l’instantané. Les fichiers indispensables courants sont tous présents ; aucun écart de SHA relevé pour ceux déjà couverts par les manifestes examinés. Les tableaux d’ancêtres distinguent les entrées facultatives avec une frontière éditable de celles indispensables à une reconstruction complète.

**Évolution de phase pendant la passe :** le raccord n’avait pas de manifeste final au début de l’audit. Au dernier contrôle, la revue finale du propriétaire apparaît avec **35 fichiers**, tous vérifiés par SHA, et la même source285eca8f/exportd168bf18. La clôture de trois vues96 est donc désormais documentée par B. Cet audit n’a ouvert aucune de ces images et ne transforme pas cette lecture de manifeste en réception artistique indépendante. Le JSON conserve les deux observations successives.

Ni génération propre, ni reproductibilité binaire, ni montage OEM, ni réception artistique déclarés.
