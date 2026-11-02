"""Draws the knot pair's exact 3D outline on the photo, so every wrong edge shows.
The shapes are rebuilt here the same way candle-builder.js builds them (lathe with flutes and bend, rope bands with twist, swell, square, tuck, lift,
turned and placed as the recipe says), projected through the photo's camera (gen_knot.py), filled, and their outline drawn.
Run:  python tools/knot_edges.py      Writes tools/fit/edges.png (2x: photo with the 3D outline in red) and prints, row by row, how far each edge is off."""
import json, math, os, runpy
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
g = runpy.run_path(os.path.join(HERE, 'gen_knot.py'), run_name='edges')
project, G, W, H = g['project'], g['G'], g['W'], g['H']
R = json.load(open(os.path.join(ROOT, 'recipes', '13-knot-pair.json'), encoding='utf-8'))


def euler_xyz(rx, ry, rz):
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    X = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]); Y = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]); Z = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return X @ Y @ Z                                                 # three.js 'XYZ' order


def lathe(p, n=720):
    pr = np.array(p['profile'][:-2]); phi = np.linspace(0, 2 * math.pi, n, endpoint=False)
    x = pr[:, :1] * np.sin(phi); z = pr[:, :1] * np.cos(phi); y = np.repeat(pr[:, 1:2], n, 1)
    if p.get('ribs'):
        a = np.arctan2(z, x) * p['ribs']['count']; d = p['ribs']['depth']
        f = 1 - d + d * np.abs(np.cos(a / 2)) if p['ribs'].get('shape') == 'flute' else 1 + d * np.cos(a)
        x, z = x * f, z * f
    if p.get('bend'):
        B = np.array(p['bend']); x = x + np.interp(y, B[:, 0], B[:, 1])
    return np.stack([x.ravel(), y.ravel(), z.ravel()], 1)


def rope(p, U=720, V=48):
    A = p.get('arc', 2 * math.pi); part = A < 6.28; S, T, D = p.get('strands', 3), p.get('twist', 40), p.get('depth', 0.14); E = p.get('square', 1)
    u = np.linspace(0, 1, U + 1)[:, None]; ph = np.linspace(0, 2 * math.pi, V, endpoint=False)[None]
    th = p.get('start', 0) + u * A; c, s = np.cos(th), np.sin(th)
    e = np.clip((u - 0.7) / 0.3, 0, 1); y0 = p.get('rise', 0) * u + p.get('lift', 0) * e * e * (3 - 2 * e)
    taper = np.sqrt(np.minimum(1, np.minimum(u, 1 - u) / 0.15)) if part else np.ones_like(u)
    rr = taper * p['tube'] * (1 + p.get('swell', 0) * c) * (1 - D + D * np.abs(np.cos((S * ph + T * th) / 2)))
    co = np.sign(np.cos(ph)) * np.abs(np.cos(ph)) ** E; si = np.sign(np.sin(ph)) * np.abs(np.sin(ph)) ** E
    out = p['r'] - p.get('tuck', 0) * (1 - taper) * p['tube'] + rr * co * p.get('flat', 1)
    return np.stack([(out * c).ravel(), (y0 + rr * si).ravel(), (out * s).ravel()], 1)


def catmull(Q, n=60):
    """three.js CatmullRomCurve3, 'centripetal', not closed: the end points are mirrored, each segment is a centripetal Catmull-Rom piece"""
    P = np.vstack([2 * Q[0] - Q[1], Q, 2 * Q[-1] - Q[-2]]); out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        d0, d1, d2 = [max(np.sum((b_ - a_) ** 2) ** 0.25, 1e-4) for a_, b_ in ((p0, p1), (p1, p2), (p2, p3))]
        t1 = ((p1 - p0) / d0 - (p2 - p0) / (d0 + d1) + (p2 - p1) / d1) * d1; t2 = ((p2 - p1) / d1 - (p3 - p1) / (d1 + d2) + (p3 - p2) / d2) * d1
        for u in np.linspace(0, 1, n, endpoint=False):
            u2, u3 = u * u, u * u * u
            out.append((2 * u3 - 3 * u2 + 1) * p1 + (u3 - 2 * u2 + u) * t1 + (-2 * u3 + 3 * u2) * p2 + (u3 - u2) * t2)
    out.append(Q[-1]); return np.array(out)


def path(p, U=1200, V=48):
    Q = np.array(p['points']); C = catmull(Q[:, :3]); seg = np.linalg.norm(np.diff(C, axis=0), axis=1); t = np.r_[0, np.cumsum(seg)]
    k = np.linspace(0, len(Q) - 1, len(C)); rad_all = np.interp(k, np.arange(len(Q)), Q[:, 3])
    Tn = np.gradient(C, axis=0); Tn /= np.linalg.norm(Tn, axis=1, keepdims=True); d = t
    r = rad_all; u = t / d[-1]; taper = np.sqrt(np.minimum(1, np.minimum(u, 1 - u) / 0.08)); E = p.get('square', 1)
    n = np.stack([C[:, 0], np.zeros(len(C)), C[:, 2]], 1); n /= np.linalg.norm(n, axis=1, keepdims=True); n -= Tn * (n * Tn).sum(1, keepdims=True); n /= np.linalg.norm(n, axis=1, keepdims=True)
    b = np.cross(Tn, n); ph = np.linspace(0, 2 * math.pi, V, endpoint=False)
    co = np.sign(np.cos(ph)) * np.abs(np.cos(ph)) ** E; si = np.sign(np.sin(ph)) * np.abs(np.sin(ph)) ** E
    rr = (r * taper)[:, None]; sink = ((1 - taper) * r)[:, None]
    pts = C[:, None] + n[:, None] * (rr * co - sink)[..., None] + b[:, None] * (rr * si)[..., None]
    return pts.reshape(-1, 3)


masks = {}
for name in ('tall', 'short'):
    m = np.zeros((H, W), bool)
    for p in R['parts']:
        if p['material'] != name: continue
        pts = lathe(p) if p['shape'] == 'lathe' else path(p) if p['shape'] == 'path' else rope(p)
        rx, ry, rz = p.get('rot', [0, 0, 0]); pts = pts @ euler_xyz(rx, ry, rz).T + np.array(p['pos']) + np.array([0, G, 0])
        q = np.round(project(pts)).astype(int); ok = (q[:, 0] >= 0) & (q[:, 0] < W) & (q[:, 1] >= 0) & (q[:, 1] < H)
        m[q[ok, 1], q[ok, 0]] = True
    masks[name] = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=3))

im = Image.open(os.path.join(ROOT, 'brief', 'ref-knot.jpg')).convert('RGB'); A = np.array(im)
for name, col in (('tall', (255, 0, 0)), ('short', (0, 120, 255))):
    edge = masks[name] & ~ndi.binary_erosion(masks[name])
    A[edge] = col
crop = Image.fromarray(A).crop((230, 370, 470 + 210, 1090)); crop = crop.resize((crop.width * 2, crop.height * 2), Image.NEAREST)
crop.save(os.path.join(HERE, 'fit', 'edges.png'))
for name in ('tall', 'short'):
    m = masks[name]; rows = np.where(m.any(1))[0]
    print(name, 'rows', rows.min(), '-', rows.max())
    for y in range(rows.min(), rows.max() + 1, 10):
        xs = np.where(m[y])[0]
        if len(xs): print(f'  {y}: {xs.min()}-{xs.max()}')


# where the photo's own edge is, near each 3D edge: the strongest brightness step within 15 px (rows where the two candles touch are skipped)
L = ndi.gaussian_filter(np.array(im.convert('L')).astype(float), 1.2); gx = np.zeros_like(L); gx[:, 1:-1] = L[:, 2:] - L[:, :-2]
print('row | 3D left, photo left (diff) | 3D right, photo right (diff)')
for name in ('tall', 'short'):
    m = masks[name]; rows = np.where(m.any(1))[0]; print(name)
    for y in range(rows.min() + 4, rows.max() - 8, 8):
        xs = np.where(m[y])[0]; l3, r3 = xs.min(), xs.max(); out = []
        for x3, sign in ((l3, 1), (r3, -1)):
            win = np.arange(x3 - 15, x3 + 16); s = gx[y, win] * sign     # wax is brighter than what is behind it? not always: take the strongest step either way
            xp = int(win[np.argmax(np.abs(gx[y, win]))]); out.append((x3, xp, xp - x3))
        print(f'  {y}: L {out[0][0]} vs {out[0][1]} ({out[0][2]:+d}) | R {out[1][0]} vs {out[1][1]} ({out[1][2]:+d})')
