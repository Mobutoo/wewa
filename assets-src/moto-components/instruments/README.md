# Compteurs — candidat séparé pour la vue de conduite

La référence visible est la [photo officielle publiée sur la page RDC](https://cdn.bajajauto.com/fr-cd/-/media/globalbajajauto/common-media/features/boxer/125-hd/bm150_usb_feature_image.png) : vitesse 0–140 km/h à gauche, carburant E/F et rapports1–5 à droite, capuchon USB et avertissement au centre. Le nom du fichier contient BM150 ; le numéro de l’ensemble réellement livré en RDC reste inconnu. Le [rapport documentaire](../../../creative/research/instruments/README.md) conserve cette ambiguïté, les variantes et les empreintes.

Source : `instruments-v1.blend`. Les coques, lunettes, joints, vitres fermées, cadrans, aiguilles et capuchon sont séparés. Les graduations, chiffres, pictogramme carburant et texte WEWA sont redessinés en géométrie vectorielle ; aucun pixel de photo fabricant n’est incorporé. Les marquages et aiguilles sont des surfaces planes, pas des volumes mécaniques. Les corps structurels reçoivent leurs contrôles de fermeture et de volume.

**Toutes les dimensions physiques sont estimées.** L’écartement de travail est128 mm ; le diamètre extérieur des pods100 mm. Sections arrière, supports, courbure des vitres et placement relatif au tube ne sont pas mesurés. La position du contact n’est pas inventée. Le capuchon USB reste fermé ; le connecteur caché et le câblage ne sont pas fabriqués. L’odomètre est encore statique.

Les pivots `SPEED_NEEDLE_PIVOT` et `FUEL_NEEDLE_PIVOT` restent distincts dans le GLB. La revue Babylon.js commande réellement ces nœuds et propose l’éclairage vert du rapport actif ; la couleur active et la calibration carburant sont des conventions de démonstration à examiner, pas une mesure constructeur. Cette commande locale n’est pas encore reliée à la simulation du jeu.

Les vitres utilisent `KHR_materials_transmission`. Les ombres réfractives/caustiques du couvercle sont omises dans le studio Blender, comme les ombres des vitres dans la revue moteur. Le transfert glTF et la lisibilité sont contrôlés ; l’équivalence photométrique et la performance iPhone restent ouvertes.

```sh
blender --background --threads 2 --python-exit-code 1 --python assets-src/moto-components/instruments/build.py
node tools/check_cockpit_exports.mjs instruments
blender --background --threads 2 --python-exit-code 1 --python assets-src/moto-components/instruments/render.py -- --denoise --samples 128
```

La distribution officielle Blender avec OpenImageDenoise permet l’option `-- --denoise` du script de rendu. Version, nombre d’échantillons et débruitage sont consignés dans chaque rapport. [Revue isolée](../../../creative/reviews/instruments-v1/README.md) · [assemblage de revue](../../../creative/reviews/cockpit-v1/README.md). Aucune réception artistique acquise.
