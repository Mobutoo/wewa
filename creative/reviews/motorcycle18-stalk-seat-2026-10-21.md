# Deux nouvelles surfaces — tige droite et tampon de selle

La fabrication ajoute deux candidats originaux aux 99 déjà enregistrés :
**101 identités candidates**, toujours distinctes de pièces complètes et des
dix-huit ensembles. Les paramètres préparatoires publiés sont conservés ; les
révisions de fabrication utilisent des paramètres v2 explicites.

| Candidat | Triangles d'inspection | Rendus détaillés | Vues Babylon non vides | Limites principales |
| --- | ---: | ---: | ---: | --- |
| Tige droite PF401002 apparentée | 130 176 | 3 Cycles96/OIDN | 4 | Deux coupes de revue, raccord à la coque et montage ouverts |
| Face de tampon DP211009 apparenté | 95 284 | 3 Cycles96/OIDN | 4 | Revers, tenon, fond et état borgne/traversant inconnus |

![Tige droite sous ciel neutre](indicator-front-right-stalk-v1/neutral-outdoor.png)

[Revue, sources et contrôles de la tige](indicator-front-right-stalk-v1/README.md)

Le profil droit est développé indépendamment de la photo PF401002, sans
réfléchir le maillage gauche. Les trois rainures ont une géométrie à raccords
C2. Longueur, rayons, sections et matière restent des choix bornés. La lumière
de studio et le ciel produisent des réponses différentes du même matériau
original, sans recoloration.

![Tampon sous ciel neutre](seat-damper-v1/neutral-outdoor.png)

[Revue, sources et contrôles du tampon](seat-damper-v1/README.md)

La face possède cinq vallées, un bord extérieur arrondi et une bouche centrale.
Les premiers défauts de normales ont été refusés ; la tessellation corrigée
contraint les bandes jusqu'à leurs intersections avec le cercle. Les deux
parois de présentation finissent à une coupe de 6 mm, qui n'est pas une cote
physique. Aucun revers, tenon ou fond n'est construit, et les sept exemplaires
ne sont pas multipliés avant revue des pièces et des montages.

Les deux fabrications ont chacune suivi la lecture des gris/reflets avant
matière, puis des aperçus studio/ciel et d'une vraie carte diffuse 18 % avant les
rendus détaillés. Les vrais buffers P/N/UV/indices et matrices sont identiques
entre les exports gris et matière. Aucun triangle ou UV d'aire nulle ni erreur
glTF n'est détecté. Les sources, PNG et vingt EXR linéaires FLOAT32 générés sont
sauvegardés, avec les passes brutes et de débruitage vérifiées par en-tête.

Les captures Babylon sont de vrais imports dans Chromium, huit vues non vides
au total et aucune erreur JavaScript ou HTTP. Elles ne prouvent pas une égalité
photographique entre moteurs ni des performances matérielles.

[Rapport incrémental de livraison](../../WEWA_Developpement_Web/validation/motorcycle18-stalk-seat-2026-10-21.json)
· [Tous les éléments visibles](../../LIVRAISONS_MOTO.md)

Le premier jalon de géométrie a été poussé dans `cb709f7`. La livraison détaillée
complète ce jalon. La moto complète, les raccords reçus, les LOD, la réception
artistique et les essais Safari/iPhone restent ouverts ; le conducteur attend
la moto seule.
