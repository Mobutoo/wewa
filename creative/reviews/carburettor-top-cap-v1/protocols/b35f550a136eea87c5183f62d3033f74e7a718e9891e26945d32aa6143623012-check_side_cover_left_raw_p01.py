"""P01 EXR header check at900x700; derived from check_component_raw_exr_v1.py, no calibration claim."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('review');args=parser.parse_args()
folder=ROOT/'creative/reviews'/args.review

def string(handle):
    value=bytearray()
    while True:
        byte=handle.read(1)
        if not byte:raise ValueError('Truncated EXR string')
        if byte==b'\0':return value.decode()
        value.extend(byte)

rows=[]
for path in sorted((folder/'raw').glob('*.exr')):
    with path.open('rb')as f:
        assert f.read(4)==b'\x76\x2f\x31\x01'
        version=struct.unpack('<I',f.read(4))[0];attributes={}
        while True:
            name=string(f)
            if not name:break
            kind=string(f);size=struct.unpack('<I',f.read(4))[0]
            attributes[name]=(kind,f.read(size))
        channels={};data=attributes['channels'][1];offset=0
        while data[offset]:
            end=data.index(0,offset);name=data[offset:end].decode();offset=end+1
            pixel_type=struct.unpack_from('<i',data,offset)[0];offset+=16
            channels[name]=pixel_type
        assert channels and all(t==2 for t in channels.values()),(path,channels)
        card=path.stem=='exposure-reference'
        if not card:
            for required in ('Combined.R','Noisy Image.R','Denoising Albedo.R','Denoising Normal.X'):
                assert any(name.endswith(required)for name in channels),(path,required)
        x0,y0,x1,y1=struct.unpack('<4i',attributes['dataWindow'][1])
        assert (x1-x0+1,y1-y0+1)==((128,128)if card else(900,700))
    rows.append({'path':str(path.relative_to(ROOT)),
                 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                 'bytes':path.stat().st_size,'version':version,
                 'channels_pixel_type':channels,'all_channels_FLOAT32':True,
                 'resolution_px':[x1-x0+1,y1-y0+1],
                 'reference_card_single_layer':card})
assert rows
(folder/'raw-render-check.json').write_text(json.dumps({'schema':1,'files':rows,
    'scope':'Actual saved EXR header/channel/dimension/hash checks, not decoded-pixel fidelity, '
            'radiometric calibration, artistic or hardware reception.'},indent=2)+'\n')
print('RAW_HEADERS_VERIFIED',args.review,len(rows))
