# ADR-007: Picking one date per record

**Status:** Locked

## The decision

When a dataset reports a time range instead of a single date (like "cases from March 1 to March 7"), this project uses the **start date** as the one date it works with.

## Why the start date

It's simple, predictable, and doesn't need any extra math. The original date range is kept in the cleaned data too, so nothing is thrown away, it's just not what the analysis calculations use.
