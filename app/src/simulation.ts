import type {Controls, Mode, Obstacle, Point, WorldData} from './types';
import {circlePolygon,clamp,distance,pointSegment,sampleRoute,sweptMove} from './math';
import rush from '../../WEWA_Developpement_Web/config/rush.json';
import tuning from '../../WEWA_Developpement_Web/config/nitro_camera.json';
export const DT=1/60;
export class Simulation {
  mode:Mode='rush'; phase:'countdown'|'running'|'finished'='countdown'; paused=true;
  ticks=0;countdownTicks=0;finishCount=0;score=0;combo=1;delivered=0;collisions=0;
  cargo:string[]=[];collected=new Set<string>();gates=new Set<string>();depotContacts=new Set<string>();
  vehicle={x:0,z:0,yaw:0,speed:0,nitro:100,boosting:false,steer:0};
  accumulator=0;nitroRest=0;nitroCooldown=0;contactTime=1;storyStage=0;message='';messageTimer=0;
  checkpoint:Point; taxiStart=0;lastKnown:Point; obstacleProvider:(t:number)=>Obstacle[]=()=>[];
  private bounds:{minx:number;maxx:number;minz:number;maxz:number;rings:Point[][]}[];
  constructor(public world:WorldData){
    this.checkpoint=[...world.spawn];this.lastKnown=[...world.spawn];
    this.bounds=world.buildings.map(b=>({rings:b.rings,minx:Math.min(...b.rings[0].map(p=>p[0])),maxx:Math.max(...b.rings[0].map(p=>p[0])),minz:Math.min(...b.rings[0].map(p=>p[1])),maxz:Math.max(...b.rings[0].map(p=>p[1]))}));
    this.reset('rush');
  }
  get elapsed(){return this.ticks*DT;}
  get remaining(){return Math.max(0,rush.duration_active_seconds-this.elapsed);}
  reset(mode:Mode){
    this.mode=mode;this.phase='countdown';this.paused=false;this.ticks=0;this.countdownTicks=0;this.finishCount=0;
    this.score=0;this.combo=1;this.delivered=0;this.collisions=0;this.cargo=[];this.collected.clear();this.gates.clear();this.depotContacts.clear();
    this.accumulator=0;this.nitroRest=0;this.nitroCooldown=0;this.contactTime=1;this.storyStage=0;this.taxiStart=0;this.checkpoint=[...this.world.spawn];this.lastKnown=[...this.world.spawn];
    const start=sampleRoute(this.world.route,0);
    this.vehicle={...start,speed:0,nitro:100,boosting:false,steer:0};
    this.say(mode==='story'?'Mado : « Kito, apporte-moi ces colis. Je t’attends au relais. »':mode==='rush'?'30 secondes. Chaque passage compte.':mode==='delivery'?'Récupère six colis et livre-les aux relais.':'Prends ton temps. La ville est à toi.');
  }
  pause(value:boolean){this.paused=value;this.accumulator=0;this.vehicle.boosting=false;}
  say(text:string){this.message=text;this.messageTimer=6;}
  respawn(){
    const closest=this.world.route.map((p,i)=>({p,i,d:distance(p,this.checkpoint)})).sort((a,b)=>a.d-b.d)[0];
    const next=this.world.route[(closest.i+1)%this.world.route.length];
    Object.assign(this.vehicle,{x:this.checkpoint[0],z:this.checkpoint[1],yaw:Math.atan2(next[0]-closest.p[0],next[1]-closest.p[1]),speed:0,boosting:false});
    this.contactTime=1;this.say('De retour au dernier point de reprise.');
  }
  advance(delta:number,input:Controls){
    if(this.paused||this.phase==='finished')return;
    this.accumulator+=clamp(delta,0,.25);
    while(this.accumulator>=DT-1e-10){this.step(input);this.accumulator-=DT;if(this.finishCount>0){this.accumulator=0;break;}}
  }
  step(input:Controls){
    if(this.paused||this.phase==='finished')return;
    if(this.phase==='countdown'){
      this.countdownTicks++;
      if(this.countdownTicks>=rush.countdown_seconds*60){this.phase='running';this.vehicle.speed=this.mode==='rush'?6:0;}
      return;
    }
    this.ticks++;
    if(this.mode==='rush'&&this.ticks>=rush.duration_active_seconds*60){this.finish();return;}
    const v=this.vehicle;
    this.messageTimer=Math.max(0,this.messageTimer-DT);this.contactTime+=DT;this.nitroCooldown=Math.max(0,this.nitroCooldown-DT);
    const boost=input.nitro&&input.gas&&!input.brake&&v.speed>1&&v.nitro>0&&this.nitroCooldown===0;
    v.boosting=boost;
    if(boost){v.nitro=Math.max(0,v.nitro-tuning.boost.drain_per_second*DT);this.nitroRest=0;if(v.nitro===0)this.nitroCooldown=tuning.boost.reactivation_delay_seconds;}
    else{this.nitroRest+=DT;if(this.nitroRest>=tuning.boost.recharge_delay_seconds)v.nitro=Math.min(100,v.nitro+tuning.boost.recharge_per_second*DT);}
    const roadDistance=this.nearestRoad([v.x,v.z]).distance;
    const maxSpeed=(roadDistance<5?19.5:10.5)*(boost?tuning.boost.top_speed_multiplier:1);
    if(input.brake){v.speed=Math.max(-3.5,v.speed-12*DT);v.boosting=false;}
    else if(input.gas){v.speed=Math.min(maxSpeed,v.speed+6.2*(boost?tuning.boost.acceleration_multiplier:1)*DT);}
    else v.speed=Math.abs(v.speed)<.08?0:v.speed-Math.sign(v.speed)*(1.4+Math.abs(v.speed)*.025)*DT;
    if(v.speed>maxSpeed)v.speed=Math.max(maxSpeed,v.speed-4*DT);
    const target=(input.right?1:0)-(input.left?1:0);v.steer+=(target-v.steer)*.14;
    v.yaw+=v.steer*1.65*clamp(Math.abs(v.speed)/4,0,1)*clamp(1-Math.abs(v.speed)/70,.45,1)*DT*Math.sign(v.speed||1);
    const obstacles=this.obstacleProvider(this.elapsed);
    const nearby=this.bounds.filter(b=>v.x>b.minx-3&&v.x<b.maxx+3&&v.z>b.minz-3&&v.z<b.maxz+3);
    const blocked=(p:Point)=>Math.abs(p[0])>890||p[1]<-880||p[1]>770||nearby.some(b=>circlePolygon(p,.42,b.rings))||obstacles.some(o=>{const dx=Math.sin(o.yaw||0)*(o.halfLength||0),dz=Math.cos(o.yaw||0)*(o.halfLength||0);return pointSegment(p,[o.x-dx,o.z-dz],[o.x+dx,o.z+dz]).distance<o.radius+.42;});
    const movement=sweptMove([v.x,v.z],[v.x+Math.sin(v.yaw)*v.speed*DT,v.z+Math.cos(v.yaw)*v.speed*DT],blocked);
    v.x=movement.point[0];v.z=movement.point[1];
    if(movement.hit){
      if(this.contactTime>.2){this.collisions++;this.combo=1;if(Math.abs(v.speed)>3)this.say('Doucement ! Trouve ton passage.');}
      this.contactTime=0;v.speed*=.45;v.boosting=false;this.nitroRest=0;
    }
    this.scoreZones();
    if(this.mode==='story'&&this.storyStage===1){
      const taxi=this.taxi();const separation=Math.hypot(v.x-taxi.x,v.z-taxi.z);
      if(separation<100)this.lastKnown=[taxi.x,taxi.z];
      if(separation>160&&this.messageTimer===0)this.say('Taxi perdu de vue. Rejoins la dernière position indiquée.');
      if(taxi.stopped&&separation<10&&Math.abs(v.speed)<4){this.storyStage=2;this.say('Mado a laissé un bracelet. « On va bien. Suis la piste vers le port. »');this.finish();}
    }
  }
  scoreZones(){
    if(this.phase!=='running')return;
    const p:Point=[this.vehicle.x,this.vehicle.z];
    for(const parcel of this.world.parcels){
      if(this.mode==='free')break;
      if(this.mode==='story'&&this.storyStage>0)break;
      if(!this.collected.has(parcel.id)&&this.cargo.length<rush.cargo_capacity&&distance(p,parcel.point)<3){this.collected.add(parcel.id);this.cargo.push(parcel.id);this.say(this.cargo.length===3?'Trois colis. Direction le relais !':`Colis récupéré · ${this.cargo.length}/3`);}
    }
    for(const depot of this.world.depots){
      const entered=distance(p,depot.point)<4.6;
      if(!entered){this.depotContacts.delete(depot.id);continue;}
      if(this.cargo.length&&Math.abs(this.vehicle.speed)*3.6<=rush.delivery_max_speed_kmh&&!this.depotContacts.has(depot.id)){
        const count=this.cargo.length;this.cargo=[];this.score+=Math.round(count*rush.points_per_delivered_parcel*this.combo);this.delivered+=count;this.combo=Math.min(rush.combo_cap,this.combo+rush.combo_step_per_clean_deposit);
        this.depotContacts.add(depot.id);this.checkpoint=[...depot.point];this.say(`${count} colis livrés. Bien joué, Wewa !`);
        if(this.mode==='delivery'&&this.delivered>=6)this.finish();
        if(this.mode==='story'&&this.storyStage===0){this.storyStage=1;this.taxiStart=this.elapsed;this.say('Mado : « Kito ? On a changé de taxi… Jaune, bande noire. Je te laisse une piste… »');}
      }
    }
    if(this.mode==='rush')for(let i=0;i<2;i++){
      const key=`gate-${i}`,gate=this.world.parcels[i+3];
      if(gate&&!this.gates.has(key)&&distance(p,gate.point)<3){this.gates.add(key);this.score+=rush.technical_gate_points;}
    }
  }
  taxi(){const distanceTravelled=Math.min(450,Math.max(0,this.elapsed-this.taxiStart)*7.2);return {...sampleRoute(this.world.route,235+distanceTravelled,-1),stopped:distanceTravelled>=450};}
  finish(){if(this.phase==='finished')return;this.phase='finished';this.finishCount++;this.vehicle.boosting=false;this.vehicle.speed=0;}
  nearestRoad(p:Point){
    let best={name:'Gombe',distance:Infinity,point:p};
    for(const segment of this.world.segments){const result=pointSegment(p,this.world.nodes[segment.a],this.world.nodes[segment.b]);if(result.distance<best.distance)best={name:segment.name,distance:result.distance,point:result.point};}return best;
  }
}
