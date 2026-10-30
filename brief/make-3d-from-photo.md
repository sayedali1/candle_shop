# Making a 3D candle from a photo (for sculpted candles that shapes cannot copy)

Why: our recipes build candles from simple shapes. That is right for jars, pillars and cups, but not for a sculpted figure like the two poodle puppies: soft fur and faces need a model made from the photo.

## Steps
1. Pick ONE clear photo of the candle (the whole candle, nothing else in front of it, plain background if possible). Crop it so the candle fills the picture.
2. Open a free image-to-3D tool and upload the photo. Options (checked 2026-10-30, free tiers change, read each page):
   - Hunyuan3D (Tencent): free demo spaces on Hugging Face (shape, then texture). Non-commercial licence.
   - TRELLIS (Microsoft): open model, free demo spaces.
   - Tripo and Meshy: a free account gives some credits; GLB export is usually behind the free account.
3. Download the result as **GLB** (a single file with its texture inside).
4. Put it in `assets/models/` (e.g. `assets/models/poodle-pups.glb`) and tell Claude. Do not sign in or pay on the tool's site for anything beyond the free tier.

## What Claude does with the file
- Makes the recipe: `{ "model": "assets/models/poodle-pups.glb", "modelHeight": 1.2, "wicks": [...], "flame": {...} }` (already supported by the builder).
- Optimises it for phones (fewer triangles, a small texture) with gltf-transform.
- Checks it in the Lab against the photo, then on the shelf and in the detail sheet. Colour choices and the name label do not apply to a model file (size does).

## Honest limits
- The generated model is a guess of the back and the sides, so check all angles.
- Licences differ (some are non-commercial): check before using it for a paying client, and ask the seller if the candle design is hers.
