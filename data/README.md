# Data

This directory is reserved for lightweight or example data only. Per
the Freeze Document (Section 23, Git & Version Control Strategy, Data
Versioning):

> Do not commit the full OpenDengue dataset to GitHub. Instead:
> document how to obtain it, document the exact version used, document
> preprocessing steps, include only small synthetic/example data if
> needed for demonstration.

No data is present at Milestone 1. Dataset acquisition, documentation
of the exact OpenDengue National Extract version used, and any small
example data begin in Milestone 2 (Data Acquisition & Understanding).

## Milestone 2: acquiring the OpenDengue National Extract

Run `python data/download_national_extract.py` to download the exact
OpenDengue National Extract (version 1.3, GitHub release tag `v1.3.0`)
used throughout this project. The script fetches the official release
archive, verifies it against a pinned SHA-256 checksum, and extracts
the single CSV into `data/raw/` — a directory that is git-ignored by
design (see `.gitignore` and Section 23 of the Freeze Document).

The script performs acquisition only — no parsing beyond unzipping, no
cleaning, no column renaming. See
[`docs/datasets/01_acquisition.md`](../docs/datasets/01_acquisition.md)
for the full source, citation, licensing, and version details, and the
rest of `docs/datasets/` for schema, quality-profile, and dataset
landscape documentation produced during Milestone 2.

## Milestone 5: acquiring the WDI population reference

Run `python data/download_population_reference.py` to download the
World Bank World Development Indicators population reference (`SP.POP.TOTL`)
for the four ADR-008 study countries, used only for Milestone 5's
optional population-normalized reported-case rate. The script queries
the WDI API, verifies the response against a pinned SHA-256 checksum,
and writes a minimal `country, year, population` CSV into `data/raw/`
— also git-ignored, following the same pattern as the OpenDengue
extract. See [`docs/eda.md`](../docs/eda.md) for the full source,
licensing, and methodology details, including why this is optional and
never a required input to `analyze()`.
