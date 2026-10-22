# Revue numérique LH — pose contextuelle proposée

Matrice correcte ; montage RDC04 non validé. Aucun fichier source, géométrie, pose gelée, catalogue ou métadonnée racine modifié. Aucun nouveau natif/GLB, aucune nouvelle pièce. Autorité : Coordinator dispatch within user-authorized autonomous motorcycle completion.

## Contrôle indépendant

Blender4.3.2 a rouvert le vrai natif lié du kit et ses trois parents ; calcul sur les vrais sommets et matrices des objets. Euler XYZ [-90,-45,-90], T=[.1505,.8147559,-.4267588]m. Forme analytique Q=[[0,0,1],[-1/√2,-1/√2,0],[1/√2,-1/√2,0]]. Déterminant+1 ; Z source→+X monde LH. Erreur numérique charnière→[.17,.65,-.60] inférieure à0.0001mm. L’œil reste un autre point : environ[.150500,.599513,-.642002]. La charnière métal est le point retenu, pas cet œil.

Les coordonnées proposées long/short sont celles des fins de courbes. Les vrais centres de perçages créés par le code historique sont décalés de1mm suivant la tangente finale. Ils donnent long[.154500,.747157,-.359160], short[.165494,.846148,-.587695]m. Le code et le JSON distinguent ces rôles. L’écart diagnostic déjà gelé de5mm entre axe de charnière métal et axe de chape reste présent : il devient transversal mondeX ; cette pose ne le ferme pas et n’établit aucun axe/pin commun.

## Lecture macro et silhouette

RDC04, crop privé et superposition privée réellement lus, ainsi que la macro PF113002 et final-source-facing gelé. Les fichiers publics ne contiennent pas les pixels privés. Deux axes de roues ont été pointés manuellement vers[204,500] et[748,489]px ; incertitude manuelle approximative±5px. L’empattement1.285m et les stationsY/Z viennent du layout mainv9 estimé, pas d’une mesure OEM. La caméra n’est pas calibrée ; la projection ignoreX et l’occlusion. Elle donne charnière[657,432], œil[636,450], long[698,329], short[740,425]px.

La charnière tombe près de la zone candidate du repose-pied devant le bas d’amortisseur, sans correspondance de centre établie. En revanche la projection du grand bras traverse la zone d’amortisseur et sa trajectoire n’est pas positivement celle du tube sombre visible depuis le dessous du cache. Le petit terminal tombe dans une zone de roue sans perçage/attache correspondant identifiable. Ce sont des réserves de routage, pas une collision3D prouvée : aucun wholebike n’a été chargé. Le sens du caoutchouc diagonal de la photo n’est pas contrôlable par une projection qui ignore la profondeur. Ni autre variante ni mauvaise identification du peg ne sont démontrées.

La proposition peut rester une hypothèse de contexte distincte ; elle ne doit pas être promue en montage reçu sur cette seule image. Aucune nouvelle pose ajustée n’est proposée pour forcer les correspondances. Les ±100mmY/±40mmZ/±25mmX et±15° sont des marges de revue du coordinateur seulement. Huit coins angulaires avec charnière fixe sont consignés ; ce ne sont ni une optimisation ni des extrema garantis ni une tolérance physique.

## Suite utile bornée

Une vue montée LH proche, légèrement arrière et sous la selle, montrant simultanément charnière, œil et les deux terminaisons permettrait d’identifier le routage et la variante. Une seconde oblique permettrait d’estimer la projection transversale du peg. Ne pas déduire un rôle de fixation cadre/amortisseur de la seule proximité. G2/fit/rôles de fixations restent ouverts, G8 inchangé.

Les81 fichiers de l’ancien gel ont été vérifiés une fois sans divergence. Le présent gel contient exclusivement ce nouveau dossier ; aucun ledger mutable externe.
