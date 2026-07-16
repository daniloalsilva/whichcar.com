---
name: motorcycle_fipe_updater
description: Update motorcycle models FIPE prices and specifications using local automation scripts and FIPE APIs.
---

# Motorcycle FIPE & Spec Updater Skill 🏍️

This skill provides instructions and automation to fetch, update, and validate the WhichBike motorcycle database with the latest Tabela FIPE prices.

## Automated Pricing Update

You can run the automatic update directly using the project Makefile target:

```bash
make update-fipe
```

Or execute the Python script manually from the workspace root:

```bash
# Update all manufacturers
python3 scripts/fipe_updater.py

# Update a single manufacturer (e.g. honda, yamaha)
python3 scripts/fipe_updater.py honda
```

## Spec Validation

Before deploying or committing changes to the database, run the validation tool to ensure YAML formatting and matching logic parse correctly:

```bash
python3 scripts/validate.py
```

## How the Scraper Works

1. **Brand Matching:** Looks up the brand name (e.g., "Honda") in FIPE's official marcas list to get the FIPE brand ID.
2. **Model Matching:** Queries FIPE models for the matched brand, performing fuzzy token comparisons to pair local models (e.g., "CG 160 Titan") with official FIPE nomenclatures (e.g., "CG 160 TITAN").
3. **Year & Valuation Retrieval:** Inspects years available for the model, preferring the "Zero Km" reference code when available, otherwise defaulting to the latest year model code.
4. **Data Sync:** Parses the returned BRL valuation, cleans formatting, and writes the numeric value back into the FIPE field in the manufacturer's YAML data file under `website/_data/`.
