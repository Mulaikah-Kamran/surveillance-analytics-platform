# Decision Log — Milestone 9 Validation Dataset Evaluation

**Date started:** 2026-09-09
**Status:** In progress. HDX's disease-outbreaks dataset, initially
accepted, was corrected to REJECTED once the primary source's own
stated limitations were read in full (see below) — the earlier
acceptance was based on incomplete evidence and is retracted, not
left standing alongside the correction. CDC NNDSS (candidate 3) is
now the leading candidate, with one open verification remaining
(historical depth across combined yearly resources) before it can be
locked via a formal ADR.
**Scope:** Selects the "one additional surveillance dataset" the
Evaluation Question (PFD Section 7) and Milestone 9 (Section 29)
require, against the four criteria in PFD Section 12: public
accessibility, reproducibility, compatible analytical structure, and
sufficient variable richness that differs meaningfully in structure
from OpenDengue (not a near-duplicate).

## Precedent this evaluation follows

The Risk Register's R-001 already modeled exactly this situation once
during planning: the originally-considered validation dataset (PAHO
PLISA) was rejected after confirming unreliable public access
(repeated 403 Forbidden/Varnish cache errors), with the mitigation
explicitly naming Project Tycho and HDX-hosted datasets as
alternatives to evaluate. This log applies the same standard —
accessibility is verified empirically, not assumed from a source's
reputation — to those two named alternatives.

---

## Candidate 1: Project Tycho — REJECTED (accessibility)

### Structural evaluation (documentation-level, before any access attempt)

Tycho's non-dengue conditions (92 US notifiable diseases: measles,
tuberculosis, diphtheria, pneumonia, etc.) were identified as a strong
structural candidate, specifically the **United States Measles**
dataset (436,932 records, 1888–2002, DOI
`10.25337/T7/ptycho.v2.0/US.14189004`):

- **Non-dengue disease** — satisfies "doesn't duplicate OpenDengue."
  (Tycho also hosts dengue data for 99 countries, which would *not*
  have satisfied this criterion — deliberately not the candidate
  considered here.)
- **US state/city geography** — genuinely different from OpenDengue's
  country-level structure, without requiring any change to our
  Location role, which is a generic column, not country-specific.
- **Weekly granularity**, confirmed independently across three sources
  (the official data.gov catalog entry, Pitt's own announcement
  material, and an unaffiliated third-party researcher's published
  analysis actually loading and reshaping real Tycho measles data into
  `YEAR, WEEK, STATE, Cases`).
- **Real numeric case counts**, not presence/absence flags — confirmed
  by the same third-party analysis.
- **Richer metadata schema** than OpenDengue: `Fatalities`,
  `DiagnosisCertainty`, `PlaceOfAcquisition`, `AgeRange`,
  `Subpopulation`, `PartOfCumulativeCountSeries`.
- Citable dataset and methodology paper (Van Panhuis, Cross, Burke).

On structure alone, this was assessed as a strong candidate — arguably
stronger than the eventual HDX candidate, since it preserves the
"continuous surveillance count time series" shape our pipeline is
built around, rather than an event-based structure.

### Accessibility evaluation — the actual blocking finding

Both the live query API and the pre-compiled dataset ZIP download
require an authenticated account (`"You must sign in to download data
from Project Tycho."`). Attempting to complete registration surfaced a
convergent pattern of failures across **seven independent attempts**,
from unrelated networks, countries, and access methods:

1. User's home network — `ERR_CONNECTION_REFUSED`
2. User's mobile hotspot (different network entirely) — same error
3. User's VPN (US exit node) — `502 Bad Gateway`
4. A second person's university network — failed
5. That same person's mobile hotspot — failed
6. That same person's VPN — failed
7. Claude's own sandbox environment, a real browser (Playwright/
   Chromium) request directly to `/accounts/register/`, no VPN, no
   geographic dependency at all — **HTTP 503 Service Unavailable**,
   zero form fields returned

Static documentation pages on the same domain (e.g. `/dataset/api/`)
were fetched successfully, repeatedly, throughout this same window —
confirming the domain is not globally down. The failures are
specific to the *authenticated* registration/login subsystem, not the
site as a whole, and reproduce across every network and method tried,
including one with no geographic or ISP dependency whatsoever
(Claude's own sandbox).

### Verdict: REJECTED

Seven independent failures at the account-creation layer, from
unrelated vantage points, is not a transient blip attributable to any
one network — it is convergent evidence that Tycho's authentication
infrastructure is currently unreliable. This directly fails two of
the four locked selection criteria (public accessibility,
reproducibility), regardless of how well the Measles dataset's
structure otherwise fits. This is the same category of finding that
sank PLISA in R-001, and is treated the same way: documented honestly,
not forced past with further workarounds.

**No further Tycho troubleshooting is planned.** If Tycho's account
system becomes reliably reachable in the future, this candidate could
be revisited, but it is not being pursued further now.

---

## Candidate 2: HDX — "A global dataset of pandemic- and epidemic-prone disease outbreaks"

### Accessibility

Confirmed genuinely open: HDX (data.humdata.org, run by UN OCHA's
Centre for Humanitarian Data) requires no registration for public
datasets — direct download button, and a public, unauthenticated API
(`package_show`/`package_search`) for programmatic access. This is
the opposite experience from Tycho: no access attempt has failed.

### Structure

Sourced from WHO's Disease Outbreak News and Coronavirus Dashboard;
published as a peer-reviewed data paper (Torres Munguía et al.,
*Scientific Data*, 2022, DOI `10.1038/s41597-022-01797-2`). Covers
2,227 outbreak records across 70 diseases and 233 countries/
territories, January 1996 – March 2022.

**Confirmed directly from the authors' own dataset description**: the
unit of analysis is one row per (country, disease, **year**) — "a
specific country cannot have two outbreaks related to the same
disease in the same year." This is annual-only, with no sub-annual
granularity anywhere in the source. It is also genuinely sparse
(~50 outbreak-year records per year, spread across 233 countries and
70 diseases) rather than a dense panel where every location reports
every period, unlike OpenDengue.

### Honest assessment against M9's actual purpose

This structure would very likely satisfy Load/Configure Roles/
Validation/Data Preparation/EDA/Visualization without difficulty —
but for Forecasting specifically, it would almost certainly produce
**zero eligible tracks across the entire dataset**, not a
country-specific limitation like Nepal's in the real OpenDengue data,
but structurally, everywhere: ADR-009's eligibility floor requires
≥72 months of *continuous sub-annual* data, and this source has
neither sub-annual resolution nor continuous multi-year runs for most
country-disease pairs at all.

This is still a legitimate M9 finding — confirming the architecture
correctly recognizes when forecasting doesn't apply, rather than
breaking, is itself informative — but it is a materially weaker test
of "does the forecasting stage generalize" than Tycho's continuous
weekly series would have been, which would have produced real,
computed SARIMA results on a genuinely different dataset. This
trade-off (accessibility vs. exercising the full pipeline) was
weighed explicitly, not defaulted into by picking whichever candidate
happened to be reachable.

### Verdict: REJECTED (corrected — the initial acceptance below was
based on incomplete evidence)

This candidate was initially marked ACCEPTED, reasoning that an
annual-only, sparse structure would still exercise Load/Configure/
Validate/Data Preparation/EDA/Visualization, with only Forecasting
affected. That assessment was incomplete. Reading the primary source
in full (Torres Munguía et al.'s own paper, not just its abstract and
a Figshare description) surfaced a more fundamental problem, stated
by the authors themselves:

> "information exclusively captures the occurrence of an outbreak...
> and not the intensity... does not reflect... the number of cases or
> deaths associated to the outbreak, which are not available in the
> DONs."

The dataset's confirmed full column schema (`Country, iso2, iso3,
Year, icd10n/103n/104n [+codes], icd11 fields, Disease, DONs,
Definition`) contains no case-count or death-count field anywhere.
Combined with the earlier finding that the COVID-sourced portion is
binary (1 if any case that year, 0 otherwise), this means **no
numeric magnitude column exists in this dataset at all** — not just
insufficient granularity for forecasting, but no valid mapping for
the required Surveillance Measure role (ADR-004) in the first place.
Mapping it to the presence-indicator would make every value `1`,
degenerate for EDA's own descriptive statistics, not just forecasting.

This is a materially different, more serious finding than "forecasting
will report zero eligible tracks" (which remains a legitimate,
survivable M9 finding for a source that does have a genuine measure).
It fails PFD Section 12's "compatible analytical structure" criterion
outright, not just the forecasting-specific portion of it. The lesson
carried forward: verify a candidate's actual measure column against
the primary source directly (not a secondary description or abstract)
before accepting, since "the paper's own authors describe the
Measurement(s) as 'disease outbreaks'" was not, on its own, sufficient
signal that a usable numeric measure existed.

**Superseded initial assessment (retained for the record, not
authoritative):**

~~Proceeding with this dataset. The M9 Dataset Compatibility Report
(next step, before any implementation) will assess the exact
structure against our role contract in full, including confirming
this forecasting-eligibility expectation empirically once the real
file is acquired, rather than resting on the paper's description
alone.~~

---

## Candidate 3: CDC NNDSS (National Notifiable Diseases Surveillance System)

### Rationale for this direction

Both prior candidates failed for structural reasons related to their
category, not bad luck: general-purpose archives (Tycho) and
humanitarian data aggregators (HDX) are not primarily built around
continuous case-count reporting the way a country's own notifiable-
disease surveillance system is. This candidate instead targets a
government-run, currently active surveillance system directly — the
same category of institution that produces OpenDengue-like data in
the first place, just for a different country and different diseases.

### Accessibility — confirmed directly with real data, not just documentation

`https://data.cdc.gov/resource/x9gk-5huc.json` (Socrata SODA API,
`accessLevel: public` per its own catalog.data.gov metadata) returns
real data via a plain unauthenticated `curl` request — no API key, no
login, no registration. Verified directly:

```
curl "https://data.cdc.gov/resource/x9gk-5huc.json?\$limit=5"
-> HTTP 200, real rows returned instantly
```

### Structure — confirmed with real pulled data

- **Weekly granularity**, confirmed empirically (`year`, `week`
  fields with real values, not just claimed in documentation).
- **Real, large, meaningful numeric case counts** — e.g. Chlamydia
  trachomatis infection, 2023 week 32: current-period count 37,668,
  cumulative counts in the hundreds of thousands. This directly
  resolves the exact problem that sank Candidate 2 — a genuine
  numeric Surveillance Measure exists.
- **Non-dengue, rich disease catalog** — confirmed via direct query:
  Anthrax, multiple arboviral diseases (Chikungunya, Eastern/Western
  equine encephalitis, Jamestown Canyon, La Crosse, Powassan, St.
  Louis encephalitis, West Nile), Babesiosis, Botulism (3 subtypes),
  Brucellosis, Campylobacteriosis, and more.
- **Mixed location granularity within one table** (`states` field
  contains national totals, regional aggregates, and individual
  states together, e.g. "TOTAL", "US RESIDENTS", "NEW ENGLAND",
  "CONNECTICUT") — genuinely analogous to the mixed-resolution
  problem our own `S_res` sanity check (ADR-010) was built for,
  under a different source's own convention. A legitimately
  interesting thing for M9 to exercise, not just a nuisance to filter
  past.
- **Scale**: 1,974,840 rows in this resource alone.

### Open question — not yet resolved, do not treat as settled

This specific resource spans only 2022–2026 (~4 years), which is
*shorter* than ADR-009's own 72-month eligibility floor. CDC
publishes per-year weekly tables going back further (references found
to tables from 2018 onward, and MMWR archives to 1952), but these may
live as **separate yearly Socrata resources** requiring concatenation
into one continuous run, not a single resource covering the full
span. This must be verified empirically — combining resources and
confirming continuity — before this candidate can be accepted.
Repeating the discipline that corrected Candidate 2: do not accept on
partial verification.

**Status: promising, not yet decided.** Next step: verify whether
per-year resources can be combined into a genuinely continuous,
≥72-month run for at least one condition, before drafting the formal
ADR.
