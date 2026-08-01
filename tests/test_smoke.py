"""Milestone 1 smoke test.

This is not an analytical test — Milestone 1 introduces no analytical
functionality. Its only purpose is to satisfy the Freeze Document's
v0.1.0 Definition of Done, criterion 5: "Testing framework works
(pytest runs, at least one trivial test passes, results reproducible)."

It confirms that the package is installed correctly and importable via
the src/ layout, with no path hacks and no broken imports.
"""

import surveillance_platform


def test_package_is_importable():
    """The top-level package should import cleanly via the src/ layout."""
    assert surveillance_platform is not None


def test_package_has_version():
    """The package should expose a version string."""
    assert isinstance(surveillance_platform.__version__, str)
    assert surveillance_platform.__version__ != ""


def test_submodules_are_importable():
    """Every placeholder analytical submodule should import without error."""
    import surveillance_platform.data_loading
    import surveillance_platform.data_preparation
    import surveillance_platform.eda
    import surveillance_platform.forecasting
    import surveillance_platform.role_configuration
    import surveillance_platform.ui
    import surveillance_platform.visualization
    import surveillance_platform.workflow

    assert surveillance_platform.data_loading is not None
    assert surveillance_platform.role_configuration is not None
    assert surveillance_platform.data_preparation is not None
    assert surveillance_platform.eda is not None
    assert surveillance_platform.visualization is not None
    assert surveillance_platform.forecasting is not None
    assert surveillance_platform.workflow is not None
    assert surveillance_platform.ui is not None
