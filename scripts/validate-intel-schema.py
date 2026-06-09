#!/usr/bin/env python3
"""Validate Article JSON-LD schema on intel pages.

Enforces the schema standard agreed for the /intel/ cluster pages:
  - datePublished : full ISO 8601 datetime WITH a timezone offset
  - dateModified  : same format
  - image         : present, absolute https URL
  - author.url    : present, absolute URL
  - publisher.url : present, absolute URL

Usage:
    validate-intel-schema.py <file> [<file> ...]

Pass the intel page(s) to check (typically the files changed in a PR).
With no files, exits 0 (nothing to validate). Exits 1 if any page fails.

This is the "template" for a template-less static site: new pages must
meet the standard before they can merge. It only checks the files handed
to it, so it never retroactively fails older pages left untouched.
"""
import json
import re
import sys
from datetime import datetime

JSONLD_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I,
)


def is_absolute_url(value):
    return isinstance(value, str) and value.startswith(("https://", "http://"))


def has_timezone_datetime(value):
    """True if value is an ISO 8601 datetime that includes a time and a timezone."""
    if not isinstance(value, str) or "T" not in value:
        return False
    candidate = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return False
    return parsed.tzinfo is not None


def find_article_blocks(html):
    blocks = []
    for raw in JSONLD_RE.findall(html):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Malformed JSON-LD is itself a problem worth surfacing.
            blocks.append(("__invalid_json__", raw.strip()[:80]))
            continue
        for node in data if isinstance(data, list) else [data]:
            if isinstance(node, dict) and node.get("@type") == "Article":
                blocks.append(("article", node))
    return blocks


def validate_article(node):
    errors = []

    dp = node.get("datePublished")
    if dp is None:
        errors.append('missing "datePublished"')
    elif not has_timezone_datetime(dp):
        errors.append(
            f'"datePublished" must be a full ISO 8601 datetime with timezone '
            f'(e.g. 2026-06-05T09:00:00-04:00), got: {dp!r}'
        )

    dm = node.get("dateModified")
    if dm is None:
        errors.append('missing "dateModified"')
    elif not has_timezone_datetime(dm):
        errors.append(
            f'"dateModified" must be a full ISO 8601 datetime with timezone, got: {dm!r}'
        )

    image = node.get("image")
    img_url = image.get("url") if isinstance(image, dict) else image
    if not image:
        errors.append('missing "image" (absolute https URL, ideally 1200x630+)')
    elif not is_absolute_url(img_url):
        errors.append(f'"image" must be an absolute URL, got: {img_url!r}')

    author = node.get("author")
    if not isinstance(author, dict):
        errors.append('"author" must be an object with a "url"')
    elif not is_absolute_url(author.get("url")):
        errors.append(f'author "url" must be an absolute URL, got: {author.get("url")!r}')

    publisher = node.get("publisher")
    if not isinstance(publisher, dict):
        errors.append('"publisher" must be an object with a "url"')
    elif not is_absolute_url(publisher.get("url")):
        errors.append(f'publisher "url" must be an absolute URL, got: {publisher.get("url")!r}')

    return errors


def main(argv):
    files = argv[1:]
    if not files:
        print("No intel pages to validate.")
        return 0

    failed = False
    for path in files:
        try:
            with open(path, encoding="utf-8") as fh:
                html = fh.read()
        except OSError as exc:
            print(f"::error file={path}::could not read file: {exc}")
            failed = True
            continue

        blocks = find_article_blocks(html)
        if not blocks:
            print(f"  {path}: no Article schema found — skipping")
            continue

        for kind, node in blocks:
            if kind == "__invalid_json__":
                print(f"::error file={path}::invalid JSON-LD near: {node}")
                failed = True
                continue
            errors = validate_article(node)
            if errors:
                failed = True
                print(f"✗ {path}")
                for err in errors:
                    print(f"::error file={path}::Article schema: {err}")
            else:
                print(f"✓ {path}: Article schema valid")

    if failed:
        print("\nSchema validation FAILED. See errors above.")
        print("Fix the Article JSON-LD to match intel/SCHEMA-CHECKLIST.md.")
        return 1
    print("\nAll checked intel pages have valid Article schema.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
