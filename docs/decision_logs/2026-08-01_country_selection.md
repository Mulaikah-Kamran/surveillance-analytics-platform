# Decision Log — Study Country Selection (Milestone 2)

**Date:** 2026-08-01
**Status:** Proposed — evidence-based, but treated as pending
confirmation before it is exercised in Milestone 3+, since it fixes the
concrete study dataset for the rest of Version 1.
**Scope:** Selects the 3–5 South Asian countries that form the "Study
Dataset" referenced in ADR-002 and Freeze Document Section 12. Does not
revisit the extract choice (National Extract; see `02_dataset_landscape.md`)
or the role model (ADR-004).

## Locked Inputs to This Decision

- **Unit of analysis:** Countries (Freeze Document Section 12).
- **Target size:** 3–5 countries (ADR-002).
- **Selection criteria:** the 8 objective requirements in Freeze Document
  Section 13 (Chapter 3.1), reproduced below. Requirements 1, 2, 3, 5, 6,
  and 8 are properties of the *dataset*, not of any individual country,
  and are already satisfied identically by every candidate (all 8 South
  Asian countries draw from the same OpenDengue National Extract). The
  requirements that actually differentiate between candidate countries
  are **4 (Sufficient Historical Coverage)** and **7 (Workflow
  Compatibility)** — which in practice means enough volume, resolution,
  and reporting consistency to support quality assessment, cleaning,
  descriptive epidemiology, and forecasting. This decision log applies
  those two criteria using the profile in `../datasets/05_data_quality_profile.md`.
- **Explicit instruction (Milestone 2 scope):** country selection must
  not be hardcoded just for being South Asian, and if Pakistan turns out
  unsuitable, that must be stated honestly rather than worked around.

## Candidate Pool

All 8 SAARC countries are present in the National Extract: Afghanistan,
Bangladesh, Bhutan, India, Maldives, Nepal, Pakistan, Sri Lanka.

## Applying Criteria 4 and 7

| Country | Historical coverage | Reporting consistency | Completeness | Verdict |
|---|---|---|---|---|
| **Sri Lanka** | 1965–2024, 49 of 60 years reported | Mostly weekly (455/579 rows); single, stable case definition (`Total`) throughout | 579 rows — by far the deepest record; near-zero zero-value share (0.5%) | **Select** |
| **Bangladesh** | 1980–2025, 42 of 46 years | Mostly monthly (183/209); case definition mixes `Confirmed`/`Total` over time | 209 rows; MOH-sourced majority | **Select** |
| **Maldives** | 1985–2025, 40 of 41 years | Mostly monthly (171/196); single case definition (`Total`) throughout | 196 rows; MOH-sourced majority | **Select** |
| **Nepal** | 1985–2025, 41 of 41 years, no gaps | Mixed monthly/annual; two case definitions (`Total`/`Confirmed`) | 76 rows; moderate zero-share (27.6%) | **Select** |
| **India** | 1991–2025, 35 of 35 years, no gaps | 34 of 35 rows are *annual* resolution (1 monthly row) — insufficient for the sub-annual trend/seasonality analysis the workflow needs | Only 35 rows total, thinnest of all 8 despite the longest continuous coverage claim | **Exclude** — see note below |
| **Pakistan** | 1994–2025, 26 of 32 years, 6-year max gap | Weakest of the 8: no MOH-sourced rows at all (`LITERATURE`/`WHO` only); three distinct case definitions in use (`Total`, `Suspected and confirmed`, `Confirmed`) | 43 rows; over half at annual resolution | **Exclude** — stated honestly per Milestone 2 instructions |
| **Bhutan** | 1985–2024, 40 of 40 years | Mostly annual (39/49); single-country small-population reporting | 49 rows; highest zero-value share of the 8 (44.9%) | **Exclude** (marginal) |
| **Afghanistan** | 2021–2025 only — 5 years | Reasonable weekly/monthly mix within that window | 94 rows, but the entire record spans a single 5-year window | **Exclude** — fails historical-coverage requirement outright |

## Selection: Sri Lanka, Bangladesh, Maldives, Nepal

This is 4 countries, within the locked 3–5 range. All four have (a) at
least four decades of history, (b) predominantly sub-annual reporting
(weekly or monthly, not just yearly), and (c) either a single stable
case definition throughout or a documented, limited set of two.

## Honest Notes on the Two Largest Exclusions

**Pakistan** is explicitly unsuitable by the objective criteria applied
here: it is the only candidate with zero direct ministry-of-health-sourced
rows (compiled entirely from `LITERATURE` and `WHO` secondary sources),
the only one spanning three distinct case definitions rather than one or
two, and has a 6-year reporting gap — the largest of any candidate except
the already-excluded Afghanistan. This is stated plainly per the
milestone's explicit instruction, rather than working around it.

**India** is a harder case, and worth being explicit about rather than
silently dropping. Despite having the largest dengue burden in the region
and a clean, gap-free 35-year span, its National Extract record is almost
entirely annual (34 of 35 rows) — one datapoint per year. That is
sufficient for a long-run trend line, but not for the seasonality and
sub-annual forecasting analysis the workflow's later milestones (EDA,
Forecasting) are designed around, which is exactly what "Workflow
Compatibility" (criterion 7) is meant to catch. India is excluded from
the Version 1 study dataset on that basis, not on data-quality grounds —
its data isn't wrong, it's just at the wrong resolution for this
project's forecasting objective. This is recorded explicitly since it's
a less obvious exclusion than Pakistan's, and worth a second opinion.

## What Would Change This

If a future milestone's forecasting approach turns out to work
adequately at annual resolution alone (unlikely, but not yet tested),
India would be a reasonable 5th country to add without any change to
this decision log's underlying criteria — the country pool and the
scoring method would carry over unchanged.

## Status

This selection is evidence-based and internally consistent with the
frozen Chapter 3.1 criteria, but is recorded as **proposed** rather than
finalized, since it fixes the concrete study dataset for the rest of
Version 1 and India's exclusion in particular is a judgment call worth a
second look before Milestone 3 begins.
