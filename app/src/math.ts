import type { Point } from './types';
export const clamp = (n:number,a:number,b:number) => Math.max(a,Math.min(b,n));
export const distance = (a:Point,b:Point) => Math.hypot(a[0]-b[0],a[1]-b[1]);
export function pointSegment(p:Point,a:Point,b:Point):{point:Point;distance:number;t:number} {
  const dx=b[0]-a[0],dz=b[1]-a[1],den=dx*dx+dz*dz;
  const t=den?clamp(((p[0]-a[0])*dx+(p[1]-a[1])*dz)/den,0,1):0;
  const point:Point=[a[0]+dx*t,a[1]+dz*t]; return {point,distance:distance(p,point),t};
}
export function insideRing(p:Point,ring:Point[]):boolean {
  let inside=false;
  for(let i=0,j=ring.length-1;i<ring.length;j=i++){
    const a=ring[i],b=ring[j];
    if((a[1]>p[1])!==(b[1]>p[1]) && p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]) inside=!inside;
  } return inside;
}
export function circlePolygon(p:Point,radius:number,rings:Point[][]):boolean {
  if(insideRing(p,rings[0])&&!rings.slice(1).some(r=>insideRing(p,r))) return true;
  return rings.some(r=>r.some((a,i)=>pointSegment(p,a,r[(i+1)%r.length]).distance<radius));
}
export function sampleRoute(route:Point[],s:number,offset=0):{x:number;z:number;yaw:number} {
  const lengths=route.slice(1).map((p,i)=>distance(p,route[i]));
  const total=lengths.reduce((a,b)=>a+b,0);s=((s%total)+total)%total;
  for(let i=0;i<lengths.length;i++){
    const length=lengths[i];if(s<=length){const a=route[i],b=route[i+1],t=length?s/length:0;
      const dx=(b[0]-a[0])/length,dz=(b[1]-a[1])/length;
      return {x:a[0]+(b[0]-a[0])*t+dz*offset,z:a[1]+(b[1]-a[1])*t-dx*offset,yaw:Math.atan2(dx,dz)};
    }s-=length;
  }return {x:route[0][0],z:route[0][1],yaw:0};
}
export function sweptMove(start:Point,end:Point,blocked:(point:Point)=>boolean):{point:Point;hit:boolean} {
  // At most 15 cm between samples, including during boosted movement.
  const steps=Math.max(1,Math.ceil(distance(start,end)/.15));let point=start;
  for(let i=1;i<=steps;i++){
    const next:Point=[start[0]+(end[0]-start[0])*i/steps,start[1]+(end[1]-start[1])*i/steps];
    if(blocked(next))return {point,hit:true};point=next;
  }return {point,hit:false};
}
