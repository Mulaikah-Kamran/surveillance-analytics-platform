# Changelog

## [Unreleased]

### Data acquisition
Picked and documented the OpenDengue dataset and the four study countries (Sri Lanka, Bangladesh, Maldives, Nepal), based on which had the longest, most consistent reporting history.

### Data cleaning and role setup
Built the system for mapping arbitrary dataset columns to their meaning (date, location, case count), plus a cleaning pipeline that fixes what it safely can and clearly reports what it can't.

### Exploration and charts
Descriptive statistics, country comparisons, and five chart types, all built on Plotly.

### Forecasting
A SARIMA model forecasting three months ahead, checked honestly against a simple baseline. It beats the baseline for Sri Lanka and Maldives, and loses to it for Bangladesh, and both results are reported plainly.

### The app itself
A full Streamlit app (Epicurve) covering the whole pipeline: upload, configure, clean, explore, visualize, forecast, and export a report. Built so the interface layer never touches the actual analysis logic, meaning the whole pipeline still works from a plain script with the interface deleted.

Along the way: added a live progress display for the slow forecasting step, a section-navigable and mobile-friendly HTML report, and clearer labeling so forecasts are never mistaken for predictions about "today," since each one is really about the months right after a location's own last available data.

### Testing on a second dataset
Ran the entire pipeline against a completely different, real dataset (CDC disease surveillance data) with zero changes to the actual analysis code, only a small script to fetch and reshape the new data. Everything worked, including the pipeline correctly recognizing when that dataset didn't have enough history to forecast reliably.

## [0.1.0]: Project foundation

Initial repository setup: structure, environment, dependencies, and CI.
