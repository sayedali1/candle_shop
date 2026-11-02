"""Builds the duck pond as real 3D wearing her real wax: the shapes are solid and turn all the way round, and their surface comes from the photo, projected through the camera measured by tools/fit_ducks.py.
1. Each duck's outline is found by colour. 2. Each duck's place and size are fitted to that outline. 3. Every point takes its colour from the pixel the camera sees it at, kept inside its own part so no pond or
wood bleeds onto a duck. Points the photo never saw (backs) take the part's plain colour. The photo's light is partly removed, and its fine detail becomes a normal map so the flame lights it.
Run after baking the bodies:  python tools/gen_duck_skin.py      Writes assets/models/11-duck-skin.glb, recipes/11-duck-pond.json, tools/fit/pose-ducks.json, tools/fit/duck-fit.png"""
import io, json, math, os, struct, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
FIT = json.load(open(os.path.join(HERE, 'fit', 'ducks-fit.json'))); v, fov = FIT['v'], FIT['fov']
A, R = FIT['A'], FIT['R']; H_TRAY, POND = 0.09, 0.074; RIM = 0.042
W, H = 1083, 863; SIZE = 0.74
env = lambda k, d: float(os.environ.get(k, d))
yawc, pitch, ld = v[0], v[1], v[2]
dd = math.exp(ld); T0 = np.array([0.0, H_TRAY, 0.0])
Pc = T0 + dd * np.array([math.sin(yawc) * math.cos(pitch), math.sin(pitch), math.cos(yawc) * math.cos(pitch)])
fw = (T0 - Pc) / dd; rt = np.cross(fw, [0, 1, 0]); rt /= np.linalg.norm(rt); upv = np.cross(rt, fw); Fp = (H / 2) / math.tan(math.radians(fov) / 2)
cr, sr = math.cos(v[5]), math.sin(v[5])


def project(p):
    q = np.atleast_2d(p) - Pc; z = q @ fw; x = q @ rt / z * Fp; y = q @ upv / z * Fp
    return np.stack([W / 2 + v[3] + x * cr - y * sr, H / 2 + v[4] - (x * sr + y * cr)], 1)


def on_plane(px, py, y):
    x0, y0 = px - W / 2 - v[3], -(py - H / 2 - v[4]); c, s = math.cos(-v[5]), math.sin(-v[5])
    x, yy = x0 * c - y0 * s, x0 * s + y0 * c; d = fw + x / Fp * rt + yy / Fp * upv; d /= np.linalg.norm(d)
    return Pc + d * ((y - Pc[1]) / d[1])


def load_body(path):
    buf = open(path, 'rb').read(); magic, n, ni, isz = struct.unpack('<4I', buf[:16])
    mn = np.array(struct.unpack('<3f', buf[16:28])); rg = np.array(struct.unpack('<3f', buf[28:40]))
    up4 = lambda x: (x + 3) & ~3; oP = 48; oN = oP + up4(n * 6); oA = oN + up4(n * 3); oI = oA + up4(n * 3)
    pos = np.frombuffer(buf, '<u2', n * 3, oP).reshape(n, 3) / 65535.0 * rg + mn
    nor = np.frombuffer(buf, 'i1', n * 3, oN).reshape(n, 3).astype(float) / 127.0; nor /= np.linalg.norm(nor, axis=1, keepdims=True) + 1e-9
    idx = np.frombuffer(buf, '<u2' if isz == 2 else '<u4', ni, oI).astype(np.int64).reshape(-1, 3)
    return pos, nor, idx


def place(pos, x, z, yaw, S, ys=1.0):
    c, s = math.cos(yaw), math.sin(yaw)
    return np.stack([x + S * (pos[:, 0] * c + pos[:, 2] * s), POND + S * ys * pos[:, 1], z + S * (-pos[:, 0] * s + pos[:, 2] * c)], 1)


def turn_n(nor, yaw):
    c, s = math.cos(yaw), math.sin(yaw)
    return np.stack([nor[:, 0] * c + nor[:, 2] * s, nor[:, 1], -nor[:, 0] * s + nor[:, 2] * c], 1)


# ---------- 1. the photo's parts, by colour
photo = Image.open(os.path.join(ROOT, 'brief', 'ref-ducks.jpg')).convert('RGB'); arr = np.array(photo).astype(float) / 255
hsv = np.array(photo.convert('HSV')).astype(float); hue, sat, val = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
duck = (hue > 8) & (hue < 62) & (sat > .38) & (val > .5)
tray_px = project(np.column_stack([*(lambda t: (A * np.sign(np.cos(t)) + (R + .03) * np.cos(t), np.full_like(t, H_TRAY), (R + .03) * np.sin(t)))(np.linspace(0, 6.283, 200))]))
him = Image.new('L', (W, H), 0); ImageDraw.Draw(him).polygon([tuple(q) for q in tray_px], fill=255); hull = np.array(him) > 0
hull_tall = hull.copy(); hull_tall[:390] = hull[:390]
duck &= hull
duck[:380] = False
top = Image.new('L', (W, H), 0)
duck = ndi.binary_fill_holes(ndi.binary_closing(ndi.binary_opening(duck, iterations=1), iterations=3))
lab, n = ndi.label(duck)
for i in range(1, n + 1):
    if (lab == i).sum() < 400: duck[lab == i] = False
SEEDS = [(725, 500), (330, 475), (437, 455), (545, 455), (297, 545), (437, 520), (575, 525), (395, 600), (525, 585)]   # one point inside each duck, to split the pairs that touch
yy, xx = np.mgrid[0:H, 0:W]; d2 = np.stack([(xx - a) ** 2 + (yy - b) ** 2 * (1.0 if j else 0.6) - (1e5 if j == 0 else 0) * 0 for j, (a, b) in enumerate(SEEDS)], 0)
d2[0] = (xx - 725) ** 2 / 4.0 + (yy - 490) ** 2 / 4.0                   # the big duck reaches further
own = np.argmin(d2, 0); masks = [duck & (own == j) for j in range(len(SEEDS))]
masks = [(lambda m: (lambda L, N: L == (1 + np.argmax(ndi.sum(m, L, range(1, N + 1)))))(*ndi.label(m)))(m) for m in masks]
blue = (hue > 180) & (hue < 245) & (sat > .15) & (val > .35) & hull & ~ndi.binary_dilation(duck, iterations=2)
pale = (sat < .42) & (val > .5) & ~ndi.binary_dilation(duck, iterations=2) & ~ndi.binary_dilation(blue, iterations=1)
near_tray = ndi.binary_dilation(hull, iterations=45); pale &= near_tray; pale[:400] = False
clamp_ix = lambda m: ndi.distance_transform_edt(~m, return_distances=False, return_indices=True)

# ---------- 2. place and size of each duck, fitted to its outline
bodies = {'big': load_body(os.path.join(ROOT, 'assets', 'models', 'duck-big.bin')), 'small': load_body(os.path.join(ROOT, 'assets', 'models', 'duck-small.bin'))}


def score(body, m, x, z, yaw, S, ys=1.0, ds=2):
    q = project(place(body[0], x, z, yaw, S, ys)) / ds; h, w = H // ds, W // ds; sil = np.zeros((h, w), bool)
    ix, iy = np.clip(q[:, 0].astype(int), 0, w - 1), np.clip(q[:, 1].astype(int), 0, h - 1); sil[iy, ix] = True
    sil = ndi.binary_fill_holes(ndi.binary_closing(sil, iterations=3)); mm = m[::ds, ::ds][:h, :w]
    ys_, xs_ = np.where(sil); my, mx = np.where(mm)
    box = (abs(ys_.min() - my.min()) + abs(ys_.max() - my.max()) + abs(xs_.min() - mx.min()) + abs(xs_.max() - mx.max())) / max(my.max() - my.min(), 1)   # the top, bottom and sides must match too, or a duck gets flattened to fit the area
    return (sil & mm).sum() / max((sil | mm).sum(), 1) - .25 * box


placed = []
for j, k in enumerate(FIT['ducks']):
    body = bodies['big' if j == 0 else 'small']; x, z, S = k['x'], k['z'], k['S']; yaw = k['yaw']
    st = np.array([.02, .02, .08, .08]) * (1 if j == 0 else .5); ys = 1.0; best = score(body, masks[j], x, z, yaw, S, ys)   # height is fitted apart from width: her ducks are not all my proportions
    for it in range(36):
        moved = False
        for a, sg in ((0, 1), (0, -1), (1, 1), (1, -1), (2, 1), (2, -1), (3, 1), (3, -1)) + (((4, 1), (4, -1)) if j == 0 else ()):
            nx, nz, nS, ny, nyw = x, z, S, ys, yaw
            if a == 0: nx += sg * st[0]
            elif a == 1: nz += sg * st[1]
            elif a == 2: nS *= math.exp(sg * st[2])
            elif a == 3: ny = min(1.8, max(.7, ny * math.exp(sg * st[3])))
            else: nyw = yaw + sg * st[3] * 1.5                                          # its direction too: a beak's two pixels are not enough to know it
            s = score(body, masks[j], nx, nz, nyw, nS, ny)
            if s > best + 1e-4: x, z, S, ys, yaw, best, moved = nx, nz, nS, ny, nyw, s, True
        if not moved: st *= .6
    placed.append((x, z, yaw, S, ys)); print(f'duck {j}: x {x:+.3f} z {z:+.3f} size {S:.3f} height x{ys:.2f}, outline overlap {best * 100:.0f}%')

# ---------- 3. the skin
X0, X1, Y0, Y1 = 190, 880, 370, 730
crop = arr[Y0:Y1, X0:X1]; L = ndi.gaussian_filter(crop.mean(-1), 42); keep_light = env('LIGHT', '0.45')
flat = np.clip(crop * ((L.mean() / L) ** (1 - keep_light))[..., None], 0, 1)         # most of the photo's sunlight comes out, so the flame can do the lighting
SWH = 24; TRH = 90; aw, ah = X1 - X0, Y1 - Y0; TOT = 2 * ah + SWH + TRH
swatches = {'yellow': arr[masks[0]].mean(0), 'small': arr[masks[1]].mean(0), 'tray': np.array([.86, .81, .73]), 'pond': arr[blue].mean(0)}
atlas = np.zeros((TOT, aw, 3)); atlas[:ah] = flat
strict = ndi.binary_erosion(blue, iterations=5)[Y0:Y1, X0:X1]                         # the pond's own picture: where a duck or its shadow stood, the blue around it flows in, so nothing shows when the candle turns
wgt = ndi.gaussian_filter(strict.astype(float), 22) + 1e-4
pond_fill = np.stack([ndi.gaussian_filter(flat[..., c] * strict, 22) / wgt for c in range(3)], -1)
ramp = ndi.gaussian_filter(strict.astype(float), 2)[..., None]
atlas[ah + SWH:2 * ah + SWH] = flat * ramp + pond_fill * (1 - ramp)
rng = np.random.RandomState(4); tr_band = np.ones((TRH, aw, 3)) * swatches['tray'] * (1 + .03 * ndi.gaussian_filter(rng.randn(TRH, aw), 6) * 6)[..., None]   # her tray is pale stone with fine dark and pale specks
for _ in range(aw * TRH // 60):
    yy_, xx_ = rng.randint(0, TRH), rng.randint(0, aw); tr_band[yy_, xx_] *= rng.uniform(.62, 1.08)
atlas[2 * ah + SWH:] = np.clip(tr_band, 0, 1)
for i, c in enumerate(swatches.values()): atlas[ah:ah + SWH, i * aw // 4:(i + 1) * aw // 4] = np.clip(c * 1.02, 0, 1)
sw_uv = {name: ((i + .5) / 4, (ah + SWH / 2) / TOT) for i, name in enumerate(swatches)}
to_uv = lambda q: np.stack([(q[:, 0] - X0 + .5) / aw, (q[:, 1] - Y0 + .5) / TOT], 1)
gray = np.array(photo.convert('L').crop((X0, Y0, X1, Y1))).astype(float) / 255
TS = 2; g2 = np.array(Image.fromarray((gray * 255).astype(np.uint8)).resize((aw * TS, ah * TS), Image.LANCZOS)).astype(float) / 255
h_ = g2 - ndi.gaussian_filter(g2, 4 * TS); h_ = ndi.gaussian_filter(h_, .5 * TS); BUMP = env('BUMP', '3.5') * TS
nx_, ny_ = -ndi.sobel(h_, axis=1) / 8 * BUMP, ndi.sobel(h_, axis=0) / 8 * BUMP; nl = np.sqrt(nx_ ** 2 + ny_ ** 2 + 1)
nimg = Image.new('RGB', (aw * TS, TOT * TS), (128, 128, 255)); nimg.paste(Image.fromarray(((np.dstack([nx_ / nl, ny_ / nl, 1 / nl]) * .5 + .5) * 255).astype(np.uint8)), (0, 0))

Vs, Ns, Us, Is = [], [], [], []; base = 0


def add(pos, nor, uv, idx):
    global base
    Vs.append(pos); Ns.append(nor); Us.append(uv); Is.append(idx + base); base += len(pos)


def skin(pos, nor, mask, plain, force_plain=False):
    q = project(pos); iy, ix = clamp_ix(mask); qi = np.clip(np.round(q).astype(int), [0, 0], [W - 1, H - 1])
    uv = to_uv(np.stack([ix[qi[:, 1], qi[:, 0]], iy[qi[:, 1], qi[:, 0]]], 1).astype(float))
    view = Pc - pos; view /= np.linalg.norm(view, axis=1, keepdims=True); face = (nor * view).sum(1)
    uv[face < .03] = sw_uv[plain]
    if force_plain:                                                                    # the tray: its own speckled band, laid across it from above
        L_ = A + R
        if abs(nor[0, 1]) < .5:                                                        # a wall: around the tray and up its height, so the specks keep their shape
            uv[:, 0] = np.arctan2(pos[:, 2], pos[:, 0]) / (2 * math.pi) % 1; uv[:, 1] = (2 * ah + SWH + 2 + pos[:, 1] / H_TRAY * 14) / TOT
        else:
            uv[:, 0] = (pos[:, 0] + L_) / (2 * L_); uv[:, 1] = (2 * ah + SWH + 2 + (pos[:, 2] + R) / (2 * R) * (TRH - 4)) / TOT
    return uv


for j, (x, z, yaw, S, ys) in enumerate(placed):
    body = bodies['big' if j == 0 else 'small']; p = place(body[0], x, z, yaw, S, ys); nn = turn_n(body[1], yaw)
    plain = 'yellow' if j == 0 else 'small'; uv = skin(p, nn, masks[j], plain); idx = body[2]
    pv = np.array(sw_uv[plain]); hidden = np.all(np.isclose(uv, pv), axis=1)
    mixed = hidden[idx].any(1) & ~hidden[idx].all(1)                                                         # a triangle on the edge between seen and unseen would stretch across the whole picture: it takes the plain colour, with its own points
    keep_i = idx[~mixed]; mi = idx[mixed].ravel()
    add(np.vstack([p, p[mi]]), np.vstack([nn, nn[mi]]), np.vstack([uv, np.tile(pv, (len(mi), 1))]), np.vstack([keep_i, np.arange(len(p), len(p) + len(mi)).reshape(-1, 3)]))


def outline(a, r, n=180):
    t = np.linspace(0, 2 * math.pi, n, endpoint=False); cx, sx = np.cos(t), np.sin(t)
    px = a * np.sign(cx) + r * cx; pz = r * sx; nx = cx; nz = sx
    return np.column_stack([px, pz]), np.column_stack([nx, nz])


def strip(a_xy, ya, b_xy, yb, nor, mask, plain, force_plain=False):
    n = len(a_xy); p = np.vstack([np.column_stack([a_xy[:, 0], np.full(n, ya), a_xy[:, 1]]), np.column_stack([b_xy[:, 0], np.full(n, yb), b_xy[:, 1]])])
    ni = np.vstack([nor, nor]); idx = []
    for i in range(n):
        j = (i + 1) % n; idx += [[i, j, i + n], [j, j + n, i + n]]
    add(p, ni, skin(p, ni, mask, plain, force_plain), np.array(idx))


o, on = outline(A, R); i_, _ = outline(A, R - RIM); UP = np.tile([0.0, 1.0, 0.0], (len(o), 1))
sideN = np.column_stack([on[:, 0], np.zeros(len(on)), on[:, 1]])
strip(o, H_TRAY, i_, H_TRAY, UP, pale, 'tray', True)                                       # the rim's top
strip(o, 0.0, o, H_TRAY, sideN, pale, 'tray', True)                                        # the outer wall
strip(i_, H_TRAY, i_, POND, -sideN, pale, 'tray', True)                                    # the step down to the pond
rings = [(R - RIM) * t / (R - RIM) for t in np.linspace(R - RIM, .02, 6)]
prev = i_
for t in np.linspace(1, .05, 6)[1:]:
    nxt = np.column_stack([i_[:, 0] * t, i_[:, 1] * t]); n0 = len(Us); strip(prev, POND, nxt, POND, UP, hull, 'pond'); prev = nxt
    Us[n0][:, 1] += (ah + SWH) / TOT

V = np.vstack(Vs); N = np.vstack(Ns); U = np.vstack(Us); I = np.vstack(Is)
# winding: every triangle faces along its normal
fn = np.cross(V[I[:, 1]] - V[I[:, 0]], V[I[:, 2]] - V[I[:, 0]]); flip = (fn * N[I[:, 0]]).sum(1) < 0; I[flip] = I[flip][:, [0, 2, 1]]

# ---------- the frame: the photo's camera straight in front, the wick at z = 0 (the page's flame burns there)
TH = -yawc; ct, st = math.cos(TH), math.sin(TH)
rotp = lambda P: np.stack([P[..., 0] * ct + P[..., 2] * st, P[..., 1], -P[..., 0] * st + P[..., 2] * ct], -1)
xb, zb, yb_, Sb, ysb = placed[0]
bigp = place(bodies['big'][0], xb, zb, yb_, Sb, ysb); wick_base = bigp[np.argmax(bigp[:, 1])]      # the wick stands on the very top of the big duck's head
wb = rotp(wick_base); shift = np.array([0.0, 0.0, -wb[2]])
V = rotp(V) + shift; N = rotp(N); wb = wb + shift

buf = io.BytesIO(); Image.fromarray((np.clip(atlas, 0, 1) * 255).astype(np.uint8)).save(buf, 'JPEG', quality=90); jpg = buf.getvalue()
b2 = io.BytesIO(); nimg.save(b2, 'JPEG', quality=86); nj = b2.getvalue()
V4, N4, U4, I4 = V.astype('<f4'), N.astype('<f4'), U.astype('<f4'), I.astype('<u4')
pad = lambda b: b + b'\0' * ((4 - len(b) % 4) % 4); views, blob = [], b''
for raw, target in ((V4.tobytes(), 34962), (N4.tobytes(), 34962), (U4.tobytes(), 34962), (I4.tobytes(), 34963), (jpg, None), (nj, None)):
    w = {'buffer': 0, 'byteOffset': len(blob), 'byteLength': len(raw)}
    if target: w['target'] = target
    views.append(w); blob += pad(raw)
gltf = {'asset': {'version': '2.0', 'generator': 'gen_duck_skin.py'}, 'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'mesh': 0}],
        'meshes': [{'primitives': [{'attributes': {'POSITION': 0, 'NORMAL': 1, 'TEXCOORD_0': 2}, 'indices': 3, 'material': 0}]}],
        'materials': [{'pbrMetallicRoughness': {'baseColorTexture': {'index': 0}, 'metallicFactor': 0, 'roughnessFactor': .55}, 'normalTexture': {'index': 1}}],
        'textures': [{'source': 0, 'sampler': 0}, {'source': 1, 'sampler': 0}], 'samplers': [{'magFilter': 9729, 'minFilter': 9729, 'wrapS': 33071, 'wrapT': 33071}],
        'images': [{'bufferView': 4, 'mimeType': 'image/jpeg'}, {'bufferView': 5, 'mimeType': 'image/jpeg'}], 'bufferViews': views, 'buffers': [{'byteLength': len(blob)}],
        'accessors': [{'bufferView': 0, 'componentType': 5126, 'count': len(V4), 'type': 'VEC3', 'min': V4.min(0).tolist(), 'max': V4.max(0).tolist()},
                      {'bufferView': 1, 'componentType': 5126, 'count': len(N4), 'type': 'VEC3'}, {'bufferView': 2, 'componentType': 5126, 'count': len(U4), 'type': 'VEC2'},
                      {'bufferView': 3, 'componentType': 5125, 'count': int(I4.size), 'type': 'SCALAR'}]}
js = json.dumps(gltf, separators=(',', ':')).encode(); js += b' ' * ((4 - len(js) % 4) % 4)
path = os.path.join(ROOT, 'assets', 'models', '11-duck-skin.glb')
with open(path, 'wb') as fh:
    fh.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob))); fh.write(struct.pack('<II', len(js), 0x4E4F534A)); fh.write(js); fh.write(struct.pack('<II', len(blob), 0x004E4942)); fh.write(blob)
F = lambda *a: [round(float(q), 4) for q in a]
ty = float(wb[1])
recipe = {'name': 'a rubber duck and eight ducklings on a marbled pond, solid shapes wearing the photo', 'turn': 0, 'size': SIZE, 'shadow': 2.1, 'model': 'assets/models/11-duck-skin.glb', 'modelRaw': True, 'modelGlow': .42, 'modelGlowColor': '#fff4e6', 'modelRough': .55, 'modelEnv': .4,
          'flameLight': .2, 'flameLightPhone': .35, 'shelfSize': 1.42, 'shelfTilt': .24,
          'materials': {'white': {'kind': 'wax', 'color': '#fbf6ea', 'roughness': .5, 'bump': 0, 'glow': .1}},
          'parts': [{'shape': 'torus', 'material': 'white', 'r': .017, 'tube': .0045, 'pos': F(wb[0] + .004, ty + .022, 0), 'rot': [math.pi / 2, 0, 0]}],
          'wicks': [{'kind': 'long', 'x': round(float(wb[0]), 3), 'z': 0, 'base': round(ty + .03, 3), 'tip': round(ty + .045, 3), 'color': '#f5f0e2', 'radius': .006}], 'flame': {'size': .4, 'width': 1.0}}
open(os.path.join(ROOT, 'recipes', '11-duck-pond.json'), 'w', encoding='utf-8').write(json.dumps(recipe, ensure_ascii=False))
Tg = (rotp(T0) + shift) * SIZE
json.dump({'camera': {'yaw': 0.0, 'pitch': pitch, 'fov': fov, 'target': [float(q) for q in Tg], 'dist': dd * SIZE}, 'blocks': []}, open(os.path.join(HERE, 'fit', 'pose-ducks.json'), 'w'), indent=1)
over = photo.copy(); dr = ImageDraw.Draw(over)
for j, (x, z, yaw, S, ys) in enumerate(placed):
    q = project(place(bodies['big' if j == 0 else 'small'][0], x, z, yaw, S, ys)); ix = np.clip(q[:, 0].astype(int), 0, W - 1); iy = np.clip(q[:, 1].astype(int), 0, H - 1)
    for a, b in zip(ix[::3], iy[::3]): dr.point((a, b), fill=(255, 0, 255))
over.crop((170, 340, 900, 740)).save(os.path.join(HERE, 'fit', 'duck-fit.png'))
print(f'{len(V4)} points, {len(I4)} triangles, {os.path.getsize(path) // 1024} KB -> {path}')
