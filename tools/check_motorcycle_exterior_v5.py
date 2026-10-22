"""Audit actual v5 delivery resources and visibility evidence, without accepting art or fit."""
import argparse
import hashlib
import json
from pathlib import Path

R=Path(__file__).resolve().parents[1]
O=R/'creative/reviews/motorcycle-exterior-v5'
P=R/'creative/research/motorcycle-exterior-v5'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
read=lambda p:json.loads((R/p).read_text())

def topology():
    gltf=read('assets-src/moto-components/motorcycle-exterior-v5.gltf')
    native=read('creative/reviews/motorcycle-exterior-v5/native-evaluated-bounds.json')
    plan=read('creative/research/motorcycle-exterior-v5/parents.json');changed={p['key']for p in plan['changes']}
    def count(i):
        node=gltf['nodes'][i]
        own=sum(gltf['accessors'][p['indices']]['count']//3 for p in gltf['meshes'][node['mesh']]['primitives'])if 'mesh'in node else 0
        return own+sum(count(c)for c in node.get('children',[]))
    exported={n['name'][8:-1]:count(i)for i,n in enumerate(gltf['nodes'])if n.get('name','').startswith('PARENT [')}
    rows=[{'key':p['key'],'native_triangles':p['triangles'],'exported_triangles':exported[p['key']],'changed_in_v5':p['key']in changed,'same_count':p['triangles']==exported[p['key']]}for p in native['parents']]
    assert all(p['same_count']for p in rows if p['changed_in_v5'])
    return {'parents':rows,'all_17_changed_source_export_counts_agree':True,'inherited_count_differences':[p for p in rows if not p['same_count']],'scope':'Native evaluated triangle counts and exact exported index counts. Equal counts are not per-vertex parity; inherited subdivision/triangulation/export differences remain explicit.'}

def audit():
    plan=read('creative/research/motorcycle-exterior-v5/parents.json')
    native=read('creative/reviews/motorcycle-exterior-v5/linked-parents-check.json')
    bounds=read('creative/research/motorcycle-exterior-v5/native-runtime-bounds-comparison.json')
    portable=read('creative/research/motorcycle-exterior-v5/portable-files.json')
    lod=read('assets-src/moto-components/motorcycle-exterior-v5/lod/build-report.json')
    comparison=read('creative/reviews/motorcycle-exterior-v5/comparison.json')
    assert len(plan['parents'])==plan['parent_count']==177
    assert len(plan['changes'])==17 and sum(x['action']=='add' for x in plan['changes'])==15
    assert native['parent_count']==177 and len(native['unchanged_parent_pose_checks'])==160
    assert native['source_sha256']==sha(R/native['source'])
    assert native['protocol_sha256']==sha(R/'tools/build_motorcycle_exterior_v5.py')
    assert all(p['sha256']==sha(R/p['source']) for p in plan['parents'])
    assert all(r['max_abs_world_bound_delta_m']<1e-5 for r in bounds['parents']) and len(bounds['parents'])==177
    for row in portable['files']:
        path=R/row['path'];assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],path
    assert lod['source_manifest_sha256']==sha(P/'portable-files.json')
    assert lod['tool_sha256']==sha(R/lod['tool'])
    assert lod['output_sha256']==sha(R/lod['output']) and lod['output_bytes']==(R/lod['output']).stat().st_size
    assert lod['gltf_validator']['numErrors']==0 and lod['serialized_parents']==177
    assert comparison['all_177_parents_isolated_and_visible'] and comparison['all_restored_matrices_exact']
    for path,digest in comparison['input_sha256'].items():assert sha(R/path)==digest,path
    for model,count in [('source',lod['before']['triangles']),('lod',lod['after']['triangles'])]:
        engine=read(f'creative/reviews/motorcycle-exterior-v5/{model}-engine-report.json')
        assert engine['groups']==177 and engine['triangles']==count
        assert not engine['page_errors'] and not engine['http_failures']
        for row in engine['files']:
            path=R/row['path'];assert sha(path)==row['sha256'] and path.stat().st_size==row['bytes'],path
        if model=='lod':
            assert len(engine['isolation_checks'])==177
            assert all(p['visible_mask_pixels']>20 and not p['edge_pixels'] and p['only_this_parent_enabled'] for p in engine['isolation_checks'])
            assert len(engine['renderable_visibility_checks'])==engine['meshes']==comparison['individually_checked_renderables']
            assert all(p['visible_mask_pixels']>0 and not p['edge_pixels'] and p['only_this_renderable_visible'] for p in engine['renderable_visibility_checks'])
    body=read('creative/reviews/fuel-tap-visible-body-v1/export-buffer-check.json')
    assert body['gltf_validator']['numErrors']==0 and body['native_triangle_counts_agree'] and len(body['parts'])==3
    body_folder=R/'assets-src/moto-components/fuel-tap-visible-body-v1'
    body_review=R/'creative/reviews/fuel-tap-visible-body-v1'
    assert body['sha256']==sha(body_folder/'child-candidate.glb')
    for phase in ['gray','candidate']:
        render=json.loads((body_review/f'{phase}-render-report.json').read_text())
        assert render['source_sha256']==sha(body_folder/f'child-{phase}.blend')
        assert render['export_sha256']==sha(body_folder/f'child-{phase}.glb')
        assert render['builder_sha256']==sha(R/'tools/build_fuel_tap_visible_body_v1.py')
        for view in render['views']:
            assert view['png_sha256']==sha(body_review/f'{view["view"]}.png')
            assert view['exr_sha256']==sha(body_review/'raw'/f'{view["view"]}.exr')
    context=read('creative/reviews/motorcycle-exterior-v5/context/report.json')
    assert len(context['files'])==17 and not context['page_errors'] and not context['http_failures']
    for path,digest in context['input_sha256'].items():assert sha(R/path)==digest,path
    for row in context['files']:assert row['sha256']==sha(R/row['path'])
    report={'schema':1,'date':'2026-10-22','current_assembly_parents':177,'individually_visible_renderables':comparison['individually_checked_renderables'],'added_parent_groups':15,'replaced_mirrors':2,'unchanged_parent_poses':160,'source_triangles':lod['before']['triangles'],'review_lod_triangles':lod['after']['triangles'],'review_lod_bytes':lod['output_bytes'],'all_parent_groups_individually_visible':True,'gltf_errors':0,'browser_errors':0,'http_failures':0,'blocked_visible_interfaces':plan['blocked_visible_interfaces'],'whole_motorcycle_complete':False,'art_accepted':False,'physical_iphone_tested':False,'game_integrated':False,'scope':'Current exterior appearance delivery. Visibility means an actual isolated canvas for every retained parent and renderable, not simultaneous visibility, complete vehicle manufacture, verified fitted interfaces or acceptance.'}
    return report

def files():
    folders=['assets-src/moto-components/fuel-tap-visible-body-v1','assets-src/moto-components/motorcycle-exterior-v5','creative/research/fuel-tap-visible-body-v1','creative/research/motorcycle-exterior-v5','creative/reviews/fuel-tap-visible-body-v1','creative/reviews/motorcycle-exterior-v5','tools/motorcycle-exterior-review-v5']
    paths={p for name in folders for p in (R/name).rglob('*') if p.is_file() and p.suffix not in {'.log','.blend1'}}
    paths.update(R/p for p in ['assets-src/moto-components/motorcycle-exterior-v5.gltf','assets-src/moto-components/motorcycle-exterior-v5.gltf.proof.json','tools/build_fuel_tap_visible_body_v1.py','tools/build_motorcycle_exterior_v5.py','tools/build_motorcycle_lod_v2.mjs','tools/prepare_motorcycle_exterior_v5.py','tools/render_motorcycle_exterior_v5.py','tools/capture_motorcycle_assembled_exterior_v5.py','tools/capture_motorcycle_exterior_context_v5.py','tools/check_fuel_tap_visible_body_v1.mjs','tools/check_motorcycle_exterior_v5.py','tools/probe_handlebar_mount_alignment_v1.mjs'])
    paths.discard(O/'production-manifest.json')
    return [{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(paths)]

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args();report=audit()
    if args.write:
        (O/'source-export-topology.json').write_text(json.dumps(topology(),indent=2)+'\n')
        (O/'completion-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        manifest={'schema':1,'scope':'New exterior-v5 delivery and child; historical files unchanged. Original dependencies additionally pinned by portable-files.json. Mutable repository entry pages are not frozen here.','files':files(),'art_accepted':False}
        (O/'production-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    else:
        stored=read('creative/reviews/motorcycle-exterior-v5/production-manifest.json')
        for row in stored['files']:
            path=R/row['path'];assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],path
        assert read('creative/reviews/motorcycle-exterior-v5/completion-report.json')==report
        assert read('creative/reviews/motorcycle-exterior-v5/source-export-topology.json')==topology()
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
