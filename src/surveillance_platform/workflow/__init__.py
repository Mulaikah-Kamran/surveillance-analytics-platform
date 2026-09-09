"""Workflow Controller module (Milestone 8, ADR-010).

Orchestrates the frozen analytical workflow (Validation -> Profiling ->
Quality Assessment -> Temporal Standardization -> Cleaning -> EDA ->
Visualization -> Forecasting -> Reporting) and manages the Analysis
Session lifecycle. Zero Streamlit imports -- fully runnable and
testable as plain Python (ADR-010's independence requirement).

Public API:

* :class:`AnalysisSession` -- the session dataclass (dataset, role
  configuration, analysis configuration, status, results).
* :func:`create_session`, :func:`set_dataset`, :func:`configure_roles`,
  :func:`run_preparation`, :func:`run_eda`, :func:`run_visualization`,
  :func:`run_forecasting` -- the controller functions, each taking an
  ``AnalysisSession`` and returning a new one (never mutates its
  input).

See ``docs/adr/ADR-010-ui-integration-strategy.md`` for the full design.
"""

from surveillance_platform.workflow.controller import (
    configure_roles,
    create_session,
    run_eda,
    run_forecasting,
    run_preparation,
    run_visualization,
    set_dataset,
)
from surveillance_platform.workflow.report import AnalysisSession, SessionStatus

__all__ = [
    "AnalysisSession",
    "SessionStatus",
    "configure_roles",
    "create_session",
    "run_eda",
    "run_forecasting",
    "run_preparation",
    "run_visualization",
    "set_dataset",
]
