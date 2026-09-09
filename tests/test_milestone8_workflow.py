"""Milestone 8 tests: workflow controller and AnalysisSession (ADR-010).

Zero Streamlit imports -- plain pytest, per ADR-010's independence
requirement. Synthetic data throughout, sized to avoid triggering a
full SARIMA backtest (M7's own tests established this pattern) so
this suite stays fast.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from surveillance_platform.forecasting import detect_tracks
from surveillance_platform.role_configuration import RoleConfiguration
from surveillance_platform.workflow import (
    configure_roles,
    create_session,
    run_eda,
    run_forecast_for_track,
    run_forecasting,
    run_preparation,
    run_visualization,
    set_dataset,
)

ROLE_CONFIG = RoleConfiguration(
    time="calendar_start_date",
    location="adm_0_name",
    surveillance_measure="dengue_total",
    identifier=None,
)


def _valid_dataset(n_months: int = 20) -> pd.DataFrame:
    """A small, structurally valid dataset -- short enough that any
    forecasting track detected from it is ineligible, so
    run_forecasting stays fast (no real SARIMA backtest triggered).
    """
    periods = pd.period_range("2010-01", periods=n_months, freq="M")
    return pd.DataFrame(
        {
            "adm_0_name": "Testland",
            "calendar_start_date": periods.to_timestamp(),
            "calendar_end_date": (periods + 1).to_timestamp() - pd.Timedelta(days=1),
            "dengue_total": np.arange(n_months) + 1,
        }
    )


# --- session lifecycle ---------------------------------------------------


def test_create_session_starts_as_created():
    session = create_session()
    assert session.status == "Created"
    assert session.dataset is None
    assert session.results == {}


def test_set_dataset_stores_it_and_stays_created():
    session = create_session()
    data = _valid_dataset()
    updated = set_dataset(session, data)
    assert updated.status == "Created"
    assert updated.dataset is data


def test_set_dataset_does_not_mutate_original_session():
    session = create_session()
    updated = set_dataset(session, _valid_dataset())
    assert session.dataset is None  # original untouched
    assert updated.dataset is not None  # new session actually has it


def test_configure_roles_requires_dataset_first():
    session = create_session()
    with pytest.raises(ValueError, match="requires a dataset"):
        configure_roles(session, ROLE_CONFIG)


def test_configure_roles_succeeds_with_valid_config():
    session = set_dataset(create_session(), _valid_dataset())
    updated = configure_roles(session, ROLE_CONFIG)
    assert updated.status == "Configured"
    assert updated.role_config == ROLE_CONFIG


def test_configure_roles_fails_with_invalid_config():
    session = set_dataset(create_session(), _valid_dataset())
    bad_config = RoleConfiguration(
        time="nonexistent_column",
        location="adm_0_name",
        surveillance_measure="dengue_total",
        identifier=None,
    )
    updated = configure_roles(session, bad_config)
    assert updated.status == "Failed"
    assert len(updated.error_messages) > 0


def test_run_preparation_requires_configured_status():
    session = set_dataset(create_session(), _valid_dataset())  # still "Created"
    with pytest.raises(ValueError, match="requires status 'Configured'"):
        run_preparation(session)


def test_run_preparation_succeeds_and_advances_to_running():
    session = configure_roles(
        set_dataset(create_session(), _valid_dataset()), ROLE_CONFIG
    )
    updated = run_preparation(session)
    assert updated.status == "Running"
    assert "preparation" in updated.results


def test_run_preparation_fails_on_structurally_invalid_data():
    empty_data = _valid_dataset(n_months=0)
    session = configure_roles(set_dataset(create_session(), empty_data), ROLE_CONFIG)
    updated = run_preparation(session)
    assert updated.status == "Failed"
    assert len(updated.error_messages) > 0


def test_run_eda_requires_completed_preparation():
    session = configure_roles(
        set_dataset(create_session(), _valid_dataset()), ROLE_CONFIG
    )
    with pytest.raises(ValueError, match="requires a completed preparation stage"):
        run_eda(session)


def test_run_eda_succeeds_after_preparation():
    session = run_preparation(
        configure_roles(set_dataset(create_session(), _valid_dataset()), ROLE_CONFIG)
    )
    updated = run_eda(session)
    assert updated.status == "Running"
    assert "eda" in updated.results


def test_run_visualization_requires_completed_eda():
    session = run_preparation(
        configure_roles(set_dataset(create_session(), _valid_dataset()), ROLE_CONFIG)
    )
    with pytest.raises(ValueError, match="requires a completed eda stage"):
        run_visualization(session)


def test_run_visualization_succeeds_after_eda():
    session = run_eda(
        run_preparation(
            configure_roles(
                set_dataset(create_session(), _valid_dataset()), ROLE_CONFIG
            )
        )
    )
    updated = run_visualization(session)
    assert updated.status == "Running"
    assert "visualization" in updated.results


def test_run_forecasting_requires_completed_preparation():
    session = create_session()
    with pytest.raises(ValueError, match="requires a completed preparation stage"):
        run_forecasting(session, {})


def test_run_forecasting_succeeds_and_reaches_completed():
    # A short dataset -> any detected track is ineligible -> no real
    # SARIMA backtest is triggered, keeping this test fast.
    session = run_preparation(
        configure_roles(set_dataset(create_session(), _valid_dataset()), ROLE_CONFIG)
    )
    updated = run_forecasting(session, population_by_country={})
    assert updated.status == "Completed"
    assert "forecast" in updated.results
    assert isinstance(updated.results["forecast"], list)


def test_controller_functions_never_mutate_input_session():
    session = create_session()
    s1 = set_dataset(session, _valid_dataset())
    s2 = configure_roles(s1, ROLE_CONFIG)
    s3 = run_preparation(s2)
    # Every earlier snapshot must remain exactly as it was.
    assert session.status == "Created" and session.dataset is None
    assert s1.status == "Created" and s1.role_config is None
    assert s2.status == "Configured" and "preparation" not in s2.results
    assert s3.status == "Running"


# --- run_forecast_for_track (ADR-010) ---------------------------------------


def test_run_forecast_for_track_requires_completed_preparation():
    session = create_session()
    with pytest.raises(ValueError, match="requires a completed preparation stage"):
        run_forecast_for_track(session, track=None, population_by_year=None)


def test_run_forecast_for_track_stores_result_keyed_by_country_and_case_definition():
    session = run_preparation(
        configure_roles(set_dataset(create_session(), _valid_dataset()), ROLE_CONFIG)
    )
    [track] = detect_tracks(session.results["preparation"].data, ROLE_CONFIG)
    updated = run_forecast_for_track(session, track, population_by_year=None)
    assert updated.status == "Completed"
    key = (track.country, track.case_definition)
    assert key in updated.results["forecast_by_track"]


def test_run_forecast_for_track_passes_through_progress_callbacks():
    session = run_preparation(
        configure_roles(set_dataset(create_session(), _valid_dataset()), ROLE_CONFIG)
    )
    [track] = detect_tracks(session.results["preparation"].data, ROLE_CONFIG)
    # population_by_year=None short-circuits before SARIMA fitting even
    # starts (existing, already-tested M7 behavior) -- a real
    # population series is needed to actually reach select_sarima_order().
    population = pd.Series({y: 1_000_000 for y in range(2010, 2012)})
    candidates_seen = []
    run_forecast_for_track(
        session,
        track,
        population_by_year=population,
        on_candidate=lambda *a: candidates_seen.append(a),
    )
    assert len(candidates_seen) == 36  # 3x3x2x2 grid, regardless of eligibility


def test_run_forecast_for_track_accumulates_multiple_tracks_without_overwriting():
    """Calling this twice for two different tracks must keep both
    results in forecast_by_track, not overwrite the first.
    """
    data_a = _valid_dataset()
    data_b = _valid_dataset()
    data_b["adm_0_name"] = "Otherland"
    combined = pd.concat([data_a, data_b], ignore_index=True)

    session = run_preparation(
        configure_roles(set_dataset(create_session(), combined), ROLE_CONFIG)
    )
    tracks = detect_tracks(session.results["preparation"].data, ROLE_CONFIG)
    assert len(tracks) == 2

    session = run_forecast_for_track(session, tracks[0], population_by_year=None)
    session = run_forecast_for_track(session, tracks[1], population_by_year=None)
    assert len(session.results["forecast_by_track"]) == 2


def test_run_forecast_for_track_does_not_mutate_input_session():
    session = run_preparation(
        configure_roles(set_dataset(create_session(), _valid_dataset()), ROLE_CONFIG)
    )
    [track] = detect_tracks(session.results["preparation"].data, ROLE_CONFIG)
    run_forecast_for_track(session, track, population_by_year=None)
    assert "forecast_by_track" not in session.results
