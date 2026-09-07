# Brief: posts are publishing an empty structured-data tag

Forward this as-is. It is self-contained.

## Symptom

35 of the 89 posts on data4thepeople.com render this in `<head>`, with nothing
between the tags:

```html
<script type="application/ld+json"></script>
```

Examples: `/p/american-income-fragility/`, `/p/children-poverty-viz/`,
`/p/the-wage-ledger/`, `/p/viral-labor-force-decline/`.

Verified by rendering the pages in a headless browser, so it is not being
hydrated later by client-side JavaScript. The tag is empty in the final DOM.

## Cause

The post document type in Prismic has a `schema` text field holding hand-written
JSON-LD. The page component prints it into a script tag unconditionally. On the
54 posts where somebody filled it, that works. On the other 35 it emits an empty
tag, and those pages publish no structured data at all.

## The change

Two parts, in the post page component.

**1. Do not render the tag when the field is empty.**

**2. When it is empty, fall back to a generated Article graph** built from
fields the page already has. All 35 already expose title, description, image and
published date in their meta tags, so no new data is needed.

```js
const raw = post.data.schema?.trim()
const schema = raw ? JSON.parse(raw) : buildArticleGraph(post)

useHead({
  script: schema
    ? [{ type: 'application/ld+json', innerHTML: JSON.stringify(schema) }]
    : [],
})
```

`buildArticleGraph` should emit a `@graph` of Organization, WebSite, WebPage,
Article and BreadcrumbList. A worked example for every one of the 35 posts,
generated from that post's own metadata, is in `docs/schema-backfill/` of the
NFP_Treemap repository — use one as the shape.

Wrap the `JSON.parse` in a try/catch. A malformed hand-written field should fall
back to the generated graph rather than throwing.

## Why do it this way

The alternative is pasting JSON into 35 documents by hand. That fixes 35 posts
and nothing else; the 36th post ships broken the first time somebody forgets the
field. Fixing the template fixes every post, past and future, in one deploy, and
leaves the hand-written field working as an override for the pages that need
something richer than an Article.

## How to verify

1. Pick any of the four example URLs above and confirm the tag now has content.
2. Run it through Google's Rich Results Test. It should report an Article with
   no errors.
3. Confirm a post that already has a hand-written schema is unchanged, for
   instance `/p/us-fertility-rate-by-county/`, which carries a Dataset. The
   override path must still win.

## Unrelated, but while you are in there

`robots.txt` does not name the sitemap. The sitemap itself is fine at
`https://www.data4thepeople.com/sitemap.xml`. Add one line:

```
Sitemap: https://www.data4thepeople.com/sitemap.xml
```

It is likely a static file at `public/robots.txt`.
