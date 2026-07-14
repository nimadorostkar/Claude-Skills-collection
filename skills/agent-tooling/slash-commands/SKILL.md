---
name: slash-commands
description: Use when creating reusable slash commands for an agent. Covers when a command beats a skill, argument handling, composing tool calls, and writing commands that are worth typing.
metadata:
  category: agent-tooling
  version: 1.0.0
  tags: [commands, automation, workflows, shortcuts]
---

# Slash Commands

## Purpose

Turn a workflow you repeat into a command you invoke. A slash command is an explicit, user-triggered prompt — as distinct from a skill, which the model decides to load on its own.

## When to Use

- A prompt you find yourself retyping.
- A multi-step workflow with a fixed shape: review, release, triage, summarize.
- A team workflow that everyone should run the same way.
- Anything you want to invoke deliberately, rather than have the model choose.

## Capabilities

- Command authoring with arguments.
- Composing tool calls and shell commands into a workflow.
- Scoping: project-level, personal, or bundled in a plugin.
- Distinguishing command from skill.

## Inputs

- The workflow, and the variable parts of it.
- What the user will type, and what they will pass as arguments.

## Outputs

- A command file that runs the workflow reliably.
- Clear argument handling with a sensible default.

## Workflow

1. **Decide: command or skill?** — A skill is loaded when the model judges it relevant. A command is invoked when the user decides. If you want control over *when* it runs, it is a command.
2. **Name it for the action** — `/review`, `/release`, `/triage`. A verb the user would think of.
3. **Handle the arguments** — What varies between invocations? A PR number, a file, a version. Provide a default where one is sensible.
4. **Write the workflow as instructions** — The command file is a prompt. It should say what to do, in order, with what constraints.
5. **Front-load the context** — A command can run shell commands and include their output before the model reads the instructions. This is what makes a command dramatically more efficient than typing the same request.

## Best Practices

- A command that just rephrases a request is not worth the file. The value is in the workflow, the pre-gathered context, and the consistency.
- Gather the context in the command, not in the model's turns. A `/review` command that includes the diff, the CI status, and the linked issue up front saves the model three tool calls.
- Give arguments a default. `/review` with no argument should review the current branch, not fail.
- Keep the command focused on one workflow. A command with a mode flag is two commands.
- Commands are the right place for team conventions: everyone running `/release` runs the same checks in the same order.
- Document what it does at the top. Someone will run it without reading the file.

## Examples

**A command that pre-gathers its own context:**

```markdown
---
description: Review the current branch's changes against main
argument-hint: "[base-branch]"
allowed-tools: Bash(git:*), Read, Grep
---

## Context

- Base branch: ${1:-main}
- Files changed: !`git diff --stat ${1:-main}...HEAD`
- Full diff: !`git diff ${1:-main}...HEAD`
- Commits: !`git log --oneline ${1:-main}..HEAD`

## Task

Review these changes as a senior engineer would.

Report findings grouped by severity:

- **Blocking** — correctness, security, or data-loss defects.
- **Should fix** — design or performance problems that will cost more later.
- **Consider** — genuinely optional improvements.

For each finding: the file and line, what is wrong, why it matters, and the fix.

Check specifically:
- Every new branch's error path. What happens on empty, null, or hostile input?
- Anything crossing a trust boundary — is it validated?
- Would the new tests fail if the implementation were subtly wrong?

If the change is sound, say so and stop. Do not manufacture findings.
```

The diff, the commit list, and the file stats are gathered by the shell before the model reads a word. It starts with everything it needs.

**Command versus skill:**

```text
/release            -> a command. You decide when to cut a release. It must
                       never happen because the model inferred it should.

database-performance -> a skill. The model should load it whenever a query is
                       slow, without being asked. You do not want to have to
                       remember to invoke it.
```

## Notes

- The `!` prefix executes a shell command and inlines its output into the prompt before the model sees it. This is the single feature that makes commands worth writing — it eliminates the tool-call round trips.
- Restrict `allowed-tools` on any command that runs shell commands. A command with unrestricted bash access is a command that can do anything.
- If you find yourself explaining to a colleague how to phrase a request, that request should be a command.
