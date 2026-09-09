"""Milestone 8 tests: World Bank population registry lookup (ADR-010 addendum).

Network calls are mocked throughout (matching sample_dataset.py's
testing pattern) -- live behavior was verified manually against the
real World Bank API and the real OpenDengue extract during
development, not re-verified on every test run.
"""

from __future__ import annotations

import json
from unittest.mock import patch

import pandas as pd
import pytest

from surveillance_platform.data_loading.population_lookup import (
    fetch_population_data,
    get_country_iso3_lookup,
    population_by_country_series,
)

_FAKE_REGISTRY = [
    {"id": "BGD", "name": "Bangladesh", "region": {"value": "South Asia"}},
    {"id": "LKA", "name": "Sri Lanka", "region": {"value": "South Asia"}},
    {"id": "MDV", "name": "Maldives", "region": {"value": "South Asia"}},
    {"id": "NPL", "name": "Nepal", "region": {"value": "South Asia"}},
    {"id": "1W", "name": "World", "region": {"value": "Aggregates"}},
    {"id": "8S", "name": "South Asia", "region": {"value": "Aggregates"}},
]


def _mock_urlopen_registry():
    class MockResponse:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def read(self):
            return json.dumps([{"total": len(_FAKE_REGISTRY)}, _FAKE_REGISTRY]).encode()

    return MockResponse()


# --- get_country_iso3_lookup ------------------------------------------------


def test_lookup_excludes_aggregate_entries(tmp_path):
    cache_path = tmp_path / "registry.json"
    with (
        patch(
            "surveillance_platform.data_loading.population_lookup._CACHE_PATH",
            cache_path,
        ),
        patch(
            "surveillance_platform.data_loading.population_lookup._fetch_country_registry",
            return_value=_FAKE_REGISTRY,
        ),
    ):
        lookup = get_country_iso3_lookup()
    assert "WORLD" not in lookup
    assert "SOUTH ASIA" not in lookup


def test_lookup_includes_real_countries_with_correct_iso3(tmp_path):
    cache_path = tmp_path / "registry.json"
    with (
        patch(
            "surveillance_platform.data_loading.population_lookup._CACHE_PATH",
            cache_path,
        ),
        patch(
            "surveillance_platform.data_loading.population_lookup._fetch_country_registry",
            return_value=_FAKE_REGISTRY,
        ),
    ):
        lookup = get_country_iso3_lookup()
    assert lookup["BANGLADESH"] == "BGD"
    assert lookup["SRI LANKA"] == "LKA"
    assert lookup["MALDIVES"] == "MDV"
    assert lookup["NEPAL"] == "NPL"


def test_lookup_caches_to_disk_and_does_not_refetch(tmp_path):
    cache_path = tmp_path / "registry.json"
    with (
        patch(
            "surveillance_platform.data_loading.population_lookup._CACHE_PATH",
            cache_path,
        ),
        patch(
            "surveillance_platform.data_loading.population_lookup._fetch_country_registry",
            return_value=_FAKE_REGISTRY,
        ) as mock_fetch,
    ):
        get_country_iso3_lookup()
        assert mock_fetch.call_count == 1
        get_country_iso3_lookup()  # second call: should use disk cache
        assert mock_fetch.call_count == 1
    assert cache_path.exists()


# --- fetch_population_data --------------------------------------------------


def _fake_population_payload(records: list[dict]) -> bytes:
    return json.dumps([{"total": len(records)}, records]).encode()


def _mock_indicator_response(records: list[dict]):
    class MockResponse:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def read(self):
            return _fake_population_payload(records)

    return MockResponse()


@pytest.fixture
def mocked_registry(tmp_path):
    cache_path = tmp_path / "registry.json"
    with (
        patch(
            "surveillance_platform.data_loading.population_lookup._CACHE_PATH",
            cache_path,
        ),
        patch(
            "surveillance_platform.data_loading.population_lookup._fetch_country_registry",
            return_value=_FAKE_REGISTRY,
        ),
    ):
        yield


def test_fetch_matches_all_four_real_study_countries(mocked_registry):
    fake_records = [
        {"countryiso3code": "BGD", "date": "2020", "value": 165000000},
        {"countryiso3code": "LKA", "date": "2020", "value": 21000000},
        {"countryiso3code": "MDV", "date": "2020", "value": 540000},
        {"countryiso3code": "NPL", "date": "2020", "value": 29000000},
    ]
    with patch(
        "surveillance_platform.data_loading.population_lookup.urllib.request.urlopen",
        return_value=_mock_indicator_response(fake_records),
    ):
        result = fetch_population_data(["BANGLADESH", "SRI LANKA", "MALDIVES", "NEPAL"])
    assert set(result["country"]) == {"BANGLADESH", "SRI LANKA", "MALDIVES", "NEPAL"}
    assert len(result) == 4


def test_fetch_matches_mixed_case_location_values(mocked_registry):
    fake_records = [{"countryiso3code": "BGD", "date": "2020", "value": 165000000}]
    with patch(
        "surveillance_platform.data_loading.population_lookup.urllib.request.urlopen",
        return_value=_mock_indicator_response(fake_records),
    ):
        result = fetch_population_data(["bangladesh"])
    assert len(result) == 1
    assert (
        result.iloc[0]["country"] == "bangladesh"
    )  # original casing, not "Bangladesh"


def test_fetch_preserves_original_casing_exactly(mocked_registry):
    fake_records = [{"countryiso3code": "LKA", "date": "2020", "value": 21000000}]
    with patch(
        "surveillance_platform.data_loading.population_lookup.urllib.request.urlopen",
        return_value=_mock_indicator_response(fake_records),
    ):
        result = fetch_population_data(["Sri Lanka"])
    assert result.iloc[0]["country"] == "Sri Lanka"  # not "SRI LANKA", not ISO3


def test_fetch_gracefully_omits_unmatched_locations(mocked_registry):
    fake_records = [{"countryiso3code": "BGD", "date": "2020", "value": 165000000}]
    with patch(
        "surveillance_platform.data_loading.population_lookup.urllib.request.urlopen",
        return_value=_mock_indicator_response(fake_records),
    ):
        result = fetch_population_data(["BANGLADESH", "Fakelandia"])
    assert "Fakelandia" not in result["country"].values
    assert "BANGLADESH" in result["country"].values


def test_fetch_returns_empty_frame_with_correct_columns_when_nothing_matches(
    mocked_registry,
):
    with patch(
        "surveillance_platform.data_loading.population_lookup.urllib.request.urlopen"
    ) as mock_urlopen:
        result = fetch_population_data(["Fakelandia", "Nowhereland"])
        mock_urlopen.assert_not_called()  # no point querying the API at all
    assert list(result.columns) == ["country", "year", "population"]
    assert len(result) == 0


def test_fetch_never_exposes_iso3_as_the_country_value(mocked_registry):
    fake_records = [{"countryiso3code": "BGD", "date": "2020", "value": 165000000}]
    with patch(
        "surveillance_platform.data_loading.population_lookup.urllib.request.urlopen",
        return_value=_mock_indicator_response(fake_records),
    ):
        result = fetch_population_data(["BANGLADESH"])
    assert "BGD" not in result["country"].values
    assert "BANGLADESH" in result["country"].values


# --- population_by_country_series (shape for forecast()) -------------------


def test_reshape_produces_dict_of_series_indexed_by_year():
    df = pd.DataFrame(
        {
            "country": ["A", "A", "B"],
            "year": [2019, 2020, 2020],
            "population": [100, 110, 200],
        }
    )
    result = population_by_country_series(df)
    assert set(result.keys()) == {"A", "B"}
    assert result["A"].loc[2020] == 110
    assert result["B"].loc[2020] == 200


def test_reshape_of_empty_dataframe_produces_empty_dict():
    df = pd.DataFrame(columns=["country", "year", "population"])
    result = population_by_country_series(df)
    assert result == {}


# --- integration: shape accepted by M5's analyze() and M7's forecast() -----


def test_output_shape_is_accepted_by_analyze_and_forecast(mocked_registry):
    """Confirms fetch_population_data()'s DataFrame is a valid
    population_data argument to analyze(), and that
    population_by_country_series()'s reshape is a valid
    population_by_country argument to forecast() -- using synthetic
    data to stay fast (manually verified against the real OpenDengue
    extract + live World Bank API during development).
    """
    import numpy as np

    from surveillance_platform.eda import analyze
    from surveillance_platform.forecasting import forecast
    from surveillance_platform.role_configuration import RoleConfiguration

    role_config = RoleConfiguration(
        time="time", location="country", surveillance_measure="cases", identifier=None
    )
    periods = pd.period_range("2010-01", periods=20, freq="M")
    prepared_data = pd.DataFrame(
        {
            "country": "BANGLADESH",
            "time": periods.to_timestamp(),
            "cases": np.arange(20) + 1,
        }
    )

    fake_records = [
        {"countryiso3code": "BGD", "date": str(y), "value": 160_000_000 + y}
        for y in range(2009, 2011)
    ]
    with patch(
        "surveillance_platform.data_loading.population_lookup.urllib.request.urlopen",
        return_value=_mock_indicator_response(fake_records),
    ):
        pop_data = fetch_population_data(["BANGLADESH"])

    # Must not raise -- confirms analyze() accepts this DataFrame shape.
    eda_result = analyze(prepared_data, role_config, pop_data)
    assert eda_result.population_normalized is not None

    # Must not raise -- confirms forecast() accepts this dict-of-Series shape.
    pop_by_country = population_by_country_series(pop_data)
    forecast_results = forecast(prepared_data, role_config, pop_by_country)
    assert isinstance(forecast_results, list)
