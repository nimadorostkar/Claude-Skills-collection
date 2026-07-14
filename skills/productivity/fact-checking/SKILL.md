---
name: fact-checking
description: Use when verifying claims. Covers tracing a claim to its origin, evaluating sources, detecting laundered statistics, and reporting a verdict with the evidence rather than an assertion.
metadata:
  category: productivity
  version: 1.0.0
  tags: [fact-checking, verification, sources, claims, evidence]
---

# Fact-Checking

## Purpose

Verify a claim by tracing it to its origin. Most false claims in circulation are not fabrications; they are real findings that have been stripped of their qualifications, or numbers that have acquired a citation through repetition.

## When to Use

- Verifying a statistic or a claim before publishing it.
- A number that is widely repeated and never sourced.
- Checking an assertion in a document, an article, or a report.
- Evaluating a claim that seems too clean.

## Capabilities

- Tracing a claim to its primary source.
- Detecting circular citation.
- Evaluating study quality and its actual conclusion.
- Identifying the qualifications that were dropped.
- Reporting a verdict with evidence.

## Inputs

- The claim, quoted exactly.
- Where it appeared and what it was used to support.

## Outputs

- A verdict: supported, unsupported, misleading, or unverifiable.
- The chain of citation, traced.
- What the original source actually says.

## Workflow

1. **Quote the claim exactly** — Vague paraphrases are unfalsifiable. "Most projects fail" cannot be checked; "70% of software projects fail" can.
2. **Follow the citation chain** — Each source cites another. Follow it until you reach a primary source, or until it loops, or until it disappears. All three outcomes are informative.
3. **Read what the original actually says** — Very frequently, the original is a limited finding about a specific population that has been generalized into a universal claim by the time it reaches you.
4. **Check for independence** — Twelve sources citing one study is one study.
5. **Check the qualifications that were dropped** — "In a survey of 43 startups in one accelerator cohort" becomes "70% of startups" within three citations.
6. **Report the chain, not just the verdict** — The chain is the evidence.

## Best Practices

- A claim with no traceable origin is not established, however widely it is repeated. Repetition is not evidence.
- Numbers that are suspiciously round (90%, 70%, 50%) are frequently rhetorical rather than measured. Check them.
- The most common falsification is not fabrication but the dropping of qualifications: a finding about a specific population, under specific conditions, becomes a universal law.
- Check the date. A statistic that was true in 2011 may have no relationship to the present, and it will still be quoted.
- Check who funded the study, and what they wanted it to show. This does not invalidate it, but it determines how much scrutiny it warrants.
- "Unverifiable" is a legitimate verdict, and a useful one. It is not the same as "false".

## Examples

**Tracing a claim to its origin:**

```markdown
## Claim
"70% of digital transformation projects fail."

## Chain

Appears in: a 2025 consultancy report.
  Cited to  -> a 2023 industry magazine article.
    Cited to  -> a 2019 blog post by a management consultancy.
      Cited to  -> a 2016 book.
        Cited to  -> a 2013 article in a business publication.
          Cited to  -> "research suggests" — no citation. The chain ends.

There is no study. The number entered circulation without a source and acquired
authority through repetition. Each citation cited the previous citation, and by
the fifth hop it was being reported as an established statistic.

## What the closest thing to evidence actually says

A separate 2011 survey — sometimes cited in the same context — found that 
of 1,471 IT projects, the average cost overrun was 27%, and one in six projects
had a cost overrun exceeding 200%. That is a real finding, and it does not say
70% of anything failed. It is about cost overrun, not failure, and "failure" is
never defined in any of the sources in the chain above.

## Verdict: UNSUPPORTED

The number has no traceable origin. It should not be used. If a figure is
needed, cite the 2011 study for what it actually measured — cost overrun — and
state the definition.

Note also: "digital transformation" is not defined in any source in the chain,
which makes the claim unfalsifiable even in principle.
```

**Detecting a dropped qualification:**

```markdown
## Claim as it appeared
"Remote workers are 13% more productive."

## What the original study found
A 2015 randomized trial at a single Chinese travel agency, on call-center staff
performing a highly measurable, repetitive task, over nine months.

The 13% figure breaks down as: ~9% from working more minutes per shift (fewer
breaks, fewer sick days) and ~4% from more calls per minute.

The same study found that half the participants asked to return to the office,
and that promotion rates for remote workers fell.

## Verdict: MISLEADING

The finding is real. The claim, as stated, is not what the study found. It
generalizes a result about call-center piecework at one company to knowledge
work generally, and it omits both the mechanism (more hours, not more output
per hour) and the negative findings from the same study.
```

## Notes

- The citation chain ending in "research suggests" with no source is the single most common pattern in laundered statistics, and it is why tracing to the primary source is not optional.
- A finding whose mechanism is "they worked more hours" being reported as "they are more productive" is not a lie, but it is not the truth either. Read the mechanism.
- Reporting the chain, rather than just the verdict, is what makes the fact-check checkable. Otherwise you are asking to be trusted, which is the problem you started with.
