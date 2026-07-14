---
name: plugin-development
description: Use when packaging skills, commands, hooks, and MCP servers into a distributable plugin. Covers manifest structure, bundling, versioning, testing, and distribution through a marketplace.
metadata:
  category: agent-tooling
  version: 1.0.0
  tags: [plugins, packaging, distribution, marketplace]
---

# Plugin Development

## Purpose

Package a coherent set of agent capabilities — skills, slash commands, hooks, and MCP servers — into something another person can install in one step and that works immediately.

## When to Use

- Distributing skills or commands to a team or publicly.
- Bundling a set of related capabilities that belong together.
- Publishing to a plugin marketplace.
- Versioning and updating an existing plugin.

## Capabilities

- Plugin structure and manifest.
- Bundling skills, commands, hooks, agents, and MCP servers.
- Versioning and compatibility.
- Testing a plugin before distribution.
- Marketplace publication.

## Inputs

- The capabilities to bundle, and their coherence as a set.
- The audience and what they already have installed.
- Any external dependencies: MCP servers, API keys, binaries.

## Outputs

- A plugin that installs cleanly and works without further configuration.
- A manifest with accurate metadata.
- Documentation of what it provides and what it requires.

## Workflow

1. **Bundle around a coherent purpose** — A plugin is a set of capabilities that a specific kind of user needs together. A grab-bag of unrelated skills is a worse experience than several focused plugins.
2. **Write the manifest accurately** — Name, description, version, and what it provides. This is what users see when deciding whether to install.
3. **Declare the dependencies honestly** — If a skill requires an MCP server, an API key, or a binary on the PATH, say so prominently. A plugin that silently fails on a missing dependency will be uninstalled.
4. **Test from a clean install** — In an environment without your local configuration. Plugins that "work on my machine" are the standard failure.
5. **Version semantically** — A breaking change to a skill's behavior is a major version. Users have workflows built on it.
6. **Document what it does, not what it is** — Users care about what problems it solves.

## Best Practices

- A plugin's skills should not overlap with each other. If two skills in one plugin trigger on the same request, they will both load and cost double.
- Declare external requirements at the top of the README. The most common plugin failure is an unstated dependency.
- Provide a working example in the README — a real request and what the plugin does with it. This is worth more than a feature list.
- Do not bundle a skill that duplicates something the agent does well already. It adds cost and no capability.
- Test the uninstall path. A plugin that leaves hooks behind after removal is a bug that is hard for a user to diagnose.
- Pin any MCP server version the plugin depends on. An upstream change to a tool's schema will break your skills silently.

## Examples

**Plugin structure:**

```text
my-plugin/
  .claude-plugin/
    plugin.json           the manifest
  skills/
    review-pr/SKILL.md
    triage-issue/SKILL.md
  commands/
    standup.md            a slash command
  hooks/
    hooks.json            format-on-write
  .mcp.json               the MCP servers this plugin needs
  README.md
```

```json
{
  "name": "engineering-workflow",
  "version": "1.2.0",
  "description": "Pull-request review, issue triage, and standup summaries for teams working in GitHub and Linear.",
  "author": { "name": "Nima Dorostkar" },
  "homepage": "https://github.com/nimadorostkar/claude-skills",
  "keywords": ["code-review", "triage", "github", "linear"]
}
```

**A README that prevents the most common failure:**

```markdown
## Requirements

This plugin requires two MCP servers, which are configured automatically on
install but need authorization:

- **GitHub** — run `/mcp` and authorize. Without it, `review-pr` cannot read diffs.
- **Linear** — run `/mcp` and authorize. Without it, `triage-issue` will fail
  with "no Linear workspace".

The plugin will install successfully without these, but the skills will not work.

## Example

    > review the PR at github.com/acme/api/pull/412

The `review-pr` skill fetches the diff, reviews it for correctness, security,
and performance, and posts findings grouped by severity as review comments.
```

## Notes

- The most common plugin defect is an undeclared dependency: the author has an MCP server configured globally, so the plugin works for them and fails for everyone else. Always test in a clean profile.
- Marketplace descriptions are the plugin's only chance to be found. Include the tools and the tasks, in the words a user would search for.
- Breaking a skill's behavior without a major version bump breaks workflows built on it. Skills are an interface.
