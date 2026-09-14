// Pixel-only marker tracker. No camera frames leave the browser.
export function detectMarkers({data,width,height}) {
  const masks=[new Uint8Array(width*height),new Uint8Array(width*height),new Uint8Array(width*height)];
  for(let p=0;p<width*height;p++) {
    const r=data[p*4],g=data[p*4+1],b=data[p*4+2];
    if(r>100 && r>g*1.5 && r>b*1.4)masks[0][p]=1;
    if(g>80 && g>r*1.35 && g>b*1.25)masks[1][p]=1;
    if(b>100 && b>r*1.4 && b>g*1.2)masks[2][p]=1;
  }
  return masks.map(mask=>{
    let largest=null; const queue=new Int32Array(width*height);
    for(let p=0;p<mask.length;p++) if(mask[p]) {
      let head=0,tail=1,sx=0,sy=0;queue[0]=p;mask[p]=0;
      while(head<tail){const q=queue[head++],x=q%width,y=Math.floor(q/width);sx+=x;sy+=y;
        for(const n of [x>0?q-1:-1,x<width-1?q+1:-1,y>0?q-width:-1,y<height-1?q+width:-1])
          if(n>=0&&mask[n]){mask[n]=0;queue[tail++]=n;}}
      if(tail>=12 && tail<width*height*.35 && (!largest||tail>largest.area))largest={x:sx/tail/width,y:sy/tail/height,area:tail};
    }return largest;
  });
}
export function markersToSignal(markers) {
  const [a,b,aux]=markers;
  const now=performance.now();
  if(!a||!b||Math.hypot(a.x-b.x,a.y-b.y)<.025){
    const held=markersToSignal.lastValid;
    if(held && now-held.time_ms<350)return {...held,time_ms:now,speed:0,dx:0,dy:0,auxVisible:!!aux};
    return {x:.5,y:.5,rotation:0,distance:0,speed:0,dx:0,dy:0,time_ms:null,visible:false,auxVisible:!!aux};
  }
  const rawX=(a.x+b.x)/2,rawY=(a.y+b.y)/2;
  const prior=markersToSignal.lastFiltered;
  // Reject implausible one-frame colour blobs. A real hand-held prop cannot
  // cross a third of the frame between camera ticks; accepting that jump
  // makes the stage appear to move on its own when segmentation catches a
  // background patch.
  if(prior && Math.hypot(rawX-prior.x,rawY-prior.y)>.22){
    const held=markersToSignal.lastValid;
    if(held)return {...held,time_ms:now,speed:0,dx:0,dy:0,auxVisible:!!aux};
  }
  const alpha=.6;
  const x=prior?prior.x+(rawX-prior.x)*alpha:rawX, y=prior?prior.y+(rawY-prior.y)*alpha:rawY;
  const dx=Math.max(-1,Math.min(1,x-(markersToSignal.lastX??x))),dy=Math.max(-1,Math.min(1,y-(markersToSignal.lastY??y)));const positionSpeed=Math.min(1,Math.hypot(dx,dy)*20);markersToSignal.lastX=x;markersToSignal.lastY=y;markersToSignal.lastFiltered={x,y};
  const rawRotation=Math.atan2(b.y-a.y,b.x-a.x)*180/Math.PI;
  const priorRotation=markersToSignal.lastRotation;
  let rotation=rawRotation;
  if(priorRotation!=null){let delta=((rawRotation-priorRotation+540)%360)-180;rotation=priorRotation+delta*.25;}
  markersToSignal.lastRotation=rotation;
  const result={x,y,rotation,speed:positionSpeed,dx,dy,time_ms:now,
    distance:aux?Math.min(1,Math.hypot(x-aux.x,y-aux.y)/Math.SQRT2):0,visible:true,auxVisible:!!aux,aux};
  markersToSignal.lastValid=result; return result;
}
export function applyRules(signal,rules,previous=null) {
  if(signal.distance_object){
    const reference=(previous?.objects||previous||{})[signal.distance_object];
    const available=!!reference&&reference.visible!==false;
    signal={...signal,auxVisible:available,distance:available?Math.min(1,Math.hypot(signal.x-reference.x,signal.y-reference.y)):1};
  }
  const trackingLost=!signal.visible;
  if(trackingLost && !rules.some(r=>r.event==='occluded'))return previous;
  const activeSince={...(previous?._active_since||{})};
  const priorStage=previous?.stage||{};
  const stage={x:trackingLost?(priorStage.x??.5):signal.x,y:trackingLost?(priorStage.y??.5):signal.y,rotation:trackingLost?(priorStage.rotation??0):signal.rotation,scale:priorStage.scale??1,light:priorStage.light??false,flags:{...(priorStage.flags||{})}};
  const moon={x:signal.aux?.x??.8,y:signal.aux?.y??.25,rotation:0,scale:1,mask:1,light:false,flags:{}};
  // Keep registered/custom actors across frames even when the current rule
  // set does not mention them; scene registration is part of the performance.
  const actors={stage,moon};
  for(const [name,value] of Object.entries(previous?.objects||previous||{}))
    if(!['stage','moon','last_signal','_active_since','visible'].includes(name))
      actors[name]={...value,flags:{...(value.flags||{})}};

  for(const rule of rules){
    const targetName=rule.target_object||rule.target||'stage';
    const actor=actors[targetName]||(actors[targetName]={x:.5,y:.5,rotation:0,scale:1,mask:1,light:false,flags:{}});
    const predicates=[{signal:rule.signal,when:rule.when??'always',threshold:rule.threshold??.5},...(rule.conditions??[])];
    const checks=predicates.map(p=>{const v=signal[p.signal],prev=previous?.last_signal?.[p.signal];return Number.isFinite(v)&&(p.when==='enter'?v>=(p.threshold??.5)&&(prev==null||prev<(p.threshold??.5)):p.when==='exit'?v<(p.threshold??.5)&&(prev==null||prev>=(p.threshold??.5)):p.when==='above'?v>=(p.threshold??.5):p.when==='below'?v<(p.threshold??.5):true)});
    const key=`${rule.version??1}:${targetName}:${rule.signal}:${rule.effect}`;
    if(!(rule.conditions_mode==='any'?checks.some(Boolean):checks.every(Boolean))){delete activeSince[key];continue;}
    if(rule.persist===false && (rule.effect==='state'||rule.effect==='light')) delete actor.flags[rule.state_key??'active'];
    if(rule.signal==='distance'&&!signal.auxVisible)continue;
    const value=signal[rule.signal];
    if(rule.event==='occluded' && signal.visible) continue;
    if(rule.event==='visible' && !signal.visible) continue;
    if(rule.event==='changed' && Object.is(value, previous?.last_signal?.[rule.signal])) continue;
    if(!Number.isFinite(value))continue;
    const threshold=rule.threshold??.5, mode=rule.when??'always';
    const active=mode==='above'||mode==='enter'?value>=threshold:mode==='below'||mode==='exit'?value<threshold:true;
    if(!active)continue;
    if(rule.duration_ms){const started=activeSince[key]??(activeSince[key]=signal.time_ms??0);if((signal.time_ms??0)-started<rule.duration_ms)continue;}else delete activeSince[key];
    const amount=rule.amount??1;
    if(rule.effect==='rotation')actor.rotation=Math.max(-180,Math.min(180,value*amount));
    if(rule.effect==='position'&&['x','y'].includes(rule.signal))actor[rule.signal]=Math.max(0,Math.min(1,amount===1?value:value*amount));
    if(rule.effect==='scale')actor.scale=Math.max(.2,Math.min(3,1+value*amount));
    if(rule.effect==='mask')actor.mask=Math.max(0,Math.min(1,amount));
    if(['state','light'].includes(rule.effect)){actor.flags[rule.state_key??'active']=true;if(rule.effect==='light')actor.light=true;}
    if(rule.effect==='attach'){const k=rule.state_key??'attached';if(!actor.flags[k])actor._attachOffset=[(actor.x??.5)-(stage.x??.5),(actor.y??.5)-(stage.y??.5)];actor.flags[k]=true;actor._attachKey=k;}
    if(rule.effect==='detach'){const k=rule.state_key??'attached';delete actor.flags[k];delete actor._attachOffset;delete actor._attachKey;delete actor._attach_offset;delete actor._attach_key;}
  }
  for(const [name,actor] of Object.entries(actors)){const attachKey=actor._attachKey??actor._attach_key??'attached';if(name!=='stage'&&actor.flags?.[attachKey]){const o=actor._attachOffset||actor._attach_offset||[0,0];actor.x=Math.max(0,Math.min(1,stage.x+o[0]));actor.y=Math.max(0,Math.min(1,stage.y+o[1]));}}
  return {stage,moon,...Object.fromEntries(Object.entries(actors).filter(([name])=>name!=='stage'&&name!=='moon')),last_signal:signal,_active_since:activeSince,visible:!trackingLost};
}
