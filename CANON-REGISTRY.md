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

## Version history

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
