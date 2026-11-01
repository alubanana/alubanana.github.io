const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname,'../site_assets/site.js'),'utf8');
function run(languages,saved,pathname='/',search='') {
  let redirect=null;
  const context={navigator:{languages},localStorage:{getItem:()=>saved},location:{pathname,search,hash:'#journey',replace:x=>{redirect=x;}},URLSearchParams,document:{documentElement:{dataset:{locale:'zh'}},querySelectorAll:()=>[],getElementById:()=>null},window:{addEventListener:()=>{}}};
  vm.runInNewContext(source,context);return redirect;
}
assert.equal(run(['en-US','zh-CN'],null),'/en/#journey');
assert.equal(run(['zh-Hant','en-US'],null),null);
assert.equal(run(['fr-FR','en-GB','zh-CN'],null),'/en/#journey');
assert.equal(run(['en-US'],'zh'),null);
assert.equal(run(['zh-CN'],'en'),'/en/#journey');
assert.equal(run(['en-US'],'corrupt'),'/en/#journey');
assert.equal(run(['en-US'],null,'/notes/'),null);
assert.equal(run(['en-US'],null,'/','?lang=zh'),null);
assert.equal(run(['de-DE'],null),null);
console.log('9 language preference cases passed');
