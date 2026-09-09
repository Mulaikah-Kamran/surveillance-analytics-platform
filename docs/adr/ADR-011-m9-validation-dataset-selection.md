# ADR-011 — Milestone 9 Validation Dataset Selection

**Status:** Locked (Milestone 9)

## Decision

The Milestone 9 validation dataset is the **CDC National Notifiable
Diseases Surveillance System (NNDSS) weekly data**, specifically the
single-table resource covering **2022–2026**
(`data.cdc.gov/resource/x9gk-5huc`, Socrata SODA API).

This satisfies the "one additional surveillance dataset" the
Evaluation Question (PFD Section 7) and Milestone 9 (Section 29)
require. Project Tycho and HDX's disease-outbreaks dataset were both
evaluated and rejected first; WHO's Global Health Observatory was
checked as a comparison point and found to share HDX's structural
limitation. This ADR does not revise ADR-002 or ADR-008, which govern
the *primary* (OpenDengue) dataset and its country selection.

## Context

PFD Section 12's four validation-dataset criteria — public
accessibility, reproducibility, compatible analytical structure, and
sufficient variable richness that differs meaningfully in structure
from OpenDengue — were already anticipated to be in tension with each
other during original planning: the Risk Register's R-001 rejected the
originally-considered candidate (PAHO PLISA) specifically on
accessibility grounds, and named Project Tycho and HDX as the
alternatives to evaluate. This ADR is the resolution of that
still-open item.

## Rationale

Four real candidates were evaluated with direct, empirical
verification at each step, not on documentation or reputation alone.
Full evidence trail:
[`../decision_logs/2026-09-09_m9_dataset_evaluation.md`](../decision_logs/2026-09-09_m9_dataset_evaluation.md).

- **Project Tycho** (US NNDSS data historically archived by an
  academic project) — structurally excellent (weekly, real case
  counts, richer metadata than OpenDengue, independently confirmed
  across three sources) but **rejected on accessibility**: seven
  independent registration/access attempts failed, from unrelated
  networks, countries, and methods, including a sandbox environment
  with no geographic dependency at all returning a 503 from the
  registration endpoint itself.
- **HDX's "global dataset of pandemic- and epidemic-prone disease
  outbreaks"** — genuinely open access, but **rejected on structure**:
  reading the primary source in full (not just its abstract) found the
  authors' own stated limitation that no case or death counts exist
  anywhere in the dataset, only outbreak occurrence. This was initially
  missed and the dataset briefly, incorrectly marked accepted before
  being corrected once the fuller evidence was read — recorded in the
  decision log as a correction, not silently fixed.
- **WHO's Global Health Observatory** — checked as a comparison point
  once the accessibility-vs-structure pattern became visible. Also
  genuinely open, but confirmed (via a real API pull, not assumption)
  to be annual-only, sharing HDX's core limitation. This confirmed the
  pattern rather than introducing a new option: institutional
  aggregators of *someone else's* surveillance data tend to publish
  annual summaries, because that is what their own source material
  (WHO's narrative outbreak reports, cross-country indicators) actually
  is.
- **CDC NNDSS** — the only candidate, of everything actually tested
  with real requests, confirmed on both properties at once: genuinely
  open (`accessLevel: public`, verified with a plain unauthenticated
  `curl` request, no key or login), and genuinely weekly with real,
  large numeric case counts (verified directly — e.g. Chlamydia
  trachomatis infection, 2023 week 32: 37,668 current-period cases,
  878,685+ cumulative). This is not coincidence: CDC is a live,
  currently-operating government surveillance system, the same
  category of institution OpenDengue's own source data comes from,
  rather than an academic archive or a downstream aggregator of
  narrative reports.

### Scope decision: 2022–2026 only, not the full historical archive

CDC confirms weekly data exists back to 2014, which would exceed
ADR-009's 72-month eligibility floor if combined with 2022–2026.
However, a real format break exists at February 2022: CDC's own
announcement describes consolidating 42 separate per-disease-group,
per-year, **wide-format** tables into the current single **long-format**
table starting with 2022 data. Pulling a real pre-2022 resource
(2020's "Table 1F") confirmed this is messier than a simple reshape —
column names for the same disease/statistic are not even fully
consistent *within* a single file (e.g. `campylobacteriosis_current`
vs. `campylobacteriosis_current_1` in different rows of the same
table), almost certainly an artifact of inconsistent source-spreadsheet
headers accumulated over years of manual publication.

**Decision: use only the 2022–2026 single-table resource, not the
full historical archive.** Harmonizing the pre/post-2022 formats would
be an open-ended, unbounded data-wrangling task whose scope cannot yet
be estimated, and it is not what Milestone 9 is meant to test —
Milestone 9 validates whether *this project's architecture*
generalizes to a genuinely different real surveillance dataset, not
how much CDC-specific historical spreadsheet reconciliation this
project is willing to absorb. This is consistent with the Reviewer
Test (Freeze Document Section 32): the harmonization work would not be
implemented, evaluated, and defended with the same rigor as the rest
of this project without materially expanding Milestone 9's scope.

### Known, accepted consequence: forecasting eligibility

2022–2026 is approximately 4 years (~48 months), shorter than
ADR-009's 72-month eligibility floor. This means Forecasting will
correctly find **no eligible tracks** for any condition in this
dataset — not a bug, and not the same failure mode as HDX's rejection
(a missing measure entirely). This is an honest, informative M9
finding in its own right: the architecture correctly recognizes when
forecasting doesn't apply due to insufficient historical span, which
is a real, legitimate limitation to encounter and document, distinct
from a structural incompatibility. Load, Configure Roles, Validation,
Data Preparation, Exploratory Analysis, and Visualization are all
expected to exercise fully against this dataset's real structure
(weekly granularity; mixed national/regional/state location
granularity within one table, genuinely analogous to the `S_res`
mixed-resolution problem ADR-010's sanity check was built for, under a
different source's own convention).

## Consequences

- Milestone 9 proceeds against CDC NNDSS's 2022–2026 single-table
  resource. The M9 Dataset Compatibility Report (next step, before any
  implementation) assesses the exact schema against our role contract
  in full, per the 14-point structure already agreed, before any code
  changes are made.
- Forecasting is expected, and accepted in advance, to report zero
  eligible tracks for this dataset — this must be documented as a
  finding in Milestone 9's own deliverables (architecture validation
  summary, adaptation log), not treated as a defect to work around.
- The pre-2022 historical archive remains available and undiscarded
  should a future milestone want to take on the format-harmonization
  work deliberately, as its own scoped effort — this ADR does not rule
  that out, only excludes it from Milestone 9's current scope.
- Per ADR Discipline (Freeze Document Section 32), any revision to this
  selection is made as an explicit new ADR revision, not a silent edit.
