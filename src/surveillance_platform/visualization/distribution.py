"""Two distribution-shaped M6 visualizations.

* :func:`annual_distribution_by_country` — the spread of *annual
  reported-case totals* (M5's ``TimeSeriesSummary.country_years``)
  across countries. Explicitly reported-case counts, never labeled as
  incidence or population-adjusted burden.
* :func:`surveillance_measure_distribution` — the distribution of the
  configured Surveillance Measure, built directly from M5's
  already-computed ``DescriptiveSummary`` / ``DistributionSummary``
  (count, mean, quartiles, min/max, zero-value share). This does not
  recompute any statistic from lower-level rows; it renders the
  summary-statistic five-number-summary M5 already produced, using
  Plotly's pre-computed ("SPC-style") box trace.
"""

from __future__ import annotations

import plotly.graph_objects as go

from surveillance_platform.eda.report import EDAResult
from surveillance_platform.visualization._theme import (
    apply_base_layout,
    color_map,
    empty_figure_guard,
)


def annual_distribution_by_country(eda_result: EDAResult) -> go.Figure:
    """Distribution of annual reported-case totals, one box per country.

    Uses the per-(country, year) ``reported_case_total`` values M5
    already aggregated — no sub-annual or raw rows are touched, and no
    new analytical statistic is computed beyond what a standard
    box-plot rendering requires.
    """
    country_years = eda_result.time_series.country_years
    empty_figure_guard(
        not country_years,
        "annual_distribution_by_country: EDAResult.time_series.country_years "
        "is empty; there is no annual distribution to visualize.",
    )

    countries = sorted({entry.country for entry in country_years})
    colors = color_map(countries)

    figure = go.Figure()
    for country in countries:
        totals = [
            entry.reported_case_total
            for entry in country_years
            if entry.country == country
        ]
        figure.add_trace(
            go.Box(
                y=totals,
                name=country,
                marker_color=colors[country],
                boxpoints="all",
                jitter=0.4,
                pointpos=0,
            )
        )

    apply_base_layout(
        figure,
        title="Annual Distribution of Reported-Case Totals by Country",
    )
    figure.update_yaxes(title_text="Reported-case total (annual)")
    figure.update_xaxes(title_text="Country")
    figure.update_layout(showlegend=False)
    return figure


def surveillance_measure_distribution(eda_result: EDAResult) -> go.Figure:
    """Render M5's Surveillance Measure summary statistics as a box trace.

    Built entirely from ``EDAResult.descriptive`` and
    ``EDAResult.distribution`` — the pre-computed five-number summary
    (min, q25, median, q75, max) plus mean and zero-value share. No
    row-level data is accessed and no statistic is recomputed; this is
    a direct visual rendering of M5's own output.
    """
    descriptive = eda_result.descriptive
    distribution = eda_result.distribution

    empty_figure_guard(
        descriptive.count == 0,
        "surveillance_measure_distribution: EDAResult.descriptive.count is "
        "0; there is no Surveillance Measure data to visualize.",
    )

    figure = go.Figure(
        go.Box(
            q1=[distribution.q25],
            median=[distribution.q50],
            q3=[distribution.q75],
            lowerfence=[descriptive.minimum],
            upperfence=[descriptive.maximum],
            mean=[descriptive.mean],
            boxmean=True,
            name="Surveillance Measure",
        )
    )

    apply_base_layout(
        figure,
        title=(
            "Surveillance Measure Distribution "
            f"(n={descriptive.count}, mean={descriptive.mean:.1f}, "
            f"std={descriptive.std:.1f}, "
            f"zero-value share={distribution.zero_value_share:.1%})"
        ),
    )
    figure.update_yaxes(title_text="Surveillance Measure value")
    figure.update_layout(showlegend=False)
    return figure
