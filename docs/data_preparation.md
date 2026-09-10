# Data preparation

**Code:** `src/surveillance_platform/data_preparation/`

Turns a raw, messy dataset into something ready for analysis. Five steps, always in this order:

```
Validation -> Profiling -> Quality check -> Date fixing -> Cleaning
```

Only the last step, cleaning, is allowed to actually change or remove data. Everything before it just checks and reports.

## What gets cleaned, and what doesn't

Cleaning is deliberately narrow. It fixes inconsistent capitalization in one known column, and it drops rows that are missing something essential (a date, a location, a case count), always recording exactly why a row was dropped. It never guesses a missing value or invents one.

If something looks off but there's no defined fix for it (like a report's end date coming before its start date), it gets flagged and left alone rather than "corrected" in a way nobody asked for.

## How to use it

```python
from surveillance_platform.data_preparation import prepare

result = prepare(raw_data, role_config)
result.data     # the cleaned dataset
result.report   # what happened: rows in, rows out, why anything got dropped
```

Running it twice on the same input always gives the same result, and it never modifies the data you pass in.
