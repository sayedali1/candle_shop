# Decisions: Candle page (practice client, test of the portfolio-coach skill)

One entry per decision, newest at the bottom. The vision table is in `brief/vision.md`.

## Client
- Name / niche: PLACEHOLDER brand (invented for the test); handmade candles
- Languages: Arabic (right-to-left layout from the start)
- Deadline / budget: none, this is a test
- Domain and hosting owner: n/a, test
- Content rights confirmed: n/a, test (no real photos or brand assets used)
- Project folder: D:\candle-page
- How the client sells: WhatsApp

## Goal
- Visitors who want a handmade candle for their home; the page teases the product with a 3D candle; the one action is to message the client on WhatsApp. (Confirmed by the user, pick A.)

## Progress
- [x] 0 Setup
- [x] 1 Visitors and the one goal
- [x] 2 Proof inventory
- [ ] 3 Vision board
- [ ] 4 Brand direction
- [ ] 5 Structure
- [ ] 6 Part by part (hero, about, proof, services, testimonials, location, booking)
- [ ] 7 Signature motion
- [ ] 8 Content swap
- [ ] 9 Quality check
- [ ] 10 Handover
- [ ] 11 Retrospective

## Log

### 2026-10-26 - Stage 0 setup answers
- My pick (before hearing Claude's view): answered directly
- Options considered: n/a
- Chosen: placeholder brand, handmade candles, Arabic, test deadline and budget, test ownership, folder D:\candle-page (user accepted the example path)
- Why: practice project to test the skill; the page features a 3D candle
- Open items / placeholders created: brand name, logo, all photos and copy are placeholders

### 2026-10-26 - Language: Arabic
- Consequence logged now so we don't forget: RTL layout, an Arabic wordmark and Arabic-capable fonts must be planned at the brand stage.

### 2026-10-26 - Stage 1 answers: visitors and goal
- My pick (before hearing Claude's view): answered directly
- Visitors: people buying handmade candles for home use
- Where they come from: "any" (no single channel chosen)
- Worries: "any" (no single worry chosen)
- How the client sells: WhatsApp
- The user's wording for the goal: "tease [the visitor] with our product"
- Note: "any" for source and worries gives no focus. Design for the widest case: phone first, WhatsApp as the single contact route. A teaser is an experience, not a visitor action, so the one action still needs the user's confirmation.
- Open items: confirm the one-action sentence

### 2026-10-26 - The one action: message on WhatsApp
- My pick (before hearing Claude's view): A, message on WhatsApp (no reason given)
- Options considered: A message on WhatsApp / B browse the collection / C something else
- Chosen: A
- Why (Claude's view, agrees): the client sells through WhatsApp, so the page's job is to start a conversation. The 3D candle teases; the button converts. Trade-off: no cart, so each candle's details must be visible on the page.
- Open items: a pre-filled WhatsApp message per candle (decide later); the client's WhatsApp number is a placeholder

### 2026-10-26 - Stage 2 proof inventory
- My pick (before hearing Claude's view): answered directly
- Candle photos: "get online ones or create them just for proof" (source not yet decided)
- Burning-candle clip: okay (placeholder is fine)
- Maker/workshop photos: no (not available)
- Customer reviews: no (not available)
- Honest numbers: okay (placeholder only, never shown as real)
- Prices: none given. Scents: "different types of candles" (placeholder list)
- WhatsApp number: okay (placeholder)
- Open items: decide the photo source (free-license online photos vs created placeholders)

### 2026-10-26 - Candle photo source: free-license online photos
- My pick (before hearing Claude's view): A, free-license online photos (no reason given)
- Options considered: A free-license online photos / B created placeholders
- Chosen: A
- Conditions: test use only, not for real publishing; each file's name, source and size is shown to the user and approved BEFORE any download; the source and license are recorded in `assets/CREDITS.md`
- Open items: choose and approve the actual photos

### 2026-10-26 - Photos downloaded (stage 2 closed)
- Approved by the user, then downloaded: candle-three-wood.jpg (226 KB), candle-pillars-dark-bands.jpg (224 KB), candle-lit-vase.jpg (313 KB)
- Two files were first over the 500 KB limit we agreed (643 KB and 587 KB), so they were re-downloaded smaller
- Viewed all three: they match their Unsplash descriptions
- Credits and license: assets/CREDITS.md. Test use only.

### 2026-10-26 - Skip ahead to the hero
- My pick (before hearing Claude's view): "skip everything for now, I just wanna see how we gonna make the hero page"
- Chosen: skip stages 3 (vision board), 4 (brand direction) and 5 (structure) for now and run the vision loop for the hero (stage 6, part 1)
- Consequence: the hero is built WITHOUT a brand direction (colors, type, voice). Treat it as a draft that will be restyled at stage 4. Stages 3 to 5 stay unticked.
- Skill note: the skill has no rule for skipping stages. It should say: log the skip, keep the stage unticked, and warn what the skip costs.

### 2026-10-27 - Hero reference: Apple AirPods Pro page
- My pick (before hearing Claude's view): learn from the Apple AirPods page; borrow "big centered 3D product" and "moves as you scroll"
- Options considered: Evermore London (full-bleed photo, one headline, one button), Apple AirPods Pro (3D product as hero). Earl of East loaded but its hero image stayed blank in the browser pane; 54Celsius did not open; neither was described.
- Chosen: Apple AirPods Pro, borrowing the two points above. Not borrowed: quiet plain background, small label + big headline.
- Open items: how to make the 3D candle (code, free 3D model file, or photo-based)

### 2026-10-27 - How to make the 3D candle: free 3D model file
- My pick (before hearing Claude's view): use a free 3D model file
- Options considered: draw it in code (Three.js shapes) / free 3D model file (GLB) / fake 3D from the photos
- Chosen: free 3D model file
- Conditions: the license must allow free use (CC0 or CC-BY, with credit recorded); the file name, source and size are shown and approved BEFORE any download; keep the model small for phones; keep a flat fallback (photo) if 3D fails or motion is reduced
- Open items: pick and approve the actual model

### 2026-10-28 - Real-looking candle: build it in code first
- My pick (before hearing Claude's view): rejected two free model files (low-poly jar, wooden candlestick); wants a real, Apple-style candle; then said "okay do that" to building it by code
- Options considered: turntable photos / scan a real candle / AI image-to-3D / Blender render / draw it in code (Three.js)
- Chosen: draw it in code as a first prototype; judge how real it looks, then decide whether a scan or turntable photos are needed
- Conditions: flat photo fallback if 3D fails; reduced-motion respected; phone-friendly (capped pixel ratio, scene pauses off-screen)
- Open items: if the code look is not real enough, choose a scan / turntable / AI route. Hero look (dark background, colors, type) is a DRAFT until stage 4.

### 2026-10-28 - Hero draft built (stage 6, part 1)
- Built: index.html, style.css, candle.js in D:\candle-page. Arabic RTL, a jar candle drawn in code with Three.js (pinned CDN version), flame shader + glow + warm light, scroll turns the candle and moves the camera, headline fades to a second line, one WhatsApp button, photo fallback if 3D fails.
- Checked: desktop-size and phone-size views in the browser pane; no console errors; no sideways scroll; fallback photo shows when 3D is off.
- Not checked: a real phone, real scroll feel (the pane runs animation slowly), slow connections.
- Fixes during the check: moved the candle lower so the headline does not cover it; stopped the zoom earlier so the button does not cover the jar base.
- Placeholders: brand name, headline and second line, WhatsApp number (0000000000), colors and dark background (brand stage skipped).
- Open: user confirms "does this match what you picked from the reference?" and judges whether the code candle looks real enough (else scan / turntable / AI route).

### 2026-10-28 - Verdict on the code candle: not real enough
- My pick (before hearing Claude's view): "It doesn't look real enough. Let's try the scan or turntable route."
- Chosen: leave the code-drawn candle as a stand-in; move to a real-object route (scan OR turntable photos). Which one is still to decide.
- Needs from the user: a real candle and a phone for capture (any candle at home is fine for the test)
- Open items: pick scan vs turntable; capture the candle; the code flame/glow can be reused on top of either

### 2026-10-28 - Real-object route: turntable photos
- My pick (before hearing Claude's view): turntable photos; the user has a candle to film
- Options considered: turntable photos / scan
- Chosen: turntable photos, scrubbed by scroll (frames drawn on a canvas)
- Conditions: candle filmed UNLIT (the code flame and glow go on top); plain dark or neutral background; same distance and light for every frame; target about 60-72 frames, WebP, about 1-2 MB total; keep the code-drawn candle as the fallback if frames fail to load
- Open items: the user films the candle; frames go in assets/turntable/; then build the scroll player and re-check on phone

### 2026-10-28 - Real-object route changed: Luma Genie 3D model
- My pick (before hearing Claude's view): the user has no candle to film, so tries Luma Genie (AI 3D) and will generate the model and send it
- Options considered: Luma video (frames) / Luma Genie 3D model / Luma Capture scan (needs a real candle, ruled out)
- Chosen: Luma Genie 3D model, saved as assets/models/candle-luma.glb
- Conditions: inspect the model before using it (shape, texture, weight); keep it small for phones (aim under about 5 MB, shrink if needed); keep the code flame and glow on top; keep the code-drawn candle as the fallback; record Luma's terms and the plan used in assets/CREDITS.md. Free-plan output is likely non-commercial, so this is test use only until the terms are checked.
- This replaces the turntable entry above (no candle to film).
- Open items: the user generates and sends the model; I load it into the existing scene and re-check on phone

### 2026-10-28 - No Luma credits: improve the code candle (free route)
- My pick (before hearing Claude's view): no credits for Luma, so look for free options; chose "better code candle" from four free routes
- Options considered: free image-to-3D tools (Upsampler, Pocket 3D AI, Hugging Face Spaces) / free Sketchfab download (needs the user's account) / better code candle / real photo with scroll motion (not 3D)
- Chosen: better code candle (free, no outside tools)
- Plan: studio-style environment reflections on the glass, glowing wax around the flame, a paper label with Arabic placeholder text, a two-layer flame, soft bloom on desktop only, grounded shadow and a glossy surface; phones skip the bloom
- Honest limit: it will still read as a render, not a photograph. If the user judges it not real enough again, the free fallback routes above remain open.
- This replaces the Luma Genie entry above (no credits).

### 2026-10-28 - Code candle version 2 built
- Built: studio-style reflections on the glass, wax that glows around the wick, a paper label with Arabic placeholder text, a two-layer flame, a soft shadow, a glossy dark table, a vignette, and bloom on desktop only (phones skip it).
- Tuning found while checking: first bloom was far too strong (washed out the jar), so strength went down and the threshold up; the flame was lost in glass haze, so glass opacity, glow size and light were lowered and flame brightness raised; a bright streak on the table was removed by making the table rougher.
- Checked: desktop-size and phone-size views, no console errors, no sideways scroll, label turns with the candle.
- Not checked: a real phone, real scroll feel, slow connections, other browsers.
- Open: the user judges whether this is real enough. If not, the free fallbacks remain: free image-to-3D tool, Sketchfab free download, or a real photo with scroll motion.

### 2026-10-28 - Verdict on version 2: keep the code candle, make it more polished, decorated and alive
- My pick (before hearing Claude's view): "urs is okay but need to be more polish, more decorated, more alive" (chosen instead of any of the other free routes)
- Chosen: keep improving the code candle. Other free routes stay available if this still is not real enough.
- Plan: DECORATED = wooden coaster, cinnamon sticks tied with twine, a lavender sprig, a few petals, twine on the jar. ALIVE = drifting dust that glints near the flame, the flame leaning and gusting, a gentle idle sway of the camera and candle, a slow fade-in. POLISHED = film grain, a soft pulse on the button, entrance animation for the headline.
- Honest limit: still a render. Decor is simple shapes, so it will look stylized next to a photo.

### 2026-10-28 - Code candle version 3 built (decorated, alive, polished)
- Built: wooden coaster, cinnamon sticks tied with twine, a lavender sprig, scattered petals, twine on the jar; drifting dust that brightens near the flame; flame that leans and gusts; gentle idle sway; slow canvas fade-in; film grain; headline entrance; soft pulse on the WhatsApp button.
- Checked: desktop-size and phone-size views, no console errors, no sideways scroll. Layout nudged so the button does not cover the decoration; twine toned down.
- Not checked: a real phone, real scroll feel, slow connections, battery use on phones (more objects and particles now).
- Known weak spots: the coaster's wood grain looks radial, not straight; decoration is simple shapes, so it is stylized next to a photo.
- Open: the user judges again.

### 2026-10-28 - Polish round 2: flame, glass and wax
- My pick (before hearing Claude's view): flame; glass and wax (not chosen this round: decoration, depth and mood)
- Plan: FLAME = smoother teardrop shape, a faint outer halo, a flickering tip, and on desktop a subtle heat shimmer above it. GLASS = on desktop, real refracting glass (transmission) instead of a see-through shell; phones keep the light shell. WAX = the glow now flickers together with the flame.
- Cost: desktop gets heavier (glass refraction + shimmer pass); phones are unchanged.

### 2026-10-28 - Polish round 2 built: flame, glass and wax
- Built: smoother teardrop flame with a faint halo and a faster-flickering tip; heat shimmer above the flame (desktop); real refracting glass on desktop (phones keep the light see-through shell); wax glow that flickers with the flame.
- Problems found and fixed while checking: the refracting glass first hid the flame behind it (depth writing, fixed with depthWrite off); the wax and flame blew out under bloom (light moved above the flame, wax glow, halo and bloom turned down).
- Checked: desktop-size and phone-size views, no console errors, no sideways scroll.
- Not checked: the heat shimmer is subtle and I could not judge it from a still screenshot; a real phone; GPU load and battery on real devices (desktop now renders a refraction pass plus bloom plus a shimmer pass).
- Open: the user judges again.

### 2026-10-28 - Hero accepted (stage 6, part 1 done)
- My pick (before hearing Claude's view): "Yes, this is good. Move on to the next part of the page."
- Chosen: the code-drawn candle hero (version 3 with polish round 2) is accepted for the test. The look is still a draft until the brand stage, which was skipped.
- Next: stage 6, part 2: About. Constraint from stage 2: no maker photos and no reviews are available, so the About section cannot use invented people, stories or numbers.

### 2026-10-28 - About section: reference and borrow
- My pick (before hearing Claude's view): learn from Candle Atelier; borrow a story timeline, a materials section and a one-line promise
- Options considered: Evermore London About page (seen), Candle Atelier on Wakilni (seen, marketplace page), a third was not found (Earl of East page was a 404; an Arabic search found no store About page)
- Chosen: as above. Note: the timeline and materials patterns come from Evermore; the one-line promise from Candle Atelier.
- Claude's view (agrees, one change): make the timeline the steps of making a candle, not dated years, because we have no brand history and the skill forbids inventing facts.
- Placeholders created: the promise line, the four steps, and the three materials texts are all marked "نص تجريبي"; the client must supply real facts.

### 2026-10-28 - About section built (stage 6, part 2)
- Built: index.html section #about, page.js (fade-up on scroll), styles in style.css. A one-line promise, four steps of making a candle (numbered timeline, right-to-left), and three material cards (wax, wick, scent). Every text is marked "نص تجريبي" and a "نص تجريبي" tag sits by the heading.
- Checked: desktop-size and phone-size views, no console errors, no sideways scroll, order reads right-to-left.
- Not checked: a real phone, Arabic proofreading by a native reader (the placeholder wording is mine), long text lengths.
- Open: the user confirms "does this match what you picked from the reference?"; the real facts must come from the client.
- Note: a stale browser cache hid the new section once; testing needs a cache-busting query like ?v=2.

### 2026-10-28 - About story: a scroll story told with the 3D candle (replaces the four static steps)
- My pick (before hearing Claude's view): "okay good do it" after the outline; when asked (add a new section / replace the four steps / leave About), chose "Replace the four steps"
- Chosen: the four numbered steps become a scroll story. The candle puts its flame out, drains its wax, loses its wick and label, then builds itself again step by step and relights. Five beats, five short Arabic lines, all marked "نص تجريبي" (placeholder).
- Claude's view (agrees, with a change): run the story inside the hero's sticky stage so it uses the same candle and ONE canvas (no second 3D scene, so no extra GPU cost). Trade-off: the hero scroll gets about 4 screens longer, and the About promise line and material cards come after it.
- The old four static steps stay in the HTML, hidden, and show only if 3D fails (the no-3D fallback). They are the same placeholder text.
- Placeholders created: the five story lines and their tags. The client must supply the real steps.
- Note: this chat edited candle.js, index.html and style.css after the other chat built About (about 14:00). The other chat must re-read these files before editing.

### 2026-10-28 - About story built (stage 6, part 2, story version)
- Built: the candle story inside the hero's sticky stage (same candle, one canvas). Five beats after the hero turn: (1) the flame goes out, the wax drains, the label and the decorations go; "تبدأ بجرة فارغة" (2) the wick grows; "فتيل واحد في المنتصف" (3) a stream of wax is poured and the wax rises; "شمع يُسكب ببطء" (4) cinnamon, lavender and petals arrive; "ثم العطر" (5) the label returns and the flame relights; "وتُضاء". Five progress dots; every line is marked "نص تجريبي".
- Files changed: candle.js (story logic, a wick that runs the full height, a wax stream, a soft light for the empty jar, shimmer off when the flame is out), index.html (story lines, dots; the four old steps now `steps-fallback`), style.css (extra scroll length via --story: 420vh desktop, 340vh phone, 0 when 3D is off).
- Problems found and fixed: the empty jar was too dark (added a soft light that only shines while the flame is out); the heat shimmer kept distorting the picture over an unlit jar (shimmer now scales with the flame); the wax stream cut through the headline (shorter, with a faded top); the old hero line lingered on a fast scroll (it now hides the moment the story starts).
- Checked: desktop-size (800x520) and phone-size (375x812) views, stepping through every beat; the story start looks identical to the accepted hero; no console errors; no sideways scroll; the About promise and material cards follow the story; with 3D off the story scroll is 0, the photo shows and the four steps appear in About.
- Not checked: a real phone (speed, battery); reduced-motion mode; the Arabic wording (mine, placeholder); slow scrolling by hand (the preview only draws frames when a screenshot is taken, so motion was judged from stills at each beat).
- Open: the user judges the story; the real steps and wording must come from the client. The other chat must re-read candle.js, index.html and style.css before editing.

### 2026-10-28 - About accepted (stage 6, part 2 done)
- My pick (before hearing Claude's view): "Yes, the story is good. Move on to the next part of the page."
- Chosen: the scroll story (five beats) plus the promise line and material cards are accepted for the test. All text is still placeholder.
- Next: stage 6, part 3: Proof (photos, albums, certificates). Constraints from stage 2: no maker photos, no reviews, no real numbers, no certificates; only 3 free-license Unsplash photos (test use only).

### 2026-10-28 - Proof section: reference and borrow
- My pick (before hearing Claude's view): learn from P.F. Candle Co.; borrow only the "lit-candle photo" (a real-looking photo of lit candles)
- Options considered: Evermore collection grid (plain product grid), Evermore product page (facts as proof), P.F. Candle Co. (type tabs, lit-candle hero photo). All three were opened and seen. Not chosen: plain grid, facts as proof, type tabs.
- Chosen: the lit-candle photo, as above.
- Claude's view (agrees, with two cautions): the 3D hero is a render, so a real photo adds the "this exists in real life" feeling the render cannot. Cautions: (1) our only lit photo is a free-license stock image, so it proves nothing about this client's candles and is tagged "صورة تجريبية"; the client's own photo must replace it; (2) the facts-as-proof pattern (wax, burn time, scent notes) is the strongest real proof a handmade candle can show, so it should come back once the client supplies the facts.
- Placeholders created: the caption line and the test photo.

### 2026-10-28 - Proof section built (stage 6, part 3)
- Built: index.html section #proof after About: one full-width photo of a lit candle (assets/photos/candle-lit-vase.jpg), a "صورة تجريبية" tag, the heading "كما تبدو في بيتك" (how it looks in your home) and a placeholder line. page.js: the photo zooms out slowly as it scrolls past (still when motion is reduced). style.css: the photo fades into the dark page above and below.
- Problem found and fixed: the caption first sat on top of the candle and its flame; it moved to the top of the photo.
- Checked: desktop-size (800x520) and phone-size (375x812) views; the flame and candle are clear; no sideways scroll; no console errors; the test-image credit shows in the footer.
- Not checked: a real phone; reduced-motion mode; how it looks with the client's own photo (the crop is tuned to this one photo: object-position 50% 72%).
- Open: the user confirms "does this match what you picked from the reference?"; the photo must be replaced by the client's own before launch. The stronger proof (wax, burn time, scent notes) is waiting on real client facts.

### 2026-10-28 - Opening index.html directly showed a blank page (found by the user)
- What the user saw: nothing, after opening index.html by double-click.
- Cause: the 3D candle is a module script (with an import map to a CDN). Browsers block module scripts on file://, so candle.js never started. Nothing switched the page to the photo, so the hero stayed dark and empty.
- Fix: (1) page.js: if the 3D has not started after 4 seconds, the page shows the flat photo and the plain steps; (2) candle.js: if the 3D starts late, it switches the fallback off; (3) a new open-page.bat starts a tiny local server and opens http://localhost:8000.
- Checked: a test page whose 3D script was missing showed the photo, the headline, the WhatsApp button and the steps after 4 s; the normal page through a server still shows the 3D candle and no fallback. The test page was deleted.
- Not checked: opening open-page.bat on the user's machine; a real double-click on index.html.
- Note: a slow connection may briefly show the photo before the 3D takes over.

### 2026-10-28 - Structure change: the candle lives behind the whole page and burns down as you scroll
- My pick (before hearing Claude's view), in the user's words: not just a candle that moves while you scroll; it should go down and finish as you scroll the whole page, go through everything and sit in the background; add a story, light it, and when we scroll it melts, and the next section is the products.
- Options considered: (A) keep the candle only in the hero / (B) the candle is a fixed full-page background and its life is the scroll: lit through the story, burning lower behind About and the photo, then out, then the products section takes over.
- Chosen: B.
- Claude's view (agrees, with cautions): scroll = the candle's life is a strong story and it ties the page together. Cautions: (1) text on top of the candle must stay readable, so on wide screens the candle slides to the left side and is dimmed behind content, and on phones it stays centered, smaller and dimmer; (2) "melts" for a jar candle means the wax level drops, the wick shortens, the flame sinks and goes out with a wisp of smoke, then the candle fades away; it is not liquid dripping; (3) an always-on full-screen 3D scene costs battery, so drawing stops once the candle has faded out at the products; (4) the full-width proof photo covers the candle while it passes; (5) the Products section starts as a clearly marked placeholder (the products need their own reference round and real client facts).
- Placeholders created: the Products section (names, text and photos are test content).
- Open: the user judges the journey; the products vision loop is next.

### 2026-10-28 - Candle journey built: one background candle that burns down as you scroll
- Built: the 3D scene is now ONE fixed layer behind the whole page (index.html: .candle-bg and .film; candle.js: the scene is driven by the scroll over the whole page). The journey: hero turn, then the story (it empties, rebuilds, lights), then a real lit-candle photo, then About with the candle sliding to the left and burning down (wax level drops, the wick burns down with it, the flame sinks), the flame goes out with a wisp of smoke, the candle fades away, and the new Products section begins on a plain dark page. After the fade the scene stops drawing (battery).
- Also built: a placeholder Products section (three cards with free-licence test photos, "نص تجريبي" tags, a WhatsApp order button each with a pre-filled Arabic message; the WhatsApp number is still 0000000000).
- Changes along the way: the proof photo moved to right after the story (it would have hidden the burn-out, which is the moment you asked for); About got a minimum height so the burn is gradual (170vh); on wide screens the candle's sideways position is computed from the visible width so it is never clipped; on phones it stays centered, smaller and dimmer behind the text; `?still` in the address shows the scene without smoothing, for checking an exact scroll position.
- Problems found and fixed: the product photos rendered at full pixel height (an HTML height attribute beat the aspect ratio); the candle was clipped at the left edge; the proof photo hid the burn-out.
- Checked (desktop 800x520 and phone 375x812, in ?still mode): the story end, About with the candle on the left, the mid-burn, the late burn (almost no wax, tiny flame), the products arrival (candle gone, canvas opacity 0), phone legibility, no sideways scroll, no console errors; the normal mode loads and the hero looks as before.
- Not checked: a real phone (speed and battery with an always-on full-screen scene); slow scrolling by hand at real speed; the smoke wisp (too brief to catch in stills); reduced-motion mode; the no-3D fallback after this change.
- Open: the user judges the journey; the Products section needs its own reference round (vision loop) and the client's real range; the Unsplash photos are test-only.

### 2026-10-28 - Change: no story in the hero; the candle just appears and lights itself
- My pick (before hearing Claude's view), in the user's words: we don't need the story in the hero; it should start in the hero but just appear and light, then when we scroll it does what it does now.
- Options considered: (a) keep the five-beat story / (b) remove it and keep the rest of the journey. (The user's first message was cut off; the change was chosen from a short list plus their own words.)
- Chosen: (b). This REVERSES the earlier decision "About story replaces the four static steps".
- Done: the story (five lines, dots, the extra 420vh of scroll and all its code, the wax stream and the empty-jar logic) is removed from the hero, the page and candle.js. The hero is back to 260vh. New light-up intro: the candle fades in unlit, then about a second later the flame grows and the wax glow and light come up (about 3 seconds). The four "how a candle is made" steps are visible in About again (they had been hidden behind the story). The rest of the journey is unchanged: turn, slide to the side, burn down behind the page, flame out, fade, products. The About gap that gave the burn room is gone, because the steps now fill About.
- Backup of the files before this change is outside the project (scratchpad backup_story), in case the story is wanted again.
- Checked (desktop 800x520 and phone 375x812): the intro (normal mode: candle appears, flame lights and reaches full size; confirmed with a temporary debug line, since removed), About with the steps and the candle burning behind, the end of the burn and the hand-off to the products, phone legibility, no sideways scroll, no console errors.
- Not checked: a real phone; slow scrolling by hand at real speed; the no-3D fallback after this change; the flame-lighting moment at real speed (judged from stills).
- Open: the user judges the new hero; the Products section still needs its reference round.

### 2026-10-28 - Hero accepted (stage 6, part 1 final)
- My pick (before hearing Claude's view): "Yes, this is the hero I wanted."
- Chosen: the hero is a candle that fades in unlit and lights itself; the rest of the candle journey (turn, slide aside, burn down behind the page, flame out, fade) is accepted too.
- Next: stage 6, part 4: Products (the "services and prices" part). Constraints from stage 2: no prices, no reviews, no real range yet; ordering is by WhatsApp; only 3 free-license test photos.

### 2026-10-28 - Products section: reference and borrow
- My pick (before hearing Claude's view): learn from P.F. Candle Co.; borrow only the "type tabs"
- Options considered (all opened and seen): Evermore London grid, P.F. Candle Co. (type tabs, best-seller badges), Candle Atelier on Wakilni (plain 3-column grid with prices), Evermore product page (facts line). Keap's site loaded blank in the browser pane and was not described. A search found no candle shop that orders through WhatsApp.
- Chosen: type tabs, as above. Not chosen: quiet grid, simple card, facts line.
- Claude's view (agrees, with three cautions): tabs earn their place once the range has more than about six candles; with only a few they add a click and hide products. (1) the default tab shows everything ("الكل") so nobody misses a candle; (2) without JavaScript every card must still show; (3) if the client has only one type, the tabs should not appear at all. The type names must come from the client; the facts line (wax, burn time, scent) is still the strongest real proof once she supplies it.
- Placeholders created: three type names, six product names and their lines (all "نص تجريبي"); no prices, because we have none.

### 2026-10-28 - Products section built (stage 6, part 4)
- Built: the Products section after the candle fades out. Heading "اختر شمعتك" with a "نص تجريبي" tag; a row of pill tabs ("الكل" plus three placeholder types) in the page's own amber style; six placeholder cards (test photo with a "صورة تجريبية" tag, name, one placeholder line, a WhatsApp order button with a pre-filled Arabic message). Choosing a tab shows only that type's cards (two each); "الكل" shows all six. Arrow keys, Home and End move between tabs and follow the visual order in right-to-left. Without JavaScript the tabs stay hidden and every card shows. No prices (none exist).
- Files: index.html (the section), style.css (tabs, hidden cards, a short fade-in), page.js (the tab logic). A backup of the three files from before this step is outside the project (scratchpad backup_tabs).
- Checked (through the page): all six cards at first; type two shows 2 cards, type three 2, all shows 6; the selected state follows; keyboard moves the right way in right-to-left; no console errors. Looked at desktop-size (800x520) and phone-size (375x812): the tabs read clearly; on the phone the tab row scrolls sideways inside itself, buttons are 45 px tall, the page does not scroll sideways.
- Not checked: a real phone; a screen reader; how it looks at 1280 px and wider (the 3-column grid was not viewed in a screenshot at that width); what the section looks like with the client's real photos and a longer range.
- Open: the user confirms "does this match what you picked from the reference?". Placeholders to replace: type names, product names and lines, the photos (test only), the WhatsApp number (0000000000). If the client has only one type, the tab row should be removed.

### 2026-10-28 - Feedback: About, the photo and Products feel separate from the candle behind them
- My pick (before hearing Claude's view), chosen from four options (all four): (1) candle light on the content, (2) no hard edges, (3) bigger candle presence with the text beside it, (4) the candle does not vanish at the products.
- Claude's read of the cause: a dark veil over About, a solid full-width photo band, a flat solid block under Products, outlined box cards, and no shared light.
- Claude's view (agrees with all four, one caution): the glow must stay subtle so the text stays readable; on phones there is no room for text beside the candle, so there it stays centered, dimmer, and the text keeps a light veil. A candle that never leaves means the 3D scene keeps running; it will draw at half the frames once it is at rest.
- Plan: a warm glow (a CSS layer centred on the flame, flickering with it) over the content; no veil or solid bands; cards become soft glass; the photo's edges fade into the scene; on wide screens About becomes two columns (candle on the left, text on the right) and the candle is larger; at the products the candle shrinks into the bottom-left corner, unlit, with a faint ember.

### 2026-10-28 - Connected the sections to the candle (built)
- Built: (1) a warm glow layer (.candle-light) centred on the flame, position and strength computed in candle.js and flickering with the flame, lights the text and cards near the candle; (2) no hard edges: the About veil and the Products solid block are gone, cards are soft glass without outlines, the photo's edges fade into the scene (mask) and the dark bands around it are gone; (3) on wide screens About is two columns: the candle is larger and takes the left half, the text sits on the right; (4) at the products the candle shrinks into the bottom-left corner, unlit, dim, with a faint pulsing ember, and keeps drawing at half the frames. A soft text shadow helps readability over the candle.
- Checked (desktop 1000x640, phone 375x812, ?still): About with the candle large on the left and the text on the right; the photo with the 3D candle showing through its soft edge; the glass cards; the candle resting at the bottom-left at the end of the page; on the phone the candle stays centered behind About, the text readable; no console errors; no sideways scroll.
- Not checked: a real phone; the glow's flicker at real speed; wider than 1000 px; the battery cost of the candle now drawing until the end of the page (half the frames at rest).
- Caveat: while the product cards are on screen the resting candle is mostly behind them; it is clearly visible at the bottom of the page.
- Backup of the files before this step is outside the project (scratchpad backup_connect).
- Open: the user judges whether the page now feels like one scene.

### 2026-10-28 - One-scene polish accepted; next part is FAQ only
- My pick (before hearing Claude's view): "Yes, it feels like one scene now."
- Chosen: the connected look (candle light on content, soft glass, no hard edges, larger candle beside the About text, the candle resting in the corner) is accepted.
- Next: stage 6, part 5: Testimonials and FAQ. Constraint from stage 2: no customer reviews exist, and the skill forbids invented testimonials, so this part is the FAQ only; testimonials wait for real ones.

### 2026-10-28 - FAQ section: reference and borrow
- My pick (before hearing Claude's view): borrow "one quiet panel" (Evermore), "product questions first" and "topic groups" (both P.F. Candle Co.)
- Options considered (opened and seen): Evermore FAQ page (quiet panel, shipping questions), P.F. Candle Co. FAQ page (topic groups, product questions). A fourth idea, ordering questions (WhatsApp, delivery, payment), was offered as our own and not chosen.
- Chosen: the three above. Testimonials are skipped because no real reviews exist.
- Claude's view (agrees, one caution): product questions are the right ones to answer first for a handmade candle. Caution: the side list for topic groups is worth it only with a longer FAQ; with six questions it is heavy, so it shows on wide screens only and is hidden on phones. Questions about ordering, delivery and payment may still be the most useful ones for a WhatsApp-only shop; add them later if the client wants.
- Placeholders created: the three topic names, six questions and all answers (answers say "نص تجريبي").

### 2026-10-28 - FAQ section built (stage 6, part 5)
- Built: section #faq after Products. Heading "ما الذي تودّ معرفته؟" with a "نص تجريبي" tag; one soft glass panel with three topic groups (المكوّنات والأمان, العناية والاستخدام, العطور), two questions each, as native open/close rows (details/summary) with a small round amber arrow; a sticky side list that jumps between topics on wide screens (hidden on phones). Every answer is the placeholder "نص تجريبي: يُكتب هنا الجواب من صاحبة المتجر." No testimonials (no real reviews).
- Files: index.html (the section), style.css (the FAQ styles). No script needed. Backup before this step: scratchpad backup_faq.
- Checked: 6 questions in 3 groups, rows open and close, 3 side-list links; wide (1000x640): panel, groups and side list read well, an open row shows its answer; phone (375x812): panel full width, side list hidden, rows 59 px tall, no sideways scroll; no console errors.
- Not checked: a real phone; a screen reader; keyboard use of the side list and rows (rows are native, so keyboard works by default, but I did not try it); the side list highlighting the current topic (it does not).
- Open: the user confirms it matches what they picked; the real questions and answers must come from the client; ordering, delivery and payment questions were not added (offered, not chosen).

### 2026-10-28 - Products redo: no cards; "a shelf you walk along"
- My pick (before hearing Claude's view), in the user's words: the cards feel off and still; wants something that is not cards, something new, catchy, a different idea. Chosen from four sketches: idea 4, "a shelf you walk along" (one long shelf of candles you swipe along; the middle one lights up as it passes). "Something that cuddles itself" was clarified as "cozy and soft".
- Options considered: (1) light the one you want, (2) the candle changes, (3) a menu of names, (4) a shelf you walk along. Ideas were Claude's own, not from references; a reference round for the chosen idea follows.
- Chosen: 4. This REPLACES the type-tab card grid (the type tabs, picked earlier from P.F. Candle Co., go away with the cards).
- Reference round done: one reference seen (the "Elevated Carousel" demo: lifted middle item, neighbours peeking in). Other search results were component pages or documentation and were not described.
- Borrow: one row you swipe along with the middle item as the focus. Do not copy: its photo cards, boxes, colors, labels or code. Our version: a "shelf" of candles with no boxes; the candle nearest the middle is lit (brighter, lifted, warm glow, and the room's light moves to it) and shows its name and order button; the others are dim.
- Claude's view (agrees, with cautions): this fits the cozy, soft brief and the candle scene better than cards. Cautions: (1) the order button must stay one tap on the lit candle; (2) a horizontal row needs arrow buttons and keyboard support because a mouse wheel does not scroll sideways; (3) all six items are stock photos twice, so the real photos of the client's candles matter even more here; (4) only the lit candle shows its text, so without JavaScript every item shows its own text and button.

### 2026-10-28 - Products redone as a shelf (built)
- Built: the Products section is now a shelf you walk along, no cards. Six candle photos with soft glowing edges on a thin wooden line, in a row that snaps so one rests in the middle. The candle in the middle is "lit": bright, lifted, with a warm glow, and the room's light (a second radial glow in the page's light layer) moves to it; the others are dim. Only the lit one shows its tag, name, placeholder line and WhatsApp order button. Round soft arrow buttons (46 px), arrow keys (right-to-left aware), and a tap on a neighbour brings it to the middle. Without JavaScript every item shows its own text and button.
- Removed: the card grid and the type tabs (and their code).
- Files: index.html (section), style.css (shelf; the card and tab rules removed), page.js (shelf logic; the tab logic removed). Backup before this step: scratchpad backup_shelf.
- Problems found and fixed: the photos' soft-edge mask did not fade fully at the sides, so hard vertical edges showed; fixed. The first test seemed to show the lit candle never changing; the cause was the preview pane, which only runs animation frames while a screenshot is taken. With frames flushed, Next moved the lit candle from the first to the second and the page light switched on.
- Checked (wide 1000x640 and phone 375x812): six items, the lit one follows the arrows, the page light turns on while the shelf is on screen, no console errors, no sideways scroll; the lit candle, the dim neighbours, the shelf line and the order button look right; the resting 3D candle shows behind.
- Not checked: a real finger swipe and mouse-wheel feel (scroll-snap and smoothness); a real phone; a screen reader; wider than 1000 px; the real photos (the six items are three stock photos twice).
- Open: the user judges the shelf. The real candles and photos must come from the client.

### 2026-10-28 - Question: why did the shelf switch from the 3D candle to photos? Decision: a shelf of 3D candles
- The user asked why the products went from the idea of the candle to pictures of candles.
- Claude's answer: the sketch showed drawn candle shapes, but when building, the project only had three stock photos and no candle variants, so photos were used as stand-ins. That was not flagged as a departure from the 3D concept; it should have been asked first. It also made the shelf look unrelated to the rest of the page.
- My pick (before hearing Claude's view): the user chose "3D candles" (out of: 3D candles / 3D lit candle with photos behind / keep photos for now).
- Chosen: the shelf is built from the same 3D candle in variants (wax color, jar size, label name); the middle one is lit and the others are unlit; the photos stay only as the fallback if 3D cannot run.
- Claude's view (agrees, with cautions): this is consistent with the concept. Cautions: (1) these are our stylized candles, not the client's real ones; her real photos still belong in the proof section; (2) more 3D on a phone, so the variants use a simple glass look (no refraction); (3) the variants (colors, sizes, names) are placeholders until the client lists her real candles.
- The earlier "candle rests in the corner" behaviour is replaced: at the Products the old candle dissolves and the shelf candles appear, with the flame moving to the middle one.

- Built (2026-10-28): six 3D candle variants (wax color, label paper, glass tint, jar size, twine) drawn on the page's canvas over the shelf slots; the middle one is lit and the flame moves between them (goes out on one, lights the next); the unlit ones are dimmer; the room light follows the lit flame. The burnt-out hero candle sinks away as the shelf arrives. The photos stay only as the fallback when 3D cannot run.
- Checked: desktop 1000x640 and phone 375x812 with ?still (candles sit on the shelf line, labels readable, lit one lifted, hero unchanged, no console errors). Not checked: finger swipe feel, real phone speed and battery, the flame hand-off while scrolling by finger, screen reader, the moment the old jar overlaps the first shelf candle on a phone (looks a little crowded for a second).
- Placeholders: colors, sizes and names of the six candles until the client lists her real candles.

### 2026-10-28 - Question: all shelf candles look the same. Decision: rebuild each from a different reference photo
- The user asked for 5-6 real candle photos to copy the look of, and later added a decorated jar (flowery wrap label, crystals on top) as a seventh.
- Photos: 3 existing + 3 new free Unsplash photos downloaded with the user's approval (ceramic cups with wooden wicks, beeswax hug figures, ribbed glass votive; credits in assets/CREDITS.md). The Unsplash+ (paid) ribbed/sculpted candles were skipped. The decorated jar comes from a listing image the user pasted; it was used only as inspiration (own pattern, own text), not copied.
- Built: seven shapes in candle.js (`shelfShapes`): beeswax tealight with a spiral, cream pillar with a dark band, white pillar, speckled ceramic cup with a flat wooden wick (wide flat flame), two hugging beeswax figures, ribbed amber glass votive (glows when lit), jar in a flowery wrap with crystals. The photos are the no-3D fallback in the same order.
- Checked: desktop 1000x640 (all seven lit one by one) and phone 375x812 (ceramic cup); no console errors. Not checked: real phone speed with seven textured shapes, finger swipe, the speckles and flowers are faint when a candle is unlit (they look better lit).
- Placeholders: every shape, color and text until the client lists her real candles. Names stay "الشمعة n".

### 2026-10-28 - Question: can new candle photos become 3D models by themselves? Decision: Way A, recipe files + a Candle Lab + a skill
- Options: (A) recipe files that Claude writes from each photo and the page builds; (B) an AI photo-to-3D service. The user chose A, with realistic detail, finish and lighting, as a skill and a tool.
- Claude's view: A fits (free, light on phones, lit flame and glow work); B gives wrong glass and wax and heavy files.
- Built: `candle-builder.js` (turns a recipe into a 3D candle: wax, matte, glaze, glass, paper, wood; ribs, spirals, stones, wicks, flame shape, contact shadow), `recipes/*.json` (the seven candles, now data instead of code; `recipes/index.json` is the shelf order), `lab.html` + `lab.js` (the Candle Lab: one candle next to the reference photo, lit/unlit, three lightings, front/3-4/top views, live recipe editor, save picture). The shelf in candle.js now loads the recipes. New user-level skill `candle-from-photo` (SKILL.md, recipe-format, polish checklist, templates).
- Checked: shelf still renders from recipes (ceramic cup); Lab loads recipes, shows the floral jar lit and the ceramic cup unlit in studio light next to its photo; no console errors. Not checked: the other five recipes in the Lab, phone-size Lab, the skill on a brand-new photo end to end.
- Known gaps: the Lab flame code is a copy of the page's flame (two copies to keep in step); no drips or lids yet.

### 2026-10-28 - Skill test: candle-from-photo on a new photo
- Photo (viewed on Unsplash, not downloaded): "A melted candle in an ornate silver candlestick" by Babak Eshaghian, https://unsplash.com/photos/a-melted-candle-in-an-ornate-silver-candlestick-kVpLr9U6F4s. Recipe: recipes/08-drippy-candlestick.json (not on the shelf; it is in index.json after the seven, which the shelf ignores).
- Result: two Lab rounds. Added a `metal` material kind and a `drips` shape to the builder because the photo needed them; silver was black until `env` was raised. Proportions, colours and finish are close; the pierced base pattern, the flared cup and irregular drips are not.
- Skill updated with these lessons. Not checked: lit state and the other lightings for this recipe.

### 2026-10-28 - Eighth candle and no photo flash on reload
- Added the drippy candlestick (recipe 08) as the eighth shelf item; its no-3D fallback reuses an existing photo (no photo of it was downloaded).
- Question: does a reload show the photo before the 3D candles? Yes, before this change: photos stayed visible until the first 3D frame. Fixed: with JavaScript on, the stand-in photos are hidden from the start and only show when 3D cannot run (the `no3d` fallback). Checked: photo hidden, candle 8 shown lit. Not checked: a slow network (the shelf is empty for a moment until the 3D is ready, which is by design).

### 2026-10-28 - Question: what should show when a candle is pressed? Decision: core + extras
- Research (vision.md row "Product detail"): Evermore, Antique Candle Co., P.F. Candle Co., a web search of retailer pages. Options: core only / core + extras. The user chose core + extras.
- Claude's view: agrees; customers cannot touch or smell the candle online, so notes, ingredients and care carry the sale. Reviews, badges and price are left out (no data; WhatsApp only).
- Built: a "details" button on each shelf item and pressing the lit candle opens a glass panel (left side on desktop in RTL, bottom sheet on phones) with: name and scent line, four facts (size, burn time, wax, wick), scent notes in three layers, ingredients, first burn, care and safety, what happens if it arrives damaged, and the WhatsApp order button. Content is in products.json (one entry per candle plus common care text); Esc, the close button or a press outside closes it.
- Placeholders: every fact is test text or "٠٠" until the client supplies hers. The care steps are common safety advice and the damaged-in-delivery line is a placeholder policy; the client must confirm both.
- Checked: desktop 1000x640 (opens from the button, Esc closes, no console errors) and phone 375x812 (opens by pressing the candle). Not checked: the phone page lifting the candle above the sheet (smooth scroll did not run in the test pane), screen reader, keyboard focus order, a long text overflow.

### 2026-10-28 - Polish the detail panel and add real photos that match each 3D candle
- The user asked for a more polished look and for real photos matching the 3D models.
- Photos: seven of the eight candles now show their matching real photo at the top of the panel (credits in assets/CREDITS.md; the eighth, the drippy candlestick, was downloaded with this request: Babak Eshaghian, Unsplash, 96 KB). Candle 7 (the flowery jar) has no photo: the only close match was a pasted listing image (not ours to use) and the free ones found had another brand's name on the jars.
- Look: photo header that fades into the panel with a slow settle, icon cards for the four facts, scent notes as three graded orbs, flame-shaped bullets for care, a soft callout for the delivery promise, a fixed order button at the bottom, content rising in one by one (off with reduced motion).
- Checked: desktop 1000x640 (candle with a photo, scrolled body, order bar stays) and phone 375x812 (candle 8), no console errors. Not checked: candle 7 without a photo, very long texts, keyboard focus order, screen reader.
- Placeholders: photos are free test images (tagged "صورة تجريبية"); replace with the client's own before launch.

- Candle 7 decision: the user chose no photo for it until the client's real photo exists. Checked: its panel opens cleanly without a photo (title first, no empty gap), desktop 1000x640.

### 2026-10-28 - Rework: "كما تبدو في بيتك" photo section and the About section
- The user did not like the photo section, and said About still needed work ("does not fit the candle behind"; chosen from: too much text / looks plain / weak headline / does not fit the candle).
- Proof: the 3D jar ghosted through the stock photo and the title sat on top of it. Options: remove / quiet 3D moment / small framed photos. The user chose: remove (my recommendation too; the shelf and panel already show candles). Removed the section, its styles and its scroll code.
- About: the four steps now hang on a fuse: a thin line with a small ember that travels down it as you scroll, and each step lights up when the ember reaches it (like the flame burning down the candle beside it); the number circles and the glass material boxes are gone (three quiet lines instead); the headline gets a soft warm glow. Without JavaScript every step stays visible.
- Checked: desktop 1000x640 and phone 375x812 (steps lit in order, ember at the right place, no console errors). Not checked: slow finger scroll feel, screen reader (the ember is hidden from it), reduced motion in a real browser.
- Not changed (not chosen): headline wording, amount of text.

### 2026-10-28 - Fix: About headline broke into one or two words per line
- The user sent a phone screenshot: the headline "شمعة صغيرة تضيء تفاصيل يومك" wrapped one word per line and the step texts were in a narrow column, so lines felt disconnected.
- Cause (most likely): the headline width was set in `ch` units (16-18ch) with a big font, which gets very narrow when the phone enlarges text on its own or the font is wide. I could not reproduce the exact screenshot (at 368, 700 and 1000 px wide it was fine), so I fixed the causes I could see.
- Fix: headline width no longer in `ch` (full column), smaller font, `text-wrap: balance` so lines carry 2-3 words; the step text wraps in even lines; phones are told not to enlarge text (`text-size-adjust: 100%`); no sideways overflow (`overflow-x: clip`); wide screens give the text column more room (40% left padding instead of 44%).
- Checked: 368, 700 and 1000 px wide: headline in 2-3 balanced lines. Not checked: the user's real phone (a reload there is the real test).

- Second fix for the About headline (the user said it was still broken): the title is now two phrases ("شمعة صغيرة" and "تضيء تفاصيل يومك"), each kept on one line, so lines break only between phrases; the font size follows the screen width so both phrases fit. Checked by loading the page at 300, 320, 360, 368, 400, 480, 560, 700, 800, 900, 1000 and 1200 px wide: always 1-2 lines, never a lone word. The old local server also let browsers keep stale files (the test itself showed a stale page once), so serve.py (no-cache) replaced it in open-page.bat and the CSS link got ?v=4. Still unverified on the user's own screen (no new screenshot arrived).

### 2026-10-28 - Brand: the user could not imagine the three directions from a picture
- The user said they could not choose because they could not imagine it. Claude's answer: stop showing pictures and let them see it on the real page. Built a temporary preview switch: open the page with ?brand=1 (warm hearth: same dark brown and amber, Naskh titles) or ?brand=3 (midnight ritual: plum backdrop in the 3D scene and page, rose-gold buttons and tags, Kufi titles); two buttons at the bottom left flip between them (they only show when the address has ?brand=).
- Direction 2 (soft linen) is not in the preview: it needs a daylight version of the 3D scene (the flame glow is additive light and would wash out), which is the most work. It can be shown later if the user asks.
- Checked: both looks load at 1000x640 (fonts, colours, plum backdrop, switch buttons). Not checked: every section and the phone in each look, the detail panel in look 1.
- Placeholders: name and taglines are still test text. The preview code (head script, CSS block at the end of style.css, block at the end of page.js, plum switch in candle.js) is removed once a direction is chosen.

### 2026-10-28 - Brand chosen: 1, warm hearth
- After comparing both looks on the real page, the user chose 1 (warm hearth): dark brown, amber and cream, classic Naskh (Amiri) titles, Cairo for reading. Applied for real and the preview was removed (head script, ?brand switch, plum backdrop, extra font).
- Still placeholders: the brand name, wordmark and taglines (all "علامة تجريبية" and test text); the logo mark (not designed yet).
- Server note: two old `python -m http.server` copies kept serving cached files (the test page showed an old stylesheet). They were stopped and `serve.py` (no-cache) now serves port 8000; `open-page.bat` starts it the same way. Close any old black window of the earlier launcher before opening the bat again.
- Checked: titles load in Amiri on desktop 1000x640 (hero and About), no preview left in the files. Not checked: the shelf, detail panel and phone in the final look (they use the same colours as before; only the title letters changed).

### 2026-10-28 - Real phone test: set up, waiting for the user's numbers
- Claude cannot hold the user's phone, so it built the test: a `?perf` readout (fps, slowest frame, draw calls, triangles, textures, pixel ratio, canvas size) and a 5-minute checklist in brief/phone-test.md. The phone opens http://192.168.1.2:8000/?perf on the same Wi-Fi (this computer's address at the time; open-page.bat must be running).
- Baseline seen in the test browser at 375x812 (hero, phone mode): 46 draw calls, about 19.8k triangles, 11 textures, 60 geometries, pixel ratio 1.5, canvas 562x1218. The fps shown there is not meaningful (the test browser only draws while taking a picture).
- Also: script and builder URLs got ?v=2 so browsers do not keep an old copy.
- Not done: the actual measurements on a real phone (waiting for the user's numbers).

### 2026-10-28 - Impeccable init: PRODUCT.md written
- Impeccable (design skill) was loaded and found no product record, so `init` ran. The user confirmed three things: the buyer (Arabic speakers buying for their home or as a gift, phone first, ordering by WhatsApp), that this is a test project (placeholders everywhere, no real client), and the position (every candle is a lit 3D model on a shelf, rebuilt from a real photo; handmade is the craft).
- Written: PRODUCT.md at the project root (facts only; marked open decisions). Not written: DESIGN.md (not requested), the image-generation workflow setting (no image generator available here) and live-mode config (not set up).

### 2026-10-28 - Impeccable critique (24/32, Good) and the fixes the user chose: all five issues, phone legibility first
- Critique: dual-agent (design review + detector/browser). 0 P0, 3 P1, 2 P2. The detector's 4 glow hits were judged false positives (flame light, About ember). Snapshot: .impeccable/critique/.
- Fixed:
  1. Phone About legibility: a soft dark veil (fades at the edges) behind the text on phones, unlit steps 34% -> 62%, body text brighter.
  2. Detail sheet on phones: facts first, photo after them. Pacing: hero 260vh -> 200vh, About 170vh -> 140vh, less blank space above the shelf (slot shape and candle size adjusted), neighbour candles brighter (40% -> 62% at rest), a position count ("١ / ٨") between the arrows.
  3. Dialog: page behind is inert while the panel is open (Tab cannot leave it), aria-modal, the lit candle announced after a swipe settles ("الشمعة ٣، ٣ / ٨"), tags 11.5px -> 13px, caption text brighter.
  4. Ending: a closing block ("جاهز تختار شمعتك؟" with a WhatsApp button; text is a placeholder), footer no longer shows a file path, header button now says "اطلب عبر واتساب", small buttons at least 44px tall.
  5. Polish: header gradient stronger so the wordmark stays readable, drawn SVG chevrons instead of text arrows.
- Checked: phone 375x812 (About, shelf, panel facts-first, closing), desktop 1000x640 (shelf), Escape closes and restores the page, no sideways overflow, no tap target under 44px, tags 13.1px, no console errors. Not checked: real phone, a screen reader reading the live announcement, keyboard Tab order end to end, tablet widths.
- Not changed: the kicker above headings ("من نحن"), the warm-hearth palette, the panel photo itself (it is still a stand-in photo, now lower on phones). Re-run the critique to see the new score.

### 2026-10-28 - Critique run 2 (24/32 again, P1 3 -> 2): second round of fixes, all five chosen
- Why the score did not move: round 1 made the phone About text readable with a heavy veil, which hid the candle, and left the desktop unlit steps at 34% opacity (measured 1.9:1).
- Fixed:
  1. About balance: unlit steps now 76% opacity (about 4.9:1, passes AA) on every width, the phone veil is lighter (62%), and on phones the candle rises and shrinks a little while About is read.
  2. Ending: a drawn, softly flickering flame above "جاهز تختار شمعتك؟" with a warm light behind it (still when motion is reduced); copy names the next step ("اكتب لنا اسم الشمعة التي أعجبتك على واتساب", placeholder text) and the button says "اكتب لنا على واتساب".
  3. Header: the button says only "واتساب" (its accessible name stays the full phrase) and steps aside while the hero button, the shelf or the closing button is on screen, so one filled order button shows at a time.
  4. Phone shelf: slots 56vw wide with a tighter gap so the neighbouring candle peeks in at the side. A first-load "nudge" was tried and removed: it left the shelf on the second candle.
  5. Detail sheet: the close button is pinned in its own header row (drawn X), and ingredients, first burn and care are folded into three accordions; the notes and the delivery promise stay visible.
- Checked: phone 375x812 (About, shelf with peek, sheet with pinned close and accordions, closing flame, header hidden at the bottom), desktop 1000x640 (About, header visible there), no console errors. Not checked: a real phone, how the flame reads on a bright phone screen, a screen reader on the accordions, the header fade timing in a real browser.
- Not changed: the placeholder photo in the sheet (does not match the 3D candle), the kicker above headings, the header wordmark overlapping the About headline at the top edge.

### 2026-10-28 - A shop with many candles: many shelves (decided in a side question, NOT yet built)
- The question: does the 3D shelf (8 candles built from tiny recipe files) work for a shop with many choices?
- Claude's first view: a single shelf works for about 8-12 candles; beyond that it needs a plain grid with filters (scent, size, price) and a shelf that only builds the nearest 5-7 candles. Not tested past 8 candles or on a real phone.
- Options shown: many shelves (one per collection) / one shelf + filter grid / shelves plus a search/filter bar
- My pick (before hearing Claude's view): many shelves
- Chosen: many shelves, one per collection (for example floral, woody, gifts)
- Claude's view (agrees, with limits): keep to about 3-5 collections of 6-8 candles each; build and draw the 3D candles of the shelf on screen only (and maybe the next one), the others stay as photos until near; it gives browse-by-mood but no search, so a filter bar can be added later if the client has many more candles. Each new 3D candle still needs a photo and a small recipe file.
- Open items: ask the client how many candles and collections she has; add the collection data to products.json; make the shelf code work for several shelves (the current code assumes one shelf with id "shelf"); test with 30 fake products on a phone-size view.
- Note: the main session is editing the same files, so the build should be done there, or after saying so.

### 2026-10-28 - Critique run 3 (20/32, three P1): third round of fixes, all five chosen
- Why 20/32: a different reviewer scored harder, and it raised issues no earlier run did (hidden buying facts, no trust cue, blank first load). One reviewer claim (focus lost after Esc) was disproved by the browser check. Trend 24 -> 24 -> 20, not like-for-like.
- Fixed:
  1. Buying path: each shelf card now shows a facts line under the name (size, burn time, scent family; placeholder values from products.json), the dimmed candles keep a readable name under their slot, and "التفاصيل" is a quiet underlined link so the order button is the only filled one.
  2. First load on a phone: the headline now arrives at once (delays cut from .5 s and .75 s to .1 s and .2 s), a small flame holds the screen while the 3D candle loads, and the header order button starts hidden so the hero shows one filled button.
  3. Trust and ending: a new placeholder block "من يصنع شموعك" (a dashed photo frame, delivery, payment, exchange lines) and a placeholder reply-time line above the closing button. NOT done: reusing the 3D candle at the ending (it would keep drawing a heavy scene below the shelf on phones); the drawn flame stays.
  4. Access: a `<main>` landmark and a skip link, larger and brighter sheet labels, phone unlit steps 84% with brighter text, candle names reachable as text under each slot.
  5. About: the materials block is cut (wax, wick and scent are in each candle's sheet), About is shorter (110vh), the header has a firmer band so the wordmark no longer collides with text.
- Checked: phone 375x812 (first load flame then headline and candle, shelf card with facts line and quiet link, maker block, closing flame), desktop 1000x640 (shelf with neighbour name, firm header), no console errors. Not checked: a real phone, a screen reader on the new landmarks and names, real pixel contrast of phone steps over the brightest flame area.
- Placeholders to be replaced by the client: the facts line values, maker text and photo, delivery, payment and exchange lines, reply time.

### 2026-10-28 - Many shelves BUILT (the decision above, done in the side session)
- Built: products.json now has `collections` (3 test collections: 8 + 6 + 6 = 20 candles). page.js builds one shelf per collection (own title, arrows, count, lit candle) and waits on `window.shelvesReady`; candle.js waits on the same promise, finds every shelf, builds each 3D candle only when its slot comes near the screen, and gives the one flame to the shelf nearest the middle of the screen. Every shelf lights its own centred candle. The detail sheet and the WhatsApp message follow the tapped card. Without the data, the one static shelf in index.html still works.
- Test data: candle number n uses product n % 8 (texts, photo) and recipe n % 8 (3D shape), so the 20 test candles repeat 8 designs. Real shops: one entry per product in products.json, one recipe file per new 3D shape.
- Stress test (temporary, then restored): 5 collections x 8 = 40 candles. After visiting shelves 1, 3 and 5 only 6 of the 40 candles were built. `?perf` now also shows "shelf candles built X of Y".
- Checked: phone 375x812 (shelf 1, shelf 2 flame hand-over, detail sheet from shelf 2, 40-candle test) and desktop 1000x680; no console errors; no sideways scroll.
- Not checked: a real phone (the preview pane does not run animation while idle, so fps readouts there are meaningless), tablet widths, keyboard order across several shelves, a screen reader reading several shelves, shelves with fewer than 3 candles.
- Known limits: no search or filter (many shelves is for browsing by mood); the test candles repeat 8 designs; a candle's first build can cause a small hitch the first time it is reached.
- Backup of the files as they were before this change: scratchpad folder `backup-before-many-shelves` (this session only).
- The main session edits the same files; it should reload page.js, candle.js, products.json and style.css before editing them.

### 2026-10-28 - Shelves: empty right side and no arrows (user screenshot of the multi-shelf page)
- The user showed the new page (shelves by collection: الأزهار, الأخشاب, الهدايا, one shared order bar) and said the right side was empty and there were no arrows to go left and right.
- Causes found: (1) the page itself could slide sideways: something in the shelves made the page 1720 px wide at a 1240 px window, so scrolling to a candle moved the whole page and left the right side empty; (2) each row began half a screen from the edge (padding so that the first candle could reach the middle); (3) the shared-bar redesign removed the arrows.
- Fixed: the products section clips sideways overflow (page width back to the window width, no sideways slide); rows start at the edge of the screen with a small gutter (a short row stays centred); every shelf has its own round arrows at its two ends (disabled at the ends); the lit candle can now be the first or the last one (lit = nearest the middle, or the first or last when the shelf is scrolled all the way), and a candle picked with an arrow or a press stays lit until the visitor scrolls the shelf themselves.
- Checked: 1240x780 (first candle at the right edge, arrows step through all 8 candles and the last one lights, page width stays 1225), 375x812 (rows from the edge, 40 px arrows, no sideways slide). Not checked: a real phone swipe, a mouse wheel over the shelf, the rows with 19-20 candles beyond the 8 sample photos.
- Not found: which part of the shelves widened the page. The clip hides it; the cause itself (probably an element inside the shelves) is not identified.

### 2026-10-28 - Impeccable polish pass (no open critique backlog: the file had changed since run 3)
- Evidence: page width at 375, 768 and 1024 (no sideways overflow), phone 375x812 and tablet 768x1000 walks, console clean, no tap target under 40 px outside the sheet.
- Fixed: the shelf hint no longer says the lit candle is "in the middle" (it is the first one until you scroll): now "مرّر على الرفّ أو استخدم الأسهم لتختار شمعة"; the shared order bar only shows while a shelf is on screen (it used to appear early over the end of About); the visible candle names under the shelves are hidden from screen readers (the hidden heading already names each candle, so it was read twice); the order bar's facts line balances its wrap.
- Cleaned: dead styles for the removed materials block and for the first version of the shelves (about 20 lines).
- Not changed: the kicker above headings, the drawn flame at the ending, placeholder text and photos, the unknown element that used to widen the page (the clip hides it).
- Critique snapshot: not closed (none was current).

### 2026-10-28 - Question: is it right to leave the hero as just the candle? Decision: keep it, add a shelf button and a scroll cue
- The user asked whether a hero with only the candle is right. Claude's answer: mostly yes (the candle is the product and the idea), but the hero was thin in three ways: no cue that there is more below, an order button before any product, and it is long. The user chose to do the first two (not the shorter hero).
- Done: the hero button now says "شاهد الشموع" and scrolls smoothly to the shelf (WhatsApp ordering starts from a candle on the shelf; the header WhatsApp button stays hidden over the hero, so the hero has one action); a small "مرّر" cue with a thin line and a travelling light sits above the button, appears after the candle lights and fades out as soon as the visitor scrolls (still under reduced motion; smooth scrolling is off under reduced motion).
- Checked: phone 375x812 (hero with cue and new button, tapping the button lands on the shelf, header button hidden), desktop 1240x780 (hero), no console errors. Not checked: a real phone, the cue over very short windows, the button's smooth scroll on slower phones.
- Not done: shortening the 200vh hero (offered, not chosen); the shelf peeking at the edge of the hero.

### 2026-10-28 - Impeccable animate: a small motion round for the page's one idea, light
- Motion plan: focal moment = the ending flame lights itself when you arrive (the hero ignition and burn-down already existed and stay); continuity = the order bar's name and facts swap with a short fade and rise when the selected candle changes; feedback = buttons and arrows press in for 100 ms, accordions in the detail sheet open smoothly (where the browser supports animating to auto height); budget = every looping animation (closing flame, About ember, scroll cue, loading flame) is paused while off screen.
- Reduced motion: the page's existing rule removes all animation and transitions, so the ending flame simply appears lit and nothing moves; the name still changes in the bar.
- Checked: desktop 1240x780 (ending flame goes from dark to lit on arrival, order bar swap class applies on each change, accordion properties supported, no console errors). Not checked: how the accordion height animation looks (supported in this browser, not watched), a real phone, battery with the sleeping loops.
- Not added on purpose: more scroll reveals, hover lifts, parallax.

### 2026-10-28 - Impeccable optimize: measure first, then the biggest cost
- Measured (phone-size window 375x812, local server, shop of 20 candles): at load 24 requests and 1511 KB, of which about 1.1 MB were the stand-in photos (all seven shelf photos and the hero fallback photo) that are only needed when 3D cannot run; three.js 196 KB (from the CDN, needed); candle.js, builder, page.js and style.css about 110 KB; at the shelf the scene had 77 draw calls, 42k triangles, 14 textures and 118 geometries with 15 of the 20 candles built (candles are built lazily, a change another session had already made).
- Fixed: the stand-in photos are no longer downloaded unless 3D cannot run (the HTML keeps them in `data-src`, and page.js loads them when the page falls back); one font request instead of two, and only the Amiri weight that is used; an early start for the Three.js download (modulepreload); the font and recipe downloads start at the beginning of the scene code instead of behind it; candles of the same recipe share geometry and textures in the builder (geometries 118 -> 106 for the same 15 candles; textures unchanged at 14); the local server now serves files in parallel like a real host.
- After: 20 requests and 510 KB at load (-66% bytes, 4 fewer requests); the shelf scene has the same draw calls and triangles; the fallback path was checked (photos load when the page falls back).
- Not measured: real frame rate and battery (the test window only draws while taking a picture, so its fps and times are not meaningful), load time on a slow connection, a real phone.
- Not done: nothing was lowered in quality; the desktop pixel ratio of 2 with bloom was left alone (it is the look); candle count beyond 20 is untested.

### 2026-10-28 - Second look at the 3D models: a contact sheet and one polish round
- The user asked to go through the 3D models again and get the best design. Built `sheet.html` (all recipes in one picture, lit or unlit, with the source photo under each) so the whole set can be judged together, and compared each model with its photo.
- Changed (recipes only, no builder change): 1 tealight: brighter, glossy honey, thicker raised spiral, a lip on the clear cup. 2 pillar with band: warmer cream, lower and wider dark band. 3 white pillar: taller and narrower (it was squat), a longer wick. 5 hugging figures: slimmer bodies with rounder heads, paler beeswax. 6 votive: deeper ribs. 8 drippy candlestick: a wider candle and thicker, more irregular drips. 4 ceramic cup and 7 floral jar were left as they were (4 already matched its photo; 7 has no photo).
- Checked: the contact sheet lit and unlit, and the shelf at 1240x780 (new shapes show). Not checked: the pierced base of the candlestick, the flared cup, real-phone look, the candles in the detail sheet photo comparison.
- Skill updated: the contact sheet and the new recipes are in the candle-from-photo templates.

### 2026-10-28 - Hero candle: "we have better" -> light, shadow and materials upgrade (hero first)
- The user felt the models, including the hero candle, could be better. Options offered: light and shadow, materials, flame and glow, scene and camera; where: hero first or hero and shelf. Chosen: light and shadow + materials, hero first.
- Done (candle.js, hero only): desktop gets soft real shadows (a very wide spot light replaces the point light on desktop, one shadow pass; the candle base, coaster, cinnamon, lavender and petals cast and receive; the glass and flame layers do not); every device gets a warm pool of light on the table that follows the flame; the glass rim is rounded instead of razor-sharp; the wax climbs the glass at its edge and dips into a melt pool; the paper label has fibre grain and one corner lifting from the glass; the coaster has grain relief. Phones keep the painted contact shadow (no shadow map).
- Checked: desktop-size windows (900x600 and 1240x780) and a phone-size window render with no console errors; the pool of light, shadows and rim show. NOT checked closely: the finer material details (the test screenshots are only 411 px wide, too small to judge them), real frame rate with the shadow pass on a laptop, the phone look on a real device.
- Not done: flame and glow, scene and camera, the same upgrades for the shelf candles.

## Skill gaps found while testing (for the stage 11 review)
- A stand-in that changes the concept (photos instead of 3D) must be flagged before it is built, not discovered by the user afterwards.
- A preview that only runs animation frames while a screenshot is taken makes frame-driven features look broken. Test them by flushing frames (act, screenshot, then read), and say so in the log.
- The skill has no rule for reversing an earlier decision: log the reversal, say what it brings back (here the four steps), and keep a backup of what is removed.
- A background scene that must be visible at a specific moment needs the content above it to leave room: check what covers the scene at the key moment (here the full-width photo hid the burn-out).
- A check switch (like ?still) that removes smoothing makes scroll-driven scenes checkable; the skill could recommend adding one early.
- The skill has no "how will the client or user open this page?" check. A page that needs a server must say so, and must not show a blank screen without one.
- A scroll story must be checked beat by beat, not only at the start and end. The skill has no step for that.
- The skill has no rule for working in a folder that another chat is editing: check file times and read the log first, and confirm which chat edits.
- A browser preview can lag behind scroll-driven animation; each beat needed several frames before judging.
- Effects that stack (glass refraction, bloom, additive flame) interact: each change needed a look-and-adjust round. The skill has no step for "test the effects together at the end".
- The skill does not say how to tune a visual effect when the first attempt looks wrong (here: bloom). It took three rounds of look-and-adjust.
- The skill does not say how to preview a page that needs a local server (ES modules do not run from file://).
- No 3D checks yet: phone speed, flat fallback, model size, reduced motion. This build added them by hand.
- No rule yet for demo/test content: free-license photos, crediting, and asking before any download.
- The skill has no 3D-specific checks yet: phone performance, a flat fallback if 3D fails, model/file size, reduced motion.

## Open placeholders
- [ ] Brand name and logo (placeholder)
- [x] How the client sells: WhatsApp
- [x] One action confirmed: message on WhatsApp
- [x] Candle photos (test): 3 Unsplash photos in assets/photos, credits in assets/CREDITS.md. Photo `candle-pillars-dark-bands.jpg` shows readable "2025" labels in the background; avoid using it large or crop it.
- [ ] Burning-candle clip (placeholder)
- [ ] Types of candles / scents list (placeholder)
- [ ] Prices (not available)
- [ ] Numbers (placeholder, not shown as real)
- [ ] WhatsApp number (placeholder)
- [ ] Maker photos and customer reviews: not available, so no About-the-maker or reviews section unless invented, which the skill forbids

## Retrospective (stage 11)
- Time per stage:
- What the client delayed:
- To make reusable:
- Price vs effort:
