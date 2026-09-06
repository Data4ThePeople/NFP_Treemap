# Hero image prompt: the mine entrance

For the cave-and-headlamp framing. The picture has one job: establish that the
data is a dark place you go into, and that you would want a light.

## Primary prompt

> Documentary photograph of a Hispanic woman standing at the mouth of an
> underground coal mine, about to go in. She is in her thirties, wearing a
> scuffed opaque hard hat with a headlamp switched on and throwing a visible
> beam, safety glasses pushed up on the brim, a high-visibility jacket over
> dusty coveralls, and work gloves. She is turned three-quarters toward the mine
> entrance, looking into it rather than at the camera, one hand resting on the
> timber frame of the portal. The tunnel behind her falls away into complete
> darkness within a few feet, and her headlamp throws a single narrow cone into
> it, the beam picking out dust in the air.
>
> Mounted on the timber frame above the entrance is a weathered enamel sign with
> two lines of plain capital lettering: "NONFARM PAYROLL DATA" on the first line
> and "BUREAU OF LABOR STATISTICS" on the second. The sign is scratched and
> slightly rusted at the corners, bolted at four points, and lit by daylight.
>
> Overcast late-afternoon daylight outside, cool and even, contrasting hard with
> the black of the tunnel. Shot on a 35mm lens at f/2.8, sharp on the woman and
> the sign, the darkness behind falling off entirely. Muted natural colour, dust
> in the air, no lens flare. Composed for a 3:2 crop, with the woman left of
> centre and the entrance opening to the right. Keep the sign and her head well
> inside the upper half of the frame, with margin at both sides.

## Shorter variant, for models that do better with less

> A Hispanic woman in a hard hat with a lit headlamp throwing a visible beam,
> wearing a high-visibility jacket, stands at the timber-framed entrance of a coal
> mine, looking into the darkness. A
> weathered metal sign above the entrance reads "NONFARM PAYROLL DATA / BUREAU OF
> LABOR STATISTICS". Overcast daylight outside, pitch black inside. Documentary
> photography, 35mm, shallow depth of field, muted colour, 3:2.

## Negative prompt

> cartoon, illustration, 3d render, clear or translucent helmet, unlit headlamp, cgi, oversaturated, hdr, dramatic sunset,
> lens flare, glamour lighting, posed smiling, text watermark, extra fingers,
> distorted hands, illegible or garbled lettering, modern corporate signage,
> cluttered background

## Practical notes

**The hero has to end up 1680 x 1080**, a ratio of about 1.56. Compose for that.

**Check the shape you actually got.** The first attempt came back as a 4:3
photograph pillarboxed inside a 16:9 file, with 343px of white down each side,
which would have shipped as white bars. The second came back full-bleed 16:9
with no padding. Measure before cropping rather than trusting the file
dimensions.

From a full 16:9 frame, the 1680 x 1080 comes out at full height, losing about
360px of width. Anchor it to the left so the whole figure is kept; the sign sits
far enough inside the right edge to survive. `posts/charts/hero-mine-entrance.jpg`
is that crop of the second generation.

**Keep the sign and her head in the upper half.** Everything below her waist is
what a crop eats first, and none of it carries meaning.

**Text is the weak point.** Most image models still garble lettering, especially
two lines of it. Three ways to handle it, in order of reliability:

1. Generate the scene with a blank or roughly-lettered sign, then set the two
   lines properly in post. Guaranteed legible, and it takes a minute.
2. Ask for one line only, "NONFARM PAYROLL DATA", and leave the agency name out.
   Shorter strings survive more often.
3. Generate several and pick the one where the lettering happens to land.

If the sign has to carry both lines, keep them in that order. "Nonfarm payroll
data" is the phrase doing the work; the agency name is the joke's punchline and
survives being smaller.

**Why the headlamp matters.** It is the whole analogy. Make sure it is switched
on and casting light into the dark, not just sitting on the hat. If the model
keeps rendering it unlit, say "headlamp beam visible in the dust".

**One caption note.** The site's credibility rests on being straight about
sources, so an AI-generated photograph of a person should be captioned as an
illustration rather than left to read as documentary. Something as short as
"Illustration" under the image is enough.


## What the two generations settled

The second pass fixed everything the first one missed, so these are the
instructions worth keeping if it is ever regenerated:

- **Both lines of the sign render correctly.** This is the part that usually
  fails, and it has now worked twice. Leave that wording alone.
- **Naming the beam is what produced it.** The first attempt had a lit lamp with
  almost no visible light, which loses the whole analogy. Asking for a beam
  picking out dust in the air is what made it read.
- **"Opaque hard hat" fixed the helmet.** The first attempt rendered something
  closer to a translucent novelty dome.
- **The tunnel is genuinely black** rather than a dim grey suggestion of depth.
  The contrast is the point.
- **The mood stays documentary rather than glossy.** Overcast, muted, dust on
  the coveralls, no dramatic lighting.

The remaining judgement call is the caption, below.
