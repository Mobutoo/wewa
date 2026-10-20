# Repères d’assemblage — aucune pièce fabriquée

`datum-guides-v1.blend` contient uniquement des axes/traits et des repères masqués au rendu. Les positions relatives au centre du guidon et les rayons extérieurs restent estimés ; seule la séparation des axes est contrainte à l’empattement publié1285mm. Ces guides ne sont pas une calibration de caméra ou un modèle de moto.

Repère : +X gauche du pilote, -X droite, +Y arrière/pilote, -Y avant, +Z haut. La conversion glTF est `(x,z,-y)`. Les sources historiques roue/pneu ont leur centre enZ=.29 ; leur déplacement candidat vers l’avant du repère cockpit serait `(0,-.42,-1.03)`, à vérifier avant montage. Aucun déplacement historique n’est appliqué.

[Contraintes et incertitudes](../../creative/workflow/motorcycle-datums-v1.json) · [script reproductible](../../tools/build_motorcycle_guides.py).
