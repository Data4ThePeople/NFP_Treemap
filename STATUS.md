# Status

Project: NFP_Treemap
Process: ~/.claude/d4tp-process/PROCESS.md

## Current

Post: none yet (October 2026 jobs report; slug set in 2a)
Step: 1
Since: 2026-11-06

## Steps

| Step | What | Confirmed | Notes |
|---|---|---|---|
| 1  | Exploration and analysis | | |
| 2a | Draft with brackets resolved | | |
| 2b | Eric's edit, Claude's look-over | | |
| 2c | Slice markup | | |
| 2d | Hero 1680x1080 + alt text | | |
| 2e | SEO | | |
| 2f | Pushed to Prismic (draft) | | |
| 2g | Mailchimp teaser | | |

## Stale

None.

## Log

- 2026-10-04 Step 1 opened. Topic: an update on the latest NFP release (September 2026 data, released October 2, 2026, with July and August revised). The project's earlier post, nonfarm-payrolls-by-industry (the explorer's manual), predates this file; it was re-pushed to Prismic on 2026-10-02 with updated_date 2026-10-02 11:00 EDT.
- 2026-10-04 Starting material from the October 2 session: August revised from +162,000 to +133,000; restaurants and other eating places (+110,400) and local government education (+49,300) together +159,700, both rebounding from July losses (-94,000 and -52,000); the restaurant series does not add up to its parent (food services +33,800). September +29,000, health care and social assistance +23,000. QCEW 2025 annual pay: restaurants $27,798, local government education $62,024, all other industries $83,794; services for the elderly and persons with disabilities plus home health care, weighted, $34,162. Social copy in posts/social-2026-10-02-august-revisions.md.
- 2026-10-04 Step 1 confirmed by Eric: the post is already written, so no separate exploration. Step 2a opened, slug september-2026-jobs-report. Eric's draft placed in POST.md verbatim; every number checked against the October 2 data and QCEW 2025. Five charts and twelve edits proposed (edit 6: the restaurant series, +110,400, does not add up to its parent food services, +33,800).
- 2026-10-04 2a: Eric accepted edits 1-12 and charts 1-5; charts built (tools/september_2026_charts.py, numbers in posts/september-2026-jobs-report/numbers/). Title 'How to Analyze U.S. Jobs Data' (Eric). Video embedded (YouTube Pk_GuM4U0c4). Five section headers added at Eric's request.
- 2026-10-04 Step 2a confirmed by Eric. Food services (+33,800) kept in place of restaurants (+110,400): the restaurant series' swing comes from its separate seasonal adjustment; unadjusted, the parts sum to food services exactly.
- 2026-10-04 Step 2b opened: Eric edits POST.md, then Claude looks it over.
- 2026-10-04 2b: Eric's edits plus three Claude rewrites he asked for (parenthesis examples, the 'still useful' section). Look-over items 1-10 accepted. Channel link https://www.youtube.com/@Data4ThePeople. Publish date October 5, 2026, 6:45 am EDT (date + time in front matter).
- 2026-10-04 Step 2b confirmed by Eric.
- 2026-10-04 Step 2c opened. Defaults kept (drop cap, 20px heading and caption spacers, no dividers; no extras section, so no end divider). Added a 20px spacer after the video embed. Convert-only: 30 slices, 5 images, 1 embed.
- 2026-10-04 Step 2c confirmed by Eric.
- 2026-10-04 Step 2d opened.
- 2026-10-04 2d: AI-image path, magnifying-glass concept (Eric). Prompts written to hero-prompt.md.
- 2026-10-04 2d: magnifying-glass images did not work; switched to a balance scale with work clothes (two sets against one suit jacket, pans level).
- 2026-10-05 Chart 1 animated (Eric): dots alone, margin-of-error bars grow out, colors resolve, hold, loop. images/01-margin-of-error.gif replaces the PNG in the post; the PNG stays as the still.
- 2026-10-05 2d: new hero concept from Eric: the word JOBS with the O as a magnifying glass over a miniature economy, illustrated. Prompts A and B in hero-prompt.md.
- 2026-10-05 2d: hero = Gemini JOBS illustration (Prompt A), hero fit --focus bottom, light D4TP logo lower left; alt text 491 characters. hero check ok.
- 2026-10-05 2d: logo moved onto the magnifying-glass handle (Eric), dark version, rotated to the handle's angle; alt text 483 characters.
- 2026-10-05 2d: logo moved up the handle and centered across the grip (Eric), 44px high.
- 2026-10-05 Step 2d confirmed by Eric.
- 2026-10-05 Step 2e opened.
- 2026-10-05 2e: searches from Claude's list (Eric: use those). Meta title 46, description 145, 8 keywords; Article schema checked. Text proposals sent.
- 2026-10-05 2e: link to Giants Walk Among Us added on '82% of all jobs added in this country' (Eric).
- 2026-10-05 2e: proposals 2, 3, 5 accepted, 4 rejected; subtitle per Eric's wording (proposal 1 revised).
- 2026-10-05 Step 2e confirmed by Eric.
- 2026-10-05 Step 2f opened. Dry run then publish: created draft asNvTREAACgASG64 (uid september-2026-jobs-report) in the Migration Release; 30 slices; 6 images uploaded (5 charts + hero). Dated 2026-10-05 6:45 am EDT. Animated chart checked as served: 37 frames as GIF and as AVIF (Prismic's auto=format). Before publishing: set author and tags in Prismic.
- 2026-10-05 Step 2f confirmed by Eric. Step 2g opened.
- 2026-10-05 2g: EMAIL.md drafted (hero, opening two paragraphs, pay chart, the August and three-year hooks, video mention); hero email JPG 146 KB; every number checked against the post.
- 2026-10-05 Step 2g confirmed by Eric (approved as drafted). september-2026-jobs-report complete (steps 1 through 2g confirmed). In Prismic: set author and tags, then publish draft asNvTREAACgASG64 from the Migration Release.
- 2026-10-05 2g follow-up (Eric): email chart changed to the static margin of error chart (images/01-margin-of-error.png).
- 2026-10-05 Social copy: posts/september-2026-jobs-report/SOCIAL.md, two versions (GIF, native tutorial video) for X and LinkedIn; supersedes social-2026-10-02-august-revisions.md.
- 2026-11-06 Step 1 opened for the next post: the October 2026 jobs report (released 2026-11-06; August and September revised). The september-2026-jobs-report post is complete (steps above were reset for the new post; its record is in git history). Order reversed at Eric's request: social reaction posts first (a GIF of the explorer stepping from level 0 to level 5, plus LinkedIn and X copy), the post itself next week. Eric's take: broad-based strength, first estimate, few unusual moves to flag.
- 2026-11-06 Reaction GIF and MP4 (levels 0-5, October 2026), LinkedIn and X copy in posts/october-2026-jobs-report/SOCIAL.md; DATASETS.md written. Own tie-out and independent fresh-agent tie-out both matched every number (75% is 74.5% rounded). Could not check: LinkedIn-editor and hashtag notes. Agreed framing: solid, not unusual (Eric's 'broad-based' dropped: level 3 breadth 58% vs 2013-2026 median 74%). Next week's post must carry every number in the social copy.
- 2026-11-06 Social copy (Eric): second leader changed from private education and health services (+53,000) to health care and social assistance (+55,100, level 3); with professional and business services (+70,000) that is 76% of the total (125,100 of 165,000).
- 2026-11-06 Second independent tie-out (fresh agent) on the health care version: all numbers matched. Fixed three wording issues it raised: X post named 'health care' (a separate BLS series, +41,600) and 'business services', now full names; '6 industries' now '6 industry series, about 4 separate industries' (nested series); GIF level 1 caption named 3 of 4 tiles, now '4 broad groups, which overlap'. GIF and MP4 rebuilt.
- 2026-11-06 Eric's LinkedIn edits merged verbatim into SOCIAL.md; proposed edits 1 (6 industry series, about 4 separate industries) and 2 ('This video', MP4 on LinkedIn) accepted.
