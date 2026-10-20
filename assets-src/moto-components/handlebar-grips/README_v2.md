# Poignées isolées — révision v2

Cette révision corrige l’attribution physique des deux côtés. Le pilote regarde −Y depuis +Y : sa gauche est +X, sa droite est −X. La poignée gauche possède l’alésage candidat Ø22,4 mm ; la droite Ø25,4 mm réservé au manchon. La v1 historique reste intacte, avec ses noms de côtés inversés pour cette vue conducteur.

Le tube symétrique n’est pas modifié. Extrémités (±0,340 ; 0,085 ; 0,105) m, longueur de poignée 120 mm, corps Ø29,6 mm et collerette Ø41 mm : toutes ces cotes sont estimées. Les deux cavités, le fond et les canaux sont des surfaces fermées et non de simples cylindres superposés. Les canaux longitudinaux, le profil du col et la fermeture sont des interprétations bornées de références voisines ; ni la variante RDC ni le motif complet ne sont certifiés.

Collection source `WEWA_HANDLEBAR_GRIP_ENVELOPES`, deux objets `Left rubber grip - editable candidate` et `Right rubber grip - editable candidate`. Le [GLB](handlebar-grips-v2-inspection.glb) contient ces deux poignées seulement ; le [Blender](handlebar-grips-v2.blend) garde source éditable et scène studio séparée. La carte originale de rugosité est embarquée dans le GLB. Aucun pixel photographique n’est utilisé.

Reproduction depuis la racine du dépôt :

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/handlebar-grips/build_v2.py
node assets-src/moto-components/handlebar-grips/check_export_v2.mjs
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/handlebar-grips/render_v2.py
```

Les rendus Cycles 96 échantillons/OIDN montrent chaque poignée seule. L’éclairage studio produit un dessus gris malgré l’albédo sombre ; ce rendu ne constitue pas une mesure de couleur ni une réception de caoutchouc réaliste. Voir [recherche](../../../creative/research/handlebar-grips/reference-observations.json), [paramètres](parameters-v2.json) et [revue](../../../creative/reviews/handlebar-grips-v2/README.md). Aucun LOD jeu, usage mécanique complet, essai Safari physique ou accord artistique n’est acquis.
