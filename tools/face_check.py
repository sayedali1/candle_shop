"""Looks at a recipe's blended body through the photo's camera, in Python, without a browser, and lays it over the photo's face crop.
Green = where the body is, yellow line = the marked head region, cyan line = the marked near ear, red dots = where eyes and nose should be.
Prints how much of the head region is covered and how much sticks out. Fast (a few seconds), so use it for every change of the face.
Run:  python tools/face_check.py [recipe.json]        Writes tools/fit/face-check.png"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fit_face as ff
import fit_pose as fp

rec = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'recipes', 'zz-lying.json')))
blob = [p for p in rec['parts'] if p['shape'] == 'blob'][0]
k = blob.get('k', 0.07); els = blob['els']
cam = json.load(open(os.path.join(HERE, 'fit', 'pose.json')))['camera']
cx = np.array([cam['yaw'], cam['pitch'], cam['fov'], *cam['target']])
X0, X1, Y0, Y1, DS = ff.X0, ff.X1, ff.Y0, ff.Y1, 1
fp.X0, fp.X1, fp.Y0, fp.Y1, fp.DS = X0, X1, Y0, Y1, DS
P, D = fp.cam_rays(cx)                                   # world rays
shape = D.shape[:2]
ct, st = math.cos(-fp.TURN), math.sin(-fp.TURN)
o = np.array([P[0] * ct + P[2] * st, P[1], -P[0] * st + P[2] * ct]) / fp.SIZE        # camera in candle space
d = D.reshape(-1, 3); dl = np.stack([d[:, 0] * ct + d[:, 2] * st, d[:, 1], -d[:, 0] * st + d[:, 2] * ct], 1)


def dist(pts):
    dd = None
    for e in els:
        r = np.array(e['r']); c = np.array(e['c']); a = e['rot'][1]; ca, sa = math.cos(a), math.sin(a)
        q = pts - c; q = np.stack([ca * q[:, 0] - sa * q[:, 2], q[:, 1], sa * q[:, 0] + ca * q[:, 2]], 1)
        u = q / r; k0 = np.linalg.norm(u, axis=1); k1 = np.linalg.norm(u / r, axis=1)
        v = np.where(k1 > 1e-9, k0 * (k0 - 1) / np.maximum(k1, 1e-9), -r.min())
        if dd is None: dd = v
        else:
            h = np.maximum(k - np.abs(dd - v), 0) / k; dd = np.minimum(dd, v) - h * h * k * 0.25
    return dd


t = np.zeros(len(dl)); alive = np.ones(len(dl), bool); hit = np.zeros(len(dl), bool)
for _ in range(90):
    idx = np.where(alive)[0]
    if not len(idx): break
    dd = dist(o + dl[idx] * t[idx, None])
    done = dd < 0.003; hit[idx[done]] = True; alive[idx[done]] = False
    t[idx] += np.maximum(dd * 0.9, 0.003); alive[idx[t[idx] > 12]] = False
M = hit.reshape(shape)
PH, PE = ff.poly_mask(ff.HEAD_POLY) if DS == ff.DS else None, None
from PIL import ImageDraw as _D
def pm(poly):
    im = Image.new('L', (fp.W, fp.H), 0); _D.Draw(im).polygon(poly, fill=255); return (np.array(im) > 0)[Y0:Y1:DS, X0:X1:DS]
PH, PE = pm(ff.HEAD_POLY), pm(ff.EAR_POLY)
spill = (M & ~(PH | PE)).sum() / max(M.sum(), 1); cover = (PH & M).sum() / PH.sum()
print(f'head region covered {cover * 100:.0f}%, {spill * 100:.0f}% of the 3D sticks out of the marked head+ear')
photo = np.array(Image.open(os.path.join(HERE, '..', 'brief', 'ref-poodle-candles.webp')).convert('RGB').crop((X0, Y0, X1, Y1))).astype(np.float32) / 255
pv = photo.copy(); pv[M] = pv[M] * 0.45 + np.array([0.0, 0.55, 0.0])
im = Image.fromarray((np.clip(pv, 0, 1) * 255).astype(np.uint8)); dr = ImageDraw.Draw(im)
for poly, col in ((ff.HEAD_POLY, (255, 255, 0)), (ff.EAR_POLY, (0, 255, 255))):
    pts = [(x - X0, y - Y0) for x, y in poly]; dr.line(pts + [pts[0]], fill=col, width=1)
for nm, (x, y) in {'eye': (412, 568), 'eye2': (442, 563), 'nose': (450, 597)}.items(): dr.ellipse([x - X0 - 2, y - Y0 - 2, x - X0 + 2, y - Y0 + 2], fill=(255, 0, 0))
im.resize((im.width * 3, im.height * 3), Image.LANCZOS).save(os.path.join(HERE, 'fit', 'face-check.png'))
