# Soleil et ombres — expérience v4 exécutée et refusée visuellement

Les deux caméras communes ont produit huit vrais canvas. Le [rapport d’exécution](conservation-report.json) vérifie les 44 entrées inchangées, les deux témoins neutres exactement égaux aux contrôles v2 et la conservation des buffers, matrices, matériaux, caméra et HDR entre W0/W1. Le [contrôle indépendant](coordinator-review.json) porte les six PNG effectivement ouverts par root et leurs empreintes, dont les deux références chaudes Blender.

[Avant sans ombres](front/W0.png) · [avant avec ombres](front/W1.png) · [opposé sans ombres](opposite/W0.png) · [opposé avec ombres](opposite/W1.png)

Les ombres donnent une lecture des intervalles d’ailettes, mais la vue opposée introduit de fines stries courbes sur une grande paroi lisse. Elles sont absentes de W0 avec les mêmes matériaux. Le résultat v4 est donc **refusé visuellement**, malgré des vérifications logicielles réussies. Un examen ciblé du bias et du filtre doit précéder tout nouvel essai. Aucun changement n’est adopté dans le jeu.

La shadowmap occlut uniquement le soleil direct. PCF ne reproduit pas la pénombre Blender à 2°, les unités de lumière ne sont pas photométriquement équivalentes et les différences AgX/ACES, BRDF et HDR demeurent. L’AO haute définition reste suspendue. Aucun rendu composite, réception artistique ni test iPhone physique.
