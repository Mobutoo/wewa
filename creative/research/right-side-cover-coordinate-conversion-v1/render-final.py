"""Independent neutral environment on third final view, without source/material edits."""
import bpy,sys,json,hashlib
from pathlib import Path
R=Path('/workspace/wewa');K='right-side-cover-coordinate-conversion-v1';H=R/'assets-src/moto-components'/K;O=R/'creative/reviews'/K;sys.path.insert(0,str(H));import build
original=build.look

def look(ob,t):
 original(ob,t)
 if ob.type=='CAMERA' and abs(ob.location.x+.55)<1e-5 and abs(ob.location.y-.20)<1e-5:
  for light in bpy.data.lights:light.energy=0
  w=bpy.data.worlds.new('Independent neutral uniform white environment');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);w.node_tree.nodes['Background'].inputs[1].default_value=.65;bpy.context.scene.world=w
build.look=look
build.render('final')
p=O/'final-render-report.json';d=json.loads(p.read_text());d.update(render_wrapper_path=str(Path(__file__).relative_to(R)),render_wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),independent_neutral_lighting='Third view: studio lights zero, separate uniform white environment strength0.65, lookNone; native parent materials untouched')
p.write_text(json.dumps(d,indent=2)+'\n')
