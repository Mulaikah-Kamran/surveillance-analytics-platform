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

st.set_page_config(page_title="Epicurve", page_icon="assets/icon.png", layout="wide")

# The lockup image's "Epicurve" text is baked into a static PNG, so it
# can't inherit Streamlit's own theme colors the way native text does.
# Dark mode was shipping with black text on a dark background,
# effectively invisible -- fixed by keeping two variants and picking
# the right one via st.context.theme.type. Falls back to the light
# variant if the theme type can't be read yet (e.g. the very first
# render of a session, per st.context's own documented caveat), since
# light-on-light is still readable while dark-on-dark is not.
_theme_type = getattr(getattr(st.context, "theme", None), "type", "light")
_lockup_path = (
    "assets/logo_lockup_dark.png"
    if _theme_type == "dark"
    else "assets/logo_lockup_light.png"
)
st.logo(_lockup_path, icon_image="assets/icon.png", size="large")

pg = st.navigation(
    [
        st.Page(
            f"{PAGES_DIR}/load_dataset.py",
            title="Load Dataset",
            icon=":material/upload_file:",
        ),
        st.Page(
            f"{PAGES_DIR}/configure_roles.py",
            title="Configure Roles",
            icon=":material/tune:",
        ),
        st.Page(
            f"{PAGES_DIR}/data_preparation.py",
            title="Data Preparation",
            icon=":material/cleaning_services:",
        ),
        st.Page(
            f"{PAGES_DIR}/exploratory_analysis.py",
            title="Exploratory Analysis",
            icon=":material/search:",
        ),
        st.Page(
            f"{PAGES_DIR}/visualization.py",
            title="Visualization",
            icon=":material/bar_chart:",
        ),
        st.Page(
            f"{PAGES_DIR}/forecasting.py",
            title="Forecasting",
            icon=":material/trending_up:",
        ),
        st.Page(
            f"{PAGES_DIR}/results_export.py",
            title="Results & Export",
            icon=":material/description:",
        ),
    ]
)

with st.sidebar:
    st.caption(
        "Public Health Surveillance & Analytics Platform, built for public health analysts."
    )

pg.run()
