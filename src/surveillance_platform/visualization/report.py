"""Result structure produced by the Visualization module.

Mirrors the flat-dataclass style already used by
``data_preparation.report.PreparationResult`` and
``eda.report.EDAResult``: one plain container bundling the output of
independently-testable functions, no nested framework.

``surveillance_profile`` and ``population_normalized_distribution``
are ``None`` rather than a figure when the underlying M5 input is
absent (no ``T_res``/``case_definition_standardised`` column at all,
or no population reference data was supplied) — the same
"absent, not an error" contract M5 already established.
"""

from __future__ import annotations

from dataclasses import dataclass

import plotly.graph_objects as go


@dataclass
class VisualizationResult:
    """The five M6 visualizations produced from one :class:`EDAResult`."""

    annual_trend: go.Figure
    annual_distribution_by_country: go.Figure
    surveillance_measure_distribution: go.Figure
    population_normalized_distribution: go.Figure | None
    surveillance_profile: go.Figure | None
