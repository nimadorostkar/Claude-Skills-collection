---
name: bug-fix-protocol
description: Use when fixing a reported bug end to end. Enforces a disciplined sequence — reproduce, write a failing test, fix minimally, verify, prevent recurrence — and blocks the common failure mode of patching symptoms.
metadata:
  category: development
  version: 1.0.0
  tags: [bugfix, testing, root-cause, process]
---

# Bug Fix Protocol

## Purpose

Turn a bug report into a merged fix without introducing a second bug. The protocol is deliberately rigid: it exists to prevent the two most common failures — fixing the symptom, and fixing the cause without proving it.

## When to Use

- Any reported defect with a reproducible symptom.
- A regression discovered in CI or production.
- A hotfix under time pressure — especially then.

## Capabilities

- Reproduction and minimization.
- Root-cause isolation (see the `debugging` skill for the search method).
- Minimal, targeted fixes with regression tests.
- Blast-radius assessment for the same class of defect elsewhere.

## Inputs

- The bug report: expected behavior, observed behavior, environment, steps.
- Access to logs, traces, or a failing build.
- The severity and whether a rollback is available.

## Outputs

- A failing test that captures the bug.
- The smallest change that makes it pass.
- A note on where else this defect class could occur.

## Workflow

1. **Reproduce before reading code.** If you cannot reproduce it, the report is incomplete — go back for the missing detail. Do not guess.
2. **Write the failing test.** In the real test suite, at the right level. It must fail for the right reason, with a clear message.
3. **Find the cause.** Not the line where it crashed — the decision that made the crash possible.
4. **Fix minimally.** Change only what is required. Refactoring belongs in a separate commit.
5. **Verify.** New test passes; full suite passes; reproduce the original scenario manually and confirm it is gone.
6. **Look for siblings.** Grep for the same pattern elsewhere. A bug found once is usually present three times.
7. **Close the loop.** State in the PR: what broke, why, what changed, and what now prevents it.

## Best Practices

- If you cannot write a test that fails before the fix, you have not understood the bug.
- Under time pressure, mitigate first (rollback, feature flag, rate limit), then fix properly. Do not ship a rushed fix to production and call it done.
- Never "fix" a flaky test by retrying it. Flakiness is a real defect in the test or the code.
- Do not widen a `try/except` to make an error go away. That hides the next bug too.
- Record the root cause in the issue, not just the fix. The next person will search for the symptom.

## Examples

**PR description that closes the loop:**

```markdown
## What broke
Users on annual plans were charged twice when upgrading mid-cycle.

## Why
`ProrationCalculator` issued the invoice before checking whether the
subscription already had a pending invoice for the same period. Under
concurrent upgrade requests, both passed the check.

## Fix
Added a unique constraint on (subscription_id, period_start) and made
invoice creation idempotent on that key. The second request now returns
the existing invoice rather than creating one.

## Prevention
Regression test `test_concurrent_upgrade_creates_one_invoice` runs two
upgrades in parallel and asserts a single invoice. Audited the other
three call sites of `issue_invoice` — `RenewalJob` had the same gap and
is fixed in the same commit.
```

## Notes

- Idempotency keys on write endpoints prevent an entire class of duplicate-side-effect bugs. If the bug was a duplicate charge, message, or record, this is usually the real fix.
- If a bug is reported and cannot be reproduced after honest effort, close it as such and say what you tried. Leaving it open forever is not diligence.
