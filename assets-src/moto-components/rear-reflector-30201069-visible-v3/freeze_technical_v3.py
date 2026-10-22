from pathlib import Path
import json,hashlib,datetime
R=Path('/workspace/wewa');k='rear-reflector-30201069-visible-v3';H=R/'assets-src/moto-components'/k;Q=R/'creative/research'/k;O=R/'creative/reviews'/k
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def info(p):return dict(path=str(p.relative_to(R))if p.is_relative_to(R)else str(p),sha256=sha(p),bytes=p.stat().st_size)
def put(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
id='MOTO-REAR-REFLECTOR-30201069-VISIBLE-STUDY-001';package='LEGACY15-REAR-REFLECTOR'
assert not(O/'production-manifest.json').exists()
old=[]
for n,m in [('rear-reflector-30201069-visible-v1','production-manifest-v2.json'),('rear-reflector-30201069-visible-v2','production-manifest.json')]:
 p=R/'creative/reviews'/n/m;a=json.loads(p.read_text())
 for row in a['files']:assert sha(R/row['path'])==row['sha256'],row['path']
 old.append(dict(**info(p),files_verified=len(a['files']),unchanged=True))
par=json.loads((O/'strict-export-parity.json').read_text());rr=json.loads((O/'render-report.json').read_text());preview=json.loads((O/'preview-review.json').read_text());final=json.loads((O/'final-review.json').read_text());eng=json.loads((O/'inspection-boyle-v1/engine-check.json').read_text())
assert final['actually_read']and preview['actually_read']
assert len(rr['views'])==3 and all(v['samples']==96 for v in rr['views'])
assert rr['source_sha256']==sha(H/(k+'.blend'))and rr['export_sha256']==sha(H/(k+'.glb'))==par['V3_sha256']
assert not eng['page_errors']and not eng['http_failures']and eng['exports'][0]['sha256']==par['V3_sha256']
assert par['all_oriented_triangles_positions_normals_exact']and par['both_exported_materials_exact']
assert all(c['max_abs_N_dot_T']<=.001 and c['max_tangent_unit_error']<=.001 and all(w in[-1,1]for w in c['handedness'])for c in par['strict_all_primitive_checks'])
assert all(v['actually_read']for v in final['native96'])and final['runtime_actually_read']
assert json.loads((O/'source-reopen-check.json').read_text())['geometry_normals_faceUV_materials_exact_V2']
assert len(json.loads((O/'raw-render-check.json').read_text())['files'])==5
fragment=json.loads((O/'component-fragment.json').read_text());assert fragment['component_id']==id and fragment['package']==package and 'assets'not in fragment and fragment['review']==k and fragment['files']==[k+'/'+k+'.glb']
fragment.update(revision=k,source_sha256=sha(H/(k+'.blend')),file_sha256=sha(H/(k+'.glb')),same_physical_specimen_as='rear-reflector-30201069-visible-v1',G4_acceptance=False,G5_acceptance=False,G8=False,fit=False,four_interfaces_M5_reverse_unknown=True)
put(O/'component-fragment.json',fragment)
proto=O/'protocols';proto.mkdir(exist_ok=True)
for p in [*H.glob('*.py'),*H.glob('*.mjs'),O/'runtime/index.html',O/'runtime/review_material_v3.js',R/'tools/check_component_raw_exr_v3.py']:(proto/(sha(p)+'-'+p.name)).write_bytes(p.read_bytes())
for n in ['native-export-report.json','preview-render-report.json','render-report.json']:
 h=json.loads((O/n).read_text())['protocol_sha256'];assert list(proto.glob(h+'-*'))
photo=Path('/workspace/wewa-assets/references/rear-reflector-brace-evidence-v1/ru-ref-detail-0.jpg');prior=R/'assets-src/moto-components/rear-reflector-30201069-visible-v2/rear-reflector-30201069-visible-v2.blend'
put(Q/'source-register.json',dict(component_id=id,package=package,previous_native=info(prior),new_native=info(H/(k+'.blend')),prior_freezes_verified=old,physical_source=dict(**info(photo),url='https://www.bajajonline.ru/upload/iblock/c39/f4qnre8bikpkcdxscrkkmtltnxaxxspp.jpg',page='https://www.bajajonline.ru/catalog/item/svetootrazhatel_zadniy_2/',scope='Previously actually viewed in V1/V2; not reopened or reinterpreted for technical UV-only V3; private, no image textures copied.'),dimensions='Inherited 80x50x6mm bounded appearance estimates V1; not OEM measurements',RDC_variant='conditional, not newly confirmed',unknowns=['back','stud/mount','M5 interface positions','seat/contact/fit','optical transport/calibration'],rights='No documentary pixels in repo/model textures; existing mathematical original normal map remains byte-identical.'))
put(Q/'component-record-fragment.json',dict(component_id=id,package=package,revision=k,owner='Boyle',same_single_specimen=True,scope='Native frame UV chart technical correction only',source=fragment['source'],files=fragment['files'],review=k,path_base='assets-src/moto-components for source/files; creative/reviews for review basename',gates=dict(G2='inherited approximate camera; two previews read',G3='all geometry unchanged exact V2',G4='not received; material unchanged exact V2',G5='not received; interfaces unknown',G6='strict all-primitive technical validation and actual Babylon captures complete; no photometric parity claim',G7='not assessed',G8='not received'),art_accepted=False,fit_claim=False))
(H/'README.md').write_text('''# 30201069 — correction technique UV cadre v3

Même exemplaire unique : `MOTO-REAR-REFLECTOR-30201069-VISIBLE-STUDY-001`, package `LEGACY15-REAR-REFLECTOR`. Aucun nouveau modèle physique ni variante. [Revue](../../../creative/reviews/rear-reflector-30201069-visible-v3/README.md).

Le source Blender v2 est ouvert puis seuls les UV de boucles des polygones du cadre sont reprojetés dans le plan dominant de chaque face : X→Y/Z, Y→Z/X, Z→X/Y, avec orientation et tuiles stables. 2400 UV de boucles modifiés ; tous les triangles UV ont une aire non nulle. Les index/séparations de sommets de l'export changent sur le cadre. Aucun changement de positions, triangles orientés, normales natives ou exportées, UV de face, matrices ou matériaux. Aucun retrait d'attribut, normale artificielle, normalmap corrective ou réparation GLB après export.

Réexport officiel Blender4.3.2 avec tangentes : face101T max|N·T|=0 ; cadre816T max|N·T|=0.00009984513, seuil strict0.001 pour chaque tangente. Erreur maximale de normeT=0.00006364431 ; W=+1 partout. Face P/N/UV/T et index identiques à v2, texture normale embarquée identique et JSON des deux matériaux exact. Toute la géométrie exportée est comparée par triangles orientés avec leurs normales, sans effacer le sens de parcours.

Deux aperçus réellement lus et pixels identiques à v2, puis trois vues natives96 et EXRfloat32, réouverture du source et Babylon réel. Les dimensions80×50×6mm restent estimées, variante RDC conditionnelle ; dos et quatre interfaces M5/revers inconnus. G4/G5/G8 non reçus, aucun fit ou transport rétro-optique certifié. V1/v2 et anciens manifestes vérifiés inchangés. Aucun Git/root/catalogue partagé.
''')
(Q/'README.md').write_text('''# Correction technique v3 — même exemplaire30201069

[Plan](technical-plan.json), [sources et inconnues](source-register.json), [fiche locale](component-record-fragment.json), [revue](../../reviews/rear-reflector-30201069-visible-v3/README.md).

Déclencheur : préflight maincoor v2 signale cadre800T max|N·T|0.993643045 malgré face101T dot0. Les UV projetés de v2 écrasaient les chants. Rechart natif des seuls polygones cadre, puis export officiel Blender sans réparation. Aucun assouplissement du seuil, aucun attribut retiré ; toutes les primitives sont contrôlées, même sans normalmap.

Les estimations visuelles, matière et quatre interfaces inconnues restent héritées, sans nouvelle hypothèse de forme, cote, fixation ou routage. Un contrôle technique réussi ne reçoit ni l'apparence G4, ni les interfaces G5, ni G8. Identité unique conservée, source/files du fragment plats relatifs à assets-src/moto-components et review simple basename. Gel SHA et fichiers0444 après tous les contrôles, sans prétention WORM.
''')
(O/'README.md').write_text('''# Réflecteur30201069 v3 — UV cadre uniquement

Identité unique `MOTO-REAR-REFLECTOR-30201069-VISIBLE-STUDY-001` / `LEGACY15-REAR-REFLECTOR`.

**Correction technique vérifiée ; G4/G5/G8 non reçus, aucun fit.** [Fragment PLAT](component-fragment.json) : fichiers relatifs à `assets-src/moto-components`, revue basename. [Plan](../../research/rear-reflector-30201069-visible-v3/technical-plan.json).

## Source et contrôle strict

[Réouverture](source-reopen-check.json), [UV natifs](native-UV-rechart.json), [export/parité stricte](strict-export-parity.json). Le seul rechart touche les boucles des polygones cadre, depuis le source Blender. Face buffers P/N/UV/T + index, texture normale, matériaux et toutes positions/triangles orientés/normales sont identiques à v2. Aucun postrepair GLB, aucune normale ou tangente fabriquée artificiellement, aucun attribut supprimé.

Face101T dot0 ; cadre816T max|N·T|0.00009984513, limite0.001 sur TOUTES les primitives. NormeT erreurmax0.00006364431, W=+1 ; aireUVmin cadre0.00000425361, face0.00048225447. Le cadre a encore des tangentes/UV inutilisés par son matériau, mais ils sont valides. glTF0erreur/0avertissement, deux informations inutilisation conservées.

## Images effectivement relues

[Aperçu large](preview-source-broad.png), [aperçu ponctuel](preview-source-compact.png), [lecture](preview-review.json) : exactement les mêmes pixels natifs que v2, aucun effet visuel du rechart non texturé.

Trois vrais rendus natifs96 du sourcev3 : [large](whole-source-broad.png), [ponctuel](whole-source-compact.png), [neutre HDR](neutral-outdoor.png). [Rapport](render-report.json), [EXR32](raw-render-check.json), [lecture finale](final-review.json). Lumières large/ponctuelle et HDR restent les mêmes protocoles que v2 ; exposition0/gamma1, AgX MediumHighContrast,900×700. Aucune calibration couleur/source.

Babylon réel : [trois-quarts](inspection-boyle-v1/engine-quarter.png), [face](inspection-boyle-v1/engine-driver.png), [coupe revers](inspection-boyle-v1/engine-reverse.png), [paysage](inspection-boyle-v1/engine-landscape-844x390.png), [contrôle](inspection-boyle-v1/engine-check.json), [caméra](native-camera-parity.json). Exportv3 réellement chargé, texture prête, canvas non vide, sans erreurJS/HTTP. Le revers ouvert montre l'omission documentaire, pas une pièce pleine ou un montage. Projection/éclairage moteur différents du natif : aucune parité photométrique ni qualification mobile physique.

## Limites et conservation

Matièrev2 et géométriev1 héritées sans nouvelle réception. Dimensions estimées80×50×6mm, courant RDC conditionnel, les quatre interfaces M5/revers toujours inconnues ; ni goujon, ni siège/contacts, ni dos ajouté. Aucun transport rétro-optique certifié. Anciennes versions/manifestev1v2 intacts vérifiés par SHA. Nouveau manifeste auto-exclu, protocoles snapshotés, fichiers0444 (pasWORM), pasGit/root/cataloguepartagé modifié.
''')
files=[p for d in[H,Q,O]for p in d.rglob('*')if p.is_file()and p.name!='production-manifest.json']
put(O/'production-manifest.json',dict(component_id=id,package=package,same_single_specimen=True,revision=k,frozen_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=[info(p)for p in sorted(files)],previous_freezes=old,self_excluded=True,strict_threshold=.001,all_primitive_tangents_pass=True,root_changed=False,shared_catalog_changed=False,Git_used=False,G4accepted=False,G5accepted=False,G8accepted=False,fit=False,four_interfaces_M5_reverse_unknown=True))
for p in files+[O/'production-manifest.json']:p.chmod(0o444)
print(json.dumps(dict(files=len(files),source_sha256=sha(H/(k+'.blend')),GLB_sha256=sha(H/(k+'.glb')),manifest_sha256=sha(O/'production-manifest.json'))))
