# Milestone 9 — Dataset Compatibility Report

**Dataset:** CDC NNDSS weekly data, single-table resource
(`data.cdc.gov/resource/x9gk-5huc`), 2022–2026
**Locked by:** [ADR-011](adr/ADR-011-m9-validation-dataset-selection.md)
**Status:** Pre-implementation. No pipeline code has been written or
modified based on this report — it exists to inform the implementation
decisions Milestone 9 will make next, per the agreed sequence (Access →
acquire → inspect → map → evaluate → decide adaptation → implement →
validate).

**Target condition for deep verification:** Chlamydia trachomatis
infection — chosen because it is a single, unstratified label with
strong volume, letting the dataset's real structure be assessed
without the added complexity of a condition's own case-definition
splits (several other conditions in this source, e.g.
Coccidioidomycosis, do have Confirmed/Probable/Total splits similar to
Bangladesh's in OpenDengue — noted below, not chosen as the primary
target). All findings below are from real pulled data (17,080 rows for
this one condition, all locations, full 2022–2026 span), not
documentation alone.

---

## 1. Exact file/schema

Pulled via Socrata SODA API, JSON format. Full column list for this
resource:

```
states, year, week, label, m1, m1_flag, m2, m2_flag, m3, m3_flag,
m4, m4_flag, location1, location2, geocode, sort_order
```

- `label` — condition name (string).
- `states` — location, at mixed granularity (see Section 4).
- `year`, `week` — ISO-style epidemiological year/week (strings,
  castable to int).
- `m1`–`m4` — four numeric measure columns per row, each with its own
  `_flag` companion column. Confirmed meaning (Section 5): `m1` =
  current week count, `m2` = previous-52-week maximum, `m3`/`m4` =
  year-to-date cumulative counts for two different reference years.
- `location1`/`location2` — appear to duplicate `states` under
  slightly different conditions (present on some rows, not others);
  not yet fully characterized — flagged as an open item, not a
  blocker.
- `geocode` — present only for individual-state rows (point
  coordinates), absent for national/regional aggregate rows.

## 2. Row count and date range

- 17,080 rows for this one condition alone (all locations, full span).
- Full resource: 1,974,840 rows, 139 distinct condition labels, 140
  distinct location strings (Section 4 explains why 140, not the
  expected ~57).
- Date range confirmed empirically: 2022 through week 35 of 2026
  (matches the current date, September 2026 — this is a live,
  currently-updating system, not a closed historical archive).

## 3. Temporal granularity actually present

**Weekly**, confirmed directly (not just claimed): every year/week
combination for a stable national-level location has exactly one row,
with 52 weeks in 2022–2024, 53 in 2025 (an ISO leap week), and 35 so
far in 2026. This is empirically the same granularity claim OpenDengue
itself makes for its sub-annual rows, verified the same way.

## 4. Location structure

Mixed granularity within a single column, genuinely analogous to the
`S_res` problem ADR-010's sanity check was built for, under a
different source's own convention:

- Individual US states and territories (e.g. `Wyoming`, `Guam`,
  `American Samoa`, `Commonwealth of Northern Mariana Islands`)
- Census-style regional aggregates (e.g. `East North Central`,
  `Middle Atlantic`)
- National-level aggregates, under **three different naming
  conventions across time**: `TOTAL` and `US RESIDENTS` for
  2022–2024, `Total` for 2025–2026 (confirmed: these do not overlap
  in time, so this is a convention change mid-series, not a
  duplication to reconcile within one period)
- **Genuine casing inconsistency**: the same real-world entity appears
  as both `Alabama` and `ALABAMA` (and equivalently for every other
  state) — confirmed directly; this alone explains most of the "140
  distinct locations" figure for what is really ~57 real places.

`TOTAL` and `US RESIDENTS` are **not duplicates of each other** —
verified directly by comparing matched weeks: a small, consistent
difference exists (`TOTAL` runs higher, matching CDC's own
documentation that `TOTAL` includes territories and non-US residents
that `US RESIDENTS` excludes). Selecting the correct single national
series requires choosing `TOTAL` (not `US RESIDENTS`) for 2022–2024
and `Total` for 2025–2026, case-normalized.

## 5. Count semantics

`m1` (current week) is the natural Surveillance Measure candidate.
Its flag column carries real, documented meaning (per CDC's own
footnote key, confirmed against the actual data): `-` = no reported
cases (i.e., a true zero, 12,366 of 17,080 rows), `U` = unavailable —
the reporting jurisdiction could not send or CDC could not process the
data (genuinely missing, not zero, 66 rows). Critically: **when the
flag is `-` (true zero), `m1` itself is stored as `null`, not `0`** —
confirmed directly on Wyoming's early-2022 weeks. This is a real,
well-defined semantic gap between "null" and "zero" that any user of
this field must resolve, and it does not exist in OpenDengue's own
data in this form.

## 6. Missingness

27.0% of all rows (4,615 of 17,080) have `m1 = null` for this
condition. Of these, the overwhelming majority (per Section 5) are
true zeros requiring a fill-with-0 step, not missing data requiring
exclusion — but distinguishing the two requires reading the flag
column, not the count column alone. Genuinely unavailable data (flag
`U`) is a small minority (66 rows, 0.4%).

## 7. Duplicates

None at the natural grain. Verified directly: grouping by
`(states, year, week)` for this condition produces a maximum of 1 row
per combination across all 17,080 rows — no exact duplicates to
resolve, unlike the location-naming issue in Section 4 (which is a
naming inconsistency, not duplicate rows).

## 8. Stratification (do multiple rows represent different things?)

For the chosen target condition (Chlamydia trachomatis infection), no
— one row per (location, year, week) is the complete unit. However,
**this is condition-dependent**: several other labels in this same
resource are explicitly stratified by case-definition, directly
analogous to Bangladesh's Confirmed/Total split in OpenDengue — e.g.
`Coccidioidomycosis`, `Coccidioidomycosis, Confirmed`,
`Coccidioidomycosis, Probable`, `Coccidioidomycosis, Total` (and, with
the same casing quirk as Section 4, `Coccidioidomycosis, total`
lowercase, appearing as a distinct label). A future extension of this
work targeting one of those conditions would need the same
case-definition-track detection logic M7's `eligibility.py` already
implements for OpenDengue — a reassuring sign the existing design
generalizes, not something to build from scratch.

## 9. Mapping to our three required roles (ADR-004)

| Role | OpenDengue | CDC NNDSS candidate mapping |
|---|---|---|
| Time | `calendar_start_date`/`calendar_end_date` | `year` + `week` (needs combining into one period column — a small, generic transformation, not dataset-specific logic) |
| Location | `adm_0_name` (country) | `states`, after case-normalization and selecting one national-level convention per era (Section 4) |
| Surveillance Measure | `dengue_total` | `m1`, after null-with-dash-flag → 0 imputation (Section 5) |

All three roles have a genuine, defensible mapping. None require
inventing a role the dataset doesn't actually have (contrast with
HDX's rejection, where no mapping existed for Surveillance Measure at
all).

## 10. M5 (EDA) compatibility

Expected to work cleanly once the Section 5/9 transformations are
applied: `m1` becomes a genuine numeric column supporting real
descriptive statistics (mean, median, distribution), unlike HDX's
degenerate all-`1`s problem. The mixed-granularity location field
(Section 4) is the main risk to descriptive statistics being
misleading if used before normalization — e.g., naively including
both `Alabama` and regional aggregates like `East North Central` in
the same "distinct location" count would double-count populations.

## 11. M7 (Forecasting) compatibility

**Confirmed, not just predicted**: combining the two national-era
series (`TOTAL` 2022–2024 + `Total` 2025–2026, case-normalized) yields
**244 continuous weekly observations ≈ 56.4 months** — short of
ADR-009's 72-month eligibility floor. This matches ADR-011's accepted
consequence exactly: Forecasting will correctly report zero eligible
tracks for this dataset within its locked 2022–2026 scope. This is
now empirically confirmed, not just anticipated from the resource's
overall date range.

## 12. Adaptations required, classified

- **None**: the three-role contract itself (Time/Location/Surveillance
  Measure) requires no new roles or contract changes.
- **Configuration-only**: selecting `label = 'Chlamydia trachomatis
  infection'` (or any other single condition) as the working subset,
  the same way OpenDengue's own pipeline is configured per-country,
  not a code change.
- **Small, generic adaptation** (would benefit other future datasets
  too, not just this one): case-insensitive location normalization
  (already precedented — `population_lookup.py` already does exact
  case-insensitive matching for a different purpose); a null-with-flag
  to zero/missing resolution step for the count column.
- **Dataset-specific adaptation**: combining `year` + `week` into one
  period value (ISO week semantics, not OpenDengue's calendar-date
  intervals); selecting the correct national-level label per era
  (`TOTAL` vs `Total`) rather than a single constant string.
- **Explicitly out of scope for Milestone 9** (per ADR-011): full
  historical harmonization across the pre-2022 wide-format archive.
  Not attempted, not needed for the mappings above.

## 13. ADR conflicts

None found. The three-role model (ADR-004) accommodates this source
without modification. ADR-009's eligibility floor is not violated by
this dataset failing to meet it — the floor still applies uniformly;
this dataset simply doesn't clear it, which ADR-011 already accepted
in advance as a legitimate outcome. No existing ADR's stated scope or
decision is contradicted by anything found here.

## 14. Recommendation

**Proceed.** Every role has a genuine, defensible mapping (unlike HDX).
Every adaptation identified is bounded and well-understood (unlike the
pre-2022 archive's open-ended column-naming mess). The one expected
limitation (forecasting eligibility) was anticipated and accepted in
ADR-011 before this report was written, and is now confirmed
empirically rather than merely predicted. This dataset is ready for
the implementation phase of Milestone 9.
