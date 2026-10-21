"""Original fictitious WEWA / 001 layout, using licensed unmodified DejaVu Sans Bold glyphs."""
from pathlib import Path
import json,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];H=R/'assets-src/moto-components/license-plate-wewa';O=R/'creative/reviews/license-plate-wewa-v1';assert json.loads((O/'gray-review.json').read_text())['actually_read'];fontdir=H/'fonts';fontdir.mkdir(exist_ok=True);font=fontdir/'DejaVuSans-Bold.ttf'
if not font.exists():shutil.copy2('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',font)
lic=fontdir/'LICENSE-DejaVu.txt'
if not lic.exists():shutil.copy2('/usr/share/doc/fonts-dejavu-core/copyright',lic)
layout=dict(resolution_px=[1024,1024],background_srgb=[238,239,232],ink_srgb=[18,20,22],border_px=[24,236,1000,788],border_radius_px=18,border_width_px=7,text=[dict(value='WEWA',center_px=[512,398],font_size_px=142),dict(value='001',center_px=[512,632],font_size_px=220)],physical_uv_scope='Authored plate180x105mm, front UV x[0,1] y[0.20833,0.79167]; no RDC legal-format claim',font='fonts/DejaVuSans-Bold.ttf',font_source='https://dejavu-fonts.github.io/',font_authorship='Original DejaVu/Bitstream authors; unmodified font, original WEWA game layout only',fictitious=True)
im=Image.new('RGB',tuple(layout['resolution_px']),tuple(layout['background_srgb']));draw=ImageDraw.Draw(im);draw.rounded_rectangle(layout['border_px'],radius=layout['border_radius_px'],outline=tuple(layout['ink_srgb']),width=layout['border_width_px'])
for row in layout['text']:draw.text(tuple(row['center_px']),row['value'],font=ImageFont.truetype(str(font),row['font_size_px']),anchor='mm',fill=tuple(layout['ink_srgb']))
p=H/'wewa-game-plate-original.png';im.save(p);layout['texture_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();layout['font_sha256']=hashlib.sha256(font.read_bytes()).hexdigest();layout['generator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();(H/'graphic-layout-v1.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2)+'\n')
