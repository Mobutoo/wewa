"""Fixed two-camera sun/shadow experiment. PREPARED ONLY; run explicitly on a served repository.

Imports frozen lab v2 in the browser; never imports v3/SSAO. No composites, source writes,
parameter search or material adjustment. Failure evidence is retained in a new output folder.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
LAB = 'tools/motorcycle-material-camera-lab-v4'
CONFIG_PATH = ROOT / LAB / 'configuration.json'
SHA = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
WRITE = lambda path, value: Path(path).write_text(json.dumps(value, indent=2) + '\n')
SNAPSHOT_KEYS = [
    'geometry_normals_allUV_tangents_indices_matrices_assignments_sha256',
    'materials_serialized_sha256', 'materials_semantic_sha256', 'camera_HDR_processing_sha256']
ORIENTATION = 'creative/research/upper-engine-environment-diagnostic-v1/report.json'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def pixel_delta(image_a, image_b):
    """Compare actual decoded canvas PNG bytes; never write a merged image."""
    a, b = Image.open(image_a).convert('RGBA'), Image.open(image_b).convert('RGBA')
    require(a.size == b.size, 'Comparison dimensions differ')
    diff = ImageChops.difference(a, b)
    nonzero = sum(any(px) for px in diff.getdata())
    return {'same_dimensions': True, 'changed_RGBA_pixels': nonzero,
            'max_channel_difference': max(v[1] for v in diff.getextrema()),
            'decoded_RGBA_equal': a.tobytes() == b.tobytes()}


def capture_page(page, destination, config, expected_spec, state_name=None):
    page.evaluate('window.__MATERIAL_CAMERA_REVIEW__.engine.stopRenderLoop()')
    if state_name:
        page.evaluate('(name)=>window.__MATERIAL_CAMERA_REVIEW__.prepareState(name)', state_name)
    else:
        page.evaluate('''async()=>{const {scene,engine}=window.__MATERIAL_CAMERA_REVIEW__;
          engine.resize();await scene.whenReadyAsync();
          for(let i=0;i<4;i++){await new Promise(requestAnimationFrame);scene.render();}}''')
    pixel = page.evaluate('''async()=>{const {engine,scene}=window.__MATERIAL_CAMERA_REVIEW__;
      scene.render();const width=engine.getRenderWidth(),height=engine.getRenderHeight();
      const p=await engine.readPixels(0,0,width,height),bg=Array.from(p.slice(0,3));let changed=0;
      for(let i=0;i<p.length;i+=4)if(Math.max(...[0,1,2].map(k=>Math.abs(p[i+k]-bg[k])))>8)changed++;
      const bytes=new Uint8Array(p.buffer,p.byteOffset,p.byteLength);
      const sha=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
      return {width,height,background_rgb:bg,changed_pixels:changed,changed_fraction:changed/(width*height),raw_RGBA_sha256:sha};}''')
    state = page.evaluate('window.__MATERIAL_CAMERA_REVIEW__.report()')
    require(state['spec'] == expected_spec, 'HTTP camera spec differs from pinned disk specification')
    snapshot = page.evaluate('''async()=>{const m=await import('/tools/motorcycle-material-camera-lab-v4/conservation.js');
      return m.snapshot(window.__MATERIAL_CAMERA_REVIEW__);}''')
    page.locator('canvas').screenshot(path=str(destination))
    image = Image.open(destination).convert('RGBA')
    require(image.size == (1000, 750), 'Unexpected actual PNG resolution')
    rgb = image.convert('RGB'); background = rgb.getpixel((0, 0))
    changed = sum(max(abs(v[k]-background[k]) for k in range(3)) > 8 for v in rgb.getdata())
    pixel['PNG_decoded_changed_pixels'] = changed
    require(pixel['width'] == 1000 and pixel['height'] == 750, 'Unexpected canvas resolution')
    require(pixel['changed_pixels'] > 100 and pixel['changed_fraction'] > .0001 and changed > 100,
            'Empty or near-empty actual canvas')
    witnesses = state['projection_witnesses']
    require(len(witnesses) == 8 and max(w['pixel_difference'] for w in witnesses) < .05,
            'Same-camera software projection mismatch')
    require(state['meshes'] == config['expected_runtime_meshes'] and
            state['drawn_triangles'] == config['expected_triangles'], 'Runtime inventory mismatch')
    require(state['actual_environment_rotation_y_radians'] == config['rotation_y_radians'], 'HDR rotation changed')
    require(state['actual_environment_intensity'] == .3 and
            state['actual_exposure'] == 2**state['spec']['exposure_EV'], 'HDR/exposure changed')
    require(snapshot['mesh_count'] == 14 and snapshot['triangles'] == 657316, 'Snapshot inventory mismatch')
    require(not state.get('pipelines'), 'Unexpected postprocess pipeline')
    state.update(actual_canvas=pixel, PNG=str(destination.relative_to(ROOT)), PNG_sha256=SHA(destination),
                 projection_max_pixel_difference=max(w['pixel_difference'] for w in witnesses),
                 runtime_snapshot=snapshot, art_accepted=False, physical_iphone_tested=False)
    return state


def verify_shadow_pair(w0, w1, config):
    for key in SNAPSHOT_KEYS:
        require(w0['runtime_snapshot'][key] == w1['runtime_snapshot'][key], 'W0/W1 content changed: '+key)
    require(w0['shadow'] == w1['shadow'], 'Shadow configuration/casters/receivers changed')
    require(w0['scene_shadows_enabled'] and w1['scene_shadows_enabled'], 'Global shadow switch changed')
    require(len(w0['lights']) == len(w1['lights']) == 1, 'Unexpected light/fill')
    for state in [w0, w1]:
        light = state['lights'][0]
        require(light['enabled'] and light['type'] == 'DirectionalLight', 'Missing fixed directional sun')
        require(light['direction'] == config['direction_gltf'] and
                light['diffuse_linear_rgb'] == light['specular_linear_rgb'] == config['color_linear_rgb'] and
                light['intensity'] == 1.5, 'Sun parameters changed')
        shadow = state['shadow']
        require(shadow['map_size'] == {'width': 2048, 'height': 2048}, 'Wrong shadow map')
        require(shadow['use_PCF'] and shadow['filter'] == 6 and shadow['filtering_quality'] == 1, 'PCF changed/fallback')
        require(shadow['generator_projection_matrix'] == shadow['light_projection_matrix'],
                'Shadow generator did not use the derived fixed projection')
        require(shadow['normal_bias_world_m'] == 1e-4 and shadow['requested_depth_bias_m'] == 2e-5,
                'Fixed bias changed')
        require(len(shadow['casters']) == len(shadow['receivers']) == 14, 'Incomplete caster/receiver list')
        require(shadow['casters'] == shadow['receivers'], 'Caster/receiver inventory differs')
        require(shadow['frustum']['near'] > 0 and shadow['frustum']['far'] > shadow['frustum']['near'],
                'Invalid derived shadow depth')
    light0, light1 = dict(w0['lights'][0]), dict(w1['lights'][0])
    require(light0.pop('shadow_enabled') is False and light1.pop('shadow_enabled') is True,
            'W0/W1 shadow switch incorrect')
    require(light0 == light1, 'The direct sun changed between W0 and W1')
    return {key: True for key in SNAPSHOT_KEYS} | {'same_light_except_shadow_enabled': True,
        'same_casters_receivers_and_fixed_shadow_parameters': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='New directory under creative/reviews; never overwritten')
    parser.add_argument('--port', type=int, default=4143, help='Existing repository Vite server; none is started')
    args = parser.parse_args()
    out = args.output.resolve()
    require(out.is_relative_to(ROOT / 'creative/reviews') and not out.exists(), 'Use a new repository review directory')
    config = json.loads(CONFIG_PATH.read_text())
    require(json.loads((ROOT/'node_modules/@babylonjs/core/package.json').read_text())['version'] == '9.31.0',
            'Babylon version differs from the checked API')
    inputs = {row['path']: row['sha256'] for row in config['protected_inputs'] + config['installed_API_references']}
    for path in [Path(__file__).resolve(), CONFIG_PATH, ROOT/LAB/'index.html', ROOT/LAB/'review.js', ROOT/LAB/'conservation.js',
                 ROOT/'node_modules/@babylonjs/core/package.json', ROOT/'node_modules/@babylonjs/loaders/package.json']:
        inputs[str(path.relative_to(ROOT))] = SHA(path)
    cameras = {}
    for name, record in config['camera_specs'].items():
        spec = json.loads((ROOT/record['path']).read_text())
        require(spec['schema'] == 'wewa.material-camera-comparison.v1' and spec['resolution_px'] == [1000, 750], 'Camera spec differs')
        for key in ['source', 'export', 'HDR', 'native_spec', 'native_report', 'native_neutral_PNG', 'tool']:
            require(SHA(ROOT/spec[key]) == spec[key+'_sha256'], 'Camera input changed: '+key)
            inputs[spec[key]] = spec[key+'_sha256']
        prefix = 'creative/reviews/upper-engine-material-lighting-' + ('v1' if name == 'front' else 'opposite-v1')
        warm, checkpoint_path = prefix+'/warm-late-day.png', prefix+'/warm-late-day-checkpoint.json'
        checkpoint = json.loads((ROOT/checkpoint_path).read_text())
        require(checkpoint['PNG_sha256'] == SHA(ROOT/warm) and checkpoint['source_sha256'] == spec['source_sha256'] and
                checkpoint['export_sha256'] == spec['export_sha256'], 'Warm Blender checkpoint mismatch')
        cameras[name] = {'camera_spec':record, 'spec':spec, 'warm_Blender_PNG':warm,
                         'warm_Blender_PNG_sha256':SHA(ROOT/warm), 'warm_Blender_checkpoint':checkpoint_path,
                         'warm_Blender_checkpoint_sha256':SHA(ROOT/checkpoint_path)}
    require(all(SHA(ROOT/path) == digest for path, digest in inputs.items()), 'Pinned input changed before capture')
    out.mkdir(parents=True)
    report = {'schema':'wewa.sun-shadow-capture.v4', 'status':'running', 'input_hashes':inputs,
              'fixed_configuration':config, 'cameras':{}, 'orientation_report':ORIENTATION,
              'runtime_claim':'Experimental desktop software Chromium only; no adoption/material parity/physical iPhone qualification.',
              'public_game_unchanged':True, 'art_accepted':False, 'physical_iphone_tested':False}
    WRITE(out/'conservation-report.json', report)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=[
                '--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
            for camera_name, camera in cameras.items():
                folder = out/camera_name; folder.mkdir()
                errors, failures = [], []
                states = {}
                query = urlencode({'spec':'/'+camera['camera_spec']['path'], 'rotation_y':config['rotation_y_radians']})
                for version in ['v2', 'v4']:
                    page = browser.new_page(viewport={'width':1000,'height':750}, device_scale_factor=1)
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.on('response', lambda response: failures.append({'url':response.url,'status':response.status})
                            if response.status >= 400 else None)
                    page.goto(f'http://127.0.0.1:{args.port}/tools/motorcycle-material-camera-lab-{version}/?'+query,
                              wait_until='networkidle', timeout=120000)
                    ready = 'sun_shadow_variant_ready' if version == 'v4' else 'orientation_variant_ready'
                    page.wait_for_function(f'window.__MATERIAL_CAMERA_REVIEW__?.{ready} && window.__MATERIAL_CAMERA_REVIEW__.scene.isReady() && window.__MATERIAL_CAMERA_REVIEW__.report().textures_ready', timeout=120000)
                    for key in ['export','HDR']:
                        response = page.request.get(f'http://127.0.0.1:{args.port}/'+camera['spec'][key])
                        require(response.ok and hashlib.sha256(response.body()).hexdigest() == camera['spec'][key+'_sha256'],
                                'HTTP '+key+' differs from pinned bytes')
                    neutral_name = 'neutral-'+version
                    states[neutral_name] = capture_page(page, folder/(neutral_name+'.png'), config, camera['spec'],
                                                       'neutral' if version == 'v4' else None)
                    WRITE(folder/(neutral_name+'-engine-check.json'), states[neutral_name])
                    if version == 'v4':
                        # Compare actual fresh controls before enabling the experimental sun.
                        pair = pixel_delta(folder/'neutral-v2.png', folder/'neutral-v4.png')
                        WRITE(folder/'neutral-control-comparison.json', pair)
                        require(pair['decoded_RGBA_equal'] and
                                states['neutral-v2']['actual_canvas']['raw_RGBA_sha256'] == states['neutral-v4']['actual_canvas']['raw_RGBA_sha256'],
                                'Fresh v2/v4 neutral controls are not exactly equal; no adoption or warm capture')
                        for key in [SNAPSHOT_KEYS[0], 'materials_semantic_sha256', 'camera_HDR_processing_sha256']:
                            require(states['neutral-v2']['runtime_snapshot'][key] == states['neutral-v4']['runtime_snapshot'][key],
                                    'Fresh neutral scene content differs: '+key)
                        require(not any(l['enabled'] for l in states['neutral-v4']['lights']), 'Neutral control has an active lamp')
                        for state in ['W0','W1']:
                            states[state] = capture_page(page, folder/(state+'.png'), config, camera['spec'], state)
                            WRITE(folder/(state+'-engine-check.json'), states[state])
                    page.close()
                require(not errors and not failures, str({'page_errors':errors,'http_failures':failures}))
                conservation = verify_shadow_pair(states['W0'], states['W1'], config)
                shadow_delta = pixel_delta(folder/'W0.png', folder/'W1.png')
                require(shadow_delta['changed_RGBA_pixels'] > 0, 'W1 has no measured shadow effect; inspect, do not retune')
                camera_report = {'references':camera, 'neutral_control':pair, 'W0_W1_conservation':conservation,
                                 'W0_W1_pixel_difference':shadow_delta, 'states':{k:{'report':str((folder/(k+'-engine-check.json')).relative_to(ROOT)),
                                 'report_sha256':SHA(folder/(k+'-engine-check.json')), 'PNG':v['PNG'], 'PNG_sha256':v['PNG_sha256']} for k,v in states.items()},
                                 'page_errors':errors,'http_failures':failures,'HTTP_export_HDR_bytes_verified':True}
                WRITE(folder/'comparison.json', camera_report)
                report['cameras'][camera_name] = camera_report
                WRITE(out/'conservation-report.json', report)
            browser.close()
        report['status'] = 'checks-passed-pending-human-review'
    except Exception as error:
        report['status'] = 'failed-no-adoption'
        report['failure'] = str(error)
        raise
    finally:
        report['protected_input_hashes_unchanged'] = {path:SHA(ROOT/path) == digest for path,digest in inputs.items()}
        if not all(report['protected_input_hashes_unchanged'].values()):
            report['status'] = 'failed-protected-input-change'
        WRITE(out/'conservation-report.json', report)
    require(report['status'] == 'checks-passed-pending-human-review', report['status'])
    print(json.dumps({'output':str(out),'status':report['status'],'camera_count':len(report['cameras']),
                      'canvas_PNG_count':8,'art_accepted':False}))


if __name__ == '__main__':
    main()
