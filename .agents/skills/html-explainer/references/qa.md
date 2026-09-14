# Look at it before you share

The page is not done when the file writes. It is done when a look at the
running page is clean.

## How

1. Write the file to disk at the harness-supplied path.
2. Open it with the harness preview.
3. Capture desktop (~1280) and mobile (~390) when the harness has a
   screenshot tool. If it does not, resize the live page to both widths
   and look.
4. Read the picture, not just the HTML.
5. Patch. Look at the broken region again.

## Faults to hunt

First two are the usual ones. They are why this checklist exists.

- Overflowing labels. Node text hanging out of the box, legend text off the
  canvas, captions wrapping onto the next node.
- Crossed lines. Unlabeled edge crossings, arrows through boxes, a spaghetti
  sequence.

Then:

- Collision. Two labels sharing pixels. A caption over a control.
- Clip. Buttons or ticks cut off at the card edge.
- Scroll surprise. Horizontal scrollbar at 1280. Full-page zoom needed at 390.
- Contrast. Grey on grey, thin gold on cream, red text on dark red fill.
- Dead play. Play does nothing. No reset. Autoplay on load. Animation that
  cannot be paused.
- Tiny targets. Step/Play under 32px.
- Orphan chrome. A sticky header covering the first heading. A toc that
  overlaps the diagram.
- Type soup. More than two families. Display face on body copy.

## Pass line

Ship when both widths show:

- Every label inside its box or its reserved column
- Edges that can be followed without guessing
- Controls visible and usable
- No horizontal scroll at 1280

If a diagram cannot pass after one redraw, split it. Two small figures beat
one dense one.
