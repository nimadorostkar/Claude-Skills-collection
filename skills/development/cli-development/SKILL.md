---
name: cli-development
description: Use when building command-line tools. Covers argument design, exit codes, streams and piping, progress output, configuration precedence, and behavior that respects the shell.
metadata:
  category: development
  version: 1.0.0
  tags: [cli, terminal, ux, tooling, unix]
---

# CLI Development

## Purpose

Build command-line tools that behave the way the shell expects: composable, scriptable, quiet by default, and honest about failure.

## When to Use

- Building a developer tool, deployment script, or internal utility with a CLI.
- Designing the argument surface of an existing tool.
- Making a tool safe to use inside pipelines and CI.

## Capabilities

- Argument and subcommand design.
- Correct use of stdout, stderr, and exit codes.
- Configuration precedence: flags, environment, config file, defaults.
- Human output versus machine output (`--json`, TTY detection).
- Progress, colour, and interactivity that degrade correctly when piped.

## Inputs

- The tasks the tool must perform and who runs it (humans, CI, both).
- Whether it will be composed with other tools.
- Whether it performs destructive operations.

## Outputs

- A command surface that is predictable and discoverable.
- Machine-readable output behind a flag.
- Exit codes that scripts can branch on.
- Help text that answers the question without a web search.

## Workflow

1. **Design the verbs** — Subcommands are verbs on nouns: `tool deploy service`, not `tool --deploy --service`. Group related operations.
2. **Separate the streams** — Results go to stdout. Everything else — progress, warnings, logs — goes to stderr. This is what makes `tool list | grep x` work.
3. **Define the exit codes** — 0 for success, 1 for a general failure, 2 for a usage error. Document any others.
4. **Set the configuration precedence** — Command-line flag beats environment variable beats config file beats default. Never surprise the user by reversing this.
5. **Detect the TTY** — Colour, spinners, and prompts only when stdout is a terminal. When piped, output is plain and non-interactive.
6. **Make destruction opt-in** — Anything irreversible requires confirmation, or `--yes` when non-interactive. `--dry-run` on anything with side effects.

## Best Practices

- Be quiet on success. A tool that prints five lines of celebration on every run is unusable in a loop.
- Provide `--json` for anything a script might parse. Parsing human output is a bug generator for everyone downstream.
- Honour `NO_COLOR` and `--no-color`. Honour `CI` by disabling interactivity.
- Long flags are self-documenting; short flags are for the ones typed constantly. Do not invent a short flag for every option.
- Read from stdin when the input argument is `-`. It costs three lines and makes the tool composable.
- Error messages state what failed, why, and what to do about it. "Error: invalid input" is not one of those.

## Examples

**Stream and exit-code discipline:**

```python
import json, sys

def main(argv: list[str]) -> int:
    args = parse_args(argv)

    try:
        results = search(args.query, limit=args.limit)
    except ConfigError as e:
        print(f"error: {e}\nhint: run `tool config init` to create a config file", file=sys.stderr)
        return 2
    except UpstreamError as e:
        print(f"error: search backend unavailable: {e}", file=sys.stderr)
        return 1

    if args.json:
        json.dump([r.to_dict() for r in results], sys.stdout)
        sys.stdout.write("\n")
    else:
        for r in results:
            print(f"{r.id}\t{r.title}")          # stdout: the result

    if not results:
        print("no matches", file=sys.stderr)     # stderr: the commentary
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

`tool search foo | head -5` works. `tool search foo --json | jq .` works. `tool search foo > /dev/null` prints nothing but the commentary. All three are the point.

## Notes

- Exiting non-zero on "no results found" is a design decision, not an obvious one. `grep` does it; most tools should not. Whatever you choose, document it.
- A `--verbose` flag that changes stdout breaks pipelines. Verbosity belongs on stderr.
- If the tool takes more than a second, print progress to stderr — but only when attached to a TTY.
