# Came de frein avant — recherche de variante

La came transforme la rotation commandée par le levier en écartement des mâchoires. **Elle est distincte de l’axe de roue.** Cette recherche ne fabrique aucun modèle et ne certifie aucune cote de la Boxer125HD RDC actuelle.

Une nouvelle source Bajaj révèle une contradiction utile à résoudre avant de figer l’assemblage : le [catalogue BM150, document71111461, révision00 de mars2012](https://reypiston.com/wp-content/uploads/2024/04/Boxer-BM150-SPC.pdf) distingue les ensembles pour roue à rayons et pour roue moulée.

| Catalogue et planche | Flasque | Levier | Came | Axe de roue |
|---|---|---|---|---|
| BM125UG, feuillePDF44, lignes standard | DZ151027 | DD151008 | 31151011 | DZ151012 |
| BM125UG, feuillePDF44, lignes UG5gear | JA131605 | JA131607 | 30151004 | DJ151041 |
| BM150 mars2012, feuillePDF41, pages61–62, roue à rayons | JA131605 | JA131607 | 30151011 | DJ151081 ; DJ151041 donné comme alternative |
| BM150 mars2012, feuillePDF42, pages63–64, roue moulée | DS151087 | DS151092 | DS151089 | JB131017 |

Ce tableau **ne prouve ni l’identité RDC ni une incompatibilité universelle** : modèles, dates et marchés diffèrent. Il interdit toutefois de considérer automatiquement la paire JA131605/JA131607 comme le frein exact de la jante moulée du jeu. Le schéma du catalogue BM125UG et ses lignes combinées standard/UG ne suffisent pas à lever cette ambiguïté. Les candidats flasque et levier restent des études de pièces voisines, sans réception de leur raccord à la roue.

La planche BM150 à rayons publie aussi un roulement `12×37×12`, un écrou `M12` et une vis de levier `M6×30`. Ces faits concernent cet ensemble lié uniquement. Ils ne permettent pas de remplacer silencieusement les alésages estimés des modèles actuels, ni de déduire toutes les dimensions de l’axe ou de la came.

Le [kit générique Sparesgen](https://sparesgen.com/product/bajaj-boxer-front-brake-cam-kit-standard/) fournit une vue oblique de came et levier, sans référence de came lisible ni dimension. **Sa photo est identique octet pour octet à celle déjà consultée chez IndianBikesSpares** : elle n’apporte pas une deuxième direction de vue. On distingue un arbre à épaulements, une zone supérieure cannelée et une partie de pied de came ; ni le profil complet du pied, ni le nombre de dents, ni les cotes ne sont établis. La mention vendeur « hardened steel » n’est pas reprise comme métallurgie certifiée. Le poids commercial de0,5kg n’est pas une mesure fiable de la came seule.

Les originaux PDF, pages rendues, HTML et photographie sont conservés hors dépôt public dans `/workspace/wewa-assets/references/front-brake-cam/`. [research.json](research.json) conserve URLs, empreintes, localisations, affirmations et incertitudes. [source-archives.json](source-archives.json) décrit les archives privées. Aucun pixel vendeur/constructeur n’est appliqué comme texture. Les deux pages rendues du catalogue BM150 ont été inspectées ; les extractions texte ne sont pas utilisées seules pour interpréter les illustrations. Les pages WheelingCycleSupply et TradeIndia ont répondu403 et ne sont pas comptées comme lues.

Le passage suivant consiste à identifier le jeu de pièces actuel, puis à obtenir les deux profils, les deux bouts d’arbre et une vue axiale du pied avec une échelle mesurée. La longueur totale, les diamètres/longueurs de portées, les épaulements, le profil et le nombre des cannelures, les gorges, la section du pied et le repère angulaire restent inconnus. Le workflow détaillé G0–G8 est conservé dans le JSON : source paramétrique isolée, matière, engagement du levier et contact des deux mâchoires, export réel, optimisation puis réception. Une animation d’arbre libre ne constituerait pas un contrôle fonctionnel du frein.

Pour les travaux indépendants sur le cockpit, ce même catalogue contient le guidon en feuillesPDF46–47 (imprimées71–74) et le compteur en feuillePDF53 (imprimées85–86). Ces localisations ont été transmises aux responsables des deux pièces ; elles restent des références BM150 de2012, sans équivalence RDC déclarée.
