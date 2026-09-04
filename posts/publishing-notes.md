# Publishing notes: Nonfarm Payrolls by Industry

Two things have to be pasted into Prismic by hand, plus one decision to make
before this goes live.

---

## 1. The iframe, for the empty `html_embed` slice

The post contains `::: embed 780px`, which the importer turns into an empty
`html_embed` slice at the right place in the document. Paste this into it.

```html
<iframe
    src="https://data4thepeople.github.io/NFP_Treemap/dist/index.html"
    title="Interactive treemap of US nonfarm payroll employment change by industry"
    width="100%"
    height="780"
    style="border:0"
    loading="lazy"></iframe>
```

Matches the house pattern used on the fertility, CPS and SNAP posts: `100%`
width, fixed pixel height, `border:0`, `loading="lazy"`, descriptive `title`.

**The `src` is live.** GitHub Pages is enabled on `main` and the URL returns the
1.85 MB build.

**Verified against the live URL at 879 x 780**, the real Prismic column width:
the page detects the frame, drops the masthead, renders in light, and everything
through the provenance line sits above the bottom edge with margin to spare. No
scrolling, no clipping. 640, 1200 and 1300 also fit. Below 560 the chart holds a
readability floor and the frame scrolls instead.

To open the embed on a specific view, append a fragment:
`...#lvl=4&h=1yr&drill=65620000`.

---

## 1b. What the dry run showed

`~/.claude/tools/prismic/prismic posts/nonfarm-payrolls-by-industry.md -n`
converts cleanly: 61 slices, 31 text blocks, 27 spacers, 2 images, 1 embed, with
the `schema` field populated and the canonical URL resolved to
`https://www.data4thepeople.com/p/nonfarm-payrolls-by-industry`.

Two things to know before the real run.

**There is no drop cap.** House style opens every post with a `drop_cap` slice,
and the installed converter does not emit one — the slice type does not appear
anywhere in `prismic_slices.py`. The first paragraph converts to an ordinary
`paragarph_text`. Either set it in the Prismic editor after import, or teach the
converter the slice. This affects every post published with this tool, not just
this one.

**The covers are set during the real run, not the dry run.** `featured_image`
and `meta_image` need uploaded asset ids, so they are absent from the dry-run
JSON by design. The front matter names `hero: charts/hero-treemap-august-2026.png`
and `meta_image: charts/social-card.png`, and both files exist. The social card
is not one of the body figures, so it carries its own `meta_image_alt`.

---

## 2. Structured data for the `schema` field

The importer already emits a `@graph` of Dataset, WebPage, FAQPage and
BreadcrumbList from `schema_type: dataset` in the front matter. That covers most
of it. The block below is the fuller version, adding the properties Google
Dataset Search actually reads and a `WebApplication` node for the tool itself.
Use it in place of the generated block if you want the extra coverage.

Replace `PAGE_URL` and confirm the Pages URL before pasting.

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Dataset",
      "@id": "PAGE_URL#dataset",
      "name": "US nonfarm payroll employment by industry, monthly",
      "description": "Monthly seasonally adjusted payroll employment for every industry published by the US Bureau of Labor Statistics Current Employment Statistics (CES) survey. 842 series covering the full published industry hierarchy, from total nonfarm payrolls down to six-digit NAICS industry detail, from January 1939 to the present month. Values are all employees in thousands, exactly as reported by BLS, with no modelling, smoothing or rescaling applied.",
      "url": "PAGE_URL",
      "isAccessibleForFree": true,
      "license": "https://www.usa.gov/government-works",
      "creditText": "US Bureau of Labor Statistics, Current Employment Statistics",
      "keywords": [
        "nonfarm payrolls",
        "employment by industry",
        "Current Employment Statistics",
        "CES",
        "NAICS",
        "payroll employment",
        "labor market",
        "seasonally adjusted employment"
      ],
      "temporalCoverage": "1939-01/..",
      "spatialCoverage": {
        "@type": "Place",
        "name": "United States"
      },
      "measurementTechnique": "Establishment survey of approximately 121,000 businesses and government agencies, seasonally adjusted",
      "variableMeasured": [
        {
          "@type": "PropertyValue",
          "name": "All employees",
          "description": "Number of people on nonfarm payrolls, seasonally adjusted",
          "unitText": "thousands of jobs"
        },
        {
          "@type": "PropertyValue",
          "name": "Net employment change",
          "description": "Change in all employees over the selected horizon, from one month to twenty years",
          "unitText": "thousands of jobs"
        },
        {
          "@type": "PropertyValue",
          "name": "Percent employment change",
          "description": "Change in all employees over the selected horizon as a percentage of the base period level",
          "unitText": "percent"
        }
      ],
      "creator": {
        "@type": "GovernmentOrganization",
        "name": "US Bureau of Labor Statistics",
        "url": "https://www.bls.gov/",
        "sameAs": "https://en.wikipedia.org/wiki/Bureau_of_Labor_Statistics"
      },
      "publisher": { "@id": "https://www.data4thepeople.com/#organization" },
      "includedInDataCatalog": {
        "@type": "DataCatalog",
        "name": "BLS Public Data API",
        "url": "https://www.bls.gov/developers/"
      },
      "distribution": [
        {
          "@type": "DataDownload",
          "name": "Current view as CSV",
          "encodingFormat": "text/csv",
          "contentUrl": "https://data4thepeople.github.io/NFP_Treemap/dist/index.html"
        }
      ],
      "sameAs": "https://www.bls.gov/ces/",
      "isBasedOn": [
        "https://www.bls.gov/ces/",
        "https://www.census.gov/naics/"
      ]
    },
    {
      "@type": "WebApplication",
      "@id": "PAGE_URL#tool",
      "name": "US Nonfarm Payrolls by Industry Treemap",
      "url": "https://data4thepeople.github.io/NFP_Treemap/dist/index.html",
      "description": "Free interactive treemap of US nonfarm payroll employment. Drill from total nonfarm down to six-digit NAICS industry detail, set any base month back to 1939, compare horizons from one month to twenty years, and export the current view as CSV or PNG.",
      "applicationCategory": "BusinessApplication",
      "applicationSubCategory": "Data visualization",
      "operatingSystem": "Web browser",
      "browserRequirements": "Requires JavaScript",
      "isAccessibleForFree": true,
      "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD"
      },
      "featureList": [
        "Drill down through eight levels of the BLS industry hierarchy",
        "Select any base month from January 1939",
        "Compare one month to twenty years",
        "Absolute and percent change colour metrics",
        "Official Census NAICS definitions on hover",
        "Anomaly scoring against each industry's own history",
        "CSV and PNG export",
        "Deep-linkable views and embeddable iframe"
      ],
      "about": { "@id": "PAGE_URL#dataset" },
      "creator": { "@id": "https://www.data4thepeople.com/#organization" }
    },
    {
      "@type": "Organization",
      "@id": "https://www.data4thepeople.com/#organization",
      "name": "Data 4 The People",
      "url": "https://www.data4thepeople.com/",
      "description": "A public-interest data journalism organization working to rebuild a shared understanding of truth through data.",
      "sameAs": ["https://github.com/Data4ThePeople"]
    }
  ]
}
```

### What each node is actually worth

**Dataset** feeds Google Dataset Search, and nothing else. It produces no rich
result in ordinary Google Search. It is still worth emitting, because Dataset
Search is a low-competition surface aimed squarely at the researcher audience
this tool serves, and `distribution.contentUrl` is real here because the CSV
export exists.

**WebApplication** will not produce a rich result. Google requires
`aggregateRating` or `review` for the software app rich result, and a rating in
markup must correspond to one visibly displayed on the page. Do not invent one.
The node is worth keeping for entity clarity, which is what AI answer surfaces
read.

**BreadcrumbList and Organization** still render in search results normally. The
importer emits the breadcrumb already.

**FAQPage is now cosmetic.** Google deprecated FAQ rich results and removed the
documentation in June 2026. The markup is still valid schema.org and harmless,
and the importer emits it automatically from the `### question?` headings, so
there is nothing to do. The FAQ section still earns its place: those answers are
written to stand alone for AI answer extraction, which is where that traffic now
goes.

---

## 3. Ranking ahead of the Bancreek version

You have no stake in Bancreek and are not being paid to maintain their copy, so
nothing here depends on their cooperation. This is what wins without it.

### What you are actually up against

Their two pages are not equally strong, and the weak one is not the problem.

**The tool page** (`/p/us-employment-data-treemap`) is 280 body words wrapping a
JavaScript-injected Tableau embed. None of the tool's content is crawlable. It
ranks for exact and brandish phrases only, and it does not lead even for its own
title. This one you beat on the first day.

**The explainer** (`/p/visualizing-nonfarm-payroll-data`) is the real competitor:
3,079 words with `Dataset` structured data, and it takes the descriptive queries
that matter, the "nonfarm payrolls by industry interactive treemap" shape. It is
a fair fight rather than a walkover.

You win it on four things they no longer have.

1. **A working, current tool.** Theirs is a Tableau embed of the older build.
   Yours is the live tool, refreshed from the BLS API after every release.
2. **Freshness.** They have let it go stale and are not paying to change that.
   For a monthly-data query, a page that visibly updates each release and one
   that does not diverge quickly.
3. **Depth.** 3,854 words with methodology, a limitations section and twelve
   FAQ answers written to stand alone, against 3,079 words of explainer.
4. **Coverage they cannot match.** Their title is brandish and their explainer
   is interpretation. Yours targets the tool-intent and question queries
   directly, and carries `Dataset` markup pointing at a real CSV export.

### The plan, in priority order

1. **Publish, then get it indexed deliberately.** Submit the URL in Search
   Console the day it goes live rather than waiting to be crawled. Add a
   `Sitemap:` line to the Data 4 The People robots.txt, which is currently
   missing one.
2. **Internal links, which is your biggest controllable lever.** The site has
   twelve labor-market posts and none of them link here yet, while Bancreek
   links to its treemap from five of its monthly recaps. Add links from
   `beyond-the-unemployment-rate`, `cps-intro-post`, `labor-force-history-viz`,
   `the-us-manufacturing-job-renaissance` and `she-carried-the-jobs-recovery`,
   and from every labor post from here on. Use the target phrasing as the anchor
   text, not "click here".
3. **The github.io credit link, now shipped.** The hosted tool carries a credit
   line linking back to this article, and the embedded layout hides it, so the
   link appears on the standalone page you control and not inside the iframe
   where it would only link to itself. That is a real cross-domain link from a
   page that will accumulate its own traffic.
4. **External links, where you already have an advantage.** Third-party
   editorial coverage of Data 4 The People exists and is specifically about the
   jobs report, including two Excess Returns episodes and Monetary Matters.
   Third-party mentions of bancreek.com are directory listings. Get the tool URL
   into those show notes. On-topic, real, and the cheapest links available.
5. **Keep publishing the monthly cadence.** Their copy goes staler every month
   you refresh yours. That gap widens on its own.

### What not to do

**Do not canonical or noindex anything to resolve this.** The two articles share
zero eight-word sequences, so there is no duplication for Google to cluster and
nothing for a canonical to consolidate. Separate registered domains are also not
merged by the results-diversity rule. Both pages can rank at once, and that is
the normal outcome rather than a problem to fix.

**Do not spend effort on their structured data or their stale dates.** Their
JSON-LD dates contradict their visible dates and their schema image is orphaned.
Not your responsibility, and fixing it would only help a page you are trying to
outrank.

**Do not link to them.** Nothing in this post references Bancreek, and it should
stay that way. A link from you to them moves signal in exactly the wrong
direction.

The reassuring part: for the tool-intent queries the results page is close to
empty, with a Go treemap library and a university course assignment filling
slots. You are not fighting for a contested position. You are the only person
who has built the thing.

## 4. The two GitHub Pages URLs

**The tool stays indexable, with no canonical and no noindex.** The only
controlled test of how Googlebot handles iframes found that a parent page can
rank for content that exists only in the framed URL, and that a noindex on the
framed URL removes that ability. Noindexing the tool would strip it from both
posts. A canonical is equally wrong: a 164-word tool and a 3,854-word article
are not equivalent pages, and Google ignores canonicals between non-equivalent
URLs. The build now emits a meta description; the levers for canonical and
robots exist in `config.py` and default to empty on purpose, with the reasoning
recorded there.

**The repository root was the real liability and is now fixed.** Pages was
rendering README.md at `/NFP_Treemap/` under the title "U.S. Employment Data
Treemap | NFP_Treemap" — the same string as the tool, with 2,016 crawlable words
against the tool's 164, and a self-referential canonical asserting itself as
preferred. If Google indexed both, the developer README about Python build
commands was the likelier page to rank for a query about jobs data. The
`_config.yml` now excludes it, so that URL stops being served. The README still
renders on github.com, which is the repository UI rather than Pages.

There is no robots.txt lever on that domain. `data4thepeople.github.io/robots.txt`
returns GitHub's "Site not found" because no organization Pages site exists, so
per-page tags and Jekyll exclusion are the only controls.

**Worth doing when this post is live:** add a visible credit link in the tool's
footer pointing back to the article. The link is worth more than the meta tag.

---

## 5. Unrelated but worth knowing

`data4thepeople.com` is on a one-year registration expiring 2026-10-29. Domain
expiry is not a confirmed ranking factor, but an eight-week runway is avoidable
risk. Renew multi-year.

---

## What not to claim

The research turned up one genuine free competitor for the form, so these would
not survive a reader checking:

- "The only free drill-down payroll treemap." The Bancreek one exists.
- "First" or "nothing like it exists." Same problem.
- "The most granular BLS employment data." QCEW goes deeper, to county and
  six-digit NAICS. It is quarterly, so "the most granular *monthly* payroll
  data BLS publishes" is accurate and safe.
- "Data back to 1939" without qualification. That is aggregates only; most
  industry detail starts in 1990. The post keeps that split visible throughout,
  which is what a researcher will check first.

The defensible position is not novelty of form. It is novelty of control:
arbitrary base month, anomaly scoring, export, deep links and embedding.
