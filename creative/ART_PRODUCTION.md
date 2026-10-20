# Viva Wewa — production artistique après le refus de la version 3

La version publique 3 reste une préalpha. La référence photographique fournie par l’utilisateur est la cible artistique. La capture du moteur dans `WEWA_Developpement_Web/validation/browser/desktop-game.png` montre que cette cible n’est pas atteinte. Les fichiers Blender, tests logiciels et quantités d’objets ne remplacent pas cette comparaison.

## Écarts qui empêchent l’acceptation

| Priorité | Constat dans le moteur | Travail nécessaire | Preuve attendue |
|---|---|---|---|
| Critique | Pilote aux volumes simplifiés, vêtements sans détails crédibles, gestes limités | Anatomie et posture en selle ; vraie coupe des vêtements, coutures/plis ; UV, normal et rugosité ; rig, mains sur le guidon, pieds et inclinaison | Gros plan arrière et trois quarts dans le moteur, séquence accélération/virage/freinage |
| Critique | Façades répétées, grandes parois aveugles, bâtiments en volumes provisoires | Reconstituer les bâtiments visibles du tronçon depuis des références identifiées ; baies en retrait, brise-soleil, balcons, accès, toits et matériaux à l’échelle | Correspondance documentée photo → bâtiment, vues à hauteur de conduite |
| Critique | Rue très vide ; grandes surfaces terreuses entre volumes | Reconstituer les limites de parcelles, clôtures, arbres, cours, commerces et usages des trottoirs ; placement composé, avec visibilité et collisions | Même cadrage de rue avant/après, sans substitution d’une image de couverture |
| Haute | Frondes peu naturelles et troncs schématiques ; presque aucun houppier feuillu | Végétation aux silhouettes, ramifications et densités crédibles ; plusieurs variantes ; alpha, ombrage, vent subtil et LOD contrôlés | Gros plan et mouvement à hauteur de moto ; absence de scintillement et de feuilles opaques |
| Haute | Chaussée uniformément fissurée, répétitions et transitions franches | Caler les dimensions physiques des textures ; distinguer enrobé, réparations, poussière, bordures et drainage ; traces et usure localisées | Plaques de matière puis chaussée dans le moteur, vues proches et rasantes |
| Haute | Véhicules propres et simples, trafic visuellement pauvre | Formes de carrosserie, vitrage et intérieur visible ; pneus, éclairage et usure plausibles ; variantes locales à partir des références | Vues rapprochées et croisement animé, sans couleur uniforme tenant lieu de matière |
| Haute | Lumière diffuse et aplatie, peu d’ombres de contact, horizon peu construit | Une heure et une direction solaire cohérentes ; exposition, ciel, ombres, lumière indirecte et profondeur ; éclairage précalculé à étudier | Même réglage d’exposition sur six vues et pendant le parcours |
| Haute | Passants peu crédibles et animations insuffisantes | Personnages habillés et riggés ; marche, attente, course groupée, vendeur, receveur ; variété de silhouettes et transitions | Séquence dans le moteur ; pieds au sol et pas de glissement/interséction visible |
| Haute | Ambiance encore une maquette sonore | Sons originaux ou autorisés ; moteurs, appels, klaxons, conversation et musique ; spatialisation ; texte et prononciation à relire | Séquence de rue audible ; paroles proposées consignées pour relecture |

## Rue étalon et cohérence géographique

Conserver les 150–250 m prévus par W16. Le corridor actuel du Boulevard du 30 Juin est une **hypothèse de travail**, pas un choix validé du tronçon final. La question précédente sur la rue exacte reste ouverte ; elle n’empêche pas de collecter les références et de produire les objets réutilisables. Ne pas affirmer que le point de vue de l’image utilisateur correspond au tracé actuel, à une pente mesurée ou à un accès au port.

Les sources géographiques ne changent pas. Les détails artistiques ajoutés portent leur source et leur statut : observé, estimé ou inventé. Une photographie ancienne décrit une date, pas l’état présent de toute la ville. Les photos de Limete ou d’autres quartiers servent à comparer les usages, sans les présenter comme des façades de Gombe.

## Bibliothèque et fabrication

Le [catalogue de collecte](library/manifest.json) distingue photographies documentaires, matériaux PBR et modèles candidats. Les [sélections](library/selection.json) indiquent à quoi chaque ressource pourrait servir. La [liste de production](library/production-inventory.json) distingue les familles à fabriquer des objets réellement reçus. Une variante ou mille instances d’une même travée ne comptent pas comme mille créations.

Les modèles et textures Poly Haven sont sous [CC0](https://polyhaven.com/license). Les photographies Commons conservent auteur, date publiée, URL et licence individuelle. Elles sont collectées pour l’étude ; aucune photo n’est automatiquement plaquée sur un bâtiment. Les marques et inscriptions étrangères des objets candidats doivent être examinées et adaptées avant leur placement dans Kinshasa.

Les sources haute définition restent dans `/workspace/wewa-asset-library`, hors du bundle web. Le manifeste et l’outil `tools/collect_art_library.py` permettent leur récupération et la vérification de leurs empreintes. Les aperçus du fournisseur montrent ses ressources ; ce ne sont pas des images de notre jeu. Un arbre source de plusieurs centaines de Mo n’est pas un arbre prêt pour Safari.

Collecte de cette passe : 17 modèles candidats, 22 ensembles PBR et 29 photographies retenues après exclusions, 196 fichiers, environ 582 Mo. Les métadonnées de sept autres photographies ont été trouvées mais leurs fichiers ont répondu HTTP 429 ; elles ne sont pas comptées comme récupérées. Le fournisseur a livré 16 modèles contrôlés sans erreur glTF, avec des avertissements notamment sur les tangentes ; la source d’arbre très lourde reste hors de cette validation. Cinq imports réellement ouverts dans Blender 4.3.2 ont des dimensions relevées et aucune image manquante. Ces vérifications concernent les fichiers, pas leur qualité artistique finale. Les résultats sont dans `library/source-checks.json` et `library/blender-inspection.json`.

Pour reconstituer exactement les sources épinglées, sans relancer les recherches : `python3 tools/collect_art_library.py --out /workspace/wewa-asset-library --restore`. Pour vérifier les fichiers déjà présents : même commande avec `--verify`. L’outil refuse de placer la bibliothèque brute sous `app/`.

Pour chaque élément proche du joueur :

1. Référence identifiable, dimensions, usage local et vues nécessaires.
2. Sélection d’un modèle autorisé adapté ou modélisation dans Blender. Le recours au procédural sert les répétitions après validation d’un exemplaire.
3. Travail de forme, UV, détails de surface, matériaux et cuisson ; retopologie si nécessaire ; rig et animation pour les êtres vivants et véhicules.
4. Export, échelle et axes, LOD, collisions séparées, textures adaptées au moteur ; vérifier aussi l’alpha, les normales et la compression visuellement.
5. Intégration dans une scène de contrôle du **moteur réel**, lumière fixe et vues comparables. Corriger ce qui échoue avant la duplication dans la rue.
6. Assemblage de la rue étalon ; contrôle à pied puis en conduite ; seulement ensuite extension du quartier et des missions.

Chaque lot garde une capture, ses écarts ouverts et sa décision : à reprendre, candidat acceptable ou accepté par relecture. Aucun statut « fini » fondé sur l’absence d’erreurs glTF.

## Ordre des lots

| Lot | Contenu | Condition de passage |
|---|---|---|
| A | Inventaire, références et bibliothèque de ressources | Fichiers réels, droits, empreintes, adéquation et manques identifiés |
| B | Moto et pilote au premier plan ; chaussée et éclairage de contrôle | Silhouettes et matières convaincantes en vue arrière et au guidon dans le moteur |
| C | Façades et végétation de la rue étalon ; limites de parcelles, commerces et drainage | Rue reconnaissable et dense aux six cadrages, sans habillage générique masquant les erreurs |
| D | Minibus/taxis et passants animés ; vie et son de la rue | Croisements, attente et traversées crédibles en mouvement, dangers lisibles |
| E | Optimisation et intégration des missions dans l’étalon | Qualité préservée après LOD/compression, conduite fonctionnelle et budgets mesurés |
| F | Extension de Gombe puis autres quartiers et suite V1 | Rue étalon reçue ; sorties P1–P4 du plan toujours respectées |

Cette organisation détaille le travail artistique du plan existant ; elle ne remplace pas ses phases et n’en déclare aucune achevée.

## Contrôle visuel avant la prochaine prévisualisation artistique

Produire six captures dans le moteur : arrière en rue, trois quarts moto/pilote, vue au guidon, devanture et trottoir, minibus au croisement, profondeur de rue avec végétation. Ajouter une séquence continue de conduite avec virage, freinage, trafic et traversée de passants. Une image Blender séparée peut documenter le travail d’un asset, jamais prouver le rendu jouable.

Pour chaque vue, relire composition et échelle, forme des objets, détails de matière, ombres/lumière, densité et cohérence kinoise. Décrire les défauts précis ; ne pas attribuer un pourcentage arbitraire de photoréalisme ou substituer une comparaison de pixels entre deux lieux différents.

Avant de proposer une nouvelle prévisualisation comme amélioration artistique, vérifier qu’aucun défaut critique de la comparaison ne reste sans traitement. Le retour utilisateur reçoit ou refuse la fidélité locale et artistique. Cela ne nécessite pas de demander l’autorisation pour chaque téléchargement ou correction déjà autorisé.

Le test matériel sur iPhone 15/16 reste distinct. L’émulation Chromium ne mesure ni le GPU d’un iPhone, ni Safari, ni la chauffe. Les plafonds de `config/performance.json` restent des objectifs à vérifier ; la collecte hors ligne ne modifie pas ces plafonds ni le chargement public.

## État de cette reprise

Audit et collecte préparatoire ; pas de nouveau jeu annoncé, pas de nouvelle version publique publiée dans cette passe. Les ressources ne sont ni toutes adaptées à Kinshasa, ni optimisées, ni intégrées, ni artistiquement acceptées. Le pilote et les personnages réalistes, les façades documentées, les vrais palmiers, les animations et l’ambiance sont encore du travail de production.
