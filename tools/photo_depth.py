"""Guesses the depth of the reference photo with a small depth-estimation model (Depth Anything V2 Small, about 100 MB, downloaded once into D:/tools/depth).
The result is RELATIVE depth (near = bright), not metres: it is only used to compare shapes, see tools/depth_check.py.
Run:  python tools/photo_depth.py        Writes tools/fit/photo-depth.npy (float32, 0 = far, 1 = near) and tools/fit/photo-depth.png"""
import os, sys
os.environ.setdefault('HF_HOME', 'D:/tools/depth')
import numpy as np
from PIL import Image
import torch
from transformers import pipeline

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'fit')
img = Image.open(os.path.join(HERE, '..', 'brief', 'ref-poodle-candles.webp')).convert('RGB')
pipe = pipeline('depth-estimation', model='depth-anything/Depth-Anything-V2-Small-hf', device=0 if torch.cuda.is_available() else -1)
d = pipe(img)['predicted_depth']
d = torch.nn.functional.interpolate(d[None] if d.ndim == 3 else d[None, None], size=img.size[::-1], mode='bicubic', align_corners=False)[0, 0].numpy()
d = (d - d.min()) / (d.max() - d.min() + 1e-9)                       # the model gives bigger = nearer
np.save(os.path.join(OUT, 'photo-depth.npy'), d.astype(np.float32))
Image.fromarray((d * 255).astype(np.uint8)).save(os.path.join(OUT, 'photo-depth.png'))
print('depth', d.shape, 'saved')
