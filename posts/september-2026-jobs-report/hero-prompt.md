# Hero image prompts: How to Analyze U.S. Jobs Data

Target: 1680x1080 landscape (a ratio of about 1.56). Generate wide; the crop is
done with `~/.claude/d4tp-process/hero fit`.

The picture has one job: a single tall bar looks like one solid number until you
look closely, and then it turns out to be made of people, most of them in
restaurant, school and care work. The workers should look capable and dignified,
busy at their jobs, never small in a pitying way.

## Prompt 1 (photographic, miniature figures)

> Photograph of a large, clean bar chart built as a physical model on a light
> wooden desk: five or six simple matte blue bars of different heights standing
> in a row, the middle one much taller than the rest. A large brass-rimmed
> magnifying glass is held at an angle in front of the tall bar by a hand
> entering from the right edge of the frame. Outside the lens, the bar looks like
> one smooth solid block. Inside the lens, the same bar is revealed to be built
> from dozens of tiny, detailed human figures stacked and standing shoulder to
> shoulder: cooks in white aprons and caps, restaurant servers carrying trays,
> teachers holding books, home health aides in light blue scrubs helping elderly
> people, a few school bus drivers. Only one or two figures in office clothes,
> near the top. The figures are busy and upright, faces calm and capable.
>
> Soft, even daylight from a window on the left, gentle shadows. Shot on a macro
> lens with shallow depth of field: the figures inside the lens are crisp, the
> rest of the chart and the desk fall softly out of focus. Muted natural color,
> blue bars against warm wood and an off-white wall. Composed for a 3:2 frame,
> the magnifying glass just right of center with clear margin on all sides. No
> text, numbers or labels anywhere in the image.

## Prompt 2 (editorial illustration)

> Clean editorial illustration in a flat, modern style with soft shading. A
> simple bar chart on a dark charcoal background (#181A1B): six bars in muted
> blue, the center bar much taller than the others. A large magnifying glass
> hovers over the tall bar. Outside the glass the bar is a plain solid blue
> shape. Inside the glass, the bar is made of many small people standing
> together and working: cooks in aprons, servers with plates, teachers with
> books, home care aides in scrubs walking with elderly people, a school bus
> driver. One or two office workers with laptops near the top. Friendly,
> dignified figures, warm skin tones of many ethnicities, light gray and orange
> accents (#f37952) on their clothing. Wide 3:2 composition, the glass slightly
> right of center, generous empty space on the left. No text, numbers or labels.

## Shorter variant, for models that do better with less

> A magnifying glass held over the tallest bar of a blue bar chart. Outside the
> lens the bar is solid; inside the lens it is made of many tiny people: cooks,
> restaurant servers, teachers, and home health aides in scrubs caring for
> elderly people, with only a couple of office workers. Dignified, busy figures.
> Macro photography, shallow depth of field, soft daylight, muted color, 3:2,
> no text.

## Negative prompt

> text, numbers, labels, watermark, garbled lettering, cartoonish exaggeration,
> sad or suffering faces, crowds in distress, dollar signs, money, cluttered
> background, oversaturated, hdr, lens flare, extra fingers, distorted hands,
> fisheye distortion

## Practical notes

- AI models garble text, so these ask for none. If you want a label on the bar
  ("JOBS ADDED"), add it to Prompt 2 only, and check the lettering before using
  it.
- Measure the shape you actually get before cropping; the explorer's launch
  hero first came back as a 4:3 image inside a 16:9 file with white bars down
  each side.
- Drop the image you pick into `images/` and I will run `hero fit`, keep the
  original as `september-2026-jobs-report-hero-source.<ext>`, and write the alt
  text.

## Chosen

File: images/september-2026-jobs-report-hero-source.<ext>
Alt (under 500 characters):
