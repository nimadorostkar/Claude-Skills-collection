---
name: skill-review
description: Use when reviewing or improving an existing agent skill. Covers triggering accuracy, content quality, redundancy with the base model, and measuring whether the skill actually changes behavior.
metadata:
  category: agent-tooling
  version: 1.0.0
  tags: [skills, review, evaluation, quality]
---

# Skill Review

## Purpose

Assess whether a skill earns its place. A skill costs context and attention every time it loads; it must return more than it costs.

## When to Use

- Reviewing a skill before publishing it.
- A skill that triggers unreliably.
- Auditing a skill library for redundancy and dead weight.
- Deciding whether two skills should be merged or split.

## Capabilities

- Triggering evaluation: does it fire when it should, and stay silent when it should not?
- Content quality: is the guidance specific, correct, and actionable?
- Redundancy check: does it tell the model something it does not already do?
- Overlap detection across a library.

## Inputs

- The skill, and the library it sits in.
- Real user phrasings for the task it addresses.
- The model's behavior on that task without the skill.

## Outputs

A verdict with specifics:

- **Keep** — Triggers correctly, changes behavior for the better.
- **Revise** — Named defects: description, content, or scope.
- **Merge or delete** — It duplicates another skill, or adds nothing.

## Workflow

1. **Test the triggering first** — Ten phrasings that should trigger it, and five that should not. This is the fastest way to find that a skill is unusable, and it is the most common defect.
2. **Run the task without the skill** — Establish the baseline. If the model already handles the task well, the skill is not needed.
3. **Run it with the skill** — Compare. The difference is the skill's entire value. If there is no difference, delete it.
4. **Read the content critically** — Is it specific enough to act on? Are the constraints real rules or vague preferences? Do the examples show the actual output shape?
5. **Check for overlap** — Two skills that both trigger on the same request will both load, doubling the cost and possibly contradicting each other.
6. **Check the accuracy** — Outdated practices in a skill are worse than no skill, because the model will follow them confidently.

## Best Practices

- The behavioral difference is the only measure that matters. A beautifully written skill that does not change the output is decoration.
- A skill that triggers on 30% of the requests it should is broken, however good its content is. Fix the description first — content quality is irrelevant if the skill never loads.
- Look for guidance that was true two years ago and is not now. Skills rot, and a confidently stated obsolete practice is a liability.
- Two skills with overlapping descriptions will both load. Either the boundary must be sharpened in both descriptions, or they should be one skill.
- Prose that describes a domain rather than instructing an action is filler. Cut it.
- A skill with no constraints ("prefer clean code") is not a skill. It is a sentiment.

## Examples

**A review that is actionable:**

```markdown
## Review: `api-testing`

### Triggering — FAIL
Tested 10 phrasings a user would actually use:
  "write tests for my API"                    -> did not trigger
  "how do I test this endpoint"               -> did not trigger
  "integration tests for the orders service"  -> triggered
  ... 3/10 triggered.

Cause: the description says "Comprehensive API testing methodology and
best practices for validating service contracts." It contains none of the
words a user would use. It reads like a conference talk title.

Fix: "Use when writing tests for an HTTP API or endpoint. Covers request
tests, contract tests, fixtures, and testing error paths. Trigger on
'write tests for my API', 'test this endpoint', 'integration tests'."

### Behavioral difference — MARGINAL
Baseline (no skill): the model writes reasonable request tests with a fixture,
covers the happy path and a 404.
With the skill: the same, plus it now tests the 422 validation path.

The skill adds one thing. That thing is worth having, but the skill is 340
lines to deliver it.

Fix: cut the sections on "why testing matters" (2 pages), the HTTP status
code reference (the model knows), and the generic pytest introduction. Keep
the error-path checklist and the contract-testing section, which are the
parts that changed the output. Target: under 120 lines.

### Overlap — ACTION REQUIRED
`api-testing` and `test-strategy` both trigger on "how should I test this".
Both load. They give different advice on mocking.

Fix: `test-strategy` owns the question of what to test at which level.
`api-testing` owns how to write an HTTP test. Add an explicit boundary to
both descriptions.

### Verdict: REVISE
Fix the description (blocking — the skill currently does not work), cut the
filler, and resolve the overlap.
```

## Notes

- The "did not trigger" failure is by far the most common and the most fatal, and it is invisible unless you test for it explicitly. Content review is pointless until triggering works.
- A skill whose value is one checklist item should be one checklist item, folded into a broader skill — not a 300-line file.
- When two skills disagree, the model will follow one of them arbitrarily. Contradiction across a library is worse than a gap.
