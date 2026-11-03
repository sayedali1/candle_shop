"""Makes a candle's GLB smaller without changing its shape or its look:
- the colour texture (PNG, for its alpha cut-out) becomes WebP with the same alpha (EXT_texture_webp; three.js r160's GLTFLoader reads it)
- the normal map stays JPEG, re-saved at the same size
- UVs become 16-bit numbers (KHR_mesh_quantization, read natively by the loader), indices 16-bit when there are fewer than 65536 points
- normals are dropped: candle-builder.js recomputes them on load (the same averaging tools/gen_relief.py uses)
Positions stay full floats, so the outline the photo was matched to does not move.
Run:  python tools/shrink_glb.py assets/models/<name>.glb [webp quality, default 82]      Rewrites the file in place, keeps <name>.orig.glb next to it once."""
import io, json, os, shutil, struct, sys
import numpy as np
from PIL import Image

path = sys.argv[1]; Q = int(sys.argv[2]) if len(sys.argv) > 2 else 82
orig = path.replace('.glb', '.orig.glb')
if not os.path.exists(orig): shutil.copy(path, orig)
b = open(orig, 'rb').read(); n = struct.unpack('<I', b[12:16])[0]; js = json.loads(b[20:20 + n]); bin_ = b[20 + n + 8:]
bv = lambda i: bin_[js['bufferViews'][i].get('byteOffset', 0):js['bufferViews'][i].get('byteOffset', 0) + js['bufferViews'][i]['byteLength']]
DT = {5126: ('<f4', 4), 5125: ('<u4', 4), 5123: ('<u2', 2), 5121: ('<u1', 1)}; NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}


def read(ai):
    a = js['accessors'][ai]; dt, sz = DT[a['componentType']]; raw = bv(a['bufferView'])[a.get('byteOffset', 0):]
    return np.frombuffer(raw, dtype=dt, count=a['count'] * NC[a['type']]).reshape(a['count'], NC[a['type']])


blob, views, accs = b'', [], []
def add(raw, target=None):
    global blob
    v = {'buffer': 0, 'byteOffset': len(blob), 'byteLength': len(raw)}
    if target: v['target'] = target
    views.append(v); blob += raw + b'\0' * ((4 - len(raw) % 4) % 4); return len(views) - 1


used = set(js.get('extensionsUsed', []))
for mesh in js['meshes']:
    for prim in mesh['primitives']:
        at = prim['attributes']; P = read(at['POSITION']).astype('<f4')
        pa = {'bufferView': add(P.tobytes(), 34962), 'componentType': 5126, 'count': len(P), 'type': 'VEC3', 'min': P.min(0).tolist(), 'max': P.max(0).tolist()}
        accs.append(pa); new = {'POSITION': len(accs) - 1}
        if 'TEXCOORD_0' in at:
            U = np.clip(np.round(read(at['TEXCOORD_0']) * 65535), 0, 65535).astype('<u2')
            accs.append({'bufferView': add(U.tobytes(), 34962), 'componentType': 5123, 'normalized': True, 'count': len(U), 'type': 'VEC2'}); new['TEXCOORD_0'] = len(accs) - 1
            used.add('KHR_mesh_quantization')
        prim['attributes'] = new
        if 'indices' in prim:
            I = read(prim['indices']).ravel(); small = len(P) < 65536
            I = I.astype('<u2' if small else '<u4')
            accs.append({'bufferView': add(I.tobytes(), 34963), 'componentType': 5123 if small else 5125, 'count': int(I.size), 'type': 'SCALAR'}); prim['indices'] = len(accs) - 1
images = []
for im in js.get('images', []):
    raw = bv(im['bufferView']); pic = Image.open(io.BytesIO(raw)); out = io.BytesIO()
    if im['mimeType'] == 'image/png':
        pic.save(out, 'WEBP', quality=Q, method=6, exact=True); images.append({'bufferView': add(out.getvalue()), 'mimeType': 'image/webp'}); used.add('EXT_texture_webp')
    else:
        pic.convert('RGB').save(out, 'JPEG', quality=85, optimize=True); images.append({'bufferView': add(out.getvalue()), 'mimeType': 'image/jpeg'})
for t in js.get('textures', []):                                       # a WebP image is named through the extension, as the spec asks
    if images[t['source']]['mimeType'] == 'image/webp': t['extensions'] = {'EXT_texture_webp': {'source': t.pop('source')}}
js.update({'images': images, 'bufferViews': views, 'accessors': accs, 'buffers': [{'byteLength': len(blob)}], 'extensionsUsed': sorted(used)})
js['extensionsRequired'] = sorted(used & {'KHR_mesh_quantization', 'EXT_texture_webp'})
j = json.dumps(js, separators=(',', ':')).encode(); j += b' ' * ((4 - len(j) % 4) % 4)
with open(path, 'wb') as fh:
    fh.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(j) + 8 + len(blob))); fh.write(struct.pack('<II', len(j), 0x4E4F534A)); fh.write(j)
    fh.write(struct.pack('<II', len(blob), 0x004E4942)); fh.write(blob)
print(f'{path}: {os.path.getsize(orig) // 1024} KB -> {os.path.getsize(path) // 1024} KB')
