# Epicurve

A tool that takes messy, real-world disease surveillance data and turns it into something you can actually use: clean numbers, clear charts, and honest forecasts.

Built around dengue surveillance data from South Asia, but designed to work on other diseases and countries too. It's already been tested on a second, completely unrelated dataset (US disease surveillance from the CDC) to check that it actually holds up, not just on the data it was built for.

## What it does

Upload a surveillance dataset, tell it which columns mean what (date, location, case count), and it walks the data through six steps: cleaning, exploration, visualization, and forecasting, ending in a shareable report.

- **Cleans data honestly.** Drops what it can't trust and says exactly why, instead of guessing or silently smoothing things over.
- **Forecasts three months ahead**, using a real statistical model (SARIMA) checked against a simple baseline. If the fancy model doesn't actually beat "just repeat last year," this tool says so.
- **Shows real progress**, not fake spinners. While a forecast is being computed, you see the actual model settings being tried, live.
- **Exports a clean report**, a single HTML file with working navigation, that opens fine on a phone or a laptop.

## Try it

```bash
git clone <this-repo>
cd surveillance-analytics-platform
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
streamlit run app.py
```

No dataset handy? The app has a "download sample dataset" button that grabs the real one used throughout this project.

## Does the forecasting actually work?

Yes and no, and that's the honest answer. Tested against a simple "repeat last year" baseline on real data:

- **Sri Lanka**: the real model wins clearly
- **Maldives**: the real model wins
- **Bangladesh**: the simple baseline actually wins

A tool that only shows its wins isn't trustworthy. This one shows both.

## How it's built

```
Interface (Streamlit)
        ↓
Workflow controller
        ↓
Analysis modules
        ↓
Data layer
```

The interface is just a thin shell. All the real logic lives in plain Python that's never even imported Streamlit, so it can be tested, reused, or dropped into a different interface entirely.

```
src/surveillance_platform/
├── data_loading/        # reading files in
├── role_configuration/  # mapping columns to their meaning
├── data_preparation/    # cleaning
├── eda/                 # exploratory analysis
├── visualization/       # charts
├── forecasting/         # the SARIMA model and its baseline
├── workflow/            # ties every step together
└── ui/                  # the Streamlit app itself
```

## More detail

- [`docs/`](docs/) has the technical writeup for each part of the pipeline
- [`docs/adr/`](docs/adr/) explains the bigger design decisions and why they were made
- [`docs/user-guide.md`](docs/user-guide.md) walks through the app with screenshots
- [`CHANGELOG.md`](CHANGELOG.md) tracks what's changed over time

## Running the tests

```bash
pytest
ruff check .
black --check .
```

## License

[MIT](LICENSE).
