# Data files

- `fbs_key_commodities_2017_2025.csv`: 135 commodity-year rows extracted from the four NISR annual Food Balance Sheets reports (national annual records). The report filename, original commodity label and exact PDF page appear in each row. Units ending `_kt` are **thousand metric tonnes**.
- `forecast_2026_baseline.csv`: deterministic model forecast using the default 2026 assumptions (2.2% population growth, no production change, no loss reduction).
- `validation_2025.csv`: 2025 holdout results for 15 commodities, with observed values, model blend, naive baseline, and errors.

To regenerate the last two CSVs from the source extract, run `python scripts/build_outputs.py` from the repository root.

The full reports are not included because they are freely accessible public NISR publications of substantial size and may contain separate copyright notices. See `../docs/DATA_SOURCES.md` for names, source pages and terms. **The figures are original NISR estimates** and the model forecasts are not official statistics.
