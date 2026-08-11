# Documentation

This directory holds detailed engineering documentation for the
project, as distinguished from the top-level `README.md` (Section 21
of the Freeze Document, Documentation Philosophy):

> `docs/` — Detailed engineering documentation (PDD, architecture
> overview, future technical notes)

## Current contents

- [`PROJECT_FREEZE_DOCUMENT.md`](PROJECT_FREEZE_DOCUMENT.md) — the
  frozen project constitution, reproduced here as a reference copy for
  traceability.
- [`PROJECT_DESIGN_DOCUMENT.md`](PROJECT_DESIGN_DOCUMENT.md) — the
  engineering blueprint (PDD), reproduced here as a reference copy.
- [`adr/`](adr/) — Architecture Decision Records (ADR-001 through
  ADR-008), locked during project planning.
- [`testing/`](testing/) — per-milestone test reports.
- [`role_configuration.md`](role_configuration.md) — the Role
  Configuration contract (Milestone 3): role model, public API, and
  validation scope.
- [`data_preparation.md`](data_preparation.md) — the Data Preparation
  Pipeline contract (Milestone 4): stage responsibilities, the M3/M4
  validation boundary, and the evidence-based cleaning policy.
- [`eda.md`](eda.md) — the Exploratory Data Analysis contract
  (Milestone 5): analytical scope, the M4/M5 boundary, the
  country-year homogeneity checks, and optional population
  normalization.
- [`visualization.md`](visualization.md) — the Visualization contract
  (Milestone 6): the five finalized visualizations, the M5/M6
  boundary, how each visualization maps to `EDAResult`, and the
  optional/graceful-omission paths.

## Planned (added incrementally, as the corresponding work exists)

- Architecture overview and diagrams
- Installation guide
- User guide
- Technical report

Per the Freeze Document's Documentation Philosophy: *"What we do not
document yet: API documentation, module reference, function
documentation — these depend on code that doesn't exist yet and would
not stay truthful if written speculatively. They are written
incrementally as modules are implemented."* The same principle applies
to the planned documents above — they are added in the milestone where
they first become truthful to write, not speculatively now.
