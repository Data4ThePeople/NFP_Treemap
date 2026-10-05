# Hero image prompts: How to Analyze U.S. Jobs Data

Target: 1680x1080 landscape (a ratio of about 1.56). Generate wide; the crop is
done with `~/.claude/d4tp-process/hero fit`.

Current concept (Eric, October 5): the word JOBS, with the O drawn as the lens of
a magnifying glass. Inside the lens, a busy miniature economy: people at work in
every kind of job. It matches the title: one word on the surface, a whole economy
when you look closely. Illustration, not photographic.

## Prompt A (recommended)

> Editorial illustration, flat modern style with soft shading and fine detail.
> The word "JOBS" in huge, bold, geometric sans-serif capital letters fills the
> width of the image, centered, on a deep charcoal background (#181A1B). The J,
> B and S are solid warm off-white. The O is a large round magnifying glass: a
> thick brass-colored rim forms the letter O exactly, the same height and weight
> as the other letters, with a short handle angled down and to the right.
>
> Inside the lens, a bright, detailed miniature city scene full of people at
> work: construction workers in hard hats on a steel frame with a small crane,
> nurses and a doctor outside a clinic, a home health aide walking with an
> elderly man, cooks and a server in a busy diner, a teacher with students, office
> workers at desks by a window, a delivery driver with a van, a warehouse worker
> with a forklift, a cashier at a store counter. Diverse people, busy and
> dignified. Warm daylight colors inside the lens, so it glows against the dark
> letters around it, with a soft glass highlight across the top of the lens.
>
> Wide 3:2 composition, the word centered with generous margin on all sides.
> The only text in the image is the single word JOBS. No other words, numbers or
> logos.

## Prompt B (lighter background)

> Same as Prompt A, but on a warm off-white paper background (#F7F5EF) with the
> letters J, B and S in deep charcoal, and the brass magnifying-glass rim as the
> O. Inside the lens, the same busy miniature scene of people at work in many
> jobs, in soft, muted colors. Flat editorial illustration, wide 3:2, the word
> JOBS centered, no other text.

## Shorter variant

> Flat editorial illustration of the word "JOBS" in big bold capital letters on
> a dark charcoal background. The letter O is a magnifying glass with a brass rim
> and a handle. Inside the lens is a tiny, detailed, colorful scene of people
> working many jobs: construction, nursing, a diner kitchen, a classroom, an
> office, a warehouse, deliveries. Wide 3:2, centered, no other text.

## Negative prompt

> photograph, photorealistic, 3d render, extra letters, misspelled word,
> garbled text, second line of text, numbers, logos, watermark, money, dollar
> signs, farm or farmworkers, sad faces, cluttered background, oversaturated

## Practical notes

- Check the spelling: the word must read JOBS, with the lens clearly the O and
  the same size as the other letters.
- No farm workers in the scene: the data is nonfarm payrolls.
- Measure the shape you actually get before cropping, and ask for at least
  1800 pixels wide; the last generation came back at 1334x888.
- Drop the image you pick into `images/` and I will run `hero fit`, keep the
  original as `september-2026-jobs-report-hero-source.<ext>`, and write the alt
  text.

## Earlier concepts

### Balance scale, prompt 1 (still life photograph)

> Still life photograph of an antique brass balance scale standing on a dark
> wooden table. The scale has two shallow round brass pans hanging from chains,
> and the beam is perfectly level, both pans at exactly the same height.
>
> On the left pan sit two neatly folded sets of work clothes stacked on top of
> each other: a white cook's apron with a few faint kitchen stains, and a set of
> light blue medical scrubs with a lanyard and ID badge clip resting on top.
> On the right pan sits a single neatly folded navy blue suit jacket with a
> folded silk tie on top.
>
> Low, warm side light from the left, like late afternoon through a window,
> raking across the brass and the fabric textures. The background falls off to
> near black (#181A1B). Shot straight on at table height, 50mm lens at f/4,
> sharp from pan to pan, the background softly out of focus. Muted, natural
> color, rich brass highlights. Wide 3:2 composition with the scale centered and
> clear margin on all sides, the full scale and both pans inside the frame. No
> text, numbers, labels or logos anywhere in the image.

### Balance scale, prompt 2 (more on the left pan)

> Still life photograph of a brass balance scale on a dark wooden table, its
> beam perfectly level. The left pan is piled with several folded work
> uniforms: a white cook's apron, a black server's apron with an order pad, a
> set of light blue scrubs, and a school cafeteria hairnet. The right pan holds
> one folded navy suit jacket and a tie. Warm side light, dark background
> (#181A1B), shallow depth of field, muted natural color, wide 3:2 composition,
> the whole scale in frame. No text, numbers or logos.

Prompt 2 shows "many against one" more strongly. Prompt 1 matches the data more
closely (about two to one).

### Balance scale, negative prompt

> people, hands, faces, text, numbers, labels, logos, watermark, garbled
> lettering, money, coins, dollar signs, tilted scale, unequal pans, cartoon,
> illustration, 3d render, oversaturated, hdr, lens flare, cluttered background

### Balance scale, practical notes

- The pans must be level. Generators often tilt a scale; regenerate any image
  where the beam is not flat, because a tilted scale says the opposite.
- Measure the shape you actually get before cropping; the explorer's launch
  hero first came back as a 4:3 image inside a 16:9 file with white bars down
  each side.
- Drop the image you pick into `images/` and I will run `hero fit`, keep the
  original as `september-2026-jobs-report-hero-source.<ext>`, and write the alt
  text.

### Tried and set aside

A magnifying glass over a bar chart, the bar made of tiny workers. Generators
could not render the figures inside the lens cleanly (October 4). The balance
scale would not stay level, and a tilted version needed a regeneration
(October 4); set aside for the JOBS concept on October 5.

## Chosen

File: images/september-2026-jobs-report-hero-source.jpg (Gemini, 2528x1696; Prompt A)
Crop: `hero fit --focus bottom`, then the dark D4TP logo set along the handle (38px high, rotated 46.9 degrees to the handle's angle), so no crop can cut it off.
Alt (491 characters): Illustration of the word JOBS in large off-white letters on a dark background. The O is a brass magnifying glass, and inside the lens is a busy scene of people at work: construction workers on a steel frame under a crane, office workers at desks, nurses and a doctor outside a clinic, a home health aide walking with an elderly man, cooks and a server in a diner, a delivery driver with a van, and a forklift operator in a warehouse. The Data 4 The People logo runs along the handle.
