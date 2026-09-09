"""Forecasting page (Milestone 8, ADR-010).

Runs M7's forecast_track() for one track at a time, selected via a
dropdown -- not the batch forecast() -- because a single progress
callback across every detected track (10 for the real four-country
dataset, only 3 eligible) would be ambiguous about which track it
belongs to (ADR-009's forecast_track() pass-through addendum). This
is also where ADR-009's deferred Confirmed/Total case-definition
selector and below-threshold-track warning finally land.

An already-computed track is served instantly from
session.results["forecast_by_track"] (built up by
run_forecast_for_track()) -- st.cache_data is not used here, since it
cannot cleanly cache a call carrying a live UI-bound progress
callback as one of its arguments.
"""

import streamlit as st

from surveillance_platform import data_loading, workflow
from surveillance_platform.forecasting import detect_tracks
from surveillance_platform.ui.cached_pipeline import cached_fetch_population_data

st.title("Forecasting")

session = st.session_state.setdefault("analysis_session", workflow.create_session())

if "preparation" not in session.results or session.status == "Failed":
    st.warning("Complete **Data Preparation** first.")
    st.stop()

prepared_data = session.results["preparation"].data
tracks = detect_tracks(prepared_data, session.role_config)

if not tracks:
    st.info("No candidate forecasting tracks were detected in this dataset.")
    st.stop()

distinct_locations = sorted(
    prepared_data[session.role_config.location].unique().tolist()
)
population_data = cached_fetch_population_data(distinct_locations)
population_by_country = data_loading.population_by_country_series(population_data)


def _track_label(t) -> str:
    case_def = t.case_definition if t.case_definition is not None else "(constant)"
    status = "eligible" if t.eligible else "below threshold"
    return f"{t.country} — {case_def} ({t.n_months} months, {status})"


selected_label = st.selectbox("Track", [_track_label(t) for t in tracks], index=0)
selected_track = tracks[[_track_label(t) for t in tracks].index(selected_label)]
track_key = (selected_track.country, selected_track.case_definition)

# --- Did-you-know facts, rotated in sync with real progress, not a timer ---
_FACTS = [
    (
        "Did you know? 'Dengue' is believed to derive from the Swahili phrase "
        "'dinga pepo', describing a sudden, cramp-like seizure."
    ),
    (
        "Only female Aedes mosquitoes bite -- they need the blood protein to "
        "develop their eggs."
    ),
    (
        "Dengue has four distinct serotypes (DENV-1 to DENV-4); infection with "
        "one doesn't protect against the others."
    ),
    (
        "Aedes aegypti, the primary dengue vector, prefers to bite during the "
        "day, especially early morning and before dusk."
    ),
    (
        "Unlike malaria mosquitoes, Aedes aegypti can breed in tiny amounts of "
        "standing water -- even a bottle cap."
    ),
    (
        "SARIMA models capture seasonality by comparing each month not just to "
        "its neighbors, but to the same month one full cycle (a year) earlier."
    ),
]

if track_key not in session.results.get("forecast_by_track", {}):
    progress_placeholder = st.empty()
    with progress_placeholder.container(border=True):
        phase_text = st.empty()
        progress_bar = st.progress(0.0)
        detail_text = st.empty()
        fact_text = st.empty()

        state = {"fact_idx": 0, "candidate_count": 0}
        order_share = 1.0 if not selected_track.eligible else 0.5

        def _advance_fact():
            state["fact_idx"] = (state["fact_idx"] + 1) % len(_FACTS)
            fact_text.caption(_FACTS[state["fact_idx"]])

        def on_candidate(order, seasonal_order, aic, converged):
            state["candidate_count"] += 1
            progress_bar.progress(min(state["candidate_count"] / 36, 1.0) * order_share)
            phase_text.markdown("**Comparing SARIMA orders by AIC...**")
            aic_str = f"{aic:.1f}" if aic is not None else "n/a"
            detail_text.code(
                f"SARIMA{order}{seasonal_order} -> AIC: {aic_str} "
                f"({'converged' if converged else 'not converged'})"
            )
            if state["candidate_count"] % 8 == 0:
                _advance_fact()

        def on_origin(completed, total):
            fraction = completed / total if total else 1.0
            progress_bar.progress(0.5 + fraction * 0.5)
            phase_text.markdown("**Running rolling-origin backtest...**")
            detail_text.code(f"Origin {completed} / {total}")
            if completed % 8 == 0:
                _advance_fact()

        _advance_fact()
        session = workflow.run_forecast_for_track(
            session,
            selected_track,
            population_by_country.get(selected_track.country),
            on_candidate=on_candidate,
            on_origin=on_origin,
        )
    # Clear the entire progress panel now that computation is done --
    # otherwise it lingers above the final results instead of being
    # replaced by them (caught via a real screenshot walkthrough, not
    # assumed).
    progress_placeholder.empty()
    st.session_state["analysis_session"] = session

result = session.results["forecast_by_track"][track_key]

if result.limitations:
    for message in result.limitations:
        st.warning(message)

if result.forecast_mean:
    st.subheader(f"3-month forecast (rate per 100,000) -- {selected_label}")
    st.line_chart(
        {
            "forecast": dict(
                zip([str(p) for p in result.forecast_periods], result.forecast_mean)
            ),
        }
    )

    if result.model_metrics is not None and result.baseline_metrics is not None:
        st.subheader("Backtest evaluation: SARIMA vs. seasonal-naive baseline")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**SARIMA (primary model)**")
            st.metric("MAE", f"{result.model_metrics.mae:.2f}")
            st.metric("RMSE", f"{result.model_metrics.rmse:.2f}")
            if result.model_metrics.mase is not None:
                st.metric("MASE", f"{result.model_metrics.mase:.2f}")
        with col2:
            st.markdown("**Seasonal-naive (baseline)**")
            st.metric("MAE", f"{result.baseline_metrics.mae:.2f}")
            st.metric("RMSE", f"{result.baseline_metrics.rmse:.2f}")

    if result.residual_diagnostics is not None:
        st.caption(
            f"Ljung-Box (lag {result.residual_diagnostics.lag}): "
            f"statistic={result.residual_diagnostics.ljung_box_stat:.2f}, "
            f"p-value={result.residual_diagnostics.ljung_box_pvalue:.3f}"
        )

    st.success("Forecasting complete. Continue to **Results & Export** in the sidebar.")
else:
    st.info("No forecast could be produced for this track (see limitations above).")
