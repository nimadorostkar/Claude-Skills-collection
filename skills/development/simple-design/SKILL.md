---
name: simple-design
description: Use when code has grown hard to hold in your head. Applies complexity limits, dependency reduction, and encapsulation to bring functions and modules back under a readable ceiling.
metadata:
  category: development
  version: 1.0.0
  tags: [simplicity, complexity, cognitive-load, encapsulation]
---

# Simple Design

## Purpose

Keep code within the limits of human working memory. Complexity is not measured by line count but by how many things you must hold in your head at once to be confident a change is correct.

## When to Use

- A function or module has become hard to reason about.
- Reviewers keep missing defects in a particular file.
- A change in one place keeps breaking something in another.
- Deciding whether an abstraction is worth its indirection.

## Capabilities

- Cyclomatic and cognitive complexity measurement and reduction.
- Dependency counting and reduction at the function and module level.
- Encapsulation: making the number of things a caller must know as small as possible.
- Guard-clause restructuring to flatten nesting.
- Identifying the abstraction that removes the most conditionals.

## Inputs

- The code and the reason it is hard: too long, too nested, too many dependencies, too many states.
- Complexity metrics from a linter, if available.

## Outputs

- Functions that fit on a screen and have one reason to exist.
- Modules with a small public surface and a large private interior.
- A stated limit the team agrees to enforce.

## Workflow

1. **Measure, do not guess** — Cyclomatic complexity per function, dependency count per module. Find the actual outliers.
2. **Flatten first** — Replace nested conditionals with guard clauses. Most deeply nested code is shallow logic wearing a costume.
3. **Reduce the inputs** — A function taking seven parameters is describing a missing type. Introduce it.
4. **Shrink the public surface** — Everything not needed by a caller becomes private. A module with three public functions is comprehensible regardless of its size.
5. **Delete** — The simplest code is the code that is not there. Remove unused options, flags, and abstractions built for a future that did not arrive.
6. **Set the ceiling** — Agree a limit (for example, cyclomatic complexity of 7) and enforce it in the linter, so this does not have to happen again.

## Best Practices

- A function should fit in one screen, without scrolling, at a normal font size. This is an arbitrary limit that works.
- Every level of nesting doubles the states a reader must track. Guard clauses and early returns are the cheapest complexity reduction available.
- Boolean parameters are complexity in disguise: `render(true, false, true)` is unreadable. Use named arguments or separate functions.
- The number of things a caller must know to use your module correctly is its true complexity. Options with subtle interactions are worse than more functions.
- Duplication is cheaper than the wrong abstraction. Wait for the third occurrence.
- Comments explaining what the code does are a signal the code should be clearer. Comments explaining why are permanent and valuable.

## Examples

**Guard clauses instead of nesting:**

```javascript
// Before: cyclomatic complexity 8, four levels of nesting.
function processOrder(order) {
  if (order) {
    if (order.items.length > 0) {
      if (order.customer.isActive) {
        if (inventory.canFulfil(order)) {
          return fulfil(order);
        } else {
          return backorder(order);
        }
      } else {
        throw new Error("inactive customer");
      }
    } else {
      throw new Error("empty order");
    }
  } else {
    throw new Error("no order");
  }
}

// After: complexity 4, one level of nesting, failure conditions read as a list.
function processOrder(order) {
  if (!order) throw new DomainError("no order");
  if (order.items.length === 0) throw new DomainError("empty order");
  if (!order.customer.isActive) throw new DomainError("inactive customer");

  return inventory.canFulfil(order) ? fulfil(order) : backorder(order);
}
```

## Notes

- Cognitive complexity (as measured by SonarQube and similar) penalizes nesting more heavily than cyclomatic complexity does, and correlates better with what humans find hard. Prefer it when you have a choice.
- A module that is 2,000 lines but exposes four functions with no shared mutable state is simpler than four 500-line modules that reach into each other.
- Simplicity is not a synonym for fewer lines. `a?.b?.c ?? d` and a four-line `if` may have identical complexity; choose the one your team reads faster.
