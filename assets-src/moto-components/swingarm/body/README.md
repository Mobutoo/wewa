# Corps de bras oscillant — reconstruction candidate apparentée

Ce travail porte sur le corps soudé seul, à partir de deux photographies du même exemplaire 52PF0219 annoncé BM/BMX150. L’identité et les dimensions du bras de la Boxer125HD commercialisée en RDC ne sont pas établies. Ce n’est pas une pièce reçue ni un montage certifié.

Les photographies originales restent privées et ne sont pas utilisées comme textures. Elles peuvent être comparées sur la [fiche Motozilla 52PF0219](https://motozilla.com.ua/product/boxer-bm-vmx-150cc-mayatnik-zadniy-52pf0219-c-razborki-novyy-bajaj-358095/). Le [dossier documentaire](../../../../creative/research/swingarm15-reference-v1/README.md) conserve leurs URL et empreintes, les planches voisines D04/D15 et la différence avec PF122030. Les deux angles du même exemplaire sont utilisés ; les variantes ne sont pas fusionnées comme des multivues.

Le corps comprend deux rails creux, leurs fentes arrière, deux logements cylindriques avant séparés et un pont en U avec retour formé et extrémités progressives. Les pattes percées, les petites attaches avant et la patte asymétrique sont fabriquées séparément dans la recette, puis réunies à la source. Les profils et cordons de soudure sont originaux. Leur forme, épaisseur, pas, matière et orientation sont des estimations, pas un relevé de fabrication. Les étiquettes et rayures des photographies ne sont pas recopiées.

Les bagues de pivot, l’axe, son écrou, le patin de chaîne, les tendeurs/plaques, la liaison de frein et les amortisseurs sont d’autres composants. Aucun tube continu n’est ajouté dans le vide entre les deux logements avant. Le rôle précis et le côté installé de certaines petites attaches restent conditionnels.

## Dimensions et repère

Le repère isolé place l’axe de pivot transversal X à l’origine ; +Y va vers l’axe arrière et +Z est le haut candidat. +X correspond au côté gauche du pilote dans le repère commun, mais le côté photographique des petits détails n’est pas certifié. La pose et l’angle installés sont inconnus.

Toutes les cotes du corps dans `parameters.json` sont estimées et bornées : entraxe de travail pivot/fente520mm [450–600], rail24×30mm [20–32]×[24–40], paroi1,8mm [1,2–3], logements extérieurs32mm [28–38] avec alésages26mm [22–30]. Les dimensions ne sont pas déduites de l’empattement1285mm ni de la photo de l’axe voisin.

La [photo cotée du vendeur JA121003](https://motozilla.com.ua/product/boxer-bm-vmx-150cc-os-mayatnika-d12mm-l260mm-ja121003-c-razborki-novyy-bajaj-358102/) indique260mm hors tout apparent, filetage12mm et fût14mm près de la tête. Cela reste une donnée vendeur d’une pièce apparentée, sans pas publié ni certification RDC. Le titre simplifie en diamètre12mm ; ces nombres ne sont pas transférés aux cotes du corps ni à un axe générique.

## Construction et contrôles

`build.py` génère le brut `swingarm-body-raw-v1.blend` à partir de profils natifs originaux et de leurs volumes locaux éditables. `refine_topology.py` fournit ensuite une étape contractée intermédiaire ; `refine_needles.py` et `authored_normals.py` produisent le source contrôlé `swingarm-body-v1.blend`. Le mode `--stage=full` ajoute retours, attaches et soudures ; le mode de base documente une étude partielle sans ces éléments. `csg.py` réunit et perce les volumes originaux avec manifold3d3.3.2, à la source uniquement. Aucune géométrie importée et aucune correction du buffer exporté.

Les longues bandes des rails sont segmentées avant réunion pour éviter des triangles numériques très minces. Les diagonales de plages planes sont ensuite reconnectées sans déplacer leurs points. `refine_topology.py` traite ensuite uniquement des arêtes adjacentes minuscules : condition de lien d’un maillage triangulaire fermé, rejet de plis et déplacement maximal de chaque groupe d’anciens sommets vers son sommet conservé borné à1µm. Ce seuil numérique ne représente pas une précision physique du relevé. La simplification générale et la fusion globale essayées ont été refusées ; leurs diagnostics sont conservés séparément. Six rotations locales de diagonale améliorent ensuite les triangles problématiques sans déplacer les sommets de l’étape contractée ; les plans connus reçoivent leurs normales auteur et les UV emploient des normales de face float64. Les fans d’un cordon explicitement continu sont conservés face aux aiguilles numériques. Les tangentes sont calculées par Blender, jamais réparées dans les buffers. Fermeture, volume, passages réels, UV et tangentes ont passé sur le G3 ; les trois gris, les deux macros de reflets intérieurs et le témoin sans ombres ont été réellement ouverts. Le matériau conserve strictement les positions, normales, UV, tangentes et indices du master G3. Les vues finales restent distinctes de la réception artistique.

Les collections de construction et de studio sont locales, cachées et exclues de l’export sélectionné. Aucune Library externe n’est nécessaire. Les deux images originales de matière sont embarquées et leurs chemins `//textures/…` sont relatifs. Pas de compatibilité de bague/roue/amortisseur, de résistance de soudure ou de LOD mobile qualifiés.


## Matière propre originale et reprise

La peinture sombre propre est une proposition : base linéaire (0,009 ; 0,010 ; 0,012), métal0, rugosité de travail0,27–0,33 et normal map tangentielle de force0,25. Deux cartes512² se répètent sur une tuile UV de10mm ; le relief auteur a un RMS d’environ0,26µm. Ces valeurs et l’échelle du grain sont estimées, sans mesure de finition ou de chimie. Les étiquettes, l’éclairage, les rayures et l’usure de la photo ne sont pas dans ces cartes. Le noir peut paraître gris dans les reflets des grandes sources du studio.

Les deux premières macros n’exposaient pas les joints intérieurs : elles sont conservées sous `creative/reviews/swingarm-body-v1/diagnostic-occluded-reflection-weld-detail.{png,json}` et `diagnostic-occluded-reflection-return-detail.{png,json}`. Leur cadrage ne constitue pas une preuve du cordon ou de la paroi. `occluded-camera-diagnostic.json` donne leurs empreintes distinctes ; les vues utiles corrigées gardent les noms `reflection-weld-detail` et `reflection-return-detail`. Le témoin sans ombres explique les deux plages sombres près des pattes dans la vue supérieure ; les ombres réelles restent actives dans les finales.

La recette source utilise Blender4.3.2 et le Python hôte avec manifold3d3.3.2 (`requirements.txt`), puis les dépendances Node du dépôt pour le contrôle glTF. Depuis la racine du checkout, utiliser le même exécutable Blender pour chaque script avec `--background --threads 1 --python-exit-code 1 --python` :

1. `assets-src/moto-components/swingarm/body/build.py -- --stage=full` produit le brut diagnostic, dont les tangentes ne sont pas encore valides.
2. `refine_topology.py`, puis `refine_needles.py` dans ce même dossier produisent le G3. Le source contracté et le brut sont des étapes intermédiaires, jamais des candidats finaux.
3. `check_export.mjs` (Node) et `inspect_interfaces.py` (Blender) contrôlent l’export et les passages. Les cartes et le shader se construisent avec `material.py` seulement après une revue grise réelle rattachée au G3.
4. Pour rejouer seulement la matière depuis le checkout, copier les deux binaires et `source-geometry-check.json` de `g3-master-v1/` vers leurs chemins actifs, restaurer le contrôle buffer G3 dans le dossier de revue, puis lancer `material.py`. Cela écrase les chemins actifs : travailler dans une copie isolée du checkout. La copie G3 fournie évite toute dépendance au cache privé ; les empreintes d’un `.blend` régénéré peuvent varier, les contrôles lisent les données réelles.
5. `check_export.mjs`, `check_material_preservation.mjs`, `inspect_material.py` et `inspect_interfaces.py` contrôlent le candidat PBR. `render.py -- --final --view=quarter --view=reverse-quarter --view=weld-detail --view=return-detail` calcule96échantillons avec checkpoint par PNG et préflight des vrais sommets.
6. Après lecture réelle des finales et écriture de `source-render-review.json`, `record.py` scelle uniquement son allowlist. `record.py --freeze` fige les entrées avant les finales. Les preuves moteur sont produites séparément par root, jamais aspirées récursivement dans ce manifeste.

Les dimensions, l’identité RDC, le côté des petites attaches, les cordons réels, l’angle installé, la résistance et les interfaces de roue/pivot/chaîne restent ouverts. Aucun mouvement ou montage complet n’est qualifié, aucun LOD ou test iPhone physique effectué.
