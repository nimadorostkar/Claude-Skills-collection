# FAQ

### Why 137 skills and not 400?

Because 263 candidates did not change what the agent did.

Coverage is not the goal. Every skill's description is loaded into context on every session so the agent can decide whether to read the body. A skill that adds tokens and no capability is not neutral — it is a net negative, and a library full of them is worse than a small one.

The test for inclusion is behavioral: run the task without the skill, run it with the skill, compare. No difference, no skill.

### Should I install all of them?

No. Install the two or three categories you actually work in.

The context cost of 137 descriptions is real, and a backend engineer gains nothing from having twelve finance skills loaded. Add categories when you find yourself wanting them.

### A skill isn't loading when it should. Why?

The description is not matching your phrasing. This is always the cause, and the fix is always in the description — never in the body.

Descriptions here are written in the vocabulary a user actually uses ("the page is slow and it's the database", not "database performance optimization"). If yours is a phrasing we did not anticipate, that is a bug worth reporting.

### A skill keeps loading when I don't want it.

Its description is too broad, or it overlaps a neighbour. Both are fixed by sharpening the description and adding an explicit boundary:

```yaml
description: >-
  Use when a database query is slow. ...
  Do not use for schema design from scratch — see the data-modeling skill.
```

### Will these work with agents other than Claude?

The format is a Markdown file with YAML frontmatter — nothing proprietary. Any agent with skill support can load them directly. Any agent without it can use the body as an injected briefing, or the library as a retrieval index. See [installation.md](installation.md).

### Why is there so little "best practice" advice?

Because "prefer composition over inheritance" changes nothing. The model already knows it.

What changes the output is the specific, non-obvious thing: that `noUncheckedIndexedAccess` is the flag most TypeScript codebases are missing, that a total row read as data silently doubles a sum, that a timestamp at the top of a system prompt disables prompt caching. That is what these skills contain.

### Is the finance content investment advice?

No, and every skill in that category says so explicitly.

It covers methodology — how position sizing works, why full Kelly is unusable in practice, why a backtest with survivorship bias overstates returns by several points a year. It is educational. It is not a recommendation to trade anything, and it cannot see your circumstances.

### How do you keep skills from going stale?

Imperfectly, which is why the `Notes` section of every skill is where version caveats live, and why an outdated skill is treated as a more serious bug than a missing one — an agent will follow obsolete guidance confidently.

If you find one, open an issue. Corrections to existing skills are more valuable than new skills.

### Can I use these commercially?

Yes. MIT. Use them, fork them, ship them, sell what you build with them.

### How do I contribute?

[CONTRIBUTING.md](../CONTRIBUTING.md). The short version: prove the skill changes the agent's behavior, show the before and after, and follow the template exactly.

The most valuable contributions are not new skills. They are corrections to existing ones — a `Notes` entry naming a real trap, a better example, a practice that has become outdated.

### Why is there no skill for X?

Either it did not change the agent's behavior in testing, or nobody has written it. Open an issue — if there is a real gap, that is worth knowing.
