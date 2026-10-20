import {SpatialIndex} from './spatial';
import {distance,pointSegment,circlePolygon} from '../math';
import type {Point,WorldData} from '../types';
export interface Lane {id:number;source_id:string;from:number;to:number;length:number;width:number;name:string;yaw:number;offset:number}
export class RoadNetwork {
  lanes:Lane[]=[];outgoing=new Map<number,Lane[]>();
  private segments;private index;private buildings;
  constructor(public world:WorldData){
    this.buildings=new SpatialIndex(world.buildings.map(b=>({...b,minx:Math.min(...b.rings[0].map(p=>p[0])),maxx:Math.max(...b.rings[0].map(p=>p[0])),minz:Math.min(...b.rings[0].map(p=>p[1])),maxz:Math.max(...b.rings[0].map(p=>p[1]))})));
    this.segments=world.segments.map(s=>{const a=world.nodes[s.a],b=world.nodes[s.b];return {...s,minx:Math.min(a[0],b[0]),maxx:Math.max(a[0],b[0]),minz:Math.min(a[1],b[1]),maxz:Math.max(a[1],b[1])};});this.index=new SpatialIndex(this.segments);
    for(const s of world.segments){const oneway=String(s.oneway||'').toLowerCase(),forward=oneway!=='-1'&&oneway!=='reverse',backward=!['yes','true','1'].includes(oneway);if(forward)this.add(s.a,s.b,s);if(backward)this.add(s.b,s.a,s);}
  }
  private add(from:number,to:number,s:WorldData['segments'][number]){const a=this.world.nodes[from],b=this.world.nodes[to],length=distance(a,b);if(length<.05)return;const lane={id:this.lanes.length,source_id:s.source_id,from,to,length,width:s.width,name:s.name,yaw:Math.atan2(b[0]-a[0],b[1]-a[1]),offset:Math.max(.35,Math.min(s.width/4,2.3))};for(let d=0;d<=length;d+=Math.min(3,length)){const p=this.point(lane,d);if(this.buildings.query({minx:p.x-1,maxx:p.x+1,minz:p.z-1,maxz:p.z+1}).some(b=>circlePolygon([p.x,p.z],.92,b.rings)))return;}this.lanes.push(lane);const out=this.outgoing.get(from)||[];out.push(lane);this.outgoing.set(from,out);}
  point(lane:Lane,along:number){const a=this.world.nodes[lane.from],b=this.world.nodes[lane.to],t=Math.max(0,Math.min(1,along/lane.length)),offset=lane.offset;return {x:a[0]+(b[0]-a[0])*t-Math.cos(lane.yaw)*offset,z:a[1]+(b[1]-a[1])*t+Math.sin(lane.yaw)*offset,yaw:lane.yaw};}
  nearest(p:Point){let nearby=this.index.query({minx:p[0]-35,maxx:p[0]+35,minz:p[1]-35,maxz:p[1]+35});if(!nearby.length)nearby=this.segments;let best={name:'Gombe',distance:Infinity,point:p,width:6,source_id:''};for(const s of nearby){const r=pointSegment(p,this.world.nodes[s.a],this.world.nodes[s.b]);if(r.distance<best.distance)best={...r,name:s.name,width:s.width,source_id:s.source_id};}return best;}
  path(from:number,to:number,excluded=new Set<number>()){
    const costs=new Map<number,number>([[from,0]]),previous=new Map<number,Lane>(),open=new Set([from]);
    while(open.size){const u=[...open].reduce((a,b)=>(costs.get(a)??Infinity)<(costs.get(b)??Infinity)?a:b);open.delete(u);if(u===to)break;for(const e of this.outgoing.get(u)||[]){if(excluded.has(e.id))continue;const cost=costs.get(u)!+e.length;if(cost<(costs.get(e.to)??Infinity)){costs.set(e.to,cost);previous.set(e.to,e);open.add(e.to);}}}
    if(!previous.has(to))return [];const path:Lane[]=[];for(let p=to;p!==from;){const edge=previous.get(p);if(!edge)return [];path.unshift(edge);p=edge.from;}return path;
  }
}
