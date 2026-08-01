"""Public Health Surveillance & Analytics Platform.

A modular research software platform that supports public health analysts
in transforming surveillance-derived datasets into reliable, reproducible
analytical outputs.

This package follows the layered architecture locked in the project's
Freeze Document:

    Presentation Layer (Streamlit)
        -> Workflow Controller
            -> Analytical Modules
                -> Data Layer

Milestone 1 status: repository foundation only. No analytical
functionality is implemented yet. Subsequent milestones populate the
submodules below in the order defined by the frozen Implementation
Roadmap.
"""

__version__ = "0.1.0"
