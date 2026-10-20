#!/usr/bin/env python3
"""Rebuild editable hero sources and review exports without touching app/ or deploying."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--out',type=Path,default=ROOT/'assets-src/hero-lot01/generated')
parser.add_argument('--gltf-transform',default=shutil.which('gltf-transform'))
parser.add_argument('--no-render',action='store_true')
parser.add_argument('--cargo',type=Path,help='Optional separately fabricated parcel GLB for the loaded review variant')
args=parser.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
if out.is_relative_to(ROOT/'app'):raise ValueError('Review output must stay outside app/.')
if not args.gltf_transform:raise SystemExit('Install @gltf-transform/cli 4.5.1 or pass --gltf-transform /absolute/path/to/gltf-transform')
sources=ROOT/'assets-src/hero-lot01';vendors=sources/'vendors'
def run(command,env=None):subprocess.run([str(x) for x in command],cwd=ROOT,env=env,check=True)
environment={**os.environ,'VIVA_WEWA_ASSET_OUTPUT':str(out/'motorcycle'),'VIVA_WEWA_RENDER':'0','VIVA_WEWA_SADDLE_NORMAL':str(vendors/'polyhaven/fabric_leather_01_nor_gl_2k.jpg')}
run(['blender','--background','--python-exit-code','1','--python',sources/'build_motorcycle.py'],environment)
config={'output':str(out/'rider'),'anatomy':str(vendors/'anatomy'),
        'clothes':[str(vendors/'makehuman-system/clothes/male_casualsuit05/male_casualsuit05.mhclo'),str(vendors/'makehuman-system/clothes/shoes04/shoes04.mhclo')],
        'skin':str(vendors/'makehuman-system/skins/young_african_male/young_darkskinned_male_diffuse.png'),
        'backpack_normal':str(vendors/'polyhaven/denim_fabric_nor_gl_2k.jpg'),
        'motorcycle':str(out/'motorcycle/viva-wewa-motorcycle.glb'),'render':not args.no_render}
if args.cargo:config['cargo']=str(args.cargo.resolve())
(out/'inputs.json').write_text(json.dumps(config,indent=2)+'\n')
run(['blender','--background','--python-exit-code','1','--python',sources/'build_rider.py','--','--config',out/'inputs.json'])
for name,source in [('rider',out/'rider/rider-review.glb'),('firstperson',out/'rider/firstperson-review.glb'),('motorcycle',out/'motorcycle/viva-wewa-motorcycle.glb')]:
    resized=source.parent/(name+'-1k.glb');compressed=source.parent/(name+'-webp.glb');final=source.parent/(name+'-validation.glb')
    run([args.gltf_transform,'resize',source,resized,'--width','1024','--height','1024'])
    run([args.gltf_transform,'webp',resized,compressed,'--quality','94'])
    run(['node','tools/prepare_hero_review.mjs',compressed,final])
print('Review sources and exports created at',out)
