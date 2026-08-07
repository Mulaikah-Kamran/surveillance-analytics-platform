"""Milestone 3 tests: Role Configuration.

Exercises the RoleConfiguration contract established in Milestone 3
(see ADR-004 and the Milestone 3 decision audit): explicit
user-assigned roles, structural validation, and dataset-compatibility
validation against a plain iterable of column names. Uses small,
deterministic synthetic column lists — no real OpenDengue data is
required.
"""

import pytest

from surveillance_platform.role_configuration import (
    RoleConfiguration,
    RoleConfigurationError,
    validate,
)

SYNTHETIC_COLUMNS = ["date", "country", "cases", "record_id", "notes"]


def _valid_config(**overrides):
    fields = {
        "time": "date",
        "location": "country",
        "surveillance_measure": "cases",
        "identifier": None,
    }
    fields.update(overrides)
    return RoleConfiguration(**fields)


def test_valid_configuration_passes():
    """A complete, valid mapping validates without raising."""
    config = _valid_config()
    assert validate(config, SYNTHETIC_COLUMNS) is None


@pytest.mark.parametrize("missing_field", ["time", "location", "surveillance_measure"])
def test_missing_required_role_fails(missing_field):
    """Each required role, if empty, is rejected."""
    config = _valid_config(**{missing_field: ""})
    with pytest.raises(RoleConfigurationError) as excinfo:
        validate(config, SYNTHETIC_COLUMNS)
    assert missing_field in str(excinfo.value)


def test_unknown_column_fails():
    """A role referencing a column absent from available_columns fails."""
    config = _valid_config(location="not_a_real_column")
    with pytest.raises(RoleConfigurationError) as excinfo:
        validate(config, SYNTHETIC_COLUMNS)
    assert "not_a_real_column" in str(excinfo.value)


def test_duplicate_column_mapping_fails():
    """Two roles assigned to the same column are rejected."""
    config = _valid_config(location="date")  # same column as time
    with pytest.raises(RoleConfigurationError) as excinfo:
        validate(config, SYNTHETIC_COLUMNS)
    assert "date" in str(excinfo.value)


def test_optional_identifier_absent_is_valid():
    """identifier=None is a valid configuration."""
    config = _valid_config(identifier=None)
    assert validate(config, SYNTHETIC_COLUMNS) is None


def test_optional_identifier_supplied_is_valid():
    """A valid Identifier assignment succeeds."""
    config = _valid_config(identifier="record_id")
    assert validate(config, SYNTHETIC_COLUMNS) is None


def test_invalid_identifier_unknown_column_fails():
    """An Identifier referencing an unknown column fails."""
    config = _valid_config(identifier="not_a_real_column")
    with pytest.raises(RoleConfigurationError) as excinfo:
        validate(config, SYNTHETIC_COLUMNS)
    assert "identifier" in str(excinfo.value)


def test_identifier_duplicating_another_role_fails():
    """An Identifier assigned to the same column as another role fails."""
    config = _valid_config(identifier="cases")  # same as surveillance_measure
    with pytest.raises(RoleConfigurationError) as excinfo:
        validate(config, SYNTHETIC_COLUMNS)
    assert "cases" in str(excinfo.value)


def test_malformed_role_value_fails():
    """A non-string role value is rejected clearly."""
    config = _valid_config(time=123)
    with pytest.raises(RoleConfigurationError) as excinfo:
        validate(config, SYNTHETIC_COLUMNS)
    assert "time" in str(excinfo.value)


def test_multiple_violations_are_all_reported():
    """Several simultaneous problems are all surfaced, not just the first."""
    config = RoleConfiguration(
        time="",  # missing
        location="date",
        surveillance_measure="date",  # duplicate with location
        identifier="not_a_real_column",  # unknown column
    )
    with pytest.raises(RoleConfigurationError) as excinfo:
        validate(config, SYNTHETIC_COLUMNS)

    error = excinfo.value
    assert len(error.violations) >= 3
    message = str(error)
    assert "time" in message
    assert "date" in message
    assert "not_a_real_column" in message
