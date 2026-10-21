# Rétroviseur gauche — revue du candidat v1

Source bdd8a799b6a5ae07a5c076ba0c5a1019f6477ff9a4be5995229e13c2def3c6d0 ; GLB fb796f4bbe842b7080ba5310aeab653a5fbc72d647f3a2c113309e27f256f8fa. Détail de construction, provenance, commandes et limites dans `assets-src/moto-components/mirrors/README-left.md`.

Vues finales réellement calculées : `whole-front.png`, `whole-back.png`, `joint-close.png` ;1000×800, Cycles96/OpenImageDenoise CPU. Les trois checkpoints `final-render-checkpoints.json` contiennent source/configuration, PNG/EXR hachés et canaux EXR réellement lus (Combined/Noisy Image/Albedo/Normal). Les EXR restent privés.

La coque/verre/couche/bande de bord n’ont pas changé depuis les deux études de tête réelles (`head-glass-reflections.png`, `head-back-grain.png`), avec preuve des quatre maillages, attributs, matières/images et transformations dans `head-to-full-identity-check.json`. Le sol de studio diffère ; ce n’est pas une preuve de parité visuelle dans le moteur.

La première vue entière provisoire a révélé un col trop ouvert et un écrou masqué : diagnostic et anciens fichiers privés reliés par `rejected-joint-gap.json`. Les caches ont été repris depuis les détails natifs : deux étages cylindriques au pied, intervalle fileté/écrou, deux lèvres/rainures et capot emboîté au col. La dernière vue rapprochée montre ce raccord sans rotule exposée. La lèvre, les épaisseurs et le mécanisme interne restent des estimations, sans plan de détail.

`source-geometry-check.json`, `final-export-check.json`, `motion-mount-check.json` et `whole-view-framing-check.json` documentent les contrôles effectifs : dix solides fermés,112204triangles sans aire nulle, glTF0/0, normales/tangentes et pixels PBR réels,45couples au repos, neuf poses de tête et cinq poses du levier lié sans traversée, trois alésages ouverts, cadrages entiers. Le maillage est une version détaillée de revue, pas une qualification iPhone.

L’identité actuelle RDC, les dimensions individuelles, le verre gauche isolé, la courbure, le chemin de tige en profondeur, le filetage, l’articulation et certaines matières restent ouverts. Les photos liées ne sont pas des plans métriques et le RH n’est pas automatiquement un miroir exact du LH. Aucune réception artistique, OEM ou sur téléphone physique n’est déduite des contrôles.
