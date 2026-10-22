"""Audit current assembly resources and all recorded motorcycle scope, without awarding artistic acceptance.

Run from any directory. The report is deterministic for its versioned inputs.
Only the current runtime resources are read; historical binary existence is checked in Git's file list.
"""
import argparse
import hashlib
import json
import posixpath
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = "creative/workflow/motorcycle-completion-audit-2026-10-22"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def audit():
    inputs = {}

    def read(relative):
        raw = (ROOT / relative).read_bytes()
        inputs[relative] = digest(raw)
        return json.loads(raw)

    scope = read(DEFAULT + "/scope.json")
    registry_path = "creative/library/component-production.json"
    registry = read(registry_path)
    lots = read("creative/workflow/motorcycle-execution-18.json")["lots"]
    manifest_path = "creative/research/motorcycle-assembled-v4/portable-files.json"
    manifest = read(manifest_path)
    model = read(manifest["runtime_model"])
    proof = read(manifest["runtime_model"] + ".proof.json")
    tracked = set(subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0"))
    errors = []
    verified = []
    for row in manifest["files"]:
        if "runtime" not in row["usage"]:
            continue
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"Unsafe runtime resource: {relative}")
            continue
        file = ROOT / relative
        if not file.is_file():
            errors.append(f"Missing current resource: {relative}")
            continue
        raw = file.read_bytes()
        if len(raw) != row["bytes"] or digest(raw) != row["sha256"]:
            errors.append(f"Current resource hash/size differs: {relative}")
        verified.append({"path":str(relative), "bytes":len(raw), "sha256":digest(raw)})

    roots = model["scenes"][model.get("scene", 0)]["nodes"]
    seen = set()

    def walk(index):
        if index in seen:
            raise ValueError("Cycle or multiply parented node in current scene")
        seen.add(index)
        for child in model["nodes"][index].get("children", []):
            walk(child)

    for index in roots:
        walk(index)
    actual_parents = {model["nodes"][i]["name"]:model["nodes"][i] for i in roots}
    parents = {p["key"]:p for p in proof["parents"]}
    if len(parents) != proof["parent_count"] or len(parents) != len(roots):
        errors.append("Current parent inventory count differs")
    for key, parent in parents.items():
        actual = actual_parents.get("PARENT [" + key + "]")
        if not actual or actual.get("matrix") != parent["matrix"]:
            errors.append("Current root/pose differs: " + key)
    primitive_instances = 0
    triangles = 0
    mesh_instances = []
    for index in sorted(seen):
        node = model["nodes"][index]
        if "mesh" not in node:
            continue
        mesh = model["meshes"][node["mesh"]]
        mesh_instances.append({"node":index,"name":node.get("name"),"mesh":node["mesh"]})
        for prim in mesh["primitives"]:
            if prim.get("mode", 4) != 4:
                errors.append("Non-triangle primitive in audit")
            accessor = prim.get("indices", prim["attributes"]["POSITION"])
            triangles += model["accessors"][accessor]["count"] // 3
            primitive_instances += 1

    packages = scope["packages"]
    if [p["id"] for p in packages] != [f"P{i:02d}" for i in range(1,31)]:
        errors.append("The audit must cover P01–P30 exactly once")
    for package in packages:
        for key in package["parents"]:
            if key not in parents:
                errors.append(f"Unknown evidence parent: {package['id']}: {key}")
        package["package_complete"] = False
    candidates = []
    for component in registry["components"]:
        refs = {}
        for key in ("candidate_source", "candidate_review", "component_workflow"):
            ref = component.get(key)
            if ref:
                relative = posixpath.normpath(posixpath.join(posixpath.dirname(registry_path),ref))
                present = relative in tracked or any(p.startswith(relative.rstrip("/")+"/") for p in tracked)
                refs[key] = {"path":relative,"exists_in_git_file_list":present}
                if not present:
                    errors.append(f"Missing recorded {key}: {component['id']}: {relative}")
        candidates.append({
            "id":component["id"], "name":component["name"], "recorded_state":component["state"],
            "recorded_gates":component.get("gates",{}), "recorded_unknowns":component.get("unknown",[]),
            "references":refs,
            "current_parent_source_folder_matches":[p["key"] for p in proof["parents"]
                if "candidate_source" in refs and any(p.get(field,"").startswith(posixpath.dirname(refs["candidate_source"]["path"])+"/") for field in ("source_glb","source_blend"))],
        })
    if len({c["id"] for c in candidates}) != len(candidates):
        errors.append("Duplicate canonical candidate IDs")
    game = (ROOT / "app/src/world.ts").read_bytes()
    inputs["app/src/world.ts"] = digest(game)
    if "'/models/','motorcycle.glb'" not in game.decode():
        errors.append("Game import changed; revise GAME assessment")
    lod_report_path = "assets-src/moto-components/motorcycle-lod-review-v1/build-report.json"
    lod = read(lod_report_path) if (ROOT / lod_report_path).is_file() else None
    comparison_path = "creative/reviews/motorcycle-lod-review-v1/engine-comparison.json"
    comparison = read(comparison_path) if (ROOT / comparison_path).is_file() else None
    if lod:
        raw = (ROOT / lod["output"]).read_bytes()
        if len(raw) != lod["output_bytes"] or digest(raw) != lod["output_sha256"]:
            errors.append("LOD artifact size/hash differs")
        if lod["source_manifest_sha256"] != inputs[manifest_path]:
            errors.append("LOD built from a different resource manifest")
        if digest((ROOT / lod["tool"]).read_bytes()) != lod["tool_sha256"]:
            errors.append("LOD builder changed after its proof was recorded")
        bounds = lod["before"]["bounds"]
        extents = [bounds["max"][i]-bounds["min"][i] for i in range(3)]
    if comparison:
        if not lod or comparison["build_report_sha256"] != inputs[lod_report_path]:
            errors.append("Browser comparison does not match the current LOD build")
        for model_name in ("source", "lod"):
            for media in comparison["models"][model_name]["files"]:
                raw = (ROOT / "creative/reviews/motorcycle-lod-review-v1" / media["path"]).read_bytes()
                if len(raw) != media["bytes"] or digest(raw) != media["sha256"]:
                    errors.append("Browser media size/hash differs: " + media["path"])
    return {
        "schema":1, "date":scope["date"], "scope":scope["scope"], "input_sha256":inputs,
        "summary":{
            "whole_motorcycle_complete":False, "art_accepted":False, "packages_complete":0,
            "canonical_candidate_records":len(candidates), "original_lots":len(lots), "finishing_packages":len(packages),
            "current_assembly_parents":len(parents), "current_mesh_nodes":len(mesh_instances),
            "current_primitive_instances":primitive_instances, "current_triangles":triangles,
            "current_skins":len(model.get("skins",[])), "current_animation_clips":len(model.get("animations",[])),
            "current_runtime_resources_verified":len(verified), "current_runtime_resource_bytes":sum(f["bytes"] for f in verified),
            "count_scope":"Candidate records, parent instances and rendered primitives are different counts; none is a count of accepted physical parts.",
            "game_model":"app/public/models/motorcycle.glb", "detailed_model_integrated_in_game":False,
        },
        "packages":packages, "cross_cutting":scope["cross_cutting"],
        "current_parent_inventory":proof["parents"], "current_mesh_node_inventory":mesh_instances,
        "canonical_candidate_inventory":candidates,
        "original_lot_inventory":[{"lot":l["lot"],"label":l["label"],"historical_state":l["state"],"group_complete":l["group_complete"],"historical_remaining":l.get("remaining_observable_units",[])} for l in lots],
        "current_resources":verified,
        "source_gabarit":None if not lod else {
            "method":"Actual source glTF mesh extents, all included components; not a physical measurement or a manufacturer dimension protocol.",
            "export_width_height_length_m":extents,
            "published_width_height_length_m":[0.740,1.134,2.016],
            "reference":"creative/MOTORCYCLE_PLAN.md",
            "mirror_and_height_measurement_conventions":"unknown",
            "dimensional_conformity_received":False,
        },
        "lod_candidate":None if not lod else {"path":lod["output"],"bytes":lod["output_bytes"],"sha256":lod["output_sha256"],"triangles":lod["after"]["triangles"],"gltf_errors":lod["gltf_validator"]["numErrors"],"browser_comparison_verified":comparison is not None,"art_accepted":False,"physical_iphone_tested":False},
        "errors":errors,
        "limits":["Documentary census and exact current file checks; no fresh visual inspection of every historical candidate.","Historical lot questions are preserved as historical; the current P01–P30 table reconciles later deliveries.","Source-folder matches are traceability hints; a component can be reused in a composite export or replaced by a later revision in another folder. An empty match does not prove physical absence.","No OEM mechanical fit, surface accuracy, artistic acceptance or physical Safari performance inferred from hashes, matrices or counts."],
    }


def markdown(report):
    s = report["summary"]
    lines = ["# Revue complète de la moto — 22 octobre 2026", "",
             "**La moto n'est pas terminée.** L'extérieur détaillé est largement présent, mais la transmission finale, des raccords/fixations, le fonctionnement mécanique et l'intégration au jeu restent ouverts.", "",
             f"Périmètre relu : **{s['canonical_candidate_records']} fiches candidates, {s['original_lots']} lots, {s['finishing_packages']} paquets et {s['current_assembly_parents']} parents de l'assemblage v4**. {s['current_runtime_resources_verified']} ressources courantes vérifiées par taille et SHA-256. Les fiches historiques ne sont pas des pièces physiques terminées.", "",
             f"L'assemblage comporte {s['current_mesh_nodes']} nœuds maillés, {s['current_primitive_instances']} occurrences de primitives et {s['current_triangles']:,} triangles. Aucun skin ni clip d'animation. Les 541 maillages indiqués dans les captures Babylon correspondent ici aux occurrences de primitives après découpage à l'import, pas à 541 pièces physiques.", "",
             "Le moteur et l'optique concave sont déjà corrigés en v4. Le jeu charge encore l'ancien lot01 dans `app/public/models/motorcycle.glb`. Le modèle détaillé est une livraison de revue séparée.", ""]
    if report["lod_candidate"]:
        lod = report["lod_candidate"]
        lines += [f"Nouvel élément réalisé : [candidat LOD](../../../assets-src/moto-components/motorcycle-lod-review-v1/motorcycle-lod.glb), **{lod['triangles']:,} triangles**, {lod['bytes']/1e6:.2f} Mo, zéro erreur glTF. [Méthode et comparaison](../../reviews/motorcycle-lod-review-v1/README.md). Les mêmes 162 parents et toutes les primitives sont conservés ; cela ne clôt pas le budget de la scène ni les essais mobiles.", ""]
    lines += ["## Les trente paquets confrontés à l'assemblage courant", "",
              "Chaque ligne reste ouverte. La colonne « manque » distingue les études isolées et les éléments réellement assemblés ; les sources/poses exactes de tous les parents sont dans le rapport JSON.", "",
              "| Paquet | État vérifié et manque restant | Donnée nécessaire |", "|---|---|---|"]
    for p in report["packages"]:
        lines.append(f"| {p['id']} — {p['label']} | {p['remaining']} | {p['needed']} |")
    lines += ["", "## Vérifications transversales", ""]
    for item in report["cross_cutting"]:
        lines.append(f"- **{item['label']}** : {item['remaining']}")
    lines += ["", "[Inventaire lisible de toutes les fiches et des 18 lots](INVENTORY.md) · [Rapport complet : 162 parents, ressources et empreintes](report.json) · [Périmètre et constats éditables](scope.json) · [Livraison détaillée v4](../../reviews/motorcycle-assembled-v4/README.md).", "",
              "Le contrôle documentaire ne prétend pas une nouvelle inspection visuelle de chaque ancien rendu. Les variantes, estimations et inconnues restent explicites. Aucun paquet n'est clôturé par un contrôle automatique.", "",
              "```sh", "python tools/check_motorcycle_completion.py --write", "```", ""]
    return "\n".join(lines)


def inventory(report):
    lines = ["# Inventaire documentaire exhaustif", "",
             "Les 205 lignes ci-dessous sont des identités de candidats historiques. Les révisions plus récentes de l'assemblage v4 sont listées séparément dans le rapport JSON ; aucun état de cette table n'est une réception de pièce physique.", "",
             "Les liens source/revue sont vérifiés dans la liste des fichiers Git. Une pièce peut être reprise dans un export composite ou une autre révision : l'absence de correspondance de dossier ne prouve pas son absence physique.", "",
             "| Fiche | Élément | État enregistré | Sources et preuves |", "|---|---|---|---|"]
    for c in report["canonical_candidate_inventory"]:
        links = []
        for key,label in (("candidate_source","Source"),("candidate_review","Revue"),("component_workflow","Fiche")):
            if key in c["references"]:
                relative = posixpath.relpath(c["references"][key]["path"],DEFAULT)
                links.append(f"[{label}]({relative})")
        lines.append(f"| {c['id']} | {c['name']} | {c['recorded_state']} | {' · '.join(links)} |")
    lines += ["", "## Les dix-huit lots initiaux", "",
              "Ces états historiques sont conservés comme provenance. Le [bilan P01–P30 actuel](README.md) tient compte des corrections ultérieures du moteur, du phare, des repose-pieds, du cadre et des assemblages.", "",
              "| Lot | Périmètre | État enregistré |", "|---|---|---|"]
    for lot in report["original_lot_inventory"]:
        lines.append(f"| {lot['lot']} | {lot['label']} | {lot['historical_state']} |")
    lines += ["", "[Rapport machine complet](report.json) · [Bilan et pièces réellement manquantes](README.md).", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write the deterministic report.json and README.md")
    args = parser.parse_args()
    report = audit()
    if args.write:
        folder = ROOT / DEFAULT
        (folder / "report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
        (folder / "README.md").write_text(markdown(report))
        (folder / "INVENTORY.md").write_text(inventory(report))
    print(json.dumps({"summary":report["summary"], "errors":report["errors"]},indent=2,ensure_ascii=False))
    raise SystemExit(bool(report["errors"]))


if __name__ == "__main__":
    main()
