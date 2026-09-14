import {detectMarkers,markersToSignal,applyRules} from './tracking.mjs?v=7';
const $=id=>document.getElementById(id),video=$('camera'),canvas=$('stage'),ctx=canvas.getContext('2d');
const capture=document.createElement('canvas');capture.width=320;capture.height=240;
const pixels=capture.getContext('2d',{willReadFrequently:true});
let stream=null,rules=[],version=0,proposal=null,scene={stage:{x:.18,y:.55,rotation:0,scale:1,mask:1,flags:{},visible:true},B:{x:.48,y:.55,rotation:0,scale:1,mask:1,flags:{},visible:true},moon:{x:.8,y:.25,rotation:0,scale:1,mask:1,flags:{},visible:true}},previewScene=null,lastSignal=null,lastFrame=-1,lastSyncAt=0,lastNativeAt=0,nativeStable=0,simulation=false,simStart=0,lastSimX=null,lastSimY=null;
const prototypeInitial=structuredClone(scene);
let pointerDown=false,lastPointer=null,playRecording=[],recordingStart=0,playSnapshot=null,playRules=[],lastPlay=null;
try{lastPlay=JSON.parse(localStorage.getItem('cast:last-play')||'null');if(lastPlay?.initial&&Array.isArray(lastPlay.frames)){playSnapshot=structuredClone(lastPlay.initial);playRecording=structuredClone(lastPlay.frames);playRules=structuredClone(lastPlay.rules||[]);$('tracking').textContent=`Play restored · ${playRecording.length} input frames`;}}catch(_){lastPlay=null;}
window.addEventListener('error',e=>announce('Stage display error: '+e.message));
function pointerSignal(event){
 const bounds=canvas.getBoundingClientRect();
 const x=Math.max(0,Math.min(1,(event.clientX-bounds.left)/bounds.width));
 const y=Math.max(0,Math.min(1,(event.clientY-bounds.top)/bounds.height));
 const time=performance.now()-recordingStart;
 const dx=lastPointer?x-lastPointer.x:0,dy=lastPointer?y-lastPointer.y:0;
 const dt=lastPointer?Math.max(.001,(time-lastPointer.time)/1000):0;
 lastPointer={x,y,time};const cargo=scene?.B;
 return {x,y,rotation:0,distance:cargo?Math.min(1,Math.hypot(x-cargo.x,y-cargo.y)):1,
  distance_object:'B',speed:dt?Math.min(1,Math.hypot(dx,dy)/dt):0,dx,dy,time_ms:time,
  visible:true,auxVisible:!!cargo&&cargo.visible!==false};
}
function recordPointer(event){const signal=pointerSignal(event);playRecording.push({t:signal.time_ms,signal});lastSignal=signal;scene=applyRules(signal,rules,scene);}
canvas.addEventListener('pointerdown',e=>{
 if(e.button!==0)return;
 // Capture requires an actual browser pointer; never claim synthetic dispatch
 // is a recorded human play when capture fails.
 try{canvas.setPointerCapture(e.pointerId);}catch(error){announce('Pointer capture failed: '+error.message);return;}
 simulation=false;if(stream)stop();pointerDown=true;lastPointer=null;
 playRecording=[];recordingStart=performance.now();
 playSnapshot=structuredClone(scene);playRules=structuredClone(rules);
 recordPointer(e);$('tracking').textContent='Recording play…';
});
canvas.addEventListener('pointermove',e=>{if(pointerDown)recordPointer(e);});
function finishPlay(){if(!pointerDown)return;pointerDown=false;lastPointer=null;
 lastPlay={id:crypto.randomUUID(),initial:structuredClone(playSnapshot),frames:structuredClone(playRecording),rules:structuredClone(playRules),version};
 try{localStorage.setItem('cast:last-play',JSON.stringify(lastPlay));}catch(_){/* private browsing may disable storage */}
 api('recording',lastPlay).catch(()=>{});
 $('tracking').textContent=`Play recorded · ${playRecording.length} input frames`;
 announce('Play recorded. Describe a mechanic change to compare this same play.');}
canvas.addEventListener('pointerup',finishPlay);
canvas.addEventListener('pointercancel',finishPlay);
canvas.addEventListener('lostpointercapture',finishPlay);

function markerMapping(){return {main_a:Number($('marker-main-a').value),main_b:Number($('marker-main-b').value),aux:Number($('marker-aux').value)}}
async function listCameras(){try{const devices=await navigator.mediaDevices.enumerateDevices();const select=$('camera-device');for(const d of devices.filter(d=>d.kind==='videoinput')){if([...select.options].some(o=>o.value===d.deviceId))continue;const option=document.createElement('option');option.value=d.deviceId;option.textContent=d.label||`Camera ${select.length}`;select.append(option);}}catch(error){$('camera-error').textContent=`Camera list unavailable: ${error.message}`;}}
listCameras();
async function api(path,body){const response=await fetch('/api/'+path,{method:body===undefined?'GET':'POST',headers:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body)});const result=await response.json();if(!response.ok)throw new Error(typeof result.detail==='string'?result.detail:JSON.stringify(result.detail));return result;}
function announce(text){$('message').textContent=text;}
async function sync(){const state=await api('state');rules=state.rules;version=state.version;$('revision').textContent=`Stage revision ${version}`;$('events').textContent=JSON.stringify(state.events,null,2);if(!scene||!scene.stage){const saved=state.state?.runtime;const existing=saved?.objects&&saved.objects.stage?{...saved.objects}:{};scene={stage:{x:.18,y:.55,rotation:0,scale:1,mask:1,flags:{},visible:true},B:{x:.48,y:.55,rotation:0,scale:1,mask:1,flags:{},visible:true},moon:{x:.8,y:.25,rotation:0,scale:1,mask:1,flags:{},visible:true},...existing};for(const [id,obj] of Object.entries(state.scene||{})){scene[id]??={...obj,scale:1,mask:1,flags:{},visible:true};}}}
async function replayCompare(candidate,play){
 if(!play?.initial||play.frames.length<2)throw new Error('Drag Player first to record a play.');
 const old=await api('replay',{initial:play.initial,frames:play.frames,rules:play.rules});
 const newer=await api('replay',{initial:play.initial,frames:play.frames,rules:candidate});
 const box=$('compare');box.hidden=false;
 box.dataset.playId=play.id;box.dataset.inputFrames=play.frames.length;
 box.scrollIntoView({behavior:'smooth',block:'center'});
 const drawReplay=(id,frame,label,color)=>{const surface=$(id);drawWorld(surface.getContext('2d'),frame.state?.objects||{},surface.width,surface.height,label);};
let i=0,started=performance.now(),playing=true,raf=0;
 const render=()=>{drawReplay('old-replay',old.frames[i],'OLD','#253b72');drawReplay('new-replay',newer.frames[i],'NEW','#9b3155');};
 const tick=()=>{if(!playing)return;const elapsed=performance.now()-started;
 while(i<old.frames.length-1&&old.frames[i+1].t<=elapsed)i++;
 render();
 if(i<old.frames.length-1)raf=requestAnimationFrame(tick);
 else announce('Same recorded play replayed under OLD and NEW. Try the candidate or keep it.');};
 const startReplay=()=>{if(i>=old.frames.length-1)i=0;playing=true;started=performance.now()-(old.frames[i]?.t||0);cancelAnimationFrame(raf);tick();};
 $('replay-play').onclick=startReplay;
 $('replay-pause').onclick=()=>{playing=false;cancelAnimationFrame(raf);};
 $('replay-again').onclick=()=>{i=0;render();startReplay();};
 tick();return {old,newer};}

function drawWorld(context,world,width,height,label='PLAYTEST'){
 context.save();context.scale(width/960,height/540);
 context.fillStyle='#f4ead7';context.fillRect(0,0,960,540);
 const delivered=world.B&&world.B.x>=.83&&world.B.x<=.97&&world.B.y>=.44&&world.B.y<=.66;
 context.fillStyle=delivered?'#b8dcc0':'#e0e9d6';context.fillRect(796.8,237.6,134.4,118.8);
 context.strokeStyle='#347a58';context.lineWidth=3;context.setLineDash([8,6]);context.strokeRect(796.8,237.6,134.4,118.8);context.setLineDash([]);
 context.fillStyle='#347a58';context.font='bold 20px system-ui';context.fillText(delivered?'DELIVERED':'GOAL',802,220);
 context.fillStyle='#29232e';context.font='bold 24px system-ui';context.fillText(label,24,36);
 for(const [name,actor] of Object.entries(world)){
  if(!actor||!Number.isFinite(actor.x)||!Number.isFinite(actor.y)||actor.visible===false)continue;
  // The prototype has two gameplay actors; optional scene actors remain
  // available to rules, but the unused legacy moon is not a game objective.
  if(name==='moon'&&!rules.some(r=>(r.target_object||r.target)==='moon'))continue;
  context.save();context.translate(actor.x*960,actor.y*540);context.rotate((actor.rotation||0)*Math.PI/180);context.scale(actor.scale??1,actor.scale??1);
  context.fillStyle=name==='stage'?'#253b72':actor.light?'#f0be45':'#d27b38';context.beginPath();
  if(name==='stage'){context.moveTo(-30,-24);context.lineTo(34,0);context.lineTo(-30,24);context.closePath();}
  else if(name==='B')context.rect(-24,-24,48,48);else context.arc(0,0,28,0,Math.PI*2*(actor.mask??1));
  context.fill();context.restore();context.fillStyle='#29232e';context.font='bold 18px system-ui';context.textAlign='center';
  context.fillText(name==='stage'?'PLAYER':name==='B'?'CARGO':name,actor.x*960,actor.y*540+(name==='stage'?-42:48));
  context.textAlign='left';
 }
 context.restore();
}
function draw(){drawWorld(ctx,scene||{},960,540);}

function frame(){if(simulation&&!stream){const t=(performance.now()-simStart)/1000;const x=.5+.28*Math.sin(t*1.4),y=.5+.18*Math.cos(t*1.1),aux={x:.62,y:.3};const dx=Math.max(-1,Math.min(1,lastSimX==null?0:x-lastSimX)),dy=Math.max(-1,Math.min(1,lastSimY==null?0:y-lastSimY));lastSimX=x;lastSimY=y;lastSignal={x,y,rotation:60*Math.sin(t*1.7),distance:Math.hypot(x-aux.x,y-aux.y)/Math.SQRT2,speed:Math.min(1,Math.hypot(dx,dy)*20),dx,dy,time_ms:performance.now(),visible:true,auxVisible:true,aux};scene=applyRules(lastSignal,rules,scene);$('tracking').textContent='Simulated performance · same runtime as camera';}if(stream&&video.readyState>=2&&video.currentTime!==lastFrame){lastFrame=video.currentTime;pixels.drawImage(video,0,0,320,240);const signal=markersToSignal(detectMarkers(pixels.getImageData(0,0,320,240)));lastSignal=signal;scene=applyRules(signal,rules,scene);if(performance.now()-lastNativeAt>500){lastNativeAt=performance.now();capture.width=320;capture.height=240;capture.getContext('2d').drawImage(video,0,0,320,240);capture.toBlob(async blob=>{if(!blob)return;const bytes=new Uint8Array(await blob.arrayBuffer());let binary='';for(const byte of bytes)binary+=String.fromCharCode(byte);try{const native=await api('native-track',{jpeg:btoa(binary),mapping:markerMapping()});if(native.backend==='opencv-aruco'&&native.visible){nativeStable++;if(nativeStable>=2){lastSignal=native;scene=applyRules(native,rules,scene);$('tracking').textContent='ArUco identity tracking · local runtime synced';}}else nativeStable=0;}catch(_){nativeStable=0;/* colour fallback remains authoritative */}},'image/jpeg',.72);}if(performance.now()-lastSyncAt>250){lastSyncAt=performance.now();api('signal',lastSignal).catch(()=>{});} $('tracking').textContent=!lastSignal.visible?'Main markers lost · input held':`Input x=${lastSignal.x.toFixed(2)} y=${lastSignal.y.toFixed(2)} rot=${lastSignal.rotation.toFixed(0)}° dist=${lastSignal.distance.toFixed(2)} ${lastSignal.auxVisible?'· blue tracked':'· blue missing'}`;}draw();if(previewScene){ctx.save();ctx.globalAlpha=.6;ctx.strokeStyle='#b34d8c';ctx.lineWidth=4;ctx.setLineDash([8,6]);ctx.strokeRect(12,12,936,516);for(const [name,p] of Object.entries(previewScene)){if(['last_signal','_active_since','visible'].includes(name)||p?.visible===false||!Number.isFinite(p?.x))continue;ctx.save();ctx.translate(p.x*960,p.y*540);ctx.rotate((p.rotation||0)*Math.PI/180);ctx.scale(p.scale||1,p.scale||1);ctx.beginPath();if(name==='moon')ctx.arc(0,0,35,0,Math.PI*2*(p.mask??1));else ctx.rect(-50,-20,100,40);ctx.stroke();ctx.restore();}ctx.fillStyle='#b34d8c';ctx.font='16px system-ui';ctx.fillText('PROPOSED CONTROL PREVIEW',24,38);ctx.restore();}requestAnimationFrame(frame);}requestAnimationFrame(frame);
$('simulate').onclick=()=>{stop();simulation=true;simStart=performance.now();lastSimX=lastSimY=null;scene=scene||{};announce('Simulation running. The same control system is driven without a camera.');};$('start').onclick=async()=>{simulation=false;if(stream)return;$('start').disabled=true;try{const deviceId=$('camera-device').value;const videoConstraints=deviceId?{deviceId:{exact:deviceId},width:640,height:480}:{width:640,height:480};stream=await navigator.mediaDevices.getUserMedia({video:videoConstraints,audio:false});video.srcObject=stream;await video.play();$('stop').disabled=false;$('camera-error').textContent='';await listCameras();stream.getVideoTracks()[0].onended=stop;}catch(error){$('camera-error').textContent=`Camera could not start: ${error.message}. Check browser permission and try again.`;stop();}};
function stop(){stream?.getTracks().forEach(t=>t.stop());stream=null;video.srcObject=null;$('start').disabled=false;$('stop').disabled=true;$('tracking').textContent='Camera stopped — stage held.';}$('stop').onclick=stop;
$('intent-form').onsubmit=async event=>{
 event.preventDefault();
 if(!playSnapshot||playRecording.length<2){announce('Drag Player to record a play before describing a change.');return;}
 if(proposal){announce('Keep or discard this candidate before requesting another change.');return;}
 // Freeze the causally relevant play before the network request. Continued
 // playing cannot replace either comparison input or its initial world.
 const play=structuredClone(lastPlay||{id:crypto.randomUUID(),initial:structuredClone(playSnapshot),frames:structuredClone(playRecording),rules:structuredClone(playRules),version});
 const baseRules=structuredClone(rules),baseScene=structuredClone(scene);
 $('generate').disabled=true;$('install').disabled=true;$('try-new').disabled=true;
 announce('CAST is building a candidate mechanic. You can keep playing.');
 try{
  const result=await api('intent',{text:$('intent').value});
  if(result.status==='unchanged'||JSON.stringify(result.rules)===JSON.stringify(baseRules)){announce('The Agent returned no rule change. No candidate was installed.');$('events').textContent=JSON.stringify(result,null,2);return;}
  proposal={rules:result.rules,expected_version:result.base_version??version,play,baseRules,baseScene};
  const compared=await replayCompare(result.rules,play);
  proposal.compared=compared;
  $('events').textContent=JSON.stringify({play_id:play.id,frames:play.frames.length,base_version:proposal.expected_version,candidate:result},null,2);
  $('install').disabled=false;$('try-new').disabled=false;
 }catch(error){announce(error.message);}finally{$('generate').disabled=false;}
};
$('try-new').onclick=()=>{if(!proposal)return;rules=structuredClone(proposal.rules);
 scene=structuredClone(proposal.play.initial);previewScene=null;
 canvas.scrollIntoView({behavior:'smooth',block:'center'});
 announce('Trying candidate. Drag Player; Keep saves this mechanic.');};
$('install').onclick=async()=>{if(!proposal)return;$('install').disabled=true;
 try{const receipt=await api('install',{rules:proposal.rules,expected_version:proposal.expected_version,origin:'agent'});
 proposal=null;previewScene=null;$('try-new').disabled=true;await sync();
 announce(`Kept mechanic revision ${receipt.version}. Keep playing or ask for another change.`);
 }catch(error){announce(error.message);$('install').disabled=false;}};
$('undo').onclick=async()=>{try{if(proposal){rules=structuredClone(proposal.baseRules);scene=structuredClone(proposal.baseScene);
 proposal=null;previewScene=null;$('try-new').disabled=true;$('install').disabled=true;
 announce('Candidate discarded. Installed mechanic restored.');return;}
 const receipt=await api('rollback',{});await sync();$('install').disabled=true;
 announce(receipt.status==='empty'?'There is no earlier change to restore.':`Previous rules restored as revision ${receipt.version}.`);
 }catch(error){announce(error.message);}};
$('manual-install').onclick=async()=>{try{const parsed=JSON.parse($('manual-rules').value);const base=version;const preview=await api('preview',{rules:parsed,signal:{x:.5,y:.5,rotation:0,distance:0,visible:true}});const receipt=await api('install',{rules:parsed,expected_version:base,origin:'human'});await sync();announce(`Human-authored rules installed at revision ${receipt.version}.`);$('events').textContent=JSON.stringify({source:'human',preview},null,2);}catch(error){announce(`Manual rules rejected: ${error.message}`);}};
sync().catch(error=>announce(`Stage connection failed: ${error.message}. Reload to retry.`));
$('scene-save').onclick=async()=>{try{const objects=JSON.parse($('scene-objects').value);const receipt=await api('scene',{objects,expected_version:version});await sync();announce(`Scene saved at revision ${receipt.version}. Rules can now target registered objects.`);}catch(error){announce(`Scene rejected: ${error.message}`);}};

$('reset-play').onclick=()=>{scene=structuredClone(prototypeInitial);playRecording=[];playSnapshot=null;lastPlay=null;lastPointer=null;lastSignal=null;previewScene=null;try{localStorage.removeItem('cast:last-play');}catch(_){}$('tracking').textContent='Drag Player. Carry Cargo into Goal.';announce('Play reset. Your mechanic is unchanged.');};

// Make the browser-captured interaction part of the portable performance
// package. The server export remains authoritative for rules, scene and audit
// events; this adds the local input recording without exposing it in the main UI.
$('export').onclick=async event=>{
 if(!lastPlay)return;
 event.preventDefault();
 try{
  const response=await fetch('/api/export');
  if(!response.ok)throw new Error('export request failed');
  const packageData=await response.json();
  packageData.play=lastPlay;
  packageData.exported_at=new Date().toISOString();
  const blob=new Blob([JSON.stringify(packageData,null,2)],{type:'application/json'});
  const url=URL.createObjectURL(blob),link=document.createElement('a');
  link.href=url;link.download='cast-performance.json';link.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
  announce('Performance exported with the recorded play and ruleset identity.');
 }catch(error){announce(`Export failed: ${error.message}`);}
};
