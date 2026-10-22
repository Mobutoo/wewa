import pathlib,json,hashlib,datetime,shutil
R=pathlib.Path('/workspace/wewa');key='rear-reflector-30201069-visible-v1';H=R/'assets-src/moto-components'/key;O=R/'creative/reviews'/key;Q=R/'creative/research'/key
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def info(p):p=pathlib.Path(p);return dict(path=str(p.relative_to(R))if p.is_relative_to(R)else str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def w(p,o):p.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
# Only this component's generated import cache, not other worker files.
if (H/'__pycache__').exists():shutil.rmtree(H/'__pycache__')
for p in list(H.glob('*.py'))+list(H.glob('*.mjs'))+[R/'tools/body_completion_pipeline_v17.py',R/'tools/body_completion_geometry_v15.py',R/'tools/check_body_completion_exports_v3.mjs',R/'tools/check_component_raw_exr_v3.py',R/'tools/front_completion_lab/review.js',R/'tools/front_completion_lab/index.html']:
 dest=O/'protocols'/(info(p)['sha256']+'-'+p.name);dest.write_bytes(p.read_bytes())
plan=json.loads((Q/'G0-G2-plan-v1.json').read_text());w(Q/'source-register.json',dict(component_id='LEGACY15-REAR-REFLECTOR',sources=[plan['source_photo'],plan['context']],catalogue_crossref='creative/research/rear-reflector-30201069-dimensions-v2/source-register.json',rights='Source pixels retained private, no copied photo texture. Authored normal texture is original material interpretation, not reference evidence.',scale_status='Broad artist-selected sensitivity intervals, not source-measured physical bounds',all_source_claims_conditional_RDC=True))
review=dict(component_id='LEGACY15-REAR-REFLECTOR',owner='Boyle',reviewed_at=now,actually_read=True,gray_before_material=True,preview_before_native96=True,native96_views_actually_read=['whole-front','whole-quarter','neutral-outdoor'],Babylon_views_actually_read=['engine-quarter','engine-driver','engine-reverse'],geometry_scope='Visible redface,lip,blackframe and sidewalls only; one open rear boundary, noback/stud/nut/prisms.',source_fidelity=dict(G3='bounded visible candidate, not measured OEM shape',G4='rework: regular normal-map pattern and lighting response do not reproduce source detail; not retroreflective simulation'),fit_claim=False,G8_accepted=False,hardware_qualified=False,limitations=['80x50x6mm authored working estimate; broad uncertain scale intervals not a datasheet.','CurrentRDC identity conditional; no assembly/root transform or contact claim.','Back cut is a review omission, not measured housing wall or actual cavity.','Illegible maker markings not invented; original apparentcell material only.'],technical=dict(triangles=1300,open_boundary_loops=1,glTF_errors=0,glTF_warnings=0,source_GLB_position_delta_m=0,normal_component_max_delta=.00005728006362915039,uv_max_delta=2.9802322387695312e-8,normal_rounding_limit='Exporter rounding, not an exact normal-byte identity',raw_FLOAT32_files=8),failures_retained=['rejected/backface-ambiguous-gray-reverse.png andEXR: firstreverse looked like inventedback, fixedbackfacecut','First capture selected revision rather than legacy identity; failedtimeout private log retained, correctedlocalcapture finalsuccess','Normalmap initially missing explicit tangents, correctedglTF0warnings; no frozenprotocol overwritten'])
w(O/'coordinator-review.json',review)
record=json.loads((R/'creative/workflow/templates/asset-template.json').read_text());record.update(id='LEGACY15-REAR-REFLECTOR',label='30201069 visible rear reflector — Boyle',source_ids=['LEGACY15-REAR-REFLECTOR'],parent_asset=None,recipes=['vehicle','material'],identity=dict(variant='Exactcode seller30201069, related BM125/BM150; currentRDC conditional',variant_confirmed=False,usage='One isolated visible-envelope candidate only',review_distances_m=[.15,.35,.65]),source_register='source-register.json',sources=['Bajajonline30201069','D04','BM1502016','RDC promotional context'],claims=[dict(status='estimated',property='working envelope',value=[80,50,6],unit='mm',source='G0-G2-plan-v1.json'),dict(status='unknown',property='reverse and mounting geometry',value=None)],criteria=['Whole-face/side silhouette candidate documented','No fabricated back/fixing/internal prisms','Original materialpixels only'],gaps=[dict(property='G4 apparent optical cells',status='rework',next='Review original material pattern versus source without asserting optical transport'),dict(property='exactdimension/currentRDCfit',status='unknown',next='Exact specimen or measured document')],source_revision=key,export_revision=key,active_detailed_fabrication=False,next_action='Main review candidate and optional bounded composition; no autoattach/fit/G8.',art_accepted=False)
states={'G0':('passed','One identity, one authorized child'),'G1':('passed','Scoped authored envelope estimates permitted by user; unknown back excluded, not fully documented optics'),'G2':('passed','Localaxes and sensitivityranges documented; graycamera views read, no exactcamera calibration'),'G3':('passed','Visible-envelope candidate technically continuous; source-faithful dimensions not claimed'),'G4':('rework','Regular apparentcell normal material, calibrated/faithful optical response not achieved'),'G5':('blocked','Rear/interface omitted; fit and realoptics unknown'),'G6':('passed','Native96 and actualBabylon read, decodedsourceGLB checks; technicalonly'),'G7':('pending','1300triangles only; no platformbudget/LOD qualification'),'G8':('pending','No userartisticacceptance requested or inferred')}
for g,(st,reason)in states.items():record['gates'][g].update(status=st,revision=key,reviewer='Boyle technical/source-scope review',reviewed_at=now,reason=reason,evidence=[])
w(Q/'component-record-fragment.json',record)
(H/'README.md').write_text('''# LEGACY15-REAR-REFLECTOR — 30201069 visiblev1

Un seul candidat Boyle : face rouge, lèvre, cadre sombre et chants observables. **Dos coupé/ouvert, aucune fixation, goujonM5 ou quincaillerie, aucun prisme interne.** SourceBlender et GLB éditables, un mesh logique / deux matériaux ; aucune intégration root.

Dimensions de travail **80×50×6mm**, estimées. Intervalles de sensibilité et méthode dans [G0–G2](../../../creative/research/rear-reflector-30201069-visible-v1/G0-G2-plan-v1.json) : largeur55–125, hauteur30–70, profondeurvisible2–13mm. Ce sont des hypothèses artistiques volontairement larges, pas des bornes mesurées ni des dimensions constructeur. RDC conditionnelle.

Repère local : XY=plan de face, +Z=extérieur visible ; origine au centre de la coupe arrièreZ0, **pas un ancrage de montage**. FrontièreZ0 volontaire ouverte, non épaisseur de paroi mesurée ; pas de backplate. Géométrie1300triangles,701positions soudées, une boucle ouverte. Les matériaux sont originaux : rouge et cadre, normale512² de cellules apparentes générée mathématiquement, sans aucun pixel source. Pas de simulation ou certification rétro-réfléchissante.

[Revue et images](../../../creative/reviews/rear-reflector-30201069-visible-v1/README.md). Gris lus avant matériau, aperçu studio/neutre lu avant native96, trois rendus96 à900×700, huit EXRFLOAT32, source rouvert, source/GLB et Babylon vérifiés. GlTF0erreur/0avertissement après export des tangentes. Les normales subissent l’arrondi de l’exporteur, delta composante maximal5,73e-5 ; positions identiques et UVdelta2,98e-8.

**G4 à reprendre** : motif trop régulier et réponse sous éclairage différents du véritable objet. L’enveloppe est candidate, pas une réception de fidélité. G5/fit bloqués, G8pending, aucune mesureiPhone. Le README source ne vaut pas autorisation de réplication/pose.

`pipeline_boyle_v1.py` : étapesgeometry,gray,graycut,material,preview,reexport,final ; `presentation_reopen_boyle_v1.py` sauvegarde caméra et96samples puis rouvre sans changer le mesh ; `check_parity_boyle_v1.mjs` compare trianglesévalués/normales/UV à l’export ; `capture_boyle_v1.py` capture le fragment isolé. Aucun helperfrozen modifié ; instantanés exacts en revue/protocols. `freeze_boyle_v1.py` est le producteur du gel, pas une commande à relancer sur cette révision.
''')
(O/'README.md').write_text('''# LEGACY15-REAR-REFLECTOR — candidat visible30201069

**Un exemplaire Boyle, pas de G8 ni fit.** Face/lèvre/cadre construits, dos inconnu omis par coupe ouverte. Dimensions80×50×6mm estimées avec larges intervalles explicites. Matière optique originale interprétée ; **G4rework**, motif encore trop régulier par rapport à la source physique.

![Candidat entier, native96](whole-quarter.png)
![Ciel neutre, native96](neutral-outdoor.png)
![Coupe de revue arrière, gris corrigé](gray-reverse.png)

[Source/GLB/paramètres](../../../assets-src/moto-components/rear-reflector-30201069-visible-v1/README.md) · [G0–G2 et méthode d’estimation](../../research/rear-reflector-30201069-visible-v1/G0-G2-plan-v1.json) · [Fragment unique](catalog-fragment.json) · [Décision détaillée](coordinator-review.json).

Séquence effectivement suivie : gris [face](gray-front.png), [quart](gray-quarter.png) et [coupe](gray-reverse.png) lus avant matériau, [gray-review](gray-review.json) ; [aperçu studio](preview-studio.png) et [neutre](preview-neutral.png) lus avant96, [preview-review](preview-review.json). [Face96](whole-front.png), quart96 et neutre96 lus. Le premier revers ambigu est conservé dans `rejected/`, pas présenté comme dos physique.

[Parité source/GLB](export-buffer-check.json), [géométrie gray/matériau et validationglTF](independent-export-check.json), [réouverture native](native-reopen-check.json), [rendus96](render-report.json), [EXRFLOAT32](raw-render-check.json). Les checks techniques ne valident ni cotes constructeur, ni apparence optique, ni interfaces. Shaderbackfaces masqués sur la coupegrise ; GLB matériaux simpleface, dos non fabriqué.

Babylon réel : [quart](inspection-boyle-v1/engine-quarter.png), [face](inspection-boyle-v1/engine-driver.png), [revers coupé](inspection-boyle-v1/engine-reverse.png), [rapport](inspection-boyle-v1/engine-check.json). Chromium logicielWebGL, aucun matérielmobile/FPS qualifié. Contrôlesdepage et capture locaux au composant ; aucun catalogue partagé ou rootmodifié.

Une seule identité dans le fragment : `LEGACY15-REAR-REFLECTOR`. Normale originale512² incluse GLB, aucun pixel documentaire ; source privée exclusivement. Pas de marquages constructeur inventés, de goujon/écrouM5, de verre/réflecteur avant ou de prismesinternes. Les éléments inconnus demeurent inconnus malgré la présence d’un candidat visible.

GelSHA256 `production-manifest.json`, source/recherche/revue/protocols et sorties exacts. Lecture seule0444, pasWORM. G4rework, G5blocked, G8pending. Aucune réception/pose transmise par les autres composants.
''')
(Q/'README.md').write_text('''# Préparation du candidat LEGACY15-REAR-REFLECTOR

Une seule fabrication autorisée à Boyle, indépendante de bavetteMencius/cacheNash. Le [planG0–G2](G0-G2-plan-v1.json) déclare les estimations avant construction, la caméra, les sources et les inconnues. [Registre](source-register.json), [fiche composant locale](component-record-fragment.json), [revue](../../reviews/rear-reflector-30201069-visible-v1/README.md).

Les recherches historiques `rear-reflector-brace-evidence-v1` et `rear-reflector-30201069-dimensions-v2` restent gelées. Elles n’ont fourni aucune cote exacte ; la nouvelle autorisation accepte des hypothèses dimensionnelles bornées et justifiées pour la seule enveloppe visible. Le contexteRDC est une aide d’ordre de grandeur conditionnelle, pas une mesure. La fixationM5 de famille n’autorise aucun revers ou goujon. Toute composition éventuelle reste conditionnelle, sans autoattache ni fit.

Les paramètres80×50×6mm et leurs intervalles sont des hypothèses de revue, pas des intervalles de confiance ou contraintes OEM. Matériau original apparent, pas transfert de phototexture. G4rework explicite : le candidat n’est pas déclaré fidèle à l’optique réelle.

Aucun Git, root, catalogue partagé ou autre parent modifié. Fiche et fragment uniquement dans ces nouveaux dossiers. Le manifeste de production en revue couvre ce dossier ; pas de second modèle créé.
''')
# Tangents finite and orthogonal tested separately by checker; preserve all protocol hashes used by reports.
for name in ['gray-render-report.json','graycut-render-report.json','preview-render-report.json','render-report.json']:
 h=json.loads((O/name).read_text())['protocol_sha256'];assert list((O/'protocols').glob(h+'-*')),(name,h)
assert list(json.loads((O/'catalog-fragment.json').read_text())['assets'])==['LEGACY15-REAR-REFLECTOR']
files=[p for folder in [H,Q,O]for p in folder.rglob('*')if p.is_file()and p.name!='production-manifest.json']
w(O/'production-manifest.json',dict(component_id='LEGACY15-REAR-REFLECTOR',owner='Boyle',frozen_at_utc=now,files=[info(p)for p in sorted(files)],private_sources=[plan['source_photo'],plan['context']],self_excluded=True,root_changed=False,Git_used=False,shared_catalog_changed=False,G8_accepted=False))
for p in files+[O/'production-manifest.json']:p.chmod(0o444)
print(json.dumps(dict(component_id='LEGACY15-REAR-REFLECTOR',files=len(files),source_sha256=info(H/(key+'.blend'))['sha256'],GLB_sha256=info(H/(key+'.glb'))['sha256'],G4='rework',G8='pending')))
