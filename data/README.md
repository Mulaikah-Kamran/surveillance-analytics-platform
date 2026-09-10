# Data

Raw data files aren't stored in this repo. They're downloaded fresh using the scripts here, and everything is verified against a pinned checksum so you always get the exact same file.

## Getting the main dataset

```bash
python data/download_national_extract.py
```

Downloads the OpenDengue National Extract used throughout this project. See [`docs/about-the-data.md`](../docs/about-the-data.md) for what's actually in it.

## Getting population figures

```bash
python data/download_population_reference.py
```

Downloads World Bank population data for the four study countries, used to convert raw case counts into rates. This step is optional, everything else works fine without it.

## Getting the second, validation dataset

```bash
python data/download_nndss_validation_dataset.py
```

Downloads a completely different disease surveillance dataset (from the CDC) used to check that the pipeline generalizes beyond the original dengue data. See [`docs/m9-validation-results.md`](../docs/m9-validation-results.md) for what happened when it did.
