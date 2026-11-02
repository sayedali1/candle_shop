# 13 knot pair: what comes from the photo, what is hidden

Photo: brief/ref-knot.jpg. Build: `python tools/gen_knot.py`. The method: the photo gives numbers only (sizes, rows, tilts, a count, a colour). No photo pixels go on the candle.

## Camera
- Fitted from the rims (tools/fit_knot_camera.py, every rim within 2 px): close and a little above the tall top. The tall top rim is nearly edge-on (8 px deep) while both feet show wide curves (29 and 27 px deep). Pixel sizes turn into units with the depth at each height.

## Numbers read from the photo (20 px grid: tools/fit/grid-tall.png, grid-short.png)
- Body outline: a left and right edge at the 8-9 rows where each outline turns (top, waist above the knot, below the knot, foot). A smooth curve runs through them.
- Lean: a straight line through the middles of all body rows (the tall's flared rim alone would tip it). Foot: the last row is the front rim, standing on the shelf.
- Size check: the 3D outline projected back into the photo matches the photo's edges within about 2-5 px on almost every row (tools/fit/knot-sheet-11.png).
- Knot: two flat bands per candle, no more (tools/fit/knots-zoom.png). Each band's middle row at the left and right edge (so its tilt) and its thickness; the knot's full width. The bands touch: the tall's upper band turns down into the lower one on the right, the short's on the left.
- Rope ridges: the fine lines along the rope, about 7 across the face we see.
- Flutes: 16 round, the bright crests counted across both bodies (21-23 degrees apart). The first count (24) took the shading lines between crests for grooves. Depth from the scalloped foot edge.
- Wax colour: the brightest wax in the photo (#e2c0a1), one plain colour.
- Wicks: base and tip from their pixels.

## Hidden (how it is filled)
- The back of each candle: the same round shape all the way round.
- The body under the knot: it runs on smoothly between the measured rows above and below.
- How deep the bands are: they lie on the body and reach out to the knot's measured edge, so they are flat (the tall's about 0.4 as deep as tall).
