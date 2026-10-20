import type {Mode} from '../types';
export const RULES_VERSION='viva-wewa-r9.2';
export const CHALLENGE_SEED=31020;
export interface FinishedRun {runId:string;mode:Mode;phase:string;score:number;delivered:number;rules:string;seed:number;worldKey?:string}
export interface Profile {schema:2;records:Record<string,number>;reputation:number;coins:number;completedRuns:string[]}
export interface StorageLike {getItem(key:string):string|null;setItem(key:string,value:string):void;removeItem(key:string):void}
export const freshProfile=():Profile=>({schema:2,records:{},reputation:0,coins:0,completedRuns:[]});
const isCount=(v:unknown)=>typeof v==='number'&&Number.isSafeInteger(v)&&v>=0&&v<=1e9;
export function validateProfile(v:unknown):v is Profile{if(!v||typeof v!=='object')return false;const p=v as Profile;return p.schema===2&&isCount(p.reputation)&&isCount(p.coins)&&!!p.records&&typeof p.records==='object'&&Object.values(p.records).every(isCount)&&Array.isArray(p.completedRuns)&&p.completedRuns.length<=256&&p.completedRuns.every(s=>typeof s==='string'&&s.length<100);}
export class ProfileStore {
  profile=freshProfile();available=true;
  constructor(private storage:StorageLike|null){try{const raw=storage?.getItem('viva-wewa.profile.v2');if(raw){const parsed=JSON.parse(raw);if(validateProfile(parsed))this.profile=parsed;}else{const old=JSON.parse(storage?.getItem('viva-wewa.v1')||'{}');if(isCount(old.record))this.profile.records['legacy/unversioned']=old.record;}}catch{this.available=false;}}
  record(mode:Mode='rush',rules=RULES_VERSION,seed=CHALLENGE_SEED,worldKey='unspecified'){return this.profile.records[`${mode}/${rules}/${seed}/${worldKey}`]||0;}
  complete(run:FinishedRun){if(run.phase!=='finished'||!run.runId||run.runId.length>99||!isCount(run.score)||!isCount(run.delivered)||this.profile.completedRuns.includes(run.runId))return false;const key=`${run.mode}/${run.rules}/${run.seed}/${run.worldKey||'unspecified'}`;this.profile.records[key]=Math.max(this.profile.records[key]||0,run.score);this.profile.reputation+=run.delivered*2+(run.mode==='story'?20:0);this.profile.coins+=run.delivered*5;this.profile.completedRuns.push(run.runId);this.profile.completedRuns=this.profile.completedRuns.slice(-256);this.write();return true;}
  reset(){this.profile=freshProfile();this.write();try{this.storage?.removeItem('viva-wewa.run.v1');}catch{this.available=false;}}
  private write(){try{this.storage?.setItem('viva-wewa.profile.v2',JSON.stringify(this.profile));}catch{this.available=false;}}
  saveRun(snapshot:unknown){try{this.storage?.setItem('viva-wewa.run.v1',JSON.stringify(snapshot));}catch{this.available=false;}}
  readRun():unknown{try{return JSON.parse(this.storage?.getItem('viva-wewa.run.v1')||'null');}catch{this.available=false;return null;}}
  clearRun(){try{this.storage?.removeItem('viva-wewa.run.v1');}catch{this.available=false;}}
}
