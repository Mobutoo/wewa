# Écrou Nyloc — revue v1

Les vues quarter, underside-thread et crown-material sont des rendus Blender4.3.2 CyclesCPU96avec OpenImageDenoise. Les deux premières montrent l’unité entière ; la dernière recadre volontairement le bas pour montrer couronne, insert et filet. Le préflight caméra joint à chaque checkpoint teste les vrais sommets évalués, les limites de profondeur et la marge d’image.

Les deux aperçus gris ont été lus avant matière. Les méplats utilisent des normales planes explicites, les coins/couronne/filet restent lisses. Un reflet étroit à une jonction de deux plans correspond au coin arrondi ; ce constat ne prouve pas une dégradation d’un méplat. Les trois aperçus matière ont ensuite été lus. Les reflets brillants dans le filet à24échantillons sont à relire dans les images finales.

La photo et le dessin Westfield définissent une famille génériqueDIN985, sans constituer une photo de l’écrou39042215. Les dimensions globales proviennent de son tableauM10 ; les profils fins, jeux, matière et couleur restent estimés. Les photographies commerciales et PDF restent privés, aucune texture n’en provient. D04/D15 établissent seulement le NylocM10 de variantes liées.

Le rapport geometry-check.json porte sur les vrais triangles, volumes, ouvertures et tangentes de l’export. geometry-preservation-check.json compare les positions, normales, matrices et triangles orientés avant/après matière, indépendamment de leur regroupement en trois matières. material-buffer-check.json relit les quatre images réellement embarquées, leurs pixels et canaux. Ces contrôles ne valident ni une norme, ni le serrage du guidon, ni la réception artistique utilisateur.
