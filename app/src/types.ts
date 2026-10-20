export type Point = [number, number];
export type Mode = 'rush' | 'delivery' | 'story' | 'free';
export interface WorldData {
  version: number; source: string; axes: string; origin: number[];
  nodes: Point[];
  segments: {a:number;b:number;name:string;width:number;source_id:string;oneway:string|null}[];
  buildings: {id:string;rings:Point[][];height:number;estimate:string}[];
  route: Point[]; route_length:number; spawn:Point;
  parcels: {id:string;point:Point}[];
  depots: {id:string;point:Point;label:string}[];
  cells: {id:string;grid_east_north:Point;files:{path:string;sha256:string}[]}[];
}
export interface Controls {gas:boolean;brake:boolean;left:boolean;right:boolean;nitro:boolean;horn:boolean;throttle?:number;steering?:number}
export interface Obstacle {x:number;z:number;radius:number;kind:'vehicle'|'person';yaw?:number;halfLength?:number}
export const emptyControls = ():Controls => ({gas:false,brake:false,left:false,right:false,nitro:false,horn:false});
