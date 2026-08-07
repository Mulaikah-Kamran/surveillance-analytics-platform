# Role Configuration

**Milestone:** 3 — Role Configuration
**Module:** `src/surveillance_platform/role_configuration/`

## Purpose

Establishes a stable, explicit contract between an arbitrary
surveillance dataset and the analytical pipeline: the user assigns
which dataset column fills each analytical role, and this module
validates that assignment. Per ADR-004 (Minimal Analytical Role
Model), the platform never infers, guesses, recommends, or
heuristically detects roles — assignment is always explicit.

## Role model

| Role | Required? |
|---|---|
| `time` | Yes |
| `location` | Yes |
| `surveillance_measure` | Yes |
| `identifier` | No (defaults to `None`) |

## Public configuration model

```python
from surveillance_platform.role_configuration import RoleConfiguration, validate

config = RoleConfiguration(
    time="date",
    location="country",
    surveillance_measure="cases",
    identifier=None,
)

validate(config, available_columns=["date", "country", "cases", "record_id"])
```

`validate` raises `RoleConfigurationError` if the configuration is
invalid, and returns `None` if it is valid. Constructing a
`RoleConfiguration` does not validate it — validation is an explicit,
separate step.

## What is validated

**Structural validity** (independent of any dataset):

- Each required role (`time`, `location`, `surveillance_measure`) is a
  non-empty string.
- `identifier`, if supplied, is a non-empty string.
- No two roles are assigned to the same column name.

**Dataset compatibility** (checked against `available_columns`, a
plain `Iterable[str]` — not a pandas `DataFrame` or a `Dataset`
abstraction):

- Every assigned column exists in `available_columns`.

All violations found are collected and reported together in one
`RoleConfigurationError`, rather than stopping at the first problem.

## What is explicitly out of scope

Role Configuration validates *assignments*, not column *contents*. It
does not check whether a column "looks like" a date, a location, or a
numeric surveillance measure — that is a data preparation concern for
Milestone 4. It also does not read or load any dataset itself; the
list of available columns is supplied by the caller.

## Consumption by later milestones

Milestone 4 (Data Preparation Pipeline) is expected to construct a
`RoleConfiguration`, validate it against the columns of a loaded
dataset, and then use `config.time`, `config.location`,
`config.surveillance_measure`, and `config.identifier` to know which
columns to operate on — without needing any knowledge of how role
configuration is validated internally.
