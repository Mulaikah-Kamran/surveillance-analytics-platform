"""Caching wrappers around workflow controller and data_loading functions
(ADR-010).

The only place `st.cache_data` is applied. `workflow/` and
`data_loading/` themselves stay Streamlit-free (ADR-010's
independence requirement) -- these wrappers apply caching from the
outside, without needing a decorator inside either module. Verified
during Batch 3 development: `st.cache_data` correctly wraps an
already-defined function, not just as a decorator at definition time.
"""

import streamlit as st

from surveillance_platform import data_loading, workflow

cached_get_sample_dataset = st.cache_data(data_loading.get_sample_dataset)
cached_fetch_population_data = st.cache_data(data_loading.fetch_population_data)
cached_run_preparation = st.cache_data(workflow.run_preparation)
cached_run_eda = st.cache_data(workflow.run_eda)
cached_run_visualization = st.cache_data(workflow.run_visualization)
cached_run_forecasting = st.cache_data(workflow.run_forecasting)
