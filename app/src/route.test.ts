import {it,expect} from 'vitest';
import {Simulation} from './simulation';
import {distance,pointSegment,sampleRoute,clamp} from './math';
import {emptyControls,type WorldData} from './types';
import gombe from '../public/world/gombe.json';
const world=gombe as unknown as WorldData;
it('the actual Gombe route can be driven to a completed delivery with building collisions active',()=>{
  const sim=new Simulation(world);sim.reset('delivery');sim.phase='running';
  let lastProgress=0;
  for(let tick=0;tick<60*180&&sim.finishCount===0;tick++){
    const v=sim.vehicle,p:[number,number]=[v.x,v.z];let length=0,best=Infinity,progress=lastProgress;
    for(let i=0;i<world.route.length-1;i++){
      const a=world.route[i],b=world.route[i+1],len=distance(a,b),projection=pointSegment(p,a,b),s=length+projection.t*len;
      if(projection.distance<best&&s>=lastProgress-8&&s<lastProgress+50){best=projection.distance;progress=s;}
      length+=len;
    }
    lastProgress=Math.max(lastProgress,progress);
    const target=sampleRoute(world.route,progress+clamp(3+Math.abs(v.speed)*.25,3,7));
    let angle=Math.atan2(target.x-v.x,target.z-v.z)-v.yaw;angle=Math.atan2(Math.sin(angle),Math.cos(angle));
    let desired=Math.abs(angle)>.35?2.8:Math.abs(angle)>.12?5:14;
    const future=sampleRoute(world.route,progress+17);let upcoming=future.yaw-v.yaw;upcoming=Math.atan2(Math.sin(upcoming),Math.cos(upcoming));
    if(Math.abs(upcoming)>.35)desired=Math.min(desired,4);
    if(sim.cargo.length&&world.depots.some(d=>distance(p,d.point)<18))desired=Math.min(desired,2);
    sim.step({...emptyControls(),gas:v.speed<desired,brake:v.speed>desired+1,left:angle<-.035,right:angle>.035});
  }
  expect(sim.delivered,{progress:lastProgress,vehicle:sim.vehicle,collisions:sim.collisions,collected:[...sim.collected]} as unknown as string).toBeGreaterThanOrEqual(6);
  expect(sim.phase).toBe('finished');expect(sim.finishCount).toBe(1);
});
