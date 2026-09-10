# ADR-005: One forecasting model, not a bake-off

**Status:** Locked

## The decision

This project builds one forecasting model and compares it against a simple baseline. It does not try out multiple competing models and pick a winner.

## Why

The point here is good engineering, not a machine learning competition. A simple baseline is enough to check whether the real model is actually adding value. Testing five different models against each other would turn this into a different kind of project entirely.
