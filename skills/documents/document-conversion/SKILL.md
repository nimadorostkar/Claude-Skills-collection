---
name: document-conversion
description: Use when converting between document formats. Covers HTML to Markdown, document to Markdown, PDF generation from HTML, and preserving structure through a conversion rather than losing it.
metadata:
  category: documents
  version: 1.0.0
  tags: [conversion, markdown, html, pandoc, scraping]
---

# Document Conversion

## Purpose

Convert documents between formats while preserving the structure that matters. Most conversion tools preserve the text and destroy the structure, which is usually the part you needed.

## When to Use

- Converting a web page or an HTML document to Markdown.
- Converting Word, PDF, or HTML into a text format for processing.
- Generating a PDF from HTML or Markdown.
- Normalizing a mixed corpus into one format.

## Capabilities

- HTML to Markdown, with structure preserved.
- Office formats to Markdown or plain text.
- Markdown or HTML to PDF, with proper pagination.
- Batch conversion and normalization.
- Content extraction from web pages, discarding the navigation.

## Inputs

- The source documents and their formats.
- What must survive the conversion: headings, tables, links, code blocks, images.
- The target format and what it can represent.

## Outputs

- Converted documents with their structure intact.
- A report of what could not be preserved.

## Workflow

1. **Decide what must survive** — Headings and tables usually must. Fonts and exact spacing usually must not. Naming this first prevents a great deal of wasted effort on preserving things nobody needs.
2. **Extract the content, not the page** — A web page is 80% navigation, cookie banners, and related-articles rails. Convert the article, not the chrome.
3. **Use a converter that understands the structure** — A regex that strips HTML tags produces a wall of text with no headings and no tables. Use a real parser.
4. **Handle the tables specially** — They are the most commonly destroyed structure. Verify them after conversion.
5. **Verify a sample** — Open the output next to the input and compare. Conversion failures are usually silent.

## Best Practices

- Structure is what makes a document useful. A conversion that produces correct text with no headings has thrown away the navigation, the outline, and every chunking boundary a downstream system would use.
- Tables convert badly by default and are frequently the highest-value content. Check them explicitly.
- Code blocks lose their language annotation in most conversions. If the corpus is technical, that matters.
- When converting HTML, strip the navigation, the footer, and the scripts *before* converting, not after — an extraction library that identifies the main content does this far better than a hand-written selector.
- PDF generation from HTML requires a real browser engine for anything with modern CSS. Older HTML-to-PDF libraries silently ignore flexbox and grid, and the output looks nothing like the page.
- Preserve the source URL or path in the output. A converted document with no provenance is unverifiable.

## Examples

**Web page to Markdown, keeping the content and discarding the page:**

```python
import trafilatura
from markdownify import markdownify

def url_to_markdown(url: str) -> Document:
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        raise ConversionError(f"could not fetch {url}")

    # trafilatura identifies the main content and discards navigation, footers,
    # cookie banners, and related-article rails. A hand-written CSS selector
    # does this badly and breaks on every site redesign.
    content_html = trafilatura.extract(
        downloaded,
        output_format="html",
        include_tables=True,       # tables are usually the point
        include_links=True,
        include_images=False,
        favor_precision=True,
    )
    if content_html is None:
        raise ConversionError(f"no main content identified in {url}")

    metadata = trafilatura.extract_metadata(downloaded)

    markdown = markdownify(
        content_html,
        heading_style="ATX",       # ## rather than underlines
        code_language_callback=lambda el: el.get("class", [""])[0].replace("language-", ""),
    )

    return Document(
        title=metadata.title,
        source_url=url,            # provenance: without it, the output is unverifiable
        retrieved_at=utcnow(),
        markdown=markdown.strip(),
    )
```

**HTML to PDF that respects modern CSS:**

```python
from playwright.sync_api import sync_playwright

def html_to_pdf(html: str, output: str) -> None:
    """A real browser engine. Older HTML-to-PDF libraries silently ignore
    flexbox and grid, and the resulting PDF bears no resemblance to the page."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        page.emulate_media(media="print")        # apply @media print rules

        page.pdf(
            path=output,
            format="A4",
            margin={"top": "20mm", "bottom": "20mm", "left": "18mm", "right": "18mm"},
            print_background=True,
            display_header_footer=True,
            footer_template=(
                '<div style="font-size:9px;width:100%;text-align:center;color:#666">'
                '<span class="pageNumber"></span> / <span class="totalPages"></span></div>'
            ),
        )
        browser.close()
```

## Notes

- Content-extraction libraries (trafilatura, readability) consistently outperform hand-written selectors, and they do not break when the site is redesigned. The instinct to write a CSS selector for the article body is a maintenance trap.
- `emulate_media(media="print")` is what applies the page's print stylesheet — without it, you get a PDF of the screen layout, including the navigation bar on every page.
- Pandoc remains the most capable general-purpose converter for document formats. For web content specifically, an extraction library plus a Markdown converter produces better results.
