# ADR-011: Picking a second dataset to test the pipeline on

**Status:** Locked

## The decision

The validation dataset is **CDC's National Notifiable Diseases Surveillance System (NNDSS)** weekly data, 2022 to 2026, pulled straight from CDC's own public API.

## Why this took a few tries

The goal was a second, genuinely different surveillance dataset (different disease, different country, different structure) to check whether the pipeline actually generalizes, or whether it secretly only works on the original dengue dataset.

Three other sources looked promising on paper and didn't pan out:

- **Project Tycho**, a historical US disease archive, had real weekly case counts, but its registration system failed to load across seven different attempts, from different networks, different countries, even a clean sandboxed browser with no connection issues at all. Something was genuinely broken on their end.
- **A global outbreak dataset from the Humanitarian Data Exchange** turned out not to track case counts at all, just whether an outbreak happened in a given country and year. No usable numbers to analyze.
- **WHO's Global Health Observatory** is reliable and easy to access, but its disease data is annual only, too coarse for the kind of week-by-week analysis this project needs.

CDC's NNDSS data was the only one that had both: real weekly case numbers, and a website that actually works, no login required.

## The catch, and why it's fine

CDC's own data only goes back cleanly to 2022 in this format, which is shorter than the 6 years of history the forecasting model needs to trust its own predictions. So forecasting correctly reports "not enough data yet" for this dataset, exactly the way it's supposed to when data is too short. Every other part of the pipeline (loading, cleaning, analysis, charts) works on it end to end, with zero changes to the actual code, just a small script to pull and reshape CDC's data into the same format the app already expects.
