# About the data

## Where it comes from

[OpenDengue](https://opendengue.org/), a public database of reported dengue cases from around the world, maintained by a team of researchers and licensed under Creative Commons (CC BY-SA). This project uses their National Extract, which reports one number per country per time period, rather than their more detailed but much messier district-level extract.

Downloads are checksum-verified, so anyone re-running the acquisition script gets the exact same file every time.

## What it actually looks like

Just under 30,000 rows, 16 columns, one row per country per reporting period. Each row covers a date range (a week, a month, or a year) rather than a single day, and that resolution varies by country and by era. This project always uses the start date of that range as the single reference date, since it's simple and avoids extra assumptions.

## What we found digging into it

A few real quirks worth knowing about:

- Coverage spans over a century in theory (1924 to 2025), but that's misleading. Most countries only have a handful of usable years, and reporting frequency shifts around a lot, sometimes weekly, sometimes monthly, sometimes just once a year.
- Some countries occasionally report using a different case definition than usual (confirmed vs. total suspected cases, for example), which matters a lot for interpreting a trend correctly.
- A handful of columns are essentially unused or redundant for this project's purposes and get ignored.

None of these are data quality problems exactly. They're just real-world reporting behavior that any pipeline working with this kind of data needs to expect and handle sensibly, which is exactly what the cleaning and analysis steps do.
