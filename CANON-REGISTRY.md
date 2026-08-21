# Marketics Claims Canon Registry

**Version:** v2.8 · **Maintained by:** Code, on ruling from CTO/Strategy · **Public visibility:** internal only — force-shadowed to 404 in `_redirects` (see bottom of that file), same pattern as `marketics-site-audit-2026-07.md`.

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
> "1,000+ listings optimized across 22 markets over the past decade; the 45% median comes from the 19 engagements with complete before/after documentation (2024–2026)."

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

## v2.8 — sample-window provenance + entity graph (2026-08-21, Boardroom pre-flight cycle)

**Sample-window provenance, recorded per the Aug 17 brief's request.** The documented window is **2024–2026**, sample **19 documented engagements**. This was corrected from an earlier **2019–2026** label in **PR #95** (2026-07-25, "Claims accuracy: machine-layer conflation, WebSite entity, sample window, Trustpilot") — that PR's own commit message states the reasoning: *"the 19 documented engagements span 2024–2026; the 2019–2026 label was wrong and would fold in COVID-era demand years."* This was a **Code-side factual correction**, not a recorded Boardroom ruling at the time — no prior changelog entry existed until this one. **Open gap:** no raw per-engagement dataset (dates, individual records) is checked into this repo — only the aggregate stat, repeated consistently across pages and schema. This registry's confirmation rests on PR #95's determination; independent re-verification against source records (spreadsheet/CRM) has not been done in-repo and would need to happen off-platform.

**Confirmed consistent as of this cycle:** rendered copy and `Dataset` schema on `/intel/str-performance-index`, the `/intel` hub description, and `llms.txt` all read 2024–2026 / 19 engagements with no drift found.

**Entity graph / sameAs wiring (Task 1, Aug 17 brief).** Organization `sameAs` on the canonical entity (`index.html`, mirrored in `results/index.html`'s description) now includes LinkedIn company page, Crunchbase, Trustpilot, YouTube, and Google Business Profile (confirmed live by Jason, 2026-08-21). Founder Person entity (`story/index.html#jason`, the canonical definition — other pages reference it by `@id`) now includes Jason's LinkedIn, personal site (jasonbaxter.ca), and Instagram. Added `legalName: "Marketics, LLC"` and `foundingDate: "2023"` to the Organization entity, and led the canonical description with the identity string `"Marketics, LLC (marketics.io)"` for disambiguation against the unrelated Bangalore analytics firm of the same brand name (acquired by WNS, 2007). **Gap, not fixed:** Clutch listing is under review with Clutch as of this cycle — not yet claimed/live, so not wired; revisit once live.

---

## Version history

- **v2.8** (2026-08-21) — sample-window provenance recorded (PR #95, Code-side correction, no dataset in-repo to independently re-verify); entity graph / sameAs wiring for Organization + founder Person, disambiguation identity string added.
- **v2.7** (2026-07-2x) — same-breath baseline rule made explicit; market-tier correction (retired "3/22 active markets" framings); footer tagline 45%-clause dropped site-wide; Item 1 calculator baseline finding recorded; this registry created.
- **Pre-v2.7** — tracked informally across PR descriptions and the July 4 audit doc (`marketics-site-audit-2026-07.md`); no single versioned file existed. This registry is the first consolidated version.
