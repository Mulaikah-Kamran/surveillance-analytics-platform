"""Exploratory Analysis page (Milestone 8, ADR-010).

Runs M5's analyze(). Population data is not yet wired in (open
question, flagged separately) -- population_normalized will
correctly show as unavailable via EDAResult's own "absent, not an
error" contract, not as an error.
"""

import streamlit as st

from surveillance_platform import workflow
from surveillance_platform.ui.cached_pipeline import cached_run_eda

st.title("Exploratory Analysis")

session = st.session_state.setdefault("analysis_session", workflow.create_session())

if "preparation" not in session.results or session.status == "Failed":
    st.warning("Complete **Data Preparation** first.")
    st.stop()

session = cached_run_eda(session)
st.session_state["analysis_session"] = session
eda = session.results["eda"]

st.subheader("Descriptive statistics")
d = eda.descriptive
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Count", f"{d.count:,}")
col2.metric("Mean", f"{d.mean:.1f}")
col3.metric("Median", f"{d.median:.1f}")
col4.metric("Min", f"{d.minimum:.0f}")
col5.metric("Max", f"{d.maximum:.0f}")
col6.metric("Std dev", f"{d.std:.1f}")

st.subheader("Distribution")
dist = eda.distribution
col1, col2, col3, col4 = st.columns(4)
col1.metric("25th pct", f"{dist.q25:.1f}")
col2.metric("Median", f"{dist.q50:.1f}")
col3.metric("75th pct", f"{dist.q75:.1f}")
col4.metric("Zero-value share", f"{dist.zero_value_share:.1%}")

st.subheader("Missingness")
m = eda.missingness
if m.missing_counts:
    st.dataframe(
        {
            "column": list(m.missing_counts.keys()),
            "missing count": list(m.missing_counts.values()),
            "missing fraction": [
                f"{m.missing_fractions[c]:.1%}" for c in m.missing_counts
            ],
        }
    )
else:
    st.success("No missing values in the analysis-ready dataset.")

if eda.resolution is not None:
    st.subheader("Reporting resolution")
    st.dataframe({"resolution": list(eda.resolution.counts.keys()),
                  "count": list(eda.resolution.counts.values())})

if eda.case_definition is not None:
    st.subheader("Case definitions")
    st.dataframe({"case definition": list(eda.case_definition.counts.keys()),
                  "count": list(eda.case_definition.counts.values())})

st.subheader("Country comparison")
for entry in eda.country_comparison.countries:
    with st.expander(f"{entry.country} ({entry.observation_count:,} observations)"):
        cd = entry.descriptive
        st.write(
            f"Mean: {cd.mean:.1f} | Median: {cd.median:.1f} | "
            f"Min: {cd.minimum:.0f} | Max: {cd.maximum:.0f}"
        )
        st.caption(f"{entry.first_date} to {entry.last_date}")

if eda.population_normalized is not None:
    st.subheader("Population-normalized rate (per 100,000)")
    st.dataframe(
        {
            "country": [r.country for r in eda.population_normalized.rates],
            "year": [r.year for r in eda.population_normalized.rates],
            "rate per 100k": [
                round(r.reported_cases_per_100000, 2) for r in eda.population_normalized.rates
            ],
        }
    )
else:
    st.caption("Population-normalized rates not available (no population data supplied).")

st.success("Exploratory analysis complete. Continue to **Visualization** in the sidebar.")
