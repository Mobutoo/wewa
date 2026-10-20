"""Functional icon vector contours from private documentary photo; no photo texture.
Native-pixel threshold only helps tracing. Original simplified editable curves are
made later; no pixel raster is put in the repository or runtime bundle.
"""
from PIL import Image
import json,math,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];photo=Path('/workspace/wewa-assets/references/switchgear/bikebox-LH.webp');im=Image.open(photo).convert('RGB')

def simplify_open(points,epsilon):
 if len(points)<3:return points
 a,b=points[0],points[-1];dx=b[0]-a[0];dy=b[1]-a[1];den=math.hypot(dx,dy)
 distances=[abs(dx*(a[1]-p[1])-(a[0]-p[0])*dy)/den if den else math.dist(p,a) for p in points]
 i=max(range(len(points)),key=lambda i:distances[i])
 if distances[i]>epsilon:return simplify_open(points[:i+1],epsilon)[:-1]+simplify_open(points[i:],epsilon)
 return [a,b]
def simplify_closed(points,epsilon=.65):
 far=max(range(len(points)),key=lambda i:math.dist(points[i],points[0]));return simplify_open(points[:far+1],epsilon)[:-1]+simplify_open(points[far:]+[points[0]],epsilon)[:-1]
def trace(box,minimum_area):
 pixels={(x,y) for y in range(box[1],box[3]) for x in range(box[0],box[2]) if min(im.getpixel((x,y)))>155};components=[]
 while pixels:
  seed=pixels.pop();pending=[seed];component={seed}
  while pending:
   x,y=pending.pop()
   for point in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
    if point in pixels:pixels.remove(point);pending.append(point);component.add(point)
  if len(component)>=minimum_area:components.append(component)
 components.sort(key=lambda c:min(y for x,y in c));out=[]
 for component in components:
  edges=set()
  for x,y in component:
   for neighbour,a,b in [((x,y-1),(x,y),(x+1,y)),((x+1,y),(x+1,y),(x+1,y+1)),((x,y+1),(x+1,y+1),(x,y+1)),((x-1,y),(x,y+1),(x,y))]:
    if neighbour not in component:edges.add((a,b))
  paths=[]
  while edges:
   a,b=min(edges);edges.remove((a,b));points=[a];start=a
   while b!=start:
    points.append(b);choices=[e for e in edges if e[0]==b]
    if not choices:raise ValueError(('Open contour',b))
    dx,dy=b[0]-a[0],b[1]-a[1]
    def priority(edge):
     ex,ey=edge[1][0]-b[0],edge[1][1]-b[1];angle=round(math.atan2(dx*ey-dy*ex,dx*ex+dy*ey)/(math.pi/2));return {1:3,0:2,-1:1,2:0,-2:0}.get(angle,-1)
    edge=max(choices,key=priority);edges.remove(edge);a,b=edge
   simplified=simplify_closed(points);area=sum(simplified[j-1][0]*p[1]-p[0]*simplified[j-1][1] for j,p in enumerate(simplified))/2
   if abs(area)>=3:paths.append({'points_px':simplified,'signed_area_px2':area,'is_hole':area<0})
  xs=[x for x,y in component];ys=[y for x,y in component];out.append({'white_pixels':len(component),'bounds_px':[min(xs),min(ys),max(xs)+1,max(ys)+1],'loops':paths})
 return out
j={'schema':1,'source_photo':str(photo),'source_sha256':hashlib.sha256(photo.read_bytes()).hexdigest(),'source_pixels':list(im.size),'threshold_for_tracing_only':155,'simplification_tolerance_px':.65,'method':'Trace connected white ink in tight native-pixel boxes, reject isolated noise; polygon boundaries preserve holes. Simplified vector contours, not photographic textures. Original Bezier handles/shape projection are authored in Blender.','glyphs':{}}
for name,box in [('high_beam',[403,115,463,150]),('low_beam',[408,170,466,205]),('horn',[286,432,361,480])]:
 components=trace(box,20 if name!='horn' else 300);j['glyphs'][name]={'crop_px':box,'components':components}
 # A beam has one D-shaped boundary component and exactly five separated rays.
 if name!='horn':assert len(components)==6,(name,len(components));j['glyphs'][name]['documented_visible_rays']=5
print({name:[(c['white_pixels'],c['bounds_px'],len(c['loops'])) for c in g['components']] for name,g in j['glyphs'].items()})
out=ROOT/'creative/research/switchgear-left/marking-vector-contours-v2.json';out.write_text(json.dumps(j,indent=2)+'\n')
