"""Surveillance resolution / case-definition profile.

Visualizes M5's two categorical surveillance-metadata distributions —
``T_res`` (temporal resolution) and ``case_definition_standardised`` —
as bar charts of reporting characteristics, not disease burden. These
describe *how* cases were reported (weekly vs. monthly; confirmed vs.
total), never *how many* cases occurred, and are kept visually and
semantically distinct from the reported-case-count visualizations.

Both ``EDAResult.resolution`` and ``EDAResult.case_definition`` are
independently optional (``None`` when the corresponding column is
absent from the dataset, per M5's graceful-degradation contract) — so
this visualization degrades the same way: it renders whichever of the
two is available and omits (returns ``None``) only if neither is.
"""

from __future__ import annotations

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from surveillance_platform.eda.report import CategoricalDistribution, EDAResult

_RESOLUTION_TITLE = "Temporal Resolution (T_res)"
_CASE_DEFINITION_TITLE = "Case Definition (case_definition_standardised)"


def _bar_trace(distribution: CategoricalDistribution) -> go.Bar:
    categories = sorted(distribution.counts)
    counts = [distribution.counts[category] for category in categories]
    return go.Bar(x=categories, y=counts, showlegend=False)


def surveillance_resolution_profile(eda_result: EDAResult) -> go.Figure | None:
    """Bar-chart profile of ``T_res`` and/or ``case_definition_standardised``.

    Returns ``None`` when both ``EDAResult.resolution`` and
    ``EDAResult.case_definition`` are ``None`` (neither column was
    present in the analyzed dataset) — there is no surveillance
    metadata to profile, so nothing is fabricated.
    """
    panels: list[tuple[str, CategoricalDistribution]] = []
    if eda_result.resolution is not None:
        panels.append((_RESOLUTION_TITLE, eda_result.resolution))
    if eda_result.case_definition is not None:
        panels.append((_CASE_DEFINITION_TITLE, eda_result.case_definition))

    if not panels:
        return None

    figure = make_subplots(
        rows=1,
        cols=len(panels),
        subplot_titles=[title for title, _ in panels],
    )
    for index, (_, distribution) in enumerate(panels, start=1):
        figure.add_trace(_bar_trace(distribution), row=1, col=index)
        figure.update_yaxes(title_text="Observation count", row=1, col=index)

    figure.update_layout(
        title=(
            "Surveillance Reporting Characteristics "
            "(reporting metadata, not disease burden)"
        ),
        template="plotly_white",
        showlegend=False,
        margin={"l": 60, "r": 30, "t": 80, "b": 50},
    )
    return figure
