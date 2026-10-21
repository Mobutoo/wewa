# Contrôle indépendant des rotations combinées

`check_blender_browser_rotation_parity.py` compare un vrai sommet du bord de tête évalué dans Blender avec le même point réellement chargé dans Babylon. Les deux nouveaux outils ne changent ni source, ni export, ni inspecteur historique. Ils écrivent uniquement dans un nouveau dossier de preuves ; un dossier déjà utilisé est refusé.

Le contrat JSON doit être écrit après gel du candidat. Les axes attendus viennent des coordonnées et paramètres **source**, indépendamment des matrices du navigateur. Pour le rétroviseur droit, la composition attendue est `rest @ yaw @ pitch`, autour du Z Blender puis de `head_pitch_axis_world`. Le pivot doit être sans rotation/échelle au repos ; le programme refuse une autre hypothèse de repère. Les limites sont celles du candidat, sans certification OEM.

Exemple de structure à compléter avec les chemins et empreintes effectivement gelés :

```json
{
  "source": "assets-src/moto-components/mirrors/mirror-right-v2.blend",
  "export": "assets-src/moto-components/mirrors/mirror-right-v2.glb",
  "source_parameters": "assets-src/moto-components/mirrors/parameters-right-v2.json",
  "source_sha256": "A_COMPLETER_APRES_GEL",
  "export_sha256": "A_COMPLETER_APRES_GEL",
  "source_parameters_sha256": "A_COMPLETER_APRES_GEL",
  "collection": "WEWA_MIRROR_RIGHT",
  "pivot": "RH mirror head adjustment PIVOT",
  "witness_mesh": "RH continuous mirror edge seal - estimated",
  "source_rotation_order": [
    {"control_id": "yaw", "axis_source": [0, 0, 1]},
    {"control_id": "pitch", "parameter_property": "head_pitch_axis_world"}
  ],
  "poses": [
    {"name": "rest", "controls": {"yaw": 0, "pitch": 0}},
    {"name": "positive_yaw_positive_pitch", "controls": {"yaw": 10, "pitch": 7}},
    {"name": "negative_yaw_positive_pitch", "controls": {"yaw": -10, "pitch": 7}},
    {"name": "positive_yaw_negative_pitch", "controls": {"yaw": 7, "pitch": -5}}
  ]
}
```

Après vérification qu'un CPU est libre, exécuter sur le serveur de revue existant :

```sh
python tools/check_blender_browser_rotation_parity.py \
  --catalog-key mirror-right-v2 \
  --spec /chemin/contrat-gele.json \
  --out-dir /chemin/preuves-nouvelles \
  --cpu 3
```

L'extraction courte utilise Blender `--threads 1`, sans rendu/export/sauvegarde. Elle choisit le sommet évalué le plus éloigné du pivot dans la vraie bande de bord, puis évalue les quatre poses et les poses avec ordre inversé. Au moins trois combinaisons distinctes doivent séparer les deux ordres de plus de dix fois la tolérance. Aucun témoin source n'est reconstruit depuis une matrice Babylon.

Le navigateur trouve ce point au repos dans le maillage nommé, conserve cet index dans toutes les poses et lit ses positions chargées et sa matrice réelle. Les éventuels doublons de position dus à l'export sont comptés. Les octets du GLB reçu par HTTP doivent avoir l'empreinte attendue ; le catalogue sélectionné doit correspondre à la source ; toute pose clampée est refusée. La conversion Blender→glTF est `(x,z,-y)`.

Le rapport conserve les deux positions, l'erreur en mètres, le contre-témoin d'ordre inversé et les empreintes des outils/contrat/inspecteur. Une erreur supérieure à `2e-7 m` ou une erreur JavaScript/HTTP fait échouer le contrôle. Cette tolérance numérique ne représente ni une cote de fabrication ni une précision OEM. Le résultat concerne un témoin de bord et ces poses, sans validation de toute la géométrie, de la matière, des butées mécaniques ou d'un iPhone physique.
