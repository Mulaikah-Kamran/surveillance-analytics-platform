# Exploratory analysis

**Code:** `src/surveillance_platform/eda/`

Takes the cleaned dataset and actually looks at it: basic stats, how much data is missing, trends over time, and how countries compare to each other. It doesn't change anything, just describes what's there.

## Two things worth knowing

**Reported cases, not true disease numbers.** Every statistic here describes what got reported, not the real number of infections out there. Surveillance data always undercounts reality to some degree, and this project is careful never to blur that line.

**Data quality quirks get flagged, not fixed.** If a country reports its data with mixed formats in the same year (for example, weekly reports for part of the year, monthly for the rest), that gets marked, but the underlying numbers stay as-is. On the real dataset, this actually caught something real: Bangladesh reported dengue cases under one case definition for most of 2021, then switched to a broader one for the last few months. That kind of thing matters for anyone doing careful analysis, so it gets surfaced rather than smoothed over.

## Optional: rates instead of raw counts

If population numbers are available, case counts get converted into a rate per 100,000 people, which makes it possible to fairly compare countries of very different sizes. Population figures come from the World Bank. If population data isn't available for a given dataset, this step is just skipped, nothing breaks.

## How to use it

```python
from surveillance_platform.eda import analyze

result = analyze(prepared_data, role_config, population_data=None)
```
