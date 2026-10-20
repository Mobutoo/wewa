# Commodo droit — candidat partiel v1

La125HD commercialisée enRDC montre une petite commande rouge sur le dessus. Sa fonction et son numéro exact restent inconnus ; les références liéesPF401417 etPF401408 sont tout noires et ne peuvent pas la remplacer silencieusement.

`switchgear-right-v1.blend` : collection originale `WEWA_SWITCHGEAR_RIGHT`. `switchgear-right-inspection.glb` : 21076triangles évalués. Mètres, droite physique−X, +Ypilote et Zhaut. `parameters.json` déclare toutes les estimations ; `controls.json` n'assigne aucune action de jeu à la commande rouge. Sa course .4mm n'est qu'une hypothèse géométrique pour revue, ni démarreur ni coupe-circuit identifié.

Coques originales creuses par sections arrondies, joint .3mm, passage tube, bossages percés et vis estimées. ChambreR19mm/q.1205..1305 réservée au manchon/roue séparé, sortie de guide évidée àq.126. La coque ne recrée ni le manchon/roue/guide ni le support de levier, possédés par leurs lots. Les boutons noirs non résolus et le faisceau sont absents.

L'ancien corps trop facetté/gris a été repris : sections adoucies, polymère sombre linéaire(.004,.005,.006), grain original10mm/RMS4µm et rugosité déterministe. Aucune photo-texture ou mesh importé. Grain et géométrie restent des hypothèses. Le bevel global post-booléens produisait un triangle nul ; il a été retiré des coques car les rayons de silhouette sont déjà construits dans les sections. Aucun élargissement de seuil pour forcer une fermeture ; seuls doublons float stricts sont fusionnés. Les six corps sont fermés, connectés et à volumes positifs.

La finalisation d'export confirme qu'aucune correction de tangente n'est nécessaire après marquage des angles francs ; aucun triangle nul n'est accepté. Le rapport prouve octets des positions/normales/UV/indices, états des matières et images inchangés. Ce n'est pas une garantie de parité visuelleMikk.

Reconstruction depuis la racine (une reconstruction invalide toutes les empreintes précédentes) :

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/switchgear-right/build.py
node assets-src/moto-components/switchgear-right/check_export.mjs
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/switchgear-right/check_interface.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/switchgear-right/check_brake_interface.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/switchgear-right/render.py
```

Outils : Blender4.3.2 officiel, Manifold3D3.3.2 etNodeIO. Cycles96/OIDNCPU, passes activées mais EXRbrut non archivé. Les scripts de revue lisent les empreintes exactes sans sauver les sources externes.

SourceSHA256 `84182072eb72607cf3b9a029cf4e09964f8b4a86df612bfed912d0d666e9087c` ; GLBSHA256 `33e78f6f5f8bdb9745a6af10701e6d610c12fd94603c61afa37362bd57714e4d`.

[Preuves](../../../creative/reviews/switchgear-right-v1/README.md), [contradictions documentaires](../../../creative/research/switchgear-right/README.md). Reproduction exacteRDC, réception artistique et qualificationiPhone non acquises.
