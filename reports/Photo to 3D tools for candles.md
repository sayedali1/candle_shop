# Buy the shape, bake the curls

**Recommendation.** Stop fitting ellipsoids for the poodle. Generate the shape with **Meshy 7.1 on a paid plan** and run **TRELLIS.2 at 1024 locally** as a free control on the same day. Then clean the mesh with PyMeshLab and trimesh, reduce it to 24k to 48k triangles with gltf-transform, bake normal and colour maps in Blender, and compress with meshopt. Keep your existing wax shader and flame. The test costs about $10. **Nobody has run any of these tools on your photo, and no source tests a poodle, curls or wax**, so this choice is provisional until the test at the end of this report. Three things no tool fixes: the back of the model is always invented, depth maps cannot repair a wrong shape, and Gaussian splats are unproven on a weak phone. One extra real photo of the back would probably help more than any tool choice.

## The recommended chain has seven steps

Each step does one job. The hand-built model failed because one method tried to do all of them.

| Step | Tool | Job | Tested? |
|---|---|---|---|
| 1. Prepare | Your outline mask, tight crop | Cut-out PNG with transparency | No |
| 2. Generate | Meshy 7.1 (TRELLIS.2 as control) | Volume, face, back | No |
| 3. Repair | PyMeshLab, trimesh | Floaters, holes, flat base, cut off any merged wick | No |
| 4. Reduce | `gltf-transform weld`, `simplify` | 24k to 48k triangles | Yes, on a synthetic mesh |
| 5. Bake | Blender headless (Cycles) | Curls into a 1024 normal map, plus colour | No |
| 6. Compress | `gltf-transform meshopt` | Small GLB that r160 can read | Yes, on a synthetic mesh |
| 7. Shade | `MeshStandardMaterial` plus `onBeforeCompile` | Lit wax, separate wick and flame | No |

- Why Meshy first: it ranks high in the largest test, its terms were readable, and its options are documented. Its evidence on fine detail is the weak point (see the next section).
- Why TRELLIS.2 as control: it is the top open model on the same board, it runs on your machine, and the photo never leaves your PC.
- Simpler candles: keep your recipe approach. A plain pillar or jar does not need an invented shape. Steps 5 and 7 still apply. This is my judgement. No source compares them.

## Hosted models lead the only large test, but none is proven on curls

The best general evidence is a crowd vote: 357 images and 262,668 votes ([benchmark.ai](https://www.benchmark.ai/image-to-3d)). Intervals are about ±17 to ±20.

| Model | Score | Type |
|---|---|---|
| Hi3D v3.0 | 1366 | Hosted |
| Meshy 7.1 | 1298 | Hosted |
| Tripo H3.1 | 1261 | Hosted |
| Hunyuan3D 3.1 Pro | 1144 | Hosted |
| TRELLIS.2 | 1005 | Open |
| Rodin Gen-2.5 High | 956 | Hosted |
| Pixal3D | 754 | Open |
| Hunyuan3D 2.1 | 750 | Open |

- This board measures general quality, not this subject. It has a Fur-Hair-Foliage tag, but the filtered ranking could not be retrieved. **Open it by hand before paying.**
- Faces: one portrait test favoured Tripo P1. It found Meshy 6 simplified and Rodin soft ([Vitalify](https://www.vitalify.asia/en/blog/ai-image-to-3d-generators-comparison)). It is one human portrait on older versions.
- Geometry: a test written by a Meshy employee still put Tripo first on untextured geometry and admitted Meshy smooths fine detail ([HackerNoon](https://hackernoon.com/how-i-stress-tested-3-ai-3d-generators-on-the-same-inputs-what-the-numbers-actually-show)). That test used Meshy 6, not 7.1.
- Rodin conflict: soft face in the first test, close tracking of small features in the second.
- So Tripo is the first backup. I did not lead with it because its official pricing and terms pages returned 403, so its rights are known only second-hand.
- Hi3D tops the board, but its price and terms are unconfirmed, and I could not confirm it is the same product as Hitem3D.
- Luma has left 3D. Its Genie product is reported as closed since January 2026 ([Meshy blog](https://www.meshy.ai/blog/best-ai-tools-for-3d-game-assets), a competitor).

**Why the old TripoSR result was a lumpy blob.** My reading: it predicts one averaged shape in a single pass, so uncertain detail like curls averages away. Newer models sample a specific shape at higher resolution. No source shows this on a curly object.

**A risk for wax.** One colour means curls show only through soft shading. That gives the model less signal than a coloured object. Sculpted bumps should still suit these models better than real hair. Expect soft bumps or noisy fake curls. This is my reasoning, not a test.

### Open models on your 12 GB card

| Model | Fit on 12 GB | Windows | Licence note |
|---|---|---|---|
| TRELLIS.2 | Official minimum is 24 GB, Linux only ([card](https://huggingface.co/microsoft/TRELLIS.2-4B)). Wrapper figures: 1024_cascade about 10 GB, 1536_cascade 12 GB or more ([DeepWiki](https://deepwiki.com/visualbruno/ComfyUI-Trellis2/6-troubleshooting-and-faq), unofficial) | Wrapper tested on Windows 11 ([repo](https://github.com/visualbruno/ComfyUI-Trellis2)) | MIT, with catches below |
| Pixal3D | `--low_vram` runs at 1024 ([repo](https://github.com/TencentARC/Pixal3D)); strict mode can run out of memory on 12 GB ([node](https://github.com/Saganaki22/Pixal3D-ComfyUI)) | Community guide | MIT stated; open question on the weights ([issue 33](https://github.com/TencentARC/Pixal3D/issues/33)) |
| Hunyuan3D 2.1 | Shape 10 GB, texture 21 GB ([repo](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1)), so shape only | Stated | Territory problem below |
| TripoSG | 8 GB, no texture mentioned ([repo](https://github.com/VAST-AI-Research/TripoSG)) | Not mentioned | MIT, cleanest fallback |
| SAM 3D Objects | 32 GB ([setup](https://raw.githubusercontent.com/facebookresearch/sam-3d-objects/main/doc/setup.md)) | Linux | Too big |

- No verified hands-on report on a 12 GB card exists. Expect trial and error.
- Timing guide: on an RTX 4080 SUPER at 1024, TRELLIS.2 took 155 s to 526 s and Pixal3D 219 s to 581 s ([Dimension pack](https://raw.githubusercontent.com/insodimension/dimension-community/HEAD/packs/gen-local-3d/README.md)). That card has more memory than yours.
- Pixal3D claims the best match to the photo, but only in its authors' words ([paper](https://arxiv.org/abs/2605.10922)), and it ranks low on the board. Try it third.
- TRELLIS.2 meshes may have small holes ([card](https://huggingface.co/microsoft/TRELLIS.2-4B)), and one portrait test saw broken hair ([Vitalify](https://www.vitalify.asia/en/blog/ai-image-to-3d-generators-comparison)).
- Hunyuan3D 3.x appears hosted only, based on secondary sources ([WaveSpeed](https://wavespeed.ai/blog/posts/hunyuan-3d-api/)).

### Skip multi-view generators

- They invent views, so they add no real information. Old ones are also small: Wonder3D makes 256 px views, Era3D 512 px ([repo](https://github.com/xxlong0/Wonder3D)).
- MV-Adapter reaches 768 px but needs about 14 GB for image to multi-view ([repo](https://github.com/huanngzh/MV-Adapter)). Its one useful role is repainting a good mesh, using the lighter SD2.1 route.
- Current models accept views directly. Meshy takes up to 4 and Rodin up to 5 ([Scenario](https://help.scenario.com/en/articles/comparing-generative-3d-models/)). Use that slot only for real photos.

## Depth and normals can add curls, but not shape

- A map changes lighting on surfaces the photo saw. It adds nothing on the back and does not change the outline. No source measures how far it can turn, so test it.
- Your soft face does not prove depth is useless. Depth Anything V2 Small is its smallest model and defaults to 518 px ([repo](https://github.com/DepthAnything/Depth-Anything-V2)). A small face gets few of those pixels.
- Nearly all detail claims come from the model authors. Published normal scores sit within a few degrees of each other ([Marigold V2 paper](https://arxiv.org/pdf/2609.08084)), and none measures curl-sized relief.

| Tool | Use | Licence | Verdict |
|---|---|---|---|
| MoGe-3 ViT-L | Depth and normals, aimed at fine geometry ([README](https://raw.githubusercontent.com/microsoft/MoGe/main/README.md)) | Code MIT; weights tagged MIT ([card](https://huggingface.co/Ruicheng/moge-3-vitl)) | **Try first, on a tight crop** |
| StableNormal | Normals, built for sharpness | Apache-2.0 listed; weight terms unchecked ([repo](https://github.com/Stable-X/StableNormal)) | Second |
| Depth Anything V2 Small | Control at raised input size | Apache 2.0; larger sizes CC BY-NC ([repo](https://github.com/DepthAnything/Depth-Anything-V2)) | Shows how much softness came from resolution |
| Marigold V2 | Claims to resolve fur ([paper](https://arxiv.org/abs/2609.08084)) | Weights and terms not found | Blocked until confirmed |
| DSINE | Normals | Non-commercial ([LICENSE](https://raw.githubusercontent.com/baegwangbin/DSINE/main/LICENSE)) | No |
| UniDepthV2 | Metric depth | BY-NC ([repo](https://github.com/lpiccinelli-eth/UniDepth)) | No |
| Lotus-2 | Depth and normals | Needs a 40 GB GPU and FLUX.1-dev access ([repo](https://github.com/EnVision-Research/Lotus-2)) | No |

How to use the result (my engineering reasoning, not a sourced method):

- Use only the high-pass of the predicted normals, so large forms do not fight the mesh.
- These normals are in camera space. Bake them onto the mesh UVs before use.
- Fade the effect on surfaces that face away from the camera.
- A misaligned relief map looks worse than none. Use the MoGe-3 point map to help line up.

Use this only if the generated mesh has a good face and soft curls. It is a repair, not a main route.

## Splats fit in the file budget but stay a side experiment

- A generator exists: TripoSplat, one photo, up to 262,144 Gaussians, MIT ([repo](https://github.com/VAST-AI-Research/TripoSplat)). Its card names birefnet, DINO v3 and the FLUX.2 VAE without their licences ([card](https://huggingface.co/VAST-AI/TripoSplat)).
- Do not use SHARP. Its model licence bans commercial use ([LICENSE_MODEL](https://raw.githubusercontent.com/apple/ml-sharp/main/LICENSE_MODEL)).
- A viewer exists: Spark, MIT, built to work with three.js ([repo](https://github.com/sparkjsdev/spark)). I did not confirm it works with r160. The three.js native renderer is reported for r186 ([Radiance Fields](https://radiancefields.com/three.js-merges-a-native-gaussian-splat-renderer-for-webgpu-in-r186)), so it needs an upgrade.
- File size is fine. Expect roughly 4 to 6 MB at the cap as SOG. I extrapolated this from a research encoder that is better than SOG ([KISS-GS](https://arxiv.org/pdf/2608.26948)), so measure it.
- **The blocker is frame rate. No measured browser fps exists for any mid-range Android or any Mali GPU.** The Galaxy M32 named in the research notes has a Mali-G52 MC2 ([GSMArena](https://m.gsmarena.com/samsung_galaxy_m32-ampp-10887.php)) and already runs near 30 fps.
- Light is baked in. A moving flame needs a colour tint (cheap, not real light) or a proxy-mesh pass ([PlayCanvas](https://developer.playcanvas.com/user-manual/gaussian-splatting/building/relighting/)), which adds cost. This conflicts with your lit-wax goal.

Run a one-day splat test only if the mesh route fails. Try 50k, 100k and 262k on the real phone.

## A 48k mesh and two 1024 maps fit a phone

**Budget.** Google's Scene Viewer calls 30k to 50k triangles ideal and 100k the limit ([Google](https://developers.google.com/ar/develop/scene-viewer)). That guidance is for its native viewer, not WebGL. No solid mid-range WebGL figure exists. My working limits: under about 40k vertices, about 30 draw calls, about 30 MB of textures in GPU memory, pixel ratio capped at 1.5 to 2.

**Reducing.** Measured locally on a synthetic 1M-triangle mesh, not on real output and not on a phone:

| Triangles | Mean error on a 20 cm candle | Max error | Meshopt gzipped | Draco gzipped |
|---|---|---|---|---|
| 48k | 0.03 mm | 0.34 mm | 215 KB | 170 KB |
| 20k | 0.05 mm | 0.51 mm | 97 KB | 76 KB |

- **Use meshopt.** With decoders counted, 48k comes to 221 KB against Draco's 245 KB. Draco wins after about two unique models. These gains assume gzip, so check `content-encoding` on Vercel.
- `gltf-transform optimize` alone will not reach budget, because its simplify ratio is 0 with error 0.0001 ([simplify.ts](https://raw.githubusercontent.com/donmccurdy/glTF-Transform/main/packages/functions/src/simplify.ts)). Set `--ratio` and `--error`.
- Fragmented UVs stop the simplifier. In the local test, 40,000 charts missed the target (79,996 triangles, 159,996 vertices). Stripping UV and NORMAL and welding fixed it. Always count vertices too.
- Use quadric collapse, not remeshers. Quadric spends triangles on bumps, and remeshers spread them evenly and lose UVs ([Blender API](https://docs.blender.org/api/current/bpy.ops.object.html)). This is reasoning from the methods. No published comparison exists.
- Bake at 2048 and downsample to 1024. Keep AO and thickness in vertex colours.
- Skip KTX2 for one or two candles. The transcoder is about 260 KB gzipped (measured), and Khronos says WebP or JPEG can be better for a single model ([Khronos](https://raw.githubusercontent.com/KhronosGroup/3D-Formats-Guidelines/main/KTXArtistGuide.md)). Use it for a shelf. A 1024 map costs 5.6 MB uncompressed in GPU memory (my arithmetic).

**r160 points.** `gltf-transform` 4.5.1 output decoded correctly with r160's meshopt decoder (measured). r160 knows `EXT_meshopt_compression` but not the `KHR_` form, so pin the tool version. Your `vendor/three` has `GLTFLoader.js` but no decoders, so copy `meshopt_decoder.module.js` from the r160 package.

## Wax comes from your shader, not the generator

- Do not use `transmission`. In r160 it renders an extra pass at full drawing-buffer size (checked in the vendored code), and it has failed on some Android devices ([forum](https://discourse.threejs.org/t/transmission-of-meshphysicalmaterial-doesnt-work-on-some-android-devices/28836)). Skip sheen too, since it is documented for cloth ([docs](https://threejs.org/docs/pages/MeshPhysicalMaterial.html)).
- Use `MeshStandardMaterial` with a distance glow, absorbing blue faster than red. This is the main "lit" cue and it is cheap. Add the Barré-Brisebois translucency term ([r160 shader](https://raw.githubusercontent.com/mrdoob/three.js/r160/examples/jsm/shaders/SubsurfaceScatteringShader.js)) if the phone allows. Drop it first if not.
- Your `candle-builder.js` already has the `aAT` attribute for shut-in-ness and thinness. Fill it from a PyMeshLab shape-diameter bake ([filters](https://pymeshlab.readthedocs.io/en/latest/filter_list.html)), after reducing the mesh. No phone measurement exists for this shader.
- **Trap at line 438:** `candle-builder.js` sets `emissiveMap = map` on loaded models, so light baked into the texture will glow. Remove the light first.
- Removing light, in order:
  1. Divide out low-frequency brightness per vertex. This suits near-single-colour wax.
  2. Try Marigold IID ([card](https://huggingface.co/prs-eth/marigold-iid-lighting-v1-1)). It uses RAIL++-M terms, which were not read, and it is not built for translucent material.
  3. Last resort: flat wax colour, and let the normal map carry all detail. For a one-colour candle this may be the best result.
- Keep wick and flame as separate objects, and store the wick point in the recipe. Cutting off a merged wick needs hand tuning. No automatic method was found.

## Licence, cost and privacy favour a paid month

This is my reading of the texts, not legal advice.

| Route | Cost | Rights | Privacy |
|---|---|---|---|
| Meshy Starter | $10/mo for 250 credits; 50% off first month for new users ([pricing](https://www.meshy.ai/pricing)). 30 to 35 credits per model ([docs](https://docs.meshy.ai/en/webapp/pricing)), so about 7 models | Paid customers own output, and rights survive a downgrade ([Terms](https://www.meshy.ai/terms-of-use), [help](https://intercom.help/meshy/en/articles/16102098-can-i-use-meshy-assets-commercially)) | **May train on uploads unless you opt out by email** |
| Meshy Free | $0 | Meshy owns output, CC BY 4.0 ([Terms](https://www.meshy.ai/terms-of-use)); no 7.1 downloads | Avoid |
| Tripo Pro | About $20/mo (third party) ([AIFreeAPI](https://www.aifreeapi.com/en/posts/tripo-3d)) | Commercial on paid, official text unread | Free tier reported public; avoid it |
| Rodin Creator | $30/mo, about 60 models ([pricing](https://hyper3d.ai/pricing)) | Export for any purpose | "Private" output has strong wording, but input images are unclear ([Terms](https://hyper3d.ai/legal/terms)) |
| Hunyuan API | $15 prepaid, about $0.38 per model ([Tencent](https://www.tencentcloud.com/document/product/1284/75281)) | Web terms not found | Terms not found |
| Local TRELLIS.2 | $0 | See below | Best: photo stays on your PC |

**Licence traps in open models:**

- **Hunyuan3D 2.x:** the licence excludes the EU, UK and South Korea, and bans display of Output there ([LICENSE](https://raw.githubusercontent.com/Tencent-Hunyuan/Hunyuan3D-2.1/main/LICENSE)). A public page can be viewed from those places. Avoid it for this site, including its delight model.
- **TRELLIS.2:** MIT, but it depends on nvdiffrast, which is for research or evaluation only ([LICENSE](https://raw.githubusercontent.com/NVlabs/nvdiffrast/main/LICENSE.txt)). Using it in a test fits that wording. Shipping paid client work is the open question. ComfyUI's native nodes reportedly avoid it, but I saw only a search excerpt ([InstaSD](https://www.instasd.com/post/trellis-2-pixal3d-native-comfyui-guide)). Confirm this before shipping a TRELLIS.2 mesh.
- **DINOv3:** the wrappers use it. Its licence needs a visible "Built with DINOv3" credit ([licence](https://ai.meta.com/resources/models-and-libraries/dinov3-license/)), and the model is gated.
- **RMBG-2.0:** non-commercial ([card](https://huggingface.co/briaai/RMBG-2.0)). Feed a PNG with real transparency, so TRELLIS.2 skips its background remover ([code](https://raw.githubusercontent.com/microsoft/TRELLIS.2/main/trellis2/pipelines/trellis2_image_to_3d.py)).
- **Tools:** PyMeshFix is GPL-3.0 ([repo](https://github.com/pyvista/pymeshfix)). Prefer PyMeshLab for the repair.

**Before any upload:**

- Get the client's yes in one message.
- Crop out the home and any people.
- Email support@meshy.ai for the training opt-out ([Terms §2.9](https://www.meshy.ai/terms-of-use)). I could not confirm how fast it applies.
- Do not use free tiers or public Hugging Face Spaces with this photo. CC BY or CC0 terms could let others reuse a copy of the maker's design.
- Tell the client the back is invented. Open the page on the photographed side and limit rotation. That is an honesty decision for her.

**Payment from Egypt is unconfirmed.** Nothing found blocks it, but Meshy's PayPal list leaves out Egypt ([help](https://intercom.help/meshy/en/articles/9991959-can-i-pay-with-paypal)). Plan on an international-enabled credit card, and make the small first payment before planning around it.

## Test it on the photo in one day

**Prepare**

1. Get the client's OK. Send the Meshy opt-out email.
2. Open the leaderboard's Fur-Hair-Foliage tag by hand.
3. Crop the poodle tightly and apply your outline mask as alpha. Save `poodle.png`.

**Generate three candidates from the same PNG**

- **A:** Meshy 7.1 on Starter, PBR on, no remesh. Meshy advises `should_remesh: false` for highest quality ([API docs](https://docs.meshy.ai/en/api/image-to-3d)). I did not confirm the web interface shows the same options. Download at once.
- **B:** TRELLIS.2 at 1024_cascade in ComfyUI on your PC.
- **C:** Your current hand-built model, as the baseline.

**Score the raw meshes before any cleanup**

Use a flat grey material and one low side light, since texture can fake relief. The pass marks are my own starting points.

| Check | How | Pass |
|---|---|---|
| Outline | Render from the photo angle, compute overlap (IoU) with your mask | Within 0.03 of the hand-built score |
| Volume | Turn to 45 and 90 degrees | Rounded body, not flattened; side agrees with MoGe-3 depth |
| Face | Phone-size render at 0 and 15 degrees, shown to someone who has not seen the model | They say "poodle" and can find eyes and snout |
| Curls | Grey mesh, moving light | Bumps catch the light, at about the same size as in the photo |
| Back | Turn to 180 degrees | Believable, no holes |

**Finish the winner only**

These commands were run only on a synthetic mesh. The repair and bake steps were not run, and PyMeshLab, Blender and KTX tools are not installed yet.

```bash
npm i -D @gltf-transform/cli@4.5.1
npx gltf-transform weld clean.glb w.glb
npx gltf-transform simplify w.glb s.glb --ratio 0.048 --error 0.01   # ratio = target tris / source tris
npx gltf-transform meshopt baked.glb out.glb --level high
```

**Phone check on the real M32.** Record fps, `renderer.info` and `gl.RENDERER`.

- Under 48k triangles and about 40k vertices.
- GLB under 3 MB (my target).
- Holds about 30 fps with the flame lit.
- Relief holds at 0, 15, 30, 45 and 60 degrees. Set the page's rotation limit from the last good angle.

**What the result decides**

- Mesh passes: ship it. Fix any licence question first if B won.
- Good face, soft curls: add the MoGe-3 relief map.
- Good curls, bad face: try Tripo 3.1, then Pixal3D.
- All fail: ask for one photo of the back and use multi-view input. If there is no second photo, keep the hand-built model with a relief map and a narrow rotation, or run the splat day.

## Conclusion

The useful question is not "which model is best". It is which layer carries which part of the look. The generator carries volume, the normal map carries curls, and the shader carries wax. Your hand-built work still has value: its outline mask becomes the cut-out input and the score that any generated mesh must match.

The biggest unknown is cheap to settle. Reading more will not decide it, because no public evidence covers a one-colour sculpted curly object. One afternoon and $10 will. If the seller can still reach the candle, ask for the second photo anyway.
