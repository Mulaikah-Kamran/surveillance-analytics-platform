"""Small shared plotting helpers for the visualization module.

Kept deliberately minimal, in the same spirit as ``data_preparation``
and ``eda``: this module exists only because two or more of the five
required visualizations genuinely need the same thing (a deterministic
per-country color and a consistent way to report "there is nothing to
plot"), not as general-purpose visualization infrastructure.
"""

from __future__ import annotations

import plotly.graph_objects as go

# A small, fixed, colorblind-friendlier qualitative palette (Plotly's
# "Set2"-style hues). Not data-driven — deterministic and independent
# of how many countries happen to be present in a given dataset.
_PALETTE: tuple[str, ...] = (
    "#4C78A8",
    "#F58518",
    "#54A24B",
    "#E45756",
    "#72B7B2",
    "#B279A2",
    "#FF9DA6",
    "#9D755D",
    "#BAB0AC",
    "#EECA3B",
)


def color_map(countries: list[str]) -> dict[str, str]:
    """Assign each country a deterministic color.

    Countries are sorted alphabetically before assignment so the same
    dataset always produces the same country -> color mapping, run to
    run, regardless of row order. Cycles through :data:`_PALETTE` if
    there are more countries than colors.
    """
    ordered = sorted(set(countries))
    return {
        country: _PALETTE[index % len(_PALETTE)]
        for index, country in enumerate(ordered)
    }


class EmptyVisualizationInputError(ValueError):
    """Raised when a visualization has no analytical data to represent.

    Distinct from the *optional* population-normalized visualization,
    which returns ``None`` rather than raising when
    ``EDAResult.population_normalized`` is absent by design. This
    error covers the case where a required input is present but
    empty (e.g. zero country-year observations) and a chart would be
    meaningless or misleading.
    """


def empty_figure_guard(condition: bool, message: str) -> None:
    """Raise :class:`EmptyVisualizationInputError` if ``condition`` is true."""
    if condition:
        raise EmptyVisualizationInputError(message)


def apply_base_layout(figure: go.Figure, *, title: str) -> go.Figure:
    """Apply the shared minimal layout (title, template, margins).

    Purely presentational — no analytical content is touched.
    """
    figure.update_layout(
        title=title,
        template="plotly_white",
        margin={"l": 60, "r": 30, "t": 60, "b": 50},
        legend_title_text="Country",
    )
    return figure
