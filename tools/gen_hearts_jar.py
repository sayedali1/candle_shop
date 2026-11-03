"""The heart-pile jar (brief/ref-hearts-side.jpg, -top.jpg, -34.jpg), built from numbers read off the photos.
Side photo (camera nearly level, so heights and widths read straight; tools/fit/hs-*.png at 2-3x): the jar 453 px wide (x 318-771) and 813 px tall
(rim 427, foot 1240), so the jar is 1 unit tall and 0.557 wide. The glass base is solid up to row 1140 (0.123). The wax top is a tilted plane, high
on the left (row 532 at the left wall: 0.871) and low on the right (row 820: 0.517). The hearts fill the wedge above it up to row 480 on the left
and middle (0.935) and 507 on the right (0.902). A face-on heart is 100 px wide and tall (0.123); a heart lying on its side is about 0.55 of that
thick (3/4 photo). Top and 3/4 photos: the jar is square in plan (as deep as wide), its corners rounded by 0.105 of the width; the glass wall is
about 10 px (0.012). The wick is a white cotton loop standing just above the pile, left of the middle (x 495, top row 445).
Hidden, and how it is filled: the hearts inside the pile and at the back are not seen one by one: the wedge is packed with hearts of the measured
size (fixed seed), as tightly as the photo's front shows. The back of the jar is the same as its front (square, the same all round).
Colours: the wax is sunlit and reads orange in most of every photo; its own colour is read where the sun does not reach (the top photo's right side). The hearts' red from the side photo.
Run:  python tools/gen_hearts_jar.py      Writes recipes/15-heart-pile.json"""
import json, math, os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
H_PX, W_PX, Y_FOOT = 813.0, 453.0, 1240.0
u = lambda px: px / H_PX                                                   # side photo px -> units (1 = the jar's height)
W = u(W_PX); D = W; R = 0.105 * W; WALL = u(10); BASE = u(Y_FOOT - 1140)
SL = (u(Y_FOOT - 532), u(Y_FOOT - 820))                                    # wax top: at the left wall, at the right wall
TOP = (u(Y_FOOT - 480), u(Y_FOOT - 507))                                   # the pile's top: left, right
HW, HT = u(100), u(100) * 0.55                                             # a heart: width, thickness

A3 = np.array(Image.open(os.path.join(ROOT, 'brief', 'ref-hearts-34.jpg')).convert('RGB')).astype(float)
AS = np.array(Image.open(os.path.join(ROOT, 'brief', 'ref-hearts-side.jpg')).convert('RGB')).astype(float)
hexc = lambda c: '#%02x%02x%02x' % tuple(int(min(255, x)) for x in c)
AT = np.array(Image.open(os.path.join(ROOT, 'brief', 'ref-hearts-top.jpg')).convert('RGB')).astype(float)
wax_c = np.mean([AT[y - 5:y + 6, x - 5:x + 6].reshape(-1, 3).mean(0) for x, y in ((700, 1000), (720, 1060))], 0)   # where the sun does not reach (top photo, right): the sunlit wax reads orange
r_, g_, b_ = AS[..., 0], AS[..., 1], AS[..., 2]; red = (r_ > 120) & (r_ - g_ > 70) & (r_ - b_ > 50); red[:470] = False; red[880:] = False
heart_c = np.percentile(AS[red], 60, axis=0)

# the pile: hearts packed into the wedge between the wax top and the pile's top, inside the glass
inner = W / 2 - WALL - 0.004
ys = lambda x: SL[0] + (SL[1] - SL[0]) * (x / W + 0.5)
yt = lambda x: TOP[0] + (TOP[1] - TOP[0]) * (x / W + 0.5)
rng = np.random.default_rng(15); pts = []; MIN = HW * 0.6
for _ in range(40000):
    x, z = rng.uniform(-inner + HW * 0.52, inner - HW * 0.52, 2)   # a turned heart reaches half its width: none pokes through the glass
    lo, hi = ys(x) + HT * 0.45, yt(x) - HW * 0.42                     # a turned heart reaches up to half its width: keep the pile's top where the photo has it
    if hi <= lo: continue
    y = rng.uniform(lo, hi); p = np.array([x, y, z])
    if all(np.linalg.norm(p - q) > MIN for q in pts): pts.append(p)
inst = [[round(float(p[0]), 4), round(float(p[1]), 4), round(float(p[2]), 4)] + [round(float(a), 3) for a in rng.uniform(-math.pi, math.pi, 3)] + [round(float(rng.uniform(0.94, 1.04)), 3)] for p in pts]

wx = u(495 - (318 + 771) / 2); wtop = u(Y_FOOT - 445); wr = 0.028       # the wick loop
loop = [[wx + 0.01, TOP[0] - 0.03, 0.02, 0.004], [wx + 0.012, TOP[0] + 0.005, 0.012, 0.0045]] + \
       [[wx + wr * math.sin(a), wtop - wr + wr * math.cos(a), 0.012 - 0.01 * math.sin(a), 0.0045] for a in np.linspace(0.3, 2 * math.pi - 0.6, 9)] + [[wx - 0.005, TOP[0] - 0.01, -0.01, 0.004]]
# glass: faintly green, as clear glass is where it is thick; the solid base denser with bright edges (side photo, rows 1140-1240); the rim rounded so it catches light
recipe = {
    'name': 'red wax hearts piled on a tilted cream wax top in a square glass jar: built from the photos\' measured numbers',
    'turn': 0, 'turnLimit': 0.3, 'size': 0.78, 'shadow': 1.6, 'shelfSize': 1.0,
    'materials': {'glass': {'kind': 'glass', 'color': '#f3fbf7', 'opacity': 0.08, 'roughness': 0.12, 'clearcoat': 1, 'clearcoatRoughness': 0.02, 'edge': {'opacity': 0.6, 'light': 0.4, 'power': 2.5, 'reflect': 0.55}, 'env': 1.8},
                  'glassBase': {'kind': 'glass', 'color': '#e8f6ef', 'opacity': 0.2, 'edge': {'opacity': 0.75, 'light': 0.5, 'power': 2.0, 'reflect': 1.0}, 'env': 2.2},
                   'wax': {'kind': 'wax', 'color': hexc(wax_c), 'sheenColor': '#fff6e8'},
                  'heart': {'kind': 'glaze', 'color': hexc(heart_c), 'roughness': 0.5, 'clearcoat': 0.2, 'env': 0.3, 'glow': 0.04},
                  'string': {'kind': 'wax', 'color': '#f6f3ee', 'roughness': 0.8, 'bump': 0}},
    'parts': [{'shape': 'roundbox', 'material': 'glass', 'w': round(W, 4), 'd': round(D, 4), 'h': 1.0, 'r': round(R, 4), 'hole': round(WALL, 4), 'bevel': round(WALL * 0.45, 4)},   # the rim: rounded, it catches the light
              {'shape': 'roundbox', 'material': 'glassBase', 'w': round(W - 0.002, 4), 'd': round(D - 0.002, 4), 'h': round(BASE, 4), 'r': round(R, 4), 'bevel': 0.02},
              {'shape': 'roundbox', 'material': 'wax', 'w': round(W - 2 * WALL - 0.002, 4), 'd': round(D - 2 * WALL - 0.002, 4), 'h': round(SL[0] - BASE, 4), 'r': round(R - WALL, 4),
               'slant': [round(SL[0] - BASE, 4), round(SL[1] - BASE, 4)], 'pos': [0, round(BASE, 4), 0]},
              {'shape': 'hearts', 'material': 'heart', 'w': round(HW, 4), 't': round(HT, 4), 'inst': inst},
              {'shape': 'path', 'material': 'string', 'strands': 6, 'depth': 0.1, 'around': 12, 'segments': 80, 'points': [[round(v, 4) for v in q] for q in loop]}],
    'wicks': [{'kind': 'cotton', 'x': round(wx, 4), 'z': 0.012, 'base': round(wtop - 0.004, 4), 'tip': round(wtop + 0.004, 4), 'radius': 0.003, 'color': '#f6f3ee'}],
    'flame': {'size': 0.8, 'width': 1.0}}
json.dump(recipe, open(os.path.join(ROOT, 'recipes', '15-heart-pile.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(f'jar {W:.3f} x {D:.3f} x 1, wax top {SL[0]:.3f} -> {SL[1]:.3f}, {len(inst)} hearts of {HW:.3f} x {HT:.3f}, wax {hexc(wax_c)}, hearts {hexc(heart_c)}')
