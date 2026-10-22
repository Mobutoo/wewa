import pathlib,json,hashlib,datetime
R=pathlib.Path('/workspace/wewa');key='rear-reflector-30201069-visible-v2';H=R/'assets-src/moto-components'/key;Q=R/'creative/research'/key;O=R/'creative/reviews'/key;id='MOTO-REAR-REFLECTOR-30201069-VISIBLE-STUDY-001';package='LEGACY15-REAR-REFLECTOR';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def info(p):return dict(path=str(p.relative_to(R))if p.is_relative_to(R)else str(p),sha256=sha(p),bytes=p.stat().st_size)
def w(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
v1=R/'creative/reviews/rear-reflector-30201069-visible-v1';oldmanifest=v1/'production-manifest-v2.json';old=json.loads(oldmanifest.read_text())
for r in old['files']:assert sha(R/r['path'])==r['sha256'],r['path']
for p in list(H.glob('*.py'))+list(H.glob('*.mjs'))+[O/'runtime/review_material_v2.js',O/'runtime/index.html',R/'tools/check_component_raw_exr_v3.py']:
 dest=O/'protocols'/(sha(p)+'-'+p.name);dest.write_bytes(p.read_bytes())
for p in [O/'G2-diagnostic-report.json',O/'G2-refined-diagnostic-report.json',O/'geometry-material-parity.json',O/'preview-render-report.json',O/'render-report.json']:
 h=json.loads(p.read_text())['protocol_sha256'];assert list((O/'protocols').glob(h+'-*')),(p,h)
parity=json.loads((O/'runtime-material-parity.json').read_text());geom=json.loads((O/'geometry-material-parity.json').read_text());reopen=json.loads((O/'source-reopen-check.json').read_text());rr=json.loads((O/'render-report.json').read_text());fragment=json.loads((O/'component-fragment.json').read_text())
assert fragment['component_id']==id and fragment['package']==package and 'assets'not in fragment and len(fragment['files'])==1
assert fragment['source_sha256']==sha(H/(key+'.blend')) and fragment['file_sha256']==sha(H/(key+'.glb'))
assert rr['source_sha256']==fragment['source_sha256']and rr['export_sha256']==fragment['file_sha256']
assert geom['before']==geom['after'] and geom['frame_material_before']==geom['frame_material_after']
assert all(v==0 for part in parity['V1_V2_actual_P_N_UV_delta'].values()for v in part.values())
assert all(v['samples']==96 for v in rr['views'])and len(rr['views'])==3
assert parity['glTF_errors']==parity['glTF_warnings']==0
assert json.loads((O/'G2-diagnostic-review.json').read_text())['actually_read']and json.loads((O/'preview-review.json').read_text())['actually_read']
photo=pathlib.Path('/workspace/wewa-assets/references/rear-reflector-brace-evidence-v1/ru-ref-detail-0.jpg')
w(Q/'source-register.json',dict(component_id=id,package=package,source_photo=dict(**info(photo),actually_viewed=True,url='https://www.bajajonline.ru/upload/iblock/c39/f4qnre8bikpkcdxscrkkmtltnxaxxspp.jpg',page='https://www.bajajonline.ru/catalog/item/svetootrazhatel_zadniy_2/',identity='Exact seller30201069, not authenticatedcurrentRDC specimen'),source_native_v1=info(R/json.loads((H/'parameters-v2.json').read_text())['source_v1']),previous_freeze=info(oldmanifest),claims=['UserG4reject and sourcephoto motivate correction, not a physicalalbedo/normal/prism measurement.','Diagonal/staggeredcells observed; apparentdensity36columns/22.5rows artistselected, not measuredcount.','M5 catalogueassociation remains onlynominal; allfourinterfacesM5/rearunknown.'],rights='Photo remains private and never sampled/copied as colour/normal texture. Allcurrent material raster authored mathematically; no photo texture.',scope='Same singleLEGACY15 specimen, v2materialrevision only, no physicalcopy/variant.'))
w(O/'final-review.json',dict(component_id=id,package=package,reviewed_at_utc=now,actually_read=True,diagnostic_then_material=True,previews_actually_read=['preview-source-broad.png','preview-source-compact.png'],native96_actually_read=[v['name']for v in rr['views']],runtime_actually_read=['engine-quarter.png','engine-driver.png','engine-reverse.png'],final_images=[info(O/(v['name']+'.png'))for v in rr['views']],observations=['Source-angle refinement inG2 places longedge closerphoto, rollhypothesis-20deg; not calibrated camera.','V1pattern remained generic under broad/compact lights; face-only apparentnormal material changed afterdiagnostic.','Currentpattern has staggeredrows/diagonalpatches, compactlight deepred with brightplanes; no roundedbeadfield or alternate squareparity.','Broadlight muchbrighter; neutralHDR dimmer; not hidden and not colourcalibrated.','Runtime shows material/density and openreverse; lightingdiffersnative, no pixelidentical claim.'],unchanged=dict(face_geometry_normals_UV=True,frame_geometry_normals_UV=True,worldmatrix=True,frame_material=True,bounds_and_cuts=True,V1_and_manifest_v2=True),G4=dict(status='rework / candidate awaiting user review',artistic_acceptance=False,colour_or_optical_calibration=False,remaining='Uniformdensity and strong specularpatches remain interpretation; sourcecomplexity/markings/opticaltransport not reconstructed.'),G5='blocked/fitnotclaimed',G8=False,four_interfaces_M5_reverse_unknown=True,limitations=['Dimensions andRDC variant inheritedconditionalV1, not improved by materialwork.','No internalprisms, back, stud, seating/contact or markingsinvented.','UnusedV1frameUV and tangents preserved, not valid for normalmap; frame hasno normaltexture. Only usedfaceUV/tangentchart checked.','Originalunusedcolourstudy remains unlinked in source; runtime exports onlynormalPNG, no basecolortexture.']))
w(Q/'component-record-fragment.json',dict(component_id=id,package=package,revision=key,owner='Boyle',same_single_specimen=True,previous_revision='rear-reflector-30201069-visible-v1',scope='Face material correction only; inheritedgeometry/bounds/interfaces',source=fragment['source'],files=fragment['files'],review=fragment['review'],gates=dict(G2='diagnostic read before material; camera approximate, no calibration',G3='unchanged exactV1geometry, not newshape acceptance',G4='rework / userreviewpending',G5='blocked interfacesunknown',G6='technicalsource/runtimeparity checked, not photometric parity',G7='not assessed',G8='notaccepted'),four_interfaces_M5_reverse_unknown=True,active_detailed_fabrication=False,art_accepted=False,fit_claim=False,shared_catalog_not_modified=True))
(H/'README.md').write_text('''# 30201069 — correction matièrev2 du même exemplaire

**component_id `MOTO-REAR-REFLECTOR-30201069-VISIBLE-STUDY-001` ; package `LEGACY15-REAR-REFLECTOR`.** Identité de coordination demandée : le codeLEGACY15 de v1 désigne le même exemplaire. Ce dossier est une révision de matière, pas une deuxième pièce ni une variante.

[Revue](../../../creative/reviews/rear-reflector-30201069-visible-v2/README.md) · [FragmentPLAT](../../../creative/reviews/rear-reflector-30201069-visible-v2/component-fragment.json) · [Plan avant travail](../../../creative/research/rear-reflector-30201069-visible-v2/material-plan-v2.json).

Le sourcev1 est ouvert sans reconstruction, puis la face seule reçoit une interprétation de matériau originale : rangées décalées de plages diagonales, normale1024² produite mathématiquement, couleur linéaire uniforme et réponse spéculaire rouge effective. **Aucun pixel de la photo n’est utilisé.** Ces valeurs ne sont ni un albédo mesuré, ni des normales optiques relevées, ni des prismes reconstruits. Aucune modification/correction du mesh par normalmap.

Empreintes natives avant/après et réouverture : **face et cadre positions/triangles/normales/UV/matrice exacts**, ainsi que matériau du cadre. Les buffersGLBv1/v2 ont également des écartsP/N/UV exactement0, séparément face/cadre. Les dimensions80×50×6mm estimées, coupe arrière et inconnuesRDC de v1 restent inchangées. Aucune pose/montage.

Le diagnosticG2 teste d’abord v1inchangé : ancienangle, hypothèseangle/roulis de source, sourceslarge/ponctuelle, puis correction de roulis. Seulement après lecture du diagnostic : matière, deux aperçuslus, trois vues96lus dont neutre, réouverture et runtime. Les essais refusés trop noirs ou trop ronds sont conservés en revue/rejected-material-attempt-a/b, comme historiques du même exemplaire.

Une seule texture est exportée : `original-staggered-cell-normal.png`, hash vérifié dans leGLB. L’imagecouleur originale d’un essai antérieur reste générée/stockée et son nœud non relié dans le source, **sans utilisation dans la matière actuelle ou leGLB**. BaseColoruniforme100%auteur ; paramètres effectifs exportés documentés, pas de métrologie duJPEG.

La face utilise TEXCOORD0,100trianglesUV non aplatis et101tangentes finies/unitaires/orthogonalesN·T=0 avec W±1. Les UV et tangentes du cadre héritésv1 restent inchangés ;200trianglesUV sans aire y sont inutilisés car ce matériau n’emploie aucune normale/texture. Limite documentée, sans dissimulation ni remise en forme.

G4reste **à revoir/non reçu**, G5interfacesbloquées, aucun fit/G8 ou qualificationiPhone. Les quatreinterfacesM5/revers restent inconnues. Sourcefigure sans dos/goujon/prismes/marquages. Sourcev1+manifestev2 préservésSHA. Aucun Git/root/cataloguepartagé modifié.

Les scripts sont propres à cette révision. `prepare_material_v2.py` est le provisionnement initial historique, pas à relancer sur le gel. `material_pipeline_v2.py` charge les paramètresv2courants, jamais un buildergéométrique ; `check_material_parity_v2.mjs` décode les exportsréels ; `reopen_source_v2.py` vérifie le sourcepersisté. Manifeste en revue, tous fichiersgelés0444.
''')
(O/'README.md').write_text('''# Même LEGACY15-REAR-REFLECTOR — matièrev2

**Candidat de correction matière, pas de réceptionG4/fit/G8.** Coordination : `MOTO-REAR-REFLECTOR-30201069-VISIBLE-STUDY-001`, package `LEGACY15-REAR-REFLECTOR`. V1 et son manifestev2 demeurent intacts.

![Sourceponctuelle — native96](whole-source-compact.png)
![Neutre — native96](neutral-outdoor.png)

[SourceBlender/GLB/paramètres](../../../assets-src/moto-components/rear-reflector-30201069-visible-v2/README.md) · **[FragmentPLAT pour main](component-fragment.json)** · [Décision finale](final-review.json) · [ManifesteSHA](production-manifest.json).

## Diagnostic avant matière

V1mesh/UV/matériaux inchangés : [ancienangle/large](G2-v1-old-angle-broad.png), [premierangle/large](G2-v1-source-angle-broad.png), [premierangle/ponctuelle](G2-v1-source-angle-compact.png). Le premierroulis était trop raide : [anglecorrigé/large](G2-refined-source-broad.png), [anglecorrigé/ponctuelle](G2-refined-source-compact.png). [LectureG2](G2-diagnostic-review.json), [rapportinitial](G2-diagnostic-report.json), [rapportcorrigé](G2-refined-diagnostic-report.json). Angle/roulis sont une hypothèsevisuelle, pas un calage métrique de la photo.

La lumièreponctuelle approfondit déjà le rouge de v1 ; elle ne transforme pas le damier en rangéesdécalées. Modification de matière autorisée seulement après cette lecture. Les essaisA/B refusés (noir/pointsblancs, puis reliefs trop ronds) restent dans `rejected-material-attempt-a/b`. Ce sont des étapes du même exemplaire, pas des pièces supplémentaires.

## Aperçus puis trois vues96

[Large](preview-source-broad.png) et [ponctuelle](preview-source-compact.png) réellement lus, [décision](preview-review.json), avant les rendus96. Rendus96 à900×700 réellement lus : [large](whole-source-broad.png), [ponctuelle](whole-source-compact.png), [neutre](neutral-outdoor.png). [Rapport](render-report.json), [dixEXRFLOAT32 courants](raw-render-check.json).

Les cellules sont décalées, les plages diagonales et le rougeprofond apparaissent sous lumièreponctuelle. La lumièrelarge reste très brillante, et leHDRneutre plus sombre : différences laissées visibles. Densité36×22,5 et paramètres spéculaires sont une interprétationoriginale non calibrée, pas une mesure duJPEG ni une validation rétro-réfléchissante. Aucun marquageinventé, phototexture ou prismeinterne.

## Géométrie et runtime

[Empreintes avant/après](geometry-material-parity.json), [sourcesrouverts](source-reopen-check.json), [GLBv1/v2+UV/tangentesutilisées](runtime-material-parity.json) : **positions/normales/UV/matrice face et cadre inchangés**. Matériau du cadre aussi exact. Export0erreur/0avertissement, deux informations de tangente/UV inutilisées sur cadre non texturé. La face seule utilise la normaleoriginale ;100trianglesUV utiles non aplatis,101tangentesN·T=0.

[Valeursmatières exportées](exported-material-values.json) : facteurbasecouleur uniforme, normalescale0,75, paramètresKHRspecular/clearcoat vérifiés ; pas de basecolortexture copiée. Les graphes natifs du cadre sont identiques. Le source contient aussi une étude couleur auteur non reliée ; leGLB n’embarque que la normaleoriginale courante, sans imagephotographique.

Babylonréel : [troisquarts](inspection-boyle-v1/engine-quarter.png), [face](inspection-boyle-v1/engine-driver.png), [revers](inspection-boyle-v1/engine-reverse.png), [rapport](inspection-boyle-v1/engine-check.json). Le runtime est propre à cette revue ; caméra avec vecteurhaut natif pour le roulis, [correspondance](native-camera-parity.json). Même export chargé, éclairage de revue distinct ; pas de paritéphotométrique ou qualificationmobile revendiquée.

**Les quatre interfacesM5/revers demeurent inconnues**, dos omis comme v1, aucune quincaillerie ou pose. Géométrie estimée/RDCconditionnelle héritéesv1. G4resteàrevoir, G5blocked, G8pending. Le nouvelidentifiant de coordination et LEGACY15 sont deux champs d’une même pièce.

## Conservation

Manifeste auto-exclu et fichiers0444, pasWORM. Protocoles exacts versionnés dans `protocols/`. Photo source et caches privés restent horsdépôt ; aucun anciengel/helperroot ou cataloguepartagé modifié. Aucun Git. Fragmentplat distinct du `runtime-config.json` interne à l’inspecteur, qui n’est pas un cataloguepartagé.
''')
(Q/'README.md').write_text('''# Planmatièrev2 — un seul exemplaire30201069

Identité de coordination `MOTO-REAR-REFLECTOR-30201069-VISIBLE-STUDY-001`, package `LEGACY15-REAR-REFLECTOR` ; v2est une correction de matière du même exemplairev1, jamais une variante ou une deuxième pièce.

[Planavanttravail](material-plan-v2.json), [sources](source-register.json), [fichecoordinationlocale](component-record-fragment.json), [revue](../../reviews/rear-reflector-30201069-visible-v2/README.md). La photo exacte non calibrée a été effectivement vue mais n’a servi ni de texture ni de mesure d’albédo. L’angle/roulis et les sourceslarge/ponctuelle ont été testés et lus avant toute modification du motif.

Le diagnosticmonteun écart de lumière et un motifv1encore générique. Correction de face uniquement : normaleoriginale de plagesdiagonales en rangéesdécalées et réponsecouleur/spéculaire effective non mesurée. Les UV/normales et mesh de la face comme du cadre sont strictement conservés ; la normale ne masque pas un défautmesh. QuatreinterfacesM5/revers toujoursinconnues, pas de constructioninterne ni marquageinventé.

G4non reçu, fit/G8non revendiqués. Paramètresdimensionnels et varianteRDCv1 restentconditionnels. Manifestev1+v2historique vérifié inchangé ; nouveaugelSHA uniquement dans les nouveauxdossiers. PasGit/root/cataloguepartagé.
''')
files=[p for folder in [H,Q,O]for p in folder.rglob('*')if p.is_file()and p.name!='production-manifest.json']
w(O/'production-manifest.json',dict(component_id=id,package=package,same_single_specimen_revision=True,frozen_at_utc=now,files=[info(p)for p in sorted(files)],previous_v1_manifest_v2=info(oldmanifest),private_sources=[info(photo)],self_excluded=True,old_freezes_verified_unchanged=True,root_changed=False,Git_used=False,shared_catalog_changed=False,G4accepted=False,G8accepted=False,four_interfaces_M5_reverse_unknown=True))
for p in files+[O/'production-manifest.json']:p.chmod(0o444)
print(json.dumps(dict(component_id=id,package=package,files=len(files),source_sha256=sha(H/(key+'.blend')),GLB_sha256=sha(H/(key+'.glb')),V1unchanged=True,G4accepted=False)))
