#!/usr/bin/env python3
"""Non-metric G2 camera hypotheses for private official side-view references.

Run from repository root. Does not modify datums, annotations, assets or scenes.
Requires numpy, scipy, Pillow. Original photo pixels stay outside the repository.
The three guide points include estimated 3D positions, not surveyed controls.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
DATUM = ROOT / 'creative/workflow/motorcycle-datums-v1.json'
LANDMARKS = ROOT / 'creative/research/body-powertrain-18/profile-landmarks.json'
NAMES = ['front_axle', 'rear_axle', 'bar_clamp']
ANCHORS = ['front_axle_uv', 'rear_axle_uv', 'bar_clamp_uv']
WIDTH, HEIGHT = 1000, 700


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def frame(side, yaw=0., pitch=0., roll=0.):
    """Camera local columns: right, up, backward. side=-1 is R00."""
    horizontal = np.array([-side*np.cos(yaw), -side*np.sin(yaw), 0.])
    right = np.cross(horizontal, [0., 0., 1.])
    forward = horizontal*np.cos(pitch) + np.array([0., 0., np.sin(pitch)])
    up = np.cross(right, forward)
    return forward, right*np.cos(roll)+up*np.sin(roll), up*np.cos(roll)-right*np.sin(roll)


def transform_record(eye, forward, right, up):
    rotation = np.column_stack([right, up, -forward])
    quat = Rotation.from_matrix(rotation).as_quat()  # xyzw -> Blender wxyz
    return {'location_m': eye.tolist(), 'rotation_matrix_local_to_world': rotation.tolist(),
            'rotation_quaternion_wxyz': [float(quat[3]), *quat[:3].tolist()],
            'forward_world': forward.tolist(), 'up_world': up.tolist()}


def residual_record(projected, observed, sigma):
    delta = projected-observed
    return {'projected_uv_px': dict(zip(NAMES, projected.tolist())),
            'observed_uv_px': dict(zip(NAMES, observed.tolist())),
            'signed_residual_uv_px': dict(zip(NAMES, delta.tolist())),
            'euclidean_residual_px': dict(zip(NAMES, np.linalg.norm(delta, axis=1).tolist())),
            'unweighted_rms_coordinate_px': float(np.sqrt(np.mean(delta**2))),
            'max_absolute_normalised_reading_residual': float(np.max(np.abs(delta/sigma))),
            'normalisation_is': 'Manual image-reading intervals only; not a probabilistic camera-error or physical tolerance.'}


def orthographic(points, uv, side, sigma):
    forward, right, up = frame(side)
    # Axle baseline determines one image scale only. Height and bar offsets stay estimated.
    scale = abs(uv[1, 0]-uv[0, 0])/np.linalg.norm(points[1]-points[0])
    horizontal_constant = uv[0, 0]-scale*np.dot(points[0], right)
    vertical_constant = uv[0, 1]+scale*np.dot(points[0], up)
    target = right*((WIDTH/2-horizontal_constant)/scale) + up*((vertical_constant-HEIGHT/2)/scale)
    eye = target-4.*forward  # arbitrary orthographic distance, not recovered
    projected = np.column_stack([horizontal_constant+scale*(points@right), vertical_constant-scale*(points@up)])
    return {'kind': 'ORTHO', 'role': 'selected_working_camera_not_calibrated',
            **transform_record(eye, forward, right, up), 'target_m': target.tolist(),
            'ortho_scale_m': WIDTH/scale, 'ortho_scale_convention': 'Blender horizontal frame width, sensor_fit HORIZONTAL',
            'pixels_per_candidate_working_m': float(scale), 'distance_m': 4.,
            'distance_status': 'Arbitrary: orthographic distance is unobservable.',
            'fit': residual_record(projected, uv, sigma)}


def perspective_family(points, uv, side, sigma):
    centre = points.mean(axis=0)
    scale = abs(uv[1, 0]-uv[0, 0])/np.linalg.norm(points[1]-points[0])
    lo = np.array([-np.pi/9, -np.pi/12, -np.pi/36, 1.3, -1., -1.])
    hi = np.array([np.pi/9, np.pi/12, np.pi/36, 15., 1., 1.])
    records = []
    for lens in [35., 50., 85., 120.]:
        fpx = lens*WIDTH/36.

        def project(parameters):
            forward, right, up = frame(side, *parameters[:3])
            distance, x, y = parameters[3:]
            q = points-centre
            depth = distance+q@forward
            return np.column_stack([WIDTH/2+fpx*(q@right-x)/depth,
                                    HEIGHT/2-fpx*(q@up-y)/depth])

        init = [0., 0., 0., fpx/scale, -(uv[:, 0].mean()-WIDTH/2)/scale,
                (uv[:, 1].mean()-HEIGHT/2)/scale]
        trials = []
        for yaw in [-.15, 0., .15]:
            start = np.array(init); start[0] = yaw
            trials.append(least_squares(lambda p: ((project(p)-uv)/sigma).ravel(), start,
                                       bounds=(lo, hi), max_nfev=5000,
                                       xtol=1e-12, ftol=1e-12, gtol=1e-12))
        best = min(trials, key=lambda r: r.cost)
        forward, right, up = frame(side, *best.x[:3])
        distance, x, y = best.x[3:]
        eye = centre-distance*forward+x*right+y*up
        records.append({'kind': 'PERSP', 'role': 'bounded_alternative_not_selected_or_calibrated',
                        'lens_mm': lens, 'sensor_width_mm': 36., 'sensor_fit': 'HORIZONTAL',
                        'principal_point_px': [WIDTH/2, HEIGHT/2],
                        **transform_record(eye, forward, right, up),
                        'yaw_pitch_roll_working_degrees': np.rad2deg(best.x[:3]).tolist(),
                        'distance_to_working_guide_centroid_m': float(distance),
                        'active_parameter_bounds': [int(i) for i, v in enumerate(best.active_mask) if v],
                        'fit': residual_record(project(best.x), uv, sigma),
                        'optimisation_note': 'Best of three deterministic local starts; no global optimum or recovered true lens claimed.'})
    return {'bounds': {'yaw_deg': [-20, 20], 'pitch_deg': [-15, 15], 'roll_deg': [-5, 5],
                       'distance_to_guide_centroid_m': [1.3, 15.], 'lens_samples_mm': [35, 50, 85, 120],
                       'horizontal_vertical_camera_offset_m_each': [-1, 1],
                       'all_bounds_are': 'Declared exploration assumptions; no EXIF/camera measurement supports them.'},
            'hypotheses': records,
            'identifiability': 'Three non-collinear points provide six scalar image constraints. Free perspective pose plus unknown focal length has at least seven parameters; all three 3D controls also include estimated coordinates. Low residual cannot determine the true lens/pose or metric shape.'}


def guides_svg(view, camera, output):
    ns = 'http://www.w3.org/2000/svg'
    ET.register_namespace('', ns)
    svg = ET.Element(f'{{{ns}}}svg', width=str(WIDTH), height=str(HEIGHT), viewBox='0 0 1000 700')
    ET.SubElement(svg, 'desc').text = 'Transparent image-space annotations and projected guide points only. No documentary photograph pixels. Overlay on original unscaled1000x700 raster.'
    assert view.get('segments'), 'Expected existing open profile segments'
    for poly in view['segments']:
        points = [view['points'][ident]['uv_px'] for ident in poly['point_ids']]
        ET.SubElement(svg, 'polyline', points=' '.join(f'{u},{v}' for u, v in points), fill='none', stroke='#00cbd4', **{'stroke-width': '1', 'opacity': '.7'})
    observed = camera['fit']['observed_uv_px']; predicted = camera['fit']['projected_uv_px']
    ET.SubElement(svg, 'line', x1=str(predicted['front_axle'][0]), y1=str(predicted['front_axle'][1]),
                  x2=str(predicted['rear_axle'][0]), y2=str(predicted['rear_axle'][1]), stroke='#ffbe22', **{'stroke-width': '2'})
    for ident in NAMES:
        u, v = observed[ident]; x, y = predicted[ident]; uncertainty = 12 if ident == 'bar_clamp' else 5
        ET.SubElement(svg, 'rect', x=str(u-uncertainty), y=str(v-uncertainty), width=str(uncertainty*2), height=str(uncertainty*2), fill='none', stroke='#34e996')
        ET.SubElement(svg, 'circle', cx=str(x), cy=str(y), r='4', fill='#ffbe22')
        ET.SubElement(svg, 'line', x1=str(u), y1=str(v), x2=str(x), y2=str(y), stroke='#ff4444', **{'stroke-width': '2'})
        ET.SubElement(svg, 'text', x=str(x+8), y=str(y-10), fill='#d47f00', **{'font-size': '12'}).text = ident
    ET.ElementTree(svg).write(output, encoding='unicode', xml_declaration=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, default=ROOT/'creative/research/reference-camera-studies')
    ap.add_argument('--private-previews', type=Path, default=Path('/tmp/viva-wewa-reference-camera-studies'))
    args = ap.parse_args(); args.output.mkdir(parents=True, exist_ok=True); args.private_previews.mkdir(parents=True, exist_ok=True)
    datum = json.loads(DATUM.read_text()); landmarks = json.loads(LANDMARKS.read_text())
    points = np.array([datum['provisional_guides_m']['front_axle'], datum['provisional_guides_m']['rear_axle'], [0., 0., 0.]])
    report = {'schema': 'wewa.reference-camera-study.v1', 'stage': 'G2_preparation_reserved',
              'camera_calibrated': False, 'physical_part_dimensions_measured': False, 'G2_passed': False,
              'inputs': [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p)} for p in [DATUM, LANDMARKS]],
              'script_sha256': sha(__file__), 'guides_world_m_unchanged': dict(zip(NAMES, points.tolist())),
              'guide_status': 'Only wheelbase is a published constraint. Guide origin/axle locations and bar relation remain estimates.',
              'raster': {'width': WIDTH, 'height': HEIGHT, 'pixel_origin': 'top-left', 'pixel_aspect': 1.},
              'tyres_used_for_fit': False, 'tyre_note': 'No provisional tyre radius, outside tyre envelope or assumption of equal apparent wheel sizes is used. Different apparent sizes may involve depth/perspective, different tyres, cutout/resampling or view error.',
              'profile_annotation_use': 'Tank/seat open contours copied only as image overlays. They have no world points and are not optimisation constraints or hidden sections.',
              'views': []}
    for i, side in [(0, -1), (1, 1)]:
        annotation = datum['side_reference_annotations'][i]; view = landmarks['views'][i]
        uv = np.array([annotation['annotations_pixels'][k] for k in ANCHORS], dtype=float)
        sigma = np.array([[5., 5.], [5., 5.], [12., 12.]])
        ref = Path(annotation['private_reference']); assert sha(ref) == annotation['sha256']
        selected = orthographic(points, uv, side, sigma)
        record = {'id': view['id'], 'reference_private_path': str(ref), 'reference_sha256': sha(ref),
                  'visible_side': view['visible_bike_side'], 'reading_uncertainty_uv_px': dict(zip(NAMES, sigma.tolist())),
                  'selected_working_camera': selected, 'perspective_comparison': perspective_family(points, uv, side, sigma),
                  'photo_projection_test': 'Not a calibrated photograph. Keep all residuals, especially R04 clamp, visible when comparing geometry.'}
        record['working_camera_limits'] = ('Near-zeroR00 residual is not independent validation: the original guide positions were already based on this view.' if i == 0 else
                                         'R04 clamp residual exceeds the12px reading interval on at least one coordinate. It remains visible; do not deform assets or move frozen datums to force agreement.')
        record['open_profile_segment_count'] = len(view['segments'])
        guides_svg(view, selected, args.output/(view['id']+'-working-guides.svg'))
        # Private derivative, never a distributable game texture or repository photo copy.
        im = Image.open(ref).convert('RGB'); draw = ImageDraw.Draw(im)
        for ident in NAMES:
            u, v = uv[NAMES.index(ident)]; x, y = selected['fit']['projected_uv_px'][ident]
            e = 12 if ident == 'bar_clamp' else 5
            draw.rectangle((u-e, v-e, u+e, v+e), outline='#34e996', width=1)
            draw.line((u, v, x, y), fill='#ff4444', width=2); draw.ellipse((x-4, y-4, x+4, y+4), outline='#ffbe22', width=2)
        private_path = args.private_previews/(view['id']+'-working-guide-overlay.png'); im.save(private_path)
        record['private_preview'] = {'path': str(private_path), 'sha256': sha(private_path), 'redistribute': False}
        report['views'].append(record)
    report['use_rules'] = ['Use selected ORTHO cameras only as repeatable profile working views, not as source-camera identification.',
                           'Do not alter frozen axle/bar guides or deform an asset to absorb R04 bar-clamp residual.',
                           'Do not recover part dimensions or hidden coordinates by inverting either camera.',
                           'Perspective alternatives demonstrate camera/guide ambiguity. No best residual is a physical calibration.',
                           'For a future measured reconstruction obtain surveyed correspondences at multiple depths, camera metadata/targets and views of actual hidden interfaces.']
    (args.output/'camera-studies.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
    cameras = json.loads(json.dumps([{'name': 'WEWA_STUDY_'+v['id'], **v['selected_working_camera']} for v in report['views']]))
    setup = '''# Generated explicit working cameras only; no model mutation or saving.\nimport bpy\nfrom mathutils import Quaternion\nCAMERAS = '''+repr(cameras)+'''\nscene = bpy.context.scene\nscene.render.resolution_x = 1000\nscene.render.resolution_y = 700\nscene.render.resolution_percentage = 100\nscene.render.pixel_aspect_x = scene.render.pixel_aspect_y = 1\nfor spec in CAMERAS:\n data = bpy.data.cameras.new(spec['name'])\n data.type = 'ORTHO'\n data.sensor_fit = 'HORIZONTAL'\n data.ortho_scale = spec['ortho_scale_m']\n data.clip_start = .01\n data.clip_end = 100\n ob = bpy.data.objects.new(spec['name'], data)\n scene.collection.objects.link(ob)\n ob.location = spec['location_m']\n ob.rotation_mode = 'QUATERNION'\n ob.rotation_quaternion = Quaternion(spec['rotation_quaternion_wxyz'])\n if scene.camera is None:\n  scene.camera = ob\n'''
    (args.output/'create-working-cameras.blender.py').write_text(setup)
    check = '''# Run in an empty Blender process; no rendering or saving.\nimport bpy, json\nfrom pathlib import Path\nfrom mathutils import Vector\nfrom bpy_extras.object_utils import world_to_camera_view\nBASE = Path('''+repr(str(args.output))+''')\nexec((BASE/'create-working-cameras.blender.py').read_text())\nreport = json.loads((BASE/'camera-studies.json').read_text())\nbpy.context.view_layer.update()\nrows = []\nfor view in report['views']:\n cam = bpy.data.objects['WEWA_STUDY_'+view['id']]\n actual = {}\n differences = {}\n for name, point in report['guides_world_m_unchanged'].items():\n  uv = world_to_camera_view(bpy.context.scene, cam, Vector(point))\n  actual[name] = [float(uv.x*1000), float((1-uv.y)*700)]\n  expected = view['selected_working_camera']['fit']['projected_uv_px'][name]\n  differences[name] = [actual[name][i]-expected[i] for i in range(2)]\n assert max(abs(d) for pair in differences.values() for d in pair) < .001, differences\n rows.append({'id': view['id'], 'actual_blender_projection_px': actual, 'blender_minus_numpy_uv_px': differences})\nresult = {'blender': bpy.app.version_string, 'threads': 1, 'render_executed': False, 'existing_source_opened_or_modified': False, 'camera_calibrated': False, 'scope': 'Independent Blender projection matches explicit working-camera equations within0.001px; no photograph/metric calibration implied.', 'views': rows}\n(BASE/'blender-projection-check.json').write_text(json.dumps(result, indent=2)+'\\n')\nprint(json.dumps(result))\n'''
    (args.output/'check-working-cameras.blender.py').write_text(check)
    print(json.dumps({'output': str(args.output), 'working_cameras': [{'id': v['id'], 'residuals': v['selected_working_camera']['fit']['signed_residual_uv_px']} for v in report['views']]}, indent=2))


if __name__ == '__main__':
    main()
