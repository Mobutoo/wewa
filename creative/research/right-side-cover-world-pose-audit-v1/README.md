# Cache latéral droit : audit de convention vers le repère moto

**Aucune rotation rigide seule ne satisfait arrière +Y, haut +Z et extérieur DROIT −X à partir de ce natif.** Le natif confirme les étiquettes X arrière / Y haut, mais construit une bosse et des normales extérieures vers son +Z. L'association de ces trois directions physiques est de parité opposée au repère global. Ce n'est pas une rotation cachée d'objet ni une raison de copier le cache gauche.

La photo officielle privée `exterior-completion-current/00.png` a été effectivement relue : roue arrière à gauche de l'image, avant à droite. Le générateur exact utilise `x=(432-u)*scale`, `y=(360-v)*scale`. Le natif v1 et le natif v2 rouvert montrent la même coque (empreinte des coordonnées identique), matrices d'objets identité, sommet central `[0,0,+0.023]` et normale quasi +Z. L'étiquette arrière/haut est donc étayée ; remplacer seulement l'étiquette +Z par « intérieur » contredirait le bombé et la tête déjà placée sur la face positive. La profondeur elle-même reste estimée, non mesurée sur la photo de profil.

## Conversion contextuelle possible, sans modifier la source

Avec une translation **T restant à déterminer**, appliquer aux deux objets existants :

```
world = T + (-localZ, localX, localY)
A = [ 0  0 -1 ]
    [ 1  0  0 ]    det(A) = -1
    [ 0  1  0 ]
```

C'est une isométrie impropre de conversion de convention, **pas une pose rigide pure**. Elle conserve longueur/hauteur et place le bombé à droite : sommet relatif `[-0.023,0,0]`, retour relatif vers +X. Elle ne réutilise aucun cache gauche.

Factorisation pour un parent Blender externe : rotation Euler XYZ **[90°,0°,90°]**, échelle **[1,1,−1]**, translation T non qualifiée. L'ordre est d'abord réflexion locale S sur Z, puis rotation propre Q : A=Q·S. Les dix contrôles numériques indépendants sont dans `matrix-check.json`. Si l'intégration exige exclusivement des transformations de déterminant positif, conserver ce parent hors montage : aucune correction silencieuse par rotation n'est possible. Aucun parent de conversion ni dérivé de géométrie n'a été fabriqué pendant cet audit.

Une échelle négative inverse la parité du winding. Les normales doivent suivre l'inverse-transposée ; le moteur doit traiter le culling selon le déterminant. Si une conversion est ultérieurement cuite dans un nouveau dérivé, il faudra traiter winding/normales/tangentes explicitement. Ce dossier ne prétend pas avoir vérifié cette conversion dans un moteur ; activer simplement le double-face ne qualifie pas ces points.

## Objets à intégrer ensemble

Source actuelle : `assets-src/moto-components/side-cover-right-v2/child-candidate.blend`.

- `RIGHT_COVER_OUTER_SKIN` appartient à `WEWA_SIDE_COVER_RIGHT_STUDY`.
- `RIGHT_COVER_LOWER_ROUND_VISIBLE_HEAD_NO_DRIVE_CLAIM` appartient directement à `Scene Collection`.

**Lier seulement la collection nommée perd la tête.** Les deux objets doivent recevoir le même parent de convention et la même transformation globale pour préserver leur placement natif. Aucun déplacement indépendant de tête ni nouvelle fermeture du revers n'est justifié.

## Limites et preuves

`native-read.json` : vrais .blend v1/v2 rouverts, matrices, points, normales, bornes, appartenances et SHA256. `orientation-audit.json` : provenance photo/URL/hash, repères, matrices et alternatives rejetées. `snapshots/` : copies immuables des paramètres, générateurs exacts et preuve de composition déjà existante. Aucun pixel privé redistribué.

La translation T, l'écartement au cadre/réservoir/selle, les attaches et le fit physique restent non qualifiés. Aucun montage wholebike, source, ancien gel, Git ou métadonnée racine modifié ; aucun rendu lancé. Zéro nouvel ID physique et aucune réception G8. Autorité : Coordinator dispatch within user-authorized autonomous motorcycle completion.
