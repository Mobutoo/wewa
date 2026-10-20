# Direction retenue : réalisme cinématographique

Le 20 octobre 2026, l’utilisateur choisit explicitement le **style 2** parmi les trois propositions. Cette décision fixe la direction artistique ; elle ne réceptionne aucun modèle ou rendu du jeu existant.

## Règles applicables à chaque pièce

Proportions et construction réalistes issues des références du dossier. Les courbures, sections, épaisseurs, vides et raccords se vérifient sous lumière neutre avant la présentation cinématographique. Pas d’agrandissement du moteur ou des pneus pour renforcer l’effet visuel. Le moodboard ne fournit aucune cote mécanique et ses détails éventuellement inventés ne doivent pas être reproduits.

Matières distinctes : peinture vernie, métal peint, chrome, aluminium moulé, caoutchouc, plastique et vinyle. Travailler leur relief à l’échelle physique, leurs arêtes, leur rugosité et leurs reflets. Un métal peint reste un diélectrique à sa surface ; seules les zones de métal exposé prennent sa réponse métallique. L’usure est localisée selon la fabrication et l’usage ; aucune couche uniforme de saleté.

La présentation cible emploie une lumière chaude de fin d’après-midi, des ombres lisibles, des couleurs riches et crédibles, une séparation douce des plans et des reflets cohérents. Le rouge de la moto et le jaune des taxis servent de repères colorés. Éviter hautes lumières brûlées, noirs bouchés, halo artificiel et dominante orange uniforme.

## Deux éclairages de contrôle

1. **Neutre :** fond gris et grandes sources blanches, exposition stable, cadrages de référence et gros plans ; déceler erreurs de forme, pincements et matières trop brillantes.
2. **Cinématographique :** source principale chaude, remplissage et contrejour sobres, même objet et mêmes matières ; vérifier le rendu cible sans cacher les défauts du premier examen.

Conserver caméra, transformée de couleur et paramètres de lumière dans la source Blender. Les images de réception proviennent de la géométrie produite. À l’export, comparer aussi dans Babylon.js : un rendu Cycles seul ne réceptionne pas le rendu du jeu ni sa performance iPhone.

## Application au workflow

G0 référence cette direction ; G3 examine la forme grise ; G4 compare les matières sous les deux éclairages ; G6 compare l’export dans le moteur ; G8 conserve la décision sur la pièce et sa révision exacte. La réception du style ne ferme aucun de ces passages de fabrication. La moto reste seule avant conducteur.

La référence générée choisie est conservée dans `direction/style-02-cinematographique.png` avec son empreinte et son statut dans `direction/provenance.json`. Elle représente une intention de lumière et de matière, pas un relevé de Gombe ni une capture du moteur.

## Identité sur la moto

Sur instruction utilisateur, le réservoir porte désormais **WEWA** à la place de Boxer. Les sources documentaires conservent leur nom constructeur ; le marquage du véhicule du jeu et les futures textures de réservoir utilisent Wewa. Le visuel courant est `direction/motorcycle-wewa-style-02-generated-reference.png`. Le marquage latéral125HD et la direction cinématographique sont conservés.
