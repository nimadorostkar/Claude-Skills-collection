# Contributing

The bar for inclusion is a single question: **does the agent's output measurably improve when this skill loads?**

A skill that is well written, accurate, comprehensive, and does not change what the agent does is rejected. Skills are not free — every description is loaded into context so the agent can decide whether to read the body. A skill that adds tokens and no capability makes the library worse.

## Before you write anything

Run the task **without** a skill. Note what the agent does, and what it gets wrong. That gap is the skill. If there is no gap, there is no skill.

This step is not optional and it is the one people skip. Most rejected contributions are accurate documents about a topic the model already handles well.

## The process

1. **Establish the baseline.** Run five realistic requests in the skill's domain, with no skill loaded. Record the output.
2. **Write the skill**, following [templates/SKILL.md](templates/SKILL.md) exactly.
3. **Test the triggering.** Ten phrasings that *should* load it, five that should not. If fewer than eight of ten trigger, the description is wrong — fix it before anything else. Content quality is irrelevant if the skill never loads.
4. **Run the baseline requests again**, with the skill loaded. Show the difference in the pull request.
5. **Validate.** `python scripts/validate.py` must pass with no errors.
6. **Open the PR** with the before/after evidence.

## What gets accepted

- A skill that encodes something specific and non-obvious, that the model gets wrong without it.
- A skill that enforces a discipline the model will otherwise skip — measuring before optimizing, reproducing before fixing, validating before trusting.
- A skill whose `Notes` section contains at least one thing that would surprise a competent practitioner.

## What gets rejected

- **Restating what the model already does.** "Write tests for your code" is not a skill.
- **A description nobody would trigger.** "Comprehensive methodology for validating service contracts" contains none of the words a user would type.
- **Filler.** A `Best Practices` section of generic advice, a `Purpose` that paraphrases the title, an `Examples` section with a toy example.
- **Overlap.** If two skills load on the same request, they will both load and possibly contradict each other. Sharpen the boundary or merge them.
- **Outdated practice, confidently stated.** Worse than no skill, because the agent will follow it.
- **Sources, credits, or attribution inside a skill.** Skills are instructions, not essays. Cite in `Notes` only where a version or a standard genuinely matters.

## Style

Read [docs/standards.md](docs/standards.md) in full before writing. The short version:

- **Sections:** all nine, in order, always. No extras.
- **Voice:** direct and declarative. Instructions, not explanation. The reader is an agent that will follow you literally.
- **Best Practices:** rules with consequences. "Never `git push --force` to a shared branch" — not "be careful with force pushes".
- **Examples:** real code that would run. A `# ...` where the hard part should be is a failing example.
- **Notes:** the non-obvious. Version caveats, the trap, the thing that catches everyone. If you have nothing surprising to say, you may not understand the topic well enough to write about it.
- **No emoji.** No exclamation marks. No "Let's dive in".
- **Line length:** wrap prose at a natural width; do not hard-wrap at 80.

## Editing an existing skill

Improvements to existing skills are more valuable than new ones. Particularly welcome:

- A `Notes` entry that names a real trap.
- A better example — one that shows the failure, not just the success.
- Removing a practice that has become outdated.
- Sharpening a description that triggers unreliably.

State in the PR what changed and why. For a behavioral change to a skill's guidance, show the before/after as you would for a new skill.

## Adding a category

Do not, unless you are contributing at least four skills that genuinely do not fit an existing one. A category with two skills is two skills in the wrong place.

## Reporting a skill that does not work

Open an issue with:

- The request you made, verbatim.
- Whether the skill loaded.
- What the agent did, and what it should have done.

A skill that does not trigger is a bug. A skill that triggers and gives bad advice is a more serious one.
