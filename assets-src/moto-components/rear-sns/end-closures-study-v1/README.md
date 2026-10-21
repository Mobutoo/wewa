# Fermetures extérieures SNS — études grises v1

Deux surfaces originales comblent les grands vides relevés dans la composition
historique des douze candidats. Elles sont conservées séparément de ces sources.
La scène Blender contient des copies importées du GLB historique pour examiner
les raccords ; elle ne constitue pas une moto complète ou un amortisseur reçu.

La préparation et ses hypothèses sont dans
`creative/research/rear-sns-end-closures-study-v1/preparation.json`.
La photo PF122033 apparentée a été récupérée depuis l'URL déjà documentée,
ouverte, et son empreinte vérifiée. Elle reste hors du dépôt public et ne fournit
aucune texture. Les sections nouvelles sont des estimations artistiques, pas des
mesures de l'exemplaire RDC.

Le candidat opposé couvre le vide radial et le court intervalle de tige. Le
candidat côté fût ajoute une enveloppe annulaire extérieure. **Sa lèvre de
travail de 0,15 mm et son jeu axial d'environ 0,85 mm au bord historique restent
à reprendre ou justifier.** Cette solution de revue ne certifie ni une coupelle
porteuse ni le contact avec le ressort. Aucun mécanisme hydraulique caché,
soudure, tolérance industrielle ou montage sur le véhicule n'est inventé.

Le premier congé automatique produisait 80 triangles dégénérés ; il a été
remplacé dans la source par des arrondis quadratiques de section. La première
enveloppe côté fût croisait le collier ; son profil rejeté et le résultat sont
conservés dans la préparation. Le profil courant ne croise pas les surfaces des
douze candidats dans le contrôle BVH. Ce contrôle ne détecte pas toute inclusion
volumique et ne certifie aucun contact mécanique.

Depuis la racine du dépôt, avec Blender 4.3.2 :

```sh
blender --background --python-exit-code 1 \
  --python assets-src/moto-components/rear-sns/end-closures-study-v1/build_and_check.py \
  -- --render
```

La commande vérifie l'empreinte d'entrée, construit les deux maillages, contrôle
leur fermeture, volume signé et triangles, puis leurs intersections et les
signatures des copies historiques. Elle sauvegarde une source `.blend`
autonome et deux exports GLB. Les images sont des rendus Cycles CPU 32 samples
sans débruitage, distincts des finales historiques Cycles96/OIDN. Les cadrages
sont contrôlés avant rendu. Le rapport lie chaque image à la source, au script,
à sa caméra et au protocole d'exposition.

Les fichiers et limites sont regroupés dans
`creative/reviews/rear-sns-end-closures-study-v1/`. Les deux études ne sont pas
ajoutées au compte des 92 composants candidats Source20. La matière, Babylon,
les fixations, les mouvements et les LOD restent à vérifier après correction de
forme. Aucune réception artistique ni qualification iPhone n'est acquise.
