# Hero image prompts: How to Analyze U.S. Jobs Data

Target: 1680x1080 landscape (a ratio of about 1.56). Generate wide; the crop is
done with `~/.claude/d4tp-process/hero fit`.

The picture has one job: it takes about two of the jobs that led August's gains
to equal one paycheck elsewhere ($41,777 against $84,226 in 2025). A balance
scale with two sets of work clothes on one pan and one on the other, sitting
perfectly level, says that at a glance. Clothes, not people: generators handle
objects far better than crowds, and it keeps the workers themselves out of the
weighing.

## Prompt 1 (still life photograph, recommended)

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

## Prompt 2 (variant: more on the left pan)

> Still life photograph of a brass balance scale on a dark wooden table, its
> beam perfectly level. The left pan is piled with several folded work
> uniforms: a white cook's apron, a black server's apron with an order pad, a
> set of light blue scrubs, and a school cafeteria hairnet. The right pan holds
> one folded navy suit jacket and a tie. Warm side light, dark background
> (#181A1B), shallow depth of field, muted natural color, wide 3:2 composition,
> the whole scale in frame. No text, numbers or logos.

Prompt 2 shows "many against one" more strongly. Prompt 1 matches the data more
closely (about two to one).

## Negative prompt

> people, hands, faces, text, numbers, labels, logos, watermark, garbled
> lettering, money, coins, dollar signs, tilted scale, unequal pans, cartoon,
> illustration, 3d render, oversaturated, hdr, lens flare, cluttered background

## Practical notes

- The pans must be level. Generators often tilt a scale; regenerate any image
  where the beam is not flat, because a tilted scale says the opposite.
- Measure the shape you actually get before cropping; the explorer's launch
  hero first came back as a 4:3 image inside a 16:9 file with white bars down
  each side.
- Drop the image you pick into `images/` and I will run `hero fit`, keep the
  original as `september-2026-jobs-report-hero-source.<ext>`, and write the alt
  text.

## Tried and set aside

A magnifying glass over a bar chart, the bar made of tiny workers. Generators
could not render the figures inside the lens cleanly (October 4).

## Chosen

File: images/september-2026-jobs-report-hero-source.<ext>
Alt (under 500 characters):
