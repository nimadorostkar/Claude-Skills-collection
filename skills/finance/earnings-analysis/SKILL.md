---
name: earnings-analysis
description: Use when analyzing an earnings report or the market's reaction to one. Covers what actually matters in the release, the reaction as information, guidance versus results, and post-earnings drift.
metadata:
  category: finance
  version: 1.0.0
  tags: [earnings, fundamentals, guidance, reaction, drift]
---

# Earnings Analysis

## Purpose

Read an earnings report for what matters, and read the market's reaction as information in its own right. A stock falling on a beat is telling you something that the beat alone does not.

## When to Use

- Analyzing a company's quarterly results.
- Interpreting an unexpected reaction to a report.
- Assessing guidance and its credibility.
- Deciding whether to hold a position through an announcement.

## Capabilities

- Reading the release: revenue quality, margins, guidance, one-time items.
- Reaction analysis: what a move against the result implies.
- Guidance assessment and management credibility.
- Post-earnings-announcement drift.
- Gap risk assessment before a report.

## Inputs

- The release, the guidance, and the call transcript.
- Consensus expectations, and — more importantly — the whisper number.
- The stock's positioning and implied move going in.

## Outputs

- What the report actually said, separated from what the headline said.
- An interpretation of the reaction.
- The implication for a position.

## Workflow

1. **Read the guidance first** — The market discounts the future. A quarter that beat, with guidance cut, is a bad report. The headline EPS number is the least important figure in the release.
2. **Check the quality of the beat** — Revenue beat, or a lower tax rate? Margin expansion, or a one-time gain? A beat driven by a buyback reducing the share count is not operating performance.
3. **Read the reaction as information** — A stock that falls on a beat means expectations were higher than the published consensus, or the guidance disappointed, or the market disbelieves something. It is information, and it is usually more reliable than your reading of the release.
4. **Assess management's credibility** — Compare this guidance with the last four. Management that guides conservatively and beats is different from management that guides optimistically and misses.
5. **Consider the drift** — Stocks that gap up on a genuine surprise have historically tended to continue drifting in that direction for weeks. This is one of the most persistent documented anomalies, and it is also a crowded one.

## Best Practices

- The headline EPS number is the least informative figure in the release. It is the most adjustable, the most gamed, and the most anticipated.
- A stock falling on a beat is the market disagreeing with you before you have finished reading. Take that seriously rather than concluding the market is wrong.
- Guidance moves stocks; the completed quarter is history. A miss with raised guidance frequently rises.
- Watch the year-over-year growth *rate*, not just the growth. Decelerating growth at a high multiple is the most reliable way to lose money on a good company.
- Holding through earnings is taking an unhedged overnight gap risk that your position sizing almost certainly did not account for. If you hold, size for the gap.
- Read the call, not the press release. The prepared remarks are marketing; the question-and-answer section is where the analysts ask what management omitted.

## Examples

**Reading past the headline:**

```text
Company reports:
  EPS         : $2.14 vs $2.05 consensus     BEAT by 4.4%
  Revenue     : $4.82B vs $4.79B consensus   BEAT by 0.6%
  Stock       : -12% after hours

The headline says "beats on both lines". The stock says otherwise. The stock
is right. What the release actually contains:

  Gross margin      : 61.2% vs 64.8% a year ago   -> 360bp of compression
  Revenue growth    : +14% YoY, decelerating from +22% and +19% in the prior
                      two quarters. The growth rate is halving.
  The EPS beat      : driven by a $0.11 benefit from a lower tax rate and a
                      buyback. Operating EPS was a MISS.
  Guidance          : next quarter revenue guided to $4.9B-$5.0B versus a
                      $5.2B consensus. A 4-6% cut.
  On the call       : management attributed margin compression to "a temporary
                      shift in customer mix" — the same phrasing used last
                      quarter, when it was also described as temporary.

The report is a miss wearing a beat's clothing: decelerating growth, compressing
margins, a below-consensus guide, and an EPS number rescued by tax and buybacks
rather than by operations.

The -12% is not an overreaction. It is a repricing of the growth rate.
```

**Gap risk, before deciding to hold through:**

```python
def earnings_gap_risk(symbol: str) -> GapRisk:
    options = option_chain(symbol, expiry=next_after_earnings(symbol))

    # The straddle price is the market's own estimate of the move.
    implied_move = straddle_price(options, atm_strike(symbol)) / spot(symbol)

    # What has actually happened, historically.
    history = past_earnings_moves(symbol, quarters=12)

    return GapRisk(
        implied_move_pct=implied_move,
        historical_median_pct=float(np.median(np.abs(history))),
        historical_max_pct=float(np.max(np.abs(history))),
        exceeded_implied_pct=float(np.mean(np.abs(history) > implied_move)),
    )

# NVDA: implied move 8.4%. Historical median 7.1%, max 24.4%.
# The move exceeded the implied move in 5 of the last 12 quarters (42%).
#
# A position sized for a 2% adverse move, held through this, is sized for a
# risk that does not exist. The relevant risk is 8%, with a tail to 24%, and
# no stop will protect against a gap — the stop executes at the open, wherever
# the open is.
```

## Notes

- A stop-loss does not protect against an earnings gap. The order executes at the next available price, which may be far below the stop. This is the specific reason holding through earnings requires different sizing, not merely more courage.
- Post-earnings-announcement drift is one of the most durable documented anomalies, but it has been heavily traded and its magnitude has declined substantially. Do not assume the historical effect size still holds.
- This is educational material about earnings analysis, not financial advice or a recommendation regarding any security.
