# Phone-ready GLB pipeline and lit-wax shading in three.js r160 (as of November 2026)

Evidence labels used throughout:
- **Measured locally** = run on this machine on 1 Nov 2026 with `@gltf-transform/cli` 4.5.1 on a synthetic mesh (a 1,000,000-triangle bumpy cylinder with an analytic surface, so error could be measured exactly). It is not a real generated mesh, and nothing was run on a phone.
- **Not run** = a recipe assembled from documented APIs. Blender, PyMeshLab, Instant Meshes and KTX-Software are not installed on this machine, so those steps are untested.

## End-to-end pipeline: what is the recommended route?

### Takeaway
Clean the mesh, drop UVs and normals, weld, reduce with a quadric simplifier to 24k to 48k triangles, unwrap, bake normal, colour and AO from the high-poly in Blender, bake thickness into vertex colours, then compress with meshopt. Only the gltf-transform steps were run here. Use `--ratio` and `--error` explicitly, because `optimize` alone will not reduce a mesh to budget.

### Cited Findings
- `gltf-transform optimize` defaults: `--compress meshopt`, `--texture-compress auto`, `--texture-size 2048`, `--simplify true`, with simplify ratio 0.0 and error 0.0001 — [glTF-Transform cli.ts](https://raw.githubusercontent.com/donmccurdy/glTF-Transform/main/packages/cli/src/cli.ts); [simplify.ts](https://raw.githubusercontent.com/donmccurdy/glTF-Transform/main/packages/functions/src/simplify.ts)
- Current package versions on 1 Nov 2026: `@gltf-transform/cli` 4.5.1 and `meshoptimizer` 1.3.0 — [npm registry](https://registry.npmjs.org/@gltf-transform/cli/latest); [npm registry](https://registry.npmjs.org/meshoptimizer/latest)
- Windows wheels exist for `pymeshlab` 2025.7.post1 (cp312 to cp314), `fast-simplification` 0.2.0, `pymeshfix` 0.18.1 and `manifold3d` 3.5.4. `bpy` 5.2.3 ships a cp313 Windows wheel — [PyPI pymeshlab](https://pypi.org/project/pymeshlab/); [PyPI bpy](https://pypi.org/project/bpy/); [PyPI fast-simplification](https://pypi.org/project/fast-simplification/); [PyPI pymeshfix](https://pypi.org/project/pymeshfix/); [PyPI manifold3d](https://pypi.org/project/manifold3d/)
- The current Blender manual is 5.2 LTS — [Blender manual](https://docs.blender.org/manual/en/latest/render/cycles/baking.html)

### Inferences
Recommended order (only steps 3 and 7 were run, on the synthetic mesh):

1. **Clean** with PyMeshLab: remove floaters, close small holes, repair non-manifold edges. Details are under the mesh repair question.
2. **Fix the base and orientation** with trimesh: slice flat, cap, stand upright.
3. **Reduce.** Two routes:
   - **Route A, keep the generated atlas, no baking.** This is the fast route. Weld, then simplify. It works only if the atlas is not too fragmented.
     ```bash
     npm i -D @gltf-transform/cli
     npx gltf-transform weld raw.glb w.glb
     npx gltf-transform simplify w.glb s.glb --ratio 0.048 --error 0.01
     ```
     `--ratio` is the vertex fraction to keep, so compute it as `target_tris / source_tris`.
   - **Route B, rebuild the UVs and bake.** This is the best quality and is recommended for hero candles. Reduce to 24k to 48k, unwrap fresh, bake from the untouched high-poly. A normal map lets the triangle count sit lower, near 24k, which leaves budget for seam vertices.
4. **Unwrap** the low-poly (Blender Smart UV Project, or `xatlas`).
5. **Bake** normal, base colour and AO in Blender headless at 2048, then downsample to 1024 (recipe under the baking question).
6. **Delight** the base colour. Preferably delight the source photo before generating, or use the low-frequency removal under the delighting question.
7. **Compress:** `npx gltf-transform meshopt s.glb out.glb --level high`
8. **Check in the browser:** `renderer.info` on a real phone, and vertex count as well as triangle count.

Size expectation for the geometry only, from the local measurements below: 48k triangles comes to about 215 to 283 KB with meshopt. A 1024 colour and 1024 normal map add more, and that addition was not measured because KTX-Software is not installed.

### Gaps
- The whole chain has not been run end to end on a real generated GLB.
- No file size was measured for textures.

## Decimation and retopology: which keeps bumpy detail best at 20k to 50k triangles, and can it run from a script on Windows?

### Takeaway
No independent benchmark on generated meshes was found, so the ranking rests on how the algorithms work plus one synthetic test. Use quadric edge collapse (meshoptimizer via gltf-transform, or PyMeshLab) for a bumpy organic candle. Keep remeshers (Voxel, QuadriFlow, Instant Meshes) as tools for repair or for clean topology, not for keeping detail. All of them have Windows builds and a batch or Python interface, except that QRemeshify's scripting path was not checked.

### Cited Findings
**meshoptimizer and gltf-transform**
- `target_error` is normalized: 1e-2 aims to keep error below 1% of mesh extents — [meshoptimizer README](https://raw.githubusercontent.com/zeux/meshoptimizer/master/README.md)
- The simplifier follows original topology to preserve attribute seams and borders, and can get stuck on faceted or seam-heavy meshes, so identical vertices should be welded first — [meshoptimizer README](https://raw.githubusercontent.com/zeux/meshoptimizer/master/README.md)
- `simplifyWithAttributes` weights normals and vertex colours around 1.0 and UVs around 10 to 100. `SimplifyPermissive` can collapse across discontinuities, and `SimplifyPrune` removes isolated components — [meshoptimizer README](https://raw.githubusercontent.com/zeux/meshoptimizer/master/README.md)
- gltf-transform says to weld before simplifying, and that topology, particularly split vertices, limits the simplifier — [gltf-transform simplify docs](https://gltf-transform.dev/modules/functions/functions/simplify)
- The CLI `simplify` passes only an optional `LockBorder` flag — [simplify.ts](https://raw.githubusercontent.com/donmccurdy/glTF-Transform/main/packages/functions/src/simplify.ts)

**Measured locally: quadric simplify on a 1M-triangle mesh** (28 MB raw GLB; error as % of candle height, from 400k surface samples against the exact surface)

| Triangles | Vertices | Mean error | P99 | Max | On a 20 cm candle (mean / max) |
|---|---|---|---|---|---|
| 99,999 | 50,370 | 0.0097% | 0.042% | 0.11% | 0.02 mm / 0.22 mm |
| 47,998 | 24,246 | 0.0145% | 0.056% | 0.17% | 0.03 mm / 0.34 mm |
| 20,000 | 10,162 | 0.0246% | 0.089% | 0.25% | 0.05 mm / 0.51 mm |

The test surface was smooth by construction, with no sharp creases or noise, so a real generated mesh should show larger errors. `--error` values of 0.01, 0.002 and 0.0005 gave identical results at ratio 0.048, so on this mesh the triangle target was the limit, not the error limit.

**Measured locally: effect of a fragmented UV atlas** (same mesh, split into square charts, simplify at `--ratio 0.048 --error 0.01`)

| UV charts | Source vertices | Result triangles | Result vertices |
|---|---|---|---|
| 400 | 530,400 | 47,999 | 30,062 |
| 6,400 | 626,400 | 47,999 | 53,801 |
| 40,000 (25 triangles per chart) | 840,000 | 79,996 (missed target) | 159,996 |
| 6,400, after removing UV and NORMAL then welding | 501,501 | 47,997 | 24,247 |

An early buggy version of this test split almost every vertex, and the simplifier removed essentially nothing (1,000,000 triangles in, about 999,998 out). That supports the same conclusion at the extreme.

**Blender operators** ([bpy.ops.object API](https://docs.blender.org/api/current/bpy.ops.object.html))
- `quadriflow_remesh(use_mesh_symmetry=True, use_preserve_sharp=False, use_preserve_boundary=False, preserve_attributes=False, smooth_normals=False, mode='FACES', target_ratio=1.0, target_edge_length=0.1, target_faces=4000, mesh_area=-1.0, seed=0)`. The doc warns that all data layers will be lost.
- `voxel_remesh()` calculates a new manifold mesh from volume and also loses all data layers. It takes no arguments, so voxel size is set on the mesh data.
- QuadriFlow requires a manifold mesh with consistent normals, according to one guide of low authority — [Retopology guide](https://glama.ai/mcp/servers/@ShirshovDIM/retopoflow_blender_mcp/blob/78358fedc1d6d47808d380d331e176370b479c59/docs/retopology_guide.md)

**PyMeshLab**
- `meshing_decimation_quadric_edge_collapse(targetfacenum=..., targetperc=0, qualitythr=0.3, preserveboundary=False, boundaryweight=1, preservenormal=False, ...)` and a `_with_texture` variant — [PyMeshLab filter list](https://pymeshlab.readthedocs.io/en/latest/filter_list.html)

**Instant Meshes**
- Batch mode exists: `-o` output (PLY/OBJ), `-f` face count, `-v` vertex count, `-d` deterministic, `-c` crease angle, `-S` smoothing steps (default 2), `-D` tri/quad dominant, `-b` align to boundaries, `-r` orientation symmetry (2, 4, 6), `-p` position symmetry (4 or 6) — [Instant Meshes main.cpp](https://raw.githubusercontent.com/wjakob/instant-meshes/master/src/main.cpp)
- Prebuilt Windows binaries are linked from the README — [Instant Meshes README](https://raw.githubusercontent.com/wjakob/instant-meshes/master/README.md)
- It was published in 2015 and produces highly isotropic output that snaps to sharp features — [BlenderNation](https://www.blendernation.com/2015/11/16/instant-meshes-a-free-qaud-based-autoretopology-program/)
- Opinion is split: one user found it much cleaner than Decimate on a sculpt — [GameDev.net](https://gamedev.net/blogs/entry/2261896-instant-meshes-retopo); a later vendor article calls it slower and lower quality than commercial tools, and that source sells render services — [SuperRenders](https://superrendersfarm.com/article/quad-remesher-blender-retopology)

**Newer free tools**
- `fast-simplification` is a Python wrapper of Fast-Quadric-Mesh-Simplification, installable with pip and MIT licensed — [GitHub](https://github.com/pyvista/fast-simplification); [Arch package page](https://www.archlinux.org/packages/extra/x86_64/python-fast-simplification)
- QRemeshify is a Blender extension built on QuadWild with a Bi-MDF solver. It requires Blender 4.2 or later and lists Windows support, with Linux and macOS still being tested — [GitHub](https://github.com/Ksami/QRemeshify)
- gltfpack is an alternative to gltf-transform, and the README recommends native binaries for efficiency and texture compression — [meshoptimizer README](https://raw.githubusercontent.com/zeux/meshoptimizer/master/README.md)

### Inferences
- Quadric collapse spends triangles where curvature is high, so bumps get more of them. Remeshers distribute edges roughly evenly, so on a mostly flat candle with local bumps they waste triangles on the smooth areas and undersample the bumps. This is reasoning from how the algorithms work, not a measured comparison.
- Remeshers lose UVs and colours, so they force Route B anyway. Their value is making a manifold shell (voxel) or clean edge flow for deformation, which a static candle does not need.
- **Check seam vertices, not only triangles.** A generated atlas with very small charts can miss the target or inflate vertices. Since the 6,400-chart case had more vertices than triangles, count both after simplifying. If the result stalls, strip UV and NORMAL, weld and simplify, then use Route B.
- Geometric error is a poor proxy for how bumps look. Sub-millimetre position error can still change the shading, because vertex normals become undersampled between kept vertices. This is the case for a normal bake even at 48k.
- Suggested starting commands, **not run**:
  ```bash
  # Instant Meshes, triangle output at 24k faces
  "Instant Meshes.exe" clean.obj -o low.obj -f 24000 -d -r 6 -p 6
  ```
  ```python
  # PyMeshLab
  ms.meshing_decimation_quadric_edge_collapse(targetfacenum=48000, qualitythr=0.3, preservenormal=True, planarquadric=True)
  ```
  `planarquadric` comes from memory of the filter's option list and should be checked against the page.

### Gaps
- No published comparison of these tools on image-to-3D output was found. A real candle mesh should be run through at least quadric and Instant Meshes and compared under a raking light.
- Whether `gltf-transform simplify` exposes attribute weights: the CLI code seen sets only `LockBorder`. `simplifyWithAttributes` may need a custom Node script.
- Windows support for xatlas on Python 3.12 or later is unconfirmed: the wheel listing checked showed cp38 and cp39, but the listing was only partly inspected.

## Baking: how to bake normal and AO by script, what texture size, and what do KTX2 and memory cost?

### Takeaway
Blender headless with Cycles covers normal, colour and AO, and xNormal is an older alternative. Target 1024 for colour and normal on phones, with AO in vertex colours or at 512. KTX2 cuts GPU memory by about 4 to 8 times, but for one or two candles on a page the 260 KB gzipped transcoder may cost more download than it saves, so WebP or JPEG is a fair choice there.

### Cited Findings
**Blender**
- Signature: `bpy.ops.object.bake(type='COMBINED', pass_filter=set(), filepath='', width=512, height=512, margin=16, margin_type='EXTEND', use_selected_to_active=False, max_ray_distance=0.0, cage_extrusion=0.0, cage_object='', normal_space='TANGENT', normal_r='POS_X', normal_g='POS_Y', normal_b='POS_Z', target=..., save_mode=..., use_clear=...)` — [bpy.ops.object API](https://docs.blender.org/api/current/bpy.ops.object.html)
- Baking requires a UV map and either a Color Attribute or an Image Texture node. The active node or attribute is the target. Cycles uses its render settings (samples, bounces) for baking. AO bakes ignore all lights — [Blender manual, Render Baking](https://docs.blender.org/manual/en/latest/render/cycles/baking.html)
- A custom cage must have the same face count and ordering as the active object. Rays are cast inward from the low-poly, which is why extrusion is needed if the high-poly is not enclosed. This is from the 2014 commit, so it is old — [Blender bake API commit](https://developer.blender.org/rB97641a0)

**Texture sizes and KTX2**
- Texture resolution is usually no larger than 2048, and an ORM texture can be 1/4 of base colour resolution — [Khronos KTX Artist Guide](https://raw.githubusercontent.com/KhronosGroup/3D-Formats-Guidelines/main/KTXArtistGuide.md)
- Khronos example lamp: JPG and PNG at 13 MB file becomes 96 MB in GPU memory; KTX brings it to 10 MB file and 21 MB in GPU memory, or 22% of the GPU size — [Khronos KTX Artist Guide](https://raw.githubusercontent.com/KhronosGroup/3D-Formats-Guidelines/main/KTXArtistGuide.md)
- UASTC works better for normal and packed ORM textures. ETC1S suits mostly solid colour — [Khronos KTX Artist Guide](https://raw.githubusercontent.com/KhronosGroup/3D-Formats-Guidelines/main/KTXArtistGuide.md). **MDN conflicts in part:** it says compressed formats are generally only acceptable for colours, not normals — [MDN WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices). Khronos is the more specific and is backed by its examples, so UASTC normals are reasonable if checked by eye.
- For single-model display, Khronos says WebP or JPEG may be preferable if file size matters more than memory — [Khronos KTX Artist Guide](https://raw.githubusercontent.com/KhronosGroup/3D-Formats-Guidelines/main/KTXArtistGuide.md)
- Khronos's high-quality normal settings: `toktx --genmipmap --t2 --encode uastc --uastc_quality 4 --uastc_rdo_l .25 --uastc_rdo_d 65536 --zcmp 22 --assign_oetf linear --assign_primaries none out.ktx2 in.png` — [Khronos KTX Artist Guide](https://raw.githubusercontent.com/KhronosGroup/3D-Formats-Guidelines/main/KTXArtistGuide.md)
- The current KTX tool is `ktx create` (reference 5.0.0). UASTC RDO lambda defaults to 1.0, with 0.25 to 0.75 suggested for normals, and UASTC should be paired with `--zstd`. `--normal-mode` stores X in RGB and Y in alpha — [KTX Tools reference](https://github.khronos.org/KTX-Software/ktxtools/ktx_create.html)
- gltf-transform `etc1s` and `uastc` call `toktx` and list KTX-Software as a dependency. Options include `--slots`, `--resize`, `--level`, `--rdo`, `--rdo-lambda`, `--zstd` — [cli.ts](https://raw.githubusercontent.com/donmccurdy/glTF-Transform/main/packages/cli/src/cli.ts)
- **Measured locally:** r160 decoder sizes from the published package. Basis transcoder is 500 KB wasm plus 62 KB JS (245 + 16 KB gzipped). Draco is 192 KB wasm plus 58 KB wrapper (63 + 12 KB gzipped). Meshopt is 25 KB (6.5 KB gzipped) — [three@0.160.0 examples/jsm/libs](https://unpkg.com/three@0.160.0/examples/jsm/libs/)

**Thickness and AO** are covered under the wax shading question.

### Inferences
**GPU memory for one texture with mips** (arithmetic: pixels × bytes per pixel × 1.33. The bit rates are standard format figures, not re-checked in a source: RGBA8 is 32 bpp, ASTC 4×4 is 8 bpp, ETC1/ETC2 RGB is 4 bpp.)

| Size | JPEG, PNG or WebP (RGBA8) | UASTC to ASTC 4×4 | ETC1S to ETC RGB |
|---|---|---|---|
| 512 | 1.4 MB | 0.35 MB | 0.17 MB |
| 1024 | 5.6 MB | 1.4 MB | 0.7 MB |
| 2048 | 22.4 MB | 5.6 MB | 2.8 MB |

**Suggested set for a hero candle:** 1024 colour (ETC1S or WebP), 1024 normal (UASTC), AO and thickness in vertex colours. If a shelf shows many candles, use KTX2 and go to 512 or 768 per candle.

**Do not use `--normal-mode` as is.** It stores X in RGB and Y in alpha, while three.js's standard normal map path reads RGB. Using it would need a shader patch. This follows from the docs and is not tested.

**Vendoring:** the site's `vendor/three` holds only `GLTFLoader.js` in `loaders` and no `libs` decoders (checked locally). KTX2 needs `KTX2Loader.js`, `utils/WorkerPool.js`, `libs/ktx-parse.module.js`, `libs/zstddec.module.js` and `libs/basis/`.

**Blender headless recipe (not run):**
```python
# blender -b --python bake.py -- high.glb low.glb outdir
import bpy, sys
hi, lo, out = sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene; s.render.engine = 'CYCLES'; s.cycles.samples = 16
def imp(p):
    bpy.ops.import_scene.gltf(filepath=p)
    return [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
H, L = imp(hi), imp(lo)
h = max(H.dimensions)
mat = bpy.data.materials.new('bake'); mat.use_nodes = True; L.data.materials.clear(); L.data.materials.append(mat)
def bake(name, size, space, **kw):
    img = bpy.data.images.new(name, size, size); img.colorspace_settings.name = space
    n = mat.node_tree.nodes.new('ShaderNodeTexImage'); n.image = img; mat.node_tree.nodes.active = n
    bpy.ops.object.select_all(action='DESELECT'); H.select_set(True); L.select_set(True)
    bpy.context.view_layer.objects.active = L
    bpy.ops.object.bake(use_selected_to_active=True, cage_extrusion=0.01*h, max_ray_distance=0.02*h, margin=16, **kw)
    img.filepath_raw = f'{out}/{name}.png'; img.file_format = 'PNG'; img.save()
bake('normal', 2048, 'Non-Color', type='NORMAL', normal_space='TANGENT')
bake('color', 2048, 'sRGB', type='DIFFUSE', pass_filter={'COLOR'})
```
Extrusion of 1% and ray distance of 2% of the largest dimension are starting values, not sourced. Raise them if the bake shows holes, lower them if detail smears. Baking at 2048 and downsampling reduces aliasing.

**Normal convention:** `normal_g='POS_Y'` is the Blender default and glTF uses +Y as well, so no flip should be needed. Confirm this on a test candle. Three.js derives tangents from screen-space derivatives if the GLB has none, while Blender bakes in MikkTSpace, so seams may show faintly. Exporting tangents adds vertex data, so try without them first.

### Gaps
- `toktx` status: gltf-transform 4.5.1 calls it, the 5.0 reference documents `ktx create`, and the KTX-Software README has no mention of `toktx` in a text search. Check whether the current Windows installer still ships `toktx.exe`, otherwise install a 4.x release or run `ktx create` on the PNGs separately.
- xNormal was named in a forum thread only. Its current status on Windows 11 was not checked, and it has no script path that was verified here.
- No KTX2 sizes were measured for real candle textures.

## Compression: Draco versus meshopt, commands, loading in r160, and real file sizes

### Takeaway
Use meshopt for one or a few candles, since it wins on total download at this scale once decoders are counted, decodes faster and needs a much smaller decoder. Draco gives the smaller file (about 40% smaller than meshopt before transfer compression), so it pays off only for a shelf with several unique models, or if the host does not gzip GLB files. Both work with r160, and the output from the current gltf-transform was verified to decode with r160's meshopt decoder.

### Cited Findings
**Measured locally (geometry only, POSITION + NORMAL + UV, no textures, gzip level 9):**

| Encoding | 47,998 triangles | gzipped | 20,000 triangles | gzipped |
|---|---|---|---|---|
| Simplified, uncompressed | 1,064,752 | 789,713 | 446,076 | 331,606 |
| `quantize` only | 774,032 | 586,334 | 324,364 | 248,955 |
| `meshopt --level medium` | 371,708 | 296,257 | 161,832 | 132,154 |
| `meshopt` (default, `high`) | 283,188 | 214,658 | 123,972 | 97,104 |
| `draco` (default) | 171,780 | 169,828 | 77,384 | 76,301 |

Sizes are in bytes. Including the decoder, gzipped, at 48k: meshopt is 214,658 + 6,461 = 221 KB and Draco is 169,828 + 74,764 = 245 KB. Decoders are cached after the first model. Per-model difference is 45 KB, so Draco overtakes after about two unique models at 48k, at the cost of slower decoding. Decode time was not measured.

**Measured locally, r160 compatibility:** gltf-transform 4.5.1 wrote `extensionsRequired: ["EXT_meshopt_compression", "KHR_mesh_quantization"]`. All 4 buffer views decoded without error using `three@0.160.0`'s `meshopt_decoder.module.js` under Node. The vendored r160 `GLTFLoader.js` knows `EXT_meshopt_compression` (line 509) but has no `KHR_meshopt_compression`, as a search of the file showed.

**Published figures**
- Meshopt decodes at 3 to 6 GB/s on desktop CPUs, with vertex compression typically 2 to 4 times over quantized data and indices at 1 to 1.2 bytes per triangle — [meshoptimizer README](https://raw.githubusercontent.com/zeux/meshoptimizer/master/README.md)
- A blog gives Draco a 50 to 80% reduction and meshopt 30 to 60%, with meshopt 5 to 10 times faster to decode, but the figures are unverified — [svilenkovic.com](https://www.svilenkovic.com/3d/draco-vs-meshopt)
- A three.js forum user found Draco's advantage almost insignificant for ~20k triangle models with gzip, and long loading times with Draco. Local measurement here disagrees mildly: Draco was still 21% smaller gzipped at 20k — [three.js forum](https://discourse.threejs.org/t/dracoloader-takes-more-time/45613)
- Google's model-viewer discussion notes meshopt also compresses animation, which Draco does not — [model-viewer issue 1164](https://github.com/google/model-viewer/issues/1164)

### Inferences
**Loading in r160 with an import map, no build step (not run on the site):**
```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js'; // only if using KTX2
const ktx2 = new KTX2Loader().setTranscoderPath('vendor/three/examples/jsm/libs/basis/').detectSupport(renderer);
const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).setKTX2Loader(ktx2);
```
Copy the decoder from the r160 package itself so that it matches the loader. The `three/addons/` alias assumes the page's import map has that entry.

**Pin the tool version.** Since r160 lacks `KHR_meshopt_compression`, a future gltf-transform that writes the KHR form would fail on the site. Check `extensionsRequired` in the output after any upgrade.

**Check gzip on the host.** The meshopt advantage depends on transfer compression. Look at `content-encoding` on the deployed GLB. The site has `vercel.json`, and whether Vercel compresses `.glb` by default was not checked. If it does not, meshopt is 283 KB against Draco's 172 KB.

### Gaps
- Decode time on a mid-range Android phone was not measured. No credible phone benchmark was found.
- Results come from a smooth synthetic mesh, and real meshes will compress somewhat differently.

## Phone budgets: triangles, texture memory and draw calls for mid-range Android in 2025-2026

### Takeaway
The site's 48k budget is on solid ground: Google's own guidance calls 30k to 50k triangles ideal and 100k the limit, though for its native viewer rather than WebGL. No authoritative 2025-2026 mid-range Android WebGL number exists for texture memory or draw calls. Treat the figures below as starting points and test on a real device.

### Cited Findings
- **Best anchor:** Google's Scene Viewer recommends at most 100,000 triangles, with 30,000 to 50,000 ideal, 2048 × 2048 maximum texture size, up to 10 materials with one mesh per material, and file size under 10 MB. It flags over 15 MB as an error. It publishes no draw-call budget — [Google Scene Viewer](https://developers.google.com/ar/develop/scene-viewer)
- Triangle size: an Arm engineer's rule of thumb is more than 10 fragments per primitive — [Arm community](https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/triangles-per-second-performance-metric-or-chocolate-teapot)
- Arm's 2025 talk lists a 3 to 6 W power budget for mobile systems, and says smaller triangles make hidden-surface removal less effective — [Arm, Vulkanised 2025 PDF](https://www.vulkan.org/user/pages/09.events/vulkanised-2025/T18-Pete-Harris-Arm-MobileBestPractices.pdf)
- WebGL has no portable VRAM query. MDN advises estimating usage, handling `webglcontextlost`, and offering quality settings — [MDN WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices)
- WebGL guarantees only 8 texture image units as a minimum, and MDN warns against assuming more. Mipmaps add about 33% — [MDN WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices)
- Draw calls: blogs suggest 100 to 150 per frame for 60 fps — [hontran.dev](https://www.hontran.dev/blog/three-js-performance-optimization). This is weak evidence.
- Texture memory: a report gives under 96 MB on mobile, basis unverified — [fablepool.com](https://fablepool.com/artifacts/1464). A vendor blog claims 128 to 256 MB WebGL ceilings without a source, so it should not be relied on — [Style3D](https://www.style3d.com/blog/?p=17748)
- Triangle counts in blogs range from under 100K to a couple of million for mid-range hardware, which is too wide to use — [skill registry](https://openskillindex.com/skills/majiayu000-claude-skill-registry-dev-performance-mobile-optimization); [hontran.dev](https://www.hontran.dev/blog/three-js-performance-optimization)
- A forum report calls 210 draw calls and 41 textures too heavy for Android-heavy use — [three.js forum](https://discourse.threejs.org/t/webgl-performance-in-all-devices/22234)

### Inferences
**Working budget for this site (judgment, not a sourced standard):**
- Body: 48k triangles or fewer, and watch vertices too (aim for under about 40k).
- Draw calls: 1 per candle body plus 1 or 2 for flame and wick. Keep the page under about 30, well inside the blog figures.
- Textures: under about 30 MB GPU per page, which is a conservative choice given the 96 MB figure above is unverified.
- Pixel ratio: cap at 1.5 to 2, since per-pixel cost is what wax shading adds.

**Arm check:** if a candle covers about 400k physical pixels and 24k of its 48k triangles face the camera, that is about 17 fragments per triangle, which passes Arm's guide. 100k triangles would give about 8 and fail. This is a useful argument against going higher, even though 100k would not be a hard limit.

**Pixel cost is the likely limit here,** not vertices, since the wax shader runs on every covered pixel.

### Gaps
- No primary 2025-2026 per-device benchmark for mid-range Android WebGL was found, and most of what turned up is vendor blogs.
- Share of current mid-range phones supporting ASTC, which decides what UASTC transcodes to, was not checked.

## Wax shading in three.js: what works without transmission, how to bake thickness, and are there real examples?

### Takeaway
Do not use `transmission`, which costs an extra full-resolution pass and only shows what is behind the object. Instead, use `MeshStandardMaterial` with a Barré-Brisebois translucency term and a distance-based emissive glow, both added with `onBeforeCompile` and driven by a baked thickness value. The site already has most of this plumbing through the `aAT` attribute.

### Cited Findings
**Transmission and sheen**
- `MeshPhysicalMaterial` has a higher per-pixel cost than other materials, and effects add cost as they are enabled — [three.js docs](https://threejs.org/docs/pages/MeshPhysicalMaterial.html)
- `thicknessMap` is read from the green channel, is a real thickness value, and works with attenuation colour and distance. Sheen is described as useful for cloth and fabric — [three.js docs](https://threejs.org/docs/pages/MeshPhysicalMaterial.html)
- In a maintainer's test of the r150 rework, a Pixel 4a dropped from 24 to 20 fps, with 7 extra texture reads in the shader noted as a possible cost on weak GPUs — [three.js PR 25483](https://github.com/mrdoob/three.js/pull/25483). This is a 2023 result on an older phone.
- In the vendored r160 build, the transmission render target is sized to the full drawing buffer on WebGL2, and no `transmissionResolutionScale` exists (`three.module.js` around lines 29835 and 29858, checked locally)
- Some Android devices have had transmission materials invisible or crashing — [three.js forum](https://discourse.threejs.org/t/transmission-of-meshphysicalmaterial-doesnt-work-on-some-android-devices/28836)

**Translucency model**
- The GDC 2011 talk by Barré-Brisebois is the base of this fake — [Frostbite](https://frostbite.com/frostbite/news/approximating-translucency-for-a-fast-cheap-and-convincing-subsurface-scattering-look)
- three.js r160's implementation is in `SubsurfaceScatteringShader.js`, and it can be adapted line for line:
  ```glsl
  vec3 thickness = thicknessColor * texture2D(thicknessMap, uv).r;
  vec3 scatteringHalf = normalize(directLight.direction + (geometryNormal * thicknessDistortion));
  float scatteringDot = pow(saturate(dot(geometryViewDir, -scatteringHalf)), thicknessPower) * thicknessScale;
  vec3 scatteringIllu = (scatteringDot + thicknessAmbient) * thickness;
  reflectedLight.directDiffuse += scatteringIllu * thicknessAttenuation * directLight.color;
  ```
  Defaults: distortion 0.1, ambient 0.0, attenuation 0.1, power 2.0, scale 10.0 — [SubsurfaceScatteringShader.js r160](https://raw.githubusercontent.com/mrdoob/three.js/r160/examples/jsm/shaders/SubsurfaceScatteringShader.js)
- **Naming trap:** in this shader, a higher "thickness" value means more light through, so it behaves as thinness, which is the opposite of physical `thicknessMap`. A three.js forum thread shows users confused by this and left unresolved — [three.js forum](https://discourse.threejs.org/t/subsurface-scattering-with-gltf-model/23629)
- A 2023 paper uses 1/(thickness + 0.05), distortion 0.08, power 16 as a variation on this model. These constants are that author's own — [MARF paper](https://arxiv.org/pdf/2307.00037)
- Stride's documentation describes a greyscale map where brighter means more scatter — [Stride docs](https://doc.stride3d.net/4.0/jp/Manual/graphics/materials/subsurface-scattering.html)

**Baking thickness**
- Blender's Ambient Occlusion node has an `Inside` option described as computing occlusion inside the mesh, plus `Samples`, `Distance`, and Cycles-only `Only Local` — [Blender manual](https://docs.blender.org/manual/en/latest/render/shader_nodes/input/ao.html)
- A common method is flipping normals, baking AO and inverting. xNormal calls its version "Translucency" — [GameDev.net](https://gamedev.net/forums/topic/653094-baking-a-local-thickness-map/5129309/)
- PyMeshLab's `compute_scalar_by_shape_diameter_function_per_vertex` shoots rays inward to find mesh thickness, and takes ray count and cone amplitude. There is also a GPU variant — [PyMeshLab filter list](https://pymeshlab.readthedocs.io/en/latest/filter_list.html)
- `compute_scalar_ambient_occlusion` (64 rays by default, using Embree) gives AO — [PyMeshLab filter list](https://pymeshlab.readthedocs.io/en/latest/filter_list.html)
- A Blender bake target may be a Color Attribute, so vertex baking works directly — [Blender manual](https://docs.blender.org/manual/en/latest/render/cycles/baking.html)

**Real candle examples** (not run or read in full; descriptions come from their pages)
- Pillar Candle: React Three Fiber, wax glowing from inside near the flame, a melt pool that widens, drips, layered flame shader. It is the closest match — [kennyL1692/candle-html](https://github.com/kennyL1692/candle-html)
- The Lonely Candle: plain three.js, `ShaderMaterial` flame, no melting. Good reference for the flame — [CodePen](https://codepen.io/prisoner849/pen/XPVGLp); [three.js forum](https://discourse.threejs.org/t/the-lonely-candle/4097)
- SmokeGL: particle-based WebGL flame and smoke — [GitHub](https://github.com/LucaAngioloni/SmokeGL)
- A Houdini breakdown drives wax roughness from temperature so that wax near the flame looks more liquid, which is not WebGL but transfers well — [The Rookies](https://www.therookies.co/entries/21455)
- An Unreal thread suggests a gradient mask so that the top of the candle glows more than the bottom — [Unreal forum](https://answers.unrealengine.com/questions/132722/view.html?sort=votes)
- No three.js example was found that combines a generated mesh, thickness bake and wax shader.

**Site context (read locally)**
- `candle-builder.js` line 199 and lines 212 to 219 already use `aAT` (shut-in-ness and thinness) with `totalEmissiveRadiance *= mix(1.0, vAT.x, uAO) * (1.0 + uThin * vAT.y)`.
- `candle-builder.js` line 438 sets `emissiveMap = map` on loaded models, so any light baked into the texture also glows.

### Inferences
**Shader recipe for r160 (not run or compiled; every constant needs tuning by eye against the photo).** Layers, cheapest first:

1. **Base:** `MeshStandardMaterial`, roughness about 0.5, no metalness, and a weak warm environment so unlit wax does not go black. Physical adds cost without a useful wax feature.
2. **Glow by distance.** Red light travels further through wax than blue, so absorb per channel. This is the main "lit" cue and is cheap.
3. **Translucency:** the term above, using `aAT.y` in place of the texture.
4. **Melt pool:** lower roughness near the flame, using the same distance.

```js
mat.onBeforeCompile = (sh) => {
  Object.assign(sh.uniforms, {
    uFlame: { value: new THREE.Vector3() },   // object space, set once from the wick tip
    uLit:   { value: 1 },                     // flicker x on/off, updated per frame
    uAbs:   { value: new THREE.Vector3(2.0, 5.0, 12.0) }, // per-channel absorption, per candle height
    uGlow:  { value: new THREE.Color(1.0, 0.55, 0.22) },
  });
  sh.vertexShader = sh.vertexShader
    .replace('#include <common>', `#include <common>
attribute vec2 aWax; varying vec2 vWax; varying vec3 vObj;`) // aWax.x = AO, aWax.y = thinness
    .replace('#include <begin_vertex>', `#include <begin_vertex>
vWax = aWax; vObj = position;`);
  sh.fragmentShader = sh.fragmentShader
    .replace('#include <common>', `#include <common>
uniform vec3 uFlame, uAbs, uGlow; uniform float uLit; varying vec2 vWax; varying vec3 vObj;`)
    .replace('#include <roughnessmap_fragment>', `#include <roughnessmap_fragment>
float flameD = distance(vObj, uFlame);
roughnessFactor = mix(roughnessFactor, 0.12, smoothstep(0.18, 0.04, flameD) * uLit);`)
    .replace('#include <lights_fragment_end>', `#include <lights_fragment_end>
#if NUM_POINT_LIGHTS > 0
{ // Assumes point light 0 is the flame
  vec3 L = normalize(pointLights[0].position - geometryPosition);
  vec3 H = normalize(L + geometryNormal * 0.1);
  float s = pow(saturate(dot(geometryViewDir, -H)), 2.0) * 10.0;
  reflectedLight.directDiffuse += s * vWax.y * 0.1 * pointLights[0].color * diffuseColor.rgb;
}
#endif`)
    .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
vec3 through = exp(-flameD * uAbs);
totalEmissiveRadiance += uGlow * through * mix(0.35, 1.0, vWax.y) * vWax.x * uLit;`);
};
```
Points to check: `flameD` is declared at `roughnessmap_fragment`, and `emissivemap_fragment` comes after it in the standard fragment shader, but confirm the chunk order in r160's `meshphysical.glsl.js`. A point-light uniform also has to exist or the `#if` drops that term. `uAbs` values are guesses, with candle height scaled to 1.

**Why the top glows:** a candle's bright rim comes from flame light entering the thin, melted top. So the distance term plus thinness does most of the visual work, and the view-dependent term adds only a little when looking toward the flame. If phone performance is tight, drop the translucency block first.

**Thickness on vertices, not textures.** Thickness and AO vary slowly, and 48k vertices are more than enough. Storing two bytes per vertex avoids another sampler, and it matches the site's `aAT` approach. Bake them after decimation so they attach to final vertices.

**Thickness bake options, ranked for this project:**
1. PyMeshLab SDF, per vertex, no UVs needed, simple script. Then normalize: `thin = 1 - clamp(sdf / (0.25 * diameter), 0, 1)`.
2. Blender AO node with `Inside` plumbed to Emission, `bake(type='EMIT', target='VERTEX_COLORS')`.
3. The existing `tools/bake-blob.mjs` if it can accept an arbitrary mesh, which was not checked.

Glb attribute names: three's GLTFLoader keeps custom attributes such as `_WAX`, lowercased as `_wax`, which would then need mapping to `aWax`. Alternatively use `COLOR_0` and read it in the shader as `color`. Confirm that compression keeps the custom attribute.

**Sheen:** skip it. The docs frame it for cloth, and it costs per pixel. Wax's soft edge is better faked by a slight fresnel in the emissive if needed.

### Gaps
- No performance measurement on a phone was made for any of these approaches.
- The original GDC slides were not retrieved, so the formula comes via three.js's implementation.
- The candle examples above were not opened or run, so their quality has not been judged here.

## Delighting: how to remove the photo's light from a generated texture, with free tools?

### Takeaway
Delight the source photo before generation, since these tools work on images and not on UV atlases. Marigold IID Lighting is the most directly useful free model. For wax, which is close to one colour, a simple non-ML approach may do as well: keep the real colour, discard low-frequency brightness. Test both before committing.

### Cited Findings
- **Marigold IID Lighting v1.1** (15 May 2025) decomposes an image as I = A*S + R: albedo, diffuse shading and a non-diffuse residual. The weights use the CreativeML Open RAIL++-M licence, and an Appearance variant estimates albedo, roughness and metallicity. It is available through diffusers — [model card](https://huggingface.co/prs-eth/marigold-iid-lighting-v1-1); [Marigold GitHub](https://github.com/prs-eth/marigold); [diffusers docs](https://huggingface.co/docs/diffusers/main/using-diffusers/marigold_usage)
- **Hunyuan3D delight** (`hunyuan3d-delight-v2-0`) is an InstructPix2Pix-style model run on the input image before shape generation — [model files](https://huggingface.co/tencent/Hunyuan3D-2/commits/d852d887db59f3ece58124f0572a51dc0a04b4ea/hunyuan3d-delight-v2-0); [pipeline code](https://huggingface.co/spaces/endlesstools/apiHunyuan3d/blame/main/hy3dgen/texgen/pipelines.py). It also runs in ComfyUI — [ComfyUI wiki](https://comfyui-wiki.com/en/tutorial/advanced/3d/huanyuan3d-2)
- **Hunyuan licence:** Territory excludes the EU, UK and South Korea, and over 1 million monthly users needs a separate licence — [Hunyuan3D-2 LICENSE](https://huggingface.co/tencent/Hunyuan3D-2/blob/main/LICENSE)
- **StableDelight** targets specular reflection removal, per its page, which does not cover diffuse shading. It shows an Apache 2.0 badge and has a script for texture source images. Hardware needs are not stated — [Stable-X/StableDelight](https://github.com/Stable-X/StableDelight)
- **Unity De-Lighting Tool** (2017, experimental, old) works from AO, normal and bent normal maps with no chrome ball, and is aimed at photogrammetry — [Unity blog](https://blog.unity.com/en/technology/experimental-feature-de-lighting-tool); [CG Channel](https://www.cgchannel.com/2017/07/download-unity-labs-free-texture-de-lighting-tool/)
- **FlashTex** separates lighting while generating a texture from a text prompt, so it would replace the texture, not fix it. Its authors admit baked lighting remains in some cases — [Roblox/FlashTex](https://github.com/Roblox/FlashTex)
- **Commercial:** Meshy has a Remove Lighting option in AI Texturing, and Neural4D advertises the same. Pricing was not checked — [Meshy docs](https://docs.meshy.ai/en/webapp/guides/3d-model/ai-texturing); [Neural4D](https://www.neural4d.com/how-tos/how-to-solve-baked-shadows-and-lighting-issues)

### Inferences
**Why this matters more on this site:** `candle-builder.js` line 438 uses the colour map as the emissive map on models, so any baked highlight or shadow will glow.

**Suggested order:**
1. **Prevent it.** Photograph or choose photos under soft, even light. Delight the photo with Marigold before generating. This removes the problem at the source and sidesteps atlas seams.
2. **Fix after generating, for wax:**
   - On base colour in UV space, compute luminance Y, blur with a large radius, then `albedo = color * (mean(Y) / blurred(Y))`.
   - Blurring across an atlas leaks across chart seams, so do this per vertex on the high-poly, or use a Blender bake with fresh, continuous UVs.
   - This removes large-scale directional light and keeps fine colour. It will not remove sharp specular spots, which need clamping or StableDelight.
3. **Better, with normals available:** fit brightness against the high-poly's world-space normals (low-order spherical harmonics, 9 coefficients), and divide out the fit. This removes the part of the shading that correlates with surface direction, while bump shadows go to the normal map's job. It is a known idea in general but no ready tool or source was found for it.
4. **Last resort for wax:** use a flat base colour with a little low-frequency tint taken from the photo, and let the baked normal map carry all detail.

**Licence check:** whether the Hunyuan Territory terms fit depends on where the site's operator and users are, and a small business site is far below the user limit. Read the licence before commercial use. For Marigold, read RAIL++-M use restrictions.

**CPU only?** The diffusion-based tools likely need a GPU to be practical. This machine has an NVIDIA GPU path listed, but the card and VRAM were not checked.

### Gaps
- No dedicated, maintained, free tool for delighting a generated mesh's UV atlas was found.
- None of these models was run on a candle photo, and waxy translucent surfaces may decompose poorly because such models are not built for subsurface scattering. That is a real risk and needs a test.
- Marigold's 2025 IID code licence: the repo noted Apache 2.0 in 2023, but that note predates IID. The weights are RAIL++-M.

## Fixing generated meshes: floaters, holes, flat bases, and placing a wick and flame by script

### Takeaway
PyMeshLab handles floaters and small holes, trimesh slices a flat base, and a downward ray places the wick. Keep the wick and flame as separate objects from the body. All of it can be scripted on Windows with pip wheels, but none of it was run here.

### Cited Findings
**PyMeshLab** ([filter list](https://pymeshlab.readthedocs.io/en/latest/filter_list.html))
- `meshing_remove_connected_component_by_diameter(mincomponentdiag=10%, removeunref=True)` deletes small floating pieces.
- `meshing_remove_connected_component_by_face_number(mincomponentsize=25, removeunref=True)`.
- `meshing_close_holes(maxholesize=30, selected=False, newfaceselected=True, selfintersection=True, refinehole=False, refineholeedgelen=3%)`, where size is the number of boundary edges.
- Also listed: `meshing_repair_non_manifold_edges`, `meshing_repair_non_manifold_vertices`, `meshing_remove_duplicate_faces`, `meshing_remove_duplicate_vertices`, `meshing_remove_null_faces`, `meshing_re_orient_faces_coherently`.

**Other tools**
- meshoptimizer's `SimplifyPrune` removes isolated components and is recommended for full-mesh simplification — [meshoptimizer README](https://raw.githubusercontent.com/zeux/meshoptimizer/master/README.md)
- PyMeshFix wraps MeshFix, targets a single closed solid and removes singularities, self-intersections and degenerate elements. It is GPL-3.0 with commercial licensing separate. API: `pymeshfix.clean_from_arrays(v, f)` — [pyvista/pymeshfix](https://github.com/pyvista/pymeshfix)
- Blender's voxel remesh creates a new manifold mesh and loses all data layers — [bpy.ops.object API](https://docs.blender.org/api/current/bpy.ops.object.html)
- `trimesh.intersections.slice_mesh_plane(mesh, plane_normal, plane_origin, face_index=None, cap=False, engine=None)` returns the part on the positive normal side, and `cap` triangulates the cut — [trimesh docs](https://trimesh.org/trimesh.intersections.html). trimesh 5.2.0 was published 24 Oct 2026 — [PyPI](https://pypi.org/project/trimesh/)

### Inferences
**Default thresholds need raising for generated meshes.** The 10% diameter default may delete real parts such as a separate wick. A base hole on a generated mesh is often much longer than the 30-edge default.

**Script (not run):**
```python
import pymeshlab as ml, trimesh, numpy as np
ms = ml.MeshSet(); ms.load_new_mesh('raw.glb')   # if GLB fails on textures, export OBJ or PLY first
ms.meshing_remove_duplicate_vertices(); ms.meshing_remove_duplicate_faces(); ms.meshing_remove_null_faces()
ms.meshing_remove_connected_component_by_diameter(mincomponentdiag=ml.PercentageValue(5))
ms.meshing_repair_non_manifold_edges(); ms.meshing_repair_non_manifold_vertices()
ms.meshing_close_holes(maxholesize=200, refinehole=True)
ms.meshing_re_orient_faces_coherently()
ms.save_current_mesh('clean.ply')

m = trimesh.load('clean.ply', force='mesh')
# Stand it up: candle axis = longest principal axis
vals, vecs = np.linalg.eigh(np.cov((m.vertices - m.centroid).T))
axis = vecs[:, np.argmax(vals)]
axis = axis if axis @ [0, 1, 0] > 0 else -axis
m.apply_transform(trimesh.geometry.align_vectors(axis, [0, 1, 0]))
# Flat base: cut off the lowest 2% and cap it
y0 = m.bounds[0][1]; h = m.bounds[1][1] - y0
m = m.slice_plane([0, y0 + 0.02 * h, 0], [0, 1, 0], cap=True)
m.apply_translation([0, -m.bounds[0][1], 0])
# Wick: use the centre of the top region, ray down to find the wax surface
top = m.vertices[m.vertices[:, 1] > m.bounds[1][1] - 0.15 * h]
cx, cz = np.median(top[:, 0]), np.median(top[:, 2])
hits, _, _ = m.ray.intersects_location([[cx, m.bounds[1][1] + 1, cz]], [[0, -1, 0]])
wick_base = hits[np.argmax(hits[:, 1])]
```
Notes on this script:
- The longest-axis test fails on squat candles, where the axis is ambiguous. For those, use the photo's known up direction or confirm by eye.
- From memory, trimesh's `cap=True` needs a watertight mesh, so run repair first. If it refuses, seal with voxel remesh or PyMeshFix, or cap with Blender's bisect tool. Confirm this behaviour.
- For a figurine candle (the site has puppy and blob shapes), the median of the top region may not be where a wick belongs, so read it from a small recipe value in `recipes/` instead.

**Runtime placement:** store `wick_base` in the recipe or a GLB node extras, and reuse the existing flame and wick from `candle-builder.js`, so the generated body only needs an anchor point. That also supplies `uFlame` for the shader. A three.js `Raycaster` could do this at load time, but raycasting 48k triangles without an index slows startup, so bake it.

**Order matters:** repair and cut on the high-poly before decimating and baking, so the bake sees the final shape.

**Remove a generated wick.** A photo-derived mesh often has a blobby wick or flame merged into the top. Cut it off with a plane or sphere selection at the top before adding the real one. This is expected to need per-candle tuning, and no automatic method was found.

### Gaps
- Generated meshes vary by tool, and no data was found on how often each problem occurs.
- PyMeshLab's GLB import was not verified on this machine (it is not installed). Convert with trimesh if needed.
- No source was found for an automatic way to remove a merged flame or wick from a generated mesh.
