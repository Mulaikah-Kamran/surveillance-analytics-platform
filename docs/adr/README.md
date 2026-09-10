# Architecture decisions

This is the record of the big design choices behind this project, and why they were made.

New records only get added when a decision is genuinely hard to reverse or worth remembering later. Once something's locked here, it stays that way unless a real problem comes up.

| ADR | What it covers |
|-----|-------|
| [ADR-001](ADR-001-primary-user.md) | Who this is built for |
| [ADR-002](ADR-002-data-strategy.md) | The main data source |
| [ADR-003](ADR-003-analytical-workflow.md) | The order things happen in |
| [ADR-004](ADR-004-minimal-analytical-role-model.md) | Letting the user tell us what's what |
| [ADR-005](ADR-005-forecasting-strategy.md) | One forecasting model, not a bake-off |
| [ADR-006](ADR-006-user-interface-strategy.md) | Keeping the interface dumb on purpose |
| [ADR-007](ADR-007-temporal-standardization-strategy.md) | Picking one date per record |
| [ADR-008](ADR-008-study-country-selection.md) | Which countries made the cut |
| [ADR-009](ADR-009-forecasting-strategy.md) | How forecasting actually works |
| [ADR-010](ADR-010-ui-integration-strategy.md) | How the app is put together |
| [ADR-011](ADR-011-m9-validation-dataset-selection.md) | Picking a second dataset to test the pipeline on |
