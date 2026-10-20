// Measure actual exported geometry independently of generator report counters.
import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import {getBounds} from '@gltf-transform/functions';
import fs from 'node:fs/promises';
import path from 'node:path';
const [folder]=process.argv.slice(2);if(!folder)throw Error('Pass the lot output directory');
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS);
const motorcycle=await io.read(path.join(folder,'motorcycle/motorcycle-validation.glb'));
const bounds=getBounds(motorcycle.getRoot().getDefaultScene());
const dimensions=bounds.max.map((x,i)=>x-bounds.min[i]);
const front=motorcycle.getRoot().listNodes().find(n=>n.getName()==='front_wheel');
const rear=motorcycle.getRoot().listNodes().find(n=>n.getName()==='rear_wheel');
if(!front||!rear)throw Error('Wheel pivots missing');
const fp=front.getWorldTranslation(),rp=rear.getWorldTranslation();
const wheelbase=Math.hypot(...fp.map((x,i)=>x-rp[i]));
const expected=[.740,1.134,2.016];
if(dimensions.some((x,i)=>Math.abs(x-expected[i])>.005)||Math.abs(wheelbase-1.285)>.001)throw Error('Exported reference envelope/wheelbase outside stated tolerance');
const rider=await io.read(path.join(folder,'rider/rider-validation.glb'));
const skin=rider.getRoot().listSkins()[0];if(skin.listJoints().length!==53)throw Error('Anatomical rig missing');
const jointNames=['hand_l','hand_r','foot_l','foot_r'];
const joints=Object.fromEntries(jointNames.map(name=>{const node=rider.getRoot().listNodes().find(n=>n.getName()===name);if(!node)throw Error('Missing joint '+name);return [name,node.getWorldTranslation()];}));
const result={schema:1,scope:'Actual review GLB geometry measurements; not manufacturer CAD or local/art acceptance',
 motorcycle_dimensions_xyz_m:dimensions,manufacturer_reference_width_height_length_m:expected,
 envelope_tolerance_m:.005,wheelbase_m:wheelbase,wheelbase_tolerance_m:.001,
 seated_rig_joints:skin.listJoints().length,joint_positions_glb_xyz_m:joints,art_accepted:false,physical_iphone_tested:false};
await fs.writeFile(path.join(folder,'geometry-check.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
