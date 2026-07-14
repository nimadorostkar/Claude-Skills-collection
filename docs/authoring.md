# Authoring a skill

A skill has two jobs: **load at the right moment**, and **change what the agent does when it loads**. Nearly every failed skill fails at the first, and nearly every rejected contribution fails at the second.

## The description is the skill

The agent sees only the `description` before deciding whether to read the body. Everything about triggering is determined here.

**A description that does not trigger:**

```yaml
description: A comprehensive methodology for validating service contracts and ensuring API reliability through systematic verification.
```

This is a conference talk title. A user with a problem types "write tests for my API" — and none of those words appear.

**A description that triggers:**

```yaml
description: >-
  Use when writing tests for an HTTP API or endpoint. Covers request tests,
  contract tests, fixtures, and testing error paths. Trigger on "write tests
  for my API", "test this endpoint", "integration tests for the orders service".
  Do not use for deciding what to test at which level — see the test-strategy skill.
```

Three things are doing the work:

1. **The user's vocabulary.** The words they will actually type.
2. **The scope.** What is in, so the agent knows when it applies.
3. **The boundary.** What is out, so it does not compete with a neighbour.

## Test the triggering before you write the body

Ten phrasings that should load it. Five that should not.

```text
Should trigger:
  "this endpoint takes 3 seconds and I think it's the database"     ✓
  "add an index to the orders table"                                 ✓
  "why is this query slow"                                           ✓
  [pastes an EXPLAIN ANALYZE output with no question]                ✓
  "the reports page times out"                                       ✓

Should NOT trigger:
  "design a schema for a booking system"     → data-modeling
  "the frontend feels slow"                  → web-performance
  "write a SQL query to find duplicates"     → sql
```

If fewer than eight of ten trigger, the description is wrong. Fix it before writing another word — the body is irrelevant if the skill never loads.

## Prove it changes behavior

Run five realistic requests with no skill loaded. Record the output. Then load the skill and run them again.

If the output is materially the same, the skill does not belong in the library. This happens most often when a skill restates what the model already does well — "write tests", "use meaningful variable names", "handle errors".

The difference should be visible and specific:

```text
Without the skill: the agent writes a reasonable request test with a fixture,
                   covering the happy path and a 404.

With the skill:    the same, plus the 422 validation path, plus an assertion
                   that the error response matches the problem-details format,
                   plus a test that the endpoint is idempotent under retry.
```

That is a skill. A skill that adds one bullet point to the output is a bullet point, and it should be folded into a broader skill rather than standing alone.

## What makes a skill good

**It names the mistake.** The single most valuable thing a skill contains is the specific, common way people get it wrong:

> The most common cost mistake is a variable value — a timestamp, a UUID, a user's name — near the top of an otherwise stable system prompt, which silently disables prompt caching.

The agent will not derive that. It is what the skill is for.

**It enforces an order.** Many skills are valuable purely because they impose a sequence the agent would otherwise skip:

> Evaluate retrieval separately, **before touching the prompt**. If the correct passage is not in the top-k, no amount of prompt engineering will produce a correct answer.

**Its examples show the failure.** A correct example teaches less than a wrong example next to a correct one. The wrong one is where the reader recognizes themselves.

**Its Notes section surprises a practitioner.** If an experienced engineer reads the `Notes` and learns nothing, the skill is a summary rather than expertise.

## Progressive disclosure

The body is loaded every time the skill triggers. Keep it to what is always needed.

```text
skills/data/database-performance/
  SKILL.md                    ~180 lines, always loaded
  references/
    explain-plans.md          read only when analyzing a plan
    index-types.md            read only when choosing an index type
    lock-modes.md             read only when diagnosing contention
  scripts/
    slow_query_report.py      executed, never read into context
```

In the body: *"For the meaning of each node type in an execution plan, read `references/explain-plans.md`."* The agent fetches it when the task requires it, and pays nothing for it otherwise.

Scripts are the strongest form of this. A script the agent runs costs a handful of tokens; the same logic written as instructions costs hundreds and is followed imperfectly.

## The common failures

| Failure | Symptom | Fix |
| --- | --- | --- |
| Description in the author's vocabulary | Never triggers | Rewrite in the user's words |
| Description too broad | Triggers on everything | Add scope and an explicit boundary |
| Overlaps another skill | Both load; they contradict | Sharpen both descriptions, or merge |
| Restates the model's defaults | No behavioral difference | Delete it |
| Written as documentation | Reads well, changes nothing | Rewrite as instructions |
| Generic Best Practices | Could appear in any skill | Cut every line that could |
| Toy examples | The agent copies the toy | Use real code that would run |
| Outdated guidance | The agent confidently does the wrong thing | Version-check the Notes |

## Once it works

Add the version. Run `python scripts/validate.py`. Open the PR with the before/after evidence.

The evidence is the review. A skill without it will be asked for it.
