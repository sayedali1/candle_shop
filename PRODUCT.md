# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Arabic speakers who buy a handmade candle for their own home or as a gift, mostly on a phone, and place the order through WhatsApp. They cannot touch or smell the candle online, so they need to see it, understand what it is, and trust it enough to send a message. (Confirmed with the user, 2026-10-28.)

## Product Purpose

A one-page shop for a handmade-candle maker: show each candle, give the facts a buyer needs, and lead to a WhatsApp order. There is no cart, no payment and no price on the page. This is currently a **test project** used to practise a portfolio-building workflow (the portfolio-coach and candle-from-photo skills); there is no real client yet, so the brand name, facts, prices, WhatsApp number and photos are placeholders. If a real candle maker adopts it, every placeholder must be replaced before launch.

## Positioning

Every candle is a lit 3D model on a shelf you walk along, each rebuilt from a real candle photo (shape, wax, glaze, wick), instead of a grid of product photos. Handmade is the craft; the lit 3D candles are how it is shown. A neighbouring shop with product photos could not truthfully copy that. (Confirmed with the user.)

## Operating Context

- Language and direction: Arabic, right to left.
- Ordering: a WhatsApp link per candle with the candle's name in the message. The number in the page (`0000000000`) is a placeholder.
- The 3D scene is one fixed full-page Three.js canvas behind the content, driven by scroll; the page must still work (photos, plain text) when 3D cannot run.
- Local testing goes through `open-page.bat` (a no-cache local server); the page cannot run from a double-clicked file.
- Candle models are built from recipe files (`recipes/*.json`) by `candle-builder.js`, checked in the Candle Lab (`lab.html`) against reference photos.

## Capabilities and Constraints

- Sections today: hero with the lit 3D candle, About (headline, four steps, materials), Products shelf (8 candles), a detail panel per candle, FAQ, footer.
- The detail panel shows: name and scent line, size, burn time, wax, wick, scent notes (top, heart, base), ingredients, first-burn advice, care and safety, what happens if it arrives damaged, and the order button. All of these facts are placeholders (`products.json`).
- Phone performance and battery with eight 3D candles are not yet measured on a real phone (a `?perf` readout and a checklist exist).
- Undecided: the real brand name, logo, taglines, prices, delivery and returns policy, real scent and wax facts, location or pickup point, whether reviews will ever exist.

## Brand Commitments

- Chosen direction (user, 2026-10-28): "warm hearth": dark brown, amber and cream, classic Naskh titles. The name "علامة تجريبية" and all taglines are placeholders.
- The page voice is warm and plain; it never claims a fact the client has not given.

## Evidence on Hand

- Photos: free Unsplash test images in `assets/photos/` with credits in `assets/CREDITS.md`. Seven of the eight candles have a matching photo; the flowery-jar candle has none. They are stand-ins for the client's own photos.
- No testimonials, reviews, sales data, awards, customer names or prices exist. Future work must not invent them.
- Decision log: `brief/decisions.md`; references: `brief/vision.md`.

## Product Principles

- The user decides; Claude guides and builds. Every design choice is logged with the options that were on the table.
- Never invent client facts. Placeholders are marked as placeholders on the page ("نص تجريبي" / "نموذج تجريبي").
- Phone first: if a detail costs frames or battery on a phone, it has to earn its place.
- The page works without 3D; the 3D adds to the product, it is not a gate.
- A candle's page tells a buyer what they cannot smell or touch: scent, size, burn time, care.

## Accessibility & Inclusion

Arabic, right to left, with respect for reduced-motion settings. No further product-specific standard has been set; keyboard focus order and screen-reader behaviour are not yet verified.
