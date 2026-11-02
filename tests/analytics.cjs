const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'../site_assets/analytics.js'),'utf8');
function run(options={}){
  let count=0,clock=1000000;
  const values=new Map(options.storage||[]),sent=[],events={},button={textContent:'',setAttribute(){},addEventListener(name,fn){events.toggle=fn;}};
  const listeners={};
  const context={URL,URLSearchParams,Date:{now:()=>clock},crypto:{randomUUID:()=>`00000000-0000-4000-8000-${String(++count).padStart(12,'0')}`},localStorage:{getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,v),removeItem:k=>values.delete(k)},location:{hostname:options.hostname||'alubanana.github.io',protocol:'https:',search:options.search||'',pathname:'/notes/example/',href:'https://alubanana.github.io/notes/example/?private=secret',origin:'https://alubanana.github.io'},navigator:{userAgent:'Chrome/140',...options.navigator},document:{currentScript:{dataset:{endpoint:options.endpoint||'https://annan-site-analytics.regalpig32.chatgpt.site/api/collect'}},documentElement:{dataset:{locale:'zh'},scrollHeight:2000},body:{dataset:{contentId:'/notes/example/',article:'true'}},referrer:'https://example.com/private?email=secret',visibilityState:'visible',getElementById:()=>button,addEventListener:(k,v)=>listeners[k]=v},fetch:(url,init)=>{sent.push({url,init,event:JSON.parse(init.body)});return Promise.resolve();},innerHeight:1000,scrollY:1000,addEventListener:(k,v)=>listeners[k]=v,requestAnimationFrame:fn=>fn(),setInterval:fn=>{events.timer=fn;return 1;},clearInterval:()=>{},};
  vm.runInNewContext(source,context);
  return {sent,values,button,toggle:()=>events.toggle(),advance:ms=>clock+=ms,reading:()=>events.timer?.(),visibility:(state)=>{context.document.visibilityState=state;listeners.visibilitychange();}};
}
assert.equal(run({hostname:'127.0.0.1'}).sent.length,0);
assert.equal(run({endpoint:'https://other.example/collect'}).sent.length,0);
assert.equal(run({navigator:{doNotTrack:'1'}}).sent.length,0);
assert.equal(run({navigator:{globalPrivacyControl:true}}).sent.length,0);
assert.equal(run({search:'?analytics=off'}).sent.length,0);
const normal=run();assert.equal(normal.sent.length,1);assert.equal(normal.sent[0].event.referrer,'example.com');assert.equal(normal.sent[0].event.path,'/notes/example/');assert.equal(normal.sent[0].init.credentials,'omit');assert(!JSON.stringify(normal.sent).includes('secret'));
const first=normal.sent[0].event;normal.toggle();assert(!normal.values.has('ac-visitor'));assert(!normal.values.has('ac-session'));normal.toggle();assert.notEqual(normal.sent[1].event.visitor,first.visitor);assert.notEqual(normal.sent[1].event.session,first.session);
const expired=run({storage:[['ac-visitor',JSON.stringify({id:'old',expires:1})],['ac-session',JSON.stringify({id:'old-session',visitor:'old',last:999999,returning:true})]]});assert.notEqual(expired.sent[0].event.visitor,'old');assert.notEqual(expired.sent[0].event.session,'old-session');assert.equal(expired.sent[0].event.returning,false);
const reading=run();reading.reading();assert.equal(reading.sent.length,1);reading.advance(11000);reading.reading();assert.equal(reading.sent.filter(x=>x.event.type==='read').length,4);reading.reading();assert.equal(reading.sent.length,5);
const hidden=run();hidden.visibility('hidden');hidden.advance(60000);hidden.visibility('visible');hidden.reading();assert.equal(hidden.sent.length,1);hidden.advance(11000);hidden.reading();assert.equal(hidden.sent.length,5);
console.log('10 analytics privacy and behavior scenarios passed');
