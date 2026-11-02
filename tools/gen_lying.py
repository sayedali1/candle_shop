"""Writes the recipe of the LYING puppy alone, from the blocks fitted to the photo (tools/fit/pose.json).
Run:  python tools/gen_lying.py [recipe-out] [res]      then  node tools/bake-blob.mjs <recipe> assets/models/<name>.bin 96"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
import numpy as np
sys.path.insert(0, HERE)
pose = json.load(open(os.path.join(HERE, 'fit', 'pose.json')))
FACE = os.path.join(HERE, 'fit', 'pose-face.json')                       # the head and near ear fitted to marked regions of the photo (fit_face.py)
face_fit = json.load(open(FACE)) if os.path.exists(FACE) else None
if face_fit:
    for b in pose['blocks']:
        if b['name'] == 'head': b['c'], b['r'] = face_fit['head']['c'], face_fit['head']['r']
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'recipes', 'zz-lying.json')
res = int(sys.argv[2]) if len(sys.argv) > 2 else 64
F = lambda *a: [round(v, 3) for v in a]
SIZE, TURN = 0.78, -0.12
W, H = 652, 863
LAND = {'eye_near': (412, 568), 'eye_far': (442, 563), 'nose': (450, 597), 'ear_near': (362, 580)}     # read off the photo (full-photo pixels, see tools/fit/face-grid.png)
cam = pose['camera']
def ray(px, py):
    yaw, pitch, fov = cam['yaw'], cam['pitch'], cam['fov']; T = np.array(cam['target']); r = cam['dist']
    P = T + r * np.array([math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch)])
    f = (T - P) / np.linalg.norm(T - P); right = np.cross(f, [0, 1, 0]); right /= np.linalg.norm(right); up = np.cross(right, f)
    t = math.tan(math.radians(fov) / 2); d = ((px / W * 2 - 1) * (W / H) * t) * right + (-(py / H * 2 - 1) * t) * up + f
    return P, d / np.linalg.norm(d)
def to_candle(w):                                                        # world -> candle space (undo size, then the recipe's turn)
    ct, st = math.cos(-TURN), math.sin(-TURN); w = np.array(w) / SIZE
    return np.array([w[0] * ct + w[2] * st, w[1], -w[0] * st + w[2] * ct])
def _ell(c, r, rot, p):
    d = p - np.array(c); ca, sa = math.cos(rot), math.sin(rot)
    q = np.array([ca * d[0] - sa * d[2], d[1], sa * d[0] + ca * d[2]])                       # world->local for a turn about y
    a = q / np.array(r); k0 = np.linalg.norm(a); k1 = np.linalg.norm(a / np.array(r))
    return k0 * (k0 - 1) / k1 if k1 > 1e-9 else -min(r)
def sdf(p, items, cuts=()):
    dd = None
    for e in items:
        d = _ell(e['c'], e['r'], e['rot'][1], p)
        if dd is None: dd = d
        else:
            h = max(0.07 - abs(dd - d), 0) / 0.07; dd = min(dd, d) - h * h * 0.07 * 0.25
    return dd
def ray_local(px, py):
    P, d = ray(px, py); ct, st = math.cos(-TURN), math.sin(-TURN)
    return to_candle(P), np.array([d[0] * ct + d[2] * st, d[1], -d[0] * st + d[2] * ct])
def surface(px, py, items):
    """the true point on the blended body that the photo's pixel sees (ray marched through the body's own distances), candle space, and its outward direction"""
    P, d = ray(px, py); o = to_candle(P); ct, st = math.cos(-TURN), math.sin(-TURN)
    dl = np.array([d[0] * ct + d[2] * st, d[1], -d[0] * st + d[2] * ct]); t = 0.0
    for _ in range(400):
        q = o + dl * t; dist = sdf(q, items)
        if dist < 0.002: break
        t += max(dist * 0.9, 0.002)
        if t > 12: return None, None
    q = o + dl * t; e = 0.004
    n = np.array([sdf(q + np.eye(3)[i] * e, items) - sdf(q - np.eye(3)[i] * e, items) for i in range(3)]); n /= np.linalg.norm(n) + 1e-9
    return q, n
def hit(block, px, py, grow=1.0):
    """where the photo's pixel lands on a block (nearest surface point, candle space) and the surface's sideways direction there"""
    P, d = ray(px, py); c = np.array(block['c']); ct, st = math.cos(TURN), math.sin(TURN)
    w = np.array([SIZE * (c[0] * ct + c[2] * st), SIZE * c[1], SIZE * (-c[0] * st + c[2] * ct)])
    ang = block['rot'] + TURN; ca, sa = math.cos(ang), math.sin(ang); Rinv = np.array([[ca, 0, -sa], [0, 1, 0], [sa, 0, ca]])
    rr = np.array(block['r']) * SIZE * grow; o = (Rinv @ (P - w)) / rr; dd = (Rinv @ d) / rr
    a = dd @ dd; b = dd @ o; cq = o @ o - 1; disc = b * b - a * cq
    if disc < 0: return None, None
    t = (-b - math.sqrt(disc)) / a; q = P + d * t
    n = Rinv.T @ ((Rinv @ (q - w)) / rr ** 2); n /= np.linalg.norm(n)
    return to_candle(q), to_candle(q + n * 0.01) - to_candle(q)
a1 = math.radians(52); f1 = (math.sin(a1), math.cos(a1)); l1 = (math.cos(a1), -math.sin(a1))
els, cuts, by = [], [], {}
for b in pose['blocks']:
    by.setdefault(b['name'], []).append(b)
    if b['name'] not in ('muzzle', 'ear'): els.append({'c': F(*b['c']), 'r': F(*b['r']), 'rot': F(0, b['rot'], 0)})
head = by['head'][0]; hc = head['c']; mz = by['muzzle'][0]
# toes at the end of each front paw, with a groove between them
for p in by['paw2']:
    tip = p['c'][0] + p['r'][0]
    zr = p['r'][2]
    for dz in (-0.62 * zr, 0.0, 0.62 * zr): els.append({'c': F(tip - 0.015 + (0.012 if dz == 0 else 0.0), p['c'][1] - 0.01, p['c'][2] + dz), 'r': F(0.028, 0.026, 0.4 * zr), 'rot': F(0, 0, 0)})
    for dz in (-0.31 * zr, 0.31 * zr): cuts.append({'c': F(tip + 0.03, p['c'][1] - 0.012, p['c'][2] + dz), 'r': F(0.04, 0.035, 0.007), 'rot': F(0, 0, 0)})
eyes0 = [hit(head, *LAND[k])[0] for k in ('eye_near', 'eye_far')]
# the ears: flat plates on the sides of the head, hanging; the sideways axis of the head is the line from one eye to the other
EAR_R = (0.075, 0.17, 0.12)
h3 = np.array(hc); lat3 = eyes0[1] - eyes0[0]; lat3[1] = 0; lat3 /= np.linalg.norm(lat3)
if face_fit:                                                            # the near ear as fitted to its region of the photo; the far one is its mirror across the head
    en = face_fit['ear']; near = np.array(en['c']); FAR_K = float(os.environ.get('FAR_K', '0.55'))
    far = h3 - FAR_K * np.dot(near - h3, lat3) * lat3; far[1] = near[1]                 # the far ear hides behind the head: nearer the head than a plain mirror would put it
    els.append({'c': F(*near), 'r': F(*en['r']), 'rot': F(0, en['rot'], 0)}); EAR_NEAR = els[-1]
    els.append({'c': F(*far), 'r': F(*[v * 0.9 for v in en['r']]), 'rot': F(0, en['rot'], 0)})
else:
    EAR_OFF = float(head['r'][2]) * 1.0 + 0.03
    for sgn in (1, -1):
        c3 = h3 + lat3 * sgn * EAR_OFF + np.array([-0.03 * f1[0], -0.1, -0.03 * f1[1]])
        els.append({'c': F(*c3), 'r': F(*EAR_R), 'rot': F(0, math.atan2(-lat3[2], lat3[0]), 0)})
# the muzzle is part of the same wax (a forward block of the head), and a paler wax colour is mixed in around it, softly
# the nose is not on the fitted head (the head fit only knows the outline): put it at the same distance from the camera as the eyes, on the nose's own pixel
eq = [surface(*LAND[k], els)[0] for k in ('eye_near', 'eye_far')]
o_, dl_ = ray_local(*LAND['nose']); t_eye = float(np.mean([np.linalg.norm(q - o_) for q in eq]))
nose_pt = o_ + dl_ * t_eye
qn, nn = hit(head, *LAND['nose'])                                          # with the fitted head the nose pixel lands on the head itself
if qn is not None: nose_pt = qn
# depth fixes (tools/depth_check.py): the silhouette fit cannot see depth, so shift parts ALONG the camera's ray, which leaves their outline where it is
vd = np.array(dl_, float); vd /= np.linalg.norm(vd)                      # from the camera into the scene
EAR_BACK, MZ_PUSH, TOP_PUSH = (float(os.environ.get(k, v)) for k, v in (('EAR_BACK', '-0.02'), ('MZ_PUSH', '0.09'), ('TOP_PUSH', '0.03')))
if face_fit: EAR_NEAR['c'] = F(*(np.array(EAR_NEAR['c']) + vd * EAR_BACK))                 # the ear lies closer against the head
nose_pt = nose_pt - vd * MZ_PUSH                                          # the muzzle (and the chin and cheeks that hang off it) comes forward
face = np.array([lat3[2], 0.0, -lat3[0]]); face /= np.linalg.norm(face)
if face[0] < 0: face = -face                                            # the face looks to the right
MZ_R = (0.115, 0.075, 0.085)
mz_rot = math.atan2(-face[2], face[0])                                  # the muzzle's long side points the way the face looks
MZ = {'c': F(*(nose_pt - face * 0.05)), 'r': F(*MZ_R), 'rot': F(0, mz_rot, 0)}
els.append(MZ)
tones = [{'c': MZ['c'], 'r': F(*[v * 2.6 for v in MZ_R]), 'rot': MZ['rot']}]
# brow, topknot, chin and a mouth line: the shapes that make it a poodle's face and not a ball, placed from the eyes and the muzzle
up_ = np.array([0.0, 1.0, 0.0]); E_ = (eyes0[0] + eyes0[1]) / 2; lat_rot = math.atan2(-lat3[2], lat3[0])
els.append({'c': F(*(E_ + up_ * 0.075 - face * 0.025)), 'r': F(0.125, 0.05, 0.09), 'rot': F(0, lat_rot, 0)})                     # the brow: a fluffy ridge over the eyes
els.append({'c': F(*(h3 + up_ * float(head['r'][1]) * 0.45 - vd * TOP_PUSH)), 'r': F(0.115, 0.06, 0.115), 'rot': F(0, 0, 0)})                       # the topknot
els.append({'c': F(*(np.array(MZ['c']) - up_ * 0.04)), 'r': F(0.07, 0.045, 0.06), 'rot': MZ['rot']})                               # the chin
ls_ = lat3 if lat3[2] > 0 else -lat3                                    # the sideways direction that points to the camera's side
for sg_, sz_, off_ in ((1, 1.0, 0.075), (-1, 0.7, 0.03)):                                    # puffy cheeks either side of the muzzle (the far one a little smaller, it is mostly hidden)
    els.append({'c': F(*(np.array(MZ['c']) + ls_ * sg_ * off_ + up_ * 0.012 - face * 0.05)), 'r': F(0.08 * sz_, 0.065 * sz_, 0.07 * sz_), 'rot': MZ['rot']})
cuts.append({'c': F(*(np.array(MZ['c']) + face * 0.01 - up_ * 0.03)), 'r': F(0.06, 0.007, 0.04), 'rot': MZ['rot']})                # the mouth line
SK_PUSH, SK_S = float(os.environ.get('SK_PUSH', '0.07')), float(os.environ.get('SK_S', '0.92'))
if SK_S > 0: els.append({'c': F(*(h3 - vd * SK_PUSH + up_ * 0.01)), 'r': F(*[float(v) * SK_S for v in head['r']]), 'rot': F(0, head['rot'], 0)})        # a skull that bulges toward the camera: the head is one rounded bump in the photo, not a flat block with a muzzle on it
if face_fit:                                                            # the ear's edge: a crease cut along the side of the ear that faces the muzzle, so the ear reads as a separate hanging flap
    EG_W, EG_D = float(os.environ.get('EG_W', '0.028')), float(os.environ.get('EG_D', '0.10'))
    a_ = EAR_NEAR['rot'][1]; zw = np.array([math.sin(a_), 0.0, math.cos(a_)])
    if np.dot(zw, face) < 0: zw = -zw
    er = EAR_NEAR['r']
    EG_Z = float(os.environ.get('EG_Z', '0.07'))                        # how far toward the camera the crease sits: past the skull's own bulge
    cuts.append({'c': F(*(np.array(EAR_NEAR['c']) + zw * er[2] * 0.97 - vd * EG_Z)), 'r': F(EG_D, er[1] * 0.92, EG_W), 'rot': EAR_NEAR['rot']})
# eyes and nose sit exactly where the photo shows them: the photo's pixel is followed through the camera onto the body's own surface
def on_surface(key, sink):
    q, n = surface(*LAND[key], els)
    return (q - n * sink) if q is not None else None
eyes = [on_surface('eye_near', 0.006), on_surface('eye_far', 0.006)]
rims = [on_surface('eye_near', 0.012), on_surface('eye_far', 0.012)]       # a darker, larger, flatter lid-rim bead just behind each eye: reads as the dark outline around an almond eye
for k_ in ('eye_near', 'eye_far'):                                         # a small dimple around each eye bead, so the eyes sit IN the face
    qe, ne = surface(*LAND[k_], els)
    if qe is not None: cuts.append({'c': F(*(qe + ne * 0.02)), 'r': F(0.034, 0.03, 0.03), 'rot': F(0, 0, 0)})
qs, ns = surface(*LAND['nose'], els)                                       # the nose bead sits on the muzzle's own surface, on the nose pixel
nose = (qs - ns * 0.01) if qs is not None else nose_pt
if any(v is None for v in eyes + [nose]): raise SystemExit('a landmark missed the body: check the fit')
els = [e for e in els]
coat = lambda c: {'kind': 'wax', 'color': c, 'roughness': 0.62, 'bump': 0, 'sheen': 0.5, 'sheenColor': '#ffe2c0', 'sheenRoughness': 0.55, 'clearcoat': 0.1, 'clearcoatRoughness': 0.55, 'glow': 0.28, 'glowColor': '#ff9a50'}
name = os.path.splitext(os.path.basename(out))[0]
recipe = {
    'name': 'the lying poodle puppy alone, fitted to the photo outline', 'turn': -0.12, 'size': 0.78, 'shadow': 1.4,
    'materials': {'coat': coat('#e09960'),
                  'muzzle': {'kind': 'matte', 'color': '#efc9aa', 'roughness': 0.85, 'sheen': 0.4, 'sheenRoughness': 0.6, 'sheenColor': '#fff0dc', 'glow': 0.18, 'glowColor': '#ff9a50'},
                  'rim': {'kind': 'matte', 'color': '#4a2a1a', 'roughness': 0.8, 'sheen': 0.2, 'sheenRoughness': 0.6, 'sheenColor': '#c89068'},
                  'ink': {'kind': 'solid', 'color': '#100907', 'roughness': 0.2, 'clearcoat': 1, 'clearcoatRoughness': 0.06}},
    'parts': [
        {'shape': 'blob', 'material': 'coat', 'res': res, 'glowThin': 1.6, 'bake': f'assets/models/{name}.bin', 'paint': f'assets/models/{name}.col', 'k': 0.07, 'clipY': 0.0, 'box': {'c': [0.12, 0.33, 0.0], 'h': 0.74}, 'els': els, 'cuts': cuts, 'tones': tones, 'pale': '#f7dcc0', 'paleK': 0.35, 'relief': {'scale': 0.95, 'depth': 0.013, 'calm': 0.5, 'fine': 1.3}},
        {'shape': 'dots', 'material': 'rim', 'r': 0.016, 'scale': [1.9, 1.2, 0.6], 'rot': round(float(lat_rot), 3), 'at': [F(*q) for q in rims]},
        {'shape': 'dots', 'material': 'ink', 'r': 0.016, 'scale': [1.45, 0.88, 0.6], 'rot': round(float(lat_rot), 3), 'at': [F(*q) for q in eyes]},
        {'shape': 'dots', 'material': 'ink', 'r': 0.024, 'scale': [1.1, 0.85, 0.95], 'at': [F(*nose)]}],
    'wicks': [{'kind': 'long', 'x': round(hc[0], 3), 'z': round(hc[2], 3), 'base': round(hc[1] + head['r'][1] - 0.02, 3), 'tip': round(hc[1] + head['r'][1] + 0.14, 3), 'color': '#efe3cf', 'radius': 0.014}],
    'flame': {'size': 0.85, 'width': 1.0}}
open(out, 'w', encoding='utf-8').write(json.dumps(recipe, ensure_ascii=False))
print('blocks', len(els), 'cuts', len(cuts), '->', out)
