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
    o[path[path.length - 1]] = opts.color;
  });
  const name = (opts.name || '').trim();
  if (name && c.name) {
    if (c.name.kind === 'title') r.materials[c.name.mat].texture.title = name;
    else {
      const th = c.name.w / c.name.r;                                   // the label is wrapped around the front, as wide as asked
      r.materials._label = { kind: 'paper', side: 'double', texture: { kind: 'label', title: name, sub: 'علامة تجريبية' } };
      r.parts.push({ shape: 'cylinder', material: '_label', r: c.name.r, h: c.name.w / 2, open: true, segments: 48, thetaStart: -th / 2, thetaLength: th, pos: [0, c.name.y, 0] });
    }
  }
  return r;
}

export function makeBuilder(THREE) {
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
    capsule: (p) => new THREE.CapsuleGeometry(p.r, p.len, 8, 24),
    box: (p) => new THREE.BoxGeometry(...p.size),
    sphere: (p) => new THREE.IcosahedronGeometry(p.r, 2)
  };

  /* builds one candle from a recipe. Returns what the page needs to light it and dim it. */
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
      if (d.bump) { o.bumpMap = noise; o.bumpScale = d.bump; }
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
        place(new THREE.Mesh(geoCache.get(gk), m), p);
      }
    });

    const wicks = recipe.wicks || [];
    wicks.forEach((w) => {                                        // cotton string, a long dark wick, or a flat wooden one
      const h = w.tip - w.base, mid = (w.tip + w.base) / 2;
      const wm = material(w.kind === 'wood' ? { kind: 'wood', color: w.color || '#b86a3a' } : { kind: 'solid', color: w.color || '#1c140e', roughness: 0.9 });
      const mesh = new THREE.Mesh(w.kind === 'wood' ? new THREE.BoxGeometry(w.width || 0.17, h, 0.022) : new THREE.CylinderGeometry(w.radius || 0.011, (w.radius || 0.011) * 1.2, h, 8), wm);
      mesh.position.set(w.x || 0, mid, 0); if (w.tilt) mesh.rotation.z = w.tilt;
      group.add(mesh);
    });

    const pw = recipe.shadow || 1.6;
    const pool = new THREE.Sprite(new THREE.SpriteMaterial({ map: poolTexture, transparent: true, depthWrite: false, opacity: 0.9 }));
    pool.scale.set(pw, pw * 0.2, 1); pool.position.set(0, 0.01, 0.1); pool.renderOrder = 1; group.add(pool);

    const w0 = wicks[0] || { tip: 0.8, x: 0 };
    const fl = recipe.flame || {};
    const dispose = () => {                                      // frees the materials (and, for a fresh candle, its textures); the shared shapes stay
      group.traverse(o => { if (o.material && o.material !== pool.material) o.material.dispose(); });
      pool.material.dispose(); own.forEach(t => t.dispose());
    };
    return { group, tints, glows, dispose, info: { wickY: w0.tip, flameX: w0.x || 0, fs: fl.size ?? 1, fw: fl.width ?? 1 }, turn: recipe.turn || 0, size: recipe.size || 1 };
  }

  return { build, canvasTexture };
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
