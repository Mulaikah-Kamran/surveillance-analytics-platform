# Decision Log — Milestone 9 Validation Dataset Evaluation

**Date started:** 2026-09-09
**Status:** In progress — candidates are evaluated and recorded here as
they're assessed; the final selection will be locked as its own ADR
once a candidate passes evaluation (per the ADR Creation Rule: this is
a decision with multiple reasonable alternatives, hard to reverse once
Milestone 9 implementation begins against it).
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

## Candidate 2: HDX-hosted datasets — evaluation in progress

(To be completed next.)
