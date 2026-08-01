# Dataset Acquisition — OpenDengue National Extract

**Milestone:** 2 — Data Acquisition & Understanding
**Status:** Acquired and verified

## Source

- **Project:** [OpenDengue](https://opendengue.org/) — a global database of
  publicly reported dengue case counts, maintained by the OpenDengue team
  (Clarke, Lim, Gupte, Pigott, van Panhuis, Brady).
- **Repository:** [github.com/OpenDengue/master-repo](https://github.com/OpenDengue/master-repo)
- **Canonical data deposit:** [Figshare](https://doi.org/10.6084/m9.figshare.24259573)
  (versioned DOIs; the GitHub repository mirrors the same releases and is
  what this project downloads from, for scriptable, checksummed access).

## Citation

Per OpenDengue's own citation guidance, both the methods paper and the
versioned dataset are cited:

- Clarke J, Lim A, Gupte P, Pigott DM, van Panhuis WG, Brady OJ. "A global
  dataset of publicly available dengue case count data." *Scientific
  Data.* 2024 Mar 14;11(1):296. DOI:
  [10.1038/s41597-024-03120-7](https://doi.org/10.1038/s41597-024-03120-7)
- Clarke J, Lim A, Gupte P, Pigott DM, van Panhuis WG, Brady OJ.
  "OpenDengue: data from the OpenDengue database." Version 1.3. figshare;
  2025. DOI:
  [10.6084/m9.figshare.24259573](https://doi.org/10.6084/m9.figshare.24259573)

## Version Used

| Field | Value |
|---|---|
| Dataset version | 1.3 |
| GitHub release tag | `v1.3.0` |
| Release date | 2025-05-27 |
| Release commit | `3dde0f6c7145744ec8c71d048c9840ad9677f2f` |
| File acquired | `data/releases/V1.3/National_extract_V1_3.zip` → `National_extract_V1_3.csv` |
| Archive SHA-256 | `d4fa7b1a881481fd5323991cc7a23dbe690112e2c473898ceea76e1e9c85dc59` |
| Coverage per release notes | 129 countries; national-level data through April 2025 for 121 of them |

Version 1.3 is the latest tagged release at the time of Milestone 2 (five
releases precede it: v1.0 through v1.2.2). The dataset is versioned and
released independently of this project, so the exact tag is pinned rather
than tracking `main`, and the archive checksum is verified on every
download — both so a reviewer re-running the acquisition script months
from now gets the identical file this project was built and documented
against, not whatever OpenDengue has published by then.

## Licensing

OpenDengue data is released under a **Creative Commons CC BY-SA** licence.
This permits reuse and adaptation (commercial and non-commercial) provided
appropriate attribution is given and any adapted/redistributed version of
the dataset is shared under the same licence terms. This project only
*reads* the dataset for analysis (it does not redistribute an adapted
version of the raw data), but the citation above is included throughout
the repository regardless, per both the licence and academic norms.

## Download Procedure

The exact, reproducible procedure used by this project:

```bash
python data/download_national_extract.py
```

This script (added in this milestone; see `data/download_national_extract.py`):

1. Downloads the release archive from
   `https://raw.githubusercontent.com/OpenDengue/master-repo/v1.3.0/data/releases/V1.3/National_extract_V1_3.zip`
2. Verifies the archive against the pinned SHA-256 checksum above
3. Extracts `National_extract_V1_3.csv` into `data/raw/` (git-ignored)

No other steps happen — no parsing beyond the zip extraction, no column
renaming, no filtering. This deliberately keeps acquisition and
understanding (Milestone 2) separate from preprocessing and cleaning
(Milestone 4), per the Freeze Document's workflow ordering (Section 14).

**Manual alternative:** the same file can be obtained by visiting the
[v1.3.0 release page](https://github.com/OpenDengue/master-repo/releases/tag/v1.3.0)
or the [Figshare deposit](https://doi.org/10.6084/m9.figshare.24259573)
and downloading the National Extract directly — the script exists purely
for reproducibility, not because manual download is unavailable.

## Expected File Format

- **Format:** CSV, UTF-8, comma-delimited
- **Size:** ~4.2 MB (National Extract; the Temporal Extract for
  comparison is ~482 MB — see `02_dataset_landscape.md`)
- **Shape:** 29,873 rows × 16 columns
- **One row per** (country, reporting interval) combination — i.e. one
  observed case count for one country over one reporting period

Full column-by-column documentation is in
[`03_schema.md`](03_schema.md).
