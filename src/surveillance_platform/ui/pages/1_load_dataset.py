"""Load Dataset page (Milestone 8, ADR-010).

Single ingestion path (ADR-010): st.file_uploader is the only way
data enters the pipeline, used both for a user's own file and for the
"Download sample dataset" convenience (which still requires the same
explicit upload step afterward).
"""

import streamlit as st

from surveillance_platform import data_loading, workflow
from surveillance_platform.ui.cached_pipeline import cached_get_sample_dataset

st.title("Load Dataset")

session = st.session_state.setdefault("analysis_session", workflow.create_session())

st.markdown(
    "Upload a surveillance dataset (CSV). If you don't have one handy, "
    "download the real, checksum-verified sample dataset below, then "
    "upload it the same way as any other file."
)

sample_bytes = cached_get_sample_dataset()
st.download_button(
    "Download sample dataset (OpenDengue National Extract)",
    data=sample_bytes,
    file_name="National_extract_V1_3.csv",
    mime="text/csv",
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
    except Exception as exc:  # pragma: no cover -- malformed CSV, not our validation
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
