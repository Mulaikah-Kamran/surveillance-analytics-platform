# ADR-004 — Minimal Analytical Role Model

**Status:** Locked

## Decision

Required Analytical Roles: Time, Location, Surveillance Measure.
Optional Analytical Role: Identifier. Generic handling of all
additional variables. Users explicitly assign the required roles
before analysis begins. The platform validates that selected columns
satisfy expected structural characteristics but does not assign roles
automatically.

## Rationale

Version 1 evaluates the portability of the analytical workflow and
software architecture across surveillance-derived datasets — not the
ability to infer semantic meaning from arbitrary schemas. Automatic
role inference would introduce a separate methodological component
requiring independent evaluation and would broaden the project's
claims beyond its intended scope.

## Optional UI Guidance

The interface may visually highlight columns whose names or data types
are commonly associated with a required role, as a convenience. These
highlights never assign roles, never pre-select roles, and always
require explicit user confirmation.

## Explicit Boundary

Version 1 performs role validation, not semantic role inference.
Automatic semantic role inference is explicitly outside the scope of
this project.
