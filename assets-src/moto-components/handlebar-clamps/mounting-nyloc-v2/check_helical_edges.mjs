// Read actual crease edges: constant-radius helices and continuity across the seam.
import fs from'node:fs/promises';import{createHash}from'node:crypto';import{NodeIO}from'@gltf-transform/core';
const current='assets-src/moto-components/handlebar-clamps/mounting-nyloc-v2/handlebar-mount-nyloc-v2-inspection.glb',old='/workspace/wewa-assets/work-in-progress/handlebar-mount-nyloc/rejected-thread-grid/source/handlebar-mount-nyloc-inspection.glb';
const P=.0015,major=.00506,minor=major-5*Math.sqrt(3)*P/16,phases=[.125,.4375,.5625,.875];
async function check(file){const bytes=await fs.readFile(file),root=(await new NodeIO().read(file)).getRoot(),rows=phases.map(phase=>({phase,edges:0,seam_edges:0,max_constant_radius_error_m:0,max_helical_pitch_edge_error_m:0})),seen=new Set();
 for(const mesh of root.listMeshes())for(const primitive of mesh.listPrimitives()){
  const p=primitive.getAttribute('POSITION'),ix=primitive.getIndices(),v=[];
  for(let i=0;i<p.getCount();i++){const q=[];p.getElement(i,q);const angle=(Math.atan2(-q[2],q[0])+2*Math.PI)%(2*Math.PI),radius=Math.hypot(q[0],q[2]),phase=((q[1]/P-angle/(2*Math.PI))%1+1)%1;const cls=phases.findIndex(x=>Math.abs(x-phase)<5e-5);v.push({q,angle,radius,cls,valid:q[1]>.0012&&q[1]<.0059&&cls>=0&&Math.abs(radius-([0,3].includes(cls)?minor:major))<5e-9});}
  for(let i=0;i<ix.getCount();i+=3)for(let j=0;j<3;j++){
   const a=v[ix.getScalar(i+j)],b=v[ix.getScalar(i+(j+1)%3)];if(!a.valid||!b.valid||a.cls!==b.cls)continue;const raw=b.angle-a.angle,da=((raw+3*Math.PI)%(2*Math.PI))-Math.PI;if(Math.abs(Math.abs(da)-2*Math.PI/288)>1e-5)continue;
   const key=[a.q.join(','),b.q.join(',')].sort().join('|');if(seen.has(key))continue;seen.add(key);const r=rows[a.cls];r.edges++;if(Math.abs(raw)>Math.PI)r.seam_edges++;r.max_constant_radius_error_m=Math.max(r.max_constant_radius_error_m,Math.abs(a.radius-b.radius));r.max_helical_pitch_edge_error_m=Math.max(r.max_helical_pitch_edge_error_m,Math.abs(b.q[1]-a.q[1]-P*da/(2*Math.PI)));
  }
 }
 const passed=rows.every(r=>r.edges>=500&&r.seam_edges>=1&&r.max_constant_radius_error_m<5e-9&&r.max_helical_pitch_edge_error_m<5e-9);return{file,sha256:createHash('sha256').update(bytes).digest('hex'),actual_crease_edge_classes:rows,constant_radius_and_shifted_seam_continuity_passed:passed};
}
const [before,after]=await Promise.all([check(old),check(current)]);if(!after.constant_radius_and_shifted_seam_continuity_passed)throw Error(JSON.stringify(after));const report={method:'Actual GLB triangle edges, four60degree-profile crease phases, mid engagement only. Fixed-radius helical edge dz=P*dAngle/2pi, including angular seam; no topology or buffers modified.',old_rejected:before,current:after,precision_tolerance_m:5e-9,manufacturer_thread_gauge_or_tolerance_verified:false,art_accepted:false};await fs.writeFile('creative/reviews/handlebar-mount-nyloc-v2/helical-edge-buffer-check.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
