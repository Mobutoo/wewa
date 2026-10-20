#!/usr/bin/env python3
"""Acquire a bounded, licensed source library; NEVER writes app/public or changes gameplay.

python3 tools/collect_art_library.py --out /workspace/wewa-asset-library
python3 tools/collect_art_library.py --out /workspace/wewa-asset-library --verify
python3 tools/collect_art_library.py --out /workspace/wewa-asset-library --restore

Raw sources stay outside the web bundle. The committed manifest records URLs, provider
checksums, local SHA-256, licenses, intended use, and unverified local suitability.
API metadata is cached for reproducible/resumable acquisition. No credentials required.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path, PurePosixPath
import re
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'creative/library'
HEADERS = {'User-Agent': 'Mozilla/5.0 (VivaWewa art-reference research)'}


def fetch(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60) as response:
                return response.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1 + attempt)


def safe_path(base, relative):
    p = PurePosixPath(relative)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError(f'Unsafe provider path: {relative}')
    return base.joinpath(*p.parts)


def acquire(base, relative, descriptor):
    target = safe_path(base, relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = target.read_bytes() if target.exists() else fetch(descriptor['url'])
    expected = descriptor.get('md5')
    if expected and hashlib.md5(data).hexdigest() != expected:
        raise ValueError(f'Provider checksum mismatch: {target}')
    if descriptor.get('size') is not None and len(data) != descriptor['size']:
        raise ValueError(f'Provider size mismatch: {target}')
    if not target.exists():
        temporary = target.with_name(target.name + '.part')
        temporary.write_bytes(data)
        temporary.replace(target)
    return {'path': relative, 'url': descriptor['url'], 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest(), 'provider_md5': expected}


def metadata(out, name, url):
    p = out / 'metadata' / (name + '.json')
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(fetch(url))
    return json.loads(p.read_text())


def text_field(value):
    return html.unescape(re.sub('<[^>]*>', '', value or '')).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--restore', action='store_true', help='Restore the exact committed manifest without searching again')
    parser.add_argument('--curate', action='store_true', help='Apply documented exclusions and review notes without network access')
    args = parser.parse_args()
    out = args.out.resolve()
    if out.is_relative_to(ROOT / 'app'):
        raise ValueError('Raw library must remain outside app/, including app/public/.')
    if args.curate:
        report = json.loads((CATALOG / 'manifest.json').read_text())
        selection = json.loads((CATALOG / 'selection.json').read_text())
        notes = json.loads((CATALOG / 'curation.json').read_text()).get('review_notes', {})
        excluded = selection.get('excluded_reference_ids', {})
        report['assets'] = [e for e in report['assets'] if not (e['id'].startswith('commons:') and e['id'].split(':')[1] in excluded)]
        report['excluded_reference_ids'] = excluded
        for entry in report['assets']:
            if entry['id'] in notes:
                entry['review_note'] = notes[entry['id']]
        entries = report['assets']
        report['summary'] = {'assets': len(entries), 'files': sum(len(e['files']) for e in entries),
                             'bytes': sum(f['bytes'] for e in entries for f in e['files']),
                             'materials': sum(e['kind'] == 'material' for e in entries),
                             'models': sum(e['kind'] == 'model' for e in entries),
                             'references': sum(e['kind'] == 'reference_photo' for e in entries)}
        (CATALOG / 'manifest.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
        print(json.dumps(report['summary']))
        return
    if args.restore:
        report = json.loads((CATALOG / 'manifest.json').read_text())
        for entry in report['assets']:
            for f in entry['files']:
                restored = acquire(out, f['path'], {'url': f['url'], 'size': f['bytes'], 'md5': f.get('provider_md5')})
                if restored['sha256'] != f['sha256']:
                    raise ValueError(f'SHA-256 differs from pinned manifest: {f["path"]}')
        print('Exact pinned source manifest restored and verified.')
        return
    if args.verify:
        report = json.loads((CATALOG / 'manifest.json').read_text())
        count = 0
        for entry in report['assets']:
            for f in entry['files']:
                data = safe_path(out, f['path']).read_bytes()
                if len(data) != f['bytes'] or hashlib.sha256(data).hexdigest() != f['sha256']:
                    raise ValueError(f'Local integrity mismatch: {f["path"]}')
                count += 1
        print(json.dumps({'verified_files': count, 'assets': len(report['assets']), 'result': 'passed'}))
        return
    selection = json.loads((CATALOG / 'selection.json').read_text())
    catalogs = {kind: metadata(out, f'polyhaven-{kind}', f'https://api.polyhaven.com/assets?t={kind}')
                for kind in ['textures', 'models']}
    entries, errors = [], []

    def poly_asset(job):
        kind, asset_id, intended = job
        catalog = catalogs['textures' if kind == 'material' else 'models'][asset_id]
        data = metadata(out, 'polyhaven-files-' + asset_id, 'https://api.polyhaven.com/files/' + asset_id)
        prefix = f'polyhaven/{kind}/{asset_id}'
        entry = {'id': 'ph:' + asset_id, 'provider': 'Poly Haven', 'kind': kind,
                 'source': 'https://polyhaven.com/a/' + asset_id, 'license': 'CC0-1.0',
                 'license_url': 'https://polyhaven.com/license', 'authors': catalog.get('authors'),
                 'provider_dimensions_mm': catalog.get('dimensions'),
                 'provider_polycount_not_runtime_budget': catalog.get('polycount'),
                 'intended_use': intended, 'status': 'downloaded_not_integrated',
                 'local_suitability': 'candidate_requires_visual_and_Kinshasa_review', 'files': []}
        if kind == 'model':
            variants = data.get('gltf', {})
            resolution = selection['model_resolution']
            if resolution not in variants:
                raise ValueError(f'{asset_id}: no {resolution} glTF source')
            mainfile = variants[resolution]['gltf']
            name = urllib.parse.urlparse(mainfile['url']).path.rsplit('/', 1)[-1]
            entry['files'].append(acquire(out, prefix + '/' + name, mainfile))
            for relative, desc in mainfile.get('include', {}).items():
                entry['files'].append(acquire(out, prefix + '/' + relative, desc))
        else:
            aliases = {'albedo': ['diff', 'Diffuse'], 'normal_opengl': ['nor_gl'],
                       'roughness': ['rough', 'Rough'], 'metalness': ['metal', 'Metal']}
            for channel, options in aliases.items():
                found = next((data[k] for k in options if k in data), {})
                maps = found.get(selection['material_resolution'], {})
                desc = maps.get('png') if channel == 'metalness' else maps.get('jpg')
                desc = desc or maps.get('jpg') or maps.get('png')
                if not desc:
                    if channel == 'metalness':
                        continue
                    raise ValueError(f'{asset_id}: missing {channel}')
                name = urllib.parse.urlparse(desc['url']).path.rsplit('/', 1)[-1]
                f = acquire(out, prefix + '/' + name, desc)
                f['channel'] = channel
                entry['files'].append(f)
        # Provider previews are asset renders, NEVER screenshots of Viva Wewa.
        thumb = catalog.get('thumbnail_url')
        if thumb:
            thumb_file = CATALOG / 'previews' / (asset_id + '.webp')
            thumb_file.parent.mkdir(exist_ok=True)
            if not thumb_file.exists():
                thumb_file.write_bytes(fetch(thumb))
            entry['provider_preview'] = 'previews/' + thumb_file.name
        return entry

    jobs = [('material', k, v) for k, v in selection['materials'].items()]
    jobs += [('model', k, v) for k, v in selection['models'].items()]
    # Small bound; do not turn research into an unbounded scrape.
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [(job, pool.submit(poly_asset, job)) for job in jobs]
        for job, future in futures:
            try:
                entry = future.result()
                entries.append(entry)
                print(job[0], job[1], sum(f['bytes'] for f in entry['files']), flush=True)
            except Exception as exc:
                errors.append({'id': job[1], 'error': str(exc)})
                print('FAILED', job[1], str(exc), flush=True)

    titles_seen = set()
    searches = [('supplement', None)] + list(selection['commons_searches'].items())
    for category, query in searches:
        params = {'action': 'query', 'format': 'json', 'generator': 'search', 'gsrsearch': query,
                  'gsrnamespace': 6, 'gsrlimit': 6, 'prop': 'imageinfo',
                  'iiprop': 'url|extmetadata|size|sha1', 'iiurlwidth': 1200}
        if category == 'supplement':
            params = {k: v for k, v in params.items() if k not in ['generator', 'gsrsearch', 'gsrnamespace', 'gsrlimit']}
            params['titles'] = '|'.join(selection['commons_titles'])
        try:
            response = metadata(out, 'commons-' + category, 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params))
            pages = response.get('query', {}).get('pages', {}).values()
            for page in pages:
                title = page['title']
                if title in titles_seen:
                    continue
                titles_seen.add(title)
                if str(page['pageid']) in selection.get('excluded_reference_ids', {}):
                    continue
                if not re.search(r'\.(jpg|jpeg|png)$', title, re.I):
                    continue
                info = page['imageinfo'][0]
                ext = info.get('extmetadata', {})
                get = lambda key: text_field(ext.get(key, {}).get('value'))
                license_name = get('LicenseShortName')
                if not any(s in license_name.lower() for s in ['cc by', 'cc0', 'public domain']):
                    continue
                # Original reference photos, not textures. Avoid huge originals.
                url = info['url'] if info.get('size', 0) < 12_000_000 else info.get('thumburl')
                if not url or not re.search(r'\.(jpg|jpeg|png)(?:\?|$)', url, re.I):
                    continue
                relative = f'commons/{page["pageid"]}' + Path(urllib.parse.urlparse(url).path).suffix.lower()
                try:
                    downloaded = acquire(out, relative, {'url': url})
                except Exception as exc:
                    errors.append({'id': f'commons:{page["pageid"]}', 'error': str(exc)})
                    continue
                entry = {'id': f'commons:{page["pageid"]}', 'kind': 'reference_photo',
                         'category': category, 'title': title, 'provider': 'Wikimedia Commons',
                         'source': info['descriptionurl'], 'license': license_name,
                         'license_url': get('LicenseUrl'), 'author': get('Artist'),
                         'capture_date_as_published': get('DateTimeOriginal'),
                         'description': get('ImageDescription'),
                         'status': 'research_only_no_game_texture_permission_inferred',
                         'location_status': 'caption_not_exact_viewpoint_or_current_field_survey',
                         'files': [downloaded]}
                entries.append(entry)
                print('reference', category, title, flush=True)
        except Exception as exc:
            errors.append({'id': 'commons-' + category, 'error': str(exc)})
            print('FAILED commons', category, str(exc), flush=True)

    manifest = {'schema': 1, 'collected_utc': datetime.now(timezone.utc).isoformat(),
                'source_root_example': str(out), 'game_bundle_modified': False,
                'integrated_assets_this_pass': 0,
                'warning': 'Downloads and provider previews do not establish local suitability or art acceptance.',
                'assets': entries, 'errors': errors,
                'excluded_reference_ids': selection.get('excluded_reference_ids', {}),
                'summary': {'assets': len(entries), 'files': sum(len(e['files']) for e in entries),
                            'bytes': sum(f['bytes'] for e in entries for f in e['files']),
                            'materials': sum(e['kind'] == 'material' for e in entries),
                            'models': sum(e['kind'] == 'model' for e in entries),
                            'references': sum(e['kind'] == 'reference_photo' for e in entries)}}
    curation_file = CATALOG / 'curation.json'
    if curation_file.exists():
        curation = json.loads(curation_file.read_text())
        for entry in entries:
            if entry['id'] in curation.get('review_notes', {}):
                entry['review_note'] = curation['review_notes'][entry['id']]
    (CATALOG / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(manifest['summary']), flush=True)


if __name__ == '__main__':
    main()
