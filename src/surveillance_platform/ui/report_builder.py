"""HTML report builder (Milestone 8, ADR-010).

Streamlit-free by design (same independence philosophy as
`workflow`/`data_loading`, ADR-010): builds a complete, self-contained
HTML string, testable as plain Python. Page 7 serves the result via
`st.download_button`.

Uses Plotly's native `.to_html()` (already a dependency since M6) for
every chart -- no new dependency for report generation. Applies the
project's locked visual identity (ADR-010): IBM Plex Sans, the deep
teal/amber palette, real section structure -- not a plain data dump.

Security (ADR-010): every user-derived string (country names, case
definitions, quality-finding messages) is passed through
``html.escape()`` before being interpolated into the template. An
unescaped malicious value in an uploaded CSV could otherwise execute
in whoever's browser later opens the exported file.
"""

from __future__ import annotations

import html
from datetime import UTC, datetime

import plotly.graph_objects as go

from surveillance_platform.workflow import AnalysisSession

_CSS = """
:root {
  --teal: #1B4B4F;
  --amber: #B7791F;
  --bg: #FAFAF8;
  --card-bg: #FFFFFF;
  --border: #E0DED7;
  --text: #1A1A1A;
  --muted: #6B6B63;
}
* { box-sizing: border-box; }
body {
  font-family: 'IBM Plex Sans', -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text);
  margin: 0;
  padding: 0 0 4rem 0;
  line-height: 1.5;
}
header {
  background: var(--teal);
  color: #FFFFFF;
  padding: 2.5rem 3rem;
}
header .wordmark { font-size: 1.9rem; font-weight: 600; margin: 0; }
header .subtitle { opacity: 0.85; margin: 0.25rem 0 0 0; font-size: 0.95rem; }
header .timestamp { opacity: 0.7; margin-top: 1rem; font-size: 0.85rem; }
main { max-width: 960px; margin: 0 auto; padding: 0 2rem; }
section {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1.75rem 2rem;
  margin-top: 2rem;
}
section h2 {
  margin-top: 0;
  font-size: 1.3rem;
  font-weight: 600;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.75rem;
}
.metric-row { display: flex; gap: 2rem; flex-wrap: wrap; margin: 1rem 0; }
.metric { min-width: 120px; }
.metric .value { font-size: 1.6rem; font-weight: 600; color: var(--teal); }
.metric .label { font-size: 0.85rem; color: var(--muted); }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
th, td {
  text-align: left;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid var(--border);
  font-size: 0.9rem;
}
th { color: var(--muted); font-weight: 600; }
.warning-banner {
  background: #FBF0DD;
  border-left: 4px solid var(--amber);
  padding: 0.75rem 1rem;
  margin: 0.75rem 0;
  font-size: 0.9rem;
}
.caption { color: var(--muted); font-size: 0.85rem; }
footer {
  max-width: 960px;
  margin: 2rem auto 0 auto;
  padding: 0 2rem;
  color: var(--muted);
  font-size: 0.8rem;
}
"""

_FONT_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:'
    'wght@400;500;600;700&display=swap" rel="stylesheet">'
)

#: Loaded once in <head>; every chart fragment below uses
#: include_plotlyjs=False and relies on this shared copy, rather than
#: re-downloading the ~3MB Plotly library once per chart.
_PLOTLY_CDN_SCRIPT = (
    '<script charset="utf-8" src="https://cdn.plot.ly/plotly-3.7.0.min.js" '
    'integrity="sha256-jvTGqxNp8AGWEcvNLVuKr+8j5dGe9Yw51LQkmDH+IYA=" '
    'crossorigin="anonymous"></script>'
)


def _esc(value: object) -> str:
    """Escape any user-derived value before it enters the HTML template."""
    return html.escape(str(value))


def _metric(label: str, value: str) -> str:
    return f'<div class="metric"><div class="value">{_esc(value)}</div><div class="label">{_esc(label)}</div></div>'


def _preparation_section(session: AnalysisSession) -> str:
    report = session.results["preparation"].report
    findings_rows = "".join(
        f"<tr><td>{_esc(f.check)}</td><td>{_esc(f.severity)}</td><td>{_esc(f.message)}</td></tr>"
        for f in report.quality_findings
    )
    findings_table = (
        f"<table><tr><th>Check</th><th>Severity</th><th>Message</th></tr>{findings_rows}</table>"
        if report.quality_findings
        else '<p class="caption">No quality issues found.</p>'
    )
    return f"""
    <section>
      <h2>Data Preparation</h2>
      <div class="metric-row">
        {_metric("Rows in", f"{report.rows_in:,}")}
        {_metric("Rows out", f"{report.rows_out:,}")}
        {_metric("Rows excluded", f"{report.rows_excluded:,}")}
      </div>
      {findings_table}
    </section>
    """


def _eda_section(session: AnalysisSession) -> str:
    eda = session.results.get("eda")
    if eda is None:
        return ""
    d = eda.descriptive
    country_rows = "".join(
        f"<tr><td>{_esc(c.country)}</td><td>{c.observation_count:,}</td>"
        f"<td>{c.descriptive.mean:.1f}</td><td>{c.descriptive.maximum:.0f}</td></tr>"
        for c in eda.country_comparison.countries
    )
    return f"""
    <section>
      <h2>Exploratory Analysis</h2>
      <div class="metric-row">
        {_metric("Mean", f"{d.mean:.1f}")}
        {_metric("Median", f"{d.median:.1f}")}
        {_metric("Max", f"{d.maximum:.0f}")}
        {_metric("Std dev", f"{d.std:.1f}")}
      </div>
      <table>
        <tr><th>Country</th><th>Observations</th><th>Mean</th><th>Max</th></tr>
        {country_rows}
      </table>
    </section>
    """


def _visualization_section(session: AnalysisSession) -> str:
    viz = session.results.get("visualization")
    if viz is None:
        return ""
    figures = [
        ("Annual surveillance trend", viz.annual_trend),
        ("Annual distribution by country", viz.annual_distribution_by_country),
        ("Surveillance measure distribution", viz.surveillance_measure_distribution),
    ]
    if viz.population_normalized_distribution is not None:
        figures.append(
            (
                "Population-normalized distribution",
                viz.population_normalized_distribution,
            )
        )
    if viz.surveillance_profile is not None:
        figures.append(("Surveillance resolution profile", viz.surveillance_profile))

    charts_html = "".join(
        f'<h3 style="font-size:1rem;margin-top:1.5rem;">{_esc(title)}</h3>'
        f"{fig.to_html(include_plotlyjs=False, full_html=False)}"
        for title, fig in figures
    )
    return f"<section><h2>Visualization</h2>{charts_html}</section>"


def _forecast_chart(result) -> go.Figure:
    """Rebuild a Plotly forecast chart for export -- Page 6's on-screen
    chart uses Streamlit's native line_chart, which can't be embedded
    in a standalone HTML file.
    """
    periods = [str(p) for p in result.forecast_periods]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=periods, y=result.forecast_upper, line={"width": 0}, showlegend=False
        )
    )
    fig.add_trace(
        go.Scatter(
            x=periods,
            y=result.forecast_lower,
            fill="tonexty",
            fillcolor="rgba(27,75,79,0.15)",
            line={"width": 0},
            name="95% interval",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=periods,
            y=result.forecast_mean,
            mode="lines+markers",
            line={"color": "#1B4B4F", "width": 2},
            name="Forecast",
        )
    )
    fig.update_layout(
        template="plotly_white",
        margin={"t": 10, "b": 10, "l": 10, "r": 10},
        height=320,
    )
    return fig


def _forecasting_section(session: AnalysisSession) -> str:
    forecast_by_track = session.results.get("forecast_by_track", {})
    if not forecast_by_track:
        return ""
    blocks = []
    for (country, case_definition), result in forecast_by_track.items():
        label = f"{_esc(country)} — {_esc(case_definition) if case_definition else '(constant)'}"
        warnings_html = "".join(
            f'<div class="warning-banner">{_esc(m)}</div>' for m in result.limitations
        )
        if result.forecast_mean:
            chart_html = _forecast_chart(result).to_html(
                include_plotlyjs=False, full_html=False
            )
            metrics_html = ""
            if result.model_metrics is not None and result.baseline_metrics is not None:
                metrics_html = f"""
                <div class="metric-row">
                  {_metric("SARIMA MAE", f"{result.model_metrics.mae:.2f}")}
                  {_metric("SARIMA RMSE", f"{result.model_metrics.rmse:.2f}")}
                  {_metric("Baseline MAE", f"{result.baseline_metrics.mae:.2f}")}
                  {_metric("Baseline RMSE", f"{result.baseline_metrics.rmse:.2f}")}
                </div>
                """
        else:
            chart_html, metrics_html = "", ""
        blocks.append(
            f'<h3 style="font-size:1.05rem;">{label}</h3>{warnings_html}{metrics_html}{chart_html}'
        )
    return f"<section><h2>Forecasting</h2>{''.join(blocks)}</section>"


def build_report_html(session: AnalysisSession) -> str:
    """Assemble the complete, self-contained HTML report for one session.

    Only includes sections for stages the session has actually
    completed -- an empty session produces a minimal (but valid)
    report, not an error.
    """
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    sections = []
    if "preparation" in session.results:
        sections.append(_preparation_section(session))
    sections.append(_eda_section(session))
    sections.append(_visualization_section(session))
    sections.append(_forecasting_section(session))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Epicurve Report</title>
{_FONT_LINK}
{_PLOTLY_CDN_SCRIPT}
<style>{_CSS}</style>
</head>
<body>
<header>
  <p class="wordmark">Epicurve</p>
  <p class="subtitle">Public Health Surveillance &amp; Analytics Platform</p>
  <p class="timestamp">Generated {generated_at}</p>
</header>
<main>
{''.join(sections)}
</main>
<footer>
  Forecasts are illustrative and evaluative, not operational
  predictions (see docs/adr/ADR-009-forecasting-strategy.md). Reported
  case counts reflect surveillance data, not true disease burden.
</footer>
</body>
</html>"""
