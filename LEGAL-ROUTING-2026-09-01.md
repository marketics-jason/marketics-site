# COUNSEL ROUTING — `/legal` describes tracking the site does not do, and omits tracking it does

**Raised by:** Code · **Date:** 2026-09-01 · **Status:** open, awaiting counsel
**Public visibility:** internal only — force-shadowed to 404 in `_redirects`.
**Nature:** factual mismatch between a live public privacy policy and the site's actual behaviour.
Not a drafting-style note.
**Recommended sequencing:** before paid advertising spend begins. See *Why the timing matters*.

---

## The issue in one line

`marketics.io/legal` was last updated **March 17, 2026**. Since then the site's tracking has
changed substantially. The policy now **names a vendor that is not present, omits one that is,
and makes one statement that the current configuration puts under strain.**

## What the policy says

| Where | What it says |
|---|---|
| §04.1 Service Providers | "**Meta Pixel (Facebook):** Advertising and conversion tracking. We use this to measure the effectiveness of advertising campaigns." |
| §06 Cookies | "**Marketing cookies:** Meta Pixel uses cookies to measure advertising campaign effectiveness and support retargeting." |
| §03 (closing lines) | "We do not sell your personal data to third parties. **We do not share your personal data with advertisers for the purpose of serving you ads on other platforms.**" |
| §04.1 Service Providers | "**Microsoft Clarity:** Session recording and heatmap analytics." |
| §08 Your Rights → California | CCPA rights described; requests directed to `privacy@marketics.io`. |

## What the site actually does

Each row below is verified against the running site by an automated browser suite, not read off
the source. Region behaviour is exercised by loading the pages under EEA, Canadian and US
timezones.

| Finding | Status |
|---|---|
| **Meta Pixel** | **Not present anywhere.** Zero occurrences in the repository or on any served page. It is described in two places and does not exist. |
| **Google Ads** (`AW-18418837499`) | **Live since 2026-08-31**, on `/lp/keep-control` only. **Named nowhere in the policy** — not in §04.1's vendor list, not in §06's cookie categories. |
| **Advertising consent signals** | For visitors outside the EEA/UK/CH and Canada — which is the great majority, and all paid traffic — `ad_storage`, `ad_user_data` and **`ad_personalization` are all granted by default**, without a banner, per the Board's Addendum B ruling of 2026-08-30. |
| **Microsoft Clarity** | Loads **only after an explicit Accept**, and the consent banner is only shown in the EEA/UK/CH and Canada. A US visitor is never asked and therefore never accepts, so **session recording never runs for them.** The policy describes Clarity as a general vendor. |
| **"Do Not Sell or Share My Personal Information"** | A working control **exists in the footer of every page** and the site honours the browser's Global Privacy Control signal. **Neither is mentioned in §08 or anywhere else in the policy.** |

## The four issues, in the order Code would rank them

**1. Google Ads is undisclosed while advertising personalisation is on by default.**
The policy's §04.1 and §06 are the two places a reader looks to learn which third parties receive
their data and which cookies are set. Google Ads is in neither, while `ad_personalization:
granted` is the live default for most visitors. This is the gap that closes least comfortably
after spend starts.

**2. §03's advertiser statement is in tension with the configuration.**
"We do not share your personal data with advertisers for the purpose of serving you ads on other
platforms" was written when nothing advertising-related was running. With Google Ads live and
`ad_personalization` granted, conversion and audience signals do reach Google. Whether that
sentence remains accurate is a legal characterisation question, not one Code can answer — but it
is the sentence most likely to be read closely, and it is the reason this brief exists rather
than a ticket.

**3. Meta Pixel is described twice and does not exist.**
Harmless in effect, but it is a statement of fact in a legal document that is not true, and it
sits three lines from the passages that matter. It also makes the policy look un-maintained,
which is a poor posture for the two issues above.

**4. Clarity is over-described, and the direction is worth noting.**
Session recording is disclosed generally but only occurs for visitors in the EEA, UK, Switzerland
and Canada who actively opted in. The practical result is an inversion: **the only people
recorded are those in the most privacy-protective jurisdictions, and they are the only ones who
were asked.** The behaviour is defensible; the disclosure simply describes more collection than
happens.

**And one thing the policy under-claims.** The Do Not Sell control and GPC support both exist and
work, and the policy mentions neither. Counsel may want §08 to describe the mechanism a California
resident is actually offered, rather than directing them only to an email address.

## Why the timing matters

The Board's remaining pre-spend gates are commercial and technical. This one is not, and it is
the only open item where the cost of fixing it **after** launch is materially higher than before:

- The fix is documentation, not engineering. It is fast.
- Once campaigns run, the window in which the policy was inaccurate becomes a period with ad
  spend, conversion data and identifiable traffic attached to it, rather than a quiet gap.
- Ad platform policies require the destination's privacy disclosures to describe the data
  practices in use. A policy that omits the ad platform being used is the specific thing those
  terms are about.

Code's recommendation, offered as sequencing rather than legal advice: **treat this as a gate on
first spend.** The campaigns are otherwise ready and nothing else is waiting on it.

## What the site does well, so counsel has the full picture

The behaviour is defensible; it is the disclosure that has drifted. For completeness:

- Consent Mode v2 with region gating — advertising and analytics storage **denied by default**
  in the EEA, UK, Switzerland and Canada until an explicit Accept.
- A functioning "Do Not Sell or Share" control on every page, persisted across visits.
- Global Privacy Control honoured — a visitor signalling GPC has advertising signals denied
  without taking any action.
- `gtag.js` loads once, after the consent decision is made, and Google Ads is scoped to the single
  paid landing page rather than the whole site.
- All of the above is enforced by automated tests that fail the build if it regresses.

## What Code did and did not do

- **Did not edit `/legal`.** Standing rule: counsel lane. Code reports rather than edits,
  regardless of how mechanical the fix looks. That rule held here even though items 3 and 4 are
  plainly just wrong.
- **Did not soften the finding.** Item 2 is raised as a tension rather than a violation because
  Code is not in a position to characterise it, not because it is minor.
- **Did add the surrounding facts** rather than only the problem, so counsel can see that the
  configuration is careful and the gap is in the description of it.

## What counsel needs to decide

1. **Add Google Ads to §04.1 and §06**, describing conversion tracking and the advertising cookies
   set — and confirm what the entry should say given `ad_personalization` is granted by default
   outside the gated regions.
2. **Rule on §03's advertiser sentence.** Does it survive as written, need qualifying, or need
   removing? This is the one Code flagged as a characterisation question rather than a fact.
3. **Remove the two Meta Pixel passages**, or confirm a Pixel is intended and Code should be
   told to build one.
4. **Correct or qualify the Clarity description** to reflect that it runs only on explicit
   consent.
5. **Consider whether §08 should describe the Do Not Sell control and GPC support**, which exist
   and work but are undisclosed.
6. **Confirm whether the update needs an effective-date change or user notice**, given the policy
   has described the wrong vendor set since Google Ads went live on 2026-08-31.

**Point 6 is the one Code cannot assess**, and is flagged for the same reason as point 3 in the
August 27 routing: it depends on obligations and on facts outside the repository.

## Contact

Privacy/policy questions: counsel, via Jason. Tracking configuration questions: CTO. Ad account
and campaign questions: Jason. This document and the underlying verification: Code.

Related: `LEGAL-ROUTING-2026-08-27.md` — the open fee-basis conflict in the same document. If
counsel is amending `/legal` anyway, both should be resolved in one pass.

Registry entries covering the tracking described here: `CANON-REGISTRY.md` v3.0 (Consent Mode),
v3.10 (Addendum B — advertising signals, Do Not Sell, GPC, Canada), v3.12 (Google Ads),
v3.14 (Ads scoped to the paid page).
