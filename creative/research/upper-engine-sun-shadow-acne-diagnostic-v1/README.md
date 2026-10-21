# Acné d’ombre v4 — diagnostic ciblé et une correction proposée

**Le v4 est rejeté visuellement malgré ses contrôles logiciels réussis.** Les vrais PNG opposés W0 et W1 ont été ouverts ici : W1 ajoute des stries fines courbes sur la grande paroi lisse de culasse, absentes de W0. Root a aussi ouvert les deux directions et les warm Blender. Le [rapport additif](report.json) conserve les empreintes des preuves ; aucun fichier v4, modèle, matériau ou outil n’a été modifié. La notice de décision de revue reste à root.

Les shaders installés **Babylon 9.31.0** montrent deux mécanismes distincts. Le `normalBias` déplace les sommets du caster selon `−N × normalBias × sinθ`, avant projection. Pour une surface localement plane face à la lumière, sa composante suivant la profondeur vaut `normalBias × sinθ × cosθ` : avec 0,1 mm elle atteint au plus **50 µm**, pas un recul constant de 100 µm. La normale vient des sommets importés, pas de la normalmap PBR. La PCF MEDIUM appelle `computeShadowWithPCF3` : quatre recherches bilinéaires pondérées comparent les profondeurs voisines à la même profondeur du receveur, sans correction locale de pente dans cette fonction.

| Grandeur réellement rapportée | Valeur |
| --- | --- |
| Frustum largeur × hauteur | 225,758 × 229,459 mm |
| Profondeur du frustum | 226,127 mm |
| Texel sur le plan de lumière, 2048² | **110,233 × 112,040 µm** |
| Bias axial actuel | 20 µm, soit 0,179 grand texel |
| Bias API actuel | 0,0001768920326, profondeur projetée |
| NormalBias actuel | 0,1 mm monde, effet axial dépendant de l’angle |

À titre d’explication seulement, une pente locale de profondeur1 — 45° suivant un axe de lumière — varie de 110–112 µm entre texels voisins. Les 20 µm constants et jusqu’à 50 µm de composante normale peuvent rester insuffisants. **L’angle réel de la paroi et l’erreur par fragment n’ont pas été mesurés** ; cet exemple ne borne pas tout le support PCF. Le contrôle W0/W1 localise le défaut dans l’activation des ombres ; il ne prouve ni un défaut de normales, ni une cause unique liée au bias. Le format et la précision effective de profondeur ne sont pas établis par ce rapport.

La seule correction proposée pour une future révision séparée est d’augmenter **uniquement le bias axial** de 20 µm à **112,0403306 µm**, soit un grand texel du frustum réel :

`requested_depth_bias_m = max(width, height) / 2048`

Avec la projection actuelle (`projection[10] = 8,844601631`, NDC complet, `BIASFACTOR=1`), le bias API deviendrait **0,0009909520912**. Le normalBias reste **0,1 mm**. Ce choix augmente la marge axiale constante sans accroître simultanément le déplacement latéral induit par la normale. Il est fixé par l’échelle du raster avant toute nouvelle image ; **ce n’est ni une garantie sur toute pente, ni un paramètre déjà adopté**. Un bias plus grand peut décoller des ombres de contact fines.

Le protocole, sans code ni exécution à ce stade :

1. Après décision de root, conserver le v4 intact et préparer une révision additive avec ce seul changement. Garder les deux caméras, source/GLB/HDR, soleil, exposition, PCF2048 MEDIUM, frustum, casters/receivers et normalBias exacts. Aucun AO, fill, sol, matériau ou mesh changé.
2. Exiger encore les témoins neutres égaux au v2, ainsi que le nouveau W0 égal au W0 v4. Recontrôler tous les buffers, matrices et PBR sérialisés. La seule différence autorisée dans la configuration est le bias axial.
3. Conserver **huit vrais PNG séparés** : avant/opposée × neutre v2, neutre v5, W0 et W1, sans composite. Capturer une seule fois W1 avec le bias proposé, pour les deux caméras, puis ouvrir les images originales séparées : W0, ancien W1, nouveau W1 et warm Blender. D’abord vérifier la disparition des stries de paroi ; ensuite les espaces entre ailettes, les contacts tubes/culasse et le logement bougie/capuchon.
4. Lire d’abord à la taille native **1000×750** : aucune nouvelle strie courbe organisée sur la paroi témoin ; aucune nouvelle bande claire séparant une ombre de contact de sa racine d’ailette, d’une jonction tube/culasse ou du contact bougie/capuchon. Refuser si un contact fin disparaît, ou si apparaît un halo, de l’acné ou un éclaircissement injustifié. Une différence ambiguë reste non résolue ; ce contrôle visuel ne certifie aucun seuil physique ou sous-pixel. Stopper et documenter ; cette proposition n’autorise aucune série d’ajustements visuels ni une nouvelle valeur automatique.

Aucune nouvelle capture, aucun navigateur ni Blender lancé. Les différences AgX/ACES, BRDF, préfiltre et occlusion du HDR subsistent. Le succès numérique ne vaudra ni réception artistique, ni qualification iPhone.
