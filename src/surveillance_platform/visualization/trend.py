"""Annual surveillance trend — country small multiples.

Consumes :class:`~surveillance_platform.eda.report.TimeSeriesSummary`
(via :class:`~surveillance_platform.eda.report.EDAResult`) only. Plots
the annual ``reported_case_total`` M5 already aggregated per
(country, year) — never raw or sub-annual values, and never a
smoothed, interpolated, or forecast line.

One subplot per country ("small multiples"), each with its own
independent axes, rather than a single chart with every country
sharing one y-axis — countries can differ by orders of magnitude in
reported-case volume, and a shared axis would flatten the smaller
countries' trends to near-invisibility.
"""

from __future__ import annotations

import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from surveillance_platform.eda.report import CountryYearSummary, EDAResult
from surveillance_platform.visualization._theme import (
    color_map,
    empty_figure_guard,
)

_MAX_COLUMNS = 2


def _heterogeneity_note(entry: CountryYearSummary) -> str | None:
    """Describe, in plain language, which reporting inconsistency applies, if any.

    Returns ``None`` when both flags are ``True`` or ``None`` (i.e. the
    underlying column was absent, which is not a heterogeneity finding).
    """
    flagged: list[str] = []
    if entry.resolution_homogeneous is False:
        flagged.append("reporting resolution changed mid-year")
    if entry.case_definition_homogeneous is False:
        flagged.append("case definition changed mid-year")
    return "; ".join(flagged) if flagged else None


def annual_surveillance_trend(eda_result: EDAResult) -> go.Figure:
    """Build the annual reported-case-total small-multiples trend chart.

    Raises :class:`EmptyVisualizationInputError` if
    ``eda_result.time_series.country_years`` is empty — there is
    nothing to plot, and an empty chart would misleadingly imply a
    dataset with zero surveillance activity rather than a dataset
    that was never analyzed.
    """
    country_years = eda_result.time_series.country_years
    empty_figure_guard(
        not country_years,
        "annual_surveillance_trend: EDAResult.time_series.country_years is "
        "empty; there is no annual trend data to visualize.",
    )

    by_country: dict[str, list[CountryYearSummary]] = {}
    for entry in country_years:
        by_country.setdefault(entry.country, []).append(entry)

    countries = sorted(by_country)
    colors = color_map(countries)

    n_countries = len(countries)
    n_cols = min(_MAX_COLUMNS, n_countries)
    n_rows = math.ceil(n_countries / n_cols)

    figure = make_subplots(
        rows=n_rows,
        cols=n_cols,
        subplot_titles=countries,
        shared_xaxes=False,
        shared_yaxes=False,
    )

    for index, country in enumerate(countries):
        row = index // n_cols + 1
        col = index % n_cols + 1
        entries = sorted(by_country[country], key=lambda e: e.year)

        years = [e.year for e in entries]
        totals = [e.reported_case_total for e in entries]
        notes = [_heterogeneity_note(e) for e in entries]

        marker_symbols = ["diamond" if note else "circle" for note in notes]
        marker_sizes = [12 if note else 8 for note in notes]
        hover_text = [
            (
                f"{country}, {year}<br>Reported-case total: {total:g}"
                + (f"<br>⚠ {note}" if note else "")
            )
            for year, total, note in zip(years, totals, notes)
        ]

        figure.add_trace(
            go.Scatter(
                x=years,
                y=totals,
                mode="lines+markers",
                name=country,
                legendgroup=country,
                showlegend=False,
                line={"color": colors[country]},
                marker={
                    "color": colors[country],
                    "symbol": marker_symbols,
                    "size": marker_sizes,
                    "line": {
                        "width": [2 if note else 0 for note in notes],
                        "color": "#B00020",
                    },
                },
                hovertext=hover_text,
                hoverinfo="text",
            ),
            row=row,
            col=col,
        )
        figure.update_yaxes(title_text="Reported-case total", row=row, col=col)
        figure.update_xaxes(
            title_text="Year",
            row=row,
            col=col,
            tickformat="d",
            nticks=8,
            tickangle=-45,
        )

    figure.update_layout(
        title=(
            "Annual Surveillance Trend by Country "
            "(reported-case totals; ⬦ = inconsistent reporting that year)"
        ),
        template="plotly_white",
        showlegend=False,
        height=320 * n_rows,
    )
    return figure
