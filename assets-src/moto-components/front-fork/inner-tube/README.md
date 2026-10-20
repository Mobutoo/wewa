# Tube intérieur de fourche — candidat isolé

Un seul tube creux original, référence documentaire **PF121017 d’une variante liée BM150/X**. L’identité exacte du tube actuellement monté sur la125HD RDC reste inconnue. Il ne constitue ni une jambe complète ni une fourche assemblée.

Les photos réelles montrent une extrémité ouverte filetée intérieurement et, à l’autre bout, une portée étagée avec deux gorges fines. La section originale continue reproduit ces détails observables. Le petit point noir près de l’épaulement reste ambigu : aucun orifice d’huile n’est inventé.

Le diamètre de travail31mm provient uniquement de la mention de joint«31DiaFork» des catalogues liésD04/D15. Il n’est pas certifié pour la référenceRDC. Longueur550mm(plage480–650), paroi3mm(plage2–4), longueur de portée55mm(plage35–75), diamètres des bouts, gorges, pas1mm et profondeur0,45mm du filet : **estimations de reconstruction**, aucun standard de bouchon ni montage compatible annoncé. Les photos en perspective ne fournissent aucune calibration globale pixels/mm.

Repère local : axe+Z, origine au bout inférieur usiné, ouverture filetée àZ550mm. Collection `WEWA_FORK_INNER_TUBE_ISOLATED`, source `front-fork-inner-tube-v1.blend`, export évalué `front-fork-inner-tube-inspection.glb`. Aucune pose installée ni longueur de course appliquée. La source ne contient qu’un tube et son studio distinct non exporté.

La paroi est un volume continu fermé autour d’un passage axial ouvert. Les contrôles source et GLB portent sur connectivité, volume, passage central, présence des lèvres, aires de triangles et tangentes. La source utilise320secteurs pour réduire la facettisation des reflets en macro. Les filetages sont de la géométrie réelle ; ils ne sont pas qualifiés pour un assemblage fonctionnel.

Trois réponses de surface distinguent chrome visuel poli, usinage inférieur et acier intérieur. Les quatre cartes512² originales proviennent d’un champ périodique calculé, sans pixel photographique. UV cylindriques référencés à la circonférence extérieure31mm, et projection plane des deux lèvres. Tuile8mm sur la partie principale et les lèvres ; sur la portée inférieure et la paroi intérieure la projection conserve cette référence extérieure, soit environ7,69mm et6,45mm par répétition circonférentielle. Cette différence connue reste une approximation de surface, sans cote OEM. Hauteur RMS0,12µm avant intensité, corrélations0,8mm en circonférence et0,08mm en longueur : échelles **estimées**. La rugosité et le métallique sont des réglages d’apparence, pas des mesures chimiques. Les canaux des images réellement embarquées sont comparés aux PNGs source.

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/front-fork/inner-tube/build.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/front-fork/inner-tube/material.py
node assets-src/moto-components/front-fork/inner-tube/check_export.mjs
python assets-src/moto-components/front-fork/inner-tube/inspect_material.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/front-fork/inner-tube/render.py
```

La source haute définition sert à la revue ; LOD mobile, coût dans une scène représentative, compatibilité des fourreaux, tés et bouchons, réception artistique et qualification sur Safari physique restent ouverts.
