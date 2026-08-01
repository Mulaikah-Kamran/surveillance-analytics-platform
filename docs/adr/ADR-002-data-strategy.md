# ADR-002 — Data Strategy

**Status:** Locked

## Decision

Use the OpenDengue data resource, specifically the National Extract, as
the foundation for Version 1. The study dataset consists of 3–5 South
Asian countries, finalized after objective evaluation of data
completeness and suitability.

## Alternatives Considered

OpenDengue Temporal Extract.

## Context

The project aims to build a reproducible analytical workflow for
surveillance-derived datasets that supports public health analysts
through validation, profiling, quality assessment, standardization,
cleaning, descriptive analysis, visualization, and forecasting.

## Rationale

The National Extract aligns more closely with the intended analytical
workflow by providing a consistent country-level view suitable for
longitudinal analysis and forecasting. Although the Temporal Extract
offers finer spatial resolution, its predominance of Admin2-level
records (~93% of rows) introduces additional complexity outside the
scope of Version 1 and does not improve the platform's ability to
answer the project's engineering research question.

## Consequences

- **Positive:** Better alignment with project objectives; simpler and
  more reproducible analytical workflow; strong foundation for
  forecasting; clearer repository narrative.
- **Negative:** No district-level spatial analysis in Version 1; some
  geographic detail is intentionally deferred.

## Scope Note

The choice of the National Extract should not be interpreted as a
claim that it is universally superior to the Temporal Extract. It is
the most appropriate choice for the objectives and scope of Version 1
of this project.
