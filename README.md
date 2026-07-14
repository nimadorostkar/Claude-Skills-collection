<div align="center">

# Claude Skills

**A curated library of 137 production-grade skills for Claude and other AI coding agents.**

Every skill follows one structure, speaks with one voice, and earns its place by changing what the agent does.

[Catalog](docs/catalog.md) · [Installation](#installation) · [Writing a skill](docs/authoring.md) · [Contributing](CONTRIBUTING.md)

</div>

---

## What this is

A skill is a Markdown file that an agent loads when it becomes relevant — a compact briefing that changes how the agent approaches a task. This repository contains 137 of them, spanning engineering, infrastructure, AI, documents, design, writing, and finance.

They are not prompts, and they are not documentation. A skill is loaded automatically, based on its description, and it must be specific enough to change the output. If it does not, it does not belong here.

```
skills/backend/api-design/SKILL.md   →  loaded when you say "review this endpoint"
skills/data/postgres/SKILL.md        →  loaded when you paste an EXPLAIN plan
skills/ai/rag/SKILL.md               →  loaded when a retrieval system returns bad answers
```

## Philosophy

**Specificity over breadth.** A skill that says "write clean code" changes nothing. A skill that says *"`noUncheckedIndexedAccess` is the highest-value flag most codebases are missing: it makes `arr[i]` return `T | undefined`, which is the truth"* changes the next file the agent writes.

**Every skill must alter behavior.** The test for inclusion is simple: run the task without the skill, run it with the skill, and compare. If the output is the same, the skill is deleted. This is why the library is 137 skills and not 400.

**Constraints, not preferences.** "Prefer composition" is advice. "An unlabelled arrow between two boxes conveys almost nothing" is a rule an agent can follow.

**The mistake is the content.** The most valuable line in most of these skills is the one that names the specific way people get it wrong — the timestamp at the top of a system prompt that silently disables prompt caching, the total row read as data that doubles a sum, the `waitForTimeout` that makes an entire E2E suite flaky.

**One author, one voice.** Consistent structure, consistent terminology, consistent tone. A library that reads like it was assembled from twelve sources is a library nobody trusts.

## Repository structure

```
.
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
├── categories/            One index per category, with a one-line summary of each skill
├── docs/
│   ├── catalog.md         Every skill, linked
│   ├── authoring.md       How to write a skill that triggers and works
│   ├── standards.md       The template and the style rules
│   ├── installation.md    Every installation path, in detail
│   └── faq.md
├── examples/              Worked end-to-end sessions showing skills in use
├── templates/
│   └── SKILL.md           The canonical template
├── scripts/
│   └── validate.py        The check that runs in CI
└── skills/
    ├── languages/         python, typescript, go, rust, java-kotlin, …
    ├── development/       code-review, debugging, refactoring, system-design, …
    ├── backend/           api-design, graphql, microservices, caching, …
    ├── frontend/          react, nextjs, accessibility, web-performance, …
    ├── mobile/            ios, react-native, flutter, mobile-release
    ├── devops/            kubernetes, terraform, ci-cd, observability, …
    ├── data/              postgres, database-performance, data-modeling, …
    ├── security/          secure-coding, threat-modeling, supply-chain, …
    ├── testing/           test-strategy, tdd, e2e-playwright, …
    ├── ai/                prompt-engineering, rag, agent-design, …
    ├── agent-tooling/     skill-authoring, hooks, subagents, plugins, …
    ├── finance/           position-sizing, risk-management, backtesting, …
    ├── documents/         word-documents, spreadsheets, pdf, diagrams, …
    ├── design/            visual-design, theming, ui-review, …
    ├── writing/           technical-documentation, changelog, editing, …
    ├── productivity/      deep-research, fact-checking, meeting-notes, …
    └── business/          competitive-analysis, product-analysis, …
```

## Installation

Clone the repository, then link the skills you want into your agent's skills directory.

**Everything:**

```bash
git clone https://github.com/nimadorostkar/claude-skills.git
ln -s "$(pwd)/claude-skills/skills"/*/* ~/.claude/skills/
```

**One category** — recommended. Loading 137 skill descriptions costs context on every session; most people want two or three categories.

```bash
ln -s "$(pwd)/claude-skills/skills/backend"/* ~/.claude/skills/
ln -s "$(pwd)/claude-skills/skills/data"/*    ~/.claude/skills/
```

**One skill:**

```bash
cp -r claude-skills/skills/ai/rag ~/.claude/skills/
```

**Per project** — commit the skills your team should share into the repository itself:

```bash
mkdir -p .claude/skills
cp -r ~/src/claude-skills/skills/testing/test-strategy .claude/skills/
git add .claude/skills && git commit -m "Add shared test-strategy skill"
```

See [docs/installation.md](docs/installation.md) for other agents and for project-scoped setups.

## Usage

Skills load themselves. You do not invoke them — you describe your problem, and the agent loads the skills whose descriptions match.

```
> this endpoint takes 3 seconds and I think it's the database

  → loads database-performance, postgres
  → asks for EXPLAIN (ANALYZE, BUFFERS) rather than guessing
  → identifies "Rows Removed by Filter: 8,214,502" as the finding
  → proposes a partial index matching both the filter and the sort
  → 3184ms → 1.8ms
```

```
> our RAG system keeps hallucinating

  → loads rag, llm-evaluation
  → measures retrieval recall BEFORE touching the prompt
  → 31 of 100 failures are retrieval, 6 are generation
  → prompt engineering would have addressed 6% of the problem
```

```
> review this PR

  → loads code-review, and the language skill for the diff
  → findings ranked: blocking, should fix, consider
  → each with a file, a line, a reason, and a fix
```

The mechanism is the `description` field in each skill's frontmatter. It is written in the words a user would actually use — "the page is slow and it's the database", not "database performance optimization" — which is why the skills load when they should.

## Skill structure

Every skill in this repository is identical in shape:

```markdown
---
name: skill-name
description: Use when <trigger>. Covers <scope>.
metadata:
  category: <category>
  version: 1.0.0
  tags: [...]
---

# Title

## Purpose        What this makes possible, and what failure it prevents.
## When to Use    Concrete situations, in the user's vocabulary.
## Capabilities   What the skill covers.
## Inputs         What it needs from you.
## Outputs        What you get.
## Workflow       Numbered steps. The order matters.
## Best Practices Rules, not preferences. Each one earns its line.
## Examples       Real code or a worked case. Never a toy.
## Notes          The non-obvious detail. Version caveats. The gotcha.
```

The template is in [templates/SKILL.md](templates/SKILL.md). The rules are in [docs/standards.md](docs/standards.md).

## Examples

Worked sessions showing skills in use, end to end:

- [Debugging a slow endpoint](examples/slow-endpoint.md) — `database-performance` → `postgres` → a 1,700× improvement
- [Reviewing a pull request](examples/pull-request-review.md) — `code-review` → `secure-coding`, and the finding a scanner cannot make
- [Fixing a RAG system](examples/rag-diagnosis.md) — `rag` → `llm-evaluation`, and why the prompt was not the problem

## Contributing

The bar is behavioral difference. A skill is accepted if the agent's output measurably improves when it loads, and rejected if it does not — however well written it is.

Read [CONTRIBUTING.md](CONTRIBUTING.md). In short:

1. Test the triggering, with ten real phrasings.
2. Run the task without the skill. Then with it. Show the difference.
3. Follow the template exactly. `python scripts/validate.py` must pass.
4. No filler. If a section has nothing to say, the skill is too thin.

## FAQ

**Why 137 and not 400?**
Because 263 of them did not change what the agent did. Coverage is not the goal; a skill that adds tokens and no capability is a net negative.

**Do I need all of them?**
No, and you should not install all of them. Every skill's description is loaded so the agent can decide whether to read it. Install the two or three categories you work in.

**Will these work with agents other than Claude?**
The format is a Markdown file with YAML frontmatter. Any agent that supports skills — or any system that can inject Markdown into context — can use them. The triggering mechanism is what varies. See [docs/installation.md](docs/installation.md).

**How do I stop a skill from loading when I don't want it?**
Its description is too broad. Sharpen it, or add an explicit boundary: `Do not use for X — see the y skill.` Both are covered in [docs/authoring.md](docs/authoring.md).

**Is the finance content advice?**
No. It is methodology — position sizing, backtesting, risk limits — and every skill in that category says so explicitly. It is not a recommendation to trade anything.

**How is this kept current?**
Skills rot. A confidently stated obsolete practice is worse than no skill at all. Each carries a version, and the `Notes` section is where version caveats live. See [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE). Use them, fork them, ship them.
