# Public Health Surveillance & Analytics Platform

> **Status: Version 1 is under active development.** This repository
> currently reflects **Milestone 1 — Project Foundation** only. No
> analytical functionality exists yet. See
> [Current Implementation Status](#current-implementation-status) below
> for exactly what does and does not work today.

A modular research software platform that supports public health
analysts in transforming surveillance-derived datasets into reliable,
reproducible analytical outputs — through validation, profiling,
quality assessment, cleaning, exploratory analysis, visualization,
forecasting, and reporting.

## Purpose

Public health surveillance systems generate large volumes of data that
are later aggregated, curated, and analyzed to monitor disease
patterns and support public health decision-making. Transforming
surveillance-derived datasets into reliable analytical outputs requires
careful data validation, profiling, quality assessment, standardization,
cleaning, exploratory analysis, forecasting, and transparent reporting.

This project builds a modular research software platform that supports
that workflow, emphasizing reproducibility, maintainability, and
epidemiological reasoning — for a single primary user: the **Public
Health Analyst**.

## Research Motivation

This project is inspired by work carried out during a public health
research internship. It recreates an infectious disease surveillance
analysis workflow using publicly available surveillance-derived data
(the [OpenDengue](https://opendengue.org/) National Extract), rather
than confidential institutional datasets.

The goal is not another dashboard or machine learning demonstration.
Instead, the project asks:

- **Engineering research question:** How can research software
  engineering principles be applied to develop a reproducible
  analytical workflow that enables public health analysts to transform
  surveillance-derived datasets into reliable analytical outputs?
- **Evaluation question:** To what extent can the proposed workflow and
  architecture, designed primarily for the OpenDengue National Extract,
  be validated using one additional surveillance dataset with minimal
  adaptation while maintaining analytical reproducibility?

## Architecture Overview

The platform follows a layered architecture:

```
Presentation Layer (Streamlit)
        ↓
Workflow Controller
        ↓
Analytical Modules
        ↓
Data Layer
```

Analytical modules are reusable, independently testable, and
independent of the user interface. The Streamlit application is the
presentation layer only — it does not contain analytical business
logic.

The analytical workflow itself is fixed in this order:

```
Validation → Profiling → Quality Assessment → Temporal Standardization
    → Cleaning → EDA → Visualization → Forecasting → Reporting
```

If validation fails, execution stops, the Analysis Session is marked
`Failed`, diagnostic information is preserved, and control returns to
the user interface — downstream modules are not executed.

Full architectural reasoning is recorded in the project's
[Architecture Decision Records](docs/adr/), which are locked and stable
unless revised through an explicit, documented process. Reference
copies of the frozen constitutional documents are also committed to
the repository: the
[Project Freeze Document](docs/PROJECT_FREEZE_DOCUMENT.md) and the
[Project Design Document](docs/PROJECT_DESIGN_DOCUMENT.md).

## Current Implementation Status

**Milestone 1 of 10 — Project Foundation.**

This repository currently provides:

- ✅ Repository structure (`src/` layout)
- ✅ Package skeleton with placeholder analytical submodules (no
  business logic)
- ✅ Development environment and dependency management
- ✅ CI (linting, formatting checks, test execution)
- ✅ Initial documentation scaffold (this README, ADRs, changelog)

It does **not** yet provide:

- ❌ Dataset loading or any dataset
- ❌ Role configuration
- ❌ Validation, profiling, quality assessment, cleaning
- ❌ Exploratory analysis or visualizations
- ❌ Forecasting
- ❌ A working Streamlit application
- ❌ Any analytical output whatsoever

Nothing in this repository should be interpreted as a working
analytical tool yet. See the Roadmap below for what each future
milestone adds.

## Roadmap Summary

Development proceeds in ten milestones, each leaving the repository in
a usable, testable state:

| # | Milestone | Adds |
|---|-----------|------|
| 1 | Project Foundation | Repository, environment, structure, CI *(this release)* |
| 2 | Data Acquisition & Understanding | OpenDengue dataset selection & documentation |
| 3 | Role Configuration | Dataset loading, role assignment & validation |
| 4 | Data Preparation Pipeline | Profiling, quality assessment, standardization, cleaning |
| 5 | Exploratory Analysis | Descriptive statistics, summaries, comparisons |
| 6 | Visualization | Interactive time-series and comparison plots |
| 7 | Forecasting | One primary forecasting workflow + transparent baseline |
| 8 | UI Integration | Full Streamlit application over the tested backend |
| 9 | Architecture Validation | Workflow re-run on a second surveillance dataset |
| 10 | Documentation & Portfolio Polish | Full docs, diagrams, user guide |

Dependencies, in keeping with the project's "start minimal, grow with
justification" principle, are introduced only in the milestone that
first requires them (e.g. `pandas` and `numpy` in Milestone 2/4,
`plotly` in Milestone 6, `scikit-learn` in Milestone 7, `streamlit` in
Milestone 8) — not all at once in Milestone 1.

## Repository Structure

```
surveillance-analytics-platform/
├── .github/
│   └── workflows/
│       └── ci.yml              # Lint, format-check, test on every push/PR
├── configs/                    # Configuration placeholders (role mappings, settings)
├── data/                       # Lightweight/example data only — never raw datasets
├── docs/
│   ├── adr/                    # Architecture Decision Records (ADR-001–007)
│   └── README.md
├── notebooks/                  # Optional exploratory notebooks (not production code)
├── src/
│   └── surveillance_platform/
│       ├── data_loading/       # Placeholder — Milestone 2
│       ├── role_configuration/ # Placeholder — Milestone 3
│       ├── data_preparation/   # Placeholder — Milestone 4
│       ├── eda/                # Placeholder — Milestone 5
│       ├── visualization/      # Placeholder — Milestone 6
│       ├── forecasting/        # Placeholder — Milestone 7
│       ├── workflow/           # Placeholder — Milestones 4–8
│       └── ui/                 # Placeholder — Milestone 8
├── tests/
│   └── test_smoke.py           # Milestone 1 smoke test only
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Quick Start

Requires **Python 3.12 or newer**.

```bash
# Clone the repository
git clone <repository-url>
cd surveillance-analytics-platform
```

Create and activate a virtual environment:

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**

```powershell
py -3 -m venv .venv
.venv\Scripts\activate
```

Then, on any platform, install dependencies and the package itself
(editable install):

```bash
pip install -r requirements.txt
pip install -e .
```

There is currently nothing to run — Milestone 1 is infrastructure
only. The Quick Start above will be extended with real usage
instructions as the analytical workflow is implemented.

## Development Setup

- **Environment:** `venv` + `pip`, not Poetry or `uv` — chosen
  deliberately so the repository communicates architectural judgment
  clearly, with no extra prerequisite tooling.
- **Dependency pinning:** exact versions only (e.g. `pytest==9.1.1`),
  to avoid silent environment drift for anyone cloning the repository
  later.
- **Linting/formatting:**

  ```bash
  ruff check .
  black --check .     # or `black .` to apply formatting
  ```

- **Version synchronization:** the project version is currently
  declared in two places — `pyproject.toml` (`project.version`) and
  `src/surveillance_platform/__init__.py` (`__version__`). Before
  creating a new release tag, update both together. This is a manual
  convention for now; no dynamic version tooling has been introduced
  (consistent with the "start minimal" dependency principle).
- **Tested environment:**

  > Developed and tested on: Linux (Ubuntu), Python 3.12.3. Also
  > verified via the project's GitHub Actions CI, which runs on
  > `ubuntu-latest`.
  >
  > Expected compatibility: macOS and Windows (no known OS-specific
  > dependencies in the code or tooling), but these have not yet been
  > formally tested as part of Milestone 1.

## Testing Philosophy

The backend is treated as an independent software library, tested at
three levels, independent of the user interface:

1. **Unit tests** — individual analytical modules, no UI involved.
2. **Integration tests** — complete workflow execution from dataset
   input to analytical outputs, no Streamlit.
3. **UI verification** — confirms the Streamlit interface correctly
   invokes backend modules and displays their outputs (an integration
   check between presentation and backend, not a re-test of analytical
   logic).

No milestone is considered complete until its planned tests have been
executed and their results documented. At Milestone 1, this means only
a trivial smoke test exists — proving the test framework itself works,
not that any analytical logic is correct (there is none yet).

Run tests with:

```bash
pytest
```

## License

Released under the [MIT License](LICENSE).

## Contribution Statement

This is currently a solo research software engineering project
developed against a frozen architecture and a fixed milestone roadmap.
External contributions are not being actively solicited at this stage.
If that changes in a future version, contribution guidelines will be
added here and in `docs/`.

## Future Versions

Explicitly out of scope for Version 1, and deferred to future versions
if pursued at all:

- Spatial hotspot / district-level (Admin2) analysis
- Multi-disease support
- Plugin architecture
- Real-time surveillance integration
- Automated semantic role inference
- AI-assisted schema interpretation
- Production deployment for health agencies
- Advanced/ensemble/deep-learning forecasting models
- Benchmarking of multiple competing forecasting algorithms, AutoML,
  or hyperparameter optimization across competing models

See the [Project Design Document](docs/PROJECT_DESIGN_DOCUMENT.md) and
[Architecture Decision Records](docs/adr/) for the full rationale
behind these exclusions.
