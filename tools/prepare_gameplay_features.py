"""Authored gameplay overlay on supplied roads; never modifies source geography."""
import json,math,heapq,hashlib
from pathlib import Path
from shapely.geometry import Polygon,LineString
from shapely.strtree import STRtree
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'app/public/world/gombe.json';w=json.loads(path.read_text());nodes=w['nodes']
buildings=[Polygon(b['rings'][0],b['rings'][1:]) for b in w['buildings']];tree=STRtree(buildings)
adj={i:[] for i in range(len(nodes))};rejected=[]
for i,e in enumerate(w['segments']):
 a,b=e['a'],e['b'];line=LineString([nodes[a],nodes[b]]).buffer(.6)
 if any(line.intersects(buildings[j]) for j in tree.query(line)):rejected.append(i);continue
 if e['width']<2:continue
 one=str(e.get('oneway') or '').lower();d=math.dist(nodes[a],nodes[b])
 if one not in ['-1','reverse']:adj[a].append((b,d,i))
 if one not in ['yes','1','true']:adj[b].append((a,d,i))
def shortest(a,b):
 q=[(0,a)];cost={a:0};prev={}
 while q:
  d,u=heapq.heappop(q)
  if u==b:break
  if d!=cost[u]:continue
  for v,length,edge in adj[u]:
   if d+length<cost.get(v,math.inf):cost[v]=d+length;prev[v]=(u,edge);heapq.heappush(q,(d+length,v))
 if b not in prev:return None
 p=[b];edges=[]
 while p[-1]!=a:u,e=prev[p[-1]];p.append(u);edges.append(e)
 return cost[b],list(reversed(p)),set(edges)
route=w['route'];progress=[0]
for a,b in zip(route,route[1:]):progress.append(progress[-1]+math.dist(a,b))
route_nodes=[min(range(len(nodes)),key=lambda i:math.dist(nodes[i],p)) for p in route]
candidates=[]
for i in range(len(route)-2):
 for j in range(i+2,len(route)-1):
  direct=progress[j]-progress[i]
  if direct<160 or direct>1000:continue
  r=shortest(route_nodes[i],route_nodes[j])
  if r and direct-r[0]>80 and r[0]/direct<.8:candidates.append({'i':i,'j':j,'main':direct,'length':r[0],'nodes':r[1],'edges':r[2],'saving':direct-r[0]})
selected=[]
# Prefer entries useful while delivering, then different geometry rather than adjacent starts.
for c in sorted(candidates,key=lambda c:(c['i']>14,-c['saving'])):
 if any(len(c['edges']&s['edges'])/max(1,min(len(c['edges']),len(s['edges'])))>.45 for s in selected):continue
 selected.append(c)
 if len(selected)==2:break
features=[];tokens=[]
for i,c in enumerate(selected):
 pts=[nodes[n] for n in c['nodes']];name=['La traverse','Le passage du relais'][i]
 features.append({'id':f'shortcut-{i+1}','name':name,'points':pts,'saving_m':round(c['saving'],1),'source_ids':sorted(set(w['segments'][e]['source_id'] for e in c['edges'])),'provenance':'Authored motorcycle itinerary on supplied at-grade directed roads; not a surveyed alley or invented road','start_progress_m':round(progress[c['i']],1),'end_progress_m':round(progress[c['j']],1)})
 tokens.append({'id':f'nitro-token-{i+1}','point':pts[len(pts)//2]})
w['traffic']={'count':8,'seed':31020};w['shortcuts']=features;w['nitroTokens']=tokens;w['surfacePatches']=[]
path.write_text(json.dumps(w,separators=(',',':'),ensure_ascii=False))
report={'version':1,'source_geometry_unchanged':True,'clearance_m':.6,'blocked_segments':rejected,'directed_motorcycle_segments':sum(map(len,adj.values())),'shortcuts':features,'traffic_priority_status':'Conservative fictional yield rules; actual signs and local priorities not certified','terrain':'Flat source baseline; authored SurfaceField supports ramps/potholes but no invented measured relief shipped','source_sha256':hashlib.sha256((ROOT/'WEWA_Developpement_Web/data/pilot/road_centerlines.local.json').read_bytes()).hexdigest()}
(ROOT/'WEWA_Developpement_Web/validation/gameplay-features.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'shortcuts':len(features),'saving_m':[f['saving_m'] for f in features],'rejected_segments':len(rejected)}))
