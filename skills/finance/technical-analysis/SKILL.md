---
name: technical-analysis
description: Use when analyzing price and volume structure. Covers trend identification, support and resistance, volume confirmation, moving-average structure, and the limits of what chart analysis can tell you.
metadata:
  category: finance
  version: 1.0.0
  tags: [technical-analysis, charts, trend, volume, indicators]
---

# Technical Analysis

## Purpose

Read price and volume structure to characterize a trend and identify where a thesis would be proven wrong. Technical analysis describes what price is doing; it does not predict what it will do, and treating it as prediction is where practitioners lose money.

## When to Use

- Assessing whether an instrument is trending, ranging, or breaking down.
- Identifying levels for entry, stop, and target.
- Confirming or contradicting a fundamental thesis with price action.
- Reviewing a chart before a trade.

## Capabilities

- Trend structure: higher highs and lows, moving-average alignment.
- Support and resistance identification.
- Volume analysis and confirmation.
- Relative strength against a benchmark.
- Common patterns and their actual, unimpressive reliability.

## Inputs

- Price and volume history, in sufficient length to see the structure.
- The benchmark, for relative strength.
- The time frame that matches the intended holding period.

## Outputs

- A characterization of the trend and its stage.
- Levels: where the structure breaks, where resistance sits.
- An explicit invalidation point.

## Workflow

1. **Establish the trend, on the right time frame** — Higher highs and higher lows is an uptrend. The 50-day above the 200-day, both rising, is a confirmed one. Match the time frame to the holding period; a daily chart is irrelevant to a multi-year position.
2. **Mark the levels that matter** — Prior swing highs and lows, and areas where price has repeatedly reversed. A level touched twice is a hypothesis; a level touched four times is a level.
3. **Check volume** — A breakout on below-average volume is a hypothesis without evidence. An advance on declining volume is a warning.
4. **Measure relative strength** — An instrument rising less than its index in an advance is weak, whatever the chart looks like in isolation.
5. **Define the invalidation before entry** — The price at which the read is wrong. This is the stop, and it must be identified before there is money at stake and an incentive to move it.

## Best Practices

- Technical analysis is descriptive, not predictive. It tells you what has happened and where you are wrong. Anyone claiming it predicts is selling something.
- Volume is the confirmation. Price can be moved by a small amount of capital; volume cannot be faked.
- The more subjective the pattern, the less reliable it is. Trend and volume are near-objective. A head-and-shoulders is in the eye of the beholder, and the beholder has a position.
- Indicators are transformations of price. A dozen indicators derived from the same price series do not constitute a dozen confirmations — they are one observation, restated.
- The trend in the dominant time frame constrains the smaller ones. Buying a bounce in a confirmed downtrend is fighting the primary trend for a secondary move.
- Backtest any pattern you intend to trade. Most classic patterns perform far worse than their reputation, and several perform no better than random.

## Examples

**Characterizing structure objectively:**

```python
def trend_state(df: pd.DataFrame) -> TrendState:
    """Objective structure: no interpretation, no drawing on charts."""
    ma50  = df.close.rolling(50).mean()
    ma200 = df.close.rolling(200).mean()

    swing_highs = find_swing_highs(df, lookback=10)
    swing_lows  = find_swing_lows(df, lookback=10)

    higher_highs = swing_highs.iloc[-1] > swing_highs.iloc[-2]
    higher_lows  = swing_lows.iloc[-1]  > swing_lows.iloc[-2]

    return TrendState(
        structure=(
            "uptrend"   if higher_highs and higher_lows else
            "downtrend" if not higher_highs and not higher_lows else
            "range"
        ),
        ma_aligned=bool(ma50.iloc[-1] > ma200.iloc[-1] and ma200.diff().iloc[-1] > 0),
        above_ma50=bool(df.close.iloc[-1] > ma50.iloc[-1]),

        # The invalidation level: below the last higher low, the uptrend structure
        # is broken by definition. This is the stop, and it was chosen by the
        # structure rather than by how much loss feels tolerable.
        invalidation=float(swing_lows.iloc[-1]),

        # Volume confirmation on the most recent advance.
        volume_confirms=bool(
            df.volume.iloc[-5:].mean() > df.volume.iloc[-50:].mean() * 1.2
            and df.close.iloc[-1] > df.close.iloc[-5]
        ),

        # Relative strength: is it outperforming the benchmark?
        rs_vs_benchmark=float(
            (df.close.iloc[-1] / df.close.iloc[-63] - 1)
            - (bench.close.iloc[-1] / bench.close.iloc[-63] - 1)
        ),
    )
```

**A read that is honest about its limits:**

```text
AAPL, daily:

Structure     : Uptrend. Higher highs and higher lows since the March low.
MA alignment  : 50-day above 200-day, both rising. Confirmed uptrend.
Location      : Price is 11% above the 50-day. Extended; the prior three
                touches of the 50-day were buyable, but chasing here has
                poor asymmetry.
Volume        : The last advance came on volume 18% BELOW the 50-day average.
                The move is not confirmed. This is the most important line here.
Relative str. : +4.2% vs SPY over 63 days. Leading.
Invalidation  : 182.40 — the last higher low. Below that, the uptrend structure
                is broken and this read is wrong.

What this does NOT tell you: whether it goes up from here. The structure is
constructive and the volume is not. That is a description, not a forecast.
```

## Notes

- The distinction between description and prediction is the whole discipline. "Price is in an uptrend and will break 200" is two claims: the first is observable, the second is a guess wearing the first one's clothes.
- Most published pattern-reliability statistics come from studies with severe selection bias — the patterns were identified after the fact, on charts chosen because the pattern worked. Backtest on out-of-sample data or do not trust the number.
- This is educational material about chart-reading methodology, not financial advice, and not a recommendation to trade any instrument.
