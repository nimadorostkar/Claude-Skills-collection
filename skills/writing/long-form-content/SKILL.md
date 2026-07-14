---
name: long-form-content
description: Use when writing a researched article, blog post, or long-form piece. Covers building an argument, researching and citing, structure, and writing something with a point rather than a survey.
metadata:
  category: writing
  version: 1.0.0
  tags: [writing, articles, research, blogging, argument]
---

# Long-Form Content

## Purpose

Write a long piece that makes an argument, supported by research, that a reader finishes. The failure mode is a survey of a topic that says nothing — comprehensive, balanced, and pointless.

## When to Use

- Writing a researched article or a substantial blog post.
- Turning a body of research into a readable piece.
- An essay that argues for something.
- Content that must be accurate and sourced.

## Capabilities

- Argument construction.
- Research and source evaluation.
- Structure: opening, development, conclusion.
- Citation and evidence.
- Editing for length and force.

## Inputs

- The topic and, more importantly, the claim.
- The audience and what they already believe.
- The research available, and how good it is.

## Outputs

- A piece with a defensible thesis.
- Claims supported by sources that were actually read.
- A structure a reader can follow.

## Workflow

1. **Find the claim** — What are you actually asserting? A piece "about" a topic is a survey. A piece arguing that something is true, or that a common belief is wrong, is an article. If you cannot state the claim in one sentence, do not start writing.
2. **Research to test the claim, not to support it** — Look for the strongest counterargument first. If it holds, the claim was wrong and you have saved yourself two thousand words.
3. **Open with the claim or with the tension** — Not with a definition, not with history, and never with "since the dawn of time". The first paragraph decides whether the piece is read.
4. **Develop with evidence** — Each section advances the argument. A section that is merely interesting but does not advance it should be cut, however good it is.
5. **Cite what you actually read** — Not the abstract, not what someone else said the paper said.
6. **Edit for force** — The first draft is 30% too long. Cut the hedging, the throat-clearing, and the paragraph you are proud of that does not advance the argument.

## Best Practices

- A piece with no claim is a survey, and surveys are not read. The reader's implicit question is "what do you think, and why should I believe you?"
- Steelman the counterargument. A piece that only engages with the weakest opposing view convinces nobody who did not already agree.
- The opening paragraph carries a disproportionate share of the work. If it does not create tension or state a claim, the reader leaves.
- Hedging weakens prose. "It could be argued that in some cases X may perhaps be true" asserts nothing. Say X, or do not.
- Cut your favourite paragraph if it does not advance the argument. This is the hardest editing rule and the most valuable.
- Cite primary sources. A statistic that has been passed through three blog posts is usually wrong by the time it reaches you.

## Examples

**Openings:**

```text
WEAK — a definition and a throat-clear. Nobody reads paragraph two.

  Microservices are an architectural approach in which an application is
  composed of small, independently deployable services. Since the term was
  popularized in the mid-2010s, many organizations have adopted this pattern.
  In this article we will explore the advantages and disadvantages of
  microservices architecture.

STRONG — a claim and a tension, in two sentences.

  Most teams that adopt microservices end up with a distributed monolith: all
  the operational cost of a distributed system, and none of the independent
  deployability that justified it. The failure is almost always the same one,
  and it happens before a single service is written.
```

The second opening makes a claim, implies the article has a specific answer, and gives the reader a reason to continue.

**Research that tests the claim rather than decorating it:**

```text
Claim: "Microservices adoption usually produces a distributed monolith."

Before writing, look for what would falsify this:
  - Are there large-scale surveys? (Yes: several state-of-DevOps style reports.
    Read them. Note that they measure adoption, not outcome — so they do not
    settle the question.)
  - Who argues the opposite, and what is their best case? (Teams with genuine
    independent deployability. Read their accounts. Their common factor:
    they split around data ownership, not around entities.)
  - Is there a definitional problem? (Yes — "distributed monolith" has no
    agreed definition. Define it explicitly, or the claim is unfalsifiable
    and therefore uninteresting.)

This research changed the piece: the claim became "teams that split by entity
rather than by data ownership produce a distributed monolith", which is
sharper, more defensible, and actually useful.
```

## Notes

- Researching to test a claim rather than to support it is the difference between an argument and a rationalization, and readers can tell.
- The 30% rule holds remarkably well: nearly every first draft improves by cutting a third, and almost none improve by adding.
- A piece that changes its own claim during research is a piece that was worth writing. One that ends where it started usually did not need the research.
