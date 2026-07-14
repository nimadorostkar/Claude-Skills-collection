---
name: test-driven-development
description: Use when practicing TDD. Covers the red-green-refactor loop, choosing the next test, designing through tests, and when TDD is and is not the right approach.
metadata:
  category: testing
  version: 1.0.0
  tags: [tdd, testing, design, red-green-refactor]
---

# Test-Driven Development

## Purpose

Use tests to drive design. TDD's value is not primarily the tests it produces — it is the pressure it puts on the design, because code that is hard to test is hard to use.

## When to Use

- Implementing logic with clear inputs and outputs.
- Fixing a bug (the failing test comes first, always).
- Working in a codebase where you do not fully understand the existing behavior.
- Designing an API you will have to live with.

## Capabilities

- The red-green-refactor cycle.
- Test selection: choosing the next test that moves the design forward.
- Outside-in (from the API) and inside-out (from the core) approaches.
- Using tests to characterize existing behavior before changing it.

## Inputs

- The requirement, small enough to express as one test.
- The existing code, if any.

## Outputs

- Code that exists because a test demanded it.
- A suite where every test failed before it passed.
- A design that is testable because it was built under test.

## Workflow

1. **Red** — Write the smallest test that fails for the right reason. Run it. Watch it fail. A test you have not seen fail is a test that may not be testing anything.
2. **Green** — Write the least code that makes it pass. Hardcoding the answer is legitimate at this stage; the next test will force generalization.
3. **Refactor** — With the test green, improve the structure. The test is your safety net, and this is the only step where you may change design without changing behavior.
4. **Choose the next test deliberately** — The next test should either force a generalization or cover a new case. A test that already passes teaches nothing.
5. **Repeat in small cycles** — Minutes, not hours. If you have been red for twenty minutes, the step was too big — revert and take a smaller one.

## Best Practices

- Watch the test fail. A test that passes before you have written the code is testing nothing, and this happens more often than anyone admits.
- If a test is hard to write, the design is wrong. That signal is TDD's main product; do not suppress it by mocking your way around the difficulty.
- Do not write five tests and then the implementation. That is not TDD; it is speculation followed by a large step.
- Triangulate: the second test is what forces you to replace `return 42` with an actual calculation. One test permits a hardcoded answer.
- TDD is poor at discovering an algorithm you do not yet understand. Spike it in a scratch file, throw the spike away, then TDD the real thing knowing where you are going.
- Never skip the refactor step. TDD without refactoring produces working code with a poor design and a suite that pins it in place.

## Examples

**The cycle, in full, on a small requirement:**

```python
# RED — the simplest failing test. Run it; watch it fail with a NameError.
def test_no_items_is_free():
    assert price(items=[]) == 0

# GREEN — the least code that passes. Yes, this is a hardcoded return.
def price(items): return 0

# RED — this test forces the hardcoding out.
def test_single_item_costs_its_price():
    assert price(items=[Item("widget", cents=250)]) == 250

# GREEN
def price(items): return sum(i.cents for i in items)

# RED — the requirement that actually has business logic in it.
def test_bulk_discount_applies_over_ten_units():
    items = [Item("widget", cents=250)] * 12
    assert price(items) == int(250 * 12 * 0.9)

# GREEN
def price(items):
    total = sum(i.cents for i in items)
    return int(total * 0.9) if len(items) > 10 else total

# REFACTOR — now that it is green, make it express the domain.
BULK_THRESHOLD = 10
BULK_MULTIPLIER = 0.9

def price(items: list[Item]) -> int:
    subtotal = sum(i.cents for i in items)
    return _apply_bulk_discount(subtotal, len(items))

def _apply_bulk_discount(subtotal: int, count: int) -> int:
    return int(subtotal * BULK_MULTIPLIER) if count > BULK_THRESHOLD else subtotal
```

Each test failed before it passed. Each piece of production code exists because a test demanded it. The design emerged from the pressure of writing the tests, not from a diagram.

## Notes

- The most valuable use of TDD is bug fixing. A failing test that reproduces the bug proves you understood it, and it becomes the regression test for free.
- TDD does not mean "test first" in the trivial sense of writing all the tests up front. The loop is minutes long, and the design feedback arrives continuously.
- TDD is a poor fit for exploratory work, UI layout, and performance tuning. Use it where correctness is the constraint, not where the shape of the answer is unknown.
