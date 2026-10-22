"""Independent small numeric audit. No Blender/render/source writes."""
from pathlib import Path
import itertools,json,math
D=Path(__file__).resolve().parent;p=json.loads((D/'orientation-audit.json').read_text());A=p['requested_linear_map_rows'];Q=p['external_convention_factorization']['Q_rows'];S=p['external_convention_factorization']['S_rows']
def mul(a,b):return[[sum(a[i][k]*b[k][j]for k in range(3))for j in range(3)]for i in range(3)]
def tr(a):return[list(x)for x in zip(*a)]
def det(a):return a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])
I=[[1,0,0],[0,1,0],[0,0,1]];checks=[]
def check(name,test):assert test,name;checks.append({'check':name,'pass':True})
check('A orthogonal, no stretch/shear',mul(tr(A),A)==I);check('A improper, no proper rotation solution',det(A)==-1);check('Q proper',det(Q)==1 and mul(tr(Q),Q)==I);check('S reflection in native depth only',S==[[1,0,0],[0,1,0],[0,0,-1]]);check('Q*S=A',mul(Q,S)==A)
rx=[[1,0,0],[0,0,-1],[0,1,0]];rz=[[0,-1,0],[1,0,0],[0,0,1]];check('Blender XYZ Euler90,0,90 equivalent to Rz90*Rx90',mul(rz,rx)==Q)
proper=[]
for perm in itertools.permutations(range(3)):
 for signs in itertools.product([-1,1],repeat=3):
  m=[[0]*3 for _ in range(3)]
  for j,k in enumerate(perm):m[k][j]=signs[j]
  if det(m)==1:proper.append(m)
check('all24 axis-aligned proper rotations reject required full map',len(proper)==24 and A not in proper)
check('nativeX to worldrear +Y',[r[0]for r in A]==[0,1,0]);check('nativeY to worldup +Z',[r[1]for r in A]==[0,0,1]);check('nativeZ to worldright -X',[r[2]for r in A]==[-1,0,0])
(D/'matrix-check.json').write_text(json.dumps({'checks':checks,'proper_rotations_enumerated':24,'scope':'Coordinate convention only; no assembled translation, physical-fit, culling implementation or render verified'},indent=2)+'\n');print(len(checks),'checks passed')
