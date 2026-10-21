"""Metadata closure only after actual reading; no rendering or source changes."""
from pathlib import Path
import json,hashlib,struct
H=Path(__file__).resolve().parent;R=H.parents[3];P=R/'creative/reviews/headlamp-housing-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();save=lambda p,d:p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n');a=json.loads((P/'source-geometry-check.json').read_text());c=json.loads((P/'render-checkpoints.json').read_text());reading=json.loads((P/'visual-reading.json').read_text());frozen=json.loads((P/'source-freeze-manifest.json').read_text());assert sha(H/'headlamp-housing-v1.blend')==a['source_sha256']==c['source_sha256']==reading['source_sha256'];assert sha(H/'headlamp-housing-v1.glb')==a['export_sha256']==c['export_sha256']==reading['export_sha256']
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
names=['whole-front','whole-back','whole-profile','lower-rounded-tip'];assert set(c['views'])==set(names);rows=[]
for n in names:
 v=c['views'][n];png=R/v['PNG_path'];exr=Path(v['EXR_private_path']);r=reading['views'][n];assert v['actually_saved']and r['read']and sha(png)==v['PNG_sha256']==r['PNG_sha256']and sha(exr)==v['EXR_sha256']and v['config']['samples']==96
 rows.append({'name':n,'camera':v['config']['camera'],'PNG_path':v['PNG_path'],'PNG_sha256':v['PNG_sha256'],'EXR_private_path':str(exr),'EXR_sha256':v['EXR_sha256'],'EXR_actual_channels':channels(exr),'config_sha256':v['config_sha256'],'actually_saved':True,'actually_read':True,'observations':r['observations']})
save(P/'render-report.json',{'schema':1,'revision':'headlamp-housing-v1','source_sha256':a['source_sha256'],'export_sha256':a['export_sha256'],'renderer':'Blender4.3.2 Cycles96/OpenImageDenoise CPU','samples':96,'resolution_px':[1100,1020],'source_and_export_unchanged':True,'visual_diagnostic_reserve':'Lowerrib highlight steps; v1 preserved, separate normals-only correction pending','views':rows,'limits':reading['limits'],'art_accepted':False,'physical_iphone_tested':False})
(P/'README.md').write_text("""# Boîtier de phare v1 — quatre vues réelles

Face entière, dos, profil et pied inférieur ont été sauvés en Cycles96/OIDN CPU et réellement ouverts. Les PNG et EXR multilayer privés sont reliés par checkpoints aux empreintes exactes de source/export. Le protocole de présentation r2 utilise +2EV par rapport au studio source, avec fond caméra compensé ; aucune matière ni lumière objet n’est modifiée.

La coque annulaire, ses cinq reliefs, ses pattes/nervures et six passages ont une épaisseur réelle. Le candidat est lié aux photos YDY02002 ; les dimensions, profondeurs, sections et emplacements restent estimés. Le clip central supérieur et les vis séparées ne sont pas fabriqués. L’identité RDC et le montage exact sont inconnus ; l’optique, les accessoires électriques, le carénage rouge et les clignotants sont des pièces suivantes. Le lot12 est incomplet.

Les inversions de normales et contours anguleux précédents ont été corrigés avant matière. La macro finale révèle toutefois de petites marches de reflets sur les nervures basses : cette v1 devient un diagnostic conservé, pendant une correction distincte du champ de normales. Les buffers géométriques/normales/UV/indices restent identiques à la grise v4. Shader propre original estimé, sans phototexture ni grain mesuré. Les cartes UV de l’étude n’établissent pas un dépliage final de patine. Contrôles moteur, assemblage, réception artistique et Safari physique restent distincts.
""")
files=[R/x['path']for x in frozen['files']]+[P/'source-freeze-manifest.json',Path(__file__),P/'render-checkpoints.json',P/'visual-reading.json',P/'render-report.json',P/'README.md']+[P/(n+'.png')for n in names];save(P/'freeze-manifest.json',{'schema':1,'revision':'headlamp-housing-v1','source_sha256':a['source_sha256'],'export_sha256':a['export_sha256'],'state':'Four real96 views actually saved/read; diagnostic v1 with lowerrib highlight steps, separate v2 correction pending. Exactidentity/mount/clip/art remain open.','files':[{'path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size}for p in sorted(set(files))],'private_EXR_checkpoints':[{k:v[k]for k in ['name','EXR_private_path','EXR_sha256']}for v in rows],'art_accepted':False});print('CLOSED',a['source_sha256'],a['export_sha256'])
