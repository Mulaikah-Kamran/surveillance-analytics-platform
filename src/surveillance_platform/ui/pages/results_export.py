"""Results & Export page (Milestone 8, ADR-010).

Assembles a self-contained HTML report (Plotly's native to_html(), no
new dependency) from whichever stages the session has actually
completed. Served via st.download_button -- report_builder.py itself
is Streamlit-free and independently testable.
"""

import streamlit as st

from surveillance_platform import workflow
from surveillance_platform.ui.report_builder import build_report_html

st.title("Results & Export")

session = st.session_state.setdefault("analysis_session", workflow.create_session())

if "preparation" not in session.results or session.status == "Failed":
    st.warning("Complete **Data Preparation** first.")
    st.stop()

st.markdown(
    "Download a complete, self-contained HTML report covering every "
    "stage completed so far (data preparation, exploratory analysis, "
    "visualization, and any forecasts you've viewed). Open it in any "
    "browser -- no need to run this app."
)

report_html = build_report_html(session)
st.download_button(
    "Download report (HTML)",
    data=report_html,
    file_name="epicurve_report.html",
    mime="text/html",
)

st.caption(f"Report size: {len(report_html) / 1024:.0f} KB")
