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
