#!/usr/bin/env python3
"""Build a read-only review gallery from registered motorcycle candidates.

Run from any directory: python tools/build_motorcycle18_gallery.py
Only the generated index.html is written. No app, registry, model or manifest is
changed. Images must live in the registered review directory and be supported by
a matching render report, source/PNG checkpoint, or hash-bound old manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
from urllib.parse import quote, unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "creative/reviews"
SOURCES = ROOT / "assets-src/moto-components"
PLAN = ROOT / "creative/workflow/motorcycle-execution-18.json"
CATALOG = ROOT / "tools/motorcycle-lab/catalog.json"
RECORDS = ROOT / "creative/workflow/records"
OUTPUT = REVIEWS / "motorcycle18-gallery/index.html"


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def within(path, root):
    return path.resolve().is_relative_to(root.resolve())


def local(value, parent):
    """Resolve a repository-local path; reject URLs and escaped/private paths."""
    if not isinstance(value, str) or urlsplit(value).scheme:
        return None
    value = unquote(value.split("#")[0])
    for base in (ROOT, parent):
        path = (base / value).resolve()
        if within(path, ROOT) and path.is_file():
            return path
    return None


def esc(value):
    return html.escape(str(value), quote=True)


def url(path):
    return quote(os.path.relpath(path, OUTPUT.parent), safe="/.-_")


def link(path, label):
    return f'<a href="{url(path)}">{esc(label)}</a>' if path and path.is_file() else ""


def inspection_link(candidate):
    """Only use the inspector version explicitly chosen by the catalogue."""
    configured = candidate["entry"].get("inspection_url")
    if not isinstance(configured, str):
        return ""
    parsed = urlsplit(configured)
    if parsed.scheme or parsed.netloc:
        return ""
    path = local(parsed.path, CATALOG.parent)
    if not path or not within(path, CATALOG.parent) or path.suffix != ".html":
        return ""
    target = url(path) + "?asset=" + quote(candidate["key"], safe="")
    return f'<a href="{target}">Inspection interactive de la pièce</a>'


def files_in_manifest(review, suffix):
    result = []
    for manifest in sorted(review.glob("*manifest.json")):
        for entry in read_json(manifest).get("files", []):
            if isinstance(entry, dict):
                p = local(entry.get("path"), manifest.parent)
                if p and p.suffix == suffix and within(p, SOURCES):
                    result.append(p)
    return list(dict.fromkeys(result))


def registered_candidates():
    records = []
    for path in sorted(RECORDS.glob("*.json")):
        record = read_json(path)
        if record.get("parent_asset") == "MOTO-BOXER-RDC-001":
            records.append((path, record))
    candidates = []
    for key, entry in read_json(CATALOG).get("assets", {}).items():
        source = local(entry.get("source"), SOURCES)
        if not source or not within(source, SOURCES) or source.suffix != ".blend":
            continue
        matches = [(p, r) for p, r in records if r.get("id") == entry.get("component_id")]
        if not matches:
            matches = [(p, r) for p, r in records
                       if (local(r.get("candidate_source") or r.get("generated_candidate_source"), p.parent)
                           or Path("/")).parent == source.parent]
        record_path, record = matches[0] if matches else (None, {})
        review = REVIEWS / entry.get("review", "_missing_")
        catalog_review = review
        has_source_review = ((review / "render-report.json").is_file()
                             or (review / "source-geometry-check.json").is_file()
                             or any(review.glob("*checkpoint*.json")))
        if not has_source_review:
            rp = local(record.get("candidate_review"), record_path.parent) if record_path else None
            review = rp.parent if rp and within(rp, REVIEWS) else review
        candidates.append({"key": key, "entry": entry, "source": source,
                           "record_path": record_path, "record": record, "review": review,
                           "catalog_review": catalog_review,
                           "lot": entry.get("lot", record.get("production_group")),
                           "glbs": [p for name in entry.get("files", [])
                                    if (p := local(name, SOURCES)) and p.suffix == ".glb" and within(p, SOURCES)]})
    # Older isolated wheel candidates have records but are absent from the lab
    # catalogue. Keep them in a separate baseline section, never silently mark
    # the plan's wheel compatibility group as completed.
    for record_path, record in records:
        rp = local(record.get("candidate_review"), record_path.parent)
        if not rp or not within(rp, REVIEWS):
            continue
        review = rp.parent
        blends = files_in_manifest(review, ".blend")
        revision = record.get("source_revision")
        chosen = [p for p in blends if p.stem == revision] or blends
        if not chosen:
            continue
        source = chosen[0]
        if any(c["source"] == source for c in candidates):
            continue
        candidates.append({"key": review.name, "entry": {"label": record.get("label", review.name)},
                           "source": source, "record_path": record_path, "record": record,
                           "review": review, "lot": record.get("production_group"),
                           "glbs": files_in_manifest(review, ".glb")})
    return candidates


def image_files(candidate):
    review, source = candidate["review"], candidate["source"]
    source_hash = sha(source)
    images, notes, evidence = {}, [], []

    def add(path, kind, proof, expected_hash=None, allowed_parent=None):
        # Never traverse out to documentary photographs or artistic targets.
        allowed_parent = (allowed_parent or review).resolve()
        if not path or path.suffix.lower() != ".png" or path.parent != allowed_parent:
            return
        if not within(path, REVIEWS) or not path.is_file():
            return
        if path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            return
        if expected_hash is not None and expected_hash != sha(path):
            notes.append(f"Empreinte PNG non conforme, image exclue : {path.name}.")
            return
        images[path] = {"path": path, "kind": kind, "proof": proof}

    def expected_png_hash(view, path):
        for key in ("PNG_sha256", "png_sha256", "image_sha256"):
            if key in view:
                return view[key] or ""
        for output in view.get("outputs", []):
            name = output.get("file") or output.get("path")
            if name and Path(name).name == path.name and "sha256" in output:
                return output["sha256"] or ""
        if str(view.get("file", view.get("path", ""))).endswith(".png"):
            return view.get("sha256")
        return None

    render_path = review / "render-report.json"
    render = read_json(render_path)
    if render and render.get("source_sha256") == source_hash:
        evidence.append(render_path)
        for view in render.get("views", []):
            if isinstance(view, dict) and view.get("actually_saved") is not False:
                p = local(view.get("file") or view.get("path") or (str(view.get("name", "")) + ".png"), review)
                if p and view.get("source_sha256", source_hash) == source_hash:
                    add(p, "Rendu Blender", render_path, expected_png_hash(view, p))
    elif render:
        notes.append("Rapport Blender lié à une autre empreinte source : ses images ne sont pas présentées comme celles de ce candidat.")

    # The first tyre/rim reviews predate render-report.json. Their registered
    # production manifests explicitly describe actual Blender renders and bind
    # both the editable source and each PNG by hash. Do not infer from a glob.
    if not render:
        for manifest_path in sorted(review.glob("*manifest.json")):
            manifest = read_json(manifest_path)
            entries = manifest.get("files", [])
            source_bound = any(isinstance(e, dict)
                               and local(e.get("path"), review) == source
                               and e.get("sha256") == source_hash for e in entries)
            claim = str(manifest.get("kind", "")).lower()
            declares = ("blender" in claim and "render" in claim) or manifest.get("real_blender_views") is True
            if source_bound and declares:
                evidence.append(manifest_path)
                for entry in entries:
                    if not isinstance(entry, dict):
                        continue
                    path = local(entry.get("path"), review)
                    if path and path.suffix == ".png" and not path.name.startswith("engine-") and entry.get("sha256") == sha(path):
                        add(path, "Rendu Blender — manifeste de fabrication", manifest_path)

    # Interrupted batches can leave completed, independently attributable views.
    # Neither a README claim nor a file timestamp establishes that relation.
    if not render:
        for checkpoint_path in sorted(review.glob("*checkpoint*.json")):
            checkpoint = read_json(checkpoint_path)
            if checkpoint.get("source_sha256") != source_hash or checkpoint.get("complete") is False:
                continue
            views = checkpoint.get("views")
            if isinstance(views, dict):
                rows = [(name, view) for name, view in views.items() if isinstance(view, dict)]
            else:
                view = checkpoint.get("view", "")
                name = view.get("name", "") if isinstance(view, dict) else view
                rows = [(name, checkpoint)]
            for name, view in rows:
                if view.get("source_sha256", source_hash) != source_hash or view.get("actually_saved") is False:
                    continue
                outputs = view.get("outputs", [])
                if outputs:
                    for output in outputs:
                        path = local(output.get("file") or output.get("path"), review)
                        if path and path.suffix == ".png" and output.get("sha256"):
                            add(path, "Rendu Blender — checkpoint source/PNG", checkpoint_path, output["sha256"])
                else:
                    path = local(view.get("PNG_path") or (str(name) + ".png"), review)
                    expected = expected_png_hash(view, path) if path else None
                    if expected is not None:
                        add(path, "Rendu Blender — checkpoint source/PNG", checkpoint_path, expected)
                evidence.append(checkpoint_path)

    # Browser captures are explicitly marked as isolated Babylon inspection,
    # not Blender renders and not screenshots of the running game.
    # The catalogue's inspection review can differ from the older Blender
    # review (notably instruments-18-baseline versus instruments-v1). Preserve
    # both: source renders stay in their original review. Prefer the newest
    # versioned inspection proof; never mutate or reclassify older captures.
    engine_roots = list(dict.fromkeys([candidate.get("catalog_review", review), review]))
    versioned_paths = [p / version / "engine-check.json"
                       for version in ("inspection-v5", "inspection-v4", "inspection-v3") for p in engine_roots]
    engine_path = next((p for p in versioned_paths if p.is_file()), review / "engine-check.json")
    inspection_version = engine_path.parent.name.removeprefix("inspection-") if engine_path in versioned_paths else None
    has_pixel_proof = inspection_version in ("v5", "v4", "v3")
    engine_directory = engine_path.parent
    engine = read_json(engine_path)
    exports = {str(p.relative_to(ROOT)): sha(p) for p in candidate["glbs"]}
    captured = engine.get("exports", [])
    engine_matches = (bool(captured) and {e.get("path") for e in captured} == set(exports)
                      and all(e.get("sha256") and exports.get(e.get("path")) == e["sha256"] for e in captured))
    frozen_capture = engine.get("inputs_unchanged_during_capture") is True and all(
        (path := local(engine.get(key + "_path"), ROOT)) and
        engine.get(key + "_sha256") == sha(path)
        for key in ("inspector", "capture_tool"))
    source_matches = True
    bound_source_proofs = []
    checked_pixels = {}
    if has_pixel_proof:
        source_matches = local(engine.get("config", {}).get("source"), SOURCES) == source
        source_proofs = [p / "source-geometry-check.json" for p in engine_roots]
        if candidate.get("record_path"):
            registered_review = local(candidate["record"].get("candidate_review"), candidate["record_path"].parent)
            if registered_review and within(registered_review, REVIEWS):
                source_proofs.append(registered_review.parent / "source-geometry-check.json")
        for p in dict.fromkeys(source_proofs):
            proof = read_json(p)
            if proof.get("source_sha256") == source_hash and proof.get("export_sha256") in [e.get("sha256") for e in captured]:
                bound_source_proofs.append(p)
        source_matches = source_matches and bool(bound_source_proofs)
        checked_pixels = {p.get("view"): p for p in engine.get("pixel_checks", [])
                          if p.get("changed_pixels", 0) > 100 and p.get("changed_fraction", 0) > .0001}
        frozen_capture = frozen_capture and bool(checked_pixels) and not engine.get("page_errors") and not engine.get("http_failures")
    if engine_matches and frozen_capture and source_matches:
        evidence.append(engine_path)
        evidence.extend(bound_source_proofs)
        for path in sorted(engine_directory.glob("engine-*.png")):
            view = path.stem.removeprefix("engine-")
            pixel_bound = view in checked_pixels or (
                view.startswith("motion-") and any(str(k).startswith(view.removeprefix("motion-") + ":") for k in checked_pixels))
            if has_pixel_proof and not pixel_bound:
                notes.append(f"Vue {inspection_version} sans contrôle de pixels correspondant : {path.name}.")
                continue
            if all(path.stat().st_mtime_ns >= p.stat().st_mtime_ns for p in candidate["glbs"]):
                kind = f"Capture Babylon.js {inspection_version} — cadre entier et pixels contrôlés" if has_pixel_proof else "Capture Babylon.js — inspection isolée"
                add(path.resolve(), kind, engine_path, allowed_parent=engine_directory)
        if has_pixel_proof:
            notes.append(f"Inspection {inspection_version} privilégiée : cadre entier et pixels contrôlés techniquement. Les anciennes séries restent en historique et ne sont pas présentées ici. Aucune qualification mobile physique ni réception artistique.")
    elif engine:
        notes.append("Capture moteur non reliée à la source, à l’export ou au code courant par les preuves disponibles. Si une série versionnée existe, les anciennes séries restent exclues ; aucune substitution par une preuve antérieure.")
    return list(images.values()), notes, list(dict.fromkeys(evidence))


def source_views_closed(candidate, images):
    report = read_json(candidate["review"] / "render-report.json")
    if report.get("source_sha256") != sha(candidate["source"]):
        return False
    views = report.get("views", [])
    if not isinstance(views, list):
        return False
    expected = {Path(v.get("file") or v.get("path") or (str(v.get("name", "")) + ".png")).stem
                for v in views if isinstance(v, dict)}
    proved = {im["path"].stem for im in images if im["kind"].startswith("Rendu Blender")}
    return bool(expected) and expected <= proved


def current_display_text(text, candidate, images):
    """Normalize old render-queue wording only when the exact series is proved."""
    if source_views_closed(candidate, images):
        text = re.sub(r"vues finales en cours", "vues finales disponibles", text, flags=re.I)
        text = re.sub(r"(vues finales\s*\d*)\s+à produire", r"\1 disponibles", text, flags=re.I)
        text = re.sub(r"vues prévues(?=\s*\d|\s*:)", "Vues disponibles", text, flags=re.I)
    return text


def correction_excerpt(candidate):
    blocks = []
    readme = candidate["review"] / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.is_file() else ""
    for para in text.split("\n\n"):
        if re.search(r"correction|corrig|reprise|à reprendre|reste(?:nt)?|inconnu", para, re.I):
            plain = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", para)
            plain = re.sub(r"[*`#]", "", plain).strip()
            plain = current_display_text(plain, candidate, candidate.get("images", []))
            if len(plain) > 40:
                blocks.append(plain[:650] + ("…" if len(plain) > 650 else ""))
    return blocks[-2:]


CSS = """
:root{color-scheme:dark;--bg:#10151b;--panel:#1a222c;--line:#354251;--text:#edf3f8;--muted:#b4c3d2;--accent:#f4b168}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 system-ui,sans-serif}
a{color:#a9d6ff;text-underline-offset:3px}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid var(--accent);outline-offset:4px}
header,main,footer{max-width:1440px;margin:auto;padding:28px clamp(16px,4vw,56px)}header{padding-top:50px}h1{font-size:clamp(2rem,5vw,3.6rem);line-height:1.1;max-width:950px;margin:10px 0 24px}h2{font-size:1.6rem}h3{margin:8px 0;font-size:1.28rem}
.eyebrow{color:var(--accent);font-weight:750;letter-spacing:.1em;font-size:.8rem}.intro{max-width:900px;color:var(--muted)}.notice{border-left:4px solid var(--accent);padding:12px 20px;background:#222833;max-width:1000px}.pills,.links{display:flex;flex-wrap:wrap;gap:10px}.pill{border:1px solid var(--line);border-radius:999px;padding:4px 12px;font-size:.85rem}.muted,figcaption,.small{color:var(--muted)}.small{font-size:.85rem}.summary{display:flex;gap:30px;flex-wrap:wrap;margin:25px 0}.summary strong{font-size:1.8rem;color:var(--accent);display:block}.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:12px}table{border-collapse:collapse;width:100%;min-width:820px}th,td{padding:15px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}th{background:#202c39;font-size:.85rem}td:first-child{font-weight:700}td small{display:block;color:var(--muted)}.status{color:var(--accent);font-weight:700}.toolbar{display:flex;flex-wrap:wrap;gap:12px;margin:28px 0}.toolbar input{flex:1;min-width:200px;background:var(--panel);border:1px solid var(--line);color:var(--text);padding:12px;border-radius:8px;font:inherit}.toolbar label{display:flex;align-items:center;gap:8px}section{margin:32px 0 50px}.candidate{border:1px solid var(--line);border-radius:14px;background:var(--panel);padding:clamp(14px,3vw,26px);margin:20px 0 30px;overflow:hidden}.candidate-head{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}.candidate .links a{background:#243243;padding:7px 12px;border-radius:6px;font-size:.9rem}.frames{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:18px;margin:22px 0}.frames figure{margin:0;min-width:0;background:#101720;border-radius:8px;overflow:hidden}.frames img{width:100%;height:270px;object-fit:contain;display:block;background:#e1e3e5}.frames figcaption{padding:12px;font-size:.85rem}.empty{padding:22px;border:1px dashed var(--line);border-radius:8px;color:var(--muted)}details{padding:12px 0;border-top:1px solid var(--line)}summary{cursor:pointer;font-weight:650}code{overflow-wrap:anywhere;font-size:.8rem}footer{border-top:1px solid var(--line)}[hidden]{display:none!important}.skip{position:absolute;left:8px;top:-70px}.skip:focus{top:8px}.correction{max-width:1050px}li{margin-bottom:5px}@media(max-width:600px){header{padding-top:34px}.frames img{height:235px}.summary{gap:22px}.summary strong{font-size:1.5rem}h3{font-size:1.1rem}}
.highlights{margin:20px 0}.highlights .frames{grid-template-columns:repeat(3,minmax(0,1fr))}.highlights img{height:210px}.plan>summary{font-size:1.4rem;padding:8px 0 18px}.quick-links{margin:18px 0}.technical-views{margin:20px 0}html{scroll-padding-top:20px}@media(max-width:600px){.highlights .frames{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:10px}.highlights figure{flex:0 0 88%;scroll-snap-align:start}.highlights img{height:220px}}
"""


def build():
    plan = read_json(PLAN)
    lots = plan.get("lots", [])
    if len(lots) != 18:
        raise ValueError("Le plan doit déclarer exactement 18 groupes.")
    candidates = registered_candidates()
    for c in candidates:
        c["images"], c["notes"], c["proofs"] = image_files(c)
        c["built"] = c["source"].is_file() and bool(c["glbs"])
    groups = {lot["lot"]: [c for c in candidates if c["lot"] == lot["lot"]] for lot in lots}
    built_groups = sum(any(c["built"] for c in cs) for cs in groups.values())
    review_groups = sum(any(c["images"] for c in cs) for cs in groups.values())
    pieces = sum(c["built"] for c in candidates)
    images_count = sum(len(c["images"]) for c in candidates)

    def image_figure(im, title, eager=False):
        path = im["path"]
        label = f'{title} — {path.stem}'
        loading = "eager" if eager else "lazy"
        return f'<figure><a href="{url(path)}" target="_blank" rel="noopener"><img src="{url(path)}" alt="{esc(label)}" loading="{loading}" decoding="async"></a><figcaption>{esc(im["kind"])} · {esc(title)} · {esc(path.stem)}<br><a href="{url(path)}" target="_blank" rel="noopener">Ouvrir l’image entière</a> · {link(im["proof"], "preuve")}</figcaption></figure>'

    highlights = []
    for key, view_name, label in [("clamps", "quarter", "Pontets"),
                                  ("clutch-control", "quarter-rest", "Levier d’embrayage v2"),
                                  ("front-brake-control", "quarter-rest", "Levier de frein v2")]:
        for c in candidates:
            if c["key"] == key:
                im = next((im for im in c["images"] if im["kind"].startswith("Rendu Blender") and im["path"].stem == view_name), None)
                if im:
                    highlights.append(image_figure(im, label, eager=True))
    banner = ('<section class="highlights" aria-label="Trois rendus Blender de candidats non reçus"><p class="small">Rendus Blender actuels, liés à leurs preuves. Candidats non reçus.</p><div class="frames">' + ''.join(highlights) + '</div></section>') if highlights else ""
    out = [f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Viva Wewa · Revue des composants moto</title><style>{CSS}</style></head><body>',
           '<a class="skip" href="#candidats">Aller aux cartes</a><header><div class="eyebrow">VIVA WEWA · ATELIER MOTO</div><h1>La moto, pièce par pièce.</h1>',
           '<p class="intro">Revue des candidats catalogués : rendus Blender et inspections isolées. Ces images ne montrent pas le jeu.</p>',
           '<nav class="links quick-links" aria-label="Accès rapide"><a href="#candidats">Voir les cartes</a><a href="#plan-18">État des 18 groupes</a></nav>', banner,
           '<p class="notice">Aucune réception artistique n’est implicite. Une source construite, un contrôle technique et un groupe complet sont trois états distincts. Les recherches documentaires seules restent à fabriquer.</p>',
           f'<div class="summary"><div><strong>{built_groups}/18</strong>groupes avec source et export</div><div><strong>{review_groups}/18</strong>groupes avec images de revue</div><div><strong>{pieces}</strong>candidats / révisions catalogués avec source + export</div><div><strong>{images_count}</strong>images de preuve disponibles</div></div>',
           '<p class="small">Les révisions historiques peuvent compter plusieurs fois une même pièce. Aucun de ces nombres ne mesure les modèles reçus ou les groupes terminés.</p><nav class="links">',
           link(PLAN, "Plan des 18 groupes"), link(CATALOG, "Catalogue réel"), link(ROOT / "creative/workflow/motorcycle-assembly.json", "Décomposition et fiches"),
           '</nav></header><main id="groupes"><details open class="plan" id="plan-18"><summary>État des 18 groupes</summary><div class="table-wrap"><table><thead><tr><th scope="col">Groupe</th><th scope="col">Fabrication constatée</th><th scope="col">Revue disponible</th><th scope="col">Périmètre et état consigné</th></tr></thead><tbody>']
    for lot in lots:
        cs = groups[lot["lot"]]
        built = sum(c["built"] for c in cs)
        views = sum(len(c["images"]) for c in cs)
        status = "En revue · partiel" if views else ("Construit · vues en attente" if built else "À fabriquer")
        legacy_existing = bool(lot.get("legacy_review_scope")) and lot.get("any_source_blend_built") is True
        construction_note = f'{built} candidat(s) avec Blender + GLB'
        review_note = f'{views} image(s)'
        if legacy_existing and not built:
            status = "Candidats existants à recontrôler"
            construction_note = "Sources et preuves historiques existantes ; compatibilité des 18 groupes à vérifier, sans nouvelle fabrication comptée"
            review_note = '<a href="#preexistants">Voir les vues des candidats antérieurs</a>'
        scope = "; ".join(lot.get("observable_fabrication_units", []))
        research = local(lot.get("research"), PLAN.parent)
        complete = lot.get("group_complete") is True and lot.get("all_required_components_built") is True
        out.append(f'<tr><td><a href="#lot-{lot["lot"]}">{lot["lot"]:02d} · {esc(lot["label"])}</a></td><td><span class="status">{status}</span><small>{esc(construction_note)} ; {"périmètre déclaré construit" if complete else "groupe non terminé"}</small></td><td>{review_note}<small>Réception artistique : {"déclarée au plan, voir preuve" if lot.get("user_art_accepted") else "non acquise"}</small></td><td>{esc(scope)}<small>État source : <code>{esc(lot.get("state", "non consigné"))}</code></small>{link(research, "Recherche — ne vaut pas fabrication")}</td></tr>')
    out.append('</tbody></table></div></details><div id="candidats" class="toolbar"><label for="search">Filtrer les candidats</label><input id="search" type="search" placeholder="Nom, groupe, révision…" autocomplete="off"><label><input id="with-images" type="checkbox"> Avec images uniquement</label></div><p id="filter-count" class="small" aria-live="polite"></p>')

    def card(c):
        source, review, record = c["source"], c["review"], c["record"]
        title = current_display_text(c["entry"].get("label", source.stem), c, c["images"])
        state = "En revue" if c["images"] else "Construit · images en attente"
        record_current = record.get("source_revision")
        historical = record_current and source.stem != record_current
        history_badge = '<span class="pill">Révision distincte de la fiche courante</span>' if historical else ""
        readme = source.parent / c["entry"].get("readme", "README.md")
        if not readme.is_file():
            readme = source.parent / "README.md"
        bits = [f'<article class="candidate" data-search="{esc(str(c["lot"]) + " " + title + " " + source.stem)}" data-images="{len(c["images"])}"><div class="candidate-head"><div><p class="eyebrow">{esc(source.stem)}</p><h3>{esc(title)}</h3></div><div class="pills"><span class="pill">{state}</span><span class="pill">Candidat non reçu</span>{history_badge}</div></div>',
                '<p class="muted">Dimensions locales et interfaces estimées ou non confirmées. La ressemblance à une pièce de marché voisin ne certifie pas sa compatibilité avec la Boxer RDC.</p>', '<div class="links">',
                link(source, "Source Blender"), *[link(p, "Export GLB" if len(c["glbs"]) == 1 else p.name) for p in c["glbs"]],
                link(readme, "README source"), link(review / "README.md", "Revue et limites"), link(c["record_path"], "Fiche du composant"), inspection_link(c), '</div>']
        blender_images = [im for im in c["images"] if im["kind"].startswith("Rendu Blender")]
        technical_images = [im for im in c["images"] if not im["kind"].startswith("Rendu Blender")]
        if blender_images:
            bits.append('<div class="frames">')
            bits.extend(image_figure(im, title) for im in blender_images)
            bits.append('</div>')
        else:
            bits.append('<p class="empty">Rendus Blender en attente : aucun PNG de rendu suffisamment relié à cette source n’est disponible. Les éventuelles captures techniques restent accessibles ci-dessous.</p>')
        if technical_images:
            bits.append('<details class="technical-views"><summary>Inspection technique dans le navigateur</summary><p class="small">Captures isolées de l’export dans Babylon.js ; elles ne montrent pas le jeu et ne valent pas réception artistique.</p><div class="frames">')
            bits.extend(image_figure(im, title) for im in technical_images)
            bits.append('</div></details>')
        excerpts = correction_excerpt(c)
        if excerpts:
            bits.append('<details class="correction"><summary>Corrections et limites consignées dans la revue</summary>')
            bits.extend(f'<p>{esc(text)}</p>' for text in excerpts)
            bits.append('</details>')
        bits.append(f'<details><summary>Traçabilité de la révision et points ouverts</summary><p>Source SHA-256 : <code>{sha(source)}</code></p>')
        if historical:
            bits.append(f'<p>La fiche courante désigne <code>{esc(record_current)}</code>. Cette autre révision reste identifiée séparément ; ses preuves ne sont pas transférées à la version courante.</p>')
        identity = record.get("identity", {})
        if identity.get("variant"):
            bits.append(f'<p>Variante consignée : {esc(identity["variant"])}</p>')
        if record.get("gaps"):
            bits.append('<ul>')
            bits.extend(f'<li>{esc(g.get("description", ""))}</li>' for g in record["gaps"] if g.get("status") != "closed")
            bits.append('</ul>')
        bits.extend(f'<p>{esc(note)}</p>' for note in c["notes"])
        bits.append('<div class="links">' + ''.join(link(p, p.name) for p in c["proofs"]) + '</div></details></article>')
        return ''.join(bits)

    for lot in lots:
        out.append(f'<section id="lot-{lot["lot"]}"><h2>{lot["lot"]:02d} · {esc(lot["label"])}</h2>')
        cs = groups[lot["lot"]]
        if cs:
            out.extend(card(c) for c in cs)
        elif lot.get("legacy_review_scope") and lot.get("any_source_blend_built") is True:
            out.append('<p class="empty">Des candidats antérieurs et leurs preuves historiques existent. <a href="#preexistants">Voir les pièces déjà isolées</a>. Leur revue et leur compatibilité dans la séquence des 18 groupes restent à vérifier ; aucun nouveau modèle ni ensemble terminé n’est compté ici.</p>')
        else:
            out.append('<p class="empty">À fabriquer dans ce groupe : aucun candidat avec source Blender enregistré dans le catalogue ou une fiche liée. La recherche, même documentée, ne constitue pas une pièce fabriquée.</p>')
        if lot.get("remaining_scope"):
            out.append(f'<p class="small">Périmètre restant consigné : {esc(lot["remaining_scope"])}</p>')
        out.append('</section>')
    baselines = [c for c in candidates if c["lot"] not in groups]
    if baselines:
        out.append('<section id="preexistants"><h2>Candidats préexistants hors décompte des 18 groupes</h2><p class="muted">Guidon, compteurs et composants avant déjà isolés. Leur existence ne termine pas le groupe de compatibilité de l’ensemble avant ; les raccords et réceptions restent distincts.</p>')
        out.extend(card(c) for c in baselines)
        out.append('</section>')
    out.append('</main><footer><p>Galerie locale régénérable avec <code>python tools/build_motorcycle18_gallery.py</code>.</p><p class="small">Les fichiers de revue restent à leur emplacement d’origine. Aucune photo documentaire privée ni cible artistique générée n’est incluse. Les captures d’inspection ne prouvent pas le rendu final du jeu ni sa qualification sur iPhone.</p></footer><script>const q=document.querySelector("#search"),only=document.querySelector("#with-images"),cards=[...document.querySelectorAll(".candidate")];function filter(){let n=0;for(const c of cards){const show=c.dataset.search.toLocaleLowerCase("fr").includes(q.value.toLocaleLowerCase("fr"))&&(!only.checked||Number(c.dataset.images)>0);c.hidden=!show;if(show)n++}document.querySelector("#filter-count").textContent=n+" candidat(s) affiché(s)"}q.addEventListener("input",filter);only.addEventListener("change",filter);filter();</script></body></html>')
    document = '\n'.join(out) + '\n'
    validate(document)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(document, encoding="utf-8")
    return {"output": str(OUTPUT.relative_to(ROOT)), "groups": len(lots), "candidate_revisions": len(candidates),
            "constructed_candidate_revisions": pieces, "groups_with_models": built_groups,
            "groups_with_review_images": review_groups, "review_pngs": images_count,
            "html_and_local_links_validated": True}


def validate(document):
    class Checker(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.ids, self.targets, self.links, self.images = set(), [], [], []

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if "id" in attrs:
                if attrs["id"] in self.ids:
                    raise ValueError("Duplicate HTML id: " + attrs["id"])
                self.ids.add(attrs["id"])
            for key in ("src", "href"):
                if key in attrs:
                    value = attrs[key]
                    if value.startswith("#"):
                        self.targets.append(value[1:])
                    else:
                        if urlsplit(value).scheme or value.startswith("//"):
                            raise ValueError("Only local gallery links are allowed: " + value)
                        p = (OUTPUT.parent / unquote(urlsplit(value).path)).resolve()
                        if not within(p, ROOT) or not p.is_file():
                            raise ValueError("Missing or unsafe gallery link: " + value)
                        self.links.append(p)
                        if tag == "img":
                            self.images.append(p)
                            if not within(p, REVIEWS) or p.suffix.lower() != ".png" or not attrs.get("alt"):
                                raise ValueError("Invalid review image")

    checker = Checker()
    checker.feed(document)
    if set(checker.targets) - checker.ids:
        raise ValueError("Missing local HTML anchor")
    if '<html lang="fr">' not in document or "name=\"viewport\"" not in document:
        raise ValueError("Missing responsive French document metadata")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(json.dumps(build(), ensure_ascii=False, indent=2))
