/* HN BLACKBOX V40 - Foreground-aware living sci-fi GPU cinematic visual surface.
 * The heavy visual layer lives in a dedicated WebGL2 context. The Tk shell only
 * owns controls/layout; Python workers handle expensive telemetry/filesystem work.
 */
const params = new URLSearchParams(location.search);
const mode = params.get('mode') === 'stego' ? 'stego' : 'modern';
const accent = mode === 'stego' ? [0.224, 0.965, 0.627] : [0.125, 0.910, 1.0];
const state = { fps: 60, quality: 'AUTO', qualityScale: 1, active: true, frames: 0, lastFps: performance.now(), pointerX: 0, pointerY: 0, burst: 0, time: 0, seq: 2048, signal: 98.4, rx: 84.2, tx: 71.9, hexEpoch: 0, pulseEpoch: 0 };
const $ = (id) => document.getElementById(id);

function setText(id, text) { const e = $(id); if (e) e.textContent = text; }
function toast(message, kind='ok') {
  const root = $('toast-root'); if (!root) return;
  const el = document.createElement('div'); el.className = `toast ${kind}`; el.textContent = message;
  root.appendChild(el);
  requestAnimationFrame(() => el.classList.add('show'));
  setTimeout(() => { el.classList.remove('show'); setTimeout(() => el.remove(), 260); }, 1800);
}
function flash(el) { if (!el) return; el.classList.remove('pulse'); void el.offsetWidth; el.classList.add('pulse'); }
function bytesToHex(bytes) { return [...bytes].map(b => b.toString(16).padStart(2,'0')).join('').toUpperCase(); }

// --- Autonomous telemetry / hex-stream bus ---------------------------------
// These timers intentionally do not depend on hover, focus, pointer or clicks.
// RAF consumes the state every frame; the intervals periodically refresh data
// epochs so the scene also has discrete operational events.
const autonomousTelemetryBus = setInterval(() => {
  state.seq = (state.seq + 1 + Math.floor(Math.random()*7)) % 100000;
  state.signal = 96.5 + Math.random()*3.4;
  state.rx = 72 + Math.random()*38;
  state.tx = 61 + Math.random()*42;
  state.pulseEpoch++;
  setText('fps', String(Math.min(144, Math.max(1, state.fps))));
}, 250);
const autonomousHexStreamBus = setInterval(() => {
  state.hexEpoch++;
  document.documentElement.style.setProperty('--hex-phase', `${state.hexEpoch}`);
  const stream = $('hero-data-stream');
  if (stream) stream.textContent = `${bytesToHex(crypto.getRandomValues(new Uint8Array(4)))} // ${bytesToHex(crypto.getRandomValues(new Uint8Array(3)))} // HN-BLACKBOX // LOCAL BUS // AUTONOMOUS`;
}, 1200);
window.addEventListener('pagehide', () => { clearInterval(autonomousTelemetryBus); clearInterval(autonomousHexStreamBus); });

// --- Real WebGL2 compositor -------------------------------------------------
function initGPU() {
  const canvas = $('gpu-canvas');
  const gl = canvas.getContext('webgl2', { antialias: false, alpha: true, depth: false, stencil: false, powerPreference: 'high-performance' });
  if (!gl) { setText('mode', 'NATIVE // GPU UNAVAILABLE'); return null; }

  const vertex = `#version 300 es\nprecision highp float;\nout vec2 uv;\nvoid main(){ vec2 p=vec2((gl_VertexID<<1)&2, gl_VertexID&2); uv=p; gl_Position=vec4(p*2.0-1.0,0.0,1.0); }`;
  const fragment = `#version 300 es
precision highp float;
in vec2 uv; out vec4 outColor;
uniform float uTime; uniform vec2 uRes; uniform vec2 uPointer; uniform float uBurst; uniform float uQuality; uniform vec3 uAccent; uniform float uMode;
float hash21(vec2 p){ p=fract(p*vec2(123.34,456.21)); p+=dot(p,p+45.32); return fract(p.x*p.y); }
float line(float d,float w){ return smoothstep(w,0.0,abs(d)); }
void main(){
  vec2 p=(uv-.5)*vec2(uRes.x/uRes.y,1.0); float t=uTime;
  float r=length(p), a=atan(p.y,p.x);
  vec3 col=vec3(0.003,0.009,0.016);
  // deep radial field
  col += uAccent*(0.030/(r+0.12));
  // tactical grid
  vec2 driftField=vec2(0.045*sin(t*.12),0.032*cos(t*.095)); vec2 gp=fract((p+0.5+driftField)*vec2(9.0,7.0));
  float grid=(line(gp.x-0.5,0.008)+line(gp.y-0.5,0.008))*0.035;
  col += uAccent*grid;
  // rotating target rings
  float ring=0.0; for(float i=0.0;i<6.0;i++){ float rr=0.18+i*0.085+0.008*sin(t*.9+i); ring += line(r-rr,0.004)/(1.0+i*.35); }
  float autoSweep=(-t*.24)+0.18*sin(t*.17); float sweep=line(a-autoSweep,0.018); ring += sweep*0.13;
  col += uAccent*ring;
  // particles / data dust
  vec2 cell=floor((uv+vec2(0.1*sin(t*.11),0.07*cos(t*.09)))*vec2(42.0,26.0));
  float rnd=hash21(cell); float drift=fract(rnd+t*(0.03+0.06*rnd));
  float px=fract(cell.x*0.031+drift*.75); float py=fract(cell.y*0.047+drift*.35);
  float particle=smoothstep(0.055,0.0,length(fract((uv+vec2(0.02*t*rnd,0.01*t))-cell/vec2(42.0,26.0))-vec2(px,py)));
  col += uAccent*particle*(0.04+0.09*rnd);
  // mode-specific covert/crypto energy
  float core = exp(-14.0*abs(r-0.34))*(0.035+0.025*sin(t*2.2));
  if(uMode>0.5){ core += exp(-28.0*abs(a-sin(t*.18)*.8))*exp(-5.0*r)*0.04; }
  else { core += exp(-22.0*abs(sin(a*8.0+t*.6)))*(0.0025+0.005*abs(sin(t))); }
  col += uAccent*core;
  // matrix streams: continuous cyber data rain with deterministic cells
  vec2 streamCell=floor(uv*vec2(58.0,34.0));
  float streamRnd=hash21(streamCell+17.0);
  float streamHead=fract(t*(0.10+0.18*streamRnd)+streamRnd);
  float streamY=fract(uv.y+streamHead);
  float streamMask=step(0.86,hash21(vec2(streamCell.x,7.0)));
  float streamTrail=exp(-18.0*fract(abs(streamY-streamHead)+0.02));
  col += uAccent*streamMask*streamTrail*(0.018+0.055*streamRnd);
  // hexagonal tactical lattice
  vec2 hx=p*vec2(10.0,17.32); hx.x += floor(hx.y)*0.5;
  vec2 hf=abs(fract(hx)-0.5); float hexEdge=smoothstep(0.045,0.0,min(hf.x,0.5-hf.y));
  col += uAccent*hexEdge*0.018;
  // autonomous hex data streams
  vec2 hs=floor((uv+vec2(t*.018,t*.011))*vec2(18.0,9.0)); float hr=hash21(hs+91.0); float hpos=fract(t*(.045+.11*hr)+hr); float hline=step(.78,hash21(vec2(hs.x,hs.y*.0+13.0))); float htrail=exp(-20.0*fract(abs(uv.x-hpos)+.015)); col += uAccent*hline*htrail*(.012+.045*hr);
  // laser rails / energy filaments
  float railA=exp(-120.0*abs(p.y-(0.24+0.025*sin(t*1.3+p.x*4.0)))) * (0.45+0.55*sin(t*2.4+p.x*13.0));
  float railB=exp(-120.0*abs(p.y-(-0.28+0.018*cos(t*1.7-p.x*5.0)))) * (0.35+0.65*cos(t*2.0-p.x*11.0));
  col += uAccent*max(0.0,railA+railB)*0.028;
  // pointer lens
  vec2 autoLens=vec2(0.30*cos(t*.31),0.20*sin(t*.43)); vec2 q=p-(autoLens+vec2(uPointer.x*.05,uPointer.y*.035)); float lens=exp(-32.0*dot(q,q)); col += uAccent*lens*0.10;
  // burst pulse after interaction
  float b=max(uBurst,0.0); col += uAccent*exp(-60.0*abs(r-(.12+b*.28)))*0.12*max(0.0,1.0-b);
  float scan=0.5+0.5*sin((uv.y*2.0-t*.16)*220.0); col *= 0.96+0.04*scan;
  col = min(col, vec3(0.38)); outColor=vec4(col,0.95);
}`;
  function compile(type, src){ const s=gl.createShader(type); gl.shaderSource(s,src); gl.compileShader(s); if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)) throw Error(gl.getShaderInfoLog(s)||'shader compile failed'); return s; }
  const prog=gl.createProgram(); gl.attachShader(prog,compile(gl.VERTEX_SHADER,vertex)); gl.attachShader(prog,compile(gl.FRAGMENT_SHADER,fragment)); gl.linkProgram(prog); if(!gl.getProgramParameter(prog,gl.LINK_STATUS)) throw Error(gl.getProgramInfoLog(prog)||'program link failed');
  gl.useProgram(prog);
  const u={time:gl.getUniformLocation(prog,'uTime'),res:gl.getUniformLocation(prog,'uRes'),pointer:gl.getUniformLocation(prog,'uPointer'),burst:gl.getUniformLocation(prog,'uBurst'),quality:gl.getUniformLocation(prog,'uQuality'),accent:gl.getUniformLocation(prog,'uAccent'),mode:gl.getUniformLocation(prog,'uMode')};
  function resize(){ const d=Math.min(devicePixelRatio||1, 2.0*state.qualityScale); const w=Math.max(1,Math.floor(innerWidth*d)), h=Math.max(1,Math.floor(innerHeight*d)); if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;canvas.style.width='100%';canvas.style.height='100%'; gl.viewport(0,0,w,h);} }
  addEventListener('resize',resize,{passive:true}); resize();
  addEventListener('pointermove', e=>{state.pointerX=(e.clientX/innerWidth-.5)*2; state.pointerY=(e.clientY/innerHeight-.5)*-2;},{passive:true});
  addEventListener('pointerdown', ()=>{state.burst=0; state.bursting=true;});
  addEventListener('pointerup', ()=>{state.bursting=false;});
  let last=performance.now();
  function frame(now){ requestAnimationFrame(frame); const dt=Math.min(.05,(now-last)/1000); last=now; state.time+=dt; state.frames++; advanceCryptoAnimation(now); if(state.bursting) state.burst=Math.min(1,state.burst+dt*2.4); else state.burst=Math.max(0,state.burst-dt*0.9); gl.useProgram(prog); gl.uniform1f(u.time,state.time); gl.uniform2f(u.res,canvas.width,canvas.height); gl.uniform2f(u.pointer,state.pointerX,state.pointerY); gl.uniform1f(u.burst,state.burst); gl.uniform1f(u.quality,state.qualityScale); gl.uniform3f(u.accent,...accent); gl.uniform1f(u.mode,mode==='stego'?1:0); gl.drawArrays(gl.TRIANGLES,0,3);
    if(now-state.lastFps>900){ state.fps=Math.round(state.frames*1000/(now-state.lastFps)); state.frames=0; state.lastFps=now; setText('fps',String(Math.min(144,state.fps))); }
    document.documentElement.style.setProperty('--telemetry-signal', state.signal.toFixed(1));
    document.documentElement.style.setProperty('--telemetry-rx', state.rx.toFixed(1));
    document.documentElement.style.setProperty('--telemetry-tx', state.tx.toFixed(1));
  }
  requestAnimationFrame(frame); setText('mode','GPU // WEBGL2 ONLINE'); setText('pipeline','WEBGL2 GPU'); return {gl,canvas};
}

// --- Modern crypto deck ----------------------------------------------------
const CRYPTO={algorithm:'AES',operation:'encrypt',input:'',key:'',output:'',step:0,total:10,playing:false,nextStepAt:0,trace:[]};
function renderMatrix(step=0){ const grid=$('matrix-grid'); if(!grid)return; grid.innerHTML=''; for(let i=0;i<CRYPTO.total;i++){const row=document.createElement('div');row.className=`round ${i<step?'done':''} ${i===step?'active':''}`; row.innerHTML=`<b>${String(i+1).padStart(2,'0')}</b><span>${CRYPTO.algorithm==='DES'?'FEISTEL':'AES STATE'} / ROUND ${i+1}</span><code>${CRYPTO.trace[i]||'00 00 00 00 00 00 00 00'}</code>`;grid.appendChild(row);}setText('round-counter',`${Math.min(step,CRYPTO.total)} / ${CRYPTO.total}`);const fill=$('progress-fill');if(fill)fill.style.width=`${Math.round(step/CRYPTO.total*100)}%`;if(step)flash(grid.querySelector('.active'));}
function seedTrace(){let h=2166136261>>>0;const seed=new TextEncoder().encode((CRYPTO.input||'BLACKBOX')+'|'+(CRYPTO.key||'KEY'));for(const b of seed)h=Math.imul(h^b,16777619)>>>0;CRYPTO.trace=Array.from({length:CRYPTO.total},(_,i)=>{h=Math.imul(h^(i+1),16777619)>>>0;return `${h.toString(16).padStart(8,'0').toUpperCase()} ${((h*2654435761)>>>0).toString(16).padStart(8,'0').toUpperCase()}`;});}
function stopPlay(){CRYPTO.playing=false;CRYPTO.nextStepAt=0;setText('play-label','PLAY');}
function stepForward(){if(CRYPTO.step<CRYPTO.total){CRYPTO.step++;renderMatrix(CRYPTO.step);}else stopPlay();}
function togglePlay(){if(CRYPTO.playing){stopPlay();return;}if(CRYPTO.step>=CRYPTO.total)CRYPTO.step=0;CRYPTO.playing=true;CRYPTO.nextStepAt=performance.now();setText('play-label','PAUSE');}
function advanceCryptoAnimation(now){if(!CRYPTO.playing)return;const interval=CRYPTO.algorithm==='DES'?140:110;if(now>=CRYPTO.nextStepAt){stepForward();CRYPTO.nextStepAt=now+interval;}}
async function aesGcmEncrypt(text,keyText){const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(keyText));const key=await crypto.subtle.importKey('raw',digest,{name:'AES-GCM'},false,['encrypt']);const iv=crypto.getRandomValues(new Uint8Array(12));const data=new TextEncoder().encode(text);const ct=new Uint8Array(await crypto.subtle.encrypt({name:'AES-GCM',iv},key,data));const packed=new Uint8Array(iv.length+ct.length);packed.set(iv);packed.set(ct,iv.length);return btoa(String.fromCharCode(...packed));}
async function aesGcmDecrypt(encoded,keyText){const packed=Uint8Array.from(atob(encoded),c=>c.charCodeAt(0));if(packed.length<13)throw Error('Invalid AES-GCM payload');const iv=packed.slice(0,12),ct=packed.slice(12);const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(keyText));const key=await crypto.subtle.importKey('raw',digest,{name:'AES-GCM'},false,['decrypt']);const pt=await crypto.subtle.decrypt({name:'AES-GCM',iv},key,ct);return new TextDecoder().decode(pt);}
async function executeCrypto(){const input=$('crypto-input').value.trim(),key=$('crypto-key').value;if(!input||!key){toast('INPUT + KEY REQUIRED','warn');return;}CRYPTO.input=input;CRYPTO.key=key;CRYPTO.operation=$('crypto-op').value;CRYPTO.algorithm=$('crypto-algo').value;CRYPTO.total=CRYPTO.algorithm==='DES'?16:10;CRYPTO.step=0;seedTrace();renderMatrix(0);setText('operation-status','PROCESSING // LOCAL CORE');try{let out='';if(CRYPTO.algorithm==='AES')out=CRYPTO.operation==='encrypt'?await aesGcmEncrypt(input,key):await aesGcmDecrypt(input,key);else throw Error('DES remains educational only in the GPU surface; use native engine for production operations.');$('crypto-output').value=out;setText('operation-status',`${CRYPTO.operation.toUpperCase()} COMPLETE // ${CRYPTO.algorithm}`);toast(`${CRYPTO.algorithm} ${CRYPTO.operation} complete`);flash($('crypto-output'));}catch(e){setText('operation-status','ERROR // '+e.message);toast(e.message,'warn');}}
function switchCryptoAlgorithm(){CRYPTO.algorithm=$('crypto-algo').value;CRYPTO.total=CRYPTO.algorithm==='DES'?16:10;setText('algo-badge',CRYPTO.algorithm==='DES'?'LEGACY / EDUCATIONAL':'AES-256-GCM / AUTHENTICATED');CRYPTO.step=0;seedTrace();renderMatrix(0);}

// --- Steganography deck ----------------------------------------------------
const STEGO={operation:'hide',source:null,sourceUrl:'',outputUrl:''};
function setStegoOperation(op){STEGO.operation=op;document.querySelectorAll('[data-stego-op]').forEach(b=>b.classList.toggle('active',b.dataset.stegoOp===op));$('hide-panel').hidden=op!=='hide';$('extract-panel').hidden=op!=='extract';setText('stego-status',op==='hide'?'READY // EMBED PAYLOAD':'READY // FORENSIC EXTRACTION');}
function loadImage(file){return new Promise((resolve,reject)=>{if(!file||!file.type.startsWith('image/'))return reject(Error('Select a supported image file.'));const url=URL.createObjectURL(file);const img=new Image();img.onload=()=>resolve({img,url,file});img.onerror=()=>reject(Error('Unable to read image.'));img.src=url;});}
function drawPreview(img,canvas){const maxW=canvas.clientWidth||640,maxH=canvas.clientHeight||340,scale=Math.min(maxW/img.width,maxH/img.height,1);canvas.width=Math.max(1,Math.floor(img.width*scale));canvas.height=Math.max(1,Math.floor(img.height*scale));canvas.getContext('2d').drawImage(img,0,0,canvas.width,canvas.height);}
function bytesFromPayload(message){const raw=new TextEncoder().encode(message),magic=new Uint8Array([72,78,76,83,66,49]),len=new Uint8Array(4);new DataView(len.buffer).setUint32(0,raw.length);return new Uint8Array([...magic,...len,...new Uint8Array(4),...raw]);}
function encodeStego(){
  if(!STEGO.source){toast('LOAD AN IMAGE FIRST','warn');return;}
  const msg=$('secret-text').value;if(!msg){toast('SECRET TEXT REQUIRED','warn');return;}
  const source=STEGO.source.img,w=source.width,h=source.height;
  const off=document.createElement('canvas');off.width=w;off.height=h;
  const ctx=off.getContext('2d',{willReadFrequently:true});ctx.drawImage(source,0,0);
  const image=ctx.getImageData(0,0,w,h),raw=new TextEncoder().encode(msg);
  const magic=new Uint8Array([72,78,76,83,66,49]),len=new Uint8Array(4);new DataView(len.buffer).setUint32(0,raw.length);
  const payload=new Uint8Array(14+raw.length);payload.set(magic);payload.set(len,6);payload.set(raw,14);
  const cap=Math.floor(w*h*3/8)-14;if(payload.length>cap){toast(`PAYLOAD TOO LARGE // ${cap} BYTES MAX`,'warn');return;}
  const workerCode=`self.onmessage=e=>{const d=new Uint8ClampedArray(e.data.pixels),p=new Uint8Array(e.data.payload);let bit=0;for(let i=0;i<d.length&&bit<p.length*8;i++){if((i&3)===3)continue;d[i]=(d[i]&254)|((p[bit>>3]>>(7-(bit&7)))&1);bit++;}self.postMessage(d.buffer,[d.buffer]);}`;
  const url=URL.createObjectURL(new Blob([workerCode],{type:'application/javascript'}));const worker=new Worker(url);
  worker.onmessage=ev=>{try{ctx.putImageData(new ImageData(new Uint8ClampedArray(ev.data),w,h),0,0);off.toBlob(blob=>{STEGO.outputUrl=URL.createObjectURL(blob);$('stego-output').src=STEGO.outputUrl;$('stego-output').hidden=false;$('download-stego').hidden=false;$('download-stego').href=STEGO.outputUrl;$('download-stego').download='HN_BLACKBOX_STEGO.png';setText('capacity-readout',`${payload.length} / ${cap} BYTES`);setText('stego-status','PAYLOAD EMBEDDED // WORKER LSB PIPELINE');flash($('output-frame'));toast('STEGO IMAGE GENERATED');worker.terminate();URL.revokeObjectURL(url);},'image/png');}catch(err){toast(err.message,'warn');worker.terminate();URL.revokeObjectURL(url);}};
  worker.onerror=()=>{toast('STEGO WORKER ERROR','warn');worker.terminate();URL.revokeObjectURL(url);};
  worker.postMessage({pixels:image.data.buffer,payload:payload.buffer},[image.data.buffer,payload.buffer]);
}
function extractStego(){toast('Use the native forensic engine for full CRC validation. The GPU deck is visualization-first.','warn');}
function handleStegoFile(file){loadImage(file).then(src=>{STEGO.source=src;$('source-image').src=src.url;$('source-image').hidden=false;drawPreview(src.img,$('source-canvas'));const cap=Math.floor(src.img.width*src.img.height*3/8)-14;setText('capacity-readout',`${Math.max(0,cap)} BYTES CAPACITY`);setText('image-meta',`${src.img.width} × ${src.img.height} // ${file.type}`);$('source-frame').classList.add('loaded');toast('IMAGE LOADED // GPU SCANNER ARMED');}).catch(e=>toast(e.message,'warn'));}

function buildUI(){
  $('title').textContent=mode==='stego'?'HN BLACKBOX // COVERT IMAGE OPS':'HN BLACKBOX // MODERN SECURITY';
  $('section-kicker').textContent=mode==='stego'?'STEGANOGRAPHY // COVERT GPU SCANNER':'MODERN SECURITY // CRYPTOGRAPHY';
  $('hero-code').textContent=mode==='stego'?'LSB FORENSICS // GPU TRACE':'CRYPTO CORE // GPU TRACE';
  $('hero-description').textContent=mode==='stego'?'GPU-driven covert-image visualization: pixel energy, RGB LSB activity, scan sweeps and forensic focus.':'GPU-driven cryptographic visualization: radial core, data field, scan sweep and live round matrix.';
  $('modern-deck').hidden=mode!=='modern';$('stego-deck').hidden=mode!=='stego';
  if(mode==='modern'){seedTrace();renderMatrix(0);}else setStegoOperation('hide');
}
function bind(){
  $('crypto-algo')?.addEventListener('change',switchCryptoAlgorithm);$('crypto-exec')?.addEventListener('click',executeCrypto);$('crypto-play')?.addEventListener('click',togglePlay);$('crypto-step')?.addEventListener('click',stepForward);$('crypto-back')?.addEventListener('click',()=>{stopPlay();CRYPTO.step=Math.max(0,CRYPTO.step-1);renderMatrix(CRYPTO.step);});$('crypto-reset')?.addEventListener('click',()=>{stopPlay();CRYPTO.step=0;seedTrace();renderMatrix(0);setText('operation-status','READY // AWAITING EXECUTION');});$('copy-encrypted')?.addEventListener('click',()=>navigator.clipboard?.writeText($('crypto-output').value||''));
  document.querySelectorAll('[data-stego-op]').forEach(b=>b.addEventListener('click',()=>setStegoOperation(b.dataset.stegoOp)));$('image-input')?.addEventListener('change',e=>handleStegoFile(e.target.files?.[0]));$('hide-btn')?.addEventListener('click',encodeStego);$('extract-btn')?.addEventListener('click',extractStego);$('dropzone')?.addEventListener('click',()=>$('image-input').click());$('dropzone')?.addEventListener('dragover',e=>{e.preventDefault();$('dropzone').classList.add('drag');});$('dropzone')?.addEventListener('dragleave',()=>$('dropzone').classList.remove('drag'));$('dropzone')?.addEventListener('drop',e=>{e.preventDefault();$('dropzone').classList.remove('drag');handleStegoFile(e.dataTransfer.files?.[0]);});
}

try{buildUI();bind();initGPU();setText('operation-status',mode==='modern'?'READY // GPU CRYPTO CORE':'READY // GPU IMAGE FORENSICS');}catch(e){console.error(e);toast('GPU LAYER ERROR // NATIVE UI AVAILABLE','warn');}
