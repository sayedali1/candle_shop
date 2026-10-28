/* Contact sheet: every recipe in one picture, next to the photo it was built from, for a quick look at all of them together. */
import * as THREE from 'three';
import { makeBuilder, makeFlame } from './candle-builder.js';

const $ = id => document.getElementById(id);
const canvas = $('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 60);
const builder = makeBuilder(THREE);

const pmrem = new THREE.PMREMGenerator(renderer);
const studio = new THREE.Scene();
studio.add(new THREE.Mesh(new THREE.BoxGeometry(20, 20, 20), new THREE.MeshBasicMaterial({ color: 0x0a0806, side: THREE.BackSide })));
[[8, 3, [-8, 3, 2], 0xffc890, 6], [2, 10, [8, 2, -2], 0x9db8ff, 3], [10, 6, [0, 9, 0], 0xfff0dd, 2.5]].forEach(([w, h, pos, c, power]) => {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(c).multiplyScalar(power), side: THREE.DoubleSide }));
  m.position.set(...pos); m.lookAt(0, 0, 0); studio.add(m);
});
scene.environment = pmrem.fromScene(studio, 0.02).texture;
scene.background = new THREE.Color(0x140e0a);
const hemi = new THREE.HemisphereLight(0x8a7a6a, 0x120c08, 0.5), key = new THREE.DirectionalLight(0xffffff, 1.8), fill = new THREE.DirectionalLight(0xdde6ff, 0.6);
key.position.set(3, 4, 5); fill.position.set(-4, 2, 3);
scene.add(hemi, key, fill);
const table = new THREE.Mesh(new THREE.PlaneGeometry(30, 30).rotateX(-Math.PI / 2), new THREE.MeshStandardMaterial({ color: 0x241810, roughness: 0.7 }));
table.position.y = -0.001; scene.add(table);

const names = await (await fetch('recipes/index.json')).json();
const data = await (await fetch('products.json')).json();
const recipes = await Promise.all(names.map(n => fetch(`recipes/${n}.json`).then(r => r.json())));
const items = recipes.map((r, i) => { const c = builder.build(r); c.group.scale.setScalar(c.size); c.group.rotation.y = c.turn; c.group.position.set((i % 4 - 1.5) * 1.55, 0, i < 4 ? 0.8 : -0.8); scene.add(c.group); return c; });
const flame = makeFlame(THREE); scene.add(flame);
const flames = items.map(() => makeFlame(THREE)); flames.forEach(f => scene.add(f));
const lights = items.map(() => { const l = new THREE.PointLight(0xffa447, 0, 4, 2); scene.add(l); return l; });

$('photos').innerHTML = recipes.map((r, i) => {
  const p = data.items[i] && data.items[i].photo;
  return `<figure>${p ? `<img src="${p.src}" alt="" style="object-position:${p.pos}">` : ''}<figcaption>${i + 1}. ${names[i].slice(3)}</figcaption></figure>`;
}).join('');
scene.remove(flame);

const state = { lit: false, light: 'studio' };
$('lit').addEventListener('click', e => { state.lit = !state.lit; e.target.setAttribute('aria-pressed', state.lit); });
$('light').addEventListener('change', e => { state.light = e.target.value; });
const clock = new THREE.Clock();
function frame() {
  requestAnimationFrame(frame);
  const t = clock.elapsedTime; clock.getDelta();
  const w = canvas.clientWidth, h = canvas.clientHeight;
  if (canvas.width !== Math.floor(w * devicePixelRatio)) { renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
  camera.position.set(0, 3.0, 6.0); camera.lookAt(0, 0.5, 0);
  const studioOn = state.light === 'studio';
  key.intensity = studioOn ? 1.8 : 0; fill.intensity = studioOn ? 0.6 : 0; hemi.intensity = studioOn ? 0.5 : 0.25;
  items.forEach((c, i) => {
    const s = c.size, x = c.group.position.x, z = c.group.position.z, amt = state.lit ? 1 : 0;
    c.tints.forEach(({ m, base }) => m.color.copy(base).multiplyScalar(studioOn ? 1 : (0.5 + 0.5 * amt)));
    const flick = flames[i].update(t + i, x + c.info.flameX * s, c.info.wickY * s - 0.005 * s, s, amt, c.info.fs, c.info.fw);
    flames[i].position.z = z;
    c.glows.forEach(({ m, k }) => { m.emissiveIntensity = k * amt * (1 + flick * 1.6); });
    lights[i].position.set(x, c.info.wickY * s + 0.4 * s, z + 0.3); lights[i].intensity = state.lit && !studioOn ? 3.4 : 0;
  });
  renderer.render(scene, camera);
}
$('msg').textContent = recipes.length + ' candles';
frame();
