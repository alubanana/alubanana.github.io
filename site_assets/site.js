(() => {
  'use strict';
  const lang = document.documentElement.dataset.locale || 'zh';
  const key = 'ac-language';
  const read = () => { try { return localStorage.getItem(key); } catch { return null; } };
  if (location.pathname === '/' && !new URLSearchParams(location.search).has('lang')) {
    const saved = read();
    const firstSupported = (navigator.languages || [navigator.language]).map(x => /^zh(?:-|$)/i.test(x) ? 'zh' : /^en(?:-|$)/i.test(x) ? 'en' : null).find(Boolean) || 'zh';
    const preferred = ['zh','en'].includes(saved) ? saved : firstSupported;
    if (preferred === 'en') location.replace('/en/' + location.search + location.hash);
  }
  document.querySelectorAll('[data-set-lang]').forEach(link => link.addEventListener('click', () => {
    try { localStorage.setItem(key,link.dataset.setLang); } catch {}
    const target = new URL(link.href,location.href);
    if (location.hash && !target.hash) target.hash = location.hash;
    link.href = target.href;
  }));
  const search = document.getElementById('project-search');
  const filters = [...document.querySelectorAll('[data-filter]')];
  const cards = [...document.querySelectorAll('[data-project]')];
  let active = 'all';
  function filterProjects() {
    const query = (search?.value || '').normalize('NFKC').trim().toLocaleLowerCase();
    let count = 0;
    cards.forEach(card => {
      card.hidden = !((active === 'all' || card.dataset.category === active) && card.dataset.search.toLocaleLowerCase().includes(query));
      if (!card.hidden) count++;
    });
    const status = document.getElementById('project-count');
    if (status) status.textContent = lang === 'en' ? `${count} project${count === 1 ? '' : 's'}` : `${count} 个项目`;
    const empty = document.getElementById('project-empty');
    if (empty) empty.hidden = count !== 0;
  }
  search?.addEventListener('input',filterProjects);
  filters.forEach(button => button.addEventListener('click',()=>{
    active=button.dataset.filter;
    filters.forEach(x=>x.setAttribute('aria-pressed',String(x===button)));
    filterProjects();
  }));
  function openOriginal() {
    const original = document.getElementById('original-en');
    if (original?.tagName === 'DETAILS' && location.hash === '#original-en') original.open = true;
  }
  window.addEventListener('hashchange',openOriginal);
  openOriginal();
})();
