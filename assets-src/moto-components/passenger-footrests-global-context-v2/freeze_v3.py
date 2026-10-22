from pathlib import Path
import json,hashlib,struct,datetime
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
collision=json.loads((O/'collision-audit-v3.json').read_text());exports=json.loads((O/'export-parity-v3.json').read_text());runtime=json.loads((O/'runtime-check.json').read_text());renders=json.loads((O/'native-96-v3-report.json').read_text())
assert len(collision['parts'])==6 and all(r['frame_surface_intersections']==0 and r['sns_surface_intersections']==0 for r in collision['parts']);assert exports['strict_pass']and exports['actual_gray_material_corner_buffers_and_world_matrices_equal']and exports['native_export_bounds_pass'];assert not runtime['page_errors']and not runtime['http_failures'];assert len(renders)==3 and all(r['samples']==96 for r in renders)
fragment=json.loads((O/'integration-fragment-v3.json').read_text());fragment['status']='frozen_v3_technical_context_validated; no installed-fit or G8 reception';fragment['SNS_context_required']={'LH_euler_XYZ_deg':[0,20,-90],'RH_euler_XYZ_deg':[0,-20,90],'native_roots':collision['SNS_roots'],'note':'Source Y transverse sign reverses on RH; source Z longitudinal inclination remains the same. SNS are diagnostic dependencies, not six-part additions.'};fragment['evidence']={'collision':'collision-audit-v3.json','native_reopened':'native-reopen-v3.json','native_96_report':'native-96-v3-report.json','export_strict_parity':'export-parity-v3.json','runtime':'runtime-check.json','source_register':'source-register-final.json','freeze':'freeze-v3.json'};fragment['native_96_views_actually_read']=['LH','RH','profile'];fragment['runtime_views_actually_read']=['quarter','reverse'];fragment['fit_qualified']=False;fragment['art_accepted']=False
for r in fragment['additions']:assert sha(R/r['source'])==r['sha256']
(O/'integration-fragment-v3.json').write_text(json.dumps(fragment,indent=2)+'\n')
def string(f):
 b=bytearray()
 while True:
  c=f.read(1);assert c
  if c==b'\0':return b.decode()
  b+=c
raw=[]
for p in sorted(O.glob('*.exr')):
 with p.open('rb')as f:
  assert f.read(4)==b'\x76\x2f\x31\x01';f.read(4);attrs={}
  while True:
   n=string(f)
   if not n:break
   kind=string(f);size=struct.unpack('<I',f.read(4))[0];attrs[n]=f.read(size)
  ch={};data=attrs['channels'];i=0
  while data[i]:
   end=data.index(0,i);n=data[i:end].decode();i=end+1;ch[n]=struct.unpack_from('<i',data,i)[0];i+=16
  assert all(v==2 for v in ch.values());x0,y0,x1,y1=struct.unpack('<4i',attrs['dataWindow']);res=[x1-x0+1,y1-y0+1]
  if p.name.startswith('native-96-v3'):assert res==[1000,800]
  raw.append({'file':p.name,'all_channels_FLOAT32':True,'resolution':res,'channels':ch,'sha256':sha(p)})
(O/'raw32-check-v3.json').write_text(json.dumps({'files':raw,'scope':'Actual saved EXR channel and dimension headers; not radiometric or artistic certification'},indent=2)+'\n')
files=[]
for p in sorted(O.rglob('*')):
 if p.is_file()and p.name!='freeze-v3.json':
  assert p.stat().st_size<100*1024**2;files.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)})
manifest={'id':'passenger-footrests-global-context-v2','revision':'v3','frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'canonical_fragment':str((O/'integration-fragment-v3.json').relative_to(R)),'canonical_native':str((O/'context-material-linked-v3.blend').relative_to(R)),'native_collection':'PASSENGER_FOOTRESTS_GLOBAL_CONTEXT_V2','count':{'parts':6,'stays_independent':2,'peg_common_exemplars':2,'rubber_common_exemplars':2,'new_physical_meshes':0,'triangles_exported':649590},'frame_and_both_SNS_surface_crossings':0,'native_96_float32_views_actually_read':3,'runtime_views_actually_read':2,'strict_errors':0,'strict_warnings':0,'actual_node_geometry_normals_uv_matrices_parity':True,'historical_freezes_81_and_88_files_unchanged':True,'all_files_under_100MiB':True,'art_accepted':False,'fit_qualified':False,'G8':'not acquired','preserved_source_limits':['5mm noncoaxial review hinge offset','22mm nominal rubber overhang','90degree diagnostic cut','donor terminal gaps LH71/28mm RH107/72mm; no hidden bridges/pins/welds'],'rejected_evidence_retained':True,'source_photo_pixels_private':True,'freeze_excludes_only_itself':True,'files':files,'bytes_total':sum(r['bytes']for r in files)}
(O/'freeze-v3.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'files':len(files),'bytes':manifest['bytes_total'],'fragment_sha256':sha(O/'integration-fragment-v3.json'),'freeze_sha256':sha(O/'freeze-v3.json')}))
