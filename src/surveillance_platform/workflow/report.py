"""Report structures for the workflow module (Milestone 8, ADR-010).

Kept minimal, matching the M4-M7 convention: a plain typed dataclass,
no formal state-machine framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import pandas as pd

from surveillance_platform.role_configuration import RoleConfiguration

#: Section 19's exact lifecycle: Created -> Configured -> Running ->
#: Completed, with a Failed branch reachable from any stage.
SessionStatus = Literal["Created", "Configured", "Running", "Completed", "Failed"]


@dataclass
class AnalysisSession:
    """The Analysis Session (PFD Section 10/19): dataset, role
    configuration, analysis configuration, workflow status, results --
    tying every stage's output back to the inputs that produced it.

    ``results`` accumulates one entry per completed stage (e.g.
    ``"preparation"``, ``"eda"``, ``"visualization"``, ``"forecast"``)
    rather than a fixed set of named fields, since not every session
    necessarily runs every stage. ``analysis_config`` exists for
    structural completeness per Section 15, but ADR-010 Decision J
    locked every current analytical parameter (forecast horizon,
    training window, etc.) as fixed, not user-configurable -- so it is
    empty in Milestone 8, not a set of exposed knobs.

    ``status`` only ever becomes ``"Failed"`` via a caught
    ``DataPreparationError`` or ``RoleConfigurationError`` in the
    current pipeline (ADR-010): EDA, Visualization, and Forecasting
    are all designed to degrade gracefully (``ForecastResult`` never
    raises on an ordinary data limitation) rather than hard-stop.
    """

    status: SessionStatus = "Created"
    dataset: pd.DataFrame | None = None
    role_config: RoleConfiguration | None = None
    analysis_config: dict[str, Any] = field(default_factory=dict)
    results: dict[str, Any] = field(default_factory=dict)
    error_messages: list[str] = field(default_factory=list)
