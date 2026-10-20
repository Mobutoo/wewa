import { Engine } from '@babylonjs/core/Engines/engine';
import { Scene } from '@babylonjs/core/scene';
import { FreeCamera } from '@babylonjs/core/Cameras/freeCamera';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import { Color3, Color4 } from '@babylonjs/core/Maths/math.color';
import { HemisphericLight } from '@babylonjs/core/Lights/hemisphericLight';
import { DirectionalLight } from '@babylonjs/core/Lights/directionalLight';
import { ShadowGenerator } from '@babylonjs/core/Lights/Shadows/shadowGenerator';
import '@babylonjs/core/Lights/Shadows/shadowGeneratorSceneComponent';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { DynamicTexture } from '@babylonjs/core/Materials/Textures/dynamicTexture';
import { MeshBuilder } from '@babylonjs/core/Meshes/meshBuilder';
import { Mesh } from '@babylonjs/core/Meshes/mesh';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { VertexData } from '@babylonjs/core/Meshes/mesh.vertexData';
import { VertexBuffer } from '@babylonjs/core/Buffers/buffer';
import { SceneLoader } from '@babylonjs/core/Loading/sceneLoader';
import '@babylonjs/loaders/glTF';
import type {Obstacle,Point,WorldData} from './types';
import type {Simulation} from './simulation';
import {distance,sampleRoute,pointSegment,insideRing,circlePolygon} from './math';

export class GameWorld {
  engine:Engine;scene:Scene;camera:FreeCamera;bike:TransformNode;rider:TransformNode;sun:DirectionalLight;shadows:ShadowGenerator;
  firstPerson=false;comfort=true;fovEffect=true;shake=false;loadedCells=new Map<string,Mesh[]>();loadingCells=new Set<string>();streamTime=0;
  materials:Record<string,StandardMaterial>={};frontWheel:TransformNode|null=null;rearWheel:TransformNode|null=null;
  vehicles:{root:TransformNode;kind:string}[]=[];pedestrians:{root:TransformNode;phase:number;crossing:boolean}[]=[];
  parcelMeshes=new Map<string,TransformNode>();depotMeshes:TransformNode[]=[];taxi:TransformNode;
  cameraPosition=new Vector3();cameraTarget=new Vector3();ready=false;frameTimes:number[]=[];lastTime=0;
  cameraShapes:{minx:number;maxx:number;minz:number;maxz:number;height:number;rings:Point[][]}[];
  constructor(public canvas:HTMLCanvasElement,public world:WorldData){
    this.cameraShapes=world.buildings.map(b=>({minx:Math.min(...b.rings[0].map(p=>p[0])),maxx:Math.max(...b.rings[0].map(p=>p[0])),minz:Math.min(...b.rings[0].map(p=>p[1])),maxz:Math.max(...b.rings[0].map(p=>p[1])),height:b.height,rings:b.rings}));
    this.engine=new Engine(canvas,true,{preserveDrawingBuffer:true,stencil:true,adaptToDeviceRatio:false,powerPreference:'high-performance'});
    this.scene=new Scene(this.engine);this.scene.useRightHandedSystem=true;
    this.scene.imageProcessingConfiguration.toneMappingEnabled=true;this.scene.imageProcessingConfiguration.toneMappingType=2;this.scene.imageProcessingConfiguration.contrast=1.05;
    this.bike=new TransformNode('bike',this.scene);
    this.scene.clearColor=new Color4(.69,.79,.83,1);this.scene.fogMode=Scene.FOGMODE_LINEAR;this.scene.fogColor=new Color3(.72,.79,.80);this.scene.fogStart=130;this.scene.fogEnd=540;
    const hemi=new HemisphericLight('sky',new Vector3(0,1,0),this.scene);hemi.intensity=.68;hemi.groundColor=new Color3(.38,.32,.27);
    this.sun=new DirectionalLight('afternoon',new Vector3(-.6,-1,.3),this.scene);this.sun.intensity=.95;this.sun.diffuse=new Color3(1,.89,.74);
    this.sun.autoUpdateExtends=false;this.sun.orthoLeft=-45;this.sun.orthoRight=45;this.sun.orthoTop=45;this.sun.orthoBottom=-45;this.sun.shadowMinZ=1;this.sun.shadowMaxZ=140;
    this.shadows=new ShadowGenerator(1024,this.sun);this.shadows.usePercentageCloserFiltering=true;this.shadows.filteringQuality=ShadowGenerator.QUALITY_LOW;this.shadows.bias=.001;this.shadows.darkness=.3;
    this.camera=new FreeCamera('camera',new Vector3(0,5,-8),this.scene);this.camera.minZ=.08;this.camera.maxZ=750;this.camera.fov=Math.PI/3;
    this.camera.inputs.clear();this.scene.activeCamera=this.camera;
    this.material('asphalt','#575655');this.material('sidewalk','#a69e8c');this.material('sand','#97846c');this.material('mark','#e5d3a1');
    this.material('yellow','#ecc13b');this.material('blue','#286b85');this.material('glass','#334953');this.material('black','#232a2c');this.material('chrome','#9aa9ad');this.material('skin','#573522');this.material('shirt','#e57526');this.material('white','#e0d9c8');this.material('leaf','#455d38');this.material('wood','#6e5140');this.material('green','#92e2ac');this.material('cyan','#5ee7eb');
    this.materials.chrome.specularColor=new Color3(.9,.9,.85);this.materials.chrome.specularPower=80;
    this.materials.green.emissiveColor=new Color3(.25,.45,.25);this.materials.cyan.emissiveColor=new Color3(.2,.45,.5);
    const ground=MeshBuilder.CreateGround('land',{width:3000,height:3000},this.scene);ground.material=this.materials.sand;ground.position.y=-.04;ground.receiveShadows=true;
    this.roads();this.facadeMaterials();this.rider=this.person(this.bike,true);this.placeholderBike();
    this.taxi=this.car('taxi');this.taxi.setEnabled(false);
    for(let i=0;i<8;i++)this.vehicles.push({root:this.car(i%3===0?'minibus':'taxi'),kind:i%3===0?'minibus':'taxi'});
    for(let i=0;i<12;i++){const root=this.person(undefined,false,i);this.pedestrians.push({root,phase:i*.23,crossing:i<4});}
    this.markers();this.streetLife();this.facadeDetails();
    this.cameraPosition.copyFromFloats(world.spawn[0]-6,4,world.spawn[1]-8);
    this.cameraTarget.copyFromFloats(...[world.spawn[0],1,world.spawn[1]] as [number,number,number]);
    this.roadTexture();this.resize();window.addEventListener('resize',()=>this.resize());
  }
  material(name:string,hex:string){const m=new StandardMaterial(name,this.scene);m.diffuseColor=Color3.FromHexString(hex);m.specularColor=new Color3(.08,.08,.08);this.materials[name]=m;return m;}
  box(name:string,size:Vector3,pos:Vector3,mat:string,parent?:TransformNode){const mesh=MeshBuilder.CreateBox(name,{width:size.x,height:size.y,depth:size.z},this.scene);mesh.position=pos;mesh.material=this.materials[mat];if(parent)mesh.parent=parent;return mesh;}
  cylinder(name:string,diameter:number,height:number,pos:Vector3,mat:string,parent?:TransformNode){const mesh=MeshBuilder.CreateCylinder(name,{diameter,height,tessellation:10},this.scene);mesh.position=pos;mesh.material=this.materials[mat];if(parent)mesh.parent=parent;return mesh;}
  roads(){
    const positions:number[]=[],indices:number[]=[],uv:number[]=[],sidePositions:number[]=[],sideIndices:number[]=[],marks:number[]=[],markIndices:number[]=[];
    const quad=(points:number[],ids:number[],a:Point,b:Point,width:number,y:number)=>{
      const dx=b[0]-a[0],dz=b[1]-a[1],len=Math.hypot(dx,dz);if(!len)return;const nx=dz/len*width/2,nz=-dx/len*width/2,i=points.length/3;
      points.push(a[0]+nx,y,a[1]+nz,b[0]+nx,y,b[1]+nz,b[0]-nx,y,b[1]-nz,a[0]-nx,y,a[1]-nz);ids.push(i,i+1,i+2,i,i+2,i+3);
    };
    for(const segment of this.world.segments){
      const a=this.world.nodes[segment.a],b=this.world.nodes[segment.b],w=segment.width;
      quad(sidePositions,sideIndices,a,b,w+1.6,.008);quad(positions,indices,a,b,w,.025);uv.push(0,0,1,0,1,1,0,1);
      const len=distance(a,b);
      if(w>=6)for(let d=3;d<len-2;d+=10){const f=d/len,g=Math.min(d+3,len)/len;quad(marks,markIndices,[a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f],[a[0]+(b[0]-a[0])*g,a[1]+(b[1]-a[1])*g],.12,.031);}
    }
    for(const [name,p,i,mat]of [['road',positions,indices,'asphalt'],['walks',sidePositions,sideIndices,'sidewalk'],['lines',marks,markIndices,'mark']] as const){
      const mesh=new Mesh(name,this.scene),v=new VertexData();v.positions=p;v.indices=i;v.normals=new Array(p.length).fill(0).map((_,n)=>n%3===1?1:0);v.uvs=[];for(let k=0;k<p.length;k+=3)v.uvs.push(p[k]/5,p[k+2]/5);v.applyToMesh(mesh);mesh.material=this.materials[mat];mesh.material.backFaceCulling=false;mesh.receiveShadows=true;mesh.freezeWorldMatrix();
    }
  }
  roadTexture(){
    const texture=new DynamicTexture('original-procedural-asphalt',{width:256,height:256},this.scene,false);const ctx=texture.getContext();
    ctx.fillStyle='#777773';ctx.fillRect(0,0,256,256);
    let seed=2941;const rand=()=>{seed=(seed*16807)%2147483647;return seed/2147483647;};
    for(let i=0;i<17000;i++){const shade=65+Math.floor(rand()*90);ctx.fillStyle=`rgba(${shade},${shade},${shade-3},.5)`;ctx.fillRect(rand()*256,rand()*256,rand()*1.2+.4,rand()*1.2+.4);}
    ctx.strokeStyle='#42443f';ctx.lineWidth=.5;ctx.beginPath();ctx.moveTo(22,0);ctx.lineTo(34,62);ctx.lineTo(18,108);ctx.lineTo(24,170);ctx.stroke();texture.update();this.materials.asphalt.diffuseTexture=texture;this.materials.asphalt.diffuseColor=Color3.White();this.materials.asphalt.specularColor=new Color3(.08,.08,.07);
  }
  facadeMaterials(){
    const palettes=['#c8b898','#bca58e','#a8afb0','#d2c6b4'];
    palettes.forEach((color,i)=>{
      const texture=new DynamicTexture(`facade-${i}`,{width:128,height:128},this.scene,false),ctx=texture.getContext();ctx.fillStyle=color;ctx.fillRect(0,0,128,128);
      ctx.fillStyle='rgba(65,54,40,.12)';for(let j=0;j<200;j++)ctx.fillRect((j*47)%128,(j*23)%128,1+(j%3),1);
      ctx.fillStyle='#485b62';ctx.fillRect(17,29,35,48);ctx.fillRect(77,29,35,48);ctx.fillStyle='#89999b';ctx.fillRect(21,33,12,40);ctx.fillRect(81,33,12,40);
      ctx.fillStyle='rgba(255,239,209,.6)';ctx.fillRect(14,25,42,4);ctx.fillRect(74,25,42,4);ctx.fillStyle='rgba(76,56,36,.17)';ctx.fillRect(0,117,128,4);texture.update();texture.uScale=1;texture.vScale=1;
      const m=this.material(`facade${i}`,'#ffffff');m.diffuseTexture=texture;m.specularColor=Color3.Black();
    });
  }
  async loadBike(){
    try{
      const result=await SceneLoader.ImportMeshAsync('','/models/','motorcycle.glb',this.scene);
      const old=this.bike.getChildMeshes().filter(m=>m.metadata?.placeholder);old.forEach(m=>m.dispose());
      for(const root of result.meshes.filter(m=>!m.parent)){root.parent=this.bike;}
      result.meshes.filter(m=>m instanceof Mesh).forEach(m=>this.shadows.addShadowCaster(m as Mesh));
      this.frontWheel=this.scene.getTransformNodeByName('front_wheel')||this.scene.getMeshByName('front_wheel');
      this.rearWheel=this.scene.getTransformNodeByName('rear_wheel')||this.scene.getMeshByName('rear_wheel');
      for(const wheel of [this.frontWheel,this.rearWheel])if(wheel?.rotationQuaternion){wheel.rotation.copyFrom(wheel.rotationQuaternion.toEulerAngles());wheel.rotationQuaternion=null;}
    }catch(error){console.warn('Provisional bike retained',error);}
    try{
      const result=await SceneLoader.ImportMeshAsync('','/models/','rider.glb',this.scene);
      this.rider.dispose();this.rider=new TransformNode('rider',this.scene);
      this.rider.parent=this.bike;result.meshes.filter(m=>!m.parent).forEach(m=>m.parent=this.rider);result.meshes.filter(m=>m instanceof Mesh).forEach(m=>this.shadows.addShadowCaster(m as Mesh));
    }catch{/* Original temporary rider remains until its asset is delivered. */}
    const container=await SceneLoader.LoadAssetContainerAsync('/models/','minibus.glb',this.scene);
    this.vehicles.filter(v=>v.kind==='minibus').forEach((v,i)=>{
      v.root.getChildMeshes().forEach(m=>m.dispose());
      const instance=container.instantiateModelsToScene(name=>`bus-${i}-${name}`,false,{doNotInstantiate:true});
      instance.rootNodes.forEach(n=>{n.parent=v.root;n.getChildMeshes().forEach(m=>this.shadows.addShadowCaster(m as Mesh));});
    });
  }
  placeholderBike(){
    const parts:Mesh[]=[];
    parts.push(this.box('tank',new Vector3(.35,.26,.48),new Vector3(0,.76,.25),'shirt',this.bike));
    parts.push(this.box('seat',new Vector3(.32,.12,.66),new Vector3(0,.80,-.25),'black',this.bike));
    for(const z of [-.6425,.6425]){const wheel=this.cylinder('wheel',.65,.1,new Vector3(0,.325,z),'black',this.bike);wheel.rotation.z=Math.PI/2;parts.push(wheel);}
    parts.forEach(m=>m.metadata={placeholder:true});
  }
  person(parent?:TransformNode,seated=false,index=0){
    const root=new TransformNode(seated?'rider':`pedestrian-${index}`,this.scene);if(parent)root.parent=parent;
    const hip=seated?.82:.92;
    this.box('trousers',new Vector3(.33,.3,.2),new Vector3(0,hip,0),'blue',root);
    this.box('shirt',new Vector3(.4,.49,.23),new Vector3(0,hip+.36,.03),index%3===0?'shirt':index%3===1?'blue':'white',root);
    const head=MeshBuilder.CreateSphere('head',{diameter:.22,segments:8},this.scene);head.position=new Vector3(0,hip+.76,.05);head.material=this.materials.skin;head.parent=root;
    for(const sign of [-1,1]){
      const arm=this.cylinder('arm',.09,seated?.47:.5,new Vector3(sign*.22,hip+.27,seated?.26:.04),'skin',root);arm.rotation.x=seated?1.05:.1;
      const leg=this.cylinder('leg',.13,seated?.5:.78,new Vector3(sign*.14,seated?.55:.48,seated?-.05:0),'blue',root);leg.rotation.x=seated?-.4:0;
      this.box('shoe',new Vector3(.14,.12,.27),new Vector3(sign*.14,seated?.28:.08,.07),'black',root);
    }
    if(seated){const helmet=MeshBuilder.CreateSphere('helmet',{diameter:.31,segments:10},this.scene);helmet.scaling.y=.78;helmet.position=new Vector3(0,hip+.84,.04);helmet.material=this.materials.black;helmet.parent=root;}
    const meshes=root.getChildMeshes() as Mesh[];const merged=Mesh.MergeMeshes(meshes,true,true,undefined,false,true);if(merged)merged.parent=root;
    return root;
  }
  car(kind:string){
    const root=new TransformNode(kind,this.scene),bus=kind==='minibus';
    const length=bus?4.9:3.9,width=bus?1.85:1.65;
    this.box('body',new Vector3(width,bus?1.3:.63,length),new Vector3(0,bus?1.04:.64,0),'yellow',root);
    this.box('cabin',new Vector3(width-.12,bus?.9:.6,bus?length-.45:2.05),new Vector3(0,bus?1.72:1.24,bus?.03:-.15),'glass',root);
    this.box('roof',new Vector3(width-.08,.14,bus?length-.4:2.1),new Vector3(0,bus?2.22:1.58,bus?.03:-.15),'yellow',root);
    if(bus)this.box('stripe',new Vector3(width+.02,.35,length+.02),new Vector3(0,.8,0),'blue',root);
    for(const x of [-width/2,width/2])for(const z of [-length*.31,length*.31]){const wheel=this.cylinder('tyre',.63,.2,new Vector3(x,.34,z),'black',root);wheel.rotation.z=Math.PI/2;}
    for(const x of [-.55,.55]){this.box('light',new Vector3(.25,.18,.03),new Vector3(x,.76,length/2+.02),'white',root);this.box('tail',new Vector3(.22,.13,.03),new Vector3(x,.76,-length/2-.02),'shirt',root);}
    this.box('bumper',new Vector3(width,.12,.08),new Vector3(0,.42,length/2+.04),'chrome',root);
    if(!bus)this.box('taxi-band',new Vector3(width+.015,.12,1.6),new Vector3(0,.89,.15),'black',root);
    const meshes=root.getChildMeshes() as Mesh[],merged=Mesh.MergeMeshes(meshes,true,true,undefined,false,true);if(merged)merged.parent=root;
    return root;
  }
  markers(){
    for(const p of this.world.parcels){
      const root=new TransformNode(p.id,this.scene);root.position=new Vector3(p.point[0],0,p.point[1]);
      const ring=MeshBuilder.CreateTorus('pickup',{diameter:3,thickness:.1,tessellation:20},this.scene);ring.position.y=.12;ring.material=this.materials.yellow;ring.parent=root;
      this.box('parcel',new Vector3(.6,.6,.6),new Vector3(0,1.1,0),'yellow',root);
      this.box('tape',new Vector3(.62,.12,.62),new Vector3(0,1.1,0),'white',root);this.parcelMeshes.set(p.id,root);
    }
    for(const d of this.world.depots){
      const root=new TransformNode(d.id,this.scene);root.position=new Vector3(d.point[0],0,d.point[1]);
      const ring=MeshBuilder.CreateTorus('depot',{diameter:7.5,thickness:.18,tessellation:32},this.scene);ring.position.y=.1;ring.material=this.materials.cyan;ring.parent=root;
      const column=this.cylinder('beacon',.12,7,new Vector3(0,3.5,0),'cyan',root);column.visibility=.65;this.depotMeshes.push(root);
    }
    // Route chevrons are fictional navigation aids, separate from source geometry.
    const arrows:Mesh[]=[];
    for(let s=12;s<this.world.route_length;s+=24){const p=sampleRoute(this.world.route,s);const a=this.box('route-chevron',new Vector3(.25,.015,.9),new Vector3(p.x,.048,p.z),'mark');a.rotation.y=p.yaw-.55;arrows.push(a);const b=this.box('route-chevron',new Vector3(.25,.015,.9),new Vector3(p.x+.42*Math.cos(p.yaw),.048,p.z-.42*Math.sin(p.yaw)),'mark');b.rotation.y=p.yaw+.55;arrows.push(b);}
    const merged=Mesh.MergeMeshes(arrows,true,true);if(merged){merged.material=this.materials.mark;merged.freezeWorldMatrix();}
  }
  streetLife(){
    const props:Mesh[]=[];
    const leaves:number[]=[],leafIndices:number[]=[];
    const widthAt=(s:number)=>{const p=sampleRoute(this.world.route,s);let best=Infinity,width=6;for(const seg of this.world.segments){const d=pointSegment([p.x,p.z],this.world.nodes[seg.a],this.world.nodes[seg.b]).distance;if(d<best){best=d;width=seg.width;}}return width;};
    for(let i=0;i<28;i++){
      const p=sampleRoute(this.world.route,20+i*51,widthAt(20+i*51)/2+2.2);
      const height=5.6+(i%4)*.4,trunk=this.cylinder('palm',.24,height,new Vector3(p.x,height/2,p.z),'wood');trunk.rotation.z=.025;props.push(trunk);
      for(let k=0;k<9;k++){
        const angle=k*Math.PI*2/9+i*.3,dx=Math.sin(angle),dz=Math.cos(angle),length=2.6+(k%3)*.4;
        for(let j=1;j<12;j++){
          const t=j/12,s=t*length,cx=p.x+dx*s,cz=p.z+dz*s,cy=height+Math.sin(t*Math.PI)*.65-t*t*1.0;
          const size=Math.sin(t*Math.PI)*.68+.08;
          for(const side of [-1,1]){const idx=leaves.length/3;
            leaves.push(cx-dx*.15,cy,cz-dz*.15,cx+dz*size*side-dx*.28,cy-.15,cz-dx*size*side-dz*.28,cx+dx*.2,cy-.03,cz+dz*.2);
            leafIndices.push(idx,idx+1,idx+2);
          }
        }
      }
      if(i%3===0){const p2=sampleRoute(this.world.route,35+i*51,-4.8);
        const curb=sampleRoute(this.world.route,35+i*51,-widthAt(35+i*51)/2-2.2);p2.x=curb.x;p2.z=curb.z;
        const stand=this.box('stall',new Vector3(2.3,1,1.3),new Vector3(p2.x,.5,p2.z),'wood');stand.rotation.y=p2.yaw;props.push(stand);
        const canopy=this.box('canopy',new Vector3(3,.12,2.1),new Vector3(p2.x,2.3,p2.z),i%2?'yellow':'blue');canopy.rotation.y=p2.yaw;props.push(canopy);
        for(const x of [-1,1]){const pole=this.cylinder('stall-post',.05,2.3,new Vector3(p2.x+x,1.15,p2.z),'wood');props.push(pole);}
      }
    }
    const merged=Mesh.MergeMeshes(props,true,true,undefined,false,true);if(merged)merged.freezeWorldMatrix();
    const palmLeaves=new Mesh('palm-fronds',this.scene),vertex=new VertexData();vertex.positions=leaves;vertex.indices=leafIndices;const normals:number[]=[];VertexData.ComputeNormals(leaves,leafIndices,normals);vertex.normals=normals;vertex.applyToMesh(palmLeaves);palmLeaves.material=this.materials.leaf;palmLeaves.material.backFaceCulling=false;palmLeaves.freezeWorldMatrix();
  }
  facadeDetails(){
    // Original decorative layer on sourced footprints, not surveyed facades.
    const details:Mesh[]=[];let windows=0;
    const focus=this.world.route.slice(0,12);
    this.material('window-frame','#bdb8a6');this.material('window-pane','#354951');this.materials['window-pane'].specularColor=new Color3(.35,.4,.42);this.materials['window-pane'].specularPower=48;
    const nearby=this.world.buildings.filter(b=>focus.some(p=>distance(p,b.rings[0][0])<105));
    for(const building of nearby){
      const ring=building.rings[0],floors=Math.min(6,Math.floor(building.height/3));
      for(let i=0;i<ring.length-1;i++){
        const a=ring[i],b=ring[i+1],length=distance(a,b);if(length<5||length>95)continue;
        const dx=(b[0]-a[0])/length,dz=(b[1]-a[1])/length;let nx=dz,nz=-dx;
        if(insideRing([(a[0]+b[0])/2+nx*.1,(a[1]+b[1])/2+nz*.1],ring)){nx=-nx;nz=-nz;}
        const yaw=Math.atan2(nx,nz),columns=Math.min(18,Math.floor(length/3.4));
        for(let floor=0;floor<floors;floor++)for(let col=0;col<columns;col++){
          if(windows>=1100)break;windows++;
          const offset=(col+1)*length/(columns+1),x=a[0]+dx*offset+nx*.04,z=a[1]+dz*offset+nz*.04,y=1.75+floor*3;
          const pane=this.box('facade-window',new Vector3(1.15,1.35,.045),new Vector3(x,y,z),'window-pane');pane.rotation.y=yaw;details.push(pane);
          for(const side of [-1,1]){const frame=this.box('window-jamb',new Vector3(.055,1.48,.075),new Vector3(x+dx*.61*side,y,z+dz*.61*side),'window-frame');frame.rotation.y=yaw;details.push(frame);}
          for(const side of [-1,1]){const frame=this.box('window-lintel',new Vector3(1.28,.08,.16),new Vector3(x,y+.7*side,z),'window-frame');frame.rotation.y=yaw;details.push(frame);}
          const bar=this.box('window-mullion',new Vector3(.035,1.32,.07),new Vector3(x+nx*.02,y,z+nz*.02),'window-frame');bar.rotation.y=yaw;details.push(bar);
        }
      }
    }
    const merged=Mesh.MergeMeshes(details,true,true,undefined,false,true);if(merged){merged.freezeWorldMatrix();merged.receiveShadows=true;}
  }
  traffic(time:number):Obstacle[]{
    const obstacles:Obstacle[]=[];
    const cycle=time%36;
    const trafficTime=time-Math.floor(time/36)*6-Math.min(3,Math.max(0,cycle-5))-Math.min(3,Math.max(0,cycle-21));
    this.vehicles.forEach((v,i)=>{
      const p=sampleRoute(this.world.route,75+i*175+trafficTime*6.4,1.35);
      v.root.position.copyFromFloats(p.x,0,p.z);v.root.rotation.y=p.yaw;
      obstacles.push({x:p.x,z:p.z,yaw:p.yaw,radius:v.kind==='minibus'?.9:.8,halfLength:v.kind==='minibus'?1.55:1.15,kind:'vehicle'});
    });
    this.pedestrians.forEach((v,i)=>{
      const crossingPhase=(time-v.phase*.5+36)%36;
      const across=!v.crossing?8.2:crossingPhase<5?-8.5:crossingPhase<8?-8.5+(crossingPhase-5)/3*17:crossingPhase<21?8.5:crossingPhase<24?8.5-(crossingPhase-21)/3*17:-8.5;
      const p=sampleRoute(this.world.route,(v.crossing?290+(i%4)*.7:70)+Math.floor(i/4)*200,across);
      v.root.position.copyFromFloats(p.x,Math.abs(Math.sin(time*10+v.phase))*.025,p.z);v.root.rotation.y=p.yaw+Math.PI/2;
      if(v.crossing)obstacles.push({x:p.x,z:p.z,radius:.42,kind:'person'});
    });return obstacles;
  }
  async stream(x:number,z:number){
    const wanted=this.world.cells.map(c=>({c,d:Math.hypot(c.grid_east_north[0]*128+64-x,-c.grid_east_north[1]*128-64-z)})).filter(v=>v.d<330).sort((a,b)=>a.d-b.d).slice(0,24);
    const ids=new Set(wanted.map(v=>v.c.id));
    for(const [id,meshes]of this.loadedCells){if(!ids.has(id)){meshes.forEach(m=>{this.shadows.removeShadowCaster(m);m.dispose();});this.loadedCells.delete(id);}}
    for(const {c}of wanted){
      if(this.loadedCells.has(c.id)||this.loadingCells.has(c.id)||this.loadingCells.size>=3)continue;
      this.loadingCells.add(c.id);
      const files=c.files.filter(f=>f.path.endsWith('_b.glb'));
      if(!files.length){this.loadedCells.set(c.id,[]);this.loadingCells.delete(c.id);continue;}
      try{
        const result=await SceneLoader.ImportMeshAsync('','/world/',files[0].path,this.scene);
        const meshes=result.meshes as Mesh[];
        for(const mesh of meshes){
          const positions=mesh.getVerticesData(VertexBuffer.PositionKind),normals=mesh.getVerticesData(VertexBuffer.NormalKind);
          if(positions&&normals){const uvs:number[]=[];for(let i=0;i<positions.length;i+=3){const roof=Math.abs(normals[i+1])>.5;uvs.push(roof?.01:(Math.abs(normals[i])>.5?positions[i+2]:positions[i])*.2,roof?.01:positions[i+1]/3.2);}mesh.setVerticesData(VertexBuffer.UVKind,uvs);const hash=Math.abs(c.grid_east_north[0]*7+c.grid_east_north[1]*3)%4;mesh.material=this.materials[`facade${hash}`];mesh.freezeWorldMatrix();}
        }
        meshes.forEach(m=>{if(m.getTotalVertices()>0){m.receiveShadows=true;this.shadows.addShadowCaster(m);}});this.loadedCells.set(c.id,meshes);
      }catch(error){console.warn('Cell loading error',c.id,error);}finally{this.loadingCells.delete(c.id);}
    }
    this.ready=true;
  }
  update(sim:Simulation,delta:number){
    const v=sim.vehicle,dir=new Vector3(Math.sin(v.yaw),0,Math.cos(v.yaw));
    this.sun.position.copyFromFloats(v.x+30,50,v.z-15);
    this.bike.position.copyFromFloats(v.x,0,v.z);this.bike.rotation.y=v.yaw;this.bike.rotation.z=-v.steer*Math.min(v.speed/80,.2);
    this.rider.setEnabled(!this.firstPerson);
    if(this.frontWheel)this.frontWheel.rotation.x+=v.speed*delta/.32;if(this.rearWheel)this.rearWheel.rotation.x+=v.speed*delta/.32;
    for(const [id,root]of this.parcelMeshes){root.setEnabled(!sim.collected.has(id)&&sim.mode!=='free'&&!(sim.mode==='story'&&sim.storyStage>0));root.getChildMeshes().filter(m=>m.name==='parcel'||m.name==='tape').forEach(m=>{m.position.y=1.1+Math.sin(sim.elapsed*3)*.12;});}
    this.depotMeshes.forEach(root=>root.setEnabled(sim.mode!=='free'&&!(sim.mode==='story'&&sim.storyStage>0)));
    const taxi=sim.taxi();this.taxi.setEnabled(sim.mode==='story'&&sim.storyStage===1);this.taxi.position.copyFromFloats(taxi.x,0,taxi.z);this.taxi.rotation.y=taxi.yaw;
    this.traffic(sim.elapsed);
    const desired=this.firstPerson?new Vector3(v.x+dir.x*.18,1.62,v.z+dir.z*.18):new Vector3(v.x-dir.x*(4.9+v.speed*.025),2.15+v.speed*.012,v.z-dir.z*(4.9+v.speed*.025));
    const target=new Vector3(v.x+dir.x*(this.firstPerson?14:5),this.firstPerson?1.57:1.1,v.z+dir.z*(this.firstPerson?14:5));
    // Keep chase camera out of buildings by shortening its boom.
    if(!this.firstPerson){
      const near=this.cameraShapes.filter(b=>v.x>b.minx-9&&v.x<b.maxx+9&&v.z>b.minz-9&&v.z<b.maxz+9);
      const start=new Vector3(v.x,1.65,v.z),goal=desired.clone();let safe=start;
      for(let i=1;i<=30;i++){const probe=Vector3.Lerp(start,goal,i/30);if(near.some(b=>probe.y<b.height+.2&&circlePolygon([probe.x,probe.z],.25,b.rings)))break;safe=probe;}
      desired.copyFrom(safe);
    }
    const alpha=1-Math.exp(-delta*(this.firstPerson?22:7));Vector3.LerpToRef(this.cameraPosition,desired,alpha,this.cameraPosition);Vector3.LerpToRef(this.cameraTarget,target,alpha,this.cameraTarget);
    this.camera.position.copyFrom(this.cameraPosition);this.camera.setTarget(this.cameraTarget);
    const base=this.firstPerson?65:60,extra=v.boosting&&this.fovEffect&&!this.comfort?(this.firstPerson?6:8):0;this.camera.fov+=( (base+extra)*Math.PI/180-this.camera.fov)*Math.min(1,delta*6);
    if(this.shake&&!this.comfort&&v.boosting)this.camera.position.y+=Math.sin(sim.elapsed*70)*.015;
    this.streamTime+=delta;if(this.streamTime>.4){this.streamTime=0;void this.stream(v.x,v.z);}
    this.scene.render();
    this.frameTimes.push(delta*1000);if(this.frameTimes.length>10800)this.frameTimes.shift();
  }
  resize(){const scale=Math.min(window.devicePixelRatio||1,1.5),width=Math.min(window.innerWidth*scale,1600),height=width/window.innerWidth*window.innerHeight;this.engine.setSize(width,height);}
  setCamera(first:boolean){this.firstPerson=first;this.cameraPosition.copyFrom(this.bike.position.add(new Vector3(0,2,-3)));}
  benchmark(){const ext=this.engine.getCaps();return {metadata:{build:'0.1.0',renderer:this.engine.getGlInfo(),webgl:this.engine.webGLVersion,width:this.engine.getRenderWidth(),height:this.engine.getRenderHeight(),userAgent:navigator.userAgent,software_gpu:/SwiftShader|llvmpipe/i.test(this.engine.getGlInfo().renderer),note:'Diagnostic de cette session uniquement ; pas une qualification matérielle'},frames:this.frameTimes.map(frame_ms=>({frame_ms})),active_meshes:this.scene.getActiveMeshes().length,limits:{maxTextures:ext.maxTexturesImageUnits}};}
}
