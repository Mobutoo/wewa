import {writeFileSync} from 'node:fs';
import dressing from '../../public/world/dressing.json';
import {it,expect} from 'vitest';
import {Simulation} from '../simulation';
import {emptyControls,type WorldData} from '../types';
import {distance,pointSegment,sampleRoute,clamp} from '../math';
import gombe from '../../public/world/gombe.json';
it('drives the story from pickup through a recoverable taxi chase and clue with collisions active',()=>{
 const s=new Simulation(({...gombe,dressing}) as unknown as WorldData);s.reset('story','story-complete');s.phase='running';let progress=0;const stages=new Set<number>();let resumed=false;
 for(let tick=0;tick<60*540&&s.finishCount===0;tick++){
  stages.add(s.storyStage);const v=s.vehicle;let length=0,best=Infinity,nearest=progress;
  for(let i=0;i<s.world.route.length-1;i++){const a=s.world.route[i],b=s.world.route[i+1],len=distance(a,b),projection=pointSegment([v.x,v.z],a,b),raw=length+projection.t*len,d=raw+Math.floor(progress/s.world.route_length)*s.world.route_length+(raw<progress%s.world.route_length-s.world.route_length/2?s.world.route_length:0);if(projection.distance<best&&d>=progress-8&&d<progress+50){best=projection.distance;nearest=d;}length+=len;}
  progress=Math.max(progress,nearest);
  const target=sampleRoute(s.world.route,progress+clamp(3+Math.abs(v.speed)*.25,3,7));let angle=Math.atan2(target.x-v.x,target.z-v.z)-v.yaw;angle=Math.atan2(Math.sin(angle),Math.cos(angle));let desired=Math.abs(angle)>.35?2.8:Math.abs(angle)>.12?5:10;
  const ahead=sampleRoute(s.world.route,progress+17);let corner=ahead.yaw-v.yaw;corner=Math.atan2(Math.sin(corner),Math.cos(corner));if(Math.abs(corner)>.35)desired=Math.min(desired,4);
  if(s.cargo.length&&s.world.depots.some(d=>distance([v.x,v.z],d.point)<18))desired=Math.min(desired,2);
  if(s.storyStage===1){const taxi=s.taxi(),gap=Math.hypot(v.x-taxi.x,v.z-taxi.z);if(gap<18)desired=Math.min(desired,taxi.stopped?1.5:4.7);}
  s.step({...emptyControls(),gas:v.speed<desired,brake:v.speed>desired+.6,left:angle>.035,right:angle<-.035});
  if(s.storyStage===1&&!resumed&&s.elapsed>80){const checkpoint=s.snapshot();expect(s.restore(checkpoint)).toBe(true);resumed=true;}
 }
 expect(stages.has(0)).toBe(true);expect(stages.has(1)).toBe(true);expect(resumed).toBe(true);expect(s.storyStage,JSON.stringify({progress,elapsed:s.elapsed,position:s.vehicle,taxi:s.taxi(),collisions:s.collisions})).toBe(2);expect(s.phase).toBe('finished');expect(s.finishCount).toBe(1);expect(s.delivered).toBeGreaterThanOrEqual(6);expect(s.elapsed).toBeGreaterThan(240);writeFileSync(new URL('../../../WEWA_Developpement_Web/validation/engine-scenario.json',import.meta.url),JSON.stringify({rules:s.rules,seed:s.seed,world_key:s.worldKey,elapsed_seconds:s.elapsed,delivered:s.delivered,collisions:s.collisions,resumed,finish_count:s.finishCount,traffic_vehicles:s.traffic.vehicles.length,static_dressing_colliders:s.world.dressing?.colliders.length,qualification:'Automated fixed-step full-route integration, not human or physical iPhone testing'},null,2)+'\n');console.info('Story traversal evidence',JSON.stringify({elapsed_seconds:s.elapsed,delivered:s.delivered,collisions:s.collisions,resumed,finished:s.finishCount}));
});
