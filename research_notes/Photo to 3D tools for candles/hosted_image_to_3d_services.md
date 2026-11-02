# Hosted one-photo-to-3D services for a handmade candle portfolio (checked 2026-11-01)

Reading note: pages were fetched on 2026-11-01 unless another date is given. Live price pages carry no date of their own, so "2026-11-01" means the date I read them. tripo3d.ai returned HTTP 403 to my fetches, so everything about Tripo comes from search snippets or third parties and is lower confidence. Most comparison articles have a commercial interest, and this is flagged where it applies.

## Which services are live, at what version and price, and what do the free tier and ownership look like?

### Takeaway
The real shortlist is Meshy 7.1, Tripo (3.1 / P2 preview), Rodin Gen-2.5 and Hunyuan3D 3.1 Pro, with Hitem3D as a newer contender. None of the free tiers suits a client site cleanly: Meshy's needs attribution and blocks the current models from download, Tripo's is reported as public and rights-retained, and Rodin's exports legacy models only. A paid month costs $10-30. Luma has left 3D.

### Cited Findings

**Comparison table (details and conflicts follow)**

| Service | Current model | Paid entry price | Approx. cost per model | Free tier | Free commercial use? |
|---|---|---|---|---|---|
| Meshy | 7.1 (also 6, 6 Lite) | Starter $10/mo, 250 credits; Pro $20/mo, 1,000 credits | 30-35 credits, so $0.60-0.70 on Pro, $1.20-1.40 on Starter (my arithmetic) | 100 credits/mo, 10 Meshy 6 Lite downloads | Yes, CC BY 4.0 with attribution |
| Tripo | 3.1, P2 preview | Pro about $20/mo (third-party) | $0.18 per API call (Meshy-authored test) | 200 or 300 credits/mo (sources conflict) | Conflicting; treat as no |
| Rodin (Hyper3D) | Gen-2.5 | Creator $30/mo or $24/mo yearly | About $0.50 (60 models for $30, my arithmetic) | Legacy-model export only, 10 private assets | Not stated on pricing page |
| Hunyuan3D (Tencent Cloud) | 3.0, 3.1 | Prepaid 1,000 credits for $15 | 25 credits = $0.375; up to 45 credits = $0.675 with PBR and FaceCount (my arithmetic) | 200 API credits once; 20 web generations/day reported Nov 2025 | Web platform terms not found |
| Hitem3D | 3.0 | 1,000 credits/mo tier; price not confirmed | Not confirmed | 100 lifetime credits, public, CC BY 4.0 (low confidence) | Reportedly yes with credit |

**Meshy**
- Plans: Free $0/100 credits/up to 10 assets, Starter $10/250, Pro $20/1,000, Premium $40/3,000, Studio $70/5,500. Starter and above are "private, customer-owned". New users get 50% off the first month on monthly plans, and annual plans get 20% off — [Meshy pricing, read 2026-11-01](https://www.meshy.ai/pricing)
- Free tier: 10 Meshy 6 Lite downloads a month, low queue priority, no API access — [Meshy pricing](https://www.meshy.ai/pricing). Downloading Meshy 7.1 output requires a paid plan — [Meshy blog, checked 2026-10-20](https://www.meshy.ai/blog/best-ai-tools-for-3d-game-assets)
- Credit costs: image-to-3D with Meshy 7.1 or 6 costs 20 credits, Ultra 2K/4K costs 25, 6 Lite costs 10; texture adds 10; remesh costs 0. Paid plans other than Enterprise start 7.1 at Ultra 2K, so the default is 25 — [Meshy docs](https://docs.meshy.ai/en/webapp/pricing)
- Ownership conflict inside Meshy's own pages: the docs say Free users own the output under CC BY 4.0 — [Meshy docs](https://docs.meshy.ai/en/webapp/pricing). The Terms say that for free-plan users Meshy "owns all right, title, and interest" and licenses output under CC BY 4.0, while paid customers "own their Customer Output" — [Meshy Terms §3.2, updated 2026-09-19](https://www.meshy.ai/terms-of-use). The Terms should be treated as controlling.
- Models generated on a paid plan keep those rights after a downgrade — [Meshy help](https://intercom.help/meshy/en/articles/16102098-can-i-use-meshy-assets-commercially)
- One third-party blog says Meshy Free is non-commercial only; this contradicts Meshy's official pages — [Sorceress](https://sorceress.games/blog/best-free-ai-3d-model-generator-honest-2026-picks)

**Tripo**
- Current models: Tripo 3.1 and P2 preview, as listed in October 2026 — [Scenario](https://help.scenario.com/en/articles/comparing-generative-3d-models/)
- Free plan: $0, 200 monthly credits (about 13 models), one concurrent task, limited exports, public models, non-commercial. Pro starts at $20/mo billed annually with private models and commercial use. Pricing checked 2026-10-05; terms page last updated 2025-07-11 — [AIFreeAPI](https://www.aifreeapi.com/en/posts/tripo-3d)
- A second aggregator adds: "non-commercial under CC BY 4.0", 15 downloads a month, storage for 10 models, Tripo branding on outputs, Pro with 3,000 credits, Max $90, Team $110. It labels itself "medium confidence" and its dates are inconsistent — [CostBench, "verified" 2026-10-20](https://www.costbench.com/software/ai-3d-generation/tripo-ai/free-plan/). "Non-commercial" and CC BY 4.0 do not fit together, since CC BY permits commercial use, so this label is unreliable.
- Free credits conflict: 200 per AIFreeAPI above, and 300 credits/15 models per [Meshy's blog](https://www.meshy.ai/blog/best-ai-tools-for-3d-game-assets).
- Rights: Tripo's help page reportedly says Tripo retains all rights to inputs and outputs from free users (Terms §5.2.1). I saw this only as a search snippet because the page returned 403 — [Tripo help](https://www.tripo3d.ai/help/privacy-policy/how-to-use-tripo-models-commercially)
- A single aggregator reports the top plan rising from $109.90 to $329.70 on 2026-08-24, which conflicts with the $110 Team price on the same site's free-plan page — [CostBench changelog](https://costbench.com/changelog/tripo-ai-price-increase-2026-08/)

**Rodin (Hyper3D, by Deemos)**
- Plans: Free $0; Creator $30/mo or $24/mo yearly (about 60 models, unlimited export for any purpose, unlimited private assets); Business $120/mo or $96/mo yearly (about 416 models, full API). Direct credits cost $1.50 each. Free tier: you can generate before confirming and pay only for results you keep, 10 private assets, export limited to legacy models, no smart low-poly, HD textures or baked normals. Commercial rights on Free are not stated — [Hyper3D pricing, read 2026-11-01](https://hyper3d.ai/pricing)
- Base Gen-2.5 generation costs 0.5 credit; Extreme-High adds 0.5; extreme-high texture adds 2.0 — [Rodin Gen-2.5 API spec](https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5)
- Terms §5(b) say Hyper3D "will not limit your use" of Rodin output, but §2 says export for commercial use varies by plan. The terms grant licences rather than state ownership; revision date not shown — [Hyper3D Terms](https://hyper3d.ai/legal/terms)
- Meshy's blog claims Rodin grants full commercial rights on all tiers — [Meshy blog](https://www.meshy.ai/blog/best-ai-tools-for-3d-game-assets). A competitor's claim; the official pricing page does not confirm it for Free.

**Hunyuan3D hosted**
- Professional API: 25 credits textured, 30 LowPoly, 15 untextured; MultiViewImages, EnablePBR and FaceCount each add 10; versions 3.0/3.1 add nothing; Smart Topology 50; UV unfold 10; format conversion 5. Express: 15 per call. 200 free credits on first activation, valid one year. Prepaid 1,000 credits for $15; postpaid $0.02 per credit. Failed tasks are not charged. Page updated 2026-05-08 — [Tencent Cloud billing](https://www.tencentcloud.com/document/product/1284/75281)
- Another Tencent page gives 20 credits per call in default mode, which conflicts with the 25 above — [Tencent Cloud doc](https://www.tencentcloud.com/document/product/1281/74121) (seen as a search snippet)
- Reseller price: $0.375 per v3 image-to-3D model on fal, updated August 2026 — [CostGoat](https://costgoat.com/pricing/hunyuan-3d)
- Individuals on the Global web platform get 20 free generations a day, as of the November 2025 launch — [Tencent](https://www.tencent.com/en-us/articles/2202235.html)
- Tencent's newest engines are hosted only; older versions can be self-hosted — [Cinevva](https://app.cinevva.com/guides/ai-3d-model-generators) (seen as a search snippet)

**Hitem3D**
- Hitem3D 3.0: 2048³ resolution, up to 5M faces, mesh-only or textured, 1-4 views — [Scenario, Oct 2026](https://help.scenario.com/en/articles/comparing-generative-3d-models/)
- A competitor-run guide says the free tier requires crediting "Generated with Hitem3D" on commercial products — [3D AI Studio](https://www.3daistudio.com/3d-generator-ai-comparison-alternatives-guide/hitem3d-alternative)

**Others**
- Luma: "We've officially Sunset Genie since January 1, 2026" (App Store notes for version 1.3.14), and no subscription tier includes 3D. Reported by a competitor, checked 2026-10-20 — [Meshy blog](https://www.meshy.ai/blog/best-ai-tools-for-3d-game-assets). CostBench still lists Genie plans at $30-300 — [CostBench](https://costbench.com/software/ai-3d-generation/genie-luma-labs/). I treat that listing as stale.
- Sloyd: Plus $15/mo or $12.50 billed annually; Guest exports only community models and is personal-use only; Plus adds commercial use. Checked 2026-10-20 — [Meshy blog](https://www.meshy.ai/blog/best-ai-tools-for-3d-game-assets)
- Sparc3D 2.1 (up to 2M faces, 1-4 views, watertight) has a Portrait variant aimed at faces — [Scenario](https://help.scenario.com/en/articles/comparing-generative-3d-models/)
- Prism 3.1 tied for first in one portrait test — [Vitalify](https://www.vitalify.asia/en/blog/ai-image-to-3d-generators-comparison)

### Inferences
- Paying for one month of Meshy Pro or Rodin Creator looks cheaper and legally cleaner than using any free tier for client work. Generate everything in that month and download it.
- Per-model cost barely matters at a handful of candles. Rights, privacy and output quality should decide this.
- Hunyuan's pay-as-you-go is the only option with no subscription, but the $15 minimum and Tencent Cloud signup may add friction.
- Sloyd is, from my background knowledge and not from a source here, mainly parametric, which would suit a sculpted one-off poorly. Kaedim is reported as far above this budget (see Gaps). Neither looks like a fit.

### Gaps
- Tripo's official pricing and terms could not be read (403). Confirm directly: free credits, licence wording, per-model credit cost.
- **Masterpiece X:** one search result said it shut down and rebranded to WorldEngen. I could not trace which page said it or confirm it with the vendor.
- **Kaedim:** search results gave conflicting prices, either trial $50, Indie $400/mo and Pro $1,200/mo, or $5-15 per asset. Neither is attributable, and my guessed pricing URL returned 404.
- **CSM/Cube:** no 2026 pricing confirmed; one comparison listed "$20/mo image-only" without clarity on the product. The fetch to csm.ai failed on DNS, which could be a tool problem and does not show the service is gone.
- **Hitem3D:** official per-model price not found. A summary listed paid tiers of 1,000/2,400/8,000 credits and $0.020 per API credit, but from a "prenotofficial" subdomain of a "Hi3D" site dated 2026-10-03, and I could not confirm Hi3D and Hitem3D are the same product.
- Whether "Hunyuan 3.5" exists for 3D: I found only 3.0/3.1, and Hy Image 3.5 is an image model.

## What output options does each give: GLB, triangle target, retopology or quads, PBR, texture resolution?

### Takeaway
Meshy documents this most fully and is the only one here where I confirmed a triangle target from 100 to 300,000, quad or triangle topology, GLB, and PBR with a normal map, all through one API. Rodin has the richest texture range and Tripo is reported to be strong on clean low-poly, but its limits are poorly confirmed.

### Cited Findings
- **Meshy API:** `target_polycount` 100-300,000 (default 30,000) with remeshing; `topology` triangle or quad-dominant; Smart Topology models are triangle-only, up to 15,000 (T2) or 30,000 (T2.5). `enable_pbr` adds metallic, roughness and normal maps. `texture_resolution` 2k, 4k, 8k (not on 6 Lite). `geometry_resolution` standard, 2k, 4k. Formats GLB, OBJ, FBX, STL, USDZ, 3MF. Meshy advises `should_remesh: false` for highest quality — [Meshy API docs](https://docs.meshy.ai/en/api/image-to-3d)
- **Meshy smart topology cost:** 5 credits (T2), 20 credits (T1) — [Meshy docs](https://docs.meshy.ai/en/webapp/pricing)
- **Rodin Gen-2.5:** five tiers from Extreme-Low to Extreme-High, the last also returning a mesh up to 10M faces. Textures 2K, or 4K with `uhd_texture`; 4K/8K with HighPack; 6K/12K at Extreme-High. GLB, FBX, USDZ named. `tier` must be sent explicitly or it falls back to a Gen-1/1.5 asset — [Rodin API spec](https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5)
- **Rodin plan gating:** smart low-poly, HD textures and baked normals from high-poly start at Creator; high-poly quads and full API at Business — [Hyper3D pricing](https://hyper3d.ai/pricing). Quad or triangle, PBR — [Scenario](https://help.scenario.com/en/articles/comparing-generative-3d-models/)
- **Tripo:** 3.1 has PBR and quad mesh with adjustable density; P2 goes up to 50,000 faces with optional quads — [Scenario](https://help.scenario.com/en/articles/comparing-generative-3d-models/). P1 goes up to 20K faces — [3D AI Studio, 2026-05-22](https://www.3daistudio.com/blog/rodin-2-5-vs-tripo-vs-hunyuan-3d-comparison). Up to 4K textures and retopology are listed in the free plan — [CostBench](https://www.costbench.com/software/ai-3d-generation/tripo-ai/free-plan/)
- **Hunyuan 3.1 Pro:** 1536 voxel grid, optional PBR; Multiview up to 1.5M faces — [Scenario](https://help.scenario.com/en/articles/comparing-generative-3d-models/). LowPoly, FaceCount and Smart Topology are paid add-ons — [Tencent billing](https://www.tencentcloud.com/document/product/1284/75281)
- **Face count in one test prompt:** Rodin 20,054, Meshy 17,438, Tripo 13,482. The lowest count won the geometry vote, and the author argues more faces does not mean better. Author works at Meshy — [HackerNoon, 2026-06-03](https://hackernoon.com/how-i-stress-tested-3-ai-3d-generators-on-the-same-inputs-what-the-numbers-actually-show)

### Inferences
- For a phone three.js page, the useful recipe is a mid-poly mesh (my judgement: tens of thousands of triangles) with a 2K normal map carrying the small relief. Keep maps at 2K, as 4K and 8K mostly cost download size and phone memory.
- Fine bumps on candles will likely live in the normal map rather than the mesh at phone budgets. So check whether the normal map is real relief or flat, not just the triangle count. Rodin's "baked normals from high-poly" and Meshy's PBR normal map are the features to test.
- Quads do not matter for a static model displayed in three.js, since GLB is triangulated for rendering anyway. Skip paying for them.

### Gaps
- Tripo's exact face-limit parameter, its export list, and texture resolution from official docs.
- Hunyuan's texture resolution and export format list.
- Whether Rodin's Creator web UI exposes the same texture options as the API spec.

## How do they handle fluffy or curly animal figurines and small faces?

### Takeaway
I found no independent side-by-side test on fur, curls, animal figurines or small faces, so nobody can honestly name a winner for this subject. Portrait evidence slightly favours Tripo for faces, and sources disagree on Rodin. A test with the client's real photo is the only reliable way to decide.

### Cited Findings
- **Closest test, one portrait through 7 tools with default settings and no cleanup:** Tripo P1 had strong facial resemblance, excellent textures and minor artifacts at hair edges. Prism 3.1 had excellent facial similarity and sharp textures, with occasional invented accessories. Hunyuan3D had faithful geometry but soft details and simple hair. Meshy 6 had simplified features and a slightly cartoonish look. Rodin 2.5 had a clean mesh but soft face and lost hair information. Trellis 2 had holes and broken hair strands. The author calls it initial rather than definitive; no affiliation is disclosed, and the blog belongs to a services firm. It covers a human portrait and older versions than today's Meshy 7.1 — [Vitalify, 2026-07-10](https://www.vitalify.asia/en/blog/ai-image-to-3d-generators-comparison)
- **Vendor-authored test (author is a Meshy Technical Artist), Meshy 6, Tripo v3.1 and Rodin Gen-2.5, April-May 2026:** Tripo first on untextured geometry (77.9% against Rodin single-view) and best topology. Rodin tracked small features such as teeth, jewelry and eye shape closely, but made errors such as wrong finger counts. Meshy tends to smooth fine surface detail, and that is an admission against its author's own product. Meshy won textured single-view output against Rodin at 83.9%. Hair was not covered. Sample size is not given and scoring was internal — [HackerNoon](https://hackernoon.com/how-i-stress-tested-3-ai-3d-generators-on-the-same-inputs-what-the-numbers-actually-show)
- Rodin's detail reputation conflicts: soft face in [Vitalify](https://www.vitalify.asia/en/blog/ai-image-to-3d-generators-comparison), close tracking of small features in [HackerNoon](https://hackernoon.com/how-i-stress-tested-3-ai-3d-generators-on-the-same-inputs-what-the-numbers-actually-show).
- An article titled as a Rodin/Tripo/Hunyuan comparison reports no tests at all and comes from a reseller, so it should not count as evidence — [3D AI Studio](https://www.3daistudio.com/blog/rodin-2-5-vs-tripo-vs-hunyuan-3d-comparison)
- Roundups disagree and several are vendor or affiliate content, for example [Medium](https://medium.com/ideas-with-wings/best-image-to-3d-tools-7eea7b05eb11) and [Neural4D](https://www.neural4d.com/features/neural4d-vs-tripo-vs-meshy-vs-rodin), neither of which I opened in full.

### Inferences
- Suggested bake-off: the same hardest candle photo through Tripo, Rodin and Hunyuan or Meshy. Judge three things: face recognisable, curls kept as relief rather than painted on, and back believable.
- Meshy's smoothing tendency is a specific risk for bumpy curly relief. Its 7.1 Ultra geometry tiers may have improved this, but I found no test confirming it.
- Texture can fake curls from the front, so judge the untextured mesh and the model under moving light.
- Wax is translucent and low-contrast, which may blur both the geometry and the face. This is my reasoning and nothing tested it.

### Gaps
- No test on fur, curls, animal figurines, small faces or candles. No Reddit threads or comparison videos surfaced in my searches, and I did not watch any video.
- A search snippet mentioned a photo-to-figurine test where Hunyuan3D V3, Trellis 2 and Tripo 2.5 each gave a complete figurine with a plausible back from one photo. I could not trace it to a page I opened, so it is unverified.
- No current test of Meshy 7.1, Tripo P2 or Hunyuan 3.1 on faces.

## How well does each handle one photo, and can it accept extra views?

### Takeaway
All shortlisted services accept a single photo, and all can take extra views if available. With one photo, the back is an invention whichever tool is used.

### Cited Findings
- Accepted views: Meshy 7.1 takes 1 or up to 4; Tripo 3.1 takes 1, Multi View up to 4; Rodin Gen-2.5 takes 1-5; Hunyuan 3.1 Pro takes 1, Multiview up to 8; Hitem3D 3.0 takes 1-4; Sparc3D 2.1 takes 1-4 — [Scenario, Oct 2026](https://help.scenario.com/en/articles/comparing-generative-3d-models/)
- Rodin's first image drives material generation — [Rodin API spec](https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5)
- Rodin's multi-image is "limited" on Free — [Hyper3D pricing](https://hyper3d.ai/pricing). Multi-view adds 10 credits on Hunyuan — [Tencent billing](https://www.tencentcloud.com/document/product/1284/75281)
- Single-view geometry: Tripo beat Rodin 77.9%, narrowing to 62.7% on multi-view (Meshy-authored) — [HackerNoon](https://hackernoon.com/how-i-stress-tested-3-ai-3d-generators-on-the-same-inputs-what-the-numbers-actually-show)

### Inferences
- Since the back of the model is invented, the page should open on the photographed side and could limit rotation, or the client should be told it is an approximation. Showing an invented back for a real product is an honesty question for the client to decide.
- If the seller can still reach the candle, one extra phone photo of the back would probably help more than any tool choice.

### Gaps
- No independent test of single-photo back quality on small handmade objects.

## What happens to the uploaded client photo, and are free-tier models public?

### Takeaway
Don't use a free tier for the client's photo without their knowledge: Tripo's is reported public, and Hitem3D's is reported public. Meshy's Terms allow training on uploads even on paid non-Enterprise plans unless you opt out by email. Rodin's "private" output has the strongest wording I found.

### Cited Findings
- **FLAG, Meshy, all non-Enterprise plans:** Meshy may use user content "to train, validate, test, or improve Services" unless you opt out by contacting support@meshy.ai (§2.9). Users also grant a worldwide licence to "reproduce, distribute, and otherwise use and display" user content (§3.2) — [Meshy Terms, 2026-09-19](https://www.meshy.ai/terms-of-use)
- **FLAG, Meshy Community:** posted content is public, output under CC0, images under CC BY-NC 4.0, with a "perpetual, irrevocable" licence to Meshy that survives termination (§3.3). Paid users can keep content private. The Terms do not say Free users must post publicly — [Meshy Terms](https://www.meshy.ai/terms-of-use). A third-party review reports Free assets go to the gallery by default — [search result, likely Toolradar, not opened](https://toolradar.com/tools/meshy/pricing), unconfirmed.
- **Meshy retention:** non-Enterprise API output is deleted 3 days after generation (§2.5) — [Meshy Terms](https://www.meshy.ai/terms-of-use)
- **FLAG, Tripo Free:** models reported as public — [AIFreeAPI](https://www.aifreeapi.com/en/posts/tripo-3d), [CostBench](https://www.costbench.com/software/ai-3d-generation/tripo-ai/free-plan/). The terms reportedly let Tripo retain rights in free users' inputs as well as outputs — [Tripo help, snippet only](https://www.tripo3d.ai/help/privacy-policy/how-to-use-tripo-models-commercially)
- **Rodin:** Output marked "private" is visible only to you, and Hyper3D says it will not use private Output beyond account display. Otherwise Prompts and Output may be used to "improve our services, and conduct and support research" (§5). Deletion after termination is at Hyper3D's option (§12) — [Hyper3D Terms](https://hyper3d.ai/legal/terms). Free includes 10 private assets — [Hyper3D pricing](https://hyper3d.ai/pricing)
- **Hunyuan:** I found no privacy or gallery terms for the Global platform.

### Inferences
- Whatever service is used, the seller should say yes to uploading her photo, and this takes one message.
- With Meshy, email the training opt-out before uploading. With Rodin, mark assets private and confirm uploaded input images get the same treatment, since §5 speaks of Prompts and Output.
- A cropped or background-removed photo reduces what is exposed, such as a home or a person in frame.
- A free-tier model with CC BY or CC0 terms could allow others to reuse a replica of the seller's design, which matters to a maker of original designs.

### Gaps
- Hyper3D's privacy policy (hyper3d.ai/legal/privacy) was not read, and the terms do not clearly treat uploaded images.
- Tripo's actual privacy policy and §5.2 text were unreadable. Tencent's Global platform terms were not found.
- Whether Meshy's opt-out covers past uploads, and how fast it applies.

## Is there an API for a recipe-style script?

### Takeaway
Yes for all the leaders, but Meshy gates it from Free and Rodin gates it to the $120 Business plan. Hunyuan through Tencent or fal, and Tripo through its own platform or fal, avoid a large subscription. For a handful of candles the web interface is enough, so an API is not needed at first.

### Cited Findings
- **Meshy:** `POST /openapi/v1/image-to-3d`, plus get, list, delete, SSE streaming and a Multi Image endpoint. Failed tasks are refunded. Download within 3 days — [Meshy API docs](https://docs.meshy.ai/en/api/image-to-3d), [Meshy Terms](https://www.meshy.ai/terms-of-use). Free has no API — [Meshy pricing](https://www.meshy.ai/pricing)
- **Rodin:** Bearer auth, multipart upload, asynchronous, JSON — [Hyper3D docs](https://docs.hyper3d.ai/). "Full API access" is listed under Business at $120/mo — [Hyper3D pricing](https://hyper3d.ai/pricing). Also reachable via [fal](https://fal.ai/models/fal-ai/hyper3d/rodin/api) (not priced here).
- **Hunyuan:** Tencent Cloud API, pay per credit — [Tencent billing](https://www.tencentcloud.com/document/product/1284/75281). fal route at $0.375 — [CostGoat](https://costgoat.com/pricing/hunyuan-3d)
- **Tripo:** an API exists, with an fal image-to-3D route exposing quad, PBR and texture options — [AIFreeAPI](https://www.aifreeapi.com/en/posts/tripo-3d). API call cost $0.18 for v3.1 — [HackerNoon](https://hackernoon.com/how-i-stress-tested-3-ai-3d-generators-on-the-same-inputs-what-the-numbers-actually-show)
- Meshy API calls measured at $0.20 and Rodin at $0.25 in the same Meshy-authored test — [HackerNoon](https://hackernoon.com/how-i-stress-tested-3-ai-3d-generators-on-the-same-inputs-what-the-numbers-actually-show)

### Inferences
- A reseller like fal gives one script access to several models with no subscription, which fits a bake-off. Licence and data terms would then include the reseller's as well, and I did not read those.
- Meshy has the easiest script to write, since every option needed for this job is a single documented parameter.

### Gaps
- Minimum Meshy plan for API access and API credit price. Tripo's platform docs returned only a title page. fal's terms and current per-model prices for Rodin and Tripo.

## Are they available and payable from Egypt?

### Takeaway
I could not confirm this for any service. Nothing found blocks Egypt, but PayPal on Meshy is not offered there, so an international-enabled credit card is the likely route, and a small test payment is the real check.

### Cited Findings
- Meshy PayPal is offered only in a listed set of countries, and Egypt is not on it — [Meshy help](https://intercom.help/meshy/en/articles/9991959-can-i-pay-with-paypal). Others go through Stripe (card, plus methods that vary by country) — [Meshy help](https://intercom.help/meshy/en/articles/9991955-what-payment-methods-do-you-offer)
- Meshy's Terms as fetched do not address restricted countries — [Meshy Terms](https://www.meshy.ai/terms-of-use). Hyper3D's do not list any, and make no representation of availability in any location (§8) — [Hyper3D Terms](https://hyper3d.ai/legal/terms)
- An undated forum user says Egyptian debit cards are disallowed for foreign currency and only credit cards work, which is anecdotal — [itch.io thread](https://itch.io/t/3408631/payment-payout-methods-for-restricted-countries), attribution from a search snippet that I did not open.

### Inferences
- Try the free signup first to confirm access. Then pay for one month with a card known to work abroad before committing work to that service.
- Egyptian bank rules on foreign-currency card spending change, so check with the card's bank.

### Gaps
- No official Egypt statement from Meshy, Tripo, Hyper3D or Tencent. No Tripo payment details. Tencent Cloud signup and billing from Egypt unconfirmed. Whether VAT or bank fees apply.
