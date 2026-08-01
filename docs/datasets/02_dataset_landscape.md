# Dataset Landscape — National Extract vs. Temporal Extract

**Milestone:** 2 — Data Acquisition & Understanding
**Status:** Confirms already-locked decision (ADR-002); no new rationale
introduced here.

## Purpose of This Document

OpenDengue publishes three global summary extracts of the same underlying
data, at different levels of spatial/temporal resolution:

- **National Extract** — the best available estimate at country level
- **Temporal Extract** — the best available temporal resolution (weekly
  where possible), at whatever spatial level that resolution exists
- **Spatial Extract** — the best available spatial resolution (often
  Admin1/Admin2), at whatever temporal resolution that exists

The choice of which extract is the project's primary dataset was already
made and locked in **ADR-002 (Data Strategy)** during project planning,
before this milestone began:

> "Use the OpenDengue data resource, specifically the National Extract, as
> the foundation for Version 1... The National Extract aligns more closely
> with the intended analytical workflow by providing a consistent
> country-level view suitable for longitudinal analysis and forecasting.
> Although the Temporal Extract offers finer spatial resolution, its
> predominance of Admin2-level records (~93% of rows) introduces
> additional complexity outside the scope of Version 1..."
> — `docs/adr/ADR-002-data-strategy.md`

This document does not re-derive that decision. Its purpose is narrower:
to record what Milestone 2 actually found when acquiring and inspecting
both extracts, and confirm it is consistent with the locked rationale —
which is exactly the kind of validation checkpoint the Implementation
Roadmap calls for at this milestone.

## Verification

The Temporal Extract (v1.3) was downloaded alongside the National Extract
for this comparison only (it is not retained in `data/raw/` — see
"Scope Note" below) and its spatial-resolution (`S_res`) column was
tallied directly:

| Spatial resolution | Row count | Share |
|---|---|---|
| Admin2 | 2,642,777 | 93.2% |
| Admin1 | 151,794 | 5.4% |
| Admin0 (country level) | 40,451 | 1.4% |
| **Total** | **2,835,022** | 100% |

This confirms the ~93% figure already cited in ADR-002. Two further
observations from direct inspection, consistent with and supporting the
locked rationale:

- **Scale difference:** the Temporal Extract CSV is ~482 MB (2.84M rows)
  versus the National Extract's ~4.2 MB (29,873 rows) — a ~115x
  difference driven almost entirely by the Admin2 disaggregation.
- **Country-level analysis needs country-level rows:** even within the
  Temporal Extract, only 40,451 of 2.84M rows (1.4%) are already at
  Admin0. Extracting a country-level view from the Temporal Extract would
  require aggregating Admin1/Admin2 rows back up — introducing exactly
  the kind of preprocessing complexity ADR-002 already identified as
  disproportionate to Version 1's scope.

## Confirmation

Given the project's locked unit of analysis is **countries** (Freeze
Document Section 12, Data Strategy), and the verified figures above match
what ADR-002 already assumed, **no revision to ADR-002 is warranted**.
The National Extract remains the primary dataset for Version 1.

## Scope Note

Per ADR-002's own scope note, this is not a claim that the National
Extract is universally superior — it is the appropriate choice for this
project's country-level, longitudinal-analysis objectives. The Temporal
Extract remains a documented future extension for spatial (Admin2-level)
analysis, explicitly deferred (Freeze Document Section 33, "Deferred to
Future Versions"). Consistent with that deferral, the Temporal Extract
was inspected only for this verification and is not part of the
project's working dataset going forward; `data/download_national_extract.py`
does not acquire it.
