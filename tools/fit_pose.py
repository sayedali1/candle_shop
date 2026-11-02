"""Fits the lying puppy's ellipsoids and the camera to the photo's outline (see photo_mask.py).
It lays the same ellipsoids the recipe uses on the photo through a perspective camera, and moves them (and the camera) until the outline matches
where the photo shows the lying puppy, with a small pull back to the first guess so directions the photo cannot show (depth) do not wander.
Run:  python tools/fit_pose.py        Writes tools/fit/pose.json and tools/fit/fit-preview.png"""
import json, math, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'fit')
d = np.load(os.path.join(OUT, 'mask.npz')); UNION, CARE, W, H = d['union'], d['care'], int(d['W']), int(d['H'])
X0, X1, Y0, Y1, DS = 130, 520, 280, 720, 3                      # the part of the photo we look at, and how much we shrink it
U = UNION[Y0:Y1:DS, X0:X1:DS]; C = CARE[Y0:Y1:DS, X0:X1:DS]
dU = ndi.distance_transform_edt(~U)                              # distance to the puppies, for pixels that stick out

# first guess: the blocks the recipe generator holds (local candle units): (name, centre, radii, turn about y, has a mirror twin in z)
a1 = math.radians(52)
head = (0.37, 0.44, 0.06); lat = (math.cos(a1), -math.sin(a1)); fwd = (math.sin(a1), math.cos(a1))
FAM = [
    ('body', (-0.02, 0.16, 0.0), (0.30, 0.15, 0.165), 0, False),
    ('rear', (-0.31, 0.17, 0.0), (0.17, 0.16, 0.17), 0, False),
    ('haunch', (-0.27, 0.12, 0.125), (0.15, 0.12, 0.085), 0, True),
    ('foot', (-0.1, 0.05, 0.15), (0.11, 0.05, 0.06), 0, True),
    ('tail', (-0.47, 0.21, 0.0), (0.05, 0.05, 0.05), 0, False),
    ('chest', (0.16, 0.2, 0.0), (0.2, 0.18, 0.17), 0, False),
    ('head', head, (0.23, 0.215, 0.22), 0, False),
    ('ear', (head[0] + lat[0] * 0.215 - 0.03, head[1] - 0.1, head[2] + lat[1] * 0.215), (0.07, 0.21, 0.13), a1, True),
    ('paw1', (0.4, 0.07, 0.1), (0.15, 0.065, 0.065), 0, True),
    ('paw2', (0.52, 0.055, 0.12), (0.07, 0.055, 0.06), 0, True),
    ('muzzle', (head[0] + fwd[0] * 0.2, head[1] - 0.07, head[2] + fwd[1] * 0.2), (0.088, 0.062, 0.075), -(math.pi / 2 - a1), False),
]
NF = len(FAM)
SIZE, TURN = 0.78, -0.12                                         # the recipe's size and turn


def blocks(x):
    """every block (a mirrored pair gives two) from the numbers x: per family 3 shifts of the centre and 3 log-scales of the radii"""
    out = []
    for i, (nm, c, r, rot, mir) in enumerate(FAM):
        dc, k = x[6 * i:6 * i + 3], x[6 * i + 3:6 * i + 6]
        c2 = (c[0] + dc[0], c[1] + dc[1], c[2] + dc[2]); r2 = (r[0] * math.exp(k[0]), r[1] * math.exp(k[1]), r[2] * math.exp(k[2]))
        out.append((nm, c2, r2, rot, 1))
        if mir:
            if nm == 'ear':                                      # the other ear sits on the other side of the head
                cc = (2 * (head[0] - 0.03) - c2[0], c2[1], 2 * head[2] - c2[2]); out.append((nm, cc, r2, rot, -1))
            else:
                out.append((nm, (c2[0], c2[1], -c2[2]), r2, rot, -1))
    return out


def cam_rays(cx):
    yaw, pitch, fov, tx, ty, tz = cx
    r = 4.2; T = np.array([tx, ty, tz]); P = T + r * np.array([math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch)])
    f = (T - P) / np.linalg.norm(T - P); right = np.cross(f, [0, 1, 0]); right /= np.linalg.norm(right); up = np.cross(right, f)
    ys, xs = np.mgrid[Y0:Y1:DS, X0:X1:DS]; t = math.tan(math.radians(fov) / 2)
    nx = (xs / W * 2 - 1) * (W / H) * t; ny = -(ys / H * 2 - 1) * t
    dirs = nx[..., None] * right + ny[..., None] * up + f
    return P, dirs / np.linalg.norm(dirs, axis=-1, keepdims=True)


def render(x, cx):
    P, D = cam_rays(cx); hit = np.zeros(D.shape[:2], bool)
    ct, st = math.cos(TURN), math.sin(TURN)
    for nm, c, r, rot, sg in blocks(x):
        w = np.array([SIZE * (c[0] * ct + c[2] * st), SIZE * c[1], SIZE * (-c[0] * st + c[2] * ct)])       # candle -> world
        ang = rot + TURN
        ca, sa = math.cos(ang), math.sin(ang); Rinv = np.array([[ca, 0, -sa], [0, 1, 0], [sa, 0, ca]])
        rr = np.array(r) * SIZE
        o = (Rinv @ (P - w)) / rr; dd = (D @ Rinv.T) / rr
        a = (dd * dd).sum(-1); b = (dd * o).sum(-1); cq = (o * o).sum() - 1
        disc = b * b - a * cq
        hit |= (disc >= 0) & ((-b + np.sqrt(np.maximum(disc, 0))) / a > 0)
    return hit


x0 = np.zeros(6 * NF); cx0 = np.array([0.4, 0.25, 30.0, 0.0, 0.5, 0.0])


def loss(v):
    x, cx = v[:6 * NF], v[6 * NF:]
    R = render(x, cx)
    out = R & ~U; miss = C & ~R
    dR = ndi.distance_transform_edt(~R)
    err = out.sum() + dU[out].sum() * 0.5 + miss.sum() + dR[miss].sum() * 0.5
    reg = 0.0
    for i in range(NF):
        reg += (np.sum(x[6 * i:6 * i + 3] ** 2) / 0.07 ** 2 + np.sum(x[6 * i + 3:6 * i + 6] ** 2) / 0.30 ** 2) * 1.5
    reg += ((cx[0] - cx0[0]) / 0.5) ** 2 * 20 + ((cx[1] - cx0[1]) / 0.4) ** 2 * 20 + ((cx[2] - cx0[2]) / 15) ** 2 * 20
    return err + reg


if __name__ == '__main__':
    v = np.concatenate([x0, cx0])
    step = np.concatenate([np.full(6 * NF, 0.02), [0.05, 0.05, 2.0, 0.08, 0.08, 0.08]])
    for i in range(NF): step[6 * i + 3:6 * i + 6] = 0.05
    best = loss(v)
    print('start', round(best, 1), flush=True)
    for it in range(80):
        improved = False
        order = np.random.RandomState(it).permutation(len(v))
        if it < 8: order = np.arange(6 * NF, len(v))             # first move the whole picture roughly onto the puppies (the camera), then everything
        for i in order:
            for sgn in (1, -1):
                w = v.copy(); w[i] += sgn * step[i]; l = loss(w)
                if l < best - 1e-6: v, best, improved = w, l, True; break
        if not improved: step *= 0.6
        if it % 10 == 0: print(it, round(best, 1), flush=True)
        if step.max() < 0.002: break
    x, cx = v[:6 * NF], v[6 * NF:]
    R = render(x, cx); bl = blocks(x)
    print('final', round(best, 1), 'camera', np.round(cx, 3).tolist())
    json.dump({'camera': {'yaw': float(cx[0]), 'pitch': float(cx[1]), 'fov': float(cx[2]), 'target': [float(t) for t in cx[3:6]], 'dist': 4.2},
               'blocks': [{'name': q[0], 'c': [float(t) for t in q[1]], 'r': [float(t) for t in q[2]], 'rot': q[3], 'side': q[4]} for q in bl]},
              open(os.path.join(OUT, 'pose.json'), 'w'), indent=1)
    photo = np.array(Image.open(os.path.join(HERE, '..', 'brief', 'ref-poodle-candles.webp')).convert('RGB').crop((X0, Y0, X1, Y1))).astype(np.float32) / 255
    Rf = np.array(Image.fromarray((R * 255).astype(np.uint8)).resize(photo.shape[1::-1], Image.NEAREST)) > 127
    Uf = UNION[Y0:Y1, X0:X1]
    pv = photo * 0.55; pv[Rf] = pv[Rf] * 0.4 + np.array([0.0, 0.6, 0.0]) * 0.6
    edge = Uf & ~ndi.binary_erosion(Uf, iterations=2); pv[edge] = [1, 1, 0]
    Image.fromarray((pv * 255).astype(np.uint8)).save(os.path.join(OUT, 'fit-preview.png'))
