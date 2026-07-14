---
name: technical-documentation
description: Use when writing developer-facing documentation. Covers the four documentation types and choosing between them, writing a README, API reference, and tutorials that work.
metadata:
  category: writing
  version: 1.0.0
  tags: [documentation, readme, api-docs, tutorials, technical-writing]
---

# Technical Documentation

## Purpose

Write documentation that answers the question the reader actually has. Most documentation fails because it mixes four incompatible purposes into one document and serves none of them.

## When to Use

- Writing a README, a getting-started guide, or API reference.
- Documentation that exists but that nobody can use.
- Documenting a library, a service, or an internal system.
- Auditing documentation for gaps.

## Capabilities

- The four types: tutorial, how-to, reference, explanation — and keeping them apart.
- README structure.
- API reference: complete, accurate, and generated where possible.
- Runnable examples.
- Keeping documentation accurate as the code changes.

## Inputs

- The system, and who reads about it.
- The questions readers actually arrive with.
- The existing documentation, and where it fails.

## Outputs

- Documentation organized by reader intent.
- Examples that run.
- A README that gets someone to a working state.

## Workflow

1. **Identify the reader's question** — "How do I start?" (tutorial), "How do I do X?" (how-to), "What are the parameters?" (reference), "Why is it built this way?" (explanation). These are four different documents. Mixing them is why documentation is unusable.
2. **Write the README to a first success** — Install, minimal working example, then links. A reader should be running something within two minutes. Everything else is a link.
3. **Make the examples runnable** — Copy, paste, and it works. An example with an elided `...` or an undefined variable is a broken promise.
4. **Generate the reference** — From the code, from the types, from the OpenAPI spec. Hand-written reference documentation is wrong within a month.
5. **Test the tutorial on a stranger** — Someone who has never seen the project. Every place they get stuck is a defect in the document.

## Best Practices

- The single most common documentation failure is mixing a tutorial with a reference. A reader trying to get started does not want a complete list of options; a reader looking up a parameter does not want a narrative.
- A README that opens with a philosophy section has lost the reader. Open with what it is, in one sentence, and how to install it.
- Every code example must run as written. Test them in CI — documentation examples rot faster than the code.
- Write the error cases. "What happens when the token is invalid" is the question people arrive with, and it is almost never documented.
- Document the why, separately. A reader who understands the design makes better decisions than one who has memorized the API.
- Do not document what the code says. Document what the code cannot say: the constraints, the reasons, the gotchas.

## Examples

**A README that gets to a working state:**

```markdown
# rateguard

Rate limiting for FastAPI, backed by Redis. Token bucket and sliding window,
with per-user and per-endpoint limits.

## Install

    pip install rateguard

## Use

    from fastapi import FastAPI
    from rateguard import RateLimiter, limit

    app = FastAPI()
    limiter = RateLimiter(redis_url="redis://localhost:6379")

    @app.get("/search")
    @limit(limiter, "20/minute", key="ip")
    async def search(q: str):
        return {"results": []}

Requests beyond the limit receive a 429 with a `Retry-After` header.

## Next

- [Per-user limits](docs/how-to/per-user.md)
- [Choosing an algorithm](docs/explanation/algorithms.md) — token bucket vs sliding window
- [API reference](docs/reference.md)
- [Deploying behind a proxy](docs/how-to/proxies.md) — you must configure this,
  or every request will appear to come from the same IP
```

The reader is running rate-limited code in under a minute. The proxy warning is placed where it will actually be seen, because it is the mistake everyone makes.

**The four types, kept apart:**

```text
docs/
  tutorial/
    getting-started.md      "Take me from nothing to a working rate limiter."
                            Learning-oriented. One path. No options. No alternatives.

  how-to/
    per-user-limits.md      "I need to limit by user ID, not IP."
    proxies.md              "I'm behind Cloudflare and all IPs are the same."
                            Task-oriented. Assumes competence. Solves one problem.

  reference/
    api.md                  "What are the parameters of `limit()`?"
                            Information-oriented. Complete. Dry. Generated.

  explanation/
    algorithms.md           "Why token bucket rather than a fixed window?"
                            Understanding-oriented. Discusses trade-offs. No steps.
```

A single "Documentation" page containing all four is the default, and it is why most documentation is unusable: the tutorial reader drowns in options and the reference reader wades through narrative.

## Notes

- The four-type framework (tutorial, how-to, reference, explanation) is the single most useful structural idea in technical writing. Most documentation problems dissolve once the types are separated.
- Run the code examples in CI. A documented example that no longer compiles is worse than no example, because it is trusted.
- The best test of a getting-started guide is watching a new person follow it without helping them. Every question they ask is a line the document is missing.
