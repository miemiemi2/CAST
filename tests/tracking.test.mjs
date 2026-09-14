import test from 'node:test';
import assert from 'node:assert/strict';
import {detectMarkers,markersToSignal,applyRules} from '../static/tracking.mjs';
function cameraImage(omitBlue=false){const width=100,height=100,data=new Uint8ClampedArray(width*height*4);for(const [x,y,color] of [[20,20,[240,20,20]],[40,20,[20,240,20]],...(omitBlue?[]:[[75,70,[20,20,240]]])])for(let dx=-3;dx<=3;dx++)for(let dy=-3;dy<=3;dy++){const p=((y+dy)*width+x+dx)*4;data.set([...color,255],p);}return {width,height,data};}
test('pixels yield two object positions and planar rotation',()=>{const markers=detectMarkers(cameraImage()),s=markersToSignal(markers);assert.equal(s.visible,true);assert.equal(s.auxVisible,true);assert.ok(Math.abs(s.x-.3)<1e-12);assert.equal(s.rotation,0);assert.ok(s.distance>.4);});
test('missing main marker freezes complete previous stage',()=>{markersToSignal.lastValid=null;markersToSignal.lastFiltered=null;const s=markersToSignal([null,{x:.4,y:.2},null]);const previous={stage:{x:.3}};assert.equal(applyRules(s,[],previous),previous);});
test('short marker occlusion holds the last signal, then expires',()=>{
 const clock=globalThis.performance;let now=1000;globalThis.performance={now:()=>now};
 try{
  markersToSignal.lastValid=null;markersToSignal.lastFiltered=null;markersToSignal.lastX=markersToSignal.lastY=undefined;
  const visible=markersToSignal([{x:.2,y:.2},{x:.4,y:.2},null]);assert.equal(visible.visible,true);
  now=1200;const held=markersToSignal([null,{x:.4,y:.2},null]);assert.equal(held.visible,true);assert.equal(held.x,visible.x);
  now=1401;const lost=markersToSignal([null,{x:.4,y:.2},null]);assert.equal(lost.visible,false);
 } finally {globalThis.performance=clock;}
});
test('same measured action changes visible effect after rule installation',()=>{const s=markersToSignal(detectMarkers(cameraImage()));const before=applyRules(s,[]);const after=applyRules(s,[{signal:'distance',target:'moon',effect:'light',threshold:.3,state_key:'lit'}]);assert.equal(before.moon.light,false);assert.equal(after.moon.light,true);assert.equal(after.stage.x,before.stage.x);});
test('missing auxiliary does not trigger distance effect with invented zero',()=>{const s=markersToSignal(detectMarkers(cameraImage(true)));assert.equal(s.auxVisible,false);assert.equal(applyRules(s,[{signal:'distance',target:'moon',effect:'light',threshold:0,state_key:'lit'}]).moon.light,false);});
test('large background red patch is not a valid marker',()=>{const im=cameraImage();for(let p=0;p<im.width*im.height;p++)im.data.set([240,20,20,255],p*4);assert.equal(detectMarkers(im)[0],null);});
test('browser honors threshold mode and effect amount',()=>{const s=markersToSignal(detectMarkers(cameraImage()));const out=applyRules(s,[{signal:'x',target:'moon',effect:'position',amount:.5},{signal:'distance',target:'moon',effect:'light',when:'above',threshold:.3,state_key:'lit'}]);assert.ok(Math.abs(out.moon.x-.15)<1e-12);assert.equal(out.moon.light,true);assert.equal(out.moon.flags.lit,true);});
test('generic conditions compose with AND for a new relation',()=>{const s=markersToSignal(detectMarkers(cameraImage()));s.distance=.2;s.rotation=60;const rule={signal:'distance',target:'moon',effect:'mask',when:'below',threshold:.3,amount:.25,conditions:[{signal:'rotation',when:'above',threshold:30}]};const out=applyRules(s,[rule]);assert.equal(out.moon.mask,.25);const open={...s,rotation:10};assert.equal(applyRules(open,[rule]).moon.mask,1);});
test('browser enter condition fires only on a threshold crossing',()=>{const s=markersToSignal(detectMarkers(cameraImage()));const rule={signal:'rotation',target:'moon',effect:'mask',when:'enter',threshold:30,amount:.2};const low={...s,rotation:10};const high={...s,rotation:40};assert.equal(applyRules(high,[rule],applyRules(low,[])).moon.mask,.2);assert.equal(applyRules({...high,rotation:50},[rule],applyRules(high,[rule],applyRules(low,[]))).moon.mask,1);});
test('browser changed event fires only when the driving signal changes',()=>{const s=markersToSignal(detectMarkers(cameraImage()));const rule={signal:'rotation',target:'moon',effect:'mask',event:'changed',amount:.25};const first=applyRules(s,[rule]);assert.equal(first.moon.mask,.25);const same=applyRules({...s},[rule],first);assert.equal(same.moon.mask,1);});
test('browser duration gates a sustained relation',()=>{const s=markersToSignal(detectMarkers(cameraImage()));const rule={signal:'rotation',target:'moon',effect:'mask',amount:.2,duration_ms:100};const a=applyRules({...s,time_ms:1000},[rule]);assert.equal(a.moon.mask,1);const b=applyRules({...s,time_ms:1050},[rule],a);assert.equal(b.moon.mask,1);const c=applyRules({...s,time_ms:1101},[rule],b);assert.equal(c.moon.mask,.2);});
test('duration restarts after a relation becomes inactive',()=>{const s=markersToSignal(detectMarkers(cameraImage()));const rule={signal:'rotation',target:'moon',effect:'mask',amount:.2,duration_ms:100,when:'above',threshold:30};const a=applyRules({...s,rotation:40,time_ms:1000},[rule]);const off=applyRules({...s,rotation:10,time_ms:1100},[rule],a);const b=applyRules({...s,rotation:40,time_ms:1150},[rule],off);assert.equal(b.moon.mask,1);});
test('custom registered actors persist across runtime frames',()=>{const s=markersToSignal(detectMarkers(cameraImage()));const first=applyRules(s,[]);first.hero={x:.2,y:.3,rotation:0,scale:1,visible:true,flags:{}};const next=applyRules(s,[],first);assert.equal(next.hero.x,.2);});
test('direction inputs can drive a generic relation',()=>{const s=markersToSignal(detectMarkers(cameraImage()));const rule={signal:'dx',target:'moon',effect:'light',when:'below',threshold:-.01,state_key:'moving_left'};const out=applyRules({...s,dx:-.2},[rule]);assert.equal(out.moon.light,true);});
test('marker tracker derives a bounded speed input',()=>{const first=markersToSignal(detectMarkers(cameraImage()));const moved=cameraImage();for(const [x,y,color] of [[35,35,[240,20,20]],[55,35,[20,240,20]]])for(let dx=-3;dx<=3;dx++)for(let dy=-3;dy<=3;dy++)moved.data[((y+dy)*moved.width+x+dx)*4]=color[0];assert.ok(first.speed>=0&&first.speed<=1);assert.ok(markersToSignal(detectMarkers(moved)).speed>=0);});

test('browser attach persists relative offset while source moves', () => {
 const rules=[{kind:'binding',source:'prop',signal:'distance',target:'stage',target_object:'B',effect:'attach',when:'below',threshold:.5}];
 let state=applyRules({x:.2,y:.2,distance:.2,visible:true,auxVisible:true},rules,{objects:{stage:{x:.2,y:.2},B:{x:.3,y:.2}},last_signal:{}});
 state=applyRules({x:.6,y:.2,distance:.2,visible:true,auxVisible:true},rules,state);
 assert.ok(state.B.x>.5);
});
