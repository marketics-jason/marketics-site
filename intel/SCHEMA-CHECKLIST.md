# /intel/ page schema checklist

Every intel cluster page is hand-built HTML — there's no template engine, so
the schema standard is enforced by CI instead (`.github/workflows/validate-schema.yml`,
which runs `scripts/validate-intel-schema.py` on the pages a PR changes).

When you add or edit an intel page, the Article JSON-LD in `<head>` **must**
have all of the following, or the PR's "Validate intel schema" check fails:

- [ ] `datePublished` — full ISO 8601 **with timezone**, e.g. `2026-06-05T09:00:00-04:00`
      (Eastern is `-04:00` in summer / EDT, `-05:00` in winter / EST). Not date-only.
- [ ] `dateModified` — same format. Set it equal to `datePublished` unless the
      article content actually changed (don't fake a refresh).
- [ ] `image` — absolute `https://` URL, ideally 1200×630+. `https://marketics.io/og/default.jpg` is fine.
- [ ] `author.url` — absolute URL (`https://marketics.io/story`, or a `sameAs` LinkedIn link).
- [ ] `publisher.url` — absolute URL (`https://marketics.io`).

## Canonical Article block (copy, then fill the values)

```html
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "Article",
 "headline": "PAGE HEADLINE",
 "description": "PAGE DESCRIPTION.",
 "author": {"@type": "Person", "name": "Jason Baxter", "url": "https://marketics.io/story"},
 "publisher": {"@type": "Organization", "name": "Marketics", "url": "https://marketics.io"},
 "image": "https://marketics.io/og/default.jpg",
 "datePublished": "2026-06-05T09:00:00-04:00",
 "dateModified": "2026-06-05T09:00:00-04:00",
 "url": "https://marketics.io/intel/SLUG"
}
</script>
```

## Run the check locally before pushing

```bash
python3 scripts/validate-intel-schema.py intel/YOUR-PAGE/index.html
```

> Note: this only enforces the standard on pages you touch. Older intel pages
> that are still date-only (e.g. `trust`, `money`, `algorithm`) are intentionally
> left alone until they're next edited — fixing them is optional polish, not a blocker.
