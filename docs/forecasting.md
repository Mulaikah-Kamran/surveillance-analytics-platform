# Forecasting

**Milestone:** 7 — Forecasting
**Module:** `src/surveillance_platform/forecasting/`
**Design reference:** `docs/adr/ADR-009-forecasting-strategy.md` (full
rationale, evidence, and the exact evaluation results referenced
below); `docs/adr/ADR-005-forecasting-strategy.md` (the original
locked scope: one primary workflow, one transparent baseline).

## Purpose

Produces a monthly, population-normalized forecast of reported dengue
cases per (country, case-definition track), using SARIMA as the
primary workflow evaluated against a seasonal-naive baseline, with a
rolling-origin backtest and residual diagnostics. M7 does not clean,
profile, or visualize data (Milestones 4–6), and exposes no UI
(Milestone 8) — the Streamlit selector for below-threshold tracks and
the Confirmed/Total case-definition choice (ADR-009) is a Milestone 8
concern; M7 delivers the underlying capability only.

## M4 / M7 boundary

M7 consumes `PreparationResult.data` (Milestone 4's output) directly
— not Milestone 5's `EDAResult`. This is a deliberate departure from
M5→M6's boundary: `EDAResult`'s `CountryYearSummary` only stores
boolean `resolution_homogeneous`/`case_definition_homogeneous` flags,
not the actual per-year dominant values M7's track detection needs to
compare across years. Consuming the cleaned dataset from an earlier
stage is consistent with PFD Section 15, which lists it as one of the
`Results` objects available to any stage, not one reserved
exclusively for EDA (see ADR-009 for the full argument).

## Output contract

```python
from surveillance_platform.forecasting import forecast

results = forecast(prepared_data, role_config, population_by_country)
```

`prepared_data` is `PreparationResult.data`. `population_by_country`
maps each country name (as it appears in the location-role column) to
its own annual population series (year → population, e.g. the WDI
`SP.POP.TOTL` series already acquired for Milestone 5). Returns a
`list[ForecastResult]`, one per candidate track `detect_tracks` finds
— see `surveillance_platform.forecasting.report` for every nested
result dataclass. Never mutates either input. Each stage
(`detect_tracks`, `monthly_series`, `population_rate`,
`select_sarima_order`, `fit_and_forecast_sarima`,
`seasonal_naive_forecast`, `rolling_origin_backtest`,
`compute_metrics`, `compute_baseline_metrics`, `forecast_track`) is
also independently importable and testable.

A `ForecastResult` never raises on an ordinary data limitation — a
below-threshold track, a country with no population data, or a
non-converged fit all still return a `ForecastResult`, with the
affected fields empty/`None` and the reason recorded in
`limitations`, per ADR-009 Point 7's "document, don't hide" principle
and the Freeze Document's testing philosophy (Section 20).

## Track detection

`detect_tracks` groups each country's calendar-month history into
contiguous candidate tracks, splitting on: non-sub-annual reporting
resolution (year-level, via the OpenDengue-specific `T_res` column,
when present); a change in dominant case definition (month-level, via
`case_definition_standardised`, when present); or a gap exceeding 2
consecutive months. A track is `eligible` at ≥72 months. Both
`T_res`- and case-definition-aware splitting are opportunistic
enhancements, not hard dependencies — see ADR-009's 2026-09-08
addendum: a future Milestone 9 dataset without equivalent columns
still gets correct detection based on plain continuity of the
role-contracted columns.

Applying this generically (not manually, per ADR-004's preference for
explicit logic over hardcoded special cases) to the four ADR-008
countries surfaces every genuine candidate window, including several
short (~12-month) fragments that are correctly returned as
ineligible rather than filtered out silently. The four tracks that
matter for Version 1's actual results:

| Country | Case definition | Months | Eligible |
|---|---|---|---|
| Bangladesh | Confirmed (2010-01–2021-09) | 141 | Yes |
| Bangladesh | Total (2021-10–2025-03) | 42 | No — illustrative only |
| Sri Lanka | (constant) | 176 | Yes |
| Maldives | (constant, 2008–2016) | 108 | Yes |

Nepal has no monthly-eligible window at all (its only sub-annual
history, 2022–2025, is 39 months) — a documented dataset limitation,
not an implementation gap.

## Target variable

Population-normalized rate per 100,000, not raw case counts — annual
population applied uniformly to every month within that year, never
interpolated between years. Rejected raw counts because measured
population growth over the actual eligible windows (Maldives ~32%
over 8 years; Bangladesh ~15% over 15 years) is large enough to bias
a raw-count model's trend term with pure demographic growth unrelated
to disease dynamics (ADR-009).

## Model

SARIMA (`statsmodels`), fit on `log1p(rate)` and back-transformed via
`expm1` — necessary, not cosmetic: 18% of Bangladesh's real
Confirmed-era months are exactly zero, and an untransformed fit on
this project's own data produced a 95% interval reaching -5.7, a
structurally impossible negative case rate. Any residual negative
interval bound is floored at 0 at reporting time. Order is chosen
**once per track** via a small AIC grid within the SARIMA family
(`p, q ∈ {0,1,2}`; `P, Q ∈ {0,1}`; `d = D = 1` fixed), then reused
across every rolling-origin backtest refit — re-running the grid at
every origin would be both wasteful and inconsistent with ADR-009's
"per eligible track" wording. A fit that does not converge is
detected via `mle_retvals["converged"]` (statsmodels only warns, it
does not raise) and excluded from the order comparison, or reported
as a limitation if it is the final chosen-order fit itself.

The baseline is seasonal-naive (lag-12): forecast month *t* as the
observed value at month *t-12*. No fitted parameters — purely an
ADR-005-mandated evaluation reference, not a competing model.

## Evaluation

Rolling-origin (expanding-window) backtest: 72-month initial training
window (deliberately reused from the eligibility floor), 3-month
horizon, 1-month step, refitting the chosen order at every origin.
Reports MAE and RMSE for both model and baseline, plus MASE (model
MAE ÷ baseline MAE, computed over the same comparable origins for a
fair ratio). MAPE/sMAPE are deliberately excluded — undefined at the
zero-valued months confirmed present in the real data. A track
shorter than the training window plus horizon cannot run the backtest
at all; this is stated as a limitation, not worked around with a
smaller window.

Real backtest results across the three eligible tracks (documented
here because they are the actual Version 1 findings, not merely
illustrative): Sri Lanka MASE ≈ 0.51 and Maldives MASE ≈ 0.70 (SARIMA
beats the baseline on both); Bangladesh Confirmed MASE ≈ 1.43 (SARIMA
loses to the baseline). This is reported as-is — the baseline exists
specifically to surface cases where the more sophisticated model does
not actually help (ADR-005), not to be tuned away.

## Residual diagnostics

Ljung-Box test at lag 12 on the final full-track fit's residuals
(leading `NaN`s from differencing initialization are dropped before
the test, not passed through). Returns `None` — never a fabricated
value — when the final fit does not converge, or when a track is too
short to have enough post-differencing residuals for a lag-12 test to
be meaningful at all (the same short fragments noted under Track
detection above).
