#!/usr/bin/env python3
"""
check-skill-sync.py — the enforcement layer for CANON-REGISTRY.md -> marketics-canon skill.

WHY THIS EXISTS (CTO ruling, 2026-09-10, registry v3.47).

The `marketics-canon` skill declares itself the canonical claims home and states it
wins where it conflicts with other sources. Its own Rule 16 requires rulings to be
written back the same session. For v3.41 (tenure) that did not happen, so for three
days the skill and the registry disagreed WITH THE STALE ONE HOLDING PRECEDENCE, and
any lane loading the skill received pre-ruling guidance with no way to detect it.

That is not a vacuous pass -- the check did not lie. It is the sibling class:
an OUTRANKED-OR-LOOSENED CONTROL. A vacuous-pass audit asks "can this check fail?"
This class needs the second question: "does this check still decide anything?"

WHAT IT CHECKS

  A. Every registry version entry at or after v3.47 carries an explicit
     `**Skill impact:** yes|no` line. Pre-v3.47 entries are grandfathered --
     retrofitting 46 of them would be busywork, and the field only has to bind
     going forward to do its job.

  B. If the skill file is reachable, its `Build: ... aligned to CANON-REGISTRY.md
     vX.Y` line is compared against the registry. Any entry NEWER than the skill's
     aligned version that declares `Skill impact: yes` is an unwritten-back ruling,
     and fails.

THE VACUITY TRAP, AND HOW IT IS AVOIDED

The skill lives outside this repo (~/.claude/skills/...), so in CI it is absent.
The obvious implementation skips silently when the file is missing -- which would
make this checker a member of the very family it exists to police. So a missing
skill is reported as NOT VERIFIED and check B is explicitly recorded as not run.
Check A still binds everywhere, including CI, because it reads only the registry.

Usage:
  python3 scripts/check-skill-sync.py [--skill PATH] [--require-skill]

  --require-skill  turn "skill not reachable" into a failure. For use where the
                   skill IS expected to be present (a session, Jason's machine).
"""
import argparse, glob, os, re, sys

REGISTRY = "CANON-REGISTRY.md"
FIELD_FROM = (3, 47)          # first version required to carry the field
DEFAULT_SKILL_GLOBS = [
    os.path.expanduser("~/.claude/skills/**/marketics-canon/SKILL.md"),
    "/root/.claude/skills/**/marketics-canon/SKILL.md",
]


def vparse(s):
    m = re.match(r"v?(\d+)\.(\d+)$", s.strip())
    return (int(m.group(1)), int(m.group(2))) if m else None


def registry_entries(text):
    """[(version_tuple, version_string, section_body)] for every '## vX.Y' heading."""
    heads = list(re.finditer(r"^## (v\d+\.\d+)\b(.*)$", text, re.M))
    out = []
    for i, h in enumerate(heads):
        body = text[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        v = vparse(h.group(1))
        if v:
            out.append((v, h.group(1), body))
    return out


def skill_impact(body):
    """The declared value, or None. ANCHORED and limited to the entry's opening
    lines -- see the note in check A: an unanchored search matches the phrase
    inside prose that merely DESCRIBES the field, which made the first draft of
    this checker satisfy itself with its own explanatory text. Both checks call
    this so they cannot disagree about what counts as a declaration."""
    head = "\n".join(body.strip("\n").split("\n")[:4])
    m = re.search(r"^\*\*Skill impact:\*\*\s*(yes|no)\b", head, re.I | re.M)
    return m.group(1).lower() if m else None


def find_skill(explicit):
    if explicit:
        return explicit if os.path.isfile(explicit) else None
    for pat in DEFAULT_SKILL_GLOBS:
        hits = sorted(glob.glob(pat, recursive=True))
        if hits:
            return hits[0]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill")
    ap.add_argument("--require-skill", action="store_true")
    a = ap.parse_args()

    if not os.path.isfile(REGISTRY):
        print(f"✗ {REGISTRY} not found — run from the repo root")
        return 2
    text = open(REGISTRY, encoding="utf-8").read()
    entries = registry_entries(text)
    if not entries:
        print("✗ no version entries parsed out of the registry — the checker cannot "
              "bind on an empty set, which would be a vacuous pass")
        return 2

    fails = []

    # ── A. the field is present and well-formed, from FIELD_FROM onward ──────
    checked_a = 0
    for v, vs, body in entries:
        if v < FIELD_FROM:
            continue
        checked_a += 1
        if skill_impact(body) is None:
            fails.append(f"{vs}: no '**Skill impact:** yes|no' line — required from "
                         f"v{FIELD_FROM[0]}.{FIELD_FROM[1]} onward (v3.47)")

    # ── B. the skill is not behind a ruling that declares it affected ────────
    skill = find_skill(a.skill)
    b_ran = False
    if skill:
        stext = open(skill, encoding="utf-8").read()
        bm = re.search(r"\*\*Build:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s*·\s*aligned to "
                       r"`?CANON-REGISTRY\.md`?\s*(v\d+\.\d+)", stext)
        if not bm:
            fails.append(f"{skill}: no parseable '**Build: DATE · aligned to "
                         f"CANON-REGISTRY.md vX.Y**' line — without it staleness is "
                         f"undetectable, which is the defect this checker exists for")
        else:
            aligned = vparse(bm.group(2))
            b_ran = True
            behind = [(v, vs) for v, vs, body in entries
                      if v > aligned and skill_impact(body) == "yes"]
            for v, vs in sorted(behind):
                fails.append(f"{vs} declares 'Skill impact: yes' but the skill is only "
                             f"aligned to {bm.group(2)} — that ruling is not written back, "
                             f"and the skill outranks the registry while stale")

    print(f"registry: {len(entries)} version entries, {checked_a} require the field")
    if b_ran:
        print(f"skill:    {skill}\n          aligned to {bm.group(2)}")
    elif skill:
        print(f"skill:    {skill} — build line unreadable")
    else:
        msg = ("skill:    NOT REACHABLE — check B (write-back) DID NOT RUN. "
               "This is reported, not skipped: a silent skip here would make this "
               "checker a vacuous pass.")
        print(msg)
        if a.require_skill:
            fails.append("--require-skill was set but no skill file was found")

    if fails:
        print(f"\n✗ {len(fails)} problem(s):")
        for f in fails:
            print(f"   - {f}")
        return 1
    print("\n✓ registry/skill sync gate passes"
          + ("" if b_ran else "  (check A only — see above)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
