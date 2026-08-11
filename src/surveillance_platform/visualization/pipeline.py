"""Pipeline orchestrator — runs the M6 visualization functions and
bundles their output into one :class:`VisualizationResult`.

Mirrors Milestone 4's ``prepare()`` / Milestone 5's ``analyze()``
orchestration pattern: this module only coordinates already
independently-testable functions defined in sibling modules; it
contains no visualization or analytical logic of its own. Consumes
only an :class:`~surveillance_platform.eda.report.EDAResult` — never
``prepared_data`` — per the frozen M5 -> M6 boundary.
"""

from __future__ import annotations

from surveillance_platform.eda.report import EDAResult
from surveillance_platform.visualization.distribution import (
    annual_distribution_by_country,
    surveillance_measure_distribution,
)
from surveillance_platform.visualization.population import (
    population_normalized_distribution,
)
from surveillance_platform.visualization.profile import (
    surveillance_resolution_profile,
)
from surveillance_platform.visualization.report import VisualizationResult
from surveillance_platform.visualization.trend import annual_surveillance_trend


def visualize(eda_result: EDAResult) -> VisualizationResult:
    """Generate all five M6 visualizations from ``eda_result``.

    Never mutates ``eda_result``. ``population_normalized_distribution``
    and ``surveillance_profile`` may be ``None`` on the returned
    result when the corresponding M5 input is absent — this is not an
    error (see :mod:`surveillance_platform.visualization.report`).
    """
    return VisualizationResult(
        annual_trend=annual_surveillance_trend(eda_result),
        annual_distribution_by_country=annual_distribution_by_country(eda_result),
        surveillance_measure_distribution=surveillance_measure_distribution(eda_result),
        population_normalized_distribution=population_normalized_distribution(
            eda_result
        ),
        surveillance_profile=surveillance_resolution_profile(eda_result),
    )
