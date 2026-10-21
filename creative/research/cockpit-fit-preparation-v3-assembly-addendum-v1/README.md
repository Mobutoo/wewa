# Assemblage cockpit v3 — contrôle indépendant

**Les 177 tests ont été rejoués sur le vrai nouveau BLEND : aucun croisement.** Le GLB livré et ses bibliothèques correspondent à cet assemblage. Les anciennes revues v1/v2 et leurs preuves restent intactes.

Source assemblée : `d29ccb05d1c10b638908f5751b962720a84606c12111fe5caee30e465df39b28`.
GLB livré : `6b0b4e3630b0594e4e1e14a1c0f8ede9f0d9f896f18dad5fea24835302fefb53`.

## Recalculé ici

- Les 14 SHA et chemins des bibliothèques chargées concordent au contrat courant. Les 13 lignes hors compteurs et les liaisons sont inchangées. Les neuf corps physiques de compteurs contrôlés utilisent réellement les données de **instruments-v5**, et leurs normales locales correspondent exactement aux sources fraîchement évaluées.
- Les neuf corps physiques C3 et C5 ont les mêmes positions, indices et matrices évalués, bit pour bit. Les normales locales diffèrent exactement sur le cache central et les deux fonds de pods. Cette vérification porte sur les neuf corps impliqués dans le protocole, pas sur les 178 objets décoratifs/structurels du fichier complet.
- Les onze cibles réelles — boucle, visière et neuf corps — ont la même géométrie locale/monde et les mêmes matrices que les anciennes copies v2. Les sources et copies ont été évaluées avec les guides activés en mémoire ; aucune correction de placement.
- Les **85 948 triangles réellement chargés du GLB** correspondent au multiensemble orienté des sources et des nouvelles copies, après dédoublages UV/normales. L’écart maximal de sommet correspondant vaut **33,7703 nm** (seuil numérique explicite : 50 nm). Le petit écart source fraîche/copie de 29,802 nm est conservé, sans prétendre à une égalité binaire de toutes les matrices.

| Contrôle recalculé directement sur la nouvelle revue | Résultat |
|---|---:|
| Paires/poses sélectionnées | 177 / 0 croisement |
| Boucle contre cache central C5 | 0 paire de triangles |
| Segments réels, dans les deux sens | 31 674 / 0 intersection |
| Sommets + centroïdes, trois directions | 31 676 / 0 contenu, ambigu ou frontalier |
| Autocroisements non adjacents de boucle | 0 |

Le minimum échantillonné sommet de boucle → surface du cache reste **3,873598 mm** ; il ne s’agit pas du jeu exact entre les surfaces.

## Réemployé sans nouveau calcul

Le témoin historique **32 paires** est repris de la preuve v2 avec son SHA, **pas déclaré recalculé**. Les algorithmes de segments, d’inclusion à redémarrage de rayon de 100 nm, de comparaison de triangles et les groupes/angles des 177 tests sont repris dans de nouveaux scripts. Les échecs numériques historiques restent dans leur dossier ; cette nouvelle passe n’a rencontré aucun échec. Les assertions artistiques, optiques et de révision sur le fichier C5 complet restent attribuées à leur auteur.

`input-snapshot.json`, `evaluated-source-assembly.json`, `world-geometry-parity-all-references.json`, `current-contact-checks.json` et `independent-spatial-checks.json` conservent les entrées, vrais tableaux et résultats. `delivery-manifest.json` ferme uniquement cet addendum.

Aucun rendu, export, sauvegarde de modèle ou édition des records globaux. Vérification technique limitée : aucun montage mécanique complet, braquage intégral, réception artistique, certification OEM ni essai iPhone physique. Connecteur, câbles supérieurs et faisceau complet restent ouverts.
