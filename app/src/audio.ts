import type {Simulation} from './simulation';
export class StreetAudio {
  context:AudioContext|null=null; master:GainNode|null=null;engine:OscillatorNode|null=null;engineGain:GainNode|null=null;
  enabled=true;music=true;voices=false;lastHorn=-10;nextBeat=0;beat=0;lastCall=0;
  async start(){
    if(!this.context){
      this.context=new AudioContext();this.master=this.context.createGain();this.master.gain.value=.24;this.master.connect(this.context.destination);
      this.engine=this.context.createOscillator();this.engine.type='sawtooth';
      const filter=this.context.createBiquadFilter();filter.type='lowpass';filter.frequency.value=330;
      this.engineGain=this.context.createGain();this.engineGain.gain.value=0;
      this.engine.connect(filter);filter.connect(this.engineGain);this.engineGain.connect(this.master);this.engine.start();
      this.nextBeat=this.context.currentTime;
    }
    await this.context.resume();
  }
  note(frequency:number,start:number,duration:number,volume=.05,type:OscillatorType='sine',pan=0){
    const c=this.context;if(!c||!this.master)return;
    const oscillator=c.createOscillator(),gain=c.createGain(),panner=c.createStereoPanner();
    oscillator.type=type;oscillator.frequency.value=frequency;gain.gain.setValueAtTime(0,start);gain.gain.linearRampToValueAtTime(volume,start+.008);gain.gain.exponentialRampToValueAtTime(.0001,start+duration);
    panner.pan.value=pan;oscillator.connect(gain);gain.connect(panner);panner.connect(this.master);oscillator.start(start);oscillator.stop(start+duration+.01);
  }
  horn(pan=0){const c=this.context;if(!c||!this.enabled||c.currentTime-this.lastHorn<.3)return;this.lastHorn=c.currentTime;this.note(370,c.currentTime,.28,.18,'square',pan);this.note(466,c.currentTime,.23,.07,'sine',pan);}
  update(sim:Simulation){
    const c=this.context;if(!c||!this.master||!this.engine||!this.engineGain)return;
    const active=!sim.paused&&sim.phase==='running'&&this.enabled;
    this.master.gain.setTargetAtTime(active?.24:0,c.currentTime,.08);
    this.engine.frequency.setTargetAtTime(45+Math.abs(sim.vehicle.speed)*4+(sim.vehicle.boosting?35:0),c.currentTime,.07);
    this.engineGain.gain.setTargetAtTime(.055+Math.abs(sim.vehicle.speed)*.003,c.currentTime,.08);
    if(this.nextBeat<c.currentTime-.5)this.nextBeat=c.currentTime;
    while(this.nextBeat<c.currentTime+.15){
      if(this.music&&active){
        // Original scratch arrangement, not a recording or transcription of an existing song.
        const phrase=[261.63,329.63,392,329.63,293.66,349.23,440,349.23,261.63,329.63,392,523.25,246.94,293.66,392,293.66];
        this.note(phrase[this.beat%16],this.nextBeat,.2,.13,'triangle',.45);
        if(this.beat%4===0)this.note(this.beat%16<8?65.4:73.4,this.nextBeat,.3,.2,'sine',-.35);
        if(this.beat%2===1)this.note(1450,this.nextBeat,.035,.025,'triangle',-.7);
      }
      this.nextBeat+=.18;this.beat++;
    }
    if(active&&sim.elapsed-this.lastCall>16){this.lastCall=sim.elapsed;this.horn(Math.sin(sim.elapsed));const call=['Gombe ! Gombe ! Encore deux places !','Eh chauffeur, tu conduis ou tu danses ?','Doucement ! Laisse passer les mamans !'][Math.floor(sim.elapsed/16)%3];if(sim.messageTimer<1)sim.say(call);if(this.voices)this.speak(call);}
  }
  speak(text:string){if(!this.enabled||!this.voices||!('speechSynthesis'in window))return;const utterance=new SpeechSynthesisUtterance(text);utterance.lang='fr-FR';utterance.rate=1.06;utterance.volume=.65;window.speechSynthesis.speak(utterance);}
  pause(){if('speechSynthesis'in window)window.speechSynthesis.cancel();}
}
