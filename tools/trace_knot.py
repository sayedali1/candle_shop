"""Traces both candles' outlines on the knot photo, every row, both sides, as numbers (tools/fit/trace-knot.json).
A dynamic-programming tracer follows the strongest brightness step down each side, moving at most a few px per row, so it cannot jump onto the
window frame or the other candle. Each side starts from a rough guide (the old outline) and searches +-14 px around it.
Every traced side is then drawn on zoomed strips (tools/fit/strip-*.png) to be checked by eye; stretches that are wrong get hand values in FIX.
Run:  python tools/trace_knot.py"""
import json, os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
im = Image.open(os.path.join(ROOT, 'brief', 'ref-knot.jpg')).convert('RGB'); A = np.array(im).astype(float)
L = ndi.gaussian_filter(A.mean(2), 1.0)
gx = np.zeros_like(L); gx[:, 1:-1] = L[:, 2:] - L[:, :-2]

# rough guides: (row, x) points along each side, from the earlier outline; the tracer looks +-14 px around them
GUIDE = {
    'tall_L': [(424, 456), (480, 455), (540, 462), (565, 462), (588, 451), (610, 455), (630, 478), (680, 480), (700, 468), (760, 452), (800, 447), (960, 442), (978, 447)],
    'tall_R': [(424, 646), (480, 645), (540, 625), (580, 602), (595, 600), (620, 622), (650, 634), (680, 631), (700, 616), (760, 628), (800, 631), (960, 626), (978, 624)],
    'short_L': [(556, 258), (600, 261), (640, 270), (670, 283), (700, 270), (725, 268), (745, 275), (765, 286), (800, 277), (850, 267), (950, 262), (1040, 266)],
    'short_R': [(556, 418), (600, 412), (640, 405), (670, 399), (700, 416), (725, 410), (745, 422), (765, 412), (800, 419), (850, 430), (950, 440), (1040, 434)]}
# hand values (straight between) where the tracer is wrong, after checking the strips:
# tall left 424-566: it followed the window frame (x 447). Above row 490 the edge is clear at 450 (tools/fit/tallL-top-contrast.png); below, the window light behind
# looks like wax, so the edge there is the right edge (clean, against the dark book) mirrored about the middle line (549 at the top, 541 at row 700): 454, 460, 467, 478 at rows 504-564.
# tall left 835-978: the short candle stands in front, so the tracer took its edge; the tall's own edge, hidden there, runs straight on from 447 to the foot corner (449).
FIX = {'tall_L': [(424, 484, 450, 451), (484, 504, 451, 454), (504, 524, 454, 460), (524, 544, 460, 467), (544, 566, 467, 478), (835, 970, 447, 446), (970, 978, 446, 449)]}


def trace(name, W_=14, step=2, lam=3.0):
    g = np.array(GUIDE[name]); rows = np.arange(g[0, 0], g[-1, 0] + 1); centre = np.interp(rows, g[:, 0], g[:, 1])
    sign = 1 if name.endswith('L') else -1                         # left side: dark/bright on either side, so use |step|, but prefer the outermost strong step
    off = np.arange(-W_, W_ + 1); n = len(rows); cost = np.zeros((n, len(off))); back = np.zeros((n, len(off)), int)
    for i, y in enumerate(rows):
        xs = np.clip(np.round(centre[i] + off).astype(int), 1, A.shape[1] - 2)
        e = -np.abs(gx[y, xs])
        if i == 0: cost[i] = e; continue
        best = np.full(len(off), np.inf)
        for d in range(-step, step + 1):
            prev = np.roll(cost[i - 1], d) + lam * abs(d)
            if d > 0: prev[:d] = np.inf
            if d < 0: prev[d:] = np.inf
            better = prev < best; best[better] = prev[better]; back[i][better] = (np.arange(len(off)) - d)[better]
        cost[i] = best + e
    j = int(np.argmin(cost[-1])); path = []
    for i in range(n - 1, -1, -1): path.append(centre[i] + off[j]); j = back[i][j]
    x = np.array(path[::-1])
    for r0, r1, x0, x1 in FIX.get(name, []):
        m = (rows >= r0) & (rows <= r1); x[m] = np.interp(rows[m], [r0, r1], [x0, x1])
    return rows, x


out = {}
for name in GUIDE:
    rows, x = trace(name); out[name] = [[int(r), round(float(v), 1)] for r, v in zip(rows, x)]
json.dump(out, open(os.path.join(HERE, 'fit', 'trace-knot.json'), 'w'), indent=0)

# strips to check by eye: 3x, each side in pieces of 120 rows, the trace in green, a row label every 10
for name, pts in out.items():
    pts = np.array(pts); r0, r1 = int(pts[0, 0]), int(pts[-1, 0]); pieces = []
    for a in range(r0, r1, 120):
        b = min(a + 120, r1); seg = pts[(pts[:, 0] >= a) & (pts[:, 0] <= b)]; xc = int(np.median(seg[:, 1])); x0 = xc - 30
        c = im.crop((x0, a, x0 + 60, b)).resize((180, (b - a) * 3), Image.LANCZOS); d = ImageDraw.Draw(c)
        for r, xx in seg: d.point(((xx - x0) * 3, (r - a) * 3), fill=(0, 255, 0))
        for y in range(a - a % 10 + 10, b, 10): d.line([(0, (y - a) * 3), (8, (y - a) * 3)], fill=(255, 0, 0)); d.text((10, (y - a) * 3 - 5), str(y), fill=(255, 0, 0))
        d.text((120, 2), str(x0), fill=(255, 0, 0)); pieces.append(c)
    W2 = sum(p.width for p in pieces) + 4 * len(pieces); H2 = max(p.height for p in pieces)
    s = Image.new('RGB', (W2, H2), (0, 0, 0)); x = 0
    for p in pieces: s.paste(p, (x, 0)); x += p.width + 4
    s.save(os.path.join(HERE, 'fit', f'strip-{name}.png'))
print('traced:', {k: len(v) for k, v in out.items()})
