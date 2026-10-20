import {RoadNetwork,type Lane} from './roads';
import {clamp,distance,sampleRoute,pointSegment} from '../math';
import type {Obstacle,WorldData} from '../types';
export interface TrafficVehicle {id:number;kind:'minibus'|'taxi';lane:number;along:number;speed:number;x:number;z:number;yaw:number;wait:number;entryX?:number;entryZ?:number}
export interface Walker {id:number;x:number;z:number;yaw:number;crossing:boolean;moving:boolean;phase:number}
export interface TrafficSnapshot {tick:number;random:number;vehicles:TrafficVehicle[]}
export class TrafficSystem {
  vehicles:TrafficVehicle[]=[];walkers:Walker[]=[];tick=0;private random:number;private seed:number;private count:number;
  constructor(public network:RoadNetwork,options={count:0,seed:31020}){this.seed=options.seed;this.count=options.count;this.random=this.seed;this.reset();}
  private rng(){this.random=(Math.imul(this.random,1664525)+1013904223)>>>0;return this.random/4294967296;}
  reset(){this.tick=0;this.random=this.seed;this.vehicles=[];const world=this.network.world;
    for(let i=0;i<this.count;i++){const target=sampleRoute(world.route,45+i*155);const candidates=this.network.lanes.filter(e=>e.width>=5&&e.length>=8).map(e=>({e,d:distance([target.x,target.z],this.network.world.nodes[e.from])})).sort((a,b)=>a.d-b.d);for(const {e}of candidates){const t=pointSegment([target.x,target.z],world.nodes[e.from],world.nodes[e.to]).t,along=Math.max(3,Math.min(e.length-3,e.length*t)),p=this.network.point(e,along);if(distance([p.x,p.z],world.spawn)<24||this.vehicles.some(v=>Math.hypot(v.x-p.x,v.z-p.z)<12))continue;this.vehicles.push({id:i,kind:i%3===0?'minibus':'taxi',lane:e.id,along,speed:0,...p,wait:0});break;}}
    this.updateWalkers();
  }
  private updateWalkers(){this.walkers=[];if(!this.count)return;const t=this.tick/60;for(let i=0;i<12;i++){const crossing=i<4,phase=(t-i*.14+36)%36,offset=!crossing?8.2:phase<5?-8.5:phase<9?-8.5+(phase-5)/4*17:phase<22?8.5:phase<26?8.5-(phase-22)/4*17:-8.5,p=sampleRoute(this.network.world.route,(crossing?290+i*.75:70)+Math.floor(i/4)*200,offset);this.walkers.push({id:i,...p,yaw:p.yaw+(phase<20?-Math.PI/2:Math.PI/2),crossing,moving:crossing&&(phase>=5&&phase<9||phase>=22&&phase<26),phase:t*5+i});}}
  private next(lane:Lane){let candidates=(this.network.outgoing.get(lane.to)||[]).filter(e=>e.to!==lane.from&&e.width>=4.5);if(!candidates.length)candidates=(this.network.outgoing.get(lane.to)||[]).filter(e=>e.width>=4.5);if(!candidates.length)return null;const straight=candidates.filter(e=>Math.cos(e.yaw-lane.yaw)>.65),pool=straight.length&&this.rng()<.8?straight:candidates;return pool[Math.floor(this.rng()*pool.length)];}
  step(dt:number,player:{x:number;z:number;speed:number}){this.tick++;this.updateWalkers();const reservations=new Map<number,number>();
    // Clear an occupied junction before granting it to an approaching vehicle.
    for(const v of this.vehicles){const lane=this.network.lanes[v.lane];if(v.along<6&&!reservations.has(lane.from))reservations.set(lane.from,v.id);}
    for(const v of [...this.vehicles].sort((a,b)=>b.wait-a.wait||a.id-b.id)){const lane=this.network.lanes[v.lane];if(lane.length-v.along<14&&!reservations.has(lane.to))reservations.set(lane.to,v.id);}
    const before=this.vehicles.map(v=>({...v}));
    for(const v of this.vehicles){let lane=this.network.lanes[v.lane],target=lane.width>=9?8.2:5.8;const remaining=lane.length-v.along;
      if(remaining<12&&(this.network.outgoing.get(lane.to)?.length||0)>2){target=Math.min(target,3.5);if(reservations.get(lane.to)!==v.id)target=remaining>4?Math.min(target,(remaining-4)*.7):0;}
      for(const other of before){if(other.id===v.id)continue;const dx=other.x-v.x,dz=other.z-v.z,along=dx*Math.sin(v.yaw)+dz*Math.cos(v.yaw),across=Math.abs(dx*Math.cos(v.yaw)-dz*Math.sin(v.yaw));if(along>0&&along<18&&across<2.1)target=Math.min(target,Math.max(0,(along-6)/1.8));}
      const dx=player.x-v.x,dz=player.z-v.z,ahead=dx*Math.sin(v.yaw)+dz*Math.cos(v.yaw),side=Math.abs(dx*Math.cos(v.yaw)-dz*Math.sin(v.yaw));if(ahead>0&&ahead<16&&side<1.7)target=Math.min(target,Math.max(0,(ahead-5)/1.6));
      for(const w of this.walkers){if(!w.crossing)continue;const dx=w.x-v.x,dz=w.z-v.z,a=dx*Math.sin(v.yaw)+dz*Math.cos(v.yaw),c=Math.abs(dx*Math.cos(v.yaw)-dz*Math.sin(v.yaw));if(a>0&&a<17&&c<2.7)target=Math.min(target,Math.max(0,(a-4)/1.4));}
      v.speed+=clamp(target-v.speed,-5.5*dt,1.8*dt);v.along+=v.speed*dt;v.wait=v.speed<.2?v.wait+dt:0;
      let guard=0;while(v.along>=lane.length&&guard++<8){const next=this.next(lane);if(!next){v.along=lane.length-.05;v.speed=0;break;}const exit=this.network.point(lane,lane.length);v.entryX=exit.x;v.entryZ=exit.z;v.along-=lane.length;lane=next;v.lane=lane.id;}
      const p=this.network.point(lane,v.along),blend=Math.min(1,v.along/5);v.x=v.entryX===undefined?p.x:v.entryX+(p.x-v.entryX)*blend;v.z=v.entryZ===undefined?p.z:v.entryZ+(p.z-v.entryZ)*blend;if(blend===1){delete v.entryX;delete v.entryZ;}let turn=p.yaw-v.yaw;turn=Math.atan2(Math.sin(turn),Math.cos(turn));v.yaw+=turn*Math.min(1,dt*9);
    }
  }
  obstacles():Obstacle[]{return [...this.vehicles.map(v=>({x:v.x,z:v.z,yaw:v.yaw,radius:v.kind==='minibus'?.9:.8,halfLength:v.kind==='minibus'?1.55:1.15,kind:'vehicle' as const})),...this.walkers.filter(w=>w.crossing).map(w=>({x:w.x,z:w.z,radius:.36,kind:'person' as const}))];}
  snapshot():TrafficSnapshot{return {tick:this.tick,random:this.random,vehicles:this.vehicles.map(v=>({...v}))};}
  restore(s:TrafficSnapshot){this.tick=s.tick;this.random=s.random;this.vehicles=s.vehicles.map(v=>({...v}));this.updateWalkers();}
}
