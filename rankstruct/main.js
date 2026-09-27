  // Sticky nav border on scroll
  const nav = document.getElementById('nav');
  const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 8);
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  // Mobile menu
  const burger = document.getElementById('burger');
  const menu = document.getElementById('mobileMenu');
  burger.addEventListener('click', () => {
    const open = menu.classList.toggle('open');
    burger.setAttribute('aria-expanded', open);
  });
  menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => menu.classList.remove('open')));

  // Cursor-tracking spotlight inside every card
  document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('pointermove', e => {
      const r = card.getBoundingClientRect();
      card.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      card.style.setProperty('--my', (e.clientY - r.top) + 'px');
    });
  });

  // Background glows also drift gently toward the cursor (parallax)
  const glows = [...document.querySelectorAll('.glow')];
  let tx = 0, ty = 0, cx = 0, cy = 0;
  window.addEventListener('pointermove', e => {
    tx = (e.clientX / innerWidth - .5) * 60;
    ty = (e.clientY / innerHeight - .5) * 60;
  }, { passive: true });
  (function loop() {
    cx += (tx - cx) * .04; cy += (ty - cy) * .04;
    glows.forEach((g, i) => {
      const k = (i % 3 + 1) * .5;
      g.style.translate = `${cx * k}px ${cy * k}px`;
    });
    requestAnimationFrame(loop);
  })();

  // Scroll reveal with stagger inside grids
  const io = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      const el = en.target;
      const sibs = [...el.parentElement.children].filter(c => c.classList.contains('reveal'));
      el.style.transitionDelay = (Math.max(0, sibs.indexOf(el)) * 70) + 'ms';
      el.classList.add('in');
      el.addEventListener('transitionend', () => { el.style.transitionDelay = ''; }, { once: true });
      io.unobserve(el);
    });
  }, { threshold: .12 });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));

  // Count-up metrics
  const cio = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      const el = en.target, end = +el.dataset.count, pre = el.dataset.prefix || '', suf = el.dataset.suffix || '';
      const t0 = performance.now(), dur = 1400;
      const tick = t => {
        const p = Math.min(1, (t - t0) / dur), v = Math.round(end * (1 - Math.pow(1 - p, 3)));
        el.textContent = pre + v + suf;
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
      cio.unobserve(el);
    });
  }, { threshold: .6 });
  document.querySelectorAll('[data-count]').forEach(el => cio.observe(el));
