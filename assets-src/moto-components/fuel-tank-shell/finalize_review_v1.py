"""Close only metadata after four real96 files were actually opened; no source mutation."""
from pathlib import Path
import json,hashlib,struct,datetime
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/fuel-tank-shell-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,j:p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n');build=json.loads((O/'build-report.json').read_text());cp=json.loads((O/'render-checkpoints.json').read_text());frozen=json.loads((O/'source-freeze-manifest.json').read_text());assert sha(H/'fuel-tank-shell-v1.blend')==build['source_sha256']==cp['source_sha256'];assert sha(H/'fuel-tank-shell-inspection.glb')==build['export_sha256']==cp['export_sha256']
for row in frozen['files']:assert sha(R/row['path'])==row['sha256'],row['path']
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
   name=zs()
   if not name:return[]
   typ=zs();size=struct.unpack('<I',f.read(4))[0];v=f.read(size)
   if typ=='chlist':
    out=[];k=0
    while k<len(v)and v[k]:
     end=v.index(0,k);out.append(v[k:end].decode());k=end+17
    return out
observations={'right-oblique':'WEWA upright and readable; upper pink-red and broad white studio highlights retained. Estimated rear flange below crown and single lower ear visible.','left-oblique':'WEWA upright and readable on opposite flank, original white/gold design proposal. Large studio reflection crosses graphic and brightens red; no calibrated finish claim.','mouth-detail':'Deliberate close crop actually read: open finite neck with estimated concentric profile and two nearby holes remain readable. No cap/locking mechanism or hidden lower tank added.','open-underside-scope':'Whole skin seen from below: intentionally absent pan/tunnel and dark inspection inner skin are explicit; flange/ear contact is estimated, not received mounting.'};assert set(cp['views'])==set(observations);rows=[]
for name,obs in observations.items():
 v=cp['views'][name];cfg=v['configuration'];png=R/v['PNG_path'];exr=Path(v['EXR_private_path']);assert v['actually_saved']and cfg['samples']==96 and sha(png)==v['PNG_sha256']and sha(exr)==v['EXR_sha256'];chs=channels(exr);assert any('Noisy Image' in x for x in chs)and any('Denoising Albedo' in x for x in chs)and any('Denoising Normal' in x for x in chs)
 rows.append({'name':name,'camera':{'location_m':cfg['camera_eye_m'],'target_m':cfg['target_m'],'actual_matrix':cfg['actual_camera_matrix'],'lens_mm':60,'sensor_width_mm':36,'sensor_fit':'HORIZONTAL','near_far_m':cfg['near_far_m'],'intentional_crop':bool(cfg['view'].get('crop'))},'PNG_path':v['PNG_path'],'PNG_sha256':v['PNG_sha256'],'EXR_private_path':str(exr),'EXR_sha256':v['EXR_sha256'],'EXR_actual_channels':chs,'config_sha256':v['config_sha256'],'paired_preview_config_sha256':cfg['paired_preview_config_sha256'],'actually_saved':True,'actually_read':True,'observations':obs})
limits=['Estimated external upper/lateral upholstery-like metal skin only; no pan/tunnel/fluid capacity/full tank.','ExactRDC code, dimensions and cap/tap/mount interfaces not established.','Related red/black isolated products are different exemplars, not calibrated opposing views.','Opaque front return remains one surface hypothesis; true opening/reflection unresolved.','Appendage root contacts and poses estimated, not accepted mounting/welds.','Original paint, metal and white/gold WEWA graphic are proposals; broad studio highlights and pink upper response are retained. Neutral HDR appointment separate and not radiometrically calibrated.','No source/browser photographic parity, artistic acceptance or physical iPhone test.']
write(O/'visual-reading.json',{'schema':1,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':build['source_sha256'],'export_sha256':build['export_sha256'],'state':'Four final96 views actually saved/opened after gray6 and studio12/neutral HDR reviews; bounded original material candidate','views':{r['name']:{'read':True,'PNG_sha256':r['PNG_sha256'],'observations':r['observations']}for r in rows},'neutral_appointment':'creative/reviews/fuel-tank-shell-v1-neutral-lighting/visual-reading.json','limits':limits,'art_accepted':False})
write(O/'render-report.json',{'schema':1,'revision':'fuel-tank-shell-v1','source_sha256':build['source_sha256'],'export_sha256':build['export_sha256'],'renderer':'Blender4.3.2 Cycles96/OpenImageDenoise CPU','samples':96,'resolution_px':[1000,800],'source_and_export_unchanged':True,'views':rows,'limits':limits,'art_accepted':False,'physical_iphone_tested':False})
(O/'README.md').write_text('''# Réservoir WEWA — candidat extérieur v1

Quatre vraies vues Cycles96/OIDN CPU ont été sauvées et ouvertes : flanc droit, flanc gauche, bouche en détail et dessous ouvert. Les checkpoints relient chaque PNG à la source, la caméra, au protocole et à son EXR multilayer privé ; les passes brutes, albedo et normales de débruitage sont réellement présentes. Les caméras, matières et lumières sont les mêmes que les quatre aperçus12 lus avant gel.

Le graphisme original WEWA blanc/or remplace BOXER et se lit debout sur les deux flancs. Les grands reflets blancs et le sommet rose clair sous le studio restent visibles. Un appoint sous ciel neutre à caméra droite identique conserve l’albedo et calcule l’exposition sur une vraie carte diffuse18% ; ce n’est pas une calibration de couleur ni une réception artistique.

La pièce reste une peau supérieure/latérale estimée. Dessous, tunnel, capacité, montages cachés, bouchon et robinet sont exclus de ce candidat. Les cotes et contacts des appendages sont estimés ; le retour avant opaque reste une hypothèse. Aucune compatibilité exacteRDC, réception graphique ou validation iPhone n’est déduite des contrôles techniques.
''')
files=[R/r['path']for r in frozen['files']]+[O/'source-freeze-manifest.json',Path(__file__),O/'render-checkpoints.json',O/'render-report.json',O/'visual-reading.json',O/'README.md']+[R/r['PNG_path']for r in rows];write(O/'freeze-manifest.json',{'schema':1,'revision':'fuel-tank-shell-v1','source_sha256':build['source_sha256'],'export_sha256':build['export_sha256'],'state':'Four actual96 views saved and read; bounded exterior tank skin/original WEWA candidate, no full tank/fit/art certification','files':[{'path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size}for p in sorted(set(files))],'private_EXR_checkpoints':[{k:r[k]for k in ['name','EXR_private_path','EXR_sha256']}for r in rows],'art_accepted':False});print('CLOSED',len(set(files)),build['source_sha256'],build['export_sha256'])
