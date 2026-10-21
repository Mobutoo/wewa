# Lot 18 — passage documentaire à C : réservoir puis selle

**Les formes extérieures disposent de vraies références ; les dimensions et interfaces cachées restent ouvertes.** Ce dossier rassemble les preuves utiles pour les deux premières futures pièces, puis une matrice courte du reste du lot18. Le [rapport JSON](report.json) donne les URL, empreintes, vues réellement ouvertes, variantes et prochains relevés. Aucun modèle, galerie, recette gelée, ancien rapport ou registre modifié.

La destination courante est **C (`instrument_references`)**, selon la mission root. L’[ancien dossier réservoir](../tank18-preparation/README.md) et l’inventaire arrêté mentionnent B : ces documents historiques restent intacts. Une seule durite réservoir→carburateur relève de C18 ; l’arrivée/carburateur et les évents/vidange restent B17.

## Première pièce : réservoir

La cible est le rouge de la 125HD longue visière du [site RDC](https://www.bajajauto.com/fr-cd/bikes/boxer-125hd), avec futur graphisme **WEWA original**. Son code OEM et son millésime sont inconnus.

| Preuve rouverte | Usage concret | Limite |
| --- | --- | --- |
| R00 droit / R04 gauche | Couronne, retours inférieurs, profils opposés et raccord au nez de selle | La selle occulte l’arrière ; pas de sections transversales cotées |
| R01 / R03 avant oblique | Épaules et courbure avant | Colonne, cockpit et phare masquent des interfaces |
| R05 / R07 arrière oblique | Retour vers l’assise et volume arrière | Ni tunnel inférieur ni arrière de coque dégagé |
| [52PF1825 rouge isolé](https://www.winter-summer.ru/cat3518/1/345614/) | Bouche ouverte, deux petites ouvertures proches, bride terminale à lumière et oreille percée visibles | BM150UG vendeur, code également D04 BM125UG5 ; **montage courant RDC non certifié**, une seule face oblique |
| [52PF1763 noir isolé](https://www.winter-summer.ru/boxer_150_ug_plastic/) | Autre finition, bouche et couronne lisibles | Autre exemplaire, **pas face opposée du rouge** |

Les originaux isolés sont `UG-52PF1825-red.jpg` (SHA256 `74a548ebbee963e41ef810c8c76ad2531014d8eec0def2dc64058d91b24fdddd`) et `UG-52PF1763-black.jpg`, dans `/workspace/wewa-assets/references/tank18-research-2026-10-21/`. La copie Bajajonline déjà connue est le même cliché rouge, pas une vue indépendante ; elle n’a pas été téléchargée de nouveau.

Préparer les courbes de couronne, épaules, creux latéraux et retours bas par zones, puis les comparer aux profils **et** aux obliques. Le contour siège/réservoir est une frontière occultante, pas le contour libre de la coque. Tunnel, soudures, épaisseur, interfaces de col et fixations cachées ne sont pas résolus. Le dessous Ensons/Kawasaki déjà rejeté ne doit pas remplir ces inconnues. Les appuis apparentés DJ141008 et JV171001 ont aussi été rouverts : une seule face chacun, sans mesure ni orientation montée certifiée.

## Deuxième pièce : selle

`wider-seat.webp` et les profils RDC montrent une longue assise noire, un raccord avant ajusté au réservoir et un arrière encadré par le rack. R05/R06/R07 apportent l’arrière et le dessus oblique. Il manque toujours un dessus perpendiculaire et le dessous de la selle actuelle.

Les **trois photos [Crosland JV191001](https://www.croslandrepuestos.pe/asiento-de-boxer-lineas-jv191001/p)** ont été rouvertes :

- `seat-crosland-00.jpg` : dessous nervuré, agrafage, **sept blocs caoutchouc** et zones d’attaches. SHA256 `cbf73ddab044bcf0c5ef1bbd23230ef9ab63fa281243bf4076c3c08e7b01fbbf`.
- `seat-crosland-01.jpg` : arrière/haut en oblique, bourrelet et grain visibles.
- `seat-crosland-02.jpg` : dessus, largeur variable, avant aminci et lignes embossées.

Ces fichiers privés sont dans `/workspace/wewa-assets/references/body-powertrain-18/`. JV191001 est la **Flat Seat** D04 PDF36 ; PF191000 est une **Profile Seat** différente dans D15. Les sept appuis concordent avec DP211009×7 du D04, sans certifier leur position ou l’embase RDC. La housse apparentée est embossée ; les petites vues RDC paraissent plus lisses, mais leur résolution ne prouve pas l’absence physique de ces lignes. Ne pas copier ou effacer ce détail par défaut.

La mousse/housse, son bourrelet et l’embase sont des formes différentes. Aucune cote de longueur, largeur, épaisseur de mousse ou entraxe d’attaches n’est publiée dans les sources lues. Une tête haute d’amortisseur ou un boulon proche du rack n’est pas reçu comme fixation de selle.

## Références suivantes du lot18

| Élément | Base disponible et variante conditionnelle | Manque utile avant détail |
| --- | --- | --- |
| Bouchon | DS141009 : coque supérieure bombée, serrure et bord/charnière, photo PartOnWheels rouverte ; BM150BS3 2011–2013 lié | Dessous, verrou/joint, diamètre/axe du col et enfoncement |
| Robinet / durite | PF171800 D04 **distinct** de PF171802 D15 ; PF171803 L185 lié. Manuels apparentés déjà archivés | Identification actuelle, dessous du réservoir, côté/orientation/sortie et routage essence |
| Caches LH/RH | Profils RDC rouge/noir ; D04 UG5 LH52JV0289/0292, RH52JV0290/0293. PF73012D blanc BM150 extérieur rouvert | Dos/pions/lèvres. Grande ouverture et côté du blanc non transférables à RDC ; pas duplication en miroir par défaut |
| Poignée / porte-bagages | PF231405 apparenté, photo WAY-C dessus oblique rouverte, profils et arrière RDC | Sections, soudures dessous et axes de fixation ; quatre fentes WAY-C non certifiées sur RDC |
| Feu arrière | Face rouge large à bas rétréci sur R06 ; PF401005 D04 **différent** de DF201138 D15 | Dos, joint, épaisseur/prismes et entraxes ; pas de luminance déduite de l’ampoule |
| Clignotants arrière | Deux ronds ambre visibles ; PF401003 LH/PF401004 RH apparentés, lentille DU201016 | Dos, tiges/câbles et optique détaillée. Quantité ambiguë d’une ligne catalogue non cumulée |
| Plaques / supports / réflecteur | R06 et obliques, petite plaque avant partielle R01/R03 ; PF231401 lié, plaque AR DF161252 D04 / DP161145 D15 | Dos/plis, dimensions et fixations courantes. Plaque, support, garde-boue et réflecteur restent distincts |

## Échelle et prochain relevé

**11 L** est une capacité publiée ; **1285 mm** est un empattement global. Ni l’un ni l’autre ne donne les sections du réservoir ou les dimensions de la selle. La durite apparentée185mm et les rondelles cotées du D04 ne calibrent pas la coque. Aucune estimation millimétrique nouvelle n’est créée ici.

Les [annotations de profil](../body-powertrain-18/profile-landmarks.json) restent des contraintes projetées ouvertes, avec ±2–7px selon le point. Elles ne prouvent ni une caméra orthographique ni les attaches3D ; aucune recette ou caméra gelée n’est changée.

Le relevé décisif reste **le même exemplaire identifié**, dessus et dessous dégagés, deux profils et avant/arrière avec règle dans les plans utiles. Pour la selle, préciser l’état sans charge et relever plusieurs largeurs/hauteurs, les appuis et les attaches ; pour le réservoir, relever col, tunnel et interfaces au cadre. Les candidats extérieurs devront conserver explicitement leurs dimensions estimées et leurs interfaces non validées.

Cette passe a rouvert **18 photos et quatre planches documentaires existantes**. Trois requêtes complémentaires ciblées n’ont livré aucune preuve nouvelle ; aucun doublon photographique téléchargé. Tous les pixels restent privés, sans publication GitHub, texture ni décalque constructeur. Aucune réception artistique ou validation iPhone implicite.
