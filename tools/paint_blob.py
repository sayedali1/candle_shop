"""Paints a baked body with the photo's own colours (the biggest fidelity lever in the img2threejs notes, done our way).
Every point of the body that the photo's camera can see takes its colour from the photo pixel it lands on; points it cannot see (the back, hidden parts) keep the plain wax colour.
The result is a colour MULTIPLIER per point (128 = unchanged), so the recipe's wax colour still decides the overall look and the photo adds what a painter would add: the cream muzzle,
the darker rims around the eyes, the shading inside the ear. Contrast is softened so it stays wax, not a photograph.
Run:  python tools/paint_blob.py assets/models/zz-lying.bin assets/models/zz-lying.col [contrast 0.85]"""
import math, os, struct, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fit_pose as fp

binp, outp = sys.argv[1], sys.argv[2]
CONTRAST = float(sys.argv[3]) if len(sys.argv) > 3 else 0.85
buf = open(binp, 'rb').read()
magic, n, ni, isz = struct.unpack('<4I', buf[:16])
mn = np.array(struct.unpack('<3f', buf[16:28])); rg = np.array(struct.unpack('<3f', buf[28:40]))
up = lambda x: (x + 3) & ~3
oPos = 48; oNor = oPos + up(n * 6)
pos = np.frombuffer(buf, '<u2', n * 3, oPos).reshape(n, 3) / 65535.0 * rg + mn
nor = np.frombuffer(buf, 'i1', n * 3, oNor).reshape(n, 3).astype(float) / 127.0
nor /= np.linalg.norm(nor, axis=1, keepdims=True) + 1e-9

import json
cam = json.load(open(os.path.join(HERE, 'fit', 'pose.json')))['camera']
yaw, pitch, fov = cam['yaw'], cam['pitch'], cam['fov']; T = np.array(cam['target']); r = cam['dist']
P = T + r * np.array([math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch)])
f = (T - P) / np.linalg.norm(T - P); right = np.cross(f, [0, 1, 0]); right /= np.linalg.norm(right); upv = np.cross(right, f)
ct, st = math.cos(fp.TURN), math.sin(fp.TURN)
world = fp.SIZE * np.stack([pos[:, 0] * ct + pos[:, 2] * st, pos[:, 1], -pos[:, 0] * st + pos[:, 2] * ct], 1)
nw = np.stack([nor[:, 0] * ct + nor[:, 2] * st, nor[:, 1], -nor[:, 0] * st + nor[:, 2] * ct], 1)
W, H = fp.W, fp.H; t = math.tan(math.radians(fov) / 2); asp = W / H
v = world - P; z = v @ f; xr = v @ right; yu = v @ upv
u = (xr / (z * t * asp) + 1) / 2 * W; w_ = (1 - yu / (z * t)) / 2 * H
facing = -(nw * (v / np.linalg.norm(v, axis=1, keepdims=True))).sum(1)         # how squarely the surface looks at the camera

# a depth map from the points themselves (each splatted a few pixels wide): a point behind another is hidden
zb = np.full((H, W), 1e9)
iu, iv = np.round(u).astype(int), np.round(w_).astype(int)
for dx in (-2, -1, 0, 1, 2):
    for dy in (-2, -1, 0, 1, 2):
        xx, yy = np.clip(iu + dx, 0, W - 1), np.clip(iv + dy, 0, H - 1)
        np.minimum.at(zb, (yy, xx), z)
visible = (z <= zb[np.clip(iv, 0, H - 1), np.clip(iu, 0, W - 1)] + 0.03) & (u >= 0) & (u < W) & (w_ >= 0) & (w_ < H)

photo = np.array(Image.open(os.path.join(HERE, '..', 'brief', 'ref-poodle-candles.webp')).convert('RGB')).astype(float) / 255
blur = np.stack([ndi.gaussian_filter(photo[..., c], 2.0) for c in range(3)], -1)
col = np.stack([ndi.map_coordinates(blur[..., c], [w_, u], order=1, mode='nearest') for c in range(3)], 1)
wgt = np.clip((facing - 0.1) / 0.4, 0, 1) * visible
ref = (col[wgt > 0.5].mean(0)) if (wgt > 0.5).any() else col.mean(0)
mult = col / ref                                                             # relative to the average visible colour: the recipe's wax colour keeps the overall tone
mult = 1 + CONTRAST * (mult - 1)
mult = np.clip(mult, 0.45, 1.6)
out = 1 + wgt[:, None] * (mult - 1)
mp = os.path.join(HERE, 'fit', 'mouth-path.json')                              # the mouth line (tools/gen_head.py): the wax is darkened along it, whatever the photo's colour there
if os.path.exists(mp):
    mj = json.load(open(mp)); pts = np.array(mj['points']); rad = 0.14 * mj['u']
    dmin = np.full(n, 1e9)
    for a, b in zip(pts[:-1], pts[1:]):
        ab = b - a; tt = np.clip(((pos - a) @ ab) / (ab @ ab), 0, 1); dmin = np.minimum(dmin, np.linalg.norm(pos - (a + tt[:, None] * ab), axis=1))
    line = np.clip(1 - dmin / rad, 0, 1) ** 0.7
    out = out * (1 - 0.55 * line)[:, None]; print(int((line > 0.3).sum()), 'points darkened for the mouth line')
open(outp, 'wb').write(np.clip(np.round(out * 128), 0, 255).astype(np.uint8).tobytes())
print(f'{n} points, {int((wgt > 0.5).sum())} painted from the photo, reference colour {np.round(ref, 2).tolist()} -> {outp}')
