# Poignées isolées — révision v3

Cette révision reprend la forme des longs motifs arrondis observés sur la photo voisine DU191009 : empreinte plus large, col plus long et collerette plus grande. La v2 conserve son état historique ; ses fins canaux ne servent plus de cible de forme. La photo ne démontre ni le nombre complet de motifs ni leur signe de relief. Huit empreintes de largeur6mm, longueur75mm et retrait0,4mm sont des paramètres de travail estimés, dans une plage de relief −0,6 à+0,6mm. La référence RH demeure insuffisante pour certifier son moule complet.

La gauche physique est+X, la droite−X pour le pilote en+Y regardant−Y. Les datums et les cavités restent ceux de la v2 : extrémités (±0,340;0,085;0,105)m, longueur120mm, alésages gauche Ø22,4mm et droit Ø25,4mm. La collerette passe à Ø46mm estimé. Aucune de ces cotes n’est une mesure physique du modèle RDC. Le manchon accélérateur est un candidat séparé.

Collection `WEWA_HANDLEBAR_GRIP_ENVELOPES`, objets `Left rubber grip - editable candidate` et `Right rubber grip - editable candidate`. Le Blender `handlebar-grips-v3.blend` conserve le modèle détaillé ; le GLB `handlebar-grips-v3-inspection.glb` exporte ce détail sans la décimation de la v2. Les deux volumes fermés incluent cavité, fond, collerette et relief. Il ne s’agit pas encore d’un LOD jeu.

Le caoutchouc PBR noir et la carte originale de rugosité périodique sont conservés. Aucun pixel photographique n’est utilisé. Le protocole studio réduit la puissance des lampes à8% de celle des anciennes vues surexposées, sans éclaircir l’albédo. Ce protocole reste une comparaison artistique, pas une mesure colorimétrique.

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/handlebar-grips/build_v3.py
node assets-src/moto-components/handlebar-grips/check_export_v3.mjs
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/handlebar-grips/render_v3.py
python assets-src/moto-components/handlebar-grips/record_review_v3.py
```

Voir [hypothèses et photos](../../../creative/research/handlebar-grips/footprint-v3.json), [paramètres](parameters-v3.json) et [preuves](../../../creative/reviews/handlebar-grips-v3/README.md). Les vérifications de surface avec commodos, leviers, rotor et guide sont indépendantes de la réception artistique. Variante RDC, ajustement réel, usage Safari physique et budget scène restent non qualifiés.
