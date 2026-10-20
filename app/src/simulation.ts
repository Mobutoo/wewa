import type {Controls, Mode, Obstacle, Point, WorldData} from './types';
import {circlePolygon,clamp,distance,pointSegment,sampleRoute,sweptMove} from './math';
import rush from '../../WEWA_Developpement_Web/config/rush.json';
import tuning from '../../WEWA_Developpement_Web/config/nitro_camera.json';
import {MissionDirector} from './engine/missions';
import {RoadNetwork} from './engine/roads';
import {SpatialIndex} from './engine/spatial';
import {TrafficSystem} from './engine/traffic';
import {SurfaceField} from './engine/surface';
import {RULES_VERSION,CHALLENGE_SEED} from './engine/profile';
import {validRun,worldKeyFor,type RunSnapshot} from './engine/checkpoint';
export const DT=1/60;
export class Simulation {
  readonly rules=RULES_VERSION;readonly seed=CHALLENGE_SEED;runId='';private runSequence=0;
  missions:MissionDirector;network:RoadNetwork;traffic:TrafficSystem;surface:SurfaceField;private collisionIndex;tokens=new Set<string>();
  previousPose={x:0,y:0,z:0,yaw:0,pitch:0};
  private compatibilityKey:string;get worldKey(){return this.compatibilityKey;}
  mode:Mode='rush'; phase:'countdown'|'running'|'finished'='countdown'; paused=true;
  ticks=0;crashTicks=0;countdownTicks=0;finishCount=0;score=0;combo=1;delivered=0;collisions=0;
  cargo:string[]=[];collected=new Set<string>();gates=new Set<string>();depotContacts=new Set<string>();
  vehicle={x:0,z:0,yaw:0,speed:0,nitro:100,boosting:false,steer:0,y:0,pitch:0};
  contactLatched=false;accumulator=0;nitroRest=0;nitroCooldown=0;contactTime=1;message='';messageTimer=0;
  checkpoint:Point; obstacleProvider:(t:number)=>Obstacle[]=()=>[];
  private bounds:{minx:number;maxx:number;minz:number;maxz:number;rings:Point[][]}[];
  constructor(public world:WorldData){
    this.compatibilityKey=worldKeyFor(world);this.missions=new MissionDirector(world);this.network=new RoadNetwork(world);this.traffic=new TrafficSystem(this.network,world.traffic);this.surface=SurfaceField.forWorld(world);
    this.checkpoint=[...world.spawn];this.lastKnown=[...world.spawn];
    this.bounds=[...world.buildings,...(world.dressing?.colliders||[])].map(b=>({rings:b.rings,minx:Math.min(...b.rings[0].map(p=>p[0])),maxx:Math.max(...b.rings[0].map(p=>p[0])),minz:Math.min(...b.rings[0].map(p=>p[1])),maxz:Math.max(...b.rings[0].map(p=>p[1]))}));
    this.collisionIndex=new SpatialIndex(this.bounds);
    this.reset('rush');
  }
  get storyStage(){return this.missions.stage;}set storyStage(value:number){this.missions.stage=value;}
  get taxiStart(){return this.missions.taxiStart;}set taxiStart(value:number){this.missions.taxiStart=value;}
  get taxiOrigin(){return this.missions.taxiOrigin;}set taxiOrigin(value:number){this.missions.taxiOrigin=value;}
  get lastKnown(){return this.missions.lastKnown;}set lastKnown(value:Point){this.missions.lastKnown=value;}
  get elapsed(){return this.ticks*DT;}
  get remaining(){return Math.max(0,rush.duration_active_seconds-this.elapsed);}
  reset(mode:Mode,runId=`local-${++this.runSequence}`){
    this.runId=runId;this.traffic.reset();this.missions.reset();this.tokens.clear();
    this.mode=mode;this.phase='countdown';this.paused=false;this.ticks=0;this.crashTicks=0;this.countdownTicks=0;this.finishCount=0;
    this.score=0;this.combo=1;this.delivered=0;this.collisions=0;this.cargo=[];this.collected.clear();this.gates.clear();this.depotContacts.clear();
    this.accumulator=0;this.contactLatched=false;this.nitroRest=0;this.nitroCooldown=0;this.contactTime=1;this.storyStage=0;this.taxiStart=0;this.checkpoint=[...this.world.spawn];this.lastKnown=[...this.world.spawn];
    const start=sampleRoute(this.world.route,0);
    this.vehicle={...start,speed:0,nitro:100,boosting:false,steer:0,y:0,pitch:0};
    this.previousPose={...this.vehicle};
    this.say(mode==='story'?'Mado : « Kito, apporte-moi les six colis. Je t’attends au relais. »':mode==='rush'?'30 secondes. Chaque passage compte.':mode==='delivery'?'Récupère six colis et livre-les aux relais.':'Prends ton temps. La ville est à toi.');
  }
  pause(value:boolean){this.paused=value;this.accumulator=0;this.vehicle.boosting=false;}
  say(text:string){this.message=text;this.messageTimer=6;}
  respawn(){
    const closest=this.world.route.map((p,i)=>({p,i,d:distance(p,this.checkpoint)})).sort((a,b)=>a.d-b.d)[0];
    const next=this.world.route[(closest.i+1)%this.world.route.length];
    Object.assign(this.vehicle,{x:this.checkpoint[0],z:this.checkpoint[1],yaw:Math.atan2(next[0]-closest.p[0],next[1]-closest.p[1]),speed:0,boosting:false});
    this.previousPose={...this.vehicle};this.crashTicks=0;this.contactTime=1;this.say('De retour au dernier point de reprise.');
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
    const v=this.vehicle;this.previousPose={...v};this.traffic.step(DT,v);
    this.messageTimer=Math.max(0,this.messageTimer-DT);this.contactTime+=DT;this.nitroCooldown=Math.max(0,this.nitroCooldown-DT);
    if(this.crashTicks>0){this.crashTicks--;this.contactTime=0;v.speed=0;v.boosting=false;this.nitroRest=0;return;}
    const throttle=clamp(input.throttle??(input.brake?-1:input.gas?1:0),-1,1);
    const boost=input.nitro&&throttle>0&&v.speed>1&&v.nitro>0&&this.nitroCooldown===0;
    v.boosting=boost;
    if(boost){v.nitro=Math.max(0,v.nitro-tuning.boost.drain_per_second*DT);this.nitroRest=0;if(v.nitro===0)this.nitroCooldown=tuning.boost.reactivation_delay_seconds;}
    else{this.nitroRest+=DT;if(this.nitroRest>=tuning.boost.recharge_delay_seconds)v.nitro=Math.min(100,v.nitro+tuning.boost.recharge_per_second*DT);}
    const road=this.nearestRoad([v.x,v.z]);
    const maxSpeed=(road.distance<road.width/2?19.5:10.5)*(boost?tuning.boost.top_speed_multiplier:1);
    if(throttle<0){v.speed=Math.max(-3.5,v.speed+12*throttle*DT);v.boosting=false;}
    else if(throttle>0){v.speed=Math.min(maxSpeed,v.speed+6.2*throttle*(boost?tuning.boost.acceleration_multiplier:1)*DT);}
    else v.speed=Math.abs(v.speed)<.08?0:v.speed-Math.sign(v.speed)*(1.4+Math.abs(v.speed)*.025)*DT;
    if(v.speed>maxSpeed)v.speed=Math.max(maxSpeed,v.speed-4*DT);
    const target=clamp(input.steering??((input.right?1:0)-(input.left?1:0)),-1,1);v.steer+=(target-v.steer)*.14;
    // Right-handed X-east/Z-south world: a rider turning right decreases heading yaw.
    v.yaw-=v.steer*1.65*clamp(Math.abs(v.speed)/4,0,1)*clamp(1-Math.abs(v.speed)/70,.45,1)*DT*Math.sign(v.speed||1);
    const obstacles=[...this.traffic.obstacles(),...this.obstacleProvider(this.elapsed)];if(this.mode==='story'&&this.storyStage===1){const t=this.taxi();obstacles.push({...t,radius:.8,halfLength:1.15,kind:'vehicle'});}
    const nearby=this.collisionIndex.query({minx:v.x-3,maxx:v.x+3,minz:v.z-3,maxz:v.z+3});
    const blockedAt=(p:Point,radius:number)=>Math.abs(p[0])+radius>890||p[1]-radius<-880||p[1]+radius>770||nearby.some(b=>circlePolygon(p,radius,b.rings))||obstacles.some(o=>{const dx=Math.sin(o.yaw||0)*(o.halfLength||0),dz=Math.cos(o.yaw||0)*(o.halfLength||0);return pointSegment(p,[o.x-dx,o.z-dz],[o.x+dx,o.z+dz]).distance<o.radius+radius;});
    const blocked=(p:Point)=>blockedAt(p,.42);
    if(this.contactLatched&&!blockedAt([v.x,v.z],.66))this.contactLatched=false;
    const movement=sweptMove([v.x,v.z],[v.x+Math.sin(v.yaw)*v.speed*DT,v.z+Math.cos(v.yaw)*v.speed*DT],blocked);
    v.x=movement.point[0];v.z=movement.point[1];
    if(movement.hit){
      if(!this.contactLatched&&Math.abs(v.speed)>9){this.crashTicks=72;this.say('Un accroc. La moto se redresse…');}
      if(!this.contactLatched){this.collisions++;this.combo=1;if(Math.abs(v.speed)>3)this.say('Doucement ! Trouve ton passage.');}
      this.contactLatched=true;this.contactTime=0;v.speed*=.45;v.boosting=false;this.nitroRest=0;
    }
    const suspension=this.surface.suspension(v.x,v.z,v.yaw);v.y+=(suspension.y-v.y)*.3;v.pitch+=(suspension.pitch-v.pitch)*.22;
    this.scoreZones();
    if(this.mode==='story'){const update=this.missions.update(v,this.elapsed);if(update.message)this.say(update.message);if(update.finished)this.finish();}
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
        const message=this.missions.deposit(this.mode,this.elapsed,this.delivered,this.checkpoint);if(message)this.say(message);
      }
    }
    for(const token of this.world.nitroTokens||[])if(this.vehicle.nitro<99.99&&!this.tokens.has(token.id)&&distance(p,token.point)<2.2){this.tokens.add(token.id);this.vehicle.nitro=Math.min(100,this.vehicle.nitro+tuning.boost.token_refill);this.say('Jeton nitro récupéré · +20');}
    if(this.mode==='rush')for(let i=0;i<2;i++){
      const key=`gate-${i}`,gate=this.world.parcels[i+3];
      if(gate&&!this.gates.has(key)&&distance(p,gate.point)<3){this.gates.add(key);this.score+=rush.technical_gate_points;}
    }
  }
  taxi(){return this.missions.taxi(this.elapsed);}
  finish(){if(this.phase==='finished')return;this.phase='finished';this.finishCount++;this.vehicle.boosting=false;this.vehicle.speed=0;}
  nearestRoad(p:Point){return this.network.nearest(p);}
  renderVehicle(){const alpha=clamp(this.accumulator/DT,0,1),v=this.vehicle,p=this.previousPose;if(this.phase!=='running')return {...v};const angle=Math.atan2(Math.sin(v.yaw-p.yaw),Math.cos(v.yaw-p.yaw));return {...v,x:p.x+(v.x-p.x)*alpha,z:p.z+(v.z-p.z)*alpha,y:p.y+(v.y-p.y)*alpha,pitch:p.pitch+(v.pitch-p.pitch)*alpha,yaw:p.yaw+angle*alpha};}
  snapshot():RunSnapshot|null{if(this.phase==='finished')return null;return {schema:1,rules:this.rules,worldKey:this.worldKey,runId:this.runId,seed:this.seed,mode:this.mode,phase:this.phase,ticks:this.ticks,crashTicks:this.crashTicks,contactLatched:this.contactLatched,countdownTicks:this.countdownTicks,score:this.score,combo:this.combo,delivered:this.delivered,collisions:this.collisions,vehicle:{...this.vehicle,boosting:false},cargo:[...this.cargo],collected:[...this.collected],gates:[...this.gates],depotContacts:[...this.depotContacts],checkpoint:[...this.checkpoint],storyStage:this.storyStage,taxiStart:this.taxiStart,taxiOrigin:this.taxiOrigin,lastKnown:[...this.lastKnown],nitroRest:this.nitroRest,nitroCooldown:this.nitroCooldown,traffic:this.traffic.snapshot(),tokens:[...this.tokens]};}
  restore(value:unknown){if(!validRun(value,this.worldKey))return false;const s=value;if(s.traffic.vehicles.some(v=>!this.network.lanes[v.lane]||v.along<0||v.along>this.network.lanes[v.lane].length||v.speed<0||v.speed>12))return false;if(s.cargo.some(id=>!this.world.parcels.some(p=>p.id===id)))return false;
    this.reset(s.mode,s.runId);for(const key of ['ticks','crashTicks','countdownTicks','score','combo','delivered','collisions','storyStage','taxiStart','taxiOrigin','nitroRest','nitroCooldown'] as const)this[key]=s[key];this.phase=s.phase;this.contactLatched=s.contactLatched;this.vehicle={...s.vehicle,boosting:false};this.cargo=[...s.cargo];this.collected=new Set(s.collected);this.gates=new Set(s.gates);this.depotContacts=new Set(s.depotContacts);this.tokens=new Set(s.tokens);this.checkpoint=[...s.checkpoint];this.lastKnown=[...s.lastKnown];this.traffic.restore(s.traffic);this.previousPose={...this.vehicle};this.accumulator=0;this.paused=false;this.say('Partie reprise. Ton chargement et ta piste ont été conservés.');return true;
  }
}
