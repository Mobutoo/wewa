"""Original right cover paint; own right-profile landmarks, no photo sampling."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path(__file__).resolve().parents[1];H=R/'assets-src/moto-components/side-cover-right-v1';P=json.loads((H/'parameters-v1.json').read_text());T=H/'textures';T.mkdir(exist_ok=True)
def srgb(x):return round(255*(12.92*x if x<=.0031308 else 1.055*x**(1/2.4)-.055))
S=2048;im=Image.new('RGB',(S,S),tuple(srgb(x)for x in [.36,.004,.012]));line=[]
for px,py in reversed(P['paint_boundary_pixels_estimated']):
 u=(432-px)*P['meters_per_pixel']/.42+.5;v=(360-py)*P['meters_per_pixel']/.25+.5;line.append((u*S,(1-v)*S))
line=[(-100,line[0][1])]+line+[(S+100,line[-1][1]),(S+100,S+100),(-100,S+100)]
ImageDraw.Draw(im).polygon(line,fill=tuple(srgb(x)for x in [.009,.010,.012]));im.resize((1024,1024),Image.Resampling.LANCZOS).save(T/'original-right-red-black-v1.png')
