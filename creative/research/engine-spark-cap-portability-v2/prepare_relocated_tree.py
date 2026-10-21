"""Copy one portable companion and its actually linked public BLEND dependencies into a NEW tree.
No source mutation; hash each copied file. For execution use ordinary Python, not Blender.
"""
from pathlib import Path
import argparse,json,hashlib,shutil
p=argparse.ArgumentParser(description=__doc__)
for s in ['baseline-report','repository-root','test-root','report']:p.add_argument('--'+s,required=True)
p.add_argument('--use-original-source',action='store_true',help='Prepare a separate moved working tree with the frozen original rather than its portable companion, for generic tool replay.')
a=p.parse_args();b=json.loads(Path(a.baseline_report).read_text());root=Path(a.repository_root).resolve();test=Path(a.test_root).resolve();assert not test.exists()and not test.is_relative_to(root);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();sources=[(Path(b['source']if a.use_original_source else b['output']),b['source_sha256']if a.use_original_source else b['output_sha256'])]+[(root/r['target_repo_relative'],r['target_sha256'])for r in b['remaps']];rows=[]
for src,expected in sources:
 src=src.resolve();assert src.is_relative_to(root)and sha(src)==expected;rel=src.relative_to(root);dst=test/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert sha(dst)==expected;rows.append({'repo_relative':str(rel),'sha256':expected,'test_target':str(dst)})
Path(a.report).write_text(json.dumps({'test_root':str(test),'files':rows,'scope':'Companion plus actual linked BLENDs only. Does not claim a complete game checkout or mutate original BLENDs.'},indent=2)+'\n');print('MOVED_TREE_FILES',len(rows))
