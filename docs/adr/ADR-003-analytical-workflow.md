# ADR-003 — Analytical Workflow

**Status:** Locked

## Decision

The analytical workflow is intentionally ordered as follows:

```
Validation
    ↓
Data Profiling
    ↓
Quality Assessment
    ↓
Temporal Standardization
    ↓
Cleaning
    ↓
Exploratory Analysis
    ↓
Visualization
    ↓
Forecasting
    ↓
Reporting
```

If validation fails, execution stops, the Analysis Session is marked
Failed, diagnostic information is preserved, and control returns to the
user interface. Downstream analytical modules are not executed.
