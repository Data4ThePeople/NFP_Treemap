---
title: Exploring U.S. Jobs Data
meta_title: "Nonfarm Payrolls by Industry: Which Months Are Unusual"
subtitle: Drill into US nonfarm payrolls by industry, from the headline number down to six-digit detail, and see which months are unusual for the industry rather than merely large.
slug: nonfarm-payrolls-by-industry
date: 2026-09-04
description: Free interactive treemap of US nonfarm payrolls by industry that scores every move against the industry's own history, so you can tell a signal from a noisy month.
keywords: nonfarm payrolls by industry, jobs report anomaly, is this jobs number unusual, payroll data revisions, jobs by industry, BLS employment data, Current Employment Statistics, CES data visualization, payroll employment treemap, which industries added jobs, employment change by industry, NAICS employment data, jobs report by sector, interactive jobs data, seasonally adjusted employment, BLS jobs data drill down
section: Visualization
schema_type: dataset
dataset_name: US nonfarm payroll employment by industry, monthly
dataset_description: Monthly seasonally adjusted payroll employment for every industry published by the US Bureau of Labor Statistics Current Employment Statistics (CES) survey, with each month's change scored against that industry's own history of comparable changes. 842 series covering the full published industry hierarchy, from total nonfarm payrolls down to six-digit NAICS industry detail, from January 1939 to the present month. Values are all employees in thousands, exactly as reported by BLS, with no modeling, smoothing or rescaling applied.
temporal: 1939-01/..
spatial: United States
measured: All employees|thousands of jobs;Net employment change over the selected horizon|thousands of jobs;Percent employment change over the selected horizon|percent
sources: https://www.bls.gov/ces/|https://www.bls.gov/news.release/empsit.toc.htm|https://www.census.gov/naics/
same_as: https://www.bls.gov/ces/
credit: US Bureau of Labor Statistics, Current Employment Statistics
catalog: BLS Public Data API|https://www.bls.gov/developers/
measurement_technique: Monthly establishment survey of approximately 121,000 businesses and government agencies, seasonally adjusted, benchmarked annually to the Quarterly Census of Employment and Wages
distribution: text/csv|https://data4thepeople.github.io/NFP_Treemap/dist/index.html
app_url: https://data4thepeople.github.io/NFP_Treemap/dist/index.html
app_name: U.S. Jobs Data Explorer
app_description: A free interactive treemap of US nonfarm payroll employment by industry. Drill from total nonfarm down to six-digit NAICS detail, set any base month back to 1939, compare horizons from one month to twenty years, and see which changes are unusual for the industry rather than merely large.
app_features: Drill down through eight levels of the BLS industry hierarchy|Select any base month from January 1939|Compare one month against up to twenty years|Absolute and percent change views|Official Census NAICS definitions on hover|Anomaly scoring against each industry's own history|CSV and PNG export|Deep-linkable views and an embeddable iframe
hero: charts/hero-mine-entrance.jpg
hero_alt: Illustration of a miner in a hard hat and high-visibility jacket standing at the timber-framed entrance of a coal mine, her headlamp throwing a beam into the darkness. A weathered sign above the entrance reads Nonfarm Payroll Data, Bureau of Labor Statistics.
meta_image: charts/social-card.jpg
meta_image_alt: Illustration of a miner in a hard hat at the entrance of a coal mine, her headlamp lit, beneath a sign reading Nonfarm Payroll Data, Bureau of Labor Statistics.
---

# Exploring U.S. Jobs Data

Every month the Bureau of Labor Statistics (BLS) issues its estimate of how many jobs the U.S. gained or lost. It is called Nonfarm Payroll (NFP) data, and it takes survey responses from U.S. businesses, cranks them through a model, and outputs them for policy makers, the stock market, and the public to blindly trust.

But warning signs are growing on this data. The [survey response rate](https://www.bls.gov/osmr/response-rates/establishment-survey-response-rates.htm) is in structural decline, from about 60% before 2020 to 43.3% now. The [confidence interval](https://www.bls.gov/news.release/empsit.tn.htm) on the monthly change is plus or minus 122,000, which is larger than the change itself in most recent months. The [benchmark revision](https://www.cnbc.com/2025/09/09/jobs-report-revisions-september-2025-.html) for the year through March 2025 cut 911,000 jobs, the largest on record in level terms. Each month's figure is also revised twice after publication, and in 2025 every one of those revisions ran [downward](https://www.bls.gov/web/empsit/cesnaicsrev.htm) — eleven for eleven, including nine consecutive months, a run matched since 1979 only by the 2008 financial crisis. And [BLS headcount](https://www.amstat.org/docs/default-source/amstat-documents/FedStatHealth_MidYearUpdate.pdf) is down about 20% in two years.

Nonfarm payroll data has always been a complex web of underground tunnels. Most people see the headline number and treat that as gospel, but there are hundreds of numbers buried underneath it, begging to be explored. This used to be easier when the data was less volatile. The tunnels were lit up, so to speak. Now they are dark. We do not know what to trust, or where to direct our skepticism.

That is why we built this tool. It is the map and the high-beam headlamp you need to responsibly explore this critical data set. The tool is embedded below and, like everything else at Data 4 The People, it is free to use. Please at least skim the rest of this report. It is the instruction manual for using this visualization responsibly.

<iframe src="https://data4thepeople.github.io/NFP_Treemap/dist/index.html" title="U.S. Jobs Data Explorer: nonfarm payroll employment change by industry" width="100%" height="780" style="border:0" loading="lazy"></iframe>

## How to explore payroll data by industry

### How to read a tile

The chart is a treemap, which shows quantity as area. Each rectangle is one industry that the BLS publishes separately.

The size of each tile corresponds to the number of jobs gained or lost in one industry. A tile's area is the absolute change in employees over the period you picked, so the industries that moved the labor market most are the biggest shapes on the screen. That stays true in both color modes, deliberately. Sizing by percent would let a three-thousand-person industry with a good month outweigh food services.

The color of each tile shows you the direction and scale. Blue is a gain, red is a loss, and the scale is symmetric around zero, so a loss and a gain of equal size read at equal strength. We computed the palette rather than picking it, and validated it against the standard color-vision-deficiency transforms, so the two directions stay apart for readers who cannot separate them by hue.

The industry tiles are grouped by what BLS calls a "supersector." There are eleven of them, and every industry lives inside one. "Restaurants and other eating places," for example, lives inside "Leisure and hospitality." Once you drill into an industry, the bands regroup around whatever you opened.

Nothing here is scaled, padded or balanced to make the arithmetic look tidy. Every tile is the number BLS reported.

### What a hatched tile means

This is one of the most important features of this tool. A colored hatch tells you the change stands out against that industry's own record, and indicates one of two things: the change is unusual, or the change is anomalous. Hatched industries, in our view, are the ones we want to look at with a skeptical eye, especially in the initial data release. Over longer time periods, hatched industries indicate real shifts in the labor market.

The types of hatch patterns: **gray** means BLS has not published a value for that industry in that month. **Colored** is the anomaly marker, a light hatch for a month that is unusual for that industry, a heavier one for a change with almost no precedent in its record. What earns a tile each mark is set out further down, in the section on how we built this.

### The controls

Every control sits in the bar above the chart. Nothing here needs an account and
nothing is saved, so you can change anything and change it back.

### Pick the month you want to look at

**Base period** is the month being measured. It opens on the most recent release
and it goes back as far as the data does, to 1939 for the broad aggregates and
1990 for most individual industries.

**Comparison period** is what that month is measured against. Leave it on 1mo to
drill into the government's jobs report and see what is driving it. Change it to
1yr, 2yr, 3yr, 5yr, 10yr or 20yr to see longer term trends and learn more about
how America's job landscape has been shaped over time.

Together these two are the tool's main use. Set the base to March 2007 and the
comparison to 1mo and you are reading a jobs report from nineteen years ago,
scored against what was normal at the time.

Note that this chart always shows the BLS's current vintage of the data. So
March 2007 is not the figure that was initially reported that month; it is the
settled number after every revision since. The most recent months on the chart
have not been through that process yet.

### Choose how much detail you want

Let's go back to our underground mine analogy. Think of **display level** as how
deep you are travelling into the mine. Level 0 has only one "industry," total
nonfarm payrolls. Travel down to level 7 and you will find industries as niche
as "Floor covering retailers." In other words, display level sets how finely
industries are broken up. Each step down splits the level above it into its
published parts.

- **Level 2** is the eleven supersectors, the broadest useful view.
- **Level 3** is nineteen sectors. The page opens here because every industry at
  this level is published with the headline, so the view is complete on the
  morning of a release.
- **Level 4** is 84 industries and is the first level where some detail may not
  be published yet on release day.
- **Levels 5, 6 and 7** go finer still, ending in 166 industries at six-digit
  NAICS detail.

Note that not every industry is published in the latest month. A message right
above the treemap tells you how many are missing data and names the most recent
month that covers all of them. Those industries still get a tile,
hatched in gray rather than colored, so you can see where the gaps are. Check
back after the next release, when BLS publishes them.

### Drill into an industry

**Click any tile** to go inside it and see the industries it is made of.

**To go back up**, click any step in the breadcrumb trail above the chart, press
the Up button, or press Escape.

**Using a keyboard**, press Tab to move between tiles and Enter to drill into the
one you have selected.

### See everything about one industry

**Hover a tile**, or select it with the keyboard, and a panel opens with five
things: the industry's total employment, its change over the comparison period
you chose, the anomaly score, the official Census definition of what the industry
contains, and a small chart of its whole history with recessions shaded.

### Find an industry by name

**Type into the highlight box.** Matching tiles stay bright and the rest dim, so
you can locate an industry without hunting for it. Clear the box to bring
everything back.

### Switch between size and rate

**Color metric** has two settings.

- **Absolute** colors each tile by the number of jobs gained or lost. This is
  the default and it answers "what moved the labor market most".
- **Percent** colors by proportional change instead. It answers "what moved most
  relative to its own size", which is how you find a small industry losing a
  tenth of its workforce.

Tile area stays the absolute job change in both settings, so size and rate are
readable at the same time.

### Take the data with you

**CSV** downloads exactly the view on screen, including whatever you have drilled
into, with the same numbers the tiles show.

**PNG** saves the chart as an image.

**Copy link** puts the whole state of the page into a URL. Send that link and the
other person opens the same industry, at the same level, over the same horizon.
It is also how to cite a specific view.

## How we built it from BLS payroll data

### Every number comes from the BLS API

We pull the monthly values directly from the BLS Public Data API rather than the flat text files, which means the whole thing refreshes in seventeen requests when a jobs report lands. Twenty-six series reach back to January 1939. Most industry detail begins in 1990, which is when CES started publishing it separately.

Two things the API cannot give us are fetched once and cached. The `ce.industry` reference file carries each industry's display level, sort order and NAICS code, and the API has no metadata endpoint to serve them. The Census NAICS descriptions supply the definition text you see on hover.

### Constructing the anomaly score

Say an industry added 8,000 jobs last month. Is that a lot? It depends entirely
on which industry. For one that usually moves by a few hundred, 8,000 is
enormous. For one that routinely swings by tens of thousands, it is a quiet
month. The number on its own cannot tell you.

To answer it you first need to know how much that industry normally moves. Take
food services and drinking places. Over the last twenty years its employment has
changed by about 19,000 in a typical month, and a *usual swing* away from that is
about 21,000. Those two numbers describe what normal looks like for restaurants.

Now you can judge any month against them. In August 2026 food services added
59,200 jobs. That is 40,500 above its typical month, which is 1.9 usual swings.
That ratio is the **z-score**: how many usual swings from normal a month sits. A
z of 1 is about as far as that industry usually gets, a z of 2 is twice that, a z
of 3 is three times and rare. Because the answer is in usual swings rather than
jobs, an industry employing twelve million people and one employing nine thousand
can be compared directly.

One refinement, and it matters here. If you measure the usual swing with a plain
average, a few enormous months drag it upward and everything afterward looks calm
by comparison. The pandemic would do exactly that. So we use the middle value
instead of the average, which a handful of extreme months cannot move. That is
what *robust* means when the tooltip says "robust z".

**What the month is compared against** is the same industry's own history of
changes over the same length of time, assembled under three rules.

- **The lookback scales with the horizon**, ten months of history for every month
  of comparison, with a floor of twenty years. The floor is not padding: a
  shorter window with the pandemic removed can contain no downturn at all, which
  leaves every sample an expansion-year change and makes an ordinary slowdown
  look extreme.
- **Overlapping windows are not independent.** Every month starts a new
  three-year window, and consecutive ones share 35 of their 36 months, so they
  are nearly the same observation counted again. This is why a longer horizon
  can cite a bigger sample and mean less by it: 305 three-year windows are about
  8 independent observations, where 212 one-month changes are 212. The tooltip
  reports both. At least six non-overlapping windows are required, and below
  that the tool says it has insufficient history rather than guessing.
- **The pandemic is excluded**, March 2020 through June 2022, from the collapse
  until payrolls regained their February 2020 peak. A window is dropped if either
  endpoint falls inside it, not only if it begins there, because a three-year
  window starting in late 2020 still measures from deep in the hole.

Hover any tile and you get one of four labels:

- **Typical** — less than one usual swing from normal.
- **Notable** — further than that, but not enough to be marked.
- **Unusual** — marked with a light hatch.
- **Anomaly** — marked with a heavy hatch.

The last two require the change to be both rare in that industry's own record and
large on its own scale. What exactly that takes is next.

### What counts as unusual, and what counts as an anomaly

A change gets a mark only if it passes two tests at once. They ask different
questions, and a month can pass one and fail the other.

**Is it big for this industry?** This is the z-score from above. To be marked
unusual, the month has to be at least 2 usual swings from normal. To be marked an
anomaly, at least 3.

**Is it rare for this industry?** Count how many of that industry's own months
landed at least this far from normal, in either direction. To be marked unusual,
this month has to be among its most extreme 10%. To be marked an anomaly, its
most extreme 1%.

Pass both and the tile is marked. The two tiers nest, so nothing is an anomaly
without also being unusual. For any given industry an unusual month comes up
roughly once a year, and an anomaly roughly once a decade.

**Why not just the z-score?** Because on this data it does not mean what a
textbook says it means. A textbook assumes changes cluster tidily around normal,
and payroll changes do not: they have long tails, with far more extreme months
than that assumption predicts. Measured across 2013 to 2026, a z of 2 turns up in
about 9% of industries rather than the 5% the textbook implies, and a z of 3
about ten times more often than it should. Counting an industry's actual months
does not drift like that, and the answer is easier to hold on to. Its most
extreme tenth is one month in ten. That is just true.

**Why not just the count?** Because BLS reports employment to the nearest hundred
jobs. An industry whose entire history sits close to that rounding floor would
set a record almost every month, and counting alone would mark it every time.
Requiring real size as well keeps the marks meaningful: at display level 5 the
median marked change is 3,400 jobs, and only 3% are under 1,000.

None of this is a formal statistical test. With hundreds of industries on screen,
a threshold loose enough to fire often would fire by chance often too, which is
why both rates were checked against thirteen years of real months rather than
assumed. Treat a marked tile as a place to look, not as a finding.

### The hierarchy comes from the codes, not the row order

Each industry's parent is derived from its industry code rather than from where
it sits in the file, because the file's ordering puts whole branches under the
wrong parent. The handful of aggregates above the supersectors are mapped
explicitly, since they overlap rather than nest.

### Every industry carries its official definition

The NAICS field in the BLS reference file is a compressed notation rather than a
plain code, with several syntaxes that have to be parsed. All 813 non-aggregate
industries resolve, which is what puts the official Census definition on every
tile that has one.

### Three roll-ups are hidden, because they double-count

A few CES roll-ups sit at the same display level as the components they are made
of, so a flat view of that level counts those jobs twice. Health care, specialty
trade contractors, and motor vehicles and parts are hidden by default for that
reason, and you can switch them back on.

### The tiles do not add up to the total, and we leave it that way

BLS publishes only some children for many parent industries, so the tiles at a
level frequently do not sum to the parent above them. Forcing a sum would mean
inventing a residual category and putting a number in it that BLS never
published, so instead every tile is the reported value and the page tells you
when the published children cover materially less than the whole.

### Revisions overwrite, because a jobs number is a moving target

Our refresh upserts on industry and month, so a revision replaces the cached value instead of accumulating beside it. What you see is always the current vintage.

This surprises people, so it is worth stating plainly. The number you saw last month may not be the number you see now, and that is the data behaving correctly.

### The detail lags the headline, and the page says so

CES publishes most industry detail about a month behind the headline aggregates. On the morning a jobs report lands, roughly a fifth of the 842 series carry the new month.

The tool opens on the newest month at level 3, because all nineteen industries at that level publish with the headline, so the opening view is complete. Go deeper on release day and some tiles have no value yet. The page counts them and names the most recent month that covers all of them, rather than hiding the gap or quietly falling back to an older month while you assume you are seeing the latest.

It also separates the two reasons a tile can be empty, because blaming the wrong one is worse than saying nothing. At the newest month, the detail is not published yet. In 1955, most of these industries did not exist as published series, because CES industry detail begins in 1990.

### It is a single file

The whole visualization is one self-contained HTML file. No server, no external requests, no build step when it loads. The browser receives raw monthly levels only and computes every change, percentage and anomaly score on demand, because precomputing them was not practical: every combination of base period, horizon and display level would dwarf the underlying data and still would not cover click-to-drill. The levels ship delta-encoded, which roughly halves the payload.

That is what makes the chart straightforward to embed, export and read offline.

## What nonfarm payroll data cannot tell you

It counts payroll jobs, not people. CES asks employers how many people are on their payrolls, so somebody with two jobs is counted twice and the self-employed are not counted at all. The unemployment rate comes from the household survey, called the CPS, which is a different survey with a different frame. We built [a separate tool](https://www.data4thepeople.com/p/beyond-the-unemployment-rate/) for that one.

It is national. CES publishes state and metropolitan detail, and this visualization does not use it.

It is seasonally adjusted throughout, which is the right basis for comparing one month to the next and the wrong basis for asking how many people worked in retail in December.

An anomaly score is not a verdict. It says a move is large relative to the industry's own history, not that it is meaningful, causal or permanent. A strike, a hurricane, a benchmark revision and a genuine turning point can all produce the same score. It tells you where to look, not what you will find.

## Frequently asked questions

### How do you know if a jobs number is unusual?

Compare it against the same industry's own history of changes over the same length of time, rather than against other industries or against a single headline figure. This tool does that automatically, reporting a robust z-score, a percentile rank and a plain-language label for every industry it shows. A change of 8,000 jobs is enormous for an industry that normally moves by a few hundred and unremarkable for one that routinely swings by tens of thousands, and only the industry's own record can tell the two apart.

### What does the hatched tile mean?

A diagonal hatch marks an industry whose change stands out against its own history, so you can find them without hovering over every tile. A light hatch means unusual: the month is at least 2 usual swings from normal for that industry, and among the most extreme 10% of its own record. A heavier hatch means an anomaly: at least 3 usual swings, and the most extreme 1%. A third hatch, in gray and leaning the other way, means no data was published for that period rather than anything about the size of the change.

### What does the anomaly score mean?

It compares the change you are looking at against the same industry's own history of changes over the same length of time. It uses at least twenty years of history, requires at least six non-overlapping comparison windows before it will report anything, and excludes March 2020 through June 2022 so the pandemic collapse and recovery do not define what counts as normal. It is a robust z-score, built on the median and median absolute deviation, so a few extreme months cannot flatten the scale. Where a change is rare as well as large it is marked on the tile, as unusual or as an anomaly.

### Why are nonfarm payroll numbers revised so much?

The Current Employment Statistics survey publishes a first estimate before all responses are in, then restates the two preceding months at every release as more arrive. Each annual benchmark can restate up to five years of seasonally adjusted history. The revisions are often larger than people expect: one food services month in this data moved by more than 20,000 jobs between vintages. Scoring a change against decades of the same industry's behavior is more durable than treating any single print as settled.

### What is the Current Employment Statistics survey?

The Current Employment Statistics survey, also called the establishment survey or the payroll survey, is a monthly US Bureau of Labor Statistics survey of roughly 121,000 businesses and government agencies. It produces the headline nonfarm payrolls figure reported each month, along with employment, hours and earnings for every industry it publishes. Because it surveys employers rather than households, it counts filled jobs rather than employed people.

### Which industries added the most jobs last month?

That changes every month, which is what this treemap is for. Open it on the most recent month with a one-month comparison and the largest blue tiles are the industries that added the most jobs, while the largest red tiles are the ones that lost the most. Hovering any tile also tells you whether that move was unusual for the industry, which the size alone will not. For a longer look at how concentrated recent job growth has become, see [Giants Walk Among Us](https://www.data4thepeople.com/p/giants-walk-among-us/).

### How often is this data updated?

BLS releases the Employment Situation report monthly, usually on the first Friday of the month, covering the previous month. We refresh this visualization from the BLS API after each release. Because CES revises the two preceding months at every release, and up to five years of history at each annual benchmark, a refresh also updates months that were already published.

### How far back does BLS payroll data go?

To January 1939 for the broadest aggregates, including total nonfarm payrolls. Most individual industries begin in January 1990, when CES started publishing that level of detail separately. This tool shows each series over the span it actually exists, and it distinguishes a gap caused by an industry not yet being broken out from a gap caused by data not yet being released.

### Why do the industries not add up to the total?

Because BLS publishes only some children for many parent industries. The published sub-industries of a parent frequently cover less than all of it, and the remainder is not published separately. Nothing here is scaled or padded to force a sum, so where the published children cover 76% of a parent, the page tells you it is 76% rather than inventing a residual category to close the gap.

### What is a treemap, and why use one for employment data?

A treemap displays quantity as area, using nested rectangles to represent a hierarchy. It suits payroll data because employment change is both hierarchical and extremely unequal, with a handful of industries accounting for most of the movement in any month. A treemap makes the largest movers the largest shapes, so the significant changes are visible without knowing in advance what to look for, and the nesting lets you click from a sector straight into the specific industry beneath it.

### Is this payroll data visualization free?

Yes. There is no account, no paywall and no usage limit, and it can be embedded in another website with a standard iframe. The underlying data is public-domain US government statistics that anyone can obtain from BLS directly.

### Can I download the data as CSV?

Yes. The CSV button downloads whatever view you are currently looking at, including any industry you have drilled into, with the same values shown on the tiles. The PNG button exports the chart as an image.

### What is the difference between the payroll survey and the household survey?

They are two separate monthly surveys. The payroll or establishment survey, the CES, shown here, asks employers how many people are on their payrolls and produces the nonfarm payrolls figure and all the industry detail. The household survey, the CPS, asks people about their own employment status and produces the unemployment rate. They regularly disagree in a given month because they measure different things by different methods.

### What does seasonally adjusted employment mean?

Seasonal adjustment removes the regular within-year pattern that repeats every year, such as retail hiring before the winter holidays or construction slowing in winter. It is what makes one month comparable to the month before it. Every figure in this visualization is seasonally adjusted, which is the correct basis for measuring change and the wrong basis for asking how many people held a particular job in a particular month.

### Can I embed this visualization on my own site?

Yes. It is a single self-contained page built to be framed. It detects that it is embedded, switches to a compact layout that fits a fixed-height iframe without scrolling, and posts its content height to the parent for hosts that want to size the frame automatically. Every control lives in the URL fragment, so you can embed a specific industry, level and horizon directly.

## The code behind this chart

The full pipeline is public, including the fetch, the hierarchy derivation, the NAICS parser, the anomaly scoring and the test suite that covers them: [github.com/Data4ThePeople/NFP_Treemap](https://github.com/Data4ThePeople/NFP_Treemap).

## Sources

- [US Bureau of Labor Statistics, Current Employment Statistics](https://www.bls.gov/ces/). All employees, seasonally adjusted, in thousands, retrieved through the BLS Public Data API v2. 842 series, 401,515 monthly observations, January 1939 through the current release.
- [BLS Employment Situation news release](https://www.bls.gov/news.release/empsit.toc.htm), the monthly release this visualization tracks.
- BLS `ce.industry` reference file, for the industry hierarchy, display levels and NAICS mappings.
- [US Census Bureau, 2022 NAICS Descriptions](https://www.census.gov/naics/), for the official industry definitions shown on hover.

Every figure in this visualization is the value BLS published. Nothing is modeled, interpolated, smoothed or rescaled.
