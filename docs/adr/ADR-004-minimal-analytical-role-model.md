# ADR-004: Letting the user tell us what's what

**Status:** Locked

## The decision

Every dataset needs three things labeled before it can be analyzed: Time, Location, and a Surveillance Measure (like case counts). An optional fourth, an Identifier, can be added too.

The user picks these columns themselves. The app never guesses.

## Why not just auto-detect them

It would be easy to have the app guess which column is which based on the name or the data type. But that guessing is its own can of worms: it needs to be tested and proven reliable across all kinds of messy real-world data, and that's a much bigger, different problem than the one this project is solving.

Keeping it manual keeps the scope honest. The app can still give hints, for example, highlighting a column that looks like a date, but it never picks anything for the user. They always confirm it themselves.
