# Source20 — Court départ supérieur de gaine d’embrayage

Base métadonnées44 `b06fa75b73b70eedee92edacf4b4617650e47ea0`. Aucune coupe ni sélection Source20 fixée. [Rapport](report.json), [fermeture](source-closure-v1.json), [entrées utiles](stable-recipe-inputs-v1.json) : **46 paires SHA/octets vérifiées**, **32 entrées stables**. Finales en cours à la mission : aucun render-report, checkpoint final ou gel final pinné.

## construction

build.py vérifie et charge clutch-control-v2.blend (586b41d0…) et son build-report-v2, instruments-v3.blend (2ac37623…) et son rapport structurel exact. Les quatre sont dans46 ; ne pas les remplacer par les révisions courantes. Objets link=False, capture de positions/triangles monde puis reset et création de guides gris propres numériques. La source finale n’a pas de Library ni image externe selon le contrôle fourni.

## geometry

Un court balayage annulaire original suit la courbe Bézier de travail, diamètre extérieur estimé5mm, lumière3mm, épaisseur1mm et coupe distale de revue. Écart de travail0,2mm au réglage ; ni ferrule/soufflet, câble interne, vraie extrémité ni continuation cachée fabriqués. UV cylindrique propre et section de bouche distincte ;49536triangles d’inspection, aucun LOD/iPhone qualifié. Aucun appel CSG/Manifold dans cette chaîne.

## material restart

material.py exige le rapport/maître G3 fourni et geometry-preview-review ready_for_representative_material, tous46. Shader noir uniforme linéaire(.012,.014,.016), métal0, rugosité.43, aucune texture ou police. Signature source puis vrais buffers natifs P/N/UV/indices/matrices protégés dans les preuves fournies ; aucun contrôle rejoué.

## render and checkpoints

render.py exige le build-report, le source et export-check, puis ses deux helpers locaux. Rendu studio autonome avec guides intégrés de contrôle visibles seulement dans la vue de contexte. Aucun HDR, mire ou checkpoint privé initial obligatoire. Les checkpoints sont lus uniquement si présents pour sauter des sorties déjà égales, sinon de nouveaux PNG/EXR sont produits. Aucune copie privée utile à la reprise des rendus.

## conditional checks

check_interface recharge le rapport embrayage exact pour le pivot et les snapshots retenus dans le source, réactive guides en mémoire. Cinq poses0/3/6/9/12° : BVH natif et72 points de milieu de paroi/pose à trois rayons, témoin cube et règle de progression float32. Ces preuves ne certifient ni contact coplanaire ni containment réciproque exhaustif, ni tout cockpit, montage réel, flexion au braquage ou rayon minimum de gaine industrielle.

## historic preview boundary

record_preflight.py relit les12 checkpoints privés et leurs propres PNG/EXR référencés par geometry-preview-review et preview-review pour refaire la signature de gel. Ce sont les preuves historiques de la lecture humaine, pas des entrées de build/material/render. Le gel46 existant est vérifié ; aucune prétention de reconstituer ce finalizer historique depuis les seuls fichiers publics, ni d’aspirer ces sorties privées. Une nouvelle itération doit produire ses propres aperçus réellement lus et ses nouveaux enregistrements.

## restart guards

recipe/build/material refusent le preflight déjà présent et recipe nomme Blender4.3.2 de travail. Travailler dans une copie isolée non figée, ne jamais supprimer/modifier le gel original. La matière repart du maître G3 sans recharger les deux ancêtres. Node et les paquets du lockfile existant, Blender et NumPy fourni par Blender sont requis ; aucune installation ou reprise propre exécutée.

Aucun constructeur/checker/rendu/export ou ouverture Blender exécuté. Sources, anciens gels, audits et registres inchangés ; aucune mutation Git. Aucune photo documentaire privée ni archive entière de partenaire copiée. Lecture statique, sans replay propre ou réception mécanique/artistique. Les tables historiques des rapports ne sont pas des manifestes vivants.
