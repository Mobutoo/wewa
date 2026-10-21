# Contrôle matière sous éclairages communs — v1

Ce contrôle complète la revue de chaque pièce du style photographique choisi. Il ne remplace pas les photos attribuées, les vues de forme ou l’examen dans le moteur du jeu.

1. Geler une source, son export et leurs empreintes. Ne jamais retoucher le matériau dans le fichier servant de témoin.
2. Écrire un protocole JSON séparé : collection, caméra explicite, HDR et empreinte, résolution, échantillons, nouveau dossier de sortie. Choisir une vue lisible puis vérifier les sommets réellement évalués avec le contrôle de cadrage.
3. Exécuter [le rendu en lecture seule](../../tools/render_motorcycle_material_lighting_review.py). Même pièce, même caméra, mêmes matériaux : HDR extérieur commun puis même HDR avec soleil chaud. Le fond de caméra gris n’éclaire pas la pièce ; les reflets et les autres rayons conservent l’environnement.
4. Ouvrir réellement les deux images. Examiner valeurs claires/sombres, teinte, comportement du métal ou du caoutchouc, largeur des reflets, lèvres et microrelief. Une pièce métallique peut prendre la couleur du ciel : ne pas modifier arbitrairement son albédo pour obtenir un gris constant.
5. Comparer avec les références dont l’éclairage est connu. Sans photographie comparable, carte/exposition mesurée ou matériau identifié, conserver la réserve ; une différence avec une softbox n’est pas une erreur matérielle démontrée.
6. Si une correction est justifiée, créer une nouvelle révision source et répéter les mêmes protocoles. Conserver le témoin précédent. Recontrôler les vrais buffers et l’apparence dans Babylon ; ce rendu Cycles ne prouve pas la parité des shaders mobiles.
7. Publier les PNG réellement produits, le protocole, le rapport, les empreintes et la lecture. Les aperçus sous 96 échantillons restent marqués comme tels. Une série techniquement complète ne donne aucune réception artistique automatique.

Premier essai : [fourreau gauche, deux images et limites](../reviews/fork-outer-left-material-lighting-v1/README.md). La lumière n’est pas radiométriquement calibrée, le soleil chaud est un scénario de comparaison choisi, et la vue orthographique reste une inspection de pièce isolée. Aucune scène urbaine ou performance iPhone n’est qualifiée par ce contrôle.
