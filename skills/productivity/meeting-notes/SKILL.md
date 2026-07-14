---
name: meeting-notes
description: Use when turning a meeting, call, or transcript into notes. Covers extracting decisions and actions rather than transcribing discussion, and producing something that is useful a month later.
metadata:
  category: productivity
  version: 1.0.0
  tags: [meetings, notes, summarization, transcripts, actions]
---

# Meeting Notes

## Purpose

Turn a meeting into a record of what was decided and what happens next. A transcript is not notes; nobody reads a transcript, and the value of a meeting evaporates within a week without a record of its decisions.

## When to Use

- Summarizing a meeting or a call.
- Processing a transcript or a recording.
- Producing a record of decisions for people who were not there.
- Extracting action items.

## Capabilities

- Extracting decisions, actions, and open questions.
- Distinguishing what was decided from what was discussed.
- Attribution and ownership.
- Structuring notes for a reader who was absent.

## Inputs

- The transcript, recording, or your own notes.
- The attendees and their roles.
- What the meeting was for.

## Outputs

- Decisions, stated with the reasoning.
- Actions with an owner and a date.
- Open questions with an owner.
- Enough context that someone absent can follow.

## Workflow

1. **Extract the decisions first** — What was actually decided? Not discussed, not raised, not considered — decided. This is what the meeting produced.
2. **Extract the actions, with an owner and a date** — An action with no owner will not be done. An action with no date will be done eventually, which means never.
3. **Record the open questions** — What was raised and not resolved? These are what the next meeting is for, and they are routinely lost.
4. **Capture the reasoning behind each decision** — Not the whole debate. Why this option, and what was rejected. In six months, the reasoning is the part people need.
5. **Write for someone who was not there** — They have no context. A note that says "agreed to go with Sam's approach" is useless to them and, in two months, to you.
6. **Send it the same day** — Notes sent a week later are archaeology.

## Best Practices

- The single most valuable thing in meeting notes is the list of decisions with their reasoning. Everything else is optional.
- An action item without an owner is a wish. Name a person, never a team.
- Do not transcribe the discussion. Nobody reads it, and it obscures the three sentences that matter.
- Record what was rejected and why. It stops the same option being re-proposed at the next meeting.
- If nothing was decided, say so plainly. A meeting that produced no decision is worth knowing about.
- Circulate the notes and invite corrections. The record everyone has seen and not disputed is a stronger record than the one you wrote alone.

## Examples

**Notes that are useful in six months:**

```markdown
# Platform sync — 2026-07-14

Present: Maya (chair), Sam, Aisha, Tom. Apologies: Jo.

## Decisions

**1. We will use PostgreSQL advisory locks for job deduplication, not Redis.**
Rejected Redis because it adds an operational dependency for a problem that
occurs once per night, and we have no Redis in production today. Rejected
"designate one instance" because it is a single point of failure.
Revisit if we ever need job scheduling without a database.

**2. The integration test gate ships Monday 21 July, not this Friday.**
Aisha raised that three teams still use `deploy --force` in their scripts.
Shipping Friday would break their deploys with no notice. One week's notice,
with an announcement going out today.

**3. We are NOT migrating to a new CI provider this quarter.**
Discussed at length. The cost is 3-4 weeks and the benefit is ~6 minutes per
pipeline run. Not worth it now; revisit if pipeline time exceeds 20 minutes.

## Actions

| Action                                                | Owner | Due     |
|-------------------------------------------------------|-------|---------|
| Announce the deploy gate change in #engineering        | Maya  | 14 Jul  |
| Implement advisory-lock deduplication                  | Sam   | 18 Jul  |
| Audit and remove `deploy --force` from the 3 repos     | Aisha | 18 Jul  |
| Write the ADR for the locking decision                 | Sam   | 21 Jul  |

## Open

- **Do we need job scheduling in the workers, or only in the API?** Tom raised
  this; not resolved. Tom to bring a proposal to the next sync.
- Jo was absent and owns the CI budget. Decision 3 assumes no budget pressure
  to move — Maya to confirm with Jo before Friday.
```

Someone who was not in the room can read this in ninety seconds and know exactly what happened, what they owe, and what is still open.

## Notes

- Recording what was rejected, and why, prevents the single most wasteful pattern in organizational life: re-litigating a settled decision because nobody wrote down why it was settled.
- The "open" section is what makes the next meeting productive. Without it, the next meeting rediscovers the same unresolved questions.
- Notes with an owner and a date on every action have a completion rate several times higher than notes with neither. This is not a subtle effect.
