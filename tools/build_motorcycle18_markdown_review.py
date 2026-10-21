#!/usr/bin/env python3
"""Generate a GitHub-readable, unique-component motorcycle review.

The component-production register defines membership; each workflow record defines
the exact revision. Image eligibility is delegated to the gallery's existing
source/PNG proof checks. No models, registries or inspection tools are changed.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import quote, unquote, urlsplit

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("wewa_motorcycle_gallery_proofs", ROOT / "tools/build_motorcycle18_gallery.py")
gallery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gallery)
REGISTER = ROOT / "creative/library/component-production.json"
OUTPUT = ROOT / "creative/reviews/motorcycle18-components.md"


def label(text):
    return str(text).replace("[", "\\[").replace("]", "\\]").replace("|", "\\|")


def href(path):
    return quote(os.path.relpath(path, OUTPUT.parent), safe="/.-_")


def link(path, text):
    return f"[{label(text)}]({href(path)})" if path and path.is_file() else ""


def exact_components():
    registered = gallery.read_json(REGISTER).get("components", [])
    ids = [entry["id"] for entry in registered]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate component IDs in the production register")
    candidates = gallery.registered_candidates()
    records = {gallery.read_json(p).get("id"): p for p in gallery.RECORDS.glob("*.json")}
    result = []
    for entry in registered:
        record_path = gallery.local(entry.get("component_workflow"), REGISTER.parent) or records.get(entry["id"])
        record = gallery.read_json(record_path) if record_path else {}
        revision = record.get("source_revision")
        matches = [c for c in candidates
                   if (c["entry"].get("component_id") or c["record"].get("id")) == entry["id"]
                   and c["source"].stem == revision]
        selected = dict(matches[0]) if matches else None
        review_readme = gallery.local(entry.get("candidate_review"), REGISTER.parent)
        source_readme = gallery.local(entry.get("candidate_source"), REGISTER.parent)
        if selected:
            # Use the registered review, not a newer catalogue-only candidate or
            # an inspection-baseline folder copied by the coordinator.
            if review_readme and gallery.within(review_readme, gallery.REVIEWS):
                selected["review"] = review_readme.parent
            selected["record"] = record
            selected["record_path"] = record_path
            images = [im for im in gallery.image_files(selected)[0]
                      if im["kind"].startswith("Rendu Blender")]
        else:
            images = []
        result.append({"id": entry["id"], "entry": entry, "record": record,
                       "record_path": record_path, "revision": revision,
                       "candidate": selected, "images": images,
                       "source_readme": source_readme, "review_readme": review_readme,
                       "lot": record.get("production_group")})
    return result


def choose_image(images):
    # Prefer an isolated whole-part view over a material/machining detail, while
    # keeping the original PNG untouched. Otherwise retain the proof order.
    preferred = ("neutral-quarter", "isolated-quarter", "quarter", "quarter-rest",
                 "front-quarter", "whole", "whole-front", "outer-bosses",
                 "outer-face", "outer-forward-boss", "front-shape",
                 "upper-quarter", "quarter-off", "descending-visible-sections")
    for name in preferred:
        image = next((im for im in images if im["path"].stem == name), None)
        if image:
            return image
    return images[0] if images else None


def known_rework(component):
    if component["candidate"]:
        source_hash = gallery.sha(component["candidate"]["source"])
        if (component["id"] == "MOTO-MIRROR-RIGHT-001" and
                source_hash == "af1bfd1155b02281eb549b428042728e55f7975f0fdc449806bb288d850e0a58"):
            audit = ROOT / "creative/research/mirrors-thread-diagnostic/source-audit.json"
            return ["À reprendre sur cette v2 : le rapprochement cache/écrou est conservé, mais le filet sous l’écrou apparaît ondulé/segmenté dans la vue de base. La grille axiale non alignée aux crêtes est une cause plausible à vérifier ; diamètre, pas et montage restent estimés.",
                    link(audit, "Diagnostic de construction du filet")]
        if (component["id"] == "MOTO-INSTRUMENTS-001" and
                source_hash == "dc4b3ccf26f35e3b4a4f10068306d841695901f987a43ebad65299cec132ad22"):
            audit = ROOT / "creative/research/instruments-v2/optical-edge-diagnostic-reading.json"
            return ["À reprendre sur cette v2 : le lissage des vitres mélange leur face avec leur tranche et produit des reflets segmentés. Les témoins à géométrie et éclairage identiques isolent ce défaut de normales. Une v3 séparée conserve les profils, graduations, matières et pivots ; ses rendus ont leurs propres preuves.",
                    link(audit, "Diagnostic optique et témoins comparés")]
    if (component["id"] == "MOTO-KICKSTARTER-001" and component["candidate"]
            and gallery.sha(component["candidate"]["source"]) == "6fade26e0f95de87cc18a8891f15b6be3b08b1a66ebca31bdce984fb2ac8f013"):
        audit_dir = ROOT / "creative/research"
        audits = [audit_dir / "kickstarter-independent-visual-audit.README.md",
                  audit_dir / "kickstarter-independent-visual-audit.json"]
        audit_links = [link(p, "Audit du kick v1" if p.suffix == ".md" else "Rapport et empreintes")
                       for p in audits if p.is_file()]
        return ["À reprendre sur cette v1 : le coordinateur signale une fuite locale du cutter cannelé sur les oreilles/ponts de charnière, visible dans la macro et non documentée par les photos. Une correction v2 est prévue après le gel LH ; les vues v1 ne sont pas des rendus reçus.",
                " · ".join(audit_links) if audit_links else "Audit indépendant à rattacher avant publication : chemin exact et SHA-256 restant à consigner."]
    plans = {
        "MOTO-ENGINE-COVER-RIGHT-001": (
            ROOT / "creative/research/engine-cover-right/revision-v2-rework-plan.json",
            "À reprendre sur cette v1 : encoches du chant inverse et facettes/ruptures de reflet aux oreilles. Le raccord sombre/pincé entre les bosses reste à diagnostiquer ; sa cause et un écart OEM ne sont pas établis.",
            ROOT / "creative/research/engine-rh-independent-visual-audit.README.md"),
        "MOTO-ENGINE-FILTER-CAP-001": (
            ROOT / "creative/research/engine-filter-cap/revision-v2-rework-plan.json",
            "À recontrôler sur cette v1 : le rebord/biseau haut gauche et les oreilles semblent facettés ou reflètent irrégulièrement. Normales, courbures et raccords restent à diagnostiquer ; aucune correction de forme n’est supposée faite.",
            None),
        "MOTO-ENGINE-COVER-LEFT-001": (
            ROOT / "creative/research/engine-cover-left/revision-v2-rework-plan.json",
            "À recontrôler sur cette v1 : petits plats/pincements et ruptures de reflet localisés sur les oreilles et les lèvres de perçages. Le grand bossage reste globalement continu ; aucune facettisation générale ni cause géométrique ou de normales n’est déduite des images.",
            ROOT / "creative/research/engine-lh-independent-visual-audit.README.md"),
    }
    if component["id"] not in plans or not component["candidate"]:
        return []
    plan_path, text, audit = plans[component["id"]]
    plan = gallery.read_json(plan_path)
    if plan.get("base_source_sha256") != gallery.sha(component["candidate"]["source"]):
        return []  # An old finding never becomes a defect claim about a new SHA.
    links = [link(plan_path, "Plan de reprise de cette révision"), link(audit, "Audit visuel indépendant")]
    return [text, " · ".join(x for x in links if x)]


def validate(document, expected_ids):
    anchors = re.findall(r'<a id="([^"]+)"', document)
    if len(anchors) != len(set(anchors)):
        raise ValueError("Duplicate Markdown component/group anchor")
    for component_id in expected_ids:
        if anchors.count(component_id.lower()) != 1:
            raise ValueError("Missing or duplicated registered component: " + component_id)
    images = 0
    for image, target in re.findall(r'(!?)\[[^\]\n]*\]\(([^)]+)\)', document):
        if target.startswith("#"):
            if target[1:] not in anchors:
                raise ValueError("Missing local Markdown anchor: " + target)
            continue
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc:
            raise ValueError("Only repository-local links allowed")
        path = (OUTPUT.parent / unquote(parsed.path)).resolve()
        if not gallery.within(path, ROOT) or not path.is_file():
            raise ValueError("Missing repository file: " + target)
        if image:
            images += 1
            if not gallery.within(path, gallery.REVIEWS) or path.suffix != ".png":
                raise ValueError("Only proved review PNGs may be embedded")
    return images


def build():
    before = gallery.sha(REGISTER)
    components = exact_components()
    plan = gallery.read_json(gallery.PLAN)
    lots = plan.get("lots", [])
    grouped = {lot["lot"]: [c for c in components if c["lot"] == lot["lot"]] for lot in lots}
    baselines = [c for c in components if c["lot"] not in grouped]
    pending = [lot for lot in lots if not grouped[lot["lot"]]]
    image_count = sum(bool(c["images"]) for c in components)
    lines = ["# Viva Wewa — revue des composants moto", "",
             f"**{len(components)} composants uniques enregistrés · {image_count} vues Blender prouvées · aucune réception artistique.**", "",
             "Une seule vue originale par composant, à la révision exacte de sa fiche. Les anciennes révisions et les sources seulement cataloguées ou gelées sans enregistrement central ne sont pas ajoutées. Ces rendus montrent des candidats isolés, pas le jeu ni une moto terminée.", "",
             "Les dimensions locales et variantes restent estimées ou non confirmées. Les interfaces complètes, les LOD, le coût mobile et Safari sur iPhone physique ne sont pas validés. Un contrôle de fichier ou une importation Babylon ne vaut pas réception de forme ou de matière.", "",
             " · ".join([link(REGISTER, "Registre des composants"), link(gallery.PLAN, "Plan des 18 groupes"), link(gallery.OUTPUT, "Galerie HTML à servir dans un navigateur")]), "",
             "## Les 18 groupes", "",
             f"**{len(pending)} groupes restent sans nouvelle pièce enregistrée dans cette séquence.** Le groupe 14 dispose de candidats antérieurs ci-dessous ; sa compatibilité actuelle reste à recontrôler.", "",
             "| Groupe | Composants enregistrés dans la séquence | État |", "| --- | --- | --- |"]
    for lot in lots:
        entries = grouped[lot["lot"]]
        if entries:
            state = "Candidats partiels en revue ; groupe non terminé"
            count = str(len(entries))
        elif lot.get("legacy_review_scope"):
            state = "Candidats antérieurs existants à recontrôler ; compatibilité restante"
            count = "Voir les préexistants ; aucun nouveau composant compté"
        else:
            state = "À fabriquer ; aucune pièce enregistrée"
            count = "0"
        lines.append(f'| [{lot["lot"]:02d} · {label(lot["label"])}](#groupe-{lot["lot"]}) | {count} | {state} |')

    def render_component(component):
        entry, candidate = component["entry"], component["candidate"]
        title = entry.get("name", component["id"])
        if candidate:
            title = gallery.current_display_text(title, candidate, component["images"])
        rework = known_rework(component)
        state = "candidat à reprendre, non reçu" if rework else "candidat non reçu"
        text = ["", f'<a id="{component["id"].lower()}"></a>', "",
                f'### {label(title)}', "",
                f'`{component["id"]}` · révision `{component["revision"] or "non enregistrée"}` · **{state}**', ""]
        chosen = choose_image(component["images"])
        if chosen:
            text.extend([f'![{label(title)} — {label(component["revision"])}]({href(chosen["path"])})', "",
                         f'{link(chosen["path"], "Image entière")} · {link(chosen["proof"], "Preuve du rendu")} · vue `{chosen["path"].stem}`', "",
                         f'Source SHA-256 : `{gallery.sha(candidate["source"])}`  ',
                         f'PNG SHA-256 : `{gallery.sha(chosen["path"])}`', ""])
        else:
            text.extend(["**Vue Blender exacte manquante : aucun rendu d’une autre révision n’est substitué.**", ""])
        links = [link(candidate["source"], "Blender") if candidate else "",
                 *([link(p, "GLB" if len(candidate["glbs"]) == 1 else p.name) for p in candidate["glbs"]] if candidate else []),
                 link(component["source_readme"], "README source"), link(component["review_readme"], "Revue et limites"),
                 link(component["record_path"], "Fiche")]
        text.extend([" · ".join(x for x in links if x), ""])
        text.extend(rework)
        others = [im for im in component["images"] if not chosen or im["path"] != chosen["path"]]
        if others:
            text.extend(["", "<details>", "<summary>Autres vues Blender prouvées de cette révision</summary>", ""])
            text.extend(f'- {link(im["path"], im["path"].stem)} · {link(im["proof"], "preuve")}' for im in others)
            text.extend(["", "</details>", ""])
        return text

    for lot in lots:
        lines.extend(["", f'<a id="groupe-{lot["lot"]}"></a>', "", f'## {lot["lot"]:02d} · {lot["label"]}', ""])
        entries = grouped[lot["lot"]]
        if entries:
            for component in entries:
                lines.extend(render_component(component))
        elif lot.get("legacy_review_scope"):
            lines.extend(["Les pièces antérieures existent dans la section des [préexistants](#preexistants). La compatibilité de l’ensemble avant reste à recontrôler ; aucun ensemble terminé n’est déclaré.", ""])
        else:
            lines.extend(["**À fabriquer : aucun composant enregistré pour ce groupe.** Une recherche documentaire ne compte pas comme un modèle fini.", ""])
        lines.append("Périmètre prévu : " + "; ".join(lot.get("observable_fabrication_units", [])) + ".")
    lines.extend(["", '<a id="preexistants"></a>', "", "## Préexistants hors décompte de compatibilité des 18 groupes", "",
                  "Ces candidats sont enregistrés et illustrés une seule fois. Leur existence ne certifie pas les raccords de l’ensemble avant ni la réception de la moto."])
    for component in baselines:
        lines.extend(render_component(component))
    lines.extend(["", "---", "", "Régénération : `python tools/build_motorcycle18_markdown_review.py`. Les images restent dans leurs dossiers de preuve ; aucune photographie documentaire privée, image générée ou composition nouvelle n’est utilisée.", ""])
    document = "\n".join(lines)
    checked_images = validate(document, [c["id"] for c in components])
    if checked_images != image_count or before != gallery.sha(REGISTER):
        raise ValueError("Registry changed during generation or image count mismatch")
    OUTPUT.write_text(document, encoding="utf-8")
    return {"output": str(OUTPUT.relative_to(ROOT)), "unique_registered_components": len(components),
            "proved_Blender_images": image_count, "groups_without_new_registered_components": len(pending),
            "component_ids_unique": True, "local_links_valid": True, "register_unchanged": True}


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
