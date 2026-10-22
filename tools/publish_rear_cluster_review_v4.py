"""Save a six-parent inspection assembly without registering a new physical component."""
import json,hashlib,subprocess as sp,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];rev='rear-cluster-review-v4';O=R/'creative/reviews'/rev;H=R/'assets-src/moto-components'/rev;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=json.loads((H/'parameters-v1.json').read_text());proof=json.loads((O/'assembly-source-check.json').read_text());rows=[];parent_proofs=[]
for part,row in zip(P['parts'],proof['components']):
 assert sha(R/part['source'])==part['source_sha256'];p=R/'creative/reviews'/part['key']/'source-geometry-check.json';d=json.loads(p.read_text());assert d['geometry_digest']==row['source_mesh_P_I_UV_digest'];parent_proofs.append(str(p.relative_to(R)));rows.append({'component_id':part['component_id'],'parent_proof':str(p.relative_to(R)),'unchanged_P_I_UV_digest':row['source_mesh_P_I_UV_digest'],'source_sha256':part['source_sha256']})
(O/'source-parts-parity.json').write_text(json.dumps({'parts':rows,'scope':'Six unchanged source mesh P/I/UV digests under rigid display transforms, not installed fit.'},indent=2)+'\n');native=json.loads((O/'render-report.json').read_text());assert len(native['views'])==3 and all(v['samples']==96 for v in native['views']);assert json.loads((O/'inspection-v3/engine-check.json').read_text())['inputs_unchanged_during_capture'];assert len(json.loads((O/'raw-render-check.json').read_text())['files'])==7
(O/'coordinator-review.json').write_text(json.dumps({'actually_read':True,'reviewed_at':'2026-10-22','native_views_read':['whole-rear.png','whole-quarter.png','neutral-rear.png'],'engine_views_read':['inspection-v3/engine-quarter.png'],'summary':'Six sources corrigées conservées, plaque originale WEWA lisible. Deux jeux de présentation bornés retirent les interférences de v3 ; les axes des trous sont nominalement alignés avec3mm de jeu opposé estimé. Attaches, soudures, optique réelle et montage sur moto restent ouverts.','art_accepted':False,'package_complete':False,'review_only_assembly':True},ensure_ascii=False,indent=2)+'\n')
(O/'README.md').write_text('''# Montage arrière v4 — revue de six sources corrigées

![Trois-quarts studio](whole-quarter.png)
![Ciel neutre](neutral-rear.png)
![Export Babylon réel](inspection-v3/engine-quarter.png)

Tôle supérieure v4, arceau3D v3, traverse formée v2, corps/lentille v2 et plaque fictive WEWA v2. Les six géométries sources sont conservées sans déformation. Cette revue ne crée aucune nouvelle pièce physique et ne reçoit pas le montage.

Le [diagnostic v3](../rear-cluster-review-v3/README.md) conserve la première pose avec interférences. Ici le feu est décalé de14mm et la plaque de3mm pour inspection. Les [jeux d’enveloppes](display-clearances-v1.json) sont respectivement2,712mm et1,606mm ; ce sont des espacements d’affichage, pas des entretoises ni des cotes relevées. Les [axes des trous de plaque/traverse](nominal-hole-axes-v1.json) sont alignés nominalement, avec3mm entre leurs faces opposées sous ces déplacements estimés.

Les vis, écrous captifs, silentblocs, colliers, gaine, soudures et ancrages au cadre ne sont pas montés. Leurs études isolées ne sont pas implicitement reçues ou répétées. Contact lentille/corps et attache haute de l’arceau restent à qualifier ; la liaison basse n’est pas certifiée. Les reliefs optiques et la photométrie ne sont pas reçus.

[Sources et paramètres](../../../assets-src/moto-components/rear-cluster-review-v4/README.md) · [Gris relus](gray-review.json) · [Aperçus relus](preview-review.json) · [Rendus96](render-report.json) · [EXR FLOAT32](raw-render-check.json) · [Six sources inchangées](source-parts-parity.json) · [Parité GLB réelle](world-export-parity.json) · [Quatre vues moteur](inspection-v3/engine-check.json) · [Revue](coordinator-review.json).

Exposition0, gamma1, AgX Medium High Contrast et ciel artistique0,65. Aucun étalonnage, certificat de montage, réception artistique ni qualification iPhone.
''');(H/'README.md').write_text('# Source de revue arrière v4\n\n[Blender](rear-cluster-review-v4.blend) · [GLB](rear-cluster-review-v4.glb) · [Paramètres et jeux estimés](parameters-v1.json) · [Images et limites](../../../creative/reviews/rear-cluster-review-v4/README.md). Six sources inchangées, pose séparée pour inspection ; aucune nouvelle pièce physique ni pose reçue.\n')
p=R/'creative/workflow/motorcycle-exterior-completion-v1.json';d=json.loads(p.read_text())
for t in d['tasks']:
 if t['id']in ['P05','P07','P08','P11']:
  t.setdefault('assembly_reviews',[])
  if 'creative/reviews/'+rev+'/README.md'not in t['assembly_reviews']:t['assembly_reviews'].append('creative/reviews/'+rev+'/README.md')
  t['package_complete']=False
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');p=R/'LIVRAISONS_MOTO.md';s=p.read_text();s+='\n- **P05/P07/P08/P11 — revue arrière v4** : [six sources corrigées, rendus96 et export](creative/reviews/rear-cluster-review-v4/README.md). Jeux d’affichage explicites après le diagnostic v3 ; montage réel, fixations et soudures ouverts.\n';p.write_text(s)
p=R/'WEWA_Developpement_Web/validation/STATUS.json';d=json.loads(p.read_text());d['art_recovery']['latest_assembly_review']={'revision':rev,'review':'../../creative/reviews/'+rev+'/README.md','physical_component_registered':False,'whole_groups_complete':0,'art_accepted':False,'scope':'Unchanged six-parent separated inspection pose; no mounted fit or hardware acceptance.'};p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
paths={str(p.relative_to(R))for folder in[O,H,R/'creative/research'/rev]for p in folder.rglob('*')if p.is_file()};paths.update(parent_proofs);paths.update(['tools/build_rear_cluster_review_v4.py','tools/check_rear_cluster_export_v4.mjs','tools/check_wewa_plate_carrier_holes_v2.mjs','tools/check_side_cover_left_raw_p01.py','tools/capture_motorcycle18_v3.py','tools/motorcycle-lab/review-v2.js','tools/publish_rear_cluster_review_v4.py','app/public/materials/kloppenheim_06_puresky_1k.hdr'])
for part in P['parts']:paths.add(part['source']);paths.update(part['export_files'])
m=O/'production-manifest.json';assert not m.exists();rows=[{'path':p,'bytes':(R/p).stat().st_size,'sha256':sha(R/p)}for p in sorted(paths)];m.write_text(json.dumps({'scope':'Review-only six-parent native/GLB/runtime delivery; no physical component registration, mounted fit or artistic acceptance.','files':rows,'art_accepted':False,'package_complete':False},indent=2)+'\n');stage=sorted(paths|{str(m.relative_to(R)),'LIVRAISONS_MOTO.md','tools/motorcycle-lab/catalog.json','creative/workflow/motorcycle-exterior-completion-v1.json','WEWA_Developpement_Web/validation/STATUS.json'});assert not sp.check_output(['git','diff','--cached','--name-only'],cwd=R).strip();sp.run(['git','add','--sparse','--',*stage],cwd=R,check=True)
for row in rows:
 b=sp.check_output(['git','show',':'+row['path']],cwd=R);assert len(b)==row['bytes']and hashlib.sha256(b).hexdigest()==row['sha256']and len(b)<100*1024**2
for p in stage:
 if p.endswith('.json'):json.loads(sp.check_output(['git','show',':'+p],cwd=R))
sp.run(['git','diff','--cached','--check'],cwd=R,check=True);sp.run(['git','commit','-m','Deliver six-parent rear inspection v4 with explicit display gaps and native review'],cwd=R,check=True,stdout=sp.DEVNULL);sp.run(['git','-c','pack.window=0','push','origin','HEAD:main'],cwd=R,check=True,env=os.environ|{'GIT_NO_LAZY_FETCH':'1','GIT_TERMINAL_PROMPT':'0'})
