# 30201069 — correction technique UV cadre v3

Même exemplaire unique : `MOTO-REAR-REFLECTOR-30201069-VISIBLE-STUDY-001`, package `LEGACY15-REAR-REFLECTOR`. Aucun nouveau modèle physique ni variante. [Revue](../../../creative/reviews/rear-reflector-30201069-visible-v3/README.md).

Le source Blender v2 est ouvert puis seuls les UV de boucles des polygones du cadre sont reprojetés dans le plan dominant de chaque face : X→Y/Z, Y→Z/X, Z→X/Y, avec orientation et tuiles stables. 2400 UV de boucles modifiés ; tous les triangles UV ont une aire non nulle. Les index/séparations de sommets de l'export changent sur le cadre. Aucun changement de positions, triangles orientés, normales natives ou exportées, UV de face, matrices ou matériaux. Aucun retrait d'attribut, normale artificielle, normalmap corrective ou réparation GLB après export.

Réexport officiel Blender4.3.2 avec tangentes : face101T max|N·T|=0 ; cadre816T max|N·T|=0.00009984513, seuil strict0.001 pour chaque tangente. Erreur maximale de normeT=0.00006364431 ; W=+1 partout. Face P/N/UV/T et index identiques à v2, texture normale embarquée identique et JSON des deux matériaux exact. Toute la géométrie exportée est comparée par triangles orientés avec leurs normales, sans effacer le sens de parcours.

Deux aperçus réellement lus et pixels identiques à v2, puis trois vues natives96 et EXRfloat32, réouverture du source et Babylon réel. Les dimensions80×50×6mm restent estimées, variante RDC conditionnelle ; dos et quatre interfaces M5/revers inconnus. G4/G5/G8 non reçus, aucun fit ou transport rétro-optique certifié. V1/v2 et anciens manifestes vérifiés inchangés. Aucun Git/root/catalogue partagé.
