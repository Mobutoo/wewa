# Embout métallique du couvercle OHC — candidat conditionnel

`MOTO-ENGINE-OHC-STUB-001` représente uniquement le tube métallique court visible sur les deux photos attribuées au couvercle apparenté **52JV0145**. Le corps moulé du couvercle reste une autre source inchangée. Aucune identité exacte RDC, cote de montage ou réception artistique n’est revendiquée.

La [préparation documentaire](../../../creative/research/engine-ohc-stub/fabrication-plan-v1.json) distingue le fût droit et l’unique bourrelet terminal observables du diamètre intérieur, de l’insertion et du métal estimés. Les photos privées ne sont ni distribuées ni utilisées comme textures. La fonction et la méthode de fixation ne sont pas certifiées.

Le modèle utilise un profil de révolution continu : paroi tubulaire fermée, lumière centrale ouverte aux deux bouts, vrais arrondis et relief annulaire. Le tronçon fin placé dans l’alésage est une estimation cachée, sans filetage inventé. Aucun deuxième collier visible de pied n’a été ajouté. Les paramètres et leurs bornes restent dans `parameters.json`.

Le repère local X suit l’axe sortant du siège provisoire déjà présent dans le couvercle ; Y/Z sont radiaux. Le zéro du siège n’est pas la surface extérieure : le sondage du maillage existant place la paroi plus en dedans. Le tube est construit sur ce raccord candidat sans déplacer ni retailler le couvercle. Ce contrôle ne devient pas une mesure du produit réel.

Sources : `engine-ohc-stub-v1.blend`, collection `WEWA_ENGINE_OHC_STUB`, objet identifié dans `build-report.json`, datum `OHC metallic stub inherited provisional seat datum`. Les bibliothèques liées servent uniquement au contrôle ; le GLB `engine-ohc-stub-inspection.glb` exporte le tube et son datum seuls. C’est une source de revue détaillée, sans budget LOD mobile reçu.

Reconstruction : Blender4.3.2, un thread, `build.py`, puis `node assets-src/moto-components/engine-ohc-stub/check_export.mjs` depuis la racine. `check_interface.py` vérifie les maillages évalués sans sauvegarder les bibliothèques. Les distances aux sommets sont des échantillons et non un jeu minimal exact. Les désaccords numériques BVH sont consignés et doivent être résolus par trois intersections directes float64 unanimes ; aucune majorité ne valide un raccord.

`render.py -- --preview --gray`, `--reflection` ou `--preview` produit des diagnostics courts privés. Les vues finales96 sont scellées uniquement après ouverture effective des PNG ; chaque vue garde source, configuration, PNG et EXR hachés. Métal PBR constant original, sans grain ni rugosité prétendument mesurés. Lumière, face cachée, diamètre intérieur et cote du bourrelet restent à examiner.
