# Patin de chaîne apparenté JB122003 — premier candidat partiel

Anneau, fourche, entretoise et profils ajourés construits en source native. **Les bouches visibles des deux extrémités ne sont pas fabriquées** : leur axe et leur chemin caché restent indécidables sur les deux obliques du même côté. Les pointes sont seulement des enveloppes candidates ; G3/G5 du composant complet restent ouverts. Aucun boulon, rondelle, chaîne ou mécanisme caché n'est inclus.

Références effectivement ouvertes : [BikeBox SKU JB122003 pour Boxer](https://bikeboxmt.com/shop/boxer-chain-slider-genuine/) et [KMMotos SKU JB122003 pour Pulsar135](https://www.kmmotos.com/products/deslizador-de-cadena-ps135-pulsar-hueso). Elles montrent le côté ouvert sous des angles différents, pas deux faces complémentaires d'un spécimen certifié. Ni identité125HD RDC, ni dimensions, ni dureté ou contact chaîne ne sont établis. Les originaux et leurs empreintes restent dans le dossier documentaire privé ; aucun pixel n'est redistribué ou employé comme texture.

Toutes valeurs métriques sont des estimations bornées : longueur construite185mm environ, anneau34/44mm de diamètres, largeur25mm, bande arrondie0,6mm et rainure candidate0,25mm. Aucune de ces valeurs n'est tirée comme mesure d'un quadrillage/photo ou de la cote estimée du bras. Les profils se construisent dans YZ et s'étendent enX ; datum centre d'anneau0, +Y vers pointes et Z entre les deux branches. La pose, la face de roulement et les contacts réels restent inconnus.

Collection `WEWA_SWINGARM_CHAIN_SLIDER_ISOLATED`, studio séparé non exporté. La source construit un contour original, vraie bouche annulaire, petite fenêtre et longue fourche libre, avec triangulation contrainte distribuée avant relief. Les rayons de bord sont des sections partagées avec les deux faces et les parois. Aucun remeshing, import d'une pièce ou réparation des buffers après export. Une rainure faible est géométrique sur la face observée ; l'opposée reste une enveloppe plane estimée, pas une vue relevée.

Dans une copie isolée depuis la racine, Blender4.3.2 avec numpy embarqué, dépendances Node verrouillées du dépôt :

```sh
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/swingarm/chain-slider/build.py
node assets-src/moto-components/swingarm/chain-slider/check_export.mjs
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/swingarm/chain-slider/inspect_interfaces.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/swingarm/chain-slider/render.py -- --view=quarter --view=face --view=reverse-quarter
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/swingarm/chain-slider/render.py -- --reflection --view=ring-detail --view=bridge-detail --view=groove-detail
```

Les contrôles de fermeture/volume positif et les trois vides réels ne réceptionnent ni la forme ni la fonction. La bande de largeur du témoin provient du dessin25mm moins la rainure jusqu'à0,25mm ; ce n'est pas une tolérance OEM ni une métrologie. Les caméras/éclairages/exposition et sources sont liés aux PNG. Aucune réception artistique, montage, résistance, LOD ou qualification iPhone physique n'est acquis.


Les premiers gris583a6d20 et les gris/reflets à grille mixte e07ba29c sont conservés en diagnostics. La rainure possède maintenant un supportC2 compact, car une queue de gaussienne fondée sur la distance minimale aux deux bords formait une petite crête à la médiane. Ensuite une ondulation de discrétisation de7,67µm sur une seule ligne témoin a été mesurée dans les vrais triangles. Les rangées contraintes suivant le contour remplacent les deux grilles mélangées :265364→147776triangles, sans masquer par matière. `inspect_groove_sampling.py` utilise des barycentriques float64 directs et compare quatre lignes de121points au champ d’auteur. Ses très petits résidus numériques ne mesurent pas l’erreur globale ni la fidélité à une pièce OEM.

Les scripts `diagnostics/profile-before-compact.py` et `diagnostics/build-before-contour-bands.py` conservent les recettes antérieures originales : les restaurer respectivement en `profile_shape.py`/`build.py` dans une copie isolée avant rejeu, car leurs chemins supposent leur emplacement d’origine. Ne jamais rejouer sur les gels historiques. Les limites de bouches d’extrémité et face opposée restent ouvertes malgré les contrôles techniques.

## Matière candidate et rejeu

Le sombre proposé est un élastomère d’apparence, sans dureté, polymère ou réflectance mesurés : base linéaire (.007,.008,.009), métal0, rugosité.62 et relief normal de force.18. Deux cartes périodiques originales512², domaine auteur5mm et hauteur RMS estimée1µm ; aucun pixel de photo, poussière ou usure copiée. Les cartes sont embarquées et leurs chemins relatifs. Le grain n’est pas utilisé pour masquer une erreur de géométrie ; les vrais POSITION/NORMAL/UV/TANGENT/indices/matrices sont comparés exactement à la baseline publique `g3-master-v1`.

Après restitution de cette baseline dans une copie isolée et sa revue gris rattachée aux SHA exacts :

```sh
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/swingarm/chain-slider/material.py
node assets-src/moto-components/swingarm/chain-slider/check_export.mjs
node assets-src/moto-components/swingarm/chain-slider/check_material_preservation.mjs
python assets-src/moto-components/swingarm/chain-slider/inspect_material.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/swingarm/chain-slider/inspect_interfaces.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/swingarm/chain-slider/render.py -- --material-preview --view=quarter --view=reverse-quarter --view=ring-detail --view=groove-detail
```

La revue des aperçus et des limites précède le gel explicite `record.py --freeze`. Cinq vues finales1400×1000,96samples avec checkpoints indépendants par vue :

```sh
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/swingarm/chain-slider/render.py -- --final --view=quarter --view=face --view=reverse-quarter --view=ring-detail --view=groove-detail
```

La macro est volontairement recadrée ; les trois vues globales gardent la pièce entière. Le contrôle caméra vérifie les sommets évalués et le clipping avant calcul. Les preuves techniques ne ferment pas les bouches manquantes ni le contact opposé inconnu. `record.py` exige la lecture réelle des cinq PNG et les SHA des sources, puis enregistre uniquement une liste explicite de fichiers auteur, jamais les preuves moteur de root.
