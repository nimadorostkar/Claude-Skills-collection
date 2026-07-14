# Standards

Every skill in this repository follows the same structure and the same voice. This is not aesthetic preference — a library that reads as though it came from twelve sources is a library nobody trusts, and inconsistent structure means the agent cannot rely on finding what it needs where it expects it.

## Frontmatter

```yaml
---
name: skill-name          # kebab-case, matches the directory name exactly
description: >-           # the only thing the agent sees before deciding to load
  Use when <situation>. Covers <scope>.
metadata:
  category: backend       # matches the parent directory
  version: 1.0.0          # semver; bump on any change to guidance
  tags: [api, rest, http] # 3-6, lowercase
---
```

**The description is the entire triggering mechanism.** It is loaded on every session; the body is not. A skill whose body is excellent and whose description is vague is a skill that never loads.

Write it in the user's vocabulary. A user with a slow query types "the page is slow and I think it's the database", not "database performance optimization". If the description does not contain the words they will use, the skill will not trigger.

Where a near neighbour exists, state the boundary explicitly:

> `Do not use for schema design from scratch — see the data-modeling skill.`

## The nine sections

In this order, always. No additions, no omissions.

| Section | Contains | Fails when |
| --- | --- | --- |
| **Purpose** | What this makes possible; what failure it prevents | It paraphrases the title |
| **When to Use** | Concrete situations, in the user's words | It says "when working with X" |
| **Capabilities** | The scope of what is covered | It reads as marketing |
| **Inputs** | What the skill needs to work | It is vague ("the code") |
| **Outputs** | Concrete artifacts produced | It promises "better quality" |
| **Workflow** | Numbered steps, in the order that matters | The order is arbitrary |
| **Best Practices** | Rules with consequences | It contains advice that could appear in any skill |
| **Examples** | Real code, showing the failure and the fix | It is a toy, or contains an elided `...` |
| **Notes** | The non-obvious; version caveats; the trap | It is generic |

## Voice

The reader is an agent that will follow you literally. Write instructions, not explanation.

**Direct and declarative.**

> Never use `as` to silence the compiler. It is an assertion, not a check; it lies at runtime.

Not:

> It is generally considered a good practice to be somewhat cautious about the use of type assertions, as they can potentially lead to runtime issues in certain circumstances.

**Rules, not preferences.** A best practice with no consequence attached is a sentiment.

> `set -e` alone does not catch failures inside pipelines. `pipefail` is what makes `a | b` fail when `a` does.

**Name the mistake.** The most valuable line in most skills is the one that names the specific, common way people get it wrong.

> The most common backtesting error is look-ahead bias, and it is usually accidental: using a closing price to make a decision that would have been made during the day.

**No hedging.** "Could potentially perhaps be considered" asserts nothing. Assert, or say nothing.

## Formatting

- **Headings:** `##` for the nine sections. `###` only inside a section, sparingly.
- **Lists:** a blank line before every list. Hyphens for bullets.
- **Code:** fenced, always with a language. Real code that would run.
- **Emphasis:** `**bold**` for the term being defined, in a rule. Not for shouting.
- **Emoji:** none.
- **Exclamation marks:** none.
- **Tables:** for genuine comparisons. Not as a substitute for prose.
- **Line length:** wrap naturally; do not hard-wrap at 80 columns.

## Terminology

Consistent across the library:

| Use | Not |
| --- | --- |
| skill | plugin, module, prompt |
| agent | AI, assistant, bot, the model (except when discussing the model specifically) |
| execution plan | query plan, explain output |
| trust boundary | security boundary, edge |
| idempotent | safe to retry |
| p99 | 99th percentile latency (in prose, `p99` is clearer) |

## Length

There is no target. A skill is as long as it needs to be and no longer.

In practice most land between 90 and 180 lines. Above roughly 250, the detail belongs in a `references/` file that the agent reads on demand — the main body is loaded whenever the skill triggers, so it should contain only what is always needed.

Below about 60 lines, ask whether the skill is thin enough that it should be a section of a broader one.

## Validation

`python scripts/validate.py` enforces the mechanical rules:

- Frontmatter parses; `name`, `description`, `metadata.category`, `metadata.version` present.
- `name` matches the directory name.
- `metadata.category` matches the parent directory.
- All nine sections present, in order.
- No `TODO`, `FIXME`, `XXX`, or placeholder text.
- No attribution, no source URLs, no "adapted from".
- No emoji.
- Every internal link resolves.

It runs in CI. It does not check whether the skill is any good — that is what review is for.
