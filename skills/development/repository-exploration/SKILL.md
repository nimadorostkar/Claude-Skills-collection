---
name: repository-exploration
description: Use when orienting in an unfamiliar codebase. Produces a map of the architecture, entry points, data flow, conventions, and the parts most likely to surprise you — before any code is changed.
metadata:
  category: development
  version: 1.0.0
  tags: [onboarding, codebase, exploration, architecture]
---

# Repository Exploration

## Purpose

Build an accurate mental model of an unfamiliar codebase quickly, so the first change you make fits the system instead of fighting it.

## When to Use

- Joining a project or inheriting a service.
- Before making a first change to a repository you do not know.
- Auditing a codebase before acquisition, handover, or a major decision.
- Writing or refreshing a `CLAUDE.md` / onboarding document.

## Capabilities

- Entry-point discovery and request-path tracing.
- Dependency and module mapping.
- Convention detection: how this codebase does errors, config, tests, logging.
- Identification of hotspots: files with the highest churn and the most authors.
- Detection of dead code, duplicated logic, and abandoned migrations.

## Inputs

- The repository, with full git history.
- Build and run instructions, if they exist.
- Any existing documentation, treated as a hypothesis rather than fact.

## Outputs

- A map: entry points, layers, data stores, external dependencies.
- The conventions a new change must follow.
- A list of the riskiest areas and why.
- Concrete questions that the code cannot answer.

## Workflow

1. **Read the boundaries first** — `README`, build files, CI config, `Dockerfile`, deployment manifests. These tell you what runs, how, and against what.
2. **Find the entry points** — HTTP routes, CLI commands, queue consumers, cron entries, `main` functions. Everything else is reachable from one of them.
3. **Trace one request end to end** — Pick the most representative operation and follow it from entry to data store and back. This single trace teaches you the layering, the error convention, and the persistence pattern at once.
4. **Detect the conventions** — Read three files from the same layer. What is common is the convention; what is unique is either newer, older, or a mistake.
5. **Find the churn** — `git log --format=%an --name-only` aggregated by file. High churn plus many authors marks the code that will be hardest and most important to understand.
6. **Run the tests** — What they cover tells you what the team is afraid of breaking.
7. **Write it down** — A map that lives in the repository, so nobody has to do this again.

## Best Practices

- Do not read the code alphabetically. Read it along the path of a real request.
- Existing documentation is a claim, not evidence. Verify it against the code before repeating it.
- The test suite is the most honest documentation in most repositories.
- Look for the seams — where the codebase changes style abruptly is usually where a rewrite, an acquisition, or a departed engineer left a boundary.
- Note what is missing: no tests around payments, no timeouts on outbound calls, no migrations directory. Absences are findings.

## Examples

**Churn analysis to find the load-bearing files:**

```bash
# Files changed most often in the last year, with author counts.
git log --since="1 year ago" --name-only --format="%an" \
  | awk 'NF' \
  | paste - - \
  | sort -k2 \
  | awk '{files[$2]++; authors[$2 " " $1]=1} END {for (f in files) print files[f], f}' \
  | sort -rn | head -20
```

**A useful output map:**

```markdown
## Entry points
- `cmd/api/main.go`      — HTTP API, 41 routes, chi router
- `cmd/worker/main.go`   — consumes 4 SQS queues
- `cmd/migrate/main.go`  — goose migrations

## Request path (POST /orders)
handler -> validation (go-playground/validator) -> service.OrderService
  -> repo.OrderRepo (pgx) -> outbox table -> worker publishes to SQS

## Conventions
- Errors wrapped with fmt.Errorf("...: %w", err); sentinel errors in errs/
- Config via envconfig struct in internal/config; no config files
- Tests: table-driven, testcontainers for repo tests

## Risks
- internal/pricing: 3,100 lines, 9 authors, 140 commits this year, no tests
- No timeouts on the calls to the tax vendor in internal/tax/client.go
```

## Notes

- Aim to produce the map before making the first change, and to have it reviewed by someone who knows the system. Their corrections are the fastest onboarding available.
- If the repository has a `CLAUDE.md` or equivalent agent instructions file, read it first — and update it with what you learn.
