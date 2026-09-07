# 35 posts serve an empty JSON-LD tag

## What is wrong

35 of the 89 posts render this, with nothing between the tags:

```html
<script type="application/ld+json"></script>
```

Confirmed by rendering one in a headless browser, so it is not being filled in
later by JavaScript. Those posts publish no structured data at all. The `schema`
field on the document is simply empty, and the template prints it regardless.

Every one of the 35 already exposes what structured data needs, in its meta
tags: title, description, image and published date, all 35 for all four. So
nothing has to be researched or written. The information is already on the page,
just not in a form a machine reads.

## The fix, and it is not 35 edits

**Change the template, not the content.** The page component renders the schema
field unconditionally. It should do two things instead:

1. **Not render the tag when the field is empty.** An empty script tag is not
   harmful, but it is noise, and it hides the problem: the pages look like they
   have structured data until you read it.
2. **Fall back to a generated Article graph** built from the fields the page
   already has. Roughly:

```js
// in the post page component
const schema = post.data.schema?.trim()
  ? JSON.parse(post.data.schema)
  : buildArticleGraph(post)      // title, description, image, date, author

useHead({
  script: schema
    ? [{ type: 'application/ld+json', innerHTML: JSON.stringify(schema) }]
    : [],
})
```

That fixes all 35 at once, costs one deploy, and — the part that matters more —
means no future post can ship without structured data because someone forgot to
fill a field. The hand-written `schema` field stays the override for pages that
need something richer, which is how the visualization posts already work.

## The fallback, if the app cannot be touched

`docs/schema-backfill/` holds a ready graph for each of the 35, one file per
slug, generated from that page's own metadata. Each contains Organization,
WebSite, WebPage, Article and BreadcrumbList. Paste the file's contents into
that post's `schema` field in Prismic.

This is the worse option. It is 35 manual edits, it does nothing for post 36,
and it duplicates into content what belongs in a template.

## How much this is worth

Honestly: moderate, and worth doing only because it is cheap the template way.

Article structured data earns few rich results now; Google cut most of them
back. The value is entity clarity — telling a crawler what the page is, who
wrote it, when, and what it belongs to — which is what the answer engines read
even when nothing renders in the results page.

That is worth one template change. It is not worth 35 rounds of copy and paste,
which is the argument for fixing it in the app.

## Not related to the creator warning

This is a separate finding from the Search Console alert. These 35 have no
Dataset markup at all, so they cannot be the source of a missing-field warning
about one. That points at `war-tax-viz`, which supplies its Dataset creator as a
bare `@id` reference rather than an inline object.
