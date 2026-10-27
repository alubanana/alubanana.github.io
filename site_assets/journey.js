(() => {
  const section = document.querySelector('.journey');
  if (!section) return;
  const buttons = [...section.querySelectorAll('button[data-city]')];
  const entries = [...section.querySelectorAll('.journey-entry')];
  const status = section.querySelector('#journey-status');
  let selected = 'all';
  section.addEventListener('click', event => {
    const button = event.target.closest('button[data-city]');
    if (!button || !section.contains(button)) return;
    const city = button.dataset.city;
    selected = city === selected ? 'all' : city;
    buttons.forEach(item => item.setAttribute('aria-pressed', String(item.dataset.city === selected)));
    let count = 0;
    entries.forEach(item => {
      item.hidden = selected !== 'all' && item.dataset.city !== selected;
      if (!item.hidden) count += 1;
    });
    const name = selected === 'all' ? '全部地点' : button.querySelector('strong').textContent;
    status.textContent = `${name}，共${count}段经历。`;
  });
})();
