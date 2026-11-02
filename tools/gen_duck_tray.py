"""The duck pond's tray and water as real 3D parts, from the measured numbers (tools/measure_tray.py): an oval with straight sides, its wall, its rim and
the water inside, closed all round. The back wall and the underside follow from the oval (the same all round). The water's marbling is read off the
photo: each point of the water's flat top is sent through the photo's camera to the pixel it was seen at (under the ducks, where the photo cannot see
the water, the nearest seen water is used).
Two steps around tools/gen_relief.py (the ducks):
  python tools/gen_duck_tray.py pose        writes tools/fit/pose-tray-ducks.json (the photo's camera, for gen_relief POSE=)
  (gen_relief with OUTLINE=outline-duckfigs.json POSE=pose-tray-ducks.json SEAT_Y=<water> TRAYFRAME=1)
  python tools/gen_duck_tray.py parts       adds the tray and water to recipes/11-duck-pond.json, writes assets/models/11-duck-water.jpg"""
import json, math, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); SIZE = 0.78
T = json.load(open(os.path.join(HERE, 'fit', 'tray-ducks.json'))); v, fov = T['camera']['v'], T['camera']['fov']
src = open(os.path.join(HERE, 'fit_ducks.py'), encoding='utf-8').read(); g = {'__file__': os.path.join(HERE, 'fit_ducks.py')}
exec(src[:src.index('TR = np.array(TRAY')], g); project, RIM_T = g['project'], g['RIM_Y']   # the camera looks at (0, RIM_T, 0)

if sys.argv[1] == 'pose':
    json.dump({'camera': {'yaw': v[0], 'pitch': v[1], 'fov': fov, 'target': [0, RIM_T * SIZE, 0], 'dist': math.exp(v[2]) * SIZE, 'u0': v[3], 'v0': v[4], 'roll': v[5]}, 'blocks': []},
              open(os.path.join(HERE, 'fit', 'pose-tray-ducks.json'), 'w'), indent=1)
    print('pose written; water height', T['water_y']); sys.exit()

A, R, h, w, yw = T['A'], T['R'], T['rim_top_y'], T['rim_width'], T['water_y']
sh = json.load(open(os.path.join(HERE, 'fit', 'shift-11-duck-pond.json'))); yaw = sh['yaw']; dz = sh['shift'][2]
im = Image.open(os.path.join(ROOT, 'brief', 'ref-ducks.jpg')).convert('RGB'); P = np.array(im).astype(float); Hh, Ww = P.shape[:2]
R_, G_, B_ = P[..., 0], P[..., 1], P[..., 2]
duck = ndi.binary_dilation((R_ > 140) & (G_ > 110) & (R_ - B_ > 55), iterations=5)
water = ndi.binary_erosion((B_ > R_ + 10) & ~duck, iterations=1)
ix = ndi.distance_transform_edt(~water, return_distances=False, return_indices=True); Pw = P[ix[0], ix[1]]   # every pixel takes the nearest seen water

# the water's top, flattened: builder 'stadium' UVs are u = (x + L) / 2L, v = (z + r) / 2r; the image's first row is v = 1
rw = R - w; L = A + rw; TW = 1024; TH = int(TW * rw / L)
uu, vv = np.meshgrid((np.arange(TW) + 0.5) / TW, 1 - (np.arange(TH) + 0.5) / TH)
X, Z = -L + 2 * L * uu, -rw + 2 * rw * vv
q = project(np.column_stack([X.ravel(), np.full(X.size, yw), Z.ravel()]), v, fov)
qx, qy = np.clip(np.round(q[:, 0]).astype(int), 0, Ww - 1), np.clip(np.round(q[:, 1]).astype(int), 0, Hh - 1)
tex = Pw[qy, qx].reshape(TH, TW, 3)
Image.fromarray(tex.astype(np.uint8)).save(os.path.join(ROOT, 'assets', 'models', '11-duck-water.jpg'), quality=88)
rim_c = np.median(P[648:660, 440:620].reshape(-1, 3), 0); wall_c = np.median(P[675:700, 400:600].reshape(-1, 3), 0)   # the rim's top and the wall, sampled
hexc = lambda c: '#%02x%02x%02x' % tuple(int(x) for x in c)

rp = os.path.join(ROOT, 'recipes', '11-duck-pond.json'); r = json.load(open(rp, encoding='utf-8'))
r['materials'].update({'tray': {'kind': 'solid', 'color': hexc((rim_c + wall_c) / 2), 'roughness': 0.85, 'metalness': 0, 'clearcoat': 0},
                       'pond': {'kind': 'wax', 'texture': {'kind': 'photo', 'src': 'assets/models/11-duck-water.jpg'}, 'roughness': 0.35, 'bump': 0, 'sheen': 0.2, 'clearcoat': 0.3, 'glow': 0.05}})
place = {'pos': [0, 0, round(dz, 4)], 'rot': [0, round(-yaw, 4), 0]}                  # the tray's world turned into the model's frame (gen_relief: camera straight in front)
r['parts'] = [q_ for q_ in r.get('parts', []) if q_.get('material') not in ('tray', 'pond')] + [
    {'shape': 'stadium', 'material': 'tray', 'a': round(A, 4), 'r': round(R, 4), 'h': round(h, 4), 'hole': round(w, 4), 'bevel': 0.004, **place},
    {'shape': 'stadium', 'material': 'tray', 'a': round(A, 4), 'r': round(rw + 0.002, 4), 'h': round(yw - 0.012, 4), **place},
    {'shape': 'stadium', 'material': 'pond', 'a': round(A, 4), 'r': round(rw + 0.001, 4), 'h': round(yw, 4), **place}]
json.dump(r, open(rp, 'w', encoding='utf-8'), ensure_ascii=False)
print(f'tray: straight {2 * A:.3f}, width {2 * R:.3f}, rim {w:.3f} wide, top {h:.3f}, water {yw:.3f}; colours rim/wall {hexc(rim_c)} {hexc(wall_c)}')
