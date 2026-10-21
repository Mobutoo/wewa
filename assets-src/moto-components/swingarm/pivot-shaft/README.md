# Axe de pivot apparenté JA121003 — candidat isolé

Les deux vraies photographies du même exemplaire [MotoZilla BM/BMX150](https://motozilla.com.ua/product/boxer-bm-vmx-150cc-os-mayatnika-d12mm-l260mm-ja121003-c-razborki-novyy-bajaj-358102/) montrent un long fût clair, une extrémité filetée réduite, une tête hexagonale et une zone large près de la tête. La photographie annotée donne **260mm hors tout apparent, 14mm fût et 12mm filetage**. Ce sont des données vendeur apparentées, sans instrument/tolérance ni certificat constructeur ou identité125HD RDC. Le titre simplifie «d12» ; il ne cote pas tout le fût à12mm. Le pas du quadrillage n’est jamais utilisé comme règle.

Toutes les autres dimensions et la forme du filet sont estimées et bornées dans `parameters.json` : pas1,25mm, longueur de zone filetée24mm, tête17mm entre plats/7,4mm d’épaisseur, zone de collerette20,5mm. Le sens droit et le profil original à crête/fond adoucis sont des choix de candidat, pas une norme ISO ou un engagement certifié. La zone près de tête peut être une rondelle séparée ou une collerette ; faute de preuve, elle reste provisoirement intégrée à notre enveloppe visible. Aucune nouvelle rondelle n’est comptée et cette interprétation peut être reprise. Aucun marquage, grade8.8, logo ou écrou inventé.

Repère en mètres : centre0, axeX, extrémités±130mm ; tête+X et filetage−X pour inspection, **côté de montage inconnu**. +Yarrière/+Zhaut. Collection `WEWA_SWINGARM_PIVOT_SHAFT_ISOLATED`, un seul volume fermé. Aucun montage avec le bras, les bagues ou le cadre n’est certifié, aucune charge/rigidité simulée.

La forme est une surface native à anneaux partagés, pas une union CSG : fût, réduction, hélice, retours, faces annulaires, contour hexagonal arrondi et chanfrein. Les limites axiales sont explicites, les extrémités sont réellement capées. 456angles circonférentiels (384uniformes complétés aux véritables arcs des six coins) et 32intervalles par pas de filet ; 694 944triangles détaillés. La géométrie et les normales auteur restent éditables dans `build.py`. La normale dérive des tangentes de surface, avec plans d’extrémité±X. Les UV sont continus par plage, avec plans de capes projetés en5mm ; les rayons variables changent localement la densité circonférentielle.

Le vérificateur initial des normales décodées contre l’axe parfait à1e−6 a échoué. Son diagnostic est conservé : les plans géométriques sont exacts à4,77nm de stockage et les normales décodées s’écartent d’environ0,00035. Rejouer les normales **exactement axiales** sur une copie RAM redonne bit pour bit les normales sauvegardées ; l’écart appartient à l’encodage Blender et n’est pas corrigé dans les buffers. L’essai RAM «ombrage plat seulement» les aggravait et n’a pas été appliqué. Ce constat numérique ne remplace pas les macros diffus/reflets. Les deux premières macros tête, mal éclairées devant le plan+X, restent des diagnostics ; un témoin frontal RAM distinct révèle ensuite cette face.

## Reproduction dans une copie isolée

Blender4.3.2, dépendances Node du dépôt, Python/Pillow/numpy pour les pixels et manifestes. Depuis la racine, remplacer BLENDER par son binaire. Les commandes écrasent les sorties actives : ne jamais les rejouer sur un gel historique.

```sh
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/swingarm/pivot-shaft/build.py
node assets-src/moto-components/swingarm/pivot-shaft/check_export.mjs
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/swingarm/pivot-shaft/inspect_interfaces.py
```

La recette de matière exige les empreintes G3 de la revue réelle. Pour la rejouer exactement, restaurer dans la copie isolée les deux binaires `g3-master-v1/` et son contrôle source au chemin actif/revue avant `material.py`. Cette entrée exacte reste publique, sans photo ni bibliothèque externe. `material.py` n’est pas réapplicable directement au PBR. Le protocole `diagnostics/render-before-head-witness.py` est une copie byte-identique du premier script à restaurer à l’emplacement `render.py` dans une autre copie isolée si l’on étudie les diagnostics ; il n’est pas destiné à être exécuté sous son chemin d’archive.

```sh
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/swingarm/pivot-shaft/material.py
node assets-src/moto-components/swingarm/pivot-shaft/check_export.mjs
node assets-src/moto-components/swingarm/pivot-shaft/check_material_preservation.mjs
python assets-src/moto-components/swingarm/pivot-shaft/inspect_material.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/swingarm/pivot-shaft/inspect_interfaces.py
BLENDER --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/swingarm/pivot-shaft/render.py -- --final --view=quarter --view=side --view=head-detail --view=thread-detail
```

Réponse métallique claire originale estimée : base linéaire(.50,.52,.55), métal1, rugosité≈.30, deux cartes512² normale/ORM, tuile de bruit nominale5mm et reliefRMS0,12µm/force0,10. Ni composition, traitement de surface, reflet ni teinte ne sont mesurés. Aucune usure ou dominante verte photographique n’est copiée dans l’albédo. Images relatives/embarquées ; fermeture/aires/UV/tangentes/canaux réels contrôlés avant les vues coûteuses. Les quatre PNG96 sont cadrés sur les vrais sommets avec checkpoints de lumière/script/source/export. Studio séparé non exporté, sources portables et aucune modification du GLB après export.

Le candidat détaillé n’est pas un LOD de jeu qualifié. Babylon, réception artistique et iPhone physique restent distincts des contrôles locaux ; preuves moteur attribuées à root, jamais aspirées automatiquement dans le manifeste A.
