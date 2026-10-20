import type {StorageLike} from './profile';
export type Action='gas'|'brake'|'left'|'right'|'nitro'|'horn';
const defaults:Record<Action,string>={gas:'w',brake:'s',left:'a',right:'d',nitro:'shift',horn:'h'};
const aliases:Record<Action,string[]>={gas:['z','arrowup'],brake:['arrowdown',' '],left:['q','arrowleft'],right:['arrowright'],nitro:[],horn:[]};
export class InputBindings {
 values={...defaults};
 constructor(private storage:StorageLike|null){try{const v=JSON.parse(storage?.getItem('viva-wewa.bindings.v1')||'null');if(v?.schema===1)for(const action of Object.keys(defaults) as Action[])if(typeof v.values?.[action]==='string'&&v.values[action].length<24)this.values[action]=v.values[action];}catch{/* Defaults remain usable. */}}
 resolve(key:string){return (Object.keys(defaults) as Action[]).filter(a=>this.values[a]===key||(this.values[a]===defaults[a]&&aliases[a].includes(key)));}
 bind(action:Action,key:string){if(!key||key.length>=24||['escape','p','c','r'].includes(key)||this.resolve(key).some(a=>a!==action))return false;this.values[action]=key;try{this.storage?.setItem('viva-wewa.bindings.v1',JSON.stringify({schema:1,values:this.values}));}catch{/* Remapping still works for the session. */}return true;}
 reset(){this.values={...defaults};try{this.storage?.removeItem('viva-wewa.bindings.v1');}catch{/* Defaults still restored. */}}
}
