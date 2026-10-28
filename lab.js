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
  candle = builder.build(recipe);
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
  const r = dist * (candle.size > 1.1 ? 1.1 : 1);
  camera.position.set(Math.sin(yaw) * Math.cos(pitch) * r, 0.55 + Math.sin(pitch) * r, Math.cos(yaw) * Math.cos(pitch) * r);
  camera.lookAt(0, 0.5, 0);
  renderer.render(scene, camera);
}
function resize() {
  const w = canvas.clientWidth, h = canvas.clientHeight; if (!w || !h) return;
  renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
}
addEventListener('resize', resize); new ResizeObserver(resize).observe(canvas); resize();

/* ---------- controls ---------- */
let drag = null;
canvas.addEventListener('pointerdown', e => { drag = [e.clientX, e.clientY]; canvas.setPointerCapture(e.pointerId); });
canvas.addEventListener('pointermove', e => { if (!drag) return; yaw -= (e.clientX - drag[0]) * 0.008; pitch = Math.min(1.35, Math.max(-0.05, pitch + (e.clientY - drag[1]) * 0.006)); drag = [e.clientX, e.clientY]; });
canvas.addEventListener('pointerup', () => { drag = null; });
canvas.addEventListener('wheel', e => { e.preventDefault(); dist = Math.min(9, Math.max(2, dist * (1 + e.deltaY * 0.001))); }, { passive: false });
document.querySelectorAll('[data-view]').forEach(b => b.addEventListener('click', () => { [yaw, pitch] = views[b.dataset.view]; }));
$('lit').addEventListener('click', e => { state.lit = !state.lit; e.target.setAttribute('aria-pressed', state.lit); });
$('spin').addEventListener('click', e => { state.spin = !state.spin; e.target.setAttribute('aria-pressed', state.spin); });
$('light').addEventListener('change', e => { state.light = e.target.value; lighting(); });
$('save').addEventListener('click', () => { const a = document.createElement('a'); a.href = canvas.toDataURL('image/png'); a.download = 'candle-lab.png'; a.click(); });
$('copy').addEventListener('click', () => navigator.clipboard && navigator.clipboard.writeText($('json').value));
$('file').addEventListener('change', e => { const f = e.target.files[0]; if (f) showRef(URL.createObjectURL(f)); });
function showRef(src) { $('ref').innerHTML = ''; const i = new Image(); i.src = src; i.alt = 'reference photo'; $('ref').append(i); }

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
  if (q.get('recipe') && names.includes(q.get('recipe'))) $('pick').value = q.get('recipe');
  if (q.get('ref')) showRef(q.get('ref'));
  if (q.get('light')) { state.light = q.get('light'); $('light').value = state.light; }
  if (q.get('lit') === '0') { state.lit = false; amount = 0; $('lit').setAttribute('aria-pressed', false); }
  lighting(); await load($('pick').value); frame();
})();
