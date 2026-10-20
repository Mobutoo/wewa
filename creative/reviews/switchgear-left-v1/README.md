# Revue commodo gauche corrigé v1

Candidat apparentéJB401400 ; variante exacteRDC inconnue, dimensions estimées.

- Source `1d3daa6c33c688e4900ed6870b403e72c6e124b511c9d1184540bcf981e48664` ; export `0a52d32bb408594b055df9aaf381dfca994d5b28a71a41440c459478a28c66ae` ; 15710triangles, glTF0erreur/0avertissement (informations UV/tangentes inutilisées sur matières sans carte).
- `source-geometry-check.json` :7corps rigides connectés, fermés, volumes positifs ; les deux passages de tube sont ouverts.
- `geometry-check.json` : vrais buffersGLB, volumes, rayons de passage, bornes, octets des deux texturesPBR et présence de tangentes.
- `export-tangent-finalization.json` :4tangentes corrigées par dérivées UV réelles ; toutes les aires géométriques concernées>0.  Aucun remplacement arbitraire. Positions/indices/UV/normales, matières et images inchangés bit à bit. Pas de paritéMikk revendiquée.
- `planar-surface-normal-check.json` : fond plan réellement contrôlé, déviation max0,543°/moy0,171° contre38,738°/moy16,532° sur l'ancienne source avec le même filtre.
- `motion-check.json` :9poses explicites du phare/selector/klaxon,0croisement avec les coques. Débattements non mesurés, pas de mécanique électrique qualifiée.
- `clutch-interface-check.json` :6pièces de l'embrayage lié,5poses0–12°,0croisement avec les7corps du commodo. Contrôle de surfaces, pas une certification de tolérance.
- `preview-front.png` : aperçu réel660×600, Cycles24/OIDN ; `front.png`, `quarter.png`, `underside.png`, `material-grazing.png` : rendus isolés1100×1000/Cycles96/OIDN quand présents dans le rapport final. Aucun imagegen ni EXRbrut archivé.

Les défauts de la première vue (slot73%, panneau absent, marquages sous couture, klaxon carré, grandes facettes, noir trop gris) ont provoqué une reprise. Les preuves refusées sont privées dans `/workspace/wewa-assets/work-in-progress/switchgear-left/rejected-front-v1/`. Les proportions/courbes/matière du candidat corrigé sont à recevoir artistiquement, pas déclarées conformes par les tests.

Restent : caméra photographique non calibrée, cotes exactes, varianteRDC, dos/vis réels, faisceau, micrograin mesuré et position des symboles de cette variante. Le pictogramme supplémentaire de la photo liée n'est pas repris comme certitude. Les capturesBabylon sont gérées par la revue commune ; la comparaison source/export sous lumière rasante reste un jugement visuel ouvert. Aucun LOD ni Safari physique testé, G8 en attente utilisateur.
