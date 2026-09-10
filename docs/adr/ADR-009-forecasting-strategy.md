# ADR-009: How forecasting actually works

**Status:** Locked

## The decision

The pipeline forecasts a monthly, population-adjusted case rate (per 100,000 people) for each country, using SARIMA as the main model and a simple seasonal baseline for comparison.

## The building blocks

**Monthly numbers, not annual ones.** Case counts get summed up to monthly totals, never annual ones, because dengue's seasonal pattern is the whole point of forecasting it, and yearly totals erase that pattern completely.

**One country at a time, never mixed together.** Each country gets its own model. Combining countries, or combining different eras of the same country's data, would blend together things that don't actually belong together. For example, Bangladesh changed how it defines a "case" partway through its data history, so that split point matters and gets respected.

**A six year minimum.** A country needs at least 72 months of fairly steady reporting before its forecast is trusted enough to run a full evaluation. This isn't an arbitrary number. It comes from standard time series practice (roughly six times the seasonal cycle length) and matches what published dengue forecasting studies typically use. Countries with less data still get a forecast, just clearly labeled as less reliable, rather than hidden.

**Adjusted for population.** Raw case counts don't mean much on their own since populations grow over time. Rates per 100,000 people make different countries and different years comparable.

## The model

SARIMA, fit on a log-transformed version of the data (to keep predictions from going negative, which raw case counts obviously can't do), compared against a basic seasonal baseline that just repeats last year's number. If the real model doesn't consistently beat that simple baseline, that's worth knowing too, and the pipeline reports both results honestly either way.

Forecasts look three months ahead, evaluated using standard error metrics (MAE, RMSE, and a baseline-relative score called MASE). Every result includes the model's own diagnostics, so a forecast never hides how confident it actually is.
