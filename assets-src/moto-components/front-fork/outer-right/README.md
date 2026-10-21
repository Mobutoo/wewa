# Fourreau droit — candidat apparenté PF121019

Une seule jambe isolée, sans joints, bagues, huile, ressort interne ou boulons. Source éditable et génération originales ; l’algorithme continu du fourreau gauche est réutilisé, puis les volumes RH sont reconstruits. Aucun miroir d’un GLB et aucune photo utilisée comme texture. La poche rectangulaire LH n’est pas copiée. L’inscription de fonderie n’est pas inventée.

Les photos Matriz PF121019 et Endurance550BF17707 sont privées ; leur attribution Boxer150 ne certifie pas le125HD RDC. Le col élargi, corps fuselé, pied arrondi, œil d’axe et deux oreilles sont observables. La face opposée et les interfaces restent incomplètes.

## Cotes et repère

Mètres, +Z axe du tube, origine centre de l’œil d’axe ; −X extérieur droit, +X vers la roue, +Y pilote. Aucun placement installé n’est validé. Longueur343mm(plage310–390), col48mm(44–52), corps41→37,5mm(35–43), passage d’axe12,4mm(12,2–14,5), oreilles Y±27/Z218mm sont **toutes estimées**. L’enveloppe principale reprend le choix provisoire du côté gauche, sans prétendre démontrer la symétrie physique. Les lectures de rapports d’image non calibrée ne sont pas des cotes fabricant.

Le col48mm et l’ouverture40,6mm du soufflet figé sont incompatibles à ce stade : aucun emboîtement n’est certifié. Cavité et fond internes ne décrivent pas le mécanisme hydraulique ni sa course.

## Construction et contrôle

`build.py` construit une section continue talon/corps/col/paroi/cavité, puis unionne œil d’axe et oreilles et enlève les trois passages. Les opérations CSG utilisent notre helper de flasque, lu sans modification. `beautify_fill AREA` reprend uniquement les diagonales coplanaires ; positions, volume et frontières sont conservés, sans réparation des buffers. Les normales sont fraîches, avec plans plats et sections courbes interpolées. Le contrôle lit également fermeture/connectivité, aires réelles, UV et repères tangents des buffers exportés. Le gris et un reflet natif précèdent les cartes.

`material.py` crée un grain original, semence121019, période10mm en projection dominante, RMS≈2µm et rugosité≈.30–.44 estimés ; aucune composition chimique ni réflectance mesurée. Les alésages et le siège intérieur restent plus lisses. Les attributs POSITION/NORMAL/UV/TANGENT et matrices doivent rester identiques entre G3 et G4, indépendamment des groupes matière.

`render.py` enregistre des checkpoints par vue96samples/OIDN, source/export/caméra/config/PNG hachés ; les vues incomplètes ne sont pas des preuves. Les contrôles Babylon et la réception utilisateur restent séparés, pilotés par le registre central. Ce candidat ne constitue ni une fourche complète, ni un composant reçu, ni une optimisation mobile.

Références attribuées : [Matriz — fourreau droit PF121019](https://bajajmatriz.com/producto/base-soporte-barra-suspension-derecha-moto-boxer-150-bajaj), [catalogue fournisseur Endurance](https://airavatautospares.in/pdf/endurance.pdf), feuille3 ligne32PF121019↔550BF17707. Images consultées en privé ; variante apparentée, pas cote ni identité RDC certifiée.
