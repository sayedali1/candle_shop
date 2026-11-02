/* Candle Lab: shows one candle built from a recipe, next to a reference photo, so we can compare and polish it.
   Use: open lab.html through a local server (open-page.bat), pick a recipe or paste one, load the photo, compare lit/unlit and in the three lightings. */
import * as THREE from 'three';
import { makeBuilder, makeFlame } from './candle-builder.js';

const $ = id => document.getElementById(id);
const canvas = $('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 50);
const builder = makeBuilder(THREE);
try { builder.setMarching((await import('three/addons/objects/MarchingCubes.js')).MarchingCubes); } catch (e) { /* no blobs */ }
try { builder.setLoader((await import('three/addons/loaders/GLTFLoader.js')).GLTFLoader); } catch (e) { /* no GLB loader: a recipe with a "model" shows nothing */ }   // for recipes with a "model" (a 3D file)

/* the same studio of soft lights the page uses, so glass and glaze reflect what they will reflect on the page */
const pmrem = new THREE.PMREMGenerator(renderer);
const studio = new THREE.Scene();
studio.add(new THREE.Mesh(new THREE.BoxGeometry(20, 20, 20), new THREE.MeshBasicMaterial({ color: 0x0a0806, side: THREE.BackSide })));
[[8, 3, [-8, 3, 2], 0xffc890, 6], [2, 10, [8, 2, -2], 0x9db8ff, 3], [10, 6, [0, 9, 0], 0xfff0dd, 2.5]].forEach(([w, h, pos, c, power]) => {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(c).multiplyScalar(power), side: THREE.DoubleSide }));
  m.position.set(...pos); m.lookAt(0, 0, 0); studio.add(m);
});
scene.environment = pmrem.fromScene(studio, 0.02).texture;
const bgTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d'); const r = g.createRadialGradient(128, 160, 0, 128, 160, 210); r.addColorStop(0, '#2e1a0a'); r.addColorStop(0.55, '#170f09'); r.addColorStop(1, '#0b0705'); g.fillStyle = r; g.fillRect(0, 0, 256, 256); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })();
scene.background = bgTex;

/* a dark table that catches the light */
const table = new THREE.Mesh(new THREE.CircleGeometry(5, 64), new THREE.MeshPhysicalMaterial({ color: 0x1d140e, roughness: 0.6, clearcoat: 0.1, envMapIntensity: 0.3 }));
table.rotation.x = -Math.PI / 2; table.position.y = -0.001; scene.add(table);

/* lights: the flame's own light, a warm lamp, and soft studio lights. The preset decides which are on. */
const flameLight = new THREE.PointLight(0xffa447, 0, 8, 2);
const hemi = new THREE.HemisphereLight(0x6a5a4a, 0x120c08, 0.3);
const lamp = new THREE.DirectionalLight(0xffd2a0, 0); lamp.position.set(-3, 3, 4);
const key = new THREE.DirectionalLight(0xffffff, 0); key.position.set(3, 4, 4);
const fill = new THREE.DirectionalLight(0xdde6ff, 0); fill.position.set(-4, 2, 2);
const rim = new THREE.DirectionalLight(0xffe0c0, 0); rim.position.set(0, 3, -4);
scene.add(flameLight, hemi, lamp, key, fill, rim);
const flame = makeFlame(THREE); scene.add(flame);
const glow = new THREE.Sprite(new THREE.SpriteMaterial({
  map: (() => { const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d'); const r = g.createRadialGradient(64, 64, 0, 64, 64, 64); r.addColorStop(0, 'rgba(255,190,90,0.9)'); r.addColorStop(0.35, 'rgba(255,140,50,0.28)'); r.addColorStop(1, 'rgba(255,120,40,0)'); g.fillStyle = r; g.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c); })(),
  blending: THREE.AdditiveBlending, depthWrite: false, transparent: true
}));
glow.renderOrder = 6; scene.add(glow);

let candle = null, state = { lit: true, spin: false, light: 'flame' }, amount = 1, yaw = 0.4, pitch = 0.25, dist = 4.2, shown = 1;
const views = { front: [0, 0.12], three: [0.7, 0.3], top: [0.4, 1.1] };

function setRecipe(recipe) {
  if (candle) { scene.remove(candle.group); candle.group.traverse(o => { if (o.geometry) o.geometry.dispose(); }); }
  const t0 = performance.now();
  candle = builder.build(recipe);
  buildMs = performance.now() - t0;
  candle.group.rotation.y = 0; scene.add(candle.group);
}

function lighting() {
  const p = state.light;
  flameLight.intensity = 0; hemi.intensity = 0.3; lamp.intensity = key.intensity = fill.intensity = rim.intensity = 0;
  if (p === 'room') { hemi.intensity = 0.5; lamp.intensity = 1.1; }
  if (p === 'studio') { hemi.intensity = 0.6; key.intensity = 2.2; fill.intensity = 0.8; rim.intensity = 1.2; }
}

/* ---------- the loop ---------- */
const clock = new THREE.Clock();
function frame() {
  requestAnimationFrame(frame);
  const dt = Math.min(clock.getDelta(), 0.05), t = clock.elapsedTime;
  if (!candle) return;
  amount += ((state.lit ? 1 : 0) - amount) * (1 - Math.exp(-dt * 6));
  const showFlame = state.light !== 'studio' || state.lit;
  if (state.spin) yaw += dt * 0.5;
  const info = candle.info, s = candle.size;
  candle.group.scale.setScalar(s);
  candle.group.rotation.y = candle.turn;
  const dim = 0.4 + 0.6 * amount;
  candle.tints.forEach(({ m, base }) => m.color.copy(base).multiplyScalar(state.light === 'studio' ? 1 : dim));
  const tipX = info.flameX * s, tipY = info.wickY * s;
  const flick = flame.update(t, tipX, tipY - 0.005 * s, s, showFlame ? amount : 0, info.fs, info.fw);
  glow.visible = showFlame && amount > 0.01;
  glow.position.set(tipX, tipY + 0.12 * s, 0); glow.scale.setScalar(1.05 * s * info.fs); glow.material.opacity = (0.9 + flick) * amount;
  const burn = showFlame ? (1 + flick * 1.6) * amount : 0;
  candle.glows.forEach(({ m, k }) => { m.emissiveIntensity = k * burn; });
  flameLight.position.set(tipX, tipY + 0.4 * s, 0.3 * s);
  flameLight.intensity = state.light === 'studio' ? 0 : 5 * (1 + flick * 1.2) * amount;
  if (photoView) {                                                  // the camera the photo was taken with (found by tools/fit_pose.py): the 3D lines up with the photo exactly
    const c = photoCam, T = c.target, rr = c.dist;
    camera.position.set(T[0] + rr * Math.sin(c.yaw) * Math.cos(c.pitch), T[1] + rr * Math.sin(c.pitch), T[2] + rr * Math.cos(c.yaw) * Math.cos(c.pitch));
    camera.lookAt(T[0], T[1], T[2]);
    if (camera.fov !== c.fov) { camera.fov = c.fov; camera.updateProjectionMatrix(); }
  } else {
    if (camera.fov !== 30) { camera.fov = 30; camera.updateProjectionMatrix(); }
    const r = dist * (candle.size > 1.1 ? 1.1 : 1);
    camera.position.set(Math.sin(yaw) * Math.cos(pitch) * r, 0.55 + Math.sin(pitch) * r, Math.cos(yaw) * Math.cos(pitch) * r);
    camera.lookAt(0, 0.5, 0);
  }
  renderer.render(scene, camera);
}
/* photo view: the picture and the 3D share one frame with the photo's own shape, so a point in the photo is the same point in the 3D */
let photoView = false, photoCam = null, cropRect = null;
function layoutPhoto() {
  const v = canvas.parentElement, ov = $('ov'), els = [canvas, ov];
  if (photoView && ov.naturalWidth) {
    const W = v.clientWidth, H = v.clientHeight, nw = ov.naturalWidth, nh = ov.naturalHeight;
    const cr = cropRect || [0, 0, nw, nh], cw = cr[2] - cr[0], ch = cr[3] - cr[1], k = Math.min(W / cw, H / ch);
    const px = (e, l, t, w, h) => { e.style.inset = 'auto'; e.style.left = l + 'px'; e.style.top = t + 'px'; e.style.width = w + 'px'; e.style.height = h + 'px'; };
    const l0 = (W - cw * k) / 2, t0 = (H - ch * k) / 2;
    px(canvas, l0, t0, cw * k, ch * k);                                    // the 3D is drawn only for the part of the photo we look at ("crop": photo pixels)...
    px(ov, l0 - cr[0] * k, t0 - cr[1] * k, nw * k, nh * k);                // ...and the photo is laid under the same frame
    v.style.overflow = 'hidden'; ov.style.objectFit = 'fill';
    const u0 = photoCam?.u0 || 0, v0 = photoCam?.v0 || 0;               // a measured camera may sit off the picture's middle (tools/gen_mermaid.py, gen_knot.py): shift the frame the same way
    if (cropRect || u0 || v0) camera.setViewOffset(nw, nh, cr[0] - u0, cr[1] - v0, cw, ch); else camera.clearViewOffset();
    renderer.setPixelRatio(cropRect ? 1 : Math.min(devicePixelRatio || 1, 2));
  } else { els.forEach(e => { e.style.inset = ''; e.style.left = e.style.top = e.style.width = e.style.height = ''; }); ov.style.objectFit = 'contain'; camera.clearViewOffset(); }
  resize();
}
function resize() {
  const w = canvas.clientWidth, h = canvas.clientHeight; if (!w || !h) return;
  renderer.setSize(w, h, false); camera.aspect = camera.view && camera.view.enabled ? camera.view.fullWidth / camera.view.fullHeight : w / h; camera.updateProjectionMatrix();
}
addEventListener('resize', layoutPhoto); new ResizeObserver(layoutPhoto).observe(canvas.parentElement); resize();

/* ---------- controls ---------- */
let drag = null;
canvas.addEventListener('pointerdown', e => { drag = [e.clientX, e.clientY]; canvas.setPointerCapture(e.pointerId); });
canvas.addEventListener('pointermove', e => { if (!drag) return; yaw -= (e.clientX - drag[0]) * 0.008; pitch = Math.min(1.35, Math.max(-0.05, pitch + (e.clientY - drag[1]) * 0.006)); drag = [e.clientX, e.clientY]; });
canvas.addEventListener('pointerup', () => { drag = null; });
canvas.addEventListener('wheel', e => { e.preventDefault(); dist = Math.min(9, Math.max(2, dist * (1 + e.deltaY * 0.001))); }, { passive: false });
document.querySelectorAll('[data-view]').forEach(b => b.addEventListener('click', () => { [yaw, pitch] = views[b.dataset.view]; }));
$('lit').addEventListener('click', e => { state.lit = !state.lit; e.target.setAttribute('aria-pressed', state.lit); });
$('spin').addEventListener('click', e => { state.spin = !state.spin; e.target.setAttribute('aria-pressed', state.spin); });
$('pv').addEventListener('click', () => { photoView = !photoView; $('pv').setAttribute('aria-pressed', photoView); if (photoView) { $('ovo').value = 0; placeOverlay(); } layoutPhoto(); });
$('light').addEventListener('change', e => { state.light = e.target.value; lighting(); });
$('save').addEventListener('click', () => { const a = document.createElement('a'); a.href = canvas.toDataURL('image/png'); a.download = 'candle-lab.png'; a.click(); });
$('copy').addEventListener('click', () => navigator.clipboard && navigator.clipboard.writeText($('json').value));
$('file').addEventListener('change', e => { const f = e.target.files[0]; if (f) showRef(URL.createObjectURL(f)); });
function showRef(src) { $('ref').innerHTML = ''; $('ov').onload = layoutPhoto; const i = new Image(); i.src = src; i.alt = 'reference photo'; $('ref').append(i); $('ov').src = src; $('ovc').classList.add('on'); }

/* the photo laid over the 3D: slide the see-through bar, match size and place, or switch on "differences" (same = black) */
function placeOverlay() {
  const o = $('ov'), d = $('ovd').checked;
  o.style.opacity = d ? 1 : $('ovo').value / 100;
  o.style.mixBlendMode = d ? 'difference' : 'normal';
  o.style.transform = `translate(${$('ovx').value}%, ${$('ovy').value}%) scale(${$('ovs').value / 100})`;
}
['ovo', 'ovs', 'ovx', 'ovy', 'ovd'].forEach(id => $(id).addEventListener('input', placeOverlay));

/* ---------- checks: the things a person spots at once, done by the program ----------
   1. the silhouette from 8 sides: more than one piece means a gap or a part floating in the air
   2. cost: draw calls and triangles of this candle, and how long it took to build
   3. size: height and width in candle units */
const maskRT = new THREE.WebGLRenderTarget(160, 200);
const maskCam = new THREE.PerspectiveCamera(30, 0.8, 0.1, 50);
const maskMat = new THREE.MeshBasicMaterial({ color: 0xffffff, toneMapped: false });
let buildMs = 0;
function pieces(yawA) {
  const r = 4.6 * (candle.size > 1.1 ? 1.1 : 1);
  maskCam.position.set(Math.sin(yawA) * r, 0.7, Math.cos(yawA) * r); maskCam.lookAt(0, 0.5, 0);
  renderer.setRenderTarget(maskRT); renderer.clear(); renderer.render(scene, maskCam); renderer.setRenderTarget(null);
  const W = 160, H = 200, px = new Uint8Array(W * H * 4); renderer.readRenderTargetPixels(maskRT, 0, 0, W, H, px);
  const on = new Uint8Array(W * H); for (let i = 0; i < W * H; i++) on[i] = px[i * 4] > 60 ? 1 : 0;
  const found = [];
  for (let s = 0; s < W * H; s++) {
    if (!on[s]) continue;
    let n = 0, top = s, st = [s]; on[s] = 0;
    while (st.length) {
      const p = st.pop(); n++; if (p < top) top = p;
      const x = p % W, nb = [x > 0 ? p - 1 : -1, x < W - 1 ? p + 1 : -1, p - W, p + W];
      for (const q of nb) if (q >= 0 && q < W * H && on[q]) { on[q] = 0; st.push(q); }
    }
    found.push(n);
  }
  return found.sort((a, b) => b - a);
}
function runChecks() {
  if (!candle) return;
  const out = [], bad = t => `<span class="bad">${t}</span>`, ok = t => `<span class="ok">${t}</span>`;
  const hide = []; scene.traverse(o => { if ((o.isSprite || o === table || o === flame) && o.visible) { o.visible = false; hide.push(o); } });
  const bg = scene.background, ov = scene.overrideMaterial, ca = renderer.getClearAlpha(), cc = renderer.getClearColor(new THREE.Color());
  scene.background = null; scene.overrideMaterial = maskMat; renderer.setClearColor(0x000000, 1);
  const names = ['front', 'front-right', 'right', 'back-right', 'back', 'back-left', 'left', 'front-left'], split = [];
  names.forEach((nm, i) => { const p = pieces(i * Math.PI / 4).filter(n => n >= 3); if (p.length > 1) split.push(`${nm}: ${p.length} pieces (${p.join(', ')} px)`); });
  scene.background = bg; scene.overrideMaterial = ov; renderer.setClearColor(cc, ca); hide.forEach(o => { o.visible = true; });
  out.push(split.length ? bad('<b>Gap or floating part</b>') + '\n' + split.join('\n') : ok('<b>Silhouette:</b> one piece from all 8 sides'));

  let meshes = 0, t = 0; candle.group.traverse(o => { if (o.isMesh) { meshes++; const g = o.geometry; t += (g.index ? g.index.count : g.attributes.position.count) / 3; } });
  const os = outlineScore();
  if (os) out.push(`<b>Outline vs photo:</b> fills ${(os.cover * 100).toFixed(0)}% of the part that is surely this figure, ${(os.spill * 100).toFixed(0)}% of the 3D sticks out of the photo's figure. ` + (os.cover > 0.93 && os.spill < 0.06 ? ok('close') : bad('not close yet: fix the biggest difference, then check again')));
  out.push(`<b>Cost:</b> ${meshes} meshes, ${Math.round(t / 1000)}k triangles. ` + (meshes > 40 || t > 60000 ? bad('heavy for a phone shelf') : ok('fine for a phone shelf')));
  out.push(`<b>Build time here:</b> ${Math.round(buildMs)} ms ` + (buildMs > 120 ? bad('(a phone is 3 to 5 times slower: it will freeze the page, consider baking it to a .glb)') : ok('(a phone is 3 to 5 times slower)')));
  const box = new THREE.Box3().setFromObject(candle.group);
  const sz = box.getSize(new THREE.Vector3());
  out.push(`<b>Size:</b> ${sz.y.toFixed(2)} tall, ${sz.x.toFixed(2)} wide, ${sz.z.toFixed(2)} deep (about 1 tall is normal)`);
  out.push('<b>You still judge by eye:</b> does it read as carved wax, not a real animal? lit and unlit? from above? Lay the photo over it and look for the biggest difference.');
  $('checks').innerHTML = out.join('\n');
}
$('check').addEventListener('click', runChecks);

/* the outline check: how well does the 3D fill the part of the photo that is surely this figure (care.png), and how much sticks out of the photo's figure (union.png)?
   Needs the photo's camera (?photocam=tools/fit/pose.json) and the masks from tools/photo_mask.py (?masks=tools/fit/) */
let masks = null;
const PW = 163, PH = 216, phRT = new THREE.WebGLRenderTarget(PW, PH);
async function loadMasks(dir) {
  const grab = async (f) => { const im = new Image(); im.src = dir + f; await im.decode(); const c = document.createElement('canvas'); c.width = PW; c.height = PH; const g = c.getContext('2d'); g.drawImage(im, 0, 0, PW, PH); const d = g.getImageData(0, 0, PW, PH).data; const a = new Uint8Array(PW * PH); for (let i = 0; i < a.length; i++) a[i] = d[i * 4] > 127 ? 1 : 0; return a; };
  masks = { union: await grab('union.png'), care: await grab('care.png') };
}
function outlineScore() {
  if (!masks || !photoCam || !candle) return null;
  const hide = []; scene.traverse(o => { if ((o.isSprite || o === table || o === flame) && o.visible) { o.visible = false; hide.push(o); } });
  const bg = scene.background, ov = scene.overrideMaterial, ca = renderer.getClearAlpha(), cc = renderer.getClearColor(new THREE.Color());
  scene.background = null; scene.overrideMaterial = maskMat; renderer.setClearColor(0x000000, 1);
  const c = photoCam, T = c.target; maskCam.fov = c.fov; maskCam.aspect = PW / PH; maskCam.updateProjectionMatrix();
  maskCam.position.set(T[0] + c.dist * Math.sin(c.yaw) * Math.cos(c.pitch), T[1] + c.dist * Math.sin(c.pitch), T[2] + c.dist * Math.cos(c.yaw) * Math.cos(c.pitch)); maskCam.lookAt(T[0], T[1], T[2]);
  renderer.setRenderTarget(phRT); renderer.clear(); renderer.render(scene, maskCam); renderer.setRenderTarget(null);
  const px = new Uint8Array(PW * PH * 4); renderer.readRenderTargetPixels(phRT, 0, 0, PW, PH, px);
  scene.background = bg; scene.overrideMaterial = ov; renderer.setClearColor(cc, ca); hide.forEach(o => { o.visible = true; });
  maskCam.fov = 30; maskCam.aspect = 0.8; maskCam.updateProjectionMatrix();
  let care = 0, miss = 0, rend = 0, out = 0;
  for (let y = 0; y < PH; y++) for (let x = 0; x < PW; x++) {
    const r = px[((PH - 1 - y) * PW + x) * 4] > 60 ? 1 : 0, i = y * PW + x;
    if (masks.care[i]) { care++; if (!r) miss++; }
    if (r) { rend++; if (!masks.union[i]) out++; }
  }
  return { cover: 1 - miss / care, spill: out / Math.max(rend, 1) };
}

let timer = null;
$('json').addEventListener('input', () => {
  clearTimeout(timer);
  timer = setTimeout(() => { try { setRecipe(JSON.parse($('json').value)); $('err').textContent = ''; } catch (e) { $('err').textContent = e.message; } }, 400);
});

async function load(name) {
  const r = await (await fetch(`recipes/${name}.json`)).json();
  $('json').value = JSON.stringify(r, null, 1); $('err').textContent = '';
  setRecipe(r);
}
(async () => {
  const names = await (await fetch('recipes/index.json')).json();
  $('pick').innerHTML = names.map(n => `<option>${n}</option>`).join('');
  $('pick').addEventListener('change', () => load($('pick').value));
  const q = new URLSearchParams(location.search);
  if (q.get('recipe')) { if (!names.includes(q.get('recipe'))) $('pick').insertAdjacentHTML('beforeend', `<option>${q.get('recipe')}</option>`); $('pick').value = q.get('recipe'); }
  if (q.get('ref')) showRef(q.get('ref'));
  if (q.get('light')) { state.light = q.get('light'); $('light').value = state.light; }
  if (q.get('lit') === '0') { state.lit = false; amount = 0; $('lit').setAttribute('aria-pressed', false); }
  if (q.get('crop')) cropRect = q.get('crop').split(',').map(Number);
  if (q.get('photocam')) { try { photoCam = (await (await fetch(q.get('photocam'))).json()).camera; $('pv').hidden = false; } catch (e) { /* no photo camera */ } }
  if (q.get('masks')) { try { await loadMasks(q.get('masks')); } catch (e) { /* no masks */ } }
  lighting(); await load($('pick').value); frame();
  if (q.get('photoview') === '1' && photoCam) $('pv').click();
})();
