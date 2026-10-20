# Contact et clé isolés — candidat

Les trois vues PF232605 montrent le cylindre lisse avant, son rotor fendu, le carter nervuré arrière, les pattes et les clés. La référence est un kit UG5gear voisin ; son identité pour la125HD RDC actuelle est inconnue. Les cotes sont des hypothèses bornées, pas un plan constructeur. [Recherche préalable](../../../creative/research/ignition-lock/reference-observations.json).

Collection `WEWA_IGNITION_LOCK` : quatre volumes de matériel fermés et connexes (corps, rotor, tête de clé, lame) et des géométries planes d’encre originales. La tête et la lame sont séparées par matière, avec recouvrement de fixation intentionnel de la lame dans la tête ; ce n’est pas un code de taille de clé réel ou une serrure fonctionnelle. Le cylindre et les trois états sont contrôlés sans traversée du corps ; le placement au repos ne croise pas les volumes fermés des compteurs.

Le datum sous compteur (0;−0,055;0,019)m et sa rotation(58;0;180)° viennent d’un guide conditionnel fondé sur le manuel150HD lié, sans certifier la125HD. Le pivot `Ignition rotor and key state pivot` tourne autour de son axe localZ ; OFF0°, LOCK−35° et ON45° sont des angles de présentation estimés. Le vrai verrou, les crans, le poussoir de blocage de direction, le câble complet et le brochage ne sont pas fabriqués. Le port USB supérieur n’est pas transformé en contact.

Les mots visibles LOCK/PUSH/IGNITION sont dessinés avec une police ordinaire originale, sans photographies ni logo fabricant. La tessellation de police a produit deux triangles collinéaires : le nettoyage de l’encre plane élimine les triangles nuls tout en conservant les surfaces imprimées. Les contours et trous de glyphes restent ouverts comme une impression, sans exiger un volume de visserie.

[Blender](ignition-lock-v1.blend) · [GLB réel](ignition-lock-inspection.glb) · [paramètres](parameters.json) · [provenance](provenance.json). Reconstruction avec Blender officiel4.3.2,1thread et `build.py`, puis `node assets-src/moto-components/ignition-lock/check_export.mjs` ; `render.py` produit deux vues isolées96/OIDN sous lumière réduite×0,08. Le contrôle renforcé des buffers et les captures du coordinateur sont séparés de la réception artistique. Aucune qualification iPhone physique ou mécanique acquise.

Les vues finales sont maintenant reprises par checkpoint indépendant : source et configuration effective, PNG et EXR linéaire hachés après chaque vue. Une reprise conserve uniquement les vues vérifiées. Clôture des preuves après inspection :

```sh
python assets-src/moto-components/throttle-control/record_checkpoint_review.py ignition-lock
```
