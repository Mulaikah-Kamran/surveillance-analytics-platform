# Testing the pipeline on a second dataset

The whole point of this stage was to answer a simple question: does this pipeline actually work on data it wasn't built for, or does it secretly only work on the original dengue dataset?

The short answer: yes, it holds up.

## What got tested

CDC's public weekly disease surveillance data (see [ADR-011](adr/ADR-011-m9-validation-dataset-selection.md) for why this dataset specifically). Completely different disease, different country, different data quirks. One small script pulls and reshapes the raw CDC data into the same format the app already expects. Nothing in the actual pipeline code changed at all.

## What happened, step by step

- **Loading and cleaning**: pulled 12,444 rows, and the existing cleaning logic caught 3,037 rows with missing case counts and dropped them automatically, using the exact same rule that already exists for the dengue dataset. No special handling needed.
- **Analysis**: produced real, sensible statistics (an average of about 323 cases per week, with genuine variation state to state). Nothing degenerate or broken.
- **Charts**: rendered correctly, with the optional charts that need extra data (like population rates) correctly skipped since this dataset doesn't have that.
- **Forecasting**: detected 63 separate location tracks and correctly marked every single one as not having enough history yet, since CDC's version of this dataset only goes back to 2022. That's a real limitation of this specific dataset, not a bug, and the pipeline recognized it and said so instead of producing an unreliable forecast anyway.

## The takeaway

A brand new, structurally different real-world dataset went through the entire pipeline (loading, cleaning, analysis, charts, forecasting) without a single change to the actual analysis code. Only the small acquisition script needed writing. That's a good sign the architecture is built the right way, not just tuned to one dataset.
