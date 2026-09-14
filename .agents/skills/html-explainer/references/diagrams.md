# Diagrams and playable flows

Every explainer has a diagram for the idea. When the page describes a
process, also make that flow playable with Play / Pause / Step / Reset.
Look at the running page at ~1280 and ~390 before sharing; screenshot
only when a capture tool exists.

## What to reach for

| Idea | Draw this |
| --- | --- |
| Who talks to whom, layers, ownership | Architecture boxes + edges. HTML+CSS grid or inline SVG. |
| Ordered steps with branches | Flowchart. Rectangles for work, diamonds for decisions, labeled edges. |
| A calls B then C over time | Sequence diagram. Lifelines + arrows. Animate the current arrow. |
| Options against the same axes | Comparison matrix. Real `<table>` or CSS grid. One claim per cell. |
| A value moving through stages | Token on a path. Play/step moves the token. |
| Before and after a change | Two aligned figures or a toggle, not a paragraph that says "before." |

Prefer hand-placed SVG or positioned HTML for anything you will screenshot. You own label anchors and edge routes. Mermaid is a first-pass sketch; if a label overflows or an edge crosses, redraw it by hand. Do not ship the sketch.

## SVG rules that survive a screenshot

- ViewBox sized to the drawing. Do not let labels sit outside it.
- Labels live in the SVG (`<text>` or `<foreignObject>` with a bounded width), not as HTML absolutely parked on top of a shrinking image.
- One edge, one route. Fan crossings at a right angle or add a hop. Crossing unlabeled edges is the usual fault.
- Node padding: text + 12px on every side at least. No label flush to a box edge.
- Stroke 1.5–2px. Arrowheads big enough to see at 390px wide.
- Color means one thing. If red is "reject", it is not also "hot path."
- Type: 13–15px on nodes. Smaller than 12px fails mobile.

## Make the flow playable

A flow on the page is a tiny machine.

Required controls, in one bar under the diagram:

- Play / Pause
- Step (one tick)
- Reset (back to tick 0)

Required picture at each tick:

- The active node or arrow is marked (fill, stroke, or a moving token).
- A one-line caption states what just happened.
- Optional: a small log of ticks already fired.

Implementation that stays small:

- Data is an array of ticks `{ at, caption, hi }` where `hi` is a node or edge id.
- CSS classes `.is-hot` / `.is-done` / `.is-idle` do the painting.
- `requestAnimationFrame` or a 700–1100ms interval. Pause cancels it.
- Keyboard: Space play/pause, `n` step, `r` reset.

Do not autoplay on load. The reader starts it.

Animation is for the flow, not decoration. No bounce on cards, no fade-in of the whole page.

## Comparison matrices

- Same axes on every option.
- The tradeoff is written on the cell, not in a footnote.
- Winner highlighting is optional and honest. If there is no winner, do not paint one.

## Sequence diagrams

- Time down. Actors across.
- Animate one message at a time on Play.
- Notes sit in a reserved column, not on top of a lifeline.

## What not to draw

- A screenshot of an ASCII diagram.
- A graph so wide it needs trackpad panning at 1280.
- Edges that hide under nodes.
- A legend that repeats what color already said, unless color is overloaded.
