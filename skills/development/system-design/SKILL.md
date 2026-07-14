---
name: system-design
description: Use when designing a system or service before implementation. Produces a design covering data model, API surface, failure modes, scaling limits, and the trade-offs that were actually decided.
metadata:
  category: development
  version: 1.0.0
  tags: [system-design, architecture, scalability, trade-offs]
---

# System Design

## Purpose

Produce a design that is honest about its constraints: what it optimizes for, what it gives up, where it breaks, and what would have to change to take it further.

## When to Use

- Designing a new service or a significant subsystem.
- Evaluating whether an existing design will hold at the next order of magnitude.
- Choosing between architectures (monolith, services, event-driven).
- Preparing a design review or an RFC.

## Capabilities

- Requirements clarification: functional, non-functional, and the ones that are actually load-bearing.
- Capacity estimation: throughput, storage, and the arithmetic behind them.
- Data modeling and storage selection.
- API and contract design.
- Failure analysis: what happens when each dependency is slow, down, or lying.
- Scaling paths and their cost.

## Inputs

- The problem, the users, and the expected load — today and at the target.
- Latency, consistency, and availability requirements. Ranked, not all "high".
- Constraints: team size, existing stack, budget, compliance.

## Outputs

A design document with:

- Requirements and explicit non-goals.
- Capacity estimates with the arithmetic shown.
- The data model and why that store.
- The API contract.
- Failure modes and the behavior under each.
- Alternatives considered and why they were rejected.

## Workflow

1. **Clarify** — Turn vague requirements into numbers. "Fast" is not a requirement; "p99 under 200ms at 5k rps" is.
2. **Estimate** — Do the arithmetic. Requests per second, bytes per record, records per day, storage at one year. Most designs die on an estimate nobody did.
3. **Model the data** — Access patterns first, schema second. The queries you must serve determine the store you need, not the other way round.
4. **Define the contract** — API surface, idempotency, pagination, error semantics, versioning.
5. **Break it** — For each dependency: what if it is down, slow, or returns garbage? Design the degraded behavior deliberately.
6. **Find the ceiling** — Name the component that saturates first and at what load. That is the scaling path.
7. **Record the trade-offs** — What you gave up, and under what conditions you would revisit.

## Best Practices

- Start with the simplest thing that meets the stated requirements. A single database and a monolith serve more traffic than most teams will ever see.
- Every network hop is a new failure mode. Distributing a system multiplies the ways it can be down.
- Consistency requirements are usually weaker than stakeholders first claim, and occasionally far stronger. Ask what happens if a user sees stale data for five seconds.
- Caches introduce a second source of truth. Know your invalidation story before you add one.
- Design for the load you will have in a year, not in a decade. Speculative scale is a tax paid now for a benefit that may never arrive.
- The bottleneck is almost always the database, and almost always a missing index or an N+1 before it is anything architectural.

## Examples

**Capacity estimate, shown rather than asserted:**

```text
Assumption: 2M daily active users, each posting 3 events/day.
Writes  : 6M events/day = ~70/s average, ~350/s peak (5x).
Payload : ~1.2 KB/event -> 7.2 GB/day -> 2.6 TB/year raw.
Reads   : 20:1 read/write -> ~1,400/s peak.

Implication: 350 writes/s is comfortably within a single Postgres primary.
2.6 TB/year is not — partition by month and move partitions older than
90 days to object storage. Read load needs a cache in front; at 1,400/s
with a 90% hit rate the primary sees ~140 reads/s.

Ceiling: single primary saturates around 3-5k writes/s. That is ~10x
current peak, i.e. roughly two years of growth at the current rate.
```

## Notes

- Write the non-goals down. They are what stops the design from growing to cover everything and satisfying nothing.
- If two designs are close, choose the one that is easier to delete.
- A design review that produces no rejected alternative was not a design review.
