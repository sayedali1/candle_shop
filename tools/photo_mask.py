"""Cuts the two puppies out of the photo and marks the part that is surely the LYING puppy (below the sitting puppy's contact line).
Writes tools/fit/mask.npz (union mask, care mask) and tools/fit/mask-preview.png. Photo coordinates are the full photo's pixels."""
import numpy as np, os
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'fit'); os.makedirs(OUT, exist_ok=True)
photo = Image.open(os.path.join(HERE, '..', 'brief', 'ref-poodle-candles.webp')).convert('RGB')
W, H = photo.size
a = np.array(photo).astype(np.float32) / 255
mx, mn = a.max(2), a.min(2); sat = (mx - mn) / np.maximum(mx, 1e-3)
m = (sat > 0.30) | (mx < 0.25)
box = np.zeros((H, W), bool); box[285:710, 150:500] = True
m &= box
m = ndi.binary_closing(m, iterations=3); m = ndi.binary_fill_holes(m)
lab, n = ndi.label(m); sizes = ndi.sum(m, lab, range(1, n + 1)); m = lab == (1 + int(np.argmax(sizes)))
m = ndi.binary_opening(m, iterations=2)
# the slab under the paws is picked up by colour: cut everything under the puppy's real bottom edge
B = [(150, 655), (200, 668), (265, 671), (300, 668), (330, 682), (380, 697), (430, 702), (460, 693), (484, 668), (500, 600)]
bx = np.arange(W); by = np.interp(bx, [p[0] for p in B], [p[1] for p in B])
yy = np.arange(H)[:, None]
m &= yy <= by[None, :] + 2
m[:, 483:] = False
# surely lying puppy: below the line where the sitting puppy's body meets the lying one's back
L = [(150, 545), (250, 552), (290, 528), (350, 524), (385, 508), (430, 497), (500, 497)]
ly = np.interp(bx, [p[0] for p in L], [p[1] for p in L])
care = m & (yy >= ly[None, :])
np.savez_compressed(os.path.join(OUT, 'mask.npz'), union=m, care=care, W=W, H=H)
prev = a.copy(); prev[m & ~care] = prev[m & ~care] * 0.5 + np.array([0.0, 0.0, 0.5])
prev[care] = prev[care] * 0.5 + np.array([0.5, 0.0, 0.0]); prev[~m] *= 0.45
im = Image.fromarray((prev * 255).astype(np.uint8)).crop((130, 280, 520, 720)); im.save(os.path.join(OUT, 'mask-preview.png'))
for nm, mk in (('union', m), ('care', care)): Image.fromarray((mk * 255).astype(np.uint8)).save(os.path.join(OUT, nm + '.png'))
print(W, H, int(m.sum()), int(care.sum()))
