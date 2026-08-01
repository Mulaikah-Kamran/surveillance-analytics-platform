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
