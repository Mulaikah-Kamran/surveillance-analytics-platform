# The app

**Code:** `src/surveillance_platform/data_loading/`, `workflow/`, `ui/`, `app.py`

Epicurve is the Streamlit app that ties everything together. Seven pages, one for each step: Load Dataset, Configure Roles, Data Preparation, Exploratory Analysis, Visualization, Forecasting, and Results & Export.

Run it locally with:

```bash
streamlit run app.py
```

## A few things worth knowing

**The backend doesn't need the app to work.** All the real logic lives in code that has never even imported Streamlit. You could delete the entire interface and still run the whole pipeline from a plain Python script.

**Forecasting shows real progress, not a fake loading bar.** While a model is fitting, you actually see which settings it's trying and how well each one scores, live.

**Population data comes from the World Bank**, matched automatically by country name. If a country in your dataset doesn't match anything in that list, its rate-based charts and forecasts are just skipped rather than guessed at.

**The exported report has its own navigation and works on your phone.** It's a single HTML file you can open anywhere, with a sticky menu to jump between sections and a layout that adapts to a small screen.

## Keeping it safe

Anything from an uploaded file is safely escaped before being shown or exported, so a booby-trapped spreadsheet can't run code in someone's browser. Files are only ever handled in memory. This is a research tool built for one person at a time, not a public multi-user service, and that's a deliberate choice, not an oversight.
