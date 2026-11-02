(() => {
  'use strict';
  const script = document.currentScript;
  const endpoint = script?.dataset.endpoint;
  const lang = document.documentElement.dataset.locale === 'en' ? 'en' : 'zh';
  const key = 'ac-analytics';
  const visitorKey = 'ac-visitor';
  const sessionKey = 'ac-session';
  const day = 86400000;
  const now = () => Date.now();
  const read = k => { try { return localStorage.getItem(k); } catch { return null; } };
  const write = (k,v) => { try { localStorage.setItem(k,v); } catch {} };
  const remove = k => { try { localStorage.removeItem(k); } catch {} };
  const parse = k => { try { return JSON.parse(read(k)); } catch { return null; } };
  const uuid = () => crypto.randomUUID();
  const query = new URLSearchParams(location.search);
  const testMode = query.get('analytics') === 'test';
  if (query.get('analytics') === 'off') write(key, 'off');
  const policyDisabled = navigator.globalPrivacyControl === true || navigator.doNotTrack === '1';
  const enabled = () => !policyDisabled && read(key) !== 'off';
  function updateControl() {
    const button = document.getElementById('analytics-toggle');
    if (button) {
      button.textContent = policyDisabled ? (lang === 'en' ? 'Tracking disabled by browser' : '浏览器已禁用统计') : enabled() ? (lang === 'en' ? 'Turn analytics off' : '关闭统计') : (lang === 'en' ? 'Turn analytics on' : '开启统计');
      button.disabled = policyDisabled;
      button.setAttribute('aria-pressed', String(enabled()));
    }
  }
  document.getElementById('analytics-toggle')?.addEventListener('click', () => {
    if (enabled()) { write(key,'off'); remove(visitorKey); remove(sessionKey); memoryVisitor=null; memorySession=null; }
    else write(key,'on');
    updateControl();
    if (enabled()) track('pageview');
  });
  updateControl();
  const production = location.hostname === 'alubanana.github.io' && location.protocol === 'https:';
  const approvedEndpoint = endpoint === 'https://annan-site-analytics.regalpig32.chatgpt.site/api/collect';
  const path = document.body.dataset.contentId || location.pathname;
  let memoryVisitor = null, memorySession = null;
  function identity() {
    const time = now();
    let visitor = parse(visitorKey) || memoryVisitor;
    let fresh = false;
    if (!visitor || !visitor.id || !visitor.expires || visitor.expires <= time) {
      visitor = {id: uuid(), expires: time + 90 * day}; fresh = true;
      write(visitorKey,JSON.stringify(visitor)); memoryVisitor = visitor;
    }
    let session = parse(sessionKey) || memorySession;
    if (fresh || !session || !session.id || session.visitor !== visitor.id || time - session.last > 30 * 60000) session = {id:uuid(),visitor:visitor.id,last:time,returning:!fresh};
    session.last = time; memorySession = session; write(sessionKey,JSON.stringify(session));
    return {visitor:visitor.id,session:session.id,returning:session.returning};
  }
  function cleanTarget(link) {
    try { const u = new URL(link,location.href); if (!/^https?:$/.test(u.protocol)) return ''; return u.origin === location.origin ? u.pathname : u.hostname + u.pathname; } catch { return ''; }
  }
  function track(type, extra = {}) {
    if (!enabled() || !production || !approvedEndpoint) return;
    let referrer = '';
    try { referrer = document.referrer ? new URL(document.referrer).hostname : ''; } catch {}
    const ua = navigator.userAgent || '';
    const device = navigator.userAgentData?.mobile || /Mobi|iPhone/i.test(ua) ? 'mobile' : /iPad|Tablet|Android/i.test(ua) ? 'tablet' : 'desktop';
    const event = {id:uuid(),type,path,language:lang,referrer,device,...identity(),...extra,...(testMode?{test:true}:{})};
    // No URL parameters, page text, form values, precise location or full UA are sent.
    fetch(endpoint,{method:'POST',mode:'cors',credentials:'omit',keepalive:true,headers:{'Content-Type':'application/json'},body:JSON.stringify(event)}).catch(() => {});
  }
  track('pageview');
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!link || link.origin === location.origin && link.pathname === location.pathname && link.hash) return;
    const target = cleanTarget(link.href);
    if (!target) return;
    track(link.dataset.setLang ? 'language_switch' : link.dataset.event === 'demo_open' ? 'demo_open' : 'click', {target});
  });
  if (document.body.dataset.article === 'true') {
    const sent = new Set();
    let visibleSince = document.visibilityState === 'visible' ? now() : null;
    let visibleElapsed = 0;
    document.addEventListener('visibilitychange',()=>{
      if (visibleSince !== null) visibleElapsed += now()-visibleSince;
      visibleSince = document.visibilityState === 'visible' ? now() : null;
    });
    let scheduled = false;
    function reading() {
      scheduled = false;
      if (!enabled() || document.visibilityState !== 'visible' || visibleElapsed+(visibleSince===null?0:now()-visibleSince) < 10000) return;
      const range = document.documentElement.scrollHeight-innerHeight;
      const depth = range <= 0 ? 100 : Math.min(100,Math.round(scrollY/range*100));
      [25,50,75,100].forEach(mark => { if (depth >= mark-1 && !sent.has(mark)) {sent.add(mark);track('read',{depth:mark});} });
    }
    addEventListener('scroll',()=>{if(!scheduled){scheduled=true;requestAnimationFrame(reading);}}, {passive:true});
    const timer = setInterval(()=>{reading();if(sent.has(100))clearInterval(timer);},1000);
  }
})();
