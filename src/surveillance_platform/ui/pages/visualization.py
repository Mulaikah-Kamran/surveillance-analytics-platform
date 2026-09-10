"""Visualization page (Milestone 8, ADR-010).

Runs M6's visualize(). Each chart in its own bounded container (the
"chart-as-card" pattern from ADR-010's visual identity design) --
M6's plotly_white charts are left exactly as approved, not modified
for dark mode.

Annual trend redesign (2026-09-10): the previous fix (a fixed-width
chart in a scrollable box) technically stopped the overflow bug, but
cramming many small per-country subplots into one scrollable box was
never a good way to look at this data, regardless of how well the
scroll mechanics worked. Replaced with a country selector -- the same
pattern already used successfully on the Forecasting page -- showing
one country at a time as a proper, full-sized native st.plotly_chart.
Each single-country figure is built by extracting that country's own
trace (name, x/y data, marker styling, hover text) directly from
M6's already-computed annual_trend figure, not by calling M6 again or
modifying its output -- a UI-layer presentation choice, not a change
to the frozen analytical figure. An expander still offers the full
small-multiples overview for anyone who wants to compare every
country at a glance.
"""

import plotly.graph_objects as go
import streamlit as st

from surveillance_platform import workflow
from surveillance_platform.ui.cached_pipeline import cached_run_visualization

st.title("Visualization")

session = st.session_state.setdefault("analysis_session", workflow.create_session())

if "eda" not in session.results or session.status == "Failed":
    st.warning("Complete **Exploratory Analysis** first.")
    st.stop()

session = cached_run_visualization(session)
st.session_state["analysis_session"] = session
viz = session.results["visualization"]

with st.container(border=True):
    st.subheader("Annual surveillance trend")
    trend_fig = viz.annual_trend
    country_names = [trace.name for trace in trend_fig.data]
    selected_country = st.selectbox("Country", country_names, key="viz_trend_country")
    selected_trace = next(t for t in trend_fig.data if t.name == selected_country)

    single_fig = go.Figure(
        data=[
            go.Scatter(
                x=selected_trace.x,
                y=selected_trace.y,
                mode="lines+markers",
                line=selected_trace.line,
                marker=selected_trace.marker,
                hovertext=selected_trace.hovertext,
                hoverinfo="text",
                showlegend=False,
            )
        ]
    )
    single_fig.update_layout(
        template="plotly_white",
        title=f"{selected_country}: Annual Reported-Case Total",
        xaxis_title="Year",
        yaxis_title="Reported-case total",
        height=420,
    )
    single_fig.update_xaxes(tickformat="d", nticks=8, tickangle=-45)
    st.plotly_chart(single_fig, use_container_width=True)
    st.caption("⬦ = inconsistent reporting that year (hover for details).")

    with st.expander("See all countries at once"):
        trend_fig.update_layout(width=780)
        viewport_height = min(int(trend_fig.layout.height), 600)
        scrollable_chart_html = (
            f'<div style="overflow:auto; -webkit-overflow-scrolling:touch; '
            f'height:{viewport_height}px;">'
            + trend_fig.to_html(include_plotlyjs=True, full_html=False)
            + "</div>"
        )
        st.components.v1.html(
            scrollable_chart_html,
            height=viewport_height + 20,
            scrolling=False,
        )

with st.container(border=True):
    st.subheader("Annual distribution by country")
    st.plotly_chart(viz.annual_distribution_by_country, use_container_width=True)

with st.container(border=True):
    st.subheader("Surveillance measure distribution")
    st.plotly_chart(viz.surveillance_measure_distribution, use_container_width=True)

if viz.population_normalized_distribution is not None:
    with st.container(border=True):
        st.subheader("Population-normalized distribution")
        st.plotly_chart(
            viz.population_normalized_distribution, use_container_width=True
        )
else:
    st.caption(
        "Population-normalized distribution not available (no matching population data)."
    )

if viz.surveillance_profile is not None:
    with st.container(border=True):
        st.subheader("Surveillance resolution profile")
        st.plotly_chart(viz.surveillance_profile, use_container_width=True)
else:
    st.caption(
        "Surveillance resolution profile not available (T_res/case_definition_standardised absent)."
    )

st.success("Visualization complete. Continue to **Forecasting** in the sidebar.")
