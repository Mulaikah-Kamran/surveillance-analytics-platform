# ADR-008 — Study Country Selection

**Status:** Locked (Milestone 2)

## Decision

The Version 1 study dataset consists of four South Asian countries:
**Sri Lanka, Bangladesh, Maldives, and Nepal.**

Afghanistan, Bhutan, India, and Pakistan were evaluated against the same
criteria and excluded. This falls within the 3–5 country range ADR-002
already locked; ADR-002 is not revised by this decision.

## Context

ADR-002 locked the *framework* — a study dataset of "3–5 South Asian
countries, selected during Phase 2 using the objective criteria defined
in Section 13" — but deliberately deferred which specific countries,
since that requires actually acquiring and profiling the data first.
Milestone 2's roadmap entry names this explicitly as a deliverable
("select 3–5 study countries per Ch.3 criteria; document rationale
(ADR)"), which is why this is recorded as a numbered ADR rather than
only a decision log entry, unlike some other Milestone 2 outputs.

## Rationale

Of the Freeze Document's 8 objective country-selection criteria
(Section 13), six (Surveillance Relevance, Temporal Information,
Geographic Information, Public Availability, Documentation Quality,
Variable Richness) are properties of the dataset as a whole and are
satisfied identically by all 8 SAARC countries present in the National
Extract. The two that actually differentiate candidates — **Sufficient
Historical Coverage** and **Workflow Compatibility** — were applied
directly against the acquired v1.3 data:

- **Sri Lanka, Bangladesh, Maldives, Nepal** all have at least four
  decades of history and predominantly sub-annual (weekly or monthly)
  reporting, with a small, stable set of case definitions.
- **Pakistan** is excluded: zero directly ministry-of-health-sourced
  rows (compiled only from `LITERATURE`/`WHO`), three distinct case
  definitions in use across its history, and a 6-year reporting gap —
  the weakest of the eight candidates on both criteria.
- **India** is excluded: despite a clean, gap-free 35-year span, 34 of
  its 35 rows are annual resolution, which is insufficient for the
  sub-annual seasonality and forecasting analysis this project's later
  milestones require. This is a data-resolution limitation, not a
  data-quality one.
- **Bhutan** is excluded as a marginal case (mostly annual reporting,
  highest zero-value share of the eight).
- **Afghanistan** is excluded outright: its entire record spans only 5
  years (2021–2025), failing the historical-coverage criterion on its
  own terms regardless of its otherwise reasonable reporting resolution.

Full per-country figures (row counts, reporting gaps, case-definition
mixes, source categories) are in
[`../decision_logs/2026-08-01_country_selection.md`](../decision_logs/2026-08-01_country_selection.md),
which this ADR treats as its supporting evidence record rather than
repeating in full here.

## Consequences

- Milestone 3 onward (role configuration, data preparation, EDA,
  forecasting) operates against exactly these four countries' data.
- India's exclusion is a genuine trade-off worth surfacing to a reviewer:
  it is the largest-burden country in the region, excluded purely on
  temporal-resolution grounds. If a future milestone's forecasting
  approach turns out to work adequately at annual resolution, India
  could be added as a 5th country without revising this ADR's criteria
  or method — only its conclusion for that one country.
- Per ADR Discipline (Freeze Document Section 32), any change to this
  selection is made as an explicit new ADR revision, not a silent edit.
