"""Measures the photo's camera from the tray: the oval's outline, traced by hand, says how high and from which side the camera looks. Then each duck's foot and beak pixel, sent through that camera
onto the pond, gives its real place and direction. Nothing here is guessed by eye except the traced pixels.
Run:  python tools/fit_ducks.py        Writes tools/fit/ducks-fit.json and tools/fit/ducks-fit.png (the fitted tray and ducks drawn on the photo)"""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
W, H = 1083, 863
R0 = 0.30; RIM_Y = 0.09; POND_Y = 0.074
# the rim's outer top edge (photo pixels)
TRAY = [(213, 555), (235, 615), (290, 657), (355, 675), (490, 672), (690, 665), (790, 632), (850, 590), (857, 550), (835, 490), (615, 420), (440, 424), (340, 435), (280, 465), (240, 505)]
# foot middle, head middle and beak tip of each duck (photo pixels); the big duck first
DUCKS = [((725, 552), (727, 433), (740, 485)),
         ((330, 490), (327, 457), (345, 470)), ((437, 470), (437, 445), (447, 457)), ((545, 475), (547, 442), (555, 459)),
         ((297, 565), (297, 530), (317, 542)), ((437, 540), (440, 505), (452, 520)), ((575, 542), (577, 512), (590, 526)),
         ((395, 620), (400, 577), (412, 595)), ((525, 605), (530, 565), (542, 585))]


def stadium(a, r, n=240):
    pts = []
    for i in range(n // 2):
        t = -math.pi / 2 + math.pi * i / (n // 2 - 1); pts.append((a + r * math.cos(t), r * math.sin(t)))
    for i in range(n // 2):
        t = math.pi / 2 + math.pi * i / (n // 2 - 1); pts.append((-a + r * math.cos(t), r * math.sin(t)))
    return np.array(pts)


def camera(v, fov):
    yaw, pitch, ld = v[0], v[1], v[2]
    d = math.exp(ld); T = np.array([0.0, RIM_Y, 0.0])
    P = T + d * np.array([math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch)])
    f = (T - P) / d; right = np.cross(f, [0, 1, 0]); right /= np.linalg.norm(right); up = np.cross(right, f)
    return P, f, right, up, (H / 2) / math.tan(math.radians(fov) / 2)


def project(p, v, fov):
    P, f, right, up, F = camera(v, fov); q = np.atleast_2d(p) - P
    z = q @ f; x = q @ right / z * F; y = q @ up / z * F
    c, s = math.cos(v[5]), math.sin(v[5])
    return np.stack([W / 2 + v[3] + x * c - y * s, H / 2 + v[4] - (x * s + y * c)], 1)


def ray(px, py, v, fov):
    P, f, right, up, F = camera(v, fov)
    x0, y0 = px - W / 2 - v[3], -(py - H / 2 - v[4]); c, s = math.cos(-v[5]), math.sin(-v[5])
    x, y = x0 * c - y0 * s, x0 * s + y0 * c
    d = f + x / F * right + y / F * up
    return P, d / np.linalg.norm(d)


def on_plane(px, py, y, v, fov):
    P, d = ray(px, py, v, fov); return P + d * ((y - P[1]) / d[1])


TR = np.array(TRAY, float)


def resid(v, fov):
    a = R0 * math.exp(v[6]); o = stadium(a, R0)
    q = project(np.column_stack([o[:, 0], np.full(len(o), RIM_Y), o[:, 1]]), v, fov)
    return np.array([np.min(np.hypot(*(q - t).T)) for t in TR])


best = None
for fov in (30, 40, 50, 60):
    for y0, ra, dd, p0 in ((a_, b_, c_, d_) for a_ in (-0.25, 0.0, 0.25) for b_ in (1.0, 1.4, 1.8) for c_ in (1.6, 2.4) for d_ in (0.5, 0.75)):
        s = least_squares(resid, [y0, p0, math.log(dd), 0, 0, 0, math.log(ra)], args=(fov,), bounds=([-1, .15, 0, -300, -300, -.08, math.log(.6)], [1, 1.3, 2.5, 300, 300, .08, math.log(2.4)]))
        c = float(np.sqrt(np.mean(s.fun ** 2)))
        if best is None or c < best[0]: best = (c, fov, s.x)
err, fov, v = best
A = R0 * math.exp(v[6])
print(f'camera: side turn {math.degrees(v[0]):.1f} deg, height {math.degrees(v[1]):.1f} deg, distance {math.exp(v[2]):.2f}, fov {fov}, roll {math.degrees(v[5]):.1f} deg; tray straight part {2 * A:.2f}, width {2 * R0:.2f}; fit error {err:.1f} px')
ducks = []
for i, (foot, head, beak) in enumerate(DUCKS):
    fp = on_plane(*foot, POND_Y, v, fov)
    S = 0.34 if i == 0 else 0.118
    hp, bp = on_plane(*head, POND_Y + .72 * S, v, fov), on_plane(*beak, POND_Y + .6 * S, v, fov)
    yaw = math.atan2(bp[0] - hp[0], bp[2] - hp[2])
    ducks.append({'x': round(float(fp[0]), 4), 'z': round(float(fp[2]), 4), 'yaw': round(yaw, 3), 'S': S})
    print(f'  duck {i}: x {fp[0]:+.3f} z {fp[2]:+.3f}, looks {math.degrees(yaw):+.0f} deg')
json.dump({'v': [float(q) for q in v], 'yaw': float(v[0]), 'pitch': float(v[1]), 'dist': float(math.exp(v[2])), 'fov': fov, 'A': A, 'R': R0, 'ducks': ducks}, open(os.path.join(HERE, 'fit', 'ducks-fit.json'), 'w'), indent=1)
im = Image.open(os.path.join(ROOT, 'brief', 'ref-ducks.jpg')).convert('RGB'); d = ImageDraw.Draw(im)
o = stadium(A, R0); q = project(np.column_stack([o[:, 0], np.full(len(o), RIM_Y), o[:, 1]]), v, fov)
d.line([tuple(p) for p in q] + [tuple(q[0])], fill=(0, 255, 0), width=2)
for t in TRAY: d.ellipse([t[0] - 3, t[1] - 3, t[0] + 3, t[1] + 3], outline=(255, 0, 0))
for k in ducks:
    p0 = project(np.array([[k['x'], POND_Y, k['z']]]), v, fov)[0]; L = k['S'] * .6
    p1 = project(np.array([[k['x'] + math.sin(k['yaw']) * L, POND_Y, k['z'] + math.cos(k['yaw']) * L]]), v, fov)[0]
    d.line([tuple(p0), tuple(p1)], fill=(255, 0, 255), width=3); d.ellipse([p0[0] - 4, p0[1] - 4, p0[0] + 4, p0[1] + 4], fill=(255, 0, 255))
im.crop((170, 320, 900, 740)).save(os.path.join(HERE, 'fit', 'ducks-fit.png'))
