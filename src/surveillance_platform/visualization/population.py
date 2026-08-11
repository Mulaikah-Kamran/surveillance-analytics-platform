"""Population-normalized reported-case-rate distribution.

Optional, mirroring M5's own optionality: ``EDAResult.population_normalized``
is ``None`` whenever ``analyze()`` was not given population reference
data, and this visualization is omitted (returns ``None``) rather than
raising or fabricating a chart. M6 never independently acquires,
imputes, or estimates population data — it only renders the rate M5
already computed.

Always labeled *reported cases per 100,000 population* — never
"incidence" (PFD Section 30, extended to the normalized figure by
``docs/eda.md``).
"""

from __future__ import annotations

import plotly.graph_objects as go

from surveillance_platform.eda.report import EDAResult
from surveillance_platform.visualization._theme import (
    apply_base_layout,
    color_map,
)


def population_normalized_distribution(eda_result: EDAResult) -> go.Figure | None:
    """Distribution of reported cases per 100,000 population, by country.

    Returns ``None`` — not an error, not an empty figure — when
    ``eda_result.population_normalized`` is absent or has no rate
    entries, so callers (and the M6 orchestrator) can omit this
    visualization gracefully, exactly as M5 omits the underlying
    result.
    """
    population_normalized = eda_result.population_normalized
    if population_normalized is None or not population_normalized.rates:
        return None

    rates = population_normalized.rates
    countries = sorted({entry.country for entry in rates})
    colors = color_map(countries)

    figure = go.Figure()
    for country in countries:
        values = [
            entry.reported_cases_per_100000
            for entry in rates
            if entry.country == country
        ]
        figure.add_trace(
            go.Box(
                y=values,
                name=country,
                marker_color=colors[country],
                boxpoints="all",
                jitter=0.4,
                pointpos=0,
            )
        )

    apply_base_layout(
        figure,
        title="Population-Normalized Reported-Case Rate by Country",
    )
    figure.update_yaxes(title_text="Reported cases per 100,000 population")
    figure.update_xaxes(title_text="Country")
    figure.update_layout(showlegend=False)
    return figure
