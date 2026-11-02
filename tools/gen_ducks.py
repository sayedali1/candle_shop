"""Writes the recipe of the duck pond candle: one big rubber duck and eight ducklings on a marbled pond in an oval tray.
Smooth figures need no photo skin: this is true 3D that can turn all the way round. Positions are read off the photo (brief/ref-ducks.jpg, pixels of each figure's foot).
Run:  python tools/gen_ducks.py     then bake both bodies:
      node tools/bake-blob.mjs recipes/11-duck-pond.json assets/models/duck-big.bin 72
      node tools/bake-blob.mjs recipes/11-duck-pond.json assets/models/duck-small.bin 30"""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
F = lambda *a: [round(float(v), 4) for v in a]
FIT = json.load(open(os.path.join(HERE, 'fit', 'ducks-fit.json')))      # measured from the photo by tools/fit_ducks.py: camera, tray size, every duck's place and direction
A, R, H = FIT['A'], FIT['R'], 0.09     # the tray: half the straight part, end radius, height
POND = H - 0.016                       # the pond sits a little below the rim
TH = -FIT['yaw']                       # the model's frame: the photo's camera straight in front, so the shelf's front view is the photo's view
ct, st = math.cos(TH), math.sin(TH)
def rot(x, z): return x * ct + z * st, -x * st + z * ct


def duck_els():
    """a rubber duck, 1 unit tall, looking along +z"""
    e = lambda c, r: {'c': F(*c), 'r': F(*r), 'rot': [0, 0, 0]}
    els = [e((0, .28, -.05), (.50, .28, .52)),      # body
           e((0, .32, .16), (.40, .30, .35)),       # chest
           e((0, .33, -.47), (.15, .12, .12)),      # tail root
           e((0, .41, -.54), (.06, .07, .06)),      # tail tip, curling up
           e((0, .72, .17), (.31, .28, .30)),       # head
           e((0, .54, .12), (.28, .15, .27)),       # neck
           e((0, .625, .47), (.21, .065, .17))]     # the beak's lump: its colour comes from the photo
    for s in (1, -1):
        els.append(e((s * .46, .36, -.08), (.10, .17, .27)))   # wings
        els.append(e((s * .17, .65, .30), (.14, .11, .13)))    # cheeks
    return els


def big_els():
    """the big duck has its own proportions in the photo: a wide, low body and a tall, narrower head set back on it"""
    e = lambda c, r: {'c': F(*c), 'r': F(*r), 'rot': [0, 0, 0]}
    els = [e((0, .27, -.03), (.50, .27, .50)),      # body
           e((0, .36, .10), (.40, .28, .36)),       # chest
           e((0, .33, -.44), (.14, .11, .11)),      # tail
           e((0, .84, .05), (.26, .25, .25)),       # head
           e((0, .62, .03), (.29, .21, .28)),       # neck
           e((0, .71, .29), (.20, .07, .17))]       # the beak's lump
    for s in (1, -1):
        els.append(e((s * .43, .44, -.05), (.13, .28, .30)))   # high, soft shoulders, as in the photo
    return els


def scene(S, yaw, x, y, z, l):
    c, s = math.cos(yaw), math.sin(yaw)
    return [x + S * (l[0] * c + l[2] * s), y + S * l[1], z + S * (-l[0] * s + l[2] * c)]


# the fitted directions carry noise from the few pixels they come from: the ducklings are pulled halfway toward their common direction
small = FIT['ducks'][1:]; mean_yaw = sum(k['yaw'] for k in small) / len(small)
big = FIT['ducks'][0]; BIG, BIG_YAW = big['S'] * 1.1, big['yaw'] + TH
bx, bz = rot(big['x'], big['z'])
hx, hz = BIG * .17 * math.sin(BIG_YAW), BIG * .17 * math.cos(BIG_YAW)
SHIFT = -(bz + hz)                     # the page's flame burns at z = 0: the big duck's head stands there
ducks = [(BIG, BIG_YAW, bx, POND, bz + SHIFT)]
for k in small:
    x, z = rot(k['x'], k['z'])
    ducks.append((k['S'], (k['yaw'] + mean_yaw) / 2 + TH, x, POND, z + SHIFT))
beak = lambda d: [*scene(d[0], d[1], d[2], d[3], d[4], (0, .625, .49)), d[1], d[0]]
eyes = []
for d in ducks:
    for sx in (1, -1): eyes.append([*scene(d[0], d[1], d[2], d[3], d[4], (sx * .225, .80, .35)), d[1], d[0]])
shadows = [[k['x'], k['z'], k['S'] * .72] for k in FIT['ducks']]         # in the tray's own frame: the pond's picture turns with the tray
wax = lambda col, **k: {'kind': 'wax', 'color': col, 'roughness': .46, 'bump': 0, 'sheen': .5, 'sheenColor': '#fff2c0', 'sheenRoughness': .5, 'clearcoat': .25, 'clearcoatRoughness': .4, 'glow': .22, 'glowColor': '#ffb040', **k}
body = {'shape': 'blob', 'k': .09, 'clipY': 0.0, 'els': duck_els(), 'box': {'c': [0, .52, -.06], 'h': .8}, 'glowThin': 1.0}
recipe = {
    'name': 'a rubber duck and eight ducklings on a marbled pond', 'turn': 0, 'size': 0.74, 'shadow': 2.1,
    'flameLight': 0.32, 'shelfSize': 1.2, 'shelfTilt': 0.14,
    'materials': {
        'yellow': wax('#f4c733'),
        'beak': wax('#ee8a1c', roughness=.38, glow=.12),
        'ink': {'kind': 'solid', 'color': '#0d0806', 'roughness': .35, 'clearcoat': .25, 'clearcoatRoughness': .25, 'env': .12},
        'tray': {'kind': 'matte', 'color': '#e9e1d2', 'roughness': .9},
        'white': wax('#fbf6ea', glow=.1),
        'pond': {'kind': 'glaze', 'color': '#ffffff', 'roughness': .5, 'clearcoat': .2, 'clearcoatRoughness': .4, 'env': .12, 'glow': .04, 'glowColor': '#7fc0ff',
                 'texture': {'kind': 'marble', 'base': '#1a5fb4', 'veins': ['#a9d4f0', '#134f96', '#5fa6de'], 'count': 110, 'a': round(A, 4), 'r': R - .03, 'shadows': [[round(a, 3), round(b, 3), round(c, 3)] for a, b, c in shadows]}}},
    'parts': [
        {'shape': 'stadium', 'material': 'tray', 'a': A, 'r': R, 'h': H, 'bevel': .014, 'hole': .042, 'pos': [0, 0, round(SHIFT, 4)], 'rot': [0, round(TH, 4), 0]},
        {'shape': 'stadium', 'material': 'pond', 'a': A, 'r': R - .03, 'h': POND, 'bevel': 0, 'pos': [0, 0, round(SHIFT, 4)], 'rot': [0, round(TH, 4), 0]},
        {**body, 'els': big_els(), 'box': {'c': [0, .62, -.02], 'h': .78}, 'material': 'yellow', 'res': 72, 'bake': 'assets/models/duck-big.bin', 'inst': [[*F(ducks[0][2], POND, ducks[0][4], BIG_YAW), BIG]]},
        {**body, 'material': 'yellow', 'res': 30, 'bake': 'assets/models/duck-small.bin', 'inst': [[*F(d[2], d[3], d[4], d[1]), d[0]] for d in ducks[1:]]},
        {'shape': 'dots', 'material': 'beak', 'r': 1, 'scale': [.25, .085, .21], 'inst': [[*F(*beak(d)[:4]), d[0]] for d in ducks]},
        {'shape': 'dots', 'material': 'ink', 'r': 1, 'scale': [.056, .06, .04], 'inst': [[*F(*q[:4]), q[4]] for q in eyes]},
        {'shape': 'torus', 'material': 'white', 'r': .02, 'tube': .005, 'pos': F(bx + hx + .022, POND + BIG * 1.03, 0), 'rot': [math.pi / 2, 0, 0]}],
    'wicks': [{'kind': 'long', 'x': round(bx + hx, 3), 'z': 0, 'base': round(POND + BIG * .98, 3), 'tip': round(POND + BIG * 1.1, 3), 'color': '#f5f0e2', 'radius': .006}],
    'flame': {'size': .48, 'width': 1.0}}
out = os.path.join(ROOT, 'recipes', '11-duck-pond.json')
open(out, 'w', encoding='utf-8').write(json.dumps(recipe, ensure_ascii=False))
tx, tz = rot(0.0, 0.0)
Tg = F(0.74 * 0, 0.74 * (H), 0.74 * SHIFT)
json.dump({'camera': {'yaw': 0.0, 'pitch': FIT['pitch'], 'fov': FIT['fov'], 'target': Tg, 'dist': round(FIT['dist'] * 0.74, 3)}, 'blocks': []}, open(os.path.join(HERE, 'fit', 'pose-ducks.json'), 'w'), indent=1)   # the same camera in the model's frame, for the Lab's photo view
print('ducks', len(ducks), 'eyes', len(eyes), '->', out)
