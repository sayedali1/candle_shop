"""The dried baby's breath as real tiny 3D florets, read off the photo (the user's choice: "real tiny clusters").
Each floret is found by colour (cream florets: warm, yellowish; dark-pink florets: magenta), one per bright spot at least SPACING px apart, its size
from the spot's own width. Each one becomes a small bead on the photo surface at its pixel (the nearest front point of the surface built by
tools/gen_relief.py), lifted toward the camera by its own radius, so it sits ON the surface. Hidden florets (behind flowers) are not built.
Run after gen_relief:  python tools/gen_florets.py <recipe name> <photo>      Adds parts 'floret_cream' / 'floret_pink' to the recipe;
writes tools/fit/florets-<name>.png (every floret found, on the photo, to check by eye)."""
import json, math, os, struct, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); SIZE = 0.78
name, photo = sys.argv[1], sys.argv[2]; SPACING = int(os.environ.get('SPACING', '7'))
im = Image.open(os.path.join(ROOT, photo)).convert('RGB'); A = np.array(im).astype(float); H, W = A.shape[:2]
R_, G_, B_ = A[..., 0], A[..., 1], A[..., 2]
inside = np.load(os.path.join(HERE, 'fit', os.environ.get('MASK', 'heart-a-mask.npy')))
if os.environ.get('ZONE'):                                                            # only where the dried flowers are (a polygon read by hand): the jute bow on the lid has the same colour
    zm = Image.new('L', (W, H), 0); ImageDraw.Draw(zm).polygon([tuple(q) for q in json.loads(os.environ['ZONE'])], fill=1); inside = inside & (np.array(zm) > 0)
cream = inside & (R_ > 165) & (G_ - B_ > 30) & (R_ - G_ < 50) & (G_ > 140)
pink = inside & (R_ > 150) & (R_ - G_ > 70) & (B_ - G_ > 5)                            # magenta: red high, blue a little above green
pink &= ~ndi.binary_dilation(ndi.binary_opening(inside & (R_ > 190) & (G_ > 110) & (B_ > 140), iterations=5), iterations=5)   # not the pink wax flowers (large, paler)
L = ndi.gaussian_filter(A.mean(2), 1.0)


def spots(mask):
    mk = ndi.binary_opening(mask, iterations=1)
    peak = (L == ndi.maximum_filter(L, size=SPACING)) & mk
    ys, xs = np.where(peak); dist = ndi.distance_transform_edt(mk)
    return xs, ys, np.clip(dist[ys, xs], 1.5, 6)                     # radius (px): how far the spot reaches inside its own colour


# the surface: front vertices of the GLB, and the pixel each came from (gen_relief's UV: u = (px - X0 + .5) / (2 cw), v = (py - Y0 + .5) / ch)
b = open(os.path.join(ROOT, 'assets', 'models', f'{name}.glb'), 'rb').read(); n = struct.unpack('<I', b[12:16])[0]; js = json.loads(b[20:20 + n]); bin_ = b[20 + n + 8:]
def acc(i, c):
    a = js['accessors'][i]; bv = js['bufferViews'][a['bufferView']]
    return np.frombuffer(bin_, dtype='<f4', count=a['count'] * c, offset=bv.get('byteOffset', 0) + a.get('byteOffset', 0)).reshape(-1, c)
V, UV = acc(0, 3).astype(float), acc(2, 2).astype(float); nv = len(V) // 2; Vf, Uf = V[:nv], UV[:nv]
ys_m, xs_m = np.where(inside); X0, Y0 = max(xs_m.min() - 8, 0), max(ys_m.min() - 8, 0); cw, ch = min(xs_m.max() + 9, W) - X0, min(ys_m.max() + 9, H) - Y0
pxv = Uf[:, 0] * 2 * cw - 0.5 + X0; pyv = Uf[:, 1] * ch - 0.5 + Y0; tree = cKDTree(np.c_[pxv, pyv])
pose = json.load(open(os.path.join(HERE, 'fit', f'pose-{name}.json')))['camera']; T = np.array(pose['target']) / SIZE; d = pose['dist'] / SIZE
cam = T + d * np.array([math.sin(pose['yaw']) * math.cos(pose['pitch']), math.sin(pose['pitch']), math.cos(pose['yaw']) * math.cos(pose['pitch'])])
F = (H / 2) / math.tan(math.radians(pose['fov']) / 2)

r = json.load(open(os.path.join(ROOT, 'recipes', f'{name}.json'), encoding='utf-8')); parts = [p for p in r.get('parts', []) if not p.get('material', '').startswith('floret')]
chk = im.copy(); dr = ImageDraw.Draw(chk); total = 0
for key, mk, ring in (('floret_cream', cream, (0, 160, 255)), ('floret_pink', pink, (0, 255, 0))):
    xs, ys, rp = spots(mk); _, ix = tree.query(np.c_[xs, ys]); P = Vf[ix]
    dist = np.linalg.norm(P - cam, axis=1); rad = rp * dist / F                      # px -> units at that depth
    P = P + (cam - P) / dist[:, None] * rad[:, None]                                   # sits on the surface, not inside it
    col = np.median(A[mk], 0); r['materials'][key] = {'kind': 'wax', 'color': '#%02x%02x%02x' % tuple(int(c) for c in col), 'roughness': 0.7, 'bump': 0, 'sheen': 0.3, 'clearcoat': 0, 'glow': 0.05}
    rb = float(np.median(rad)); parts.append({'shape': 'dots', 'material': key, 'r': round(rb, 4), 'inst': [[round(float(p[0]), 4), round(float(p[1]), 4), round(float(p[2]), 4), 0, round(float(s / rb), 3)] for p, s in zip(P, rad)]})
    for x, y, q in zip(xs, ys, rp): dr.ellipse([x - q, y - q, x + q, y + q], outline=ring)
    total += len(xs); print(f'{key}: {len(xs)} florets, colour {r["materials"][key]["color"]}, median radius {rb:.4f}')
r['parts'] = parts; json.dump(r, open(os.path.join(ROOT, 'recipes', f'{name}.json'), 'w', encoding='utf-8'), ensure_ascii=False)
chk.save(os.path.join(HERE, 'fit', f'florets-{name}.png')); print(total, 'florets')
