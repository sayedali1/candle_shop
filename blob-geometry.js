/* "blob": one smooth soft body made of blended ellipsoids (a puppy, a bear, a pebble), built with the MarchingCubes addon from our own distances.
   Used by the page (a small body built on the fly) and by tools/bake-blob.mjs (a bigger body built once and saved as a file, see below).
   Recipe part: "els": [{c:[x,y,z], r:[a,b,c], rot:[x,y,z]}], "cuts": same shape, carved OUT of the body (grooves between toes), "k" how softly they melt together,
   "res" grid size, "box": {c:[x,y,z], h} the cube it fits in, "clipY" a flat floor.
   Besides the shape, every point gets two numbers worked out from the same distances (the "baked" part, free while drawing):
     aAT.x  ambient occlusion: how shut-in the point is (creases and contact with the other puppy are darker)
     aAT.y  thinness: 1 where the body is thin (ears, paws), so light from the flame shows through there, 0 where it is thick
     aAT.z  tone: 1 inside the "tones" blocks (a muzzle, a chest): the paler wax colour is mixed in there, softly, like a hand-dyed candle */
export function makeBlobGeometry(THREE, MC) {
  return (p) => {
    if (!MC) return new THREE.BufferGeometry();
    const res = p.res || 56, half = res / 2, C = p.box.c, S = p.box.h, k = p.k ?? 0.07, ISO = 80, G = 2000;
    const mc = new MC(res, new THREE.MeshBasicMaterial(), false, false, res * res * 12);
    const eul = new THREE.Euler(), M = new THREE.Matrix4();
    const prep = (list) => (list || []).map((e) => {
      M.makeRotationFromEuler(eul.set(...(e.rot || [0, 0, 0]))); const m = M.elements;     // the inverse of a rotation is its transpose
      return { c: e.c, r: e.r, inv: [m[0], m[1], m[2], m[4], m[5], m[6], m[8], m[9], m[10]], mr: Math.min(...e.r) };
    });
    const els = prep(p.els), cuts = prep(p.cuts);
    const one = (e, wx, wy, wz) => {
      const dx = wx - e.c[0], dy = wy - e.c[1], dz = wz - e.c[2], v = e.inv;
      const qx = v[0] * dx + v[1] * dy + v[2] * dz, qy = v[3] * dx + v[4] * dy + v[5] * dz, qz = v[6] * dx + v[7] * dy + v[8] * dz;
      const ax = qx / e.r[0], ay = qy / e.r[1], az = qz / e.r[2];
      const k0 = Math.sqrt(ax * ax + ay * ay + az * az), k1 = Math.sqrt((ax / e.r[0]) ** 2 + (ay / e.r[1]) ** 2 + (az / e.r[2]) ** 2);
      return k1 > 1e-9 ? k0 * (k0 - 1) / k1 : -e.mr;                       // a good estimate of the distance to an ellipsoid
    };
    const smin = (a, b, kk) => { const h = Math.max(kk - Math.abs(a - b), 0) / kk; return Math.min(a, b) - h * h * kk * 0.25; };
    const dist = (wx, wy, wz) => {
      let dd = 1e9;
      for (let i = 0; i < els.length; i++) { const d = one(els[i], wx, wy, wz); dd = dd > 1e8 ? d : smin(dd, d, k); }
      for (let i = 0; i < cuts.length; i++) dd = -smin(-dd, one(cuts[i], wx, wy, wz), 0.012);     // carve: a smooth maximum with the cut's inside
      if (p.clipY !== undefined) dd = Math.max(dd, p.clipY - wy);
      return dd;
    };
    const f = mc.field;
    for (let z = 0; z < res; z++) for (let y = 0; y < res; y++) for (let x = 0; x < res; x++)
      f[x + y * res + z * res * res] = ISO - dist(C[0] + S * (x - half) / half, C[1] + S * (y - half) / half, C[2] + S * (z - half) / half) * G;
    mc.isolation = ISO; mc.update();

    /* the marching cubes give separate triangles: join the points that sit in the same place, so the body is one indexed mesh (a sixth of the points) */
    const seen = new Map(), P = [], N = [], idx = [];
    for (let i = 0; i < mc.count; i++) {
      const x = mc.positionArray[i * 3] * S + C[0], y = mc.positionArray[i * 3 + 1] * S + C[1], z = mc.positionArray[i * 3 + 2] * S + C[2];
      const key = Math.round(x * 4000) + ',' + Math.round(y * 4000) + ',' + Math.round(z * 4000);
      let id = seen.get(key);
      if (id === undefined) {
        id = P.length / 3; seen.set(key, id); P.push(x, y, z);
        const nx = mc.normalArray[i * 3], ny = mc.normalArray[i * 3 + 1], nz = mc.normalArray[i * 3 + 2], l = Math.hypot(nx, ny, nz) || 1;
        N.push(nx / l, ny / l, nz / l);
      }
      idx.push(id);
    }
    const tones = prep(p.tones);
    const toneAt = (x, y, z) => { let best = 0; for (const e of tones) { const dd = one(e, x, y, z) / Math.min(...e.r); best = Math.max(best, 1 - Math.min(1, Math.max(0, dd / 0.9 + 0.35))); } return best; };
    const n = P.length / 3, AT = new Float32Array(n * 3), floor = p.clipY ?? -1e9;
    const aoK = p.aoK ?? 5, thinA = p.thinFrom ?? 0.12, thinB = p.thinTo ?? 0.34;
    for (let i = 0; i < n; i++) {
      const x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2], nx = N[i * 3], ny = N[i * 3 + 1], nz = N[i * 3 + 2];
      let occ = 0, sca = 1;                                                   // ambient occlusion: how much closer than "free air" is the body a little way out?
      for (let j = 1; j <= 4; j++) { const h = 0.03 * j; occ += (h - dist(x + nx * h, y + ny * h, z + nz * h)) * sca; sca *= 0.7; }
      let ao = Math.min(1, Math.max(0, 1 - aoK * occ));
      const up = Math.min(1, Math.max(0, (y - floor) / 0.1)); ao *= 0.6 + 0.4 * up * up * (3 - 2 * up);      // a little darker where it touches the table
      let t = thinB;                                                          // thickness: walk inwards until we come out the other side
      for (let s = 1; s <= 14; s++) { const w = s * 0.025; if (dist(x - nx * w, y - ny * w, z - nz * w) > 0.002) { t = w; break; } }
      const q = Math.min(1, Math.max(0, (t - thinA) / (thinB - thinA)));
      AT[i * 3] = ao; AT[i * 3 + 1] = 1 - q * q * (3 - 2 * q); AT[i * 3 + 2] = tones.length ? toneAt(x, y, z) : 0;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(P), 3));
    g.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(N), 3));
    g.setAttribute('aAT', new THREE.BufferAttribute(AT, 3));
    g.setIndex(new THREE.BufferAttribute(n > 65535 ? new Uint32Array(idx) : new Uint16Array(idx), 1));
    g.computeBoundingSphere(); return g;
  };
}

/* ---- baked bodies: build the body once on a computer (tools/bake-blob.mjs), keep it as a small file, load that on the page.
   File: 4 numbers of header (magic, points, indices, index size), the box (min, size), then the points squeezed to 16 and 8 bits. About a fifth of a .glb of the same body. */
export function encodeBlob(geo) {
  const P = geo.attributes.position.array, N = geo.attributes.normal.array, A = geo.attributes.aAT.array, I = geo.index.array;
  const n = P.length / 3, ni = I.length, isz = n > 65535 ? 4 : 2, mn = [1e9, 1e9, 1e9], mx = [-1e9, -1e9, -1e9];
  for (let i = 0; i < n; i++) for (let a = 0; a < 3; a++) { mn[a] = Math.min(mn[a], P[i * 3 + a]); mx[a] = Math.max(mx[a], P[i * 3 + a]); }
  const rg = mx.map((v, a) => (v - mn[a]) || 1), up = (x) => (x + 3) & ~3;
  const oPos = 48, oNor = oPos + up(n * 6), oAT = oNor + up(n * 3), oIdx = oAT + up(n * 3), total = oIdx + up(ni * isz);
  const buf = new ArrayBuffer(total), dv = new DataView(buf);
  dv.setUint32(0, 0x424c4232, true); dv.setUint32(4, n, true); dv.setUint32(8, ni, true); dv.setUint32(12, isz, true);
  for (let a = 0; a < 3; a++) { dv.setFloat32(16 + a * 4, mn[a], true); dv.setFloat32(28 + a * 4, rg[a], true); }
  const pos = new Uint16Array(buf, oPos, n * 3), nor = new Int8Array(buf, oNor, n * 3), at = new Uint8Array(buf, oAT, n * 3), idx = isz === 4 ? new Uint32Array(buf, oIdx, ni) : new Uint16Array(buf, oIdx, ni);
  for (let i = 0; i < n; i++) {
    for (let a = 0; a < 3; a++) { pos[i * 3 + a] = Math.round((P[i * 3 + a] - mn[a]) / rg[a] * 65535); nor[i * 3 + a] = Math.round(N[i * 3 + a] * 127); }
    at[i * 3] = Math.round(A[i * 3] * 255); at[i * 3 + 1] = Math.round(A[i * 3 + 1] * 255); at[i * 3 + 2] = Math.round(A[i * 3 + 2] * 255);
  }
  idx.set(I);
  return buf;
}
export function decodeBlob(THREE, buf, paint) {
  const dv = new DataView(buf);
  if (dv.getUint32(0, true) !== 0x424c4232) throw new Error('not a baked body');
  const n = dv.getUint32(4, true), ni = dv.getUint32(8, true), isz = dv.getUint32(12, true), up = (x) => (x + 3) & ~3;
  const mn = [0, 1, 2].map(a => dv.getFloat32(16 + a * 4, true)), rg = [0, 1, 2].map(a => dv.getFloat32(28 + a * 4, true));
  const oPos = 48, oNor = oPos + up(n * 6), oAT = oNor + up(n * 3), oIdx = oAT + up(n * 3);
  const pq = new Uint16Array(buf, oPos, n * 3), nq = new Int8Array(buf, oNor, n * 3), aq = new Uint8Array(buf, oAT, n * 3);
  const P = new Float32Array(n * 3), N = new Float32Array(n * 3), A = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    for (let a = 0; a < 3; a++) { P[i * 3 + a] = mn[a] + pq[i * 3 + a] / 65535 * rg[a]; N[i * 3 + a] = nq[i * 3 + a] / 127; }
    const l = Math.hypot(N[i * 3], N[i * 3 + 1], N[i * 3 + 2]) || 1; N[i * 3] /= l; N[i * 3 + 1] /= l; N[i * 3 + 2] /= l;
    A[i * 3] = aq[i * 3] / 255; A[i * 3 + 1] = aq[i * 3 + 1] / 255; A[i * 3 + 2] = aq[i * 3 + 2] / 255;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(P, 3)); g.setAttribute('normal', new THREE.BufferAttribute(N, 3)); g.setAttribute('aAT', new THREE.BufferAttribute(A, 3));
  g.setIndex(new THREE.BufferAttribute(isz === 4 ? new Uint32Array(buf, oIdx, ni) : new Uint16Array(buf, oIdx, ni), 1));
  if (paint) {                                                              // paint: colour multipliers per point (128 = no change), made from the photo by tools/paint_blob.py
    const pq = new Uint8Array(paint), C = new Float32Array(n * 3); for (let j = 0; j < n * 3; j++) C[j] = pq[j] / 128;
    g.setAttribute('color', new THREE.BufferAttribute(C, 3));
  }
  g.computeBoundingSphere(); return g;
}
