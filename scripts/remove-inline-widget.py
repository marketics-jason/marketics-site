#!/usr/bin/env python3
"""
remove-inline-widget.py — Addendum B4, one-shot migration.

Removes the per-page inline GHL chat-widget loader from every HTML page. The
widget is now loaded from `mkx-consent.js`, which restricts it to the
audit-request form page and, in gated regions, waits for an explicit Accept.
Before this, it loaded on 34 pages — and on 33 of them five seconds after load
with no interaction at all, which is a third-party script and its storage for a
visitor who had done nothing and, outside the gated regions, been asked nothing.

The block appears in three comment variants, so this anchors on structure — the
`<!-- GHL Chat Widget` comment through the `</script>` that closes the loader —
rather than on any one wording. Every match is checked for the loader URL before
it is removed, so a mis-anchored match deletes nothing.

Usage:
  python3 scripts/remove-inline-widget.py --dry-run   # report only
  python3 scripts/remove-inline-widget.py             # apply
"""
import glob
import re
import sys

BLOCK = re.compile(r'\n*[ \t]*<!--\s*GHL Chat Widget.*?</script>\s*', re.S)
LOADER = 'widgets.leadconnectorhq.com/loader.js'

dry = '--dry-run' in sys.argv
files = sorted(f for f in glob.glob('**/*.html', recursive=True)
               if not f.startswith('audits/'))

removed, skipped, problems = [], [], []

for path in files:
    src = open(path, encoding='utf-8').read()
    matches = list(BLOCK.finditer(src))
    if not matches:
        if LOADER in src:
            problems.append(f'{path}: loader present but no anchored block — inspect by hand')
        continue
    if len(matches) > 1:
        problems.append(f'{path}: {len(matches)} candidate blocks — refusing to guess')
        continue

    m = matches[0]
    if LOADER not in m.group(0):
        problems.append(f'{path}: matched block does not contain the loader URL — refusing')
        continue

    out = src[:m.start()] + '\n' + src[m.end():]
    if LOADER in out:
        problems.append(f'{path}: loader still present after removal — refusing')
        continue

    if not dry:
        open(path, 'w', encoding='utf-8').write(out)
    removed.append(path)

for p in removed:
    print(f'  {"would remove" if dry else "removed"}  {p}')
if skipped:
    for p in skipped:
        print(f'  skipped  {p}')
print(f'\n{len(removed)} page(s) {"would be " if dry else ""}cleaned')

if problems:
    print('\nPROBLEMS — nothing was changed in these files:')
    for p in problems:
        print(f'  ! {p}')
    sys.exit(1)
