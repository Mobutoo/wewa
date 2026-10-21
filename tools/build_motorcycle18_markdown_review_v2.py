#!/usr/bin/env python3
"""Add the source-specific gasket1 material finding without rewriting builder v1."""
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('wewa_markdown_review_v1', ROOT/'tools/build_motorcycle18_markdown_review.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
previous_rework = review.known_rework


def known_rework(component):
    candidate = component['candidate']
    if (component['id'] == 'MOTO-EXHAUST-HEADER-GASKET-001' and candidate and
            review.gallery.sha(candidate['source']) == '754d172acafd51cf22d7a085626bf35023e567e9c71d6358266dfc9764bd0672'):
        folder = ROOT/'creative/research/exhaust-header-gasket/material-diagnostic-v1'
        return [
            'À reprendre sur cette matière v1 : un quadrillage régulier apparaît sur le joint. Dans les trois vrais contrôles à caméra et éclairage identiques, il disparaît quand seule la carte normale est débranchée et demeure quand seule la rugosité devient constante. La carte normale est la cause dominante observée ; le contrôle sans normale ne constitue pas une matière finale reçue.',
            ' · '.join([review.link(folder/'report.json', 'Diagnostic et trois rendus réels'),
                        review.link(folder/'coordinator-review.json', 'Lecture indépendante et empreintes')])]
    return previous_rework(component)


if __name__ == '__main__':
    review.known_rework = known_rework
    result = review.build()
    document = review.OUTPUT.read_text().replace(
        'Régénération : `python tools/build_motorcycle18_markdown_review.py`.',
        'Régénération : `python tools/build_motorcycle18_markdown_review_v2.py`.')
    review.validate(document, [c['id'] for c in review.exact_components()])
    review.OUTPUT.write_text(document)
    result['source_specific_gasket1_finding'] = True
    print(json.dumps(result, ensure_ascii=False, indent=2))
