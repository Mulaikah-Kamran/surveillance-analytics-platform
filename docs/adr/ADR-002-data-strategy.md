# ADR-002: The main data source

**Status:** Locked

## The decision

This project uses OpenDengue's National Extract as its main dataset, focused on 3 to 5 South Asian countries.

## The alternative

OpenDengue also publishes a Temporal Extract with finer geographic detail, down to the district level.

## Why National, not Temporal

The Temporal Extract sounds better on paper, more detail is usually good. But 93% of its rows are at the district level, which adds a lot of complexity without actually helping this project answer its core question: can a well-built pipeline turn messy surveillance data into something useful for forecasting?

The National Extract gives a cleaner, country-level view that's easier to work with and better suited to spotting long-term trends. The trade-off is no district-level analysis in this version, which is fine. That's not what this project set out to do.
