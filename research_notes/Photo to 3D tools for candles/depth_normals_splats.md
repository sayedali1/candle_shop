# Monocular depth, normals and phone Gaussian splats for one-photo candles (as of 1 Nov 2026)

Reading note: nearly all quality claims below come from the model authors' own papers and READMEs. I found no independent test on small objects, fur or wax, and I did not run any model on the client's photo. Licence lines are readings of repo and model-card text, not legal advice.

## Which depth model gives the finest detail on small objects and fur?

### Takeaway
Try MoGe-3 first: it is the newest model aimed specifically at fine geometry, it gives real metric geometry plus normals, and both code and weights are tagged MIT. Marigold V2 is the most interesting challenger on fur, but I could not confirm that its weights are available or how they are licensed. Depth Anything V2 Small was close to the weakest choice for this job, so the soft face in the earlier test does not show that the whole approach fails.

### Cited Findings

Comparison table. Speed barely matters because maps are baked offline. Only the finished map reaches the phone.

| Model | Date | Geometry | Detail evidence (self-reported) | Speed | Licence | Client use? |
|---|---|---|---|---|---|---|
| MoGe-3 (`moge-3-vitl` 370M, `moge-3-vitg` 1.25B) | Aug 2026 | Metric point map, depth, intrinsics, normals | "significantly improved fine-grained point map geometry"; sparse refinement, 3 steps by default. No numbers on the page | Not stated for v3. README's 60 ms is for ViT-L on A100/RTX3090, version unclear | Code MIT (DINOv2 part Apache 2.0); weights tagged MIT | Yes, on these tags |
| MoGe-2 (ViT-S/B/L) | Jul 2025 | Metric point map, normals in `-normal` variants | Boundary sharpness comparable to Depth Pro, with better overall geometry | As above | Code MIT; `moge-2-vitl-normal` tagged MIT | Yes |
| Marigold V2 | Sep 2026, SIGGRAPH Asia | Depth; authors also claim state of the art on normals | Claims to resolve "fur, foliage, and hair-thin edges" (qualitative) and 16-26% better AbsRel on KITTI and ETH3D | Single-step; no figures | Paper CC BY-SA 4.0; code and weights licence not found | Unknown: confirm first |
| Pixel-Perfect Depth | NeurIPS 2025 | Relative depth; metric and intrinsics via MoGe-2 | Diffuses in pixel space to avoid VAE-caused flying pixels; trained at 1024x768 | No figures | Code Apache 2.0; weights not stated. Needs DA2 ViT-L (CC BY-NC) or MoGe-2 for semantics | Only with the MoGe-2 checkpoint, and confirm `ppd.pth` terms |
| Depth Anything 3 Mono-Large / Metric-Large | Nov 2025 | Relative depth / metric depth | No fine-detail comparison found | Not checked | Apache 2.0 for these two, and for Small and Base. Giant, Large and Nested are CC BY-NC 4.0 | Yes for the Apache variants |
| Depth Anything V2 | 2024 | Relative disparity | Default input 518; "You can increase the size for even more fine-grained results" | Fast | Small Apache 2.0; Base, Large and Giant CC BY-NC 4.0 | Small only |
| Depth Pro (Apple) | ICLR 2025 | Metric depth | Built for sharpness; authors report much better boundary accuracy and far faster than Marigold and PatchFusion | Under a second | "personal, non-exclusive license"; no commercial ban in the text; no separate weight terms found | Probably; read the full text |
| Lotus-2 | c. 2025 | Depth and normals | Claims sharp geometric detail | No figures; needs a GPU with at least 40 GB | Code Apache 2.0; weights not stated; requires access to FLUX.1-dev | Doubtful (see Gaps) |
| Metric3D v2 | Older | Metric depth; normals on ViT models | Accuracy tables only | No figures | Code BSD-2; weights not stated; README directs "further commercial inquiries" to the author | Ask the authors |
| UniDepthV2 | Feb 2025 | Metric depth | Not assessed | "Faster" than V1 | "Creatives Common BY-NC 4.0" | No |
| GeoWizard | V2 Apr 2024, older | Depth and normals | Not assessed | Defaults: 3 ensembles, 10 steps | CC BY 4.0 | Yes, with attribution; older |

Sources:
- MoGe-3 release, checkpoints, refinement and normals — [MoGe README](https://raw.githubusercontent.com/microsoft/MoGe/main/README.md); weights tag MIT — [moge-3-vitl](https://huggingface.co/Ruicheng/moge-3-vitl)
- MoGe-2 variants and code licence — [MoGe repo](https://github.com/microsoft/MoGe); weights tag MIT — [moge-2-vitl-normal](https://huggingface.co/Ruicheng/moge-2-vitl-normal); sharpness comparison — [MoGe-2 paper](https://arxiv.org/html/2507.02546v1)
- MoGe-3 depends on FlexGEMM and does not support macOS, and the uv setup pins a CUDA wheel index, so plan on an NVIDIA GPU machine — [MoGe README](https://raw.githubusercontent.com/microsoft/MoGe/main/README.md)
- Marigold V2 claims — [arXiv 2609.08084](https://arxiv.org/abs/2609.08084); the demo Space exists, but the fetched page showed no terms — [marigold-v2-web](https://huggingface.co/spaces/huawei-bayerlab/marigold-v2-web)
- Pixel-Perfect Depth flying-pixel explanation — [arXiv 2510.07316](https://arxiv.org/abs/2510.07316v1); code licence, checkpoints and resolution — [repo](https://github.com/gangweix/pixel-perfect-depth)
- DA3 licence per variant, including the note that -1.1 retrained models are preferred — [DA3 repo](https://github.com/ByteDance-Seed/Depth-Anything-3). Third-party pages disagree on DA3 licensing ([Voxel51](https://docs.voxel51.com/model_zoo/models/depth_anything_v3_small_torch.html) lists Small as CC BY-NC); the official repo says Apache 2.0, and I follow that.
- DA2 licences and input-size note — [DA2 repo](https://github.com/DepthAnything/Depth-Anything-V2)
- Depth Pro claims — [paper](https://arxiv.org/abs/2410.02073); licence text — [LICENSE](https://github.com/apple/ml-depth-pro/blob/main/LICENSE); acknowledgements list only timm and DINOv2 — [ACKNOWLEDGEMENTS](https://raw.githubusercontent.com/apple/ml-depth-pro/main/ACKNOWLEDGEMENTS.md)
- Lotus-2 — [repo](https://github.com/EnVision-Research/Lotus-2); Metric3D — [repo](https://github.com/YvanYin/Metric3D); UniDepth — [repo](https://github.com/lpiccinelli-eth/UniDepth); GeoWizard — [repo](https://github.com/fuxiao0719/GeoWizard)

### Inferences
- Why the earlier test was soft: DA2 Small is the smallest DA2 model (24.8M parameters) and defaults to 518 px input. A figure's face on a small candle may cover few of those pixels. Also, DA2 was never designed for the fine-detail goal that MoGe-3 and Marigold V2 target.
- What would do better, in test order:
  1. MoGe-3 ViT-L, on a tight crop of the candle so the face fills more input pixels.
  2. The same crop through DA2 Small at a raised `--input-size`, as a cheap control. It shows how much of the softness came from resolution.
  3. Marigold V2, if weights and terms check out.
  4. Pixel-Perfect Depth with the MoGe-2 checkpoint, if `ppd.pth` terms check out.
- Only MoGe-2, MoGe-3, Depth Pro, Metric3D, UniDepth and DA3 Metric give metric or camera-aware geometry. For a candle, absolute scale is not important, but camera intrinsics help when projecting the photo back onto a mesh.
- Fine-detail and sharp-boundary claims are mostly about object edges and thin structures. A curl pressed into wax is low-contrast relief inside the object, so these claims may not carry over. It must be tested on the actual photo.

### Gaps
- No independent benchmark on small objects, fur or wax-like surfaces. All detail rankings are author claims.
- Marigold V2 weights and licence not confirmed. The [Marigold repo](https://github.com/prs-eth/Marigold) did not mention V2 when fetched.
- Lotus-2's weight licence is not stated. From background knowledge FLUX.1-dev carries a non-commercial licence, but I did not verify this in this research. Treat Lotus-2 as blocked until checked.
- No results were run on the client's photo; the photo was not part of this assignment.

## Which normal estimator keeps fine relief such as curls, and can it be used as a real normal map?

### Takeaway
Published averages place the main models within a few degrees of each other, and none of them measures curl-level relief, so the choice has to be made by eye on the photo. For client use, test MoGe-3 normals and StableNormal. Marigold is a third option if RAIL++-M terms are acceptable. DSINE is ruled out. The output is usable as a normal map only in a limited sense, because it is correct only from the photo's angle and needs converting first.

### Cited Findings
- Accuracy across DSINE, StableNormal, Lotus-2 and Marigold is within a few degrees and depends on dataset — [Vision Banana paper](https://arxiv.org/pdf/2604.20329); similar closeness in — [Marigold V2 paper](https://arxiv.org/pdf/2609.08084)
- StableNormal targets sharpness by reducing diffusion variance with a two-stage coarse-to-fine design — [paper](https://arxiv.org/pdf/2406.16864). Mean error on DIODE-indoor is 13.701 for the full model and 16.748 for turbo. Turbo is about 10x faster and scored better on ScanNet (17.432 vs 18.098) — [repo](https://github.com/Stable-X/StableNormal)
- StableNormal licence: listed Apache-2.0, with no separate weight statement on the repo page — [repo](https://github.com/Stable-X/StableNormal)
- MoGe-3 normals are in OpenCV camera coordinates, and both checkpoints support them — [MoGe README](https://raw.githubusercontent.com/microsoft/MoGe/main/README.md)
- Marigold v1.1 normals (May 2025): code Apache 2.0, models under "RAIL++-M License" — [Marigold repo](https://github.com/prs-eth/Marigold). The same release includes intrinsic decomposition models for appearance and lighting.
- Lotus (v1): normal models in generation and regression modes; code Apache-2.0; weight licence not stated — [Lotus repo](https://github.com/EnVision-Research/Lotus)
- DSINE: "You may not use the Software for commercial purposes"; commercial use requires written permission from Imperial College — [LICENSE](https://raw.githubusercontent.com/baegwangbin/DSINE/main/LICENSE)
- One benchmark puts DSINE at about 59 ms and Marigold at about 260 ms per image, and found StableNormal and Lotus good on accuracy against speed — [DiMeR paper](https://arxiv.org/pdf/2504.17670)
- Vision Banana's authors show finer granular normal detail than Lotus-2, in their own visual comparison — [arXiv 2604.20329](https://arxiv.org/pdf/2604.20329)

### Inferences
- These are camera-space normals. To use one on a mesh, either bake it into tangent space for that mesh's UVs, or treat it as an object-space map that holds only while the object's pose matches the photo. This is my reasoning, not a sourced result.
- Keep the low-frequency shape from the mesh and use only the high-pass of the predicted normal for relief. Otherwise the predicted large-scale form fights the hand-built form. Also my reasoning.
- Marigold's lighting and appearance models may help remove the shading baked into the photo before it is used as a colour texture, which matters for flame relighting. Not tested for this use.

### Gaps
- No published metric or test for preserving small embossed relief. Average angular error on room and street datasets says little about it.
- RAIL++-M terms were not read. From background knowledge it allows commercial use with use-based restrictions, but confirm this from [LICENSE-MODEL](https://github.com/prs-eth/Marigold).
- StableNormal and Lotus weight terms on their model cards were not checked.

## Can a single-photo normal or depth map add surface detail to a low-poly three.js mesh, and how does it hold up when turned?

### Takeaway
Yes for surface detail near the photo's angle, but it cannot rescue the figure's shape. A map adds lighting and relief on the surfaces the photo saw. It adds nothing about the back and sides, and it does not change the silhouette. Best fit: a mostly front-facing page with limited rotation. I found no measured limit for how far it can turn; that needs a test.

### Cited Findings
- A normal map is cheap and adds no vertices, while displacement gives real depth but looks blocky on low-poly meshes unless segments or LOD are added — [DEV guide](https://dev.to/peterridingdev/normal-maps-vs-displacement-maps-in-threejs-what-beginners-get-wrong-3nnk) (beginner-level source)
- A 2026 Codrops tutorial relights a flat image in three.js: normals derived from a depth map, shadows traced through depth samples, the photo as diffuse colour, using TSL and WebGPU. It notes that 8-bit depth shows steps, so it converts to float and blurs first. I saw this only through the search summary, as the page returned 403 — [Codrops](https://tympanus.net/codrops/2026/08/19/relighting-images-with-depth-maps-and-three-js/)
- BiNI integrates normals into a surface while preserving discontinuities, with public code — [ECCV 2022 paper](https://www.ecva.net/papers/eccv_2022/papers_ECCV/html/3202_ECCV_2022_paper.php) (older)
- A 2024 method reports lower mean absolute depth error than BiNI and handles bas-relief inputs with subtle detail — [arXiv 2404.03138](https://arxiv.org/pdf/2404.03138)
- ECON's double-sided BiNI needed a silhouette consistency term; without it, front and back surfaces intersect and cause "blobby" artifacts. Too large a discontinuity parameter also shows artifacts — [ECON supplement context](https://arxiv.org/pdf/2212.07422)

### Inferences
These are my engineering reasoning, not sourced measurements.
- Three usable techniques, best first for this project:
  1. **Camera projection plus a baked relief map.** Line the hand-built mesh up with the photo, project the photo and the predicted normals onto its UVs, then blend to a plain wax material where surfaces face away from the camera. Rotation should be limited on the page.
  2. **Bas-relief from normal integration or depth.** Build a shallow height field for the front of the figure, then displace a dense patch only there. It gives real parallax at the cost of more vertices and shows sidewall stretching at steep angles.
  3. **Depth-relit photo plane.** Cheapest and most convincing for the original view, but it has no real rotation. Suits a hero image with flame lighting more than a turning object.
- What goes wrong as it turns: projected colour stretches on surfaces nearly parallel to the camera, hidden areas have no data, baked photo shading stays fixed while the object turns, and the unchanged low-poly silhouette exposes the fake. Fading normal strength and projected colour by facing angle hides some of this.
- Getting the hand-built mesh to line up with the photo is the hard part. A misaligned relief map looks worse than none, and predicted point maps can help with alignment.
- Baked-map cost on the phone is mainly one extra texture, so this should be much kinder to a Galaxy M32 than splats. Not measured.

### Gaps
- No source measures how many degrees of rotation a single-view map holds up for. Test at 0, 15, 30, 45 and 60 degrees on the real candle.
- Search returned no authoritative write-up on projective-texture stretching in three.js.
- The Codrops method uses WebGPU; whether it can be ported to WebGL2 at usable speed on the M32 is untested.

## Are Gaussian splats realistic for showing a candle on a phone page?

### Takeaway
File size and three.js integration are fine; the unknowns are frame rate on the M32 and flame lighting. TripoSplat is the only generator I found that is both recent and commercially licensed, capped at 262,144 Gaussians. Spark is the viewer to use. I found no measured frame rate on a browser on a mid-range Android phone, and the M32's GPU is much weaker than the phones in published numbers. Splats have baked lighting, so a moving flame needs a tint or proxy-mesh trick. Treat it as a one-day experiment on the M32, not a decision yet.

### Cited Findings

**Generators**

| Generator | Single photo? | Output | Licence | Client use? |
|---|---|---|---|---|
| TripoSplat (VAST AI, 2026) | Yes | "Arbitrary Gaussian count (up to 262,144)"; `.ply` or `.splat`; ComfyUI template said to export GLB, SPZ or video | "TripoSplat code and weight models are released under the MIT License" | Yes, but check components below |
| SHARP (Apple) | Yes | 3DGS `.ply`, "nearby views" only; under 1 s on GPU | Model: "does not include any commercial exploitation, product development or use in any commercial product or service" | **No** |
| LiTo (Apple, ICLR 2026) | Yes | Not assessed | Weights described as Apple research non-commercial | **No** |
| DA3 Nested/Giant (Gaussian head) | Multi-view oriented | Splats | CC BY-NC 4.0 | **No** |
| LGM | Yes | Gaussian count not stated; about 10 GB GPU memory | MIT on repo | Likely; older |
| Splatter Image | Yes | Count not stated; Objaverse model for "any object" | BSD-3-Clause | Likely; older |

Sources: TripoSplat — [repo](https://github.com/VAST-AI-Research/TripoSplat), [model card](https://huggingface.co/VAST-AI/TripoSplat), [ComfyUI docs](https://docs.comfy.org/tutorials/3d/triposplat.md), [Radiance Fields](https://radiancefields.com/comfyui-adds-native-3d-gaussian-splat-generation-with-triposplat). SHARP — [repo](https://github.com/apple/ml-sharp), [LICENSE_MODEL](https://raw.githubusercontent.com/apple/ml-sharp/main/LICENSE_MODEL). LiTo — [wrapper listing](https://awesome.ecosyste.ms/projects/github.com%2FPozzettiAndrea%2FComfyUI-LiTo). DA3 — [repo](https://github.com/ByteDance-Seed/Depth-Anything-3). LGM — [repo](https://github.com/3DTopia/LGM). Splatter Image — [repo](https://github.com/szymanowiczs/splatter-image).

- The TripoSplat model card names birefnet, DINO v3 and the FLUX.2 VAE as components without giving their licences — [model card](https://huggingface.co/VAST-AI/TripoSplat). The MIT statement may not settle those parts.
- The TripoSplat card links arXiv 2605.16355, "Generative 3D Gaussians with Learned Density Control", which claims "state-of-the-art quality in single-image-to-3D generation" with a sampling budget that controls decoding resolution — [arXiv](https://arxiv.org/abs/2605.16355)

**Viewers**
- Spark (World Labs): MIT; loads PLY, compressed PLY, SPZ, SPLAT, KSPLAT and SOG; "Integrates with THREE.js rendering pipeline to fuse splat and mesh-based objects"; correct sorting across splat objects; shader graph with colour editing, displacement and skeletal animation; WebGL2 — [repo](https://github.com/sparkjsdev/spark)
- Spark 2.0: LoD trees, `.RAD` streaming over HTTP Range, fixed splat budget per frame. Default budget is 500K on mobile — [LoD docs](https://sparkjs.dev/docs/new-spark-renderer/); "500K to 2.5M depending on device" — [2.0 features](https://sparkjs.dev/docs/new-features-2.0/). The LoD docs warn they may not be fully up to date. Use `lodSplatCount` to set the budget, and `antialias: false` for performance.
- GaussianSplats3D: MIT, but "no longer in active development", recommends Spark, lists "Sub-optimal performance on mobile devices", and works only with opaque depth-writing three.js objects — [repo](https://github.com/mkkellogg/GaussianSplats3D). Do not start a new project on it.
- three.js native renderer: `GaussianSplatMesh`, reported for r186 as WebGPU/TSL with GPU counting sort and PLY, SPZ, KSPLAT and glTF loaders; no LoD or chunked streaming, so cost scales with total splats — [Radiance Fields](https://radiancefields.com/three.js-merges-a-native-gaussian-splat-renderer-for-webgpu-in-r186), [CGWORLD](https://cgworld.jp/flashnews/01-202610-Threejs-r186.html). Sources disagree on whether it was in a tagged release; CGWORLD (Sept 2026) says r186 was published. I did not open the official release page. A forum author says WebGL2 fallback exists — [three.js forum](https://discourse.threejs.org/t/two-gunpla-scanned-as-3d-gaussian-splats-relit-inside-a-three-js-city/94407.md).
- SuperSplat and PlayCanvas: named as having reasonable mobile support if under 1 million splats, as a recommendation rather than a benchmark — [Polyvia3D guide](https://www.polyvia3d.com/guides/gaussian-splatting-web-viewer). PlayCanvas is its own engine rather than three.js.

**File size and compression**
- SOG: "typically yielding files ~15–20× smaller than an equivalent PLY"; lossless WebP channels; about 17 bytes per splat before image compression, by my count from the spec table — [SOG spec](https://developer.playcanvas.com/user-manual/gaussian-splatting/formats/sog.md)
- SPZ: about 90% smaller than PLY, roughly 25 MB vs 250 MB for a rich scene — [Niantic](https://scaniverse.com/news/spz-gaussian-splat-open-source-file-format); PlayCanvas puts it at about 10x — [formats](https://developer.playcanvas.com/user-manual/gaussian-splatting/formats/)
- A measured reference point: 3.878 MB for 256k splats (Bicycle scene) with SOG-XT, a research encoder better than official SOG, so official SOG will be larger — [KISS-GS](https://arxiv.org/pdf/2608.26948)

**Frame rate (no direct match exists)**

| Number | Device and renderer | Quality of evidence |
|---|---|---|
| 500k splats in 14 ms; 2M in 19 ms | Xiaomi Mi 9, Adreno 640, native Vulkan | Project's own, not browser — [SplatKit](https://github.com/Xget7/splatkit) |
| 116 fps at 1600x1063 | Snapdragon 8 Gen 3, native | Paper's own method, flagship chip — [Mobile-GS](https://arxiv.org/pdf/2603.11531) |
| About 20.41 falling to 18.5 fps, SH degree 0 to 3 | Device not named in retrieved text | Draft standards contribution — [3GPP S4-260168](https://www.3gpp.org/ftp/Meetings_3GPP_SYNC/SA4/Inbox/Drafts/Video/S4-260168_pcr_renderer_rev1.docx) |
| 1-2M splats at 30 fps on Snapdragon 7xx; 20-30 fps on older devices | Web, general | Unattributed estimate — [Utsubo guide](https://www.utsubo.com/blog/gaussian-splatting-guide) (attribution between guides is from search summaries; check before quoting) |
| 200-500K max, 30-45 fps target on mobile | Web, general | No method given; contradicts the 1-2M figure — [WHD Studio](https://thewhdstudio.com/articles/article-gaussian-splatting.html) (same caution) |

- Galaxy M32: Helio G80 with Mali-G52 MC2 per GSMArena and most listings; an early Geekbench report said Mali-G57 — [GSMArena](https://m.gsmarena.com/samsung_galaxy_m32-ampp-10887.php), [Gizchina](https://gizchina.newsifier.com/samsung/samsung-galaxy-m32-has-key-specs-revealed-by-geekbench)

**Relighting by a moving flame**
- PlayCanvas: lights a proxy mesh, renders that lighting to an offscreen texture, and modulates each splat fragment by screen position. It supports point lights; proxy quality is "the main factor"; a `blend` setting controls strength. No mobile figures — [PlayCanvas](https://developer.playcanvas.com/user-manual/gaussian-splatting/building/relighting/)
- three.js example: baked-light scans with a custom relight pass responding to fire glow; a convex hull from splat positions works as an invisible shadow caster. No counts or fps — [three.js forum](https://discourse.threejs.org/t/two-gunpla-scanned-as-3d-gaussian-splats-relit-inside-a-three-js-city/94407.md)
- Research: PRTGS reaches 30+ fps at 1080p with precomputation but targets low-frequency lighting and says high-quality dynamic-light shadows remain hard — [PRTGS](https://www.arxiv.org/pdf/2408.03538)

### Inferences
- File size is not the blocker. At the 262,144 cap, expect roughly 4-6 MB as SOG (extrapolated from the KISS-GS point; official SOG is larger). At 100k, around 2 MB. Measure on real output.
- Frame rate is the real risk. The M32 already sits at about 30 fps with the current scene, so there is no headroom. Its Mali-G52 MC2 is an entry-level configuration and much weaker than the Adreno 640 or Snapdragon 8 Gen 3 above, so those numbers do not carry over. A close-up candle also fills the screen with overlapping transparent splats, which costs GPU fill rate, so splat count alone will mislead. Lowering render resolution is the first lever.
- Spark's default 500K mobile budget exceeds TripoSplat's maximum, so the budget would not protect the M32. Set the count deliberately, and test at 50k, 100k and 262k.
- Use SH degree 0: single-image output has little real view-dependent data, and the higher orders cost size.
- Hidden-side quality is generated, not captured. A generator may invent the figure's back or simplify a face, which is a fidelity concern for a real client's product. Check its output against the photo before investing in it.
- Flame relight: a cheap radial tint by distance from the flame, flickering over time and written in Spark's shader graph, should look acceptable for warm glow. It is a colour multiply, not real relighting, so baked highlights and shadows stay. A proper result needs a proxy mesh and an extra lighting pass, which the M32 can least afford.
- Mixing: Spark can sit in the existing three.js scene. A transparent, additive flame near the splats is the ordering case most likely to need testing, since transparent objects are hard for the older viewer too.
- Verdict for the two objectives: depth and normals can improve the front-facing surface but cannot fix a poor shape. Splats are technically realistic in size and integration but unproven on the M32. A short-rotation splat test and a relief-map test on the same candle would decide this better than more reading. Ship a poster image fallback whichever way it goes.

### Gaps
- **No measured browser fps on any mid-range Android phone, and none on any Mali GPU**, for Spark, SuperSplat, PlayCanvas or three.js native. Needs a device test recording fps, splat count, resolution and `gl.RENDERER`.
- TripoSplat generation time, VRAM, and independent quality on candles or fur are not published on the pages read. Hidden-side behaviour was also not checked.
- Licences for TripoSplat's third-party components (birefnet, DINO v3, FLUX.2 VAE) are unverified, as is whether their terms reach generated output. Dates for the Radiance Fields article conflict (byline Jun 1, metadata Oct 31, 2026).
- Spark's "Splat budget recommendations" table and its current release number were not confirmed. The README's CDN example shows 2.4.0.
- WebGPU availability on the M32 was not checked, and it decides whether the three.js native renderer's main path is usable there.
- No source covers a moving-flame relight running on a phone.
