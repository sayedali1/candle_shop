"""Grows real curls on a baked body and writes a recipe that shows them. A smooth skin with a bump texture can never read as a curly coat: the outline stays hard and the light stays smooth.
So each curl is a real small lump: spaced evenly over the body (small on the face, large on the back), kept off the eyes and nose, and coloured from the photo pixel it lands on.
The body underneath turns darker, so the gaps between the curls read as shadow.
File format (.crl): 12 float32 per curl: x y z, nx ny nz, size, twist, stretch, r g b.
Run:  python tools/gen_curls.py recipes/zz-puppy.json recipes/zz-curly.json [contrast 1.2]"""
import json, math, os, struct, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); sys.path.insert(0, HERE)
import fit_pose as fp

src, out = sys.argv[1], sys.argv[2]
CONTRAST = float(sys.argv[3]) if len(sys.argv) > 3 else 1.2
env = lambda k, v: float(os.environ.get(k, v))
FACE_S, HEAD_S, BODY_S = env('FACE_S', '0.012'), env('HEAD_S', '0.019'), env('BODY_S', '0.042')       # the spacing between curls: on the muzzle, on the head and ear, on the body
SIZE_K, SINK = env('SIZE_K', '1.15'), env('SINK', '0.6')                                              # curl radius as a share of the spacing; how much of a curl stands sunk in the body
rec = json.load(open(src, encoding='utf-8'))
blob = [p for p in rec['parts'] if p['shape'] == 'blob'][0]
dots = [p for p in rec['parts'] if p['shape'] == 'dots']
keep_off = [(np.array(q), p['r'] * max(p.get('scale', [1])) * env('CLEAR', '2.2')) for p in dots for q in p['at']]     # the eyes and the nose stay clear
nose = np.array(dots[-1]['at'][0]); eyes = np.array(dots[-2]['at']); face_c = (nose + eyes.mean(0)) / 2

buf = open(os.path.join(ROOT, blob['bake']), 'rb').read()
magic, n, ni, isz = struct.unpack('<4I', buf[:16])
mn = np.array(struct.unpack('<3f', buf[16:28])); rg = np.array(struct.unpack('<3f', buf[28:40]))
up4 = lambda x: (x + 3) & ~3
oPos = 48; oNor = oPos + up4(n * 6); oAT = oNor + up4(n * 3)
pos = np.frombuffer(buf, '<u2', n * 3, oPos).reshape(n, 3) / 65535.0 * rg + mn
nor = np.frombuffer(buf, 'i1', n * 3, oNor).reshape(n, 3).astype(float) / 127.0
nor /= np.linalg.norm(nor, axis=1, keepdims=True) + 1e-9
ao = np.frombuffer(buf, 'u1', n * 3, oAT).reshape(n, 3)[:, 0] / 255.0
print(f'body: {n} points, mean shut-in value {ao.mean():.2f}')


def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)


# the spacing at every point of the body, small near the face and large far from it
d_face = np.linalg.norm(pos - face_c, axis=1)
spacing = FACE_S + (HEAD_S - FACE_S) * smooth(0.05, 0.11, d_face) + (BODY_S - HEAD_S) * smooth(0.24, 0.36, d_face)
rng = np.random.RandomState(7)
free = (pos[:, 1] > 0.012) & ((nor[:, 1] > -0.35) | (d_face < 0.22)) & (ao > 0.2)  # nothing on the floor line, the underside or deep inside folds: nobody sees them
#                                                                            # nothing on the floor line
for c, r in keep_off: free &= np.linalg.norm(pos - c, axis=1) > r
order = rng.permutation(np.where(free)[0])
tree = cKDTree(pos)
taken = np.zeros(n, bool); chosen = []
for i in order:                                                                                      # even spacing without a pattern: take a point, then block its neighbours
    if taken[i]: continue
    chosen.append(i); taken[tree.query_ball_point(pos[i], spacing[i] * (0.85 + 0.3 * rng.rand()))] = True
chosen = np.array(chosen); N = len(chosen)

P, Nr = pos[chosen], nor[chosen]; S = spacing[chosen] * SIZE_K * (0.8 + 0.4 * rng.rand(N))
C = P + Nr * S[:, None] * (1 - SINK) * 0.5
for c, r in keep_off:                                                                                # a curl next to an eye must not lean over it: pull its size down there
    d = np.linalg.norm(C - c, axis=1); S = np.where(d - S < r * 0.75, np.minimum(S, np.maximum(d - r * 0.75, S * 0.4)), S)

# the colour: the photo pixel the curl lands on, as a multiplier on the wax colour
cam = json.load(open(os.path.join(HERE, 'fit', 'pose.json')))['camera']
yaw, pitch, fov = cam['yaw'], cam['pitch'], cam['fov']; T = np.array(cam['target']); r = cam['dist']
E = T + r * np.array([math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch)])
f = (T - E) / np.linalg.norm(T - E); right = np.cross(f, [0, 1, 0]); right /= np.linalg.norm(right); upv = np.cross(right, f)
ct, st = math.cos(fp.TURN), math.sin(fp.TURN); W, H = fp.W, fp.H; tn = math.tan(math.radians(fov) / 2); asp = W / H


def project(p):
    w = fp.SIZE * np.stack([p[:, 0] * ct + p[:, 2] * st, p[:, 1], -p[:, 0] * st + p[:, 2] * ct], 1); v = w - E
    z = v @ f; return (v @ right / (z * tn * asp) + 1) / 2 * W, (1 - v @ upv / (z * tn)) / 2 * H, z, v


ub, vb, zb_, _ = project(pos)
zb = np.full((H, W), 1e9); iu, iv = np.round(ub).astype(int), np.round(vb).astype(int)
for dx in (-2, -1, 0, 1, 2):
    for dy in (-2, -1, 0, 1, 2):
        np.minimum.at(zb, (np.clip(iv + dy, 0, H - 1), np.clip(iu + dx, 0, W - 1)), zb_)
u, v_, z, v = project(C)
visible = (z <= zb[np.clip(np.round(v_).astype(int), 0, H - 1), np.clip(np.round(u).astype(int), 0, W - 1)] + 0.05) & (u >= 0) & (u < W) & (v_ >= 0) & (v_ < H)
nw = np.stack([Nr[:, 0] * ct + Nr[:, 2] * st, Nr[:, 1], -Nr[:, 0] * st + Nr[:, 2] * ct], 1)
facing = -(nw * (v / np.linalg.norm(v, axis=1, keepdims=True))).sum(1)
wgt = np.clip((facing - 0.05) / 0.35, 0, 1) * visible
photo = np.array(Image.open(os.path.join(ROOT, 'brief', 'ref-poodle-candles.webp')).convert('RGB')).astype(float) / 255
blur = np.stack([ndi.gaussian_filter(photo[..., c], 1.2) for c in range(3)], -1)
col = np.stack([ndi.map_coordinates(blur[..., c], [v_, u], order=1, mode='nearest') for c in range(3)], 1)
ref = col[wgt > 0.5].mean(0)
mult = np.clip(1 + CONTRAST * (col / ref - 1), 0.4, 1.7)
spots = 0.97 + 0.06 * rng.rand(N)                                                                    # no two curls alike
rgb = (1 + wgt[:, None] * (mult - 1)) * spots[:, None]
shut = np.clip(ao[chosen] * 1.15, 0.45, 1.0)                                                         # curls in a fold are darker
rgb *= (1 - wgt[:, None] * 0 - (1 - shut[:, None]) * (1 - wgt[:, None] * 0.6))

name = os.path.splitext(os.path.basename(out))[0]
crl = f'assets/models/{name}.crl'
data = np.column_stack([C, Nr, S, rng.rand(N) * math.tau, 0.88 + 0.3 * rng.rand(N), rgb]).astype('<f4')
open(os.path.join(ROOT, crl), 'wb').write(data.tobytes())

curl_mat = dict(rec['materials']['coat']); curl_mat['color'] = os.environ.get('CURL_C', '#dd9a62'); curl_mat['bump'] = 0
rec['materials']['curl'] = curl_mat
core = dict(rec['materials']['coat']); core['color'] = os.environ.get('CORE_C', '#c08250'); core['sheen'] = 0; core['glow'] = 0.16
rec['materials']['core'] = core
body = dict(blob); body['material'] = 'core'; body.pop('relief', None); body.pop('paint', None); body['tones'] = []; body['paleK'] = 0; body['res'] = int(env('CORE_RES', '64')); body['bake'] = f'assets/models/{os.path.splitext(os.path.basename(out))[0]}-core.bin'  # the core is mostly hidden: a coarse one saves triangles
LIFT = env('LIFT', '0.009')                                                                          # eyes and nose stand at coat height, or the coat swallows them
lifted = []
for p in dots:
    p = dict(p); at = []
    for q in p['at']:
        q = np.array(q); at.append([round(float(v), 4) for v in q + nor[tree.query(q)[1]] * LIFT])
    p['at'] = at; lifted.append(p)
dots = lifted
rec['parts'] = [body, {'shape': 'tufts', 'material': 'curl', 'src': crl, 'detail': int(env('DETAIL', '1'))}] + dots
rec['name'] = 'the lying puppy, with real curls coloured from the photo'
open(out, 'w', encoding='utf-8').write(json.dumps(rec, ensure_ascii=False))
tri = 56                                                                                            # about 56 of the 80 faces: the foot of each curl is left out by the builder
print(f'{N} curls ({int((wgt > 0.5).sum())} coloured from the photo), {N * tri} triangles in curls, {data.nbytes // 1024} KB -> {crl}')
