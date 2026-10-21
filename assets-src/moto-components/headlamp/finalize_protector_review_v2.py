"""Metadata closure only after actual reading; no rendering or source changes."""
from pathlib import Path
import json,hashlib,struct
H=Path(__file__).resolve().parent;R=H.parents[2];P=R/'creative/reviews/headlamp-front-protector-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();save=lambda p,d:p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n');a=json.loads((P/'source-geometry-check.json').read_text());c=json.loads((P/'render-checkpoints.json').read_text());reading=json.loads((P/'visual-reading.json').read_text());frozen=json.loads((P/'source-freeze-manifest.json').read_text());assert sha(H/'headlamp-front-protector-v2.blend')==a['source_sha256']==c['source_sha256']==reading['source_sha256'];assert sha(H/'headlamp-front-protector-v2.glb')==a['export_sha256']==c['export_sha256']==reading['export_sha256']
for x in frozen['files']:assert sha(R/x['path'])==x['sha256'],x['path']
def channels(path):
 with path.open('rb')as f:
  assert struct.unpack('<I',f.read(4))[0]==20000630;f.read(4)
  def zs():
   a=bytearray()
   while True:
    b=f.read(1)
    if not b or b==b'\0':return a.decode('utf8','replace')
    a.extend(b)
  while True:
   n=zs()
   if not n:return[]
   typ=zs();size=struct.unpack('<I',f.read(4))[0];v=f.read(size)
   if typ=='chlist':
    out=[];k=0
    while k<len(v)and v[k]:
     end=v.index(0,k);out.append(v[k:end].decode());k=end+17
    return out
names=['whole-front','whole-quarter','whole-back','rod-band-junction'];assert set(c['views'])==set(names);rows=[]
for n in names:
 v=c['views'][n];png=R/v['PNG_path'];exr=Path(v['EXR_private_path']);r=reading['views'][n];assert v['actually_saved']and r['read']and sha(png)==v['PNG_sha256']==r['PNG_sha256']and sha(exr)==v['EXR_sha256']and v['config']['samples']==96
 rows.append({'name':n,'camera':v['config']['camera'],'PNG_path':v['PNG_path'],'PNG_sha256':v['PNG_sha256'],'EXR_private_path':str(exr),'EXR_sha256':v['EXR_sha256'],'EXR_actual_channels':channels(exr),'config_sha256':v['config_sha256'],'actually_saved':True,'actually_read':True,'observations':r['observations']})
save(P/'render-report.json',{'schema':1,'revision':'headlamp-front-protector-v2','source_sha256':a['source_sha256'],'export_sha256':a['export_sha256'],'renderer':'Blender4.3.2 Cycles96/OpenImageDenoise CPU','samples':96,'resolution_px':[1100,1020],'source_and_export_unchanged':True,'views':rows,'limits':reading['limits'],'art_accepted':False,'physical_iphone_tested':False})
(P/'README.md').write_text('''# Protection avant v2 — quatre vues réelles\n\nFace entière, troisquarts, dos et jonction d’arceau ont été sauvés en Cycles96/OIDN CPU et réellement ouverts. Les PNG et EXR multilayer privés sont reliés par checkpoints au protocole et aux empreintes exactes de source/export. Le corps, les normales et UV de l’étude grise v3 sont conservés ; le revêtement propre neutre est estimé.\n\nLa pièce couvre les trois surfaces visibles de protection : entourage, arceau supérieur et inférieur. Le code actuelRDC, la démontabilité, les attaches arrière et les jeux avec l’optique/cowl restent inconnus. Aucun godet, réflecteur, verre, ampoule, carénage rouge ou clignotant n’est compris dans ce candidat. Le lot12 est incomplet.\n\nLa construction et les matériaux sont originaux, sans photographie ni mesh commercial comme texture/asset. Les photos liées DY401002 montrent la structure mais ne certifient pas la compatibilitéRDC. Contrôle moteur, assemblage complet et Safari physique sont distincts ; aucune réception artistique implicite.\n''')
files=[R/x['path']for x in frozen['files']]+[P/'source-freeze-manifest.json',Path(__file__),P/'render-checkpoints.json',P/'visual-reading.json',P/'render-report.json',P/'README.md']+[P/(n+'.png')for n in names];save(P/'freeze-manifest.json',{'schema':1,'revision':'headlamp-front-protector-v2','source_sha256':a['source_sha256'],'export_sha256':a['export_sha256'],'state':'Four real96 views actually saved/read; protection candidate only, exactidentity/mount/runtime/artistic acceptance open.','files':[{'path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size}for p in sorted(set(files))],'private_EXR_checkpoints':[{k:v[k]for k in ['name','EXR_private_path','EXR_sha256']}for v in rows],'art_accepted':False});print('CLOSED',a['source_sha256'],a['export_sha256'])
