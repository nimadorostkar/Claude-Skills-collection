---
name: skill-authoring
description: Use when writing a new skill for an AI agent. Covers scoping, description writing for reliable triggering, progressive disclosure, and the difference between a skill and a prompt.
metadata:
  category: agent-tooling
  version: 1.0.0
  tags: [skills, authoring, agents, prompting]
---

# Skill Authoring

## Purpose

Write a skill that loads at the right time and materially changes the agent's behavior when it does. A skill that never triggers is dead weight; a skill that triggers constantly is a system prompt with extra steps.

## When to Use

- Creating a new skill.
- A skill that does not activate when it should, or activates when it should not.
- Converting a recurring prompt into a reusable capability.
- Reviewing a skill before publishing it.

## Capabilities

- Scoping: what belongs in a skill and what does not.
- Description writing, which is what determines triggering.
- Structuring the body for an agent to act on.
- Progressive disclosure through supporting files.
- Testing that the skill triggers on real requests.

## Inputs

- The capability the skill should provide.
- The requests that should trigger it, phrased as a user would phrase them.
- The requests that should *not* trigger it.

## Outputs

- A `SKILL.md` with valid frontmatter and an actionable body.
- A description that triggers reliably on the intended requests.
- Supporting files for detail that is not always needed.

## Workflow

1. **Scope it to one capability** — A skill that covers "backend development" is too broad to trigger precisely and too shallow to be useful. A skill about API design is neither.
2. **Write the description last, and carefully** — It is the only part the agent sees before deciding whether to load the skill. It must state what the skill does *and* when to use it, using the words a user would actually use.
3. **Write the body as instructions, not as an essay** — The agent will act on it. Concrete steps, explicit constraints, worked examples. Prose about the philosophy of the domain is not actionable.
4. **Move detail into supporting files** — The main file is loaded whenever the skill triggers, so it should be the part that is always needed. Reference material goes in adjacent files the agent reads on demand.
5. **Test the triggering** — With real phrasings, including the ones that should *not* trigger it. A skill that fires on every mention of "code" is a nuisance.

## Best Practices

- The description is the skill's entire interface. Include the domain terms, the tools, and the user-facing verbs — a user asking to "make the query faster" will not say "database performance optimization".
- Name the negative cases in the description when there is a near neighbor: "Use for API design. Do not use for GraphQL schema design — see the graphql skill."
- A skill that only restates what the model already does well adds tokens and no capability. The test is whether behavior changes when it loads.
- Keep the main body focused. If it exceeds roughly 500 lines, the detail belongs in supporting files.
- Worked examples do more than instructions. One good example of the output shape is worth three paragraphs describing it.
- Write the constraints as constraints. "Prefer X" is advice; "Never do Y; always do Z" is a rule the agent will follow.

## Examples

**A description that triggers, and one that does not:**

```yaml
# Too vague: what is a "database helper"? A user will never phrase a request
# in a way that matches this.
description: A helpful skill for database stuff.

# Precise, with the user's own vocabulary and an explicit boundary.
description: >
  Use when a database query is slow or a table needs an index. Covers reading
  EXPLAIN output, composite and partial index design, N+1 detection, and lock
  contention. Trigger on "slow query", "add an index", "the page is slow and
  it's the database", or a pasted EXPLAIN plan. Do not use for schema design
  from scratch — see the data-modeling skill.
```

**Progressive disclosure — the main file stays small:**

```text
skills/database-performance/
  SKILL.md                    ~200 lines, always loaded when triggered
  references/
    explain-plans.md          read only when analyzing a plan
    index-types.md            read only when choosing an index type
    lock-modes.md             read only when diagnosing contention
  scripts/
    slow_query_report.py      executed, not read into context
```

In the body: "For the meaning of each node type in an execution plan, read `references/explain-plans.md`." The agent loads it when the task requires it, and not otherwise.

**Testing that it triggers:**

```text
Should trigger:
  "this endpoint takes 3 seconds and I think it's the database"    -> yes
  "add an index to the orders table"                               -> yes
  "why is this query slow"                                         -> yes
  [pastes an EXPLAIN ANALYZE output with no question]              -> yes

Should NOT trigger:
  "design a schema for a booking system"      -> data-modeling
  "the frontend feels slow"                   -> web-performance
  "write a SQL query to find duplicates"      -> sql
```

## Notes

- Triggering is determined entirely by the description. If a skill is not loading, the fix is always in the description — never in the body.
- The most common authoring mistake is writing the skill as documentation for a human. The reader is an agent that will follow instructions literally; write instructions, not explanation.
- A skill with no constraints and no examples rarely changes behavior. The value is in the specifics.
