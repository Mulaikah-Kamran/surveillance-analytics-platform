# ADR-010 — UI Integration Strategy

**Status:** Locked (Milestone 8)

## Decision

Milestone 8 implements the presentation layer as **three genuinely
independent modules** -- `data_loading`, `workflow`, and `ui` --
where the first two contain zero Streamlit imports and remain fully
runnable and testable as plain Python, and `ui` is a thin, cached
wrapper around them. The app is branded **Epicurve** ("Inspect the
records. Evaluate the trend. Benchmark the model."), with the PFD's
formal title retained as the authoritative name in all documentation.

### Architecture & independence

- `workflow/` owns a plain `AnalysisSession` dataclass (`dataset`,
  `role_config`, `analysis_config`, `status:
  Created|Configured|Running|Completed|Failed`, `results`) and
  controller functions that call `prepare()`, `analyze()`,
  `visualize()`, `forecast()` directly. **Zero Streamlit imports
  anywhere in `workflow/` or `data_loading/`** -- deleting `ui/` must
  leave the pipeline fully runnable from a script, matching ADR-006
  and Section 20's "backend tested independently of the UI"
  requirement, extended explicitly to the controller and session
  layer, not just the analytical stages.
- `data_loading/` formalizes what M2's ad hoc scripts did: load a CSV
  into a DataFrame, plus the `S_res`-based sanity check (Admin0 vs.
  sub-national), as a real, tested module -- not reused from
  `data/download_national_extract.py` directly, though that script's
  checksum-verification logic is reused for the sample-dataset
  feature.
- `ui/` holds `st.cache_data`-decorated wrapper functions and the
  Streamlit pages themselves. This is the only layer permitted to
  import `streamlit`.
- The Workflow Controller catches `DataPreparationError` (confirmed:
  raised by `validate_dataset()` inside `prepare()`) and sets
  `status="Failed"`, storing the exception's violation messages --
  implementing PFD Section 14's exact failure behavior (halt
  downstream execution, preserve diagnostics, return control to the
  presentation layer).

### Dataset input

- **Single ingestion path**: `st.file_uploader` (CSV) -- used for
  both the four ADR-008 study countries and, later, Milestone 9's
  validation dataset. No separate auto-load path.
- **"Download sample dataset" button**: triggers the existing
  checksum-verified `download_national_extract.py` logic
  server-side, serves the result via `st.download_button`. Produces
  the *real* National Extract, so a reviewer's results match
  ADR-009's documented findings exactly, while still requiring the
  same explicit upload step as any other file.
- **Sanity check**: if an `S_res` column is present
  (OpenDengue-specific, opportunistic -- absent for other datasets is
  not an error), warn -- don't block -- if any value other than
  `"Admin0"` appears, since ADR-002 documented the Temporal Extract as
  ~93% Admin2-level and untested against this pipeline.

### Role configuration

Data preview (columns + dtypes) -> three required dropdowns (Time,
Location, Surveillance Measure) + one optional (Identifier, with a
"(none)" choice) -> immediate `validate()` call, displaying
`RoleConfigurationError`'s violations directly. Optional column
highlighting (ADR-004-permitted convenience) is built: a cheap
heuristic (name/dtype pattern matching) suggests, never pre-selects or
auto-assigns.

### App structure

Multi-page via `st.navigation`, **file-based pages** (required for
`AppTest.switch_page()`, verified empirically), each gated by
`AnalysisSession.status`:

1. **Load Dataset** -- upload / sample-download, preview, sanity check
2. **Configure Roles** -- dropdowns, highlighting, validation
3. **Data Preparation** -- `prepare()` -> `PreparationReport` (rows
   in/out/excluded as metrics, exclusion reasons, quality findings
   table with amber accent for warnings, cleaning actions, an
   explicit "no issues found" state when empty) or, on
   `DataPreparationError`, only the violation messages
4. **Exploratory Analysis** -- `analyze()` -> `EDAResult`, section by
   section, respecting its "absent, not an error" contract
   (`resolution`/`case_definition`/`population_normalized` shown only
   when not `None`)
5. **Visualization** -- `visualize()`'s five `VisualizationResult`
   figures via `st.plotly_chart`, each in a bounded container (charts
   stay `plotly_white` -- a deliberate "light card" pattern, not a
   dark-mode gap; M6 is not modified)
6. **Forecasting** -- `forecast()`; a track selector for countries
   with more than one candidate (Bangladesh Confirmed/Total -- the
   selector ADR-009 explicitly deferred here); a persistent amber
   warning banner using `ForecastResult.limitations` verbatim for
   below-threshold tracks; forecast chart, `model_metrics` vs.
   `baseline_metrics` side by side, residual diagnostics when
   available
7. **Results / Export** -- self-contained HTML report (Plotly's
   native `.to_html()` + f-string-templated tables, no new
   dependency), via `st.download_button`

### Caching & performance

`st.cache_data` wraps `workflow` calls at the `ui/` boundary --
verified empirically against our actual (unhashable-by-`__hash__`)
`RoleConfiguration` and a real `ForecastResult` (pickle-caches
correctly, ~1,238x speedup on repeat calls, correct cache-miss on
genuinely different inputs). For the two genuinely slow steps (SARIMA
order selection, ~3-4s; rolling-origin backtest, tens of seconds), a
bordered progress panel shows **real** completion (not a fake
spinner): a progress bar tracking actual candidate/origin count, a
live monospace line of the current SARIMA order and its AIC as it's
tested, and a "did you know?" dengue/epidemiology fact that advances
in sync with progress (paced by real computation, not a separate
timer) -- one deliberate cross-fade transition, the app's single
non-user-triggered motion moment.

### Configurability

Every analytical/methodological parameter ADR-009 already locked
(horizon, training window, order grid, eligibility floor, gap
tolerance, metrics) stays fixed -- not exposed as UI controls.
User-facing choices are limited to selection and navigation: dataset,
role mapping, which track/case-definition to view.

### Visual identity

- **Palette**: primary deep teal `#1B4B4F`; functional-only amber
  accent `#B7791F` (warnings/status, never decoration); light
  background `#FAFAF8`; dark background `#14181C` -- each chosen
  specifically to avoid the AI-generated-design tells (no
  cream+terracotta, no near-black+neon accent, no SaaS-purple
  gradients).
- **Typography**: IBM Plex Sans throughout, loaded via
  `config.toml`'s native Google Fonts support (`font = "IBM Plex
  Sans:https://fonts.googleapis.com/css2?..."`) -- confirmed to
  require zero custom CSS injection, which is itself part of the
  professionalism goal (hand-rolled CSS overrides are a common source
  of the "hacky" look this ADR is explicitly trying to avoid).
- **Light/Dark/System toggle**: Streamlit's native Settings-menu
  toggle (present since a 2021 feature release, confirmed available
  in our pinned `1.63.0`) -- zero custom code required.
- **Layout**: left-aligned, sidebar navigation mirroring the locked
  pipeline order, single column per stage; no decorative numbered
  badges, ALL-CAPS labels, or arrow-suffixed buttons.

### Security

Not part of the original decision list -- added explicitly here,
before implementation, per project convention that additions are
documented, not silently introduced.

- **HTML export XSS mitigation**: every user-derived string value
  (uploaded CSV's country names, column values, etc.) is passed
  through Python's stdlib `html.escape()` before being interpolated
  into the f-string-templated HTML report (Decision H). Real risk,
  not theoretical: an unescaped malicious cell (e.g. containing a
  `<script>` tag) would execute in whoever's browser later opens the
  exported file.
- **No `unsafe_allow_html=True` anywhere in the live app.** Standard
  Streamlit widgets (`st.write`, `st.dataframe`, `st.table`)
  auto-escape; the app never reaches for the unsafe flag when
  displaying anything derived from an uploaded file.
- **Uploaded files are processed in-memory only.** `pandas.read_csv()`
  reads directly from Streamlit's in-memory `UploadedFile` object;
  nothing is written to disk with a user-influenced filename, which
  avoids path-traversal risk entirely rather than requiring filename
  sanitization.
- **Explicit upload constraints**: `st.file_uploader(type=["csv"])`,
  max size ~50MB (generous relative to the real ~4.2MB National
  Extract, small enough to bound memory use from a bad-faith upload).
- **Sample-dataset download is deduplicated**: the existing
  checksum-verified local file is reused if already present, rather
  than re-fetching from OpenDengue's GitHub on every button click --
  confirmed the existing `download_national_extract.py` script has no
  such check, so this is new logic, not a reused guarantee.
- **Stated, not silently accepted, limitation**: this remains a
  research/portfolio tool, not a hardened multi-tenant service --
  there is no user authentication and no rate-limiting on the
  genuinely expensive computation (SARIMA fitting/backtesting).
  Documented explicitly in `docs/ui.md` as a stated scope boundary,
  consistent with Section 8's exclusion of production deployment.
- Verified separately: no existing code anywhere in `src/` uses
  `.eval()` or `.query()` on user-controlled input.

### Dependencies & testing

- `streamlit==1.63.0` -- verified compatible with pinned
  `pandas==3.0.5`/Python 3.12 (clean import, no conflicts).
- Testing via `streamlit.testing.v1.AppTest`, confirmed working
  end-to-end against a real file-based multi-page smoke test
  (`switch_page()` verified functional). Tests verify UI<->backend
  wiring per Section 20 -- not re-testing analytical correctness,
  which M4-M7's own suites already own.

## Context

ADR-006 locked *that* Streamlit is the presentation layer with zero
analytical logic; it left the Workflow Controller, Analysis Session,
dataset-ingestion mechanism, and every UI-specific detail unspecified
-- resolved here using the same evidence-based process as ADR-009,
including several points verified empirically before being locked
(RoleConfiguration hashability, ForecastResult cacheability,
AppTest's file-based-page requirement, native theming's Google Fonts
support).

## Rationale

Each major choice was checked against either the actual frozen
documents or real behavior, not assumed: the `S_res`-based sanity
check was designed from the real column values in our actual data
(National Extract is 100% `"Admin0"`); the single-ingestion-path
design (upload, with sample-download feeding the *same* uploader) was
chosen specifically to avoid a second, untested code path into the
pipeline; the page-to-object mapping follows the granularity
M4/M5/M6/M7 already established (`PreparationResult`, `EDAResult`,
`VisualizationResult`, `ForecastResult`) rather than inventing a finer
split; and the decision to keep M6 untouched (treating `plotly_white`
charts as an intentional light-card pattern in dark mode) avoids
reopening a frozen, Antigravity-approved milestone for a cosmetic
concern.

## Consequences

- `data_loading/` and `workflow/`'s M1-era placeholders are replaced
  with real modules and their own test suites, mirroring the M7
  pattern of replacing `forecasting/__init__.py`.
- Milestone 9's validation dataset flows through the identical upload
  path with no code changes needed for it specifically.
- A future contributor can run the entire analytical pipeline via
  `workflow.run_analysis(...)` from a plain script with `streamlit`
  uninstalled.
- Per ADR Discipline, any change to this strategy is made as an
  explicit new ADR revision.
