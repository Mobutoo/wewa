# Soleil et ombres — essai v5 exécuté, candidat conservé

Le [rapport d’exécution](conservation-report.json) conserve les huit vrais canvas des deux caméras. Les 72 entrées protégées sont inchangées. Les témoins neutres restent exactement égaux au v2 ; chaque W0 est exactement égal au W0 v4. Les buffers, matrices, PBR, caméra et HDR restent identiques entre W0 et W1. Le [contrôle indépendant](coordinator-review.json) répertorie les huit nouvelles images réellement ouvertes et les références antérieures.

[Avant sans ombres](front/W0.png) · [avant avec ombres](front/W1.png) · [opposé sans ombres](opposite/W0.png) · [opposé avec ombres](opposite/W1.png)

L’unique changement est le bias axial dérivé du grand texel réel : 112,040330647 µm, API0,0009909520912. Le normalBias reste 0,1 mm. Les stries courbes observées dans [v4 refusé](../upper-engine-sun-shadow-v4/README.md) ne sont plus visibles sur la paroi opposée à la résolution native1000×750. Aucun nouveau jour évident entre un contact et son ombre n’a été identifié dans ces cadrages ; cela ne certifie pas les détails sous-pixel.

Le résultat demeure **un candidat de diagnostic, sans adoption dans le jeu**. La lumière et les matières ne sont pas devenues photométriquement équivalentes à Blender ; les creux du warm Blender restent plus doux/sombres. La PCF n’occlut que le soleil direct et non le HDR diffus. Aucun nouveau réglage n’est essayé : le contrôle de coût, des contacts et des ombres reprendra avec les vrais LOD runtime. Pas de réception artistique ni d’essai iPhone physique.
