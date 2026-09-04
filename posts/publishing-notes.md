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

## 3. Publishing on both sites: what the research settled

The worry was that publishing this on both bancreek.com and data4thepeople.com
would split the two against each other. Measured, it does not.

**The two articles share nothing.** Stripped to lowercase alphanumerics and
compared as eight-word shingles, the Bancreek explainer and this draft share
**zero** sequences. Jaccard similarity 0.0000. This is not a syndication or
duplicate-content case, so the canonical and noindex machinery aimed at
near-copies does not apply. Google clusters duplicates; with no overlap the
clustering never fires. Separate registered domains are also not merged by the
2019 site-diversity change, so both pages can appear at once.

**Why the Bancreek page ranks: because the results page is empty.** It is 280
body words with a JavaScript-injected Tableau embed and no crawlable tool
content. It does not lead even for its own exact title. Its co-results for
"jobs report treemap" include a Go treemap library and a university course
assignment. A results page reaching for a Go library to fill slots has no
supply. That page is not the competition. Nothing is.

**Where each domain is stronger.** Bancreek is older (2021 vs 2025), has fifteen
monthly nonfarm-payroll recap posts, and internally links to its treemap from
five of them. Data 4 The People has more volume and cadence but **zero** existing
payroll posts, and would launch with no internal links to this one. The one place
Data 4 The People wins outright is external editorial coverage, which is real and
specifically about the jobs report: two Excess Returns episodes, Monetary Matters,
and others. Third-party mentions of bancreek.com are directory listings only.

### The plan, in priority order

1. **Publish here first and leave Bancreek untouched for two to four weeks.**
   Let this page get crawled and ranked on its own merits before changing any
   competing signal, so you can see whether it wins unaided.
2. **Do not apply a cross-domain canonical or noindex to the Bancreek pages.**
   At zero overlap a canonical would either be ignored or, if honored, delete a
   page that can rank on its own.
3. **Differentiate by intent, not by rewriting.** Bancreek is monthly market
   commentary; this is the instrument and its methodology. One concrete edit:
   drop "Interactive Treemap Visualization" from the Bancreek explainer's title
   tag so the two stop bidding on the same string.
4. **Fix the Bancreek structured data.** Both pages ship JSON-LD dates that
   contradict their visible dates, and the tool page's schema image points at an
   orphaned S3 asset. Free to fix and it benefits the client.
5. **Link from Bancreek to here.** This is the highest-leverage item. Because
   signals never consolidate across two domains on their own, an editorial link
   is the only way this page inherits any of Bancreek's topical equity. Link
   from both Bancreek pages and from the monthly recaps. Do not reciprocate
   heavily.

Then: internal links from the existing labor posts, the tool URL into the
podcast show notes, and a `Sitemap:` line in robots.txt, which both sites are
missing.

**On redirecting the Bancreek page here.** A 301 is the strongest consolidation
signal Google documents and it would hand this page the one URL with proven
traction. It is not recommended, for three reasons: it is a client's asset and
that is a business decision rather than a technical one; five of Bancreek's own
posts link to it, so redirecting sends their readers off-site mid-funnel; and at
zero duplication there is no conflict to resolve, so it would be donating an
asset rather than consolidating one. If Bancreek's stake is winding down and you
choose it anyway, the order matters: publish here, wait four weeks, confirm this
page holds the position, then redirect. Never redirect into a page that has not
proven it can hold.

---

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
