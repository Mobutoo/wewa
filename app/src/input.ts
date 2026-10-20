/** Independent axis dead zones preserve full acceleration while steering diagonally. */
export function joystickAxes(x:number,y:number){
  const axis=(value:number)=>{const v=Math.max(-1,Math.min(1,value));return Math.abs(v)<.12?0:Math.sign(v)*(Math.abs(v)-.12)/.88;};
  return {steering:axis(x),throttle:axis(-y)};
}
