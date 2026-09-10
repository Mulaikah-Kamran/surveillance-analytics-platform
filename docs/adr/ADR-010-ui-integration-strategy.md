# ADR-010: How the app is put together

**Status:** Locked

## The decision

The app, called **Epicurve**, is split into three clean layers:

- **data_loading** and **workflow** hold all the real logic (loading files, running the pipeline, managing state) and don't know Streamlit exists. You could delete the entire interface and still run the analysis from a plain script.
- **ui** is a thin layer on top that just displays things and wires up buttons.

That split means the backend can be tested on its own, and the interface stays simple because it isn't doing any real work.

## How it's structured

Seven pages, one per pipeline stage: Load Dataset, Configure Roles, Data Preparation, Exploratory Analysis, Visualization, Forecasting, and Results & Export. Each one only unlocks once the step before it is done.

Uploading a file always goes through the same single path, whether it's your own data or the built-in sample dataset. There's no separate shortcut that skips validation.

## Performance and progress

The two slowest steps (fitting the forecasting model and running its backtest) show real progress as they happen: the actual model order being tested, its score, and a live progress bar. Not a fake spinner. Everything else on the page is cached so repeat views are instant.

## Look and feel

A deep teal and warm amber color scheme, one clean font (IBM Plex Sans), and a sidebar that mirrors the pipeline order. Dark mode comes from Streamlit's own built-in toggle, no custom code needed.

## Security basics

Anything from an uploaded file gets safely escaped before it's shown or exported, so a maliciously crafted spreadsheet cell can't run code in someone's browser. Files are only ever handled in memory, never saved to disk under a name a user could control. This is a research and portfolio tool, not a public multi-user service, so there's no login system or rate limiting, and that's a deliberate, stated boundary rather than an oversight.

## A related decision: where population data comes from

Forecasting needs population numbers to calculate rates. The app fetches these from the World Bank's public country list, matching by country name. If a location doesn't have a match, that country's forecast is simply marked as unavailable rather than guessed at.
