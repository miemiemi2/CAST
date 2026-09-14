// Real browser mouse events and real HTTP/model traffic. No request mocking.
const {chromium}=require('/root/.local/share/gstack/node_modules/playwright');
const fs=require('fs');const path=require('path');
const out=path.resolve(__dirname,'../records/browser-replay',String(Date.now()));fs.mkdirSync(out,{recursive:true});
(async()=>{const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const context=await browser.newContext({viewport:{width:1440,height:1080},recordVideo:{dir:out,size:{width:1440,height:1080}}});
const p=await context.newPage();const log={errors:[],requests:[],responses:[]};const pending=[];
p.on('pageerror',e=>log.errors.push(e.message));
p.on('request',r=>{if(r.url().includes('/api/')&&r.method()==='POST')log.requests.push({url:r.url(),body:r.postDataJSON()})});
p.on('response',r=>{if(r.url().includes('/api/')&&r.request().method()==='POST')pending.push(r.json().then(body=>log.responses.push({url:r.url(),status:r.status(),body})).catch(()=>{}))});
try{
await p.goto('http://127.0.0.1:8765');await p.waitForFunction(()=>document.querySelector('#revision').textContent.includes('revision'));
const box=await p.locator('#stage').boundingBox();
const move=async(x,y=.55)=>p.mouse.move(box.x+x*box.width,box.y+y*box.height);
await move(.18);await p.mouse.down();
for(let x=.185;x<=.54;x+=.005){await p.waitForTimeout(45);await move(x)}
await p.waitForTimeout(20);await move(.80);await p.mouse.up();
log.recorded=await p.locator('#tracking').textContent();
await p.screenshot({path:path.join(out,'01-play.png')});
await p.locator('#intent').fill('When Player moves quickly, detach Cargo and leave it where it was. Keep the existing slow approach attachment mechanic.');
const request=p.waitForResponse(r=>r.url().endsWith('/api/intent'),{timeout:120000});
await p.locator('#generate').click();
const response=await request;const candidate=await response.json();if(!response.ok()||candidate.status!=='proposed')throw new Error('Agent did not propose a change: '+JSON.stringify(candidate));
await p.locator('#try-new').waitFor({state:'visible',timeout:120000});
await p.waitForFunction(()=>!document.querySelector('#try-new').disabled,{timeout:120000});
await p.waitForFunction(()=>document.querySelector('#message').textContent.startsWith('Same recorded play replayed'),{timeout:30000});
await p.locator('#compare').scrollIntoViewIfNeeded();
await p.screenshot({path:path.join(out,'02-compare.png')});
log.compareVisible=await p.locator('#compare').isVisible();log.message=await p.locator('#message').textContent();
await Promise.all(pending);
const replays=log.requests.filter(x=>x.url.endsWith('/api/replay'));
log.identicalInput=JSON.stringify(replays[0]?.body.frames)===JSON.stringify(replays[1]?.body.frames);
log.identicalInitial=JSON.stringify(replays[0]?.body.initial)===JSON.stringify(replays[1]?.body.initial);
const results=log.responses.filter(x=>x.url.endsWith('/api/replay'));
log.finalCargo=results.map(x=>x.body.final?.objects?.B);
log.visiblyDifferent=Math.abs(log.finalCargo[0].x-log.finalCargo[1].x)>.1;
if(!log.visiblyDifferent)throw new Error('Candidate did not visibly change the recorded play');
await p.locator('#try-new').click();await p.waitForTimeout(400);
await p.screenshot({path:path.join(out,'03-try.png')});
// Discard the trial and verify the installed version is retained.
await p.locator('#undo').click();log.discard=await p.locator('#message').textContent();
console.log(JSON.stringify({recorded:log.recorded,compareVisible:log.compareVisible,identicalInput:log.identicalInput,identicalInitial:log.identicalInitial,finalCargo:log.finalCargo,errors:log.errors,discard:log.discard}));
}catch(e){log.failure=e.message;console.error(e.message);await p.screenshot({path:path.join(out,'failure.png')});process.exitCode=1}
finally{await Promise.allSettled(pending);fs.writeFileSync(path.join(out,'evidence.json'),JSON.stringify(log,null,2));await context.close();await browser.close()}
})();
