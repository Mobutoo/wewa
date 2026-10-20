import './style.css';
import {GameWorld} from './world';
import {Simulation} from './simulation';
import {StreetAudio} from './audio';
import {emptyControls,type Controls,type Mode,type WorldData} from './types';
import {distance} from './math';

const icon=(name:string)=>`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${({play:'<path d="m9 5 10 7-10 7z" fill="currentColor" stroke="none"/>',pause:'<path d="M8 5v14M16 5v14" stroke-width="4"/>',camera:'<path d="M4 6h4l2-2h4l2 2h4v14H4z"/><circle cx="12" cy="13" r="4"/>',sound:'<path d="M11 4 5 9H2v6h3l6 5zM15 8a6 6 0 0 1 0 8M18 4a11 11 0 0 1 0 16"/>',arrow:'<path d="M5 12h14m-6-6 6 6-6 6"/>',left:'<path d="m15 5-7 7 7 7"/>',right:'<path d="m9 5 7 7-7 7"/>',up:'<path d="m5 15 7-7 7 7"/>',down:'<path d="m5 9 7 7 7-7"/>',bolt:'<path d="m14 2-9 12h7l-2 8 9-13h-7z"/>',close:'<path d="m6 6 12 12M6 18 18 6"/>',reset:'<path d="M4 10a8 8 0 1 1 2 8M4 4v6h6"/>',pin:'<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2"/>',horn:'<path d="m4 10 13-5v14L4 14zM4 10H2v4h2m4 1 2 6h4l-2-5M20 8l3-2m-3 10 3 2m-3-6h3"/>'} as Record<string,string>)[name]||''}</svg>`;
const modes:{id:Mode;num:string;title:string;description:string;tag:string}[]=[
  {id:'rush',num:'01',title:'Wewa Rush',description:'30 secondes. Des colis. Ton meilleur passage.',tag:'COURSE EXPRESS'},
  {id:'delivery',num:'02',title:'La tournée',description:'Six colis à livrer. La rue ne t’attendra pas.',tag:'LIVRAISON'},
  {id:'story',num:'03',title:'Le dernier appel',description:'Un taxi jaune. Un message de Mado. Une piste.',tag:'HISTOIRE'},
  {id:'free',num:'04',title:'Kin à ton rythme',description:'Rouler, écouter, trouver les raccourcis.',tag:'BALADE'}
];
interface Save {record:number;runs:number;camera:boolean;comfort:boolean;fov:boolean;shake:boolean;music:boolean;sound:boolean;voices:boolean;storyComplete:boolean}
const defaultSave:Save={record:0,runs:0,camera:false,comfort:true,fov:true,shake:false,music:true,sound:true,voices:false,storyComplete:false};
let save:Save={...defaultSave};
try{save={...defaultSave,...JSON.parse(localStorage.getItem('viva-wewa.v1')||'{}')};}catch{/* Private browsing may deny persistence. */}
const persist=()=>{try{localStorage.setItem('viva-wewa.v1',JSON.stringify(save));}catch{/* Playing remains possible without storage. */}};
const app=document.querySelector<HTMLDivElement>('#app')!;
app.innerHTML=`
  <canvas id="world" aria-label="Jeu de conduite Viva Wewa"></canvas>
  <section id="home" class="screen home">
    <picture class="keyart"><source media="(max-width:700px)" srcset="/art/viva-wewa-keyart-960.webp"><img src="/art/viva-wewa-keyart.webp" alt="Pilote Wewa et passagère, minibus et rue animée de Kinshasa au soleil couchant"></picture>
    <div class="home-shade"></div>
    <header class="home-header"><a class="mini-logo" href="/" aria-label="Viva Wewa, accueil">VW<span>®</span></a><span class="location-label">${icon('pin')}KINSHASA, RDC <i></i> GOMBE</span><span class="edition">LE PASSAGE EST À TOI.</span></header>
    <div class="home-copy"><span class="eyebrow"><span class="tiny-line"></span> UNE VILLE. MILLE PASSAGES.</span><h1><span>VIVA</span><strong>WEWA<span class="logo-dot">.</span></strong></h1><p>La ville est vivante.<br>À toi de trouver le passage.</p><div class="home-flavour"><span>DU BRUIT.</span><span>DU RYTHME.</span><span>DU CULOT.</span></div></div>
    <div class="mode-dock"><div class="dock-title"><span>CHOISIS TON DÉPART</span><span class="dock-rule"></span><span id="home-record">RECORD RUSH · ${save.record}</span></div><div class="mode-grid">${modes.map((m,i)=>`<button class="mode-card ${i===0?'selected':''}" data-mode="${m.id}" aria-pressed="${i===0}"><span class="mode-num">${m.num}</span><div><small>${m.tag}</small><h2>${m.title}</h2><p>${m.description}</p></div><span class="mode-indicator">${icon('arrow')}</span></button>`).join('')}</div><div class="dock-bottom"><span class="control-hint"><kbd>ZQSD</kbd> / <kbd>WASD</kbd> ou tactile <span>·</span> <kbd>MAJ</kbd> nitro <span>·</span> <kbd>C</kbd> caméra</span><button id="play" class="primary">ENTRER DANS KIN ${icon('arrow')}</button></div></div>
    <footer class="home-footer"><span>VIVA WEWA <span class="small-cross">✳</span> KINSHASA À MOTO</span><span>PRÉVERSION JOUABLE <i></i> CHAPITRE GOMBE</span></footer>
  </section>
  <section id="hud" class="hidden" aria-label="Tableau de bord">
    <div class="hud-top"><div class="hud-brand">VIVA<br><b>WEWA.</b></div><div class="street"><span>GOMBE / KINSHASA</span><strong id="street-name">La rue t’attend</strong></div><div class="objective"><span id="mode-label">WEWA RUSH</span><strong id="objective-text">Récupère les colis. Freine au relais.</strong></div><div class="hud-actions"><button id="camera" class="icon-button" aria-label="Changer de caméra">${icon('camera')}</button><button id="sound" class="icon-button" aria-label="Activer ou couper le son">${icon('sound')}</button><button id="pause" class="icon-button" aria-label="Mettre en pause">${icon('pause')}</button></div></div>
    <div id="countdown" aria-live="polite"></div><div id="callout" role="status"><span>LA RUE TE PARLE</span><p></p></div>
    <div class="run-stats"><div><small id="time-caption">SECONDES</small><strong id="timer">30<span>.0</span></strong></div><div class="stat-divider"></div><div><small>SCORE</small><strong id="score">0000</strong></div><div class="combo" id="combo">×1</div></div>
    <div class="ride-data"><div class="speed"><strong id="speed">0</strong><span>KM/H</span></div><div class="nitro-meta"><span>${icon('bolt')} NITRO</span><span id="cargo">0 / 3 COLIS</span></div><div class="nitro-track"><i id="nitro-fill"></i></div><span class="keyboard-help">ESPACE · FREIN &nbsp; H · KLAXON &nbsp; R · REPRISE</span></div>
    <div class="minimap-wrap"><canvas id="minimap" width="240" height="240" aria-label="Carte du parcours"></canvas><span class="map-north">N ↑</span><span class="map-title">GOMBE <i></i> TON QUARTIER</span><div class="map-key"><i></i> TOI <i></i> COLIS <i></i> RELAIS</div></div>
    <div id="touch-controls"><div class="touch-steering"><button data-input="left" aria-label="Tourner à gauche">${icon('left')}</button><button data-input="right" aria-label="Tourner à droite">${icon('right')}</button></div><button data-input="horn" class="touch-horn" aria-label="Klaxonner">${icon('horn')}</button><div class="touch-pedals"><button data-input="nitro" class="touch-nitro" aria-label="Activer le nitro">${icon('bolt')}<span>NITRO</span></button><button data-input="brake" class="touch-brake" aria-label="Freiner ou reculer">${icon('down')}<span>FREIN</span></button><button data-input="gas" class="touch-gas" aria-label="Accélérer">${icon('up')}<span>GAZ</span></button></div></div>
    <div id="nitro-vignette"></div><div id="loading" class="hidden">Le quartier se réveille…</div>
  </section>
  <section id="pause-panel" class="screen modal hidden"><div class="modal-card"><span class="eyebrow">ON SOUFFLE UN PEU.</span><h2>La rue peut<br>attendre.</h2><div class="settings"><label><input type="checkbox" id="comfort"> Mode Confort <small>Horizon calme, effets réduits</small></label><label><input type="checkbox" id="fov"> Effet de vitesse <small>Variation du champ de vision</small></label><label><input type="checkbox" id="shake"> Vibrations de caméra</label><label><input type="checkbox" id="music"> Musique originale</label><label><input type="checkbox" id="voices"> Appels parlés <small>Voix française du téléphone, si disponible</small></label></div><div class="pause-controls">ZQSD / WASD · conduire &nbsp; MAJ · nitro<br>C · caméra &nbsp; H · klaxon &nbsp; R · reprise<br>P / ÉCHAP · pause</div><button id="resume" class="primary">REPRENDRE ${icon('play')}</button><div class="button-row"><button id="restart" class="secondary">${icon('reset')} RECOMMENCER</button><button id="menu" class="secondary">ACCUEIL</button></div><button id="credits-toggle" class="text-button">Crédits et progression</button><div id="credits" class="hidden"><p>Géographie : © contributeurs OpenStreetMap, ODbL. Modèles de Gombe issus du kit fourni. Illustration, moto et sons de maquette créés pour Viva Wewa. Personnages et missions fictifs.</p><button id="reset-save" class="text-button">Effacer la progression locale</button><button id="export-diagnostic" class="text-button">Exporter le diagnostic de session</button></div></div></section>
  <section id="results" class="screen modal hidden"><div class="modal-card result-card"><span class="eyebrow" id="result-kicker">LE PASSAGE ÉTAIT À TOI.</span><h2 id="result-title">Bien joué,<br>Wewa !</h2><div class="result-score" id="result-score">0</div><div class="result-stats"><span><b id="result-deliveries">0</b> COLIS LIVRÉS</span><span><b id="result-collisions">0</b> ACCROCS</span><span><b id="result-best">0</b> RECORD</span></div><p id="result-description"></p><button id="replay" class="primary">ON REPART ${icon('reset')}</button><button id="result-menu" class="secondary">CHOISIR UN AUTRE DÉPART</button><small>Chaque nouvelle tentative est gratuite.</small></div></section>
`;
const $=<T extends HTMLElement=HTMLElement>(selector:string)=>document.querySelector<T>(selector)!;
let selected:Mode='rush',sim:Simulation|null=null,world:GameWorld|null=null,data:WorldData|null=null;
let controls=emptyControls(),playing=false,starting=false,lastFrame=0,hudTime=0,finishedSaved=false;
const audio=new StreetAudio();
const inputPointers=new Map<number,keyof Controls>(),keys=new Set<string>();
const labels:Record<Mode,string>={rush:'WEWA RUSH',delivery:'LA TOURNÉE',story:'LE DERNIER APPEL',free:'KIN À TON RYTHME'};
function clearInput(){keys.clear();inputPointers.clear();controls=emptyControls();document.querySelectorAll('[data-input]').forEach(b=>b.classList.remove('pressed'));if(sim)sim.vehicle.boosting=false;}
function rebuildInput(){controls=emptyControls();const mapping:Record<string,keyof Controls>={w:'gas',z:'gas',arrowup:'gas',s:'brake',arrowdown:'brake',' ':'brake',a:'left',q:'left',arrowleft:'left',d:'right',arrowright:'right',shift:'nitro',h:'horn'};for(const key of keys){if(mapping[key])controls[mapping[key]]=true;}for(const input of inputPointers.values())controls[input]=true;}
function pause(){if(!sim||!playing||sim.phase==='finished')return;clearInput();sim.pause(true);audio.pause();$('#pause-panel').classList.remove('hidden');}
function resume(){if(!sim)return;clearInput();sim.pause(false);lastFrame=performance.now();$('#pause-panel').classList.add('hidden');void audio.start();}
function home(){clearInput();sim?.pause(true);audio.pause();playing=false;$('#hud').classList.add('hidden');$('#home').classList.remove('hidden');$('#pause-panel').classList.add('hidden');$('#results').classList.add('hidden');$('#world').classList.remove('active');$('#home-record').textContent=`RECORD RUSH · ${save.record}`;}
function applySettings(){if(world){world.comfort=save.comfort;world.fovEffect=save.fov;world.shake=save.shake;world.setCamera(save.camera);}audio.enabled=save.sound;audio.music=save.music;audio.voices=save.voices;for(const setting of ['comfort','fov','shake','music','voices'] as const)$<HTMLInputElement>('#'+setting).checked=save[setting];$('#sound').classList.toggle('muted',!save.sound);}
const dataPromise=fetch('/world/gombe.json').then(r=>{if(!r.ok)throw new Error('Le quartier ne peut pas être chargé. Vérifie ta connexion.');return r.json() as Promise<WorldData>;});
async function start(){
  if(starting)return;starting=true;const button=$<HTMLButtonElement>('#play');button.disabled=true;button.innerHTML='LE QUARTIER SE RÉVEILLE…';
  try{
    await audio.start();data=await dataPromise;
    if(!world){world=new GameWorld($<HTMLCanvasElement>('#world'),data);sim=new Simulation(data);sim.obstacleProvider=t=>{const obstacles=world!.traffic(t);if(sim?.mode==='story'&&sim.storyStage===1){const taxi=sim.taxi();obstacles.push({...taxi,radius:.8,halfLength:1.15,kind:'vehicle'});}return obstacles;};await Promise.all([world.stream(data.spawn[0],data.spawn[1]),world.loadBike()]);}
    sim!.reset(selected);finishedSaved=false;clearInput();playing=true;world.bike.position.copyFromFloats(sim!.vehicle.x,0,sim!.vehicle.z);world.bike.rotation.y=sim!.vehicle.yaw;applySettings();
    $('#home').classList.add('hidden');$('#pause-panel').classList.add('hidden');$('#results').classList.add('hidden');$('#hud').classList.remove('hidden');$('#world').classList.add('active');$('#mode-label').textContent=labels[selected];world.resize();lastFrame=performance.now();
    if(audio.voices)audio.speak('Gombe ! Gombe ! Encore deux places !');
  }catch(error){button.innerHTML='RÉESSAYER';const message=document.createElement('p');message.className='load-error';message.textContent=error instanceof Error?error.message:'Impossible de démarrer. Réessaie.';$('.dock-bottom').prepend(message);console.error(error);}
  finally{starting=false;button.disabled=false;if(playing)button.innerHTML=`ENTRER DANS KIN ${icon('arrow')}`;}
}
function results(){
  if(!sim||finishedSaved)return;finishedSaved=true;clearInput();audio.pause();save.runs++;
  if(sim.mode==='rush')save.record=Math.max(save.record,sim.score);if(sim.mode==='story')save.storyComplete=true;persist();
  $('#result-title').innerHTML=sim.mode==='story'?'Mado a laissé<br>une piste.':'Bien joué,<br>Wewa !';
  $('#result-kicker').textContent=sim.mode==='rush'?'30 SECONDES. UN PASSAGE DE PLUS.':sim.mode==='story'?'CHAPITRE 01 · LA PISTE JAUNE':'LA TOURNÉE EST BOUCLÉE.';
  $('#result-score').textContent=String(sim.score);$('#result-deliveries').textContent=String(sim.delivered);$('#result-collisions').textContent=String(sim.collisions);$('#result-best').textContent=String(save.record);
  $('#result-description').textContent=sim.mode==='story'?'Un bracelet au bord de la route. Mado a réussi à te laisser un indice. La suite mènera vers d’autres quartiers.':sim.mode==='rush'?'Les colis restés à bord ne comptent pas. Le prochain passage sera peut-être le meilleur.':'Des colis livrés, des rues apprises. Tu connais un peu mieux le quartier.';
  $('#results').classList.remove('hidden');
}
function drawMap(){
  if(!data||!sim)return;const canvas=$<HTMLCanvasElement>('#minimap'),ctx=canvas.getContext('2d')!,v=sim.vehicle,scale=.29;
  ctx.fillStyle='#192a2b';ctx.fillRect(0,0,240,240);
  const xy=(p:number[])=>[120+(p[0]-v.x)*scale,120+(p[1]-v.z)*scale];
  ctx.lineCap='round';ctx.lineWidth=2;ctx.strokeStyle='#51605a';ctx.beginPath();
  for(const segment of data.segments){const a=xy(data.nodes[segment.a]),b=xy(data.nodes[segment.b]);if(Math.abs(a[0]-120)>260&&Math.abs(b[0]-120)>260)continue;ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);}ctx.stroke();
  ctx.strokeStyle='#b6a66b';ctx.lineWidth=2;ctx.beginPath();data.route.forEach((p,i)=>{const [x,y]=xy(p);if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);});ctx.stroke();
  const dot=(p:number[],color:string,size:number)=>{const [x,y]=xy(p);ctx.fillStyle=color;ctx.beginPath();ctx.arc(x,y,size,0,Math.PI*2);ctx.fill();};
  if(sim.mode!=='free'&&!(sim.mode==='story'&&sim.storyStage>0)){
    data.parcels.filter(p=>!sim!.collected.has(p.id)).forEach(p=>dot(p.point,'#f6c645',3.4));data.depots.forEach(p=>dot(p.point,'#72e2dd',5));
  }
  if(sim.mode==='story'&&sim.storyStage===1){const t=sim.taxi();dot(Math.hypot(t.x-v.x,t.z-v.z)<100?[t.x,t.z]:sim.lastKnown,'#f78f8b',5);}
  ctx.save();ctx.translate(120,120);ctx.rotate(-v.yaw);ctx.fillStyle='#ff8050';ctx.strokeStyle='#192a2b';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(0,10);ctx.lineTo(7,-7);ctx.lineTo(0,-3);ctx.lineTo(-7,-7);ctx.closePath();ctx.fill();ctx.stroke();ctx.restore();
}
function updateHUD(){
  if(!sim||!world)return;const v=sim.vehicle;
  $('#speed').textContent=String(Math.round(Math.abs(v.speed)*3.6));$('#nitro-fill').style.width=`${v.nitro}%`;$('#cargo').textContent=`${sim.cargo.length} / 3 COLIS`;
  $('#score').textContent=String(sim.score).padStart(4,'0');$('#combo').textContent=`×${sim.combo.toFixed(2).replace(/0+$/,'').replace(/\.$/,'')}`;
  $('#time-caption').textContent=sim.mode==='rush'?'SECONDES':'TEMPS';
  const value=sim.mode==='rush'?sim.remaining:sim.elapsed;$('#timer').innerHTML=`${Math.floor(value)}<span>.${Math.floor((value%1)*10)}</span>`;
  $('#street-name').textContent=sim.nearestRoad([v.x,v.z]).name;
  $('#countdown').textContent=sim.phase==='countdown'?String(3-Math.floor(sim.countdownTicks/60)):'';
  $('#callout').classList.toggle('visible',sim.messageTimer>0);$('#callout p').textContent=sim.message;
  $('#objective-text').textContent=sim.mode==='free'?'La ville est à toi. Prends le prochain passage.':sim.mode==='story'&&sim.storyStage===1?(sim.taxi().stopped?'Rejoins le taxi et ralentis pour chercher l’indice.':'Suis le taxi jaune. S’il disparaît, rejoins sa dernière position.'):sim.cargo.length?(sim.mode==='delivery'?`${sim.delivered}/6 livrés · Ralentis à moins de 15 km/h dans le relais bleu.`:'Ralentis à moins de 15 km/h dans le relais bleu.'):'Passe sur les colis jaunes. Jusqu’à trois à la fois.';
  $('#nitro-vignette').classList.toggle('boosting',v.boosting&&!save.comfort);drawMap();
}
function frame(now:number){
  const delta=Math.min((now-lastFrame)/1000||0,.25);lastFrame=now;
  if(playing&&sim&&world){
    if(!sim.paused){sim.advance(delta,controls);if(controls.horn)audio.horn();}
    if(!sim.paused&&!finishedSaved)world.update(sim,delta);audio.update(sim);hudTime+=delta;
    if(hudTime>.08){updateHUD();hudTime=0;}if(sim.phase==='finished')results();
  }
  requestAnimationFrame(frame);
}
document.querySelectorAll<HTMLButtonElement>('[data-mode]').forEach(button=>button.addEventListener('click',()=>{selected=button.dataset.mode as Mode;document.querySelectorAll('[data-mode]').forEach(b=>{b.classList.toggle('selected',b===button);b.setAttribute('aria-pressed',String(b===button));});}));
$('#play').addEventListener('click',()=>void start());$('#pause').addEventListener('click',pause);$('#resume').addEventListener('click',resume);$('#menu').addEventListener('click',home);$('#result-menu').addEventListener('click',home);
for(const selector of ['#restart','#replay'])$(selector).addEventListener('click',()=>{if(sim)selected=sim.mode;void start();});
$('#camera').addEventListener('click',()=>{save.camera=!save.camera;persist();world?.setCamera(save.camera);});
$('#sound').addEventListener('click',()=>{save.sound=!save.sound;audio.enabled=save.sound;persist();$('#sound').classList.toggle('muted',!save.sound);});
for(const setting of ['comfort','fov','shake','music','voices'] as const)$<HTMLInputElement>('#'+setting).addEventListener('change',e=>{save[setting]=(e.target as HTMLInputElement).checked;persist();applySettings();});
$('#credits-toggle').addEventListener('click',()=>$('#credits').classList.toggle('hidden'));
$('#reset-save').addEventListener('click',()=>{if(window.confirm('Effacer le record et la progression enregistrés sur cet appareil ?')){save={...defaultSave};persist();applySettings();$('#home-record').textContent='RECORD RUSH · 0';}});
$('#export-diagnostic').addEventListener('click',()=>{if(!world)return;const url=URL.createObjectURL(new Blob([JSON.stringify(world.benchmark(),null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='viva-wewa-diagnostic.json';a.click();URL.revokeObjectURL(url);});
document.querySelectorAll<HTMLButtonElement>('[data-input]').forEach(button=>{
  button.addEventListener('pointerdown',e=>{e.preventDefault();if(!sim||sim.paused||sim.phase==='finished')return;button.setPointerCapture(e.pointerId);inputPointers.set(e.pointerId,button.dataset.input as keyof Controls);button.classList.add('pressed');rebuildInput();});
  const release=(e:PointerEvent)=>{inputPointers.delete(e.pointerId);if(![...inputPointers.values()].includes(button.dataset.input as keyof Controls))button.classList.remove('pressed');rebuildInput();};
  button.addEventListener('pointerup',release);button.addEventListener('pointercancel',release);button.addEventListener('lostpointercapture',release);
});
window.addEventListener('keydown',e=>{
  if(!playing||!sim)return;if((e.target as HTMLElement).matches('input,select,textarea'))return;const key=e.key.toLowerCase();
  if([' ','arrowup','arrowdown','arrowleft','arrowright','shift'].includes(key))e.preventDefault();
  if(!e.repeat){if(key==='escape'||key==='p'){sim.paused?resume():pause();return;}if(key==='c')$('#camera').click();if(key==='r'&&!sim.paused)sim.respawn();}
  if(!sim.paused){keys.add(key);rebuildInput();}
});
window.addEventListener('keyup',e=>{keys.delete(e.key.toLowerCase());rebuildInput();});
window.addEventListener('blur',()=>{clearInput();pause();});document.addEventListener('visibilitychange',()=>{if(document.hidden){clearInput();pause();}});
applySettings();requestAnimationFrame(frame);
// Read-only diagnostics are useful to collect real-device evidence. Mutating QA hooks are localhost-only.
const diagnostics={snapshot:()=>sim?{mode:sim.mode,phase:sim.phase,paused:sim.paused,elapsed:sim.elapsed,score:sim.score,cargo:sim.cargo,delivered:sim.delivered,collisions:sim.collisions,vehicle:{...sim.vehicle},storyStage:sim.storyStage,finishCount:sim.finishCount,loadedCells:world?.loadedCells.size,controls:{...controls}}:null};
(window as unknown as {__WEWA__:unknown}).__WEWA__=location.hostname==='127.0.0.1'||location.hostname==='localhost'?{...diagnostics,sim:()=>sim,world:()=>world}:diagnostics;
