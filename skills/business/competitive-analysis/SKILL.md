---
name: competitive-analysis
description: Use when analyzing competitors. Covers gathering evidence rather than opinion, positioning and pricing analysis, identifying real differentiation, and producing a conclusion that changes a decision.
metadata:
  category: business
  version: 1.0.0
  tags: [competitive, market, positioning, pricing, strategy]
---

# Competitive Analysis

## Purpose

Understand what competitors actually do, as opposed to what they say, and turn that into a decision. A feature-comparison table is not an analysis; it is a table.

## When to Use

- Entering a market or evaluating a new segment.
- Positioning or repositioning a product.
- Pricing decisions.
- Responding to a competitor's move.

## Capabilities

- Evidence gathering: product, pricing, positioning, customers.
- Positioning-map construction.
- Pricing and packaging analysis.
- Identifying real differentiation versus claimed differentiation.
- Turning findings into a decision.

## Inputs

- The competitors, including the non-obvious ones (the spreadsheet, the incumbent process, doing nothing).
- Your own product and position, honestly assessed.
- The decision this analysis informs.

## Outputs

- What each competitor actually offers and to whom.
- Where the market is crowded and where it is not.
- A recommendation that changes something.

## Workflow

1. **Define the competitive set honestly** — Including the substitutes. For most B2B products, the largest competitor is a spreadsheet and the status quo, and they are usually left off the list.
2. **Gather evidence, not marketing** — Sign up. Use the product. Read the documentation and the changelog — the changelog tells you what they actually build, as opposed to what they advertise. Read the reviews, especially the three-star ones, which are the honest ones.
3. **Map the positioning** — Two axes that matter to buyers. Where is everyone? The empty quadrant is either an opportunity or a place people have tried and failed.
4. **Analyze the pricing structure, not the number** — What do they charge for, and what does that reveal about who they think their customer is? Per-seat pricing and usage-based pricing target different buyers.
5. **Separate claimed differentiation from real** — Everyone claims to be easy to use and to have great support. What is actually different, and is it something a buyer would pay for?
6. **Reach a conclusion** — An analysis that ends in a table has not concluded anything.

## Best Practices

- A feature comparison table is the least useful output of competitive analysis. Buyers do not choose on feature count, and a table full of green ticks is a table you constructed to win.
- Read the three-star reviews. Five-star reviews are enthusiasm, one-star reviews are usually a support incident, and three-star reviews are the honest assessment of a real user.
- The changelog is more informative than the website. It reveals what a company actually invests in, and where their roadmap is going, months before they announce it.
- Pricing structure reveals strategy. A move from per-seat to usage-based pricing is a company changing who it sells to.
- The status quo is a competitor, and usually the strongest one. "They will keep using the spreadsheet" is the most likely outcome and it belongs in the analysis.
- If the analysis does not change a decision, it was not worth doing.

## Examples

**An analysis that reaches a conclusion:**

```markdown
## Competitive set

| Competitor        | Actual positioning                    | Evidence                        |
|-------------------|---------------------------------------|---------------------------------|
| Acme              | Enterprise, top-down, procurement-led | 12-month contracts, no self-serve, "book a demo" only |
| Bolt              | Bottom-up, developer-first            | Free tier, API-first docs, no sales team visible |
| **Spreadsheets**  | **The actual incumbent**              | **Mentioned in 60% of the reviews we read as "what we used before" — and in 15% as "what we went back to"** |
| Doing nothing     | The default                           | — |

## What the evidence says (not the marketing)

**Acme** — signed up via a demo request. Time to first value: 3 weeks, requiring
an implementation call. Their changelog shows 80% of releases in the last year
were compliance and admin features (SSO, audit logs, SCIM). They are building
for procurement, not for users.

**Bolt** — signed up in 4 minutes. Excellent API documentation. But their
changelog shows almost nothing shipped in the core workflow for 8 months; they
are building integrations. Their three-star reviews consistently say the same
thing: "great API, but the UI is unusable for our non-technical team."

## Positioning map

           technical buyer
                  |
          Bolt    |
                  |
  self-serve -----+----- sales-led
                  |
                  |    Acme
           business buyer

The empty quadrant — self-serve, business buyer — is where the spreadsheet users
are. That is not a coincidence, and it is not obviously an opportunity: it may be
empty because that buyer will not adopt a tool without being sold to.

## Pricing

Acme: $40/seat/month, annual, minimum 25 seats. Floor: $12k/year.
Bolt : usage-based, free to ~$200/month for a typical team.

The gap between $2,400/year and $12,000/year is where a business-buyer,
self-serve product would sit. Nobody is there.

## Conclusion — and the decision it changes

Do NOT build the enterprise admin features on the roadmap for Q3. That is
competing with Acme on the axis they have spent two years and a sales team
building. We will lose.

The defensible position is self-serve for the business buyer, priced between
the two — which is exactly where our current users came from (60% from
spreadsheets, per our own onboarding survey).

The risk, stated honestly: the quadrant may be empty because that buyer does not
self-serve. Test it before committing the quarter — a $99/month tier with no
sales contact, measured on activation, would answer the question in six weeks
for a fraction of the cost of building the wrong thing.
```

## Notes

- The changelog is genuinely the highest-signal public artifact a competitor produces. It is written for existing customers, not prospects, and it therefore tells the truth about where engineering time goes.
- An empty quadrant on a positioning map is not automatically an opportunity. Ask why it is empty before celebrating it — sometimes the answer is that people have tried.
- The status quo being the largest competitor is true for most products and is almost never in the analysis. It is why "we lost to no decision" is the most common outcome in B2B sales.
