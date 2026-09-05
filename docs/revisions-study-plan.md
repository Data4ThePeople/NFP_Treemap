# Do flagged prints get revised more? A study plan

**Status: plan only. Nothing here has been built or run.**

## The question

The tool marks an industry's month as *unusual* or an *anomaly* using the vintage
of the data available now. A reader seeing a fresh flag on release morning is
really asking a different question: **is this real, or will it be revised away?**

Three versions of it, in increasing order of usefulness:

1. Are flagged prints revised by more than unflagged ones, once you account for
   the fact that big changes get revised more anyway?
2. Do flagged prints **mean-revert** — is the revision more likely to run
   against the original move? This is the pattern you described for local
   government education.
3. **Does the flag survive?** Of the prints flagged on first release, what share
   are still flagged three months later? This is the number a reader actually
   needs, and it is the one that would go on the tool itself.

Question 3 is the headline. If the answer is "four out of five anomalies
survive", the flag is a trustworthy signal on release morning. If it is one in
five, the honest thing is to say so on the page.

## Why this is hard

**The BLS API serves one vintage: the current one.** Ask it for August 2026 today
and you get today's value, with no record of what it said on release morning.
Our own cache has the same limitation, because `--refresh` upserts, which is
correct for the tool and useless for this question.

So the study needs a *real-time* dataset: what each number was when it was first
published. That has to come from outside the BLS API.

## Candidate sources, in preference order

**1. ALFRED (St. Louis Fed).** The archival version of FRED. Its API takes
`output_type=4`, "initial release only", which returns exactly the first print of
every observation in a series — one request per series rather than one per
vintage. If coverage is adequate this is the whole data problem solved cheaply.
Needs a free API key.

The open question is **coverage**. FRED carries CES series, but likely the
aggregates and mid-level industries rather than all 842. A count of how many of
our industry codes map to a FRED series ID is the first thing to establish.

**2. BLS Employment Situation news release archives.** Every monthly release is
archived as HTML. Table B-1 carries the first print for roughly 80 industries at
display levels 2 to 4. Parsing 150 archived releases is tedious but entirely
doable, and it is authoritative in a way a third-party mirror is not. This is
the fallback if ALFRED's coverage is too thin, and a cross-check on ALFRED
either way.

**3. BLS revision tables.** BLS publishes its own summaries of revision size.
Useful for validating our numbers, not as the primary source, because they are
aggregated.

## The design flaw to avoid

The obvious approach is to take the prints we flag *today* and look up how much
they were revised. **That is look-ahead bias and it would invalidate the study.**
We would be flagging using post-revision data and then "predicting" the revision
we already used.

The flag has to be computed on the information available at first print. That
means, for each industry-month, the reference distribution has to be built from
what was known then.

There is a defensible shortcut. The reference distribution is twenty years of
that industry's changes, and revisions to months from years ago are tiny next to
its spread. So using the current vintage for the *reference distribution* while
using the first print for the *change being scored* is a reasonable
approximation. It has to be stated plainly, and phase 3 should test how much it
matters on the subset where full vintages are available.

## Design

**Unit of observation.** One industry-month first print.

**Definitions.**

- `P1(i, m)` — the value for industry i in month m as first published, in the
  release covering month m.
- `P4(i, m)` — the value three releases later, after both scheduled revisions.
- `R = P4 − P1`, the revision. `C1` is the first-print one-month change.

Two candidates for "settled", and this is a decision to make up front:

- **+3 months.** After the two scheduled revisions. Clean, fast, and it is the
  window a reader cares about.
- **Post-benchmark.** After the annual benchmark, which can restate five years.
  Truer to "final", but it delays every observation by up to eighteen months and
  mixes in a different revision process.

I would run the primary analysis at +3 months and report the benchmark version as
a robustness check.

**Predictor.** The tier at first print: none, unusual, anomaly.

**Outcomes.**

| outcome | measures |
|---|---|
| `abs(R)` | revision magnitude |
| `abs(R) / abs(C1)` | revision relative to the move itself |
| `sign(R) != sign(C1)` | reversal |
| tier at P4 | whether the flag survives |

**The control that matters.** Big changes get revised more, and flagged changes
are big by construction. Comparing flagged to unflagged without controlling for
magnitude would find an effect that is pure selection. Two ways to handle it,
and both should be reported:

- Compare within magnitude bins — flagged versus unflagged prints of similar
  size.
- Regress `abs(R)` on `abs(C1)`, industry fixed effects and a tier dummy, and
  read the tier coefficient.

**Sample size.** Roughly 150 months. With ALFRED coverage of even 60 industries
that is ~9,000 industry-months, of which ~8% are watch tier and ~1% anomaly, so
about 700 watch and 90 anomaly observations. Enough for the watch tier
comfortably, thin but workable for the anomaly tier. If coverage is only 30
series, the anomaly tier will be too thin to say much and the study should be
framed around the watch tier.

## Phases

**Phase 0 — feasibility, half a day.** Get a FRED key. Count how many of the 842
industry codes map to a FRED series. Confirm `output_type=4` returns what the
docs say. Pull three series end to end and eyeball the first prints against two
archived BLS releases. **Stop and report before going further** — if coverage is
under about 30 series, the study changes shape and that is worth a conversation
rather than a workaround.

**Phase 1 — build the real-time dataset.** First prints for every mappable
series, stored beside the existing parquet as a separate vintage table. Never
merged into `ces_observations.parquet`, which must stay current-vintage for the
tool.

**Phase 2 — recompute flags at first print** and join the outcomes.

**Phase 3 — analysis.** The three questions, the magnitude control, and the
sensitivity check on the reference-distribution shortcut.

**Phase 4 — write it up**, and decide whether anything belongs in the tool.

## What this could add to the tool

This is the part that would matter beyond one post. If the survival rate is
solid, the tooltip could carry a line like "anomalies flagged on first print
have held about four times in five since 2013", which no other free labor tool
offers because none of them score anomalies in the first place. If the rate is
poor, saying so is still better than silence, and it is the kind of honesty the
rest of the page already runs on.

A second possibility, if the data supports it: a per-industry typical revision
size, so a reader can see that this industry moves by 8,000 on first print and
gets revised by 3,000 on average.

## Decisions needed before phase 1

1. **Settled at +3 months or post-benchmark?** My recommendation is +3 months
   primary, benchmark as robustness.
2. **Scope.** Whatever ALFRED covers, or restrict to levels 2 to 4 where the BLS
   archives give a clean fallback and the industries are ones readers recognise?
3. **Is a thin anomaly tier acceptable**, with the study framed on the watch
   tier, or should phase 0 stop the work if the anomaly sample is under about
   100?
4. **Separate post, or a section added to the existing one?** My view: separate.
   The current post is evergreen and this one is a finding.

## Risks

- **Coverage.** The most likely failure. Mitigated by the BLS archive fallback,
  at the cost of more work and fewer industries.
- **Series ID mapping.** CES industry codes to FRED IDs is not a clean
  transformation and may need a hand-built map for the industries that matter.
- **Regime change.** Revision behaviour after 2020 is not the same as before.
  Report pre-2020 and post-2022 separately rather than pooling.
- **Multiple testing.** Three questions across two tiers and several outcomes.
  Pre-register the primary comparison — survival rate of the anomaly tier at +3
  months — and label the rest exploratory.
