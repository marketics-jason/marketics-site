#!/usr/bin/env python3
"""
count-lead-events.py — turn /api/lead's function log into the numbers CTO asked for.

WHY A SCRIPT AND NOT AN EYEBALL (CTO deliverables 3 and 4, registry v3.56).

The counter is LOG-BASED BY RULING: no durable store, no Netlify Blobs, no
package.json, no dependency. The trade was made explicitly -- the repo's
no-build-step property is worth more than a persisted integer, and a structured
line per event is already a denominator that consent cannot gate away and that
GA4 cannot undercount.

What a log-based counter needs to stay honest is a MECHANICAL reader. Counting
by scrolling is how "we think it's about half" becomes a number in a board
paper. This reads the same lines the function emits and prints counts, so the
denominator is reproducible rather than remembered.

WHAT IT CANNOT DO, said plainly so the output is never over-read:
  * Netlify's function log RETENTION IS FINITE. This counts what is in the
    window you exported, not all of history. A window with no start date is a
    number with no denominator of its own.
  * It cannot deduplicate a visitor. `impression` counts banners shown, not
    people. That is the correct denominator for a consent rate and the wrong
    one for reach.
  * `ignore` is inferred from a pagehide beacon. A browser that kills the tab
    without firing pagehide is an undercount on that row ONLY -- it never
    inflates accept or deny.

Usage:
  netlify logs:function lead > lead.log     # or paste from the Netlify UI
  python3 scripts/count-lead-events.py lead.log
  cat lead.log | python3 scripts/count-lead-events.py
"""
import json, sys, collections

CONSENT_ACTIONS = ("impression", "accept", "deny", "ignore")


def parse(stream):
    """Every JSON object on a line, ignoring Netlify's own log furniture."""
    for line in stream:
        i = line.find("{")
        if i < 0:
            continue
        try:
            obj = json.loads(line[i:].strip())
        except ValueError:
            continue
        if isinstance(obj, dict) and "evt" in obj:
            yield obj


def main():
    src = open(sys.argv[1], encoding="utf-8") if len(sys.argv) > 1 else sys.stdin
    events = list(parse(src))
    if not events:
        print("no /api/lead events found in that input — nothing to count.\n"
              "(An empty count is reported, never printed as zeros: zeros would "
              "read as 'no traffic' when the truth is 'no data'.)")
        return 2

    leads = [e for e in events if e.get("evt") == "lead_forwarded"]
    consent = [e for e in events if e.get("evt") == "consent_event"]
    rejected = [e for e in events if e.get("evt") in ("lead_rejected", "consent_rejected")]
    misconfig = [e for e in events if e.get("evt") == "lead_misconfigured"]

    stamps = sorted(e["ts"] for e in events if e.get("ts"))
    window = f"{stamps[0]} → {stamps[-1]}" if stamps else "unknown"
    print(f"\nWindow: {window}   ({len(events)} event line(s))")

    print("\n── Leads forwarded (deliverable 3) " + "─" * 38)
    by_route = collections.Counter(e.get("route", "?") for e in leads)
    ok_n = sum(1 for e in leads if e.get("ok"))
    for route, n in sorted(by_route.items()):
        r_ok = sum(1 for e in leads if e.get("route") == route and e.get("ok"))
        print(f"  {route:<18} {n:>5}   ({r_ok} reached GHL, {n - r_ok} did not)")
    print(f"  {'TOTAL':<18} {len(leads):>5}   ({ok_n} reached GHL, {len(leads) - ok_n} did not)")
    print("  Cross-check this total against the GHL contact count for the same window.")

    empties = sum(e.get("emptyKeys", 0) for e in leads)
    if empties:
        print(f"\n  ⚠  {empties} EMPTY KEY(S) arrived from the browser across "
              f"{sum(1 for e in leads if e.get('emptyKeys'))} submission(s).")
        print("     The v3.51 filter is upstream of this. A non-zero number here means "
              "it regressed —\n     GHL would write those blanks over populated fields "
              "and report success.")
    else:
        print("  Empty keys arriving from the browser: 0 (the v3.51 filter is holding).")

    print("\n── Consent denominator (deliverable 4) " + "─" * 34)
    if not consent:
        print("  No consent events in this window — NOT the same as 'nobody saw a banner'.")
    else:
        counts = collections.Counter(e.get("action") for e in consent)
        shown = counts.get("impression", 0)
        for a in CONSENT_ACTIONS:
            n = counts.get(a, 0)
            pct = f"{100.0 * n / shown:5.1f}%" if shown and a != "impression" else "     "
            print(f"  {a:<12} {n:>5}  {pct}")
        answered = counts.get("accept", 0) + counts.get("deny", 0)
        if shown:
            print(f"\n  Answered: {answered} of {shown} banners ({100.0 * answered / shown:.1f}%).")
            if counts.get("accept", 0) + counts.get("deny", 0) > shown:
                print("  ⚠  More decisions than impressions — the counts are not "
                      "from one consistent window.")
        else:
            print("\n  Decisions recorded with no impressions — the window is partial; "
                  "rates would be wrong.")

    if rejected or misconfig:
        print("\n── Rejected / misconfigured " + "─" * 45)
        for kind, n in collections.Counter(
                (e.get("evt"), e.get("reason", e.get("envName", "—"))) for e in rejected + misconfig).items():
            print(f"  {kind[0]:<20} {kind[1]:<18} {n:>5}")
        if misconfig:
            print("  ⚠  A misconfigured line means a hook env var was missing and a "
                  "REAL LEAD WAS REFUSED.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
