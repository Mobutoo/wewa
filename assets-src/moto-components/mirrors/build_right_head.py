import sys,json,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[2];review=json.loads((root/'creative/reviews/mirror-right-v1/shell-preview-review.json').read_text());assert review['read_by_agent']and review['passed_for_head_construction']and review['source_sha256']==hashlib.sha256((p/'mirror-right-shell-study-v1.blend').read_bytes()).hexdigest()
sys.path.insert(0,str(p))
from mirror_builder_right_v1 import build
build('right','head')
