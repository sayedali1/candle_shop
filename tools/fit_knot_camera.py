"""Fits the knot photo's camera from the rims, read as numbers (tools/fit/feet.png, tops.png, 4x close-ups):
each foot and top is a circle seen from above, so the photo shows it as an ellipse: its side corners, its lowest front point and (tops) its back point.
A close camera near the tall top looking down explains the wide foot ellipses next to the nearly flat top rims; the old far camera could not.
Run:  python tools/fit_knot_camera.py      Prints the camera for gen_knot.py (CAM)."""
import math
import numpy as np
from scipy.optimize import least_squares

W, H = 896, 1200
# (circle, photo points): side corners as (x, row) left and right, front = lowest row in the middle, back = highest row (tops only)
OBS = {'tall_foot': {'sides': ((449, 978), (624, 978)), 'front': 1007},
       'tall_top': {'sides': ((455, 423), (647, 423)), 'front': 427, 'back': 419},
       'short_foot': {'sides': ((266, 1045), (437, 1045)), 'front': 1072},
       'short_top': {'sides': ((257, 554), (420, 554)), 'front': 562, 'back': 547}}


def cam(pitch, fov, dist, target, u0):
    T = np.array([0, target, 0.0]); P = T + dist * np.array([0, math.sin(pitch), math.cos(pitch)])
    f = (T - P) / np.linalg.norm(T - P); r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    return P, f, r, u, (H / 2) / math.tan(math.radians(fov) / 2), u0


def proj(C, p):
    P, f, r, u, F, u0 = C; q = p - P; z = q @ f
    return np.stack([W / 2 + u0 + q @ r / z * F, H / 2 - q @ u / z * F], 1)


TH = np.linspace(0, 2 * math.pi, 720, endpoint=False)


def ellipse(C, cx, cy, cz, R):
    return proj(C, np.stack([cx + R * np.cos(TH), np.full_like(TH, cy), cz + R * np.sin(TH)], 1))


def resid(v):
    pitch, fov, dist, target, xt, xs, zs, rtf, rtt, rsf, rst, hs, dxt, dxs = v; u0 = 0.0   # the picture's middle is the camera's middle (else it trades off against where the candles stand)
    C = cam(pitch, fov, dist, target, u0); out = []
    for name, (cx, cy, cz, R) in {'tall_foot': (xt, 0, 0, rtf), 'tall_top': (xt + dxt, 1.0, 0, rtt),
                                  'short_foot': (xs, 0, zs, rsf), 'short_top': (xs + dxs, hs, zs, rst)}.items():
        e = ellipse(C, cx, cy, cz, R); o = OBS[name]
        l, rr = e[np.argmin(e[:, 0])], e[np.argmax(e[:, 0])]
        out += [l[0] - o['sides'][0][0], l[1] - o['sides'][0][1], rr[0] - o['sides'][1][0], rr[1] - o['sides'][1][1], e[:, 1].max() - o['front']]
        if 'back' in o: out.append(e[:, 1].min() - o['back'])
    return np.array(out)


v0 = [0.15, 40, 3.3, 0.6, 0.3, 0.0, 0.5, 0.16, 0.17, 0.15, 0.15, 0.8, 0.0, 0.0]
fit = least_squares(resid, v0, x_scale='jac')
names = 'pitch fov dist target xt xs zs rtf rtt rsf rst hs dxt dxs'.split()
print({n: round(float(x), 4) for n, x in zip(names, fit.x)})
print('misses (px):', np.round(resid(fit.x), 1))
