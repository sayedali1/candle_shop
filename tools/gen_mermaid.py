"""The mermaid-tail candle: a glass tumbler, a clear thick base, blue gel, cream wax, and on top a mermaid's tail, two shells, pearls and a looped wick.
What comes from the photo (brief/ref-mermaid.jpg): the glass's size and taper, every layer's height, the camera (from the rim's oval), the gel's side (the photo's own pixels,
unwrapped around the glass), the tail (tools/gen_relief.py, its own surface), where each pearl and shell sits, and every colour. Guessed: the shells' 3D form (ribbed domes), the hidden back.
Run:  python tools/gen_mermaid.py          (then the tail:  see tools/fit/mermaid-build-settings.txt)
Writes recipes/12-mermaid.json, assets/models/12-mermaid-gel.jpg, tools/fit/pose-mermaid-photo.json and tools/fit/mermaid-check.png (the 3D outlines drawn on the photo)"""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
photo = Image.open(os.path.join(ROOT, 'brief', 'ref-mermaid.jpg')).convert('RGB'); W, H = photo.size; A = np.array(photo).astype(float)
SIZE = 0.78
# read off the photo (tools/fit/mermaid-grid*.png). Model units: the glass is 1 tall
PX = 685.0                                             # the glass's front height in pixels: rim front y 550, foot front y 1235
RT, RB = 0.44, 0.367                                   # radius at the rim and at the foot (601 and 502 px wide)
FLOOR, GEL, WAX = 0.2, 0.635, 0.87                     # the inside floor of the thick base, the top of the gel, the top of the wax
CAM = {'pitch': 0.14, 'fov': 20, 'dist': 5.92, 'target': 0.72, 'u0': 23.0, 'v0': 0.0, 'roll': 0.0}


def camera():
    p, T = CAM['pitch'], np.array([0, CAM['target'], 0.0])
    P = T + CAM['dist'] * np.array([0, math.sin(p), math.cos(p)])
    f = (T - P) / np.linalg.norm(T - P); right = np.cross(f, [0, 1, 0]); right /= np.linalg.norm(right); up = np.cross(right, f)
    return P, f, right, up, (H / 2) / math.tan(math.radians(CAM['fov']) / 2)


def project(p):
    P, f, right, up, F = camera(); q = np.atleast_2d(p) - P; z = q @ f
    return np.stack([W / 2 + CAM['u0'] + q @ right / z * F, H / 2 + CAM['v0'] - q @ up / z * F], 1)


def on_plane(px, py, y):
    P, f, right, up, F = camera()
    d = f + (px - W / 2 - CAM['u0']) / F * right - (py - H / 2 - CAM['v0']) / F * up
    return P + d * ((y - P[1]) / d[1])


rad = lambda h: RB + (RT - RB) * h
def sample(x, y, r=4, sat=1.0):
    c = A[y - r:y + r, x - r:x + r].reshape(-1, 3).mean(0); c = np.clip(c.mean() + sat * (c - c.mean()), 0, 255)     # sat > 1: the photo's soft light greys small things a little
    return '#%02x%02x%02x' % tuple(int(v) for v in c)

# the check: the glass's outline and layers, drawn with this camera over the photo
im = photo.copy(); dr = ImageDraw.Draw(im)
for h, colr in ((0, (255, 0, 0)), (FLOOR, (255, 160, 0)), (GEL, (0, 255, 0)), (WAX, (255, 0, 255)), (1, (255, 0, 0))):
    t = np.linspace(0, 2 * math.pi, 120); q = project(np.stack([rad(h) * np.sin(t), np.full_like(t, h), rad(h) * np.cos(t)], 1))
    dr.line([tuple(v) for v in q] + [tuple(q[0])], fill=colr, width=3)

# the gel's side: the photo's pixels, unwrapped around the glass (the front half seen; the back repeats it mirrored)
from scipy import ndimage as ndi
TW, TH_ = 2048, 512                                    # finer than the photo's own gel (about 500 x 330 px), read smoothly between pixels: the bubbles and swirls stay sharp
jj, ii = np.mgrid[0:TH_, 0:TW]
h = GEL - (GEL - FLOOR) * (jj + 0.5) / TH_
th = 2 * math.pi * (ii + 0.5) / TW - math.pi
th = np.where(np.abs(th) > math.pi / 2, np.copysign(math.pi, th) - th, th)
far = np.abs(th) > 0.8                                 # the front matches the photo; toward the side it is squeezed onto 46-60 degrees: nearer the edge the photo sees the gel end-on, and repeating that column made streaks
th = np.where(far, np.copysign(0.8 + 0.25 * np.sin(np.clip(np.abs(th) - 0.8, 0, None) / (math.pi / 2 - 0.8) * math.pi / 2), th), th)
r = rad(h) * 0.97
xy = project(np.stack([(r * np.sin(th)).ravel(), h.ravel(), (r * np.cos(th)).ravel()], 1))
gel = np.stack([ndi.map_coordinates(A[..., c], [xy[:, 1], xy[:, 0]], order=1, mode='nearest') for c in range(3)], -1).reshape(TH_, TW, 3)
os.makedirs(os.path.join(ROOT, 'assets', 'models'), exist_ok=True)
Image.fromarray(gel.astype(np.uint8)).save(os.path.join(ROOT, 'assets', 'models', '12-mermaid-gel.jpg'), quality=90)

# pearls and shells: their pixel, sent through the camera onto the wax top
PEARL = 0.03
pearls = [(360, 617), (462, 617), (707, 622), (797, 617), (500, 552), (608, 548)]
pp = [[round(float(v), 4) for v in on_plane(x, y, WAX + PEARL)] for x, y in pearls]
for q in pp:                                           # the two at the back sit higher than the wax's back edge in the photo (on the tail and the shell): kept inside the glass
    k = min(1, (rad(WAX) - 0.06) / math.hypot(q[0], q[2])); q[0], q[2] = round(q[0] * k, 4), round(q[2] * k, 4)
pink, purple = on_plane(585, 640, WAX), on_plane(680, 622, WAX)
for q in pp + [pink.tolist(), purple.tolist()]:
    x, y = project(np.array(q))[0]; dr.ellipse([x - 6, y - 6, x + 6, y + 6], outline=(0, 0, 255), width=3)
im.crop((100, 250, 1000, 1300)).save(os.path.join(HERE, 'fit', 'mermaid-check.png'))

# the camera for gen_relief and the Lab, in page units (the candle is shown at SIZE)
json.dump({'camera': {'yaw': 0.0, 'pitch': CAM['pitch'], 'fov': CAM['fov'], 'target': [0, CAM['target'] * SIZE, 0], 'dist': CAM['dist'] * SIZE, 'u0': CAM['u0'], 'v0': CAM['v0'], 'roll': CAM['roll']}, 'blocks': []},
          open(os.path.join(HERE, 'fit', 'pose-mermaid-photo.json'), 'w'), indent=1)
json.dump({'camera': {'yaw': 0.0, 'pitch': CAM['pitch'], 'fov': CAM['fov'], 'target': [0, CAM['target'] * SIZE, 0], 'dist': CAM['dist'] * SIZE, 'u0': CAM['u0'], 'v0': CAM['v0'], 'roll': CAM['roll']}, 'blocks': []},
          open(os.path.join(HERE, 'fit', 'pose-12-mermaid.json'), 'w'), indent=1)

F = lambda *a: [round(float(v), 4) for v in a]
wax_side, wax_top = sample(560, 720, 8), sample(560, 660, 6)
tail = {}
tp = os.path.join(ROOT, 'recipes', 'zz-mermaid-tail.json')
if os.path.exists(tp): tail = json.load(open(tp, encoding='utf-8'))
recipe = {
    'name': 'a mermaid tail, shells and pearls on cream wax over blue gel, in a glass tumbler',
    'turn': 0, 'turnLimit': 0.35, 'size': SIZE, 'shadow': 1.7, 'shelfSize': 1.0,
    'model': 'assets/models/12-mermaid-tail.glb', 'modelRaw': True, 'modelGlow': tail.get('modelGlow', 0.14), 'modelGlowColor': tail.get('modelGlowColor', '#fff0f0'), 'modelEnv': 0.6, 'modelRough': 0.5,
    'flameLight': 0.6, 'flameLightPhone': 0.6,
    'materials': {
        'glass': {'kind': 'glass', 'opacity': 0.12},
        'gel': {'kind': 'glaze', 'roughness': 0.3, 'clearcoat': 0.25, 'env': 0.12, 'selfLight': 0.7, 'glow': 0.05, 'glowColor': '#5aa0ff', 'texture': {'kind': 'photo', 'src': 'assets/models/12-mermaid-gel.jpg'}},
        'gelTop': {'kind': 'glaze', 'color': sample(560, 820, 6), 'roughness': 0.3},
        'wax': {'kind': 'wax', 'color': wax_side, 'sheenColor': '#fff6e8'},
        'waxTop': {'kind': 'wax', 'color': wax_top, 'sheenColor': '#fff6e8'},
        'pearl': {'kind': 'glaze', 'color': sample(707, 617, 5), 'roughness': 0.18, 'clearcoat': 1, 'sheen': 0.6, 'sheenColor': '#ffd8f0', 'env': 0.9},
        'pink': {'kind': 'glaze', 'color': sample(585, 628, 6, 1.4), 'roughness': 0.45, 'clearcoat': 0.3, 'env': 0.4, 'glow': 0.1},
        'purple': {'kind': 'glaze', 'color': sample(640, 590, 6, 1.4), 'roughness': 0.45, 'clearcoat': 0.3, 'env': 0.4, 'glow': 0.1},
        'string': {'kind': 'wax', 'color': '#f6f3ee', 'roughness': 0.8, 'bump': 0}},
    'parts': [
        {'shape': 'lathe', 'material': 'glass', 'profile': [[0, 0], [RB - 0.02, 0], [RB, 0.015], [RB + 0.002, 0.04], [RT, 0.99], [RT - 0.004, 1.0], [RT - 0.016, 1.0], [RT - 0.02, 0.99], [rad(FLOOR) - 0.02, FLOOR + 0.02], [rad(FLOOR) - 0.06, FLOOR], [0, FLOOR - 0.01]]},
        {'shape': 'cylinder', 'material': 'gel', 'r': rad(GEL) - 0.012, 'rb': rad(FLOOR) - 0.012, 'h': GEL - FLOOR, 'open': True, 'segments': 96, 'thetaStart': -math.pi, 'thetaLength': 2 * math.pi, 'pos': [0, (GEL + FLOOR) / 2, 0]},
        {'shape': 'lathe', 'material': 'wax', 'profile': [[rad(GEL) - 0.012, GEL], [rad(WAX) - 0.021, WAX - 0.008], [rad(WAX) - 0.026, WAX], [0, WAX + 0.004]]},
        {'shape': 'dots', 'material': 'pearl', 'r': PEARL, 'at': pp},
        {'shape': 'lathe', 'material': 'pink', 'ribs': {'count': 18, 'depth': 0.05}, 'profile': [[0, 0], [0.13, 0], [0.125, 0.03], [0.085, 0.065], [0, 0.075]],
         'pos': F(pink[0], WAX - 0.01, pink[2]), 'rot': [-0.25, 0, 0], 'scale': [1.1, 1, 0.75]},
        {'shape': 'lathe', 'material': 'purple', 'ribs': {'count': 10, 'depth': 0.06}, 'profile': [[0, 0], [0.12, 0], [0.13, 0.04], [0.11, 0.09], [0.05, 0.11], [0, 0.105]],
         'pos': F(purple[0], WAX - 0.005, purple[2]), 'rot': [0.15, 0.4, 0], 'scale': [1, 1, 0.8]},
        {'shape': 'torus', 'material': 'string', 'r': 0.045, 'tube': 0.012, 'pos': [-0.03, 1.05, 0.0], 'rot': [math.pi / 2, 0, 0.3]}],
    'wicks': [{'kind': 'cotton', 'x': -0.03, 'z': 0, 'base': WAX, 'tip': 1.1, 'color': '#f6f3ee', 'radius': 0.008}],
    'flame': {'size': 0.75, 'width': 1.0}}
open(os.path.join(ROOT, 'recipes', '12-mermaid.json'), 'w', encoding='utf-8').write(json.dumps(recipe, ensure_ascii=False))
print('pearls', pp, '\npink', F(*pink), 'purple', F(*purple), '\ncolours', wax_side, wax_top)
