# Flasque de frein arrière — DS151069 — recherche v1

**Résultat utile : photos réelles de face, oblique extérieure, revers nu et oblique du revers retrouvées et effectivement vues pour DS151069.** La topologie générale du flasque est documentée. Les cotes, le profil de chant complet et la confirmation de la variante RDC actuelle restent ouverts. Recherche uniquement : aucune géométrie, aucun Git, aucune mise à jour des registres ou anciens gels.

## Réconciliation des codes

| Code | Preuve lue | Conséquence |
|---|---|---|
| **DS151069** | D04 BM125, feuille46, planche33 repère16, page70 : «Panel Rear Brake». D04 feuille43 : roue arrière cinq branches DM151323 et option UG5Gear JZ131213. | Candidat principal pour le flasque arrière BM125 à roue moulée ; pas une certification de l’année/marché RDC. |
| **DS151069** | Catalogue Bajaj BM150 Rev01 mars2016, feuille44 pages67–68 : **Rear Hub (for Alloy Wheel)** repère18. | Confirme le circuit roue moulée de la famille BM150. |
| **DS151076** | Même catalogue, feuille43 pages65–66 : **Rear Hub (for Spoke Wheel)** repère20. | Variante à rayons dans cette édition ; ne pas réduire à «ancien code». |
| **DS151069 → DS151076** | Bajajonline, catalogue et pages produit réellement lus : annonce de remplacement explicite. | Donnée revendeur à conserver ; aucune circulaire constructeur lue, aucune égalité géométrique prouvée. |
| **DJ151092** | Liste de pièces2019–2020 et extraits indexés Pulsar/Discover : rear brake panel. | Pas attribué au flasque D04 ni au BM150 moulé de l’édition inspectée. Association150X proposée par utilisateur non vérifiée ici. |
| **PF131606** | Association d’ensemble signalée par utilisateur sur99rpm ; accès direct403, index général sans ligne de code. | Composition et lien exact à DS151069 restent inconnus ; aucun contenu d’ensemble inventé. |

Le nom «4 Rubber» apparaît pour DS151076 dans la liste2019–2020 ; D04 dit simplement «Panel Rear Brake» pour DS151069. Le nombre de caoutchoucs de transmission ne devient pas une caractéristique visuelle supposée du flasque. La liste et les catalogues sont des documents Bajaj hébergés par des tiers, pas des nouveaux téléchargements depuis un domaine constructeur.

## Photos physiques réellement vues — pixels privés

- [Parton Wheels — DS151069](https://partonwheels.com/product/panel-brake-rear-for-ct110-discover-125-boxer-bm150-ct-125x-bajaj/) : `parton-4.png` face, `parton-6.png` oblique légère, `parton-8.png` revers nu, `parton-10.png` revers oblique avec bord usiné. Le dernier fichier conserve un nom local.png mais contient un JPEG. **Marquage moulé DS15 1069 lisible au revers.**
- [Bajaj Matriz — SKU DS151069](https://bajajmatriz.com/producto/porta-balatas-freno-trasero-moto-boxer-150-bajaj/) : `matriz-DS151069.jpg`, face extérieure sur boîte Bajaj. Même famille de nervures, bosses et oreille. Application annoncée Boxer150 quatre/cinq vitesses UG ; pas RDC125 attestée.
- [Bajajonline — DS151069](https://www.bajajonline.ru/catalog/item/kryshka_zadnego_kolesa/) : `russian-069-0.jpg`, oblique extérieure utile ; `russian-069-1.jpg`, revers **strictement identique en SHA256 à parton-10.png** ; vignette catalogue même pose extérieure réduite. Ne pas compter cette reprise comme vue opposée indépendante.
- [Bajajonline — DS151076](https://www.bajajonline.ru/catalog/item/kryshka_zadnego_kolesa_1/) : page lue, aucune photo de pièce, seulement placeholder.

Huit fichiers photographiques inspectés, dont un doublon exact et une vignette de même pose. Cinq rendus privés de pages PDF également examinés. Les URL directes et SHA256 individuels sont dans `images-viewed.json` ; aucun pixel ni HTML documentaire n’est publié dans ce dossier du repo.

## Ce que les vues débloquent

La face révèle un corps circulaire légèrement en cuvette, un relief périphérique annulaire, un bossage central arrondi et sa portée usinée, un second alésage décentré, une oreille latérale épaisse percée et **trois longues nervures** convergeant vers elle. Le cartouche courbe porte «USABLERANGE» ; un petit creux rond est visible près du départ des nervures.

Le revers nu révèle une bague centrale saillante, des nervures radiales courtes, des cloisons courbes et radiales délimitant des poches, un pion cylindrique décentré, l’arrière de l’alésage secondaire et une poche hexagonale derrière l’oreille. L’oblique montre plusieurs étages/gorges concentriques usinés sur la périphérie. Ces éléments sont physiques et visibles, sans interprétation fondée sur les seuls reflets.

La position de l’axe et de la came est soutenue par l’éclaté D04 ; le pion comme appui de mâchoire et l’oreille comme interface de réaction restent des interprétations documentées comme telles. Aucune fonction attribuée comme fait au petit creux, aux pastilles rondes, aux marquages ou aux gorges. Le texte générique Parton parlant de «brake valves» est écarté.

Une estimation des proportions projetées et de l’agencement des reliefs est désormais possible. Aucune cote en millimètres, hauteur de nervure, profondeur de gorge ou tolérance ne peut être déclarée mesurée. Pas de profil orthographique de chant ni échelle. Aucune estimation numérique ou géométrie n’a été produite.

## Sources et limites de variante

D04 : https://motobro.ua/files/Boxer_BM_125_UG_Provisional_SPC_%282%29.pdf — provenance URL lue dans `creative/workflow/sources.json`. PDF privé fourni : `/workspace/wewa-assets/references/exterior-completion-current/BM125.pdf`, SHA256 `5228ed1fb3f5ab9ec1503864bf6cccf66bd429ece78adb30516f9904a099372e`. Pages43/46 rendues et vues ; pas seulement texte indexé.

BM150 : https://bajaj.club/catalog_file/Boxer-BM150.pdf — catalogue constructeur sur miroir tiers, Rev01 mars2016 selon texte de la première feuille. Pages40/43/44 rendues et vues. La planche roue moulée cite PF131222 cinq branches depuis mai2012 ; le tableau comporte aussi une option six branches. Le pneu arrière BM150 est100/90-17 avec chambre dans cette édition : **ne pas transférer ces cotes au3.00-17 RDC125**. D04 lui-même distingue des références de roues et mentionne des pneus avec chambre ; l’identité de moyeu et la révision RDC actuelle restent à confirmer.

Liste2019–2020 : https://catalog.wlimg.com/1/2197403/other-images/table-559249.pdf — texte extrait consulté pour les désignations des trois codes, pas un plan de montage ni preuve d’interchangeabilité.

Liens officiels famille découverts : [OwnersZone Global Bajaj](https://global.globalbajaj.com/en/ownerszone) et [BM150_PM Iraq](https://cdn.globalbajaj.com/-/media/Iraq/Documents/Boxer/Boxer-BM150/Boxer-BM150_PM.pdf?rev=ea8a2a1e668d4ed0b53010c06565a0eb). Tous deux403 ; le PM est indexé «User’s Guide», pas confirmé comme catalogue pièces. Pas d’accès protégé contourné.

## Canaux négatifs et gel

99rpm403 ; MotosPremium500 ; Prom exact DS151069 indexé comme pièce de démontage, mais la page aboutit à une catégorie générique200 sans photo cible. Recherches ciblées Crosland/Mundimotos : pas de résultat exact exploitable dans cette session. Dernières recherches Brave : quatre429, arrêt du canal. Ces limites ne prouvent aucune inexistence. Aucun message vendeur, authentification, DRM/captcha ou API épuisée relancé.

Terminé : recherche ciblée, vues réellement examinées, rapprochement de codes, observations/limites et manifeste. Manquant : cotes et coupe métrique, montage exact RDC, preuve constructeur de substitution076 et composition PF131606. La recherche fournit un dossier de forme DS151069 ; elle ne vaut ni fabrication, ni validation G3 globale, ni réception artistique.

Fichiers JSON/Markdown du gel en lecture seule ; toutes les empreintes du manifeste vérifiées. Immuabilité par règle de version et intégrité SHA256, pas stockage WORM. Toute suite demande un nouveau gel. Aucune modification du gel réflecteur.
