# Installation

Skills are directories containing a `SKILL.md`. Installing one means putting that directory where your agent looks for skills.

## Claude Code

**A single skill** — copy it in:

```bash
mkdir -p ~/.claude/skills
cp -r skills/ai/rag ~/.claude/skills/
```

**A category** — symlink, so `git pull` keeps them current:

```bash
ln -s "$(pwd)/skills/backend"/* ~/.claude/skills/
ln -s "$(pwd)/skills/data"/*    ~/.claude/skills/
```

**Everything:**

```bash
ln -s "$(pwd)/skills"/*/* ~/.claude/skills/
```

Installing all 137 is possible and usually not what you want. Every skill's `description` is loaded into context so the agent can decide whether to read the body — 137 descriptions is a real cost on every session. Install the two or three categories you work in, and add more when you find yourself wanting them.

## Project-scoped

Skills committed to a repository apply to everyone who works in it, and are versioned with the code:

```bash
mkdir -p .claude/skills
cp -r ~/src/claude-skills/skills/testing/test-strategy   .claude/skills/
cp -r ~/src/claude-skills/skills/development/code-review .claude/skills/
git add .claude/skills
git commit -m "Add shared team skills"
```

This is the right place for skills that encode how *your team* works. Project-scoped skills take precedence over personal ones of the same name.

## Verifying

Ask the agent something that should trigger the skill, and check that it loads:

```
> this query is slow, here's the EXPLAIN output
```

If it does not load, the description is not matching your phrasing. That is a bug — [open an issue](https://github.com/nimadorostkar/claude-skills/issues) with the exact phrasing you used.

## Other agents

The format is a Markdown file with YAML frontmatter. Any system that can select a document by its description and inject it into context can use these.

**Agents with native skill support** — point them at the `skills/` directory, or copy the directories in. The frontmatter is standard.

**Agents without it** — the `SKILL.md` body is a self-contained briefing. Inject the relevant one into the system prompt, or expose the library as a retrieval tool the agent can search:

```python
# The description field is the retrieval target. It is written to be matched
# against a user's own phrasing, which is exactly what you want here.
skills = [parse_frontmatter(p) for p in Path("skills").glob("*/*/SKILL.md")]
index = embed([s["description"] for s in skills])

def load_skill(user_request: str) -> str | None:
    match, score = nearest(index, embed(user_request))
    return skills[match]["body"] if score > THRESHOLD else None
```

**As documentation** — the skills are readable on their own. [docs/catalog.md](catalog.md) links every one.

## Updating

```bash
cd claude-skills && git pull
```

Symlinked skills update immediately. Copied skills do not — re-copy them, or use symlinks.

Check [CHANGELOG.md](../CHANGELOG.md) before updating across a major version. A change to a skill's *guidance* is a breaking change for any workflow built on it, and it is versioned as one.

## Removing

```bash
rm ~/.claude/skills/rag           # a copied skill
unlink ~/.claude/skills/postgres  # a symlinked one
```
