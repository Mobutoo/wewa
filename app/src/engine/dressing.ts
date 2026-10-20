import {SceneLoader} from '@babylonjs/core/Loading/sceneLoader';
import {Mesh} from '@babylonjs/core/Meshes/mesh';
import {Matrix,Quaternion,Vector3} from '@babylonjs/core/Maths/math.vector';
import '@babylonjs/core/Meshes/thinInstanceMesh';
import type {Material} from '@babylonjs/core/Materials/material';
import type {Scene} from '@babylonjs/core/scene';
import type {ShadowGenerator} from '@babylonjs/core/Lights/Shadows/shadowGenerator';
import type {Point} from '../types';
export interface Placement {asset:string;x:number;y:number;z:number;yaw:number;source_id?:string;provenance:string}
export interface StreetDressing {version:number;corridor_length_m:number;library:string;facades:Placement[];props:Placement[];colliders:{id:string;rings:Point[][];reason:string}[]}
export class StreetKitInstances {
 stats={instances:0,parts:0,triangles:0,lod0:0,lod1:0};private lastX=Infinity;private lastZ=Infinity;
 constructor(private parts:{mesh:Mesh;placements:Placement[];lod:0|1;facade:boolean}[],private staticMeshes:Mesh[]=[]){}
 update(x:number,z:number){if(Math.hypot(x-this.lastX,z-this.lastZ)<3)return;this.lastX=x;this.lastZ=z;Object.assign(this.stats,{instances:0,parts:0,triangles:0,lod0:0,lod1:0});
  for(const mesh of this.staticMeshes){const b=mesh.getBoundingInfo().boundingBox,dx=Math.max(b.minimumWorld.x-x,0,x-b.maximumWorld.x),dz=Math.max(b.minimumWorld.z-z,0,z-b.maximumWorld.z),active=Math.hypot(dx,dz)<160;mesh.setEnabled(active);if(active){this.stats.parts++;this.stats.instances++;this.stats.triangles+=mesh.getTotalIndices()/3;}}
  for(const {mesh,placements,lod,facade}of this.parts){const visible=placements.filter(p=>{const d=Math.hypot(p.x-x,p.z-z,p.y-1.5);return facade?(lod===0?d<45&&p.y<6:(d>=45||p.y>=6)&&d<200):d<160;});mesh.setEnabled(visible.length>0);if(!visible.length)continue;const matrices=new Float32Array(visible.length*16);visible.forEach((p,i)=>Matrix.Compose(Vector3.One(),Quaternion.RotationYawPitchRoll(p.yaw,0,0),new Vector3(p.x,p.y,p.z)).copyToArray(matrices,i*16));mesh.thinInstanceSetBuffer('matrix',matrices,16,true);mesh.thinInstanceRefreshBoundingInfo(true);this.stats.instances+=visible.length;this.stats.parts++;this.stats.triangles+=mesh.getTotalIndices()/3*visible.length;this.stats[lod===0?'lod0':'lod1']+=visible.length;}
 }
}
export async function loadStreetDressing(scene:Scene,shadows:ShadowGenerator,dressing:StreetDressing|undefined,spawn:Point){
 const parts:ConstructorParameters<typeof StreetKitInstances>[0]=[],staticMeshes:Mesh[]=[],propGroups=new Map<Material,Mesh[]>();if(dressing){const container=await SceneLoader.LoadAssetContainerAsync('/models/street-kit/','street-kit.glb',scene);container.addAllToScene();const placements=new Map<string,Placement[]>();for(const p of [...dressing.facades,...dressing.props]){const list=placements.get(p.asset)||[];list.push(p);placements.set(p.asset,list);}
  for(const node of container.meshes){if(!(node instanceof Mesh)||!node.getTotalVertices())continue;const lod=node.name.startsWith('lod1_')?1:0,id=node.name.replace(/^lod1_/,'').split('__')[0],list=placements.get(id)||[];if(!list.length){node.setEnabled(false);continue;}node.receiveShadows=true;node.isPickable=false;
   if(!id.startsWith('facade_')&&node.material){for(const p of list){const copy=node.clone('prop-batch-source',null,true);copy.parent=null;copy.position.copyFromFloats(p.x,p.y,p.z);copy.rotationQuaternion=Quaternion.RotationYawPitchRoll(p.yaw,0,0);copy.setEnabled(true);copy.computeWorldMatrix(true);const group=propGroups.get(node.material)||[];group.push(copy);propGroups.set(node.material,group);}node.setEnabled(false);continue;}
   if(lod===0&&!matchMedia('(pointer:coarse)').matches)shadows.addShadowCaster(node);parts.push({mesh:node,placements:list,lod,facade:true});}}
 for(const [material,group]of propGroups){const merged=Mesh.MergeMeshes(group,true,true,undefined,false,false);if(merged){merged.name='street-props-'+material.name;merged.material=material;merged.receiveShadows=true;merged.isPickable=false;merged.freezeWorldMatrix();shadows.addShadowCaster(merged);staticMeshes.push(merged);}}
 const result=new StreetKitInstances(parts,staticMeshes);result.update(spawn[0],spawn[1]);return result;
}
