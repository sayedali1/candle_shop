"""The knot-tied pair (brief/ref-knot.jpg), built from numbers read off the photo, not from its pixels.
The photo gives dimensions only: a few heights and widths per candle, the knot's rows and tilt, the flute count, the wax colour.
Every number below was read on a 20 px grid laid over the photo (tools/fit/grid-tall.png, grid-short.png).
1. Body: a smooth lathe through the measured widths; 16 real flutes cut into it.
2. Knot: one rope along the path traced on the photo, round the candle twice, crossing itself on the front; fine cords run along it.
3. Wax: one plain colour (the photo's brightest wax), no photo on the candle.
Run:  python tools/gen_knot.py      Writes recipes/13-knot-pair.json, tools/fit/pose-13-knot-pair.json. Check: python tools/knot_edges.py"""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import PchipInterpolator

PI = math.pi
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
photo = Image.open(os.path.join(ROOT, 'brief', 'ref-knot.jpg')).convert('RGB'); W, H = photo.size
SIZE = 0.78
# the camera, fitted from the rims by tools/fit_knot_camera.py (every rim within 2 px): close, a little above the tall top, looking down.
# So the tall top rim is nearly edge-on (8 px deep) while both feet show wide curves (29 and 27 px deep)
CAM = {'pitch': 0.1226, 'fov': 32.27, 'dist': 3.6655, 'target': 0.6879, 'u0': 0.0, 'v0': 0.0}

# the numbers. Body: (photo row, left edge, right edge) at the rows where the outline turns.
# Body: every traced row (tools/trace_knot.py: both outlines traced row by row and checked by eye on zoomed strips, tools/fit/strip-*.png), one every 4 rows.
# Where one side is the rope ('rope_rows'), that row's body edge is the other side mirrored about the middle line; where both are rope it is hidden (pinched under the rope).
# The rope's side bulges ('side' points) take their row and reach from the traced lobe: the outermost point of the trace in that stretch.
# Knot: ONE rope per candle, along the path traced on the photo (tools/fit/band-tall.png, band-short.png at 4x; edges checked with tools/knot_edges.py).
# Each point: (kind, where, middle row, thickness px, reach px, middle px). kind 'x': seen on the front, where = its photo x; 'side': on the left or right outline
# (where = angle: 0 right, pi left, growing toward the front), 'hid': hidden behind or under the other strand (where = angle; its row is read from its neighbours).
# reach: how far the rope's outside stands from that winding's middle (px); its middle line sits reach - thickness/2 out.
# Hidden points are kept inside the traced outline: where the rope goes under itself its outside may not pass the bare waist the photo shows there.
# Tall: strand A comes round the left (row 588, outline 451: the 444 the edge reader found there is the window frame behind it), crosses the front going down (602, 610, 615) and reaches the right outline at 623 (624); behind, it goes back
# to the left and passes under A (hidden, ~605), dives down at the front-left (out from under A at x 480, its middle at x 500, row 648: ridges at 38 degrees there) and crosses the front lower (658, 668, 670) to the
# right outline at 664 (635; its lobe there spans 647-680), then goes behind (end tucked). Short: A round the left (714, outline 268), across the front rising (718, 714, 707), right outline 707 (415);
# behind, then B round the left inside (it never reaches the outline there: the trace stays at 284-292), across the front falling (744, 745, 748), right outline 746 (422), behind (end tucked).
# Under the tall knot the body comes out narrow and flares slowly (left edge 470 px at row 690 to 447 at 800, right 617 at 710 to 631 at 800: the brightness step at each edge).
# Under each knot the left edge shows the body itself, pinched in (the lower band is tucked under the upper one there): that row's right edge is the left one mirrored about the axis ('m': not used for the middle line). Row 588 is the other way round: its right edge (598) is the bare waist, its left the band.
# The rope is a round cord on a pinched waist: the tall knot reaches 90 px out and the rope is ~50 px thick, so its middle line sits ~65 px out; the bare waist under it measures 60-66.
# No single lean: each candle's middle wanders (tall: 551 px at the top, 546 at row 520, 540 at 560, 537 near the foot), so every row is moved to its own measured middle ('bend').
# The short's right edge above the knot (412, 408, 405, 402 at rows 600-660) was read at 3x next to the 3D outline: the window frame behind does not reach it.
# The last body row is the foot's front rim, standing on the shelf. Close-ups: tools/fit/knots-zoom.png, short-lower.png
TALL = {'body': 'tall', 'name': 'tall', 'rope_rows': {'L': (566, 628), 'R': (592, 702)}, 'top': 422, 'foot': (978, 449, 624),
        'knot': [('hid', 3*PI/2, 598, 46, 85, 534), ('side', PI, ('L', 566, 628, 589), 44, None, 534), ('x', 500, 602, 50, 90, 534), ('x', 540, 610, 54, 90, 534), ('x', 580, 615, 52, 90, 534),
                          ('side', 0, ('R', 592, 640), 48, -6, 534), ('hid', -PI/2, 615, 48, 84, 536), ('hid', -PI, 605, 40, 60, 538), ('hid', -PI - 0.35, 630, 44, 62, 541), ('x', 500, 648, 48, 94, 541), ('x', 520, 658, 52, 94, 541),
                          ('x', 560, 668, 52, 94, 541), ('x', 600, 670, 50, 94, 541), ('side', -2*PI, ('R', 641, 702), 50, None, 541), ('hid', -5*PI/2, 640, 46, 85, 541)],
        'wick': ((548, 422), (555, 386))}
SHORT = {'body': 'short', 'name': 'short', 'rope_rows': {'L': (686, 762), 'R': (682, 768)}, 'top': 553, 'foot': (1045, 268, 437),
         'knot': [('hid', 3*PI/2, 716, 44, 74, 341), ('side', PI, ('L', 686, 735), 50, None, 341), ('x', 300, 718, 46, 74, 341), ('x', 340, 714, 45, 74, 341), ('x', 380, 707, 42, 74, 341),
                           ('side', 0, ('R', 682, 725), 36, None, 341), ('hid', -PI/2, 725, 40, 74, 341), ('hid', -PI, 745, 30, 50, 341), ('x', 315, 744, 36, 76, 345), ('x', 340, 745, 34, 78, 345),
                           ('x', 380, 748, 36, 78, 345), ('side', -2*PI, ('R', 726, 768), 36, None, 341), ('hid', -5*PI/2, 735, 34, 72, 341)],
         'wick': ((340, 547), (341, 524))}
FLUTES, FLUTE_D = 16, 0.14         # 16: the bright crests, 21-23 degrees apart (tools/fit/flute-recount.png). Depth: the foot's front edge waves 4 px up and down,
                                   # seen from ~19 degrees above (foot ellipse 29 px on 88), so the grooves are ~12 px deep on 88 (0.14). The side outline hides it: crests cover the grooves
WAX = '#e2c0a1'                    # the brightest wax in the photo (the lit front of the short candle), the room's warm cast included
# where the rope presses on itself the photo shows only a thin dark line (3-4 px), not the V a round cord leaves: its cross-section is a little boxy
SQUARE = 0.75
ROPE = {'strands': 14, 'depth': 0.12, 'around': 40}   # the rope's fine ridges run along it, about 7 across the face we see (14 round the whole tube)


def camera():
    p, T = CAM['pitch'], np.array([0, CAM['target'], 0.0])
    P = T + CAM['dist'] * np.array([0, math.sin(p), math.cos(p)])
    f = (T - P) / np.linalg.norm(T - P); right = np.cross(f, [0, 1, 0]); right /= np.linalg.norm(right); up = np.cross(right, f)
    return P, f, right, up, (H / 2) / math.tan(math.radians(CAM['fov']) / 2)


P, f, right, up, F = camera()


def ray(px, py):
    d = f + (px - W / 2 - CAM['u0']) / F * right - (py - H / 2 - CAM['v0']) / F * up
    return d / np.linalg.norm(d)


def project(p):
    q = np.atleast_2d(p) - P; z = q @ f
    return np.stack([W / 2 + CAM['u0'] + q @ right / z * F, H / 2 + CAM['v0'] - q @ up / z * F], 1)


def axis(c):
    """where a candle stands: the middle of its foot's side corners, on the shelf. k turns photo px into units at that distance"""
    y, xl, xr = c['foot']; d = ray((xl + xr) / 2, y); at = P + d * (-P[1] / d[1])   # the foot's side corners lie level with its middle: that row meets the shelf at the axis
    return at, np.linalg.norm(at - P) / F


def scale(ax, h):
    """photo px -> units at a height on the axis: its depth along the camera's view over the focal length (the camera is close, so this changes with height)"""
    return float((ax + np.array([0, h, 0]) - P) @ f) / F


def height(ax, py):
    d = ray(ax[0], py); return float((P + d * ((ax[2] - P[2]) / d[2]))[1])


def middle(ax, row, px):
    """how far a row's measured middle sits sideways from the axis, in units (read at the axis depth)"""
    d = ray(px, row); return float((P + d * ((ax[2] - P[2]) / d[2]))[0] - ax[0])


TRACE = json.load(open(os.path.join(HERE, 'fit', 'trace-knot.json')))


def body_rows(c):
    from scipy.ndimage import gaussian_filter1d
    def smooth(side):                                              # the tracer jitters ~1 px row to row; on wax that shows as rings, so each stretch outside the rope is smoothed (4 rows)
        T = np.array(TRACE[c['name'] + '_' + side]); y, x = T[:, 0].astype(int), T[:, 1].copy(); r0, r1 = c['rope_rows'][side]
        for m in (y < r0, y > r1): x[m] = gaussian_filter1d(x[m], 4, mode='nearest')
        return dict(zip(y.tolist(), x.tolist()))
    L, R = smooth('L'), smooth('R'); rr = c['rope_rows']
    rope = lambda side, y: rr[side][0] <= y <= rr[side][1]
    both = [y for y in L if y in R and not rope('L', y) and not rope('R', y)]
    mid = np.poly1d(np.polyfit(both, [(L[y] + R[y]) / 2 for y in both], 3))
    out = [(c['top'], L[min(L)], R[min(R)])]
    for y in range(min(L) + 2, c['foot'][0] - 12, 4):            # the last ~12 rows of the trace follow the foot's curved bottom edge inward: the side runs straight down instead
        if y not in L or y not in R: continue
        a, b = rope('L', y), rope('R', y)
        if not a and not b: out.append((y, L[y], R[y]))
        elif a != b: m = float(mid(y)); e = R[y] if a else L[y]; out.append((y, min(e, 2 * m - e), max(e, 2 * m - e), 'm'))
    last = out[-1]; return out + [(c['foot'][0], last[1], last[2])]


def lobe(c, side, y0, y1, row=None):
    T = dict(map(tuple, TRACE[c['name'] + '_' + side])); ys = [y for y in T if y0 <= y <= y1]
    ext = (min if side == 'L' else max)(T[y_] for y_ in ys)          # the outermost x; the bulge's middle row: the middle of the rows within 4 px of it
    near = [y_ for y_ in ys if abs(T[y_] - ext) <= 4]
    return (row or round(sum(near) / len(near))), ext             # a row given by hand wins (the tall's left bulge is flat-topped: it starts at 567, so its middle is 589)


def build(c):
    ax, k = axis(c)
    rows = c['body'] = body_rows(c) if isinstance(c['body'], str) else c['body']; hs = np.array([height(ax, r[0]) for r in rows[:-1]] + [0.0])
    half = np.array([(r[2] - r[1]) / 2 * scale(ax, h) for r, h in zip(rows, hs)])
    rad0 = PchipInterpolator(*zip(*sorted(zip(hs, half))))
    bend = sorted((float(h), middle(ax, r[0], (r[1] + r[2]) / 2)) for r, h in zip(rows, hs) if len(r) == 3)
    shift = lambda h: float(np.interp(h, [b_[0] for b_ in bend], [b_[1] for b_ in bend]))
    path = []
    for kind, where, row, th, reach, mid in c['knot']:
        if kind == 'side':                                         # its row and reach: the traced lobe
            row, edge = lobe(c, *row); reach = abs(edge - mid) + (reach or 0)   # a number in the reach slot: px to take off, where the drawn outline overshoots the trace (tools/knot_edges.py)
        h = height(ax, row)
        for _ in range(4):                                         # the row is where the point shows: solve its height at its own depth
            k_ = scale(ax, h); rc = (reach - th / 2) * k_
            ang = where if kind != 'x' else math.acos(max(-1, min(1, (where - mid) / (reach - th / 2))))
            if kind == 'x' and path and path[-1][4] < -PI + 1e-6: ang -= 2 * PI   # the second time round
            dx = middle(ax, row, mid); pt = ax + np.array([dx + rc * math.cos(ang), h, rc * math.sin(ang)])
            h += (project(pt)[0][1] - row) * k_
        path.append([float(dx + rc * math.cos(ang)), h, float(rc * math.sin(ang)), th / 2 * k_, ang, rc])
    # hidden: under the rope the body pinches in to its middle line
    extra = [(q_[1], min(float(rad0(q_[1])), q_[5])) for q_ in path]
    pts = sorted(list(zip(hs, half)) + extra); hs2 = np.array([p_[0] for p_ in pts]); hv = np.array([p_[1] for p_ in pts])
    keep = np.concatenate([[True], np.diff(hs2) > 1e-4]); rad = PchipInterpolator(hs2[keep], hv[keep])
    prof = [[round(float(rad(h)), 4), round(float(h), 4)] for h in np.linspace(hs.min(), hs.max(), 120)]
    top = prof[-1]; prof += [[round(top[0] * 0.5, 4), round(top[1] - 0.004, 4)], [0, round(top[1] - 0.006, 4)]]   # a flat top, very slightly sunk at the wick
    return ax, scale(ax, prof[-3][1]), prof, path, [[round(h, 4), round(dx, 4)] for h, dx in bend], shift


tall, short = build(TALL), build(SHORT)
G = min(tall[2][0][1], short[2][0][1])                              # the lower foot stands on the page's shelf: everything moves down by its height


def parts(b, name):
    ax, k, prof, ropes, bend, shift = b
    out = [{'shape': 'lathe', 'material': name, 'segments': 144, 'ribs': {'count': FLUTES, 'depth': FLUTE_D, 'shape': 'flute'}, 'bend': bend,
            'pos': [round(float(ax[0]), 4), round(-G, 4), round(float(ax[2]), 4)], 'profile': prof}]
    out.append({'shape': 'path', 'material': name, **ROPE, 'square': SQUARE, 'segments': 360, 'pos': [round(float(ax[0]), 4), round(-G, 4), round(float(ax[2]), 4)],
                'points': [[round(x, 4), round(y, 4), round(z, 4), round(r, 4)] for x, y, z, r, _, _ in ropes]})
    return out


def wick(b, px):
    ax, k, prof, _, _, shift = b; (bx, by), (tx, ty) = px; top = prof[-3][1]
    return {'kind': 'cotton', 'x': round(float(ax[0] + shift(top)), 4), 'z': round(float(ax[2]), 4), 'base': round(top - G - 0.02, 4), 'tip': round(top - G + (by - ty) * k, 4),
            'tilt': round(math.atan2(tx - bx, by - ty), 3), 'radius': round(3 * k, 4), 'color': '#bfa288'}   # cotton, 6 px wide (tools/fit/wicks.png, 8x); colour from the lit short wick (the tall one is backlit)


wax = {'kind': 'wax', 'color': WAX, 'roughness': 0.6, 'bump': 0, 'sheen': 0.4, 'sheenColor': '#fff4e6', 'clearcoat': 0, 'glow': 0.3}
recipe = {
    'name': 'two ribbed pillar candles, each with a wax rope knot round its waist: built from the photo\'s measured numbers, plain wax',
    'turn': 0, 'turnLimit': 0.3, 'size': SIZE, 'shadow': 1.8, 'shelfSize': 1.05,
    'materials': {'tall': wax, 'short': wax},
    'parts': parts(tall, 'tall') + parts(short, 'short'),
    'wicks': [wick(tall, TALL['wick']), wick(short, SHORT['wick'])],
    'flame': {'size': 0.8, 'width': 1.0}}
open(os.path.join(ROOT, 'recipes', '13-knot-pair.json'), 'w', encoding='utf-8').write(json.dumps(recipe, ensure_ascii=False))
json.dump({'camera': {'yaw': 0.0, 'pitch': CAM['pitch'], 'fov': CAM['fov'], 'target': [0, (CAM['target'] - G) * SIZE, 0], 'dist': CAM['dist'] * SIZE, 'u0': CAM['u0'], 'v0': CAM['v0'], 'roll': 0.0}, 'blocks': []},
          open(os.path.join(HERE, 'fit', 'pose-13-knot-pair.json'), 'w'), indent=1)

# the check: python tools/knot_edges.py draws the exact 3D outline on the photo
print('tall height %.3f, short height %.3f' % (tall[2][-3][1] - G, short[2][-3][1] - G))
