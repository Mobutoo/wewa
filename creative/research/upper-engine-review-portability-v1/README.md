# Portabilité réelle de l’assemblage haut moteur — v1

**L’assemblage original est portable pour ses sept bibliothèques chargées. Aucun compagnon d’assemblage n’est créé.** Le maître `7c62b0c1752751632318c6c5347cbe6ff2667e463db05e72233b87a6c043eb58` a été copié sans réécriture au même chemin relatif et réellement ouvert dans l’arbre déplacé.

Les **12 copies physiques et7 datums** conservent exactement positions brutes/évaluées, indices, UV, attributs, normales de coins, matériaux/PBR intégrés, parents et matrices. Les sept Library et les propriétaires des12 maillages se résolvent dans le nouvel arbre avec les SHA attendus ; aucun objet/maillage manquant. Le HDR intégré est aussi identique. Les liens vers capuchon2 et bougie2 désignent bien leurs **maîtres originaux**, pas les compagnons portables.

Cela passe parce que cette scène charge uniquement les collections physiques sélectionnées. Les collections de contexte cachées à l’intérieur des maîtres cap2/plug2 ne sont pas chargées ici. Leurs liens absolus internes restent présents lorsqu’on ouvre ces maîtres séparément ; cet audit ne les répare pas et ne remplace pas leurs compagnons déjà livrés.

Le test précédent capuchon13BLEND/18liens n’avait **pas encore ouvert l’assemblage**. Sa fixture fermée est réutilisée, puis quatre fichiers exacts y sont ajoutés : originaux cap2/plug2, embout OHC1 et source assemblage. Aucun ancêtre, registre, catalogue ou gel43 n’est modifié. Le contrôle13/18 et celui des triangles GLB antérieurs ne sont pas rejoués.

`actual-moved-assembly-check.json` contient les deux empreintes détaillées et les vraies Library chargées. Le script `check_moved_assembly.py` réutilise les fonctions d’empreinte de l’outil public de portabilité ; ses chemins source, racines, helper et rapport sont des arguments. Il refuse d’écraser une fixture existante différente. `command.json` donne l’appel réellement utilisé et l’exécutable ; remplacer les racines et le chemin de Blender pour un autre poste.

```sh
blender --background --threads 1 --python-exit-code 1 --python check_moved_assembly.py -- --assembly ASSEMBLAGE.blend --repository-root CHECKOUT_SOURCE --moved-root ARBRE_FERME_DEPLACE --source-proof PREUVE_SOURCE.json --helper portable_library_copy.py --report preuve-ouverture.json
```

Aucun nouveau rendu, export ou noyau géométrique. Aucun test de collision, réception mécanique/OEM, artistique ou iPhone déduit de cette ouverture. Les originaux et le source des rendus restent intacts.
