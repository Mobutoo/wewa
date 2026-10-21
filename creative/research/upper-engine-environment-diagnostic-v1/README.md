# Orientation HDR commune — diagnostic indépendant v1

La prochaine correction précise est **`environmentTexture.rotationY = +Math.PI / 2`**, dans une nouvelle variante de l’inspecteur uniquement. Aucune bascule supplémentaire de Y/Z, matière ou pièce n’est indiquée. La caméra commune est déjà un contrôle distinct.

Cycles 4.3.2 échantillonne son environnement Z-up selon `u = ½ − atan2(y,x)/(2π)`. Notre conversion d’objets vers glTF donne `(x,z,−y)`. Dans Babylon 9.31.0, il faut encore tenir compte des axes des six faces du convertisseur RGBE, de son inversion de lignes, de l’ordre d’upload et du `REFLECTIONMAP_OPPOSITEZ` activé en repère droit. Avec les flags actuels et la matrice identité, le panorama est alors lu **un quart de tour plus loin**. La matrice Babylon `RotationY(+π/2)` annule cet écart ; le haut reste le haut. Cette matrice agit sur le sampling, pas sur la pièce.

Six rayons CPU, dont deux obliques, ont été confrontés au vrai décodage Babylon du HDR 1024×512 et au cube 256 non préfiltré. Ils retrouvent cet écart d’azimut, puis son annulation dans les formules. Le JSON conserve les directions, UV, valeurs échantillonnées, URL/code exact et empreintes. Ce contrôle **ne valide pas le GPU ni le cube préfiltré runtime** : les deux captures réelles prévues par le coordinateur restent nécessaires, à caméra et matières inchangées.

Les quatre images de comparaison ont été réellement ouvertes. Babylon présente des surfaces d’ailettes éclairées plus uniformément ; cela ne désigne pas une cause unique. Les différences restantes sont indépendantes :

- **Affichage :** AgX Medium High Contrast et ACESFitted ont des transformations différentes. Un même EV, ou `contrast=1`, ne les rend pas identiques. La carte grise a été rendue dans Cycles seulement ; la copie de son facteur d’exposition n’étalonne pas Babylon.
- **Intégration :** Cycles trace le ciel et la géométrie ; Babylon utilise un cube préfiltré, une BRDF d’IBL et un polynôme sphérique pour le diffus. Filtrage, débruitage à 12 spp et stockage ne sont pas une preuve de parité.
- **Visibilité :** le lab n’installe ni occlusion de scène ni ombres du HDR sur les ailettes. Les 12 matières du GLB n’ont aucune `occlusionTexture`. La rotation du ciel ne peut recréer ce facteur de visibilité manquant ; il faudra l’examiner séparément, sans assombrir l’albédo pour le masquer.
- **Fond :** le fond caméra Blender transformé par AgX et le `clearColor` Babylon suivent des chemins différents ; ils ne sont pas une référence de couleur.

Les sources Blender consultées sont le [manuel environnement 4.3](https://docs.blender.org/manual/en/4.3/render/shader_nodes/textures/environment.html), [Cycles projection.h v4.3.2](https://raw.githubusercontent.com/blender/blender/v4.3.2/intern/cycles/kernel/camera/projection.h) et [svm/image.h v4.3.2](https://raw.githubusercontent.com/blender/blender/v4.3.2/intern/cycles/kernel/svm/image.h). Les fichiers Babylon 9.31.0 installés, l’OCIO local et les outils existants sont référencés avec SHA dans `report.json`. Les archives documentaires restent privées.

Aucun nouveau rendu, modification de source/GLB/matière, outil existant ou galerie. Aucune réception artistique ni parité photométrique annoncée.
