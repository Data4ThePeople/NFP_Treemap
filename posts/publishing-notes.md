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

**The `src` is not live yet.** GitHub Pages is not enabled on the repository —
`gh api repos/Data4ThePeople/NFP_Treemap/pages` returns 404. Enable Pages on the
`main` branch from the repository root and that URL serves the tracked
`dist/index.html` unchanged. Nothing else needs to move.

Verified frame heights for the 879px Prismic column: 640, 780, 1200 and 1300 all
fit without the frame scrolling. Below 560 the chart holds a readability floor
and the frame scrolls instead.

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

## 3. One decision before publishing

There is an existing, ranking page for essentially this tool:
[bancreek.com/p/us-employment-data-treemap](https://www.bancreek.com/p/us-employment-data-treemap),
with an [explainer](https://www.bancreek.com/p/visualizing-nonfarm-payroll-data/),
published April 2025. It is currently the only on-topic result ranking for
"jobs report treemap," which is the best low-competition query in this space.

Two similar tools under related authorship competing for the same thin results
page splits the signal and helps neither. Worth deciding which of these happens
before the new post goes live:

1. **Redirect** the Bancreek pages to the new post. Cleanest, and it passes the
   existing ranking signal to the new page.
2. **Point the old page at the new one** with a prominent canonical link, if the
   Bancreek pages need to stay up for their own reasons.
3. **Differentiate deliberately**, keeping Bancreek's as the firm-branded
   version and this as the public-interest one, accepting that they compete.

What the new tool has that the old one does not: a selectable base month (the
old one anchors everything to the latest month), anomaly scoring, CSV and PNG
export, deep links, and an embeddable frame. That is the honest differentiator
and it is worth leading with if you keep both.

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
