"""Joins the rebuilt head (recipes/zz-head.json, from landmarks) to the lying puppy's body (recipes/zz-lying.json, from the silhouette fit).
The old head block and everything that was built around it (ears, muzzle, brow, cheeks, skull patches) are dropped; the body blocks and the toes stay.
Run:  python tools/gen_join.py [recipe-out] [res]     then  node tools/bake-blob.mjs <recipe> assets/models/<name>.bin 96  and  python tools/paint_blob.py <bin> <col> 1.35"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'recipes', 'zz-puppy.json')
res = int(sys.argv[2]) if len(sys.argv) > 2 else 64
pose = json.load(open(os.path.join(HERE, 'fit', 'pose.json')))
body = json.load(open(os.path.join(HERE, '..', 'recipes', 'zz-lying.json')))
head = json.load(open(os.path.join(HERE, '..', 'recipes', 'zz-head.json')))
bb = [p for p in body['parts'] if p['shape'] == 'blob'][0]; hb = [p for p in head['parts'] if p['shape'] == 'blob'][0]
blocks = [b for b in pose['blocks'] if b['name'] not in ('muzzle', 'ear')]
paws = [b for b in pose['blocks'] if b['name'] == 'paw2']
n_blocks, n_toes = len(blocks), 3 * len(paws)
keep = bb['els'][:n_blocks + n_toes]
i_head = [i for i, b in enumerate(blocks) if b['name'] == 'head'][0]
keep = [e for i, e in enumerate(keep) if i != i_head]                    # the old head block goes; its place is taken by the new skull
cuts = bb['cuts'][:2 * len(paws)] + hb['cuts']                           # the toe grooves, then the head's own cuts
blob = dict(bb); blob['els'] = keep + hb['els']; blob['cuts'] = cuts; blob['tones'] = hb['tones']; blob['res'] = res
blob['k'] = 0.06; blob['relief'] = hb['relief']
name = os.path.splitext(os.path.basename(out))[0]
blob['bake'] = f'assets/models/{name}.bin'; blob['paint'] = f'assets/models/{name}.col'
recipe = dict(body); recipe['name'] = 'the lying puppy: fitted body with the head rebuilt from landmarks'
recipe['materials'] = dict(body['materials']); recipe['materials']['ink'] = head['materials']['ink']
recipe['parts'] = [blob] + [p for p in head['parts'] if p['shape'] == 'dots']
recipe['wicks'] = head['wicks']
open(out, 'w', encoding='utf-8').write(json.dumps(recipe, ensure_ascii=False))
print('els', len(blob['els']), 'cuts', len(blob['cuts']), '->', out)
