"""Exploratory Analysis page (Milestone 8, ADR-010).

Runs M5's analyze(), with population data from the World Bank
registry lookup (ADR-010 addendum) -- matched deterministically
against whichever Location values are actually present in the
dataset. A location that doesn't match is simply absent from the
result; population_normalized then shows as unavailable via
EDAResult's own "absent, not an error" contract for exactly those
countries, not as an error for the whole page.

Visual polish (2026-09-10): grouped into bordered cards for structure
rather than a flat wall of tables; a wide statistic (e.g. a large
Max value) is now formatted compactly instead of truncating in its
metric box; the missingness table only lists columns that actually
have missing values, since an all-zero table added noise without
adding information; and any real per-country-year reporting
inconsistency (resolution or case-definition heterogeneity) is
surfaced as a visible callout instead of being invisible on this page
entirely (it previously only showed up as a marker on the
Visualization page's chart).
"""

import streamlit as st

from surveillance_platform import workflow
from surveillance_platform.ui.cached_pipeline import (
    cached_fetch_population_data,
    cached_run_eda,
)

st.title("Exploratory Analysis")

session = st.session_state.setdefault("analysis_session", workflow.create_session())

if "preparation" not in session.results or session.status == "Failed":
    st.warning("Complete **Data Preparation** first.")
    st.stop()

prepared_data = session.results["preparation"].data
distinct_locations = sorted(
    prepared_data[session.role_config.location].unique().tolist()
)
population_data = cached_fetch_population_data(distinct_locations)

session = cached_run_eda(session, population_data)
st.session_state["analysis_session"] = session
eda = session.results["eda"]


def _fmt(value: float) -> str:
    """Compact formatting so a wide number never truncates in a metric box."""
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs(value) >= 10_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.1f}" if value != int(value) else f"{value:,.0f}"


# --- The one finding worth seeing first, if it exists ----------------------

heterogeneous_years = [
    cy
    for cy in eda.time_series.country_years
    if cy.resolution_homogeneous is False or cy.case_definition_homogeneous is False
]
if heterogeneous_years:
    with st.container(border=True):
        st.markdown("**Worth knowing before you trust a trend line**")
        st.caption(
            f"{len(heterogeneous_years)} country-year(s) had a reporting "
            "inconsistency, which can distort a trend if read at face value."
        )
        preview_count = 3
        for cy in heterogeneous_years[:preview_count]:
            reasons = []
            if cy.resolution_homogeneous is False:
                reasons.append("reporting resolution changed mid-year")
            if cy.case_definition_homogeneous is False:
                reasons.append("case definition changed mid-year")
            st.caption(f"**{cy.country}, {cy.year}**: {' and '.join(reasons)}.")
        if len(heterogeneous_years) > preview_count:
            with st.expander(f"Show all {len(heterogeneous_years)}"):
                for cy in heterogeneous_years[preview_count:]:
                    reasons = []
                    if cy.resolution_homogeneous is False:
                        reasons.append("reporting resolution changed mid-year")
                    if cy.case_definition_homogeneous is False:
                        reasons.append("case definition changed mid-year")
                    st.caption(f"**{cy.country}, {cy.year}**: {' and '.join(reasons)}.")

# --- Summary card ------------------------------------------------------------

with st.container(border=True):
    st.subheader("Summary")
    d, dist = eda.descriptive, eda.distribution
    col1, col2, col3 = st.columns(3)
    col1.metric("Observations", f"{d.count:,}")
    col1.metric("Zero-value share", f"{dist.zero_value_share:.1%}")
    col2.metric("Mean", _fmt(d.mean))
    col2.metric("Median", _fmt(d.median))
    col3.metric("Min", _fmt(d.minimum))
    col3.metric("Max", _fmt(d.maximum))
    st.caption(
        f"25th percentile {dist.q25:,.1f} · 75th percentile {dist.q75:,.1f} · "
        f"std dev {d.std:,.1f}"
    )

# --- Data quality card ---------------------------------------------------

with st.container(border=True):
    st.subheader("Data quality")
    m = eda.missingness
    incomplete_columns = {c: v for c, v in m.missing_counts.items() if v > 0}
    if incomplete_columns:
        st.dataframe(
            {
                "column": list(incomplete_columns.keys()),
                "missing count": list(incomplete_columns.values()),
                "missing fraction": [
                    f"{m.missing_fractions[c]:.1%}" for c in incomplete_columns
                ],
            },
            hide_index=True,
        )
    else:
        st.success("No missing values in the analysis-ready dataset.")

    if eda.resolution is not None or eda.case_definition is not None:
        col_a, col_b = st.columns(2)
        if eda.resolution is not None:
            with col_a:
                st.caption("Reporting resolution")
                st.dataframe(
                    {
                        "resolution": list(eda.resolution.counts.keys()),
                        "count": list(eda.resolution.counts.values()),
                    },
                    hide_index=True,
                )
        if eda.case_definition is not None:
            with col_b:
                st.caption("Case definitions")
                st.dataframe(
                    {
                        "case definition": list(eda.case_definition.counts.keys()),
                        "count": list(eda.case_definition.counts.values()),
                    },
                    hide_index=True,
                )

# --- By country card ----------------------------------------------------

with st.container(border=True):
    st.subheader("By country")
    for entry in eda.country_comparison.countries:
        with st.expander(f"{entry.country} ({entry.observation_count:,} observations)"):
            cd = entry.descriptive
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Mean", _fmt(cd.mean))
            col2.metric("Median", _fmt(cd.median))
            col3.metric("Min", _fmt(cd.minimum))
            col4.metric("Max", _fmt(cd.maximum))
            st.caption(f"{entry.first_date} to {entry.last_date}")

    if eda.population_normalized is not None and eda.population_normalized.rates:
        st.markdown("**Population-normalized rate (per 100,000)**")
        st.dataframe(
            {
                "country": [r.country for r in eda.population_normalized.rates],
                "year": [r.year for r in eda.population_normalized.rates],
                "rate per 100k": [
                    round(r.reported_cases_per_100000, 2)
                    for r in eda.population_normalized.rates
                ],
            },
            hide_index=True,
        )
    else:
        st.caption(
            "Population-normalized rates not available (none of this dataset's "
            "locations matched the World Bank country registry)."
        )

st.success(
    "Exploratory analysis complete. Continue to **Visualization** in the sidebar."
)
