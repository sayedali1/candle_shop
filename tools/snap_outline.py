"""Turns a rough hand outline (a closed polygon of photo pixels) into a dense, exact one: points every 2 px, each slid along its normal onto the
photo's outermost strong COLOUR edge (from 3 px inside to `reach` px outside) (colour, not brightness: a yellow duck on a white curtain, a white tray on brown wood), smoothed.
Writes tools/fit/<out>.json ({"outline": [...]}, the format tools/gen_relief.py reads) and tools/fit/<out>-tiles.png: the outline on zoomed tiles
all the way round, to check by eye. Wrong stretches: add points to the rough outline there and run it again.
Rough points may be [x, y, 1]: read by hand on a grid; they and the stretch between two of them are not moved.
Run:  python tools/snap_outline.py <photo> <rough outline json> <out name> [reach px]"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
photo_p, rough_p, out = sys.argv[1:4]; reach = int(sys.argv[4]) if len(sys.argv) > 4 else 14
im = Image.open(os.path.join(ROOT, photo_p)).convert('RGB'); A = ndi.gaussian_filter(np.array(im).astype(float), (1.2, 1.2, 0)); H, W = A.shape[:2]
g = np.zeros((H, W))
for c in range(3): gy, gx = np.gradient(A[..., c]); g += gy * gy + gx * gx          # colour edge strength
g = np.sqrt(g)
rough = json.load(open(os.path.join(HERE, 'fit', rough_p))); R0 = rough.get('outline') or rough['outlines'][0]
P = np.array([q[:2] for q in R0], float); LOCK = np.array([len(q) > 2 and q[2] == 1 for q in R0])   # [x, y, 1]: read by hand on a grid, not moved by the snap

# densify: a point every 2 px along the rough outline
seg = np.r_[np.linalg.norm(np.diff(np.vstack([P, P[:1]]), axis=0), axis=1)]; t = np.r_[0, np.cumsum(seg)]; L = t[-1]
s = np.arange(0, L, 2.0); Q = np.stack([np.interp(s, t, np.r_[P[:, 0], P[0, 0]]), np.interp(s, t, np.r_[P[:, 1], P[0, 1]])], 1)
seg_i = np.clip(np.searchsorted(t, s, side='right') - 1, 0, len(P) - 1); locked = LOCK[seg_i] & LOCK[(seg_i + 1) % len(P)]   # between two hand points: locked
area = 0.5 * np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1]); sgn = 1 if area > 0 else -1   # which side is outside
T = np.roll(Q, -1, 0) - np.roll(Q, 1, 0); N = sgn * np.stack([T[:, 1], -T[:, 0]], 1); N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-9
# one pass: from 3 px inside to `reach` px outside, take the OUTERMOST edge at least 60% as strong as the strongest there. The strongest alone would
# pick an inner edge (blue water against the white rim is stronger than the white rim against brown wood)
off = np.arange(-reach if not os.environ.get('OUTER') else -3, reach + 1); best = []
for (x, y), (nx, ny) in zip(Q, N):
    xs = np.clip(np.round(x + off * nx).astype(int), 0, W - 1); ys = np.clip(np.round(y + off * ny).astype(int), 0, H - 1); gv = g[ys, xs]
    if os.environ.get('OUTER'): ok = np.where(gv >= 0.6 * gv.max())[0]; best.append(off[ok[-1]])   # OUTER=1: the outermost strong edge (a clean background only: wood grain fools it)
    else: best.append(off[int(np.argmax(gv - 0.15 * np.abs(off)))])                                 # default: the strongest edge near the rough line
d = np.array(best, float); d[locked] = 0; d = ndi.median_filter(d, 9, mode='wrap'); d = ndi.gaussian_filter1d(d, 2, mode='wrap'); d[locked] = 0
Q = Q + d[:, None] * N
json.dump({'note': f'snapped from {rough_p} by tools/snap_outline.py, checked by eye on {out}-tiles.png', 'outline': [[round(float(x), 1), round(float(y), 1)] for x, y in Q]},
          open(os.path.join(HERE, 'fit', out + '.json'), 'w'))

# tiles all round the outline, 3x, for the eye check: rough outline in red, snapped in green
tiles = []; step = max(1, len(Q) // 12)
for i in range(0, len(Q), step):
    cx, cy = Q[i]; x0, y0 = int(cx) - 40, int(cy) - 40
    c = im.crop((x0, y0, x0 + 80, y0 + 80)).resize((240, 240), Image.LANCZOS); dr = ImageDraw.Draw(c)
    for x, y in P: dr.ellipse([(x - x0) * 3 - 3, (y - y0) * 3 - 3, (x - x0) * 3 + 3, (y - y0) * 3 + 3], outline=(255, 0, 0))
    dr.line([((x - x0) * 3, (y - y0) * 3) for x, y in np.vstack([Q, Q[:1]])], fill=(0, 255, 0), width=2)
    dr.text((3, 3), f'{int(cx)},{int(cy)}', fill=(255, 0, 0)); tiles.append(c)
cols = 4; rows = math.ceil(len(tiles) / cols); sheet = Image.new('RGB', (cols * 244, rows * 244))
for k, c in enumerate(tiles): sheet.paste(c, ((k % cols) * 244, (k // cols) * 244))
sheet.save(os.path.join(HERE, 'fit', out + '-tiles.png')); print(f'{len(Q)} points -> tools/fit/{out}.json; LOOK at tools/fit/{out}-tiles.png')
