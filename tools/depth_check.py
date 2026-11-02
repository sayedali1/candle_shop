"""Compares the DEPTH of the 3D puppy with the depth the model guessed for the photo (tools/photo_depth.py), in the face crop, same camera as face_check.py.
Both are relative, so ours is first fitted to the photo's by a straight line (one scale, one offset) over the whole face region; what is left over is the error in shape.
Red = ours sticks out MORE than the photo (too near the camera), blue = ours sits too far back. Numbers are in 'percent of the head's depth range'.
Run:  python tools/depth_check.py [recipe.json]        Writes tools/fit/depth-check.png (photo | model depth | ours | difference)"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import face_check as fc                                     # runs the ray march: fc.t (distance to the body per pixel), fc.M (body mask), fc.PH, fc.PE
ff = fc.ff
X0, X1, Y0, Y1 = ff.X0, ff.X1, ff.Y0, ff.Y1
M = fc.M; shape = M.shape
t = fc.t.reshape(shape)
dep = np.load(os.path.join(HERE, 'fit', 'photo-depth.npy'))[Y0:Y1, X0:X1]
disp = np.where(M, 1.0 / np.maximum(t, 1e-3), 0)                # ours as disparity (near = big), like the model's output
reg = M & (fc.PH | fc.PE)                                       # fit only where the model's depth is trustworthy: inside the marked head and ear
A = np.stack([disp[reg], np.ones(reg.sum())], 1); coef = np.linalg.lstsq(A, dep[reg], rcond=None)[0]
ours = np.where(M, disp * coef[0] + coef[1], np.nan)
rng = np.nanpercentile(dep[reg], 95) - np.nanpercentile(dep[reg], 5)
err = (ours - dep) / rng * 100                                  # percent of the head's depth range
print(f'fit scale {coef[0]:.3f}, head depth range in model units {rng:.3f}')
print(f'inside head+ear: mean absolute error {np.nanmean(np.abs(err[reg])):.1f}%, bias {np.nanmean(err[reg]):+.1f}%')
spots = {'near eye': (412, 568), 'far eye': (442, 563), 'nose': (450, 597), 'muzzle': (440, 590), 'near cheek': (410, 595), 'brow': (425, 545), 'topknot': (425, 512), 'ear': (355, 580), 'chin': (435, 612)}
for nm, (x, y) in spots.items():
    xx, yy = x - X0, y - Y0; w = err[max(yy - 4, 0):yy + 5, max(xx - 4, 0):xx + 5]
    print(f'  {nm:11s} {np.nanmean(w):+6.1f}%' + ('   (ours too near)' if np.nanmean(w) > 8 else '   (ours too far back)' if np.nanmean(w) < -8 else ''))
photo = np.array(Image.open(os.path.join(HERE, '..', 'brief', 'ref-poodle-candles.webp')).convert('RGB').crop((X0, Y0, X1, Y1)))
lo, hi = np.nanpercentile(dep[reg], 1), np.nanpercentile(dep[reg], 99)
g = lambda a: np.repeat((np.clip((a - lo) / (hi - lo + 1e-9), 0, 1) * 255).astype(np.uint8)[..., None], 3, 2)
ours_img = g(np.nan_to_num(ours, nan=lo)); ours_img[~M] = 0
e = np.clip(np.nan_to_num(err) / 25, -1, 1); diff = np.stack([np.where(e > 0, 255, 255 * (1 + e)), 255 * (1 - np.abs(e)), np.where(e < 0, 255, 255 * (1 - e))], -1).astype(np.uint8)
diff = (diff * 0.75 + photo * 0.25).astype(np.uint8); diff[~M] = photo[~M] // 3
tiles = [photo, g(dep), ours_img, diff]
sheet = Image.new('RGB', (sum(x.shape[1] for x in tiles) * 3, tiles[0].shape[0] * 3))
xo = 0
for im in tiles:
    im3 = Image.fromarray(im).resize((im.shape[1] * 3, im.shape[0] * 3), Image.LANCZOS); sheet.paste(im3, (xo, 0)); xo += im3.width
dr = ImageDraw.Draw(sheet); w1 = tiles[0].shape[1] * 3
for i, lab in enumerate(('photo', 'model depth', 'our depth', 'red = ours too near')): dr.text((i * w1 + 6, 4), lab, fill=(255, 255, 255))
sheet.save(os.path.join(HERE, 'fit', 'depth-check.png')); print('saved tools/fit/depth-check.png')
