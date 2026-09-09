"""Visualization page (Milestone 8, ADR-010).

Runs M6's visualize(). Each chart in its own bounded container (the
"chart-as-card" pattern from ADR-010's visual identity design) --
M6's plotly_white charts are left exactly as approved, not modified
for dark mode.
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
    st.plotly_chart(viz.annual_trend, use_container_width=True)

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
