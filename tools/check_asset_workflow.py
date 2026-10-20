#!/usr/bin/env python3
"""Check asset declarations and evidence integrity; never assess visual realism."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'creative/workflow'


def read(path):
    return json.loads(path.read_text())


def check_record(path, workflow):
    record = read(path)
    errors = []
    required = {'schema', 'id', 'label', 'source_ids', 'recipes', 'identity',
                'source_register', 'sources', 'claims', 'gaps', 'gates',
                'source_revision', 'art_accepted', 'active_detailed_fabrication'}
    missing = required - record.keys()
    if missing:
        return record, [f'missing fields: {sorted(missing)}']
    sources = {x['id'] for x in read(path.parent / record['source_register'])['sources']}
    if not record['recipes'] or set(record['recipes']) - set(workflow['recipes']):
        errors.append('unknown or empty recipe')
    if set(record['sources']) - sources:
        errors.append('unknown source IDs')
    for claim in record['claims']:
        cid = claim.get('id')
        if claim.get('status') not in workflow['claim_statuses']:
            errors.append(f'invalid claim status: {cid}')
        if claim.get('source') not in record['sources']:
            errors.append(f'claim missing declared source: {cid}')
        if claim.get('adopted') and claim.get('status') in {'unknown', 'rejected', 'documented_related_variant'}:
            errors.append(f'unresolved or related claim adopted as exact constraint: {cid}')
        if claim.get('status') in {'estimated', 'photo_inferred'} and not all(claim.get(k) for k in ('method', 'uncertainty', 'scope')):
            errors.append(f'inference lacks method/uncertainty/scope: {cid}')
    if set(record['gates']) != {s['id'] for s in workflow['stages']}:
        errors.append('gate set differs from workflow')
    completed = set()
    for stage in workflow['stages']:
        sid = stage['id']
        gate = record['gates'].get(sid, {})
        status = gate.get('status')
        if status not in workflow['statuses']:
            errors.append(f'{sid}: invalid status')
            continue
        if status not in {'passed', 'not_applicable'}:
            continue
        reviewer = gate.get('reviewer') or {}
        if not gate.get('reason') or not isinstance(reviewer, dict) or not reviewer.get('name') or reviewer.get('role') not in {'technical', 'artistic', 'user'} or not gate.get('reviewed_at'):
            errors.append(f'{sid}: missing decision reason/reviewer')
        if not gate.get('revision') or gate['revision'] != record['source_revision']:
            errors.append(f'{sid}: stale or unspecified revision')
        if not set(stage['depends_on']) <= completed:
            errors.append(f'{sid}: predecessor not complete')
        evidence = gate.get('evidence', [])
        if not set(stage['required_evidence']) <= {e.get('kind') for e in evidence}:
            errors.append(f'{sid}: missing required evidence types')
        for entry in evidence:
            proof = path.parent / entry.get('path', '')
            if not proof.is_file():
                errors.append(f'{sid}: evidence file missing')
            elif hashlib.sha256(proof.read_bytes()).hexdigest() != entry.get('sha256'):
                errors.append(f'{sid}: evidence hash mismatch')
            if entry.get('revision') != record['source_revision']:
                errors.append(f'{sid}: evidence revision mismatch')
        for gap in record['gaps']:
            if gap.get('critical') and gap.get('status') != 'closed' and sid in gap.get('blocks', []):
                errors.append(f"{sid}: unresolved critical gap {gap.get('id')}")
        completed.add(sid)
    accepted = record['gates'].get('G8', {}).get('status') == 'passed'
    if record['art_accepted'] != accepted:
        errors.append('art_accepted does not match G8')
    if record['gates'].get('G8', {}).get('status') == 'not_applicable':
        errors.append('G8 user reception cannot be not_applicable')
    if accepted and record['gates']['G8'].get('reviewer', {}).get('role') != 'user':
        errors.append('G8 requires a user decision')
    return record, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('records', type=Path, nargs='*')
    parser.add_argument('--ready-for', choices=[f'G{i}' for i in range(9)])
    args = parser.parse_args()
    workflow = read(WORK / 'workflow.json')
    paths = args.records or sorted((WORK / 'records').glob('*.json'))
    errors, reports, ids = [], [], []
    active = 0
    for path in paths:
        record, issues = check_record(path, workflow)
        errors.extend(f'{path.name}: {x}' for x in issues)
        ids.append(record['id'])
        active += bool(record.get('active_detailed_fabrication'))
        pending = [s['id'] for s in workflow['stages'] if record['gates'].get(s['id'], {}).get('status') not in {'passed', 'not_applicable'}]
        report = {'id': record['id'], 'first_unfinished_gate': pending[0] if pending else None,
                  'art_accepted': record['art_accepted']}
        if args.ready_for:
            before = int(args.ready_for[1:])
            blockers = [f"{s['id']} incomplete" for s in workflow['stages'][:before] if s['id'] in pending]
            blockers += [g['id'] for g in record['gaps'] if g.get('critical') and g.get('status') != 'closed' and args.ready_for in g.get('blocks', [])]
            if record['gates'].get(args.ready_for, {}).get('status') in {'blocked', 'rework'}:
                blockers.append(f'{args.ready_for} explicitly blocked/rework')
            report.update(requested_gate=args.ready_for, blockers=blockers)
            errors.extend(f"{record['id']}: {b}" for b in blockers)
        reports.append(report)
    if len(set(ids)) != len(ids):
        errors.append('duplicate component IDs')
    if active > workflow['policy']['detailed_active_components_max']:
        errors.append('too many components in detailed fabrication')
    catalogue = read(ROOT / 'creative/library/fabrication-register.json')
    coverage = read(WORK / 'coverage.json')
    expected = {i['id'] for i in catalogue['items']}
    actual = [i['source_id'] for i in coverage['rows']]
    if len(set(actual)) != len(actual) or set(actual) != expected:
        errors.append('source row routing incomplete or duplicated')
    for item in coverage['rows']:
        if not item['recipes'] or set(item['recipes']) - set(workflow['recipes']):
            errors.append(f"invalid routing: {item['source_id']}")
        for link in item['component_records']:
            if not (WORK / link).is_file():
                errors.append(f'missing component record: {link}')
    print(json.dumps({'valid': not errors, 'reports': reports, 'routed_source_rows': len(actual),
                      'errors': errors, 'scope': 'Declarations and local evidence integrity; no visual or hardware qualification'}, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == '__main__':
    raise SystemExit(main())
