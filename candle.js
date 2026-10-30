/* Hero candle, drawn in code with Three.js. Version 2.
   Studio-style reflections on the glass, wax that glows around the flame, a paper label,
   a two-layer flame and a soft bloom (desktop only).
   DRAFT: shapes, colors and light are placeholders until the brand stage.
   Scrolling the hero turns the candle and moves the camera closer. */

import { makeBuilder, customize } from './candle-builder.js?v=6';

const hero = document.getElementById('hero');
const stage = document.getElementById('stage');
const canvas = document.getElementById('candle');
const bg = document.getElementById('candleBg') || stage;          // the fixed layer that holds the canvas
const productsEl = document.getElementById('products');
const aboutEl = document.getElementById('about');
let shelfEls = [], shelfItems = [], shelfOf = [];                    // every shelf, every candle slot of every shelf, and which shelf each slot belongs to
const copyA = document.getElementById('copyA');
const copyB = document.getElementById('copyB');
const cue = document.getElementById('cue');
const lightEl = document.querySelector('.candle-light');
/* reduced motion: no smoothing, no flicker. Adding ?still to the address does the same, which is handy for checking an exact scroll position. */
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches || location.search.includes('still');
const lite = matchMedia('(max-width: 860px), (pointer: coarse)').matches;

const clamp = (v, a = 0, b = 1) => Math.min(Math.max(v, a), b);
const lerp = (a, b, t) => a + (b - a) * t;
const smooth = x => x * x * (3 - 2 * x);
const band = (x, a, b) => smooth(clamp((x - a) / (b - a)));

/* if anything about 3D fails, show the flat photo instead */
function showFallback(why) { stage.classList.add('no3d'); document.documentElement.classList.add('no3d'); console.warn('3D candle off:', why); }

async function start() {
  /* downloads that do not depend on Three.js start now, so they run beside it instead of after it */
  const fontP = Promise.race([document.fonts.load('700 60px Cairo'), new Promise(r => setTimeout(r, 1500))]).catch(() => {});
  const recipesP = fetch('recipes/index.json').then(r => r.json()).then(names => Promise.all(names.map(n => fetch(`recipes/${n}.json`).then(r => r.json())))).catch(e => { console.warn('shelf recipes not loaded:', e); return []; });
  let THREE;
  try { THREE = await import('three'); }
  catch (e) { return showFallback('could not load Three.js'); }

  /* the bloom is optional: if it cannot load, we simply render without it */
  let post = null;
  if (!lite) {
    try {
      const [a, b, c, d, f] = await Promise.all([
        import('three/addons/postprocessing/EffectComposer.js'), import('three/addons/postprocessing/RenderPass.js'),
        import('three/addons/postprocessing/UnrealBloomPass.js'), import('three/addons/postprocessing/OutputPass.js'),
        import('three/addons/postprocessing/ShaderPass.js')
      ]);
      post = { EffectComposer: a.EffectComposer, RenderPass: b.RenderPass, UnrealBloomPass: c.UnrealBloomPass, OutputPass: d.OutputPass, ShaderPass: f.ShaderPass };
    } catch (e) { console.warn('bloom off:', e); }
  }

  let renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' }); }
  catch (e) { return showFallback('WebGL is not available'); }

  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  const qs = new URLSearchParams(location.search);                 // ?w=0 turns the idle pre-build off (for measuring)
  let pixelRatio = Math.min(devicePixelRatio || 1, (lite ? 1.5 : 2));      // (a phone may step it down while scrolling, see the frame loop)
  renderer.setPixelRatio(pixelRatio);
  renderer.shadowMap.enabled = !lite;                              // real soft shadows on desktop; phones keep the cheap painted contact shadow
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 50);

  /* ---------- small helpers that make textures with a canvas ---------- */
  const canvasTexture = (w, h, draw, srgb = true) => {
    const c = document.createElement('canvas'); c.width = w; c.height = h;
    draw(c.getContext('2d'), w, h);
    const t = new THREE.CanvasTexture(c);
    if (srgb) t.colorSpace = THREE.SRGBColorSpace;
    return t;
  };
  const radialTexture = (stops, srgb = true) => canvasTexture(128, 128, (g) => {
    const r = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    stops.forEach(([o, col]) => r.addColorStop(o, col));
    g.fillStyle = r; g.fillRect(0, 0, 128, 128);
  }, srgb);
  const noiseTexture = (size, spread) => {
    const t = canvasTexture(size, size, (g) => {
      const img = g.createImageData(size, size);
      for (let i = 0; i < img.data.length; i += 4) { const v = 128 + (Math.random() - 0.5) * spread; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255; }
      g.putImageData(img, 0, 0);
    }, false);
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(3, 2);
    return t;
  };
  const lathe = pts => new THREE.LatheGeometry(pts.map(([r, y]) => new THREE.Vector2(r, y)), 72);

  /* ---------- the room: a dark warm backdrop, and a studio of soft lights that the glass reflects ---------- */
  scene.background = canvasTexture(512, 512, (g) => {
    const r = g.createRadialGradient(256, 330, 0, 256, 330, 420);
    r.addColorStop(0, '#4a1407'); r.addColorStop(0.55, '#230a04'); r.addColorStop(1, '#100302');
    g.fillStyle = r; g.fillRect(0, 0, 512, 512);
  });

  const pmrem = new THREE.PMREMGenerator(renderer);
  const studio = new THREE.Scene();
  studio.add(new THREE.Mesh(new THREE.BoxGeometry(20, 20, 20), new THREE.MeshBasicMaterial({ color: 0x0a0806, side: THREE.BackSide })));
  const softbox = (w, h, pos, color, power) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(color).multiplyScalar(power), side: THREE.DoubleSide }));
    m.position.set(...pos); m.lookAt(0, 0, 0); studio.add(m);
  };
  softbox(8, 3, [-8, 3, 2], 0xffc890, 6);      // warm strip on the left
  softbox(2, 10, [8, 2, -2], 0x9db8ff, 3);     // cool edge light on the right
  softbox(10, 6, [0, 9, 0], 0xfff0dd, 2.5);    // soft light from above
  scene.environment = pmrem.fromScene(studio, 0.02).texture;

  /* ---------- the candle: a jar candle, 1 unit tall ---------- */
  const candle = new THREE.Group();
  scene.add(candle);

  /* desktop: real glass that bends what is behind it (a bit heavier); phones: a light see-through shell */
  const glassMat = post
    ? new THREE.MeshPhysicalMaterial({
        color: 0xffffff, metalness: 0, roughness: 0.02, transmission: 1, thickness: 0.06, ior: 1.5,
        attenuationColor: new THREE.Color(0xe6f2ec), attenuationDistance: 1.6,
        envMapIntensity: 1.8, clearcoat: 1, clearcoatRoughness: 0.03, side: THREE.DoubleSide,
        depthWrite: false                                            // otherwise the glass hides the flame inside it
      })
    : new THREE.MeshPhysicalMaterial({
        color: 0xffffff, metalness: 0, roughness: 0.03, transparent: true, opacity: 0.13,
        envMapIntensity: 1.8, clearcoat: 1, clearcoatRoughness: 0.03, side: THREE.DoubleSide, depthWrite: false
      });
  const jar = new THREE.Mesh(lathe([
    [0, 0], [0.44, 0], [0.48, 0.02], [0.5, 0.07], [0.5, 0.965], [0.497, 0.99], [0.488, 1.004],      // outside, with a rounded rim
    [0.468, 1.004], [0.459, 0.99], [0.455, 0.97], [0.455, 0.1], [0.43, 0.07], [0, 0.07]              // inside
  ]), glassMat);
  jar.renderOrder = 2;
  candle.add(jar);

  /* wax: the top surface glows warm around the wick, like light passing through real wax */
  const waxGlow = canvasTexture(4, 64, (g, w, h) => {
    const r = g.createLinearGradient(0, h, 0, 0);               // canvas top = top of the wax
    r.addColorStop(0, '#0d0602'); r.addColorStop(0.28, '#1c0d04'); r.addColorStop(0.5, '#6a3a12'); r.addColorStop(1, '#ffb060');
    g.fillStyle = r; g.fillRect(0, 0, w, h);
  });
  const waxMat = new THREE.MeshPhysicalMaterial({
    color: 0xf3e4c4, roughness: 0.42, sheen: 1, sheenRoughness: 0.5, sheenColor: new THREE.Color(0xffd9a0),
    emissive: new THREE.Color(0xffffff), emissiveMap: waxGlow, emissiveIntensity: 0.6,
    bumpMap: noiseTexture(256, 60), bumpScale: 0.6, envMapIntensity: 0.3, side: THREE.DoubleSide
  });
  const wax = new THREE.Mesh(lathe([
    [0, 0.075], [0.446, 0.075], [0.452, 0.58], [0.455, 0.618], [0.44, 0.612], [0.38, 0.604], [0.27, 0.598], [0.14, 0.59], [0.06, 0.58], [0, 0.575]   // climbs the glass at the edge, then a melt pool dips toward the wick
  ]), waxMat);
  candle.add(wax);

  /* paper label on the front of the jar. The text is a placeholder. */
  await fontP;                                                     // (if the font is late the label simply uses a fallback font)
  const logoImg = new Image(); logoImg.src = 'assets/brand/boba-logo-dark.png';               // her logo, dark ink for the paper label
  await Promise.race([logoImg.decode().catch(() => {}), new Promise(r => setTimeout(r, 1500))]);
  const paintLabel = (paper, ink, ink2, name) => canvasTexture(1024, 512, (g, w, h) => {
    g.fillStyle = paper; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 2600; i++) { g.fillStyle = `rgba(90,70,40,${Math.random() * 0.05})`; g.fillRect(Math.random() * w, Math.random() * h, 2, 2); }   // paper grain
    g.strokeStyle = ink2; g.lineWidth = 6; g.strokeRect(34, 34, w - 68, h - 68);
    g.globalAlpha = 0.5; g.lineWidth = 2; g.strokeRect(50, 50, w - 100, h - 100); g.globalAlpha = 1;
    if (logoImg.naturalWidth) { const lh = 372, lw = lh * logoImg.naturalWidth / logoImg.naturalHeight; g.drawImage(logoImg, (w - lw) / 2, (h - lh) / 2, lw, lh); }   // her logo on the label
    else {                                                           // the logo did not load: the old placeholder text
      g.fillStyle = ink; g.textAlign = 'center'; g.direction = 'rtl';
      g.font = '700 118px Cairo, Tahoma, sans-serif'; g.fillText('Boba Candels', w / 2, 235);
      g.font = '600 56px Cairo, Tahoma, sans-serif'; g.fillStyle = ink2; g.fillText(name, w / 2, 330);
    }
  });
  const labelMap = paintLabel('#eadfc8', '#2b1d0f', '#4a3520', 'شمعة يدوية');
  const labelArc = 1.7;
  const labelGeo = new THREE.CylinderGeometry(0.507, 0.507, 0.4, 64, 6, true, -labelArc / 2, labelArc);
  {
    const pa = labelGeo.attributes.position;
    for (let i = 0; i < pa.count; i++) {                             // the top corner of the paper lifts a little away from the glass
      const x = pa.getX(i), z = pa.getZ(i), y = pa.getY(i), r = Math.hypot(x, z);
      const u = (Math.atan2(x, z) + labelArc / 2) / labelArc, v = (y + 0.2) / 0.4;
      const lift = Math.pow(Math.max(0, (u - 0.82) / 0.18), 2) * Math.pow(Math.max(0, (v - 0.55) / 0.45), 2) * 0.03;
      pa.setX(i, x * (1 + lift / r)); pa.setZ(i, z * (1 + lift / r));
    }
    labelGeo.computeVertexNormals();
  }
  const label = new THREE.Mesh(
    labelGeo,
    new THREE.MeshStandardMaterial({ map: labelMap, roughness: 0.86, bumpMap: noiseTexture(256, 50), bumpScale: 0.35, side: THREE.DoubleSide, envMapIntensity: 0.4 })
  );
  label.position.y = 0.4;
  candle.add(label);

  /* the wick runs from the bottom of the jar to above the wax, so it can burn down with the wax */
  const wick = new THREE.Mesh(new THREE.CylinderGeometry(0.011, 0.013, 0.73, 8), new THREE.MeshStandardMaterial({ color: 0x17120e, roughness: 0.9 }));
  wick.position.y = 0.435; wick.rotation.z = -0.015;
  candle.add(wick);
  const ember = new THREE.Mesh(new THREE.SphereGeometry(0.017, 12, 12), new THREE.MeshBasicMaterial({ color: 0xff6a1a }));
  ember.position.set(0.0055, 0.8, 0);
  candle.add(ember);

  /* flame: an outer soft layer and a bright inner core, both swaying and flickering */
  const flameMaterial = (core) => new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    uniforms: { uTime: { value: 0 }, uFlicker: { value: 1 }, uCore: { value: core ? 1 : 0 }, uLean: { value: 0 } },
    vertexShader: `
      uniform float uTime; uniform float uLean; varying float vY; varying vec3 vN;
      void main() {
        float y = position.y / 0.27; vY = y;
        vec3 p = position;
        p.x += (sin(uTime * 7.0 + y * 4.0) * 0.012 + sin(uTime * 13.0 + y * 7.0) * 0.006) * y * y * 4.0;
        p.z += cos(uTime * 6.0 + y * 3.0) * 0.008 * y;
        p.x += uLean * y * y;
        vN = normalize(normalMatrix * normal);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
      }`,
    fragmentShader: `
      uniform float uTime; uniform float uFlicker; uniform float uCore; varying float vY; varying vec3 vN;
      void main() {
        float edge = smoothstep(0.0, 0.65, abs(vN.z));
        vec3 col = mix(vec3(0.25, 0.4, 1.0), vec3(1.0, 0.92, 0.65), smoothstep(0.0, 0.25, vY));
        col = mix(col, vec3(1.0, 0.45, 0.08), smoothstep(0.35, 1.0, vY));
        float a = edge * (1.0 - smoothstep(0.7, 1.0, vY)) * (0.35 + 0.65 * smoothstep(0.0, 0.2, vY)) * uFlicker;
        if (uCore > 1.5) { col = vec3(1.0, 0.5, 0.12); a *= 0.14; }
        else if (uCore > 0.5) { col = mix(vec3(1.0, 0.97, 0.88), vec3(1.0, 0.8, 0.4), vY); a *= 1.6; }
        a *= 0.88 + 0.12 * sin(uTime * 26.0 + vY * 9.0) * smoothstep(0.4, 1.0, vY);      // the tip flickers faster than the body
        gl_FragColor = vec4(col * 1.7, a);
      }`
  });
  /* a smooth teardrop: fat near the wick, drawing out to a point */
  const flameShape = Array.from({ length: 26 }, (_, i) => { const u = i / 25; return [0.06 * Math.sin(Math.PI * Math.pow(u, 0.7)) * (1 - 0.3 * u), u * 0.27]; });
  const flameOuterMat = flameMaterial(false), flameCoreMat = flameMaterial(true), flameHaloMat = flameMaterial(false);
  flameHaloMat.uniforms.uCore.value = 2;
  const flame = new THREE.Mesh(lathe(flameShape), flameOuterMat);
  const flameCore = new THREE.Mesh(lathe(flameShape), flameCoreMat);
  const flameHalo = new THREE.Mesh(lathe(flameShape), flameHaloMat);
  flame.position.y = flameCore.position.y = flameHalo.position.y = 0.795;
  flameHalo.renderOrder = 3; flame.renderOrder = 4; flameCore.renderOrder = 5;
  candle.add(flameHalo, flame, flameCore);

  const glow = new THREE.Sprite(new THREE.SpriteMaterial({
    map: radialTexture([[0, 'rgba(255,190,90,0.9)'], [0.35, 'rgba(255,140,50,0.28)'], [1, 'rgba(255,120,40,0)']]),
    blending: THREE.AdditiveBlending, depthWrite: false, transparent: true
  }));
  glow.position.y = 0.92; glow.scale.set(1.05, 1.05, 1); glow.renderOrder = 5;
  candle.add(glow);

  /* ---------- the light the flame throws, a glossy dark table that catches it, and a grounding shadow ---------- */
  const FLAME_LIGHT = post ? 3.4 : 5;
  const flameLight = post
    ? new THREE.SpotLight(0xffa447, FLAME_LIGHT, 8, 1.45, 0.9, 2)    // desktop: a very wide spot that casts soft shadows with one shadow pass
    : new THREE.PointLight(0xffa447, FLAME_LIGHT, 8, 2);
  flameLight.position.set(0, post ? 1.25 : 0.9, 0);               // on desktop the light sits above the flame so the wax is not blown out
  if (post) {
    flameLight.castShadow = true;
    flameLight.shadow.mapSize.set(1024, 1024); flameLight.shadow.camera.near = 0.3; flameLight.shadow.camera.far = 8; flameLight.shadow.bias = -0.0006; flameLight.shadow.radius = 4;
    scene.add(flameLight.target);
  }
  scene.add(flameLight);
  scene.add(new THREE.HemisphereLight(0x6a5a4a, 0x1a0602, 0.3));

  const table = new THREE.Mesh(
    new THREE.CircleGeometry(5, 64),
    new THREE.MeshPhysicalMaterial({
      color: 0x1d140e, roughness: 0.68, metalness: 0, clearcoat: 0.08, clearcoatRoughness: 0.6, envMapIntensity: 0.3, transparent: true,
      alphaMap: radialTexture([[0, '#fff'], [0.55, '#fff'], [1, '#000']], false)
    })
  );
  table.rotation.x = -Math.PI / 2;
  table.position.y = -0.06;                                       // the coaster sits on the table
  scene.add(table);

  const shadow = new THREE.Mesh(
    new THREE.PlaneGeometry(1.9, 1.9),
    new THREE.MeshBasicMaterial({ map: radialTexture([[0, 'rgba(0,0,0,0.8)'], [0.55, 'rgba(0,0,0,0.38)'], [1, 'rgba(0,0,0,0)']]), transparent: true, depthWrite: false })
  );
  shadow.rotation.x = -Math.PI / 2; shadow.position.y = 0.002;
  scene.add(shadow);
  const pool = new THREE.Mesh(
    new THREE.PlaneGeometry(4.6, 4.6),
    new THREE.MeshBasicMaterial({ map: radialTexture([[0, 'rgba(255,170,80,0.5)'], [0.4, 'rgba(255,140,50,0.17)'], [1, 'rgba(255,120,40,0)']]), blending: THREE.AdditiveBlending, transparent: true, depthWrite: false, opacity: 0 })
  );
  pool.rotation.x = -Math.PI / 2; pool.position.y = 0.004; pool.renderOrder = 1;
  scene.add(pool);

  /* ---------- decoration: it all sits on the turntable with the candle ---------- */
  const woodTex = canvasTexture(256, 256, (g, w, h) => {
    g.fillStyle = '#6b4a2b'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 70; i++) {
      g.strokeStyle = `rgba(${40 + Math.random() * 30 | 0},${24 + Math.random() * 20 | 0},10,${0.12 + Math.random() * 0.18})`;
      g.lineWidth = 1 + Math.random() * 2; g.beginPath();
      const y = Math.random() * h; g.moveTo(0, y);
      g.bezierCurveTo(w * 0.3, y + (Math.random() - 0.5) * 14, w * 0.7, y + (Math.random() - 0.5) * 14, w, y + (Math.random() - 0.5) * 10); g.stroke();
    }
  });
  const coaster = new THREE.Mesh(
    lathe([[0, -0.06], [0.64, -0.06], [0.68, -0.045], [0.69, -0.01], [0.66, 0], [0, 0]]),
    new THREE.MeshStandardMaterial({ map: woodTex, bumpMap: woodTex, bumpScale: 1.2, roughness: 0.55, envMapIntensity: 0.4 })
  );
  candle.add(coaster);

  const twineMat = new THREE.MeshStandardMaterial({ color: 0x9c8a64, roughness: 0.95, envMapIntensity: 0.3 });
  const jarTwine = new THREE.Mesh(new THREE.TorusGeometry(0.509, 0.0065, 8, 72), twineMat);
  jarTwine.rotation.x = Math.PI / 2; jarTwine.position.y = 0.915;
  candle.add(jarTwine);
  for (const [ang, len] of [[0.9, 0.13], [1.05, 0.1]]) {            // two short tails hanging from the knot
    const tail = new THREE.Mesh(new THREE.CylinderGeometry(0.0045, 0.0045, len, 6), twineMat);
    tail.position.set(Math.sin(ang) * 0.512, 0.915 - len / 2, Math.cos(ang) * 0.512);
    tail.rotation.z = (ang - 1) * 0.15;
    candle.add(tail);
  }

  const cinnamonMat = new THREE.MeshStandardMaterial({ color: 0x8a4b22, roughness: 0.85, bumpMap: noiseTexture(128, 110), bumpScale: 1.2, envMapIntensity: 0.3 });
  const cinnamon = new THREE.Group();
  [[0, 0.04, -0.04, 0.56], [0, 0.04, 0.04, 0.53], [0, 0.115, 0, 0.5]].forEach(([x, y, z, len]) => {
    const stick = new THREE.Mesh(new THREE.CylinderGeometry(0.036, 0.04, len, 12), cinnamonMat);
    stick.rotation.z = Math.PI / 2; stick.position.set(x, y, z);
    cinnamon.add(stick);
  });
  const bundleTwine = new THREE.Mesh(new THREE.TorusGeometry(0.075, 0.007, 8, 24), twineMat);
  bundleTwine.rotation.y = Math.PI / 2; bundleTwine.position.y = 0.07;
  cinnamon.add(bundleTwine);
  cinnamon.position.set(0.45, -0.06, 0.7); cinnamon.rotation.y = -0.9;
  candle.add(cinnamon);

  const lavender = new THREE.Group();
  const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.005, 0.006, 0.7, 6), new THREE.MeshStandardMaterial({ color: 0x6f7a4a, roughness: 0.8 }));
  stem.rotation.z = Math.PI / 2; lavender.add(stem);
  const budColors = [0x7b5ea7, 0x9a7cc4, 0x5f4890];
  for (let i = 0; i < 18; i++) {
    const bud = new THREE.Mesh(new THREE.SphereGeometry(0.017, 8, 6), new THREE.MeshStandardMaterial({ color: budColors[i % 3], roughness: 0.7 }));
    bud.scale.set(1.6, 0.9, 0.9);
    bud.position.set(0.12 + (i >> 1) * 0.025, 0.004, (i % 2 ? 1 : -1) * 0.012);
    lavender.add(bud);
  }
  lavender.position.set(-0.5, -0.05, 0.78); lavender.rotation.y = 0.55;
  candle.add(lavender);

  const petalMat = [0x8c2f3b, 0xb04a56].map(c => new THREE.MeshStandardMaterial({ color: c, roughness: 0.75, side: THREE.DoubleSide }));
  [[0.1, 0.92], [-0.25, 1.0], [0.85, 0.2], [-0.9, 0.35], [0.55, 1.05], [-0.15, 0.85], [0.95, 0.6]].forEach(([x, z], i) => {
    const petal = new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 8), petalMat[i % 2]);
    petal.scale.set(1, 0.12, 0.7); petal.position.set(x, -0.05, z); petal.rotation.y = i * 1.3;
    candle.add(petal);
  });

  candle.traverse(o => { if (o.isMesh && o !== jar && o !== ember && !o.material.isShaderMaterial) { o.castShadow = true; o.receiveShadow = true; } });
  table.receiveShadow = true;

  /* ---------- a soft light for the moment before the flame is lit, so the candle is visible in the dark ---------- */
  const softFill = new THREE.PointLight(0xffd9b0, 0, 10, 2);
  softFill.position.set(1.4, 1.6, 2.2);
  scene.add(softFill);

  /* ---------- dust floating in the candlelight: it brightens near the flame and twinkles ---------- */
  const dustCount = lite ? 70 : 150;
  const dustPos = new Float32Array(dustCount * 3), dustSeed = new Float32Array(dustCount * 2);
  for (let i = 0; i < dustCount; i++) {
    const r = 0.3 + Math.random() * 2.1, a = Math.random() * Math.PI * 2;
    dustPos.set([Math.cos(a) * r, Math.random() * 2.4, Math.sin(a) * r * 0.8], i * 3);
    dustSeed.set([Math.random(), Math.random()], i * 2);
  }
  const dustGeo = new THREE.BufferGeometry();
  dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
  dustGeo.setAttribute('aSeed', new THREE.BufferAttribute(dustSeed, 2));
  const dustMat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: { uTime: { value: 0 }, uLight: { value: new THREE.Vector3(0, 0.95, 0) }, uPx: { value: pixelRatio } },
    vertexShader: `
      attribute vec2 aSeed; uniform float uTime; uniform vec3 uLight; uniform float uPx; varying float vB;
      void main() {
        vec3 p = position;
        p.y = mod(p.y + uTime * (0.03 + aSeed.x * 0.05), 2.4);
        p.x += sin(uTime * 0.3 + aSeed.y * 6.28) * 0.12;
        p.z += cos(uTime * 0.25 + aSeed.x * 6.28) * 0.12;
        float d = distance(p, uLight);
        vB = smoothstep(2.2, 0.15, d) * (0.5 + 0.5 * sin(uTime * (0.8 + aSeed.x * 1.5) + aSeed.y * 30.0));
        vec4 mv = modelViewMatrix * vec4(p, 1.0);
        gl_PointSize = (3.0 + aSeed.x * 5.0) * uPx * (4.0 / -mv.z);
        gl_Position = projectionMatrix * mv;
      }`,
    fragmentShader: `
      varying float vB;
      void main() {
        float r = length(gl_PointCoord - 0.5);
        float a = smoothstep(0.5, 0.0, r) * vB;
        gl_FragColor = vec4(1.0, 0.78, 0.45, a);
      }`
  });
  const dust = new THREE.Points(dustGeo, dustMat);
  dust.frustumCulled = false;
  scene.add(dust);

  /* ---------- optional bloom: only the brightest things (the flame and glow) bleed light ---------- */
  let composer = null, shimmer = null;
  if (post) {
    const target = new THREE.WebGLRenderTarget(2, 2, { type: THREE.HalfFloatType, samples: 4 });
    composer = new post.EffectComposer(renderer, target);
    composer.addPass(new post.RenderPass(scene, camera));
    /* heat shimmer: the picture wobbles very slightly in a narrow column above the flame */
    shimmer = new post.ShaderPass({
      uniforms: { tDiffuse: { value: null }, uTime: { value: 0 }, uCenter: { value: new THREE.Vector2(0.5, 0.5) }, uAspect: { value: 1 }, uAmp: { value: 1 } },
      vertexShader: 'varying vec2 vUv; void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
      fragmentShader: `
        uniform sampler2D tDiffuse; uniform float uTime; uniform vec2 uCenter; uniform float uAspect; uniform float uAmp; varying vec2 vUv;
        void main() {
          vec2 d = vUv - uCenter; d.x *= uAspect;
          float m = exp(-(d.x * d.x) / 0.0016 - (d.y * d.y) / 0.02) * smoothstep(-0.02, 0.06, d.y);
          vec2 off = vec2(sin(vUv.y * 70.0 - uTime * 5.0) + sin(vUv.y * 130.0 - uTime * 7.3) * 0.5, 0.0) * 0.0016 * m * uAmp;
          gl_FragColor = texture2D(tDiffuse, vUv + off);
        }`
    });
    composer.addPass(shimmer);
    composer.addPass(new post.UnrealBloomPass(new THREE.Vector2(2, 2), 0.22, 0.55, 1.5));      // low strength, high threshold: only the flame bleeds light
    composer.addPass(new post.OutputPass());
  }

  /* ---------- smoke: a few soft puffs that rise when the flame goes out at the end of the burn ---------- */
  const smokeTex = radialTexture([[0, 'rgba(200,190,180,0.55)'], [0.5, 'rgba(160,150,140,0.2)'], [1, 'rgba(120,110,100,0)']]);
  const smoke = [0, 1, 2].map(() => {
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: smokeTex, transparent: true, depthWrite: false, opacity: 0 }));
    sp.visible = false; sp.renderOrder = 6;
    candle.add(sp);
    return sp;
  });

  /* ---------- the shelf: the same candle in a few variants, one for each slot of the products shelf ----------
     The candles hang in a group fixed to the camera, so each one can be placed exactly over its slot in the page (page.js and
     style.css keep the slots, names and order buttons; here we only draw). The candle in the middle carries the flame.
     DRAFT: colors, sizes and labels are placeholders until the client lists her real candles. */
  const SHELF_D = 4.5;                                            // distance of the shelf from the camera
  const shelfGroup = new THREE.Group();
  shelfGroup.position.z = -SHELF_D; shelfGroup.visible = false;
  camera.add(shelfGroup); scene.add(camera);
  /* the candles are built from recipe files (recipes/*.json, see candle-builder.js): a new candle is a new file, not new code.
     If the recipes cannot load, the shelf keeps the stand-in photos. */
  const builder = makeBuilder(THREE);
  const recipes = await recipesP;
  await (window.shelvesReady || Promise.resolve());                // page.js builds the shelves from products.json; wait for it
  shelfEls = [...document.querySelectorAll('.shelf')];
  shelfItems = []; shelfOf = [];
  shelfEls.forEach((s, si) => s.querySelectorAll('.shelf-item').forEach(it => { shelfItems.push(it); shelfOf.push(si); }));
  /* ---------- phones: every shelf candle is drawn INTO its own slot ----------
     A fixed canvas that is redrawn after every scroll step is always a frame or two behind the page, which scrolls on its own fast thread:
     on a weak phone the candles trail and jump. So on phones each candle gets a small canvas INSIDE its slot, which the phone scrolls together
     with the page, in both directions. A candle is drawn again only when it changes (lit or not, the flame); a second, hidden renderer does the
     drawing and the result is copied into the slot. ?slots=0 goes back to the single fixed canvas, for comparing. */
  let slotsOn = lite && qs.get('slots') !== '0', sr = null, sScene = null, sCam = null;
  if (slotsOn) {                                                    // the hidden renderer itself is made later (initSlots): making it at the start made the first seconds heavier
    sScene = new THREE.Scene();
    sScene.add(new THREE.HemisphereLight(0x6a5a4a, 0x1a0602, 0.3));
    sCam = new THREE.PerspectiveCamera(30, 1, 0.1, 50); sCam.position.set(0, 0, SHELF_D);
  }
  const slotRatio = Math.min(devicePixelRatio || 1, 1.5);

  /* a shop can have many candles, so each 3D candle is built only when its slot first comes near the screen */
  const shelfCandles = new Array(shelfItems.length).fill(null);
  const makeShelfCandle = (item, i) => {
    const c = builder.build(recipes[i % recipes.length]);
    c.g = c.group; c.el = item.querySelector('.img'); c.lit = 0;    // the slot is the picture box of the item
    c.g.visible = false; (slotsOn ? sScene : shelfGroup).add(c.g);
    c.swayAmt = 0; c.dLit = 0; c.dSway = 0; c.hadFlame = false; c.dirty = true;   // what was last drawn into the slot
    return c;
  };

  /* the one flame of the shelf moves between candles: it goes out on one and lights the next */
  const sFlame = new THREE.Mesh(flame.geometry, flameOuterMat), sCore = new THREE.Mesh(flame.geometry, flameCoreMat), sHalo = new THREE.Mesh(flame.geometry, flameHaloMat);
  sHalo.renderOrder = 3; sFlame.renderOrder = 4; sCore.renderOrder = 5;
  const sGlow = new THREE.Sprite(glow.material.clone()); sGlow.renderOrder = 5;
  const sEmber = new THREE.Mesh(ember.geometry, ember.material);
  const shelfLight = new THREE.PointLight(0xffa447, 0, 8, 2);
  const shelfFire = [sHalo, sFlame, sCore, sGlow, sEmber];
  shelfFire.forEach(m => { m.visible = false; });
  (slotsOn ? sScene : shelfGroup).add(...shelfFire, shelfLight);
  let flameAt = 0, flameAmt = 0;                                  // which candle holds the flame, and how strongly it burns
  const hideShelf = () => { shelfGroup.visible = false; return { amt: 0, x: 0, y: 0 }; };
  /* makes the hidden renderer: a few seconds after the page has opened (idle time), or at once if the visitor reaches the shelf sooner */
  /* It is done in two small steps (the graphics context, then the reflections it needs), each in a quiet moment, so no single step freezes the page. */
  const slotsReady = () => !slotsOn || !!(sr && sScene.environment);
  const initSlotsStep = () => {
    if (slotsReady()) return;
    try {
      if (!sr) {
        sr = new THREE.WebGLRenderer({ antialias: true, alpha: true, premultipliedAlpha: true, powerPreference: 'high-performance' });
        sr.toneMapping = THREE.ACESFilmicToneMapping; sr.toneMappingExposure = 1.05; sr.setPixelRatio(1);
      } else sScene.environment = new THREE.PMREMGenerator(sr).fromScene(studio, 0.02).texture;
    } catch (e) {                                                   // no second graphics context: go back to the single fixed canvas
      console.warn('slot drawing off:', e); slotsOn = false; sr = null;
      shelfGroup.add(...shelfFire, shelfLight);
    }
  };
  const initSlots = () => { while (!slotsReady()) initSlotsStep(); };          // all at once: the visitor reached the shelf before the quiet steps were done

  /* the slot's own canvas: bigger than the slot, so the flame's glow has room (it is only a picture; taps pass through to the slot) */
  const SLOT_PAD = { x: 0.3, top: 0.4, bottom: 0.14 };               // fractions of the slot's size
  const ensureCanvas = c => {
    const w = c.el.offsetWidth, h = c.el.offsetHeight;
    if (!w || !h) return false;
    if (c.cv && c.cw === w && c.ch === h) return true;
    c.cw = w; c.ch = h;
    const px = Math.round(w * SLOT_PAD.x), pt = Math.round(h * SLOT_PAD.top), pb = Math.round(h * SLOT_PAD.bottom);
    c.pad = [px, pt, pb];
    if (!c.cv) { c.cv = document.createElement('canvas'); c.cv.className = 'slot3d'; c.cv.setAttribute('aria-hidden', 'true'); c.el.append(c.cv); c.ctx = c.cv.getContext('2d'); }
    const cssW = w + 2 * px, cssH = h + pt + pb;
    c.cv.style.cssText = `left:${-px}px;top:${-pt}px;width:${cssW}px;height:${cssH}px`;
    c.cv.width = Math.round(cssW * slotRatio); c.cv.height = Math.round(cssH * slotRatio);
    c.dirty = true;
    return true;
  };
  /* draws one candle (alone in the small scene) and copies the picture into its slot */
  const drawSlot = (c, i, t, flick, isFlame, fAmt) => {
    const [px, pt, pb] = c.pad, cssW = c.cw + 2 * px, cssH = c.ch + pt + pb, W = c.cv.width, H = c.cv.height;
    if (sr.domElement.width !== W || sr.domElement.height !== H) { sr.setSize(W, H, false); sCam.aspect = W / H; sCam.updateProjectionMatrix(); }
    const ppu = cssH / (2 * Math.tan(Math.PI / 12) * SHELF_D);        // css pixels per world unit at the candle's distance
    const sc = c.ch * 0.74 / ppu * (0.9 + 0.1 * c.lit) * c.size;       // the candle is 1 unit tall: this is its height in world units
    c.g.visible = true; c.g.scale.setScalar(sc);
    c.g.position.set(0, (cssH / 2 - (pt + c.ch + 4 - 10 * c.lit)) / ppu, 0);   // sits a little below the slot (on the shelf), lifted when lit
    c.g.rotation.y = c.turn + (reduce ? 0 : Math.sin(t * 0.4 + i) * 0.25 * c.swayAmt);
    const dim = 0.62 + 0.38 * c.lit;
    c.tints.forEach(({ m, base }) => m.color.copy(base).multiplyScalar(dim));
    const lightUp = isFlame ? (1 + flick * 1.6) * fAmt : 0;
    c.glows.forEach(({ m, k: gk }) => { m.emissiveIntensity = gk * lightUp; });
    shelfFire.forEach(m => { m.visible = isFlame; });
    if (isFlame) {
      const L = fAmt, fs = c.info.fs, fw = c.info.fw;
      const fx = (c.info.flameX || 0) * sc, fy = c.g.position.y + c.info.wickY * sc;
      sHalo.position.set(fx, fy - 0.005 * sc, 0); sFlame.position.copy(sHalo.position); sCore.position.copy(sHalo.position);
      sFlame.scale.set(0.9 * L * sc * fs * fw, 0.9 * L * sc * fs * (1 + flick * 0.5), 0.9 * L * sc * fs);
      sCore.scale.set(0.5 * L * sc * fs * fw, 0.5 * L * sc * fs * (1 + flick * 0.6), 0.5 * L * sc * fs);
      sHalo.scale.set(1.5 * L * sc * fs * fw, 1.15 * L * sc * fs * (1 + flick * 0.4), 1.5 * L * sc * fs);
      sGlow.position.set(fx, fy + 0.12 * sc, 0); sGlow.scale.setScalar(1.05 * sc * fs);
      sGlow.material.opacity = (0.9 + flick) * L;
      sEmber.position.set(fx + 0.0055 * sc, fy, 0); sEmber.scale.setScalar(L * sc);
      shelfLight.position.set(fx, fy + 0.4 * sc, 0.3 * sc);
    }
    shelfLight.intensity = isFlame ? FLAME_LIGHT * (1 + flick * 1.2) * fAmt : 0;
    sr.render(sScene, sCam);
    c.ctx.clearRect(0, 0, W, H); c.ctx.drawImage(sr.domElement, 0, 0);
    c.g.visible = false;
    c.dirty = false; c.dLit = c.lit; c.dSway = c.swayAmt; c.hadFlame = isFlame;
    const shelfEl = shelfEls[shelfOf[i]];
    if (!shelfEl.classList.contains('is3d')) shelfEl.classList.add('is3d');       // the stand-in photos step aside once a candle is really there
  };
  /* phones: decides which slots need drawing again. A candle that did not change costs nothing, so scrolling only moves the page. */
  function layoutSlots(t, flick, k) {
    if (!slotsReady()) { initSlots(); if (!slotsOn) return layoutShelf(t, flick, k); }
    const vw = lastW || innerWidth, vh = lastH || innerHeight;
    const active = shelfItems.findIndex(el => el.classList.contains('is-focus'));   // the lit candle of the shelf nearest the middle carries the flame
    if (reduce) { if (active >= 0) flameAt = active; flameAmt = active >= 0 ? 1 : 0; }
    else {
      if (flameAmt < 0.08 && active >= 0 && active !== flameAt) flameAt = active;
      flameAmt = clamp(flameAmt + ((active === flameAt ? 1 : 0) - flameAmt) * k * 1.2);
    }
    let budget = 3, out = { amt: 0, x: 0, y: 0 };                    // at most three quiet candles per frame; the flame candle is always drawn
    shelfItems.forEach((item, i) => {
      const r = item.getBoundingClientRect();
      if (!(r.bottom > -vh * 0.6 && r.top < vh * 1.6 && r.right > -vw * 0.6 && r.left < vw * 1.6)) return;   // far from the screen: nothing to draw
      let c = shelfCandles[i];
      if (!c) c = shelfCandles[i] = makeShelfCandle(item, i);
      if (!ensureCanvas(c)) return;
      c.lit += ((item.classList.contains('is-active') ? 1 : 0) - c.lit) * (reduce ? 1 : k);
      const isFlame = i === flameAt && flameAmt > 0.01;
      c.swayAmt += ((isFlame ? c.lit : 0) - c.swayAmt) * (reduce ? 1 : k);      // only the candle with the flame sways, and it eases in and out
      const changed = c.dirty || isFlame || c.hadFlame !== isFlame || Math.abs(c.lit - c.dLit) > 0.004 || Math.abs(c.swayAmt - c.dSway) > 0.004;
      if (changed && (isFlame || budget-- > 0)) drawSlot(c, i, t, flick, isFlame, flameAmt);
      if (isFlame) {                                                  // where the flame is on screen, for the warm light of the page
        const px = c.ch * 0.74 * (0.9 + 0.1 * c.lit) * c.size, rr = c.el.getBoundingClientRect();
        out = { amt: flameAmt, x: rr.left + rr.width / 2 + (c.info.flameX || 0) * px, y: rr.bottom + 4 - 10 * c.lit - (c.info.wickY + 0.1) * px };
      }
    });
    return out;
  }

  /* places every candle over its slot, and the flame on the lit one. Returns where the flame is on screen, for the room's light. */
  function layoutShelf(t, flick, k) {
    const vw = lastW || innerWidth, vh = lastH || innerHeight;    // the canvas size, which stays constant (the window's height changes with the browser bar)
    const ppu = vh / (2 * Math.tan(Math.PI / 12) * SHELF_D);       // pixels per world unit at the shelf's distance (the field of view is 30 degrees)
    /* every shelf lights its own centred candle, but there is only one flame: it belongs to the shelf nearest the middle of the screen */
    const sRects = shelfEls.map(s => s.getBoundingClientRect());
    const active = shelfItems.findIndex(el => el.classList.contains('is-focus'));   // page.js marks the selected candle: the lit one of the shelf nearest the middle
    if (reduce) { if (active >= 0) flameAt = active; flameAmt = active >= 0 ? 1 : 0; }
    else {
      if (flameAmt < 0.08 && active >= 0 && active !== flameAt) flameAt = active;
      flameAmt = clamp(flameAmt + ((active === flameAt ? 1 : 0) - flameAmt) * k * 1.2);
    }
    shelfGroup.visible = true;
    shelfItems.forEach((item, i) => {
      let c = shelfCandles[i];
      const sr = sRects[shelfOf[i]];
      if (sr.bottom < -vh * 0.5 || sr.top > vh * 1.5) { if (c) c.g.visible = false; return; }   // a far shelf: nothing to read or draw
      const r = (c ? c.el : item.querySelector('.img')).getBoundingClientRect();
      if (!c) {
        if (!(r.right > -vw * 0.5 && r.left < vw * 1.5)) return;    // not near yet
        c = shelfCandles[i] = makeShelfCandle(item, i);
      }
      c.g.visible = r.right > -80 && r.left < vw + 80 && r.bottom > -40 && r.top < vh + 40;
      if (!c.g.visible) return;
      c.lit += ((item.classList.contains('is-active') ? 1 : 0) - c.lit) * (reduce ? 1 : k);
      c.g.scale.setScalar(r.height * 0.74 / ppu * (0.9 + 0.1 * c.lit) * c.size);
      c.g.position.set((r.left + r.width / 2 - vw / 2) / ppu, (vh / 2 - (r.bottom + 4 - 10 * c.lit)) / ppu, 0);   // lifted a little when lit
      c.g.rotation.y = c.turn + (reduce ? 0 : Math.sin(t * 0.4 + i) * 0.25 * c.lit);
      const dim = 0.62 + 0.38 * c.lit;                                // the unlit ones are dimmer
      c.tints.forEach(({ m, base }) => m.color.copy(base).multiplyScalar(dim));
      const lightUp = i === flameAt ? (1 + flick * 1.6) * flameAmt : 0;
      c.glows.forEach(({ m, k: gk }) => { m.emissiveIntensity = gk * lightUp; });
    });
    const c = shelfCandles[flameAt];
    const on = !!c && c.g.visible && flameAmt > 0.01;
    shelfFire.forEach(m => { m.visible = on; });
    let x = 0, y = 0;
    if (on) {
      const L = flameAmt, sw = c.g.scale.x, sh = c.g.scale.y, fs = c.info.fs, fw = c.info.fw;
      const fx = c.g.position.x + (c.info.flameX || 0) * sw, fy = c.g.position.y + c.info.wickY * sh;   // the tip of the wick
      sHalo.position.set(fx, fy - 0.005 * sh, 0); sFlame.position.copy(sHalo.position); sCore.position.copy(sHalo.position);
      sFlame.scale.set(0.9 * L * sw * fs * fw, 0.9 * L * sh * fs * (1 + flick * 0.5), 0.9 * L * sw * fs);
      sCore.scale.set(0.5 * L * sw * fs * fw, 0.5 * L * sh * fs * (1 + flick * 0.6), 0.5 * L * sw * fs);
      sHalo.scale.set(1.5 * L * sw * fs * fw, 1.15 * L * sh * fs * (1 + flick * 0.4), 1.5 * L * sw * fs);
      sGlow.position.set(fx, fy + 0.12 * sh, 0); sGlow.scale.setScalar(1.05 * sw * fs);
      sGlow.material.opacity = ((composer ? 0.4 : 0.9) + flick) * L;
      sEmber.position.set(fx + 0.0055 * sw, fy, 0); sEmber.scale.setScalar(L * sw);
      shelfLight.position.set(fx, fy + 0.4 * sh, 0.3 * sw);
      x = vw / 2 + fx * ppu; y = vh / 2 - (fy + 0.1 * sh) * ppu;
    }
    shelfLight.intensity = on ? FLAME_LIGHT * (1 + flick * 1.2) * flameAmt : 0;
    return { amt: on ? flameAmt : 0, x, y };
  }

  /* ---------- size, pointer, layout ---------- */
  let aspect = 1, productsTop = Infinity, productsBottom = Infinity, aboutTop = Infinity;
  let frameNo = 0;                                                // counts frames; the first few are always drawn (also after a resize)
  const readLayout = () => {
    productsTop = productsEl ? productsEl.getBoundingClientRect().top + scrollY : Infinity;     // the page position where the products section starts
    productsBottom = productsEl ? productsEl.getBoundingClientRect().bottom + scrollY : Infinity;
    aboutTop = aboutEl ? aboutEl.getBoundingClientRect().top + scrollY : Infinity;              // where About starts: the candle burns down behind it
  };
  let lastW = 0, lastH = 0;                                        // the canvas is as tall as the LARGEST window (100lvh in the CSS), so the phone's browser bar sliding in and out never resizes it
  function resize() {
    readLayout();
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (!w || !h) return;                                         // the page is not laid out yet (or the window is hidden): wait for the next resize
    if (w === lastW && h === lastH) return;                       // same size: nothing to do (setSize would clear the picture and make it flash)
    lastW = w; lastH = h;
    renderer.setSize(w, h, false);
    if (composer) { composer.setPixelRatio(pixelRatio); composer.setSize(w, h); }
    aspect = w / h; frameNo = 0;                                  // resizing clears the canvas: draw again
    camera.aspect = aspect; camera.updateProjectionMatrix();
  }
  addEventListener('resize', resize); resize();
  new ResizeObserver(resize).observe(canvas);                      // also covers a canvas that had no size when it was created
  new ResizeObserver(readLayout).observe(document.body);          // sections above the products can change height

  const pointer = { x: 0, y: 0 };
  if (!lite) addEventListener('pointermove', e => { pointer.x = e.clientX / innerWidth - 0.5; pointer.y = e.clientY / innerHeight - 0.5; }, { passive: true });

  /* ---------- the frame loop ----------
     The candle is the page's fixed background and its life is the scroll:
     it appears and lights itself in the hero -> turns while you scroll the hero -> slides to the side and burns down
     behind the page -> the flame goes out -> it fades away as the products arrive (and we stop drawing). */
  /* ?perf in the address shows a small readout (frames per second, draw calls) so a real phone can be measured */
  let perf = null;
  if (/[?&]perf/.test(location.search)) {
    const el = document.createElement('pre');
    el.style.cssText = 'position:fixed;z-index:99;top:4.2rem;left:.5rem;margin:0;padding:.4rem .6rem;font:12px/1.4 ui-monospace,monospace;color:#9f9;background:rgba(0,0,0,.72);border-radius:6px;pointer-events:none;direction:ltr;white-space:pre';
    document.body.append(el);
    let n = 0, t0 = performance.now(), last = t0, worst = 0, firstFrame = 0, early = 0, earlyAt = 0, earlyN = 0;
    perf = () => {
      const now = performance.now(); worst = Math.max(worst, now - last);
      if (!firstFrame) firstFrame = now; else if (now < 8000) { if (now - last > early) { early = now - last; earlyAt = now; } earlyN++; }   // the first 8 seconds after the page opened: where the load lag lives
      last = now; n++;
      if (now - t0 < 1000) return;
      const i = renderer.info;
      el.textContent = `LOAD first ${Math.round(firstFrame)}  worst ${Math.round(early)} ms at ${Math.round(earlyAt)}  n ${earlyN}
fps ${Math.round(n * 1000 / (now - t0))}   slowest frame ${Math.round(worst)} ms
calls ${i.render.calls}   triangles ${i.render.triangles}
textures ${i.memory.textures}   geometries ${i.memory.geometries}
lite ${lite}   pixel ratio ${pixelRatio}   canvas ${renderer.domElement.width}x${renderer.domElement.height}
cpu per frame ${jsN ? (jsSum / jsN).toFixed(1) : '-'} ms
shelf candles built ${shelfCandles.filter(Boolean).length} of ${shelfItems.length}`;
      n = 0; t0 = now; worst = 0; jsSum = 0; jsN = 0;
    };
  }
  const clock = new THREE.Clock();
  const flameTop = new THREE.Vector3();
  let cur = 0, burn = 0, side = 0;                                // smoothed: the hero turn, the burn-down, the slide to the side
  let drewGone = false;                                           // the big canvas has been drawn once with the hero candle gone
  let shelfDrawn = false;                                         // true while the shelf candles were in the last drawn picture
  let igniteAt = null;                                            // when the flame starts to light (a moment after the first frame)
  /* phones: draw 30 frames a second while only the flame moves (60 while the visitor scrolls or touches), and step the resolution down if frames take too long */
  let lastActive = performance.now(), idleTick = 0, lastExec = 0, ema = 16, slow = 0, step = 0, applyRatio = false, jsSum = 0, jsN = 0;
  const RATIOS = lite ? [pixelRatio, 1.25, 1, 0.8].filter((r, i, a) => i === 0 || r < a[i - 1]) : [pixelRatio];
  const wake = () => { lastActive = performance.now(); };
  ['scroll', 'touchstart', 'touchmove', 'pointerdown', 'keydown', 'wheel', 'resize'].forEach(ev => addEventListener(ev, wake, { passive: true, capture: true }));
  function frame() {
    requestAnimationFrame(frame);
    const frameStart = performance.now(), idleFor = frameStart - lastActive;
    if (lite && !reduce && idleFor > 600 && (idleTick++ & 1)) return;
    if (applyRatio) {                                             // a lower resolution is applied here, right before drawing, so there is no blank frame
      applyRatio = false; renderer.setPixelRatio(pixelRatio); renderer.setSize(lastW, lastH, false);
      dustMat.uniforms.uPx.value = pixelRatio; if (composer) composer.setPixelRatio(pixelRatio);
    }
    const dt = Math.min(clock.getDelta(), 0.05), t = clock.elapsedTime;
    const y = scrollY, vh = lastH || innerHeight;                  // a steady height for every scroll position, so the scene does not jitter when the browser bar moves

    /* once the products section has arrived the candle has faded out: stop drawing to save battery */
    const rest = isFinite(productsTop) ? band(y, productsTop - 0.45 * vh, productsTop + 0.05 * vh) : 0;   // 0..1: the products have arrived and the shelf takes over
    const nearShelf = shelfItems.length > 0 && recipes.length > 0 && y + vh > productsTop && y < productsBottom;
    if (frameNo++ > 3 && !nearShelf && y >= productsBottom && !shelfDrawn) return;   // below the products nothing moves: keep the last picture
    shelfDrawn = nearShelf;

    /* the hero turn uses the hero's scroll; the burn uses everything between the hero and the products */
    const heroTop = hero.getBoundingClientRect().top + y;
    const scrolled = y - heroTop;
    const heroDist = Math.max(hero.offsetHeight - vh, 1);
    const heroEnd = heroTop + heroDist;                           // the page position where the hero ends
    const target = clamp(scrolled / heroDist);
    const burnStart = isFinite(aboutTop) ? Math.max(heroEnd + 0.3 * vh, aboutTop - 0.5 * vh) : heroEnd + 0.3 * vh;
    const burnEnd = isFinite(productsTop) ? productsTop - 0.5 * vh : burnStart + 4 * vh;
    const burnTarget = clamp((y - burnStart) / Math.max(burnEnd - burnStart, 1));
    const sideTarget = clamp((y - (heroEnd - 0.05 * vh)) / (0.6 * vh));
    const k = 1 - Math.exp(-dt * (lite ? 12 : 6));
    cur = reduce ? target : cur + (target - cur) * k;
    burn = reduce ? burnTarget : burn + (burnTarget - burn) * k * 0.6;     // slower, so the burn feels gradual
    side = reduce ? sideTarget : side + (sideTarget - side) * k;
    const e = smooth(cur);

    /* the candle appears dark, then its flame lights itself */
    if (igniteAt === null) igniteAt = t + 0.9;
    const ignite = reduce ? 1 : band(t, igniteAt, igniteAt + 2.8);

    /* the burn: the wax level drops, the wick burns down with it, and near the end the flame goes out */
    const fillBurn = 1 - 0.86 * burn;
    const burnOut = band(burn, 0.82, 0.93);
    const litAll = ignite * (1 - burnOut);

    const wide = aspect >= 1.15;
    const fit = aspect < 0.8 ? 1.5 : aspect < 1.2 ? 1.2 : 1;      // keep the candle in frame on tall phone screens
    const sway = reduce ? 0 : Math.sin(t * 0.35) * 0.06;           // the scene never sits perfectly still
    const zoomOut = 1 + (wide ? 0.1 : 0.22) * side;               // after the hero the candle steps back and becomes a background
    const camZ = lerp(4.6, 3.5, e) * fit * zoomOut;
    camera.position.set(pointer.x * 0.35 + sway, lerp(1.35, 0.95, e) - pointer.y * 0.15, camZ);
    camera.lookAt(0, lerp(0.64, 0.78, e), 0);                      // looking above the candle keeps it low in the frame, clear of the headline
    const halfW = Math.tan(Math.PI / 12) * camZ * aspect;          // half of the visible width at the candle (the field of view is 30 degrees)
    const sideX = wide ? -halfW * 0.5 : 0;                         // wide screens: the candle takes the left half of the page and the text the right half
    const gone = band(rest, 0.1, 0.8);                             // the burnt-out candle sinks away as the shelf arrives
    const lift = wide ? 0 : 0.6 * side * (1 - gone);               // phones: the candle rises clear of the About text, so the text sits on dark
    const cx = sideX * side, cy = -0.5 * gone + lift, cs = Math.max((1 - gone) * (wide ? 1 : 1 - 0.18 * side), 0.001);
    candle.position.set(cx, cy, 0); candle.scale.setScalar(cs);
    table.position.set(cx, -0.06 + cy, 0); table.scale.setScalar(cs);
    shadow.position.set(cx, 0.002 + cy, 0); shadow.scale.setScalar(cs);
    pool.position.set(cx, 0.004 + cy, 0); pool.scale.setScalar(cs);
    dust.position.set(cx, cy, 0);
    candle.visible = table.visible = shadow.visible = gone < 0.98; dust.visible = gone < 0.5;
    candle.rotation.y = 0.4 + e * Math.PI * 1.6 + side * 0.5 + burn * 0.9 + (reduce ? 0 : Math.sin(t * 0.25) * 0.07);

    /* where the top of the wick is: it burns down with the wax */
    const waxTopBurn = 0.075 + 0.547 * fillBurn;
    const wickTop = Math.min(0.8, waxTopBurn + 0.18);

    const flick = reduce ? 0 : Math.sin(t * 9) * 0.05 + Math.sin(t * 23.7) * 0.03 + Math.sin(t * 37) * 0.02;
    const gust = reduce ? 0 : Math.pow(Math.max(0, Math.sin(t * 0.6) * Math.sin(t * 1.7 + 1)), 2) * 0.06;   // now and then a little draft bends the flame
    const lean = gust + (reduce ? 0 : Math.sin(t * 3.1) * 0.004);
    for (const m of [flameOuterMat, flameCoreMat, flameHaloMat]) { m.uniforms.uTime.value = t; m.uniforms.uFlicker.value = 1 + flick * 1.5 + gust * 3; m.uniforms.uLean.value = lean; }
    flame.position.y = flameCore.position.y = flameHalo.position.y = wickTop - 0.005;
    glow.position.y = wickTop + 0.12;
    ember.position.y = wickTop;
    flameLight.position.set(cx + lean * 0.6 * cs, cy + (wickTop + (post ? 0.45 : 0.1)) * cs, 0);
    if (post) flameLight.target.position.set(cx, cy, 0);
    dustMat.uniforms.uTime.value = t;
    dustMat.uniforms.uLight.value.y = wickTop + 0.15;
    if (shimmer) {
      camera.updateMatrixWorld();
      flameTop.set(cx, cy + (wickTop + 0.13) * cs, 0).project(camera);
      shimmer.uniforms.uCenter.value.set(flameTop.x * 0.5 + 0.5, flameTop.y * 0.5 + 0.5);
      shimmer.uniforms.uAspect.value = aspect;
      shimmer.uniforms.uTime.value = t;
      shimmer.uniforms.uAmp.value = litAll;                       // no heat above a flame that is not lit
    }
    const L = Math.max(litAll, 0.0001);                            // the flame grows from nothing when it lights, and shrinks to nothing when it goes out
    flame.visible = flameCore.visible = flameHalo.visible = litAll > 0.01;
    ember.visible = glow.visible = litAll > 0.01;
    ember.scale.setScalar(L);
    flame.scale.set(0.9 * L, 0.9 * L * (1 + flick * 0.5), 0.9 * L);
    flameCore.scale.set(0.5 * L, 0.5 * L * (1 + flick * 0.6), 0.5 * L);
    flameHalo.scale.set(1.5 * L, 1.15 * L * (1 + flick * 0.4), 1.5 * L);
    waxMat.emissiveIntensity = (post ? 0.22 : 0.6) * (1 + flick * 1.6) * litAll;   // the wax glow flickers with the flame (softer on desktop, where the glass adds brightness)
    flameLight.intensity = FLAME_LIGHT * (1 + flick * 1.2) * litAll;
    pool.material.opacity = (0.75 + flick * 1.2) * litAll * (1 - gone);              // the light the flame throws on the table
    softFill.intensity = 3.5 * (1 - ignite);                       // while the flame is not lit yet, a soft light keeps the candle visible
    glow.material.opacity = ((composer ? 0.4 : 0.9) + flick) * litAll;

    /* the wax sinks and the wick burns down as the candle burns */
    wax.visible = fillBurn > 0.003;
    wax.scale.y = Math.max(fillBurn, 0.003); wax.position.y = 0.075 * (1 - fillBurn);
    const wickS = Math.max((wickTop - 0.07) / 0.73, 0.003);
    wick.scale.y = wickS; wick.position.y = 0.07 + 0.365 * wickS;

    /* the wisp of smoke as the flame goes out */
    const smokeT = clamp((burn - 0.88) / 0.12);
    smoke.forEach((sp, i) => {
      sp.visible = smokeT > 0 && smokeT < 1;
      if (!sp.visible) return;
      sp.material.opacity = band(smokeT, 0, 0.2) * (1 - band(smokeT, 0.6, 1)) * 0.5;
      sp.position.set(Math.sin(t * 1.3 + i * 2.1) * (0.03 + smokeT * 0.1), wickTop + 0.1 + smokeT * (0.7 + i * 0.25) + i * 0.05, 0);
      sp.scale.setScalar(0.1 + smokeT * (0.3 + i * 0.08));
    });

    /* the candle's light on the page: a warm glow centred on the flame (a CSS layer reads these three values) */
    const sh = nearShelf ? (slotsOn ? layoutSlots(t, flick, reduce ? 1 : k) : layoutShelf(t, flick, reduce ? 1 : k)) : hideShelf();   // on the shelf the light follows the lit candle
    camera.updateMatrixWorld();
    flameTop.set(cx, cy + (wickTop + 0.1) * cs, 0).project(camera);
    const root = lightEl.style;                                     // only the light layer restyles, not the whole page
    const onShelf = sh.amt > 0.01;
    root.setProperty('--lx', (onShelf ? sh.x : (flameTop.x * 0.5 + 0.5) * lastW).toFixed(0) + 'px');
    root.setProperty('--ly', (onShelf ? sh.y : (-flameTop.y * 0.5 + 0.5) * lastH).toFixed(0) + 'px');
    root.setProperty('--li', Math.max(0, (onShelf ? sh.amt : litAll) * (0.85 + flick * 2.2)).toFixed(3));

    copyA.style.opacity = (1 - band(cur, 0.22, 0.42)).toFixed(3);
    if (cue) cue.style.opacity = (1 - band(cur, 0.03, 0.2)).toFixed(3);       // the scroll cue goes as soon as the visitor scrolls
    copyB.style.opacity = (band(cur, 0.5, 0.68) * (1 - band(cur, 0.9, 1))).toFixed(3);

    /* behind the content the candle is a little dimmer (more on phones), and at rest it is dim */
    canvas.style.opacity = lerp(lerp(1, wide ? 0.95 : 0.55, side), 1, rest).toFixed(3);

    /* with slots, once the hero candle has gone the big canvas shows only the dark room: draw that once, then leave it alone (half the work on a phone) */
    const skipMain = slotsOn && nearShelf && gone > 0.98;
    if (!skipMain || !drewGone) { if (composer) composer.render(); else renderer.render(scene, camera); }
    drewGone = skipMain;
    jsSum += performance.now() - frameStart; jsN++;
    if (lite && lastExec && idleFor < 400) {                      // while the visitor scrolls: too many slow frames in a row means too many pixels
      ema = ema * 0.9 + (frameStart - lastExec) * 0.1;
      slow = ema > 28 ? slow + 1 : 0;
      if (slow > 40 && step < RATIOS.length - 1) { step++; slow = 0; ema = 16; pixelRatio = RATIOS[step]; applyRatio = true; }
    }
    lastExec = frameStart;
    if (perf) perf();
    if (stage.classList.contains('no3d')) { stage.classList.remove('no3d'); document.documentElement.classList.remove('no3d'); }   // 3D started after the timeout: use it
    if (recipes.length && !slotsOn) shelfEls.forEach(s => s.classList.add('is3d'));                   // the shelf candles are drawn: the stand-in photos step aside
    stage.classList.add('ready'); bg.classList.add('ready');       // fades the scene in after the first drawn frame
  }
  /* the shelf candles are built ahead of time, one at a time while the phone is idle, so scrolling to a new candle does not stall */
  const idle = window.requestIdleCallback ? fn => requestIdleCallback(fn) : fn => setTimeout(fn, 250);
  /* A new candle is slow to show for the first time not because of building it but because the graphics chip has to compile its materials and
     receive its textures. That is done here ahead of time, but in SMALL pieces (one texture, or one material, per quiet moment): on a weak phone
     doing a whole candle at once froze the page for over half a second (measured on a real phone). Nothing runs while the visitor is scrolling. */
  const tasks = [];
  const prepare = c => {
    const seen = new Set();
    c.g.traverse(o => {
      if (o.material) tasks.push(() => (slotsOn ? sr : renderer).compileAsync(o, slotsOn ? sCam : camera, slotsOn ? sScene : scene).catch(() => {}));      // one material at a time
      [].concat(o.material || []).forEach(m => {
        for (const k in m) { const v = m[k]; if (v && v.isTexture && !seen.has(v)) { seen.add(v); tasks.push(() => (slotsOn ? sr : renderer).initTexture(v)); } }
      });
    });
  };
  const warm = () => {
    if (performance.now() - lastActive < 400) return setTimeout(() => idle(warm), 400);   // the visitor is moving: wait
    if (!slotsReady()) initSlotsStep();                           // first the hidden renderer, in its small steps
    else if (tasks.length) tasks.shift()();
    else {
      const i = recipes.length ? shelfCandles.findIndex(c => !c) : -1;
      if (i < 0) return;
      prepare(shelfCandles[i] = makeShelfCandle(shelfItems[i], i));
    }
    setTimeout(() => idle(warm), slotsReady() ? 60 : 250);
  };
  if (qs.get('w') !== '0') setTimeout(() => idle(warm), slotsOn ? 4500 : 1500);    // after the hero has started (?w=0 turns the pre-build off, for measuring)

  /* ---------- the live preview in the detail sheet ----------
     The pressed candle, lit, drawn with the buyer's choices (colour, name on the label, size). It is drawn by a hidden renderer (on phones the
     one the shelf slots already use) and copied into a small canvas of the sheet. page.js builds the controls and calls these. */
  let pv = null;
  const getPv = () => {
    if (pv) return pv;
    if (slotsOn) initSlots();
    let r, env;
    if (slotsOn && sr) { r = sr; env = sScene.environment; }
    else {
      r = new THREE.WebGLRenderer({ antialias: true, alpha: true, premultipliedAlpha: true });
      r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = 1.05; r.setPixelRatio(1);
      env = new THREE.PMREMGenerator(r).fromScene(studio, 0.02).texture;
    }
    const scene = new THREE.Scene(); scene.environment = env;
    scene.add(new THREE.HemisphereLight(0x6a5a4a, 0x1a0602, 0.3));
    const cam = new THREE.PerspectiveCamera(30, 1, 0.1, 50); cam.position.set(0, 0.8, 3.8); cam.lookAt(0, 0.52, 0);
    const fh = new THREE.Mesh(flame.geometry, flameHaloMat), fo = new THREE.Mesh(flame.geometry, flameOuterMat), fc = new THREE.Mesh(flame.geometry, flameCoreMat);
    fh.renderOrder = 3; fo.renderOrder = 4; fc.renderOrder = 5;
    const fg = new THREE.Sprite(glow.material.clone()); fg.renderOrder = 5;
    const fe = new THREE.Mesh(ember.geometry, ember.material);
    const light = new THREE.PointLight(0xffa447, 0, 8, 2);
    scene.add(fh, fo, fc, fg, fe, light);
    return (pv = { r, scene, cam, fh, fo, fc, fg, fe, light });
  };
  const SIZES = { s: 0.8, m: 1, l: 1.2 };
  const cp = { k: -1, canvas: null, ctx: null, opts: {}, c: null, raf: 0, last: 0, rot: 0, drag: null };
  const dropPreviewCandle = () => { if (cp.c && pv) { pv.scene.remove(cp.c.group); cp.c.dispose(); } cp.c = null; };
  const buildPreviewCandle = () => {
    const p = getPv(); dropPreviewCandle();
    cp.c = builder.build(customize(recipes[cp.k % recipes.length], cp.opts), true);       // fresh: its textures are freed when the buyer changes the choice
    p.scene.add(cp.c.group);
  };
  const drawPreview = ts => {
    cp.raf = requestAnimationFrame(drawPreview);
    if (ts - cp.last < 32) return; cp.last = ts;                                 // 30 pictures a second are enough
    const p = pv, c = cp.c; if (!p || !c || !cp.canvas.isConnected) return;
    const W = cp.canvas.width, H = cp.canvas.height; if (!W || !H) return;
    if (p.r.domElement.width !== W || p.r.domElement.height !== H) { p.r.setSize(W, H, false); p.cam.aspect = W / H; p.cam.updateProjectionMatrix(); }
    const t = clock.elapsedTime, flick = reduce ? 0 : Math.sin(t * 9) * 0.05 + Math.sin(t * 23.7) * 0.03 + Math.sin(t * 37) * 0.02;
    const sc = (SIZES[cp.opts.size] || 1) * c.size;
    c.group.scale.setScalar(sc);
    c.group.rotation.y = c.turn + cp.rot + (reduce || cp.drag ? 0 : Math.sin(t * 0.5) * 0.35);
    c.glows.forEach(({ m, k }) => { m.emissiveIntensity = k * (1 + flick * 1.6); });
    const fx = (c.info.flameX || 0) * sc, fy = c.info.wickY * sc, fs = c.info.fs, fw = c.info.fw;
    p.fh.position.set(fx, fy - 0.005 * sc, 0); p.fo.position.copy(p.fh.position); p.fc.position.copy(p.fh.position);
    p.fo.scale.set(0.9 * sc * fs * fw, 0.9 * sc * fs * (1 + flick * 0.5), 0.9 * sc * fs);
    p.fc.scale.set(0.5 * sc * fs * fw, 0.5 * sc * fs * (1 + flick * 0.6), 0.5 * sc * fs);
    p.fh.scale.set(1.5 * sc * fs * fw, 1.15 * sc * fs * (1 + flick * 0.4), 1.5 * sc * fs);
    p.fg.position.set(fx, fy + 0.12 * sc, 0); p.fg.scale.setScalar(1.05 * sc * fs); p.fg.material.opacity = (0.9 + flick);
    p.fe.position.set(fx + 0.0055 * sc, fy, 0); p.fe.scale.setScalar(sc);
    p.light.position.set(fx, fy + 0.4 * sc, 0.3 * sc); p.light.intensity = FLAME_LIGHT * (1 + flick * 1.2);
    p.r.render(p.scene, p.cam);
    cp.ctx.clearRect(0, 0, W, H); cp.ctx.drawImage(p.r.domElement, 0, 0);
  };
  window.candlePreview = {
    config(k) {                                                                  // what this candle lets the buyer change (null: not ready, or nothing)
      if (!recipes.length) return null;
      const cu = recipes[k % recipes.length].custom || {};
      return { color: !!cu.color, name: !!cu.name };
    },
    show(k, canvas) {
      this.hide();
      cp.k = k; cp.canvas = canvas; cp.ctx = canvas.getContext('2d'); cp.opts = {}; cp.rot = 0;
      const box = canvas.getBoundingClientRect(), ratio = Math.min(devicePixelRatio || 1, 1.5);
      canvas.width = Math.round(box.width * ratio); canvas.height = Math.round(box.height * ratio);
      let lastX = 0;                                                             // drag sideways to turn the candle
      canvas.onpointerdown = e => { cp.drag = true; lastX = e.clientX; canvas.setPointerCapture(e.pointerId); };
      canvas.onpointermove = e => { if (cp.drag) { cp.rot += (e.clientX - lastX) * 0.012; lastX = e.clientX; } };
      canvas.onpointerup = canvas.onpointercancel = () => { cp.drag = null; };
      buildPreviewCandle();
      cp.raf = requestAnimationFrame(drawPreview);
    },
    set(opts) { if (cp.canvas) { cp.opts = { ...opts }; buildPreviewCandle(); } },   // the buyer changed a choice: build the candle again
    hide() { cancelAnimationFrame(cp.raf); dropPreviewCandle(); if (cp.canvas) { cp.canvas.onpointerdown = cp.canvas.onpointermove = cp.canvas.onpointerup = cp.canvas.onpointercancel = null; } cp.canvas = null; }
  };

  frame();
}

start();
