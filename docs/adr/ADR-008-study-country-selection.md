# ADR-008: Which countries made the cut

**Status:** Locked

## The decision

The study dataset covers four countries: **Sri Lanka, Bangladesh, Maldives, and Nepal.**

Afghanistan, Bhutan, India, and Pakistan were also considered and dropped.

## Why these four

Out of eight South Asian countries with dengue data available, these four had the longest, most consistent, sub-annual (weekly or monthly) reporting history. That combination matters most for later analysis, especially forecasting, which needs regular, frequent data points to find seasonal patterns.

The other four fell short in different ways:

- **India** has 35 years of clean data, but almost all of it is reported once a year. That's too coarse for trend and seasonality work, even though the data quality itself is excellent.
- **Pakistan** mixes three different case definitions over time and has a six year reporting gap.
- **Bhutan** reports mostly annually too, with the highest share of zero-case entries of any candidate.
- **Afghanistan** only has five years of history on record, too short to work with.

## What this means going forward

Every stage after this point (cleaning, exploratory analysis, forecasting) works with these four countries.

India is worth a second look someday. It's the largest country by dengue burden in the region, and it only got excluded because of its reporting frequency, not because the data is bad. If a future version of this project finds a good way to handle mostly-annual data, India could be added without changing the reasoning here, just the outcome for that one country.
