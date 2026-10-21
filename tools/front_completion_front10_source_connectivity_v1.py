"""Read source edge graph independently; useful for unioned sheet components, no source mutation."""
import bpy,sys,json,hashlib
from pathlib import Path
R=Path('/workspace/wewa');source,out=sys.argv[sys.argv.index('--')+1:][:2];p=R/source;bpy.ops.wm.open_mainfile(filepath=str(p));rows=[]
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 m=ob.data;parent=list(range(len(m.vertices)))
 def root(a):
  while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
  return a
 for e in m.edges:
  a,b=(root(i)for i in e.vertices)
  if a!=b:parent[a]=b
 counts={}
 for i in range(len(parent)):
  r=root(i);counts[r]=counts.get(r,0)+1
 rows.append({'object':ob.name,'connected_components':len(counts),'component_vertex_counts':sorted(counts.values(),reverse=True)});assert len(counts)==1,(ob.name,counts)
(R/out).write_text(json.dumps({'source':source,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'method':'Mesh source edge graph, one connected component per explicitly separate source body; not visual fidelity or fitted interfaces','objects':rows},indent=2))
