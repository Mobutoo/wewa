# Réservoir WEWA — préparation G0/G1 du lot 18

Recherche du 21 octobre 2026, transmise à B (`lever_visual_audit`), futur propriétaire de la fabrication. **La documentation progresse pour la bouche, les brides et les appuis ; le dessous et les sections métriques restent inconnus.** Aucun modèle, rendu, registre partagé ou fichier source de modèle n’a été modifié.

La cible est le réservoir rouge de la **125 HD à longue visière présentée sur le site RDC**. Le millésime et le numéro OEM du réservoir actuel ne sont pas établis. Le marquage du jeu sera **WEWA**, conformément à la demande utilisateur. Les graphismes et photographies BOXER servent uniquement de documentation privée.

## Nouvelles références réellement ouvertes

Les fichiers restent dans `/workspace/wewa-assets/references/tank18-research-2026-10-21/`. [Le rapport](report.json) et [les archives](archives.json) donnent les URL exactes, empreintes SHA-256, variantes et limites.

| Référence | Ce que l’image montre effectivement | Limite pour la cible RDC |
| --- | --- | --- |
| [52PF1825 rouge, Winter-Summer](https://www.winter-summer.ru/cat3518/1/345614/) — `UG-52PF1825-red.jpg` | Réservoir isolé vu par un flanc et le dessus en oblique : bouche ouverte, deux petites ouvertures proches, bride terminale avec lumière et une oreille percée descendant sous le flanc. | Le code apparaît aussi dans D04 pour BM125 UG 5 vitesses, mais le vendeur annonce BM150 UG. Identité actuelle RDC non certifiée ; aucune vue inférieure. |
| [52PF1763 noir](https://www.winter-summer.ru/boxer_150_ug_plastic/) — `UG-52PF1763-black.jpg` | Autre pièce photographiée dans une direction proche : bouche, couronne et fixations extérieures plus lisibles que sur une moto montée. | Autre finition liée ; ce n’est pas la face opposée du réservoir rouge. |
| [52PF1825, Bajajonline](https://bajajonline.ru/catalog/item/toplivnyy_bak_s_nakleykami_krasnyy_1/) — `UG-52PF1825-bajajonline.jpg` | Même cliché rouge avec davantage de contexte autour de la pièce. | **Même exposition que Winter-Summer**, reconnaissable aux rayures, reflets et graphismes. Aucun contrôle indépendant ajouté. |
| [Appui avant DJ141008, Matriz](https://bajajmatriz.com/producto/goma-tanque-de-gasolina-boxer-150-pulsar-135-neon-180-discover-125-bajaj) — `mount-DJ141008.jpg` | Une face circulaire pleine et une périphérie cylindrique cannelée de la pièce isolée. | Dos/logement, dimensions et orientation montée cachés. Applications multiples ; montage RDC non établi. |
| [Appui arrière JV171001](https://prom.ua/p2564398282-dempfer-toplivnogo-baka.html) — `mount-JV171001-prom.jpg` | Coussin rectangulaire, bords arrondis et relief central avec évidements radiaux. L’étiquette indique **JV171001 / DAMPER TANK REAR**. | Pas de règle, pas de face arrière ni de montage. L’emballage n’est pas une référence dimensionnelle. |
| [Bouchon DS141009, PartOnWheels](https://partonwheels.com/product/cap-fuel-tank-for-bajaj-boxer-bm150-bs3/) — `cap-DS141009-front.png` et `cap-DS141009-oblique.png` | Deux vues supérieures de la coque métallique bombée, de l’ouverture de serrure et du bord avec charnière. | Le vendeur limite l’application au BM150 BS3 2011–2013. **Aucune de ces images ne montre le dessous**, le verrou ou le joint. |

Les autres nouveaux fichiers ont une portée plus faible : le petit recadrage monté 52PF2452 ne révèle pas de face cachée ; le 52PF0590 bleu est annoncé largement « 125–150 » mais accompagné d’une planche X125 ; la seconde image est une planche, pas une deuxième photo de la pièce. Le dessin 99rpm est un éclaté BM150 2011–2013, pas une photographie ni un plan à l’échelle. Les 11 fichiers ouverts ne représentent donc pas 11 vues indépendantes de la cible.

Les manuels constructeur **125 X Kenya, feuille PDF 9 / page imprimée 6**, et **150 HD disponible sur RDC, feuille PDF 10 / page imprimée 7**, étaient déjà archivés : aucun PDF n’a été téléchargé à nouveau. Leurs gros plans montrent le bouchon monté et le robinet séparément. Ils documentent l’ouverture à clé, rotation horaire puis levage, la fermeture par pression et les positions ON/RES/OFF du robinet. Ils ne prouvent pas la variante de coque ou le mécanisme exact de la 125 HD actuelle.

## Décomposition avant toute construction

| Sous-ensemble | Base observable | Ce qui reste à résoudre |
| --- | --- | --- |
| Coque supérieure et flancs | Couronne bombée, épaules larges, flancs pour les genoux, arrondi avant et retour inférieur dans les profils RDC et les obliques. | Largeurs et sections réelles, asymétries, épaisseur et position de la jonction inférieure. |
| Coque inférieure et tunnel | Aucun dessous acceptable de la cible. | Tunnel complet, soudures, appuis, passages et dégagements au cadre. **Construction fidèle bloquée.** |
| Bouche et portée du bouchon | Col circulaire et siège local visibles sur les réservoirs UG isolés. | Diamètre, hauteur, enfoncement, position réelle et entraxe des ouvertures. |
| Bouchon, charnière, serrure et joints | Deux vues supérieures du DS141009 lié et projection grise du bouchon actuel dans les profils. | Dessous, verrou, joint, épaisseurs, course et référence exacte actuelle. |
| Brides et oreilles de coque | Bride terminale, lumière et une oreille percée sur les pièces UG isolées. | Face opposée, sections pliées/soudées et fonction de chaque trou. Une oreille visible n’est pas automatiquement un support au châssis. |
| Appuis et retenue | D04 feuille 53 : DJ141008 avant ×2, JV171001 arrière ×1, rondelle 39105411 et goupille 39098308 ; photos isolées liées. | Logements cachés, compression, orientation montée, entraxes et identité RDC. |
| Robinet et durite | Vues liées et éclatés. D04 : PF171800 ; D15 : PF171802. | Ne pas fusionner ces deux références. Position inférieure, bride, sortie et version actuelle inconnues. |
| Jauge et passage éventuel | D15 feuille 51 montre PF402600 et une fixation à quatre écrous. D04 évoque notamment un joint de jauge UG. | La présence d’un indicateur de carburant ne prouve pas l’interface D15 sous le réservoir actuel. |
| Peinture et marquage WEWA | Direction graphique choisie et apparence rouge brillante de la référence. | Matière à réaliser après la forme ; reflets photographiques et graphismes constructeur ne deviennent pas une texture. |

## Matrice de vues et sections à préparer

Les profils opposés existent **déjà** : R00 montre le côté droit du pilote et R04 son côté gauche. R01/R03 donnent l’avant en oblique, R05/R07 l’arrière. Ces six vues ont été rouvertes. La selle, la colonne et les éléments montés cachent les interfaces. Il manque toujours un dessus perpendiculaire, des faces avant/arrière dégagées et surtout le dessous d’une pièce correctement identifiée.

Préparer les courbes longitudinales de couronne et de retour inférieur, puis des sections transversales **par zone caractéristique** : avant près de la colonne ; passage de la bouche ; épaules et largeur maximale ; creux des genoux ; raccord au nez de selle ; bride arrière. Leur emplacement reste un choix d’échantillonnage, pas une cote mesurée. Construire séparément les deux flancs et les interfaces ; une symétrie parfaite ou une section elliptique répétée ne sont pas démontrées.

Les annotations existantes de `body-powertrain-18/profile-landmarks.json` fournissent des **contours projetés ouverts**, avec leurs propres intervalles de lecture selon le point. Le bord siège/réservoir est une interface de matériaux occultante, pas le contour libre complet de la coque. Les paramètres de `reference-camera-studies` sont des caméras de travail estimées : conserver le résidu R04 du guidon, environ **(+19,4 ; −13,6) px**, sans déformer le réservoir pour l’absorber.

On peut donc borner des écarts **dans les images observées**, préparer la continuité des surfaces visibles et une variante conditionnelle du bouchon. On ne peut pas encore borner honnêtement en millimètres la largeur, la hauteur, la profondeur du tunnel, les entraxes ou l’épaisseur. La capacité publiée de **11 L** et l’empattement de **1285 mm** ne fournissent ni une caméra calibrée ni les sections du réservoir. La durite L185 et les rondelles cotées dans D04 concernent des pièces liées ; elles ne mettent pas la coque à l’échelle.

## Sources écartées et prochaine preuve utile

Le dessous Ensons/Kawasaki déjà archivé a été revu : il demeure **rejeté pour la structure du réservoir RDC**, malgré sa bonne visibilité. Son tunnel et ses brides ne doivent pas remplir les inconnues. Safex présente ici une moto entière comme image principale, pas le réservoir isolé ; ses indications de conditionnement ne sont pas des mesures de pièce. MercadoLibre a répondu HTTP403. La page Teka-Somba obtenue n’expose que l’enveloppe de l’application et un logo générique, aucune photo utile de l’annonce. Les anciens échecs Motokvartal/Pavithra n’ont pas été relancés inutilement.

La prochaine preuve qui ferait réellement progresser la fidélité est **un même réservoir identifié**, photographié dessus perpendiculaire, des deux faces, puis dessous avec une règle dans le plan observé et son code de pièce. Ajouter les appuis séparés et leur orientation montée, ainsi que le bouchon ouvert/retourné. Cela résoudrait largeur par station, bouche, tunnel, fixations et dégagements. En attendant, ces interfaces restent explicitement inconnues ; aucune forme générique ne les clôt.

Cette recherche prépare G0/G1 et la comparaison G2. Elle ne certifie aucune cote extérieure, ne clôt pas G1 pour le dessous et ne vaut aucune réception artistique.
