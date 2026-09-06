# Hero image prompt: the mine entrance

For the cave-and-headlamp framing. The picture has one job: establish that the
data is a dark place you go into, and that you would want a light.

## Primary prompt

> Documentary photograph of a woman standing at the mouth of an underground coal
> mine, about to go in. She is in her thirties, wearing a scuffed hard hat with a
> headlamp switched on, safety glasses pushed up on the brim, a high-visibility
> jacket over dusty coveralls, and work gloves. She is turned three-quarters
> toward the mine entrance, looking into it rather than at the camera, one hand
> resting on the timber frame of the portal. The tunnel behind her falls away
> into complete darkness within a few feet, and her headlamp throws a single
> narrow cone into it.
>
> Mounted on the timber frame above the entrance is a weathered enamel sign with
> two lines of plain capital lettering: "NONFARM PAYROLL DATA" on the first line
> and "BUREAU OF LABOR STATISTICS" on the second. The sign is scratched and
> slightly rusted at the corners, bolted at four points, and lit by daylight.
>
> Overcast late-afternoon daylight outside, cool and even, contrasting hard with
> the black of the tunnel. Shot on a 35mm lens at f/2.8, sharp on the woman and
> the sign, the darkness behind falling off entirely. Muted natural colour, dust
> in the air, no lens flare. Wide 16:9 framing with the woman placed left of
> centre and the entrance opening to the right, generous headroom above and
> margin at both sides.

## Shorter variant, for models that do better with less

> A woman in a hard hat with a lit headlamp and high-visibility jacket stands at
> the timber-framed entrance of a coal mine, looking into the darkness. A
> weathered metal sign above the entrance reads "NONFARM PAYROLL DATA / BUREAU OF
> LABOR STATISTICS". Overcast daylight outside, pitch black inside. Documentary
> photography, 35mm, shallow depth of field, muted colour, 16:9.

## Negative prompt

> cartoon, illustration, 3d render, cgi, oversaturated, hdr, dramatic sunset,
> lens flare, glamour lighting, posed smiling, text watermark, extra fingers,
> distorted hands, illegible or garbled lettering, modern corporate signage,
> cluttered background

## Practical notes

**Composition for the crop.** Render at 16:9 and keep the woman and the sign well
inside the frame. The hero gets cropped for the listing card and again for the
link preview, and anything near an edge is what gets cut. Same lesson as the
current hero.

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
