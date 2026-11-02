# Open-weight models for one photo to textured 3D (checked 2026-11-01)

Scope note for the writer: nobody has run these models on the candle photo. No source tests a poodle, a curled-fur sculpt or a wax object. All judgement about the candle is inference from general evidence and is labelled as such.

## Which open models would be most faithful for the poodle candle, and which run on the user's machine?

### Takeaway
Try TRELLIS.2 first through a Windows ComfyUI wrapper, then Pixal3D, and pick by eye. TRELLIS.2 has the best independent ranking among open models, and Pixal3D has the strongest authors' claim on likeness to the photo. The machine this research ran on has a 12 GB RTX 4070 Ti, so both are plausible at 1024 but tight at 1536, and neither is officially supported on it.

### Cited Findings
- This machine reports `NVIDIA GeForce RTX 4070 Ti, 12282 MiB`. Source: `nvidia-smi`, run locally on 2026-11-01. I assume this is the machine the user means.
- A crowd-vote leaderboard, run by Rapidata and covering 357 fixed images with 262,668 votes, gives these overall scores: Hi3D v3.0 1366, Meshy v7.1 1298, Meshy v7 1287, Tripo H3.1 1261, Hunyuan3D 3.1 Pro 1144, Seed3D 2.0 1097, TRELLIS.2 1005, Rodin Gen-2.5 High 956, Rodin Gen-2.5 Low 772, Pixal3D 754, Hunyuan3D 2.1 750, SAM 3D Objects 658 (95% intervals about ±17 to ±20) — [benchmark.ai](https://www.benchmark.ai/image-to-3d)
- TRELLIS.2-4B: paper dated December 16, 2025, MIT licence, NVIDIA GPU with at least 24 GB, tested only on Linux — [model card](https://huggingface.co/microsoft/TRELLIS.2-4B)
- Pixal3D: accepted to SIGGRAPH 2026, code and demo May 2026, multi-view code September 2026. The `main` branch uses the TRELLIS.2 backbone, and `--low_vram` defaults to resolution 1024 instead of 1536 — [repo](https://github.com/TencentARC/Pixal3D)
- Pixal3D's authors say it "substantially improves fidelity, approaching the fidelity level of reconstruction", by projecting image features into 3D in the input camera's view. The abstract gives no numbers — [arXiv 2605.10922](https://arxiv.org/abs/2605.10922)
- The latest open Hunyuan3D is 2.1, released June 13, 2025 (about 10 GB shape, 21 GB texture, 29 GB together) — [repo](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1)
- A hands-on test of one human portrait scored Hunyuan3D 4/4/4 and TRELLIS 2 3/2/3. It reported "numerous holes, broken hair strands" for TRELLIS 2, and simple hair and softer small facial features for Hunyuan3D — [Vitalify, July 2026](https://www.vitalify.asia/en/blog/ai-image-to-3d-generators-comparison). The article's scores do not say which Hunyuan3D version was used, so it may be a hosted 3.x.

### Inferences
- Suggested order to test on the real photo: TRELLIS.2 at 1024_cascade, Pixal3D at 1024_cascade, then Hunyuan3D 2.1 shape only.
- The leaderboard and the Vitalify test disagree on the order of TRELLIS.2 and Hunyuan3D. The leaderboard deserves more weight as a general signal because it covers 357 images rather than one. Neither predicts this specific subject.
- The candle is a hard case: one wax colour means the curls show only through soft shading, so the model gets less signal than from a coloured object. This reasoning is mine and no source tests it.
- Hosted commercial models take the top six places on the leaderboard. If open models fall short, that is the fallback, and it sits outside this note's scope.

### Gaps
- No test of any model on a monochrome sculpted object, wax or poodle.
- The leaderboard has a Fur-Hair-Foliage tag, but I could not retrieve a ranking filtered to it. It is worth opening by hand in a browser.

## Current state of each model, and the best on organic figures with fine relief

### Takeaway
The open frontier in late 2026 is TRELLIS.2 and its derivative Pixal3D, ahead of Hunyuan3D 2.1. Tencent's newer Hunyuan3D 3.x appears to be hosted only. Nothing found proves a winner for fine relief on organic figures.

### Cited Findings
| Model | Latest open release | Weights status |
|---|---|---|
| Hunyuan3D 2.0, mini, mv, turbo | Jan to Apr 2025 | Open — [repo](https://github.com/Tencent-Hunyuan/Hunyuan3D-2) |
| Hunyuan3D 2.1 | Jun 13, 2025 | Open — [repo](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1) |
| Hunyuan3D 2.5 | Technical report Jun 23, 2025 | I found only the report — [repo news](https://github.com/Tencent-Hunyuan/Hunyuan3D-2) |
| Hunyuan3D 3.0, 3.1 | 3.0 Sep 2025, 3.1 late Nov 2025 | Described as commercial, with 2.x as the open line — [WaveSpeed](https://wavespeed.ai/blog/posts/hunyuan-3d-api/) (secondary) |
| TRELLIS.2-4B | Paper Dec 2025 | Open — [model card](https://huggingface.co/microsoft/TRELLIS.2-4B) |
| Pixal3D | May 2026, multi-view Sep 2026 | Open — [repo](https://github.com/TencentARC/Pixal3D) |
| SAM 3D Objects | Nov 19, 2025, encoder weights Jun 2026 | Open, SAM License — [repo](https://github.com/facebookresearch/sam-3d-objects) |
| TripoSG | Mar 2025, scribble model Apr 2025 | Open — [repo](https://github.com/VAST-AI-Research/TripoSG) |
| Step1X-3D | May 13, 2025, multi-view May 27, 2025 | Open — [repo](https://github.com/stepfun-ai/Step1X-3D) |
| SPAR3D | Paper Jan 2025 (older) | Open, gated — [model card](https://huggingface.co/stabilityai/stable-point-aware-3d) |
| SF3D | Paper Aug 2024 (older) | Open, gated — [model card](https://huggingface.co/stabilityai/stable-fast-3d) |
| TripoSR | arXiv ID suggests Mar 2024 (older) | Open — [repo](https://github.com/VAST-AI-Research/TripoSR) |
| InstantMesh | arXiv ID suggests Apr 2024 (older) | Open — [repo](https://github.com/TencentARC/InstantMesh) |

- The same-repo news log for Hunyuan3D shows little activity since mid-2025, and one vendor blog says open repos have seen little activity since late 2025 — [triposr.org](https://triposr.org/blog/hunyuan3d-vs-trellis) (vendor, documentation review only)
- ComfyUI's native TRELLIS.2 integration merged August 22, 2026 and shipped in v0.34.0 on August 26, 2026 — [Hakky guide](https://book.st-hakky.com/en/data-science/trellis2-native-vs-legacy-vram-guide)
- The community wrapper keeps moving, with Pixal3D multi-view support added September 7 to 8, 2026 — [ComfyUI-Trellis2](https://github.com/visualbruno/ComfyUI-Trellis2)

### Inferences
- An earlier "3.5" mention could not be confirmed, so treat it as not real until a primary source appears.
- Pixal3D sitting well below TRELLIS.2 on the leaderboard, despite sharing a backbone, suggests its likeness gain may not read as better overall quality to voters. That leaderboard row may reflect either branch, so this is tentative.

### Gaps
- I found no official Tencent statement that 3.x weights will never be released. "Hosted only" rests on no weights being found plus secondary sources.
- The Reddit thread said to claim TRELLIS.2 is "already getting dethroned" was reported only second-hand by [Trify3D](https://trify3d.com/blog/trellis-2-vs-hunyuan-3d), and I could not find it.
- I searched for other 2026 open releases but may have missed some. Direct3D-S2 was confirmed only as the base of Pixal3D's `paper` branch, not reviewed separately.

## Hardware, run time, Windows, CPU, hosted demo and output

### Takeaway
On 12 GB, TRELLIS.2 and Pixal3D depend on community Windows wrappers and low-memory modes. Official minimums and community figures conflict, so expect some trial and error. CPU is realistic only for the older, weaker models.

### Cited Findings
| Model | GPU memory | Windows | CPU | Output |
|---|---|---|---|---|
| TRELLIS.2 official | 24 GB minimum; 3 s at 512³, 17 s at 1024³, 60 s at 1536³ on H100 | Linux only | Not stated | GLB, example 4096 texture, example 1M decimation target, WebP option — [repo](https://github.com/microsoft/TRELLIS.2) |
| TRELLIS.2 ComfyUI wrapper | 512 about 6 GB, 1024 about 8 GB, 1024_cascade about 10 GB, 1536_cascade about 12 GB or more — [DeepWiki](https://deepwiki.com/visualbruno/ComfyUI-Trellis2/6-troubleshooting-and-faq) (unofficial) | Tested on Windows 11 — [repo](https://github.com/visualbruno/ComfyUI-Trellis2) | Not stated | Has simplify and remesh nodes |
| TRELLIS.2 quantized | About 4 GB low-VRAM mode, about 14 GB fast mode, about 7 min — [uploader claim](https://huggingface.co/Lifec-321/trellis2-quantized-v3) | Not stated | Not stated | Not reviewed |
| Pixal3D | No official figures; `--low_vram` available — [repo](https://github.com/TencentARC/Pixal3D). Strict NAF can run out of memory on 12 GB, with fixes listed — [ComfyUI node](https://github.com/Saganaki22/Pixal3D-ComfyUI) | Community guide | Not stated | GLB; recommended 4096 texture and 1M target, around 5000 allowed but can lose detail |
| Hunyuan3D 2.1 | 10 GB shape, 21 GB texture, 29 GB both | Stated — [repo](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1) | Not stated | Format not named on the 2.1 page |
| Hunyuan3D 2.0 | About 6 GB shape, about 16 GB both | Stated — [repo](https://github.com/Tencent-Hunyuan/Hunyuan3D-2) | Not stated | Trimesh, saved as GLB or OBJ |
| TripoSG | 8 GB minimum | Not mentioned | Not stated | GLB, `--faces` control; page does not mention texture — [repo](https://github.com/VAST-AI-Research/TripoSG) |
| Step1X-3D | About 27 GB with texture, about 152 s | Not mentioned | Not stated | GLB — [repo](https://github.com/stepfun-ai/Step1X-3D) |
| SAM 3D Objects | 32 GB minimum — [setup](https://raw.githubusercontent.com/facebookresearch/sam-3d-objects/main/doc/setup.md) | Linux 64-bit only | Not stated | Splat as PLY shown; GLB not confirmed — [repo](https://github.com/facebookresearch/sam-3d-objects) |
| SPAR3D | 10.5 GB, about 7 GB low-VRAM (the page also says about 6 GB) | Experimental | Yes, very slow | GLB, texture size and remesh options — [repo](https://github.com/Stability-AI/stable-point-aware-3d) |
| SF3D | About 6 GB | Experimental | Yes | GLB, texture size and remesh options — [repo](https://github.com/Stability-AI/stable-fast-3d) |
| TripoSR | About 6 GB; under 0.5 s on A100 | No specific notes | CPU fallback per [triposr.org](https://triposr.org/blog/hunyuan3d-vs-trellis) | Vertex colours, or `--bake-texture` — [repo](https://github.com/VAST-AI-Research/TripoSR) |
| InstantMesh | Not stated | Not mentioned | Not stated | OBJ with vertex colours, `--export_texmap` option — [repo](https://github.com/TencentARC/InstantMesh) |

- Consumer-card timings: on an RTX 4080 SUPER at resolution 1024, using Q8 GGUF weights, TRELLIS.2 took 155 s (prop) and 526 s (character), and Pixal3D took 219 s and 581 s — [Dimension pack](https://raw.githubusercontent.com/insodimension/dimension-community/HEAD/packs/gen-local-3d/README.md)
- A vendor reports about 3.5 minutes for TRELLIS.2 at 1024 on an RTX 4070 Ti Super — [Trify3D](https://trify3d.com/blog/trellis-2-vs-hunyuan-3d)
- The ComfyUI wrapper needs approved access to the gated DINOv3 model — [repo](https://github.com/visualbruno/ComfyUI-Trellis2)
- Hugging Face Spaces showed "Running on Zero" when checked, with no visible error: [TRELLIS.2](https://huggingface.co/spaces/microsoft/TRELLIS.2), [Hunyuan3D-2.1](https://huggingface.co/spaces/tencent/Hunyuan3D-2.1), [Pixal3D](https://huggingface.co/spaces/TencentARC/Pixal3D)
- VRAM tiers beyond 24 GB are not relevant here. A Hakky guide suggests 512 and a tiled decoder as the starting point at 12 GB, and calls its figures non-benchmarks — [Hakky](https://book.st-hakky.com/en/data-science/trellis2-native-vs-legacy-vram-guide)
- Hunyuan3D ComfyUI node defaults to octree resolution 256, with a range of 16 to 512 — [Comfy docs](https://docs.comfy.org/built-in-nodes/VAEDecodeHunyuan3D.md)

### Inferences
- By tier, for this subject:
  - 6 to 8 GB: Hunyuan3D 2.0 shape, TripoSG, SF3D, TripoSR. TRELLIS.2 at 512 only.
  - 12 GB: TRELLIS.2 and Pixal3D at 1024 with low-memory settings, Hunyuan3D 2.1 shape only, SPAR3D.
  - 16 GB: the above with more margin, plus Hunyuan3D 2.0 with texture.
  - 24 GB or more: official TRELLIS.2 and 1536 modes, on Linux or WSL.
  - 32 GB: SAM 3D Objects, and full Hunyuan3D 2.1 at about 29 GB.
- The cheapest first test is the three Spaces, with no install. This uploads the client's photo to a public service, so check the client is comfortable with that.
- For a phone page, 1M triangles and 4096 textures are far too heavy. Decimate hard and bake the relief into a normal map, so the curls survive at a low triangle count. Note that three.js WebP texture support should be tested on target phones.

### Gaps
- No verified 12 GB hands-on report on TRELLIS.2 or Pixal3D. The figures above are unofficial, and the uploader and vendor claims are untested.
- ZeroGPU daily quotas for these Spaces were not established.
- Default triangle counts and texture sizes are unavailable for Hunyuan3D 2.1, TripoSG, SPAR3D and SF3D.

## Licences: is use on a client's portfolio site allowed?

### Takeaway
"MIT" on TRELLIS.2 and Pixal3D is not the full picture, because they depend on separately licensed parts, one of which is non-commercial. Hunyuan3D's territory clause does not exclude Egypt, but it also forbids displaying output in the EU, UK and South Korea, which is a real question for a public website. This is a reading of the text and not legal advice.

### Cited Findings
- **Hunyuan3D 2.1**
  - Territory is "the worldwide territory, excluding the territory of the European Union, United Kingdom and South Korea". Section 5(c) says you "must not use, reproduce, modify, distribute, or display the Tencent Hunyuan 3D 2.1 Works, Output or results" outside it — [LICENSE](https://raw.githubusercontent.com/Tencent-Hunyuan/Hunyuan3D-2.1/main/LICENSE)
  - Above 1 million monthly active users a separate licence is required, and "Tencent claims no rights in Outputs You generate" — [LICENSE](https://raw.githubusercontent.com/Tencent-Hunyuan/Hunyuan3D-2.1/main/LICENSE)
- **Hunyuan3D 2.0** has the same Territory wording and 1 million threshold — [LICENSE](https://raw.githubusercontent.com/Tencent-Hunyuan/Hunyuan3D-2/main/LICENSE). A third-party wiki lists it as Apache-2.0, which [the LICENSE file](https://raw.githubusercontent.com/Tencent-Hunyuan/Hunyuan3D-2/main/LICENSE) contradicts — [ComfyUI wiki](https://comfyui-wiki.com/en/models/hunyuan3d)
- **TRELLIS.2**: "released under the MIT License" — [model card](https://huggingface.co/microsoft/TRELLIS.2-4B). Dependencies nvdiffrast and nvdiffrec have their own terms — [repo](https://github.com/microsoft/TRELLIS.2)
- **nvdiffrast**: "The Work and any derivative works thereof only may be used or intended for use non-commercially", defined as "for research or evaluation purposes only and not for any direct or indirect monetary gain" — [LICENSE](https://raw.githubusercontent.com/NVlabs/nvdiffrast/main/LICENSE.txt)
- ComfyUI's native TRELLIS.2 and Pixal3D nodes reportedly avoid those NVIDIA dependencies, according to a search excerpt. The page itself refused my fetch, so this needs checking — [InstaSD](https://www.instasd.com/post/trellis-2-pixal3d-native-comfyui-guide)
- **Pixal3D**: the project says "released under the MIT License", with third-party components keeping their terms — [model page](https://huggingface.co/TencentARC/Pixal3D). An open issue from July 9, 2026 asks about a wrapper's description of the weights as "academic-only / non-commercial / EU-excluded", with no maintainer reply visible — [issue 33](https://github.com/TencentARC/Pixal3D/issues/33)
- **DINOv3** (used by TRELLIS.2 and Pixal3D wrappers): a worldwide royalty-free grant with no field-of-use limit, but you must prominently display "Built with DINOv3" on a related site or documentation — [licence](https://ai.meta.com/resources/models-and-libraries/dinov3-license/)
- **RMBG-2.0**: CC BY-NC 4.0, and "Commercial use is subject to a commercial agreement with BRIA" — [model card](https://huggingface.co/briaai/RMBG-2.0). TRELLIS.2 skips its background remover when the input already has real transparency — [pipeline code](https://raw.githubusercontent.com/microsoft/TRELLIS.2/main/trellis2/pipelines/trellis2_image_to_3d.py). The repo also ships a [BiRefNet remover](https://raw.githubusercontent.com/microsoft/TRELLIS.2/main/trellis2/pipelines/rembg/BiRefNet.py), and I could not confirm which one the default config uses.
- **SAM 3D Objects**: "non-exclusive, worldwide, non-transferable and royalty-free limited license", no non-commercial limit in the grant, trade-control and military-use limits apply — [LICENSE](https://raw.githubusercontent.com/facebookresearch/sam-3d-objects/main/LICENSE)
- **SF3D and SPAR3D**: Stability AI Community License, free for commercial use under US $1,000,000 annual revenue, Enterprise License above — [SF3D](https://huggingface.co/stabilityai/stable-fast-3d), [SPAR3D](https://huggingface.co/stabilityai/stable-point-aware-3d)
- **Plain permissive**: TripoSR MIT — [repo](https://github.com/VAST-AI-Research/TripoSR); TripoSG MIT — [repo](https://github.com/VAST-AI-Research/TripoSG); Step1X-3D Apache-2.0 — [repo](https://github.com/stepfun-ai/Step1X-3D); InstantMesh Apache-2.0 — [repo](https://github.com/TencentARC/InstantMesh); MV-Adapter Apache-2.0 — [repo](https://github.com/huanngzh/MV-Adapter); Wonder3D MIT — [repo](https://github.com/xxlong0/Wonder3D)

### Inferences
- Egypt falls inside Hunyuan's Territory, so generating there is licensed. But a public portfolio page can be viewed from the EU, UK and South Korea, and the clause names "display" of "Output". Whether web access counts as display outside the Territory is unclear, so a cautious reading avoids Hunyuan3D for a public client site or takes advice.
- To reduce TRELLIS.2 risk: feed a pre-cut PNG with transparency so no background remover runs, prefer the native ComfyUI path if its nvdiffrast-free claim holds, and add a "Built with DINOv3" credit.
- Whether the nvdiffrast licence reaches a mesh baked with it is a legal question I cannot settle. A paid client job is plausibly "monetary gain", so the conservative route is to avoid nvdiffrast in the pipeline.
- A permissive fallback for geometry only is TripoSG (MIT), but textures would need another tool.

### Gaps
- No authoritative answer on whether the nvdiffrast clause covers outputs. An [issue on the original TRELLIS repo](https://github.com/microsoft/TRELLIS/issues/298) asks this, and I saw no maintainer reply in the search excerpt.
- I did not read the Stability Community License text beyond the model card summaries, or Zero123++ and Era3D licence files.
- Hosted 3.x terms were not reviewed.

## What happens to the sides the photo never saw?

### Takeaway
Every model invents the back. I found no test that measures whether curls and the face survive on a monochrome sculpt, so this must be judged by eye on the user's own photo.

### Cited Findings
- TripoSR guesses occluded parts from one view and gives less fine detail from its single feed-forward pass — [triposr.org](https://triposr.org/blog/hunyuan3d-vs-trellis) (vendor)
- SPAR3D advertises "improved backside modelling using a fast point diffusion model" — [model card](https://huggingface.co/stabilityai/stable-point-aware-3d), and its point cloud can be edited to correct missing back-side detail — [repo](https://github.com/Stability-AI/stable-point-aware-3d)
- Pixal3D's abstract does not address unseen regions, and multi-view aggregation applies only when views are supplied — [arXiv](https://arxiv.org/abs/2605.10922)
- TRELLIS.2 raw meshes "may contain small holes or minor topological discontinuities", and the model "has not been aligned with human preferences" — [model card](https://huggingface.co/microsoft/TRELLIS.2-4B)
- Reported on a human portrait: Hunyuan3D had softer small facial features and simple hair, and TRELLIS 2 had a face "more sculpted than realistic" — [Vitalify](https://www.vitalify.asia/en/blog/ai-image-to-3d-generators-comparison). The article did not assess back sides.

### Inferences
- Pixel-aligned generation (Pixal3D) should help the side facing the camera most, because detail comes straight from pixels. It gives no extra information about the back, so a mismatch in quality between front and back is the thing to look for. This is reasoning from the method and untested.
- A poodle's curls are a repeating pattern, which generative models may continue plausibly around the body. The small face is the bigger risk. Both points are my expectation.

### Gaps
- No source compares back quality across these models. The leaderboard uses turntable videos, so its votes include back views, but it publishes no back-specific score.

## Do multi-view generators still matter?

### Takeaway
As the main route, largely no: direct models have overtaken them on recency and on detail resolution. They remain useful as an optional helper, generating extra views to feed a model that accepts multi-view input, though those views are invented and add no real information.

### Cited Findings
- Wonder3D's last dated news is December 22, 2024. It produces six views at 256x256, which its README calls "low resolution", is sensitive to facing direction, and assumes orthographic input. Era3D produces 512x512 — [repo](https://github.com/xxlong0/Wonder3D)
- InstantMesh uses a customised Zero123++ — [repo](https://github.com/TencentARC/InstantMesh)
- MV-Adapter: last dated update June 2025, Apache-2.0, 768 resolution from SDXL, image-to-multiview needs about 14 GB, SD2.1 variants under 10 GB for texture work, and it can texture a given mesh and save a GLB — [repo](https://github.com/huanngzh/MV-Adapter)
- Downstream models now accept views directly: Pixal3D multi-view needs images plus camera data in `transforms.json`, with a four-view orbit example — [repo](https://github.com/TencentARC/Pixal3D). The ComfyUI wrapper has multi-view nodes for TRELLIS.2 and Pixal3D — [repo](https://github.com/visualbruno/ComfyUI-Trellis2). Hunyuan3D-2mv takes multi-view input — [repo](https://github.com/Tencent-Hunyuan/Hunyuan3D-2).

### Inferences
- The most useful current role is possibly texturing: keep a good mesh from a direct model, and use MV-Adapter or a mesh-texturing node to repaint it. At 14 GB, image-to-multiview exceeds the 12 GB card unless the SD2.1 route is used.
- Multi-view generators smooth detail across views, which is a poor fit for tiny curls at 256 to 768 pixels. No source tests this directly.

### Gaps
- No independent comparison of multi-view plus reconstruction against direct models. None of these generators appears on the leaderboard.
- Newer multi-view generators from 2026 were not found. Zero123++ and Era3D were not reviewed from their own repos.

## Independent evidence, known failures on fur, and why TripoSR gave a lumpy blob

### Takeaway
Independent evidence is thin, and only the crowd leaderboard is at scale. Newer models should be materially better than TripoSR because they generate a high-resolution shape instead of regressing a coarse one in one pass, but no source shows this on a curly object.

### Cited Findings
- The leaderboard does not list TripoSR, TripoSG, SF3D or SPAR3D in its visible ranking. The operator is a crowd-data firm with no evident stake in a model — [benchmark.ai](https://www.benchmark.ai/image-to-3d)
- triposr.org, which sells hosted TripoSR, says outright that its comparison is "not an independent benchmark" and that no independent apples-to-apples benchmark exists. Its "last tested" date refers to re-checking documentation — [triposr.org](https://triposr.org/blog/hunyuan3d-vs-trellis)
- Vendor claims need discounting: Pixazo ranks Hunyuan 3D Pro first on its own board — [Pixazo](https://www.pixazo.ai/models/leaderboard); Meshy says Meshy 7 leads its own benchmark — [Meshy](https://www.meshy.ai/blog/meshy-7-image-to-3d-geometry-alignment)
- Trify3D says the gap between models "widens on complex ones (characters, vehicles, organic shapes)" — [Trify3D](https://trify3d.com/blog/trellis-2-vs-hunyuan-3d) (vendor, opinion)
- Hair failures so far come from a single human portrait: broken strands and holes on TRELLIS 2, simple hair on Hunyuan3D — [Vitalify](https://www.vitalify.asia/en/blog/ai-image-to-3d-generators-comparison)
- TripoSR outputs vertex colours by default — [repo](https://github.com/VAST-AI-Research/TripoSR). TRELLIS.2 has modes up to 1536³ with separate shape and material stages — [repo](https://github.com/microsoft/TRELLIS.2)

### Inferences
- The likely cause of the blob is that TripoSR predicts one averaged shape in a single pass, so fine uncertain detail such as curls averages away. Vertex colours then cannot hide this. Newer models sample a specific shape at far higher resolution and can output a PBR texture.
- Curls on the candle are probably sculpted bumps, not separate strands, which should suit these models better than real fur or the broken-strand failure seen on human hair. Expect either soft bumps or noisy pseudo-curls, and check for holes in TRELLIS.2 output.
- A sensible pass test: rotate the mesh under flat grey material. A texture can fake relief that the geometry does not have.

### Gaps
- No controlled fur, plush or poodle test found. The one plush reference was a vendor gallery label — [hunyuan3d.dev](https://hunyuan3d.dev/)
- No Reddit or ComfyUI community thread on fur could be retrieved, and the [Medium hands-on with TRELLIS.2](https://medium.com/@ammanakhtar8/one-image-in-3d-out-free-open-source-i-ran-trellis-2-3f7f5ed8e96c) refused my fetch.
- I did not try to verify the published voxel resolution of TripoSR, so the resolution contrast above is qualitative.
