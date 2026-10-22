# Repose-pieds passager — contexte global v2, candidat corrigé v3

**Employer `integration-fragment-v3.json` et `context-material-linked-v3.blend`.** Les fichiers sans suffixe v3 et les rapports `rejected-*` sont des essais refusés, pas des poses installées. Aucun Git, fichier racine, catalogue, board ou source historique modifié. Le complément reste un contexte de donneur apparenté, sans réception G8 ni raccord mécanique acquis.

## Intégration main

Le fragment v3 fournit six parents directs : stay PF113002 LH indépendant, stay PF113003 RH indépendant, deux DP161170 et deux JK113008. Sources, SHA256, objets sélectionnés et matrices monde natives 4×4 sont explicites. Aucun miroir, aucune échelle, aucune nouvelle pièce physique. Ne pas ajouter aussi les trois objets du kit LH historique : ils sont déjà représentés par les trois parents LH du fragment. Ne pas importer les deux SNS de diagnostic dans le whole : main possède ses propres répétitions.

La collection `PASSENGER_FOOTRESTS_GLOBAL_CONTEXT_V2` dans `context-material-linked-v3.blend` contient les six wrappers locaux liés aux vrais maillages/matières historiques. Elle peut être liée une seule fois à l’identité. La scène contient en plus le cadre lié v2 et les deux SNS de contrôle ; ils ne sont pas une deuxième livraison de pièces. Le petit export pair seul est `passenger-pair-material-v3.glb` ; son gris est `passenger-pair-gray-v3.glb`.

Repère natif : mètres, X gauche pilote, Y arrière, Z haut ; matrices rangées par lignes, appliquées aux vecteurs colonnes. glTF `(X,Z,-Y)`. Charnières retenues : LH `(0.150,0.650,-0.555)`, RH `(-0.180,0.650,-0.555)`. Clocking du plan donneur : rotation X monde +90° depuis l’hypothèse Nash ; pegs/caoutchoucs repliés rigidement autour de leurs axes natifs, angles LH−75° / RH+75°. Les stays ne sont pas déformés.

Ces positions **outboard** sont une enveloppe de présentation estimée, pas une cote RDC. La profondeur X est peu contrainte dans les photos. Les bornes de recherche élargies et les alternatives refusées figurent dans les scans v3 ; ne pas reprendre l’ancienne marge ±25mm comme si elle couvrait cette nouvelle hypothèse.

## Sources effectivement lues

Photos officielles RDC03/04/05/07 ouvertes, dont la région passager de04 ; elles montrent la silhouette et le caoutchouc relevé, mais n’identifient ni les quatre centres de fixations des stays ni leur profondeur. Emballages et vues nues obliques PF113002/PF113003 lus ; sources indépendantes apparentées, sans certificat de variante installée RDC. Catalogue BM125 UG, feuille PDF40/planche28 réellement lu et ouvert : PF113002LH×1, PF113003RH×1, DP161170×2, JK113008×2. Les pins/rondelles/goupilles sont des enfants distincts non fabriqués.

`source-register-final.json` publie seulement URL, SHA et observations documentaires. Les pixels des sources et les dérivés de catalogue restent privés. Aucun rendu n’est présenté comme photo de référence. Les sources Blender et les vrais rendus natifs/exportés ont également été lus.

## Contrôles et limites

`collision-audit-v3.json` : zéro paire de triangles en traversée pour chacune des six pièces contre tout le contexte de cadre, airbox, batterie et supports, et contre les deux SNS complets. Les matrices des SNS, déterminants et axes sont consignés : sourceY transversal→+X à gauche, →−X à droite ; sourceZ longitudinal a le même sens sur les deux côtés. Le contrôle porte sur les surfaces, pas sur une certification de volume, de débattement ou de montage. Les distances par échantillonnage sont des diagnostics, pas des minima garantis.

La pose clock0 proche du premier test main laisse le petit terminal à environ217mm LH/210mm RH du cadre. Clock75 rapproche ses centres de surfaces du cadre mais produit des traversées. La localisation révèle une diagonale du cadre à gauche, et surtout la batterie/son support estimés à droite. La première grille X/Y ne résout pas tout ; elle reste refusée. La recherche v3 compare trois clockings75/90/105°, stationsY/Z bornées et choix transversal inboard/outboard. Elle retient des donneurs outboard sans traversée, puis les réouvre et les réévalue.

**L’absence de collision n’est pas un raccord.** `native-reopen-v3.json` mesure les distances des vrais centres de perçages terminaux aux surfaces du cadre : LH environ71/28mm, RH107/72mm. Ces terminaisons ne correspondent pas à des fixations RDC identifiées. La forme planaire et la profondeur du donneur, ainsi que le cadre/batterie eux-mêmes estimés, ne suffisent pas à un montage ajusté. Aucun pin, soudure, pont, adaptateur ou déformation cachée ne comble ces jeux. Une référence montée avec les deux bouts visibles, ou une révision de variante documentée, reste nécessaire pour G5.

Les limites du kit LH gelé restent strictement conservées : décalage5mm entre axes métal/chape, dépassement distal nominal22mm du caoutchouc, coupe diagnostique90° du JK113008. Le repli est un déplacement rigide des surfaces existantes, pas la preuve d’un mécanisme fonctionnel ou d’une insertion. Les modèles, normales, UV, matières et paramètres historiques ne sont pas réécrits.

`export-parity-v3.json` : deux exports stricts zéro erreur/avertissement, zéro triangle dégénéré/non fini ; six instances,649590 triangles. Les vrais buffers de coins indexés P/N/UV et les matrices monde sont identiques gris/matière. Les bornes des sommets natifs évalués et exportés diffèrent au plus de2.78e-8m. `native-reopen-v3.json` vérifie six rotations propres, liens d’origine et empreintes inchangées.

Aperçus gris puis matière v3 ouverts avant finales. Trois vues natives Cycles CPU2,96 samples,1000×800,EXR multilayers32bits, AgX/exposition0/gamma1 et PNG ont été ouvertes : `native-96-v3-LH`, `RH`, `profile`. Le contexte avant du cadre est volontairement recadré ; les pièces passager restent dans le champ. Aucun whole heavy. Deux captures Babylon du vrai GLB pair ont été ouvertes : six maillages,649590 triangles, canvas non vide, aucune erreur page/HTTP ; pas de qualification Safari/iPhone/FPS ou d’équivalence photométrique.

Les échecs de parentage/évaluation et les logs Blender sont conservés. Le premier `libraries.write` avant sauvegarde du même Main provoquait une erreur de validation des noms ; le flux corrigé sauvegarde le natif lié sans ce checkpoint intermédiaire. Aucun contrôle d’un candidat refusé n’est promu en réception. `freeze-v3.json` donne l’inventaire exact final, lui-même exclu de son propre hachage. Les vieux gels ne sont pas modifiés ; G1/G2 exacts, montage G5 et G8 restent ouverts.
