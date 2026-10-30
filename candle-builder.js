/* Builds a 3D candle from a small recipe (a JSON file), so a new candle is a new file, not new code.
   The recipe format is documented in the candle-from-photo skill (references/recipe-format.md).
   Used by the page (candle.js) and by the Candle Lab (lab.html). Needs Three.js passed in. */

const KINDS = {                                                   // what each material kind starts from; a recipe overrides any of it
  wax:   { roughness: 0.48, sheen: 1, sheenRoughness: 0.5, sheenColor: '#ffe0a0', bump: 0.35, glow: 0.35, clearcoat: 0.12, clearcoatRoughness: 0.5 },
  matte: { roughness: 0.88, bump: 0.15, glow: 0.3 },
  glaze: { roughness: 0.38, clearcoat: 0.6, clearcoatRoughness: 0.15, glow: 0.08 },
  glass: { roughness: 0.03, opacity: 0.15, clearcoat: 1, clearcoatRoughness: 0.03, glow: 0, glass: true },
  solid: { roughness: 0.5, glow: 0 },
  wood:  { roughness: 0.8, glow: 0 },
  paper: { roughness: 0.78, glow: 0.05 },
  metal: { roughness: 0.35, metalness: 1, glow: 0, env: 1.4 }
};
const FINISH = { matte: { rough: 0.3, coat: 0 }, satin: { rough: 0, coat: 0 }, glossy: { rough: -0.22, coat: 0.5 } };   // "finish" nudges roughness and clear coat

/* What the buyer can change, from the recipe's own "custom" block (nothing is invented here: a recipe without it is not customizable):
     "color": [{ "mat": "<material>", "path": "color" }]  the main colour, set on those materials
     "name":  { "kind": "label", "r": radius, "y": height, "w": width }  a paper label wrapped on the front, with the name on it
              { "kind": "title", "mat": "<material>" }                   or the title of a label the candle already has
   Returns a changed copy. opts: { color: '#rrggbb', name: 'text' } */
export function customize(recipe, opts = {}) {
  const r = JSON.parse(JSON.stringify(recipe)), c = r.custom || {};
  if (opts.color && c.color) c.color.forEach(t => {
    const m = r.materials[t.mat]; if (!m) return;
    const path = t.path.split('.'); let o = m;
    for (let i = 0; i < path.length - 1; i++) o = o[path[i]];
    let col = opts.color;
    if (t.mul) { const n = parseInt(col.slice(1), 16), k = t.mul, ch = v => Math.max(0, Math.min(255, Math.round(v * k))); col = '#' + [ch(n >> 16 & 255), ch(n >> 8 & 255), ch(n & 255)].map(v => v.toString(16).padStart(2, '0')).join(''); }
    o[path[path.length - 1]] = col;
  });
  const name = (opts.name || '').trim();
  if (name && c.name) {
    if (c.name.kind === 'title') r.materials[c.name.mat].texture.title = name;
    else {
      const th = c.name.w / c.name.r;                                   // the label is wrapped around the front, as wide as asked
      r.materials._label = { kind: 'paper', side: 'double', texture: { kind: 'label', title: name, sub: 'Boba Candels' } };
      r.parts.push({ shape: 'cylinder', material: '_label', r: c.name.r, h: c.name.w / 2, open: true, segments: 48, thetaStart: -th / 2, thetaLength: th, pos: [0, c.name.y, 0] });
    }
  }
  return r;
}

export function makeBuilder(THREE) {
  let MC = null;                                                   // the MarchingCubes class, given by the page with setMarching (only recipes with a "blob" part need it)
  let GLTF = null;                                                 // the GLB loader, given by the page with setLoader (only pages that have a recipe with a "model" need it)
  const color = c => new THREE.Color(c);
  const geoCache = new Map(), texCache = new Map();                 // a shop has many candles but few recipes: they share geometry and textures (less memory, less building)

  const canvasTexture = (w, h, draw, srgb = true) => {
    const c = document.createElement('canvas'); c.width = w; c.height = h;
    draw(c.getContext('2d'), w, h);
    const t = new THREE.CanvasTexture(c);
    if (srgb) t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 4;
    return t;
  };
  const noise = (() => {                                          // a grain that makes wax look hand-poured instead of perfectly smooth
    const t = canvasTexture(256, 256, (g, w, h) => {
      const img = g.createImageData(w, h);
      for (let i = 0; i < img.data.length; i += 4) { const v = 128 + (Math.random() - 0.5) * 60; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255; }
      g.putImageData(img, 0, 0);
    }, false);
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(3, 2);
    return t;
  })();
  let furTex = null;
  const getFur = () => furTex || (furTex = (() => {                 // thousands of tiny curls, drawn so the picture tiles without a seam
    const t = canvasTexture(512, 512, (g, w, h) => {
      g.fillStyle = '#808080'; g.fillRect(0, 0, w, h);
      let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
      for (let i = 0; i < 2400; i++) {
        const x = rnd() * w, y = rnd() * h, r = 5 + rnd() * 6, a = rnd() * 6;
        for (const [ox, oy] of [[0, 0], [-w, 0], [w, 0], [0, -h], [0, h]]) {
          const gr = g.createRadialGradient(x + ox, y + oy, 0, x + ox, y + oy, r);
          gr.addColorStop(0, 'rgba(255,255,255,0.6)'); gr.addColorStop(0.6, 'rgba(255,255,255,0.2)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
          g.fillStyle = gr; g.beginPath(); g.arc(x + ox, y + oy, r, 0, 7); g.fill();
          g.strokeStyle = 'rgba(0,0,0,0.4)'; g.lineWidth = 1.7; g.beginPath(); g.arc(x + ox, y + oy, r * 0.8, a, a + 3.6); g.stroke();      // the dark line of a curl
        }
      }
    }, false);
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(4, 3);
    return t;
  })());
  const poolTexture = canvasTexture(128, 128, (g) => {            // the soft contact shadow under every candle
    const r = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    r.addColorStop(0, 'rgba(0,0,0,0.7)'); r.addColorStop(0.6, 'rgba(0,0,0,0.3)'); r.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = r; g.fillRect(0, 0, 128, 128);
  });

  /* ---------- textures a material can ask for ---------- */
  const painters = {
    /* a glazed cup: glaze on the top, bare clay below, with speckles */
    ceramic: (t) => canvasTexture(512, 256, (g, w, h) => {
      g.fillStyle = t.clay || '#d8aa8c'; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(120,80,50,${Math.random() * 0.12})`; g.fillRect(Math.random() * w, h * 0.5 + Math.random() * h * 0.5, 2, 2); }
      const split = t.split ?? 0.48;
      g.fillStyle = t.glaze || '#f3f0e8'; g.beginPath(); g.moveTo(0, 0); g.lineTo(w, 0);
      for (let x = w; x >= 0; x -= 16) g.lineTo(x, h * split + Math.sin(x / 40) * 7);       // a hand-dipped, wavy edge
      g.closePath(); g.fill();
      const specks = t.specks || ['#1f3f9a', '#6a3b20'];
      for (let i = 0; i < (t.count ?? 420); i++) { g.fillStyle = specks[i % specks.length]; g.beginPath(); g.arc(Math.random() * w, Math.random() * h * (split - 0.02), 1 + Math.random() * 3.2, 0, 7); g.fill(); }
    }),
    /* a wrap around a jar: small flowers and leaves, with a cream panel in the middle (the front of the jar) */
    floral: (t) => canvasTexture(2048, 320, (g, w, h) => {
      g.fillStyle = t.base || '#c9776a'; g.fillRect(0, 0, w, h);
      const leaves = t.leaves || ['#4d6b3f', '#6f8a52'], petals = t.petals || ['#f6e6d8', '#e89aa0', '#f7d79a'];
      for (let i = 0; i < 150; i++) {
        g.save(); g.translate(Math.random() * w, Math.random() * h); g.rotate(Math.random() * 6.3);
        g.fillStyle = leaves[i % leaves.length]; g.beginPath(); g.ellipse(0, 0, 20 + Math.random() * 14, 8 + Math.random() * 5, 0, 0, 7); g.fill(); g.restore();
      }
      for (let i = 0; i < 100; i++) {
        const x = Math.random() * w, y = Math.random() * h, s = 11 + Math.random() * 12;
        g.fillStyle = petals[i % petals.length];
        for (let k = 0; k < 5; k++) { const an = k * Math.PI * 2 / 5; g.beginPath(); g.arc(x + Math.cos(an) * s * 0.55, y + Math.sin(an) * s * 0.55, s * 0.42, 0, 7); g.fill(); }
        g.fillStyle = '#e9b44c'; g.beginPath(); g.arc(x, y, s * 0.28, 0, 7); g.fill();
      }
      const rr = (x, y, rw, rh, r) => { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + rw, y, x + rw, y + rh, r); g.arcTo(x + rw, y + rh, x, y + rh, r); g.arcTo(x, y + rh, x, y, r); g.arcTo(x, y, x + rw, y, r); g.closePath(); };
      const pw = 700, ph = 236, px = (w - pw) / 2, py = (h - ph) / 2;
      g.fillStyle = t.panel || '#f3e8d2'; rr(px, py, pw, ph, 30); g.fill();
      g.strokeStyle = t.line || '#a8483a'; g.lineWidth = 5; rr(px + 14, py + 14, pw - 28, ph - 28, 20); g.stroke();
      g.fillStyle = '#3a2a17'; g.textAlign = 'center'; g.direction = 'rtl';
      let fs = 84; g.font = `700 ${fs}px Cairo, Tahoma, sans-serif`;
      while (g.measureText(t.title || 'علامة تجريبية').width > pw - 90 && fs > 36) { fs -= 4; g.font = `700 ${fs}px Cairo, Tahoma, sans-serif`; }   // a long name shrinks to fit the panel
      g.fillText(t.title || 'علامة تجريبية', w / 2, py + 108);
      g.fillStyle = '#5a4128'; g.font = '500 40px Cairo, Tahoma, sans-serif'; g.fillText(t.sub || 'نص تجريبي', w / 2, py + 178);
    }),
    /* a paper label with a border, for jars */
    label: (t) => canvasTexture(1024, 512, (g, w, h) => {
      g.fillStyle = t.paper || '#eadfc8'; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 2600; i++) { g.fillStyle = `rgba(90,70,40,${Math.random() * 0.05})`; g.fillRect(Math.random() * w, Math.random() * h, 2, 2); }
      const ink = t.ink || '#2b1d0f';
      g.strokeStyle = ink; g.lineWidth = 6; g.strokeRect(34, 34, w - 68, h - 68);
      g.globalAlpha = 0.5; g.lineWidth = 2; g.strokeRect(50, 50, w - 100, h - 100); g.globalAlpha = 1;
      g.fillStyle = ink; g.textAlign = 'center'; g.direction = 'rtl';
      let fs = 160; g.font = `700 ${fs}px Cairo, Tahoma, sans-serif`;
      while (g.measureText(t.title || 'علامة تجريبية').width > w - 170 && fs > 44) { fs -= 6; g.font = `700 ${fs}px Cairo, Tahoma, sans-serif`; }   // a long name shrinks to fit the label
      g.fillText(t.title || 'علامة تجريبية', w / 2, 235);
      g.font = '600 56px Cairo, Tahoma, sans-serif'; g.fillText(t.sub || 'شمعة يدوية', w / 2, 330);
    })
  };

  /* "fuzz": { amp, freq } pushes a surface in and out with smooth noise: curly fur on a sculpted candle (sphere and capsule parts) */
  const hash3 = (x, y, z) => { let h = Math.imul(x, 374761393) ^ Math.imul(y, 668265263) ^ Math.imul(z, 2147483629); h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967295; };
  const GRADS = [[1, 1, 0], [-1, 1, 0], [1, -1, 0], [-1, -1, 0], [1, 0, 1], [-1, 0, 1], [1, 0, -1], [-1, 0, -1], [0, 1, 1], [0, -1, 1], [0, 1, -1], [0, -1, -1]];
  const grad = (xi, yi, zi, x, y, z) => { const g = GRADS[Math.floor(hash3(xi, yi, zi) * 12) % 12]; return g[0] * x + g[1] * y + g[2] * z; };
  const vnoise = (x, y, z) => {                                 // smooth gradient noise, about -0.9 to 0.9 (no grid-aligned steps)
    const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z), fx = x - xi, fy = y - yi, fz = z - zi;
    const fade = t => t * t * t * (t * (t * 6 - 15) + 10), u = fade(fx), v = fade(fy), w = fade(fz), L = (a, b, t) => a + (b - a) * t;
    return L(L(L(grad(xi, yi, zi, fx, fy, fz), grad(xi + 1, yi, zi, fx - 1, fy, fz), u), L(grad(xi, yi + 1, zi, fx, fy - 1, fz), grad(xi + 1, yi + 1, zi, fx - 1, fy - 1, fz), u), v),
             L(L(grad(xi, yi, zi + 1, fx, fy, fz - 1), grad(xi + 1, yi, zi + 1, fx - 1, fy, fz - 1), u), L(grad(xi, yi + 1, zi + 1, fx, fy - 1, fz - 1), grad(xi + 1, yi + 1, zi + 1, fx - 1, fy - 1, fz - 1), u), v), w);
  };
  const fuzzGeo = (g, f) => {
    const pa = g.attributes.position, na = g.attributes.normal;
    for (let i = 0; i < pa.count; i++) {
      const x = pa.getX(i), y = pa.getY(i), z = pa.getZ(i), q = f.freq;
      const x2 = (0.36 * x + 0.48 * y - 0.8 * z) * q * 2.3, y2 = (-0.8 * x + 0.6 * y) * q * 2.3, z2 = (0.48 * x + 0.64 * y + 0.6 * z) * q * 2.3;   // the finer layer is turned, so the two never line up
      const d = (vnoise(x * q, y * q, z * q) + 0.5 * vnoise(x2, y2, z2)) * f.amp;      // two layers: big curls and finer ones
      pa.setXYZ(i, x + na.getX(i) * d, y + na.getY(i) * d, z + na.getZ(i) * d);
    }
    g.computeVertexNormals();
    return g;
  };

  /* a capsule built as a lathe with many rings along its length (the stock capsule has none in the middle, so the fur could not bend it) */
  const capsuleLathe = p => {
    const C = 18, H = Math.max(2, Math.ceil(p.len / (p.r * 0.14))), pts = [];
    for (let i = 0; i <= C; i++) { const a = -Math.PI / 2 + (i / C) * (Math.PI / 2); pts.push(new THREE.Vector2(Math.max(p.r * Math.cos(a), 0.0001), -p.len / 2 + p.r * Math.sin(a))); }
    for (let j = 1; j < H; j++) pts.push(new THREE.Vector2(p.r, -p.len / 2 + (j / H) * p.len));
    for (let i = 0; i <= C; i++) { const a = (i / C) * (Math.PI / 2); pts.push(new THREE.Vector2(Math.max(p.r * Math.cos(a), 0.0001), p.len / 2 + p.r * Math.sin(a))); }
    return new THREE.LatheGeometry(pts, 64);
  };

  /* ---------- geometry for each part shape ---------- */
  const shapes = {
    lathe: (p) => {                                              // a profile of [radius, height] points turned around the middle
      const g = new THREE.LatheGeometry(p.profile.map(([r, y]) => new THREE.Vector2(r, y)), p.segments || (p.ribs ? 144 : 72));
      if (p.ribs) {                                              // vertical ribs: the radius swells and shrinks around the candle
        const pa = g.attributes.position;
        for (let i = 0; i < pa.count; i++) {
          const x = pa.getX(i), z = pa.getZ(i);
          if (Math.hypot(x, z) > 0.001) { const f = 1 + p.ribs.depth * Math.cos(Math.atan2(z, x) * p.ribs.count); pa.setX(i, x * f); pa.setZ(i, z * f); }
        }
        g.computeVertexNormals();
      }
      return g;
    },
    cylinder: (p) => new THREE.CylinderGeometry(p.r, p.rb ?? p.r, p.h, p.segments || 64, 1, !!p.open, p.thetaStart, p.thetaLength),
    disc: (p) => new THREE.CircleGeometry(p.r, 48).rotateX(-Math.PI / 2),
    torus: (p) => new THREE.TorusGeometry(p.r, p.tube, 10, 64).rotateX(Math.PI / 2),
    capsule: (p) => p.fuzz ? fuzzGeo(capsuleLathe(p), p.fuzz) : new THREE.CapsuleGeometry(p.r, p.len, 8, 24),
    box: (p) => new THREE.BoxGeometry(...p.size),
    sphere: (p) => p.fuzz ? fuzzGeo(new THREE.SphereGeometry(p.r, 72, 52), p.fuzz) : p.smooth ? new THREE.SphereGeometry(p.r, 40, 28) : new THREE.IcosahedronGeometry(p.r, 2)
  };

  /* builds one candle from a recipe. Returns what the page needs to light it and dim it. */

  /* "blob": one smooth soft body made of blended ellipsoids (a puppy, a bear, a pebble). It is built once, by filling the MarchingCubes grid with our own
     distances: "els": [{c:[x,y,z], r:[a,b,c], rot:[x,y,z]}], "k" how softly they melt together, "res" grid size, "box": {c:[x,y,z], h} the cube it fits in,
     "clipY" a flat floor. Fur ("fur": {...}) is then drawn as thin shells around it, see the part code. */
  const blobGeometry = (p) => {
    if (!MC) return new THREE.BufferGeometry();
    const res = p.res || 56, half = res / 2, C = p.box.c, S = p.box.h, k = p.k ?? 0.07, ISO = 80, G = 2000;
    const mc = new MC(res, new THREE.MeshBasicMaterial(), false, false, res * res * 10);
    const eul = new THREE.Euler(), M = new THREE.Matrix4();
    const els = p.els.map((e) => {
      M.makeRotationFromEuler(eul.set(...(e.rot || [0, 0, 0]))); const m = M.elements;     // the inverse of a rotation is its transpose
      return { c: e.c, r: e.r, inv: [m[0], m[1], m[2], m[4], m[5], m[6], m[8], m[9], m[10]], mr: Math.min(...e.r) };
    });
    const f = mc.field;
    for (let z = 0; z < res; z++) for (let y = 0; y < res; y++) for (let x = 0; x < res; x++) {
      const wx = C[0] + S * (x - half) / half, wy = C[1] + S * (y - half) / half, wz = C[2] + S * (z - half) / half;
      let dd = 1e9;
      for (let i = 0; i < els.length; i++) {
        const e = els[i], dx = wx - e.c[0], dy = wy - e.c[1], dz = wz - e.c[2], v = e.inv;
        const qx = v[0] * dx + v[1] * dy + v[2] * dz, qy = v[3] * dx + v[4] * dy + v[5] * dz, qz = v[6] * dx + v[7] * dy + v[8] * dz;
        const ax = qx / e.r[0], ay = qy / e.r[1], az = qz / e.r[2];
        const k0 = Math.sqrt(ax * ax + ay * ay + az * az), k1 = Math.sqrt((ax / e.r[0]) ** 2 + (ay / e.r[1]) ** 2 + (az / e.r[2]) ** 2);
        const d = k1 > 1e-9 ? k0 * (k0 - 1) / k1 : -e.mr;                  // a good estimate of the distance to an ellipsoid
        if (dd > 1e8) dd = d; else { const h = Math.max(k - Math.abs(dd - d), 0) / k; dd = Math.min(dd, d) - h * h * k * 0.25; }     // melt: smooth minimum
      }
      if (p.clipY !== undefined) dd = Math.max(dd, p.clipY - wy);
      f[x + y * res + z * res * res] = ISO - dd * G;
    }
    mc.isolation = ISO; mc.update();
    const n = mc.count * 3, pos = new Float32Array(n), nor = new Float32Array(n);
    for (let i = 0; i < mc.count; i++) {
      pos[i * 3] = mc.positionArray[i * 3] * S + C[0]; pos[i * 3 + 1] = mc.positionArray[i * 3 + 1] * S + C[1]; pos[i * 3 + 2] = mc.positionArray[i * 3 + 2] * S + C[2];
      const nx = mc.normalArray[i * 3], ny = mc.normalArray[i * 3 + 1], nz = mc.normalArray[i * 3 + 2], l = Math.hypot(nx, ny, nz) || 1;
      nor[i * 3] = nx / l; nor[i * 3 + 1] = ny / l; nor[i * 3 + 2] = nz / l;
    }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
    g.computeBoundingSphere(); return g;
  };

  /* fur shells: the same body drawn "layers" times, each a little bigger, with most of it cut away by a pattern of strands: stacked up it looks like fur.
     "fur": { material, layers, len, dens, droop, under, bare: [[x,y,z,radius], ...] (no fur there: a muzzle) } */
  const furShellMaterial = (base, t, F, glows, tints) => {
    const fm = base.clone(); fm.bumpMap = null;
    tints.push({ m: fm, base: fm.color.clone() });
    const g = glows.find((q) => q.m === base); if (g) glows.push({ m: fm, k: g.k });
    const bare = [0, 1, 2, 3].map((i) => (F.bare && F.bare[i]) ? new THREE.Vector4(...F.bare[i]) : new THREE.Vector4(0, 0, 0, 0));
    fm.onBeforeCompile = (sh) => {
      sh.uniforms.uShell = { value: t }; sh.uniforms.uLen = { value: F.len || 0.04 }; sh.uniforms.uDroop = { value: F.droop || 0 };
      sh.uniforms.uDens = { value: F.dens || 40 }; sh.uniforms.uUnder = { value: F.under ?? 0.55 }; sh.uniforms.uBare = { value: bare };
      sh.vertexShader = sh.vertexShader
        .replace('#include <common>', '#include <common>\nvarying vec3 vObj; uniform float uShell, uLen, uDroop;')
        .replace('#include <begin_vertex>', '#include <begin_vertex>\nvObj = position; transformed += normal * (uShell * uLen); transformed.y -= uShell * uShell * uDroop;');
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <common>', `#include <common>
varying vec3 vObj; uniform float uShell, uDens, uUnder; uniform vec4 uBare[4];
float h3(vec3 p) { p = fract(p * 0.3183099 + 0.1); p *= 17.0; return fract(p.x * p.y * p.z * (p.x + p.y + p.z)); }`)
        .replace('#include <clipping_planes_fragment>', `#include <clipping_planes_fragment>
float tone = 1.0;
for (int bi = 0; bi < 4; bi++) { if (uBare[bi].w > 0.0 && distance(vObj, uBare[bi].xyz) < uBare[bi].w) discard; }
{
  vec3 pc = vObj * uDens; vec3 cell = floor(pc); vec3 fr = fract(pc) - 0.5;
  float hh = 0.6 + 0.4 * h3(cell);
  vec3 jit = vec3(h3(cell + 7.1), h3(cell + 13.7), h3(cell + 3.3)) - 0.5;
  fr += 0.28 * uShell * vec3(sin(cell.y * 2.3 + uShell * 6.0), sin(cell.z * 1.7 + 2.0), cos(cell.x * 2.9 + uShell * 6.0));     // curl: each strand wanders as it rises
  tone = 0.82 + 0.3 * h3(cell + 21.7);
  float dist = length(fr - jit * 0.5 - jit.zxy * uShell * 0.9) * 1.6;
  float reach = 1.0 - uShell / hh;
  if (uShell > hh || dist > 0.42 + 0.45 * reach) discard;
}`)
        .replace('#include <color_fragment>', '#include <color_fragment>\ndiffuseColor.rgb *= mix(uUnder, 1.0, uShell) * tone;');
    };
    return fm;
  };

  function build(recipe, fresh = false) {
    const group = new THREE.Group(), tints = [], glows = [], cache = {}, own = [];   // fresh: its textures are its own (not shared), so dispose() can free them

    const material = (ref) => {
      const key = typeof ref === 'string' ? ref : null;
      if (key && cache[key]) return cache[key];
      const def = typeof ref === 'string' ? recipe.materials[ref] : ref;
      if (!def) throw new Error('unknown material: ' + ref);
      const kind = KINDS[def.kind || 'solid'];
      const d = { ...kind, ...def };
      const fin = FINISH[d.finish];
      const o = { color: color(d.texture ? '#ffffff' : d.color || '#ffffff'), roughness: Math.min(1, Math.max(0, d.roughness + (fin ? fin.rough : 0))), metalness: d.metalness || 0, envMapIntensity: d.env ?? (d.glass ? 1.8 : 0.3) };
      if (d.sheen) { o.sheen = d.sheen; o.sheenRoughness = d.sheenRoughness; o.sheenColor = color(d.sheenColor); }
      if (d.clearcoat || (fin && fin.coat)) { o.clearcoat = Math.max(d.clearcoat || 0, fin ? fin.coat : 0); o.clearcoatRoughness = d.clearcoatRoughness ?? 0.2; }
      if (d.bump) { o.bumpMap = d.fur ? getFur() : noise; o.bumpScale = d.bump; }
      if (d.texture) {
        const tk = JSON.stringify(d.texture);
        if (fresh) { o.map = painters[d.texture.kind](d.texture); own.push(o.map); }
        else {
          if (!texCache.has(tk)) texCache.set(tk, painters[d.texture.kind](d.texture));
          o.map = texCache.get(tk);
        }
      }
      if (d.glass) { o.transparent = true; o.opacity = d.opacity; o.depthWrite = false; }
      o.side = d.side === 'back' ? THREE.BackSide : (d.glass || d.side === 'double') ? THREE.DoubleSide : THREE.FrontSide;
      o.emissive = color(d.glowColor || '#ff9a40'); o.emissiveIntensity = 0;
      const m = new THREE.MeshPhysicalMaterial(o);
      if (!d.glass || d.tint) tints.push({ m, base: o.color.clone() });      // unlit candles are dimmer; glass is not tinted
      if (d.glow) glows.push({ m, k: d.glow });
      if (key) cache[key] = m;
      return m;
    };

    const place = (mesh, p) => {
      if (p.pos) mesh.position.set(...p.pos);
      if (p.rot) mesh.rotation.set(...p.rot);
      if (p.scale) typeof p.scale === 'number' ? mesh.scale.setScalar(p.scale) : mesh.scale.set(...p.scale);
      const m = mesh.material; if (m.transparent) mesh.renderOrder = 2;
      group.add(mesh);
      return mesh;
    };

    (recipe.parts || []).forEach((p) => {
      const m = material(p.material);
      if (p.shape === 'spiral') {                                 // raised spirals on the top of the wax (a triskele when count is 3)
        for (let k = 0; k < p.count; k++) {
          const base = k * Math.PI * 2 / p.count + (p.start || 0.5), pts = [];
          for (let i = 0; i <= 24; i++) {
            const t = i / 24, an = base + t * Math.PI * 2 * p.turns, r = p.r0 + (p.r1 - p.r0) * t;
            pts.push(new THREE.Vector3(Math.cos(base) * p.ring + Math.cos(an) * r, p.y, Math.sin(base) * p.ring + Math.sin(an) * r));
          }
          group.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 40, p.tube, 6), m));
        }
      } else if (p.shape === 'drips') {                           // wax that ran down the side: rounded drips of different lengths
        let seed = p.seed || 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
        for (let k = 0; k < p.count; k++) {
          const an = (k + rnd() * 0.6) * Math.PI * 2 / p.count, len = p.len[0] + rnd() * (p.len[1] - p.len[0]), r = p.r * (0.8 + rnd() * 0.5);
          const d = new THREE.Mesh(new THREE.CapsuleGeometry(r, len, 4, 10), m);
          d.position.set(Math.cos(an) * (p.ring + r * 0.3), p.y - len / 2, Math.sin(an) * (p.ring + r * 0.3)); group.add(d);
        }
      } else if (p.shape === 'curls') {                           // curly fur: "pos", "radii" [x,y,z], "rot", "n" tufts of size "r"; "hide": {dir, angle} leaves a bare patch (a face); "minY" skips what is under the table
        if (!geoCache.has('curl')) geoCache.set('curl', new THREE.SphereGeometry(1, 6, 3));
        const im = new THREE.InstancedMesh(geoCache.get('curl'), m, p.n), dummy = new THREE.Object3D(), col = new THREE.Color();
        const UP = new THREE.Vector3(0, 1, 0), spin = new THREE.Quaternion();
        const cen = new THREE.Vector3(...p.pos), eul = new THREE.Euler(...(p.rot || [0, 0, 0])), hide = p.hide && { d: new THREE.Vector3(...p.hide.dir).normalize(), c: Math.cos(p.hide.angle) };
        let seed = p.seed || 3; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
        const golden = Math.PI * (3 - Math.sqrt(5)); let k = 0;
        for (let i = 0; i < p.n; i++) {
          const y = 1 - (i + 0.5) / p.n * 2, rr = Math.sqrt(Math.max(0, 1 - y * y)), th = golden * i + rnd() * 0.5;     // evenly spread over the surface, a little shaken
          const u = new THREE.Vector3(Math.cos(th) * rr + (rnd() - 0.5) * 0.14, y + (rnd() - 0.5) * 0.14, Math.sin(th) * rr + (rnd() - 0.5) * 0.14).normalize();
          const pt = new THREE.Vector3(u.x * p.radii[0], u.y * p.radii[1], u.z * p.radii[2]).applyEuler(eul).add(cen);
          if (pt.y < (p.minY ?? -9)) continue;
          if (hide && pt.clone().sub(cen).normalize().dot(hide.d) > hide.c) continue;
          const nrm = new THREE.Vector3(u.x / p.radii[0], u.y / p.radii[1], u.z / p.radii[2]).normalize().applyEuler(eul);   // the tuft lies on the skin: flat side down, turned at random
          dummy.position.copy(pt); dummy.quaternion.setFromUnitVectors(UP, nrm).multiply(spin.setFromAxisAngle(UP, rnd() * 6.283));
          const sz = p.r * (0.8 + 0.4 * rnd()); dummy.scale.set(sz * 1.15, sz * (0.55 + 0.2 * rnd()), sz * 1.15); dummy.updateMatrix();
          im.setMatrixAt(k, dummy.matrix);
          const shade = (0.9 + 0.2 * rnd()) * (u.y < -0.3 ? 0.78 : 1);        // each tuft a little lighter or darker, and darker underneath: depth
          im.setColorAt(k, col.setRGB(shade, shade, shade)); k++;
        }
        im.count = k; im.instanceMatrix.needsUpdate = true; if (im.instanceColor) im.instanceColor.needsUpdate = true;
        im.frustumCulled = false; group.add(im);
      } else if (p.shape === 'blob') {                            // a soft body of blended ellipsoids, with fur shells (see blobGeometry)
        const bk = 'blob' + JSON.stringify([p.els, p.k, p.res, p.box, p.clipY]);
        if (!geoCache.has(bk)) geoCache.set(bk, blobGeometry(p));
        const geo = geoCache.get(bk), F = p.fur;
        group.add(new THREE.Mesh(geo, m));
        if (F && F.layers) {
          const base = material(F.material || p.material);
          for (let i = 1; i <= F.layers; i++) { const sm = new THREE.Mesh(geo, furShellMaterial(base, i / F.layers, F, glows, tints)); sm.frustumCulled = false; group.add(sm); }
        }
      } else if (p.shape === 'dots') {                            // small round things: eyes, a nose. "at": [[x,y,z],...], "r"
        const dk = 'dot' + p.r;
        if (!geoCache.has(dk)) geoCache.set(dk, new THREE.SphereGeometry(p.r, 16, 12));
        p.at.forEach(([x, y, z]) => { const d = new THREE.Mesh(geoCache.get(dk), m); d.position.set(x, y, z); if (p.scale) d.scale.set(...p.scale); group.add(d); });
      } else if (p.shape === 'stones') {                          // a ring of crystals around the wick
        p.colors.forEach((c, k) => {
          const sk = 'stone' + (p.size || 0.065);
          if (!geoCache.has(sk)) geoCache.set(sk, new THREE.IcosahedronGeometry(p.size || 0.065, 1));
          const st = new THREE.Mesh(geoCache.get(sk), material({ kind: 'solid', color: c, roughness: 0.22, metalness: 0.1, clearcoat: 0.6, glow: 0.08 }));
          const an = k * 1.05 + 0.4, r = p.ring + 0.05 * (k % 2);
          st.position.set(Math.cos(an) * r, p.y, Math.sin(an) * r); st.scale.set(1, 0.75, 1); group.add(st);
        });
      } else {
        const { pos, rot, scale, material: _m, ...shape } = p, gk = JSON.stringify(shape);
        if (!geoCache.has(gk)) geoCache.set(gk, shapes[p.shape](p));
        const mesh = place(new THREE.Mesh(geoCache.get(gk), m), p);
        if (p.mirror) {                                           // the same part on the other side: "mirror": { "axis": "x" or "z", "about": number }
          const mm = mesh.clone(), ax = p.mirror.axis;
          mm.position[ax] = 2 * (p.mirror.about || 0) - mesh.position[ax];
          if (ax === 'x') { mm.rotation.z = -mesh.rotation.z; mm.rotation.y = -mesh.rotation.y; } else { mm.rotation.x = -mesh.rotation.x; mm.rotation.y = -mesh.rotation.y; }
          group.add(mm);
        }
      }
    });

    const wicks = recipe.wicks || [];
    wicks.forEach((w) => {                                        // cotton string, a long dark wick, or a flat wooden one
      const h = w.tip - w.base, mid = (w.tip + w.base) / 2;
      const wm = material(w.kind === 'wood' ? { kind: 'wood', color: w.color || '#b86a3a' } : { kind: 'solid', color: w.color || '#1c140e', roughness: 0.9 });
      const mesh = new THREE.Mesh(w.kind === 'wood' ? new THREE.BoxGeometry(w.width || 0.17, h, 0.022) : new THREE.CylinderGeometry(w.radius || 0.011, (w.radius || 0.011) * 1.2, h, 8), wm);
      mesh.position.set(w.x || 0, mid, w.z || 0); if (w.tilt) mesh.rotation.z = w.tilt;
      group.add(mesh);
    });

    const pw = recipe.shadow || 1.6;
    const pool = new THREE.Sprite(new THREE.SpriteMaterial({ map: poolTexture, transparent: true, depthWrite: false, opacity: 0.9 }));
    pool.scale.set(pw, pw * 0.2, 1); pool.position.set(0, 0.01, 0.1); pool.renderOrder = 1; group.add(pool);

    const w0 = wicks[0] || { tip: 0.8, x: 0 };
    const fl = recipe.flame || {};
    /* a recipe with "model": "assets/models/x.glb" shows that 3D file: scaled to "modelHeight" (default 1) tall, standing on the table, centred.
       It is lit, dimmed and warmed like every other candle. Its wick and flame still come from the recipe's "wicks" (heights in the same units). */
    let loaded = null;
    if (recipe.model && GLTF) {
      loaded = new Promise(res => new GLTF().load(recipe.model, gltf => {
        const m = gltf.scene, box = new THREE.Box3().setFromObject(m), size = box.getSize(new THREE.Vector3()), mid = box.getCenter(new THREE.Vector3());
        const k = (recipe.modelHeight || 1) / size.y;
        m.scale.setScalar(k); m.position.set(-mid.x * k, -box.min.y * k, -mid.z * k);
        m.rotation.y = recipe.modelTurn || 0;
        m.traverse(o => {
          if (!o.isMesh || !o.material) return;
          const mat = o.material; o.material = mat.isMeshStandardMaterial ? mat : new THREE.MeshStandardMaterial({ map: mat.map, color: mat.color });
          const mm = o.material; mm.envMapIntensity = recipe.modelEnv ?? 0.3; mm.roughness = Math.max(mm.roughness ?? 0.8, recipe.modelRough ?? 0.7); mm.metalness = 0;
          if (mm.color) tints.push({ m: mm, base: mm.color.clone() });
          mm.emissive = new THREE.Color(recipe.modelGlowColor || '#ff9a50'); if (mm.map) mm.emissiveMap = mm.map; mm.emissiveIntensity = 0;
          glows.push({ m: mm, k: recipe.modelGlow ?? 0.18 });
        });
        group.add(m); res(m);
      }, undefined, e => { console.warn('model not loaded:', recipe.model, e); res(null); }));
    }
    const dispose = () => {                                      // frees the materials (and, for a fresh candle, its textures); the shared shapes stay
      group.traverse(o => { if (o.isInstancedMesh) o.dispose(); if (o.material && o.material !== pool.material) o.material.dispose(); });
      pool.material.dispose(); own.forEach(t => t.dispose());
    };
    return { group, tints, glows, dispose, loaded, info: { wickY: w0.tip, flameX: w0.x || 0, fs: fl.size ?? 1, fw: fl.width ?? 1 }, turn: recipe.turn || 0, size: recipe.size || 1 };
  }

  return { build, canvasTexture, setLoader: L => { GLTF = L; }, setMarching: C => { MC = C; } };
}

/* the flame: an outer soft layer, a bright core and a faint halo, all swaying. Used by the Candle Lab; the page has its own copy in candle.js. */
export function makeFlame(THREE) {
  const lathe = pts => new THREE.LatheGeometry(pts.map(([r, y]) => new THREE.Vector2(r, y)), 36);
  const material = (core) => new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    uniforms: { uTime: { value: 0 }, uFlicker: { value: 1 }, uCore: { value: core }, uLean: { value: 0 } },
    vertexShader: `
      uniform float uTime; uniform float uLean; varying float vY; varying vec3 vN;
      void main() {
        float y = position.y / 0.27; vY = y; vec3 p = position;
        p.x += (sin(uTime * 7.0 + y * 4.0) * 0.012 + sin(uTime * 13.0 + y * 7.0) * 0.006) * y * y * 4.0;
        p.z += cos(uTime * 6.0 + y * 3.0) * 0.008 * y; p.x += uLean * y * y;
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
        a *= 0.88 + 0.12 * sin(uTime * 26.0 + vY * 9.0) * smoothstep(0.4, 1.0, vY);
        gl_FragColor = vec4(col * 1.7, a);
      }`
  });
  const shape = Array.from({ length: 26 }, (_, i) => { const u = i / 25; return [0.06 * Math.sin(Math.PI * Math.pow(u, 0.7)) * (1 - 0.3 * u), u * 0.27]; });
  const mats = [material(0), material(1), material(2)];
  const geo = lathe(shape);
  const halo = new THREE.Mesh(geo, mats[2]), outer = new THREE.Mesh(geo, mats[0]), core = new THREE.Mesh(geo, mats[1]);
  halo.renderOrder = 3; outer.renderOrder = 4; core.renderOrder = 5;
  const group = new THREE.Group(); group.add(halo, outer, core);
  /* place the flame at (x, y) with a candle scale s; amount 0..1 is how strongly it burns */
  group.update = (t, x, y, s, amount, fs = 1, fw = 1) => {
    const flick = Math.sin(t * 9) * 0.05 + Math.sin(t * 23.7) * 0.03 + Math.sin(t * 37) * 0.02;
    const gust = Math.pow(Math.max(0, Math.sin(t * 0.6) * Math.sin(t * 1.7 + 1)), 2) * 0.06;
    mats.forEach(m => { m.uniforms.uTime.value = t; m.uniforms.uFlicker.value = 1 + flick * 1.5 + gust * 3; m.uniforms.uLean.value = gust; });
    group.visible = amount > 0.01;
    group.position.set(x, y, 0);
    outer.scale.set(0.9 * amount * s * fs * fw, 0.9 * amount * s * fs * (1 + flick * 0.5), 0.9 * amount * s * fs);
    core.scale.set(0.5 * amount * s * fs * fw, 0.5 * amount * s * fs * (1 + flick * 0.6), 0.5 * amount * s * fs);
    halo.scale.set(1.5 * amount * s * fs * fw, 1.15 * amount * s * fs * (1 + flick * 0.4), 1.5 * amount * s * fs);
    return flick;
  };
  return group;
}
