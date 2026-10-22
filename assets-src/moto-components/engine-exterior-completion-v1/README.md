# Engine exterior completion v1 — variante conditionnelle à reprendre

Kit moteur séparé, huit objets, sources historiques inchangées. Pas G8, pas de moteur OEM complet déclaré. Les poses sont provisoires et les deux donneurs BM150 ne sont pas prouvés appariés.

## Inventaire rapide pour main

- `poses-and-sources.json` : chemins exacts, SHA256, matrices 4×4, axes et bornes estimées ; cinq pièces historiques + deux grands corps + un col de service.
- `sourcekit-preflight.json` : objets évalués, triangles, bornes et matières.
- `engine-exterior-completion-v1.blend` et `.glb` : moteur seulement ; main conserve répétitions et assemblage global. Aucun rendu whole lancé ici.
- `native-inventory.json` : lecture effective des onze sources moteur/carter ; ATTENTION les bornes brutes historiques incluent leur studio. `interfaces.json` isole les bonnes collections et leurs bornes utiles.
- `physical-observations.json` : photos réellement lues, URL/SHA/observations uniquement. Aucune photographie redistribuée.

## Audit v14 et limites visibles

V14 contient les couvercles LH/RH, sortie, cylindre et culasse ; aucun des sept nouveaux composants crankcase. Les flancs de carter manquent derrière les couvercles. Ajouter les corps n’est pas remplacer les couvercles amovibles. Chaque ancien couvercle est présent une seule fois ; aucune nouvelle révision de couvercle trouvée dans les sources auditées. Ne pas masquer un doublon par une réception implicite.

Le donneur LH contient déjà la bande périphérique inférieure : ne jamais ajouter `crankcase-lh-lower-peripheral-wall-v1` au-dessus. Les plans supérieurs LH/RH et le panneau de sortie restent des études distinctes : origine photographique différente, pas de matrice installée certifiable. Ils ne sont pas empilés artificiellement pour remplir le vide. Le col de service reprend le même exemplaire LH et sa projection, sans bouchon inventé.

Les grands corps existants sont des parois périphériques ouvertes. Ils ne reproduisent pas tout le relief photographié : bossages/attaches et flancs bombés LH restent insuffisants, raccord au cylindre non validé. Les ouvertures intérieures démontées ne sont pas des trous à boucher par un cube, un disque ou des soudures supposées. Les paliers, galeries et rouages ne sont pas documentés ici comme surfaces visibles en moteur assemblé. Le caractère visible de chaque vide en contexte doit être relu sur le global de main.

Les matrices calent le plan des couvercles à X=±0,105 m (bornes natives effectivement lues), profil longitudinal/vertical selon leurs enveloppes et celle du cylindre. La profondeur donneur est étirée provisoirement jusqu’au plan médian ; cette estimation n’est pas une mesure ni une preuve de raccord. Translation profil ±35 mm, plan axial ±20 mm, rotation ±12°, facteur de profondeur exploratoire 1,3–2,1. Les erreurs locales peuvent dépasser ces bornes : montage non certifié. Aucun weld ni géométrie cachée ajouté.

## Preuves

Le premier export incomplet est conservé dans `rejected-selection-export/`. `parity.json` compare réellement le GLB réimporté aux triangles natifs évalués ; `gltf-validation.json` contrôle le format séparément. Les trois vues natives utilisent 96 échantillons CPU, deux threads, EXR float32 + PNG. `runtime-check.json` et la capture correspondante concernent Babylon/Chromium logiciel, pas un iPhone physique. Seuls les rapports présents et réussis valent exécution.

## Suite nécessaire

Cette livraison corrige l’omission des corps pour comparaison ; elle ne finalise pas fidèlement tout le moteur. Avant installation définitive : résoudre le donneur et la profondeur réelle, caler le cylindre/les plans supérieurs, documenter les bossages manquants visibles et vérifier les raccords au cadre sur le global. Les documents physiques existants couvrent déjà le diagnostic présent ; pas de téléchargement redondant. Réception artistique utilisateur non obtenue.

## Livraison liée pour main

`engine-exterior-completion-v1-linked.blend` (environ 85 Ko), collection `WEWA_ENGINE_EXTERIOR_COMPLETION_V1_CONDITIONAL`, lie les huit sources exactes. Réouverture et triangles contrôlés dans `linked-wrapper-check.json`. Pour v14, utiliser seulement `add_only` dans `main-integration-fragment.json` ; les cinq objets moteur historiques y sont déjà. Si le wrapper complet remplace le groupe moteur, retirer explicitement ces cinq parents de v14, jamais les doubler.

Les vues gauche/droite montrent une marge inférieure excessive des enveloppes donneuses sous les couvercles : pose/contour à reprendre avant installation. Les photographies ne justifient pas de déclarer ce raccord fidèle. Les trois rendus restent une preuve de comparaison d’un candidat rejetable, pas une réception. Aucun moteur générique ajouté.

Le wrapper lié est le livrable conseillé pour intégration ; le GLB technique séparé (moins de 100 MiB) est uniquement la preuve d’export/parité déjà exécutée, aucune recopie nécessaire pour main.
