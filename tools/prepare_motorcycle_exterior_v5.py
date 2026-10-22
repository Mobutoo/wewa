"""Freeze existing source attachments and bounded exterior-only placements; never edit source libraries."""
import hashlib
import json
import math
import struct
from pathlib import Path
import numpy as np

R=Path(__file__).resolve().parents[1]
D=R/'creative/research/motorcycle-exterior-v5';D.mkdir(parents=True,exist_ok=True)
catalog=json.loads((R/'tools/motorcycle-lab/catalog.json').read_text())['assets']
base=json.loads((R/'creative/reviews/whole-exterior-coverage-v22/linked-parents-check.json').read_text())
routes=json.loads((R/'creative/research/motorcycle-assembled-v4/export-routes.json').read_text())
rows={x['key']:x for x in base['parents']};route_rows={x['key']:x for x in routes['rows']}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def matrix(rotation=(0,0,0),translation=(0,0,0)):
    x,y,z=[math.radians(v) for v in rotation];cx,sx,cy,sy,cz,sz=math.cos(x),math.sin(x),math.cos(y),math.sin(y),math.cos(z),math.sin(z)
    rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]);ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]);rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
    m=np.eye(4);m[:3,:3]=rz@ry@rx;m[:3,3]=translation;return m


def parent(key):
    r=rows[key]
    if 'matrix_world' in r:return np.array(r['matrix_world'])
    return matrix(r['rotation_degrees'],r['translation_m'])@np.diag([*r['scale'],1])


def mesh_names(file):
    with file.open('rb') as f:
        f.seek(12);length,kind=struct.unpack('<II',f.read(8));assert kind==0x4e4f534a;d=json.loads(f.read(length))
    return [n['name'] for n in d['nodes'] if 'mesh' in n]


changes=[]


def attach(key,asset,pose,reason,replacement=False):
    c=catalog[asset];source='assets-src/moto-components/'+c['source'];glb='assets-src/moto-components/'+next(f for f in c['files'] if f.endswith('.glb'))
    row={'key':key,'source':source,'sha256':sha(R/source),'collection':c['collection'],'selected_objects':mesh_names(R/glb),'matrix_world':np.asarray(pose).tolist(),'placement_status':reason,'scale':[1,1,1]}
    rows[key]=row;route_rows[key]={'key':key,'source_blend':source,'glb':glb,'selected_objects':row['selected_objects']}
    changes.append({'key':key,'asset':asset,'action':'replace' if replacement else 'add','scope':reason,'source_sha256':row['sha256'],'glb_sha256':sha(R/glb)})


for key,asset in [('mirror-left','mirror-left-v2'),('mirror-right','mirror-right-v3')]:
    attach(key,asset,parent(key),'Latest independently reviewed mirror revision; original whole-bike parent matrix retained.',True)
attach('throttle-visible-assembly','throttle',parent('handlebar'),'Original cockpit datum retained; no newly invented cable continuation.')
attach('exhaust-heatshield-fasteners','exhaust-heatshield-screw',parent('exhaust-heatshield'),'Two existing fasteners in their original common heatshield coordinates; head identity and hidden engagement remain unqualified.')
attach('instrument-support-visible','instrument-bracket-v2',matrix((-24.5,0,0))@matrix((0,0,180)), 'Bounded support pose inferred between existing cluster and steering carrier; no OEM mounting claim.')
rows['instrument-support-visible']['matrix_world'][0][3]=0
rows['instrument-support-visible']['matrix_world'][1][3]=-.2395
rows['instrument-support-visible']['matrix_world'][2][3]=.025
attach('steering-cap-visible','front-completion-p25-steering-cap-front12-v2-coordination-v1',parent('steering-upper')@matrix(translation=(0,0,.005)),'Common steering axis; exposed exterior and authored clearance only, hidden seat/thread not qualified.')
for side,x in [('left',-.075),('right',.075)]:
    attach('plate-captive-nut-'+side,'rear-plate-captive-nut-exterior-v1',parent('rear-plate-carrier-crossbar-v2')@matrix(translation=(x,0,-.0038)),'Existing square nut aligned with the crossbar nominal hole; bounded review clearance, no hidden thread or weld.')
for side,x,angle in [('left',.1092,90),('right',-.1092,-90)]:
    attach('rear-indicator-washer-'+side,'rear-indicator-mount-washer-v2',matrix((0,angle,0),(x,1.13,-.34)),'Existing exterior washer at the stalk root with authored display clearance; no stud/adapter invented.')
attach('centre-stand-operating-arm','centre-stand-operating-arm-v1-coordination-v1',parent('centre-stand-main-frame-v1'),'Shared related study frame, retracted stand pose; root weld and operating travel remain unqualified.')
attach('centre-stand-pivot-exterior','centre-stand-pivot-shaft-v1-coordination-v1',parent('centre-stand-main-frame-v1')@matrix((0,90,0),(-.045,.286,0)),'Transverse exterior shaft aligned with the existing pivot tube; authored axial placement, no cotter or fitted tolerance claimed.')
attach('side-stand-spring-anchor','side-stand-spring-anchor-pin-v1-coordination-v1',parent('side-stand-fork-stem-v1'),'Existing stem-local exterior anchor; no hidden weld or frame adaptation invented.')
attach('side-stand-return-spring','side-stand-return-spring-v1-coordination-v1',matrix(translation=(.06,.3585,-.764)),'Bounded retracted exterior spring pose adjacent to the existing anchor; preload and opposite frame anchorage unqualified.')
attach('side-stand-spring-sleeve','side-stand-spring-cover-v1-coordination-v1',matrix((-90,0,0),(.06,.337,-.764)),'Visible sleeve around the separately retained spring, authored coaxial pose; inner wall and far mouth remain review assumptions.')
fuel_pose=np.eye(4);fuel_pose[:3,:3]=np.array([[0,1,0],[0,0,1],[1,0,0]]);fuel_pose[:3,3]=[.133,.23,-.360]
body_source='assets-src/moto-components/fuel-tap-visible-body-v1/child-candidate.blend';body_glb='assets-src/moto-components/fuel-tap-visible-body-v1/child-candidate.glb'
rows['fuel-tap-visible-body']={'key':'fuel-tap-visible-body','source':body_source,'sha256':sha(R/body_source),'collection':'Scene Collection','selected_objects':mesh_names(R/body_glb),'matrix_world':fuel_pose.tolist(),'placement_status':'Related PF171800 photographic exterior only; bounded under-tank pose. Tank strainer and valve internals excluded.','scale':[1,1,1]}
route_rows['fuel-tap-visible-body']={'key':'fuel-tap-visible-body','source_blend':body_source,'glb':body_glb,'selected_objects':rows['fuel-tap-visible-body']['selected_objects']}
changes.append({'key':'fuel-tap-visible-body','action':'add','scope':rows['fuel-tap-visible-body']['placement_status'],'source_sha256':sha(R/body_source),'glb_sha256':sha(R/body_glb)})
attach('fuel-tap-visible-lever','fuel-valve-visible-lever-v1',fuel_pose,'The original lever study and new visible body use the same related Crosland photograph; all depths and mounting remain bounded estimates.')
blocked=[
    {'part':'M6 control-perch clamp bolt','reason':'Existing4.3mm perch bore conflicts with M6; not inserted, resized or hidden by an invented adapter.'},
    {'part':'Side-stand pivot bolt','reason':'Existing9mm eye conflicts with12mm shoulder; original fork and fastener preserved, no false inserted fit.'},
    {'part':'Handlebar lower fastener stack','reason':'Native ray probe finds the current stud axes intersect the steering plate. Hole/stud registration must be corrected from a coherent variant before adding nuts as fitted.'},
    {'part':'Complete final drive','reason':'Six-hole sprocket study is not qualified with the retained four-hole carrier; exact chain route and variant remain unresolved.'},
    {'part':'Complete visible cables and hose route','reason':'Only observed segments are retained; concealed junctions and endpoint identity are not fabricated.'},
]
plan={'schema':1,'base_native':'assets-src/moto-components/whole-exterior-material-preview-v9/whole-exterior-material-preview-v9.blend','base_native_sha256':sha(R/'assets-src/moto-components/whole-exterior-material-preview-v9/whole-exterior-material-preview-v9.blend'),'parents':list(rows.values()),'parent_count':len(rows),'changes':changes,'blocked_visible_interfaces':blocked,'whole_motorcycle_complete':False,'art_accepted':False,'scope':'Exterior visibility priority. Reuse exact components and expose all retained parts in the inspector; bounded layouts do not certify hidden mechanical interfaces.'}
(D/'parents.json').write_text(json.dumps(plan,indent=2)+'\n');(D/'routes.json').write_text(json.dumps({'rows':list(route_rows.values())},indent=2)+'\n')
print('PREPARED_EXTERIOR_PARENTS',len(rows),'CHANGES',len(changes))
