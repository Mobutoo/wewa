import {describe,it,expect} from 'vitest';
import {Simulation} from './simulation';
import {emptyControls,type WorldData} from './types';
import {circlePolygon,sweptMove} from './math';
const fixture=():WorldData=>({version:1,source:'test fixture',axes:'XZ',origin:[0,0],nodes:[[0,0],[0,100]],segments:[{a:0,b:1,name:'Test',width:10,source_id:'test',oneway:null}],buildings:[],route:[[0,0],[0,100],[100,100],[100,0],[0,0]],route_length:400,spawn:[0,0],parcels:[],depots:[],cells:[]});
function run(sim:Simulation,seconds:number,fps:number,input=emptyControls()){for(let i=0;i<seconds*fps;i++)sim.advance(1/fps,input);}
describe('Rush rules',()=>{
  it('ends once at exactly 30 active seconds at 30 and 60 fps, and rejects late scoring',()=>{
    for(const fps of [30,60]){const sim=new Simulation(fixture());run(sim,33,fps);expect(sim.elapsed).toBe(30);expect(sim.finishCount).toBe(1);expect(sim.phase).toBe('finished');run(sim,3,fps);sim.cargo=['late'];sim.world.depots=[{id:'d',point:[0,0],label:'late'}];sim.scoreZones();expect(sim.score).toBe(0);expect(sim.finishCount).toBe(1);}
  });
  it('pauses countdown, active timer and nitro without catch-up',()=>{
    const sim=new Simulation(fixture());sim.pause(true);run(sim,8,60);expect(sim.countdownTicks).toBe(0);sim.pause(false);run(sim,4,60);sim.pause(true);const time=sim.elapsed;run(sim,8,60);expect(sim.elapsed).toBe(time);sim.pause(false);sim.advance(1/60,emptyControls());expect(sim.elapsed-time).toBeCloseTo(1/60);
  });
  it('scores a grouped deposit atomically with one combo increment, without duplicates',()=>{
    const w=fixture();w.depots=[{id:'depot',point:[0,0],label:'Relais'}];const sim=new Simulation(w);sim.phase='running';sim.cargo=['a','b','c'];sim.scoreZones();expect(sim.score).toBe(300);expect(sim.combo).toBe(1.25);expect(sim.delivered).toBe(3);sim.scoreZones();expect(sim.score).toBe(300);expect(sim.cargo).toEqual([]);
  });
  it('does not award the same parcel twice after passing its location again',()=>{
    const w=fixture();w.parcels=[{id:'once',point:[0,0]}];const sim=new Simulation(w);sim.phase='running';sim.scoreZones();expect(sim.cargo).toEqual(['once']);sim.cargo=[];sim.vehicle.z=10;sim.scoreZones();sim.vehicle.z=0;sim.scoreZones();expect(sim.cargo).toEqual([]);
  });
  it('reset restores the full independent state of a new run',()=>{
    const sim=new Simulation(fixture());sim.score=900;sim.combo=3;sim.collected.add('x');sim.cargo=['x'];sim.ticks=900;sim.vehicle.nitro=2;sim.storyStage=1;sim.reset('rush');expect(sim.score).toBe(0);expect(sim.combo).toBe(1);expect(sim.vehicle.nitro).toBe(100);expect(sim.elapsed).toBe(0);expect(sim.collected.size).toBe(0);expect(sim.cargo.length).toBe(0);expect(sim.storyStage).toBe(0);
  });
});
describe('Delivery and narrative checkpoints',()=>{
  it('delivery can finish with six distinct parcels at two relays',()=>{
    const w=fixture();w.parcels=Array.from({length:6},(_,i)=>({id:`p${i}`,point:[0,10+i*10]}));w.depots=[{id:'a',point:[0,45],label:'A'},{id:'b',point:[0,85],label:'B'}];
    const sim=new Simulation(w);sim.reset('delivery');sim.phase='running';
    for(let group=0;group<2;group++){
      for(let i=0;i<3;i++){sim.vehicle.z=w.parcels[group*3+i].point[1];sim.scoreZones();}
      sim.vehicle.z=w.depots[group].point[1];sim.scoreZones();
    }
    expect(sim.delivered).toBe(6);expect(sim.phase).toBe('finished');expect(sim.score).toBe(675);expect(sim.finishCount).toBe(1);
  });
  it('the story moves from a free delivery checkpoint to a recoverable taxi and a clue',()=>{
    const w=fixture();w.depots=[{id:'mado',point:[0,0],label:'Mado'}];const sim=new Simulation(w);sim.reset('story');sim.phase='running';sim.cargo=['intro'];sim.scoreZones();expect(sim.storyStage).toBe(1);expect(sim.checkpoint).toEqual([0,0]);
    sim.vehicle.x=300;sim.vehicle.z=300;sim.ticks=100;sim.messageTimer=0;sim.step(emptyControls());expect(sim.phase).toBe('running');expect(sim.storyStage).toBe(1);
    sim.ticks=4000;const taxi=sim.taxi();expect(taxi.stopped).toBe(true);sim.vehicle.x=taxi.x;sim.vehicle.z=taxi.z;sim.vehicle.speed=0;sim.step(emptyControls());expect(sim.storyStage).toBe(2);expect(sim.phase).toBe('finished');expect(sim.finishCount).toBe(1);
  });
});
describe('Vehicle safety and nitro',()=>{
  it('gives the same movement and charge at 30 and 60 fps',()=>{
    const simulations=[30,60].map(fps=>{const sim=new Simulation(fixture());sim.reset('free');run(sim,3,fps);sim.vehicle.speed=6;run(sim,2,fps,{...emptyControls(),gas:true,nitro:true});return sim;});expect(simulations[0].vehicle.z).toBeCloseTo(simulations[1].vehicle.z,8);expect(simulations[0].vehicle.nitro).toBeCloseTo(simulations[1].vehicle.nitro,8);
  });
  it('requires forward motion and cancels boost immediately on brake and pause',()=>{
    const sim=new Simulation(fixture());sim.phase='running';sim.step({...emptyControls(),gas:true,nitro:true});expect(sim.vehicle.boosting).toBe(false);sim.vehicle.speed=8;sim.step({...emptyControls(),gas:true,nitro:true});expect(sim.vehicle.boosting).toBe(true);sim.step({...emptyControls(),gas:true,brake:true,nitro:true});expect(sim.vehicle.boosting).toBe(false);sim.pause(true);expect(sim.vehicle.boosting).toBe(false);
  });
  it('stops a boosted vehicle at a thin wall without tunneling or repeated contact incidents',()=>{
    const w=fixture();w.buildings=[{id:'wall',rings:[[[1,-20],[1.02,-20],[1.02,20],[1,20],[1,-20]]],height:3,estimate:'fixture'}];const sim=new Simulation(w);sim.reset('free');sim.phase='running';sim.vehicle.speed=24;sim.vehicle.yaw=Math.PI/2;run(sim,2,60,{...emptyControls(),gas:true,nitro:true});expect(sim.vehicle.x).toBeLessThan(.6);expect(sim.collisions).toBe(1);expect(sim.combo).toBe(1);
  });
  it('preserves courtyards as free space and stops at their perimeter',()=>{
    const rings:[number,number][][]=[[[0,0],[10,0],[10,10],[0,10],[0,0]],[[3,3],[7,3],[7,7],[3,7],[3,3]]];expect(circlePolygon([5,5],.4,rings)).toBe(false);expect(circlePolygon([1,1],.4,rings)).toBe(true);const movement=sweptMove([5,5],[12,5],p=>circlePolygon(p,.4,rings));expect(movement.hit).toBe(true);expect(movement.point[0]).toBeLessThan(7);
  });
});

describe('One-thumb analog driving',()=>{
  it('accelerates and turns simultaneously with analog axes',()=>{
    const sim=new Simulation(fixture());sim.reset('free');sim.phase='running';run(sim,1,60,{...emptyControls(),throttle:.7,steering:.6});expect(sim.vehicle.speed).toBeGreaterThan(3);expect(sim.vehicle.yaw).toBeLessThan(-.2);
  });
  it('pulling down brakes before reversing, release coasts and nitro requires forward throttle',()=>{
    const sim=new Simulation(fixture());sim.reset('free');sim.phase='running';sim.vehicle.speed=6;const down={...emptyControls(),throttle:-1,steering:0,nitro:true};run(sim,.25,60,down);expect(sim.vehicle.speed).toBeGreaterThan(0);expect(sim.vehicle.speed).toBeLessThan(6);expect(sim.vehicle.boosting).toBe(false);run(sim,1,60,down);expect(sim.vehicle.speed).toBeLessThan(0);expect(sim.vehicle.speed).toBeGreaterThanOrEqual(-3.5);const reverse=sim.vehicle.speed;run(sim,.25,60);expect(sim.vehicle.speed).toBeGreaterThan(reverse);
  });
});
