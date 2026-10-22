# Adapted local routing wrapper SHA256 03293637642b8585ab4dc65afa991da58541893499aff79d14716f6b896863f3
"""Run unchanged stock capturev5 with isolated read/browser catalogue routing; no shared writes."""
from pathlib import Path
import json,runpy,sys,hashlib
from playwright.sync_api import Browser
R=Path('/workspace/wewa');O=Path(__file__).resolve().parent
cfg=json.loads((O/'coordinator-config.json').read_text());catalog=json.dumps({'assets':{cfg['key']:cfg}})
original_read=Path.read_text
original_page=Browser.new_page
shared=R/'tools/motorcycle-lab/catalog.json';before=hashlib.sha256(shared.read_bytes()).hexdigest()
def read_local(self,*a,**kw):
 if self.resolve()==shared.resolve():return catalog
 return original_read(self,*a,**kw)
def isolated_page(self,*a,**kw):
 page=original_page(self,*a,**kw)
 page.route('**/tools/motorcycle-lab/catalog.json',lambda route:route.fulfill(status=200,content_type='application/json',body=catalog))
 return page
Path.read_text=read_local;Browser.new_page=isolated_page
sys.argv=[str(R/'tools/capture_motorcycle_exterior_v5.py'),cfg['key'],'--port','4164']
try:runpy.run_path(sys.argv[0],run_name='__main__')
finally:Path.read_text=original_read;Browser.new_page=original_page
after=hashlib.sha256(shared.read_bytes()).hexdigest() # Other coordinator owns root; concurrent changes allowed, no writes here
p=O/'inspection-v5/engine-check.json';report=json.loads(p.read_text());report['isolated_catalogue_routing']={'config':str((O/'coordinator-config.json').relative_to(R)),'config_sha256':hashlib.sha256((O/'coordinator-config.json').read_bytes()).hexdigest(),'wrapper':str(Path(__file__).resolve().relative_to(R)),'wrapper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'catalogue_read_redirect_only':True,'browser_route_fulfill_only':True,'shared_catalogue_sha256_before':before,'shared_catalogue_sha256_after':after,'concurrent_external_catalogue_change':before!=after,'shared_catalogue_written':False};p.write_text(json.dumps(report,indent=2)+'\n')
