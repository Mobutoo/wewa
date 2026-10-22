# Direction supérieure — lecture critique des interfaces v1

**DS181005 est bien la famille du té supérieur large ; DS181019 est un demi-collier de guidon, pas son autre référence. Les photos de DS181012 rendent crédible un petit passage supérieur au-dessus d’un tube de31mm, mais ne prouvent pas son ajustement.** Aucun alésage, placement, source ou contact modifié.

## Identification et empilement documentaire

| Article | D04 effectivement lu | Ce que la preuve autorise |
|---|---|---|
| DS181005 | FeuillePDF51, page80, planche37, repère10 : BracketUpperFrontFork, quantité1 | Té supérieur large ; photo physique correspondante retrouvée. |
| DS181019 | Feuille48, page74, planche35 guidon, repère12 UG5Gear, quantité2 | Demi-collier supérieur de guidon ; sa photo montre une petite selle à deux trous. DS181006 est l’élément inférieur repère13. |
| DS181020 | Feuille51 repère12, quantité1 | Té inférieur / ensemble sous-fourche ; photo avec deux colliers fendus et axe central. Le parent natif inférieur n’est pas tout cet ensemble avec axe. |
| PF121017 | Feuille51 repère5, quantité2 ; joint repère2 «For31DiaFork» | Famille nominale31mm. Pas une mesure physique du tube ni de la tolérance. |
| DS181012 | Feuille51 repère18, quantité2 ; joint torique30181029 repère19 | Élément fileté au sommet de chaque jambe. La photo révèle filetage extérieur, gorge, épaulement/hexagone, col réduit et taraudage central. |
| 59040006 | Feuille51 repère7, quantité2 : BoltWithWasherM10x24 | Vis et rondelle au-dessus de l’extrémité de jambe dans l’éclaté. Photo physique lue. |
| DS181015 + DS181016 | Feuille51 repères8/9, quantité1 chacun | Écrou borgne et rondelle dessinés au centre, sur l’axe de direction, au-dessus du té ; pas deux bouchons de tubes. |

Le catalogue BM150Rev01mars2016, feuille49/pages77–78, planche34 fairing, recoupe cette famille :005/020/017 et paire012/59040006. Son repèreDS181012 est19, ne pas recopier le repérage18 duD04. Sources Bajaj sur miroirs tiers : [D04](https://motobro.ua/files/Boxer_BM_125_UG_Provisional_SPC_%282%29.pdf), [BM150](https://www.bajaj.club/catalog_file/Boxer-BM150.pdf). Trois pages rendues privées et effectivement vues.

## Photos physiques nouvelles et cache

Pages publiques Bajajonline réellement lues, avec photos réellement ouvertes :

- [DS181005 — plaque supérieure](https://www.bajajonline.ru/catalog/item/traversa_verkhnyaya/)
- [DS181019 — collier guidon](https://www.bajajonline.ru/catalog/item/kronshteyn_rulya_2/)
- [DS181020 — inférieur avec axe](https://www.bajajonline.ru/catalog/item/traversa_nizhnyaya_4/)
- [DS181012 — bouchon épaulé taraudé](https://www.bajajonline.ru/catalog/item/bolt_fork_1/)
- [DS181015 — écrou borgne central](https://www.bajajonline.ru/catalog/item/gayka_traversy_verkhnyaya/)
- [PF121017 — tube intérieur](https://www.bajajonline.ru/catalog/item/truba_amortizatora_1/)
- [59040006 — vis M10×24 avec rondelle](https://www.bajajonline.ru/search/?q=59040006)

Ces références sont `exact` pour le code de la page, `related` pour le montage RDC actuel ; aucun code estampé n’est lisible sur le métal. Le cache privé `front-completion-p25/fork.jpg`, pagecanonique [Matriz](https://bajajmatriz.com/producto/horquilla-suspension-delantera-boxer-150-4-vel-5-vel-ug-bajaj), a aussi été vu : jambes, té inférieur et axe assemblés, té supérieur absent. Des extrémités réduites dépassent des tubes, sans montrer de plaque assise sur ces portées. Toutes les URL directes, chemins privés etSHA256 sont dans `images-viewed.json`. Pixels privés uniquement.

## Pourquoi16–18mm n’est pas nécessairement contradictoire avec31mm

Les annotations fournies par utilisateur donnent rayons9,5/10px×0,00088m/px, soit8,36/8,80mm et diamètres16,72/17,60mm. Ce sont des valeurs d’un tracé de photo non calibrée, pas des mesures OEM. La plaque DS181005 photographiée n’est pas un té à deux colliers cylindriques fendus : les grands tubes n’ont donc pas à être supposés traverser ses trous extrêmes à plein diamètre.

Le bouchon DS181012 possède physiquement une grosse zone filetée extérieure et un col réduit taraudé au centre. Avec l’éclaté et la vis M10/rondelle séparée, cela soutient une architecture où la fixation supérieure se fait par une section plus petite que le tube. **L’explication par bouchon/épaulement est désormais étayée qualitativement ; ni diamètre du col, ni plan d’appui de la plaque, ni jeu ni hauteur d’empilement ne sont mesurés.** La photo ne tranche pas exactement quelle surface du col ou de la vis traverse ou porte sur la plaque. Un diamètre nominal M10 n’explique pas à lui seul le diamètre total17mm estimé.

Ne pas élargir les trous à31mm pour supprimer un écart visuel, ni déclarer un contact parce que trois axes sont alignés. Les cinq autres trous de la plaque restent sans affectation fonctionnelle certaine dans ce dossier. Aucun filet, épaulement caché, pression de serrage ou raccord n’est inventé.

## Repères locaux utiles à main

Les deux `.blend` ont été ouverts avec scripts désactivés, sans sauvegarde ; leurs SHA sont inchangés et concordent avec les fiches existantes. `local-landmarks.json` donne les centres lus des guides/cutters de construction, sans les confondre avec des cotes de la vraie pièce.

- Supérieur : extrêmes environ`(-0.087120,+0.051040,0)` et`(+0.089760,+0.052800,0)` ; guide central`(0,0,0)`.
- Inférieur : jambes environ`(-0.087500,0,0)` et`(+0.087500,0,0)` ; centre`(0,+0.045000,0)`.

Il y a une différence de datum et de signe du déport centre/jambes. Les parents ne sont pas dans un repère commun prêt à monter. L’entraxe candidat supérieur≈176,89mm et inférieur175mm reste issu de constructions estimées, pas une exigence à égaliser. Aucune rotation ou translation proposée/appliquée ici. La correctionRx/Rz de mainv4 est reçue comme information utilisateur, pas validée par une lecture de sa source.

Le fichier demandé `assets-src/moto-components/steering-triples/upper/parameters.json` est absent dans cet espace. Il n’a pas été restauré : **aucun Git**. Les valeurspx et le facteur d’échelle sont donc attribués au message utilisateur, et non présentés comme relus dans ceJSON. Les positions de guides ont été vérifiées indépendamment dans les sources natives. Leurs demi-bounds englobent les guides/chanfreins et ne sont pas annoncées comme vrais rayons de passage.

## Bilan borné

Fermé : confusion005/019 ; famille documentaire005+020+017 ; existence physique du bouchon épaulé012 taraudé et de la vis59040006/rondelle ; distinction de l’écrou borgne central015. Mieux étayé : fixation supérieure à section réduite, compatible en principe avec des trous plus petits que31mm.

Ouvert : dimension et fonction précise de chaque passage, hauteur/plan d’appui, contacts, révision exacteRDC, pose et serrage réels. La preuve décisive reste une vue démontée/assemblée du même ensemble ou une coupe/mesure montrant plaque, bouchon et vis ensemble. Les centres conditionnels peuvent servir au diagnostic main ; aucune réception de fit n’en découle.

Recherche publique directe sans Brave, sans contournement, sans vendeur contacté. La recherche Matriz DS181005 sans résultat ne prouve aucune absence. Aucun ancien gel ou registre partagé modifié. JSON/Markdown seuls dans le repo ; gel et manifeste en lecture seule, empreintes vérifiées, sans garantieWORM.
