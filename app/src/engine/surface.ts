import type {WorldData} from '../types';
export interface SurfacePatch {id:string;x:number;z:number;radius:number;height:number;kind:'ramp'|'pothole';provenance:string}
/** Authored game surfaces are separate from immutable surveyed/source geometry. */
export class SurfaceField {
  constructor(private patches:SurfacePatch[]=[]){}
  height(x:number,z:number){let y=0;for(const p of this.patches){const r=Math.hypot(x-p.x,z-p.z)/p.radius;if(r<1)y+=p.height*.5*(1+Math.cos(r*Math.PI));}return y;}
  suspension(x:number,z:number,yaw:number,wheelbase=1.285){const dx=Math.sin(yaw)*wheelbase/2,dz=Math.cos(yaw)*wheelbase/2,front=this.height(x+dx,z+dz),rear=this.height(x-dx,z-dz);return {y:(front+rear)/2,pitch:Math.atan2(rear-front,wheelbase),front,rear};}
  static forWorld(world:WorldData){return new SurfaceField(world.surfacePatches||[]);}
}
