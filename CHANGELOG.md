# Changelog

All notable changes to this project are documented in this file, in
line with the tagged-release strategy locked in the Freeze Document
(Section 23, Git & Version Control Strategy):

| Tag | Meaning |
|-----|---------|
| v0.1.0 | Repository foundation complete |
| v0.2.0 | Data preparation pipeline complete |
| v0.3.0 | Exploratory analysis & visualization complete |
| v0.4.0 | Forecasting complete |
| v0.5.0 | UI integration complete |
| v0.6.0 | Architecture validation complete |
| v1.0.0 | Documentation, portfolio polish, and first stable public release |

## [Unreleased]

### Added — Milestone 2: Data Acquisition & Understanding

- `data/download_national_extract.py`: reproducible, checksum-verified
  script to acquire the OpenDengue National Extract v1.3 (download +
  extract only; no transformation).
- `docs/datasets/`: acquisition (source, citation, licensing),
  dataset-landscape verification against ADR-002, full schema
  documentation, time-representation documentation (applying ADR-007),
  a data quality profile (global and South-Asia-specific), and
  investigation of validation dataset candidates for R-001 (PLISA
  confirmed inaccessible; Project Tycho and HDX evaluated, neither
  locked).
- `docs/adr/ADR-008-study-country-selection.md`: locks the four Version
  1 study countries (Sri Lanka, Bangladesh, Maldives, Nepal), with
  Pakistan and India explicitly evaluated and excluded.
- `docs/decision_logs/`: full per-country evidence backing ADR-008.
- `tests/test_milestone2_dataset_acquisition.py`: milestone-verification
  tests (not preprocessing tests) confirming successful acquisition,
  schema-documentation accuracy, and presence of the selected study
  countries — skipped gracefully in CI, where the raw dataset is
  correctly absent (it is git-ignored by design).

No preprocessing, cleaning, role-assignment, or analytical logic was
implemented in this milestone, per its exploratory scope.

### Added — Milestone 6: Visualization

- `src/surveillance_platform/visualization/`: the five finalized M6
  visualizations, consuming only `EDAResult` (never `prepared_data`),
  per the frozen M5 -> M6 boundary — annual surveillance trend
  (country small multiples, with M5's generic country-year
  heterogeneity flags surfaced on affected observations), annual
  distribution of reported-case totals by country, an optional
  population-normalized reported-case-rate distribution (omitted
  gracefully when `EDAResult.population_normalized` is absent), a
  surveillance resolution / case-definition profile (`T_res` and
  `case_definition_standardised`, each independently optional), and a
  Surveillance Measure distribution rendered directly from M5's
  already-computed summary statistics.
- `visualize()` / `VisualizationResult`: a single orchestrator
  function bundling all five visualizations, mirroring the
  `prepare()` / `analyze()` pattern already established in M4 and M5.
- `requirements.txt`: adds `plotly==6.9.0` — the visualization
  dependency locked in the Freeze Document's Dependency Table
  (Section 26) and Implementation Roadmap (Section 29), introduced
  now that Milestone 6 first requires it.
- `docs/visualization.md`: the Visualization contract — the M5/M6
  boundary, how each visualization maps to `EDAResult`, and the
  optional/graceful-omission paths.
- `tests/test_milestone6_visualization.py`: milestone tests covering
  generation of each of the five visualizations, correct
  representation of M5's analytical results, preservation of
  country/year structure, generic (not hard-coded) propagation of
  heterogeneity flags to the annual trend, graceful omission of the
  population-normalized visualization when unavailable, non-mutation
  of `EDAResult`, and graceful failure (a clear typed error, not a
  fabricated chart) on genuinely empty analytical input.

No data cleaning, imputation, recomputation of M5 statistics beyond
what rendering inherently requires, hypothesis testing, regression,
forecasting, or Streamlit/dashboard functionality was implemented in
this milestone, per its representation-only scope. M1–M5 files and
behavior are untouched.

### Added — Milestone 7: Forecasting

- `src/surveillance_platform/forecasting/`: the full ADR-009 pipeline,
  consuming `PreparationResult.data` directly (not `EDAResult`, which
  only stores boolean homogeneity flags — see ADR-009). Window/track
  detection (`detect_tracks`) groups each country's calendar-month
  history into contiguous candidate tracks, evaluated against a
  72-month eligibility floor with tolerance for isolated gaps up to 2
  months; monthly aggregation and population-rate normalization
  (`monthly_series`, `population_rate`); a SARIMA primary workflow
  with order chosen once per track via an AIC grid
  (`select_sarima_order`, `fit_and_forecast_sarima`), fit on
  `log1p(rate)` and back-transformed with intervals floored at 0; a
  seasonal-naive baseline (`seasonal_naive_forecast`) per ADR-005; a
  rolling-origin backtest and MAE/RMSE/MASE evaluation
  (`rolling_origin_backtest`, `compute_metrics`,
  `compute_baseline_metrics`); and `forecast()` /
  `ForecastResult`, mirroring the `prepare()` / `analyze()` pattern
  already established in M4 and M5. Replaces the M1 placeholder
  `forecasting/__init__.py`.
- `docs/adr/ADR-009-forecasting-strategy.md`: locks the specific
  design ADR-005 deliberately left open (target variable, track
  eligibility, model and baseline choice, evaluation protocol), with a
  2026-09-08 addendum correcting an initial dataset-agnosticism claim
  about the OpenDengue-specific `T_res`/`case_definition_standardised`
  columns.
- `docs/forecasting.md`: the Forecasting contract, the M4/M7 boundary,
  the real Version 1 track list and backtest results (Sri Lanka
  MASE≈0.51, Maldives MASE≈0.70, Bangladesh Confirmed MASE≈1.43,
  reported as-is per ADR-005), and every documented limitation.
- `requirements.txt`: adds `statsmodels==0.15.0` — introduced now that
  Milestone 7 first requires SARIMA, per Dependency Management
  Principle 4. Verified compatible with the pinned
  `pandas==3.0.5`/Python 3.12 environment via a fresh, isolated
  install reproducing the full passing test suite.
- `tests/test_milestone7_eligibility.py`,
  `tests/test_milestone7_aggregation.py`, `tests/test_milestone7_model.py`,
  `tests/test_milestone7_backtest.py`, `tests/test_milestone7_pipeline.py`:
  44 new tests (unit tests per stage, synthetic fixtures mirroring the
  M4/M5 style, plus end-to-end integration tests), covering the
  eligibility floor and gap tolerance, case-definition-track
  splitting at month-level precision, non-convergence handling,
  interval flooring, MASE fairness, and graceful, documented handling
  of below-threshold tracks and missing population data rather than
  raising. Full suite: 151 passed, 0 failed, including a fresh-clone
  reproducibility run from `requirements.txt` alone.

Every design decision was checked directly against the real acquired
data (OpenDengue National Extract, WDI population reference) before
being locked, not adopted by convention — see ADR-009 for the full
evidence trail, including two implementation-time corrections (window
detection needed month-level, not year-level, case-definition
precision; a non-converged SARIMA fit warns rather than raises and
must be explicitly excluded from the AIC comparison).

### Added — Milestone 8: UI Integration

- `data_loading/`, `workflow/`, `ui/`, `app.py`: the Epicurve
  Streamlit application, per ADR-010. `data_loading` (CSV ingestion,
  the `S_res` sanity check, checksum-verified sample-dataset download,
  World Bank population registry matching) and `workflow`
  (`AnalysisSession` and its controller functions, implementing PFD
  Section 19's lifecycle) are both fully Streamlit-free and
  independently testable — deleting `ui/` leaves the entire pipeline
  runnable from a script. Replaces the M1 placeholders for both
  modules.
- Seven pages (`ui/pages/`), each mapped to an existing backend result
  object: Load Dataset, Configure Roles, Data Preparation, Exploratory
  Analysis, Visualization, Forecasting, and Results & Export. `st.
  cache_data` wraps `workflow`/`data_loading` calls only at the `ui/`
  boundary (`cached_pipeline.py`), keeping both wrapped modules
  Streamlit-free.
- Forecasting (Page 6) computes one selected track at a time via a new
  `workflow.run_forecast_for_track()`, not the batch `forecast()` —
  needed so a live progress panel (real AIC-grid and rolling-origin
  progress, not simulated) can attach to exactly one track
  unambiguously. Required a small, purely-additive ADR-009 revision
  (`on_candidate`/`on_origin` callbacks on `select_sarima_order()`,
  `rolling_origin_backtest()`, and `forecast_track()`, all default
  `None`, verified byte-identical behavior with and without them).
  This is also where ADR-009's deferred Confirmed/Total
  case-definition selector and below-threshold-track warning land.
- `data_loading/population_lookup.py`: population data sourcing for
  EDA/Forecasting (never decided in the original ADR-010 design),
  resolved as deterministic exact matching against the World Bank's
  own country registry — never fuzzy, never hardcoded to the four
  ADR-008 countries.
- `ui/report_builder.py`: a self-contained, visually designed HTML
  export (real CSS applying the project's locked palette/typography,
  embedded interactive Plotly charts, no new dependency) — Streamlit-
  free and independently testable, served via Page 7.
- Security (ADR-010 addendum, added before implementation): HTML-
  export XSS mitigation via `html.escape()` on every user-derived
  string, in-memory-only uploaded-file handling, upload size limits
  enforced at two layers, sample-dataset download deduplication.
- CI compliance fix: `ruff`/`black` (already required by the existing
  CI workflow, Section 27) were only ever checked via `pytest` locally
  throughout M7/M8's development, leading to a real, silent CI
  failure on `main`. Fixed with zero behavioral change, confirmed by
  an identical passing-test-count before and after every fix.
- `docs/adr/ADR-010-ui-integration-strategy.md` (plus population-
  sourcing and forecast-progress addenda) and `docs/ui.md`.
- 99 new tests across `data_loading`, `workflow`, `report_builder.py`,
  and all seven pages (via `streamlit.testing.v1.AppTest`, simulating
  real file uploads and dropdown selections, not just "loads without
  exception"). Full suite: 253 passed, 0 failed, including a
  fresh-install reproducibility run from `requirements.txt` alone.

Several real gaps were caught and fixed during implementation rather
than assumed away: `st.cache_data` cannot cleanly cache a call
carrying a live UI-bound progress callback (resolved via the
session's own results dict as manual memoization); a report missing
its shared Plotly library script entirely (every chart would have
rendered as an empty div); `AppTest.switch_page()` requiring
file-based pages, not inline functions; and Streamlit's `N999`
module-naming rule, which led to renaming all seven page files rather
than suppressing a real naming-convention violation for no benefit.

### Added — Milestone 9: Architecture Validation

- `data/download_nndss_validation_dataset.py`: acquisition script for
  the Milestone 9 validation dataset, per
  [ADR-011](adr/ADR-011-m9-validation-dataset-selection.md) —
  CDC NNDSS weekly notifiable-disease data (2022–2026), pulled live
  from CDC's public Socrata API (no key or login required). Mirrors
  `download_national_extract.py`'s own acquisition/cleaning boundary:
  the minimum structural transformation needed to produce a loadable
  file (combining `year`+`week` into one date column, filtering and
  case-normalizing location to the 50 states + DC), not a cleaning
  script.
- **Zero changes to `src/surveillance_platform/`.** The entire M3–M7
  pipeline (role configuration, data preparation, EDA, visualization,
  forecasting) ran against this real, structurally different dataset
  completely unmodified, directly answering the Evaluation Question
  (PFD Section 7): the architecture transfers with minimal
  (acquisition-only) adaptation while maintaining full analytical
  reproducibility.
- `docs/m9-dataset-compatibility-report.md`: full 14-point
  pre-implementation analysis (schema, role mapping, adaptation
  classification, proceed/reject recommendation), grounded in real
  pulled data, not documentation alone.
- `docs/m9-architecture-validation-summary.md`: the post-implementation
  workflow trace and final answer to the Evaluation Question.
- `docs/adr/ADR-011-m9-validation-dataset-selection.md` (plus its
  supporting decision log,
  `docs/decision_logs/2026-09-09_m9_dataset_evaluation.md`): the full
  validation-dataset evaluation trail. Project Tycho evaluated and
  rejected on accessibility (seven independent access failures across
  unrelated networks and methods); HDX's disease-outbreaks dataset
  initially accepted, then corrected to rejected once the primary
  source revealed no genuine numeric measure exists at all; WHO GHO
  checked as a comparison and found to share HDX's annual-only
  limitation; CDC NNDSS accepted after being the only candidate
  confirmed on both accessibility and structure with real requests.
- 10 new tests: 6 fast, deterministic unit tests for the acquisition
  script's transformation logic (its MMWR-week arithmetic verified
  against a real, independently-sourced CDC reference date, not just
  internal consistency), 4 full-pipeline regression tests against the
  real acquired file, skipping gracefully when absent (mirroring M2's
  own established pattern for the never-committed raw dataset) rather
  than failing in CI. Full suite: 263 passed, 0 failed, including a
  fresh-install reproducibility run from `requirements.txt` alone,
  checked both with and without the validation dataset present.

One real implementation bug caught and fixed during acquisition: CDC's
`week` column is MMWR epidemiological week numbering, not strict ISO
8601 (they disagree on which years get a 53rd week) — caught when
`pandas`' ISO-week parser raised on 2025's real week 53. Fixed with a
direct, dependency-free MMWR calculation, verified against a real
reference date before being trusted, consistent with the project's
"does the standard library already solve this?" dependency principle.

### Fixed — Post-M9 UI refinements

- **Forecast-date context** (Page 6): different tracks show forecasts
  for very different years with no visible explanation, since each
  forecast starts the month immediately after that track's own last
  real data point, not after today's date. Addressed at three
  touchpoints (track selector label, an immediate info caption on
  selection, and the results subheader) rather than a single fix,
  following an Antigravity-reviewed design recommendation — verified
  against the codebase's real field names first, since the review's
  own draft cited a nonexistent file and attribute.
- **HTML report navigation and mobile responsiveness**
  (`report_builder.py`): the report was one long scroll with no way
  to jump to a section and had zero responsive breakpoints. Added a
  sticky section nav with scroll-spy highlighting (generated only for
  sections actually present in a given session) and real
  `@media (max-width: 640px)` rules — metric rows stack vertically,
  tables scroll horizontally instead of overflowing, Plotly charts
  are genuinely responsive. Verified with real screenshots at both a
  1280px and a 390px viewport.
- **Mobile-illegible annual trend chart** (Page 5): the chart's
  unbounded per-country subplot grid became illegible when squeezed
  to a phone's width via `st.plotly_chart`'s native container-width
  behavior. Confirmed directly against Streamlit's own documentation
  that this widget can never be made to exceed its parent container's
  width, by design, before switching to an `st.components.v1.html()`
  embed with an explicit wider figure width inside a scrollable
  container — verified with real screenshots that desktop is
  unaffected while mobile now shows each panel legibly with genuine
  scroll to see the rest. Scoped to only this one chart; the other
  multi-panel chart on the page (`surveillance_profile`) is capped at
  2 panels and never has this problem.
- Investigated and deliberately left unfixed: Streamlit's own default
  sidebar-overlay behavior on mobile (stays open after navigating,
  requiring one extra tap to dismiss) — a genuine but minor platform
  default, not introduced by this project's own code, where the only
  available fix (custom JS forcing it closed) would contradict
  ADR-010's own locked "zero custom CSS/JS injection" principle for a
  one-tap inconvenience rather than a broken state.

## [0.1.0] — Milestone 1: Project Foundation

### Added

- Repository structure using the `src/` layout.
- Package skeleton (`surveillance_platform`) with placeholder
  submodules mirroring the frozen source module list: dataset
  loading, role configuration, data preparation, exploratory data
  analysis, visualization, forecasting, workflow controller, and UI
  layer. No analytical business logic yet.
- Initial smoke test confirming the package installs and imports
  cleanly.
- Development dependency management (`requirements.txt`, pinned exact
  versions) covering `pytest`, `black`, and `ruff`. Runtime
  dependencies are intentionally deferred to the milestones that first
  require them.
- Packaging configuration (`pyproject.toml`) for the `src/` layout.
- GitHub Actions CI workflow: install dependencies, run Ruff, run Black
  in check mode, run pytest.
- Documentation scaffold: `README.md`, `docs/`, `docs/adr/` (ADR-001
  through ADR-007), `CHANGELOG.md`.
- `LICENSE` (MIT).
- `.gitignore` covering virtual environments, Python caches, OS/IDE
  artifacts, reproducible generated outputs, and raw datasets.
