---
name: design-patterns
description: Use when choosing how to structure code for a recurring problem. Covers the patterns that earn their keep, the ones that usually do not, and how to recognize when a pattern is being applied for its own sake.
metadata:
  category: development
  version: 1.0.0
  tags: [design-patterns, architecture, solid, abstraction]
---

# Design Patterns

## Purpose

Apply structural patterns as solutions to problems you actually have. A pattern applied prophylactically is just indirection with a formal name.

## When to Use

- A problem recurs and the current structure requires a change in many places each time.
- Choosing between inheritance, composition, and configuration.
- Reviewing code that is heavily abstracted and hard to follow.
- Designing an extension point for third parties.

## Capabilities

- Creational: factory, builder, dependency injection.
- Structural: adapter, facade, decorator, proxy.
- Behavioral: strategy, observer, command, state machine.
- Concurrency: producer-consumer, worker pool, circuit breaker.
- Recognizing pattern misuse: the singleton-as-global, the abstract factory of one.

## Inputs

- The problem being solved and how often it recurs.
- The axis of expected change — what varies, and what stays fixed.
- Who extends the code: you, your team, or external consumers.

## Outputs

- A structure with a named rationale.
- The specific change it makes cheap, stated explicitly.

## Workflow

1. **Name the axis of variation.** A pattern buys flexibility along exactly one axis, at the cost of indirection along all of them. If you cannot name the axis, do not apply a pattern.
2. **Count the instances.** One implementation needs no strategy interface. Two might. Three definitely does.
3. **Choose the lightest structure that works.** A function passed as a parameter is a strategy. It does not need a class hierarchy.
4. **Write it concretely first.** Then extract the pattern when the second case arrives — the shape of the abstraction will be obvious rather than guessed.
5. **Justify the indirection.** If a reader must open three files to answer "what happens when I call this", the pattern is costing more than it returns.

## Best Practices

- Composition over inheritance, nearly always. Inheritance couples you to the parent's internals forever.
- Strategy, adapter, and decorator earn their keep constantly. Abstract factory and visitor rarely do outside frameworks.
- A singleton is a global variable with better manners. Use dependency injection instead — it makes the dependency visible and the code testable.
- A state machine with explicit states and transitions beats a tangle of boolean flags every time.
- Circuit breakers, retries, and timeouts are patterns too, and they are more likely to save you than any of the Gang of Four.
- Two similar pieces of code are not necessarily duplication. Deduplicating things that merely look alike couples things that change for different reasons.

## Examples

**Explicit state machine instead of boolean soup:**

```python
# Before: state is implied by three booleans, and half the combinations are invalid.
if order.is_paid and not order.is_shipped and not order.is_cancelled:
    ship(order)

# After: states are enumerated, transitions are the only way to move.
class OrderState(Enum):
    PENDING = auto()
    PAID = auto()
    SHIPPED = auto()
    CANCELLED = auto()

TRANSITIONS: dict[OrderState, set[OrderState]] = {
    OrderState.PENDING:   {OrderState.PAID, OrderState.CANCELLED},
    OrderState.PAID:      {OrderState.SHIPPED, OrderState.CANCELLED},
    OrderState.SHIPPED:   set(),
    OrderState.CANCELLED: set(),
}

def transition(order: Order, to: OrderState) -> None:
    if to not in TRANSITIONS[order.state]:
        raise InvalidTransition(f"{order.state.name} -> {to.name}")
    order.state = to
```

Invalid states are now unrepresentable, and the legal transitions are readable in one place.

## Notes

- The dependency-inversion principle is about direction, not about interfaces. An interface with exactly one implementation, created only to "follow the principle", inverts nothing.
- Facades are the most under-used pattern in large codebases: a single, small entry point to a subsystem does more for comprehensibility than any amount of internal cleanliness.
