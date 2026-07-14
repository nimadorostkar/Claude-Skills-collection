---
name: architecture-decisions
description: Use when a significant technical decision needs to be recorded. Produces Architecture Decision Records that capture context, options, the decision, and its consequences — so the reasoning survives the people who made it.
metadata:
  category: development
  version: 1.0.0
  tags: [adr, documentation, architecture, decision-record]
---

# Architecture Decisions

## Purpose

Record why a decision was made, not just what was decided. Code shows the what. The context, the alternatives, and the constraints that made the choice correct at the time are otherwise lost within months.

## When to Use

- Choosing a database, framework, protocol, or vendor.
- Adopting or abandoning an architectural pattern.
- Making a decision that will be expensive to reverse.
- Revisiting a decision someone made and nobody can explain.

## Capabilities

- ADR authoring in a consistent, greppable format.
- Options analysis with honest trade-offs.
- Superseding and amending existing decisions without rewriting history.

## Inputs

- The decision to be made and the forces acting on it.
- The realistic options, including "do nothing".
- Constraints: team, time, budget, compliance, existing systems.

## Outputs

A numbered ADR in `docs/adr/NNNN-short-title.md` with:

- Status: proposed, accepted, superseded by NNNN.
- Context: the situation and the forces, written so a new hire understands them.
- Decision: what was chosen, in the active voice.
- Consequences: what becomes easier, what becomes harder, what is now hard to reverse.

## Workflow

1. **State the forces** — What is pushing on this decision? Latency, cost, team familiarity, compliance, an existing commitment. If there are no forces, there is no decision to record.
2. **List real options** — Including the status quo. An ADR with one option is a justification, not a decision.
3. **Evaluate against the forces** — Each option, against each force. The trade-offs should be visible in the table.
4. **Decide and state it plainly** — "We will use PostgreSQL." Not "PostgreSQL was considered favorably."
5. **Write the consequences honestly** — Especially the negative ones. An ADR with only upsides is marketing.
6. **Never delete an ADR** — Supersede it. The old reasoning is what explains the old code.

## Best Practices

- One decision per record. If the title needs "and", split it.
- Write for someone who joins in two years and has none of your context.
- Include the numbers that drove the decision. "Cheaper" is not a reason; "$400/month vs $3,100/month at our volume" is.
- Record decisions you rejected loudly, especially the popular ones. The next person will ask "why not Kafka?" — answer it once, in writing.
- Keep them in the repository, in version control, next to the code they govern.
- Status changes are edits to the old ADR; the reasoning is never rewritten.

## Examples

```markdown
# 0007. Use Postgres advisory locks for job deduplication

- Status: Accepted
- Date: 2025-03-11
- Deciders: platform team

## Context

Scheduled jobs run on three application instances. Each instance's cron
fires independently, so a nightly reconciliation job runs three times.
Two of the three runs are wasted work; occasionally they interleave and
double-write ledger entries.

We already run Postgres 15 and have no Redis or Zookeeper in production.
Adding one introduces a new operational dependency for a problem that
occurs once per night.

## Options

| Option                     | Correctness | New infra | Ops cost |
|----------------------------|-------------|-----------|----------|
| Postgres advisory lock     | Strong      | None      | None     |
| Redis SETNX lock           | Strong      | Redis     | Moderate |
| Leader election (Raft lib) | Strong      | None      | High     |
| Single designated instance | Weak (SPOF) | None      | Low      |

## Decision

We will use Postgres transaction-level advisory locks, keyed by job name,
acquired at the start of each scheduled run. An instance that cannot
acquire the lock exits immediately.

## Consequences

- No new infrastructure; the lock is released automatically if an instance
  dies, because it is tied to the transaction.
- Job scheduling now depends on Postgres availability. If Postgres is down,
  no jobs run — which is already true, since every job writes to it.
- This does not generalize to jobs that must run without a database. If we
  add such a job, this decision must be revisited.
```

## Notes

- ADRs are cheap to write and expensive to skip. The cost of the missing one is a six-month argument two years from now.
- If a decision is reversed, write a new ADR that supersedes the old one and explain what changed. "We were wrong" is a perfectly good context section.
