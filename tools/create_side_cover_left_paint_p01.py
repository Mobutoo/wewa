"""Original analytic UV paint: no product image is sampled."""
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];out=R/'assets-src/moto-components/side-cover-left/textures';out.mkdir(parents=True,exist_ok=True)
def srgb(x):return round(255*(12.92*x if x<=.0031308 else 1.055*x**(1/2.4)-.055))
size=2048
im=Image.new('RGB',(size,size),tuple(srgb(x)for x in [.36,.004,.012]));draw=ImageDraw.Draw(im);line=[]
for u in range(size):
 x=(u/(size-1)-.5)*.30;y=-.030+.35*max(0,-x);v=y/.18+.5;line.append((u,(1-v)*size))
draw.polygon(line+[(size-1,size),(0,size)],fill=tuple(srgb(x)for x in [.009,.010,.012]));im.resize((1024,1024),Image.Resampling.LANCZOS).save(out/'original-red-black-study-v1.png')
