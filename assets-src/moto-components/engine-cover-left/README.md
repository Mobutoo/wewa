# Carter magnéto gauche — candidat isolé v1

`MOTO-ENGINE-COVER-LEFT-001` : carter gauche seul, avec son grand bossage avant et un périmètre supérieur asymétrique. Ce n’est pas le miroir du carter droit. Cache arrière de transmission, bouchons, vis, décalque et mécanismes internes restent séparés.

Les vues officiellesR03/R04/R05 montrent surtout le grand bossage arrondi, avec quelques fixations et une limite supérieure partiellement cachée. Les recherches des codes36PF0007 et52PF1735 n’ont pas trouvé de photo nue de la variante actuelle ; des résultats Pulsar/Dominar ont été rejetés. Le catalogue BM125 voisin montre trois secteurs courbes de relief, mais la petite photo RDC ne permet pas de certifier leur présence ni leur profondeur : ces secteurs ne sont pas recopiés. La peau actuelle est donc un candidat de volume et de silhouette, avec ce détail de face encore à résoudre.

Contour et repère proviennent d’annotations non calibrées deR04. Environ162×191×43mm et paroi3mm sont des choix de travail estimés ; aucune dimension physique de cette pièce n’est mesurée. Trois fixations candidates ne constituent pas un décompte complet. Le dos n’est qu’une coque creuse estimée, sans nervures ou interface de stator inventées.

La source construit des sections continues fermées avec un helper réutilisable de loft. Aucun congé global ne vient casser la coque mince. Le nettoyage ne déplace aucun sommet retenu et ne modifie ni surface ni volume. Les normales personnalisées héritées sont explicitement effacées ; courbes lissées et vraies arêtes des ouvertures conservées. Source et GLB ont une seule coque positive fermée et connexe, sans triangle nul ni erreur glTF.

Collection `WEWA_ENGINE_COVER_LEFT`, objet `LH magneto cover hollow casting - editable candidate`, parent `Engine LH cover provisional datum`. Axes locaux u=arrière+Y, v=haut+Z, w=extérieur gauche+X, base de déterminant+1. Le repère cockpit est inchangé. Le PBR argent peint est une hypothèse originale, sans texture photographique. Export détaillé d’inspection, sans LOD ou budget de scène mobile qualifié.

```sh
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-cover-left/build.py
node assets-src/moto-components/engine-cover-left/check_export.mjs
/workspace/wewa-tools/blender-4.3.2-linux-x64/blender --background --threads 1 --python-exit-code 1 --python assets-src/moto-components/engine-cover-left/render.py
python assets-src/moto-components/engine-cover-left/record_body_review.py engine-cover-left
```

Voir [paramètres](parameters.json), [recherche et inconnues](../../../creative/research/engine-cover-left/reference-observations.json) et [revue](../../../creative/reviews/engine-cover-left-v1/README.md). Aucune variante exacte, interface mécanique, fidélité de face, matière, réception artistique ou qualification iPhone physique n’est acquise.
