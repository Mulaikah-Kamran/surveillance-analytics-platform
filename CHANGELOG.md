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
