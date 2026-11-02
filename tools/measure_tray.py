"""Measures the duck pond's tray as numbers, through the camera fitted from its rim (tools/fit_ducks.py: an oval with straight sides, "A" half the straight part,
"R" the end radius, its outer top edge at RIM_Y). Read from the photo:
- the table: the tray's bottom edge (the traced outline's lower stretch) is the same oval, lower down; the height that puts it on that edge is the table
- the water: the blue's edge (the water's own outline) is a smaller oval at the water's height: its size gives the rim's width, its height the water level
Everything the photo cannot see (the back wall, the underside) follows from the oval: it is the same all round.
Run:  python tools/measure_tray.py      Writes tools/fit/tray-ducks.json and tools/fit/tray-ducks.png (the measured ovals drawn on the photo)"""
import json, math, os, runpy, io, contextlib
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
src = open(os.path.join(HERE, 'fit_ducks.py'), encoding='utf-8').read()               # its camera functions and constants, without rerunning its slow search
g = {'__file__': os.path.join(HERE, 'fit_ducks.py')}; exec(src[:src.index('TR = np.array(TRAY')], g)
fit = json.load(open(os.path.join(HERE, 'fit', 'ducks-fit.json'))); v, fov, A, R, RIM_Y = fit['v'], fit['fov'], fit['A'], fit['R'], g['RIM_Y']
project, stadium = g['project'], g['stadium']
im = Image.open(os.path.join(ROOT, 'brief', 'ref-ducks.jpg')).convert('RGB'); P = np.array(im).astype(float); H, W = P.shape[:2]


def oval_px(a, r, y): o = stadium(a, r, 480); return project(np.column_stack([o[:, 0], np.full(len(o), y), o[:, 1]]), v, fov)


from scipy.spatial import cKDTree


def dist_to(curve, pts):                                              # each point's distance to the projected curve
    return cKDTree(curve).query(pts)[0]


# fit the camera AND the tray together from points read by hand on 2x grids (tools/fit/tray-left-grid.png, tray-mid-grid.png, tray-right-grid.png), each
# point on its own edge: the rim's outer top edge (height h), its inner edge where the water starts (water height yw, radius R - w), and the wall's
# bottom edge on the table (height 0). Two automatic tries (the old 15-point fit, and a fit to the whole traced outline) landed the oval 10-40 px off.
# (hand-read points were tried too: reading the 2x grids by eye was 10-25 px off. The edges below come from colour, checked by eye before.)
# OUTER: the checked outline's upper half (above the line joining its two ends) is the rim's top edge; BOTTOM: its lower half is the wall's foot on the
# table; INNER: the blue's edge. Points next to a duck are left out (the big duck's head makes the outline there).
Pc = np.array(im).astype(float); Rc, Gc, Bc = Pc[..., 0], Pc[..., 1], Pc[..., 2]
yel = ndi.binary_dilation((Rc > 140) & (Gc > 110) & (Rc - Bc > 55), iterations=3)
olp = np.array(json.load(open(os.path.join(HERE, 'fit', 'outline-ducks-dense.json')))['outline'])
olp = olp[~yel[olp[:, 1].astype(int), olp[:, 0].astype(int)]]
lft, rgt = olp[np.argmin(olp[:, 0])], olp[np.argmax(olp[:, 0])]
above = olp[:, 1] < lft[1] + (olp[:, 0] - lft[0]) * (rgt[1] - lft[1]) / (rgt[0] - lft[0])
OUTER, BOTTOM = olp[above][::4], olp[~above][::4]
wat = ndi.binary_opening((Bc > Rc + 10) & (Bc > 120), iterations=2); lb_, nb_ = ndi.label(wat); wat = ndi.binary_fill_holes(lb_ == (np.argmax(np.bincount(lb_.ravel())[1:]) + 1))
ey_, ex_ = np.where(wat & ~ndi.binary_erosion(wat)); cyw, cxw = np.mean(np.where(wat), 1)
dx_, dy_ = ex_ - cxw, (ey_ - cyw) * 2.2; nn = np.hypot(dx_, dy_) + 1e-9                  # outward, away from the water's middle (the oval is ~2.2x wider than tall)
ox_ = np.clip((ex_ + 6 * dx_ / nn).astype(int), 0, Rc.shape[1] - 1); oy_ = np.clip((ey_ + 6 * dy_ / nn / 2.2).astype(int), 0, Rc.shape[0] - 1)
pc_ = Pc[oy_, ox_]; rimlike = (pc_.min(1) > 140) & (pc_.max(1) - pc_.min(1) < 50)    # the next pixel out is the white rim: this is the water's edge with the rim, not a duck's
INNER = np.stack([ex_[rimlike], ey_[rimlike]], 1)[::6]
po, pi, pb = (np.array(q, float) for q in (OUTER, INNER, BOTTOM))


def res(q, fv):
    vv = list(q[:6]); a = R * math.exp(q[6]); h, w, yw = q[7], q[8], q[9]
    so, si = stadium(a, R, 720), stadium(a, R - w, 720)
    oval = lambda st, y: project(np.column_stack([st[:, 0], np.full(len(st), y), st[:, 1]]), vv, fv)
    return np.r_[dist_to(oval(so, h), po), dist_to(oval(si, yw), pi), dist_to(oval(so, 0.0), pb)]


best = None
for fv in (40,):                                                               # start from the old camera (it was close: 10-40 px), let everything move
    q0 = list(v[:6]) + [math.log(A / R), 0.09, 0.075, 0.075]
    sol = least_squares(res, q0, args=(fv,), loss='soft_l1', f_scale=4, bounds=([-1, .2, -1, -400, -400, -.2, math.log(.1), .02, .005, .005], [1, 1.4, 3, 400, 400, .2, math.log(3), .4, .25, .4]))
    c = float(np.median(np.abs(sol.fun)))
    if best is None or c < best[0]: best = (c, fv, sol.x)
err, fov, qq = best; v = list(qq[:6]); A = R * math.exp(qq[6]); h, rim_w, yw = qq[7], qq[8], qq[9]; RIM_Y = h; yt = 0.0
miss = res(qq, fov); n_ol = len(po)
out = {'A': A, 'R': R, 'rim_top_y': RIM_Y, 'table_y': float(yt), 'water_y': float(yw), 'rim_width': float(rim_w),
       'wall_height': float(RIM_Y - yt), 'water_below_rim': float(RIM_Y - yw),
       'camera': {'v': [float(x) for x in v], 'fov': fov}, 'fit_px': {'rms': err, 'outer': float(np.max(miss[:len(po)])), 'inner': float(np.max(miss[len(po):len(po) + len(pi)])), 'bottom': float(np.max(miss[len(po) + len(pi):]))},
       'note': 'world: table at y 0, the tray centred at the origin, end radius 0.3. Hidden back wall and underside: the same oval all round.'}
json.dump(out, open(os.path.join(HERE, 'fit', 'tray-ducks.json'), 'w'), indent=1)
d = ImageDraw.Draw(im)
for (a, r, y), col in (((A, R, RIM_Y), (0, 255, 0)), ((A, R, yt), (255, 0, 255)), ((A, R - rim_w, yw), (255, 255, 0))):
    st = stadium(a, r, 720); q = project(np.column_stack([st[:, 0], np.full(len(st), y), st[:, 1]]), v, fov); d.line([tuple(p) for p in q] + [tuple(q[0])], fill=col, width=2)
for pts, col in ((OUTER, (0, 255, 0)), (INNER, (255, 255, 0)), (BOTTOM, (255, 0, 255))):
    for x, y in list(pts)[::3]: d.ellipse([x - 4, y - 4, x + 4, y + 4], outline=col, width=2)
im.crop((170, 360, 900, 740)).resize((1095, 570)).save(os.path.join(HERE, 'fit', 'tray-ducks.png'))
print(json.dumps(out, indent=1))
