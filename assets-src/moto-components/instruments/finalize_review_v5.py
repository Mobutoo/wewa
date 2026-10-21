"""Metadata closure only after actual reading; no rendering or source changes."""
from pathlib import Path
import json,hashlib,struct
H=Path(__file__).resolve().parent;R=H.parents[2];P=R/'creative/reviews/instruments-v5';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();save=lambda p,d:p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n');a=json.loads((P/'source-geometry-check.json').read_text());c=json.loads((P/'render-checkpoints.json').read_text());reading=json.loads((P/'visual-reading.json').read_text());frozen=json.loads((P/'source-freeze-manifest.json').read_text());assert sha(H/'instruments-v5.blend')==a['source_sha256']==c['source_sha256']==reading['source_sha256'];assert sha(H/'instruments-v5-inspection.glb')==a['export_sha256']==c['export_sha256']==reading['export_sha256']
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
names=['whole-rear','cover-context'];assert set(c['views'])==set(names);rows=[]
for n in names:
 v=c['views'][n];png=R/v['PNG_path'];exr=Path(v['EXR_private_path']);r=reading['views'][n];assert v['actually_saved']and r['read']and sha(png)==v['PNG_sha256']==r['PNG_sha256']and sha(exr)==v['EXR_sha256']and v['config']['samples']==96
 chs=channels(exr);assert any('Denoising Albedo'in x for x in chs)and any('Denoising Normal'in x for x in chs)and any('Noisy Image'in x for x in chs)
 rows.append({'name':n,'camera':v['config']['camera'],'PNG_path':v['PNG_path'],'PNG_sha256':v['PNG_sha256'],'EXR_private_path':str(exr),'EXR_sha256':v['EXR_sha256'],'EXR_actual_channels':channels(exr),'config_sha256':v['config_sha256'],'actually_saved':True,'actually_read':True,'observations':r['observations']})
save(P/'render-report.json',{'schema':1,'revision':'instruments-v5','source_sha256':a['source_sha256'],'export_sha256':a['export_sha256'],'renderer':'Blender4.3.2 Cycles96/OpenImageDenoise CPU','samples':96,'resolution_px':[1100,850],'source_and_export_unchanged':True,'correction_scope':'Central-cover side normal field from3 to4, then two planar pod cap fields from4 to5; indexed triangle POSITION/UV/material and transforms unchanged across chain.','views':rows,'limits':reading['limits'],'art_accepted':False,'physical_iphone_tested':False})
(P/'README.md').write_text("""# Compteurs v5 — deux nouvelles vues ciblées

Le dos entier des compteurs et le carter en contexte clé/faisceau ont été sauvés en Cycles96/OIDN CPU puis réellement ouverts. PNG et EXR multilayer32 privés sont reliés aux sources, protocole et caméras par checkpoints. Les passes bruitées/albédo/normales sont contrôlées dans l’en-tête EXR. Le contexte conserve exactement la caméra/lumières et les composants gelés de cockpit-cablesv2 ; seule la copie du carter5 est utilisée en RAM, sans nouvelle source d’assemblage.

La v4 intermédiaire reste gelée avec ses aperçus : le carter y était corrigé mais les fonds des deux pods conservaient un faux creux de normales. Aucun96 ni enregistrement4. La v5 garde le carter4, corrige uniquement les caps réellement plans des deux pods et leurs limites de normales. La chaîne3→4→5 protège positions/topologie/UV/matières/matrices, cadrans, USB, angles et contrôleurs. Les autres176objets sources et173nœuds de maillage GLB restent exacts par rapport à4. Une nouvelle séparation de normales peut modifier la duplication de sommets/indexage, sans déplacer de triangle physique.

Les dimensions, profondeur, montage et grain restent estimés ; l’identité RDC exacte et les angles de calibration ne sont pas établis. LCD1–5 = démonstration d’affichage, sans certification du nombre de rapports. Les réserves de reflets HDR des vitres restent ouvertes. Aucun essai physique iPhone, parité d’apparence moteur ou réception artistique n’est déduit de ces contrôles.
""")
files=[R/x['path']for x in frozen['files']]+[P/'source-freeze-manifest.json',Path(__file__),P/'render-checkpoints.json',P/'visual-reading.json',P/'render-report.json',P/'README.md']+[P/(n+'.png')for n in names];save(P/'freeze-manifest.json',{'schema':1,'revision':'instruments-v5','source_sha256':a['source_sha256'],'export_sha256':a['export_sha256'],'state':'Two real96 views actually saved/read; normals-only instruments revision3-to4-to5, unchanged physical geometry/material/rigs; variant, calibration, mount, runtime appearance and artistic reception open.','files':[{'path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size}for p in sorted(set(files))],'private_EXR_checkpoints':[{k:v[k]for k in ['name','EXR_private_path','EXR_sha256']}for v in rows],'art_accepted':False});print('CLOSED',a['source_sha256'],a['export_sha256'])
