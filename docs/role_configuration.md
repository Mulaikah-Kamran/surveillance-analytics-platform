# Role configuration

**Code:** `src/surveillance_platform/role_configuration/`

Before any analysis can happen, the app needs to know which column is which. Time, Location, and a Surveillance Measure (like case counts) are required. An Identifier column is optional.

The user picks these manually every time. Nothing gets auto-detected or guessed.

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

`validate` checks that the required roles are filled in, no column got assigned twice, and every chosen column actually exists in the dataset. If something's wrong, it collects every problem at once instead of stopping at the first one.

It doesn't check whether a column's actual values make sense (like whether a "date" column really contains dates). That happens later, during cleaning.
