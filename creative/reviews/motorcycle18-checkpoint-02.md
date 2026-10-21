# Viva Wewa — fabrication moto, point de revue 02

La fabrication des18groupes est autorisée et en cours. Ce point conserve des pièces réellement construites ; il ne déclare ni18groupes terminés, ni une moto reçue, ni un nouveau rendu du jeu.

## Rendus à examiner

![Pontets séparés — Blender réel](handlebar-clamps-v1/quarter.png)

![Portée satinée et grain extérieur — Blender réel](handlebar-clamps-v1/material-close.png)

[Galerie des composants](motorcycle18-gallery/index.html) · [plan détaillé](../workflow/motorcycle-execution-18.json)

Les leviers [embrayage v2](clutch-control-v2/README.md), [frein à câble v2](front-brake-control-v2/README.md) et le [commodo droit](switchgear-right-v1/README.md) ont aussi leurs vues Blender et leur contrôle des mouvements réels dans Babylon. Le [commodo gauche v2](switchgear-left-v2/README.md) reste à reprendre sur le lissage des pictogrammes. Les tests techniques ne prononcent pas la réception visuelle.

## Avancement des18groupes

|Groupe|Fabrication et point restant|
|---|---|
|1 Pontets|Deux unités séparées, vis et goujons ; deux vues finales, portée corrigée. Dimensions/interfaces estimées.|
|2 Support compteurs|v1 conservée ; v2 construite, nervure corrigée, vues finales en cours. Montage actuel non certifié.|
|3 Accélérateur|Manchon et guide séparés, deux vues finales et rotation contrôlée ; poignées v3 construites, vues en file.|
|4 Commodo gauche|v2 en revue ; contours des symboles à lisser en v3.|
|5 Commodo droit|Candidat en revue ; fonction du bouton rouge non identifiée.|
|6 Embrayage|Levier/support v2 en revue ; source nettoyée, course partielle contrôlée.|
|7 Frein au guidon|Levier/support à câble v2 en revue ; aucun circuit hydraulique inventé.|
|8 Rétroviseurs|Miroir gauche provisoire en correction des caches ; source exclue de ce point Git. Droit à fabriquer.|
|9 Contacteur|Source et états de présentation construits ; vues finales en file.|
|10 Câbles|Trois tronçons visibles construits ; affectation de deux gaines inconnue, réseau complet absent.|
|11 Visière|Recherche disponible, fabrication à faire.|
|12 Phare/clignotants avant|Recherche disponible, pièces séparées à fabriquer.|
|13 Fourche/direction|Tube intérieur isolé et té supérieur avec leurs vues finales ; corps inférieur en fabrication, autres pièces à faire.|
|14 Ensemble avant|Pneu, jante et frein préexistants à revoir et à vérifier ensemble ; axe/entretoises à fabriquer.|
|15 Garde-boue/cadre/bras|Recherche disponible, fabrication à faire.|
|16 Roue arrière/transmission/amortisseurs|Recherche disponible, fabrication à faire.|
|17 Moteur/échappement/commandes/béquilles|Carter droit extérieur en fabrication ; autres pièces distinctes à faire.|
|18 Habillage WEWA/éclairage arrière|Recherche disponible, fabrication à faire.|

## Corrections observées et limites

Les pontets ont reçu une vraie correction des secteurs de normales et de la portée ; la comparaison finale porte sur deux PNG de la source figée, relus indépendamment. Les surfaces des leviers ont été conservées pendant le retrait des triangles d’aire nulle et la correction des normales.

La nouvelle inspection des compteurs conserve les quatre rendus historiques à l’identique et corrige la preuve de cadrage dans un dossier séparé. Le contrôle plus strict a aussi révélé8triangles nuls dans quatre marquages du modèle historique ; le capuchon USB reste à corriger. Ces points ouverts ne sont pas masqués par une capture réussie.

Les dimensions publiées de la moto ne donnent pas les cotes de chaque pièce. Les références de variantes liées et les dimensions estimées restent distinguées ; les poses isolées ne certifient pas un montage. Les PNG des pontets sont disponibles sans EXR ; les EXR des autres composants sont qualifiés dans leurs rapports : certains sont linéaires mais déjà débruités, certains conservent des passes brutes privées. Tous ne sont pas des Noisy Image.

Aucun conducteur ajouté. Aucun test physique sur iPhone15/16 réalisé. Les sources d’inspection ne sont pas encore les versions optimisées pour une scène jouable. Le jeu public n’est pas redéployé par ce point de fabrication.
