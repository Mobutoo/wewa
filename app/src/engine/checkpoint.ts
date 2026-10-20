import {RULES_VERSION} from './profile';
import type {TrafficSnapshot} from './traffic';
import type {Mode,Point,WorldData} from '../types';
export interface RunSnapshot {
 schema:1;rules:string;worldKey:string;runId:string;seed:number;mode:Mode;phase:'countdown'|'running';ticks:number;crashTicks:number;contactLatched:boolean;countdownTicks:number;
 score:number;combo:number;delivered:number;collisions:number;vehicle:{x:number;z:number;yaw:number;speed:number;nitro:number;boosting:boolean;steer:number;y:number;pitch:number};
 cargo:string[];collected:string[];gates:string[];depotContacts:string[];checkpoint:Point;storyStage:number;taxiStart:number;taxiOrigin:number;lastKnown:Point;
 nitroRest:number;nitroCooldown:number;traffic:TrafficSnapshot;tokens:string[];
}
const finite=(n:unknown)=>typeof n==='number'&&Number.isFinite(n)&&Math.abs(n)<1e8;
const strings=(v:unknown)=>Array.isArray(v)&&v.length<=1000&&v.every(s=>typeof s==='string'&&s.length<=100)&&new Set(v).size===v.length;
export function validRun(v:unknown,worldKey:string):v is RunSnapshot{
 if(!v||typeof v!=='object')return false;const s=v as RunSnapshot;
 if(typeof s.contactLatched!=='boolean'||s.schema!==1||s.rules!==RULES_VERSION||s.worldKey!==worldKey||!['rush','delivery','story','free'].includes(s.mode)||!['countdown','running'].includes(s.phase)||typeof s.runId!=='string'||s.runId.length>99)return false;
 if(![s.seed,s.ticks,s.crashTicks,s.countdownTicks,s.score,s.combo,s.delivered,s.collisions,s.storyStage,s.taxiStart,s.taxiOrigin,s.nitroRest,s.nitroCooldown].every(finite)||s.seed!==31020||s.runId.length<1||s.crashTicks<0||s.crashTicks>72||!Number.isInteger(s.crashTicks)||s.ticks<0||s.ticks>60*60*24||s.score<0||s.combo<1||s.combo>3||!Number.isInteger(s.ticks)||s.countdownTicks<0||s.countdownTicks>180||s.storyStage<0||s.storyStage>2)return false;
 if(!s.vehicle||!['x','z','yaw','speed','nitro','steer','y','pitch'].every(key=>finite((s.vehicle as unknown as Record<string,unknown>)[key]))||s.vehicle.nitro<0||s.vehicle.nitro>100||Math.abs(s.vehicle.speed)>30||typeof s.vehicle.boosting!=='boolean')return false;
 if(![s.cargo,s.collected,s.gates,s.depotContacts,s.tokens].every(strings)||s.cargo.length>3||s.cargo.some(id=>!s.collected.includes(id)))return false;
 if(![s.checkpoint,s.lastKnown].every(p=>Array.isArray(p)&&p.length===2&&p.every(finite)))return false;
 if(!s.traffic||s.traffic.tick<0||!Number.isInteger(s.traffic.tick)||!Number.isInteger(s.traffic.random)||s.traffic.random<0||s.traffic.random>4294967295||!Array.isArray(s.traffic.vehicles)||s.traffic.vehicles.length>32||!s.traffic.vehicles.every(a=>Number.isInteger(a.id)&&Number.isInteger(a.lane)&&a.id>=0&&a.id<32&&['taxi','minibus'].includes(a.kind)&&(a.entryX===undefined||finite(a.entryX))&&(a.entryZ===undefined||finite(a.entryZ))&&[a.id,a.lane,a.along,a.speed,a.x,a.z,a.yaw,a.wait].every(finite)))return false;
 return true;
}

/** Compatibility fingerprint, not an anti-cheat signature. Cosmetic meshes may change independently. */
export function worldKeyFor(world:WorldData){const text=JSON.stringify([world.version,world.nodes,world.segments,world.route,world.parcels,world.depots,world.buildings,world.traffic,world.nitroTokens,world.surfacePatches,world.dressing?.colliders]);let hash=2166136261;for(let i=0;i<text.length;i++)hash=Math.imul(hash^text.charCodeAt(i),16777619);return `${world.version}/${(hash>>>0).toString(16)}`;}
