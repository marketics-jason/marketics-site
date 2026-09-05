# Marketics Claims Canon Registry

**Version:** v3.38 · **Maintained by:** Code, on ruling from CTO/Strategy · **Public visibility:** internal only — force-shadowed to 404 in `_redirects` (see bottom of that file), same pattern as `marketics-site-audit-2026-07.md`.

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

**Entity graph / sameAs wiring (Task 1, Aug 17 brief).** Organization `sameAs` on the canonical entity (`index.html`, mirrored in `results/index.html`'s description) now includes LinkedIn company page, Crunchbase, Trustpilot, YouTube, and Google Business Profile (confirmed live by Jason, 2026-08-21). Founder Person entity (`story/index.html#jason`, the canonical definition — other pages reference it by `@id`) now includes Jason's LinkedIn, personal site (jasonbaxter.ca), and Instagram. Added `legalName: "Marketics, LLC"` and `foundingDate: "2023"` to the Organization entity, and led the canonical description with the identity string `"Marketics, LLC (marketics.io)"` for disambiguation against the unrelated Bangalore analytics firm of the same brand name (acquired by WNS, 2007). **Gap, not fixed:** Clutch listing is under review with Clutch as of this cycle — not yet claimed/live, so not wired; revisit once live. — **CLOSED 2026-08-26, see v3.2 below.**

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

## v3.2 — Clutch listing wired; v2.8 entity-graph gap closed (2026-08-26)

The Clutch listing recorded as an open gap in v2.8 ("under review with Clutch … not yet
claimed/live, so not wired; revisit once live") is now live and claimed. Added
`https://clutch.co/profile/marketics` to the Organization `sameAs` on the canonical entity
(`index.html`, `@id: https://marketics.io/#business`). That completes the v2.8 `sameAs` set:
LinkedIn, Crunchbase, Trustpilot, Clutch, YouTube, Google Business Profile.

Only the canonical entity carries `sameAs` — other pages reference the Organization by `@id`,
so this is a one-place change by design, not an omission.

**Verification note, recorded because it is a real limit.** The session that made this change
could not fetch `clutch.co` — the environment's egress policy denied it (403 at the gateway),
the same denial pattern as `marketics.io` during the v3.1 sweep. Unlike that case there is no
CI path to verify a third-party page, and adding one would make our build depend on an external
site. **So liveness and identity rest on Clutch's own publication notice, not on a machine check.**

The evidence is Clutch's "Your Profile is Published" email to Jason, 2026-08-26 07:49
("Marketics is now visible to over 1 million buyers…"). That is the right evidence for this
specific doubt. Jason first confirmed while logged in to Clutch, then flagged the risk himself:
an owner viewing their own profile sees it whether or not it is published, so a logged-in look
cannot distinguish "live" from "still under review" — the exact state v2.8 recorded. The
publication notice settles it from Clutch's side, and being addressed to Jason settles the
same-name question below at the same time.

That confirmation mattered more than usual here: `sameAs` asserts identity, and this repo already
tracks an unrelated Bangalore analytics firm trading as "Marketics" (acquired by WNS, 2007) —
the reason v2.8 added the `"Marketics, LLC (marketics.io)"` disambiguation string in the first
place. A generic `/profile/marketics` slug pointing at the wrong company would have actively
merged the two entities in search engines, the precise opposite of what the entity-graph work
exists to do. **Rule going forward: a `sameAs` URL gets added only on positive confirmation that
the destination is Marketics, LLC — never on a plausible-looking slug.** And a corollary the owner-view catch earned: **for a third-party
listing, "I can see it" is not evidence it is public** — confirmation has to come from the
platform (a publication notice) or from a logged-out load, never from an authenticated session.

**Residual, small and cheap to fix:** the publication notice names the company, not the URL
slug, so the exact path `/profile/marketics` rests on Jason reading it off his own profile. It
is Clutch's standard public profile format. If that URL ever 404s, the fix is deleting one line
from the `sameAs` array — no other surface depends on it.

**Still open from v2.8:** nothing. The entity-graph task is complete as specified.

---

## v3.3 — press citation: "Quoted by" bar + /media Press section (2026-08-26)

Jason was quoted by name in **CNBC Make It**, Aug 22 2026 — "Airbnb's new fee change frustrates
hosts," by Mike Winters. First third-party press citation on the estate, so the claim strings are
registered here before they multiply across surfaces.

**Registered strings — exact, no improvisation:**

| Slot | String |
|---|---|
| Bar label | `Quoted by` (fallback, if design needs length: `As featured in`) |
| Logo alt / entity string | `CNBC Make It — article quoting Jason Baxter, founder of Marketics` |
| Article URL | `https://www.cnbc.com/2026/08/22/airbnb-fee-change-frustrates-hosts-what-to-know-before-listing.html` |
| /media byline | `by Mike Winters · CNBC Make It · Aug 22, 2026` |
| Verbatim quote (only if displayed) | "If you're looking for passive income and not active income, don't touch it." |

**Retired before it was ever used:** "trusted by," "endorsed by," "as seen on," and any variant
implying CNBC recommends Marketics. The claim is literal and narrow — **they quoted him**. An
outlet quoting a source is not an outlet endorsing a vendor, and the gap between those two is
exactly where a credibility asset turns into a liability.

**Treatment rules, and where they are enforced.** Outlet marks are placed as assets, never typed
as styled text. Single-tone, never gold (gold is the CTA accent — a third-party mark wearing the
action colour dilutes the CTA and implies affiliation) and never full-colour (a colour mark reads
as an ad row; monochrome reads as a citation). The never-full-colour rule is enforced in CSS via
`filter:grayscale(1)` rather than left as a rule someone must remember when adding outlet #2.
Every mark links to its own source: a proof element that links to its source audits itself, one
that doesn't looks decorative.

**Press bar is press only.** No podcast or directory logos for balance — Clutch (v3.2) lives in
the review layer, appearances live on `/media`. Not animated, not a carousel, never in the footer.

**Growth path:** the bar and the `/media` Press section both take 1..n entries. Outlet #2
(GlobeSt, second CNBC piece) is one `<li>` and one `<article>` — data, not redesign. The bar
renders correctly at n=1; the `Quoted by` label carries it.

**No numeric claims added.** The 45% median, the gate sentence, the 19-engagement sample and the
2019–2026 window are untouched by this work.

**Asset provenance.** The CNBC wordmark is **inlined** in each placement as paths with
`fill="currentColor"` — no external file. Jason supplied the vector after this session's egress
blocked every source (`upload.wikimedia.org`, `commons.wikimedia.org`, `www.cnbc.com` all denied;
`simple-icons` on npm carries only `nbc.svg`, the NBC peacock, which is a different network's mark
and would misattribute the outlet). Hand-drawing a trademarked wordmark was never an option.

The supplied vector was full-colour (navy `#001e5a` letterforms, `#0076ff` wedge) on a transparent
ground. Both fills were stripped so the root `fill="currentColor"` carries the tone. The wedge
merges into the N, which is how CNBC's own one-colour logo reads — the wedge is integral to the
letterform, not a separate accent. Verified by rendering before it went on three pages.

**Why inline rather than an `<img>` asset:** it makes the colour rule structural. There is no
colour left in the mark to leak, so "never full-colour, never gold" cannot be violated by a future
asset swap — it is not a rule someone has to remember when adding outlet #2, it is a property of
the markup. Cost is ~3.4 KB of path data duplicated per page, accepted deliberately.

**Mark is the plain CNBC wordmark, not the Make It lockup** — the documented fallback in the
brief. It is literally true (the article lives on cnbc.com), and "Make It" precision is carried by
the accessible name and the `/media` byline.

---

## v3.4 — fee basis is NET PAYOUT; press mark is the outlet's own (2026-08-27)

Two rulings from Jason on the Aug 27 design review.

### The fee is 10% of net payout, not "10% of revenue"

**Canon:** *"10% of your net payout, taken per booking."* Net payout is what the platform deposits
after its own fees and platform-remitted taxes — the definition already written into the Co-Host
Agreement (`/join` §2). Retired: "10% of revenue", "10% of the revenue your property earns",
"10% of bookings", "10% of net bookings", "one rate on the whole number".

This was not a rewrite for tone. The site was describing the fee on a **different basis than the
contract the client signs**, and gross-vs-net on a booking is a real money difference (the
platform's host service fee plus taxes). Corrected across 19 marketing surfaces — homepage,
`/pricing`, `/results`, `/faq`, `/join` page copy, `/lp/keep-control`, `llms.txt`, and 11 intel
pages — with rendered copy and JSON-LD kept verbatim-identical wherever both exist.

**COUNSEL LANE — NOT FIXED HERE, AND IT NEEDS FIXING.** `/legal` contradicts itself on the fee
basis and no marketing wording can resolve that:

| `/legal` | Says |
|---|---|
| §390 | "Marketics receives **10% of booking revenue** directly from the platform at the time of payout" |
| §588 | "direct **10% of gross booking revenue** per booking" |
| §601 | "the ongoing service fee is **10% of the net payout** per booking" |
| §602 | "The Service Fee is calculated on **gross booking revenue before platform service fees, taxes, or other deductions**" |

§601 and §602 are mutually exclusive: net payout is *after* those deductions, gross-before-
deductions is the opposite. The Co-Host Agreement (`/join` §2) says net payout, matching §601.
So the terms a client reads disagree with themselves, and two of the four statements now
disagree with every marketing surface. **Routed to counsel; Code did not edit `/legal` or the
Co-Host Agreement body, per the standing counsel-lane rule.** Until it is corrected the estate is
consistent on net payout everywhere *except* `/legal` §390, §588 and §602.

### Press mark: the outlet's own logo, unmodified — supersedes v3.3's monochrome rule

**v3.3 said single-tone, never full-colour, enforced via `fill="currentColor"`. That is
withdrawn.** The mark is now Design's reversed CNBC lockup as supplied — white letterforms,
CNBC's own blue accent retained — served from one shared asset, `/images/press/cnbc.svg`, used
identically on the homepage bar, the `/lp/keep-control` bar and the `/media` Press entry.

**Why the reversal.** The monochrome rule had us *recolouring a third party's trademark*.
Altering a mark is generally the bigger brand-guideline risk; carrying the outlet's own reversed
variant is the conservative choice. **CNBC's actual brand guidelines could not be checked** —
`cnbc.com` is denied by the build environment's egress — so this is reasoned, not verified, and
would be worth confirming against their press kit if one is ever to hand.

Still in force from v3.3: label is literal (`Quoted by`); "trusted by" / "endorsed by" / "as seen
on" stay retired; **never gold**, which is the CTA accent; press only, no podcast or directory
logos; not animated, not a carousel, never in the footer.

One asset also means outlet #2 stays a data change — a new file plus one `<li>` — and there is
now a single place to change the treatment rather than three inlined copies.

---

## v3.5 — `/lp/keep-control` rebuilt from copy v3.1; two ledger entries (2026-08-27)

Built to ship brief **Rev C** from copy **v3.1**. Both staleness checks in the batch README were
run before building: the brief reads "GATE 0 — RULED" (not BLOCKER), and the copy's Section 4 H2
reads "You pay 10%. Your manager takes 20–35%." — the v3.1 fingerprint, with no "growth" or "the
increase" framing.

**Copy versions v1, v2 and v3 are all superseded.** v1 carries the stale 2024–2026 window; v2
carries canon apparatus in body copy; v3 carries the retired incremental fee framing. Build from
v3.1 only.

### Registered LP claim strings

| Claim | String, as built |
|---|---|
| Fee | "10% of your net payout, taken per booking — a 90/10 split at the transaction level." |
| Performance | "On median: 45% more revenue than the market would have given you." (Section 5 H2, **once**) |
| Baseline | "Measured across 19 documented engagements, 2019–2026." |
| Gate sentence | "Results are property-specific; every property is audited before a target is set." |
| PM cost | "20–35%" |
| Tenure / footprint | "1,000+ listings across 22 markets over the past decade." · "35× Airbnb Superhost." |
| Press | "Quoted by CNBC on short-term rental economics." |

### Two LP-only exceptions to standing canon — ruled, not drift

1. **The methodology pointer is plain text, not a link.** Canon says performance claims link to
   the STR Performance Index. Rev C overrides that for this page: `Full methodology:
   marketics.io/intel/str-performance-index` renders as text. Canon's substance is satisfied —
   the methodology home is named in the same block as the claim — without adding an exit to a
   paid page. **Applies to `/lp/*` only.** Indexed surfaces still link.
2. **The press mark renders unlinked here.** Homepage and `/media` keep the article link, so the
   citation remains auditable on every surface a reader can reach organically. Same component,
   two behaviours.

Both exist because a paid landing page's job is different from an indexed page's. Neither weakens
a claim; both remove an exit.

### Ledger entries riding this ship

- **PM cost range 20–35%** — ratified for published surfaces. Sources: SkyRun Apr 2026,
  PriceLabs May 2026. Closes open flag #4. *(If Jason holds 25–35, Strategy re-strings the four
  instances the same day.)*
- **Airbnb fee change** — 15.5%, effective Sept 15; **18.34% is arithmetic on it** (1 ÷ 0.845),
  not a separate claim. Anchors: Airbnb's official fee-structure announcement and CNBC Make It,
  Aug 22 2026 (Winters). The paid page's numbers are therefore sourced.

### Build gates verified on the built page

Scan test (H1 + 7 H2s read as the complete argument, matching the copy header chain) · 45%
appears exactly once · gate sentence verbatim · fine print in the same block as the claim and
never sized up · methodology pointer plain text · press strip unlinked · single CTA path (three
buttons, one destination) · no accordions above the first CTA · no property photos · `noindex,
follow` in the rendered head · FAQ schema identical to rendered FAQ, both generated from v3.1.

**New CI gate:** `validate-site.py` now runs a **FAQ pair check** — where a page renders FAQ
accordions and carries `FAQPage` schema, the two must match verbatim. Editing one and not the
other shows Google different text than the visitor, which on a page that states the fee is a
claims risk, not just a structured-data one. Negative-control tested.

**Not done here, and not Code's to do:** the CTA end-to-end test (form → GHL → sequence) and the
UTM assertion on the GHL contact record and GA4 conversion event both need a tagged live
submission against systems this environment cannot reach.

**Footer deviation from the design, deliberate:** the design shows a link-free footer. The build
keeps Privacy and Terms, per the standing note in the LP source that these are an **ad-policy
requirement, not navigation** — a paid landing page without a privacy link risks ad
disapproval. Flagged rather than silently resolved either way.

---

## v3.6 — fee-phrasing ruling RATIFIED; LP fine-print footer (2026-08-27)

**Jason: ratified.** The Boardroom sign-off the Rev C contingency was waiting on. The homepage
re-string was executed in full rather than held as a follow-on PR.

### The canonical fee sentence — one truth, every surface

> **10% of your net payout, per booking — you keep 90%. No monthly fee, no retainer, no contract.
> Our fee only grows when your revenue does.**

Incentive close, where only the clause fits: *"Our fee only grows when your revenue does."*

**What was retired, and why it mattered more than tone.** Every "paid only when your revenue
grows" variant described a **growth-contingent fee** — you pay only on the increase. Under
GATE 0 (Option A) that is simply not the structure: the fee is 10% of net payout on *every*
booking. These were not off-brand phrasings, they were **inaccurate descriptions of what the
client is charged**, and they sat next to the corrected basis until now. Re-strung across the
homepage, `/pricing`, and 12 intel pages.

**Comparison table re-strung as a PAIR** (per Rev C, because the row's contrast depended on the
retired claim — fixing one cell would have left the row arguing nothing):

| | Before | After |
|---|---|---|
| Property manager | "20–35% of every booking, grow or not." | "20–35% of every booking, contract typical." |
| Marketics | "10% of net payout, paid only when yours grows." | "10% of your net payout — you keep 90%. No contract." |

**"How do you charge?" rebuilt, not patched.** Its closing clause was the visible problem; the
body was worse — *"Revenue growth earns a commission"* is the incremental structure stated as
principle. Now leads with the canonical sentence, keeps the commission-what-scales principle,
and drops the growth-contingent framing entirely. Schema and rendered re-strung together.

### Survivor sweep — every hit reviewed, not pattern-replaced

Rev C's four patterns plus the incentive-close family. Kept as legitimate, and why:

- `/legal` §603 "earns the Service Fee only when the Client earns booking revenue" — accurate (no
  bookings, no fee) and counsel lane regardless.
- `/intel/performance-based-management` "You pay only when a booking happens" — accurate per-booking.
- `/intel/airbnb-cohost-revenue-share-model` "the co-host earns more only when you do" — says the
  fee is *larger* when revenue is larger. True of a percentage, and not the retired claim.
- `llms.txt` "Marketics only earns when the host earns" — same shape; about earning at all, not growth.
- `/lp/keep-control` "Our fee is only worth more when your revenue is" — v3.1 ruled copy, same distinction.
- Wally case study "earning only when summer pushed enough volume" — narrative about the property.
- `/media` "used only when no real media exists" — a CSS comment.

**The distinction that decides each case:** *contingent on growth* is retired; *proportional to
revenue* is true and stays. A blind find-and-replace would have destroyed the accurate ones.

### LP fine-print footer — ADDENDUM to Rev C §1

`© Marketics, LLC · Privacy Policy · Terms`, both links `target="_blank" rel="noopener"`.
**The sole sanctioned exception to the no-exit rule**, on ad-platform destination requirements
and lead-capture compliance: this page puts names and emails into GHL off paid traffic. Opening
in a new tab means the exception costs the page no visitor. **Same treatment applies to any
future paid LP.**

**Privacy policy: it exists, and it is adequate — no launch blocker.** `/legal` carries a full
Privacy Policy covering all four things Strategy named: what the form collects ("Information We
Collect"), processing via **GoHighLevel** (named as CRM sub-processor), analytics and pixels
(GA4, Clarity, cookies), and contact routes for data requests. `/privacy` and `/privacy-policy`
301 to it; `/terms` 301 to the terms tab. Contents are still a Jason/legal review item — Code
does not draft policy — but the structural gate is **met**.

---

## v3.7 — three rulings closed (Jason, 2026-08-27)

**1. PM cost range 20–35% — CONFIRMED as standard.** Closes open ledger flag #4. The four
published instances stand as built; no re-string. Sources on file: SkyRun Apr 2026, PriceLabs
May 2026. Live on `/lp/keep-control` (strip, Sections 1 and 4, FAQ), the homepage comparison
table, and the intel pages that carry the contrast.

**2. 45%-provenance check — CLOSED, gate satisfied.** Ruled by Jason: the median was computed by
Claude on the documented engagement set. Rev C made this a hard precondition for the LP going
live; that precondition is now met and the LP is clear to ship.

Recorded precisely, because the two statements sit side by side and should not be conflated:
v2.9 established the 45% was **never recomputed** on the narrowed 2024–2026 window — the figures
have been byte-identical since the Index page was created. This ruling adds the provenance of the
original figure. The standing limitation from v2.8 is unchanged and still true: **no
per-engagement dataset is checked into this repo**, so no in-repo recomputation is possible, and
any future re-verification is an off-platform exercise against source records.

**3. `/legal` fee contradiction — routed to counsel.** Lined up as `LEGAL-ROUTING-2026-08-27.md`
(internal, 404-shadowed): a counsel-ready statement of the four conflicting sections, what each
says, why they cannot all be true, and what the rest of the estate now says. Code did not edit
`/legal` and will not. The `validate-site.py` counsel-lane warning stays on until it is resolved,
so it cannot quietly fall off the list.

---

## v3.8 — inline audit form on `/lp/keep-control` (board memo, 2026-08-30)

**Signed off by the board, conditional on the Aug 30 memo.** The lead form now sits on the LP
itself rather than routing paid traffic to a second page. `/get-started` is unchanged and keeps
serving organic and direct traffic.

### What the board settled

| # | Ruling | Effect on the build |
|---|---|---|
| 2 | `pricing_owner` ships as a **select** (I do / my property manager / a pricing tool / not sure) | Optional, never gates submission, diagnostic only |
| 4 | The paid conversion event is **distinct** from the organic form's | LP fires its own event, not `generate_lead` |
| 5 | Privacy link in the fine-print footer | Already live since v3.6; design caught up in its Aug 30 revision |
| 6 | Fee wording — **not** "10% of revenue" | Already canon since v3.4; the handoff README's "held sacred" line was stale, the design itself was clean |
| — | Inline form vs. separate page | Inline. A stripped-down second page stops being a different kind of page and becomes a click between the pitch and the ask |

**The memo itself is not in hand.** Rulings 4, 5 and 6 are known from the handoff README's own
overruled-lines note and the board's message; rulings 1 and 3 have not been seen by Code. Nothing
in the build depends on them, but they are unread, not cleared.

### The one assumption in the build

Ruling 4 says the paid event is distinct; it does not reach Code with the event's **name**. Built
as `lp_audit_lead`, held in a single constant at the top of the LP's form script so the memo's own
name is a one-line change. Everything else about the wiring matches `/get-started` deliberately:
same GHL webhook, same first-touch UTM source (`mkx-utm.js`), so one pipeline receives both and
only the paid signal is separable.

### Registered LP form strings

| Element | String |
|---|---|
| Card | "Free revenue audit" · "Send the listing. See the gap." |
| Fields | "Your listing URL" · "Where to send it" · "Who sets your pricing today? — optional" |
| Submit note | "Two minutes to request. Yours within 48 hours. Free, no contract, yours to keep either way." |
| Consent line | "We use your details only to prepare and send the audit, and we never share them." |
| Confirmation | "Request received." · "Jason reads it personally and sends the audit back within 48 hours. Nothing happens to your listing in the meantime — and you don't need to tell your manager anything yet." |

The consent line is claims-adjacent and gated by the same page-wide token sweep as the rest of
the copy, per the handoff.

### Two guards added — both enforce rulings that already existed

- **Paid-LP no-exit rule** (Rev C §1 + the v3.6 footer addendum). Any `<a href>` on
  `/lp/keep-control` that is not an in-page anchor or the fine-print footer's `/legal` links is
  now a hard CI failure. It fired on its first run — see the correction below.
- **Retired contrast tokens** on pages built to the current palette. `#6B6A65` / `#55534E` are
  known debt on the older designs and remain Design's to schedule; a page built to the current
  tokens may not regress into them.

Both were verified by deliberately breaking them, as was the existing FAQ pair check.

### Correction to the Thursday build (Code)

The no-exit guard immediately caught **an exit Code shipped on Aug 27**: the masthead logo was
wrapped in `<a href="/">`. Both design handoffs — Aug 27 and Aug 30, identical in this respect —
show the logo as a plain image with a `MARKETICS.IO` wordmark beside it, and Rev C §1 says no nav.
The link was Code's addition and contradicted both. Logo unlinked, wordmark added. On a paid page
the masthead is identification, not navigation.

The founder thumbnail was also being served from the 2000×1333 hero image (68 KB) for a 44px
box; replaced with a pre-cropped 88px asset (2 KB).

### Open — not resolved by this ship

**Audit turnaround is published three different ways, and the page that receives the request
promises the slowest.** Unregistered until now:

| Promise | Surfaces |
|---|---|
| 24 hours | `/pricing`, 4 market pages + their report/thank-you pages |
| 48 hours | `/calculator`, `/lp/keep-control`, `/join` |
| 2–3 business days | `/get-started` |

The LP's "48 hours" is v3.1 ruled copy and board-approved, so it was built verbatim rather than
reconciled by Code. This is a canon question for Strategy: one number, or a stated reason the
paid path is faster. It now sits on the submit path of a page buying traffic, which is where a
missed promise costs most.

---

## v3.9 — board addendum A: turnaround canon, paid event, perf gate (2026-08-30)

Rides with the Aug 30 LP/form ruling memo. A1, A2 and A5 shipped; A3 held pending the
what-actually-fires inventory; A4, A6, A7 are Jason's.

### A1 — one turnaround phrasing

**Canon: "48 hours or less."** Every surface that promises the audit. The 24-hour internal
delivery target is **not** a published claim. Retired: "24 hours" as a turnaround promise, and
"2–3 business days" outright.

Applied to 24 instances across the four market pages (request form + success state), their
report and thank-you pages, `/get-started` (confirmation + the Turnaround spec row),
`/calculator`, and `/lp/keep-control`.

**Two hits reviewed and deliberately NOT swept** — the same phrase carrying a different claim:

| Surface | Text | Why it stays |
|---|---|---|
| `/pricing` §payout | "about 24 hours after the guest checks in" | **Payout settlement timing**, not audit turnaround |
| `/join` §2 | "Implement Marketics' recommendations within 48 hours of receipt" | **Client obligation in the Co-Host Agreement** — counsel lane, report only |

`/calculator`'s "free demand report within 48 hours" is a **different deliverable** (market demand
report, not the audit) and was left as authored; flagged to Strategy rather than harmonised by Code.

**This corrects v3.8's own table**, which listed `/pricing` as a 24-hour turnaround surface and
`/join` as a 48-hour one. Neither is a turnaround claim. The v3.8 count was wrong.

**Enforcement.** "2–3 business days" is a flat retired token. "24 hours" could not be, precisely
because of the `/pricing` payout line — so the rule is **scoped**: no page but `/pricing` may
carry the phrase, and the exemption records which claim it is. Adding a second exemption requires
naming the claim, which is the step that stops the next blind sweep.

### A2 — the paid conversion event

**`lp_audit_lead` stands.** The paid-only conversion event, fired by `/lp/keep-control` on
successful submit with `form: 'lp-keep-control'`, `landing_page`, and the captured UTMs.

**Never shared with organic.** `/get-started` fires `generate_lead`. A shared event name would let
organic leads train the paid bidding signal, which is the opposite of what the six-week test
measures. To be imported into Google Ads as its own conversion action (CTO).

### A5 — the paid page is now measured

`/lp/keep-control` added to Lighthouse CI. It is held to the **homepage bar**, not the
calculator's relaxed LCP — it carries spend. Current: performance 100, accessibility 100,
LCP 1.8s, TBT 0ms, CLS 0.

Its own matrix entry turns the SEO assertion **off**: the page is deliberately `noindex, follow`,
which Lighthouse scores ~69, and a gate that warns every run for a setting we chose on purpose
trains people to ignore it.

### Standing rule, promoted from method to policy

**Individual review over pattern-replace on ambiguous hits.** The fee sweep (v3.6) worked this
way; A1 confirms it as the rule. The payout-settlement line and the Co-Host Agreement obligation
are semantically different claims wearing the same phrase, and a pattern replace would have
corrupted both. Ratified by CTO, Aug 30.

### Correction recorded against Code

The A1 sweep was run twice because the first pass was wrong in two ways: a **truncated match
string** produced `"Delivered in 48 hours or lessurs."` on `/intel/nashville/thank-you`, and
**three instances were missed** (two thank-you pages and a Miami line with different phrasing).
Both were caught by re-sweeping from zero afterwards rather than trusting the edit list. A sweep
is not finished when the edits apply; it is finished when the grep comes back empty.

### Open — the tracking inventory

`/legal` describes a **Meta Pixel** performing retargeting. **No Meta Pixel exists anywhere on
this site.** The contradiction is three-way: the policy describes advertising tracking that does
not run, the banner promises none (currently true), and A3 would permit it. Per CTO: Code produces
a one-page factual inventory of what actually fires, routed through CTO to counsel and the Board,
so `/legal`, the banner and reality are aligned in one pass against the post-ruling state.
**A3 is not built until that lands.**

---

## v3.10 — Addendum B: consent architecture (2026-08-30)

**Supersedes A3**, which was void as written: it governed a banner the US audience never sees.
The finding that voided it came out of the what-actually-fires inventory.

### Two populations, and the difference is the design

| | Gated regions — EEA/UK/CH **+ Canada** (B2) | Everywhere else (B1) |
|---|---|---|
| Banner | Shown | Never |
| Before a decision | Everything denied | Analytics + all three ad signals **granted** |
| On Accept | All four families granted; Clarity and the chat widget may load | n/a |
| On Decline | Everything denied; nothing loads | n/a |
| Visitor control | The banner | "Do Not Sell or Share My Personal Information" + GPC |

Banner copy (B3): *"We use cookies for analytics and advertising measurement if you accept. No
tracking if you decline."*

The opt-out denies the three advertising signals and **leaves analytics alone** — it is about sale
and sharing, not measurement. Global Privacy Control is honoured as the same opt-out with no
visitor action, which several US state laws require.

### The architectural call: one file, not fifty-one

The ruling implied editing the inline Consent Mode defaults in all 51 pages. It did not need to.

`gtag.js` is injected only by `mkx-consent.js`, on idle, after `load`. The inline stubs merely
**queue** the defaults, `gtag('js')` and `gtag('config')` into dataLayer — nothing is *sent* until
that script has run, so every update it pushes lands ahead of the flush.

So the grant lives in one file, and the 51 stubs keep denying advertising everywhere as the
**fail-safe if the script is blocked or fails**. Canada joined the gated set without touching a
single region list. The next consent ruling will not need a 51-page edit either.

The "Do Not Sell or Share" control is injected from that same file rather than hand-added to 51
hand-authored footers — one implementation cannot drift out of sync with itself, and a footer that
silently lost the link on one page is exactly what a site with no template engine cannot prevent.
It is a **button, not a link**: it acts in place and navigates nowhere, which is why it can sit on
`/lp/keep-control` without breaking the no-exit rule.

### B4 — the chat widget, restricted and gated

Loaded from `mkx-consent.js` only, on `/get-started` only, on the standard 5s timer outside the
gated regions and after an explicit Accept inside them. One behaviour, no per-page exceptions.
Never on `/lp/keep-control`: that page's discipline is that the form is the only door.

**What it replaced:** the widget loaded on 34 pages, and on 33 of them five seconds after load with
no interaction at all — a third-party script and its storage for a visitor who had done nothing
and, outside the gated regions, been asked nothing. The homepage was the sole exception, and only
because the timer had been removed there for Lighthouse.

Removed by `scripts/remove-inline-widget.py`, which anchors on structure rather than on any of the
three comment variants, and refuses to touch a file whose matched block does not contain the loader
URL. Enforced afterwards: an inline loader on any page is now a hard CI failure.

### `/audit-request` retired

The addendum names "`/get-started` and `/audit-request`" as the two widget pages. **`/audit-request`
has never existed on this site.** It is a stale name for `/get-started` that travelled through the
Aug 30 design handoff and both board memos. It is not carried in the allowlist — an allowlist entry
for a path that does not exist is how the name survives to the next brief — only recorded in a
comment at the point where it would otherwise have been added.

### Correction to two source comments (B6)

`mkx-consent.js` and `mkx-utm.js` both described a **browser-originated** POST as "server-side."
Consent-independent and server-side are unrelated properties; the conflation had become load-bearing
in a gate. Both now state the distinction rather than assume it. Recorded alongside: the consent
beacon only fires where a banner renders, so it has never been a site-wide accept rate.

### Verified

29 checks in an instrumented browser across region, consent state, GPC and opt-out: the ungated
grant, GPC with no visitor action, the opt-out and its persistence, Canada's gate, Accept, Decline,
the LP exclusion, the widget's page restriction and consent gate, and that exactly one loader tag
exists in every path that loads it. The CI guard was negative-controlled. `scripts/counsel` note:
`/legal`'s inline widget block was removed with the rest — **script infrastructure, not a word of
its legal text**, which remains counsel's alone.

### Gate effect

"Ad consent signals" → **CLOSED**. Remaining before spend: P1b (form → GHL → sequence, UTM on
contact), US Ads account verification, lead-loss proxy status.

---

## v3.11 — guest bylines and pen names (Strategy brief, 2026-08-31)

First partner content on the site, and the first byline that is not Jason's. Cost Seg Smart
publishes editorial under the pen name **Jamie Melgar**; the principal keeps his legal name off
published content because of expert-witness work.

### The rule

A pen name is legitimate and has a long publishing history. Manufacturing a **person** is not.
The line between them is what this build enforces structurally rather than by remembering:

- Any guest byline shows **name + affiliated firm** — never a name floating alone.
- A pen name additionally carries the disclosure line, verbatim, in two places: the author page
  and the foot of the article.
- The author page carries exactly five things: the name, one line of what they write about, the
  disclosure, the firm link, and the list of posts under that byline.
- It carries **no** photo or avatar of any kind (including a placeholder silhouette, which still
  implies a person), no biography beyond that one line, no credentials, titles, years of
  experience or education, no social or LinkedIn link, no contact form or personal email.
- Article `author` in schema is the **Organization that stands behind the content**, not a Person.
  The visible byline may be the pen name; the machine-readable claim attaches to the entity that
  is actually accountable.
- The author page emits `WebPage` only. **No `Person`, no `sameAs`.**

The schema rule is the load-bearing one. A pen name in visible text is a publishing convention a
reader understands. The same name asserted as a verified individual in structured data is a false
claim, made to the systems — search and AI engines — that increasingly check exactly this.

### Registered strings

- Byline, rendered: `Jamie Melgar, Cost Seg Smart`
- Disclosure, verbatim, both placements: *"Jamie Melgar is the byline used for editorial content
  from Cost Seg Smart, Marketics' cost segregation partner. Cost Seg Smart and Marketics are
  referral partners."*
- Referral URL, all visible links: `https://costsegsmart.com/?ref=MARKETICS-Q0DZ`
- Schema `author.url`: `https://costsegsmart.com` — the plain domain. A tracking parameter does
  not belong in an entity identifier; the referral link is a visitor path, not an identity.

### Correction to the draft, made under this rule

Strategy's draft bylined "Jonathan [LAST NAME], **founder of** Cost Seg Smart" and closed with
"Jonathan [LAST NAME] is the **founder of** Cost Seg Smart". Swapping the pen name in mechanically
would have published *"Jamie Melgar is the founder of Cost Seg Smart"* — a title attached to a
person who does not exist, which is the precise failure the rest of this rule exists to prevent.
Code stopped rather than swapping. Jason ruled: remove the founder. The closing sentence is now
the disclosure line, which is where §2d puts it anyway; the byline drops the title per §2a.

### Claims ownership

Every tax statement in the article belongs to Cost Seg Smart and publishes under their byline.
No Marketics performance claim appears in the piece — no 45%, no engagement count — verified
against the draft and not added. The only Marketics voice is Jason's framing intro and closing
note, both visually distinct from the guest author's text.

### Open — not resolved by this ship

- **CLOSED 2026-08-31 (Jason): Cost Seg Smart has signed off on the pen-name treatment.** The
  brief's footer asked for that confirmation before publish and the article shipped with #126
  ahead of it, so the approval was retrospective by a few hours. It is given: pen name + firm +
  disclosure, no invented persona, is acceptable to them. The pages stay live and indexable; no
  `noindex` needed. Jonathan's separate approval of the tax claims was already on record.
- `/partners` and the Miami partner card do not exist. The brief's §3 referral-URL swap in the
  partner card and §4 inbound link from `/partners` are therefore **not done** — Jason confirmed
  the cards are built and published after this, and that they will link back to this article and
  to other items once they exist. The article's only inbound links today are the `/intel` hub card
  and the author page, which is thin for a page the brief itself says will otherwise sit
  unindexed.
- IndexNow submission for both pages, once that is wired (ties to the open P2 indexing batch).
- Jason has committed to indexing the reciprocal post on Cost Seg Smart's site; tracked separately.

---

## v3.12 — Google Ads tag, and the conversion that was not installed (Jason, 2026-08-31)

Google Ads account `AW-18418837499` is now a destination on the site. Jason forwarded
Google's own "set up a Google tag" instructions; the tag went in, one of the two snippets
did not.

### What Google's instructions say, and why the build differs

**"Paste `<script async src=".../gtag/js?id=AW-...">` before `</head>` on every page."**
Not done, twice over. `gtag.js` is one library serving many destinations — we already
load it once, from `mkx-consent.js`, on idle. A second script tag fetches and bootstraps
the same library again for nothing. The real objection is placement: markup in `<head>`
runs *before* this file decides consent, so a visitor in a gated region would be
registered for advertising having been asked nothing. That is the same failure B4 fixed
for the chat widget. Ads is added as `gtag('config', ADS_ID)` in the one file, after the
region-aware grant, so it inherits the whole consent gate — denied by default in
EEA/UK/CH/Canada until Accept, and denied anywhere the Do Not Sell control or GPC says so.

**"Install the page-view conversion snippet."** Deliberately NOT installed, and this is
the substantive call rather than a plumbing preference. That snippet fires
`gtag('event','conversion', {value: 1.0, currency: 'USD'})` on page load. Installed as
instructed it scores every pageview as a one-dollar conversion, which does not merely
measure the wrong thing — it points Smart Bidding at pageviews instead of leads and
spends real budget doing it. It also contradicts board addendum A2, which already named
`lp_audit_lead` as the paid conversion event. And there is nowhere honest to put it: the
LP form does not navigate on success, it unmounts and confirms inline, so no page load
corresponds to a conversion.

The conversion label Jason was given (`8867CLagvescEPvP5M5E`) belongs to that page-view
action and is therefore not wired to anything.

### Open, and Jason's to close

A **lead** conversion action has to be created in Google Ads. Then either import
`lp_audit_lead` from GA4 (preferred — no new code, inherits consent handling), or fire
`gtag('event','conversion',{send_to:'AW-18418837499/<lead label>'})` inside the existing
success handler next to the lead event. Code has done neither, because the action does
not exist yet.

`value: 1.0 USD` is Google's placeholder. If value-based bidding is wanted the figure
should reflect real lead economics; otherwise send no value and bid on conversion count.
A fabricated $1 is worse than none.

### Enforced

Two CI guards, both negative-controlled against the exact snippets Google supplies:

- any inline `googletagmanager.com/gtag/js` loader on any page — hard failure
- any page-level `gtag('event','conversion', ...)` — hard failure

These exist because the instructions Jason received are the instructions anyone receives,
and the next person to read them will be told to paste the same two blocks.

### Gate effect

The site half of the pre-spend gate is done: the tag is live and consent-gated. Still
open from v3.10 before spend — P1b (form → GHL → sequence, UTM on contact), US Ads
account verification, lead-loss proxy status — plus the lead conversion action above.

### Cost

`mkx-consent.js` +437 bytes. Held deliberately low: this file ships to every page and
`/calculator` has no headroom, which is what the v3.10 entry records. The long rationale
lives here rather than in the source for exactly that reason.

---

## v3.13 — the paid conversion event gets its name (Strategy, 2026-08-31)

Strategy named the paid conversion event `generate_lead_paid` and restated the board's
rule while doing so: paid and organic never share a counter.

### The rename

`MKX_LP_EVENT` on `/lp/keep-control` moves from the placeholder `lp_audit_lead` to
**`generate_lead_paid`**. This is the one-line change the constant was built for — v3.8
recorded the placeholder precisely because "the memo's own event name has not reached
Code," and it now has.

  organic  `/get-started`      generate_lead
  organic  `/join`             begin_checkout
  paid     `/lp/keep-control`  generate_lead_paid

### The rule is now a gate, not a comment

Board ruling 4 lived in a source comment. It is now a hard CI failure: the validator
reads `MKX_LP_EVENT` out of the LP and compares it against every `gtag('event', …)` name
fired by every other page on the site. Compared against what the site actually fires
rather than a hardcoded `generate_lead`, so renaming the organic event later cannot
silently collide either.

Negative-controlled three ways, all firing: colliding with `generate_lead`, colliding
with `/join`'s `begin_checkout`, and removing the constant altogether.

This matters more than most gates because the failure is invisible. If the two shared a
name, organic leads would train the paid bidding signal and both counters would simply
look healthy — nothing would break, the number would just be wrong, and the six-week
test would measure the wrong thing.

### Where this sits in Strategy's chain

  tracking code live -> generate_lead_paid firing -> imported into Ads as the
  conversion action -> full-path UTM test -> replace the rep's automated campaign
  with the three paused Search campaigns -> un-pause on Jason's word

Code owns link one and has now delivered it (with v3.12's tag). **Link two is a
sequencing constraint worth stating: GA4 will not offer an event as a key event until it
has seen it fire at least once.** So the order is deploy, submit the form once for real,
then mark `generate_lead_paid` as a key event in GA4, then import it into Ads. The Ads
conversion action cannot be created from an event that has never fired.

Everything from link two onward is Jason's and the CTO's.

### Bidding

Strategy's note stands and is not a Code decision: once the event has fired a few real
times, that is the moment bidding can move off Maximize clicks. Until then Maximize
clicks is correct, because there is no conversion history to bid against.

---

## v3.14 — the Ads tag is scoped to the paid path (CI, 2026-08-31)

Corrects v3.12, which configured Google Ads on every page. CI caught it; I did not.

### What failed

`/calculator`, mobile, three consecutive runs — not a flake:

  performance               0.68, 0.67, 0.67   floor 0.80
  largest-contentful-paint  6549, 6597, 6589   budget 5200ms

The previous head without the Ads tag passed. A second gtag destination is not
free: it is roughly **1,850ms of extra mobile LCP** on the heaviest page on the
site, the same page v3.10 already records as having no headroom.

### Why local verification missed it

This is the part worth keeping. Local Lighthouse runs showed `/calculator` at 100
across three runs, and they were measuring a lie: **the sandbox blocks
`googletagmanager.com`**, so gtag.js never loaded and the runs scored a page with no
third-party tag on it at all. The thing under test was the one thing that could not
execute.

The lesson generalises past this tag: a local perf number for anything third-party is
worthless here, and CI is the only measurement that means anything. v3.10's regression
was caught locally because it was bytes-on-the-wire; this one could not have been.

### The fix, and why it is not a workaround

`ADS_PAGES = ['/lp/keep-control']`, mirroring B4's `WIDGET_PAGES`. Not a budget
relaxation, and not merely the cheapest way to green — it is where the tag belongs:

- Conversions happen on the LP form and nowhere else.
- Paid traffic lands on the LP, and the no-exit rule keeps it there, so the LP *is*
  the entire paid path.
- Site-wide Ads would only add remarketing-audience collection, which nobody asked
  for, which no board ruling authorises, and which is precisely the kind of ambient
  ad-tech the consent architecture exists to keep scoped.

GA4 is unchanged and still configured everywhere.

### Verified

27 checks: the destination is configured on the LP in the US and in the gated regions
(where Consent Mode denies it until Accept), and is **absent** on `/`, `/calculator`,
`/get-started` and an intel page, each of which still carries GA4. One gtag.js tag and
one request throughout.

The perf recovery itself can only be confirmed by CI, for the reason above.

---

## v3.15 — live-page fixes and the registered guest-article strings (Strategy, 2026-08-31)

Strategy's live-page brief. Three fixes applied, three verifications reported, and the
article's claim strings registered as the checklist asked.

### Applied

- **Meta description and `og:description`** replaced with the ruled string, em dash gone:
  *"Cost segregation explained for STR owners: what a study reclassifies, the material
  participation test, and the question a refund can't answer."*
  Also applied to **`twitter:description`**, which the brief did not name but carried the
  same em dash the house rule exists to remove. Same ruled string rather than one Code
  invented; revert that one line if Strategy wants it separate.
- **Framing, ruled by Jason.** *"The closing question, though, is mine."* → *"I've added one
  thought at the end, from the revenue side."* And *"Here is the question the study cannot
  answer, and the reason this article is on my site."* → *"Here is the question the study
  cannot answer."* Both blocks otherwise unchanged.

### Reported, not changed

- **`og:title` and `twitter:title` still contain an em dash** — "The tax half of the STR buy
  decision — Marketics". That is the site-wide title convention on every intel page, so if the
  no-em-dash rule extends to titles it is a change to twenty-odd pages and a style decision,
  not this page's fix. Left for Strategy to rule.

### The partner link: intentional, ref intact, and two things the brief did not assume

`/costseg/intel-article` is a deliberate internal redirect, not a placeholder. It 301s with
the ref parameter intact, so **the partner's attribution window opens correctly.** Two
differences from what the brief expected:

1. It resolves to **`costsegsmart.com/order/`**, not the bare domain.
2. It appends four UTMs (`utm_source=marketics`, `utm_medium=partner`,
   `utm_campaign=costseg`, `utm_content=<placement>`) which the bare URL has no way to carry.

Both come from the `/costseg/:placement` rule in `_redirects`, which predates this article and
was presumably written for a partner-card CTA. **Worth a ruling: `/order/` is the right landing
for someone clicking "get a study" from a card, but an article reader meeting the firm mid-
paragraph is a colder audience, and dropping them on an order form may convert worse than the
homepage.** Code has not changed it — the rule is shared with the cards.

Per-placement destinations are now asserted in `smoke.sh` against production, so a partner link
that silently loses its ref fails the daily gate. It would otherwise be invisible: the link
still goes somewhere sensible, it just arrives anonymous.

### Verified

- **Article `author` is `Organization: Cost Seg Smart`.** No `Person`, no `sameAs`.
  `/authors/jamie-melgar` emits `WebPage` only. All four are CI gates as of v3.11, not just
  facts about today's file.
- **Sitemap:** both pages present.
- **IndexNow:** not wired yet. Still open with the P2 batch.
- **Internal links — short of the brief's bar, honestly counted.** The article has two
  distinct referring pages (the `/intel` hub card and the author page). The author page has
  **one** (the article, which links it twice — from the byline and from the disclosure). The
  brief's suggested third source, a cost-seg mention in `/intel/money`, **does not exist**;
  there is no cost-seg mention anywhere in `/intel` outside this article. Code did not
  manufacture links to hit the number: `/partners` and the Miami card are the real fix and are
  Jason's, pending.

### Registered claim strings — `/intel/str-cost-segregation-tax-half`

Tax claims belong to Cost Seg Smart and publish under their byline; Marketics makes none of
them. Registered so a later sweep can tell the difference between a partner's claim and ours:

| String | Owner |
|---|---|
| "residential studies from $495, delivered in about an hour" | Cost Seg Smart |
| "Traditional engineering firms charge $5,000 to $15,000" | Cost Seg Smart |
| "more than 100 hours in the year and more hours than anyone else" | Cost Seg Smart |
| "a five-figure deduction pulled forward into the first return, sometimes six" | Cost Seg Smart |
| "$60,000 year-one deduction … $20,000 less than its market" | Jason, illustrative |
| "The audit is free and it commits you to nothing." | Marketics, existing canon |

No Marketics performance claim appears in the piece — no 45%, no engagement count — verified
again after these edits and gated by the byline suite.

### `/authors/jamie-melgar`

Registered strings are the v3.11 set: the one-line descriptor and the disclosure, both verbatim
and both CI-gated.

---

## v3.16 — Strategy's rulings on the live-page brief (2026-09-01)

Three rulings on the questions v3.15 routed back.

### 1. Editorial placements land softer than card placements

Ruling: keep the shared `/costseg/:placement` rule as it is — rewiring it for one page would
change the cards too — but give the article a different destination **if that is config-level
rather than a refactor.**

**It is config-level.** Netlify resolves `_redirects` first-match-wins, so two specific paths
listed *above* the wildcard override it and the shared rule is untouched by construction:

```
/costseg/intel-article  ->  costsegsmart.com/       (+ ref + 4 UTMs)
/costseg/author-page    ->  costsegsmart.com/       (+ ref + 4 UTMs)
/costseg/:placement     ->  costsegsmart.com/order/ (unchanged — cards)
```

The reasoning, in Strategy's words, is scent: a card reader has already been told what Cost Seg
Smart is and is clicking a CTA, so `/order/` matches intent; a reader who met the firm
mid-paragraph has not been sold anything, and the wasted click is *worse than no click* because
it burns the referral without a conversion.

**`/costseg/author-page` was included though the ruling named only the article.** That link is
labelled "costsegsmart.com" — pointing a link labelled with a domain at an order form is the
same scent break, arguably plainer. One line to revert if Strategy wants it back on `/order/`.

Homepage rather than a methodology page: egress from the build environment cannot reach
`costsegsmart.com`, so a methodology URL could not be verified to exist. The homepage is the URL
the original brief named, so it is known good.

Smoke now asserts both editorial placements land on the homepage **and** that a card placement
still reaches `/order/` — the second assertion is the one that matters, because if those two
specific lines ever slipped below the wildcard the destination would silently revert and nothing
else would notice.

### 2. House style amended: em dashes are a prose rule, not a title rule

Strategy's own amendment, recorded because it is now canon and broader than one page:

> **No em dashes in prose. The title-suffix separator is exempt as a structural convention.**

So `og:title` / `twitter:title` keep "Title — Marketics" across the estate. Description strings
still change as briefed, because those are prose. Changing the separator would be a deliberate
estate-wide sweep with its own brief, never a side effect of a partner-page fix.

### 3. The third internal link stays unmanufactured

Ruling: correct not to invent one. A link created to satisfy a checklist makes an
internal-linking audit look healthy while helping nothing.

The author page ships with its two real links. The deeper fix is a **content gap, not a linking
task** — Strategy will write one-line cost-seg references into `/intel/money` and
`/intel/what-a-property-manager-actually-costs`, where they belong naturally, rather than asking
Code to invent placements. Tracked as Strategy's.

### Open — P3

If the editorial link produces clicks that do not convert, revisit the destination. The
attribution works either way, which was the actual risk.

---

## v3.17 — `/legal` routed to counsel a second time: the tracking disclosures (Code, 2026-09-01)

`LEGAL-ROUTING-2026-09-01.md`. Raised by Code, reported not edited, per the standing counsel-lane
rule — which held here even though two of the four findings are plainly just wrong rather than
arguable.

### The finding

`/legal` was last updated **2026-03-17**. The tracking has changed substantially since. The policy
now names a vendor that is not present, omits one that is, and carries one sentence the current
configuration puts under strain.

| | |
|---|---|
| **Meta Pixel** | described in §04.1 and §06 — **does not exist**, zero occurrences anywhere |
| **Google Ads** `AW-18418837499` | **live since v3.12** — **named nowhere in the policy** |
| §03 "we do not share your personal data with advertisers…" | in tension: `ad_personalization` is **granted by default** outside the gated regions (Addendum B) |
| **Microsoft Clarity** | described as a general vendor — actually runs **only after an explicit Accept**, and the banner only shows in the EEA/UK/CH and Canada |
| **Do Not Sell control + GPC** | both exist and work — **undisclosed** in §08 |

Every row verified against the running site by the browser suite under EEA, Canadian and US
timezones, not read off the source.

### The Clarity inversion, recorded because it is counter-intuitive

Session recording runs **only for visitors in the EEA, UK, Switzerland and Canada who actively
opted in.** A US visitor is never shown a banner, therefore never accepts, therefore is never
recorded. The people being session-recorded are exactly the people in the most privacy-protective
jurisdictions, and they are the only ones who were asked. The behaviour is defensible; the
disclosure describes more collection than occurs.

### Recommended sequencing: a gate on first spend

Not legal advice, and stated as sequencing. This is the only open pre-spend item where fixing it
afterwards costs materially more than fixing it before: the remedy is documentation and therefore
fast, ad-platform terms require the destination's disclosures to describe the practices in use,
and once campaigns run the inaccurate window acquires spend and conversion data rather than
staying a quiet gap.

### What was NOT done, deliberately

`/legal` untouched. The §03 sentence is raised as a **tension rather than a violation** because
Code cannot characterise it legally — not because it is minor. The brief also carries what the
site does *well* (region gating, working opt-out, GPC, single tag load, Ads scoped to one page,
all CI-enforced) so counsel can see the configuration is careful and the gap is in the
description of it.

The doc is force-shadowed to 404 in both URL forms and **asserted in `smoke.sh`** — a new internal
doc is public the moment it merges unless two lines are remembered, which is why that assertion
exists rather than being trusted.

### Open

Six questions for counsel, listed in the brief. Point 6 — whether the update needs an
effective-date change or user notice — is the one Code flagged as unanswerable from the
repository, the same class as point 3 in the August 27 routing.

Both `/legal` routings are now open at once. If counsel amends the document, the fee-basis
conflict (v3.4, `LEGAL-ROUTING-2026-08-27.md`) should be resolved in the same pass.

---

## v3.18 — Partner capacity: they run studies, they do not advise (Strategy ruling, 2026-09-01)

Cost Seg Smart's own terms disclaim being a CPA firm, accounting firm, law firm or registered
investment adviser, and disclaim providing tax, legal, accounting or financial advice. Section 6
of the referral agreement obliges Marketics not to hold them out as able to give tax advice on
their behalf. **"Our tax partner" claims exactly the capacity they disclaim.** "Cost segregation
partner" describes what they actually produce: an engineering-based study.

### Standing rule

On any Marketics surface, a cost segregation study is described as a **study, never as advice**,
and readers are pointed to their own CPA for their situation. Tax conclusions belong to the
partner; **Marketics makes no tax claims.**

### What changed

| | |
|---|---|
| `/intel/str-cost-segregation-tax-half`, Jason's note | "Cost Seg Smart is our tax partner" → **"Cost Seg Smart runs cost segregation studies"** |
| Miami partner card, "Our national tax partner." | **no such card exists yet** — the partner cards are still open from v3.11, so the ruling is recorded here and applies when the card is built |
| Sitewide sweep for "tax partner" | **one instance**, the one above. No others anywhere in the estate, `_redirects` and the registry included — the grep was run unscoped by extension this time, per the v3.15 lesson |

Explicitly unchanged, per the brief: the "Tax & cost segregation" category heading (it labels a
category of need, not the partner's capacity), the word "partner" itself (their agreement uses
"Referral Partner" as a commercial designation), and the author-page disclosure line, which
already said "cost segregation partner".

### Made structural

A string ruling that lives only in a doc comes back. `PARTNER_CAPACITY` in `validate-site.py` is
a hard gate on the possessive capacity forms — `our|Marketics'` + `tax|accounting|CPA|legal` +
`partner|advisor|adviser|firm` — matched against rendered text, so entity- and
whitespace-insensitive. Scoped to the possessive on purpose: a page telling a reader to check with
**their own** tax advisor is the correct sentence and has to keep passing. Negative-controlled
four ways — "is our tax partner" fires, "Our national tax partner" fires, "Marketics&rsquo; tax
advisor" fires (proving the entity form is caught), "your own tax advisor" does not.

---

## v3.19 — BOARD ADDENDUM C: `ad_personalization` denied everywhere; the counsel lane has a ruler (2026-09-01)

Addendum C responds to the counsel routing of the same day (v3.17) and **adopts Code's
sequencing recommendation: `/legal` accuracy gates first spend.** Spend does not start until
C1–C4 are live on production.

### C1 — amends B1: advertising personalization is off for everyone

| Signal | Gated (EEA/UK/CH/CA) | Everywhere else |
|---|---|---|
| `analytics_storage` | denied → granted on Accept | granted |
| `ad_storage` | denied → granted on Accept | granted |
| `ad_user_data` | denied → granted on Accept | granted |
| **`ad_personalization`** | **denied, stays denied** | **denied** |

Remarketing audiences are unusable below ~1,000 users and the six-week test will not reach that,
so personalization buys nothing today while making §03 harder to write. **Conversion measurement
— the CAC read the whole build exists for — is unaffected**, because it rides `ad_storage` and
`ad_user_data`.

**Not a permanent posture, and not automatic either:** revisiting is trigger-gated on a "scale"
ruling at activation + 6 weeks, with lawyer-drafted policy language to support it. Recorded here
as a flag so the trigger is findable rather than remembered.

**Implementation.** `ad_personalization` is a **hardcoded `'denied'` literal** in `updateConsent()`,
not a variable and not derived from `granted` — there is no path through that function, Accept
included, that turns it on. The previous shape was `ad_personalization: ad`, which reads correct
at a glance and is exactly what a later edit would restore by accident, so the gate rejects
anything derived rather than just anything granted.

Two CI gates, negative-controlled three ways: reverting to the derived form fires, deleting the
key fires, and a single page's inline stub granting it fires. Verified behaviourally as well, in
a browser under four region/consent combinations — US ungated, EEA undecided, EEA after Accept,
Canada after Accept — **20/20, with `ad_personalization` denied in every consent call in all
four**, and the measurement signals still following the region rules exactly as the table says.

### C2 — the counsel lane now has a named ruler

No retained counsel exists. Until one does, **Jason rules factual corrections to `/legal`; Code
drafts and ships them with the ruling dated here.** Characterisation questions defer to the C4
lawyer review. The boundary Code has held since v3.4 — never edit `/legal` unbidden — stands
unchanged; what changed is that there is now someone to ask.

### C3 — seven ruled edits, drafted as a redline

`LEGAL-REDLINE-2026-09-01.md`. Google Ads added to §04.1 and §06; §03's advertiser sentence
qualified rather than removed; both Meta Pixel passages deleted; Clarity corrected to
consent-only in four jurisdictions; §08 describing the Do Not Sell control and GPC; effective
date moved; and the fee basis at lines 390, 588 and 602 corrected to net payout, closing the
Aug 27 routing.

**Sequence is redline → Jason approves → Code ships**, so the document is unchanged on production
until that approval. Three items are flagged in the redline rather than drafted, because the
ruling does not cover them: §06 still implying Clarity sets cookies for everyone, §04.1's
"IP anonymization is enabled" describing a GA4 setting that does not exist, and whether the §03
notice block should carry the longer explanation or keep it in body text.

On shipping, the claim sweep extends to `/legal` — `Meta Pixel` and `gross booking revenue` as
retired tokens, `Google Ads` as a required one — and the counsel-lane exemption that lets
`/legal` carry the retired fee strings is removed, since it exists only because the document
could not be edited.

### C4 — a lawyer, dated

One-hour paid review of the full document, both routings, by a privacy/commercial lawyer with US
and Canadian exposure. **Booked by Sept 12, completed by Sept 30.** Scope: confirm C3 items 2 and
6, catch what the factual pass missed, and pre-draft the personalization language for C1's
trigger.

---

## v3.20 — `/legal` corrected: the first edit Code has ever made to that document (2026-09-01)

Jason approved the C3 redline and all three flagged items the same day. **`LEGAL-REDLINE-2026-09-01.md`
is the record of what was approved; the seven edits are now in `legal/index.html`.**

This is the first time Code has edited `/legal`. The boundary did not move because the document
became less sensitive — it moved because C2 named someone with authority to rule on it. Every
edit below traces to a ruling; none was Code's judgement about what the policy should say.

### What the document now says

| # | Was | Is |
|---|---|---|
| 1 | Google Ads named nowhere | §04.1 vendor entry + §06 marketing-cookie line, both naming conversion measurement on the paid LP and *no* personalization or remarketing |
| 2 | "We do not share your personal data with advertisers…" | the sell sentence kept verbatim; a body paragraph now states what *is* shared with Google Ads and why, and that no advertising audiences are built |
| 3 | Meta Pixel described in two places | **removed**, and `Meta Pixel` is now a retired token |
| 4 | Clarity as a general vendor | "runs only for visitors in the EEA, UK, Switzerland and Canada who have explicitly accepted… It does not run for any other visitor." |
| 5 | §08 pointed only at an email address | describes the footer Do Not Sell control and automatic GPC support, email kept as the fallback |
| 6 | Effective / Last Updated: March 17, 2026 | **September 1, 2026**, both tabs — the Terms half changed too, so its date could not stay |
| 7 | §390/§588/§602 on a gross basis, contradicting §601 | all four now say **net payout**, matching the signed Co-Host Agreement |

The three flagged items were approved as proposed: §06's analytics line now says Clarity's
cookies are set only for visitors who accepted them; GA4's "IP anonymization is enabled" — which
is Universal Analytics language for a setting GA4 does not have — became "does not store IP
addresses"; and §03's notice block keeps only the flat commitment, with the Google Ads
explanation in body text below it, verified in a browser so the gold-ruled block still reads as
a promise rather than an argument.

### The Aug 27 routing closes with it

`LEGAL-ROUTING-2026-08-27.md` was open for five days over the fee basis. Edit 7 closes it, and
the **counsel-lane exemption is deleted rather than kept as a courtesy** — it existed only
because Code could not edit the document, and keeping a dead exemption is how a real one stops
being noticed. `COUNSEL_LANE_EXEMPT` is now empty; the mechanism stays, because a document Code
must not edit should still warn rather than pass silently.

### Enforcement, both directions

A retired token catches copy that came *back*. `/legal` needed the inverse too — the whole
finding was about copy that quietly *went away* — so **`REQUIRED_TOKENS`** is new: `Google Ads`,
`net payout`, `Do Not Sell or Share` and `Global Privacy Control` must all remain present.
Negative-controlled four ways, including removing each required string and reintroducing the
Pixel. Smoke asserts the same six facts against the **served** page, since the repo copy and the
deployed copy are different questions and this document is the one an ad platform or a regulator
reads.

**One assertion class was nearly worthless and got caught by accident.** The local origin died
mid-run and the absence checks — "no Meta Pixel in `/legal`" — all reported green **against an
empty body**. Absence is unfalsifiable when the fetch fails. The block now proves the page
arrived before trusting anything that follows.

### `gross booking revenue` on `/calculator` — the same-phrase trap, third occurrence

Adding the token failed CI immediately on `/calculator`, which uses the phrase for **what the
calculator measures** (top-line, before platform and cleaning fees — it says so in its own
assumptions list), not for the basis Marketics' fee is charged on. Same words, different claim —
the trap `24 hours` on `/pricing` set in v3.9 and the Aug 30 sweep set before that. Handled the
same way: a scoped exemption with the reason written down, **never by softening the token**.
`SAME_PHRASE_EXEMPT` now carries that pattern explicitly instead of it being re-derived each time.

### Still open

C3 items 2 and 6 — the §03 characterisation and whether the date change needs user notice —
remain **provisional pending C4**, the lawyer review booked by Sept 12 and complete by Sept 30.
Everything else in the `/legal` accuracy gate is closed, which clears Addendum C's gate on first
spend as far as Code's side of it goes.

---

## v3.21 — a form field's NAME is not the key the webhook sends (2026-09-01)

Jason asked whether the LP's pricing dropdown reaches GHL. **It already did** — as `pricingOwner`,
since the form shipped in v3.8. The question surfaced something more useful than the answer.

### The distinction that cost a wrong diagnosis

The LP handler reads elements by id and **hand-builds the JSON payload**. It does not serialise
the form. So the `name` attributes and the transmitted keys are two different vocabularies, and
only one of them ever reaches GHL:

| Form `name` | Key GHL receives |
|---|---|
| `listing_url` | **`listingUrl`** |
| `pricing_owner` | **`pricingOwner`** |
| `email` | `email` |
| `source` | `source` |

Earlier the same day, debugging a GHL custom-variable error, Code read the `name` attributes and
told Jason "the site posts `listing_url`" — and built a field-collision hypothesis on it.
**`listing_url` is never transmitted.** The markup says one thing and the wire says another, and
nothing in the file makes that visible; the payload is 200 lines below the inputs. Corrected to
Jason directly rather than quietly.

**Rule: when a question is about what a third party receives, read the request, not the markup.**
Verified here by intercepting the actual POST in a browser, not by reading either.

### `pricing_owner` added alongside `pricingOwner`

Both keys, one value. The new key matches the GHL custom field exactly, so the workflow mapping is
a like-for-like pick rather than a judgement call — which is the whole failure mode the same day's
`listingurl` confusion demonstrated. `pricingOwner` stays until it is known that nothing consumes
it; renaming a live key to tidy up is how a CRM field silently empties.

### The values are the option `value`s, not the labels

This is the part that would have broken the conditional email branch:

| Label in the dropdown | String GHL receives |
|---|---|
| I do | `me` |
| My property manager | `manager` |
| A pricing tool | `tool` |
| Not sure | `unsure` |
| *(skipped)* | `""` (empty string) |

A branch built on "My property manager" never fires. The values are also the better thing to
branch on — short, stable, no punctuation — so the label copy can be rewritten without touching
the workflow. Verified across all five options by intercepting the POST: **25/25.**

### Gated

The transmitted keys are now checked by name in `validate-site.py`. A rename here throws no error
and breaks nothing visibly — the lead simply arrives with an empty field and a conditional branch
that silently takes the wrong path. Negative-controlled on all three of `listingUrl`,
`pricingOwner` and `pricing_owner`.

---

## v3.22 — the paid LP gets its own webhook trigger (2026-09-03)

Two hours were lost hunting for which GHL workflow owned the shared inbound-webhook trigger. The
hunt was the wrong shape, and the reason is worth recording because the same trap is available
again tomorrow.

### What was actually wrong

Every form on this site posted to **one** trigger, `1297f709-…` — 29 files: `/get-started`,
`/join`, `/404`, the homepage, every intel page, the author page, and `mkx-consent.js`'s consent
beacon. A workflow bound to it therefore receives the whole estate, and the only way for the paid
workflow to tell itself apart was a filter on `source == "lp-keep-control"`.

**A filter that silently stops matching is indistinguishable from a broken deploy.** That is what
sent the CTO looking for a missing serverless Function — which has never existed here; every GHL
call on this site is a browser `fetch` to an inbound webhook, so the site cannot map a custom
field or apply a tag at all. Contacts were being created (with the correct `source`) by whatever
legacy workflow owns the shared hook, while "Paid LP — Tag → Audit Sequence" showed 0 executions
because nothing had ever pointed at it.

So the fix was wiring, not archaeology.

### The owner, once found: "Inbound Lead" — and why it was ruled out

It was **"Inbound Lead"**, and it had already been restored and dismissed during the hunt as
*"old native Facebook/TikTok/LinkedIn lead-form routing, pre-dates the website, not a webhook
trigger."* It created contacts and never applied a tag, which is exactly the symptom.

**Ruling a workflow out by its name and its vintage is what kept the search running for two
hours.** A workflow can acquire an inbound-webhook trigger long after it was built and long after
its name stopped describing it; the name is documentation, and documentation drifts. The
identifying question is which trigger a workflow *currently holds*, never what it was for.

Recorded because the same trap is set again the moment another old workflow gets repurposed.

### The paid path now has its own entry point

`/lp/keep-control` posts to `3c750621-…`, generated by Jason in the trigger panel. The organic hook
is untouched and still serves the other 29 surfaces.

An earlier id, `2ebb4312-…`, was superseded before it ever shipped. It is kept in `DEAD_HOOKS` and
gated rather than simply deleted: a retired trigger id is the most dangerous string in this file,
because posting to one produces no error, no contact and no lead — it fails exactly like success.
A stale copy in a branch, a doc or someone's clipboard now fails CI instead.

Beyond ending the ambiguity, this matters for bidding: the paid path is the only one that fires a
conversion Smart Bidding learns from, and it should not share an entry point with 29 organic
surfaces and a cookie banner.

**Gated in both directions.** The LP must carry the paid hook and must not carry the shared one;
no other file may carry the paid hook, since a second caller would put organic traffic into the
paid conversion workflow. Negative-controlled both ways. The gate holds trigger **ids**, not full
URLs — they are already public in every visitor's page source, but a grep of the validator should
not hand anyone a ready-to-POST endpoint.

### Flagged to the CTO, not fixed here — and it was the missing step

The swap moves contact creation. The legacy workflow on the shared hook was creating the contact;
after the swap nothing on that path does, so the paid workflow must create it itself. An Inbound
Webhook trigger does not create a contact on its own — that is an action, and it was not in the
wiring plan. **Named before the swap rather than discovered after it**, and it went into the final
build as the explicit first action.

### CONFIRMED LIVE — 2026-09-03

Verified by the CTO through GHL's Execution Logs, not by inspection: **three test submissions, one
clean single-pass execution each**, routed correctly to the Manager / Self-or-Tool / None branches
with the right email variant firing each time, and **zero duplicate or parallel executions** — the
last being the point of the whole change, since it is what proves the old trigger is detached
rather than quietly running alongside.

Smoke now asserts on the **served** page which trigger the LP posts to: the paid one present, the
shared one absent, the retired one absent. `validate-site.py` gates the repo copy; a stale deploy
or a bad rollback is a different question, and this is the one that would put paid leads back on
the shared hook with nothing visibly wrong.

---

## v3.23 — the consent posture is asserted against production, not just the repo (2026-09-03)

`mkx-consent.js` decides the consent signals for every visitor on every page, from one file. That
makes it the highest-leverage thing on this site to get wrong quietly: nothing renders differently,
nothing errors, and the first symptom is a regulator's question or a bidding signal that should
never have existed.

`validate-site.py` has gated the repo copy since v3.19. Smoke now gates the **served** one, on the
unblocked CI runner against production — a different question, and the one a stale deploy or a bad
rollback answers wrongly.

| Asserted on the live file | Addendum |
|---|---|
| `ad_personalization: 'denied'` present as a **literal** | C1 |
| `ad_personalization: ad` (the derived form) **absent** | C1 |
| Global Privacy Control honoured | B1 |
| Do Not Sell opt-out present | B1 |
| Canada inside the region gate | B2 |

**C1 is checked in both directions on purpose.** The pre-C1 shape was `ad_personalization: ad`,
which reads correct at a glance and is exactly what a careless edit restores — so "denied appears
somewhere in the file" would not have caught it. Asserting the literal *and* the absence of the
derived form is what makes the check mean something.

Negative-controlled four ways: reverting to the derived shape fires both C1 assertions, stripping
GPC fires, dropping Canada fires, and an empty body fires the fetch guard — which exists because
the absence checks **do** pass vacuously against nothing, exactly as v3.20 found when a dead origin
made four `/legal` checks report green.

### What this proves, and what it does not

It proves the deployed script carries the posture the addenda specify. The US-visitor behavioural
check that accompanied it — three timezones × three pages, `ad_storage` and `ad_user_data` granted,
`ad_personalization` denied in *every* consent call rather than merely the last, no banner, 63/0 —
ran against a clean worktree of the deployed commit rather than the live origin, because session
egress to `marketics.io` is denied and a browser confirmed that (`ERR_TUNNEL_CONNECTION_FAILED`)
rather than it being assumed. Static files plus a green production smoke make those the same bytes;
it is still not the same act, and the distinction is recorded rather than smoothed over.

### A stale local ref nearly produced a false alarm

Checking whether C1 had shipped, a first pass read a **stale local `main`** and found the pre-C1
`ad_personalization: ad`. Re-reading `origin/main` gave the correct answer. Anyone spot-checking a
clone should fetch first: that ref would have reported C1 as never having shipped, on the morning
of a paid launch.

---

## v3.24 — the measurement layer was double-blocked: consent AND CSP (2026-09-03)

`generate_lead_paid` never reached GA4. Three suspects were proposed — a build-time flag, a
redirect race, a silent JS error — and **all three were wrong.** The site's code was correct
throughout: a browser repro of the form submit put the event into `dataLayer` in every scenario
tested, including a deliberately slow GHL endpoint and a failing one.

The blocker was the **CSP `connect-src` header**, refusing every Google measurement beacon.

### Why it survived three days and every test we had

**`script-src` governs whether a tag LOADS. `connect-src` governs whether it can SEND.** Get the
second wrong and nothing looks broken: gtag.js loads, `page_view` may still arrive by an allowed
route, and the conversion beacon is refused into a console the visitor never opens.

**The trap that made it pass review:** `https://*.analytics.google.com` was already in the policy.
A CSP host wildcard matches **subdomains only, never the bare domain** — so `analytics.google.com`
itself was blocked while the line directly above it looked like it covered exactly that. If a host
is used both bare and as a subdomain, both forms must be listed.

Worth stating plainly, because the brief that arrived proposed adding seven hosts: two of them
(`*.google-analytics.com`, `www.googletagmanager.com`) were **already present**. The wildcard was
never the problem. The real delta was five hosts:

| Added to `connect-src` | Was blocking |
|---|---|
| `https://analytics.google.com` | `/g/collect` — GA4 |
| `https://www.google.com` | `/g/collect`, `/ccm/collect`, `/pagead/form-data` |
| `https://google.com` | `/pagead/form-data`, `/ccm/form-data` |
| `https://ad.doubleclick.net` | `/ccm/s/collect` |
| `https://googleads.g.doubleclick.net` | Ads conversion transport |

Only `connect-src` was touched. `script-src` and `img-src` were already correct — demonstrated by
gtag.js loading successfully the entire time, which is precisely what made the failure look like
application code.

### The blind spot, named

**A local server sends no CSP.** Every test in this repo — the validator, the browser repros, the
form-submit interception that proved the payload keys in v3.21 — runs against `python3 -m
http.server`, which has no security headers at all. So a code-level repro **passed while
production refused every beacon**, and it was right to pass: the code was fine.

Smoke now asserts the served `connect-src`, and the guard is scoped to the **directive**, not the
whole header. That is load-bearing: `www.google.com` is in `script-src`, so grepping the full CSP
would have reported this exact bug as passing.

Regression-tested against the real thing rather than asserted: replaying the guard against the
**pre-fix policy** fires on exactly the five blocked hosts and correctly passes
`*.google-analytics.com`. A CSP-less origin fires the vacuous-pass guard.

### Retroactive, and offered as a lead rather than a conclusion

The v2.7 anomaly — GA4 reporting ~2 users in 4 weeks against 28 GSC clicks on the homepage alone —
was attributed to consent gating. **It may never have been only that.** `analytics.google.com` and
`www.google.com/g/collect` were blocked for as long as this policy has stood, so some share of GA4
traffic was being refused at the header regardless of consent.

Not proven: the primary `*.google-analytics.com` endpoint *was* allowed, and which host gtag picks
varies by region and consent state. So this is a plausible contributing cause, not a demonstrated
one — recorded so that the next person reading the v2.7 entry knows consent was not the only
suspect, without overclaiming what was measured.

---

## v3.25 — the phantom traffic on `/calculator` was our own CI (2026-09-03)

GA4 Realtime showed three active users on `/calculator` and the question was whether something was
targeting it. It was **Lighthouse CI**.

| GA4 Realtime path | Users | |
|---|---|---|
| `/calculator/index.html` | 3 | = `numberOfRuns: 3` |
| `/lp/keep-control/index.html` | 3 | = `numberOfRuns: 3` |
| `/index.html` | 2 | Lighthouse, third run not yet counted |
| `/lp/keep-control` | 1 | **the only real session** |

**The `/index.html` suffix is the tell.** Netlify serves pretty URLs and the canon is the no-slash
form, so no visitor ever sees those paths — only lhci's own static server addresses pages that way.
The three URLs match `lighthouserc.json` exactly.

CI reaches GA4 because **lhci serves from `staticDistDir` with no CSP and the runner has open
internet** — the same blind spot as v3.24, seen from the other side. Our CI has had cleaner
analytics than our live site.

### What it does and does not pollute

**Conversions are clean.** Lighthouse never submits the form, so `generate_lead_paid` cannot fire
from CI. The number being imported into Ads is unaffected.

**Page-level metrics are inflated** — roughly nine page_views per PR into the production property,
so any rate computed against sessions is measuring partly against robots. It also means real
traffic is *lower* than the dashboard suggests, which sharpens rather than softens the v2.7 anomaly.

### `traffic_type: 'internal'`, stamped not suppressed

When `navigator.webdriver === true`, `mkx-consent.js` sets `traffic_type: 'internal'`. This became
urgent with v3.24: opening `connect-src` means CI's full event stream now transmits, where the
header had been refusing it.

**Deliberately not suppression.** Skipping gtag.js under webdriver would also stop measuring what
the tag *costs*, and v3.14 exists because the Ads tag cost `/calculator` ~1,850ms of LCP. A
prettier score that hides real third-party weight is the wrong trade — the same reason
`blockedUrlPatterns` was rejected. The tag loads exactly as it does for a visitor; only the data is
marked.

**Partial when first shipped; closed in v3.26.** The inline stub queues `gtag('config')` during
parse, so its page_view flushed ahead of the `set` and went out unstamped. The stub now carries the
parameter on the config call itself.

> **CORRECTION.** This entry originally proposed closing the gap with "a GA4 data filter on page
> paths ending in `/index.html`". **No such filter exists.** See v3.26.

Verified in a browser both ways: headless (`navigator.webdriver === true`) emits
`["set",{"traffic_type":"internal"}]`; spoofed as a real visitor emits nothing.

### `/calculator` sits on its floor — a dated P1, not a regression

The 0.79-vs-0.80 failure on this branch was **threshold drift, not a change**. Ruled out three
ways: the failing run predated the CSP commit by 77 minutes; main-vs-failing-head differed only by
`CANON-REGISTRY.md` and `scripts/smoke.sh`, neither browser-loaded; and `staticDistDir` means
Lighthouse never reads `netlify.toml`, so no header change can move a score. A later run on the
CSP head passed. **The budget was not relaxed**, and `/calculator` will keep flapping until the
page is genuinely faster.

---

## v3.26 — GA4 has no path-based data filters; stamp at config time instead (2026-09-03)

### The standing fact, recorded because it has now been proposed twice in one day

**GA4 data filters support exactly two types: Developer traffic and Internal traffic. Neither
matches URL or path patterns.** Internal traffic tests the `traffic_type` parameter. There is no
"exclude page paths ending in `/index.html`" filter to create, and no amount of looking in the
console will produce one.

Code proposed that mechanism twice on 2026-09-03 — once in v3.24's follow-up and again in v3.25 —
and it was struck both times. It is written here as a fact rather than a correction so the third
proposal does not happen: **if automated traffic is to be excluded from GA4, the exclusion has to
be stamped by the page.** The server side can only filter on what the page sends.

### The consequence: stamp on `config`, not via `set`

v3.25 stamped `traffic_type: 'internal'` with a separate `gtag('set')` from `mkx-consent.js`, and
was honest that this left one page_view unstamped per CI run: the inline stub queues
`gtag('config')` during parse, so it flushes first. With no path filter available to catch the
remainder, "accept the bounded gap" was the only fallback — so the gap is closed at source instead.

`navigator.webdriver` is readable at parse time, so the stub carries the parameter on the config
call itself:

```js
gtag('config','G-51HW9TQFTJ',navigator.webdriver===true?{traffic_type:'internal'}:{});
```

Applied to all **53** pages that carry the stub. The 54th, `/audits/<token>/`, has no stub and no
consent script by design (`CONSENT_EXEMPT_PREFIXES`) — nothing to stamp there.

The `set` in `mkx-consent.js` is kept, narrowed to what it is now for: the net for destinations
configured *after* the stub, which today is the Ads destination on the paid LP.

### Still stamped, not suppressed

Unchanged from v3.25 and worth restating, since the refinement makes suppression look tempting:
skipping gtag.js under webdriver would stop measuring what the tag *costs*, and v3.14 exists
because the Ads tag cost `/calculator` ~1,850ms of LCP. The tag loads exactly as it does for a
visitor; only the data is marked.

### Console task

Create the **Internal traffic** filter matching `traffic_type = internal`, set straight to
**Active**. That is the whole GA4-side job — there is no second filter.

### The stub comment, corrected in the same pass

All 53 stubs still carried *"ad_* stay denied everywhere pending an explicit decision when paid
launches — see CANON-REGISTRY v3.0."* That has been untrue since **Addendum B** granted the two ad
measurement signals outside the gated regions, and doubly so since **C1** made
`ad_personalization` permanently denied rather than pending. A comment that describes a *pending
decision* which has since been ruled twice is worse than no comment: it invites someone to "finish"
a decision that is already made.

Rewritten to state the actual posture — Canada in the gate, measurement signals granted outside it
and reversible by the Do Not Sell control or GPC, `ad_personalization` denied everywhere with no
Accept path — and to explain why the stamp sits on `config` rather than a later `set`. Comment-only
across 53 files; verified that every changed line is inside the comment block and that the consent
behaviour and the stamp are byte-for-byte unaffected.

---

## v3.27 — the sixth host, and the CORS error that is not a bug (2026-09-03)

### Unblocking one layer reveals the next

The first console capture showed five blocked hosts and v3.24 fixed those five. The post-deploy
console then showed a **sixth**: `pagead2.googlesyndication.com/ccm/collect`, where the Ads
conversion beacon actually goes.

It was not missing from the first capture by oversight. **A browser reports the first block, not
every block** — gtag never got far enough to attempt the conversion beacon while the earlier hosts
were being refused. So "fix everything the console showed" was a correct step and still an
incomplete one, and the same will be true of the next capture.

Added: `pagead2.googlesyndication.com` (demonstrated) and `www.googleadservices.com`
(**precautionary, and labelled as such**). Every other host in this directive was added only
against a demonstrated block; that distinction is kept visible rather than blurred, because "we
added it because the console showed it" and "we added it because it seemed likely" are different
kinds of claim and the file should not pretend otherwise.

### The GHL webhook CORS error is expected and harmless

```
Access to resource at 'https://services.leadconnectorhq.com/hooks/…' from origin
'https://marketics.io' has been blocked by CORS policy: … 'Access-Control-Allow-Origin'
must not be the wildcard '*' when the request's credentials mode is 'include'.
```

**The contact is created anyway.** Confirmed by Jason on 2026-09-03, and consistent with every
submission before it: the POST reaches GHL server-side; only the browser's ability to *read the
response* is refused. Nothing in this estate sets `credentials: 'include'` — the fetch is
byte-identical on `/lp/keep-control` and `/get-started`, and the escalation comes from the
visitor's browser environment.

`/get-started` has carried the comment *"Show confirmation regardless of the webhook's CORS/network
outcome"* since long before today; the code catches and proceeds by design. **This is recorded
because it looks exactly like a broken lead path and is not one.** It was re-diagnosed on a launch
day at the cost of a full stop, and it will look just as alarming to the next person who opens a
console.

The distinction that matters, if it ever does need investigating: a console CORS error is
consistent with the lead arriving. **The decisive test is whether the contact exists in GHL, not
what the console says.**

---

## v3.29 — the CORS errors were never the lead form (2026-09-03)

### The evidence was in the first screenshot

The failing request's URL ends **`b58c-e3a47721392e`**. That is
`1297f709-5970-411d-b58c-e3a47721392e` — the **consent beacon's** hook. The paid LP's form posts to
`3c750621-84a1-444d-b64a-5712e15cfb5e`, which appears in none of the errors.

On `/lp/keep-control`, the only thing that posts to `1297f709` is `beacon()` in `mkx-consent.js`.
The form and the beacon are two different requests to two different endpoints, and only the beacon
was failing.

**The lead form has been succeeding silently the whole time.** That is why a contact existed
alongside the errors — not intermittency, not a race, not luck.

### What that means for v3.27, and for the entry that briefly replaced it

- **v3.27 reached the right conclusion for the wrong reason.** "The CORS error is harmless, the
  contact is created anyway" is correct, and stands. The reasoning given — *"the POST reaches GHL
  server-side; only reading the response is refused"* — was wrong, and it was wrong about a request
  that was not the one erroring.
- **v3.28 (written, shipped, reverted the same evening; no longer in this file, since the revert
  took the entry with the code) overturned a correct conclusion using a correct general fact.** A
  failed preflight really does drop a request — that mechanism was demonstrated against a mock and
  remains true. But it was applied to the form, which was not the thing preflighting and failing.
  The result was a change that broke a working path to fix a problem it did not have, and cost
  roughly twenty minutes of silently dropped submissions.

The durable finding from that reverted entry, worth keeping even though its application was wrong:
**`application/json` is not CORS-safelisted and forces a preflight; a failed preflight sends
nothing at all. And GHL rejects a `text/plain` body**, so that escape route is closed — proven the
expensive way.

### The failure mode in my own reasoning

Two errors compounding, and the second was avoidable:

1. **I read the error text and not the URL.** The hook id was truncated in the console display but
   present, and it is the only thing that identifies *which request* failed. I diagnosed a symptom
   without establishing which component produced it.
2. **I then built a mock to test the mechanism** — and the mock was faithful about CORS while being
   silent about identity. It could confirm "a failed preflight drops a body". It could not tell me
   whether the request I was theorising about was the request that failed.

**Rule: before diagnosing why a request failed, establish which request it was.** On a page with
more than one endpoint, the error text is not enough; the URL is the identity.

### What is actually broken, and it is small

The consent beacon fails under `credentials:'include'`. It carries `consent_impression`,
`consent_accept`, `consent_decline` and `ad_optout` — instrumentation only, no lead data, and
already documented in-file as best-effort. Losing some of it costs an accept-rate signal that has
never been reliable anyway (it only fires where a banner renders).

`text/plain` is not the remedy for it either: GHL rejected that body outright, which is what #137
proved at the cost of twenty minutes of dropped leads. If the beacon is worth fixing, it is worth
fixing the same way the form would be — same-origin, through a proxy — not by another
Content-Type guess.

---

## v3.30 — the consent beacon never worked, and "we don't set that" was the wrong check (2026-09-03)

Removed on 2026-09-03 on Jason's ruling. Root cause, which is exact and not a probability:

**`navigator.sendBeacon()` always sends with credentials mode `include`.** That is specified
behaviour of the API, not a browser quirk, not a setting, and not an extension. The beacon passed a
`Blob` typed `application/json`, which is not one of the three CORS-safelisted Content-Types, so the
request required a preflight — and GHL answers preflights with a wildcard
`Access-Control-Allow-Origin: *`, which is invalid under credentials mode `include`. The preflight
failed every time, and a failed preflight sends nothing at all.

So the beacon was not intermittent, not degraded, and not environment-dependent. It delivered
**zero events from the day it shipped** (Aug 21 2026 CTO brief, P1) to the day it was removed. Four
console errors per banner render, no data, and nothing in the calling code able to tell.

### The check that failed

v3.27 recorded, as the reason the CORS errors were harmless: *"Nothing in the estate sets
`credentials: 'include'`."* That sentence is **true about our code and wrong about the request.**
`sendBeacon` sets it for us. The CTO brief then compounded it by reaching for a browser extension
to explain a credentials mode the platform was supplying by specification.

**Rule: "our code does not set X" is not the same as "X is not set."** A platform API has specified
defaults you did not write and cannot see at the call site. When a request behaves as though a flag
is set, read the API's spec, not only your own arguments.

This is a different failure from v3.29 and worth keeping separate. v3.29 was *not establishing which
request failed*. This one is *establishing the right request and then reasoning about it from our
source instead of the platform's contract.* Both produce a confident wrong answer from true premises.

### Why removal rather than a fix

Option B was to retype the Blob as `text/plain`, which is safelisted and would transmit. Ruled out:
whether GHL then **parses** that body is an assumption about a system we did not write, and that
exact assumption broke lead capture the same evening (#137, v3.29). Transmission is the half we can
verify; reception is not. If consent telemetry is wanted again it goes through a same-origin proxy,
where CORS does not apply at all — it is browser-enforced and a same-origin request never triggers
it. That also takes the webhook URL out of public page source and gives a submission-side counter.

Removed: `GHL_HOOK`, `beacon()`, its four call sites (`ad_optout`, `consent_impression`,
`consent_accept`, `consent_decline`), and the `mkx_imp` sessionStorage dedupe, which existed only to
stop the beacon firing once per pageview. Nothing else referenced it.

**Nothing measurable was lost, because nothing was ever measured.** The accept-rate signal this was
built to capture — the v2.7 "~2 users in 4 weeks against 28 GSC clicks" anomaly — has never had a
working instrument. That anomaly now has two partial explanations on record (consent gating, v2.7;
CSP refusing every measurement beacon, v3.24) and the thing that was supposed to arbitrate between
them was dead the whole time.

### Gated

- `validate-site.py`: `mkx-consent.js` may carry no `webhook-trigger/…` at all. Matched on the URL
  **path segment**, not a list of hook ids — a newly minted trigger id would sail past an id list
  and be the same mistake.
- `validate-site.py`: estate-wide, a `sendBeacon` call carrying a Content-Type outside the three
  safelisted values is a hard failure — on every HTML page and on both JS files, since `check()`
  only sees HTML.
- `smoke.sh`: the **served** `mkx-consent.js` carries no webhook trigger, behind the existing fetch
  guard. A stale deploy or a rollback is what would put it back, and the only symptom is console
  errors on a page nobody has open.

Negative-controlled four ways: the webhook gate fires on a re-added URL, the sendBeacon gate fires
in JS and in HTML, and a `text/plain` beacon produces no finding — the false-positive control, since
a gate that fires on the correct fix is worse than no gate.

### Confirmed the same evening, unrelated to the removal

`generate_lead_paid` **fires on production.** `dataLayer.filter(a => a[0] === 'event').map(a => a[1])`
returned `['generate_lead_paid']` after a real submission. Separately, a `collect` request to
`analytics.google.com` returned **204** carrying `gcs=G111` and `npa=1` — the CSP fix (v3.24/v3.27)
proven end-to-end, and board addendum **C1 verified on the wire** rather than only in source, since
`npa=1` is `ad_personalization: 'denied'` as Google received it. The event captured in that
particular request was `form_start`, GA4's own enhanced-measurement auto-event; it is generated
inside the tag and never appears in `dataLayer`, which is why the two observations agree rather
than conflict.

---

## v3.31 — Turno ship: two corrections that had nothing to correct (2026-09-03)

The Sept 3 Strategy brief (Rev B) asked for an estate-wide data correction, a tracked-link swap, and
the publication of `/intel/airbnb-operations-at-cost`. Two of those three had no targets.

### Findings, reported rather than worked around

- **`25,000` / `25000` / `25k` appear nowhere on this site.** Case-insensitive, every file. The only
  regex hits were base64 image data inside an `/audits/<token>/` page, which is untouched by rule.
  So the 126,000+ correction is a no-op in rendered copy **and** in structured data: there is no
  schema anywhere carrying the old figure either. The figure ships correct on the new page, which is
  its first appearance on the estate.
- **Turno is not mentioned anywhere on this site.** Every apparent match is the word *turnover*.
  There is no Turno brand mention, no partner card, and no plain `turno.com` link, so §2's tracked-link
  swap also has no targets. The tracked URL ships on the new page, again as its first appearance.
- **`/partners` and the Miami partner card do not exist, and that is by design.** They are sequenced
  behind partner volume: Jason is accumulating partners and their intel pages first, because a
  partner page carrying two cards is worse than no partner page. The page exists in the mockup, not
  on the estate, which is why two consecutive briefs specified inbound links from it. Jason has taken
  that as his own error and corrected the standing instruction (see the rulings below); it is not
  brief drift and should not be read as such.
- **Open Flag #4 was already closed**, at **v3.7 (2026-08-27)**, with the same 20–35% figure and the
  same two sources (SkyRun Apr 2026, PriceLabs May 2026). §5.2 re-affirms a closed flag rather than
  closing one. Recorded so a later reader does not think the flag was open for a week.

Code did not author a partner card, invent a `/partners` page, or manufacture links to hit a number.

### Registry rules added

**1. Partner statistics are the partner's own supplied or published figures.** When a partner corrects
a number it changes estate-wide in one pass, rendered copy and structured data together, never one
surface at a time. Schema-matches-copy applies to a partner's claims exactly as to ours.

**2. Wedge figure is 20–35%** (re-affirmed; see above). The 25–35% board-gate phrasing was the error,
and this settles the parenthetical v3.7 left open.

**3. Paid-only surfaces never receive links from organic surfaces.** `/lp/keep-control` is paid-only;
no intel page, partner page, or other indexed surface links to it, now or in future. Organic
conversion paths point to `/get-started`.

Rule 3 is **gated**, not just written down. It is the inverse of the existing no-exit rule and protects
a different thing: no-exit stops the paid page leaking traffic out, this stops organic traffic leaking
in. One link from an indexed page pours organic sessions into `generate_lead_paid` and the paid numbers
quietly stop meaning anything, because a lead still looks like a lead. Paid and organic never share a
counter (board ruling 4), so they must not share an entry point. Matched on the `/lp/` prefix rather
than the one slug, so a second landing page is covered the day it exists; negative-controlled both with
a query string and bare. Nothing links there today, which is why it goes in now, while it is free.

### The page

`/intel/airbnb-operations-at-cost` ships the Rev B copy verbatim: Jason Baxter byline, no partner
byline, no pen name, **no fee or referral disclosure** (no arrangement exists, so there is nothing to
disclose), tracked Turno link in a new tab with `rel="noopener"`, closing link to `/get-started`, and
the 20 to 35% wedge in the opening line as written.

What it deliberately does **not** carry: the deck, the "short answer" citation box, the FAQ block, and
the inline CTA box that the sibling intel pages have. The supplied copy contains none of them and Code
does not author canon-bearing copy. The page is structurally lighter than its siblings as a result;
that is a Strategy decision to make, not a gap to fill in silently. Its inherited stylesheet still
carries the rules for those blocks, which is dead CSS on this page and not worth the breakage risk to
strip tonight.

Canon verified mechanically: 45% appears exactly once in the whole file, with sample and gate sentence
in the same paragraph, "net of market" explained in plain language, methodology as plain text and not
a link, the ruled fee sentence verbatim, and zero em dashes in prose (the two in the file are the
`og:title` / `twitter:title` separators every other page uses).

**Inbound links: three, honestly counted.** The `/intel` hub card; a `Keep reading` card on
`/intel/what-a-property-manager-actually-costs` (the nearest sibling, per ruling 2); and a reciprocal
pair with `/intel/str-cost-segregation-tax-half`, added on Jason's go-ahead. The last one is the first
edge of the **partner intel mesh**: both pages are "the parts of running an STR that are not revenue
management", written for the same reader, and until tonight they did not reference each other at all.

That mesh is the point of the sequencing. Partners ramp, each gets an intel page, the pages link to
each other as they ship, and the city partner pages later link *down* into a cluster that is already
connected rather than a set of islands. The cost of publishing ahead of the partner pages is thin
inbound linking, which is the exact condition for Google's "crawled — currently not indexed"; cheap
sibling cards are what keep that from compounding one page at a time.

**The recrawl at the end of that sequence needs no manual step.** `indexnow.yml` submits the *entire*
sitemap on every push to `main`, not a diff, so the relink pass that lands when the partner pages ship
also re-submits every URL on the estate by itself.

Card counts checked in a browser rather than assumed: the ops page went 3 → 4, completing its two-column
grid, and the cost-seg page 2 → 3, the same shape every other sibling carries. Equal widths, no
overflow, no page errors.

**IndexNow needs no action** and the item left open at the Cost Seg Smart ship is closed:
`.github/workflows/indexnow.yml` now bulk-submits every sitemap URL on each push to `main`, so adding
the page to `sitemap.xml` is the whole job.

### Strategy rulings on this ship (2026-09-03)

**1. Ship without the deck, short-answer box, FAQ and CTA box.** They are standard for the intel
template, but this piece is a straight argumentative essay with one recommendation at the end. A FAQ
would mean inventing questions nobody asked, and a CTA box would duplicate the closing paragraph,
which already *is* the CTA. The one omitted element with real value is the **short-answer box** at the
top, because AI engines extract those and the unbranded prompts are still scoring zero. That is a
content addition rather than a formatting fix, so it is written properly later rather than improvised
at merge time. **Open Strategy item:** supply a short-answer box for this page if the template is to
stay consistent.

**2. Internal links are `/intel` index plus the nearest sibling article** — until a partners page
actually ships. No brief references `/partners` again. Worth noting that this needs no new gate: a
link to `/partners` already fails the existing broken-internal-link check, verified by negative
control. The rule that had to be written down was the positive one (what to link *to*), not the
prohibition.

**3. Evidence of a signal is not the signal.** `generate_lead_paid` was confirmed firing on production
the same evening, which is the evidence the CTO lane's LP verification rests on. It is not the
declaration. That signal is the CTO lane's to give, it gates ad spend as well as this publish, and a
gate on spend is given **once, explicitly, by its owner** rather than inferred from a passing
observation by someone else. Recorded as a general rule, because the tempting move is always to treat
a green check as the ruling it supports.

### §4 hold, and who released it

Publish was gated on the CTO lane's LP-verification signal. The evidence for that signal landed the
same evening — `generate_lead_paid` confirmed firing on production — but the ruling was never Code's
to infer from it (ruling 3 above).

**Jason released the hold himself, as owner of the brief, on 2026-09-03.** That is his to do; §4 is
his gate. It is recorded here as an owner release rather than left ambiguous, because the two are not
the same event and the difference matters downstream:

**Releasing the publish gate did NOT release the ad-spend gate.** The CTO lane's LP-verification
signal gates both. Publishing this page is not that signal and must never be read back as one. Ads
import remains blocked on the CTO lane declaring verification complete, explicitly and once. Anyone
reading "the page shipped" as "verification was declared" would be making exactly the inference
ruling 3 exists to prevent.


---

## v3.32 — CTO approval of the operations-at-cost publish, and one rule adopted (2026-09-04)

Approved. The approval arrived **after** the merge: Jason released his own §4 hold as brief owner and
instructed the merge ~25 minutes before the CTO checklist landed, so this was a retrospective approval
of shipped work. Recorded plainly, because "approved" and "approved before it shipped" are different
facts and the second one is not true here.

### Items 3 and 6: spec debt, not a Code gap

The checklist required the tracked Turno URL on a **Miami partner card**, and inbound links from
**`/partners`**. Neither surface exists. The CTO's own reading: the checklist propagated Strategy's
error, having passed those surfaces through without verifying them against the estate. Both items are
accepted **as substantively achievable** — tracked URL in the intel piece, sitemap and IndexNow, and
three real inbound links, which clears the ≥2 bar anyway.

The load-bearing behaviour was refusing to author a partner card to satisfy the letter of a checklist.
A manufactured card would have made every item read true and left a fabricated surface on the estate
carrying a partner's statistic. **Stop-and-route beat checklist compliance, and the checklist was the
thing that was wrong.**

### Rule adopted: a mid-flight scope addition is logged when it is authorised, not when it is approved

The reciprocal cost-seg cards were not in Rev B. Code proposed them, Jason authorised them mid-flight,
and Code named them in the approval summary. Authorisation was never in question; the CTO's note is
that the **naming arrived one gate too late** — a reviewer should meet a scope addition in the ledger,
not for the first time in the summary that asks them to approve it.

**From here: when work is authorised outside the brief that commissioned it, it gets a one-line
registry note at the moment of authorisation, carrying who authorised it and why.** Calibration, not
objection, and cheap enough that there is no reason not to.

### Item 7, taken

Flag #4 was closed by Jason's 20–35% ruling, logged in the CTO's Sep 3 brief to Strategy. The registry
entry records the ruling as **already made**, not as made by this PR. Correct as written.

### Parked: the Turno partner-card copy has no home yet

Routed to Strategy, not Code: their brief specced a Miami partner page and Turno card that do not
exist. Either the surfaces are planned and the brief was premature, or it was written against an
imagined estate. **The card copy is parked here verbatim so it is not lost between now and the page
being built**, together with the link treatment that is already proven on the intel piece:

> "Automated turnover scheduling straight from the booking calendar, a marketplace of 126,000+ vetted
> cleaners with per-clean pricing and photo checklists, and an official Airbnb Software Partner. The
> operations layer we recommend at every onboarding."

Link treatment, ready to reuse:
`https://turno.com/?utm_source=website&utm_medium=partner&utm_campaign=marketics_intel`, new tab,
`rel="noopener"`.

Two constraints that already bind that page the day it ships: it points at `/get-started`, never the
LP (the `/lp/` inbound gate fails CI otherwise), and the 126,000+ figure is Amy Plummer's supplied
statistic, so it moves estate-wide in one pass if she corrects it again — copy and structured data
together.


---

## v3.33 — `gclid` capture, consent-gated by ruling (2026-09-04)

Ruled Jason, Sep 4, amending Code's CTO brief of the same day. Code proposed a **consent-independent**
capture, matching how the UTM parameters already behave, and flagged that it raised a privacy question
it was not the right lane to answer. Jason's amendment is better than the proposal: **capture only where
`ad_storage` is granted.**

That inverts the situation. A consent-independent capture would have needed a counsel ruling on whether
an advertising identifier may be collected from someone who declined advertising consent. The gate
**moots that question rather than deferring it** — the case never arises. Ungated traffic, which is
where AG1–AG3 point, captures by default and loses nothing.

**Recorded as considered and not shipped:** the consent-independent variant goes to counsel (C4) first
if it is ever wanted. It must not be reintroduced as a simplification.

### Why the gate is gated

An unconditional capture reads like a harmless tidy-up — three fewer lines, one less indirection — and
it would silently put an advertising click identifier in the CRM for a visitor who was shown a banner
and declined. So the gate fails the build rather than relying on anyone remembering:
`validate-site.py` rejects `mkx-utm.js` if the capture exists without `adStorageGranted`, and rejects
`mkxCommitClickIds()` if it persists without calling it. `smoke.sh` asserts the gate on the **served**
file. Negative-controlled both ways.

### `/legal`, under C2

`/legal` said GHL receives "contact information, property details, and UTM attribution data". A `gclid`
is none of those, so the sentence would have been incomplete the day this deployed. Ruled a **factual
correction under Board Addendum C2** — Jason rules, Code drafts and ships with the ruling dated here.
The privacy tab now also states the negative case ("If you have not granted advertising consent, no
click identifier is collected or sent"), which is the part that is actually load-bearing for a reader.
Privacy tab dates moved to September 4, 2026; the terms tab is untouched by this edit and correctly
keeps September 1.

### Mechanism, and the one honest limitation

Click ids are read from the URL at load and held **in memory**, then committed to `sessionStorage` only
once `ad_storage` is granted — at load for ungated traffic, on Accept for a gated visitor. A gated
visitor who accepts after navigating away from the landing page is **not** captured, because the URL
carrying the id is gone. That is correct rather than a gap: they had not consented when the click
landed.

`adStorageGranted()` reads the same `dataLayer` gtag reads and **skips region-scoped defaults**, which
apply only inside their region list and cannot be evaluated from this file. Skipping them can only
withhold capture, never grant it.

Verified in a browser, 8 assertions, all four states: ungated captures; **gated-and-ignored does not,
and the lead still posts**; gated-and-accepted captures; and a prior Do Not Sell opt-out blocks capture,
because the gate is on the ad signals rather than on the grant (an opt-out calls `updateConsent(true)`
while denying all three ad signals).

### `wbraid` / `gbraid`

Captured under the same gate and sent under their own keys. **Deliberately not folded into
`gclid_first`**: Ads offline conversion import takes the three in separate upload columns, so conflating
them would produce a field that cannot be uploaded. No GHL field exists for them yet, so GHL will drop
them until one does — flagged rather than silently conflated.

### A fourth vacuous pass, found by a negative control on my own gate

The payload-key gate matches `^\s*<key>\s*:` per line. The explanatory comment I wrote above the new
key **began a line with `gclid_first:`** — so the comment satisfied the gate, and renaming the actual
key produced no finding. The gate could not fail. Found only because the negative control was run;
fixed by rewording the comment.

That is the **fourth** member of the vacuous-pass family this week, in a fourth layer: a CSP
whole-header grep that would have called the bug green (v3.24); a mock that validated its own
assumption (v3.29); a workflow that exits 0 on any HTTP code; and now a gate satisfied by its own
documentation. **A check that cannot fail is not a check** — and the only reliable way to find one is to
break the thing on purpose and confirm the check notices.


---

## v3.34 — campaign attribution has never reached the CRM (2026-09-04)

Found by submitting one live test lead before changing anything, rather than by adding the fix and
watching it work. That order is the whole reason the finding is this complete.

### The pattern, from one contact

| GHL field | Key we transmit | Result |
|---|---|---|
| `pricing_owner` | `pricing_owner` | **populated** ("manager") |
| `listingUrl` | `listingUrl` | **populated** |
| `Submitted At` | `submittedAt` | **populated** |
| `utm_source_first` … `utm_term_first` | `utm_source` … `utm_term` | **blank** |
| `first_touch_lp` | `landingPage` | **blank** |
| `first_touch_ts` | nothing | blank |
| `lead_form_id` | nothing | blank |
| `fbclid` | nothing | blank |

Every field whose key **exactly matches** a transmitted key is populated. Every field whose key
differs is blank.

> **CORRECTED by v3.35 (2026-09-04, same evening).** This entry originally concluded "there is no
> mapping bridge — GHL matches on the transmitted key." **That is wrong.** GHL requires an explicit
> mapping row per field, and `gclid_first` proved it: transmitted under the exact field key, it
> landed nowhere until a row was created. The fix shipped here was correct; the mechanism written
> down for it was not. See v3.35 for what is actually true.

**Consequence: UTM attribution has never reached the CRM.** The browser captured it correctly the
whole time, the payload carried it, the contact was created, the tag was applied, and the campaign
fields were empty. Nothing anywhere reported an error. The historical "contact created, zero
attribution data" symptom was only half fixed when the shared-trigger problem was solved in v3.22;
this is the other half, and it survived that fix because the visible parts all worked.

### Why the submission had to come first

The tempting move was to add the matching keys straight away — additive, low risk, obviously right.
It would have fixed the five UTM fields and **permanently destroyed the evidence** for the other
three, because a populated field cannot tell you whether it was populated by the new key or by a
bridge that was working all along.

One submission against the unchanged page answered all eight fields at once. That is the same
discipline as v3.29 (establish which request failed before diagnosing why) applied to a different
question: **establish what is actually broken before shipping the thing that would hide it.**

### Fixed here — the mechanical half

Six keys added to the LP payload, same values, keys matching the GHL field keys exactly:
`utm_source_first`, `utm_medium_first`, `utm_campaign_first`, `utm_content_first`, `utm_term_first`,
`first_touch_lp`. The unsuffixed keys stay until something is known not to read them; removing them is
a separate cleanup. Gated in `validate-site.py` and asserted on the served page in `smoke.sh`, each
negative-controlled.

### Routed, not authored — the non-mechanical half

- **`first_touch_ts`** — nothing captures a first-touch timestamp. `submittedAt` is a *different
  value* (submission time, already populating its own field), so mapping it here would fill the field
  with a plausible wrong number, which is worse than blank. Needs a real first-touch capture in
  `mkx-utm.js`, alongside the landing page it already stores. Small, and a scope addition.
- **`lead_form_id`** — semantics unclear. Candidates: the form's DOM id (`lpAuditForm`) or the
  `source` value (`lp-keep-control`, which already populates GHL's built-in Contact source). Guessing
  would put a stable-looking value in a field that means something else.
- **`fbclid`** — nothing captures it and the estate runs no Meta Pixel (both passages were removed
  from `/legal` on 2026-09-01). The field can never fill; it belongs on the existing dup-field cleanup
  item.

### Suspected but NOT evidenced

`/get-started` and `/join` transmit the same unsuffixed UTM keys and post to the **shared** organic
hook, whose workflow is a different mapping this test says nothing about. Their attribution is
plausibly blank for the same reason and that is a guess, not a finding. It needs its own test contact
through the organic form. Recorded as suspected so nobody reads this entry as having cleared them.


---

## v3.35 — the paid funnel is proven end to end, and v3.34's mechanism was wrong (2026-09-04)

### Proven, on a live contact

```
gclid_first        TESTGCLID_SEP4          first_touch_lp    /lp/keep-control
utm_source_first   google                  utm_medium_first  cpc
utm_campaign_first lptest                  utm_content_first ad1
utm_term_first     str                     pricing_owner     tool
```

GHL's own event message: *"Fields included: Email, listingUrl, pricing_owner, utm_source_first,
utm_medium_first, utm_campaign_first, utm_content_first, utm_term_first, Submitted At, Contact
source, gclid_first, first_touch_lp"* — twelve fields written. Full chain executed: create, tag,
Self/Tool branch, A1 confirmation, paid-lead notification.

**Capture → transport → CRM field is closed for the first time.** Offline conversion import now has
an identifier to match on. Closes the CTO's §7 done-when.

### The correction: GHL requires explicit mapping rows

v3.34 concluded there was **no mapping bridge** and GHL matched on the transmitted key. **Wrong.**
`gclid_first` was transmitted under the exact field key, in a payload GHL captured and displayed, and
the field read `--` until a row was added to the `Create contact` action. Rows are mandatory; a
matching key is necessary and not sufficient.

The v3.34 *fix* was right — send keys matching the field keys — and the *reason* recorded for it was
not. That is the v3.27 shape again: a correct conclusion resting on a wrong mechanism. Corrected in
place at v3.34 as well as here, because a reader who hits the old entry first would otherwise carry
the wrong model away.

**Still unexplained, and deliberately not invented:** why `utm_source_first` was blank at 15:43 and
populated at 16:05, when its row's chip reads `Inbound Webhook Trigger . Utm Source` — the unsuffixed
key, sent in both. Either the rows were edited between the two submissions or the chip label does not
mean what it appears to. It works; the mechanism is not written down because it is not known.

### The fifth vacuous pass: a stale sample labelled "Active"

The two tokens could not be selected because GHL builds its picker from **one captured request**:

> `MAPPING REFERENCE — Active: (2026-09-03 13:02:59) Request XLxmJvuvjrSdQtVBew2T`

A **Sep 3** snapshot. The new keys first shipped **Sep 4 at 16:05**. A sample taken a day before a
field existed cannot contain it. Re-pointing the reference to the Sep 4 request and saving the trigger
made both tokens available immediately.

Nothing indicated the reference was stale. The trigger said *Active*, the workflow ran, contacts were
created, tagged and emailed. Fifth member of the family this week, in a fifth layer:

1. a CSP whole-header grep that would have called the bug green (v3.24)
2. a mock that validated its own assumption instead of testing it (v3.29)
3. `indexnow-submit.sh` exiting 0 on any HTTP code
4. a payload-key gate satisfied by its own explanatory comment (v3.33)
5. a mapping reference labelled *Active* that was a day-old snapshot

**Operational rule: when the site starts sending a new payload key, the GHL Mapping Reference must be
re-pointed before the mapping can be created.** It is not discoverable from the failure — the field
simply reads `--`, and every visible part of the workflow succeeds.

### The near-miss worth keeping

The first attempt at the `gclid_first` row selected `Contact . Custom Fields . gclid_first` as its
value — reading the field's own empty value and writing it back. A permanent silent no-op that would
have looked correctly configured forever. **Jason caught it before saving and asked rather than
assuming.** That question was worth more than the fix.

### Still open, unchanged

`first_touch_ts` (nothing captures a first-touch timestamp; `submittedAt` is a different value and
mapping it there would fill the field with a plausible wrong number), `lead_form_id` (semantics
unclear), `fbclid` (nothing captures it, no Meta Pixel runs, it can never fill). All three remain
routed rather than authored.

Suspected but still not evidenced: `/get-started` and `/join` send unsuffixed keys to the shared
organic hook, whose mapping this says nothing about. Needs its own test contact.
## v3.38 — lead_form_id retired; delete-by-default; the Sep 5 attribution epoch (2026-09-05)

### `lead_form_id` is retired, not answered

Code routed it as a semantics question — form DOM id, or the source value that already populates
Contact source? CTO retired the field instead. **The right answer to "what should this field mean"
was that it should not exist:** `source` already carries which form produced the lead, and a second
field meaning almost the same thing is a field two people will read differently a year from now.
Not to be reintroduced without a stated use that `source` cannot serve.

### Delete-by-default for CRM fields nothing feeds

**A mapping row whose source key is never transmitted, or a CRM field nothing sends, is deleted
rather than kept "in case".** The default was previously the other way round — an unfed field looked
free, so it stayed — and the cost is not storage. It is that a blank field is ambiguous: nobody
reading a contact can tell whether the value was never collected, collected and lost, or collected
and empty. That ambiguity is what hid the fact that campaign attribution had *never* reached the CRM
(v3.34) behind a contact record that otherwise looked complete.

The bar for keeping an unfed field is now positive and narrow: **it carries qualification or fit
signal we actually intend to collect.** Convenience, symmetry with another field, and "we might want
it later" do not clear it. Later is when to add it, and adding is cheap now that a row can point any
key at any field (v3.37).

Two constraints on the deletion itself:

- **Removing a payload key requires a condition-reference check first.** GHL workflow *conditions*
  read transmitted keys, not just field mappings, and a branch whose condition stops matching looks
  exactly like a broken deploy — two hours went to that on 2026-09-03. `pricing_owner` is known to
  drive the Self/Tool branch. Check before removing, not after.
- **Removing a mapping ROW is a different act from removing a payload key** and needs no such check
  when the row is inert, because a row whose source is never transmitted already writes nothing.

### The Sep 5 attribution epoch

**Campaign attribution in the CRM begins on 2026-09-04 for paid and 2026-09-05 for organic.** Before
those dates the fields exist and are blank on every contact, because no mapping row filled them — not
because those leads had no campaign.

This is recorded because the blank fields are indistinguishable from real absence, which is the same
ambiguity the delete-by-default rule exists to stop creating. Any cohort analysis, CAC read or
attribution report that spans those dates is comparing a period with no attribution data to one with
it, and **will read as a step change in organic-vs-paid mix that did not happen.** Segment on or
after the epoch, or state the gap.

## v3.37 — a mapping row, not a payload key (2026-09-05)

### Both lead paths now carry attribution

Jason wired the organic workflow the morning of Sep 5: five `utm_*_first` rows plus
`first_touch_lp` **pointed at the `landingPage` key the form had been sending since it was built**.
Verified with a real submission — `organictest/t/c` matched, `first_touch_lp = /get-started/`, and a
bare-URL control correctly captured `/`. **No code change, and no Mapping Reference re-point**, because
that key was already in every snapshot. That was option C in the Sep 4 brief and it was right.

### The standing rule, and why it is a rule rather than a note

**A GHL field is filled by a MAPPING ROW, and a row can point ANY transmitted key at ANY field.**

v3.34 recorded the opposite — "GHL matches on the transmitted key, no mapping bridge" — and v3.35
corrected it. The consequence had not been drawn out until now, and it is the part worth keeping:
**the LP's six suffixed keys were never strictly necessary.** Six rows pointing at the unsuffixed
keys would have done the same job. They work and they stay; re-keying a lead path four days into
working is not a trade worth making, and the duplicate `landingPage` / `first_touch_lp` pair on the
LP stays deferred for the same reason.

But nothing new gets duplicated for that reason again. **The next CRM field that needs filling gets a
mapping row, not a payload change.** Recorded in three places at once — the LP's own comment, the
`validate-site.py` failure message, and the `smoke.sh` comment — because all three were still
teaching the wrong mechanism, and a gate whose failure message states a false rule is how the next
person makes a confident wrong call. Same reason v3.34 was corrected in place rather than only
superseded.

### `first_touch_ts` — authorised, with the shortcut refused in code

Ruled by CTO in the Sep 5 weekly. Captured in `mkx-utm.js`, session-scoped, ISO 8601 UTC, written
**inside the landing-page guard** so the landing path and the timestamp record the same event.

The refusal is the interesting half: **mapping `submittedAt` into the field stays refused.** It is a
real value from the wrong moment, and a CRM field full of confidently wrong timestamps cannot be told
apart from a correct one after the fact — blank is recoverable, wrong is not. That has a consequence
people will read as a bug: **a session that already carries a landing page and no timestamp gets
none**, because its first touch happened before the code existed. Correct, not a gap.

Three gates, because the shortcut is one line and reads like a simplification:

- the payload value is inspected, not just the key's presence — `first_touch_ts: new Date()...` sitting
  next to `submittedAt` doing exactly that would otherwise pass every check in the file
- `TS_KEY` must be written **exactly once**, so a second unconditional write cannot make every
  returning visitor's value the current page load
- that one write must sit inside the landing-page guard — **brace-matched**, see below

Sent from **both** forms, because both paths now carry attribution and a timestamp on half the leads
is useless for cohort analysis. No `/legal` edit: a first-touch timestamp introduces no new category
— `submittedAt` and `landingPage` already ship under the same sentence — but that is a
characterisation call and is flagged for **C4** rather than treated as settled.

Verified in a browser, 18 assertions: capture on first page; unchanged across three navigations;
earlier than submission time; a separate session gets its own value; a pre-existing session gets
none; and **both forms submitted for real with the webhook intercepted** — `first_touch_ts` present
in both payloads, matching what was captured, and distinct from `submittedAt`. That last step is
there deliberately: verifying capture to `sessionStorage` without submitting the form is exactly the
gap that let `gclid_first` reach the CRM as a blank field.

### `<br>` in headings, now gated repo-side (CTO authorised)

Item 6 of the GEO batch was defended only by a production smoke assertion, which speaks after a
merge. `validate-site.py` now fails the PR. Comments, `<script>` and `<style>` are stripped before
matching — the original sweep corrupted `/calculator` by matching an `<h1>` inside an HTML comment,
and **a checker has exactly the same exposure a rewriter does.**

### Vacuous passes six, seven and eight — all three inside checks written to close a vacuous-pass gap

1. **The homepage `ClaimReview` smoke check ran against the cleaned body**, and the cleaner strips
   `<script>` — where the JSON-LD lives. It inspected a document with every schema block already
   removed. **It read green with `ClaimReview` restored to the page.**
2. The `llms.txt` coverage failure message was unreadable in the direction where coverage *gains* the
   excluded page ("absent: 'none'").
3. **The first-touch guard check sliced at `} catch` instead of the `if` block's closing brace.** A
   write moved out of the conditional but left inside the same `try` still fell in that slice, so the
   check passed on precisely the regression it exists to catch. Replaced with real brace matching.

Eight members in nine days. The pattern has stopped being about any one check: **building the guard
and proving it can fail are different habits, and only the second one does work.** Every gate in this
entry was broken on purpose, and three of them were wrong the first time.

## v3.36 — the GEO batch (2026-09-04)

### llms.txt: gated, not generated

The brief asked for build-step generation. **There is no build step**, and nothing emits
`sitemap.xml` — it is hand-maintained, which is why 39 of 42 `lastmod` values were frozen at
2026-07-18. The goal (coverage cannot drift) is met differently: the sitemap is the source,
`scripts/gen-llms.py` gates `llms.txt` against it, and CI fails when a page is in one and not the
other. Exclusions, section routing and Strategy-supplied copy live in `scripts/llms-config.json`, so
a coverage decision appears in a diff instead of inside a script.

**Wholesale regeneration was considered and refused.** The 22 pre-existing entries carry curated GEO
copy; replacing their descriptions with meta descriptions would be **authoring by side-effect** —
rewriting approved text under cover of "generation". Existing entries are never touched; only missing
ones are added, sourced from each page's own approved `<meta name="description">`. Result: 41 of 42,
**zero lines removed**.

The audit cited 21 omitted URLs; the live sitemap yields 20. Most likely
`/intel/airbnb-operations-at-cost`, published after the audit ran. **The fixture is derived from the
current sitemap, not inherited from a stale count** — the same failure as a Mapping Reference
labelled "Active" (v3.35).

### ClaimReview retired as a class

Both nodes were Marketics reviewing Marketics: `author` and `itemReviewed.author` the same
organisation, rating our own 45% claim five stars with `alternateName: "Documented"`. ClaimReview is
fact-checking markup for accredited publishers; a claim we make about ourselves does not qualify.

Gated as a class: **ClaimReview banned outright, and any Review whose author is Marketics banned.**
The three customer reviews on `/results` are untouched — their authors are `Person` nodes, which is
exactly what makes them legitimate. Negative-controlled three ways including a **false-positive
control** proving the real reviews produce zero findings.

### lastmod: set by evidence, gated only against overclaims (ruled Jason, option B)

Naive git-per-file was built, run, and **rejected before shipping**. It dated 35 pages to 2026-09-03
and 7 to 2026-09-04, because commit `825222c` ("Correct the consent stub comment on all 53 pages")
touched 54 files. Verified on three files independently: 19 changed lines each, **zero outside the
HTML comment**. Shipping that tells crawlers the whole estate changed because a comment was edited —
the exact harm the brief chose git-per-file to avoid, arriving one day later.

**Git-per-file is only as honest as commit hygiene.** A mechanical sweep re-dates the estate exactly
like a build timestamp.

Values are now set by evidence: pages this batch genuinely changed → today; otherwise the page's own
JSON-LD `dateModified` where it has one; otherwise left alone. 20 / 14 / 8.

`scripts/gen-lastmod.py` is kept for `--check` only, wired into CI. It fails when a `lastmod` claims
a date **newer** than the file's real git date. It deliberately does **not** enforce equality: a
squash merge re-dates the commit, so equality would turn main red for reasons unrelated to content,
and a check that flaps gets ignored — the vacuous-pass family from the other direction.

**`lastmod` and `dateModified` are different facts** and are not driven from one source.
`lastmod` = this file changed. `dateModified` = this article was revised. Driving both from git makes
a heading sweep re-date every article, which `intel/SCHEMA-CHECKLIST.md` forbids in terms ("don't
fake a refresh"). The homepage contradiction the brief named is resolved honestly: its H1 **copy**
changed today, so both moved to 2026-09-04. The other 19 pages had markup swapped with identical
rendered text, so **zero** `dateModified` values moved.

### Byline scope: nothing to strip, and the stated goal is not true

There is no Melgar `Person` node anywhere. The author page is `WebPage`-only by design and the
article carries an `Organization` author — implemented under v3.11, before the brief asked for it.
**Second specified change in two briefs with no target** (after `25,000` and Turno).

The brief's goal — "the entity graph carries exactly one person, Jason Baxter" — **is not true and
should not be made true.** Eight other `Person` nodes exist: five media participants on `/media`, and
the three customer review authors on `/results`. Enforcing it literally would delete the very review
authors whose `Person` nodes make those reviews valid. Read as intent ("no manufactured
Marketics-side person"), it is already satisfied. Recorded as scope, not identity.

A gate written for this was **deleted before commit**: its negative control fired a message Code had
not written, revealing a comprehensive pen-name gate already at lines 511-535. Two gates for one rule
drift apart and the stale one gets trusted.

### `<br>` in headings: 60 across 28 files

`<br>` yields no whitespace when tags are stripped, so extraction read `YOURMARKET.MASTERED.` as one
token. Replaced with `<span class="hln">` blocks joined by a **real space** — the space is what makes
extraction correct; `display:block` restores the visual break. Both named test cases now read
correctly: "YOUR MARKET. MASTERED." and "Two Disasters. Zero Collapse." One **pre-existing** glue on
`/markets` (a nested block span with no preceding whitespace) fixed in passing.

Homepage H1 is now Strategy's verbatim sentence — **"Performance-based Airbnb revenue management",
exact string, no variants** (sign-off 2026-09-05). The wordmark is a `div` carrying the same class.

Placement was first shipped visually hidden via `.sr-only`, and that was flagged rather than
defended: **an audit that flags a logotype H1 will plausibly flag a hidden one next.** Strategy ruled
the better fix — the slot directly above the wordmark was already a kicker, so it was **promoted to
the `h1`** and its text swapped. That yields a real, visible H1 naming the category, with no new
element and no visual change beyond three characters of line length. `.bar` became a `<span>`
because a `<div>` inside an `<h1>` is invalid; it is a flex item either way and renders identically.

**One string, one slot, one H1.** The claim is deliberately not restated elsewhere: a second copy in
the reach strip would be the redundant-repetition pattern the content analysis already docked. The
audit's own suggestion — add a descriptive H1 *alongside* the wordmark — was declined in favour of
this, which gets the same machine-readable result with one fewer element to defend.

Verified at 1440px and 390px: H1 visible in both, no overflow, no page errors, wordmark box
unchanged.

**A corruption caught by testing, not by review.** The first sweep matched an `<h1>` inside an HTML
*comment* in `/calculator` and swallowed everything to the next `</h1>` 93 lines later, mangling the
real heading and leaving an orphan `</span>`. Found by an extraction test, not by reading the diff.
The whole sweep was reverted and redone with comments, `<style>` and `<script>` masked out.
**A regex that finds tags will find them in comments too.**

### The "Anthony alias note": there is no alias (ruled Jason, 2026-09-04)

The done-when asked for an **"Anthony alias note"**, which implies the name stands in for someone.
Nothing in the repo supported that: `/case-studies/anthony-san-antonio` uses the name throughout —
nine times in body copy, in the schema `headline`, and in the slug — with no disclaimer anywhere.

Code declined to write the entry rather than assert an unverifiable fact about a named client, and
routed it. **Jason ruled: Anthony is the client's real name.** So no alias note exists to write, no
on-page disclosure is required, and the pen-name treatment (v3.11) does not apply here — that
convention exists for a firm's editorial byline, not for a named case-study subject.

Recorded so the question is not reopened by the next reader of that brief. **A named case-study
subject is a real person unless the registry says otherwise**, and nothing about Anthony needs
qualifying.


---

## Version history


- **v3.36** (2026-09-04) — **the GEO batch.** `llms.txt` is **gated, not generated**: there is no build step and nothing emits `sitemap.xml`, so the sitemap is the source and CI fails when a page is in one and not the other. Wholesale regeneration refused as **authoring by side-effect** — 41 of 42 covered, **zero existing lines removed**. Audit cited 21 omissions, live sitemap yields 20; fixture derived from the current sitemap, not a stale count. **ClaimReview retired as a class** (both nodes were Marketics reviewing Marketics); customer reviews untouched because their authors are `Person` nodes, proven by a false-positive control. **lastmod set by evidence, not git-per-file:** the naive version dated 35 pages to Sep 3 because a comment-only sweep touched 54 files — the exact harm the brief chose git-per-file to avoid. Git-per-file is only as honest as commit hygiene. CI keeps the **overclaim gate only** (never equality: a squash merge re-dates commits, and a check that flaps gets ignored). **`lastmod` and `dateModified` are different facts** and are not driven from one source; the homepage moved both because its H1 copy genuinely changed, and zero other `dateModified` values moved. **Byline scope: nothing to strip** — no Melgar `Person` node exists, implemented under v3.11 before the brief asked. The stated goal ("exactly one person") **is not true and must not be made true**: eight legitimate third-party `Person` nodes exist, including the review authors whose nodes make those reviews valid. A gate written for it was deleted before commit when its negative control revealed an existing gate. **60 `<br>` removed from headings across 28 files**, replaced with block spans joined by a real space — the space is what fixes extraction. **A corruption caught by testing, not review:** the first sweep matched an `<h1>` inside an HTML comment and swallowed 93 lines; reverted and redone with comments masked. **A regex that finds tags will find them in comments too.** **The "Anthony alias note" is closed, not written:** the brief's phrasing implied an alias; nothing in the repo supported one, and Code declined to assert an unverifiable fact about a named client. **Jason ruled the name is real**, so no note and no on-page disclosure are needed — the pen-name treatment (v3.11) covers a firm's editorial byline, not a case-study subject.
- **v3.35** (2026-09-04) — **the paid funnel is proven end to end, and v3.34's mechanism was wrong.** A live contact now carries `gclid_first: TESTGCLID_SEP4`, `first_touch_lp: /lp/keep-control` and all five `utm_*_first`; GHL's own event message confirms twelve fields written and the full chain executed. **Capture → transport → CRM field is closed for the first time**, and offline conversion import finally has an identifier to match on. Closes the CTO's §7 done-when. **The correction:** v3.34 concluded there was no mapping bridge and GHL matched on the transmitted key. Wrong — `gclid_first` was transmitted under the exact field key and landed nowhere until an explicit row was added to the `Create contact` action. Rows are mandatory; a matching key is necessary, not sufficient. The fix was right, the recorded reason was not — the v3.27 shape again, corrected in place at v3.34 too so a reader hitting the old entry does not carry the wrong model away. **Fifth vacuous pass:** the tokens were unselectable because GHL builds its picker from one captured request, and the `MAPPING REFERENCE` read *"Active: (2026-09-03 13:02:59)"* — a snapshot from the day before the keys existed. Re-pointing it to the Sep 4 request made both available at once. Nothing indicated staleness: the trigger said *Active*, contacts were created, tagged and emailed. **Rule: when the site starts sending a new payload key, the Mapping Reference must be re-pointed before the mapping can be created** — the failure is invisible, the field simply reads `--`. **Near-miss worth keeping:** the first attempt selected `Contact . Custom Fields . gclid_first` as the value — the field reading its own empty value back into itself, a permanent silent no-op that would have looked configured forever. Jason caught it before saving and asked rather than assuming. **Still unexplained and deliberately not invented:** why `utm_source_first` was blank at 15:43 and populated at 16:05 when its chip reads the unsuffixed key, sent in both. It works; the mechanism is not recorded because it is not known.
- **v3.34** (2026-09-04) — **campaign attribution has never reached the CRM.** One live test lead, submitted *before* changing anything, showed the pattern exactly: every GHL field whose key matches a transmitted key is populated (`pricing_owner`, `listingUrl`, `submittedAt`), and **every field whose key differs is blank** — all five `utm_*_first`, plus `first_touch_lp`. **There is no mapping bridge**; GHL matches on the transmitted key, which is v3.21 holding at estate scale rather than a one-off about `listingUrl`. So the browser captured UTM data correctly, the payload carried it, the contact was created and tagged, and the campaign fields were empty, with nothing reporting an error. The v3.22 shared-trigger fix was only half of "contact created, zero attribution data"; this is the other half, and it survived because every visible part worked. **The order was the finding:** adding the matching keys first would have fixed five fields and permanently destroyed the evidence for the other three, since a populated field cannot say whether the new key or an existing bridge filled it. Same discipline as v3.29, applied to a different question — establish what is actually broken before shipping the thing that would hide it. Fixed here (mechanical): six keys added matching the GHL field keys exactly, unsuffixed keys retained, gated in the validator and asserted on the served page, negative-controlled. **Routed, not authored:** `first_touch_ts` (nothing captures a first-touch timestamp; `submittedAt` is a different value and would fill the field with a plausible wrong number), `lead_form_id` (semantics unclear), `fbclid` (nothing captures it and no Meta Pixel runs — it can never fill). **Suspected but not evidenced:** `/get-started` and `/join` send the same unsuffixed keys to the shared hook, whose mapping this test says nothing about; recorded as a guess needing its own test contact, so nobody reads this entry as clearing them.
- **v3.33** (2026-09-04) — **`gclid` capture, consent-gated by ruling.** Code proposed a consent-independent capture (matching the UTM parameters) and flagged the privacy question; Jason amended it to **capture only where `ad_storage` is granted**, which **moots that question rather than deferring it** — the case of collecting an advertising identifier from someone who declined never arises. Ungated traffic, where AG1–AG3 point, captures by default. The consent-independent variant is recorded as **considered and not shipped**: it goes to counsel (C4) first if ever wanted, and must not return as a "simplification". The gate is itself gated, because dropping it looks like a tidy-up and would silently put a click identifier in the CRM for someone who declined: `validate-site.py` rejects the capture without `adStorageGranted`, and rejects `mkxCommitClickIds()` if it persists without calling it; `smoke.sh` asserts it on the served file. `/legal` gains the disclosure as a **C2 factual correction**, including the negative case ("if you have not granted advertising consent, no click identifier is collected or sent"); privacy-tab dates to Sep 4, terms tab untouched and correctly still Sep 1. Ids are held in memory and committed only on grant, so a gated visitor who accepts after navigating away is not captured — correct, not a gap. Verified in a browser across all four states (8 assertions): **gated-and-ignored does not capture and the lead still posts**. `wbraid`/`gbraid` ride the same gate under their own keys, deliberately not folded into `gclid_first`, since Ads offline import takes the three in separate columns. **And a fourth vacuous pass, found by a negative control on my own gate:** the explanatory comment I wrote began a line with `gclid_first:`, satisfying the very `^\s*<key>\s*:` gate meant to catch a rename — the check could not fail. Fourth member this week, in a fourth layer (CSP whole-header grep, a mock validating its own assumption, a workflow exiting 0 on any HTTP code, and now a gate satisfied by its own documentation). **A check that cannot fail is not a check**, and breaking it on purpose is the only reliable way to find out.
- **v3.32** (2026-09-04) — **CTO approval of the operations-at-cost publish, granted retrospectively.** Jason released his own §4 hold as brief owner and instructed the merge ~25 minutes before the checklist arrived; recorded plainly, since "approved" and "approved before it shipped" are different facts and only the first is true. **Items 3 and 6 were unsatisfiable as written** — they required a Miami partner card and inbound links from `/partners`, neither of which exists — and the CTO ruled that his checklist had propagated Strategy's error rather than verifying those surfaces against the estate. Both accepted as substantively achievable. The load-bearing behaviour was **refusing to author a partner card to satisfy the letter of a checklist**: a manufactured card would have made every item read true and left a fabricated surface carrying a partner's statistic. Stop-and-route beat compliance, and the checklist was the thing that was wrong. **Rule adopted: a mid-flight scope addition is logged when it is authorised, not when it is approved.** The reciprocal cost-seg cards were authorised by Jason mid-flight and named in the approval summary; authorisation was never in question, but a reviewer should meet a scope addition in the ledger rather than in the summary asking them to approve it. From here, work authorised outside its commissioning brief gets a one-line registry note at the moment of authorisation, with who authorised it and why. Item 7 correction taken: Flag #4 was closed by Jason's 20–35% ruling, and the registry records it as already made rather than made by this PR. **Parked:** the specced Turno partner-card copy and its proven link treatment are recorded verbatim here, because the surface they were written for does not exist and the phrasing would otherwise be lost between now and the page being built. Two constraints already bind that page: it points at `/get-started`, never the LP (the `/lp/` gate fails CI otherwise), and the 126,000+ figure is Amy Plummer's, so it moves estate-wide in one pass if she corrects it.
- **v3.31** (2026-09-03) — **the Turno ship: two of three corrections had no targets.** `25,000`/`25000`/`25k` appear **nowhere** on the estate (case-insensitive, every file; the only regex hits were base64 image data in an `/audits/<token>/` page), so the 126,000+ correction is a no-op in copy **and** schema. **Turno is not mentioned anywhere either** — every apparent match is the word *turnover* — so the tracked-link swap has no targets; both values ship for the first time on the new page. `/partners` and the Miami partner card **do not exist, by design** — sequenced behind partner volume, since a partner page with two cards is worse than none — so the "two internal links in (`/partners`, `/intel` index)" bar cannot be met as written; Jason took the repeated reference as his own error and corrected the standing instruction to **`/intel` index plus the nearest sibling article** until a partners page ships. That needs no new gate: a `/partners` link already fails the broken-internal-link check, negative-controlled. And **Open Flag #4 was already closed at v3.7** (2026-08-27) with the same figure and the same two sources, so §5.2 re-affirms rather than closes. Code authored no partner card, invented no `/partners`, and manufactured no links to hit a number. **Three rules recorded:** partner statistics are the partner's own figures and change estate-wide in one pass, copy and structured data together; the wedge figure is **20–35%** (settling the parenthetical v3.7 left open); and **paid-only surfaces never receive links from organic surfaces**. That last one is **gated** — the inverse of the no-exit rule, protecting the opposite direction: no-exit stops the paid page leaking traffic out, this stops organic traffic leaking in and quietly corrupting `generate_lead_paid`, since a lead still looks like a lead. Matched on the `/lp/` prefix so a second LP is covered the day it exists; negative-controlled bare and with a query string. Nothing links there today, which is why it goes in while it is free. **The page** ships the Rev B copy verbatim (Jason byline, no disclosure, tracked Turno link in a new tab, closing link to `/get-started`, 20 to 35% as written) and deliberately omits the deck, short-answer box, FAQ and CTA box its siblings carry, because the supplied copy contains none and Code does not author canon-bearing copy. Canon verified mechanically: 45% exactly once, sample and gate sentence in the same paragraph, methodology as plain text not a link, zero em dashes in prose. Three inbound links, honestly counted: the `/intel` hub card, a `Keep reading` card on the nearest sibling, and a **reciprocal pair with the cost-seg page** — the first edge of the partner intel mesh, two pages written for the same reader that did not reference each other at all until now. That mesh is the point of the sequencing: partners ramp, each gets an intel page, the pages link to each other as they ship, and the city partner pages later link *down* into a connected cluster instead of a set of islands. The recrawl at the end needs no manual step — `indexnow.yml` submits the **entire** sitemap on every push to `main`, not a diff. IndexNow now needs no action (automatic on push to `main`), closing the item left open at the Cost Seg ship. Publish was held for the CTO lane's signal; **Jason released that hold himself, as owner of the brief** — recorded as an owner release, not as the CTO signal, because **releasing the publish gate did not release the ad-spend gate**: the CTO lane's LP verification gates both, ads import stays blocked on it, and "the page shipped" must never be read back as "verification was declared". **Strategy ruled** the page ships without the deck, short-answer box, FAQ and CTA box: it is an argumentative essay with one recommendation, a FAQ would invent questions nobody asked, and a CTA box would duplicate the closing paragraph that already *is* the CTA. The one omission with real value is the **short-answer box** (AI engines extract those; unbranded prompts still score zero) and it is a content addition, not a formatting fix — left as an open Strategy item rather than improvised at merge time. **Rule recorded: evidence of a signal is not the signal.** `generate_lead_paid` firing on production is the evidence the CTO lane's verification rests on, not the declaration; a signal that gates ad spend is given once, explicitly, by its owner, never inferred from a passing observation by someone else.
- **v3.30** (2026-09-03) — **the consent beacon never worked, and "we don't set that" was the wrong check.** `navigator.sendBeacon()` **always** sends with credentials mode `include` — specified behaviour, not a quirk and not an extension. The beacon's `application/json` Blob is not CORS-safelisted, so it needed a preflight, and GHL's wildcard `Access-Control-Allow-Origin: *` is invalid under credentials mode `include`. The preflight failed every time and a failed preflight sends nothing: **zero events delivered from the day it shipped** (Aug 21 2026) to its removal. Not intermittent, not environment-dependent. This retires two things on record: v3.27's *"nothing in the estate sets `credentials: 'include'`"* — true about our code, wrong about the request — and the CTO brief's extension theory, which reached for a cause the platform was already supplying by spec. **Rule: "our code does not set X" is not the same as "X is not set."** A platform API has defaults you did not write and cannot see at the call site; read the spec, not only your own arguments. Distinct from v3.29, which was failing to establish *which* request failed — this is establishing the right request and then reasoning about it from our source instead of the platform's contract. **Jason ruled removal, not a Content-Type change:** whether GHL *parses* a `text/plain` body is an assumption about a system we did not write, and that exact assumption broke lead capture the same evening (#137). Removed `GHL_HOOK`, `beacon()`, its four call sites and the `mkx_imp` dedupe that existed only to throttle it. Nothing measurable was lost because nothing was ever measured — the v2.7 accept-rate anomaly's designated instrument was dead the whole time. If consent telemetry returns it goes same-origin through a proxy, where CORS does not apply at all. Gated three ways (no `webhook-trigger/` in `mkx-consent.js`, matched on the path segment so a *new* hook id fails too; no non-safelisted `sendBeacon` type anywhere, HTML and both JS files; the served file in smoke behind its fetch guard), negative-controlled four ways including a `text/plain` false-positive control. Also confirmed this evening: **`generate_lead_paid` fires on production** (`dataLayer` returned `['generate_lead_paid']`), and a `collect` to `analytics.google.com` came back **204** with `gcs=G111` and `npa=1` — the CSP fix proven end-to-end and **C1 verified on the wire**, not just in source.
- **v3.29** (2026-09-03) — **the CORS errors were never the lead form.** The failing URL ends `b58c-e3a47721392e` — the **consent beacon's** hook (`1297f709-…`). The paid LP's form posts to `3c750621-…b64a-5712e15cfb5e`, which appears in none of the errors. On that page the only thing posting to `1297f709` is `beacon()` in `mkx-consent.js`, documented in-file as *"best-effort; never block the banner."* **The form has been succeeding silently throughout** — that is why a contact existed alongside the errors, not intermittency or luck. Consequences: v3.27's conclusion (harmless, contact created) was right for the wrong reason and stands; v3.28 — written, shipped and reverted the same evening — overturned it using a true general fact applied to the wrong request, breaking a working path and dropping ~20 minutes of submissions. **My reasoning failure, in two steps:** I read the error text and not the URL, so I never established *which* request failed; then I built a mock faithful about CORS but silent about identity, which could confirm the mechanism while being unable to tell me it was the wrong component. **Rule: before diagnosing why a request failed, establish which request it was — on a page with more than one endpoint, the URL is the identity, not the error text.** Durable from the reverted entry: `application/json` forces a preflight and a failed preflight sends nothing; and GHL rejects `text/plain`, so that route is closed. What is actually broken is the beacon — instrumentation only, no lead data — and it needs the same-origin proxy, not another Content-Type guess.
- **v3.27** (2026-09-03) — **a sixth blocked host, and a CORS error that is not a bug.** The post-deploy console showed `pagead2.googlesyndication.com/ccm/collect` still refused — not an oversight in v3.24 but the shape of the problem: **a browser reports the first block, not every block**, so gtag never reached the conversion beacon while earlier hosts were being refused. "Fix what the console showed" is correct and incomplete, and will be again next time. Added it plus `www.googleadservices.com`, the latter labelled **precautionary** rather than evidenced, since every other host here was added against a demonstrated block and the two kinds of claim should stay distinguishable. Also recorded: the GHL webhook's CORS error (`ACAO must not be '*' when credentials mode is 'include'`) is **expected and harmless — the contact is created anyway**, confirmed by Jason. Nothing in the estate sets `credentials: 'include'`; the fetch is identical to `/get-started`, which has carried "show confirmation regardless of the webhook's CORS/network outcome" since long before today. Written down because it looks exactly like a broken lead path, cost a full stop on a launch day, and will alarm the next person to open a console. **The decisive test is whether the contact exists in GHL, not what the console says.**
- **v3.26** (2026-09-03) — **GA4 has no path-based data filters.** Data filters are Developer traffic and Internal traffic only; Internal traffic tests `traffic_type`. Recorded as a standing fact because Code proposed a nonexistent "exclude paths ending in `/index.html`" filter **twice in one day** and it was struck both times — if automated traffic is to be excluded, the page has to stamp it, because the server side can only filter on what the page sends. Consequence: the v3.25 gap (one unstamped page_view per CI run, since the stub's `gtag('config')` flushes before a separate `set`) is closed at source rather than accepted — `navigator.webdriver` is readable at parse time, so the stub now carries `traffic_type` on the config call itself across all **53** stub-bearing pages. The 54th, `/audits/<token>/`, has no stub by design. The `set` in `mkx-consent.js` is kept and narrowed to its real job: destinations configured after the stub, i.e. the Ads destination on the paid LP. Still stamped, not suppressed (v3.14). Console task is one filter: Internal traffic, `traffic_type = internal`, Active.
- **v3.25** (2026-09-03) — **the phantom traffic on `/calculator` was our own CI.** GA4 Realtime's three active users matched `lighthouserc.json`'s three URLs at `numberOfRuns: 3` exactly; the `/index.html` suffix is the tell, since Netlify serves pretty URLs and no visitor ever sees those paths. lhci serves from `staticDistDir` with no CSP on a runner with open internet — the v3.24 blind spot from the other side. Conversions are clean (Lighthouse never submits the form) but page-level metrics carry ~9 page_views per PR, so real traffic is *lower* than the dashboard shows. `traffic_type: 'internal'` now stamps `navigator.webdriver` traffic — **stamped, not suppressed**, because skipping gtag.js would stop measuring what the tag costs and v3.14 exists for that reason. Partial as first shipped and stated as such; closed at config time in v3.26 (the GA4 path-filter proposed here does not exist). Verified both ways in a browser. Also: the 0.79-vs-0.80 `/calculator` failure was **threshold drift, not a regression** — ruled out three ways (the failing run predated the CSP commit by 77 minutes; the diff was registry + smoke only; Lighthouse never reads `netlify.toml`), and a later run on the CSP head passed. Budget not relaxed; `/calculator` is a dated P1.
- **v3.24** (2026-09-03) — **the measurement layer was double-blocked: consent AND CSP.** `generate_lead_paid` never reached GA4; the three suspects proposed (build-time flag, redirect race, silent JS error) were all wrong, and a browser repro proved the site pushes the event to `dataLayer` in every scenario including a slow and a failing GHL endpoint. The blocker was CSP `connect-src` refusing every Google measurement beacon. **`script-src` governs whether a tag loads; `connect-src` governs whether it can send** — so gtag.js loaded fine the whole time and nothing looked broken. The trap: `https://*.analytics.google.com` was already listed, and a CSP host wildcard matches **subdomains only, never the bare domain**, so `analytics.google.com` was blocked by the line that appeared to allow it. Two of the seven hosts in the incoming brief were already present; the real delta was five (`analytics.google.com`, `www.google.com`, `google.com`, `ad.doubleclick.net`, `googleads.g.doubleclick.net`), `connect-src` only. Named blind spot: **a local server sends no CSP**, so every browser repro in this repo is structurally blind to this class of bug and passed while production refused every beacon. Smoke now asserts the served `connect-src` scoped to the **directive** — load-bearing, since `www.google.com` is in `script-src` and a whole-header grep would have called this bug green. Regression-tested by replaying the guard against the pre-fix policy: fires on exactly the five blocked hosts. Retroactive lead, not a conclusion: the v2.7 "~2 users vs 28 GSC clicks" anomaly may never have been only consent gating.
- **v3.23** (2026-09-03) — the consent posture is now asserted against **production**, not just the repo: smoke checks the served `mkx-consent.js` for C1's hardcoded `ad_personalization: 'denied'` **and** the absence of the pre-C1 derived `ad_personalization: ad`, plus B1's GPC and Do Not Sell opt-out and B2's Canada gate. Both directions on C1 deliberately — "denied appears somewhere" would not catch the derived shape, which reads correct at a glance. Negative-controlled four ways including an empty body, which fires the fetch guard because the absence checks genuinely do pass vacuously (v3.20). The accompanying US-visitor behavioural check (3 timezones × 3 pages, 63/0, `ad_personalization` denied in every consent call rather than only the last) ran against a clean worktree of the deployed commit, not the live origin — egress to `marketics.io` is denied and a browser confirmed it; same bytes, not the same act, and recorded as such. Also fixes the `## Version history` heading dropped from this file in v3.22.
- **v3.22** (2026-09-03) — the paid LP gets its **own** inbound-webhook trigger (`3c750621-…`), separating it from the shared organic hook that 29 files use, the consent beacon included. Sharing it meant the paid workflow could only distinguish itself by filtering on `source`, and a filter that silently stops matching is indistinguishable from a broken deploy — two hours were lost hunting for a serverless Function that has never existed here (every GHL call on this site is a browser fetch to an inbound webhook, so the site cannot map a field or apply a tag at all). Contacts were being created by whatever legacy workflow owns the shared hook while the new paid workflow showed 0 executions, never having been pointed at. Fix was wiring, not archaeology. The owner, once found, was "Inbound Lead" -- already restored and ruled out during the hunt as pre-dating the website; it created contacts and never tagged them. Ruling a workflow out by name and vintage is what kept the search running: a workflow can acquire a webhook trigger long after its name stopped describing it. Gated both directions — the LP must carry the paid hook and not the shared one, and no other file may carry the paid hook — negative-controlled both ways, with ids rather than full URLs in the validator. Flagged and not fixed here: after the swap nothing creates the contact unless the paid workflow does it itself.
- **v3.21** (2026-09-01) — a form field's `name` is **not** the key the webhook sends: the LP hand-builds its JSON payload, so `name="listing_url"` transmits as `listingUrl` and is never sent as written. Code had read the markup rather than the request earlier the same day and gave Jason a wrong key while debugging a GHL error; corrected directly. The pricing dropdown already reached GHL as `pricingOwner`; `pricing_owner` added alongside it so the new custom field maps like-for-like, with the old key kept until something is known to no longer read it. The transmitted values are the option **values** (`me`, `manager`, `tool`, `unsure`, `""`), not the visible labels — a conditional branch built on "My property manager" would never have fired. Payload keys now gated by name, negative-controlled three ways; all five options verified by intercepting the real POST, 25/25.
- **v3.20** (2026-09-01) — **`/legal` corrected — the first edit Code has ever made to that document**, on Jason's approval of the C3 redline (all seven edits plus all three flagged items). Google Ads named in §04.1 and §06; §03's sell sentence kept verbatim with the advertiser claim replaced by what is actually shared; both Meta Pixel passages removed; Clarity corrected to consent-only in four jurisdictions; §08 describing the Do Not Sell control and GPC; dates moved on both tabs; and the fee basis at §390/§588/§602 corrected to net payout, **closing the Aug 27 routing** and deleting the counsel-lane exemption rather than keeping it as a courtesy. New `REQUIRED_TOKENS` gate for copy that quietly goes away, the inverse of a retired token; smoke asserts the same six facts against the served page. Two things caught in the doing: the absence assertions passed **vacuously against an empty body** when the origin died, now guarded; and `gross booking revenue` on `/calculator` is the same-phrase/different-claim trap for the third time, scoped with its reason rather than softening the token. C3 items 2 and 6 stay provisional pending the C4 lawyer review.
- **v3.19** (2026-09-01) — BOARD ADDENDUM C, amending B1: `ad_personalization` **denied for every visitor in every region**, including an Accept in a gated region — remarketing is unusable at test scale, so it buys nothing while straining §03; conversion measurement is unaffected. Hardcoded literal rather than a derived value, since `ad_personalization: ad` reads correct at a glance; two CI gates, negative-controlled three ways, plus a four-region browser test (20/20). `/legal` accuracy adopted as a **gate on first spend**, per Code's recommendation. Counsel lane now has a named ruler (Jason, interim) — the never-edit-unbidden boundary is unchanged. Seven ruled edits drafted as `LEGAL-REDLINE-2026-09-01.md` and awaiting approval; three uncovered items flagged rather than drafted. Lawyer review booked by Sept 12, complete by Sept 30.
- **v3.18** (2026-09-01) — Strategy terminology ruling: Cost Seg Smart is our **cost segregation partner**, never our "tax partner" — their own terms disclaim advisory capacity and the referral agreement obliges us not to hold them out as advisers. One instance estate-wide, in Jason's note on the guest article; the Miami card the brief also names does not exist yet (partner cards still open from v3.11), so the ruling waits for it. Standing rule recorded: a cost segregation study is a **study, never advice**, readers go to their own CPA, and Marketics makes no tax claims. Enforced by a `PARTNER_CAPACITY` gate scoped to the possessive form, so "your own tax advisor" still passes.
- **v3.17** (2026-09-01) — `/legal` routed to counsel a second time (`LEGAL-ROUTING-2026-09-01.md`): the policy names a Meta Pixel that does not exist, omits the Google Ads tag that does, carries a "we do not share with advertisers" sentence in tension with `ad_personalization` granted by default, over-describes Clarity (which runs only on explicit Accept, so only for gated-region visitors — an inversion worth naming), and leaves the working Do Not Sell control and GPC support undisclosed. Reported, not edited. Recommended as a gate on first ad spend, since the remedy is documentation and the cost of fixing it after launch is materially higher. Doc 404-shadowed in both URL forms and asserted in smoke.
- **v3.16** (2026-09-01) — Strategy rulings. Editorial partner placements (`/costseg/intel-article`, `/costseg/author-page`) now land on the Cost Seg Smart homepage rather than `/order/`, as specific `_redirects` lines above the shared `:placement` rule, which is untouched so card behaviour is unchanged; same ref, same four UTMs. Smoke asserts both the new destinations and that a card placement still reaches `/order/`. House style amended: no em dashes in PROSE, the "Title — Marketics" separator exempt as a structural convention, so titles are unchanged estate-wide. The third internal link stays unmanufactured — a cost-seg reference in `/intel/money` and `/intel/what-a-property-manager-actually-costs` is a content gap Strategy will write.
- **v3.15** (2026-08-31) — Strategy live-page brief: ruled meta description applied to `description`, `og:description` and (unnamed but same defect) `twitter:description`; both framing edits applied verbatim. Partner link confirmed intentional with the ref intact, and two unassumed differences reported — it resolves to `/order/` rather than the bare domain and carries four UTMs, both from a `_redirects` rule shared with the partner cards, with a ruling invited on whether an order form is the right landing for an article reader. Per-placement destinations now asserted in smoke against production. Schema verified as Organization/WebPage. Internal-link count reported honestly as short of the brief's bar rather than padded; `/intel/money` has no cost-seg mention to link from. Article claim strings registered by owner. `og:title`/`twitter:title` em dashes left as a site-wide style question.
- **v3.14** (2026-08-31) — corrects v3.12: the Ads destination is scoped to `/lp/keep-control` rather than every page. Configured site-wide it cost `/calculator` ~1,850ms of mobile LCP (0.68 vs the 0.80 floor, 6549ms vs the 5200ms budget) and failed CI. Local runs could not have caught it — this sandbox blocks googletagmanager.com, so they were scoring a page with no tag on it. The LP is the whole paid path (no-exit rule) and the only page a conversion can occur on, so the scope is correct on the merits, not just cheap. GA4 unchanged everywhere.
- **v3.13** (2026-08-31) — paid conversion event named `generate_lead_paid` by Strategy, replacing the `lp_audit_lead` placeholder v3.8 recorded pending the name. Board ruling 4 (paid and organic never share a counter) promoted from a source comment to a hard CI gate that compares the LP's event against every event the rest of the site fires; negative-controlled three ways. Sequencing noted for the Ads import: GA4 will not offer an event as a key event until it has fired at least once.
- **v3.12** (2026-08-31) — Google Ads `AW-18418837499` added as a second destination on the existing gtag.js load in `mkx-consent.js`, after the region-aware grant, so it inherits the consent gate rather than being pasted into 53 `<head>`s ahead of it. Google's page-view conversion snippet deliberately NOT installed: it scores every pageview as a $1 conversion, points Smart Bidding at pageviews instead of leads, and contradicts A2, which named `lp_audit_lead`. A lead conversion action in Ads is Jason's to create; nothing is wired to the page-view label. Both rules are CI guards, negative-controlled against Google's own snippets.
- **v3.11** (2026-08-31) — first guest byline: pen-name rule recorded and enforced structurally. Name + firm always paired, disclosure line verbatim on the author page and the article foot, author page limited to five elements with no photo/bio/credentials/socials, Article `author` as Organization rather than Person, author page `WebPage` only with no `sameAs`. Strategy's draft called the pen name "founder of Cost Seg Smart" in two places; Code stopped rather than swap it and Jason ruled the title out. `/partners` and the Miami partner card deferred, so two of the brief's items are open.
- **v3.10** (2026-08-30) — Addendum B, superseding A3: advertising signals granted by default outside the gated regions, with a "Do Not Sell or Share" control and GPC as the opt-out; Canada joins the banner gate; new banner copy grants all four families on Accept and nothing on Decline. Implemented in one file rather than 51 inline stubs — gtag.js is injected on idle, so the stubs' deny-advertising default stays as the fail-safe. Chat widget cut from 34 pages to one, page-restricted and consent-gated, with a CI guard. `/audit-request` retired as a path that never existed.
- **v3.9** (2026-08-30) — board addendum A: turnaround canon unified to "48 hours or less" across 24 instances with two same-phrase/different-claim hits deliberately excluded (`/pricing` payout, `/join` contract); scoped CI guard rather than a blanket token; `lp_audit_lead` recorded as the paid-only conversion event; `/lp/keep-control` added to Lighthouse CI at the homepage bar. Corrects v3.8's turnaround table. A3 held pending the what-actually-fires inventory — `/legal` describes a Meta Pixel that does not exist.
- **v3.8** (2026-08-30) — inline audit form shipped on `/lp/keep-control` per the board memo; `pricing_owner` select, distinct paid conversion event, honeypot, UTM + hidden-source plumbing to the same GHL pipeline as `/get-started`. Paid-LP no-exit rule and retired-contrast-token guards added to CI — the first caught a masthead logo link Code shipped on Aug 27, now corrected along with the missing wordmark. Turnaround-time divergence (24h / 48h / 2–3 business days) recorded as an open canon question.
- **v3.7** (2026-08-27) — PM cost 20–35% confirmed standard (closes ledger flag #4); 45%-provenance check closed by Jason's ruling, unblocking the LP sequencing gate; `/legal` fee contradiction routed to counsel with a prepared brief.
- **v3.6** (2026-08-27) — fee-phrasing ruling RATIFIED (Jason); canonical fee sentence applied estate-wide, growth-contingent variants retired across homepage/`/pricing`/12 intel pages, comparison table re-strung as a pair; survivor sweep run with every hit reviewed individually. LP fine-print footer added as the sole sanctioned no-exit exception; `/legal` confirmed to carry an adequate privacy policy, so the ad-launch gate is met.
- **v3.5** (2026-08-27) — `/lp/keep-control` rebuilt from copy v3.1 to ship brief Rev C; v1/v2/v3 superseded; LP claim strings registered; two ruled LP-only exceptions (methodology pointer plain text, press mark unlinked); PM-cost and Airbnb-fee ledger entries written; FAQ pair check added to CI.
- **v3.4** (2026-08-27) — fee basis corrected to **net payout** across 19 marketing surfaces (was "10% of revenue", a different basis than the signed Co-Host Agreement); `/legal`'s internal gross-vs-net contradiction reported to counsel, not edited. Press mark switched to the outlet's own reversed lockup from one shared asset, superseding v3.3's monochrome rule — recolouring a third party's trademark is the bigger risk.
- **v3.3** (2026-08-26) — CNBC Make It press citation: "Quoted by" bar (homepage + `/lp/keep-control`) and `/media` Press section. Claim strings, accessible-name string and treatment rules registered; "trusted by"/"as seen on"/endorsement framings retired before first use. Mark inlined with `fill="currentColor"`, which makes the never-full-colour/never-gold rule structural rather than remembered.
- **v3.2** (2026-08-26) — Clutch listing live and claimed; wired into Organization `sameAs`, closing the last open v2.8 entity-graph gap. Liveness/identity confirmed by Jason (egress blocked `clutch.co`, no CI path for third-party pages). Rule recorded: `sameAs` additions require positive identity confirmation, given the same-name Bangalore firm.
- **v3.1** (2026-08-25) — canon sweep: verdict *cache artifact* (repo clean, deploy current, live clean). No copy changed. Closed two enforcement gaps: five brief-named retired claims were ungated in CI; live canon check covered four phrasings on one page, now the full pattern set across 17 surfaces. Findings: `CANON-SWEEP-2026-08-25.md`.
- **v3.0** (2026-08-21) — BOARD RULING: Consent Mode v2 + EEA/UK/CH region gating; gtag.js now loads on every path (cookieless pings for denied traffic). `ad_*` denied everywhere pending banner-copy change — flagged as a live constraint on the paid launch.
- **v2.9** (2026-08-21) — BOARD RULING: window reverted to 2019–2026; PR #95's narrowing to 2024–2026 was an unverified assumption. Verified the 45% median was never recomputed on the narrowed set (figures byte-identical since the Index page was created). `2024–2026` added to RETIRED_TOKENS.
- **v2.8** (2026-08-21) — sample-window provenance recorded (PR #95, Code-side correction, no dataset in-repo to independently re-verify); entity graph / sameAs wiring for Organization + founder Person, disambiguation identity string added.
- **v2.7** (2026-07-2x) — same-breath baseline rule made explicit; market-tier correction (retired "3/22 active markets" framings); footer tagline 45%-clause dropped site-wide; Item 1 calculator baseline finding recorded; this registry created.
- **Pre-v2.7** — tracked informally across PR descriptions and the July 4 audit doc (`marketics-site-audit-2026-07.md`); no single versioned file existed. This registry is the first consolidated version.
