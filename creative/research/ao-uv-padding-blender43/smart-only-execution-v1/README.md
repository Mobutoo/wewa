# Smart Project seul — mesure exécutée, addendum

Root a réellement exécuté une fois l’outil dans Blender4.3.2, en environ30s, code de sortie0. [measurement.json](measurement.json) est la **copie binaire exacte du seul petit JSON numérique** produit, sans BLEND rejeté, gros rapport d’anomalies ou archivegz. Les documents de préparation précédents restent historiques ; cet addendum décrit le résultat exécuté.

SHA-256 du JSON : `c8a29842955402d4ee9ef63595c6163404500c4422f1e75747850d36cd982b31` ; taille150595octets. Outil exécuté : `8e1b46eb3ab75dcefb0f9e267735d93005087d45cdf02a2850da838cc018440e` ; copie rejetée épinglée : `7017d79d4fb8d8279ba544173e0d9b3586346af90da2d59267d5ecf3c3ea0e25`.

| Compte sur12maillages,657316triangles | Copie rejetée | Après SmartProject66°/marge0 seulement |
|---|---:|---:|
| Triangles UV à zéro exact | 637656 | 88 |
| Union stricte des anomalies | 644312 | 113 |
| Zéros sur petites faces locales≤1e-12 | 65 | 65 |
| Zéros sur faces locales au-dessus de1e-12 | 637591 | 23 |
| Îlots par continuité exacte des arêtesUV | 1840 | 1840 |

Le compte optionnel d’îlots a été réellement exécuté :1840 dans chaque état, dont1169 pour la culasse ; couper aussi les arêtes marquées couture donne le même total. Ce comptage topologique ne prouve pas l’absence de recouvrement ni la place disponible après padding.

Après Smart Project,25triangles restent hors[0,1] ; aucun triangle non fini. Les582496faces comprennent65faces locales≤1e-12. Les65zéros correspondants sont compatibles avec le traitement explicite de ces petites faces dans le code officiel. Les23autres zéros sont tous dans la culasse et ne sont pas expliqués par ce seuil ; aucune cause plus précise n’est affirmée. La distinction entre faces et triangles reste conservée.

**L’atlas n’est pas valide.** Les seuils n’ont pas été relâchés : les nombres aireUV≤1e-18 et déterminant absolu≤1e-18 sont rapportés séparément, avec la même union stricte d’anomalies que le contrôleur. Les empreintes de géométrie, normales par coin, tous les UVhorsAO et les fichiers sources protégés sont exactement conservées. Les couchesUV0 de remplacement sont également restées intactes pendant ce diagnostic.

## Portée causale

Le probe réactiveUV_AOindex1 sur les12copies et **sélectionne explicitement les UV avant Smart Project**, alors que la séquence initiale ne les sélectionnait explicitement qu’après. Il repart aussi de la copie rejetée ; ce n’est donc pas une ablation strictement identique de la pipeline initiale. La forte différence rend plausible une dégradation dans les étapes ultérieures/de packing, mais ne démontre pas à elle seule que FRACTION est l’unique cause des637656zéros initiaux. Smart Project contient déjà son propre packing.

L’outil est revenu enOBJECT avant tout deuxième pack/bord. Il n’a effectué aucun bake/export/sauvegarde ni réparation de source. La mesure ne valide aucune AO ni réception graphique. Root suspend cette AO sur les hauts maillages jusqu’aux vrais atlas de LOD ; **aucun nouvel essai de seuil ou de packing n’est préparé**.
