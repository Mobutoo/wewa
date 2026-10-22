import json,hashlib
from pathlib import Path
R=Path('/workspace/wewa');O=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=['creative/research/powertrain-completion-p18-v1/used-casting-and-dependency-evidence-v76.json','creative/research/powertrain-completion-p18-v1/rh-major-envelope-physical-evidence-v99.json'];rows=[]
for f in files:
 data=json.loads((R/f).read_text());data=data['sources'][0] if 'sources' in data else data
 for x in data['images']:
  n=x['url'].split('/')[-1].split('.')[0]
  if n not in ['65221','65222','65202']:continue
  p=Path(x['private_path']);assert sha(p)==x['sha256'];rows.append(dict(url=x['url'],sha256=x['sha256'],observations={'65221':'LH complete profile, real lower service mouth and rear output face; independent donor JE541038.','65222':'LH external depth and upper saddle; wall has major outward forms and mounting bosses missing from simplified source wall.','65202':'RH independent clutch-side profile, outer bored bosses, visible internals are not modeled.'}[n],actual_image_read=True,redistribution='not included; documentary observation only'))
(O/'physical-observations.json').write_text(json.dumps(rows,indent=2))
(O/'README.md').write_text('''# Engine exterior completion v1 — variante conditionnelle à reprendre

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
''')
