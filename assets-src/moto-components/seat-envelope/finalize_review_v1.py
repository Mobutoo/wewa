"""Close only metadata after four real96 files were actually opened; no source mutation."""
from pathlib import Path
import json,hashlib,struct,datetime
H=Path(__file__).resolve().parent;R=H.parents[2];O=R/'creative/reviews/seat-envelope-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,j:p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n');build=json.loads((O/'build-report.json').read_text());cp=json.loads((O/'render-checkpoints.json').read_text());frozen=json.loads((O/'source-freeze-manifest.json').read_text());assert sha(H/'seat-envelope-v1.blend')==build['source_sha256']==cp['source_sha256'];assert sha(H/'seat-envelope-inspection.glb')==build['export_sha256']==cp['export_sha256']
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
observations={'upper-oblique':'Whole cover read: narrow raised nose, shallow middle and broader higher rear. Large studio reflection brightens the black vinyl; material is nonmetallic and original.','rear-opposite':'WEWA rear word upright/readable; rear piping remains visible. Black vinyl appears gray in bright studio reflections, not a calibrated color sample.','rear-seam-detail':'Deliberate cropped macro read: original grain, C2 rear piping and surface-conforming102estimated thread strands visible. No new definite floating or pinched defect imposed; exactcurrent cover identity/embossing unresolved.','open-underside-scope':'Whole underside read: lower boundary intentionally open, no foam/base/ribs/supports/mounts represented. Not a full seat.','neutral-upper-oblique':'Actual96 neutral HDR view read at same upper camera and same materials: dark blue-black sky reflection. Exposure from prior actual18percent diffuse card, no WB/albedo change; HDR not radiometrically calibrated.'};assert set(cp['views'])==set(observations);rows=[]
for name,obs in observations.items():
 v=cp['views'][name];cfg=v['configuration'];png=R/v['PNG_path'];exr=Path(v['EXR_private_path']);assert v['actually_saved']and cfg['samples']==96 and sha(png)==v['PNG_sha256']and sha(exr)==v['EXR_sha256'];chs=channels(exr);assert any('Noisy Image' in x for x in chs)and any('Denoising Albedo' in x for x in chs)and any('Denoising Normal' in x for x in chs)
 rows.append({'name':name,'camera':{'location_m':cfg['camera_eye_m'],'target_m':cfg['target_m'],'actual_matrix':cfg['actual_camera_matrix'],'lens_mm':60,'sensor_width_mm':36,'sensor_fit':'HORIZONTAL','near_far_m':cfg['near_far_m'],'intentional_crop':bool(cfg['view'].get('crop'))},'PNG_path':v['PNG_path'],'PNG_sha256':v['PNG_sha256'],'EXR_private_path':str(exr),'EXR_sha256':v['EXR_sha256'],'EXR_actual_channels':chs,'config_sha256':v['config_sha256'],'paired_preview_sha256':cfg['paired_preview_sha256'],'paired_preview_type':cfg['paired_preview_type'],'lighting':cfg['lighting'],'actually_saved':True,'actually_read':True,'observations':obs})
limits=['Estimated external upholstery envelope/rear piping/thread candidate only; no foam/base/ribs/supports/mounts or completed hidden front seam.','Exactcurrent RDC partcode, dimensions, shape/projection and assembly compatibility not established.','RelatedJV191001 top/rear/underside photos support visible details but do not certify currentRDC underside or embossing. Plain proposal is not evidence of actual absence of embossed lines.','Initial main symmetry, section widths/heights and rear seam continuation/radius/thread count/pitch are authored estimates.','Original black vinyl/grain and WEWA lettering are proposals; gray studio and dark blue neutral sky responses remain separately documented. No OEM finish calibration.','All101320oriented POSITION/NORMAL/UV triangles unchanged from gray4; transport-only tangent projection documented, no bit-identical Mikk or visual parity claim.','No source/browser photographic parity, artistic acceptance or physical iPhone test.']
write(O/'visual-reading.json',{'schema':1,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':build['source_sha256'],'export_sha256':build['export_sha256'],'state':'Five final96 views actually saved/opened after gray4 and studio12/neutral HDR reviews; bounded original cover candidate','views':{r['name']:{'read':True,'PNG_sha256':r['PNG_sha256'],'observations':r['observations']}for r in rows},'neutral_appointment':'creative/reviews/seat-envelope-v1-neutral-lighting/visual-reading.json','limits':limits,'art_accepted':False})
write(O/'render-report.json',{'schema':1,'revision':'seat-envelope-v1','source_sha256':build['source_sha256'],'export_sha256':build['export_sha256'],'renderer':'Blender4.3.2 Cycles96/OpenImageDenoise CPU','samples':96,'resolution_px':[1000,800],'source_and_export_unchanged':True,'views':rows,'limits':limits,'art_accepted':False,'physical_iphone_tested':False})
(O/'README.md').write_text('''# Selle WEWA — enveloppe extérieure candidate v1

Cinq vraies vues Cycles96/OIDN CPU ont été sauvées et ouvertes : entière avant-oblique, entière arrière, macro couture, dessous ouvert et entière sous ciel neutre. Chaque PNG est relié au gel, caméra, protocole et EXR multilayer privé ; les passes brutes, albedo et normales de débruitage sont réellement présentes.

Les quatre caméras/lumières studio sont celles des aperçus12. Le vinyle noir paraît gris clair dans ces grands reflets et sombre/bleuté sous le ciel. La cinquième vue conserve exactement la caméra du vrai appoint neutre12 et son exposition issue d’une carte diffuse18% réellement rendue, sans retoucher albedo ou balance des blancs. Le ciel et l’exposition ne sont pas radiométriquement calibrés.

Le mot original WEWA remplace BOXER à l’arrière et se lit debout. Le grain est original, le bourrelet et102points de couture sont des candidats estimés d’après JV191001 lié. La housse actuelleRDC embossée ou lisse reste non tranchée ; cette proposition ne prouve pas l’absence de lignes. Les101320triangles de position/normales/UV sont identiques au maître gris4. La petite projection des tangentes de transport est documentée sans en déduire une parité visuelle.

Le dessous reste ouvert. Mousse, embase, nervures, appuis et interfaces de fixation seront des éléments séparés ; aucune selle complète ou compatibilité actuelle n’est reçue. Cotes, sections et matériaux restent estimés. Aucun contrôle technique ne vaut réception artistique, montage ou validation iPhone.
''')
files=[R/r['path']for r in frozen['files']]+[O/'source-freeze-manifest.json',Path(__file__),O/'render-checkpoints.json',O/'render-report.json',O/'visual-reading.json',O/'README.md']+[R/r['PNG_path']for r in rows];write(O/'freeze-manifest.json',{'schema':1,'revision':'seat-envelope-v1','source_sha256':build['source_sha256'],'export_sha256':build['export_sha256'],'state':'Five actual96 views saved and read; bounded exterior upholstered cover/original WEWA candidate, no full seat/fit/art certification','files':[{'path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size}for p in sorted(set(files))],'private_EXR_checkpoints':[{k:r[k]for k in ['name','EXR_private_path','EXR_sha256']}for r in rows],'art_accepted':False});print('CLOSED',len(set(files)),build['source_sha256'],build['export_sha256'])
