"""Traces a photo's outlines, every row, both sides, as numbers: the measured outline every 3D shape is built from and scored against.
A dynamic-programming tracer follows the strongest brightness step down each side, moving at most `step` px per row, so it cannot jump onto a
window frame or the object behind. Each side starts from a rough guide and searches +-`window` px around it.
Every traced side is drawn on zoomed strips (tools/fit/strip-<name>-<side>.png): LOOK AT EVERY STRIP. Where the trace is wrong (a frame or another
object behind the edge, light behind the edge that looks like the object), add a hand fix in the settings file and say in its note why.
For an edge the background hides, read it in a contrast or colour view (the object is warmer or more saturated than the room), or mirror the clean
other side about the middle line.
Settings file (JSON):
  {"photo": "brief/ref-x.jpg", "window": 14, "step": 2,
   "guides": {"tall_L": [[row, x], ...], "tall_R": [...]},           # rough points along each side, top to bottom
   "fix":    {"tall_L": [[row0, row1, x0, x1], ...]},                  # hand values, straight between, where the tracer is wrong
   "notes":  {"tall_L": "why each fix"}}
Run:  python tools/trace_outline.py tools/fit/trace-<name>.cfg.json      Writes tools/fit/trace-<name>.json and the strips."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
cfg_path = sys.argv[1]; cfg = json.load(open(cfg_path, encoding='utf-8'))
name = os.path.basename(cfg_path).replace('trace-', '').replace('.cfg.json', '')
im = Image.open(os.path.join(ROOT, cfg['photo'])).convert('RGB'); A = np.array(im).astype(float)
L = ndi.gaussian_filter(A.mean(2), 1.0); gx = np.zeros_like(L); gx[:, 1:-1] = L[:, 2:] - L[:, :-2]


def trace(side, W_, step, lam=3.0):
    g = np.array(cfg['guides'][side]); rows = np.arange(g[0, 0], g[-1, 0] + 1); centre = np.interp(rows, g[:, 0], g[:, 1])
    off = np.arange(-W_, W_ + 1); n = len(rows); cost = np.zeros((n, len(off))); back = np.zeros((n, len(off)), int)
    for i, y in enumerate(rows):
        xs = np.clip(np.round(centre[i] + off).astype(int), 1, A.shape[1] - 2); e = -np.abs(gx[y, xs])
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
    for r0, r1, x0, x1 in cfg.get('fix', {}).get(side, []):
        m = (rows >= r0) & (rows <= r1); x[m] = np.interp(rows[m], [r0, r1], [x0, x1])
    return rows, x


out = {}
for side in cfg['guides']:
    rows, x = trace(side, cfg.get('window', 14), cfg.get('step', 2)); out[side] = [[int(r), round(float(v), 1)] for r, v in zip(rows, x)]
json.dump(out, open(os.path.join(HERE, 'fit', f'trace-{name}.json'), 'w'), indent=0)

for side, pts in out.items():                                      # strips to check by eye: 3x, 120 rows a piece, the trace in green, a row label every 10, the strip's left x on top
    pts = np.array(pts); r0, r1 = int(pts[0, 0]), int(pts[-1, 0]); pieces = []
    for a in range(r0, r1, 120):
        b = min(a + 120, r1); seg = pts[(pts[:, 0] >= a) & (pts[:, 0] <= b)]; x0 = int(np.median(seg[:, 1])) - 30
        c = im.crop((x0, a, x0 + 60, b)).resize((180, (b - a) * 3), Image.LANCZOS); d = ImageDraw.Draw(c)
        for r, xx in seg: d.point(((xx - x0) * 3, (r - a) * 3), fill=(0, 255, 0))
        for y in range(a - a % 10 + 10, b, 10): d.line([(0, (y - a) * 3), (8, (y - a) * 3)], fill=(255, 0, 0)); d.text((10, (y - a) * 3 - 5), str(y), fill=(255, 0, 0))
        d.text((120, 2), str(x0), fill=(255, 0, 0)); pieces.append(c)
    s = Image.new('RGB', (sum(p.width + 4 for p in pieces), max(p.height for p in pieces))); x = 0
    for p in pieces: s.paste(p, (x, 0)); x += p.width + 4
    s.save(os.path.join(HERE, 'fit', f'strip-{name}-{side}.png'))
print('traced', {k: len(v) for k, v in out.items()}, '-> tools/fit/trace-%s.json; now look at every tools/fit/strip-%s-*.png' % (name, name))
