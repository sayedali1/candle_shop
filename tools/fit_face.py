"""Second fitting step, for the FACE: the silhouette fit (fit_pose.py) cannot see inside the figure, so the head came out as one big ball and the ear vanished into it.
Here the head and the near ear are fitted to hand-marked regions of the photo (polygons in photo pixels, read off tools/fit/face-grid.png), with the camera fixed.
Each part must cover its own region and nothing more; the head may hide behind the ear (it is in front of it).
Run:  python tools/fit_face.py          Reads tools/fit/pose.json, writes tools/fit/pose-face.json and tools/fit/face-fit-preview.png"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'fit'); sys.path.insert(0, HERE)
import fit_pose as fp

X0, X1, Y0, Y1, DS = 318, 502, 478, 662, 2
W, H = fp.W, fp.H
pose = json.load(open(os.path.join(OUT, 'pose.json')))
cam = pose['camera']; cx = np.array([cam['yaw'], cam['pitch'], cam['fov'], *cam['target']])

# the regions of the photo (photo pixels): the head with its muzzle (without the ear), and the near ear
HEAD_POLY = [(395, 500), (410, 496), (428, 497), (445, 505), (458, 520), (466, 545), (467, 568), (472, 585), (474, 598), (468, 608), (455, 617), (440, 620), (425, 622), (410, 615), (395, 605), (388, 585), (386, 560), (388, 535), (392, 515)]
EAR_POLY = [(352, 505), (375, 500), (388, 512), (387, 540), (386, 580), (384, 615), (378, 640), (355, 645), (335, 625), (325, 590), (325, 545), (335, 520)]


def poly_mask(poly):
    im = Image.new('L', (W, H), 0); ImageDraw.Draw(im).polygon(poly, fill=255)
    return (np.array(im) > 0)[Y0:Y1:DS, X0:X1:DS]


PH, PE = poly_mask(HEAD_POLY), poly_mask(EAR_POLY)
dPH, dPE = ndi.distance_transform_edt(~PH), ndi.distance_transform_edt(~PE)
fp.X0, fp.X1, fp.Y0, fp.Y1, fp.DS = X0, X1, Y0, Y1, DS


def block_mask(c, r, rot, P, D):
    ct, st = math.cos(fp.TURN), math.sin(fp.TURN)
    w = np.array([fp.SIZE * (c[0] * ct + c[2] * st), fp.SIZE * c[1], fp.SIZE * (-c[0] * st + c[2] * ct)])
    ang = rot + fp.TURN; ca, sa = math.cos(ang), math.sin(ang); Rinv = np.array([[ca, 0, -sa], [0, 1, 0], [sa, 0, ca]])
    rr = np.array(r) * fp.SIZE; o = (Rinv @ (P - w)) / rr; dd = (D @ Rinv.T) / rr
    a = (dd * dd).sum(-1); b = (dd * o).sum(-1); cq = (o * o).sum() - 1; disc = b * b - a * cq
    return (disc >= 0) & ((-b + np.sqrt(np.maximum(disc, 0))) / a > 0)


P, D = fp.cam_rays(cx)
head0 = [b for b in pose['blocks'] if b['name'] == 'head'][0]
a1 = math.radians(52)
EAR0 = {'c': [head0['c'][0] - 0.02, head0['c'][1] - 0.08, head0['c'][2] + 0.2], 'r': [0.07, 0.17, 0.12], 'rot': 1.2}
others = [b for b in pose['blocks'] if b['name'] not in ('head', 'ear', 'muzzle')]
OTH = np.zeros(PH.shape, bool)
for b in others: OTH |= block_mask(b['c'], b['r'], b['rot'], P, D)


def parts(v):
    h = {'c': [head0['c'][i] + v[i] for i in range(3)], 'r': [head0['r'][i] * math.exp(v[3 + i]) for i in range(3)], 'rot': 0.0}
    e = {'c': [EAR0['c'][i] + v[6 + i] for i in range(3)], 'r': [EAR0['r'][i] * math.exp(v[9 + i]) for i in range(3)], 'rot': EAR0['rot'] + v[12]}
    return h, e


def loss(v):
    h, e = parts(v)
    MH = block_mask(h['c'], h['r'], h['rot'], P, D); ME = block_mask(e['c'], e['r'], e['rot'], P, D)
    dMH, dME = ndi.distance_transform_edt(~MH), ndi.distance_transform_edt(~ME)
    # the head: must cover its region (where nothing else does), and may stick out only behind the ear
    unc = PH & ~(MH | OTH); over = MH & ~(PH | PE)
    # the ear: must match its region (it is in front)
    eun = PE & ~ME; eov = ME & ~(PE)
    err = unc.sum() + 0.5 * dMH[unc].sum() + over.sum() + 0.5 * dPH[over].sum() * 0 + 0.5 * (dPH + dPE)[over].sum() * 0.5
    err += eun.sum() + 0.5 * dME[eun].sum() + eov.sum() + 0.25 * dPE[eov].sum()
    reg = np.sum((v[0:3] / 0.05) ** 2) + np.sum((v[3:6] / 0.25) ** 2) + np.sum((v[6:9] / 0.08) ** 2) + np.sum((v[9:12] / 0.35) ** 2) + (v[12] / 0.5) ** 2
    return err + 2.0 * reg


if __name__ == '__main__':
    v = np.zeros(13); step = np.array([0.02] * 3 + [0.05] * 3 + [0.02] * 3 + [0.05] * 3 + [0.1]); best = loss(v)
    print('start', round(best, 1), flush=True)
    for it in range(70):
        improved = False
        for i in np.random.RandomState(it).permutation(13):
            for sg in (1, -1):
                w = v.copy(); w[i] += sg * step[i]; l = loss(w)
                if l < best - 1e-6: v, best, improved = w, l, True; break
        if not improved: step *= 0.6
        if it % 10 == 0: print(it, round(best, 1), flush=True)
        if step.max() < 0.002: break
    h, e = parts(v)
    print('final', round(best, 1), 'head', np.round(h['c'], 3).tolist(), np.round(h['r'], 3).tolist(), 'ear', np.round(e['c'], 3).tolist(), np.round(e['r'], 3).tolist(), round(e['rot'], 2))
    json.dump({'head': h, 'ear': e}, open(os.path.join(OUT, 'pose-face.json'), 'w'), indent=1)
    photo = np.array(Image.open(os.path.join(HERE, '..', 'brief', 'ref-poodle-candles.webp')).convert('RGB').crop((X0, Y0, X1, Y1))).astype(np.float32) / 255
    up = lambda m: np.array(Image.fromarray((m * 255).astype(np.uint8)).resize(photo.shape[1::-1], Image.NEAREST)) > 127
    MH = up(block_mask(h['c'], h['r'], h['rot'], P, D)); ME = up(block_mask(e['c'], e['r'], e['rot'], P, D))
    pv = photo * 0.6; pv[MH] = pv[MH] * 0.5 + np.array([0, 0.5, 0]); pv[ME] = pv[ME] * 0.5 + np.array([0.5, 0, 0.5])
    im = Image.fromarray((np.clip(pv, 0, 1) * 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    for poly, col in ((HEAD_POLY, (255, 255, 0)), (EAR_POLY, (0, 255, 255))):
        pts = [((x - X0), (y - Y0)) for x, y in poly]; d.line(pts + [pts[0]], fill=col, width=1)
    im.resize((im.width * 3, im.height * 3), Image.LANCZOS).save(os.path.join(OUT, 'face-fit-preview.png'))
