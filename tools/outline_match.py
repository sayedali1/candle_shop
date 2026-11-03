"""How close the 3D is to the photo, as a number: the recipe's exact 3D outline against the photo's traced outline (tools/trace_outline.py).
The shapes are rebuilt here the way candle-builder.js builds them (lathe with ribs and bend; rope; path rope; parts turned and placed; the group scaled by
the recipe's size), seen through the photo's camera (the Lab's photocam pose file), filled, and compared row by row with the trace.
Scores (each object is a recipe 'material' name that matches a trace side name, e.g. trace sides tall_L / tall_R and parts with material 'tall'):
  edges   = % of traced rows where the 3D edge is within 3 px of the photo's edge (also given for 6 px)
  overlap = how much the 3D silhouette and the photo's silhouette (filled between the traced sides) cover each other (intersection over union)
  MATCH   = the mean of the two. This is the number to show the user before calling a candle done.
Also lists the worst stretches (rows where the edge is more than 6 px off) and writes tools/fit/match-<recipe>.png: the photo with the trace in green
and the 3D outline in red, 2x, cropped to the objects.
Also reads 'model' GLB files (figure candles from tools/gen_relief.py, in candle units) and cylinder / torus / sphere parts; other parts are listed as not drawn.
If no part has an object's name as its material, the object is the whole candle (all parts and the model).
Run:  python tools/outline_match.py <recipe> <pose json> <trace json> [photo]
      python tools/outline_match.py <recipe> <pose json> --snap <name> <photo>     for FIGURES (tails, animals, trays: outlines that jump sideways
      from row to row): starts from the 3D outline, slides each point along its normal to the photo's strongest edge within 25 px (SNAP=n to change), smooths it, and writes
      tools/fit/trace-<name>.json with "<name>_poly" (a closed outline) and tools/fit/snap-<name>.png to check by eye. Wrong stretches: edit the points by hand.
      Then score it like any trace. (A figure's score is only as good as its outline: look at the snap picture first.)
      python tools/outline_match.py <recipe> <pose json> --guides <name> <photo>   writes tools/fit/trace-<name>.cfg.json with rough guides taken from the
      3D outline (one object, every 10 rows); then run tools/trace_outline.py on it and LOOK at the strips."""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
name, pose_p, trace_p = sys.argv[1:4]
R = json.load(open(os.path.join(ROOT, 'recipes', name + '.json'), encoding='utf-8'))
cam = json.load(open(pose_p))['camera']
GUIDES = trace_p in ('--guides', '--snap'); SNAP = trace_p == '--snap'
if GUIDES: gname, photo_arg = sys.argv[4], sys.argv[5]; TR = {gname + '_L': [], gname + '_R': []}
else: TR = json.load(open(trace_p))
cfg_p = trace_p.replace('.json', '.cfg.json')                     # the photo: from the trace's settings file, or the last argument
photo_p = os.path.join(ROOT, photo_arg) if GUIDES else os.path.join(ROOT, json.load(open(cfg_p))['photo']) if os.path.exists(cfg_p) else sys.argv[4]
im = Image.open(photo_p).convert('RGB'); W, H = im.size

T = np.array(cam['target'], float); yaw, pitch, dist = cam.get('yaw', 0), cam['pitch'], cam['dist']
P = T + dist * np.array([math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch)])
f = (T - P) / np.linalg.norm(T - P); rt = np.cross(f, [0, 1, 0]); rt /= np.linalg.norm(rt); up = np.cross(rt, f)
F = (H / 2) / math.tan(math.radians(cam['fov']) / 2); U0, V0 = cam.get('u0', 0), cam.get('v0', 0)


RL = cam.get('roll', 0)                                            # a camera that leans (tools/gen_relief.py bakes it into the surface; the Lab ignores it)


def project(p):
    q = np.atleast_2d(p) - P; z = q @ f; xr, yr = q @ rt / z * F, q @ up / z * F
    x0, y0 = xr * math.cos(RL) - yr * math.sin(RL), xr * math.sin(RL) + yr * math.cos(RL)
    return np.stack([W / 2 + U0 + x0, H / 2 + V0 - y0], 1)


def euler_xyz(rx, ry, rz):
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    return np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]) @ np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])


def lathe(p, n=720):
    pr = np.array(p['profile']); phi = np.linspace(0, 2 * math.pi, n, endpoint=False)
    x = pr[:, :1] * np.sin(phi); z = pr[:, :1] * np.cos(phi); y = np.repeat(pr[:, 1:2], n, 1)
    if p.get('ribs'):
        a = np.arctan2(z, x) * p['ribs']['count']; d = p['ribs']['depth']
        fl = 1 - d + d * np.abs(np.cos(a / 2)) if p['ribs'].get('shape') == 'flute' else 1 + d * np.cos(a); x, z = x * fl, z * fl
    if p.get('bend'):
        B = np.array(p['bend']); x = x + np.interp(y, B[:, 0], B[:, 1])
    return np.stack([x.ravel(), y.ravel(), z.ravel()], 1)


def rope(p, U=720, V=48):
    A = p.get('arc', 2 * math.pi); part = A < 6.28; S, Tw, D = p.get('strands', 3), p.get('twist', 40), p.get('depth', 0.14); E = p.get('square', 1)
    u = np.linspace(0, 1, U + 1)[:, None]; ph = np.linspace(0, 2 * math.pi, V, endpoint=False)[None]
    th = p.get('start', 0) + u * A; c, s = np.cos(th), np.sin(th)
    e = np.clip((u - 0.7) / 0.3, 0, 1); y0 = p.get('rise', 0) * u + p.get('lift', 0) * e * e * (3 - 2 * e)
    taper = np.sqrt(np.minimum(1, np.minimum(u, 1 - u) / 0.15)) if part else np.ones_like(u)
    rr = taper * p['tube'] * (1 + p.get('swell', 0) * c) * (1 - D + D * np.abs(np.cos((S * ph + Tw * th) / 2)))
    co = np.sign(np.cos(ph)) * np.abs(np.cos(ph)) ** E; si = np.sign(np.sin(ph)) * np.abs(np.sin(ph)) ** E
    out = p['r'] - p.get('tuck', 0) * (1 - taper) * p['tube'] + rr * co * p.get('flat', 1)
    return np.stack([(out * c).ravel(), (y0 + rr * si).ravel(), (out * s).ravel()], 1)


def catmull(Q, n=60):                                              # three.js CatmullRomCurve3, centripetal, open
    Pp = np.vstack([2 * Q[0] - Q[1], Q, 2 * Q[-1] - Q[-2]]); out = []
    for i in range(1, len(Pp) - 2):
        p0, p1, p2, p3 = Pp[i - 1], Pp[i], Pp[i + 1], Pp[i + 2]
        d0, d1, d2 = [max(np.sum((b_ - a_) ** 2) ** 0.25, 1e-4) for a_, b_ in ((p0, p1), (p1, p2), (p2, p3))]
        t1 = ((p1 - p0) / d0 - (p2 - p0) / (d0 + d1) + (p2 - p1) / d1) * d1; t2 = ((p2 - p1) / d1 - (p3 - p1) / (d1 + d2) + (p3 - p2) / d2) * d1
        for u in np.linspace(0, 1, n, endpoint=False):
            u2, u3 = u * u, u * u * u; out.append((2 * u3 - 3 * u2 + 1) * p1 + (u3 - 2 * u2 + u) * t1 + (-2 * u3 + 3 * u2) * p2 + (u3 - u2) * t2)
    out.append(Q[-1]); return np.array(out)


def path(p, V=48):
    Q = np.array(p['points']); C = catmull(Q[:, :3]); t = np.r_[0, np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))]; u = t / t[-1]
    r = np.interp(np.linspace(0, len(Q) - 1, len(C)), np.arange(len(Q)), Q[:, 3]); taper = np.sqrt(np.minimum(1, np.minimum(u, 1 - u) / 0.08)); E = p.get('square', 1)
    Tn = np.gradient(C, axis=0); Tn /= np.linalg.norm(Tn, axis=1, keepdims=True)
    n = np.stack([C[:, 0], np.zeros(len(C)), C[:, 2]], 1); n /= np.linalg.norm(n, axis=1, keepdims=True); n -= Tn * (n * Tn).sum(1, keepdims=True); n /= np.linalg.norm(n, axis=1, keepdims=True)
    b = np.cross(Tn, n); ph = np.linspace(0, 2 * math.pi, V, endpoint=False)
    co = np.sign(np.cos(ph)) * np.abs(np.cos(ph)) ** E; si = np.sign(np.sin(ph)) * np.abs(np.sin(ph)) ** E
    rr = (r * taper)[:, None]; sink = ((1 - taper) * r)[:, None]
    return (C[:, None] + n[:, None] * (rr * co - sink)[..., None] + b[:, None] * (rr * si)[..., None]).reshape(-1, 3)


def cylinder(p, n=180):
    th = np.linspace(0, 2 * math.pi, n, endpoint=False); h = p['h']; out = []
    for y, r in ((-h / 2, p.get('rb', p['r'])), (h / 2, p['r'])):
        for k in np.linspace(0, 1, 2): out.append(np.stack([r * np.sin(th), np.full(n, y), r * np.cos(th)], 1))
    return np.vstack(out + [np.stack([p['r'] * np.sin(th) * t, np.full(n, y), p['r'] * np.cos(th) * t], 1) for y in (-h / 2, h / 2) for t in (0.5,)])


def torus(p, U=180, V=24):
    u = np.linspace(0, 2 * math.pi, U)[:, None]; v = np.linspace(0, 2 * math.pi, V)[None]; R_, t = p['r'], p['tube']
    return np.stack([((R_ + t * np.cos(v)) * np.cos(u)).ravel(), (t * np.sin(v) + 0 * u).ravel(), ((R_ + t * np.cos(v)) * np.sin(u)).ravel()], 1)


def sphere(p, n=60):
    a, b = np.meshgrid(np.linspace(0, math.pi, n), np.linspace(0, 2 * math.pi, n)); r = p['r']
    return np.stack([(r * np.sin(a) * np.cos(b)).ravel(), (r * np.cos(a)).ravel(), (r * np.sin(a) * np.sin(b)).ravel()], 1)


def glb_alpha_mask(path_, project_, size_, turn_, W_, H_):
    """what a GLB really shows from the camera: its triangles filled, each pixel kept only where the texture's alpha passes the material's cutoff
    (alphaMode MASK: tools/gen_relief.py cuts the outline in the texture, finer than the mesh grid). Falls back to plain triangles without alpha."""
    import io, struct
    b = open(path_, 'rb').read(); n = struct.unpack('<I', b[12:16])[0]; js = json.loads(b[20:20 + n]); bin_ = b[20 + n + 8:]
    def acc(i, cols):
        a = js['accessors'][i]; bv = js['bufferViews'][a['bufferView']]; dt = {5126: '<f4', 5125: '<u4', 5123: '<u2', 5121: '<u1'}[a['componentType']]
        return np.frombuffer(bin_, dtype=dt, count=a['count'] * cols, offset=bv.get('byteOffset', 0) + a.get('byteOffset', 0)).reshape(a['count'], cols).astype(float)
    out = np.zeros((H_, W_), bool)
    for node in js.get('nodes', [{'mesh': 0}]):
        if 'mesh' not in node: continue
        for prim in js['meshes'][node['mesh']]['primitives']:
            V = acc(prim['attributes']['POSITION'], 3); I = acc(prim['indices'], 1).astype(int).reshape(-1, 3)
            if turn_: c_, s_ = math.cos(turn_), math.sin(turn_); V = V @ np.array([[c_, 0, s_], [0, 1, 0], [-s_, 0, c_]]).T
            q = project_(V * size_); mat = js['materials'][prim.get('material', 0)] if js.get('materials') else {}
            tex = mat.get('pbrMetallicRoughness', {}).get('baseColorTexture'); alpha = None
            if mat.get('alphaMode') == 'MASK' and tex is not None and 'TEXCOORD_0' in prim['attributes']:
                img = js['images'][js['textures'][tex['index']]['source']]; bv = js['bufferViews'][img['bufferView']]
                pic = Image.open(io.BytesIO(bin_[bv.get('byteOffset', 0):bv.get('byteOffset', 0) + bv['byteLength']]))
                if pic.mode in ('RGBA', 'LA'): alpha = np.array(pic.getchannel('A')).astype(float) / 255; UV = acc(prim['attributes']['TEXCOORD_0'], 2); cut = mat.get('alphaCutoff', 0.5)
            for tri in I:                                              # small triangles: fill each one's box with barycentric weights
                P3 = q[tri]; x0, y0 = np.floor(P3.min(0)).astype(int); x1, y1 = np.ceil(P3.max(0)).astype(int)
                x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, W_ - 1), min(y1, H_ - 1)
                if x1 < x0 or y1 < y0 or (x1 - x0) * (y1 - y0) > 250000: continue
                yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1] + 0.5; (ax, ay), (bx, by), (cx, cy) = P3; den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
                if abs(den) < 1e-9: continue
                w0 = ((by - cy) * (xx - cx) + (cx - bx) * (yy - cy)) / den; w1 = ((cy - ay) * (xx - cx) + (ax - cx) * (yy - cy)) / den; w2 = 1 - w0 - w1
                inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
                if alpha is not None:
                    uv = w0[..., None] * UV[tri[0]] + w1[..., None] * UV[tri[1]] + w2[..., None] * UV[tri[2]]
                    ti = np.clip((uv[..., 1] * alpha.shape[0]).astype(int), 0, alpha.shape[0] - 1); tj = np.clip((uv[..., 0] * alpha.shape[1]).astype(int), 0, alpha.shape[1] - 1)
                    inside &= alpha[ti, tj] >= cut
                out[y0:y1 + 1, x0:x1 + 1] |= inside
    return out


def glb_points(path_, tris=None):
    """every vertex of a GLB, with its node's translation, rotation and scale (one level, enough for tools/gen_relief.py files); tris: a list that gets the triangles"""
    import struct
    b = open(path_, 'rb').read(); n = struct.unpack('<I', b[12:16])[0]; js = json.loads(b[20:20 + n]); bin_ = b[20 + n + 8:]
    pts = []
    for node in js.get('nodes', [{'mesh': 0}]):
        if 'mesh' not in node: continue
        for prim in js['meshes'][node['mesh']]['primitives']:
            acc = js['accessors'][prim['attributes']['POSITION']]; bv = js['bufferViews'][acc['bufferView']]
            off = bv.get('byteOffset', 0) + acc.get('byteOffset', 0); stride = bv.get('byteStride', 12)
            raw = np.frombuffer(bin_, dtype=np.uint8, count=stride * acc['count'], offset=off).reshape(acc['count'], stride)[:, :12]
            v = raw.copy().view('<f4').reshape(-1, 3).astype(float)
            if 'scale' in node: v *= np.array(node['scale'])
            if 'rotation' in node:
                x, y, z, w = node['rotation']; Rm = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]); v = v @ Rm.T
            if 'translation' in node: v += np.array(node['translation'])
            if tris is not None and 'indices' in prim:
                ia = js['accessors'][prim['indices']]; ib = js['bufferViews'][ia['bufferView']]; dt = {5121: '<u1', 5123: '<u2', 5125: '<u4'}[ia['componentType']]
                idx = np.frombuffer(bin_, dtype=dt, count=ia['count'], offset=ib.get('byteOffset', 0) + ia.get('byteOffset', 0)).astype(int)
                tris.append(idx.reshape(-1, 3) + sum(len(q_) for q_ in pts))
            pts.append(v)
    return np.vstack(pts)


def boundary(m):
    """the outline of a filled shape, in order (Moore neighbour tracing): no extra library needed"""
    ys, xs = np.where(m); i = np.lexsort((xs, ys))[0]; start = (int(ys[i]), int(xs[i]))
    N = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]; inside = lambda p_: 0 <= p_[0] < m.shape[0] and 0 <= p_[1] < m.shape[1] and m[p_]
    out, cur, d = [start], start, 6
    for _ in range(int(m.sum()) * 4):
        for k in range(8):
            dd = (d + k) % 8; nb = (cur[0] + N[dd][0], cur[1] + N[dd][1])
            if inside(nb): cur, d = nb, (dd + 5) % 8; break
        if cur == start: break
        out.append(cur)
    return out


def stadium(p, n=360):
    """builder 'stadium': an oval with straight sides (half straight part a, end radius r), height h from 0; its outline top and bottom, filled"""
    a, r, h = p['a'], p['r'], p['h']; t = np.linspace(-math.pi / 2, math.pi / 2, n // 2)
    ring = np.r_[np.c_[a + r * np.cos(t), r * np.sin(t)], np.c_[-a - r * np.cos(t), -r * np.sin(t)]]
    pts = [np.c_[ring[:, 0] * k, np.full(len(ring), y), -ring[:, 1] * k] for y in np.linspace(0, h, 6) for k in np.linspace(0, 1, 12)]
    return np.vstack(pts)


def roundbox(p, n=40):
    """builder 'roundbox': rounded rectangle w x d, corner r, height h, top optionally cut by 'slant' [y at -x, y at +x]; points over its whole surface"""
    w, d, r, h = p['w'], p['d'], p['r'], p['h']; ring = []
    for cx, cz, a0 in ((w / 2 - r, d / 2 - r, 0), (-(w / 2 - r), d / 2 - r, math.pi / 2), (-(w / 2 - r), -(d / 2 - r), math.pi), (w / 2 - r, -(d / 2 - r), 1.5 * math.pi)):
        for t in np.linspace(a0, a0 + math.pi / 2, n): ring.append((cx + r * math.cos(t), cz + r * math.sin(t)))
    ring = np.array(ring); out = []
    for k in np.linspace(0, 1, 10):
        for x, z in ring * k if k > 0 else ring[:1] * 0:
            top = p['slant'][0] + (p['slant'][1] - p['slant'][0]) * (x / w + 0.5) if p.get('slant') else h
            out += [[x, y, z] for y in np.linspace(0, top, 24)]
    return np.array(out)


def hearts(p):
    """builder 'hearts': each heart as a filled disc of its width and thickness, turned as placed"""
    w, t = p['w'], p['t']; a, b = np.meshgrid(np.linspace(-0.5, 0.5, 9), np.linspace(-0.5, 0.5, 9)); disc = np.c_[a.ravel(), b.ravel()][np.hypot(a.ravel(), b.ravel()) <= 0.5] * w
    base = np.vstack([np.c_[disc, np.full(len(disc), zz)] for zz in (-t / 2, 0, t / 2)]); out = []
    for x, y, z, rx, ry, rz, sc in p['inst']:
        out.append((base * sc) @ euler_xyz(rx, ry, rz).T + [x, y, z])
    return np.vstack(out)


SHAPES = {'roundbox': roundbox, 'hearts': hearts, 'lathe': lathe, 'rope': rope, 'path': path, 'cylinder': cylinder, 'torus': torus, 'sphere': sphere, 'stadium': stadium}
objs = sorted({k.rsplit('_', 1)[0] for k in TR}); size = R.get('size', 1)
masks, skipped = {}, set()
for o in objs:
    m = np.zeros((H, W), bool); mine = [p for p in R['parts'] if p.get('material') == o]; whole = not mine
    if whole: mine = R['parts']
    if whole and R.get('model'):                                   # the figure itself: its GLB, in candle units ("modelRaw"), turned by modelTurn
        if not R.get('modelRaw'): skipped.add('model (not modelRaw: scaled at load, not drawn)')
        else:
            m |= glb_alpha_mask(os.path.join(ROOT, R['model']), project, size, R.get('modelTurn', 0), W, H)   # triangles filled, cut by the texture's alpha like three.js
    for p in mine:
        if p['shape'] not in SHAPES: skipped.add(p['shape']); continue
        pts = SHAPES[p['shape']](p); rx, ry, rz = p.get('rot', [0, 0, 0])
        pts = (pts @ euler_xyz(rx, ry, rz).T + np.array(p.get('pos', [0, 0, 0]))) * size
        q = np.round(project(pts)).astype(int); ok = (q[:, 0] >= 0) & (q[:, 0] < W) & (q[:, 1] >= 0) & (q[:, 1] < H); m[q[ok, 1], q[ok, 0]] = True
    masks[o] = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=1 if R.get('model') and whole else 3))

if SNAP:                                                           # a closed outline for a figure: the 3D outline, each point slid to the photo's edge
    m = masks[gname]; lab, n = ndi.label(m); m = lab == (np.argmax(np.bincount(lab.ravel())[1:]) + 1)
    c = np.array(boundary(m), float)[::3]                          # (row, col), in order round the outline
    Lg = ndi.gaussian_filter(np.array(im.convert('L')).astype(float), 1.2); gy_, gx_ = np.gradient(Lg); gm = np.hypot(gx_, gy_)
    t = np.gradient(c, axis=0); nrm = np.stack([-t[:, 1], t[:, 0]], 1); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
    reach = int(os.environ.get('SNAP', 25)); off = np.arange(-reach, reach + 1); snapped = []   # far enough that the photo's edge wins, not the 3D's
    for (r, q), (nr, nq) in zip(c, nrm):
        rr = np.clip(np.round(r + off * nr).astype(int), 0, H - 1); qq = np.clip(np.round(q + off * nq).astype(int), 0, W - 1)
        k = int(np.argmax(gm[rr, qq] - 0.08 * np.abs(off))); snapped.append(off[k])
    d = ndi.median_filter(np.array(snapped, float), 7, mode='wrap'); d = ndi.gaussian_filter1d(d, 2, mode='wrap')
    poly = c + d[:, None] * nrm
    json.dump({gname + '_poly': [[round(float(q), 1), round(float(r), 1)] for r, q in poly]}, open(os.path.join(HERE, 'fit', f'trace-{gname}.json'), 'w'))
    A2 = np.array(im); e = m & ~ndi.binary_erosion(m); A2[e] = (255, 0, 0)
    for r, q in poly: A2[int(round(r)), int(round(q))] = (0, 230, 0)
    ys, xs = np.where(m); y0, y1, x0, x1 = max(0, ys.min() - 20), min(H, ys.max() + 20), max(0, xs.min() - 20), min(W, xs.max() + 20)
    Image.fromarray(A2).crop((x0, y0, x1, y1)).resize(((x1 - x0) * 2, (y1 - y0) * 2), Image.NEAREST).save(os.path.join(HERE, 'fit', f'snap-{gname}.png'))
    print(f'snapped outline: tools/fit/trace-{gname}.json ({len(poly)} points); LOOK at tools/fit/snap-{gname}.png (green = photo edge found, red = 3D)'); sys.exit()

if GUIDES:                                                         # rough guides from the 3D outline, every 10 rows, for tools/trace_outline.py
    m = masks[gname]; filled = m.any(1); lab, n = ndi.label(filled); big = np.argmax(np.bincount(lab)[1:]) + 1   # the longest unbroken run of rows
    rows = np.where(lab == big)[0]; g = {gname + '_L': [], gname + '_R': []}
    for y in list(range(rows.min() + 2, rows.max() - 2, 10)) + [rows.max() - 2]:
        xs = np.where(m[y])[0]; g[gname + '_L'].append([int(y), int(xs.min())]); g[gname + '_R'].append([int(y), int(xs.max())])
    json.dump({'photo': photo_arg, 'window': 14, 'step': 2, 'guides': g, 'fix': {}, 'notes': {}}, open(os.path.join(HERE, 'fit', f'trace-{gname}.cfg.json'), 'w'), indent=1)
    print(f'guides written: tools/fit/trace-{gname}.cfg.json (from the 3D outline: wherever the 3D is wrong by more than the window, fix the guide by hand)'); sys.exit()

A = np.array(im); report = {}; allx = []; ally = []
for o in objs:
    if o + '_poly' in TR:                                          # a figure: closed outline
        from PIL import ImageDraw as _D
        poly = TR[o + '_poly']; pm = Image.new('L', (W, H), 0); _D.Draw(pm).polygon([tuple(p_) for p_ in poly], fill=1); photo = np.array(pm) > 0
        m = masks[o]; iou = (m & photo).sum() / (m | photo).sum(); edge3d = m & ~ndi.binary_erosion(m); dist = ndi.distance_transform_edt(~edge3d)
        dd = np.array([dist[min(H - 1, int(round(y))), min(W - 1, int(round(x)))] for x, y in poly]); e3, e6 = (dd <= 3).mean(), (dd <= 6).mean()
        far = [(x, y, d_) for (x, y), d_ in zip(poly, dd) if d_ > 6]
        report[o] = {'edges_3px': round(100 * e3, 1), 'edges_6px': round(100 * e6, 1), 'overlap': round(100 * iou, 1), 'MATCH': round(50 * (e3 + iou), 1),
                     'off_more_than_6px': f'{len(far)} of {len(poly)} outline points' + (f', worst near x {int(max(far, key=lambda f_: f_[2])[0])}, row {int(max(far, key=lambda f_: f_[2])[1])} ({int(max(f_[2] for f_ in far))} px)' if far else '')}
        A[edge3d] = (255, 0, 0)
        for x, y in poly: A[int(round(y)), int(round(x))] = (0, 230, 0)
        allx += [min(p_[0] for p_ in poly), max(p_[0] for p_ in poly)]; ally += [min(p_[1] for p_ in poly), max(p_[1] for p_ in poly)]
        continue
    Lt, Rt = dict(map(tuple, TR[o + '_L'])), dict(map(tuple, TR[o + '_R'])); rows = sorted(set(Lt) & set(Rt)); m = masks[o]
    photo = np.zeros_like(m)
    for y in rows: photo[y, int(round(Lt[y])):int(round(Rt[y])) + 1] = True
    ys = np.where(m.any(1))[0]; band = (np.arange(H) >= min(rows[0], ys.min())) & (np.arange(H) <= max(rows[-1], ys.max()))
    inter = (m & photo)[band].sum(); union = (m | photo)[band].sum(); iou = inter / union
    miss = []
    for side, Tside in (('L', Lt), ('R', Rt)):
        for y, x in sorted(Tside.items()):
            xs = np.where(m[y])[0]
            miss.append((abs((xs.min() if side == 'L' else xs.max()) - x) if len(xs) else 99, y, side))
    d = np.array([q[0] for q in miss]); e3, e6 = (d <= 3).mean(), (d <= 6).mean()
    bad, run = [], None                                            # stretches more than 6 px off
    for v, y, s in sorted(miss, key=lambda q: (q[2], q[1])):
        if v > 6:
            if run and run[2] == s and y - run[1] <= 2: run[1] = y; run[3] = max(run[3], v)
            else:
                if run: bad.append(run)
                run = [y, y, s, v]
    if run: bad.append(run)
    report[o] = {'edges_3px': round(100 * e3, 1), 'edges_6px': round(100 * e6, 1), 'overlap': round(100 * iou, 1), 'MATCH': round(50 * (e3 + iou), 1),
                 'off_more_than_6px': [f'{s} rows {a}-{b} (up to {int(v)} px)' for a, b, s, v in bad]}
    edge = m & ~ndi.binary_erosion(m); A[edge] = (255, 0, 0)
    for y in rows: A[y, int(round(Lt[y]))] = A[y, int(round(Rt[y]))] = (0, 230, 0)
    allx += [min(Lt.values()), max(Rt.values())]; ally += [rows[0], rows[-1]]
x0, x1, y0, y1 = max(0, int(min(allx)) - 30), min(W, int(max(allx)) + 30), max(0, int(min(ally)) - 30), min(H, int(max(ally)) + 40)
Image.fromarray(A).crop((x0, y0, x1, y1)).resize(((x1 - x0) * 2, (y1 - y0) * 2), Image.NEAREST).save(os.path.join(HERE, 'fit', f'match-{name}.png'))
total = round(sum(r['MATCH'] for r in report.values()) / len(report), 1)
print(json.dumps(report, indent=1)); print(f'MATCH {total}%  (edges within 3 px and silhouette overlap, averaged)' + (f'  | not drawn: {sorted(skipped)}' if skipped else ''))
