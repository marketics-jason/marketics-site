# Marketics Claims Canon Registry

**Version:** v3.0 · **Maintained by:** Code, on ruling from CTO/Strategy · **Public visibility:** internal only — force-shadowed to 404 in `_redirects` (see bottom of that file), same pattern as `marketics-site-audit-2026-07.md`.

This file is the single in-repo source of truth for performance-claim wording, retired phrasings, and market-tier framing. Every ruling that changes what the site is allowed to say should land here in the same PR that enforces it. `scripts/validate-site.py` `RETIRED_TOKENS` is the mechanical enforcement layer for the phrasings below — when adding a retired token here, add it there too.

---

## The performance canon (unchanged since v2.x, restated for reference)

- **45% median, net of market, documented, across 19 documented engagements.** This is the single published performance figure. Never "42%+". Never a range. Never a second, differently-sourced performance percentage presented as if comparable — a second figure must either share the Index's baseline (STR-to-STR, net of market) or state its own baseline inline, same breath.
- **The gate sentence** accompanies the 45% figure wherever the format allows: *"results are property-specific; every property is audited before any target is set."*
- **Tenure:** "the past decade." Never "20 years" in an STR context.
- **Footprint:** "1,000+ listings across 22 markets" is experience and social proof — lifetime footprint, not a claim of 22 *active* markets and not the sample the 45% median is measured against.
- Performance claims link to the STR Performance Index as the canonical methodology home rather than restating variants.

## v2.7 — same-breath baseline rule (2026-07-27 ruling)

**Rule:** wherever a performance figure and a footprint/count figure sit adjacent (same section, same summary block, same sentence group) with no stated relationship between them, that is a canon violation — an "adjacency-without-distinction" instance. The fix is always the same shape: **performance number + named baseline + date, in the same breath.** A methodology link alone does not satisfy this — links don't travel with extracted spans (AI summarizers, snippet extraction).

**Ruled pattern** (homepage Key Takeaways, applied 2026-07-2x):
> "1,000+ listings optimized across 22 markets over the past decade; the 45% median comes from the 19 engagements with complete before/after documentation (2019–2026)."

*(Window corrected from 2024–2026 to 2019–2026 per the v2.9 Board ruling below.
The shape of the rule — number + named baseline + date, same breath — is
unchanged; only the date was wrong.)*

**Footer tagline resolution:** the site-wide footer tagline could not carry baseline + gate in a one-line brand tagline, so the 45% clause was **dropped** from the footer (site-wide, 49 pages) rather than patched — the 45% claim continues to live, gated and sourced, on every page that actually makes the claim (homepage, /results, /pricing, case studies, the Index). Footer now reads: *"Full-stack short-term rental revenue · 1,000+ listings across 22 markets."*

**Homepage hero stat tile** ("45% / Median lift / net of market," standalone, no adjacent footprint number in the same tile row) — reviewed and left as-is. The full claim (baseline + count + date) sits immediately below in Selected Work and Key Takeaways; the tile itself has no adjacent footprint figure to create ambiguity against.

## Retired framings — market operational depth (v2.7 correction)

**"3 active markets" / "active depth markets" / "22 active markets" are retired.** This was a regression: PR #92 applied "operational depth = 3 active markets" site-wide, which is the retired shape from the original 42/45 failure mode. The July 8 three-tier canon superseded it:

| Tier | Markets |
|---|---|
| **ANCHOR** | San Antonio |
| **Candidates** | Orlando, Hill Country |
| **Convening bases** | Miami, Montréal |
| **Optimization-only** | Tulum |

**This tier structure is internal-only — never public copy.** Public-facing language never states an active-market count. Canon for public surfaces:
- "we optimize in any market — the method travels"
- "1,000+ listings across 22 markets" (lifetime footprint)
- Never: "22 active markets," "3 active markets," or any variant asserting a live operational-market count.

`llms.txt` was reframed off the active-market count (was: "Service area: … (22 active markets)" and "Marketics operates in 22 active markets…") to footprint framing, consistent with the rendered-page canon.

## Item 1 — calculator baseline (2026-07-2x finding, no change required)

**Finding:** the calculator's ~32% figure = the median **gross** uplift of "top-performer" comps (the average of Marketics-managed properties per city) over the market-average benchmark, across the calculator's city models — gross booking revenue, not the net-of-market pre/post-engagement basis of the documented 45% median.

**Disposition:** no code change required. The calculator renders a **dollar walk** (current → market benchmark → with-Marketics, in $/mo), never a standalone performance percentage; the top-performer basis is named inline in the benchmark-table caption and the calculator FAQ; `+32%` is already a `RETIRED_TOKENS` entry; the underlying constant is real per-city data with no "conservative" caption to contradict it. Confirmed by CTO 2026-07-2x.

## v3.0 — BOARD RULING: Consent Mode v2 + EEA/UK/CH region gating (2026-08-21)

**Ruling:** add Consent Mode v2 **and** region-gate the banner to EEA/UK/CH, so
US/Canadian traffic — the actual market — measures normally. Treated as a
**pre-flight gate for paid**: no ad spend is read as valid until measurement
works, because CAC cannot be read through a blind analytics install.

**Recorded caveat, at the Board's instruction.** The region-gate half rests on a
PIPEDA / US-state-privacy judgment. Jason made the call and it is a standard
posture. This registry entry is the record of a **business decision, not a legal
opinion** — if it is ever pressure-tested, that is a counsel question, not a Code
one.

**What changed.** The prior build was a hard block: `gtag.js` was never requested
until an Accept click, so declined and undecided traffic was invisible to GA4
entirely (2 measured users against 28 GSC clicks). Now `gtag.js` loads on every
path and the consent *signals* decide what may be stored, so denied traffic
contributes cookieless pings instead of nothing.

**`ad_*` stays denied everywhere — including after an Accept.** The banner copy
promises *"No advertising or third-party tracking."* Granting `ad_storage`,
`ad_user_data` or `ad_personalization` would contradict the notice the visitor
just read. **This is a live constraint on the paid launch:** Google Ads
conversion tracking will want those signals, and turning them on requires
changing the banner copy *first*. That is a Strategy/Board call, not a Code one,
and it should be settled before ads run rather than discovered mid-campaign.

**Region detection is deliberately split.** The consent *signals* are
region-scoped by Google server-side via the `region` parameter — authoritative.
The *banner* is gated by browser timezone, which is approximate, over-inclusive
(any `Europe/*` zone), and fail-safe (a detection failure shows the banner).
Mismatches degrade safely in both directions.

**Also:** Clarity has no consent-mode equivalent and sets cookies
unconditionally, so it remains gated on an actual grant. The
impression/accept/decline beacon is retained and now deduped once per session —
the banner re-renders on every pageview until answered, and one webhook call per
pageview would have swamped the CRM.

---

## v2.9 — BOARD RULING: the window is 2019–2026 (2026-08-21)

**This supersedes v2.8's window statement below, which was wrong.** Recorded here
as a Board ruling rather than a silent PR, at the Board's explicit instruction.

**Ruling:** the documented span is **2019–2026**, sample **19 documented
engagements**, median **45% net of market**, range **−3% to +193%**. Confirmed by
Jason from direct knowledge of the engagements.

**What went wrong.** PR #95 (2026-07-25) narrowed the label from 2019–2026 to
2024–2026 on an *assumption* about COVID-era demand distortion. That was an
unverified Code-side change and it was incorrect — some of the 19 documented
engagements fall outside 2024–2026, so the count and the window contradicted each
other. COVID distortion is already handled by **"net of market,"** which is the
correct mechanism; you don't relabel the window to clean the data. Reverted
across all 22 instances site-wide on 2026-08-21.

**The load-bearing check, and its result.** The Board asked whether the 45%
median had been silently recomputed on the narrowed 2024–2026 set — which would
have made the headline figure wrong and put a wrong number into paid ads.
**It was not.** Verified in git history:

- `a030885` is the commit that *created* `/intel/str-performance-index`
  (confirmed via `--diff-filter=A`). The figures were born there as 45% median,
  range −3% to +193%, 19 engagements, **measured 2019–2026**.
- PR #95 changed *only* the window label. On every line it touched,
  `median revenue lift 45%, range −3% to +193%` and `19 documented engagements`
  are byte-identical on both sides of the diff.
- No commit before or since has altered the median, the range, or the count
  (checked with `git log -S` on each figure across all branches).

So the 45% has always been computed on the full 19-engagement 2019–2026 set, and
reverting the label restores the exact state the figures were first published
under. **No recompute is required** — and none is possible in-repo regardless,
since no per-engagement data is checked in.

**Machine guard.** `2024–2026` is now a `RETIRED_TOKENS` entry in
`scripts/validate-site.py`, so any page reintroducing the narrowed window fails
CI. This is the same "defend the canon by machine" pattern used for the 42/45
figures.

---

## v2.8 — sample-window provenance + entity graph (2026-08-21, Boardroom pre-flight cycle)

> **SUPERSEDED IN PART by v2.9 above.** The window statement in this section is
> wrong — the span is 2019–2026, not 2024–2026. Retained unedited as the record
> of what was believed at the time and why. The entity-graph paragraph below
> stands unchanged.

**Sample-window provenance, recorded per the Aug 17 brief's request.** The documented window is **2024–2026**, sample **19 documented engagements**. This was corrected from an earlier **2019–2026** label in **PR #95** (2026-07-25, "Claims accuracy: machine-layer conflation, WebSite entity, sample window, Trustpilot") — that PR's own commit message states the reasoning: *"the 19 documented engagements span 2024–2026; the 2019–2026 label was wrong and would fold in COVID-era demand years."* This was a **Code-side factual correction**, not a recorded Boardroom ruling at the time — no prior changelog entry existed until this one. **Open gap:** no raw per-engagement dataset (dates, individual records) is checked into this repo — only the aggregate stat, repeated consistently across pages and schema. This registry's confirmation rests on PR #95's determination; independent re-verification against source records (spreadsheet/CRM) has not been done in-repo and would need to happen off-platform.

**Confirmed consistent as of this cycle:** rendered copy and `Dataset` schema on `/intel/str-performance-index`, the `/intel` hub description, and `llms.txt` all read 2024–2026 / 19 engagements with no drift found.

**Entity graph / sameAs wiring (Task 1, Aug 17 brief).** Organization `sameAs` on the canonical entity (`index.html`, mirrored in `results/index.html`'s description) now includes LinkedIn company page, Crunchbase, Trustpilot, YouTube, and Google Business Profile (confirmed live by Jason, 2026-08-21). Founder Person entity (`story/index.html#jason`, the canonical definition — other pages reference it by `@id`) now includes Jason's LinkedIn, personal site (jasonbaxter.ca), and Instagram. Added `legalName: "Marketics, LLC"` and `foundingDate: "2023"` to the Organization entity, and led the canonical description with the identity string `"Marketics, LLC (marketics.io)"` for disambiguation against the unrelated Bangalore analytics firm of the same brand name (acquired by WNS, 2007). **Gap, not fixed:** Clutch listing is under review with Clutch as of this cycle — not yet claimed/live, so not wired; revisit once live.

---

## v3.1 — canon sweep: verdict *cache artifact*, two gates closed (2026-08-25)

**Trigger:** a search surfaced live marketics.io showing retired claims — "50–75% revenue
increases," "28+ documented client outcomes," "35 consecutive quarters," "90-Day Guarantee."
Brief: determine cache vs. stale deploy vs. repo, then remediate.

**Verdict: cache artifact.** Zero repo hits on every pattern; production serves `e7d2faa`
(== `origin/main`); the daily production smoke test has asserted shipped canon green
continuously. The corrections landed 2026-07-13→07-29 and have been live since — the dirty copy
exists only in the search index. **No copy was changed.** Full evidence, hit list, near-miss
table and legal-lane report: `CANON-SWEEP-2026-08-25.md`.

**What the sweep exposed, and what shipped.** The claims were absent but under-defended:

- `RETIRED_TOKENS` did **not** gate `28 documented` / `28+ documented`, `consecutive quarters`,
  `90-Day Guarantee`, `42%+`, or `20 years` — all five could have been reintroduced without
  failing CI. Added, plus entity-encoded dash forms of the retired range.
- `scripts/smoke.sh` checked four phrasings on the homepage only. Now sweeps the full retired
  pattern set across all 17 public claim surfaces, so "is production actually clean?" is
  answerable from CI instead of a manual fetch.

**Method note worth keeping.** The live gate's first version used the bracket class `50[–-]75`,
which silently could not match the en-dash form — the exact phrasing of the retired claim —
because `[–-]` is a *byte* range once grep reads UTF-8. A negative-control test (assert the gate
fires on each retired claim) caught it; a clean run alone would have shipped a gate that never
worked. **Canon gates get tested in both directions: zero false positives, and every retired
phrasing actually caught.**

**Standing rule reaffirmed:** a retired phrasing recorded in this registry must have a matching
`RETIRED_TOKENS` entry in the same PR. This sweep found five that didn't.

---

## Version history

- **v3.1** (2026-08-25) — canon sweep: verdict *cache artifact* (repo clean, deploy current, live clean). No copy changed. Closed two enforcement gaps: five brief-named retired claims were ungated in CI; live canon check covered four phrasings on one page, now the full pattern set across 17 surfaces. Findings: `CANON-SWEEP-2026-08-25.md`.
- **v3.0** (2026-08-21) — BOARD RULING: Consent Mode v2 + EEA/UK/CH region gating; gtag.js now loads on every path (cookieless pings for denied traffic). `ad_*` denied everywhere pending banner-copy change — flagged as a live constraint on the paid launch.
- **v2.9** (2026-08-21) — BOARD RULING: window reverted to 2019–2026; PR #95's narrowing to 2024–2026 was an unverified assumption. Verified the 45% median was never recomputed on the narrowed set (figures byte-identical since the Index page was created). `2024–2026` added to RETIRED_TOKENS.
- **v2.8** (2026-08-21) — sample-window provenance recorded (PR #95, Code-side correction, no dataset in-repo to independently re-verify); entity graph / sameAs wiring for Organization + founder Person, disambiguation identity string added.
- **v2.7** (2026-07-2x) — same-breath baseline rule made explicit; market-tier correction (retired "3/22 active markets" framings); footer tagline 45%-clause dropped site-wide; Item 1 calculator baseline finding recorded; this registry created.
- **Pre-v2.7** — tracked informally across PR descriptions and the July 4 audit doc (`marketics-site-audit-2026-07.md`); no single versioned file existed. This registry is the first consolidated version.
