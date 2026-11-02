"""Fits the photo's camera from round rims seen as ovals (a candle's foot and top), read as numbers on a zoomed photo.
A rim is a circle; the photo shows it as an oval: its two side corners (x, row), its lowest front row and, if you can see it, its highest back row.
A close camera looking down shows wide ovals low down and flat ones near eye level: a far camera cannot do both, so fit it, do not assume it.
Settings file (JSON): {"photo": "brief/ref-x.jpg", "objects": {"tall": {"foot": {...}, "top": {...}}, "short": {...}}}, each rim:
  {"sides": [[x, row], [x, row]], "front": row, "back": row (optional)}.  The first object's height is 1 unit (the scale).
Run:  python tools/fit_camera_rims.py tools/fit/rims-<name>.json      Prints the camera (for the generator's CAM and the Lab's photocam) and each miss in px.
The fit should land every rim within ~2 px; if not, re-read the rims."""
import json, math, sys
import numpy as np
from PIL import Image
from scipy.optimize import least_squares

cfg = json.load(open(sys.argv[1], encoding='utf-8')); W, H = Image.open(cfg['photo']).size
objs = list(cfg['objects']); TH = np.linspace(0, 2 * math.pi, 720, endpoint=False)


def cam(pitch, fov, dist, target):
    T = np.array([0, target, 0.0]); P = T + dist * np.array([0, math.sin(pitch), math.cos(pitch)])
    f = (T - P) / np.linalg.norm(T - P); r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    return P, f, r, u, (H / 2) / math.tan(math.radians(fov) / 2)


def proj(C, p):
    P, f, r, u, F = C; q = p - P; z = q @ f
    return np.stack([W / 2 + q @ r / z * F, H / 2 - q @ u / z * F], 1)


def unpack(v):
    cam_v, rest = v[:4], v[4:]; out = {}
    for i, o in enumerate(objs):                                   # per object: x, z, foot radius, top radius, height (the first is 1, at z 0), top's sideways shift
        x, z, rf, rt, h, dx = rest[i * 6:(i + 1) * 6]; out[o] = (x, 0.0 if i == 0 else z, rf, rt, 1.0 if i == 0 else h, dx)   # the first stands at z = 0, else camera and candles slide together
    return cam_v, out


def resid(v):
    cam_v, ob = unpack(v); C = cam(*cam_v); res = []
    for o, (x, z, rf, rt, h, dx) in ob.items():
        for rim, (cx, cy, R) in (('foot', (x, 0.0, rf)), ('top', (x + dx, h, rt))):
            if rim not in cfg['objects'][o]: continue
            m = cfg['objects'][o][rim]; e = proj(C, np.stack([cx + R * np.cos(TH), np.full_like(TH, cy), z + R * np.sin(TH)], 1))
            l, r = e[np.argmin(e[:, 0])], e[np.argmax(e[:, 0])]
            res += [l[0] - m['sides'][0][0], l[1] - m['sides'][0][1], r[0] - m['sides'][1][0], r[1] - m['sides'][1][1], e[:, 1].max() - m['front']]
            if 'back' in m: res.append(e[:, 1].min() - m['back'])
    return np.array(res)


v0 = [0.15, 40, 3.3, 0.6] + sum([[0.3 * (i - (len(objs) - 1) / 2), 0.3 * i, 0.16, 0.16, 0.8, 0.0] for i in range(len(objs))], [])
fit = least_squares(resid, v0, x_scale='jac'); (pitch, fov, dist, target), ob = unpack(fit.x)
print(json.dumps({'CAM': {'pitch': round(pitch, 4), 'fov': round(fov, 3), 'dist': round(dist, 4), 'target': round(target, 4), 'u0': 0.0, 'v0': 0.0},
                  'objects': {o: {'x': round(v[0], 4), 'z': round(v[1], 4), 'height': round(v[4], 4)} for o, v in ob.items()}}, indent=1))
print('misses (px):', np.round(resid(fit.x), 1).tolist())
