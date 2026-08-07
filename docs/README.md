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
