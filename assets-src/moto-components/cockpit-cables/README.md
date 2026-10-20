# Tronçons visibles de gaines — candidat partiel

Trois volumes creux sont construits : deux gaines descendantes visibles près de la fourche gauche et le petit départ en boucle du contact PF232605 lié. Les fonctions des deux gaines restent inconnues (frein/compteur non départagés), leurs extrémités libres ne sont pas raccordées au moyeu. Le passage caché sous phare, le faisceau complet, les prises, brochages et colliers non identifiés restent absents. Les coupes annulaires ferment la paroi du volume de gaine ; elles ne représentent pas des bouchons ou terminaisons usine.

Le tracé natif de la rotation04 est conservé dans les [paramètres](parameters.json). L’empattement fournit un guide de projection YZ provisoire ; il ne calibre ni la caméra ni le diamètre local. La profondeurX, les diamètres et les sections sont estimés. Le petit faisceau du contact reprend sa boucle visible en photo liée avec un parcours3D estimé, sans prise fabriquée. Le rayon de courbure calculé est une observation de ce candidat, pas une limite fabricant.

Collection `WEWA_COCKPIT_CABLES_PARTIAL`, trois maillages séparés, sans animation de braquage ni transmission mécanique. Les contrôles vérifient connexité, fermeture de paroi, volumes, absence de traversée entre les trois gaines et avec le corps du contact. Ils ne prouvent pas le jeu au braquage, l’affectation ou l’installation réelle. [Recherche](../../../creative/research/cockpit-cables/reference-observations.json).

La source utilise le repère partagé +Xgauche,+Ypilote,Zhaut ; origine guidon. Les photos ne sont pas redistribuées et ne fournissent aucun pixel de texture. PBR de polymère noir original, sans relief photographique. [Blender](cockpit-cables-v1.blend) · [GLB](cockpit-cables-inspection.glb). Aucun harnais complet, aucune compatibilité JA/DS ou réception artistique et aucune qualification iPhone physique déclarés.

Les vues finales sont maintenant reprises par checkpoint indépendant : source et configuration effective, PNG et EXR linéaire hachés après chaque vue. Une reprise conserve uniquement les vues vérifiées. Clôture des preuves après inspection :

```sh
python assets-src/moto-components/throttle-control/record_checkpoint_review.py cockpit-cables
```
