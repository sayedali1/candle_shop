"""The side photo's camera for the heart-pile jar, fitted from the jar's corners (photo px read on tools/fit/hs-*.png): front-top corners (318,431) and
(771,431), the rim's back edge 424, front-bottom corners (322,1240) (767,1240). Writes tools/fit/pose-15-heart-pile.json (candle units x size)."""
import json, math, numpy as np
from scipy.optimize import least_squares
W, H, SIZE = 1086, 1448, 0.78; w = 453 / 813; d = w
obs = [((-w/2, 1, d/2), (318, 431)), ((w/2, 1, d/2), (771, 431)), ((-w/2, 0, d/2), (322, 1240)), ((w/2, 0, d/2), (767, 1240)), ((0, 1, -d/2), (None, 424))]
def proj(v, p):
    pitch, fov, dist, ty, u0, v0 = v; T = np.array([0, ty, 0]); P = T + dist * np.array([0, math.sin(pitch), math.cos(pitch)])
    f = (T - P) / dist; r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r); up = np.cross(r, f); F = (H / 2) / math.tan(math.radians(fov) / 2)
    q = np.array(p) - P; z = q @ f; return W / 2 + u0 + q @ r / z * F, H / 2 + v0 - q @ up / z * F
def res(v):
    out = []
    for p, (x, y) in obs:
        px, py = proj(v, p)
        if x is not None: out.append(px - x)
        out.append(py - y)
    return out
s = least_squares(res, [0.05, 35, 3, 0.5, 0, 0]); v = s.x; print('misses', np.round(res(v), 1), 'pitch', round(v[0], 3), 'fov', round(v[1], 2), 'dist', round(v[2], 3))
json.dump({'camera': {'yaw': 0.0, 'pitch': float(v[0]), 'fov': float(v[1]), 'target': [0, float(v[3]) * SIZE, 0], 'dist': float(v[2]) * SIZE, 'u0': float(v[4]), 'v0': float(v[5]), 'roll': 0.0}, 'blocks': []},
          open('tools/fit/pose-15-heart-pile.json', 'w'), indent=1)
