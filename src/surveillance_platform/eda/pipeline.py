"""Pipeline orchestrator — runs the M5 analytical functions and bundles
their output into one :class:`EDAResult`.

Mirrors Milestone 4's ``prepare()`` orchestration pattern: this module
only coordinates already-independently-testable functions defined in
sibling modules; it does not contain analytical logic itself. Consumes
the plain, cleaned DataFrame produced by Milestone 4
(``PreparationResult.data``) and the same ``RoleConfiguration`` —
never the whole ``PreparationResult``, so M5 stays decoupled from M4's
internal report structure.
"""

from __future__ import annotations

import pandas as pd

from surveillance_platform.eda.country_comparison import country_comparison
from surveillance_platform.eda.descriptive import (
    case_definition_summary,
    descriptive_statistics,
    distribution_summary,
    resolution_summary,
)
from surveillance_platform.eda.missingness import missingness_summary
from surveillance_platform.eda.population import population_normalized_summary
from surveillance_platform.eda.report import EDAResult
from surveillance_platform.eda.time_series import time_series_summary
from surveillance_platform.role_configuration import RoleConfiguration


def analyze(
    prepared_data: pd.DataFrame,
    role_config: RoleConfiguration,
    population_data: pd.DataFrame | None = None,
) -> EDAResult:
    """Run Exploratory Data Analysis over an already-prepared dataset.

    ``prepared_data`` is the plain, cleaned DataFrame from Milestone
    4's ``PreparationResult.data`` (role columns preserved, plus the
    derived ``time`` column). ``population_data`` is optional — if
    omitted, ``EDAResult.population_normalized`` is ``None`` and every
    other analytical output is produced normally. Never mutates
    ``prepared_data`` or ``population_data``.
    """
    time_series = time_series_summary(prepared_data, role_config)

    return EDAResult(
        descriptive=descriptive_statistics(prepared_data, role_config),
        distribution=distribution_summary(prepared_data, role_config),
        missingness=missingness_summary(prepared_data),
        resolution=resolution_summary(prepared_data),
        case_definition=case_definition_summary(prepared_data),
        time_series=time_series,
        country_comparison=country_comparison(prepared_data, role_config),
        population_normalized=population_normalized_summary(
            time_series, population_data
        ),
    )
