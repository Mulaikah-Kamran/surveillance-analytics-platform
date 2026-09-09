# UI Integration

**Milestone:** 8 — UI Integration
**Modules:** `src/surveillance_platform/data_loading/`,
`src/surveillance_platform/workflow/`, `src/surveillance_platform/ui/`,
`app.py`
**Design reference:** `docs/adr/ADR-010-ui-integration-strategy.md`
(full rationale, evidence, and every point verified empirically before
being locked); `docs/adr/ADR-006-user-interface-strategy.md` (the
original locked scope this ADR resolves).

## Purpose

Epicurve is the Streamlit presentation layer over Milestones 1–7's
backend: upload a surveillance dataset, configure roles, run it
through validation/cleaning/EDA/visualization/forecasting, and export
a report — all without touching any analytical logic directly.

## Architecture: three independent layers

- **`data_loading/`** and **`workflow/`** contain **zero Streamlit
  imports** and are fully runnable/testable as plain Python (verified
  throughout development: every unit test for these two modules is
  plain `pytest`, no `AppTest` needed). Deleting `ui/` entirely would
  leave `workflow.run_preparation(...)` etc. fully functional from a
  script.
- **`ui/`** (plus the root `app.py`) is the only layer permitted to
  import `streamlit`. It holds the seven page files, the
  `st.cache_data` wrapping (`cached_pipeline.py`), the optional
  column-highlighting heuristic (`highlighting.py`, also
  Streamlit-free), and the HTML report builder (`report_builder.py`,
  also Streamlit-free).

This split matters for a concrete reason, not just architectural
tidiness: ADR-006 already required backend logic to stay separate
from the UI; ADR-010 extends that requirement explicitly to the
Workflow Controller and Analysis Session, which hadn't existed yet
when ADR-006 was written.

## The Analysis Session

`workflow.AnalysisSession` implements the lifecycle from PFD Section
19 (`Created → Configured → Running → Completed`, with `Failed`
reachable from `configure_roles`/`run_preparation`). Every controller
function takes a session and returns a **new** one via
`dataclasses.replace()` — never mutates its input, the same
convention M4–M7 already established. `status` only ever becomes
`"Failed"` via a caught `DataPreparationError` or
`RoleConfigurationError`: EDA, Visualization, and Forecasting are all
designed to degrade gracefully (a `ForecastResult` never raises on an
ordinary data limitation) rather than hard-stop.

## The seven pages

Each page maps directly to an existing backend result object, not an
invented finer granularity:

1. **Load Dataset** — single ingestion path (`st.file_uploader`, CSV
   only, 50MB limit enforced at both the widget and `load_csv()`
   levels) plus a "Download sample dataset" button that fetches the
   real, checksum-verified National Extract and feeds it through the
   *same* uploader — not a separate load path. An `S_res`-based
   sanity check warns, never blocks, on data that looks sub-national.
2. **Configure Roles** — the three required dropdowns plus optional
   Identifier, immediate `validate()` feedback, and ADR-004's optional
   column-highlighting convenience (verified: suggestions are shown as
   caption hints, never pre-selected as a dropdown's default value).
3. **Data Preparation** — `PreparationReport` in full: metrics,
   exclusion reasons, quality findings, cleaning actions. On
   `DataPreparationError`, shows *only* the violation messages — no
   downstream content renders, per PFD Section 14's exact failure
   behavior.
4. **Exploratory Analysis** — `EDAResult` section by section,
   respecting its "absent, not an error" contract throughout.
5. **Visualization** — M6's five figures, each in a bounded container
   (a deliberate "light card" pattern; M6's `plotly_white` charts are
   not modified for dark mode).
6. **Forecasting** — see below; this is where ADR-009's deferred
   Confirmed/Total selector and below-threshold warning finally land.
7. **Results & Export** — see below.

## Forecasting: per-track, not batch

Page 6 calls `detect_tracks()` directly for its track selector, then
`workflow.run_forecast_for_track()` for **only the selected track** —
not the batch `forecast()`/`run_forecasting()`. This was a real
architectural finding during development: `forecast()` processes every
detected track in one call (10 for the real four-country dataset, only
3 eligible), and a single progress callback across that batch would be
ambiguous about which track it belongs to. `forecast_track()` itself
needed a small, purely-additive ADR-009 revision (`on_candidate`/
`on_origin` callbacks, default `None`, verified byte-identical
behavior with and without them) to make this possible at all.

An already-computed track is served instantly from
`session.results["forecast_by_track"]` — **not** `st.cache_data`,
which cannot cleanly cache a call carrying a live UI-bound progress
callback as one of its arguments. The session's own accumulated
results dict, which already persists in `st.session_state`, serves as
the memoization layer instead.

### Live progress panel

A real progress bar (not simulated) driven by the actual callbacks:
`on_candidate` reports each of the 36 AIC-grid points as it's tested
(order, seasonal order, AIC, converged), `on_origin` reports each
backtest origin. Progress-bar share is allocated 50/50 between order
selection and backtesting for eligible tracks, or 100% to order
selection for below-threshold tracks (which never reach the backtest
phase at all). A dengue/epidemiology fact rotates every 8 progress
events — paced by real computation, not a separate timer.

## Population data sourcing

Not part of the original ADR-010 design — surfaced during Page 4
development, since Decision C covered only the surveillance dataset's
own ingestion, not where population data comes from.
`data_loading/population_lookup.py` matches a dataset's actual
Location values against the World Bank's own country registry,
deterministically and exactly (case-insensitive), never fuzzy, never
hardcoded to the four ADR-008 countries. What generalizes is the
*mechanism*: for any dataset whose Location values happen to match the
registry, population data is obtained; an unmatched location is simply
omitted, falling through to Forecasting's existing per-country
"unavailable" limitation. Cached at two layers — the registry itself
on disk (`data_loading`, rarely changes), the per-dataset fetch via
`st.cache_data` (`ui/cached_pipeline.py`).

## Results & Export

`report_builder.py` assembles a complete, self-contained HTML report
— real CSS applying the project's locked palette (deep teal, IBM Plex
Sans) and card-style sections, embedded interactive Plotly charts via
`.to_html()` (already a dependency since M6, no new one added), and a
forecast chart rebuilt specifically for export (Page 6's on-screen
chart uses Streamlit's native `line_chart`, which cannot be embedded
in a standalone file). Only includes sections for stages the session
has actually completed.

## Security

Not part of the original decision list — added explicitly to ADR-010
before implementation began, per the project's convention that
additions are documented, not silently introduced:

- Every user-derived string (country names, quality-finding messages)
  is passed through `html.escape()` before entering the HTML report —
  verified directly with a malicious `<script>`-containing country
  name, confirmed it never appears unescaped in the output.
- No `unsafe_allow_html=True` anywhere in the live app.
- Uploaded files are processed in-memory only; nothing is written to
  disk with a user-influenced filename.
- The "Download sample dataset" fetch is deduplicated (existence-check
  against the local cache) so repeated clicks don't hammer OpenDengue's
  GitHub.
- Stated, not silently accepted, limitation: no authentication, no
  rate-limiting on the genuinely expensive computation — this remains
  a research/portfolio tool, not a hardened multi-tenant service,
  consistent with Section 8's exclusion of production deployment.

## Testing

`streamlit.testing.v1.AppTest`, with every page as its own file
(required for `AppTest.switch_page()` to work — verified early in
development). Tests simulate real interactions (file uploads via
`FileUploader.upload()`, dropdown selections via `Selectbox.select()`),
not just "does it load without exception." `data_loading`/`workflow`/
`report_builder.py` are tested as plain Python, no `AppTest` needed.

## CI compliance

`ruff` and `black --check` (run in CI per Section 27) were not
verified locally throughout most of M7/M8's development — only
`pytest` was — leading to a real, silent CI failure on `main` that
was only caught via a GitHub notification. Fixed with zero behavioral
change (confirmed via an identical passing-test-count before and
after every fix). Two categories of finding were suppressed with
explained `noqa` comments rather than restructured: deliberate broad
`except Exception` blocks (SARIMAX can raise many distinct exception
types; any of them means "skip this candidate," not a bug to narrow)
and confirmed-false-positive closure warnings in `eligibility.py`
(traced through carefully; the closures are redefined fresh each loop
iteration and called only within that same iteration, and one
variable's late-binding is specifically required, not accidental).
