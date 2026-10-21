# Viva Wewa — fabrication moto, point de revue 11

**La fabrication des dix-huit lots continue.** Ce point livre les sources candidates du corps de bras oscillant, de l’isolant d’admission et du collecteur métallique. L’isolant v2 reprend seulement la matière de son type existant. Le registre contient52 ID candidats, avec60 fiches déclarées et aucun lot complet ou reçu.

[Images courantes](motorcycle18-components.md) · [Galerie](motorcycle18-gallery/index.html) · [Plan18](../workflow/motorcycle-execution-18.json) · [Point10 conservé](motorcycle18-checkpoint-10.md)

## Corps de bras oscillant, séparé de ses accessoires

![Corps de bras oscillant, véritable rendu Blender](swingarm-body-v1/quarter.png)

Le [corps soudé](swingarm-body-v1/README.md) possède deux rails creux, leurs fentes arrière, deux logements de pivot distincts, un pont en U avec retour formé, des pattes percées et des cordons originaux. Deux photographies du même exemplaire52PF0219 apparenté guident la forme. Les dimensions, les soudures, le côté installé des petites attaches et la variante RDC restent estimés ou inconnus.

Les quatre finales Blender à96échantillons sont réellement relues, après gris et reflets des raccords. Le témoin sans rayons d’ombre explique deux plages sombres de la vue supérieure ; il ne remplace pas les finales avec ombres. Deux anciens macros masqués sont conservés comme diagnostics, sans être présentés comme preuve de joint.

La peinture noire propre est originale, sans rayures ou étiquettes copiées. Elle conserve exactement positions, normales, UV, tangentes et indices du maître gris fourni. Le vrai GLB205920triangles, ses textures embarquées et ses UV sont contrôlés ; quatre vues Babylon vérifient le chargement et les pixels. Cela ne certifie pas l’apparence sous le même éclairage ni le coût iPhone.

**Le corps seul est livré.** Bagues, axe, écrou, patin, tendeurs, plaques, commande de frein et amortisseurs sont des unités séparées. L’angle installé, les jeux et les interfaces du véhicule ne sont pas reçus.

## Admission : forme conservée, matière et collecteur séparés

![Collecteur métallique d’admission isolé](engine-intake-manifold-v1/reference-like-quarter.png)

Le [collecteur52JV0180 apparenté](engine-intake-manifold-v1/README.md) est un corps creux avec trois bandes de col, un raccord moulé et deux oreilles percées. Ses quatre finales96 et la vraie photo de référence sont relues. Les deux cartes originales de grain sont réellement cuites, embarquées et décodées. Le revers simplifié, le petit relief latéral, les dimensions, l’axe, l’alliage et l’échelle du grain restent réservés.

![Isolant d’admission, matière originale v2](engine-intake-insulator-v2/front-quarter.png)

L’[isolant v2](engine-intake-insulator-v2/README.md) ajoute deux cartes couleur/rugosité à la [forme v1 conservée](engine-intake-insulator-v1/README.md). Trois finales96, dont les macros neutre et rasante, montrent les stries originales. La géométrie rendue et sa pose sont protégées ; aucun relief, normalmap ou profondeur mesurée n’est annoncé. La direction, la régularité et le contraste des stries restent représentatifs. Les statistiques historiques CSG de v1 ne sont pas déclarées comme des opérations rejouées en v2.

Les vrais exports, images embarquées et quatre cadrages Babylon par candidat sont contrôlés. Les vérifications ciblées avec culasse/isolant/collecteur n’ont pas rapporté de traversée ou d’inclusion échantillonnée. **La marche25/22mm, les jeux et le montage restent ouverts.** Deux joints toriques, manchon, colliers, carburateur et fixations sont des pièces distinctes encore absentes de ces exports.

Les [recettes admission1](../research/motorcycle-source-dependencies-publication10-intake-v1/README.md) et [isolant2/bras1](../research/motorcycle-source-dependencies-publication10-insulator2-swingarm1-v1/README.md) distinguent maîtres fournis, étapes régénérables, guides et diagnostics. Aucun maître indispensable seulement privé n’a été détecté ; aucune reconstruction complète depuis un clone propre n’est déclarée. Les photos documentaires restent privées.

## Éclairage moteur : cadrage commun et défauts conservés

La [comparaison à caméra commune](upper-engine-common-camera-v1/README.md) charge le GLB du haut moteur déjà publié. Ses deux cadrages correspondent numériquement aux caméras Blender ; les huit témoins par vue contrôlent uniquement la projection logicielle, sans mesurer une photo.

La [variante HDR orientée](upper-engine-common-camera-v2/README.md) applique explicitement un quart de tour de sampling, dérivé des conventions Cycles4.3.2/Babylon9.31.0. Deux nouveaux canvas réels montrent les reflets déplacés, sans modifier modèle ou matière. AgX/ACES, préfiltres, BRDF et visibilité géométrique restent différents ; la copie d’un facteur d’exposition ne les étalonne pas ensemble.

L’[essai d’occlusion écran](upper-engine-occlusion-diagnostic-v1/README.md) possède un vrai témoin désactivé identique pixel par pixel à la vue HDR précédente. L’état activé assombrit les creux mais introduit du bruit et des contours irréguliers : **il est refusé pour adoption dans le jeu**. L’autre caméra n’est pas calculée avant correction. Les captures sont conservées sans retoucher l’albédo pour masquer le défaut.

L’[addendum de portabilité du haut moteur](../research/upper-engine-review-portability-v1/README.md) ouvre réellement la scène liée dans un autre arbre : sept bibliothèques physiques, douze meshes, données et poses inchangées. Aucun nouveau compagnon d’assemblage ni nouvel audit global de collisions n’est inventé.

## Travaux qui continuent

Une [nouvelle photo physique DS181008](../research/handlebar-mount-stack-followup-v2/README.md) documente mieux son extérieur ; revers, section et cotes restent inconnus. DS181009/010 n’ont pas de nouvelle preuve physique utile.

Le pneu arrière reste à reprendre : sa correction de terminaisons et son raffinement local ne sont pas clos dans ce point. Le tube d’échappement et le carénage de phare suivent leurs propres revues ; réservoir WEWA puis selle sont engagés dans la chaîne18. Les études actives ne sont pas de nouvelles pièces livrées ici. Le conducteur attend la moto seule. Le jeu public, sa source et la qualification physique iPhone restent inchangés.

Les preuves de commit exact, CI et synchronisation Ewutelo/Directus seront ajoutées après la coupe de ce point. Le suivi Directus reste structuré ; aucun téléversement binaire n’est déclaré.

## Vérification après publication

Source immuable : [`b0db1d39`](https://github.com/Mobutoo/wewa/commit/b0db1d397d63cbf602de27b741ae3fcf475c5c28), arbre `b317b57f7f83c4656c9ac3bca6d549c5254b0678`. Le contrôle de ce commit lit2386JSON,213manifestes,5702empreintes de fichiers,36empreintes PNG de checkpoints et3601liens ; aucune erreur. Ses71entrées de catalogue restent distinctes des52ID physiques enregistrés.

[GitHub Actions](https://github.com/Mobutoo/wewa/actions/runs/39558784551) et son étape de preuves moto ont réussi sur ce même commit. Le PRD Ewutelo complet est sauvegardé puis relu en révision36, avec égalité de tous ses champs et45exigences conservées. Ce pied de revue et les [métadonnées de vérification](../../WEWA_Developpement_Web/validation/motorcycle18-source11-integrity.json) sont postérieurs à cet arbre ; ils ne sont pas présentés comme des fichiers déjà contenus dans le commit source. Aucun binaire n’a été téléversé dans Directus.
