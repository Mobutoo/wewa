# LEGACY15-REAR-REFLECTOR — 30201069 visiblev1

Un seul candidat Boyle : face rouge, lèvre, cadre sombre et chants observables. **Dos coupé/ouvert, aucune fixation, goujonM5 ou quincaillerie, aucun prisme interne.** SourceBlender et GLB éditables, un mesh logique / deux matériaux ; aucune intégration root.

Dimensions de travail **80×50×6mm**, estimées. Intervalles de sensibilité et méthode dans [G0–G2](../../../creative/research/rear-reflector-30201069-visible-v1/G0-G2-plan-v1.json) : largeur55–125, hauteur30–70, profondeurvisible2–13mm. Ce sont des hypothèses artistiques volontairement larges, pas des bornes mesurées ni des dimensions constructeur. RDC conditionnelle.

Repère local : XY=plan de face, +Z=extérieur visible ; origine au centre de la coupe arrièreZ0, **pas un ancrage de montage**. FrontièreZ0 volontaire ouverte, non épaisseur de paroi mesurée ; pas de backplate. Géométrie1300triangles,701positions soudées, une boucle ouverte. Les matériaux sont originaux : rouge et cadre, normale512² de cellules apparentes générée mathématiquement, sans aucun pixel source. Pas de simulation ou certification rétro-réfléchissante.

[Revue et images](../../../creative/reviews/rear-reflector-30201069-visible-v1/README.md). Gris lus avant matériau, aperçu studio/neutre lu avant native96, trois rendus96 à900×700, huit EXRFLOAT32, source rouvert, source/GLB et Babylon vérifiés. GlTF0erreur/0avertissement après export des tangentes. Les normales subissent l’arrondi de l’exporteur, delta composante maximal5,73e-5 ; positions identiques et UVdelta2,98e-8.

**G4 à reprendre** : motif trop régulier et réponse sous éclairage différents du véritable objet. L’enveloppe est candidate, pas une réception de fidélité. G5/fit bloqués, G8pending, aucune mesureiPhone. Le README source ne vaut pas autorisation de réplication/pose.

`pipeline_boyle_v1.py` : étapesgeometry,gray,graycut,material,preview,reexport,final ; `presentation_reopen_boyle_v1.py` sauvegarde caméra et96samples puis rouvre sans changer le mesh ; `check_parity_boyle_v1.mjs` compare trianglesévalués/normales/UV à l’export ; `capture_boyle_v1.py` capture le fragment isolé. Aucun helperfrozen modifié ; instantanés exacts en revue/protocols. `freeze_boyle_v1.py` est le producteur du gel, pas une commande à relancer sur cette révision.
