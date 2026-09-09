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
        st.Page(f"{PAGES_DIR}/load_dataset.py", title="Load Dataset"),
        st.Page(f"{PAGES_DIR}/configure_roles.py", title="Configure Roles"),
        st.Page(f"{PAGES_DIR}/data_preparation.py", title="Data Preparation"),
        st.Page(f"{PAGES_DIR}/exploratory_analysis.py", title="Exploratory Analysis"),
        st.Page(f"{PAGES_DIR}/visualization.py", title="Visualization"),
        st.Page(f"{PAGES_DIR}/forecasting.py", title="Forecasting"),
        st.Page(f"{PAGES_DIR}/results_export.py", title="Results & Export"),
    ]
)

with st.sidebar:
    st.markdown("### Epicurve")
    st.caption("Public Health Surveillance & Analytics Platform")

pg.run()
