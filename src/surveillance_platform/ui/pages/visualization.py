"""Visualization page (Milestone 8, ADR-010).

Runs M6's visualize(). Each chart in its own bounded container (the
"chart-as-card" pattern from ADR-010's visual identity design) --
M6's plotly_white charts are left exactly as approved, not modified
for dark mode.

Mobile fix (2026-09-10): annual_trend uses an unbounded per-country
subplot grid (trend.py's _MAX_COLUMNS=2, but the row count grows with
however many countries are in the dataset). st.plotly_chart's own
width parameter cannot help here -- confirmed directly against
Streamlit's own documented behavior: a chart's width is always capped
to its parent container's width, with no way to let it overflow, so
on a phone every panel gets compressed to illegible size regardless of
how the width is requested. Rendered instead via
st.components.v1.html() with the chart's own to_html() output inside
a scrollable div: desktop is unaffected (900px fits the ~960px content
column with no scrolling needed, confirmed visually), while a
narrower viewport shows each country panel at a legible size with
horizontal scroll for the rest, rather than squeezing everything to
fit. Every other chart on this page stays on the native
st.plotly_chart widget -- surveillance_profile's grid is capped at 2
panels (resolution + case definition), too small to have this problem.
"""

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
    annual_trend_fig = viz.annual_trend
    annual_trend_fig.update_layout(width=900)
    scrollable_chart_html = (
        '<div style="overflow-x:auto; -webkit-overflow-scrolling:touch;">'
        + annual_trend_fig.to_html(include_plotlyjs=True, full_html=False)
        + "</div>"
    )
    st.components.v1.html(
        scrollable_chart_html,
        height=int(annual_trend_fig.layout.height) + 30,
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
