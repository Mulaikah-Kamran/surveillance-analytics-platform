"""Milestone 8 tests: HTML report builder (ADR-010).

Zero Streamlit imports -- plain pytest, per ADR-010's independence
requirement (report_builder.py is Streamlit-free by design).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from surveillance_platform import workflow
from surveillance_platform.forecasting import detect_tracks
from surveillance_platform.role_configuration import RoleConfiguration
from surveillance_platform.ui.report_builder import _esc, build_report_html

ROLE_CONFIG = RoleConfiguration(
    time="time", location="country", surveillance_measure="cases", identifier=None
)


def _prepared_session() -> workflow.AnalysisSession:
    periods = pd.period_range("2020-01", periods=12, freq="M")
    data = pd.DataFrame(
        {
            "country": "Testland",
            "time": periods.to_timestamp(),
            "cases": np.arange(12) + 1,
        }
    )
    role_config = RoleConfiguration(
        time="time", location="country", surveillance_measure="cases", identifier=None
    )
    session = workflow.create_session()
    session = workflow.set_dataset(session, data)
    session = workflow.configure_roles(session, role_config)
    session = workflow.run_preparation(session)
    return session


# --- security: XSS escaping -------------------------------------------------


def test_esc_escapes_script_tags():
    malicious = "<script>alert('xss')</script>"
    escaped = _esc(malicious)
    assert "<script>" not in escaped
    assert "&lt;script&gt;" in escaped


def test_build_report_html_escapes_malicious_country_names():
    """A country name containing a script tag must never appear
    unescaped in the generated report -- real risk, not theoretical
    (ADR-010's Security section).
    """
    periods = pd.period_range("2020-01", periods=12, freq="M")
    data = pd.DataFrame(
        {
            "country": "<script>alert(1)</script>",
            "time": periods.to_timestamp(),
            "cases": np.arange(12) + 1,
        }
    )
    session = workflow.create_session()
    session = workflow.set_dataset(session, data)
    session = workflow.configure_roles(session, ROLE_CONFIG)
    session = workflow.run_preparation(session)
    session = workflow.run_eda(session)

    report = build_report_html(session)
    assert "<script>alert(1)</script>" not in report
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in report


# --- section presence reflects actual session state -------------------------


def test_report_includes_only_completed_stages():
    session = _prepared_session()  # preparation only, no EDA/viz/forecast
    report = build_report_html(session)
    assert "Data Preparation" in report
    assert "Exploratory Analysis" not in report
    assert "Visualization" not in report
    assert "Forecasting" not in report


def test_report_includes_eda_section_once_present():
    session = _prepared_session()
    session = workflow.run_eda(session)
    report = build_report_html(session)
    assert "Exploratory Analysis" in report


def test_report_includes_forecasting_section_with_limitations():
    session = _prepared_session()
    [track] = detect_tracks(session.results["preparation"].data, ROLE_CONFIG)
    session = workflow.run_forecast_for_track(session, track, population_by_year=None)
    report = build_report_html(session)
    assert "Forecasting" in report
    assert "No population data available" in report


# --- Plotly embedding correctness --------------------------------------------


def test_report_loads_plotly_library_exactly_once():
    session = _prepared_session()
    session = workflow.run_eda(session)
    session = workflow.run_visualization(session)
    report = build_report_html(session)
    assert report.count("cdn.plot.ly") == 1


def test_report_is_well_formed_html():
    session = _prepared_session()
    report = build_report_html(session)
    assert report.startswith("<!DOCTYPE html>")
    assert report.rstrip().endswith("</html>")
    assert "Epicurve" in report


# --- section navigation ------------------------------------------------


def test_nav_only_links_to_sections_actually_present():
    session = _prepared_session()  # preparation only
    report = build_report_html(session)
    assert '<a href="#preparation">' in report
    assert '<a href="#eda">' not in report
    assert '<a href="#visualization">' not in report
    assert '<a href="#forecasting">' not in report


def test_nav_links_match_section_ids_present():
    session = _prepared_session()
    session = workflow.run_eda(session)
    report = build_report_html(session)
    assert '<a href="#preparation">' in report
    assert '<a href="#eda">' in report
    assert 'id="preparation"' in report
    assert 'id="eda"' in report


def test_report_includes_viewport_meta_for_mobile():
    session = _prepared_session()
    report = build_report_html(session)
    assert 'name="viewport"' in report
    assert "width=device-width" in report
