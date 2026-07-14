---
name: agent-memory
description: Use when an agent needs state that survives a session or a context compaction. Covers what to persist, file-based memory, structuring notes for retrieval, and preventing memory from becoming stale.
metadata:
  category: agent-tooling
  version: 1.0.0
  tags: [memory, persistence, state, context, notes]
---

# Agent Memory

## Purpose

Give an agent state that outlives its context window. Anything the agent must not forget belongs in a file it can re-read — not in a conversation history that will be compacted away.

## When to Use

- A task that spans more turns than the context window holds.
- Work that continues across sessions.
- An agent that repeatedly rediscovers the same fact or repeats the same failed approach.
- Accumulating knowledge about a codebase or a domain over time.

## Capabilities

- Deciding what deserves persistence.
- File-based memory the agent reads and writes.
- Structuring notes for retrieval rather than for narrative.
- Staleness detection and pruning.

## Inputs

- The task and its expected duration.
- What has been learned that would be expensive to rediscover.
- What has been tried and failed.

## Outputs

- A memory file that survives compaction and session end.
- Notes structured so that the relevant part is findable.
- A pruning discipline so the memory does not become a stale swamp.

## Workflow

1. **Write down what would be expensive to rediscover** — File locations, API shapes, the reason an approach was abandoned, a constraint the user stated once. Not the narrative of how you got there.
2. **Write it as facts, not as a story** — "The auth middleware is in `src/mw/auth.ts` and it does not run on `/health`." Not "I looked for the auth middleware and eventually found it."
3. **Record failures explicitly** — "Tried X. It does not work because Y." This is the highest-value memory content, because without it the agent will try X again.
4. **Re-read at the start of each session** — Memory that is not read is not memory.
5. **Prune what is stale** — A note that was true three refactors ago is now a trap. Date the entries and check them.
6. **Keep it small** — This file is loaded every session. It competes with the actual work for context.

## Best Practices

- The most valuable memory is a record of what failed and why. Without it, an agent will confidently repeat a failed approach in a new session.
- Structure the file so the agent can find the relevant section without reading all of it. Headings, not prose.
- Do not persist the conversation. Persist the conclusions.
- A memory file that grows monotonically will eventually be mostly wrong. Pruning is part of the discipline, not an afterthought.
- Distinguish stable facts (architecture, conventions) from working state (what I am doing now). They have different lifetimes and belong in different sections or different files.
- Date the entries. A fact from six months ago about a fast-moving codebase is a hypothesis.

## Examples

**A memory file structured for retrieval:**

```markdown
# Working memory — orders service migration

_Last updated: 2026-06-14_

## Stable facts (verified, unlikely to change)
- Auth middleware: `src/middleware/auth.ts`. Runs on every route EXCEPT
  `/health` and `/metrics` (see the exclusion list at line 22).
- Money is `Money` (integer minor units) throughout. There is no float money
  anywhere and there must not be.
- The migration runner is `pnpm db:migrate`. It does NOT run automatically on
  deploy — this is deliberate; migrations are run manually before the deploy.

## Current task
Strangling `legacy/billing` into `src/features/billing`.
Done: invoice generation, proration.
Next: refunds.
Not started: dunning, tax.

## Tried and failed — do not repeat
- 2026-06-02: Tried to run the two billing paths in parallel and diff the
  outputs. Abandoned: the legacy path writes to the ledger as a side effect,
  so running both double-writes. Shadow mode requires a read-only ledger
  adapter, which does not exist yet.
- 2026-06-09: Tried extracting `PricingEngine` first. It depends on
  `LegacyCustomer`, which depends on half the legacy module. The dependency
  runs the wrong way; extract `Customer` first.

## Open questions for the user
- Should refunds issued before the migration remain visible in the new UI?
  (Asked 2026-06-11, not yet answered.)
```

The "tried and failed" section is what stops the next session from spending two hours rediscovering that shadow mode double-writes the ledger.

## Notes

- Without a memory of failed approaches, an agent starting a fresh session will reason its way to the same plausible-but-wrong approach it already abandoned. This is the most common and most wasteful memory failure.
- Memory and context compaction serve the same goal from different directions: compaction summarizes what happened, memory records what was concluded. Both are needed.
- If a memory file exceeds a couple of hundred lines, it has stopped being memory and become a document. Prune it or split it.
