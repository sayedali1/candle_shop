"""Each figure of the duck pond as its own outline (photo pixels), for tools/gen_relief.py ("outlines": one polygon per figure).
The figures are found by colour (yellow, touching the water), split where they touch by hand-read cut lines and completed with hand-read pale areas
(tools/fit/parts-ducks.json). Writes tools/fit/outline-duckfigs.json and tools/fit/duckfigs.png (each outline on the photo, to check by eye).
Run:  python tools/duck_outlines.py"""
import json, os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
im = Image.open(os.path.join(ROOT, 'brief', 'ref-ducks.jpg')).convert('RGB'); A = np.array(im).astype(float); H, W = A.shape[:2]
cfg = json.load(open(os.path.join(HERE, 'fit', 'parts-ducks.json')))
ol = json.load(open(os.path.join(HERE, 'fit', 'outline-ducks-dense.json')))['outline']
mi = Image.new('L', (W, H), 0); ImageDraw.Draw(mi).polygon([tuple(p) for p in ol], fill=1); m = np.array(mi) > 0
R_, G_, B_ = A[..., 0], A[..., 1], A[..., 2]
water = m & (B_ > R_ + 10)
strong = ndi.binary_opening(m & (R_ > 140) & (G_ > 110) & (R_ - B_ > 55) & (G_ - B_ > 25), iterations=2)
cut = Image.new('L', (W, H), 0)
for ln in cfg.get('cut', []): ImageDraw.Draw(cut).line([tuple(q) for q in ln], fill=1, width=4)
cut = np.array(cut) > 0; strong &= ~cut
add = Image.new('L', (W, H), 0)
for pg in cfg.get('add', []): ImageDraw.Draw(add).polygon([tuple(q) for q in pg], fill=1)
add = (np.array(add) > 0) & m & ~water
lab, n = ndi.label(strong); near = ndi.binary_dilation(water, iterations=8); big = [k for k in range(1, n + 1) if (lab == k).sum() >= 300 and ((lab == k) & near).any()]


def boundary(mk):
    ys, xs = np.where(mk); i = np.lexsort((xs, ys))[0]; start = (int(ys[i]), int(xs[i]))
    N = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]; ins = lambda p: 0 <= p[0] < H and 0 <= p[1] < W and mk[p]
    out, cur, d = [start], start, 6
    for _ in range(int(mk.sum()) * 4):
        for k in range(8):
            dd = (d + k) % 8; nb = (cur[0] + N[dd][0], cur[1] + N[dd][1])
            if ins(nb): cur, d = nb, (dd + 5) % 8; break
        if cur == start: break
        out.append(cur)
    return out


polys = []; chk = A * 0.5; dr = None
for k in big:
    c = lab == k
    c = ndi.binary_fill_holes(ndi.binary_closing(c, iterations=12, border_value=0)) & m & ~water & ~cut & ~ndi.binary_dilation(np.isin(lab, [q for q in big if q != k]), iterations=2)
    if (ndi.binary_dilation(c, iterations=3) & add).any(): c = ndi.binary_fill_holes(c | add)
    c = ndi.binary_opening(c, iterations=2); lb, nb = ndi.label(c); c = lb == (np.argmax(np.bincount(lb.ravel())[1:]) + 1)
    b = np.array(boundary(c))[::2]; polys.append([[int(x), int(y)] for y, x in b])
json.dump({'note': 'one outline per figure (tools/duck_outlines.py), the big duck first', 'outlines': sorted(polys, key=lambda p: -len(p))}, open(os.path.join(HERE, 'fit', 'outline-duckfigs.json'), 'w'))
img = im.copy(); d = ImageDraw.Draw(img)
for p in polys: d.line([tuple(q) for q in p] + [tuple(p[0])], fill=(255, 0, 255), width=2)
img.crop((200, 360, 880, 720)).save(os.path.join(HERE, 'fit', 'duckfigs.png')); print(len(polys), 'figures')
