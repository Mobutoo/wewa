# 30201069 — correction matièrev2 du même exemplaire

**component_id `MOTO-REAR-REFLECTOR-30201069-VISIBLE-STUDY-001` ; package `LEGACY15-REAR-REFLECTOR`.** Identité de coordination demandée : le codeLEGACY15 de v1 désigne le même exemplaire. Ce dossier est une révision de matière, pas une deuxième pièce ni une variante.

[Revue](../../../creative/reviews/rear-reflector-30201069-visible-v2/README.md) · [FragmentPLAT](../../../creative/reviews/rear-reflector-30201069-visible-v2/component-fragment.json) · [Plan avant travail](../../../creative/research/rear-reflector-30201069-visible-v2/material-plan-v2.json).

Le sourcev1 est ouvert sans reconstruction, puis la face seule reçoit une interprétation de matériau originale : rangées décalées de plages diagonales, normale1024² produite mathématiquement, couleur linéaire uniforme et réponse spéculaire rouge effective. **Aucun pixel de la photo n’est utilisé.** Ces valeurs ne sont ni un albédo mesuré, ni des normales optiques relevées, ni des prismes reconstruits. Aucune modification/correction du mesh par normalmap.

Empreintes natives avant/après et réouverture : **face et cadre positions/triangles/normales/UV/matrice exacts**, ainsi que matériau du cadre. Les buffersGLBv1/v2 ont également des écartsP/N/UV exactement0, séparément face/cadre. Les dimensions80×50×6mm estimées, coupe arrière et inconnuesRDC de v1 restent inchangées. Aucune pose/montage.

Le diagnosticG2 teste d’abord v1inchangé : ancienangle, hypothèseangle/roulis de source, sourceslarge/ponctuelle, puis correction de roulis. Seulement après lecture du diagnostic : matière, deux aperçuslus, trois vues96lus dont neutre, réouverture et runtime. Les essais refusés trop noirs ou trop ronds sont conservés en revue/rejected-material-attempt-a/b, comme historiques du même exemplaire.

Une seule texture est exportée : `original-staggered-cell-normal.png`, hash vérifié dans leGLB. L’imagecouleur originale d’un essai antérieur reste générée/stockée et son nœud non relié dans le source, **sans utilisation dans la matière actuelle ou leGLB**. BaseColoruniforme100%auteur ; paramètres effectifs exportés documentés, pas de métrologie duJPEG.

La face utilise TEXCOORD0,100trianglesUV non aplatis et101tangentes finies/unitaires/orthogonalesN·T=0 avec W±1. Les UV et tangentes du cadre héritésv1 restent inchangés ;200trianglesUV sans aire y sont inutilisés car ce matériau n’emploie aucune normale/texture. Limite documentée, sans dissimulation ni remise en forme.

G4reste **à revoir/non reçu**, G5interfacesbloquées, aucun fit/G8 ou qualificationiPhone. Les quatreinterfacesM5/revers restent inconnues. Sourcefigure sans dos/goujon/prismes/marquages. Sourcev1+manifestev2 préservésSHA. Aucun Git/root/cataloguepartagé modifié.

Les scripts sont propres à cette révision. `prepare_material_v2.py` est le provisionnement initial historique, pas à relancer sur le gel. `material_pipeline_v2.py` charge les paramètresv2courants, jamais un buildergéométrique ; `check_material_parity_v2.mjs` décode les exportsréels ; `reopen_source_v2.py` vérifie le sourcepersisté. Manifeste en revue, tous fichiersgelés0444.
