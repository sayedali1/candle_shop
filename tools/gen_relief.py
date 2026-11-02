"""Builds the candle's 3D surface directly from the photo: its form comes from the depth model, its skin is the photo's own pixels.
Every kept pixel of the photo's outline becomes a point on its ray through the photo's camera, so from that camera the model IS the photo, and turning it gives real depth.
The edge is rounded like a pillow so it does not look like a cut-out. The back is the same outline closed behind it, with a very blurred copy of the photo as skin: the photo never saw the back.
Run:  python tools/gen_relief.py [recipe-out] [grid step in pixels]          Writes assets/models/<name>.glb
Env:  DEPTH (form depth, candle units), PILLOW (edge rounding), R (rounding width in pixels)"""
import io, json, math, os, struct, sys
os.environ.setdefault('HF_HOME', 'D:/tools/depth')
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'recipes', 'zz-relief.json')
STEP = int(sys.argv[2]) if len(sys.argv) > 2 else 3
env = lambda k, v: float(os.environ.get(k, v))
DEPTH, PILLOW, R = env('DEPTH', '0.45'), env('PILLOW', '0.11'), env('R', '45')
MIX = bool(os.environ.get('MIX'))                                                     # wax with the photo's detail added softly: real light does the work, the photo only guides it
SIZE, TURN = 0.78, -0.12
CFG = lambda k, d: os.environ.get(k, d)                                               # any candle: its photo, outline, camera, eyes and wick (defaults are the poodle's)
cam = json.load(open(os.path.join(HERE, 'fit', CFG('POSE', 'pose.json'))))['camera']
name = os.path.splitext(os.path.basename(out))[0]

photo = Image.open(os.path.join(ROOT, 'brief', CFG('PHOTO', 'ref-poodle-candles.webp'))).convert('RGB'); W, H = photo.size
# the outline is traced by hand on the photo (tools/fit/outline.json). The silhouette fit's mask was not good enough: it held floor around a paw and missed part of a head
from PIL import ImageDraw
ol_ = json.load(open(os.path.join(HERE, 'fit', CFG('OUTLINE', 'outline.json'))))
mim = Image.new('L', (W, H), 0)
labim = Image.new('L', (W, H), 0)
for k_, poly_ in enumerate(ol_.get('outlines', [ol_.get('outline')])):
    ImageDraw.Draw(mim).polygon([tuple(q) for q in poly_], fill=255)   # several pieces in one photo (two knots): one mask
    ImageDraw.Draw(labim).polygon([tuple(q) for q in poly_], fill=k_ + 1)                  # and which piece each pixel belongs to
field = ndi.gaussian_filter((np.array(mim) > 0).astype(float), env('EDGE', '1.5')); MASK_T = env('MASK_T', '0.5'); mask = field > MASK_T   # a higher cut keeps the edge just inside the traced line, off the wood
ys, xs = np.where(mask); X0, X1, Y0, Y1 = max(xs.min() - 8, 0), min(xs.max() + 9, W), max(ys.min() - 8, 0), min(ys.max() + 9, H)

# depth on a tight crop: the model then spends its pixels on the candle, not on the room
import torch
from transformers import pipeline
pipe = pipeline('depth-estimation', model='depth-anything/Depth-Anything-V2-Small-hf', device=0 if torch.cuda.is_available() else -1)
crop = photo.crop((X0, Y0, X1, Y1)); cw, ch = crop.size
d = pipe(crop.resize((cw * 2, ch * 2), Image.LANCZOS))['predicted_depth']
d = torch.nn.functional.interpolate(d[None] if d.ndim == 3 else d[None, None], size=(ch, cw), mode='bicubic', align_corners=False)[0, 0].numpy()
m = mask[Y0:Y1, X0:X1]
lo, hi = np.percentile(d[m], 2), np.percentile(d[m], 98); d = np.clip((d - lo) / (hi - lo), 0, 1)
BAND = int(env('BAND', '9'))                                                         # near the outline the depth model blurs into the background: copy the depth from just inside, or the edge turns into spikes
dm_ = ndi.distance_transform_edt(m)
ridge = (dm_ >= ndi.maximum_filter(dm_, size=9)) & (dm_ > 2.5)                        # the middle line of thin parts (a paw) keeps its own depth: without it a paw borrows the body's depth and smears when turned
inner = (dm_ > BAND) | ridge
ix = ndi.distance_transform_edt(~inner, return_distances=False, return_indices=True)
d = d[ix[0], ix[1]]
d = ndi.gaussian_filter(d, 1.2)
for _ in range(3):                                                                    # where the depth changes very fast the photo sees the surface almost end-on, and its pixels stretch into streaks when turned: ease those slopes
    gr_ = np.hypot(*np.gradient(d)); w_ = np.clip(gr_ / env('SLOPE', '0.009') - 1, 0, 1)
    d = d * (1 - w_) + ndi.gaussian_filter(d, 4) * w_
cropA = np.array(crop); near = ndi.distance_transform_edt(~m, return_distances=False, return_indices=True)
cropA = cropA[near[0], near[1]]                                                      # outside the outline the skin repeats the wax, so no room colour can bleed in at the edge
alpha = np.clip((field[Y0:Y1, X0:X1] - MASK_T) / 0.12 + 0.5, 0, 1)                      # the real outline is cut in the texture, sharper than the mesh grid
m_geo = ndi.binary_dilation(m, iterations=STEP + 2)                                  # the mesh reaches a little past it
dist = ndi.distance_transform_edt(m); t_ = np.clip(dist / R, 0, 1); profile = np.sqrt(np.maximum(1 - (1 - t_) ** 2, 0))     # a round edge, not a cut-out


def rays():
    yaw, pitch, fov = cam['yaw'], cam['pitch'], cam['fov']; T = np.array(cam['target']); r = cam['dist']
    P = T + r * np.array([math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch)])
    f = (T - P) / np.linalg.norm(T - P); right = np.cross(f, [0, 1, 0]); right /= np.linalg.norm(right); up = np.cross(right, f)
    return P, f, right, up, math.tan(math.radians(fov) / 2)


P, f, right, upv, tn = rays(); ct, st = math.cos(-cam['yaw']), math.sin(-cam['yaw'])     # the model's frame: the photo's camera straight in front, so the page's front view IS the photo's view
o = np.array(P) / SIZE; o = np.array([o[0] * ct + o[2] * st, o[1], -o[0] * st + o[2] * ct])
t0 = float(cam['dist']) / SIZE


def point(px, py, t):
    u0, v0, rl = cam.get('u0', 0), cam.get('v0', 0), cam.get('roll', 0)               # a measured camera may sit off the picture's middle and lean a little
    x0, y0 = px - W / 2 - u0, -(py - H / 2 - v0); c_, s_ = math.cos(-rl), math.sin(-rl); xr, yr = x0 * c_ - y0 * s_, x0 * s_ + y0 * c_
    dw = (xr / (H / 2) * tn)[..., None] * right + (yr / (H / 2) * tn)[..., None] * upv + f
    dw = dw / np.linalg.norm(dw, axis=-1, keepdims=True)
    dl = np.stack([dw[..., 0] * ct + dw[..., 2] * st, dw[..., 1], -dw[..., 0] * st + dw[..., 2] * ct], -1)
    return o + dl * t[..., None]


# the grid: one point every STEP pixels; front and back share the outline
gy, gx = np.mgrid[Y0:Y1:STEP, X0:X1:STEP]; gh, gw = gy.shape
SOLIDS = bool(os.environ.get('SOLIDS'))


def grid_tris(idx_):
    t_ = []
    for j in range(gh - 1):
        for i in range(gw - 1):
            a, b, c, e = idx_[j, i], idx_[j, i + 1], idx_[j + 1, i], idx_[j + 1, i + 1]
            if a >= 0 and b >= 0 and c >= 0 and e >= 0: t_.append((a, c, b)); t_.append((b, c, e))
            elif a >= 0 and b >= 0 and c >= 0: t_.append((a, c, b))
            elif b >= 0 and c >= 0 and e >= 0: t_.append((b, c, e))
            elif a >= 0 and b >= 0 and e >= 0: t_.append((a, e, b))
            elif a >= 0 and c >= 0 and e >= 0: t_.append((a, c, e))
    return np.array(t_, dtype=np.int64).reshape(-1, 3)


if SOLIDS:
    # HIDDEN PARTS, worked out from the photo (the user's rule, 2026-11-03): the candle is whole objects, not one sheet seen from the front.
    # Each figure (found by colour, touching the base; pale parts it misses are added by hand in PARTS) is its own solid: its depth along the view equals
    # its seen width there (a round body: chord 2*sqrt(d*(2R-d)) from its own outline). The base (tray, dish) is one solid down to the table and out to
    # its own far rim (the ray is followed until it leaves the base's footprint or reaches the table). The base surface hidden under each figure is
    # filled smoothly from around it (the water is flat).
    pcfg = json.load(open(os.path.join(HERE, 'fit', CFG('PARTS', 'parts.json'))))
    cA = np.array(crop).astype(float); R_, G_, B_ = cA[..., 0], cA[..., 1], cA[..., 2]
    strong = ndi.binary_opening(m & (R_ > 140) & (G_ > 110) & (R_ - B_ > 55) & (G_ - B_ > 25), iterations=2)
    base_c = m & (B_ > R_ + 10)                                                         # the water: the base's top
    cutm = Image.new('L', (W, H), 0)                                                    # figures that touch in the photo (two ducklings): a cut line read by hand
    for ln_ in pcfg.get('cut', []): ImageDraw.Draw(cutm).line([tuple(q) for q in ln_], fill=1, width=4)
    strong &= ~(np.array(cutm) > 0)[Y0:Y1, X0:X1]
    lab_, nl_ = ndi.label(strong)
    near_ = ndi.binary_dilation(base_c, iterations=8); figs = []
    addm = Image.new('L', (W, H), 0)
    for poly_ in pcfg.get('add', []): ImageDraw.Draw(addm).polygon([tuple(q) for q in poly_], fill=1)
    addm = (np.array(addm) > 0)[Y0:Y1, X0:X1] & m & ~base_c
    for i_ in range(1, nl_ + 1):
        c_ = lab_ == i_
        if c_.sum() < env('MIN_PART', '300') or not (c_ & near_).any(): continue
        c_ = ndi.binary_fill_holes(ndi.binary_closing(c_, iterations=12, border_value=0)) & m & ~base_c & ~(np.array(cutm) > 0)[Y0:Y1, X0:X1] & ~ndi.binary_dilation(np.isin(lab_, [k for k in range(1, nl_ + 1) if k != i_ and (lab_ == k).sum() >= env('MIN_PART', '300')]), iterations=2)
        if (c_ & addm).any() or (ndi.binary_dilation(c_, iterations=3) & addm).any(): c_ = ndi.binary_fill_holes(c_ | addm)
        figs.append(c_)
    anyfig = np.any(figs, 0) if figs else np.zeros_like(m)
    chk_ = np.array(crop).astype(float) * 0.45; rng_ = np.random.default_rng(3)          # the pieces, to check by eye: each figure its own colour
    for c_ in figs: chk_[c_] = chk_[c_] * 0.3 + rng_.integers(80, 255, 3) * 0.7
    Image.fromarray(chk_.astype(np.uint8)).save(os.path.join(HERE, 'fit', f'parts-{name}.png'))
    # the base's surface under the figures: filled from around (harmonic fill of the depth)
    hole = ndi.binary_dilation(anyfig, iterations=3) & m; d_base = d.copy()
    ix_ = ndi.distance_transform_edt(hole, return_distances=False, return_indices=True); d_base[hole] = d_base[ix_[0][hole], ix_[1][hole]]
    for _ in range(200): d_base[hole] = ndi.gaussian_filter(d_base, 3)[hole]
    # each figure's own depth near its outline: copied from inside it, so the water behind does not leak in
    d_fig = d.copy(); prof_fig = np.zeros_like(profile); chord = np.zeros_like(profile)
    for c_ in figs:
        dc_ = ndi.distance_transform_edt(c_); inn = c_ & (dc_ > env('BAND_PART', '4'))
        if inn.any():
            j_ = ndi.distance_transform_edt(~inn, return_distances=False, return_indices=True); d_fig[c_] = d[j_[0][c_], j_[1][c_]]
        prof_fig[c_] = np.sqrt(np.maximum(1 - (1 - np.clip(dc_ / env('R_PART', '8'), 0, 1)) ** 2, 0))[c_]
        Rm = dc_.max(); chord[c_] = (2 * np.sqrt(np.maximum(dc_ * (2 * Rm - dc_), 0)))[c_]
    hgeo_full = (lambda g_: g_ - ndi.gaussian_filter(g_, env('CURL_G', '7')))(ndi.gaussian_filter(np.array(crop.convert('L')).astype(float) / 255, 1.2))

    def piece(mask_c, dd, pf_full, kind):
        keep_ = ndi.binary_dilation(mask_c, iterations=1 if kind == 'fig' else STEP + 2)[gy - Y0, gx - X0] if kind != 'fig' else mask_c[gy - Y0, gx - X0]
        idx_ = -np.ones(gy.shape, int); idx_[keep_] = np.arange(keep_.sum())
        yi, xi = gy[keep_] - Y0, gx[keep_] - X0; pf_ = pf_full[yi, xi]
        tf_ = t0 + DEPTH * (0.5 - dd[yi, xi]) - (env('PILLOW_PART', '0.06') if kind == 'fig' else PILLOW) * pf_ - env('RELIEF', '0.06') * hgeo_full[yi, xi] * np.clip(pf_ * 2.5, 0, 1)
        return keep_, idx_, tf_, pf_, yi, xi

    # the base is only where the base is: the convex outline of its own seen pixels (a tray is an oval). A figure standing up past its far rim (the big
    # duck's head) has no base behind it, or the filled water rises behind it as a sheet
    from scipy.spatial import ConvexHull
    by_, bx_ = np.where(m & ~anyfig); hv_ = ConvexHull(np.stack([bx_, by_], 1)).vertices
    bm_ = Image.new('L', (m.shape[1], m.shape[0]), 0); ImageDraw.Draw(bm_).polygon([(float(bx_[k]), float(by_[k])) for k in hv_], fill=1)
    base_m = m & (np.array(bm_) > 0)
    wy_, wx_ = np.where(base_c); top_w = np.full(m.shape[1], -1)                      # nor above its own rim: per column, no higher than the water's top edge
    for xq in np.unique(wx_): top_w[xq] = wy_[wx_ == xq].min()                          # plus the rim's width (RIM_UP px)
    top_w = ndi.minimum_filter1d(np.where(top_w < 0, 10 ** 6, top_w), 9).astype(float); top_w[top_w > 10 ** 5] = -1
    rows_ = np.arange(m.shape[0])[:, None]; base_m &= (top_w[None, :] < 0) | (rows_ >= top_w[None, :] - env('RIM_UP', '16'))
    dist_b = ndi.distance_transform_edt(base_m); prof_b = np.sqrt(np.maximum(1 - (1 - np.clip(dist_b / R, 0, 1)) ** 2, 0))
    parts_ = [('base', base_m, d_base, prof_b)] + [('fig', c_, d_fig, prof_fig) for c_ in figs]
    built = [piece(mk, dd, pf, kd) + (kd,) for kd, mk, dd, pf in parts_]
    # the base's top under the figures is the water, and water is flat: a plane fitted to the water the photo shows, met by each hidden pixel's sight line
    kb0, _, tfb0, _, yb0, xb0, _ = built[0]; seen_w = (base_c & ~hole)[yb0, xb0]
    Wpts = point(gx[kb0][seen_w].astype(float), gy[kb0][seen_w].astype(float), tfb0[seen_w])
    Aw = np.c_[Wpts[:, 0], Wpts[:, 2], np.ones(len(Wpts))]; cw_ = np.linalg.lstsq(Aw, Wpts[:, 1], rcond=None)[0]   # y = a x + b z + c
    under = hole[yb0, xb0]
    rd_ = point(gx[kb0][under].astype(float), gy[kb0][under].astype(float), np.ones(under.sum())) - o
    tpl = (cw_[0] * o[0] + cw_[1] * o[2] + cw_[2] - o[1]) / (rd_[:, 1] - cw_[0] * rd_[:, 0] - cw_[1] * rd_[:, 2])
    tfb0[under] = tpl; built[0] = built[0][:2] + (tfb0,) + built[0][3:]
    print(f'water plane fitted on {seen_w.sum()} seen points, filled under the figures on {under.sum()}')
    # the base's footprint on the table: its front points seen from above, closed into a convex outline
    from scipy.spatial import Delaunay
    kb, ib, tfb, pfb, yb, xb, _ = built[0]
    Vbase = point(gx[kb].astype(float), gy[kb].astype(float), tfb); y_tab = float(np.percentile(Vbase[:, 1], 0.5))
    foot = Delaunay(Vbase[:, [0, 2]])
    Vf_l, Vb_l, uv_l, tri_l, pf_l, off_ = [], [], [], [], [], 0; FIG_PLANES = []; base_n = int(built[0][0].sum())
    for keep_, idx_, tf_, pf_, yi, xi, kd in built:
        px_, py_ = gx[keep_].astype(float), gy[keep_].astype(float)
        cap = env('BASE_DEEP', '3.0') * pf_ if kd == 'base' else chord[yi, xi] * tf_ * tn / (H / 2) * env('BODY', '1.0')   # a figure: as deep as it is wide (px -> units at its depth)
        if kd == 'fig':
            # a figure is a whole, mirror-symmetric body worked out from the photo: it SITS on the base (its lowest outline point touches the base surface),
            # its middle plane stands upright half its seen width behind that point, and each pixel's front and back lie on that pixel's own sight line,
            # level-distance +-half-chord from the middle plane (half-chord from the outline: a round body). The front view stays exactly the photo's.
            mk = parts_[len(Vf_l)][1]; ys_, xs_ = np.where(mk)
            # a round body: from any angle its depth runs along the line of sight, centred on its middle. Its middle is on the sight line through the
            # middle of its outline, at the height where its lowest point just touches the water (centre height = water + half its seen width)
            xc_, yc_ = xs_.mean() + X0, ys_.mean() + Y0; rc = point(np.array(xc_), np.array(yc_), np.array(1.0)) - o
            unit = None; r_ = None
            for _ in range(3):                                                          # its size in units depends on its distance: settle both
                tguess = t0 if r_ is None else tc_
                unit = tguess * tn / (H / 2); r_ = (xs_.max() - xs_.min()) / 2 * unit * env('BODY', '1.0')
                yw_ = cw_[0] * (o[0] + rc[0] * tguess) + cw_[1] * (o[2] + rc[2] * tguess) + cw_[2]
                tc_ = float((yw_ + r_ - o[1]) / rc[1])
            C = o + rc * tc_; FIG_PLANES.append((mk, C, (C - o) / np.linalg.norm(C - o)))
            rd = point(px_, py_, np.ones(len(px_))) - o; fv = (C - o) / np.linalg.norm(C - o)
            tmid = ((C - o) @ fv) / (rd @ fv)                                           # each sight line's own middle: the plane through C facing the camera
            hc = 0.5 * chord[yi, xi] * unit * env('BODY', '1.0') + 0.002
            t_f = tmid - hc - env('RELIEF', '0.06') * 0.3 * hgeo_full[yi, xi] * np.clip(pf_ * 2.5, 0, 1); t_b = tmid + hc
            Vf_l.append(o + rd * t_f[:, None]); Vb_l.append(o + rd * t_b[:, None]); pf_l.append(pf_)
            uv_l.append(np.stack([(px_ - X0 + 0.5) / (cw * 2), (py_ - Y0 + 0.5) / ch], 1))
            tri_l.append(grid_tris(idx_) + off_); off_ += int(keep_.sum()); continue
        tb_ = tf_ + 0.002; alive = np.ones(len(tf_), bool); stp = env('MARCH', '0.004')
        for k_ in range(1, 600):                                                        # follow the view ray into the object until it leaves the base's footprint, reaches the table, or the cap
            tt_ = tf_ + k_ * stp; q_ = point(px_, py_, tt_)
            out_ = (q_[:, 1] < y_tab) | (foot.find_simplex(q_[:, [0, 2]]) < 0) | (k_ * stp > cap)
            newly = alive & out_; tb_[newly] = tf_[newly] + max(k_ - 1, 0) * stp + 0.002; alive &= ~out_
            if not alive.any(): break
        tb_[alive] = tf_[alive] + cap[alive]
        Vf_l.append(point(px_, py_, tf_)); Vb_l.append(point(px_, py_, tb_)); pf_l.append(pf_)
        uv_l.append(np.stack([(px_ - X0 + 0.5) / (cw * 2), (py_ - Y0 + 0.5) / ch], 1))
        tri_l.append(grid_tris(idx_) + off_); off_ += int(keep_.sum())
    Vf, Vb = np.vstack(Vf_l), np.vstack(Vb_l); pf = np.concatenate(pf_l); nv = len(Vf)
    uf = np.vstack(uv_l); SOLID_TRIS = np.vstack(tri_l).astype(np.uint32)
    wall_ = CFG('BASE_BACK', '')                                                       # the base's hidden walls and underside: one plain colour read off its seen wall (no stretched photo)
    BASE_BACK_UV = None if not wall_ else np.array([(float(wall_.split(',')[0]) - X0 + 0.5) / (cw * 2) + 0.5, (float(wall_.split(',')[1]) - Y0 + 0.5) / ch])
    profile = np.where(anyfig, prof_fig, profile); d = np.where(anyfig, d_fig, d)     # for the eye beads and the wick
    PILLOW_EYES = env('PILLOW_PART', '0.06')
    print(f'hidden parts: {len(figs)} figures as solids, base closed to the table (y {y_tab:.3f}) and its footprint')
keep = m_geo[gy - Y0, gx - X0]
if not SOLIDS:
  idx = -np.ones(gy.shape, int); idx[keep] = np.arange(keep.sum()); nv = int(keep.sum())
  df, pf = d[gy - Y0, gx - X0][keep], profile[gy - Y0, gx - X0][keep]
  h_geo = (lambda g_: g_ - ndi.gaussian_filter(g_, env('CURL_G', '7')))(ndi.gaussian_filter(np.array(crop.convert('L')).astype(float) / 255, 1.2))[gy - Y0, gx - X0][keep]
  tf = t0 + DEPTH * (0.5 - df) - PILLOW * pf - env('RELIEF', '0.06') * h_geo * np.clip(pf * 2.5, 0, 1)                                           # near pixels come toward the camera, the middle of each form bulges
  if os.environ.get('TMAP'):                                                            # each pixel's distance measured from outside (tools/gen_knot.py: a rope round a candle lies on a cylinder): the depth model only adds the small bumps
      tm_ = np.load(os.path.join(HERE, 'fit', os.environ['TMAP']))
      tm_ = tm_[np.clip(gy[keep], 0, H - 1), np.clip(gx[keep], 0, W - 1)].astype(float)
      tm_ = np.where(np.isnan(tm_), np.nanmax(tm_), tm_)
      tf = tf - t0 + tm_
  if os.environ.get('FLAT_BASE'):                                                       # off: pulling the lowest edge down to the shelf makes a flat flap and brings back the streaks at the paw (tried 2026-11-01)
      ybot = np.where(m.any(0), m.shape[0] - 1 - np.argmax(m[::-1], axis=0), 0)
      col_i = (gx[keep] - X0).astype(int); yb_ = ybot[col_i] + Y0
      dl_ = point(gx[keep].astype(float), yb_.astype(float), np.ones(len(col_i))) - o
      t_fl = np.where(dl_[:, 1] < -1e-3, -o[1] / np.minimum(dl_[:, 1], -1e-3), tf)
      wf = np.clip(1 - (yb_ - gy[keep]) / env('BASE_H', '26'), 0, 1) * (yb_ > Y1 - env('BASE_ZONE', '70'))
      tf = tf * (1 - wf) + t_fl * wf
  tb = tf + env('THICK', '0.32') * pf + 0.002                                           # the back follows the front and meets it at the outline: one closed solid, no loose flap when it turns
  px, py = gx[keep].astype(float), gy[keep].astype(float)
  Vf, Vb = point(px, py, tf), point(px, py, tb)
  floor = env('FLOOR', '0.025') if MIX else 0.0                                         # a cut slightly above the lowest wave: the underside becomes flat, the wavy bottom edge shrinks
  Vf[:, 1] = np.maximum(Vf[:, 1], floor); Vb[:, 1] = np.maximum(Vb[:, 1], floor)
  if os.environ.get('SEAT_Y'):
      # each piece SITS on the measured water (tools/measure_tray.py): its lowest point is moved along its own sight line onto the water's height.
      # The depth model only knows near and far inside the picture, not where a figure stands; the water plane does.
      SEAT = env('SEAT_Y', '0'); labk = np.array(labim)[gy[keep], gx[keep]]
      for k_ in np.unique(labk[labk > 0]):
          sel = np.where(labk == k_)[0]; lo_ = sel[np.argmax(gy[keep][sel])]
          r1 = point(px[lo_:lo_ + 1], py[lo_:lo_ + 1], np.ones(1))[0] - o
          dt_ = (SEAT - o[1]) / r1[1] - tf[lo_]
          tf[sel] += dt_; tb[sel] += dt_
      Vf, Vb = point(px, py, tf), point(px, py, tb)
# the skin: left half of the texture is the photo, right half a very blurred copy for the back
EYES = json.load(open(os.path.join(HERE, 'fit', os.environ['EYES']))) if os.environ.get('EYES') else {'eye': [(412, 569), (443, 563), (359, 394), (400, 396)], 'nose': [(455, 596), (392, 407)]}   # read off the photo (tools/fit/landmarks.png, top-head-grid.png)
normal_png = None
if MIX:
    SOFT, KEEP, BUMP = env('SOFT', '5'), env('KEEP', '0.6'), env('BUMP', '6')
    sharp = cropA.astype(float) / 255
    soft = np.stack([ndi.gaussian_filter(sharp[..., c], SOFT) for c in range(3)], -1)    # the big colour areas stay (cream muzzle, shade under the ear), the printed light and curls go
    wax = soft[m].mean(0) * env('WAX_L', '1.32')                                         # the wax colour is the candle's own average, not a guess
    col_ = wax + KEEP * (soft - soft[m].mean(0))
    yy, xx = np.mgrid[0:ch, 0:cw]; fw = np.zeros((ch, cw))                               # around the eyes and nose the photo stays sharper: the expression lives in the dark rims and the fur over the eyes
    for px_, py_ in EYES['eye'] + EYES['nose']:
        fw = np.maximum(fw, np.exp(-(((xx - (px_ - X0)) ** 2 + (yy - (py_ - Y0)) ** 2) / env('FACE_R', '13') ** 2)))
    face = wax + env('FACE_K', '0.8') * (sharp - soft[m].mean(0))
    col_ = col_ * (1 - fw[..., None]) + face * fw[..., None]
    for px_, py_ in EYES['eye']:                                                         # a soft dark rim around each eye: it keeps the eye readable in flame light
        col_ *= (1 - env('RIM', '0.62') * np.exp(-((xx - (px_ - X0)) ** 2 + (yy - (py_ - Y0)) ** 2) / 8.0 ** 2))[..., None]
    col_ *= (0.74 + 0.26 * np.clip(ndi.distance_transform_edt(m) / env('EDGE_AO', '9'), 0, 1))[..., None]   # the wax darkens gently toward the edge: rounder form, no light rim on the outline
    ybot_ = np.where(m.any(0), m.shape[0] - 1 - np.argmax(m[::-1], axis=0), 0)            # the wax darkens where it meets the shelf, so the figure sits down on its shadow
    col_ *= (0.66 + 0.34 * np.clip((ybot_[None, :] - yy) / env('FOOT_H', '14'), 0, 1) ** 0.8)[..., None]
    if env('LIFT_LOW', '0') > 0:                                                     # a wall in the photo's shadow: lift the lowest band of the outline toward the colour above it
        lowb = np.clip(1 - (ybot_[None, :] - yy) / env('LOW_H', '30'), 0, 1)[..., None] * env('LIFT_LOW', '0')
        col_ = col_ * (1 - lowb) + np.clip(col_ * 1.45, 0, 1) * lowb
    g_ = col_.mean(-1, keepdims=True); col_ = g_ + env('SAT', '0.82') * (col_ - g_)       # a little less colour in the wax: the flame's own light adds the orange
    cropA = (np.clip(col_, 0, 1) * 255).astype(np.uint8)
    TS = int(env('TEX', '2'))                                                            # the maps are made at twice the photo's size: a finer normal map, and an outline that does not show pixels
    g2 = np.array(crop.resize((cw * TS, ch * TS), Image.LANCZOS).convert('L')).astype(float) / 255
    h_ = (g2 - ndi.gaussian_filter(g2, env('CURL', '5') * TS)) + env('FINE', '0.7') * (g2 - ndi.gaussian_filter(g2, 1.6 * TS))   # two sizes: the curls, and the fine strands inside them
    yy2, xx2 = np.mgrid[0:ch * TS, 0:cw * TS]
    for px_, py_ in EYES['eye'] + EYES['nose']:
        r2 = ((xx2 - (px_ - X0) * TS) ** 2 + (yy2 - (py_ - Y0) * TS) ** 2) / (11.0 * TS) ** 2; h_ *= 1 - np.exp(-r2 * r2)   # the dark eyes and nose would read as deep pits: the beads take their place
    h_ = ndi.gaussian_filter(h_, 0.5 * TS)
    for px_, py_ in EYES['eye']:                                                         # a real lid: a soft ridge just above each eye, so the flame above casts shade onto the eye
        h_ += env('LID', '0.16') * np.exp(-(((xx2 - (px_ - X0) * TS) / (8.5 * TS)) ** 2 + ((yy2 - (py_ - 6 - Y0) * TS) / (3.0 * TS)) ** 2))
    nx_ = -ndi.sobel(h_, axis=1) / 8 * BUMP * TS; ny_ = ndi.sobel(h_, axis=0) / 8 * BUMP * TS
    nl_ = np.sqrt(nx_ ** 2 + ny_ ** 2 + 1); nrm = np.dstack([nx_ / nl_, ny_ / nl_, 1 / nl_]) * 0.5 + 0.5
    nimg = Image.new('RGB', (cw * 2 * TS, ch * TS), (128, 128, 255)); nimg.paste(Image.fromarray((nrm * 255).astype(np.uint8)), (0, 0))
    b2 = io.BytesIO(); nimg.save(b2, 'JPEG', quality=88); normal_png = b2.getvalue()
tex_c = Image.fromarray(np.dstack([cropA, (alpha * 255).astype(np.uint8)]), 'RGBA')
blur = Image.fromarray(np.array(cropA)).filter(__import__('PIL.ImageFilter', fromlist=['GaussianBlur']).GaussianBlur(14)).point(lambda v: int(v * (env('BACK_K', '0.62') if MIX else 1))).convert('RGBA'); blur.putalpha(tex_c.getchannel('A'))
if MIX:
    tex_c, blur = tex_c.resize((cw * TS, ch * TS), Image.LANCZOS), blur.resize((cw * TS, ch * TS), Image.BICUBIC)
    if env('SHARP', '0') > 0:                                                        # stretching smooths: sharpen the colour back, the outline (alpha) stays soft
        from PIL import ImageFilter
        a_ = tex_c.getchannel('A'); tex_c = tex_c.convert('RGB').filter(ImageFilter.UnsharpMask(radius=2, percent=int(env('SHARP', '0')), threshold=2)).convert('RGBA'); tex_c.putalpha(a_)
atlas = Image.new('RGBA', (tex_c.width * 2, tex_c.height)); atlas.paste(tex_c, (0, 0)); atlas.paste(blur, (tex_c.width, 0))
if not SOLIDS: uf = np.stack([(px - X0 + 0.5) / (cw * 2), (py - Y0 + 0.5) / ch], 1)
ub = uf.copy(); ub[:, 0] += 0.5
if SOLIDS and BASE_BACK_UV is not None: ub[:base_n] = BASE_BACK_UV
tris = [] if not SOLIDS else SOLID_TRIS
for j in (range(gh - 1) if not SOLIDS else []):
    for i in range(gw - 1):
        a, b, c, e = idx[j, i], idx[j, i + 1], idx[j + 1, i], idx[j + 1, i + 1]
        if a >= 0 and b >= 0 and c >= 0 and e >= 0: tris.append((a, c, b)); tris.append((b, c, e))
        elif a >= 0 and b >= 0 and c >= 0: tris.append((a, c, b))
        elif b >= 0 and c >= 0 and e >= 0: tris.append((b, c, e))
        elif a >= 0 and b >= 0 and e >= 0: tris.append((a, e, b))
        elif a >= 0 and c >= 0 and e >= 0: tris.append((a, c, e))
tris = np.array(tris, dtype=np.uint32).reshape(-1, 3)
# make sure the front faces the camera
n0 = np.cross(Vf[tris[0, 1]] - Vf[tris[0, 0]], Vf[tris[0, 2]] - Vf[tris[0, 0]])
if np.dot(n0, Vf[tris[0, 0]] - o) > 0: tris = tris[:, [0, 2, 1]]
# the wick stands where the photo shows it; the model is centred on it front to back (the page's flame sits at z = 0) and on its own width sideways
wx, wb, wt = (float(q) for q in CFG('WICK', '367,344,298').split(','))
cy, cx = int(min(max(wb + 12, Y0), Y1 - 1)), int(min(max(wx, X0), X1 - 1))
tw = t0 + DEPTH * (0.5 - d[cy - Y0, cx - X0])
if os.environ.get('SEAT_Y') and not SOLIDS:                                           # the wick stands on its seated figure: the front point nearest its base
    kk_ = int(np.argmin((px - wx) ** 2 + (py - (wb + 6)) ** 2)); tw = float(tf[kk_])
if SOLIDS:                                                                            # the wick stands on the figure it grows from: on that figure's middle plane
    for mk_, C_, hd_ in FIG_PLANES:
        if mk_[min(max(int(wb) + 6 - Y0, 0), mk_.shape[0] - 1), min(max(int(wx) - X0, 0), mk_.shape[1] - 1)]:
            r_ = point(np.array(wx), np.array(wb), np.array(1.0)) - o; tw = float(((C_ - o) @ hd_) / (r_ @ hd_)); break
b_, t_w = point(np.array(wx), np.array(wb), np.array(tw)), point(np.array(wx), np.array(wt), np.array(tw))
all_ = np.vstack([Vf, Vb]); shift = np.array([-(all_[:, 0].min() + all_[:, 0].max()) / 2, -all_[:, 1].min(), -float(b_[2])])
if os.environ.get('NOSHIFT'): shift = np.zeros(3)
if os.environ.get('TRAYFRAME'): shift = np.array([0.0, 0.0, -float(b_[2])])            # the measured tray's frame (table at 0, tray centred): only the wick is brought to z = 0
json.dump({'shift': shift.tolist(), 'yaw': cam['yaw']}, open(os.path.join(HERE, 'fit', f'shift-{name}.json'), 'w'))                                     # a figure that is one piece of a bigger candle (the mermaid's tail in its glass): keep the camera's own frame, where the glass is built
Vf, Vb, b_, t_w = Vf + shift, Vb + shift, b_ + shift, t_w + shift
ca_, sa_ = math.cos(-cam['yaw']), math.sin(-cam['yaw']); Tg = np.array(cam['target'])
Tn = np.array([Tg[0] * ca_ + Tg[2] * sa_, Tg[1], -Tg[0] * sa_ + Tg[2] * ca_]) + shift * SIZE
json.dump({'camera': {**cam, 'yaw': 0.0, 'target': Tn.tolist()}, 'blocks': []}, open(os.path.join(HERE, 'fit', f'pose-{name}.json'), 'w'), indent=1)   # the same camera, in the model's frame: for the Lab's photo view
V = np.vstack([Vf, Vb]).astype('<f4'); UV = np.vstack([uf, ub]).astype('<f4')
I = np.vstack([tris, tris[:, [0, 2, 1]] + nv]).astype('<u4')


def normals(v, t):
    n = np.zeros_like(v, dtype=float); c = np.cross(v[t[:, 1]] - v[t[:, 0]], v[t[:, 2]] - v[t[:, 0]])
    for k in range(3): np.add.at(n, t[:, k], c)
    return (n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)).astype('<f4')


N = normals(V, I)
buf = io.BytesIO(); atlas.save(buf, 'PNG', optimize=True); jpg = buf.getvalue()
pad = lambda b: b + b'\0' * ((4 - len(b) % 4) % 4)
views, blob = [], b''
for raw, target in ((V.tobytes(), 34962), (N.tobytes(), 34962), (UV.tobytes(), 34962), (I.tobytes(), 34963), (jpg, None)) + (((normal_png, None),) if normal_png else ()):
    v = {'buffer': 0, 'byteOffset': len(blob), 'byteLength': len(raw)}
    if target: v['target'] = target
    views.append(v); blob += pad(raw)
gltf = {'asset': {'version': '2.0', 'generator': 'gen_relief.py'}, 'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'mesh': 0}],
        'meshes': [{'primitives': [{'attributes': {'POSITION': 0, 'NORMAL': 1, 'TEXCOORD_0': 2}, 'indices': 3, 'material': 0}]}],
        'materials': [{'pbrMetallicRoughness': {'baseColorTexture': {'index': 0}, 'metallicFactor': 0, 'roughnessFactor': 0.75}, 'doubleSided': True, 'alphaMode': 'MASK', 'alphaCutoff': 0.5}],
        'textures': [{'source': 0, 'sampler': 0}], 'samplers': [{'magFilter': 9729, 'minFilter': 9729, 'wrapS': 33071, 'wrapT': 33071}],
        'images': [{'bufferView': 4, 'mimeType': 'image/png'}], 'bufferViews': views, 'buffers': [{'byteLength': len(blob)}],
        'accessors': [{'bufferView': 0, 'componentType': 5126, 'count': len(V), 'type': 'VEC3', 'min': V.min(0).tolist(), 'max': V.max(0).tolist()},
                      {'bufferView': 1, 'componentType': 5126, 'count': len(N), 'type': 'VEC3'}, {'bufferView': 2, 'componentType': 5126, 'count': len(UV), 'type': 'VEC2'},
                      {'bufferView': 3, 'componentType': 5125, 'count': int(I.size), 'type': 'SCALAR'}]}
if os.environ.get('PLAIN'):                                                          # the same shape in plain wax, with no photo skin: shows what the form alone gives
    gltf['materials'] = [{'pbrMetallicRoughness': {'baseColorFactor': [0.72, 0.42, 0.22, 1], 'metallicFactor': 0, 'roughnessFactor': 0.7}}]
    for k in ('textures', 'samplers', 'images'): gltf.pop(k)
if normal_png:
    gltf['images'].append({'bufferView': 5, 'mimeType': 'image/jpeg'}); gltf['textures'].append({'source': 1, 'sampler': 0})
    gltf['materials'][0]['normalTexture'] = {'index': 1}; gltf['materials'][0]['pbrMetallicRoughness']['roughnessFactor'] = 0.6
js = json.dumps(gltf, separators=(',', ':')).encode(); js += b' ' * ((4 - len(js) % 4) % 4)
path = os.path.join(ROOT, 'assets', 'models', f'{name}.glb')
with open(path, 'wb') as fh:
    fh.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob)))
    fh.write(struct.pack('<II', len(js), 0x4E4F534A)); fh.write(js); fh.write(struct.pack('<II', len(blob), 0x004E4942)); fh.write(blob)
recipe = {'name': CFG('NAME', 'the two puppies, surface built from the photo'), 'turn': 0, 'turnLimit': env('LIMIT', '0.3'), 'size': SIZE, 'shadow': 1.9, 'model': f'assets/models/{name}.glb', 'modelRaw': True, 'modelGlow': 0.32, 'modelEnv': 0.6, 'modelRough': 0.75,
          'materials': {}, 'parts': [], 'wicks': [{'kind': 'long', 'x': round(float(b_[0]), 3), 'z': round(float(b_[2]), 3), 'base': round(float(b_[1]) - 0.02, 3), 'tip': round(float(t_w[1]), 3), 'color': '#efe3cf', 'radius': 0.014}], 'flame': {'size': 0.85, 'width': 1.0}}
if MIX:                                                                              # real eyes and noses, as beads on the surface
    def on_face(px_, py_):
        x_, y_ = px_ - X0, py_ - Y0; tt = t0 + DEPTH * (0.5 - d[y_, x_]) - (PILLOW_EYES if SOLIDS else PILLOW) * profile[y_, x_] - 0.004
        return [round(float(v), 4) for v in point(np.array(float(px_)), np.array(float(py_)), np.array(tt)) + shift]
    recipe['materials'] = {'ink': {'kind': 'solid', 'color': '#100907', 'roughness': 0.3, 'clearcoat': 0.7, 'clearcoatRoughness': 0.12}}
    if not os.environ.get('BEADS', '1') == '1': recipe['parts'] = []              # the photo's own painted eyes, without bead eyes on top
    else: recipe['parts'] = [{'shape': 'dots', 'material': 'ink', 'r': env('EYE', '0.0155'), 'scale': [1.1, 0.9, 0.5], 'at': [on_face(*q) for q in EYES['eye']]},
                       {'shape': 'dots', 'material': 'ink', 'r': env('NOSE', '0.023'), 'scale': [1.2, 0.85, 0.75], 'at': [on_face(*q) for q in EYES['nose']]}]
    recipe['modelGlow'] = env('GLOW', '0.14'); recipe['modelGlowColor'] = CFG('GLOW_C', '#ffc79a'); recipe['shelfTilt'] = env('SHELF_TILT', '0'); recipe['shelfLift'] = env('SHELF_LIFT', '0'); recipe['flameLightPhone'] = env('FLAME_PHONE', '1'); recipe['flame'] = {'size': env('FLAME_SIZE', '0.85'), 'width': 1.0}; recipe['turnLimit'] = env('LIMIT', '0.22'); recipe['flameLight'] = env('FLAME_L', '0.35'); recipe['shelfSize'] = env('SHELF_SIZE', '0.92'); recipe['modelRough'] = 0.6
open(out, 'w', encoding='utf-8').write(json.dumps(recipe, ensure_ascii=False))
print(f'{len(V)} points, {len(I)} triangles, texture {atlas.size}, {os.path.getsize(path) // 1024} KB -> {path}')
