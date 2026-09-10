# Visualization

**Code:** `src/surveillance_platform/visualization/`

Turns the exploratory analysis into charts, using Plotly. This layer only draws what's already been calculated. It doesn't compute anything new.

```python
from surveillance_platform.visualization import visualize

result = visualize(eda_result)
```

## The five charts

- **Annual trend by country**, one small chart per country rather than one shared chart, since case counts can differ by orders of magnitude between countries.
- **Annual distribution by country**, a box plot comparing the spread of case counts.
- **Population-adjusted distribution**, only shown if population data was available.
- **Reporting resolution and case-definition breakdown**, showing how consistently a country reported its data, kept visually separate from the case-count charts so nobody mistakes reporting quirks for actual disease trends.
- **Overall measure distribution**, a summary box plot of the whole dataset.

One nice touch: if a country's data has an inconsistency, like reporting under two different case definitions in the same year, its point on the trend chart gets a distinct marker so it stands out rather than getting lost.

If a chart's underlying data genuinely doesn't exist (like population figures nobody provided), it's just skipped, never faked or drawn empty.
