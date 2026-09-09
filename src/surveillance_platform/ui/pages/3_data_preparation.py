"""Data Preparation page (Milestone 8, ADR-010).

Runs M4's prepare(). On DataPreparationError, shows only the
diagnostic messages (PFD Section 14's exact failure behavior) -- no
downstream page becomes reachable.
"""

import streamlit as st

from surveillance_platform import workflow
from surveillance_platform.ui.cached_pipeline import cached_run_preparation

st.title("Data Preparation")

session = st.session_state.setdefault("analysis_session", workflow.create_session())

if session.dataset is None:
    st.warning("Load a dataset first, on the **Load Dataset** page.")
    st.stop()
if session.role_config is None:
    st.warning("Configure roles first, on the **Configure Roles** page.")
    st.stop()

session = cached_run_preparation(session)
st.session_state["analysis_session"] = session

if session.status == "Failed":
    st.error("Data preparation failed structural validation:")
    for message in session.error_messages:
        st.markdown(f"- {message}")
    st.stop()

report = session.results["preparation"].report

col1, col2, col3 = st.columns(3)
col1.metric("Rows in", f"{report.rows_in:,}")
col2.metric("Rows out", f"{report.rows_out:,}")
col3.metric("Rows excluded", f"{report.rows_excluded:,}")

if report.exclusion_reasons:
    st.subheader("Exclusion reasons")
    st.dataframe(
        {"reason": list(report.exclusion_reasons.keys()),
         "count": list(report.exclusion_reasons.values())}
    )

st.subheader("Quality findings")
warning_count = sum(1 for f in report.quality_findings if f.severity == "warning")
if report.quality_findings:
    if warning_count:
        st.warning(f"{warning_count} warning-level finding(s) below.")
    st.dataframe(
        {
            "check": [f.check for f in report.quality_findings],
            "severity": [f.severity for f in report.quality_findings],
            "message": [f.message for f in report.quality_findings],
        }
    )
else:
    st.success("No quality issues found.")

st.subheader("Cleaning actions")
if report.cleaning_actions:
    for action in report.cleaning_actions:
        st.markdown(f"- {action}")
else:
    st.info("No cleaning actions were needed.")

if report.warnings:
    st.subheader("Warnings")
    for warning in report.warnings:
        st.warning(warning)

st.success("Data preparation complete. Continue to **Exploratory Analysis** in the sidebar.")
