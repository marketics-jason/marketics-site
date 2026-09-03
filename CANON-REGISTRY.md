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

So the fix was wiring, not archaeology. The old owner still has not been identified, and no longer
needs to be.

### The paid path now has its own entry point

`/lp/keep-control` posts to `2ebb4312-…`, generated by Jason in the trigger panel. The organic hook
is untouched and still serves the other 29 surfaces.

Beyond ending the ambiguity, this matters for bidding: the paid path is the only one that fires a
conversion Smart Bidding learns from, and it should not share an entry point with 29 organic
surfaces and a cookie banner.

**Gated in both directions.** The LP must carry the paid hook and must not carry the shared one;
no other file may carry the paid hook, since a second caller would put organic traffic into the
paid conversion workflow. Negative-controlled both ways. The gate holds trigger **ids**, not full
URLs — they are already public in every visitor's page source, but a grep of the validator should
not hand anyone a ready-to-POST endpoint.

### Flagged to the CTO, not fixed here

The swap moves contact creation. Today the legacy workflow on the shared hook creates the contact;
after the swap nothing on that path does, so the paid workflow must create it itself. An Inbound
Webhook trigger does not create a contact on its own — that is an action, and it was not in the
wiring plan. Named before the swap rather than discovered after it.



- **v3.22** (2026-09-03) — the paid LP gets its **own** inbound-webhook trigger (`2ebb4312-…`), separating it from the shared organic hook that 29 files use, the consent beacon included. Sharing it meant the paid workflow could only distinguish itself by filtering on `source`, and a filter that silently stops matching is indistinguishable from a broken deploy — two hours were lost hunting for a serverless Function that has never existed here (every GHL call on this site is a browser fetch to an inbound webhook, so the site cannot map a field or apply a tag at all). Contacts were being created by whatever legacy workflow owns the shared hook while the new paid workflow showed 0 executions, never having been pointed at. Fix was wiring, not archaeology; the old owner is still unidentified and no longer needs to be. Gated both directions — the LP must carry the paid hook and not the shared one, and no other file may carry the paid hook — negative-controlled both ways, with ids rather than full URLs in the validator. Flagged and not fixed here: after the swap nothing creates the contact unless the paid workflow does it itself.
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
