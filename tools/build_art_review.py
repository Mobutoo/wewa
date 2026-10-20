#!/usr/bin/env python3
"""Build a local, linked source catalogue. Provider previews are explicitly not game screenshots."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
folder = ROOT / 'creative/library'
manifest = json.loads((folder / 'manifest.json').read_text())
esc = html.escape
parts = ['''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Viva Wewa — bibliothèque de production</title><style>
*{box-sizing:border-box}body{margin:0;background:#141a1e;color:#edf0ee;font:16px/1.5 system-ui,sans-serif}
main{max-width:1400px;margin:auto;padding:28px}h1{font-size:32px;margin:0}h2{margin-top:40px}
p{max-width:1000px;color:#cbd1ce}a{color:#eecb78}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}
article{background:#20282d;border:1px solid #4b575d;border-radius:8px;overflow:hidden}article div{padding:12px}
img{display:block;width:100%;aspect-ratio:1;object-fit:contain;background:#3a4146}h3{font-size:17px;margin:0 0 8px}
.meta{font-size:12px;color:#aebbb8}nav{display:flex;gap:24px;flex-wrap:wrap;margin:24px 0}table{width:100%;border-collapse:collapse}
th,td{padding:10px;border-bottom:1px solid #465055;text-align:left;vertical-align:top}small{color:#d8bf80}
</style><main><h1>Viva Wewa · bibliothèque de production</h1>
<p><strong>Ressources sources à examiner. Aucun aperçu ci-dessous n’est une capture de Viva Wewa.</strong>
Les vignettes 3D sont les rendus du fournisseur. Les objets téléchargés ne sont pas encore intégrés, optimisés ou acceptés artistiquement.
La présence d’une ressource ici ne confirme pas sa présence à Kinshasa.</p>
<nav><a href="#models">Modèles</a><a href="#materials">Matières</a><a href="#references">Photos documentaires</a><a href="../ART_PRODUCTION.md">Audit et méthode</a><a href="manifest.json">Manifeste et empreintes</a></nav>''']
summary = manifest['summary']
parts.append(f'<p>{summary["models"]} modèles candidats · {summary["materials"]} ensembles PBR · {summary["references"]} photographies documentaires · {summary["bytes"]/1_000_000:.1f} Mo de sources hors du jeu public.</p>')
for kind, anchor, heading in [('model','models','Modèles candidats'),('material','materials','Matériaux photographiques')]:
    parts.append(f'<h2 id="{anchor}">{heading}</h2><div class="grid">')
    for entry in [e for e in manifest['assets'] if e['kind'] == kind]:
        name = entry['id'].split(':',1)[1]
        parts.append('<article>')
        if entry.get('provider_preview'):
            parts.append(f'<img src="{esc(entry["provider_preview"])}" alt="Aperçu fournisseur de {esc(name)}">')
        authors = ', '.join((entry.get('authors') or {}).keys())
        parts.append(f'<div><h3>{esc(name)}</h3><p>{esc(entry["intended_use"])}</p>')
        parts.append(f'<p class="meta">{esc(authors)} · CC0 · {sum(f["bytes"] for f in entry["files"])/1_000_000:.1f} Mo source</p>')
        parts.append(f'<small>Candidat, pas encore intégré</small><br><a href="{esc(entry["source"])}">Source et détails</a></div></article>')
    parts.append('</div>')
parts.append('<h2 id="references">Photographies documentaires</h2><p>Les dates sont celles publiées par les auteurs. Ni relevé terrain récent, ni textures prêtes à publier. Les licences et auteurs s’appliquent individuellement.</p><table><thead><tr><th>Référence</th><th>Date, auteur et droits</th><th>Usage et limites</th></tr></thead><tbody>')
for entry in [e for e in manifest['assets'] if e['kind'] == 'reference_photo']:
    note = entry.get('review_note','Vue à relire : cadrage exact et état actuel non confirmés.')
    parts.append(f'<tr><td><a href="{esc(entry["source"])}">{esc(entry["title"])}</a></td><td>{esc(entry.get("capture_date_as_published") or "Date non établie")}<br>{esc(entry["author"])}<br>{esc(entry["license"])}</td><td>{esc(note)}</td></tr>')
parts.append('</tbody></table><p>Sources CC0 : <a href="https://polyhaven.com/license">Poly Haven</a>. Métadonnées Commons : pages liées ci-dessus. La collecte n’engage aucun achat.</p></main></html>')
(folder / 'index.html').write_text(''.join(parts))
print('Created creative/library/index.html')
