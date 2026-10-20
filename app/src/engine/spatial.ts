export interface Bounds {minx:number;minz:number;maxx:number;maxz:number}
/** Immutable broad phase. Objects spanning cells are inserted in every covered cell. */
export class SpatialIndex<T extends Bounds>{
  private cells=new Map<string,T[]>();
  constructor(items:T[],private size=48){for(const item of items)for(let x=Math.floor(item.minx/size);x<=Math.floor(item.maxx/size);x++)for(let z=Math.floor(item.minz/size);z<=Math.floor(item.maxz/size);z++){const key=`${x},${z}`;const cell=this.cells.get(key)||[];cell.push(item);this.cells.set(key,cell);}}
  query(area:Bounds):T[]{const found=new Set<T>();for(let x=Math.floor(area.minx/this.size);x<=Math.floor(area.maxx/this.size);x++)for(let z=Math.floor(area.minz/this.size);z<=Math.floor(area.maxz/this.size);z++)for(const item of this.cells.get(`${x},${z}`)||[])if(item.minx<=area.maxx&&item.maxx>=area.minx&&item.minz<=area.maxz&&item.maxz>=area.minz)found.add(item);return [...found];}
}
