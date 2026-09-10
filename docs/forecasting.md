# Forecasting

**Code:** `src/surveillance_platform/forecasting/`

Fits a SARIMA model to each country's dengue history and forecasts three months ahead, compared against a simple seasonal baseline.

```python
from surveillance_platform.forecasting import forecast

results = forecast(prepared_data, role_config, population_by_country)
```

## Not every country gets a forecast, and that's by design

A country needs at least six years of fairly regular reporting before its forecast is trustworthy enough to fully evaluate. Here's how the four study countries actually stack up:

| Country | Data | Months | Good enough to forecast? |
|---|---|---|---|
| Bangladesh (earlier era) | 2010–2021 | 141 | Yes |
| Bangladesh (later era) | 2021–2025 | 42 | No, shown as illustrative only |
| Sri Lanka | full history | 176 | Yes |
| Maldives | 2008–2016 | 108 | Yes |

Nepal doesn't have a long enough stretch of regular data at all, so it gets no real forecast. That's a real limit of the data, not a bug.

## Does it actually work?

Honestly, sometimes yes and sometimes no, and that's worth saying plainly. Compared to a naive "repeat last year" baseline:

- **Sri Lanka**: the model clearly wins
- **Maldives**: the model wins
- **Bangladesh**: the simple baseline actually wins

That last one matters. A forecasting tool that only reports its wins isn't trustworthy. This one reports both, because an honest "it doesn't beat the baseline here" is more useful than a cherry-picked success story.

## Why rates, not raw counts

Case counts get converted to a rate per 100,000 people before modeling. Populations grow over time, and without adjusting for that, a rising population alone would look like a worsening outbreak in the model's eyes.
