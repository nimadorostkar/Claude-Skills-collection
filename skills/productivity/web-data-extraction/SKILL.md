---
name: web-data-extraction
description: Use when extracting data from web pages. Covers choosing between an API, static parsing, and a browser, handling JavaScript-rendered content, resilient selectors, rate limiting, and scraping responsibly.
metadata:
  category: productivity
  version: 1.0.0
  tags: [scraping, extraction, html, browser, automation]
---

# Web Data Extraction

## Purpose

Get structured data out of web pages reliably. The two questions that determine the entire approach are whether an API exists, and whether the content is rendered by JavaScript — and both are answered in under a minute.

## When to Use

- Extracting structured data from a website.
- A scraper that returns empty results or breaks constantly.
- Deciding between static parsing and a headless browser.
- Building a repeatable data-collection pipeline.

## Capabilities

- Approach selection: API, static HTML, or browser rendering.
- Resilient selector strategy.
- JavaScript-rendered content.
- Rate limiting, retries, and politeness.
- Detecting and handling structure changes.

## Inputs

- The target pages and the data required.
- Whether the site has an API, documented or otherwise.
- Volume and frequency.

## Outputs

- Structured, validated data.
- A scraper that fails loudly when the page changes, rather than silently returning nothing.

## Workflow

1. **Look for an API first** — Check the documentation, then check the network tab. Very often the page itself calls a JSON endpoint, and that endpoint is stable, structured, and far easier to use than the HTML.
2. **Determine whether the content is in the HTML** — `curl` the URL and search for the data. If it is absent, the page renders it with JavaScript and static parsing will return nothing, forever, with no error.
3. **Choose the tool accordingly** — Static HTML: an HTTP client and a parser. JavaScript-rendered: a headless browser. Do not use a browser when you do not need one; it is fifty times slower.
4. **Write resilient selectors** — Anchor on stable attributes (`data-*`, an id, a semantic element), not on a generated class name that changes with every deploy.
5. **Be polite** — Rate limit, identify yourself, respect `robots.txt`, and cache. A scraper that hammers a site is both rude and likely to be blocked.
6. **Validate the output** — A scraper that silently returns zero rows because the page changed is worse than one that crashes.

## Best Practices

- The most common scraping bug is a silent empty result. A page redesign turns your scraper into a machine that confidently produces nothing. Raise on an empty match, always.
- Class names in modern frontends are generated and change on every build. `data-testid`, `id`, and semantic elements are the only stable anchors.
- A headless browser is fifty to a hundred times slower and heavier than an HTTP request. Establish that you need one before reaching for it.
- Rate limit and cache. Re-fetching the same page during development, dozens of times, is both wasteful and the fastest way to get your IP blocked.
- Send a real User-Agent that identifies you and provides a contact. Anonymous scraping at volume is what gets scrapers banned as a class.
- Respect `robots.txt` and the site's terms. Scraping public data is generally lawful in many jurisdictions; ignoring an explicit prohibition is a different matter, and the legal position varies.

## Examples

**The check that determines everything:**

```bash
# Is the data in the HTML, or is it rendered by JavaScript?
curl -s "https://example.com/products" | grep -c "product-title"

# 0  -> The content is not in the HTML. It is rendered client-side. A static
#       parser will return nothing and will not tell you why. You need a browser
#       — OR, better, find the API the page itself is calling.
# 24 -> The content is there. Parse it statically; it is 50x faster.
```

**Find the API the page calls, rather than scraping the page:**

```javascript
// In the browser's network tab, filter by Fetch/XHR. Very frequently:
//   GET /api/v2/products?page=1&limit=24
//   -> {"products": [{"id": ..., "title": ..., "price_cents": ...}], "total": 480}
//
// This is structured, paginated, stable, and 100x cheaper to consume than
// parsing the rendered HTML. It is also far less likely to break, because the
// site's own frontend depends on it.
```

**A scraper that fails loudly:**

```python
async def extract_products(html: str, url: str) -> list[Product]:
    tree = HTMLParser(html)

    # Anchor on data attributes and semantic structure, not on generated class
    # names like ".css-1x7f9ka" that change on every deploy.
    cards = tree.css("[data-testid='product-card']")

    if not cards:
        # This is the critical branch. A scraper that returns [] when the page
        # structure changes will quietly produce an empty dataset for weeks.
        raise StructureChanged(
            f"No product cards found at {url}. The selector "
            f"[data-testid='product-card'] matched nothing. The page structure "
            f"has probably changed — do not treat this as 'no products'."
        )

    products = []
    for card in cards:
        title = card.css_first("[data-testid='title']")
        price = card.css_first("[data-testid='price']")

        if title is None or price is None:
            logger.warning("card_missing_fields", extra={"url": url, "html": card.html[:200]})
            continue

        products.append(Product(
            title=title.text(strip=True),
            price_cents=parse_price(price.text(strip=True)),
            url=urljoin(url, card.css_first("a").attributes["href"]),
        ))

    return products
```

## Notes

- Finding the JSON API the page already calls is the single highest-value move in web scraping, and it takes thirty seconds in the network tab. Most people go straight to parsing the HTML and never look.
- `robots.txt` is not legally binding everywhere, but ignoring it is both discourteous and the fastest route to being blocked. Where a site's terms explicitly prohibit automated access, that is a different and more serious question — check before proceeding.
- Cache aggressively during development. Every re-run against a live site is a request someone else pays for.
