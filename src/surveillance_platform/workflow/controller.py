"""Workflow Controller (Milestone 8, ADR-010).

Orchestrates the frozen analytical workflow and manages the
AnalysisSession lifecycle (PFD Section 14/19). Zero Streamlit
imports: every function here is plain Python, runnable and testable
without the UI layer -- deleting `ui/` must leave this fully
functional (ADR-010's independence requirement).

Each function takes an AnalysisSession and returns a new one
(dataclasses.replace-based, never mutates its input), consistent with
the "never mutates" convention M4-M7 already established.
"""

from __future__ import annotations

import dataclasses

import pandas as pd

from surveillance_platform.data_preparation import prepare
from surveillance_platform.data_preparation.exceptions import DataPreparationError
from surveillance_platform.eda import analyze
from surveillance_platform.forecasting import forecast
from surveillance_platform.role_configuration import RoleConfiguration, validate
from surveillance_platform.role_configuration.exceptions import RoleConfigurationError
from surveillance_platform.visualization import visualize
from surveillance_platform.workflow.report import AnalysisSession


def create_session() -> AnalysisSession:
    """A fresh, empty session -- status "Created"."""
    return AnalysisSession()


def set_dataset(session: AnalysisSession, dataset: pd.DataFrame) -> AnalysisSession:
    """Attach the loaded (raw, uploaded) dataset to the session.

    Stays in "Created" status -- role configuration hasn't happened
    yet, so the session isn't "Configured" until :func:`configure_roles`
    succeeds.
    """
    return dataclasses.replace(session, dataset=dataset, status="Created")


def configure_roles(
    session: AnalysisSession, role_config: RoleConfiguration
) -> AnalysisSession:
    """Validate and attach a role configuration.

    Requires ``session.dataset`` to already be set. Catches
    ``RoleConfigurationError`` and sets status "Failed" with its
    violation messages, rather than letting it propagate -- the same
    "document, don't crash" pattern used throughout this project.
    """
    if session.dataset is None:
        raise ValueError("configure_roles() requires a dataset to already be set.")
    try:
        validate(role_config, session.dataset.columns)
    except RoleConfigurationError as exc:
        return dataclasses.replace(session, status="Failed", error_messages=exc.violations)
    return dataclasses.replace(session, role_config=role_config, status="Configured")


def run_preparation(session: AnalysisSession) -> AnalysisSession:
    """Run Milestone 4's ``prepare()``.

    Requires status "Configured". Catches ``DataPreparationError``
    (confirmed: the only hard-stop exception in the current pipeline,
    raised solely by Validation) and sets status "Failed" with its
    violation messages -- implementing PFD Section 14's exact failure
    behavior: halt downstream execution, preserve diagnostics, return
    control to the presentation layer.
    """
    if session.status != "Configured":
        raise ValueError(
            f"run_preparation() requires status 'Configured', got {session.status!r}."
        )
    try:
        result = prepare(session.dataset, session.role_config)
    except DataPreparationError as exc:
        return dataclasses.replace(session, status="Failed", error_messages=exc.violations)
    results = {**session.results, "preparation": result}
    return dataclasses.replace(session, status="Running", results=results)


def run_eda(
    session: AnalysisSession, population_data: pd.DataFrame | None = None
) -> AnalysisSession:
    """Run Milestone 5's ``analyze()`` over the prepared dataset.

    Requires a completed "preparation" stage. ``analyze()`` has no
    hard-stop failure mode in the current design (only Validation
    does), so this never sets status "Failed".
    """
    if "preparation" not in session.results:
        raise ValueError("run_eda() requires a completed preparation stage.")
    prepared_data = session.results["preparation"].data
    eda_result = analyze(prepared_data, session.role_config, population_data)
    results = {**session.results, "eda": eda_result}
    return dataclasses.replace(session, status="Running", results=results)


def run_visualization(session: AnalysisSession) -> AnalysisSession:
    """Run Milestone 6's ``visualize()`` over the EDA result.

    Requires a completed "eda" stage. Consumes ``EDAResult`` only,
    never ``prepared_data`` directly, matching M6's own frozen
    boundary.
    """
    if "eda" not in session.results:
        raise ValueError("run_visualization() requires a completed eda stage.")
    viz_result = visualize(session.results["eda"])
    results = {**session.results, "visualization": viz_result}
    return dataclasses.replace(session, status="Running", results=results)


def run_forecasting(
    session: AnalysisSession, population_by_country: dict[str, pd.Series]
) -> AnalysisSession:
    """Run Milestone 7's ``forecast()`` over the prepared dataset.

    Requires a completed "preparation" stage -- forecasting consumes
    ``PreparationResult.data`` directly, not ``EDAResult`` (ADR-009).
    This is the pipeline's terminal analytical stage (PFD Section 14:
    ...Forecasting -> Reporting, where Reporting is export of already-
    computed results, not a further computational stage) -- sets
    status "Completed" on success. ``forecast_track()`` never raises
    on an ordinary data limitation, so this also never sets "Failed".
    """
    if "preparation" not in session.results:
        raise ValueError("run_forecasting() requires a completed preparation stage.")
    prepared_data = session.results["preparation"].data
    forecast_results = forecast(prepared_data, session.role_config, population_by_country)
    results = {**session.results, "forecast": forecast_results}
    return dataclasses.replace(session, status="Completed", results=results)
