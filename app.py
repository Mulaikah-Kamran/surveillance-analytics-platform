"""Epicurve -- Streamlit entrypoint (Milestone 8, ADR-010).

Run with: streamlit run app.py

Thin by design (ADR-006, ADR-010): this file only wires up
navigation. All analytical logic lives in the Streamlit-free
`workflow`/`data_loading` modules and the individually-tested
backend modules from M4-M7; this file and the page files under
src/surveillance_platform/ui/pages/ are the only places in the
project permitted to import streamlit.
"""

import streamlit as st

PAGES_DIR = "src/surveillance_platform/ui/pages"

st.set_page_config(page_title="Epicurve", layout="wide")

pg = st.navigation(
    [
        st.Page(f"{PAGES_DIR}/1_load_dataset.py", title="Load Dataset"),
        st.Page(f"{PAGES_DIR}/2_configure_roles.py", title="Configure Roles"),
        st.Page(f"{PAGES_DIR}/3_data_preparation.py", title="Data Preparation"),
        st.Page(f"{PAGES_DIR}/4_exploratory_analysis.py", title="Exploratory Analysis"),
        st.Page(f"{PAGES_DIR}/5_visualization.py", title="Visualization"),
        st.Page(f"{PAGES_DIR}/6_forecasting.py", title="Forecasting"),
        st.Page(f"{PAGES_DIR}/7_results_export.py", title="Results & Export"),
    ]
)

with st.sidebar:
    st.markdown("### Epicurve")
    st.caption("Public Health Surveillance & Analytics Platform")

pg.run()
