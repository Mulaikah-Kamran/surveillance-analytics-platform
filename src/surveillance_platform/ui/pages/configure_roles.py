"""Configure Roles page (Milestone 8, ADR-010).

Per ADR-004: explicit user configuration, never auto-assignment.
Optional column highlighting is shown as a caption hint next to each
dropdown -- never as the dropdown's pre-selected value.
"""

import streamlit as st

from surveillance_platform import workflow
from surveillance_platform.role_configuration import RoleConfiguration
from surveillance_platform.ui.highlighting import suggest_roles

st.title("Configure Roles")

session = st.session_state.setdefault("analysis_session", workflow.create_session())

if session.dataset is None:
    st.warning("Load a dataset first, on the **Load Dataset** page.")
    st.stop()

columns = list(session.dataset.columns)
suggestions = suggest_roles(session.dataset)

st.markdown(
    "Assign each required role to a column. Suggestions are a "
    "convenience only -- nothing is pre-selected; you choose."
)

col1, col2 = st.columns(2)
with col1:
    time_col = st.selectbox(
        "Time",
        columns,
        index=None,
        placeholder="-- select a column --",
        key="role_time",
    )
    if suggestions["time"]:
        st.caption(f"Suggested: `{suggestions['time']}`")

    location_col = st.selectbox(
        "Location",
        columns,
        index=None,
        placeholder="-- select a column --",
        key="role_location",
    )
    if suggestions["location"]:
        st.caption(f"Suggested: `{suggestions['location']}`")

with col2:
    measure_col = st.selectbox(
        "Surveillance Measure",
        columns,
        index=None,
        placeholder="-- select a column --",
        key="role_measure",
    )
    if suggestions["surveillance_measure"]:
        st.caption(f"Suggested: `{suggestions['surveillance_measure']}`")

    identifier_col = st.selectbox(
        "Identifier (optional)", ["(none)"] + columns, index=0, key="role_identifier"
    )
    if suggestions["identifier"]:
        st.caption(f"Suggested: `{suggestions['identifier']}`")

if time_col and location_col and measure_col:
    role_config = RoleConfiguration(
        time=time_col,
        location=location_col,
        surveillance_measure=measure_col,
        identifier=None if identifier_col == "(none)" else identifier_col,
    )
    session = workflow.configure_roles(session, role_config)
    st.session_state["analysis_session"] = session

    if session.status == "Failed":
        st.error("This role configuration is invalid:")
        for message in session.error_messages:
            st.markdown(f"- {message}")
    else:
        st.success(
            "Role configuration is valid. Continue to **Data Preparation** in the sidebar."
        )
else:
    st.info(
        "Select all three required roles (Time, Location, Surveillance Measure) to continue."
    )
