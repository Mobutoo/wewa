from pathlib import Path
import json,hashlib,shutil
from PIL import Image
R=Path('/workspace/wewa');D=Path(__file__).resolve().parent;P=Path('/workspace/wewa-assets/references/passenger-left-world-context-audit-v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj):(D/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
old=R/'creative/reviews/passenger-footrest-left-exterior-context-v1/delivery-frozen.json';delivery=json.loads(old.read_text());bad=[]
for row in delivery['files']:
 p=R/row['path']
 if not p.exists() or sha(p)!=row['sha256']:bad.append(row['path'])
assert not bad,bad
save('frozen-source-integrity.json',{'previous_delivery':str(old.relative_to(R)),'delivery_sha256':sha(old),'files_verified':len(delivery['files']),'mismatches':bad,'method':'One SHA256 verification pass, read-only','sources':[row for row in delivery['files'] if row['path'].endswith(('.blend','parameters.json'))]})
shutil.copyfile(R/'creative/research/passenger-footrest-left-exterior-context-v1/native-links-and-transforms.json',D/'source-rigid-links-snapshot.json')
a=json.loads((D/'numeric-audit.json').read_text())
photos=[]
for p,role in [(Path('/workspace/wewa-assets/references/exterior-completion-current/04.png'),'official current RDC LH profile, actually read'),(P/'04-region.png','private crop actually read, box570,300,825,520, scaled4x'),(P/'04-projection.png','private diagnostic overlay actually read; uncalibrated, no depth occlusion'),(Path('/workspace/wewa-assets/references/powertrain-continuation-p16-v39/PF113002_3-scaled.jpg'),'bare PF113002 clevis/eye macro actually read, independent market specimen')]:
 photos.append({'private_path':str(p),'sha256':sha(p),'pixels':list(Image.open(p).size),'role':role})
photos[0]['url']='https://www.bajajauto.com/fr-cd/-/media/globalbajajauto/common-media/360/boxer/boxer-125-hd-new/red-long-visor/04.png';photos[3]['url']='https://bajajstoremexico.com/wp-content/uploads/2025/02/PF113002_3-scaled.jpg'
save('source-and-visual-read.json',{'photos':photos,'no_private_photo_pixels_in_repository':True,'source_facing_read':{'path':'creative/reviews/passenger-footrest-left-exterior-context-v1/final-source-facing.png','sha256':sha(R/'creative/reviews/passenger-footrest-left-exterior-context-v1/final-source-facing.png')},'manual_current_photo_observations':[{'region_pixel':[645,415,685,455],'interpretation':'Candidate diagonal passenger rubber/peg ahead of lower shock; exact hinge pixel/depth not established, not a confirmed landmark pair'},{'region_pixel':[620,340,665,455],'interpretation':'Visible dark support descending rearward from under side cover; not positively identified as either PF113002 arm'},{'region_pixel':[735,315,795,445],'interpretation':'Separate rearward tubular support visible; cannot assign short-arm identity or attachment'}],'projection_read':{'hinge_pixel':a['landmarks']['peg_hinge']['pixel_estimate'],'long_terminal_pixel':a['landmarks']['long_actual_aperture_centre']['pixel_estimate'],'short_terminal_pixel':a['landmarks']['short_actual_aperture_centre']['pixel_estimate'],'flags':['Projected hinge falls in plausible passenger-step region, not a measured agreement','Projected long arm runs upward/rearward across shock region; visible current-photo tube routing is not positively matched','Projected short terminal near740,425 lies in weakly supported/open wheel region; no current-image aperture/bolt correspondence','Outward X maps correctly but X-depth is absent from coarse projection; actual diagonal rubber appearance cannot be tested with this profile approximation','Product macro confirms clevis/eye feature distinction, not installed current-RDC variant identity']},'verdict':'Numerical transform accepted. Current installed routing remains G2 unqualified; reject interpreting this nominal pose as a validated motorcycle mounting. Neither a confirmed different variant nor a confirmed wrong-peg identification is established by this one image.'})
# Public schematic contains original geometric data only; no photo pixels.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="650" viewBox="560 280 300 270">','<rect x="560" y="280" width="300" height="270" fill="white"/>','<text x="565" y="292" font-size="7">Uncalibrated profile diagnostic — no photograph / no fit</text>']
for k,cs in a['curves_pixel'].items():svg.append('<polyline fill="none" stroke="#008899" stroke-width="1.5" points="'+' '.join(f'{x:.2f},{y:.2f}'for x,y in cs)+'"/>')
for k,v in a['landmarks'].items():
 if 'bezier'in k or 'clevis'in k:continue
 x,y=v['pixel_estimate'];svg.extend([f'<circle cx="{x}" cy="{y}" r="2" fill="#ab0070"/>',f'<text x="{x+3}" y="{y+8}" font-size="5">{k}</text>'])
svg.append('</svg>');(D/'coarse-projection.svg').write_text('\n'.join(svg)+'\n')
(D/'README.md').write_text('''# Revue numérique LH — pose contextuelle proposée

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
''')
files=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(D.iterdir()) if p.is_file() and p.name!='delivery-frozen.json']
save('delivery-frozen.json',{'schema':1,'kind':'read_only_numeric_and_private_macro_pose_audit','authorization':'Coordinator dispatch within user-authorized autonomous motorcycle completion','files':files,'file_count':len(files),'new_physical_ids':0,'geometry_or_historical_sources_modified':False,'numeric_matrix_valid':True,'current_RDC_mount_validated':False,'fit_qualified':False,'g8':False,'mutable_external_ledgers_excluded':True})
print('FREEZE',len(files),sha(D/'delivery-frozen.json'))
