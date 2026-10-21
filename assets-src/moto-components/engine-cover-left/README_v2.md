# Carter magnéto gauche — reprise isolée v2

`MOTO-ENGINE-COVER-LEFT-001` garde son identité et son repère. Cette révision corrige les trois fixations candidates de la v1 ; cette source historique et ses images restent intactes.

La peau courbe de la v1 traversait le plan des couronnes : le calcul du cylindre utilisait seulement la hauteur au centre. Les rayons sur la vraie construction ont montré jusqu’à 3,48–8,43 mm de dépassement autour des trois couronnes. Les normales personnalisées étaient déjà absentes. Ce défaut géométrique ne pouvait donc pas être résolu par le correctif de normales du carter droit.

La v2 raccorde progressivement la peau à des plages planes, avec des pieds locaux élargis et des appuis intérieurs évasés. Un maillage contraint suit les anneaux des plages et leurs transitions ; les triangles extérieurs à la silhouette concave sont explicitement retirés, puis les arêtes, l’aire et le contour sont contrôlés. Les premières variantes non gelées ont été refusées pour des stries puis une enveloppe convexe ajoutée. Les profils des appuis se raccordent directement aux anneaux de la peau intérieure, sans union tangentielle. Les plans d’appui et centres historiques restent estimés et conservés. Un premier essai relevant les plans au-dessus du maximum de peau a été écarté : le diagnostic du modèle n’établit pas une hauteur OEM. Les transitions C1 de la peau et du contour ne sont pas des congés circulaires de rayon constant. Les lèvres de support et d’entrée d’alésage utilisent des sections arrondies explicites ; leurs rayons sont estimés.

Les vraies arêtes du chant sont conservées par un seuil géométrique de 0,70 radian ; les transitions arrondies détaillées restent lissées. Le test qui effaçait toutes les arêtes hors du plan arrière produisait une ondulation de reflet sur le chant et a été écarté. Cette dernière finition ne déplace aucun triangle, contrairement à la reprise géométrique initiale par rapport à la v1.

Les trois passages restent ouverts, le corps est fermé, positif et connexe ; les buffers du véritable GLB sont examinés. La vérification des plages mesure les erreurs de hauteur des rayons, en gardant les petits écarts de triangulation comme résultats chiffrés. Ce contrôle géométrique ne constitue pas une tolérance d’usinage de la moto réelle. Le cache arrière gauche lié reste inchangé et sert seulement à un test de traversée des surfaces candidates.

Collection `WEWA_ENGINE_COVER_LEFT`, objet `LH magneto cover hollow casting - editable candidate`, parent `Engine LH cover provisional datum`. Local u = arrière +Y, v = haut +Z, w = extérieur gauche +X ; datum cockpit `(0.105, 0.154, -0.624)` m. Export `engine-cover-left-v2-inspection.glb`, source `engine-cover-left-v2.blend`.

Les références R03/R04/R05 restent partielles et non calibrées. Contour supérieur caché, trois secteurs décoratifs voisins, dos exact, vis, bouchons, nombre intégral de fixations et compatibilité RDC restent inconnus ou séparés. Toutes les dimensions de la pièce et la matière PBR argent sont estimées, sans pixels photographiques. Aucune réception artistique, cote OEM, interface physique ni qualification iPhone n’est acquise.

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-cover-left/build_v2.py
node assets-src/moto-components/engine-cover-left/check_export_v2.mjs
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-cover-left/verify_fixations_v2.py
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-cover-left/render_v2.py -- --view outer-forward-boss
```
