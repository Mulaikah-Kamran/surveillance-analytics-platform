"""Load Dataset page (Milestone 8, ADR-010).

Single ingestion path (ADR-010): st.file_uploader is the only way
data enters the pipeline, used both for a user's own file and for the
"Download sample dataset" convenience (which still requires the same
explicit upload step afterward).

Starter dataset scoped to four countries (2026-09-10): the full
National Extract covers 129 countries, which is a lot for a first
download -- offering the four countries this project was actually
built and evaluated around (ADR-008) instead, with a separate link to
OpenDengue's own data explorer for anyone who wants a different
country or date range. Uploading a dataset from any other source was
always supported and still is.
"""

import streamlit as st

from surveillance_platform import data_loading, workflow
from surveillance_platform.ui.cached_pipeline import cached_get_starter_sample_dataset

st.title("Load Dataset")

session = st.session_state.setdefault("analysis_session", workflow.create_session())

if session.dataset is None:
    st.markdown(
        "Turn raw surveillance data into clean numbers, clear charts, and "
        "honest forecasts, in seven steps: load, configure, clean, explore, "
        "visualize, forecast, and export."
    )

st.markdown(
    "Upload a surveillance dataset (CSV) from any source. If you don't have "
    "one handy, start with the sample below (Sri Lanka, Bangladesh, Maldives, "
    "and Nepal, the four countries this project was built around), or get a "
    "different country or date range directly from OpenDengue. Either way, "
    "upload the CSV the same way as any other file."
)

col1, col2 = st.columns(2)
with col1:
    sample_bytes = cached_get_starter_sample_dataset()
    st.download_button(
        "Download sample dataset (4 countries)",
        data=sample_bytes,
        file_name="opendengue_starter_sample.csv",
        mime="text/csv",
    )
with col2:
    st.link_button(
        "Get other countries from OpenDengue",
        "https://opendengue.org/data.html",
    )

uploaded_file = st.file_uploader(
    "Upload your surveillance dataset (CSV)",
    type=["csv"],
    max_upload_size=50,  # MB -- ADR-010 Security section
)

if uploaded_file is not None:
    try:
        data = data_loading.load_csv(uploaded_file)
    except data_loading.FileTooLargeError as exc:
        st.error(str(exc))
        st.stop()
    except Exception as exc:  # noqa: BLE001 -- pandas can raise many distinct
        # parser exception types for a malformed CSV; any of them should show
        # this same friendly message, not crash the page.
        st.error(f"Could not read this file as a CSV: {exc}")
        st.stop()

    warning = data_loading.check_spatial_resolution(data)
    if warning:
        st.warning(warning)

    st.success(f"Loaded {len(data):,} rows, {len(data.columns)} columns.")
    st.dataframe(data.head())
    st.caption("Column types:")
    st.dataframe(data.dtypes.astype(str).rename("dtype"))

    session = workflow.set_dataset(session, data)
    st.session_state["analysis_session"] = session
    st.info("Dataset loaded. Continue to **Configure Roles** in the sidebar.")
elif session.dataset is not None:
    st.success(f"Dataset already loaded: {len(session.dataset):,} rows.")
    st.dataframe(session.dataset.head())
