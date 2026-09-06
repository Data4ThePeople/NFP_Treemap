# Internal links to add, by hand, in Prismic

**These cannot be scripted.** The Content API token here is write-only for types
and assets, so the other posts cannot be read; the importer only updates
documents it created, and this repository holds one of them. Even with full
access, a publish rewrites a whole document from Markdown, and the Markdown for
these posts does not exist here. Running the importer at them would destroy
them.

So this is a paste job. Each link goes in the Prismic editor, on the post named,
as a hyperlink on the bolded anchor text.

Target for all of them:
`https://www.data4thepeople.com/p/nonfarm-payrolls-by-industry`

## Why the anchor text varies

Every link pointing at a page with the same words looks automated and is worth
less than a set of links that read like sentences someone wrote. Each one below
uses different wording, and each one leads with a phrase somebody actually
searches.

## The six worth doing, strongest first

**1. Giants Walk Among Us** — `/p/giants-walk-among-us/`
The closest match in subject: it is CES industry concentration, which is what
the explorer shows. This is the single most valuable link on the list.

> The same survey publishes hundreds of industries beneath that headline. You
> can **explore nonfarm payrolls by industry** yourself, and see which months
> were unusual rather than merely large.

**2. The fastest growing industry in America** — `/p/mental-health-jobs/`
It already reasons across roughly 700 industries, which is exactly the surface
the tool draws.

> Every industry in this piece comes from the BLS payroll survey. The full
> **drill-down of jobs data by industry** is here, back to 1939.

**3. The US Manufacturing Job Renaissance** — `/p/the-us-manufacturing-job-renaissance/`
Industry-specific, so the link can point at a specific view rather than the
front page.

> Manufacturing is one of eleven supersectors in the payroll survey. See
> **manufacturing employment against every other industry**, and how unusual
> each month was.

Deep-link it if you want it to open on manufacturing:
`https://www.data4thepeople.com/p/nonfarm-payrolls-by-industry` is the post, and
the tool inside it takes `#drill=30000000&lvl=4`.

**4. America's Aging Is Concentrating Job Growth** — `/p/medicaid-care-economy-post/`
Care-economy employment, drawn from the same survey.

> This is one industry inside a survey that publishes hundreds. The rest are
> **in the payroll data explorer**, scored against their own histories.

**5. The New Rosie Wears Scrubs** — `/p/she-carried-the-jobs-recovery/`
It already bridges the payroll survey and the household survey, so it can carry
a link to each tool.

> For the payroll side of that story, industry by industry, see
> **which industries are actually driving job growth**.

**6. Beyond the Unemployment Rate** — `/p/beyond-the-unemployment-rate/`
and **We Built the Labor-Market Tool That Didn't Exist** — `/p/cps-intro-post/`
The two tools are siblings, one per survey, and should point at each other. The
new post already links back to the CPS explorer, so this closes the loop.

> That tool covers the household survey. Its counterpart for the employer
> survey, **nonfarm payrolls broken out by industry**, is here.

## Two rules worth keeping

**Put the link in the body, not in a footer or a related-posts block.** A link
inside a sentence a reader might follow is worth considerably more than one in
a list of links at the bottom, and the template already generates the latter.

**Add one to every labor post from here on.** The value is cumulative and it
costs a sentence. This is the lever that is fully within your control, and right
now the count is zero.
