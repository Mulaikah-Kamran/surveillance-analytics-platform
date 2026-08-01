# Validation Dataset Investigation (R-001)

**Milestone:** 2 — Data Acquisition & Understanding
**Status:** Investigation only. Per the Freeze Document's explicit
instruction, the final validation dataset is **not locked** in this
milestone unless the evidence clearly supports doing so — it does not
here, so none is selected.

## Why This Matters

ADR-002 and the Evaluation Question both require validating the
platform's workflow and architecture against one additional surveillance
dataset (Freeze Document Section 7, 12; Milestone 9's later deliverable).
Risk **R-001** already flagged, before this milestone began, that the
originally-considered candidate (PAHO PLISA) might not satisfy Version
1's reproducibility/accessibility requirements, and named the mitigation:
"During Phase 2, evaluate alternatives such as Project Tycho or
HDX-hosted datasets before locking the validation dataset." This document
carries out that mitigation.

## Candidate 1: PAHO PLISA

**Status: confirmed inaccessible**, consistent with the risk already
recorded before this milestone. PLISA's data portal returned repeated
403 Forbidden / Varnish cache errors during evaluation (per R-001).
Re-checking during this milestone did not change that finding — PLISA is
not treated as a viable validation dataset for Version 1.

There is a further structural reason PLISA would have been a poor fit
regardless of accessibility: PLISA covers the Americas (PAHO's mandate),
not South Asia, so it would not offer country overlap with the study
dataset even if fully accessible.

## Candidate 2: Project Tycho

**Publicly accessible:** yes. Project Tycho publishes per-country,
per-condition datasets with a DOI, a standard citation, a documented CSV
format, and both bulk-download and API access
(`https://www.tycho.pitt.edu/`). Data is licensed CC BY 4.0.

**Reproducibility:** high — each dataset has a stable DOI-backed
download URL and a fixed, versioned format.

**Schema compatibility:** structurally compatible in principle — Project
Tycho's dengue datasets report per-country, per-period case counts, which
the platform's minimal role model (Time, Location, Surveillance Measure)
can accommodate without redesign.

**Coverage for South Asian countries — the limiting factor:** Project
Tycho's dengue data was last updated no later than 2012, and for the
specific countries selected in this project it stops even earlier:

| Country | Project Tycho dengue coverage |
|---|---|
| Sri Lanka | 1965–2006 |
| Bangladesh | 1980–2006 |
| Maldives, Nepal | not confirmed as separately published pre-compiled datasets during this search |

This means a Project Tycho validation run would only exercise the
architecture on historical data (pre-2007), with no temporal overlap
with OpenDengue's recent reporting — a real limitation for demonstrating
workflow portability on *current* surveillance data, though not
necessarily disqualifying for an architecture-validation exercise, which
only needs a structurally different, genuinely reproducible dataset.

**A more serious independence concern, found directly in this project's
own data profiling (`../datasets/05_data_quality_profile.md`):** Project
Tycho is not fully independent of OpenDengue for two of this project's
selected countries. The National Extract's `UUID` source-prefix field
shows `TYCHO`-sourced rows already present within OpenDengue's own
compiled data for **Sri Lanka (36 rows)** and **Bangladesh (1 row)** —
meaning Project Tycho was itself one of the inputs OpenDengue's authors
used when building those countries' records. Using Project Tycho as the
"second, independent" validation dataset for those countries would
partially validate the workflow against data that already flows into the
primary dataset, undermining the intent of an independent architecture
validation. This does not disqualify Project Tycho outright (Maldives and
Nepal show no Tycho-sourced rows in the primary dataset, for instance),
but it is a genuine caveat that a external reviewer would reasonably raise,
so it is recorded here rather than discovered later.

## Candidate 3: HDX (Humanitarian Data Exchange)

**Publicly accessible:** yes, in general — HDX is UN OCHA's open data
platform, no authentication required for public datasets.

**Reproducibility and schema accessibility:** variable by design. HDX is
a multi-provider marketplace, not a single standardized source like
OpenDengue or Project Tycho — format, granularity, and documentation
quality differ dataset-by-dataset. One confirmed, promising example
found during this search: *Philippine Dengue Cases and Deaths*
(Department of Health–Epidemiology Bureau, via HDX), covering 2016–2021
as yearly CSV resources, sourced directly from a ministry of health
rather than compiled/harmonized the way OpenDengue is.

**Relevance to this project's study countries:** none of the
South-Asia-specific candidates surfaced during this search were
South Asian — the clearest HDX dengue example found is the Philippines,
outside this project's selected country set. HDX would need a targeted,
country-by-country search (not performed as part of this milestone,
consistent with the instruction to evaluate alternatives "only to the
extent required by the frozen roadmap," not to exhaustively survey HDX)
to determine whether a South-Asia-relevant, schema-accessible dengue
dataset exists there.

**Structural fit for the "differs meaningfully in structure" criterion
(Freeze Document Section 12):** genuinely promising if a South Asian
equivalent exists — HDX datasets are typically raw ministry exports
rather than OpenDengue-style harmonized extracts, which is exactly the
kind of structural difference the validation dataset selection criteria
call for.

## Summary Table

| Candidate | Publicly accessible | Reproducible | Compatible structure | Sufficiently different from primary | South Asia coverage confirmed | Verdict |
|---|---|---|---|---|---|---|
| PAHO PLISA | No (confirmed 403/Varnish) | N/A | N/A | N/A | No (Americas-only mandate) | Excluded |
| Project Tycho | Yes | Yes | Yes | Partially — some overlap with OpenDengue's own sources for Sri Lanka/Bangladesh | Yes (historical, pre-2007, for Sri Lanka/Bangladesh only) | Candidate, with a caveat |
| HDX | Yes (platform-level) | Varies by dataset | Varies by dataset | Likely yes, where available | Not yet confirmed | Needs targeted follow-up, not yet evaluated in depth |

## Why No Dataset Is Locked Yet

Per the explicit Milestone 2 instruction, the validation dataset is not
finalized here unless evidence clearly supports it. It doesn't: Project
Tycho is reproducible and schema-compatible but has both a coverage-recency
limitation and a partial-independence concern for two of the four selected
countries; HDX has at least one promising *structural* precedent but no
confirmed South Asian dengue dataset was found within this milestone's
scope. This is left as an open item for the Architecture Validation
milestone (Milestone 9), which is where the validation dataset is
actually acquired and exercised — this document exists so that milestone
doesn't have to re-investigate PLISA's accessibility or re-discover the
Tycho independence caveat from scratch.
