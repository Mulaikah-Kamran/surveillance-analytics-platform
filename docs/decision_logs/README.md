# Decision Logs

Dated records of project decisions that have a concrete rationale and
evidence trail, but are not themselves architectural (which is what
`docs/adr/` is for). Per the Freeze Document's Documentation Philosophy,
these exist to record research thinking, not just outcomes — a reviewer
should be able to see *why* a decision was made, not just what it was.

## Contents

- [`2026-08-01_country_selection.md`](2026-08-01_country_selection.md) —
  full per-country profiling behind the study country selection, now
  formally locked as [ADR-008](../adr/ADR-008-study-country-selection.md)
  (the roadmap calls for this specific decision to be an ADR; most other
  Milestone 2 decisions are recorded here instead, without their own ADR).
- [`2026-09-09_m9_dataset_evaluation.md`](2026-09-09_m9_dataset_evaluation.md) —
  Milestone 9 validation-dataset evaluation against PFD Section 12's
  four criteria, now formally locked as
  [ADR-011](../adr/ADR-011-m9-validation-dataset-selection.md). Project
  Tycho rejected on accessibility (seven independent access failures);
  HDX's disease-outbreaks dataset initially accepted, then corrected
  to rejected once the primary source revealed no genuine numeric
  measure exists at all; WHO GHO checked as a comparison and found to
  share HDX's annual-only limitation; CDC NNDSS (2022–2026) accepted.

## Decision Logs vs. ADRs

An ADR (`docs/adr/`) records a decision with multiple reasonable
alternatives that affects future architecture and would be difficult to
reverse (per the Freeze Document's ADR Creation Rule). A decision log
records a decision made *within* an already-locked architectural
boundary — country selection operates inside ADR-002's already-decided
"3–5 South Asian countries, National Extract" framework; it doesn't
revise that framework, so it doesn't warrant a new ADR number.
