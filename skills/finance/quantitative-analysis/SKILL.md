---
name: quantitative-analysis
description: Use when applying statistical methods to financial data. Covers return distributions, stationarity, correlation versus causation, the multiple-testing problem, and the statistical traps specific to financial time series.
metadata:
  category: finance
  version: 1.0.0
  tags: [quant, statistics, time-series, significance, modeling]
---

# Quantitative Analysis

## Purpose

Apply statistics to financial data without being fooled by it. Financial time series violate nearly every assumption of standard statistical methods, and the tools will produce confident, well-formatted, wrong answers without complaint.

## When to Use

- Testing whether a signal has predictive value.
- Modeling returns, volatility, or correlations.
- Evaluating a quantitative claim someone else has made.
- Building a factor model or a risk model.

## Capabilities

- Return distributions and their fat tails.
- Stationarity, unit roots, and spurious regression.
- Correlation, causation, and confounding.
- Multiple-testing correction and data snooping.
- Volatility modeling and clustering.

## Inputs

- The data, and an honest account of how it was selected.
- The hypothesis — stated before the data was examined.
- The number of hypotheses that have already been tested on this data.

## Outputs

- A result with its assumptions stated.
- A significance level corrected for the number of tests actually run.
- An honest statement of what the result does and does not support.

## Workflow

1. **Look at the distribution before assuming one** — Financial returns are not normal. They have fat tails and skew, and every method that assumes normality will underestimate the probability of a large move — which is the only probability that matters for survival.
2. **Test for stationarity** — Regressing one non-stationary series on another produces a high R-squared and a significant t-statistic between two entirely unrelated things. This is spurious regression, and it is the most common error in financial statistics.
3. **Work in returns, not prices** — Prices are non-stationary by construction. Returns are approximately stationary. Almost every meaningful analysis operates on returns.
4. **Count the hypotheses you have tested** — If you tried a hundred signals and one has a p-value of 0.01, you have found exactly what pure chance predicts. A p-value not adjusted for the search is not evidence.
5. **Distinguish correlation from causation, and both from coincidence** — With enough series, something will correlate with anything. A mechanism stated in advance is what separates a finding from a coincidence.
6. **Validate out of sample** — On data that was not available when the hypothesis was formed. Everything else is description.

## Best Practices

- Financial returns have fat tails. A "six-sigma" event under a normal distribution should occur once in several million years; in markets it occurs every few years. Any model built on normality is quietly understating tail risk.
- Non-stationarity produces spurious regressions with astonishing reliability. Two random walks will regress on each other with a significant t-statistic roughly 70% of the time. Always difference or test first.
- Correlation between financial series is unstable. A correlation estimated over three years describes those three years, and it will not hold in the crisis you are trying to protect against.
- The multiple-testing problem is the single largest source of false discovery in quantitative finance. The published anomaly literature is substantially a record of it.
- In-sample fit is not evidence. Any sufficiently flexible model fits any dataset. The only test that means anything is out of sample.
- Report the effect size, not just the p-value. A statistically significant edge of 0.02% per trade is not tradable after costs.

## Examples

**Spurious regression — the error that produces the most confident wrong answers:**

```python
import numpy as np, statsmodels.api as sm

# Two independent random walks. There is no relationship whatsoever.
np.random.seed(1)
a = np.cumsum(np.random.randn(500))
b = np.cumsum(np.random.randn(500))

model = sm.OLS(a, sm.add_constant(b)).fit()
print(f"R-squared: {model.rsquared:.3f}   t-stat: {model.tvalues[1]:.2f}")
# R-squared: 0.681   t-stat: 32.71
#
# An R-squared of 0.68 and a t-statistic of 33 between two series with NO
# relationship at all. This is not a fluke of the seed; it happens most of the
# time with non-stationary series. Any conclusion drawn from this is fiction.

# The correct procedure: test for stationarity, and work in returns.
from statsmodels.tsa.stattools import adfuller

for name, series in [("a", a), ("b", b)]:
    p = adfuller(series)[1]
    print(f"{name}: ADF p={p:.3f} -> {'non-stationary' if p > 0.05 else 'stationary'}")
# a: ADF p=0.712 -> non-stationary
# b: ADF p=0.884 -> non-stationary
#
# Differencing to returns removes the spurious relationship entirely.
model_returns = sm.OLS(np.diff(a), sm.add_constant(np.diff(b))).fit()
print(f"R-squared: {model_returns.rsquared:.4f}   t-stat: {model_returns.tvalues[1]:.2f}")
# R-squared: 0.0004   t-stat: -0.44   <- the truth: no relationship
```

**Multiple testing — why most published anomalies are not real:**

```python
def corrected_significance(p_values: list[float], n_tested: int) -> Report:
    """A p-value of 0.01 means nothing if you tested 100 hypotheses."""
    best_p = min(p_values)

    # Bonferroni: the family-wise error rate.
    bonferroni = min(1.0, best_p * n_tested)

    # The probability that the best of n random signals looks this good by chance.
    prob_by_chance = 1 - (1 - best_p) ** n_tested

    return Report(
        raw_p=best_p,
        bonferroni_p=bonferroni,
        prob_at_least_one_by_chance=prob_by_chance,
        verdict=(
            "Not distinguishable from chance."
            if bonferroni > 0.05
            else "Survives correction. Now validate out of sample."
        ),
    )

# Tested 120 signal variants. The best has p = 0.008.
#   raw p                      : 0.008     "significant!"
#   Bonferroni-corrected p     : 0.96
#   P(at least one this good
#     by chance among 120)     : 0.62
#   Verdict: not distinguishable from chance.
#
# The signal is exactly as good as the best of 120 random signals would be
# expected to be. It is a discovery about the search, not about the market.
```

## Notes

- The spurious-regression demonstration above is the single most important thing in this skill. An R-squared of 0.68 between two unrelated random walks is not a corner case — it is the typical result, and it has produced a great many published findings.
- Fat tails mean that variance is a poor risk measure for financial returns. Maximum drawdown and expected shortfall describe what actually hurts.
- This is educational material about quantitative methodology, not financial advice, and none of it constitutes a recommendation.
