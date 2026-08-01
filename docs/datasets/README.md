# Dataset Documentation

Documentation produced during **Milestone 2 — Data Acquisition &
Understanding**. This milestone is exploratory: it documents what the
data is, where it comes from, and what it looks like, without
implementing any preprocessing, cleaning, or analytical logic (those
begin in Milestone 4, per the Implementation Roadmap, Freeze Document
Section 29).

## Contents

1. [`01_acquisition.md`](01_acquisition.md) — source, citation, version,
   licensing, and download procedure for the OpenDengue National Extract.
2. [`02_dataset_landscape.md`](02_dataset_landscape.md) — why the
   National Extract (not the Temporal Extract) is the project's primary
   dataset, grounded in the already-locked ADR-002.
3. [`03_schema.md`](03_schema.md) — column-by-column schema
   documentation and mapping to the platform's analytical role model
   (Time / Location / Surveillance Measure / Identifier).
4. [`04_time_representation.md`](04_time_representation.md) — how
   OpenDengue represents time, and the (already-locked, ADR-007)
   decision for deriving a representative analysis date.
5. [`05_data_quality_profile.md`](05_data_quality_profile.md) — initial,
   observation-only data quality profile (missingness, duplicates,
   coverage, anomalies) — no cleaning performed here.
6. [`06_validation_dataset_investigation.md`](06_validation_dataset_investigation.md) —
   investigation of candidate validation datasets (R-001), including
   confirmation that PLISA remains inaccessible.

Country selection (Milestone 2, Chapter 3 criteria) is formally locked
as [ADR-008](../adr/ADR-008-study-country-selection.md), with the full
per-country profiling behind it in
[`../decision_logs/`](../decision_logs/).
