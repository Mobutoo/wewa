"""Authorfield check: compact groove becomes exactly flat before rail medialaxis."""
from pathlib import Path
import json,numpy as np,hashlib,importlib.util
from profile_shape import shape,normal2,front_field
H=Path(__file__).resolve().parent;P=json.loads((H/'parameters.json').read_text());loops=shape(P);caps=[a-P['edge_radius_m_estimated']*normal2(a)for a in loops];p=np.array([[.100,.0175]]);e=1e-8
old=H/'diagnostics/profile-before-compact.py';spec=importlib.util.spec_from_file_location('slider_diagnostic_old_profile',old);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def slopes(fn):
 h=float(fn(p,caps)[0]);left=(h-float(fn(p-[0,e],caps)[0]))/e;right=(float(fn(p+[0,e],caps)[0])-h)/e;return{'height_m':h,'left_dX_dZ':left,'right_dX_dZ':right,'derivative_jump':right-left}
a=slopes(mod.front_field);b=slopes(front_field);assert abs(a['derivative_jump'])>.01 and b['height_m']==b['derivative_jump']==0
r={'diagnostic_source_sha256':'583a6d207a9e80b5d2e890fb09dab736cf04fb963bcc8f0b7497c038c9d6099e','old_profile_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'current_profile_sha256':hashlib.sha256((H/'profile_shape.py').read_bytes()).hexdigest(),'probe_YZ_m':p[0].tolist(),'finite_difference_step_m':e,'old_nearest_boundary_infinite_Gaussian':a,'current_C2_compact_support_before_medialaxis':b,'scope':'One actual planar rail medialaxis of authorfield, not global3D error/photographic certification. Render glints alone did not establish this defect; finite one-sided derivative demonstrates the previous construction cusp.','visible_tipmouths_still_unbuilt':True,'art_accepted':False};print(json.dumps(r,indent=2))
