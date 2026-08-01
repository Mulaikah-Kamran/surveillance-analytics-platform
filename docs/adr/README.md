# Architecture Decision Records (ADR)

This directory is the historical record of the project's major, locked
design decisions, as required by the Freeze Document (Section 21,
Documentation Philosophy: *"ADRs record architectural reasoning"*).

Per the Freeze Document's ADR Creation Rule (Section 23): an ADR is
created only when a decision has multiple reasonable alternatives,
affects future architecture, would be difficult to reverse, or would
otherwise be hard to remember later. Once an ADR is locked, it is
considered stable (Section 32, ADR Discipline) — revisions happen only
when implementation reveals a genuine engineering issue, and any
revision is made explicitly as a new ADR revision, synchronized across
every dependent document, never silently.

## Index

| ADR | Title |
|-----|-------|
| [ADR-001](ADR-001-primary-user.md) | Primary User |
| [ADR-002](ADR-002-data-strategy.md) | Data Strategy |
| [ADR-003](ADR-003-analytical-workflow.md) | Analytical Workflow |
| [ADR-004](ADR-004-minimal-analytical-role-model.md) | Minimal Analytical Role Model |
| [ADR-005](ADR-005-forecasting-strategy.md) | Forecasting Strategy (Revised) |
| [ADR-006](ADR-006-user-interface-strategy.md) | User Interface Strategy |
| [ADR-007](ADR-007-temporal-standardization-strategy.md) | Temporal Standardization Strategy |
| [ADR-008](ADR-008-study-country-selection.md) | Study Country Selection |

ADR-001 through ADR-007 were locked during project planning (Phase 0)
and are reproduced here from the Freeze Document, Section 18, as the
authoritative historical record within the repository itself. ADR-008
is the first ADR created during implementation rather than planning —
Milestone 2's roadmap entry explicitly calls for the study country
selection to be recorded as an ADR, since it fixes a concrete input to
every later milestone and would be difficult to reverse once Milestone 3
begins building against it.
