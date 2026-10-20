# Recettes par famille

Ces adaptations appliquent le [workflow commun](README.md). Elles définissent les preuves à chercher, pas des recherches déjà achevées sur tous les objets. La présence d’une recette dans [coverage.json](coverage.json) indique un routage initial à relire à G0. Une entrée composite reçoit plusieurs recettes et plusieurs fiches enfants.

## Véhicules et pièces mécaniques — `vehicle`

Identifier marque, modèle, génération, marché, année plausible et modifications locales. Chercher brochure technique, catalogue de pièces, profil des deux côtés, face/dos, dessus, cockpit, roues et raccords. Cotes prioritaires : empattement, voies si applicable, diamètre réel des roues, gabarit et pivots. Ne pas emprunter une cote à une autre génération.

Décomposer roues/pneus, freins, suspensions, châssis, moteur, carrosserie, sièges, vitrage/optiques et commandes. Construire par sections/surfaces, courbes et répétitions documentées. Contrôler ajours et asymétries en gris avant matières. Vérifier braquage, suspension, roues et portes utiles, sans intersection. Le budget cockpit peut différer de celui du trafic éloigné. La moto seule suit aussi son [plan spécifique](../MOTORCYCLE_PLAN.md).

## Architecture et lieux — `architecture`

Identifier bâtiment/lieu, adresse, date et état ; conserver les coordonnées et emprises sources. Chercher façade de face et obliques, angles, toiture et détails d’ouvertures. Séparer hauteur documentée, nombre d’étages et estimation. OSM fournit un modèle d’information d’emprise/parties/toit, pas une photo de façade exacte [W03].

Décomposer travée, mur, menuiserie, balcon, brise-soleil, toiture, gouttière et accessoires. Comparer d’abord une travée complète, son épaisseur et ses ombres, avant duplication. Vérifier cours, passages, porte-à-faux, niveaux et accès. Un lieu fictif garde cette qualification ; une enseigne originale ne doit pas être présentée comme un relevé réel.

## Voirie, terrain et drainage — `terrain`

Documenter coupe transversale, largeur utile, pentes, bordures, fossés, grilles, raccords et état sec/pluvieux. Distinguer relief réel, adaptation jouable et matériau. Une image satellite informe le tracé visible, beaucoup moins la profondeur d’un caniveau.

Fabriquer un échantillon de raccord à l’échelle : chaussée/bordure/trottoir/caniveau ; contrôler joints, ajours et écoulement plausible, puis répétition. Gros nids-de-poule, marches et fossés visibles/collisionnables demandent une forme ; la normal map ne déplace pas la roue. Valider collision, contact et transition de cellule séparément du rendu de surface. Aucune modification des géodonnées sources.

## Objets, mobilier et assemblages — `prop`

Identifier produit réel ou création originale, dimensions, matière et usage. Rechercher face/profil/dos et gros plans de jonctions. Décomposer panneaux, profils, pieds, fixations, charnières, cordes et contenu. Conserver épaisseur et jeu de montage, éviter les pièces qui se traversent sans liaison.

Construire puis recevoir un exemplaire avant variantes. Vérifier assise d’une chaise, empilage de caisse, suspension de câble ou ouverture utile. Les faces cachées peuvent être simplifiées seulement si elles restent invisibles lors des interactions. Un objet narratif important conserve sa lisibilité à la distance de jeu.

## Surfaces et matériaux — `material`

Rechercher matière, échelle du grain, méthode de fabrication et état ; distinguer teinte, relief, rugosité, métal et lumière photographiée [W01–W02]. Si capture possible : éclairage contrôlé, référence d’échelle/couleur et photos montrant les reflets [W04]. Sinon sélectionner une ressource autorisée et vérifier son adéquation locale ; ne pas inventer une carte de rugosité mesurée.

G2 devient l’échelle du motif et le protocole de lumière ; G3 est le relief de support/surface et peut être justifié non applicable pour un matériau plat sans géométrie propre. Présenter plaque et objet utile, lumière neutre puis rasante, sec/humide séparés, répétition sans raccord visible. Export : espaces de couleur et canaux glTF, mipmaps et compression à examiner. Ne pas recopier l’éclairage de la photo dans l’albédo.

## Végétation — `vegetation`

Identifier espèce ou famille avec niveau de certitude, taille, maturité et saison. Chercher arbre entier, tronc, branche et feuille face/dos à l’échelle. Construire d’abord une feuille/fronde et une branche, puis houppier et asymétries ; recevoir l’exemplaire avant les variations.

Contrôler de dessus et de dessous : silhouette, densité, courbure et réponse lumineuse. Des cartes planes peuvent disparaître de profil ; des contours trop larges augmentent les pixels transparents inutiles [W05]. Vérifier feuillage en groupe, vent, alpha, LOD et ombres. Le choix d’un palmier dans une bibliothèque ne prouve pas l’espèce plantée à Gombe.

## Personnages, vêtements et animation — `character` / `animation`

Personnages fictifs ; références d’anatomie, vêtements et usages locales, sans supposer que la licence d’un vêtement couvre toutes les ressources tierces. Séparer corps, visage, mains, chaque vêtement, chaussure, cheveux et accessoires. Réception de forme et de tissu avant ensemble ; silhouette et plis doivent fonctionner en mouvement.

Documenter squelette, unités, pose de repos et transferts ; aides IK utiles aux contacts [W06]. Contrôler épaules/coudes/genoux/doigts, pincements, traversées de tissu et glissement des pieds. Pour la conduite : contacts mains/leviers/pieds/selle, braquage et montée/descente ; conducteur différé jusqu’à réception de la moto. Pour une animation autonome, G3/G4 concernent le support ou renvoient aux fiches reçues ; preuve centrale = séquence de poses et résultat moteur.

## Audio et contenu culturel — `audio`

Identifier événement, source, interprète/auteur, droits d’enregistrement, langue, sens et contexte. Séparer moteur/charge/rapports, klaxon, appels, conversations et musique. Une référence musicale ne donne aucun droit de l’incorporer. Les appels lingala et taquineries gardent le statut à relire par une personne compétente ; ne pas les inventer comme expressions authentifiées.

G2 devient protocole d’écoute et étalonnage de niveaux ; G3/G4 deviennent montage, timbre et texture sonore, sans caméra imposée. Conserver source non destructive, boucles et variantes ; écouter isolé puis avec trafic et danger audible. Tester orientation/atténuation et déplacement auditeur/source [W07], démarrage tactile, pause/reprise et saturation. Le statut technique ne vaut pas validation linguistique ou culturelle.

## Interface, publicité et objets de jeu — `interface` / `gameplay`

Définir fonction, états, texte, distance de lecture, format portrait/paysage et gestes. Graphismes originaux, publicités fictives ; règles et sources du dossier conservées. G2 devient grille/échelle écran et protocole tactile ; G3/G4 deviennent composition, contraste, typographie et matière si objet 3D. La recette mécanique s’ajoute pour un compteur réel ou un accessoire physique.

Montrer états réels et lisibilité sur scène claire/sombre/en mouvement. Vérifier joystick unique pour accélérer/freiner/reculer/diriger, commandes secondaires indépendantes, pouces et zones sûres. Tester la séquence de jeu utile ; une maquette statique ne prouve ni ergonomie ni fonctionnement sur Safari physique.

## Assemblage et réutilisation

Relier les composants reçus par leurs révisions, conserver pivots/interfaces et rechercher les incompatibilités au montage. Faire une revue de l’ensemble sans conducteur pour la moto ; réception du véhicule avant personnage. Pour la rue, recevoir un tronçon étalon avant extension. Pour la végétation ou le trafic, mesurer un groupe représentatif avant multiplication. L’origine d’une ressource, sa qualité locale, ses droits et son coût restent quatre questions séparées.
