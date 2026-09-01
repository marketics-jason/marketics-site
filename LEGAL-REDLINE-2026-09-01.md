# `/legal` REDLINE — Board Addendum C3, seven ruled edits
**Prepared by:** Code · **Date:** 2026-09-01
**Status: APPROVED by Jason 2026-09-01 and APPLIED.** All seven edits are in `legal/index.html`,
plus all three flagged items, which Jason approved in the same ruling. This document is kept as
the record of what was approved — the text below is what shipped, not a proposal.
**Authority:** Board Addendum C, Sept 1 2026. C2 names Jason as the interim counsel lane;
C3 rules the seven edits below. C3's sequence was **redline → Jason approves → Code ships**, and
that is the order it ran in.
**Public visibility:** internal only — force-shadowed to 404 in `_redirects`.

**How the three flagged items were resolved** (all three approved):
- **A — §06 Clarity contradiction:** the analytics-cookie line now says *"Clarity's cookies are
  set only for visitors who have accepted them, as described in Section 4.1."*
- **B — GA4 "IP anonymization is enabled":** replaced with *"Google Analytics 4 does not store
  IP addresses."*
- **C — §03 notice block:** the notice keeps only *"We do not sell your personal data to third
  parties."* The Google Ads explanation sits in ordinary body text immediately below it, so the
  flat commitment keeps its visual weight. Verified in a browser.

---

## How to read this

Every edit shows the **exact current text** and the **exact proposed text**. Nothing is
paraphrased, because the point of a redline is that the thing you approve is the thing that
ships. Line numbers are from `legal/index.html` as of `87c1a0c`.

Three items at the end are **flagged, not drafted** — they are things the ruling does not cover
that a reader of the amended document would notice. They need a yes or no from you before I ship,
and none of them blocks the seven.

Nothing in this file has been applied to `/legal`. The document on production is unchanged.

---

## Edit 1 — §04.1: add Google Ads · *ruling: fact*

**Insert** as a new list item immediately after the Google Analytics 4 entry (line 369):

> **Google Ads:** Conversion measurement for our paid advertising. When you arrive from a
> Google ad and submit an audit request, a conversion event is recorded so we can measure which
> campaigns produce enquiries. Cookies are set for this measurement on our advertising landing
> page. We do not enable advertising personalization or build remarketing audiences.
> [Google Privacy Policy]

Follows the vendor-entry shape already used in §04.1: bold vendor name, what it does, what data
it receives, an external policy link.

The last sentence is a factual statement about the configuration, not a promise about intent —
it is true because `ad_personalization` is denied for every visitor in code, and CI now fails
if that changes (Addendum C1, shipped alongside this).

## Edit 2 — §03: qualify the advertiser sentence · *ruling: characterisation, provisional*

**Current** (line 354, inside the `.notice` block):

> **We do not sell your personal data to third parties.** We do not share your personal data
> with advertisers for the purpose of serving you ads on other platforms.

**Proposed:**

> **We do not sell your personal data to third parties.** When you arrive from one of our
> advertisements, we share conversion data with Google Ads so we can measure which campaigns
> are effective. We do not build advertising audiences from visitor data, and we do not enable
> advertising personalization.

First sentence kept verbatim, per the ruling. The replacement states what is shared, with whom,
and why, and then makes the narrower claim the configuration actually supports.

**This is the one C4 confirms.** It is a legal characterisation and I am not in a position to
warrant the wording — I have drafted it to be accurate about the mechanism and left the
judgement to the lawyer review.

## Edit 3 — §04.1 and §06: remove both Meta Pixel passages · *ruling: fact*

**Delete** from §04.1 (line 370), entire list item:

> **Meta Pixel (Facebook):** Advertising and conversion tracking. We use this to measure the
> effectiveness of advertising campaigns. [Meta Privacy Policy]

**Replace** in §06 (line 405), the Marketing cookies item:

> **Marketing cookies:** Meta Pixel uses cookies to measure advertising campaign effectiveness
> and support retargeting.

with:

> **Marketing cookies:** Google Ads sets cookies on our advertising landing page to measure
> conversions from our paid campaigns. These cookies are not used for personalization or
> retargeting.

The §06 item is rewritten rather than deleted because the category still exists — it just has a
different, real occupant. Deleting it outright would leave §06 silent about the only marketing
cookie the site actually sets, which is the gap that started this.

## Edit 4 — §04.1: correct Microsoft Clarity · *ruling: fact*

**Current** (line 371):

> **Microsoft Clarity:** Session recording and heatmap analytics. Microsoft may use data
> collected through Clarity to improve its products and services. [Microsoft Privacy Statement]

**Proposed:**

> **Microsoft Clarity:** Session recording and heatmap analytics. Clarity runs only for
> visitors in the EEA, the United Kingdom, Switzerland and Canada who have explicitly accepted
> cookies through our consent banner. It does not run for any other visitor. Microsoft may use
> data collected through Clarity to improve its products and services.
> [Microsoft Privacy Statement]

## Edit 5 — §08: describe the Do Not Sell control and GPC · *ruling: fact*

**Current** (line 439, California Residents):

> …the right to opt out of the sale or sharing of personal information (we do not sell personal
> data), and the right to non-discrimination for exercising these rights. To exercise your CCPA
> rights, contact us at privacy@marketics.io.

**Proposed** — same sentence up to "these rights", then:

> …and the right to non-discrimination for exercising these rights. A **"Do Not Sell or Share My
> Personal Information"** control is available in the footer of every page on this Site; using it
> turns off advertising-related data collection for your browser and your choice is remembered on
> return visits. We also honour the **Global Privacy Control (GPC)** signal automatically — if
> your browser sends it, advertising signals are turned off without you having to do anything.
> For any other CCPA request, contact us at privacy@marketics.io.

The email address is kept as the fallback, per the ruling. The mechanism is described first
because it is the thing a resident can act on immediately.

## Edit 6 — header: effective date · *ruling: procedure*

**Current** (lines 285 and 509, both tabs):

> Effective Date: **March 17, 2026** · Last Updated: **March 17, 2026**

**Proposed** — ship date in both fields, both tabs:

> Effective Date: **[ship date]** · Last Updated: **[ship date]**

Filled with the actual merge date at ship time rather than guessed here.

**One observation, not an objection.** §12 of the policy says *"we will update the 'Last Updated'
date"* — it describes updating that field, not the Effective Date. Moving both is the more
conservative reading and it is what C3 says, so that is what I have drafted. If C4 prefers
"Effective Date" to stay at original publication with only "Last Updated" moving, it is a
one-line change. **Both tabs move**, because Edit 7 changes the Terms half too.

## Edit 7 — fee basis: net payout · *ruling: fact, already ruled Aug 27*

Three lines. §601 already says net payout and is the one they are being made to match.

**Line 390** (Privacy tab, §05 Platform Account Access):

> Configure the payout split mechanism so that Marketics receives **10% of booking revenue**
> directly from the platform at the time of payout

→

> Configure the payout split mechanism so that Marketics receives **10% of the net payout**
> directly from the platform at the time of payout

**Line 588** (Terms, §5.2 Payout Configuration):

> …to direct **10% of gross booking revenue per booking** to Marketics' designated co-host
> payout account.

→

> …to direct **10% of the net payout per booking** to Marketics' designated co-host payout
> account.

**Line 602** (Terms, §6):

> The Service Fee is calculated on **gross booking revenue before platform service fees, taxes,
> or other deductions by the booking platform.** The Service Fee is earned by Marketics at the
> time of guest check-in…

→

> The Service Fee is calculated on **the net payout — the amount the booking platform deposits
> after its own service fees and platform-remitted taxes.** The Service Fee is earned by
> Marketics at the time of guest check-in…

Line 602 is the substantive one: it currently states the **opposite** basis to §601 four lines
above it, and gross-vs-net on a booking is a real money difference. This matches the Co-Host
Agreement (`/join` §2) and the canonical sentence ratified in registry v3.6.

---

## Flagged, not drafted — three things the ruling does not cover

I have not written these into the redline. Each needs a yes or no.

**A. §06 still implies Clarity sets cookies for everyone.** Edit 4 corrects §04.1, which is what
C3 item 4 names. But §06's analytics-cookie line reads:

> **Analytics cookies:** Google Analytics 4 and Microsoft Clarity use cookies to collect usage
> statistics.

After Edit 4 the document says in one section that Clarity runs only on explicit consent in four
jurisdictions, and in another that it sets cookies as a general matter. **Proposed, if you say
yes:** append *"Clarity's cookies are set only for visitors who have accepted them, as described
in Section 4.1."* One sentence, same fact as Edit 4, no new claim.

**B. §04.1 says GA4 has "IP anonymization is enabled".** GA4 has no such setting — it is
Universal Analytics language. GA4 does not log or store IP addresses in the first place, so the
sentence understates rather than overstates, but it describes a control that does not exist.
Not ruled, and not mine to characterise. **Proposed, if you say yes:** *"Google Analytics 4 does
not store IP addresses."* Otherwise it goes to C4 as an observation.

**C. §03's heading context.** Edit 2 changes a sentence inside a highlighted `.notice` block
whose visual weight reads as a promise. The replacement is longer and more qualified than what
it replaces, which is correct but changes the block's tone from a flat commitment to an
explanation. If you would rather the notice carry only the sell sentence and the Google Ads
explanation sit in ordinary body text below it, say so — it is a formatting choice with no
effect on the words.

---

## What ships with the edits, once approved

1. **The seven edits**, exactly as approved.
2. **Claim sweep extended to `/legal`** (C3's own instruction): `Meta Pixel` and
   `gross booking revenue` become retired tokens, `Google Ads` becomes a required token. The
   counsel-lane exemption that currently lets `/legal` carry the retired fee strings is removed
   in the same commit — it exists only because the document could not be edited.
3. **Registry v3.20**, recording the ruling, the date, and that Jason approved the wording.

Both `/legal` routing docs close on this shipping, except C3 item 2 and item 6, which stay open
until C4.

## What has already shipped

**C1** — `ad_personalization` denied for every visitor in every region, including an Accept in
a gated region. It is a hardcoded literal in `mkx-consent.js` with two CI gates and a
four-region browser test. That had to land first: Edits 1 and 2 both assert it as fact, and a
policy sentence should not describe a configuration that is not yet true.
