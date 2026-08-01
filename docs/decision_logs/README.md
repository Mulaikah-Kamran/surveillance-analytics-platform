# Decision Logs

Dated records of project decisions that have a concrete rationale and
evidence trail, but are not themselves architectural (which is what
`docs/adr/` is for). Per the Freeze Document's Documentation Philosophy,
these exist to record research thinking, not just outcomes — a reviewer
should be able to see *why* a decision was made, not just what it was.

## Contents

- [`2026-08-01_country_selection.md`](2026-08-01_country_selection.md) —
  selection of the study countries (Milestone 2, Chapter 3.1 criteria),
  including the explicit reasoning for excluding Pakistan and India.

## Decision Logs vs. ADRs

An ADR (`docs/adr/`) records a decision with multiple reasonable
alternatives that affects future architecture and would be difficult to
reverse (per the Freeze Document's ADR Creation Rule). A decision log
records a decision made *within* an already-locked architectural
boundary — country selection operates inside ADR-002's already-decided
"3–5 South Asian countries, National Extract" framework; it doesn't
revise that framework, so it doesn't warrant a new ADR number.
