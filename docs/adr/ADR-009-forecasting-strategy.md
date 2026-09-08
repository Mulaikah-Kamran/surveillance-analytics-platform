# ADR-009 — Forecasting Input, Model, and Evaluation Strategy

**Status:** Locked (Milestone 7)

## Decision

Milestone 7 forecasts a **monthly, population-normalized reported-case
rate per 100,000 population**, per (country, case-definition track),
using **SARIMA** (`statsmodels`) as the primary workflow and
**seasonal-naive (lag-12)** as ADR-005's required transparent baseline.

### Input construction

- **Granularity:** Monthly, built only by summing sub-annual
  (weekly/monthly) `prepared_data` rows into calendar-month totals.
  Never derived from annual-only years — annual aggregation was
  considered and rejected because it discards seasonality, dengue's
  dominant and best-evidenced signal.
- **Modeling unit:** Per (country, case-definition track) — never
  pooled across countries, and never across an in-country case-definition
  change. Eligible windows differ by more than a decade in length across
  the four ADR-008 countries, and Bangladesh's `case_definition_standardised`
  changed from `"Confirmed"` to `"Total"` in October 2021 (a genuine
  change in what is measured, not a casing artifact M4's cleaning
  policy addresses) — concatenating either would introduce a fake
  structural break unrelated to disease transmission.
- **Eligibility rule:** A track qualifies for the full backtest
  protocol if it has **≥72 consecutive months** (6 years) of sub-annual
  reporting under one consistent case definition. This threshold
  is evidence-based, not a project-scope convenience: the Box-Jenkins
  rule of thumb requires roughly 6× the seasonal lag (12) for reliable
  autocorrelation estimation, and published dengue SARIMA studies in
  practice use 8–20 years. Internal gaps of **≤2 consecutive months**
  are tolerated within a run (filled as `NaN` for SARIMAX's native
  Kalman-filter handling — never imputed or fabricated); a larger gap
  splits the run into separate candidate tracks, each independently
  checked against the floor.
- **Window/track detection** is a generic function operating on
  `prepared_data` directly, computing per-year dominant `T_res` and
  `case_definition_standardised` values itself. It cannot be built from
  M5's `EDAResult`: `CountryYearSummary` stores only the boolean
  `resolution_homogeneous`/`case_definition_homogeneous` flags, not the
  actual per-year values needed to compare adjacent years. Consuming
  `prepared_data` from a later stage is consistent with PFD Section 15,
  which lists the cleaned dataset as one of the `Results` objects
  available to any stage, not one reserved exclusively for EDA (M6's
  "never touch `prepared_data`" rule was M6's own self-imposed
  boundary, not a project-wide constraint). The function is
  deliberately generic — evaluated against real per-year values, not
  hardcoded per-country windows — so it runs unmodified against
  whichever dataset Milestone 9 introduces, consistent with the
  project's Evaluation Question and ADR-004's preference for explicit,
  verifiable logic over hardcoded special cases.
- **Below-threshold tracks** (e.g. Bangladesh's `"Total"` era, 42
  months) are shown, not hidden, with an explicit reliability warning
  — consistent with ADR-004's "explicit configuration over hidden
  automation" and the Freeze Document's testing philosophy (a
  documented limitation, not a blocking failure). Such a track cannot
  run the full backtest protocol at all, since it is shorter than the
  protocol's own training window; it is presented as illustrative-only.
- **Resolution shifts within an eligible window** (e.g. Sri Lanka's
  repeated Week↔Month changes) are aggregated to monthly totals
  without a per-row flag. Both source resolutions roll up to the same
  kind of monthly total, so this is a transparency question, not a
  correctness one — the aggregation rule is documented once in
  methodology text rather than surfaced per observation.
- **Target normalization:** annual WDI population (`SP.POP.TOTL`,
  already acquired and checksum-verified for Milestone 5) is applied
  uniformly across every month within that year — never interpolated
  between years. Measured population growth over the actual eligible
  windows (Maldives ~32% over 8 years; Bangladesh ~15% over 15 years)
  is large enough to bias a raw-count model's trend term with pure
  demographic growth unrelated to disease dynamics, which is why raw
  counts were rejected as the forecasting target.

### Model

- **Primary workflow:** SARIMA via `statsmodels==0.15.0` (verified
  compatible with the pinned `pandas==3.0.5`/Python 3.12 environment,
  and verified deterministic across repeated fits on identical input).
  Fit on `log1p(rate)`, forecast back-transformed via `expm1`. This is
  necessary, not cosmetic: the real data is heavily zero-inflated
  (18% of Bangladesh's Confirmed-era months are exactly zero) and
  right-skewed, and an untransformed SARIMA fit on this project's own
  real data produced a 3-month-ahead 95% interval reaching -5.7 —
  a structurally impossible negative case rate. The log transform
  bounds the theoretical worst case (`expm1(x) > -1` for all real
  `x`); any residual negative interval bound is floored at 0 at
  reporting time, documented as a stated convention.
- **Order selection:** a small AIC-comparison grid *within* the SARIMA
  family (`p, q ∈ {0,1,2}`, `P, Q ∈ {0,1}`, `d = D = 1` fixed per
  standard seasonal-differencing practice), run independently per
  eligible track, with the chosen order and its AIC recorded in the
  output. This is standard Box-Jenkins model identification, not the
  "Automated model selection (AutoML)" or "hyperparameter optimization
  across competing models" the Freeze Document excludes — those
  exclusions target selecting between different model families (e.g.
  ARIMA vs. LSTM vs. Prophet), not order selection within one fixed,
  chosen family. Every SARIMA dengue study surveyed during this design
  (Yangon, Rajasthan, Bangladesh) independently fits its own order this
  way.
- **Transparent baseline:** seasonal-naive (forecast month *t* as the
  observed value at month *t-12*), computed directly on the same rate
  series. No new dependency, no fitted parameters — purely an
  evaluation reference per ADR-005, not a competing model.

### Evaluation

- **Backtest protocol:** rolling-origin (expanding window), 72-month
  initial training window (deliberately reused from the eligibility
  floor above, for internal consistency), 3-month forecast horizon,
  1-month step, run for both the primary model and the baseline.
- **Forecast horizon:** 3 months ahead — convergent with the dengue
  early-warning literature (Sierra Leone: h ∈ {1,2,3}; Brazil World Cup
  early-warning system: 3 months), and realistic to backtest robustly
  even on the shortest eligible track (Maldives, 108 months).
- **Evaluation metrics:** MAE, RMSE, and MASE (scaled against the
  seasonal-naive baseline's error). MAPE/sMAPE are explicitly excluded
  — undefined or unstable at the zero-valued months confirmed present
  in the real data. MASE directly operationalizes ADR-005's stated
  purpose for the baseline (context for interpreting the primary
  model, not algorithm competition): MASE < 1 means the primary model
  beats seasonal-naive.
- **Output contract:** `ForecastResult` (mirroring the
  `PreparationResult`/`EDAResult` pattern) carries track identity and
  eligibility flag, the target definition, the chosen SARIMA order and
  AIC, the 3-month forward forecast with floored intervals, the full
  backtest record (per-origin prediction vs. actual, for both model
  and baseline), the three metrics for each, residual diagnostics
  (Ljung-Box), and a documented limitations list.

## Context

ADR-005 locked *that* Milestone 7 implements one primary forecasting
workflow evaluated against one transparent baseline, but deliberately
left the specific model, input granularity, and evaluation design
undecided, since — as with ADR-008's country selection — that
requires the actual data in hand. This ADR resolves those open
questions using the real acquired data (OpenDengue National Extract,
WDI population reference), not assumptions.

## Rationale

Each design choice above was checked directly against the real data
before being locked, not adopted by convention:

- Annual aggregation (the initial default) was rejected after
  confirming, via literature search, that dengue forecasting is
  standardly done at monthly resolution specifically because
  seasonality is the dominant signal — annual aggregation would
  discard it.
- Per-track (not per-country) eligibility was forced by measuring
  actual per-year `T_res` and `case_definition_standardised` values
  across all four countries: Bangladesh's case-definition change and
  Maldives' internal 12-month reporting gap (which, on inspection,
  invalidated an initially-assumed second Maldives track entirely)
  were both found this way, not assumed in advance.
- The 6-year eligibility floor, the SARIMA log-transform, the
  MAPE exclusion, and the 3-month horizon were each grounded in either
  a direct empirical check against this project's real data or a
  convergent reading of the published dengue-forecasting literature,
  documented in the Milestone 7 design discussion.

## Consequences

- **Final verified track list:** Bangladesh (`"Confirmed"`, 141
  months, eligible), Bangladesh (`"Total"`, 42 months, below
  threshold), Sri Lanka (176 months, eligible), Maldives (108 months,
  eligible), Nepal (no monthly-eligible window — excluded from M7
  entirely, a documented dataset limitation per Freeze Document
  Section 20's testing philosophy, not an implementation failure).
- The window/track-detection function's dataset-agnostic design is a
  direct investment in Milestone 9: it should require no modification
  to run against the second surveillance dataset once selected.
- `statsmodels==0.15.0` is added as a new pinned runtime dependency,
  introduced at the milestone that first requires it (Dependency
  Management Principle 4).
- Per ADR Discipline (Freeze Document Section 32), any change to this
  strategy is made as an explicit new ADR revision, not a silent edit.

## Addendum (2026-09-08) — correction to the dataset-agnostic claim

The window/track-detection function's dataset-agnostic design claim
above is corrected: `T_res` and `case_definition_standardised` are
OpenDengue-specific passthrough columns (per
`temporal_standardization.py`'s own docstring), not part of ADR-004's
frozen minimal role model (Time, Location, Surveillance Measure,
optional Identifier). A future Milestone 9 dataset is not guaranteed
to provide equivalent columns.

The function is implemented so that resolution- and
case-definition-aware track splitting is an **opportunistic
enhancement, not a hard dependency**: it checks for the presence of
`T_res`/`case_definition_standardised` and uses them when available
(as with OpenDengue); when absent, it falls back to eligibility based
purely on month-to-month continuity of the role-contracted columns,
which is genuinely generic. This preserves the original intent
(no modification needed for Milestone 9) without overstating what the
OpenDengue-specific checks themselves guarantee.

## Addendum (2026-09-08, later same day) — Antigravity review findings and fixes

A deep scientific/architectural review (Antigravity, read-only audit
of `feature/forecasting`) independently re-ran the full pipeline
against the real OpenDengue/WDI data and confirmed the four locked
tracks above, the reported MASE values, and the honest Bangladesh
result unchanged. Three findings were accepted and fixed:

- **Phantom track generation on long gaps (required correction).**
  `detect_tracks`'s loop could start a new candidate run on a month
  with no data at all, immediately after closing a run for exceeding
  the tolerated-gap limit — producing spurious 1-2 month tracks
  consisting entirely of missing months. Reproduced on countries
  outside the four ADR-008 study countries (their gaps are shorter
  than the failure mode requires, or — Maldives' 2021 gap — span a
  full calendar year and are already excluded earlier via the
  resolution check). Confirmed via manual trace and a regression test
  (`test_long_gap_does_not_produce_phantom_tracks`) that this does
  **not** change any of the four tracks in the table above. Fixed by
  requiring a candidate run's start month to actually have data.
- **Docstring said "per-year" case definition (required correction).**
  `detect_tracks`'s docstring was not updated when the underlying
  logic was corrected to month-level precision during implementation
  (see the first addendum above); `_month_case_definition_signals`'s
  own docstring was already correct. Fixed to say "per-month".
- **Non-convergence path untested (required correction).** The
  `mle_retvals["converged"]` check in both `select_sarima_order` and
  `fit_and_forecast_sarima` was implemented and exercised incidentally
  by real short-series fits, but never asserted on directly. Added
  two mocked tests confirming a non-converged fit is rejected even
  when its AIC would otherwise win, and that the final production fit
  raises rather than returning an unreliable forecast.

Also applied one recommendation: `SarimaOrder.aic` is now explicitly
cast to Python `float` (statsmodels returns `np.float64`), to avoid a
possible downstream serialization surprise in Milestone 8. The
warning-suppression recommendation was not applied — the warnings are
statsmodels' own non-convergence signal, already handled
programmatically, and left visible rather than silenced.

All four locked tracks, their exact month counts, and their reported
MASE values are unchanged after these fixes (re-verified against the
real data). Full suite after fixes: 154 passed, 0 failed (151 + 3 new
tests: 1 phantom-track regression, 2 non-convergence-rejection).
