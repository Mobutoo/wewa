"""Prepare NEW moved test tree from static public Library graph plus additive replacements.
All paths are CLI arguments. Copies frozen ancestors byte-for-byte, never rewrites them.
"""
from pathlib import Path
import argparse,json,hashlib,shutil
p=argparse.ArgumentParser(description=__doc__)
for s in ['repository-root','dependency-report','replacement-map','test-root','report']:p.add_argument('--'+s,required=True)
a=p.parse_args();root=Path(a.repository_root).resolve();test=Path(a.test_root).resolve();assert not test.exists()and not test.is_relative_to(root);d=json.loads(Path(a.dependency_report).read_text());mapping=json.loads(Path(a.replacement_map).read_text());graph=d['context_library_closure']['files'];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rows=[]
for node in graph:
 rel=mapping.get(node['file'],node['file']);src=root/rel;assert src.is_file();dst=test/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert sha(src)==sha(dst);edges=[]
 for e in node['library_links']:edges.append(mapping.get(e['repo_path'],e['repo_path']))
 rows.append({'original_logical_source':node['file'],'source':rel,'sha256':sha(src),'expected_direct_link_targets':sorted(edges),'is_additive_companion':rel!=node['file']})
Path(a.report).write_text(json.dumps({'test_root':str(test),'repository_root':str(root),'files':rows,'dependency_report_sha256':sha(a.dependency_report),'replacement_map_sha256':sha(a.replacement_map),'tool_sha256':sha(__file__),'expected_direct_links':sum(len(r['expected_direct_link_targets'])for r in rows)},indent=2)+'\n');print('MOVED_CONTEXT_FILES',len(rows),'EXPECTED_DIRECT_LINKS',sum(len(r['expected_direct_link_targets'])for r in rows))
