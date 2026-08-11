"""Visualization module.

Implements Milestone 6: the five finalized visualizations that
represent Milestone 5's (``EDAResult``) analytical output. M6 is a
pure representation layer -- it consumes only ``EDAResult``, never
``prepared_data`` directly, and performs no cleaning, imputation,
recomputation of M5 statistics, hypothesis testing, regression,
forecasting, or smoothing/interpolation of its own.

Public API:

* :func:`visualize` -- run all five M6 visualizations at once.
* :class:`VisualizationResult` -- the bundled output (see
  ``surveillance_platform.visualization.report``).

Each visualization function is also independently importable and
testable:

* :func:`~surveillance_platform.visualization.trend.annual_surveillance_trend`
* :func:`~surveillance_platform.visualization.distribution.annual_distribution_by_country`
* :func:`~surveillance_platform.visualization.distribution.surveillance_measure_distribution`
* :func:`~surveillance_platform.visualization.population.population_normalized_distribution`
* :func:`~surveillance_platform.visualization.profile.surveillance_resolution_profile`

See ``docs/visualization.md`` for the full M6 design and the mapping
from each visualization to its ``EDAResult`` inputs.
"""

from surveillance_platform.visualization.distribution import (
    annual_distribution_by_country,
    surveillance_measure_distribution,
)
from surveillance_platform.visualization.pipeline import visualize
from surveillance_platform.visualization.population import (
    population_normalized_distribution,
)
from surveillance_platform.visualization.profile import (
    surveillance_resolution_profile,
)
from surveillance_platform.visualization.report import VisualizationResult
from surveillance_platform.visualization.trend import annual_surveillance_trend

__all__ = [
    "VisualizationResult",
    "annual_distribution_by_country",
    "annual_surveillance_trend",
    "population_normalized_distribution",
    "surveillance_measure_distribution",
    "surveillance_resolution_profile",
    "visualize",
]
