/* Small page behaviours that are not 3D: things below the hero fade up as they scroll into view. */
const io = new IntersectionObserver(entries => {
  entries.forEach(en => {
    if (!en.isIntersecting) return;
    en.target.classList.add('in');
    io.unobserve(en.target);
  });
}, { threshold: 0.15 });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));

/* if the 3D candle has not started after 4 seconds (for example the page was opened by double-clicking the file,
   which browsers block for modules), show the flat photo and the plain steps instead of a blank screen.
   If the 3D starts later, candle.js switches the fallback off again. */
setTimeout(() => {
  const st = document.getElementById('stage');
  if (st && !st.classList.contains('ready') && !st.classList.contains('no3d')) {
    st.classList.add('no3d'); document.documentElement.classList.add('no3d');
  }
}, 4000);
/* PRODUCTS: shelves you walk along, one shelf for each collection (products.json "collections"). On every shelf the candle nearest
   the middle is "lit": bright and lifted, with its name and order button. Without JavaScript (or without the data) the one static
   shelf of the page is used, and every item simply shows its own text and button. */
const root = document.querySelector('.candle-light').style;           // the shelf's own light is set on the light layer only (not on the root: that would restyle the whole page)
const arDigits = n => String(n).replace(/\d/g, d => '٠١٢٣٤٥٦٧٨٩'[d]);
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
/* The stand-in photos of the shelves (about 1 MB) are only needed when 3D cannot run, so they are not downloaded until then. */
function loadFallbackPhotos() { document.querySelectorAll('img[data-src]').forEach(i => { i.src = i.dataset.src; i.removeAttribute('data-src'); }); }
new MutationObserver(() => { if (document.documentElement.classList.contains('no3d')) loadFallbackPhotos(); }).observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
const visibleShelves = new Set();                                    // the shelves currently on screen

/* The "selected" candle is the lit candle of the shelf nearest the middle of the screen. It carries the flame (candle.js reads the
   is-focus class) and fills the one shared bar under the shelves, so no shelf needs its own name, buttons or arrows. */
let focusItem = null, pickBar = null, pickTimer = null;
let lastPick = null;
function fillPick() {
  if (!pickBar || !focusItem) return;
  if (lastPick !== null && lastPick !== focusItem) {                 // the selected candle changed: the name and facts arrive with a short fade and rise
    const info = pickBar.querySelector('.pick-info');
    info.classList.remove('swap'); void info.offsetWidth; info.classList.add('swap');
  }
  lastPick = focusItem;
  const data = window.shelfData, k = Number(focusItem.dataset.k);
  const p = data ? data.items[k % data.items.length] : null;
  pickBar.querySelector('.pick-name').textContent = focusItem.dataset.name;
  pickBar.querySelector('.pick-facts').textContent = p ? `${p.size} · ${p.burn} · ${p.family}` : '';
  pickBar.querySelector('a.btn').href = focusItem.dataset.href;
  clearTimeout(pickTimer);                                           // announce the selected candle once the swipe settles
  pickTimer = setTimeout(() => { pickBar.querySelector('.sr-only').textContent = focusItem.dataset.name + (p ? '، ' + p.family : ''); }, 450);
}
function refocus() {
  let best = null, bd = Infinity;
  document.querySelectorAll('.shelf').forEach(s => {
    const r = s.getBoundingClientRect();
    if (r.bottom < 0 || r.top > innerHeight) return;
    const it = s.querySelector('.shelf-item.is-active'), d = Math.abs((r.top + r.bottom) / 2 - innerHeight / 2);
    if (it && d < bd) { bd = d; best = it; }
  });
  if (!best || best === focusItem) return;                           // nothing on screen: keep the last one
  if (focusItem) focusItem.classList.remove('is-focus');
  focusItem = best; best.classList.add('is-focus');
  fillPick();
}

/* One shelf per collection, built from the data: plain rows of candles. Candle number n shows the photo of product n % (number of
   products), so a test shop with 20 candles needs only the 8 sample products. The static shelf of the page is the template and is replaced. */
function buildShelves(data) {
  const sec = document.getElementById('products');
  const oldShelf = sec && sec.querySelector('.shelf');
  if (!oldShelf) return;
  const oldCtrl = sec.querySelector('.shelf-ctrl'), oldLive = sec.querySelector('[aria-live]');
  const templates = [...oldShelf.querySelectorAll('.shelf-item')];
  const frag = document.createDocumentFragment();
  let n = 0;
  data.collections.forEach(col => {
    const block = document.createElement('div'); block.className = 'collection';
    block.innerHTML = `<div class="wrap collection-head"><h3>${esc(col.title)} <span class="tag">نص تجريبي</span></h3></div>
      <div class="shelf" tabindex="0" aria-label="رفّ ${esc(col.title)}. مرّر لتختار شمعة"><div class="shelf-row"></div></div>`;
    const row = block.querySelector('.shelf-row');
    for (let i = 0; i < col.count; i++, n++) {
      const name = `الشمعة ${arDigits(n + 1)}`, it = document.createElement('div');
      it.className = 'shelf-item'; it.dataset.k = n; it.dataset.name = name;
      it.dataset.href = 'https://wa.me/0000000000?text=' + encodeURIComponent('مرحبًا، أريد أن أطلب: ' + name);
      it.innerHTML = `<h3 class="sr-only">${esc(name)}</h3>`;       // the visible name is a small tag under the candle (setupShelf)
      const pic = templates[n % templates.length].querySelector('.img').cloneNode(true), ph = pic.querySelector('img');
      it.append(pic);
      row.append(it);
    }
    frag.append(block);
  });
  oldShelf.remove(); if (oldCtrl) oldCtrl.remove(); if (oldLive) oldLive.remove();
  sec.append(frag);
  /* the one shared bar: sticks to the bottom of the screen while the shelves are in view */
  pickBar = document.createElement('div'); pickBar.className = 'pick';
  pickBar.innerHTML = `<div class="pick-info"><h3 class="pick-name"></h3><p class="pick-facts"></p></div>
    <div class="pick-actions"><a class="btn btn-small" href="#" target="_blank" rel="noopener">اطلب عبر واتساب</a><button type="button" class="detail-open" data-pick-detail>التفاصيل</button></div>
    <p class="sr-only" aria-live="polite"></p>`;
  sec.append(pickBar);
}

/* the behaviour of one shelf: which candle is lit, keys and swipes. Only the one static shelf (no data) has its own arrows and count. */
function setupShelf(shelf) {
  const items = [...shelf.querySelectorAll('.shelf-item')];
  items.forEach(el => {                                              // every candle keeps a readable name, also the dimmed ones
    const t = document.createElement('span'); t.className = 'shelf-tag'; t.setAttribute('aria-hidden', 'true'); t.textContent = el.querySelector('h3').textContent;   // the hidden heading already names it for a screen reader
    el.querySelector('.img').append(t);
  });
  const block = shelf.closest('.collection') || shelf.parentElement;
  const ctrl = block.querySelector('.shelf-ctrl'), count = block.querySelector('.shelf-count'), live = block.querySelector('[aria-live]');
  let [prev, next] = ctrl ? ctrl.querySelectorAll('button') : [];
  if (!ctrl && block.classList.contains('collection')) {            // each shelf of the data-built page gets its own arrows, so a mouse can walk along it too
    const mk = (cls, label, d) => { const b = document.createElement('button'); b.type = 'button'; b.className = 'shelf-arrow ' + cls; b.setAttribute('aria-label', label); b.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${d}"/></svg>`; block.append(b); return b; };
    prev = mk('prev', 'الشمعة السابقة', 'M9 5l7 7-7 7'); next = mk('next', 'الشمعة التالية', 'M15 5l-7 7 7 7');
  }
  let active = -1, ticking = false, onScreen = false, liveTimer = null;
  let forced = -1;                                                  // a candle chosen with an arrow, a key or a press stays lit until the visitor drags or scrolls the shelf
  const atStart = () => Math.abs(shelf.scrollLeft) < 2;
  const atEnd = () => Math.abs(shelf.scrollLeft) > shelf.scrollWidth - shelf.clientWidth - 2;
  const center = el => { const r = el.getBoundingClientRect(); return r.left + r.width / 2; };
  const update = () => {
    ticking = false;
    const mid = shelf.getBoundingClientRect().left + shelf.clientWidth / 2;
    let best = 0, bd = Infinity;
    items.forEach((el, k) => { const d = Math.abs(center(el) - mid); if (d < bd) { bd = d; best = k; } });
    if (forced >= 0) best = forced;
    else if (atStart()) best = 0;                                   // the rows start at the edge of the screen, so the ends are lit when the shelf is scrolled all the way
    else if (atEnd()) best = items.length - 1;
    if (prev) prev.setAttribute('aria-disabled', String(best === 0));
    if (next) next.setAttribute('aria-disabled', String(best === items.length - 1));
    if (best !== active) {
      active = best; items.forEach((el, k) => el.classList.toggle('is-active', k === best));
      if (count) count.textContent = `${arDigits(best + 1)} / ${arDigits(items.length)}`;
      if (live) {
        clearTimeout(liveTimer);                                    // announce the lit candle once the swipe settles
        liveTimer = setTimeout(() => { live.textContent = `${items[best].querySelector('h3').textContent}، ${count.textContent}`; }, 450);
      }
    }
    if (onScreen) {                                                 // where the lit candle is, for the photo shelf's own light
      const ir = items[best].querySelector('.img').getBoundingClientRect();
      root.setProperty('--sx', (ir.left + ir.width / 2).toFixed(0) + 'px');
      root.setProperty('--sy', (ir.top + ir.height / 2).toFixed(0) + 'px');
    }
    root.setProperty('--si', [...visibleShelves].some(s => !s.classList.contains('is3d')) ? '1' : '0');   // with 3D the flame (candle.js) lights the room instead
    refocus();
  };
  const queue = () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } };
  const go = k => {
    k = Math.max(0, Math.min(items.length - 1, k)); forced = k; queue();
    items[k].scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
  };
  ['wheel', 'pointerdown', 'touchstart'].forEach(ev => shelf.addEventListener(ev, () => { forced = -1; }, { passive: true }));   // the visitor takes over: the lit candle follows the scroll again
  shelf.classList.add('js');
  shelf.addEventListener('scroll', queue, { passive: true });
  addEventListener('scroll', queue, { passive: true });
  addEventListener('resize', queue);
  new IntersectionObserver(([e]) => { onScreen = e.isIntersecting; if (onScreen) visibleShelves.add(shelf); else visibleShelves.delete(shelf); if (pickBar) pickBar.classList.toggle('show', visibleShelves.size > 0); queue(); }, { threshold: 0.35 }).observe(shelf);
  items.forEach((el, k) => el.addEventListener('click', e => { if (k !== active && !e.target.closest('a')) go(k); }));
  if (prev) prev.addEventListener('click', () => go(active - 1));
  if (next) next.addEventListener('click', () => go(active + 1));
  shelf.addEventListener('keydown', e => {                          // arrow keys follow the visual direction, which is reversed in right-to-left
    const rtl = getComputedStyle(shelf).direction === 'rtl';
    if (e.key === 'ArrowLeft') go(active + (rtl ? 1 : -1));
    else if (e.key === 'ArrowRight') go(active + (rtl ? -1 : 1));
    else return;
    e.preventDefault();
  });
  if (ctrl) ctrl.hidden = false;
  update();
}

/* the data first, then the shelves; candle.js waits for this too (window.shelvesReady) so it finds the final shelves */
window.shelvesReady = (async () => {
  let data = null;
  try { data = await (await fetch('products.json')).json(); } catch (e) { /* no data: the static shelf stays */ }
  window.shelfData = data;
  if (data && Array.isArray(data.collections) && data.collections.length) buildShelves(data);
  document.querySelectorAll('.shelf').forEach(setupShelf);
  addEventListener('scroll', refocus, { passive: true }); addEventListener('resize', refocus); refocus();
  return data;
})();

/* PRODUCT DETAIL: pressing the lit candle (or its "details" button) opens a panel with what a buyer needs. The facts come from
   products.json and are TEST text until the client supplies hers. Esc, the close button or a press outside closes it. */
(async () => {
  const data = await window.shelvesReady;
  if (!data) return;                                                 // no data: the shelves work without details
  const panel = document.getElementById('detail'), body = document.getElementById('detailBody'), scrim = document.getElementById('detailScrim');
  const items = [...document.querySelectorAll('.shelf-item')];       // every candle of every shelf, in page order
  items.forEach((el, k) => {                                         // the card line: size, burn time and scent family, from the same data as the sheet
    const p = data.items[k % data.items.length], f = el.querySelector('.facts-line');
    if (f) f.textContent = `${p.size} · ${p.burn} · ${p.family}`;
  });
  let opener = null, current = -1;
  const setInert = on => [...document.body.children].forEach(el => { if (el !== panel && el !== scrim && el.tagName !== 'SCRIPT') el.inert = on; });   // the page behind the open dialog cannot be reached by Tab
  const icons = {
    size: '<svg viewBox="0 0 24 24"><path d="M5 19h14M7 19l1.6-9h6.8L17 19M10 10a2 2 0 1 1 4 0"/></svg>',
    burn: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/></svg>',
    wax: '<svg viewBox="0 0 24 24"><path d="M12 3c3 4 6 7 6 10a6 6 0 0 1-12 0c0-3 3-6 6-10z"/></svg>',
    wick: '<svg viewBox="0 0 24 24"><path d="M12 3c1 3.5 4.5 5.5 4.5 9.5a4.5 4.5 0 0 1-9 0c0-2 1-3.2 2.2-4.2.1 2 1 2.6 2 2.6-.4-3.2-.6-5 .3-7.9z"/></svg>'
  };
  const render = k => {
    const p = data.items[k % data.items.length], c = data.common;
    const shot = p.photo ? `<figure class="shot"><img src="${esc(p.photo.src)}" alt="" style="object-position:${esc(p.photo.pos)}" decoding="async">
        <figcaption><span class="tag">صورة تجريبية</span><span>${esc(p.photo.credit)} · Unsplash</span></figcaption></figure>` : '';
    body.innerHTML = shot + `<div class="detail-in">
      <div><div class="kick"><span class="tag">نص تجريبي</span></div><h3 id="detailName">${esc(items[k].querySelector('h3').textContent)}</h3><p class="lead">${esc(p.scent)}</p></div>
      <dl class="facts">
        <div>${icons.size}<dt>الحجم</dt><dd>${esc(p.size)}</dd></div><div>${icons.burn}<dt>مدة الاحتراق</dt><dd>${esc(p.burn)}</dd></div>
        <div>${icons.wax}<dt>الشمع</dt><dd>${esc(p.wax)}</dd></div><div>${icons.wick}<dt>الفتيل</dt><dd>${esc(p.wick)}</dd></div>
      </dl>
      <section><h4>نوتات العطر</h4><div class="notes">
        <div class="note" style="--s:3"><i></i><span>القمة</span><b>${esc(p.notes.top)}</b></div>
        <div class="note" style="--s:2"><i></i><span>القلب</span><b>${esc(p.notes.heart)}</b></div>
        <div class="note" style="--s:1"><i></i><span>القاعدة</span><b>${esc(p.notes.base)}</b></div>
      </div></section>
      <div class="folds">
        <details class="fold"><summary>المكونات</summary><p>${esc(p.ingredients)}</p></details>
        <details class="fold"><summary>أول إشعال</summary><p>${esc(c.firstBurn)}</p></details>
        <details class="fold"><summary>العناية والأمان</summary><ul class="care">${c.care.map(x => `<li>${esc(x)}</li>`).join('')}</ul></details>
      </div>
      <section class="callout"><h4>إن وصلت تالفة</h4><p>${esc(c.damaged)}</p></section>
    </div>`;
    panel.classList.toggle('has-shot', !!p.photo);
    document.getElementById('detailOrder').href = items[k].dataset.href || items[k].querySelector('a.btn').href;
    body.scrollTop = 0;
  };
  const open = k => {
    current = k; render(k); opener = document.activeElement;
    if (matchMedia('(max-width: 860px)').matches) {                  // on a phone the sheet covers the lower part: lift the lit candle above it
      const r = items[k].querySelector('.img').getBoundingClientRect();
      scrollBy({ top: r.bottom - 0.4 * innerHeight, behavior: 'smooth' });
    }
    scrim.hidden = false; panel.setAttribute('aria-hidden', 'false'); setInert(true);
    requestAnimationFrame(() => { scrim.classList.add('open'); panel.classList.add('open'); panel.focus({ preventScroll: true }); });
  };
  const close = () => {
    panel.classList.remove('open'); scrim.classList.remove('open'); panel.setAttribute('aria-hidden', 'true');
    setTimeout(() => { scrim.hidden = true; }, 350); setInert(false);
    if (opener && opener.focus) opener.focus({ preventScroll: true });
    current = -1;
  };
  items.forEach((el, k) => {
    const d = el.querySelector('[data-detail]');                     // only the static shelf has its own details button
    if (d) d.addEventListener('click', e => { e.stopPropagation(); open(k); });
    el.querySelector('.img').addEventListener('click', () => { if (el.classList.contains('is-active')) open(k); });   // pressing the lit candle itself
  });
  if (pickBar) pickBar.querySelector('[data-pick-detail]').addEventListener('click', () => { const k = items.indexOf(focusItem); if (k >= 0) open(k); });
  document.getElementById('detailClose').addEventListener('click', close);
  scrim.addEventListener('click', close);
  addEventListener('keydown', e => { if (e.key === 'Escape' && current >= 0) close(); });
})();

/* ABOUT: the line beside the steps is a fuse. A small ember travels down it as you scroll, and each step lights up when the ember
   reaches it, like the flame burning down the candle behind. Without JavaScript every step is simply visible. */
const steps = document.querySelector('.steps');
if (steps) {
  const lis = [...steps.querySelectorAll('li')];
  const ember = document.createElement('span'); ember.className = 'fuse'; ember.setAttribute('aria-hidden', 'true');
  steps.append(ember); steps.classList.add('js');
  const place = () => {
    const r = steps.getBoundingClientRect(), mark = innerHeight * 0.62;       // the ember rides a little below the middle of the screen
    steps.style.setProperty('--p', Math.min(Math.max((mark - r.top) / r.height, 0), 1).toFixed(3));
    lis.forEach(li => { const b = li.getBoundingClientRect(); li.classList.toggle('lit', b.top + b.height * 0.3 < mark); });
  };
  addEventListener('scroll', place, { passive: true }); addEventListener('resize', place); place();
}

/* HEADER: only one filled order button on screen at a time. The header one steps aside while the hero button, the shelf or the closing button is visible. */
(async () => {
  await window.shelvesReady;                                         // the shelves are built first, so the right elements are watched
  const btn = document.querySelector('.top .btn');
  const targets = [...document.querySelectorAll('.hero .cta, .shelf, .closing .btn')];
  if (!btn || !targets.length) return;
  const seen = new Set();
  const io = new IntersectionObserver(es => {
    es.forEach(e => (e.isIntersecting ? seen.add(e.target) : seen.delete(e.target)));
    btn.classList.toggle('away', seen.size > 0);
  }, { threshold: 0.25 });
  targets.forEach(t => io.observe(t));
})();

/* MOTION: the ending flame lights itself when you arrive, and every looping animation sleeps while it is off screen. */
(() => {
  const flame = document.querySelector('.closing .flame');
  if (flame) flame.classList.add('unlit');                           // without JavaScript it simply stays lit
  const loops = [...document.querySelectorAll('.closing .flame, .steps .fuse, .cue, .boot')];
  const io = new IntersectionObserver(es => es.forEach(e => {
    e.target.classList.toggle('asleep', !e.isIntersecting);
    if (e.isIntersecting && e.target === flame) e.target.classList.remove('unlit');
  }), { threshold: 0.5 });
  loops.forEach(l => io.observe(l));
})();
