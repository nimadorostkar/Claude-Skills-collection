---
name: deep-research
description: Use when researching a question that requires multiple sources. Covers question decomposition, source evaluation, tracking what is known versus assumed, and producing a synthesis with honest confidence levels.
metadata:
  category: productivity
  version: 1.0.0
  tags: [research, sources, synthesis, evidence, verification]
---

# Deep Research

## Purpose

Answer a question properly, from sources, with an honest account of what is established and what is not. The failure mode is a confident synthesis that reads well and rests on three blog posts that all cite the same missing original.

## When to Use

- A question that cannot be answered from one source.
- Comparing options where the marketing material is the only easily available information.
- Establishing what is actually known about a contested question.
- Producing a briefing someone will act on.

## Capabilities

- Question decomposition into answerable sub-questions.
- Source evaluation: primary versus secondary, independence, recency, incentive.
- Tracking claims against evidence.
- Synthesis with explicit confidence.
- Identifying what is not known.

## Inputs

- The question, sharpened until it is answerable.
- The decision it informs — this determines how much rigour is warranted.
- Time available.

## Outputs

- An answer, with confidence stated.
- Sources, cited, that were actually read.
- An explicit list of what could not be established.

## Workflow

1. **Sharpen the question** — "Is Kubernetes good?" is unanswerable. "For a team of six running four services with no dedicated ops engineer, does Kubernetes reduce or increase operational burden compared with a managed container service?" is answerable, and the answer is useful.
2. **Decompose it** — Into sub-questions that each have a findable answer. The decomposition is most of the work.
3. **Find primary sources** — The paper, the documentation, the filing, the original benchmark. Not the blog post summarizing the blog post summarizing it.
4. **Check for independence** — Six sources that all cite the same original are one source. This is the most common way a false claim becomes "well established".
5. **Track claim to evidence** — Every assertion in the output must be traceable to a source you read, or marked as an inference.
6. **State what you could not establish** — This is the most valuable part of the output and it is nearly always omitted.

## Best Practices

- Six articles citing the same study are one piece of evidence, not six. Trace every claim to its origin before counting it.
- The absence of evidence is a finding. "I could not find any independent benchmark of this claim" is genuinely useful and is almost never reported.
- Check the incentive of the source. A vendor's benchmark showing their product winning is not evidence; it is marketing with numbers.
- Recency matters differently by field. A 2019 paper on transformer architectures is ancient; a 2019 paper on distributed consensus is current.
- Distinguish what you found from what you inferred. Both are legitimate; conflating them is not.
- If the research changes your view, say so. Research that confirms the original hypothesis every time is not research.

## Examples

**Decomposition and honest synthesis:**

```markdown
## Question
Should a six-person team with four services and no dedicated ops engineer
adopt Kubernetes, or use a managed container service?

## Sub-questions
1. What is the operational burden of a managed Kubernetes cluster, measured
   rather than asserted?
2. What capabilities does Kubernetes provide that a managed container service
   does not, and does this team need them?
3. What is the cost difference at this scale?
4. What is the migration cost if the initial choice turns out to be wrong?

## Findings

**1. Operational burden — MODERATE CONFIDENCE**

Managed Kubernetes removes control-plane operation but not cluster operation:
upgrades, node management, ingress, certificates, and RBAC remain. Public
accounts from teams of this size consistently report 0.25-0.5 FTE of ongoing
maintenance [1][2][4].

Caveat: these are self-reported, from teams who chose to write about it, and
that is a self-selected population. Teams for whom it went smoothly may be
less likely to publish. Treat 0.25-0.5 FTE as an upper-middle estimate, not a
median.

**2. Capabilities — HIGH CONFIDENCE**

Kubernetes provides multi-tenancy, sophisticated scheduling, and a large
ecosystem. For four stateless services with no bin-packing requirement, none
of these is load-bearing. [Verified against the team's actual requirements
document.]

**3. Cost — HIGH CONFIDENCE**

Managed Kubernetes: ~$73/month control plane + nodes. A managed container
service at this scale: comparable compute cost, no control-plane fee.
The difference is not material. Cost is not a deciding factor.

**4. Migration cost — LOW CONFIDENCE**

I could not find good data on the cost of migrating from a managed container
service TO Kubernetes later. Anecdotally it is described as "a few weeks", but
I found no account with enough detail to verify. This is the weakest part of
the analysis and it matters, because it is the argument for adopting
Kubernetes pre-emptively.

## Conclusion

The evidence supports the managed container service for this team: the
capabilities that justify Kubernetes are not needed, cost is neutral, and the
operational burden is real and falls on a team with no one to absorb it.

The one argument I cannot rebut is "we will need Kubernetes later and migrating
will be expensive" — because I could not establish the migration cost. If that
number turned out to be large, the conclusion could change.

## Sources
[1] ... (primary, read in full)
[2] ... (primary)
[3] NOT USED — a vendor blog post; its "independent benchmark" is a link to
    its own marketing page.
[4] ...
```

## Notes

- The "what I could not establish" section is what distinguishes research from advocacy. It is also the section that a reader who disagrees will go to first, and having it there is what makes the rest credible.
- Source [3] in the example — a vendor citing its own marketing as an independent benchmark — is extremely common. Always follow the citation.
- Self-selection bias in published accounts is pervasive and rarely acknowledged. People write about the migration that was hard, not the one that was fine.
