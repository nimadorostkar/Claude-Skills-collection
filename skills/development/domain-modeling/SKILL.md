---
name: domain-modeling
description: Use when the code's vocabulary does not match the business's. Establishes a ubiquitous language, models domain concepts as explicit types, and identifies bounded contexts.
metadata:
  category: development
  version: 1.0.0
  tags: [ddd, domain-model, ubiquitous-language, bounded-context]
---

# Domain Modeling

## Purpose

Make the code speak the business's language precisely. Most long-lived complexity comes from a mismatch between the words the business uses and the structures the code has — where "user" means four different things and none of them are named.

## When to Use

- The same concept has different names in code, in the database, and in conversation.
- A single model class is used by three subsystems that each need something different from it.
- New requirements consistently require changes in unrelated modules.
- Designing a new subsystem in a domain with real business rules.

## Capabilities

- Ubiquitous language: a shared, enforced vocabulary between code and domain experts.
- Modeling entities, value objects, and aggregates with clear invariants.
- Bounded-context identification and mapping.
- Replacing primitive obsession with domain types.
- Making illegal states unrepresentable.

## Inputs

- The domain vocabulary, ideally from the people who use it daily.
- The current model and where it hurts.
- The business rules, especially the ones that are currently enforced by convention.

## Outputs

- A glossary of terms, each with exactly one meaning.
- Domain types that carry their invariants.
- Named bounded contexts and the translation between them.

## Workflow

1. **Collect the vocabulary** — Listen to how the domain experts speak. When they say "a subscription lapses", the code should have a `lapse()` and not a `status = 3`.
2. **Find the collisions** — The same word meaning two things is the highest-value finding. "Order" in fulfilment and "Order" in billing are usually different concepts.
3. **Draw the context boundaries** — Where the meaning of a word changes, a context boundary exists. Draw it explicitly and translate at the edge.
4. **Replace primitives with types** — `Money`, `EmailAddress`, `SubscriptionId`. A type that validates on construction cannot be invalid downstream.
5. **Move invariants into the model** — If a rule is currently enforced in a controller, the model permits an invalid state. Move it.
6. **Rename ruthlessly** — Code that uses a word the business does not use is code the business cannot verify.

## Best Practices

- One word, one meaning, per context. If you need to say "billing order" to be clear, the type should be `BillingOrder`.
- A value object with no identity should be immutable and compared by value. `Money(1000, "USD")` equals `Money(1000, "USD")`.
- An aggregate is a consistency boundary. Everything inside it is transactionally consistent; everything outside it is eventually consistent. Choose the boundary deliberately.
- Never share a database table across bounded contexts. That is a hidden coupling that no interface can undo.
- Do not build a domain model for a CRUD application. If there are no invariants, a form and a table is the correct architecture.
- The glossary belongs in the repository, and disagreements about it are the most productive meetings you will have.

## Examples

**Primitive obsession versus a domain type:**

```typescript
// Before: every caller must remember the currency and the unit.
function refund(orderId: string, amount: number, currency: string) { ... }
refund("ord_1", 19.99, "USD");   // floating point money, in an unvalidated string id

// After: the types make the mistakes impossible.
class Money {
  private constructor(readonly cents: bigint, readonly currency: Currency) {}

  static of(cents: bigint, currency: Currency): Money {
    if (cents < 0n) throw new DomainError("Money cannot be negative");
    return new Money(cents, currency);
  }

  plus(other: Money): Money {
    if (other.currency !== this.currency) {
      throw new DomainError(`Cannot add ${other.currency} to ${this.currency}`);
    }
    return new Money(this.cents + other.cents, this.currency);
  }
}

function refund(orderId: OrderId, amount: Money): Refund { ... }
```

Currency mismatches and negative amounts are now compile-time or construction-time errors rather than production incidents.

## Notes

- Aggregate boundaries that are too large create lock contention; boundaries that are too small push consistency into the application layer. Start with the smallest set of objects that must change together atomically.
- Anti-corruption layers exist so that a bad upstream model does not leak into a good one. When integrating a vendor API, translate at the edge — do not let their nouns into your domain.
