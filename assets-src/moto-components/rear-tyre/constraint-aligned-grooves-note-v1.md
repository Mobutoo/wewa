# Rainures sur une surface courbe : procédure réutilisable

Une grille uniforme peut produire un volume fermé et des tangentes valides tout en donnant des lèvres dentelées. Sur ce pneu, le macro en gris a refusé la première grille puis révélé les petites limites du premier patch contraint. Les contrôles numériques et les petites vues globales ne suffisaient pas.

Définir d’abord un domaine en mètres et une section fermée. Séparer les paramètres observés, les dimensions nominales et les estimations ; un nominal de pneu ne cote ni sa largeur réelle ni son moule. Définir les sillons comme une forme géométrique, puis échantillonner leurs lèvres, fonds et terminaisons pour contraindre la triangulation. Pour une répétition, imposer exactement les mêmes points sur les deux frontières périodiques et raccorder ces points aux autres surfaces natives.

Contrôler l’approximation du champ aux barycentres et aux milieux d’arête. Ajouter les points là où la forme est mal approximée plutôt que densifier toutes les surfaces. Ici, un objectif de50µm correspond à la moitié d’un pixel du macro120mm/1200px ; ce n’est ni une norme constructeur, ni une borne globale. Le résultat garde quelques maxima≈196µm malgré p99≈45,6µm. Une subdivision explicite des segments n’a pas supprimé ces rares maxima : cette réserve reste consignée, sans déclarer une correction non démontrée.

Les normales d’auteur doivent suivre la surface choisie. Les clés de raccord incluent toutes les coordonnées utiles : une clé X/angle seule confondrait intérieur et extérieur d’un pneu. Vérifier le volume des vrais triangles, les composants connexes, les ouvertures, les UV et les cadres tangentiels dans les buffers exportés. Ne pas réparer les buffers pour cacher un défaut source.

Lire réellement le gris natif puis la réflexion rasante, rattachés à leurs SHA. Archiver les versions refusées. Passer à la matière seulement lorsque cette lecture ne retrouve plus le défaut critique visé. Le microrelief de caoutchouc reste distinct des sillons millimétriques et ne sert pas à les masquer.

Conserver un master G3 public exact avant le matériau. Comparer ensuite les vrais attributs/indices et les images embarquées, puis relire les vues finales. Garder les mises à jour d’état hors des documents de provenance déjà hachés, ou fournir leur snapshot de phase exact. LOD, coût sur iPhone, montage et réception utilisateur restent des étapes distinctes.
