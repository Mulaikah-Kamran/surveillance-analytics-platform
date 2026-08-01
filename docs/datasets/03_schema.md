# Schema Documentation — OpenDengue National Extract (v1.3)

**Milestone:** 2 — Data Acquisition & Understanding
**Status:** Documentation only. No loading or role-assignment code is
implemented here — that begins in Milestone 3 (Role Configuration).

## Shape

29,873 rows × 16 columns. One row = one reported case count for one
country over one reporting interval.

## Column-by-Column

| Column | Type (pandas) | Missing (National Extract) | Meaning |
|---|---|---|---|
| `adm_0_name` | string | 0% | Country name (text), e.g. `SRI LANKA` |
| `adm_1_name` | float64 (always `NaN`) | 100% | Admin1 (province/state) name — only populated in the Spatial/Temporal extracts, not the National Extract |
| `adm_2_name` | float64 (always `NaN`) | 100% | Admin2 (district) name — same as above |
| `full_name` | string | 0% | Full location name; identical to `adm_0_name` in every row of this extract (verified) |
| `ISO_A0` | string | 0% | ISO 3166-1 alpha-3 country code, e.g. `LKA` |
| `FAO_GAUL_code` | int64 | 0% | FAO Global Administrative Unit Layer code for the country; one fixed value per country |
| `RNE_iso_code` | string | 0% | Matching country code for the `rnaturalearth` shapefile package; identical to `ISO_A0` in the sampled data |
| `IBGE_code` | float64 (always `NaN`) | 100% | Brazilian statistics-agency subdivision code — populated only for Brazil-specific subnational records elsewhere in OpenDengue, not relevant at national level |
| `calendar_start_date` | string, `YYYY-mm-dd` | 0% | Start date of the reporting interval |
| `calendar_end_date` | string, `YYYY-mm-dd` | 0% | End date of the reporting interval |
| `Year` | int64 | 0% | Calendar year associated with the record |
| `dengue_total` | float64 | 0% | Reported dengue case count for the interval — the surveillance measure |
| `case_definition_standardised` | string | 0% | Standardized case definition category: `Total`, `Suspected`, `Confirmed`, `Probable`, `Probable and confirmed`, `Suspected and confirmed` (plus one inconsistently-cased `confirmed` — see the data quality profile) |
| `S_res` | string | 0% | Spatial resolution of the row; always `Admin0` in the National Extract |
| `T_res` | string | 0% | Temporal resolution of the reporting interval: `Week`, `Month`, or `Year` |
| `UUID` | string | 0% | Identifier of the **source data batch** the row came from (see below) — not a per-row identifier |

## A Note on `UUID`

`UUID` looks like a row identifier but is not one: across 29,873 rows
there are only 943 distinct `UUID` values. One `UUID` typically
identifies a single ministry-of-health bulletin, WHO regional summary, or
literature source that was digitized into many rows (one per reporting
interval it covered) — e.g. `WHOPAHO-ALL-19802024-Y03-00` alone accounts
for 1,837 rows spanning many countries and years. `UUID` is documented
here because it is directly relevant to the Optional `Identifier` role
(see below), and because it is the traceability key back to
`sourcedata_V1.3.csv` in the OpenDengue repository, if a specific row's
provenance ever needs auditing.

The true row-level unique key, verified directly against this file, is
the combination of **(`adm_0_name`, `calendar_start_date`,
`calendar_end_date`)** — zero duplicate combinations exist in the
29,873 rows.

## Mapping to the Platform's Analytical Role Model

ADR-004 locks a minimal role model: Required roles **Time**, **Location**,
**Surveillance Measure**; Optional role **Identifier**. Confirming that
model against this actual schema:

| Role | Status | Candidate column(s) | Notes |
|---|---|---|---|
| **Time** | Required | `calendar_start_date`, `calendar_end_date` | Represented as a reporting *interval*, not a single date — see `04_time_representation.md` for how ADR-007 already resolves this |
| **Location** | Required | `adm_0_name` (or `ISO_A0`) | Straightforward at country level; `adm_1_name`/`adm_2_name` are irrelevant here since they are always empty in the National Extract |
| **Surveillance Measure** | Required | `dengue_total` | Matches ADR-004's rationale for the generic "Surveillance Measure" naming — this file happens to report a case *count*, but the column name (`dengue_total`) is dataset-specific, not a fixed schema assumption |
| **Identifier** | Optional | `UUID` | Available, but — as shown above — identifies a source batch, not a row. This actually reinforces ADR-004's own stated rationale: identifier uniqueness for this dataset is genuinely implicit via location + time, not via `UUID` |

No assumptions in ADR-004's role model are contradicted by the actual
schema. One clarification worth recording for Milestone 3: because
`UUID` is many-to-one with rows, if it is ever surfaced in the UI as the
optional Identifier, it should be presented as a *source reference*, not
a row identifier — assigning it the Identifier role would not, by
itself, guarantee row uniqueness the way a true identifier column would.

## Additional (Generically-Handled) Variables

Per the Freeze Document's Data Model Philosophy, everything outside the
four modeled entities is handled generically by profiling/EDA rather than
being semantically understood by the platform. In this schema that means:
`FAO_GAUL_code`, `ISO_A0`, `RNE_iso_code` (all alternate location codes),
`Year` (derivable from the time columns), `case_definition_standardised`,
`S_res`, and `T_res`. None of these require special-casing in the role
model; they remain visible to the user for profiling and EDA once those
modules exist.
