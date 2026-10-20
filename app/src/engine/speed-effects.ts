import {PostProcess} from '@babylonjs/core/PostProcesses/postProcess';
import {Effect} from '@babylonjs/core/Materials/effect';
import {Texture} from '@babylonjs/core/Materials/Textures/texture';
import type {FreeCamera} from '@babylonjs/core/Cameras/freeCamera';
import type {Engine} from '@babylonjs/core/Engines/engine';
Effect.ShadersStore['wewaRadialFragmentShader']=`precision highp float;
varying vec2 vUV;uniform sampler2D textureSampler;uniform float strength;
void main(){vec2 direction=vUV-vec2(.5);float edge=smoothstep(.22,.65,length(direction));vec4 color=texture2D(textureSampler,vUV)*.28;
for(int i=1;i<=4;i++){float t=float(i)/4.;vec2 offset=direction*t*strength*edge;color+=texture2D(textureSampler,vUV-offset)*.09;color+=texture2D(textureSampler,vUV+offset)*.09;}gl_FragColor=color;}`;
export class SpeedEffects {
 attached=false;strength=0;private process:PostProcess;
 constructor(private camera:FreeCamera,engine:Engine){this.process=new PostProcess('wewa-peripheral-speed','wewaRadial',['strength'],null,1,null,Texture.BILINEAR_SAMPLINGMODE,engine);this.process.onApply=effect=>effect.setFloat('strength',this.strength);}
 update(enabled:boolean,boosting:boolean,dt:number){const target=(enabled&&boosting)? .035:0;this.strength+=(target-this.strength)*Math.min(1,dt/(target? .2:.35)*3);const active=enabled&&this.strength>.0001;if(active&&!this.attached){this.camera.attachPostProcess(this.process);this.attached=true;}else if(!active&&this.attached){this.camera.detachPostProcess(this.process);this.attached=false;}}
}
