# ADR-003: The order things happen in

**Status:** Locked

## The decision

Every dataset that goes through this pipeline follows the same fixed order:

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

If validation fails at the start, everything stops right there. The session gets marked as failed, the reason gets saved, and nothing downstream runs. No partial results, no silent guesswork.
